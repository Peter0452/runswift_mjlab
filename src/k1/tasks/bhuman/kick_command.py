"""B-Human's kick environment state (Booster Gym ``envs/t1_ball.py``, K1).

Booster Gym keeps the whole kick task in one env class. Here it lives in one
command term so the mjlab managers can read it:

- ``post_physics_step`` (after the physics substeps, before terminations and
  rewards) = the body of ``T1_Ball.step`` up to ``_compute_reward``: robot
  state refresh, gait clock, ``_update_kick_tensors``, ball-reset requests,
  random robot kicks / pushes, the odometry buffer and ``_check_termination``.
- ``reset`` (mjlab env reset) = ``_reset_idx``: robot, joints, ball, gains,
  calibration offsets, kick flags.
- ``compute`` (after resets) = ``_reset_ball_idx`` for ball-only resets,
  ``_teleport_robot`` and ``_resample_commands``.
- ``actor_obs`` / ``critic_obs`` = ``_compute_observations``.

Names and formulas follow the original so the two can be compared line by
line; comments mark the few places that differ on purpose.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

import numpy as np
import torch

from k1.tasks.bhuman.actuator import BHumanPdActuator
from k1.tasks.bhuman.robot import (
  BALL_RADIUS,
  DEFAULT_LEG_POS,
  FEET,
  FEET_EDGE_POS,
  FEET_SOLE_POS,
  LEG_JOINTS,
  URDF_EFFORT,
)
from k1.tasks.bhuman.terrain import FieldHeights
from mjlab.managers.command_manager import CommandTerm, CommandTermCfg
from mjlab.utils.lab_api.math import (
  euler_xyz_from_quat,
  quat_apply,
  quat_apply_inverse,
  quat_from_euler_xyz,
)

if TYPE_CHECKING:
  from k1.tasks.bhuman.mdp import BHumanKickAction
  from mjlab.entity import Entity
  from mjlab.envs import ManagerBasedRlEnv
  from mjlab.viewer.debug_visualizer import DebugVisualizer

_PI = math.pi


@dataclass
class Rand:
  """One ``randomization`` / ``noise`` entry of the YAML (``apply_randomization``).

  gaussian: ``lo + hi * N(0, 1)``; uniform: ``U(lo, hi)``; uniform_log:
  ``lo + (hi - lo) * U(0, 1) / -log(clamp(U(0, 1), 0.0067, 0.37))``.
  """

  dist: Literal["gaussian", "uniform", "uniform_log"]
  op: Literal["additive", "scaling"]
  lo: float
  hi: float


def gauss(sigma: float) -> Rand:
  return Rand("gaussian", "additive", 0.0, sigma)


def apply_rand(x: torch.Tensor, r: Rand | None) -> torch.Tensor:
  return apply_rand_noise(x, r)[0]


def apply_rand_noise(
  x: torch.Tensor, r: Rand | None
) -> tuple[torch.Tensor, torch.Tensor]:
  """Returns (result, raw sample), like ``apply_randomization(return_noise=True)``."""
  if r is None:
    return x, torch.zeros_like(x)
  u = torch.rand_like(x) if r.dist != "gaussian" else torch.randn_like(x)
  if r.dist == "gaussian":
    val = r.lo + r.hi * u
  elif r.dist == "uniform":
    val = r.lo + (r.hi - r.lo) * u
  else:
    log_scale = torch.log(torch.rand_like(x).clamp(min=0.0067, max=0.37))
    val = r.lo + (r.hi - r.lo) * u / -log_scale
  out = x + val if r.op == "additive" else x * val
  return out, u


def wrap(a: torch.Tensor) -> torch.Tensor:
  return (a + _PI) % (2 * _PI) - _PI


def rot2d(v: torch.Tensor, a: torch.Tensor) -> torch.Tensor:
  c, s = torch.cos(a), torch.sin(a)
  return torch.stack((c * v[:, 0] - s * v[:, 1], s * v[:, 0] + c * v[:, 1]), -1)


def yaw_of(quat: torch.Tensor) -> torch.Tensor:
  """``get_euler_xyz`` yaw, in [0, 2 pi)."""
  return euler_xyz_from_quat(quat, wrap_to_2pi=True)[2]


@dataclass(kw_only=True)
class BHumanKickCommandCfg(CommandTermCfg):
  """``K1_Ball.yaml`` (initial-stage values; see ``stages.py`` for later ones)."""

  resampling_time_range: tuple[float, float] = (1.0e9, 1.0e9)
  border_size: float = 15.0
  decimation: int = 10

  # commands
  resampling_kick_type: tuple[float, float] = (2.0, 20.0)
  random_ball_reset: tuple[float, float, float] = (1e-4, 1e-4, 1e-4)
  random_ball_distance_reset: float = 5e-5
  ball_freeze_at_kick: float = 0.2
  distance_reset: tuple[float, float] = (0.3, 0.5)
  force_ball_close: float = 0.1
  keep_old_ball_when_reset: float = 0.2
  reset_ball_request: float = 1e-4
  add_ball_vel: float = 1e-5
  add_ball_vel_max_velocity: float = 0.5
  add_ball_vel_in_direction: float = 1e-5
  add_ball_vel_in_direction_max_velocity: float = 0.5
  ball_vel_in_direction_range: Rand = field(default_factory=lambda: gauss(0.5))

  # normalization
  norm_gravity: float = 1.0
  norm_lin_vel: float = 1.0
  norm_ang_vel: float = 1.0
  norm_dof_pos: float = 1.0
  norm_dof_vel: float = 0.1
  norm_ball_pos: float = 0.1
  norm_ball_vel: float = 0.1
  norm_ball_kick_range: float = 0.1
  filter_weight: float = 0.1
  norm_push_force: float = 0.1
  norm_push_torque: float = 0.5
  clip_actions: float = 2.0
  action_frequence_limit: tuple[float, float] = (-0.5, 0.5)

  # noise
  observation_noise: bool = True
  noise_gravity: float = 0.01
  noise_lin_vel: float = 0.05
  noise_ang_vel: float = 0.1
  noise_dof_pos: float = 0.01
  noise_dof_vel: float = 0.5
  noise_height: float = 0.02
  ball_pos_noise_scale_range: tuple[float, float] = (0.5, 10.0)
  ball_pos_noise_x: tuple[float, float] = (0.03, 2.0)
  ball_pos_noise_y: tuple[float, float] = (0.03, 0.35)
  ball_pos_odo_noise: tuple[float, float] = (0.01, 0.01)
  ball_vel_noise: float = 0.01
  ball_vel_scale_noise: tuple[float, float] = (0.0, 2.0)
  ball_range_noise: float = 0.05
  ball_direction_noise: float = 0.01

  # randomization
  init_dof_pos: float = 0.05
  dof_pos_offset_pitch: float = 0.02
  dof_pos_offset_roll: float = 0.01
  dof_pos_offset_other: float = 0.005
  init_base_pos_xy: float = 1.0
  init_base_lin_vel_xy: float = 0.05
  init_base_lin_vel_z: float = 0.05
  init_base_ang_vel_xyz: float = 0.1
  init_ball_pos_x: Rand = field(
    default_factory=lambda: Rand("uniform_log", "additive", 0.4, 1.5)
  )
  init_ball_pos_far_x: Rand = field(
    default_factory=lambda: Rand("uniform_log", "additive", 0.6, 1.5)
  )
  init_ball_vel: Rand = field(
    default_factory=lambda: Rand("uniform_log", "additive", 0.0, 7.5)
  )
  kick_interval_s: float = 3.0
  kick_lin_vel: float = 0.3
  kick_lin_vel_z: float = 0.1
  kick_ang_vel: float = 0.1
  push_interval_s: float = 5.0
  push_duration_s: float = 2.0
  push_force: float = 5.0
  push_torque: float = 2.0
  dof_stiffness: tuple[float, float] = (0.95, 1.05)
  dof_ankle_stiffness: tuple[float, float] = (0.8, 1.2)
  dof_hiproll_stiffness: tuple[float, float] = (0.9, 1.1)
  dof_damping: tuple[float, float] = (0.95, 1.05)
  dof_ankle_damping: tuple[float, float] = (0.9, 1.1)
  dof_hiproll_damping: tuple[float, float] = (0.9, 1.1)
  dof_friction: tuple[float, float] = (0.0, 2.0)
  ball_radius_range: tuple[float, float] = (-0.01, 0.01)

  # ball
  kick_strong_range: float = 20.0
  kick_normal_range: Rand = field(
    default_factory=lambda: Rand("uniform_log", "additive", 0.5, 20.0)
  )
  ball_linear_damping: float = 0.75
  ball_angular_damping: float = 0.5
  ball_max_linear_velocity: float = 20.0

  # rewards (general)
  episode_length_s: float = 30.0
  episode_number_of_kicks: int = 3
  terminate_height: float = 0.30
  terminate_vel: float = 400.0
  terminate_time: float = 0.1
  base_height_target: float = 0.50
  soft_dof_pos_limit: float = 0.95
  swing_period: float = 0.2
  feet_distance_ref: float = 0.192
  feet_height_ref: float = 0.02
  target_frequence: float = 1.5

  # rewards.ball_parameters
  time_after_kick: int = 20
  kick_pose_y_off: float = 0.06
  ball_y_dis_ratio: tuple[float, float] = (2.0, 2.0)
  ball_kicked_start_counter: int = 1
  ball_kicked_max_counter: int = 50
  ball_kicked_clipped_counter: int = 10
  ball_walk_vision_sigma: float = 0.75
  ball_walk_direction_sigma: float = 0.75
  kick_direction_sigma_range: float = 1.0
  kick_direction_sigma_just_hit: float = 1.0
  ball_friction: float = 0.3
  ball_velocity_range_sigma_scale: float = 1.0
  ball_avoidance_range: float = 0.55
  kick_pose_x: tuple[float, float] = (0.0, -0.35)
  ball_distance_offset: float = 0.3
  ball_rotation_offset: float = 0.1
  base_height_scaling: tuple[float, float] = (0.45, 0.49)
  kick_pose_increase_value: float = 0.025
  clip_max_speed_near_ball: float = 0.5
  kick_direction_negative_factor: float = 0.1
  negative_walk_speed_factor: float = 1.0
  target_sole_yaw_angle: float = 0.0
  target_sole_yaw_sigma: float = 1.0
  heavy_ball: float = 0.0
  disable_sole_yaw_direction_penalty: bool = False
  disable_deviation_flag: bool = True
  disable_extra_deviation_flag: bool = True

  def build(self, env: ManagerBasedRlEnv) -> BHumanKickCommand:
    return BHumanKickCommand(self, env)


class BHumanKickCommand(CommandTerm):
  cfg: BHumanKickCommandCfg

  def __init__(self, cfg: BHumanKickCommandCfg, env: ManagerBasedRlEnv):
    super().__init__(cfg, env)
    self.robot: Entity = env.scene["robot"]
    self.ball: Entity = env.scene["ball"]
    dev = self.device
    n = self.num_envs
    self.dt = env.step_dt
    self.heights = FieldHeights(env.sim.mj_model, cfg.border_size, dev)

    def z(*shape: int) -> torch.Tensor:
      return torch.zeros(n, *shape, device=dev)

    def zb(*shape: int) -> torch.Tensor:
      return torch.zeros(n, *shape, dtype=torch.bool, device=dev)

    # Robot indexing and constants.
    names = list(self.robot.joint_names)
    self.leg_ids = torch.tensor([names.index(j) for j in LEG_JOINTS], device=dev)
    bodies = list(self.robot.body_names)
    self.feet_ids = [bodies.index(f) for f in FEET]
    self.default_dof_pos = torch.tensor(DEFAULT_LEG_POS, device=dev).unsqueeze(0)
    lim = self.robot.data.joint_pos_limits[0, self.leg_ids]
    self.dof_pos_limits = lim.clone()
    self.torque_limits = torch.tensor(URDF_EFFORT, device=dev)
    self.feet_edge = torch.tensor(FEET_EDGE_POS, device=dev)
    self.sole_pos = torch.tensor(FEET_SOLE_POS, device=dev)
    self.leg_actuators: list[BHumanPdActuator] = [
      a for a in self.robot.actuators if isinstance(a, BHumanPdActuator)
    ]
    # Column of each leg joint in each actuator (actuators are grouped by joint
    # type, B-Human's arrays are in DOF order).
    self._act_cols = [
      [LEG_JOINTS.index(t) for t in a.target_names] for a in self.leg_actuators
    ]
    self.default_kp = z(12)
    self.default_kd = z(12)
    for a, cols in zip(self.leg_actuators, self._act_cols, strict=True):
      assert a.stiffness is not None and a.damping is not None
      self.default_kp[:, cols] = a.stiffness
      self.default_kd[:, cols] = a.damping
    self.default_kp = self.default_kp[0].clone()
    self.default_kd = self.default_kd[0].clone()
    self.dof_stiffness = self.default_kp.repeat(n, 1)
    self.dof_damping = self.default_kd.repeat(n, 1)

    # State (same names as T1_Ball).
    self.base_pos = z(3)
    self.base_quat = z(4)
    self.base_quat[:, 0] = 1.0
    self.base_quat_z = self.base_quat.clone()
    self.yaw = z()
    self.root_lin_vel_w = z(3)
    self.root_ang_vel_w = z(3)
    self.base_lin_vel = z(3)
    self.base_ang_vel = z(3)
    self.projected_gravity = z(3)
    self.projected_gravity[:, 2] = -1.0
    self.filtered_lin_vel = z(3)
    self.filtered_ang_vel = z(3)
    self.last_root_vel = z(6)
    self.dof_pos = z(12)
    self.dof_vel = z(12)
    self.last_dof_vel = z(12)
    self.custom_dof_vel = z(12)
    self.torques = z(12)
    self.dof_pos_offset = z(12)
    self.feet_pos = z(2, 3)
    self.feet_quat = z(2, 4)
    self.feet_quat[..., 0] = 1.0
    self.feet_vel = z(2, 3)
    self.feet_vel_filtered = z(2, 3)
    self.last_feet_pos = z(2, 3)
    self.feet_roll = z(2)
    self.feet_yaw = z(2)
    self.last_feet_yaw = z(2)
    self.feet_contact = zb(2)
    self.last_feet_contact = zb(2)
    self.feet_height_over_ground = z(2)
    self.feet_swing_counter = z(2)
    self.gait_process = z()
    self.episode_length_buf = torch.zeros(n, dtype=torch.long, device=dev)
    self.cmd_resample_time = torch.zeros(n, dtype=torch.long, device=dev)
    self.terminate_counter = z()
    self.ball_reset_counter = z()
    self.base_mass_scaled = z(4)
    self.pushing_forces = z(3)
    self.pushing_torques = z(3)
    self.delay_ball_pos = torch.zeros(n, dtype=torch.long, device=dev)

    # Ball.
    self.ball_state = z(13)  # pos, quat (wxyz), lin vel w, ang vel w
    self.ball_state[:, 3] = 1.0
    self.ball_pos = z(3)
    self.ball_vel = z(3)
    self.last_relative_ball_pos = z(2)
    self.last_ball_pos = z(3)
    self.last_ball_vel = z(3)
    self.filtered_ball_pos = z(3)
    self.buffered_global_ball_pos = z(4, 3)
    self.kick_leg_was_obvious = torch.zeros(n, dtype=torch.long, device=dev)
    self.ball_walk_target_overshoot = torch.zeros(n, dtype=torch.long, device=dev)
    self.ball_vel_before_kick = z()
    self.direction = z(2)
    self.direction_angle = z()
    self.direction_angle_current = z()
    self.robot_direction_ref = z()
    self.range = z()
    self.ball_end_target = z(2)
    self.ball_kick_pose = z(3)
    self.ball_close_to_kick_pose = z()
    self.more_harsh_walk_speed_condition = z()
    self.origin_pos = z(3)
    self.inside_kick_pose_counter = z()
    self.current_kick_pose_distance = z()
    self.last_kick_pose_distance = z()
    self.ball_kicked_counter = z()
    self.ball_kick_direction_reward = z()
    self.ball_velocity_norm = z()
    self.ball_velocity_norm_at_kick = z()
    self.ball_still_counter = z()
    self.kick_pose_translation_ratio = z()
    self.allow_ball_kick = zb()
    self.kick_sole_yaw_ratio = z()
    self.last_world_pose = z(3)
    self.current_world_pose = z(3)
    self.ball_freeze_at_kick = zb()
    self.ball_pos_at_kick = z(3)
    self.ball_request_resetted = zb()
    self.odo_buffer = z(10, 3)
    self.odo_noise_factor = z(2)
    self.flag_is_strong_kick = zb()
    self.flag_is_inaccurate_kick = z()
    self.flag_allow_deviation = zb()
    self.heavy_ball = zb()
    self.request_changed = torch.zeros(n, dtype=torch.long, device=dev)
    self.changed_ball_vel = zb()

    # Termination flags (set in post_physics_step).
    self.reset_ball = zb()
    self.terminated = zb()
    self.time_out_buf = zb()
    self.bootstrap_buf = zb()
    # Envs whose ball-relative state still has to be filled in after a reset
    # (needs the post-reset kinematics, which exist only after forward()).
    self._pending_kick_ball = zb()
    # Fixed kick tasks (``place_task``); NaN = sample as in training.
    self.task_direction = torch.full((n,), float("nan"), device=dev)
    self.task_range = torch.full((n,), float("nan"), device=dev)
    # One-off kick direction for the next target only (DecAP clip spawns).
    self._direction_once = torch.full((n,), float("nan"), device=dev)

    self.metrics["kicks"] = z()
    self.metrics["kick_speed"] = z()
    self.metrics["kick_angle_error"] = z()

  # Command-term interface.

  @property
  def command(self) -> torch.Tensor:
    return torch.stack(
      (self.direction_angle_current, self.range, self.flag_is_strong_kick.float()),
      -1,
    )

  @property
  def action_term(self) -> BHumanKickAction:
    term = self._env.action_manager.get_term("legs")
    return term  # type: ignore[return-value]

  def _update_metrics(self) -> None:
    pass

  def _debug_vis_impl(self, visualizer: DebugVisualizer) -> None:
    """Kick line (red: strong, yellow: scaled; first 2 m), kick pose (blue)
    and walk target (green), as Booster Gym draws them."""
    env_ids = list(visualizer.get_env_indices(self.num_envs))
    if not env_ids:
      return
    ball = self.ball_state[env_ids, :3]
    to_target = self.ball_end_target[env_ids] - ball[:, :2]
    length = to_target.norm(dim=-1, keepdim=True)
    end = ball.clone()
    end[:, :2] += to_target / length.clamp(min=1e-6) * length.clamp(max=2.0)
    walk = quat_apply(self.base_quat_z, self.helper_walk_target()) + self.base_pos
    pose = self.ball_kick_pose[env_ids].cpu().numpy()
    ball_np, end_np = ball.cpu().numpy(), end.cpu().numpy()
    walk_np = walk[env_ids].cpu().numpy()
    strong = self.flag_is_strong_kick[env_ids].cpu().numpy()
    for k in range(len(env_ids)):
      color = (1.0, 0.1, 0.1, 1.0) if strong[k] else (1.0, 0.9, 0.1, 1.0)
      visualizer.add_arrow(ball_np[k], end_np[k], color)
      p = np.array([pose[k, 0], pose[k, 1], 0.02])
      visualizer.add_sphere(p, 0.03, (0.1, 0.3, 1.0, 1.0))
      w = np.array([walk_np[k, 0], walk_np[k, 1], 0.02])
      visualizer.add_sphere(w, 0.025, (0.1, 0.9, 0.2, 1.0))

  def _update_command(self) -> None:
    pass

  # Reading the sim.

  def _read_ball(self) -> None:
    d = self.ball.data.data
    q = self.ball.indexing.free_joint_q_adr
    v = self.ball.indexing.free_joint_v_adr
    self.ball_state[:, :7] = d.qpos[:, q]
    self.ball_state[:, 7:10] = d.qvel[:, v[:3]]
    self.ball_state[:, 10:13] = quat_apply(self.ball_state[:, 3:7], d.qvel[:, v[3:]])

  def _write_ball(self, env_ids: torch.Tensor | None = None) -> None:
    ids = slice(None) if env_ids is None else env_ids
    self.ball.write_root_state_to_sim(self.ball_state[ids], env_ids)

  def _read_robot(self) -> None:
    d = self.robot.data.data
    q = self.robot.indexing.free_joint_q_adr
    v = self.robot.indexing.free_joint_v_adr
    self.base_pos[:] = d.qpos[:, q[:3]]
    self.base_quat[:] = d.qpos[:, q[3:7]]
    self.yaw[:] = yaw_of(self.base_quat)
    zero = torch.zeros_like(self.yaw)
    self.base_quat_z[:] = quat_from_euler_xyz(zero, zero, self.yaw)
    self.root_lin_vel_w[:] = d.qvel[:, v[:3]]
    self.base_ang_vel[:] = d.qvel[:, v[3:]]
    self.root_ang_vel_w[:] = quat_apply(self.base_quat, self.base_ang_vel)
    self.base_lin_vel[:] = quat_apply_inverse(self.base_quat, self.root_lin_vel_w)
    g = torch.zeros_like(self.base_pos)
    g[:, 2] = -1.0
    self.projected_gravity[:] = quat_apply_inverse(self.base_quat, g)
    self.dof_pos[:] = self.robot.data.joint_pos[:, self.leg_ids]
    self.dof_vel[:] = self.robot.data.joint_vel[:, self.leg_ids]

  def _refresh_feet_state(self) -> None:
    data = self.robot.data
    self.feet_pos[:] = data.body_link_pos_w[:, self.feet_ids]
    self.feet_quat[:] = data.body_link_quat_w[:, self.feet_ids]
    roll, _, yaw = euler_xyz_from_quat(self.feet_quat.reshape(-1, 4), wrap_to_2pi=True)
    self.feet_roll[:] = wrap(roll.reshape(-1, 2))
    self.feet_yaw[:] = wrap(yaw.reshape(-1, 2))
    edges = self._feet_edges()
    h = edges[..., 2] - self.heights(edges)
    self.feet_contact[:] = (h < 0.01).any(dim=-1)
    self.feet_height_over_ground[:] = h.min(dim=-1).values

  def _feet_edges(self) -> torch.Tensor:
    """World positions of the 4 sole corners of each foot: (n, 2, 4, 3)."""
    n = self.num_envs
    q = self.feet_quat.unsqueeze(2).expand(n, 2, 4, 4).reshape(-1, 4)
    e = self.feet_edge.expand(n, 2, 4, 3).reshape(-1, 3)
    return self.feet_pos.unsqueeze(2) + quat_apply(q, e).reshape(n, 2, 4, 3)

  def ball_sole_distance(self) -> tuple[torch.Tensor, torch.Tensor]:
    """``_helper_ball_sole_distance``: xy distance ball - nearest sole corner."""
    edges = self._feet_edges()
    d = (edges[..., :2] - self.ball_state[:, None, None, :2]).norm(dim=-1)
    return d[:, 0].min(dim=-1).values, d[:, 1].min(dim=-1).values

  def _sole_origin(self) -> torch.Tensor:
    n = self.num_envs
    sole = quat_apply(
      self.feet_quat.reshape(-1, 4), self.sole_pos.expand(n * 2, 3)
    ).reshape(n, 2, 3)
    return (self.feet_pos + sole).mean(dim=1)

  def terrain_height(self, xy: torch.Tensor) -> torch.Tensor:
    return self.heights(xy)

  @property
  def ball_contact_radius(self) -> float:
    """Nominal radius + the radius DR's upper bound (used for touch tests)."""
    return BALL_RADIUS + self.cfg.ball_radius_range[1]

  # T1_Ball.step, after the physics.

  def post_physics_step(self, dt: float) -> None:
    cfg = self.cfg
    # End-of-step bookkeeping of the previous step (T1_Ball keeps these at the
    # end of step(); here they are taken before the new state is read).
    self.last_dof_vel[:] = self.dof_vel
    self.last_root_vel[:] = torch.cat((self.root_lin_vel_w, self.root_ang_vel_w), -1)
    self.last_feet_pos[:] = self.feet_pos
    self.last_feet_yaw[:] = self.feet_yaw
    self.last_feet_contact[:] = self.feet_contact
    self.last_ball_pos[:] = self.ball_state[:, :3]
    self.last_ball_vel[:] = self.ball_state[:, 7:10]
    self.last_kick_pose_distance[:] = self.current_kick_pose_distance
    self.last_relative_ball_pos[:] = self.ball_pos[:, :2]
    self.last_world_pose[:] = self.current_world_pose

    for a, cols in zip(self.leg_actuators, self._act_cols, strict=True):
      self.torques[:, cols] = a.pop_mean_torque()
      self.custom_dof_vel[:, cols] = a.vel_fd

    self._read_robot()
    self._read_ball()
    fw = cfg.filter_weight
    self.filtered_lin_vel[:] = self.base_lin_vel * fw + self.filtered_lin_vel * (1 - fw)
    self.filtered_ang_vel[:] = self.base_ang_vel * fw + self.filtered_ang_vel * (1 - fw)
    self.feet_vel[:] = self.robot.data.body_link_lin_vel_w[:, self.feet_ids]
    self.feet_vel_filtered[:] = self.feet_vel * 0.3 + self.feet_vel_filtered * 0.7
    self._refresh_feet_state()

    self.episode_length_buf += 1
    actions_gait = self.action_term.actions_gait
    self.gait_process[:] = torch.fmod(self.gait_process + dt * actions_gait, 1.0)

    self.buffered_global_ball_pos[:] = self.buffered_global_ball_pos.roll(-1, dims=1)
    self.buffered_global_ball_pos[:, -1] = self.ball_state[:, :3]
    self.request_changed += 1

    self._update_kick_tensors()

    l_dis, r_dis = self.ball_sole_distance()
    min_distance = torch.minimum(l_dis, r_dis)
    candidates = (
      (self.ball_close_to_kick_pose < 1.0)
      & (min_distance < 0.5)
      & (min_distance > 0.25)
      & (self.ball_kicked_counter == 0)
    )
    request = candidates & (torch.rand_like(min_distance) < cfg.reset_ball_request)
    ids = request.nonzero(as_tuple=False).flatten()
    if len(ids) > 0:
      self._resample_kick_ball(ids)
      self.request_changed[ids] = 0

    self._kick_robots()
    self._push_robots()
    self._update_odometry_buffer()
    self._check_termination()
    self.ball_kick_direction_reward[:] = self.helper_ball_kick_direction()
    self._log_kicks()

  def _update_kick_tensors(self) -> None:
    cfg = self.cfg
    dt = self.dt
    yaw = self.yaw
    bs = self.ball_state
    radius = self.ball_contact_radius

    # 1) Ball kicked?
    l_dis, r_dis = self.ball_sole_distance()
    min_distance = torch.minimum(l_dis, r_dis)
    ball_acc = (bs[:, 7:9] - self.last_ball_vel[:, :2]).norm(dim=-1)
    is_right = l_dis >= r_dis
    sel = (~is_right).unsqueeze(-1)
    sole_movement = torch.where(
      sel,
      self.feet_pos[:, 0, :2] - self.last_feet_pos[:, 0, :2],
      self.feet_pos[:, 1, :2] - self.last_feet_pos[:, 1, :2],
    )
    sole_to_ball = torch.where(
      sel, bs[:, :2] - self.feet_pos[:, 0, :2], bs[:, :2] - self.feet_pos[:, 1, :2]
    )
    kick_sole_direction = torch.atan2(sole_movement[:, 1], sole_movement[:, 0])
    sole_speed = sole_movement.norm(dim=-1) / dt
    sole_to_ball_direction = torch.atan2(sole_to_ball[:, 1], sole_to_ball[:, 0])
    kick_height = self.feet_height_over_ground.gather(
      1, is_right.long().unsqueeze(1)
    ).squeeze(1)
    self.allow_ball_kick[:] = (
      (wrap(kick_sole_direction - sole_to_ball_direction).abs() < _PI / 2.0)
      & (self.episode_length_buf > 5)
      & (sole_speed > 0.1)
      & (kick_height > 0.003)
    ) | (self.episode_length_buf > 50)
    still_kick = (self.ball_still_counter > 10) & (ball_acc > 0.01)
    moved_kick = (ball_acc > 0.1) & self.allow_ball_kick
    kicked = (still_kick | moved_kick | self.heavy_ball) & (
      min_distance < radius + 0.04
    )
    self.ball_kicked_counter += ((self.ball_kicked_counter > 0) | kicked).float()

    # 2) Ball position at kick start.
    self.ball_pos_at_kick[:] = torch.where(
      (self.ball_kicked_counter == 0).unsqueeze(-1), bs[:, :3], self.ball_pos_at_kick
    )

    # 3) Ball relative to the point between the soles.
    self.origin_pos[:] = self._sole_origin()
    self.current_world_pose[:, :2] = self.origin_pos[:, :2]
    self.current_world_pose[:, 2] = yaw
    self.ball_velocity_norm[:] = bs[:, 7:10].norm(dim=-1)

    # 3.2) Freeze the observed ball during some kicks (real robots often lose
    # the ball while kicking).
    first = self.ball_kicked_counter == 1
    self.ball_freeze_at_kick |= first & (
      torch.rand_like(self.yaw) < cfg.ball_freeze_at_kick
    )

    # 3.3) Observed ball position (delayed 0-2 steps) and velocity.
    idx = torch.arange(self.num_envs, device=self.device)
    seen = self.buffered_global_ball_pos[idx, self.delay_ball_pos]
    pos = torch.where(
      self.ball_freeze_at_kick.unsqueeze(-1), self.ball_pos_at_kick, seen
    )
    self.ball_pos[:] = quat_apply_inverse(self.base_quat_z, pos - self.origin_pos)
    self.ball_pos[:, 2] = 0.0
    self.ball_vel[:] = quat_apply_inverse(self.base_quat_z, bs[:, 7:10])
    self.ball_vel[:, 2] = 0.0

    # 4) Kick direction / range point at the target, also while rolling.
    ball_to_target = self.ball_end_target - bs[:, :2]
    global_direction = torch.atan2(ball_to_target[:, 1], ball_to_target[:, 0])
    self.direction_angle[:] = wrap(global_direction - self.robot_direction_ref) / _PI
    self.range[:] = ball_to_target.norm(dim=-1).clip(max=cfg.kick_strong_range)
    self.direction_angle_current[:] = wrap(
      self.direction_angle * _PI - (yaw - self.robot_direction_ref)
    )

    # 5) Bookkeeping; slow an incoming fast ball.
    ball_distance = self.ball_pos[:, :2].norm(dim=-1)
    zero = torch.zeros_like(yaw)
    self.ball_still_counter[:] = torch.where(
      self.ball_kicked_counter > 0,
      self.ball_still_counter,
      torch.where(self.ball_velocity_norm < 1e-4, self.ball_still_counter + 1, zero),
    )
    self.ball_velocity_norm_at_kick[:] = torch.where(
      self.ball_kicked_counter <= 1,
      self.ball_velocity_norm,
      torch.maximum(self.ball_velocity_norm_at_kick, self.ball_velocity_norm),
    )
    self.ball_vel_before_kick[:] = torch.where(
      self.ball_kicked_counter > 0, self.ball_vel_before_kick, self.ball_velocity_norm
    )
    slow = (self.ball_kicked_counter == 0) & (self.ball_velocity_norm > 1.5)
    factor = torch.where(slow, 0.97 - 0.2 * (ball_distance - 2).clip(min=0.0), 1.0)
    bs[:, 7:10] *= factor.unsqueeze(-1)

    # 6) Ball in the kick-direction frame.
    dac = wrap(self.direction_angle_current)
    rotation_ratio = ((dac.abs() - cfg.ball_rotation_offset) / 0.4).clip(0.0, 1.0)
    biak = self.ball_pos.clone()
    biak[:, :2] = rot2d(self.ball_pos[:, :2], -dac)

    # 7) Overshooting left / right of the kick leg.
    old_obvious = self.kick_leg_was_obvious.clone()
    by = biak[:, 1]
    self.kick_leg_was_obvious[:] = torch.where(
      (self.kick_leg_was_obvious * by > 0) | (by.abs() > 0.05),
      torch.sign(by).long(),
      0,
    )
    self.ball_walk_target_overshoot[:] = torch.where(
      (old_obvious != self.kick_leg_was_obvious)
      & (self.kick_leg_was_obvious == 0)
      & (self.episode_length_buf > 25),
      10,
      self.ball_walk_target_overshoot - 1,
    )

    # 8) Kick pose.
    r0, r1 = cfg.ball_y_dis_ratio
    y_ratio = ((by.abs() - r0 * cfg.kick_pose_y_off) / (r1 * BALL_RADIUS)).clip(
      0.0, 1.0
    )
    self.kick_pose_translation_ratio[:] = (
      (torch.atan2(by, biak[:, 0]).abs() - 0.3) / 1.2
    ).clip(0.0, 1.0)
    dist_ratio = ((ball_distance - cfg.ball_distance_offset) / 0.4).clip(0.0, 1.0)
    pose_ratio = torch.maximum(
      torch.maximum(dist_ratio, rotation_ratio), self.kick_pose_translation_ratio
    )
    min_ratio = torch.maximum(y_ratio, pose_ratio)
    close = self.ball_close_to_kick_pose
    self.ball_close_to_kick_pose[:] = torch.clamp(
      -1.0 + 2.0 * min_ratio, close - dt * 2, close + dt * 2
    )
    self.more_harsh_walk_speed_condition[:] = torch.where(
      pose_ratio < 1, 1.0, self.more_harsh_walk_speed_condition - 0.1
    ).clip(min=0.0)
    increase = torch.where(
      self.ball_kicked_counter > 0, 0.0, cfg.kick_pose_increase_value
    )
    self.inside_kick_pose_counter[:] = torch.where(
      (self.ball_close_to_kick_pose < 1) | (self.ball_kicked_counter > 1),
      (self.inside_kick_pose_counter + increase).clip(max=1.0),
      0.0,
    )
    lowpass = torch.where(min_ratio == 1.0, 0.9, 0.2).unsqueeze(-1)
    self.filtered_ball_pos[:] = (
      1.0 - lowpass
    ) * self.filtered_ball_pos + lowpass * biak
    kp0, kp1 = cfg.kick_pose_x
    offset = kp0 + (kp1 - kp0) * self.ball_close_to_kick_pose.clip(min=0.0)
    cos_dir, sin_dir = torch.cos(global_direction), torch.sin(global_direction)
    self.ball_kick_pose[:, 0] = bs[:, 0] + cos_dir * offset
    self.ball_kick_pose[:, 1] = bs[:, 1] + sin_dir * offset
    self.current_kick_pose_distance[:] = (
      self.ball_kick_pose[:, :2] - self.base_pos[:, :2]
    ).norm(dim=-1)

    # 9.1) Random ball velocity near the robot.
    near = (
      (self.ball_kicked_counter == 0)
      & ~self.changed_ball_vel
      & (min_distance > 0.35)
      & (min_distance < 0.55)
    )
    ids = (near & (torch.rand_like(yaw) < cfg.add_ball_vel)).nonzero().flatten()
    if len(ids) > 0:
      vmax = cfg.add_ball_vel_max_velocity
      self.ball_vel[ids, 0] = torch.rand(len(ids), device=self.device) * vmax
      self.ball_vel[ids, 1] = (
        torch.rand(len(ids), device=self.device) * vmax - 0.5
      ) * 2.0
      bs[ids, 7:9] = quat_apply(self.base_quat_z[ids], self.ball_vel[ids])[:, :2]
      self.changed_ball_vel[ids] = True

    # 9.2) Random ball velocity along the kick direction.
    near = (
      (self.ball_kicked_counter == 0)
      & ~self.changed_ball_vel
      & (min_distance > 0.35)
      & (min_distance < 0.55)
      & (self.kick_pose_translation_ratio < 1)
      & (self.ball_pos[:, 0] > 0)
    )
    ids = (near & (torch.rand_like(yaw) < cfg.add_ball_vel_in_direction)).nonzero()
    ids = ids.flatten()
    if len(ids) > 0:
      strength = (torch.rand(len(ids), device=self.device) + 1.0) / 2.0
      vdir = apply_rand(
        self.direction_angle_current[ids].clone(), cfg.ball_vel_in_direction_range
      )
      vmax = cfg.add_ball_vel_in_direction_max_velocity
      self.ball_vel[ids, 0] = torch.cos(vdir) * vmax * strength
      self.ball_vel[ids, 1] = torch.sin(vdir) * vmax * strength
      bs[ids, 7:9] = quat_apply(self.base_quat_z[ids], self.ball_vel[ids])[:, :2]
      self.changed_ball_vel[ids] = True

    # 9.3) Isaac Gym's per-actor ball damping (applied every substep there,
    # once per policy step here), its speed cap, then write the ball back.
    steps = self.cfg.decimation
    h = self._env.physics_dt
    bs[:, 7:10] *= (1.0 / (1.0 + h * cfg.ball_linear_damping)) ** steps
    bs[:, 10:13] *= (1.0 / (1.0 + h * cfg.ball_angular_damping)) ** steps
    speed = bs[:, 7:10].norm(dim=-1, keepdim=True)
    bs[:, 7:10] *= (cfg.ball_max_linear_velocity / speed.clamp(min=1e-6)).clip(max=1.0)
    self._write_ball()

    # 10) Kick sole yaw relative to the kick direction.
    fyl = yaw_of(self.feet_quat[:, 0])
    fyr = yaw_of(self.feet_quat[:, 1])
    left = l_dis < r_dis
    target_yaw = torch.where(left, 1.0, -1.0) * cfg.target_sole_yaw_angle
    diff = wrap(target_yaw - (torch.where(left, fyl, fyr) - global_direction))
    ratio = torch.exp(-diff.square() / cfg.target_sole_yaw_sigma)
    self.kick_sole_yaw_ratio[:] = torch.where(
      self.ball_kicked_counter <= 1,
      ratio,
      torch.minimum(ratio, self.kick_sole_yaw_ratio),
    )

  def _kick_robots(self) -> None:
    """Random impulse: add to the base velocity every ``kick_interval_s``."""
    cfg = self.cfg
    step = self._env.common_step_counter
    if step % math.ceil(cfg.kick_interval_s / self.dt) != 0:
      return
    lin = self.root_lin_vel_w.clone()
    ang = self.root_ang_vel_w.clone()
    lin[:, :2] = apply_rand(lin[:, :2], gauss(cfg.kick_lin_vel))
    lin[:, 2] = apply_rand(lin[:, 2], gauss(cfg.kick_lin_vel_z))
    ang = apply_rand(ang, gauss(cfg.kick_ang_vel))
    self.root_lin_vel_w[:] = lin
    self.root_ang_vel_w[:] = ang
    self.robot.write_root_link_velocity_to_sim(torch.cat((lin, ang), -1))

  def _push_robots(self) -> None:
    """Lateral force / torque on the trunk (body frame) for ``push_duration_s``."""
    cfg = self.cfg
    step = self._env.common_step_counter
    period = math.ceil(cfg.push_interval_s / self.dt)
    if step % period == 0:
      self.pushing_forces.zero_()
      self.pushing_forces[:, 1] = cfg.push_force * torch.randn_like(self.yaw)
      self.pushing_torques[:] = cfg.push_torque * torch.randn_like(self.pushing_torques)
    elif step % period == math.ceil(cfg.push_duration_s / self.dt):
      self.pushing_forces.zero_()
      self.pushing_torques.zero_()
    # Isaac Gym applied it in LOCAL_SPACE; xfrc_applied is world frame.
    f = quat_apply(self.base_quat, self.pushing_forces).unsqueeze(1)
    t = quat_apply(self.base_quat, self.pushing_torques).unsqueeze(1)
    self.robot.write_external_wrench_to_sim(f, t, body_ids=[0])

  def _update_odometry_buffer(self) -> None:
    lw, cw = self.last_world_pose, self.current_world_pose
    ll = rot2d(self.last_feet_pos[:, 0, :2] - lw[:, :2], -lw[:, 2])
    lr = rot2d(self.last_feet_pos[:, 1, :2] - lw[:, :2], -lw[:, 2])
    cl = rot2d(self.feet_pos[:, 0, :2] - cw[:, :2], -cw[:, 2])
    cr = rot2d(self.feet_pos[:, 1, :2] - cw[:, :2], -cw[:, 2])
    left_up = self.feet_height_over_ground[:, 0] > self.feet_height_over_ground[:, 1]
    trans = (
      torch.where(left_up.unsqueeze(-1), (ll - lr) - (cl - cr), (cr - cl) - (lr - ll))
      * 0.5
    )
    rot = cw[:, 2] - lw[:, 2]
    self.odo_buffer[:] = self.odo_buffer.roll(-1, dims=1)
    self.odo_buffer[:, -1] = torch.cat((trans.abs(), rot.abs().unsqueeze(-1)), -1)

  def _check_termination(self) -> None:
    cfg = self.cfg
    dt = self.dt
    self.reset_ball[:] = False
    vel_sq = torch.cat((self.root_lin_vel_w, self.root_ang_vel_w), -1).square().sum(-1)
    terminated = vel_sq > cfg.terminate_vel
    height = self.base_pos[:, 2] - self.heights(self.base_pos)
    self.terminate_counter += (
      (self.terminate_counter > 0) | (height < cfg.terminate_height)
    ).float()
    terminated |= self.terminate_counter > cfg.terminate_time / dt
    time_out = self.episode_length_buf > math.ceil(cfg.episode_length_s / dt)

    threshold = torch.full_like(self.yaw, float(cfg.time_after_kick))
    threshold[self.heavy_ball] *= 3
    self.reset_ball |= self.ball_kicked_counter >= threshold

    l_dis, r_dis = self.ball_sole_distance()
    min_dist = torch.minimum(l_dis, r_dis)
    p0, p1, p2 = cfg.random_ball_reset
    p = torch.full_like(self.yaw, p0)
    p[self.flag_allow_deviation] = p1
    p[self.flag_allow_deviation & self.flag_is_strong_kick] = p2
    kicks = cfg.episode_number_of_kicks
    random_reset = (
      (torch.rand_like(p) < p)
      & (self.ball_reset_counter < kicks)
      & (
        (
          (self.ball_close_to_kick_pose < 1.0)
          & (min_dist < FEET_EDGE_POS[0][0] + BALL_RADIUS)
        )
        | (self.ball_kicked_counter > 1)
      )
    )
    self.reset_ball |= random_reset
    lo, hi = cfg.distance_reset
    distance_reset = (
      (self.ball_reset_counter < kicks) & (min_dist < hi) & (min_dist > lo)
    ) & (torch.rand_like(p) < cfg.random_ball_distance_reset)
    self.reset_ball |= distance_reset

    self.ball_reset_counter += (
      self.reset_ball & (self.ball_kicked_counter > 0)
    ).float()
    time_out |= (self.ball_reset_counter > kicks) & self.reset_ball
    self.terminated[:] = terminated & ~time_out
    self.time_out_buf[:] = time_out
    reset = terminated | time_out
    # Booster Gym also cuts the return (bootstrap from the value) whenever the
    # kick-type timer fires, without resetting anything.
    self.bootstrap_buf[:] = time_out | (
      self.episode_length_buf == self.cmd_resample_time
    )
    self.reset_ball &= ~reset

  def _log_kicks(self) -> None:
    done = self.ball_kicked_counter == 3
    if not bool(done.any()):
      return
    angle = wrap(
      torch.atan2(self.ball_vel[:, 1], self.ball_vel[:, 0])
      - self.direction_angle_current
    )
    self.metrics["kicks"] += done.float()
    self.metrics["kick_speed"] = torch.where(
      done, self.ball_velocity_norm_at_kick, self.metrics["kick_speed"]
    )
    self.metrics["kick_angle_error"] = torch.where(
      done, angle.abs(), self.metrics["kick_angle_error"]
    )

  # T1_Ball._reset_idx.

  def _resample_command(self, env_ids: torch.Tensor) -> None:
    cfg = self.cfg
    n = len(env_ids)
    if n == 0:
      return
    dev = self.device
    # Joints around the default pose.
    dof = self.default_dof_pos + cfg.init_dof_pos * torch.randn(n, 12, device=dev)
    self.dof_pos[env_ids] = dof
    self.dof_vel[env_ids] = 0.0
    self.custom_dof_vel[env_ids] = 0.0
    self.last_dof_vel[env_ids] = 0.0
    pos = self.robot.data.default_joint_pos[env_ids].clone()
    pos[:, self.leg_ids] = dof
    vel = torch.zeros_like(pos)
    self.robot.write_joint_state_to_sim(pos, vel, env_ids=env_ids)

    # Root: random spot on the field, random yaw, small velocity.
    root = torch.zeros(n, 13, device=dev)
    root[:, :2] = self._spawn_xy(n)
    root[:, 2] = self.robot.data.default_root_state[env_ids, 2] + self.heights(
      root[:, :2]
    )
    zero = torch.zeros(n, device=dev)
    yaw = torch.rand(n, device=dev) * 2 * _PI
    root[:, 3:7] = quat_from_euler_xyz(zero, zero, yaw)
    root[:, 7:9] = cfg.init_base_lin_vel_xy * torch.randn(n, 2, device=dev)
    root[:, 9] = cfg.init_base_lin_vel_z * torch.randn(n, device=dev)
    root[:, 10:13] = cfg.init_base_ang_vel_xyz * torch.randn(n, 3, device=dev)
    self.robot.write_root_state_to_sim(root, env_ids)
    self.base_pos[env_ids] = root[:, :3]
    self.base_quat[env_ids] = root[:, 3:7]
    self.yaw[env_ids] = yaw
    self.base_quat_z[env_ids] = root[:, 3:7]
    self.root_lin_vel_w[env_ids] = root[:, 7:10]
    self.root_ang_vel_w[env_ids] = root[:, 10:13]
    self._reset_ball_root_states(env_ids)

    self.last_root_vel[env_ids] = root[:, 7:13]
    self.filtered_lin_vel[env_ids] = 0.0
    self.filtered_ang_vel[env_ids] = 0.0
    self.terminate_counter[env_ids] = 0
    self.ball_reset_counter[env_ids] = 0
    self.feet_swing_counter[env_ids] = 0

    # Gains: all joints, then ankles and hip rolls on their own ranges.
    def u(lo_hi: tuple[float, float], *shape: int) -> torch.Tensor:
      lo, hi = lo_hi
      return lo + (hi - lo) * torch.rand(n, *shape, device=dev)

    kp = self.default_kp * u(cfg.dof_stiffness, 12) * u(cfg.dof_stiffness, 12)
    kd = self.default_kd * u(cfg.dof_damping, 12) * u(cfg.dof_damping, 12)
    ankles = [4, 5, 10, 11]
    hip_rolls = [1, 7]
    kp[:, ankles] = self.default_kp[ankles] * u(cfg.dof_ankle_stiffness, 4)
    kd[:, ankles] = self.default_kd[ankles] * u(cfg.dof_ankle_damping, 4)
    kp[:, hip_rolls] = self.default_kp[hip_rolls] * u(cfg.dof_hiproll_stiffness, 2)
    kd[:, hip_rolls] = self.default_kd[hip_rolls] * u(cfg.dof_hiproll_damping, 2)
    self.dof_stiffness[env_ids] = kp
    self.dof_damping[env_ids] = kd
    for a, cols in zip(self.leg_actuators, self._act_cols, strict=True):
      a.set_gains(env_ids, kp=kp[:, cols], kd=kd[:, cols])

    # Calibration offsets.
    off = torch.zeros(n, 12, device=dev)
    pitch, roll, other = [0, 3, 4, 6, 9, 10], [1, 5, 7, 11], [2, 8]
    off[:, pitch] = cfg.dof_pos_offset_pitch * torch.randn(n, 6, device=dev)
    off[:, roll] = cfg.dof_pos_offset_roll * torch.randn(n, 4, device=dev)
    off[:, other] = cfg.dof_pos_offset_other * torch.randn(n, 2, device=dev)
    self.dof_pos_offset[env_ids] = off

    self._reset_ball_idx(env_ids)
    self.delay_ball_pos[env_ids] = torch.randint(0, 3, (n,), device=dev)
    self._decap_spawn(env_ids)

  def _decap_spawn(self, env_ids: torch.Tensor) -> None:
    """APEX DecAP (training aid, set by the runner): with probability equal to
    the prior's strength, start this episode on a mocap kick take shortly
    before its strike, with the ball where the clip strikes it and the target
    along the clip's kick. Mirrors ``KickLoopCommand._apply_decap_spawn``."""
    decap = getattr(self._env, "decap", None)
    if decap is None or decap.ball_pos is None:
      return
    decap.active[env_ids] = False
    if decap.factor <= 0.0:
      return
    dev = self.device
    ids = env_ids[torch.rand(len(env_ids), device=dev) < decap.factor]
    k = len(ids)
    if k == 0:
      return
    decap.arm(ids)
    frame = decap.clip_starts[decap.clip_id[ids]] + decap.frame[ids]
    root_c = decap.root_pos[frame]
    yaw_c = yaw_of(decap.root_quat[frame])
    yaw_n = self.yaw[ids]
    xy = self.base_pos[ids, :2]
    ground = self.heights(xy)
    decap.capture_anchor(ids, xy, ground + root_c[:, 2], yaw_n)
    decap.refresh(ids)
    decap.write_root(self.robot, ids)
    q = decap.joint_pos[frame]
    nxt = torch.minimum(
      frame + 1,
      decap.clip_starts[decap.clip_id[ids]]
      + decap.clip_lengths[decap.clip_id[ids]]
      - 1,
    )
    qd = (decap.joint_pos[nxt] - q) / self.dt
    pos = self.robot.data.default_joint_pos[ids].clone()
    vel = torch.zeros_like(pos)
    pos[:, self.leg_ids] = q
    vel[:, self.leg_ids] = qd
    self.robot.write_joint_state_to_sim(pos, vel, env_ids=ids)
    dyaw = yaw_n - yaw_c
    c, s_ = torch.cos(dyaw), torch.sin(dyaw)

    def rot(v: torch.Tensor) -> torch.Tensor:
      return torch.stack((c * v[:, 0] - s_ * v[:, 1], s_ * v[:, 0] + c * v[:, 1]), -1)

    ball_c = decap.ball_pos[decap.clip_id[ids]]
    rel = rot(ball_c[:, :2] - root_c[:, :2])
    away = rel / rel.norm(dim=-1, keepdim=True).clamp(min=1e-6)
    clip_radius = float(ball_c[0, 2])
    ball_xy = xy + rel + away * (BALL_RADIUS - clip_radius)
    state = torch.zeros(k, 13, device=dev)
    state[:, :2] = ball_xy
    state[:, 2] = self.heights(ball_xy) + BALL_RADIUS + 0.005
    state[:, 3] = 1.0
    self.ball_state[ids] = state
    self._write_ball(ids)
    self.last_ball_pos[ids] = state[:, :3]
    self.last_ball_vel[ids] = 0.0
    self.buffered_global_ball_pos[ids] = state[:, :3].unsqueeze(1).expand(k, 4, 3)
    to_target = rot(decap.target_xy[decap.clip_id[ids]] - ball_c[:, :2])
    self._direction_once[ids] = wrap(
      torch.atan2(to_target[:, 1], to_target[:, 0]) - yaw_n
    )

  def place_task(
    self,
    env_ids: torch.Tensor,
    ball_xy_b: torch.Tensor,
    direction: torch.Tensor,
    kick_range: torch.Tensor,
    strong: torch.Tensor,
    ball_radius: torch.Tensor,
  ) -> None:
    """Fixed kick task (benchmarks): still ball at ``ball_xy_b`` in the
    robot's yaw frame, kick ``direction`` (rad, relative to the robot's
    heading) over ``kick_range`` m, strong flag; no deviation flags. Takes
    effect at the next ``compute``."""
    self._reset_ball_idx(env_ids)
    self.flag_is_strong_kick[env_ids] = strong
    self.flag_is_inaccurate_kick[env_ids] = 0.0
    self.flag_allow_deviation[env_ids] = False
    n = len(env_ids)
    local = torch.zeros(n, 3, device=self.device)
    local[:, :2] = ball_xy_b
    pos = self.base_pos[env_ids] + quat_apply(self.base_quat_z[env_ids], local)
    pos[:, 2] = self.heights(pos[:, :2]) + ball_radius
    state = torch.zeros(n, 13, device=self.device)
    state[:, :3] = pos
    state[:, 3] = 1.0
    self.ball_state[env_ids] = state
    self._write_ball(env_ids)
    self.last_ball_pos[env_ids] = pos
    self.last_ball_vel[env_ids] = 0.0
    self.buffered_global_ball_pos[env_ids] = pos.unsqueeze(1).expand(n, 4, 3)
    self.task_direction[env_ids] = direction
    self.task_range[env_ids] = kick_range
    self._pending_kick_ball[env_ids] = True

  def _spawn_xy(self, n: int) -> torch.Tensor:
    """B-Human spreads env origins over the field (+-1 m); here each reset
    picks a fresh spot so robots see every strip type."""
    h = self.heights
    if not h.enabled:
      r = self.cfg.init_base_pos_xy
      return (torch.rand(n, 2, device=self.device) * 2 - 1) * r
    lo = h.inner_lo + 1.0
    hi = h.inner_hi - 1.0
    return lo + (hi - lo) * torch.rand(n, 2, device=self.device)

  def _set_delay(self, env_ids: torch.Tensor) -> None:
    d = torch.randint(0, self.cfg.decimation, (len(env_ids),), device=self.device)
    for a in self.leg_actuators:
      a.delay[env_ids] = d

  def _reset_ball_idx(self, env_ids: torch.Tensor) -> None:
    cfg = self.cfg
    n = len(env_ids)
    if n == 0:
      return
    dev = self.device
    self._resample_input_flags(env_ids)
    self.ball_close_to_kick_pose[env_ids] = 1
    self.ball_kicked_counter[env_ids] = 0
    self.ball_vel_before_kick[env_ids] = 0
    self.ball_still_counter[env_ids] = 0
    self.inside_kick_pose_counter[env_ids] = 0
    self.changed_ball_vel[env_ids] = False
    keep = torch.rand(n, device=dev) <= cfg.keep_old_ball_when_reset
    self._reset_ball_root_states(env_ids[~keep])
    self._pending_kick_ball[env_ids] = True
    self._set_delay(env_ids)
    self.episode_length_buf[env_ids] = 0
    self.cmd_resample_time[env_ids] = self._resample_time(n)
    self.allow_ball_kick[env_ids] = False
    self.ball_walk_target_overshoot[env_ids] = 0
    self.kick_leg_was_obvious[env_ids] = 0
    self.kick_sole_yaw_ratio[env_ids] = 0
    self.odo_buffer[env_ids] = 0
    self.ball_freeze_at_kick[env_ids] = False
    sx, sy = cfg.ball_pos_odo_noise
    self.odo_noise_factor[env_ids, 0] = sx * torch.randn(n, device=dev)
    self.odo_noise_factor[env_ids, 1] = sy * torch.randn(n, device=dev)

  def _resample_time(self, n: int) -> torch.Tensor:
    lo, hi = self.cfg.resampling_kick_type
    return torch.randint(int(lo / self.dt), int(hi / self.dt), (n,), device=self.device)

  def _reset_ball_root_states(self, env_ids: torch.Tensor) -> None:
    cfg = self.cfg
    n = len(env_ids)
    if n == 0:
      return
    dev = self.device
    self.request_changed[env_ids] = 0
    bs = self.ball_state
    # "Second half" of the field gets a rolling ball (B-Human: x >= env_width/2).
    h = self.heights
    if h.enabled:
      mid = 0.5 * (h.inner_lo[0] + h.inner_hi[0])
      rolling = bs[env_ids, 0] >= mid
    else:
      rolling = env_ids % 2 == 1
    x = torch.zeros(n, device=dev)
    x = torch.where(
      rolling,
      apply_rand(x, cfg.init_ball_pos_far_x),
      apply_rand(x, cfg.init_ball_pos_x),
    )
    rot = torch.randint(-180, 180, (n,), device=dev) / 180.0 * _PI
    local = torch.zeros(n, 3, device=dev)
    local[:, 0] = x * torch.cos(rot)
    local[:, 1] = x * torch.sin(rot)
    base = self.base_pos[env_ids]
    pos = base + quat_apply(self.base_quat[env_ids], local)
    pos[:, 2] = self.heights(pos[:, :2]) + BALL_RADIUS + cfg.ball_radius_range[1] + 0.01
    vel = torch.zeros(n, 3, device=dev)
    vel[:, :2] = torch.where(
      rolling.unsqueeze(-1), apply_rand(vel[:, :2], cfg.init_ball_vel), 0.0
    )
    toward = rolling & (torch.rand(n, device=dev) < 0.05)
    to_robot = base[:, :2] - pos[:, :2]
    d = to_robot.norm(dim=-1, keepdim=True)
    aimed = torch.where(d > 0, to_robot / d.clamp(min=1e-9), 0.0) * vel[:, :2].norm(
      dim=-1, keepdim=True
    )
    vel[:, :2] = torch.where(toward.unsqueeze(-1), aimed, vel[:, :2])

    # 10 % still balls right next to the robot (learn to walk around it).
    close = torch.rand(n, device=dev) < cfg.force_ball_close
    near_r = torch.where(
      rolling, cfg.init_ball_pos_far_x.lo, cfg.init_ball_pos_x.lo
    ).unsqueeze(-1)
    out = pos[:, :2] - base[:, :2]
    out = out / out.norm(dim=-1, keepdim=True).clamp(min=1e-9)
    pos[:, :2] = torch.where(
      close.unsqueeze(-1), base[:, :2] + out * near_r, pos[:, :2]
    )
    vel[:, :2] = torch.where(close.unsqueeze(-1), 0.0, vel[:, :2])

    state = torch.zeros(n, 13, device=dev)
    state[:, :3] = pos
    state[:, 3] = 1.0
    state[:, 7:10] = vel
    bs[env_ids] = state
    self._write_ball(env_ids)
    self.last_ball_pos[env_ids] = pos
    self.last_ball_vel[env_ids] = vel
    self.buffered_global_ball_pos[env_ids] = pos.unsqueeze(1).expand(n, 4, 3)

  def _resample_input_flags(self, env_ids: torch.Tensor) -> None:
    cfg = self.cfg
    n = len(env_ids)
    dev = self.device
    self.flag_is_strong_kick[env_ids] = torch.rand(n, device=dev) < 0.5
    self.flag_is_inaccurate_kick[env_ids] = (torch.rand(n, device=dev) < 0.3).float()
    self.flag_allow_deviation[env_ids] = torch.rand(n, device=dev) < 0.5
    self.flag_allow_deviation[self.heavy_ball] = True
    if cfg.disable_deviation_flag:
      self.flag_allow_deviation[:] = False
    if cfg.disable_extra_deviation_flag:
      self.flag_is_inaccurate_kick[:] = 0.0

  def _resample_kick_ball(self, env_ids: torch.Tensor) -> None:
    """New kick target for the ball where it is (``_resample_kick_ball``)."""
    cfg = self.cfg
    n = len(env_ids)
    if n == 0:
      return
    dev = self.device
    bs = self.ball_state
    yaw = self.yaw[env_ids]
    origin = self._sole_origin()[env_ids]
    self.origin_pos[env_ids] = origin
    self.current_world_pose[env_ids, :2] = origin[:, :2]
    self.current_world_pose[env_ids, 2] = yaw
    self.last_world_pose[env_ids] = self.current_world_pose[env_ids]
    qz = self.base_quat_z[env_ids]
    ball_pos = quat_apply_inverse(qz, bs[env_ids, :3] - origin)
    ball_pos[:, 2] = 0.0
    self.ball_pos[env_ids] = ball_pos
    self.last_relative_ball_pos[env_ids] = ball_pos[:, :2]
    ball_vel = quat_apply_inverse(qz, bs[env_ids, 7:10])
    ball_vel[:, 2] = 0.0
    self.ball_vel[env_ids] = ball_vel

    direction = torch.rand(n, device=dev) * 2 - 1
    strong = self.flag_is_strong_kick[env_ids]
    rng = apply_rand(torch.zeros(n, device=dev), cfg.kick_normal_range)
    rng = torch.where(strong, cfg.kick_strong_range, rng)
    # Fixed tasks (benchmarks) replace the random direction / range.
    fixed_dir = self.task_direction[env_ids]
    fixed_dir = torch.where(fixed_dir.isnan(), self._direction_once[env_ids], fixed_dir)
    self._direction_once[env_ids] = float("nan")
    fixed_rng = self.task_range[env_ids]
    direction = torch.where(fixed_dir.isnan(), direction, fixed_dir / _PI)
    rng = torch.where(fixed_rng.isnan(), rng, fixed_rng)
    self.direction_angle[env_ids] = direction
    self.robot_direction_ref[env_ids] = yaw
    dac = wrap(direction * _PI)
    self.direction_angle_current[env_ids] = dac
    self.range[env_ids] = rng
    gdir = wrap(yaw + direction * _PI)
    cos_d, sin_d = torch.cos(gdir), torch.sin(gdir)
    self.ball_end_target[env_ids, 0] = bs[env_ids, 0] + cos_d * rng
    self.ball_end_target[env_ids, 1] = bs[env_ids, 1] + sin_d * rng
    self.ball_kick_pose[env_ids, 0] = bs[env_ids, 0] + cos_d * -0.35
    self.ball_kick_pose[env_ids, 1] = bs[env_ids, 1] + sin_d * -0.35
    dist = (bs[env_ids, :2] - self.base_pos[env_ids, :2]).norm(dim=-1)
    self.current_kick_pose_distance[env_ids] = dist
    self.last_kick_pose_distance[env_ids] = dist
    self.ball_close_to_kick_pose[env_ids] = 1
    self.ball_kicked_counter[env_ids] = 0
    self.inside_kick_pose_counter[env_ids] = 0
    self.ball_still_counter[env_ids] = 0
    self.ball_vel_before_kick[env_ids] = 0
    biak = ball_pos.clone()
    biak[:, :2] = rot2d(ball_pos[:, :2], -dac)
    self.filtered_ball_pos[env_ids] = biak
    self.last_ball_pos[env_ids] = bs[env_ids, :3]
    self.last_ball_vel[env_ids] = bs[env_ids, 7:10]
    self.ball_request_resetted[env_ids] = False

  # After resets: ball-only resets, wrap-around, kick-type timer.

  def compute(self, dt: float) -> None:
    ids = self.reset_ball.nonzero(as_tuple=False).flatten()
    if len(ids) > 0:
      self._reset_ball_idx(ids)
      self.reset_ball[ids] = False
    self._teleport()
    self._read_robot()
    self.feet_pos[:] = self.robot.data.body_link_pos_w[:, self.feet_ids]
    self.feet_quat[:] = self.robot.data.body_link_quat_w[:, self.feet_ids]
    pending = self._pending_kick_ball.nonzero(as_tuple=False).flatten()
    if len(pending) > 0:
      self._resample_kick_ball(pending)
      self._pending_kick_ball[pending] = False
    self._resample_commands()
    super().compute(dt)

  def _resample_commands(self) -> None:
    l_dis, r_dis = self.ball_sole_distance()
    far = torch.minimum(l_dis, r_dis) > self.ball_contact_radius + 0.04
    ids = ((self.episode_length_buf == self.cmd_resample_time) & far).nonzero()
    ids = ids.flatten()
    if len(ids) > 0:
      self.cmd_resample_time[ids] += self._resample_time(len(ids))

  def _teleport(self) -> None:
    """Wrap robots and balls that leave the field (``_teleport_robot``)."""
    h = self.heights
    if not h.enabled:
      return
    b = h.border
    width = h.inner_hi - h.inner_lo + b  # env_width / length + border
    lo = h.inner_lo - 0.75 * b
    hi = h.inner_hi + 0.75 * b

    def shift(xy: torch.Tensor) -> torch.Tensor:
      return (xy < lo).float() * width - (xy > hi).float() * width

    bs = self.ball_state
    bshift = shift(bs[:, :2])
    fell = bs[:, 2] < self.heights(bs[:, :2]) - 0.5
    if bool((bshift != 0).any() | fell.any()):
      bs[:, :2] += bshift
      bs[:, 2] = torch.where(fell, 0.3 + self.heights(bs[:, :2]), bs[:, 2])
      self.buffered_global_ball_pos[..., :2] += bshift.unsqueeze(1)
      self.ball_end_target += bshift
      self.ball_pos_at_kick[:, :2] += bshift
      self.last_ball_pos[:, :2] += bshift
      self._write_ball()
    rshift = shift(self.base_pos[:, :2])
    moved = (rshift != 0).any(dim=-1)
    if bool(moved.any()):
      ids = moved.nonzero().flatten()
      pose = torch.cat((self.base_pos[ids], self.base_quat[ids]), -1)
      pose[:, :2] += rshift[ids]
      self.robot.write_root_link_pose_to_sim(pose, ids)
      self.base_pos[ids, :2] += rshift[ids]
      self.last_world_pose[ids, :2] += rshift[ids]
      self.current_world_pose[ids, :2] += rshift[ids]
      self.feet_pos[ids, :, :2] += rshift[ids].unsqueeze(1)
      self.last_feet_pos[ids, :, :2] += rshift[ids].unsqueeze(1)

  # Observations (T1_Ball._compute_observations).

  def _noise(self, x: torch.Tensor, sigma: float) -> torch.Tensor:
    if not self.cfg.observation_noise:
      return x
    return x + sigma * torch.randn_like(x)

  def actor_obs(self) -> torch.Tensor:
    cfg = self.cfg
    noisy = cfg.observation_noise
    ball = self.ball_pos.clone()
    noise = torch.zeros_like(ball)
    lo, hi = cfg.ball_pos_noise_scale_range
    rx = ((self.ball_pos[:, 0].abs() - lo) / (hi - lo)).clip(0.0, 1.0)
    ry = ((self.ball_pos[:, 1].abs() - lo) / (hi - lo)).clip(0.0, 1.0)
    nx0, nx1 = cfg.ball_pos_noise_x
    ny0, ny1 = cfg.ball_pos_noise_y
    scale = torch.stack(((nx1 - nx0) * rx + nx0, (ny1 - ny0) * ry + ny0), -1)
    if noisy:
      noise[:, :2] = torch.randn_like(scale) * scale
      odo = self.odo_buffer.sum(dim=1)
      noise[:, :2] += self.odo_noise_factor * odo[:, :2]
      noise[:, :2] += 0.2 * (self.odo_noise_factor[:, 1] * odo[:, 2]).unsqueeze(-1)
    ball = ball + noise
    last_ball = self.last_relative_ball_pos + noise[:, :2]
    direction = self._noise(self.direction_angle_current, cfg.ball_direction_noise)
    self.direction[:, 0] = torch.sin(direction)
    self.direction[:, 1] = torch.cos(direction)
    act = self.action_term
    walking = (act.actions_gait > 1.0e-8).float()
    phase = 2 * _PI * self.gait_process
    expected_vel = 1.4142135623 * torch.sqrt(cfg.ball_friction * self.range)

    def ball_vel(axis: int) -> torch.Tensor:
      v = self._noise(self.ball_vel[:, axis], cfg.ball_vel_noise)
      if noisy:
        lo_s, hi_s = cfg.ball_vel_scale_noise
        v = v * (lo_s + (hi_s - lo_s) * torch.rand_like(v))
      return v.unsqueeze(-1) * cfg.norm_ball_vel

    dof = self.dof_pos - self.dof_pos_offset - self.default_dof_pos
    return torch.cat(
      (
        self._noise(self.projected_gravity, cfg.noise_gravity) * cfg.norm_gravity,
        self._noise(self.base_ang_vel, cfg.noise_ang_vel) * cfg.norm_ang_vel,
        ball[:, :2] * cfg.norm_ball_pos,
        (direction / _PI).unsqueeze(-1),
        (torch.cos(phase) * walking).unsqueeze(-1),
        (torch.sin(phase) * walking).unsqueeze(-1),
        self._noise(dof, cfg.noise_dof_pos) * cfg.norm_dof_pos,
        self._noise(self.custom_dof_vel, cfg.noise_dof_vel) * cfg.norm_dof_vel,
        act.actions,
        self.flag_is_strong_kick.float().unsqueeze(-1),
        self.flag_is_inaccurate_kick.unsqueeze(-1),
        self.flag_allow_deviation.float().unsqueeze(-1),
        ball_vel(0),
        ball_vel(1),
        torch.zeros_like(expected_vel).unsqueeze(-1),
        self.direction,
        self._noise(expected_vel, cfg.ball_range_noise).unsqueeze(-1)
        * cfg.norm_ball_kick_range,
        last_ball * cfg.norm_ball_pos,
      ),
      dim=-1,
    )

  def critic_obs(self) -> torch.Tensor:
    cfg = self.cfg
    height = self.base_pos[:, 2] - self.heights(self.base_pos)
    return torch.cat(
      (
        self.base_mass_scaled,
        self._noise(self.base_lin_vel, cfg.noise_lin_vel) * cfg.norm_lin_vel,
        self._noise(height, cfg.noise_height).unsqueeze(-1),
        self.pushing_forces * cfg.norm_push_force,
        self.pushing_torques * cfg.norm_push_torque,
        self.inside_kick_pose_counter.unsqueeze(-1),
        self.ball_close_to_kick_pose.unsqueeze(-1),
      ),
      dim=-1,
    )

  # Reward helpers shared by several terms.

  def helper_ball_kick_direction(self) -> torch.Tensor:
    cfg = self.cfg
    counter = self.ball_kicked_counter
    start = cfg.ball_kicked_start_counter
    clip_factor = torch.where(counter - start > cfg.ball_kicked_clipped_counter, 0, 1)
    time_ratio = 1.0 - ((counter - start) / cfg.ball_kicked_max_counter).clip(0, 1)
    ratio = torch.where(counter > 0, 1, 0)
    angle_diff = wrap(
      self.direction_angle_current
      - torch.atan2(self.ball_vel[:, 1], self.ball_vel[:, 0])
    )
    sigma = torch.full_like(self.yaw, cfg.kick_direction_sigma_range)
    sigma[self.flag_is_inaccurate_kick > 0.5] = cfg.kick_direction_sigma_just_hit
    pose_factor = self.inside_kick_pose_counter.square()
    sole_factor = self.kick_sole_yaw_ratio * 0.5 + 0.5
    pose_factor[self.flag_allow_deviation] = 1
    sole_factor[self.flag_allow_deviation] = 1
    if cfg.disable_sole_yaw_direction_penalty:
      sole_factor[:] = 1
    reward = (
      (torch.exp(-angle_diff.square() / sigma) - 0.5)
      * 2.0
      * ratio
      * time_ratio
      * clip_factor
    )
    base_height = self.base_pos[:, 2] - self.heights(self.base_pos)
    h0, h1 = cfg.base_height_scaling
    height_ratio = ((base_height - h0) / (h1 - h0)).clip(0.0, 1.0)
    vel_scale = 1.0 - 0.9 * self.ball_vel_before_kick.clip(max=2.0) / 2.0
    neg_scale = 0.1 + 0.9 * (
      (self.request_changed - 0.25 / self.dt) / (0.5 / self.dt)
    ).clip(0.0, 1.0)
    return torch.where(
      reward < 0,
      reward * cfg.kick_direction_negative_factor * vel_scale * neg_scale,
      reward * height_ratio * pose_factor * sole_factor,
    )

  def helper_walk_target(self) -> torch.Tensor:
    cfg = self.cfg
    n = self.num_envs
    kick_pose_in_robot = quat_apply_inverse(
      self.base_quat_z, self.ball_kick_pose - self.base_pos
    )
    extra = ((self.kick_pose_translation_ratio - 0.5) / 0.5).clip(min=0.0) * (
      BALL_RADIUS + 0.1
    )
    dac = self.direction_angle_current
    x_off = -torch.sin(dac) * (cfg.kick_pose_y_off + extra)
    y_off = torch.cos(dac) * (cfg.kick_pose_y_off + extra)
    left = kick_pose_in_robot.clone()
    right = kick_pose_in_robot.clone()
    left[:, 0] += x_off
    left[:, 1] += y_off
    right[:, 0] -= x_off
    right[:, 1] -= y_off
    walk_target = torch.where(
      (self.filtered_ball_pos[:, 1] < 0).unsqueeze(-1), left, right
    )
    gdir = self.robot_direction_ref + self.direction_angle * _PI
    zero = torch.zeros(n, device=self.device)
    dq = quat_from_euler_xyz(zero, zero, gdir)
    bir = quat_apply_inverse(dq, self.ball_state[:, :3] - self.base_pos)
    ratio = torch.where(
      self.ball_close_to_kick_pose < 1, 0.0, (-bir[:, 0] / 0.3).clip(0.0, 1.0)
    )
    side = (bir[:, 1].abs() / 0.3).clip(0.0, 1.0)
    bir[:, 0] += (
      side * -0.2 + torch.maximum(-bir[:, 0], 1.0 - side).clip(0.0, 1.0) * 0.3
    )
    bir[:, 1] += (
      torch.where(self.filtered_ball_pos[:, 1] < 0, 1.0, -1.0)
      * cfg.ball_avoidance_range
    )
    side_target = quat_apply_inverse(self.base_quat_z, quat_apply(dq, bir))
    r = ratio.unsqueeze(-1)
    return walk_target * (1.0 - r) + side_target * r

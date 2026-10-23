"""Shared Walk↔Kick handoff helpers (Setup B play + Recipe C train)."""

from __future__ import annotations

import math
import re
from dataclasses import asdict
from pathlib import Path

import torch
from tensordict import TensorDict

from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import MjlabOnPolicyRunner, RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.utils.lab_api.math import quat_apply_inverse, wrap_to_pi, yaw_quat

# Kick Near leg action order (12-D).
KICK_LEG_JOINTS: tuple[str, ...] = (
  "Left_Hip_Pitch",
  "Right_Hip_Pitch",
  "Left_Hip_Roll",
  "Right_Hip_Roll",
  "Left_Hip_Yaw",
  "Right_Hip_Yaw",
  "Left_Knee_Pitch",
  "Right_Knee_Pitch",
  "Left_Ankle_Pitch",
  "Right_Ankle_Pitch",
  "Left_Ankle_Roll",
  "Right_Ankle_Roll",
)

# AMP Walk full-body action / joint-pos order (22-D).
WALK_JOINTS: tuple[str, ...] = (
  "Head_Yaw",
  "Head_Pitch",
  "Left_Shoulder_Pitch",
  "Left_Shoulder_Roll",
  "Left_Elbow_Pitch",
  "Left_Elbow_Yaw",
  "Right_Shoulder_Pitch",
  "Right_Shoulder_Roll",
  "Right_Elbow_Pitch",
  "Right_Elbow_Yaw",
  "Left_Hip_Pitch",
  "Left_Hip_Roll",
  "Left_Hip_Yaw",
  "Left_Knee_Pitch",
  "Left_Ankle_Pitch",
  "Left_Ankle_Roll",
  "Right_Hip_Pitch",
  "Right_Hip_Roll",
  "Right_Hip_Yaw",
  "Right_Knee_Pitch",
  "Right_Ankle_Pitch",
  "Right_Ankle_Roll",
)

WALK_UPPER_JOINTS: tuple[str, ...] = WALK_JOINTS[:10]

DEFAULT_WALK_TASK = "Mjlab-Velocity-Flat-Amp-DA-Muon-Booster-K1"
DEFAULT_WALK_CKPT = Path(
  "logs/rsl_rl/k1_velocity_amp_symmetric_muon_wwcmu50_roughft/"
  "2026-09-21_20-34-24_stageA/model_9950.pt"
)

PHASE_APPROACH = 0
PHASE_KICK = 1
PHASE_EXIT = 2


def resolve_scale_dict(
  scale: float | dict[str, float], joint_names: tuple[str, ...]
) -> torch.Tensor:
  """Match ``BaseAction`` scale dict (regex keys) onto ``joint_names``."""
  out = torch.ones(len(joint_names), dtype=torch.float32)
  if isinstance(scale, (float, int)):
    out[:] = float(scale)
    return out
  for i, name in enumerate(joint_names):
    for pattern, value in scale.items():
      if re.fullmatch(pattern, name):
        out[i] = float(value)
        break
  return out


def load_walk_inference_policy(
  *,
  walk_task: str,
  walk_checkpoint: Path | str,
  device: str,
) -> tuple[object, RslRlVecEnvWrapper]:
  """Load frozen Walk actor via a 1-env shell (caller should ``close`` the env)."""
  ckpt = Path(walk_checkpoint)
  if not ckpt.exists():
    raise FileNotFoundError(f"Walk checkpoint not found: {ckpt}")
  env_cfg = load_env_cfg(walk_task, play=True)
  env_cfg.scene.num_envs = 1
  agent_cfg = load_rl_cfg(walk_task)
  env = ManagerBasedRlEnv(cfg=env_cfg, device=device, render_mode=None)
  env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
  runner_cls = load_runner_cls(walk_task) or MjlabOnPolicyRunner
  runner = runner_cls(env, asdict(agent_cfg), device=device)
  runner.load(
    str(ckpt), load_cfg={"actor": True}, strict=True, map_location=device
  )
  policy = runner.get_inference_policy(device=device)
  return policy, env


class WalkHandoffKit:
  """Pose / twist / obs utilities for Walk↔Kick hard switches."""

  def __init__(
    self,
    *,
    raw_env: ManagerBasedRlEnv,
    walk_scale_full: torch.Tensor,
    kick_scale: torch.Tensor,
    walk_leg_indices: torch.Tensor,
    walk_upper_indices: torch.Tensor,
    enter_facing_rad: float = 0.40,
    enter_tilt_max_rad: float = 0.35,
    enter_speed_max: float = 0.55,
    approach_speed: float = 0.9,
    approach_yaw_gain: float = 2.0,
    approach_turn_speed: float = 1.2,
    fall_min_height: float = 0.40,
    fall_tilt_max_rad: float = 0.85,
  ) -> None:
    self.raw = raw_env
    device = raw_env.device
    self.walk_scale_full = walk_scale_full.to(device)
    self.kick_scale = kick_scale.to(device)
    self.walk_leg_indices = walk_leg_indices.to(device)
    self.walk_upper_indices = walk_upper_indices.to(device)
    self.leg_scale_ratio = (self.walk_scale_full[self.walk_leg_indices] / self.kick_scale)
    self.enter_facing_rad = float(enter_facing_rad)
    self.enter_speed_max = float(enter_speed_max)
    self.enter_upright_gz = -math.cos(float(enter_tilt_max_rad))
    self.approach_speed = float(approach_speed)
    self.approach_yaw_gain = float(approach_yaw_gain)
    self.approach_turn_speed = float(approach_turn_speed)
    self.fall_min_height = float(fall_min_height)
    self.fall_upright_gz = -math.cos(float(fall_tilt_max_rad))
    n = raw_env.num_envs
    self.last_walk_action = torch.zeros(n, len(WALK_JOINTS), device=device)

  def ball_dist(self) -> torch.Tensor:
    robot_xy = self.raw.scene["robot"].data.root_link_pos_w[:, :2]
    ball_xy = self.raw.scene["ball"].data.root_link_pos_w[:, :2]
    return torch.linalg.norm(ball_xy - robot_xy, dim=-1)

  def heading_err_to_ball(self) -> torch.Tensor:
    robot = self.raw.scene["robot"]
    ball = self.raw.scene["ball"]
    delta_w = torch.zeros(self.raw.num_envs, 3, device=self.raw.device)
    delta_w[:, :2] = (
      ball.data.root_link_pos_w[:, :2] - robot.data.root_link_pos_w[:, :2]
    )
    delta_b = quat_apply_inverse(yaw_quat(robot.data.root_link_quat_w), delta_w)
    return wrap_to_pi(torch.atan2(delta_b[:, 1], delta_b[:, 0]))

  def enter_gates(self) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    robot = self.raw.scene["robot"]
    heading_err = self.heading_err_to_ball()
    facing = heading_err.abs() <= self.enter_facing_rad
    upright = robot.data.projected_gravity_b[:, 2] <= self.enter_upright_gz
    speed = torch.linalg.norm(robot.data.root_link_lin_vel_b[:, :2], dim=-1)
    slow = speed <= self.enter_speed_max
    ok = facing & upright & slow
    return ok, {
      "facing": facing,
      "upright": upright,
      "slow": slow,
      "heading_err": heading_err,
      "speed": speed,
    }

  def is_fallen(self) -> torch.Tensor:
    robot = self.raw.scene["robot"]
    low = robot.data.root_link_pos_w[:, 2] < self.fall_min_height
    tipped = robot.data.projected_gravity_b[:, 2] > self.fall_upright_gz
    return low | tipped

  def free_arms(self, env_ids: torch.Tensor) -> None:
    if env_ids.numel() == 0:
      return
    robot = self.raw.scene["robot"]
    q = robot.data.joint_pos[env_ids][:, self.walk_upper_indices]
    robot.set_joint_position_target(
      q, joint_ids=self.walk_upper_indices, env_ids=env_ids
    )

  def apply_walk_upper_body(
    self, a_walk: torch.Tensor, env_ids: torch.Tensor
  ) -> None:
    if env_ids.numel() == 0:
      return
    robot = self.raw.scene["robot"]
    default_q = robot.data.default_joint_pos
    assert default_q is not None
    idx = self.walk_upper_indices
    a_u = a_walk[env_ids][:, idx]
    scale = self.walk_scale_full[idx]
    q_des = a_u * scale + default_q[env_ids][:, idx]
    robot.set_joint_position_target(q_des, joint_ids=idx, env_ids=env_ids)

  def set_twist(
    self,
    env_ids: torch.Tensor,
    vx: torch.Tensor | float,
    vy: torch.Tensor | float,
    wz: torch.Tensor | float,
    *,
    standing: bool = False,
  ) -> None:
    if env_ids.numel() == 0:
      return
    twist = self.raw.command_manager.get_term("twist")
    if isinstance(vx, (float, int)):
      twist.vel_command_b[env_ids, 0] = float(vx)
    else:
      twist.vel_command_b[env_ids, 0] = vx
    if isinstance(vy, (float, int)):
      twist.vel_command_b[env_ids, 1] = float(vy)
    else:
      twist.vel_command_b[env_ids, 1] = vy
    if isinstance(wz, (float, int)):
      twist.vel_command_b[env_ids, 2] = float(wz)
    else:
      twist.vel_command_b[env_ids, 2] = wz
    if twist.vel_command_b.shape[1] > 3:
      twist.vel_command_b[env_ids, 3] = 0.0
    if hasattr(twist, "is_standing_env"):
      twist.is_standing_env[env_ids] = standing
    if hasattr(twist, "vel_command_w"):
      twist.vel_command_w[env_ids, :] = 0.0
      twist.vel_command_w[env_ids, 0] = twist.vel_command_b[env_ids, 0]

  def drive_approach(
    self,
    env_ids: torch.Tensor,
    *,
    stand_hold: torch.Tensor | None = None,
    slow_start_m: float = 1.0,
    slow_floor_m: float = 0.45,
    near_speed_frac: float = 0.50,
  ) -> None:
    """Body-frame Walk cmd toward the ball + yaw to face it.

    Soft-brakes below ``slow_start_m``: speed scales from full cruise down to
    ``near_speed_frac`` of cruise by ``slow_floor_m`` (limits overshoot into
    the enter band without crawling).
    """
    if env_ids.numel() == 0:
      return
    robot = self.raw.scene["robot"]
    ball = self.raw.scene["ball"]
    root_quat = robot.data.root_link_quat_w[env_ids]
    delta_w = torch.zeros(env_ids.numel(), 3, device=self.raw.device)
    delta_w[:, :2] = (
      ball.data.root_link_pos_w[env_ids, :2]
      - robot.data.root_link_pos_w[env_ids, :2]
    )
    dist = torch.linalg.norm(delta_w[:, :2], dim=-1).clamp(min=1e-3)
    delta_b = quat_apply_inverse(yaw_quat(root_quat), delta_w)
    heading_err = wrap_to_pi(torch.atan2(delta_b[:, 1], delta_b[:, 0]))
    wz = (
      self.approach_yaw_gain * heading_err
    ).clamp(-self.approach_turn_speed, self.approach_turn_speed)
    face = (heading_err.abs() < 0.8).float()
    # Distance taper: 1 at ≥slow_start_m → near_speed_frac at ≤slow_floor_m.
    lo = float(slow_floor_m)
    hi = max(float(slow_start_m), lo + 1e-3)
    frac = ((dist - lo) / (hi - lo)).clamp(0.0, 1.0)
    near_frac = float(near_speed_frac)
    speed_scale = near_frac + (1.0 - near_frac) * frac
    speed = self.approach_speed * (0.35 + 0.65 * face) * speed_scale
    dir_b = delta_b[:, :2] / dist.unsqueeze(-1)
    vx = speed * dir_b[:, 0]
    vy = speed * dir_b[:, 1] * 0.35
    standing = torch.zeros(
      env_ids.numel(), dtype=torch.bool, device=self.raw.device
    )
    if stand_hold is not None:
      hold = stand_hold[env_ids]
      vx = torch.where(hold, torch.zeros_like(vx), vx)
      vy = torch.where(hold, torch.zeros_like(vy), vy)
      standing = hold
    self.set_twist(env_ids, vx, vy, wz, standing=False)
    if bool(standing.any()):
      twist = self.raw.command_manager.get_term("twist")
      if hasattr(twist, "is_standing_env"):
        twist.is_standing_env[env_ids[standing]] = True

  def build_walk_obs(self) -> TensorDict:
    robot = self.raw.scene["robot"]
    default_q = robot.data.default_joint_pos
    assert default_q is not None
    q = robot.data.joint_pos_biased - default_q
    default_qd = robot.data.default_joint_vel
    assert default_qd is not None
    qd = robot.data.joint_vel - default_qd
    twist = self.raw.command_manager.get_term("twist")
    cmd = twist.vel_command_b[:, :3]
    actor = torch.cat(
      (
        robot.data.root_link_ang_vel_b,
        robot.data.projected_gravity_b,
        q,
        qd,
        self.last_walk_action,
        cmd,
      ),
      dim=-1,
    )
    assert actor.shape[-1] == 75, f"expected 75-D walk obs, got {actor.shape[-1]}"
    return TensorDict({"actor": actor}, batch_size=[self.raw.num_envs])

  def walk_actions_to_kick(self, a_walk: torch.Tensor) -> torch.Tensor:
    return a_walk[:, self.walk_leg_indices] * self.leg_scale_ratio

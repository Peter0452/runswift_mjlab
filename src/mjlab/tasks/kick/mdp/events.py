"""Kick-task event (reset) functions."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import torch

from mjlab.entity import Entity
from mjlab.envs.mdp.events import resolve_env_ids
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.tasks.kick.mdp.geometry import (
  behind_ball_waypoint_xy,
  ensure_approach_waypoint_latch,
  get_approach_waypoint_latch,
  nearest_foot_kick_side,
  update_plant_arrival_latch,
)
from mjlab.utils.lab_api.math import (
  quat_apply,
  quat_apply_inverse,
  quat_from_euler_xyz,
  sample_uniform,
)

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_DEFAULT_BALL_CFG = SceneEntityCfg("ball")
_DEFAULT_ROBOT_CFG = SceneEntityCfg("robot")


def _ball_resting_z(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor,
  height: float,
) -> torch.Tensor:
  """World-frame ball centre height when resting on the env terrain plane."""
  return env.scene.env_origins[env_ids, 2] + height


def reset_ball_uniform(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  pose_range: dict[str, tuple[float, float]],
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  initial_speed: float = 0.0,
  initial_speed_range: tuple[float, float] | None = None,
) -> None:
  """Reset the ball to a uniform random position in world (env-local) space.

  Args:
    env: The environment.
    env_ids: Environments to reset; ``None`` means all.
    pose_range: Dict with optional keys ``"x"``, ``"y"``, ``"z"`` giving
      ``(min, max)`` offsets relative to the env origin.
    ball_cfg: Scene entity config for the ball.
    initial_speed: Fixed planar speed (m/s) if ``initial_speed_range`` is None.
    initial_speed_range: Optional ``(min, max)`` planar speed; random heading.
  """
  env_ids = resolve_env_ids(env, env_ids)
  ball: Entity = env.scene[ball_cfg.name]

  default_state = ball.data.default_root_state[env_ids].clone()

  _SE3_KEYS = ("x", "y", "z")
  ranges = torch.tensor(
    [pose_range.get(k, (0.0, 0.0)) for k in _SE3_KEYS],
    device=env.device,
  )
  offsets = sample_uniform(ranges[:, 0], ranges[:, 1], (len(env_ids), 3), env.device)

  default_state[:, 0:3] += offsets + env.scene.env_origins[env_ids]
  # Zero out velocity, then optionally assign planar speed with random heading.
  default_state[:, 7:] = 0.0
  n = len(env_ids)
  if initial_speed_range is not None:
    speed = sample_uniform(
      torch.full((n,), initial_speed_range[0], device=env.device),
      torch.full((n,), initial_speed_range[1], device=env.device),
      (n,),
      env.device,
    )
  elif initial_speed > 0.0:
    speed = torch.full((n,), initial_speed, device=env.device)
  else:
    speed = None
  if speed is not None:
    heading = sample_uniform(
      torch.full((n,), -math.pi, device=env.device),
      torch.full((n,), math.pi, device=env.device),
      (n,),
      env.device,
    )
    default_state[:, 7] = speed * torch.cos(heading)
    default_state[:, 8] = speed * torch.sin(heading)
  ball.write_root_state_to_sim(default_state, env_ids=env_ids)


def latch_spawn_waypoint_side(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor,
  robot_xy: torch.Tensor,
  ball_xy: torch.Tensor,
  waypoint_lateral_range: tuple[float, float] | None,
  fixed_kick_side: float | None,
  goal_command_name: str,
) -> None:
  """Latch kick foot from the spawn-closer leg; sample lateral range."""
  latch = ensure_approach_waypoint_latch(env)
  latch.side[env_ids] = 0.0
  latch.lateral[env_ids] = 0.0
  latch.at_plant[env_ids] = False
  latch.ready_time_s[env_ids] = 0.0
  command = env.command_manager.get_command(goal_command_name)
  assert command is not None, f"Command '{goal_command_name}' not found."
  n = len(env_ids)
  device = env.device
  goal_xy = command[env_ids, :2] + env.scene.env_origins[env_ids, :2]
  goal_dir = goal_xy - ball_xy
  goal_dir = goal_dir / torch.linalg.norm(goal_dir, dim=-1, keepdim=True).clamp(
    min=1.0e-6
  )
  if waypoint_lateral_range is None:
    if fixed_kick_side is not None:
      latch.side[env_ids] = float(fixed_kick_side)
    else:
      latch.side[env_ids] = nearest_foot_kick_side(robot_xy, ball_xy, goal_dir)
    return
  if fixed_kick_side is None:
    side = nearest_foot_kick_side(robot_xy, ball_xy, goal_dir)
  else:
    side = torch.full((n,), float(fixed_kick_side), device=device)
  lo, hi = float(waypoint_lateral_range[0]), float(waypoint_lateral_range[1])
  lat = sample_uniform(
    torch.full((n,), lo, device=device),
    torch.full((n,), hi, device=device),
    (n,),
    device,
  )
  latch.side[env_ids] = side
  latch.lateral[env_ids] = lat


def reset_robot_around_ball_facing(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  radius_range: tuple[float, float] = (0.5, 4.0),
  angle_range: tuple[float, float] = (-math.pi, math.pi),
  spawn_on_approach_side: bool = False,
  approach_spread: float = math.pi / 2.0,
  goal_command_name: str = "goal",
  waypoint_lateral_range: tuple[float, float] | None = None,
  fixed_kick_side: float | None = None,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> None:
  """Reset the robot around the ball while facing it.

  The ball is expected to be reset at the environment centre.  Sampling the
  robot in polar coordinates gives uniform angular coverage, while its yaw is
  set toward the ball so the approach policy starts with the ball in view.

  When ``spawn_on_approach_side`` is True, the robot is sampled on the
  hemisphere opposite the goal so it never starts on the target side of the
  ball.  Use this with ``mode="post_reset"`` so the goal command is already
  sampled for the episode.

  ``waypoint_lateral_range`` latches a spawn-side offset for the yellow
  approach waypoint (swing foot on the kick line). ``None`` keeps it on-axis.
  Kick foot is the spawn-closer leg unless ``fixed_kick_side`` is set.
  """
  env_ids = resolve_env_ids(env, env_ids)
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]

  n = len(env_ids)
  device = env.device
  radius = sample_uniform(
    torch.full((n,), radius_range[0], device=device),
    torch.full((n,), radius_range[1], device=device),
    (n,),
    device,
  )
  if spawn_on_approach_side:
    ball_state = ball.data.default_root_state[env_ids]
    ball_pos = ball_state[:, :3] + env.scene.env_origins[env_ids]
    command = env.command_manager.get_command(goal_command_name)
    assert command is not None, f"Command '{goal_command_name}' not found."
    goal_pos = command[env_ids, :2] + env.scene.env_origins[env_ids, :2]
    goal_angle = torch.atan2(
      goal_pos[:, 1] - ball_pos[:, 1],
      goal_pos[:, 0] - ball_pos[:, 0],
    )
    approach_center = goal_angle + math.pi
    half_spread = approach_spread * 0.5
    angle = approach_center + sample_uniform(
      torch.full((n,), -half_spread, device=device),
      torch.full((n,), half_spread, device=device),
      (n,),
      device,
    )
  else:
    angle = sample_uniform(
      torch.full((n,), angle_range[0], device=device),
      torch.full((n,), angle_range[1], device=device),
      (n,),
      device,
    )

  ball_state = ball.data.default_root_state[env_ids]
  ball_pos = ball_state[:, :3] + env.scene.env_origins[env_ids]
  robot_state = robot.data.default_root_state[env_ids].clone()
  robot_pos = robot_state[:, :3].clone()
  robot_pos[:, 0] = ball_pos[:, 0] + radius * torch.cos(angle)
  robot_pos[:, 1] = ball_pos[:, 1] + radius * torch.sin(angle)

  yaw = torch.atan2(ball_pos[:, 1] - robot_pos[:, 1], ball_pos[:, 0] - robot_pos[:, 0])
  zeros = torch.zeros(n, device=device)
  robot_quat = quat_from_euler_xyz(zeros, zeros, yaw)

  robot.write_root_link_pose_to_sim(
    torch.cat([robot_pos, robot_quat], dim=-1),
    env_ids=env_ids,
  )
  robot.write_root_link_velocity_to_sim(
    robot_state[:, 7:13],
    env_ids=env_ids,
  )
  latch_spawn_waypoint_side(
    env,
    env_ids,
    robot_pos[:, :2],
    ball_pos[:, :2],
    waypoint_lateral_range,
    fixed_kick_side,
    goal_command_name,
  )


def update_approach_twist_command(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  command_name: str = "twist",
  goal_command_name: str = "goal",
  target_distance: float = 0.35,
  cruise_speed: float = 0.7,
  min_speed: float = 0.25,
  slow_distance: float = 1.0,
  ready_ball_distance: float = 0.50,
  ready_waypoint_distance: float = 0.20,
  yaw_gain: float = 2.0,
  max_ang_vel: float = 1.2,
  gait_frequency: float = 2.0,
  body_pitch_target: float = 0.04,
  body_roll_target: float = 0.0,
  feet_offset_x_target: float = 0.0,
  feet_offset_y_target: float = 0.0,
  hold_gait_when_ready: bool = False,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> None:
  """Drive the HTWK twist command toward the behind-ball waypoint each step.

  Replaces random walk velocity samples with a goal-directed command so the
  walking tracker and gait rewards reinforce approach instead of conflicting
  with kick shaping.  Commands go to zero once the robot is close enough to
  hold the kick-ready pose.

  ParameterWalk body pitch/roll and foot offsets are pinned to mild upright
  targets so the orientation reward does not command a deep crouch under push
  disturbances.
  """
  from mjlab.tasks.velocity.mdp.velocity_command import UniformVelocityCommand

  twist_term = env.command_manager.get_term(command_name)
  assert isinstance(twist_term, UniformVelocityCommand)

  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]

  robot_pos = robot.data.root_link_pos_w
  ball_pos = ball.data.root_link_pos_w[:, :2]
  waypoint = behind_ball_waypoint_xy(env, ball_pos, target_distance, goal_command_name)

  to_waypoint = waypoint - robot_pos[:, :2]
  waypoint_distance = torch.linalg.norm(to_waypoint, dim=-1, keepdim=True).clamp(
    min=1.0e-6
  )
  dir_w = to_waypoint / waypoint_distance

  dir_b = quat_apply_inverse(
    robot.data.root_link_quat_w,
    torch.cat(
      [dir_w, torch.zeros_like(dir_w[:, :1])],
      dim=-1,
    ),
  )[:, :2]

  speed_scale = torch.clamp(waypoint_distance.squeeze(-1) / slow_distance, 0.0, 1.0)
  speed = min_speed + (cruise_speed - min_speed) * speed_scale
  lin_cmd = dir_b * speed.unsqueeze(-1)

  ball_distance = torch.linalg.norm(ball_pos - robot_pos[:, :2], dim=-1)
  ready = (ball_distance <= ready_ball_distance) & (
    waypoint_distance.squeeze(-1) <= ready_waypoint_distance
  )
  creep = ready & (ball_distance > target_distance + 0.03)

  rel_b = quat_apply_inverse(
    robot.data.root_link_quat_w,
    ball.data.root_link_pos_w - robot_pos,
  )
  bearing = torch.atan2(rel_b[:, 1], rel_b[:, 0])
  ang_cmd = torch.clamp(yaw_gain * bearing, min=-max_ang_vel, max=max_ang_vel)

  twist_term.vel_command_b[:, 0] = lin_cmd[:, 0]
  twist_term.vel_command_b[:, 1] = lin_cmd[:, 1]
  twist_term.vel_command_b[:, 2] = ang_cmd
  twist_term.vel_command_b[ready, :3] = 0.0
  if hold_gait_when_ready:
    creep_speed = 0.22
    twist_term.vel_command_b[creep, 0] = torch.clamp(
      rel_b[creep, 0] * 0.8, min=0.05, max=creep_speed
    )
    twist_term.vel_command_b[creep, 1] = torch.clamp(
      rel_b[creep, 1] * 0.5, min=-0.08, max=0.08
    )

  if twist_term.vel_command_b.shape[1] > 3:
    if hold_gait_when_ready:
      twist_term.vel_command_b[:, 3] = gait_frequency
      twist_term.is_standing_env[:] = False
    else:
      moving = ~ready
      twist_term.vel_command_b[moving, 3] = gait_frequency
      twist_term.vel_command_b[ready, 3] = 0.0
      twist_term.is_standing_env[:] = ready
  if twist_term.vel_command_b.shape[1] > 6:
    twist_term.vel_command_b[:, 6] = body_pitch_target
    twist_term.vel_command_b[:, 7] = body_roll_target
    twist_term.vel_command_b[:, 8] = feet_offset_x_target
    twist_term.vel_command_b[:, 9] = feet_offset_y_target


def reset_ball_relative_to_robot(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  forward_range: tuple[float, float] = (0.3, 0.8),
  lateral_range: tuple[float, float] = (-0.1, 0.1),
  height: float = 0.11,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> None:
  """Reset the ball to a random position in front of the robot.

  Useful for the kick task: the episode always starts with the ball already
  in the robot's kick zone so no approach phase is needed.

  Args:
    env: The environment.
    env_ids: Environments to reset; ``None`` means all.
    forward_range: Offset range (min, max) in robot-forward direction (metres).
    lateral_range: Offset range (min, max) in robot-lateral direction (metres).
    height: Fixed ball height above terrain (metres).
    ball_cfg: Ball entity config.
    robot_cfg: Robot entity config (used to get current root pose).
  """
  env_ids = resolve_env_ids(env, env_ids)
  ball: Entity = env.scene[ball_cfg.name]
  robot: Entity = env.scene[robot_cfg.name]

  n = len(env_ids)
  robot_pos_w = robot.data.root_link_pos_w[env_ids]  # [N, 3]
  robot_quat_w = robot.data.root_link_quat_w[env_ids]  # [N, 4]

  # Sample offsets in robot body frame.
  fwd = sample_uniform(
    torch.full((n,), forward_range[0], device=env.device),
    torch.full((n,), forward_range[1], device=env.device),
    (n,),
    env.device,
  )
  lat = sample_uniform(
    torch.full((n,), lateral_range[0], device=env.device),
    torch.full((n,), lateral_range[1], device=env.device),
    (n,),
    env.device,
  )
  offset_b = torch.stack([fwd, lat, torch.zeros(n, device=env.device)], dim=-1)

  # Rotate to world frame and translate.
  offset_w = quat_apply(robot_quat_w, offset_b)
  ball_pos_w = robot_pos_w + offset_w
  ball_pos_w[:, 2] = _ball_resting_z(env, env_ids, height)

  # Build full 13-D root state: [pos(3), quat(4), lin_vel(3), ang_vel(3)].
  ball_state = ball.data.default_root_state[env_ids].clone()
  ball_state[:, 0:3] = ball_pos_w
  ball_state[:, 3:7] = torch.tensor([1.0, 0.0, 0.0, 0.0], device=env.device)
  ball_state[:, 7:] = 0.0
  ball.write_root_state_to_sim(ball_state, env_ids=env_ids)


def reset_ball_bilateral(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  forward_range: tuple[float, float] = (0.25, 0.45),
  lateral_inner: float = 0.04,
  lateral_outer: float = 0.12,
  height: float = 0.11,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> None:
  """Reset the ball in front of the robot on the left or right side.

  Samples lateral offset outside the centre corridor so the policy learns
  implicit foot selection from ``ball_rel_pos.y`` without a foot command.
  """
  env_ids = resolve_env_ids(env, env_ids)
  ball: Entity = env.scene[ball_cfg.name]
  robot: Entity = env.scene[robot_cfg.name]

  n = len(env_ids)
  device = env.device
  robot_pos_w = robot.data.root_link_pos_w[env_ids]
  robot_quat_w = robot.data.root_link_quat_w[env_ids]

  fwd = sample_uniform(
    torch.full((n,), forward_range[0], device=device),
    torch.full((n,), forward_range[1], device=device),
    (n,),
    device,
  )
  use_right = torch.randint(0, 2, (n,), device=device, dtype=torch.bool)
  lat_min = torch.where(use_right, lateral_inner, -lateral_outer)
  lat_max = torch.where(use_right, lateral_outer, -lateral_inner)
  lat = sample_uniform(lat_min, lat_max, (n,), device=device)

  offset_b = torch.stack([fwd, lat, torch.zeros(n, device=device)], dim=-1)
  offset_w = quat_apply(robot_quat_w, offset_b)
  ball_pos_w = robot_pos_w + offset_w
  ball_pos_w[:, 2] = _ball_resting_z(env, env_ids, height)

  ball_state = ball.data.default_root_state[env_ids].clone()
  ball_state[:, 0:3] = ball_pos_w
  ball_state[:, 3:7] = torch.tensor([1.0, 0.0, 0.0, 0.0], device=device)
  ball_state[:, 7:] = 0.0
  ball.write_root_state_to_sim(ball_state, env_ids=env_ids)


def ensure_robot_ball_twist_command(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None = None,
  command_name: str = "twist",
  cruise_speed: float = 0.7,
  min_speed: float = 0.25,
  slow_distance: float = 1.0,
  plant_distance: float = 0.20,
  turn_speed: float = 1.0,
  heading_deadzone: float = 0.05,
  use_sampled_magnitudes: bool = True,
  gait_frequency: float = 2.0,
  body_pitch_target: float = 0.04,
  body_roll_target: float = 0.0,
  feet_offset_x_target: float = 0.0,
  feet_offset_y_target: float = 0.0,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  # Orbit / circle: drive to behind-ball approach waypoint (not pure radial).
  orbit_to_approach: bool = False,
  goal_command_name: str = "goal",
  approach_standoff: float = 0.40,
  ready_waypoint_distance: float = 0.20,
  ready_facing_angle: float = math.radians(20.0),
  ready_hold_time_s: float = 0.10,
  # Near-kick plant: drive root to support-side plant pose + pin feet offsets.
  orbit_to_plant_box: bool = False,
  plant_root_behind: float = 0.22,
  plant_root_lateral: float = 0.10,
  plant_feet_offset_x: float = -0.02,
  plant_feet_offset_y: float = 0.12,
  prefer_right_foot: bool = True,
  # Keep walking through plant (in-walk catch) instead of freezing at waypoint.
  creep_through_plant: bool = False,
  creep_speed: float = 0.25,
  # Face path for speed; clamp yaw so ball stays in FOV cone (fixed forward cam).
  face_path_fov_clip: bool = False,
  fov_half_angle: float = 0.69,  # ~75% of 105° HFOV → ±39°
  yaw_gain: float = 2.0,
  # Latch only when support foot is in the plant box (blocks long reaches).
  require_support_plant_for_latch: bool = False,
  support_plant_sagittal_target: float = 0.14,
  support_plant_sagittal_tol: float = 0.10,
  support_plant_lateral_target: float = 0.175,
  support_plant_lateral_tol: float = 0.10,
  # Also wait for the swing foot to catch up (blocks early plant + drag).
  require_swing_foot_for_latch: bool = False,
  swing_foot_max_ball_distance: float = 0.38,
  force: bool = False,
  **_unused,
) -> None:
  """Set twist targets once per env step (unless ``force``).

  Default (paper radial): ``v = v_x · r̂_rb``, ``ω = ω_z · sign(θ_ball)``.

  With ``orbit_to_plant_box=True``: aims at the support-side plant root
  (approach side) and pins ``feet_offset_x/y``. With
  ``creep_through_plant=True``, never stands still — once near the plant
  pose the linear cmd continues toward the ball so kick setup can catch
  mid-stride. With ``face_path_fov_clip=True``, yaw faces the path but is
  clamped so the ball bearing stays within ``±fov_half_angle``.
  """
  del env_ids, _unused
  step = int(env.common_step_counter)
  if not force and getattr(env, "_kick_robot_ball_twist_step", -1) == step:
    return

  from mjlab.tasks.kick.mdp.geometry import ball_to_goal_direction_xy
  from mjlab.tasks.kick.mdp.pref_pose import setup_offset_xy
  from mjlab.tasks.velocity.mdp.velocity_command import UniformVelocityCommand
  from mjlab.utils.lab_api.math import wrap_to_pi

  twist_term = env.command_manager.get_term(command_name)
  assert isinstance(twist_term, UniformVelocityCommand)

  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  robot_pos = robot.data.root_link_pos_w
  ball_xy = ball.data.root_link_pos_w[:, :2]
  robot_xy = robot_pos[:, :2]

  to_ball = ball_xy - robot_xy
  ball_dist = torch.linalg.norm(to_ball, dim=-1)

  if use_sampled_magnitudes:
    v_x = twist_term.vel_command_b[:, 0].abs()
    omega_z = twist_term.vel_command_b[:, 2].abs()
    v_x = torch.where(
      v_x < float(min_speed),
      torch.full_like(v_x, float(cruise_speed)),
      v_x,
    )
    omega_z = torch.where(
      omega_z < 0.05,
      torch.full_like(omega_z, float(turn_speed)),
      omega_z,
    )
  else:
    v_x = torch.full(
      (env.num_envs,), float(cruise_speed), device=env.device, dtype=robot_xy.dtype
    )
    omega_z = torch.full(
      (env.num_envs,), float(turn_speed), device=env.device, dtype=robot_xy.dtype
    )

  wp_dist = torch.full_like(ball_dist, torch.inf)
  drive_hat = to_ball / ball_dist.unsqueeze(-1).clamp(min=1.0e-6)
  goal_dir = drive_hat
  near_plant = torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)

  support_ready = None
  if require_support_plant_for_latch:
    from mjlab.tasks.kick.mdp.rewards import support_plant_ready_mask

    support_ready = support_plant_ready_mask(
      env,
      command_name=goal_command_name,
      sagittal_target=float(support_plant_sagittal_target),
      sagittal_tol=float(support_plant_sagittal_tol),
      lateral_target=float(support_plant_lateral_target),
      lateral_tol=float(support_plant_lateral_tol),
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    )

  swing_ready = None
  if require_swing_foot_for_latch:
    from mjlab.tasks.kick.mdp.rewards import swing_foot_ready_mask

    swing_ready = swing_foot_ready_mask(
      env,
      max_ball_distance=float(swing_foot_max_ball_distance),
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    )

  if orbit_to_plant_box:
    goal_dir = ball_to_goal_direction_xy(env, ball_xy, goal_command_name)
    offset = setup_offset_xy(
      goal_dir,
      behind=float(plant_root_behind),
      lateral=float(plant_root_lateral),
      prefer_right_foot=prefer_right_foot,
    )
    plant_wp = ball_xy + offset
    to_plant = plant_wp - robot_xy
    wp_dist = torch.linalg.norm(to_plant, dim=-1)
    plant_hat = to_plant / wp_dist.unsqueeze(-1).clamp(min=1.0e-6)
    ball_hat = to_ball / ball_dist.unsqueeze(-1).clamp(min=1.0e-6)
    fwd = quat_apply(
      robot.data.root_link_quat_w,
      torch.tensor([1.0, 0.0, 0.0], device=env.device, dtype=robot_xy.dtype).expand(
        env.num_envs, 3
      ),
    )[:, :2]
    fwd = fwd / fwd.norm(dim=-1, keepdim=True).clamp(min=1.0e-6)
    facing = torch.sum(fwd * goal_dir, dim=-1).clamp(-1.0, 1.0)
    near_plant = update_plant_arrival_latch(
      env,
      wp_dist,
      facing,
      float(ready_waypoint_distance),
      facing_min=math.cos(float(ready_facing_angle)),
      hold_time_s=float(ready_hold_time_s),
      support_ready=support_ready,
      swing_ready=swing_ready,
    )
    # Approach-side catch: go to plant pose, then keep walking toward ball.
    if creep_through_plant:
      drive_hat = torch.where(near_plant.unsqueeze(-1), ball_hat, plant_hat)
      speed_scale = torch.clamp(wp_dist / max(float(slow_distance), 1.0e-6), 0.0, 1.0)
      approach_speed = float(min_speed) + (v_x - float(min_speed)) * speed_scale
      speed = torch.where(
        near_plant,
        torch.full_like(approach_speed, float(creep_speed)),
        approach_speed,
      )
      plant = torch.zeros_like(near_plant)  # never freeze / stand
    else:
      drive_hat = plant_hat
      speed_scale = torch.clamp(wp_dist / max(float(slow_distance), 1.0e-6), 0.0, 1.0)
      speed = float(min_speed) + (v_x - float(min_speed)) * speed_scale
      plant = near_plant
    v_w = drive_hat * speed.unsqueeze(-1)
  elif orbit_to_approach:
    waypoint = behind_ball_waypoint_xy(
      env, ball_xy, float(approach_standoff), goal_command_name
    )
    to_wp = waypoint - robot_xy
    wp_dist = torch.linalg.norm(to_wp, dim=-1)
    goal_dir = ball_to_goal_direction_xy(env, ball_xy, goal_command_name)
    fwd = quat_apply(
      robot.data.root_link_quat_w,
      torch.tensor([1.0, 0.0, 0.0], device=env.device, dtype=robot_xy.dtype).expand(
        env.num_envs, 3
      ),
    )[:, :2]
    fwd = fwd / fwd.norm(dim=-1, keepdim=True).clamp(min=1.0e-6)
    yaw_err = torch.atan2(
      fwd[:, 0] * goal_dir[:, 1] - fwd[:, 1] * goal_dir[:, 0],
      (fwd * goal_dir).sum(dim=-1).clamp(-1.0, 1.0),
    )
    facing = torch.cos(yaw_err)
    at_plant = update_plant_arrival_latch(
      env,
      wp_dist,
      facing,
      float(ready_waypoint_distance),
      facing_min=math.cos(float(ready_facing_angle)),
      hold_time_s=float(ready_hold_time_s),
      support_ready=support_ready,
      swing_ready=swing_ready,
    )
    waypoint = behind_ball_waypoint_xy(
      env, ball_xy, float(approach_standoff), goal_command_name
    )
    to_wp = waypoint - robot_xy
    wp_dist = torch.linalg.norm(to_wp, dim=-1)
    plant_hat = to_wp / wp_dist.unsqueeze(-1).clamp(min=1.0e-6)
    near_plant = at_plant
    if creep_through_plant:
      ball_hat = to_ball / ball_dist.unsqueeze(-1).clamp(min=1.0e-6)
      drive_hat = torch.where(at_plant.unsqueeze(-1), ball_hat, plant_hat)
      speed_scale = torch.clamp(wp_dist / max(float(slow_distance), 1.0e-6), 0.0, 1.0)
      approach_speed = float(min_speed) + (v_x - float(min_speed)) * speed_scale
      speed = torch.where(
        at_plant,
        torch.full_like(approach_speed, float(creep_speed)),
        approach_speed,
      )
      plant = torch.zeros_like(at_plant)
    else:
      drive_hat = plant_hat
      speed_scale = torch.clamp(wp_dist / max(float(slow_distance), 1.0e-6), 0.0, 1.0)
      speed = float(min_speed) + (v_x - float(min_speed)) * speed_scale
      plant = wp_dist <= float(ready_waypoint_distance)
    v_w = drive_hat * speed.unsqueeze(-1)
  else:
    r_hat = to_ball / ball_dist.unsqueeze(-1).clamp(min=1.0e-6)
    speed_scale = torch.clamp(ball_dist / max(float(slow_distance), 1.0e-6), 0.0, 1.0)
    speed = float(min_speed) + (v_x - float(min_speed)) * speed_scale
    v_w = r_hat * speed.unsqueeze(-1)
    plant = ball_dist <= float(plant_distance)

  v_b = quat_apply_inverse(
    robot.data.root_link_quat_w,
    torch.cat([v_w, torch.zeros_like(v_w[:, :1])], dim=-1),
  )[:, :2]

  rel_b = quat_apply_inverse(
    robot.data.root_link_quat_w,
    ball.data.root_link_pos_w - robot_pos,
  )
  theta_ball = torch.atan2(rel_b[:, 1], rel_b[:, 0])

  use_path_yaw = (
    (orbit_to_approach or orbit_to_plant_box)
    and face_path_fov_clip
    and drive_hat is not None
  )
  if use_path_yaw:
    # Path heading error (face along robot→waypoint for forward speed).
    body_fwd = quat_apply(
      robot.data.root_link_quat_w,
      torch.tensor([1.0, 0.0, 0.0], device=env.device, dtype=robot_xy.dtype).expand(
        env.num_envs, 3
      ),
    )
    body_yaw = torch.atan2(body_fwd[:, 1], body_fwd[:, 0])
    yaw_hat = drive_hat
    if orbit_to_plant_box:
      yaw_hat = torch.where(
        (wp_dist <= float(slow_distance)).unsqueeze(-1), goal_dir, drive_hat
      )
    elif orbit_to_approach:
      # Close in: keep translating toward the waypoint, but lock heading to
      # ball→goal so a nearby offset marker cannot spin the robot into an orbit.
      face_goal = near_plant | (wp_dist <= float(slow_distance))
      yaw_hat = torch.where(face_goal.unsqueeze(-1), goal_dir, drive_hat)
    path_yaw = torch.atan2(yaw_hat[:, 1], yaw_hat[:, 0])
    phi_path = wrap_to_pi(path_yaw - body_yaw)
    # Turning by δ (CCW+) moves ball bearing: θ' = θ_ball − δ.
    # Keep |θ'| ≤ fov_half_angle ⇒ δ ∈ [θ_ball − θ_safe, θ_ball + θ_safe].
    theta_safe = float(fov_half_angle)
    delta_min = theta_ball - theta_safe
    delta_max = theta_ball + theta_safe
    delta = torch.minimum(torch.maximum(phi_path, delta_min), delta_max)
    ang_cmd = torch.clamp(float(yaw_gain) * delta, min=-omega_z, max=omega_z)
    ang_cmd = torch.where(
      delta.abs() < float(heading_deadzone),
      torch.zeros_like(ang_cmd),
      ang_cmd,
    )
    heading_err = delta.abs()
  else:
    # Legacy: always face the ball.
    ang_cmd = omega_z * torch.sign(theta_ball)
    ang_cmd = torch.where(
      theta_ball.abs() < float(heading_deadzone),
      torch.zeros_like(ang_cmd),
      ang_cmd,
    )
    heading_err = theta_ball.abs()

  lin_cmd = torch.where(plant.unsqueeze(-1), torch.zeros_like(v_b), v_b)

  twist_term.vel_command_b[:, 0] = lin_cmd[:, 0]
  twist_term.vel_command_b[:, 1] = lin_cmd[:, 1]
  twist_term.vel_command_b[:, 2] = ang_cmd

  if twist_term.vel_command_b.shape[1] > 3:
    moving = ~plant
    twist_term.vel_command_b[moving, 3] = gait_frequency
    twist_term.vel_command_b[plant, 3] = 0.0
    twist_term.is_standing_env[:] = plant
  if twist_term.vel_command_b.shape[1] > 6:
    twist_term.vel_command_b[:, 6] = body_pitch_target
    twist_term.vel_command_b[:, 7] = body_roll_target
    twist_term.vel_command_b[:, 8] = float(feet_offset_x_target)
    twist_term.vel_command_b[:, 9] = float(feet_offset_y_target)
    if orbit_to_plant_box:
      pin = wp_dist <= max(float(ready_waypoint_distance), 0.35)
      twist_term.vel_command_b[pin, 8] = float(plant_feet_offset_x)
      twist_term.vel_command_b[pin, 9] = float(plant_feet_offset_y)

  env._kick_robot_ball_twist_step = step
  env.extras.setdefault("log", {})
  env.extras["log"]["Metrics/twist_ball_dist"] = ball_dist.mean()
  env.extras["log"]["Metrics/twist_heading_err"] = heading_err.mean()
  env.extras["log"]["Metrics/twist_ball_bearing"] = theta_ball.abs().mean()
  env.extras["log"]["Metrics/twist_orbit"] = float(
    orbit_to_approach or orbit_to_plant_box
  )
  env.extras["log"]["Metrics/twist_plant_box"] = float(orbit_to_plant_box)
  env.extras["log"]["Metrics/twist_creep_through"] = float(creep_through_plant)
  env.extras["log"]["Metrics/twist_near_plant"] = near_plant.float().mean()
  env.extras["log"]["Metrics/twist_fov_clip"] = float(use_path_yaw)
  if support_ready is not None:
    env.extras["log"]["Metrics/support_plant_ready"] = support_ready.float().mean()
  if swing_ready is not None:
    env.extras["log"]["Metrics/swing_foot_ready"] = swing_ready.float().mean()
  if orbit_to_approach or orbit_to_plant_box:
    env.extras["log"]["Metrics/twist_waypoint_dist"] = wp_dist.mean()
  latch = get_approach_waypoint_latch(env)
  if latch is not None:
    env.extras["log"]["Metrics/waypoint_side"] = latch.side.mean()
    env.extras["log"]["Metrics/waypoint_lateral"] = latch.lateral.mean()
    env.extras["log"]["Metrics/waypoint_at_plant"] = latch.at_plant.float().mean()


def update_pref_pose_twist_command(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  command_name: str = "twist",
  goal_command_name: str = "goal",
  cruise_speed: float = 0.7,
  min_speed: float = 0.25,
  slow_distance: float = 1.0,
  plant_distance: float = 0.20,
  turn_speed: float = 1.0,
  heading_deadzone: float = 0.05,
  use_sampled_magnitudes: bool = True,
  gait_frequency: float = 2.0,
  body_pitch_target: float = 0.04,
  body_roll_target: float = 0.0,
  feet_offset_x_target: float = 0.0,
  feet_offset_y_target: float = 0.0,
  orbit_to_approach: bool = False,
  approach_standoff: float = 0.40,
  ready_waypoint_distance: float = 0.20,
  orbit_to_plant_box: bool = False,
  plant_root_behind: float = 0.22,
  plant_root_lateral: float = 0.10,
  plant_feet_offset_x: float = -0.02,
  plant_feet_offset_y: float = 0.12,
  prefer_right_foot: bool = True,
  creep_through_plant: bool = False,
  creep_speed: float = 0.25,
  face_path_fov_clip: bool = False,
  fov_half_angle: float = 0.69,
  yaw_gain: float = 2.0,
  require_support_plant_for_latch: bool = False,
  support_plant_sagittal_target: float = 0.14,
  support_plant_sagittal_tol: float = 0.10,
  support_plant_lateral_target: float = 0.175,
  support_plant_lateral_tol: float = 0.10,
  require_swing_foot_for_latch: bool = False,
  swing_foot_max_ball_distance: float = 0.38,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  **_legacy,
) -> None:
  """Step-event teacher: refresh robot→ball / orbit twist after command resample.

  Also invoked from kick tracking rewards via
  :func:`ensure_robot_ball_twist_command` so the student tracks the same
  targets during reward computation (events run after rewards).
  """
  del _legacy
  ensure_robot_ball_twist_command(
    env,
    env_ids,
    command_name=command_name,
    cruise_speed=cruise_speed,
    min_speed=min_speed,
    slow_distance=slow_distance,
    plant_distance=plant_distance,
    turn_speed=turn_speed,
    heading_deadzone=heading_deadzone,
    use_sampled_magnitudes=use_sampled_magnitudes,
    gait_frequency=gait_frequency,
    body_pitch_target=body_pitch_target,
    body_roll_target=body_roll_target,
    feet_offset_x_target=feet_offset_x_target,
    feet_offset_y_target=feet_offset_y_target,
    orbit_to_approach=orbit_to_approach,
    goal_command_name=goal_command_name,
    approach_standoff=approach_standoff,
    ready_waypoint_distance=ready_waypoint_distance,
    orbit_to_plant_box=orbit_to_plant_box,
    plant_root_behind=plant_root_behind,
    plant_root_lateral=plant_root_lateral,
    plant_feet_offset_x=plant_feet_offset_x,
    plant_feet_offset_y=plant_feet_offset_y,
    prefer_right_foot=prefer_right_foot,
    creep_through_plant=creep_through_plant,
    creep_speed=creep_speed,
    face_path_fov_clip=face_path_fov_clip,
    fov_half_angle=fov_half_angle,
    yaw_gain=yaw_gain,
    require_support_plant_for_latch=require_support_plant_for_latch,
    support_plant_sagittal_target=support_plant_sagittal_target,
    support_plant_sagittal_tol=support_plant_sagittal_tol,
    support_plant_lateral_target=support_plant_lateral_target,
    support_plant_lateral_tol=support_plant_lateral_tol,
    require_swing_foot_for_latch=require_swing_foot_for_latch,
    swing_foot_max_ball_distance=swing_foot_max_ball_distance,
    robot_cfg=robot_cfg,
    ball_cfg=ball_cfg,
    force=True,  # after resample, always rewrite
  )


def update_kick_twist_command(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  command_name: str = "twist",
  body_pitch_target: float = 0.04,
  body_roll_target: float = 0.0,
  feet_offset_x_target: float = 0.0,
  feet_offset_y_target: float = 0.0,
) -> None:
  """Pin the HTWK twist command to standing for stationary kick training."""
  from mjlab.tasks.velocity.mdp.velocity_command import UniformVelocityCommand

  twist_term = env.command_manager.get_term(command_name)
  assert isinstance(twist_term, UniformVelocityCommand)
  twist_term.vel_command_b[:, 0:3] = 0.0
  if twist_term.vel_command_b.shape[1] > 3:
    twist_term.vel_command_b[:, 3] = 0.0
    twist_term.is_standing_env[:] = True
  if twist_term.vel_command_b.shape[1] > 6:
    twist_term.vel_command_b[:, 6] = body_pitch_target
    twist_term.vel_command_b[:, 7] = body_roll_target
    twist_term.vel_command_b[:, 8] = feet_offset_x_target
    twist_term.vel_command_b[:, 9] = feet_offset_y_target


def update_ball_phase_buffers(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  kick_window_speed_threshold: float = 0.5,
  min_kick_speed: float = 1.2,
  strong_kick_speed: float = 5.0,
  dribble_speed: float = 0.15,
  chase_speed_threshold: float = 0.12,
  goal_command_name: str = "goal",
  kick_phase_robot_ball_distance: float | None = 0.5,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> None:
  """Step hook that refreshes ball-phase buffers (also called lazily by rewards).

  Note: ``ManagerBasedRlEnv.step`` applies step events *after* terminations and
  rewards, so this hook is usually a no-op for the current step (first caller
  already filled the cache). Defaults on ``ensure_ball_phase_updated`` must be
  correct; params here document the intended recipe and matter if call order
  changes.
  """
  from mjlab.tasks.kick.mdp.ball_phase import ensure_ball_phase_updated

  ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    kick_window_speed_threshold=kick_window_speed_threshold,
    min_kick_speed=min_kick_speed,
    strong_kick_speed=strong_kick_speed,
    dribble_speed=dribble_speed,
    chase_speed_threshold=chase_speed_threshold,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=goal_command_name,
    robot_cfg_name=robot_cfg.name,
    kick_phase_robot_ball_distance=kick_phase_robot_ball_distance,
  )


def reset_strike_episode(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  behind_distance_range: tuple[float, float] = (0.30, 0.40),
  lateral_jitter: float = 0.05,
  forward_jitter: float = 0.05,
  ball_lateral_inner: float = 0.04,
  ball_lateral_outer: float = 0.12,
  ball_forward_range: tuple[float, float] = (0.25, 0.45),
  initial_ball_speed_range: tuple[float, float] = (0.1, 0.3),
  goal_command_name: str = "goal",
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> None:
  """Place the robot in a kick-ready pose behind a centred ball (strike stage).

  The ball receives a small random initial velocity so the policy learns to
  trap and kick rather than swing at a perfectly static target.
  """
  env_ids = resolve_env_ids(env, env_ids)
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  n = len(env_ids)
  device = env.device

  ball_state = ball.data.default_root_state[env_ids].clone()
  ball_pos = ball_state[:, :3] + env.scene.env_origins[env_ids]
  ball_pos[:, 2] = _ball_resting_z(env, env_ids, 0.11)

  command = env.command_manager.get_command(goal_command_name)
  assert command is not None, f"Command '{goal_command_name}' not found."
  goal_pos = command[env_ids, :2] + env.scene.env_origins[env_ids, :2]
  ball_to_goal = goal_pos - ball_pos[:, :2]
  ball_to_goal = ball_to_goal / torch.linalg.norm(
    ball_to_goal, dim=-1, keepdim=True
  ).clamp(min=1.0e-6)
  goal_dir = ball_to_goal

  behind_dist = sample_uniform(
    torch.full((n,), behind_distance_range[0], device=device),
    torch.full((n,), behind_distance_range[1], device=device),
    (n,),
    device,
  )
  perp = torch.stack([-goal_dir[:, 1], goal_dir[:, 0]], dim=-1)
  lat = sample_uniform(
    torch.full((n,), -lateral_jitter, device=device),
    torch.full((n,), lateral_jitter, device=device),
    (n,),
    device,
  )
  fwd = sample_uniform(
    torch.full((n,), -forward_jitter, device=device),
    torch.full((n,), forward_jitter, device=device),
    (n,),
    device,
  )
  robot_xy = (
    ball_pos[:, :2]
    - goal_dir * behind_dist.unsqueeze(-1)
    + perp * lat.unsqueeze(-1)
    + goal_dir * fwd.unsqueeze(-1)
  )

  robot_state = robot.data.default_root_state[env_ids].clone()
  robot_pos = robot_state[:, :3].clone()
  robot_pos[:, 0:2] = robot_xy
  robot_pos[:, 2] = robot_state[:, 2] + env.scene.env_origins[env_ids, 2]

  to_ball = ball_pos[:, :2] - robot_pos[:, :2]
  yaw = torch.atan2(to_ball[:, 1], to_ball[:, 0])
  zeros = torch.zeros(n, device=device)
  robot_quat = quat_from_euler_xyz(zeros, zeros, yaw)
  robot.write_root_link_pose_to_sim(
    torch.cat([robot_pos, robot_quat], dim=-1),
    env_ids=env_ids,
  )
  robot.write_root_link_velocity_to_sim(
    robot_state[:, 7:13],
    env_ids=env_ids,
  )

  robot_pos_w = robot.data.root_link_pos_w[env_ids]
  robot_quat_w = robot.data.root_link_quat_w[env_ids]
  fwd_ball = sample_uniform(
    torch.full((n,), ball_forward_range[0], device=device),
    torch.full((n,), ball_forward_range[1], device=device),
    (n,),
    device,
  )
  use_right = torch.randint(0, 2, (n,), device=device, dtype=torch.bool)
  lat_min = torch.where(use_right, ball_lateral_inner, -ball_lateral_outer)
  lat_max = torch.where(use_right, ball_lateral_outer, -ball_lateral_inner)
  lat_ball = sample_uniform(lat_min, lat_max, (n,), device=device)
  offset_b = torch.stack([fwd_ball, lat_ball, torch.zeros(n, device=device)], dim=-1)
  offset_w = quat_apply(robot_quat_w, offset_b)
  ball_pos_w = robot_pos_w + offset_w
  ball_pos_w[:, 2] = _ball_resting_z(env, env_ids, 0.11)

  speed = sample_uniform(
    torch.full((n,), initial_ball_speed_range[0], device=device),
    torch.full((n,), initial_ball_speed_range[1], device=device),
    (n,),
    device,
  )
  vel_dir = torch.randn(n, 2, device=device)
  vel_dir = vel_dir / torch.linalg.norm(vel_dir, dim=-1, keepdim=True).clamp(min=1.0e-6)
  ball_lin_vel = torch.zeros(n, 3, device=device)
  ball_lin_vel[:, 0:2] = vel_dir * speed.unsqueeze(-1)

  ball_state[:, 0:3] = ball_pos_w
  ball_state[:, 3:7] = torch.tensor([1.0, 0.0, 0.0, 0.0], device=device)
  ball_state[:, 7:10] = ball_lin_vel
  ball_state[:, 10:13] = 0.0
  ball.write_root_state_to_sim(ball_state, env_ids=env_ids)

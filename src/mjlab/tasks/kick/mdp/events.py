"""Kick-task event (reset) functions."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import torch

from mjlab.entity import Entity
from mjlab.envs.mdp.events import resolve_env_ids
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.utils.lab_api.math import (
  quat_apply_inverse,
  quat_from_euler_xyz,
  sample_uniform,
)

from mjlab.tasks.kick.mdp.geometry import behind_ball_waypoint_xy

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_DEFAULT_BALL_CFG = SceneEntityCfg("ball")
_DEFAULT_ROBOT_CFG = SceneEntityCfg("robot")


def reset_ball_uniform(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  pose_range: dict[str, tuple[float, float]],
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> None:
  """Reset the ball to a uniform random position in world (env-local) space.

  Args:
    env: The environment.
    env_ids: Environments to reset; ``None`` means all.
    pose_range: Dict with optional keys ``"x"``, ``"y"``, ``"z"`` giving
      ``(min, max)`` offsets relative to the env origin.
    ball_cfg: Scene entity config for the ball.
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
  # Zero out velocity.
  default_state[:, 7:] = 0.0
  ball.write_root_state_to_sim(default_state, env_ids=env_ids)


def reset_robot_around_ball_facing(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  radius_range: tuple[float, float] = (0.5, 4.0),
  angle_range: tuple[float, float] = (-math.pi, math.pi),
  spawn_on_approach_side: bool = False,
  approach_spread: float = math.pi / 2.0,
  goal_command_name: str = "goal",
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
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> None:
  """Drive the HTWK twist command toward the behind-ball waypoint each step.

  Replaces random walk velocity samples with a goal-directed command so the
  walking tracker and gait rewards reinforce approach instead of conflicting
  with kick shaping.  Commands go to zero once the robot is close enough to
  hold the kick-ready pose.
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

  if twist_term.vel_command_b.shape[1] > 3:
    moving = ~ready
    twist_term.vel_command_b[moving, 3] = gait_frequency
    twist_term.vel_command_b[ready, 3] = 0.0
    twist_term.is_standing_env[:] = ready


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
  ball_pos_w[:, 2] = robot_pos_w[:, 2] + height  # fixed height above robot origin

  # Build full 13-D root state: [pos(3), quat(4), lin_vel(3), ang_vel(3)].
  ball_state = ball.data.default_root_state[env_ids].clone()
  ball_state[:, 0:3] = ball_pos_w
  ball_state[:, 3:7] = torch.tensor([1.0, 0.0, 0.0, 0.0], device=env.device)
  ball_state[:, 7:] = 0.0
  ball.write_root_state_to_sim(ball_state, env_ids=env_ids)

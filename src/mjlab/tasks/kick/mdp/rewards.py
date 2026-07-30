"""Kick-task reward terms."""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from mjlab.entity import Entity
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.utils.lab_api.math import quat_apply_inverse

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_DEFAULT_ROBOT_CFG = SceneEntityCfg("robot")
_DEFAULT_BALL_CFG = SceneEntityCfg("ball")


def ball_approach_reward(
  env: ManagerBasedRlEnv,
  std: float = 1.0,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Dense Gaussian reward for reducing distance to the ball.

  Args:
    std: Gaussian width in metres. Smaller = sharper peak near the ball.

  Returns:
    ``[B]`` reward in ``(0, 1]``.
  """
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]

  robot_pos = robot.data.root_link_pos_w[:, :2]
  ball_pos = ball.data.root_link_pos_w[:, :2]
  dist_sq = torch.sum(torch.square(ball_pos - robot_pos), dim=-1)
  reward = torch.exp(-dist_sq / std**2)
  env.extras["log"]["Metrics/ball_distance"] = torch.sqrt(dist_sq).mean()
  return reward


def ball_in_kick_zone(
  env: ManagerBasedRlEnv,
  kick_distance: float = 0.35,
  lateral_half_width: float = 0.15,
  distance_std: float = 0.08,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Reward for the ball being in the robot's kick zone.

  The kick zone is defined as a region directly in front of the robot:
  forward offset ≈ ``kick_distance``, lateral offset within
  ``±lateral_half_width``.  Both conditions must be met.

  Returns:
    ``[B]`` reward in ``[0, 1]``.
  """
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]

  robot_pos_w = robot.data.root_link_pos_w
  robot_quat_w = robot.data.root_link_quat_w
  ball_pos_w = ball.data.root_link_pos_w

  rel_w = ball_pos_w - robot_pos_w
  rel_b = quat_apply_inverse(robot_quat_w, rel_w)  # [B, 3] body frame

  # Must be in front.
  in_front = (rel_b[:, 0] > 0.0).float()

  # Distance reward centred on kick_distance.
  fwd_dist = rel_b[:, 0].clamp(min=0.0)
  dist_to_ideal = torch.abs(fwd_dist - kick_distance)
  dist_reward = torch.exp(-(dist_to_ideal**2) / distance_std**2)

  # Lateral alignment: soft gate.
  lateral_ok = torch.exp(-torch.square(rel_b[:, 1]) / (lateral_half_width / 2.0) ** 2)

  reward = in_front * dist_reward * lateral_ok
  env.extras["log"]["Metrics/kick_zone_reward"] = reward.mean()
  return reward


def ball_velocity_toward_goal(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  min_speed: float = 0.5,
) -> torch.Tensor:
  """Reward ball velocity projected onto the goal direction.

  Activates only when the ball is moving faster than ``min_speed`` m/s
  to avoid rewarding accidental nudges.

  Returns:
    ``[B]`` reward (non-negative).
  """
  ball: Entity = env.scene[ball_cfg.name]
  ball_vel = ball.data.root_link_lin_vel_w[:, :2]  # [B, 2]

  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  goal_pos = command[:, :2]  # [B, 2]

  ball_pos = ball.data.root_link_pos_w[:, :2]  # [B, 2]
  to_goal = goal_pos - ball_pos
  to_goal_dist = torch.norm(to_goal, dim=-1, keepdim=True).clamp(min=1e-6)
  goal_dir = to_goal / to_goal_dist  # [B, 2] unit vec toward goal

  speed = torch.norm(ball_vel, dim=-1)  # [B]
  moving = (speed > min_speed).float()

  vel_toward_goal = torch.sum(ball_vel * goal_dir, dim=-1).clamp(min=0.0)
  reward = vel_toward_goal * moving
  env.extras["log"]["Metrics/ball_vel_toward_goal"] = reward.mean()
  return reward


def ball_goal_proximity(
  env: ManagerBasedRlEnv,
  std: float = 1.0,
  command_name: str = "goal",
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Dense Gaussian reward for the ball's proximity to the goal position.

  Args:
    std: Gaussian width in metres.

  Returns:
    ``[B]`` reward in ``(0, 1]``.
  """
  ball: Entity = env.scene[ball_cfg.name]
  ball_pos = ball.data.root_link_pos_w[:, :2]

  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  goal_pos = command[:, :2]

  dist_sq = torch.sum(torch.square(ball_pos - goal_pos), dim=-1)
  reward = torch.exp(-dist_sq / std**2)
  env.extras["log"]["Metrics/ball_goal_distance"] = torch.sqrt(dist_sq).mean()
  return reward

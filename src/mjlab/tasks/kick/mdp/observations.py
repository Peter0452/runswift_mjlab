"""Kick-task observation terms."""

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


def ball_relative_position(
  env: ManagerBasedRlEnv,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  clip_distance: float = 5.0,
) -> torch.Tensor:
  """Ball position expressed in the robot's base frame, clipped to ``clip_distance``.

  Returns:
    Tensor of shape ``[B, 3]`` (forward, lateral, vertical) in metres,
    clipped to ``[-clip_distance, clip_distance]``.
  """
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]

  robot_pos_w = robot.data.root_link_pos_w  # [B, 3]
  robot_quat_w = robot.data.root_link_quat_w  # [B, 4]
  ball_pos_w = ball.data.root_link_pos_w  # [B, 3]

  rel_w = ball_pos_w - robot_pos_w  # [B, 3]
  rel_b = quat_apply_inverse(robot_quat_w, rel_w)  # [B, 3] in body frame
  return rel_b.clamp(-clip_distance, clip_distance)


def goal_direction(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> torch.Tensor:
  """Goal direction as a unit vector in the robot's base frame.

  Returns:
    Tensor of shape ``[B, 2]`` (forward, lateral), unit-normalised.
  """
  robot: Entity = env.scene[robot_cfg.name]
  robot_quat_w = robot.data.root_link_quat_w  # [B, 4]

  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  goal_pos_w = command[:, :2] + env.scene.env_origins[:, :2]

  robot_pos_w = robot.data.root_link_pos_w[:, :2]  # [B, 2]
  diff_w = goal_pos_w - robot_pos_w  # [B, 2]
  dist = torch.norm(diff_w, dim=-1, keepdim=True).clamp(min=1e-6)
  dir_w = diff_w / dist  # unit vec in world frame

  # Rotate into robot body frame (yaw only).
  dir_w_3d = torch.cat([dir_w, torch.zeros_like(dir_w[:, :1])], dim=-1)
  dir_b_3d = quat_apply_inverse(robot_quat_w, dir_w_3d)
  return dir_b_3d[:, :2]  # [B, 2]


def ball_to_goal_direction(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Return the ball-to-goal direction in the robot body frame.

  Goal commands are stored relative to each environment origin, while ball and
  robot positions are world-frame values.  The returned unit vector therefore
  remains correct for batched environments and directly describes the desired
  launch direction.
  """
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]

  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  goal_pos_w = command[:, :2] + env.scene.env_origins[:, :2]
  ball_pos_w = ball.data.root_link_pos_w[:, :2]
  direction_w = goal_pos_w - ball_pos_w
  direction_w = direction_w / torch.linalg.norm(
    direction_w, dim=-1, keepdim=True
  ).clamp(min=1.0e-6)

  direction_w_3d = torch.cat(
    [direction_w, torch.zeros_like(direction_w[:, :1])], dim=-1
  )
  direction_b = quat_apply_inverse(
    robot.data.root_link_quat_w, direction_w_3d
  )
  return direction_b[:, :2]

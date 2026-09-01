"""Shared kick-approach geometry helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv


def ball_to_goal_direction_xy(
  env: ManagerBasedRlEnv,
  ball_pos_xy: torch.Tensor,
  command_name: str,
) -> torch.Tensor:
  """Unit vector from the ball to the goal in world XY."""
  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  goal_pos = command[:, :2] + env.scene.env_origins[:, :2]
  ball_to_goal = goal_pos - ball_pos_xy
  return ball_to_goal / torch.linalg.norm(
    ball_to_goal, dim=-1, keepdim=True
  ).clamp(min=1.0e-6)


def behind_ball_waypoint_xy(
  env: ManagerBasedRlEnv,
  ball_pos_xy: torch.Tensor,
  target_distance: float,
  command_name: str,
) -> torch.Tensor:
  """Target-side approach point behind the ball."""
  ball_to_goal = ball_to_goal_direction_xy(env, ball_pos_xy, command_name)
  return ball_pos_xy - ball_to_goal * target_distance

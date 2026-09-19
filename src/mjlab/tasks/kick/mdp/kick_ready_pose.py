"""Shared kick-ready pose scoring for rewards and terminations."""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from mjlab.entity import Entity
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.tasks.kick.mdp.geometry import (
  ball_to_goal_direction_xy,
  behind_ball_waypoint_xy,
)
from mjlab.utils.lab_api.math import quat_apply, quat_apply_inverse

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_DEFAULT_ROBOT_CFG = SceneEntityCfg("robot")
_DEFAULT_BALL_CFG = SceneEntityCfg("ball")


def compute_kick_ready_score(
  env: ManagerBasedRlEnv,
  target_distance: float,
  command_name: str,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  waypoint_std: float = 0.20,
  distance_std: float = 0.08,
  lateral_half_width: float = 0.12,
  bearing_std: float = 0.35,
  target_alignment_std: float = 0.20,
  camera_soft_limit: float = 0.78,
  camera_sigma: float = 0.35,
) -> torch.Tensor:
  """Return the multiplicative kick-ready score in ``[0, 1]``."""
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]

  robot_pos_w = robot.data.root_link_pos_w
  ball_pos_w = ball.data.root_link_pos_w
  ball_pos_xy = ball_pos_w[:, :2]
  waypoint = behind_ball_waypoint_xy(env, ball_pos_xy, target_distance, command_name)
  waypoint_error_sq = torch.sum(torch.square(robot_pos_w[:, :2] - waypoint), dim=-1)
  waypoint_score = torch.exp(-waypoint_error_sq / waypoint_std**2)

  rel_b = quat_apply_inverse(robot.data.root_link_quat_w, ball_pos_w - robot_pos_w)
  fwd_error = torch.abs(rel_b[:, 0] - target_distance)
  distance_score = torch.exp(-torch.square(fwd_error) / distance_std**2)
  lateral_score = torch.exp(
    -torch.square(rel_b[:, 1]) / (lateral_half_width / 2.0) ** 2
  )
  front_score = torch.sigmoid(20.0 * rel_b[:, 0])
  kick_zone_score = front_score * distance_score * lateral_score

  bearing = torch.atan2(rel_b[:, 1], rel_b[:, 0])
  facing_ball_score = torch.exp(-torch.square(bearing) / bearing_std**2)

  ball_to_goal = ball_to_goal_direction_xy(env, ball_pos_xy, command_name)
  ball_to_goal_3d = torch.cat(
    [ball_to_goal, torch.zeros_like(ball_to_goal[:, :1])], dim=-1
  )
  body_forward = quat_apply(
    robot.data.root_link_quat_w,
    torch.tensor([1.0, 0.0, 0.0], device=env.device).expand_as(ball_to_goal_3d),
  )
  target_alignment = torch.sum(body_forward * ball_to_goal_3d, dim=-1)
  target_alignment_score = torch.exp(
    -torch.square(1.0 - target_alignment) / target_alignment_std**2
  )

  outside_camera_cone = torch.clamp(torch.abs(bearing) - camera_soft_limit, min=0.0)
  camera_score = torch.exp(-torch.square(outside_camera_cone) / camera_sigma**2)

  return (
    waypoint_score
    * kick_zone_score
    * facing_ball_score
    * target_alignment_score
    * camera_score
  )


def kick_ready_activation_mask(
  env: ManagerBasedRlEnv,
  robot_cfg: SceneEntityCfg,
  ball_cfg: SceneEntityCfg,
  command_name: str,
  target_distance: float,
  kick_ready_threshold: float,
) -> torch.Tensor:
  """Return 1 only when the robot is in a genuine kick-ready pose."""
  ready_score = compute_kick_ready_score(
    env,
    target_distance=target_distance,
    command_name=command_name,
    robot_cfg=robot_cfg,
    ball_cfg=ball_cfg,
  )
  return (ready_score >= kick_ready_threshold).float()

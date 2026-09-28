from __future__ import annotations

from typing import TYPE_CHECKING, cast

import torch

from mjlab.utils.lab_api.math import (
  matrix_from_quat,
  quat_apply_inverse,
  subtract_frame_transforms,
)

from .commands import MotionCommand

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv


def motion_anchor_pos_b(env: ManagerBasedRlEnv, command_name: str) -> torch.Tensor:
  command = cast(MotionCommand, env.command_manager.get_term(command_name))

  pos, _ = subtract_frame_transforms(
    command.robot_anchor_pos_w,
    command.robot_anchor_quat_w,
    command.anchor_pos_w,
    command.anchor_quat_w,
  )

  return pos.view(env.num_envs, -1)


def ball_pos_b(env: ManagerBasedRlEnv, command_name: str) -> torch.Tensor:
  """Ball position in the robot trunk frame, clipped to ±8 m."""
  command = cast(MotionCommand, env.command_manager.get_term(command_name))
  ball = env.scene["ball"]
  rel_w = ball.data.root_link_pos_w - command.robot_anchor_pos_w
  rel_b = quat_apply_inverse(command.robot_anchor_quat_w, rel_w)
  return rel_b.clamp(-8.0, 8.0)


def target_pos_b(env: ManagerBasedRlEnv, command_name: str = "goal") -> torch.Tensor:
  """Goal position in the robot trunk frame. The goal lies on the ground plane."""
  motion = cast(MotionCommand, env.command_manager.get_term("motion"))
  goal_xy = env.command_manager.get_command(command_name)
  assert goal_xy is not None
  goal_w = torch.cat(
    [
      goal_xy[:, :2] + env.scene.env_origins[:, :2],
      torch.zeros(env.num_envs, 1, device=env.device),
    ],
    dim=-1,
  )
  rel_w = goal_w - motion.robot_anchor_pos_w
  rel_b = quat_apply_inverse(motion.robot_anchor_quat_w, rel_w)
  return rel_b.clamp(-18.0, 18.0)


def motion_style_z(env: ManagerBasedRlEnv, command_name: str) -> torch.Tensor:
  """One-hot kick style for the clip this env is tracking. Shape (N, 3)."""
  command = cast(MotionCommand, env.command_manager.get_term(command_name))
  return command.style_z


def motion_anchor_ori_b(env: ManagerBasedRlEnv, command_name: str) -> torch.Tensor:
  command = cast(MotionCommand, env.command_manager.get_term(command_name))

  _, ori = subtract_frame_transforms(
    command.robot_anchor_pos_w,
    command.robot_anchor_quat_w,
    command.anchor_pos_w,
    command.anchor_quat_w,
  )
  mat = matrix_from_quat(ori)
  return mat[..., :2].reshape(mat.shape[0], -1)


def robot_body_pos_b(env: ManagerBasedRlEnv, command_name: str) -> torch.Tensor:
  command = cast(MotionCommand, env.command_manager.get_term(command_name))

  num_bodies = len(command.cfg.body_names)
  pos_b, _ = subtract_frame_transforms(
    command.robot_anchor_pos_w[:, None, :].repeat(1, num_bodies, 1),
    command.robot_anchor_quat_w[:, None, :].repeat(1, num_bodies, 1),
    command.robot_body_pos_w,
    command.robot_body_quat_w,
  )

  return pos_b.view(env.num_envs, -1)


def robot_body_ori_b(env: ManagerBasedRlEnv, command_name: str) -> torch.Tensor:
  command = cast(MotionCommand, env.command_manager.get_term(command_name))

  num_bodies = len(command.cfg.body_names)
  _, ori_b = subtract_frame_transforms(
    command.robot_anchor_pos_w[:, None, :].repeat(1, num_bodies, 1),
    command.robot_anchor_quat_w[:, None, :].repeat(1, num_bodies, 1),
    command.robot_body_pos_w,
    command.robot_body_quat_w,
  )
  mat = matrix_from_quat(ori_b)
  return mat[..., :2].reshape(mat.shape[0], -1)

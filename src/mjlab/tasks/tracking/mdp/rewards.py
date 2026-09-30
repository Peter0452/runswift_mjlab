from __future__ import annotations

from typing import TYPE_CHECKING, cast

import torch

from mjlab.sensor import ContactSensor
from mjlab.utils.lab_api.math import quat_error_magnitude

from .commands import MotionCommand
from .stand_blend import SOLE_OFFSET, motor_limits

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv


def _get_body_indexes(
  command: MotionCommand, body_names: tuple[str, ...] | None
) -> list[int]:
  return [
    i
    for i, name in enumerate(command.cfg.body_names)
    if (body_names is None) or (name in body_names)
  ]


def motion_global_anchor_position_error_exp(
  env: ManagerBasedRlEnv, command_name: str, std: float
) -> torch.Tensor:
  command = cast(MotionCommand, env.command_manager.get_term(command_name))
  error = torch.sum(
    torch.square(command.anchor_pos_w - command.robot_anchor_pos_w), dim=-1
  )
  return torch.exp(-error / std**2)


def motion_global_anchor_orientation_error_exp(
  env: ManagerBasedRlEnv, command_name: str, std: float
) -> torch.Tensor:
  command = cast(MotionCommand, env.command_manager.get_term(command_name))
  error = quat_error_magnitude(command.anchor_quat_w, command.robot_anchor_quat_w) ** 2
  return torch.exp(-error / std**2)


def motion_relative_body_position_error_exp(
  env: ManagerBasedRlEnv,
  command_name: str,
  std: float,
  body_names: tuple[str, ...] | None = None,
) -> torch.Tensor:
  command = cast(MotionCommand, env.command_manager.get_term(command_name))
  body_indexes = _get_body_indexes(command, body_names)
  error = torch.sum(
    torch.square(
      command.body_pos_relative_w[:, body_indexes]
      - command.robot_body_pos_w[:, body_indexes]
    ),
    dim=-1,
  )
  return torch.exp(-error.mean(-1) / std**2)


def motion_relative_body_orientation_error_exp(
  env: ManagerBasedRlEnv,
  command_name: str,
  std: float,
  body_names: tuple[str, ...] | None = None,
) -> torch.Tensor:
  command = cast(MotionCommand, env.command_manager.get_term(command_name))
  body_indexes = _get_body_indexes(command, body_names)
  error = (
    quat_error_magnitude(
      command.body_quat_relative_w[:, body_indexes],
      command.robot_body_quat_w[:, body_indexes],
    )
    ** 2
  )
  return torch.exp(-error.mean(-1) / std**2)


def motion_global_body_linear_velocity_error_exp(
  env: ManagerBasedRlEnv,
  command_name: str,
  std: float,
  body_names: tuple[str, ...] | None = None,
) -> torch.Tensor:
  command = cast(MotionCommand, env.command_manager.get_term(command_name))
  body_indexes = _get_body_indexes(command, body_names)
  error = torch.sum(
    torch.square(
      command.body_lin_vel_w[:, body_indexes]
      - command.robot_body_lin_vel_w[:, body_indexes]
    ),
    dim=-1,
  )
  return torch.exp(-error.mean(-1) / std**2)


def motion_global_body_angular_velocity_error_exp(
  env: ManagerBasedRlEnv,
  command_name: str,
  std: float,
  body_names: tuple[str, ...] | None = None,
) -> torch.Tensor:
  command = cast(MotionCommand, env.command_manager.get_term(command_name))
  body_indexes = _get_body_indexes(command, body_names)
  error = torch.sum(
    torch.square(
      command.body_ang_vel_w[:, body_indexes]
      - command.robot_body_ang_vel_w[:, body_indexes]
    ),
    dim=-1,
  )
  return torch.exp(-error.mean(-1) / std**2)


def action_smoothness(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Penalize action acceleration, clamped so one spike cannot dominate."""
  action_acc = (
    env.action_manager.action
    - 2 * env.action_manager.prev_action
    + env.action_manager.prev_prev_action
  )
  return torch.sum(torch.square(action_acc), dim=1).clamp(0.0, 10.0)


def feet_slip(
  env: ManagerBasedRlEnv,
  command_name: str,
  sensor_name: str,
  body_names: tuple[str, ...],
  threshold: float = 1.0,
) -> torch.Tensor:
  """Penalize horizontal foot speed while that foot is on the ground."""
  command = cast(MotionCommand, env.command_manager.get_term(command_name))
  sensor: ContactSensor = env.scene[sensor_name]
  assert sensor.data.force is not None
  force = sensor.data.force
  body_index = {name: i for i, name in enumerate(command.cfg.body_names)}
  speeds = []
  contacts = []
  for slot, name in enumerate(sensor.primary_names):
    if name not in body_names:
      continue
    body = body_index[name]
    speed_xy = torch.linalg.norm(command.robot_body_lin_vel_w[:, body, :2], dim=-1)
    contact = torch.linalg.norm(force[:, slot], dim=-1) > threshold
    speeds.append(speed_xy)
    contacts.append(contact)
  foot_speed = torch.stack(speeds, dim=1)
  foot_contact = torch.stack(contacts, dim=1)
  slipping = torch.where(foot_contact, foot_speed, torch.zeros_like(foot_speed))
  return torch.sum(torch.square(slipping), dim=-1)


def no_fly(
  env: ManagerBasedRlEnv,
  command_name: str,
  body_names: tuple[str, ...],
  height: float = 0.05,
) -> torch.Tensor:
  """1 when every selected foot is above ``height`` at the same time."""
  command = cast(MotionCommand, env.command_manager.get_term(command_name))
  body_index = {name: i for i, name in enumerate(command.cfg.body_names)}
  indexes = [body_index[name] for name in body_names]
  foot_z = command.robot_body_pos_w[:, indexes, 2] - env.scene.env_origins[:, 2:3]
  return torch.all(foot_z > height, dim=-1).float()


def stand_joint_pose(
  env: ManagerBasedRlEnv,
  command_name: str,
  std: float,
) -> torch.Tensor:
  """Match the AMP walk stand. Zero until the ball has left and the clip is over."""
  command = cast(MotionCommand, env.command_manager.get_term(command_name))
  if not command.cfg.stand_after_kick:
    return torch.zeros(env.num_envs, device=env.device)
  error = torch.sum(torch.square(command.robot_joint_pos - command.joint_pos), dim=-1)
  reward = torch.exp(-error / std**2)
  return torch.where(command.standing, reward, torch.zeros_like(reward))


def base_height_too_low(
  env: ManagerBasedRlEnv,
  command_name: str,
  threshold: float = 0.48,
) -> torch.Tensor:
  """Meters the trunk is below ``threshold``, unless that is the clip height.

  The floor is the reference trunk height when the clip itself is under
  ``threshold``. Matching the clip pays nothing.
  """
  command = cast(MotionCommand, env.command_manager.get_term(command_name))
  origin_z = env.scene.env_origins[:, 2]
  robot_z = command.robot_anchor_pos_w[:, 2] - origin_z
  reference_z = command.anchor_pos_w[:, 2] - origin_z
  floor = torch.minimum(reference_z, robot_z.new_full(robot_z.shape, threshold))
  return torch.clamp(floor - robot_z, min=0.0)


def ee_body_pos_fall_penalty(
  env: ManagerBasedRlEnv,
  command_name: str,
  threshold: float,
  body_names: tuple[str, ...],
) -> torch.Tensor:
  """1 when a foot or hand height leaves the reference by more than ``threshold``."""
  command = cast(MotionCommand, env.command_manager.get_term(command_name))
  body_indexes = _get_body_indexes(command, body_names)
  error = torch.abs(
    command.body_pos_relative_w[:, body_indexes, -1]
    - command.robot_body_pos_w[:, body_indexes, -1]
  )
  return torch.any(error > threshold, dim=-1).float()


def foot_sole_penetration(
  env: ManagerBasedRlEnv,
  command_name: str,
  body_names: tuple[str, ...],
  clearance: float = 0.01,
) -> torch.Tensor:
  """Meters a foot sole is below the ground while recovering to the stand.

  The foot-link origin sits about ``SOLE_OFFSET`` above a flat sole. Active
  only after the clip, so the kick plant is not punished for the same estimate.
  """
  command = cast(MotionCommand, env.command_manager.get_term(command_name))
  indexes = _get_body_indexes(command, body_names)
  sole = (
    command.robot_body_pos_w[:, indexes, 2]
    - env.scene.env_origins[:, None, 2]
    - SOLE_OFFSET
  )
  depth = torch.clamp(-(sole + clearance), min=0.0).sum(dim=-1)
  return torch.where(command.standing, depth, torch.zeros_like(depth))


def joint_velocity_over_motor(
  env: ManagerBasedRlEnv,
  command_name: str,
) -> torch.Tensor:
  """Rad/s each joint is past its motor speed limit, during the stand blend."""
  command = cast(MotionCommand, env.command_manager.get_term(command_name))
  velocity = command.robot_joint_vel
  limits = velocity.new_tensor(
    [motor_limits(name)[3] for name in command.robot.joint_names]
  )
  excess = torch.clamp(velocity.abs() - limits, min=0.0).sum(dim=-1)
  return torch.where(command.standing, excess, torch.zeros_like(excess))


def self_collision_cost(
  env: ManagerBasedRlEnv,
  sensor_name: str,
  force_threshold: float = 10.0,
) -> torch.Tensor:
  """Penalize self-collisions.

  When the sensor provides force history (from ``history_length > 0``),
  counts substeps where any contact force exceeds *force_threshold*.
  Falls back to the instantaneous ``found`` count otherwise.
  """
  sensor: ContactSensor = env.scene[sensor_name]
  data = sensor.data
  if data.force_history is not None:
    # force_history: [B, N, H, 3]
    force_mag = torch.norm(data.force_history, dim=-1)  # [B, N, H]
    hit = (force_mag > force_threshold).any(dim=1)  # [B, H]
    return hit.sum(dim=-1).float()  # [B]
  assert data.found is not None
  return data.found.squeeze(-1)

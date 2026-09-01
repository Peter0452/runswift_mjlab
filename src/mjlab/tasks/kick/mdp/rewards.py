"""Kick-task reward terms."""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from mjlab.entity import Entity
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.tasks.kick.mdp.geometry import (
  behind_ball_waypoint_xy,
  ball_to_goal_direction_xy,
)
from mjlab.utils.lab_api.math import quat_apply, quat_apply_inverse
from mjlab.utils.lab_api.math import quat_apply, quat_apply_inverse

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_DEFAULT_ROBOT_CFG = SceneEntityCfg("robot")
_DEFAULT_BALL_CFG = SceneEntityCfg("ball")


def trunk_orientation_l2(
  env: ManagerBasedRlEnv,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> torch.Tensor:
  """Penalize roll/pitch of the robot's upper-body trunk.

  The K1 root and ``Trunk`` body are distinct model bodies.  Using the root's
  projected gravity alone therefore does not guarantee that the upper body
  stays upright while the legs move.
  """
  robot: Entity = env.scene[robot_cfg.name]
  if robot_cfg.body_ids:
    trunk_quat_w = robot.data.body_link_quat_w[:, robot_cfg.body_ids, :].squeeze(1)
  else:
    trunk_quat_w = robot.data.root_link_quat_w
  projected_gravity_b = quat_apply_inverse(trunk_quat_w, robot.data.gravity_vec_w)
  return torch.sum(torch.square(projected_gravity_b[:, :2]), dim=1)


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


def ball_distance_band(
  env: ManagerBasedRlEnv,
  min_distance: float = 0.35,
  max_distance: float = 0.45,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Reward planar ball distance inside ``[min_distance, max_distance]``.

  Returns ``+1`` inside the band and penalises crowding inside ``min_distance``.
  Long-range spawns are shaped by ``ball_approach_far`` instead.
  """
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]

  robot_pos = robot.data.root_link_pos_w[:, :2]
  ball_pos = ball.data.root_link_pos_w[:, :2]
  distance = torch.linalg.norm(ball_pos - robot_pos, dim=-1)

  in_band = (
    (distance >= min_distance) & (distance <= max_distance)
  ).float()
  too_close = torch.clamp(min_distance - distance, min=0.0)

  env.extras["log"]["Metrics/ball_distance"] = distance.mean()
  env.extras["log"]["Metrics/ball_distance_band_violation"] = too_close.mean()
  env.extras["log"]["Metrics/ball_distance_in_band_fraction"] = in_band.mean()
  # Outside the band: penalise crowding in, but do not punish long-range spawns.
  # Far approach is handled by ``ball_approach_far``.
  return in_band - too_close


def ball_approach_far(
  env: ManagerBasedRlEnv,
  activate_distance: float = 0.6,
  std: float = 2.5,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Reward closing distance to the ball while still outside the kick band.

  Active when planar distance exceeds ``activate_distance`` so the policy
  learns to walk in from long range without a large constant penalty.
  """
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]

  robot_pos = robot.data.root_link_pos_w[:, :2]
  ball_pos = ball.data.root_link_pos_w[:, :2]
  distance = torch.linalg.norm(ball_pos - robot_pos, dim=-1)

  active = (distance > activate_distance).float()
  reward = torch.exp(-torch.square(distance) / std**2)
  env.extras["log"]["Metrics/ball_approach_far_reward"] = (
    (active * reward).mean()
  )
  return active * reward


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


def behind_ball_waypoint(
  env: ManagerBasedRlEnv,
  target_distance: float = 0.35,
  std: float = 0.50,
  command_name: str = "goal",
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Reward the robot for reaching the target-side approach point.

  The waypoint is behind the ball relative to the ball-to-goal direction.  A
  robot that is beside the ball must therefore walk around it instead of
  merely rotating in place.
  """
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]

  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  ball_pos = ball.data.root_link_pos_w[:, :2]
  waypoint = behind_ball_waypoint_xy(env, ball_pos, target_distance, command_name)

  robot_pos = robot.data.root_link_pos_w[:, :2]
  distance_sq = torch.sum(torch.square(robot_pos - waypoint), dim=-1)
  reward = torch.exp(-distance_sq / std**2)
  env.extras["log"]["Metrics/behind_ball_distance"] = torch.sqrt(
    distance_sq
  ).mean()
  return reward


def body_face_ball(
  env: ManagerBasedRlEnv,
  sigma: float = 0.60,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Reward the robot for keeping the ball in front of its body."""
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  rel_w = ball.data.root_link_pos_w - robot.data.root_link_pos_w
  rel_b = quat_apply_inverse(robot.data.root_link_quat_w, rel_w)
  bearing = torch.atan2(rel_b[:, 1], rel_b[:, 0])
  reward = torch.exp(-torch.square(bearing) / sigma**2)
  env.extras["log"]["Metrics/ball_bearing_abs"] = torch.abs(bearing).mean()
  return reward


def ball_camera_cone(
  env: ManagerBasedRlEnv,
  soft_limit: float = 0.78,
  sigma: float = 0.35,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Reward keeping the ball inside a forward-facing camera cone.

  ``soft_limit`` is the preferred half-angle in radians.  The reward smoothly
  decays outside that cone and remains finite if the ball moves behind the
  robot.
  """
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  rel_w = ball.data.root_link_pos_w - robot.data.root_link_pos_w
  rel_b = quat_apply_inverse(robot.data.root_link_quat_w, rel_w)
  bearing = torch.atan2(rel_b[:, 1], rel_b[:, 0]).abs()
  outside = torch.clamp(bearing - soft_limit, min=0.0)
  return torch.exp(-torch.square(outside) / sigma**2)


def kick_ready(
  env: ManagerBasedRlEnv,
  target_distance: float = 0.35,
  waypoint_std: float = 0.20,
  distance_std: float = 0.08,
  lateral_half_width: float = 0.12,
  bearing_std: float = 0.35,
  target_alignment_std: float = 0.20,
  camera_soft_limit: float = 0.78,
  camera_sigma: float = 0.35,
  command_name: str = "goal",
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Reward the complete preparation pose for a kick.

  Readiness combines four conditions: the robot is at the behind-ball
  waypoint, the ball is in the kick distance/lateral corridor, the body faces
  the ball-to-goal line, and the ball remains inside the forward camera cone.
  The multiplicative form prevents a good score from only one condition from
  masking a failed alignment condition.
  """
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]

  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  robot_pos_w = robot.data.root_link_pos_w
  ball_pos_w = ball.data.root_link_pos_w
  ball_pos_xy = ball_pos_w[:, :2]
  waypoint = behind_ball_waypoint_xy(env, ball_pos_xy, target_distance, command_name)
  waypoint_error_sq = torch.sum(
    torch.square(robot_pos_w[:, :2] - waypoint), dim=-1
  )
  waypoint_score = torch.exp(-waypoint_error_sq / waypoint_std**2)

  rel_b = quat_apply_inverse(
    robot.data.root_link_quat_w, ball_pos_w - robot_pos_w
  )
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

  outside_camera_cone = torch.clamp(
    torch.abs(bearing) - camera_soft_limit, min=0.0
  )
  camera_score = torch.exp(
    -torch.square(outside_camera_cone) / camera_sigma**2
  )

  reward = (
    waypoint_score
    * kick_zone_score
    * facing_ball_score
    * target_alignment_score
    * camera_score
  )
  env.extras["log"]["Metrics/kick_ready_reward"] = reward.mean()
  env.extras["log"]["Metrics/kick_ready_fraction"] = (
    (reward > 0.5).float().mean()
  )
  env.extras["log"]["Metrics/kick_ready_waypoint_error"] = torch.sqrt(
    waypoint_error_sq
  ).mean()
  return reward


def waypoint_approach_velocity(
  env: ManagerBasedRlEnv,
  target_distance: float = 0.35,
  command_name: str = "goal",
  activate_ball_distance: float = 0.55,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Reward planar velocity toward the behind-ball waypoint.

  Active only while the robot is still outside the kick-ready hold zone so it
  reinforces closing distance instead of jittering once ready.
  """
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]

  robot_pos = robot.data.root_link_pos_w
  ball_pos = ball.data.root_link_pos_w[:, :2]
  waypoint = behind_ball_waypoint_xy(env, ball_pos, target_distance, command_name)

  to_waypoint = waypoint - robot_pos[:, :2]
  dir_w = to_waypoint / torch.linalg.norm(to_waypoint, dim=-1, keepdim=True).clamp(
    min=1.0e-6
  )
  vel_w = robot.data.root_link_lin_vel_w[:, :2]
  progress = torch.sum(vel_w * dir_w, dim=-1).clamp(min=0.0)

  ball_distance = torch.linalg.norm(ball_pos - robot_pos[:, :2], dim=-1)
  active = (ball_distance > activate_ball_distance).float()
  env.extras["log"]["Metrics/waypoint_approach_velocity"] = (
    (active * progress).mean()
  )
  return active * progress


def waypoint_retreat_penalty(
  env: ManagerBasedRlEnv,
  target_distance: float = 0.35,
  command_name: str = "goal",
  activate_ball_distance: float = 0.55,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Penalise velocity away from the behind-ball waypoint while approaching."""
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]

  robot_pos = robot.data.root_link_pos_w
  ball_pos = ball.data.root_link_pos_w[:, :2]
  waypoint = behind_ball_waypoint_xy(env, ball_pos, target_distance, command_name)

  to_waypoint = waypoint - robot_pos[:, :2]
  dir_w = to_waypoint / torch.linalg.norm(to_waypoint, dim=-1, keepdim=True).clamp(
    min=1.0e-6
  )
  vel_w = robot.data.root_link_lin_vel_w[:, :2]
  progress = torch.sum(vel_w * dir_w, dim=-1)
  retreat = torch.clamp(-progress, min=0.0)

  ball_distance = torch.linalg.norm(ball_pos - robot_pos[:, :2], dim=-1)
  active = (ball_distance > activate_ball_distance).float()
  env.extras["log"]["Metrics/waypoint_retreat_penalty"] = (
    (active * retreat).mean()
  )
  return active * retreat


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

"""Kick-task reward terms."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import torch

from mjlab.entity import Entity
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.sensor.contact_sensor import ContactSensor
from mjlab.tasks.kick.mdp.ball_phase import ensure_ball_phase_updated
from mjlab.tasks.kick.mdp.geometry import (
  ball_to_goal_direction_xy,
  behind_ball_waypoint_xy,
  expected_ballistic_speed,
  get_approach_waypoint_latch,
)
from mjlab.tasks.kick.mdp.kick_ready_pose import (
  compute_kick_ready_score,
  kick_ready_activation_mask,
)
from mjlab.utils.lab_api.math import quat_apply, quat_apply_inverse

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_DEFAULT_ROBOT_CFG = SceneEntityCfg("robot")
_DEFAULT_BALL_CFG = SceneEntityCfg("ball")


def _robot_ball_planar_distance(
  env: ManagerBasedRlEnv,
  robot_cfg: SceneEntityCfg,
  ball_cfg: SceneEntityCfg,
) -> torch.Tensor:
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  return torch.linalg.norm(
    ball.data.root_link_pos_w[:, :2] - robot.data.root_link_pos_w[:, :2], dim=-1
  )


def _planar_closing_speed(
  robot: Entity,
  waypoint: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
  """Return ``(v · dir_to_waypoint, planar distance)``."""
  to_waypoint = waypoint - robot.data.root_link_pos_w[:, :2]
  dist = torch.linalg.norm(to_waypoint, dim=-1)
  direction = to_waypoint / dist.unsqueeze(-1).clamp(min=1.0e-6)
  vel_xy = robot.data.root_link_lin_vel_w[:, :2]
  return torch.sum(vel_xy * direction, dim=-1), dist


def _approach_phase_mask(
  env: ManagerBasedRlEnv,
  robot_cfg: SceneEntityCfg,
  ball_cfg: SceneEntityCfg,
  inactive_inside_ball_distance: float | None,
) -> torch.Tensor:
  """Return 1 while the robot is still outside the kick-contact zone."""
  if inactive_inside_ball_distance is None:
    return torch.ones(env.num_envs, device=env.device)
  distance = _robot_ball_planar_distance(env, robot_cfg, ball_cfg)
  return (distance > inactive_inside_ball_distance).float()


def _kick_zone_mask(
  env: ManagerBasedRlEnv,
  robot_cfg: SceneEntityCfg,
  ball_cfg: SceneEntityCfg,
  activate_inside_ball_distance: float,
) -> torch.Tensor:
  distance = _robot_ball_planar_distance(env, robot_cfg, ball_cfg)
  return (distance <= activate_inside_ball_distance).float()


def _ball_stationary_mask(
  env: ManagerBasedRlEnv,
  ball_cfg: SceneEntityCfg,
  ball_stationary_speed_threshold: float,
) -> torch.Tensor:
  ball: Entity = env.scene[ball_cfg.name]
  speed = torch.linalg.norm(ball.data.root_link_lin_vel_w[:, :2], dim=-1)
  return (speed <= ball_stationary_speed_threshold).float()


def _approach_reward_gate(
  env: ManagerBasedRlEnv,
  robot_cfg: SceneEntityCfg,
  ball_cfg: SceneEntityCfg,
  inactive_inside_ball_distance: float | None,
  require_ball_stationary: bool,
  ball_stationary_speed_threshold: float,
) -> torch.Tensor:
  gate = _approach_phase_mask(env, robot_cfg, ball_cfg, inactive_inside_ball_distance)
  if require_ball_stationary:
    gate = gate * _ball_stationary_mask(env, ball_cfg, ball_stationary_speed_threshold)
  return gate


def _compute_kick_ready_score(
  env: ManagerBasedRlEnv,
  target_distance: float,
  command_name: str,
  robot_cfg: SceneEntityCfg,
  ball_cfg: SceneEntityCfg,
  **kwargs,
) -> torch.Tensor:
  return compute_kick_ready_score(
    env,
    target_distance=target_distance,
    command_name=command_name,
    robot_cfg=robot_cfg,
    ball_cfg=ball_cfg,
    **kwargs,
  )


def _kick_ready_activation_mask(
  env: ManagerBasedRlEnv,
  robot_cfg: SceneEntityCfg,
  ball_cfg: SceneEntityCfg,
  command_name: str,
  target_distance: float,
  kick_ready_threshold: float,
) -> torch.Tensor:
  return kick_ready_activation_mask(
    env,
    robot_cfg,
    ball_cfg,
    command_name,
    target_distance,
    kick_ready_threshold,
  )


def _kick_contact_activation_mask(
  env: ManagerBasedRlEnv,
  state,
  robot_cfg: SceneEntityCfg,
  ball_cfg: SceneEntityCfg,
  ball_stationary_speed_threshold: float,
  require_kick_ready: bool,
  kick_ready_threshold: float,
  command_name: str,
  target_distance: float,
  activate_inside_ball_distance: float | None,
  before_contact: bool = True,
) -> torch.Tensor:
  """Mask for kick-contact rewards: ready pose, stationary ball, optional pre-contact."""
  stationary = _ball_stationary_mask(env, ball_cfg, ball_stationary_speed_threshold)
  if require_kick_ready:
    active = _kick_ready_activation_mask(
      env,
      robot_cfg,
      ball_cfg,
      command_name,
      target_distance,
      kick_ready_threshold,
    )
  elif activate_inside_ball_distance is not None:
    active = _kick_zone_mask(env, robot_cfg, ball_cfg, activate_inside_ball_distance)
  else:
    active = torch.ones(env.num_envs, device=env.device)
  active = active * stationary
  if before_contact:
    active = active * (~state.kick_detected).float()
  return active


def _resolve_foot_ids(
  robot: Entity,
  feet_cfg: SceneEntityCfg | None,
) -> list[int]:
  if feet_cfg is not None and feet_cfg.body_ids != slice(None):
    return list(feet_cfg.body_ids)
  left_ids, _ = robot.find_bodies("left_foot_link")
  right_ids, _ = robot.find_bodies("right_foot_link")
  return [left_ids[0], right_ids[0]]


def _kick_stance_foot_indices(
  env: ManagerBasedRlEnv,
  robot: Entity,
  ball: Entity,
) -> tuple[torch.Tensor, torch.Tensor]:
  """Return kicking/support foot indices (0=left, 1=right).

  Spawn-side latch (yellow plant) wins when set: +1 left of axis → right
  foot kicks. Otherwise ball-on-left in the body frame.
  """
  latch = get_approach_waypoint_latch(env)
  if latch is not None and bool((latch.side.abs() > 0.5).any()):
    kicking_idx = (latch.side > 0.0).to(dtype=torch.long)
    return kicking_idx, 1 - kicking_idx
  rel_w = ball.data.root_link_pos_w - robot.data.root_link_pos_w
  rel_b = quat_apply_inverse(robot.data.root_link_quat_w, rel_w)
  ball_on_left = rel_b[:, 1] > 0.0
  kicking_idx = torch.where(
    ball_on_left,
    torch.ones(env.num_envs, dtype=torch.long, device=env.device),
    torch.zeros(env.num_envs, dtype=torch.long, device=env.device),
  )
  support_idx = 1 - kicking_idx
  return kicking_idx, support_idx


def _gather_foot_tensor(
  values: torch.Tensor,
  foot_indices: torch.Tensor,
) -> torch.Tensor:
  """Select per-env foot rows from ``[B, 2, ...]`` foot tensors."""
  batch = torch.arange(values.shape[0], device=values.device)
  return values[batch, foot_indices]


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


def _plant_latch_mask(env: ManagerBasedRlEnv) -> torch.Tensor:
  latch = get_approach_waypoint_latch(env)
  if latch is None:
    return torch.zeros(env.num_envs, device=env.device)
  return latch.at_plant.float()


_LATCH_BONUS_PREV = "_kick_latch_bonus_prev_at_plant"


def plant_latch_arrival_bonus(env: ManagerBasedRlEnv) -> torch.Tensor:
  """One on the step ``at_plant`` first becomes true; zero otherwise."""
  zeros = torch.zeros(env.num_envs, device=env.device)
  latch = get_approach_waypoint_latch(env)
  if latch is None:
    return zeros
  prev = getattr(env, _LATCH_BONUS_PREV, None)
  if prev is None or prev.shape[0] != env.num_envs:
    prev = torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
  bonus = (latch.at_plant & ~prev).float()
  setattr(env, _LATCH_BONUS_PREV, latch.at_plant.clone())
  env.extras["log"]["Metrics/plant_latch_arrival"] = bonus.mean()
  return bonus


def ball_touch_keepout_penalty(
  env: ManagerBasedRlEnv,
  keepout_distance: float = 0.3,
  contact_cost: float = 1.0,
  feet_ball_sensor_name: str = "feet_ball_contact",
  body_ball_sensor_name: str = "body_ball_contact",
  release_when_planted: bool = False,
  release_all_when_planted: bool = False,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Approach-stage keep-out: do not enter / touch the ball disk.

  Returns a non-negative cost in roughly ``[0, 1 + contact_cost]``:
  - distance intrusion ``clamp((keepout − ‖robot−ball‖) / keepout, 0, 1)``
  - plus ``contact_cost`` on any feet/body↔ball contact

  With ``release_when_planted``, after the alignment latch swing-foot touch is
  legal; body and support-foot contact are still taxed. Setting
  ``release_all_when_planted`` removes the proximity keep-out entirely while
  leaving actual wrong-contact penalties to their separate reward term.
  """
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  dist = torch.linalg.norm(
    robot.data.root_link_pos_w[:, :2] - ball.data.root_link_pos_w[:, :2],
    dim=-1,
  )
  keepout = max(float(keepout_distance), 1.0e-6)
  intrusion = torch.clamp((keepout - dist) / keepout, min=0.0, max=1.0)

  def _any_contact(name: str) -> torch.Tensor:
    if name not in env.scene.sensors:
      return torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
    found = getattr(env.scene.sensors[name].data, "found", None)
    if found is None:
      return torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
    return found.reshape(found.shape[0], -1).any(dim=-1) > 0

  contact = _any_contact(feet_ball_sensor_name) | _any_contact(body_ball_sensor_name)
  cost = intrusion + float(contact_cost) * contact.float()
  if release_when_planted:
    planted = _plant_latch_mask(env)
    body = _any_contact(body_ball_sensor_name)
    _, support_idx = _kick_stance_foot_indices(env, robot, ball)
    foot_ids = _resolve_foot_ids(robot, None)
    feet_xy = robot.data.body_link_pos_w[:, foot_ids, :2]
    support_xy = _gather_foot_tensor(feet_xy, support_idx)
    support_near = (
      torch.linalg.norm(support_xy - ball.data.root_link_pos_w[:, :2], dim=-1) < 0.16
    ).float()
    post = float(contact_cost) * (body.float() + support_near)
    if release_all_when_planted:
      post = torch.zeros_like(post)
    cost = cost * (1.0 - planted) + post * planted
    env.extras["log"]["Metrics/plant_support_near"] = (planted * support_near).mean()
  env.extras["log"]["Metrics/ball_keepout_intrusion"] = intrusion.mean()
  env.extras["log"]["Metrics/ball_touch_contact"] = contact.float().mean()
  env.extras["log"]["Metrics/ball_touch_keepout"] = cost.mean()
  return cost


def wrong_ball_contact_penalty(
  env: ManagerBasedRlEnv,
  feet_ball_sensor_name: str = "feet_ball_contact",
  body_ball_sensor_name: str = "body_ball_contact",
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Penalize support-foot or body contact while allowing the selected foot."""
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  _, support_idx = _kick_stance_foot_indices(env, robot, ball)

  support_contact = torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
  if feet_ball_sensor_name in env.scene.sensors:
    sensor = env.scene.sensors[feet_ball_sensor_name]
    assert isinstance(sensor, ContactSensor)
    found = getattr(sensor.data, "found", None)
    if found is not None:
      per_foot = found.reshape(env.num_envs, len(sensor.primary_names), -1).any(dim=-1)
      batch = torch.arange(env.num_envs, device=env.device)
      support_contact = per_foot[batch, support_idx]

  body_contact = torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
  if body_ball_sensor_name in env.scene.sensors:
    found = getattr(env.scene.sensors[body_ball_sensor_name].data, "found", None)
    if found is not None:
      body_contact = found.reshape(env.num_envs, -1).any(dim=-1)

  cost = (support_contact | body_contact).float()
  env.extras["log"]["Metrics/wrong_foot_ball_contact"] = support_contact.float().mean()
  env.extras["log"]["Metrics/body_ball_contact_penalty"] = body_contact.float().mean()
  return cost


def agent_approach_ball(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  velocity_eps: float = 0.1,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Dense cosine approach of agent velocity toward the ball (paper ``r_a-approach-b``).

  ``max(0, cos(v_agent, d_agent→ball)) / (1 + max(0, v_ball · d_target→ball))``
  when ``‖v_agent‖ > ε``, else 0. Inverse ball-progress scaling shrinks the
  approach signal once the ball is already moving toward the target.
  """
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]

  robot_pos = robot.data.root_link_pos_w[:, :2]
  robot_vel = robot.data.root_link_lin_vel_w[:, :2]
  ball_pos = ball.data.root_link_pos_w[:, :2]
  ball_vel = ball.data.root_link_lin_vel_w[:, :2]

  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  goal_pos = command[:, :2] + env.scene.env_origins[:, :2]

  d_agent_ball = ball_pos - robot_pos
  d_target_ball = goal_pos - ball_pos

  agent_speed = torch.linalg.norm(robot_vel, dim=-1)
  d_agent_norm = torch.linalg.norm(d_agent_ball, dim=-1).clamp(min=1.0e-6)
  cos_clip = (
    torch.sum(robot_vel * d_agent_ball, dim=-1)
    / (agent_speed.clamp(min=1.0e-6) * d_agent_norm)
  ).clamp(min=0.0)

  ball_progress = torch.sum(ball_vel * d_target_ball, dim=-1).clamp(min=0.0)
  reward = cos_clip / (1.0 + ball_progress)
  reward = torch.where(agent_speed > velocity_eps, reward, torch.zeros_like(reward))

  env.extras["log"]["Metrics/agent_approach_ball"] = reward.mean()
  env.extras["log"]["Metrics/ball_distance"] = d_agent_norm.mean()
  return reward


def ball_distance_band(
  env: ManagerBasedRlEnv,
  min_distance: float = 0.35,
  max_distance: float = 0.45,
  inactive_inside_ball_distance: float | None = None,
  require_ball_stationary: bool = False,
  ball_stationary_speed_threshold: float = 0.1,
  stop_after_plant_latch: bool = False,
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

  in_band = ((distance >= min_distance) & (distance <= max_distance)).float()
  too_close = torch.clamp(min_distance - distance, min=0.0)

  env.extras["log"]["Metrics/ball_distance"] = distance.mean()
  env.extras["log"]["Metrics/ball_distance_band_violation"] = too_close.mean()
  env.extras["log"]["Metrics/ball_distance_in_band_fraction"] = in_band.mean()
  # Outside the band: penalise crowding in, but do not punish long-range spawns.
  # Far approach is handled by ``ball_approach_far``.
  gate = _approach_reward_gate(
    env,
    robot_cfg,
    ball_cfg,
    inactive_inside_ball_distance,
    require_ball_stationary,
    ball_stationary_speed_threshold,
  )
  if stop_after_plant_latch:
    gate = gate * (1.0 - _plant_latch_mask(env))
  return (in_band - too_close) * gate


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
  env.extras["log"]["Metrics/ball_approach_far_reward"] = (active * reward).mean()
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


def _body_face_goal_yaw_score(
  env: ManagerBasedRlEnv,
  command_name: str,
  robot_cfg: SceneEntityCfg,
  ball_cfg: SceneEntityCfg,
  facing_std: float,
) -> torch.Tensor:
  """Gaussian on yaw error between body forward and ball→goal, in ``[0, 1]``."""
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  goal_dir = ball_to_goal_direction_xy(
    env, ball.data.root_link_pos_w[:, :2], command_name
  )
  goal_3d = torch.cat([goal_dir, torch.zeros_like(goal_dir[:, :1])], dim=-1)
  body_forward = quat_apply(
    robot.data.root_link_quat_w,
    torch.tensor([1.0, 0.0, 0.0], device=env.device, dtype=goal_3d.dtype).expand_as(
      goal_3d
    ),
  )
  fwd_xy = body_forward[:, :2]
  fwd_xy = fwd_xy / fwd_xy.norm(dim=-1, keepdim=True).clamp(min=1.0e-6)
  dot = (fwd_xy * goal_dir).sum(dim=-1).clamp(-1.0, 1.0)
  cross = fwd_xy[:, 0] * goal_dir[:, 1] - fwd_xy[:, 1] * goal_dir[:, 0]
  yaw_err = torch.atan2(cross, dot)
  sigma = max(float(facing_std), 1.0e-6)
  return torch.exp(-torch.square(yaw_err) / sigma**2)


def behind_ball_waypoint(
  env: ManagerBasedRlEnv,
  target_distance: float = 0.35,
  std: float = 0.50,
  command_name: str = "goal",
  facing_std: float | None = None,
  inactive_inside_ball_distance: float | None = None,
  require_ball_stationary: bool = False,
  ball_stationary_speed_threshold: float = 0.1,
  stop_after_plant_latch: bool = False,
  progress: bool = False,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Reward the behind-ball waypoint, optionally gated on heading.

  The waypoint is attached to the ball (behind it along ball→goal, plus any
  latched lateral offset). With ``progress=True``, pays heading-gated closing
  speed instead of a static Gaussian, so standing still earns nothing.
  """
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]

  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  ball_pos = ball.data.root_link_pos_w[:, :2]
  waypoint = behind_ball_waypoint_xy(env, ball_pos, target_distance, command_name)
  if facing_std is None:
    facing = torch.ones(env.num_envs, device=env.device, dtype=ball_pos.dtype)
  else:
    facing = _body_face_goal_yaw_score(
      env, command_name, robot_cfg, ball_cfg, facing_std
    )
  if progress:
    closing, dist = _planar_closing_speed(robot, waypoint)
    pos_score = closing.clamp(min=0.0)
    reward = pos_score * facing
  else:
    robot_pos = robot.data.root_link_pos_w[:, :2]
    distance_sq = torch.sum(torch.square(robot_pos - waypoint), dim=-1)
    dist = torch.sqrt(distance_sq)
    pos_score = torch.exp(-distance_sq / std**2)
    reward = pos_score * facing
  env.extras["log"]["Metrics/behind_ball_distance"] = dist.mean()
  env.extras["log"]["Metrics/waypoint_facing"] = facing.mean()
  env.extras["log"]["Metrics/waypoint_proximity_pos"] = pos_score.mean()
  gate = _approach_reward_gate(
    env,
    robot_cfg,
    ball_cfg,
    inactive_inside_ball_distance,
    require_ball_stationary,
    ball_stationary_speed_threshold,
  )
  if stop_after_plant_latch:
    gate = gate * (1.0 - _plant_latch_mask(env))
  return reward * gate


def behind_ball_inv_distance(
  env: ManagerBasedRlEnv,
  target_distance: float = 0.40,
  command_name: str = "goal",
  inactive_inside_ball_distance: float | None = None,
  stop_after_plant_latch: bool = False,
  progress: bool = False,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Dense pull toward the ball-attached waypoint.

  Default is ``1 / (1 + d)``. With ``progress=True``, pays signed closing
  speed so standing is zero and retreating is negative.
  """
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  ball_pos = ball.data.root_link_pos_w[:, :2]
  waypoint = behind_ball_waypoint_xy(env, ball_pos, target_distance, command_name)
  if progress:
    closing, dist = _planar_closing_speed(robot, waypoint)
    reward = closing
  else:
    dist = torch.linalg.norm(robot.data.root_link_pos_w[:, :2] - waypoint, dim=-1)
    reward = 1.0 / (1.0 + dist)
  if inactive_inside_ball_distance is not None:
    ball_dist = torch.linalg.norm(robot.data.root_link_pos_w[:, :2] - ball_pos, dim=-1)
    reward = reward * (ball_dist > float(inactive_inside_ball_distance)).float()
  if stop_after_plant_latch:
    reward = reward * (1.0 - _plant_latch_mask(env))
  env.extras["log"]["Metrics/behind_ball_distance"] = dist.mean()
  env.extras["log"]["Metrics/behind_ball_inv_distance"] = reward.mean()
  return reward


def body_face_ball(
  env: ManagerBasedRlEnv,
  sigma: float = 0.60,
  # Only shape facing while still approaching the plant (not loitering).
  min_pref_dist: float = 1.0,
  command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.9,
  setup_exit_dist: float = 1.0,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Reward facing the ball during far approach only.

  Zero when ``‖xy − P_ref‖ < min_pref_dist`` so facing-at-loiter cannot replace
  plant/align/kick (``P_ref`` is setup_xy).
  """
  from mjlab.tasks.kick.mdp.pref_pose import compute_reference_pose_xy

  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  pref, _phase = compute_reference_pose_xy(
    env,
    **_pref_pose_kwargs(
      command_name=command_name,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    ),
  )
  pref_dist = torch.linalg.norm(robot.data.root_link_pos_w[:, :2] - pref, dim=-1)
  rel_w = ball.data.root_link_pos_w - robot.data.root_link_pos_w
  rel_b = quat_apply_inverse(robot.data.root_link_quat_w, rel_w)
  bearing = torch.atan2(rel_b[:, 1], rel_b[:, 0])
  reward = torch.exp(-torch.square(bearing) / sigma**2)
  gate = (pref_dist >= float(min_pref_dist)).float()
  env.extras["log"]["Metrics/ball_bearing_abs"] = torch.abs(bearing).mean()
  return reward * gate


def loiter_stage_penalty(
  env: ManagerBasedRlEnv,
  activate_inside_ball_distance: float = 1.2,
  activate_inside_pref_dist: float = 1.0,
  ramp_tau_s: float = 1.0,
  max_scale: float = 4.0,
  command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.9,
  setup_exit_dist: float = 1.0,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Growing cost while near the ball/plant without having kicked.

  Stage clock for anti-farm: once ``‖robot−ball‖ < activate_inside_ball_distance``
  or ``‖xy−P_ref‖ < activate_inside_pref_dist``, cost ``(t/τ)²`` (cap
  ``max_scale``) until ``kick_detected``. Far approach is free.
  """
  from mjlab.tasks.kick.mdp.pref_pose import compute_reference_pose_xy

  state = ensure_ball_phase_updated(
    env,
    ball_cfg_name=ball_cfg.name,
    robot_cfg_name=robot_cfg.name,
    goal_command_name=command_name,
  )
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  pref, _phase = compute_reference_pose_xy(
    env,
    **_pref_pose_kwargs(
      command_name=command_name,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    ),
  )
  robot_xy = robot.data.root_link_pos_w[:, :2]
  ball_dist = torch.linalg.norm(robot_xy - ball.data.root_link_pos_w[:, :2], dim=-1)
  pref_dist = torch.linalg.norm(robot_xy - pref, dim=-1)
  in_stage = (
    (ball_dist < float(activate_inside_ball_distance))
    | (pref_dist < float(activate_inside_pref_dist))
  ) & (~state.kick_detected)
  timer = getattr(env, "_loiter_stage_timer", None)
  if timer is None or timer.shape[0] != env.num_envs:
    timer = torch.zeros(env.num_envs, device=env.device)
  timer = torch.where(
    in_stage,
    timer + env.step_dt,
    torch.zeros_like(timer),
  )
  env._loiter_stage_timer = timer
  scale = torch.clamp(
    torch.square(timer / max(float(ramp_tau_s), 1.0e-6)),
    max=float(max_scale),
  )
  cost = in_stage.float() * scale
  env.extras["log"]["Metrics/loiter_stage_active"] = in_stage.float().mean()
  env.extras["log"]["Metrics/loiter_stage_timer_s"] = timer.mean()
  return cost


def _plant_proximity_walk_scale(
  env: ManagerBasedRlEnv,
  *,
  full_dist: float = 0.6,
  far_dist: float = 2.0,
  far_scale: float = 0.15,
  restore_after_kick: bool = True,
  goal_command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.45,
  setup_exit_dist: float = 0.5,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Invert walk-farm incentive: full near plant, weak when far.

  ``scale = 1`` for ``pref_dist <= full_dist``, ``far_scale`` for
  ``pref_dist >= far_dist``, linear in between. After ``kick_detected``,
  optionally restores full scale so post-kick gait is not crushed.
  """
  from mjlab.tasks.kick.mdp.pref_pose import compute_reference_pose_xy

  robot: Entity = env.scene[robot_cfg.name]
  pref, _phase = compute_reference_pose_xy(
    env,
    **_pref_pose_kwargs(
      command_name=goal_command_name,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    ),
  )
  pref_dist = torch.linalg.norm(robot.data.root_link_pos_w[:, :2] - pref, dim=-1)
  denom = max(float(far_dist) - float(full_dist), 1.0e-6)
  t = ((pref_dist - float(full_dist)) / denom).clamp(0.0, 1.0)
  scale = (1.0 - t) + t * float(far_scale)
  if restore_after_kick:
    state = ensure_ball_phase_updated(
      env,
      ball_cfg_name=ball_cfg.name,
      robot_cfg_name=robot_cfg.name,
      goal_command_name=goal_command_name,
    )
    scale = torch.where(state.kick_detected, torch.ones_like(scale), scale)
  env.extras["log"]["Metrics/plant_walk_scale"] = scale.mean()
  env.extras["log"]["Metrics/pref_distance"] = pref_dist.mean()
  return scale


def _loiter_tracking_scale(
  env: ManagerBasedRlEnv,
  *,
  loiter_ball_distance: float,
  loiter_scale: float,
  robot_cfg: SceneEntityCfg,
  ball_cfg: SceneEntityCfg,
) -> torch.Tensor:
  """Deprecated keep-out nerf (pushes park outside the band). Prefer plant scale."""
  state = ensure_ball_phase_updated(
    env,
    ball_cfg_name=ball_cfg.name,
    robot_cfg_name=robot_cfg.name,
  )
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  dist = torch.linalg.norm(
    robot.data.root_link_pos_w[:, :2] - ball.data.root_link_pos_w[:, :2],
    dim=-1,
  )
  near = (dist < float(loiter_ball_distance)) & (~state.kick_detected)
  return torch.where(
    near,
    torch.full_like(dist, float(loiter_scale)),
    torch.ones_like(dist),
  )


def track_lin_vel_axis_for_kick(
  env: ManagerBasedRlEnv,
  axis: int,
  command_name: str = "twist",
  tracking_sigma: float = 0.25,
  filter_weight: float = 0.1,
  speed_ref: float = 0.0,
  high_speed_threshold: float = 0.0,
  high_speed_sigma: float = 0.0,
  # Invert: full near plant, weak far (not a keep-out band).
  plant_full_dist: float = 0.6,
  plant_far_dist: float = 2.0,
  plant_far_scale: float = 0.15,
  restore_tracking_after_kick: bool = True,
  # Paper robot→ball command (student): sync twist before measuring error.
  align_robot_ball: bool = True,
  cruise_speed: float = 0.7,
  min_speed: float = 0.25,
  slow_distance: float = 1.0,
  plant_distance: float = 0.20,
  turn_speed: float = 1.0,
  heading_deadzone: float = 0.05,
  use_sampled_magnitudes: bool = True,
  goal_command_name: str = "goal",
  orbit_to_approach: bool = False,
  approach_standoff: float = 0.40,
  ready_waypoint_distance: float = 0.20,
  orbit_to_plant_box: bool = False,
  plant_root_behind: float = 0.22,
  plant_root_lateral: float = 0.10,
  plant_feet_offset_x: float = -0.02,
  plant_feet_offset_y: float = 0.12,
  creep_through_plant: bool = False,
  creep_speed: float = 0.25,
  face_path_fov_clip: bool = False,
  fov_half_angle: float = 0.69,
  yaw_gain: float = 2.0,
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.45,
  setup_exit_dist: float = 0.5,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  # Legacy kwargs ignored if present.
  loiter_ball_distance: float | None = None,
  loiter_scale: float | None = None,
  inactive_inside_ball_distance: float | None = None,
  asset_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  robot_cfg: SceneEntityCfg | None = None,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Lin-vel tracking vs robot→ball / orbit twist targets × plant-proximity scale."""
  del loiter_ball_distance, loiter_scale
  from mjlab.tasks.kick.mdp.events import ensure_robot_ball_twist_command
  from mjlab.tasks.velocity import mdp as velocity_mdp

  robot = robot_cfg if robot_cfg is not None else asset_cfg
  if align_robot_ball:
    ensure_robot_ball_twist_command(
      env,
      None,
      command_name=command_name,
      cruise_speed=cruise_speed,
      min_speed=min_speed,
      slow_distance=slow_distance,
      plant_distance=plant_distance,
      turn_speed=turn_speed,
      heading_deadzone=heading_deadzone,
      use_sampled_magnitudes=use_sampled_magnitudes,
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
      robot_cfg=robot,
      ball_cfg=ball_cfg,
    )
  raw = velocity_mdp.track_lin_vel_axis(
    env,
    axis=axis,
    command_name=command_name,
    tracking_sigma=tracking_sigma,
    filter_weight=filter_weight,
    speed_ref=speed_ref,
    high_speed_threshold=high_speed_threshold,
    high_speed_sigma=high_speed_sigma,
    asset_cfg=robot,
  )
  scale = _plant_proximity_walk_scale(
    env,
    full_dist=plant_full_dist,
    far_dist=plant_far_dist,
    far_scale=plant_far_scale,
    restore_after_kick=restore_tracking_after_kick,
    goal_command_name=goal_command_name,
    arc_radius=arc_radius,
    setup_enter_dist=setup_enter_dist,
    setup_exit_dist=setup_exit_dist,
    setup_behind=setup_behind,
    setup_lateral=setup_lateral,
    prefer_right_foot=prefer_right_foot,
    bearing_thresh=bearing_thresh,
    lateral_thresh=lateral_thresh,
    setup_blend_end=setup_blend_end,
    strike_blend_thresh=strike_blend_thresh,
    setup_pos_thresh=setup_pos_thresh,
    dynamic_kick_foot=dynamic_kick_foot,
    robot_cfg=robot,
    ball_cfg=ball_cfg,
  )
  reward = raw * scale
  if inactive_inside_ball_distance is not None:
    ball_dist = _robot_ball_planar_distance(env, robot, ball_cfg)
    reward = reward * (ball_dist > float(inactive_inside_ball_distance)).float()
  return reward


def track_ang_vel_z_for_kick(
  env: ManagerBasedRlEnv,
  command_name: str = "twist",
  tracking_sigma: float = 0.25,
  filter_weight: float = 0.1,
  speed_ref: float = 0.0,
  high_speed_threshold: float = 0.0,
  high_speed_sigma: float = 0.0,
  plant_full_dist: float = 0.6,
  plant_far_dist: float = 2.0,
  plant_far_scale: float = 0.15,
  restore_tracking_after_kick: bool = True,
  align_robot_ball: bool = True,
  cruise_speed: float = 0.7,
  min_speed: float = 0.25,
  slow_distance: float = 1.0,
  plant_distance: float = 0.20,
  turn_speed: float = 1.0,
  heading_deadzone: float = 0.05,
  use_sampled_magnitudes: bool = True,
  goal_command_name: str = "goal",
  orbit_to_approach: bool = False,
  approach_standoff: float = 0.40,
  ready_waypoint_distance: float = 0.20,
  orbit_to_plant_box: bool = False,
  plant_root_behind: float = 0.22,
  plant_root_lateral: float = 0.10,
  plant_feet_offset_x: float = -0.02,
  plant_feet_offset_y: float = 0.12,
  creep_through_plant: bool = False,
  creep_speed: float = 0.25,
  face_path_fov_clip: bool = False,
  fov_half_angle: float = 0.69,
  yaw_gain: float = 2.0,
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.45,
  setup_exit_dist: float = 0.5,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  loiter_ball_distance: float | None = None,
  loiter_scale: float | None = None,
  inactive_inside_ball_distance: float | None = None,
  asset_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  robot_cfg: SceneEntityCfg | None = None,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Yaw tracking vs robot→ball / orbit twist targets × plant-proximity scale."""
  del loiter_ball_distance, loiter_scale
  from mjlab.tasks.kick.mdp.events import ensure_robot_ball_twist_command
  from mjlab.tasks.velocity import mdp as velocity_mdp

  robot = robot_cfg if robot_cfg is not None else asset_cfg
  if align_robot_ball:
    ensure_robot_ball_twist_command(
      env,
      None,
      command_name=command_name,
      cruise_speed=cruise_speed,
      min_speed=min_speed,
      slow_distance=slow_distance,
      plant_distance=plant_distance,
      turn_speed=turn_speed,
      heading_deadzone=heading_deadzone,
      use_sampled_magnitudes=use_sampled_magnitudes,
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
      robot_cfg=robot,
      ball_cfg=ball_cfg,
    )
  raw = velocity_mdp.track_ang_vel_z(
    env,
    command_name=command_name,
    tracking_sigma=tracking_sigma,
    filter_weight=filter_weight,
    speed_ref=speed_ref,
    high_speed_threshold=high_speed_threshold,
    high_speed_sigma=high_speed_sigma,
    asset_cfg=robot,
  )
  scale = _plant_proximity_walk_scale(
    env,
    full_dist=plant_full_dist,
    far_dist=plant_far_dist,
    far_scale=plant_far_scale,
    restore_after_kick=restore_tracking_after_kick,
    goal_command_name=goal_command_name,
    arc_radius=arc_radius,
    setup_enter_dist=setup_enter_dist,
    setup_exit_dist=setup_exit_dist,
    setup_behind=setup_behind,
    setup_lateral=setup_lateral,
    prefer_right_foot=prefer_right_foot,
    bearing_thresh=bearing_thresh,
    lateral_thresh=lateral_thresh,
    setup_blend_end=setup_blend_end,
    strike_blend_thresh=strike_blend_thresh,
    setup_pos_thresh=setup_pos_thresh,
    dynamic_kick_foot=dynamic_kick_foot,
    robot_cfg=robot,
    ball_cfg=ball_cfg,
  )
  reward = raw * scale
  if inactive_inside_ball_distance is not None:
    ball_dist = _robot_ball_planar_distance(env, robot, ball_cfg)
    reward = reward * (ball_dist > float(inactive_inside_ball_distance)).float()
  return reward


def kick_heading_misalignment(
  env: ManagerBasedRlEnv,
  free_angle: float = 0.25,
  command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.9,
  setup_exit_dist: float = 1.0,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Penalize yaw off the ball→goal axis during Setup/Strike (kick window).

  Returns hinge excess ``max(0, ∠(body_fwd, goal_dir) − free_angle)`` so small
  heading error inside ``free_angle`` is free; larger misalignment is constrained.
  Inactive during Arc approach.
  """
  from mjlab.tasks.kick.mdp.geometry import ball_to_goal_direction_xy
  from mjlab.tasks.kick.mdp.pref_pose import PHASE_SETUP, compute_reference_pose_xy

  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  _pref, phase = compute_reference_pose_xy(
    env,
    **_pref_pose_kwargs(
      command_name=command_name,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    ),
  )
  goal_dir = ball_to_goal_direction_xy(
    env, ball.data.root_link_pos_w[:, :2], command_name
  )
  qw, qx, qy, qz = (
    robot.data.root_link_quat_w[:, 0],
    robot.data.root_link_quat_w[:, 1],
    robot.data.root_link_quat_w[:, 2],
    robot.data.root_link_quat_w[:, 3],
  )
  body_fwd = torch.stack(
    (1.0 - 2.0 * (qy * qy + qz * qz), 2.0 * (qx * qy + qw * qz)),
    dim=-1,
  )
  body_fwd = body_fwd / torch.linalg.norm(body_fwd, dim=-1, keepdim=True).clamp(
    min=1.0e-6
  )
  cos_align = (body_fwd * goal_dir).sum(dim=-1).clamp(-1.0, 1.0)
  angle = torch.acos(cos_align)
  excess = (angle - float(free_angle)).clamp(min=0.0)
  gate = (phase >= PHASE_SETUP).float()
  penalty = gate * excess
  env.extras["log"]["Metrics/kick_heading_err"] = (
    gate * angle
  ).sum() / gate.sum().clamp(min=1.0)
  return penalty


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
  inactive_inside_ball_distance: float | None = None,
  require_ball_stationary: bool = False,
  ball_stationary_speed_threshold: float = 0.1,
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
  waypoint_error_sq = torch.sum(torch.square(robot_pos_w[:, :2] - waypoint), dim=-1)

  reward = _compute_kick_ready_score(
    env,
    target_distance=target_distance,
    command_name=command_name,
    robot_cfg=robot_cfg,
    ball_cfg=ball_cfg,
    waypoint_std=waypoint_std,
    distance_std=distance_std,
    lateral_half_width=lateral_half_width,
    bearing_std=bearing_std,
    target_alignment_std=target_alignment_std,
    camera_soft_limit=camera_soft_limit,
    camera_sigma=camera_sigma,
  )
  env.extras["log"]["Metrics/kick_ready_reward"] = reward.mean()
  env.extras["log"]["Metrics/kick_ready_fraction"] = (reward > 0.5).float().mean()
  env.extras["log"]["Metrics/kick_ready_waypoint_error"] = torch.sqrt(
    waypoint_error_sq
  ).mean()
  gate = _approach_reward_gate(
    env,
    robot_cfg,
    ball_cfg,
    inactive_inside_ball_distance,
    require_ball_stationary,
    ball_stationary_speed_threshold,
  )
  return reward * gate


def waypoint_approach_velocity(
  env: ManagerBasedRlEnv,
  target_distance: float = 0.35,
  command_name: str = "goal",
  activate_ball_distance: float | None = 0.55,
  activate_waypoint_distance: float | None = None,
  inactive_inside_ball_distance: float | None = None,
  velocity_eps: float = 0.1,
  use_cosine: bool = False,
  stop_after_plant_latch: bool = False,
  facing_std: float | None = None,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Reward planar velocity toward the ball-attached waypoint.

  By default active only while outside ``activate_ball_distance``. For orbit
  approach, set ``activate_waypoint_distance`` (and ``activate_ball_distance=None``)
  so the gate matches the twist plant radius. With ``use_cosine=True`` returns
  ``max(0, cos(v, to_wp))`` in ``[0, 1]`` (same scale as ``agent_approach_ball``).
  ``inactive_inside_ball_distance`` zeros the term in the kick zone so approach
  payday cannot compete with contact / strike. ``facing_std`` multiplies by
  body-vs-goal yaw so closing while turned away does not pay.
  """
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]

  robot_pos = robot.data.root_link_pos_w
  ball_pos = ball.data.root_link_pos_w[:, :2]
  waypoint = behind_ball_waypoint_xy(env, ball_pos, target_distance, command_name)

  to_waypoint = waypoint - robot_pos[:, :2]
  wp_dist = torch.linalg.norm(to_waypoint, dim=-1)
  dir_w = to_waypoint / wp_dist.unsqueeze(-1).clamp(min=1.0e-6)
  vel_w = robot.data.root_link_lin_vel_w[:, :2]
  speed = torch.linalg.norm(vel_w, dim=-1)

  if use_cosine:
    progress = (torch.sum(vel_w * dir_w, dim=-1) / speed.clamp(min=1.0e-6)).clamp(
      min=0.0
    )
    progress = torch.where(
      speed > float(velocity_eps), progress, torch.zeros_like(progress)
    )
  else:
    progress = torch.sum(vel_w * dir_w, dim=-1).clamp(min=0.0)
  if facing_std is not None:
    progress = progress * _body_face_goal_yaw_score(
      env, command_name, robot_cfg, ball_cfg, facing_std
    )

  ball_distance = torch.linalg.norm(ball_pos - robot_pos[:, :2], dim=-1)
  if activate_waypoint_distance is not None:
    active = (wp_dist > float(activate_waypoint_distance)).float()
  elif activate_ball_distance is not None:
    active = (ball_distance > float(activate_ball_distance)).float()
  else:
    active = torch.ones_like(progress)
  if inactive_inside_ball_distance is not None:
    active = active * (ball_distance > float(inactive_inside_ball_distance)).float()
  if stop_after_plant_latch:
    active = active * (1.0 - _plant_latch_mask(env))

  env.extras["log"]["Metrics/waypoint_approach_velocity"] = (active * progress).mean()
  env.extras["log"]["Metrics/behind_ball_distance"] = wp_dist.mean()
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
  env.extras["log"]["Metrics/waypoint_retreat_penalty"] = (active * retreat).mean()
  return active * retreat


def trunk_height_floor(
  env: ManagerBasedRlEnv,
  minimum_height: float = 0.53,
  asset_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> torch.Tensor:
  """Penalize trunk/root height only when below ``minimum_height``.

  One-sided guard against crouch-under-push without punishing normal gait
  bounce above the floor.
  """
  robot: Entity = env.scene[asset_cfg.name]
  if asset_cfg.body_ids:
    height = robot.data.body_link_pos_w[:, asset_cfg.body_ids, 2].squeeze(1)
  else:
    height = robot.data.root_link_pos_w[:, 2]
  violation = torch.clamp(minimum_height - height, min=0.0)
  env.extras["log"]["Metrics/trunk_height_floor_violation"] = violation.mean()
  return torch.square(violation)


def ball_velocity_toward_goal(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  max_reward: float = 10.0,
  min_reward_speed: float = 0.0,
  decay_time_s: float = 0.1,
  use_decay: bool = True,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  require_plant_latch: bool = False,
  quality_gated: bool = False,
  gate_foot_proximity: bool = True,
  gate_support_stability: bool = True,
  foot_proximity_sigma: float = 0.12,
  body_alignment_sigma: float = 0.25,
  support_speed_sigma: float = 0.25,
  upright_sigma: float = 0.40,
  feet_cfg: SceneEntityCfg | None = None,
  **_unused,
) -> torch.Tensor:
  """Projected ball speed, optionally gated by a correct and stable strike.

  ``r = clamp( (v · û_goal)_+ [* exp(-t_moving / τ)], 0, max_reward )``.
  With ``use_decay=False`` this is ``clip(v·d̂, 0, max_reward)`` — strength
  matters, unlike scale-free ``ball_approach_target`` (direction aux).

  With ``quality_gated=True``, body-to-goal yaw alignment and upright posture
  gate the outcome. Selected-foot proximity and support stability can be
  enabled as additional gates, but are disabled for strike discovery.
  """
  del _unused
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
  )

  ball: Entity = env.scene[ball_cfg.name]
  ball_vel = ball.data.root_link_lin_vel_w[:, :2]

  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  goal_pos = command[:, :2] + env.scene.env_origins[:, :2]
  ball_pos = ball.data.root_link_pos_w[:, :2]
  to_goal = goal_pos - ball_pos
  goal_dir = to_goal / torch.linalg.norm(to_goal, dim=-1, keepdim=True).clamp(
    min=1.0e-6
  )

  vel_toward_goal = torch.sum(ball_vel * goal_dir, dim=-1)
  strength = torch.clamp(
    vel_toward_goal - float(min_reward_speed),
    min=0.0,
    max=max(float(max_reward) - float(min_reward_speed), 0.0),
  )
  if use_decay:
    decay = torch.exp(-state.time_since_moving_s / max(float(decay_time_s), 1.0e-6))
    reward = strength * decay
  else:
    reward = strength
  if require_plant_latch:
    reward = reward * _plant_latch_mask(env)

  if quality_gated:
    robot: Entity = env.scene[robot_cfg.name]
    foot_ids = _resolve_foot_ids(robot, feet_cfg)
    feet_pos = robot.data.body_link_pos_w[:, foot_ids, :]
    feet_vel = robot.data.body_link_lin_vel_w[:, foot_ids, :]
    kicking_idx, support_idx = _kick_stance_foot_indices(env, robot, ball)
    kicking_pos = _gather_foot_tensor(feet_pos, kicking_idx)
    support_vel = _gather_foot_tensor(feet_vel, support_idx)

    foot_dist = torch.linalg.norm(ball.data.root_link_pos_w - kicking_pos, dim=-1)
    foot_proximity = torch.exp(
      -torch.square(foot_dist) / max(float(foot_proximity_sigma), 1.0e-6) ** 2
    )

    body_forward = quat_apply(
      robot.data.root_link_quat_w,
      torch.tensor([1.0, 0.0, 0.0], device=env.device, dtype=ball_pos.dtype).expand(
        env.num_envs, 3
      ),
    )[:, :2]
    body_forward = body_forward / torch.linalg.norm(
      body_forward, dim=-1, keepdim=True
    ).clamp(min=1.0e-6)
    yaw_error = torch.atan2(
      body_forward[:, 0] * goal_dir[:, 1] - body_forward[:, 1] * goal_dir[:, 0],
      torch.sum(body_forward * goal_dir, dim=-1).clamp(-1.0, 1.0),
    )
    body_alignment = torch.exp(
      -torch.square(yaw_error) / max(float(body_alignment_sigma), 1.0e-6) ** 2
    )

    support_speed = torch.linalg.norm(support_vel[:, :2], dim=-1)
    support_stability = torch.exp(
      -torch.square(support_speed) / max(float(support_speed_sigma), 1.0e-6) ** 2
    )
    projected_gravity_b = quat_apply_inverse(
      robot.data.root_link_quat_w, robot.data.gravity_vec_w
    )
    tilt = torch.linalg.norm(projected_gravity_b[:, :2], dim=-1)
    upright = torch.exp(-torch.square(tilt) / max(float(upright_sigma), 1.0e-6) ** 2)
    quality = body_alignment * upright
    if gate_foot_proximity:
      quality = quality * foot_proximity
    if gate_support_stability:
      quality = quality * support_stability
    reward = reward * quality

    env.extras["log"]["Metrics/kick_foot_proximity"] = foot_proximity.mean()
    env.extras["log"]["Metrics/kick_body_alignment"] = body_alignment.mean()
    env.extras["log"]["Metrics/kick_support_stability"] = support_stability.mean()
    env.extras["log"]["Metrics/kick_upright"] = upright.mean()
    env.extras["log"]["Metrics/kick_quality_gate"] = quality.mean()
  env.extras["log"]["Metrics/ball_vel_toward_goal"] = reward.mean()
  env.extras["log"]["Metrics/ball_vel_toward_goal_raw"] = vel_toward_goal.clamp(
    min=0.0
  ).mean()
  return reward


def kick_direction_accuracy_window(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  window_s: float = 0.30,
  angle_sigma: float = 0.25,
  min_ball_speed: float = 0.1,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> torch.Tensor:
  """Reward kick direction briefly after a detected foot-ball strike."""
  state = ensure_ball_phase_updated(
    env,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
    robot_cfg_name=robot_cfg.name,
  )
  assert state.kick_detected is not None
  assert state.time_since_kick_s is not None

  ball: Entity = env.scene[ball_cfg.name]
  ball_vel = ball.data.root_link_lin_vel_w[:, :2]
  ball_speed = torch.linalg.norm(ball_vel, dim=-1)
  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  goal_pos = command[:, :2] + env.scene.env_origins[:, :2]
  to_goal = goal_pos - ball.data.root_link_pos_w[:, :2]
  goal_dir = to_goal / torch.linalg.norm(to_goal, dim=-1, keepdim=True).clamp(
    min=1.0e-6
  )
  ball_dir = ball_vel / ball_speed.unsqueeze(-1).clamp(min=1.0e-6)
  cosine = torch.sum(ball_dir * goal_dir, dim=-1).clamp(-1.0, 1.0)
  angular_error = torch.acos(cosine)
  score = torch.exp(-torch.square(angular_error) / max(float(angle_sigma), 1.0e-6) ** 2)
  active = (
    state.kick_detected
    & (state.time_since_kick_s <= float(window_s))
    & (ball_speed >= float(min_ball_speed))
  )
  reward = score * active.float()
  env.extras["log"]["Metrics/kick_direction_error"] = angular_error.mean()
  env.extras["log"]["Metrics/kick_direction_window"] = reward.mean()
  return reward


def kick_speed_match_window(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  window_s: float = 0.30,
  relative_sigma: float = 0.35,
  launch_angle: float = math.pi / 4.0,
  gravity: float = 9.81,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> torch.Tensor:
  """Match ball speed to the ballistic speed for the commanded landing range.

  Uses ``R = v² sin(2θ) / g`` and a relative-error Gaussian, allowing separate
  loose and tight reward terms without changing scale across target ranges.
  """
  state = ensure_ball_phase_updated(
    env,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
    robot_cfg_name=robot_cfg.name,
  )
  assert state.kick_detected is not None
  assert state.time_since_kick_s is not None

  ball: Entity = env.scene[ball_cfg.name]
  ball_speed = torch.linalg.norm(ball.data.root_link_lin_vel_w, dim=-1)
  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  goal_pos = command[:, :2] + env.scene.env_origins[:, :2]
  target_range = torch.linalg.norm(goal_pos - ball.data.root_link_pos_w[:, :2], dim=-1)
  expected_speed = expected_ballistic_speed(target_range, launch_angle, gravity)
  relative_error = (ball_speed - expected_speed) / expected_speed.clamp(min=1.0e-6)
  score = torch.exp(
    -torch.square(relative_error) / max(float(relative_sigma), 1.0e-6) ** 2
  )
  active = state.kick_detected & (state.time_since_kick_s <= float(window_s))
  reward = score * active.float()
  env.extras["log"]["Metrics/kick_expected_ball_speed"] = expected_speed.mean()
  env.extras["log"]["Metrics/kick_ball_speed"] = ball_speed.mean()
  env.extras["log"][f"Metrics/kick_speed_match_{relative_sigma:g}"] = reward.mean()
  return reward


def ball_approach_target(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  velocity_eps: float = 0.1,
  require_plant_latch: bool = False,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Dense cosine of ball velocity vs ball→target (paper ``r_b-approach-t``).

  ``max(0, cos(v_ball, d_target→ball))`` when ``‖v_ball‖ > ε``, else 0.
  Scale-free alignment (unlike ``ball_velocity_toward_goal`` projected speed).
  """
  ball: Entity = env.scene[ball_cfg.name]
  ball_pos = ball.data.root_link_pos_w[:, :2]
  ball_vel = ball.data.root_link_lin_vel_w[:, :2]

  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  goal_pos = command[:, :2] + env.scene.env_origins[:, :2]
  d_target_ball = goal_pos - ball_pos

  ball_speed = torch.linalg.norm(ball_vel, dim=-1)
  d_norm = torch.linalg.norm(d_target_ball, dim=-1).clamp(min=1.0e-6)
  cos_clip = (
    torch.sum(ball_vel * d_target_ball, dim=-1)
    / (ball_speed.clamp(min=1.0e-6) * d_norm)
  ).clamp(min=0.0)
  reward = torch.where(ball_speed > velocity_eps, cos_clip, torch.zeros_like(cos_clip))
  if require_plant_latch:
    reward = reward * _plant_latch_mask(env)

  env.extras["log"]["Metrics/ball_approach_target"] = reward.mean()
  return reward


def target_reached(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  contact_window_s: float = 2.0,
  velocity_eps: float = 0.1,
  std: float = 1.0,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Sparse settle reward after kick when ball is nearly stagnant (``r_target-reached``).

  Active when ``time_since_kick_s > T_window`` and ``‖v_ball‖ < ε``:
  ``exp(−‖d_target,ball‖ / σ²)``. Zero otherwise.
  """
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
  )

  ball: Entity = env.scene[ball_cfg.name]
  ball_pos = ball.data.root_link_pos_w[:, :2]
  ball_vel = ball.data.root_link_lin_vel_w[:, :2]
  ball_speed = torch.linalg.norm(ball_vel, dim=-1)

  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  goal_pos = command[:, :2] + env.scene.env_origins[:, :2]
  dist = torch.linalg.norm(goal_pos - ball_pos, dim=-1)

  active = (state.time_since_kick_s > contact_window_s) & (ball_speed < velocity_eps)
  reward = torch.where(
    active,
    torch.exp(-dist / (std**2)),
    torch.zeros_like(dist),
  )
  env.extras["log"]["Metrics/target_reached"] = reward.mean()
  env.extras["log"]["Metrics/ball_goal_distance"] = dist.mean()
  return reward


def kicking_foot_approach_ball_stationary(
  env: ManagerBasedRlEnv,
  approach_proximity_sigma: float = 0.1,
  max_reward: float = 2.0,
  activate_inside_ball_distance: float | None = None,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  feet_cfg: SceneEntityCfg | None = None,
) -> torch.Tensor:
  """Reward the nearest foot approaching a stationary ball (HTWK-style).

  Foot selection is implicit: whichever foot is closer to the ball receives
  the proximity shaping.  Active only while the ball is nearly at rest.
  """
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
  )

  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  if feet_cfg is not None and feet_cfg.body_ids != slice(None):
    foot_ids = feet_cfg.body_ids
  else:
    left_ids, _ = robot.find_bodies("left_foot_link")
    right_ids, _ = robot.find_bodies("right_foot_link")
    foot_ids = [left_ids[0], right_ids[0]]
  feet_pos = robot.data.body_link_pos_w[:, foot_ids, :]
  ball_pos = ball.data.root_link_pos_w.unsqueeze(1)
  foot_dists = torch.linalg.norm(feet_pos - ball_pos, dim=-1)
  nearest_dist = torch.min(foot_dists, dim=-1).values

  stationary = (
    torch.linalg.norm(ball.data.root_link_lin_vel_w[:, :2], dim=-1)
    <= ball_stationary_speed_threshold
  ).float()
  proximity = torch.exp(-nearest_dist / approach_proximity_sigma)
  reward = (
    torch.clamp(proximity, min=0.0, max=max_reward)
    * stationary
    * (~state.kick_detected).float()
  )
  if activate_inside_ball_distance is not None:
    reward = reward * _kick_zone_mask(
      env, robot_cfg, ball_cfg, activate_inside_ball_distance
    )
  env.extras["log"]["Metrics/kicking_foot_approach"] = reward.mean()
  return reward


def kicking_foot_swing_toward_goal(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  target_distance: float = 0.35,
  activate_inside_ball_distance: float = 0.55,
  require_kick_ready: bool = True,
  kick_ready_threshold: float = 0.45,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  feet_cfg: SceneEntityCfg | None = None,
) -> torch.Tensor:
  """Reward the designated kicking foot swinging toward the goal before contact."""
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    kick_phase_robot_ball_distance=activate_inside_ball_distance,
    robot_cfg_name=robot_cfg.name,
    ball_cfg_name=ball_cfg.name,
  )

  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  foot_ids = _resolve_foot_ids(robot, feet_cfg)
  feet_vel = robot.data.body_link_lin_vel_w[:, foot_ids, :]
  kicking_idx, _ = _kick_stance_foot_indices(env, robot, ball)
  kicking_vel = _gather_foot_tensor(feet_vel, kicking_idx)

  ball_pos = ball.data.root_link_pos_w[:, :2]
  goal_dir = ball_to_goal_direction_xy(env, ball_pos, command_name)
  goal_dir_3d = torch.cat([goal_dir, torch.zeros_like(goal_dir[:, :1])], dim=-1)
  progress = torch.sum(kicking_vel * goal_dir_3d, dim=-1).clamp(min=0.0)

  active = _kick_contact_activation_mask(
    env,
    state,
    robot_cfg,
    ball_cfg,
    ball_stationary_speed_threshold,
    require_kick_ready,
    kick_ready_threshold,
    command_name,
    target_distance,
    activate_inside_ball_distance,
  )
  reward = active * progress
  env.extras["log"]["Metrics/kicking_foot_swing_speed"] = (active * progress).mean()
  return reward


def kicking_foot_strike_ball(
  env: ManagerBasedRlEnv,
  activate_inside_ball_distance: float = 0.55,
  target_distance: float = 0.35,
  command_name: str = "goal",
  require_kick_ready: bool = True,
  kick_ready_threshold: float = 0.45,
  proximity_sigma: float = 0.08,
  proximity_gated_speed: bool = False,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  require_plant_latch: bool = False,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  feet_cfg: SceneEntityCfg | None = None,
) -> torch.Tensor:
  """Reward the kicking foot closing on and striking the ball."""
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    kick_phase_robot_ball_distance=activate_inside_ball_distance,
    robot_cfg_name=robot_cfg.name,
    ball_cfg_name=ball_cfg.name,
  )

  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  foot_ids = _resolve_foot_ids(robot, feet_cfg)
  feet_pos = robot.data.body_link_pos_w[:, foot_ids, :]
  feet_vel = robot.data.body_link_lin_vel_w[:, foot_ids, :]
  kicking_idx, _ = _kick_stance_foot_indices(env, robot, ball)
  kicking_pos = _gather_foot_tensor(feet_pos, kicking_idx)
  kicking_vel = _gather_foot_tensor(feet_vel, kicking_idx)
  ball_pos = ball.data.root_link_pos_w

  to_ball = ball_pos - kicking_pos
  to_ball_dir = to_ball / torch.linalg.norm(to_ball, dim=-1, keepdim=True).clamp(
    min=1.0e-6
  )
  foot_dist = torch.linalg.norm(to_ball, dim=-1)
  proximity = torch.exp(-foot_dist / proximity_sigma)
  strike_speed = torch.sum(kicking_vel * to_ball_dir, dim=-1).clamp(min=0.0)

  active = _kick_contact_activation_mask(
    env,
    state,
    robot_cfg,
    ball_cfg,
    ball_stationary_speed_threshold,
    require_kick_ready,
    kick_ready_threshold,
    command_name,
    target_distance,
    activate_inside_ball_distance,
  )
  if proximity_gated_speed:
    reward = active * proximity * strike_speed
  else:
    reward = active * (2.0 * proximity + strike_speed)
  if require_plant_latch:
    reward = reward * _plant_latch_mask(env)
  env.extras["log"]["Metrics/kicking_foot_ball_dist"] = (active * foot_dist).mean()
  env.extras["log"]["Metrics/kicking_foot_strike_speed"] = (
    active * strike_speed
  ).mean()
  return reward


def support_foot_clear_of_ball(
  env: ManagerBasedRlEnv,
  activate_inside_ball_distance: float = 0.55,
  target_distance: float = 0.35,
  command_name: str = "goal",
  require_kick_ready: bool = True,
  kick_ready_threshold: float = 0.45,
  min_clearance: float = 0.20,
  sigma: float = 0.06,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  feet_cfg: SceneEntityCfg | None = None,
) -> torch.Tensor:
  """Reward the support foot staying clear of the ball before the kick."""
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
  )
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  foot_ids = _resolve_foot_ids(robot, feet_cfg)
  feet_pos = robot.data.body_link_pos_w[:, foot_ids, :]
  _, support_idx = _kick_stance_foot_indices(env, robot, ball)
  support_pos = _gather_foot_tensor(feet_pos, support_idx)
  ball_pos = ball.data.root_link_pos_w
  support_dist = torch.linalg.norm(support_pos - ball_pos, dim=-1)
  clearance = (support_dist - min_clearance).clamp(min=0.0)
  reward = torch.tanh(clearance / sigma)

  active = _kick_contact_activation_mask(
    env,
    state,
    robot_cfg,
    ball_cfg,
    ball_stationary_speed_threshold,
    require_kick_ready,
    kick_ready_threshold,
    command_name,
    target_distance,
    activate_inside_ball_distance,
  )
  env.extras["log"]["Metrics/support_foot_clearance"] = (active * support_dist).mean()
  return active * reward


def support_foot_planted(
  env: ManagerBasedRlEnv,
  activate_inside_ball_distance: float = 0.55,
  target_distance: float = 0.35,
  command_name: str = "goal",
  require_kick_ready: bool = True,
  kick_ready_threshold: float = 0.45,
  require_plant_latch: bool = False,
  speed_sigma: float = 0.25,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  feet_cfg: SceneEntityCfg | None = None,
) -> torch.Tensor:
  """Reward a planted support foot while the kicking leg swings."""
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
  )
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  foot_ids = _resolve_foot_ids(robot, feet_cfg)
  feet_vel = robot.data.body_link_lin_vel_w[:, foot_ids, :]
  _, support_idx = _kick_stance_foot_indices(env, robot, ball)
  support_vel = _gather_foot_tensor(feet_vel, support_idx)
  support_speed = torch.linalg.norm(support_vel[:, :2], dim=-1)
  reward = torch.exp(-torch.square(support_speed) / speed_sigma**2)

  active = _kick_contact_activation_mask(
    env,
    state,
    robot_cfg,
    ball_cfg,
    ball_stationary_speed_threshold,
    require_kick_ready,
    kick_ready_threshold,
    command_name,
    target_distance,
    activate_inside_ball_distance,
  )
  if require_plant_latch:
    active = active * _plant_latch_mask(env)
  env.extras["log"]["Metrics/support_foot_speed"] = (active * support_speed).mean()
  return active * reward


def both_feet_near_ball_penalty(
  env: ManagerBasedRlEnv,
  touch_distance: float = 0.20,
  activate_inside_ball_distance: float = 0.90,
  target_distance: float = 0.35,
  command_name: str = "goal",
  require_kick_ready: bool = False,
  kick_ready_threshold: float = 0.45,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  require_ball_stationary: bool = False,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  feet_cfg: SceneEntityCfg | None = None,
) -> torch.Tensor:
  """Penalize both feet crowding the ball instead of a single-leg kick."""
  del target_distance, command_name, kick_ready_threshold  # unused when not kick-ready
  ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
  )
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  foot_ids = _resolve_foot_ids(robot, feet_cfg)
  feet_pos = robot.data.body_link_pos_w[:, foot_ids, :]
  ball_pos = ball.data.root_link_pos_w.unsqueeze(1)
  foot_dists = torch.linalg.norm(feet_pos - ball_pos, dim=-1)
  both_near = torch.all(foot_dists < touch_distance, dim=-1).float()

  if require_kick_ready:
    active = _kick_ready_activation_mask(
      env,
      robot_cfg,
      ball_cfg,
      "goal",
      0.35,
      0.45,
    )
  else:
    active = _kick_zone_mask(env, robot_cfg, ball_cfg, activate_inside_ball_distance)
  if require_ball_stationary:
    active = active * _ball_stationary_mask(
      env, ball_cfg, ball_stationary_speed_threshold
    )
  env.extras["log"]["Metrics/both_feet_near_ball"] = (active * both_near).mean()
  return active * both_near


def stance_foot_near_ball_penalty(
  env: ManagerBasedRlEnv,
  min_clearance: float = 0.22,
  prefer_right_foot: bool = True,
  command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.9,
  setup_exit_dist: float = 1.0,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Penalize the non-kicking (stance) foot entering the ball during Setup/Strike.

  Uses the latched swing foot from ``pref_pose`` so straddling / ball-between-legs
  is punished while the swing foot may still approach for the kick.
  """
  from mjlab.tasks.kick.mdp.pref_pose import (
    PHASE_SETUP,
    compute_reference_pose_xy,
    get_latched_kicking_foot,
  )

  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  _pref, phase = compute_reference_pose_xy(
    env,
    **_pref_pose_kwargs(
      command_name=command_name,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    ),
  )
  kicking = get_latched_kicking_foot(env, prefer_right_foot)
  left_ids, _ = robot.find_bodies("left_foot_link")
  right_ids, _ = robot.find_bodies("right_foot_link")
  left_xy = robot.data.body_link_pos_w[:, left_ids[0], :2]
  right_xy = robot.data.body_link_pos_w[:, right_ids[0], :2]
  stance_xy = torch.where((kicking == 0).unsqueeze(-1), right_xy, left_xy)
  ball_xy = ball.data.root_link_pos_w[:, :2]
  stance_dist = torch.linalg.norm(stance_xy - ball_xy, dim=-1)
  penetration = (float(min_clearance) - stance_dist).clamp(min=0.0)
  gate = (phase >= PHASE_SETUP).float()
  penalty = gate * penetration
  env.extras["log"]["Metrics/stance_foot_ball_dist"] = (
    gate * stance_dist
  ).sum() / gate.sum().clamp(min=1.0)
  return penalty


def premature_kick_lunge_penalty(
  env: ManagerBasedRlEnv,
  target_distance: float = 0.35,
  command_name: str = "goal",
  kick_ready_threshold: float = 0.45,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  feet_cfg: SceneEntityCfg | None = None,
) -> torch.Tensor:
  """Penalize feet lunging toward the ball before the robot is kick-ready."""
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
  )
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  foot_ids = _resolve_foot_ids(robot, feet_cfg)
  feet_vel = robot.data.body_link_lin_vel_w[:, foot_ids, :]
  ball_pos = ball.data.root_link_pos_w.unsqueeze(1)
  feet_pos = robot.data.body_link_pos_w[:, foot_ids, :]
  to_ball = ball_pos - feet_pos
  to_ball_dir = to_ball / torch.linalg.norm(to_ball, dim=-1, keepdim=True).clamp(
    min=1.0e-6
  )
  foot_progress = torch.sum(feet_vel * to_ball_dir, dim=-1).clamp(min=0.0)
  lunge = torch.max(foot_progress, dim=-1).values

  ready = _kick_ready_activation_mask(
    env,
    robot_cfg,
    ball_cfg,
    command_name,
    target_distance,
    kick_ready_threshold,
  )
  not_ready = 1.0 - ready
  stationary = _ball_stationary_mask(env, ball_cfg, ball_stationary_speed_threshold)
  active = not_ready * stationary * (~state.kick_detected).float()
  env.extras["log"]["Metrics/premature_kick_lunge"] = (active * lunge).mean()
  return active * lunge


def foot_velocity_toward_ball(
  env: ManagerBasedRlEnv,
  activate_inside_ball_distance: float = 0.55,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  feet_cfg: SceneEntityCfg | None = None,
) -> torch.Tensor:
  """Reward the nearest foot swinging toward the ball inside the kick zone."""
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    kick_phase_robot_ball_distance=activate_inside_ball_distance,
    robot_cfg_name=robot_cfg.name,
    ball_cfg_name=ball_cfg.name,
  )

  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  if feet_cfg is not None and feet_cfg.body_ids != slice(None):
    foot_ids = feet_cfg.body_ids
  else:
    left_ids, _ = robot.find_bodies("left_foot_link")
    right_ids, _ = robot.find_bodies("right_foot_link")
    foot_ids = [left_ids[0], right_ids[0]]

  feet_pos = robot.data.body_link_pos_w[:, foot_ids, :]
  feet_vel = robot.data.body_link_lin_vel_w[:, foot_ids, :]
  ball_pos = ball.data.root_link_pos_w.unsqueeze(1)
  to_ball = ball_pos - feet_pos
  to_ball_dir = to_ball / torch.linalg.norm(to_ball, dim=-1, keepdim=True).clamp(
    min=1.0e-6
  )
  foot_progress = torch.sum(feet_vel * to_ball_dir, dim=-1)
  nearest_progress = torch.max(foot_progress, dim=-1).values.clamp(min=0.0)

  stationary = (
    torch.linalg.norm(ball.data.root_link_lin_vel_w[:, :2], dim=-1)
    <= ball_stationary_speed_threshold
  ).float()
  in_zone = _kick_zone_mask(env, robot_cfg, ball_cfg, activate_inside_ball_distance)
  active = in_zone * stationary * (~state.kick_detected).float()
  reward = active * nearest_progress
  env.extras["log"]["Metrics/foot_velocity_toward_ball"] = reward.mean()
  return reward


def _support_plant_offsets(
  env: ManagerBasedRlEnv,
  command_name: str,
  robot_cfg: SceneEntityCfg,
  ball_cfg: SceneEntityCfg,
  feet_cfg: SceneEntityCfg | None = None,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
  """Return ``(sagittal_behind, lateral_signed, plant_score_inputs)``.

  Sagittal: metres the support foot sits *behind* the ball along ball→goal
  (positive = behind). Lateral: metres to the *support side* of the kick
  line (positive = correct side for the support foot).
  """
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  foot_ids = _resolve_foot_ids(robot, feet_cfg)
  feet_xy = robot.data.body_link_pos_w[:, foot_ids, :2]
  ball_xy = ball.data.root_link_pos_w[:, :2]
  goal_dir = ball_to_goal_direction_xy(env, ball_xy, command_name)
  # Left of goal axis when facing goal.
  left_dir = torch.stack((-goal_dir[:, 1], goal_dir[:, 0]), dim=-1)

  kicking_idx, support_idx = _kick_stance_foot_indices(env, robot, ball)
  support_xy = _gather_foot_tensor(feet_xy, support_idx)
  rel = support_xy - ball_xy
  sagittal_behind = -torch.sum(rel * goal_dir, dim=-1)
  lateral_from_left = torch.sum(rel * left_dir, dim=-1)
  # Right kick → left support → want +lateral; left kick → right support → −lateral.
  support_is_left = support_idx == 0
  lateral_signed = torch.where(support_is_left, lateral_from_left, -lateral_from_left)
  return sagittal_behind, lateral_signed, kicking_idx


def _plant_box_score(
  sag: torch.Tensor,
  lat: torch.Tensor,
  *,
  sagittal_target: float,
  sagittal_sigma: float,
  lateral_target: float,
  lateral_sigma: float,
  sagittal_funnel: float = 0.12,
  lateral_funnel: float = 0.10,
  funnel_weight: float = 0.55,
) -> torch.Tensor:
  """Dense plant score in ``(0, 1]`` with strong sagittal closing pressure.

  Uses a squared-inverse funnel (steep near the box) and a product of
  sagittal/lateral terms so a good lateral offset cannot mask standing
  too far behind the ball (the failure mode at ~0.6 m sagittal).
  """
  sag_err = torch.abs(sag - float(sagittal_target))
  lat_err = torch.abs(lat - float(lateral_target))
  sag_scale = max(float(sagittal_funnel), 1.0e-6)
  lat_scale = max(float(lateral_funnel), 1.0e-6)
  # Squared funnel: at err=0.45, scale=0.12 → ~0.07 (was ~0.4 with linear).
  sag_funnel = 1.0 / (1.0 + torch.square(sag_err / sag_scale))
  lat_funnel = 1.0 / (1.0 + torch.square(lat_err / lat_scale))
  funnel = torch.sqrt(torch.clamp(sag_funnel * lat_funnel, min=0.0))
  sag_peak = torch.exp(-torch.square(sag_err) / max(float(sagittal_sigma), 1.0e-6) ** 2)
  lat_peak = torch.exp(-torch.square(lat_err) / max(float(lateral_sigma), 1.0e-6) ** 2)
  peak = torch.sqrt(torch.clamp(sag_peak * lat_peak, min=0.0))
  w = float(funnel_weight)
  return w * funnel + (1.0 - w) * peak


def support_plant_score(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  sagittal_target: float = 0.14,
  sagittal_sigma: float = 0.12,
  lateral_target: float = 0.175,
  lateral_sigma: float = 0.08,
  sagittal_funnel: float = 0.12,
  lateral_funnel: float = 0.10,
  funnel_weight: float = 0.55,
  activate_inside_ball_distance: float = 1.2,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  stop_after_plant_latch: bool = False,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  feet_cfg: SceneEntityCfg | None = None,
) -> torch.Tensor:
  """Reward support-foot plant in the kick box (beside + behind the ball).

  Target: sagittal ``~0.10–0.18 m`` behind ball centre, lateral
  ``~0.15–0.20 m`` on the support side. Dense funnel + wide peak so there
  is gradient from approach-scale offsets.
  """
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    kick_phase_robot_ball_distance=activate_inside_ball_distance,
    robot_cfg_name=robot_cfg.name,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
  )
  sag, lat, _ = _support_plant_offsets(env, command_name, robot_cfg, ball_cfg, feet_cfg)
  score = _plant_box_score(
    sag,
    lat,
    sagittal_target=sagittal_target,
    sagittal_sigma=sagittal_sigma,
    lateral_target=lateral_target,
    lateral_sigma=lateral_sigma,
    sagittal_funnel=sagittal_funnel,
    lateral_funnel=lateral_funnel,
    funnel_weight=funnel_weight,
  )
  in_zone = _kick_zone_mask(env, robot_cfg, ball_cfg, activate_inside_ball_distance)
  active = in_zone * (~state.kick_detected).float()
  if stop_after_plant_latch:
    active = active * (1.0 - _plant_latch_mask(env))
  reward = active * score
  env.extras["log"]["Metrics/support_plant_score"] = reward.mean()
  env.extras["log"]["Metrics/support_plant_sagittal"] = (active * sag).mean()
  env.extras["log"]["Metrics/support_plant_lateral"] = (active * lat).mean()
  return reward


def strike_ankle_pitch(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  target_pitch: float = -0.50,
  pitch_sigma: float = 0.15,
  feet_ball_sensor_name: str = "feet_ball_contact",
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Reward instep ankle plantarflexion on the swinging foot at contact.

  ``target_pitch≈-0.5`` rad presents the top of the foot near the ankle
  (instep). Active on feet↔ball contact before / at kick latch.
  """
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    robot_cfg_name=robot_cfg.name,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
  )
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  kicking_idx, _ = _kick_stance_foot_indices(env, robot, ball)

  left_ids, _ = robot.find_joints("Left_Ankle_Pitch")
  right_ids, _ = robot.find_joints("Right_Ankle_Pitch")
  ankle_ids = [left_ids[0], right_ids[0]]
  ankle_q = robot.data.joint_pos[:, ankle_ids]
  swing_ankle = _gather_foot_tensor(ankle_q, kicking_idx)
  pitch_score = torch.exp(
    -torch.square(swing_ankle - float(target_pitch)) / float(pitch_sigma) ** 2
  )

  if feet_ball_sensor_name in env.scene.sensors:
    found = getattr(env.scene.sensors[feet_ball_sensor_name].data, "found", None)
    if found is None:
      contact = torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
    else:
      contact = found.reshape(found.shape[0], -1).any(dim=-1) > 0
  else:
    contact = state.agent_ball_contact

  # Pay on contact, and briefly after latch so the strike posture is credited.
  in_window = (~state.kick_detected) | (state.time_since_kick_s < 0.15)
  active = contact.float() * in_window.float()
  reward = active * pitch_score
  env.extras["log"]["Metrics/strike_ankle_pitch"] = reward.mean()
  env.extras["log"]["Metrics/strike_ankle_pitch_rad"] = (
    active * swing_ankle
  ).sum() / active.sum().clamp(min=1.0)
  return reward


def kick_contact_bridge(
  env: ManagerBasedRlEnv,
  activate_inside_ball_distance: float = 0.80,
  contact_bonus: float = 1.0,
  max_closing_speed: float = 2.0,
  closing_scale: float = 0.25,
  impulse_scale: float = 4.0,
  max_impulse: float = 3.0,
  impulse_contact_eps: float = 0.05,
  min_plant_score: float = 0.15,
  plant_gate_power: float = 1.0,
  command_name: str = "goal",
  sagittal_target: float = 0.14,
  sagittal_sigma: float = 0.12,
  lateral_target: float = 0.175,
  lateral_sigma: float = 0.08,
  sagittal_funnel: float = 0.12,
  lateral_funnel: float = 0.10,
  funnel_weight: float = 0.55,
  feet_ball_sensor_name: str = "feet_ball_contact",
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  feet_cfg: SceneEntityCfg | None = None,
) -> torch.Tensor:
  """Dense pre-kick bridge: light closing + goal impulse + contact.

  ``r = closing_scale * clip(foot_closing, 0, max_closing)
      + impulse_scale * clip(Δ(v_b·d̂), 0, max_impulse)
      + contact_bonus * contact * 1{Δ(v_b·d̂) > eps}``,
  active only while ``‖robot−ball‖ ≤ activate`` and ``~kick_detected``.
  When ``min_plant_score > 0``, multiplies by plant-box score so long reaches
  without a support plant do not farm the bridge.
  """
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    kick_phase_robot_ball_distance=activate_inside_ball_distance,
    robot_cfg_name=robot_cfg.name,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
  )
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  left_ids, _ = robot.find_bodies("left_foot_link")
  right_ids, _ = robot.find_bodies("right_foot_link")
  foot_ids = [left_ids[0], right_ids[0]]

  feet_pos = robot.data.body_link_pos_w[:, foot_ids, :]
  feet_vel = robot.data.body_link_lin_vel_w[:, foot_ids, :]
  ball_pos = ball.data.root_link_pos_w.unsqueeze(1)
  to_ball = ball_pos - feet_pos
  to_ball_dir = to_ball / torch.linalg.norm(to_ball, dim=-1, keepdim=True).clamp(
    min=1.0e-6
  )
  closing = torch.sum(feet_vel * to_ball_dir, dim=-1)
  # Prefer swing-foot closing (not support foot jabbing).
  kicking_idx, _ = _kick_stance_foot_indices(env, robot, ball)
  swing_closing = _gather_foot_tensor(closing, kicking_idx).clamp(
    min=0.0, max=float(max_closing_speed)
  )

  if feet_ball_sensor_name in env.scene.sensors:
    found = getattr(env.scene.sensors[feet_ball_sensor_name].data, "found", None)
    if found is None:
      contact = torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
    else:
      contact = found.reshape(found.shape[0], -1).any(dim=-1) > 0
  else:
    contact = torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)

  impulse = torch.clamp(state.delta_vel_toward_goal, min=0.0, max=float(max_impulse))
  useful_contact = contact & (state.delta_vel_toward_goal > float(impulse_contact_eps))

  in_zone = _kick_zone_mask(env, robot_cfg, ball_cfg, activate_inside_ball_distance)
  active = in_zone * (~state.kick_detected).float()

  if float(min_plant_score) > 0.0 or float(plant_gate_power) > 0.0:
    sag, lat, _ = _support_plant_offsets(
      env, command_name, robot_cfg, ball_cfg, feet_cfg
    )
    plant = _plant_box_score(
      sag,
      lat,
      sagittal_target=sagittal_target,
      sagittal_sigma=sagittal_sigma,
      lateral_target=lateral_target,
      lateral_sigma=lateral_sigma,
      sagittal_funnel=sagittal_funnel,
      lateral_funnel=lateral_funnel,
      funnel_weight=funnel_weight,
    )
    if float(min_plant_score) > 0.0:
      active = active * (plant >= float(min_plant_score)).float()
    if float(plant_gate_power) > 0.0:
      active = active * plant.clamp(min=0.0).pow(float(plant_gate_power))

  reward = active * (
    float(closing_scale) * swing_closing
    + float(impulse_scale) * impulse
    + float(contact_bonus) * useful_contact.float()
  )
  env.extras["log"]["Metrics/kick_contact_bridge"] = reward.mean()
  env.extras["log"]["Metrics/kick_contact_bridge_contact"] = (
    active * contact.float()
  ).mean()
  env.extras["log"]["Metrics/kick_contact_bridge_impulse"] = (active * impulse).mean()
  return reward


def ball_acceleration_toward_goal(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  acceleration_scale: float = 10.0,
  max_reward: float = 1.0,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Reward positive ball acceleration toward the sampled goal direction."""
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
  )

  ball: Entity = env.scene[ball_cfg.name]
  ball_vel = ball.data.root_link_lin_vel_w[:, :2]
  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  ball_pos = ball.data.root_link_pos_w[:, :2]
  goal_pos = command[:, :2] + env.scene.env_origins[:, :2]
  goal_dir = (goal_pos - ball_pos) / torch.norm(
    goal_pos - ball_pos, dim=-1, keepdim=True
  ).clamp(min=1e-6)

  acceleration = (ball_vel - state.last_ball_vel_w[:, :2]) / env.step_dt
  along_goal = torch.sum(acceleration * goal_dir, dim=-1)
  reward = (
    torch.tanh(torch.clamp(along_goal, min=0.0) / acceleration_scale) * max_reward
  )
  state.last_ball_vel_w[:] = ball.data.root_link_lin_vel_w
  env.extras["log"]["Metrics/ball_accel_toward_goal"] = reward.mean()
  return reward


def near_ball_wait_penalty(
  env: ManagerBasedRlEnv,
  near_ball_distance: float = 1.0,
  ramp_tau_s: float = 1.0,
  max_scale: float = 3.0,
  robot_still_speed: float = 0.25,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> torch.Tensor:
  """Penalize waiting / standing near the ball before a kick.

  While ``‖robot−ball‖ < near_ball_distance`` and the ball has not been kicked,
  cost grows as ``(t/τ)²`` (capped). Extra scale when nearly still so passive
  loitering is worse than continuing to act.
  """

  state = ensure_ball_phase_updated(
    env,
    ball_cfg_name=ball_cfg.name,
    robot_cfg_name=robot_cfg.name,
    kick_phase_robot_ball_distance=near_ball_distance,
  )
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  dist = torch.linalg.norm(
    robot.data.root_link_pos_w[:, :2] - ball.data.root_link_pos_w[:, :2],
    dim=-1,
  )
  near = (dist < float(near_ball_distance)) & (~state.kick_detected)
  timer = getattr(env, "_near_ball_wait_timer", None)
  if timer is None or timer.shape[0] != env.num_envs:
    timer = torch.zeros(env.num_envs, device=env.device)
  fresh = env.episode_length_buf <= 1
  timer = torch.where(
    near & (~fresh),
    timer + env.step_dt,
    torch.zeros_like(timer),
  )
  env._near_ball_wait_timer = timer
  scale = torch.clamp(
    torch.square(timer / max(float(ramp_tau_s), 1.0e-6)),
    max=float(max_scale),
  )
  robot_speed = torch.linalg.norm(robot.data.root_link_lin_vel_w[:, :2], dim=-1)
  still_boost = torch.where(
    robot_speed < float(robot_still_speed),
    torch.full_like(scale, 1.5),
    torch.ones_like(scale),
  )
  cost = near.float() * scale * still_boost
  env.extras["log"]["Metrics/near_ball_wait_s"] = timer.mean()
  env.extras["log"]["Metrics/near_ball_wait"] = cost.mean()
  return cost


def post_kick_upright(
  env: ManagerBasedRlEnv,
  sigma: float = 0.20,
  contact_window_s: float = 1.0,
  min_kick_speed: float = 5.0,
  target_height: float | None = None,
  height_sigma: float = 0.08,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  asset_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> torch.Tensor:
  """Reward upright (+ optional walk height) after a real kick.

  Active while ``kick_detected``, ``time_since_kick_s < contact_window_s``, and
  ``max_vel_toward_goal >= min_kick_speed``. Uses the kick latch (not the
  ≥5 m/s strong-kick flag) so discovery stages can shape balance after moderate
  strikes. When ``target_height`` is set, multiplies by a Gaussian on trunk
  height so crouch / collapse after contact is not rewarded.
  """
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
  )
  robot: Entity = env.scene[asset_cfg.name]
  if asset_cfg.body_ids:
    trunk_quat_w = robot.data.body_link_quat_w[:, asset_cfg.body_ids, :].squeeze(1)
    height = robot.data.body_link_pos_w[:, asset_cfg.body_ids, 2].squeeze(1)
  else:
    trunk_quat_w = robot.data.root_link_quat_w
    height = robot.data.root_link_pos_w[:, 2]
  projected_gravity_b = quat_apply_inverse(trunk_quat_w, robot.data.gravity_vec_w)
  tilt = torch.sum(torch.square(projected_gravity_b[:, :2]), dim=-1)
  upright = torch.exp(-tilt / sigma**2)

  if target_height is not None:
    height_score = torch.exp(
      -torch.square(height - float(target_height)) / float(height_sigma) ** 2
    )
    reward = upright * height_score
  else:
    height_score = torch.ones_like(upright)
    reward = upright

  active = _post_kick_window_mask(state, contact_window_s, min_kick_speed)
  env.extras["log"]["Metrics/post_kick_upright"] = (active * reward).mean()
  env.extras["log"]["Metrics/post_kick_window"] = active.mean()
  env.extras["log"]["Metrics/post_kick_height_score"] = (active * height_score).mean()
  return active * reward


def _post_kick_window_mask(
  state,
  contact_window_s: float,
  min_kick_speed: float,
) -> torch.Tensor:
  """1 during the post-kick recover window after a real toward-goal kick."""
  in_window = state.time_since_kick_s < float(contact_window_s)
  speed_ok = state.max_vel_toward_goal >= float(min_kick_speed)
  return (state.kick_detected & in_window & speed_ok).float()


def post_kick_stance(
  env: ManagerBasedRlEnv,
  contact_window_s: float = 1.5,
  min_kick_speed: float = 1.2,
  feet_distance_ref: float = 0.19,
  distance_sigma: float = 0.06,
  flat_sigma: float = 0.25,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  feet_cfg: SceneEntityCfg | None = None,
) -> torch.Tensor:
  """Reward standing recovery after a kick: feet close + soles flat.

  Same activation window as ``post_kick_upright``. Returns
  ``close_score * flat_score`` in ``[0, 1]`` so a splayed / tipped-foot finish
  does not get paid after contact.
  """
  from mjlab.utils.lab_api.math import euler_xyz_from_quat

  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
  )
  robot: Entity = env.scene[robot_cfg.name]
  foot_ids = _resolve_foot_ids(robot, feet_cfg)

  foot_xy = robot.data.body_link_pos_w[:, foot_ids, :2]
  _, _, yaw = euler_xyz_from_quat(robot.data.root_link_quat_w)
  dx = foot_xy[:, 1, 0] - foot_xy[:, 0, 0]
  dy = foot_xy[:, 1, 1] - foot_xy[:, 0, 1]
  lateral = torch.abs(torch.cos(yaw) * dy - torch.sin(yaw) * dx)
  close_score = torch.exp(
    -torch.square(lateral - float(feet_distance_ref)) / float(distance_sigma) ** 2
  )

  foot_quat = robot.data.body_link_quat_w[:, foot_ids, :]
  roll, pitch, _ = euler_xyz_from_quat(foot_quat.reshape(-1, 4))
  roll = roll.reshape(env.num_envs, -1)
  pitch = pitch.reshape(env.num_envs, -1)
  flat_err = torch.sum(torch.square(roll) + torch.square(pitch), dim=-1)
  flat_score = torch.exp(-flat_err / float(flat_sigma) ** 2)

  reward = close_score * flat_score
  active = _post_kick_window_mask(state, contact_window_s, min_kick_speed)
  env.extras["log"]["Metrics/post_kick_stance"] = (active * reward).mean()
  env.extras["log"]["Metrics/post_kick_feet_lateral"] = (active * lateral).mean()
  env.extras["log"]["Metrics/post_kick_feet_flat"] = (active * flat_score).mean()
  return active * reward


def post_kick_robot_still(
  env: ManagerBasedRlEnv,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Penalize robot motion after a kick is detected while the ball is rolling."""
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
  )
  robot: Entity = env.scene[robot_cfg.name]
  speed = torch.linalg.norm(robot.data.root_link_lin_vel_w[:, :2], dim=-1)
  ball_moving = (
    torch.linalg.norm(env.scene[ball_cfg.name].data.root_link_lin_vel_w[:, :2], dim=-1)
    > ball_stationary_speed_threshold
  )
  active = (state.kick_detected & ball_moving).float()
  penalty = torch.square(speed)
  env.extras["log"]["Metrics/post_kick_robot_speed"] = (active * speed).mean()
  return active * penalty


def post_kick_chase_penalty(
  env: ManagerBasedRlEnv,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Penalize the robot moving toward the ball after contact."""
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
  )
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  to_ball = ball.data.root_link_pos_w[:, :2] - robot.data.root_link_pos_w[:, :2]
  dir_w = to_ball / torch.linalg.norm(to_ball, dim=-1, keepdim=True).clamp(min=1e-6)
  chase = torch.sum(robot.data.root_link_lin_vel_w[:, :2] * dir_w, dim=-1).clamp(
    min=0.0
  )
  ball_moving = (
    torch.linalg.norm(ball.data.root_link_lin_vel_w[:, :2], dim=-1)
    > ball_stationary_speed_threshold
  )
  active = (state.kick_detected & ball_moving).float()
  env.extras["log"]["Metrics/post_kick_chase"] = (active * chase).mean()
  return active * chase


def kick_pre_kick_urgency(
  env: ManagerBasedRlEnv,
  max_still_time_s: float = 2.0,
  target_distance: float = 0.35,
  command_name: str = "goal",
  kick_ready_threshold: float = 0.45,
  activate_robot_ball_distance: float = 0.55,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Penalize delaying the kick once the robot is in the kick-ready pose."""
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    kick_phase_robot_ball_distance=activate_robot_ball_distance,
    robot_cfg_name=robot_cfg.name,
    ball_cfg_name=ball_cfg.name,
  )
  ready = _kick_ready_activation_mask(
    env,
    robot_cfg,
    ball_cfg,
    command_name,
    target_distance,
    kick_ready_threshold,
  )
  progress = (state.time_since_still_s / max_still_time_s).clamp(max=1.0)
  active = (~state.kick_detected).float()
  return active * ready * progress * progress


def ball_dribble_penalty(
  env: ManagerBasedRlEnv,
  min_kick_speed: float = 2.0,
  dribble_speed: float = 0.15,
  kick_phase_robot_ball_distance: float = 0.55,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Penalize slow ball motion in the kick zone that is not a real kick."""
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    min_kick_speed=min_kick_speed,
    dribble_speed=dribble_speed,
    ball_cfg_name=ball_cfg.name,
    robot_cfg_name=robot_cfg.name,
    kick_phase_robot_ball_distance=kick_phase_robot_ball_distance,
  )
  dribbling = (state.time_since_slow_ball_s > 0.0).float()
  env.extras["log"]["Metrics/ball_dribble_penalty"] = dribbling.mean()
  return dribbling


def ball_not_moving_penalty(
  env: ManagerBasedRlEnv,
  activate_inside_ball_distance: float = 1.0,
  pref_dwell_dist: float = 0.35,
  ramp_tau_s: float = 0.5,
  max_scale: float = 4.0,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.9,
  setup_exit_dist: float = 1.0,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Ramped penalty for camping a dead ball at the kick magnet.

  Must be near the ball **and** committed to ``P_ref`` (``‖xy−P_ref‖ <
  pref_dwell_dist`` or phase ≥ Setup). A bare distance gate taught the
  policy to stay outside the bubble instead of kicking; this only punishes
  lingering once it has arrived at the approach/kick pose.

  Cost ``(t / ramp_tau_s)²`` clamped at ``max_scale``. Cleared after
  ``kick_detected``.
  """
  from mjlab.tasks.kick.mdp.pref_pose import (
    PHASE_SETUP,
    compute_reference_pose_xy,
  )

  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
    robot_cfg_name=robot_cfg.name,
    kick_phase_robot_ball_distance=activate_inside_ball_distance,
  )
  near = _kick_zone_mask(env, robot_cfg, ball_cfg, activate_inside_ball_distance)
  ball_still = _ball_stationary_mask(env, ball_cfg, ball_stationary_speed_threshold)
  pref, phase = compute_reference_pose_xy(
    env,
    **_pref_pose_kwargs(
      command_name=command_name,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    ),
  )
  robot: Entity = env.scene[robot_cfg.name]
  pref_dist = torch.linalg.norm(robot.data.root_link_pos_w[:, :2] - pref, dim=-1)
  committed = (pref_dist < float(pref_dwell_dist)) | (phase >= PHASE_SETUP)
  camping = (near > 0.0) & (ball_still > 0.0) & (~state.kick_detected) & committed
  timer = getattr(env, "_ball_not_moving_timer", None)
  if timer is None or timer.shape[0] != env.num_envs:
    timer = torch.zeros(env.num_envs, device=env.device)
  timer = torch.where(
    camping,
    timer + env.step_dt,
    torch.zeros_like(timer),
  )
  env._ball_not_moving_timer = timer
  ramp = torch.square(timer / max(float(ramp_tau_s), 1.0e-6)).clamp(
    max=float(max_scale)
  )
  penalty = camping.float() * ramp
  env.extras["log"]["Metrics/ball_not_moving"] = penalty.mean()
  env.extras["log"]["Metrics/ball_not_moving_timer_s"] = timer.mean()
  env.extras["log"]["Metrics/ball_not_moving_active"] = camping.float().mean()
  return penalty


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
  goal_pos = command[:, :2] + env.scene.env_origins[:, :2]

  dist_sq = torch.sum(torch.square(ball_pos - goal_pos), dim=-1)
  reward = torch.exp(-dist_sq / std**2)
  env.extras["log"]["Metrics/ball_goal_distance"] = torch.sqrt(dist_sq).mean()
  return reward


def _pref_pose_kwargs(
  *,
  command_name: str,
  arc_radius: float,
  setup_enter_dist: float,
  setup_exit_dist: float,
  setup_behind: float,
  setup_lateral: float,
  prefer_right_foot: bool,
  bearing_thresh: float,
  lateral_thresh: float,
  setup_blend_end: float,
  strike_blend_thresh: float,
  setup_pos_thresh: float,
  dynamic_kick_foot: bool,
  robot_cfg: SceneEntityCfg,
  ball_cfg: SceneEntityCfg,
) -> dict:
  return {
    "command_name": command_name,
    "arc_radius": arc_radius,
    "setup_enter_dist": setup_enter_dist,
    "setup_exit_dist": setup_exit_dist,
    "setup_behind": setup_behind,
    "setup_lateral": setup_lateral,
    "prefer_right_foot": prefer_right_foot,
    "bearing_thresh": bearing_thresh,
    "lateral_thresh": lateral_thresh,
    "setup_blend_end": setup_blend_end,
    "strike_blend_thresh": strike_blend_thresh,
    "setup_pos_thresh": setup_pos_thresh,
    "dynamic_kick_foot": dynamic_kick_foot,
    "robot_cfg": robot_cfg,
    "ball_cfg": ball_cfg,
  }


def pref_pose_tracking(
  env: ManagerBasedRlEnv,
  std: float = 0.45,
  robot_still_speed: float = 0.25,
  still_decay_tau_s: float = 0.35,
  dwell_dist: float = 0.65,
  dwell_decay_tau_s: float = 0.25,
  setup_scale: float = 0.0,
  strike_scale: float = 0.0,
  command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.9,
  setup_exit_dist: float = 1.0,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Gaussian approach carrot to plant ``P_ref`` — not a park reward.

  Pays while closing from afar. Inside ``dwell_dist`` the scale decays fast
  (still + dwell). ``setup_scale`` / ``strike_scale`` (default **0**) zero the
  term once in Setup/Strike so plant camping cannot replace a kick. Arrived
  at the plant band (``pref_dist < setup_pos_thresh``) is also zeroed.
  """
  from mjlab.tasks.kick.mdp.pref_pose import (
    PHASE_SETUP,
    PHASE_STRIKE,
    compute_reference_pose_xy,
    get_kick_aligned,
  )

  robot: Entity = env.scene[robot_cfg.name]
  pref, phase = compute_reference_pose_xy(
    env,
    **_pref_pose_kwargs(
      command_name=command_name,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    ),
  )
  pref_dist = torch.linalg.norm(robot.data.root_link_pos_w[:, :2] - pref, dim=-1)
  reward = torch.exp(-torch.square(pref_dist) / std**2)

  near_pref = pref_dist < float(dwell_dist)
  robot_speed = torch.linalg.norm(robot.data.root_link_lin_vel_w[:, :2], dim=-1)
  robot_still = robot_speed < float(robot_still_speed)

  still_timer = getattr(env, "_pref_pose_robot_still_timer", None)
  if still_timer is None or still_timer.shape[0] != env.num_envs:
    still_timer = torch.zeros(env.num_envs, device=env.device)
  still_timer = torch.where(
    near_pref & robot_still,
    still_timer + env.step_dt,
    torch.zeros_like(still_timer),
  )
  env._pref_pose_robot_still_timer = still_timer
  motion_decay = torch.exp(-still_timer / max(float(still_decay_tau_s), 1.0e-6))

  dwell_timer = getattr(env, "_pref_pose_dwell_timer", None)
  if dwell_timer is None or dwell_timer.shape[0] != env.num_envs:
    dwell_timer = torch.zeros(env.num_envs, device=env.device)
  dwell_timer = torch.where(
    near_pref,
    dwell_timer + env.step_dt,
    torch.zeros_like(dwell_timer),
  )
  env._pref_pose_dwell_timer = dwell_timer
  dwell_decay = torch.exp(-dwell_timer / max(float(dwell_decay_tau_s), 1.0e-6))

  scale = motion_decay * dwell_decay
  # Arrived / kick window: position magnet off — swing + ball vel must take over.
  arrived = pref_dist < float(setup_pos_thresh)
  scale = torch.where(arrived, torch.zeros_like(scale), scale)
  scale = torch.where(
    phase == PHASE_SETUP,
    torch.full_like(scale, float(setup_scale)),
    scale,
  )
  scale = torch.where(
    phase == PHASE_STRIKE,
    torch.full_like(scale, float(strike_scale)),
    scale,
  )
  reward = reward * scale
  env.extras["log"]["Metrics/pref_pose_dist"] = pref_dist.mean()
  env.extras["log"]["Metrics/pref_pose_phase"] = phase.float().mean()
  env.extras["log"]["Metrics/pref_pose_scale"] = scale.mean()
  env.extras["log"]["Metrics/pref_pose_robot_still_s"] = still_timer.mean()
  env.extras["log"]["Metrics/pref_pose_dwell_s"] = dwell_timer.mean()
  env.extras["log"]["Metrics/kick_aligned"] = (
    get_kick_aligned(env, prefer_right_foot).float().mean()
  )
  return reward


def pref_pose_approach_velocity(
  env: ManagerBasedRlEnv,
  arrival_dist: float = 0.65,
  strike_scale: float = 0.0,
  setup_scale: float = 0.0,
  command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.9,
  setup_exit_dist: float = 1.0,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Reward planar velocity toward plant ``P_ref`` while still approaching.

  Zero inside ``arrival_dist`` and in Setup/Strike so the policy cannot farm
  micro-shuffles on the plant instead of aligning and kicking.
  """
  from mjlab.tasks.kick.mdp.pref_pose import (
    PHASE_SETUP,
    PHASE_STRIKE,
    compute_reference_pose_xy,
  )

  robot: Entity = env.scene[robot_cfg.name]
  pref, phase = compute_reference_pose_xy(
    env,
    **_pref_pose_kwargs(
      command_name=command_name,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    ),
  )
  delta = pref - robot.data.root_link_pos_w[:, :2]
  dist = torch.linalg.norm(delta, dim=-1)
  direction = delta / dist.unsqueeze(-1).clamp(min=1.0e-6)
  vel = robot.data.root_link_lin_vel_w[:, :2]
  toward = torch.sum(vel * direction, dim=-1).clamp(min=0.0)
  scale = (dist >= float(arrival_dist)).float()
  scale = torch.where(
    phase == PHASE_SETUP,
    torch.full_like(scale, float(setup_scale)),
    scale,
  )
  scale = torch.where(
    phase == PHASE_STRIKE,
    torch.full_like(scale, float(strike_scale)),
    scale,
  )
  return toward * scale


def swing_foot_ball_proximity(
  env: ManagerBasedRlEnv,
  std: float = 0.316,
  still_decay_tau_s: float = 0.6,
  ball_stationary_speed_threshold: float = 0.1,
  command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.9,
  setup_exit_dist: float = 1.0,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Dense shaping: pull latched swing foot toward the ball **after align**.

  Gate is kick ``aligned`` (plant pose + bearing on ball→goal) — not bare Setup
  or near-``P_ref``. Far / unaligned approach cannot farm foot→ball or touch
  early. Foot choice is nearest-during-Arc, latched on Setup entry.

  Decayed by near-ball ball-still time so proximity alone does not replace a
  swing (``ball_velocity_toward_goal``, ``swing_foot_velocity_toward_ball``).
  """
  from mjlab.tasks.kick.mdp.pref_pose import (
    compute_reference_pose_xy,
    get_kick_aligned,
    get_latched_kicking_foot,
  )

  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  _pref, _phase = compute_reference_pose_xy(
    env,
    **_pref_pose_kwargs(
      command_name=command_name,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    ),
  )
  kicking_foot = get_latched_kicking_foot(env, prefer_right_foot)
  left_ids, _ = robot.find_bodies("left_foot_link")
  right_ids, _ = robot.find_bodies("right_foot_link")
  left_xy = robot.data.body_link_pos_w[:, left_ids[0], :2]
  right_xy = robot.data.body_link_pos_w[:, right_ids[0], :2]
  swing_xy = torch.where((kicking_foot == 0).unsqueeze(-1), left_xy, right_xy)
  ball_xy = ball.data.root_link_pos_w[:, :2]
  dist_sq = torch.sum(torch.square(swing_xy - ball_xy), dim=-1)
  shaping = torch.exp(-dist_sq / (std * std))
  gate = get_kick_aligned(env, prefer_right_foot).float()
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_phase_robot_ball_distance=setup_exit_dist,
    ball_cfg_name=ball_cfg.name,
    robot_cfg_name=robot_cfg.name,
  )
  decay = torch.exp(-state.time_since_still_s / max(float(still_decay_tau_s), 1.0e-6))
  reward = gate * shaping * decay
  env.extras["log"]["Metrics/swing_foot_ball_dist"] = (
    gate * torch.sqrt(dist_sq)
  ).sum() / gate.sum().clamp(min=1.0)
  env.extras["log"]["Metrics/kicking_foot_right"] = kicking_foot.float().mean()
  env.extras["log"]["Metrics/swing_foot_proximity_decay"] = (
    gate * decay
  ).sum() / gate.sum().clamp(min=1.0)
  return reward


def swing_foot_velocity_toward_ball(
  env: ManagerBasedRlEnv,
  max_speed: float = 3.0,
  command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.9,
  setup_exit_dist: float = 1.0,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Reward swing-foot speed through the ball **after align**.

  Same ``aligned`` gate as ``swing_foot_ball_proximity``. Far / unaligned
  approach stays off so the policy cannot touch early for shaping.
  """
  from mjlab.tasks.kick.mdp.pref_pose import (
    compute_reference_pose_xy,
    get_kick_aligned,
    get_latched_kicking_foot,
  )

  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  _pref, _phase = compute_reference_pose_xy(
    env,
    **_pref_pose_kwargs(
      command_name=command_name,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    ),
  )
  kicking_foot = get_latched_kicking_foot(env, prefer_right_foot)
  left_ids, _ = robot.find_bodies("left_foot_link")
  right_ids, _ = robot.find_bodies("right_foot_link")
  feet_pos = robot.data.body_link_pos_w[:, [left_ids[0], right_ids[0]], :2]
  feet_vel = robot.data.body_link_lin_vel_w[:, [left_ids[0], right_ids[0]], :2]
  swing_pos = _gather_foot_tensor(feet_pos, kicking_foot)
  swing_vel = _gather_foot_tensor(feet_vel, kicking_foot)

  ball_xy = ball.data.root_link_pos_w[:, :2]
  to_ball = ball_xy - swing_pos
  to_ball_dir = to_ball / torch.linalg.norm(to_ball, dim=-1, keepdim=True).clamp(
    min=1.0e-6
  )
  progress = torch.sum(swing_vel * to_ball_dir, dim=-1).clamp(min=0.0, max=max_speed)

  gate = get_kick_aligned(env, prefer_right_foot).float()
  reward = gate * progress
  env.extras["log"]["Metrics/swing_foot_velocity"] = (
    gate * progress
  ).sum() / gate.sum().clamp(min=1.0)
  return reward


def collision_except_strike_phase(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.9,
  setup_exit_dist: float = 1.0,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  sensor_name: str = "self_collision",
  force_threshold: float = 1.0,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Self-collision penalty gated off during Phase C (CoM through ball)."""
  from mjlab.tasks.kick.mdp.pref_pose import PHASE_STRIKE, compute_reference_pose_xy
  from mjlab.tasks.velocity import mdp as velocity_mdp

  _pref, phase = compute_reference_pose_xy(
    env,
    **_pref_pose_kwargs(
      command_name=command_name,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    ),
  )
  raw = velocity_mdp.self_collision_cost(
    env, sensor_name=sensor_name, force_threshold=force_threshold
  )
  gate = (phase != PHASE_STRIKE).float()
  return gate * raw


def ball_avoidance_except_strike(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  min_clearance: float = 0.22,
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.9,
  setup_exit_dist: float = 1.0,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Penalize CoM inside ball clearance until kick-aligned.

  Stays on through Arc/Setup while ``aligned`` is false so the robot cannot
  crowd/touch the ball on the way in. Clears once plant pose + bearing match
  ball→goal so the swing can enter. (Name kept for cfg compatibility.)
  """
  from mjlab.tasks.kick.mdp.pref_pose import (
    compute_reference_pose_xy,
    get_kick_aligned,
  )

  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  _pref, _phase = compute_reference_pose_xy(
    env,
    **_pref_pose_kwargs(
      command_name=command_name,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    ),
  )
  dist = torch.linalg.norm(
    robot.data.root_link_pos_w[:, :2] - ball.data.root_link_pos_w[:, :2], dim=-1
  )
  penetration = (min_clearance - dist).clamp(min=0.0)
  gate = (~get_kick_aligned(env, prefer_right_foot)).float()
  return gate * penetration


def premature_ball_contact_penalty(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  feet_ball_sensor_name: str = "feet_ball_contact",
  body_ball_sensor_name: str = "body_ball_contact",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.9,
  setup_exit_dist: float = 1.0,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Penalize any feet/body↔ball contact before kick alignment.

  Complements CoM ``ball_avoidance``: even a grazing foot touch while still
  unaligned is costly. Clears when ``aligned`` so the real strike is allowed.
  """
  from mjlab.tasks.kick.mdp.pref_pose import (
    compute_reference_pose_xy,
    get_kick_aligned,
  )

  compute_reference_pose_xy(
    env,
    **_pref_pose_kwargs(
      command_name=command_name,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    ),
  )

  def _any_contact(name: str) -> torch.Tensor:
    if name not in env.scene.sensors:
      return torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
    found = getattr(env.scene.sensors[name].data, "found", None)
    if found is None:
      return torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
    return found.reshape(found.shape[0], -1).any(dim=-1) > 0

  contact = _any_contact(feet_ball_sensor_name) | _any_contact(body_ball_sensor_name)
  unaligned = ~get_kick_aligned(env, prefer_right_foot)
  cost = (unaligned & contact).float()
  env.extras["log"]["Metrics/premature_ball_contact"] = cost.mean()
  env.extras["log"]["Metrics/kick_aligned"] = (
    get_kick_aligned(env, prefer_right_foot).float().mean()
  )
  return cost


def _kick_phase_walk_scale(
  env: ManagerBasedRlEnv,
  *,
  arc_scale: float = 1.0,
  setup_scale: float = 0.25,
  strike_scale: float = 0.0,
  near_ball_dist: float | None = None,
  near_ball_scale: float = 1.0,
  plant_full_dist: float | None = 0.6,
  plant_far_dist: float = 2.0,
  plant_far_scale: float = 0.15,
  restore_tracking_after_kick: bool = True,
  goal_command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.45,
  setup_exit_dist: float = 0.5,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Per-env scale for BaseWalk regularizers: phase × optional plant proximity.

  Phase: full in Arc, soft Setup, off Strike. Plant proximity (when enabled)
  further weakens far-from-plant walk farming: full near ``P_ref``, weak far.
  """
  from mjlab.tasks.kick.mdp.pref_pose import (
    PHASE_SETUP,
    PHASE_STRIKE,
    compute_reference_pose_xy,
  )

  pref, phase = compute_reference_pose_xy(
    env,
    **_pref_pose_kwargs(
      command_name=goal_command_name,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    ),
  )
  _ = pref
  scale = torch.full(
    (env.num_envs,), float(arc_scale), device=env.device, dtype=torch.float32
  )
  scale = torch.where(
    phase == PHASE_SETUP,
    torch.full_like(scale, float(setup_scale)),
    scale,
  )
  scale = torch.where(
    phase == PHASE_STRIKE,
    torch.full_like(scale, float(strike_scale)),
    scale,
  )
  if near_ball_dist is not None:
    robot: Entity = env.scene[robot_cfg.name]
    ball: Entity = env.scene[ball_cfg.name]
    ball_dist = torch.linalg.norm(
      robot.data.root_link_pos_w[:, :2] - ball.data.root_link_pos_w[:, :2],
      dim=-1,
    )
    scale = torch.where(
      ball_dist < float(near_ball_dist),
      scale * float(near_ball_scale),
      scale,
    )
  if plant_full_dist is not None:
    scale = scale * _plant_proximity_walk_scale(
      env,
      full_dist=plant_full_dist,
      far_dist=plant_far_dist,
      far_scale=plant_far_scale,
      restore_after_kick=restore_tracking_after_kick,
      goal_command_name=goal_command_name,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
    )
  return scale


def _pref_scale_kwargs(
  *,
  goal_command_name: str,
  arc_scale: float,
  setup_scale: float,
  strike_scale: float,
  arc_radius: float,
  setup_enter_dist: float,
  setup_exit_dist: float,
  setup_behind: float,
  setup_lateral: float,
  prefer_right_foot: bool,
  bearing_thresh: float,
  lateral_thresh: float,
  setup_blend_end: float,
  strike_blend_thresh: float,
  setup_pos_thresh: float,
  dynamic_kick_foot: bool,
  robot_cfg: SceneEntityCfg,
  ball_cfg: SceneEntityCfg,
  near_ball_dist: float | None = None,
  near_ball_scale: float = 1.0,
  plant_full_dist: float | None = 0.6,
  plant_far_dist: float = 2.0,
  plant_far_scale: float = 0.15,
  restore_tracking_after_kick: bool = True,
) -> dict:
  return {
    "arc_scale": arc_scale,
    "setup_scale": setup_scale,
    "strike_scale": strike_scale,
    "near_ball_dist": near_ball_dist,
    "near_ball_scale": near_ball_scale,
    "plant_full_dist": plant_full_dist,
    "plant_far_dist": plant_far_dist,
    "plant_far_scale": plant_far_scale,
    "restore_tracking_after_kick": restore_tracking_after_kick,
    "goal_command_name": goal_command_name,
    "arc_radius": arc_radius,
    "setup_enter_dist": setup_enter_dist,
    "setup_exit_dist": setup_exit_dist,
    "setup_behind": setup_behind,
    "setup_lateral": setup_lateral,
    "prefer_right_foot": prefer_right_foot,
    "bearing_thresh": bearing_thresh,
    "lateral_thresh": lateral_thresh,
    "setup_blend_end": setup_blend_end,
    "strike_blend_thresh": strike_blend_thresh,
    "setup_pos_thresh": setup_pos_thresh,
    "dynamic_kick_foot": dynamic_kick_foot,
    "robot_cfg": robot_cfg,
    "ball_cfg": ball_cfg,
  }


class feet_swing_for_kick:
  """``feet_swing`` gated by kick phase (off in Setup/Strike by default)."""

  def __init__(self, cfg: object, env: ManagerBasedRlEnv):
    from mjlab.tasks.velocity.mdp.rewards import feet_swing

    self._inner = feet_swing(cfg, env)  # type: ignore[arg-type]

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    sensor_name: str,
    period: float = 0.6,
    swing_period: float = 0.2,
    command_name: str = "twist",
    command_threshold: float = 0.05,
    left_foot_name: str = "left_foot_link",
    right_foot_name: str = "right_foot_link",
    arc_scale: float = 1.0,
    setup_scale: float = 0.0,
    strike_scale: float = 0.0,
    near_ball_dist: float | None = 1.2,
    near_ball_scale: float = 0.05,
    goal_command_name: str = "goal",
    arc_radius: float = 0.4,
    setup_enter_dist: float = 0.45,
    setup_exit_dist: float = 0.5,
    setup_behind: float = 0.35,
    setup_lateral: float = 0.12,
    prefer_right_foot: bool = True,
    bearing_thresh: float = 0.2,
    lateral_thresh: float = 0.05,
    setup_blend_end: float = 0.20,
    strike_blend_thresh: float = 0.75,
    setup_pos_thresh: float = 0.28,
    dynamic_kick_foot: bool = True,
    robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
    ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
    plant_full_dist: float | None = None,
    plant_far_dist: float = 2.0,
    plant_far_scale: float = 0.15,
    restore_tracking_after_kick: bool = True,
    disable_when_planted: bool = False,
  ) -> torch.Tensor:
    raw = self._inner(
      env,
      sensor_name=sensor_name,
      period=period,
      swing_period=swing_period,
      command_name=command_name,
      command_threshold=command_threshold,
      left_foot_name=left_foot_name,
      right_foot_name=right_foot_name,
    )
    scale = _kick_phase_walk_scale(
      env,
      **_pref_scale_kwargs(
        goal_command_name=goal_command_name,
        arc_scale=arc_scale,
        setup_scale=setup_scale,
        strike_scale=strike_scale,
        near_ball_dist=near_ball_dist,
        near_ball_scale=near_ball_scale,
        arc_radius=arc_radius,
        setup_enter_dist=setup_enter_dist,
        setup_exit_dist=setup_exit_dist,
        setup_behind=setup_behind,
        setup_lateral=setup_lateral,
        prefer_right_foot=prefer_right_foot,
        bearing_thresh=bearing_thresh,
        lateral_thresh=lateral_thresh,
        setup_blend_end=setup_blend_end,
        strike_blend_thresh=strike_blend_thresh,
        setup_pos_thresh=setup_pos_thresh,
        dynamic_kick_foot=dynamic_kick_foot,
        robot_cfg=robot_cfg,
        ball_cfg=ball_cfg,
        plant_full_dist=plant_full_dist,
        plant_far_dist=plant_far_dist,
        plant_far_scale=plant_far_scale,
        restore_tracking_after_kick=restore_tracking_after_kick,
      ),
    )
    if disable_when_planted:
      scale = scale * (1.0 - _plant_latch_mask(env))
    return raw * scale


def feet_offset_x_for_kick(
  env: ManagerBasedRlEnv,
  command_name: str = "twist",
  target: float = 0.0,
  max_vel: float = 1.0,
  min_velocity_scale: float = 0.0,
  max_velocity_scale: float = 1.0,
  asset_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  arc_scale: float = 1.0,
  setup_scale: float = 0.2,
  strike_scale: float = 0.0,
  goal_command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.45,
  setup_exit_dist: float = 0.5,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  plant_full_dist: float | None = None,
  plant_far_dist: float = 2.0,
  plant_far_scale: float = 0.15,
  restore_tracking_after_kick: bool = True,
  disable_when_planted: bool = False,
) -> torch.Tensor:
  """Walk sagittal foot stagger; attenuated in Setup, off in Strike."""
  from mjlab.tasks.velocity import mdp as velocity_mdp

  raw = velocity_mdp.feet_offset_x_fixed(
    env,
    command_name=command_name,
    target=target,
    max_vel=max_vel,
    min_velocity_scale=min_velocity_scale,
    max_velocity_scale=max_velocity_scale,
    asset_cfg=asset_cfg,
  )
  scale = _kick_phase_walk_scale(
    env,
    **_pref_scale_kwargs(
      goal_command_name=goal_command_name,
      arc_scale=arc_scale,
      setup_scale=setup_scale,
      strike_scale=strike_scale,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
      plant_full_dist=plant_full_dist,
      plant_far_dist=plant_far_dist,
      plant_far_scale=plant_far_scale,
      restore_tracking_after_kick=restore_tracking_after_kick,
    ),
  )
  if disable_when_planted:
    scale = scale * (1.0 - _plant_latch_mask(env))
  return raw * scale


def feet_offset_y_for_kick(
  env: ManagerBasedRlEnv,
  command_name: str = "twist",
  target: float = 0.0,
  max_vel: float = 1.0,
  feet_distance_ref: float = 0.19,
  min_velocity_scale: float = 0.0,
  max_velocity_scale: float = 1.0,
  asset_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  arc_scale: float = 1.0,
  setup_scale: float = 0.2,
  strike_scale: float = 0.0,
  goal_command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.45,
  setup_exit_dist: float = 0.5,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  plant_full_dist: float | None = None,
  plant_far_dist: float = 2.0,
  plant_far_scale: float = 0.15,
  restore_tracking_after_kick: bool = True,
  disable_when_planted: bool = False,
) -> torch.Tensor:
  """Walk stance-width regularizer; attenuated in Setup, off in Strike."""
  from mjlab.tasks.velocity import mdp as velocity_mdp

  raw = velocity_mdp.feet_offset_y_fixed(
    env,
    command_name=command_name,
    target=target,
    max_vel=max_vel,
    feet_distance_ref=feet_distance_ref,
    min_velocity_scale=min_velocity_scale,
    max_velocity_scale=max_velocity_scale,
    asset_cfg=asset_cfg,
  )
  scale = _kick_phase_walk_scale(
    env,
    **_pref_scale_kwargs(
      goal_command_name=goal_command_name,
      arc_scale=arc_scale,
      setup_scale=setup_scale,
      strike_scale=strike_scale,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
      plant_full_dist=plant_full_dist,
      plant_far_dist=plant_far_dist,
      plant_far_scale=plant_far_scale,
      restore_tracking_after_kick=restore_tracking_after_kick,
    ),
  )
  if disable_when_planted:
    scale = scale * (1.0 - _plant_latch_mask(env))
  return raw * scale


def feet_distance_for_kick(
  env: ManagerBasedRlEnv,
  feet_distance_ref: float = 0.18,
  max_penalty: float = 0.1,
  wide_margin: float | None = None,
  command_name: str = "twist",
  side_walk_threshold: float = 0.1,
  side_walk_margin_scale: float = 3.0,
  asset_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  arc_scale: float = 1.0,
  setup_scale: float = 0.2,
  strike_scale: float = 0.0,
  goal_command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.45,
  setup_exit_dist: float = 0.5,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  plant_full_dist: float | None = None,
  plant_far_dist: float = 2.0,
  plant_far_scale: float = 0.15,
  restore_tracking_after_kick: bool = True,
) -> torch.Tensor:
  """Lateral foot spacing band; attenuated in Setup, off in Strike."""
  from mjlab.tasks.velocity import mdp as velocity_mdp

  raw = velocity_mdp.feet_distance_lateral(
    env,
    feet_distance_ref=feet_distance_ref,
    max_penalty=max_penalty,
    wide_margin=wide_margin,
    command_name=command_name,
    side_walk_threshold=side_walk_threshold,
    side_walk_margin_scale=side_walk_margin_scale,
    asset_cfg=asset_cfg,
  )
  scale = _kick_phase_walk_scale(
    env,
    **_pref_scale_kwargs(
      goal_command_name=goal_command_name,
      arc_scale=arc_scale,
      setup_scale=setup_scale,
      strike_scale=strike_scale,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
      plant_full_dist=plant_full_dist,
      plant_far_dist=plant_far_dist,
      plant_far_scale=plant_far_scale,
      restore_tracking_after_kick=restore_tracking_after_kick,
    ),
  )
  return raw * scale


def feet_yaw_diff_for_kick(
  env: ManagerBasedRlEnv,
  asset_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  arc_scale: float = 1.0,
  setup_scale: float = 0.2,
  strike_scale: float = 0.0,
  goal_command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.45,
  setup_exit_dist: float = 0.5,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  plant_full_dist: float | None = None,
  plant_far_dist: float = 2.0,
  plant_far_scale: float = 0.15,
  restore_tracking_after_kick: bool = True,
) -> torch.Tensor:
  """Feet yaw gap; attenuated in Setup, off in Strike."""
  from mjlab.tasks.velocity import mdp as velocity_mdp

  raw = velocity_mdp.feet_yaw_diff_l2(env, asset_cfg=asset_cfg)
  scale = _kick_phase_walk_scale(
    env,
    **_pref_scale_kwargs(
      goal_command_name=goal_command_name,
      arc_scale=arc_scale,
      setup_scale=setup_scale,
      strike_scale=strike_scale,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
      plant_full_dist=plant_full_dist,
      plant_far_dist=plant_far_dist,
      plant_far_scale=plant_far_scale,
      restore_tracking_after_kick=restore_tracking_after_kick,
    ),
  )
  return raw * scale


def feet_yaw_mean_for_kick(
  env: ManagerBasedRlEnv,
  asset_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  arc_scale: float = 1.0,
  setup_scale: float = 0.2,
  strike_scale: float = 0.0,
  goal_command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.45,
  setup_exit_dist: float = 0.5,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  plant_full_dist: float | None = None,
  plant_far_dist: float = 2.0,
  plant_far_scale: float = 0.15,
  restore_tracking_after_kick: bool = True,
) -> torch.Tensor:
  """Mean foot yaw vs base; attenuated in Setup, off in Strike."""
  from mjlab.tasks.velocity import mdp as velocity_mdp

  raw = velocity_mdp.feet_yaw_mean_l2(env, asset_cfg=asset_cfg)
  scale = _kick_phase_walk_scale(
    env,
    **_pref_scale_kwargs(
      goal_command_name=goal_command_name,
      arc_scale=arc_scale,
      setup_scale=setup_scale,
      strike_scale=strike_scale,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
      plant_full_dist=plant_full_dist,
      plant_far_dist=plant_far_dist,
      plant_far_scale=plant_far_scale,
      restore_tracking_after_kick=restore_tracking_after_kick,
    ),
  )
  return raw * scale


def knee_flex_cmd_excess_for_kick(
  env: ManagerBasedRlEnv,
  asset_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  q_threshold: float = 1.85,
  roll_gate: float = 0.15,
  action_name: str = "joint_pos",
  command_name: str | None = "twist",
  speed_ref: float = 0.0,
  arc_scale: float = 1.0,
  setup_scale: float = 0.25,
  strike_scale: float = 0.0,
  goal_command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.45,
  setup_exit_dist: float = 0.5,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  plant_full_dist: float | None = None,
  plant_far_dist: float = 2.0,
  plant_far_scale: float = 0.15,
  restore_tracking_after_kick: bool = True,
  disable_when_planted: bool = False,
) -> torch.Tensor:
  """Knee crouch-cmd tax; soft in Setup, off in Strike so the swing leg can flex."""
  from mjlab.tasks.velocity import mdp as velocity_mdp

  raw = velocity_mdp.knee_flex_cmd_excess(
    env,
    asset_cfg=asset_cfg,
    q_threshold=q_threshold,
    roll_gate=roll_gate,
    action_name=action_name,
    command_name=command_name,
    speed_ref=speed_ref,
  )
  scale = _kick_phase_walk_scale(
    env,
    **_pref_scale_kwargs(
      goal_command_name=goal_command_name,
      arc_scale=arc_scale,
      setup_scale=setup_scale,
      strike_scale=strike_scale,
      arc_radius=arc_radius,
      setup_enter_dist=setup_enter_dist,
      setup_exit_dist=setup_exit_dist,
      setup_behind=setup_behind,
      setup_lateral=setup_lateral,
      prefer_right_foot=prefer_right_foot,
      bearing_thresh=bearing_thresh,
      lateral_thresh=lateral_thresh,
      setup_blend_end=setup_blend_end,
      strike_blend_thresh=strike_blend_thresh,
      setup_pos_thresh=setup_pos_thresh,
      dynamic_kick_foot=dynamic_kick_foot,
      robot_cfg=robot_cfg,
      ball_cfg=ball_cfg,
      plant_full_dist=plant_full_dist,
      plant_far_dist=plant_far_dist,
      plant_far_scale=plant_far_scale,
      restore_tracking_after_kick=restore_tracking_after_kick,
    ),
  )
  if disable_when_planted:
    scale = scale * (1.0 - _plant_latch_mask(env))
  return raw * scale

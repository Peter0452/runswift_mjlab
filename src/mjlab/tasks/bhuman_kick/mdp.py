"""Actions, observations, rewards, terminations and startup randomization of
B-Human's K1 kick (Booster Gym ``envs/t1_ball.py``). Reward functions keep
the original ``_reward_<name>`` names (without the prefix) and formulas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch

from mjlab.managers.action_manager import ActionTerm, ActionTermCfg
from mjlab.managers.event_manager import RecomputeLevel, requires_model_fields
from mjlab.tasks.bhuman_kick.actuator import BHumanPdActuator
from mjlab.tasks.bhuman_kick.kick_command import (
  BHumanKickCommand,
  wrap,
  yaw_of,
)
from mjlab.tasks.bhuman_kick.robot import (
  BALL_MASS,
  BALL_RADIUS,
  LEG_JOINTS,
  TOE_NUB_HIDDEN_POS,
  TOE_NUB_Y,
)
from mjlab.utils.lab_api.math import quat_apply_inverse

if TYPE_CHECKING:
  from mjlab.entity import Entity
  from mjlab.envs import ManagerBasedRlEnv
  from mjlab.sensor import ContactSensor

_PI = torch.pi


def _geoms(entity: Entity, pattern: str) -> torch.Tensor:
  local, _ = entity.find_geoms((pattern,))
  ids = entity.indexing.geom_ids
  return ids[torch.tensor(local, device=ids.device)].long()


def _bodies(entity: Entity, names: tuple[str, ...]) -> torch.Tensor:
  local, _ = entity.find_bodies(names, preserve_order=True)
  ids = entity.indexing.body_ids
  return ids[torch.tensor(local, device=ids.device)].long()


def kick_cmd(env: ManagerBasedRlEnv) -> BHumanKickCommand:
  term = env.command_manager.get_term("kick")
  assert isinstance(term, BHumanKickCommand)
  return term


##
# Action: 12 leg position offsets + gait frequency.
##


@dataclass(kw_only=True)
class BHumanKickActionCfg(ActionTermCfg):
  entity_name: str = "robot"
  clip_actions: float = 2.0
  action_scale: float = 1.0
  action_frequence_limit: tuple[float, float] = (-0.5, 0.5)
  target_frequence: float = 1.5

  def build(self, env: ManagerBasedRlEnv) -> BHumanKickAction:
    return BHumanKickAction(self, env)


class BHumanKickAction(ActionTerm):
  """``T1_Ball.step`` pre-physics: targets = default + offset + action, clipped
  to the joint limits. The gait clock runs with the *previous* step's
  frequency action, as in the original."""

  cfg: BHumanKickActionCfg

  def __init__(self, cfg: BHumanKickActionCfg, env: ManagerBasedRlEnv):
    super().__init__(cfg, env)
    n, dev = self.num_envs, self.device
    names = list(self._entity.joint_names)
    self.leg_ids = torch.tensor([names.index(j) for j in LEG_JOINTS], device=dev)
    self.actions_raw = torch.zeros(n, 13, device=dev)
    self.actions = torch.zeros(n, 13, device=dev)
    self.last_actions = torch.zeros(n, 13, device=dev)
    self.actions_gait = torch.zeros(n, device=dev)
    self.dof_targets = torch.zeros(n, 12, device=dev)
    self._actuators = [
      a for a in self._entity.actuators if isinstance(a, BHumanPdActuator)
    ]

  @property
  def action_dim(self) -> int:
    return 13

  @property
  def raw_action(self) -> torch.Tensor:
    return self.actions_raw

  def process_actions(self, actions: torch.Tensor) -> None:
    cfg = self.cfg
    cmd = kick_cmd(self._env)
    self.actions_raw[:] = actions
    lo, hi = cfg.action_frequence_limit
    self.actions_gait[:] = self.actions[:, -1].clip(lo, hi) + cfg.target_frequence
    self.last_actions[:] = self.actions
    self.actions[:] = actions.clip(-cfg.clip_actions, cfg.clip_actions)
    lim = cmd.dof_pos_limits
    self.dof_targets[:] = torch.clip(
      cmd.default_dof_pos
      + cmd.dof_pos_offset
      + cfg.action_scale * self.actions[:, :12],
      min=lim[:, 0],
      max=lim[:, 1],
    )
    for a in self._actuators:
      a.sync_substep()
    decap = getattr(self._env, "decap", None)
    if decap is not None:
      decap.refresh()
      decap.advance()

  def apply_actions(self) -> None:
    targets = self.dof_targets
    decap = getattr(self._env, "decap", None)
    if decap is not None and decap.factor > 0.0 and bool(decap.active.any()):
      # APEX DecAP: blend toward the kick clip and carry the base along it.
      joint_pos = self._entity.data.joint_pos[:, self.leg_ids]
      targets = decap.blend(self.dof_targets, joint_pos)
      decap.write_root(self._entity)
    self._entity.set_joint_position_target(targets, joint_ids=self.leg_ids)

  def reset(self, env_ids: torch.Tensor | slice | None = None) -> None:
    del env_ids  # Booster Gym keeps the action buffers across resets.


##
# Observations (59 actor, 16 privileged; the critic sees both).
##


def actor_obs(env: ManagerBasedRlEnv) -> torch.Tensor:
  return kick_cmd(env).actor_obs()


def critic_obs(env: ManagerBasedRlEnv) -> torch.Tensor:
  return kick_cmd(env).critic_obs()


##
# Terminations.
##


def terminated(env: ManagerBasedRlEnv) -> torch.Tensor:
  return kick_cmd(env).terminated


def time_out(env: ManagerBasedRlEnv) -> torch.Tensor:
  return kick_cmd(env).time_out_buf


##
# Rewards.
##


def _swing(c: BHumanKickCommand) -> tuple[torch.Tensor, torch.Tensor]:
  period = c.cfg.swing_period
  walking = c.action_term.actions_gait > 1.0e-8
  left = ((c.gait_process - 0.25).abs() < 0.5 * period) & walking
  right = ((c.gait_process - 0.75).abs() < 0.5 * period) & walking
  return left, right


def terminate(env: ManagerBasedRlEnv) -> torch.Tensor:
  return (kick_cmd(env).terminate_counter > 0).float()


def base_height(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  h = c.base_pos[:, 2] - c.terrain_height(c.base_pos)
  return (h - c.cfg.base_height_target).square()


def collision(
  env: ManagerBasedRlEnv, sensor_name: str = "body_contact"
) -> torch.Tensor:
  sensor: ContactSensor = env.scene[sensor_name]
  force = sensor.data.force
  assert force is not None
  return (force.norm(dim=-1) > 1.0).sum(dim=-1).float()


def lin_vel_z(env: ManagerBasedRlEnv) -> torch.Tensor:
  return kick_cmd(env).filtered_lin_vel[:, 2].square()


def ang_vel_xy(env: ManagerBasedRlEnv) -> torch.Tensor:
  return kick_cmd(env).base_ang_vel[:, :2].square().sum(dim=-1)


def orientation(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  ratio = torch.where(c.ball_kicked_counter > 0, 2.0, 1.0)
  return c.projected_gravity[:, :2].square().sum(dim=-1) * ratio


def torques(env: ManagerBasedRlEnv) -> torch.Tensor:
  return kick_cmd(env).torques.square().sum(dim=-1)


def dof_vel(env: ManagerBasedRlEnv) -> torch.Tensor:
  return kick_cmd(env).dof_vel.square().sum(dim=-1)


def dof_acc(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  return ((c.last_dof_vel - c.dof_vel) / c.dt).square().sum(dim=-1)


def root_acc(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  vel = torch.cat((c.root_lin_vel_w, c.root_ang_vel_w), -1)
  return ((c.last_root_vel - vel) / c.dt).square().sum(dim=-1)


def action_rate(env: ManagerBasedRlEnv) -> torch.Tensor:
  a = kick_cmd(env).action_term
  return (a.last_actions - a.actions).square().sum(dim=-1)


def dof_pos_limits(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  lo, hi = c.dof_pos_limits[:, 0], c.dof_pos_limits[:, 1]
  margin = 0.5 * (1 - c.cfg.soft_dof_pos_limit) * (hi - lo)
  out = (c.dof_pos < lo + margin) | (c.dof_pos > hi - margin)
  return out.float().sum(dim=-1)


def actions_in_range(env: ManagerBasedRlEnv) -> torch.Tensor:
  a = kick_cmd(env).action_term
  raw = a.actions_raw[:, :-1]
  clip = a.cfg.clip_actions
  return (raw - raw.clip(-clip, clip)).abs().sum(dim=-1)


def action_pos_limits(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  target = c.default_dof_pos + c.action_term.actions[:, :12]
  lo, hi = c.dof_pos_limits[:, 0], c.dof_pos_limits[:, 1]
  return ((target < lo) | (target > hi)).float().sum(dim=-1)


def torque_limits(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  return (c.torques.abs() - c.torque_limits).clip(min=0.0).sum(dim=-1)


def torque_tiredness(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  return (c.torques / c.torque_limits).square().clip(max=1.0).sum(dim=-1)


def power(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  return (c.torques * c.dof_vel).clip(min=0.0).sum(dim=-1)


def feet_slip(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  v = ((c.last_feet_pos - c.feet_pos) / c.dt).square().sum(dim=-1)
  return (v * c.feet_contact.float()).sum(dim=-1) * (c.episode_length_buf > 1).float()


def feet_yaw_diff(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  return wrap(c.feet_yaw[:, 1] - c.feet_yaw[:, 0]).square()


def feet_yaw_mean(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  fy = c.feet_yaw
  mean = fy.mean(dim=-1) + _PI * ((fy[:, 1] - fy[:, 0]).abs() > _PI).float()
  return wrap(yaw_of(c.base_quat) - mean).square()


def feet_roll(env: ManagerBasedRlEnv) -> torch.Tensor:
  return kick_cmd(env).feet_roll.square().sum(dim=-1)


def feet_distance(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  yaw = yaw_of(c.base_quat)
  fp = c.feet_pos
  d = (
    torch.cos(yaw) * (fp[:, 1, 1] - fp[:, 0, 1])
    - torch.sin(yaw) * (fp[:, 1, 0] - fp[:, 0, 0])
  ).abs()
  return (c.cfg.feet_distance_ref - d).clip(0.0, 0.1)


def feet_swing(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  left, right = _swing(c)
  air_l = left & ~c.feet_contact[:, 0]
  air_r = right & ~c.feet_contact[:, 1]
  cnt = c.feet_swing_counter
  cnt[:, 0] += air_l.float() + (~air_l).float() * -0.2
  cnt[:, 1] += air_r.float() + (~air_r).float() * -0.2
  cnt.clamp_(min=0.0)
  return (air_l & (cnt[:, 0] < 7.1)).float() + (air_r & (cnt[:, 1] < 7.1)).float()


def ground_pressure(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  touch = ~c.last_feet_contact & c.feet_contact
  vz = (c.feet_vel_filtered[:, :, 2] + 0.2).clamp(max=0.0)
  return -(touch.float() * vz).sum(dim=-1)


def gait_phase_factor(env: ManagerBasedRlEnv) -> torch.Tensor:
  a = kick_cmd(env).action_term
  f = a.actions[:, -1]
  lo, hi = a.cfg.action_frequence_limit
  return (f - f.clamp(lo, hi)).square()


def feet_height(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  left, right = _swing(c)
  ref = c.cfg.feet_height_ref
  z = c.feet_pos[:, :, 2]
  dl = (z[:, 0] - z[:, 1] - ref).clip(max=0.0)
  dr = (z[:, 1] - z[:, 0] - ref).clip(max=0.0)
  le = (~left).float() + left.float() * torch.exp(-dl.square() / 0.0005)
  re = (~right).float() + right.float() * torch.exp(-dr.square() / 0.0005)
  return 2 - le - re


def _vision_cone(c: BHumanKickCommand) -> torch.Tensor:
  bir = quat_apply_inverse(c.base_quat_z, c.ball_state[:, :3] - c.base_pos)
  angle = torch.atan2(bir[:, 1], bir[:, 0])
  return torch.exp(-angle.square() / c.cfg.ball_walk_vision_sigma)


def ball_vision_cone(env: ManagerBasedRlEnv) -> torch.Tensor:
  return (_vision_cone(kick_cmd(env)) - 0.5) * 2.0


def ball_kick_direction(env: ManagerBasedRlEnv) -> torch.Tensor:
  return kick_cmd(env).ball_kick_direction_reward


def ball_kick_velocity(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  cfg = c.cfg
  # Expected launch speed from B-Human's BallPhysics (rolling friction model).
  expected = 1.4142135623 * torch.sqrt(cfg.ball_friction * c.range)
  diff = expected - c.ball_velocity_norm_at_kick
  started = (c.ball_kicked_counter > cfg.ball_kicked_start_counter).float()
  reward = torch.exp(-diff.square() / cfg.ball_velocity_range_sigma_scale) * started
  d = c.ball_kick_direction_reward
  return torch.where(d < 0, d * 0.1 * c.ball_velocity_norm_at_kick, reward * d)


def ball_kick_velocity_strong(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  d = c.ball_kick_direction_reward
  reward = c.ball_velocity_norm_at_kick * torch.where(d < 0, d * 0.1, d)
  return reward * c.flag_is_strong_kick.float()


def _walk_towards_ball(c: BHumanKickCommand) -> torch.Tensor:
  target = c.helper_walk_target()
  target_angle = torch.atan2(target[:, 1], target[:, 0])
  walk_angle = torch.atan2(c.filtered_lin_vel[:, 1], c.filtered_lin_vel[:, 0])
  diff = wrap(target_angle - walk_angle)
  far = (torch.exp(-diff.square() / c.cfg.ball_walk_direction_sigma) - 0.5) * 2.0
  return torch.where(far < 0, -1.0, far)


def ball_walk_speed(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  cfg = c.cfg
  allow_positive = torch.where(c.ball_kick_direction_reward < 0, 0.0, 1.0)
  vel = c.filtered_lin_vel[:, :3].clone()
  vel[:, 2] = c.filtered_ang_vel[:, 2]
  too_much_rotation = 1.0 - ((vel[:, 2].abs() - 4.0) / 0.5).clip(min=0.0)

  vision = ball_vision_cone(env)
  min_rot_negative = torch.min(
    -((vel[:, 2].abs() - 0.3).clip(0.0, 1.0)), vision.clip(max=0.0)
  )
  # Verbatim from Booster Gym, including clip(min=1, max=0) (always 0) and the
  # "- 0.4 / 0.3" precedence.
  vision_scaling = 1.0 - ((vision + 0.5) / 0.25).clip(min=1.0, max=0.0)
  ball_dist = c.ball_pos.norm(dim=-1)
  max_rot_positive = vision_scaling + (1.0 - vision_scaling) * (
    0.25 + 0.75 * (ball_dist - 0.4 / 0.3).clip(0.0, 1.0)
  )
  rotation_sign = torch.where(
    vel[:, 2] * c.ball_pos[:, 1] >= 0.0,
    allow_positive * max_rot_positive,
    min_rot_negative,
  )

  direction = _walk_towards_ball(c)
  direction = direction * torch.where(
    direction < 0,
    (vision_scaling * 3.0 + 1.0) * cfg.negative_walk_speed_factor,
    1.0,
  )
  direction = torch.where(
    c.ball_close_to_kick_pose < 1,
    direction.clip(min=-1.0),
    direction * allow_positive,
  )

  vel[:, 0] = vel[:, 0].abs()
  vel[:, 1] = vel[:, 1].abs()
  vel[:, 2] = vel[:, 2].abs() * rotation_sign
  vel[:, 2] = vel[:, 2] * torch.where(vel[:, 2] < 0, 1.0, too_much_rotation)

  ratio = torch.where(
    (c.ball_close_to_kick_pose < 1.0) & (c.ball_pos[:, :2].norm(dim=-1) < 0.6),
    0.0,
    1.0,
  )
  cap = cfg.clip_max_speed_near_ball * (1.0 - ratio) + 3 * ratio
  vel[:, 0] = torch.where(direction < 0, vel[:, 0], vel[:, 0].abs().clip(max=cap))
  vel[:, 1] = torch.where(direction < 0, vel[:, 1], vel[:, 1].abs().clip(max=cap))
  rot_cap = 3 * ((ratio - 0.5) * 2).clip(min=0.0)
  vel[:, 2] = torch.where(
    vel[:, 2] < 0, vel[:, 2], torch.minimum(vel[:, 2].abs(), rot_cap)
  )
  return vel[:, :2].norm(dim=-1) * direction + vel[:, 2]


def ball_walk_target_overshoot(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  return (
    (c.ball_walk_target_overshoot.clip(min=0).float() / 10.0)
    * (1.0 - ((c.ball_velocity_norm - 0.3) / 0.7).clip(0.0, 1.0))
    * (1.0 - (c.ball_kicked_counter > 0).float())
  )


def ball_sole_yaw(env: ManagerBasedRlEnv) -> torch.Tensor:
  c = kick_cmd(env)
  pose = c.inside_kick_pose_counter.square()
  pose[c.flag_allow_deviation] = 1
  return pose * c.kick_sole_yaw_ratio * (c.ball_kick_direction_reward > 0).float()


##
# Startup randomization (``_process_rigid_body_props`` / ``_shape_props``,
# ball asset, DOF friction).
##


@requires_model_fields(
  "body_mass", "body_ipos", "body_inertia", recompute=RecomputeLevel.set_const
)
def bhuman_body_dr(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  base_com: float = 0.1,
  base_mass: tuple[float, float] = (0.8, 1.2),
  other_com: float = 0.005,
  other_mass: tuple[float, float] = (0.98, 1.02),
) -> None:
  """Trunk COM +-``base_com`` and mass x``base_mass`` (welded head and arms
  scale with it, as Isaac Gym merges them into the trunk), other links a
  little. The raw U(0, 1) samples go to the critic (``base_mass_scaled``)."""
  robot: Entity = env.scene["robot"]
  dev = env.device
  ids = (
    torch.arange(env.num_envs, device=dev)
    if env_ids is None
    else env_ids.to(dev, dtype=torch.long)
  )
  n = len(ids)
  model = env.sim.model
  bodies = robot.indexing.body_ids.long()
  names = list(robot.body_names)
  welded_parents = {"Head_1", "Head_2", "Left_Arm_1", "Left_Arm_2", "Left_Arm_3"}
  welded_parents |= {"left_hand_link", "right_hand_link"}
  welded_parents |= {"Right_Arm_1", "Right_Arm_2", "Right_Arm_3"}
  trunk = [i for i, b in enumerate(names) if b == "Trunk"]
  merged = trunk + [i for i, b in enumerate(names) if b in welded_parents]
  other = [i for i in range(len(names)) if i not in merged]
  m_t = bodies[trunk]
  m_m = bodies[merged]
  m_o = bodies[other]
  u = torch.rand(n, 4, device=dev)
  com = -base_com + 2 * base_com * u[:, :3]
  scale = base_mass[0] + (base_mass[1] - base_mass[0]) * u[:, 3]
  merged_mass = model.body_mass[ids[:, None], m_m[None, :]].sum(dim=-1)
  trunk_mass = model.body_mass[ids[:, None], m_t[None, :]].sum(dim=-1)
  # Shift the trunk COM so the merged body's COM moves by ``com``.
  shift = com * (merged_mass / trunk_mass).unsqueeze(-1)
  model.body_ipos[ids[:, None], m_t[None, :]] += shift.unsqueeze(1)
  model.body_mass[ids[:, None], m_m[None, :]] *= scale[:, None]
  model.body_inertia[ids[:, None], m_m[None, :]] *= scale[:, None, None]
  ko = len(m_o)
  model.body_ipos[ids[:, None], m_o[None, :]] += (
    torch.rand(n, ko, 3, device=dev) * 2 - 1
  ) * other_com
  s = other_mass[0] + (other_mass[1] - other_mass[0]) * torch.rand(n, ko, device=dev)
  model.body_mass[ids[:, None], m_o[None, :]] *= s
  model.body_inertia[ids[:, None], m_o[None, :]] *= s.unsqueeze(-1)
  kick_cmd(env).base_mass_scaled[ids] = u


@requires_model_fields("geom_friction", "geom_pos")
def bhuman_feet_dr(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  friction: tuple[float, float] = (0.3, 1.0),
) -> None:
  """Sole friction per env (Isaac Gym used the terrain patch's 0.3-1.0) and
  the robot variant: toe nub left, right, or none (``env_id % 3``)."""
  robot: Entity = env.scene["robot"]
  dev = env.device
  ids = (
    torch.arange(env.num_envs, device=dev)
    if env_ids is None
    else env_ids.to(dev, dtype=torch.long)
  )
  n = len(ids)
  model = env.sim.model
  soles = _geoms(robot, r".*_(sole|toe)_collision")
  f = friction[0] + (friction[1] - friction[0]) * torch.rand(n, device=dev)
  model.geom_friction[ids[:, None], soles[None, :], 0] = f[:, None]
  toes = _geoms(robot, r".*_toe_collision")
  variant = ids % 3
  pos = torch.tensor(TOE_NUB_HIDDEN_POS, device=dev).repeat(n, 1)
  for v, side in ((1, "left"), (2, "right")):
    sel = variant == v
    pos[sel] = torch.tensor((0.11, TOE_NUB_Y[side], 0.002), device=dev)
  model.geom_pos[ids[:, None], toes[None, :]] = pos.unsqueeze(1)


@requires_model_fields(
  "geom_size",
  "geom_rbound",
  "geom_aabb",
  "body_mass",
  "body_inertia",
  recompute=RecomputeLevel.set_const,
)
def bhuman_ball_dr(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  radius: tuple[float, float] = (-0.01, 0.01),
  mass: tuple[float, float] = (-0.01, 0.01),
) -> None:
  """Ball radius / mass per env; rare 100x "heavy" balls (``heavy_ball``)."""
  dev = env.device
  ids = (
    torch.arange(env.num_envs, device=dev)
    if env_ids is None
    else env_ids.to(dev, dtype=torch.long)
  )
  n = len(ids)
  r = BALL_RADIUS + radius[0] + (radius[1] - radius[0]) * torch.rand(n, device=dev)
  m = BALL_MASS + mass[0] + (mass[1] - mass[0]) * torch.rand(n, device=dev)
  cmd = kick_cmd(env)
  heavy = torch.rand(n, device=dev) < cmd.cfg.heavy_ball
  m = torch.where(heavy, m * 100, m)
  cmd.heavy_ball[ids] = heavy
  set_ball_size_mass(env, ids, r, m)


def set_ball_size_mass(
  env: ManagerBasedRlEnv, ids: torch.Tensor, r: torch.Tensor, m: torch.Tensor
) -> None:
  """Ball collision radius and mass (solid sphere) per env. The caller
  recomputes model constants (``bhuman_ball_dr``'s event does it)."""
  ball: Entity = env.scene["ball"]
  model = env.sim.model
  g = _geoms(ball, "ball_collision")
  b = _bodies(ball, ("ball",))
  model.geom_size[ids[:, None], g[None, :], 0] = r[:, None]
  model.geom_rbound[ids[:, None], g[None, :]] = r[:, None]
  model.geom_aabb[ids[:, None], g[None, :], 1] = r[:, None, None].expand(-1, len(g), 3)
  model.body_mass[ids[:, None], b[None, :]] = m[:, None]
  inertia = 0.4 * m * r * r
  model.body_inertia[ids[:, None], b[None, :]] = inertia[:, None, None].expand(
    -1, len(b), 3
  )


def bhuman_joint_friction(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  friction: tuple[float, float] = (0.0, 2.0),
) -> None:
  """Coulomb-like DOF friction subtracted from the PD torque (0-2 Nm)."""
  robot: Entity = env.scene["robot"]
  ids = slice(None) if env_ids is None else env_ids
  for a in robot.actuators:
    if isinstance(a, BHumanPdActuator):
      lo, hi = friction
      f = a.friction[ids]
      a.friction[ids] = lo + (hi - lo) * torch.rand_like(f)

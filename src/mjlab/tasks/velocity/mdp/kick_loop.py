"""Stage 3: approach, kick, recover, find the ball again and kick again.

One policy with the approach stage's 83-dim actor layout. ``KickLoopCommand``
extends the approach command with kick events, goals and an AMP style gate.
Events are detected at the end of a step and paid by the rewards of the next
step, so each event pays exactly once.

A goal is reached when a kicked ball passes within ``goal_tolerance`` of the
target. A new target is then placed 1–10 m from the ball in a random
direction, so every kick starts from a fresh approach.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch

from mjlab.entity import Entity
from mjlab.tasks.velocity.mdp.approach import (
  STAND_DISTANCE,
  WALK_COMMAND_SPEED,
  YAW_ALIGN_LIMIT,
  ApproachYawCommand,
  ApproachYawCommandCfg,
  _command,
  _current,
)

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv


# Short / medium / long kicks; the kick-range one-hot uses the same edges.
TARGET_BINS = ((1.0, 4.0), (4.0, 8.0), (8.0, 10.0))
RANGE_EDGES = (4.0, 8.0)
# Within this distance the robot should line up and kick quickly.
NEAR_DISTANCE = 1.5
# Body-heading shaping ramps in from here to the stand distance.
HEADING_FAR = 2.0
# A touch is a kick if the ball leaves at ≥ KICK_MIN_SPEED after a jump.
KICK_MIN_SPEED = 1.0
KICK_MIN_JUMP = 0.8
# Ball speed that earns full kick_vel; exact speed comes later.
KICK_VEL_REF = 3.0
# Width of the sharp part of the kick-direction score (rad, ~20°).
KICK_AIM_SIGMA = 0.35
DOUBLE_TOUCH_WINDOW = 0.5
POST_KICK_WINDOW = 2.0
# After a kick, the near-ball time does not count for this long.
STYLE_OFF_AFTER_KICK = 1.0
# Style is judged everywhere except the kick itself: within this distance in
# the wedge (about to kick) and for STYLE_KICK_WINDOW after a kick. Gating the
# whole 1.5 m zone left style off ~60 % of the time and the motion drifted
# (joint limits, falls) in stage3_v8–v10.
STYLE_OFF_DISTANCE = 0.6
STYLE_KICK_WINDOW = 0.7
SPEED_SMOOTH_TAU = 0.3
# The speed limit is waived this long after a kick (the swing moves the base).
SPEED_LIMIT_GRACE = 0.5
# Measured on a plane with the approach ball: roll distance ≈ v² / (2·0.95).
BALL_ROLL_DECEL = 0.95
SINGLE_SUPPORT_MAX = 0.8
BALL_REST_SPEED = 0.1
MAX_TARGET_DISTANCE = 10.0
# A real kick: support nearly still, kicking foot swinging fast relative to
# the body. v13/v16 "kicked" at 0.9 m/s body speed with the foot only 1 m/s
# faster than the body: running into the ball, not kicking it.
KICK_BODY_SPEED_SCALE = 0.4
KICK_SWING_MIN = 1.0
KICK_SWING_SPAN = 1.5


def heading_potential(
  dist: torch.Tensor,
  yaw_error: torch.Tensor,
  far: float = HEADING_FAR,
  near: float = STAND_DISTANCE,
) -> torch.Tensor:
  """-w(d)·|yaw error|, with w ramping from 0 at ``far`` to 1 at ``near``.

  Paid as a difference between steps, so the episode total depends only on
  the start and end states: entering the ramp misaligned earns nothing, and
  closing in while misaligned costs reward.
  """
  w = ((far - dist) / (far - near)).clamp(0.0, 1.0)
  return -w * yaw_error.abs()


def required_kick_speed(
  distance: torch.Tensor, decel: float = BALL_ROLL_DECEL
) -> torch.Tensor:
  """Launch speed that rolls the ball ``distance`` before it stops."""
  return torch.sqrt(2.0 * decel * distance.clamp(min=0.0))


def kick_quality_score(
  body_speed: torch.Tensor,
  foot_rel_speed: torch.Tensor,
  body_scale: float = KICK_BODY_SPEED_SCALE,
  swing_min: float = KICK_SWING_MIN,
  swing_span: float = KICK_SWING_SPAN,
) -> torch.Tensor:
  """1 for a planted kick with a fast swing, ~0 for running into the ball.

  exp(-(body/0.4)²) · clamp((foot_rel - 1.0)/1.5, 0, 1): 1.0 still, 0.005 at
  0.9 m/s body speed; 0 for a walking step (foot ~1 m/s over the body), 1 at
  2.5 m/s.
  """
  still = torch.exp(-torch.square(body_speed / body_scale))
  swing = ((foot_rel_speed - swing_min) / swing_span).clamp(0.0, 1.0)
  return still * swing


def goal_tolerance(distance: torch.Tensor) -> torch.Tensor:
  """How close a kicked ball must pass to the target: 25 %, 0.5–1.5 m."""
  return (0.25 * distance).clamp(0.5, 1.5)


def classify_touch(
  touch: torch.Tensor,
  prev_touch: torch.Tensor,
  ball_speed: torch.Tensor,
  prev_ball_speed: torch.Tensor,
  time_since_kick: torch.Tensor,
  min_speed: float = KICK_MIN_SPEED,
  min_jump: float = KICK_MIN_JUMP,
  double_window: float = DOUBLE_TOUCH_WINDOW,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
  """Split foot-ball contact into (kick, double touch, push).

  Kick: contact this or last step that launched the ball, outside the
  double-touch window. Double touch: a new contact inside that window.
  Push: contact that does not launch the ball, outside the window.
  """
  launched = (ball_speed >= min_speed) & (ball_speed - prev_ball_speed >= min_jump)
  in_window = time_since_kick < double_window
  kick = (touch | prev_touch) & launched & ~in_window
  double = touch & ~prev_touch & in_window
  push = touch & ~launched & ~in_window
  return kick, double, push


def _found(env: ManagerBasedRlEnv, sensor_name: str) -> torch.Tensor:
  found = env.scene[sensor_name].data.found
  if found is None:
    return torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
  return found.reshape(env.num_envs, -1).amax(dim=-1) > 0


class KickLoopCommand(ApproachYawCommand):
  """Approach command plus kick events, goals and the AMP style gate."""

  cfg: KickLoopCommandCfg

  def __init__(self, cfg: KickLoopCommandCfg, env: ManagerBasedRlEnv):
    super().__init__(cfg, env)
    n, dev = self.num_envs, self.device

    def flag() -> torch.Tensor:
      return torch.zeros(n, dtype=torch.bool, device=dev)

    def zeros() -> torch.Tensor:
      return torch.zeros(n, device=dev)

    self.kick_event = flag()
    self.double_touch_event = flag()
    self.push = flag()
    self.body_touch = flag()
    self.goal_event = flag()
    self.lined_up_event = flag()
    self.lined_up_latched = flag()
    self.kicked_since_target = flag()
    self.near_pending = flag()
    self.prev_touch = flag()
    self.time_since_kick = torch.full((n,), 1.0e3, device=dev)
    self.near_time = zeros()
    # Near-ball time that preceded the latest kick (near_time resets on kicks).
    self.kick_near_time = zeros()
    self.kick_speed = zeros()
    self.kick_cos = zeros()
    self.kick_speed_req = zeros()
    self.prev_ball_speed = zeros()
    self.goal_tol = torch.ones(n, device=dev)
    self.prev_heading_phi = zeros()
    self.smoothed_vel = torch.zeros(n, 3, device=dev)
    self.style_gate = torch.ones(n, device=dev)
    # The AMP runner reads this to switch style off around kicks only.
    env.amp_style_gate = self.style_gate  # ty: ignore[unresolved-attribute]

    feet, _ = self.robot.find_bodies(
      ("left_foot_link", "right_foot_link"), preserve_order=True
    )
    self._feet_ids = list(feet)
    self.prev_foot_rel = torch.zeros(n, 2, device=dev)
    self.kick_quality = zeros()
    # Quality of the kick that last launched the ball (goal credit).
    self.last_kick_quality = zeros()
    self.kick_body_speed = zeros()
    self.kick_foot_rel = zeros()
    self._kick_quality_sum = zeros()
    self._kicks = zeros()
    self._goals = zeros()
    self._double_touches = zeros()
    self._push_time = zeros()
    self._kick_speed_sum = zeros()
    self._kick_dir_err_sum = zeros()
    self._near_time_sum = zeros()
    for name in (
      "kicks",
      "goals",
      "double_touches",
      "push_time",
      "kick_speed",
      "kick_quality",
      "kick_dir_err",
      "near_time_to_kick",
    ):
      self.metrics[name] = zeros()

  def _update_metrics(self) -> None:
    super()._update_metrics()
    kicks = self._kicks.clamp(min=1.0)
    self.metrics["kicks"][:] = self._kicks
    self.metrics["goals"][:] = self._goals
    self.metrics["double_touches"][:] = self._double_touches
    self.metrics["push_time"][:] = self._push_time
    self.metrics["kick_speed"][:] = self._kick_speed_sum / kicks
    self.metrics["kick_quality"][:] = self._kick_quality_sum / kicks
    self.metrics["kick_dir_err"][:] = self._kick_dir_err_sum / kicks
    self.metrics["near_time_to_kick"][:] = self._near_time_sum / kicks

  def _resample_command(self, env_ids: torch.Tensor) -> None:
    super()._resample_command(env_ids)
    for buf in (
      self.kick_event,
      self.double_touch_event,
      self.push,
      self.body_touch,
      self.goal_event,
      self.lined_up_event,
      self.lined_up_latched,
      self.kicked_since_target,
      self.near_pending,
      self.prev_touch,
    ):
      buf[env_ids] = False
    for buf in (
      self.near_time,
      self.kick_near_time,
      self.kick_speed,
      self.kick_cos,
      self.kick_quality,
      self.last_kick_quality,
      self.kick_body_speed,
      self.kick_foot_rel,
      self._kick_quality_sum,
      self.kick_speed_req,
      self.prev_ball_speed,
      self._kicks,
      self._goals,
      self._double_touches,
      self._push_time,
      self._kick_speed_sum,
      self._kick_dir_err_sum,
      self._near_time_sum,
    ):
      buf[env_ids] = 0.0
    self.time_since_kick[env_ids] = 1.0e3
    self.smoothed_vel[env_ids] = 0.0
    self.style_gate[env_ids] = 1.0
    self.goal_tol[env_ids] = goal_tolerance(self.target_dist[env_ids])

  def _update_command(self) -> None:
    dt = self._env.step_dt
    ball_xy = self.ball.data.root_link_pos_w[:, :2]
    ball_vel = self.ball.data.root_link_lin_vel_w[:, :2]
    ball_speed = ball_vel.norm(dim=-1)
    touch = _found(self._env, self.cfg.feet_ball_sensor)
    self.body_touch[:] = _found(self._env, self.cfg.body_ball_sensor)
    self.time_since_kick += dt

    kick, double, push = classify_touch(
      touch, self.prev_touch, ball_speed, self.prev_ball_speed, self.time_since_kick
    )
    to_target = self.target_w - ball_xy
    target_dist = to_target.norm(dim=-1)
    cos = (ball_vel * to_target).sum(dim=-1) / (ball_speed * target_dist).clamp(
      min=1.0e-6
    )
    self.kick_event[:] = kick
    self.double_touch_event[:] = double
    self.push[:] = push
    self.kick_speed[:] = torch.where(kick, ball_speed, self.kick_speed)
    # Body and kicking-foot motion at the kick (foot speed: the larger of this
    # and the last step, since the impact slows the foot).
    data = self.robot.data
    base_v = data.root_link_lin_vel_w[:, :2]
    foot_rel = (
      data.body_link_lin_vel_w[:, self._feet_ids, :2] - base_v.unsqueeze(1)
    ).norm(dim=-1)
    found = self._env.scene[self.cfg.feet_ball_sensor].data.found
    if found is not None:
      which = (found.reshape(self.num_envs, -1)[:, :2] > 0).float().argmax(dim=-1)
    else:
      which = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
    rows = torch.arange(self.num_envs, device=self.device)
    swing = torch.maximum(foot_rel, self.prev_foot_rel)[rows, which]
    body = base_v.norm(dim=-1)
    quality = kick_quality_score(body, swing)
    self.kick_quality[:] = torch.where(kick, quality, self.kick_quality)
    self.last_kick_quality[:] = torch.where(kick, quality, self.last_kick_quality)
    self.kick_body_speed[:] = torch.where(kick, body, self.kick_body_speed)
    self.kick_foot_rel[:] = torch.where(kick, swing, self.kick_foot_rel)
    self._kick_quality_sum += torch.where(kick, quality, 0.0)
    self.prev_foot_rel[:] = foot_rel
    self.kick_cos[:] = torch.where(kick, cos, self.kick_cos)
    self.kick_speed_req[:] = torch.where(
      kick,
      required_kick_speed(target_dist, self.cfg.ball_roll_decel),
      self.kick_speed_req,
    )
    self._kicks += kick.float()
    self._double_touches += double.float()
    self._push_time += push.float() * dt
    self._kick_speed_sum += torch.where(kick, ball_speed, 0.0)
    self._kick_dir_err_sum += torch.where(kick, torch.acos(cos.clamp(-1.0, 1.0)), 0.0)
    self._near_time_sum += torch.where(kick, self.near_time, 0.0)
    self.kick_near_time[:] = torch.where(kick, self.near_time, self.kick_near_time)
    self.near_time[:] = torch.where(kick, 0.0, self.near_time)
    self.time_since_kick[:] = torch.where(kick, 0.0, self.time_since_kick)
    self.kicked_since_target |= kick
    self.lined_up_latched &= ~kick
    self.prev_touch[:] = touch
    self.prev_ball_speed[:] = ball_speed

    # Goal, or a kicked ball resting out of range: new target from the ball.
    # Done before the approach update so every "prev" value uses the new target.
    reached = self.kicked_since_target & (target_dist <= self.goal_tol)
    resting_far = (
      (ball_speed < BALL_REST_SPEED)
      & (self.time_since_kick > 1.0)
      & (target_dist > self.cfg.max_target_distance)
    )
    self.goal_event[:] = reached
    self._goals += reached.float()
    respawn = reached | resting_far
    if respawn.any():
      ids = respawn.nonzero(as_tuple=False).squeeze(-1)
      self._place_target(ids, ball_xy[ids])
      self.goal_tol[ids] = goal_tolerance(self.target_dist[ids])
      self.kicked_since_target[ids] = False
      self.lined_up_latched[ids] = False

    super()._update_command()
    # Kicking is not standing: keep the gait terms in their walking regime.
    self.vel_command_b[:, 0] = WALK_COMMAND_SPEED

    lined = (
      self.in_wedge
      & (self.dist <= STAND_DISTANCE)
      & (self.yaw_error.abs() <= YAW_ALIGN_LIMIT)
    )
    self.lined_up_event[:] = lined & ~self.lined_up_latched
    self.lined_up_latched |= lined

    recent_kick = self.time_since_kick < STYLE_OFF_AFTER_KICK
    self.near_pending[:] = (self.dist <= self.cfg.near_distance) & ~recent_kick
    self.near_time += self.near_pending.float() * dt
    about_to_kick = self.in_wedge & (self.dist <= STYLE_OFF_DISTANCE)
    kicking = self.time_since_kick < STYLE_KICK_WINDOW
    self.style_gate[:] = (~(about_to_kick | kicking)).float()
    self.prev_heading_phi[:] = heading_potential(
      self.dist, self.yaw_error, self.cfg.heading_far
    )

    robot = self.robot
    vel = torch.cat(
      (robot.data.root_link_lin_vel_b[:, :2], robot.data.root_link_ang_vel_b[:, 2:3]),
      dim=-1,
    )
    alpha = dt / (self.cfg.speed_smooth_tau + dt)
    self.smoothed_vel += alpha * (vel - self.smoothed_vel)


@dataclass(kw_only=True)
class KickLoopCommandCfg(ApproachYawCommandCfg):
  """Kick-loop command. Targets 1–10 m in three range bins."""

  target_distance_bins: tuple[tuple[float, float], ...] = TARGET_BINS
  range_edges: tuple[float, float] = RANGE_EDGES
  near_distance: float = NEAR_DISTANCE
  heading_far: float = HEADING_FAR
  ball_roll_decel: float = BALL_ROLL_DECEL
  aim_broad_share: float = 0.0
  """Share of the broad cosine in ``kick_direction`` (0.5 in v5–v14)."""
  """Rolling deceleration of the ball (m/s²); match it to the real ball."""
  max_target_distance: float = MAX_TARGET_DISTANCE
  speed_smooth_tau: float = SPEED_SMOOTH_TAU
  ball_memory: bool = True
  ball_obs_noise: tuple[float, float] = (0.03, 0.05)
  feet_ball_sensor: str = "feet_ball_contact"
  body_ball_sensor: str = "body_ball_contact"

  def build(self, env: ManagerBasedRlEnv) -> KickLoopCommand:
    return KickLoopCommand(self, env)


def _kick_command(env: ManagerBasedRlEnv) -> KickLoopCommand:
  cmd = _command(env)
  assert isinstance(cmd, KickLoopCommand)
  return cmd


# Rewards. Events (kick, goal, ...) were set at the end of the last step.


def kick_dir_alignment(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Change in the body-heading potential (see ``heading_potential``)."""
  cmd = _kick_command(env)
  _, dist, _, yaw_error, _, _, _, _ = _current(env)
  phi = heading_potential(dist, yaw_error, cmd.cfg.heading_far)
  near = dist <= cmd.cfg.near_distance
  log = env.extras["log"]
  log["Metrics/kick_body_yaw_err_near"] = (yaw_error.abs() * near).sum() / (
    near.sum().clamp(min=1)
  )
  return phi - cmd.prev_heading_phi


def walk_speed(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Signed speed toward the ball over the vx limit, in [-1, 1], outside 1.5 m.

  Signed so stepping back costs what stepping in paid; a clamp at 0 let the
  policy farm it by shuffling back and forth.
  """
  cmd = _kick_command(env)
  _, dist, _, _, _, _, _, ball_b = _current(env)
  robot: Entity = env.scene["robot"]
  heading = ball_b / ball_b.norm(dim=-1, keepdim=True).clamp(min=1.0e-6)
  toward = (robot.data.root_link_lin_vel_b[:, :2] * heading).sum(dim=-1)
  score = (toward / cmd.speed_limit[:, 0]).clamp(-1.0, 1.0)
  # Recover first, then chase: half of the falls in stage3_v6/v7 came 1–2 s
  # after a kick, at speed, rushing after the ball.
  active = (dist > cmd.cfg.near_distance) & (cmd.time_since_kick >= POST_KICK_WINDOW)
  return torch.where(active, score, torch.zeros_like(score))


def walk_speed_limit(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Excess of the ~0.3 s smoothed |vx|, |vy|, |wz| over the limits.

  Smoothing ignores step-to-step gait sway; the kick itself is exempt.
  """
  cmd = _kick_command(env)
  excess = (cmd.smoothed_vel.abs() - cmd.speed_limit).clamp(min=0.0).sum(dim=-1)
  exempt = cmd.time_since_kick < SPEED_LIMIT_GRACE
  env.extras["log"]["Metrics/kick_speed_excess"] = excess.mean()
  return torch.where(exempt, torch.zeros_like(excess), excess)


def kick_direction(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per kick: b·cos⁺ + (1 - b)·exp(-(angle/σ)²) to the target, σ ≈ 20°.

  b = ``aim_broad_share``. The cosine alone paid 64% for a 50° miss and aim
  stalled there (stage3_v4). b = 0.5 (v5–v14) kept a gradient for rough kicks
  but still paid 0.32 for a 50° miss, and long runs traded accuracy for more,
  sloppier kicks; b = 0 pays only for accurate kicks.
  """
  cmd = _kick_command(env)
  angle = torch.acos(cmd.kick_cos.clamp(-1.0, 1.0))
  sharp = torch.exp(-torch.square(angle / KICK_AIM_SIGMA))
  b = cmd.cfg.aim_broad_share
  score = b * cmd.kick_cos.clamp(min=0.0) + (1.0 - b) * sharp
  return cmd.kick_event.float() * score * cmd.kick_quality


def _aim(cmd: KickLoopCommand) -> torch.Tensor:
  """Squared cosine to the target, floored at 0: 1 on target, 0.15 at 67°."""
  return torch.square(cmd.kick_cos.clamp(min=0.0))


def kick_vel(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per kick: ball speed over KICK_VEL_REF, capped at 1, times the aim.

  Without the aim, speed in any direction paid; in stage3_v3 that rewarded
  wild, noisy kicks (direction error grew to ~67°) and the action noise grew.
  """
  cmd = _kick_command(env)
  speed = (cmd.kick_speed / KICK_VEL_REF).clamp(max=1.0)
  return cmd.kick_event.float() * speed * _aim(cmd) * cmd.kick_quality


def kick_vel_accurate(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per kick: Gaussian match to the speed that rolls the ball to the target,
  times the aim."""
  cmd = _kick_command(env)
  req = cmd.kick_speed_req.clamp(min=0.5)
  match = torch.exp(-torch.square((cmd.kick_speed - req) / (0.25 * req)))
  return cmd.kick_event.float() * match * _aim(cmd) * cmd.kick_quality


def kick_goal(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per goal: a kicked ball passed the target, times that kick's quality."""
  cmd = _kick_command(env)
  return cmd.goal_event.float() * cmd.last_kick_quality


def kick_lined_up(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Once per approach: first step lined up behind the ball (no stop needed)."""
  return _kick_command(env).lined_up_event.float()


def kick_near_ball_time(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Each step near the ball with a kick pending.

  Not used in the stage-3 config: a cost tied to a zone fences the zone, and
  the policy learned to hover just outside it. ``kick_time_cost`` replaces it.
  """
  return _kick_command(env).near_pending.float()


def kick_time_cost(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Each step, anywhere, except the second after a kick.

  Urgency without a fence: hovering away from the ball costs the same as
  waiting next to it. Keep it below the per-step "alive" rewards so ending the
  episode never pays.
  """
  return (_kick_command(env).time_since_kick >= STYLE_OFF_AFTER_KICK).float()


def ball_avoidance(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Ball contact that is not a kick: any non-foot body, or a foot push."""
  cmd = _kick_command(env)
  return (cmd.body_touch | cmd.push).float()


def kick_double_touch(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per event: a new foot touch within 0.5 s of a kick (a carry, not a kick)."""
  return _kick_command(env).double_touch_event.float()


def single_feet_avoidance(
  env: ManagerBasedRlEnv, sensor_name: str = "feet_ground_contact"
) -> torch.Tensor:
  """Seconds beyond SINGLE_SUPPORT_MAX that one foot stays up on the other."""
  data = env.scene[sensor_name].data
  air = data.current_air_time
  contact = data.current_contact_time
  if air is None or contact is None:
    return torch.zeros(env.num_envs, device=env.device)
  other_down = contact.flip(dims=(-1,)) > 0.0
  excess = (air - SINGLE_SUPPORT_MAX).clamp(min=0.0) * other_down.float()
  return excess.sum(dim=-1)


def kick_fall(env: ManagerBasedRlEnv) -> torch.Tensor:
  """A fall within POST_KICK_WINDOW of a kick, on top of the general fall.

  Long runs drifted toward riskier kicks: falls within 2 s of a kick grew
  from 37 % to 66 % of all falls (v8 → v12b). This prices exactly those.
  """
  cmd = _kick_command(env)
  fell = env.termination_manager.terminated
  return (fell & (cmd.time_since_kick < POST_KICK_WINDOW)).float()


def post_kick_stability(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Upright and calm trunk for POST_KICK_WINDOW seconds after each kick."""
  cmd = _kick_command(env)
  robot: Entity = env.scene["robot"]
  upright = (-robot.data.projected_gravity_b[:, 2]).clamp(0.0, 1.0)
  calm = torch.exp(-torch.square(robot.data.root_link_ang_vel_b).sum(dim=-1) / 2.0)
  window = cmd.time_since_kick < POST_KICK_WINDOW
  return window.float() * torch.square(upright) * calm


__all__ = [
  "BALL_ROLL_DECEL",
  "KICK_AIM_SIGMA",
  "KICK_VEL_REF",
  "NEAR_DISTANCE",
  "RANGE_EDGES",
  "TARGET_BINS",
  "KickLoopCommand",
  "KickLoopCommandCfg",
  "ball_avoidance",
  "classify_touch",
  "goal_tolerance",
  "heading_potential",
  "kick_dir_alignment",
  "kick_direction",
  "kick_double_touch",
  "kick_fall",
  "kick_goal",
  "kick_quality_score",
  "kick_lined_up",
  "kick_near_ball_time",
  "kick_time_cost",
  "kick_vel",
  "kick_vel_accurate",
  "post_kick_stability",
  "required_kick_speed",
  "single_feet_avoidance",
  "walk_speed",
  "walk_speed_limit",
]

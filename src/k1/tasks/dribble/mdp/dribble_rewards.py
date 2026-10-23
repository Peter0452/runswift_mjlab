"""§6 reward for the dribble task — the surface /harbor:reward-tune edits.

``apply_dribble_rewards`` is called by ``booster_k1_dribble_env_cfg`` after the
approach rewards are inherited. Reward functions for this task live in this file
(or in ``dribble.py`` for ones that need the command's state).

Reward-tune iter 12: ``alternate_leg_dribble`` — when dribbling forwards, tap
L→R→L→R and swing the other leg through between touches (faster, more stable
than one-leg drag). First-control and collinear step-over are unchanged.
Reward-tune iter 6 (= iter 4 + ``approach_progress`` for far / behind spawns).
Reward-tune iter 4 (= iter 3 + stability/speed: redirect_bonus 25 -> 10,
non-timeout ``termination_penalty`` -100, dribble-local ``approach_speed_limit``
with vx limit max(vx_limit, s + 0.2), ball_vel_cmd_tracking 3 -> 4.5).
Iter 3 (= iter 2 + turn-and-push: behind_ball_alignment removed,
outcome-based ``bad_touch``, ``follow_ball_heading``, one-shot ``redirect_bonus``,
Gaussian ``ball_vel_cmd_tracking`` (sigma 0.25), approach_view 0.3 -> 0.5).
Iter 2 (= iter 1 + tent-shaped ``ball_progress``, upright 1 -> 2).
Iter 1: dense signed ``ball_progress`` along the command plus
distance-gated velocity tracking; the static "stand at the ball" terms are cut.
Notation: d = trunk-to-ball planar distance, v = ball planar velocity (world),
s = commanded ball speed, c_hat = commanded direction, cmd = s * c_hat.
All terms read the true sim state.
"""

from __future__ import annotations

import json
import math
import os
from typing import TYPE_CHECKING

import torch

from k1.tasks.dribble.mdp.dribble import _dribble, dribble_window_success
from k1.tasks.kick.mdp.approach import (
  _yaw_angle,
  approach_view,
  speed_limit_excess,
)
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.utils.lab_api.math import wrap_to_pi

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv, ManagerBasedRlEnvCfg

GATE_FLAT_DIST = 0.6
"""Velocity terms pay in full while the ball is within this distance (m)."""
GATE_DECAY = 3.0
MOVING_BALL_SPEED = 0.05
TRACK_SIGMA = 0.25
"""Gaussian width of the velocity-tracking kernel (m/s) = the success bound scale."""
TOUCH_WINDOW_STEPS = 10
"""recent_touch: a foot-ball contact within the last 0.2 s (10 steps)."""
BAD_TOUCH_MIN_SPEED = 0.1
BAD_TOUCH_STOP_SPEED = 0.3
REDIRECT_ALONG_FRAC = 0.5
REDIRECT_COS_MIN = 0.7
REDIRECT_MAX_DIST = 1.0
DRIBBLE_VX_MARGIN = 0.2
"""While dribbling, the vx speed limit is raised to at least s + this margin (m/s)."""
ALT_FORWARD_COS_MIN = 0.50
"""Robot-behind-ball alignment (b_hat · c_hat) required for alternate-leg dribble."""
ALT_FORWARD_HEADING_MAX = 0.70
"""Body heading error vs cmd_dir (rad) below which the dribble counts as forward."""
ALT_SWING_WINDOW = (0.10, 0.55)
"""Seconds after a tap during which the other leg's forward swing is rewarded."""
FAST_SPEED_RANGE = (0.6, 1.5)
"""v14 (2026-10-19): commanded ball speeds (m/s) over which the control envelope
widens. v13 kept the ball at ~0.4 m at every command and topped out at ~0.8 m/s
ball speed (4 steps/s x 0.17 m steps); a 1.5 m/s dribble pushes the ball ahead
and runs after it, touching every few strides."""
FAST_GATE_EXTRA = 0.5
"""Extra flat distance of the velocity-reward gate at the top of FAST_SPEED_RANGE
(0.6 m -> 1.1 m)."""
FAST_PROXIMITY_EXTRA = 0.32
"""Extra flat radius of ball_proximity at the top of FAST_SPEED_RANGE (0.28 -> 0.6 m)."""
FAST_FRESH_EXTRA = 0.4
"""v15: extra distance (m) at which fov_recheck still counts the ball as near, at
the top of FAST_SPEED_RANGE (0.5 -> 0.9 m). At 1.5 m/s the ball runs ahead and
v14's term (worth as much as all speed terms) paid 20 % less above 1.1 m/s."""
FAST_VIEW_FADE = 0.6
"""v15d: share of the ball-view terms (approach_view, fov_recheck) removed at the
top of FAST_SPEED_RANGE. v15b drifted from 12400 to 13000 by trading speed for
these terms (fov_recheck +0.07, approach_view +0.04 per episode) at flat total
reward, slowing every commanded speed in the eval."""
ALT_FADE_SPEED = (0.7, 1.1)
"""alternate_leg_dribble (a tap on every stride) fades out over these commanded
speeds (m/s): full below, zero above."""

DRIBBLE_GENES: dict = json.loads(os.environ.get("DRIBBLE_GENES", "{}") or "{}")
"""Per-run switches, as KICK_GENES for the kick: "track_sigma_fast" (m/s),
"amp_mix" ("fast", read in rl_cfg), "amp_cond" (true: command-conditioned
discriminator, env_cfgs + rl_cfg), "tilt_guard" (weight), "push_chase" (true:
push the ball 1-2 m ahead at fast commands; here and in env_cfgs). Empty = the
v17 recipe."""
TRACK_SIGMA_FAST = float(DRIBBLE_GENES.get("track_sigma_fast", TRACK_SIGMA))
"""v18 (2026-10-20): tracking-kernel width at the top of FAST_SPEED_RANGE. With
0.25 the term (weight 8, x2 aligned) paid ~0 once the ball ran > 0.5 m/s under
the command: swa_v17 runs 0.62 m/s at a 1.0 command, 4e-6 of the term at 1.5,
so only ball_progress and fast_dribble_drive pulled toward speed."""
PUSH_SPEED_RANGE = (0.9, 1.5)
"""v21 push-and-chase ("push_chase" gene): commanded speeds over which the ball
may run 1-2 m ahead between touches. Starts above 0.8 m/s, so the slow dribble
and its gates are unchanged. Same range as DribbleCommandCfg.push_speed_range."""
_PUSH = bool(DRIBBLE_GENES.get("push_chase"))
PUSH_GATE_EXTRA = 0.9 if _PUSH else 0.0
"""Velocity-reward gate flat distance at the top: 1.1 -> 2.0 m."""
PUSH_PROXIMITY_EXTRA = 1.0 if _PUSH else 0.0
"""ball_proximity flat radius at the top: 0.6 -> 1.6 m."""
PUSH_FRESH_EXTRA = 0.6 if _PUSH else 0.0
"""fov_recheck near distance at the top: 0.9 -> 1.5 m."""


def _push_frac(s: torch.Tensor) -> torch.Tensor:
  """0 at or below PUSH_SPEED_RANGE[0], 1 at or above PUSH_SPEED_RANGE[1]."""
  lo, hi = PUSH_SPEED_RANGE
  return ((s - lo) / (hi - lo)).clamp(0.0, 1.0)


def _kicked(cmd) -> torch.Tensor:
  """v22: in a kick window after its kick, where the robot should stand still
  instead of following, approaching or searching for the kicked ball."""
  return cmd.kick_mode & cmd.kick_done


def _state(env: ManagerBasedRlEnv):
  cmd = _dribble(env)
  robot_xy = env.scene["robot"].data.root_link_pos_w[:, :2]
  ball = env.scene["ball"].data
  ball_xy = ball.root_link_pos_w[:, :2]
  v = ball.root_link_lin_vel_w[:, :2]
  d = torch.linalg.norm(ball_xy - robot_xy, dim=-1)
  return cmd, robot_xy, ball_xy, v, d


def _fast_frac(s: torch.Tensor) -> torch.Tensor:
  """0 at or below FAST_SPEED_RANGE[0], 1 at or above FAST_SPEED_RANGE[1]."""
  lo, hi = FAST_SPEED_RANGE
  return ((s - lo) / (hi - lo)).clamp(0.0, 1.0)


def _dist_gate(d: torch.Tensor, s: torch.Tensor) -> torch.Tensor:
  """g(d) = exp(-3 * max(0, d - flat)): flat 1 within 0.6 m, widening to 1.1 m
  with the commanded speed s (v14), and to 2.0 m with push_chase (v21)."""
  flat = (
    GATE_FLAT_DIST + FAST_GATE_EXTRA * _fast_frac(s) + PUSH_GATE_EXTRA * _push_frac(s)
  )
  return torch.exp(-GATE_DECAY * (d - flat).clamp(min=0.0))


def _aligned_posture_bonus(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Multiplier in [1.0, 2.0]:
  - 1.0 from ANY body position (so initial lateral 90° or collinear 180° step-over
    touches are never penalized and move the ball immediately).
  - Rises up to 2.0 when the robot transitions behind the ball (cos_behind -> +1)
    with its body heading aligned with cmd_dir (b_cmd -> 0), making aligned forward
    dribbling pay 2x as much as continuing to drag the ball sideways/backward."""
  cmd, robot_xy, ball_xy, _, d = _state(env)
  c_hat = cmd.ball_cmd_dir_w
  to_ball = ball_xy - robot_xy
  b_hat = to_ball / (d.unsqueeze(-1) + 1.0e-3)
  cos_behind = torch.sum(b_hat * c_hat, dim=-1)
  behind_score = ((cos_behind + 0.2) / 1.2).clamp(0.0, 1.0)

  yaw = _yaw_angle(env.scene["robot"].data.root_link_quat_w)
  cmd_yaw = torch.atan2(c_hat[:, 1], c_hat[:, 0])
  b_cmd = wrap_to_pi(cmd_yaw - yaw)
  heading_score = torch.exp(-2.0 * torch.square(b_cmd))

  mult = 1.0 + behind_score * heading_score
  env.extras["log"]["Metrics/dribble_posture_gate"] = mult.mean()
  return mult


def ball_progress(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Tent: clip(min(u, 2s - u) / max(s, 0.2), -1, 1) * g(d) * aligned_mult while s > 0."""
  cmd, _, _, v, d = _state(env)
  s = cmd.ball_cmd_speed
  along = torch.sum(v * cmd.ball_cmd_dir_w, dim=-1)
  tent = torch.minimum(along, 2.0 * s - along)
  raw = (tent / s.clamp(min=0.2)).clamp(-1.0, 1.0) * _dist_gate(d, s)
  mult = _aligned_posture_bonus(env)
  prog = torch.where(raw > 0.0, raw * mult, raw)
  return torch.where(s > 0.0, prog, torch.zeros_like(prog))


def ball_vel_cmd_tracking(env: ManagerBasedRlEnv) -> torch.Tensor:
  """exp(-||v - cmd||^2 / sigma^2) * g(d) * aligned_mult; s > 0 and ||v|| > 0.05.
  sigma = TRACK_SIGMA, widening to TRACK_SIGMA_FAST over FAST_SPEED_RANGE."""
  cmd, _, _, v, d = _state(env)
  s = cmd.ball_cmd_speed
  c = cmd.ball_cmd_dir_w * s.unsqueeze(-1)
  err_sq = torch.sum(torch.square(v - c), dim=-1)
  sigma = TRACK_SIGMA + (TRACK_SIGMA_FAST - TRACK_SIGMA) * _fast_frac(s)
  r = torch.exp(-err_sq / sigma.square()) * _dist_gate(d, s)
  r = r * _aligned_posture_bonus(env)
  gate = (s > 0.0) & (torch.linalg.norm(v, dim=-1) > MOVING_BALL_SPEED)
  return torch.where(gate, r, torch.zeros_like(r))


def ball_stop_tracking(env: ManagerBasedRlEnv) -> torch.Tensor:
  """exp(-4 ||v||) * exp(-2 max(0, d - 0.5)) while s == 0, else 0."""
  cmd, _, _, v, d = _state(env)
  r = torch.exp(-4.0 * torch.linalg.norm(v, dim=-1)) * torch.exp(
    -2.0 * (d - 0.5).clamp(min=0.0)
  )
  # v22: a kick window has speed 0 too, but the ball is meant to leave.
  stop = (cmd.ball_cmd_speed == 0.0) & ~cmd.kick_mode
  return torch.where(stop, r, torch.zeros_like(r))


def ball_proximity(env: ManagerBasedRlEnv) -> torch.Tensor:
  """exp(-5 max(0, d - r_flat)), r_flat = 0.28 m when moving (K1 foot reach),
  widening to 0.6 m at fast commands (v14), 0.50 m when stopped."""
  cmd, _, _, _, d = _state(env)
  s = cmd.ball_cmd_speed
  r_flat = torch.where(
    s > 0.0,
    0.28 + FAST_PROXIMITY_EXTRA * _fast_frac(s) + PUSH_PROXIMITY_EXTRA * _push_frac(s),
    torch.full_like(d, 0.50),
  )
  r = torch.exp(-5.0 * (d - r_flat).clamp(min=0.0))
  return torch.where(_kicked(cmd), torch.zeros_like(r), r)


def follow_ball_heading(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Turn body toward the ball/command: before first touch in window, mild tracking
  so lateral/perpendicular first-touch control is uninhibited; when collinear in-between
  (cos_behind < -0.35) or after first touch (redirect_latched), fast turn (up to
  2.2 rad/s) to align body heading with cmd_dir."""
  cmd, robot_xy, ball_xy, _, d = _state(env)
  robot = env.scene["robot"].data
  yaw = _yaw_angle(robot.root_link_quat_w)
  to_ball = ball_xy - robot_xy
  b_hat = to_ball / (d.unsqueeze(-1) + 1.0e-3)
  cos_behind = torch.sum(b_hat * cmd.ball_cmd_dir_w, dim=-1)
  b_ball = wrap_to_pi(torch.atan2(to_ball[:, 1], to_ball[:, 0]) - yaw)
  cmd_yaw = torch.atan2(cmd.ball_cmd_dir_w[:, 1], cmd.ball_cmd_dir_w[:, 0])
  b_cmd = wrap_to_pi(cmd_yaw - yaw)
  in_between = (cos_behind < -0.35) & (d < 0.70) & (cmd.ball_cmd_speed > 0.0)
  turn_to_cmd = (cmd.redirect_latched | in_between) & (cmd.ball_cmd_speed > 0.0)
  target_err = torch.where(
    in_between,
    b_cmd,
    torch.where(turn_to_cmd, wrap_to_pi(0.5 * b_ball + 0.5 * b_cmd), b_ball),
  )
  max_wz = torch.where(
    in_between,
    torch.full_like(target_err, 2.2),
    torch.where(
      cmd.redirect_latched,
      torch.full_like(target_err, 1.6),
      torch.full_like(target_err, math.pi / 4),
    ),
  )
  wz_des = torch.clamp(5.0 * target_err, -max_wz, max_wz)
  wz = robot.root_link_ang_vel_w[:, 2]
  return torch.exp(-3.0 * torch.square(wz_des - wz))


def post_touch_body_align(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Two-phase dynamic control:
  - Phase 1 (pre-touch): 0 here so the first touch happens as fast as possible
    from any body orientation (lateral, diagonal, or perpendicular).
  - Phase 2 (after first control touch / redirect_latched): rewards quickly turning
    the body to align with the ball & command direction, plus a sustained power/control
    bonus when the body is aligned and driving the ball forward along cmd_dir."""
  cmd, robot_xy, ball_xy, v_ball, d = _state(env)
  s = cmd.ball_cmd_speed
  c_hat = cmd.ball_cmd_dir_w
  robot = env.scene["robot"].data
  yaw = _yaw_angle(robot.root_link_quat_w)
  to_ball = ball_xy - robot_xy
  b_ball = wrap_to_pi(torch.atan2(to_ball[:, 1], to_ball[:, 0]) - yaw)
  cmd_yaw = torch.atan2(c_hat[:, 1], c_hat[:, 0])
  b_cmd = wrap_to_pi(cmd_yaw - yaw)
  align_err = wrap_to_pi(0.5 * b_cmd + 0.5 * b_ball)

  # 1. Fast body turn rate toward alignment right after the first touch, plus
  # stepping around behind the ball (reposition_r) when cos_behind < 0.75.
  wz = robot.root_link_ang_vel_b[:, 2]
  turn_dir = torch.where(align_err >= 0.0, 1.0, -1.0)
  need_turn = (align_err.abs() > 0.20).float()
  turn_rate_r = (wz * turn_dir / 1.5).clamp(0.0, 1.0) * need_turn

  b_hat = to_ball / (d.unsqueeze(-1) + 1.0e-3)
  cos_behind = torch.sum(b_hat * c_hat, dim=-1)
  behind_score = ((cos_behind + 0.3) / 1.3).clamp(0.0, 1.0)

  # Tangential step toward the behind-ball pocket after the first touch
  v_r = robot.root_link_lin_vel_w[:, :2]
  t_ccw = torch.stack((-b_hat[:, 1], b_hat[:, 0]), dim=-1)
  t_sign = torch.where(
    torch.sum(t_ccw * (-c_hat), dim=-1) >= 0.0,
    torch.ones_like(s),
    -torch.ones_like(s),
  )
  t_hat = t_ccw * t_sign.unsqueeze(-1)
  reposition_r = (torch.sum(v_r * t_hat, dim=-1) / 0.6).clamp(0.0, 1.0) * (
    cos_behind < 0.75
  ).float()

  # 2. Sustained aligned ball-drive bonus once body is behind the ball AND facing cmd_dir
  body_aligned = torch.exp(-2.5 * torch.square(align_err)) * behind_score
  along_speed = (torch.sum(v_ball * c_hat, dim=-1) / s.clamp(min=0.2)).clamp(0.0, 1.5)
  aligned_drive_r = body_aligned * along_speed * _dist_gate(d, s)

  active = (cmd.redirect_latched | cmd.win_touched) & (s > 0.0) & (~cmd.ball_lost)
  env.extras["log"]["Metrics/dribble_post_touch_align_err"] = (
    align_err.abs() * active.float()
  ).sum() / active.float().sum().clamp(min=1.0)
  return torch.where(
    active,
    0.6 * turn_rate_r + 0.6 * reposition_r + 1.2 * aligned_drive_r,
    torch.zeros_like(s),
  )


def _forward_dribble_mask(
  cmd,
  robot_xy: torch.Tensor,
  ball_xy: torch.Tensor,
  v: torch.Tensor,
  d: torch.Tensor,
  env: ManagerBasedRlEnv,
) -> torch.Tensor:
  """True while moving the ball forwards from an aligned behind-the-ball posture.

  Excludes pre-touch, lost-ball, stop, and collinear step-over (cos_behind < 0).
  """
  s = cmd.ball_cmd_speed
  c_hat = cmd.ball_cmd_dir_w
  to_ball = ball_xy - robot_xy
  b_hat = to_ball / (d.unsqueeze(-1) + 1.0e-3)
  cos_behind = torch.sum(b_hat * c_hat, dim=-1)
  yaw = _yaw_angle(env.scene["robot"].data.root_link_quat_w)
  cmd_yaw = torch.atan2(c_hat[:, 1], c_hat[:, 0])
  heading_err = wrap_to_pi(cmd_yaw - yaw).abs()
  along = torch.sum(v * c_hat, dim=-1)
  return (
    (s > 0.0)
    & (~cmd.ball_lost)
    & cmd.win_touched
    & (cos_behind > ALT_FORWARD_COS_MIN)
    & (heading_err < ALT_FORWARD_HEADING_MAX)
    & (d < 0.65)
    & (along > MOVING_BALL_SPEED)
  )


def alternate_leg_dribble(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Forward-dribble gait: after a tap, swing the *other* leg through and tap
  with it next (L→R→L→R). Faster cadence and a planted support foot instead of
  one-leg dragging / hopping.

  Sparse: +1 on a debounced exclusive tap by the opposite foot, scaled by how
  well the ball is tracking command speed. Dense: in the 0.10–0.55 s window
  after a tap, reward the next foot being airborne and moving forward while the
  last tap foot is planted. First tap of an episode is free (any foot). Collinear
  step-overs and unaligned first-control stay on their own terms.
  """
  cmd, robot_xy, ball_xy, v, d = _state(env)
  s = cmd.ball_cmd_speed
  c_hat = cmd.ball_cmd_dir_w
  forward = _forward_dribble_mask(cmd, robot_xy, ball_xy, v, d, env)
  along_frac = (torch.sum(v * c_hat, dim=-1) / s.clamp(min=0.2)).clamp(0.0, 1.0)
  event_r = cmd.alt_touch_event.float() * along_frac

  robot = env.scene["robot"].data
  yaw = _yaw_angle(robot.root_link_quat_w)
  heading = torch.stack((yaw.cos(), yaw.sin()), dim=-1)
  feet_contact = cmd.gait_contact_prev
  feet_vel = robot.body_link_lin_vel_w[:, cmd._gait_feet_ids, :2]
  last_left = cmd.tap_side > 0.0
  last_right = cmd.tap_side < 0.0
  next_air = torch.where(
    last_left,
    ~feet_contact[:, 1],
    torch.where(last_right, ~feet_contact[:, 0], torch.zeros_like(last_left)),
  )
  support_planted = torch.where(
    last_left,
    feet_contact[:, 0],
    torch.where(last_right, feet_contact[:, 1], torch.zeros_like(last_left)),
  )
  next_vel = torch.where(
    last_left.unsqueeze(-1),
    feet_vel[:, 1],
    torch.where(
      last_right.unsqueeze(-1), feet_vel[:, 0], torch.zeros_like(feet_vel[:, 0])
    ),
  )
  next_fwd = (torch.sum(next_vel * heading, dim=-1) / 0.8).clamp(0.0, 1.0)
  in_swing = (cmd.time_since_tap >= ALT_SWING_WINDOW[0]) & (
    cmd.time_since_tap <= ALT_SWING_WINDOW[1]
  )
  swing_r = next_air.float() * support_planted.float() * next_fwd * in_swing.float()
  lo, hi = ALT_FADE_SPEED
  fade = ((hi - s) / (hi - lo)).clamp(0.0, 1.0)
  r = (event_r + 0.25 * swing_r * along_frac) * fade
  log = env.extras.setdefault("log", {})
  log["Metrics/dribble_alt_leg_active"] = forward.float().mean()
  log["Metrics/dribble_alt_leg_swing"] = (swing_r * forward.float()).mean()
  return torch.where(forward, r, torch.zeros_like(r))


def bad_touch(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Outcome-based: 1 if recent_touch and ||v|| > 0.1 and the ball moves the wrong
  way (s > 0: v . c_hat < 0; s == 0: ||v|| > 0.3). Never reads the robot pose."""
  cmd, _, _, v, _ = _state(env)
  speed = torch.linalg.norm(v, dim=-1)
  along = torch.sum(v * cmd.ball_cmd_dir_w, dim=-1)
  wrong = torch.where(
    cmd.ball_cmd_speed > 0.0, along < 0.0, speed > BAD_TOUCH_STOP_SPEED
  )
  bad = cmd.recent_touch(TOUCH_WINDOW_STEPS) & (speed > BAD_TOUCH_MIN_SPEED) & wrong
  env.extras["log"]["Metrics/dribble_bad_touch"] = bad.float().mean()
  return bad.float()


def redirect_bonus(env: ManagerBasedRlEnv) -> torch.Tensor:
  """One-shot per command window: 1 on the first step where s > 0, recent_touch,
  u > 0.5 s, cos(angle(v, c_hat)) > 0.7 and d < 1.0; latched until the next
  command resample or episode reset."""
  cmd, _, _, v, d = _state(env)
  s = cmd.ball_cmd_speed
  speed = torch.linalg.norm(v, dim=-1)
  along = torch.sum(v * cmd.ball_cmd_dir_w, dim=-1)
  cos = along / (speed + 1.0e-6)
  fire = (
    (s > 0.0)
    & ~cmd.redirect_latched
    & cmd.recent_touch(TOUCH_WINDOW_STEPS)
    & (along > REDIRECT_ALONG_FRAC * s)
    & (cos > REDIRECT_COS_MIN)
    & (d < REDIRECT_MAX_DIST)
  )
  cmd.redirect_latched |= fire
  env.extras["log"]["Metrics/dribble_redirect_fire"] = fire.float().mean()
  return fire.float()


APPROACH_MIN_DIST = 0.25
APPROACH_SPEED = 0.8


def approach_progress(env: ManagerBasedRlEnv) -> torch.Tensor:
  """clip(v_r . b_hat / 0.8, 0, 1) * 1[d > 0.25]: walk all the way into K1 foot reach."""
  cmd, robot_xy, ball_xy, _, d = _state(env)
  v_r = env.scene["robot"].data.root_link_lin_vel_w[:, :2]
  b_hat = (ball_xy - robot_xy) / (d.unsqueeze(-1) + 1.0e-3)
  r = (torch.sum(v_r * b_hat, dim=-1) / APPROACH_SPEED).clamp(0.0, 1.0)
  return torch.where((d > APPROACH_MIN_DIST) & ~_kicked(cmd), r, torch.zeros_like(r))


def termination_penalty(env: ManagerBasedRlEnv) -> torch.Tensor:
  """1 on the step an episode terminates for any reason other than a time-out
  (illegal_contact, fell_over, ball_lost, nan). The termination manager keeps
  time-out terms (time_out, out_of_terrain_bounds) in a separate truncation
  buffer, so ``terminated`` already excludes them; a step on which a real
  termination coincides with a time-out still counts. Terminations are computed
  before the rewards in the env step, so the flags refer to this step."""
  return env.termination_manager.terminated.float()


def fast_fall(env: ManagerBasedRlEnv) -> torch.Tensor:
  """v28: on a fall (illegal contact or fell over), the robot's planar speed
  (m/s). With a negative weight a fall at speed costs more than one standing:
  v27 sped up 0.72 -> 0.9 m/s while dribble falls rose 0.52 -> 1.06-1.42 %."""
  tm = env.termination_manager
  v = torch.linalg.norm(env.scene["robot"].data.root_link_lin_vel_w[:, :2], dim=-1)
  fell = torch.zeros_like(v, dtype=torch.bool)
  # Play configs drop some terminations (illegal_contact): use the active ones.
  for name in ("illegal_contact", "fell_over"):
    if name in tm.active_terms:
      fell = fell | tm.get_term(name)
  return fell.float() * v


def stepover_backtap_turn(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Collinear in-between maneuver (robot is between the ball and the target,
  cos_behind = b_hat . c_hat < -0.35, as in 094502 frames 110..185):
  1. Take a big step over/past the ball (lead foot reaches across the ball with
     wide foot span).
  2. Controllably tap/pull the ball backward along c_hat while simultaneously
     turning the body 180° toward c_hat at high yaw rate."""
  cmd, robot_xy, ball_xy, v_ball, d = _state(env)
  s = cmd.ball_cmd_speed
  c_hat = cmd.ball_cmd_dir_w
  robot = env.scene["robot"].data
  to_ball = ball_xy - robot_xy
  b_hat = to_ball / (d.unsqueeze(-1) + 1.0e-3)
  cos_behind = torch.sum(b_hat * c_hat, dim=-1)

  feet_xy = robot.body_link_pos_w[:, cmd._gait_feet_ids, :2]
  # Reach of each foot past the ball along b_hat (= -c_hat when collinear)
  foot_rel_ball = feet_xy - ball_xy.unsqueeze(1)
  proj_over = torch.sum(foot_rel_ball * b_hat.unsqueeze(1), dim=-1)
  max_over = proj_over.max(dim=-1).values
  foot_span = torch.linalg.norm(feet_xy[:, 0] - feet_xy[:, 1], dim=-1)
  step_over_r = ((max_over + 0.08) / 0.16).clamp(0.0, 1.0) * (
    (foot_span - 0.16) / 0.12
  ).clamp(0.0, 1.0)

  # Simultaneous controllable backward ball velocity along c_hat + fast body turn
  u_back = (torch.sum(v_ball * c_hat, dim=-1) / s.clamp(min=0.2)).clamp(0.0, 1.5)
  yaw = _yaw_angle(robot.root_link_quat_w)
  cmd_yaw = torch.atan2(c_hat[:, 1], c_hat[:, 0])
  b_cmd = wrap_to_pi(cmd_yaw - yaw)
  wz = robot.root_link_ang_vel_b[:, 2]
  turn_dir = torch.where(b_cmd >= 0.0, 1.0, -1.0)
  turn_spd = (wz * turn_dir / 2.0).clamp(0.0, 1.0)

  # Active ONLY during the initial 0.65 s of the window's touch so the policy
  # cannot farm it by dragging the ball backward indefinitely, and backward tap
  # is strictly multiplied by turn_spd so it only pays when simultaneously turning!
  in_grace = cmd.time_since_win_touch <= 0.65
  in_between = (cos_behind < -0.35) & (d < 0.65)
  turning_through = cmd.recent_touch(15) & (b_cmd.abs() > 0.60) & (d < 0.70)
  active = (s > 0.0) & (~cmd.ball_lost) & in_grace & (in_between | turning_through)
  synergy = (
    0.35 * step_over_r * (0.3 + 0.7 * turn_spd)
    + 0.5 * turn_spd
    + 1.0 * u_back * turn_spd
  )
  env.extras["log"]["Metrics/dribble_stepover_active"] = active.float().mean()
  return torch.where(active, synergy, torch.zeros_like(s))


def dribble_speed_limit(env: ManagerBasedRlEnv) -> torch.Tensor:
  """approach_speed_limit with the vx limit replaced by max(vx_limit, s + 0.2)
  while s > 0, wz limit raised to 1.6 rad/s during post-touch body alignment,
  and 2.5 rad/s during collinear step-over 180° turns or lost-ball spin."""
  cmd, robot_xy, ball_xy, _, d = _state(env)
  robot = env.scene["robot"].data
  s = cmd.ball_cmd_speed
  to_ball = ball_xy - robot_xy
  b_hat = to_ball / (d.unsqueeze(-1) + 1.0e-3)
  cos_behind = torch.sum(b_hat * cmd.ball_cmd_dir_w, dim=-1)
  in_between = (cos_behind < -0.35) & (d < 0.70) & (s > 0.0)
  limits = cmd.speed_limit.clone()
  vx_dribble = torch.maximum(limits[:, 0], s + DRIBBLE_VX_MARGIN)
  limits[:, 0] = torch.where(s > 0.0, vx_dribble, limits[:, 0])
  wz_align = torch.maximum(limits[:, 2], torch.full_like(s, 1.6))
  limits[:, 2] = torch.where(cmd.redirect_latched & (s > 0.0), wz_align, limits[:, 2])
  wz_spin = torch.maximum(limits[:, 2], torch.full_like(s, 2.5))
  limits[:, 2] = torch.where(cmd.ball_lost | in_between, wz_spin, limits[:, 2])
  excess = speed_limit_excess(
    robot.root_link_lin_vel_b, robot.root_link_ang_vel_b[:, 2], limits
  )
  env.extras["log"]["Metrics/approach_speed_excess"] = excess.mean()
  return excess


KICK_VEL_TARGET = 7.0
"""v22 kick mode: the speed goal (m/s; user: kick straight at 7 m/s)."""
KICK_WAIT_FREE_S = float(DRIBBLE_GENES.get("kick_wait_free_s", 2.0))
"""kick_wait_cost starts after this long in a kick window without the kick done
(v36 gene for a quicker kick)."""
KICK_POWER_CAP = float(DRIBBLE_GENES.get("kick_cap", 1.15))
"""kick_power pays speed / 7 m/s up to this (v33 gene kick_cap: 2.0 = no
practical cap, so a faster kick always pays more)."""
KICK_AIM_SIGMA2 = (0.5, 0.05)
"""Aim = mean of a wide exp(-err^2 / 0.5) and the kick loop's sharp long-kick
exp(-err^2 / 0.05) (B-Human's sigma): 1 on line, 0.86 at 6 deg, 0.24 at
35 deg. The sharp kernel alone paid ~0 at the untrained 35 deg (smoke test)."""
KICK_SETUP_DIST = 0.3
"""Trunk-to-ball distance behind the ball (m) that kick_line_up pulls toward."""
KICK_LINE_UP_TAU = float(DRIBBLE_GENES.get("kick_line_up_tau", 1.0e9))
"""v26: kick_line_up fades as exp(-wait / tau) (s); default = no fade."""
KICK_QUICK_TAU = float(DRIBBLE_GENES.get("kick_quick_tau", 1.0e9))
KICK_AIM_NEG = float(DRIBBLE_GENES.get("kick_aim_neg", 0.0))
"""v44: kick_power's aim falls to -KICK_AIM_NEG at 2 x KICK_AIM_NEG_DEG error."""
KICK_AIM_NEG_RAD = math.radians(float(DRIBBLE_GENES.get("kick_aim_neg_deg", 40.0)))
"""v40: kick_power x (0.5 + 0.5 exp(-wait / tau)); default = no time factor."""


def kick_power(env: ManagerBasedRlEnv) -> torch.Tensor:
  """On the kick-window kick: ground speed / 7 m/s (to 1.15) x sharp aim x no
  loft. Speed and aim together (kick lessons 4 and 11): aim alone paid weak
  taps, speed alone paid wild kicks, and launch speed counted lofted balls."""
  cmd = _dribble(env)
  speed = (cmd.kick_speed / KICK_VEL_TARGET).clamp(max=KICK_POWER_CAP)
  wide, sharp = KICK_AIM_SIGMA2
  wide = float(DRIBBLE_GENES.get("kick_aim_wide", wide))  # v49: fixed tighter wide
  if KICK_AIM_CURRICULUM:
    wide = _aim_curriculum_wide(env, cmd)
  err2 = cmd.kick_err.square()
  aim = 0.5 * (torch.exp(-err2 / wide) + torch.exp(-err2 / sharp))
  # v44 (B-Human's signed direction reward): beyond KICK_AIM_NEG_DEG the aim
  # turns negative, to -KICK_AIM_NEG at twice that error, so a hard kick the
  # wrong way costs more than a soft one.
  if KICK_AIM_NEG > 0.0:
    over = ((cmd.kick_err - KICK_AIM_NEG_RAD) / KICK_AIM_NEG_RAD).clamp(0.0, 1.0)
    aim = aim - KICK_AIM_NEG * over
  # v40 (user: kick as soon as possible): a kick pays 0.5-1 by how soon it came
  # in the window; v37's wait cost alone did not shorten the time to kick.
  quick = 0.5 + 0.5 * torch.exp(-cmd.kick_wait / KICK_QUICK_TAU)
  if KICK_POSE_GATE:
    # v45 (B-Human's kick-pose counter): the paid part scales 0.5-1 with how
    # long the robot was set up for the kick; the wrong-way penalty does not.
    ready = _kick_pose_ready(env, cmd)
    aim = torch.where(aim > 0.0, aim * (0.5 + 0.5 * ready.square()), aim)
  return cmd.kick_event.float() * speed * aim * cmd.kick_loft * quick


KICK_POSE_GATE = bool(DRIBBLE_GENES.get("kick_pose_gate", False))
KICK_POSE_S = 0.6
"""v45: seconds set up (ball 0.05-0.40 m ahead of the feet along the kick
direction, within 0.15 m sideways, trunk within 60 deg of it) for full pay."""
KICK_AIM_CURRICULUM = bool(DRIBBLE_GENES.get("kick_aim_curriculum", False))
KICK_AIM_WIDE_RANGE = (0.5, 0.15)
KICK_AIM_CURR_DEG = tuple(DRIBBLE_GENES.get("kick_aim_curr_deg", (10.0, 20.0)))
"""v46b: running kick error (deg) at which the wide kernel is tightest / widest.
The training error runs ~5 deg above the bench's (noise, 90 deg kicks)."""
"""v46: the wide aim kernel's sigma^2, from 0.5 while the running kick error
is >= 20 deg down to 0.15 once it is <= 10 deg (B-Human's narrowing sigma)."""


def _kick_pose_ready(env: ManagerBasedRlEnv, cmd) -> torch.Tensor:
  """0-1: how long (to KICK_POSE_S) the robot has been set up for the kick,
  read before this step's update so the kick step itself does not count."""
  if not hasattr(cmd, "_pose_t"):
    cmd._pose_t = torch.zeros(env.num_envs, device=env.device)
  ready = (cmd._pose_t / KICK_POSE_S).clamp(0.0, 1.0)
  robot = env.scene["robot"].data
  mid = robot.body_link_pos_w[:, cmd._gait_feet_ids, :2].mean(dim=1)
  rel = env.scene["ball"].data.root_link_pos_w[:, :2] - mid
  d = cmd.ball_cmd_dir_w
  along = (rel * d).sum(dim=-1)
  side = rel[:, 1] * d[:, 0] - rel[:, 0] * d[:, 1]
  yaw = _yaw_angle(robot.root_link_quat_w)
  face = wrap_to_pi(yaw - torch.atan2(d[:, 1], d[:, 0])).abs()
  ok = (
    cmd.kick_mode
    & ~cmd.kick_done
    & (along > 0.05)
    & (along < 0.40)
    & (side.abs() < 0.15)
    & (face < math.radians(60.0))
  )
  dt = env.step_dt
  t = torch.where(ok, cmd._pose_t + dt, cmd._pose_t - 2.0 * dt)
  cmd._pose_t = torch.where(cmd.kick_mode, t.clamp(0.0, KICK_POSE_S), 0.0)
  return ready


def _aim_curriculum_wide(env: ManagerBasedRlEnv, cmd) -> float:
  """v46: the wide aim sigma^2 from a running mean of the kick error."""
  if not hasattr(cmd, "_aim_err_ema"):
    cmd._aim_err_ema = math.radians(25.0)
  ev = cmd.kick_event
  if bool(ev.any()):
    cmd._aim_err_ema = 0.995 * cmd._aim_err_ema + 0.005 * float(cmd.kick_err[ev].mean())
  lo, hi = (math.radians(d) for d in KICK_AIM_CURR_DEG)
  frac = min(max((cmd._aim_err_ema - lo) / (hi - lo), 0.0), 1.0)
  w_tight, w_wide = KICK_AIM_WIDE_RANGE[1], KICK_AIM_WIDE_RANGE[0]
  wide = w_tight + (w_wide - w_tight) * frac
  log = env.extras.setdefault("log", {})
  log["Metrics/kick_aim_wide_sigma2"] = torch.tensor(wide)
  log["Metrics/kick_aim_err_ema_deg"] = torch.tensor(math.degrees(cmd._aim_err_ema))
  return wide


def kick_line_up(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Before the kick: trunk near the spot KICK_SETUP_DIST behind the ball along
  the kick direction, facing that way (side steps line it up)."""
  cmd, robot_xy, ball_xy, _, _ = _state(env)
  spot = ball_xy - KICK_SETUP_DIST * cmd.ball_cmd_dir_w
  near = torch.exp(-torch.linalg.norm(robot_xy - spot, dim=-1) / 0.5)
  yaw = _yaw_angle(env.scene["robot"].data.root_link_quat_w)
  kick_yaw = torch.atan2(cmd.ball_cmd_dir_w[:, 1], cmd.ball_cmd_dir_w[:, 0])
  face = 0.5 * (1.0 + torch.cos(yaw - kick_yaw))
  # v26: fades with the time already spent waiting in the window; v25 parked
  # 0.2 m short of the spot for angled kicks and collected this term all window.
  fade = torch.exp(-cmd.kick_wait / KICK_LINE_UP_TAU)
  return (cmd.kick_mode & ~cmd.kick_done).float() * near * face * fade


def kick_stand(env: ManagerBasedRlEnv) -> torch.Tensor:
  """After the kick and its 0.6 s follow-through: stand still until the command
  changes (user). Paid, not a penalty for moving (kick lesson 10)."""
  cmd = _dribble(env)
  robot = env.scene["robot"].data
  v = robot.root_link_lin_vel_w[:, :2]
  wz = robot.root_link_ang_vel_w[:, 2]
  r = torch.exp(-v.square().sum(dim=-1) / 0.04) * torch.exp(-wz.square() / 0.25)
  return (_kicked(cmd) & (cmd.time_since_kick > 0.6)).float() * r


def kick_side(env: ManagerBasedRlEnv) -> torch.Tensor:
  """v27 B-Human side kick (bhuman_kick ``ball_sole_yaw``): on the kick, the
  kicking foot turned ~90 deg to the kick direction (inside of the foot), times
  the aim, so only kicks that go the right way pay (their direction gate)."""
  cmd = _dribble(env)
  wide, sharp = KICK_AIM_SIGMA2
  err2 = cmd.kick_err.square()
  aim = 0.5 * (torch.exp(-err2 / wide) + torch.exp(-err2 / sharp))
  # v35 (user: geometry first): only kicks that turn the ball more than
  # SIDE_GATE off the robot-to-ball line; straight kicks stay pure power.
  angled = (cmd.kick_offset > SIDE_GATE).float()
  # v38 (user: then outcome): x ground speed / 7 m/s, so weak inside taps pay ~0.
  outcome = (cmd.kick_speed / KICK_VEL_TARGET).clamp(max=1.0) if SIDE_OUTCOME else 1.0
  return cmd.kick_event.float() * cmd.kick_sole_ratio * aim * angled * outcome


SIDE_GATE = math.radians(float(DRIBBLE_GENES.get("side_gate_deg", 0.0)))
"""v35: kick_side pays only for kick windows whose direction is more than this
off the robot-to-ball line at the window start (0 = every kick, v27-v34)."""
SIDE_OUTCOME = bool(DRIBBLE_GENES.get("side_outcome", False))
"""v38: kick_side also scales with the kick's ground speed / 7 m/s (to 1)."""


PUSH_AHEAD_DIST = 1.5
"""v27 ball_ahead: the ball's preferred lead along the command (m), user's
"push it 1-2 m ahead and sprint after it"."""


def push_ahead(env: ManagerBasedRlEnv) -> torch.Tensor:
  """v27, per launch in a fast dribble window (push_frac > 0): ball speed along
  the command right after the touch over 1.3 s, to 1, so each push sends the
  ball out ahead of the robot instead of a close tap."""
  cmd = _dribble(env)
  s = cmd.ball_cmd_speed
  r = (cmd.launch_along / (1.3 * s.clamp(min=0.2))).clamp(0.0, 1.0)
  fast = _push_frac(s) * (~cmd.kick_mode).float()
  return cmd.launch_event.float() * r * fast


def ball_ahead(env: ManagerBasedRlEnv) -> torch.Tensor:
  """v27, fast dribble windows after the first touch: the ball 1-2 m ahead of
  the trunk along the command. A ramp, lead / 1.5 up to 1, flat to 2 m, then
  down to 0 at 3 m, x push_frac. A kernel centred on 1.5 m paid ~0.03 at the
  policy's current 0.4 m lead (v26 probe: p50 0.38, p90 0.78 m)."""
  cmd, robot_xy, ball_xy, _, _ = _state(env)
  lead = torch.sum((ball_xy - robot_xy) * cmd.ball_cmd_dir_w, dim=-1)
  r = (lead / PUSH_AHEAD_DIST).clamp(0.0, 1.0) - (lead - 2.0).clamp(0.0, 1.0)
  # Paid while chasing, so pushing the ball ahead and standing does not farm it.
  v_r = env.scene["robot"].data.root_link_lin_vel_w[:, :2]
  chase = torch.sum(v_r * cmd.ball_cmd_dir_w, dim=-1) / cmd.ball_cmd_speed.clamp(
    min=0.2
  )
  r = r * chase.clamp(0.0, 1.0)
  active = cmd.has_touched & ~cmd.kick_mode & (cmd.ball_cmd_speed > 0.0)
  return active.float() * r * _push_frac(cmd.ball_cmd_speed)


KICK_GROUP_TERMS = (
  "kick_power",
  "kick_line_up",
  "kick_stand",
  "kick_wait_cost",
  "kick_side",
)
"""v27: reward terms of the kick critic's group (the rest of the env reward
stays the task group)."""


def kick_wait_cost(env: ManagerBasedRlEnv) -> torch.Tensor:
  """1 per step in a kick window still without its kick after KICK_WAIT_FREE_S."""
  cmd = _dribble(env)
  return (cmd.kick_mode & ~cmd.kick_done & (cmd.kick_wait > KICK_WAIT_FREE_S)).float()


TILT_GUARD_FREE = math.sin(math.radians(10.0))
"""tilt_guard is free up to 10 deg of trunk tilt (v17's p90 in the runner sim)."""


def tilt_guard(env: ManagerBasedRlEnv) -> torch.Tensor:
  """v20: linear hinge on trunk tilt beyond 10 deg (|gravity_xy| in the trunk
  frame), at every speed. ``upright`` is a soft kernel that still pays ~72 %
  at 15 deg; v19's faster style mix leaned 16.5 deg at 0.5 m/s with it on."""
  g = env.scene["robot"].data.projected_gravity_b
  return (torch.linalg.norm(g[:, :2], dim=-1) - TILT_GUARD_FREE).clamp(min=0.0)


def fov_recheck_reward(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Active 2D (horizontal + vertical) FOV re-check: keep ball_age_obs fresh when
  near the ball, with a pre-touch 2D gaze bonus when the ball is inside both
  horizontal and vertical FOV within 0.45 m."""
  cmd, _, _, _, d = _state(env)
  s = cmd.ball_cmd_speed
  near = 0.5 + FAST_FRESH_EXTRA * _fast_frac(s) + PUSH_FRESH_EXTRA * _push_frac(s)
  freshness = cmd.ball_age_obs * torch.exp(-1.5 * (d - near).clamp(min=0.0))
  pre_touch_gaze = ((cmd.see_ball > 0.5) & (d < 0.45)).float() * 0.5
  fade = 1.0 - FAST_VIEW_FADE * _fast_frac(cmd.ball_cmd_speed)
  return torch.where(
    cmd.ball_lost, torch.zeros_like(freshness), (freshness + pre_touch_gaze) * fade
  )


def dribble_view(env: ManagerBasedRlEnv) -> torch.Tensor:
  """approach_view, faded by FAST_VIEW_FADE at fast commands (v15d)."""
  fade = 1.0 - FAST_VIEW_FADE * _fast_frac(_dribble(env).ball_cmd_speed)
  return approach_view(env) * fade


def fast_dribble_drive(env: ManagerBasedRlEnv) -> torch.Tensor:
  """v15: speed with the ball at fast commands. min(ball, robot) speed along the
  command / s, clipped to [0, 1], times the speed gate, after the first touch,
  scaled by _fast_frac(s). Linear right up to the command: in v14 the task
  reward stopped rising above ~0.9 m/s robot speed at a 1.5 m/s command."""
  cmd, _, _, v, d = _state(env)
  s = cmd.ball_cmd_speed
  c_hat = cmd.ball_cmd_dir_w
  v_r = env.scene["robot"].data.root_link_lin_vel_w[:, :2]
  u = torch.minimum(torch.sum(v * c_hat, dim=-1), torch.sum(v_r * c_hat, dim=-1))
  r = (u / s.clamp(min=0.2)).clamp(0.0, 1.0) * _dist_gate(d, s) * _fast_frac(s)
  return torch.where(cmd.has_touched & (s > 0.0), r, torch.zeros_like(r))


def lost_ball_spin(env: ManagerBasedRlEnv) -> torch.Tensor:
  """When ball_lost (unseen >= 1.5 s or missing in view >= 0.5 s): spin in the
  history-conditioned direction cmd.lost_dir as fast as possible + look into the turn."""
  cmd = _dribble(env)
  robot = env.scene["robot"].data
  wz = robot.root_link_ang_vel_b[:, 2]
  head_yaw = robot.joint_pos[:, 0]
  spin_body = (wz * cmd.lost_dir / 1.5).clamp(-1.0, 1.0)
  spin_head = 0.3 * (head_yaw * cmd.lost_dir / 0.8).clamp(-1.0, 1.0)
  return (cmd.ball_lost & ~_kicked(cmd)).float() * (spin_body + spin_head)


LOST_HEAD_PITCH = math.radians(float(DRIBBLE_GENES.get("lost_head_pitch_deg", 15.0)))
"""v50: head pitch (+ = down) to hold while the ball is lost. The search ran with
the head ~40 deg down: the camera's +-21 deg vertical view then ends ~2-3 m out,
so a ball 3-4 m away stayed unseen however fast the robot spun."""


def lost_head_up(env: ManagerBasedRlEnv) -> torch.Tensor:
  """When ball_lost: head pitch near LOST_HEAD_PITCH (looks far while spinning)."""
  cmd = _dribble(env)
  pitch = env.scene["robot"].data.joint_pos[:, 1]
  r = torch.exp(-(pitch - LOST_HEAD_PITCH).square() / math.radians(15.0) ** 2)
  return (cmd.ball_lost & ~_kicked(cmd)).float() * r


def apply_dribble_rewards(cfg: ManagerBasedRlEnvCfg) -> None:
  """Iter-4 §6: upright 2.0; approach terms that conflict with dribbling are off;
  approach_view 0.5; approach_speed_limit and the AMP walk regularisers stay."""
  for name in (
    "approach_align",
    "approach_close",
    "approach_stand",
    "approach_heading",
    "approach_bad_contact",
  ):
    cfg.rewards[name].weight = 0.0
  cfg.rewards["approach_view"].weight = 1.5
  cfg.rewards["approach_view"].func = dribble_view
  cfg.rewards["upright"].weight = 2.0
  for name, func, weight in (
    ("dribble_window_success", dribble_window_success, 25.0),
    ("ball_progress", ball_progress, 5.0),
    ("ball_vel_cmd_tracking", ball_vel_cmd_tracking, 8.0),
    ("ball_stop_tracking", ball_stop_tracking, 1.5),
    ("ball_proximity", ball_proximity, 0.3),
    ("approach_progress", approach_progress, 1.0),
    ("follow_ball_heading", follow_ball_heading, 0.5),
    ("post_touch_body_align", post_touch_body_align, 4.0),
    ("stepover_backtap_turn", stepover_backtap_turn, 4.0),
    ("alternate_leg_dribble", alternate_leg_dribble, 2.0),
    ("bad_touch", bad_touch, -1.0),
    ("redirect_bonus", redirect_bonus, 20.0),
    ("fov_recheck", fov_recheck_reward, 3.0),
    (
      "fast_dribble_drive",
      fast_dribble_drive,
      float(DRIBBLE_GENES.get("drive_w", 6.0)),  # v31 gene
    ),
    (
      "lost_ball_spin",
      lost_ball_spin,
      float(DRIBBLE_GENES.get("lost_spin_w", 1.0)),  # v47 gene
    ),
    ("termination_penalty", termination_penalty, -100.0),
    ("approach_speed_limit", dribble_speed_limit, -10.0),
  ):
    cfg.rewards[name] = RewardTermCfg(func=func, weight=weight)
  if float(DRIBBLE_GENES.get("lost_head_w", 0.0)) != 0.0:
    cfg.rewards["lost_head_up"] = RewardTermCfg(
      func=lost_head_up, weight=float(DRIBBLE_GENES["lost_head_w"])
    )
  if "tilt_guard" in DRIBBLE_GENES:
    cfg.rewards["tilt_guard"] = RewardTermCfg(
      func=tilt_guard, weight=float(DRIBBLE_GENES["tilt_guard"])
    )
  if float(DRIBBLE_GENES.get("kick_prob", 0.0)) > 0.0:
    # v22 kick mode. Event weights as the kick loop's (kick_vel 900, long power
    # up to 2000): rewards are scaled by dt, so a 7 m/s kick on line pays 30.
    for name, func, weight in (
      ("kick_power", kick_power, float(DRIBBLE_GENES.get("kick_power_w", 1500.0))),
      ("kick_line_up", kick_line_up, 4.0),
      ("kick_stand", kick_stand, 3.0),
      ("kick_wait_cost", kick_wait_cost, float(DRIBBLE_GENES.get("kick_wait_w", -1.0))),
    ):
      cfg.rewards[name] = RewardTermCfg(func=func, weight=weight)
  # v27: push-and-chase incentives and the B-Human side kick, by gene weight.
  for gene, name, func in (
    ("push_w", "push_ahead", push_ahead),
    ("ahead_w", "ball_ahead", ball_ahead),
    ("side_w", "kick_side", kick_side),
    ("fast_fall_w", "fast_fall", fast_fall),
  ):
    if float(DRIBBLE_GENES.get(gene, 0.0)) != 0.0:
      cfg.rewards[name] = RewardTermCfg(func=func, weight=float(DRIBBLE_GENES[gene]))

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

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch

from mjlab.entity import Entity
from mjlab.envs.mdp.actions import JointPositionAction, JointPositionActionCfg
from mjlab.envs.mdp.dr._core import _get_entity_indices
from mjlab.envs.mdp.events import push_by_setting_velocity
from mjlab.managers.event_manager import RecomputeLevel, requires_model_fields
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.tasks.velocity.mdp.approach import (
  BALL_RADIUS,
  NOMINAL_ROOT_HEIGHT,
  STAND_DISTANCE,
  WALK_COMMAND_SPEED,
  YAW_ALIGN_LIMIT,
  ApproachYawCommand,
  ApproachYawCommandCfg,
  _command,
  _current,
  _yaw_angle,
  ball_radius,
)
from mjlab.utils.lab_api.math import quat_apply_inverse, quat_mul, yaw_quat

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv


# Short / medium / long kicks; the kick-range one-hot uses the same edges.
# Long (v33): 8 m and beyond, kicked hard (LONG_KICK_SPEED_BAND), not rolled
# to the target; 8–10 m before.
TARGET_BINS = ((1.0, 4.0), (4.0, 8.0), (8.0, 20.0))
RANGE_EDGES = (4.0, 8.0)
# Within this distance the robot should line up and kick quickly.
NEAR_DISTANCE = 1.5
# Body-heading shaping ramps in from here to the stand distance.
HEADING_FAR = 2.0
# A touch is a kick if the ball leaves at ≥ KICK_MIN_SPEED after a jump.
KICK_MIN_SPEED = 1.0
KICK_MIN_JUMP = 0.8
KICK_VEL_REF = 3.0
# v54: short / medium kick_vel reference = min(KICK_VEL_REF, needed speed).
KICK_VEL_CAP_AT_NEEDED = True
# v54b: rest-accuracy score scale (m) and linear short / medium speed match.
REST_MISS_SCALE = 2.0
LINEAR_SPEED_MATCH = True
# Long-range kicks (range one-hot "long"): ball speed 7–8 m/s; kick_vel pays
# up to LONG_KICK_VEL_REF and kick_vel_accurate is 1 inside the band.
LONG_KICK_SPEED_BAND = (7.0, 8.0)
LONG_KICK_VEL_REF = 7.5
LONG_KICK_SPEED_SIGMA = 1.0
# v34: the long-kick speed band starts where the policy can reach it and moves
# up LONG_BAND_STEP each time LONG_BAND_SUCCESS of recent long kicks land in it,
# until it reaches LONG_KICK_SPEED_BAND. v33's fixed 7–8 m/s band paid ~0 below
# 6 m/s and long kicks stayed at 3.3 m/s.
# v35: the band is on the kicking-foot speed relative to the body at impact
# (what the robot controls), not ball speed: with balls up to 0.25 kg an
# absolute ball-speed band was out of reach for many balls (v34). A scripted
# swing in this sim launches the 0.1 kg ball at 7–12 m/s (balance aside), so
# the motors allow 7–8 m/s; the curriculum stops where kicking stays reliable.
# v46: fixed target 6.5 m/s (start = final): with a monotonic ramp the
# curriculum is not needed for a gradient, and it stalled at 4.5 m/s because
# only 10–25 % of long kicks reached it (40 % needed).
LONG_BAND_START = (6.5, 7.5)
LONG_FOOT_BAND_FINAL = (6.5, 7.5)
# v36: long_kick_power is a monotonic ramp from LONG_SWING_FLOOR up to the
# current target (long_band_lo), 1 at or above it. The v35 band (sigma 1.5)
# still paid 0.83 for a 3.1 m/s swing against a 3.75 m/s band, so nothing
# pulled the swing up and the band stalled at 3.75 for 350 iterations.
LONG_SWING_FLOOR = 2.5
# v50d: 0.9 → 0.7. At 0.9 (v50c) long kicks rose 3.98 → 4.83 m/s but setup
# slowed (near-ball time 2.7 → 3.1 s, goals 1.00 → 0.91).
STRIKE_EFFICIENCY = 0.7
# v45: kick_direction pays in full only for kicks reaching this fraction of the
# rolling speed the target needs.
KICK_DIR_SPEED_FRACTION = 0.7
# walk_speed pays speed toward the ball over this fixed reference (v35); with
# speed / cap the pay per m/s fell as caps rose and v34 walked slower.
WALK_SPEED_REF = 1.0
LONG_BAND_STEP = 0.25
LONG_BAND_SUCCESS = 0.4
LONG_BAND_EMA = 0.02  # per long kick
LONG_POWER_SIGMA = 1.5
# v34 speed caps (policy inputs 75–77), ramped in from the v31 maxima over
# SPEED_CAP_RAMP_STEPS env steps. Backward speed is capped at BACKWARD_SPEED_MAX.
SPEED_CAP_FINAL = ((0.3, 2.0), (0.2, 1.5), (0.4, 1.5))
# v34 ramped from (1.2, 1.0, 1.25); runs resuming from v34 or later start at
# the final caps.
SPEED_CAP_START_MAX = (2.0, 1.5, 1.5)
SPEED_CAP_RAMP_STEPS = 300 * 24
BACKWARD_SPEED_MAX = 1.75
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
MAX_TARGET_DISTANCE = 25.0
# A real kick: support nearly still, kicking foot swinging fast relative to
# the body. v13/v16 "kicked" at 0.9 m/s body speed with the foot only 1 m/s
# faster than the body: running into the ball, not kicking it.
KICK_BODY_SPEED_SCALE = 0.4
# K2 (v57): momentum kicks. Kick quality only counts body motion that is not
# toward the kick direction (sideways, backward, or faster than
# MOMENTUM_KICK_MAX_SPEED forward), and the swing is the kicking foot's
# world speed, so walking into the ball counts. B-Human kicks at 0.8 m/s
# body speed (foot 1.4 m/s over the body) and reaches 8.2 m/s on long kicks;
# the old standstill score paid that ~1 %.
MOMENTUM_KICKS = True
MOMENTUM_KICK_MAX_SPEED = 1.0
# K2 (v57): kick speed is the ball's 3D speed (B-Human measures it so).
KICK_SPEED_3D = True
# K4 (v59): AMP style on near the ball (kick clips are in the style data).
KICK_STYLE_AMP = True
# K4b (v60): kick quality × this when the support foot is off the ground.
SUPPORT_PLANT_FACTOR = 0.5
# Kick styles in one policy (2026-10-06, user): B-Human's inside-foot kick and
# a hop kick, chosen by situation without new inputs. STYLE_MAP:
#   "off"   - no style terms (champion recipe);
#   "range" - short / medium kicks with the inside of the foot, long kicks
#             with a hop (the range one-hot already tells the policy which);
#   "free"  - both styles paid in every range, outcome rewards pick.
# Evidence (kick_anatomy, x4 champion): its hop long kicks reach 5.93 m/s vs
# 5.09 planted at equal aim; B-Human's inside-foot kicks are 99 % within 20 deg
# and its short passes softer (2.6 vs 3.9 m/s).
STYLE_MAP = "off"
# Inside-foot target: signed foot yaw to the kick line (toe-out positive),
# raised from INSIDE_YAW_START to π/2 in INSIDE_YAW_STEP steps whenever
# INSIDE_SUCCESS of the styled kicks match (B-Human raises its sole-yaw target
# 0 -> 90 deg by hand; our ramp-reward attempt at a fixed 90 deg found 1 %).
INSIDE_YAW_START = 0.35
INSIDE_YAW_STEP = 0.15
INSIDE_SIGMA = 0.35
INSIDE_SUCCESS = 0.4
# Share of a styled kick's quality (all kick rewards) that depends on using
# the mapped style (B-Human scales its direction reward by 0.5 + 0.5 x sole).
STYLE_SHARE_INSIDE = 0.5
STYLE_SHARE_HOP = 0.0
# Range styles: quality factor for a short / medium kick without the support
# foot on the ground (the inside-foot pass is a planted kick; sty_power/17149
# hopped into 56 % of its passes and late falls rose 0.35 -> 1.8 %).
SHORT_PLANT_FACTOR = 1.0
KICK_SWING_MIN = 1.0
KICK_SWING_SPAN = 1.5
# Scripted head (v21): the policy pointed the camera up near the pitch limit
# (-0.3 rad) and nothing on the robot could steer it. The head now looks at
# the ball estimate the actor sees; the runner uses the same tracker.
HEAD_PIVOT_B = (0.0056, 0.0, 0.2149)  # Head_1 in the trunk frame, default pose
TRUNK_HEIGHT = 0.55
HEAD_YAW_LIMIT = 0.85
HEAD_PITCH_LIMITS = (-0.25, 0.82)  # positive looks down; joint −0.349…0.855
# Aim this far below the ball (about half the vertical half-FOV), so the ball
# sits in the upper image and stays in view as it comes close. Centred, it
# left the 21° vertical view early and on the robot the head looked too high.
HEAD_LOOK_DOWN = 0.18
HEAD_FILTER_ALPHA = 0.3
HEAD_MAX_STEP = 0.06  # rad per 20 ms policy step (3 rad/s)
HEAD_DEFAULT = (0.0, 0.4)
# Share of episodes where the head scans instead of tracking, so the policy
# copes with a head it does not control (a user steering it on the robot).
HEAD_SCAN_SHARE = 0.2
HEAD_SCAN_YAW = 0.8
HEAD_SCAN_PERIOD = 4.0
# Search (v27): with the robot's memory (no odometry) the stale estimate
# often points where the ball no longer is. Unseen for HEAD_SEARCH_AFTER s,
# the head sweeps yaw and alternates near / far pitch until it sees the ball.
HEAD_SEARCH_AFTER = 0.5
HEAD_SEARCH_YAW = 0.8
HEAD_SEARCH_YAW_PERIOD = 3.0
HEAD_SEARCH_PITCH = (0.55, 0.2)  # centre, amplitude
HEAD_SEARCH_PITCH_PERIOD = 1.5
# Lost close to the robot (v28): walking onto the ball, it leaves the bottom
# of the image while the no-odometry memory still says it is farther. Look
# straight down at once, and sweep yaw down there, instead of the mid sweep
# (v27 at 0.4–0.7 m: seen 51 %, the misses all below the image).
HEAD_LOST_AFTER = 0.2
HEAD_NEAR_LOST = 1.5
# Posture (v21). Default-pose knee spacing is ~0.19 m; kicks closed it to
# 0.09–0.12 m in the runner sim.
KNEE_GAP_MIN = 0.16
# Walking pose (v29), from the gold AMP walk in the runner sim: base 0.544 m,
# feet 0.15 m apart, knees outside the feet. v28 walked at 0.48 m, feet 0.25 m
# apart, knees inside the feet (knock-kneed), 6.9 steps/s. Paid only where the
# style gate is on (not around kicks), so the kick itself is free.
WALK_BASE_HEIGHT = 0.52  # v34 (0.54 in v29–v33)
WALK_HEIGHT_DEADBAND = 0.01
# Foot link origin above flat ground while walking (measured, v47/8800).
FOOT_LINK_HEIGHT = 0.040
WALK_HEIGHT_SCALE = 0.02
# v53: upper edge +3 → +1°. v50d leaned +2.2° mean / 5.1° p90 at 1.0–1.5 m/s,
# mostly inside the old band, so only the tail paid (doubling the weight in
# v51 changed nothing).
TRUNK_PITCH_BAND_DEG = (-5.0, 1.0)
TRUNK_PITCH_SCALE_DEG = 2.0
# v48 diagnostic: upper pitch limit when walking faster than this (None = off).
TRUNK_PITCH_FAST_SPEED = 1.2
TRUNK_PITCH_FAST_UPPER_DEG: float | None = None  # diagnostic, off
WALK_STANCE_WIDTH = (0.12, 0.19)
# v31: the pose terms apply only beyond this distance from the ball. Applied up
# to the style gate (0.6 m), v29/v30 arrived in the narrow walking stance and
# kick quality fell 0.85 → 0.78 (two seeds); the last metre sets up the kick.
WALK_POSE_MIN_DIST = 1.0
# Kick promptness (v27): kick rewards × (0.5 + 0.5·exp(-near time / tau)),
# near time = time within NEAR_DISTANCE before the kick. A multiplier, not a
# time cost: zone-tied time costs fenced the ball off in stage3_v1.
PROMPT_KICK_TAU = 1.5
# Promptness floor: the kick-reward factor after a long dither near the ball
# (0.5 = a slow kick still earns half; gene k.PROMPT_FLOOR, 2026-10-07).
PROMPT_FLOOR = 0.5
KNEE_GAP_SCALE = 0.02


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


# v55: kicks launched above LOFT_FREE_DEG lose speed reward linearly, none at
# LOFT_ZERO_DEG. v53 lofted long kicks (median peak 12 cm, 41 % above 15 cm);
# planar speed paid for them in sim, but on the real robot they bounce and the
# ball's forward speed was weaker (user report, 2026-10-05).
# K2 (v57): 5 / 20° → 20 / 35°. The user accepts low drives / air balls;
# B-Human's long kicks launch at ~+11° and reach 8.2 m/s 3D in our sim.
LOFT_FREE_DEG = 20.0
LOFT_ZERO_DEG = 35.0
LOFT_PENALTY = True


def loft_factor(angle: torch.Tensor) -> torch.Tensor:
  """1 for a launch angle ≤ LOFT_FREE_DEG, 0 at ≥ LOFT_ZERO_DEG, linear between."""
  if not LOFT_PENALTY:
    return torch.ones_like(angle)
  lo, hi = math.radians(LOFT_FREE_DEG), math.radians(LOFT_ZERO_DEG)
  return (1.0 - (angle - lo) / (hi - lo)).clamp(0.0, 1.0)


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


def head_track_angles(
  ball_b: torch.Tensor,
  pivot: tuple[float, float, float] = HEAD_PIVOT_B,
  ball_z: float = BALL_RADIUS - TRUNK_HEIGHT,
  camera_pitch: float = 0.0,
  look_down: float = HEAD_LOOK_DOWN,
) -> torch.Tensor:
  """(yaw, pitch) that point the head at a ball at trunk-frame xy ``ball_b``.

  Pitch is positive looking down; ``camera_pitch`` is the optical axis below
  the head x-axis; ``look_down`` aims below the ball. Clamped to the head's
  range.
  """
  dx = ball_b[..., 0] - pivot[0]
  dy = ball_b[..., 1] - pivot[1]
  dz = ball_z - pivot[2]
  yaw = torch.atan2(dy, dx).clamp(-HEAD_YAW_LIMIT, HEAD_YAW_LIMIT)
  pitch = torch.atan2(torch.full_like(dx, -dz), torch.hypot(dx, dy))
  pitch = pitch - camera_pitch + look_down
  pitch = pitch.clamp(*HEAD_PITCH_LIMITS)
  return torch.stack((yaw, pitch), dim=-1)


def head_search_angles(lost_s: torch.Tensor) -> torch.Tensor:
  """Search sweep after ``lost_s`` seconds unseen (starts at the centre)."""
  t = (lost_s - HEAD_SEARCH_AFTER).clamp(min=0.0)
  yaw = HEAD_SEARCH_YAW * torch.sin(6.2832 * t / HEAD_SEARCH_YAW_PERIOD)
  centre, amp = HEAD_SEARCH_PITCH
  pitch = centre + amp * torch.cos(6.2832 * t / HEAD_SEARCH_PITCH_PERIOD)
  return torch.stack((yaw, pitch), dim=-1)


def head_goal(
  ball_b: torch.Tensor, lost_s: torch.Tensor, camera_pitch: float = 0.0
) -> torch.Tensor:
  """Tracker goal from the actor's ball estimate and time since last seen.

  Seen (or lost < HEAD_LOST_AFTER): look at the estimate. Lost close
  (estimate within HEAD_NEAR_LOST): look down at the pitch limit, sweeping
  yaw after HEAD_SEARCH_AFTER. Lost far for HEAD_SEARCH_AFTER: full sweep.
  """
  goal = head_track_angles(ball_b, camera_pitch=camera_pitch)
  sweep = head_search_angles(lost_s)
  near = ball_b.norm(dim=-1) < HEAD_NEAR_LOST
  searching = lost_s > HEAD_SEARCH_AFTER
  down_yaw = torch.where(searching, sweep[..., 0], goal[..., 0])
  down = torch.stack((down_yaw, torch.full_like(down_yaw, HEAD_PITCH_LIMITS[1])), -1)
  lost_near = (lost_s > HEAD_LOST_AFTER) & near
  goal = torch.where(lost_near.unsqueeze(-1), down, goal)
  return torch.where((searching & ~near).unsqueeze(-1), sweep, goal)


def head_step(
  current: torch.Tensor,
  goal: torch.Tensor,
  alpha: float = HEAD_FILTER_ALPHA,
  max_step: float = HEAD_MAX_STEP,
) -> torch.Tensor:
  """Low-pass toward ``goal``, then limit the change per step."""
  delta = (alpha * (goal - current)).clamp(-max_step, max_step)
  return current + delta


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
    # Ball launch angle above the ground at the kick (rad) and its loft factor.
    self.kick_launch_angle = zeros()
    # Kicking-foot yaw relative to the kick direction at contact, |rad| (side
    # foot ≈ π/2, front ≈ 0).
    self.kick_foot_yaw = zeros()
    # Situational style statistics (2026-10-07, user: learn when front or side
    # foot is best given speed and accuracy). Cells: range bin (3) x redirect
    # (3); styles: front / side / other, x hop (6). EMA of the outcome score.
    self.style_score = torch.zeros(9, 6, device=dev)
    self.style_count = torch.zeros(9, 6, device=dev)
    self.kick_style_adv = zeros()
    # Style at contact: inside-foot match (0-1, current curriculum target) and
    # hop (both feet off the ground).
    self.kick_inside = zeros()
    self.kick_hop = flag()
    self.last_kick_hop = flag()
    self.inside_target = INSIDE_YAW_START
    self.inside_hit = 0.0
    self.inside_count = 0
    self.kick_loft = torch.ones(n, device=dev)
    self.kick_cos = zeros()
    self.kick_speed_req = zeros()
    # Whether the latest kick was a long-range one (range one-hot at the kick).
    self.kick_long = flag()
    # v54: where a short / medium kick should stop (target and tolerance at the
    # kick), pending until the ball rests; rest_event / rest_score on that step.
    self.rsi_start = flag()  # episode started mid-kick (K4b)
    self.rest_pending = flag()
    self.rest_event = flag()
    self.rest_score = zeros()
    self.rest_target_w = torch.zeros(n, 2, device=dev)
    self.rest_tol = torch.ones(n, device=dev)
    # Long-kick speed band (curriculum, shared by all envs) and its hit rate.
    self.long_band_lo = float(cfg.long_band_start[0])
    self.long_band_width = float(cfg.long_band_start[1] - cfg.long_band_start[0])
    self.long_band_hit = 0.0
    self.long_band_count = 0
    self._own_steps = 0  # env steps seen by this command (speed-cap ramp)
    self.prev_ball_speed = zeros()
    self.goal_tol = torch.ones(n, device=dev)
    self.prev_heading_phi = zeros()
    self.smoothed_vel = torch.zeros(n, 3, device=dev)
    self.style_gate = torch.ones(n, device=dev)
    # The AMP runner reads this to switch style off around kicks only.
    # K4 (v59): with kick clips in the AMP data, style stays on near the ball
    # too (the walking pose terms still use style_gate).
    self.amp_gate = self.style_gate if not KICK_STYLE_AMP else torch.ones(n, device=dev)
    env.amp_style_gate = self.amp_gate  # ty: ignore[unresolved-attribute]

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
      self.kick_long,
      self.rsi_start,
      self.rest_pending,
      self.rest_event,
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
      self.kick_launch_angle,
      self.kick_cos,
      self.kick_quality,
      self.last_kick_quality,
      self.kick_body_speed,
      self.kick_foot_rel,
      self._kick_quality_sum,
      self.kick_speed_req,
      self.rest_score,
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
    if self.cfg.speed_cap_final is not None and len(env_ids) > 0:
      # Counted by this command, not env.common_step_counter: on resume the
      # runner sets that to the checkpoint's iteration and the ramp would be
      # skipped.
      steps = float(self._own_steps)
      ramp = min(1.0, steps / max(1.0, float(self.cfg.speed_cap_ramp_steps)))
      for i, ((lo, hi), start_hi) in enumerate(
        zip(self.cfg.speed_cap_final, self.cfg.speed_cap_start_max, strict=True)
      ):
        top = start_hi + ramp * (hi - start_hi)
        self.speed_limit[env_ids, i] = torch.empty(
          len(env_ids), device=self.device
        ).uniform_(lo, top)
      if self.cfg.cap_low_prob > 0.0:
        # L3: some episodes at runswift's low caps (0.5 / 0.3 / 0.6, +-10 %).
        low = torch.rand(len(env_ids), device=self.device) < self.cfg.cap_low_prob
        caps = torch.tensor((0.5, 0.3, 0.6), device=self.device)
        jit = 1.0 + 0.1 * (2 * torch.rand(len(env_ids), 3, device=self.device) - 1)
        self.speed_limit[env_ids] = torch.where(
          low.unsqueeze(-1), caps * jit, self.speed_limit[env_ids]
        )
    # Recorded mid-kick starts bring their own targets: off while a range is pinned.
    if self.cfg.rsi_files and len(env_ids) > 0 and self._range_pin is None:
      self._reference_state_init(env_ids)

  def _load_rsi(self) -> list[tuple[float, dict[str, torch.Tensor]]]:
    if not hasattr(self, "_rsi_sets"):
      import numpy as np

      sets = []
      for path, prob in self.cfg.rsi_files:
        d = np.load(path)
        sets.append(
          (
            prob,
            {
              k: torch.as_tensor(d[k], dtype=torch.float32, device=self.device)
              for k in d.files
            },
          )
        )
      self._rsi_sets = sets
    return self._rsi_sets

  def _reference_state_init(self, env_ids: torch.Tensor) -> None:
    """K4b: start some episodes mid-kick from recorded kicks (B-Human side-foot,
    our front kicks), ~0.2–0.4 s before contact, with the ball and target
    placed as recorded. Pose is rotated to a random heading at the robot's
    spawn position, so the policy experiences each kick style and the
    outcome rewards decide between them."""
    dev = self.device
    u = torch.rand(len(env_ids), device=dev)
    lo = 0.0
    for prob, d in self._load_rsi():
      pick = (u >= lo) & (u < lo + prob)
      lo += prob
      if not bool(pick.any()):
        continue
      ids = env_ids[pick]
      k = len(ids)
      j = torch.randint(0, d["root_pos"].shape[0], (k,), device=dev)
      root_c, quat_c = d["root_pos"][j], d["root_quat"][j]
      yaw_c = _yaw_angle(quat_c)
      yaw_n = torch.rand(k, device=dev) * (2.0 * math.pi) - math.pi
      dyaw = yaw_n - yaw_c
      c, s_ = dyaw.cos(), dyaw.sin()

      def rot(
        v: torch.Tensor, c: torch.Tensor = c, s_: torch.Tensor = s_
      ) -> torch.Tensor:
        out = v.clone()
        out[:, 0] = c * v[:, 0] - s_ * v[:, 1]
        out[:, 1] = s_ * v[:, 0] + c * v[:, 1]
        return out

      half = 0.5 * dyaw
      qz = torch.stack(
        (half.cos(), torch.zeros_like(half), torch.zeros_like(half), half.sin()), -1
      )
      quat_n = quat_mul(qz, quat_c)
      spawn = self.robot.data.root_link_pos_w[ids]
      ground = spawn[:, 2] - NOMINAL_ROOT_HEIGHT
      root_n = spawn.clone()
      root_n[:, 2] = ground + root_c[:, 2]
      state = torch.cat(
        (root_n, quat_n, rot(d["lin_vel"][j]), rot(d["ang_vel"][j])), -1
      )
      self.robot.write_root_state_to_sim(state, env_ids=ids)
      self.robot.write_joint_state_to_sim(
        d["joint_pos"][j], d["joint_vel"][j], env_ids=ids
      )
      ball_rel = rot(d["ball_pos"][j] - root_c)
      # Clips were recorded with the nominal ball; a larger ball is pushed
      # away from the robot by the extra radius so it does not start inside
      # the foot, and sits on the ground.
      dr = ball_radius(self._env, ids) - BALL_RADIUS
      away = ball_rel[:, :2] / ball_rel[:, :2].norm(dim=-1, keepdim=True).clamp(
        min=1e-6
      )
      ball_n = root_n.clone()
      ball_n[:, :2] = root_n[:, :2] + ball_rel[:, :2] + away * dr.unsqueeze(-1)
      ball_n[:, 2] = ground + d["ball_pos"][j][:, 2] + dr
      bstate = self.ball.data.default_root_state[ids].clone()
      bstate[:, 0:3] = ball_n
      bstate[:, 3:7] = torch.tensor([1.0, 0.0, 0.0, 0.0], device=dev)
      bstate[:, 7:10] = rot(d["ball_vel"][j])
      bstate[:, 10:] = 0.0
      self.ball.write_root_state_to_sim(bstate, ids)
      tgt_rel = torch.zeros(k, 3, device=dev)
      tgt_rel[:, :2] = d["target"][j] - d["ball_pos"][j][:, :2]
      self.target_w[ids] = ball_n[:, :2] + rot(tgt_rel)[:, :2]
      # The robot has just been looking at the ball.
      self.last_seen_ball_w[ids] = ball_n[:, :2]
      self.time_since_seen[ids] = 0.0
      self.ball_lost[ids] = False
      rel = torch.zeros(k, 3, device=dev)
      rel[:, :2] = ball_n[:, :2] - root_n[:, :2]
      self.last_seen_ball_b[ids] = quat_apply_inverse(yaw_quat(quat_n), rel)[:, :2]
      self.last_seen_yaw[ids] = yaw_n
      dist = (self.target_w[ids] - ball_n[:, :2]).norm(dim=-1)
      self.goal_tol[ids] = goal_tolerance(dist)
      self.rsi_start[ids] = True

  def _replace_targets(self, env_ids: torch.Tensor, ball_xy: torch.Tensor) -> None:
    super()._replace_targets(env_ids, ball_xy)
    self.goal_tol[env_ids] = goal_tolerance(self.target_dist[env_ids])
    self.kicked_since_target[env_ids] = False
    self.lined_up_latched[env_ids] = False

  def _style_stats_update(
    self, kick, foot_yaw, kick_heading, to_target, ball_speed
  ) -> None:
    """Per kick: outcome score (aim x speed for the range) per situation cell
    and style; kick_style_adv = this style's EMA score minus the cell's
    count-weighted mean score (what using this style is worth here)."""
    if not bool(kick.any()):
      self.kick_style_adv[:] = 0.0
      return
    fy = torch.rad2deg(foot_yaw)
    st = torch.where(fy < 30, 0, torch.where((fy >= 60) & (fy <= 120), 1, 2))
    gnd = self._env.scene["feet_ground_contact"].data.found
    if gnd is not None:
      hop = ~(gnd.reshape(self.num_envs, -1)[:, :2] > 0).any(-1)
      st = torch.where(hop, st + 3, st)
    td = to_target.norm(dim=-1)
    rb = torch.where(td < 4, 0, torch.where(td < 8, 1, 2))
    yaw = _yaw_angle(self.robot.data.root_link_quat_w)
    red = torch.rad2deg(
      torch.atan2(torch.sin(kick_heading - yaw), torch.cos(kick_heading - yaw)).abs()
    )
    sb = torch.where(red < 30, 0, torch.where(red < 60, 1, 2))
    cell = rb * 3 + sb
    cos = (self.ball.data.root_link_lin_vel_w[:, :2] * to_target).sum(-1) / (
      ball_speed * td
    ).clamp(min=1.0e-6)
    aim = torch.exp(-torch.square(torch.acos(cos.clamp(-1, 1)) / KICK_AIM_SIGMA))
    speed3 = self.ball.data.root_link_lin_vel_w.norm(dim=-1)
    ratio = speed3 / required_kick_speed(td, self.cfg.ball_roll_decel).clamp(min=0.5)
    spd = torch.where(
      rb == 2, (ratio / 1.5).clamp(max=1.0), (1.0 - (ratio - 1.0).abs()).clamp(min=0.0)
    )
    score = aim * spd
    k = kick.nonzero(as_tuple=False).squeeze(-1)
    idx = cell[k] * 6 + st[k]
    flat_s = self.style_score.view(-1)
    flat_c = self.style_count.view(-1)
    n_add = torch.bincount(idx, minlength=54).float()
    s_add = torch.bincount(idx, weights=score[k], minlength=54)
    a = (n_add * STYLE_STATS_RATE).clamp(max=1.0)
    mean_new = s_add / n_add.clamp(min=1.0)
    upd = n_add > 0
    first = upd & (flat_c == 0)
    flat_s[:] = torch.where(
      first, mean_new, torch.where(upd, flat_s + a * (mean_new - flat_s), flat_s)
    )
    flat_c[:] = flat_c * (1.0 - STYLE_STATS_RATE * 0.1) + n_add
    w = self.style_count / self.style_count.sum(dim=1, keepdim=True).clamp(min=1e-6)
    cell_mean = (w * self.style_score).sum(dim=1)
    seen = self.style_count[cell, st] >= STYLE_STATS_MIN
    adv = torch.where(seen, self.style_score[cell, st] - cell_mean[cell], 0.0)
    self.kick_style_adv[:] = torch.where(kick, adv, 0.0)

  def _update_command(self) -> None:
    self._own_steps += 1
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
    speed_3d = self.ball.data.root_link_lin_vel_w.norm(dim=-1)
    launch_speed = speed_3d if KICK_SPEED_3D else ball_speed
    self.kick_speed[:] = torch.where(kick, launch_speed, self.kick_speed)
    vz = self.ball.data.root_link_lin_vel_w[:, 2]
    angle = torch.atan2(vz, ball_speed.clamp(min=1.0e-3))
    self.kick_launch_angle[:] = torch.where(kick, angle, self.kick_launch_angle)
    self.kick_loft[:] = torch.where(kick, loft_factor(angle), self.kick_loft)
    # Body and kicking-foot motion at the kick (foot speed: the larger of this
    # and the last step, since the impact slows the foot).
    data = self.robot.data
    base_v = data.root_link_lin_vel_w[:, :2]
    if MOMENTUM_KICKS:
      foot_rel = data.body_link_lin_vel_w[:, self._feet_ids, :2].norm(dim=-1)
    else:
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
    if MOMENTUM_KICKS:
      u_dir = to_target / target_dist.clamp(min=1.0e-6).unsqueeze(-1)
      v_par = (base_v * u_dir).sum(dim=-1)
      v_perp = base_v[:, 0] * u_dir[:, 1] - base_v[:, 1] * u_dir[:, 0]
      off = torch.sqrt(
        v_perp**2
        + v_par.clamp(max=0.0) ** 2
        + (v_par - MOMENTUM_KICK_MAX_SPEED).clamp(min=0.0) ** 2
      )
      quality = kick_quality_score(off, swing)
    else:
      quality = kick_quality_score(body, swing)
    if SUPPORT_PLANT_FACTOR < 1.0:
      # K4b: the support foot (not the kicking one) must be on the ground at
      # contact. v58 kicked with both feet off the ground in 28 % of kicks
      # (B-Human 2 %): a hop into the ball.
      gfound = self._env.scene["feet_ground_contact"].data.found
      if gfound is not None:
        ground = gfound.reshape(self.num_envs, -1)[:, :2] > 0
        planted = ground[rows, 1 - which]
        quality = quality * torch.where(planted, 1.0, SUPPORT_PLANT_FACTOR)
    fq = data.body_link_quat_w[:, self._feet_ids][rows, which]
    foot_yaw = torch.atan2(
      2 * (fq[:, 0] * fq[:, 3] + fq[:, 1] * fq[:, 2]),
      1 - 2 * (fq[:, 2] ** 2 + fq[:, 3] ** 2),
    )
    kick_heading = torch.atan2(to_target[:, 1], to_target[:, 0])
    rel_yaw = torch.atan2(
      torch.sin(foot_yaw - kick_heading), torch.cos(foot_yaw - kick_heading)
    )
    self.kick_foot_yaw[:] = torch.where(kick, rel_yaw.abs(), self.kick_foot_yaw)
    self._style_stats_update(kick, rel_yaw.abs(), kick_heading, to_target, ball_speed)
    if STYLE_MAP != "off":
      # Inside of the foot: left foot toe-out = +yaw, right foot toe-out = -yaw.
      toe_out = rel_yaw * torch.where(which == 0, 1.0, -1.0)
      amount = torch.where(toe_out > 0.5 * math.pi, math.pi - toe_out, toe_out)
      gap = (self.inside_target - amount).clamp(min=0.0)
      inside = torch.exp(-torch.square(gap / INSIDE_SIGMA))
      gnd = self._env.scene["feet_ground_contact"].data.found
      hop = (
        ~(gnd.reshape(self.num_envs, -1)[:, :2] > 0).any(-1)
        if gnd is not None
        else torch.zeros_like(kick)
      )
      long_now = self.kick_range[:, 2] > 0.5
      if STYLE_MAP == "range":
        share = torch.where(long_now, STYLE_SHARE_HOP, STYLE_SHARE_INSIDE)
        match = torch.where(long_now, hop.float(), inside)
        quality = quality * (1.0 - share + share * match)
        if SHORT_PLANT_FACTOR < 1.0:
          quality = quality * torch.where(long_now | ~hop, 1.0, SHORT_PLANT_FACTOR)
        styled = kick & ~long_now
      else:
        styled = kick
      self.kick_inside[:] = torch.where(kick, inside, self.kick_inside)
      self.kick_hop[:] = torch.where(kick, hop, self.kick_hop)
      self.last_kick_hop[:] = torch.where(kick, hop, self.last_kick_hop)
      n_st = int(styled.sum())
      if n_st > 0:
        hit = float((inside[styled] > 0.5).float().mean())
        a = min(1.0, LONG_BAND_EMA * n_st)
        self.inside_hit += a * (hit - self.inside_hit)
        self.inside_count += n_st
        if (
          self.inside_hit >= INSIDE_SUCCESS
          and self.inside_count >= 200
          and self.inside_target < 0.5 * math.pi
        ):
          self.inside_target = min(0.5 * math.pi, self.inside_target + INSIDE_YAW_STEP)
          self.inside_count = 0
          self.inside_hit = 0.0
      log = self._env.extras.setdefault("log", {})
      log["Metrics/inside_target"] = self.inside_target
      log["Metrics/inside_hit"] = self.inside_hit
      if kick.any():
        log["Metrics/hop_share"] = float(hop[kick].float().mean())
    self.kick_quality[:] = torch.where(kick, quality, self.kick_quality)
    self.last_kick_quality[:] = torch.where(kick, quality, self.last_kick_quality)
    self.kick_body_speed[:] = torch.where(kick, body, self.kick_body_speed)
    self.kick_foot_rel[:] = torch.where(kick, swing, self.kick_foot_rel)
    self._kick_quality_sum += torch.where(kick, quality, 0.0)
    self.prev_foot_rel[:] = foot_rel
    self.kick_cos[:] = torch.where(kick, cos, self.kick_cos)
    self.kick_long[:] = torch.where(kick, self.kick_range[:, 2] > 0.5, self.kick_long)
    long_kicks = kick & (self.kick_range[:, 2] > 0.5)
    n_long = int(long_kicks.sum())
    if n_long > 0:
      sp = swing[long_kicks]
      hit = float((sp >= self.long_band_lo).float().mean())
      a = min(1.0, LONG_BAND_EMA * n_long)
      self.long_band_hit += a * (hit - self.long_band_hit)
      self.long_band_count += n_long
      final_lo = self.cfg.long_foot_band_final[0]
      if (
        self.long_band_hit >= LONG_BAND_SUCCESS
        and self.long_band_count >= 200
        and self.long_band_lo < final_lo
      ):
        self.long_band_lo = min(final_lo, self.long_band_lo + LONG_BAND_STEP)
        self.long_band_count = 0
        self.long_band_hit = 0.0
    log = self._env.extras.setdefault("log", {})
    log["Metrics/long_band_lo"] = self.long_band_lo
    log["Metrics/long_band_hit"] = self.long_band_hit
    log["Metrics/speed_cap_ramp"] = min(
      1.0, self._own_steps / max(1.0, float(self.cfg.speed_cap_ramp_steps))
    )
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

    # v54: rest accuracy of short / medium kicks (a pass should stop near the
    # target, not run 8 m past it). Another touch cancels the pending score.
    short_kick = kick & (self.kick_range[:, 2] < 0.5)
    self.rest_target_w[:] = torch.where(
      short_kick.unsqueeze(-1), self.target_w, self.rest_target_w
    )
    self.rest_tol[:] = torch.where(short_kick, self.goal_tol, self.rest_tol)
    touched = (double | push | self.body_touch) | (kick & ~short_kick)
    self.rest_pending[:] = (self.rest_pending & ~touched) | short_kick
    rested = (
      self.rest_pending
      & ~kick
      & (ball_speed < BALL_REST_SPEED)
      & (self.time_since_kick > 0.5)
    )
    miss = (ball_xy - self.rest_target_w).norm(dim=-1)
    # v54b: exp(−miss / 2 m). v54 used exp(−(miss / tolerance)²) with a
    # 0.5 m tolerance: ~0 for the 5–6 m overshoots, so no gradient.
    self.rest_score[:] = torch.exp(-miss / REST_MISS_SCALE)
    self.rest_event[:] = rested
    self.rest_pending &= ~rested
    log["Metrics/rest_miss_short_medium"] = (miss * rested).sum() / rested.sum().clamp(
      min=1
    )

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
  rsi_files: tuple[tuple[str, float], ...] = ()
  cap_low_prob: float = 0.0
  """L3: share of episodes at runswift's low caps (0.5 / 0.3 / 0.6)."""
  """K4b: (npz path, probability) of starting an episode mid-kick from that set."""
  heading_far: float = HEADING_FAR
  ball_roll_decel: float = BALL_ROLL_DECEL
  aim_broad_share: float = 0.0
  """Share of the broad cosine in ``kick_direction`` (0.5 in v5–v14)."""
  """Rolling deceleration of the ball (m/s²); match it to the real ball."""
  max_target_distance: float = MAX_TARGET_DISTANCE
  speed_smooth_tau: float = SPEED_SMOOTH_TAU
  ball_memory: bool = True
  memory_odometry: bool = False
  vision_dropout: float = 0.02
  """v48c: 2 % of in-view steps miss the ball (5 % in v48/v48b)."""
  vision_delay_steps: tuple[int, int] = (0, 2)
  """v48: actor ball detection 0–40 ms old, per episode."""
  ball_distance_range: tuple[float, float] = (1.0, 4.0)
  """v40 tried 1–8 m: no faster (the policy cruises at ~1.3 m/s with room to
  run) and fewer kicks / goals; back to 1–4 m."""
  long_band_start: tuple[float, float] = LONG_BAND_START
  long_band_final: tuple[float, float] = LONG_KICK_SPEED_BAND
  long_foot_band_final: tuple[float, float] = LONG_FOOT_BAND_FINAL
  speed_cap_final: tuple[tuple[float, float], ...] | None = SPEED_CAP_FINAL
  speed_cap_start_max: tuple[float, float, float] = SPEED_CAP_START_MAX
  speed_cap_ramp_steps: int = SPEED_CAP_RAMP_STEPS
  ball_obs_noise: tuple[float, float] = (0.03, 0.05)
  feet_ball_sensor: str = "feet_ball_contact"
  body_ball_sensor: str = "body_ball_contact"

  def build(self, env: ManagerBasedRlEnv) -> KickLoopCommand:
    return KickLoopCommand(self, env)


def _kick_command(env: ManagerBasedRlEnv) -> KickLoopCommand:
  cmd = _command(env)
  assert isinstance(cmd, KickLoopCommand)
  return cmd


class HeadTrackedJointPositionAction(JointPositionAction):
  """Joint position action whose head targets come from a scripted tracker.

  The policy still outputs all 22 actions; its head outputs are ignored. The
  head follows the actor's ball estimate (seen or remembered), or, in
  ``scan_share`` of episodes, sweeps side to side.
  """

  cfg: HeadTrackedJointPositionActionCfg

  def __init__(self, cfg: HeadTrackedJointPositionActionCfg, env: ManagerBasedRlEnv):
    super().__init__(cfg=cfg, env=env)
    ids = [self._target_names.index(n) for n in ("Head_Yaw", "Head_Pitch")]
    self._head_cols = torch.tensor(ids, device=self.device)
    n = self.num_envs
    self.head_target = torch.tensor(HEAD_DEFAULT, device=self.device).repeat(n, 1)
    self.scan = torch.zeros(n, dtype=torch.bool, device=self.device)
    self._scan_phase = torch.zeros(n, device=self.device)
    self._scan_pitch = torch.zeros(n, device=self.device)
    self._t = torch.zeros(n, device=self.device)

  def reset(self, env_ids: torch.Tensor | slice | None = None) -> None:
    super().reset(env_ids)
    if env_ids is None:
      env_ids = slice(None)
    k = self.scan[env_ids].shape[0]
    self.head_target[env_ids] = torch.tensor(HEAD_DEFAULT, device=self.device)
    self.scan[env_ids] = torch.rand(k, device=self.device) < self.cfg.scan_share
    self._scan_phase[env_ids] = torch.rand(k, device=self.device) * 6.2832
    self._scan_pitch[env_ids] = torch.empty(k, device=self.device).uniform_(0.1, 0.6)
    self._t[env_ids] = 0.0

  def process_actions(self, actions: torch.Tensor) -> None:
    super().process_actions(actions)
    cmd = _command(self._env)
    self._t += self._env.step_dt
    # v56: a lost ball (memory judged stale) gets the far sweep, not the
    # look-down that a (0, 0) estimate would trigger.
    ball_b = torch.where(
      cmd.ball_lost.unsqueeze(-1),
      torch.full_like(cmd.masked_ball_b, 10.0),
      cmd.masked_ball_b,
    )
    lost_s = torch.where(
      cmd.ball_lost,
      cmd.time_since_seen.clamp(min=HEAD_SEARCH_AFTER + 0.01),
      cmd.time_since_seen,
    )
    goal = head_goal(ball_b, lost_s, cmd.cfg.camera_pitch)
    scan_yaw = HEAD_SCAN_YAW * torch.sin(
      6.2832 * self._t / HEAD_SCAN_PERIOD + self._scan_phase
    )
    scan_goal = torch.stack((scan_yaw, self._scan_pitch), dim=-1)
    goal = torch.where(self.scan.unsqueeze(-1), scan_goal, goal)
    self.head_target[:] = head_step(self.head_target, goal)
    processed = self._processed_actions.clone()
    processed[:, self._head_cols] = self.head_target
    self._processed_actions = processed


@dataclass(kw_only=True)
class HeadTrackedJointPositionActionCfg(JointPositionActionCfg):
  scan_share: float = HEAD_SCAN_SHARE

  def build(self, env: ManagerBasedRlEnv) -> HeadTrackedJointPositionAction:
    return HeadTrackedJointPositionAction(self, env)


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
  """Signed speed toward the ball, clipped to the vx cap, over min(cap, 1 m/s),
  outside 1.5 m: walking at a cap ≤ 1 m/s pays 1; above, 2 m/s pays twice 1 m/s.

  Signed so stepping back costs what stepping in paid; a clamp at 0 let the
  policy farm it by shuffling back and forth.
  """
  cmd = _kick_command(env)
  _, dist, _, _, _, _, _, ball_b = _current(env)
  robot: Entity = env.scene["robot"]
  heading = ball_b / ball_b.norm(dim=-1, keepdim=True).clamp(min=1.0e-6)
  toward = (robot.data.root_link_lin_vel_b[:, :2] * heading).sum(dim=-1)
  cap = cmd.speed_limit[:, 0]
  # v37: over min(cap, ref). With speed / ref alone (v35/v36) a 0.4 m/s cap
  # paid at most 0.4 and the robot idled at far balls in low-cap episodes
  # (13 % of waiting time, cap median 0.41); with speed / cap (v34) high caps
  # paid no more for going faster.
  score = torch.maximum(torch.minimum(toward, cap), -cap) / cap.clamp(
    max=WALK_SPEED_REF
  )
  # Recover first, then chase: half of the falls in stage3_v6/v7 came 1–2 s
  # after a kick, at speed, rushing after the ball.
  active = (dist > cmd.cfg.near_distance) & (cmd.time_since_kick >= POST_KICK_WINDOW)
  # v56: no pay for walking at a ball the robot has lost (search instead).
  active &= ~cmd.ball_lost
  return torch.where(active, score, torch.zeros_like(score))


# v39: when the ball is far, move at the cap. v38 chased at 0.90 m/s mean with
# a 1.6–2.0 m/s cap and exceeded 0.3–0.6 m/s caps 31 % of the time.
TRACK_CAP_MIN_DIST = 2.5
# v55: braking profile for walk_speed_track — target = min(cap, gain ×
# (dist − stop)), floor 0.3 m/s, active beyond TRACK_BRAKE_MIN_DIST. With the
# cap only tracked beyond 2.5 m (balls spawn 1–4 m away) v53 averaged 0.74 m/s
# at 1.6–2.0 m/s caps. Gain 1.2 /s reaches 2 m/s at 2.3 m from the ball.
TRACK_BRAKE_PROFILE = False
TRACK_BRAKE_GAIN = 1.2
TRACK_BRAKE_STOP = 0.6
TRACK_BRAKE_MIN_DIST = 1.0


def walk_speed_track(
  env: ManagerBasedRlEnv, min_dist: float | None = None
) -> torch.Tensor:
  """1 − |speed toward the ball − vx cap| / cap, clipped at 0: peaks at the
  cap, linear on both sides. Only with the ball beyond ``min_dist`` and after
  the post-kick window."""
  cmd = _kick_command(env)
  # Read at call time so the gene k.TRACK_CAP_MIN_DIST applies (2026-10-08).
  min_dist = TRACK_CAP_MIN_DIST if min_dist is None else min_dist
  _, dist, _, _, _, _, _, ball_b = _current(env)
  robot: Entity = env.scene["robot"]
  heading = ball_b / ball_b.norm(dim=-1, keepdim=True).clamp(min=1.0e-6)
  toward = (robot.data.root_link_lin_vel_b[:, :2] * heading).sum(dim=-1)
  cap = cmd.speed_limit[:, 0]
  if TRACK_BRAKE_PROFILE:
    brake = (TRACK_BRAKE_GAIN * (dist - TRACK_BRAKE_STOP)).clamp(min=0.3)
    cap = torch.minimum(cap, brake)
    min_dist = TRACK_BRAKE_MIN_DIST
  score = (1.0 - (toward - cap).abs() / cap).clamp(min=0.0)
  active = (dist > min_dist) & (cmd.time_since_kick >= POST_KICK_WINDOW)
  active &= ~cmd.ball_lost
  return torch.where(active, score, torch.zeros_like(score))


def walk_speed_limit(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Excess of the ~0.3 s smoothed |vx|, |vy|, |wz| over the limits.

  Smoothing ignores step-to-step gait sway; the kick itself is exempt.
  """
  cmd = _kick_command(env)
  limit = cmd.speed_limit.clone()
  # Backward: the vx cap, at most BACKWARD_SPEED_MAX (v34).
  backward = cmd.smoothed_vel[:, 0] < 0.0
  limit[:, 0] = torch.where(
    backward, limit[:, 0].clamp(max=BACKWARD_SPEED_MAX), limit[:, 0]
  )
  excess = (cmd.smoothed_vel.abs() - limit).clamp(min=0.0).sum(dim=-1)
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
  # v45: weak taps do not earn the full aim reward. Paid per kick regardless
  # of power, it let the policy farm several weak taps instead of one strong
  # kick (v43/7800, v44: more kicks, weaker long kicks, swing curriculum stalled).
  power = (
    cmd.kick_speed / (KICK_DIR_SPEED_FRACTION * cmd.kick_speed_req.clamp(min=0.5))
  ).clamp(0.0, 1.0)
  return cmd.kick_event.float() * score * cmd.kick_quality * _promptness(cmd) * power


def _promptness(cmd: KickLoopCommand) -> torch.Tensor:
  """1 for a kick right on arrival, 0.5 for a long dither near the ball."""
  return PROMPT_FLOOR + (1.0 - PROMPT_FLOOR) * torch.exp(
    -cmd.kick_near_time / PROMPT_KICK_TAU
  )


# K3 (v58): long-kick power pays only aimed kicks, exp(−err² / 0.05) (B-Human's
# final kick-direction sigma): 1 on target, 0.78 at 6°, 0.30 at 14°, 0.09 at
# 20°. cos² (0.88 at 20°) let v57 trade aim for power (68 % within 20°).
LONG_AIM_SHARP = True
LONG_AIM_SIGMA2 = 0.05


def _long_aim(cmd: KickLoopCommand) -> torch.Tensor:
  if not LONG_AIM_SHARP:
    return _aim(cmd)
  err = torch.acos(cmd.kick_cos.clamp(-1.0, 1.0))
  return torch.exp(-torch.square(err) / LONG_AIM_SIGMA2)


def _aim(cmd: KickLoopCommand) -> torch.Tensor:
  """Squared cosine to the target, floored at 0: 1 on target, 0.15 at 67°."""
  return torch.square(cmd.kick_cos.clamp(min=0.0))


def kick_vel(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per kick: ball speed over KICK_VEL_REF, capped at 1, times the aim.

  Without the aim, speed in any direction paid; in stage3_v3 that rewarded
  wild, noisy kicks (direction error grew to ~67°) and the action noise grew.
  """
  cmd = _kick_command(env)
  ref = torch.where(cmd.kick_long, LONG_KICK_VEL_REF, KICK_VEL_REF)
  if KICK_VEL_CAP_AT_NEEDED:
    # v54: short / medium pay full at the speed the target needs, so a 4 m/s
    # blast to a 2 m target earns no more than a 2.2 m/s pass.
    need = cmd.kick_speed_req.clamp(min=0.5)
    ref = torch.where(cmd.kick_long, ref, torch.minimum(ref, need))
  speed = (cmd.kick_speed / ref).clamp(max=1.0) * cmd.kick_loft
  return (
    cmd.kick_event.float() * speed * _aim(cmd) * cmd.kick_quality * _promptness(cmd)
  )


def kick_vel_accurate(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per kick: speed match, times the aim and quality.

  Short / medium: Gaussian match to the speed that rolls the ball to the
  target. Long: ball speed over that rolling speed, capped at 1 (faster is
  never penalised).
  """
  cmd = _kick_command(env)
  req = cmd.kick_speed_req.clamp(min=0.5)
  if LINEAR_SPEED_MATCH:
    # v54b: 1 − |speed / needed − 1|: a slope back from 1.8× (0.2), where the
    # Gaussian (σ = 0.25 × needed) was ~0 and gave no gradient.
    match = (1.0 - (cmd.kick_speed / req - 1.0).abs()).clamp(min=0.0)
  else:
    match = torch.exp(-torch.square((cmd.kick_speed - req) / (0.25 * req)))
  long_match = (cmd.kick_speed / req).clamp(max=1.0) * cmd.kick_loft
  match = torch.where(cmd.kick_long, long_match, match)
  return cmd.kick_event.float() * match * _aim(cmd) * cmd.kick_quality


def side_foot_strike(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per kick: (foot-yaw distance from the kick line, peak 1 at π/2) × aim × quality —
  pays striking with the inside of the foot (B-Human's style). Off (weight 0)
  except as an explicit experiment; adopted only if the benchmark says so."""
  cmd = _kick_command(env)
  # Linear ramp to the peak at pi/2 (and back down past it): pays from the
  # current front-kick angle (~7 deg) upward. The first version was a Gaussian
  # at pi/2 with sigma 0.3, ~e^-23 at 7 deg: no gradient (lesson 1).
  y = cmd.kick_foot_yaw
  side = torch.minimum(y, math.pi - y).clamp(min=0.0) / (0.5 * math.pi)
  return cmd.kick_event.float() * side * _aim(cmd) * cmd.kick_quality


def inside_foot_style(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per kick: inside-foot match to the current target (signed toe-out yaw,
  B-Human's 90 deg at the end of the curriculum) x aim x quality. STYLE_MAP
  "range": short / medium kicks only; "free": every kick."""
  cmd = _kick_command(env)
  k = cmd.kick_event
  if STYLE_MAP == "range":
    k = k & ~cmd.kick_long
  elif STYLE_MAP == "off":
    k = k & False
  return k.float() * cmd.kick_inside * _aim(cmd) * cmd.kick_quality


def hop_kick_style(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per kick struck with both feet off the ground: power (speed over the
  needed speed, capped at 1) x aim x quality. A weak hop earns nothing.
  STYLE_MAP "range": long kicks only; "free": every kick."""
  cmd = _kick_command(env)
  k = cmd.kick_event & cmd.kick_hop
  if STYLE_MAP == "range":
    k = k & cmd.kick_long
  elif STYLE_MAP == "off":
    k = k & False
  power = (cmd.kick_speed / cmd.kick_speed_req.clamp(min=0.5)).clamp(max=1.0)
  return k.float() * power * _aim(cmd) * cmd.kick_quality


def hop_kick_fall(env: ManagerBasedRlEnv) -> torch.Tensor:
  """A fall within POST_KICK_WINDOW of a hop kick (on top of kick_fall): a
  hop only pays if the robot lands it."""
  cmd = _kick_command(env)
  fell = env.termination_manager.terminated
  return (fell & cmd.last_kick_hop & (cmd.time_since_kick < POST_KICK_WINDOW)).float()


TURN_TRACK_DIST = 2.0
TURN_TRACK_ERR = 0.5


def turn_rate_track(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Near the ball (< TURN_TRACK_DIST) and misaligned with the kick line: turn
  at the yaw-rate cap toward it (2026-10-07, user: fast turns within the
  joint range, for time to kick). sign(err) * wz / wz_cap in [0, 1] times
  min(|err| / TURN_TRACK_ERR, 1); 0 once aligned, while the ball is unknown
  or lost, and in the second after a kick."""
  cmd = _kick_command(env)
  robot: Entity = env.scene["robot"]
  wz = robot.data.root_link_ang_vel_b[:, 2]
  cap = cmd.speed_limit[:, 2].clamp(min=0.1)
  err = cmd.yaw_error
  toward = (torch.sign(err) * wz / cap).clamp(0.0, 1.0)
  need = (err.abs() / TURN_TRACK_ERR).clamp(max=1.0)
  gate = (cmd.dist < TURN_TRACK_DIST) & ~cmd.ball_lost & (cmd.time_since_kick >= 1.0)
  if hasattr(cmd, "never_seen"):
    gate = gate & ~cmd.never_seen
  return gate.float() * toward * need


LONG_LINEAR_REF = 8.0
LONG_LINEAR_CLIP = 2.0


def long_kick_speed_linear(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per long (>= 8 m) kick: 3D ball speed / LONG_LINEAR_REF, uncapped up to
  LONG_LINEAR_CLIP (16 m/s), x sharp aim x quality (2026-10-07, user: long
  kicks without restriction, as strong as or stronger than B-Human; air balls
  are fine - no loft factor). B-Human's ball_kick_velocity_strong is linear too."""
  cmd = _kick_command(env)
  lk = cmd.kick_event & cmd.kick_long
  speed = (cmd.kick_speed / LONG_LINEAR_REF).clamp(max=LONG_LINEAR_CLIP)
  return lk.float() * speed * _long_aim(cmd) * cmd.kick_quality


STYLE_STATS_RATE = 0.01
STYLE_STATS_MIN = 20.0


def style_advantage(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per kick: how much better (or worse) this kick's style does than the
  average style in this situation, from running statistics of the policy's own
  kicks (aim x speed for the range), clipped to +-0.5. Pulls style choice to
  whatever works best where, without hand-coding which style is best."""
  cmd = _kick_command(env)
  return cmd.kick_event.float() * cmd.kick_style_adv.clamp(-0.5, 0.5)


def kick_rest_accuracy(env: ManagerBasedRlEnv) -> torch.Tensor:
  """When a short / medium kick's ball comes to rest: exp(−miss / 2 m) × that
  kick's quality, the miss measured to the target at the kick (v54, v54b)."""
  cmd = _kick_command(env)
  return cmd.rest_event.float() * cmd.rest_score * cmd.last_kick_quality


LONG_UNDERPOWER_FRACTION = 0.8


def long_kick_underpower(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per long kick: shortfall below 0.8 × the speed the target needs, as a
  fraction (0 at ≥ 0.8×, 1 at standstill). v54c: v54b's soft short passes
  bled into long kicks (median 0.74× needed, 47 % under 0.7×)."""
  cmd = _kick_command(env)
  need = LONG_UNDERPOWER_FRACTION * cmd.kick_speed_req.clamp(min=0.5)
  short = (1.0 - cmd.kick_speed / need).clamp(0.0, 1.0)
  return (cmd.kick_event & cmd.kick_long).float() * short


def _long_band(cmd) -> tuple[float, float]:
  return cmd.long_band_lo, cmd.long_band_lo + cmd.long_band_width


SIDE_KICK_ANGLE = (0.52, 1.05)
"""Ball launch angle off the body heading (rad) where the side-kick bonus
ramps from 0 (30°) to 1 (60°)."""


def side_kick_bonus(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per short / medium kick: ramp(launch angle off the body heading) × aim ×
  quality. A side kick only pays if it is aimed and struck well (v52b: the
  relaxed alignment alone left side kicks at ~3 % of kicks, mostly misses)."""
  cmd = _kick_command(env)
  ball: Entity = env.scene["ball"]
  robot: Entity = env.scene["robot"]
  v = ball.data.root_link_vel_w[:, :2]
  fwd = quat_apply_inverse(
    robot.data.root_link_quat_w, torch.cat((v, torch.zeros_like(v[:, :1])), dim=-1)
  )
  off = torch.atan2(fwd[:, 1].abs(), fwd[:, 0])
  lo, hi = SIDE_KICK_ANGLE
  ramp = ((off - lo) / (hi - lo)).clamp(0.0, 1.0)
  short = (cmd.kick_event & ~cmd.kick_long).float()
  return short * ramp * _aim(cmd) * cmd.kick_quality


def long_kick_power(
  env: ManagerBasedRlEnv, floor: float = LONG_SWING_FLOOR
) -> torch.Tensor:
  """Per long kick: kicking-foot speed (relative to the body) ramped from
  ``floor`` to the current target (0 → 1, 1 above), times aim² and quality.
  Short / medium kicks: 0."""
  cmd = _kick_command(env)
  target = cmd.long_band_lo
  ramp = ((cmd.kick_foot_rel - floor) / max(target - floor, 1.0e-3)).clamp(0.0, 1.0)
  # v50: only a swing that transfers into the ball pays (ball / swing speed
  # ≥ STRIKE_EFFICIENCY for full pay). v49/9900 kept a fast swing (p50 4.05
  # m/s) but struck off-centre: ball / foot speed 0.93 vs 1.16 at 9650.
  transfer = (
    cmd.kick_speed / (STRIKE_EFFICIENCY * cmd.kick_foot_rel.clamp(min=0.5))
  ).clamp(0.0, 1.0)
  long_kick = cmd.kick_event & cmd.kick_long
  return (
    long_kick.float()
    * ramp
    * transfer
    * _long_aim(cmd)
    * cmd.kick_quality
    * cmd.kick_loft
  )


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


def knee_gap(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Lateral knee spacing in the trunk frame (m)."""
  robot: Entity = env.scene["robot"]
  ids, _ = robot.find_bodies(("Left_Shank", "Right_Shank"), preserve_order=True)
  rel = robot.data.body_link_pos_w[:, ids[0]] - robot.data.body_link_pos_w[:, ids[1]]
  rel_b = quat_apply_inverse(robot.data.root_link_quat_w, rel)
  return rel_b[:, 1]


def knee_gap_violation(
  env: ManagerBasedRlEnv,
  min_gap: float = KNEE_GAP_MIN,
  scale: float = KNEE_GAP_SCALE,
) -> torch.Tensor:
  """((min_gap - gap) / scale)² when the knees are closer than ``min_gap``."""
  short = (min_gap - knee_gap(env)).clamp(min=0.0)
  return torch.square(short / scale)


def _walking(env: ManagerBasedRlEnv) -> torch.Tensor:
  """1 while walking: style gate on and the ball over WALK_POSE_MIN_DIST away."""
  cmd = _kick_command(env)
  return cmd.style_gate * (cmd.dist > WALK_POSE_MIN_DIST).float()


def _lateral_gaps(env: ManagerBasedRlEnv) -> tuple[torch.Tensor, torch.Tensor]:
  """(knee gap, foot gap): left minus right, trunk-frame y (m)."""
  robot: Entity = env.scene["robot"]
  ids, _ = robot.find_bodies(
    ("Left_Shank", "Right_Shank", "left_foot_link", "right_foot_link"),
    preserve_order=True,
  )
  pos = robot.data.body_link_pos_w[:, ids]
  quat = robot.data.root_link_quat_w
  knee = quat_apply_inverse(quat, pos[:, 0] - pos[:, 1])[:, 1]
  foot = quat_apply_inverse(quat, pos[:, 2] - pos[:, 3])[:, 1]
  return knee, foot


def push_near_ball(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  velocity_range: dict[str, tuple[float, float]],
  max_dist: float = 1.0,
  prob: float = 0.3,
) -> None:
  """Contested-ball bump (v50): for robots within ``max_dist`` of the ball,
  with probability ``prob`` per call, add a sampled base-velocity kick (as
  ``push_by_setting_velocity``). Use with ``mode="interval"``."""
  cmd = _kick_command(env)
  if env_ids is None:
    env_ids = torch.arange(env.num_envs, device=env.device)
  near = cmd.dist[env_ids] < max_dist
  lucky = torch.rand(len(env_ids), device=env.device) < prob
  chosen = env_ids[near & lucky]
  if len(chosen) > 0:
    push_by_setting_velocity(env, chosen, velocity_range)


def ball_nudge(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  speed_range: tuple[float, float] = (0.5, 1.5),
  prob: float = 0.5,
  rest_speed: float = 0.3,
  min_time_since_kick: float = 2.0,
  require_in_view: bool = True,
) -> None:
  """Moving ball (v51): with probability ``prob``, knock a nearly resting ball
  (slower than ``rest_speed``, ``min_time_since_kick`` after a kick) to a
  random speed in ``speed_range`` and direction, like a deflection or an
  opponent's touch. Use with ``mode="interval"``."""
  cmd = _kick_command(env)
  if env_ids is None:
    env_ids = torch.arange(env.num_envs, device=env.device)
  ball: Entity = env.scene["ball"]
  vel = ball.data.root_link_vel_w[env_ids].clone()
  slow = vel[:, :2].norm(dim=-1) < rest_speed
  calm = cmd.time_since_kick[env_ids] >= min_time_since_kick
  lucky = torch.rand(len(env_ids), device=env.device) < prob
  pick = slow & calm & lucky
  if require_in_view:
    # v51b: only a ball the camera sees. v51 nudged unseen balls too; with no
    # odometry in the ball memory the robot lost them and learned to stand
    # (idle at far balls 10 % → 31 %).
    pick &= cmd.see_ball[env_ids] > 0.5
  if not bool(pick.any()):
    return
  n = int(pick.sum())
  speed = torch.empty(n, device=env.device).uniform_(*speed_range)
  heading = torch.rand(n, device=env.device) * (2.0 * torch.pi)
  vel[pick, 0] = speed * heading.cos()
  vel[pick, 1] = speed * heading.sin()
  ball.write_root_link_velocity_to_sim(vel[pick], env_ids=env_ids[pick])


def search_turn(env: ManagerBasedRlEnv) -> torch.Tensor:
  """While the ball is lost: signed turning speed toward the side it was last
  remembered, over the wz cap, in [−1, 1].

  v56c: signed. v56/v56b paid |wz| (half for the other way), and the policy
  wiggled its heading back and forth — 3.7 rad of turning in 6 s with the
  ball still behind it. Turning back now costs what turning on paid.
  """
  cmd = _kick_command(env)
  robot: Entity = env.scene["robot"]
  wz = robot.data.root_link_ang_vel_b[:, 2]
  cap = cmd.speed_limit[:, 2].clamp(min=0.1)
  env.extras["log"]["Metrics/ball_lost"] = cmd.ball_lost.float().mean()
  return cmd.ball_lost.float() * (wz * cmd.lost_dir / cap).clamp(-1.0, 1.0)


def search_backward(env: ManagerBasedRlEnv) -> torch.Tensor:
  """v56: backward speed (m/s) while the ball is lost."""
  cmd = _kick_command(env)
  robot: Entity = env.scene["robot"]
  vx = robot.data.root_link_lin_vel_b[:, 0]
  return cmd.ball_lost.float() * (-vx).clamp(min=0.0)


def ball_relocate_unseen(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  prob: float = 0.1,
  dist_range: tuple[float, float] = (1.5, 4.0),
  min_off_heading: float = 1.0,
) -> None:
  """v56: with probability ``prob``, move a resting ball the camera does not see
  to a random spot ``dist_range`` away, at least ``min_off_heading`` rad off
  the robot's heading — as if another robot took it. Use with mode="interval"."""
  cmd = _kick_command(env)
  if env_ids is None:
    env_ids = torch.arange(env.num_envs, device=env.device)
  ball: Entity = env.scene["ball"]
  robot: Entity = env.scene["robot"]
  speed = ball.data.root_link_vel_w[env_ids, :2].norm(dim=-1)
  pick = (
    (cmd.see_ball[env_ids] < 0.5)
    & (speed < 0.3)
    & (cmd.time_since_kick[env_ids] > 1.0)
    & (torch.rand(len(env_ids), device=env.device) < prob)
  )
  if not bool(pick.any()):
    return
  ids = env_ids[pick]
  k = len(ids)
  q = robot.data.root_link_quat_w[ids]
  yaw = torch.atan2(
    2 * (q[:, 0] * q[:, 3] + q[:, 1] * q[:, 2]), 1 - 2 * (q[:, 2] ** 2 + q[:, 3] ** 2)
  )
  off = torch.empty(k, device=env.device).uniform_(
    min_off_heading, 2 * math.pi - min_off_heading
  )
  r = torch.empty(k, device=env.device).uniform_(*dist_range)
  pose = ball.data.root_link_pose_w[ids].clone()
  pose[:, 0] = robot.data.root_link_pos_w[ids, 0] + r * torch.cos(yaw + off)
  pose[:, 1] = robot.data.root_link_pos_w[ids, 1] + r * torch.sin(yaw + off)
  st = torch.cat((pose, torch.zeros(k, 6, device=env.device)), dim=-1)
  ball.write_root_state_to_sim(st, env_ids=ids)


@requires_model_fields(
  "geom_size",
  "geom_rbound",
  "geom_aabb",
  "body_mass",
  "body_inertia",
  recompute=RecomputeLevel.set_const,
)
def ball_size_mass(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  radius_range: tuple[float, float] = (0.07, 0.13),
  alpha_range: tuple[float, float] = (-0.347, 0.752),
  nominal_mass: float = 0.1,
  *,
  geom_cfg: SceneEntityCfg,
  body_cfg: SceneEntityCfg,
) -> None:
  """A different ball every episode (user 2026-10-08): collision radius uniform
  in ``radius_range`` and mass ``nominal_mass * e^{2 alpha}``, independent;
  thin-shell inertia 2/3 m r^2 to match the collision geom. Spawns read the
  radius back (``ball_radius``); the visual mesh keeps the nominal size."""
  if env_ids is None:
    env_ids = torch.arange(env.num_envs, device=env.device)
  env_ids = env_ids.to(env.device, dtype=torch.long)
  ball: Entity = env.scene["ball"]
  n = len(env_ids)
  r = torch.empty(n, device=env.device).uniform_(*radius_range)
  alpha = torch.empty(n, device=env.device).uniform_(*alpha_range)
  m = nominal_mass * torch.exp(2.0 * alpha)
  g = _get_entity_indices(ball.indexing, geom_cfg, "geom", False)
  b = _get_entity_indices(ball.indexing, body_cfg, "body", False)
  model = env.sim.model
  model.geom_size[env_ids[:, None], g[None, :], 0] = r[:, None]
  model.geom_rbound[env_ids[:, None], g[None, :]] = r[:, None]
  model.geom_aabb[env_ids[:, None], g[None, :], 1] = r[:, None, None].expand(
    -1, len(g), 3
  )
  model.body_mass[env_ids[:, None], b[None, :]] = m[:, None]
  inertia = (2.0 / 3.0) * m * r * r
  model.body_inertia[env_ids[:, None], b[None, :]] = inertia[:, None, None].expand(
    -1, len(b), 3
  )


def stand_start(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  prob: float = 0.25,
) -> None:
  """Cold starts (2026-10-09): with probability ``prob`` the robot starts
  still, upright in its default pose (position and heading from the motion
  reset kept). Every reset came from moving motion clips, and the runner
  sim showed falls within 0.8 s of a standing start with the ball behind
  (runswift goal grid, "away" starts). Must run after the motion reset."""
  if env_ids is None:
    env_ids = torch.arange(env.num_envs, device=env.device)
  pick = torch.rand(len(env_ids), device=env.device) < prob
  if not bool(pick.any()):
    return
  ids = env_ids[pick]
  robot: Entity = env.scene["robot"]
  q = robot.data.root_link_quat_w[ids]
  yaw = torch.atan2(
    2 * (q[:, 0] * q[:, 3] + q[:, 1] * q[:, 2]), 1 - 2 * (q[:, 2] ** 2 + q[:, 3] ** 2)
  )
  half = 0.5 * yaw
  zero = torch.zeros_like(half)
  state = robot.data.default_root_state[ids].clone()
  state[:, :2] = robot.data.root_link_pos_w[ids, :2]
  state[:, 2] = state[:, 2] + env.scene.env_origins[ids, 2]
  state[:, 3:7] = torch.stack((half.cos(), zero, zero, half.sin()), dim=-1)
  state[:, 7:] = 0.0
  robot.write_root_state_to_sim(state, env_ids=ids)
  robot.write_joint_state_to_sim(
    robot.data.default_joint_pos[ids].clone(),
    torch.zeros_like(robot.data.default_joint_vel[ids]),
    env_ids=ids,
  )


# K3 (v58): B-Human's sim2real torque clip for the K1 legs (Nm). Our sim allows
# 68 / 76 / 38 / 112 / 38 / 38; v57's long kicks reach knee p90 88 Nm.
TORQUE_SOFT_LIMIT = {
  "Hip_Pitch": 50.0,
  "Hip_Roll": 50.0,
  "Hip_Yaw": 30.0,
  "Knee_Pitch": 60.0,
  "Ankle_Pitch": 30.0,
  "Ankle_Roll": 30.0,
}
_torque_cache: dict[int, tuple[torch.Tensor, torch.Tensor]] = {}


def torque_over_soft_limit(env: ManagerBasedRlEnv) -> torch.Tensor:
  """K3: sum over leg actuators of ((|torque| − soft limit) / soft limit)², so
  kicks rely only on torque the real K1 can deliver (B-Human's clip values)."""
  key = id(env)
  if key not in _torque_cache:
    model = env.sim.mj_model
    ids, lims = [], []
    for i in range(model.nu):
      name = model.actuator(i).name
      for joint, lim in TORQUE_SOFT_LIMIT.items():
        if joint in name:
          ids.append(i)
          lims.append(lim)
    _torque_cache[key] = (
      torch.tensor(ids, device=env.device),
      torch.tensor(lims, device=env.device),
    )
  ids, lims = _torque_cache[key]
  tau = env.sim.data.actuator_force[:, ids].abs()
  over = ((tau - lims) / lims).clamp(min=0.0)
  env.extras["log"]["Metrics/torque_over_soft_limit"] = (over > 0).float().mean()
  return torch.square(over).sum(dim=-1)


def walk_base_height(
  env: ManagerBasedRlEnv,
  target: float = WALK_BASE_HEIGHT,
  deadband: float = WALK_HEIGHT_DEADBAND,
  scale: float = WALK_HEIGHT_SCALE,
) -> torch.Tensor:
  """((|h − target| − deadband) / scale)² while walking (not around kicks).

  h is the trunk height above the robot's own lowest foot (+ the foot link's
  height on flat ground), so it is right on any terrain. v48 used the world
  height: on generated terrain some robots stood on raised ground, the term
  returned huge penalties and training collapsed.
  """
  robot: Entity = env.scene["robot"]
  ids, _ = robot.find_bodies(("left_foot_link", "right_foot_link"), preserve_order=True)
  lowest_foot = robot.data.body_link_pos_w[:, ids, 2].min(dim=-1).values
  height = robot.data.root_link_pos_w[:, 2] - lowest_foot + FOOT_LINK_HEIGHT
  err = (height - target).abs()
  # Capped at 10 cm outside the band (25): beyond that the robot is falling,
  # which the fall terms price; an uncapped square let rare states dominate.
  cost = torch.square((err - deadband).clamp(min=0.0) / scale).clamp(max=25.0)
  return _walking(env) * cost


def trunk_pitch_band(
  env: ManagerBasedRlEnv,
  band_deg: tuple[float, float] = TRUNK_PITCH_BAND_DEG,
  scale_deg: float = TRUNK_PITCH_SCALE_DEG,
) -> torch.Tensor:
  """((pitch outside band) / scale)² while walking; pitch + = nose down.

  The gold AMP walk leans slightly back (−4° at 0.4 m/s, −2° at 0.7 m/s);
  v31 leaned forward more with speed (+4° mean, +8° p90 at 1–1.5 m/s).
  """
  robot: Entity = env.scene["robot"]
  g = robot.data.projected_gravity_b
  pitch = torch.rad2deg(torch.atan2(g[:, 0], -g[:, 2]))
  upper = torch.full_like(pitch, band_deg[1])
  if TRUNK_PITCH_FAST_UPPER_DEG is not None:
    # v48 diagnostic: allow more forward lean when walking fast.
    fast = _kick_command(env).smoothed_vel[:, 0] > TRUNK_PITCH_FAST_SPEED
    upper = torch.where(fast, TRUNK_PITCH_FAST_UPPER_DEG, upper)
  out = (band_deg[0] - pitch).clamp(min=0.0) + (pitch - upper).clamp(min=0.0)
  return _walking(env) * torch.square(out / scale_deg)


def walk_stance_width(
  env: ManagerBasedRlEnv, band: tuple[float, float] = WALK_STANCE_WIDTH
) -> torch.Tensor:
  """Squared foot-spacing excess outside ``band`` while walking."""
  _, foot = _lateral_gaps(env)
  out = (band[0] - foot).clamp(min=0.0) + (foot - band[1]).clamp(min=0.0)
  return _walking(env) * torch.square(out)


def knee_valgus(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Squared amount the knees sit inside the feet (knock-knee), while walking.

  The gold walk keeps the knees ~4 cm outside the feet; v28 had them ~7 cm
  inside while the knee gap alone looked normal.
  """
  knee, foot = _lateral_gaps(env)
  return _walking(env) * torch.square((foot - knee).clamp(min=0.0))


# v38: arms held out sideways. From v35 the shoulder roll drifted to a constant
# +0.28 rad from default (v31 0.19) and elbow yaw to ±0.21 (v31 ±0.04); the
# 8-joint arm_pose term priced this at ~0.7/s. Arm swing (shoulder pitch) is
# left free.
ARM_ABDUCTION_JOINTS = (r".*_Shoulder_Roll", r".*_Elbow_Yaw")
ARM_ABDUCTION_DEADBAND = 0.1
ARM_ABDUCTION_SCALE = 0.1


def arm_abduction(
  env: ManagerBasedRlEnv,
  deadband: float = ARM_ABDUCTION_DEADBAND,
  scale: float = ARM_ABDUCTION_SCALE,
) -> torch.Tensor:
  """Σ ((|shoulder roll / elbow yaw − default| − deadband) / scale)², off
  around kicks (style gate)."""
  robot: Entity = env.scene["robot"]
  ids, _ = robot.find_joints(ARM_ABDUCTION_JOINTS)
  dev = (robot.data.joint_pos[:, ids] - robot.data.default_joint_pos[:, ids]).abs()
  cost = torch.square((dev - deadband).clamp(min=0.0) / scale).sum(dim=-1)
  return _kick_command(env).style_gate * cost


def arm_pose_deviation(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Squared deviation of shoulders and elbows from the default pose."""
  robot: Entity = env.scene["robot"]
  ids, _ = robot.find_joints((r".*_Shoulder_.*", r".*_Elbow_.*"))
  dev = robot.data.joint_pos[:, ids] - robot.data.default_joint_pos[:, ids]
  return torch.square(dev).sum(dim=-1)


def _apply_kick_genes() -> None:
  """Evolutionary search: override runtime module constants from KICK_GENES
  ("k.<NAME>": value). Only constants read at call time are allowed."""
  import json
  import os

  genes = json.loads(os.environ.get("KICK_GENES", "{}") or "{}")
  g = globals()
  for key, value in genes.items():
    if key.startswith("k."):
      name = key[2:]
      if name not in g:
        raise KeyError(f"KICK_GENES: unknown kick_loop constant {name}")
      g[name] = type(g[name])(value)


_apply_kick_genes()

__all__ = [
  "BALL_ROLL_DECEL",
  "HEAD_SCAN_SHARE",
  "KICK_AIM_SIGMA",
  "KICK_VEL_REF",
  "LONG_KICK_SPEED_BAND",
  "NEAR_DISTANCE",
  "RANGE_EDGES",
  "TARGET_BINS",
  "HeadTrackedJointPositionAction",
  "HeadTrackedJointPositionActionCfg",
  "KickLoopCommand",
  "KickLoopCommandCfg",
  "arm_abduction",
  "arm_pose_deviation",
  "ball_avoidance",
  "head_goal",
  "head_search_angles",
  "head_step",
  "head_track_angles",
  "knee_gap",
  "knee_gap_violation",
  "knee_valgus",
  "ball_nudge",
  "push_near_ball",
  "long_kick_power",
  "side_kick_bonus",
  "kick_rest_accuracy",
  "search_turn",
  "side_foot_strike",
  "inside_foot_style",
  "turn_rate_track",
  "long_kick_speed_linear",
  "style_advantage",
  "hop_kick_style",
  "hop_kick_fall",
  "torque_over_soft_limit",
  "search_backward",
  "ball_relocate_unseen",
  "ball_size_mass",
  "stand_start",
  "long_kick_underpower",
  "trunk_pitch_band",
  "walk_base_height",
  "walk_stance_width",
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
  "walk_speed_track",
]

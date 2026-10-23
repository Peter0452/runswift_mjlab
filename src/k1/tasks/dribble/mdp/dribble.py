"""Dribble stage: move the ball at a commanded velocity (after DribbleMaster).

Built on ``ApproachYawCommand`` and registered under the same command name
("twist"), so the approach stage's 83-dim actor layout, vision model, speed
limits and ball spawn carry over unchanged:

- 72–74: ball xy in the trunk frame (zero when unseen), slot 74 unused.
- 75–77: this episode's |vx|, |vy|, |wz| limits.
- 78–79: commanded ball direction (cos, sin) in the yaw frame; zero for stop.
- 80–82: stop flag (1 iff the commanded speed is 0), commanded ball speed (m/s), 0.

The kick target becomes a virtual target ``VIRTUAL_TARGET_DIST`` ahead of the
ball along the commanded direction, refreshed every step, so the approach
geometry (alpha, wedge, yaw error) reads "behind the ball, facing the
dribble direction".

A command window lasts ``resampling_time_range``. It succeeds when, over its
last ``success_tail_s``, the mean error between the ball's planar velocity and
the command is below min(``success_vel_err``, ``success_vel_rel`` * speed)
(``success_stop_err`` for a stop command) and the ball ends within
``success_ball_dist`` of the trunk.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

import torch

from k1.tasks.kick.mdp.approach import (
  WALK_COMMAND_SPEED,
  ApproachYawCommand,
  ApproachYawCommandCfg,
  _root_pose,
  _yaw_angle,
  ball_radius,
)
from k1.tasks.kick.mdp.kick_loop import classify_touch, loft_factor
from mjlab.motion.motion_loader import COND_SPEED_SCALE

if TYPE_CHECKING:
  import viser

  from mjlab.envs import ManagerBasedRlEnv

VIRTUAL_TARGET_DIST = 4.0
TOUCH_EMA_STEPS = 240.0
"""Time constant (env steps, = 10 PPO iterations) of the per-foot touch counts
behind ``Metrics/dribble_touch_left_share``."""
GAIT_MOVING_SPEED = 0.2
"""Reward-tune iter 9: robot planar speed (m/s) above which the gait metrics count."""
TIME_TO_SPEED_FRAC = 0.8
"""Iter 9: a moving window has reached speed once v . c_hat >= this share of s."""
TIME_TO_SPEED_CAP = 4.0
"""Iter 9: time_to_speed logged for windows that never reach speed (s)."""
GAIT_MIN_AIR_S = 0.08
"""Reward-tune iter 10: a touchdown counts for the gait metrics only after an air
phase of at least this long (s); shorter lifts are contact chatter."""
ALT_TAP_MIN_INTERVAL_S = 0.12
"""Minimum time between exclusive foot-ball taps counted as a new dribble tap.
Shorter onsets are contact chatter, not a second stride."""


def classify_alternate_tap(
  lr: torch.Tensor,
  lr_prev: torch.Tensor,
  tap_side: torch.Tensor,
  time_since_tap: torch.Tensor,
  dt: float,
  min_interval_s: float = ALT_TAP_MIN_INTERVAL_S,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
  """Debounced exclusive foot-ball tap classification.

  A tap is an exclusive onset (exactly one foot newly in contact, the other
  not contacting). Returns ``(alt, same, new_tap_side, new_time_since_tap)``.
  ``tap_side`` is 0 before the first tap, +1 left, -1 right. The first tap of
  an episode is neither alt nor same.
  """
  time_since = time_since_tap + dt
  onset = lr & ~lr_prev
  left_on = onset[:, 0] & ~lr[:, 1]
  right_on = onset[:, 1] & ~lr[:, 0]
  new_tap = (left_on | right_on) & (time_since >= min_interval_s)
  had = tap_side != 0.0
  alt = new_tap & had & ((left_on & (tap_side < 0.0)) | (right_on & (tap_side > 0.0)))
  same = new_tap & had & ((left_on & (tap_side > 0.0)) | (right_on & (tap_side < 0.0)))
  ones = torch.ones_like(tap_side)
  new_side = torch.where(
    new_tap,
    torch.where(left_on, ones, -ones),
    tap_side,
  )
  new_time = torch.where(new_tap, torch.zeros_like(time_since), time_since)
  return alt, same, new_side, new_time


class DribbleCommand(ApproachYawCommand):
  """Ball spawn and speed limits per episode; ball velocity command per window."""

  cfg: DribbleCommandCfg

  def __init__(self, cfg: DribbleCommandCfg, env: ManagerBasedRlEnv):
    super().__init__(cfg, env)
    n, device = self.num_envs, self.device
    self.ball_cmd_dir_w = torch.zeros(n, 2, device=device)
    self.ball_cmd_dir_w[:, 0] = 1.0
    self.ball_cmd_speed = torch.zeros(n, device=device)
    # v15: length of the current command window (s), set on every resample.
    # Deploy match: slow turn of the commanded direction within a window
    # (rad/s), like a joystick held off-centre; 0 for a steady command.
    self.cmd_drift = torch.zeros(n, device=device)
    self.window_len = torch.full(
      (n,), float(cfg.resampling_time_range[0]), device=device
    )
    self.ball_vel_err = torch.zeros(n, device=device)
    self.ball_trunk_dist = torch.zeros(n, device=device)
    self.far_time = torch.zeros(n, device=device)
    self.window_success = torch.zeros(n, dtype=torch.bool, device=device)
    self._tail_err_sum = torch.zeros(n, device=device)
    self._tail_vel_sum = torch.zeros(n, 2, device=device)
    self._tail_steps = torch.zeros(n, device=device)
    self._windows = torch.zeros(n, device=device)
    self._successes = torch.zeros(n, device=device)
    self._in_reset = False
    # Foot-ball touch memory (reward-tune iter 3): steps since the last touch,
    # updated lazily once per env step by ``recent_touch``; and a per-window latch
    # for the one-shot redirect bonus, cleared on every resample and reset.
    self.steps_since_touch = torch.full((n,), 1.0e6, device=device)
    self._touch_step = -1
    self.redirect_latched = torch.zeros(n, dtype=torch.bool, device=device)
    self.win_touched = torch.zeros(n, dtype=torch.bool, device=device)
    self.time_since_win_touch = torch.zeros(n, device=device)
    # Reward-tune iter 7: per-foot touches this step (left, right), a per-episode
    # "has touched the ball" flag, and per-window "started after the first touch"
    # flag used by the speed-curriculum gate. Running per-foot touch counts
    # (EMA over ~TOUCH_EMA_STEPS env steps) give the left share of touches.
    self.touch_lr = torch.zeros(n, 2, dtype=torch.bool, device=device)
    self.has_touched = torch.zeros(n, dtype=torch.bool, device=device)
    self._window_post_touch = torch.zeros(n, dtype=torch.bool, device=device)
    self._touch_ema = torch.zeros(2, device=device)
    # Ball-speed curriculum (reward-tune iter 6): the commanded speed is drawn
    # from (ball_speed_range[0], speed_hi); speed_hi rises by speed_hi_step
    # whenever the window success rate in the top band [hi - band, hi] over a
    # period reaches the threshold. It never decreases.
    self.speed_hi = (
      float(self.cfg.speed_hi_start)
      if self.cfg.speed_curriculum
      else float(self.cfg.ball_speed_range[1])
    )
    self._band_windows = torch.zeros((), device=device)
    self._band_successes = torch.zeros((), device=device)
    self._band_last_step = 0
    self.top_band_success = 0.0
    # Reward-tune iter 8: low band [0.2, 0.4] post-touch window counts for the
    # relative gate (top-band success >= ratio * low-band success).
    self._low_windows = torch.zeros((), device=device)
    self._low_successes = torch.zeros((), device=device)
    self.low_band_success = 0.0
    # Reward-tune iter 9: seconds since the last command resample (t_win), and the
    # per-window "ball reached 0.8 s along the command" latch + time (time_to_speed).
    self.window_time = torch.zeros(n, device=device)
    self.speed_reached = torch.zeros(n, dtype=torch.bool, device=device)
    self.speed_reach_time = torch.zeros(n, device=device)
    # Gait state, columns (left, right): last completed swing duration (s) and the
    # forward step length (m, heading frame) at the last touchdown. Iter 10:
    # touchdowns are debounced (air phase >= GAIT_MIN_AIR_S) from the raw contact
    # flag, and only forward steps (touching-down foot ahead) update the length.
    self.gait_air_last = torch.zeros(n, 2, device=device)
    self.gait_step_last = torch.zeros(n, 2, device=device)
    self.gait_air_run = torch.zeros(n, 2, device=device)
    self.gait_contact_prev = torch.ones(n, 2, dtype=torch.bool, device=device)
    # Reward-tune iter 11: share of resampled moving commands that fall in the
    # top band [hi - band, hi] (EMA of (count, total) over resamples).
    self._top_cmd_ema = torch.zeros(2, device=device)
    self._gait_step = -1
    feet_ids, _ = self.robot.find_bodies(
      ("left_foot_link", "right_foot_link"), preserve_order=True
    )
    self._gait_feet_ids = list(feet_ids)
    sensor = env.scene["feet_ground_contact"]
    names = list(sensor.primary_names)
    self._gait_lr = [names.index("left_foot_link"), names.index("right_foot_link")]
    # EMA accumulators (sum, count) for the iter-9 logging-only metrics.
    self._ema = {
      k: torch.zeros(2, device=device)
      for k in (
        "gait_air_time_left",
        "gait_air_time_right",
        "gait_step_length_left",
        "gait_step_length_right",
        "gait_single_support_frac",
        "gait_cadence",
        "time_to_speed",
        "time_to_speed_post_touch",
        "robot_speed_along_cmd_ratio",
        "kick_window_success",
        "kick_window_kicked",
        "kick_end_still",
        "kick_speed",
        "kick_err_deg",
        "kick_wait_s",
      )
    }
    self._style_patched = False
    self.pred_ball_vel_w = torch.zeros(n, 2, device=device)
    self._prev_seen_ball_w = torch.zeros(n, 2, device=device)
    self._was_visible = torch.zeros(n, dtype=torch.bool, device=device)
    self.last_touch_side = torch.ones(n, device=device)
    # Exclusive debounced ball-tap side for alternating-leg dribble: 0 = none
    # yet this episode, +1 = left, -1 = right. Distinct from last_touch_side,
    # which follows any contact (including two-foot traps) for lost-ball spin.
    self.tap_side = torch.zeros(n, device=device)
    self.touch_lr_prev = torch.zeros(n, 2, dtype=torch.bool, device=device)
    self.time_since_tap = torch.full((n,), 1.0e6, device=device)
    self.alt_touch_event = torch.zeros(n, dtype=torch.bool, device=device)
    self.same_touch_event = torch.zeros(n, dtype=torch.bool, device=device)
    self._alt_tap_ema = torch.zeros(2, device=device)
    self.metrics["ball_vel_err"] = torch.zeros(n, device=device)
    self.metrics["dribble_success_rate"] = torch.zeros(n, device=device)
    # v22 kick mode: the window's kick flag, whether its one kick happened, and
    # that kick's ground speed, direction error and loft factor.
    self.kick_mode = torch.zeros(n, dtype=torch.bool, device=device)
    self.kick_done = torch.zeros(n, dtype=torch.bool, device=device)
    self.kick_event = torch.zeros(n, dtype=torch.bool, device=device)
    self.kick_speed = torch.zeros(n, device=device)
    self.kick_err = torch.full((n,), math.pi, device=device)
    self.kick_loft = torch.ones(n, device=device)
    self.kick_wait = torch.zeros(n, device=device)
    self.time_since_kick = torch.full((n,), 1.0e6, device=device)
    self._prev_touch_any = torch.zeros(n, dtype=torch.bool, device=device)
    self._prev_ball_speed = torch.zeros(n, device=device)
    # v27: every foot launch of the ball (push events in dribble windows) with
    # the ball speed along the command, and the kicking foot's sole yaw match
    # to B-Human's inside-kick pose at the window's kick.
    self.launch_event = torch.zeros(n, dtype=torch.bool, device=device)
    self.launch_along = torch.zeros(n, device=device)
    self.kick_sole_ratio = torch.zeros(n, device=device)
    self._kicked_once = torch.zeros(n, dtype=torch.bool, device=device)
    self.prev_window_kick_done = torch.zeros(n, dtype=torch.bool, device=device)
    self.kick_offset = torch.zeros(n, device=device)
    self._speed_ok = torch.zeros(n, dtype=torch.bool, device=device)
    # Viewer manual control (create_gui); None outside the viser viewer.
    self._gui_manual = None
    self._gui_new_ball = False
    self._gui_was_manual = False
    # The task owns the AMP style gate: style stays on everywhere (the inherited
    # gate fades it with robot-ball distance), except around a kick (v22).
    env.amp_style_gate = torch.ones(n, device=device)  # ty: ignore[unresolved-attribute]

  def reset(self, env_ids: torch.Tensor | slice | None) -> dict[str, float]:
    # Cleared before the reset resample so the first window is pre-touch.
    self.has_touched[env_ids] = False
    self.kick_mode[env_ids] = False
    self.kick_done[env_ids] = False
    self._kicked_once[env_ids] = False
    self.kick_event[env_ids] = False
    self.kick_wait[env_ids] = 0.0
    self.time_since_kick[env_ids] = 1.0e6
    self._prev_touch_any[env_ids] = False
    self._prev_ball_speed[env_ids] = 0.0
    self._in_reset = True
    try:
      extras = super().reset(env_ids)
    finally:
      self._in_reset = False
    self.far_time[env_ids] = 0.0
    self._windows[env_ids] = 0.0
    self._successes[env_ids] = 0.0
    self.window_success[env_ids] = False
    self.steps_since_touch[env_ids] = 1.0e6
    self.win_touched[env_ids] = False
    self.time_since_win_touch[env_ids] = 0.0
    self.pred_ball_vel_w[env_ids] = 0.0
    self._prev_seen_ball_w[env_ids] = self.last_seen_ball_w[env_ids]
    self._was_visible[env_ids] = ~self.never_seen[env_ids]
    self.last_touch_side[env_ids] = 1.0
    self.tap_side[env_ids] = 0.0
    self.touch_lr_prev[env_ids] = False
    self.time_since_tap[env_ids] = 1.0e6
    self.alt_touch_event[env_ids] = False
    self.same_touch_event[env_ids] = False
    self.gait_air_last[env_ids] = 0.0
    self.gait_step_last[env_ids] = 0.0
    self.gait_air_run[env_ids] = 0.0
    self.gait_contact_prev[env_ids] = True
    return extras

  def compute(self, dt: float) -> None:
    self._apply_style_weight()
    # Windows that end this step are judged before their command is resampled.
    ending = self.time_left - dt <= 0.0
    if dt > 0.0:
      self.window_time += dt
      self.time_since_win_touch[:] = torch.where(
        self.win_touched,
        self.time_since_win_touch + dt,
        torch.zeros_like(self.time_since_win_touch),
      )
      self._update_time_to_speed(ending)
      self._update_gait()
    tail_err = self._tail_err_sum / self._tail_steps.clamp(min=1.0)
    mean_tail_vel = self._tail_vel_sum / self._tail_steps.clamp(min=1.0).unsqueeze(-1)
    cmd_vel = self.ball_cmd_dir_w * self.ball_cmd_speed.unsqueeze(-1)
    vec_tail_err = torch.linalg.norm(mean_tail_vel - cmd_vel, dim=-1)
    eff_tail_err = torch.where(self.ball_cmd_speed > 0.0, vec_tail_err, tail_err)
    # Relative bound while moving, so a ball left still never passes a slow command.
    moving = self.ball_cmd_speed > 0.0
    thr = torch.where(
      moving,
      (self.cfg.success_vel_rel * self.ball_cmd_speed).clamp(
        max=self.cfg.success_vel_err
      ),
      torch.full_like(tail_err, self.cfg.success_stop_err),
    )
    lo, hi = self.cfg.push_speed_range
    push = ((self.ball_cmd_speed - lo) / (hi - lo)).clamp(0.0, 1.0)
    ball_dist_ok = self.ball_trunk_dist < (
      self.cfg.success_ball_dist + self.cfg.push_dist_extra * push
    )
    ok = (self._tail_steps > 0) & (eff_tail_err < thr) & ball_dist_ok
    if self.cfg.kick_prob > 0.0:
      # v22: a kick window succeeds with one fast, straight kick and the robot
      # standing at the end, wherever the ball went.
      still = self.robot.data.root_link_lin_vel_w[:, :2].norm(dim=-1) < 0.25
      ok_kick = (
        self.kick_done
        & (self.kick_speed >= self.cfg.kick_success_speed)
        & (self.kick_err <= self.cfg.kick_success_err)
        & still
      )
      kick_end = ending & self.kick_mode
      self._ema_add("kick_window_success", ok_kick.float(), kick_end)
      self._ema_add("kick_window_kicked", self.kick_done.float(), kick_end)
      self._ema_add("kick_end_still", still.float(), kick_end & self.kick_done)
      ok = torch.where(self.kick_mode, ok_kick, ok)
    self.window_success[:] = ending & ok
    self._update_touch()
    self._windows += ending.float()
    self._successes += self.window_success.float()
    along = (mean_tail_vel * self.ball_cmd_dir_w).sum(dim=-1)
    self._speed_ok = (self._tail_steps > 0) & (
      along >= self.cfg.speed_gate_achieved_frac * self.ball_cmd_speed
    )
    if self.cfg.speed_curriculum and dt > 0.0:
      self._update_speed_curriculum(ending)
    super().compute(dt)

  def _update_speed_curriculum(self, ending: torch.Tensor) -> None:
    hi = self.speed_hi
    # Iter 7: only windows that started after the env's first foot-ball touch
    # of the episode count (approach windows after far / behind spawns do not).
    band = (
      ending
      & (self.ball_cmd_speed >= hi - self.cfg.speed_band_width - 1.0e-6)
      & (self.ball_cmd_speed > 0.0)
    )
    if self.cfg.speed_gate_post_touch:
      band = band & self._window_post_touch
    self._band_windows += band.float().sum()
    # v27: optionally "reached speed" (tail ball speed along the command >=
    # speed_gate_achieved_frac x s) instead of full window success, which was
    # ~0 above 1.2 m/s, so speed_hi never left 1.5.
    gate_ok = (
      self._speed_ok if self.cfg.speed_gate_achieved_frac > 0.0 else self.window_success
    )
    self._band_successes += (band & gate_ok).float().sum()
    # Iter 8: low band [low_lo, low_hi] under the same post-touch rule.
    lo_lo, lo_hi = self.cfg.speed_low_band
    low = (
      ending
      & (self.ball_cmd_speed >= lo_lo - 1.0e-6)
      & (self.ball_cmd_speed <= lo_hi + 1.0e-6)
      & (self.ball_cmd_speed > 0.0)
    )
    if self.cfg.speed_gate_post_touch:
      low = low & self._window_post_touch
    self._low_windows += low.float().sum()
    self._low_successes += (low & gate_ok).float().sum()
    step = int(self._env.common_step_counter)
    if step - self._band_last_step >= self.cfg.speed_curriculum_period_steps:
      self._band_last_step = step
      n_win = float(self._band_windows.item())
      rate = float(self._band_successes.item()) / max(n_win, 1.0)
      low_rate = float(self._low_successes.item()) / max(
        float(self._low_windows.item()), 1.0
      )
      self.top_band_success = rate
      self.low_band_success = low_rate
      if self.cfg.speed_gate_relative:
        passed = (
          rate >= self.cfg.speed_gate_ratio * low_rate
          and low_rate >= self.cfg.speed_low_min_success
        ) or (rate >= self.cfg.speed_band_success)
      else:
        passed = rate >= self.cfg.speed_band_success
      if n_win >= self.cfg.speed_band_min_windows and passed:
        self.speed_hi = min(
          self.speed_hi + self.cfg.speed_hi_step, self.cfg.speed_hi_max
        )
      self._band_windows.zero_()
      self._band_successes.zero_()
      self._low_windows.zero_()
      self._low_successes.zero_()
    log = self._env.extras.setdefault("log", {})
    log["Metrics/ball_speed_hi"] = self.speed_hi
    log["Metrics/top_band_success"] = self.top_band_success
    # Iter 9: the gate's reference band is speed_low_band (0.4-0.6 m/s).
    log["Metrics/ref_band_success"] = self.low_band_success
    # Iter 11: share of moving commands drawn in the top band.
    log["Metrics/top_band_cmd_share"] = self._top_cmd_ema[0] / self._top_cmd_ema[
      1
    ].clamp(min=1.0e-6)

  def _ema_add(self, key: str, values: torch.Tensor, mask: torch.Tensor) -> None:
    decay = 1.0 - 1.0 / TOUCH_EMA_STEPS
    acc = self._ema[key]
    acc.mul_(decay)
    acc[0] += torch.where(mask, values, torch.zeros_like(values)).sum()
    acc[1] += mask.float().sum()

  def _ema_log(self) -> None:
    log = self._env.extras.setdefault("log", {})
    for key, acc in self._ema.items():
      log[f"Metrics/{key}"] = torch.where(
        acc[1] > 1.0e-6, acc[0] / acc[1].clamp(min=1.0e-6), torch.zeros_like(acc[0])
      )

  def _apply_style_weight(self) -> None:
    """Reward-tune iter 9: a constant AMP style weight owned by the task. The AMP
    wrapper installs its ``amp_style_weight`` curriculum (0.3) after the task cfg
    is built, so the task patches that term's params once and writes the weight
    the runner reads (``env.amp_style_reward_weight``) every step."""
    w = self.cfg.amp_style_weight
    if w is None:
      return
    if not self._style_patched:
      cm = getattr(self._env, "curriculum_manager", None)
      if cm is not None:
        try:
          params = cm.get_term_cfg("amp_style_weight").params
          params["start_weight"] = params["end_weight"] = float(w)
        except (KeyError, ValueError, AttributeError):
          pass
        self._style_patched = True
    setattr(self._env, "amp_style_reward_weight", float(w))

  def _update_time_to_speed(self, ending: torch.Tensor) -> None:
    """Iter 9: latch the first step of a moving window with v . c_hat >= 0.8 s;
    log seconds-to-speed (capped at 4 s) for each moving window that ends."""
    s = self.ball_cmd_speed
    v = self.ball.data.root_link_lin_vel_w[:, :2]
    u = torch.sum(v * self.ball_cmd_dir_w, dim=-1)
    newly = (s > 0.0) & ~self.speed_reached & (u >= TIME_TO_SPEED_FRAC * s)
    self.speed_reach_time[:] = torch.where(
      newly, self.window_time, self.speed_reach_time
    )
    self.speed_reached |= newly
    tts = torch.where(
      self.speed_reached,
      self.speed_reach_time.clamp(max=TIME_TO_SPEED_CAP),
      torch.full_like(self.speed_reach_time, TIME_TO_SPEED_CAP),
    )
    done = ending & (s > 0.0)
    self._ema_add("time_to_speed", tts, done)
    self._ema_add("time_to_speed_post_touch", tts, done & self._window_post_touch)
    # robot speed along the command / s, while s > 0 and the ball is within 1 m.
    robot = self.robot.data
    v_r = robot.root_link_lin_vel_w[:, :2]
    along_r = torch.sum(v_r * self.ball_cmd_dir_w, dim=-1)
    d = torch.linalg.norm(
      self.ball.data.root_link_pos_w[:, :2] - robot.root_link_pos_w[:, :2], dim=-1
    )
    self._ema_add(
      "robot_speed_along_cmd_ratio",
      along_r / s.clamp(min=1.0e-3),
      (s > 0.0) & (d < 1.0),
    )

  def _update_gait(self) -> None:
    """Once per env step (iter 10, debounced): a touchdown is a contact onset after
    an air phase >= GAIT_MIN_AIR_S. At each touchdown: that foot's swing duration,
    and -- for forward steps only (touching-down foot ahead of the other along the
    heading) -- its step length. Metrics are counted while robot planar speed >
    0.2 m/s: air time / step length per touchdown event, single-support share and
    cadence (debounced touchdowns per second) per step."""
    step = int(self._env.common_step_counter)
    if step == self._gait_step:
      return
    self._gait_step = step
    dt = self._env.step_dt
    sensor = self._env.scene["feet_ground_contact"]
    data = sensor.data
    lr = self._gait_lr
    assert data.found is not None
    found = (
      data.found.reshape(self.num_envs, len(sensor.primary_names), -1).amax(dim=-1) > 0
    )
    contact = found[:, lr]
    robot = self.robot.data
    feet = robot.body_link_pos_w[:, self._gait_feet_ids, :2]
    yaw = _yaw_angle(robot.root_link_quat_w)
    head = torch.stack((yaw.cos(), yaw.sin()), dim=-1)
    fwd_l = torch.sum((feet[:, 0] - feet[:, 1]) * head, dim=-1)
    moving = (
      torch.linalg.norm(robot.root_link_lin_vel_w[:, :2], dim=-1) > GAIT_MOVING_SPEED
    )
    self._gait_update(contact, fwd_l, moving, dt)
    self._ema_log()

  def _gait_update(
    self, contact: torch.Tensor, fwd_l: torch.Tensor, moving: torch.Tensor, dt: float
  ) -> torch.Tensor:
    """Debounced gait bookkeeping for one env step. ``contact`` [N, 2] (left,
    right) raw foot-ground contact, ``fwd_l`` [N] left foot ahead of the right
    along the heading (m), ``moving`` [N] robot planar speed > 0.2. Returns the
    debounced touchdown mask [N, 2]."""
    onset = contact & ~self.gait_contact_prev
    touchdown = onset & (self.gait_air_run >= GAIT_MIN_AIR_S - 1.0e-6)
    self.gait_air_last[:] = torch.where(
      touchdown, self.gait_air_run, self.gait_air_last
    )
    step_now = torch.stack((fwd_l, -fwd_l), dim=-1)
    fwd_step = touchdown & (step_now > 0.0)
    self.gait_step_last[:] = torch.where(fwd_step, step_now, self.gait_step_last)
    self.gait_air_run[:] = torch.where(
      contact, torch.zeros_like(self.gait_air_run), self.gait_air_run + dt
    )
    self.gait_contact_prev[:] = contact
    self._ema_add(
      "gait_air_time_left", self.gait_air_last[:, 0], moving & touchdown[:, 0]
    )
    self._ema_add(
      "gait_air_time_right", self.gait_air_last[:, 1], moving & touchdown[:, 1]
    )
    self._ema_add(
      "gait_step_length_left", self.gait_step_last[:, 0], moving & fwd_step[:, 0]
    )
    self._ema_add(
      "gait_step_length_right", self.gait_step_last[:, 1], moving & fwd_step[:, 1]
    )
    single = (contact.sum(dim=-1) == 1).float()
    self._ema_add("gait_single_support_frac", single, moving)
    self._ema_add("gait_cadence", touchdown.float().sum(dim=-1) / dt, moving)
    return touchdown

  def _update_metrics(self) -> None:
    super()._update_metrics()
    self.metrics["ball_vel_err"][:] = self.ball_vel_err
    self.metrics["dribble_success_rate"][:] = self._successes / self._windows.clamp(
      min=1.0
    )

  def _resample_command(self, env_ids: torch.Tensor) -> None:
    if self._in_reset:
      # New episode: ball spawn, vision lag and speed limits from the approach.
      super()._resample_command(env_ids)
      self._ground_ball(env_ids)
    n = len(env_ids)
    if n == 0:
      return
    device = self.device
    lo, hi = self.cfg.ball_speed_range[0], self.speed_hi
    speed = torch.empty(n, device=device).uniform_(lo, hi)
    # Reward-tune iter 11: top-band oversampling -- with probability
    # top_band_prob a moving speed is drawn from [max(lo, hi - band), hi].
    if self.cfg.top_band_prob > 0.0:
      band_lo = max(lo, hi - self.cfg.speed_band_width)
      top_speed = torch.empty(n, device=device).uniform_(band_lo, hi)
      use_top = torch.rand(n, device=device) < self.cfg.top_band_prob
      speed = torch.where(use_top, top_speed, speed)
    stop = torch.rand(n, device=device) < self.cfg.stop_prob
    moving = ~stop
    in_top = moving & (speed >= hi - self.cfg.speed_band_width - 1.0e-6)
    decay = 1.0 - 1.0 / TOUCH_EMA_STEPS
    self._top_cmd_ema.mul_(decay)
    self._top_cmd_ema[0] += in_top.float().sum()
    self._top_cmd_ema[1] += moving.float().sum()
    self.ball_cmd_speed[env_ids] = torch.where(stop, torch.zeros_like(speed), speed)
    # Direction relative to the robot-to-ball bearing; half-angle pi = any.
    # qpos and the spawn's last_seen_ball_w are valid before the next forward().
    robot_xy = _root_pose(self.robot, env_ids)[:, :2]
    ball_xy = (
      self.last_seen_ball_w[env_ids]
      if self._in_reset
      else self.ball.data.root_link_pos_w[env_ids, :2]
    )
    to_ball = ball_xy - robot_xy
    bearing = torch.atan2(to_ball[:, 1], to_ball[:, 0])
    half = self.cfg.cmd_heading_half_angle
    heading = bearing + torch.empty(n, device=device).uniform_(-half, half)
    # Collinear in-between drill (robot is between the ball and the target, so
    # cmd_dir points ~180° opposite to robot->ball bearing, training the
    # step-over + controllable backward tap + simultaneous 180° body turn).
    if self.cfg.collinear_drill_prob > 0.0:
      collinear = moving & (
        torch.rand(n, device=device) < self.cfg.collinear_drill_prob
      )
      back_heading = (
        bearing + math.pi + torch.empty(n, device=device).uniform_(-0.35, 0.35)
      )
      heading = torch.where(collinear, back_heading, heading)
      if self._in_reset and bool(collinear.any()):
        # Place the ball at close step-over range (0.26–0.44 m) in front of the
        # robot for collinear drill starts.
        c_ids = env_ids[collinear]
        b_dir = torch.stack(
          (bearing[collinear].cos(), bearing[collinear].sin()), dim=-1
        )
        close_d = torch.empty(len(c_ids), 1, device=device).uniform_(0.26, 0.44)
        close_xy = robot_xy[collinear] + close_d * b_dir
        self.last_seen_ball_w[c_ids] = close_xy
        self._ground_ball(c_ids)
    # v15: fast windows last longer and, once the ball is under control, turn
    # at most fast_turn_half_angle from the previous command, so a fast window
    # is mostly spent running with the ball rather than getting around it.
    fast = moving & (speed >= self.cfg.fast_window_min_speed)
    if self.cfg.fast_window_s is not None:
      length = torch.empty(n, device=device).uniform_(*self.cfg.fast_window_s)
      self.time_left[env_ids] = torch.where(fast, length, self.time_left[env_ids])
    if self.cfg.fast_turn_half_angle < math.pi and not self._in_reset:
      prev = self.ball_cmd_dir_w[env_ids]
      near = torch.atan2(prev[:, 1], prev[:, 0]) + torch.empty(
        n, device=device
      ).uniform_(-self.cfg.fast_turn_half_angle, self.cfg.fast_turn_half_angle)
      heading = torch.where(fast & self.has_touched[env_ids], near, heading)
    self.window_len[env_ids] = self.time_left[env_ids]
    drift = torch.empty(n, device=device).uniform_(
      -self.cfg.cmd_drift_max, self.cfg.cmd_drift_max
    )
    use_drift = moving & (torch.rand(n, device=device) < self.cfg.cmd_drift_prob)
    self.cmd_drift[env_ids] = torch.where(use_drift, drift, torch.zeros_like(drift))
    new_dir = torch.stack((heading.cos(), heading.sin()), dim=-1)
    # A stop command keeps the previous direction for the approach geometry.
    self.ball_cmd_dir_w[env_ids] = torch.where(
      stop.unsqueeze(-1), self.ball_cmd_dir_w[env_ids], new_dir
    )
    if self.cfg.kick_prob > 0.0 or self.cfg.vanish_prob > 0.0:
      self._resample_ball_events(env_ids, ball_xy)
    self._tail_err_sum[env_ids] = 0.0
    self._tail_vel_sum[env_ids] = 0.0
    self._tail_steps[env_ids] = 0.0
    self.redirect_latched[env_ids] = False
    self.win_touched[env_ids] = False
    self.time_since_win_touch[env_ids] = 0.0
    self.window_time[env_ids] = 0.0
    self.speed_reached[env_ids] = False
    self.speed_reach_time[env_ids] = 0.0
    if self._in_reset:
      self._window_post_touch[env_ids] = False
    else:
      self._window_post_touch[env_ids] = self.has_touched[env_ids]

  def _resample_ball_events(self, env_ids: torch.Tensor, ball_xy: torch.Tensor) -> None:
    """v22, at a window resample: replace a kicked ball with a new one, take the
    ball away (vanish), and draw kick windows. ``ball_xy`` is the ball position
    the resample used for these envs (updated here for moved balls)."""
    n, device = len(env_ids), self.device
    ball_xy = ball_xy.clone()
    if not self._in_reset:
      kicked = self.kick_mode[env_ids] & self.kick_done[env_ids]
      vanish = (
        ~kicked
        & self.has_touched[env_ids]
        & (torch.rand(n, device=device) < self.cfg.vanish_prob)
      )
      for mask, dist in (
        (kicked, self.cfg.respawn_dist),
        (vanish, self.cfg.vanish_dist),
      ):
        if bool(mask.any()):
          ball_xy[mask] = self._move_ball(env_ids[mask], dist)
      log = self._env.extras.setdefault("log", {})
      log["Metrics/ball_respawn_frac"] = kicked.float().mean()
      log["Metrics/ball_vanish_frac"] = vanish.float().mean()
    kick = torch.rand(n, device=device) < self.cfg.kick_prob
    # The ending window's outcome, for evals that read it after the resample.
    self.prev_window_kick_done[env_ids] = (
      self.kick_mode[env_ids] & self.kick_done[env_ids]
    )
    self.kick_mode[env_ids] = kick
    self.kick_done[env_ids] = False
    self._kicked_once[env_ids] = False
    self.kick_wait[env_ids] = 0.0
    if not bool(kick.any()):
      return
    k_ids = env_ids[kick]
    to_ball = ball_xy[kick] - _root_pose(self.robot, k_ids)[:, :2]
    half, lo = self.cfg.kick_half_angle, self.cfg.kick_min_angle
    off = torch.empty(len(k_ids), device=device).uniform_(lo, half)
    sign = torch.where(torch.rand(len(k_ids), device=device) < 0.5, -1.0, 1.0)
    heading = torch.atan2(to_ball[:, 1], to_ball[:, 0]) + sign * off
    self.ball_cmd_dir_w[k_ids] = torch.stack((heading.cos(), heading.sin()), dim=-1)
    # v35 geometry gate: how far the kick turns away from the robot-to-ball line.
    self.kick_offset[k_ids] = off
    self.ball_cmd_speed[k_ids] = 0.0
    self.cmd_drift[k_ids] = 0.0
    length = torch.empty(len(k_ids), device=device).uniform_(*self.cfg.kick_window_s)
    self.time_left[k_ids] = length
    self.window_len[k_ids] = length

  def _move_ball(
    self, env_ids: torch.Tensor, dist: tuple[float, float]
  ) -> torch.Tensor:
    """Put the ball, at rest, ``dist`` from the robot at any bearing. The robot's
    ball memory is left as it was: it has to find the new ball."""
    m, device = len(env_ids), self.device
    angle = torch.empty(m, device=device).uniform_(-math.pi, math.pi)
    radius = torch.empty(m, device=device).uniform_(*dist)
    xy = self.robot.data.root_link_pos_w[env_ids, :2] + radius.unsqueeze(
      -1
    ) * torch.stack((angle.cos(), angle.sin()), dim=-1)
    state = self.ball.data.default_root_state[env_ids].clone()
    state[:, 0:2] = xy
    state[:, 2] = (
      self._env.scene.env_origins[env_ids, 2]
      + ball_radius(self._env, env_ids)
      + self.cfg.spawn_clearance
    )
    state[:, 3:7] = 0.0
    state[:, 3] = 1.0
    state[:, 7:] = 0.0
    self.ball.write_root_state_to_sim(state, env_ids)
    self.has_touched[env_ids] = False
    self.far_time[env_ids] = 0.0
    return xy

  def _update_kick(self, dt: float) -> None:
    """v22: detect the window's kick (kick_loop.classify_touch) and score its
    ground speed, direction error and loft; gate AMP style off around it."""
    touch = self.touch_lr.any(dim=-1)
    vel3 = self.ball.data.root_link_lin_vel_w
    vel = vel3[:, :2]
    speed = vel.norm(dim=-1)
    kick, _, _ = classify_touch(
      touch, self._prev_touch_any, speed, self._prev_ball_speed, self.time_since_kick
    )
    first = kick & self.kick_mode & ~self.kick_done
    along = (vel * self.ball_cmd_dir_w).sum(dim=-1)
    self.launch_event[:] = kick
    self.launch_along[:] = along
    cos = along / speed.clamp(min=1.0e-6)
    err = torch.acos(cos.clamp(-1.0, 1.0))
    angle = torch.atan2(vel3[:, 2], speed.clamp(min=1.0e-3))
    self.kick_event[:] = first
    # v33 (user: "air ball is fine"): kick_air_ok pays the 3D launch speed with
    # no loft penalty; otherwise ground speed and loft_factor as the kick loop.
    launch = vel3.norm(dim=-1) if self.cfg.kick_air_ok else speed
    self.kick_speed[:] = torch.where(first, launch, self.kick_speed)
    self.kick_err[:] = torch.where(first, err, self.kick_err)
    loft = torch.ones_like(angle) if self.cfg.kick_air_ok else loft_factor(angle)
    self.kick_loft[:] = torch.where(first, loft, self.kick_loft)
    if bool(first.any()):
      self.kick_sole_ratio[:] = torch.where(
        first, self._sole_yaw_ratio(), self.kick_sole_ratio
      )
    self._ema_add("kick_speed", speed, first)
    self._ema_add("kick_err_deg", torch.rad2deg(err), first)
    self._ema_add("kick_wait_s", self.kick_wait, first)
    d = (
      self.ball.data.root_link_pos_w[:, :2] - self.robot.data.root_link_pos_w[:, :2]
    ).norm(dim=-1)
    # v32 (user): a kick that leaves the ball within kick_leave_dist is not the
    # end; keep kicking until it leaves, then stand. 0 = done on the first kick.
    self._kicked_once |= first
    self.kick_done |= self._kicked_once & (d > self.cfg.kick_leave_dist)
    self.time_since_kick[:] = torch.where(
      kick, torch.zeros_like(self.time_since_kick), self.time_since_kick + dt
    )
    self.kick_wait += dt * (self.kick_mode & ~self.kick_done).float()
    self._prev_touch_any[:] = touch
    self._prev_ball_speed[:] = speed
    # Style off while lining up near the ball and through the swing: the AMP
    # reference has no kicks (as the kick loop gates it around each kick).
    off = self.kick_mode & (
      (~self.kick_done & (d < 1.2)) | (self.time_since_kick < 0.6)
    )
    self._env.amp_style_gate[:] = (~off).float()  # ty: ignore[unresolved-attribute]

  def _sole_yaw_ratio(self) -> torch.Tensor:
    """B-Human's inside-kick pose (bhuman_kick ``kick_sole_yaw_ratio``): the
    kicking foot's yaw minus the kick direction should be +90 deg (left foot)
    or -90 deg (right); exp(-diff^2 / sole_yaw_sigma). The kicking foot is the
    one touching now, else the last touch side."""
    q = self.robot.data.body_link_quat_w[:, self._gait_feet_ids]
    yaw_l, yaw_r = _yaw_angle(q[:, 0]), _yaw_angle(q[:, 1])
    left = torch.where(
      self.touch_lr.any(dim=-1), self.touch_lr[:, 0], self.last_touch_side > 0
    )
    kick_yaw = torch.atan2(self.ball_cmd_dir_w[:, 1], self.ball_cmd_dir_w[:, 0])
    rel = torch.where(left, yaw_l, yaw_r) - kick_yaw
    target = torch.where(left, 1.0, -1.0) * (math.pi / 2.0)
    diff = torch.atan2(torch.sin(target - rel), torch.cos(target - rel))
    return torch.exp(-diff.square() / self.cfg.sole_yaw_sigma)

  def _update_touch(self) -> None:
    """Once per env step: per-foot touches, the touch memory, the per-episode
    touched flag and the left/right touch metrics."""
    step = int(self._env.common_step_counter)
    if step == self._touch_step:
      return
    self._touch_step = step
    found = self._env.scene["feet_ball_contact"].data.found
    if found is not None:
      # Sensor primaries are (left_foot_link, right_foot_link), one slot each.
      lr = found.reshape(self.num_envs, 2, -1).amax(dim=-1) > 0
    else:
      lr = torch.zeros(self.num_envs, 2, dtype=torch.bool, device=self.device)
    self.touch_lr[:] = lr
    touch = lr.any(dim=-1)
    self.last_touch_side[:] = torch.where(
      lr[:, 0],
      torch.ones_like(self.last_touch_side),
      torch.where(
        lr[:, 1], -torch.ones_like(self.last_touch_side), self.last_touch_side
      ),
    )
    alt, same, new_side, new_time = classify_alternate_tap(
      lr,
      self.touch_lr_prev,
      self.tap_side,
      self.time_since_tap,
      float(self._env.step_dt),
    )
    self.alt_touch_event[:] = alt
    self.same_touch_event[:] = same
    self.tap_side[:] = new_side
    self.time_since_tap[:] = new_time
    self.touch_lr_prev[:] = lr
    decay = 1.0 - 1.0 / TOUCH_EMA_STEPS
    self._alt_tap_ema.mul_(decay).add_(
      torch.stack((alt.float().sum(), same.float().sum()))
    )
    alt_total = self._alt_tap_ema.sum()
    alt_share = torch.where(
      alt_total > 0,
      self._alt_tap_ema[0] / alt_total.clamp(min=1.0e-6),
      torch.full_like(alt_total, 0.5),
    )
    self.steps_since_touch[:] = torch.where(
      touch, torch.zeros_like(self.steps_since_touch), self.steps_since_touch + 1.0
    )
    # A contact reported on an env's first step comes from before its reset.
    valid_touch = touch & (self._env.episode_length_buf > 0)
    self.has_touched |= valid_touch
    self.win_touched |= valid_touch
    rates = lr.float().mean(dim=0)
    self._touch_ema.mul_(decay).add_(lr.float().sum(dim=0))
    total_ema = self._touch_ema.sum()
    share = torch.where(
      total_ema > 0,
      self._touch_ema[0] / total_ema.clamp(min=1.0e-6),
      torch.full_like(total_ema, 0.5),
    )
    log = self._env.extras.setdefault("log", {})
    log["Metrics/dribble_touch_left"] = rates[0]
    log["Metrics/dribble_touch_right"] = rates[1]
    log["Metrics/dribble_touch_total"] = touch.float().mean()
    log["Metrics/dribble_touch_left_share"] = share
    log["Metrics/dribble_alt_touch"] = alt.float().mean()
    log["Metrics/dribble_same_touch"] = same.float().mean()
    log["Metrics/dribble_alt_touch_share"] = alt_share

  def recent_touch(self, window_steps: int = 10) -> torch.Tensor:
    """True where a foot touched the ball within the last ``window_steps`` steps
    (this step included). The counter advances once per env step."""
    self._update_touch()
    return self.steps_since_touch < window_steps

  def _ground_ball(self, env_ids: torch.Tensor) -> None:
    """Put the spawned ball on the ground of its terrain patch.

    The approach spawn takes the ball height from the robot root (minus a
    nominal 0.53 m), but the AMP pose-pool reset starts the robot crouched or
    mid-stride, so ~20 % of balls spawned inside the ground and were ejected.
    The patch origin is the ground; ``spawn_clearance`` covers the field bumps.
    """
    state = self.ball.data.default_root_state[env_ids].clone()
    state[:, 0:2] = self.last_seen_ball_w[env_ids]
    state[:, 2] = (
      self._env.scene.env_origins[env_ids, 2]
      + ball_radius(self._env, env_ids)
      + self.cfg.spawn_clearance
    )
    state[:, 3:7] = 0.0
    state[:, 3] = 1.0
    state[:, 7:] = 0.0
    self.ball.write_root_state_to_sim(state, env_ids)

  def create_gui(
    self,
    name: str,
    server: viser.ViserServer,
    get_env_idx: Callable[[], int],
    on_change: Callable[[], None] | None = None,
    request_action: Callable[[str, Any], None] | None = None,
  ) -> None:
    """Viewer controls (2026-10-21, user): drive every env by hand with a
    mode (dribble / stop / kick), a field direction and a ball speed, and drop
    a new ball next to the robots. Off = the task's own command windows."""
    super().create_gui(name, server, get_env_idx, on_change, request_action)
    with server.gui.add_folder("Dribble control"):
      self._gui_manual = server.gui.add_checkbox("Manual control", initial_value=False)
      self._gui_mode = server.gui.add_dropdown(
        "Mode", options=("dribble", "stop", "kick"), initial_value="dribble"
      )
      self._gui_heading = server.gui.add_slider(
        "Direction (deg, field)", min=-180.0, max=180.0, step=5.0, initial_value=0.0
      )
      self._gui_speed = server.gui.add_slider(
        "Speed (m/s)", min=0.2, max=2.0, step=0.1, initial_value=0.8
      )
      new_ball = server.gui.add_button("New ball (~1 m away)")

      @self._gui_mode.on_update
      def _(_ev) -> None:
        # Each switch into kick arms one fresh kick.
        self.kick_done[:] = False
        self._kicked_once[:] = False
        self.kick_wait[:] = 0.0

      @new_ball.on_click
      def _(_ev) -> None:
        self._gui_new_ball = True

  def _apply_gui_command(self) -> None:
    """Overwrite every env's command with the viewer's manual one."""
    if self._gui_new_ball:
      self._gui_new_ball = False
      ids = torch.arange(self.num_envs, device=self.device)
      self._move_ball(ids, (0.8, 1.2))
      self.kick_done[:] = False
      self._kicked_once[:] = False
      self.kick_wait[:] = 0.0
    mode = self._gui_mode.value
    angle = math.radians(float(self._gui_heading.value))
    self.ball_cmd_dir_w[:, 0] = math.cos(angle)
    self.ball_cmd_dir_w[:, 1] = math.sin(angle)
    self.ball_cmd_speed[:] = float(self._gui_speed.value) if mode == "dribble" else 0.0
    self.kick_mode[:] = mode == "kick"
    self.cmd_drift[:] = 0.0
    self.time_left[:] = 1.0e6  # no automatic window resampling while manual

  def _update_command(self) -> None:
    manual = self._gui_manual is not None and bool(self._gui_manual.value)
    if manual:
      self._apply_gui_command()
    elif self._gui_was_manual:
      self.time_left[:] = 0.05  # back to the task's windows: resample now
    self._gui_was_manual = manual
    dt = max(float(self._env.step_dt), 1.0e-3)
    if self.cfg.cmd_drift_prob > 0.0:
      ang = self.cmd_drift * dt
      c, s_ = ang.cos(), ang.sin()
      d = self.ball_cmd_dir_w
      self.ball_cmd_dir_w[:] = torch.stack(
        (c * d[:, 0] - s_ * d[:, 1], s_ * d[:, 0] + c * d[:, 1]), dim=-1
      )
    if self.cfg.ball_memory:
      # Propagate the predicted ball position while unseen using the estimated
      # velocity, decaying with turf rolling friction.
      unseen_active = ~self._was_visible & ~self.ball_lost & ~self.never_seen
      self.last_seen_ball_w[:] = torch.where(
        unseen_active.unsqueeze(-1),
        self.last_seen_ball_w + self.pred_ball_vel_w * dt,
        self.last_seen_ball_w,
      )
      self.pred_ball_vel_w[:] = torch.where(
        unseen_active.unsqueeze(-1),
        self.pred_ball_vel_w * math.exp(-1.5 * dt),
        self.pred_ball_vel_w,
      )

    ball_xy = self.ball.data.root_link_pos_w[:, :2]
    self.target_w[:] = ball_xy + VIRTUAL_TARGET_DIST * self.ball_cmd_dir_w
    was_lost = self.ball_lost.clone()
    super()._update_command()

    if self.cfg.ball_memory:
      visible = self.see_ball > 0.5
      both_vis = visible & self._was_visible
      obs_vel = ((self.last_seen_ball_w - self._prev_seen_ball_w) / dt).clamp(-3.0, 3.0)
      self.pred_ball_vel_w[:] = torch.where(
        both_vis.unsqueeze(-1),
        0.5 * self.pred_ball_vel_w + 0.5 * obs_vel,
        self.pred_ball_vel_w,
      )
      self._prev_seen_ball_w[:] = torch.where(
        visible.unsqueeze(-1), self.last_seen_ball_w, self._prev_seen_ball_w
      )
      self._was_visible[:] = visible
      # When newly lost and the predicted ball y was nearly dead-center, fall
      # back to the last foot-touch side for the spin direction.
      newly_lost = self.ball_lost & ~was_lost
      near_center = self.last_seen_ball_b[:, 1].abs() < 0.08
      self.lost_dir[:] = torch.where(
        newly_lost & near_center, self.last_touch_side, self.lost_dir
      )
      # Slot 74 is 0.0 when ball_lost so the actor distinguishes virtual-ball
      # spin search (slot 74 == 0) from live/aging ball prediction (slot 74 > 0).
      self.ball_age_obs[:] = torch.where(
        self.ball_lost, torch.zeros_like(self.ball_age_obs), self.ball_age_obs
      )
      log = self._env.extras.setdefault("log", {})
      log["Metrics/dribble_ball_age"] = self.ball_age_obs.mean()
      log["Metrics/dribble_ball_lost_frac"] = self.ball_lost.float().mean()

    if self.cfg.kick_prob > 0.0:
      self._update_kick(dt)
    moving = self.ball_cmd_speed > 0.0
    # Slots 78–79: commanded direction in the yaw frame (ball velocity, or the
    # kick direction in a kick window; zero for stop).
    rel = self.ball_cmd_dir_w
    yaw = _yaw_angle(self.robot.data.root_link_quat_w)
    c, s = yaw.cos(), yaw.sin()
    dir_b = torch.stack(
      (c * rel[:, 0] + s * rel[:, 1], -s * rel[:, 0] + c * rel[:, 1]), dim=-1
    )
    self.kick_dir_b[:] = dir_b * (moving | self.kick_mode).unsqueeze(-1)
    # Slots 80–82: stop flag, exact commanded speed (m/s), kick flag (v22; 0
    # before).
    self.kick_range[:] = 0.0
    # In a kick window slot 80 is the "kicked" flag (v24): (0, 0, 1) = kick,
    # (1, 0, 1) = kicked, stand. Without it a far ball after the kick looked
    # like a far ball still to kick (the actor has no memory).
    self.kick_range[:, 0] = torch.where(self.kick_mode, self.kick_done, ~moving).float()
    self.kick_range[:, 1] = self.ball_cmd_speed
    self.kick_range[:, 2] = self.kick_mode.float()
    # Hidden walk flag: keep the gait terms on while there is a ball to move.
    self.vel_command_b[:, 0] = torch.where(
      moving | (self.kick_mode & ~self.kick_done),
      torch.full_like(self.ball_cmd_speed, WALK_COMMAND_SPEED),
      self.vel_command_b[:, 0],
    )

    # Success bookkeeping on the true ball state.
    ball_vel = self.ball.data.root_link_lin_vel_w[:, :2]
    cmd_vel = self.ball_cmd_dir_w * self.ball_cmd_speed.unsqueeze(-1)
    self.ball_vel_err[:] = torch.linalg.norm(ball_vel - cmd_vel, dim=-1)
    robot_xy = self.robot.data.root_link_pos_w[:, :2]
    self.ball_trunk_dist[:] = torch.linalg.norm(ball_xy - robot_xy, dim=-1)
    in_tail = self.time_left <= self.cfg.success_tail_s
    self._tail_err_sum += self.ball_vel_err * in_tail
    self._tail_vel_sum += ball_vel * in_tail.unsqueeze(-1)
    self._tail_steps += in_tail.float()
    far = self.ball_trunk_dist > self.cfg.lost_ball_dist
    if self.cfg.lost_needs_touch:
      far = far & self.has_touched & ~self.kick_mode
    self.far_time[:] = torch.where(
      far, self.far_time + self._env.step_dt, torch.zeros_like(self.far_time)
    )


@dataclass(kw_only=True)
class DribbleCommandCfg(ApproachYawCommandCfg):
  """Dribble command. Resamples the ball-velocity command every window."""

  resampling_time_range: tuple[float, float] = (4.0, 4.0)
  ball_memory: bool = True
  ball_memory_tau: float = 0.6
  memory_invalidate: bool = True
  memory_lost_in_view_s: float = 0.5
  memory_lost_timeout_s: float = 1.5
  lost_virtual_ball: bool = True
  lost_virtual_bearing: float = 1.6
  lost_virtual_range: float = 1.2
  memory_odometry: bool = True
  ball_speed_range: tuple[float, float] = (0.2, 0.8)
  """Commanded ball speed when moving (m/s)."""
  stop_prob: float = 0.1
  """Share of windows that command the ball to stop near the robot."""
  fast_speed_edge: float = 0.5
  """Slow/fast edge of the speed one-hot (m/s)."""
  cmd_heading_half_angle: float = math.pi
  """Command direction within this half-angle of the robot-to-ball bearing."""
  collinear_drill_prob: float = 0.25
  """Share of moving windows where the robot starts collinear between the ball and
  the target (cmd_dir ~180° opposite to robot->ball) at step-over range."""
  success_tail_s: float = 2.0
  success_vel_err: float = 0.25
  """Cap on the moving-command error bound (m/s)."""
  success_vel_rel: float = 0.5
  """Moving-command error bound as a share of the commanded speed."""
  success_stop_err: float = 0.1
  """Ball speed bound for a stop command (m/s)."""
  success_ball_dist: float = 1.0
  push_dist_extra: float = 0.0
  """v21 push-and-chase: success_ball_dist grows by this much (m) across
  push_speed_range, so a fast window may end with the ball pushed ahead."""
  push_speed_range: tuple[float, float] = (0.9, 1.5)
  speed_gate_achieved_frac: float = 0.0
  sole_yaw_sigma: float = 1.0
  """v27 side kick: width of the inside-kick sole-yaw match (B-Human stage 2
  uses 1.0, stage 3 narrows to 0.1)."""
  """v27: > 0 = the speed curriculum counts a window when its tail ball speed
  along the command reaches this share of the command (0 = window success)."""
  kick_prob: float = 0.0
  """v22 kick mode (obs slot 82): share of command windows that ask for one
  straight kick along the commanded direction, then standing still."""
  kick_window_s: tuple[float, float] = (6.0, 9.0)
  kick_half_angle: float = math.pi / 2.0
  kick_min_angle: float = 0.0
  """Kick direction at least this far (rad) off the robot-to-ball bearing
  (viewer demos of angled kicks; 0 in training)."""
  """Kick direction within this half-angle of the robot-to-ball bearing, so
  lining up often needs side steps."""
  kick_air_ok: bool = False
  """v33: kicks are scored on 3D launch speed with no loft penalty."""
  kick_leave_dist: float = 0.0
  """v32: the kick counts as done (slot 80, then stand) only once the ball is
  this far (m) from the trunk after a kick; until then further kicks pay.
  0 = done on the first kick (v22-v31)."""
  kick_success_speed: float = 4.0
  kick_success_err: float = 0.26
  """A kick window succeeds with one kick this fast (m/s) within this angle
  (rad) of the command and the robot standing (< 0.25 m/s) at the end."""
  respawn_dist: tuple[float, float] = (1.0, 8.0)
  """After a kick window the kicked ball is replaced by a new one this far away
  (m), at any bearing: approach and search practice."""
  vanish_prob: float = 0.0
  """v22: share of windows after the first touch where the ball is moved
  vanish_dist away at any bearing (taken away), so it must be found again."""
  vanish_dist: tuple[float, float] = (1.5, 5.0)
  lost_needs_touch: bool = False
  """v22: ball_lost counts only after the first touch of the current ball and
  outside kick windows (far spawns, respawns and kicked balls are not lost)."""
  spawn_clearance: float = 0.02
  """Ball spawn height above its patch ground (m); the field bumps reach 2 cm."""
  lost_ball_dist: float = 3.0
  """Ball farther than this from the trunk counts toward ``dribble_ball_lost``."""
  speed_curriculum: bool = False
  """Draw moving speeds from (ball_speed_range[0], speed_hi), speed_hi raised by
  top-band success (reward-tune iter 6); off = ball_speed_range as is."""
  speed_hi_start: float = 0.6
  speed_hi_max: float = 1.5
  speed_hi_step: float = 0.1
  speed_band_width: float = 0.2
  """Top band = commanded speeds in [hi - width, hi] (m/s)."""
  speed_band_success: float = 0.25
  speed_band_min_windows: int = 200
  speed_curriculum_period_steps: int = 1200
  """Evaluation period in env steps (common_step_counter; 24 per PPO iteration)."""
  speed_gate_post_touch: bool = False
  """Count only windows that start after the episode's first foot-ball touch in
  the curriculum gate (reward-tune iter 7). Scored window success is unchanged."""
  speed_gate_relative: bool = False
  """Reward-tune iter 8: advance when top-band success >= speed_gate_ratio *
  low-band success AND low-band success >= speed_low_min_success (instead of
  the absolute speed_band_success threshold); >= speed_band_min_windows top-band
  windows still required."""
  speed_gate_ratio: float = 0.5
  speed_low_band: tuple[float, float] = (0.2, 0.4)
  """Low (easy) band of commanded speeds for the relative gate (m/s)."""
  speed_low_min_success: float = 0.10
  top_band_prob: float = 0.0
  """Reward-tune iter 11: probability that a moving command speed is drawn from
  the top band [max(ball_speed_range[0], hi - speed_band_width), hi] instead of
  uniformly from [ball_speed_range[0], hi]."""
  cmd_drift_prob: float = 0.0
  """Deploy match: share of moving windows whose direction turns steadily."""
  cmd_drift_max: float = 0.6
  """Largest turn rate of a drifting command (rad/s)."""
  fast_window_min_speed: float = 0.9
  """v15: commanded speeds (m/s) at or above this get the fast-window rules."""
  fast_window_s: tuple[float, float] | None = None
  """v15: window length range (s) for fast commands; None = resampling_time_range."""
  fast_turn_half_angle: float = math.pi
  """v15: after the first touch, a fast command turns at most this far (rad) from
  the previous command; pi = any direction."""
  amp_style_weight: float | None = None
  """Reward-tune iter 9: constant AMP style weight set by the task (overrides the
  AMP wrapper's ``amp_style_weight`` curriculum); None leaves it alone."""

  def build(self, env: ManagerBasedRlEnv) -> DribbleCommand:
    return DribbleCommand(self, env)


def _dribble(env: ManagerBasedRlEnv) -> DribbleCommand:
  term = env.command_manager.get_term("twist")
  assert isinstance(term, DribbleCommand)
  return term


def amp_dribble_cond(env: ManagerBasedRlEnv) -> torch.Tensor:
  """v20 style condition, APEX-style command coupling for the discriminator:
  [s / 2, cos, sin of the commanded ball direction in the robot yaw frame, 1]
  once the ball is under control (touched, not lost); direction zeros for a
  stop. Zeros (the "free" condition) before the first touch and while lost.
  The motion loader labels expert frames with their own smoothed travel
  velocity in the same layout (MotionLoader cond_dim)."""
  cmd = _dribble(env)
  yaw = _yaw_angle(env.scene["robot"].data.root_link_quat_w)
  rel = torch.atan2(cmd.ball_cmd_dir_w[:, 1], cmd.ball_cmd_dir_w[:, 0]) - yaw
  s = cmd.ball_cmd_speed
  moving = (s > 0.0).float()
  cond = torch.stack(
    (
      s / COND_SPEED_SCALE,
      torch.cos(rel) * moving,
      torch.sin(rel) * moving,
      torch.ones_like(s),
    ),
    dim=-1,
  )
  # Kick window (v22): free while lining up and kicking (style is gated off
  # there), then [0, 0, 0, 1] = stand while it waits for the next command.
  active = torch.where(cmd.kick_mode, cmd.kick_done, cmd.has_touched & ~cmd.ball_lost)
  return cond * active.float().unsqueeze(-1)


def dribble_ball_lost(env: ManagerBasedRlEnv, grace_s: float = 2.0) -> torch.Tensor:
  """Ball farther than ``lost_ball_dist`` from the trunk for ``grace_s``."""
  return _dribble(env).far_time >= grace_s


def dribble_window_success(env: ManagerBasedRlEnv) -> torch.Tensor:
  """1 / windows-per-episode on the step a command window succeeds.

  Its episodic sum is the share of successful windows, so with weight w the
  logged nominal return / w is the dribble success rate.
  """
  cmd = _dribble(env)
  base_len = cmd.cfg.resampling_time_range[0]
  per_episode = max(env.max_episode_length_s / base_len, 1.0)
  # v15: a longer (fast) window pays in proportion to its length, so the
  # success rate of the time spent dribbling keeps the same payout.
  return cmd.window_success.float() * (cmd.window_len / base_len) / per_episode


# ---------------------------------------------------------------------------
# Left/right mirror for PPO symmetry augmentation (reward-tune iter 7).
#
# Mirror = reflection through the robot's sagittal (x-z) plane, i.e. y -> -y.
# Polar vectors (positions, linear velocities, forces, gravity) negate their y
# component; axial vectors (angular velocities) negate x and z; angles about z
# (yaw) and their sines negate; magnitudes, flags and speeds are invariant; L/R
# pairs swap. Joints use the K1 swap of amp_symmetry (L<->R, roll/yaw axes
# negated).
#
# Dribble actor (83):
#   0-2   base ang vel (IMU, body)        x neg, y keep, z neg
#   3-5   projected gravity (body)        y neg
#   6-27  joint pos rel (biased)          K1 joint swap
#   28-49 joint vel                       K1 joint swap
#   50-71 last action                     K1 joint swap
#   72-73 ball xy (trunk frame, masked)   y neg
#   74    ball memory age (0 here)        keep
#   75-77 |vx|, |vy|, |wz| limits         keep
#   78-79 command dir (cos, sin), yaw fr. sin neg
#   80-82 stop flag, speed, 0             keep
# Dribble critic (98) = the actor layout (true ball in 72-73) plus
#   83-85 base lin vel (IMU, body)        y neg
#   86-87 foot height (L, R)              swap
#   88-89 foot air time (L, R)            swap
#   90-91 foot contact (L, R)             swap
#   92-97 foot net force (L xyz, R xyz)   swap triples, y neg
# ---------------------------------------------------------------------------

DRIBBLE_ACTOR_DIM = 83
DRIBBLE_CRITIC_DIM = 98
DRIBBLE_JOINT_BLOCKS = ((6, 28), (28, 50), (50, 72))
DRIBBLE_ACTOR_NEGATE = (0, 2, 4, 73, 79)
DRIBBLE_CRITIC_NEGATE = DRIBBLE_ACTOR_NEGATE + (84,)
DRIBBLE_CRITIC_SWAP_SRC = (86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97)
DRIBBLE_CRITIC_SWAP_DST = (87, 86, 89, 88, 91, 90, 95, 96, 97, 92, 93, 94)
DRIBBLE_CRITIC_FORCE_Y = (93, 96)


def _mirror_joint_blocks(obs: torch.Tensor) -> None:
  from k1.tasks.velocity.mdp.amp_symmetry import (
    K1_INVERTED_JOINT_INDICES,
    _switch_k1_joints_left_right,
  )

  for a, b in DRIBBLE_JOINT_BLOCKS:
    obs[:, a:b] = _switch_k1_joints_left_right(obs[:, a:b], K1_INVERTED_JOINT_INDICES)


def flip_dribble_actor_obs(obs: torch.Tensor) -> torch.Tensor:
  """Left/right mirror of the 83-dim dribble actor observation."""
  if obs.shape[1] != DRIBBLE_ACTOR_DIM:
    raise ValueError(
      f"dribble actor obs must be {DRIBBLE_ACTOR_DIM}-dim, got {obs.shape[1]}"
    )
  out = obs.clone()
  _mirror_joint_blocks(out)
  out[:, list(DRIBBLE_ACTOR_NEGATE)] = -out[:, list(DRIBBLE_ACTOR_NEGATE)]
  return out


def flip_dribble_critic_obs(obs: torch.Tensor) -> torch.Tensor:
  """Left/right mirror of the 98-dim dribble critic observation."""
  if obs.shape[1] != DRIBBLE_CRITIC_DIM:
    raise ValueError(
      f"dribble critic obs must be {DRIBBLE_CRITIC_DIM}-dim, got {obs.shape[1]}"
    )
  out = obs.clone()
  _mirror_joint_blocks(out)
  out[:, list(DRIBBLE_CRITIC_SWAP_DST)] = obs[:, list(DRIBBLE_CRITIC_SWAP_SRC)]
  neg = list(DRIBBLE_CRITIC_NEGATE + DRIBBLE_CRITIC_FORCE_Y)
  out[:, neg] = -out[:, neg]
  return out


def flip_dribble_actions(actions: torch.Tensor) -> torch.Tensor:
  from k1.tasks.velocity.mdp.amp_symmetry import (
    K1_ACTION_DIM,
    K1_INVERTED_JOINT_INDICES,
    _switch_k1_joints_left_right,
  )

  if actions.shape[1] != K1_ACTION_DIM:
    raise ValueError(f"action dim must be {K1_ACTION_DIM}, got {actions.shape[1]}")
  return _switch_k1_joints_left_right(actions, K1_INVERTED_JOINT_INDICES)


def augment_symmetries_dribble(env, obs, actions):
  """rsl_rl symmetry hook for the dribble task: originals first, then mirrors.

  Same calling convention as ``amp_symmetry.augment_symmetries``.
  """
  del env
  from tensordict import TensorDict

  if obs is not None:
    actor = obs["actor"]
    critic = obs["critic"]
    n = actor.shape[0]
    obs = TensorDict(
      {
        "actor": torch.cat((actor, flip_dribble_actor_obs(actor)), dim=0),
        "critic": torch.cat((critic, flip_dribble_critic_obs(critic)), dim=0),
      },
      batch_size=(2 * n,),
    )
  if actions is not None:
    actions = torch.cat((actions, flip_dribble_actions(actions)), dim=0)
  return obs, actions

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
from typing import TYPE_CHECKING

import torch

from mjlab.tasks.velocity.mdp.approach import (
  WALK_COMMAND_SPEED,
  ApproachYawCommand,
  ApproachYawCommandCfg,
  _root_pose,
  _yaw_angle,
  ball_radius,
)

if TYPE_CHECKING:
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


class DribbleCommand(ApproachYawCommand):
  """Ball spawn and speed limits per episode; ball velocity command per window."""

  cfg: DribbleCommandCfg

  def __init__(self, cfg: DribbleCommandCfg, env: ManagerBasedRlEnv):
    super().__init__(cfg, env)
    n, device = self.num_envs, self.device
    self.ball_cmd_dir_w = torch.zeros(n, 2, device=device)
    self.ball_cmd_dir_w[:, 0] = 1.0
    self.ball_cmd_speed = torch.zeros(n, device=device)
    self.ball_vel_err = torch.zeros(n, device=device)
    self.ball_trunk_dist = torch.zeros(n, device=device)
    self.far_time = torch.zeros(n, device=device)
    self.window_success = torch.zeros(n, dtype=torch.bool, device=device)
    self._tail_err_sum = torch.zeros(n, device=device)
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
      )
    }
    self._style_patched = False
    self.metrics["ball_vel_err"] = torch.zeros(n, device=device)
    self.metrics["dribble_success_rate"] = torch.zeros(n, device=device)
    # The task owns the AMP style gate: style stays on everywhere (the inherited
    # gate fades it with robot-ball distance).
    env.amp_style_gate = torch.ones(n, device=device)  # ty: ignore[unresolved-attribute]

  def reset(self, env_ids: torch.Tensor | slice | None) -> dict[str, float]:
    # Cleared before the reset resample so the first window is pre-touch.
    self.has_touched[env_ids] = False
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
      self._update_time_to_speed(ending)
      self._update_gait()
    tail_err = self._tail_err_sum / self._tail_steps.clamp(min=1.0)
    # Relative bound while moving, so a ball left still never passes a slow command.
    moving = self.ball_cmd_speed > 0.0
    thr = torch.where(
      moving,
      (self.cfg.success_vel_rel * self.ball_cmd_speed).clamp(max=self.cfg.success_vel_err),
      torch.full_like(tail_err, self.cfg.success_stop_err),
    )
    ok = (
      (self._tail_steps > 0)
      & (tail_err < thr)
      & (self.ball_trunk_dist < self.cfg.success_ball_dist)
    )
    self.window_success[:] = ending & ok
    self._update_touch()
    self._windows += ending.float()
    self._successes += self.window_success.float()
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
    self._band_successes += (band & self.window_success).float().sum()
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
    self._low_successes += (low & self.window_success).float().sum()
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
        )
      else:
        passed = rate >= self.cfg.speed_band_success
      if n_win >= self.cfg.speed_band_min_windows and passed:
        self.speed_hi = min(self.speed_hi + self.cfg.speed_hi_step, self.cfg.speed_hi_max)
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
    log["Metrics/top_band_cmd_share"] = self._top_cmd_ema[0] / self._top_cmd_ema[1].clamp(
      min=1.0e-6
    )

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
    self.speed_reach_time[:] = torch.where(newly, self.window_time, self.speed_reach_time)
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
    d = torch.linalg.norm(self.ball.data.root_link_pos_w[:, :2] - robot.root_link_pos_w[:, :2], dim=-1)
    self._ema_add(
      "robot_speed_along_cmd_ratio", along_r / s.clamp(min=1.0e-3), (s > 0.0) & (d < 1.0)
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
    found = data.found.reshape(self.num_envs, len(sensor.primary_names), -1).amax(dim=-1) > 0
    contact = found[:, lr]
    robot = self.robot.data
    feet = robot.body_link_pos_w[:, self._gait_feet_ids, :2]
    yaw = _yaw_angle(robot.root_link_quat_w)
    head = torch.stack((yaw.cos(), yaw.sin()), dim=-1)
    fwd_l = torch.sum((feet[:, 0] - feet[:, 1]) * head, dim=-1)
    moving = torch.linalg.norm(robot.root_link_lin_vel_w[:, :2], dim=-1) > GAIT_MOVING_SPEED
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
    self.gait_air_last[:] = torch.where(touchdown, self.gait_air_run, self.gait_air_last)
    step_now = torch.stack((fwd_l, -fwd_l), dim=-1)
    fwd_step = touchdown & (step_now > 0.0)
    self.gait_step_last[:] = torch.where(fwd_step, step_now, self.gait_step_last)
    self.gait_air_run[:] = torch.where(
      contact, torch.zeros_like(self.gait_air_run), self.gait_air_run + dt
    )
    self.gait_contact_prev[:] = contact
    self._ema_add("gait_air_time_left", self.gait_air_last[:, 0], moving & touchdown[:, 0])
    self._ema_add("gait_air_time_right", self.gait_air_last[:, 1], moving & touchdown[:, 1])
    self._ema_add("gait_step_length_left", self.gait_step_last[:, 0], moving & fwd_step[:, 0])
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
    new_dir = torch.stack((heading.cos(), heading.sin()), dim=-1)
    # A stop command keeps the previous direction for the approach geometry.
    self.ball_cmd_dir_w[env_ids] = torch.where(
      stop.unsqueeze(-1), self.ball_cmd_dir_w[env_ids], new_dir
    )
    self._tail_err_sum[env_ids] = 0.0
    self._tail_steps[env_ids] = 0.0
    self.redirect_latched[env_ids] = False
    self.window_time[env_ids] = 0.0
    self.speed_reached[env_ids] = False
    self.speed_reach_time[env_ids] = 0.0
    if self._in_reset:
      self._window_post_touch[env_ids] = False
    else:
      self._window_post_touch[env_ids] = self.has_touched[env_ids]

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
    self.steps_since_touch[:] = torch.where(
      touch, torch.zeros_like(self.steps_since_touch), self.steps_since_touch + 1.0
    )
    # A contact reported on an env's first step comes from before its reset.
    self.has_touched |= touch & (self._env.episode_length_buf > 0)
    rates = lr.float().mean(dim=0)
    decay = 1.0 - 1.0 / TOUCH_EMA_STEPS
    self._touch_ema.mul_(decay).add_(lr.float().sum(dim=0))
    total_ema = self._touch_ema.sum()
    share = torch.where(
      total_ema > 0, self._touch_ema[0] / total_ema.clamp(min=1.0e-6),
      torch.full_like(total_ema, 0.5),
    )
    log = self._env.extras.setdefault("log", {})
    log["Metrics/dribble_touch_left"] = rates[0]
    log["Metrics/dribble_touch_right"] = rates[1]
    log["Metrics/dribble_touch_total"] = touch.float().mean()
    log["Metrics/dribble_touch_left_share"] = share

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

  def _update_command(self) -> None:
    ball_xy = self.ball.data.root_link_pos_w[:, :2]
    self.target_w[:] = ball_xy + VIRTUAL_TARGET_DIST * self.ball_cmd_dir_w
    super()._update_command()

    moving = self.ball_cmd_speed > 0.0
    # Slots 78–79: commanded direction in the yaw frame (zero for stop).
    rel = self.ball_cmd_dir_w
    yaw = _yaw_angle(self.robot.data.root_link_quat_w)
    c, s = yaw.cos(), yaw.sin()
    dir_b = torch.stack(
      (c * rel[:, 0] + s * rel[:, 1], -s * rel[:, 0] + c * rel[:, 1]), dim=-1
    )
    self.kick_dir_b[:] = dir_b * moving.unsqueeze(-1)
    # Slots 80–82: stop flag, exact commanded speed (m/s), unused (0).
    self.kick_range[:] = 0.0
    self.kick_range[:, 0] = (~moving).float()
    self.kick_range[:, 1] = self.ball_cmd_speed
    # Hidden walk flag: keep the gait terms on while there is a ball to move.
    self.vel_command_b[:, 0] = torch.where(
      moving, torch.full_like(self.ball_cmd_speed, WALK_COMMAND_SPEED),
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
    self._tail_steps += in_tail.float()
    far = self.ball_trunk_dist > self.cfg.lost_ball_dist
    self.far_time[:] = torch.where(
      far, self.far_time + self._env.step_dt, torch.zeros_like(self.far_time)
    )


@dataclass(kw_only=True)
class DribbleCommandCfg(ApproachYawCommandCfg):
  """Dribble command. Resamples the ball-velocity command every window."""

  resampling_time_range: tuple[float, float] = (4.0, 4.0)
  ball_speed_range: tuple[float, float] = (0.2, 0.8)
  """Commanded ball speed when moving (m/s)."""
  stop_prob: float = 0.1
  """Share of windows that command the ball to stop near the robot."""
  fast_speed_edge: float = 0.5
  """Slow/fast edge of the speed one-hot (m/s)."""
  cmd_heading_half_angle: float = math.pi
  """Command direction within this half-angle of the robot-to-ball bearing."""
  success_tail_s: float = 2.0
  success_vel_err: float = 0.25
  """Cap on the moving-command error bound (m/s)."""
  success_vel_rel: float = 0.5
  """Moving-command error bound as a share of the commanded speed."""
  success_stop_err: float = 0.1
  """Ball speed bound for a stop command (m/s)."""
  success_ball_dist: float = 1.0
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
  amp_style_weight: float | None = None
  """Reward-tune iter 9: constant AMP style weight set by the task (overrides the
  AMP wrapper's ``amp_style_weight`` curriculum); None leaves it alone."""

  def build(self, env: ManagerBasedRlEnv) -> DribbleCommand:
    return DribbleCommand(self, env)


def _dribble(env: ManagerBasedRlEnv) -> DribbleCommand:
  term = env.command_manager.get_term("twist")
  assert isinstance(term, DribbleCommand)
  return term


def dribble_ball_lost(env: ManagerBasedRlEnv, grace_s: float = 2.0) -> torch.Tensor:
  """Ball farther than ``lost_ball_dist`` from the trunk for ``grace_s``."""
  return _dribble(env).far_time >= grace_s


def dribble_window_success(env: ManagerBasedRlEnv) -> torch.Tensor:
  """1 / windows-per-episode on the step a command window succeeds.

  Its episodic sum is the share of successful windows, so with weight w the
  logged nominal return / w is the dribble success rate.
  """
  cmd = _dribble(env)
  per_episode = max(env.max_episode_length_s / cmd.cfg.resampling_time_range[0], 1.0)
  return cmd.window_success.float() / per_episode


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
  from mjlab.tasks.velocity.mdp.amp_symmetry import (
    K1_INVERTED_JOINT_INDICES,
    _switch_k1_joints_left_right,
  )

  for a, b in DRIBBLE_JOINT_BLOCKS:
    obs[:, a:b] = _switch_k1_joints_left_right(obs[:, a:b], K1_INVERTED_JOINT_INDICES)


def flip_dribble_actor_obs(obs: torch.Tensor) -> torch.Tensor:
  """Left/right mirror of the 83-dim dribble actor observation."""
  if obs.shape[1] != DRIBBLE_ACTOR_DIM:
    raise ValueError(f"dribble actor obs must be {DRIBBLE_ACTOR_DIM}-dim, got {obs.shape[1]}")
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
  from mjlab.tasks.velocity.mdp.amp_symmetry import (
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

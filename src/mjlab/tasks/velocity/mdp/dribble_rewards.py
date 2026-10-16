"""§6 reward for the dribble task — the surface /harbor:reward-tune edits.

``apply_dribble_rewards`` is called by ``booster_k1_dribble_env_cfg`` after the
approach rewards are inherited. Reward functions for this task live in this file
(or in ``dribble.py`` for ones that need the command's state).

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

from typing import TYPE_CHECKING

import torch

from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.tasks.velocity.mdp.approach import _yaw_angle, speed_limit_excess
from mjlab.tasks.velocity.mdp.dribble import _dribble, dribble_window_success
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


def _state(env: ManagerBasedRlEnv):
  cmd = _dribble(env)
  robot_xy = env.scene["robot"].data.root_link_pos_w[:, :2]
  ball = env.scene["ball"].data
  ball_xy = ball.root_link_pos_w[:, :2]
  v = ball.root_link_lin_vel_w[:, :2]
  d = torch.linalg.norm(ball_xy - robot_xy, dim=-1)
  return cmd, robot_xy, ball_xy, v, d


def _dist_gate(d: torch.Tensor) -> torch.Tensor:
  """g(d) = exp(-3 * max(0, d - 0.6)): flat 1 within 0.6 m."""
  return torch.exp(-GATE_DECAY * (d - GATE_FLAT_DIST).clamp(min=0.0))


def ball_progress(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Tent: clip(min(u, 2s - u) / max(s, 0.2), -1, 1) * g(d) while s > 0, else 0,
  with u = v . c_hat. Peaks at u = s; 0 at u = 0 and u = 2s."""
  cmd, _, _, v, d = _state(env)
  s = cmd.ball_cmd_speed
  along = torch.sum(v * cmd.ball_cmd_dir_w, dim=-1)
  tent = torch.minimum(along, 2.0 * s - along)
  prog = (tent / s.clamp(min=0.2)).clamp(-1.0, 1.0) * _dist_gate(d)
  return torch.where(s > 0.0, prog, torch.zeros_like(prog))


def ball_vel_cmd_tracking(env: ManagerBasedRlEnv) -> torch.Tensor:
  """exp(-||v - cmd||^2 / 0.25^2) * g(d); s > 0 and ||v|| > 0.05."""
  cmd, _, _, v, d = _state(env)
  s = cmd.ball_cmd_speed
  c = cmd.ball_cmd_dir_w * s.unsqueeze(-1)
  err_sq = torch.sum(torch.square(v - c), dim=-1)
  r = torch.exp(-err_sq / TRACK_SIGMA**2) * _dist_gate(d)
  gate = (s > 0.0) & (torch.linalg.norm(v, dim=-1) > MOVING_BALL_SPEED)
  return torch.where(gate, r, torch.zeros_like(r))


def ball_stop_tracking(env: ManagerBasedRlEnv) -> torch.Tensor:
  """exp(-4 ||v||) * exp(-2 max(0, d - 0.5)) while s == 0, else 0."""
  cmd, _, _, v, d = _state(env)
  r = torch.exp(-4.0 * torch.linalg.norm(v, dim=-1)) * torch.exp(
    -2.0 * (d - 0.5).clamp(min=0.0)
  )
  return torch.where(cmd.ball_cmd_speed == 0.0, r, torch.zeros_like(r))


def ball_proximity(env: ManagerBasedRlEnv) -> torch.Tensor:
  """exp(-5 max(0, d - 0.6))."""
  _, _, _, _, d = _state(env)
  return torch.exp(-5.0 * (d - 0.6).clamp(min=0.0))


def follow_ball_heading(env: ManagerBasedRlEnv) -> torch.Tensor:
  """exp(-5 (wz_des - wz)^2), wz_des = clip(5 * bearing_ball, -pi/4, pi/4) at all
  distances: turn to follow the ball, never to face the command first."""
  _, robot_xy, ball_xy, _, _ = _state(env)
  robot = env.scene["robot"].data
  yaw = _yaw_angle(robot.root_link_quat_w)
  to_ball = ball_xy - robot_xy
  b_ball = wrap_to_pi(torch.atan2(to_ball[:, 1], to_ball[:, 0]) - yaw)
  wz_des = (5.0 * b_ball).clamp(-torch.pi / 4, torch.pi / 4)
  wz = robot.root_link_ang_vel_w[:, 2]
  return torch.exp(-5.0 * torch.square(wz_des - wz))


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


APPROACH_MIN_DIST = 0.6
APPROACH_SPEED = 0.8


def approach_progress(env: ManagerBasedRlEnv) -> torch.Tensor:
  """clip(v_r . b_hat / 0.8, 0, 1) * 1[d > 0.6], v_r = robot root planar velocity
  (world), b_hat = unit robot-to-ball direction: walk toward a ball that is away."""
  _, robot_xy, ball_xy, _, d = _state(env)
  v_r = env.scene["robot"].data.root_link_lin_vel_w[:, :2]
  b_hat = (ball_xy - robot_xy) / (d.unsqueeze(-1) + 1.0e-3)
  r = (torch.sum(v_r * b_hat, dim=-1) / APPROACH_SPEED).clamp(0.0, 1.0)
  return torch.where(d > APPROACH_MIN_DIST, r, torch.zeros_like(r))


def termination_penalty(env: ManagerBasedRlEnv) -> torch.Tensor:
  """1 on the step an episode terminates for any reason other than a time-out
  (illegal_contact, fell_over, ball_lost, nan). The termination manager keeps
  time-out terms (time_out, out_of_terrain_bounds) in a separate truncation
  buffer, so ``terminated`` already excludes them; a step on which a real
  termination coincides with a time-out still counts. Terminations are computed
  before the rewards in the env step, so the flags refer to this step."""
  return env.termination_manager.terminated.float()


def dribble_speed_limit(env: ManagerBasedRlEnv) -> torch.Tensor:
  """approach_speed_limit with the vx limit replaced by max(vx_limit, s + 0.2)
  while s > 0 (s == 0 leaves it unchanged); vy and wz limits unchanged."""
  cmd = _dribble(env)
  robot = env.scene["robot"].data
  s = cmd.ball_cmd_speed
  limits = cmd.speed_limit.clone()
  vx_dribble = torch.maximum(limits[:, 0], s + DRIBBLE_VX_MARGIN)
  limits[:, 0] = torch.where(s > 0.0, vx_dribble, limits[:, 0])
  excess = speed_limit_excess(
    robot.root_link_lin_vel_b, robot.root_link_ang_vel_b[:, 2], limits
  )
  env.extras["log"]["Metrics/approach_speed_excess"] = excess.mean()
  return excess


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
  cfg.rewards["approach_view"].weight = 0.5
  cfg.rewards["upright"].weight = 2.0
  for name, func, weight in (
    ("dribble_window_success", dribble_window_success, 1.0),
    ("ball_progress", ball_progress, 3.0),
    ("ball_vel_cmd_tracking", ball_vel_cmd_tracking, 4.5),
    ("ball_stop_tracking", ball_stop_tracking, 1.5),
    ("ball_proximity", ball_proximity, 0.3),
    ("approach_progress", approach_progress, 1.0),
    ("follow_ball_heading", follow_ball_heading, 0.3),
    ("bad_touch", bad_touch, -1.0),
    ("redirect_bonus", redirect_bonus, 10.0),
    ("termination_penalty", termination_penalty, -100.0),
    ("approach_speed_limit", dribble_speed_limit, -10.0),
  ):
    cfg.rewards[name] = RewardTermCfg(func=func, weight=weight)

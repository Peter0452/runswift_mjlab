"""1v1 self-play on the stage-3 kick loop: striker against striker.

A second K1 (``opponent``) shares the field and the ball. Each episode has a
field of random size (9 x 6 up to 14 x 9 m) and heading around the spawned ball,
with 2.4 m goal mouths: the learner attacks ``target_w`` (an aim point on one
goal line, which the policy gets as its kick direction / range, as the
behaviour would hand it) and defends the other goal (``own_goal_w``, the
opponent's aim point); the opponent the reverse. The whole
ball over a goal line between the posts and under the bar is a goal; over any
other line it is out. Either ends the point and the side that did not cause
it restarts, as in a match: after a goal the side that conceded, after an out
the side that did not touch the ball last. A learner restart puts the ball
ahead of the learner, inside the field, and the opponent at the learner's spot
mirrored through the ball (both meet the ball from their own side). An
opponent restart puts the ball near where it went out (the centre after a
goal), clear of the learner, with the opponent behind it facing its attack,
as far from it as the learner. Both sides perceive alike (noise, dropout,
delay) and copies of the learner sample actions as it does.
The learner is never teleported; episodes end on falls or time out.

Both robots see each other as the robot's vision reports other robots: the
ground position (``position_projection``, x / y in the robot frame) of a robot
inside the head camera's view and range, plus a seen flag; zeros when unseen.
These three inputs follow the stage-3 actor's 83, so stage-3 checkpoints
warm-start with zero weights on them (the runner pads the first layer).

The opponent is not trained. ``OpponentPolicyAction`` runs frozen policies on
observations it builds from the sim in the actor's layout and adds no policy
actions. Each episode the opponent is either the learner's latest weights
(mirror) or a policy from a pool of seed checkpoints and snapshots, which the
self-play runner keeps up to date. 83-input policies get the first 83 inputs.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Literal, cast

import numpy as np
import torch
import torch.nn.functional as F

from k1.tasks.velocity.mdp import striker_skills as skills
from k1.tasks.velocity.mdp.amp_symmetry import augment_symmetries_kick_loop
from k1.tasks.velocity.mdp.approach import (
  NOMINAL_ROOT_HEIGHT,
  ApproachYawCommandCfg,
  _root_pose,
  _yaw_angle,
  ball_radius,
  camera_angles,
  in_camera_view,
  kick_direction_b,
  range_one_hot,
)
from k1.tasks.velocity.mdp.kick_loop import (
  HEAD_DEFAULT,
  HEAD_SCAN_PERIOD,
  HEAD_SCAN_YAW,
  HEAD_SEARCH_AFTER,
  HEAD_SEARCH_PITCH,
  HEAD_SEARCH_YAW,
  POST_KICK_WINDOW,
  SPEED_CAP_FINAL,
  WALK_SPEED_REF,
  KickLoopCommand,
  KickLoopCommandCfg,
  _found,
  goal_tolerance,
  head_goal,
  head_step,
)
from mjlab.entity import Entity
from mjlab.envs.mdp.actions import JointPositionAction, JointPositionActionCfg
from mjlab.managers.action_manager import ActionTerm, ActionTermCfg
from mjlab.utils.lab_api.math import (
  quat_apply,
  quat_apply_inverse,
  wrap_to_pi,
  yaw_quat,
)

if TYPE_CHECKING:
  from rsl_rl.env import VecEnv
  from tensordict import TensorDict

  from mjlab.envs import ManagerBasedRlEnv
  from mjlab.viewer.debug_visualizer import DebugVisualizer

_REPO = Path(__file__).resolve().parents[5]

# Seeds for the opponent pool (paths relative to the repo root work too).
SELFPLAY_KICK_CKPT = "logs/rsl_rl/k1_kick_stage3_amp/blends/h022_c2_x50.pt"
SELFPLAY_WALK_CKPT = (
  "logs/rsl_rl/k1_velocity_amp_symmetric_muon_wwcmu50_roughft/"
  "2026-09-21_20-34-24_stageA/model_9950.pt"
)

PolicyKind = Literal["kick", "walk", "controller"]
# Robot detection inputs appended to the stage-3 actor: x, y, seen.
DETECTION_DIM = 3
ACTOR_DIM = 83 + DETECTION_DIM
# Input sizes: the kick loop (stage 3, or with the opponent detection), the
# AMP walk (velocity command) and the two-level striker's controller.
OBS_DIM: dict[str, tuple[int, ...]] = {
  "kick": (83, ACTOR_DIM),
  "walk": (75,),
  "controller": (ACTOR_DIM + skills.SKILL_STATE_DIM,),
}
OUT_DIM: dict[str, int] = {
  "kick": 22,
  "walk": 22,
  "controller": skills.CONTROLLER_ACTION_DIM,
}
# EmpiricalNormalization's default eps in rsl_rl (not stored in checkpoints).
_NORM_EPS = 1.0e-2


def resolve_checkpoint(path: str) -> Path:
  """``path`` as given if it exists, else relative to the repo root."""
  p = Path(path).expanduser()
  if p.is_absolute() or p.exists():
    return p
  return _REPO / p


##
# Frozen policies.
##


@dataclass
class FrozenPolicy:
  """Deterministic actor (normalizer, optional one-layer GRU, ELU MLP) with
  weights detached from any optimizer, so the learner's updates never touch
  it. A recurrent policy's hidden state is the caller's (one row per env)."""

  kind: str
  name: str
  mean: torch.Tensor
  std: torch.Tensor
  layers: list[tuple[torch.Tensor, torch.Tensor]]
  gru: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor] | None = None
  """``weight_ih, weight_hh, bias_ih, bias_hh`` of rsl_rl's ``RNNModel``."""
  action_std: torch.Tensor | None = None
  """The actor's Gaussian action std (``[1, out]``), for sampled copies."""

  @property
  def in_dim(self) -> int:
    return (self.gru[0] if self.gru is not None else self.layers[0][0]).shape[1]

  @property
  def hidden_dim(self) -> int:
    """GRU state size (0: feed-forward)."""
    return 0 if self.gru is None else self.gru[1].shape[1]

  def step(
    self, obs: torch.Tensor, h: torch.Tensor | None = None
  ) -> tuple[torch.Tensor, torch.Tensor | None]:
    """Output and next hidden state. ``obs`` may carry more inputs than the
    policy takes (an 83-input stage-3 policy ignores the appended detection);
    ``h`` None starts a recurrent policy from zeros."""
    x = (obs[:, : self.in_dim] - self.mean) / self.std
    if self.gru is not None:
      w_ih, w_hh, b_ih, b_hh = self.gru
      if h is None:
        h = x.new_zeros(x.shape[0], self.hidden_dim)
      # torch.nn.GRU, gates ordered r, z, n.
      ir, iz, in_ = F.linear(x, w_ih, b_ih).chunk(3, dim=-1)
      hr, hz, hn = F.linear(h, w_hh, b_hh).chunk(3, dim=-1)
      r = torch.sigmoid(ir + hr)
      z = torch.sigmoid(iz + hz)
      n = torch.tanh(in_ + r * hn)
      h = (1.0 - z) * n + z * h
      x = h
    for i, (w, b) in enumerate(self.layers):
      x = F.linear(x, w, b)
      if i < len(self.layers) - 1:
        x = F.elu(x)
    return x, h

  def __call__(self, obs: torch.Tensor) -> torch.Tensor:
    return self.step(obs)[0]


def frozen_policy_from_state_dict(
  state_dict: dict[str, torch.Tensor], kind: str, name: str, device: str
) -> FrozenPolicy:
  """Copy an rsl_rl ``MLPModel`` or GRU ``RNNModel`` actor state dict into a
  ``FrozenPolicy``."""
  idx = sorted(
    int(k.split(".")[1])
    for k in state_dict
    if k.startswith("mlp.") and k.endswith(".weight")
  )
  if not idx:
    raise ValueError(f"{name}: no mlp.* weights in the actor state dict")

  def get(key: str) -> torch.Tensor:
    return state_dict[key].detach().to(device=device, dtype=torch.float32).clone()

  layers = [(get(f"mlp.{i}.weight"), get(f"mlp.{i}.bias")) for i in idx]
  gru = None
  if any(k.startswith("rnn.") for k in state_dict):
    if "rnn.rnn.weight_hh_l1" in state_dict or "rnn.rnn.weight_ih_l0" not in state_dict:
      raise ValueError(f"{name}: only one-layer GRU actors are supported")
    gru = (
      get("rnn.rnn.weight_ih_l0"),
      get("rnn.rnn.weight_hh_l0"),
      get("rnn.rnn.bias_ih_l0"),
      get("rnn.rnn.bias_hh_l0"),
    )
    if gru[1].shape[0] != 3 * gru[1].shape[1]:
      raise ValueError(f"{name}: recurrent actor is not a GRU (LSTM?)")
  in_dim = (gru[0] if gru is not None else layers[0][0]).shape[1]
  if in_dim not in OBS_DIM[kind]:
    raise ValueError(
      f"{name}: a '{kind}' opponent takes {OBS_DIM[kind]} inputs, got {in_dim}"
    )
  if "obs_normalizer._mean" in state_dict:
    mean = get("obs_normalizer._mean").reshape(1, -1)
    std = get("obs_normalizer._std").reshape(1, -1) + _NORM_EPS
  else:
    mean = torch.zeros(1, in_dim, device=device)
    std = torch.ones(1, in_dim, device=device)
  action_std = None
  if "distribution.std_param" in state_dict:
    action_std = get("distribution.std_param").reshape(1, -1).abs()
  elif "distribution.log_std_param" in state_dict:
    action_std = get("distribution.log_std_param").exp().reshape(1, -1)
  return FrozenPolicy(
    kind=kind,
    name=name,
    mean=mean,
    std=std,
    layers=layers,
    gru=gru,
    action_std=action_std,
  )


def zero_policy(kind: str, name: str, device: str) -> FrozenPolicy:
  """A policy that outputs zeros (a placeholder until the runner syncs)."""
  in_dim, out_dim = OBS_DIM[kind][-1], OUT_DIM[kind]
  return FrozenPolicy(
    kind=kind,
    name=name,
    mean=torch.zeros(1, in_dim, device=device),
    std=torch.ones(1, in_dim, device=device),
    layers=[
      (
        torch.zeros(out_dim, in_dim, device=device),
        torch.zeros(out_dim, device=device),
      )
    ],
  )


def load_frozen_policy(path: str, kind: str, device: str) -> FrozenPolicy:
  ckpt = resolve_checkpoint(path)
  if not ckpt.is_file():
    raise FileNotFoundError(
      f"Self-play opponent checkpoint not found: {ckpt}. Point the "
      "env.actions.opponent config at an existing file."
    )
  loaded = torch.load(ckpt, map_location=device, weights_only=False)
  return frozen_policy_from_state_dict(
    loaded["actor_state_dict"], kind, ckpt.stem, device
  )


def pad_input_columns(
  state_dict: dict[str, torch.Tensor], in_dim: int
) -> dict[str, torch.Tensor]:
  """Widen an MLP model's input to ``in_dim``: zero weights and an identity
  normalizer on the new inputs, so the model's output is unchanged."""
  w = state_dict["mlp.0.weight"]
  extra = in_dim - w.shape[1]
  if extra <= 0:
    return state_dict
  out = dict(state_dict)
  out["mlp.0.weight"] = torch.cat((w, w.new_zeros(w.shape[0], extra)), dim=1)
  for key, fill in (("_mean", 0.0), ("_var", 1.0), ("_std", 1.0)):
    k = f"obs_normalizer.{key}"
    if k in out:
      v = out[k]
      out[k] = torch.cat((v, v.new_full((*v.shape[:-1], extra), fill)), dim=-1)
  return out


def detect_robot(
  viewer: Entity,
  head_id: int,
  origin_xy: torch.Tensor,
  target: Entity,
  target_feet_ids: list[int],
  cam: ApproachYawCommandCfg,
  max_range: float,
  noise: tuple[float, float],
  dropout: float,
) -> tuple[torch.Tensor, torch.Tensor]:
  """Another robot as the vision reports it: ground position under its feet
  (``position_projection``) in the viewer's level frame, and a seen flag.

  Seen when its trunk is inside the head camera's view, within ``max_range``,
  and not dropped. Returns (detection, truth), each ``[N, 3]``: the detection
  is noisy and zero when unseen; the truth is always (x, y, 1).
  """
  quat = viewer.data.root_link_quat_w
  ground = target.data.body_link_pos_w[:, target_feet_ids, :2].mean(dim=1)
  rel = torch.zeros_like(target.data.root_link_pos_w)
  rel[:, :2] = ground - origin_xy
  true_b = quat_apply_inverse(yaw_quat(quat), rel)[:, :2]
  head_pos = viewer.data.body_link_pos_w[:, head_id]
  head_quat = viewer.data.body_link_quat_w[:, head_id]
  depth, az, el = camera_angles(
    quat_apply_inverse(head_quat, target.data.root_link_pos_w - head_pos),
    cam.camera_pitch,
  )
  dist = true_b.norm(dim=-1)
  seen = in_camera_view(depth, az, el, cam.fov_half_angle, cam.fov_vertical_half_angle)
  seen &= dist <= max_range
  if dropout > 0.0:
    seen &= torch.rand_like(dist) >= dropout
  base, slope = noise
  sigma = (base + slope * dist).unsqueeze(-1)
  noisy = true_b + sigma * torch.randn_like(true_b)
  flag = seen.float().unsqueeze(-1)
  detection = torch.cat((noisy * flag, flag), dim=-1)
  truth = torch.cat((true_b, torch.ones_like(flag)), dim=-1)
  return detection, truth


##
# Command: goals, kickoffs and point outcomes.
##


class SelfPlayKickCommand(KickLoopCommand):
  """Kick-loop command on a real field: two goal mouths, touchlines and
  kickoffs after each point, with an opponent."""

  cfg: SelfPlayKickCommandCfg  # pyright: ignore[reportIncompatibleVariableOverride]
  controller_decision: (
    tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor | None] | None
  ) = None
  """The learner's two-level decision (kick, direction, level, direct walk
  command or None), set by the controller wrapper; drawn by
  ``_debug_vis_impl``."""

  def __init__(self, cfg: SelfPlayKickCommandCfg, env: ManagerBasedRlEnv):
    # Set before super().__init__: the parent may place targets while building.
    self._freeze_target = False
    super().__init__(cfg, env)
    self.opponent: Entity = env.scene[cfg.opponent_name]
    feet, _ = self.opponent.find_bodies(
      ("left_foot_link", "right_foot_link"), preserve_order=True
    )
    self._opponent_feet_ids = list(feet)
    n, dev = self.num_envs, self.device
    # The learner's view of the opponent (actor) and the truth (critic).
    self.opponent_detection = torch.zeros(n, DETECTION_DIM, device=dev)
    self.opponent_true = torch.zeros(n, DETECTION_DIM, device=dev)
    # Field per episode: centre, unit axis towards the goal the learner
    # attacks (``target_w``), length, width and crossbar height.
    self.field_center = torch.zeros(n, 2, device=dev)
    self.field_axis = torch.zeros(n, 2, device=dev)
    self.field_axis[:, 0] = 1.0
    self.field_length = torch.full((n,), cfg.field_length_range[1], device=dev)
    self.field_width = torch.full((n,), cfg.field_width_range[1], device=dev)
    self.goal_height = torch.full((n,), cfg.goal_heights[1], device=dev)
    self.own_goal_w = torch.zeros(n, 2, device=dev)
    self.contest_scored = torch.zeros(n, dtype=torch.bool, device=dev)
    self.contest_conceded = torch.zeros(n, dtype=torch.bool, device=dev)
    self.ball_out = torch.zeros(n, dtype=torch.bool, device=dev)
    # Last robot to touch the ball this point: 1 learner, -1 opponent, 0 none.
    self.last_touch = torch.zeros(n, dtype=torch.long, device=dev)
    # +1 when the learner takes the ball, -1 when the opponent does.
    self.possession_change = torch.zeros(n, device=dev)
    # Ball race (``ball_race``): opponent's minus learner's time to the ball.
    self.race_phi = torch.zeros(n, device=dev)
    self.race_delta = torch.zeros(n, device=dev)
    # Set on kickoffs, cleared by the opponent action once it has re-read the
    # field (its ball memory, head and last action restart).
    self.kickoff_pending = torch.ones(n, dtype=torch.bool, device=dev)
    self._scored = torch.zeros(n, device=dev)
    self._conceded = torch.zeros(n, device=dev)
    self._outs = torch.zeros(n, device=dev)
    self._outs_by_learner = torch.zeros(n, device=dev)
    self._opponent_restarts = torch.zeros(n, device=dev)
    for name in (
      "contest_scored",
      "contest_conceded",
      "ball_out",
      "ball_out_by_learner",
      "opponent_restarts",
    ):
      self.metrics[name] = torch.zeros(n, device=dev)

  def _update_metrics(self) -> None:
    super()._update_metrics()
    self.metrics["contest_scored"][:] = self._scored
    self.metrics["contest_conceded"][:] = self._conceded
    self.metrics["ball_out"][:] = self._outs
    self.metrics["ball_out_by_learner"][:] = self._outs_by_learner
    self.metrics["opponent_restarts"][:] = self._opponent_restarts

  def _place_target(self, env_ids: torch.Tensor, ball_xy: torch.Tensor) -> None:
    # The target is the centre of the goal the learner attacks; the kick loop
    # would move it after a goal or a ball resting far away.
    if self._freeze_target:
      return
    super()._place_target(env_ids, ball_xy)

  def field_coords(
    self, xy: torch.Tensor, env_ids: torch.Tensor | None = None
  ) -> tuple[torch.Tensor, torch.Tensor]:
    """(along, across) of world points in the field frame: along points to
    the goal the learner attacks, across to its left."""
    ids = slice(None) if env_ids is None else env_ids
    rel = xy - self.field_center[ids]
    u = self.field_axis[ids]
    along = (rel * u).sum(dim=-1)
    across = u[:, 0] * rel[:, 1] - u[:, 1] * rel[:, 0]
    return along, across

  def _to_world(
    self, along: torch.Tensor, across: torch.Tensor, env_ids: torch.Tensor
  ) -> torch.Tensor:
    u = self.field_axis[env_ids]
    perp = torch.stack((-u[:, 1], u[:, 0]), dim=-1)
    return (
      self.field_center[env_ids] + u * along.unsqueeze(-1) + perp * across.unsqueeze(-1)
    )

  def _set_goals(self, env_ids: torch.Tensor, ball_xy: torch.Tensor) -> None:
    """Aim points on both goal lines: the centre, or (``aim_offset``) a lane
    across the mouth, as runswift's ``select_target`` hands the striker."""
    n, dev = len(env_ids), self.device
    half = 0.5 * self.field_length[env_ids].unsqueeze(-1)
    u = self.field_axis[env_ids]
    perp = torch.stack((-u[:, 1], u[:, 0]), dim=-1)
    span = self.cfg.aim_offset * self.cfg.goal_width
    lane = (torch.rand(n, 2, device=dev) * 2.0 - 1.0) * span
    center = self.field_center[env_ids]
    self.target_w[env_ids] = center + u * half + perp * lane[:, :1]
    self.own_goal_w[env_ids] = center - u * half + perp * lane[:, 1:]
    self.target_dist[env_ids] = (self.target_w[env_ids] - ball_xy).norm(dim=-1)
    self.goal_tol[env_ids] = goal_tolerance(self.target_dist[env_ids])

  def _resample_command(self, env_ids: torch.Tensor) -> None:
    super()._resample_command(env_ids)
    for buf in (self.contest_scored, self.contest_conceded, self.ball_out):
      buf[env_ids] = False
    for buf in (
      self._scored,
      self._conceded,
      self._outs,
      self._outs_by_learner,
      self._opponent_restarts,
    ):
      buf[env_ids] = 0.0
    self.last_touch[env_ids] = 0
    # The ball may come from a mid-kick reference state; read it from qpos.
    ball_xy = _root_pose(self.ball, env_ids)[:, :2]
    self._place_field(env_ids, ball_xy)
    self._set_goals(env_ids, ball_xy)
    self.place_opponent(env_ids, ball_xy)

  def _place_field(self, env_ids: torch.Tensor, ball_xy: torch.Tensor) -> None:
    """A field of random size and heading around the spawned ball, with the
    ball and the learner inside it."""
    n, dev, cfg = len(env_ids), self.device, self.cfg
    if n == 0:
      return
    lo, hi = cfg.field_length_range
    length = torch.empty(n, device=dev).uniform_(lo, hi)
    frac = (length - lo) / max(hi - lo, 1.0e-6)
    w_lo, w_hi = cfg.field_width_range
    width = w_lo + frac * (w_hi - w_lo)
    small, medium = cfg.goal_heights
    self.goal_height[env_ids] = torch.where(
      length < cfg.medium_field_min_length,
      torch.full_like(length, small),
      torch.full_like(length, medium),
    )
    k, m = 8, cfg.spawn_margin
    yaw = torch.rand(n, k, device=dev) * (2.0 * math.pi)
    # Kickoff-like starts: the learner on its own side, attacking roughly
    # along its line to the ball.
    to_ball = ball_xy - _root_pose(self.robot, env_ids)[:, :2]
    heading = torch.atan2(to_ball[:, 1], to_ball[:, 0]).unsqueeze(1)
    own_side = torch.rand(n, 1, device=dev) < cfg.own_side_start_prob
    near = heading + (torch.rand(n, k, device=dev) - 0.5) * (2.0 * math.pi / 3.0)
    yaw = torch.where(own_side, near, yaw)
    bx = (torch.rand(n, k, device=dev) - 0.5) * (length - 2 * m).unsqueeze(1)
    by = (torch.rand(n, k, device=dev) - 0.5) * (width - 2 * m).unsqueeze(1)
    c, s = yaw.cos(), yaw.sin()
    center = ball_xy.unsqueeze(1) - torch.stack(
      (c * bx - s * by, s * bx + c * by), dim=-1
    )
    rel = _root_pose(self.robot, env_ids)[:, :2].unsqueeze(1) - center
    rx = c * rel[..., 0] + s * rel[..., 1]
    ry = -s * rel[..., 0] + c * rel[..., 1]
    # Margin of the learner inside the field; keep the best candidate.
    inside = torch.minimum(
      0.5 * length.unsqueeze(1) - rx.abs(), 0.5 * width.unsqueeze(1) - ry.abs()
    )
    pick = inside.argmax(dim=1)
    rows = torch.arange(n, device=dev)
    self.field_center[env_ids] = center[rows, pick]
    self.field_axis[env_ids] = torch.stack((c[rows, pick], s[rows, pick]), dim=-1)
    self.field_length[env_ids] = length
    self.field_width[env_ids] = width

  def _update_command(self) -> None:
    goal_tol = self.goal_tol.clone()
    self._freeze_target = True
    try:
      super()._update_command()
    finally:
      self._freeze_target = False
    self.goal_tol[:] = goal_tol
    # Ties count as the learner's touch (an out from a scramble is not its
    # free ball).
    learner_touch = _found(self._env, self.cfg.feet_ball_sensor) | self.body_touch
    opponent_touch = _found(self._env, self.cfg.opponent_ball_sensor)
    prev_touch = self.last_touch.clone()
    self.last_touch[:] = torch.where(
      learner_touch, 1, torch.where(opponent_touch, -1, self.last_touch)
    )
    self.possession_change[:] = ((self.last_touch == 1) & (prev_touch != 1)).float() - (
      (self.last_touch == -1) & (prev_touch != -1)
    ).float()
    self._update_race()
    self.opponent_detection[:], self.opponent_true[:] = detect_robot(
      self.robot,
      self._head_id,
      self._ball_origin_w()[:, :2],
      self.opponent,
      self._opponent_feet_ids,
      self.cfg,
      self.cfg.opponent_max_range,
      self.cfg.opponent_obs_noise,
      self.cfg.opponent_dropout,
    )
    ball = self.ball.data.root_link_pos_w
    ids = torch.arange(self.num_envs, device=self.device)
    r = ball_radius(self._env, ids)
    along, across = self.field_coords(ball[:, :2])
    height = ball[:, 2] - self._env.scene.env_origins[:, 2]
    # A goal: the whole ball over the goal line, between the posts, under the
    # bar. Over any other line: out.
    half_l = 0.5 * self.field_length
    mouth = (across.abs() < 0.5 * self.cfg.goal_width) & (height < self.goal_height)
    scored = (along > half_l + r) & mouth
    conceded = (along < -half_l - r) & mouth
    out = ~(scored | conceded) & (
      (along.abs() > half_l + r) | (across.abs() > 0.5 * self.field_width + r)
    )
    self.contest_scored[:] = scored
    self.contest_conceded[:] = conceded
    self.ball_out[:] = out
    self._scored += scored.float()
    self._conceded += conceded.float()
    self._outs += out.float()
    # Out off nobody (a rolling kickoff ball) counts as the learner's.
    learner_out = out & (self.last_touch >= 0)
    self._outs_by_learner += learner_out.float()
    restart = scored | conceded | out
    if not bool(restart.any()):
      return
    to_opponent = (scored | learner_out) & self.cfg.opponent_restarts
    self._opponent_restarts += to_opponent.float()
    ids = to_opponent.nonzero(as_tuple=False).squeeze(-1)
    # Restart near where the ball went out; the centre after a goal.
    anchor = torch.where(
      scored[ids].unsqueeze(-1), self.field_center[ids], ball[ids, :2]
    ).clone()
    ours = restart & ~to_opponent
    if bool(ours.any()):
      self._kickoff(ours.nonzero(as_tuple=False).squeeze(-1))
    if len(ids) > 0:
      self._opponent_kickoff(ids, anchor)

  def _kickoff(self, env_ids: torch.Tensor) -> None:
    """New point on the same field: ball ahead of the learner as at spawn,
    kept inside the field, and the opponent at the mirrored spot."""
    self._freeze_target = True
    try:
      self._spawn_ball_and_target(env_ids)
    finally:
      self._freeze_target = False
    ball_xy = _root_pose(self.ball, env_ids)[:, :2]
    along, across = self.field_coords(ball_xy, env_ids)
    m = self.cfg.spawn_margin
    half_l = 0.5 * self.field_length[env_ids] - m
    half_w = 0.5 * self.field_width[env_ids] - m
    inside = self._to_world(
      torch.maximum(torch.minimum(along, half_l), -half_l),
      torch.maximum(torch.minimum(across, half_w), -half_w),
      env_ids,
    )
    learner = _root_pose(self.robot, env_ids)[:, :2]
    # Not under the learner's feet: then the centre spot.
    crowded = (inside - learner).norm(dim=-1) < 0.5
    inside = torch.where(crowded.unsqueeze(-1), self.field_center[env_ids], inside)
    moved = (inside - ball_xy).norm(dim=-1) > 1.0e-4
    if bool(moved.any()):
      self._move_ball(env_ids[moved], inside[moved])
      ball_xy = inside
    self._new_point(env_ids, ball_xy)
    self.place_opponent(env_ids, ball_xy)

  def _new_point(self, env_ids: torch.Tensor, ball_xy: torch.Tensor) -> None:
    self._set_goals(env_ids, ball_xy)
    for buf in (
      self.kicked_since_target,
      self.lined_up_latched,
      self.rest_pending,
      self.near_pending,
    ):
      buf[env_ids] = False
    self.last_touch[env_ids] = 0

  def _opponent_kickoff(self, env_ids: torch.Tensor, anchor: torch.Tensor) -> None:
    """New point for the opponent: the ball near ``anchor``, inside the
    field and at least ``restart_learner_distance`` from the learner (the
    learner is never teleported), the opponent behind it facing the goal it
    attacks, as far from the ball as the learner (as a learner restart puts
    them), clear of the learner. Of the candidates that qualify, the one
    nearest the anchor; else the one farthest from the learner."""
    n, dev, cfg = len(env_ids), self.device, self.cfg
    k = 32
    m = cfg.spawn_margin
    half_l = (0.5 * self.field_length[env_ids] - m).unsqueeze(1)
    half_w = (0.5 * self.field_width[env_ids] - m).unsqueeze(1)
    a_along, a_across = self.field_coords(anchor, env_ids)
    # Half the candidates around the anchor, half anywhere on the field.
    r = cfg.restart_search_radius
    local_along = (
      a_along.unsqueeze(1) + (torch.rand(n, k // 2, device=dev) - 0.5) * 2 * r
    )
    local_across = (
      a_across.unsqueeze(1) + (torch.rand(n, k // 2, device=dev) - 0.5) * 2 * r
    )
    any_along = (torch.rand(n, k - k // 2, device=dev) - 0.5) * 2 * half_l
    any_across = (torch.rand(n, k - k // 2, device=dev) - 0.5) * 2 * half_w
    along = torch.cat((local_along, any_along), 1)
    across = torch.cat((local_across, any_across), 1)
    along = torch.maximum(torch.minimum(along, half_l), -half_l)
    across = torch.maximum(torch.minimum(across, half_w), -half_w)
    rows = env_ids.repeat_interleave(k)
    ball = self._to_world(along.reshape(-1), across.reshape(-1), rows).reshape(n, k, 2)
    learner = _root_pose(self.robot, env_ids)[:, :2].unsqueeze(1)
    ball_gap = (ball - learner).norm(dim=-1)
    # The opponent attacks -axis: it stands on the +axis side of the ball,
    # as far from it as the learner (jittered as in place_opponent).
    jitter = torch.empty(n, k, device=dev).uniform_(0.8, 1.2)
    d = (ball_gap * jitter).clamp(*cfg.opponent_distance_range)
    ang = torch.empty(n, k, device=dev).uniform_(
      -cfg.opponent_spawn_half_angle, cfg.opponent_spawn_half_angle
    )
    u = self.field_axis[env_ids].unsqueeze(1)
    c, s = ang.cos(), ang.sin()
    back = torch.stack(
      (c * u[..., 0] - s * u[..., 1], s * u[..., 0] + c * u[..., 1]), -1
    )
    opp = ball + back * d.unsqueeze(-1)
    opp_gap = (opp - learner).norm(dim=-1)
    o_along, o_across = self.field_coords(opp.reshape(-1, 2), rows)
    on_field = (
      (o_along.abs() < 0.5 * self.field_length[rows])
      & (o_across.abs() < 0.5 * self.field_width[rows])
    ).reshape(n, k)
    ok = (
      (ball_gap >= cfg.restart_learner_distance)
      & (opp_gap >= cfg.opponent_clearance)
      & on_field
    )
    near = (ball - anchor.unsqueeze(1)).norm(dim=-1)
    score = torch.where(ok, 1.0e3 - near, ball_gap)
    pick = score.argmax(dim=1)
    idx = torch.arange(n, device=dev)
    ball_xy, opp_xy = ball[idx, pick], opp[idx, pick]
    self._move_ball(env_ids, ball_xy)
    self._new_point(env_ids, ball_xy)
    yaw = self._mirrored_yaw(env_ids, ball_xy, opp_xy)
    place_upright(self.opponent, env_ids, opp_xy, yaw, self._env.scene.env_origins)
    self.kickoff_pending[env_ids] = True

  def _mirrored_yaw(
    self, env_ids: torch.Tensor, ball_xy: torch.Tensor, opp_xy: torch.Tensor
  ) -> torch.Tensor:
    """Opponent heading that puts the ball at the bearing the learner has it
    (ahead after a learner restart, anywhere after it shot or kicked out),
    jittered by ``opponent_yaw_noise``."""
    pose = _root_pose(self.robot, env_ids)
    to_ball = ball_xy - pose[:, :2]
    bearing = wrap_to_pi(
      torch.atan2(to_ball[:, 1], to_ball[:, 0]) - _yaw_angle(pose[:, 3:7])
    )
    face = ball_xy - opp_xy
    jitter = torch.empty(len(env_ids), device=self.device).uniform_(
      -self.cfg.opponent_yaw_noise, self.cfg.opponent_yaw_noise
    )
    return torch.atan2(face[:, 1], face[:, 0]) - bearing + jitter

  def _move_ball(self, env_ids: torch.Tensor, xy: torch.Tensor) -> None:
    """Put a resting ball at ``xy`` where the learner just saw it."""
    pose = _root_pose(self.ball, env_ids)
    state = self.ball.data.default_root_state[env_ids].clone()
    state[:, 0:2] = xy
    state[:, 2] = pose[:, 2]
    state[:, 3:7] = torch.tensor([1.0, 0.0, 0.0, 0.0], device=self.device)
    state[:, 7:] = 0.0
    self.ball.write_root_state_to_sim(state, env_ids)
    robot = _root_pose(self.robot, env_ids)
    rel = torch.zeros(len(env_ids), 3, device=self.device)
    rel[:, :2] = xy - robot[:, :2]
    self.last_seen_ball_w[env_ids] = xy
    self.last_seen_ball_b[env_ids] = quat_apply_inverse(yaw_quat(robot[:, 3:7]), rel)[
      :, :2
    ]
    self.time_since_seen[env_ids] = 0.0
    self.ball_lost[env_ids] = False

  def place_opponent(self, env_ids: torch.Tensor, ball_xy: torch.Tensor) -> None:
    """Opponent at the learner's spot mirrored through the ball, so both meet
    the ball from the same side of their own attack, facing it; jittered, on
    the field and clear of the learner."""
    n = len(env_ids)
    if n == 0:
      return
    dev = self.device
    learner_xy = _root_pose(self.robot, env_ids)[:, :2]
    mirror = ball_xy - learner_xy
    dist = mirror.norm(dim=-1).clamp(min=0.6)
    base = torch.atan2(mirror[:, 1], mirror[:, 0])
    # A few jittered candidates; keep the first on the field and clear of the
    # learner, else the farthest from the learner.
    k = 6
    half = self.cfg.opponent_spawn_half_angle
    ang = base.unsqueeze(1) + torch.empty(n, k, device=dev).uniform_(-half, half)
    jitter = torch.empty(n, k, device=dev).uniform_(0.8, 1.2)
    rad = (dist.unsqueeze(1) * jitter).clamp(*self.cfg.opponent_distance_range)
    cand = ball_xy.unsqueeze(1) + torch.stack(
      (ang.cos(), ang.sin()), -1
    ) * rad.unsqueeze(-1)
    clear = (cand - learner_xy.unsqueeze(1)).norm(dim=-1)
    along, across = self.field_coords(cand.reshape(-1, 2), env_ids.repeat_interleave(k))
    on_field = (along.abs() < 0.5 * self.field_length[env_ids].repeat_interleave(k)) & (
      across.abs() < 0.5 * self.field_width[env_ids].repeat_interleave(k)
    )
    ok = (clear >= self.cfg.opponent_clearance) & on_field.reshape(n, k)
    score = torch.where(ok, 1.0e3 - torch.arange(k, device=dev).float(), clear)
    pick = score.argmax(dim=1)
    rows = torch.arange(n, device=dev)
    xy = cand[rows, pick]
    yaw = self._mirrored_yaw(env_ids, ball_xy, xy)
    place_upright(self.opponent, env_ids, xy, yaw, self._env.scene.env_origins)
    self.kickoff_pending[env_ids] = True

  def _update_race(self) -> None:
    """Ball-race potential and its change this step (see ``ball_race``)."""
    opp = self._env.action_manager.get_term("opponent")
    assert isinstance(opp, OpponentPolicyAction)
    ball = self.ball.data.root_link_pos_w[:, :2]
    mine = race_time(self.robot, ball, self.speed_limit)
    theirs = race_time(self.opponent, ball, opp.speed_limit)
    phi = (theirs - mine).clamp(-RACE_CLIP_S, RACE_CLIP_S)
    delta = phi - self.race_phi
    # Teleports (kickoffs, resets, a fallen opponent stood up) are not play.
    self.race_delta[:] = torch.where(delta.abs() > RACE_JUMP_S, 0.0, delta)
    self.race_phi[:] = phi

  def _debug_vis_impl(self, visualizer: DebugVisualizer) -> None:
    """Touchlines, goal lines and goals, on top of the kick-loop drawing."""
    super()._debug_vis_impl(visualizer)
    env_ids = list(visualizer.get_env_indices(self.num_envs))
    if not env_ids:
      return
    ids = torch.tensor(env_ids, device=self.device)
    ground = self._env.scene.env_origins[ids, 2].cpu().numpy() + 0.01
    hl = 0.5 * self.field_length[ids]
    hw = 0.5 * self.field_width[ids]
    hg = torch.full_like(hl, 0.5 * self.cfg.goal_width)
    corners = [
      self._to_world(a, b, ids).cpu().numpy()
      for a, b in ((hl, hw), (hl, -hw), (-hl, -hw), (-hl, hw))
    ]
    posts = [
      self._to_world(a, b, ids).cpu().numpy()
      for a, b in ((hl, hg), (hl, -hg), (-hl, -hg), (-hl, hg))
    ]
    height = self.goal_height[ids].cpu().numpy()
    white, goal_color = (0.95, 0.95, 0.95, 0.9), (1.0, 0.85, 0.1, 0.95)
    for k in range(len(env_ids)):
      z = ground[k]
      for i in range(4):
        a, b = corners[i][k], corners[(i + 1) % 4][k]
        visualizer.add_cylinder(
          np.array([a[0], a[1], z]), np.array([b[0], b[1], z]), 0.02, white
        )
      for a, b in ((posts[0][k], posts[1][k]), (posts[2][k], posts[3][k])):
        top = z + height[k]
        for p in (a, b):
          visualizer.add_cylinder(
            np.array([p[0], p[1], z]), np.array([p[0], p[1], top]), 0.05, goal_color
          )
        visualizer.add_cylinder(
          np.array([a[0], a[1], top]), np.array([b[0], b[1], top]), 0.05, goal_color
        )
    self._draw_controllers(visualizer, env_ids)

  def _draw_controllers(self, visualizer: DebugVisualizer, env_ids: list[int]) -> None:
    """Two-level strikers' decisions (see ``CONTROLLER_VIS_LEGEND``)."""
    opp = self._env.action_manager.get_term("opponent")
    assert isinstance(opp, OpponentPolicyAction)
    memory = opp.cfg.controller_ball_memory
    rows = []
    if self.controller_decision is not None:
      kick, theta, level, walk_cmd = self.controller_decision
      ball = _controller_ball_view(
        self.masked_ball_b,
        self.ball_lost | self.never_seen,
        self.memory_disproved | self.never_seen,
        self.memory_ball_b,
        self.time_since_seen == 0.0,
        memory,
      )
      rows.append((self.robot, kick, theta, level, ball, None, walk_cmd))
    kinds = [getattr(p, "kind", "") for p in opp.slots]
    is_ctrl = torch.tensor([kinds[i] == "controller" for i in opp.slot.tolist()])
    if bool(is_ctrl.any()):
      opp_ball = _controller_ball_view(
        opp.memory_ball_b,
        opp.ball_lost,
        opp.memory_disproved,
        opp.memory_ball_b,
        opp.time_unseen == 0.0,
        memory,
      )
      walk = torch.where(
        opp.ctrl_walk_direct.unsqueeze(-1),
        opp.ctrl_walk,
        skills.walk_command(opp.ctrl_theta, opp.ctrl_level),
      )
      rows.append(
        (
          self.opponent,
          opp.ctrl_kick,
          opp.ctrl_theta,
          opp.ctrl_level,
          opp_ball,
          is_ctrl,
          walk,
        )
      )
    for entity, kick, theta, level, (ball_b, state), mask, walk_cmd in rows:
      if walk_cmd is None:
        walk_cmd = skills.walk_command(theta, level)
      walk_np = walk_cmd.cpu().numpy()
      pos = entity.data.root_link_pos_w.cpu().numpy()
      yaw = _yaw_angle(entity.data.root_link_quat_w).cpu().numpy()
      kick_np, theta_np = kick.cpu().numpy(), theta.cpu().numpy()
      ball_np, state_np = ball_b.cpu().numpy(), state
      rng = skills.range_from_level(level).argmax(-1).cpu().numpy()
      for k in env_ids:
        if mask is not None and not bool(mask[k]):
          continue
        p, c, s_ = pos[k], math.cos(yaw[k]), math.sin(yaw[k])
        top = p + np.array([0.0, 0.0, 0.62])
        if kick_np[k]:
          color, length = _VIS_KICK_RANGE[rng[k]], 0.6 * (rng[k] + 1)
          a = yaw[k] + theta_np[k]
        else:
          vx, vy = walk_np[k, 0], walk_np[k, 1]
          color, length = _VIS_WALK, 0.3 + math.hypot(vx, vy)
          a = yaw[k] + math.atan2(vy, vx)
        visualizer.add_sphere(top, 0.09, color, label="skill")
        start = np.array([p[0], p[1], 0.05])
        end = start + length * np.array([math.cos(a), math.sin(a), 0.0])
        visualizer.add_arrow(start, end, color, width=0.03, label="command")
        st = int(state_np[k])
        if st == _BALL_DISPROVED:
          visualizer.add_sphere(
            top + np.array([0.0, 0.0, 0.2]), 0.06, _VIS_BALL[st], label="search"
          )
          continue
        bx, by = ball_np[k]
        w = np.array([p[0] + c * bx - s_ * by, p[1] + s_ * bx + c * by, 0.12])
        visualizer.add_sphere(w, 0.07, _VIS_BALL[st], label="ball belief")


# Debug drawing of two-level strikers in play (the learner and controller
# opponents alike).
CONTROLLER_VIS_LEGEND = (
  "sphere over the head: skill (blue walk; yellow / orange / red kick short /"
  " medium / long); ground arrow: commanded direction (length: walk speed or"
  " kick range); ball belief: green seen, yellow remembered, magenta the"
  " kick skill's lost-ball turn cue (controller without its own view); red"
  " sphere over the skill sphere: memory disproved, searching"
)
_VIS_WALK = (0.2, 0.5, 1.0, 0.9)
_VIS_KICK_RANGE = (
  (1.0, 0.9, 0.1, 0.9),
  (1.0, 0.55, 0.05, 0.9),
  (0.9, 0.1, 0.05, 0.9),
)
_BALL_SEEN, _BALL_MEMORY, _BALL_CUE, _BALL_DISPROVED = 0, 1, 2, 3
_VIS_BALL = (
  (0.1, 0.9, 0.2, 0.9),
  (1.0, 0.9, 0.1, 0.9),
  (0.9, 0.2, 0.9, 0.9),
  (1.0, 0.1, 0.1, 0.95),
)


def _controller_ball_view(
  cue_b: torch.Tensor,
  lost: torch.Tensor,
  disproved: torch.Tensor,
  memory_b: torch.Tensor,
  seen: torch.Tensor,
  controller_memory: bool,
) -> tuple[torch.Tensor, np.ndarray]:
  """Where a controller believes the ball is (trunk frame) and why."""
  state = torch.where(seen, _BALL_SEEN, _BALL_MEMORY)
  if controller_memory:
    state = torch.where(lost & disproved, _BALL_DISPROVED, state)
    ball = torch.where(lost.unsqueeze(-1), memory_b, cue_b)
  else:
    state = torch.where(lost, _BALL_CUE, state)
    ball = cue_b
  return ball, state.cpu().numpy()


def place_upright(
  entity: Entity,
  env_ids: torch.Tensor,
  xy: torch.Tensor,
  yaw: torch.Tensor,
  env_origins: torch.Tensor,
) -> None:
  """Write a standing robot at ``xy`` with heading ``yaw``, default joints."""
  state = entity.data.default_root_state[env_ids].clone()
  state[:, 0:2] = xy
  state[:, 2] = env_origins[env_ids, 2] + NOMINAL_ROOT_HEIGHT
  half = 0.5 * yaw
  state[:, 3:7] = torch.stack(
    (half.cos(), torch.zeros_like(half), torch.zeros_like(half), half.sin()), -1
  )
  state[:, 7:] = 0.0
  entity.write_root_state_to_sim(state, env_ids=env_ids)
  default_pos = entity.data.default_joint_pos
  default_vel = entity.data.default_joint_vel
  assert default_pos is not None and default_vel is not None
  entity.write_joint_state_to_sim(
    default_pos[env_ids].clone(), default_vel[env_ids].clone(), env_ids=env_ids
  )


@dataclass(kw_only=True)
class SelfPlayKickCommandCfg(KickLoopCommandCfg):
  """Kick-loop command for 1v1 self-play."""

  opponent_name: str = "opponent"
  field_length_range: tuple[float, float] = (9.0, 14.0)
  """Touchline length per episode (m), small to large field."""
  field_width_range: tuple[float, float] = (6.0, 9.0)
  """Goal-line width (m), scaled with the length (9 x 6 up to 14 x 9)."""
  goal_width: float = 2.4
  """Between the posts (m)."""
  goal_heights: tuple[float, float] = (1.6, 1.8)
  """Crossbar height on small / medium fields (m)."""
  medium_field_min_length: float = 11.5
  """Fields at least this long use the medium goal (m)."""
  aim_offset: float = 0.0
  """Aim points spread across each goal mouth by up to this share of its
  width (0: centre). Lanes keep a kick skill responsive to the aim."""
  spawn_margin: float = 0.5
  """Kickoff balls stay this far inside the lines (m)."""
  own_side_start_prob: float = 0.5
  """Share of episodes whose field puts the learner on its own side of the
  ball (attacking within 60 degrees of its line to the ball)."""
  opponent_distance_range: tuple[float, float] = (0.8, 5.0)
  """Limits of the opponent's distance from the ball at kickoff (m)."""
  opponent_spawn_half_angle: float = 0.4
  """Jitter of the opponent's mirrored spot around the ball (rad)."""
  opponent_yaw_noise: float = 0.1
  """Jitter of the opponent's heading around the learner's bearing to the
  ball (rad)."""
  opponent_clearance: float = 1.0
  """Minimum learner-opponent distance at kickoff (m), when achievable."""
  opponent_max_range: float = 6.0
  """Farthest robot detection (m); match the robot detector."""
  opponent_obs_noise: tuple[float, float] = (0.05, 0.05)
  """Detection noise: sigma = base + rel * distance (m, per axis)."""
  opponent_dropout: float = 0.05
  """Probability per step that a robot in view is not detected."""
  opponent_ball_sensor: str = "opponent_ball_contact"
  """Opponent-ball contact (any body), for who touched the ball last."""
  opponent_restarts: bool = True
  """The opponent restarts after the learner scores or puts the ball out
  (False: every point restarts with the learner's ball)."""
  restart_search_radius: float = 1.5
  """Opponent restart balls are sought within this of the anchor (m)."""
  restart_learner_distance: float = 1.0
  """Opponent restart balls are at least this far from the learner (m), the
  near end of the learner's own spawn distance."""

  def build(self, env: ManagerBasedRlEnv) -> SelfPlayKickCommand:
    return SelfPlayKickCommand(self, env)


def _selfplay_command(
  env: ManagerBasedRlEnv, name: str = "twist"
) -> SelfPlayKickCommand:
  cmd = env.command_manager.get_term(name)
  assert isinstance(cmd, SelfPlayKickCommand)
  return cmd


# Rewards. Point outcomes are set at the end of a step and paid by the next.


def opponent_detection(
  env: ManagerBasedRlEnv, privileged: bool = False
) -> torch.Tensor:
  """Opponent as the vision reports it: x, y (robot frame, m) and seen; zeros
  while unseen. ``privileged`` gives the true position, always seen."""
  cmd = _selfplay_command(env)
  return cmd.opponent_true if privileged else cmd.opponent_detection


def augment_symmetries_selfplay(
  env: VecEnv, obs: TensorDict | None, actions: torch.Tensor | None
) -> tuple[TensorDict | None, torch.Tensor | None]:
  """Kick-loop mirror plus the trailing detection (x, y, seen): y flips."""
  if obs is None:
    return augment_symmetries_kick_loop(env, obs, actions)
  k = DETECTION_DIM
  groups = ("actor", "critic")
  full = {g: cast(torch.Tensor, obs[g]) for g in groups}
  base = obs.clone()
  for g in groups:
    base[g] = full[g][:, :-k]
  base, actions = augment_symmetries_kick_loop(env, base, actions)
  assert base is not None
  sign = torch.tensor([1.0, -1.0, 1.0], device=full["actor"].device)
  for g in groups:
    tail = full[g][:, -k:]
    mirrored = cast(torch.Tensor, base[g])
    base[g] = torch.cat((mirrored, torch.cat((tail, tail * sign), dim=0)), dim=-1)
  return base, actions


def dribble_progress(
  env: ManagerBasedRlEnv, possession_distance: float = 0.6, max_speed: float = 1.5
) -> torch.Tensor:
  """Ball speed towards the attacked goal (m/s, capped) while the learner has
  it: within ``possession_distance`` of its feet and closer than the opponent.
  Carrying the ball past the opponent pays, not only striking it."""
  cmd = _selfplay_command(env)
  ball = cmd.ball.data.root_link_pos_w[:, :2]
  vel = cmd.ball.data.root_link_lin_vel_w[:, :2]
  to_goal = cmd.target_w - ball
  u = to_goal / to_goal.norm(dim=-1, keepdim=True).clamp(min=1.0e-6)
  toward = (vel * u).sum(dim=-1).clamp(0.0, max_speed)
  mine = cmd.robot.data.body_link_pos_w[:, cmd._feet_ids, :2].mean(dim=1)
  theirs = cmd.opponent.data.body_link_pos_w[:, cmd._opponent_feet_ids, :2].mean(dim=1)
  d_mine = (ball - mine).norm(dim=-1)
  possess = (d_mine < possession_distance) & (d_mine < (ball - theirs).norm(dim=-1))
  return toward * possess.float()


def walk_engage(env: ManagerBasedRlEnv, min_dist: float = 0.6) -> torch.Tensor:
  """Speed at which the learner closes the gap to the ball by its own motion,
  clipped to the vx cap, over min(cap, 1 m/s) as ``walk_speed``; down to
  ``min_dist``.

  Replaces stage 3's ``walk_speed`` in self-play. That term paid the robot's
  speed toward the ball beyond 1.5 m, so following a ball the opponent carries
  away paid as much as reaching it, and the last 1.5 m paid nothing: v8 moved
  its time from < 0.6 m (21 % -> 14 %) to 1.5-3 m (28 % -> 34 %) and its goal
  share vs h022 fell 0.39 -> 0.19. Here a ball moving away is subtracted, a
  ball rolling in is not credited, and stepping back still costs.
  """
  cmd = _selfplay_command(env)
  ball = cmd.ball.data.root_link_pos_w[:, :2]
  me = cmd.robot.data.root_link_pos_w[:, :2]
  gap = ball - me
  dist = gap.norm(dim=-1)
  u = gap / dist.unsqueeze(-1).clamp(min=1.0e-6)
  v_robot = (cmd.robot.data.root_link_lin_vel_w[:, :2] * u).sum(dim=-1)
  v_ball = (cmd.ball.data.root_link_lin_vel_w[:, :2] * u).sum(dim=-1)
  engage = torch.minimum(v_robot, v_robot - v_ball)
  cap = cmd.speed_limit[:, 0]
  score = engage.clamp(min=-cap, max=cap) / cap.clamp(max=WALK_SPEED_REF)
  active = (dist > min_dist) & (cmd.time_since_kick >= POST_KICK_WINDOW)
  active &= ~cmd.ball_lost
  return torch.where(active, score, torch.zeros_like(score))


def possession_change(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per event: +1 when the learner takes the ball (touches it and was not
  the last to), -1 when the opponent does. Zero-sum; own repeated touches
  (a dribble) pay nothing, so it cannot be farmed.

  Goals reach the decision to commit to a ball only faintly (gamma 0.995 is
  a ~4 s horizon; race -> kick -> goal takes 5-10 s), and tripling them
  (v11) gave a small, short-lived gain. Winning the ball is a quick,
  frequent signal of the same thing.
  """
  return _selfplay_command(env).possession_change


RACE_CLIP_S = 2.0
"""Ball-race advantage is capped at this many seconds either way."""
RACE_JUMP_S = 0.25
"""A one-step change beyond this is a teleport, not play (play moves the
potential by about 0.05 s per step at most)."""


def race_time(
  robot: Entity, ball_xy: torch.Tensor, speed_limit: torch.Tensor
) -> torch.Tensor:
  """Rough time for ``robot`` to reach the ball: distance at its forward speed
  cap plus the turn to face the ball at its turn-rate cap (s)."""
  rel = ball_xy - robot.data.root_link_pos_w[:, :2]
  heading = _yaw_angle(robot.data.root_link_quat_w)
  bearing = wrap_to_pi(torch.atan2(rel[:, 1], rel[:, 0]) - heading)
  run = rel.norm(dim=-1) / speed_limit[:, 0].clamp(min=0.2)
  return run + bearing.abs() / speed_limit[:, 2].clamp(min=0.3)


def ball_race(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Change of the ball-race advantage per second: the opponent's estimated
  time to the ball minus the learner's (``race_time``), capped at
  ``RACE_CLIP_S``. Potential-based (it sums to the change between any two
  states, so loops pay nothing) and zero-sum (the sides' times swap).

  Pays for whatever makes the learner first to the ball: closing on it,
  turning to it, standing goal-side, kicking it where the opponent is not.
  Standing still while the opponent closes costs.
  """
  return _selfplay_command(env).race_delta / env.step_dt


def territory_progress(env: ManagerBasedRlEnv, max_speed: float = 3.0) -> torch.Tensor:
  """Ball velocity along the field axis, own goal -> attacked goal (m/s),
  clipped to ``max_speed`` either way and paid only while the ball is inside
  the field.

  Summed over time this is the ball's net progress up the field: a dense,
  zero-sum game signal (the opponent's progress is the learner's loss, and
  shuffling the ball back and forth nets nothing). Unlike the kick and dribble
  shaping it is not annealed, so the attack keeps a signal between goals. A
  ball rolling out (a long hoof over the line) stops paying at the line.
  """
  cmd = _selfplay_command(env)
  ball = cmd.ball.data.root_link_pos_w[:, :2]
  vel = cmd.ball.data.root_link_lin_vel_w[:, :2]
  u = cmd.field_axis
  perp = torch.stack((-u[:, 1], u[:, 0]), dim=-1)
  rel = ball - cmd.field_center
  inside = ((rel * u).sum(dim=-1).abs() <= 0.5 * cmd.field_length) & (
    (rel * perp).sum(dim=-1).abs() <= 0.5 * cmd.field_width
  )
  toward = (vel * u).sum(dim=-1).clamp(-max_speed, max_speed)
  return toward * inside.float()


def contest_score(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per goal scored: the whole ball over the line between the posts."""
  return _selfplay_command(env).contest_scored.float()


def contest_concede(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per goal conceded into the goal the learner defends."""
  return _selfplay_command(env).contest_conceded.float()


##
# Opponent action: frozen policies driving the second robot.
##


@dataclass(frozen=True)
class OpponentSeedCfg:
  """A fixed member of the opponent pool."""

  checkpoint: str
  kind: PolicyKind = "kick"
  """"kick": stage-3 actor (83 inputs). "walk": AMP walk (75 inputs) driven
  by a scripted velocity command that dribbles the ball to its goal."""
  weight: float = 1.0
  """Sampling weight within the pool (snapshots use ``snapshot_weight``)."""


class OpponentPolicyAction(ActionTerm):
  """Drives the opponent with frozen policies; takes no policy actions.

  Slot 0 is the learner's latest weights (mirror), then the seeds, then the
  runner's snapshots. Each episode the opponent uses slot 0 with probability
  ``latest_prob``, else a pool slot by weight.
  """

  cfg: OpponentPolicyActionCfg
  _entity: Entity

  def __init__(self, cfg: OpponentPolicyActionCfg, env: ManagerBasedRlEnv):
    super().__init__(cfg, env)
    self._joint = JointPositionAction(cfg.joint_action, env)
    self.ball: Entity = env.scene[cfg.ball_name]
    cmd = env.command_manager.get_term(cfg.command_name)
    assert isinstance(cmd, SelfPlayKickCommand)
    self._cmd = cmd
    n, dev = self.num_envs, self.device
    names = self._joint.target_names
    self._head_cols = torch.tensor(
      [names.index(j) for j in ("Head_Yaw", "Head_Pitch")], device=dev
    )
    feet, _ = self._entity.find_bodies(
      ("left_foot_link", "right_foot_link"), preserve_order=True
    )
    self._feet_ids = list(feet)
    head, _ = self._entity.find_bodies("Head_2")
    self._head_id = int(head[0])
    imu = f"{cfg.entity_name}/imu_ang_vel"
    self._imu = imu if imu in env.scene.sensors else None

    # Policy slots. Slot 0 starts as the init checkpoint (or zeros) until the
    # runner syncs the learner's weights.
    if cfg.latest_init_checkpoint:
      latest = load_frozen_policy(cfg.latest_init_checkpoint, cfg.latest_kind, dev)
    else:
      latest = zero_policy(cfg.latest_kind, "latest", dev)
    latest.name = "latest"
    self.slots: list[FrozenPolicy] = [latest]
    self.slot_weights: list[float] = [0.0]
    seeds = list(cfg.seeds)
    if cfg.controller_checkpoint:
      seeds.append(
        OpponentSeedCfg(
          cfg.controller_checkpoint, "controller", weight=cfg.controller_weight
        )
      )
    for seed in seeds:
      self.slots.append(load_frozen_policy(seed.checkpoint, seed.kind, dev))
      self.slot_weights.append(float(seed.weight))
    self._kick_skill: FrozenPolicy | None = None
    self._walk_skill: FrozenPolicy | None = None
    self._num_fixed = len(self.slots)
    self.slot = torch.zeros(n, dtype=torch.long, device=dev)
    # Learner's points won / played per slot (recent window).
    self.slot_wins = torch.zeros(0, device=dev)
    self.slot_points = torch.zeros(0, device=dev)
    self._grow_stats()

    # Perception and control state.
    self.last_seen_w = torch.zeros(n, 2, device=dev)
    self.time_unseen = torch.zeros(n, device=dev)
    self.lost_side = torch.ones(n, device=dev)
    # The learner's memory model (approach command): the last sighting in the
    # trunk frame, turned by the IMU yaw change since (no odometry), and a
    # lost flag latched until the ball is seen again.
    self.last_seen_b = torch.zeros(n, 2, device=dev)
    self.last_seen_yaw = torch.zeros(n, device=dev)
    self.ball_lost = torch.zeros(n, dtype=torch.bool, device=dev)
    self.memory_disproved = torch.zeros(n, dtype=torch.bool, device=dev)
    self.memory_ball_b = torch.zeros(n, 2, device=dev)
    self.memory_age = torch.zeros(n, device=dev)
    self.head_target = torch.tensor(HEAD_DEFAULT, device=dev).repeat(n, 1)
    self.speed_limit = torch.zeros(n, 3, device=dev)
    self.fallen_time = torch.zeros(n, device=dev)
    # Two-level strikers: the held decision and its timing.
    self.ctrl_kick = torch.zeros(n, dtype=torch.bool, device=dev)
    self.ctrl_theta = torch.zeros(n, device=dev)
    self.ctrl_level = torch.zeros(n, device=dev)
    self.ctrl_walk = torch.zeros(n, 3, device=dev)
    self.ctrl_walk_direct = torch.zeros(n, dtype=torch.bool, device=dev)
    self.ctrl_yaw = torch.zeros(n, device=dev)
    self.ctrl_wait = torch.zeros(n, dtype=torch.long, device=dev)
    self.ctrl_since = torch.zeros(n, dtype=torch.long, device=dev)
    # Recurrent controllers' hidden state, widened to the largest slot.
    self.ctrl_h = torch.zeros(n, 0, device=dev)
    # Ball detections as the learner gets them: a per-episode delay of
    # vision_delay_steps policy steps (history of detections).
    hist = int(self._cmd.cfg.vision_delay_steps[1]) + 1
    self._det_hist_b = torch.zeros(n, hist, 2, device=dev)
    self._det_hist_vis = torch.zeros(n, hist, dtype=torch.bool, device=dev)
    self._det_lag = torch.zeros(n, dtype=torch.long, device=dev)
    # Head sweeps in scan_share of episodes, as the learner's head.
    self.scan = torch.zeros(n, dtype=torch.bool, device=dev)
    self._scan_phase = torch.zeros(n, device=dev)
    self._scan_pitch = torch.zeros(n, device=dev)
    self._scan_t = torch.zeros(n, device=dev)
    self._raw = torch.zeros(n, 0, device=dev)
    self._resample_speed_limit(torch.arange(n, device=dev))

  # ActionTerm interface. The opponent consumes no policy actions.

  @property
  def action_dim(self) -> int:
    return 0

  @property
  def raw_action(self) -> torch.Tensor:
    return self._raw

  @property
  def opponent_action(self) -> torch.Tensor:
    """Last raw opponent action (before scale, offset and clip)."""
    return self._joint.raw_action

  def reset(self, env_ids: torch.Tensor | slice | None = None) -> None:
    if env_ids is None:
      env_ids = slice(None)
    ids = torch.arange(self.num_envs, device=self.device)[env_ids]
    self._joint.reset(ids)
    self.fallen_time[ids] = 0.0
    self._resample_speed_limit(ids)
    self.slot[ids] = self._sample_slots(len(ids))
    lo, hi = self._cmd.cfg.vision_delay_steps
    if hi > 0 and len(ids) > 0:
      self._det_lag[ids] = torch.randint(
        int(lo), int(hi) + 1, (len(ids),), device=self.device
      )
    self._det_hist_vis[ids] = False
    k = len(ids)
    self.scan[ids] = torch.rand(k, device=self.device) < self.cfg.scan_share
    self._scan_phase[ids] = torch.rand(k, device=self.device) * 6.2832
    self._scan_pitch[ids] = torch.empty(k, device=self.device).uniform_(0.1, 0.6)
    self._scan_t[ids] = 0.0
    # Recurrent memory starts empty each episode (and, with
    # ``memory_reset_mean_s``, each kickoff and at random; see ``_restart``).
    self._forget(ids)

  def process_actions(self, actions: torch.Tensor) -> None:
    del actions  # Width 0.
    self._record_outcomes()
    self._referee()
    pending = self._cmd.kickoff_pending
    if bool(pending.any()):
      self._restart(pending.nonzero(as_tuple=False).squeeze(-1))
      pending[:] = False
    ball_b, age, kick_dir, kick_range = self._perceive()
    joint = self._joint_obs()
    learner, _ = detect_robot(
      self._entity,
      self._head_id,
      self._origin_xy(),
      self._cmd.robot,
      self._cmd._feet_ids,
      self._cmd.cfg,
      self._cmd.cfg.opponent_max_range,
      self._cmd.cfg.opponent_obs_noise,
      self._cmd.cfg.opponent_dropout,
    )
    kick_obs = torch.cat(
      (
        joint,
        ball_b,
        age.unsqueeze(-1),
        self.speed_limit,
        kick_dir,
        kick_range,
        learner,
      ),
      -1,
    )
    walk_obs = torch.cat((joint, self._walk_command()), -1)
    ctrl_obs = kick_obs
    if self.cfg.controller_ball_memory:
      ctrl_obs = skills.controller_ball_obs(
        kick_obs,
        self.ball_lost,
        self.memory_disproved,
        self.memory_ball_b,
        self.memory_age,
      )
    raw = torch.zeros_like(self._joint.raw_action)
    for s in torch.unique(self.slot).tolist():
      ids = (self.slot == s).nonzero(as_tuple=False).squeeze(-1)
      policy = self.slots[s]
      if policy.kind == "controller":
        raw[ids] = self._run_controller(s, ids, kick_obs[ids], ctrl_obs[ids])
      else:
        obs = kick_obs if policy.kind == "kick" else walk_obs
        raw[ids] = self._sample(s, policy(obs[ids]))
    self._joint.process_actions(raw)
    # The kick policy's head outputs are ignored, as for the learner: the head
    # tracks the ball estimate (also under a controller). A walk-only opponent
    # keeps its own head.
    # As the learner's head: a lost ball gets the far sweep.
    lost_s = torch.where(
      self.ball_lost,
      self.time_unseen.clamp(min=HEAD_SEARCH_AFTER + 0.01),
      self.time_unseen,
    )
    head_ball = torch.where(
      self.ball_lost.unsqueeze(-1), torch.full_like(ball_b, 10.0), ball_b
    )
    # The learner's search range, so both heads search alike.
    learner_head = self._env.action_manager.get_term("joint_pos").cfg
    goal = head_goal(
      head_ball,
      lost_s,
      self._cmd.cfg.camera_pitch,
      getattr(learner_head, "search_yaw", HEAD_SEARCH_YAW),
      getattr(learner_head, "search_pitch", HEAD_SEARCH_PITCH),
    )
    self._scan_t += self._env.step_dt
    scan_yaw = HEAD_SCAN_YAW * torch.sin(
      6.2832 * self._scan_t / HEAD_SCAN_PERIOD + self._scan_phase
    )
    scan_goal = torch.stack((scan_yaw, self._scan_pitch), dim=-1)
    goal = torch.where(self.scan.unsqueeze(-1), scan_goal, goal)
    self.head_target[:] = head_step(self.head_target, goal)
    kick = torch.tensor(
      [p.kind in ("kick", "controller") for p in self.slots], device=self.device
    )[self.slot]
    processed = self._joint._processed_actions.clone()
    head = processed[:, self._head_cols]
    processed[:, self._head_cols] = torch.where(
      kick.unsqueeze(-1), self.head_target, head
    )
    self._joint._processed_actions = processed

  def apply_actions(self) -> None:
    self._joint.apply_actions()

  def skills(self) -> tuple[FrozenPolicy, FrozenPolicy]:
    """The frozen kick and walk skills of two-level strikers (loaded once)."""
    if self._kick_skill is None or self._walk_skill is None:
      dev = self.device
      self._kick_skill = load_frozen_policy(self.cfg.kick_skill_checkpoint, "kick", dev)
      self._walk_skill = load_frozen_policy(self.cfg.walk_skill_checkpoint, "walk", dev)
    return self._kick_skill, self._walk_skill

  def _run_controller(
    self,
    slot: int,
    ids: torch.Tensor,
    actor_obs: torch.Tensor,
    ctrl_obs: torch.Tensor | None = None,
  ) -> torch.Tensor:
    """A two-level opponent: decide every few steps, run the chosen skill.
    ``ctrl_obs``: the controller's inputs where they differ from the skills'
    (``controller_ball_memory``)."""
    ctrl_obs = actor_obs if ctrl_obs is None else ctrl_obs
    policy = self.slots[slot]
    due = self.ctrl_wait[ids] <= 0
    if bool(due.any()):
      d = ids[due]
      inputs = skills.controller_inputs(
        ctrl_obs[due], self.ctrl_kick[d], self.ctrl_since[d]
      )
      hd = policy.hidden_dim
      if hd > self.ctrl_h.shape[1]:
        pad = self.ctrl_h.new_zeros(self.num_envs, hd - self.ctrl_h.shape[1])
        self.ctrl_h = torch.cat((self.ctrl_h, pad), dim=1)
      mean_s = self.cfg.memory_reset_mean_s
      if hd and mean_s is not None:
        p = self.cfg.decision_steps * self._env.step_dt / mean_s
        self.ctrl_h[d[torch.rand(len(d), device=self.device) < p]] = 0.0
      out, h = policy.step(inputs, self.ctrl_h[d, :hd] if hd else None)
      if h is not None:
        self.ctrl_h[d, :hd] = h
      action = self._sample(slot, out)
      kick, theta, level = skills.decode(action)
      copy = slot == 0 or slot >= self._num_fixed
      direct = self.cfg.controller_walk_velocity and copy
      if direct:
        self.ctrl_walk[d] = skills.walk_velocity_command(action, self.speed_limit[d])
      self.ctrl_walk_direct[d] = direct
      switched = kick != self.ctrl_kick[d]
      self.ctrl_since[d] = torch.where(switched, 0, self.ctrl_since[d])
      self.ctrl_kick[d], self.ctrl_theta[d], self.ctrl_level[d] = kick, theta, level
      self.ctrl_yaw[d] = skills.yaw_of(self._entity.data.root_link_quat_w[d])
      self.ctrl_wait[d] = self.cfg.decision_steps
    self.ctrl_wait[ids] -= 1
    self.ctrl_since[ids] += 1
    kick_skill, walk_skill = self.skills()
    theta, level = self.ctrl_theta[ids], self.ctrl_level[ids]
    if self.cfg.aim_world:
      yaw = skills.yaw_of(self._entity.data.root_link_quat_w[ids])
      theta = skills.held_direction(theta, self.ctrl_yaw[ids], yaw)
    walk_cmd = torch.where(
      self.ctrl_walk_direct[ids].unsqueeze(-1),
      self.ctrl_walk[ids],
      skills.walk_command(theta, level),
    )
    return skills.run_skills(
      actor_obs, self.ctrl_kick[ids], theta, level, kick_skill, walk_skill, walk_cmd
    )

  def _sample(self, slot: int, out: torch.Tensor) -> torch.Tensor:
    """Copies of the learner (mirror, snapshots) act as it does in training:
    their mean plus its Gaussian noise. Seeds stay deterministic."""
    policy = self.slots[slot]
    copy = slot == 0 or slot >= self._num_fixed
    if not (self.cfg.sample_copies and copy and policy.action_std is not None):
      return out
    return out + policy.action_std * torch.randn_like(out)

  # Pool management, called by the self-play runner.

  def set_latest(self, actor_state_dict: dict[str, torch.Tensor]) -> None:
    self.slots[0] = frozen_policy_from_state_dict(
      actor_state_dict, self.cfg.latest_kind, "latest", self.device
    )

  def add_snapshot(self, actor_state_dict: dict[str, torch.Tensor], name: str) -> None:
    policy = frozen_policy_from_state_dict(
      actor_state_dict, self.cfg.latest_kind, name, self.device
    )
    if len(self.slots) - self._num_fixed >= self.cfg.max_snapshots:
      # Drop the oldest snapshot; envs using it move to the mirror.
      drop = self._num_fixed
      del self.slots[drop]
      del self.slot_weights[drop]
      keep = torch.ones(len(self.slot_wins), dtype=torch.bool, device=self.device)
      keep[drop] = False
      self.slot_wins = self.slot_wins[keep]
      self.slot_points = self.slot_points[keep]
      moved = self.slot == drop
      self.slot[moved] = 0
      # ctrl_h is widened inside the rollout's inference mode; the runner calls
      # this outside it, where an inference tensor cannot be written in place.
      self.ctrl_h = self.ctrl_h.clone()
      self.ctrl_h[moved] = 0.0
      self.slot[self.slot > drop] -= 1
    self.slots.append(policy)
    self.slot_weights.append(float(self.cfg.snapshot_weight))
    self._grow_stats()

  def _grow_stats(self) -> None:
    extra = len(self.slots) - len(self.slot_wins)
    if extra > 0:
      pad = torch.zeros(extra, device=self.device)
      self.slot_wins = torch.cat((self.slot_wins, pad))
      self.slot_points = torch.cat((self.slot_points, pad.clone()))

  def _sample_slots(self, n: int) -> torch.Tensor:
    dev = self.device
    out = torch.zeros(n, dtype=torch.long, device=dev)
    w = torch.tensor(self.slot_weights, device=dev)
    if n == 0 or float(w.sum()) <= 0.0:
      return out
    pool = torch.multinomial(w, n, replacement=True)
    use_pool = torch.rand(n, device=dev) >= self.cfg.latest_prob
    return torch.where(use_pool, pool, out)

  def _record_outcomes(self) -> None:
    won = self._cmd.contest_scored
    lost = self._cmd.contest_conceded
    k = len(self.slots)
    self.slot_wins += torch.bincount(self.slot, weights=won.float(), minlength=k)
    self.slot_points += torch.bincount(
      self.slot, weights=(won | lost).float(), minlength=k
    )
    # A sliding window: older points fade once a slot has a full window.
    fade = (self.cfg.win_rate_window / self.slot_points.clamp(min=1.0)).clamp(max=1.0)
    self.slot_wins *= fade
    self.slot_points *= fade
    log = self._env.extras.setdefault("log", {})
    pts = self.slot_points.clamp(min=1.0)
    rate = self.slot_wins / pts
    log["SelfPlay/win_rate_latest"] = float(rate[0])
    if k > 1:
      played = self.slot_points[1:] > 0
      if bool(played.any()):
        log["SelfPlay/win_rate_pool"] = float(rate[1:][played].mean())
    log["SelfPlay/pool_size"] = float(k - 1)
    log["SelfPlay/opponent_fallen"] = float((self.fallen_time > 0).float().mean())

  # Field state for the frozen policies.

  def _restart(self, env_ids: torch.Tensor) -> None:
    """After a kickoff or reset: the opponent knows where the ball is."""
    ball_xy = self.ball.data.root_link_pos_w[env_ids, :2]
    self.last_seen_w[env_ids] = ball_xy
    self.time_unseen[env_ids] = 0.0
    quat = self._entity.data.root_link_quat_w[env_ids]
    rel = torch.zeros(len(env_ids), 3, device=self.device)
    rel[:, :2] = ball_xy - self._origin_xy()[env_ids]
    self.last_seen_b[env_ids] = quat_apply_inverse(yaw_quat(quat), rel)[:, :2]
    self.last_seen_yaw[env_ids] = _yaw_angle(quat)
    self.ball_lost[env_ids] = False
    self.head_target[env_ids] = torch.tensor(HEAD_DEFAULT, device=self.device)
    self.fallen_time[env_ids] = 0.0
    self.ctrl_kick[env_ids] = False
    self.ctrl_wait[env_ids] = 0
    self.ctrl_since[env_ids] = 0
    self.ctrl_walk[env_ids] = 0.0
    if self.cfg.memory_reset_mean_s is not None:
      self._forget(env_ids)
    self._joint.reset(env_ids)

  def _forget(self, env_ids: torch.Tensor) -> None:
    """Zero recurrent controllers' state (clone an inference tensor first)."""
    if self.ctrl_h.is_inference() and not torch.is_inference_mode_enabled():
      self.ctrl_h = self.ctrl_h.clone()
    self.ctrl_h[env_ids] = 0.0

  def _referee(self) -> None:
    """Stand a fallen opponent back up, placed as at a kickoff (the ball
    stays where it is)."""
    grav_z = self._entity.data.projected_gravity_b[:, 2]
    fallen = grav_z > -math.cos(self.cfg.fallen_tilt)
    self.fallen_time[:] = torch.where(fallen, self.fallen_time + self._env.step_dt, 0.0)
    pick = self.fallen_time >= self.cfg.getup_after_s
    if not bool(pick.any()):
      return
    ids = pick.nonzero(as_tuple=False).squeeze(-1)
    self._cmd.place_opponent(ids, self.ball.data.root_link_pos_w[ids, :2])

  def _resample_speed_limit(self, env_ids: torch.Tensor) -> None:
    for i, (lo, hi) in enumerate(self.cfg.speed_limit_ranges):
      self.speed_limit[env_ids, i] = torch.empty(
        len(env_ids), device=self.device
      ).uniform_(lo, hi)

  def _joint_obs(self) -> torch.Tensor:
    """Base angular velocity, gravity, joint pos / vel and last action (72)."""
    data = self._entity.data
    if self._imu is not None:
      ang_vel = self._env.scene[self._imu].data
    else:
      ang_vel = data.root_link_ang_vel_b
    default_pos = data.default_joint_pos
    default_vel = data.default_joint_vel
    assert default_pos is not None and default_vel is not None
    parts = [
      ang_vel,
      data.projected_gravity_b,
      # With the encoder bias of the startup DR, as the learner's joint_pos.
      data.joint_pos_biased - default_pos,
      data.joint_vel - default_vel,
    ]
    if self.cfg.obs_noise:
      # The actor's training noise (velocity_amp_env_cfg).
      parts = [
        p + (2.0 * torch.rand_like(p) - 1.0) * a
        for p, a in zip(parts, (0.2, 0.05, 0.01, 1.5), strict=True)
      ]
    return torch.cat((*parts, self._joint.raw_action), -1)

  def _origin_xy(self) -> torch.Tensor:
    """Ball frame origin: the midpoint of the feet (runswift vision)."""
    return self._entity.data.body_link_pos_w[:, self._feet_ids, :2].mean(dim=1)

  def _perceive(
    self,
  ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Ball estimate (head camera, delayed as the learner's, with memory), its age and the
    kick direction / range to the goal the opponent attacks."""
    data = self._entity.data
    quat = data.root_link_quat_w
    ball_w = self.ball.data.root_link_pos_w
    origin = self._origin_xy()
    rel = torch.zeros_like(ball_w)
    rel[:, :2] = ball_w[:, :2] - origin
    true_b = quat_apply_inverse(yaw_quat(quat), rel)[:, :2]
    head_pos = data.body_link_pos_w[:, self._head_id]
    head_quat = data.body_link_quat_w[:, self._head_id]
    cam = self._cmd.cfg
    depth, az, el = camera_angles(
      quat_apply_inverse(head_quat, ball_w - head_pos), cam.camera_pitch
    )
    visible = in_camera_view(
      depth, az, el, cam.fov_half_angle, cam.fov_vertical_half_angle
    )
    if self.cfg.vision_dropout > 0.0:
      visible &= torch.rand_like(depth) >= self.cfg.vision_dropout
    base, slope = self.cfg.ball_obs_noise
    sigma = base + slope * true_b.norm(dim=-1, keepdim=True)
    seen_b = true_b + sigma * torch.randn_like(true_b)
    if self._det_hist_b.shape[1] > 1:
      self._det_hist_b[:] = torch.roll(self._det_hist_b, 1, dims=1)
      self._det_hist_vis[:] = torch.roll(self._det_hist_vis, 1, dims=1)
      self._det_hist_b[:, 0] = seen_b
      self._det_hist_vis[:, 0] = visible
      rows = torch.arange(self.num_envs, device=self.device)
      seen_b = self._det_hist_b[rows, self._det_lag]
      visible = self._det_hist_vis[rows, self._det_lag]

    self.last_seen_w[:] = torch.where(
      visible.unsqueeze(-1), ball_w[:, :2], self.last_seen_w
    )
    vis = visible.unsqueeze(-1)
    yaw = _yaw_angle(quat)
    self.last_seen_b[:] = torch.where(vis, seen_b, self.last_seen_b)
    self.last_seen_yaw[:] = torch.where(visible, yaw, self.last_seen_yaw)
    dt = self._env.step_dt
    self.time_unseen[:] = torch.where(visible, 0.0, self.time_unseen + dt)
    if cam.memory_odometry:
      mem = torch.zeros_like(ball_w)
      mem[:, :2] = self.last_seen_w - origin
      memory_b = quat_apply_inverse(yaw_quat(quat), mem)[:, :2]
    else:
      # As the learner (and the robot runner): turned back by the IMU yaw
      # change since the sighting, no translation.
      dyaw = -wrap_to_pi(yaw - self.last_seen_yaw)
      c, s_ = dyaw.cos(), dyaw.sin()
      mb = self.last_seen_b
      memory_b = torch.stack(
        (c * mb[:, 0] - s_ * mb[:, 1], s_ * mb[:, 0] + c * mb[:, 1]), dim=-1
      )
    ball_b = torch.where(vis, seen_b, memory_b)
    # Lost as the learner's memory_invalidate: the remembered spot in view and
    # unseen for memory_lost_in_view_s, or unseen for memory_lost_timeout_s.
    t = self.time_unseen
    stale = t >= cam.memory_lost_timeout_s
    if cam.memory_invalidate:
      rel = torch.zeros_like(ball_w)
      rel[:, :2] = memory_b
      mem_w = data.root_link_pos_w + quat_apply(yaw_quat(quat), rel)
      mem_w[:, 2] = ball_w[:, 2]
      md, ma, me = camera_angles(
        quat_apply_inverse(head_quat, mem_w - head_pos), cam.camera_pitch
      )
      in_view = in_camera_view(
        md, ma, me, cam.fov_half_angle, cam.fov_vertical_half_angle
      ) & (memory_b.norm(dim=-1) <= cam.memory_view_range)
      disproved = in_view & (t >= cam.memory_lost_in_view_s)
      stale |= disproved
    else:
      disproved = torch.zeros_like(stale)
    newly = stale & ~self.ball_lost & ~visible
    side = torch.where(memory_b[:, 1] >= 0.0, 1.0, -1.0)
    self.lost_side[:] = torch.where(newly, side, self.lost_side)
    self.ball_lost[:] = (self.ball_lost | stale) & ~visible
    lost = self.ball_lost.unsqueeze(-1)
    age = torch.exp(-t / self.cfg.ball_memory_tau)
    # The controller's view (as the learner's command keeps it).
    self.memory_disproved[:] = (self.memory_disproved | disproved) & self.ball_lost
    self.memory_ball_b[:] = memory_b
    self.memory_age[:] = age
    if cam.lost_virtual_ball:
      # A virtual ball beside the robot on the side it was last remembered,
      # the learner's search cue (kick loop v56d); age keeps decaying.
      ang, r = cam.lost_virtual_bearing, cam.lost_virtual_range
      virt = torch.stack(
        (torch.full_like(side, r * math.cos(ang)), self.lost_side * r * math.sin(ang)),
        -1,
      )
      ball_b = torch.where(lost, virt, ball_b)
    else:
      ball_b = torch.where(lost, 0.0, ball_b)
      age = torch.where(self.ball_lost, 0.0, age)

    goal = self._cmd.own_goal_w
    kick_dir = kick_direction_b(goal, self.last_seen_w, quat)
    kick_range = range_one_hot(
      (goal - self.last_seen_w).norm(dim=-1), *self._cmd.cfg.range_edges
    )
    return ball_b, age, kick_dir, kick_range

  def _walk_command(self) -> torch.Tensor:
    """Velocity command for a walk opponent: get behind the ball, then walk
    through it toward the goal it attacks (a dribble)."""
    data = self._entity.data
    pos = data.root_link_pos_w[:, :2]
    ball = self.ball.data.root_link_pos_w[:, :2]
    to_goal = self._cmd.own_goal_w - ball
    u = to_goal / to_goal.norm(dim=-1, keepdim=True).clamp(min=1.0e-6)
    behind = ball - 0.35 * u
    near = (pos - ball).norm(dim=-1) < 0.6
    aim = torch.where(near.unsqueeze(-1), ball + 0.5 * u, behind)
    delta = torch.zeros(self.num_envs, 3, device=self.device)
    delta[:, :2] = aim - pos
    delta_b = quat_apply_inverse(yaw_quat(data.root_link_quat_w), delta)[:, :2]
    dist = delta_b.norm(dim=-1).clamp(min=1.0e-3)
    heading = wrap_to_pi(torch.atan2(delta_b[:, 1], delta_b[:, 0]))
    wz = (2.0 * heading).clamp(-1.2, 1.2)
    facing = (heading.abs() < 0.8).float()
    speed = self.cfg.walk_speed * (0.35 + 0.65 * facing) * (dist / 0.5).clamp(max=1.0)
    vx = speed * delta_b[:, 0] / dist
    vy = 0.35 * speed * delta_b[:, 1] / dist
    return torch.stack((vx, vy, wz), -1)


@dataclass(kw_only=True)
class OpponentPolicyActionCfg(ActionTermCfg):
  """Frozen-policy opponent for :class:`SelfPlayKickCommand`."""

  entity_name: str = "opponent"
  joint_action: JointPositionActionCfg
  """The learner's joint action (scale, offset, clip, order) on the opponent."""
  command_name: str = "twist"
  ball_name: str = "ball"
  latest_kind: PolicyKind = "kick"
  """What the learner is: "kick" (flat striker) or "controller" (two-level)."""
  latest_init_checkpoint: str | None = SELFPLAY_KICK_CKPT
  """Mirror slot before the runner's first sync (and in play); None: zeros."""
  seeds: tuple[OpponentSeedCfg, ...] = field(
    default_factory=lambda: (
      OpponentSeedCfg(SELFPLAY_KICK_CKPT, "kick"),
      OpponentSeedCfg(SELFPLAY_WALK_CKPT, "walk"),
    )
  )
  controller_checkpoint: str | None = None
  """A trained two-level striker's controller, added to the pool (it runs
  the skills below)."""
  controller_weight: float = 1.0
  """Sampling weight of ``controller_checkpoint`` within the pool."""
  kick_skill_checkpoint: str = SELFPLAY_KICK_CKPT
  """Kick skill of two-level strikers (learner and opponent)."""
  walk_skill_checkpoint: str = SELFPLAY_WALK_CKPT
  """Walk skill of two-level strikers (learner and opponent)."""
  decision_steps: int = skills.DECISION_STEPS
  """Env steps per controller decision."""
  memory_reset_mean_s: float | None = None
  """Recurrent controllers' state is zeroed at every kickoff / restart and at
  random, on average this often (s), as the robot's runner zeroes it on each
  striker takeover. None: only at episode ends. Applies to the learner's
  controller (``StrikerControllerVecEnv``) and to controller opponents."""
  controller_ball_memory: bool = False
  """Controllers see a lost ball as their memory until the camera disproves
  it, then (0, 0) and age 0 (``striker_skills.controller_ball_obs``); their
  skills keep the kick loop's search cue. Learner's controller and controller
  opponents alike."""
  aim_world: bool = False
  """Controllers' directions (kick aim, walk heading) are held fixed in the
  world between decisions (``striker_skills.held_direction``), as the robot
  runner holds them by IMU yaw; False: held in the robot frame, so they turn
  with the robot for the 0.2 s a decision lasts."""
  controller_walk_velocity: bool = False
  """The learner's controller (and its copies in the pool) drives the walk
  skill's command directly (``striker_skills.walk_velocity_command``);
  ``controller_checkpoint`` keeps the direction / speed interface it learned."""
  latest_prob: float = 0.5
  """Share of episodes against the learner's latest weights (mirror)."""
  max_snapshots: int = 8
  snapshot_weight: float = 1.0
  obs_noise: bool = True
  vision_dropout: float = 0.02
  ball_obs_noise: tuple[float, float] = (0.03, 0.05)
  ball_memory_tau: float = 2.0
  speed_limit_ranges: tuple[tuple[float, float], ...] = SPEED_CAP_FINAL
  """Per-episode |vx|, |vy|, |wz| limits the kick opponent observes."""
  walk_speed: float = 1.0
  """Cruise speed of the scripted command for walk opponents (m/s)."""
  fallen_tilt: float = 1.0
  """Tilt from upright beyond which the opponent counts as fallen (rad)."""
  getup_after_s: float = 1.0
  """A fallen opponent is stood up again after this long (s)."""
  scan_share: float = 0.0
  """Share of episodes whose head sweeps instead of tracking the ball (set
  to the learner's)."""
  sample_copies: bool = True
  """Copies of the learner sample actions with its noise, as the learner does
  in training (False: their mean; play and evaluations)."""
  win_rate_window: float = 200.0
  """Points per opponent slot that the logged win rates cover (about)."""

  def build(self, env: ManagerBasedRlEnv) -> OpponentPolicyAction:
    return OpponentPolicyAction(self, env)

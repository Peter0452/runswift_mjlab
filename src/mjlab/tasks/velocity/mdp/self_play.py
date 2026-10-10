"""1v1 self-play on the stage-3 kick loop: striker against striker.

A second K1 (``opponent``) shares the field and the ball. Each episode has a
field of random size (9 x 6 up to 14 x 9 m) and heading around the spawned ball,
with 2.4 m goal mouths: the learner attacks ``target_w`` (the centre of one
goal, which the policy gets as its kick direction / range, as the behaviour
would hand it) and defends ``own_goal_w``; the opponent the reverse. The whole
ball over a goal line between the posts and under the bar is a goal; over any
other line it is out. Either ends the point and a new kickoff puts the ball
ahead of the learner, inside the field, and the opponent at the learner's spot
mirrored through the ball (both meet the ball from their own side).
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

from mjlab.entity import Entity
from mjlab.envs.mdp.actions import JointPositionAction, JointPositionActionCfg
from mjlab.managers.action_manager import ActionTerm, ActionTermCfg
from mjlab.tasks.velocity.mdp.amp_symmetry import augment_symmetries_kick_loop
from mjlab.tasks.velocity.mdp.approach import (
  NOMINAL_ROOT_HEIGHT,
  ApproachYawCommandCfg,
  _root_pose,
  ball_radius,
  camera_angles,
  in_camera_view,
  kick_direction_b,
  range_one_hot,
)
from mjlab.tasks.velocity.mdp.kick_loop import (
  HEAD_DEFAULT,
  SPEED_CAP_FINAL,
  KickLoopCommand,
  KickLoopCommandCfg,
  goal_tolerance,
  head_goal,
  head_step,
)
from mjlab.utils.lab_api.math import quat_apply_inverse, wrap_to_pi, yaw_quat

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

PolicyKind = Literal["kick", "walk"]
# Robot detection inputs appended to the stage-3 actor: x, y, seen.
DETECTION_DIM = 3
# Actor input sizes: the kick loop (stage 3, or with the opponent detection)
# and the AMP walk (velocity command).
OBS_DIM: dict[str, tuple[int, ...]] = {"kick": (83, 83 + DETECTION_DIM), "walk": (75,)}
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
  """Deterministic actor (normalizer + ELU MLP) with weights detached from
  any optimizer, so the learner's updates never touch it."""

  kind: str
  name: str
  mean: torch.Tensor
  std: torch.Tensor
  layers: list[tuple[torch.Tensor, torch.Tensor]]

  @property
  def in_dim(self) -> int:
    return self.layers[0][0].shape[1]

  def __call__(self, obs: torch.Tensor) -> torch.Tensor:
    """``obs`` may carry more inputs than the policy takes (an 83-input
    stage-3 policy ignores the appended detection)."""
    x = (obs[:, : self.in_dim] - self.mean) / self.std
    for i, (w, b) in enumerate(self.layers):
      x = F.linear(x, w, b)
      if i < len(self.layers) - 1:
        x = F.elu(x)
    return x


def frozen_policy_from_state_dict(
  state_dict: dict[str, torch.Tensor], kind: str, name: str, device: str
) -> FrozenPolicy:
  """Copy an rsl_rl ``MLPModel`` actor state dict into a ``FrozenPolicy``."""
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
  in_dim = layers[0][0].shape[1]
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
  return FrozenPolicy(kind=kind, name=name, mean=mean, std=std, layers=layers)


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
    # Set on kickoffs, cleared by the opponent action once it has re-read the
    # field (its ball memory, head and last action restart).
    self.kickoff_pending = torch.ones(n, dtype=torch.bool, device=dev)
    self._scored = torch.zeros(n, device=dev)
    self._conceded = torch.zeros(n, device=dev)
    self._outs = torch.zeros(n, device=dev)
    for name in ("contest_scored", "contest_conceded", "ball_out"):
      self.metrics[name] = torch.zeros(n, device=dev)

  def _update_metrics(self) -> None:
    super()._update_metrics()
    self.metrics["contest_scored"][:] = self._scored
    self.metrics["contest_conceded"][:] = self._conceded
    self.metrics["ball_out"][:] = self._outs

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
    half = 0.5 * self.field_length[env_ids].unsqueeze(-1)
    u = self.field_axis[env_ids]
    self.target_w[env_ids] = self.field_center[env_ids] + u * half
    self.own_goal_w[env_ids] = self.field_center[env_ids] - u * half
    self.target_dist[env_ids] = (self.target_w[env_ids] - ball_xy).norm(dim=-1)
    self.goal_tol[env_ids] = goal_tolerance(self.target_dist[env_ids])

  def _resample_command(self, env_ids: torch.Tensor) -> None:
    super()._resample_command(env_ids)
    for buf in (self.contest_scored, self.contest_conceded, self.ball_out):
      buf[env_ids] = False
    for buf in (self._scored, self._conceded, self._outs):
      buf[env_ids] = 0.0
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
    restart = scored | conceded | out
    if bool(restart.any()):
      self._kickoff(restart.nonzero(as_tuple=False).squeeze(-1))

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
    self._set_goals(env_ids, ball_xy)
    for buf in (
      self.kicked_since_target,
      self.lined_up_latched,
      self.rest_pending,
      self.near_pending,
    ):
      buf[env_ids] = False
    self.place_opponent(env_ids, ball_xy)

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
    face = ball_xy - xy
    yaw = torch.atan2(face[:, 1], face[:, 0])
    yaw = yaw + torch.empty(n, device=dev).uniform_(
      -self.cfg.opponent_yaw_noise, self.cfg.opponent_yaw_noise
    )
    place_upright(self.opponent, env_ids, xy, yaw, self._env.scene.env_origins)
    self.kickoff_pending[env_ids] = True

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
  spawn_margin: float = 0.5
  """Kickoff balls stay this far inside the lines (m)."""
  own_side_start_prob: float = 0.5
  """Share of episodes whose field puts the learner on its own side of the
  ball (attacking within 60 degrees of its line to the ball)."""
  opponent_distance_range: tuple[float, float] = (0.8, 5.0)
  """Limits of the opponent's distance from the ball at kickoff (m)."""
  opponent_spawn_half_angle: float = 0.4
  """Jitter of the opponent's mirrored spot around the ball (rad)."""
  opponent_yaw_noise: float = 0.3
  opponent_clearance: float = 1.0
  """Minimum learner-opponent distance at kickoff (m), when achievable."""
  opponent_max_range: float = 6.0
  """Farthest robot detection (m); match the robot detector."""
  opponent_obs_noise: tuple[float, float] = (0.05, 0.05)
  """Detection noise: sigma = base + rel * distance (m, per axis)."""
  opponent_dropout: float = 0.05
  """Probability per step that a robot in view is not detected."""

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

    # Policy slots. Slot 0 starts as the init checkpoint until the runner
    # syncs the learner's weights.
    latest = load_frozen_policy(cfg.latest_init_checkpoint, "kick", dev)
    latest.name = "latest"
    self.slots: list[FrozenPolicy] = [latest]
    self.slot_weights: list[float] = [0.0]
    for seed in cfg.seeds:
      self.slots.append(load_frozen_policy(seed.checkpoint, seed.kind, dev))
      self.slot_weights.append(float(seed.weight))
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
    self.head_target = torch.tensor(HEAD_DEFAULT, device=dev).repeat(n, 1)
    self.speed_limit = torch.zeros(n, 3, device=dev)
    self.fallen_time = torch.zeros(n, device=dev)
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
    raw = torch.zeros_like(self._joint.raw_action)
    for s in torch.unique(self.slot).tolist():
      ids = (self.slot == s).nonzero(as_tuple=False).squeeze(-1)
      policy = self.slots[s]
      obs = kick_obs if policy.kind == "kick" else walk_obs
      raw[ids] = policy(obs[ids])
    self._joint.process_actions(raw)
    # The kick policy's head outputs are ignored, as for the learner: the head
    # tracks the ball estimate. The walk policy keeps its own head.
    lost_s = torch.where(
      self.time_unseen > self.cfg.lost_timeout_s,
      self.time_unseen.clamp(min=0.51),
      self.time_unseen,
    )
    goal = head_goal(ball_b, lost_s, self._cmd.cfg.camera_pitch)
    self.head_target[:] = head_step(self.head_target, goal)
    kick = torch.tensor([p.kind == "kick" for p in self.slots], device=self.device)[
      self.slot
    ]
    processed = self._joint._processed_actions.clone()
    head = processed[:, self._head_cols]
    processed[:, self._head_cols] = torch.where(
      kick.unsqueeze(-1), self.head_target, head
    )
    self._joint._processed_actions = processed

  def apply_actions(self) -> None:
    self._joint.apply_actions()

  # Pool management, called by the self-play runner.

  def set_latest(self, actor_state_dict: dict[str, torch.Tensor]) -> None:
    self.slots[0] = frozen_policy_from_state_dict(
      actor_state_dict, "kick", "latest", self.device
    )

  def add_snapshot(self, actor_state_dict: dict[str, torch.Tensor], name: str) -> None:
    policy = frozen_policy_from_state_dict(actor_state_dict, "kick", name, self.device)
    if len(self.slots) - self._num_fixed >= self.cfg.max_snapshots:
      # Drop the oldest snapshot; envs using it move to the mirror.
      drop = self._num_fixed
      del self.slots[drop]
      del self.slot_weights[drop]
      keep = torch.ones(len(self.slot_wins), dtype=torch.bool, device=self.device)
      keep[drop] = False
      self.slot_wins = self.slot_wins[keep]
      self.slot_points = self.slot_points[keep]
      self.slot[self.slot == drop] = 0
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
    self.last_seen_w[env_ids] = self.ball.data.root_link_pos_w[env_ids, :2]
    self.time_unseen[env_ids] = 0.0
    self.head_target[env_ids] = torch.tensor(HEAD_DEFAULT, device=self.device)
    self.fallen_time[env_ids] = 0.0
    self._joint.reset(env_ids)

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
      data.joint_pos - default_pos,
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
    """Ball estimate (head camera, delay-free, with memory), its age and the
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

    self.last_seen_w[:] = torch.where(
      visible.unsqueeze(-1), ball_w[:, :2], self.last_seen_w
    )
    dt = self._env.step_dt
    self.time_unseen[:] = torch.where(visible, 0.0, self.time_unseen + dt)
    mem = torch.zeros_like(ball_w)
    mem[:, :2] = self.last_seen_w - origin
    memory_b = quat_apply_inverse(yaw_quat(quat), mem)[:, :2]
    ball_b = torch.where(visible.unsqueeze(-1), seen_b, memory_b)
    # Lost: a virtual ball beside the robot on the side it was last seen, the
    # learner's search cue (kick loop v56d).
    lost = self.time_unseen > self.cfg.lost_timeout_s
    newly = lost & (self.time_unseen - dt <= self.cfg.lost_timeout_s)
    side = torch.where(memory_b[:, 1] >= 0.0, 1.0, -1.0)
    self.lost_side[:] = torch.where(newly, side, self.lost_side)
    ang, r = 1.6, 2.0
    virt = torch.stack(
      (torch.full_like(side, r * math.cos(ang)), self.lost_side * r * math.sin(ang)),
      -1,
    )
    ball_b = torch.where(lost.unsqueeze(-1), virt, ball_b)
    age = torch.exp(-self.time_unseen / self.cfg.ball_memory_tau)

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
  latest_init_checkpoint: str = SELFPLAY_KICK_CKPT
  """Mirror slot before the runner's first sync (and in play)."""
  seeds: tuple[OpponentSeedCfg, ...] = field(
    default_factory=lambda: (
      OpponentSeedCfg(SELFPLAY_KICK_CKPT, "kick"),
      OpponentSeedCfg(SELFPLAY_WALK_CKPT, "walk"),
    )
  )
  latest_prob: float = 0.5
  """Share of episodes against the learner's latest weights (mirror)."""
  max_snapshots: int = 8
  snapshot_weight: float = 1.0
  obs_noise: bool = True
  vision_dropout: float = 0.02
  ball_obs_noise: tuple[float, float] = (0.03, 0.05)
  ball_memory_tau: float = 2.0
  lost_timeout_s: float = 1.5
  speed_limit_ranges: tuple[tuple[float, float], ...] = SPEED_CAP_FINAL
  """Per-episode |vx|, |vy|, |wz| limits the kick opponent observes."""
  walk_speed: float = 1.0
  """Cruise speed of the scripted command for walk opponents (m/s)."""
  fallen_tilt: float = 1.0
  """Tilt from upright beyond which the opponent counts as fallen (rad)."""
  getup_after_s: float = 1.0
  """A fallen opponent is stood up again after this long (s)."""
  win_rate_window: float = 200.0
  """Points per opponent slot that the logged win rates cover (about)."""

  def build(self, env: ManagerBasedRlEnv) -> OpponentPolicyAction:
    return OpponentPolicyAction(self, env)

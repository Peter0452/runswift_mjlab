"""1v1 self-play on the stage-3 kick loop.

A second K1 (``opponent``) shares the field and the ball. Each point has two
goals on one axis: the learner attacks ``target_w`` (the kick-loop target) and
defends ``own_goal_w``; the opponent attacks ``own_goal_w`` and defends
``target_w``. A ball inside either goal's tolerance, or out of play, ends the
point: a new kickoff places the ball, both goals and the opponent, as the kick
loop places a new target after a goal. The learner is never teleported and the
episode only ends on the usual terminations (falls, time out).

The opponent is not trained. ``OpponentPolicyAction`` runs frozen policies on
observations it builds from the sim with the actor's 83-dim layout, so it adds
no policy actions: the learner's action and observation layouts are those of
stage 3 and its checkpoints warm-start unchanged. Each episode the opponent is
either the learner's latest weights (mirror) or a policy from a pool of seed
checkpoints and snapshots, which the self-play runner keeps up to date.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import torch
import torch.nn.functional as F

from mjlab.entity import Entity
from mjlab.envs.mdp.actions import JointPositionAction, JointPositionActionCfg
from mjlab.managers.action_manager import ActionTerm, ActionTermCfg
from mjlab.tasks.velocity.mdp.approach import (
  NOMINAL_ROOT_HEIGHT,
  _root_pose,
  camera_angles,
  in_camera_view,
  kick_direction_b,
  range_one_hot,
  sample_binned,
)
from mjlab.tasks.velocity.mdp.kick_loop import (
  HEAD_DEFAULT,
  SPEED_CAP_FINAL,
  TARGET_BINS,
  KickLoopCommand,
  KickLoopCommandCfg,
  goal_tolerance,
  head_goal,
  head_step,
)
from mjlab.utils.lab_api.math import quat_apply_inverse, wrap_to_pi, yaw_quat

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_REPO = Path(__file__).resolve().parents[5]

# Seeds for the opponent pool (paths relative to the repo root work too).
SELFPLAY_KICK_CKPT = "logs/rsl_rl/k1_kick_stage3_amp/blends/h022_c2_x50.pt"
SELFPLAY_WALK_CKPT = (
  "logs/rsl_rl/k1_velocity_amp_symmetric_muon_wwcmu50_roughft/"
  "2026-09-21_20-34-24_stageA/model_9950.pt"
)

PolicyKind = Literal["kick", "walk"]
# Actor input sizes: stage-3 kick loop and the AMP walk (velocity command).
OBS_DIM: dict[str, int] = {"kick": 83, "walk": 75}
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

  def __call__(self, obs: torch.Tensor) -> torch.Tensor:
    x = (obs - self.mean) / self.std
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
  if in_dim != OBS_DIM[kind]:
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


##
# Command: goals, kickoffs and point outcomes.
##


class SelfPlayKickCommand(KickLoopCommand):
  """Kick-loop command with an opponent, two fixed goals per point and
  kickoffs after each point."""

  cfg: SelfPlayKickCommandCfg  # pyright: ignore[reportIncompatibleVariableOverride]

  def __init__(self, cfg: SelfPlayKickCommandCfg, env: ManagerBasedRlEnv):
    # Set before super().__init__: the parent may place targets while building.
    self._freeze_target = False
    super().__init__(cfg, env)
    self.opponent: Entity = env.scene[cfg.opponent_name]
    n, dev = self.num_envs, self.device
    self.own_goal_w = torch.zeros(n, 2, device=dev)
    self.own_goal_tol = torch.ones(n, device=dev)
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
    # Goals stay put during a point; the kick loop would move the target
    # after a goal or a ball resting far away.
    if self._freeze_target:
      return
    super()._place_target(env_ids, ball_xy)

  def _replace_targets(self, env_ids: torch.Tensor, ball_xy: torch.Tensor) -> None:
    super()._replace_targets(env_ids, ball_xy)
    self._place_own_goal(env_ids, ball_xy)

  def _resample_command(self, env_ids: torch.Tensor) -> None:
    super()._resample_command(env_ids)
    for buf in (self.contest_scored, self.contest_conceded, self.ball_out):
      buf[env_ids] = False
    for buf in (self._scored, self._conceded, self._outs):
      buf[env_ids] = 0.0
    # The ball may come from a mid-kick reference state; read it from qpos.
    ball_xy = _root_pose(self.ball, env_ids)[:, :2]
    self._place_own_goal(env_ids, ball_xy)
    self.place_opponent(env_ids, ball_xy)

  def _update_command(self) -> None:
    # The kick loop re-derives the goal tolerance when it would move the
    # target; both goals keep theirs until the point ends.
    goal_tol = self.goal_tol.clone()
    self._freeze_target = True
    try:
      super()._update_command()
    finally:
      self._freeze_target = False
    self.goal_tol[:] = goal_tol
    ball_xy = self.ball.data.root_link_pos_w[:, :2]
    scored = (ball_xy - self.target_w).norm(dim=-1) <= self.goal_tol
    conceded = ~scored & ((ball_xy - self.own_goal_w).norm(dim=-1) <= self.own_goal_tol)
    out = ~(scored | conceded) & self._out_of_play(ball_xy)
    self.contest_scored[:] = scored
    self.contest_conceded[:] = conceded
    self.ball_out[:] = out
    self._scored += scored.float()
    self._conceded += conceded.float()
    self._outs += out.float()
    restart = scored | conceded | out
    if bool(restart.any()):
      self._kickoff(restart.nonzero(as_tuple=False).squeeze(-1))

  def _out_of_play(self, ball_xy: torch.Tensor) -> torch.Tensor:
    """Ball wide of the goal axis, or past either goal (missed it)."""
    axis = self.target_w - self.own_goal_w
    length = axis.norm(dim=-1).clamp(min=1.0e-6)
    u = axis / length.unsqueeze(-1)
    rel = ball_xy - self.own_goal_w
    along = (rel * u).sum(dim=-1)
    across = (rel[:, 0] * u[:, 1] - rel[:, 1] * u[:, 0]).abs()
    overrun = self.cfg.goal_overrun
    past = (along < -overrun) | (along > length + overrun)
    return past | (across > self.cfg.field_half_width)

  def _kickoff(self, env_ids: torch.Tensor) -> None:
    """New point: ball ahead of the learner (as at spawn), new goals and the
    opponent back on its defending side."""
    self._spawn_ball_and_target(env_ids)
    self.goal_tol[env_ids] = goal_tolerance(self.target_dist[env_ids])
    for buf in (
      self.kicked_since_target,
      self.lined_up_latched,
      self.rest_pending,
      self.near_pending,
    ):
      buf[env_ids] = False
    ball_xy = _root_pose(self.ball, env_ids)[:, :2]
    self._place_own_goal(env_ids, ball_xy)
    self.place_opponent(env_ids, ball_xy)

  def _place_own_goal(self, env_ids: torch.Tensor, ball_xy: torch.Tensor) -> None:
    """Learner's own goal on the far side of the ball from its target."""
    to_target = self.target_w[env_ids] - ball_xy
    u = to_target / to_target.norm(dim=-1, keepdim=True).clamp(min=1.0e-6)
    dist = sample_binned(len(env_ids), self.cfg.own_goal_distance_bins, self.device)
    self.own_goal_w[env_ids] = ball_xy - u * dist.unsqueeze(-1)
    self.own_goal_tol[env_ids] = goal_tolerance(dist)

  def place_opponent(self, env_ids: torch.Tensor, ball_xy: torch.Tensor) -> None:
    """Opponent between the ball and the goal it defends (the learner's
    target), facing the ball, clear of the learner."""
    n = len(env_ids)
    if n == 0:
      return
    dev = self.device
    to_target = self.target_w[env_ids] - ball_xy
    base = torch.atan2(to_target[:, 1], to_target[:, 0])
    learner_xy = _root_pose(self.robot, env_ids)[:, :2]
    # A few candidate spots; keep the first clear of the learner, else the
    # farthest from it.
    k = 4
    half = self.cfg.opponent_spawn_half_angle
    ang = base.unsqueeze(1) + torch.empty(n, k, device=dev).uniform_(-half, half)
    rad = torch.empty(n, k, device=dev).uniform_(*self.cfg.opponent_distance_range)
    # In front of the goal it defends, not behind it.
    reach = (0.8 * to_target.norm(dim=-1)).clamp(min=0.6)
    rad = torch.minimum(rad, reach.unsqueeze(1))
    cand = ball_xy.unsqueeze(1) + torch.stack(
      (ang.cos(), ang.sin()), -1
    ) * rad.unsqueeze(-1)
    clear = (cand - learner_xy.unsqueeze(1)).norm(dim=-1)
    ok = clear >= self.cfg.opponent_clearance
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
  own_goal_distance_bins: tuple[tuple[float, float], ...] = TARGET_BINS
  """Ball-to-own-goal distance bins (m) at each kickoff."""
  opponent_distance_range: tuple[float, float] = (1.0, 4.0)
  """Opponent's distance from the ball at kickoff (m), as the learner's."""
  opponent_spawn_half_angle: float = 0.6
  """Spread of the opponent's spot around the ball-to-target line (rad)."""
  opponent_yaw_noise: float = 0.3
  opponent_clearance: float = 1.0
  """Minimum learner-opponent distance at kickoff (m), when achievable."""
  field_half_width: float = 4.0
  """Ball farther than this from the goal axis is out of play (m)."""
  goal_overrun: float = 1.5
  """Ball this far past either goal (outside its tolerance) is out (m)."""

  def build(self, env: ManagerBasedRlEnv) -> SelfPlayKickCommand:
    return SelfPlayKickCommand(self, env)


def _selfplay_command(
  env: ManagerBasedRlEnv, name: str = "twist"
) -> SelfPlayKickCommand:
  cmd = env.command_manager.get_term(name)
  assert isinstance(cmd, SelfPlayKickCommand)
  return cmd


# Rewards. Point outcomes are set at the end of a step and paid by the next.


def contest_score(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per point won: the ball entered the goal the learner attacks."""
  return _selfplay_command(env).contest_scored.float()


def contest_concede(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Per point lost: the ball entered the goal the learner defends."""
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
    kick_obs = torch.cat(
      (joint, ball_b, age.unsqueeze(-1), self.speed_limit, kick_dir, kick_range), -1
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
    """Stand a fallen opponent back up on its defending side, as at a
    kickoff (the ball stays where it is)."""
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

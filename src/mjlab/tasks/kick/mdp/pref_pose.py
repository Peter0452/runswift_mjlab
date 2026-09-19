"""3-phase kick reference pose (Arc → Setup → Strike) for reward shaping.

``P_ref`` is a reward magnet only — not an observation or teacher command.
In every phase it is the behind-ball plant ``setup_xy`` (not a side-arc
orbit), so rising ``pref_pose`` means approaching the kick stance. Phase still
gates swing/kick terms; Arc vs Setup is hysteresis on robot–ball distance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch

from mjlab.entity import Entity
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.tasks.kick.mdp.geometry import ball_to_goal_direction_xy

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_DEFAULT_ROBOT_CFG = SceneEntityCfg("robot")
_DEFAULT_BALL_CFG = SceneEntityCfg("ball")

# Phase ids for logging / gating.
PHASE_ARC = 0
PHASE_SETUP = 1
PHASE_STRIKE = 2


@dataclass
class PrefPoseState:
  """Per-env latched phase and kicking-foot choice."""

  phase: torch.Tensor  # int64 [B]
  kicking_foot: torch.Tensor  # int64 [B], 0=left, 1=right
  prefer_right_foot: bool  # config default when dynamic_kick_foot=False
  aligned: torch.Tensor  # bool [B] — plant pose + bearing vs ball→goal


def _get_state(env: ManagerBasedRlEnv, prefer_right_foot: bool) -> PrefPoseState:
  state = getattr(env, "_kick_pref_pose", None)
  if (
    state is None
    or state.phase.shape[0] != env.num_envs
    or not hasattr(state, "kicking_foot")
    or state.kicking_foot.shape[0] != env.num_envs
    or not hasattr(state, "aligned")
    or state.aligned.shape[0] != env.num_envs
  ):
    default_foot = 1 if prefer_right_foot else 0
    state = PrefPoseState(
      phase=torch.zeros(env.num_envs, dtype=torch.long, device=env.device),
      kicking_foot=torch.full(
        (env.num_envs,), default_foot, dtype=torch.long, device=env.device
      ),
      prefer_right_foot=prefer_right_foot,
      aligned=torch.zeros(env.num_envs, dtype=torch.bool, device=env.device),
    )
    env._kick_pref_pose = state
  state.prefer_right_foot = prefer_right_foot
  return state


def reset_pref_pose_state(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None = None,
) -> None:
  """Clear phase / kicking-foot latches on episode reset."""
  from mjlab.envs.mdp.events import resolve_env_ids

  state = getattr(env, "_kick_pref_pose", None)
  if state is None:
    return
  env_ids = resolve_env_ids(env, env_ids)
  state.phase[env_ids] = 0
  default_foot = 1 if state.prefer_right_foot else 0
  state.kicking_foot[env_ids] = default_foot
  state.aligned[env_ids] = False


def _rotate90_ccw(v: torch.Tensor) -> torch.Tensor:
  return torch.stack((-v[:, 1], v[:, 0]), dim=-1)


def preferred_arc_side(
  robot_xy: torch.Tensor,
  ball_xy: torch.Tensor,
  goal_dir: torch.Tensor,
) -> torch.Tensor:
  """+1 = left of goal axis (looking toward goal), -1 = right.

  Uses ``sign(goal × (robot - ball))`` in 2D.
  """
  rel = robot_xy - ball_xy
  cross = goal_dir[:, 0] * rel[:, 1] - goal_dir[:, 1] * rel[:, 0]
  return torch.where(cross >= 0.0, torch.ones_like(cross), -torch.ones_like(cross))


def _nearest_foot_to_ball(
  robot: Entity,
  ball_xy: torch.Tensor,
) -> torch.Tensor:
  """Per-env foot index closer to the ball in XY (0=left, 1=right)."""
  left_ids, _ = robot.find_bodies("left_foot_link")
  right_ids, _ = robot.find_bodies("right_foot_link")
  feet = robot.data.body_link_pos_w[:, [left_ids[0], right_ids[0]], :2]
  dist = torch.linalg.norm(feet - ball_xy.unsqueeze(1), dim=-1)
  return torch.argmin(dist, dim=-1)


def setup_offset_xy(
  goal_dir: torch.Tensor,
  *,
  behind: float = 0.35,
  lateral: float = 0.12,
  prefer_right_foot: bool | torch.Tensor = True,
) -> torch.Tensor:
  """Offset in world XY: behind ball along -goal, lateral for kick foot.

  Right-footed kick → stand on the **left** of the goal axis (+lateral).
  ``prefer_right_foot`` may be a bool or a per-env bool/tensor mask.
  """
  left = _rotate90_ccw(goal_dir)
  if isinstance(prefer_right_foot, torch.Tensor):
    side = torch.where(prefer_right_foot.unsqueeze(-1), left, -left)
  else:
    side = left if prefer_right_foot else -left
  return -goal_dir * behind + side * lateral


def nearest_arc_point_xy(
  robot_xy: torch.Tensor,
  ball_xy: torch.Tensor,
  goal_dir: torch.Tensor,
  radius: float,
) -> torch.Tensor:
  """Closest point on the preferred-side arc of radius ``radius`` around the ball."""
  side = preferred_arc_side(robot_xy, ball_xy, goal_dir)
  left = _rotate90_ccw(goal_dir)
  tangent = left * side.unsqueeze(-1)

  rel = robot_xy - ball_xy
  dist = torch.linalg.norm(rel, dim=-1, keepdim=True).clamp(min=1.0e-6)
  direction = rel / dist

  on_side = (direction * tangent).sum(dim=-1)  # [B]
  # Wrong half-plane: flip lateral component across the goal axis.
  lat = (direction * tangent).sum(dim=-1, keepdim=True)
  along = (direction * goal_dir).sum(dim=-1, keepdim=True)
  flipped = along * goal_dir + torch.abs(lat) * tangent
  flipped = flipped / torch.linalg.norm(flipped, dim=-1, keepdim=True).clamp(min=1.0e-6)
  direction = torch.where((on_side < 0.0).unsqueeze(-1), flipped, direction)
  return ball_xy + direction * radius


def _smoothstep(edge0: float, edge1: float, x: torch.Tensor) -> torch.Tensor:
  """Hermite smoothstep: 0 for ``x <= edge0``, 1 for ``x >= edge1``."""
  denom = float(edge1) - float(edge0)
  if abs(denom) < 1.0e-6:
    return (x >= float(edge1)).to(dtype=x.dtype)
  t = ((x - float(edge0)) / denom).clamp(0.0, 1.0)
  return t * t * (3.0 - 2.0 * t)


def compute_reference_pose_xy(
  env: ManagerBasedRlEnv,
  command_name: str = "goal",
  arc_radius: float = 0.4,
  setup_enter_dist: float = 0.9,
  setup_exit_dist: float = 1.0,
  setup_behind: float = 0.35,
  setup_lateral: float = 0.12,
  prefer_right_foot: bool = True,
  bearing_thresh: float = 0.2,
  lateral_thresh: float = 0.05,
  setup_blend_end: float = 0.20,
  strike_blend_thresh: float = 0.75,
  setup_pos_thresh: float = 0.28,
  dynamic_kick_foot: bool = True,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> tuple[torch.Tensor, torch.Tensor]:
  """Return ``(P_ref_xy [B,2], phase [B])`` with Arc→Setup→Strike hysteresis.

  ``P_ref`` is always the behind-ball plant ``setup_xy`` (Arc / Setup / Strike).
  The old nearest-arc magnet is intentionally unused for the reward target — it
  created a stable side-orbit that never entered Setup. ``arc_radius`` is kept
  for call-site compatibility / debug helpers only.

  ``blend_t`` (``setup_enter_dist`` → ``setup_blend_end``) only drives the
  soft Setup→Strike latch (``strike_blend_thresh``); it does **not** pull
  ``P_ref`` onto the ball (CoM stays planted; swing foot reaches the ball).

  With ``dynamic_kick_foot``, the nearer foot is tracked during Arc and
  **latched** on Setup/Strike so setup offset + swing rewards stay consistent.
  """
  _ = arc_radius  # reward magnet no longer uses the side-arc; keep kw for API.
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  robot_xy = robot.data.root_link_pos_w[:, :2]
  ball_xy = ball.data.root_link_pos_w[:, :2]
  goal_dir = ball_to_goal_direction_xy(env, ball_xy, command_name)

  dist = torch.linalg.norm(robot_xy - ball_xy, dim=-1)
  state = _get_state(env, prefer_right_foot)
  phase = state.phase.clone()

  # --- kicking foot: update in Arc, latch in Setup/Strike ---
  if dynamic_kick_foot:
    nearest = _nearest_foot_to_ball(robot, ball_xy)
    in_arc = phase == PHASE_ARC
    state.kicking_foot = torch.where(in_arc, nearest, state.kicking_foot)
    prefer_right_mask = state.kicking_foot == 1
  else:
    prefer_right_mask = prefer_right_foot

  # --- desired phase from geometry ---
  offset = setup_offset_xy(
    goal_dir,
    behind=setup_behind,
    lateral=setup_lateral,
    prefer_right_foot=prefer_right_mask,
  )
  setup_xy = ball_xy + offset
  setup_err = robot_xy - setup_xy
  left = _rotate90_ccw(goal_dir)
  lateral_err = torch.abs((setup_err * left).sum(dim=-1))
  qw, qx, qy, qz = (
    robot.data.root_link_quat_w[:, 0],
    robot.data.root_link_quat_w[:, 1],
    robot.data.root_link_quat_w[:, 2],
    robot.data.root_link_quat_w[:, 3],
  )
  body_fwd = torch.stack(
    (1.0 - 2.0 * (qy * qy + qz * qz), 2.0 * (qx * qy + qw * qz)),
    dim=-1,
  )
  body_fwd = body_fwd / torch.linalg.norm(body_fwd, dim=-1, keepdim=True).clamp(
    min=1.0e-6
  )
  bearing = torch.acos((body_fwd * goal_dir).sum(dim=-1).clamp(-1.0, 1.0))
  at_setup = (lateral_err < lateral_thresh) & (
    torch.linalg.norm(setup_err, dim=-1) < float(setup_pos_thresh)
  )
  aligned = (bearing < bearing_thresh) & at_setup

  # Blend weight: 0 at setup_enter_dist (just entered), 1 at setup_blend_end (into ball).
  blend_t = 1.0 - _smoothstep(float(setup_blend_end), float(setup_enter_dist), dist)

  # Hysteresis transitions.
  want_setup = dist < setup_enter_dist
  leave_setup = dist > setup_exit_dist
  soft_strike = blend_t >= float(strike_blend_thresh)

  new_phase = phase.clone()
  to_setup = (phase == PHASE_ARC) & want_setup
  new_phase = torch.where(to_setup, torch.full_like(phase, PHASE_SETUP), new_phase)
  to_arc = (phase == PHASE_SETUP) & leave_setup
  new_phase = torch.where(to_arc, torch.full_like(phase, PHASE_ARC), new_phase)
  to_strike = (phase == PHASE_SETUP) & (aligned | soft_strike)
  new_phase = torch.where(to_strike, torch.full_like(phase, PHASE_STRIKE), new_phase)
  strike_reset = (phase == PHASE_STRIKE) & leave_setup
  new_phase = torch.where(strike_reset, torch.full_like(phase, PHASE_ARC), new_phase)

  # Latch foot on Arc→Setup transition (final nearest before leaving Arc).
  if dynamic_kick_foot:
    entering_setup = (phase == PHASE_ARC) & (new_phase == PHASE_SETUP)
    if entering_setup.any():
      nearest = _nearest_foot_to_ball(robot, ball_xy)
      state.kicking_foot = torch.where(entering_setup, nearest, state.kicking_foot)

  state.phase.copy_(new_phase)
  phase = new_phase
  state.aligned.copy_(aligned)

  # Always plant behind the ball — never a side-arc orbit, never onto ball_xy.
  return setup_xy, phase


def get_latched_kicking_foot(
  env: ManagerBasedRlEnv,
  prefer_right_foot: bool = True,
) -> torch.Tensor:
  """Return latched kicking foot indices (0=left, 1=right), shape ``[B]``."""
  return _get_state(env, prefer_right_foot).kicking_foot


def get_kick_aligned(
  env: ManagerBasedRlEnv,
  prefer_right_foot: bool = True,
) -> torch.Tensor:
  """Return last ``aligned`` mask from ``compute_reference_pose_xy`` (bool ``[B]``)."""
  return _get_state(env, prefer_right_foot).aligned

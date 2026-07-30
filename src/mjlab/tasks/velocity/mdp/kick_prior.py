"""Kick-prior observation and reward terms for RL.

These terms expose a cubic Bézier kick trajectory as an action prior,
enabling two complementary training strategies:

**Residual policy**
  The actor observes ``kick_prior_target`` and outputs *residual* joint
  corrections.  The environment adds the prior target to the network output
  before applying actions:

      action_applied = prior_target(phase) + policy_output

  The policy only needs to learn small corrections; the prior carries the
  gross motion, drastically reducing the exploration burden.

**Shaped reward**
  Add ``kick_prior_tracking`` to the reward mix.  The Gaussian kernel rewards
  how closely the robot tracks the Bézier trajectory at each timestep.  Weight
  it heavily early in training, then anneal (via ``drop_step`` / ``fade_steps``)
  as the policy matures.

Both terms share the ``advance_gait_phase`` clock from ``observations.py`` so
they remain in sync with the ``gait_cycle`` observation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from mjlab.entity import Entity
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.tasks.velocity.mdp.observations import advance_gait_phase, gait_scale

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv
  from mjlab.managers.observation_manager import ObservationTermCfg

_DEFAULT_ASSET_CFG = SceneEntityCfg("robot")

# ─────────────────────────── trajectory library ──────────────────────────────
# Joint limits (rad) for quick reference when tuning control points:
#   Hip_Pitch  : [-3.0, 2.21]    Hip_Roll  : [-0.4, 1.57]
#   Hip_Yaw    : [-1.0, 1.0]     Knee_Pitch: [0.0, 2.23]
#   Ankle_Pitch: [-0.87, 0.345]  Ankle_Roll: [-0.345, 0.345]
#
# Each entry maps joint_name → (P0, P1, P2, P3) scalars in radians.

KICK_TRAJECTORIES: dict[str, dict[str, tuple[float, float, float, float]]] = {
  # Hip cocks to -0.8, drives forward to 1.3 rad; knee snaps near-straight.
  "snap": {
    "Left_Hip_Pitch": (0.0, -0.8, 1.3, 0.0),
    "Left_Knee_Pitch": (0.0, 1.4, 0.05, 0.0),
    "Left_Ankle_Pitch": (0.0, -0.6, 0.3, 0.0),
  },
  # Hip drives to 2.1 rad (near its 2.21 limit); leg mostly straight at apex.
  "high": {
    "Left_Hip_Pitch": (0.0, -0.4, 2.1, 0.0),
    "Left_Knee_Pitch": (0.0, 1.6, 0.15, 0.0),
    "Left_Ankle_Pitch": (0.0, -0.3, 0.3, 0.0),
  },
  # Hip abduction arc; pitch carries foot clear of stance leg first.
  "side": {
    "Left_Hip_Pitch": (0.0, 0.2, 0.4, 0.0),
    "Left_Hip_Roll": (0.0, 0.5, 1.1, 0.0),
    "Left_Hip_Yaw": (0.0, 0.3, 0.5, 0.0),
    "Left_Knee_Pitch": (0.0, 1.0, 0.15, 0.0),
    "Left_Ankle_Roll": (0.0, 0.1, 0.2, 0.0),
  },
  # Deep hip extension (-2.3 rad); heel strike.
  "back": {
    "Left_Hip_Pitch": (0.0, -0.3, -2.3, 0.0),
    "Left_Knee_Pitch": (0.0, 1.8, 0.2, 0.0),
    "Left_Ankle_Pitch": (0.0, -0.4, -0.75, 0.0),
  },
  # Short forward arc (0.7 rad), fast; ball-tap or close-range pass.
  "chip": {
    "Left_Hip_Pitch": (0.0, -0.3, 0.7, 0.0),
    "Left_Knee_Pitch": (0.0, 0.6, 0.05, 0.0),
    "Left_Ankle_Pitch": (0.0, -0.3, 0.2, 0.0),
  },
}


# ─────────────────────────── Bézier maths ────────────────────────────────────


def _make_ctrl_tensor(
  joints: dict[str, tuple[float, float, float, float]],
  device: torch.device | str,
) -> torch.Tensor:
  """Build a [4, J] control-point tensor from a joint dict."""
  pts = list(joints.values())
  # Row i = control point i across all J joints.
  return torch.tensor(
    [[p[i] for p in pts] for i in range(4)],
    dtype=torch.float32,
    device=device,
  )


def cubic_bezier_batch(s: torch.Tensor, ctrl: torch.Tensor) -> torch.Tensor:
  """Evaluate a cubic Bézier for a batch of phases.

  Args:
      s: Phase values in ``[0, 1]``, shape ``[B]``.
      ctrl: Control points, shape ``[4, J]``.

  Returns:
      Joint target angles, shape ``[B, J]``.
  """
  s = s.clamp(0.0, 1.0).unsqueeze(-1)  # [B, 1]
  p0, p1, p2, p3 = ctrl[0], ctrl[1], ctrl[2], ctrl[3]  # each [J]
  return (
    (1 - s) ** 3 * p0 + 3 * (1 - s) ** 2 * s * p1 + 3 * (1 - s) * s**2 * p2 + s**3 * p3
  )  # [B, J]


# ─────────────────────────── observation term ─────────────────────────────────


class kick_prior_target:
  """Bézier kick-prior joint targets at the current gait phase.

  Returns ``[B, J]`` target angles (radians) for the kick joints, evaluated
  at the shared open-loop gait phase.  Feed this to the actor so the policy
  can learn a residual:

      ``action_applied = kick_prior_target(phase) + policy_output``

  After ``drop_step`` steps the signal fades to zero over ``fade_steps``,
  keeping the observation dimension fixed while allowing the policy to
  graduate away from the prior.
  """

  def __init__(self, cfg: ObservationTermCfg, env: ManagerBasedRlEnv) -> None:
    del cfg
    self._env = env
    self._ctrl: dict[str, torch.Tensor] = {}

  def _ctrl_for(self, kick: str) -> torch.Tensor:
    if kick not in self._ctrl:
      self._ctrl[kick] = _make_ctrl_tensor(KICK_TRAJECTORIES[kick], self._env.device)
    return self._ctrl[kick]

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    kick: str = "snap",
    period: float = 1.5,
    command_name: str = "twist",
    command_threshold: float = 0.05,
    drop_step: int = 8_000 * 24,
    fade_steps: int = 2_000 * 24,
  ) -> torch.Tensor:
    scale = gait_scale(env.common_step_counter, drop_step, fade_steps)
    phase, _ = advance_gait_phase(env, period, command_name, command_threshold)
    targets = cubic_bezier_batch(phase, self._ctrl_for(kick))  # [B, J]
    if scale == 0.0:
      return torch.zeros_like(targets)
    return targets if scale == 1.0 else targets * scale

  def reset(self, env_ids: torch.Tensor | slice | None = None) -> None:
    del env_ids  # Phase reset is handled by gait_cycle.


# ─────────────────────────── reward term ──────────────────────────────────────


class kick_prior_tracking:
  """Reward for tracking the Bézier kick-prior trajectory.

  At each step, evaluates the prior at the current gait phase to get target
  joint angles, then rewards proximity with a Gaussian kernel (same form as
  ``track_linear_velocity``):

      ``r = exp(-||q_actual - q_prior||² / std²)``

  Gated by command magnitude (zero reward when standing still) and the same
  drop/fade curriculum as ``feet_gait``.

  Typical ``std`` values: ``0.3`` rad for loose shaping, ``0.1`` for tight
  imitation.  Anneal weight in the config rather than here.
  """

  def __init__(self, cfg: RewardTermCfg, env: ManagerBasedRlEnv) -> None:
    kick: str = cfg.params.get("kick", "snap")
    asset: Entity = env.scene[cfg.params["asset_cfg"].name]
    joint_names = list(KICK_TRAJECTORIES[kick].keys())
    _, self._joint_ids = asset.find_joints(joint_names)
    self._ctrl = _make_ctrl_tensor(KICK_TRAJECTORIES[kick], env.device)

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    std: float,
    kick: str = "snap",
    period: float = 1.5,
    command_name: str = "twist",
    command_threshold: float = 0.05,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
    drop_step: int = 8_000 * 24,
    fade_steps: int = 2_000 * 24,
  ) -> torch.Tensor:
    scale = gait_scale(env.common_step_counter, drop_step, fade_steps)
    if scale == 0.0:
      return torch.zeros(env.num_envs, device=env.device)

    phase, moving = advance_gait_phase(env, period, command_name, command_threshold)
    targets = cubic_bezier_batch(phase, self._ctrl)  # [B, J]

    asset: Entity = env.scene[asset_cfg.name]
    actual = asset.data.joint_pos[:, self._joint_ids]  # [B, J]

    error_sq = torch.sum(torch.square(targets - actual), dim=-1)  # [B]
    reward = torch.exp(-error_sq / std**2) * moving.float() * scale
    env.extras["log"]["Metrics/kick_prior_tracking"] = reward.mean()
    return reward

  def reset(self, env_ids: torch.Tensor) -> None:
    del env_ids

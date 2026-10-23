"""Left-right symmetry augmentation for NuBots K1 walk (66-D actor / 16-D action)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch
from tensordict import TensorDict

if TYPE_CHECKING:
  from rsl_rl.env import VecEnv

# NuBots actor obs layout (concatenated terms):
#   projected_gravity(3), base_ang_vel(3), parameter_walk_cmd(12),
#   joint_pos(16), joint_vel(16), last_action(16)  → 66
# Critic adds base_lin_vel(3) + base_height(1) → 70
ACTOR_DIM = 66
CRITIC_DIM = 70

# Type-major L/R joint pairs: (L, R) at indices ...
_JOINT_PAIRS = ((0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13), (14, 15))
# Roll / yaw joints flip sign under sagittal mirror; pitch joints do not.
_NEGATE_JOINT_PAIRS = frozenset({(4, 5), (6, 7), (8, 9), (14, 15)})


def mirror_joints16(x: torch.Tensor) -> torch.Tensor:
  """Mirror 16-D leg (+ shoulder) blocks in NuBots type-major L/R order."""
  out = torch.empty_like(x)
  for i, j in _JOINT_PAIRS:
    if (i, j) in _NEGATE_JOINT_PAIRS:
      out[..., i] = -x[..., j]
      out[..., j] = -x[..., i]
    else:
      out[..., i] = x[..., j]
      out[..., j] = x[..., i]
  return out


def _mirror_actor_obs(x: torch.Tensor) -> torch.Tensor:
  """Mirror a flat 66-D NuBots actor observation."""
  m = x.clone()
  # projected_gravity
  m[..., 1] = -x[..., 1]
  # base_ang_vel
  m[..., 3] = -x[..., 3]
  m[..., 5] = -x[..., 5]
  # parameter_walk_cmd (12-D)
  src = x[..., 6:18]
  pw = src.clone()
  pw[..., 1] = -src[..., 1]  # vy
  pw[..., 2] = -src[..., 2]  # yaw
  pw[..., 4] = -src[..., 5]  # foot_yaw_L ← −R
  pw[..., 5] = -src[..., 4]  # foot_yaw_R ← −L
  pw[..., 7] = -src[..., 7]  # body_roll
  pw[..., 9] = -src[..., 9]  # feet_off_y
  pw[..., 10] = -src[..., 10]  # cos(2πφ) phase +0.5
  pw[..., 11] = -src[..., 11]  # sin(2πφ)
  m[..., 6:18] = pw
  m[..., 18:34] = mirror_joints16(x[..., 18:34])
  m[..., 34:50] = mirror_joints16(x[..., 34:50])
  m[..., 50:66] = mirror_joints16(x[..., 50:66])
  return m


def _mirror_critic_obs(x: torch.Tensor) -> torch.Tensor:
  """Mirror a flat 70-D NuBots critic observation."""
  actor_m = _mirror_actor_obs(x[..., :ACTOR_DIM])
  lin_vel = x[..., ACTOR_DIM : ACTOR_DIM + 3].clone()
  lin_vel[..., 1] = -x[..., ACTOR_DIM + 1]
  height = x[..., ACTOR_DIM + 3 : ACTOR_DIM + 4]
  return torch.cat([actor_m, lin_vel, height], dim=-1)


def _augment_obs(obs: TensorDict) -> TensorDict:
  actor = obs["actor"]
  critic = obs["critic"]
  actor_m = _mirror_actor_obs(actor)
  critic_m = _mirror_critic_obs(critic)
  batch = actor.shape[0]
  return TensorDict(
    {
      "actor": torch.cat([actor, actor_m], dim=0),
      "critic": torch.cat([critic, critic_m], dim=0),
    },
    batch_size=[batch * 2],
  )


def nubots_symmetry(
  env: VecEnv,
  obs: TensorDict | None,
  actions: torch.Tensor | None = None,
) -> tuple[TensorDict | None, torch.Tensor | None]:
  """rsl_rl symmetry callback for NuBots K1 walk.

  Doubles the batch with a sagittal-plane mirror. Supports obs-only,
  action-only, or joint augmentation depending on which inputs are provided.
  """
  del env  # unused; kept for rsl_rl API compatibility

  if obs is not None and actions is not None:
    return _augment_obs(obs), torch.cat([actions, mirror_joints16(actions)], dim=0)

  if obs is not None:
    return _augment_obs(obs), None

  if actions is not None:
    return None, torch.cat([actions, mirror_joints16(actions)], dim=0)

  raise ValueError("nubots_symmetry requires obs and/or actions")

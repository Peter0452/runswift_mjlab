"""Tests for NuBots left-right symmetry augmentation."""

from __future__ import annotations

import torch
from tensordict import TensorDict

from mjlab.tasks.velocity.mdp.symmetry import (
  ACTOR_DIM,
  CRITIC_DIM,
  _mirror_actor_obs,
  _mirror_critic_obs,
  mirror_joints16,
  nubots_symmetry,
)


def test_mirror_joints16_involution() -> None:
  x = torch.randn(8, 16)
  mm = mirror_joints16(mirror_joints16(x))
  assert torch.allclose(x, mm, atol=1e-6)


def test_mirror_actor_obs_involution() -> None:
  x = torch.randn(4, ACTOR_DIM)
  mm = _mirror_actor_obs(_mirror_actor_obs(x))
  assert torch.allclose(x, mm, atol=1e-6)


def test_mirror_critic_obs_involution() -> None:
  x = torch.randn(4, CRITIC_DIM)
  mm = _mirror_critic_obs(_mirror_critic_obs(x))
  assert torch.allclose(x, mm, atol=1e-6)


def test_nubots_symmetry_doubles_batch() -> None:
  actor = torch.randn(3, ACTOR_DIM)
  critic = torch.randn(3, CRITIC_DIM)
  actions = torch.randn(3, 16)
  obs = TensorDict({"actor": actor, "critic": critic}, batch_size=[3])

  obs_aug, act_aug = nubots_symmetry(None, obs, actions)  # type: ignore[arg-type]
  assert obs_aug is not None and act_aug is not None
  assert obs_aug["actor"].shape == (6, ACTOR_DIM)
  assert obs_aug["critic"].shape == (6, CRITIC_DIM)
  assert act_aug.shape == (6, 16)
  assert torch.allclose(obs_aug["actor"][:3], actor)
  assert torch.allclose(act_aug[:3], actions)


def test_roll_joints_negate_under_mirror() -> None:
  x = torch.zeros(1, 16)
  x[..., 4] = 0.3  # L shoulder roll
  x[..., 5] = -0.2  # R shoulder roll
  m = mirror_joints16(x)
  assert abs(m[..., 4].item() - 0.2) < 1e-6
  assert abs(m[..., 5].item() - (-0.3)) < 1e-6

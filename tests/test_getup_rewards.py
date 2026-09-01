"""Tests for get-up reward helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

import torch

from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.tasks.getup.mdp.rewards import (
  standing_bonus,
  upright,
  upright_climb,
)


def _identity_quat(batch: int) -> torch.Tensor:
  q = torch.zeros(batch, 4)
  q[:, 0] = 1.0
  return q


def _make_asset(
  *,
  batch: int = 1,
  root_z: float = 0.57,
  projected_gravity_b: torch.Tensor | None = None,
  lin_vel: torch.Tensor | None = None,
  ang_vel: torch.Tensor | None = None,
) -> MagicMock:
  asset = MagicMock()
  if projected_gravity_b is None:
    # Fully upright: gravity in body frame points -z.
    projected_gravity_b = torch.tensor([[0.0, 0.0, -1.0]]).expand(batch, 3).clone()
  asset.data.projected_gravity_b = projected_gravity_b
  pos = torch.zeros(batch, 3)
  pos[:, 2] = root_z
  asset.data.root_link_pos_w = pos
  if lin_vel is None:
    lin_vel = torch.zeros(batch, 3)
  asset.data.root_link_lin_vel_w = lin_vel
  if ang_vel is None:
    ang_vel = torch.zeros(batch, 3)
  asset.data.root_link_ang_vel_w = ang_vel
  return asset


def _make_env(asset: MagicMock) -> MagicMock:
  env = MagicMock()
  env.scene = {"robot": asset}
  env.device = "cpu"
  return env


def test_standing_bonus_requires_upright_height_and_slow() -> None:
  upright_asset = _make_asset(root_z=0.57)
  env = _make_env(upright_asset)
  assert standing_bonus(env, stand_height=0.57).item() == 1.0

  # High but horizontal (downward-dog style) must not count.
  dog = _make_asset(
    root_z=0.57,
    projected_gravity_b=torch.tensor([[1.0, 0.0, 0.0]]),
  )
  assert standing_bonus(_make_env(dog), stand_height=0.57).item() == 0.0

  # Upright but too fast.
  fast = _make_asset(root_z=0.57, lin_vel=torch.tensor([[1.0, 0.0, 0.0]]))
  assert standing_bonus(_make_env(fast), stand_height=0.57).item() == 0.0


def test_upright_climb_gates_height_by_orientation() -> None:
  upright_asset = _make_asset(root_z=0.4)
  climb = upright_climb(_make_env(upright_asset), stand_height=0.57)
  assert torch.isclose(climb, torch.tensor(0.4)).item()

  horizontal = _make_asset(
    root_z=0.4,
    projected_gravity_b=torch.tensor([[0.0, 1.0, 0.0]]),
  )
  climb_h = upright_climb(_make_env(horizontal), stand_height=0.57)
  assert torch.isclose(climb_h, torch.tensor(0.0)).item()


def test_upright_reward_matches_neg_gravity_z() -> None:
  asset = _make_asset(
    projected_gravity_b=torch.tensor([[0.0, 0.0, -0.5]]),
  )
  assert torch.isclose(upright(_make_env(asset)), torch.tensor(0.5)).item()


def test_standing_bonus_term_cfg_callable() -> None:
  """Smoke: RewardTermCfg can wrap standing_bonus like the env does."""
  cfg = RewardTermCfg(
    func=standing_bonus,
    weight=10.0,
    params={"stand_height": 0.57, "asset_cfg": SceneEntityCfg("robot")},
  )
  assert cfg.weight == 10.0

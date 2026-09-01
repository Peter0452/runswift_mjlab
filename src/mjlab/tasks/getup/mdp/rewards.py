"""Reward functions for discovery-based humanoid get-up.

Port of ``booster_train`` ``k1_getup/rewards.py``. One policy rises from any
fallen posture (supine / prone / side). Motion is not scripted — it emerges from
standing bonus + upright-gated height climb + time pressure + light
regularization.

Body-frame projected gravity encodes posture:
  standing  -> proj_grav_b ~ ( 0, 0, -1)
  supine    -> proj_grav_b ~ (-1, 0,  0)   (face up)
  prone     -> proj_grav_b ~ (+1, 0,  0)   (face down)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from mjlab.entity import Entity
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_DEFAULT_ASSET_CFG = SceneEntityCfg("robot")


def _robot(env: ManagerBasedRlEnv, asset_cfg: SceneEntityCfg) -> Entity:
  return env.scene[asset_cfg.name]


def _upright_factor(asset: Entity) -> torch.Tensor:
  """0 when horizontal, 1 when fully upright."""
  return torch.clamp(-asset.data.projected_gravity_b[:, 2], min=0.0, max=1.0)


def _is_standing(asset: Entity, stand_height: float) -> torch.Tensor:
  """Upright AND base near standing height AND slow.

  Uses base height gated by uprightness so a butt-in-air downward-dog (pelvis
  high but body horizontal) does not count as standing.
  """
  upright = asset.data.projected_gravity_b[:, 2] < -0.9
  high = asset.data.root_link_pos_w[:, 2] > stand_height * 0.88
  slow = torch.linalg.norm(asset.data.root_link_lin_vel_w, dim=-1) < 0.6
  return upright & high & slow


def standing_bonus(
  env: ManagerBasedRlEnv,
  stand_height: float = 0.57,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Sparse reward for being in the standing state."""
  return _is_standing(_robot(env, asset_cfg), stand_height).float()


class head_height:
  """Dense head-above-feet height (HoST-style), capped at ``max_diff``.

  Low in a downward-dog (head near ground between feet) and high only when the
  body is genuinely upright.
  """

  def __init__(self, cfg: RewardTermCfg, env: ManagerBasedRlEnv):
    asset_cfg: SceneEntityCfg = cfg.params.get("asset_cfg", _DEFAULT_ASSET_CFG)
    asset: Entity = env.scene[asset_cfg.name]
    head_names = cfg.params.get("head_body_names", ("Head_2",))
    foot_names = cfg.params.get(
      "foot_body_names", ("left_foot_link", "right_foot_link")
    )
    self._head_ids, _ = asset.find_bodies(head_names, preserve_order=True)
    self._foot_ids, _ = asset.find_bodies(foot_names, preserve_order=True)

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    max_diff: float = 0.7,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
    head_body_names: tuple[str, ...] = ("Head_2",),
    foot_body_names: tuple[str, ...] = ("left_foot_link", "right_foot_link"),
  ) -> torch.Tensor:
    del head_body_names, foot_body_names
    asset = _robot(env, asset_cfg)
    head_z = asset.data.body_link_pos_w[:, self._head_ids[0], 2]
    feet_z = asset.data.body_link_pos_w[:, self._foot_ids, 2].mean(dim=1)
    return torch.clamp(head_z - feet_z, min=0.0, max=max_diff)


def upright_climb(
  env: ManagerBasedRlEnv,
  stand_height: float = 0.57,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Primary dense climb: base height gated by uprightness.

  Near zero in a downward-dog (high pelvis, horizontal torso).
  """
  asset = _robot(env, asset_cfg)
  base_h = torch.clamp(asset.data.root_link_pos_w[:, 2], min=0.0, max=stand_height)
  return base_h * _upright_factor(asset)


def upright(
  env: ManagerBasedRlEnv,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Reward gravity-aligned torso (1 upright, 0 horizontal)."""
  return torch.clamp(-_robot(env, asset_cfg).data.projected_gravity_b[:, 2], min=0.0)


def not_standing_time_penalty(
  env: ManagerBasedRlEnv,
  stand_height: float = 0.57,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """1.0 every step while not standing (weight ramped by curriculum)."""
  return (~_is_standing(_robot(env, asset_cfg), stand_height)).float()


class rising_velocity:
  """Reward upward head velocity, capped so violent flings are not farmed."""

  def __init__(self, cfg: RewardTermCfg, env: ManagerBasedRlEnv):
    asset_cfg: SceneEntityCfg = cfg.params.get("asset_cfg", _DEFAULT_ASSET_CFG)
    asset: Entity = env.scene[asset_cfg.name]
    head_names = cfg.params.get("head_body_names", ("Head_2",))
    self._head_ids, _ = asset.find_bodies(head_names, preserve_order=True)

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    max_vel: float = 1.0,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
    head_body_names: tuple[str, ...] = ("Head_2",),
  ) -> torch.Tensor:
    del head_body_names
    asset = _robot(env, asset_cfg)
    head_vel_z = asset.data.body_link_lin_vel_w[:, self._head_ids[0], 2]
    return torch.clamp(head_vel_z, min=0.0, max=max_vel)


def standing_stability(
  env: ManagerBasedRlEnv,
  stand_height: float = 0.57,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """When standing, reward low base velocity (hold the pose)."""
  asset = _robot(env, asset_cfg)
  standing = _is_standing(asset, stand_height).float()
  vel = torch.sum(torch.square(asset.data.root_link_lin_vel_w[:, :2]), dim=-1)
  vel = vel + torch.sum(torch.square(asset.data.root_link_ang_vel_w), dim=-1)
  return torch.exp(-1.0 * vel) * standing


class feet_under_body:
  """Reward feet below the trunk, gated by uprightness."""

  def __init__(self, cfg: RewardTermCfg, env: ManagerBasedRlEnv):
    asset_cfg: SceneEntityCfg = cfg.params.get("asset_cfg", _DEFAULT_ASSET_CFG)
    asset: Entity = env.scene[asset_cfg.name]
    trunk_names = cfg.params.get("trunk_body_names", ("Trunk",))
    foot_names = cfg.params.get(
      "foot_body_names", ("left_foot_link", "right_foot_link")
    )
    self._trunk_ids, _ = asset.find_bodies(trunk_names, preserve_order=True)
    self._foot_ids, _ = asset.find_bodies(foot_names, preserve_order=True)

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
    trunk_body_names: tuple[str, ...] = ("Trunk",),
    foot_body_names: tuple[str, ...] = ("left_foot_link", "right_foot_link"),
  ) -> torch.Tensor:
    del trunk_body_names, foot_body_names
    asset = _robot(env, asset_cfg)
    trunk_h = asset.data.body_link_pos_w[:, self._trunk_ids[0], 2]
    feet_h = asset.data.body_link_pos_w[:, self._foot_ids, 2].mean(dim=1)
    return torch.clamp(trunk_h - feet_h, min=0.0) * _upright_factor(asset)


class arms_at_side:
  """When standing, reward arm joints near default (arms-down) pose.

  Unlike the Isaac port (target=0), this uses the entity default joint pose so
  K1 shoulder-roll defaults (~±1.45) count as arms at sides.
  """

  def __init__(self, cfg: RewardTermCfg, env: ManagerBasedRlEnv):
    asset_cfg: SceneEntityCfg = cfg.params["asset_cfg"]
    asset: Entity = env.scene[asset_cfg.name]
    default_joint_pos = asset.data.default_joint_pos
    assert default_joint_pos is not None
    self._default = default_joint_pos

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    asset_cfg: SceneEntityCfg,
    stand_height: float = 0.57,
  ) -> torch.Tensor:
    asset = _robot(env, asset_cfg)
    standing = _is_standing(asset, stand_height).float()
    jp = asset.data.joint_pos[:, asset_cfg.joint_ids]
    desired = self._default[:, asset_cfg.joint_ids]
    err = torch.sum(torch.square(jp - desired), dim=1)
    return torch.exp(-err) * standing

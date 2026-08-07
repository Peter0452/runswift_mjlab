"""Velocity-task event terms."""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from mjlab.entity import Entity
from mjlab.envs.mdp.events import resolve_env_ids
from mjlab.managers.event_manager import EventTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.utils.lab_api.math import sample_uniform
from mjlab.utils.string import resolve_expr

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_DEFAULT_ASSET_CFG = SceneEntityCfg("robot")


class reset_joints_from_pose_catalog:
  """Reset joints by sampling a discrete pose, then adding uniform noise.

  Each pose is a joint-name pattern map (same format as entity init_state).
  ``base_heights`` are absolute root z values for feet-on-ground; the term
  applies ``height - default_root_z`` on top of whatever ``reset_base`` wrote
  so taller poses do not sink into the ground.
  """

  def __init__(self, cfg: EventTermCfg, env: ManagerBasedRlEnv):
    asset_cfg: SceneEntityCfg = cfg.params.get("asset_cfg", _DEFAULT_ASSET_CFG)
    asset: Entity = env.scene[asset_cfg.name]
    poses: list[dict[str, float]] = cfg.params["poses"]
    base_heights: list[float] = cfg.params["base_heights"]
    if len(poses) != len(base_heights):
      raise ValueError("poses and base_heights must have the same length.")
    if len(poses) == 0:
      raise ValueError("poses must be non-empty.")

    joint_poses = [
      torch.tensor(
        resolve_expr(pose, asset.joint_names, 0.0),
        device=env.device,
        dtype=torch.float32,
      )
      for pose in poses
    ]
    self.poses = torch.stack(joint_poses, dim=0)  # [P, J]

    default_root = asset.data.default_root_state
    assert default_root is not None
    default_z = float(default_root[0, 2].item())
    self.delta_z = torch.tensor(
      [h - default_z for h in base_heights],
      device=env.device,
      dtype=torch.float32,
    )

    probs = cfg.params.get("probabilities")
    if probs is None:
      self.probabilities = torch.full(
        (len(poses),), 1.0 / len(poses), device=env.device, dtype=torch.float32
      )
    else:
      self.probabilities = torch.tensor(probs, device=env.device, dtype=torch.float32)
      self.probabilities = self.probabilities / self.probabilities.sum()

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    env_ids: torch.Tensor | None,
    poses: list[dict[str, float]],
    base_heights: list[float],
    position_range: tuple[float, float] = (0.0, 0.0),
    velocity_range: tuple[float, float] = (0.0, 0.0),
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
    probabilities: list[float] | None = None,
  ) -> None:
    del poses, base_heights, probabilities  # Resolved in __init__.

    env_ids = resolve_env_ids(env, env_ids)
    asset: Entity = env.scene[asset_cfg.name]
    n = len(env_ids)

    pose_ids = torch.multinomial(self.probabilities, n, replacement=True)

    joint_pos = self.poses[pose_ids].clone()
    joint_ids = asset_cfg.joint_ids
    if isinstance(joint_ids, list):
      joint_ids = torch.tensor(joint_ids, device=env.device)
      joint_pos = joint_pos[:, joint_ids]
    elif joint_ids != slice(None):
      joint_pos = joint_pos[:, joint_ids]

    joint_pos += sample_uniform(*position_range, joint_pos.shape, env.device)
    soft_limits = asset.data.soft_joint_pos_limits
    assert soft_limits is not None
    joint_pos_limits = soft_limits[env_ids][:, joint_ids]
    joint_pos = joint_pos.clamp_(joint_pos_limits[..., 0], joint_pos_limits[..., 1])

    default_joint_vel = asset.data.default_joint_vel
    assert default_joint_vel is not None
    joint_vel = default_joint_vel[env_ids][:, joint_ids].clone()
    joint_vel += sample_uniform(*velocity_range, joint_vel.shape, env.device)

    asset.write_joint_state_to_sim(
      joint_pos.view(n, -1),
      joint_vel.view(n, -1),
      env_ids=env_ids,
      joint_ids=joint_ids,
    )

    # Lift/drop root so the sampled pose's feet stay near the ground.
    q_adr = asset.indexing.free_joint_q_adr
    root_pose = asset.data.data.qpos[env_ids[:, None], q_adr].clone()
    root_pose[:, 2] += self.delta_z[pose_ids]
    asset.write_root_link_pose_to_sim(root_pose, env_ids=env_ids)


def set_joint_position_targets_to_default(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> None:
  """Set PD position targets to the entity default joint pose.

  Needed when the action only commands a joint subset (e.g. K1 legs): other
  actuated joints otherwise keep ``joint_pos_target=0`` after ``clear_state``
  and drift away from the keyframe (tucked arms/head).
  """
  env_ids = resolve_env_ids(env, env_ids)
  asset: Entity = env.scene[asset_cfg.name]
  default_joint_pos = asset.data.default_joint_pos
  assert default_joint_pos is not None

  joint_ids = asset_cfg.joint_ids
  if isinstance(joint_ids, list):
    joint_ids = torch.tensor(joint_ids, device=env.device)

  targets = default_joint_pos[env_ids][:, joint_ids].clone()
  asset.set_joint_position_target(targets, joint_ids=joint_ids, env_ids=env_ids)

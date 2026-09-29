"""Tracking-scene events."""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from mjlab.entity import Entity
from mjlab.envs.mdp.events import resolve_env_ids
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.utils.lab_api.math import quat_from_euler_xyz

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_DEFAULT_GOAL_CFG = SceneEntityCfg("goal")


def goal_yaw_facing_origin(goal_xy: torch.Tensor) -> torch.Tensor:
  """Yaw that points the goal mouth (local +y) at the env origin.

  ``goal_xy`` is env-local, shape (N, 2). The returned yaw is in radians.
  """
  toward_origin = -goal_xy
  toward_origin = toward_origin / torch.linalg.norm(
    toward_origin, dim=-1, keepdim=True
  ).clamp(min=1.0e-6)
  return torch.atan2(-toward_origin[:, 0], toward_origin[:, 1])


def place_goal_at_command(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  command_name: str = "goal",
  asset_cfg: SceneEntityCfg = _DEFAULT_GOAL_CFG,
) -> None:
  """Put the goal mouth on the sampled target, facing the env origin."""
  env_ids = resolve_env_ids(env, env_ids)
  if len(env_ids) == 0:
    return
  goal_xy = env.command_manager.get_command(command_name)
  assert goal_xy is not None
  goal_xy = goal_xy[env_ids, :2]
  goal: Entity = env.scene[asset_cfg.name]
  pos = torch.zeros(len(env_ids), 3, device=env.device)
  pos[:, :2] = goal_xy + env.scene.env_origins[env_ids, :2]
  yaw = goal_yaw_facing_origin(goal_xy)
  zeros = torch.zeros_like(yaw)
  quat = quat_from_euler_xyz(zeros, zeros, yaw)
  goal.write_mocap_pose_to_sim(torch.cat([pos, quat], dim=-1), env_ids=env_ids)

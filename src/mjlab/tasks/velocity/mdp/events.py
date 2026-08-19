"""Velocity-task event terms."""

from __future__ import annotations

import math
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


def _interval_steps(interval_s: float, step_dt: float) -> int:
  """Booster Gym uses ``ceil(interval / dt)`` control-step counts."""
  return max(1, math.ceil(interval_s / step_dt))


class booster_kick_robots:
  """Booster T1 velocity kick: additive Gaussian noise every ``kick_interval_s``.

  Matches ``booster_gym/envs/t1.py`` ``_kick_robots`` and ``T1.yaml``:
  ``kick_interval_s=2``, lin vel ``N(0, 0.1)``, ang vel ``N(0, 0.02)``.
  """

  def __init__(self, cfg: EventTermCfg, env: ManagerBasedRlEnv):
    self._asset: Entity = env.scene[cfg.params["asset_cfg"].name]
    self._interval_steps = _interval_steps(
      cfg.params.get("kick_interval_s", 2.0), env.step_dt
    )
    self._lin_std = float(cfg.params.get("kick_lin_vel_std", 0.1))
    self._ang_std = float(cfg.params.get("kick_ang_vel_std", 0.02))

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    env_ids: torch.Tensor | None,
    kick_interval_s: float = 2.0,
    kick_lin_vel_std: float = 0.1,
    kick_ang_vel_std: float = 0.02,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
  ) -> None:
    del env_ids, kick_interval_s, kick_lin_vel_std, kick_ang_vel_std, asset_cfg
    if env.common_step_counter % self._interval_steps != 0:
      return
    vel_w = self._asset.data.root_link_vel_w.clone()
    vel_w[:, :3] += torch.randn_like(vel_w[:, :3]) * self._lin_std
    vel_w[:, 3:] += torch.randn_like(vel_w[:, 3:]) * self._ang_std
    self._asset.write_root_link_velocity_to_sim(vel_w)


class booster_push_robots:
  """Booster T1 sustained trunk push: Gaussian wrench held for ``push_duration_s``.

  Matches ``booster_gym/envs/t1.py`` ``_push_robots`` and ``T1.yaml``:
  resample every ``push_interval_s=5``, hold ``push_duration_s=1``, force
  ``N(0, 10)`` N, torque ``N(0, 2)`` Nm (body frame, like Isaac LOCAL_SPACE).
  """

  def __init__(self, cfg: EventTermCfg, env: ManagerBasedRlEnv):
    self._asset: Entity = env.scene[cfg.params["asset_cfg"].name]
    self._body_ids = cfg.params["asset_cfg"].body_ids
    self._device = env.device
    self._num_envs = env.num_envs
    self._num_bodies = (
      len(self._body_ids)
      if isinstance(self._body_ids, list)
      else self._asset.num_bodies
    )
    self._interval_steps = _interval_steps(
      cfg.params.get("push_interval_s", 5.0), env.step_dt
    )
    self._duration_steps = _interval_steps(
      cfg.params.get("push_duration_s", 1.0), env.step_dt
    )
    self._force_std = float(cfg.params.get("push_force_std", 10.0))
    self._torque_std = float(cfg.params.get("push_torque_std", 2.0))
    self._forces = torch.zeros(self._num_envs, self._num_bodies, 3, device=self._device)
    self._torques = torch.zeros(
      self._num_envs, self._num_bodies, 3, device=self._device
    )

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    env_ids: torch.Tensor | None,
    push_interval_s: float = 5.0,
    push_duration_s: float = 1.0,
    push_force_std: float = 10.0,
    push_torque_std: float = 2.0,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
  ) -> None:
    del (
      env_ids,
      push_interval_s,
      push_duration_s,
      push_force_std,
      push_torque_std,
      asset_cfg,
    )
    phase = env.common_step_counter % self._interval_steps
    if phase == 0:
      self._forces = torch.randn_like(self._forces) * self._force_std
      self._torques = torch.randn_like(self._torques) * self._torque_std
    elif phase == self._duration_steps:
      self._forces.zero_()
      self._torques.zero_()
    self._asset.write_external_wrench_to_sim(
      self._forces, self._torques, body_ids=self._body_ids
    )

  def reset(self, env_ids: torch.Tensor | slice | None = None) -> None:
    if env_ids is None:
      self._forces.zero_()
      self._torques.zero_()
      return
    self._forces[env_ids] = 0.0
    self._torques[env_ids] = 0.0

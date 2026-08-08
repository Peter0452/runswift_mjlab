from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import torch

from mjlab.entity import Entity
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.sensor import BuiltinSensor, ContactSensor
from mjlab.sensor.terrain_height_sensor import TerrainHeightSensor
from mjlab.tasks.velocity.mdp.observations import advance_gait_phase, gait_scale
from mjlab.tasks.velocity.mdp.terrain_utils import terrain_normal_from_sensors
from mjlab.utils.lab_api.math import quat_apply, quat_apply_inverse
from mjlab.utils.lab_api.string import (
  resolve_matching_names_values,
)

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv
  from mjlab.viewer.debug_visualizer import DebugVisualizer


_DEFAULT_ASSET_CFG = SceneEntityCfg("robot")


def track_linear_velocity(
  env: ManagerBasedRlEnv,
  std: float,
  command_name: str,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Reward for tracking the commanded base linear velocity.

  The commanded z velocity is assumed to be zero.
  """
  asset: Entity = env.scene[asset_cfg.name]
  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  actual = asset.data.root_link_lin_vel_b
  xy_error = torch.sum(torch.square(command[:, :2] - actual[:, :2]), dim=1)
  z_error = torch.square(actual[:, 2])
  lin_vel_error = xy_error + z_error
  return torch.exp(-lin_vel_error / std**2)


def track_angular_velocity(
  env: ManagerBasedRlEnv,
  std: float,
  command_name: str,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Reward heading error for heading-controlled envs, angular velocity for others.

  The commanded xy angular velocities are assumed to be zero.
  """
  asset: Entity = env.scene[asset_cfg.name]
  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  actual = asset.data.root_link_ang_vel_b
  z_error = torch.square(command[:, 2] - actual[:, 2])
  xy_error = torch.sum(torch.square(actual[:, :2]), dim=1)
  ang_vel_error = z_error + xy_error
  return torch.exp(-ang_vel_error / std**2)


class upright:
  """Reward for keeping the base upright.

  Without ``terrain_sensor_names``, penalizes tilt relative to world up (correct for
  flat ground).

  With ``terrain_sensor_names``, penalizes tilt relative to the terrain surface normal.
  """

  def __init__(self, cfg: RewardTermCfg, env: ManagerBasedRlEnv):
    self._terrain_sensor_names: tuple[str, ...] | None = cfg.params.get(
      "terrain_sensor_names"
    )
    self._debug_vis_enabled = True
    self._env = env
    self._asset_cfg: SceneEntityCfg = cfg.params.get("asset_cfg", _DEFAULT_ASSET_CFG)

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    std: float,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
    terrain_sensor_names: tuple[str, ...] | None = None,
  ) -> torch.Tensor:
    asset: Entity = env.scene[asset_cfg.name]

    if asset_cfg.body_ids:
      body_quat_w = asset.data.body_link_quat_w[:, asset_cfg.body_ids, :]  # [B, N, 4]
      body_quat_w = body_quat_w.squeeze(1)  # [B, 4]
    else:
      body_quat_w = asset.data.root_link_quat_w  # [B, 4]

    if terrain_sensor_names is not None:
      terrain_normal = terrain_normal_from_sensors(env, terrain_sensor_names)  # [B, 3]
      # Project terrain normal into body frame. When aligned with the terrain surface
      # this should be (0, 0, 1); XY measures tilt.
      target_b = quat_apply_inverse(body_quat_w, terrain_normal)  # [B, 3]
      xy_squared = torch.sum(torch.square(target_b[:, :2]), dim=1)
    else:
      gravity_w = asset.data.gravity_vec_w  # [3]
      projected_gravity_b = quat_apply_inverse(body_quat_w, gravity_w)
      xy_squared = torch.sum(torch.square(projected_gravity_b[:, :2]), dim=1)

    return torch.exp(-xy_squared / std**2)

  def reset(self, env_ids: torch.Tensor) -> None:
    del env_ids  # Unused.

  def debug_vis(self, visualizer: DebugVisualizer) -> None:
    if not self._debug_vis_enabled or self._terrain_sensor_names is None:
      return

    env = self._env
    asset: Entity = env.scene[self._asset_cfg.name]

    env_indices = list(visualizer.get_env_indices(env.num_envs))
    if not env_indices:
      return

    terrain_normal = terrain_normal_from_sensors(env, self._terrain_sensor_names)
    if self._asset_cfg.body_ids:
      body_quat_w = asset.data.body_link_quat_w[:, self._asset_cfg.body_ids, :].squeeze(
        1
      )
    else:
      body_quat_w = asset.data.root_link_quat_w
    up_local = torch.tensor([0.0, 0.0, 1.0], device=env.device).expand_as(
      body_quat_w[:, :3]
    )
    body_up_w = quat_apply(body_quat_w, up_local)

    positions = asset.data.root_link_pos_w.cpu().numpy()
    offset = np.array([0.0, 0.3, 0.0])
    terrain_normal_np = terrain_normal.cpu().numpy()
    body_up_np = body_up_w.cpu().numpy()
    scale = 0.25

    for i in env_indices:
      origin = positions[i] + offset
      # Terrain normal (magenta).
      visualizer.add_arrow(
        start=origin,
        end=origin + terrain_normal_np[i] * scale,
        color=(0.8, 0.2, 0.8, 0.8),
        width=0.01,
      )
      # Body up (orange).
      visualizer.add_arrow(
        start=origin,
        end=origin + body_up_np[i] * scale,
        color=(1.0, 0.5, 0.0, 0.8),
        width=0.01,
      )


def self_collision_cost(
  env: ManagerBasedRlEnv,
  sensor_name: str,
  force_threshold: float = 10.0,
) -> torch.Tensor:
  """Penalize self-collisions.

  When the sensor provides force history (from ``history_length > 0``),
  counts substeps where any contact force exceeds *force_threshold*.
  Falls back to the instantaneous ``found`` count otherwise.
  """
  sensor: ContactSensor = env.scene[sensor_name]
  data = sensor.data
  if data.force_history is not None:
    # force_history: [B, N, H, 3]
    force_mag = torch.norm(data.force_history, dim=-1)  # [B, N, H]
    hit = (force_mag > force_threshold).any(dim=1)  # [B, H]
    return hit.sum(dim=-1).float()  # [B]
  assert data.found is not None
  return data.found.sum(dim=-1).float()


def body_angular_velocity_penalty(
  env: ManagerBasedRlEnv,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Penalize excessive body angular velocities."""
  asset: Entity = env.scene[asset_cfg.name]
  ang_vel = asset.data.body_link_ang_vel_w[:, asset_cfg.body_ids, :]
  ang_vel = ang_vel.squeeze(1)
  ang_vel_xy = ang_vel[:, :2]  # Don't penalize z-angular velocity.
  return torch.sum(torch.square(ang_vel_xy), dim=1)


def angular_momentum_penalty(
  env: ManagerBasedRlEnv,
  sensor_name: str,
) -> torch.Tensor:
  """Penalize whole-body angular momentum to encourage natural arm swing."""
  angmom_sensor: BuiltinSensor = env.scene[sensor_name]
  angmom = angmom_sensor.data
  angmom_magnitude_sq = torch.sum(torch.square(angmom), dim=-1)
  angmom_magnitude = torch.sqrt(angmom_magnitude_sq)
  env.extras["log"]["Metrics/angular_momentum_mean"] = torch.mean(angmom_magnitude)
  return angmom_magnitude_sq


def feet_air_time(
  env: ManagerBasedRlEnv,
  sensor_name: str,
  threshold_min: float = 0.05,
  threshold_max: float = 0.5,
  command_name: str | None = None,
  command_threshold: float = 0.5,
) -> torch.Tensor:
  """Reward feet air time."""
  sensor: ContactSensor = env.scene[sensor_name]
  sensor_data = sensor.data
  current_air_time = sensor_data.current_air_time
  assert current_air_time is not None
  in_range = (current_air_time > threshold_min) & (current_air_time < threshold_max)
  reward = torch.sum(in_range.float(), dim=1)
  in_air = current_air_time > 0
  num_in_air = torch.sum(in_air.float())
  mean_air_time = torch.sum(current_air_time * in_air.float()) / torch.clamp(
    num_in_air, min=1
  )
  env.extras["log"]["Metrics/air_time_mean"] = mean_air_time
  if command_name is not None:
    command = env.command_manager.get_command(command_name)
    if command is not None:
      linear_norm = torch.norm(command[:, :2], dim=1)
      angular_norm = torch.abs(command[:, 2])
      total_command = linear_norm + angular_norm
      scale = (total_command > command_threshold).float()
      reward *= scale
  return reward


def feet_clearance(
  env: ManagerBasedRlEnv,
  target_height: float,
  height_sensor_name: str,
  command_name: str | None = None,
  command_threshold: float = 0.01,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Penalize deviation from target clearance height, weighted by foot velocity."""
  asset: Entity = env.scene[asset_cfg.name]
  height_sensor = env.scene[height_sensor_name]
  assert isinstance(height_sensor, TerrainHeightSensor), (
    f"feet_clearance requires a TerrainHeightSensor, got {type(height_sensor).__name__}"
  )
  foot_height = height_sensor.data.heights  # [B, F]
  foot_vel_xy = asset.data.site_lin_vel_w[:, asset_cfg.site_ids, :2]  # [B, F, 2]
  vel_norm = torch.norm(foot_vel_xy, dim=-1)  # [B, F]
  delta = torch.abs(foot_height - target_height)  # [B, F]
  cost = torch.sum(delta * vel_norm, dim=1)  # [B]
  if command_name is not None:
    command = env.command_manager.get_command(command_name)
    if command is not None:
      linear_norm = torch.norm(command[:, :2], dim=1)
      angular_norm = torch.abs(command[:, 2])
      total_command = linear_norm + angular_norm
      active = (total_command > command_threshold).float()
      cost = cost * active
  return cost


class feet_swing_height:
  """Penalize deviation from target swing height, evaluated at landing."""

  def __init__(self, cfg: RewardTermCfg, env: ManagerBasedRlEnv):
    height_sensor = env.scene[cfg.params["height_sensor_name"]]
    assert isinstance(height_sensor, TerrainHeightSensor), (
      f"feet_swing_height requires a TerrainHeightSensor, got {type(height_sensor).__name__}"
    )
    num_feet = height_sensor.num_frames
    self.peak_heights = torch.zeros(
      (env.num_envs, num_feet), device=env.device, dtype=torch.float32
    )
    self.step_dt = env.step_dt

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    sensor_name: str,
    height_sensor_name: str,
    target_height: float,
    command_name: str,
    command_threshold: float,
  ) -> torch.Tensor:
    contact_sensor: ContactSensor = env.scene[sensor_name]
    command = env.command_manager.get_command(command_name)
    assert command is not None
    height_sensor: TerrainHeightSensor = env.scene[height_sensor_name]
    foot_heights = height_sensor.data.heights
    in_air = contact_sensor.data.found == 0
    self.peak_heights = torch.where(
      in_air,
      torch.maximum(self.peak_heights, foot_heights),
      self.peak_heights,
    )
    first_contact = contact_sensor.compute_first_contact(dt=self.step_dt)
    linear_norm = torch.norm(command[:, :2], dim=1)
    angular_norm = torch.abs(command[:, 2])
    total_command = linear_norm + angular_norm
    active = (total_command > command_threshold).float()
    error = self.peak_heights / target_height - 1.0
    cost = torch.sum(torch.square(error) * first_contact.float(), dim=1) * active
    num_landings = torch.sum(first_contact.float())
    peak_heights_at_landing = self.peak_heights * first_contact.float()
    mean_peak_height = torch.sum(peak_heights_at_landing) / torch.clamp(
      num_landings, min=1
    )
    env.extras["log"]["Metrics/peak_height_mean"] = mean_peak_height
    self.peak_heights = torch.where(
      first_contact,
      torch.zeros_like(self.peak_heights),
      self.peak_heights,
    )
    return cost


def feet_slip(
  env: ManagerBasedRlEnv,
  sensor_name: str,
  command_name: str,
  command_threshold: float = 0.01,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Penalize foot sliding (xy velocity while in contact)."""
  asset: Entity = env.scene[asset_cfg.name]
  contact_sensor: ContactSensor = env.scene[sensor_name]
  command = env.command_manager.get_command(command_name)
  assert command is not None
  linear_norm = torch.norm(command[:, :2], dim=1)
  angular_norm = torch.abs(command[:, 2])
  total_command = linear_norm + angular_norm
  active = (total_command > command_threshold).float()
  assert contact_sensor.data.found is not None
  in_contact = (contact_sensor.data.found > 0).float()  # [B, N]
  foot_vel_xy = asset.data.site_lin_vel_w[:, asset_cfg.site_ids, :2]  # [B, N, 2]
  vel_xy_norm = torch.norm(foot_vel_xy, dim=-1)  # [B, N]
  vel_xy_norm_sq = torch.square(vel_xy_norm)  # [B, N]
  cost = torch.sum(vel_xy_norm_sq * in_contact, dim=1) * active
  num_in_contact = torch.sum(in_contact)
  mean_slip_vel = torch.sum(vel_xy_norm * in_contact) / torch.clamp(
    num_in_contact, min=1
  )
  env.extras["log"]["Metrics/slip_velocity_mean"] = mean_slip_vel
  return cost


def soft_landing(
  env: ManagerBasedRlEnv,
  sensor_name: str,
  command_name: str | None = None,
  command_threshold: float = 0.05,
) -> torch.Tensor:
  """Penalize high impact forces at landing to encourage soft footfalls."""
  contact_sensor: ContactSensor = env.scene[sensor_name]
  sensor_data = contact_sensor.data
  assert sensor_data.force is not None
  forces = sensor_data.force  # [B, N, 3]
  force_magnitude = torch.norm(forces, dim=-1)  # [B, N]
  first_contact = contact_sensor.compute_first_contact(dt=env.step_dt)  # [B, N]
  landing_impact = force_magnitude * first_contact.float()  # [B, N]
  cost = torch.sum(landing_impact, dim=1)  # [B]
  num_landings = torch.sum(first_contact.float())
  mean_landing_force = torch.sum(landing_impact) / torch.clamp(num_landings, min=1)
  env.extras["log"]["Metrics/landing_force_mean"] = mean_landing_force
  if command_name is not None:
    command = env.command_manager.get_command(command_name)
    if command is not None:
      linear_norm = torch.norm(command[:, :2], dim=1)
      angular_norm = torch.abs(command[:, 2])
      total_command = linear_norm + angular_norm
      active = (total_command > command_threshold).float()
      cost = cost * active
  return cost


class feet_gait:
  """Reward bipedal foot contacts that match an open-loop gait phase.

  Reference schedule (shared with ``gait_cycle`` observation):

  - ``φ ∈ [0, 0.5)``: left swing, right stance
  - ``φ ∈ [0.5, 1)``: left stance, right swing

  Returns a value in ``[0, 1]`` (fraction of feet matching), gated by
  command magnitude and the same drop/fade curriculum as the gait clock.
  """

  def __init__(self, cfg: RewardTermCfg, env: ManagerBasedRlEnv):
    sensor = env.scene[cfg.params["sensor_name"]]
    assert isinstance(sensor, ContactSensor), (
      f"feet_gait requires a ContactSensor, got {type(sensor).__name__}"
    )
    left_name: str = cfg.params.get("left_foot_name", "left_foot_link")
    right_name: str = cfg.params.get("right_foot_name", "right_foot_link")
    names = list(sensor.primary_names)
    if left_name not in names or right_name not in names:
      raise ValueError(
        f"feet_gait expected primaries '{left_name}' and '{right_name}', got {names}"
      )
    self.left_idx = names.index(left_name)
    self.right_idx = names.index(right_name)

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    sensor_name: str,
    period: float = 0.6,
    command_name: str = "twist",
    command_threshold: float = 0.05,
    left_foot_name: str = "left_foot_link",
    right_foot_name: str = "right_foot_link",
    drop_step: int = 8_000 * 24,
    fade_steps: int = 2_000 * 24,
  ) -> torch.Tensor:
    del left_foot_name, right_foot_name  # Resolved in __init__.
    scale = gait_scale(env.common_step_counter, drop_step, fade_steps)
    if scale == 0.0:
      return torch.zeros(env.num_envs, device=env.device)

    phase, gait_active = advance_gait_phase(env, period, command_name, command_threshold)
    sensor: ContactSensor = env.scene[sensor_name]
    assert sensor.data.found is not None
    contact = (sensor.data.found > 0).float()  # [B, P]
    left_contact = contact[:, self.left_idx]
    right_contact = contact[:, self.right_idx]

    # φ < 0.5 → left swing (0), right stance (1); else swapped.
    left_desired = (phase >= 0.5).float()
    right_desired = (phase < 0.5).float()
    match = 0.5 * (
      (1.0 - torch.abs(left_contact - left_desired))
      + (1.0 - torch.abs(right_contact - right_desired))
    )
    reward = match * gait_active.float() * scale
    env.extras["log"]["Metrics/gait_match_mean"] = torch.mean(match * gait_active.float())
    return reward


class feet_swing:
  """Reward airborne feet during Booster T1-style swing windows.

  Port of ``booster_gym`` ``_reward_feet_swing``:

  - Left swing window centered at phase ``0.25``
  - Right swing window centered at phase ``0.75``
  - Window half-width = ``0.5 * swing_period`` (default ``0.2`` → ±0.1)
  - +1 per foot in its window, airborne, and ``gait_frequency > 1e-8``

  Shares the open-loop phase buffer with ``gait_cycle`` via ``advance_gait_phase``.
  """

  def __init__(self, cfg: RewardTermCfg, env: ManagerBasedRlEnv):
    self.sensor_name: str = cfg.params["sensor_name"]
    sensor = env.scene[self.sensor_name]
    assert isinstance(sensor, ContactSensor), (
      f"feet_swing requires a ContactSensor, got {type(sensor).__name__}"
    )
    left_name: str = cfg.params.get("left_foot_name", "left_foot_link")
    right_name: str = cfg.params.get("right_foot_name", "right_foot_link")
    names = list(sensor.primary_names)
    if left_name not in names or right_name not in names:
      raise ValueError(
        f"feet_swing expected primaries '{left_name}' and '{right_name}', got {names}"
      )
    self.left_idx = names.index(left_name)
    self.right_idx = names.index(right_name)

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    sensor_name: str,
    period: float = 0.6,
    swing_period: float = 0.2,
    command_name: str = "twist",
    command_threshold: float = 0.05,
    left_foot_name: str = "left_foot_link",
    right_foot_name: str = "right_foot_link",
  ) -> torch.Tensor:
    del sensor_name, left_foot_name, right_foot_name, command_threshold
    phase, gait_active = advance_gait_phase(env, period, command_name)
    sensor: ContactSensor = env.scene[self.sensor_name]
    assert sensor.data.found is not None
    in_air = sensor.data.found == 0  # [B, P]
    left_air = in_air[:, self.left_idx]
    right_air = in_air[:, self.right_idx]

    half = 0.5 * swing_period
    left_swing = (torch.abs(phase - 0.25) < half) & gait_active
    right_swing = (torch.abs(phase - 0.75) < half) & gait_active
    reward = (left_swing & left_air).float() + (right_swing & right_air).float()
    env.extras["log"]["Metrics/feet_swing_mean"] = torch.mean(reward)
    return reward


class variable_posture:
  """Penalize deviation from default pose with speed-dependent tolerance.

  Uses per-joint standard deviations to control how much each joint can deviate
  from default pose. Smaller std = stricter (less deviation allowed), larger
  std = more forgiving. The reward is: exp(-mean(error² / std²))

  Three speed regimes (based on linear + angular command velocity):
    - std_standing (speed < walking_threshold): Tight tolerance for holding pose.
    - std_walking (walking_threshold <= speed < running_threshold): Moderate.
    - std_running (speed >= running_threshold): Loose tolerance for large motion.

  Tune std values per joint based on how much motion that joint needs at each
  speed. Map joint name patterns to std values, e.g. {".*knee.*": 0.35}.
  """

  def __init__(self, cfg: RewardTermCfg, env: ManagerBasedRlEnv):
    asset: Entity = env.scene[cfg.params["asset_cfg"].name]
    default_joint_pos = asset.data.default_joint_pos
    assert default_joint_pos is not None
    self.default_joint_pos = default_joint_pos

    _, joint_names = asset.find_joints(cfg.params["asset_cfg"].joint_names)

    _, _, std_standing = resolve_matching_names_values(
      data=cfg.params["std_standing"],
      list_of_strings=joint_names,
    )
    self.std_standing = torch.tensor(
      std_standing, device=env.device, dtype=torch.float32
    )

    _, _, std_walking = resolve_matching_names_values(
      data=cfg.params["std_walking"],
      list_of_strings=joint_names,
    )
    self.std_walking = torch.tensor(std_walking, device=env.device, dtype=torch.float32)

    _, _, std_running = resolve_matching_names_values(
      data=cfg.params["std_running"],
      list_of_strings=joint_names,
    )
    self.std_running = torch.tensor(std_running, device=env.device, dtype=torch.float32)

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    std_standing,
    std_walking,
    std_running,
    asset_cfg: SceneEntityCfg,
    command_name: str,
    walking_threshold: float = 0.5,
    running_threshold: float = 1.5,
  ) -> torch.Tensor:
    del std_standing, std_walking, std_running  # Unused.

    asset: Entity = env.scene[asset_cfg.name]
    command = env.command_manager.get_command(command_name)
    assert command is not None

    linear_speed = torch.norm(command[:, :2], dim=1)
    angular_speed = torch.abs(command[:, 2])
    total_speed = linear_speed + angular_speed

    standing_mask = (total_speed < walking_threshold).float()
    walking_mask = (
      (total_speed >= walking_threshold) & (total_speed < running_threshold)
    ).float()
    running_mask = (total_speed >= running_threshold).float()

    std = (
      self.std_standing * standing_mask.unsqueeze(1)
      + self.std_walking * walking_mask.unsqueeze(1)
      + self.std_running * running_mask.unsqueeze(1)
    )

    current_joint_pos = asset.data.joint_pos[:, asset_cfg.joint_ids]
    desired_joint_pos = self.default_joint_pos[:, asset_cfg.joint_ids]
    error_squared = torch.square(current_joint_pos - desired_joint_pos)

    return torch.exp(-torch.mean(error_squared / (std**2), dim=1))


def joint_deviation_l2(
  env: ManagerBasedRlEnv,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Penalize squared deviation from default joint positions.

  Unlike the exp pose reward, this does not saturate when joints are far from
  default, so it keeps providing gradient against postures like wide stance.
  """
  asset: Entity = env.scene[asset_cfg.name]
  assert asset.data.default_joint_pos is not None
  diff = (
    asset.data.joint_pos[:, asset_cfg.joint_ids]
    - asset.data.default_joint_pos[:, asset_cfg.joint_ids]
  )
  return torch.sum(torch.square(diff), dim=1)


def joint_deviation_l2_when_still(
  env: ManagerBasedRlEnv,
  command_name: str = "twist",
  command_threshold: float = 0.05,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """``joint_deviation_l2`` gated on near-zero twist (standing / still)."""
  cost = joint_deviation_l2(env, asset_cfg)
  command = env.command_manager.get_command(command_name)
  if command is None:
    return cost
  speed = torch.norm(command[:, :2], dim=1) + torch.abs(command[:, 2])
  still = (speed < command_threshold).float()
  return cost * still


def _cubic_bezier(y_start: torch.Tensor, y_end: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
  y_diff = y_end - y_start
  bezier = x**3 + 3.0 * (x**2 * (1.0 - x))
  return y_start + y_diff * bezier


def _expected_foot_height_from_phase(
  phase_01: torch.Tensor, swing_height: float
) -> torch.Tensor:
  """Holosoma/MuJoCo Playground foot-height profile for phase in ``[0, 1)``."""
  x = phase_01
  stance = _cubic_bezier(
    torch.zeros_like(x), torch.full_like(x, swing_height), (2.0 * x).clamp(0.0, 1.0)
  )
  swing = _cubic_bezier(
    torch.full_like(x, swing_height),
    torch.zeros_like(x),
    (2.0 * x - 1.0).clamp(0.0, 1.0),
  )
  return torch.where(x <= 0.5, stance, swing)


def feet_phase(
  env: ManagerBasedRlEnv,
  height_sensor_name: str,
  swing_height: float = 0.09,
  tracking_sigma: float = 0.008,
  period: float = 0.6,
  command_name: str = "twist",
  command_threshold: float = 0.05,
) -> torch.Tensor:
  """Reward tracking desired swing/stance foot height from the gait phase.

  Port of Holosoma ``feet_phase`` (MuJoCo Playground profile). Left foot uses
  shared phase ``φ``; right foot uses ``(φ + 0.5) % 1`` for antiphase.
  """
  height_sensor = env.scene[height_sensor_name]
  assert isinstance(height_sensor, TerrainHeightSensor), (
    f"feet_phase requires a TerrainHeightSensor, got {type(height_sensor).__name__}"
  )
  foot_heights = height_sensor.data.heights  # [B, 2]
  phase, _ = advance_gait_phase(env, period, command_name, command_threshold)
  rz_left = _expected_foot_height_from_phase(phase, swing_height)
  rz_right = _expected_foot_height_from_phase((phase + 0.5) % 1.0, swing_height)
  error = torch.square(foot_heights[:, 0] - rz_left) + torch.square(
    foot_heights[:, 1] - rz_right
  )
  return torch.exp(-error / tracking_sigma)


def feet_too_close_xy(
  env: ManagerBasedRlEnv,
  close_feet_threshold: float = 0.15,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Penalize when foot sites are closer than ``close_feet_threshold`` in xy.

  Port of Holosoma ``penalty_close_feet_xy``.
  """
  asset: Entity = env.scene[asset_cfg.name]
  foot_pos = asset.data.site_pos_w[:, asset_cfg.site_ids, :2]  # [B, 2, 2]
  separation = torch.norm(foot_pos[:, 0] - foot_pos[:, 1], dim=-1)
  return (separation < close_feet_threshold).float()


def feet_orientation_l2(
  env: ManagerBasedRlEnv,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Penalize non-flat foot orientation (projected gravity xy in foot frames).

  Port of Holosoma ``penalty_feet_ori``.
  """
  asset: Entity = env.scene[asset_cfg.name]
  foot_quat_w = asset.data.body_link_quat_w[:, asset_cfg.body_ids]  # [B, 2, 4]
  gravity_w = torch.tensor([0.0, 0.0, -1.0], device=env.device).expand(
    env.num_envs, 2, 3
  )
  quat_flat = foot_quat_w.reshape(-1, 4)
  grav_flat = gravity_w.reshape(-1, 3)
  grav_f = quat_apply_inverse(quat_flat, grav_flat).reshape(env.num_envs, 2, 3)
  tilt = torch.sqrt(torch.sum(torch.square(grav_f[..., :2]), dim=-1))  # [B, 2]
  return tilt[:, 0] + tilt[:, 1]


class weighted_pose_penalty:
  """Holosoma-style pose penalty: ``sum(w_i * (q_i - q0_i)^2)``."""

  def __init__(self, cfg: RewardTermCfg, env: ManagerBasedRlEnv):
    asset: Entity = env.scene[cfg.params["asset_cfg"].name]
    joint_ids, joint_names = asset.find_joints(cfg.params["asset_cfg"].joint_names)
    self.joint_ids = torch.tensor(joint_ids, device=env.device, dtype=torch.long)
    _, _, values = resolve_matching_names_values(
      cfg.params["pose_weights"], joint_names
    )
    self.weights = torch.tensor(values, device=env.device, dtype=torch.float32)

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    pose_weights: dict[str, float],
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
  ) -> torch.Tensor:
    del pose_weights  # Resolved in __init__.
    asset: Entity = env.scene[asset_cfg.name]
    assert asset.data.default_joint_pos is not None
    diff = (
      asset.data.joint_pos[:, self.joint_ids]
      - asset.data.default_joint_pos[:, self.joint_ids]
    )
    return torch.sum(self.weights.unsqueeze(0) * torch.square(diff), dim=1)


# ---------------------------------------------------------------------------
# Booster Gym–style reward terms (ported for K1 / mjlab)
# ---------------------------------------------------------------------------


def track_lin_vel_axis(
  env: ManagerBasedRlEnv,
  axis: int,
  command_name: str,
  tracking_sigma: float = 0.25,
  filter_weight: float = 0.1,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Booster Gym ``tracking_lin_vel_{x,y}``: ``exp(-(cmd-v)^2 / sigma)``.

  Uses EMA-filtered body linear velocity (Booster ``filter_weight``).
  """
  asset: Entity = env.scene[asset_cfg.name]
  command = env.command_manager.get_command(command_name)
  assert command is not None
  filtered_lin, _ = _ema_filtered_base_vel(env, asset, filter_weight)
  error = torch.square(command[:, axis] - filtered_lin[:, axis])
  return torch.exp(-error / tracking_sigma)


def track_ang_vel_z(
  env: ManagerBasedRlEnv,
  command_name: str,
  tracking_sigma: float = 0.25,
  filter_weight: float = 0.1,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Booster Gym ``tracking_ang_vel`` on yaw rate (EMA-filtered)."""
  asset: Entity = env.scene[asset_cfg.name]
  command = env.command_manager.get_command(command_name)
  assert command is not None
  _, filtered_ang = _ema_filtered_base_vel(env, asset, filter_weight)
  error = torch.square(command[:, 2] - filtered_ang[:, 2])
  return torch.exp(-error / tracking_sigma)


def _ema_filtered_base_vel(
  env: ManagerBasedRlEnv,
  asset: Entity,
  filter_weight: float,
) -> tuple[torch.Tensor, torch.Tensor]:
  """Booster-style EMA of body lin/ang velocity, shared across reward terms.

  Updates once per env step via ``common_step_counter``. Resets to raw velocity
  on the first step after episode reset.
  """
  raw_lin = asset.data.root_link_lin_vel_b
  raw_ang = asset.data.root_link_ang_vel_b
  cache = getattr(env, "_booster_vel_ema", None)
  step = int(env.common_step_counter)
  if (
    cache is None
    or cache["lin"].shape[0] != env.num_envs
    or cache["step"] != step
  ):
    if cache is None or cache["lin"].shape[0] != env.num_envs:
      filtered_lin = raw_lin.clone()
      filtered_ang = raw_ang.clone()
    else:
      filtered_lin = cache["lin"]
      filtered_ang = cache["ang"]
      w = float(filter_weight)
      filtered_lin = raw_lin * w + filtered_lin * (1.0 - w)
      filtered_ang = raw_ang * w + filtered_ang * (1.0 - w)
    # Fresh episodes: snap filter to raw (match T1 reset-to-zero then blend).
    reset = env.episode_length_buf <= 1
    if reset.any():
      filtered_lin = filtered_lin.clone()
      filtered_ang = filtered_ang.clone()
      filtered_lin[reset] = raw_lin[reset]
      filtered_ang[reset] = raw_ang[reset]
    cache = {"step": step, "lin": filtered_lin, "ang": filtered_ang}
    env._booster_vel_ema = cache  # type: ignore[attr-defined]
  return cache["lin"], cache["ang"]


def base_height_range_l2(
  env: ManagerBasedRlEnv,
  minimum_height: float,
  maximum_height: float,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Penalize root height outside ``[minimum_height, maximum_height]``.

  K1 uses a band (e.g. 0.48–0.80) instead of T1's single ``base_height_target``.
  """
  asset: Entity = env.scene[asset_cfg.name]
  height = asset.data.root_link_pos_w[:, 2]
  below = torch.clamp(minimum_height - height, min=0.0)
  above = torch.clamp(height - maximum_height, min=0.0)
  return torch.square(below) + torch.square(above)


def base_height_target_l2(
  env: ManagerBasedRlEnv,
  target_height: float = 0.50,
  sensor_name: str | None = "terrain_scan",
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Booster / ParameterWalk ``base_height``: ``(h - target)^2``.

  ``h`` is clearance of the base above terrain (Booster:
  ``base_z - terrain_height(base_xy)``). See ``base_terrain_clearance``.
  """
  from mjlab.tasks.velocity.mdp.terrain_utils import base_terrain_clearance

  clearance = base_terrain_clearance(env, sensor_name, asset_cfg.name)
  return torch.square(clearance - target_height)


def root_lin_vel_z_l2(
  env: ManagerBasedRlEnv,
  filter_weight: float = 0.1,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Booster Gym ``lin_vel_z``: penalize vertical base velocity (EMA-filtered)."""
  asset: Entity = env.scene[asset_cfg.name]
  filtered_lin, _ = _ema_filtered_base_vel(env, asset, filter_weight)
  return torch.square(filtered_lin[:, 2])


def feet_distance_lateral(
  env: ManagerBasedRlEnv,
  feet_distance_ref: float = 0.18,
  max_penalty: float = 0.1,
  wide_margin: float | None = None,
  command_name: str = "twist",
  side_walk_threshold: float = 0.1,
  side_walk_margin_scale: float = 3.0,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Penalize lateral foot spacing outside a band around ``feet_distance_ref``.

  Booster Gym only penalized a *narrow* stance
  (``clip(ref - dist, 0, max_penalty)``). When ``wide_margin`` is set, also
  penalize too-wide stance:
  ``clip(dist - (ref + margin), 0, max_penalty)``.

  If ``|cmd_vy| > side_walk_threshold``, ``margin`` is scaled by
  ``side_walk_margin_scale`` (default 3×) so side-walk can open the stance.
  """
  from mjlab.utils.lab_api.math import euler_xyz_from_quat

  asset: Entity = env.scene[asset_cfg.name]
  foot_xy = asset.data.site_pos_w[:, asset_cfg.site_ids, :2]  # [B, 2, 2]
  _, _, yaw = euler_xyz_from_quat(asset.data.root_link_quat_w)
  dx = foot_xy[:, 1, 0] - foot_xy[:, 0, 0]
  dy = foot_xy[:, 1, 1] - foot_xy[:, 0, 1]
  lateral = torch.abs(torch.cos(yaw) * dy - torch.sin(yaw) * dx)
  narrow = torch.clamp(feet_distance_ref - lateral, min=0.0, max=max_penalty)
  if wide_margin is None:
    return narrow

  margin = float(wide_margin)
  command = env.command_manager.get_command(command_name)
  if command is not None and side_walk_margin_scale != 1.0:
    side = torch.abs(command[:, 1]) > side_walk_threshold
    margin_b = torch.full_like(lateral, margin)
    margin_b = torch.where(
      side, margin_b * float(side_walk_margin_scale), margin_b
    )
  else:
    margin_b = margin

  wide = torch.clamp(lateral - (feet_distance_ref + margin_b), min=0.0, max=max_penalty)
  return narrow + wide


def joint_power_penalty(
  env: ManagerBasedRlEnv, asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG
) -> torch.Tensor:
  """Booster Gym ``power``: ``sum(max(tau * qdot, 0))``."""
  asset: Entity = env.scene[asset_cfg.name]
  tau = asset.data.actuator_force[:, asset_cfg.actuator_ids]
  qd = asset.data.joint_vel[:, asset_cfg.joint_ids]
  return torch.sum(torch.clamp(tau * qd, min=0.0), dim=1)


class torque_tiredness:
  """Booster Gym ``torque_tiredness``: ``sum(clip(tau / limit, ±1)^2)``."""

  def __init__(self, cfg: RewardTermCfg, env: ManagerBasedRlEnv):
    del cfg, env
    self._limits: torch.Tensor | None = None

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
  ) -> torch.Tensor:
    asset: Entity = env.scene[asset_cfg.name]
    ids = asset_cfg.actuator_ids
    tau = asset.data.actuator_force[:, ids]
    if self._limits is None:
      n_ctrl = asset.data.actuator_force.shape[1]
      full = torch.ones(n_ctrl, device=env.device, dtype=torch.float32)
      for act in asset.actuators:
        force_limit = getattr(act, "force_limit", None)
        if force_limit is None:
          continue
        full[act.global_ctrl_ids] = force_limit[0]
      self._limits = full[ids].clamp(min=1.0e-6)
    ratio = (tau / self._limits.unsqueeze(0)).clamp(min=-1.0, max=1.0)
    return torch.sum(torch.square(ratio), dim=1)


class root_acc_l2:
  """Booster Gym ``root_acc``: finite-diff root lin+ang acceleration L2."""

  def __init__(self, cfg: RewardTermCfg, env: ManagerBasedRlEnv):
    del cfg
    self._last_vel = torch.zeros(env.num_envs, 6, device=env.device)

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
  ) -> torch.Tensor:
    asset: Entity = env.scene[asset_cfg.name]
    vel = asset.data.root_link_vel_w
    acc = (vel - self._last_vel) / env.step_dt
    # First step after reset: last_vel is stale; zero the penalty.
    fresh = env.episode_length_buf <= 1
    out = torch.sum(torch.square(acc), dim=-1)
    out = out * (~fresh).float()
    self._last_vel = vel.clone()
    return out


def feet_roll_l2(
  env: ManagerBasedRlEnv, asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG
) -> torch.Tensor:
  """Penalize non-flat foot soles (world / gravity frame).

  Uses ``body_link_quat_w`` → XYZ-extrinsic Euler; ``roll→0`` means the sole is
  level with the world horizontal. That is exactly "lands flat on the ground"
  on flat terrain: hip roll is allowed as long as ankle roll cancels it so the
  foot link stays flat (less ankle motor fight than forcing hip_roll=0).

  Not trunk-frame roll, and not local terrain slope (on banks, world-flat ≠
  terrain-parallel).
  """
  from mjlab.utils.lab_api.math import euler_xyz_from_quat

  asset: Entity = env.scene[asset_cfg.name]
  foot_quat = asset.data.body_link_quat_w[:, asset_cfg.body_ids]  # [B, 2, 4]
  roll, _, _ = euler_xyz_from_quat(foot_quat.reshape(-1, 4))
  roll = roll.reshape(env.num_envs, -1)
  return torch.sum(torch.square(roll), dim=1)


def _feet_yaw_angles(
  env: ManagerBasedRlEnv, asset_cfg: SceneEntityCfg
) -> tuple[torch.Tensor, torch.Tensor]:
  """Return ``(feet_yaw [B, 2], root_yaw [B])`` wrapped to ``[-pi, pi]``."""
  from mjlab.utils.lab_api.math import euler_xyz_from_quat, wrap_to_pi

  asset: Entity = env.scene[asset_cfg.name]
  foot_quat = asset.data.body_link_quat_w[:, asset_cfg.body_ids]
  _, _, feet_yaw = euler_xyz_from_quat(foot_quat.reshape(-1, 4))
  feet_yaw = wrap_to_pi(feet_yaw.reshape(env.num_envs, -1))
  _, _, root_yaw = euler_xyz_from_quat(asset.data.root_link_quat_w)
  return feet_yaw, wrap_to_pi(root_yaw)


def feet_yaw_diff_l2(
  env: ManagerBasedRlEnv, asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG
) -> torch.Tensor:
  """Booster Gym ``feet_yaw_diff``: squared yaw gap between left/right feet."""
  from mjlab.utils.lab_api.math import wrap_to_pi

  feet_yaw, _ = _feet_yaw_angles(env, asset_cfg)
  return torch.square(wrap_to_pi(feet_yaw[:, 1] - feet_yaw[:, 0]))


def feet_yaw_mean_l2(
  env: ManagerBasedRlEnv, asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG
) -> torch.Tensor:
  """Booster Gym ``feet_yaw_mean``: squared gap between base yaw and mean foot yaw."""
  from mjlab.utils.lab_api.math import wrap_to_pi

  feet_yaw, root_yaw = _feet_yaw_angles(env, asset_cfg)
  # Match T1: when feet straddle ±π, shift the mean by π before comparing.
  feet_yaw_mean = feet_yaw.mean(dim=-1) + torch.pi * (
    torch.abs(feet_yaw[:, 1] - feet_yaw[:, 0]) > torch.pi
  ).float()
  return torch.square(wrap_to_pi(root_yaw - feet_yaw_mean))

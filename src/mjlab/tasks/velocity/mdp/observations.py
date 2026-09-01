from __future__ import annotations

from typing import TYPE_CHECKING, Any

import torch

from mjlab.entity import Entity
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.sensor import ContactSensor
from mjlab.sensor.terrain_height_sensor import TerrainHeightSensor

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv
  from mjlab.managers.observation_manager import ObservationTermCfg

_DEFAULT_ASSET_CFG = SceneEntityCfg("robot")

# Shared across actor/critic term instances for the same env (keyed by id).
_GAIT_STATE: dict[int, dict[str, Any]] = {}


def foot_height(env: ManagerBasedRlEnv, sensor_name: str) -> torch.Tensor:
  """Per-foot vertical clearance above terrain.

  Returns:
    Tensor of shape [B, F] where F is the number of frames (feet).
  """
  sensor = env.scene[sensor_name]
  assert isinstance(sensor, TerrainHeightSensor), (
    f"foot_height requires a TerrainHeightSensor, got {type(sensor).__name__}"
  )
  return sensor.data.heights


def foot_air_time(env: ManagerBasedRlEnv, sensor_name: str) -> torch.Tensor:
  sensor: ContactSensor = env.scene[sensor_name]
  sensor_data = sensor.data
  current_air_time = sensor_data.current_air_time
  assert current_air_time is not None
  return current_air_time


def foot_contact(env: ManagerBasedRlEnv, sensor_name: str) -> torch.Tensor:
  sensor: ContactSensor = env.scene[sensor_name]
  sensor_data = sensor.data
  assert sensor_data.found is not None
  return (sensor_data.found > 0).float()


def foot_contact_forces(env: ManagerBasedRlEnv, sensor_name: str) -> torch.Tensor:
  sensor: ContactSensor = env.scene[sensor_name]
  sensor_data = sensor.data
  assert sensor_data.force is not None
  forces_flat = sensor_data.force.flatten(start_dim=1)  # [B, N*3]
  return torch.sign(forces_flat) * torch.log1p(torch.abs(forces_flat))


def base_mass_scaled(
  env: ManagerBasedRlEnv, asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG
) -> torch.Tensor:
  """Booster / ParameterWalk privileged mass state: trunk COM delta + mass delta."""
  from mjlab.envs.mdp.dr._core import _select_default_values

  asset: Entity = env.scene[asset_cfg.name]
  env_ids = torch.arange(env.num_envs, device=env.device, dtype=torch.int)
  global_body_ids = asset.indexing.body_ids[asset_cfg.body_ids].to(
    device=env.device, dtype=torch.int
  )
  default_ipos = _select_default_values(env, "body_ipos", env_ids, global_body_ids)
  default_mass = _select_default_values(env, "body_mass", env_ids, global_body_ids)
  current_ipos = env.sim.model.body_ipos[:, global_body_ids]
  current_mass = env.sim.model.body_mass[:, global_body_ids]
  d_ipos = (current_ipos - default_ipos).reshape(env.num_envs, -1)
  d_mass = (current_mass - default_mass).reshape(env.num_envs, -1)
  return torch.cat((d_ipos, d_mass), dim=-1)


def base_clearance(
  env: ManagerBasedRlEnv,
  sensor_name: str | None = "terrain_scan",
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Booster privileged height: trunk clearance above terrain."""
  from mjlab.tasks.velocity.mdp.terrain_utils import base_terrain_clearance

  return base_terrain_clearance(env, sensor_name, asset_cfg.name).unsqueeze(-1)


def trunk_external_force(
  env: ManagerBasedRlEnv,
  scale: float = 0.1,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Booster privileged push force on trunk (``xfrc_applied``), scaled."""
  asset: Entity = env.scene[asset_cfg.name]
  force = asset.data.body_external_wrench[:, asset_cfg.body_ids, :3]
  return force.reshape(env.num_envs, -1) * scale


def trunk_external_torque(
  env: ManagerBasedRlEnv,
  scale: float = 0.5,
  asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
  """Booster privileged push torque on trunk (``xfrc_applied``), scaled."""
  asset: Entity = env.scene[asset_cfg.name]
  torque = asset.data.body_external_wrench[:, asset_cfg.body_ids, 3:6]
  return torque.reshape(env.num_envs, -1) * scale


def twist_velocity_commands(env: ManagerBasedRlEnv, command_name: str) -> torch.Tensor:
  """Velocity command ``[vx, vy, wz]`` without gait frequency (Booster T1 actor)."""
  command = env.command_manager.get_command(command_name)
  assert command is not None
  return command[:, :3]


def _gait_state(env: ManagerBasedRlEnv) -> dict[str, Any]:
  key = id(env)
  state = _GAIT_STATE.get(key)
  if state is None:
    state = {
      "phase": torch.zeros(env.num_envs, device=env.device),
      "step": -1,
    }
    _GAIT_STATE[key] = state
  return state


def gait_scale(step: int, drop_step: int, fade_steps: int) -> float:
  """Curriculum scale for gait obs/reward: 1 → 0 after ``drop_step``."""
  if fade_steps < 0:
    raise ValueError(f"fade_steps must be >= 0, got {fade_steps}")
  if step >= drop_step + fade_steps:
    return 0.0
  if step > drop_step and fade_steps > 0:
    return 1.0 - (step - drop_step) / float(fade_steps)
  if step > drop_step:
    return 0.0
  return 1.0


# Booster T1: gait clock active when gait_frequency > 1e-8.
_GAIT_FREQ_EPS = 1.0e-8


def advance_gait_phase(
  env: ManagerBasedRlEnv,
  period: float = 0.6,
  command_name: str = "twist",
  command_threshold: float = 0.05,
) -> tuple[torch.Tensor, torch.Tensor]:
  """Advance the shared open-loop gait phase at most once per env step.

  Booster T1 (4-D twist with gait frequency):
    - ``phase += dt * freq`` every step (``freq=0`` → frozen)
    - active mask = ``freq > 1e-8`` (not cmd-speed gated)

  Legacy 3-D commands (no freq dim):
    - ``phase += dt / period`` while ``|v| > command_threshold``

  Returns:
    ``(phase, gait_active)`` — phase in ``[0, 1)``, gait_active bool ``[B]``.
  """
  state = _gait_state(env)
  phase: torch.Tensor = state["phase"]
  step = env.common_step_counter
  command = env.command_manager.get_command(command_name)

  if command is not None and command.shape[-1] >= 4:
    freq = command[:, 3]
    gait_active = freq > _GAIT_FREQ_EPS
  elif command is not None:
    speed = torch.norm(command[:, :2], dim=1) + torch.abs(command[:, 2])
    gait_active = speed > command_threshold
  else:
    gait_active = torch.ones(env.num_envs, device=env.device, dtype=torch.bool)

  if state["step"] != step:
    state["step"] = step
    if command is not None and command.shape[-1] >= 4:
      # Booster: gait_process = fmod(gait_process + dt * gait_frequency, 1)
      phase[:] = torch.fmod(phase + env.step_dt * freq, 1.0)
    else:
      phase[:] = torch.where(
        gait_active,
        (phase + env.step_dt / period) % 1.0,
        phase,
      )
  return phase, gait_active


class gait_cycle:
  """Open-loop gait phase as ``[sin(2πφ), cos(2πφ)]``.

  Booster T1: phase from ``dt * gait_frequency``; sin/cos zeroed when
  ``gait_frequency <= 1e-8`` (standing). With 4-D twist commands, cadence
  follows commanded Hz. Legacy 3-D uses fixed ``period`` and speed gate.

  A random phase offset is sampled on reset. Actor and critic share one buffer.
  Optional ``drop_step`` / ``fade_steps`` fade sin/cos (Holosoma PPO); Booster
  keeps the clock always on — set ``drop_step`` very large to disable.
  """

  def __init__(self, cfg: ObservationTermCfg, env: ManagerBasedRlEnv):
    del cfg  # Unused; params arrive via __call__.
    self._env = env
    _gait_state(env)

  def reset(self, env_ids: torch.Tensor | slice | None = None) -> None:
    state = _gait_state(self._env)
    phase: torch.Tensor = state["phase"]
    if env_ids is None:
      env_ids = slice(None)
    if isinstance(env_ids, slice):
      count = self._env.num_envs
    else:
      count = int(env_ids.shape[0])
    phase[env_ids] = torch.rand(count, device=self._env.device)

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    period: float = 0.6,
    command_name: str = "twist",
    command_threshold: float = 0.05,
    drop_step: int = 8_000 * 24,
    fade_steps: int = 2_000 * 24,
  ) -> torch.Tensor:
    phase, gait_active = advance_gait_phase(
      env, period, command_name, command_threshold
    )
    angle = 2.0 * torch.pi * phase
    out = torch.stack((torch.sin(angle), torch.cos(angle)), dim=-1)
    out = out * gait_active.float().unsqueeze(-1)
    scale = gait_scale(env.common_step_counter, drop_step, fade_steps)
    if scale == 0.0:
      return torch.zeros_like(out)
    if scale != 1.0:
      out = out * scale
    return out


class nubots_parameter_walk_commands:
  """12-D ParameterWalk command matching NuBots / Isaac ``k1_walk_htwk`` obs.

  Layout::

    vx, vy, yaw, gait_freq,
    foot_yaw_L, foot_yaw_R, body_pitch, body_roll,
    feet_off_x, feet_off_y, cos(2πφ), sin(2πφ)

  Velocity + frequency come from the ``twist`` command (4-D). Pose targets are
  resampled on reset from the configured ranges (deploy uses fixed defaults).
  Gait clock shares ``advance_gait_phase`` with other gait terms.
  """

  def __init__(self, cfg: ObservationTermCfg, env: ManagerBasedRlEnv):
    self._env = env
    p = cfg.params or {}
    self._command_name = str(p.get("command_name", "twist"))
    self._command_threshold = float(p.get("command_threshold", 0.05))
    self._period = float(p.get("period", 1.0 / 1.7))
    self._ranges = {
      "foot_yaw_l": p.get("foot_yaw_l_range"),
      "foot_yaw_r": p.get("foot_yaw_r_range"),
      "body_pitch": p.get("body_pitch_range", (0.1, 0.1)),
      "body_roll": p.get("body_roll_range", (0.0, 0.0)),
      "feet_off_x": p.get("feet_offset_x_range"),
      "feet_off_y": p.get("feet_offset_y_range"),
    }
    n = env.num_envs
    device = env.device
    self._foot_yaw_l = torch.zeros(n, device=device)
    self._foot_yaw_r = torch.zeros(n, device=device)
    self._body_pitch = torch.zeros(n, device=device)
    self._body_roll = torch.zeros(n, device=device)
    self._feet_off_x = torch.zeros(n, device=device)
    self._feet_off_y = torch.zeros(n, device=device)
    _gait_state(env)
    self.reset(slice(None))

  def _sample(self, key: str, count: int, default: float) -> torch.Tensor:
    lo_hi = self._ranges.get(key)
    if lo_hi is None:
      return torch.full((count,), default, device=self._env.device)
    lo, hi = lo_hi
    return torch.empty(count, device=self._env.device).uniform_(float(lo), float(hi))

  def reset(self, env_ids: torch.Tensor | slice | None = None) -> None:
    if env_ids is None:
      env_ids = slice(None)
    if isinstance(env_ids, slice):
      count = self._env.num_envs
      idx: slice | torch.Tensor = env_ids
    else:
      count = int(env_ids.shape[0])
      idx = env_ids
    self._foot_yaw_l[idx] = self._sample("foot_yaw_l", count, 0.0)
    self._foot_yaw_r[idx] = self._sample("foot_yaw_r", count, 0.0)
    self._body_pitch[idx] = self._sample("body_pitch", count, 0.1)
    self._body_roll[idx] = self._sample("body_roll", count, 0.0)
    self._feet_off_x[idx] = self._sample("feet_off_x", count, 0.0)
    self._feet_off_y[idx] = self._sample("feet_off_y", count, 0.0)

  def __call__(self, env: ManagerBasedRlEnv, **_params) -> torch.Tensor:
    command = env.command_manager.get_command(self._command_name)
    assert command is not None
    # The dedicated HTWK command already owns and exposes its gait clock.
    # Return the reference 10-D command plus cos/sin phase without generating a
    # second clock in the observation term.
    if command.shape[-1] >= 12:
      return command[:, :12]
    vx = command[:, 0]
    vy = command[:, 1]
    yaw = command[:, 2]
    if command.shape[-1] >= 4:
      freq = command[:, 3]
    else:
      speed = torch.norm(command[:, :2], dim=1) + torch.abs(command[:, 2])
      freq = torch.where(
        speed > self._command_threshold,
        torch.full_like(speed, 1.0 / self._period),
        torch.zeros_like(speed),
      )

    if command.shape[-1] >= 10:
      foot_yaw_l = command[:, 4]
      foot_yaw_r = command[:, 5]
      body_pitch = command[:, 6]
      body_roll = command[:, 7]
      feet_off_x = command[:, 8]
      feet_off_y = command[:, 9]
    else:
      foot_yaw_l = self._foot_yaw_l
      foot_yaw_r = self._foot_yaw_r
      body_pitch = self._body_pitch
      body_roll = self._body_roll
      feet_off_x = self._feet_off_x
      feet_off_y = self._feet_off_y

    phase, gait_active = advance_gait_phase(
      env, self._period, self._command_name, self._command_threshold
    )
    angle = 2.0 * torch.pi * phase
    # NuBots deploy / Isaac: [..., cos, sin] (not sin, cos).
    clock_c = torch.cos(angle) * gait_active.float()
    clock_s = torch.sin(angle) * gait_active.float()

    return torch.stack(
      (
        vx,
        vy,
        yaw,
        freq,
        foot_yaw_l,
        foot_yaw_r,
        body_pitch,
        body_roll,
        feet_off_x,
        feet_off_y,
        clock_c,
        clock_s,
      ),
      dim=-1,
    )

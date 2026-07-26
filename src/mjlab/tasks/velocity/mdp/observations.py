from __future__ import annotations

from typing import TYPE_CHECKING, Any

import torch

from mjlab.sensor import ContactSensor
from mjlab.sensor.terrain_height_sensor import TerrainHeightSensor

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv
  from mjlab.managers.observation_manager import ObservationTermCfg

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


class gait_cycle:
  """Open-loop gait phase as ``[sin(2πφ), cos(2πφ)]``.

  Phase advances only while the velocity command exceeds
  ``command_threshold`` (standing freezes and zeros the clock). A random
  phase offset is sampled on reset. Actor and critic share one phase buffer
  per env so both groups stay synchronized.

  After ``drop_step`` env steps the signal linearly fades to zero over
  ``fade_steps``, keeping the observation dim fixed for the network.
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
    if fade_steps < 0:
      raise ValueError(f"fade_steps must be >= 0, got {fade_steps}")

    state = _gait_state(env)
    phase: torch.Tensor = state["phase"]
    step = env.common_step_counter
    command = env.command_manager.get_command(command_name)
    if command is not None:
      speed = torch.norm(command[:, :2], dim=1) + torch.abs(command[:, 2])
      moving = speed > command_threshold
    else:
      moving = torch.ones(env.num_envs, device=env.device, dtype=torch.bool)

    # Advance at most once per env step (actor + critic share this buffer).
    if state["step"] != step:
      state["step"] = step
      phase[:] = torch.where(
        moving,
        (phase + env.step_dt / period) % 1.0,
        phase,
      )

    angle = 2.0 * torch.pi * phase
    out = torch.stack((torch.sin(angle), torch.cos(angle)), dim=-1)
    out = out * moving.float().unsqueeze(-1)

    if step >= drop_step + fade_steps:
      return torch.zeros_like(out)
    if step > drop_step and fade_steps > 0:
      alpha = 1.0 - (step - drop_step) / float(fade_steps)
      out = out * alpha
    elif step > drop_step:
      return torch.zeros_like(out)
    return out

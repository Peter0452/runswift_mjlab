"""Kick-task curriculum terms."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv


def approach_spawn_radius_curriculum(
  env: ManagerBasedRlEnv,
  env_ids: object,
  event_name: str = "reset_base",
  start_radius: tuple[float, float] = (0.5, 1.0),
  end_radius: tuple[float, float] = (4.0, 4.0),
  start_step: int = 0,
  end_step: int = 400_000,
) -> float:
  """Linearly expand robot spawn radius from short range to full approach distance."""
  del env_ids
  step = env.common_step_counter
  if step <= start_step:
    radius = start_radius
  elif step >= end_step:
    radius = end_radius
  else:
    fraction = (step - start_step) / float(end_step - start_step)
    radius = (
      start_radius[0] + fraction * (end_radius[0] - start_radius[0]),
      start_radius[1] + fraction * (end_radius[1] - start_radius[1]),
    )
  cfg = env.event_manager.get_term_cfg(event_name)
  cfg.params["radius_range"] = radius
  return float(radius[1])

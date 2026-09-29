"""Episode state for the stage-2 kick: best shot and latched foot contact."""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_APPROACH_HOLD_STEPS = 50


class KickShot:
  """Best ball-to-target distance and the first swinging-foot contact."""

  def __init__(self, num_envs: int, device: str) -> None:
    self.min_dist = torch.full((num_envs,), torch.inf, device=device)
    self.contacted = torch.zeros(num_envs, dtype=torch.bool, device=device)
    self.contact_ball_xy = torch.zeros(num_envs, 2, device=device)
    self.contact_step = torch.full((num_envs,), -1, dtype=torch.long, device=device)
    self._synced_step = -1

  def reset(self, env_ids: torch.Tensor) -> None:
    self.min_dist[env_ids] = torch.inf
    self.contacted[env_ids] = False
    self.contact_ball_xy[env_ids] = 0.0
    self.contact_step[env_ids] = -1

  def sync(self, env: ManagerBasedRlEnv) -> KickShot:
    """Fold this step's ball pose and foot contact into the episode state."""
    if self._synced_step == env.common_step_counter:
      return self
    self._synced_step = env.common_step_counter
    ball_xy = env.scene["ball"].data.root_link_pos_w[:, :2]
    goal_xy = env.command_manager.get_command("goal")
    assert goal_xy is not None
    target_xy = goal_xy[:, :2] + env.scene.env_origins[:, :2]
    dist = torch.linalg.norm(ball_xy - target_xy, dim=-1)
    self.min_dist = torch.minimum(self.min_dist, dist)

    command = env.command_manager.get_term("motion")
    is_left = command.kick_foot_is_left()
    right = env.scene["ball_foot_contact"]
    assert right.data.found is not None
    right_hit = right.data.found.reshape(env.num_envs, -1).amax(dim=-1) > 0
    if "ball_left_foot_contact" in env.scene.sensors:
      left = env.scene["ball_left_foot_contact"]
      assert left.data.found is not None
      left_hit = left.data.found.reshape(env.num_envs, -1).amax(dim=-1) > 0
      hit = torch.where(is_left, left_hit, right_hit)
    else:
      hit = right_hit
    new = hit & ~self.contacted
    self.contact_ball_xy[new] = ball_xy[new]
    self.contact_step[new] = env.common_step_counter
    self.contacted |= hit
    return self

  def approach_done(self, env: ManagerBasedRlEnv) -> torch.Tensor:
    """True once the post-contact approach reward should turn off."""
    return self.contacted & (
      env.common_step_counter - self.contact_step > _APPROACH_HOLD_STEPS
    )


def kick_shot(env: ManagerBasedRlEnv) -> KickShot:
  state = getattr(env, "_kick_shot", None)
  if state is None:
    state = KickShot(env.num_envs, env.device)
    env._kick_shot = state  # type: ignore[attr-defined]
  return state.sync(env)


def reset_kick_shot(env: ManagerBasedRlEnv, env_ids: torch.Tensor) -> None:
  state = getattr(env, "_kick_shot", None)
  if state is not None:
    state.reset(env_ids)

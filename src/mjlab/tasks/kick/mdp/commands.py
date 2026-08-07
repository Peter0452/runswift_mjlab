"""Goal-position command for the kick task."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

import torch

from mjlab.managers.command_manager import CommandTerm, CommandTermCfg

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv


class UniformGoalPositionCommand(CommandTerm):
  """Sample a random 2-D goal position on the field.

  The command is a 2-D world-frame position ``[goal_x, goal_y]`` (in metres)
  relative to the env origin.  The policy receives this via the
  ``goal_direction`` observation term (converted to body-frame unit vector).

  Resampled every ``resampling_time_range`` seconds.
  """

  cfg: UniformGoalPositionCommandCfg

  def __init__(self, cfg: UniformGoalPositionCommandCfg, env: ManagerBasedRlEnv):
    super().__init__(cfg, env)
    self._command = torch.zeros(env.num_envs, 2, device=env.device)

  @property
  def command(self) -> torch.Tensor:
    """Goal position ``[x, y]`` in world-frame env-local coords, shape ``[B, 2]``."""
    return self._command

  def _resample(self, env_ids: torch.Tensor) -> None:
    n = len(env_ids)
    r_min, r_max = self.cfg.distance_range
    theta_min, theta_max = self.cfg.angle_range

    # Polar sampling → uniform-area distribution over the annulus.
    r = torch.empty(n, device=self._env.device).uniform_(r_min, r_max)
    theta = torch.empty(n, device=self._env.device).uniform_(theta_min, theta_max)
    self._command[env_ids, 0] = r * torch.cos(theta)
    self._command[env_ids, 1] = r * torch.sin(theta)

  def _set_debug_vis_impl(self, debug_vis: bool) -> None:
    pass

  def _debug_vis_callback(self, event) -> None:
    pass


@dataclass
class UniformGoalPositionCommandCfg(CommandTermCfg):
  """Configuration for :class:`UniformGoalPositionCommand`."""

  class_type: ClassVar[type] = UniformGoalPositionCommand

  distance_range: tuple[float, float] = (3.0, 8.0)
  """Min/max goal distance from env origin in metres."""

  angle_range: tuple[float, float] = (-math.pi, math.pi)
  """Min/max goal direction angle in radians (0 = robot forward)."""

  resampling_time_range: tuple[float, float] = field(default=(8.0, 12.0))

  def build(self, env: ManagerBasedRlEnv) -> UniformGoalPositionCommand:
    return UniformGoalPositionCommand(self, env)

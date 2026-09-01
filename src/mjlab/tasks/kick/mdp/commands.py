"""Goal-position command for the kick task."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

import torch

from mjlab.managers.command_manager import CommandTerm, CommandTermCfg
from mjlab.utils.lab_api.math import quat_apply

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv
  from mjlab.viewer.debug_visualizer import DebugVisualizer


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

  def _update_metrics(self) -> None:
    """Goal positions do not require running command metrics."""
    pass

  def _update_command(self) -> None:
    """Goal positions remain fixed until the next resampling event."""
    pass

  def _debug_vis_impl(self, visualizer: DebugVisualizer) -> None:
    """Draw the goal, ready waypoint, heading, and camera-cone boundaries."""
    robot = self._env.scene["robot"]
    ball = self._env.scene["ball"]
    env_ids = visualizer.get_env_indices(self._env.num_envs)

    ball_pos = ball.data.root_link_pos_w
    robot_pos = robot.data.root_link_pos_w
    goal_pos = torch.cat(
      [
        self._command + self._env.scene.env_origins[:, :2],
        ball_pos[:, 2:3],
      ],
      dim=-1,
    )
    ball_to_goal = goal_pos[:, :2] - ball_pos[:, :2]
    ball_to_goal = ball_to_goal / torch.linalg.norm(
      ball_to_goal, dim=-1, keepdim=True
    ).clamp(min=1.0e-6)
    waypoint = goal_pos.clone()
    waypoint[:, :2] = ball_pos[:, :2] - 0.35 * ball_to_goal

    body_forward = quat_apply(
      robot.data.root_link_quat_w,
      torch.tensor([1.0, 0.0, 0.0], device=self._env.device).expand_as(robot_pos),
    )
    body_heading = body_forward.clone()
    body_heading[:, 2] = 0.0
    body_heading = body_heading / torch.linalg.norm(
      body_heading, dim=-1, keepdim=True
    ).clamp(min=1.0e-6)
    camera_half_angle = math.radians(45.0)
    cos_half = math.cos(camera_half_angle)
    sin_half = math.sin(camera_half_angle)
    camera_left = torch.stack(
      [
        cos_half * body_heading[:, 0] - sin_half * body_heading[:, 1],
        sin_half * body_heading[:, 0] + cos_half * body_heading[:, 1],
        torch.zeros_like(body_heading[:, 2]),
      ],
      dim=-1,
    )
    camera_right = torch.stack(
      [
        cos_half * body_heading[:, 0] + sin_half * body_heading[:, 1],
        -sin_half * body_heading[:, 0] + cos_half * body_heading[:, 1],
        torch.zeros_like(body_heading[:, 2]),
      ],
      dim=-1,
    )
    robot_marker = robot_pos + torch.tensor(
      [0.0, 0.0, 0.15], device=self._env.device
    )
    for env_id in env_ids:
      visualizer.add_sphere(
        ball_pos[env_id].detach().cpu().numpy(),
        radius=0.11,
        color=(1.0, 0.35, 0.05, 0.9),
      )
      visualizer.add_sphere(
        goal_pos[env_id].detach().cpu().numpy(),
        radius=0.14,
        color=(0.1, 1.0, 0.2, 0.9),
      )
      visualizer.add_sphere(
        waypoint[env_id].detach().cpu().numpy(),
        radius=0.12,
        color=(0.1, 0.75, 1.0, 0.9),
      )
      visualizer.add_arrow(
        ball_pos[env_id].detach().cpu().numpy(),
        goal_pos[env_id].detach().cpu().numpy(),
        color=(0.1, 1.0, 0.2, 0.8),
        width=0.025,
      )
      visualizer.add_arrow(
        robot_pos[env_id].detach().cpu().numpy(),
        ball_pos[env_id].detach().cpu().numpy(),
        color=(1.0, 0.45, 0.05, 0.75),
        width=0.02,
      )
      visualizer.add_arrow(
        robot_marker[env_id].detach().cpu().numpy(),
        (robot_marker[env_id] + 0.55 * body_forward[env_id]).detach().cpu().numpy(),
        color=(1.0, 0.05, 0.05, 0.9),
        width=0.025,
      )
      visualizer.add_arrow(
        robot_marker[env_id].detach().cpu().numpy(),
        (robot_marker[env_id] + 0.8 * camera_left[env_id]).detach().cpu().numpy(),
        color=(1.0, 0.1, 0.8, 0.75),
        width=0.015,
      )
      visualizer.add_arrow(
        robot_marker[env_id].detach().cpu().numpy(),
        (robot_marker[env_id] + 0.8 * camera_right[env_id]).detach().cpu().numpy(),
        color=(1.0, 0.1, 0.8, 0.75),
        width=0.015,
      )
      visualizer.add_arrow(
        waypoint[env_id].detach().cpu().numpy(),
        (waypoint[env_id] + 0.5 * torch.cat(
          [ball_to_goal[env_id], torch.zeros(1, device=self._env.device)]
        )).detach().cpu().numpy(),
        color=(0.1, 0.4, 1.0, 0.9),
        width=0.025,
      )


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

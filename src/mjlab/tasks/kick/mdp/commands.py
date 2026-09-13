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

  def _resample_command(self, env_ids: torch.Tensor) -> None:
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
    """Draw kick target (goal), approach waypoint, 3-phase ``P_ref``, and heading aids."""
    from mjlab.tasks.kick.mdp.geometry import behind_ball_waypoint_xy
    from mjlab.tasks.kick.mdp.pref_pose import (
      PHASE_ARC,
      PHASE_SETUP,
      PHASE_STRIKE,
      compute_reference_pose_xy,
    )

    robot = self._env.scene["robot"]
    ball = self._env.scene["ball"]
    env_ids = visualizer.get_env_indices(self._env.num_envs)

    ball_pos = ball.data.root_link_pos_w
    robot_pos = robot.data.root_link_pos_w
    # Goal is a fixed world XY (env-local command + origin). Keep marker height
    # fixed so it does not bob with the ball; only XY jumps on command resample.
    goal_xy = self._command + self._env.scene.env_origins[:, :2]
    goal_z = torch.full(
      (self._env.num_envs, 1), 0.15, device=self._env.device, dtype=ball_pos.dtype
    )
    goal_pos = torch.cat([goal_xy, goal_z], dim=-1)
    goal_dir = goal_xy - ball_pos[:, :2]
    goal_dir = goal_dir / torch.linalg.norm(goal_dir, dim=-1, keepdim=True).clamp(
      min=1.0e-6
    )
    # Short aim arrow (fixed length) — tip moves only if ball moves or goal resamples.
    aim_len = 1.2
    aim_end = torch.cat(
      [
        ball_pos[:, :2] + aim_len * goal_dir,
        ball_pos[:, 2:3] + 0.05,
      ],
      dim=-1,
    )

    # Behind-ball approach waypoint (orbit teacher / waypoint_* rewards).
    wp_xy = behind_ball_waypoint_xy(
      self._env,
      ball_pos[:, :2],
      float(self.cfg.approach_standoff),
      "goal",
    )
    wp_pos = torch.cat([wp_xy, ball_pos[:, 2:3] + 0.04], dim=-1)

    pref_xy, phase = compute_reference_pose_xy(
      self._env,
      command_name="goal",
      arc_radius=self.cfg.arc_radius,
      setup_enter_dist=self.cfg.setup_enter_dist,
      setup_exit_dist=self.cfg.setup_exit_dist,
      setup_behind=self.cfg.setup_behind,
      setup_lateral=self.cfg.setup_lateral,
      prefer_right_foot=self.cfg.prefer_right_foot,
      bearing_thresh=self.cfg.bearing_thresh,
      lateral_thresh=self.cfg.lateral_thresh,
      setup_blend_end=self.cfg.setup_blend_end,
      strike_blend_thresh=self.cfg.strike_blend_thresh,
      setup_pos_thresh=self.cfg.setup_pos_thresh,
      dynamic_kick_foot=self.cfg.dynamic_kick_foot,
    )
    pref_pos = torch.cat([pref_xy, ball_pos[:, 2:3] + 0.02], dim=-1)

    phase_colors = {
      int(PHASE_ARC): (0.15, 0.85, 1.0, 0.95),  # cyan — arc
      int(PHASE_SETUP): (0.2, 0.35, 1.0, 0.95),  # blue — setup
      int(PHASE_STRIKE): (1.0, 0.15, 0.85, 0.95),  # magenta — strike
    }

    body_forward = quat_apply(
      robot.data.root_link_quat_w,
      torch.tensor([1.0, 0.0, 0.0], device=self._env.device).expand_as(robot_pos),
    )
    body_heading = body_forward.clone()
    body_heading[:, 2] = 0.0
    body_heading = body_heading / torch.linalg.norm(
      body_heading, dim=-1, keepdim=True
    ).clamp(min=1.0e-6)
    # Usable FOV cone (fixed forward camera) — matches twist FOV clamp / ball_camera_cone.
    camera_half_angle = float(self.cfg.fov_half_angle)
    cone_range = float(self.cfg.fov_vis_range)
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
      [0.0, 0.0, 0.12], device=self._env.device
    )
    # Arc points across the usable cone at fov_vis_range.
    n_arc = 7
    arc_angles = torch.linspace(
      -camera_half_angle,
      camera_half_angle,
      n_arc,
      device=self._env.device,
      dtype=body_heading.dtype,
    )
    cos_a = torch.cos(arc_angles)
    sin_a = torch.sin(arc_angles)
    # Rotate body_heading by ±angles in XY for each env: [B, n_arc, 2]
    hx = body_heading[:, 0:1]
    hy = body_heading[:, 1:2]
    arc_dir_x = cos_a.unsqueeze(0) * hx - sin_a.unsqueeze(0) * hy
    arc_dir_y = sin_a.unsqueeze(0) * hx + cos_a.unsqueeze(0) * hy
    arc_pts = torch.stack(
      [
        robot_marker[:, 0:1] + cone_range * arc_dir_x,
        robot_marker[:, 1:2] + cone_range * arc_dir_y,
        robot_marker[:, 2:3].expand(-1, n_arc),
      ],
      dim=-1,
    )  # [B, n_arc, 3]
    for env_id in env_ids:
      visualizer.add_sphere(
        ball_pos[env_id].detach().cpu().numpy(),
        radius=0.11,
        color=(1.0, 0.35, 0.05, 0.9),
        label="ball",
      )
      # Fixed kick-target location (world).
      visualizer.add_sphere(
        goal_pos[env_id].detach().cpu().numpy(),
        radius=0.18,
        color=(0.1, 1.0, 0.2, 0.95),
        label="kick_target",
      )
      # Short aim direction from ball (not a long rubber-band to the target).
      visualizer.add_arrow(
        ball_pos[env_id].detach().cpu().numpy(),
        aim_end[env_id].detach().cpu().numpy(),
        color=(0.1, 1.0, 0.2, 0.9),
        width=0.03,
        label="kick_aim",
      )
      # Approach waypoint (yellow) + robot→waypoint (waypoint_approach direction).
      visualizer.add_sphere(
        wp_pos[env_id].detach().cpu().numpy(),
        radius=0.12,
        color=(1.0, 0.85, 0.1, 0.95),
        label="approach_waypoint",
      )
      visualizer.add_arrow(
        robot_pos[env_id].detach().cpu().numpy(),
        wp_pos[env_id].detach().cpu().numpy(),
        color=(1.0, 0.75, 0.05, 0.9),
        width=0.028,
        label="to_approach_waypoint",
      )
      # Ball → waypoint (anti-goal standoff axis).
      visualizer.add_arrow(
        ball_pos[env_id].detach().cpu().numpy(),
        wp_pos[env_id].detach().cpu().numpy(),
        color=(1.0, 0.9, 0.3, 0.55),
        width=0.015,
        label="standoff_axis",
      )
      p = int(phase[env_id].item())
      visualizer.add_sphere(
        pref_pos[env_id].detach().cpu().numpy(),
        radius=0.13,
        color=phase_colors.get(p, (1.0, 1.0, 1.0, 0.9)),
        label="pref_pose",
      )
      visualizer.add_arrow(
        robot_pos[env_id].detach().cpu().numpy(),
        pref_pos[env_id].detach().cpu().numpy(),
        color=phase_colors.get(p, (1.0, 1.0, 1.0, 0.85)),
        width=0.022,
        label="to_pref_pose",
      )
      visualizer.add_arrow(
        robot_marker[env_id].detach().cpu().numpy(),
        (robot_marker[env_id] + 0.55 * body_forward[env_id]).detach().cpu().numpy(),
        color=(1.0, 0.05, 0.05, 0.9),
        width=0.025,
        label="body_forward",
      )
      # FOV usable cone (cyan): left/right edges + far arc.
      cone_color = (0.2, 0.85, 1.0, 0.85)
      visualizer.add_arrow(
        robot_marker[env_id].detach().cpu().numpy(),
        (robot_marker[env_id] + cone_range * camera_left[env_id]).detach().cpu().numpy(),
        color=cone_color,
        width=0.022,
        label="fov_cone_left",
      )
      visualizer.add_arrow(
        robot_marker[env_id].detach().cpu().numpy(),
        (robot_marker[env_id] + cone_range * camera_right[env_id]).detach().cpu().numpy(),
        color=cone_color,
        width=0.022,
        label="fov_cone_right",
      )
      visualizer.add_arrow(
        robot_marker[env_id].detach().cpu().numpy(),
        (robot_marker[env_id] + cone_range * body_heading[env_id]).detach().cpu().numpy(),
        color=(0.4, 0.95, 1.0, 0.55),
        width=0.012,
        label="fov_cone_center",
      )
      for i in range(n_arc - 1):
        visualizer.add_arrow(
          arc_pts[env_id, i].detach().cpu().numpy(),
          arc_pts[env_id, i + 1].detach().cpu().numpy(),
          color=cone_color,
          width=0.018,
          label="fov_cone_arc",
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

  # Pref-pose debug-vis knobs (match Arc→Setup→Strike reward geometry).
  arc_radius: float = 0.4
  setup_enter_dist: float = 0.9
  setup_exit_dist: float = 1.0
  setup_behind: float = 0.35
  setup_lateral: float = 0.12
  prefer_right_foot: bool = True
  bearing_thresh: float = 0.2
  lateral_thresh: float = 0.05
  setup_blend_end: float = 0.20
  strike_blend_thresh: float = 0.75
  setup_pos_thresh: float = 0.28
  dynamic_kick_foot: bool = True
  # Approach waypoint standoff (behind ball along −goal); matches orbit teacher.
  approach_standoff: float = 0.40
  # Usable FOV half-angle (rad) for debug cone — 75% of 105° HFOV ≈ 0.69.
  fov_half_angle: float = 0.69
  # Length of FOV cone rays / arc in play (m).
  fov_vis_range: float = 2.5

  def build(self, env: ManagerBasedRlEnv) -> UniformGoalPositionCommand:
    return UniformGoalPositionCommand(self, env)

"""Shared kick-approach geometry helpers."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_LATCH_ATTR = "_kick_waypoint_latch"


@dataclass
class ApproachWaypointLatch:
  """Per-env spawn-side offset for the yellow approach waypoint."""

  side: torch.Tensor  # [B] +1 left of goal axis, −1 right, 0 on-axis
  lateral: torch.Tensor  # [B] metres
  at_plant: torch.Tensor  # [B] bool — arrived and aligned; sticky until reset
  ready_time_s: torch.Tensor  # [B] continuous time inside the ready gate


def get_approach_waypoint_latch(
  env: ManagerBasedRlEnv,
) -> ApproachWaypointLatch | None:
  latch = getattr(env, _LATCH_ATTR, None)
  if (
    latch is None
    or latch.side.shape[0] != env.num_envs
    or not hasattr(latch, "at_plant")
    or not hasattr(latch, "ready_time_s")
  ):
    return None
  return latch


def ensure_approach_waypoint_latch(
  env: ManagerBasedRlEnv,
) -> ApproachWaypointLatch:
  latch = get_approach_waypoint_latch(env)
  if latch is None:
    n = env.num_envs
    latch = ApproachWaypointLatch(
      side=torch.zeros(n, device=env.device),
      lateral=torch.zeros(n, device=env.device),
      at_plant=torch.zeros(n, dtype=torch.bool, device=env.device),
      ready_time_s=torch.zeros(n, device=env.device),
    )
    setattr(env, _LATCH_ATTR, latch)
  return latch


def update_plant_arrival_latch(
  env: ManagerBasedRlEnv,
  wp_dist: torch.Tensor,
  facing: torch.Tensor,
  ready_distance: float,
  facing_min: float = 0.5,
  hold_time_s: float = 0.0,
) -> torch.Tensor:
  """Sticky plant latch after continuously satisfying distance and alignment."""
  latch = ensure_approach_waypoint_latch(env)
  ready = (wp_dist <= float(ready_distance)) & (facing >= float(facing_min))
  latch.ready_time_s = torch.where(
    ready,
    latch.ready_time_s + float(env.step_dt),
    torch.zeros_like(latch.ready_time_s),
  )
  arrived = ready & (latch.ready_time_s >= float(hold_time_s))
  latch.at_plant = latch.at_plant | arrived
  return latch.at_plant


def ball_to_goal_direction_xy(
  env: ManagerBasedRlEnv,
  ball_pos_xy: torch.Tensor,
  command_name: str,
) -> torch.Tensor:
  """Unit vector from the ball to the goal in world XY."""
  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  goal_pos = command[:, :2] + env.scene.env_origins[:, :2]
  ball_to_goal = goal_pos - ball_pos_xy
  return ball_to_goal / torch.linalg.norm(ball_to_goal, dim=-1, keepdim=True).clamp(
    min=1.0e-6
  )


def rotate90_ccw_xy(v: torch.Tensor) -> torch.Tensor:
  """Rotate planar vectors 90° counter-clockwise."""
  return torch.stack((-v[:, 1], v[:, 0]), dim=-1)


def nearest_foot_kick_side(
  robot_xy: torch.Tensor,
  ball_xy: torch.Tensor,
  goal_dir: torch.Tensor,
  hip_half_width: float = 0.095,
) -> torch.Tensor:
  """``+1`` if the right foot is closer to the kick axis (right kick), else ``-1``.

  The robot faces the ball, so both hips are the same distance from the ball
  centre. The inside leg is the hip with smaller lateral offset from
  ball→goal; that foot becomes the kicker.
  """
  to_ball = ball_xy - robot_xy
  fwd = to_ball / torch.linalg.norm(to_ball, dim=-1, keepdim=True).clamp(min=1.0e-6)
  left = rotate90_ccw_xy(fwd)
  hip = float(hip_half_width)
  left_xy = robot_xy + left * hip
  right_xy = robot_xy - left * hip

  def _axis_offset(foot_xy: torch.Tensor) -> torch.Tensor:
    rel = foot_xy - ball_xy
    return (goal_dir[:, 0] * rel[:, 1] - goal_dir[:, 1] * rel[:, 0]).abs()

  return torch.where(
    _axis_offset(right_xy) <= _axis_offset(left_xy),
    torch.ones(robot_xy.shape[0], device=robot_xy.device, dtype=robot_xy.dtype),
    -torch.ones(robot_xy.shape[0], device=robot_xy.device, dtype=robot_xy.dtype),
  )


def expected_ballistic_speed(
  target_range: torch.Tensor,
  launch_angle: float = math.pi / 4.0,
  gravity: float = 9.81,
) -> torch.Tensor:
  """Launch speed required for planar range ``R = v² sin(2θ) / g``."""
  sin_double_angle = max(math.sin(2.0 * float(launch_angle)), 1.0e-6)
  return torch.sqrt(target_range.clamp(min=0.0) * float(gravity) / sin_double_angle)


def offset_behind_ball_waypoint_xy(
  ball_pos_xy: torch.Tensor,
  goal_dir: torch.Tensor,
  target_distance: float | torch.Tensor,
  side: torch.Tensor | None = None,
  lateral: torch.Tensor | None = None,
) -> torch.Tensor:
  """Behind-ball waypoint, optionally shifted off the goal axis.

  ``side`` +1 is left of the goal axis looking toward the goal (right-foot
  kick plant); −1 is the mirror. ``lateral`` is metres. Hip half-width is
  ~0.095 m, so 0.08–0.12 m puts the swing foot on the kick line.
  """
  if isinstance(target_distance, torch.Tensor):
    waypoint = ball_pos_xy - goal_dir * target_distance.unsqueeze(-1)
  else:
    waypoint = ball_pos_xy - goal_dir * float(target_distance)
  if side is None or lateral is None:
    return waypoint
  left = rotate90_ccw_xy(goal_dir)
  return waypoint + left * (side * lateral).unsqueeze(-1)


def behind_ball_waypoint_xy(
  env: ManagerBasedRlEnv,
  ball_pos_xy: torch.Tensor,
  target_distance: float,
  command_name: str,
  collapse_when_planted: bool = True,
) -> torch.Tensor:
  """Target-side approach point behind the ball.

  Uses the spawn-latched lateral offset on ``env`` when present. After the
  plant latch, standoff collapses to 0 so yellow sits beside the ball
  (swing foot on the kick line).
  """
  ball_to_goal = ball_to_goal_direction_xy(env, ball_pos_xy, command_name)
  latch = get_approach_waypoint_latch(env)
  side = None if latch is None else latch.side
  lateral = None if latch is None else latch.lateral
  dist: float | torch.Tensor = float(target_distance)
  if latch is not None and collapse_when_planted:
    zeros = torch.zeros(
      ball_pos_xy.shape[0], device=ball_pos_xy.device, dtype=ball_pos_xy.dtype
    )
    ones = torch.full(
      (ball_pos_xy.shape[0],),
      float(target_distance),
      device=ball_pos_xy.device,
      dtype=ball_pos_xy.dtype,
    )
    dist = torch.where(latch.at_plant, zeros, ones)
  return offset_behind_ball_waypoint_xy(ball_pos_xy, ball_to_goal, dist, side, lateral)

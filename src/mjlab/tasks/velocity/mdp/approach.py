"""Approach stage: ball position replaces the linear velocity command.

The actor keeps the stage-1 width and only sees what the robot can know on
hardware:

- 72–73: ball xy in the trunk frame, zero when the head camera cannot see it.
- 74: unused, always zero.
- 75–77: this episode's limits on |vx|, |vy| and |wz|.
- 78–79: kick direction (cos, sin) in the yaw frame, from the last seen ball.
- 80–82: kick-range one-hot. Nothing rewards it here; stage 3 inherits it.

The critic reads the true ball in 72–73.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import torch

from mjlab.entity import Entity
from mjlab.managers.command_manager import CommandTerm, CommandTermCfg
from mjlab.utils.lab_api.math import (
  quat_apply,
  quat_apply_inverse,
  wrap_to_pi,
  yaw_quat,
)

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv
  from mjlab.viewer.debug_visualizer import DebugVisualizer


FOV_HALF_ANGLE = 0.69
WEDGE_HALF_ANGLE = math.pi / 4.0
STAND_DISTANCE = 0.5
YAW_ALIGN_LIMIT = 0.4
# Body-heading shaping starts this far from the ball, inside the wedge, so the
# robot lines up on the way in rather than turning next to the ball.
HEADING_SHAPING_DISTANCE = 1.5
BALL_DISTANCE_RANGE = (1.0, 4.0)
TARGET_DISTANCE_RANGE = (4.0, 8.0)
# Ball spawn bearing from the trunk heading; inside the camera cone with margin
# for the head yaw of the reset pose.
SPAWN_VIEW_HALF_ANGLE = 0.4
# Per-episode speed limits, inside what the stage-1 walk tracks well.
SPEED_LIMIT_VX = (0.3, 1.2)
SPEED_LIMIT_VY = (0.2, 1.0)
SPEED_LIMIT_WZ = (0.4, 1.25)
BALL_RADIUS = 0.08
# Pelvis height used only to put the ball on the ground under the robot.
NOMINAL_ROOT_HEIGHT = 0.53
VIEW_SIGMA = 0.35
# Nonzero linear command until the robot is lined up, so the gait terms stay
# on while it walks or turns. The actor does not see this value.
WALK_COMMAND_SPEED = 0.6
RANGE_SHORT_MAX = 4.0 + (8.0 - 4.0) / 3.0
RANGE_MEDIUM_MAX = 4.0 + 2.0 * (8.0 - 4.0) / 3.0
# Debug drawing (play only).
TARGET_MARKER_HEIGHT = 0.3
FOV_VIS_RANGE = 3.0
_TARGET_COLOR = (1.0, 0.8, 0.1, 0.9)
_FOV_SEEN_COLOR = (0.2, 0.9, 0.3, 0.8)
_FOV_LOST_COLOR = (0.95, 0.2, 0.2, 0.8)


def approach_alpha(
  robot_xy: torch.Tensor, ball_xy: torch.Tensor, target_xy: torch.Tensor
) -> torch.Tensor:
  """Signed angle at the ball from the approach line to the robot.

  Zero means the robot is on the approach side of the ball-to-target line.
  """
  axis = ball_xy - target_xy
  to_robot = robot_xy - ball_xy
  cross = axis[:, 0] * to_robot[:, 1] - axis[:, 1] * to_robot[:, 0]
  dot = (axis * to_robot).sum(dim=-1)
  return torch.atan2(cross, dot)


def range_one_hot(
  distance: torch.Tensor,
  short_max: float = RANGE_SHORT_MAX,
  medium_max: float = RANGE_MEDIUM_MAX,
) -> torch.Tensor:
  """Three-way one-hot of a ball-to-target distance: short, medium, long."""
  short = distance < short_max
  medium = (distance >= short_max) & (distance < medium_max)
  strong = distance >= medium_max
  return torch.stack((short, medium, strong), dim=-1).to(dtype=distance.dtype)


def sample_binned(
  n: int, bins: tuple[tuple[float, float], ...], device: torch.device | str
) -> torch.Tensor:
  """Pick a bin uniformly, then a value uniformly inside it."""
  edges = torch.tensor(bins, device=device, dtype=torch.float32)
  which = torch.randint(len(bins), (n,), device=device)
  low, high = edges[which, 0], edges[which, 1]
  return low + torch.rand(n, device=device) * (high - low)


def stand_yaw_quality(yaw_error: torch.Tensor) -> torch.Tensor:
  """Yaw score in [0, 1]: a sharp peak on the line plus a linear ramp.

  A Gaussian alone is flat far from the line (e^-58 at 1.9 rad for σ=0.25),
  so a robot parked sideways got no signal to turn.
  """
  peak = torch.exp(-torch.square(yaw_error) / 0.25**2)
  ramp = 1.0 - yaw_error.abs() / math.pi
  return 0.5 * peak + 0.5 * ramp


def camera_angles(
  ball_in_head: torch.Tensor, camera_pitch: float = 0.0
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
  """Depth, azimuth and elevation of the ball in the camera frame.

  ``camera_pitch`` tilts the optical axis down from the head x-axis (rad).
  The angles are pinhole image angles, atan2(y, x) and atan2(z, x).
  """
  c, s = math.cos(camera_pitch), math.sin(camera_pitch)
  x = c * ball_in_head[:, 0] - s * ball_in_head[:, 2]
  y = ball_in_head[:, 1]
  z = s * ball_in_head[:, 0] + c * ball_in_head[:, 2]
  return x, torch.atan2(y, x), torch.atan2(z, x)


def fov_edge_rays(
  half_h: float, half_v: float | None, camera_pitch: float = 0.0
) -> torch.Tensor:
  """Unit edge rays of the camera cone in the head frame, the inverse of
  ``camera_angles``. Two horizontal edges, or four corners with ``half_v``."""
  if half_v is None:
    corners = [(half_h, 0.0), (-half_h, 0.0)]
  else:
    corners = [(a, e) for a in (half_h, -half_h) for e in (half_v, -half_v)]
  c, s = math.cos(camera_pitch), math.sin(camera_pitch)
  rays = []
  for az, el in corners:
    xc, yc, zc = 1.0, math.tan(az), math.tan(el)
    rays.append((c * xc + s * zc, yc, -s * xc + c * zc))
  out = torch.tensor(rays)
  return out / out.norm(dim=-1, keepdim=True)


def in_camera_view(
  depth: torch.Tensor,
  azimuth: torch.Tensor,
  elevation: torch.Tensor,
  half_h: float,
  half_v: float | None,
) -> torch.Tensor:
  """In front of the camera and inside the cone. ``half_v=None`` skips elevation."""
  visible = (depth > 0.0) & (azimuth.abs() <= half_h)
  if half_v is not None:
    visible = visible & (elevation.abs() <= half_v)
  return visible


def view_angle_excess(
  azimuth: torch.Tensor,
  elevation: torch.Tensor,
  half_h: float,
  half_v: float | None,
) -> torch.Tensor:
  """Angle by which the ball sits outside the camera cone, zero inside."""
  outside = torch.clamp(azimuth.abs() - half_h, min=0.0)
  if half_v is not None:
    outside = torch.hypot(outside, torch.clamp(elevation.abs() - half_v, min=0.0))
  return outside


def speed_limit_excess(
  lin_vel_b: torch.Tensor, yaw_rate: torch.Tensor, limits: torch.Tensor
) -> torch.Tensor:
  """Summed excess of |vx|, |vy| and |wz| over ``limits`` ([N, 3])."""
  speed = torch.cat((lin_vel_b[:, :2].abs(), yaw_rate.abs().unsqueeze(-1)), dim=-1)
  return torch.clamp(speed - limits, min=0.0).sum(dim=-1)


def kick_direction_b(
  target_xy: torch.Tensor, ball_xy: torch.Tensor, robot_quat: torch.Tensor
) -> torch.Tensor:
  """Unit ball-to-target direction in the robot yaw frame, as (cos, sin)."""
  to_target = torch.zeros(
    target_xy.shape[0], 3, device=target_xy.device, dtype=target_xy.dtype
  )
  to_target[:, :2] = target_xy - ball_xy
  dir_w = to_target / to_target.norm(dim=-1, keepdim=True).clamp(min=1.0e-6)
  return quat_apply_inverse(yaw_quat(robot_quat), dir_w)[:, :2]


def _root_pose(robot: Entity, env_ids: torch.Tensor) -> torch.Tensor:
  """Root pose from qpos, valid before the next forward()."""
  adr = robot.data.indexing.free_joint_q_adr
  return robot.data.data.qpos[env_ids][:, adr]


def _yaw_angle(quat: torch.Tensor) -> torch.Tensor:
  qw, qx, qy, qz = quat[:, 0], quat[:, 1], quat[:, 2], quat[:, 3]
  return torch.atan2(2.0 * (qw * qz + qx * qy), 1.0 - 2.0 * (qy * qy + qz * qz))


class ApproachYawCommand(CommandTerm):
  """Ball, target and speed limits for one approach episode."""

  cfg: ApproachYawCommandCfg

  def __init__(self, cfg: ApproachYawCommandCfg, env: ManagerBasedRlEnv):
    super().__init__(cfg, env)
    self.robot: Entity = env.scene[cfg.entity_name]
    self.ball: Entity = env.scene[cfg.ball_name]
    head_ids, _ = self.robot.find_bodies("Head_2")
    self._head_id = int(head_ids[0])

    n = self.num_envs
    device = self.device
    self.vel_command_b = torch.zeros(n, 3, device=device)
    self.target_w = torch.zeros(n, 2, device=device)
    self.target_dist = torch.full((n,), 4.0, device=device)
    self.speed_limit = torch.zeros(n, 3, device=device)
    self.last_seen_ball_w = torch.zeros(n, 2, device=device)
    self.prev_abs_alpha = torch.zeros(n, device=device)
    self.prev_abs_yaw_error = torch.zeros(n, device=device)
    self.prev_dist = torch.ones(n, device=device)
    self.prev_in_wedge = torch.zeros(n, dtype=torch.bool, device=device)
    self.masked_ball_b = torch.zeros(n, 2, device=device)
    self.true_ball_b = torch.zeros(n, 2, device=device)
    self.see_ball = torch.zeros(n, device=device)
    self.kick_dir_b = torch.zeros(n, 2, device=device)
    self.kick_range = torch.zeros(n, 3, device=device)
    self.abs_alpha = torch.zeros(n, device=device)
    self.dist = torch.ones(n, device=device)
    self.in_wedge = torch.zeros(n, dtype=torch.bool, device=device)
    self.yaw_error = torch.zeros(n, device=device)
    self.azimuth = torch.zeros(n, device=device)
    self.time_since_seen = torch.zeros(n, device=device)
    # exp(-time since seen / tau); only filled with ``ball_memory``.
    self.ball_age_obs = torch.zeros(n, device=device)
    self.metrics["abs_alpha"] = torch.zeros(n, device=device)
    self.metrics["see_ball"] = torch.zeros(n, device=device)

  @property
  def command(self) -> torch.Tensor:
    return self.vel_command_b

  def _update_metrics(self) -> None:
    self.metrics["abs_alpha"][:] = self.abs_alpha
    self.metrics["see_ball"][:] = self.see_ball

  def _resample_command(self, env_ids: torch.Tensor) -> None:
    self._spawn_ball_and_target(env_ids)
    ranges = (self.cfg.speed_limit_vx, self.cfg.speed_limit_vy, self.cfg.speed_limit_wz)
    for i, (low, high) in enumerate(ranges):
      self.speed_limit[env_ids, i] = torch.empty(
        len(env_ids), device=self.device
      ).uniform_(low, high)

  def _update_command(self) -> None:
    alpha, dist, in_wedge, yaw_error, azimuth, _, visible, true_ball_b = self._measure()
    self.prev_abs_alpha[:] = alpha.abs()
    self.prev_abs_yaw_error[:] = yaw_error.abs()
    self.prev_dist[:] = dist
    self.prev_in_wedge[:] = in_wedge
    self.abs_alpha[:] = alpha.abs()
    self.dist[:] = dist
    self.in_wedge[:] = in_wedge
    self.yaw_error[:] = yaw_error
    self.azimuth[:] = azimuth
    self.see_ball[:] = visible.float()
    self.true_ball_b[:] = true_ball_b
    seen_b = true_ball_b
    base_sigma, rel_sigma = self.cfg.ball_obs_noise
    if base_sigma > 0.0 or rel_sigma > 0.0:
      # Vision noise grows with range: sigma = base + rel * distance.
      sigma = base_sigma + rel_sigma * true_ball_b.norm(dim=-1, keepdim=True)
      seen_b = true_ball_b + sigma * torch.randn_like(true_ball_b)
    self.masked_ball_b[:] = seen_b * visible.unsqueeze(-1)

    # The kick direction uses the ball only where the camera last saw it.
    ball_pos = self.ball.data.root_link_pos_w
    self.last_seen_ball_w[:] = torch.where(
      visible.unsqueeze(-1), ball_pos[:, :2], self.last_seen_ball_w
    )
    self.time_since_seen[:] = torch.where(
      visible, torch.zeros_like(dist), self.time_since_seen + self._env.step_dt
    )
    if self.cfg.ball_memory:
      # Out of view, report where the ball was last seen, in the current
      # trunk frame (on hardware: the ball model carried by odometry).
      robot_pos = self.robot.data.root_link_pos_w
      rel = torch.zeros_like(robot_pos)
      rel[:, :2] = self.last_seen_ball_w - robot_pos[:, :2]
      rel[:, 2] = ball_pos[:, 2] - robot_pos[:, 2]
      memory_b = quat_apply_inverse(self.robot.data.root_link_quat_w, rel)[:, :2]
      self.masked_ball_b[:] = torch.where(visible.unsqueeze(-1), seen_b, memory_b)
      self.ball_age_obs[:] = torch.exp(-self.time_since_seen / self.cfg.ball_memory_tau)
    self.kick_dir_b[:] = kick_direction_b(
      self.target_w, self.last_seen_ball_w, self.robot.data.root_link_quat_w
    )
    # Range from the last seen ball, so it tracks a ball that has moved.
    self.target_dist[:] = (self.target_w - self.last_seen_ball_w).norm(dim=-1)
    self.kick_range[:] = range_one_hot(self.target_dist, *self.cfg.range_edges)

    lined_up = (
      in_wedge & (dist <= STAND_DISTANCE) & (yaw_error.abs() <= YAW_ALIGN_LIMIT)
    )
    self.vel_command_b[:, 0] = torch.where(
      lined_up, torch.zeros_like(dist), torch.full_like(dist, WALK_COMMAND_SPEED)
    )
    self.vel_command_b[:, 1:] = 0.0

  def _debug_vis_impl(self, visualizer: DebugVisualizer) -> None:
    """Target, ball-to-target line, and camera FOV edges (green: ball seen)."""
    env_ids = list(visualizer.get_env_indices(self.num_envs))
    if not env_ids:
      return
    head_pos = self.robot.data.body_link_pos_w[env_ids, self._head_id]
    head_quat = self.robot.data.body_link_quat_w[env_ids, self._head_id]
    rays = fov_edge_rays(
      self.cfg.fov_half_angle,
      self.cfg.fov_vertical_half_angle,
      self.cfg.camera_pitch,
    ).to(head_quat)
    n, r = len(env_ids), rays.shape[0]
    rays_w = quat_apply(
      head_quat.repeat_interleave(r, dim=0), rays.repeat(n, 1)
    ).reshape(n, r, 3)
    ends = head_pos.unsqueeze(1) + FOV_VIS_RANGE * rays_w

    target = self.target_w[env_ids].cpu().numpy()
    ball = self.ball.data.root_link_pos_w[env_ids].cpu().numpy()
    head = head_pos.cpu().numpy()
    ends = ends.cpu().numpy()
    seen = self.see_ball[env_ids].cpu().numpy() > 0.5
    for k in range(n):
      base = np.array([target[k, 0], target[k, 1], 0.0])
      top = base + np.array([0.0, 0.0, TARGET_MARKER_HEIGHT])
      visualizer.add_cylinder(base, top, 0.02, _TARGET_COLOR, label="target")
      visualizer.add_sphere(top, 0.08, _TARGET_COLOR, label="target")
      ground_ball = np.array([ball[k, 0], ball[k, 1], 0.02])
      visualizer.add_cylinder(
        ground_ball, base + np.array([0.0, 0.0, 0.02]), 0.008, _TARGET_COLOR
      )
      color = _FOV_SEEN_COLOR if seen[k] else _FOV_LOST_COLOR
      for end in ends[k]:
        visualizer.add_cylinder(head[k], end, 0.006, color, label="fov")

  def _spawn_ball_and_target(self, env_ids: torch.Tensor) -> None:
    n = len(env_ids)
    if n == 0:
      return
    device = self.device
    pose = _root_pose(self.robot, env_ids)
    robot_xy = pose[:, 0:2]
    robot_yaw = _yaw_angle(pose[:, 3:7])
    ball_z = pose[:, 2] - NOMINAL_ROOT_HEIGHT + BALL_RADIUS

    # The robot faces the ball; the kick line can point anywhere.
    half = self.cfg.spawn_view_half_angle
    angle = robot_yaw + torch.empty(n, device=device).uniform_(-half, half)
    radius = torch.empty(n, device=device).uniform_(*BALL_DISTANCE_RANGE)
    offset = torch.stack((angle.cos(), angle.sin()), dim=-1) * radius.unsqueeze(-1)
    ball_xy = robot_xy + offset
    self.last_seen_ball_w[env_ids] = ball_xy
    self.time_since_seen[env_ids] = 0.0
    self._place_target(env_ids, ball_xy)

    state = self.ball.data.default_root_state[env_ids].clone()
    state[:, 0:2] = ball_xy
    state[:, 2] = ball_z
    state[:, 3:7] = 0.0
    state[:, 3] = 1.0
    state[:, 7:] = 0.0
    self.ball.write_root_state_to_sim(state, env_ids)

  def _place_target(self, env_ids: torch.Tensor, ball_xy: torch.Tensor) -> None:
    """New target in a random direction from ``ball_xy``, at a binned distance."""
    n = len(env_ids)
    angle = torch.rand(n, device=self.device) * (2.0 * math.pi)
    dist = sample_binned(n, self.cfg.target_distance_bins, self.device)
    offset = torch.stack((angle.cos(), angle.sin()), dim=-1) * dist.unsqueeze(-1)
    self.target_w[env_ids] = ball_xy + offset
    self.target_dist[env_ids] = dist

  def _measure(
    self,
  ) -> tuple[
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
  ]:
    """True-state geometry: alpha, dist, in_wedge, yaw_error, azimuth,
    elevation, visible, true_ball_b."""
    robot_pos = self.robot.data.root_link_pos_w
    robot_quat = self.robot.data.root_link_quat_w
    ball_pos = self.ball.data.root_link_pos_w
    head_pos = self.robot.data.body_link_pos_w[:, self._head_id]
    head_quat = self.robot.data.body_link_quat_w[:, self._head_id]

    alpha = approach_alpha(robot_pos[:, :2], ball_pos[:, :2], self.target_w)
    dist = torch.linalg.norm(robot_pos[:, :2] - ball_pos[:, :2], dim=-1)
    in_wedge = alpha.abs() <= WEDGE_HALF_ANGLE

    to_target = self.target_w - ball_pos[:, :2]
    kick_heading = torch.atan2(to_target[:, 1], to_target[:, 0])
    yaw_error = wrap_to_pi(kick_heading - _yaw_angle(robot_quat))

    head_rel = quat_apply_inverse(head_quat, ball_pos - head_pos)
    depth, azimuth, elevation = camera_angles(head_rel, self.cfg.camera_pitch)
    visible = in_camera_view(
      depth,
      azimuth,
      elevation,
      self.cfg.fov_half_angle,
      self.cfg.fov_vertical_half_angle,
    )

    true_ball_b = quat_apply_inverse(robot_quat, ball_pos - robot_pos)[:, :2]
    return (
      alpha,
      dist,
      in_wedge,
      yaw_error,
      azimuth,
      elevation,
      visible,
      true_ball_b,
    )


@dataclass(kw_only=True)
class ApproachYawCommandCfg(CommandTermCfg):
  """Approach command. Resamples only on reset."""

  entity_name: str = "robot"
  ball_name: str = "ball"
  resampling_time_range: tuple[float, float] = (1.0e6, 1.0e6)
  debug_vis: bool = False
  fov_half_angle: float = FOV_HALF_ANGLE
  """Horizontal half-angle of the head camera (rad)."""
  fov_vertical_half_angle: float | None = None
  """Vertical half-angle of the head camera (rad). ``None`` skips the check.

  Take it from the robot or the datasheet minus a margin. Err small: a cone
  larger than the real camera trains the policy on views it will not get.
  """
  camera_pitch: float = 0.0
  """Pitch of the optical axis below the head link x-axis (rad, positive down)."""
  spawn_view_half_angle: float = SPAWN_VIEW_HALF_ANGLE
  """Max bearing of the spawned ball from the trunk heading (rad)."""
  speed_limit_vx: tuple[float, float] = SPEED_LIMIT_VX
  speed_limit_vy: tuple[float, float] = SPEED_LIMIT_VY
  speed_limit_wz: tuple[float, float] = SPEED_LIMIT_WZ
  target_distance_bins: tuple[tuple[float, float], ...] = (TARGET_DISTANCE_RANGE,)
  """Ball-to-target distance bins (m); a bin is picked uniformly, then a value."""
  range_edges: tuple[float, float] = (RANGE_SHORT_MAX, RANGE_MEDIUM_MAX)
  ball_memory: bool = False
  """Out of view, give the last-seen ball (in the current trunk frame) instead
  of zeros, and its age in slot 74. Off for the approach stage."""
  ball_memory_tau: float = 2.0
  ball_obs_noise: tuple[float, float] = (0.0, 0.0)
  """Actor ball noise while seen: sigma = base + rel * distance (m, per axis)."""
  """Age time constant (s): slot 74 = exp(-time since seen / tau)."""
  """Short/medium and medium/long edges of the kick-range one-hot (m)."""

  def build(self, env: ManagerBasedRlEnv) -> ApproachYawCommand:
    return ApproachYawCommand(self, env)


def _command(env: ManagerBasedRlEnv) -> ApproachYawCommand:
  term = env.command_manager.get_term("twist")
  assert isinstance(term, ApproachYawCommand)
  return term


def approach_command_obs(
  env: ManagerBasedRlEnv, privileged: bool = False
) -> torch.Tensor:
  """Ball xy, then slot 74.

  The actor's ball is masked to the camera view: zero when unseen, or the
  last-seen position with ``ball_memory``. Slot 74 is the memory age
  exp(-t/tau) with ``ball_memory``, else zero. The critic gets the true ball.
  """
  cmd = _command(env)
  ball = cmd.true_ball_b if privileged else cmd.masked_ball_b
  return torch.cat((ball, cmd.ball_age_obs.unsqueeze(-1)), dim=-1)


def approach_speed_limit_obs(env: ManagerBasedRlEnv) -> torch.Tensor:
  """This episode's limits on |vx|, |vy| and |wz|."""
  return _command(env).speed_limit


def approach_kick_direction_obs(env: ManagerBasedRlEnv) -> torch.Tensor:
  return _command(env).kick_dir_b


def approach_kick_range_obs(env: ManagerBasedRlEnv) -> torch.Tensor:
  return _command(env).kick_range


def _current(env: ManagerBasedRlEnv):
  return _command(env)._measure()


def approach_align(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Signed reduction in |α|. Growing the angle costs the same amount."""
  cmd = _command(env)
  alpha, _, _, _, _, _, _, _ = _current(env)
  env.extras["log"]["Metrics/approach_abs_alpha"] = alpha.abs().mean()
  return cmd.prev_abs_alpha - alpha.abs()


def approach_close(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Signed closing speed along the wedge, and a cost for leaving the stand disk."""
  cmd = _command(env)
  _, dist, _, _, _, _, _, _ = _current(env)
  delta = cmd.prev_dist - dist
  closing = cmd.prev_in_wedge & (cmd.prev_dist > STAND_DISTANCE)
  leaving = (
    cmd.prev_in_wedge & (cmd.prev_dist <= STAND_DISTANCE) & (dist > STAND_DISTANCE)
  )
  env.extras["log"]["Metrics/approach_ball_dist"] = dist.mean()
  return torch.where(closing | leaving, delta, torch.zeros_like(delta))


def approach_stand(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Near-zero base speed and yaw on the kick line, inside the wedge and 0.5 m."""
  _, dist, in_wedge, yaw_error, _, _, _, _ = _current(env)
  robot: Entity = env.scene["robot"]
  speed = torch.linalg.norm(robot.data.root_link_lin_vel_b[:, :2], dim=-1)
  quality = torch.exp(-torch.square(speed) / 0.15**2) * stand_yaw_quality(yaw_error)
  gate = in_wedge & (dist <= STAND_DISTANCE)
  env.extras["log"]["Metrics/approach_in_stand"] = gate.float().mean()
  return quality * gate.float()


def approach_heading(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Signed reduction in body |yaw error| to the kick line, near the ball.

  Active from the previous step inside the wedge and HEADING_SHAPING_DISTANCE.
  Turning away costs what turning back pays, so only net progress counts.
  """
  cmd = _command(env)
  _, _, in_wedge, yaw_error, _, _, _, _ = _current(env)
  gate = cmd.prev_in_wedge & (cmd.prev_dist <= HEADING_SHAPING_DISTANCE)
  delta = cmd.prev_abs_yaw_error - yaw_error.abs()

  robot: Entity = env.scene["robot"]
  head_quat = robot.data.body_link_quat_w[:, cmd._head_id]
  head_offset = wrap_to_pi(
    _yaw_angle(head_quat) - _yaw_angle(robot.data.root_link_quat_w)
  ).abs()
  near = gate.float()
  log = env.extras["log"]
  log["Metrics/approach_body_yaw_err_near"] = (yaw_error.abs() * near).sum() / (
    near.sum().clamp(min=1.0)
  )
  log["Metrics/approach_head_offset"] = head_offset.mean()
  return torch.where(gate, delta, torch.zeros_like(delta))


def approach_bad_contact(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Foot-ball contact outside the wedge, or with yaw more than 0.4 rad off the line."""
  _, _, in_wedge, yaw_error, _, _, _, _ = _current(env)
  sensor = env.scene["feet_ball_contact"]
  found = sensor.data.found
  if found is None:
    return torch.zeros(env.num_envs, device=env.device)
  touch = found.reshape(env.num_envs, -1).amax(dim=-1) > 0
  bad = touch & (~in_wedge | (yaw_error.abs() > YAW_ALIGN_LIMIT))
  env.extras["log"]["Metrics/approach_bad_contact"] = bad.float().mean()
  return bad.float()


def approach_view(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Full reward inside the head-camera cone, smooth falloff outside it."""
  cmd = _command(env)
  _, _, _, _, azimuth, elevation, visible, _ = _current(env)
  outside = view_angle_excess(
    azimuth, elevation, cmd.cfg.fov_half_angle, cmd.cfg.fov_vertical_half_angle
  )
  reward = torch.exp(-torch.square(outside) / VIEW_SIGMA**2)
  env.extras["log"]["Metrics/approach_see_ball"] = visible.float().mean()
  return reward


def approach_speed_limit(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Summed excess of base |vx|, |vy| and |wz| over this episode's limits."""
  cmd = _command(env)
  robot: Entity = env.scene["robot"]
  excess = speed_limit_excess(
    robot.data.root_link_lin_vel_b,
    robot.data.root_link_ang_vel_b[:, 2],
    cmd.speed_limit,
  )
  env.extras["log"]["Metrics/approach_speed_excess"] = excess.mean()
  return excess

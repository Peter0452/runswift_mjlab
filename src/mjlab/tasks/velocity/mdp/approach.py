"""Approach stage: ball position replaces the linear velocity command.

The actor still has the stage-1 width. Channels 72–73 are the ball in the trunk
frame, masked to zero outside the head camera. Channel 74 is a yaw rate. The
critic reads the true ball through the two spare speed-limit slots so the
network shape matches the stage-1 checkpoint.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch

from mjlab.entity import Entity
from mjlab.managers.command_manager import CommandTerm, CommandTermCfg
from mjlab.utils.lab_api.math import quat_apply_inverse, wrap_to_pi, yaw_quat

if TYPE_CHECKING:
    from mjlab.envs import ManagerBasedRlEnv


FOV_HALF_ANGLE = 0.69
FOV_EDGE_MARGIN = 0.15
YAW_RATE_LIMIT = 1.5
YAW_GAIN = 2.0
WEDGE_HALF_ANGLE = math.pi / 4.0
STAND_DISTANCE = 0.5
YAW_ALIGN_LIMIT = 0.4
BALL_DISTANCE_RANGE = (1.0, 4.0)
TARGET_DISTANCE_RANGE = (4.0, 8.0)
BALL_RADIUS = 0.08
# Pelvis height used only to put the ball on the ground under the robot.
NOMINAL_ROOT_HEIGHT = 0.53
VIEW_SIGMA = 0.35
# Nonzero linear command while walking, so the existing gait terms stay on.
# The actor does not see this value; its first two command channels are the ball.
WALK_COMMAND_SPEED = 0.6
RANGE_SHORT_MAX = 4.0 + (8.0 - 4.0) / 3.0
RANGE_MEDIUM_MAX = 4.0 + 2.0 * (8.0 - 4.0) / 3.0


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


def range_one_hot(distance: torch.Tensor) -> torch.Tensor:
  """Three-way one-hot of a ball-to-target distance in [4, 8] m."""
  short = distance < RANGE_SHORT_MAX
  medium = (distance >= RANGE_SHORT_MAX) & (distance < RANGE_MEDIUM_MAX)
  strong = distance >= RANGE_MEDIUM_MAX
  return torch.stack((short, medium, strong), dim=-1).to(dtype=distance.dtype)


def yaw_rate_toward_line(
  line_error: torch.Tensor,
  azimuth: torch.Tensor,
  visible: torch.Tensor,
  *,
  gain: float = YAW_GAIN,
  limit: float = YAW_RATE_LIMIT,
  fov_half_angle: float = FOV_HALF_ANGLE,
  edge_margin: float = FOV_EDGE_MARGIN,
) -> torch.Tensor:
  """Yaw rate toward the kick line, clamped so the ball stays in view.

  Outside the cone the rate turns toward the ball. Inside it, a turn that
  would push the ball out through the near edge is dropped.
  """
  ball_rate = torch.clamp(gain * azimuth, -limit, limit)
  line_rate = torch.clamp(gain * line_error, -limit, limit)
  margin = fov_half_angle - azimuth.abs()
  pushes_ball_out = (line_rate * azimuth < 0) & (margin < edge_margin)
  clamped = torch.where(pushes_ball_out, torch.zeros_like(line_rate), line_rate)
  return torch.where(visible, clamped, ball_rate)


def _root_pose(robot: Entity, env_ids: torch.Tensor) -> torch.Tensor:
  """Root pose from qpos, valid before the next forward()."""
  adr = robot.data.indexing.free_joint_q_adr
  return robot.data.data.qpos[env_ids][:, adr]


def _yaw_angle(quat: torch.Tensor) -> torch.Tensor:
  qw, qx, qy, qz = quat[:, 0], quat[:, 1], quat[:, 2], quat[:, 3]
  return torch.atan2(2.0 * (qw * qz + qx * qy), 1.0 - 2.0 * (qy * qy + qz * qz))


class ApproachYawCommand(CommandTerm):
  """Yaw-rate command plus the ball and target for one approach episode."""

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
    self.prev_abs_alpha = torch.zeros(n, device=device)
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

  def _update_command(self) -> None:
    alpha, dist, in_wedge, yaw_error, azimuth, visible, true_ball_b, kick_dir_b = (
      self._measure()
    )
    self.prev_abs_alpha[:] = alpha.abs()
    self.prev_dist[:] = dist
    self.prev_in_wedge[:] = in_wedge
    self.abs_alpha[:] = alpha.abs()
    self.dist[:] = dist
    self.in_wedge[:] = in_wedge
    self.yaw_error[:] = yaw_error
    self.azimuth[:] = azimuth
    self.see_ball[:] = visible.float()
    self.true_ball_b[:] = true_ball_b
    self.masked_ball_b[:] = true_ball_b * visible.unsqueeze(-1)
    self.kick_dir_b[:] = kick_dir_b
    self.kick_range[:] = range_one_hot(self.target_dist)

    yaw_rate = yaw_rate_toward_line(yaw_error, azimuth, visible)
    walking = ~(in_wedge & (dist <= STAND_DISTANCE))
    self.vel_command_b[:, 0] = torch.where(
      walking, torch.full_like(dist, WALK_COMMAND_SPEED), torch.zeros_like(dist)
    )
    self.vel_command_b[:, 1] = 0.0
    self.vel_command_b[:, 2] = yaw_rate

  def _spawn_ball_and_target(self, env_ids: torch.Tensor) -> None:
    n = len(env_ids)
    if n == 0:
      return
    device = self.device
    pose = _root_pose(self.robot, env_ids)
    robot_xy = pose[:, 0:2]
    ball_z = pose[:, 2] - NOMINAL_ROOT_HEIGHT + BALL_RADIUS

    angle = torch.rand(n, device=device) * (2.0 * math.pi)
    radius = torch.empty(n, device=device).uniform_(*BALL_DISTANCE_RANGE)
    offset = torch.stack((angle.cos(), angle.sin()), dim=-1) * radius.unsqueeze(-1)
    ball_xy = robot_xy + offset

    target_angle = torch.rand(n, device=device) * (2.0 * math.pi)
    target_dist = torch.empty(n, device=device).uniform_(*TARGET_DISTANCE_RANGE)
    target_offset = torch.stack(
      (target_angle.cos(), target_angle.sin()), dim=-1
    ) * target_dist.unsqueeze(-1)
    self.target_w[env_ids] = ball_xy + target_offset
    self.target_dist[env_ids] = target_dist

    state = self.ball.data.default_root_state[env_ids].clone()
    state[:, 0:2] = ball_xy
    state[:, 2] = ball_z
    state[:, 3:7] = 0.0
    state[:, 3] = 1.0
    state[:, 7:] = 0.0
    self.ball.write_root_state_to_sim(state, env_ids)

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
    robot_pos = self.robot.data.root_link_pos_w
    robot_quat = self.robot.data.root_link_quat_w
    ball_pos = self.ball.data.root_link_pos_w
    head_pos = self.robot.data.body_link_pos_w[:, self._head_id]
    head_quat = self.robot.data.body_link_quat_w[:, self._head_id]

    alpha = approach_alpha(robot_pos[:, :2], ball_pos[:, :2], self.target_w)
    dist = torch.linalg.norm(robot_pos[:, :2] - ball_pos[:, :2], dim=-1)
    in_wedge = alpha.abs() <= WEDGE_HALF_ANGLE

    to_target = torch.zeros_like(robot_pos)
    to_target[:, :2] = self.target_w - ball_pos[:, :2]
    kick_heading = torch.atan2(to_target[:, 1], to_target[:, 0])
    yaw_error = wrap_to_pi(kick_heading - _yaw_angle(robot_quat))

    head_rel = quat_apply_inverse(head_quat, ball_pos - head_pos)
    azimuth = torch.atan2(head_rel[:, 1], head_rel[:, 0])
    visible = (head_rel[:, 0] > 0.0) & (azimuth.abs() <= FOV_HALF_ANGLE)

    true_ball_b = quat_apply_inverse(robot_quat, ball_pos - robot_pos)[:, :2]
    dir_w = to_target / to_target.norm(dim=-1, keepdim=True).clamp(min=1.0e-6)
    kick_dir_b = quat_apply_inverse(yaw_quat(robot_quat), dir_w)[:, :2]
    return (
      alpha,
      dist,
      in_wedge,
      yaw_error,
      azimuth,
      visible,
      true_ball_b,
      kick_dir_b,
    )


@dataclass(kw_only=True)
class ApproachYawCommandCfg(CommandTermCfg):
  """Approach command. Resamples only on reset."""

  entity_name: str = "robot"
  ball_name: str = "ball"
  resampling_time_range: tuple[float, float] = (1.0e6, 1.0e6)
  debug_vis: bool = False

  def build(self, env: ManagerBasedRlEnv) -> ApproachYawCommand:
    return ApproachYawCommand(self, env)


def _command(env: ManagerBasedRlEnv) -> ApproachYawCommand:
  term = env.command_manager.get_term("twist")
  assert isinstance(term, ApproachYawCommand)
  return term


def approach_command_obs(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Actor command: masked ball xy and the yaw rate. The walk-speed flag is hidden."""
  cmd = _command(env)
  return torch.cat((cmd.masked_ball_b, cmd.vel_command_b[:, 2:3]), dim=-1)


def approach_speed_limit_obs(
  env: ManagerBasedRlEnv, privileged: bool = False
) -> torch.Tensor:
  """See-ball flag, then zeros. The critic's last two slots are the true ball."""
  cmd = _command(env)
  zeros = torch.zeros_like(cmd.true_ball_b)
  ball = cmd.true_ball_b if privileged else zeros
  return torch.cat((cmd.see_ball.unsqueeze(-1), ball), dim=-1)


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
    cmd.prev_in_wedge
    & (cmd.prev_dist <= STAND_DISTANCE)
    & (dist > STAND_DISTANCE)
  )
  env.extras["log"]["Metrics/approach_ball_dist"] = dist.mean()
  return torch.where(closing | leaving, delta, torch.zeros_like(delta))


def approach_stand(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Near-zero base speed and yaw on the kick line, inside the wedge and 0.5 m."""
  _, dist, in_wedge, yaw_error, _, _, _, _ = _current(env)
  robot: Entity = env.scene["robot"]
  speed = torch.linalg.norm(robot.data.root_link_lin_vel_b[:, :2], dim=-1)
  quality = torch.exp(-torch.square(speed) / 0.15**2) * torch.exp(
    -torch.square(yaw_error) / 0.25**2
  )
  gate = in_wedge & (dist <= STAND_DISTANCE)
  env.extras["log"]["Metrics/approach_in_stand"] = gate.float().mean()
  return quality * gate.float()


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
  _, _, _, _, azimuth, visible, _, _ = _current(env)
  outside = torch.clamp(azimuth.abs() - FOV_HALF_ANGLE, min=0.0)
  reward = torch.exp(-torch.square(outside) / VIEW_SIGMA**2)
  env.extras["log"]["Metrics/approach_see_ball"] = visible.float().mean()
  return reward

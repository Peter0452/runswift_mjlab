"""Stage-2 kick rewards. The Gaussian target width is 1 m.

Contact is the right foot. Approach terms pay until 1 s after that contact,
then drop out so the follow-through is left to the motion prior.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from mjlab.entity import Entity
from mjlab.tasks.tracking.mdp.shot import kick_shot

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_RIGHT_FOOT = "right_foot_link"
_LEFT_FOOT = "left_foot_link"
_BALL_RADIUS = 0.11


def _body_pos(robot: Entity, name: str) -> torch.Tensor:
  return robot.data.body_link_pos_w[:, robot.body_names.index(name)]


def _kick_is_left(env: ManagerBasedRlEnv) -> torch.Tensor:
  command = env.command_manager.get_term("motion")
  return command.kick_foot_is_left()


def _swing_foot_pos(env: ManagerBasedRlEnv) -> torch.Tensor:
  """World position of the foot the current clip is swinging."""
  robot: Entity = env.scene["robot"]
  right = _body_pos(robot, _RIGHT_FOOT)
  left = _body_pos(robot, _LEFT_FOOT)
  return torch.where(_kick_is_left(env).unsqueeze(-1), left, right)


def _plant_foot_pos(env: ManagerBasedRlEnv) -> torch.Tensor:
  """World position of the foot that is not swinging."""
  robot: Entity = env.scene["robot"]
  right = _body_pos(robot, _RIGHT_FOOT)
  left = _body_pos(robot, _LEFT_FOOT)
  return torch.where(_kick_is_left(env).unsqueeze(-1), right, left)


def _swing_contact_force(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Contact force magnitude between the swinging foot and the ball."""
  is_left = _kick_is_left(env)
  right = env.scene["ball_foot_contact"]
  assert right.data.force is not None
  right_force = torch.linalg.norm(
    right.data.force.reshape(env.num_envs, -1, 3), dim=-1
  ).amax(dim=-1)
  if "ball_left_foot_contact" not in env.scene.sensors:
    return right_force
  left = env.scene["ball_left_foot_contact"]
  assert left.data.force is not None
  left_force = torch.linalg.norm(
    left.data.force.reshape(env.num_envs, -1, 3), dim=-1
  ).amax(dim=-1)
  return torch.where(is_left, left_force, right_force)


def _ball(env: ManagerBasedRlEnv) -> Entity:
  return env.scene["ball"]


def _target_xy(env: ManagerBasedRlEnv) -> torch.Tensor:
  goal_xy = env.command_manager.get_command("goal")
  assert goal_xy is not None
  return goal_xy[:, :2] + env.scene.env_origins[:, :2]


def error_ball_to_target(env: ManagerBasedRlEnv, std: float) -> torch.Tensor:
  """Gaussian on the ball's best distance to the target point."""
  state = kick_shot(env)
  return torch.exp(-(state.min_dist**2) / std**2)


def ball_over_line(env: ManagerBasedRlEnv) -> torch.Tensor:
  """+2 once the ball passes the goal mouth, -1 if it goes behind the robot."""
  ball_x = _ball(env).data.root_link_pos_w[:, 0]
  target_x = _target_xy(env)[:, 0]
  origin_x = env.scene.env_origins[:, 0]
  over = ball_x > target_x
  behind = ball_x < origin_x - 1.0
  return 2.0 * over.float() - behind.float()


def robot_ball_contact_count(env: ManagerBasedRlEnv) -> torch.Tensor:
  """1 after the swinging foot has touched the ball."""
  return kick_shot(env).contacted.float()


def robot_ball_contact(
  env: ManagerBasedRlEnv,
  goal_sigma: float = 2.0,
  feet_sigma: float = 1.0,
  force_threshold: float = 2.0,
  vel_threshold: float = 2.0,
) -> torch.Tensor:
  """Shape the touch by foot proximity, aim, ball speed, and contact force."""
  state = kick_shot(env)
  ball = _ball(env)
  foot = _swing_foot_pos(env)
  ball_pos = ball.data.root_link_pos_w
  gap = (torch.linalg.norm(foot - ball_pos, dim=-1) - _BALL_RADIUS).clamp(1.0e-8, 10.0)
  r_contact = torch.exp(-gap / feet_sigma)
  r_contact = torch.where(state.contacted, torch.ones_like(r_contact), r_contact)

  goal_mask = state.min_dist < 0.5 * goal_sigma
  min_distance = (state.min_dist - 0.5 * goal_sigma).clamp(0.0, 10.0)
  r_goal = torch.exp(-(min_distance**2) / (2 * goal_sigma) ** 2)
  r_goal = torch.where(goal_mask, torch.ones_like(r_goal), r_goal)

  speed = ball.data.root_link_lin_vel_w.norm(dim=-1).clamp(vel_threshold, 10.0)
  r_vel = 1.0 - torch.exp(-((speed - vel_threshold) ** 2) / 10.0).clamp(0.0, 1.0)

  r_force = (_swing_contact_force(env) / force_threshold).clamp(max=1.0)
  return (r_contact + r_goal) * (r_vel + r_force) / 4.0


def ball_velocity(env: ManagerBasedRlEnv, std: float = 1.0) -> torch.Tensor:
  """Ball speed after the swinging foot has made contact."""
  state = kick_shot(env)
  speed = _ball(env).data.root_link_lin_vel_w.norm(dim=-1).clamp(0.0, 10.0)
  reward = 1.0 - 1.0 / (1.0 + speed / std)
  return torch.where(state.contacted, reward, torch.zeros_like(reward))


def ball_contact_orientation(env: ManagerBasedRlEnv) -> torch.Tensor:
  """Ball velocity toward the target, in a window after contact."""
  state = kick_shot(env)
  if not bool(state.contacted.any()):
    return torch.zeros(env.num_envs, device=env.device)
  target_xy = _target_xy(env)
  delta_xy = target_xy - state.contact_ball_xy
  direction_xy = delta_xy / (torch.linalg.norm(delta_xy, dim=-1, keepdim=True) + 1.0e-6)
  vel = _ball(env).data.root_link_lin_vel_w
  along_xy = (vel[:, :2] * direction_xy).sum(dim=-1).clamp(-10.0, 10.0) / 10.0
  delta_z = -_ball(env).data.root_link_pos_w[:, 2]
  delta = torch.cat([delta_xy, delta_z.unsqueeze(-1)], dim=-1)
  direction = delta / (torch.linalg.norm(delta, dim=-1, keepdim=True) + 1.0e-6)
  along = (vel * direction).sum(dim=-1).clamp(-15.0, 15.0) / 15.0
  reward = 0.5 * along_xy + 0.5 * along
  reward = torch.where(state.contacted, reward, torch.zeros_like(reward))
  return torch.where(reward < 0.0, 0.1 * reward, reward)


def _approach(reward: torch.Tensor, env: ManagerBasedRlEnv) -> torch.Tensor:
  done = kick_shot(env).approach_done(env)
  return torch.where(done, torch.zeros_like(reward), reward)


def robot_feet_ball_distance(env: ManagerBasedRlEnv, std: float = 0.5) -> torch.Tensor:
  """Swinging foot closing on the ball."""
  dist = torch.linalg.norm(
    _swing_foot_pos(env) - _ball(env).data.root_link_pos_w, dim=-1
  )
  state = kick_shot(env)
  dist = torch.where(state.contacted, torch.full_like(dist, _BALL_RADIUS), dist)
  gap = dist.clamp(min=_BALL_RADIUS) - _BALL_RADIUS
  reward = 1.0 / (1.0 + torch.square(gap / std))
  return _approach(reward, env)


def robot_com_ball_distance(env: ManagerBasedRlEnv, std: float = 0.5) -> torch.Tensor:
  """Root staying near the ball in the horizontal plane."""
  robot: Entity = env.scene["robot"]
  dist = torch.linalg.norm(
    robot.data.root_link_pos_w[:, :2] - _ball(env).data.root_link_pos_w[:, :2],
    dim=-1,
  )
  state = kick_shot(env)
  dist = torch.where(state.contacted, torch.full_like(dist, 0.25), dist)
  gap = dist.clamp(min=0.25) - 0.25
  reward = 1.0 / (1.0 + torch.square(gap / std))
  return _approach(reward, env)


def robot_torso_ball_distance(
  env: ManagerBasedRlEnv, std: float = 0.5, body_name: str = "Trunk"
) -> torch.Tensor:
  """Trunk staying near the ball in the horizontal plane."""
  robot: Entity = env.scene["robot"]
  dist = torch.linalg.norm(
    _body_pos(robot, body_name)[:, :2] - _ball(env).data.root_link_pos_w[:, :2],
    dim=-1,
  )
  state = kick_shot(env)
  dist = torch.where(state.contacted, torch.full_like(dist, 0.3), dist)
  gap = dist.clamp(min=0.3) - 0.3
  reward = 1.0 / (1.0 + torch.square(gap / std))
  return _approach(reward, env)


def penalize_weak_foot_contact(
  env: ManagerBasedRlEnv, threshold: float = 0.12, std: float = 0.1
) -> torch.Tensor:
  """Penalty that peaks when the plant foot is within reach of the ball."""
  dist = torch.linalg.norm(
    _plant_foot_pos(env) - _ball(env).data.root_link_pos_w, dim=-1
  )
  return torch.exp(-torch.square(dist - threshold) / std**2)


def penalize_self_contact_feet(
  env: ManagerBasedRlEnv, threshold: float = 0.2, std: float = 0.05
) -> torch.Tensor:
  """Penalty when the feet come closer than ``threshold``."""
  robot: Entity = env.scene["robot"]
  gap = torch.linalg.norm(
    _body_pos(robot, _LEFT_FOOT) - _body_pos(robot, _RIGHT_FOOT), dim=-1
  )
  close = gap < threshold
  penalty = 10.0 * (1.0 - torch.exp(-torch.square(gap - threshold) / std**2))
  return torch.where(close, penalty, torch.zeros_like(penalty))

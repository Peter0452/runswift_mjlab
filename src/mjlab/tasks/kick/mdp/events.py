"""Kick-task event (reset) functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from mjlab.entity import Entity
from mjlab.envs.mdp.events import resolve_env_ids
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.utils.lab_api.math import quat_apply, sample_uniform

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_DEFAULT_BALL_CFG = SceneEntityCfg("ball")
_DEFAULT_ROBOT_CFG = SceneEntityCfg("robot")


def reset_ball_uniform(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  pose_range: dict[str, tuple[float, float]],
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> None:
  """Reset the ball to a uniform random position in world (env-local) space.

  Args:
    env: The environment.
    env_ids: Environments to reset; ``None`` means all.
    pose_range: Dict with optional keys ``"x"``, ``"y"``, ``"z"`` giving
      ``(min, max)`` offsets relative to the env origin.
    ball_cfg: Scene entity config for the ball.
  """
  env_ids = resolve_env_ids(env, env_ids)
  ball: Entity = env.scene[ball_cfg.name]

  default_state = ball.data.default_root_state[env_ids].clone()

  _SE3_KEYS = ("x", "y", "z")
  ranges = torch.tensor(
    [pose_range.get(k, (0.0, 0.0)) for k in _SE3_KEYS],
    device=env.device,
  )
  offsets = sample_uniform(ranges[:, 0], ranges[:, 1], (len(env_ids), 3), env.device)

  default_state[:, 0:3] += offsets + env.scene.env_origins[env_ids]
  # Zero out velocity.
  default_state[:, 7:] = 0.0
  ball.write_root_state_to_sim(default_state, env_ids=env_ids)


def reset_ball_relative_to_robot(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
  forward_range: tuple[float, float] = (0.3, 0.8),
  lateral_range: tuple[float, float] = (-0.1, 0.1),
  height: float = 0.11,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> None:
  """Reset the ball to a random position in front of the robot.

  Useful for the kick task: the episode always starts with the ball already
  in the robot's kick zone so no approach phase is needed.

  Args:
    env: The environment.
    env_ids: Environments to reset; ``None`` means all.
    forward_range: Offset range (min, max) in robot-forward direction (metres).
    lateral_range: Offset range (min, max) in robot-lateral direction (metres).
    height: Fixed ball height above terrain (metres).
    ball_cfg: Ball entity config.
    robot_cfg: Robot entity config (used to get current root pose).
  """
  env_ids = resolve_env_ids(env, env_ids)
  ball: Entity = env.scene[ball_cfg.name]
  robot: Entity = env.scene[robot_cfg.name]

  n = len(env_ids)
  robot_pos_w = robot.data.root_link_pos_w[env_ids]  # [N, 3]
  robot_quat_w = robot.data.root_link_quat_w[env_ids]  # [N, 4]

  # Sample offsets in robot body frame.
  fwd = sample_uniform(
    torch.full((n,), forward_range[0], device=env.device),
    torch.full((n,), forward_range[1], device=env.device),
    (n,),
    env.device,
  )
  lat = sample_uniform(
    torch.full((n,), lateral_range[0], device=env.device),
    torch.full((n,), lateral_range[1], device=env.device),
    (n,),
    env.device,
  )
  offset_b = torch.stack([fwd, lat, torch.zeros(n, device=env.device)], dim=-1)

  # Rotate to world frame and translate.
  offset_w = quat_apply(robot_quat_w, offset_b)
  ball_pos_w = robot_pos_w + offset_w
  ball_pos_w[:, 2] = robot_pos_w[:, 2] + height  # fixed height above robot origin

  # Build full 13-D root state: [pos(3), quat(4), lin_vel(3), ang_vel(3)].
  ball_state = ball.data.default_root_state[env_ids].clone()
  ball_state[:, 0:3] = ball_pos_w
  ball_state[:, 3:7] = torch.tensor([1.0, 0.0, 0.0, 0.0], device=env.device)
  ball_state[:, 7:] = 0.0
  ball.write_root_state_to_sim(ball_state, env_ids=env_ids)

"""Kick-task termination terms (ported from HTWK T1 kicking).

Episode end conditions used by the unified Arc→Setup→Strike task:

* Time out — episode length ``t > T_max`` (BaseWalk ``time_out``).
* Fell over — orientation ``θ_t > θ_limit`` (BaseWalk ``fell_over``).
* Fell down — trunk height ``z_trunk < z_falldown`` (BaseWalk ``root_height``).
* Target hit — ball stopped inside target radius.
* Target missed — ball stopped outside target after the post-kick window.
* Double touch — illegal agent–ball contact after the post-kick window.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.tasks.kick.mdp.ball_phase import ensure_ball_phase_updated

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_DEFAULT_BALL_CFG = SceneEntityCfg("ball")
_DEFAULT_ROBOT_CFG = SceneEntityCfg("robot")


def _goal_ball_distance_xy(
  env: ManagerBasedRlEnv,
  command_name: str,
  ball_cfg: SceneEntityCfg,
) -> torch.Tensor:
  """Planar distance from ball to kick target (world frame)."""
  from mjlab.entity import Entity

  ball: Entity = env.scene[ball_cfg.name]
  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  goal_xy = command[:, :2] + env.scene.env_origins[:, :2]
  ball_xy = ball.data.root_link_pos_w[:, :2]
  return torch.linalg.norm(goal_xy - ball_xy, dim=-1)


def ball_still_timeout(
  env: ManagerBasedRlEnv,
  max_still_time_s: float = 2.0,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  kick_phase_robot_ball_distance: float | None = None,
  target_distance: float = 0.35,
  kick_ready_threshold: float = 0.45,
  command_name: str = "goal",
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> torch.Tensor:
  """Terminate when the ball stays still too long without a kick while ready."""
  from mjlab.tasks.kick.mdp.kick_ready_pose import kick_ready_activation_mask

  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
    robot_cfg_name=robot_cfg.name,
    kick_phase_robot_ball_distance=kick_phase_robot_ball_distance,
  )
  ready = (
    kick_ready_activation_mask(
      env,
      robot_cfg,
      ball_cfg,
      command_name,
      target_distance,
      kick_ready_threshold,
    )
    > 0.0
  )
  return (~state.kick_detected) & ready & (state.time_since_still_s > max_still_time_s)


def ball_moving_timeout(
  env: ManagerBasedRlEnv,
  max_moving_time_s: float = 5.0,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  command_name: str = "goal",
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Terminate after the ball has been rolling for too long post-kick."""
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
  )
  return state.kick_detected & (state.time_since_moving_s > max_moving_time_s)


def kick_success(
  env: ManagerBasedRlEnv,
  min_kick_speed: float = 2.0,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  command_name: str = "goal",
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """End the episode once the ball reaches the minimum kick speed toward goal."""
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    min_kick_speed=min_kick_speed,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
  )

  from mjlab.entity import Entity

  ball: Entity = env.scene[ball_cfg.name]
  command = env.command_manager.get_command(command_name)
  assert command is not None, f"Command '{command_name}' not found."
  ball_pos = ball.data.root_link_pos_w[:, :2]
  goal_pos = command[:, :2] + env.scene.env_origins[:, :2]
  goal_dir = (goal_pos - ball_pos) / torch.linalg.norm(
    goal_pos - ball_pos, dim=-1, keepdim=True
  ).clamp(min=1.0e-6)
  vel_toward_goal = torch.sum(ball.data.root_link_lin_vel_w[:, :2] * goal_dir, dim=-1)
  success = vel_toward_goal >= min_kick_speed
  env.extras["log"]["Metrics/kick_success_speed"] = vel_toward_goal.mean()
  env.extras["log"]["Metrics/kick_success_max_vel"] = state.max_vel_toward_goal.mean()
  return success


def target_hit(
  env: ManagerBasedRlEnv,
  target_radius: float = 1.0,
  ball_stationary_speed_threshold: float = 0.1,
  min_stopped_time_s: float = 0.1,
  require_kick: bool = True,
  kick_detection_speed_increase_threshold: float = 0.5,
  command_name: str = "goal",
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> torch.Tensor:
  """Success: ball stopped inside the target radius.

  ``(‖d_target,ball‖ < r) ∧ (‖v_ball‖ < ε)`` (and optional prior kick).
  """
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
    robot_cfg_name=robot_cfg.name,
  )
  dist = _goal_ball_distance_xy(env, command_name, ball_cfg)
  stopped = state.time_since_ball_stopped_s >= min_stopped_time_s
  inside = dist < target_radius
  kicked = state.kick_detected if require_kick else torch.ones_like(stopped)
  hit = kicked & stopped & inside
  env.extras["log"]["Metrics/target_ball_distance"] = dist.mean()
  env.extras["log"]["Metrics/target_hit"] = hit.float().mean()
  return hit


def target_missed(
  env: ManagerBasedRlEnv,
  target_radius: float = 1.0,
  post_kick_window_s: float = 2.0,
  ball_stationary_speed_threshold: float = 0.1,
  min_stopped_time_s: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  command_name: str = "goal",
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> torch.Tensor:
  """Failure: ball stopped outside the target after the post-kick window.

  ``(‖d_target,ball‖ > r) ∧ (‖v_ball‖ < ε) ∧ (c_t > T_window)``.
  """
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
    robot_cfg_name=robot_cfg.name,
  )
  dist = _goal_ball_distance_xy(env, command_name, ball_cfg)
  stopped = state.time_since_ball_stopped_s >= min_stopped_time_s
  outside = dist > target_radius
  past_window = state.time_since_kick_s > post_kick_window_s
  missed = state.kick_detected & past_window & stopped & outside
  env.extras["log"]["Metrics/target_missed"] = missed.float().mean()
  return missed


def double_touch(
  env: ManagerBasedRlEnv,
  post_kick_window_s: float = 1.0,
  contact_distance: float = 0.22,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  command_name: str = "goal",
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> torch.Tensor:
  """Failure: a second contact edge after the kick-contact debounce.

  Sustained first contact is allowed; leaving and touching the ball again is
  terminated.
  """
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
    robot_cfg_name=robot_cfg.name,
    contact_distance=contact_distance,
  )
  assert state.time_since_kick_s is not None
  assert state.kick_detected is not None
  assert state.post_kick_contact_count is not None
  past_window = state.time_since_kick_s > post_kick_window_s
  illegal = state.kick_detected & past_window & (state.post_kick_contact_count >= 2)
  env.extras["log"]["Metrics/double_touch"] = illegal.float().mean()
  return illegal


def ball_dribble_timeout(
  env: ManagerBasedRlEnv,
  max_dribble_time_s: float = 0.8,
  min_kick_speed: float = 2.0,
  dribble_speed: float = 0.15,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  kick_phase_robot_ball_distance: float = 0.55,
  command_name: str = "goal",
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> torch.Tensor:
  """Terminate when the ball dribbles slowly in the kick zone without a real kick."""
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    min_kick_speed=min_kick_speed,
    dribble_speed=dribble_speed,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
    robot_cfg_name=robot_cfg.name,
    kick_phase_robot_ball_distance=kick_phase_robot_ball_distance,
  )
  env.extras["log"]["Metrics/ball_dribble_time"] = state.time_since_slow_ball_s.mean()
  return state.time_since_slow_ball_s > max_dribble_time_s


def near_ball_no_kick_timeout(
  env: ManagerBasedRlEnv,
  max_near_time_s: float = 2.5,
  near_ball_distance: float = 1.0,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  command_name: str = "goal",
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> torch.Tensor:
  """Terminate if the robot loiters near the ball without kicking.

  Counts time while ``‖robot−ball‖ < near_ball_distance`` and
  ``kick_detected`` is false. Clears when the robot leaves the band or kicks.
  Stops dense per-step rewards from scaling with endless near-ball episodes.
  """
  from mjlab.entity import Entity

  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
    robot_cfg_name=robot_cfg.name,
    kick_phase_robot_ball_distance=near_ball_distance,
  )
  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  dist = torch.linalg.norm(
    robot.data.root_link_pos_w[:, :2] - ball.data.root_link_pos_w[:, :2],
    dim=-1,
  )
  near = (dist < float(near_ball_distance)) & (~state.kick_detected)
  timer = getattr(env, "_near_ball_no_kick_timer", None)
  if timer is None or timer.shape[0] != env.num_envs:
    timer = torch.zeros(env.num_envs, device=env.device)
  # Spawn is often still inside the near band; clear the timer on the first
  # step after reset or the previous episode's timeout instantly re-fires.
  fresh = env.episode_length_buf <= 1
  timer = torch.where(
    near & (~fresh),
    timer + env.step_dt,
    torch.zeros_like(timer),
  )
  env._near_ball_no_kick_timer = timer
  env.extras["log"]["Metrics/near_ball_no_kick_s"] = timer.mean()
  return near & (timer > float(max_near_time_s))


def near_ball_reached(
  env: ManagerBasedRlEnv,
  near_ball_distance: float = 0.50,
  min_keepout_distance: float = 0.0,
  min_time_s: float = 0.5,
  max_waypoint_distance: float | None = None,
  approach_standoff: float = 0.40,
  command_name: str = "goal",
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> torch.Tensor:
  """Success for approach-only: hold near ball and/or approach waypoint.

  Ball band: ``min_keepout_distance ≤ ‖robot−ball‖ < near_ball_distance``.
  Optional waypoint success: ``‖robot−waypoint‖ < max_waypoint_distance``
  (soft curriculum when finishing the last meter is hard).
  """
  from mjlab.entity import Entity
  from mjlab.tasks.kick.mdp.geometry import behind_ball_waypoint_xy

  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  robot_xy = robot.data.root_link_pos_w[:, :2]
  ball_xy = ball.data.root_link_pos_w[:, :2]
  dist = torch.linalg.norm(robot_xy - ball_xy, dim=-1)
  near = (dist < float(near_ball_distance)) & (dist >= float(min_keepout_distance))
  if max_waypoint_distance is not None:
    waypoint = behind_ball_waypoint_xy(
      env, ball_xy, float(approach_standoff), command_name
    )
    wp_dist = torch.linalg.norm(robot_xy - waypoint, dim=-1)
    near = near | (wp_dist < float(max_waypoint_distance))
    env.extras["log"]["Metrics/near_waypoint_dist"] = wp_dist.mean()

  timer = getattr(env, "_near_ball_reached_timer", None)
  if timer is None or timer.shape[0] != env.num_envs:
    timer = torch.zeros(env.num_envs, device=env.device)
  timer = torch.where(near, timer + env.step_dt, torch.zeros_like(timer))
  env._near_ball_reached_timer = timer
  env.extras["log"]["Metrics/near_ball_reached_s"] = timer.mean()
  env.extras["log"]["Metrics/near_ball_reached"] = (
    (near & (timer >= float(min_time_s))).float().mean()
  )
  return near & (timer >= float(min_time_s))


def robot_chase_ball_timeout(
  env: ManagerBasedRlEnv,
  max_chase_time_s: float = 0.6,
  chase_speed_threshold: float = 0.12,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  command_name: str = "goal",
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
) -> torch.Tensor:
  """Terminate when the robot keeps chasing the ball after contact."""
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    chase_speed_threshold=chase_speed_threshold,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
    robot_cfg_name=robot_cfg.name,
  )
  env.extras["log"]["Metrics/robot_chase_time"] = state.time_since_chase_s.mean()
  return state.time_since_chase_s > max_chase_time_s


def kick_window_timeout(
  env: ManagerBasedRlEnv,
  max_kick_window_time_s: float = 1.0,
  kick_window_speed_threshold: float = 0.5,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  command_name: str = "goal",
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Terminate shortly after the ball starts moving (post-kick reward window)."""
  state = ensure_ball_phase_updated(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    kick_detection_speed_increase_threshold=kick_detection_speed_increase_threshold,
    kick_window_speed_threshold=kick_window_speed_threshold,
    ball_cfg_name=ball_cfg.name,
    goal_command_name=command_name,
  )
  env.extras["log"]["Metrics/kick_window_time"] = state.time_since_kick_window_s.mean()
  return state.kick_window_active & (
    state.time_since_kick_window_s > max_kick_window_time_s
  )


def ball_too_far_strike(
  env: ManagerBasedRlEnv,
  max_ball_distance: float = 0.5,
  robot_cfg: SceneEntityCfg = _DEFAULT_ROBOT_CFG,
  ball_cfg: SceneEntityCfg = _DEFAULT_BALL_CFG,
) -> torch.Tensor:
  """Terminate when the robot drifts too far from the ball during strike training."""
  from mjlab.entity import Entity

  robot: Entity = env.scene[robot_cfg.name]
  ball: Entity = env.scene[ball_cfg.name]
  dist = torch.linalg.norm(
    ball.data.root_link_pos_w[:, :2] - robot.data.root_link_pos_w[:, :2],
    dim=-1,
  )
  env.extras["log"]["Metrics/strike_ball_distance"] = dist.mean()
  return dist > max_ball_distance

"""Per-env ball phase tracking for kick tasks (HTWK-style episode logic)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv


@dataclass
class BallPhaseState:
  """Buffers updated once per env step for kick rewards and terminations."""

  last_update_step: int = -1
  last_ball_vel_w: torch.Tensor | None = None
  time_since_still_s: torch.Tensor | None = None
  time_since_moving_s: torch.Tensor | None = None
  time_since_slow_ball_s: torch.Tensor | None = None
  time_since_chase_s: torch.Tensor | None = None
  kick_window_active: torch.Tensor | None = None
  time_since_kick_window_s: torch.Tensor | None = None
  time_since_kick_s: torch.Tensor | None = None
  kick_detected: torch.Tensor | None = None
  max_vel_toward_goal: torch.Tensor | None = None
  prev_ball_speed: torch.Tensor | None = None
  prev_vel_toward_goal: torch.Tensor | None = None
  delta_vel_toward_goal: torch.Tensor | None = None
  agent_ball_contact: torch.Tensor | None = None
  time_since_ball_stopped_s: torch.Tensor | None = None
  strong_kick_detected: torch.Tensor | None = None
  time_since_strong_kick_s: torch.Tensor | None = None


def _get_state(env: ManagerBasedRlEnv) -> BallPhaseState:
  state = getattr(env, "_kick_ball_phase", None)
  if state is None:
    state = BallPhaseState()
    env._kick_ball_phase = state
  return state


def init_ball_phase_state(env: ManagerBasedRlEnv) -> BallPhaseState:
  """Allocate ball-phase buffers once (resize if ``num_envs`` changes)."""
  state = _get_state(env)
  device = env.device
  n = env.num_envs
  needs_alloc = (
    state.kick_detected is None
    or state.kick_detected.shape[0] != n
    or state.agent_ball_contact is None
    or state.time_since_ball_stopped_s is None
    or state.strong_kick_detected is None
    or state.time_since_strong_kick_s is None
    or state.prev_vel_toward_goal is None
    or state.delta_vel_toward_goal is None
  )
  if not needs_alloc:
    return state
  state.last_update_step = -1
  state.last_ball_vel_w = torch.zeros(n, 3, device=device)
  state.time_since_still_s = torch.zeros(n, device=device)
  state.time_since_moving_s = torch.zeros(n, device=device)
  state.time_since_slow_ball_s = torch.zeros(n, device=device)
  state.time_since_chase_s = torch.zeros(n, device=device)
  state.kick_window_active = torch.zeros(n, dtype=torch.bool, device=device)
  state.time_since_kick_window_s = torch.zeros(n, device=device)
  state.time_since_kick_s = torch.zeros(n, device=device)
  state.kick_detected = torch.zeros(n, dtype=torch.bool, device=device)
  state.max_vel_toward_goal = torch.zeros(n, device=device)
  state.prev_ball_speed = torch.zeros(n, device=device)
  state.prev_vel_toward_goal = torch.zeros(n, device=device)
  state.delta_vel_toward_goal = torch.zeros(n, device=device)
  state.agent_ball_contact = torch.zeros(n, dtype=torch.bool, device=device)
  state.time_since_ball_stopped_s = torch.zeros(n, device=device)
  state.strong_kick_detected = torch.zeros(n, dtype=torch.bool, device=device)
  state.time_since_strong_kick_s = torch.zeros(n, device=device)
  return state


def reset_ball_phase_state(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | None,
) -> None:
  """Clear ball-phase buffers on episode reset."""
  from mjlab.envs.mdp.events import resolve_env_ids

  state = init_ball_phase_state(env)
  env_ids = resolve_env_ids(env, env_ids)
  state.last_ball_vel_w[env_ids] = 0.0
  state.time_since_still_s[env_ids] = 0.0
  state.time_since_moving_s[env_ids] = 0.0
  state.time_since_slow_ball_s[env_ids] = 0.0
  state.time_since_chase_s[env_ids] = 0.0
  state.kick_window_active[env_ids] = False
  state.time_since_kick_window_s[env_ids] = 0.0
  state.time_since_kick_s[env_ids] = 0.0
  state.kick_detected[env_ids] = False
  state.max_vel_toward_goal[env_ids] = 0.0
  state.prev_ball_speed[env_ids] = 0.0
  state.prev_vel_toward_goal[env_ids] = 0.0
  state.delta_vel_toward_goal[env_ids] = 0.0
  state.agent_ball_contact[env_ids] = False
  state.time_since_ball_stopped_s[env_ids] = 0.0
  state.strong_kick_detected[env_ids] = False
  state.time_since_strong_kick_s[env_ids] = 0.0


def ensure_ball_phase_updated(
  env: ManagerBasedRlEnv,
  *,
  ball_stationary_speed_threshold: float = 0.1,
  kick_detection_speed_increase_threshold: float = 0.5,
  kick_window_speed_threshold: float = 0.5,
  min_kick_speed: float = 1.2,
  strong_kick_speed: float = 5.0,
  dribble_speed: float = 0.15,
  chase_speed_threshold: float = 0.12,
  ball_cfg_name: str = "ball",
  goal_command_name: str = "goal",
  robot_cfg_name: str = "robot",
  # Default matches ``arc_kick_env_cfg`` setup_exit / near-ball (0.5 m).
  # Must stay gated: the first caller each step is a termination (``target_hit``),
  # and step events run *after* rewards — so None would let still-time count from
  # episode start and zero out Setup foot shaping before the robot arrives.
  kick_phase_robot_ball_distance: float | None = 0.5,
  contact_distance: float = 0.22,
  feet_ball_sensor_name: str = "feet_ball_contact",
  body_ball_sensor_name: str = "body_ball_contact",
  require_foot_contact_for_kick: bool = True,
) -> BallPhaseState:
  """Update ball-phase buffers at most once per environment step.

  CAUTION: this state is a per-env-step cache — only the *first* caller each
  step actually applies its kwargs (``last_update_step`` guard below); every
  later caller in the same step silently gets that first caller's values back,
  regardless of what it passed itself. Terminations run before rewards each
  env step (see ``ManagerBasedRlEnv.step``); step events run *after* both, so
  ``update_ball_phase_buffers`` never wins the race for the current step.
  In practice *these defaults* decide still-timer / dribble / strong-kick
  gating. Keep them in sync with ``arc_kick_env_cfg``
  (``_NEAR_BALL`` / ``_KICK_REWARD_GATE_SPEED`` / ``_MIN_KICK_SPEED``).

  Kick latch: speed jump **and** (by default) feet↔ball contact sensor, so a
  roll without a touch does not count. ``agent_ball_contact`` prefers the
  feet/body↔ball contact sensors; falls back to foot-distance only if sensors
  are missing.

  Strong-kick re-arm: when projected ball speed toward goal crosses
  ``strong_kick_speed``, ``time_since_strong_kick_s`` resets so
  ``post_kick_upright`` can pay on a real strike even after an earlier dribble
  latch of ``kick_detected``.
  """
  state = init_ball_phase_state(env)
  step = int(env.common_step_counter)
  if state.last_update_step == step:
    return state

  from mjlab.entity import Entity

  ball: Entity = env.scene[ball_cfg_name]
  ball_vel_w = ball.data.root_link_lin_vel_w
  ball_speed = torch.linalg.norm(ball_vel_w[:, :2], dim=-1)

  command = env.command_manager.get_command(goal_command_name)
  assert command is not None, f"Command '{goal_command_name}' not found."
  ball_pos = ball.data.root_link_pos_w[:, :2]
  # Goal command is env-local XY; convert to world.
  goal_pos = command[:, :2] + env.scene.env_origins[:, :2]
  to_goal = goal_pos - ball_pos
  goal_dir = to_goal / torch.linalg.norm(to_goal, dim=-1, keepdim=True).clamp(
    min=1.0e-6
  )
  vel_toward_goal = torch.sum(ball_vel_w[:, :2] * goal_dir, dim=-1)

  feet_contact = _contact_sensor_any(env, feet_ball_sensor_name)
  body_contact = _contact_sensor_any(env, body_ball_sensor_name)

  ball_moving = ball_speed > ball_stationary_speed_threshold
  speed_increase = ball_speed - state.prev_ball_speed
  new_kick = (~state.kick_detected) & (
    speed_increase > kick_detection_speed_increase_threshold
  )
  if require_foot_contact_for_kick and feet_contact is not None:
    new_kick = new_kick & feet_contact
  state.kick_detected = state.kick_detected | new_kick

  kick_window_open = ball_speed > kick_window_speed_threshold
  state.kick_window_active = state.kick_window_active | kick_window_open

  dt = env.step_dt
  state.time_since_kick_window_s = torch.where(
    state.kick_window_active,
    state.time_since_kick_window_s + dt,
    torch.zeros_like(state.time_since_kick_window_s),
  )
  state.time_since_kick_s = torch.where(
    state.kick_detected,
    state.time_since_kick_s + dt,
    torch.zeros_like(state.time_since_kick_s),
  )

  # Rising-edge re-arm when ball velocity toward goal crosses strong threshold.
  strong_now = vel_toward_goal >= strong_kick_speed
  new_strong = strong_now & (state.prev_vel_toward_goal < strong_kick_speed)
  state.strong_kick_detected = state.strong_kick_detected | new_strong
  state.time_since_strong_kick_s = torch.where(
    new_strong,
    torch.zeros_like(state.time_since_strong_kick_s),
    torch.where(
      state.strong_kick_detected,
      state.time_since_strong_kick_s + dt,
      state.time_since_strong_kick_s,
    ),
  )

  robot: Entity = env.scene[robot_cfg_name]
  robot_ball_dist = torch.linalg.norm(
    ball_pos - robot.data.root_link_pos_w[:, :2], dim=-1
  )
  if kick_phase_robot_ball_distance is not None:
    in_kick_context = robot_ball_dist <= kick_phase_robot_ball_distance
  else:
    in_kick_context = torch.ones(env.num_envs, dtype=torch.bool, device=env.device)

  still_increment = in_kick_context & ~ball_moving
  state.time_since_still_s = torch.where(
    still_increment,
    state.time_since_still_s + dt,
    torch.zeros_like(state.time_since_still_s),
  )
  state.time_since_moving_s = torch.where(
    ball_moving,
    state.time_since_moving_s + dt,
    torch.zeros_like(state.time_since_moving_s),
  )

  slow_ball = (
    in_kick_context
    & ball_moving
    & (vel_toward_goal < min_kick_speed)
    & (ball_speed >= dribble_speed)
  )
  state.time_since_slow_ball_s = torch.where(
    slow_ball,
    state.time_since_slow_ball_s + dt,
    torch.zeros_like(state.time_since_slow_ball_s),
  )

  to_ball = ball_pos - robot.data.root_link_pos_w[:, :2]
  to_ball_dir = to_ball / torch.linalg.norm(to_ball, dim=-1, keepdim=True).clamp(
    min=1.0e-6
  )
  chase_speed = torch.sum(
    robot.data.root_link_lin_vel_w[:, :2] * to_ball_dir, dim=-1
  ).clamp(min=0.0)
  chasing = state.kick_detected & ball_moving & (chase_speed > chase_speed_threshold)
  state.time_since_chase_s = torch.where(
    chasing,
    state.time_since_chase_s + dt,
    torch.zeros_like(state.time_since_chase_s),
  )

  state.max_vel_toward_goal = torch.maximum(
    state.max_vel_toward_goal,
    vel_toward_goal.clamp(min=0.0),
  )

  # True contacts from sensors; distance proxy only if sensors absent.
  if feet_contact is not None or body_contact is not None:
    contact = torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
    if feet_contact is not None:
      contact = contact | feet_contact
    if body_contact is not None:
      contact = contact | body_contact
    state.agent_ball_contact = contact
  else:
    left_ids, _ = robot.find_bodies("left_foot_link")
    right_ids, _ = robot.find_bodies("right_foot_link")
    feet_xy = robot.data.body_link_pos_w[:, [left_ids[0], right_ids[0]], :2]
    foot_dist = torch.linalg.norm(feet_xy - ball_pos.unsqueeze(1), dim=-1).amin(dim=-1)
    state.agent_ball_contact = foot_dist < contact_distance

  env.extras["log"]["Metrics/feet_ball_contact"] = (
    feet_contact.float().mean()
    if feet_contact is not None
    else torch.tensor(0.0, device=env.device)
  )
  env.extras["log"]["Metrics/body_ball_contact"] = (
    body_contact.float().mean()
    if body_contact is not None
    else torch.tensor(0.0, device=env.device)
  )
  env.extras["log"]["Metrics/agent_ball_contact"] = state.agent_ball_contact.float().mean()
  env.extras["log"]["Metrics/strong_kick_detected"] = (
    state.strong_kick_detected.float().mean()
  )

  # Time the ball has been continuously stopped (for target hit/miss).
  state.time_since_ball_stopped_s = torch.where(
    ~ball_moving,
    state.time_since_ball_stopped_s + dt,
    torch.zeros_like(state.time_since_ball_stopped_s),
  )

  state.delta_vel_toward_goal = vel_toward_goal - state.prev_vel_toward_goal
  state.prev_ball_speed = ball_speed
  state.prev_vel_toward_goal = vel_toward_goal
  state.last_update_step = step
  return state


def _contact_sensor_any(
  env: ManagerBasedRlEnv,
  sensor_name: str,
) -> torch.Tensor | None:
  """Return ``[B]`` bool contact mask from a ContactSensor, or ``None`` if absent."""
  if sensor_name not in env.scene.sensors:
    return None
  sensor = env.scene.sensors[sensor_name]
  found = getattr(sensor.data, "found", None)
  if found is None:
    return torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
  return found.reshape(found.shape[0], -1).any(dim=-1) > 0


def ball_is_stationary(
  env: ManagerBasedRlEnv,
  *,
  ball_stationary_speed_threshold: float = 0.1,
  ball_cfg_name: str = "ball",
) -> torch.Tensor:
  """Return ``True`` where the ball speed is below the stationary threshold."""
  from mjlab.entity import Entity

  ball: Entity = env.scene[ball_cfg_name]
  speed = torch.linalg.norm(ball.data.root_link_lin_vel_w[:, :2], dim=-1)
  return speed <= ball_stationary_speed_threshold


def ball_is_moving(
  env: ManagerBasedRlEnv,
  *,
  ball_stationary_speed_threshold: float = 0.1,
  **kwargs,
) -> torch.Tensor:
  """Return ``True`` where the ball is moving faster than the threshold."""
  return ~ball_is_stationary(
    env,
    ball_stationary_speed_threshold=ball_stationary_speed_threshold,
    ball_cfg_name=kwargs.get("ball_cfg_name", "ball"),
  )

"""Kick observation wiring: BaseWalk core (47-D) + kick slots (9-D) = 56-D."""

from __future__ import annotations

from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.managers.observation_manager import ObservationTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.tasks.kick import mdp as kick_mdp

KICK_BALL_OBS_DIM = 9
K1_BASE_WALK_CORE_DIM = 47
K1_BASE_WALK_ACTOR_DIM = K1_BASE_WALK_CORE_DIM + KICK_BALL_OBS_DIM
K1_BASE_WALK_KICK_ACTOR_DIM = K1_BASE_WALK_ACTOR_DIM

# Legacy HTWK / NuBots stack (66 walk + 9 kick).
HTWK_WALK_ACTOR_DIM = 66
HTWK_KICK_ACTOR_DIM = HTWK_WALK_ACTOR_DIM + KICK_BALL_OBS_DIM


def add_kick_slot_placeholders(cfg: ManagerBasedRlEnvCfg) -> None:
  """Append nine zero kick-slot inputs (walk training; same layout as kick tasks)."""
  ball_obs = ObservationTermCfg(func=kick_mdp.ball_rel_pos_placeholder)
  target_obs = ObservationTermCfg(func=kick_mdp.ball_goal_direction_placeholder)
  kick_range_obs = ObservationTermCfg(func=kick_mdp.kick_range_placeholder)
  ball_vel_obs = ObservationTermCfg(func=kick_mdp.ball_vel_placeholder)
  for group in ("actor", "critic"):
    terms = cfg.observations[group].terms
    terms["ball_rel_pos"] = ball_obs
    terms["ball_goal_direction"] = target_obs
    terms["kick_range"] = kick_range_obs
    terms["ball_vel_placeholder"] = ball_vel_obs


def add_unified_kick_observations(
  cfg: ManagerBasedRlEnvCfg,
  *,
  robot_cfg: SceneEntityCfg,
  ball_cfg: SceneEntityCfg,
  command_name: str = "goal",
  clip_distance: float = 6.0,
  ball_pos_noise: tuple[float, float] | None = (-0.05, 0.05),
) -> None:
  """Append ball and placeholder obs terms on top of the walk actor vector.

  ``ball_pos_noise`` is ``(n_min, n_max)`` uniform noise on actor ``ball_rel_pos``
  only (critic stays clean). Pass ``None`` to disable.
  """
  from mjlab.utils.noise import UniformNoiseCfg as Unoise

  actor_noise = (
    None
    if ball_pos_noise is None
    else Unoise(n_min=ball_pos_noise[0], n_max=ball_pos_noise[1])
  )
  ball_obs_actor = ObservationTermCfg(
    func=kick_mdp.ball_relative_position,
    params={
      "robot_cfg": robot_cfg,
      "ball_cfg": ball_cfg,
      "clip_distance": clip_distance,
    },
    noise=actor_noise,
  )
  ball_obs_critic = ObservationTermCfg(
    func=kick_mdp.ball_relative_position,
    params={
      "robot_cfg": robot_cfg,
      "ball_cfg": ball_cfg,
      "clip_distance": clip_distance,
    },
    noise=None,
  )
  target_obs = ObservationTermCfg(
    func=kick_mdp.ball_to_goal_direction,
    params={
      "command_name": command_name,
      "robot_cfg": robot_cfg,
      "ball_cfg": ball_cfg,
    },
  )
  kick_range_obs = ObservationTermCfg(
    func=kick_mdp.kick_range_expected_speed,
    params={
      "command_name": command_name,
      "ball_cfg": ball_cfg,
    },
  )
  ball_vel_obs = ObservationTermCfg(func=kick_mdp.ball_vel_placeholder)

  cfg.observations["actor"].terms["ball_rel_pos"] = ball_obs_actor
  cfg.observations["critic"].terms["ball_rel_pos"] = ball_obs_critic
  for group in ("actor", "critic"):
    terms = cfg.observations[group].terms
    terms["ball_goal_direction"] = target_obs
    terms["kick_range"] = kick_range_obs
    terms["ball_vel_placeholder"] = ball_vel_obs

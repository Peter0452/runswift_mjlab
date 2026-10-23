"""K1 unified Arc→Setup→Strike kick environment configuration."""

from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.tasks.kick.arc_kick_env_cfg import (
  make_approach_only_env_cfg,
  make_near_kick_env_cfg,
)
from mjlab.tasks.velocity.config.k1.env_cfgs import booster_k1_base_walk_env_cfg


def k1_kick_approach_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Stage-1: approach the ball only (no kick payday)."""
  base = booster_k1_base_walk_env_cfg(play=play)
  cfg = make_approach_only_env_cfg(base)
  if play:
    cfg.episode_length_s = int(1e9)
    cfg.observations["actor"].enable_corruption = False
    cfg.observations["actor"].terms["ball_rel_pos"].noise = None
    cfg.curriculum = {}
    cfg.events.pop("push_robot", None)
    cfg.terminations.pop("near_ball_reached", None)
    cfg.commands["twist"].debug_vis = False
    # Yellow approach waypoint + cyan FOV cone (goal debug vis).
    cfg.commands["goal"].debug_vis = True
    cfg.commands["goal"].approach_standoff = 0.15
    cfg.commands["goal"].fov_half_angle = 0.69
    cfg.commands["goal"].fov_vis_range = 2.5
    cfg.commands["goal"].resampling_time_range = (1e9, 1e9)
  return cfg


def k1_kick_near_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Stage-2: near-ball kick (strong kick payday, no dribble)."""
  base = booster_k1_base_walk_env_cfg(play=play)
  cfg = make_near_kick_env_cfg(base)
  if play:
    cfg.episode_length_s = int(1e9)
    cfg.observations["actor"].enable_corruption = False
    cfg.observations["actor"].terms["ball_rel_pos"].noise = None
    cfg.curriculum = {}
    cfg.events.pop("push_robot", None)
    cfg.terminations.pop("target_hit", None)
    cfg.terminations.pop("target_missed", None)
    cfg.terminations.pop("double_touch", None)
    cfg.terminations.pop("near_ball_no_kick", None)
    cfg.commands["twist"].debug_vis = False
    cfg.commands["goal"].debug_vis = True
    cfg.commands["goal"].approach_standoff = 0.0
    cfg.commands["goal"].fov_half_angle = 0.69
    cfg.commands["goal"].fov_vis_range = 2.5
    cfg.commands["goal"].resampling_time_range = (1e9, 1e9)
    # Play / Setup B FSM: always start from configured Near radius (no mix).
    cfg.events["reset_base"].params["handoff_fraction"] = 0.0
  return cfg


def k1_kick_walkamp_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Kick-on-Walk-AMP: Flat AMP Walk + thesis kick (78/95, no AMP style)."""
  from mjlab.tasks.kick.walkamp_kick_env_cfg import make_walkamp_kick_env_cfg

  return make_walkamp_kick_env_cfg(play=play)


def k1_kick_walkamp_amp_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Kick-on-Walk-AMP + kick AMP obs (style until ``kick_detected``)."""
  from mjlab.tasks.kick.walkamp_kick_env_cfg import make_walkamp_kick_amp_env_cfg

  return make_walkamp_kick_amp_env_cfg(play=play)

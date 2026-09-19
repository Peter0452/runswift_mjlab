"""K1 unified Arc→Setup→Strike kick environment configuration."""

from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.tasks.kick.arc_kick_env_cfg import (
  make_approach_only_env_cfg,
  make_arc_kick_env_cfg,
  make_near_kick_env_cfg,
)
from mjlab.tasks.velocity.config.k1.env_cfgs import booster_k1_base_walk_env_cfg


def k1_arc_kick_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """BaseWalk + 3-phase reference-pose kick (replaces chase/approach/strike/score)."""
  base = booster_k1_base_walk_env_cfg(play=play)
  cfg = make_arc_kick_env_cfg(base)
  if play:
    cfg.episode_length_s = int(1e9)
    cfg.observations["actor"].enable_corruption = False
    # Clean ball obs in play.
    cfg.observations["actor"].terms["ball_rel_pos"].noise = None
    cfg.curriculum = {}
    cfg.events.pop("push_robot", None)
    cfg.events["reset_base"].params["radius_range"] = (2.0, 3.0)
    cfg.terminations.pop("target_hit", None)
    cfg.terminations.pop("target_missed", None)
    cfg.terminations.pop("double_touch", None)
    cfg.terminations.pop("kick_success", None)
    cfg.terminations.pop("near_ball_no_kick", None)
    # Keep walking: zero twist collapses BaseWalk/kick policies (gait + tracking).
    # Only hide twist arrows so they are not confused with the green kick aim.
    cfg.commands["twist"].debug_vis = False
    # Pin kick goal — green sphere/aim should only move if the ball moves.
    cfg.commands["goal"].resampling_time_range = (1e9, 1e9)
  return cfg


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
  return cfg

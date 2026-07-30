"""K1 kick task environment configurations."""

from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.tasks.kick.approach_env_cfg import make_approach_env_cfg
from mjlab.tasks.kick.score_env_cfg import make_score_env_cfg
from mjlab.tasks.velocity.config.k1.env_cfgs import booster_k1_flat_env_cfg


def k1_approach_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """K1 ball-approach task: walk to the ball and reach the kick zone."""
  base = booster_k1_flat_env_cfg(play=play)
  cfg = make_approach_env_cfg(base)
  if play:
    cfg.episode_length_s = int(1e9)
    cfg.observations["actor"].enable_corruption = False
    cfg.curriculum = {}
  return cfg


def k1_score_env_cfg(
  kick_style: str = "snap",
  play: bool = False,
) -> ManagerBasedRlEnvCfg:
  """K1 kick-to-goal task: kick the ball toward a target position."""
  base = booster_k1_flat_env_cfg(play=play)
  cfg = make_score_env_cfg(base, kick_style=kick_style)
  if play:
    cfg.episode_length_s = int(1e9)
    cfg.observations["actor"].enable_corruption = False
    cfg.curriculum = {}
  return cfg

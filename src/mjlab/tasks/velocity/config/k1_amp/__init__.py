from mjlab.tasks.registry import register_mjlab_task
from mjlab.tasks.velocity.config.k1_amp.amp_wrapper import with_amp_obs_group
from mjlab.tasks.velocity.rl.amp_runner import VelocityAmpOnPolicyRunner

from .env_cfgs import (
  KICK_STYLE_WEIGHT,
  booster_k1_amp_flat_env_cfg,
  booster_k1_amp_kick_handoff_env_cfg,
  booster_k1_amp_rough_env_cfg,
  booster_k1_amp_rough_ft_env_cfg,
  booster_k1_kick_approach_env_cfg,
  booster_k1_kick_stage1_env_cfg,
  booster_k1_kick_stage3_env_cfg,
)
from .rl_cfg import (
  booster_k1_amp_kick_handoff_runner_cfg,
  booster_k1_amp_ppo_runner_cfg,
  booster_k1_amp_ppo_symmetric_runner_cfg,
  booster_k1_kick_approach_runner_cfg,
  booster_k1_kick_stage1_runner_cfg,
  booster_k1_kick_stage3_runner_cfg,
)


def _with_amp_reset_cfg(env_cfg, runner_cfg):
  return with_amp_obs_group(
    env_cfg,
    dataset_root=runner_cfg.dataset_root,
    speed_factor=runner_cfg.speed_factor,
    dataset_weights=runner_cfg.dataset_weights,
    augmentations=runner_cfg.dataset_augmentations,
    include_base_lin_vel=True,
  )


_AMP_TASKS = {
  "Rough-Amp": (booster_k1_amp_rough_env_cfg, booster_k1_amp_ppo_runner_cfg),
  "Rough-Amp-DA": (
    booster_k1_amp_rough_ft_env_cfg,
    booster_k1_amp_ppo_symmetric_runner_cfg,
  ),
  "Flat-Amp": (booster_k1_amp_flat_env_cfg, booster_k1_amp_ppo_runner_cfg),
  "Flat-Amp-DA": (
    booster_k1_amp_flat_env_cfg,
    booster_k1_amp_ppo_symmetric_runner_cfg,
  ),
}

for use_muon in (False, True):
  optimizer = "-Muon" if use_muon else ""
  for name, (env_cfg_fn, rl_cfg_fn) in _AMP_TASKS.items():
    rl_cfg = rl_cfg_fn(use_muon=use_muon)
    register_mjlab_task(
      task_id=f"Mjlab-Velocity-{name}{optimizer}-Booster-K1",
      env_cfg=_with_amp_reset_cfg(env_cfg_fn(), rl_cfg),
      play_env_cfg=_with_amp_reset_cfg(env_cfg_fn(play=True), rl_cfg),
      rl_cfg=rl_cfg,
      runner_cls=VelocityAmpOnPolicyRunner,
    )

_approach_rl = booster_k1_kick_approach_runner_cfg()
register_mjlab_task(
  task_id="Mjlab-Velocity-Kick-Approach-Amp-DA-Muon-Booster-K1",
  env_cfg=_with_amp_reset_cfg(booster_k1_kick_approach_env_cfg(), _approach_rl),
  play_env_cfg=_with_amp_reset_cfg(
    booster_k1_kick_approach_env_cfg(play=True), _approach_rl
  ),
  rl_cfg=_approach_rl,
  runner_cls=VelocityAmpOnPolicyRunner,
)


def _with_kick_style(env_cfg):
  """The AMP wrapper sets style weight 0.3; the kick stage sets its own."""
  style = env_cfg.curriculum["amp_style_weight"].params
  style["start_weight"] = style["end_weight"] = KICK_STYLE_WEIGHT
  return env_cfg


_stage3_rl = booster_k1_kick_stage3_runner_cfg()
register_mjlab_task(
  task_id="Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1",
  env_cfg=_with_kick_style(
    _with_amp_reset_cfg(booster_k1_kick_stage3_env_cfg(), _stage3_rl)
  ),
  play_env_cfg=_with_kick_style(
    _with_amp_reset_cfg(booster_k1_kick_stage3_env_cfg(play=True), _stage3_rl)
  ),
  rl_cfg=_stage3_rl,
  runner_cls=VelocityAmpOnPolicyRunner,
)

_stage1_rl = booster_k1_kick_stage1_runner_cfg()
register_mjlab_task(
  task_id="Mjlab-Velocity-Kick-Stage1-Amp-DA-Muon-Booster-K1",
  env_cfg=_with_amp_reset_cfg(booster_k1_kick_stage1_env_cfg(), _stage1_rl),
  play_env_cfg=_with_amp_reset_cfg(
    booster_k1_kick_stage1_env_cfg(play=True), _stage1_rl
  ),
  rl_cfg=_stage1_rl,
  runner_cls=VelocityAmpOnPolicyRunner,
)

_handoff_rl = booster_k1_amp_kick_handoff_runner_cfg()
register_mjlab_task(
  task_id="Mjlab-Velocity-Rough-Amp-DA-Muon-Booster-K1-KickHandoff",
  env_cfg=_with_amp_reset_cfg(booster_k1_amp_kick_handoff_env_cfg(), _handoff_rl),
  play_env_cfg=_with_amp_reset_cfg(
    booster_k1_amp_kick_handoff_env_cfg(play=True), _handoff_rl
  ),
  rl_cfg=_handoff_rl,
  runner_cls=VelocityAmpOnPolicyRunner,
)

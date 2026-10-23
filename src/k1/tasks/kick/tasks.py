"""Registers the kick pipeline: stage 1, approach, stage 3 (the deployed kick
loop) and the walk-to-kick handoff fine-tune."""

from k1.tasks.kick.env_cfg import (
  booster_k1_amp_kick_handoff_env_cfg,
  booster_k1_kick_approach_env_cfg,
  booster_k1_kick_stage1_env_cfg,
  booster_k1_kick_stage3_env_cfg,
  with_kick_prior_contact,
  with_kick_style,
  with_stand_start,
)
from k1.tasks.kick.rl_cfg import (
  booster_k1_amp_kick_handoff_runner_cfg,
  booster_k1_kick_approach_runner_cfg,
  booster_k1_kick_stage1_runner_cfg,
  booster_k1_kick_stage3_runner_cfg,
)
from k1.tasks.velocity.config.k1_amp.amp_wrapper import with_amp_reset_cfg
from k1.tasks.velocity.rl.amp_runner import VelocityAmpOnPolicyRunner
from mjlab.tasks.registry import register_mjlab_task

_approach_rl = booster_k1_kick_approach_runner_cfg()
register_mjlab_task(
  task_id="Mjlab-Velocity-Kick-Approach-Amp-DA-Muon-Booster-K1",
  env_cfg=with_amp_reset_cfg(booster_k1_kick_approach_env_cfg(), _approach_rl),
  play_env_cfg=with_amp_reset_cfg(
    booster_k1_kick_approach_env_cfg(play=True), _approach_rl
  ),
  rl_cfg=_approach_rl,
  runner_cls=VelocityAmpOnPolicyRunner,
)

_stage3_rl = booster_k1_kick_stage3_runner_cfg()
register_mjlab_task(
  task_id="Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1",
  env_cfg=with_stand_start(
    with_kick_prior_contact(
      with_kick_style(with_amp_reset_cfg(booster_k1_kick_stage3_env_cfg(), _stage3_rl)),
      _stage3_rl,
    )
  ),
  play_env_cfg=with_kick_prior_contact(
    with_kick_style(
      with_amp_reset_cfg(booster_k1_kick_stage3_env_cfg(play=True), _stage3_rl)
    ),
    _stage3_rl,
  ),
  rl_cfg=_stage3_rl,
  runner_cls=VelocityAmpOnPolicyRunner,
)

_stage1_rl = booster_k1_kick_stage1_runner_cfg()
_stage1_rl.decap = True
_stage1_rl.decap_source = "loader"
_stage1_rl.algorithm.multi_critic_alphas = (0.2, 0.8)
register_mjlab_task(
  task_id="Mjlab-Velocity-Kick-Stage1-Amp-DA-Muon-Booster-K1",
  env_cfg=with_amp_reset_cfg(booster_k1_kick_stage1_env_cfg(), _stage1_rl),
  play_env_cfg=with_amp_reset_cfg(
    booster_k1_kick_stage1_env_cfg(play=True), _stage1_rl
  ),
  rl_cfg=_stage1_rl,
  runner_cls=VelocityAmpOnPolicyRunner,
)

_handoff_rl = booster_k1_amp_kick_handoff_runner_cfg()
register_mjlab_task(
  task_id="Mjlab-Velocity-Rough-Amp-DA-Muon-Booster-K1-KickHandoff",
  env_cfg=with_amp_reset_cfg(booster_k1_amp_kick_handoff_env_cfg(), _handoff_rl),
  play_env_cfg=with_amp_reset_cfg(
    booster_k1_amp_kick_handoff_env_cfg(play=True), _handoff_rl
  ),
  rl_cfg=_handoff_rl,
  runner_cls=VelocityAmpOnPolicyRunner,
)

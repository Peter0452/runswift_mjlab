"""Registers the dribble task (dribble with kick mode)."""

from k1.tasks.dribble.env_cfg import booster_k1_dribble_env_cfg
from k1.tasks.dribble.rl_cfg import booster_k1_dribble_runner_cfg
from k1.tasks.velocity.config.k1_amp.amp_wrapper import with_amp_reset_cfg
from k1.tasks.velocity.rl.amp_runner import VelocityAmpOnPolicyRunner
from mjlab.tasks.registry import register_mjlab_task

_dribble_rl = booster_k1_dribble_runner_cfg()
register_mjlab_task(
  task_id="Mjlab-Velocity-Dribble-Amp-DA-Muon-Booster-K1",
  env_cfg=with_amp_reset_cfg(booster_k1_dribble_env_cfg(), _dribble_rl),
  play_env_cfg=with_amp_reset_cfg(booster_k1_dribble_env_cfg(play=True), _dribble_rl),
  rl_cfg=_dribble_rl,
  runner_cls=VelocityAmpOnPolicyRunner,
)

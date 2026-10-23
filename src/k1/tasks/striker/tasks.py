"""Registers the two-level striker: a controller over the frozen walk and kick
skills, also trained by self-play (phase 1; the flat self-play task is phase 2)."""

from k1.tasks.kick.rl_cfg import booster_k1_kick_stage3_runner_cfg
from k1.tasks.selfplay.config import (
  booster_k1_striker_controller_env_cfg,
  booster_k1_striker_controller_runner_cfg,
)
from k1.tasks.striker.runner import StrikerControllerRunner
from k1.tasks.velocity.config.k1_amp.amp_wrapper import with_amp_reset_cfg
from mjlab.tasks.registry import register_mjlab_task

# The AMP observation group follows the stage-3 kick's motion dataset.
_stage3_rl = booster_k1_kick_stage3_runner_cfg()
register_mjlab_task(
  task_id="Mjlab-Velocity-Striker-Controller-Booster-K1",
  env_cfg=with_amp_reset_cfg(booster_k1_striker_controller_env_cfg(), _stage3_rl),
  play_env_cfg=with_amp_reset_cfg(
    booster_k1_striker_controller_env_cfg(play=True), _stage3_rl
  ),
  rl_cfg=booster_k1_striker_controller_runner_cfg(),
  runner_cls=StrikerControllerRunner,
)

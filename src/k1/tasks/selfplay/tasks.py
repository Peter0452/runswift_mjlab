"""Registers 1v1 self-play: stage 3 against a frozen opponent (mirror +
snapshot pool)."""

from k1.tasks.kick.env_cfg import with_kick_style, with_stand_start
from k1.tasks.selfplay.config import (
  booster_k1_kick_selfplay_env_cfg,
  booster_k1_kick_selfplay_runner_cfg,
)
from k1.tasks.selfplay.runner import SelfPlayAmpOnPolicyRunner
from k1.tasks.velocity.config.k1_amp.amp_wrapper import with_amp_reset_cfg
from mjlab.tasks.registry import register_mjlab_task

_selfplay_rl = booster_k1_kick_selfplay_runner_cfg()
register_mjlab_task(
  task_id="Mjlab-Velocity-Kick-SelfPlay-Amp-DA-Muon-Booster-K1",
  env_cfg=with_stand_start(
    with_kick_style(
      with_amp_reset_cfg(booster_k1_kick_selfplay_env_cfg(), _selfplay_rl)
    )
  ),
  play_env_cfg=with_kick_style(
    with_amp_reset_cfg(booster_k1_kick_selfplay_env_cfg(play=True), _selfplay_rl)
  ),
  rl_cfg=_selfplay_rl,
  runner_cls=SelfPlayAmpOnPolicyRunner,
)

"""Registers the AMP walk tasks (the prior every K1 skill builds on)."""

from k1.tasks.velocity.config.k1_amp.amp_wrapper import with_amp_reset_cfg
from k1.tasks.velocity.rl.amp_runner import VelocityAmpOnPolicyRunner
from k1.tasks.walk.env_cfg import (
  booster_k1_amp_flat_env_cfg,
  booster_k1_amp_rough_ft_env_cfg,
)
from k1.tasks.walk.rl_cfg import booster_k1_amp_ppo_symmetric_runner_cfg
from mjlab.tasks.registry import register_mjlab_task

_AMP_TASKS = {
  "Rough-Amp-DA": (
    booster_k1_amp_rough_ft_env_cfg,
    booster_k1_amp_ppo_symmetric_runner_cfg,
  ),
  "Flat-Amp-DA": (
    booster_k1_amp_flat_env_cfg,
    booster_k1_amp_ppo_symmetric_runner_cfg,
  ),
}

for name, (env_cfg_fn, rl_cfg_fn) in _AMP_TASKS.items():
  rl_cfg = rl_cfg_fn(use_muon=True)
  # Walk spring and two critics. Style is 0.2: at a 98% discriminator
  # accuracy the style advantage is saturated noise, and 0.5 of it was
  # washing out the tracking gradient.
  rl_cfg.decap = True
  rl_cfg.decap_source = "loader"
  rl_cfg.algorithm.multi_critic_alphas = (0.2, 0.8)
  register_mjlab_task(
    task_id=f"Mjlab-Velocity-{name}-Muon-Booster-K1",
    env_cfg=with_amp_reset_cfg(env_cfg_fn(), rl_cfg),
    play_env_cfg=with_amp_reset_cfg(env_cfg_fn(play=True), rl_cfg),
    rl_cfg=rl_cfg,
    runner_cls=VelocityAmpOnPolicyRunner,
  )

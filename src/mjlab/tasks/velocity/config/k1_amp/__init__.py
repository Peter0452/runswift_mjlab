from mjlab.tasks.registry import register_mjlab_task
from mjlab.tasks.velocity.config.k1_amp.amp_wrapper import with_amp_obs_group
from mjlab.tasks.velocity.rl.amp_runner import VelocityAmpOnPolicyRunner

from .env_cfgs import (
  booster_k1_amp_flat_env_cfg,
  booster_k1_amp_rough_env_cfg,
  booster_k1_amp_rough_ft_env_cfg,
)
from .rl_cfg import (
  booster_k1_amp_ppo_runner_cfg,
  booster_k1_amp_ppo_symmetric_runner_cfg,
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

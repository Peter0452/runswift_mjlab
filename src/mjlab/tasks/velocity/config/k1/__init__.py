from mjlab.tasks.registry import register_mjlab_task
from mjlab.tasks.velocity.rl import VelocityOnPolicyRunner

from .env_cfgs import (
  booster_k1_flat_env_cfg,
  booster_k1_flat_fast_sac_env_cfg,
  booster_k1_flat_g1_env_cfg,
  booster_k1_rough_env_cfg,
  booster_k1_rough_fast_sac_env_cfg,
  booster_k1_rough_g1_env_cfg,
)
from .rl_cfg import booster_k1_ppo_runner_cfg

# ParameterWalk-style K1 rewards + PPO.
register_mjlab_task(
  task_id="Mjlab-Velocity-Rough-Booster-K1",
  env_cfg=booster_k1_rough_env_cfg(),
  play_env_cfg=booster_k1_rough_env_cfg(play=True),
  rl_cfg=booster_k1_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-Flat-Booster-K1",
  env_cfg=booster_k1_flat_env_cfg(),
  play_env_cfg=booster_k1_flat_env_cfg(play=True),
  rl_cfg=booster_k1_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

# G1-like mjlab velocity rewards + PPO (K1 robot / sensors / commands).
register_mjlab_task(
  task_id="Mjlab-Velocity-Rough-Booster-K1-G1",
  env_cfg=booster_k1_rough_g1_env_cfg(),
  play_env_cfg=booster_k1_rough_g1_env_cfg(play=True),
  rl_cfg=booster_k1_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-Flat-Booster-K1-G1",
  env_cfg=booster_k1_flat_g1_env_cfg(),
  play_env_cfg=booster_k1_flat_g1_env_cfg(play=True),
  rl_cfg=booster_k1_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

# Booster T1-aligned rewards / commands / DR + PPO (was FastSAC).
# Task IDs keep the FastSAC suffix so existing train/play commands still resolve.
register_mjlab_task(
  task_id="Mjlab-Velocity-Rough-Booster-K1-FastSAC",
  env_cfg=booster_k1_rough_fast_sac_env_cfg(),
  play_env_cfg=booster_k1_rough_fast_sac_env_cfg(play=True),
  rl_cfg=booster_k1_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-Flat-Booster-K1-FastSAC",
  env_cfg=booster_k1_flat_fast_sac_env_cfg(),
  play_env_cfg=booster_k1_flat_fast_sac_env_cfg(play=True),
  rl_cfg=booster_k1_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

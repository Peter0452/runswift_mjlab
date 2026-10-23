from k1.tasks.velocity.rl import VelocityOnPolicyRunner
from mjlab.tasks.registry import register_mjlab_task

from .env_cfgs import (
  booster_k1_base_walk_env_cfg,
  booster_k1_base_walk_rough_ft_env_cfg,
  booster_k1_flat_env_cfg,
  booster_k1_nubots_htwk_env_cfg,
  booster_k1_nubots_htwk_exact_env_cfg,
  booster_k1_nubots_htwk_robust_ft_env_cfg,
  booster_k1_nubots_htwk_unclipped_env_cfg,
  booster_k1_rough_env_cfg,
)
from .rl_cfg import (
  booster_k1_base_walk_ppo_runner_cfg,
  booster_k1_base_walk_rough_ft_ppo_runner_cfg,
  booster_k1_nubots_htwk_exact_ppo_runner_cfg,
  booster_k1_nubots_htwk_ppo_runner_cfg,
  booster_k1_nubots_htwk_robust_ft_ppo_runner_cfg,
  booster_k1_nubots_htwk_unclipped_ppo_runner_cfg,
  booster_k1_ppo_runner_cfg,
)

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

# HTWK-gym Base_Walk rewards on K1: 47-D obs, 12 leg actions, vx/vy/yaw + gait clock.
register_mjlab_task(
  task_id="Mjlab-Velocity-Flat-Booster-K1-BaseWalk",
  env_cfg=booster_k1_base_walk_env_cfg(),
  play_env_cfg=booster_k1_base_walk_env_cfg(play=True),
  rl_cfg=booster_k1_base_walk_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

# BaseWalk rough FT: 80/10/10 flat/rough/wave, terrain_scan height, fixed 5e-6 LR.
register_mjlab_task(
  task_id="Mjlab-Velocity-Rough-Booster-K1-BaseWalk",
  env_cfg=booster_k1_base_walk_rough_ft_env_cfg(),
  play_env_cfg=booster_k1_base_walk_rough_ft_env_cfg(play=True),
  rl_cfg=booster_k1_base_walk_rough_ft_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-HTWK-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_htwk_env_cfg(),
  play_env_cfg=booster_k1_nubots_htwk_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_htwk_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-HTWK-Unclipped-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_htwk_unclipped_env_cfg(),
  play_env_cfg=booster_k1_nubots_htwk_unclipped_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_htwk_unclipped_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-HTWK-Exact-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_htwk_exact_env_cfg(),
  play_env_cfg=booster_k1_nubots_htwk_exact_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_htwk_exact_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-HTWK-Robust-FT-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_htwk_robust_ft_env_cfg(),
  play_env_cfg=booster_k1_nubots_htwk_robust_ft_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_htwk_robust_ft_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

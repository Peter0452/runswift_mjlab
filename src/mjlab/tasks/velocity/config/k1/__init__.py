from mjlab.tasks.registry import register_mjlab_task
from mjlab.tasks.velocity.rl import VelocityOnPolicyRunner

from .env_cfgs import (
  booster_k1_flat_env_cfg,
  booster_k1_flat_fast_sac_env_cfg,
  booster_k1_flat_g1_env_cfg,
  booster_k1_nubots_flat_env_cfg,
  booster_k1_nubots_phase1_env_cfg,
  booster_k1_nubots_phase2_env_cfg,
  booster_k1_nubots_phase2_stabilize_env_cfg,
  booster_k1_nubots_phase3_env_cfg,
  booster_k1_nubots_htwk_env_cfg,
  booster_k1_nubots_htwk_exact_env_cfg,
  booster_k1_nubots_htwk_robust_ft_env_cfg,
  booster_k1_nubots_htwk_unclipped_env_cfg,
  booster_k1_nubots_quality_env_cfg,
  booster_k1_nubots_rough_env_cfg,
  booster_k1_nubots_speed_env_cfg,
  booster_k1_rough_env_cfg,
  booster_k1_rough_fast_sac_env_cfg,
  booster_k1_rough_g1_env_cfg,
)
from .rl_cfg import (
  booster_k1_nubots_phase1_ppo_runner_cfg,
  booster_k1_nubots_phase1_symmetry_ppo_runner_cfg,
  booster_k1_nubots_phase2_ppo_runner_cfg,
  booster_k1_nubots_phase2_stabilize_ppo_runner_cfg,
  booster_k1_nubots_phase2_stabilize_symmetry_ppo_runner_cfg,
  booster_k1_nubots_phase2_symmetry_ppo_runner_cfg,
  booster_k1_nubots_phase3_ppo_runner_cfg,
  booster_k1_nubots_phase3_symmetry_ppo_runner_cfg,
  booster_k1_nubots_ppo_runner_cfg,
  booster_k1_nubots_htwk_ppo_runner_cfg,
  booster_k1_nubots_htwk_exact_ppo_runner_cfg,
  booster_k1_nubots_htwk_robust_ft_ppo_runner_cfg,
  booster_k1_nubots_htwk_unclipped_ppo_runner_cfg,
  booster_k1_nubots_quality_ppo_runner_cfg,
  booster_k1_nubots_rough_ppo_runner_cfg,
  booster_k1_nubots_speed_ppo_runner_cfg,
  booster_k1_nubots_symmetry_ppo_runner_cfg,
  booster_k1_nubots_symmetry_v2_ppo_runner_cfg,
  booster_k1_ppo_runner_cfg,
)

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

# NuBots teacher→student (same 66→16 MLP). Import ONNX then PPO fine-tune.
register_mjlab_task(
  task_id="Mjlab-Velocity-Flat-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_flat_env_cfg(),
  play_env_cfg=booster_k1_nubots_flat_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-Rough-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_rough_env_cfg(),
  play_env_cfg=booster_k1_nubots_rough_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_rough_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-Phase1-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_phase1_env_cfg(),
  play_env_cfg=booster_k1_nubots_phase1_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_phase1_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-Phase1Sym-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_phase1_env_cfg(),
  play_env_cfg=booster_k1_nubots_phase1_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_phase1_symmetry_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-Phase2-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_phase2_env_cfg(),
  play_env_cfg=booster_k1_nubots_phase2_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_phase2_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-Phase2Sym-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_phase2_env_cfg(),
  play_env_cfg=booster_k1_nubots_phase2_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_phase2_symmetry_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-Phase2Stab-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_phase2_stabilize_env_cfg(),
  play_env_cfg=booster_k1_nubots_phase2_stabilize_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_phase2_stabilize_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-Phase2StabSym-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_phase2_stabilize_env_cfg(),
  play_env_cfg=booster_k1_nubots_phase2_stabilize_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_phase2_stabilize_symmetry_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-Phase3-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_phase3_env_cfg(),
  play_env_cfg=booster_k1_nubots_phase3_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_phase3_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-Phase3Sym-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_phase3_env_cfg(),
  play_env_cfg=booster_k1_nubots_phase3_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_phase3_symmetry_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-Quality-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_quality_env_cfg(),
  play_env_cfg=booster_k1_nubots_quality_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_quality_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-Speed-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_speed_env_cfg(),
  play_env_cfg=booster_k1_nubots_speed_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_speed_ppo_runner_cfg(),
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

register_mjlab_task(
  task_id="Mjlab-Velocity-Symmetry-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_quality_env_cfg(),
  play_env_cfg=booster_k1_nubots_quality_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_symmetry_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-SymmetryV2-Booster-K1-Nubots",
  env_cfg=booster_k1_nubots_quality_env_cfg(),
  play_env_cfg=booster_k1_nubots_quality_env_cfg(play=True),
  rl_cfg=booster_k1_nubots_symmetry_v2_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

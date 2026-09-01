"""RL configuration for Booster K1 velocity task."""

import math

from mjlab.rl import (
  FastSacAlgorithmCfg,
  FastSacRunnerCfg,
  RslRlModelCfg,
  RslRlOnPolicyRunnerCfg,
  RslRlPpoAlgorithmCfg,
)

_NUBOTS_SYMMETRY_CFG = {
  "use_data_augmentation": True,
  "use_mirror_loss": False,
  "mirror_loss_coeff": 0.05,
  "data_augmentation_func": "mjlab.tasks.velocity.mdp.symmetry:nubots_symmetry",
}


def _apply_nubots_symmetry(cfg: RslRlOnPolicyRunnerCfg) -> RslRlOnPolicyRunnerCfg:
  """Enable left-right leg symmetry data augmentation on a NuBots runner cfg."""
  cfg.algorithm.symmetry_cfg = dict(_NUBOTS_SYMMETRY_CFG)
  return cfg


def booster_k1_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """PPO runner aligned with booster_gym T1.yaml algorithm / action std.

  Booster stores ``logstd = -2`` (σ≈0.135) and clips actions to ±1. Its loss uses
  ``+ entropy_coef * H`` with ``entropy_coef=-0.01``; rsl_rl uses ``- entropy_coef * H``,
  so we set ``entropy_coef=0.01`` for the same effect. ``bound_coef`` has no rsl_rl
  equivalent — ``clip_actions=1.0`` hard-clips samples instead.
  """
  # Booster: Parameter(fill_value=-2.0) → std = exp(-2).
  booster_init_std = math.exp(-2.0)
  return RslRlOnPolicyRunnerCfg(
    actor=RslRlModelCfg(
      hidden_dims=(256, 128, 128),
      activation="elu",
      obs_normalization=True,
      distribution_cfg={
        "class_name": "GaussianDistribution",
        "init_std": booster_init_std,
        "std_type": "log",
        "std_range": (1e-3, 1.0),
      },
    ),
    critic=RslRlModelCfg(
      hidden_dims=(256, 256, 128),
      activation="elu",
      obs_normalization=True,
    ),
    algorithm=RslRlPpoAlgorithmCfg(
      value_loss_coef=1.0,
      use_clipped_value_loss=True,
      clip_param=0.2,
      # Booster T1.yaml entropy_coef=-0.01 with opposite loss sign → +0.01 here.
      entropy_coef=0.01,
      # Booster runner.mini_epochs=20; full-batch updates ≈ 1 mini-batch.
      num_learning_epochs=20,
      num_mini_batches=1,
      learning_rate=5.0e-6,  # Aug 7 K1 FT + ParameterWalk; 1e-5 oscillates from scratch.
      schedule="adaptive",
      gamma=0.995,
      lam=0.95,
      desired_kl=0.01,
      max_grad_norm=1.0,
    ),
    experiment_name="k1_velocity",
    save_interval=100,
    num_steps_per_env=24,  # Booster horizon_length
    max_iterations=100_000,
    clip_actions=1.0,  # Booster normalization.clip_actions
  )


def booster_k1_nubots_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """PPO runner matching NuBots ``agent.yaml`` (student = teacher MLP).

  Actor/critic ``[512, 256, 128]``, ``init_noise_std=0.5``, no action clip.
  ``obs_normalization=False`` so imported ONNX weights match raw deploy obs.
  Learning rate lowered for fine-tune from the teacher checkpoint.
  """
  return RslRlOnPolicyRunnerCfg(
    actor=RslRlModelCfg(
      hidden_dims=(512, 256, 128),
      activation="elu",
      obs_normalization=False,
      distribution_cfg={
        "class_name": "GaussianDistribution",
        "init_std": 0.5,
        "std_type": "scalar",
        # Floor keeps torch.normal valid if Adam briefly drives std_param < 0.
        "std_range": (1e-3, 1.0),
      },
    ),
    critic=RslRlModelCfg(
      hidden_dims=(512, 256, 128),
      activation="elu",
      obs_normalization=False,
    ),
    algorithm=RslRlPpoAlgorithmCfg(
      value_loss_coef=1.0,
      use_clipped_value_loss=True,
      clip_param=0.2,
      entropy_coef=0.005,
      num_learning_epochs=5,
      num_mini_batches=4,
      learning_rate=5.0e-5,  # FT from teacher (agent.yaml used 1e-3 from scratch).
      # Adaptive can ramp 5e-7 → 1e-2 when KL is low and NaN std_param mid-update.
      schedule="fixed",
      gamma=0.995,
      lam=0.95,
      desired_kl=0.01,
      max_grad_norm=1.0,
    ),
    experiment_name="k1_nubots",
    save_interval=100,
    num_steps_per_env=24,
    max_iterations=40_000,  # Continue FT past teacher adapt (was 20k) with tight shoulders.
    # Unclipped actions exploded mid arm-unlock FT (surrogate/obs NaN). ±1
    # matches Booster and keeps raw policy outputs in a sane band.
    clip_actions=1.0,
  )


def booster_k1_nubots_rough_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """NuBots PPO for rough FT: lower LR, eval/best checkpoint, slightly higher entropy."""
  cfg = booster_k1_nubots_ppo_runner_cfg()
  cfg.algorithm.learning_rate = 5.0e-6
  cfg.algorithm.entropy_coef = 0.008  # was 0.005; damp brittle gait on mixed terrain
  cfg.eval_interval = 1000
  cfg.eval_steps = 240
  return cfg


def booster_k1_nubots_phase1_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """Phase-1 posture lock: 2k iters, early stop, full-episode eval."""
  cfg = booster_k1_nubots_rough_ppo_runner_cfg()
  cfg.max_iterations = 2_000
  cfg.eval_interval = 500
  cfg.eval_steps = 1500
  cfg.early_stop_enabled = True
  cfg.early_stop_min_iters = 200
  cfg.early_stop_drop_fraction = 0.15
  cfg.early_stop_patience = 50
  return cfg


def booster_k1_nubots_phase2_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """Phase-2 rough ramp: 3k iters, early stop, full-episode eval."""
  cfg = booster_k1_nubots_phase1_ppo_runner_cfg()
  cfg.max_iterations = 3_000
  cfg.eval_interval = 500
  cfg.eval_steps = 1500
  cfg.early_stop_enabled = True
  cfg.early_stop_min_iters = 300
  cfg.early_stop_drop_fraction = 0.15
  cfg.early_stop_patience = 50
  return cfg


def booster_k1_nubots_phase2_stabilize_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """Phase-2 stabilize: 2k iters, tighter early stop on ep-length drop."""
  cfg = booster_k1_nubots_phase1_ppo_runner_cfg()
  cfg.max_iterations = 2_000
  cfg.eval_interval = 500
  cfg.eval_steps = 1500
  cfg.early_stop_enabled = True
  cfg.early_stop_min_iters = 150
  cfg.early_stop_drop_fraction = 0.10
  cfg.early_stop_patience = 30
  return cfg


def booster_k1_nubots_phase3_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """Phase-3 speed unlock: 2k iters, early stop, full-episode eval."""
  cfg = booster_k1_nubots_phase1_ppo_runner_cfg()
  cfg.max_iterations = 2_000
  cfg.eval_interval = 500
  cfg.eval_steps = 1500
  cfg.early_stop_enabled = True
  cfg.early_stop_min_iters = 200
  cfg.early_stop_drop_fraction = 0.12
  cfg.early_stop_patience = 40
  return cfg


def booster_k1_nubots_quality_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """Quality FT: gentler LR, denser eval, patient early stop.

  Prior run early-stopped at +335 iters before the next eval window, so
  ``model_best`` never moved off the resume checkpoint.
  """
  cfg = booster_k1_nubots_phase1_ppo_runner_cfg()
  cfg.max_iterations = 3_000
  cfg.algorithm.learning_rate = 2.0e-6
  cfg.eval_interval = 250
  cfg.eval_steps = 1500
  cfg.early_stop_enabled = True
  cfg.early_stop_min_iters = 600
  cfg.early_stop_drop_fraction = 0.15
  cfg.early_stop_patience = 80
  return cfg


def booster_k1_nubots_speed_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """Speed lineage, trained from scratch.

  Chains the NuBots base rather than Quality so it does not inherit the
  fine-tune settings: Quality's 2e-6 learning rate and drop-triggered early stop
  are meant for nudging an already-good policy, and both are wrong from a random
  init -- the early stop in particular would fire on the normal early thrash.

  ``schedule="fixed"`` is inherited deliberately. The adaptive schedule clamps to
  a 1e-5 floor and chases ``desired_kl=0.01`` hard enough that it effectively
  ignores a requested lower rate, which is what overwrote the pretrained policy
  in the earlier fine-tune attempts.
  """
  cfg = booster_k1_nubots_ppo_runner_cfg()
  cfg.algorithm.learning_rate = 1.0e-4
  cfg.algorithm.entropy_coef = 0.01  # more exploration than an FT needs
  cfg.max_iterations = 60_000
  cfg.eval_interval = 1_000
  cfg.eval_steps = 1_500
  cfg.early_stop_enabled = False
  return cfg


def booster_k1_nubots_htwk_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """HTWK/NuBots teacher-compatible fine-tune runner."""
  cfg = booster_k1_nubots_ppo_runner_cfg()
  cfg.max_iterations = 20_000
  cfg.save_interval = 100
  cfg.algorithm.learning_rate = 5.0e-6
  cfg.algorithm.entropy_coef = 0.005
  cfg.eval_interval = 500
  cfg.eval_steps = 1_500
  cfg.early_stop_enabled = False
  return cfg


def booster_k1_nubots_htwk_unclipped_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """40k signed-reward fine-tune runner for the HTWK task."""
  cfg = booster_k1_nubots_htwk_ppo_runner_cfg()
  cfg.max_iterations = 40_000
  return cfg


def booster_k1_nubots_htwk_exact_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """PPO runner matching the reference HTWK ``agent.yaml``."""
  cfg = booster_k1_nubots_ppo_runner_cfg()
  cfg.experiment_name = "k1_walk_htwk"
  cfg.max_iterations = 20_000
  cfg.algorithm.learning_rate = 1.0e-3
  cfg.algorithm.schedule = "adaptive"
  cfg.actor.obs_normalization = True
  cfg.critic.obs_normalization = True
  cfg.actor.distribution_cfg = dict(cfg.actor.distribution_cfg or {})
  cfg.actor.distribution_cfg.pop("std_range", None)
  cfg.clip_actions = None
  cfg.eval_interval = 0
  cfg.eval_steps = 0
  cfg.early_stop_enabled = False
  return cfg


def booster_k1_nubots_htwk_robust_ft_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """Stable fresh-optimizer runner for deployment-focused HTWK fine-tuning."""
  cfg = booster_k1_nubots_htwk_exact_ppo_runner_cfg()
  cfg.experiment_name = "k1_walk_htwk_robust_ft"
  cfg.max_iterations = 50_000
  # Keep the FT update size fixed; the adaptive schedule previously ramped a
  # nominal 5e-6 rate above 1e-4 and the policy collapsed.
  cfg.algorithm.learning_rate = 5.0e-6
  cfg.algorithm.schedule = "fixed"
  cfg.clip_actions = 1.0
  return cfg


def booster_k1_nubots_symmetry_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """Symmetry FT: quality env + left-right data augmentation on legs."""
  cfg = booster_k1_nubots_quality_ppo_runner_cfg()
  cfg.max_iterations = 2_000
  cfg.algorithm.learning_rate = 2.0e-6
  return _apply_nubots_symmetry(cfg)


def booster_k1_nubots_symmetry_v2_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """Symmetry v2: ankle kd=2, gentler LR after v1 train-stats dip."""
  cfg = booster_k1_nubots_symmetry_ppo_runner_cfg()
  cfg.max_iterations = 1_500
  cfg.algorithm.learning_rate = 1.0e-6
  cfg.eval_interval = 250
  cfg.early_stop_min_iters = 400
  cfg.early_stop_patience = 60
  return cfg


def booster_k1_nubots_phase1_symmetry_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """Phase-1 + symmetry from ONNX teacher (posture lock, 95/5 flat/rough)."""
  return _apply_nubots_symmetry(booster_k1_nubots_phase1_ppo_runner_cfg())


def booster_k1_nubots_phase2_symmetry_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """Phase-2 rough ramp + symmetry."""
  return _apply_nubots_symmetry(booster_k1_nubots_phase2_ppo_runner_cfg())


def booster_k1_nubots_phase2_stabilize_symmetry_ppo_runner_cfg() -> (
  RslRlOnPolicyRunnerCfg
):
  """Phase-2 stabilize (70/15/15) + symmetry."""
  return _apply_nubots_symmetry(booster_k1_nubots_phase2_stabilize_ppo_runner_cfg())


def booster_k1_nubots_phase3_symmetry_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """Phase-3 speed unlock + symmetry."""
  return _apply_nubots_symmetry(booster_k1_nubots_phase3_ppo_runner_cfg())


def booster_k1_fast_sac_runner_cfg() -> FastSacRunnerCfg:
  """Create FastSAC runner configuration for Booster K1 velocity task."""
  return FastSacRunnerCfg(
    algorithm=FastSacAlgorithmCfg(
      critic_learning_rate=3e-4,
      actor_learning_rate=3e-4,
      alpha_learning_rate=3e-4,
      buffer_size=1024,
      num_steps=1,
      gamma=0.97,
      tau=0.125,
      batch_size=8192,
      learning_starts=10,
      policy_frequency=4,
      num_updates=8,
      target_entropy_ratio=0.0,
      num_atoms=101,
      v_min=-20.0,
      v_max=20.0,
      critic_hidden_dim=768,
      actor_hidden_dim=512,
      alpha_init=0.001,
      use_autotune=True,
      use_tanh=True,
      obs_normalization=True,
      use_layer_norm=True,
      num_q_networks=2,
      amp=True,
      amp_dtype="bf16",
      compile=False,
      logging_interval=100,
    ),
    experiment_name="k1_velocity_fast_sac",
    save_interval=1_000,
    max_iterations=50_000,
    obs_groups={"actor": ("actor",), "critic": ("critic",)},
  )

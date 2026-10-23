"""RL configuration for Booster K1 velocity task."""

import math

from mjlab.rl import (
  RslRlModelCfg,
  RslRlOnPolicyRunnerCfg,
  RslRlPpoAlgorithmCfg,
)


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


def booster_k1_base_walk_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """PPO for BaseWalk: scratch original (1e-5 adaptive, std 1e-3–1.0)."""
  cfg = booster_k1_ppo_runner_cfg()
  cfg.algorithm.learning_rate = 1.0e-5
  cfg.algorithm.schedule = "adaptive"
  cfg.experiment_name = "k1_base_walk"
  cfg.max_iterations = 50_000
  cfg.clip_actions = None
  cfg.actor.distribution_cfg = dict(cfg.actor.distribution_cfg or {})
  cfg.actor.distribution_cfg["std_range"] = (1e-3, 1.0)
  return cfg


def booster_k1_base_walk_rough_ft_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """BaseWalk rough FT: fixed 5e-6 LR (HTWK robust-style)."""
  cfg = booster_k1_base_walk_ppo_runner_cfg()
  cfg.algorithm.learning_rate = 5.0e-6
  cfg.algorithm.schedule = "fixed"
  cfg.experiment_name = "k1_base_walk_rough_ft"
  cfg.max_iterations = 15_000
  return cfg


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
  cfg.actor.distribution_cfg = dict(cfg.actor.distribution_cfg or {})
  # Cap exploration during long FT resumes; uncapped std preceded both collapses.
  cfg.actor.distribution_cfg["std_range"] = (0.05, 0.40)
  cfg.early_stop_enabled = True
  cfg.early_stop_min_iters = 200
  cfg.early_stop_drop_fraction = 0.20
  cfg.early_stop_patience = 80
  return cfg

"""RL configuration for Booster K1 velocity task."""

import math

from mjlab.rl import (
  FastSacAlgorithmCfg,
  FastSacRunnerCfg,
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

"""RL runner configuration for the unified K1 Arc→Setup→Strike kick task."""

import math

from mjlab.rl import (
  RslRlModelCfg,
  RslRlOnPolicyRunnerCfg,
  RslRlPpoAlgorithmCfg,
)


def _k1_kick_ppo_base(
  *, experiment_name: str, max_iterations: int
) -> RslRlOnPolicyRunnerCfg:
  """PPO MLP + std match BaseWalk for warm-start."""
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
      entropy_coef=0.005,
      num_learning_epochs=5,
      num_mini_batches=4,
      learning_rate=5.0e-4,
      schedule="adaptive",
      gamma=0.995,
      lam=0.95,
      desired_kl=0.01,
      max_grad_norm=1.0,
    ),
    experiment_name=experiment_name,
    save_interval=100,
    num_steps_per_env=24,
    max_iterations=max_iterations,
  )


def k1_arc_kick_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """PPO for full kick."""
  return _k1_kick_ppo_base(experiment_name="k1_arc_kick", max_iterations=20_000)


def k1_kick_approach_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """PPO for approach-only stage."""
  return _k1_kick_ppo_base(experiment_name="k1_kick_approach", max_iterations=10_000)


def k1_kick_near_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """PPO for near-ball kick stage."""
  return _k1_kick_ppo_base(experiment_name="k1_kick_near", max_iterations=15_000)

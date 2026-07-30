"""RL runner configurations for K1 kick tasks."""

from mjlab.rl import (
  RslRlModelCfg,
  RslRlOnPolicyRunnerCfg,
  RslRlPpoAlgorithmCfg,
)


def k1_approach_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """Runner config for the ball-approach task.

  Identical network size to the velocity task so a locomotion checkpoint
  can be loaded directly (obs dim will differ by +3 for ball_rel_pos; the
  extra input weights are randomly initialised).
  """
  return RslRlOnPolicyRunnerCfg(
    actor=RslRlModelCfg(
      hidden_dims=(512, 256, 128),
      activation="elu",
      obs_normalization=True,
      distribution_cfg={
        "class_name": "GaussianDistribution",
        "init_std": 1.0,
        "std_type": "scalar",
      },
    ),
    critic=RslRlModelCfg(
      hidden_dims=(512, 256, 128),
      activation="elu",
      obs_normalization=True,
    ),
    algorithm=RslRlPpoAlgorithmCfg(
      value_loss_coef=1.0,
      use_clipped_value_loss=True,
      clip_param=0.2,
      entropy_coef=0.01,
      num_learning_epochs=5,
      num_mini_batches=4,
      learning_rate=1.0e-3,
      schedule="adaptive",
      gamma=0.99,
      lam=0.95,
      desired_kl=0.01,
      max_grad_norm=1.0,
    ),
    experiment_name="k1_approach",
    save_interval=100,
    num_steps_per_env=24,
    max_iterations=15_000,
  )


def k1_score_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  """Runner config for the kick-to-goal task."""
  return RslRlOnPolicyRunnerCfg(
    actor=RslRlModelCfg(
      hidden_dims=(512, 256, 128),
      activation="elu",
      obs_normalization=True,
      distribution_cfg={
        "class_name": "GaussianDistribution",
        "init_std": 1.0,
        "std_type": "scalar",
      },
    ),
    critic=RslRlModelCfg(
      hidden_dims=(512, 256, 128),
      activation="elu",
      obs_normalization=True,
    ),
    algorithm=RslRlPpoAlgorithmCfg(
      value_loss_coef=1.0,
      use_clipped_value_loss=True,
      clip_param=0.2,
      entropy_coef=0.005,  # lower entropy: more exploitation of the prior
      num_learning_epochs=5,
      num_mini_batches=4,
      learning_rate=5.0e-4,  # lower LR for fine-tuning
      schedule="adaptive",
      gamma=0.995,  # longer horizon: ball needs time to travel
      lam=0.95,
      desired_kl=0.01,
      max_grad_norm=1.0,
    ),
    experiment_name="k1_score",
    save_interval=100,
    num_steps_per_env=24,
    max_iterations=20_000,
  )

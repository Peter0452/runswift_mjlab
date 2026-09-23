"""AMP runner config for Near kick (kick-clip style until contact)."""

from __future__ import annotations

import math
from pathlib import Path

from mjlab.amp.runners import (
  AmpDiscriminatorCfg,
  AmpOnPolicyRunnerCfg,
  AmpRslRlPpoAlgorithmCfg,
)
from mjlab.rl import RslRlModelCfg

# Project/RL/data/retargeted/k1/kick (WW-quality plant clips).
_KICK_AMP_DIR = (
  Path(__file__).resolve().parents[6].parent / "data" / "retargeted" / "k1" / "kick"
)


def k1_kick_near_amp_ppo_runner_cfg() -> AmpOnPolicyRunnerCfg:
  """Near kick + always-on kick AMP until ``kick_detected``, then style off.

  Actor/critic sizes match Near PPO so warm-start from a Near checkpoint works.
  """
  if not _KICK_AMP_DIR.is_dir():
    raise FileNotFoundError(
      f"Kick AMP dataset not found at {_KICK_AMP_DIR}. "
      "Expected retargeted kick clips under data/retargeted/k1/kick."
    )
  return AmpOnPolicyRunnerCfg(
    actor=RslRlModelCfg(
      hidden_dims=(256, 128, 128),
      activation="elu",
      obs_normalization=True,
      distribution_cfg={
        "class_name": "GaussianDistribution",
        "init_std": math.exp(-2.0),
        "std_type": "log",
        "std_range": (1e-3, 1.0),
      },
    ),
    critic=RslRlModelCfg(
      hidden_dims=(256, 256, 128),
      activation="elu",
      obs_normalization=True,
    ),
    discriminator=AmpDiscriminatorCfg(
      hidden_layer_sizes=(256, 128),
      reward_scale=1.0,
      reward_clamp_epsilon=1.0e-4,
      loss_type="bce",
      loss_fn_kwargs={},
    ),
    algorithm=AmpRslRlPpoAlgorithmCfg(
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
    experiment_name="k1_kick_near_amp",
    save_interval=100,
    num_steps_per_env=24,
    max_iterations=15_000,
    dataset_root=str(_KICK_AMP_DIR),
    speed_factor=1.0,
    dataset_augmentations=[
      {"name": "mirror"},
      {"name": "speed", "percent": 10.0},
      {"name": "speed", "percent": -10.0},
    ],
    style_reward_weight=0.3,
  )

"""RL configs for Kick-on-Walk-AMP (thesis Appendix B.1 + Walk AMP DA/Muon)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mjlab.amp.runners import (
  AmpDiscriminatorCfg,
  AmpOnPolicyRunnerCfg,
  AmpRslRlMuonPpoAlgorithmCfg,
  AmpRslRlPpoAlgorithmCfg,
)
from mjlab.rl import RslRlModelCfg, RslRlOnPolicyRunnerCfg, RslRlPpoAlgorithmCfg

_KICK_AMP_DIR = (
  Path(__file__).resolve().parents[6].parent / "data" / "retargeted" / "k1" / "kick"
)

_AMP_SYMMETRY_CFG = {
  "use_data_augmentation": True,
  "use_mirror_loss": False,
  "data_augmentation_func": "mjlab.tasks.velocity.mdp.amp_symmetry:augment_symmetries",
}


@dataclass
class RslRlMuonPpoAlgorithmCfg(RslRlPpoAlgorithmCfg):
  """Standard PPO with Muon for actor/critic matrix weights."""

  class_name: str = "mjlab.rl.muon:MuonPPO"
  muon_weight_decay: float = 0.0
  muon_momentum: float = 0.95
  muon_ns_steps: int = 5


def k1_kick_walkamp_ppo_runner_cfg(
  *,
  use_muon: bool = False,
  use_symmetry: bool = False,
) -> RslRlOnPolicyRunnerCfg:
  """PPO Kick-on-Walk-AMP (no AMP style / discriminator)."""
  algorithm_cls = RslRlMuonPpoAlgorithmCfg if use_muon else RslRlPpoAlgorithmCfg
  cfg = RslRlOnPolicyRunnerCfg(
    actor=RslRlModelCfg(
      hidden_dims=(512, 256, 128),
      activation="elu",
      obs_normalization=True,
      distribution_cfg={
        "class_name": "rsl_rl.modules.distribution:GaussianDistribution",
        "init_std": 1.0,
      },
    ),
    critic=RslRlModelCfg(
      hidden_dims=(512, 256, 128),
      activation="elu",
      obs_normalization=True,
    ),
    algorithm=algorithm_cls(
      value_loss_coef=1.0,
      use_clipped_value_loss=True,
      clip_param=0.2,
      entropy_coef=0.01,
      num_learning_epochs=5,
      num_mini_batches=4,
      learning_rate=1.0e-4,
      schedule="adaptive",
      gamma=0.99,
      lam=0.95,
      desired_kl=0.01,
      max_grad_norm=1.0,
    ),
    experiment_name="k1_kick_walkamp"
    + ("_da" if use_symmetry else "")
    + ("_muon" if use_muon else ""),
    save_interval=100,
    num_steps_per_env=24,
    max_iterations=15_000,
  )
  if use_symmetry:
    cfg.algorithm.symmetry_cfg = dict(_AMP_SYMMETRY_CFG)
  return cfg


def k1_kick_walkamp_amp_ppo_runner_cfg(
  *,
  use_muon: bool = False,
  use_symmetry: bool = False,
) -> AmpOnPolicyRunnerCfg:
  """Kick-on-Walk-AMP + kick AMP dataset; optional DA + Muon.

  Train from scratch (no Walk 9950 reload). Style weight 0.3 until
  ``kick_detected`` (runner gate).
  """
  if not _KICK_AMP_DIR.is_dir():
    raise FileNotFoundError(
      f"Kick AMP dataset not found at {_KICK_AMP_DIR}. "
      "Expected retargeted kick clips under data/retargeted/k1/kick."
    )
  algorithm_cls = AmpRslRlMuonPpoAlgorithmCfg if use_muon else AmpRslRlPpoAlgorithmCfg
  cfg = AmpOnPolicyRunnerCfg(
    actor=RslRlModelCfg(
      hidden_dims=(512, 256, 128),
      activation="elu",
      obs_normalization=True,
      distribution_cfg={
        "class_name": "rsl_rl.modules.distribution:GaussianDistribution",
        "init_std": 1.0,
      },
    ),
    critic=RslRlModelCfg(
      hidden_dims=(512, 256, 128),
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
    algorithm=algorithm_cls(
      value_loss_coef=1.0,
      use_clipped_value_loss=True,
      clip_param=0.2,
      entropy_coef=0.01,
      num_learning_epochs=5,
      num_mini_batches=4,
      learning_rate=1.0e-4,
      schedule="adaptive",
      gamma=0.99,
      lam=0.95,
      desired_kl=0.01,
      max_grad_norm=1.0,
    ),
    experiment_name="k1_kick_walkamp_amp"
    + ("_da" if use_symmetry else "")
    + ("_muon" if use_muon else ""),
    save_interval=100,
    num_steps_per_env=24,
    max_iterations=15_000,
    speed_factor=1.0,
    dataset_root=str(_KICK_AMP_DIR),
    dataset_augmentations=[
      {"name": "mirror"},
      {"name": "speed", "percent": 10.0},
      {"name": "speed", "percent": -10.0},
    ],
    style_reward_weight=0.3,
  )
  if use_symmetry:
    cfg.algorithm.symmetry_cfg = dict(_AMP_SYMMETRY_CFG)
  return cfg

"""RL configuration for Booster K1 AMP velocity tasks."""

from __future__ import annotations

import json
from pathlib import Path

from mjlab.amp.runners import (
  AmpDiscriminatorCfg,
  AmpOnPolicyRunnerCfg,
  AmpRslRlMuonPpoAlgorithmCfg,
  AmpRslRlPpoAlgorithmCfg,
)
from mjlab.rl import RslRlModelCfg

_AMP_SYMMETRY_CFG = {
  "use_data_augmentation": True,
  "use_mirror_loss": False,
  "data_augmentation_func": "mjlab.tasks.velocity.mdp.amp_symmetry:augment_symmetries",
}

# Whirlwind LAFAN + CMU-09 K1 retargets. Weights: WW 70% (equal per clip),
# CMU 30% (duration-proportional within CMU so 09_12 dominates).
# rl_cfg.py → …/runswift_mjlab/src/mjlab/tasks/velocity/config/k1_amp
# parents[6] = runswift_mjlab, parent of that = Project/RL
_AMP_MIX_DIR = (
  Path(__file__).resolve().parents[6].parent / "data" / "amp_mix_ww_cmu"
)
_AMP_MIX_WEIGHTS_FILE = _AMP_MIX_DIR / "dataset_weights.json"


def _amp_mix_dataset() -> tuple[str, list[float] | None]:
  """Return (dataset_root, weights) for the local WW+CMU mix if present."""
  if not _AMP_MIX_DIR.is_dir():
    return "whirlwind-ams/lafan_locomotion_k1", None
  weights: list[float] | None = None
  if _AMP_MIX_WEIGHTS_FILE.is_file():
    meta = json.loads(_AMP_MIX_WEIGHTS_FILE.read_text())
    weights = [float(w) for w in meta["weights"]]
  return str(_AMP_MIX_DIR), weights


def booster_k1_amp_ppo_runner_cfg(use_muon: bool = False) -> AmpOnPolicyRunnerCfg:
  """AMP runner configuration matching booster_mjlab's K1 walk recipe.

  With ``use_muon`` the actor/critic matrices are optimized with Muon; the
  discriminator stays on Adam.

  Uses ``data/amp_mix_ww_cmu`` when that folder exists (WW + CMU-09 with
  curated sampling weights); otherwise falls back to the Hub LAFAN set.
  """
  dataset_root, dataset_weights = _amp_mix_dataset()
  algorithm_cls = AmpRslRlMuonPpoAlgorithmCfg if use_muon else AmpRslRlPpoAlgorithmCfg
  return AmpOnPolicyRunnerCfg(
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
      learning_rate=1.0e-3,
      schedule="adaptive",
      gamma=0.99,
      lam=0.95,
      desired_kl=0.01,
      max_grad_norm=1.0,
    ),
    experiment_name="k1_velocity_amp" + ("_muon" if use_muon else ""),
    save_interval=50,
    num_steps_per_env=24,
    max_iterations=30_000,
    speed_factor=1.0,
    dataset_root=dataset_root,
    dataset_weights=dataset_weights,
    dataset_augmentations=[
      {"name": "mirror"},
      {"name": "speed", "percent": 10.0},
      {"name": "speed", "percent": -10.0},
      {"name": "speed", "percent": 20.0},
      {"name": "speed", "percent": -20.0},
    ],
    style_reward_weight=0.3,
  )


def booster_k1_amp_ppo_symmetric_runner_cfg(
  use_muon: bool = False,
) -> AmpOnPolicyRunnerCfg:
  """AMP runner configuration with left/right symmetry data augmentation."""
  cfg = booster_k1_amp_ppo_runner_cfg(use_muon=use_muon)
  cfg.algorithm.symmetry_cfg = dict(_AMP_SYMMETRY_CFG)
  cfg.experiment_name = cfg.experiment_name.replace(
    "k1_velocity_amp", "k1_velocity_amp_symmetric"
  )
  return cfg

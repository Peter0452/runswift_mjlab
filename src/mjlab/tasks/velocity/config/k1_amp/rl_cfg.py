"""RL configuration for Booster K1 AMP velocity tasks."""

from __future__ import annotations

import json
import os
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

# Whirlwind LAFAN + CMU-09 K1 retargets.
# Stage A (default ``dataset_weights.json``): WW 50% equal; CMU 50% with
# 09_12 dominant and sprints capped at 15% total mass.
# Stage B (``dataset_weights_equal_cmu.json``): same 50/50 but CMU equal-clip —
# swap this file in (or point here) when widening after ~4k iters.
# rl_cfg.py → …/runswift_mjlab/src/mjlab/tasks/velocity/config/k1_amp
# parents[6] = runswift_mjlab, parent of that = Project/RL
_AMP_MIX_DIR = Path(__file__).resolve().parents[6].parent / "data" / "amp_mix_ww_cmu"
_AMP_MIX_WEIGHTS_FILE = _AMP_MIX_DIR / "dataset_weights.json"
_AMP_KICK_MIX_DIR = _AMP_MIX_DIR.parent / "amp_mix_ww_cmu_kicks_v2"
_AMP_KICK_MIX_WEIGHTS = _AMP_KICK_MIX_DIR / "dataset_weights.json"
KICK_STYLE_AMP_DATA = True


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


def booster_k1_kick_stage1_runner_cfg() -> AmpOnPolicyRunnerCfg:
  """Flat DA-Muon walk runner for kick stage 1. Dataset stays the 50/50 mix."""
  cfg = booster_k1_amp_ppo_symmetric_runner_cfg(use_muon=True)
  cfg.experiment_name = "k1_kick_stage1_amp"
  return cfg


def booster_k1_kick_approach_runner_cfg() -> AmpOnPolicyRunnerCfg:
  """Approach stage. Same walk AMP runner, separate log directory."""
  cfg = booster_k1_kick_stage1_runner_cfg()
  cfg.experiment_name = "k1_kick_approach_amp"
  cfg.run_name = "approach"
  return cfg


KICK_MAX_ACTION_STD = 0.6


def booster_k1_kick_stage3_runner_cfg() -> AmpOnPolicyRunnerCfg:
  """Kick stage. Same walk AMP runner; the task gates style off around kicks."""
  cfg = booster_k1_kick_stage1_runner_cfg()
  cfg.experiment_name = "k1_kick_stage3_amp"
  cfg.run_name = "stage3"
  # Half the walk's entropy bonus: kick rewards already drive exploration, and
  # action noise grew unchecked in stage3_v2/v3.
  cfg.algorithm.entropy_coef = 0.005
  # Longer horizon (~4 s at 50 Hz instead of ~2 s). With 0.99 a fall cost
  # only ~24 in discounted value against ~36 for a kick, and every
  # continuation of v8 drifted toward riskier kicks (falls 2 s after kicks
  # 37 % → 66 % of all falls).
  cfg.algorithm.gamma = 0.995
  # Smooth deterministic actions (CAPS). The action_rate reward did not reduce
  # jitter: in the runner sim v17/v18 jittered 13x the deployed walk policy.
  # 1.0 / 0.5 (v19) reached ~2x the walk's jitter but cut kick accuracy
  # (93% -> 81%) and raised falls (0.2% -> 4.2%); v20 at 0.3 / 0.1 kept the
  # kick but jittered 4.5x. v21/v22 at 0.5 / 0.2 kept 94-95% accuracy but
  # jitter swung 2.1-4.8x between checkpoints; v23 at 0.8 / 0.3 still ~4x
  # while active. v24 uses 1.0 / 0.4.
  # v42 (0.6 / 0.25 everywhere): kick swing p50 3.51 → 3.94 m/s but leg
  # jitter +7–9 % at matched walking speed. v43: full CAPS while walking,
  # half within 0.8 m of the ball (actor ball estimate) for the kick swing.
  cfg.algorithm.caps_temporal_coef = 1.0
  cfg.algorithm.caps_spatial_coef = 0.4
  cfg.algorithm.caps_near_ball_scale = 0.5
  cfg.algorithm.caps_near_ball_dist = 0.8
  # Cap action noise: it grew in every kick run (v3 0.48→1.47, v5 0.82→1.40),
  # inflating action_rate and falls. v4 kicked well at 0.55–0.7.
  assert cfg.actor.distribution_cfg is not None
  cfg.actor.distribution_cfg = dict(
    cfg.actor.distribution_cfg, std_range=(0.05, KICK_MAX_ACTION_STD)
  )
  cfg.algorithm.symmetry_cfg = dict(
    _AMP_SYMMETRY_CFG,
    data_augmentation_func=(
      "mjlab.tasks.velocity.mdp.amp_symmetry:augment_symmetries_kick_loop"
    ),
  )
  # K4 (v59): walk data plus kick clips recorded in our sim — B-Human's
  # side-foot kicks and our own front kicks (data/kick_clips, 20 % of style
  # samples) — with style kept on near the ball (KICK_STYLE_AMP), so both kick
  # styles are "natural" and the outcome rewards choose between them.
  genes = json.loads(os.environ.get("KICK_GENES", "{}") or "{}")
  if "desired_kl" in genes:
    cfg.algorithm.desired_kl = float(genes["desired_kl"])
  # L5 teacher imitation (B-Human near-ball leg actions), off by default.
  if float(genes.get("imitation_coef", 0.0)) > 0.0:
    cfg.algorithm.imitation_coef = float(genes["imitation_coef"])
    cfg.algorithm.imitation_decay_updates = int(genes.get("imitation_decay_updates", 1000))
  use_kick_data = bool(genes.get("amp_kick_data", KICK_STYLE_AMP_DATA))
  if use_kick_data and _AMP_KICK_MIX_WEIGHTS.is_file():
    meta = json.loads(_AMP_KICK_MIX_WEIGHTS.read_text())
    cfg.dataset_root = str(_AMP_KICK_MIX_DIR)
    cfg.dataset_weights = [float(w) for w in meta["weights"]]
  return cfg


def booster_k1_amp_kick_handoff_runner_cfg() -> AmpOnPolicyRunnerCfg:
  """Short warm-start fine-tune of the rough AMP walk on kick handoffs."""
  cfg = booster_k1_amp_ppo_symmetric_runner_cfg(use_muon=True)
  cfg.algorithm.learning_rate = 2.0e-4
  cfg.max_iterations = 12_000
  cfg.experiment_name = "k1_velocity_amp_symmetric_muon_wwcmu50_roughft"
  cfg.run_name = "kickhandoff"
  return cfg


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

"""AMP-PPO runner config for the Booster K1 dribble."""

from __future__ import annotations

import json
import os

from k1.tasks.dribble.mdp.dribble_rewards import KICK_GROUP_TERMS
from k1.tasks.kick.rl_cfg import (
  _KICK_TEACHER_CKPT,
  KICK_MAX_ACTION_STD,
  booster_k1_kick_stage1_runner_cfg,
)
from k1.tasks.walk.rl_cfg import (
  _AMP_MIX_DIR,
  _AMP_SYMMETRY_CFG,
)
from mjlab.amp.runners import (
  AmpOnPolicyRunnerCfg,
)

_AMP_DRIBBLE_MIX_DIR = _AMP_MIX_DIR.parent / "amp_mix_dribble_stage2"
_AMP_DRIBBLE_MIX_WEIGHTS = _AMP_DRIBBLE_MIX_DIR / "dataset_weights.json"
_AMP_DRIBBLE_FAST_MIX_WEIGHTS = _AMP_DRIBBLE_MIX_DIR / "dataset_weights_fast.json"


def booster_k1_dribble_runner_cfg() -> AmpOnPolicyRunnerCfg:
  """Stage-2 dribble runner: 70% GVHMR dribble/cut clips + 30% WW/CMU walks."""
  cfg = booster_k1_kick_stage1_runner_cfg()
  cfg.experiment_name = "k1_dribble_amp"
  cfg.run_name = "dribble"
  cfg.algorithm.entropy_coef = 0.005
  cfg.algorithm.caps_temporal_coef = 1.0
  cfg.algorithm.caps_spatial_coef = 0.4
  cfg.algorithm.caps_near_ball_scale = 0.5
  cfg.algorithm.caps_near_ball_dist = 0.8
  assert cfg.actor.distribution_cfg is not None
  cfg.actor.distribution_cfg = dict(
    cfg.actor.distribution_cfg, std_range=(0.05, KICK_MAX_ACTION_STD)
  )
  cfg.algorithm.symmetry_cfg = dict(
    _AMP_SYMMETRY_CFG,
    data_augmentation_func=("k1.tasks.dribble.mdp.dribble:augment_symmetries_dribble"),
  )
  # v19 (2026-10-20): DRIBBLE_GENES {"amp_mix": "fast"} swaps in the fast weights
  # (same clips). The stage-2 mix puts 11 % of its weight on clips above
  # 1.2 m/s (weighted mean 0.56 m/s), so style rewards the slow gait.
  genes = json.loads(os.environ.get("DRIBBLE_GENES", "{}") or "{}")
  weights_file = _AMP_DRIBBLE_MIX_WEIGHTS
  if genes.get("amp_mix") == "fast":
    weights_file = _AMP_DRIBBLE_FAST_MIX_WEIGHTS
    assert weights_file.is_file(), weights_file
  # v26 (2026-10-21): runner-sim leg jitter rose 0.067 (v17/v18) -> ~0.080 (v20,
  # conditioned style) -> ~0.10 (v22+, sprints / vanish / kick windows); CAPS
  # weights as genes (the kick loop has them in KICK_GENES).
  # v27: a kick critic. Three groups (style, dribble task, kick) with their own
  # heads and advantage weights; the kick terms leave the task group.
  if "critic_alphas" in genes:
    cfg.algorithm.multi_critic_alphas = tuple(float(a) for a in genes["critic_alphas"])
    if len(cfg.algorithm.multi_critic_alphas) == 3:
      cfg.extra_reward_group = KICK_GROUP_TERMS
  for g in ("caps_temporal_coef", "caps_spatial_coef", "caps_near_ball_scale"):
    if g in genes:
      setattr(cfg.algorithm, g, float(genes[g]))
  if float(genes.get("kick_teacher_coef", 0.0)) > 0.0:
    # v23 (2026-10-21): v22's kick reward alone left kicks at ~1.6 m/s, 50 deg
    # after 1000 iterations. The kick-loop champion candidate h011 (long kick
    # 4.4-4.5 m/s, accurate) shares the 83 inputs; imitate its legs in kick
    # windows near the ball, fading over kick_teacher_decay updates.
    cfg.kick_teacher_checkpoint = str(_KICK_TEACHER_CKPT)
    cfg.algorithm.imitation_coef = float(genes["kick_teacher_coef"])
    cfg.algorithm.imitation_decay_updates = int(genes.get("kick_teacher_decay", 5000))
    # v24: v23 imitated legs within 1.5 m only and the student stayed at
    # 1.6 m/s, 42 deg, while the teacher alone in the same kick windows kicked
    # 3.1 m/s (p90 5.2), 14.5 deg: its approach and arms are part of the kick.
    if "kick_teacher_dist" in genes:
      cfg.kick_teacher_dist = float(genes["kick_teacher_dist"])
    cfg.kick_teacher_arms = bool(genes.get("kick_teacher_arms", False))
    if "kick_teacher_max_offset_deg" in genes:
      cfg.kick_teacher_max_offset_deg = float(genes["kick_teacher_max_offset_deg"])
    if "kick_teacher_bhuman_dist" in genes:
      cfg.kick_teacher_bhuman_dist = float(genes["kick_teacher_bhuman_dist"])
    if "kick_takeover_prob" in genes:
      cfg.kick_takeover_prob = float(genes["kick_takeover_prob"])
      cfg.kick_takeover_decay = int(genes.get("kick_takeover_decay", 3000))
  if genes.get("amp_cond"):
    # v20: conditioned discriminator (env_cfgs adds the amp_cond group). The
    # stage-2 clip weights put 11 % of the mass above 1.2 m/s; give each
    # travel-speed bin its own share so fast commands have expert frames.
    cfg.amp_speed_mass = (
      (0.3, 0.15),
      (0.7, 0.30),
      (1.1, 0.20),
      (1.6, 0.20),
      (3.5, 0.15),
    )
  if weights_file.is_file():
    meta = json.loads(weights_file.read_text())
    cfg.dataset_root = str(_AMP_DRIBBLE_MIX_DIR)
    cfg.dataset_weights = [float(w) for w in meta["weights"]]
  cfg.decap = False
  # v27: the critic_alphas gene (above) overrides this default.
  if "critic_alphas" not in genes:
    cfg.algorithm.multi_critic_alphas = (0.2, 0.8)
  # v15b (2026-10-19): v15 checkpoints swung hard in deterministic evals
  # (1.0 m/s success 0.52 at 12100 -> 0.24 at 12400, 2 seeds) while every
  # training curve stayed flat: the adaptive schedule held Muon at ~1e-3 and
  # action std sat at the 0.6 cap. Same fix as the self-play kick: fixed small
  # steps and less action noise.
  cfg.algorithm.schedule = "fixed"
  cfg.algorithm.learning_rate = DRIBBLE_LR
  cfg.actor.distribution_cfg = dict(
    cfg.actor.distribution_cfg, std_range=(0.05, DRIBBLE_MAX_ACTION_STD)
  )
  return cfg


DRIBBLE_LR = 1.0e-4
DRIBBLE_MAX_ACTION_STD = 0.4

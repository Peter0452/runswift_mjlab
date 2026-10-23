"""Kick stage 1: flat DA-Muon walk, rough fine-tune ground, zero kick slots."""

from __future__ import annotations

import torch

import mjlab.tasks  # noqa: F401  (registers tasks)
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg
from mjlab.tasks.velocity.mdp.amp_symmetry import (
  CRITIC_EXTRA_DIM_WALK,
  POLICY_DIM_KICK_STAGE1,
  flip_k1_critic_obs_left_right,
  flip_k1_policy_obs_left_right,
)
from mjlab.tasks.velocity.mdp.observations import constant_zeros

TASK = "Mjlab-Velocity-Kick-Stage1-Amp-DA-Muon-Booster-K1"


def test_stage1_terrain_is_the_rough_finetune_mix() -> None:
  cfg = load_env_cfg(TASK)
  assert cfg.scene.terrain is not None
  generator = cfg.scene.terrain.terrain_generator
  assert generator is not None
  assert generator.curriculum is False
  assert cfg.curriculum is not None
  assert "terrain_levels" not in cfg.curriculum
  terrains = generator.sub_terrains
  assert set(terrains) == {"flat", "random_rough", "wave_terrain"}
  assert terrains["flat"].proportion == 0.80
  assert terrains["random_rough"].proportion == 0.10
  assert terrains["random_rough"].noise_range == (0.02, 0.10)
  assert terrains["wave_terrain"].proportion == 0.10
  assert terrains["wave_terrain"].amplitude_range == (0.0, 0.2)
  assert terrains["wave_terrain"].num_waves == 4


def test_stage1_command_curriculum_raises_only_the_final_forward_cap() -> None:
  cfg = load_env_cfg(TASK)
  assert cfg.curriculum is not None
  stages = cfg.curriculum["command_vel"].params["velocity_stages"]
  assert stages[-1]["lin_vel_x"] == (-1.5, 2.0)
  assert stages[-1]["lin_vel_y"] == (-1.75, 1.75)
  assert stages[-1]["ang_vel_z"] == (-1.5, 1.5)
  assert stages[-1]["step"] == 15000 * 24
  assert cfg.rewards["track_linear_velocity"].weight == 2.25
  assert cfg.rewards["track_angular_velocity"].weight == 2.0
  assert cfg.commands is not None
  assert cfg.commands["twist"].rel_standing_envs == 0.2


def test_stage1_kick_slots_are_zeros_after_the_twist_command() -> None:
  cfg = load_env_cfg(TASK)
  actor = list(cfg.observations["actor"].terms)
  critic = list(cfg.observations["critic"].terms)
  assert actor[5:9] == ["command", "speed_limit", "kick_direction", "kick_range"]
  assert critic[5:10] == [
    "command",
    "speed_limit",
    "kick_direction",
    "kick_range",
    "base_lin_vel",
  ]
  for name, dim in (("speed_limit", 3), ("kick_direction", 2), ("kick_range", 3)):
    term = cfg.observations["actor"].terms[name]
    assert term.func is constant_zeros
    assert term.params["dim"] == dim
    assert term.noise is None


def test_stage1_runner_is_flat_da_muon_on_the_half_half_mix() -> None:
  rl = load_rl_cfg(TASK)
  assert rl.experiment_name == "k1_kick_stage1_amp"
  assert rl.algorithm.use_muon is True
  assert rl.algorithm.symmetry_cfg is not None
  assert rl.dataset_weights is not None
  assert abs(sum(rl.dataset_weights[:12]) - 0.5) < 1e-9
  assert abs(sum(rl.dataset_weights[12:]) - 0.5) < 1e-9
  assert rl.style_reward_weight == 0.3


def test_stage1_symmetry_keeps_zero_slots_zero_and_flips_lateral_signs() -> None:
  """Stage 1 writes zeros in the tail, so the approach sign flips stay zero."""
  n = 4
  actor = torch.zeros(n, POLICY_DIM_KICK_STAGE1)
  actor[:, :75] = torch.randn(n, 75)
  flipped = flip_k1_policy_obs_left_right(actor)
  assert torch.equal(flipped[:, 75:], actor[:, 75:])
  assert torch.equal(flip_k1_policy_obs_left_right(flipped), actor)

  signed = torch.randn(n, POLICY_DIM_KICK_STAGE1)
  signed_flipped = flip_k1_policy_obs_left_right(signed)
  for index in (75, 76, 77, 78, 80, 81, 82):
    assert torch.equal(signed_flipped[:, index], signed[:, index])
  assert torch.equal(signed_flipped[:, 79], -signed[:, 79])
  assert torch.equal(flip_k1_policy_obs_left_right(signed_flipped), signed)

  critic = torch.randn(n, POLICY_DIM_KICK_STAGE1 + CRITIC_EXTRA_DIM_WALK)
  critic_flipped = flip_k1_critic_obs_left_right(critic)
  assert torch.equal(critic_flipped[:, 77], critic[:, 77])
  assert torch.equal(critic_flipped[:, 79], -critic[:, 79])
  assert torch.equal(flip_k1_critic_obs_left_right(critic_flipped), critic)

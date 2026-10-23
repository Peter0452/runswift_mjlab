"""Config smoke tests for Kick-on-Walk-AMP (78/95/22)."""

from __future__ import annotations

import math

import torch

from mjlab.tasks.registry import load_env_cfg, load_rl_cfg
from mjlab.tasks.velocity.mdp.amp_symmetry import (
  CRITIC_EXTRA_DIM_KICK,
  POLICY_DIM_KICK_WALKAMP,
  flip_k1_critic_obs_left_right,
  flip_k1_policy_obs_left_right,
)

TASK = "Mjlab-Kick-WalkAmp-DA-Muon-Booster-K1"
TASK_AMP = "Mjlab-Kick-WalkAmp-Amp-DA-Muon-Booster-K1"
TASK_DA = "Mjlab-Kick-WalkAmp-Amp-DA-Muon-Booster-K1"

_REWARDS = {
  "target_reached",
  "ball_approach_target",
  "agent_approach_ball",
  "ball_velocity_toward_goal",
  "ball_stagnant",
  "survival",
  "upright",
  "base_height",
  "fell_over_penalty",
  "fall_down",
  "dof_pos_limits",
  "action_rate_l2",
  "foot_slip",
  "arm_swing",
  "arm_posture",
}

_TERMINATIONS = {
  "time_out",
  "fell_over",
  "root_height",
  "target_hit",
  "target_missed",
  "double_touch",
  "nan_state",
}


def test_walkamp_reward_and_term_set():
  cfg = load_env_cfg(TASK)
  assert set(cfg.rewards.keys()) == _REWARDS
  assert len(cfg.rewards) == 15
  assert cfg.rewards["target_reached"].weight == 250.0
  assert cfg.rewards["ball_velocity_toward_goal"].weight == 1.0
  assert cfg.rewards["ball_velocity_toward_goal"].params["max_reward"] == 6.0
  assert cfg.rewards["ball_velocity_toward_goal"].params["use_decay"] is False
  assert cfg.rewards["base_height"].weight == -15.0
  # The config has used 0.5 / 0.3 since 2026-09-28 (8468d7c), when the legacy
  # walk-AMP kick runs were trained.
  assert cfg.rewards["base_height"].params["target_height"] == 0.5
  assert cfg.rewards["ball_stagnant"].weight == -0.02
  assert cfg.rewards["ball_stagnant"].params["max_ball_distance"] == 0.3
  assert "min_ball_distance" not in cfg.rewards["agent_approach_ball"].params
  assert cfg.rewards["agent_approach_ball"].params["velocity_eps"] == 0.1
  assert cfg.rewards["action_rate_l2"].weight == -0.0075
  assert cfg.rewards["arm_posture"].weight == 0.3
  assert cfg.rewards["fell_over_penalty"].weight == -100.0
  assert cfg.rewards["fall_down"].weight == -100.0
  assert cfg.only_positive_rewards is False
  assert math.isclose(cfg.episode_length_s, 8.0)
  assert set(cfg.terminations.keys()) == _TERMINATIONS
  assert cfg.terminations["target_missed"].params["contact_window_steps"] == 50
  assert cfg.terminations["fell_over"].params["limit_angle"] == 1.2217
  assert math.isclose(cfg.commands["goal"].angle_range[0], -math.pi / 2.0)
  assert math.isclose(cfg.commands["goal"].angle_range[1], math.pi / 2.0)
  reset = cfg.events["reset_walkamp"].params
  assert math.isclose(reset["spawn_half_angle"], math.pi / 2.0)
  assert reset["face_ball"] is False
  assert reset["ball_x_max"] == 1.5


def test_walkamp_obs_layout_terms():
  cfg = load_env_cfg(TASK)
  actor = list(cfg.observations["actor"].terms.keys())
  critic = list(cfg.observations["critic"].terms.keys())
  assert actor == [
    "base_ang_vel",
    "projected_gravity",
    "ball_rel_pos",
    "target_pos",
    "joint_pos",
    "joint_vel",
    "actions",
  ]
  assert "command" not in actor
  assert "base_lin_vel" not in critic
  assert critic[-2:] == ["ball_velocity", "ball_foot_contact"]
  assert cfg.observations["actor"].enable_corruption is True
  assert cfg.observations["critic"].enable_corruption is False


def test_walkamp_amp_and_da_tasks_register():
  amp = load_env_cfg(TASK_AMP)
  assert "amp" in amp.observations
  rl = load_rl_cfg(TASK_DA)
  assert rl.algorithm.symmetry_cfg is not None
  assert "Muon" in type(rl.algorithm).__name__ or "muon" in rl.experiment_name
  # No-AMP DA+Muon variant: same env obs, no amp group.
  no_amp = load_env_cfg("Mjlab-Kick-WalkAmp-DA-Muon-Booster-K1")
  assert "amp" not in no_amp.observations
  rl_no = load_rl_cfg("Mjlab-Kick-WalkAmp-DA-Muon-Booster-K1")
  assert rl_no.experiment_name == "k1_kick_walkamp_da_muon"
  assert not hasattr(rl_no, "style_reward_weight")
  assert rl_no.algorithm.symmetry_cfg is not None
  assert "Muon" in type(rl_no.algorithm).__name__ or "muon" in rl_no.experiment_name


def test_walkamp_da_flip_dims():
  """78-D actor + 95-D critic flip without error and negate lateral ball/target."""
  n = 4
  actor = torch.randn(n, POLICY_DIM_KICK_WALKAMP)
  critic = torch.randn(n, POLICY_DIM_KICK_WALKAMP + CRITIC_EXTRA_DIM_KICK)
  # Plant known lateral signs in ball_rel_pos / target_pos.
  actor[:, 7] = 1.0  # ball y
  actor[:, 10] = 2.0  # target y
  flipped = flip_k1_policy_obs_left_right(actor)
  assert torch.allclose(flipped[:, 7], -actor[:, 7])
  assert torch.allclose(flipped[:, 10], -actor[:, 10])
  critic_f = flip_k1_critic_obs_left_right(critic)
  assert critic_f.shape == critic.shape
  # Round-trip approx identity for policy part (double flip).
  twice = flip_k1_policy_obs_left_right(flipped)
  assert torch.allclose(twice, actor, atol=1e-5)


def test_walkamp_amp_obs_group_present():
  cfg = load_env_cfg(TASK_AMP)
  amp_terms = cfg.observations["amp"].terms
  assert "joint_pos" in amp_terms
  assert "base_lin_vel" in amp_terms
  assert "projected_gravity" in amp_terms


def test_walkamp_play_keeps_double_touch():
  cfg = load_env_cfg(TASK, play=True)
  assert "double_touch" in cfg.terminations
  assert "target_hit" not in cfg.terminations
  assert "target_missed" not in cfg.terminations
  reset = cfg.events["reset_walkamp"].params
  assert reset["ball_x_min_base"] == 0.3
  assert reset["ball_x_max"] == 0.3
  assert reset["momentum_time_s"] == 0.0
  assert reset["face_ball"] is True
  assert reset["spawn_half_angle"] == 0.0

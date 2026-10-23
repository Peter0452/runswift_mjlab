"""Kick-handoff walk fine-tune: mix, command, and task registration."""

from __future__ import annotations

import torch

from k1.tasks.velocity.mdp.kick_handoff import (
  DEFAULT_KICK_CKPTS,
  sample_handoff_command,
  select_handoff_ids,
)
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg

TASK = "Mjlab-Velocity-Rough-Amp-DA-Muon-Booster-K1-KickHandoff"


def test_select_handoff_ids_respects_fraction():
  ids = torch.arange(1000)
  none = select_handoff_ids(ids, 0.0)
  all_ids = select_handoff_ids(ids, 1.0)
  some = select_handoff_ids(ids, 0.35)
  assert none.numel() == 0
  assert torch.equal(all_ids, ids)
  assert 250 < int(some.numel()) < 450


def test_handoff_command_is_stand_or_within_limit():
  stand, command = sample_handoff_command(
    400, stand_prob=0.5, limit=0.5, device="cpu"
  )
  assert command.shape == (400, 3)
  assert torch.all(command.abs() <= 0.5 + 1.0e-6)
  assert torch.all(command[stand] == 0)
  moving = command[~stand]
  assert moving.numel() > 0
  assert torch.any(moving.abs() > 0)


def test_kick_handoff_task_mixes_thirty_five_percent():
  cfg = load_env_cfg(TASK)
  play = load_env_cfg(TASK, play=True)
  agent = load_rl_cfg(TASK)
  event = cfg.events["kick_handoff"]
  assert event.mode == "post_reset"
  assert event.params["fraction"] == 0.35
  assert event.params["stand_prob"] == 0.5
  assert event.params["cmd_limit"] == 0.5
  assert "reset_robot_from_motion" in cfg.events
  assert play.events["kick_handoff"].params["fraction"] == 0.0
  assert agent.max_iterations == 12000
  late = cfg.curriculum["command_vel"].params["velocity_stages"][-1]
  assert late["step"] == 8000 * 24
  assert late["lin_vel_x"] == (-2.0, 2.5)
  assert late["lin_vel_y"] == (-2.0, 2.0)
  assert late["ang_vel_z"] == (-1.8, 1.8)
  assert agent.algorithm.learning_rate == 2.0e-4
  assert agent.run_name == "kickhandoff"
  assert agent.warm_start is False
  listed = tuple(event.params["kick_checkpoints"])
  assert len(listed) == 1
  assert listed[0].endswith("2026-09-29_08-23-57/model_80000.pt")
  assert len(DEFAULT_KICK_CKPTS) == 1
  assert DEFAULT_KICK_CKPTS[0].is_file()
  checkpoint = torch.load(DEFAULT_KICK_CKPTS[0], map_location="cpu", weights_only=False)
  assert "actor_state_dict" in checkpoint

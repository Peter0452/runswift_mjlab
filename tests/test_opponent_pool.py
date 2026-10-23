"""Opponent pool bookkeeping without a simulation."""

from types import SimpleNamespace

import torch

from k1.tasks.velocity.mdp import self_play
from k1.tasks.velocity.mdp.self_play import OpponentPolicyAction


def test_full_pool_drop_after_rollout_in_inference_mode(monkeypatch):
  """Dropping a snapshot clears its envs' controller memory even when that
  memory was created during the rollout's inference mode (the runner adds
  snapshots outside it; run 2026-10-11_19-43-56 crashed at iteration 1800)."""
  monkeypatch.setattr(
    self_play,
    "frozen_policy_from_state_dict",
    lambda state, kind, name, device: SimpleNamespace(name=name),
  )
  opp = OpponentPolicyAction.__new__(OpponentPolicyAction)
  opp._env = SimpleNamespace(num_envs=4, device="cpu")
  opp.cfg = SimpleNamespace(
    latest_kind="controller", max_snapshots=1, snapshot_weight=1.0
  )
  opp.slots = [SimpleNamespace(name="latest"), SimpleNamespace(name="iter_200")]
  opp.slot_weights = [0.0, 1.0]
  opp._num_fixed = 1
  opp.slot_wins = torch.zeros(2)
  opp.slot_points = torch.zeros(2)
  opp.slot = torch.tensor([0, 1, 1, 0])
  opp.ctrl_h = torch.zeros(4, 0)
  with torch.inference_mode():
    # As _run_controller widens the memory on first use.
    opp.ctrl_h = torch.cat((opp.ctrl_h, torch.ones(4, 3)), dim=1)

  opp.add_snapshot({}, "iter_400")

  assert [p.name for p in opp.slots] == ["latest", "iter_400"]
  assert opp.slot.tolist() == [0, 0, 0, 0]
  assert opp.ctrl_h.sum(dim=1).tolist() == [3.0, 0.0, 0.0, 3.0]
  # The next rollout still writes it in place.
  with torch.inference_mode():
    opp.ctrl_h[0] = 0.0

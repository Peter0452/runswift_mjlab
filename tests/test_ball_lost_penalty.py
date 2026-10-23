"""Ball-lost penalty (self-play's replacement for search_turn)."""

from types import SimpleNamespace

import torch

from k1.tasks.kick.mdp import kick_loop


def test_lost_always_costs_and_scan_episodes_are_exempt(monkeypatch):
  cmd = SimpleNamespace(
    ball_lost=torch.tensor([False, True, True, True, True]),
    lost_dir=torch.tensor([1.0, 1.0, 1.0, -1.0, 1.0]),
    speed_limit=torch.full((5, 3), 1.0),
  )
  monkeypatch.setattr(kick_loop, "_kick_command", lambda env: cmd)
  # Tracked; lost turning toward it; lost turning away; lost still (dir -1);
  # lost but the head scans this episode.
  wz = torch.tensor([0.0, 1.0, -1.0, 0.0, 1.0])
  ang = torch.zeros(5, 3)
  ang[:, 2] = wz
  robot = SimpleNamespace(data=SimpleNamespace(root_link_ang_vel_b=ang))
  head = SimpleNamespace(scan=torch.tensor([False, False, False, False, True]))
  env = SimpleNamespace(
    scene={"robot": robot},
    action_manager=SimpleNamespace(get_term=lambda name: head),
    extras={"log": {}},
  )

  cost = kick_loop.ball_lost_penalty(env)  # type: ignore[arg-type]

  assert cost.tolist() == [0.0, 1.0, 3.0, 2.0, 0.0]
  log = env.extras["log"]
  assert abs(float(log["Metrics/ball_lost"]) - 0.8) < 1e-6
  assert abs(float(log["Metrics/ball_lost_tracking"]) - 0.75) < 1e-6

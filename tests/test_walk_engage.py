"""Approach pay that a ball carried away cannot farm (``walk_engage``)."""

from types import SimpleNamespace

import torch

from k1.tasks.velocity.mdp import self_play


def _env(robot_v, ball_v, dist=3.0, cap=1.0, since_kick=10.0, lost=False):
  n = len(robot_v)

  def body(pos, vel):
    return SimpleNamespace(
      data=SimpleNamespace(
        root_link_pos_w=torch.tensor(pos, dtype=torch.float),
        root_link_lin_vel_w=torch.tensor(vel, dtype=torch.float),
      )
    )

  # Robot at the origin, ball on +x at ``dist``: +x velocity is toward it.
  cmd = SimpleNamespace(
    robot=body([[0.0, 0.0, 0.5]] * n, [[v, 0.0, 0.0] for v in robot_v]),
    ball=body([[dist, 0.0, 0.1]] * n, [[v, 0.0, 0.0] for v in ball_v]),
    speed_limit=torch.tensor([[cap, 0.5, 1.0]] * n),
    time_since_kick=torch.full((n,), since_kick),
    ball_lost=torch.full((n,), lost),
  )
  return cmd


def _score(monkeypatch, cmd, **kw):
  monkeypatch.setattr(self_play, "_selfplay_command", lambda env: cmd)
  return self_play.walk_engage(None, **kw).tolist()  # type: ignore[arg-type]


def test_only_closing_by_own_motion_pays(monkeypatch):
  # Chase a ball rolling away as fast: 0. Gain on it: the gain. Ball still: the
  # speed. Ball rolling in: only the robot's own speed. Step back: costs.
  cmd = _env(robot_v=[0.8, 0.8, 0.8, 0.8, -0.5], ball_v=[0.8, 0.5, 0.0, -1.0, 0.0])
  got = _score(monkeypatch, cmd)
  for g, want in zip(got, [0.0, 0.3, 0.8, 0.8, -0.5], strict=True):
    assert abs(g - want) < 1e-6


def test_clipped_to_cap_and_gated(monkeypatch):
  cmd = _env(robot_v=[3.0], ball_v=[0.0], cap=2.0)
  assert abs(_score(monkeypatch, cmd)[0] - 2.0) < 1e-6  # 2 m/s cap over 1 m/s ref
  for kw in ({"dist": 0.4}, {"since_kick": 0.5}, {"lost": True}):
    cmd = _env(robot_v=[0.8], ball_v=[0.0], **kw)
    assert _score(monkeypatch, cmd) == [0.0]
  # Pays inside stage 3's 1.5 m dead zone.
  assert abs(_score(monkeypatch, _env([0.8], [0.0], dist=1.0))[0] - 0.8) < 1e-6

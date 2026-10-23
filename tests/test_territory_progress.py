"""Territory reward: ball velocity up the field, inside the field only."""

from types import SimpleNamespace

import torch

from k1.tasks.selfplay.mdp import self_play


def test_pays_progress_along_axis_clipped_and_inside_field_only(monkeypatch):
  # Axis +y; field 10 x 6 m centred at the origin.
  ball = SimpleNamespace(
    data=SimpleNamespace(
      root_link_pos_w=torch.tensor(
        [[0.0, 0.0, 0.1], [0.0, 0.0, 0.1], [0.0, 0.0, 0.1], [0.0, 5.5, 0.1]]
      ),
      root_link_lin_vel_w=torch.tensor(
        [[0.0, 1.0, 0.0], [0.0, -2.0, 0.0], [3.0, 5.0, 0.0], [0.0, 2.0, 0.0]]
      ),
    )
  )
  cmd = SimpleNamespace(
    ball=ball,
    field_axis=torch.tensor([[0.0, 1.0]]).repeat(4, 1),
    field_center=torch.zeros(4, 2),
    field_length=torch.full((4,), 10.0),
    field_width=torch.full((4,), 6.0),
  )
  monkeypatch.setattr(self_play, "_selfplay_command", lambda env: cmd)

  value = self_play.territory_progress(SimpleNamespace(), max_speed=3.0)  # type: ignore[arg-type]

  # Forward, backward (costs), clipped, and out over the goal line (unpaid).
  assert value.tolist() == [1.0, -2.0, 3.0, 0.0]

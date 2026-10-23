"""Zero-sum possession reward (``possession_change``)."""

from types import SimpleNamespace

import torch

from k1.tasks.selfplay.mdp import self_play


def _step(cmd, learner, opponent):
  """The command's update of last_touch / possession_change for one step."""
  prev = cmd.last_touch.clone()
  cmd.last_touch[:] = torch.where(
    torch.tensor(learner), 1, torch.where(torch.tensor(opponent), -1, cmd.last_touch)
  )
  cmd.possession_change[:] = ((cmd.last_touch == 1) & (prev != 1)).float() - (
    (cmd.last_touch == -1) & (prev != -1)
  ).float()
  return self_play.possession_change(None).tolist()  # type: ignore[arg-type]


def test_gains_and_losses_and_no_dribble_farming(monkeypatch):
  cmd = SimpleNamespace(
    last_touch=torch.zeros(1, dtype=torch.long), possession_change=torch.zeros(1)
  )
  monkeypatch.setattr(self_play, "_selfplay_command", lambda env: cmd)
  seq = [
    (True, False, 1.0),  # loose ball: learner takes it
    (True, False, 0.0),  # dribble touch: nothing
    (False, False, 0.0),
    (True, False, 0.0),  # still its ball
    (False, True, -1.0),  # opponent takes it
    (False, True, 0.0),
    (True, False, 1.0),  # won back
  ]
  total = 0.0
  for learner, opponent, want in seq:
    got = _step(cmd, [learner], [opponent])[0]
    assert got == want
    total += got
  assert total == 1.0  # net: who has it now


def test_update_matches_command_code():
  src = open(self_play.__file__).read()
  assert "self.possession_change[:] = (" in src
  assert "prev_touch = self.last_touch.clone()" in src

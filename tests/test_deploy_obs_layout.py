"""The deployment contract's actor layouts match the golden models' envs."""

from pathlib import Path

import pytest
import torch

from k1.deploy.obs_layout import KICK_LOOP_V1, LAYOUTS, SELFPLAY_V1

GOLDEN = Path(__file__).parent / "golden" / "policies"
# Golden model -> the layout it is deployed with.
GOLDEN_LAYOUT = {
  "gold_walk": "walk_amp",
  "kick_champion_h022": "kick_loop_v1",
  "kick_h011_teacher": "kick_loop_v1",
  "dribble_v51_11750": "dribble_v1",
  "selfplay_swa_v15v16": "selfplay_v1",
  "striker_controller_v2": "striker_controller_v2",
}


@pytest.mark.parametrize("model", sorted(GOLDEN_LAYOUT))
def test_layout_matches_golden(model: str) -> None:
  record = torch.load(GOLDEN / f"{model}.pt", weights_only=False)
  layout = LAYOUTS[GOLDEN_LAYOUT[model]]
  actor = [(term, dim[0]) for term, dim in record["layout"]["actor"]]
  assert actor == layout.terms()
  assert record["model"]["task"] == layout.task


def test_documented_slot_indices() -> None:
  # deployment.md §3: the kick loop's ball, caps, direction and range slots.
  assert KICK_LOOP_V1.size == 83
  assert KICK_LOOP_V1.slots("command") == range(72, 75)
  assert KICK_LOOP_V1.slots("speed_limit") == range(75, 78)
  assert KICK_LOOP_V1.slots("kick_direction") == range(78, 80)
  assert KICK_LOOP_V1.slots("kick_range") == range(80, 83)
  assert SELFPLAY_V1.size == 86
  assert SELFPLAY_V1.slots("opponent") == range(83, 86)

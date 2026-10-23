"""Verdict rules and the kick judge's scoring."""

import json

import pytest

from k1.eval import judges
from k1.eval.verdict import Verdict


def test_ungradable_is_never_zero() -> None:
  with pytest.raises(ValueError):
    Verdict("j", "diverged", "ck", score=0.0)
  with pytest.raises(ValueError):
    Verdict("j", "scored", "ck")
  assert Verdict("j", "train_failed", "ck").score is None


def test_promotion_needs_a_confirmed_clean_gain() -> None:
  assert not Verdict("j", "scored", "ck", score=5.0).promotable
  assert not Verdict(
    "j", "scored", "ck", score=5.0, confirmed=True, regressions=["x"]
  ).promotable
  assert Verdict("j", "scored", "ck", score=5.0, confirmed=True).promotable


def test_kick_judge_scores_the_champion_against_itself_as_zero() -> None:
  ref = json.loads(judges.KICK_REFERENCE["quick"].read_text())
  total, regressions, _ = judges.score_kick(ref, "quick")
  assert total == 0.0 and regressions == []


def test_every_judge_names_its_tool() -> None:
  stage3 = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"
  assert judges.judge_for(stage3).wrapped  # type: ignore[union-attr]
  for j in judges.JUDGES:
    assert (judges.ROOT / j.tool.split()[0]).is_file(), j.name

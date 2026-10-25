"""The approach designer (gaps -> approaches from the knowledge base) and
literature reviews started from gaps."""

import random

import pytest
import yaml

from k1 import recipes
from k1.approaches import knowledge, review
from k1.engine.designers.approach import ApproachDesigner
from k1.engine.gaps import Gap


def _champion():
  path = recipes.RECIPES / "kick" / "kick_stage3_h022.yaml"
  return {"recipe": yaml.safe_load(path.read_text()), "checkpoint": "champ.pt"}


def _gap(tags, metric="fall_pct", key="approach/behind/world/typical", size=8.0):
  return Gap(key, metric, "low", 24.6, 0.0, "target", size, "S1", tuple(tags))


def test_proposes_a_runnable_approach_for_the_biggest_gap() -> None:
  d = ApproachDesigner("kick", lambda c: [_gap(["safety", "perception"])])
  props = d.propose(_champion(), [], random.Random(0))
  assert props, "no proposal"
  p = props[0]
  assert p.designer == "approach"
  assert "fall_pct" in p.hypothesis and "lower" in p.hypothesis
  card = knowledge.cards()[p.hypothesis.split(" ")[0]]
  assert card.meta["trial"] is not None and card.meta["impact"] == "training-only"


def test_never_repeats_and_skips_what_the_champion_has() -> None:
  d = ApproachDesigner("kick", lambda c: [_gap(["safety", "perception", "power"])])
  history, changes = [], []
  for _ in range(10):
    props = d.propose(_champion(), history, random.Random(0))
    if not props:
      break
    assert props[0].change not in changes and "->" in props[0].change
    changes.append(props[0].change)
    history.append({"change": props[0].change})
  assert len(changes) >= 2


def test_rejected_and_runtime_approaches_are_never_proposed() -> None:
  d = ApproachDesigner("kick", lambda c: [_gap(knowledge.TAGS)])
  cards = knowledge.cards()
  for mv in d.moves(_champion(), random.Random(0)):
    card = mv.card
    assert card.meta["status"] not in ("rejected", "parked")
    assert card.meta["impact"] != "runtime"
  ids = {mv.card.id for mv in d.moves(_champion(), random.Random(0))}
  assert "bhuman_action_imitation" not in ids
  assert all(cards[b].meta["trial"] is None or cards[b].meta["impact"] == "runtime"
             for b in d.blocked)  # fmt: skip


def test_approved_shortlist_ranks_first(monkeypatch) -> None:
  gaps = [_gap(["safety", "perception"])]
  plain = ApproachDesigner("kick", lambda c: gaps).moves(_champion(), random.Random(0))
  last = plain[-1].card.id
  monkeypatch.setattr(knowledge, "approved_shortlist", lambda t: [{"approach": last}])
  ranked = ApproachDesigner("kick", lambda c: gaps).moves(_champion(), random.Random(0))
  assert ranked[0].card.id == last


def test_review_skeleton_and_approval(tmp_path, monkeypatch) -> None:
  monkeypatch.setattr(knowledge, "REVIEWS", tmp_path)
  monkeypatch.setattr(review, "gaps_for", lambda f, top=8: [_gap(["safety"])])
  path = review.new("Falls with the ball behind", "kick", "test")
  meta = knowledge.front_matter(path)
  assert meta["task"] == "kick" and meta["approved"] is False
  assert "fall_pct" in meta["gaps"][0]
  text = path.read_text()
  assert "Runnable by the engine" in text and "## Shortlist" in text
  with pytest.raises(ValueError):
    review.approve(path.stem)  # empty shortlist
  text = text.replace("shortlist: []", "shortlist:\n- approach: ball_behind_starts\n"
                      "  gap: fall_pct\n  hypothesis: fewer falls")  # fmt: skip
  path.write_text(text)
  review.approve(path.stem)
  assert knowledge.approved_shortlist("kick")[0]["approach"] == "ball_behind_starts"
  assert knowledge.check() == []


def test_a_trial_on_a_runtime_card_is_an_error(monkeypatch) -> None:
  real = knowledge.cards()
  card = real["gait_clock"]
  bad = knowledge.Card({**card.meta, "trial": {"genes": {"x": 1}}}, card.path)
  monkeypatch.setattr(knowledge, "cards", lambda: {**real, "gait_clock": bad})
  assert any("runtime approach" in p for p in knowledge.check())


def test_tunes_an_approach_that_is_on_in_the_knowledge_direction() -> None:
  power = Gap("close_any/camera/typical", "long_3d", "high", 4.0, 4.31, "bhuman",
              1.2, "P3", ("power",))  # fmt: skip
  d = ApproachDesigner("kick", lambda c: [power])
  tunes = [mv for mv in d.moves(_champion(), random.Random(0)) if mv.kind == "tune"]
  edits = {p: v for mv in tunes for p, v in mv.edits.items()}
  # long_kick_power is 4000 in the champion; its step is "up" (stronger reward)
  assert edits["genes.w.long_kick_power"] == 5000.0
  assert all(mv.card.id == "task_reward_shaping" for mv in tunes)


def test_tries_spread_over_approaches() -> None:
  d = ApproachDesigner("kick", lambda c: [_gap(["safety", "perception"])])
  first = d.propose(_champion(), [], random.Random(0))[0]
  card = first.change.split(" ")[1].rstrip(":")
  second = d.propose(_champion(), [{"change": first.change}], random.Random(0))[0]
  assert second.change.split(" ")[1].rstrip(":") != card


def test_combine_bundles_moves_on_different_approaches() -> None:
  gaps = [_gap(["safety", "perception", "power"])]
  one = ApproachDesigner("kick", lambda c: gaps).propose(
    _champion(), [], random.Random(0)
  )
  two = ApproachDesigner("kick", lambda c: gaps, combine=2).propose(
    _champion(), [], random.Random(0)
  )
  assert " + " not in one[0].change
  parts = two[0].change.split(" + ")
  assert len(parts) == 2 and parts[0].split(" ")[1] != parts[1].split(" ")[1]
  assert " and " in two[0].hypothesis

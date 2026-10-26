"""The LLM designer's interface: proposal schema and check, the inbox the
engine reads, and the design context."""

import random

import pytest
import yaml
from tests.test_k1_engine import FakeJudge, FakeTrainer

from k1 import recipes
from k1.engine import design, outer, state
from k1.engine.designers import GeneDesigner
from k1.engine.designers.llm import InboxDesigner


def _champion():
  path = recipes.RECIPES / "kick" / "kick_stage3_h022.yaml"
  return {"recipe": yaml.safe_load(path.read_text()), "checkpoint": "champ.pt"}


GOOD = {
  "designer": "test",
  "task": "kick",
  "kind": "add",
  "approaches": ["ball_behind_starts"],
  "edits": {"genes.s.far_spawn_prob": 0.3},
  "gap": "fall_pct in approach/behind/world/typical",
  "hypothesis": "fewer behind falls",
  "expect": [
    {
      "metric": "fall_pct",
      "situation": "approach/behind/world/typical",
      "direction": "lower",
      "by": 9.0,
      "p": 0.5,
    }
  ],  # fmt: skip
  "why": "biggest gap",
}


@pytest.fixture
def dirs(tmp_path, monkeypatch):
  for name in ("INBOX", "USED", "REJECTED", "BUILD"):
    monkeypatch.setattr(design, name, tmp_path / name.lower())
  design.INBOX.mkdir()
  return tmp_path


def _write(name, p):
  (design.INBOX / f"{name}.yaml").write_text(yaml.safe_dump(p))


def test_a_good_proposal_checks_and_becomes_a_recipe() -> None:
  assert design.check(GOOD, _champion(), []) == []
  prop = design.to_proposal(GOOD, _champion())
  assert prop.recipe["genes"]["s.far_spawn_prob"] == 0.3
  assert prop.designer == "llm:test" and prop.hypothesis == "fewer behind falls"
  assert prop.change == "add ball_behind_starts: genes.s.far_spawn_prob: 0.2 -> 0.3"


@pytest.mark.parametrize(
  ("change", "problem"),
  [
    ({"approaches": ["bhuman_action_imitation"]}, "rejected"),
    ({"approaches": ["gait_clock"]}, "parked"),
    ({"approaches": ["caps", "decap"]}, "one change per run"),
    ({"edits": {"methods.caps.temporal": 3.0}}, "outside the tune range"),
    ({"edits": {"observations.actor": 1}}, "methods.*, genes.* or rewards.*"),
    ({"edits": {"methods.caps.nope": 1.0}}, "no parameter nope"),
    ({"edits": {"genes.s.spawn_any_prob": 0.3}}, "don't change"),
    ({"touches": "runtime"}, "runtime changes"),
    ({"approaches": ["no_such_card"]}, "unknown approach"),
    ({"expect": [{**GOOD["expect"][0], "by": 2.0}]}, "not detectable"),
    ({"expect": [{**GOOD["expect"][0], "p": 0.1}]}, "not worth a run"),
    ({"expect": {"metric": "fall_pct", "direction": "lower"}}, "needs"),
  ],
)
def test_check_catches(change, problem) -> None:
  problems = design.check({**GOOD, **change}, _champion(), [])
  assert any(problem in p for p in problems), problems


def test_repeats_and_reasons() -> None:
  champ = _champion()
  history = [{"change": design.change_text(GOOD, champ["recipe"])}]
  assert any("already tried" in p for p in design.check(GOOD, champ, history))
  wide = {**GOOD, "approaches": ["caps"], "edits": {"methods.caps.temporal": 3.0},
          "out_of_range_reason": "test"}  # fmt: skip
  assert design.check(wide, champ, []) == []


def test_expected_gain_follows_the_fitness_formula() -> None:
  # 9 points / tol 3 = 3 tol, safety weight 2, both caps (where the gap is), p 0.5
  est = design.estimate(GOOD)
  assert est.ok and est.gain == pytest.approx(0.5 * 3 * 2 * 2)
  side = {"metric": "goals_per_ep", "situation": "full_loop/camera/typical",
          "direction": "higher", "by": 0.12, "p": 0.5, "caps": ["high"]}  # fmt: skip
  both = design.estimate({**GOOD, "expect": [*GOOD["expect"], side]})
  assert both.gain == pytest.approx(6 + 0.5 * 2 * 3 * 1)


def test_inbox_designer_picks_the_highest_expected_gain(dirs) -> None:
  small = {**GOOD, "expect": [{**GOOD["expect"][0], "p": 0.4}]}
  _write("a_small", small)
  _write("b_big", {**GOOD, "edits": {"genes.s.far_spawn_prob": 0.4}})
  props = InboxDesigner().propose(_champion(), [], random.Random(0))
  assert props[0].expected_gain == pytest.approx(6.0)
  assert (design.USED / "b_big.yaml").is_file()
  assert (design.INBOX / "a_small.yaml").is_file()  # waits for a later step


def test_inbox_designer_asks_the_llm_when_empty(dirs) -> None:
  calls = []

  def ask() -> str:
    calls.append(1)
    _write("from_llm", GOOD)
    return "wrote 1"

  d = InboxDesigner(ask=ask, ask_every=3600)
  assert d.propose(_champion(), [], random.Random(0))[0].designer == "llm:test"
  assert d.propose(_champion(), [], random.Random(0)) == [] and d.empty
  assert len(calls) == 1  # rate-limited: not asked again within ask_every
  assert any("asked the LLM designer: wrote 1" in m for m in d.log)


def test_inbox_designer_files_proposals(dirs) -> None:
  _write("a_bad", {**GOOD, "approaches": ["gait_clock"]})
  _write("b_new", {**GOOD, "kind": "new", "approaches": ["privileged_teacher_dagger"],
                   "edits": {}})  # fmt: skip
  _write("c_good", GOOD)
  d = InboxDesigner()
  props = d.propose(_champion(), [], random.Random(0))
  assert len(props) == 1 and props[0].designer == "llm:test"
  assert (design.REJECTED / "a_bad.yaml").is_file()
  assert "parked" in (design.REJECTED / "a_bad.why.txt").read_text()
  assert (design.BUILD / "b_new.yaml").is_file()
  assert (design.USED / "c_good.yaml").is_file()
  assert d.propose(_champion(), [], random.Random(0)) == [] and d.empty


def test_engine_asks_the_llm_inbox_first(dirs, tmp_path) -> None:
  _write("good", GOOD)
  st = state.State(champion=_champion())
  designers = [GeneDesigner({"w.kick_direction": (100.0, 2000.0)}), InboxDesigner()]
  outer.step(
    st, outer.Config(max_in_flight=2), designers, FakeTrainer(), FakeJudge(),
    random.Random(0), tmp_path / "loop", check=lambda p: [],
  )  # fmt: skip
  assert [c["designer"] for c in st.in_flight] == ["llm", "genes"]
  assert st.in_flight[0]["hypothesis"] == "fewer behind falls"


def test_context_has_every_section() -> None:
  text = design.context(_champion(), [], "kick")
  for section in ("## Task request", "## Champion", "## Measured gaps",
                  "## Engine history", "## Approaches", "## Baseline suggestions",
                  "## Rules", "## Proposal schema"):  # fmt: skip
    assert section in text, section
  assert "fall_pct" in text and "ball_behind_starts" in text


def test_doses_parent_ceiling_and_rs_kick_forecasts(tmp_path) -> None:
  # Doses: other strengths of the one edit, as sibling recipes.
  p = {**GOOD, "doses": {"genes.s.far_spawn_prob": [0.4]}}
  assert design.check(p, _champion(), []) == []
  prop = design.to_proposal(p, _champion())
  assert [r["genes"]["s.far_spawn_prob"] for _, r in prop.doses] == [0.4]
  bad = {**GOOD, "doses": {"genes.s.cap_low_prob": [0.4]}}
  assert any("doses" in m for m in design.check(bad, _champion(), []))
  # Parent: continue from an earlier child's recipe and checkpoint.
  rec = tmp_path / "e0003.yaml"
  child = {**_champion()["recipe"], "name": "e0003"}
  child["genes"] = {**child["genes"], "s.far_spawn_prob": 0.25}
  rec.write_text(yaml.safe_dump(child))
  hist = [{"id": "e0003", "change": "x", "recipe": str(rec),
           "verdict": {"checkpoint": "ck3.pt", "score": 10.0, "regressions": []}}]  # fmt: skip
  q = {**GOOD, "parent": "e0003"}
  assert design.check(q, _champion(), hist) == []
  prop = design.to_proposal(q, _champion(), history=hist)
  assert prop.init == "ck3.pt" and prop.parent == "e0003"
  assert prop.change.endswith("0.25 -> 0.3")
  assert design.check({**GOOD, "parent": "e0099"}, _champion(), hist)
  # A gap at a ceiling is closed to training-only proposals.
  problems = design.check(GOOD, _champion(), [], ceilings=[GOOD["gap"]])
  assert any("ceiling" in m for m in problems)
  # rs_kick metrics are valid forecasts.
  rs = {**GOOD, "expect": [{"metric": "power_small", "situation": "rs_kick/lab",
                            "direction": "higher", "by": 0.3, "p": 0.6}]}  # fmt: skip
  est = design.estimate(rs, [])
  assert not est.problems or "not worth" in est.problems[0]
  assert est.gain > 0


def test_proposal_targets_are_its_forecast_situations() -> None:
  p = {**GOOD, "expect": [*GOOD["expect"],
       {"metric": "power_small", "situation": "rs_kick/lab", "by": 0.3, "p": 0.5}]}  # fmt: skip
  assert design.to_proposal(p, _champion()).targets == ["approach/behind/world/typical"]

"""The engine (evolution loop) logic with a fake trainer and judge (no GPU)."""

import random
from pathlib import Path

import pytest
import yaml

from k1 import recipes
from k1.engine import inner, outer, state
from k1.engine.designers import GeneDesigner, MethodDesigner
from k1.eval.verdict import Verdict


class FakeTrainer:
  def __init__(self, fail: set[str] = frozenset()) -> None:
    self.started, self.fail = [], fail

  def start(self, recipe_path, run_id, iterations):
    self.started.append(run_id)
    return {"id": run_id}

  def poll(self, handle):
    if handle["id"] in self.fail:
      return ("failed", "diverged at 120")
    return ("done", f"ck_{handle['id']}.pt")


class FakeJudge:
  """Scores by the gene value the child's recipe set: higher kick_vel wins."""

  def __init__(self, gains: bool = True) -> None:
    self.gains = gains

  def _score(self, ck):
    return 5.0 if self.gains and ck.endswith("e0001.pt") else -3.0

  def screen(self, task, ck, name):
    return Verdict("fake", "scored", ck, score=self._score(ck))

  def confirm(self, task, ck, name):
    s = self._score(ck)
    return Verdict("fake", "scored", ck, score=s, confirmed=s > 0)


def _champion():
  path = recipes.RECIPES / "kick" / "kick_stage3_h022.yaml"
  return {"recipe": yaml.safe_load(path.read_text()), "checkpoint": "champ.pt"}


def _designers():
  return [
    GeneDesigner({"w.kick_direction": (100.0, 2000.0)}),
    MethodDesigner({"decap": False}),
  ]


def test_starts_children_and_promotes_a_confirmed_gain(tmp_path) -> None:
  st = state.State(champion=_champion())
  cfg = outer.Config(max_in_flight=2)
  trainer, judge, rng = FakeTrainer(), FakeJudge(), random.Random(0)
  log = outer.step(
    st, cfg, _designers(), trainer, judge, rng, tmp_path, check=lambda p: []
  )
  assert len(st.in_flight) == 2 and len(trainer.started) == 2, log
  first = yaml.safe_load((tmp_path / "recipes" / "e0001.yaml").read_text())
  assert first["init"] == "champ.pt" and first["control"] == "kick_stage3_h022"
  log = outer.step(
    st, cfg, _designers(), trainer, judge, rng, tmp_path, check=lambda p: []
  )
  assert st.champion["checkpoint"] == "ck_e0001.pt", log
  assert [h["promoted"] for h in st.history] == [True, False]


def test_children_carry_a_hypothesis(tmp_path) -> None:
  st = state.State(champion=_champion())
  rng = random.Random(0)
  outer.step(
    st, outer.Config(), _designers(), FakeTrainer(), FakeJudge(), rng, tmp_path,
    check=lambda p: [],
  )  # fmt: skip
  child = st.in_flight[0]
  assert "raises the judge's score" in child["hypothesis"]
  recipe = yaml.safe_load(Path(child["recipe_path"]).read_text())
  assert recipe["hypothesis"] == child["hypothesis"]


def test_escalates_after_non_improving_verdicts(tmp_path) -> None:
  st = state.State(champion=_champion())
  cfg = outer.Config(max_in_flight=1, escalate_after=2)
  designers = [
    GeneDesigner({"w.kick_direction": (100.0, 2000.0), "w.kick_vel": (100.0, 2000.0)})
  ]
  trainer, judge, rng = FakeTrainer(), FakeJudge(gains=False), random.Random(1)
  for _ in range(3):
    log = outer.step(
      st, cfg, designers, trainer, judge, rng, tmp_path, check=lambda p: []
    )
  assert any(line.startswith("escalated") for line in log)
  packets = list((tmp_path / "packets").glob("packet_*.md"))
  assert packets and "decision needed" in packets[0].read_text()
  n = len(trainer.started)
  outer.step(st, cfg, designers, trainer, judge, rng, tmp_path, check=lambda p: [])
  assert len(trainer.started) == n  # stopped proposing


def test_never_repeats_a_change(tmp_path) -> None:
  st = state.State(champion=_champion())
  cfg = outer.Config(max_in_flight=1, escalate_after=99)
  designers = [GeneDesigner({"w.kick_direction": (100.0, 2000.0)})]
  trainer = FakeTrainer(fail={f"e{i:04d}" for i in range(1, 10)})
  for _ in range(4):
    outer.step(
      st,
      cfg,
      designers,
      trainer,
      FakeJudge(),
      random.Random(2),
      tmp_path,
      check=lambda p: [],
    )
  changes = [h["change"] for h in st.history]
  assert len(changes) == len(set(changes)) and all(
    h["verdict"]["score"] is None for h in st.history
  )


def test_failed_recipe_check_is_recorded_not_trained(tmp_path) -> None:
  st = state.State(champion=_champion())
  trainer = FakeTrainer()
  outer.step(st, outer.Config(max_in_flight=1), _designers()[:1], trainer, FakeJudge(),
             random.Random(0), tmp_path, check=lambda p: ["method caps is on but not declared"])  # fmt: skip
  assert trainer.started == []
  assert st.history[0]["verdict"]["status"] == "smoke_failed"


def test_state_roundtrip_and_single_writer(tmp_path) -> None:
  path = tmp_path / "state.json"
  st = state.State(champion=_champion())
  st.next_id()
  state.save(st, path)
  assert state.load(path).counter == 1
  with state.single_writer(path):
    with pytest.raises(RuntimeError):
      with state.single_writer(path):
        pass


def test_pbt_copies_strong_into_weak_within_ranges() -> None:
  pop = [
    inner.Member(f"m{i}", {"lr": 5e-5 * (i + 1)}, f"ck{i}", score=float(i))
    for i in range(8)
  ]
  ranges = {"lr": (5e-5, 6e-4)}
  changes = inner.step(pop, ranges, random.Random(0))
  assert {c["member"] for c in changes} == {"m0", "m1"}
  assert pop[0].checkpoint in {"ck6", "ck7"} and pop[0].score is None
  assert all(ranges["lr"][0] <= m.params["lr"] <= ranges["lr"][1] for m in pop)


def test_real_trainer_reads_a_finished_child(tmp_path) -> None:
  from k1.engine.real import RsTrainer

  run = tmp_path / "run"
  run.mkdir()
  for it in (18050, 18500, 18100):
    (run / f"model_{it}.pt").write_bytes(b"")
  log = tmp_path / "e0001.log"
  log.write_text(f"[k1] run.json -> {run / 'run.json'}\nLearning iteration 18500\n")
  finished = {"pid": 2**22 + 12345, "log": str(log)}  # no such process
  assert RsTrainer().poll(finished) == ("done", str(run / "model_18500.pt"))
  log.write_text("Traceback (most recent call last):\n  boom\n")
  status = RsTrainer().poll(finished)
  assert status is not None and status[0] == "failed"

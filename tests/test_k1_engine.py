"""The engine (evolution loop) logic with a fake trainer and judge (no GPU)."""

import random
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml

from k1 import recipes
from k1.engine import inner, outer, state
from k1.engine.designers import GeneDesigner, MethodDesigner, Proposal
from k1.eval.verdict import Verdict


class FakeTrainer:
  """Finishes each child on the first poll; ``slow`` ones run until killed and
  report progress 0.35, 0.6, 0.85, ... per poll."""

  def __init__(
    self, fail: frozenset[str] = frozenset(), slow: frozenset[str] = frozenset()
  ):
    self.started, self.fail, self.slow, self.killed = [], fail, slow, []
    self.polls: dict[str, int] = {}

  def start(self, recipe_path, run_id, iterations):
    self.started.append(run_id)
    return {"id": run_id}

  def poll(self, handle):
    i = handle["id"]
    if i in self.killed:
      return ("failed", "killed")
    if i in self.slow:
      self.polls[i] = self.polls.get(i, 0) + 1
      return None
    if i in self.fail:
      return ("failed", "diverged at 120")
    return ("done", f"ck_{i}.pt")

  def progress(self, handle):
    n = self.polls.get(handle["id"], 0)
    return (0.1 + 0.25 * n, f"ck_{handle['id']}_{n}.pt")

  def kill(self, handle):
    self.killed.append(handle["id"])


class FakeJudge:
  """Every stage finishes on the first poll. Scores e0001 +15, others -3
  (``gains=False``: all -3); probes return ``probe_margin``."""

  def __init__(self, gains=True, smoke_problems=(), probe_margin=(0.0, -0.01, 0.01)):
    self.gains, self.smoke_problems = gains, list(smoke_problems)
    self.probe_margin = list(probe_margin)
    self.started: list[tuple[str, str]] = []

  def _score(self, ck):
    return 15.0 if self.gains and "e0001" in ck else -3.0

  def start(self, stage, spec):
    self.started.append((stage, spec["name"]))
    return {"stage": stage, "spec": spec}

  def poll(self, handle):
    stage, spec = handle["stage"], handle["spec"]
    ck = spec.get("checkpoint", "")
    out = {"stage": stage, "ok": True, "hours": 0.1}
    if stage == "smoke":
      out["problems"] = self.smoke_problems
    elif stage == "probe":
      out["margin"] = self.probe_margin
    elif stage in ("screen", "confirm"):
      s = self._score(ck)
      out["verdict"] = Verdict("fake", "scored", ck, score=s,
                               confirmed=stage == "confirm" and s > 0).to_dict()  # fmt: skip
    elif stage == "reverify":
      out["verdict"] = Verdict("fake", "scored", ck, score=1.0).to_dict()
      out["refs"] = {"bench": {"gate_1": f"{ck}.gate.json"}, "rs": {}}
    elif stage == "clip":
      out.update(file=f"{ck}.mp4", checks={"stays_up": True})
    return out


def _run(st, cfg, designers, trainer, judge, tmp_path, n, seed=0):
  log = []
  for _ in range(n):
    log += outer.step(st, cfg, designers, trainer, judge, random.Random(seed),
                      tmp_path, check=lambda p: [])  # fmt: skip
  return log


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
  trainer, judge = FakeTrainer(), FakeJudge()
  log = _run(st, cfg, _designers(), trainer, judge, tmp_path, 1)
  assert [c["stage"] for c in st.in_flight] == ["smoke", "smoke"], log
  first = yaml.safe_load((tmp_path / "recipes" / "e0001.yaml").read_text())
  assert first["init"] == "champ.pt" and first["control"] == "kick_stage3_h022"
  # smoke -> train -> done -> screen -> confirm -> promoted
  log += _run(st, cfg, _designers(), trainer, judge, tmp_path, 5)
  assert st.champion["checkpoint"] == "ck_e0001.pt", log
  promoted = {h["id"]: h["promoted"] for h in st.history}
  assert promoted["e0001"] and not promoted["e0002"]
  # the new champion's references are re-made, and a clip recorded
  log += _run(st, cfg, _designers(), trainer, judge, tmp_path, 1)
  assert st.champion["refs"]["bench"]["gate_1"] == "ck_e0001.pt.gate.json", log
  assert not st.champion["refs_pending"]
  assert next(h for h in st.history if h["id"] == "e0001")["clip"]["file"]


def test_children_carry_a_hypothesis(tmp_path) -> None:
  st = state.State(champion=_champion())
  _run(st, outer.Config(), _designers(), FakeTrainer(), FakeJudge(), tmp_path, 1)
  child = st.in_flight[0]
  assert "raises the judge's score" in child["hypothesis"]
  recipe = yaml.safe_load(Path(child["recipe_path"]).read_text())
  assert recipe["hypothesis"] == child["hypothesis"]


def test_smoke_failure_is_recorded_not_trained(tmp_path) -> None:
  st = state.State(champion=_champion())
  trainer = FakeTrainer()
  judge = FakeJudge(smoke_problems=["edited reward terms not logged: ['x']"])
  _run(st, outer.Config(max_in_flight=1), _designers()[:1], trainer, judge, tmp_path, 2)
  assert trainer.started == []
  assert st.history[0]["verdict"]["status"] == "smoke_failed"


def test_probes_stop_a_child_that_falls_behind(tmp_path) -> None:
  st = state.State(champion=_champion())
  cfg = outer.Config(max_in_flight=1, smoke=False, escalate_after=99)
  trainer = FakeTrainer(slow=frozenset({"e0001"}))
  judge = FakeJudge(probe_margin=(-0.03, -0.05, -0.01))
  log = _run(st, cfg, _designers()[:1], trainer, judge, tmp_path, 8)
  assert trainer.killed == ["e0001"], log
  h = st.history[0]
  assert h["verdict"]["status"] == "stopped_early" and len(h["probes"]) == 2


def test_probes_keep_a_child_that_holds_up(tmp_path) -> None:
  st = state.State(champion=_champion())
  cfg = outer.Config(max_in_flight=1, smoke=False)
  trainer = FakeTrainer(slow=frozenset({"e0001"}))
  _run(st, cfg, _designers()[:1], trainer, FakeJudge(), tmp_path, 10)
  assert trainer.killed == [] and len(st.in_flight[0]["probes"]) == 3


def test_escalates_after_non_improving_verdicts(tmp_path) -> None:
  st = state.State(champion=_champion())
  cfg = outer.Config(max_in_flight=1, escalate_after=2, smoke=False)
  designers = [
    GeneDesigner({"w.kick_direction": (100.0, 2000.0), "w.kick_vel": (100.0, 2000.0)})
  ]
  trainer, judge = FakeTrainer(), FakeJudge(gains=False)
  log = _run(st, cfg, designers, trainer, judge, tmp_path, 10, seed=1)
  assert any(line.startswith("escalated") for line in log)
  packets = list((tmp_path / "packets").glob("packet_*.md"))
  assert packets and "decision needed" in packets[0].read_text()
  n = len(trainer.started)
  _run(st, cfg, designers, trainer, judge, tmp_path, 1, seed=1)
  assert len(trainer.started) == n  # stopped proposing


def test_never_repeats_a_change(tmp_path) -> None:
  st = state.State(champion=_champion())
  cfg = outer.Config(max_in_flight=1, escalate_after=99, smoke=False)
  designers = [GeneDesigner({"w.kick_direction": (100.0, 2000.0)})]
  trainer = FakeTrainer(fail=frozenset(f"e{i:04d}" for i in range(1, 10)))
  _run(st, cfg, designers, trainer, FakeJudge(), tmp_path, 4, seed=2)
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


class ListDesigner:
  name = "list"

  def __init__(self, proposals):
    self.proposals = list(proposals)

  def propose(self, champion, history, rng):
    return [self.proposals.pop(0)] if self.proposals else []


def _proposal(gene_value, gap="g1", doses=(), **kw):
  recipe = dict(_champion()["recipe"])
  recipe["genes"] = {**recipe.get("genes", {}), "w.kick_direction": gene_value}
  return Proposal(recipe, f"w.kick_direction -> {gene_value}", "why", "list", "h",
                  gap=gap, doses=list(doses), **kw)  # fmt: skip


def test_doses_run_as_siblings_of_one_change(tmp_path) -> None:
  st = state.State(champion=_champion())
  cfg = outer.Config(max_in_flight=2, smoke=False, escalate_after=99)
  doses = [(f"w.kick_direction -> {v}", {**_champion()["recipe"], "dose": v})
           for v in (700, 1100)]  # fmt: skip
  designer = ListDesigner([_proposal(900, doses=doses)])
  trainer = FakeTrainer()
  _run(st, cfg, [designer], trainer, FakeJudge(gains=False), tmp_path, 6)
  fams = {h["family"] for h in st.history}
  assert len(trainer.started) == 3 and fams == {"e0001"}
  third = yaml.safe_load((tmp_path / "recipes" / "e0003.yaml").read_text())
  assert third["dose"] == 1100 and third["change"] == "w.kick_direction -> 1100"


def test_child_can_continue_from_a_parent(tmp_path) -> None:
  st = state.State(champion=_champion())
  p = _proposal(950, parent="e0007", init="ck_e0007.pt")
  _run(st, outer.Config(max_in_flight=1), [ListDesigner([p])], FakeTrainer(),
       FakeJudge(), tmp_path, 1)  # fmt: skip
  recipe = yaml.safe_load((tmp_path / "recipes" / "e0001.yaml").read_text())
  assert recipe["init"] == "ck_e0007.pt" and recipe["control"] == "e0007"


def test_a_gap_that_keeps_failing_goes_to_the_user(tmp_path) -> None:
  st = state.State(champion=_champion())
  cfg = outer.Config(max_in_flight=1, smoke=False, ceiling_after=2, escalate_after=99)
  designer = ListDesigner([_proposal(v) for v in (300, 500, 700, 900)])
  trainer = FakeTrainer()
  log = _run(st, cfg, [designer], trainer, FakeJudge(gains=False), tmp_path, 8)
  assert st.ceilings == ["g1"], log
  assert list((tmp_path / "packets").glob("ceiling_*.md"))
  assert len(trainer.started) == 2  # the rest were skipped: gap at a ceiling


def test_gpu_budget_stops_new_children(tmp_path) -> None:
  st = state.State(champion=_champion(), gpu_hours=5.0)
  trainer = FakeTrainer()
  log = _run(st, outer.Config(gpu_hours=4.0), _designers(), trainer, FakeJudge(),
             tmp_path, 1)  # fmt: skip
  assert trainer.started == [] and not st.in_flight
  assert any(m.startswith("budget:") for m in log)


def test_worth_calibration_and_unblock_credit() -> None:
  from k1.engine import worth

  hist = [{"expected_gain": 10.0, "verdict": {"status": "scored", "score": s}}
          for s in (2.0, -5.0, 1.0)]  # fmt: skip
  assert worth.calibration(hist[:2]) == 1.0  # not enough history yet
  assert worth.calibration(hist) == 0.25  # measured 3 of forecast 30, floored
  parent = {
    "verdict": {
      "score": 40.0,
      "regressions": [
        "full_loop/camera/typical:short_stop_m:high",
        "near_grid/camera/typical:fall_pct:low",
      ],
    }
  }
  e = {"situation": "full_loop/camera/typical", "metric": "short_stop_m"}
  assert worth.unblock_credit(e, parent) == 20.0
  assert worth.unblock_credit({**e, "metric": "goals_per_ep"}, parent) == 0.0


def test_scorecard_combines_benchmark_and_rs_kick() -> None:
  from k1.eval import rs_judge, scorecard

  bench = Verdict("kick_bench_v2", "scored", "ck", score=-5.0, confirmed=False)
  rs = rs_judge.RsVerdict("ck", margins={"deployed_s0": [0.02, 0.005, 0.035],
                                         "deployed_s1": [0.03, 0.01, 0.05],
                                         "lab_s0": [0.0, -0.01, 0.01]})  # fmt: skip
  v = scorecard.combine(bench, rs, confirm=True)
  assert v.score == 20.0 and v.confirmed and not v.regressions  # rs gain carries it
  rs.margins["lab_s1"] = [-0.03, -0.05, -0.01]
  v = scorecard.combine(bench, rs, confirm=True)
  assert v.regressions == ["rs_kick:lab_s1:-0.030"] and not v.promotable


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
  # a lock left by a dead loop is taken over
  path.with_suffix(".lock").write_text(str(2**22 + 12345))
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


def test_a_finished_child_process_is_not_alive() -> None:
  from k1.engine.real import _alive

  proc = subprocess.Popen([sys.executable, "-c", "pass"])
  deadline = time.time() + 10
  while _alive(proc.pid) and time.time() < deadline:
    time.sleep(0.05)
  assert not _alive(proc.pid)  # exited: reaped, not mistaken for running

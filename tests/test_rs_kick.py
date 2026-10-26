"""Kick benchmark (runswift spec v2): trials, score, metrics, kick rule."""

import importlib.util
import math

import numpy as np
import torch

from k1.eval import rs_kick


def test_trials_cover_the_spec() -> None:
  trials = rs_kick.make_trials(25, 0)
  assert len(trials) == 200 and trials == rs_kick.make_trials(25, 0)
  assert sum(t["strong"] for t in trials) == 100
  for t in trials:
    assert 0.35 <= t["dist"] <= 1.0 and 0.5 <= t["range"] <= 20.0
    lo, hi = rs_kick.SIDES[t["side"]]
    assert lo <= t["bearing_deg"] <= hi
    d0, d1 = rs_kick.SECTORS[t["sector"]]
    assert d0 <= t["direction_deg"] <= d1
    assert 0.08 <= t["radius"] <= 0.12 and 0.28 <= t["mass"] <= 0.32


def test_bhuman_benchmark_uses_the_same_trials() -> None:
  spec = importlib.util.spec_from_file_location(
    "bh",
    rs_kick.__file__.replace(
      "src/k1/eval/rs_kick.py", "scripts/tools/bench_bhuman_kick_v2.py"
    ),
  )
  assert spec and spec.loader
  bh = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(bh)
  assert bh.make_trials is rs_kick.make_trials


def test_score_formula() -> None:
  assert rs_kick.score(1.0, 0.0, 10.0, 20.0) == 1.0
  # time 4.6 s halves the time term; 15 deg halves accuracy; half the speed.
  need = math.sqrt(2 * rs_kick.DECEL * 3.0)
  assert math.isclose(rs_kick.score(4.6, 15.0, need / 2, 3.0), 0.25 + 0.15 + 0.1)


def test_power_follows_the_kick_class() -> None:
  assert [rs_kick.kick_class(r) for r in (0.5, 3.9, 4.0, 7.9, 8.0, 20.0)] == [
    "small", "small", "medium", "medium", "strong", "strong"
  ]  # fmt: skip
  # Strong: harder is better up to the long-kick reference, never penalised.
  assert rs_kick.power_score(3.75, 20.0) == 0.5
  assert rs_kick.power_score(9.0, 8.0) == 1.0
  # Small / medium: the speed that rolls the ball to the target; overshoot
  # costs as much as falling short.
  for r in (2.0, 6.0):
    need = rs_kick.need_speed(r)
    assert rs_kick.power_score(need, r) == 1.0
    assert math.isclose(rs_kick.power_score(1.5 * need, r), 0.5)
    assert math.isclose(rs_kick.power_score(0.5 * need, r), 0.5)
    assert rs_kick.power_score(2.5 * need, r) == 0.0
  assert rs_kick.need_speed(0.05) == rs_kick.MIN_NEED


def test_power_classes_match_the_training_design() -> None:
  from k1.tasks.kick.mdp import kick_loop

  assert rs_kick.RANGE_EDGES == kick_loop.RANGE_EDGES
  assert rs_kick.DECEL == kick_loop.BALL_ROLL_DECEL
  assert rs_kick.STRONG_REF == kick_loop.LONG_KICK_VEL_REF


def test_rescore_reads_csv_rows() -> None:
  row = {"fell": "False", "kicked": "True", "time": "1.0", "dir_err": "0.0",
         "peak_speed": "7.5", "range": "20.0"}  # fmt: skip
  assert rs_kick.rescore(row) == 1.0
  assert rs_kick.rescore(row | {"fell": "True"}) == 0.0
  assert rs_kick.rescore(row | {"kicked": "False", "time": "nan"}) == 0.0


def test_trial_row_on_a_straight_kick() -> None:
  trial = {"range": 5.0, "sector": "forward", "side": "left", "strong": False}
  dt, steps = 0.02, 400
  speed = np.zeros(steps)
  speed[100:200] = np.linspace(4.0, 0.0, 100)
  x = np.concatenate([np.zeros(100), np.cumsum(speed[100:200]) * dt, np.full(200, 0.0)])
  x[200:] = x[199]
  pos = np.stack([x, np.zeros(steps)], -1)
  row = rs_kick.trial_row(trial, 100, False, steps, pos, speed, np.zeros(2), 0.0, dt)
  assert row["kicked"] and row["dir_err"] < 1e-6 and math.isclose(row["time"], 101 * dt)
  assert row["distance"] > 3.0 and 0.9 < row["score"] <= 1.0
  fell = rs_kick.trial_row(trial, 100, True, steps, pos, speed, np.zeros(2), 0.0, dt)
  assert fell["score"] == 0.0


def test_kick_rule_needs_a_foot_at_the_ball() -> None:
  rule = rs_kick.KickRule(2, "cpu")
  q = torch.tensor([1.0, 0.0, 0.0, 0.0]).expand(2, 2, 4)
  feet = torch.tensor([[[0.0, 0.1, 0.04], [0.0, -0.1, 0.04]]]).repeat(2, 1, 1)
  # env 0: ball just ahead of the left toe; env 1: ball 1 m away.
  ball = torch.tensor([[0.2, 0.1, 0.1], [1.2, 0.1, 0.1]])
  r = torch.tensor([0.1, 0.1])
  still = torch.zeros(2, 3)
  for _ in range(12):  # ball at rest long enough
    assert not rule.update(feet, q, ball, still, r, 0.02).any()
    rule.remember_ball_velocity(still)
  moving = torch.tensor([[2.0, 0.0, 0.0], [2.0, 0.0, 0.0]])
  kicked = rule.update(feet, q, ball, moving, r, 0.02)
  assert kicked.tolist() == [True, False]

"""Kick scorecard: one judgement from benchmark v2 and rs_kick (user 2026-10-26:
"use our updated bench").

Benchmark v2 (``judges.run_kick``) covers the whole loop (approach, goals,
falls, short-pass stop, smoothness); rs_kick (``rs_judge``, power by kick
class) is the runswift-spec kick test paired per trial. The engine uses three
stages, each against the current champion's own results (``refs``):

- **probe** (during training): rs_kick deployed, seed 0. Cheap; a child whose
  margin is significantly negative at two probes in a row is stopped early.
- **screen**: benchmark v2 ``gate`` size, seed 1 (quick plus the full loop and
  the goal grid, where n1 passed quick and failed later) + rs_kick deployed s0.
- **confirm**: benchmark v2 full on seeds 1 and 2 + rs_kick lab and deployed on
  seeds 0 and 1.

Score = benchmark v2 fitness + ``RS_POINTS`` x the mean deployed rs_kick margin
(0.02 = +20, about one benchmark seed's noise). Regressions: every benchmark v2
regression, plus any rs_kick margin whose 95 % CI lies below zero. Confirmed
(promotable) when there are no regressions, the score is positive, and either
benchmark v2 gains on both seeds or rs_kick gains significantly on both
deployed seeds.
"""

from __future__ import annotations

import statistics
from pathlib import Path
from typing import Any

from k1.eval import judges, rs_judge
from k1.eval.verdict import Verdict

ROOT = judges.ROOT
RS_POINTS = 1000.0
# h022's benchmark v2 gate-size result (seed 1); made with
# `python scripts/tools/kick_bench2.py run h022_c2_18450_gate_s1 CK --size gate`.
GATE_REFERENCE = judges.BENCH / "h022_c2_18450_gate_s1.json"


def default_refs() -> dict[str, Any]:
  """The champion's reference results when the state has none (h022)."""
  return {
    "bench": {
      "gate_1": str(GATE_REFERENCE),
      "full_1": str(judges.KICK_REFERENCE[("full", 1)]),
      "full_2": str(judges.KICK_REFERENCE[("full", 2)]),
    },
    "rs": {f"{m}_s{s}": str(p) for (m, s), p in rs_judge.CHAMPION.items()},
  }


def _deployed(margins: dict[str, list[float]]) -> list[list[float]]:
  return [m for k, m in sorted(margins.items()) if k.startswith("deployed")]


def combine(bench: Verdict, rs: rs_judge.RsVerdict, confirm: bool) -> Verdict:
  """One verdict from a benchmark v2 verdict and an rs_kick result."""
  if bench.status != "scored":
    return bench
  rs_regress = [f"rs_kick:{k}:{m[0]:+.3f}" for k, m in sorted(rs.margins.items())
                if m[2] < 0]  # fmt: skip
  dep = _deployed(rs.margins)
  rs_points = RS_POINTS * statistics.fmean(m[0] for m in dep) if dep else 0.0
  score = round((bench.score or 0.0) + rs_points, 3)
  regress = list(bench.regressions) + rs_regress
  rs_gain = bool(dep) and all(m[1] > 0 for m in dep) and len(dep) >= 2
  confirmed = confirm and not regress and score > 0 and (bench.confirmed or rs_gain)
  return Verdict(
    judge="kick_scorecard",
    status="scored",
    checkpoint=bench.checkpoint,
    score=score,
    regressions=regress,
    metrics={
      **bench.metrics,
      "bench_score": bench.score,
      "rs_points": round(rs_points, 2),
      "rs": rs.to_dict(),
    },  # fmt: skip
    findings=list(bench.findings),
    reference=bench.reference,
    confirmed=confirmed,
  )


def probe(checkpoint: str, name: str, refs: dict[str, Any]) -> rs_judge.RsVerdict:
  return rs_judge.run(checkpoint, name, (0,), ("deployed",), refs.get("rs"))


def screen(checkpoint: str, name: str, refs: dict[str, Any]) -> Verdict:
  gate = Path(refs["bench"]["gate_1"])
  if not gate.is_file():
    return Verdict("kick_scorecard", "smoke_failed", checkpoint,
                   findings=[f"no gate-size reference for the champion: {gate}"])  # fmt: skip
  bench = judges.run_kick(checkpoint, f"{name}_gate_s1", "gate", 1, gate)
  if bench.status != "scored":
    return bench
  rs = rs_judge.run(checkpoint, f"{name}_screen", (0,), ("deployed",), refs.get("rs"))
  return combine(bench, rs, confirm=False)


def confirm(checkpoint: str, name: str, refs: dict[str, Any]) -> Verdict:
  verdicts = [
    judges.run_kick(
      checkpoint, f"{name}_full_s{s}", "full", s, Path(refs["bench"][f"full_{s}"])
    )  # fmt: skip
    for s in (1, 2)
  ]
  failed = next((v for v in verdicts if v.status != "scored"), None)
  if failed is not None:
    return failed
  scores = [v.score or 0.0 for v in verdicts]
  regress = [r for v in verdicts for r in v.regressions]
  bench = Verdict(
    judge="kick_bench_v2",
    status="scored",
    checkpoint=checkpoint,
    score=round(sum(scores), 3),
    regressions=regress,
    findings=[f for v in verdicts for f in v.findings if f.startswith("ungated")],
    metrics={
      "size": "full",
      "seeds": [1, 2],
      "per_seed": scores,
      "bench": [v.metrics["bench"] for v in verdicts],
    },  # fmt: skip
    reference=", ".join(v.reference or "" for v in verdicts),
    confirmed=all(sc > 0 for sc in scores) and not regress,
  )
  rs = rs_judge.run(checkpoint, f"{name}_confirm", (0, 1), tuple(rs_judge.MODES),
                    refs.get("rs"))  # fmt: skip
  return combine(bench, rs, confirm=True)


def refs_after_promotion(v: Verdict, gate_result: str) -> dict[str, Any]:
  """The new champion's references: its confirm results plus a gate-size run."""
  bench = v.metrics["bench"]
  return {
    "bench": {
      "gate_1": str(ROOT / gate_result),
      "full_1": str(ROOT / bench[0]),
      "full_2": str(ROOT / bench[1]),
    },
    "rs": dict(v.metrics["rs"]["trials"]),
  }

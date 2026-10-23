"""One judge per task family: run its fixed benchmark on a checkpoint and return
a ``Verdict``.

kick       benchmark v2 (``scripts/tools/kick_bench2.py``) scored by
           ``fitness_v2`` against the champion h022 (same size and seed) and
           B-Human: weighted fitness and no-regression gates (lessons E4, E27).
           ``confirm_kick`` is the promotion check: the full benchmark on seeds 1
           and 2, as the old loop's ``confirm_and_install``.
Others are listed with the tool that judges them today; wrapping them into
verdicts is the next step (``wrapped = False``).
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from k1.eval.verdict import Verdict

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "scripts" / "tools"
BENCH = ROOT / "docs" / "benchmarks_v2"
# The champion's results per (size, seed).
KICK_REFERENCE = {
  ("quick", 1): ROOT / "tests" / "golden" / "bench" / "kick_champion_h022_quick.json",
  ("full", 1): BENCH / "h022_c2_18450_2seed.json",
  ("full", 2): BENCH / "h022_c2_18450_2seed_s2.json",
}
BHUMAN = BENCH / "bhuman.json"
# Benchmarks run in the default env: no genes, reward program or ball override,
# as the references were made (evolve_kick.bench, golden_bench.py). Genes shape
# training, not the judged behaviour.
_BENCH_ENV_DROP = ("KICK_GENES", "DRIBBLE_GENES", "KICK_REWARD_PROGRAM", "K1_BALL")
# Metrics without a confidence interval (style statistics): reported as
# findings, not regressions, as in golden_bench.py; an identical re-run of the
# champion "regressed" on style_selection_pct. Identical re-runs of the champion
# also scored +10.6 and +29.3 on one seed (2026-10-24), so a single-seed score
# is not a promotion: confirm on a second seed (Verdict.confirmed).
UNGATED = ("style_selection_pct", "style_repertoire")


@dataclass(frozen=True)
class Judge:
  name: str
  tasks: tuple[str, ...]
  tool: str
  wrapped: bool


JUDGES = (
  Judge(
    "kick_bench_v2",
    ("Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1",),
    "scripts/tools/kick_bench2.py + fitness_v2.py",
    True,
  ),
  Judge(
    "dribble_gate",
    ("Mjlab-Velocity-Dribble-Amp-DA-Muon-Booster-K1",),
    "scripts/tools/dribble_gate.py (vs swa_v17), dribble_eval.py",
    False,
  ),
  Judge(
    "selfplay_eval",
    ("Mjlab-Velocity-Kick-SelfPlay-Amp-DA-Muon-Booster-K1",),
    "scripts/tools/selfplay_eval.py",
    False,
  ),
  Judge(
    "controller_eval",
    ("Mjlab-Velocity-Striker-Controller-Booster-K1",),
    "scripts/tools/controller_eval.py",
    False,
  ),
  Judge(
    "bhuman_bench_v2",
    tuple(f"Mjlab-BHuman-Kick{s}-Booster-K1" for s in ("", "-Stage1")),
    "scripts/tools/bench_bhuman_kick_v2.py",
    False,
  ),
)


def judge_for(task: str) -> Judge | None:
  return next((j for j in JUDGES if task in j.tasks), None)


def _fitness() -> ModuleType:
  spec = importlib.util.spec_from_file_location("fitness_v2", TOOLS / "fitness_v2.py")
  assert spec and spec.loader
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


def score_kick(
  result: dict, size: str, seed: int = 1
) -> tuple[float, list[str], list[str]]:
  """Fitness, regressions and B-Human metrics beaten, against the champion."""
  fit = _fitness()
  ref = json.loads(KICK_REFERENCE[(size, seed)].read_text())
  bh = json.loads(BHUMAN.read_text()) if BHUMAN.is_file() else None
  total, regress = fit.score(result, ref, bh)
  beaten = fit.convincing(result, bh) if bh else []
  return float(total), list(regress), list(beaten)


def _bench_kick(checkpoint: str, name: str, size: str, seed: int) -> dict | str:
  env = {k: v for k, v in os.environ.items() if k not in _BENCH_ENV_DROP}
  env["BENCH2_SEED"] = str(seed)
  proc = subprocess.run(
    [sys.executable, str(TOOLS / "kick_bench2.py"), "run", name, checkpoint, "--size", size],
    cwd=ROOT, env=env, capture_output=True, text=True,
  )  # fmt: skip
  out = BENCH / f"{name}.json"
  if proc.returncode != 0 or not out.is_file():
    tail = (proc.stderr or proc.stdout).strip().splitlines()[-4:]
    return "benchmark crashed: " + " | ".join(tail)
  return json.loads(out.read_text())


def run_kick(checkpoint: str, name: str, size: str = "quick", seed: int = 1) -> Verdict:
  result = _bench_kick(checkpoint, name, size, seed)
  if isinstance(result, str):
    return Verdict("kick_bench_v2", "smoke_failed", checkpoint, findings=[result])
  total, regress, beaten = score_kick(result, size, seed)
  ungated = [r for r in regress if r.split(":")[1] in UNGATED]
  return Verdict(
    judge="kick_bench_v2",
    status="scored",
    checkpoint=checkpoint,
    score=round(total, 3),
    regressions=[r for r in regress if r not in ungated],
    findings=[f"ungated change (no CI): {r}" for r in ungated]
    + ["single seed: identical champion re-runs scored up to +29; confirm on seed 2"],
    metrics={"bench": f"docs/benchmarks_v2/{name}.json", "size": size, "seed": seed,
             "bhuman_beaten": beaten},
    reference=str(KICK_REFERENCE[(size, seed)].relative_to(ROOT)),
  )  # fmt: skip


def confirm_kick(checkpoint: str, name: str) -> Verdict:
  """Full benchmark on seeds 1 and 2, each against the champion's same seed;
  confirmed when both gain without regressions (score is the sum)."""
  verdicts = [run_kick(checkpoint, f"{name}_full_s{s}", "full", s) for s in (1, 2)]
  failed = next((v for v in verdicts if v.status != "scored"), None)
  if failed is not None:
    return failed
  regress = [r for v in verdicts for r in v.regressions]
  scores = [v.score or 0.0 for v in verdicts]
  return Verdict(
    judge="kick_bench_v2",
    status="scored",
    checkpoint=checkpoint,
    score=round(sum(scores), 3),
    regressions=regress,
    findings=[f for v in verdicts for f in v.findings if f.startswith("ungated")],
    metrics={"size": "full", "seeds": [1, 2], "per_seed": scores,
             "bench": [v.metrics["bench"] for v in verdicts]},
    reference=", ".join(v.reference or "" for v in verdicts),
    confirmed=all(sc > 0 for sc in scores) and not regress,
  )  # fmt: skip


def run(
  task: str, checkpoint: str, name: str, size: str, confirm: bool = False
) -> Verdict:
  judge = judge_for(task)
  if judge is None or not judge.wrapped:
    tool = judge.tool if judge else "none"
    raise NotImplementedError(f"no wrapped judge for {task} yet (today: {tool})")
  return confirm_kick(checkpoint, name) if confirm else run_kick(checkpoint, name, size)

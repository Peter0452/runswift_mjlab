"""Champion benchmark check: does the kick champion still score the same?

Runs benchmark v2 (`kick_bench2.py`, quick size, seed 1) on the kick-loop
champion and compares every metric with the recorded reference: a metric
fails when its 95 % CI no longer overlaps the reference CI (the same rule
`kick_bench2.py compare` uses for "better" / "worse"). Up to MAX_SEPARATED
separations are tolerated (the measured noise between equivalent runs). The
two whole-run style statistics (no CI, very noisy) are reported but not gated.

  .venv/bin/python scripts/tools/golden_bench.py record
  .venv/bin/python scripts/tools/golden_bench.py check      # exit 1 on failure
  .venv/bin/python scripts/tools/golden_bench.py history    # vs the Oct-9 bench

About 5-10 minutes on the GPU; run it alone, not next to training.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCH_OUT = ROOT / "docs" / "benchmarks_v2"
REF = ROOT / "tests" / "golden" / "bench" / "kick_champion_h022_quick.json"
HISTORY = BENCH_OUT / "h022_c2_18450.json"  # full bench from 2026-10-09
UNGATED = {"style_selection_pct", "style_repertoire"}
# Equivalent code separated on 0-2 of ~220 metric/cap pairs across five runs
# (2026-10-23); the B-Human-ball regression separated 29.
MAX_SEPARATED = 3
CHECKPOINT = (
  "logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/"
  "model_18450.pt"
)


def bench(name: str) -> dict:
  out = BENCH_OUT / f"{name}.json"
  out.unlink(missing_ok=True)  # kick_bench2 resumes finished tracks otherwise
  # Default recipe and ball: per-run switches would change what is measured.
  env = {k: v for k, v in os.environ.items() if k not in ("KICK_GENES", "K1_BALL")}
  env["BENCH2_SEED"] = "1"
  subprocess.run(
    [
      sys.executable,
      str(ROOT / "scripts/tools/kick_bench2.py"),
      "run",
      name,
      CHECKPOINT,
      "--size",
      "quick",
    ],
    cwd=ROOT,
    env=env,
    check=True,
  )
  return json.loads(out.read_text())


def compare(new: dict, ref: dict) -> list[str]:
  """CI separations between two bench results, as report lines."""
  bad, checked, no_ci = [], 0, set()
  for key in sorted(set(new) & set(ref)):
    if key.startswith("_"):
      continue
    for metric in sorted(set(new[key]) & set(ref[key])):
      if metric.startswith("_"):
        continue
      for cap in ("low", "high"):
        x, y = new[key][metric].get(cap), ref[key][metric].get(cap)
        if not x or not y or x[3] == 0 or y[3] == 0:
          continue
        # Whole-run style statistics have no CI and swing widely between
        # identical runs (33 vs 92 %); report, don't gate.
        if metric in UNGATED:
          no_ci.add(metric)
          continue
        checked += 1
        if x[2] < y[1] or y[2] < x[1]:
          bad.append(
            f"{key} {metric} {cap}: now {x[0]:.3g} [{x[1]:.3g}, {x[2]:.3g}]"
            f" vs {y[0]:.3g} [{y[1]:.3g}, {y[2]:.3g}]"
          )
  print(f"BENCH compared {checked} metric/cap pairs, {len(bad)} separated", flush=True)
  if no_ci:
    print(f"BENCH not gated (no CI): {sorted(no_ci)}", flush=True)
  return bad


def main(mode: str) -> int:
  if mode == "record":
    bench("golden_h022_quick")
    REF.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(BENCH_OUT / "golden_h022_quick.json", REF)
    print(f"BENCH recorded {REF.relative_to(ROOT)}", flush=True)
    return 0
  if mode == "check":
    bad = compare(bench("golden_h022_quick_check"), json.loads(REF.read_text()))
  elif mode == "history":
    bad = compare(json.loads(REF.read_text()), json.loads(HISTORY.read_text()))
  else:
    raise SystemExit(f"unknown mode {mode}")
  for line in bad:
    print(f"  {line}", flush=True)
  ok = len(bad) <= MAX_SEPARATED
  print(
    f"BENCH {'ok' if ok else 'FAIL'} ({len(bad)} separated, tolerance {MAX_SEPARATED})",
    flush=True,
  )
  return 0 if ok else 1


if __name__ == "__main__":
  sys.exit(main(sys.argv[1]))

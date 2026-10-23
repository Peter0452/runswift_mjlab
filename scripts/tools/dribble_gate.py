"""No-regression gate for dribble candidates against a fixed bench model (swa_v17).

Inputs, all produced by dribble_watch_bench.sh for both models:
  * deploy-cfg eval:  logs/dribble_eval/bench/<name>.jsonl (dribble_eval.py, 2 seeds)
  * runner sim2real:  k1_policy_runner/runs/dribble_bench.jsonl (dribble_bench.py)
  * parity:           a dribble_parity_check.py log (optional)

Prints the objective (speed) deltas, every gate with PASS / FAIL, and a verdict:

  uv run python scripts/tools/dribble_gate.py CANDIDATE [--base swa_v17] \
      [--parity LOG]
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVAL_DIR = ROOT / "logs" / "dribble_eval" / "bench"
RUNNER_BENCH = ROOT.parent / "k1_policy_runner" / "runs" / "dribble_bench.jsonl"
SLOW_TOL = 0.08
"""Allowed success loss vs the bench model at 0.3 and 0.5 m/s commands."""


def deploy_eval(name: str) -> dict[float, dict[str, float]]:
  """Window-weighted means per commanded speed over seeds and directions."""
  acc: dict[float, collections.Counter] = collections.defaultdict(collections.Counter)
  for line in (EVAL_DIR / f"{name}.jsonl").read_text().splitlines():
    d = json.loads(line)
    w = d["windows"]
    a = acc[d["speed"]]
    a["w"] += w
    for k in ("success", "ball_along", "robot_along", "ball_dist", "fall"):
      a[k] += w * d[k]
  return {s: {k: a[k] / a["w"] for k in a if k != "w"} for s, a in acc.items()}


def runner_bench(onnx_name: str) -> dict:
  rows = [json.loads(x) for x in RUNNER_BENCH.read_text().splitlines()]
  rows = [r for r in rows if r["model"] == onnx_name]
  if not rows:
    sys.exit(f"no runner bench row for {onnx_name} in {RUNNER_BENCH}")
  return rows[-1]


def main() -> int:
  p = argparse.ArgumentParser()
  p.add_argument("candidate", help="bench name, e.g. v18_15700")
  p.add_argument("--base", default="swa_v17")
  p.add_argument("--base-onnx", default="k1_dribble_flat_swa_v17_14200-15400.onnx")
  p.add_argument("--onnx", help="candidate ONNX file name (default <candidate>.onnx)")
  p.add_argument("--parity", help="dribble_parity_check.py log of the candidate")
  args = p.parse_args()

  ce, be = deploy_eval(args.candidate), deploy_eval(args.base)
  cr = runner_bench(args.onnx or f"{args.candidate}.onnx")
  br = runner_bench(args.base_onnx)

  print(f"{args.candidate} vs {args.base}")
  print("objective (deploy-cfg eval): speed  success  ball speed  ball dist  falls")
  for s in sorted(ce):
    c, b = ce[s], be.get(s)
    if b is None:
      continue
    print(
      f"  {s:4.1f}  {c['success']:.2f} ({c['success'] - b['success']:+.2f})"
      f"  {c['ball_along']:.2f} ({c['ball_along'] - b['ball_along']:+.2f})"
      f"  {c['ball_dist']:.2f} ({c['ball_dist'] - b['ball_dist']:+.2f})"
      f"  {c['fall']:.3f} ({c['fall'] - b['fall']:+.3f})"
    )
  print("objective (runner sim): ball speed per command")
  for k in [k for k in cr if k.startswith("ball_v ")]:
    print(f"  {k[7:]:8s} {cr[k]:.2f} ({cr[k] - br[k]:+.2f})")

  def fall_rate(e: dict) -> float:
    return sum(v["fall"] for v in e.values()) / len(e)

  gates: list[tuple[str, bool, str]] = []

  def gate(name: str, ok: bool, detail: str) -> None:
    gates.append((name, ok, detail))

  # User (2026-10-21): "we can sacrifice slow dribble for fast a bit", so the
  # slow speeds may give up SLOW_TOL; 0.8 m/s keeps the strict -0.03.
  for s in (0.3, 0.5, 0.8):
    c, b = ce[s]["success"], be[s]["success"]
    tol = SLOW_TOL if s < 0.8 else 0.03
    gate(
      f"deploy success {s}", c >= b - tol, f"{c:.2f} vs {b:.2f} (-{tol:.2f} allowed)"
    )
  cf, bf = fall_rate(ce), fall_rate(be)
  gate("deploy falls", cf <= max(1.5 * bf, bf + 0.003), f"{cf:.4f} vs {bf:.4f}")
  c, b = ce[0.5]["ball_dist"], be[0.5]["ball_dist"]
  gate("deploy ball dist 0.5", c <= b + 0.05, f"{c:.2f} vs {b:.2f} (+0.05 allowed)")
  gate("runner falls", cr["falls"] == 0, f"{cr['falls']} runs")
  fs = cr["flat_stance"]
  gate("runner flat stance", 0.70 <= fs <= 0.87, f"{fs:.0%} (AMP walk 73 %, 70-87 %)")
  for k, extra in (("landing_p50", 0.15), ("landing_p90", 0.20)):
    gate(f"runner {k}", cr[k] <= br[k] + extra, f"{cr[k]:.2f} vs {br[k]:.2f}")
  gate(
    "runner torque saturation",
    cr["leg_torque_sat"] <= max(0.01, 2 * br["leg_torque_sat"]),
    f"{cr['leg_torque_sat']:.4f} vs {br['leg_torque_sat']:.4f}",
  )
  for k in (
    "tau_p99_left",
    "tau_p99_right",
    "dq_target_p99",
    "jitter_mean",
    "angrate_p90",
  ):
    gate(f"runner {k}", cr[k] <= 1.15 * br[k], f"{cr[k]:.3f} vs {br[k]:.3f} (x1.15)")
  gate(
    "runner leg over speed",
    cr["leg_over_speed"] <= 0.001,
    f"{cr['leg_over_speed']:.4f}",
  )
  gate(
    "runner tilt p90",
    cr["tilt_p90"] <= br["tilt_p90"] + 2.0,
    f"{cr['tilt_p90']:.1f} vs {br['tilt_p90']:.1f} deg",
  )
  gate("runner stop", abs(cr["ball_v 0@0"]) <= 0.05, f"{cr['ball_v 0@0']:.3f} m/s")
  ce5, be5 = abs(cr["ball_v 0.5@0"] - 0.5), abs(br["ball_v 0.5@0"] - 0.5)
  gate("runner 0.5 tracking", ce5 <= be5 + 0.10, f"err {ce5:.2f} vs {be5:.2f}")
  if args.parity:
    text = Path(args.parity).read_text()
    m = re.search(r"ONNX vs training policy action\s+max\s+([0-9.e+-]+)", text)
    diff = float(m.group(1)) if m else float("inf")
    gate("parity ONNX action", diff <= 1e-4, f"{diff:.1e}")

  print("gates:")
  for name, ok, detail in gates:
    print(f"  {'PASS' if ok else 'FAIL'}  {name:28s} {detail}")
  failed = [g[0] for g in gates if not g[1]]
  print(f"verdict: {'PASS' if not failed else 'FAIL (' + ', '.join(failed) + ')'}")
  return 0 if not failed else 1


if __name__ == "__main__":
  raise SystemExit(main())

"""Fixed K1 kick benchmark: one scored table per checkpoint, compared to B-Human
and to our current best, with explicit pass rules.

usage:
  python scripts/tools/kick_benchmark.py run NAME CHECKPOINT   # ours
  python scripts/tools/kick_benchmark.py run bhuman             # B-Human kick
  python scripts/tools/kick_benchmark.py compare NAME [--best BEST]

Results: docs/benchmarks/NAME.json. `compare` prints every metric for NAME,
B-Human and BEST (default: docs/benchmarks/BEST), and applies the rules:
  * head-to-head metrics (close-start kick, B-Human's own scenario): "beats
    B-Human" when better than B-Human's value;
  * all metrics: "no regression" when not worse than BEST by more than the
    metric's tolerance.
A candidate is promotable only if it has no regressions; it "transcends" a
head-to-head metric when it beats both B-Human and BEST there.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "benchmarks"
PY = ["uv", "run", "python"]

# name: (higher_is_better, tolerance, head_to_head, description)
# Tolerances ~ seed-to-seed noise of one 1024-env eval (2026-10-05: goals ±0.06,
# accuracy ±2 %, search ±5 %). Air balls are allowed (user), so a wide margin.
METRICS: dict[str, tuple[bool, float, bool, str]] = {
  # Close start (ball 0.4-1.5 m, any bearing) - B-Human's scenario
  "h2h_first_kick_s": (False, 0.15, True, "time to first kick, p50 (s)"),
  "h2h_first_kick_pct": (True, 4.0, True, "robots kicking within 10 s (%)"),
  "h2h_first_on_target_pct": (True, 3.0, True, "first kick within 20 deg (%)"),
  "h2h_aim_pct": (True, 2.0, True, "all kicks within 20 deg (%)"),
  "h2h_long_3d": (True, 0.3, True, "long kicks, ball 3D speed p50 (m/s)"),
  "h2h_long_aim_pct": (True, 3.0, True, "long kicks within 20 deg (%)"),
  "h2h_long_knee_p90": (False, 5.0, True, "long kicks, knee torque p90 (Nm)"),
  "h2h_long_hip_p90": (False, 5.0, True, "long kicks, hip pitch torque p90 (Nm)"),
  "h2h_support_planted_pct": (True, 3.0, True, "support foot on ground at contact (%)"),
  # Same close-start scenario with perfect perception for both policies
  # (fairness both ways, 2026-10-06): exact ball every step.
  "h2h_true_first_kick_s": (
    False,
    0.15,
    True,
    "[perfect perception] time to first kick, p50 (s)",
  ),
  "h2h_true_first_kick_pct": (
    True,
    4.0,
    True,
    "[perfect perception] robots kicking within 10 s (%)",
  ),
  "h2h_true_first_on_target_pct": (
    True,
    3.0,
    True,
    "[perfect perception] first kick within 20 deg (%)",
  ),
  "h2h_true_aim_pct": (
    True,
    2.0,
    True,
    "[perfect perception] all kicks within 20 deg (%)",
  ),
  "h2h_true_long_3d": (
    True,
    0.3,
    True,
    "[perfect perception] long kicks, ball 3D speed p50 (m/s)",
  ),
  "h2h_true_long_aim_pct": (
    True,
    3.0,
    True,
    "[perfect perception] long kicks within 20 deg (%)",
  ),
  # Full loop (our scenario)
  "bumps_aim_pct": (True, 3.0, False, "bumps: kicks within 20 deg (%)"),
  "bumps_goals": (True, 0.07, False, "bumps: goals per episode"),
  "bumps_late_falls_pct": (False, 0.5, False, "bumps: falls after 2 s (%)"),
  "flat_aim_pct": (True, 3.0, False, "flat: kicks within 20 deg (%)"),
  "flat_goals": (True, 0.07, False, "flat: goals per episode"),
  "flat_late_falls_pct": (False, 0.3, False, "flat: falls after 2 s (%)"),
  "push_late_falls_pct": (False, 0.7, False, "push 0.6: falls after 2 s (%)"),
  "moving_goals": (True, 0.07, False, "moving ball: goals per episode"),
  "short_stop_m": (
    False,
    0.6,
    False,
    "short passes: stop distance from target p50 (m)",
  ),
  "long_x_needed": (True, 0.05, False, "long kicks: speed / needed p50"),
  "long_air15_pct": (False, 10.0, False, "long kicks above 15 cm (%)"),
  "search_turn_rad": (
    True,
    0.2,
    False,
    "search: net heading change per search p50 (rad)",
  ),
  "search_found_pct": (True, 6.0, False, "search: moved ball re-found within 6 s (%)"),
  "lean_fast_deg": (False, 0.7, False, "trunk pitch at 1.0-1.5 m/s, mean (deg, + fwd)"),
  "height_fast_m": (True, 0.005, False, "trunk height at 1.0-1.5 m/s (m)"),
  "caps_fast_vx": (True, 0.08, False, "speed at 1.6-2.0 m/s caps, mean (m/s)"),
  # Latency robustness (robot 2026-10-06: evo_g014 missed the ball on the real
  # K1): bumps with ball detections delayed 60-120 ms instead of 0-40 ms.
  "latency_goals": (True, 0.07, False, "detection delay 60-120 ms: goals per episode"),
  "latency_aim_pct": (
    True,
    3.0,
    False,
    "detection delay 60-120 ms: kicks within 20 deg (%)",
  ),
  # Approach from far (ball 3-8 m, any bearing): the policy must still
  # approach and kick like the earlier models (user, 2026-10-06).
  "approach_kick_pct": (True, 4.0, False, "far start: kicked within 15 s (%)"),
  "approach_first_s": (False, 0.4, False, "far start: time to first kick, p50 (s)"),
  "approach_on_target_pct": (
    True,
    4.0,
    False,
    "far start: first kick within 20 deg (%)",
  ),
  "approach_vx": (True, 0.05, False, "far start: approach speed, mean (m/s)"),
}


def sh(args: list[str]) -> str:
  r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
  return r.stdout + r.stderr


def num(pat: str, text: str, i: int = 1) -> float | None:
  m = re.search(pat, text)
  return float(m.group(i)) if m else None


def run_bhuman() -> dict:
  m: dict = {}
  s = sh(
    PY
    + [
      "scripts/tools/kick_style_compare.py",
      "bhuman",
      "--any-bearing",
      "--perception",
      "camera",
    ]
  )
  _style(
    m,
    sh(
      PY
      + [
        "scripts/tools/kick_style_compare.py",
        "bhuman",
        "--any-bearing",
        "--perception",
        "true",
      ]
    ),
    "h2h_true_",
  )
  a = sh(PY + ["scripts/tools/kick_anatomy.py", "bhuman"])
  _style(m, s)
  m["h2h_support_planted_pct"] = num(r"support foot on ground at contact (\d+) %", a)
  return m


def _style(m: dict, s: str, pre: str = "h2h_") -> None:
  m[f"{pre}first_kick_s"] = num(
    r"first kick within 10 s: [\d.]+ % of robots, time p50 ([\d.]+)", s
  )
  m[f"{pre}first_kick_pct"] = num(r"first kick within 10 s: ([\d.]+) %", s)
  m[f"{pre}first_on_target_pct"] = num(r"first kick within 20 deg ([\d.]+) %", s)
  m[f"{pre}aim_pct"] = num(r"aim err <= 20 deg ([\d.]+) %", s)
  long = re.search(r"STYLE long .*", s)
  if long:
    t = long.group(0)
    m[f"{pre}long_3d"] = num(r"ball 3D p50 ([\d.]+)", t)
    m[f"{pre}long_aim_pct"] = num(r"aim <= 20 deg ([\d.]+) %", t)
    if pre == "h2h_":
      m["h2h_long_knee_p90"] = num(r"knee p90 ([\d.]+)", t)
      m["h2h_long_hip_p90"] = num(r"hip p90 ([\d.]+)", t)


def run_ours(ck: str) -> dict:
  m: dict = {}
  ev = PY + [
    "scripts/tools/eval_kick_loop.py",
    "--checkpoint",
    ck,
    "--num-envs",
    "1024",
    "--seed",
    os.environ.get("KICK_BENCH_SEED", "1"),
  ]
  for key, extra in (
    ("bumps", ["--no-push"]),
    ("flat", ["--flat", "--no-push"]),
    ("push", ["--push-test", "0.6"]),
    ("moving", ["--moving-ball", "--no-push"]),
  ):
    t = sh(ev + extra)
    if key in ("bumps", "flat"):
      m[f"{key}_aim_pct"] = num(r"kicks on target \(≤20°\)\s+(\d+)%", t)
    if key in ("bumps", "flat", "moving"):
      m[f"{key}_goals"] = num(r"goals per episode\s+mean ([\d.]+)", t)
    if key in ("bumps", "flat", "push"):
      m[f"{key}_late_falls_pct"] = num(r"after the first 2 s ([\d.]+)%", t)
  t = sh(ev + ["--no-push", "--vision-delay", "3,6"])
  m["latency_goals"] = num(r"goals per episode\s+mean ([\d.]+)", t)
  m["latency_aim_pct"] = num(r"kicks on target \(≤20°\)\s+(\d+)%", t)
  probe = PY + ["scripts/tools/kick_probes.py", ck]
  t = sh(probe + ["range"])
  m["short_stop_m"] = num(r"REST short .*stop from target p50 ([\d.]+)", t)
  m["long_x_needed"] = num(r"RANGE long .*x needed p50 ([\d.]+)", t)
  t = sh(probe + ["loft"])
  m["long_air15_pct"] = num(r"LOFT long .*\(> 15 cm\) (\d+) %", t)
  t = sh(probe + ["search"])
  m["search_found_pct"] = num(r"re-found within 6 s (\d+) %", t)
  m["search_turn_rad"] = num(r"net heading change per search p50 ([\d.]+)", t)
  t = sh(probe + ["lean"])
  fast = re.search(
    r"LEAN 1\.0-1\.5 m/s\s+\d+%\s+([+-][\d.]+) /\s+[+-][\d.]+\s+([\d.]+)", t
  )
  if fast:
    m["lean_fast_deg"], m["height_fast_m"] = float(fast.group(1)), float(fast.group(2))
  t = sh(probe + ["approach"])
  m["approach_kick_pct"] = num(r"kicked within 15 s (\d+) %", t)
  m["approach_first_s"] = num(r"first kick p50 ([\d.]+) s", t)
  m["approach_on_target_pct"] = num(r"on target (\d+) %", t)
  m["approach_vx"] = num(r"approach vx mean ([\d.-]+)", t)
  t = sh(probe + ["caps"])
  m["caps_fast_vx"] = num(r"CAPS cap 1\.6-2\.0: vx mean ([\d.]+)", t)
  s = sh(
    PY
    + [
      "scripts/tools/kick_style_compare.py",
      "ours",
      ck,
      "--any-bearing",
      "--perception",
      "camera",
    ]
  )
  _style(
    m,
    sh(
      PY
      + [
        "scripts/tools/kick_style_compare.py",
        "ours",
        ck,
        "--any-bearing",
        "--perception",
        "true",
      ]
    ),
    "h2h_true_",
  )
  _style(m, s)
  a = sh(PY + ["scripts/tools/kick_anatomy.py", "ours", ck])
  m["h2h_support_planted_pct"] = num(r"support foot on ground at contact (\d+) %", a)
  return m


def better(key: str, a: float, b: float) -> bool:
  hib = METRICS[key][0]
  return a > b if hib else a < b


def worse_by(key: str, a: float, b: float) -> float:
  hib = METRICS[key][0]
  return (b - a) if hib else (a - b)


def compare(name: str, best: str) -> None:
  cur = json.loads((OUT / f"{name}.json").read_text())
  bh = (
    json.loads((OUT / "bhuman.json").read_text())
    if (OUT / "bhuman.json").exists()
    else {}
  )
  ref = (
    json.loads((OUT / f"{best}.json").read_text())
    if (OUT / f"{best}.json").exists()
    else {}
  )
  regress, beats, trans = [], [], []
  print(f"| metric | {name} | B-Human | {best} | verdict |")
  print("|---|---|---|---|---|")
  for key, (_, tol, h2h, desc) in METRICS.items():
    v, b, r = cur.get(key), bh.get(key), ref.get(key)
    verdict = []
    if v is not None and r is not None and worse_by(key, v, r) > tol:
      verdict.append("REGRESSION")
      regress.append(key)
    if h2h and v is not None and b is not None:
      if better(key, v, b):
        verdict.append("beats B-Human")
        beats.append(key)
        if r is None or better(key, v, r):
          trans.append(key)
      else:
        verdict.append("behind B-Human")
    fmt = lambda x: "—" if x is None else f"{x:g}"  # noqa: E731
    print(
      f"| {desc} | {fmt(v)} | {fmt(b) if h2h else ''} | {fmt(r)} | {', '.join(verdict)} |"
    )
  h2h_n = sum(1 for k in METRICS if METRICS[k][2])
  print(
    f"\nBEATS B-Human on {len(beats)} / {h2h_n} head-to-head metrics; transcends (beats"
    f" B-Human and {best}) on {len(trans)}; regressions vs {best}: {len(regress)}"
    f" ({', '.join(regress) or 'none'}) -> {'PROMOTABLE' if not regress else 'NOT promotable'}"
  )


def main() -> None:
  OUT.mkdir(parents=True, exist_ok=True)
  if sys.argv[1] == "run":
    name = sys.argv[2]
    m = run_bhuman() if name == "bhuman" else run_ours(sys.argv[3])
    (OUT / f"{name}.json").write_text(json.dumps(m, indent=2))
    print(json.dumps(m, indent=2))
  else:
    best = sys.argv[sys.argv.index("--best") + 1] if "--best" in sys.argv else "BEST"
    compare(sys.argv[2], best)


if __name__ == "__main__":
  main()

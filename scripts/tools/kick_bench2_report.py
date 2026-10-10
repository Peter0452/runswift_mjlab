"""Kick benchmark v2 report: headline metrics per situation for several
policies side by side (GPU engine, mean [95 % CI]), plus the CPU engine's
runner-code results (runswift-comparable).

usage: python scripts/tools/kick_bench2_report.py NAME [NAME ...] > report.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "benchmarks_v2"

HEADLINE = {
  "near_grid": ["first_touch_15_pct", "first_touch_err_deg", "first_touch_speed",
                "first_kick_s", "fall_pct", "joint_stop_pct"],
  "close_any": ["first_touch_15_pct", "first_kick_pct", "first_kick_s",
                "kicks_20_pct", "long_3d", "fall_pct"],
  "approach": ["first_kick_pct", "first_kick_s", "fall_pct", "fall_pct_front",
               "fall_pct_side", "fall_pct_behind", "first_kick_pct_behind", "cap_use"],
  "goal_grid": ["goal_pct", "goal_s", "fall_pct", "fall_before_contact_pct"],
  "full_loop": ["goals_per_ep", "kicks_20_pct", "first_kick_s", "long_3d",
                "long_x_needed", "short_stop_m", "fall_pct", "knee_peak_at_kick",
                "torque_sat_pct", "fast_height_m", "fast_pitch_deg", "action_rate"],
}  # fmt: skip


def fmt(v) -> str:
  if not v or v[3] == 0:
    return "—"
  return f"{v[0]:.3g} [{v[1]:.3g}, {v[2]:.3g}]"


def main() -> None:
  names = sys.argv[1:]
  data = {n: json.loads((OUT / f"{n}.json").read_text()) for n in names}
  keys = sorted({k for d in data.values() for k in d if not k.startswith("_")})
  print("# Kick benchmark v2\n")
  for n, d in data.items():
    m = d.get("_meta", {})
    print(f"- **{n}**: {m.get('policy')} ({m.get('size')}, {m.get('date')})")
  for key in keys:
    track = key.split("/")[0]
    metrics = HEADLINE.get(track, [])
    print(f"\n## {key}\n")
    print("| metric | caps | " + " | ".join(names) + " |")
    print("|---|---|" + "---|" * len(names))
    for metric in metrics:
      for cap in ("low", "high"):
        row = [fmt(data[n].get(key, {}).get(metric, {}).get(cap)) for n in names]
        if all(r == "—" for r in row):
          continue
        print(f"| {metric} | {cap} | " + " | ".join(row) + " |")
  cpu = OUT / "cpu"
  rows = []
  for n in names:
    for d in sorted((cpu / n).glob("*/summary.json")) if (cpu / n).exists() else []:
      for r in json.loads(d.read_text())["rows"]:
        tag = d.parent.name
        if tag.startswith("near"):
          rows.append(
            f"| {n} | {tag} | {r['ball_profile']} | first strike ≤ 15° "
            f"{r['on_direction_launch']}/{r['planned']}, err p50 "
            f"{r['median_absolute_heading_error_deg']:.1f}°, speed p50 "
            f"{r['median_launch_speed_m_s']:.2f} m/s, upright {r['survived']}/{r['planned']} |"
          )
        else:
          rows.append(
            f"| {n} | {tag} | {r['ball_profile']} | goals {r['goals']}/{r['planned']}, "
            f"falls during attempt {r['falls_during_attempt']}, contact {r['robot_contact']} |"
          )
  if rows:
    print("\n## CPU engine (runner code, runswift harness)\n")
    print("| policy | run | ball | result |\n|---|---|---|---|")
    print("\n".join(rows))


if __name__ == "__main__":
  main()

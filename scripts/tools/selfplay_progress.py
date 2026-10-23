"""Block-averaged self-play training curves for one or more runs.

  uv run python scripts/tools/selfplay_progress.py RUN_DIR [RUN_DIR ...] \
      [--block 300]

Per-iteration self-play metrics are noisy (sparse goals, mixed opponents);
block means show the trend. Reward terms are per-second episode averages.
"""

from __future__ import annotations

import argparse
import statistics as st
from pathlib import Path

from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

KEYS = [
  ("Curriculum/task_reward_anneal/alpha", "alpha"),
  ("Metrics/twist/contest_scored", "goals for"),
  ("Metrics/twist/contest_conceded", "goals against"),
  ("SelfPlay/win_rate_pool", "win vs pool"),
  ("SelfPlay/win_rate_latest", "win vs copy"),
  ("Metrics/twist/kicks", "kicks"),
  ("Metrics/twist/kick_speed", "kick speed"),
  ("Metrics/twist/kick_quality", "kick quality"),
  ("Metrics/twist/kick_dir_err", "kick dir err"),
  ("Metrics/twist/near_time_to_kick", "time to kick"),
  ("Metrics/ball_lost", "ball lost"),
  ("Episode_Reward/territory", "territory/s"),
  ("Episode_Reward/dribble_progress", "dribble/s"),
  ("Train/mean_reward", "ep reward"),
]


def main() -> None:
  ap = argparse.ArgumentParser()
  ap.add_argument("runs", nargs="+")
  ap.add_argument("--block", type=int, default=300)
  args = ap.parse_args()
  evs = {}
  for r in args.runs:
    e = EventAccumulator(r, size_guidance={"scalars": 0})
    e.Reload()
    evs[Path(r).name[-16:]] = e
  first = next(iter(evs.values()))
  last = first.Scalars("Train/mean_reward")[-1].step
  edges = list(range(0, last + 1, args.block))
  if edges[-1] < last:
    edges.append(last)
  pairs = list(zip(edges[:-1], edges[1:], strict=True))
  print(f"first run last iteration {last}")
  print(f"{'metric':15s}{'run':>17s}" + "".join(f"{f'{a}-{b}':>11s}" for a, b in pairs))
  for key, name in KEYS:
    for run, e in evs.items():
      row = []
      for a, b in pairs:
        try:
          s = [x.value for x in e.Scalars(key) if a <= x.step < b]
        except KeyError:
          s = []
        row.append(f"{st.mean(s):11.3f}" if len(s) > 5 else f"{'-':>11s}")
      print(f"{name:15s}{run:>17s}" + "".join(row))


if __name__ == "__main__":
  main()

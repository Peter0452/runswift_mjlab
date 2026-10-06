"""Watch a training run and exit as soon as it reaches an iteration or breaks.

Exits with a one-line reason, so it can run in the background and wake whoever
is monitoring. Hard failures are judged on the last ``--window`` iterations:

- episodes collapsed to < 40% of their peak (falling at once),
- kicks collapsed to < 20% of their peak (stopped kicking),
- a value-loss spike > 1e3 (blow-up or reward explosion),
- the training process is gone.

  uv run python scripts/tools/watch_run.py <run_dir> --until 1000 --name stage3_v5
"""

from __future__ import annotations

import argparse
import glob
import subprocess
import sys
import time

from tensorboard.backend.event_processing.event_accumulator import EventAccumulator


def _series(run_dir: str) -> dict[str, dict[int, float]]:
  files = sorted(glob.glob(f"{run_dir}/events*"))
  if not files:
    return {}
  acc = EventAccumulator(files[-1], size_guidance={"scalars": 0})
  acc.Reload()
  tags = acc.Tags()["scalars"]
  return {t: {x.step: x.value for x in acc.Scalars(t)} for t in tags}


def _alive(name: str) -> bool:
  out = subprocess.run(["ps", "-eo", "cmd"], capture_output=True, text=True).stdout
  return any(
    f"run-name {name}" in line and "train" in line for line in out.splitlines()
  )


def check(run_dir: str, window: int, warmup: int) -> tuple[int, str | None]:
  s = _series(run_dir)
  ep = s.get("Train/mean_episode_length", {})
  if not ep:
    return -1, None
  last = max(ep)
  if last < warmup:
    return last, None

  def recent(tag: str) -> float:
    vals = [v for k, v in s.get(tag, {}).items() if k > last - window]
    return sum(vals) / len(vals) if vals else 0.0

  def peak(tag: str) -> float:
    d = s.get(tag, {})
    steps = sorted(d)
    best = 0.0
    for i in range(0, max(1, len(steps) - window + 1), max(1, window // 2)):
      chunk = [d[k] for k in steps[i : i + window]]
      if chunk:
        best = max(best, sum(chunk) / len(chunk))
    return best

  ep_peak, ep_now = (
    peak("Train/mean_episode_length"),
    recent("Train/mean_episode_length"),
  )
  if ep_peak > 500 and ep_now < 0.4 * ep_peak:
    return last, f"EPLEN collapse: {ep_now:.0f} steps vs peak {ep_peak:.0f}"
  k_peak, k_now = peak("Metrics/twist/kicks"), recent("Metrics/twist/kicks")
  if k_peak > 1.0 and k_now < 0.2 * k_peak:
    return last, f"NOKICK: {k_now:.2f} kicks/ep vs peak {k_peak:.2f}"
  spikes = [
    k for k, v in s.get("Loss/value", {}).items() if v > 1.0e3 and k > last - window
  ]
  if spikes:
    return last, f"VALUE spike at {spikes}"
  return last, None


def main() -> None:
  p = argparse.ArgumentParser(description=__doc__)
  p.add_argument("run_dir")
  p.add_argument("--until", type=int, required=True, help="exit at this iteration")
  p.add_argument("--name", required=True, help="the --agent.run-name of the run")
  p.add_argument("--window", type=int, default=40)
  p.add_argument("--warmup", type=int, default=120)
  p.add_argument("--poll", type=float, default=60.0)
  args = p.parse_args()
  while True:
    last, problem = check(args.run_dir, args.window, args.warmup)
    if problem:
      print(f"PROBLEM at iter {last}: {problem}")
      sys.exit(2)
    if last >= args.until:
      print(f"REACHED iter {last}")
      return
    if not _alive(args.name):
      print(f"STOPPED: process for {args.name} is gone (last iter {last})")
      sys.exit(3)
    time.sleep(args.poll)


if __name__ == "__main__":
  main()

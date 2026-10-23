"""Find each run's best checkpoint: the saved model nearest the peak of
smoothed Train/mean_reward. Writes restructure/best.csv."""

import csv, glob, re, sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

REPO = Path(__file__).resolve().parents[1]
WINDOW = 25  # iterations of smoothing
STEP = re.compile(r"model_(\d+)\.pt$")


def best_for(run: str):
  steps, vals = [], []
  for f in sorted(glob.glob(f"{run}/events.out.tfevents*")):
    ea = EventAccumulator(f, size_guidance={"scalars": 0})
    ea.Reload()
    if "Train/mean_reward" in ea.Tags()["scalars"]:
      for e in ea.Scalars("Train/mean_reward"):
        steps.append(e.step)
        vals.append(e.value)
  saved = sorted(int(m.group(1)) for p in glob.glob(f"{run}/model_*.pt") if (m := STEP.search(p)))
  if not steps or not saved:
    return run, None, None, None
  order = np.argsort(steps)
  s, v = np.asarray(steps)[order], np.asarray(vals)[order]
  k = min(WINDOW, len(v))
  smooth = np.convolve(v, np.ones(k) / k, mode="valid")
  peak_i = int(np.argmax(smooth)) + k // 2
  peak_step = int(s[min(peak_i, len(s) - 1)])
  best = min(saved, key=lambda x: abs(x - peak_step))
  return run, peak_step, best, float(smooth.max())


if __name__ == "__main__":
  runs = sorted(glob.glob(str(REPO / "logs/rsl_rl/*/*/")))
  with Pool(12) as pool:
    rows = pool.map(best_for, runs)
  out = REPO / "restructure/best.csv"
  with open(out, "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["run", "peak_iteration", "best_ckpt", "peak_smoothed_reward"])
    for run, peak, best, val in rows:
      if best is not None:
        rel = str(Path(run).relative_to(REPO))
        w.writerow([rel, peak, f"{rel}/model_{best}.pt", f"{val:.3f}"])
  print(sum(r[2] is not None for r in rows), "runs with a best checkpoint ->", out, file=sys.stderr)

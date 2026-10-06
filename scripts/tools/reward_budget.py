"""Reward budget report for a training run (TensorBoard events).

Shows, per window of iterations: episode length, the per-second reward of
staying up (dense terms) vs per-episode event rewards, task metrics, and the
largest reward terms. Flags the failure signatures seen in the kick runs:

- DENSE<0      staying up costs reward (stage3_v2 fell on purpose).
- STAY<0       staying up is worth nothing even with events counted.
- EPLEN        episodes collapsed (falling at once).
- STD          action noise growing fast (v3: noise fed action_rate).
- NOKICK       kicks stopped after having started (v1: hovered near ball).
- VALUE        value-loss spike (sim blow-up or reward explosion).
- STYLE        AMP style active < 50% of the time (v8–v10 drifted unnatural).
- LIMITS       joint-limit penalty grew 3x (motion getting extreme).

  uv run python scripts/tools/reward_budget.py logs/rsl_rl/<exp>/<run>
"""

from __future__ import annotations

import argparse
import glob
import math

from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

EVENT_TERMS = {
  "kick_direction",
  "kick_vel",
  "kick_vel_accurate",
  "kick_goal",
  "kick_lined_up",
  "kick_double_touch",
  "fall",
}


def load(run_dir: str) -> EventAccumulator:
  files = sorted(glob.glob(f"{run_dir}/events*"))
  if not files:
    raise SystemExit(f"no event file in {run_dir}")
  acc = EventAccumulator(files[-1], size_guidance={"scalars": 0})
  acc.Reload()
  return acc


def report(run_dir: str, episode_s: float, windows: int, step_dt: float) -> list[str]:
  acc = load(run_dir)
  tags = set(acc.Tags()["scalars"])
  series = {t: {x.step: x.value for x in acc.Scalars(t)} for t in tags}
  last = max(series["Train/mean_episode_length"])
  first = min(series["Train/mean_episode_length"])

  def mean(tag: str, a: int, b: int) -> float:
    vals = [v for s, v in series.get(tag, {}).items() if a <= s < b]
    return sum(vals) / len(vals) if vals else math.nan

  span = max(1, (last - first + 1) // windows)
  rows, flags = [], []
  prev = None
  print(f"run {run_dir}  iterations {first}..{last}")
  head = (
    f"{'iters':>11} {'ep_s':>5} {'dense/s':>7} {'stay/s':>7} {'ev/ep':>6} {'kicks':>5} "
    f"{'goals':>5} {'falls':>6} {'std':>5} {'see':>4} {'aim':>5} {'v_kick':>6}"
  )
  print(head)
  for a in range(first, last + 1, span):
    b = min(a + span, last + 1)
    ep_s = mean("Train/mean_episode_length", a, b) * step_dt
    dense = event = 0.0
    for t in tags:
      if t.startswith("Episode_Reward/"):
        v = mean(t, a, b) * episode_s
        if t.removeprefix("Episode_Reward/") in EVENT_TERMS:
          event += v
        else:
          dense += v
    dense_s = dense / max(ep_s, 1e-3)
    stay_s = (dense + event) / max(ep_s, 1e-3)
    row = {
      "a": a,
      "b": b - 1,
      "ep_s": ep_s,
      "dense_s": dense_s,
      "stay_s": stay_s,
      "event": event,
      "kicks": mean("Metrics/twist/kicks", a, b),
      "goals": mean("Metrics/twist/goals", a, b),
      "falls": mean("Episode_Termination/illegal_contact", a, b),
      "std": mean("Policy/mean_std", a, b),
      "see": mean("Metrics/twist/see_ball", a, b),
      "aim": mean("Metrics/twist/kick_dir_err", a, b),
      "v_kick": mean("Metrics/twist/kick_speed", a, b),
    }
    rows.append(row)
    print(
      f"{a:5d}-{b - 1:5d} {ep_s:5.1f} {dense_s:+7.2f} {stay_s:+7.2f} {event:+6.0f} "
      f"{row['kicks']:5.2f} {row['goals']:5.2f} {row['falls']:6.2f} {row['std']:5.2f} "
      f"{row['see']:4.2f} {row['aim']:5.2f} {row['v_kick']:6.2f}"
    )
    prev = prev or row
  cur = rows[-1]
  peak_kicks = max((r["kicks"] for r in rows if not math.isnan(r["kicks"])), default=0)
  if cur["dense_s"] < -0.5:
    flags.append(f"DENSE<0: staying up costs {cur['dense_s']:+.2f}/s before events")
  if cur["stay_s"] < 0:
    flags.append(f"STAY<0: staying up is net negative ({cur['stay_s']:+.2f}/s)")
  peak_ep = max(r["ep_s"] for r in rows)
  if peak_ep > 10 and cur["ep_s"] < 0.4 * peak_ep:
    flags.append(f"EPLEN: episodes {cur['ep_s']:.1f}s vs peak {peak_ep:.1f}s")
  if cur["std"] > 1.0 or (len(rows) > 2 and cur["std"] > 1.6 * rows[0]["std"]):
    flags.append(f"STD: action noise {rows[0]['std']:.2f} -> {cur['std']:.2f}")
  if peak_kicks > 1.0 and cur["kicks"] < 0.2 * peak_kicks:
    flags.append(f"NOKICK: kicks {cur['kicks']:.2f}/ep vs peak {peak_kicks:.2f}")
  style_now = mean("Metrics/amp_style_active", cur["a"], cur["b"] + 1)
  if not math.isnan(style_now) and style_now < 0.5:
    flags.append(f"STYLE: AMP style active only {style_now:.0%} of the time")
  lim0 = mean("Episode_Reward/dof_pos_limits", rows[0]["a"], rows[0]["b"] + 1)
  lim1 = mean("Episode_Reward/dof_pos_limits", cur["a"], cur["b"] + 1)
  if lim0 < 0 and lim1 < 3 * lim0:
    flags.append(f"LIMITS: joint-limit penalty {lim0:.3f} -> {lim1:.3f}")
  value = series.get("Loss/value", {})
  spikes = [s for s, v in value.items() if v > 1.0e3]
  if spikes:
    flags.append(f"VALUE: value-loss spikes at {spikes[:5]}")

  a, b = rows[0]["a"], rows[0]["b"] + 1
  c, d = cur["a"], cur["b"] + 1
  terms = []
  for t in tags:
    if t.startswith("Episode_Reward/"):
      x, y = mean(t, a, b) * episode_s, mean(t, c, d) * episode_s
      terms.append((abs(y), t.removeprefix("Episode_Reward/"), x, y))
  print(f"largest terms per episode, iters {a}-{b - 1} -> {c}-{d - 1}:")
  for _, name, x, y in sorted(terms, reverse=True)[:10]:
    print(f"  {name:26s} {x:+8.2f} -> {y:+8.2f}")
  print("flags:", "; ".join(flags) if flags else "none")
  return flags


def main() -> None:
  p = argparse.ArgumentParser(description=__doc__)
  p.add_argument("run_dir")
  p.add_argument("--episode-s", type=float, default=30.0)
  p.add_argument("--windows", type=int, default=6)
  p.add_argument("--step-dt", type=float, default=0.02)
  args = p.parse_args()
  report(args.run_dir, args.episode_s, args.windows, args.step_dt)


if __name__ == "__main__":
  main()

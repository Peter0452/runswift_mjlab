"""Per-term training curves of a run (TensorBoard scalars), summarised for the
verdict and the designer: each reward term's mean over the first and last 10 %
of the run, and a PNG of the terms a proposal edited.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PREFIXES = ("Episode_Reward/", "Metrics/", "Train/mean_reward", "Loss/")


def scalars(run_dir: Path) -> dict[str, list[tuple[int, float]]]:
  from tensorboard.backend.event_processing.event_accumulator import (
    EventAccumulator,
  )

  out: dict[str, list[tuple[int, float]]] = {}
  for f in sorted(run_dir.glob("events.out.tfevents.*")):
    acc = EventAccumulator(str(f), size_guidance={"scalars": 0})
    acc.Reload()
    for tag in acc.Tags()["scalars"]:
      if tag.startswith(PREFIXES):
        out.setdefault(tag, []).extend((e.step, e.value) for e in acc.Scalars(tag))
  return {k: sorted(v) for k, v in out.items()}


def summarize(series: dict[str, list[tuple[int, float]]]) -> dict[str, dict[str, Any]]:
  out = {}
  for tag, pts in series.items():
    if len(pts) < 2:
      continue
    n = max(1, len(pts) // 10)
    first = sum(v for _, v in pts[:n]) / n
    last = sum(v for _, v in pts[-n:]) / n
    out[tag] = {
      "first": round(first, 5),
      "last": round(last, 5),
      "change": round(last - first, 5),
      "steps": [pts[0][0], pts[-1][0]],
    }
  return out


def edited_terms(recipe: dict[str, Any], champion_recipe: dict[str, Any]) -> list[str]:
  """Reward terms whose weight the child changed (genes w.<term>, rewards.<term>)."""
  terms = []
  for src in ("genes", "rewards"):
    a, b = recipe.get(src) or {}, champion_recipe.get(src) or {}
    for k, v in a.items():
      if b.get(k) != v:
        terms.append(k[2:] if src == "genes" and k.startswith("w.") else k)
  return [t for t in terms if "." not in t]


def write(run_dir: Path, focus: list[str]) -> dict[str, Any]:
  """curves.json (+ curves.png of the focus terms) in the run directory."""
  series = scalars(run_dir)
  summary = summarize(series)
  (run_dir / "curves.json").write_text(json.dumps(summary, indent=1))
  tags = [f"Episode_Reward/{t}" for t in focus if f"Episode_Reward/{t}" in series]
  tags += [t for t in ("Train/mean_reward",) if t in series]
  if tags:
    try:
      import matplotlib

      matplotlib.use("Agg")
      import matplotlib.pyplot as plt

      fig, axes = plt.subplots(
        len(tags), 1, figsize=(7, 2.2 * len(tags)), squeeze=False
      )
      for ax, tag in zip(axes[:, 0], tags, strict=True):
        steps, vals = zip(*series[tag], strict=True)
        ax.plot(steps, vals, lw=1)
        ax.set_title(tag, fontsize=9)
      fig.tight_layout()
      fig.savefig(run_dir / "curves.png", dpi=90)
      plt.close(fig)
    except ImportError:
      pass
  missing = [t for t in focus if f"Episode_Reward/{t}" not in series]
  return {
    "file": str(run_dir / "curves.json"),
    "focus": {t: summary.get(f"Episode_Reward/{t}") for t in focus},
    "missing_terms": missing,
    "mean_reward": summary.get("Train/mean_reward"),
  }

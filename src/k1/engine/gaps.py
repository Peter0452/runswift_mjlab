"""Measured gaps: where the champion falls short, as data the designers and
literature reviews can act on.

Kick (the only task with a wrapped judge): from the champion's full benchmark
v2 result,

- **vs B-Human**: every kick-league metric (``fitness_v2.BHUMAN``) where
  B-Human is better than us (point estimates), sized in units of the metric's
  fitness tolerance;
- **safety**: every fall metric in ``fitness_v2.METRICS`` that is above zero
  (the kick request's S1 target is 0 falls), sized the same way.

Each gap carries goal tags from ``knowledge/approaches/symptoms.yaml`` (metric
tags + situation words) and the request requirement it belongs to; ``weight``
ranks gaps (size x requirement priority: safety 2, primary 3, rest 1).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from k1.approaches import knowledge

ROOT = Path(__file__).resolve().parents[3]
PRIORITY_WEIGHT = {"S": 2.0, "P": 3.0, "Q": 1.0}


@dataclass(frozen=True)
class Gap:
  key: str  # benchmark situation, e.g. "close_any/camera/typical"
  metric: str
  cap: str  # "low" / "high" speed caps
  ours: float
  ref: float  # B-Human, or the target (0 falls)
  reference: str  # "bhuman" or "target"
  size: float  # how far behind, in units of the metric's tolerance (> 0)
  requirement: str | None
  tags: tuple[str, ...] = field(default_factory=tuple)
  extra_tags: tuple[str, ...] = field(default_factory=tuple)  # half-weight tags

  @property
  def weight(self) -> float:
    prio = PRIORITY_WEIGHT.get((self.requirement or "Q")[0], 1.0)
    return self.size * prio

  def describe(self) -> str:
    vs = "B-Human" if self.reference == "bhuman" else "target"
    return (
      f"{self.metric} in {self.key} ({self.cap} caps): ours {self.ours:.3g}, "
      f"{vs} {self.ref:.3g} ({self.size:.1f} tol behind; {self.requirement})"
    )


def _tags(family: str, key: str, metric: str) -> tuple[tuple, tuple, str | None]:
  spec = knowledge.symptoms().get(family, {})
  entry = (spec.get("metrics") or {}).get(metric, {"tags": [], "requirement": None})
  tags = list(entry["tags"])
  for word, extra in (spec.get("situations") or {}).items():
    if word in key.split("/"):
      tags += [t for t in extra if t not in tags]
  req = entry.get("requirement")
  primary = req is not None and req.startswith("P")
  extra = tuple(spec.get("primary_extra") or []) if primary else ()
  return tuple(tags), tuple(t for t in extra if t not in tags), req


def kick_gaps(result: dict, bhuman: dict | None, fitness: Any) -> list[Gap]:
  """Gaps of a benchmark v2 result (``fitness`` is the fitness_v2 module)."""
  tol = {(k, m): t for k, m, _, t, _ in fitness.METRICS}
  gaps: list[Gap] = []
  if bhuman:
    for key, metric, hib in fitness.BHUMAN:
      for cap in fitness.CAPS:
        a, b = (
          fitness._get(result, key, metric, cap),
          fitness._get(bhuman, key, metric, cap),
        )
        if not a or not b:
          continue
        behind = (b[0] - a[0]) if hib else (a[0] - b[0])
        if behind <= 0:
          continue
        t = tol.get((key, metric)) or abs(b[0]) * 0.05 or 1.0
        tags, extra, req = _tags("kick", key, metric)
        gaps.append(
          Gap(key, metric, cap, a[0], b[0], "bhuman", behind / t, req, tags, extra)
        )
  for key, metric, _, t, _ in fitness.METRICS:
    if not metric.startswith("fall_pct"):
      continue
    for cap in fitness.CAPS:
      a = fitness._get(result, key, metric, cap)
      if a and a[0] > 0:
        tags, extra, req = _tags("kick", key, metric)
        gaps.append(
          Gap(key, metric, cap, a[0], 0.0, "target", a[0] / t, req, tags, extra)
        )
  return sorted(gaps, key=lambda g: -g.weight)


def champion_gaps(task: str, bench: str | Path | None = None) -> list[Gap]:
  """Gaps of the champion (or of a given benchmark JSON) for a task family."""
  from k1.eval import judges

  judge = judges.judge_for(task)
  if judge is None or not judge.wrapped:
    return []
  path = Path(bench) if bench else judges.KICK_REFERENCE[("full", 1)]
  result = json.loads((ROOT / path).read_text())
  bh = json.loads(judges.BHUMAN.read_text()) if judges.BHUMAN.is_file() else None
  return kick_gaps(result, bh, judges._fitness())

"""Inner loop: population-based training (PBT) of one recipe.

A population of 4-8 copies of one recipe trains with a pinned seed; every
50-100 iterations each member gets a quick screen score. Weak members take the
weights and numbers of strong ones (exploit) and nudge the numbers (explore).
Only continuous numbers inside the recipe's declared ranges change; the recipe's
structure (methods, rewards present, task) never does, so the population stays
one design. PB2 (a bandit over the numbers instead of random nudges) can replace
``explore`` with the same interface.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Member:
  name: str
  params: dict[str, float]
  checkpoint: str | None = None
  score: float | None = None  # None = not screened or ungradable
  lineage: list[str] = field(default_factory=list)


def exploit(
  population: list[Member], fraction: float = 0.25
) -> list[tuple[Member, Member]]:
  """(weak, strong) pairs: each of the bottom ``fraction`` copies one of the top.
  Ungradable members count as the weakest."""
  ranked = sorted(population, key=lambda m: -1e18 if m.score is None else m.score)
  n = max(1, int(len(population) * fraction))
  weak, strong = ranked[:n], ranked[-n:]
  return [
    (w, strong[i % len(strong)]) for i, w in enumerate(weak) if w is not strong[0]
  ]


def explore(
  params: dict[str, float],
  ranges: dict[str, tuple[float, float]],
  rng: random.Random,
  factors: tuple[float, float] = (0.8, 1.25),
) -> dict[str, float]:
  """Multiply each tunable number by one of ``factors``, clipped to its range."""
  out = dict(params)
  for key, (lo, hi) in ranges.items():
    out[key] = min(hi, max(lo, params[key] * rng.choice(factors)))
  return out


def step(
  population: list[Member],
  ranges: dict[str, tuple[float, float]],
  rng: random.Random,
) -> list[dict[str, Any]]:
  """One exploit/explore round, in place; returns what changed (for the log)."""
  changes = []
  for weak, strong in exploit(population):
    new_params = explore(strong.params, ranges, rng)
    changes.append(
      {
        "member": weak.name,
        "copied": strong.name,
        "from": weak.params,
        "to": new_params,
      }
    )
    weak.checkpoint = strong.checkpoint
    weak.params = new_params
    weak.score = None
    weak.lineage.append(strong.name)
  return changes

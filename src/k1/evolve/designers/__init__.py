"""Designers propose recipes. Each returns ``Proposal`` objects: a full recipe
(dict, as in experiments/recipes) plus the one change it makes and why.

Built-in, deterministic designers (no LLM): ``method`` (enable / tune a
registered experimental method) and ``genes`` (nudge one continuous recipe
number). Others from the architecture (reward grammar, constraint, scenario/DR,
task, LLM front-end) plug in by the same interface.
"""

from __future__ import annotations

import copy
import random
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class Proposal:
  recipe: dict[str, Any]
  change: str
  why: str
  designer: str


class Designer(Protocol):
  name: str

  def propose(
    self, champion: dict[str, Any], history: list[dict[str, Any]], rng: random.Random
  ) -> list[Proposal]: ...


def _tried(history: list[dict[str, Any]]) -> set[str]:
  return {h.get("change", "") for h in history}


class GeneDesigner:
  """Nudge one continuous gene of the champion's recipe by x0.8 or x1.25,
  skipping changes already tried (distinct from history)."""

  name = "genes"

  def __init__(self, genes: dict[str, tuple[float, float]]) -> None:
    self.genes = genes  # gene -> allowed (low, high)

  def propose(self, champion, history, rng):
    tried = _tried(history)
    out = []
    for gene in rng.sample(sorted(self.genes), len(self.genes)):
      lo, hi = self.genes[gene]
      cur = float(champion["recipe"].get("genes", {}).get(gene, (lo + hi) / 2))
      for factor in rng.sample([0.8, 1.25], 2):
        new = min(hi, max(lo, cur * factor))
        change = f"genes.{gene}: {cur:g} -> {new:g}"
        if new == cur or change in tried:
          continue
        recipe = copy.deepcopy(champion["recipe"])
        recipe.setdefault("genes", {})[gene] = new
        out.append(
          Proposal(
            recipe, change, f"one-gene step x{factor} within [{lo}, {hi}]", self.name
          )
        )
        break
      if out:
        break
    return out


class MethodDesigner:
  """Turn one registered experimental, training-only method on or off in the
  champion's recipe (the method's card says what it does)."""

  name = "method"

  def __init__(self, candidates: dict[str, dict[str, Any] | bool]) -> None:
    self.candidates = candidates  # method -> params to switch to (False = off)

  def propose(self, champion, history, rng):
    from k1.methods import METHODS

    tried = _tried(history)
    for name in rng.sample(sorted(self.candidates), len(self.candidates)):
      m = METHODS[name]
      if m.impact != "training-only" or m.status in ("rejected", "parked"):
        continue
      target = self.candidates[name]
      current = champion["recipe"].get("methods", {}).get(name, False)
      if current == target:
        continue
      change = f"methods.{name}: {current!r} -> {target!r}"
      if change in tried:
        continue
      recipe = copy.deepcopy(champion["recipe"])
      recipe.setdefault("methods", {})[name] = target
      return [
        Proposal(
          recipe, change, f"{m.title} ({m.status}); see {m.card.name}", self.name
        )
      ]
    return []

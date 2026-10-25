"""The approach designer: reads the champion's measured gaps, looks up its
options in the knowledge base, and proposes the move most likely to close the
biggest gap. Deterministic rules over the knowledge, not an LLM; the knowledge
it reads is written by people and literature reviews (``rsw review``).

Two kinds of move:

- **add**: switch on an approach the champion doesn't use yet (the card's
  ``trial``), e.g. ball-behind starts, DecAP, multi-critic;
- **tune**: step one parameter of an approach that is already on (the card's
  ``tune``: range + tags per parameter) by x0.8 or x1.25 within its range, e.g.
  the AMP style weight or a reward-shaping weight.

Combination comes from stacking: each promoted child becomes the champion, so
AMP + reward shaping + a scenario + ... accumulate one verified change at a
time (standing decision 2026-10-21: one change per run, judged against a
same-length control). ``combine`` > 1 bundles that many moves on different
approaches into one child; it stays 1 unless the user allows multi-change runs.

Ranking, per (gap, move): tag match (the gap's tags 1, a primary gap's extra
tags 0.5) x (status weight: adopted 1, experimental 0.8, trial 0.8, candidate
0.6, + our track record on this task: uses +0.5 positive, -0.5 negative) x gap
weight; tune moves x0.9; x0.5 per earlier try of the same approach, so tries
spread over approaches. A tune parameter's ``step`` (up / down / both, in
magnitude) says which way helps its tags. Approved review shortlists rank
before every tag
match. Rejected and parked approaches are skipped. Matching approaches the
engine can't apply (no ``trial``/``tune``, or runtime) go to ``blocked``.
"""

from __future__ import annotations

import copy
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from k1.approaches import knowledge
from k1.engine.designers import Proposal
from k1.engine.gaps import Gap

STATUS_WEIGHT = {"adopted": 1.0, "experimental": 0.8, "trial": 0.8, "candidate": 0.6}
LOWER_IS_BETTER = (
  "first_kick_cens", "action_rate", "touchdown_speed", "landing_force",
  "short_stop_m", "torque_sat_pct",
)  # fmt: skip


@dataclass
class Move:
  score: float
  gap: Gap
  card: Any
  kind: str  # "add" | "tune"
  edits: dict[str, Any]  # path ("methods.x.p" / "methods.x" / "genes.g") -> value
  shortlisted: bool = False

  def change(self, recipe: dict[str, Any]) -> str:
    parts = [f"{p}: {_get(recipe, p)!r} -> {v!r}" for p, v in self.edits.items()]
    return f"{self.kind} {self.card.id}: " + "; ".join(parts)


def _get(recipe: dict[str, Any], path: str) -> Any:
  kind, rest = path.split(".", 1)
  if kind == "genes":
    return (recipe.get("genes") or {}).get(rest)
  name, _, param = rest.partition(".")
  entry = (recipe.get("methods") or {}).get(name, False)
  if not param:
    return entry
  return entry.get(param) if isinstance(entry, dict) else None


def _apply(recipe: dict[str, Any], edits: dict[str, Any]) -> dict[str, Any]:
  out = copy.deepcopy(recipe)
  for path, value in edits.items():
    kind, rest = path.split(".", 1)
    if kind == "genes":
      out.setdefault("genes", {})[rest] = value
      continue
    name, _, param = rest.partition(".")
    methods = out.setdefault("methods", {})
    entry = methods.get(name)
    base = entry if isinstance(entry, dict) else {}
    methods[name] = {**base, **value} if not param else {**base, param: value}
  return out


def _trial_edits(recipe: dict[str, Any], trial: dict[str, Any]) -> dict[str, Any]:
  """The trial's edits that change the recipe (method params merged)."""
  edits: dict[str, Any] = {}
  for name, params in (trial.get("methods") or {}).items():
    entry = (recipe.get("methods") or {}).get(name)
    base = entry if isinstance(entry, dict) else {}
    if not isinstance(entry, dict) or any(base.get(k) != v for k, v in params.items()):
      edits[f"methods.{name}"] = {**base, **params}
  for gene, value in (trial.get("genes") or {}).items():
    if (recipe.get("genes") or {}).get(gene) != value:
      edits[f"genes.{gene}"] = value
  return edits


def _track_record(approach: str, family: str) -> float:
  score = {"positive": 0.5, "negative": -0.5}
  return sum(score.get(u["result"], 0.0) for u in knowledge.uses_of(approach)
             if u["task"] == family)  # fmt: skip


def _match(tags: set[str], gap: Gap) -> float:
  return len(tags & set(gap.tags)) + 0.5 * len(tags & set(gap.extra_tags))


class ApproachDesigner:
  name = "approach"

  def __init__(
    self,
    task_family: str,
    gaps: Callable[[dict[str, Any]], list[Gap]],
    combine: int = 1,
  ) -> None:
    self.family = task_family
    self.gaps = gaps  # champion -> ranked gaps
    self.combine = combine  # moves per child; 1 = one change per run
    self.blocked: list[str] = []

  def moves(
    self,
    champion: dict[str, Any],
    rng: random.Random,
    history: Sequence[dict[str, Any]] = (),
  ) -> list[Move]:
    """Every add and tune move for every gap, best first."""
    recipe = champion["recipe"]
    tries: dict[str, int] = {}
    for h in history:  # earlier children's changes: "add <card>: ..." etc.
      for part in h.get("change", "").split(" + "):
        words = part.split(" ", 2)
        if len(words) > 1 and words[0] in ("add", "tune"):
          card_id = words[1].rstrip(":")
          tries[card_id] = tries.get(card_id, 0) + 1
    shortlisted = {e["approach"] for e in knowledge.approved_shortlist(self.family)}
    out, blocked = [], set()
    for gap in self.gaps(champion):
      for card in knowledge.cards().values():
        m = card.meta
        if m["status"] in ("rejected", "parked"):
          continue
        short = card.id in shortlisted
        if m["impact"] == "runtime" or (m["trial"] is None and not m["tune"]):
          if _match(set(m["tags"]), gap) and m["status"] != "adopted":
            blocked.add(card.id)
          continue
        prior = STATUS_WEIGHT.get(m["status"], 0.5) + _track_record(
          card.id, self.family
        )
        prior *= 0.5 ** tries.get(card.id, 0)  # spread tries over approaches
        if m["trial"] is not None:
          edits = _trial_edits(recipe, m["trial"])
          match = _match(set(m["tags"]), gap)
          if edits and (match or short):
            score = max(match, 0.25) * prior * gap.weight
            out.append(Move(score, gap, card, "add", edits, short))
        for path, spec in (m["tune"] or {}).items():
          match = _match(set(spec.get("tags", [])), gap)
          current = _get(recipe, path)
          if not (match or short) or not isinstance(current, int | float):
            continue  # not relevant, or the approach is not on
          lo, hi = spec["range"]
          # step: which way helps the listed tags, in magnitude (a penalty's
          # "up" is more negative); "both" when the knowledge doesn't say.
          factors = {"up": [1.25], "down": [0.8]}.get(spec.get("step"), [0.8, 1.25])
          for factor in rng.sample(factors, len(factors)):
            new = round(min(hi, max(lo, current * factor)), 6)
            if new != current:
              score = max(match, 0.25) * prior * gap.weight * 0.9
              out.append(Move(score, gap, card, "tune", {path: new}, short))
    self.blocked = sorted(blocked)
    return sorted(out, key=lambda mv: (not mv.shortlisted, -mv.score))

  def propose(
    self, champion: dict[str, Any], history: list[dict[str, Any]], rng: random.Random
  ) -> list[Proposal]:
    tried = {h.get("change", "") for h in history}
    recipe = champion["recipe"]
    chosen: list[Move] = []
    for mv in self.moves(champion, rng, history):
      if mv.change(recipe) in tried or any(c.card.id == mv.card.id for c in chosen):
        continue
      chosen.append(mv)
      if len(chosen) == self.combine:
        break
    if not chosen:
      return []
    merged = _apply(recipe, {p: v for mv in chosen for p, v in mv.edits.items()})
    change = " + ".join(mv.change(recipe) for mv in chosen)
    why, hyp = [], []
    for mv in chosen:
      g, c = mv.gap, mv.card
      evidence = "; ".join(f"{u['id']} {u['result']}" for u in knowledge.uses_of(c.id))
      why.append(
        f"gap {g.describe()} -> {mv.kind} {c.id} ({c.meta['element']}, "
        f"{c.meta['status']}); evidence: {evidence or 'no uses yet'}; see {c.path.name}"
      )
      lower = g.reference == "target" or g.metric in LOWER_IS_BETTER
      hyp.append(
        f"{c.id} ({mv.kind}) moves {g.metric} in {g.key} "
        f"{'lower' if lower else 'higher'} than the champion's {g.ours:.3g} by at "
        "least one tolerance"
      )
    hypothesis = " and ".join(hyp) + ", with no regression elsewhere"
    return [Proposal(merged, change, " | ".join(why), self.name, hypothesis)]

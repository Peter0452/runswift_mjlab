"""The LLM designer as seen by the engine: it reads candidate proposals that the
LLM agent wrote into the inbox (``k1/engine/design.py``), checks each against
the current champion and history, and hands the valid one with the highest
expected benchmark gain to the engine (``k1/engine/worth.py``). Invalid ones,
including those not worth a kick retrain, are filed in ``proposals/rejected/``
with the reasons; ``kind: new`` ones (need building) in ``proposals/build/``.

When the inbox is empty it can ask the LLM agent itself (``ask``, e.g.
``design.ask_llm``: ``claude -p /design``), at most once per ``ask_every``
seconds and ``max_asks`` times per engine run. Otherwise it proposes nothing
and the engine moves on.
"""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from typing import Any

import yaml

from k1.engine import design, worth
from k1.engine.designers import Proposal
from k1.engine.gaps import Gap


class InboxDesigner:
  name = "llm"
  priority = True  # the engine asks it first, every step

  def __init__(
    self,
    allow_combine: bool = False,
    gaps: Callable[[dict[str, Any]], list[Gap]] | None = None,
    min_gain: float = worth.MIN_GAIN,
    ask: Callable[[], str] | None = None,
    ask_every: float = 3600.0,
    max_asks: int = 6,
  ) -> None:
    self.allow_combine = allow_combine
    self.gaps = gaps
    self.min_gain = min_gain
    self.ask = ask
    self.ask_every = ask_every
    self.max_asks = max_asks
    self.asks: list[float] = []
    self.log: list[str] = []
    self.empty = False
    # Set by the engine every step (outer.step).
    self.ceilings: list[str] = []
    self.calibration = 1.0
    self.history: list[dict[str, Any]] = []

  def propose(
    self, champion: dict[str, Any], history: list[dict[str, Any]], rng: random.Random
  ) -> list[Proposal]:
    self.empty = False
    best = self._best(champion, history)
    if best is None and self._may_ask():
      self.asks.append(time.time())
      self.log.append(f"asked the LLM designer: {self.ask()}")  # type: ignore[misc]
      best = self._best(champion, history)
    if best is None:
      self.empty = True  # nothing worth a run this step: the engine moves on
      return []
    path, p, gain = best
    design.file_away(path, design.USED)
    return [design.to_proposal(p, champion, gain, self.history or history)]

  def _may_ask(self) -> bool:
    if self.ask is None or len(self.asks) >= self.max_asks:
      return False
    return not self.asks or time.time() - self.asks[-1] >= self.ask_every

  def _best(self, champion, history):
    gaps = self.gaps(champion) if self.gaps else None
    valid = []
    for path in design.inbox():
      try:
        p = yaml.safe_load(path.read_text()) or {}
      except yaml.YAMLError as e:
        design.file_away(path, design.REJECTED, f"not YAML: {e}")
        continue
      full = self.history or history
      problems = design.check(
        p, champion, full, self.allow_combine, gaps, self.min_gain,
        self.ceilings, self.calibration,
      )  # fmt: skip
      if problems:
        design.file_away(path, design.REJECTED, "\n".join(problems))
        self.log.append(f"rejected {path.name}: {problems[0]}")
        continue
      if p["kind"] == "new":
        design.file_away(path, design.BUILD)
        self.log.append(f"build request {path.name}: {p['approaches']}")
        continue
      parent = design._parent_entry(p, full)
      est = design.estimate(p, gaps, self.min_gain, self.calibration, parent)
      valid.append((path, p, est.gain))
    return max(valid, key=lambda v: v[2]) if valid else None

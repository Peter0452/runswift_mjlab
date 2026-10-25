"""The LLM designer as seen by the engine: it reads candidate proposals that the
LLM agent wrote into the inbox (``k1/engine/design.py``), checks each against
the current champion and history, and hands valid ones to the engine. Invalid
ones are filed in ``proposals/rejected/`` with the reasons; ``kind: new`` ones
(need building) in ``proposals/build/``. When the inbox is empty it proposes
nothing and the engine falls back to the next designer (the deterministic
approach designer).
"""

from __future__ import annotations

import random
from typing import Any

import yaml

from k1.engine import design
from k1.engine.designers import Proposal


class InboxDesigner:
  name = "llm"
  priority = True  # the engine asks it first, every step

  def __init__(self, allow_combine: bool = False) -> None:
    self.allow_combine = allow_combine
    self.log: list[str] = []
    self.empty = False

  def propose(
    self, champion: dict[str, Any], history: list[dict[str, Any]], rng: random.Random
  ) -> list[Proposal]:
    self.empty = False
    for path in design.inbox():
      try:
        p = yaml.safe_load(path.read_text()) or {}
      except yaml.YAMLError as e:
        design.file_away(path, design.REJECTED, f"not YAML: {e}")
        continue
      problems = design.check(p, champion, history, self.allow_combine)
      if problems:
        design.file_away(path, design.REJECTED, "\n".join(problems))
        self.log.append(f"rejected {path.name}: {problems[0]}")
        continue
      if p["kind"] == "new":
        design.file_away(path, design.BUILD)
        self.log.append(f"build request {path.name}: {p['approaches']}")
        continue
      design.file_away(path, design.USED)
      return [design.to_proposal(p, champion)]
    self.empty = True  # nothing left this step: the engine moves on
    return []

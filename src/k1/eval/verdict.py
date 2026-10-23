"""The verdict: one fixed shape for every judgement of a run, appended to its
``run.json``.

``status`` says whether the run could be judged at all. Only ``scored`` verdicts
carry a ``score``; anything that could not be graded has ``score = None``,
never 0, so a crashed or diverged child can't look like a neutral result.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any

STATUSES = ("smoke_failed", "parity_failed", "train_failed", "diverged", "scored")


@dataclass
class Verdict:
  judge: str
  status: str
  checkpoint: str
  score: float | None = None
  regressions: list[str] = field(default_factory=list)
  metrics: dict[str, Any] = field(default_factory=dict)
  # Behaviour checklist (falls, posture, technique, reward hacking, deployed
  # path, peak vs final): name -> True (ok) / False (problem) / None (unchecked).
  checklist: dict[str, bool | None] = field(default_factory=dict)
  findings: list[str] = field(default_factory=list)
  reference: str | None = None
  # Confirmed on a second seed against the reference's second seed, as the
  # evolution loop's confirm_and_install does: one run is not enough to promote.
  confirmed: bool = False
  created: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S"))
  kind: str = "judge"

  def __post_init__(self) -> None:
    if self.status not in STATUSES:
      raise ValueError(f"status must be one of {STATUSES}, got {self.status!r}")
    if self.status != "scored" and self.score is not None:
      raise ValueError("only scored verdicts carry a score (ungradable is not 0)")
    if self.status == "scored" and self.score is None:
      raise ValueError("a scored verdict needs a score")

  @property
  def promotable(self) -> bool:
    """Scored, better than the reference, no regressions, confirmed on a second
    seed (identical re-runs of the champion score up to about +30 on one seed)."""
    return (
      self.status == "scored"
      and (self.score or 0) > 0
      and not self.regressions
      and self.confirmed
    )

  def to_dict(self) -> dict[str, Any]:
    return asdict(self)

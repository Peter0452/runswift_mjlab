"""Hold still for a duration. Skills only write ``MotionCommand``."""
from __future__ import annotations

import time
from dataclasses import dataclass

from action.types import MotionCommand
from skills.base import Skill, SkillProgress, SkillStatus


@dataclass(frozen=True)
class StandRequest:
    duration_sec: float = 2.0


class Stand(Skill):
    def __init__(self) -> None:
        self._started_at: float | None = None

    def on_enter(self, request: StandRequest) -> None:
        self._started_at = time.monotonic()

    def on_exit(self) -> None:
        self._started_at = None

    def tick(
        self,
        request: StandRequest,
        command: MotionCommand,
    ) -> SkillProgress:
        command.stop_body()
        if self._started_at is None:
            self._started_at = time.monotonic()
        elapsed = time.monotonic() - self._started_at
        if elapsed >= request.duration_sec:
            return SkillProgress(status=SkillStatus.SUCCEEDED, progress=1.0, reason="held")
        progress = 0.0 if request.duration_sec <= 0.0 else min(1.0, elapsed / request.duration_sec)
        return SkillProgress(status=SkillStatus.RUNNING, progress=progress, reason="holding")

"""Skill base types. Skills write ``MotionCommand``; they never call the vendor SDK."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from enum import Enum, auto
from typing import Any

from action.types import MotionCommand
from runswift_types import Point2, Pose2

__all__ = [
    "Point2",
    "Pose2",
    "Skill",
    "SkillProgress",
    "SkillStatus",
    "request_with_robot",
]


class SkillStatus(Enum):
    RUNNING = auto()
    SUCCEEDED = auto()
    FAILED = auto()


@dataclass
class SkillProgress:
    status: SkillStatus
    progress: float = 0.0
    reason: str = ""


def request_with_robot(request: Any, pose: Pose2) -> Any:
    """Copy ``pose`` onto a request that has a ``robot_pose`` field."""
    if not hasattr(request, "robot_pose"):
        return request
    return replace(request, robot_pose=pose)


class Skill(ABC):
    def on_enter(self, request: Any) -> None:
        return None

    def on_exit(self) -> None:
        return None

    @abstractmethod
    def tick(self, request: Any, command: MotionCommand) -> SkillProgress:
        """Fill ``command`` for this tick from ``request`` only. No vendor I/O."""

    def cancel(self, command: MotionCommand) -> None:
        command.stop_body()

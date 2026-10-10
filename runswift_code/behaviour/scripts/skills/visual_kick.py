"""Compute visual-kick direction and robot-frame ball. No vendor I/O."""
from __future__ import annotations

import time
from dataclasses import dataclass
from math import atan2, cos, sin

from action.types import MotionCommand
from skills.base import Point2, Pose2, Skill, SkillProgress, SkillStatus
from skills.walk_to_pose import wrap_pi


@dataclass(frozen=True)
class VisualKickRequest:
    """Kick facts this tick. ``robot_pose`` is the robot now; ball and target are world points."""

    robot_pose: Pose2
    ball: Point2
    target: Point2
    power: float
    duration_sec: float = 3.0


@dataclass(frozen=True)
class VisualKickReference:
    direction: float
    power: float
    ball_x: float
    ball_y: float


def world_to_robot(dx: float, dy: float, yaw: float) -> tuple[float, float]:
    return (
        dx * cos(yaw) + dy * sin(yaw),
        -dx * sin(yaw) + dy * cos(yaw),
    )


def kick_direction_robot(
    ball_x: float,
    ball_y: float,
    target_x: float,
    target_y: float,
    robot_yaw: float,
) -> float:
    """Yaw from ball to target, in the robot frame. 0 forward, left positive."""
    return wrap_pi(atan2(target_y - ball_y, target_x - ball_x) - robot_yaw)


def visual_kick_reference(request: VisualKickRequest) -> VisualKickReference:
    robot = request.robot_pose
    ball = request.ball
    target = request.target
    direction = kick_direction_robot(
        ball.x,
        ball.y,
        target.x,
        target.y,
        robot.theta,
    )
    ball_x, ball_y = world_to_robot(
        ball.x - robot.x,
        ball.y - robot.y,
        robot.theta,
    )
    return VisualKickReference(
        direction=direction,
        power=float(request.power),
        ball_x=ball_x,
        ball_y=ball_y,
    )


class VisualKick(Skill):
    def __init__(self) -> None:
        self._started_at: float | None = None
        self.reference: VisualKickReference | None = None

    def on_enter(self, request: VisualKickRequest) -> None:
        self._started_at = time.monotonic()
        self.reference = None

    def on_exit(self) -> None:
        self._started_at = None
        self.reference = None

    def tick(
        self,
        request: VisualKickRequest,
        command: MotionCommand,
    ) -> SkillProgress:
        command.stop_body()
        self.reference = visual_kick_reference(request)
        if self._started_at is None:
            self._started_at = time.monotonic()
        elapsed = time.monotonic() - self._started_at
        if elapsed >= request.duration_sec:
            return SkillProgress(status=SkillStatus.SUCCEEDED, progress=1.0, reason="held")
        progress = (
            0.0 if request.duration_sec <= 0.0 else min(1.0, elapsed / request.duration_sec)
        )
        return SkillProgress(status=SkillStatus.RUNNING, progress=progress, reason="kicking")

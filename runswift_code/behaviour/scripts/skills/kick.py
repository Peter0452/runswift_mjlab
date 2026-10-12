"""Kick skill: stop the body and write visual-kick intent onto ``MotionCommand``.

Uses ``VisualKick`` as a subskill for direction / robot-frame ball. Does not
enable vendor kick mode; the executive does that on enter/exit.
"""
from __future__ import annotations

from dataclasses import dataclass

from action.types import MotionCommand
from skills.base import Point2, Pose2, Skill, SkillProgress
from skills.visual_kick import VisualKick, VisualKickReference, VisualKickRequest


@dataclass(frozen=True)
class KickRequest:
    """Kick this tick. ``robot_pose`` is the robot; ball and target are world points."""

    robot_pose: Pose2
    ball: Point2
    target: Point2
    power: float


def _visual_request(request: KickRequest) -> VisualKickRequest:
    return VisualKickRequest(
        robot_pose=request.robot_pose,
        ball=request.ball,
        target=request.target,
        power=request.power,
        duration_sec=1e9,
    )


class Kick(Skill):
    def __init__(self) -> None:
        self._visual = VisualKick()
        self.reference: VisualKickReference | None = None

    def on_enter(self, request: KickRequest) -> None:
        self.reference = None
        self._visual.on_enter(_visual_request(request))

    def on_exit(self) -> None:
        self.reference = None
        self._visual.on_exit()

    def tick(
        self,
        request: KickRequest,
        command: MotionCommand,
    ) -> SkillProgress:
        progress = self._visual.tick(_visual_request(request), command)
        self.reference = self._visual.reference
        if self.reference is not None:
            command.set_kick(
                self.reference.direction,
                self.reference.power,
                self.reference.ball_x,
                self.reference.ball_y,
            )
        return progress

    def cancel(self, command: MotionCommand) -> None:
        command.stop_body()
        command.clear_kick()
        self._visual.cancel(command)

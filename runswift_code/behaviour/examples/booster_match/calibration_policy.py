"""Replaceable policy interface and the existing native K1 calibration candidate."""

from dataclasses import dataclass
from math import cos, sin
from typing import Protocol


@dataclass(frozen=True)
class PolicyStep:
    """Policy output; completion is independently measured by the evaluator."""

    stage: str
    velocity: tuple = (0.0, 0.0, 0.0)
    head: tuple = (0.45, 0.0, 1.2, 1.2)
    kick: tuple | None = None
    status: str = "running"
    reason: str = ""


class CalibrationPolicy(Protocol):
    def tick(self, context, motion, elapsed_s: float) -> PolicyStep:
        """Use only supplied world context, SDK feedback and fixture elapsed time."""

    def cancel(self) -> None:
        """Discard private policy state."""


def make_k1_policy(case, field_frame, config):
    """Factory contract shared by candidates; called afresh for every trial."""
    if config:
        raise ValueError("The baseline K1 candidate has no configuration overrides")
    return K1CalibrationPolicy(case, field_frame)


class K1CalibrationPolicy:
    """Timed native walks, existing navigation, and the existing SingleShot skill."""

    def __init__(self, case, field_frame):
        from action.types import MotionCommand
        from run_score_benchmark import make_runner
        from skills.single_shot import SingleShot
        from world_model import types as wm

        self.case, self.frame = case, field_frame
        self.command = MotionCommand()
        self.navigation = (
            make_runner().navigation if case.kind == "transition" else None
        )
        self.shot = SingleShot()
        self.target = wm.FramedPoint2(field_frame, wm.Point2(*case.target))
        self.stage = (
            "walk"
            if case.kind == "walk"
            else "approach" if case.kind == "transition" else "kick"
        )
        self.changed_at = 0.0
        self.attempt = "calibration-shot"  # Each trial has a distinct actuator session.

    def cancel(self):
        self.shot.cancel(self.command)
        if self.navigation:
            self.navigation.cancel(self.command)

    def tick(self, context, motion, elapsed_s):
        from skills.base import SkillStatus
        from skills.single_shot import SingleShotGoal
        from skills.world import NavigateToPoseGoal
        from world_model import types as wm

        case = self.case
        if self.stage == "walk":
            if elapsed_s < case.duration_s:
                velocity = case.velocity
                for at_s, changed in case.changes:
                    if elapsed_s >= at_s:
                        velocity = tuple(changed)
                return PolicyStep("walk", velocity=tuple(velocity))
            return PolicyStep("done", status="completed")
        if self.stage == "approach":
            target = wm.FramedPose2(
                self.frame,
                wm.Pose2(
                    case.ball[0] - 0.65 * cos(case.yaw_rad),
                    case.ball[1] - 0.65 * sin(case.yaw_rad),
                    case.yaw_rad,
                ),
            )
            progress = self.navigation.tick(
                context,
                NavigateToPoseGoal(
                    target,
                    distance_tolerance=0.15,
                    theta_tolerance=0.2,
                    max_vx=0.2,
                    max_vy=0.2,
                    max_vtheta=0.8,
                ),
                self.command,
            )
            if progress.status == SkillStatus.FAILED:
                return PolicyStep("approach", status="failed", reason=progress.reason)
            if progress.status == SkillStatus.RUNNING:
                return PolicyStep(
                    "approach",
                    velocity=(self.command.x, self.command.y, self.command.theta),
                )
            self.stage = "kick"
            self.changed_at = elapsed_s
            return PolicyStep("kick")
        if self.stage == "kick":
            progress = self.shot.tick(
                context,
                SingleShotGoal(
                    case.power,
                    target=self.target,
                    duration_sec=8,
                    attempt_id=self.attempt,
                ),
                self.command,
                motion=motion,
            )
            if progress.status == SkillStatus.FAILED:
                return PolicyStep("kick", status="failed", reason=progress.reason)
            if progress.status == SkillStatus.SUCCEEDED:
                if case.kind == "kick":
                    return PolicyStep(
                        "done", status="completed", reason=progress.reason
                    )
                self.stage, self.changed_at = "recovery", elapsed_s
                return PolicyStep("recovery")
            kick = (
                (
                    self.command.kick_direction,
                    self.command.kick_power,
                    self.command.kick_ball_x,
                    self.command.kick_ball_y,
                )
                if self.command.kick_active
                else None
            )
            return PolicyStep("kick", kick=kick, head=self.command.head_targets())
        if self.stage == "recovery":
            if elapsed_s - self.changed_at < 2.0:
                return PolicyStep("recovery", velocity=(0.1, 0.0, 0.0))
            return PolicyStep("done", status="completed")
        raise RuntimeError("Unknown calibration policy stage")

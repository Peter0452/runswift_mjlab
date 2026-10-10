"""A bounded kick activation followed by ball departure and confirmed controller exit."""

from dataclasses import dataclass
from math import hypot, isfinite

from skills.base import SkillProgress, SkillStatus
from skills.uncertainty import UnusableEstimate
from skills.world import Kick, KickGoal, KickPolicy, WorldSkill
from world_model import types as wm


@dataclass(frozen=True)
class SingleShotGoal(KickGoal):
    """Fixed aim and unique attempt identity; duration bounds activation, not success."""

    attempt_id: str = ""

    def __post_init__(self):
        super().__post_init__()
        if (
            self.target is None
            or not isinstance(self.attempt_id, str)
            or not self.attempt_id
        ):
            raise ValueError("A single shot requires a fixed target and attempt ID")


@dataclass(frozen=True)
class ShotPolicy:
    """Conservative departure threshold and bounded follow-through/stop intervals."""

    departure_m: float = 0.25
    follow_through_ns: int = 350_000_000
    stop_timeout_ns: int = 2_000_000_000
    feedback_age_ns: int = 150_000_000

    def __post_init__(self):
        if not isfinite(self.departure_m) or self.departure_m <= 0:
            raise ValueError("Departure distance must be positive and finite")
        if (
            type(self.follow_through_ns) is not int
            or not 0 <= self.follow_through_ns <= 500_000_000
        ):
            raise ValueError("Follow-through must be at most 500 ms")
        if (
            type(self.stop_timeout_ns) is not int
            or not 0 < self.stop_timeout_ns <= 3_000_000_000
        ):
            raise ValueError("Stop timeout must be at most three seconds")
        if (
            type(self.feedback_age_ns) is not int
            or not 0 < self.feedback_age_ns <= 150_000_000
        ):
            raise ValueError("Feedback age must be at most 150 ms")


class SingleShot(WorldSkill):
    """Own one attempt; success means observed departure and a stopped controller.

    Neither SDK phases nor timer expiry prove a strike. No contact or goal is
    claimed. Cancellation, stale information and frame resets clear the intent.
    A completed goal stays stopped until its owner explicitly starts a new one.
    """

    def __init__(self, *, policy=None, shot_policy=None, **kwargs):
        super().__init__(**kwargs)
        self.policy = KickPolicy() if policy is None else policy
        self.shot_policy = ShotPolicy() if shot_policy is None else shot_policy
        self.kick = Kick(policy=self.policy, limits=self.limits)
        self.on_exit()

    def on_exit(self):
        super().on_exit()
        self.kick.on_exit()
        self.phase = "ready"
        self._origin = self._departed_at = self._stopping_at = self._basis = None

    def tick(self, context, goal, command, *, motion=None):
        self._motion = motion
        return super().tick(context, goal, command)

    def _tick(self, context, goal, command):
        motion = self._motion
        if (
            motion is None
            or motion.at.clock_epoch != context.now.clock_epoch
            or not 0
            <= context.now.ns - motion.at.ns
            <= self.shot_policy.feedback_age_ns
            or not motion.upright
        ):
            raise UnusableEstimate("shot_motion_feedback_unavailable")
        basis = (
            context.world.self.localisation_epoch,
            context.world.snapshot.field.frame,
            context.world.snapshot.configuration_id,
            tuple(
                (s.source, s.target, s.model_id, s.calibration_id)
                for s in context.world.snapshot.transforms
                if isinstance(s, wm.KinematicTransformSample)
                and s.source.name in {"robot_base", "odom"}
            ),
        )
        if self._basis is not None and self._basis != basis:
            raise UnusableEstimate("shot_reference_reset")
        self._basis = basis
        same_attempt = motion.kick_attempt_id == goal.attempt_id
        if self.phase == "complete":
            return SkillProgress(
                SkillStatus.SUCCEEDED, reason="shot_departed_and_stopped"
            )
        if same_attempt and motion.kick_status == "failed":
            raise UnusableEstimate("shot_actuator_failed")
        if self.phase == "stopping":
            if same_attempt and motion.kick_status == "stopped":
                self.phase = "complete"
                return SkillProgress(
                    SkillStatus.SUCCEEDED, reason="shot_departed_and_stopped"
                )
            if context.now.ns - self._stopping_at >= self.shot_policy.stop_timeout_ns:
                raise UnusableEstimate("shot_stop_unconfirmed")
            return SkillProgress(SkillStatus.RUNNING, reason="shot_stopping")
        if not motion.kick_ready:
            raise UnusableEstimate("shot_motion_not_ready")
        ball = self._ball(context, goal.target.frame)
        spread = self.policy.assess_ball(ball).position_std_m
        point = ball.value.position
        if self._origin is None:
            self._origin = (point, spread, ball.meta.evidence_at)
        origin, origin_spread, evidence_at = self._origin
        if (
            same_attempt
            and motion.kick_status == "running"
            and evidence_at is not None
            and ball.meta.evidence_at is not None
            and ball.meta.evidence_at.ns > evidence_at.ns
            and hypot(point.x - origin.x, point.y - origin.y)
            > self.shot_policy.departure_m
            + self.policy.margin_sigma * (spread + origin_spread)
        ):
            self._departed_at = (
                context.now.ns if self._departed_at is None else self._departed_at
            )
        if self._departed_at is not None:
            self.phase = "follow_through"
            if context.now.ns - self._departed_at >= self.shot_policy.follow_through_ns:
                self.kick.cancel(command)
                self.phase, self._stopping_at = "stopping", context.now.ns
                return SkillProgress(SkillStatus.RUNNING, reason="shot_stopping")
        progress = self.kick.tick(context, goal, command)
        if progress.status == SkillStatus.SUCCEEDED:
            raise UnusableEstimate("shot_activation_timeout")
        if progress.status == SkillStatus.FAILED:
            raise UnusableEstimate(progress.reason)
        if self.phase == "ready":
            self.phase = "active"
        return SkillProgress(SkillStatus.RUNNING, reason="shot_" + self.phase)

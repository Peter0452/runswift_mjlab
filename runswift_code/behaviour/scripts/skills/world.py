"""Incremental world-model entry points for the extracted skills.

Requests here contain goals/options only. Legacy request-based entry points stay
available to the match runner while its remaining inputs are migrated.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import asin, atan2, cos, hypot, isclose, isfinite, pi, sin

from action.types import MotionCommand
from navigation_safety import CollisionScene
from world_model.types import FramedPoint2, FramedPose2

from skills.base import SkillProgress, SkillStatus
from skills.navigation_policy import NavigationPolicy
from skills.uncertainty import KickPolicy, PosePolicy, UnusableEstimate, ball_spread
from skills.visual_kick import VisualKickReference, kick_direction_robot
from skills.walk_in_circle import (
    WalkInCircleRequest,
    circle_angle,
    walk_in_circle_velocity,
)
from skills.walk_to_pose import WalkToPose as WalkController
from skills.walk_to_pose import WalkToPoseRequest, pose_error, wrap_pi
from world_model import TickContext
from world_model import types as wm


@dataclass(frozen=True)
class ReadLimits:
    """Behaviour policy for age at decision time; these do not change estimation."""

    snapshot_ns: int = 150_000_000
    state_ns: int = 150_000_000
    evidence_ns: int = 500_000_000
    allow_unknown_evidence: bool = False

    def __post_init__(self):
        for value in (self.snapshot_ns, self.state_ns, self.evidence_ns):
            if type(value) is not int or value < 0:
                raise ValueError("Age limits must be non-negative integer nanoseconds")


@dataclass(frozen=True)
class WalkToPoseGoal:
    """A target in one fixed field/odom epoch; no robot pose or sensed obstacles."""

    target: FramedPose2
    distance_tolerance: float = 0.3
    theta_tolerance: float = 0.4
    speed_scale: float = 1.0
    max_vx: float = 0.8
    max_vy: float = 0.6
    max_vtheta: float = 1.2


@dataclass(frozen=True)
class NavigateToPoseGoal(WalkToPoseGoal):
    """A fixed field target and controller options, with no measured world facts.

    keep_out is an optional minimum centre separation, never a replacement for
    footprint and uncertainty margins. safety_margin adds field-edge clearance.
    """

    keep_out: float = 0.0
    ball_keep_out_m: float = 0.0  # Tactical centre distance, read ball from this tick.
    safety_margin: float = 0.0

    def __post_init__(self):
        if not all(
            isfinite(value)
            for value in (
                self.target.pose.x,
                self.target.pose.y,
                self.target.pose.theta,
            )
        ):
            raise ValueError("Navigation target must be finite")
        for name in (
            "distance_tolerance",
            "theta_tolerance",
            "max_vx",
            "max_vy",
            "max_vtheta",
        ):
            value = getattr(self, name)
            if not isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if not isfinite(self.speed_scale) or not 0 <= self.speed_scale <= 1:
            raise ValueError("speed_scale must be between zero and one")
        if not isfinite(self.safety_margin) or self.safety_margin < 0:
            raise ValueError("safety_margin must be finite and non-negative")
        if not isfinite(self.ball_keep_out_m) or self.ball_keep_out_m < 0:
            raise ValueError("ball_keep_out_m must be finite and non-negative")
        if not isfinite(self.keep_out) or self.keep_out < 0:
            raise ValueError("keep_out must be finite and non-negative")


@dataclass(frozen=True)
class NavigationEvidence:
    """The accepted immutable facts for one tick, retained intact for diagnostics."""

    snapshot_id: wm.SnapshotId
    pose: wm.Estimate[wm.FramedPose2]
    obstacles: wm.ObstacleSet
    field: wm.FieldGeometry
    scene: CollisionScene


@dataclass(frozen=True)
class WalkInCircleGoal:
    """Circle geometry in a fixed field/odom epoch; progress stays in the skill."""

    centre: FramedPoint2
    radius: float
    speed: float = 0.35
    direction: float = 1.0
    revolutions: float = 1.0


@dataclass(frozen=True)
class KickGoal:
    """Aim at a fixed field/odom target, or a body-relative direction in radians.

    Exactly one of target/direction is required. A direction goal needs no global
    localisation. Duration measures intent holding, never measured kick success.
    """

    power: float
    target: FramedPoint2 | None = None
    direction: float | None = None
    duration_sec: float = 3.0

    def __post_init__(self):
        if (self.target is None) == (self.direction is None):
            raise ValueError("Supply exactly one kick target or direction")
        for value in (self.power, self.duration_sec, self.direction):
            if value is not None and not isfinite(value):
                raise ValueError("Kick options must be finite")
        if self.power < 0 or self.duration_sec < 0:
            raise ValueError("Power and duration must be non-negative")


@dataclass(frozen=True)
class StandGoal:
    """Hold a stopped intent for this many seconds of the supplied decision clock."""

    duration_sec: float = 2.0

    def __post_init__(self):
        if not isfinite(self.duration_sec) or self.duration_sec < 0:
            raise ValueError("Duration must be finite and non-negative")


class WorldSkill:
    """Receive one frozen tick plus a goal; never own a reader, clock or updater."""

    def __init__(self, *, limits: ReadLimits | None = None):
        self.limits = ReadLimits() if limits is None else limits
        self._scope = None
        self._goal = None
        self._last_ns = None
        self._started_ns = None

    def on_enter(self, context: TickContext, goal) -> None:
        """Begin private skill state in the supplied world/clock epoch."""
        self.on_exit()
        self._scope = (context.world.snapshot.id.world_epoch, context.now.clock_epoch)
        self._goal = goal
        self._started_ns = context.now.ns

    def on_exit(self) -> None:
        """Drop private state without touching the world or action hardware."""
        self._scope = self._goal = self._last_ns = self._started_ns = None

    def cancel(self, command: MotionCommand) -> None:
        self.on_exit()
        command.reset()

    def tick(self, context: TickContext, goal, command: MotionCommand) -> SkillProgress:
        """Overwrite body/kick intent; unavailable evidence produces a stopped failure."""
        command.reset()
        try:
            age = context.world.age(context.now)
            if age.status != "ok":
                raise UnusableEstimate(age.reason)
            if age.value > self.limits.snapshot_ns:
                raise UnusableEstimate("stale_snapshot")
            if any(
                item.component == "world_runtime" and item.status != "ready"
                for item in context.world.health
            ):
                raise UnusableEstimate("world_runtime_unavailable")
            scope = (context.world.snapshot.id.world_epoch, context.now.clock_epoch)
            if self._scope is not None and self._scope != scope:
                raise UnusableEstimate("world_or_clock_changed")
            if self._last_ns is not None and context.now.ns < self._last_ns:
                raise UnusableEstimate("decision_time_reversed")
            if self._scope is None or goal != self._goal:
                self.on_enter(context, goal)
            self._last_ns = context.now.ns
            return self._tick(context, goal, command)
        except UnusableEstimate as error:
            self.cancel(command)
            return SkillProgress(SkillStatus.FAILED, reason=str(error))

    def _estimate(self, context, estimate):
        meta = estimate.meta
        if estimate.value is None or meta.status in {"unavailable", "lost"}:
            raise UnusableEstimate("estimate_unavailable")
        if any(
            stamp.clock_epoch != context.now.clock_epoch
            for stamp in (meta.state_at, meta.valid_until)
        ):
            raise UnusableEstimate("clock_epoch_mismatch")
        if context.now.ns >= meta.valid_until.ns:
            raise UnusableEstimate("expired_estimate")
        state_age = context.now.ns - meta.state_at.ns
        if state_age < 0 or state_age > self.limits.state_ns:
            raise UnusableEstimate("stale_state")
        if meta.evidence_at is None:
            if not self.limits.allow_unknown_evidence:
                raise UnusableEstimate("unknown_evidence_age")
        elif meta.evidence_at.clock_epoch != context.now.clock_epoch:
            raise UnusableEstimate("clock_epoch_mismatch")
        elif not 0 <= context.now.ns - meta.evidence_at.ns <= self.limits.evidence_ns:
            raise UnusableEstimate("stale_evidence")
        return estimate

    def _pose(self, context, frame):
        result = context.world.self_pose(frame)
        if result.status != "ok":
            raise UnusableEstimate(result.reason)
        return self._estimate(context, result.value)

    def _ball(self, context, frame):
        # Use the publication time, not decision time: reads cannot predict.
        at = context.world.snapshot.as_of
        result = context.world.ball_at("local", at, frame, reference_at=at)
        if result.status != "ok":
            raise UnusableEstimate(result.reason)
        return self._estimate(context, result.value.estimate)

    def _local_ball(self, context):
        result = context.world.current_local_ball()
        if result.status != "ok":
            raise UnusableEstimate(result.reason)
        return self._estimate(context, result.value)

    @staticmethod
    def _fixed_target(target):
        if target.frame.name not in {"odom", "team_field"}:
            raise UnusableEstimate("target_requires_fixed_frame")
        if target.reference_at is not None:
            raise UnusableEstimate("target_requires_fixed_reference")

    def _held(self, context, duration_sec, reason):
        elapsed = (context.now.ns - self._started_ns) / 1e9
        done = elapsed >= duration_sec
        return SkillProgress(
            SkillStatus.SUCCEEDED if done else SkillStatus.RUNNING,
            1.0 if done else elapsed / duration_sec,
            "intent_duration_elapsed" if done else reason,
        )


class WalkToPose(WorldSkill):
    """Scale walking by pose precision and include uncertainty in arrival checks."""

    def __init__(self, *, policy: PosePolicy | None = None, **kwargs):
        super().__init__(**kwargs)
        self.policy = PosePolicy() if policy is None else policy

    def _tick(self, context, goal: WalkToPoseGoal, command):
        self._fixed_target(goal.target)
        estimate = self._pose(context, goal.target.frame)
        spread = self.policy.assess(estimate)
        request = WalkToPoseRequest(
            robot_pose=estimate.value.pose,
            target_pose=goal.target.pose,
            distance_tolerance=goal.distance_tolerance,
            theta_tolerance=goal.theta_tolerance,
            speed_scale=goal.speed_scale * self.policy.speed_scale(spread),
            max_vx=goal.max_vx,
            max_vy=goal.max_vy,
            max_vtheta=goal.max_vtheta,
        )
        distance, heading = pose_error(request)
        if distance < goal.distance_tolerance and heading < goal.theta_tolerance:
            if (
                distance + self.policy.margin_sigma * spread.position_std_m
                < goal.distance_tolerance
                and heading + self.policy.margin_sigma * spread.heading_std_rad
                < goal.theta_tolerance
            ):
                return SkillProgress(SkillStatus.SUCCEEDED, 1.0, "arrived")
            # The mean is at the goal, but the uncertainty margin does not fit.
            return SkillProgress(SkillStatus.RUNNING, reason="arrival_uncertain")
        return WalkController().tick(request, command)


class NavigateToPose(WorldSkill):
    """Plan from one frozen field-frame tick; keep caches and progress in the skill."""

    def __init__(
        self,
        *,
        policy: PosePolicy | None = None,
        navigation_policy: NavigationPolicy | None = None,
        max_obstacles=10,
        replan_period_sec=0.25,
        planner=None,
        tracker=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        from skills.navigate_to_pose import NavigateToPose as NavigationController

        if type(max_obstacles) is not int or max_obstacles <= 0:
            raise ValueError("max_obstacles must be positive")
        if not isfinite(replan_period_sec) or replan_period_sec <= 0:
            raise ValueError("replan_period_sec must be finite and positive")
        for component in (planner, tracker):
            if component is not None and not callable(
                getattr(component, "reset", None)
            ):
                raise ValueError("Injected navigation components must support reset()")
        if planner is not None:
            capacity = getattr(getattr(planner, "config", None), "max_obstacles", None)
            if type(capacity) is not int or capacity < max_obstacles:
                raise ValueError("Planner must declare sufficient config.max_obstacles")
        self.policy = PosePolicy() if policy is None else policy
        self.navigation_policy = (
            NavigationPolicy() if navigation_policy is None else navigation_policy
        )
        self.max_obstacles = max_obstacles
        self._navigation = NavigationController(
            max_obstacles=max_obstacles,
            replan_period_sec=replan_period_sec,
            planner=planner,
            tracker=tracker,
            log_paths=False,
        )
        self._basis = self._localisation_epoch = self.evidence = None

    @property
    def debug(self):
        """Read the private controller's path/tracker diagnostics for this tick."""
        return self._navigation.debug

    def on_exit(self):
        super().on_exit()
        self._navigation.on_exit()
        self._basis = self._localisation_epoch = self.evidence = None

    @staticmethod
    def _planning_field(field):
        from navigation_types import PlanningField

        half_x, half_y = field.length / 2, field.width / 2
        expected = {
            (-half_x, -half_y),
            (half_x, -half_y),
            (half_x, half_y),
            (-half_x, half_y),
        }
        boundary = {(p.x, p.y) for p in field.playing_boundary.vertices}
        vertices = field.playing_boundary.vertices
        # The reused planner supports centred rectangles only. Do not quietly
        # replace a different boundary with a rectangle based on length/width.
        if (
            half_x <= 0
            or half_y <= 0
            or boundary != expected
            or len(field.playing_boundary.vertices) != 4
            or any(
                a.x != b.x and a.y != b.y
                for a, b in zip(vertices, vertices[1:] + vertices[:1])
            )
        ):
            raise UnusableEstimate("unsupported_navigation_field")
        goals = (field.own_goal, field.opponent_goal)
        if any(
            not isclose(abs(g.centre.x), half_x)
            or g.width <= 0
            or abs(g.centre.y) + g.width / 2 > half_y
            for g in goals
        ):
            raise UnusableEstimate("unsupported_navigation_goals")
        return PlanningField(
            field.length,
            field.width,
            tuple((g.centre.x, g.centre.y, g.width) for g in goals),
        )

    def _inputs(self, context, goal):
        snapshot = context.world.snapshot
        self._fixed_target(goal.target)
        if goal.target.frame.name != "team_field":
            raise UnusableEstimate("navigation_requires_field_target")
        field = snapshot.field
        if field.frame != goal.target.frame:
            raise UnusableEstimate("navigation_field_frame_mismatch")
        planning_field = self._planning_field(field)
        half_x, half_y = (
            field.length / 2 - goal.safety_margin,
            field.width / 2 - goal.safety_margin,
        )
        if min(half_x, half_y) <= 0:
            raise UnusableEstimate("navigation_margin_exceeds_field")
        if abs(goal.target.pose.x) > half_x or abs(goal.target.pose.y) > half_y:
            raise UnusableEstimate("navigation_target_outside_field")
        pose = self._pose(context, field.frame)
        if pose.meta.state_at != snapshot.as_of:
            raise UnusableEstimate("navigation_pose_time_mismatch")
        if (
            pose.value.child_frame is None
            or pose.value.child_frame.owner != snapshot.identity
        ):
            raise UnusableEstimate("navigation_robot_frame_unavailable")
        spread = self.policy.assess(pose)

        result = context.world.obstacles_in(field.frame)
        if result.status != "ok":
            raise UnusableEstimate(result.reason)
        obstacles, memory = result.value, context.world.obstacles
        if obstacles.at != snapshot.as_of:
            raise UnusableEstimate("navigation_obstacle_time_mismatch")
        if obstacles.valid_until.clock_epoch != context.now.clock_epoch:
            raise UnusableEstimate("clock_epoch_mismatch")
        if context.now.ns >= obstacles.valid_until.ns:
            raise UnusableEstimate("expired_obstacle_input")
        if obstacles.unavailable_track_ids:
            raise UnusableEstimate("obstacle_conversions_unavailable")
        if memory.dropped_tracks:
            raise UnusableEstimate("obstacle_memory_incomplete")
        if len(obstacles.estimates) > self.max_obstacles:
            raise UnusableEstimate("navigation_obstacle_capacity")
        last = memory.last_frame
        if last is None or last.time_quality != "synchronised":
            raise UnusableEstimate("obstacle_input_time_unknown")
        if last.event_at.clock_epoch != context.now.clock_epoch:
            raise UnusableEstimate("clock_epoch_mismatch")
        if not 0 <= context.now.ns - last.event_at.ns <= self.limits.evidence_ns:
            raise UnusableEstimate("stale_obstacle_input")
        sources = {last.id.source}
        for estimate in (pose, *obstacles.estimates):
            sources.update(item.source for item in estimate.meta.contributors)
        for estimate in obstacles.estimates:
            try:
                self._estimate(context, estimate)
            except UnusableEstimate as error:
                raise UnusableEstimate(f"obstacle_{error}") from error
        if any(
            item.component in sources and item.status != "ready"
            for item in snapshot.health
        ):
            raise UnusableEstimate("navigation_source_unavailable")

        # Transform values evolve normally; only identities/calibrations define
        # the coordinate basis. Field-localisation reset identity is separate.
        transforms = tuple(
            sorted(
                (
                    (item.source, item.target, item.model_id, item.calibration_id)
                    for item in snapshot.transforms
                    if isinstance(item, wm.KinematicTransformSample)
                    and item.source.name in {"robot_base", "odom"}
                ),
                key=lambda item: item[0].name,
            )
        )
        basis = (
            snapshot.configuration_id,
            snapshot.identity,
            field,
            pose.value.child_frame,
            pose.meta.provider_epoch,
            transforms,
        )
        if self._basis is not None:
            if self._basis != basis:
                raise UnusableEstimate("navigation_frame_changed")
            if self._localisation_epoch != context.world.self.localisation_epoch:
                raise UnusableEstimate("localisation_changed")
        self._basis = basis
        self._localisation_epoch = context.world.self.localisation_epoch
        scene = self.navigation_policy.scene(
            context, goal, planning_field, obstacles, spread
        )
        if goal.ball_keep_out_m:
            from navigation_types import PlanningObstacle

            ball = self._ball(context, field.frame)
            error = ball_spread(ball).position_std_m
            if ball.meta.quality not in {"nominal", "degraded"}:
                raise UnusableEstimate("ball_quality_rejected")
            if len(scene.obstacles) >= self.max_obstacles:
                raise UnusableEstimate("navigation_obstacle_capacity")
            margin = self.navigation_policy.uncertainty_sigma * (
                error + spread.position_std_m
            )
            keep_out = PlanningObstacle(
                "tactical-ball",
                (ball.value.position.x, ball.value.position.y),
                0.0,
                ball.covariance.matrix,
                margin,
                goal.ball_keep_out_m + margin,
            )
            scene = replace(scene, obstacles=scene.obstacles + (keep_out,))
        if scene.field_margin_m >= min(field.length, field.width) / 2:
            raise UnusableEstimate("navigation_margin_exceeds_field")
        if (
            abs(goal.target.pose.x) >= field.length / 2 - scene.field_margin_m
            or abs(goal.target.pose.y) >= field.width / 2 - scene.field_margin_m
        ):
            raise UnusableEstimate("navigation_target_outside_field")
        self.evidence = NavigationEvidence(snapshot.id, pose, obstacles, field, scene)
        return planning_field, pose, obstacles, spread

    def _tick(self, context, goal: NavigateToPoseGoal, command):
        from skills.navigate_to_pose import NavigateToPoseRequest

        field, pose, obstacles, spread = self._inputs(context, goal)
        request = NavigateToPoseRequest(
            robot_pose=pose.value.pose,
            target_pose=goal.target.pose,
            plan_obstacles=tuple(
                (e.value.position.x, e.value.position.y) for e in obstacles.estimates
            ),
            # A shared scene performs local swept-command avoidance after tracking.
            apply_avoidance=False,
            keep_out=goal.keep_out,
            safety_margin=goal.safety_margin,
            distance_tolerance=goal.distance_tolerance,
            theta_tolerance=goal.theta_tolerance,
            speed_scale=goal.speed_scale * self.policy.speed_scale(spread),
            vx_limit=goal.max_vx,
            vy_limit=goal.max_vy,
            vtheta_limit=goal.max_vtheta,
        )
        distance, heading = pose_error(request)
        if distance < goal.distance_tolerance and heading < goal.theta_tolerance:
            self._navigation.on_exit()
            if (
                distance + self.policy.margin_sigma * spread.position_std_m
                < goal.distance_tolerance
                and heading + self.policy.margin_sigma * spread.heading_std_rad
                < goal.theta_tolerance
            ):
                return SkillProgress(SkillStatus.SUCCEEDED, 1.0, "arrived")
            return SkillProgress(SkillStatus.RUNNING, reason="arrival_uncertain")
        if goal.speed_scale == 0:
            self._navigation.on_exit()
            return SkillProgress(SkillStatus.RUNNING, reason="navigation_paused")
        result = self._navigation.tick(
            request,
            command,
            now_mono=context.now.ns / 1e9,
            field=field,
            collision_scene=self.evidence.scene,
        )
        if result.status == SkillStatus.FAILED:
            self.cancel(command)
        return result


class WalkInCircle(WorldSkill):
    """Count private progress only from sufficiently precise, unambiguous poses."""

    def __init__(self, *, policy: PosePolicy | None = None, **kwargs):
        super().__init__(**kwargs)
        self.policy = PosePolicy() if policy is None else policy
        self._reset_progress()

    def _reset_progress(self):
        self._localisation_epoch = None
        self._previous_angle = None
        self._previous_margin = self._initial_margin = self._travelled = 0.0

    def on_exit(self):
        super().on_exit()
        self._reset_progress()

    def _tick(self, context, goal: WalkInCircleGoal, command):
        self._fixed_target(goal.centre)
        if goal.centre.frame.name == "team_field":
            epoch = context.world.self.localisation_epoch
            if self._localisation_epoch not in (None, epoch):
                raise UnusableEstimate("localisation_changed")
            self._localisation_epoch = epoch
        estimate = self._pose(context, goal.centre.frame)
        spread = self.policy.assess(estimate)
        pose, centre = estimate.value.pose, goal.centre.point
        distance = hypot(pose.x - centre.x, pose.y - centre.y)
        radius_margin = self.policy.margin_sigma * spread.position_std_m
        if distance <= radius_margin:
            raise UnusableEstimate("circle_position_uncertain")
        margin = asin(radius_margin / distance)
        request = WalkInCircleRequest(
            robot_pose=pose,
            centre=centre,
            radius=goal.radius,
            speed=goal.speed,
            direction=goal.direction,
            revolutions=goal.revolutions,
        )
        angle = circle_angle(request)
        if self._previous_angle is None:
            self._initial_margin = margin
        else:
            change = wrap_pi(angle - self._previous_angle)
            if abs(change) + self._previous_margin + margin >= pi:
                raise UnusableEstimate("circle_progress_ambiguous")
            self._travelled += change
        self._previous_angle, self._previous_margin = angle, margin
        # Endpoint errors may correlate; sum their angular margins conservatively.
        travelled = max(0.0, abs(self._travelled) - self._initial_margin - margin)
        target = abs(goal.revolutions) * 2 * pi
        if target > 1e-6 and travelled >= target:
            return SkillProgress(SkillStatus.SUCCEEDED, 1.0, "revolutions")
        velocity = walk_in_circle_velocity(request)
        scale = self.policy.speed_scale(spread)
        command.set_body(*(value * scale for value in velocity))
        return SkillProgress(
            SkillStatus.RUNNING,
            0.0 if target <= 1e-6 else min(1.0, travelled / target),
            "circling",
        )


class Stand(WorldSkill):
    """Hold stopped intent using TickContext.now, including deterministic replay."""

    def _tick(self, context, goal: StandGoal, command):
        return self._held(context, goal.duration_sec, "holding")


class VisualKick(WorldSkill):
    """Screen local-ball and aiming uncertainty before producing a kick reference."""

    def __init__(self, *, policy: KickPolicy | None = None, **kwargs):
        super().__init__(**kwargs)
        self.policy = KickPolicy() if policy is None else policy
        self.reference = None

    def on_exit(self):
        super().on_exit()
        self.reference = None

    def _tick(self, context, goal: KickGoal, command):
        local_ball = self._local_ball(context)
        self.policy.assess_ball(local_ball)
        if goal.target is not None:
            self._fixed_target(goal.target)
            pose = self._pose(context, goal.target.frame)
            if pose.meta.state_at != context.world.snapshot.as_of:
                raise UnusableEstimate("pose_ball_time_mismatch")
            ball = self._ball(context, goal.target.frame)
            if (
                local_ball.value.observation_ref is None
                or pose.value.child_frame != local_ball.value.frame
                or ball.value.observation_ref != local_ball.value.observation_ref
                or ball.meta.state_at != local_ball.meta.state_at
            ):
                raise UnusableEstimate("kick_estimate_basis_mismatch")
            self.policy.assess_aim(pose, ball, goal.target.point)
            direction = kick_direction_robot(
                ball.value.position.x,
                ball.value.position.y,
                goal.target.point.x,
                goal.target.point.y,
                pose.value.pose.theta,
            )
        else:
            direction = atan2(sin(goal.direction), cos(goal.direction))
        progress = self._held(context, goal.duration_sec, "aiming")
        # Always use the owner's correlated local estimate for the SDK ball
        # point; do not subtract separately uncertain field pose/ball means.
        position = local_ball.value.position
        self.reference = (
            None
            if progress.status == SkillStatus.SUCCEEDED
            else VisualKickReference(direction, goal.power, position.x, position.y)
        )
        return progress


class Kick(VisualKick):
    """Write kick intent from the same frozen view; completion is intent duration only."""

    def _tick(self, context, goal: KickGoal, command):
        progress = super()._tick(context, goal, command)
        if self.reference is not None:
            ref = self.reference
            command.set_kick(ref.direction, ref.power, ref.ball_x, ref.ball_y)
        return progress

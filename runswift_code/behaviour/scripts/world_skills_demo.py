#!/usr/bin/env python3
"""Deterministic world/skill handoff demo; prints intents and never sends commands.

Install src/world_model into Python 3.11+ and run this file from any directory.
Synthetic dimensions, kinematics and covariance are for this example only.
"""

from dataclasses import replace

from action.types import MotionCommand
from skills.base import SkillStatus
from skills.world import (
    Kick,
    KickGoal,
    NavigateToPose,
    NavigateToPoseGoal,
    NavigationPolicy,
    Stand,
    StandGoal,
    WalkToPose,
    WalkToPoseGoal,
)

from world_model import capture_tick, create_world_model, noise_from_covariance
from world_model import types as t

SECOND = 1_000_000_000
DEMO_EXACT = t.GaussianNoise(())  # Exact only for synthetic inputs in this example.


def make_config():
    """Declare a synthetic planar robot and stationary-ball model for this demo."""
    identity = t.RobotIdentity(1, 2)
    field = t.FrameId("team_field", "field-1")
    bounds = t.Polygon(
        (t.Point2(-4.5, -3), t.Point2(4.5, -3), t.Point2(4.5, 3), t.Point2(-4.5, 3))
    )
    geometry = t.FieldGeometry(
        "demo-field",
        "official-only",
        field,
        9.0,
        6.0,
        0.75,
        t.GoalGeometry(t.Point2(-4.5, 0), 2.0),
        t.GoalGeometry(t.Point2(4.5, 0), 2.0),
        (),
        (),
        bounds,
    )
    spatial = t.SpatialConfig(
        t.BodyReference("demo-model", "demo-calibration", "pelvis", transform()),
        (t.FrameLink("robot_base", "odom"), t.FrameLink("robot_body", "robot_base")),
        ball_height=0.05,
        ball_height_tolerance=0.02,
        stationary_variance_rate=0.04,
    )
    return t.WorldConfig(
        "world-skills-demo",
        identity,
        geometry,
        ball_max_age_ns=SECOND,
        pose_max_age_ns=SECOND,
        official_report_max_age_ns=SECOND,
        peer_report_max_age_ns=SECOND,
        peer_retention_ns=2 * SECOND,
        projection_wait_ns=100_000_000,
        max_future_skew_ns=100_000_000,
        pose_history_capacity=32,
        sensor_queue_capacity=32,
        transition_queue_capacity=8,
        spatial=spatial,
    )


def transform(x=0.0):
    return t.RigidTransform3(t.Point3(x, 0.0, 0.0), t.Quaternion(1.0, 0.0, 0.0, 0.0))


class ReplayClock:
    """The application/replay harness advances time; skills only receive its value."""

    def __init__(self):
        self.ns = 0

    def now(self):
        return t.TimePoint("world-skills-demo-clock", self.ns)


class DemoInputs:
    """Stand in for measured input adapters with plain, explicitly timed values."""

    def __init__(self, port, clock, config):
        self.port, self.clock, self.config = port, clock, config
        self.sequence = 0
        self.base = t.FrameId("robot_base", "base-1", config.identity)
        self.odom = t.FrameId("odom", "odom-1", config.identity)

    def submit(self, source, payload):
        now = self.clock.now()
        event = t.WorldEvent(
            t.InputMeta(
                t.EventId(source, "demo-source", self.sequence),
                None,
                now,
                now,
                "synchronised",
                0,
                self.config.configuration_id,
            ),
            payload,
        )
        self.sequence += 1
        admission = self.port.submit(event)
        if admission.status != "queued":
            raise RuntimeError(admission.reason)
        return event

    def pose(self, x=0.0, *, noise=DEMO_EXACT):
        now = self.clock.now()
        return self.submit(
            "odometry",
            t.KinematicTransformSample(
                self.base,
                self.odom,
                now,
                replace(now, ns=now.ns + SECOND),
                transform(x),
                noise,
                "demo-model",
                "demo-calibration",
            ),
        )

    def ball(self, x=1.0, *, noise=DEMO_EXACT):
        return self.submit(
            "vision",
            t.VisionFrame(
                "demo-image",
                "demo-calibration",
                (
                    t.BallDetection(
                        t.FramedPoint2(self.base, t.Point2(x, 0.0), self.clock.now()),
                        0.9,
                        noise=noise,
                    ),
                ),
            ),
        )


def navigation_example():
    """Replay field navigation and a producer pause, using no robot interfaces."""
    config = make_config()
    config = replace(
        config,
        obstacles=t.ObstacleConfig(SECOND, 16, 0.04),
        spatial=replace(
            config.spatial,
            links=config.spatial.links + (t.FrameLink("odom", "team_field"),),
        ),
    )
    clock = ReplayClock()
    model = create_world_model(config=config, clock=clock)
    inputs = DemoInputs(model.input, clock, config)
    inputs.pose()
    inputs.submit(
        "field-localisation",
        t.KinematicTransformSample(
            inputs.odom,
            config.field.frame,
            clock.now(),
            replace(clock.now(), ns=SECOND),
            transform(),
            DEMO_EXACT,
            "demo-model",
            "demo-calibration",
        ),
    )
    inputs.submit(
        "vision",
        t.VisionFrame(
            "obstacle-image",
            "demo-calibration",
            (),
            obstacles=(
                t.ObstacleDetection(
                    t.FramedPoint2(inputs.base, t.Point2(1, 0), clock.now()),
                    0.28,
                    0.9,
                    noise=DEMO_EXACT,
                ),
            ),
        ),
    )
    model.owner.advance(clock.now())
    # This synthetic replay opts into slow travel through uninspected space.
    # A deployed caller should agree a coverage profile and use require_clear.
    navigation = NavigateToPose(
        navigation_policy=NavigationPolicy(unknown_space="allow_unknown")
    )
    goal = NavigateToPoseGoal(t.FramedPose2(config.field.frame, t.Pose2(2, 0, 0)))
    command = MotionCommand()
    context = capture_tick(model.reader, clock, 0)
    result = navigation.tick(context, goal, command)
    assert result.status == SkillStatus.RUNNING and len(navigation.debug.path) > 2
    assert navigation.evidence.obstacles.coverage == "unknown"
    print(
        f"navigation: {len(navigation.debug.path)} waypoints; individual margins; unknown space explicitly allowed at limited speed"
    )
    clock.ns = 200_000_000
    held = capture_tick(model.reader, clock, 1)
    result = navigation.tick(held, goal, command)
    assert (
        result.reason == "stale_snapshot"
        and command.x == command.y == command.theta == 0
    )
    assert navigation.debug.path is None
    print(
        "navigation: paused producer -> stale_snapshot, stopped intent, discarded path"
    )


def main():
    config, clock = make_config(), ReplayClock()
    model = create_world_model(config=config, clock=clock)
    inputs = DemoInputs(model.input, clock, config)
    inputs.pose()
    inputs.ball()
    # These owner calls belong to the application replay scheduler, not skills.
    model.owner.advance(clock.now())
    context = capture_tick(model.reader, clock, tick_id=0)
    command = MotionCommand()
    walk = WalkToPose()
    goal = WalkToPoseGoal(t.FramedPose2(inputs.odom, t.Pose2(2.0, 0.0, 0.0)))
    result = walk.tick(context, goal, command)
    print(f"walk: {result.reason}, body=({command.x}, {command.y}, {command.theta})")
    assert result.reason == "walking" and command.x > 0
    # Strategy may choose another skill using exactly the same frozen view.
    kick = Kick()
    kick_goal = KickGoal(power=1.0, direction=0.0)
    result = kick.tick(context, kick_goal, command)
    print(
        f"kick: {result.reason}, local ball=({command.kick_ball_x}, {command.kick_ball_y})"
    )
    assert command.kick_active and command.kick_ball_x == 1.0
    assert context.world.self.field_pose.summary.value is None

    clock.ns = 100_000_000
    inputs.pose(x=0.5)
    model.owner.advance(clock.now())
    moved = capture_tick(model.reader, clock, tick_id=1)
    kick.tick(moved, kick_goal, command)
    assert abs(command.kick_ball_x - 0.5) < 1e-6
    assert context.world.snapshot.as_of.ns == 0
    print(f"after movement: local ball x={command.kick_ball_x:.2f}; old view unchanged")

    stand = Stand()
    result = stand.tick(moved, StandGoal(duration_sec=0.0), command)
    assert result.reason == "intent_duration_elapsed" and not command.kick_active
    # A held view is immutable, so readers must reject it after it becomes old.
    clock.ns = 400_000_000
    stale = capture_tick(model.reader, clock, tick_id=2)
    result = kick.tick(stale, kick_goal, command)
    assert result.reason == "stale_snapshot" and not command.kick_active
    print(f"paused producer: {result.reason}, stopped body, cleared kick intent")

    # New evidence is fresh, but freshness does not imply adequate precision.
    clock.ns = 500_000_000
    inputs.pose(x=0.5)
    inputs.ball(
        x=0.5,
        noise=noise_from_covariance(((0.01, 0.0), (0.0, 0.01)), "noisy-demo-image"),
    )
    model.owner.advance(clock.now())
    noisy = capture_tick(model.reader, clock, tick_id=3)
    result = kick.tick(noisy, kick_goal, command)
    assert result.reason == "ball_position_uncertain" and not command.kick_active
    print(f"fresh but imprecise ball: {result.reason}, kick withheld")
    navigation_example()


if __name__ == "__main__":
    main()

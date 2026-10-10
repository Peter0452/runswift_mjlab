"""Real world core -> frozen context -> extracted skill -> intent (no ROS/SDK)."""

import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from math import pi
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from action.types import MotionCommand
from skills.base import SkillStatus
from skills.world import (
    Kick,
    KickGoal,
    KickPolicy,
    PosePolicy,
    ReadLimits,
    Stand,
    StandGoal,
    VisualKick,
    WalkInCircle,
    WalkInCircleGoal,
    WalkToPose,
    WalkToPoseGoal,
)
from world_skills_demo import DemoInputs, ReplayClock, main, make_config

from world_model import (
    TickContext,
    WorldView,
    capture_tick,
    create_world_model,
    noise_from_covariance,
)
from world_model import types as t


class WorldSkillsTest(unittest.TestCase):
    def setUp(self):
        self.config, self.clock = make_config(), ReplayClock()
        self.model = create_world_model(config=self.config, clock=self.clock)
        self.inputs = DemoInputs(self.model.input, self.clock, self.config)
        self.command = MotionCommand()

    def publish(self, ns=0, x=0, ball=False):
        self.clock.ns = ns
        self.inputs.pose(x)
        if ball:
            self.inputs.ball()
        self.model.owner.advance(self.clock.now())
        return capture_tick(self.model.reader, self.clock, tick_id=ns)

    def goal(self, frame=None):
        return WalkToPoseGoal(
            t.FramedPose2(
                self.inputs.odom if frame is None else frame, t.Pose2(2.0, 0.0, 0.0)
            )
        )

    def assert_stopped(self, result, reason):
        self.assertEqual(result.status, SkillStatus.FAILED)
        self.assertEqual(result.reason, reason)
        self.assertEqual(
            (self.command.x, self.command.y, self.command.theta), (0, 0, 0)
        )
        self.assertFalse(self.command.kick_active)

    def changed(self, context, /, **changes):
        return replace(
            context, world=WorldView(replace(context.world.snapshot, **changes))
        )

    def test_real_core_walk_and_arrival_without_field_localisation(self):
        skill, goal = WalkToPose(), self.goal()
        context = self.publish()
        self.assertIsNone(context.world.self.field_pose.summary.value)
        result = skill.tick(context, goal, self.command)
        self.assertEqual(result.status, SkillStatus.RUNNING)
        self.assertGreater(self.command.x, 0)
        result = skill.tick(self.publish(10_000_000, x=2), goal, self.command)
        self.assertEqual(result.status, SkillStatus.SUCCEEDED)
        self.assertEqual(self.command.x, 0)

    def test_runtime_failure_stops_even_when_frozen_clock_makes_values_look_fresh(self):
        context = self.publish(ball=True)
        skill, goal = Kick(), KickGoal(power=1, direction=0)
        skill.tick(context, goal, self.command)
        self.assertTrue(self.command.kick_active)
        failed = self.changed(
            context,
            health=context.world.health
            + (
                t.ComponentHealth(
                    "world_runtime", "faulted", reasons=("input_stalled",)
                ),
            ),
        )
        self.assert_stopped(
            skill.tick(failed, goal, self.command), "world_runtime_unavailable"
        )

    def test_stale_held_snapshot_clears_previous_intents(self):
        context = self.publish(ball=True)
        kick, goal = Kick(), KickGoal(power=1, direction=0)
        kick.tick(context, goal, self.command)
        self.assertTrue(self.command.kick_active)
        held = replace(context, now=replace(context.now, ns=200_000_000))
        self.assert_stopped(kick.tick(held, goal, self.command), "stale_snapshot")
        self.assertIsNotNone(context.world.ball.local.summary.value)

    def test_expiry_checked_at_decision_even_for_unmodified_view(self):
        context = self.publish()
        held = replace(context, now=replace(context.now, ns=1_000_000_000))
        skill = WalkToPose(
            limits=ReadLimits(snapshot_ns=2_000_000_000, state_ns=2_000_000_000)
        )
        self.assert_stopped(
            skill.tick(held, self.goal(), self.command), "expired_estimate"
        )

    def test_pose_frame_epoch_and_owner_are_checked(self):
        context = self.publish()
        for frame in (
            replace(self.inputs.odom, epoch="reset"),
            replace(self.inputs.odom, owner=t.RobotIdentity(1, 3)),
        ):
            with self.subTest(frame=frame):
                self.assert_stopped(
                    WalkToPose().tick(context, self.goal(frame), self.command),
                    "pose_frame_mismatch",
                )
        self.assert_stopped(
            WalkToPose().tick(context, self.goal(self.inputs.base), self.command),
            "target_requires_fixed_frame",
        )

    def test_fresh_publication_with_old_state_or_evidence_is_rejected(self):
        context = self.publish()
        at = replace(context.now, ns=200_000_000)
        # Keep the old estimate in a fresh publication, as a coasting provider can.
        view = WorldView(replace(context.world.snapshot, as_of=at))
        newer = TickContext(1, at, view)
        self.assert_stopped(
            WalkToPose().tick(newer, self.goal(), self.command), "stale_state"
        )
        estimate = view.self.odom_pose
        old_evidence = replace(estimate, meta=replace(estimate.meta, state_at=at))
        view = WorldView(
            replace(view.snapshot, self=replace(view.self, odom_pose=old_evidence))
        )
        skill = WalkToPose(limits=ReadLimits(evidence_ns=100_000_000))
        self.assert_stopped(
            skill.tick(TickContext(2, at, view), self.goal(), self.command),
            "stale_evidence",
        )

    def test_receive_only_evidence_requires_explicit_policy(self):
        context = self.publish()
        pose = context.world.self.odom_pose
        pose = replace(pose, meta=replace(pose.meta, evidence_at=None))
        context = self.changed(
            context, self=replace(context.world.self, odom_pose=pose)
        )
        self.assert_stopped(
            WalkToPose().tick(context, self.goal(), self.command),
            "unknown_evidence_age",
        )
        permissive = WalkToPose(limits=ReadLimits(allow_unknown_evidence=True))
        self.assertEqual(
            permissive.tick(context, self.goal(), self.command).status,
            SkillStatus.RUNNING,
        )

    def test_missing_pose_stops(self):
        context = capture_tick(self.model.reader, self.clock, 0)
        self.assert_stopped(
            WalkToPose().tick(context, self.goal(), self.command), "pose_unavailable"
        )

    def test_local_kick_uses_prepared_base_ball_after_robot_movement(self):
        old = self.publish(ball=True)
        moved = self.publish(100_000_000, x=0.5)
        result = Kick().tick(moved, KickGoal(power=2, direction=pi / 2), self.command)
        self.assertEqual(result.status, SkillStatus.RUNNING)
        self.assertAlmostEqual(self.command.kick_ball_x, 0.5)
        self.assertAlmostEqual(self.command.kick_direction, pi / 2)
        self.assertIsNone(moved.world.self.field_pose.summary.value)
        self.assertEqual(old.world.snapshot.as_of.ns, 0)
        with self.assertRaises(FrozenInstanceError):
            old.world.snapshot.as_of.ns = 1

    def test_unknown_or_ambiguous_ball_cannot_kick(self):
        context = self.publish()
        self.assert_stopped(
            Kick().tick(context, KickGoal(1, direction=0), self.command),
            "current_robot_base_unavailable",
        )
        context = self.publish(ball=True)
        ball = replace(
            context.world.ball,
            local=replace(context.world.ball.local, ambiguity="unresolved"),
        )
        context = self.changed(context, ball=ball)
        self.assert_stopped(
            Kick().tick(context, KickGoal(1, direction=0), self.command),
            "ambiguous_belief",
        )

    def test_odom_target_kick_and_visual_reference_use_same_time(self):
        context = self.publish(ball=True)
        goal = KickGoal(
            power=2, target=t.FramedPoint2(self.inputs.odom, t.Point2(4, 0))
        )
        visual = VisualKick()
        visual.tick(context, goal, self.command)
        self.assertIsNotNone(visual.reference)
        self.assertFalse(self.command.kick_active)
        Kick().tick(context, goal, self.command)
        self.assertAlmostEqual(self.command.kick_direction, 0)
        moved = self.publish(10_000_000, x=0.1)
        stale_pose = context.world.self.odom_pose
        moved = self.changed(
            moved, self=replace(moved.world.self, odom_pose=stale_pose)
        )
        self.assert_stopped(
            Kick().tick(moved, goal, self.command), "pose_ball_time_mismatch"
        )

    def test_capture_ball_without_current_transform_cannot_be_reused(self):
        self.publish(ball=True)
        self.clock.ns = 10_000_000
        self.model.owner.advance(self.clock.now())  # No exact-time transform supplied.
        context = capture_tick(self.model.reader, self.clock, 1)
        self.assert_stopped(
            Kick().tick(context, KickGoal(1, direction=0), self.command),
            "current_robot_base_unavailable",
        )

    def test_timers_use_tick_time_and_kick_completion_clears_intent(self):
        skill, goal = Kick(), KickGoal(1, direction=0, duration_sec=0.1)
        with patch(
            "time.monotonic", side_effect=AssertionError("skill read wall clock")
        ):
            context = self.publish(ball=True)
            skill.on_enter(context, goal)
            skill.tick(context, goal, self.command)
            self.assertTrue(self.command.kick_active)
            context = self.publish(100_000_000)
            result = skill.tick(context, goal, self.command)
            self.assertEqual(result.reason, "intent_duration_elapsed")
            self.assertFalse(self.command.kick_active)
            stand = Stand()
            stand.tick(context, StandGoal(0.1), self.command)
            result = stand.tick(self.publish(200_000_000), StandGoal(0.1), self.command)
            self.assertEqual(result.status, SkillStatus.SUCCEEDED)

    def test_clock_reversal_or_world_replacement_resets_private_state(self):
        skill, goal = Stand(), StandGoal()
        original = self.publish()
        later = self.publish(10_000_000)
        skill.tick(later, goal, self.command)
        self.assert_stopped(
            skill.tick(original, goal, self.command), "decision_time_reversed"
        )
        skill.tick(original, goal, self.command)
        changed = self.changed(
            original, id=replace(original.world.snapshot.id, world_epoch="new")
        )
        self.assert_stopped(
            skill.tick(changed, goal, self.command), "world_or_clock_changed"
        )

    def test_circle_progress_is_private_and_goal_change_resets_it(self):
        context = self.publish(x=1)
        skill = WalkInCircle()
        goal = WalkInCircleGoal(t.FramedPoint2(self.inputs.odom, t.Point2(0, 0)), 1.0)
        skill.tick(context, goal, self.command)
        estimate = context.world.self.odom_pose
        rotated = replace(
            estimate, value=replace(estimate.value, pose=t.Pose2(0, 1, pi))
        )
        changed = self.changed(
            context, self=replace(context.world.self, odom_pose=rotated)
        )
        result = skill.tick(changed, goal, self.command)
        self.assertAlmostEqual(result.progress, 0.25)
        result = skill.tick(changed, replace(goal, revolutions=2), self.command)
        self.assertEqual(result.progress, 0)
        self.assertEqual(context.world.self.odom_pose.value.pose.x, 1)

    def test_skills_cannot_refresh_or_invoke_providers(self):
        context = self.publish(ball=True)
        with patch.object(
            type(self.model.reader), "latest", side_effect=AssertionError("extra read")
        ):
            for skill, goal in (
                (WalkToPose(), self.goal()),
                (Kick(), KickGoal(1, direction=0)),
                (Stand(), StandGoal()),
            ):
                self.assertNotEqual(
                    skill.tick(context, goal, self.command).status, SkillStatus.FAILED
                )
        self.assertEqual(
            self.model.reader.latest().snapshot.id, context.world.snapshot.id
        )

    def with_pose_uncertainty(self, context, xy_std=0.0, heading_std=0.0, **changes):
        estimate = context.world.self.odom_pose
        covariance = t.Covariance(
            ("forward", "lateral", "turn"),
            ("m", "m", "rad"),
            ((xy_std**2, 0.0, 0.0), (0.0, xy_std**2, 0.0), (0.0, 0.0, heading_std**2)),
            "right_tangent",
            estimate.value.child_frame,
        )
        estimate = replace(estimate, covariance=replace(covariance, **changes))
        return self.changed(
            context, self=replace(context.world.self, odom_pose=estimate)
        )

    def with_ball_uncertainty(
        self, context, std, *, frame_name="robot_base", **changes
    ):
        views = []
        for item in context.world.snapshot.spatial_views:
            if item.estimate.value.frame.name == frame_name:
                covariance = replace(
                    item.estimate.covariance,
                    matrix=((std**2, 0.0), (0.0, std**2)),
                    **changes,
                )
                item = replace(
                    item, estimate=replace(item.estimate, covariance=covariance)
                )
            views.append(item)
        return self.changed(context, spatial_views=tuple(views))

    def test_walking_slows_for_uncertainty_then_rejects_imprecise_pose(self):
        context = self.publish()
        goal = self.goal()
        WalkToPose().tick(context, goal, self.command)
        precise_velocity = self.command.x
        uncertain = self.with_pose_uncertainty(context, xy_std=0.1)
        result = WalkToPose().tick(uncertain, goal, self.command)
        self.assertEqual(result.status, SkillStatus.RUNNING)
        self.assertGreater(self.command.x, 0)
        self.assertLess(self.command.x, precise_velocity)
        for xy, heading, reason in (
            (0.3, 0, "pose_position_uncertain"),
            (0, 0.3, "pose_heading_uncertain"),
        ):
            self.assert_stopped(
                WalkToPose().tick(
                    self.with_pose_uncertainty(context, xy, heading), goal, self.command
                ),
                reason,
            )

    def test_arrival_requires_positional_and_heading_margin(self):
        context = self.publish(x=1.9)
        for xy, heading in ((0.11, 0), (0, 0.21)):
            uncertain = self.with_pose_uncertainty(context, xy, heading)
            result = WalkToPose().tick(uncertain, self.goal(), self.command)
            self.assertEqual(result.status, SkillStatus.RUNNING)
            self.assertEqual(result.reason, "arrival_uncertain")
            self.assertEqual(self.command.x, 0)
        precise = self.with_pose_uncertainty(context, 0.02, 0.02)
        self.assertEqual(
            WalkToPose().tick(precise, self.goal(), self.command).status,
            SkillStatus.SUCCEEDED,
        )

    def test_unknown_covariance_and_unknown_quality_are_distinct(self):
        context = self.publish()
        estimate = context.world.self.odom_pose
        absent = self.changed(
            context,
            self=replace(
                context.world.self, odom_pose=replace(estimate, covariance=None)
            ),
        )
        self.assert_stopped(
            WalkToPose().tick(absent, self.goal(), self.command),
            "pose_uncertainty_unknown",
        )
        unknown = self.changed(
            context,
            self=replace(
                context.world.self,
                odom_pose=replace(
                    estimate, meta=replace(estimate.meta, quality="unknown")
                ),
            ),
        )
        self.assert_stopped(
            WalkToPose().tick(unknown, self.goal(), self.command),
            "pose_quality_rejected",
        )
        skill = WalkToPose(policy=PosePolicy(allowed_qualities=("unknown",)))
        self.assertEqual(
            skill.tick(unknown, self.goal(), self.command).status, SkillStatus.RUNNING
        )
        # Stand needs neither pose nor ball; irrelevant uncertainty must not block it.
        self.assertEqual(
            Stand().tick(absent, StandGoal(0), self.command).status,
            SkillStatus.SUCCEEDED,
        )

    def test_cartesian_and_body_tangent_pose_covariance_are_explicit(self):
        context = self.publish()
        estimate = context.world.self.odom_pose
        cartesian = self.with_pose_uncertainty(
            context,
            0.05,
            0.1,
            coordinates="cartesian",
            components=("x", "y", "theta"),
            frame=estimate.value.frame,
        )
        self.assertEqual(
            WalkToPose().tick(cartesian, self.goal(), self.command).status,
            SkillStatus.RUNNING,
        )
        for change in (
            {"frame": estimate.value.frame},
            {"frame": None},
            {"units": ("cm", "cm", "rad")},
            {"components": ("turn", "forward", "lateral")},
        ):
            with self.subTest(change=change):
                self.assert_stopped(
                    WalkToPose().tick(
                        self.with_pose_uncertainty(context, **change),
                        self.goal(),
                        self.command,
                    ),
                    "pose_covariance_convention",
                )

    def test_correlated_position_errors_use_largest_directional_variance(self):
        context = self.publish()
        # Both coordinate deviations are .2m; the major-axis deviation exceeds .25m.
        context = self.with_pose_uncertainty(
            context, matrix=((0.04, 0.039, 0), (0.039, 0.04, 0), (0, 0, 0))
        )
        self.assert_stopped(
            WalkToPose().tick(context, self.goal(), self.command),
            "pose_position_uncertain",
        )

    def test_invalid_covariance_fails_even_with_positive_diagonal(self):
        context = self.publish()
        context = self.with_pose_uncertainty(
            context, matrix=((0.01, 0.02, 0), (0.02, 0.01, 0), (0, 0, 0))
        )
        self.assert_stopped(
            WalkToPose().tick(context, self.goal(), self.command),
            "pose_covariance_invalid",
        )

    def test_kick_rejects_imprecise_local_ball_and_clears_prior_intent(self):
        context = self.publish(ball=True)
        skill, goal = Kick(), KickGoal(1, direction=0)
        skill.tick(context, goal, self.command)
        self.assertTrue(self.command.kick_active)
        uncertain = self.with_ball_uncertainty(context, 0.1)
        self.assert_stopped(
            skill.tick(uncertain, goal, self.command), "ball_position_uncertain"
        )
        self.assertIsNone(skill.reference)
        relaxed = Kick(policy=KickPolicy(max_ball_std_m=0.12))
        self.assertEqual(
            relaxed.tick(uncertain, goal, self.command).status, SkillStatus.RUNNING
        )
        self.assertTrue(self.command.kick_active)

    def test_kick_unknown_covariance_and_wrong_frame_fail(self):
        context = self.publish(ball=True)
        goal = KickGoal(1, direction=0)
        views = tuple(
            replace(item, estimate=replace(item.estimate, covariance=None))
            for item in context.world.snapshot.spatial_views
        )
        self.assert_stopped(
            Kick().tick(self.changed(context, spatial_views=views), goal, self.command),
            "ball_uncertainty_unknown",
        )
        wrong = self.with_ball_uncertainty(context, 0, frame=self.inputs.odom)
        self.assert_stopped(
            Kick().tick(wrong, goal, self.command), "ball_covariance_convention"
        )

    def test_fixed_target_requires_heading_precision_but_body_direction_does_not(self):
        context = self.with_pose_uncertainty(self.publish(ball=True), heading_std=0.2)
        goal = KickGoal(1, target=t.FramedPoint2(self.inputs.odom, t.Point2(4, 0)))
        self.assert_stopped(
            Kick().tick(context, goal, self.command), "pose_heading_uncertain"
        )
        self.assertEqual(
            Kick().tick(context, KickGoal(1, direction=0), self.command).status,
            SkillStatus.RUNNING,
        )

    def test_fixed_target_aim_screen_does_not_assume_independence(self):
        context = self.with_pose_uncertainty(self.publish(ball=True), heading_std=0.08)
        context = self.with_ball_uncertainty(context, 0.08, frame_name="odom")
        goal = KickGoal(1, target=t.FramedPoint2(self.inputs.odom, t.Point2(2, 0)))
        # 2*(.08+.08) = .32rad fails .25; quadrature would wrongly pass at .226rad.
        self.assert_stopped(
            Kick().tick(context, goal, self.command), "kick_direction_uncertain"
        )
        near = replace(goal, target=t.FramedPoint2(self.inputs.odom, t.Point2(1.1, 0)))
        self.assert_stopped(
            Kick().tick(context, near, self.command), "kick_target_uncertain"
        )

    def test_fixed_target_kick_uses_prepared_local_point_not_reprojection(self):
        context = self.publish(ball=True)
        # A provider can deliberately supply a different mean; the action uses
        # its local estimate instead of recreating one from marginal field means.
        views = tuple(
            replace(
                item,
                estimate=replace(
                    item.estimate,
                    value=replace(item.estimate.value, position=t.Point2(0.9, 0.1)),
                ),
            )
            if item.estimate.value.frame == self.inputs.base
            else item
            for item in context.world.snapshot.spatial_views
        )
        context = self.changed(context, spatial_views=views)
        goal = KickGoal(1, target=t.FramedPoint2(self.inputs.odom, t.Point2(4, 0)))
        Kick().tick(context, goal, self.command)
        self.assertTrue(self.command.kick_active)
        self.assertEqual(
            (self.command.kick_ball_x, self.command.kick_ball_y), (0.9, 0.1)
        )

    def test_circle_uncertainty_reduces_progress_and_failure_resets_it(self):
        context = self.with_pose_uncertainty(self.publish(x=1), 0.1)
        goal = WalkInCircleGoal(t.FramedPoint2(self.inputs.odom, t.Point2(0, 0)), 1)
        skill = WalkInCircle()
        skill.tick(context, goal, self.command)
        pose = context.world.self.odom_pose
        pose = replace(pose, value=replace(pose.value, pose=t.Pose2(0, 1, pi)))
        changed = self.changed(
            context, self=replace(context.world.self, odom_pose=pose)
        )
        result = skill.tick(changed, goal, self.command)
        self.assertGreater(result.progress, 0)
        self.assertLess(result.progress, 0.25)
        uncertain = self.with_pose_uncertainty(changed, 0.3)
        self.assert_stopped(
            skill.tick(uncertain, goal, self.command), "pose_position_uncertain"
        )
        self.assertEqual(skill.tick(changed, goal, self.command).progress, 0)

    def test_circle_cannot_count_angle_when_position_covers_centre(self):
        context = self.with_pose_uncertainty(self.publish(x=0.1), 0.1)
        goal = WalkInCircleGoal(t.FramedPoint2(self.inputs.odom, t.Point2(0, 0)), 1)
        self.assert_stopped(
            WalkInCircle().tick(context, goal, self.command),
            "circle_position_uncertain",
        )

    def test_same_mean_high_uncertainty_does_not_count_circle_completion(self):
        context = self.with_pose_uncertainty(self.publish(x=1), 0.1)
        goal = WalkInCircleGoal(
            t.FramedPoint2(self.inputs.odom, t.Point2(0, 0)), 1, revolutions=0.25
        )
        skill = WalkInCircle()
        skill.tick(context, goal, self.command)
        pose = context.world.self.odom_pose
        pose = replace(pose, value=replace(pose.value, pose=t.Pose2(0, 1, pi)))
        context = self.changed(
            context, self=replace(context.world.self, odom_pose=pose)
        )
        result = skill.tick(context, goal, self.command)
        self.assertEqual(result.status, SkillStatus.RUNNING)
        self.assertLess(result.progress, 1)

    def test_fixed_target_rejects_missing_or_mismatched_observation_identity(self):
        context = self.publish(ball=True)
        goal = KickGoal(1, target=t.FramedPoint2(self.inputs.odom, t.Point2(4, 0)))
        for identity in (None, t.EventId("other-image", "epoch", 0)):
            views = tuple(
                replace(
                    item,
                    estimate=replace(
                        item.estimate,
                        value=replace(item.estimate.value, observation_ref=identity),
                    ),
                )
                if item.estimate.value.frame == self.inputs.base
                else item
                for item in context.world.snapshot.spatial_views
            )
            self.assert_stopped(
                Kick().tick(
                    self.changed(context, spatial_views=views), goal, self.command
                ),
                "kick_estimate_basis_mismatch",
            )

    def test_real_shared_odometry_error_cancels_for_local_kick(self):
        noise = noise_from_covariance(
            tuple(
                tuple(1.0 if row == col == 0 else 0.0 for col in range(6))
                for row in range(6)
            ),
            "shared-odometry-bias",
        )
        self.inputs.pose(noise=noise)
        self.inputs.ball()
        self.model.owner.advance(self.clock.now())
        self.clock.ns = 100_000_000
        self.inputs.pose(x=0.5, noise=noise)
        self.model.owner.advance(self.clock.now())
        context = capture_tick(self.model.reader, self.clock, 1)
        local = context.world.current_local_ball().value
        self.assertAlmostEqual(local.covariance.matrix[0][0], 0.004)
        self.assertAlmostEqual(
            context.world.self.odom_pose.covariance.matrix[0][0], 1.0
        )
        result = Kick().tick(context, KickGoal(1, direction=0), self.command)
        self.assertEqual(result.status, SkillStatus.RUNNING)
        self.assertTrue(self.command.kick_active)
        self.assertAlmostEqual(self.command.kick_ball_x, 0.5)
        # A field/odom position target cannot use that cancellation automatically.
        self.assert_stopped(
            WalkToPose().tick(context, self.goal(), self.command),
            "pose_position_uncertain",
        )

    def test_real_unknown_ball_noise_stays_unknown_to_kick_policy(self):
        self.inputs.pose()
        self.inputs.ball(noise=None)
        self.model.owner.advance(self.clock.now())
        context = capture_tick(self.model.reader, self.clock, 0)
        self.assertIsNone(context.world.current_local_ball().value.covariance)
        self.assert_stopped(
            Kick().tick(context, KickGoal(1, direction=0), self.command),
            "ball_uncertainty_unknown",
        )

    def test_circle_rejects_uncertain_half_turn_without_counting_it(self):
        context = self.with_pose_uncertainty(self.publish(x=1), 0.05)
        goal = WalkInCircleGoal(t.FramedPoint2(self.inputs.odom, t.Point2(0, 0)), 1)
        skill = WalkInCircle()
        skill.tick(context, goal, self.command)
        pose = context.world.self.odom_pose
        changed = replace(pose, value=replace(pose.value, pose=t.Pose2(-1, 0, pi)))
        context = self.changed(
            context, self=replace(context.world.self, odom_pose=changed)
        )
        self.assert_stopped(
            skill.tick(context, goal, self.command), "circle_progress_ambiguous"
        )
        self.assertEqual(skill.tick(context, goal, self.command).progress, 0)

    def test_retained_checked_estimate_preserves_metadata_and_covariance(self):
        context = self.publish()
        estimate = context.world.self.odom_pose
        checked = PosePolicy().assess(estimate)
        self.assertIs(checked.estimate, estimate)
        self.assertIs(checked.estimate.meta, estimate.meta)
        self.assertIs(checked.estimate.covariance, estimate.covariance)
        self.assertEqual(context.world.snapshot, self.model.reader.latest().snapshot)

    def test_policy_validation_rejects_unbounded_or_invalid_limits(self):
        for constructor, options in (
            (PosePolicy, {"max_position_std_m": float("inf")}),
            (PosePolicy, {"minimum_speed_scale": 2}),
            (PosePolicy, {"allowed_qualities": ()}),
            (KickPolicy, {"margin_sigma": 0}),
            (KickPolicy, {"max_ball_std_m": -1}),
        ):
            with self.subTest(options=options), self.assertRaises(ValueError):
                constructor(**options)

    def test_runnable_demo(self):
        main()

    def test_new_import_does_not_load_ros_sdk_or_legacy_model(self):
        import subprocess

        code = """
import importlib.abc
import sys
class Guard(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'rclpy', 'ament_index_python', 'legacy_world_model',
                                      'booster_robotics_sdk_python', 'world_model_ros'}:
            raise AssertionError(fullname)
sys.meta_path.insert(0, Guard())
import skills.world
import world_skills_demo
world_skills_demo.main()
"""
        subprocess.run(
            [sys.executable, "-c", code],
            cwd=SCRIPTS,
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )


if __name__ == "__main__":
    unittest.main()

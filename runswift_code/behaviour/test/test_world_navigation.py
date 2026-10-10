"""Real world-model inputs through navigation, with controlled time and no robot I/O."""

import builtins
import sys
import unittest
from dataclasses import FrozenInstanceError, fields, replace
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from action.types import MotionCommand
from navigation_planner import GlobalPlanner, GlobalPlannerConfig
from navigation_types import NavPath, PlanningField
from path_tracker import PathTracker
from skills.base import SkillStatus
from skills.navigation_policy import NavigationPolicy
from skills.world import NavigateToPose, NavigateToPoseGoal, ReadLimits
from world_skills_demo import (
    DEMO_EXACT,
    DemoInputs,
    ReplayClock,
    make_config,
    transform,
)

from world_model import (
    WorldView,
    capture_tick,
    create_world_model,
    noise_from_covariance,
)
from world_model import types as t

MS = 1_000_000
SECOND = 1_000 * MS


class NavigationWorldTest(unittest.TestCase):
    def setUp(self):
        self.clock = ReplayClock()
        base = make_config()
        self.config = replace(
            base,
            obstacles=t.ObstacleConfig(
                SECOND, 16, 0.04, coverage=t.ObstacleCoverageConfig(200 * MS)
            ),
            spatial=replace(
                base.spatial,
                links=base.spatial.links + (t.FrameLink("odom", "team_field"),),
            ),
        )
        self.rebuild()
        self.command = MotionCommand()

    def navigation(self, **kwargs):
        # These integration cases deliberately exercise known-obstacle planning.
        # Coverage policy itself is tested separately below.
        kwargs.setdefault(
            "navigation_policy", NavigationPolicy(unknown_space="allow_unknown")
        )
        return NavigateToPose(**kwargs)

    def rebuild(self):
        self.model = create_world_model(config=self.config, clock=self.clock)
        self.inputs = DemoInputs(self.model.input, self.clock, self.config)

    def goal(self, x=2.0, **changes):
        return NavigateToPoseGoal(
            t.FramedPose2(self.config.field.frame, t.Pose2(x, 0, 0)), **changes
        )

    def publish(
        self,
        ns=0,
        *,
        x=0.0,
        obstacles=(),
        vision=True,
        odometry=True,
        localisation=True,
        localisation_epoch=None,
        calibration="demo-calibration",
        pose_noise=DEMO_EXACT,
        field_noise=DEMO_EXACT,
        obstacle_noise=DEMO_EXACT,
        coverage=None,
    ):
        self.clock.ns = ns
        if odometry:
            self.inputs.pose(x, noise=pose_noise)
        if localisation:
            self.inputs.submit(
                "field-localisation",
                t.KinematicTransformSample(
                    self.inputs.odom,
                    self.config.field.frame,
                    self.clock.now(),
                    replace(self.clock.now(), ns=ns + SECOND),
                    transform(),
                    field_noise,
                    "demo-model",
                    calibration,
                ),
            )
        if localisation_epoch is not None:
            self.inputs.submit(
                "localisation-reset",
                t.LocalisationEstimate(
                    t.FramedPose2(self.config.field.frame, t.Pose2(x, 0, 0)),
                    self.clock.now(),
                    None,
                    "nominal",
                    localisation_epoch,
                ),
            )
        if vision:
            detections = tuple(
                t.ObstacleDetection(
                    t.FramedPoint2(
                        self.inputs.base, t.Point2(*point[:2]), self.clock.now()
                    ),
                    radius_m=point[2] if len(point) > 2 else 0.28,
                    confidence=0.9,
                    track_id=str(index),
                    noise=obstacle_noise,
                )
                for index, point in enumerate(obstacles)
            )
            self.inputs.submit(
                "vision",
                t.VisionFrame(
                    "image",
                    "demo-calibration",
                    (),
                    obstacles=detections,
                    obstacle_coverage=coverage,
                ),
            )
        self.model.owner.advance(self.clock.now())
        return capture_tick(self.model.reader, self.clock, ns)

    def test_planning_reserve_adds_tracking_room_without_relaxing_collision_checks(
        self,
    ):
        context = self.publish(obstacles=((2, 0, 0.45),))
        widths = []
        for slack in (0.03, 0.2):
            skill = self.navigation(
                planner=GlobalPlanner(
                    GlobalPlannerConfig(10, False, 0.25, tracking_reserve_m=slack)
                )
            )
            result = skill.tick(context, self.goal(4.0), self.command)
            self.assertEqual(result.status, SkillStatus.RUNNING, result.reason)
            widths.append(max(abs(p[1]) for p in skill.debug.path))
            self.assertIsNone(
                skill.evidence.scene.path_reason(skill.debug.path, start=(0.0, 0.0))
            )
            self.assertEqual(skill.evidence.scene.obstacles[0].radius_m, 0.45)
        self.assertGreater(widths[1], widths[0] + 0.1)
        for invalid in (-0.1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                GlobalPlannerConfig(10, False, 0.25, tracking_reserve_m=invalid)

    def test_tracking_reserve_also_prevents_a_tight_direct_shortcut(self):
        context = self.publish(obstacles=((2, 1.05, 0.45),))
        for reserve, direct in ((0.0, True), (0.2, False)):
            skill = self.navigation(
                planner=GlobalPlanner(
                    GlobalPlannerConfig(10, False, 0.25, tracking_reserve_m=reserve)
                )
            )
            result = skill.tick(context, self.goal(4.0), self.command)
            self.assertEqual(result.status, SkillStatus.RUNNING, result.reason)
            self.assertEqual(len(skill.debug.path) == 2, direct)
            self.assertIsNone(
                skill.evidence.scene.path_reason(skill.debug.path, start=(0.0, 0.0))
            )

    def stopped(self, skill, context, reason, goal=None):
        self.command.set_body(0.5, 0.1, 0.1)
        self.command.set_kick(0, 1, 1, 0)
        result = skill.tick(context, goal or self.goal(), self.command)
        self.assertEqual(result.status, SkillStatus.FAILED)
        self.assertEqual(result.reason, reason)
        self.assertEqual(
            (self.command.x, self.command.y, self.command.theta), (0, 0, 0)
        )
        self.assertFalse(self.command.kick_active)
        self.assertIsNone(skill.debug.path)
        self.assertIsNone(skill.evidence)
        self.assertIsNone(skill._navigation._planner._cache)
        self.assertIsNone(skill._navigation._tracker._prepared)

    def active(self, *, ns=0, localisation_epoch=None):
        skill = self.navigation()
        context = self.publish(
            ns, obstacles=((1, 0),), localisation_epoch=localisation_epoch
        )
        result = skill.tick(context, self.goal(), self.command)
        self.assertEqual(result.status, SkillStatus.RUNNING, result.reason)
        self.assertIsNotNone(skill._navigation._planner._cache)
        self.assertIsNotNone(skill._navigation._tracker._prepared)
        return skill, context

    def test_goal_contains_only_intentions_and_options(self):
        names = {item.name for item in fields(NavigateToPoseGoal)}
        self.assertFalse(
            names.intersection(
                {"robot_pose", "obstacles", "field", "now", "go_ball_pos"}
            )
        )
        with self.assertRaises(FrozenInstanceError):
            self.goal().keep_out = 0.1
        with self.assertRaises(ValueError):
            self.goal(x=float("nan"))
        for kwargs in (
            {"keep_out": -1},
            {"speed_scale": -1},
            {"speed_scale": float("nan")},
            {"safety_margin": -1},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.goal(**kwargs)

    def test_real_pose_obstacles_and_geometry_all_come_from_held_tick(self):
        held = self.publish(obstacles=((1, 0),))
        self.publish(100 * MS, x=2, obstacles=((0, 2),))
        skill = self.navigation()
        # No reader or owner is reachable from the adapter; retain an older valid tick.
        with (
            patch.object(
                type(self.model.reader),
                "latest",
                side_effect=AssertionError("live read"),
            ),
            patch.object(
                type(self.model.owner),
                "advance",
                side_effect=AssertionError("world update"),
            ),
        ):
            result = skill.tick(held, self.goal(), self.command)
        self.assertEqual(result.status, SkillStatus.RUNNING)
        self.assertEqual(skill.evidence.snapshot_id, held.world.snapshot.id)
        self.assertIs(skill.evidence.field, held.world.snapshot.field)
        self.assertIs(skill.evidence.pose, held.world.self.field_pose.summary)
        self.assertEqual(
            skill.evidence.obstacles,
            held.world.obstacles_in(self.config.field.frame).value,
        )
        self.assertGreater(
            len(skill.debug.path), 2
        )  # Real detour around the held obstacle.
        self.assertEqual(skill.evidence.obstacles.estimates[0].value.position.x, 1)
        self.assertEqual(skill.evidence.obstacles.coverage, "unknown")
        self.assertIsNotNone(skill.evidence.obstacles.estimates[0].covariance)

    def test_replanning_uses_decision_time_and_reuses_cache_within_interval(self):
        skill = self.navigation(replan_period_sec=0.25)
        planner = skill._navigation._planner
        with patch.object(planner, "_run_plan", wraps=planner._run_plan) as plan:
            context = self.publish(obstacles=((1, 0),))
            context = replace(context, now=replace(context.now, ns=20 * MS))
            with patch(
                "time.monotonic", side_effect=AssertionError("wall-clock decision")
            ):
                skill.tick(context, self.goal(), self.command)
            self.assertEqual(planner._cache["mono_sec"], 0.02)
            second = self.publish(100 * MS, obstacles=((1, 0),))
            skill.tick(second, self.goal(), self.command)
            self.assertEqual(plan.call_count, 1)
            skill.tick(
                self.publish(300 * MS, obstacles=((1, 0),)), self.goal(), self.command
            )
            self.assertEqual(plan.call_count, 2)

    def test_cancel_and_exit_discard_planner_tracker_and_progress(self):
        skill, context = self.active()
        skill.cancel(self.command)
        self.assertIsNone(skill.debug.path)
        self.assertIsNone(skill.evidence)
        self.assertIsNone(skill._navigation._planner._cache)
        self.assertIsNone(skill._navigation._tracker._prepared)
        self.assertEqual(self.command.x, 0)
        result = skill.tick(context, self.goal(), self.command)
        self.assertEqual(result.status, SkillStatus.RUNNING)
        skill.on_exit()
        self.assertIsNone(skill._navigation._planner._cache)
        self.assertIsNone(skill._navigation._tracker._prepared)

    def test_changed_goal_discards_cache_even_below_planner_goal_tolerance(self):
        skill, context = self.active()
        planner = skill._navigation._planner
        with patch.object(planner, "_run_plan", wraps=planner._run_plan) as plan:
            skill.tick(context, self.goal(x=2.05), self.command)
            self.assertEqual(plan.call_count, 1)
        self.assertAlmostEqual(planner._cache["plan_goal"][0], 2.05)

    def test_stale_held_context_clears_previous_intents_and_cache(self):
        skill, context = self.active()
        stale = replace(context, now=replace(context.now, ns=200 * MS))
        self.stopped(skill, stale, "stale_snapshot")
        self.assertEqual(context.world.obstacles.tracks[0].visibility, "observed")

    def test_pose_loss_cancels_and_recovery_builds_a_new_path(self):
        skill, _ = self.active()
        self.stopped(
            skill, self.publish(100 * MS, localisation=False), "pose_unavailable"
        )
        planner = skill._navigation._planner
        with patch.object(planner, "_run_plan", wraps=planner._run_plan) as plan:
            recovered = self.publish(200 * MS, obstacles=((1, 0),))
            result = skill.tick(recovered, self.goal(), self.command)
            self.assertEqual(result.status, SkillStatus.RUNNING)
            self.assertEqual(plan.call_count, 1)

    def test_localisation_reset_clears_path_and_next_checked_tick_can_restart(self):
        skill, _ = self.active(localisation_epoch="loc-1")
        reset = self.publish(100 * MS, obstacles=((1, 0),), localisation_epoch="loc-2")
        self.stopped(skill, reset, "localisation_changed")
        self.assertEqual(
            skill.tick(reset, self.goal(), self.command).status, SkillStatus.RUNNING
        )

    def test_odom_frame_and_calibration_resets_discard_cached_paths(self):
        for mode in ("frame", "calibration"):
            with self.subTest(mode=mode):
                self.setUp()
                skill, _ = self.active()
                if mode == "frame":
                    self.inputs.odom = replace(self.inputs.odom, epoch="odom-reset")
                context = self.publish(
                    100 * MS,
                    obstacles=((1, 0),),
                    calibration="changed"
                    if mode == "calibration"
                    else "demo-calibration",
                )
                self.stopped(skill, context, "navigation_frame_changed")

    def test_field_change_and_incompatible_goal_frame_stop(self):
        skill, context = self.active()
        changed = replace(
            context,
            world=WorldView(
                replace(
                    context.world.snapshot,
                    field=replace(
                        context.world.snapshot.field, geometry_id="new-layout"
                    ),
                )
            ),
        )
        self.stopped(skill, changed, "navigation_frame_changed")
        for frame, reason in (
            (self.inputs.odom, "navigation_requires_field_target"),
            (
                replace(self.config.field.frame, epoch="old"),
                "navigation_field_frame_mismatch",
            ),
        ):
            goal = replace(self.goal(), target=t.FramedPose2(frame, t.Pose2(2, 0, 0)))
            self.stopped(self.navigation(), context, reason, goal)

    def test_world_clock_and_backwards_time_discard_navigation_state(self):
        for mode in ("world", "clock", "backwards"):
            with self.subTest(mode=mode):
                self.setUp()
                skill, context = self.active()
                if mode == "world":
                    context = replace(
                        context,
                        world=WorldView(
                            replace(
                                context.world.snapshot,
                                id=replace(
                                    context.world.snapshot.id, world_epoch="new-world"
                                ),
                            )
                        ),
                    )
                    reason = "world_or_clock_changed"
                elif mode == "clock":
                    now = replace(context.now, clock_epoch="new-clock")
                    context = replace(
                        context,
                        now=now,
                        world=WorldView(
                            replace(context.world.snapshot, as_of=now, published_at=now)
                        ),
                    )
                    reason = "world_or_clock_changed"
                else:
                    skill.tick(
                        replace(context, now=replace(context.now, ns=100 * MS)),
                        self.goal(),
                        self.command,
                    )
                    context = replace(context, now=replace(context.now, ns=50 * MS))
                    reason = "decision_time_reversed"
                self.stopped(skill, context, reason)

    def test_no_detector_frame_and_stale_detector_input_are_explicit(self):
        self.stopped(
            self.navigation(), self.publish(vision=False), "no_obstacle_frames"
        )
        self.publish()
        context = self.publish(100 * MS, vision=False)
        self.stopped(
            self.navigation(limits=ReadLimits(evidence_ns=50 * MS)),
            context,
            "stale_obstacle_input",
        )
        self.stopped(
            self.navigation(),
            self.publish(SECOND, vision=False),
            "obstacle_input_stale",
        )

    def test_per_obstacle_age_cannot_be_refreshed_by_an_empty_frame(self):
        self.publish(obstacles=((1, 0),))
        context = self.publish(100 * MS)
        skill = self.navigation(limits=ReadLimits(evidence_ns=50 * MS))
        self.stopped(skill, context, "obstacle_stale_evidence")

    def test_collection_and_pose_expiry_are_checked_at_decision_time(self):
        self.config = replace(
            self.config, obstacles=replace(self.config.obstacles, max_age_ns=100 * MS)
        )
        self.rebuild()
        context = self.publish()
        held = replace(context, now=replace(context.now, ns=100 * MS))
        self.stopped(self.navigation(), held, "expired_obstacle_input")
        held = replace(context, now=replace(context.now, ns=SECOND))
        self.stopped(
            self.navigation(
                limits=ReadLimits(snapshot_ns=2 * SECOND, state_ns=2 * SECOND)
            ),
            held,
            "expired_estimate",
        )

    def test_missing_capture_transform_reports_incomplete_obstacles(self):
        self.publish(obstacles=((1, 0),), odometry=False)
        context = self.publish(50 * MS)
        self.assertTrue(
            context.world.obstacles_in(
                self.config.field.frame
            ).value.unavailable_track_ids
        )
        self.stopped(self.navigation(), context, "obstacle_conversions_unavailable")

    def test_memory_eviction_and_planner_capacity_never_silently_drop_obstacles(self):
        self.config = replace(
            self.config, obstacles=replace(self.config.obstacles, max_tracks=1)
        )
        self.rebuild()
        self.publish(obstacles=((1, 0),))
        self.inputs.submit(
            "second-camera",
            t.VisionFrame(
                "other",
                "demo-calibration",
                (),
                obstacles=(
                    t.ObstacleDetection(
                        t.FramedPoint2(
                            self.inputs.base, t.Point2(0, 1), self.clock.now()
                        ),
                        0.28,
                        0.9,
                        noise=DEMO_EXACT,
                    ),
                ),
            ),
        )
        self.model.owner.advance(self.clock.now())
        self.stopped(
            self.navigation(),
            capture_tick(self.model.reader, self.clock, 1),
            "obstacle_memory_incomplete",
        )
        self.setUp()
        context = self.publish(obstacles=((1, 0), (1, 1)))
        self.stopped(
            self.navigation(max_obstacles=1), context, "navigation_obstacle_capacity"
        )

    def test_unreliable_empty_detector_time_does_not_become_a_complete_scene(self):
        context = self.publish()
        memory = context.world.obstacles
        memory = replace(
            memory, last_frame=replace(memory.last_frame, time_quality="receive_only")
        )
        context = replace(
            context, world=WorldView(replace(context.world.snapshot, obstacles=memory))
        )
        self.stopped(self.navigation(), context, "obstacle_input_time_unknown")

    def test_pose_and_obstacle_state_must_share_publication_time(self):
        context = self.publish()
        old = replace(
            context.world.self.field_pose.summary,
            meta=replace(
                context.world.self.field_pose.summary.meta,
                state_at=replace(context.now, ns=-MS),
            ),
        )
        altered = replace(
            context,
            world=WorldView(
                replace(
                    context.world.snapshot,
                    self=replace(
                        context.world.self,
                        field_pose=replace(context.world.self.field_pose, summary=old),
                    ),
                )
            ),
        )
        self.stopped(self.navigation(), altered, "navigation_pose_time_mismatch")

    def test_field_dimensions_and_goal_mouths_are_supplied_without_legacy_imports(self):
        original_import = builtins.__import__

        def guarded(name, *args, **kwargs):
            if name.split(".")[0] in {
                "legacy_world_model",
                "bigbrother",
                "rclpy",
                "rerun",
                "booster_robotics_sdk_python",
            }:
                raise AssertionError("Unexpected navigation dependency: " + name)
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=guarded):
            context = self.publish()
            skill = self.navigation()
            self.assertEqual(
                skill.tick(context, self.goal(), self.command).status,
                SkillStatus.RUNNING,
            )
            small = replace(
                context.world.snapshot.field,
                length=3.0,
                width=2.0,
                own_goal=t.GoalGeometry(t.Point2(-1.5, 0), 1),
                opponent_goal=t.GoalGeometry(t.Point2(1.5, 0), 1),
                playing_boundary=t.Polygon(
                    (
                        t.Point2(-1.5, -1),
                        t.Point2(1.5, -1),
                        t.Point2(1.5, 1),
                        t.Point2(-1.5, 1),
                    )
                ),
            )
            context = replace(
                context, world=WorldView(replace(context.world.snapshot, field=small))
            )
            self.stopped(self.navigation(), context, "navigation_target_outside_field")
            self.stopped(
                self.navigation(),
                context,
                "navigation_target_outside_field",
                self.goal(x=1.5),
            )
            self.assertEqual(
                self.navigation().tick(context, self.goal(x=1), self.command).status,
                SkillStatus.RUNNING,
            )

    def test_non_rectangular_field_is_not_silently_replaced_by_dimensions(self):
        context = self.publish()
        field = replace(
            context.world.snapshot.field,
            playing_boundary=t.Polygon(
                (t.Point2(0, 0), t.Point2(1, 0), t.Point2(0, 1))
            ),
        )
        context = replace(
            context, world=WorldView(replace(context.world.snapshot, field=field))
        )
        self.stopped(self.navigation(), context, "unsupported_navigation_field")

    def test_pose_uncertainty_and_arrival_reuse_existing_skill_policy(self):
        context = self.publish(field_noise=None)
        self.stopped(self.navigation(), context, "pose_uncertainty_unknown")
        self.setUp()
        goal = self.goal(x=0.29)
        context = self.publish(
            pose_noise=noise_from_covariance(
                (
                    (0.0001, 0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0, 0),
                ),
                "pose-noise",
            )
        )
        skill = self.navigation()
        result = skill.tick(context, goal, self.command)
        self.assertEqual(result.reason, "arrival_uncertain")
        self.assertEqual(self.command.x, 0)
        exact = self.publish(10 * MS)
        self.assertEqual(
            skill.tick(exact, goal, self.command).status, SkillStatus.SUCCEEDED
        )

    def test_zero_speed_pauses_and_discards_cached_path(self):
        skill, context = self.active()
        result = skill.tick(context, self.goal(speed_scale=0), self.command)
        self.assertEqual(result.reason, "navigation_paused")
        self.assertEqual(
            (self.command.x, self.command.y, self.command.theta), (0, 0, 0)
        )
        self.assertIsNone(skill._navigation._planner._cache)
        self.assertIsNone(skill._navigation._tracker._prepared)

    def test_planner_failure_discards_both_caches(self):
        skill, context = self.active()
        planner = skill._navigation._planner
        with patch.object(
            planner,
            "update",
            return_value=(None, type("Selected", (), {"selected": []})()),
        ):
            self.stopped(skill, context, "no_path")

    def test_track_cache_uses_all_waypoints_and_headings(self):
        tracker = PathTracker()
        path = NavPath(
            [
                (0, 0, 0, "a"),
                (1, 0, 0, "b"),
                (2, 0, 0, "c"),
                (3, 0, 0, "d"),
                (4, 0, 0, "e"),
            ],
            False,
            False,
        )
        prepared = tracker._prepare(path)
        changed = replace(
            path, waypoints=[path.waypoints[0], (1, 1, 0.5, "b"), *path.waypoints[2:]]
        )
        new = tracker._prepare(changed)
        self.assertIsNot(prepared, new)
        self.assertEqual(new.pts[1, 1], 1)
        self.assertEqual(new.ths[1], 0.5)
        tracker.reset()
        self.assertIsNone(tracker._prepared)

    def test_legacy_planner_caller_still_gets_compatibility_field(self):
        import numpy as np

        planner = GlobalPlanner(GlobalPlannerConfig(10, False, 0.25))
        with patch(
            "navigation_planner.legacy_field",
            return_value=PlanningField(9, 6, ((-4.5, 0, 2), (4.5, 0, 2))),
        ) as old:
            path, _ = planner.update(
                now_mono=0,
                X0=np.array([0, 0, 0]),
                plan_goal=np.array([2, 0, 0]),
                raw_obstacles=[],
                keep_out=0.6,
            )
        self.assertEqual(old.call_count, 1)
        self.assertTrue(path.direct)

    def test_source_failure_is_not_ignored_by_fresh_estimate_times(self):
        skill, context = self.active()
        health = tuple(
            replace(item, status="stalled") if item.component == "vision" else item
            for item in context.world.snapshot.health
        )
        context = replace(
            context, world=WorldView(replace(context.world.snapshot, health=health))
        )
        self.stopped(skill, context, "navigation_source_unavailable")

    def test_injected_components_must_support_cancellation_and_full_capacity(self):
        with self.assertRaises(ValueError):
            self.navigation(tracker=object())
        with self.assertRaises(ValueError):
            self.navigation(
                max_obstacles=10,
                planner=GlobalPlanner(GlobalPlannerConfig(5, False, 0.25)),
            )

    def report(self, *, ns=0, **changes):
        def box(left, bottom, right, top):
            return t.Polygon(
                (
                    t.Point2(left, bottom),
                    t.Point2(right, bottom),
                    t.Point2(right, top),
                    t.Point2(left, top),
                )
            )

        region = box(-1, -2, 3, 2)
        return replace(
            t.ObstacleCoverage(
                self.config.field.frame,
                replace(self.clock.now(), ns=ns),
                replace(self.clock.now(), ns=ns + 200 * MS),
                "ground-robots:v1",
                (region,),
                (region,),
                boundary_error_m=0.01,
            ),
            **changes,
        )

    def test_navigation_policy_rejects_invalid_configuration(self):
        for kwargs in (
            {"robot_radius_m": 0},
            {"clearance_m": -1},
            {"uncertainty_sigma": 0},
            {"obstacle_speed_bound_mps": -1},
            {"command_horizon_sec": 0},
            {"max_unknown_speed_mps": float("nan")},
            {"unknown_space": "ignore"},
            {"coverage_profile": ""},
            {"allowed_obstacle_qualities": ()},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                NavigationPolicy(**kwargs)

    def test_empty_obstacle_list_requires_explicit_space_policy(self):
        context = self.publish()
        self.stopped(NavigateToPose(), context, "navigation_space_unobserved")
        slow = self.navigation(
            navigation_policy=NavigationPolicy(
                unknown_space="allow_unknown", max_unknown_speed_mps=0.07
            )
        )
        result = slow.tick(context, self.goal(), self.command)
        self.assertEqual(result.status, SkillStatus.RUNNING)
        self.assertLessEqual((self.command.x**2 + self.command.y**2) ** 0.5, 0.07000001)
        self.assertTrue(self.command.avoidance_applied)
        self.assertEqual(slow.evidence.obstacles.coverage, "unknown")

    def test_current_profile_matched_clear_corridor_allows_motion(self):
        context = self.publish(coverage=self.report())
        skill = NavigateToPose(
            navigation_policy=NavigationPolicy(coverage_profile="ground-robots:v1")
        )
        result = skill.tick(context, self.goal(), self.command)
        self.assertEqual(result.status, SkillStatus.RUNNING, result.reason)
        self.assertGreater(self.command.x, 0.2)
        self.assertEqual(skill.evidence.obstacles.coverage, "partial")
        self.assertIsNone(skill.evidence.scene.path_reason(skill.debug.path))

    def test_partial_coverage_is_not_a_whole_route_clear_claim(self):
        for mode in (
            "inspected_only",
            "wrong_profile",
            "wrong_frame",
            "short",
            "occluded",
            "boundary_error",
        ):
            with self.subTest(mode=mode):
                self.setUp()
                report = self.report()
                reason = "navigation_space_unobserved"
                if mode == "inspected_only":
                    report = replace(report, clear=())
                elif mode == "wrong_profile":
                    report = replace(report, profile_id="unrelated-detector")
                elif mode == "wrong_frame":
                    report = replace(report, frame=self.inputs.base)
                elif mode == "short":
                    report = replace(
                        report,
                        clear=(
                            t.Polygon(
                                (
                                    t.Point2(-1, -1),
                                    t.Point2(1, -1),
                                    t.Point2(1, 1),
                                    t.Point2(-1, 1),
                                )
                            ),
                        ),
                    )
                elif mode == "occluded":
                    report = replace(
                        report,
                        occluded=(
                            t.Polygon(
                                (
                                    t.Point2(0.8, -0.2),
                                    t.Point2(1.2, -0.2),
                                    t.Point2(1.2, 0.2),
                                    t.Point2(0.8, 0.2),
                                )
                            ),
                        ),
                    )
                    reason = "navigation_space_occluded"
                else:
                    report = replace(report, boundary_error_m=0.8)
                context = self.publish(coverage=report)
                self.stopped(
                    NavigateToPose(
                        navigation_policy=NavigationPolicy(
                            coverage_profile="ground-robots:v1"
                        )
                    ),
                    context,
                    reason,
                )

    def test_coverage_loss_and_occlusion_stop_cached_navigation(self):
        skill = NavigateToPose(
            navigation_policy=NavigationPolicy(coverage_profile="ground-robots:v1")
        )
        first = self.publish(coverage=self.report())
        self.assertEqual(
            skill.tick(first, self.goal(), self.command).status, SkillStatus.RUNNING
        )
        # A new empty detector frame supersedes the clear report, not renews it.
        self.stopped(skill, self.publish(100 * MS), "navigation_space_unobserved")
        self.assertEqual(
            first.world.obstacles_in(self.config.field.frame).value.coverage, "partial"
        )

    def test_cached_detour_is_rechecked_when_clear_evidence_disappears(self):
        occluded = t.Polygon(
            (
                t.Point2(0.7, -0.3),
                t.Point2(1.3, -0.3),
                t.Point2(1.3, 0.3),
                t.Point2(0.7, 0.3),
            )
        )
        report = self.report(occluded=(occluded,))
        skill = NavigateToPose(
            navigation_policy=NavigationPolicy(coverage_profile="ground-robots:v1")
        )
        first = self.publish(obstacles=((1, 0),), coverage=report)
        result = skill.tick(first, self.goal(), self.command)
        self.assertEqual(result.status, SkillStatus.RUNNING, result.reason)
        planner = skill._navigation._planner
        self.assertIsNotNone(planner._cache)
        with patch.object(planner, "_run_plan", wraps=planner._run_plan) as core:
            self.stopped(
                skill,
                self.publish(10 * MS, obstacles=((1, 0),)),
                "navigation_space_unobserved",
            )
        self.assertEqual(core.call_count, 1)

    def test_increased_pose_uncertainty_invalidates_cached_detour(self):
        skill = self.navigation(
            navigation_policy=NavigationPolicy(
                unknown_space="allow_unknown", obstacle_speed_bound_mps=0
            )
        )
        skill.tick(self.publish(obstacles=((1, 0, 0.1),)), self.goal(), self.command)
        old_path = list(skill.debug.path)
        noisy_pose = noise_from_covariance(
            tuple(
                tuple(0.0025 if i == j == 0 else 0 for j in range(6)) for i in range(6)
            ),
            "pose-growth",
        )
        planner = skill._navigation._planner
        with patch.object(planner, "_run_plan", wraps=planner._run_plan) as core:
            result = skill.tick(
                self.publish(10 * MS, obstacles=((1, 0, 0.1),), pose_noise=noisy_pose),
                self.goal(),
                self.command,
            )
        self.assertEqual(result.status, SkillStatus.RUNNING, result.reason)
        self.assertEqual(core.call_count, 1)
        self.assertIsNotNone(skill.evidence.scene.path_reason(old_path))
        self.assertIsNone(skill.evidence.scene.path_reason(skill.debug.path))

    def test_expired_coverage_and_unhealthy_coverage_source_do_not_authorise_motion(
        self,
    ):
        report = self.report(valid_until=replace(self.clock.now(), ns=50 * MS))
        context = self.publish(coverage=report)
        held = replace(context, now=replace(context.now, ns=50 * MS))
        self.stopped(
            NavigateToPose(
                navigation_policy=NavigationPolicy(coverage_profile="ground-robots:v1")
            ),
            held,
            "expired_obstacle_input",
        )
        # The policy also rejects an unhealthy source even when its report is usable.
        context = replace(
            context,
            world=WorldView(
                replace(
                    context.world.snapshot,
                    health=tuple(
                        replace(h, status="stalled") if h.component == "vision" else h
                        for h in context.world.snapshot.health
                    ),
                )
            ),
        )
        self.stopped(NavigateToPose(), context, "navigation_source_unavailable")

    def test_individual_radii_and_covariance_reach_underlying_planner(self):
        from navigation_planner import plan

        noise = noise_from_covariance(
            ((0.0004, 0.0003), (0.0003, 0.0004)), "correlated-obstacle"
        )
        context = self.publish(
            obstacles=((1, 2, 0.4), (1, 0, 0.1)), obstacle_noise=noise
        )
        skill = self.navigation(
            navigation_policy=NavigationPolicy(
                unknown_space="allow_unknown",
                robot_radius_m=0.2,
                clearance_m=0.05,
                obstacle_speed_bound_mps=0,
            )
        )
        with patch("navigation_planner.plan", wraps=plan) as core:
            result = skill.tick(context, self.goal(), self.command)
        self.assertEqual(result.status, SkillStatus.RUNNING, result.reason)
        scene = skill.evidence.scene
        self.assertEqual([o.radius_m for o in scene.obstacles], [0.4, 0.1])
        for item, estimate in zip(scene.obstacles, skill.evidence.obstacles.estimates):
            self.assertEqual(item.covariance, estimate.covariance.matrix)
            self.assertAlmostEqual(item.uncertainty_margin_m, 3 * 0.0007**0.5)
            self.assertAlmostEqual(
                item.keep_out_m, item.radius_m + 0.25 + 3 * 0.0007**0.5
            )
        supplied = core.call_args.args[2]
        by_centre = {o.centre: o.keep_out_m for o in scene.obstacles}
        self.assertEqual(
            tuple(supplied.centers[0]), (1, 0)
        )  # Selection reordered input.
        for centre, radius in zip(supplied.centers, supplied.radii):
            self.assertEqual(radius, by_centre[tuple(centre)])
        self.assertEqual(core.call_args.args[3].field_margin, 0)
        self.assertAlmostEqual(
            supplied.field_halfsize[0], self.config.field.length / 2 - 0.25
        )
        self.assertIsNone(scene.path_reason(skill.debug.path))

    def test_radius_or_covariance_growth_invalidates_cache_before_replan_period(self):
        for mode in ("radius", "covariance"):
            with self.subTest(mode=mode):
                self.setUp()
                skill = self.navigation(
                    navigation_policy=NavigationPolicy(
                        unknown_space="allow_unknown", obstacle_speed_bound_mps=0
                    )
                )
                skill.tick(
                    self.publish(obstacles=((1, 0, 0.1),)), self.goal(), self.command
                )
                old_path = list(skill.debug.path)
                kwargs = (
                    {"obstacles": ((1, 0, 0.4),)}
                    if mode == "radius"
                    else {
                        "obstacles": ((1, 0, 0.1),),
                        "obstacle_noise": noise_from_covariance(
                            ((0.01, 0), (0, 0.01)), "new-noise"
                        ),
                    }
                )
                planner = skill._navigation._planner
                with patch.object(
                    planner, "_run_plan", wraps=planner._run_plan
                ) as core:
                    result = skill.tick(
                        self.publish(10 * MS, **kwargs), self.goal(), self.command
                    )
                self.assertEqual(result.status, SkillStatus.RUNNING, result.reason)
                self.assertEqual(core.call_count, 1)
                self.assertEqual(
                    skill.debug.planner_debug["replan_reason"], "path_blocked"
                )
                self.assertIsNotNone(skill.evidence.scene.path_reason(old_path))
                self.assertIsNone(skill.evidence.scene.path_reason(skill.debug.path))

    def test_new_obstacle_invalidates_direct_route_immediately(self):
        skill = self.navigation()
        skill.tick(self.publish(), self.goal(), self.command)
        self.assertEqual(len(skill.debug.path), 2)
        result = skill.tick(
            self.publish(10 * MS, obstacles=((1, 0),)), self.goal(), self.command
        )
        self.assertEqual(result.status, SkillStatus.RUNNING)
        self.assertGreater(len(skill.debug.path), 2)
        self.assertIsNone(skill.evidence.scene.path_reason(skill.debug.path))

    def test_unknown_obstacle_covariance_never_becomes_zero(self):
        context = self.publish(obstacles=((1, 0),), obstacle_noise=None)
        skill = self.navigation(
            navigation_policy=NavigationPolicy(
                unknown_space="allow_unknown",
                allowed_obstacle_qualities=("nominal", "degraded", "unknown"),
            )
        )
        self.stopped(skill, context, "obstacle_uncertainty_unknown")

    def test_invalid_and_wrong_frame_covariance_stop_navigation(self):
        context = self.publish(obstacles=((1, 0),))
        for mode in ("frame", "indefinite"):
            memory = context.world.obstacles
            views = tuple(
                replace(
                    e,
                    covariance=replace(
                        e.covariance,
                        **(
                            {"frame": self.inputs.odom}
                            if mode == "frame"
                            else {"matrix": ((0.01, 0.02), (0.02, 0.01))}
                        ),
                    ),
                )
                if e.value.frame == self.config.field.frame
                else e
                for e in memory.views
            )
            altered = replace(
                context,
                world=WorldView(
                    replace(
                        context.world.snapshot, obstacles=replace(memory, views=views)
                    )
                ),
            )
            self.stopped(
                self.navigation(),
                altered,
                "obstacle_covariance_convention"
                if mode == "frame"
                else "obstacle_covariance_invalid",
            )

    def test_pose_and_obstacle_margins_are_summed_without_independence_assumption(self):
        pose_noise = noise_from_covariance(
            tuple(
                tuple(0.0001 if i == j == 0 else 0 for j in range(6)) for i in range(6)
            ),
            "shared-pose",
        )
        context = self.publish(obstacles=((1, 0, 0.1),), pose_noise=pose_noise)
        skill = self.navigation(
            navigation_policy=NavigationPolicy(
                unknown_space="allow_unknown", obstacle_speed_bound_mps=0
            )
        )
        result = skill.tick(context, self.goal(), self.command)
        self.assertEqual(result.status, SkillStatus.RUNNING)
        # Both field-frame marginals contain the shared x uncertainty. We keep
        # the conservative sum rather than pretending those errors independent.
        self.assertAlmostEqual(
            skill.evidence.scene.obstacles[0].uncertainty_margin_m, 0.06
        )
        self.assertAlmostEqual(skill.evidence.scene.field_margin_m, 0.35)

    def test_motion_bound_includes_decision_age_and_command_horizon(self):
        context = self.publish(obstacles=((1.5, 1, 0.1),))
        context = replace(context, now=replace(context.now, ns=100 * MS))
        policy = NavigationPolicy(
            unknown_space="allow_unknown",
            obstacle_speed_bound_mps=0.4,
            command_horizon_sec=0.3,
        )
        skill = self.navigation(navigation_policy=policy)
        skill.tick(context, self.goal(), self.command)
        self.assertAlmostEqual(
            skill.evidence.scene.obstacles[0].keep_out_m, 0.1 + 0.28 + 0.04 + 0.4 * 0.4
        )

    def test_planner_cannot_return_a_path_through_an_inflated_obstacle(self):
        import numpy as np

        context = self.publish(obstacles=((1, 0),))
        with patch(
            "navigation_planner.plan",
            return_value=(np.array([[0, 0, 0], [2, 0, 0]]), {}),
        ):
            self.stopped(self.navigation(), context, "navigation_obstacle_clearance")

    def test_robot_size_and_clearance_apply_to_field_edges(self):
        context = self.publish()
        self.stopped(
            self.navigation(
                navigation_policy=NavigationPolicy(
                    unknown_space="allow_unknown", robot_radius_m=0.5, clearance_m=0.2
                )
            ),
            context,
            "navigation_target_outside_field",
            self.goal(x=self.config.field.length / 2 - 0.6),
        )

    def test_tracker_correction_is_limited_using_the_same_footprints(self):
        import numpy as np
        from navigation_types import NavigationCommand, TrackerResult

        context = self.publish(obstacles=((0.7, 0.4, 0.1),))
        skill = self.navigation(
            navigation_policy=NavigationPolicy(
                unknown_space="allow_unknown",
                robot_radius_m=0.2,
                clearance_m=0.02,
                obstacle_speed_bound_mps=0,
                max_unknown_speed_mps=2,
            )
        )
        proposal = TrackerResult(
            NavigationCommand(0.8, 0.6, 0, "test"), np.zeros(3), 0, 0, 0, 0
        )
        with patch.object(skill._navigation._tracker, "track", return_value=proposal):
            result = skill.tick(context, self.goal(), self.command)
        self.assertEqual(result.status, SkillStatus.RUNNING)
        self.assertEqual(result.reason, "navigation_command_limited")
        self.assertLess(self.command.x, 0.8)
        self.assertGreater(self.command.x, 0)
        self.assertTrue(self.command.avoidance_applied)
        scene = skill.evidence.scene
        self.assertIsNone(scene.path_reason(skill.debug.path))
        self.assertEqual(
            scene.segment_reason((0, 0), (0.4, 0.3)), "navigation_obstacle_clearance"
        )
        self.assertIsNone(
            scene.segment_reason((0, 0), (0.5 * self.command.x, 0.5 * self.command.y))
        )

    def test_local_adjustment_after_tracking_cannot_bypass_margins(self):
        from skills.navigate_to_pose import NavigateToPoseRequest

        context = self.publish(obstacles=((0.7, 0.4, 0.1),))
        skill = self.navigation(
            navigation_policy=NavigationPolicy(
                unknown_space="allow_unknown",
                robot_radius_m=0.2,
                clearance_m=0.02,
                obstacle_speed_bound_mps=0,
                max_unknown_speed_mps=2,
            )
        )
        skill.tick(context, self.goal(), self.command)
        scene = skill.evidence.scene
        request = NavigateToPoseRequest(
            robot_pose=skill.evidence.pose.value.pose,
            target_pose=self.goal().target.pose,
            apply_avoidance=True,
            vx_limit=0.8,
            vy_limit=0.6,
        )
        with patch(
            "skills.walk_to_pose.avoid_opponents", return_value=(0.8, 0.6, 0)
        ) as adjust:
            result = skill._navigation.tick(
                request,
                self.command,
                now_mono=0,
                field=scene.field,
                collision_scene=scene,
            )
        adjust.assert_called_once()
        self.assertEqual(result.reason, "navigation_command_limited")
        self.assertTrue(self.command.avoidance_applied)
        self.assertLess(self.command.x, 0.8)
        self.assertIsNone(
            scene.segment_reason((0, 0), (0.5 * self.command.x, 0.5 * self.command.y))
        )

    def test_non_finite_controller_command_is_not_clamped_into_motion(self):
        for value in (float("nan"), float("inf")):
            skill = self.navigation()
            with patch.object(
                skill._navigation, "_plan_velocity", return_value=(value, 0, 0)
            ):
                self.stopped(skill, self.publish(), "navigation_command_invalid")


class NavigationCollisionGeometryTest(unittest.TestCase):
    def scene(self, **changes):
        from navigation_safety import CollisionScene

        return replace(
            CollisionScene(
                (),
                PlanningField(9, 6, ()),
                0.3,
                0.3,
                unknown_space="allow_unknown",
                max_unknown_speed_mps=2,
            ),
            **changes,
        )

    def obstacle(self, centre, radius=0.4):
        from navigation_types import PlanningObstacle

        return PlanningObstacle("test", centre, 0.1, ((0, 0), (0, 0)), 0, radius)

    def test_tangency_and_single_point_paths_are_blocked(self):
        scene = self.scene(obstacles=(self.obstacle((1, 0.4)),))
        self.assertEqual(
            scene.path_reason([(0, 0), (2, 0)]), "navigation_obstacle_clearance"
        )
        self.assertEqual(scene.path_reason([(1, 0)]), "navigation_obstacle_clearance")
        self.assertIsNone(scene.path_reason([(0, -0.01), (2, -0.01)]))

    def test_cached_path_rejoin_segment_is_checked_but_travelled_path_is_not(self):
        scene = self.scene(obstacles=(self.obstacle((0, 1)),))
        path = [(0, 0), (2, 0)]
        self.assertIsNone(scene.path_reason(path))
        self.assertEqual(
            scene.path_reason(path, start=(0, 2)), "navigation_obstacle_clearance"
        )
        behind = self.scene(obstacles=(self.obstacle((0, 0)),))
        self.assertIsNone(behind.path_reason(path, start=(1, 0)))

    def test_full_robot_disc_must_fit_clear_regions_without_bridging_seams(self):
        from navigation_safety import ClearRegion

        left = ((-1, -1), (1, -1), (1, 1), (-1, 1))
        right = ((1, -1), (3, -1), (3, 1), (1, 1))
        scene = self.scene(
            unknown_space="require_clear",
            regions=(ClearRegion((left, right), (left, right), (), 0),),
        )
        self.assertEqual(
            scene.segment_reason((0, 0), (2, 0)), "navigation_space_unobserved"
        )
        self.assertEqual(
            scene.segment_reason((0, 0), (0.7, 0)), "navigation_space_unobserved"
        )
        self.assertIsNone(scene.segment_reason((0, 0), (0.69, 0)))

    def test_occlusion_crossing_and_tangency_override_clear_and_allow_unknown(self):
        from navigation_safety import ClearRegion

        area = ((-2, -2), (3, -2), (3, 2), (-2, 2))
        hole = ((0.8, -0.2), (1.2, -0.2), (1.2, 0.2), (0.8, 0.2))
        for policy in ("allow_unknown", "require_clear"):
            scene = self.scene(
                unknown_space=policy,
                regions=(ClearRegion((area,), (area,), (hole,), 0),),
            )
            for a, b in (((0, 0), (2, 0)), ((0, 0.5), (2, 0.5)), ((1, 0), (1, 0))):
                self.assertEqual(
                    scene.segment_reason(a, b), "navigation_space_occluded"
                )
            self.assertIsNone(scene.segment_reason((0, 0.51), (2, 0.51)))

    def test_turning_body_velocity_uses_a_conservative_swept_envelope(self):
        from skills.base import Pose2

        # A left turn curves towards the obstacle even though the initial
        # straight segment is clear. A heading uncertainty has the same effect.
        scene = self.scene(
            obstacles=(self.obstacle((0.5, 0.5), 0.4),), command_horizon_sec=1
        )
        self.assertIsNone(scene.segment_reason((0, 0), (1, 0)))
        velocity, reason = scene.limit_command(Pose2(0, 0, 0), (1, 0, 1))
        self.assertEqual(reason, "navigation_command_limited")
        self.assertLess(velocity[0], 1)
        from math import cos, sin

        for step in range(101):
            time = step / 100
            point = (velocity[0] * sin(time), velocity[0] * (1 - cos(time)))
            self.assertGreater(
                ((point[0] - 0.5) ** 2 + (point[1] - 0.5) ** 2) ** 0.5, 0.4
            )
        uncertain = replace(scene, heading_margin_rad=0.8)
        velocity, _ = uncertain.limit_command(Pose2(0, 0, 0), (1, 0, 0))
        self.assertLess(velocity[0], 1)

    def test_final_command_cannot_start_in_collision_or_unknown_space(self):
        from skills.base import Pose2

        scene = self.scene(obstacles=(self.obstacle((0, 0)),))
        self.assertEqual(
            scene.limit_command(Pose2(0, 0, 0), (1, 0, 0)),
            (None, "navigation_obstacle_clearance"),
        )
        strict = self.scene(unknown_space="require_clear")
        self.assertEqual(
            strict.limit_command(Pose2(0, 0, 0), (0, 0, 1)),
            (None, "navigation_space_unobserved"),
        )


if __name__ == "__main__":
    unittest.main()

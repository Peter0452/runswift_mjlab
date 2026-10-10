"""Acceptance tests: real world core, match decisions, skills and expiring intents."""

import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "behaviour" / "scripts"))

from action.match_intent import MatchIntent, MatchIntentGate
from action.types import MotionCommand
from match_execution import MatchExecutive
from match_runner import MatchGoal, MatchPolicy, MatchRunner, MotionFeedback
from skills.base import SkillStatus
from skills.world import KickPolicy, NavigateToPose, NavigationPolicy
from world_match_replay import MatchReplayWorld, ReplayMotion, main, open_play_report
from world_model.adapters.booster import Frame, Robot

from world_model import WorldView
from world_model import types as wm

MS = 1_000_000
DEFAULT = object()


class MatchFixture:
    def setUp(self):
        self.world = MatchReplayWorld("match-test", radii={"robot2": 0.45})
        self.runner = MatchRunner(
            navigation=NavigateToPose(
                navigation_policy=NavigationPolicy(unknown_space="allow_unknown")
            )
        )
        self.goal = MatchGoal()
        self.command = MotionCommand()
        self.sequence = 0

    def context(
        self,
        ns=0,
        *,
        x=-2,
        ball=(0.0, 0.0, 0.11),
        report=DEFAULT,
        obstacle=None,
        localised=True,
    ):
        robots = (Robot("robot1", (x, 0, 0.7), 0, 1),)
        if obstacle is not None:
            robots += (Robot("robot2", (*obstacle, 0.7), 0, 1),)
        frame = Frame(ns, self.sequence, robots, ball)
        self.sequence += 1
        return self.world.publish(
            frame,
            report=open_play_report() if report is DEFAULT else report,
            localised=localised,
        )

    def tick(self, context, *, motion=DEFAULT, goal=None):
        if motion is DEFAULT:
            motion = MotionFeedback(context.now, True, True, True)
        return self.runner.tick(
            context, self.goal if goal is None else goal, self.command, motion=motion
        )

    def stopped(self):
        self.assertEqual(
            (self.command.x, self.command.y, self.command.theta), (0, 0, 0)
        )
        self.assertFalse(self.command.kick_active)


class MatchRunnerTest(MatchFixture, unittest.TestCase):
    def test_stand_search_approach_kick_and_official_stop(self):
        result = self.tick(
            self.context(ball=None, report=open_play_report(state="initial"))
        )
        self.assertEqual(result.reason, "match_initial")
        self.stopped()
        self.tick(self.context(100 * MS, ball=None))
        self.assertEqual(self.runner.state, "search")
        self.stopped()
        self.tick(self.context(200 * MS, ball=None))
        self.assertGreater(self.command.head_yaw, 0)
        self.tick(self.context(300 * MS))
        self.assertEqual(self.runner.state, "approach")
        self.assertGreater(self.command.x, 0)
        self.assertTrue(self.command.avoidance_applied)
        self.tick(self.context(400 * MS, x=-0.7))
        self.assertEqual(self.runner.state, "kick")
        self.assertTrue(self.command.kick_active)
        self.assertAlmostEqual(self.command.kick_ball_x, 0.7, places=5)
        result = self.tick(
            self.context(500 * MS, x=-0.7, report=open_play_report(state="set"))
        )
        self.assertEqual(result.reason, "match_set")
        self.stopped()
        self.assertIsNone(self.runner.navigation.debug.path)

    def test_all_skills_receive_the_same_context_without_reading_or_updating_world(
        self,
    ):
        context = self.context(x=-0.7)
        with (
            patch.object(
                self.world.model.reader,
                "latest",
                side_effect=AssertionError("second read"),
            ),
            patch.object(
                self.world.model.owner,
                "advance",
                side_effect=AssertionError("behaviour updated world"),
            ),
            patch.object(
                self.runner.navigation, "tick", wraps=self.runner.navigation.tick
            ) as nav,
            patch.object(self.runner.kick, "tick", wraps=self.runner.kick.tick) as kick,
        ):
            self.tick(context)
            self.assertIs(nav.call_args.args[0], context)
            self.assertIs(kick.call_args.args[0], context)

    def test_missing_official_or_motion_readiness_never_grants_permission(self):
        result = self.tick(self.context(report=None))
        self.assertEqual(result.reason, "official_state_unavailable")
        self.stopped()
        result = self.tick(self.context(100 * MS), motion=None)
        self.assertEqual(result.reason, "motion_feedback_unavailable")
        self.stopped()

    def test_unknown_core_permissions_are_not_changed_by_behaviour_policy(self):
        context = self.context()
        self.assertEqual(context.world.match.restrictions.walk, "unknown")
        self.tick(context)
        self.assertGreater(self.command.x, 0)
        self.assertEqual(context.world.match.restrictions.walk, "unknown")

    def test_penalty_stop_restart_and_unsupported_phases_clear_previous_kick(self):
        reports = [
            (open_play_report(penalty="manual"), "penalised"),
            (replace(open_play_report(), stopped=True), "official_stop"),
            (
                replace(open_play_report(), secondary_seconds=10, kicking_team=2),
                "opponent_restart_wait",
            ),
            (
                replace(open_play_report(), set_play="unknown"),
                "unknown_restart",
            ),
            (
                replace(open_play_report(), game_phase="penalty_shootout"),
                "unsupported_game_phase",
            ),
            (open_play_report(state="finished"), "match_finished"),
        ]
        for i, (report, reason) in enumerate(reports):
            with self.subTest(reason=reason):
                self.runner.cancel(self.command)
                self.tick(self.context(i * 200 * MS, x=-0.7))
                self.assertTrue(self.command.kick_active)
                result = self.tick(
                    self.context((i * 200 + 100) * MS, x=-0.7, report=report)
                )
                self.assertEqual(result.reason, reason)
                self.stopped()

    def test_goalkeeper_blocks_and_missing_player_penalty_holds(self):
        self.assertEqual(
            self.tick(self.context(), goal=MatchGoal(role="goalkeeper")).reason,
            "blocking_position",
        )
        report = replace(
            open_play_report(), teams=(wm.TeamReport(1, 0, ()), wm.TeamReport(2, 0, ()))
        )
        self.assertEqual(
            self.tick(self.context(100 * MS, report=report)).reason,
            "our_penalty_unknown",
        )
        self.stopped()

    def test_fresh_world_publications_do_not_refresh_old_referee_evidence(self):
        self.tick(self.context())
        result = self.tick(self.context(500 * MS, report=None))
        self.assertEqual(result.reason, "official_state_stale_or_untrusted")
        self.stopped()
        self.assertEqual(self.tick(self.context(600 * MS)).reason, "approaching")

    def test_motion_feedback_staleness_fall_and_kick_readiness(self):
        first = self.context(x=-0.7)
        self.tick(first)
        for i, (changes, reason) in enumerate(
            (
                ({"at": first.now}, "motion_feedback_stale"),
                ({"upright": False}, "recovery_unavailable"),
                ({"walk_ready": False}, "motion_not_ready"),
                ({"kick_ready": False}, "kick_not_ready"),
            )
        ):
            self.runner.cancel(self.command)
            context = self.context((i + 1) * 200 * MS, x=-0.7)
            feedback = replace(MotionFeedback(context.now, True, True, True), **changes)
            self.assertEqual(self.tick(context, motion=feedback).reason, reason)
            self.stopped()

    def test_loss_of_ball_searches_stationary_and_discards_approach(self):
        self.tick(self.context())
        self.assertIsNotNone(self.runner.navigation.debug.path)
        result = self.tick(self.context(1100 * MS, ball=None))
        self.assertTrue(result.reason.startswith("search:"))
        self.stopped()
        self.assertIsNone(self.runner.navigation.debug.path)

    def test_localisation_loss_stops_and_explicit_restart_can_recover(self):
        self.tick(self.context())
        result = self.tick(self.context(100 * MS, localised=False))
        self.assertEqual(result.status, SkillStatus.FAILED)
        self.stopped()
        self.assertIsNone(self.runner.navigation.debug.path)
        self.assertEqual(self.tick(self.context(200 * MS)).reason, "approaching")

    def test_world_epoch_change_cannot_reuse_progress(self):
        self.tick(self.context())
        self.world = MatchReplayWorld("new-session")
        result = self.tick(self.context(100 * MS))
        self.assertEqual(result.reason, "world_or_clock_changed")
        self.stopped()

    def test_uninspected_space_blocks_both_approach_and_kick_by_default(self):
        for i, x in enumerate((-2, -0.7)):
            self.runner = MatchRunner()
            result = self.tick(self.context(i * 100 * MS, x=x))
            self.assertEqual(result.reason, "navigation_space_unobserved")
            self.stopped()

    def test_kick_corridor_checks_obstacle_footprint(self):
        result = self.tick(self.context(x=-0.7, obstacle=(0.2, 0)))
        self.assertEqual(result.reason, "no_clear_kick_lane")
        self.stopped()

    def test_pose_uncertainty_prevents_kick_and_is_configurable(self):
        context = self.context(x=-0.7)
        pose = context.world.self.field_pose.summary
        matrix = ((0.01, 0.0, 0.0), (0.0, 0.01, 0.0), (0.0, 0.0, 0.04))
        uncertain = replace(pose, covariance=replace(pose.covariance, matrix=matrix))
        snapshot = replace(
            context.world.snapshot,
            self=replace(
                context.world.self,
                field_pose=replace(context.world.self.field_pose, summary=uncertain),
            ),
        )
        result = self.tick(replace(context, world=WorldView(snapshot)))
        self.assertEqual(result.status, SkillStatus.FAILED)
        self.assertEqual(result.reason, "pose_heading_uncertain")
        self.stopped()
        self.runner = MatchRunner(
            navigation=self.runner.navigation,
            policy=MatchPolicy(kick_heading_rad=0.6),
            kick_policy=KickPolicy(max_heading_std_rad=0.3, max_aim_margin_rad=0.6),
        )
        result = self.tick(replace(context, world=WorldView(snapshot)))
        self.assertEqual(result.reason, "kicking")
        self.assertTrue(self.command.kick_active)

    def test_search_can_start_without_global_localisation(self):
        result = self.tick(self.context(ball=None, localised=False))
        self.assertEqual(self.runner.state, "search")
        self.assertEqual(result.status, SkillStatus.RUNNING)
        self.stopped()

    def test_a_new_runner_cannot_reuse_an_old_kick_attempt_identity(self):
        context = self.context(x=-0.7)
        self.tick(context)
        old_id = self.runner.attempt_id
        self.runner = MatchRunner(navigation=self.runner.navigation)
        feedback = MotionFeedback(context.now, True, True, True, old_id, "completed")
        self.assertEqual(self.tick(context, motion=feedback).reason, "kicking")
        self.assertNotEqual(self.runner.attempt_id, old_id)

    def test_small_ball_jitter_retains_goal_then_larger_movement_retargets(self):
        self.tick(self.context())
        goal = self.runner._approach_goal
        self.tick(self.context(100 * MS, ball=(0.02, 0, 0.11)))
        self.assertIs(self.runner._approach_goal, goal)
        self.tick(self.context(200 * MS, ball=(0.4, 0, 0.11)))
        self.assertGreater(
            self.runner._approach_goal.target.pose.x, goal.target.pose.x + 0.2
        )

    def test_kick_timer_is_not_success_and_same_ball_does_not_retrigger(self):
        goal = MatchGoal(kick_duration_sec=0.1)
        self.tick(self.context(x=-0.7), goal=goal)
        result = self.tick(self.context(100 * MS, x=-0.7), goal=goal)
        self.assertEqual(result.reason, "kick_window_elapsed")
        self.assertEqual(result.status, SkillStatus.RUNNING)
        self.stopped()
        result = self.tick(self.context(200 * MS, x=-0.7), goal=goal)
        self.assertEqual(result.reason, "awaiting_ball_change")
        self.stopped()
        result = self.tick(self.context(300 * MS, x=-0.7, ball=(1, 0, 0.11)), goal=goal)
        self.assertEqual(result.reason, "approaching")

    def test_kick_outcomes_are_correlated_with_attempt(self):
        self.tick(self.context(x=-0.7))
        attempt = self.runner.attempt_id
        context = self.context(100 * MS, x=-0.7)
        old = MotionFeedback(context.now, True, True, True, "old-attempt", "completed")
        self.assertEqual(self.tick(context, motion=old).reason, "kicking")
        self.assertEqual(
            self.tick(context, motion=replace(old, kick_attempt_id=attempt)).reason,
            "kicking",
        )
        self.assertTrue(
            self.command.kick_active
        )  # Phase/legacy completion is not a shot.

    def test_departing_ball_finishes_one_shot_only_after_confirmed_stop(self):
        self.tick(self.context(x=-0.7))
        attempt = self.runner.attempt_id
        context = self.context(100 * MS, x=-0.7, ball=(0.5, 0, 0.11))
        motion = MotionFeedback(context.now, True, True, True, attempt, "running")
        self.assertEqual(
            self.tick(context, motion=motion).reason, "shot_follow_through"
        )
        self.assertTrue(self.command.kick_active)
        context = self.context(450 * MS, x=-0.7, ball=(1.0, 0, 0.11))
        self.assertEqual(
            self.tick(context, motion=replace(motion, at=context.now)).reason,
            "shot_stopping",
        )
        self.stopped()
        context = self.context(475 * MS, x=-0.7, ball=(1.05, 0, 0.11))
        transition = replace(
            motion,
            at=context.now,
            walk_ready=False,
            kick_ready=False,
            kick_status="stopping",
        )
        self.assertEqual(self.tick(context, motion=transition).reason, "shot_stopping")
        self.stopped()
        context = self.context(500 * MS, x=-0.7, ball=(1.1, 0, 0.11))
        motion = replace(motion, at=context.now, kick_status="stopped")
        self.assertEqual(
            self.tick(context, motion=motion).reason, "shot_departed_and_stopped"
        )
        self.assertEqual(self.runner.state, "stand")
        self.stopped()
        # The rearm anchor is the resulting ball position, not its pre-shot position.
        self.assertEqual(
            self.tick(self.context(550 * MS, x=-0.7, ball=(1.1, 0, 0.11))).reason,
            "awaiting_ball_change",
        )

    def test_held_snapshot_stops_even_though_its_values_remain_available(self):
        context = self.context(x=-0.7)
        self.tick(context)
        held = replace(context, now=replace(context.now, ns=200 * MS))
        self.assertEqual(self.tick(held).reason, "stale_snapshot")
        self.stopped()
        self.assertIsNotNone(context.world.current_local_ball().value)


class MatchExecutiveTest(MatchFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.wall = 0
        self.port = ReplayMotion(lambda: self.wall)
        self.executive = MatchExecutive(
            self.runner, self.port, wall_clock=lambda: self.wall
        )
        self.executive.start(self.goal)

    def execute(self, context, receipt=DEFAULT):
        return self.executive.tick(
            context,
            self.wall if receipt is DEFAULT else receipt,
            motion=MotionFeedback(context.now, True, True, True),
        )

    def test_cancellation_revokes_kick_and_does_not_restart_on_next_tick(self):
        context = self.context(x=-0.7)
        self.execute(context)
        self.assertIsNotNone(self.port.gate.current(0).kick)
        self.executive.cancel()
        self.assertIsNone(self.port.gate.current(0))
        self.assertEqual(self.execute(context).reason, "cancelled")
        self.stopped()

    def test_receiver_expires_kick_even_if_behaviour_and_world_clock_freeze(self):
        self.execute(self.context(x=-0.7))
        self.wall = 250 * MS
        self.assertIsNone(self.port.gate.current(self.wall))
        self.assertEqual(self.port.gate.failure, "match_intent_expired")

    def test_new_decisions_cannot_extend_old_receipt_deadline(self):
        context = self.context()
        self.execute(context)
        self.wall = 200 * MS
        result = self.execute(context, receipt=0)
        self.assertEqual(result.intent.valid_until_ns, 350 * MS)
        self.wall = 350 * MS
        self.assertEqual(
            self.execute(context, receipt=0).reason, "observations_expired"
        )
        self.assertIsNone(self.port.gate.current(self.wall))

    def test_slow_decision_consumes_observation_budget(self):
        context = self.context()
        original = self.runner.tick

        def slow(*args, **kwargs):
            result = original(*args, **kwargs)
            self.wall = 350 * MS
            return result

        with patch.object(self.runner, "tick", side_effect=slow):
            self.assertEqual(
                self.execute(context, receipt=0).reason, "observations_expired"
            )
        self.assertIsNone(self.port.gate)

    def test_unexpected_failure_also_stops_existing_kick(self):
        context = self.context(x=-0.7)
        self.execute(context)
        with (
            patch.object(
                self.runner, "tick", side_effect=ValueError("bad provider data")
            ),
            self.assertRaises(ValueError),
        ):
            self.execute(context)
        self.assertIsNone(self.port.gate.current(0))
        self.assertIsNone(self.executive.goal)

    def test_decision_retains_snapshot_and_tick_identity(self):
        context = self.context()
        result = self.execute(context)
        self.assertEqual(result.snapshot_id, context.world.snapshot.id)
        self.assertEqual(result.tick_id, context.tick_id)


class MatchReplayTest(unittest.TestCase):
    def test_runner_imports_without_ros_sdk_or_legacy_world_model(self):
        code = """
import importlib.abc
import sys
class Guard(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'rclpy', 'world_model_ros', 'legacy_world_model',
                                      'boosteros', 'booster_robotics_sdk_python'}:
            raise AssertionError(fullname)
sys.meta_path.insert(0, Guard())
import match_runner
import match_execution
import world_match_replay
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT / "behaviour/scripts",
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_stop_fences_commands_still_waiting_in_transport(self):
        intent = MatchIntent(
            "test", 0, 0, 250 * MS, (0.0, 0.0, 0.0), (0.45, 0.0, 1.0, 1.0), None, None
        )
        gate = MatchIntentGate("test")
        gate.accept(intent, 0)
        gate.stop(through_sequence=2)
        self.assertFalse(gate.accept(replace(intent, sequence=1), MS))
        self.assertIsNone(gate.current(MS))

    def test_runnable_scripted_sequence(self):
        output = io.StringIO()
        with redirect_stdout(output):
            main(["--allow-unknown"])
        rows = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(
            [r["state"] for r in rows], ["stand", "search", "approach", "kick", "stand"]
        )
        self.assertTrue(all(r["input"] == "scripted" for r in rows))

    def test_recorded_ground_truth_with_explicit_scripted_permissions(self):
        recording = ROOT / "world_model/tests/fixtures/booster-studio-1.10.5.jsonl"
        output = io.StringIO()
        with redirect_stdout(output):
            main(
                [
                    str(recording),
                    "--radius",
                    "robot2=.45",
                    "--allow-unknown",
                    "--script-open-play",
                ]
            )
        rows = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertGreater(len(rows), 2)
        self.assertTrue(all(r["state"] == "approach" for r in rows), rows)
        self.assertTrue(all(r["input"] == "recorded" for r in rows))

    def test_reordered_and_late_intents_cannot_restart_actuator(self):
        intent = MatchIntent(
            "test",
            0,
            0,
            250 * MS,
            (0.0, 0.0, 0.0),
            (0.45, 0.0, 1.0, 1.0),
            (0.0, 1.0, 0.7, 0.0),
            "attempt",
        )
        gate = MatchIntentGate("test")
        self.assertTrue(gate.accept(intent, 0))
        self.assertFalse(gate.accept(intent, MS))
        self.assertIsNone(gate.current(MS))
        gate = MatchIntentGate("test")
        gate.accept(intent, 0)
        self.assertFalse(
            gate.accept(
                replace(
                    intent, sequence=1, issued_ns=300 * MS, valid_until_ns=500 * MS
                ),
                300 * MS,
            )
        )
        self.assertEqual(gate.failure, "match_intent_expired")


if __name__ == "__main__":
    unittest.main()

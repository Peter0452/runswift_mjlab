"""Controlled immutable inputs cover every registered legacy match tactic."""

import importlib.util
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src/behaviour/scripts"))
from action.types import MotionCommand
from match_execution import MatchExecutive
from match_runner import MatchGoal, MatchRunner, MotionFeedback
from match_tactics import (
    DefaultFormation,
    RecordedFormation,
    TacticsPolicy,
    blocking_target,
    fresh_peers,
)
from skills.base import SkillStatus
from skills.world import NavigateToPose, NavigationPolicy
from world_match_replay import MatchReplayWorld, ReplayMotion, open_play_report
from world_model.adapters.booster import Frame, Robot

from world_model import WorldView
from world_model import types as wm

MS = 1_000_000


def official(**kwargs):
    base = open_play_report()
    base = replace(
        base,
        teams=(
            wm.TeamReport(
                1, 0, tuple(wm.PlayerReport(n, "none", 0) for n in range(1, 5))
            ),
            base.teams[1],
        ),
    )
    return replace(base, **kwargs)


class TacticsTest(unittest.TestCase):
    def setUp(self):
        self.world = MatchReplayWorld(
            "tactics", identity=wm.RobotIdentity(1, 2), radii={"robot2": 0.3}
        )
        self.runner = MatchRunner(
            navigation=NavigateToPose(
                navigation_policy=NavigationPolicy(unknown_space="allow_unknown")
            )
        )
        self.command = MotionCommand()
        self.ns = -100 * MS
        self.seq = 0

    def context(
        self,
        *,
        x=-2,
        y=0,
        yaw=0,
        ball=(0, 0, 0.11),
        report=None,
        obstacle=None,
        localised=True,
        step=100 * MS,
    ):
        self.ns += step
        robots = (Robot("robot1", (x, y, 0.7), yaw, 1),)
        if obstacle is not None:
            robots += (Robot("robot2", (*obstacle, 0.7), 0, 1),)
        frame = Frame(self.ns, self.seq, robots, ball)
        self.seq += 1
        return self.world.publish(
            frame, report=official() if report is None else report, localised=localised
        )

    def tick(self, context, goal=None, motion=None):
        return self.runner.tick(
            context,
            MatchGoal() if goal is None else goal,
            self.command,
            motion=MotionFeedback(context.now, True, True, True)
            if motion is None
            else motion,
        )

    def stopped(self):
        self.assertEqual(
            (self.command.x, self.command.y, self.command.theta), (0, 0, 0)
        )
        self.assertFalse(self.command.kick_active)

    def peer(
        self,
        context,
        *,
        x=-0.5,
        n=3,
        covariance=True,
        ball=False,
        role="striker",
        age=0,
    ):
        stamp = replace(context.now, ns=context.now.ns - age)
        frame = context.world.snapshot.field.frame
        cov = wm.Covariance(
            ("x", "y", "theta"),
            ("m", "m", "rad"),
            ((0.01, 0, 0), (0, 0.01, 0), (0, 0, 0.01)),
            frame=frame,
        )
        evidence = None
        if ball:
            state = wm.BallState(frame, wm.Point2(1, 1), None, True)
            evidence = wm.PeerBallReport(
                state,
                stamp,
                stamp,
                wm.Covariance(
                    ("x", "y"), ("m", "m"), ((0.001, 0), (0, 0.001)), frame=frame
                ),
            )
        payload = wm.PeerReport(
            wm.RobotIdentity(1, n),
            wm.FramedPose2(frame, wm.Pose2(x, 0, 0)),
            evidence,
            wm.PeerIntention(role, True),
            stamp,
            cov if covariance else None,
        )
        meta = wm.InputMeta(
            wm.EventId("peer", "peer-epoch", self.seq),
            None,
            context.now,
            context.now,
            "synchronised",
            0,
            self.world.config.configuration_id,
        )
        admission = self.world.model.input.submit(wm.WorldEvent(meta, payload))
        self.assertEqual(admission.status, "queued", admission.reason)
        self.world.model.owner.advance(context.now)
        return replace(context, world=self.world.model.reader.latest())

    def test_ready_positions_and_set_clear_kick(self):
        self.tick(self.context(x=-0.7))
        self.assertTrue(self.command.kick_active)
        result = self.tick(self.context(x=-0.7, report=official(state="ready")))
        self.assertEqual(self.runner.state, "ready")
        self.assertFalse(self.command.kick_active)
        self.assertTrue(self.command.avoidance_applied)
        result = self.tick(self.context(report=official(state="set")))
        self.assertEqual(result.reason, "match_set")
        self.stopped()

    def test_pre_entry_scans_and_requests_localisation_without_timed_permission(self):
        self.tick(self.context(report=official(state="initial")))
        for i in range(3):
            context = self.context(localised=False, ball=None, step=6_000 * MS)
            self.tick(context)
            self.assertEqual(self.runner.state, "pre_enter_field")
            self.assertEqual(self.runner.localisation_hint.at, context.now)
            self.stopped()
        self.assertNotEqual(self.command.head_yaw, 0)
        self.tick(self.context())
        self.assertEqual(self.runner.state, "approach")
        self.assertIsNone(self.runner.localisation_hint)

    def test_assist_formation_never_kicks(self):
        self.tick(self.context(x=-0.7), MatchGoal(role="assist"))
        self.assertEqual(self.runner.state, "assist")
        self.assertFalse(self.command.kick_active)
        self.assertTrue(self.command.avoidance_applied)

    def test_manual_target_is_an_intention_and_cannot_override_set(self):
        context = self.context()
        goal = MatchGoal(
            target=wm.FramedPose2(
                context.world.snapshot.field.frame, wm.Pose2(-1, 1, 0)
            )
        )
        self.tick(context, goal)
        self.assertEqual(self.runner.state, "walk_to_point")
        self.assertGreater(self.command.x, 0)
        self.tick(self.context(report=official(state="set")), goal)
        self.stopped()
        bad = replace(
            goal, target=replace(goal.target, frame=wm.FrameId("team_field", "other"))
        )
        self.assertEqual(
            self.tick(self.context(), bad).reason, "manual_target_frame_mismatch"
        )

    def test_own_restarts_play_but_opponent_kickoff_waits(self):
        self.tick(self.context(x=-0.7, report=official(secondary_seconds=10)))
        self.assertTrue(self.command.kick_active)
        self.tick(
            self.context(x=-0.7, report=official(secondary_seconds=10, kicking_team=2))
        )
        self.stopped()
        self.assertEqual(self.runner.state, "stand")

    def test_restart_release_requires_new_displacement_not_just_new_publications(self):
        report = official(state="set", kicking_team=2, secondary_seconds=10)
        self.tick(self.context(report=report))
        report = replace(report, state="playing")
        self.assertEqual(
            self.tick(self.context(report=report)).reason, "opponent_restart_wait"
        )
        self.assertEqual(
            self.tick(self.context(report=report, ball=(0.1, 0, 0.11))).reason,
            "opponent_restart_wait",
        )
        result = self.tick(self.context(report=report, ball=(2, 0, 0.11)))
        self.assertEqual(self.runner.state, "approach", result.reason)
        # A new timer starts a new restart even if kind/team did not change.
        result = self.tick(
            self.context(
                report=replace(report, secondary_seconds=20), ball=(2, 0, 0.11)
            )
        )
        self.assertEqual(result.reason, "opponent_restart_wait")
        result = self.tick(
            self.context(report=replace(report, secondary_seconds=0), ball=(2, 0, 0.11))
        )
        self.assertEqual(self.runner.state, "approach", result.reason)

    def test_opponent_restart_support_keeps_exclusion_in_planner(self):
        context = self.context(
            x=-4, report=official(set_play="corner_kick", kicking_team=2)
        )
        result = self.tick(context, MatchGoal(role="assist"))
        self.assertNotEqual(result.status, SkillStatus.FAILED, result.reason)
        disc = next(
            o
            for o in self.runner.navigation.evidence.scene.obstacles
            if o.track_id == "tactical-ball"
        )
        self.assertGreaterEqual(disc.keep_out_m, 2.0)
        self.assertFalse(self.command.kick_active)
        near = self.context(
            x=-1, report=official(set_play="corner_kick", kicking_team=2)
        )
        self.assertEqual(self.tick(near).reason, "restart_exclusion_zone")
        self.stopped()

    def test_unknown_restart_and_phase_do_not_grant_permission(self):
        for change, reason in (
            ({"set_play": "new_rule"}, "unknown_restart"),
            ({"secondary_seconds": -1}, "restart_time_unknown"),
            ({"game_phase": "penalty_shootout"}, "unsupported_game_phase"),
        ):
            self.assertEqual(
                self.tick(self.context(report=official(**change))).reason, reason
            )
            self.stopped()
        self.assertEqual(
            self.tick(self.context(report=official(game_phase="extra_time"))).reason,
            "approaching",
        )

    def test_goalkeeper_blocks_returns_home_and_clears_with_hysteresis(self):
        goal = MatchGoal(role="goalkeeper", play_style="walk_through")
        self.tick(self.context(x=-6), goal)
        self.assertEqual(self.runner.state, "blocking")
        self.tick(self.context(x=-6, ball=(-5.5, 0, 0.11)), goal)
        self.assertEqual(self.runner.state, "dribble_clear")
        self.assertGreater(self.command.x, 0)
        self.tick(self.context(x=-5.5, ball=(-4.9, 0, 0.11)), goal)
        self.assertEqual(self.runner.state, "dribble_clear")
        self.tick(self.context(x=-5.5, ball=(-4.4, 0, 0.11)), goal)
        self.assertEqual(self.runner.state, "blocking")
        result = self.tick(self.context(x=-5.5, ball=None, step=1100 * MS), goal)
        self.assertEqual(result.reason, "blocking_home")
        self.assertFalse(self.command.kick_active)

    def test_goalkeeper_never_clears_a_ball_in_own_goal(self):
        result = self.tick(
            self.context(x=-6.4, ball=(-7.1, 0, 0.11)), MatchGoal(role="goalkeeper")
        )
        self.assertEqual(self.runner.state, "blocking", result.reason)
        self.assertFalse(self.command.kick_active)

    def test_intercept_requires_fresh_velocity_covariance_and_towards_goal(self):
        context = self.context(x=-6, ball=(-5, 1, 0.11))
        ball = self.runner._ball(context, context.world.snapshot.field.frame)
        frame = ball.value.frame
        cov = wm.Covariance(
            ("vx", "vy"), ("m/s", "m/s"), ((0.0001, 0), (0, 0.0001)), frame=frame
        )
        precise = replace(
            ball,
            value=replace(
                ball.value, velocity=wm.Point2(-1, -0.5), velocity_covariance=cov
            ),
        )
        target, reason = blocking_target(context, precise, TacticsPolicy(), 2)
        self.assertEqual(reason, "blocking_intercept")
        self.assertAlmostEqual(target.y, 0.3)
        for value in (
            replace(precise.value, velocity_covariance=None),
            replace(precise.value, velocity=wm.Point2(1, 0)),
            replace(
                precise.value, velocity_covariance=replace(cov, matrix=((1, 0), (0, 1)))
            ),
        ):
            self.assertEqual(
                blocking_target(
                    context, replace(ball, value=value), TacticsPolicy(), 2
                )[1],
                "blocking_position",
            )
        stale = replace(
            precise,
            meta=replace(precise.meta, evidence_at=replace(context.now, ns=-400 * MS)),
        )
        self.assertEqual(
            blocking_target(context, stale, TacticsPolicy(), 2)[1], "blocking_position"
        )

    def test_dribble_walk_through_and_kick_on_attacking_line(self):
        for style, state in (("dribble", "dribble"), ("walk_through", "walk_through")):
            self.tick(self.context(x=-0.7), MatchGoal(play_style=style))
            self.assertEqual(self.runner.state, state)
            self.assertGreater(self.command.x, 0)
            self.assertTrue(self.command.avoidance_applied)
            self.assertFalse(self.command.kick_active)
        self.tick(
            self.context(x=2.3, ball=(3, 0, 0.11)), MatchGoal(play_style="dribble")
        )
        self.assertEqual(self.runner.state, "kick")

    def test_dribble_refuses_obstacles_unknown_space_and_kick_restrictions(self):
        goal = MatchGoal(play_style="dribble")
        result = self.tick(self.context(x=-0.7, obstacle=(-0.3, 0)), goal)
        self.assertEqual(result.status, SkillStatus.FAILED)
        self.stopped()
        self.runner = MatchRunner()
        result = self.tick(self.context(x=-0.7, step=1100 * MS), goal)
        self.assertEqual(result.reason, "navigation_space_unobserved")
        self.stopped()
        context = self.context(x=-0.7)
        match = replace(
            context.world.match,
            restrictions=replace(context.world.match.restrictions, kick="denied"),
        )
        context = replace(
            context, world=WorldView(replace(context.world.snapshot, match=match))
        )
        self.assertEqual(self.tick(context, goal).reason, "kick_restricted")
        self.stopped()

    def test_ball_keepout_is_planned_from_context_and_does_not_mutate_obstacles(self):
        context = self.context(x=1.5, y=0.4)
        result = self.tick(context)
        self.assertNotEqual(result.status, SkillStatus.FAILED, result.reason)
        obstacle = next(
            o
            for o in self.runner.navigation.evidence.scene.obstacles
            if o.track_id == "tactical-ball"
        )
        self.assertGreaterEqual(obstacle.keep_out_m, 0.35)
        self.assertEqual(context.world.obstacles.tracks, ())
        path = self.runner.navigation.debug.path
        self.assertIsNotNone(path)

    def test_search_expands_to_checked_body_turn_then_stops_on_unknown_space(self):
        self.tick(self.context(ball=None))
        result = self.tick(self.context(ball=None, step=7_000 * MS))
        self.assertEqual(self.runner.state, "search", result.reason)
        self.assertNotEqual(self.command.theta, 0)
        self.assertTrue(self.command.avoidance_applied)
        self.runner = MatchRunner()
        self.tick(self.context(ball=None))
        self.tick(self.context(ball=None, step=7_000 * MS))
        self.stopped()

    def test_auto_role_uses_peer_covariance_penalties_and_hysteresis(self):
        context = self.peer(self.context(), x=-0.3)
        self.tick(context, MatchGoal(role="auto"))
        self.assertEqual(self.runner.role, "assist")
        self.assertEqual(self.runner.coordination.chaser, 3)
        # A small advantage during the hold period does not swap the roles.
        context = self.peer(self.context(x=-0.3), x=-0.5)
        self.tick(context, MatchGoal(role="auto"))
        self.assertEqual(self.runner.role, "assist")
        context = self.peer(self.context(x=-0.3, step=1100 * MS), x=-2)
        self.tick(context, MatchGoal(role="auto"))
        self.assertEqual(self.runner.role, "striker")
        self.assertEqual(
            len(fresh_peers(context, TacticsPolicy(), self.runner._estimate)), 1
        )
        # Unknown precision and penalised reports cannot win a role auction.
        context = self.peer(self.context(), covariance=False)
        self.assertEqual(
            fresh_peers(context, TacticsPolicy(), self.runner._estimate), ()
        )

    def test_unknown_or_stale_peer_pose_is_not_used_and_cancel_drops_coordination(self):
        context = self.peer(self.context(step=1_000 * MS), age=600 * MS)
        self.tick(context, MatchGoal(role="auto"))
        self.assertEqual(self.runner.role, "striker")
        self.runner.cancel(self.command)
        self.assertIsNone(self.runner.coordination.chaser)
        self.assertIsNone(self.runner.restart.baseline)
        self.stopped()

    def test_team_ball_guides_search_but_is_not_used_for_kicking_or_rebroadcast(self):
        context = self.peer(self.context(ball=None), ball=True)
        result = self.tick(context)
        self.assertEqual(self.runner.state, "search_team", result.reason)
        self.assertFalse(self.command.kick_active)
        self.assertIsNone(self.runner.broadcast.report.ball)

    def test_existing_formation_json_works_without_ros_or_backend(self):
        import json

        path = ROOT / "utils/formation/player_template/formation_player.py"
        spec = importlib.util.spec_from_file_location("formation_player_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        config = json.loads(
            (ROOT / "utils/formation/examples/normal_play_5_players.json").read_text()
        )
        self.runner.formation = RecordedFormation(
            config, module.compute_player_position, DefaultFormation(TacticsPolicy())
        )
        context = self.context(report=official(state="ready"))
        result = self.tick(context)
        self.assertEqual(self.runner.state, "ready", result.reason)
        self.assertFalse(self.command.kick_active)

    def test_all_paths_use_supplied_context_without_a_second_read_or_update(self):
        for role, style in (
            ("striker", "dribble"),
            ("goalkeeper", "auto"),
            ("assist", "auto"),
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
                    side_effect=AssertionError("world update"),
                ),
            ):
                result = self.tick(context, MatchGoal(role=role, play_style=style))
            self.assertNotEqual(result.status, SkillStatus.FAILED, result.reason)
            self.assertEqual(
                self.runner.broadcast.snapshot_id, context.world.snapshot.id
            )

    def test_recovery_has_attempt_identity_timeout_and_referee_cancellation(self):
        context = self.context()
        fallen = MotionFeedback(
            context.now, False, False, False, recovery_available=True
        )
        result = self.tick(context, motion=fallen)
        self.assertEqual(result.reason, "recovering")
        attempt = self.command.recovery_attempt_id
        self.assertTrue(attempt)
        self.stopped()
        context = self.context()
        self.tick(
            context,
            motion=replace(
                fallen,
                at=context.now,
                recovery_attempt_id="old",
                recovery_status="completed",
            ),
        )
        self.assertEqual(self.command.recovery_attempt_id, attempt)
        context = self.context(step=13_000 * MS)
        self.assertEqual(
            self.tick(context, motion=replace(fallen, at=context.now)).reason,
            "recovery_timeout",
        )
        self.assertIsNone(self.command.recovery_attempt_id)
        context = self.context()
        self.assertEqual(
            self.tick(context, motion=replace(fallen, at=context.now)).reason,
            "recovery_requires_restart",
        )
        self.runner.cancel(self.command)
        context = self.context()
        self.tick(context, motion=replace(fallen, at=context.now))
        context = self.context(report=official(stopped=True))
        self.assertEqual(
            self.tick(context, motion=replace(fallen, at=context.now)).reason,
            "official_stop",
        )
        self.assertIsNone(self.command.recovery_attempt_id)

    def test_executive_sends_recovery_and_rate_limited_local_reports(self):
        clock = lambda: self.ns
        port, team = ReplayMotion(clock), Mock()
        executive = MatchExecutive(self.runner, port, wall_clock=clock, team_port=team)
        executive.start(MatchGoal())
        context = self.context()
        result = executive.tick(
            context,
            self.ns,
            motion=MotionFeedback(
                context.now, False, False, False, recovery_available=True
            ),
        )
        self.assertIsNotNone(result.intent.recovery_attempt_id)
        self.assertEqual(result.intent.velocity, (0, 0, 0))
        self.assertEqual(team.send.call_count, 1)
        context = self.context()
        executive.tick(
            context, self.ns, motion=MotionFeedback(context.now, True, True, True)
        )
        self.assertEqual(team.send.call_count, 1)
        for _ in range(4):
            context = self.context()
            executive.tick(
                context, self.ns, motion=MotionFeedback(context.now, True, True, True)
            )
        self.assertEqual(team.send.call_count, 2)
        packet = team.send.call_args.args[0]
        self.assertEqual(packet.snapshot_id, context.world.snapshot.id)
        self.assertIsNotNone(packet.report.pose_covariance)
        executive.cancel()
        self.assertIsNone(port.gate.intent)

    def test_head_tracking_uses_robot_base_ball_not_field_heading(self):
        context = self.context(x=-2, ball=(0, 0.4, 0.11))
        self.tick(context)
        self.assertGreater(self.command.head_yaw, 0)
        self.assertLessEqual(self.command.head_pitch, 0.7)

    def test_new_obstacle_cancels_a_locked_kick_lane(self):
        self.tick(self.context(x=-0.7))
        self.assertTrue(self.command.kick_active)
        result = self.tick(self.context(x=-0.7, obstacle=(6, 0)))
        self.assertIn(result.reason, {"kick_lane_changed", "no_clear_kick_lane"})
        self.stopped()

    def test_own_corner_does_not_drive_through_and_restart_revokes_old_attempt(self):
        goal = MatchGoal(play_style="walk_through")
        context = self.context(x=-0.7, report=official(set_play="corner_kick"))
        self.tick(context, goal)
        self.assertEqual(self.runner.state, "kick")
        old = self.runner.attempt_id
        result = self.tick(
            self.context(x=-0.7, report=official(set_play="goal_kick")), goal
        )
        self.assertEqual(result.reason, "awaiting_ball_change")
        self.assertEqual(self.runner.attempt_id, old)
        self.stopped()

    def test_penalised_peer_and_unhealthy_ball_source_do_not_authorise_chasing(self):
        report = official()
        own = replace(
            report.teams[0],
            players=tuple(
                replace(p, penalty="manual") if p.player_number == 3 else p
                for p in report.teams[0].players
            ),
        )
        context = self.peer(
            self.context(report=replace(report, teams=(own, report.teams[1])))
        )
        self.assertEqual(
            fresh_peers(context, TacticsPolicy(), self.runner._estimate), ()
        )
        local = context.world.current_local_ball().value
        source = local.meta.contributors[0].source
        health = tuple(
            replace(h, status="failed") if h.component == source else h
            for h in context.world.health
        )
        context = replace(
            context, world=WorldView(replace(context.world.snapshot, health=health))
        )
        self.tick(context)
        self.assertFalse(self.command.kick_active)
        self.assertNotEqual(self.runner.state, "approach")

    def test_localisation_hint_is_delivered_once_per_waiting_episode(self):
        output = Mock()
        executive = MatchExecutive(
            self.runner,
            ReplayMotion(lambda: self.ns),
            wall_clock=lambda: self.ns,
            localisation_port=output,
        )
        executive.start(MatchGoal())
        context = self.context(report=official(state="initial"))
        executive.tick(context, self.ns)
        for _ in range(3):
            context = self.context(localised=False, ball=None)
            executive.tick(
                context, self.ns, motion=MotionFeedback(context.now, True, True, True)
            )
        self.assertEqual(output.send.call_count, 1)
        self.assertEqual(output.send.call_args.args[0].mode, "own_half")

    def test_recovery_set_hold_cannot_silently_rearm_cancelled_attempt(self):
        context = self.context()
        fallen = MotionFeedback(
            context.now, False, False, False, recovery_available=True
        )
        self.tick(context, motion=fallen)
        self.assertIsNotNone(self.command.recovery_attempt_id)
        context = self.context(report=official(state="set"))
        self.tick(context, motion=replace(fallen, at=context.now))
        context = self.context()
        self.assertEqual(
            self.tick(context, motion=replace(fallen, at=context.now)).reason,
            "recovery_requires_restart",
        )
        self.stopped()
        self.assertIsNone(self.command.recovery_attempt_id)

    def test_auto_goalkeeper_number_is_configurable(self):
        self.runner.tactics = replace(self.runner.tactics, goalkeeper_number=2)
        self.tick(self.context(x=-6), MatchGoal(role="auto"))
        self.assertEqual(self.runner.role, "goalkeeper")
        self.assertEqual(self.runner.state, "blocking")

    def test_unknown_peer_ball_precision_falls_back_to_local_search(self):
        context = self.peer(self.context(ball=None), ball=True)
        peer = context.world.peers[0]
        peer = replace(peer, ball=replace(peer.ball, covariance=None))
        context = replace(
            context, world=WorldView(replace(context.world.snapshot, peers=(peer,)))
        )
        result = self.tick(context)
        self.assertEqual(self.runner.state, "search", result.reason)
        self.stopped()

    def test_diagonal_support_command_respects_total_sdk_speed_limit(self):
        from math import hypot

        self.runner = MatchRunner(
            navigation=NavigateToPose(
                navigation_policy=NavigationPolicy(
                    unknown_space="allow_unknown", max_unknown_speed_mps=1.0
                )
            )
        )
        self.tick(self.context(x=-3, y=1), MatchGoal(role="assist"))
        self.assertGreater(hypot(self.command.x, self.command.y), 0)
        self.assertLessEqual(hypot(self.command.x, self.command.y), 0.2 + 1e-10)
        self.assertTrue(self.command.avoidance_applied)


if __name__ == "__main__":
    unittest.main()

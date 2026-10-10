"""Real world inputs -> one shot -> measured controller stop, without ROS or SDK."""

import sys
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from match_runner import MotionFeedback
from skills.base import SkillStatus
from skills.single_shot import ShotPolicy, SingleShot, SingleShotGoal
from test_match_runner import MS, MatchFixture

from world_model import WorldView
from world_model import types as wm


class SingleShotTest(MatchFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.shot = SingleShot()
        self.shot_goal = SingleShotGoal(
            1.0,
            target=wm.FramedPoint2(self.world.config.field.frame, wm.Point2(7, 0)),
            duration_sec=8.0,
            attempt_id="one-shot",
        )

    def step(self, ns=0, *, status="running", attempt="one-shot", **kwargs):
        context = self.context(ns, x=kwargs.pop("x", -0.65), **kwargs)
        feedback = MotionFeedback(context.now, True, True, True, attempt, status)
        return self.shot.tick(context, self.shot_goal, self.command, motion=feedback)

    def depart(self):
        self.step()
        self.step(100 * MS, ball=(0.5, 0, 0.11))
        return self.step(450 * MS, ball=(1, 0, 0.11))

    def test_departure_then_correlated_stop_and_no_second_activation(self):
        self.assertEqual(self.depart().reason, "shot_stopping")
        self.stopped()
        self.assertEqual(
            self.step(500 * MS, status="stopped", attempt="old").status,
            SkillStatus.RUNNING,
        )
        self.assertEqual(
            self.step(550 * MS, status="stopping").status, SkillStatus.RUNNING
        )
        result = self.step(600 * MS, status="stopped", ball=None)
        self.assertEqual(result.status, SkillStatus.SUCCEEDED)
        self.assertEqual(result.reason, "shot_departed_and_stopped")
        self.stopped()
        self.assertEqual(
            self.step(700 * MS, status="stopped", ball=(2, 0, 0.11)).status,
            SkillStatus.SUCCEEDED,
        )
        self.stopped()

    def test_robot_movement_alone_is_not_departure(self):
        self.step()
        self.step(100 * MS, x=-0.1)
        self.step(500 * MS, x=-0.1)
        self.assertEqual(self.shot.phase, "active")
        self.assertTrue(self.command.kick_active)

    def test_ball_change_before_measured_activation_is_not_departure(self):
        self.step(status="idle")
        self.step(100 * MS, status="idle", ball=(0.6, 0, 0.11))
        self.assertEqual(self.shot.phase, "active")

    def test_uncertainty_margin_rejects_ambiguous_departure(self):
        # Include both marginal error bounds; do not assume independent errors.
        with patch.object(
            type(self.shot.policy),
            "assess_ball",
            return_value=SimpleNamespace(position_std_m=0.08),
        ):
            self.step()
            self.step(100 * MS, ball=(0.5, 0, 0.11))
            self.assertEqual(self.shot.phase, "active")
            self.step(200 * MS, ball=(0.7, 0, 0.11))
            self.assertEqual(self.shot.phase, "follow_through")

    def test_stop_timeout_and_actuator_failure_never_succeed(self):
        self.depart()
        result = self.step(2450 * MS, status="stopping")
        self.assertEqual(result.reason, "shot_stop_unconfirmed")
        self.assertEqual(result.status, SkillStatus.FAILED)
        self.stopped()
        self.shot = SingleShot()
        self.step(2500 * MS)
        self.assertEqual(
            self.step(2600 * MS, status="failed").status, SkillStatus.FAILED
        )
        self.stopped()

    def test_localisation_reset_or_stale_feedback_during_stop_is_failure(self):
        self.depart()
        context = self.context(500 * MS, x=-0.65)
        snapshot = replace(
            context.world.snapshot,
            self=replace(context.world.self, localisation_epoch="reset"),
        )
        context = replace(context, world=WorldView(snapshot))
        feedback = MotionFeedback(context.now, True, True, True, "one-shot", "stopped")
        result = self.shot.tick(context, self.shot_goal, self.command, motion=feedback)
        self.assertEqual(result.status, SkillStatus.FAILED)
        self.stopped()

    def test_stale_motion_or_world_cannot_confirm_exit(self):
        self.depart()
        context = self.context(700 * MS, x=-0.65)
        motion = MotionFeedback(
            replace(context.now, ns=500 * MS), True, True, True, "one-shot", "stopped"
        )
        result = self.shot.tick(context, self.shot_goal, self.command, motion=motion)
        self.assertEqual(result.reason, "shot_motion_feedback_unavailable")
        self.stopped()

    def test_cancellation_discards_follow_through_and_policy_is_bounded(self):
        self.step()
        self.step(100 * MS, ball=(0.5, 0, 0.11))
        self.shot.cancel(self.command)
        self.stopped()
        self.assertEqual(self.shot.phase, "ready")
        for kwargs in (
            {"departure_m": 0},
            {"follow_through_ns": 501 * MS},
            {"feedback_age_ns": 151 * MS},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                ShotPolicy(**kwargs)


if __name__ == "__main__":
    unittest.main()

"""Replay real Booster frames through the model, planner and command checks."""

import json
import sys
import unittest
from dataclasses import replace
from math import hypot
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "behaviour" / "scripts"))
sys.path.insert(0, str(ROOT / "world_model" / "examples" / "booster_simulator"))

from action.types import MotionCommand
from adapter import Frame
from replay import Replay
from skills.base import SkillStatus
from skills.world import NavigateToPose, NavigateToPoseGoal, NavigationPolicy

from world_model import capture_tick
from world_model import types as wm

FIXTURE = ROOT / "world_model" / "tests" / "fixtures" / "booster-studio-1.10.5.jsonl"


class BoosterNavigationTest(unittest.TestCase):
    def setUp(self):
        self.rows = [json.loads(line) for line in FIXTURE.read_text().splitlines()]
        self.replay = Replay(
            self.rows[0]["epoch"], robot="robot1", radii={"robot2": 0.45}
        )
        self.skill = NavigateToPose(
            navigation_policy=NavigationPolicy(unknown_space="allow_unknown")
        )
        self.command = MotionCommand()
        self.goal = NavigateToPoseGoal(
            wm.FramedPose2(self.replay.config.field.frame, wm.Pose2(2, 0, 0))
        )

    def tick(self, frame, *, skill=None, **kwargs):
        context = self.replay.step(frame, **kwargs)
        return (skill or self.skill).tick(context, self.goal, self.command)

    def test_recorded_obstacle_produces_checked_detour_and_limited_intent(self):
        for row in self.rows:
            result = self.tick(Frame.parse(row["payload"]))
            self.assertEqual(result.status, SkillStatus.RUNNING, result.reason)
            self.assertLessEqual(hypot(self.command.x, self.command.y), 0.2 + 1e-7)
            self.assertFalse(self.command.kick_active)
            self.assertTrue(self.command.avoidance_applied)
            self.assertIsNotNone(self.skill.debug.path)
        self.assertEqual(len(self.skill.evidence.scene.obstacles), 1)

    def test_default_policy_does_not_interpret_oracle_stream_as_clear_space(self):
        result = self.tick(Frame.parse(self.rows[0]["payload"]), skill=NavigateToPose())
        self.assertEqual(result.status, SkillStatus.FAILED)
        self.assertEqual(result.reason, "navigation_space_unobserved")
        self.assertEqual(
            (self.command.x, self.command.y, self.command.theta), (0, 0, 0)
        )

    def test_localisation_loss_discards_cached_path_and_recovery_can_restart(self):
        first, second, third = (Frame.parse(row["payload"]) for row in self.rows[:3])
        self.assertEqual(self.tick(first).status, SkillStatus.RUNNING)
        result = self.tick(second, localised=False)
        self.assertEqual(result.status, SkillStatus.FAILED)
        self.assertTrue(result.reason)
        self.assertIsNone(self.skill.debug.path)
        self.assertEqual(
            (self.command.x, self.command.y, self.command.theta), (0, 0, 0)
        )
        self.assertEqual(self.tick(third).status, SkillStatus.RUNNING)

    def test_input_pause_stops_even_without_another_capture(self):
        self.tick(Frame.parse(self.rows[0]["payload"]))
        self.replay.clock.ns += 2_000_000_000
        # Independent application update, not a navigation-side world update.
        self.replay.model.owner.advance(self.replay.clock.now())
        ctx = capture_tick(self.replay.model.reader, self.replay.clock, 1)
        result = self.skill.tick(ctx, self.goal, self.command)
        self.assertEqual(result.status, SkillStatus.FAILED)
        self.assertIsNone(self.skill.debug.path)
        self.assertEqual(
            (self.command.x, self.command.y, self.command.theta), (0, 0, 0)
        )

    def test_delayed_capture_cannot_supply_a_current_navigation_pose(self):
        result = self.tick(Frame.parse(self.rows[0]["payload"]), delay_ns=100_000_000)
        self.assertEqual(result.status, SkillStatus.FAILED)
        self.assertEqual(
            (self.command.x, self.command.y, self.command.theta), (0, 0, 0)
        )

    def test_new_session_cannot_reuse_old_goal_or_path(self):
        first = Frame.parse(self.rows[0]["payload"])
        self.tick(first)
        new = Replay("reset-session", robot="robot1", radii={"robot2": 0.45})
        ctx = new.step(replace(first, ns=0, sequence=0))
        result = self.skill.tick(ctx, self.goal, self.command)
        self.assertEqual(result.status, SkillStatus.FAILED)
        self.assertIsNone(self.skill.debug.path)
        self.assertEqual(
            (self.command.x, self.command.y, self.command.theta), (0, 0, 0)
        )


if __name__ == "__main__":
    unittest.main()

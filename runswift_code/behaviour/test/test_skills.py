#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from action.types import MotionCommand  # noqa: E402
from skills.base import Point2, Pose2, SkillStatus  # noqa: E402
from skills.kick import Kick, KickRequest  # noqa: E402
from skills.navigate_to_pose import NavigateToPose, NavigateToPoseRequest  # noqa: E402
from skills.obstacle_avoid import avoid_opponents  # noqa: E402
from skills.walk_to_pose import WalkToPose, WalkToPoseRequest  # noqa: E402


class AvoidOpponentsTest(unittest.TestCase):
    def test_opponent_ahead_reduces_forward_speed(self) -> None:
        pose = Pose2(0.0, 0.0, 0.0)
        vx, vy, vth = avoid_opponents(pose, 0.8, 0.0, 0.0, ((0.4, 0.0),))
        self.assertLess(vx, 0.8)
        self.assertEqual(vth, 0.0)

    def test_protect_ball_skips_avoid_when_lane_clear(self) -> None:
        pose = Pose2(0.0, 0.0, 0.0)
        vx, vy, vth = avoid_opponents(
            pose,
            0.8,
            0.0,
            0.0,
            ((0.2, 1.5),),
            protect_ball=(1.0, 0.0),
        )
        self.assertEqual((vx, vy, vth), (0.8, 0.0, 0.0))

    def test_protect_ball_avoids_when_opponent_in_lane(self) -> None:
        pose = Pose2(0.0, 0.0, 0.0)
        vx, vy, vth = avoid_opponents(
            pose,
            0.8,
            0.0,
            0.0,
            ((0.4, 0.0),),
            protect_ball=(1.0, 0.0),
        )
        self.assertLess(vx, 0.8)


class WalkToPoseAvoidTest(unittest.TestCase):
    def test_applies_avoidance_and_marks_command(self) -> None:
        skill = WalkToPose()
        command = MotionCommand()
        request = WalkToPoseRequest(
            robot_pose=Pose2(0.0, 0.0, 0.0),
            target_pose=Pose2(3.0, 0.0, 0.0),
            obstacles=((0.4, 0.0),),
            apply_avoidance=True,
        )
        progress = skill.tick(request, command)
        self.assertEqual(progress.status, SkillStatus.RUNNING)
        self.assertTrue(command.avoidance_applied)
        self.assertLess(command.x, 0.8)

    def test_planned_velocity_is_used_then_avoided(self) -> None:
        skill = WalkToPose()
        command = MotionCommand()
        request = WalkToPoseRequest(
            robot_pose=Pose2(0.0, 0.0, 0.0),
            target_pose=Pose2(3.0, 0.0, 0.0),
            obstacles=((0.4, 0.0),),
            apply_avoidance=True,
            planned_velocity=(0.6, 0.0, 0.0),
        )
        skill.tick(request, command)
        self.assertTrue(command.avoidance_applied)
        self.assertLess(command.x, 0.6)


class _FakePlanner:
    def prepare_obstacles(self, obstacles, **kwargs):
        return SimpleNamespace(selected=list(obstacles))

    def update(self, **kwargs):
        start = kwargs["X0"]
        goal = kwargs["plan_goal"]
        path = SimpleNamespace(
            waypoints=[
                (float(start[0]), float(start[1]), float(start[2]), "start"),
                (float(goal[0]), float(goal[1]), float(goal[2]), "direct"),
            ],
            reused=False,
            direct=True,
            debug={},
        )
        return path, SimpleNamespace(selected=list(kwargs.get("raw_obstacles", [])))


class _FailingPlanner(_FakePlanner):
    def update(self, **kwargs):
        return None, SimpleNamespace(selected=[])


class _FakeTracker:
    def track(self, **kwargs):
        return SimpleNamespace(
            command=SimpleNamespace(as_tuple=lambda: (0.55, 0.0, 0.0)),
            lookahead=np.array([1.0, 0.0, 0.0]),
            debug={"fake": True},
        )


class NavigateToPoseTest(unittest.TestCase):
    def test_arrived_stops_without_planning(self) -> None:
        skill = NavigateToPose(planner=_FailingPlanner(), tracker=_FakeTracker())
        command = MotionCommand()
        progress = skill.tick(
            NavigateToPoseRequest(
                robot_pose=Pose2(1.0, 2.0, 0.1),
                target_pose=Pose2(1.05, 2.02, 0.12),
            ),
            command,
        )
        self.assertEqual(progress.status, SkillStatus.SUCCEEDED)
        self.assertEqual(progress.reason, "arrived")
        self.assertEqual((command.x, command.y, command.theta), (0.0, 0.0, 0.0))

    def test_planned_velocity_goes_to_walk_subskill(self) -> None:
        skill = NavigateToPose(planner=_FakePlanner(), tracker=_FakeTracker())
        command = MotionCommand()
        progress = skill.tick(
            NavigateToPoseRequest(
                robot_pose=Pose2(0.0, 0.0, 0.0),
                target_pose=Pose2(1.5, 0.0, 0.0),
                apply_avoidance=False,
            ),
            command,
        )
        self.assertEqual(progress.status, SkillStatus.RUNNING)
        self.assertAlmostEqual(command.x, 0.55)
        self.assertEqual(skill.debug.source, "path_tracker")

    def test_no_path_stops_and_fails(self) -> None:
        warnings: list[str] = []
        skill = NavigateToPose(
            planner=_FailingPlanner(),
            tracker=_FakeTracker(),
            log_warning=warnings.append,
        )
        command = MotionCommand()
        command.set_body(0.4, 0.0, 0.0)
        progress = skill.tick(
            NavigateToPoseRequest(
                robot_pose=Pose2(0.0, 0.0, 0.0),
                target_pose=Pose2(1.5, 0.0, 0.0),
            ),
            command,
        )
        self.assertEqual(progress.status, SkillStatus.FAILED)
        self.assertEqual(progress.reason, "no_path")
        self.assertEqual((command.x, command.y, command.theta), (0.0, 0.0, 0.0))
        self.assertEqual(warnings, ["tracker nav: no global path; stopping"])

    def test_uses_walk_subskill_for_local_avoid(self) -> None:
        skill = NavigateToPose(planner=_FakePlanner(), tracker=_FakeTracker())
        command = MotionCommand()
        skill.tick(
            NavigateToPoseRequest(
                robot_pose=Pose2(0.0, 0.0, 0.0),
                target_pose=Pose2(1.5, 0.0, 0.0),
                avoid_obstacles=((0.4, 0.0),),
                apply_avoidance=True,
            ),
            command,
        )
        self.assertTrue(command.avoidance_applied)
        self.assertLess(command.x, 0.55)


class KickSkillTest(unittest.TestCase):
    def test_writes_kick_intent_and_stops_body(self) -> None:
        skill = Kick()
        request = KickRequest(
            robot_pose=Pose2(0.0, 0.0, 0.0),
            ball=Point2(1.0, 0.0),
            target=Point2(5.0, 0.0),
            power=2.5,
        )
        command = MotionCommand()
        command.set_body(0.4, 0.1, 0.2)
        skill.on_enter(request)
        progress = skill.tick(request, command)
        self.assertEqual(progress.status, SkillStatus.RUNNING)
        self.assertEqual((command.x, command.y, command.theta), (0.0, 0.0, 0.0))
        self.assertTrue(command.kick_active)
        self.assertAlmostEqual(command.kick_direction, 0.0, places=3)
        self.assertAlmostEqual(command.kick_ball_x, 1.0, places=3)
        self.assertEqual(command.kick_power, 2.5)
        skill.on_exit()
        self.assertIsNone(skill.reference)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
from __future__ import annotations

import sys
import types
import unittest
from math import atan2, pi
from pathlib import Path


def _install_world_model_stub() -> None:
    world_model = types.ModuleType("legacy_world_model")
    world_model.FIELD_LENGTH_M = 9.0
    world_model.FIELD_WIDTH_M = 6.0
    sys.modules["legacy_world_model"] = world_model


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

_install_world_model_stub()

import blocking  # noqa: E402


class ToPInPiTest(unittest.TestCase):
    def test_wraps_to_minus_pi_pi(self) -> None:
        self.assertAlmostEqual(blocking.to_p_in_pi(0.0), 0.0)
        self.assertAlmostEqual(blocking.to_p_in_pi(pi), -pi)
        self.assertAlmostEqual(blocking.to_p_in_pi(3 * pi), -pi)


class AngleBetweenVectorsTest(unittest.TestCase):
    def test_right_angle(self) -> None:
        angle = blocking._angle_between_vectors((1.0, 0.0), (0.0, 1.0))
        self.assertAlmostEqual(abs(angle), pi / 2.0)

    def test_opposite_direction(self) -> None:
        angle = blocking._angle_between_vectors((1.0, 0.0), (-1.0, 0.0))
        self.assertAlmostEqual(abs(angle), pi)


class DefendingDepthTest(unittest.TestCase):
    def test_goalie_uses_goal_area_depth(self) -> None:
        self.assertAlmostEqual(blocking.defending_depth("goalie"), blocking.GOAL_AREA_DEPTH)

    def test_outfield_role_has_placeholder_depth(self) -> None:
        self.assertAlmostEqual(blocking.defending_depth("defender_near"), 1.0)


class BisectorBlockingPoseTest(unittest.TestCase):
    def test_goalie_depth_is_in_front_of_own_goal_line(self) -> None:
        pose = blocking.calculate_blocking_pose("goalie", (0.0, 0.0))
        self.assertIsNotNone(pose)
        assert pose is not None
        x, _, _ = pose
        self.assertAlmostEqual(x, blocking.GOALIE_GOAL_X + blocking.GOAL_AREA_DEPTH)

    def test_central_ball_stays_near_goal_centre(self) -> None:
        pose = blocking.calculate_blocking_pose("goalie", (0.0, 0.0))
        self.assertIsNotNone(pose)
        assert pose is not None
        _, y, _ = pose
        self.assertAlmostEqual(y, 0.0, places=2)

    def test_offset_ball_shifts_laterally_same_sign(self) -> None:
        pose = blocking.calculate_blocking_pose("goalie", (0.0, 1.5))
        self.assertIsNotNone(pose)
        assert pose is not None
        _, y, _ = pose
        self.assertGreater(y, 0.0)

        pose_neg = blocking.calculate_blocking_pose("goalie", (0.0, -1.5))
        self.assertIsNotNone(pose_neg)
        assert pose_neg is not None
        _, y_neg, _ = pose_neg
        self.assertLess(y_neg, 0.0)

    def test_pose_faces_ball(self) -> None:
        ball_pos = (0.0, 1.0)
        pose = blocking.calculate_blocking_pose("goalie", ball_pos)
        self.assertIsNotNone(pose)
        assert pose is not None
        x, y, theta = pose
        expected_theta = atan2(ball_pos[1] - y, ball_pos[0] - x)
        self.assertAlmostEqual(theta, blocking.to_p_in_pi(expected_theta))

    def test_ball_behind_goal_line_is_clamped_forward(self) -> None:
        pose = blocking.calculate_blocking_pose("goalie", (blocking.GOALIE_GOAL_X - 1.0, 0.0))
        self.assertIsNotNone(pose)
        assert pose is not None
        x, _, _ = pose
        self.assertGreater(x, blocking.GOALIE_GOAL_X)

    def test_non_goalie_role_not_implemented_yet(self) -> None:
        self.assertIsNone(blocking.calculate_blocking_pose("defender_near", (0.0, 0.0)))

    def test_ball_on_post_uses_bisector_with_clamped_x(self) -> None:
        ball_pos = (blocking.GOALIE_GOAL_X, blocking.GOALPOST_LEFT_Y)
        pose = blocking.calculate_blocking_pose("goalie", ball_pos)
        self.assertIsNotNone(pose)
        assert pose is not None
        x, y, _ = pose
        self.assertAlmostEqual(x, blocking.GOALIE_GOAL_X + blocking.GOAL_AREA_DEPTH)
        self.assertGreater(y, 0.0)


class CalculateBlockingPoseTest(unittest.TestCase):
    def test_bisector_is_default(self) -> None:
        ball_pos = (0.0, 1.0)
        self.assertEqual(
            blocking.calculate_blocking_pose("goalie", ball_pos),
            blocking.calculate_blocking_pose("goalie", ball_pos, use_bisector=True),
        )

    def test_goal_centre_mode_uses_defending_depth(self) -> None:
        ball_pos = (1.0, 0.5)
        pose = blocking.calculate_blocking_pose("goalie", ball_pos, use_bisector=False)
        self.assertIsNotNone(pose)
        assert pose is not None
        x, y, theta = pose
        self.assertAlmostEqual(x, blocking.GOALIE_GOAL_X + blocking.GOAL_AREA_DEPTH)
        self.assertAlmostEqual(y, 0.0, places=1)
        expected_theta = atan2(ball_pos[1] - y, ball_pos[0] - x)
        self.assertAlmostEqual(theta, blocking.to_p_in_pi(expected_theta))

    def test_goal_centre_mode_differs_from_bisector_on_wide_ball(self) -> None:
        ball_pos = (0.0, 1.5)
        bisector_pose = blocking.calculate_blocking_pose("goalie", ball_pos, use_bisector=True)
        centre_pose = blocking.calculate_blocking_pose("goalie", ball_pos, use_bisector=False)
        self.assertIsNotNone(bisector_pose)
        self.assertIsNotNone(centre_pose)
        assert bisector_pose is not None and centre_pose is not None
        self.assertNotAlmostEqual(bisector_pose[1], centre_pose[1], places=2)

    def test_rejects_non_goalie(self) -> None:
        self.assertIsNone(
            blocking.calculate_blocking_pose("defender_near", (0.0, 0.0), use_bisector=False)
        )


class GeometrySanityTest(unittest.TestCase):
    def test_own_goal_is_on_field_end_line(self) -> None:
        self.assertAlmostEqual(blocking.GOALIE_GOAL_X, -4.5)

    def test_posts_are_inside_field_width(self) -> None:
        half_field = 3.0
        self.assertLess(abs(blocking.GOALPOST_LEFT_Y), half_field)
        self.assertLess(abs(blocking.GOALPOST_RIGHT_Y), half_field)


if __name__ == "__main__":
    unittest.main()

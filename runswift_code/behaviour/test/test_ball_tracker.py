#!/usr/bin/env python3
from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path

import numpy as np


def _install_ros_stubs() -> None:
    callback_groups = types.ModuleType("rclpy.callback_groups")
    callback_groups.ReentrantCallbackGroup = type("ReentrantCallbackGroup", (), {})
    sys.modules["rclpy.callback_groups"] = callback_groups

    node = types.ModuleType("rclpy.node")
    node.Node = type("Node", (), {})
    sys.modules["rclpy.node"] = node

    geometry_msgs = types.ModuleType("geometry_msgs.msg")
    geometry_msgs.PointStamped = type("PointStamped", (), {})
    geometry_msgs.Pose2D = type("Pose2D", (), {})
    sys.modules["geometry_msgs.msg"] = geometry_msgs

    std_msgs = types.ModuleType("std_msgs.msg")
    std_msgs.Bool = type("Bool", (), {})
    std_msgs.String = type("String", (), {})
    sys.modules["std_msgs.msg"] = std_msgs

    vision_interface = types.ModuleType("vision_interface.msg")
    vision_interface.Detections = type("Detections", (), {})
    sys.modules["vision_interface.msg"] = vision_interface

    communication_interface = types.ModuleType("communication_interface.msg")
    communication_interface.GameState = type("GameState", (), {})
    communication_interface.RobotComms = type("RobotComms", (), {})
    sys.modules["communication_interface.msg"] = communication_interface

    booster_interface = types.ModuleType("booster_interface.msg")
    booster_interface.LowState = type("LowState", (), {})
    booster_interface.FallDownState = type("FallDownState", (), {})
    booster_interface.FallDownState.IS_READY = 0
    sys.modules["booster_interface.msg"] = booster_interface

    object_avoidance = types.ModuleType("object_avoidance_apf")
    object_avoidance.PFParams = type("PFParams", (), {})
    object_avoidance.SimpleAvoidanceFilter = type("SimpleAvoidanceFilter", (), {})
    sys.modules["object_avoidance_apf"] = object_avoidance

    whistle_detector_interface = types.ModuleType("whistle_detector_interface.msg")
    whistle_detector_interface.WhistleDetection = type("WhistleDetection", (), {})
    sys.modules["whistle_detector_interface.msg"] = whistle_detector_interface


_install_ros_stubs()
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from ball_physics import (
    DEFAULT_BALL_FRICTION,
    propagate_ball_position,
    velocity_after_distance_for_time,
)
from ball_tracker import (
    BallTracker,
    MAX_INFERRED_SPEED_MPS,
    MIN_MEASUREMENTS_BEFORE_INFERRED_V,
)
from legacy_world_model import BallMeasurement, BallModel, WorldModel


def _measurement(
    x: float,
    y: float,
    t: float,
    *,
    source: str = "vision",
    player_id: int | None = None,
) -> BallMeasurement:
    return BallMeasurement(
        ball=BallModel(
            global_x=x,
            global_y=y,
            source=source,
            confidence=90.0,
            last_seen_sec=t,
        ),
        source=source,
        player_id=player_id,
        last_seen_sec=t,
        confidence=90.0,
    )


class BallPhysicsTest(unittest.TestCase):
    def test_stationary_ball_stays_put(self) -> None:
        p = np.array([1.0, 2.0])
        v = np.zeros(2)
        out = propagate_ball_position(p, v, 0.5, DEFAULT_BALL_FRICTION)
        np.testing.assert_allclose(out, p, atol=1e-6)

    def test_velocity_after_distance_for_time(self) -> None:
        p0 = np.array([0.0, 0.0])
        p1 = np.array([1.0, 0.0])
        v = velocity_after_distance_for_time(p0, p1, 1.0, DEFAULT_BALL_FRICTION)
        self.assertGreater(v[0], 0.9)


class BallTrackerTest(unittest.TestCase):
    def test_stationary_ball_low_velocity(self) -> None:
        tracker = BallTracker()
        for t in np.linspace(0.0, 1.0, 8):
            tracker.update(t, _measurement(1.0, 2.0, t))

        self.assertTrue(tracker.valid)
        vx, vy = tracker.velocity_at()
        self.assertLess(abs(vx) + abs(vy), 0.2)
        x, y = tracker.position_at(0.5)
        self.assertAlmostEqual(x, 1.0, delta=0.3)
        self.assertAlmostEqual(y, 2.0, delta=0.3)

    def test_rolling_ball_forward_prediction(self) -> None:
        tracker = BallTracker()
        speed = 0.5
        for i, t in enumerate(np.linspace(0.0, 1.5, 10)):
            tracker.update(t, _measurement(speed * t, 0.0, t))

        self.assertTrue(tracker.valid)
        x_now, _ = tracker.position_at(0.0)
        x_future, _ = tracker.position_at(0.5)
        self.assertGreater(x_future, x_now)

    def test_coast_without_measurement_then_invalid(self) -> None:
        tracker = BallTracker(max_coast_sec=1.0)
        tracker.update(0.0, _measurement(0.0, 0.0, 0.0))
        tracker.update(0.5, None)
        self.assertTrue(tracker.valid)

        tracker.update(2.0, None)
        self.assertFalse(tracker.valid)
        self.assertEqual(tracker.position_at(0.0), (0.0, 0.0))

    def test_source_switch_reinitializes(self) -> None:
        tracker = BallTracker()
        for t in np.linspace(0.0, 1.0, 6):
            tracker.update(t, _measurement(5.0 + t, 0.0, t))

        tracker.update(1.2, _measurement(-2.0, 3.0, 1.2, source="comms_peer", player_id=2))
        x, y = tracker.position_at(0.0)
        self.assertAlmostEqual(x, -2.0, delta=0.2)
        self.assertAlmostEqual(y, 3.0, delta=0.2)
        vx, vy = tracker.velocity_at()
        self.assertEqual(vx, 0.0)
        self.assertEqual(vy, 0.0)

    def test_startup_spike_capped_after_warmup(self) -> None:
        tracker = BallTracker()
        tracker.update(0.0, _measurement(0.0, 0.0, 0.0))
        tracker.update(0.25, _measurement(3.0, 0.0, 0.25))
        self.assertLess(float(np.linalg.norm(tracker.velocity)), 1.0)

        for t in np.linspace(0.5, 1.25, MIN_MEASUREMENTS_BEFORE_INFERRED_V + 2):
            tracker.update(t, _measurement(3.0, 0.0, t))

        speed = float(np.linalg.norm(tracker.velocity))
        self.assertLessEqual(speed, MAX_INFERRED_SPEED_MPS + 0.01)

    def test_apply_fused_estimate_propagates_to_now(self) -> None:
        tracker = BallTracker()
        tracker.apply_fused_estimate(
            position=np.array([1.0, 0.0]),
            velocity=np.array([0.5, 0.0]),
            estimate_time_sec=9.0,
            now_sec=10.0,
            valid=True,
        )
        self.assertTrue(tracker.valid)
        x, _y = tracker.position_at(0.0)
        self.assertGreater(x, 1.0)

    def test_apply_fused_estimate_invalid_clears(self) -> None:
        tracker = BallTracker()
        tracker.update(0.0, _measurement(1.0, 0.0, 0.0))
        tracker.apply_fused_estimate(
            position=np.zeros(2),
            velocity=np.zeros(2),
            estimate_time_sec=0.0,
            now_sec=1.0,
            valid=False,
        )
        self.assertFalse(tracker.valid)

    def test_vision_global_requires_pose(self) -> None:
        wm = WorldModel()
        wm.update_ball_from_vision(
            local_x=2.0,
            local_y=0.1,
            global_x=None,
            global_y=None,
            pixel_x=100.0,
            pixel_y=100.0,
            confidence=90.0,
            now_sec=1.0,
        )
        self.assertTrue(wm.vision_ball.has_local_position())
        self.assertFalse(wm.vision_ball.has_global_position())


if __name__ == "__main__":
    unittest.main()

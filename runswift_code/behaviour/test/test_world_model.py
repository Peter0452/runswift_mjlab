#!/usr/bin/env python3
from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path


def _ensure_module(name: str) -> types.ModuleType:
    if name in sys.modules:
        return sys.modules[name]

    module = types.ModuleType(name)
    sys.modules[name] = module

    if "." in name:
        parent_name, child_name = name.rsplit(".", 1)
        parent = _ensure_module(parent_name)
        setattr(parent, child_name, module)

    return module


def _install_ros_stubs() -> None:
    rclpy = _ensure_module("rclpy")
    rclpy.__path__ = []  # type: ignore[attr-defined]

    callback_groups = _ensure_module("rclpy.callback_groups")
    callback_groups.ReentrantCallbackGroup = type("ReentrantCallbackGroup", (), {})

    qos = _ensure_module("rclpy.qos")
    qos.QoSProfile = type("QoSProfile", (), {})
    qos.ReliabilityPolicy = type("ReliabilityPolicy", (), {"RELIABLE": 0})
    qos.HistoryPolicy = type("HistoryPolicy", (), {"KEEP_LAST": 0})

    node = _ensure_module("rclpy.node")
    node.Node = type("Node", (), {})

    geometry_msgs = _ensure_module("geometry_msgs.msg")
    geometry_msgs.Point = type("Point", (), {})
    geometry_msgs.PointStamped = type("PointStamped", (), {})
    geometry_msgs.Pose2D = type("Pose2D", (), {})

    std_msgs = _ensure_module("std_msgs.msg")
    std_msgs.Bool = type("Bool", (), {})
    std_msgs.String = type("String", (), {})

    vision_interface = _ensure_module("vision_interface.msg")
    vision_interface.CameraGroundQuad = type("CameraGroundQuad", (), {})
    vision_interface.Detections = type("Detections", (), {})

    visualization_msgs = _ensure_module("visualization_msgs.msg")
    visualization_msgs.Marker = type("Marker", (), {"DELETEALL": 0, "LINE_STRIP": 1, "SPHERE": 2, "ADD": 0})
    visualization_msgs.MarkerArray = type("MarkerArray", (), {})

    communication_interface = _ensure_module("communication_interface.msg")
    communication_interface.GameState = type("GameState", (), {})
    communication_interface.RobotComms = type("RobotComms", (), {})

    booster_interface = _ensure_module("booster_interface.msg")
    booster_interface.LowState = type("LowState", (), {})
    booster_interface.FallDownState = type("FallDownState", (), {"IS_READY": 0})

    whistle_detector_interface = _ensure_module("whistle_detector_interface.msg")
    whistle_detector_interface.WhistleDetection = type("WhistleDetection", (), {})

    object_avoidance = types.ModuleType("object_avoidance_apf")
    object_avoidance.PFParams = type("PFParams", (), {})
    object_avoidance.SimpleAvoidanceFilter = type("SimpleAvoidanceFilter", (), {})
    sys.modules["object_avoidance_apf"] = object_avoidance

    bigbrother = types.ModuleType("bigbrother")
    bigbrother.log_ball_vision = lambda **_: None
    bigbrother.log_field_features = lambda **_: None
    bigbrother.log_ground_fov_markers = lambda **_: None
    sys.modules["bigbrother"] = bigbrother


_install_ros_stubs()

_yaml = types.ModuleType("yaml")
_yaml.safe_load = lambda _f: {
    "length": 9.0,
    "width": 6.0,
    "goalAreaLength": 1.0,
    "goalAreaWidth": 3.0,
    "penaltyAreaLength": 2.0,
    "penaltyAreaWidth": 4.0,
    "penaltyMarkDistance": 1.5,
    "centreCircleDiameter": 1.51,
    "cornerArcRadius": 0.5,
}
sys.modules["yaml"] = _yaml

_ament = types.ModuleType("ament_index_python.packages")
_repo_root = Path(__file__).resolve().parents[3]
_ament.get_package_share_directory = lambda _name: str(_repo_root / "runswift_configs")
sys.modules["ament_index_python"] = types.ModuleType("ament_index_python")
sys.modules["ament_index_python.packages"] = _ament

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import numpy as np

from ball_tracker import BallTracker
from legacy_world_model import (  # noqa: E402
    BallModel,
    CameraGroundFovModel,
    CENTER_CIRCLE_RADIUS_M,
    FUTURE_HORIZONS_SEC,
    Pose2,
    RobotObservation,
    RobotPeerFromComms,
    SET_PLAY_GOAL_KICK,
    SET_PLAY_NONE,
    STATE_PLAYING,
    STATE_SET,
    VISION_ROBOT_MEMORY_SEC,
    WorldModel,
    WorldStateSnapshot,
    robot_local_to_global,
    world_model_to_dict,
)


VISION_TIMEOUT_SEC = 1.2
ROLE_KW = dict(
    margin_m=0.2,
    keep_margin_m=0.1,
    w_lane_m_per_rad=0.4,
    w_body_m_per_rad=0.15,
    now_sec=10.0,
    peer_timeout_sec=2.0,
)


def _add_vision_ball(wm: WorldModel, now_sec: float) -> None:
    wm.update_ball_from_vision(
        local_x=0.1,
        local_y=0.2,
        global_x=1.0,
        global_y=2.0,
        pixel_x=10.0,
        pixel_y=20.0,
        confidence=90.0,
        now_sec=now_sec,
    )


def _ball_at_origin(wm: WorldModel) -> None:
    wm.ball = BallModel(global_x=0.0, global_y=0.0, source="test")
    wm.fused_ball = BallModel(global_x=0.0, global_y=0.0, source="fused")


def _setup_wm(
    wm: WorldModel,
    *,
    player_id: int = 2,
    pose: Pose2,
) -> None:
    wm.game.player_id = player_id
    wm.game.team_number = 1
    wm.update_self_pose(pose.x, pose.y, pose.theta)
    _ball_at_origin(wm)


class WorldModelBallTest(unittest.TestCase):
    def test_has_fresh_vision_ball_from_last_seen(self) -> None:
        wm = WorldModel()
        _add_vision_ball(wm, now_sec=2.0)
        self.assertTrue(wm.has_fresh_vision_ball(2.0, VISION_TIMEOUT_SEC))
        self.assertFalse(wm.has_fresh_vision_ball(5.0, VISION_TIMEOUT_SEC))

    def test_has_vision_memory_keeps_stale_local_coords(self) -> None:
        wm = WorldModel()
        _add_vision_ball(wm, now_sec=2.0)
        self.assertTrue(wm.has_vision_memory(5.0, max_age_sec=10.0))
        self.assertFalse(wm.has_vision_memory(15.0, max_age_sec=10.0))

    def test_ball_property_aliases_fused_ball(self) -> None:
        wm = WorldModel()
        fused = BallModel(global_x=1.5, global_y=-0.5, source="fused", last_seen_sec=3.0)
        wm.fused_ball = fused
        self.assertEqual(wm.ball.global_x, 1.5)
        wm.ball = BallModel(global_x=2.0, global_y=0.0, source="fused")
        self.assertEqual(wm.fused_ball.global_x, 2.0)

    def test_vision_measurement_for_tracker_requires_fresh_vision(self) -> None:
        wm = WorldModel()
        _add_vision_ball(wm, now_sec=2.0)

        meas = wm.vision_measurement_for_tracker(
            now_sec=2.5,
            vision_timeout_sec=VISION_TIMEOUT_SEC,
        )
        self.assertIsNotNone(meas)
        self.assertEqual(meas.source, "vision")

        stale = wm.vision_measurement_for_tracker(
            now_sec=5.0,
            vision_timeout_sec=VISION_TIMEOUT_SEC,
        )
        self.assertIsNone(stale)

    def test_has_global_ball_uses_fused_when_set(self) -> None:
        wm = WorldModel()
        wm.fused_ball = BallModel(
            global_x=1.0,
            global_y=2.0,
            source="fused",
            last_seen_sec=1.0,
        )
        self.assertTrue(
            wm.has_global_ball(now_sec=2.0, vision_timeout_sec=VISION_TIMEOUT_SEC)
        )

    def test_has_global_ball_rejects_off_field_fused(self) -> None:
        wm = WorldModel()
        wm.fused_ball = BallModel(
            global_x=20.0,
            global_y=0.0,
            source="fused",
            last_seen_sec=1.0,
        )
        self.assertFalse(
            wm.has_global_ball(now_sec=2.0, vision_timeout_sec=VISION_TIMEOUT_SEC)
        )

    def test_off_field_vision_clears_vision_ball(self) -> None:
        wm = WorldModel()
        _add_vision_ball(wm, now_sec=2.0)
        wm.update_ball_from_vision(
            local_x=0.1,
            local_y=0.2,
            global_x=20.0,
            global_y=0.0,
            pixel_x=10.0,
            pixel_y=20.0,
            confidence=90.0,
            now_sec=2.5,
        )
        self.assertFalse(wm.vision_ball.has_global_position())
        self.assertFalse(
            wm.has_fresh_vision_global(2.5, VISION_TIMEOUT_SEC)
        )

    def test_stale_bounded_vision_ball_xy_rejects_off_field(self) -> None:
        wm = WorldModel()
        wm.vision_ball = BallModel(
            global_x=20.0,
            global_y=0.0,
            source="vision",
            last_seen_sec=2.0,
        )
        self.assertIsNone(wm.stale_bounded_vision_ball_xy(5.0, max_age_sec=10.0))

    def test_stale_bounded_vision_ball_xy_returns_in_field(self) -> None:
        wm = WorldModel()
        _add_vision_ball(wm, now_sec=2.0)
        self.assertEqual(
            wm.stale_bounded_vision_ball_xy(5.0, max_age_sec=10.0),
            (1.0, 2.0),
        )

    def test_build_team_ball_inputs_uses_receive_time_for_peers(self) -> None:
        wm = WorldModel()
        wm.game.player_id = 2
        tracker = BallTracker()
        tracker.valid = True
        tracker.position[:] = [1.0, 0.0]
        tracker.velocity[:] = [0.0, 0.0]
        tracker.last_measurement_sec = 9.0

        wm.robot_peers_from_comms[3] = RobotPeerFromComms(
            player_id=3,
            pose=Pose2(x=0.0, y=0.0, theta=0.0),
            ball_global=BallModel(
                global_x=1.1,
                global_y=0.0,
                global_vx=0.5,
                global_vy=0.0,
                source="comms_peer",
            ),
            purpose="assist",
            last_seen_sec=9.5,
            ball_valid=True,
        )

        local, peers = wm.build_team_ball_inputs(
            now_sec=10.0,
            my_player_id=2,
            local_tracker=tracker,
            peer_timeout_sec=2.0,
            local_timeout_sec=3.0,
        )
        self.assertEqual(local.player_id, 2)
        self.assertEqual(len(peers), 1)
        self.assertEqual(peers[0].entry_time_sec, 9.5)
        self.assertAlmostEqual(peers[0].velocity[0], 0.5)


class WorldStateSnapshotLoggingTest(unittest.TestCase):
    def test_to_dict_logs_local_and_fused_futures(self) -> None:
        local_tracker = BallTracker()
        local_tracker.valid = True
        local_tracker.position = np.array([0.0, 0.0])
        local_tracker.velocity = np.array([1.0, 0.0])
        local_tracker.num_measurements = 10
        local_tracker.last_measurement_sec = 10.0
        local_tracker.last_update_sec = 10.0

        fused_tracker = BallTracker()
        fused_tracker.apply_fused_estimate(
            position=np.array([2.0, 0.0]),
            velocity=np.array([0.5, 0.0]),
            estimate_time_sec=10.0,
            now_sec=10.0,
            valid=True,
        )

        snap = WorldStateSnapshot(
            wm=WorldModel(),
            role="chase",
            vision_ball_timeout_sec=VISION_TIMEOUT_SEC,
            timestamp_sec=10.0,
            ball_tracker=fused_tracker,
            local_ball_tracker=local_tracker,
        )
        record = snap.to_dict()

        self.assertTrue(record["fused_ball_valid"])
        self.assertTrue(record["local_ball_valid"])
        self.assertEqual(record["future_ball1"], record["fused_future_ball1"])
        self.assertNotEqual(record["local_future_ball1"], record["fused_future_ball1"])
        self.assertTrue(snap.has_fresh_fused_ball(max_age_sec=1.0))
        self.assertAlmostEqual(snap.fused_ball_age_sec(), 0.0)
        for horizon in FUTURE_HORIZONS_SEC:
            self.assertIn(f"fused_future_ball{horizon}", record)
            self.assertIn(f"local_future_ball{horizon}", record)
            self.assertEqual(record[f"future_ball{horizon}"], record[f"fused_future_ball{horizon}"])


class WorldModelDecideRoleTest(unittest.TestCase):
    def _decide(
        self,
        wm: WorldModel,
        *,
        player_id: int = 2,
        current_role: str = "assist",
    ) -> str:
        wm.game.player_id = player_id
        return wm.decide_role(
            my_player_id=player_id,
            current_role=current_role,
            **ROLE_KW,
        )

    def test_behind_ball_beats_past_ball_despite_distance(self) -> None:
        wm = WorldModel()
        # Past the ball (close) vs goal-side peer: lane penalty flips winner.
        _setup_wm(wm, player_id=2, pose=Pose2(x=2.0, y=0.0, theta=3.14159))
        wm.robot_peers_from_comms[3] = RobotPeerFromComms(
            player_id=3,
            pose=Pose2(x=-2.0, y=0.0, theta=0.0),
            ball_global=BallModel(),
            purpose="assist",
            last_seen_sec=10.0,
        )
        self.assertEqual(self._decide(wm), "assist")

    def test_closer_goal_side_still_chases(self) -> None:
        wm = WorldModel()
        _setup_wm(wm, player_id=2, pose=Pose2(x=-2.0, y=0.0, theta=0.0))
        wm.robot_peers_from_comms[3] = RobotPeerFromComms(
            player_id=3,
            pose=Pose2(x=-4.0, y=0.0, theta=0.0),
            ball_global=BallModel(),
            purpose="assist",
            last_seen_sec=10.0,
        )
        self.assertEqual(self._decide(wm), "chase")

    def test_incumbent_hysteresis_small_score_gap(self) -> None:
        wm = WorldModel()
        _setup_wm(wm, player_id=2, pose=Pose2(x=-2.0, y=0.0, theta=0.0))
        wm.robot_peers_from_comms[3] = RobotPeerFromComms(
            player_id=3,
            pose=Pose2(x=-2.05, y=0.0, theta=0.0),
            ball_global=BallModel(),
            purpose="assist",
            last_seen_sec=10.0,
        )
        self.assertEqual(self._decide(wm, current_role="chase"), "chase")

    def test_incumbent_yields_large_score_gap(self) -> None:
        wm = WorldModel()
        _setup_wm(wm, player_id=2, pose=Pose2(x=2.0, y=0.0, theta=3.14159))
        wm.robot_peers_from_comms[3] = RobotPeerFromComms(
            player_id=3,
            pose=Pose2(x=-2.0, y=0.0, theta=0.0),
            ball_global=BallModel(),
            purpose="assist",
            last_seen_sec=10.0,
        )
        self.assertEqual(self._decide(wm, current_role="chase"), "assist")

    def test_purpose_chase_does_not_block_clearly_better_lower_id(self) -> None:
        wm = WorldModel()
        _setup_wm(wm, player_id=2, pose=Pose2(x=-2.0, y=0.0, theta=0.0))
        wm.robot_peers_from_comms[4] = RobotPeerFromComms(
            player_id=4,
            pose=Pose2(x=-5.0, y=0.0, theta=0.0),
            ball_global=BallModel(),
            purpose="chase",
            last_seen_sec=10.0,
        )
        self.assertEqual(self._decide(wm), "chase")

    def test_purpose_chase_defers_when_scores_within_margin(self) -> None:
        wm = WorldModel()
        _setup_wm(wm, player_id=2, pose=Pose2(x=-2.0, y=0.0, theta=0.0))
        wm.robot_peers_from_comms[4] = RobotPeerFromComms(
            player_id=4,
            pose=Pose2(x=-2.05, y=0.0, theta=0.0),
            ball_global=BallModel(),
            purpose="chase",
            last_seen_sec=10.0,
        )
        self.assertEqual(self._decide(wm), "assist")

    def test_opponent_set_play_assist(self) -> None:
        wm = WorldModel()
        _setup_wm(wm, player_id=2, pose=Pose2(x=-2.0, y=0.0, theta=0.0))
        wm.game.kicking_team = 99
        wm.game.team_number = 1
        self.assertEqual(self._decide(wm), "assist")

    def test_tie_score_higher_player_id(self) -> None:
        wm = WorldModel()
        _setup_wm(wm, player_id=2, pose=Pose2(x=-2.0, y=0.0, theta=0.0))
        wm.robot_peers_from_comms[3] = RobotPeerFromComms(
            player_id=3,
            pose=Pose2(x=-2.0, y=0.0, theta=0.0),
            ball_global=BallModel(),
            purpose="assist",
            last_seen_sec=10.0,
        )
        self.assertEqual(self._decide(wm), "assist")

    def test_goalie_player_one(self) -> None:
        wm = WorldModel()
        _setup_wm(wm, player_id=1, pose=Pose2(x=-5.0, y=0.0, theta=0.0))
        self.assertEqual(self._decide(wm, player_id=1), "goalie")

    def test_vision_ball_preferred_over_fused_for_role(self) -> None:
        wm = WorldModel()
        wm.game.player_id = 2
        wm.update_self_pose(x=-2.0, y=0.0, theta=0.0)
        wm.vision_ball = BallModel(
            global_x=0.0,
            global_y=0.0,
            source="vision",
            confidence=90.0,
            last_seen_sec=10.0,
        )
        wm.fused_ball = BallModel(
            global_x=5.0,
            global_y=0.0,
            source="fused",
            last_seen_sec=10.0,
        )
        wm.ball = wm.fused_ball
        # Fused at x=5 would make peer at -2 closer to fused; vision at origin makes self chase.
        wm.robot_peers_from_comms[3] = RobotPeerFromComms(
            player_id=3,
            pose=Pose2(x=-3.0, y=0.0, theta=0.0),
            ball_global=BallModel(),
            purpose="assist",
            last_seen_sec=10.0,
        )
        role = wm.decide_role(
            my_player_id=2,
            current_role="assist",
            ball_xy=None,
            vision_timeout_sec=VISION_TIMEOUT_SEC,
            **{k: v for k, v in ROLE_KW.items() if k != "now_sec"},
            now_sec=10.0,
        )
        self.assertEqual(role, "chase")


class CameraGroundFovTest(unittest.TestCase):
    def test_robot_local_to_global(self) -> None:
        gx, gy = robot_local_to_global(1.0, 0.0, 2.0, 3.0, 0.0)
        self.assertAlmostEqual(gx, 3.0)
        self.assertAlmostEqual(gy, 3.0)

    def test_update_camera_ground_fov_serializes_in_snapshot_dict(self) -> None:
        wm = WorldModel()
        wm.update_camera_ground_fov(
            local_corners=[(1.0, 0.0), (2.0, 0.0), (2.0, -1.0), (1.0, -1.0)],
            global_corners=[(3.0, 1.0), (4.0, 1.0), (4.0, 0.0), (3.0, 0.0)],
            adjusted_pixels=[(10.0, 10.0), (200.0, 10.0), (200.0, 200.0), (10.0, 200.0)],
            valid=True,
            now_sec=12.5,
        )
        payload = world_model_to_dict(wm)["camera_ground_fov"]
        self.assertTrue(payload["valid"])
        self.assertEqual(len(payload["global_corners"]), 4)
        self.assertEqual(payload["last_seen_sec"], 12.5)


GLOBAL_TEST_QUAD = [(1.0, 3.0), (3.0, 3.0), (3.0, 1.0), (1.0, 1.0)]


def _vision_robot(
    x: float, y: float, label: str, last_seen_sec: float,
) -> RobotObservation:
    affinity = {"Opponent": -1.0, "Person": -0.7}.get(label, 0.0)
    return RobotObservation(
        pose=Pose2(x=x, y=y, theta=0.0),
        team_affinity=affinity,
        source="vision",
        label=label,
        last_seen_sec=last_seen_sec,
    )


class VisionRobotMemoryTest(unittest.TestCase):
    def _wm_with_quad(self, *, valid: bool = True) -> WorldModel:
        wm = WorldModel()
        wm.update_camera_ground_fov(
            local_corners=[(0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0)],
            global_corners=list(GLOBAL_TEST_QUAD),
            adjusted_pixels=[],
            valid=valid,
            now_sec=0.0,
        )
        return wm

    def test_inside_quad_one_miss_keeps_obstacle(self) -> None:
        wm = self._wm_with_quad()
        wm.robots = [_vision_robot(2.0, 2.0, "Opponent", 5.0)]
        wm.replace_vision_robots([], now_sec=10.0)
        vision = [r for r in wm.robots if r.source == "vision"]
        self.assertEqual(len(vision), 1)
        self.assertEqual(vision[0].vision_miss_ticks, 1)

    def test_inside_quad_two_misses_removes_obstacle(self) -> None:
        wm = self._wm_with_quad()
        wm.robots = [_vision_robot(2.0, 2.0, "Opponent", 5.0)]
        wm.replace_vision_robots([], now_sec=10.0)
        wm.replace_vision_robots([], now_sec=10.033)
        vision = [r for r in wm.robots if r.source == "vision"]
        self.assertEqual(vision, [])

    def test_outside_quad_not_redetected_is_kept_until_ttl(self) -> None:
        wm = self._wm_with_quad()
        wm.robots = [_vision_robot(5.0, 5.0, "Opponent", 5.0)]
        wm.replace_vision_robots([], now_sec=10.0)
        self.assertEqual(len(wm.path_planning_obstacles()), 1)
        wm.replace_vision_robots([], now_sec=5.0 + VISION_ROBOT_MEMORY_SEC + 1.0)
        self.assertEqual(wm.path_planning_obstacles(), [])

    def test_current_detection_is_appended(self) -> None:
        wm = self._wm_with_quad()
        fresh = _vision_robot(2.0, 2.0, "Person", 10.0)
        wm.replace_vision_robots([fresh], now_sec=10.0)
        vision = [r for r in wm.robots if r.source == "vision"]
        self.assertEqual(len(vision), 1)
        self.assertAlmostEqual(vision[0].last_seen_sec, 10.0)
        self.assertEqual(vision[0].vision_miss_ticks, 0)

    def test_inside_quad_merge_updates_nearby_memory(self) -> None:
        wm = self._wm_with_quad()
        wm.robots = [_vision_robot(2.0, 2.0, "Opponent", 5.0)]
        updated = _vision_robot(2.1, 2.1, "Opponent", 10.0)
        wm.replace_vision_robots([updated], now_sec=10.0)
        vision = [r for r in wm.robots if r.source == "vision"]
        self.assertEqual(len(vision), 1)
        self.assertAlmostEqual(vision[0].pose.x, 2.1)
        self.assertAlmostEqual(vision[0].pose.y, 2.1)
        self.assertEqual(vision[0].vision_miss_ticks, 0)

    def test_same_frame_duplicate_detections_merge(self) -> None:
        wm = self._wm_with_quad()
        d1 = _vision_robot(2.0, 2.0, "Opponent", 10.0)
        d2 = _vision_robot(2.05, 2.05, "Opponent", 10.0)
        wm.replace_vision_robots([d1, d2], now_sec=10.0)
        vision = [r for r in wm.robots if r.source == "vision"]
        self.assertEqual(len(vision), 1)

    def test_outside_quad_unmatched_keeps_without_miss_decay(self) -> None:
        wm = self._wm_with_quad()
        wm.robots = [_vision_robot(5.0, 5.0, "Opponent", 5.0)]
        wm.replace_vision_robots([], now_sec=10.0)
        vision = wm.path_planning_obstacles()
        self.assertEqual(len(vision), 1)
        self.assertEqual(vision[0].vision_miss_ticks, 0)

    def test_invalid_quad_skips_instant_decay(self) -> None:
        wm = self._wm_with_quad(valid=False)
        wm.robots = [_vision_robot(2.0, 2.0, "Opponent", 5.0)]
        wm.replace_vision_robots([], now_sec=10.0)
        self.assertEqual(len(wm.path_planning_obstacles()), 1)

    def test_path_planning_includes_robot_likely_opponents_does_not(self) -> None:
        wm = WorldModel()
        wm.robots = [
            _vision_robot(0.0, 0.0, "Robot", 0.0),
            _vision_robot(1.0, 1.0, "Opponent", 0.0),
        ]
        self.assertEqual(len(wm.path_planning_obstacles()), 2)
        self.assertEqual(len(wm.likely_opponents()), 1)
        self.assertEqual(wm.likely_opponents()[0].label, "Opponent")

    def test_merge_ttl_drops_stale_outside_quad_at_30s(self) -> None:
        wm = self._wm_with_quad()
        wm.robots = [_vision_robot(5.0, 5.0, "Opponent", 0.0)]
        wm.replace_vision_robots([], now_sec=29.0)
        self.assertEqual(len(wm.path_planning_obstacles()), 1)
        wm.replace_vision_robots([], now_sec=31.0)
        self.assertEqual(wm.path_planning_obstacles(), [])


class VisionRobotFieldBoundsTest(unittest.TestCase):
    def test_off_field_detection_rejected(self) -> None:
        wm = WorldModel()
        wm.replace_vision_robots(
            [_vision_robot(20.0, 0.0, "Opponent", 10.0)],
            now_sec=10.0,
        )
        vision = [r for r in wm.robots if r.source == "vision"]
        self.assertEqual(vision, [])

    def test_in_field_detection_accepted(self) -> None:
        wm = WorldModel()
        wm.replace_vision_robots(
            [_vision_robot(2.0, 2.0, "Opponent", 10.0)],
            now_sec=10.0,
        )
        vision = [r for r in wm.robots if r.source == "vision"]
        self.assertEqual(len(vision), 1)
        self.assertAlmostEqual(vision[0].pose.x, 2.0)
        self.assertAlmostEqual(vision[0].pose.y, 2.0)

    def test_set_play_buffer_allows_slightly_outside_strict_line(self) -> None:
        wm = WorldModel()
        edge = _vision_robot(4.9, 0.0, "Opponent", 10.0)
        wm.replace_vision_robots([edge], now_sec=10.0)
        self.assertEqual([r for r in wm.robots if r.source == "vision"], [])

        wm.game.set_play = SET_PLAY_GOAL_KICK
        wm.replace_vision_robots([edge], now_sec=10.0)
        vision = [r for r in wm.robots if r.source == "vision"]
        self.assertEqual(len(vision), 1)
        self.assertAlmostEqual(vision[0].pose.x, 4.9)


def _trusted_ball_at(x: float, y: float, now_sec: float = 10.0) -> BallModel:
    return BallModel(
        global_x=x,
        global_y=y,
        source="fused",
        confidence=100.0,
        last_seen_sec=now_sec,
    )


class BallMovedSinceSetTest(unittest.TestCase):
    def test_reset_latches_reference_position(self) -> None:
        wm = WorldModel()
        wm.fused_ball = _trusted_ball_at(0.0, 0.0)
        wm.reset_ball_movement_since_set((0.0, 0.0))
        self.assertFalse(wm.game.ball_moved_since_set)
        self.assertEqual(wm.game.ball_xy_at_set, (0.0, 0.0))

    def test_movement_below_radius_keeps_gc_state_set(self) -> None:
        wm = WorldModel()
        wm.game.state = STATE_SET
        wm.reset_ball_movement_since_set((0.0, 0.0))
        wm.fused_ball = _trusted_ball_at(0.5, 0.0)
        wm.tick_ball_movement_since_set(10.0)
        self.assertFalse(wm.game.ball_moved_since_set)
        self.assertEqual(wm.gc_state, STATE_SET)

    def test_movement_above_radius_promotes_gc_state_to_playing(self) -> None:
        wm = WorldModel()
        wm.game.state = STATE_SET
        wm.reset_ball_movement_since_set((0.0, 0.0))
        wm.fused_ball = _trusted_ball_at(0.5, 0.0)
        wm.tick_ball_movement_since_set(10.0)
        beyond = CENTER_CIRCLE_RADIUS_M + 0.1
        wm.fused_ball = _trusted_ball_at(beyond, 0.0)
        wm.tick_ball_movement_since_set(10.1)
        self.assertTrue(wm.game.ball_moved_since_set)
        self.assertEqual(wm.game.state, STATE_SET)
        self.assertEqual(wm.gc_state, STATE_PLAYING)

    def test_set_play_blocks_ball_movement_promotion(self) -> None:
        wm = WorldModel()
        wm.game.state = STATE_SET
        wm.game.set_play = SET_PLAY_GOAL_KICK
        wm.reset_ball_movement_since_set((0.0, 0.0))
        beyond = CENTER_CIRCLE_RADIUS_M + 0.1
        wm.fused_ball = _trusted_ball_at(beyond, 0.0)
        wm.tick_ball_movement_since_set(10.0)
        self.assertFalse(wm.game.ball_moved_since_set)
        self.assertEqual(wm.gc_state, STATE_SET)

    def test_deferred_latch_when_no_ball_at_set_entry(self) -> None:
        wm = WorldModel()
        wm.game.state = STATE_SET
        wm.reset_ball_movement_since_set(None)
        wm.fused_ball = _trusted_ball_at(0.0, 0.0)
        wm.tick_ball_movement_since_set(10.0)
        self.assertFalse(wm.game.ball_moved_since_set)
        self.assertEqual(wm.game.ball_xy_at_set, (0.0, 0.0))

    def test_ball_leaving_center_circle_promotes_gc_state_to_playing(self) -> None:
        wm = WorldModel()
        wm.game.state = STATE_SET
        wm.reset_ball_movement_since_set((0.02, 0.04))
        wm.fused_ball = _trusted_ball_at(0.436, 0.011)
        wm.tick_ball_movement_since_set(10.0)
        self.assertFalse(wm.game.ball_moved_since_set)
        wm.fused_ball = _trusted_ball_at(0.916, 0.062)
        wm.tick_ball_movement_since_set(10.1)
        self.assertTrue(wm.game.ball_moved_since_set)
        self.assertEqual(wm.gc_state, STATE_PLAYING)

    def test_far_field_reading_does_not_promote_gc_state(self) -> None:
        wm = WorldModel()
        wm.game.state = STATE_SET
        wm.reset_ball_movement_since_set((0.02, 0.04))
        wm.fused_ball = _trusted_ball_at(2.2966363430023193, -0.12873980402946472)
        wm.tick_ball_movement_since_set(10.0)
        self.assertFalse(wm.game.ball_moved_since_set)
        self.assertEqual(wm.gc_state, STATE_SET)

    def test_teleport_reading_does_not_promote_gc_state(self) -> None:
        wm = WorldModel()
        wm.game.state = STATE_SET
        wm.reset_ball_movement_since_set((0.02, 0.04))
        wm.fused_ball = _trusted_ball_at(1.0, 0.0)
        wm.tick_ball_movement_since_set(10.0)
        self.assertFalse(wm.game.ball_moved_since_set)
        self.assertEqual(wm.gc_state, STATE_SET)

    def test_update_game_preserves_ball_movement_fields(self) -> None:
        wm = WorldModel()
        wm.game.ball_moved_since_set = True
        wm.game.ball_xy_at_set = (1.0, 2.0)
        wm.update_game(state=STATE_SET, stopped=True, whistle_heard=False)
        self.assertTrue(wm.game.ball_moved_since_set)
        self.assertEqual(wm.game.ball_xy_at_set, (1.0, 2.0))


if __name__ == "__main__":
    unittest.main()

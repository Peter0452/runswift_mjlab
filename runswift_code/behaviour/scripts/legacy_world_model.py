#!/usr/bin/env python3
"""Threaded ROS owner for the behaviour world model.

Shared types (``Pose2``, ``BallModel``, GC codes, ...) live in
``runswift_types``. ``WorldModel`` / ``WorldStateNode`` own the estimator and
ROS subscriptions; the chase node reads them via ``WorldStateNode``.
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import yaml
from ament_index_python.packages import get_package_share_directory
from dataclasses import dataclass, field, replace
from math import atan2, cos, hypot, sin, pi

import numpy as np
from threading import Lock, RLock

from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from geometry_msgs.msg import Pose2D, Point
from vision_interface.msg import CameraGroundQuad, Detections
from visualization_msgs.msg import Marker, MarkerArray
from communication_interface.msg import GameState, RobotComms
from booster_interface.msg import LowState, FallDownState
from object_avoidance_apf import PFParams, SimpleAvoidanceFilter
from ball_tracker import BallTracker
from team_ball_fusion import (
    BallEstimateInput,
    DEFAULT_LOCAL_POSE_QUALITY,
    DEFAULT_PEER_POSE_QUALITY,
    TeamBallEstimate,
    fuse_team_ball,
)

from whistle_detector_interface.msg import WhistleDetection
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import bigbrother

from runswift_types import (
    BallMeasurement,
    BallModel,
    CameraGroundFovModel,
    GAME_PHASE_EXTRA_TIME,
    GAME_PHASE_NORMAL,
    GAME_PHASE_PENALTY_SHOOT_OUT,
    GAME_PHASE_TIMEOUT,
    GameModel,
    HeadModel,
    Pose2,
    RobotObservation,
    RobotPeerFromComms,
    SET_PLAY_CORNER_KICK,
    SET_PLAY_DIRECT_FREE_KICK,
    SET_PLAY_GOAL_KICK,
    SET_PLAY_INDIRECT_FREE_KICK,
    SET_PLAY_NONE,
    SET_PLAY_PENALTY_KICK,
    SET_PLAY_THROW_IN,
    STATE_FINISHED,
    STATE_INITIAL,
    STATE_PLAYING,
    STATE_READY,
    STATE_SET,
)

Pose2DModel = Pose2

TEAMMATE_THRESHOLD = 0.7
OPPONENT_THRESHOLD = -0.7

_dimension_yaml = Path(get_package_share_directory("runswift_config")) / "dimension.yaml"
with _dimension_yaml.open() as f:
    _dimension = yaml.safe_load(f)
FIELD_LENGTH_M = float(_dimension["length"])
FIELD_WIDTH_M = float(_dimension["width"])
CENTER_CIRCLE_RADIUS_M = float(_dimension["centreCircleDiameter"]) / 2.0
GOAL_WIDTH_M = float(_dimension["goalAreaWidth"])
GOAL_LENGTH_M = float(_dimension["goalAreaLength"])
PENALTY_WIDTH_M = float(_dimension["penaltyAreaWidth"])
PENALTY_LENGTH_M = float(_dimension["penaltyAreaLength"])
FORMATION_FIELD_DIMENSIONS: dict[str, float] = {
    key: float(value)
    for key, value in _dimension.items()
    if isinstance(value, (int, float))
}

ATTACK_GOAL_X = FIELD_LENGTH_M / 2.0
ATTACK_GOAL_Y = 0.0


def _wrap_angle(angle: float) -> float:
    return atan2(sin(angle), cos(angle))


def robot_local_to_global(
    local_x: float,
    local_y: float,
    robot_x: float,
    robot_y: float,
    robot_yaw: float,
) -> tuple[float, float]:
    global_x = robot_x + cos(robot_yaw) * local_x - sin(robot_yaw) * local_y
    global_y = robot_y + sin(robot_yaw) * local_x + cos(robot_yaw) * local_y
    return global_x, global_y


def point_in_quad(
    x: float, y: float, corners: list[tuple[float, float]],
) -> bool:
    """Return True if (x, y) lies inside the polygon defined by corners."""
    if len(corners) < 3:
        return False
    inside = False
    j = len(corners) - 1
    for i, (xi, yi) in enumerate(corners):
        xj, yj = corners[j]
        if ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi
        ):
            inside = not inside
        j = i
    return inside


def _robot_global_xy(robot: RobotObservation) -> tuple[float, float] | None:
    if robot.pose is None:
        return None
    return robot.pose.x, robot.pose.y


def _closest_robot_index(
    xy: tuple[float, float],
    robots: list[RobotObservation],
    *,
    radius: float,
    skip: set[int],
) -> int | None:
    best_i: int | None = None
    best_d = radius
    for i, robot in enumerate(robots):
        if i in skip:
            continue
        rxy = _robot_global_xy(robot)
        if rxy is None:
            continue
        d = hypot(xy[0] - rxy[0], xy[1] - rxy[1])
        if d < best_d:
            best_i = i
            best_d = d
    return best_i


def _in_camera_ground_quad(
    robot: RobotObservation, fov: CameraGroundFovModel,
) -> bool:
    rxy = _robot_global_xy(robot)
    if rxy is None:
        return False
    if not fov.valid or len(fov.global_corners) != 4:
        return False
    return point_in_quad(rxy[0], rxy[1], fov.global_corners)


def _refresh_vision_robot(
    old: RobotObservation, new: RobotObservation, now_sec: float,
) -> RobotObservation:
    return replace(
        old,
        pose=new.pose,
        label=new.label,
        confidence=new.confidence,
        team_affinity=new.team_affinity,
        last_seen_sec=now_sec,
        vision_miss_ticks=0,
    )


def lane_alignment_error(
    rx: float,
    ry: float,
    bx: float,
    by: float,
    tx: float,
    ty: float,
) -> float:
    """Radians: misalignment of robot→ball vs ball→attack target (0 = on attack line)."""
    robot_to_ball = atan2(by - ry, bx - rx)
    vec_goal_to_ball_x = bx - tx
    vec_goal_to_ball_y = by - ty
    ball_to_goal = atan2(-vec_goal_to_ball_y, -vec_goal_to_ball_x)
    return abs(_wrap_angle(robot_to_ball - ball_to_goal))


def body_alignment_error(
    rx: float,
    ry: float,
    bx: float,
    by: float,
    yaw: float,
) -> float:
    """Radians: |yaw − bearing(robot→ball)|."""
    bearing = atan2(by - ry, bx - rx)
    return abs(_wrap_angle(yaw - bearing))


def attack_score(
    rx: float,
    ry: float,
    bx: float,
    by: float,
    yaw: float,
    *,
    w_lane_m_per_rad: float,
    w_body_m_per_rad: float,
    tx: float = ATTACK_GOAL_X,
    ty: float = ATTACK_GOAL_Y,
) -> float:
    """Lower is better for chase election."""
    d_ball = hypot(bx - rx, by - ry)
    lane = lane_alignment_error(rx, ry, bx, by, tx, ty)
    body = body_alignment_error(rx, ry, bx, by, yaw)
    return d_ball + w_lane_m_per_rad * lane + w_body_m_per_rad * body


NORMAL_BALL_FIELD_BUFFER_M = 0.3
SET_PLAY_BALL_FIELD_BUFFER_M = 0.5
SET_BALL_MOTION_MAX_STEP_M = 0.5

VISION_KICK_BLOCKER_LABELS = frozenset({"Opponent", "Person"})
VISION_ROBOT_MEMORY_SEC = 1.0
VISION_PATH_OBSTACLE_LABELS = frozenset({"Robot", "robot", "Person", "Opponent"})
VISION_ROBOT_MERGE_RADIUS_M = 0.3
VISION_QUAD_MISS_TICKS_MAX = 2


def _vision_team_affinity(label: str) -> float:
    if label == "Opponent":
        return -1.0
    if label == "Person":
        return -0.7
    return 0.0


@dataclass
class WorldModel:
    """Shared behaviour world model.

    Compatibility properties keep the current threaded state-machine code
    working while the underlying data is structured into pose/head/ball/game
    models.
    """

    self_pose: Pose2 | None = None
    head: HeadModel = field(default_factory=HeadModel)
    fused_ball: BallModel = field(default_factory=BallModel)
    vision_ball: BallModel = field(default_factory=BallModel)
    camera_ground_fov: CameraGroundFovModel = field(default_factory=CameraGroundFovModel)
    game: GameModel = field(default_factory=GameModel)
    robots: list[RobotObservation] = field(default_factory=list)
    robot_peers_from_comms: dict[int, RobotPeerFromComms] = field(default_factory=dict)

    fall_down_state = FallDownState.IS_READY
    is_recovery_available: bool = False

    def teammates(self) -> list[RobotObservation]:
        return [
            robot for robot in self.robots
            if robot.team_affinity >= TEAMMATE_THRESHOLD
        ]

    def likely_opponents(
        self,
        *,
        now_sec: float | None = None,
        max_age_sec: float | None = None,
    ) -> list[RobotObservation]:
        """Vision Opponent/Person and any robot with opponent team affinity."""
        opponents = [
            robot for robot in self.robots
            if robot.team_affinity <= OPPONENT_THRESHOLD
            or ( # to be removed after testing
                robot.source == "vision"
                and robot.label in VISION_KICK_BLOCKER_LABELS
            )
        ]
        if now_sec is None or max_age_sec is None:
            return opponents
        return [
            robot for robot in opponents
            if robot.is_fresh(now_sec, max_age_sec)
        ]

    def path_planning_obstacles(self) -> list[RobotObservation]:
        """Vision humanoids to avoid when walking (Robot/Person/Opponent)."""
        return [
            robot for robot in self.robots
            if robot.source == "vision"
            and robot.label in VISION_PATH_OBSTACLE_LABELS
        ]

    def unknown_robots(self) -> list[RobotObservation]:
        return [
            robot for robot in self.robots
            if OPPONENT_THRESHOLD < robot.team_affinity < TEAMMATE_THRESHOLD
        ]

    def update_self_pose(self, x: float, y: float, theta: float) -> None:
        self.self_pose = Pose2(x=x, y=y, theta=theta)

    def update_falldown_state(self, fall_down_state: int, is_recovery_available: bool) -> None:
        self.fall_down_state = fall_down_state
        self.is_recovery_available = is_recovery_available

    def update_head(self, pitch: float, yaw: float) -> None:
        self.head.pitch = pitch
        self.head.yaw = yaw

    def _field_buffer_m(self) -> float:
        return (
            SET_PLAY_BALL_FIELD_BUFFER_M
            if self.game.set_play != SET_PLAY_NONE
            else NORMAL_BALL_FIELD_BUFFER_M
        )

    def position_allowed_at(self, global_x: float, global_y: float) -> bool:
        buffer_m = self._field_buffer_m()
        half_length = FIELD_LENGTH_M / 2.0 + buffer_m
        half_width = FIELD_WIDTH_M / 2.0 + buffer_m
        return (
            abs(global_x) <= half_length and
            abs(global_y) <= half_width
        )

    def position_within_circle(self, global_x: float, global_y: float, tolerance_m: float = 0.0) -> bool:
        # do not ask me why i used field buffer
        return (global_x**2 + global_y**2) ** 0.5 <= CENTER_CIRCLE_RADIUS_M + tolerance_m

    def ball_allowed_by_field_bounds(self, ball: BallModel) -> bool:
        if not ball.has_global_position():
            return False
        return self.position_allowed_at(ball.global_x, ball.global_y)

    def ball_allowed_at(self, global_x: float, global_y: float) -> bool:
        return self.position_allowed_at(global_x, global_y)

    def robot_allowed_at(self, global_x: float, global_y: float) -> bool:
        return self.position_allowed_at(global_x, global_y)

    def has_trusted_fused_ball(self) -> bool:
        """Fused estimate with a field-frame position inside allowed bounds."""
        return (
            self.has_fused_ball_position()
            and self.ball_allowed_by_field_bounds(self.fused_ball)
        )

    def stale_bounded_vision_ball_xy(
        self,
        now_sec: float,
        max_age_sec: float,
    ) -> tuple[float, float] | None:
        """In-bounds vision global position within max_age_sec (search memory)."""
        if self.vision_ball.last_seen_sec is None:
            return None
        if self.vision_ball.age_sec(now_sec) > max_age_sec:
            return None
        if not self.vision_ball.has_global_position():
            return None
        if not self.ball_allowed_by_field_bounds(self.vision_ball):
            return None
        return self.vision_ball.global_xy()

    def update_ball_from_vision(
        self,
        *,
        local_x: float,
        local_y: float,
        pixel_x: float,
        pixel_y: float,
        confidence: float,
        now_sec: float,
        global_x: float | None = None,
        global_y: float | None = None,
    ) -> None:
        """Update vision ball. Global coords are set only when pose is valid upstream."""
        candidate = BallModel(
            local_x=local_x,
            local_y=local_y,
            global_x=global_x,
            global_y=global_y,
            pixel_x=pixel_x,
            pixel_y=pixel_y,
            source="vision",
            confidence=confidence,
            last_seen_sec=now_sec,
        )

        if (
            candidate.has_global_position()
            and not self.ball_allowed_by_field_bounds(candidate)
        ):
            return

        self.vision_ball = candidate

    def update_camera_ground_fov(
        self,
        *,
        local_corners: list[tuple[float, float]],
        global_corners: list[tuple[float, float]],
        adjusted_pixels: list[tuple[float, float]],
        valid: bool,
        now_sec: float,
    ) -> None:
        self.camera_ground_fov = CameraGroundFovModel(
            local_corners=list(local_corners),
            global_corners=list(global_corners),
            adjusted_pixels=list(adjusted_pixels),
            valid=valid,
            last_seen_sec=now_sec,
        )

    def update_game(
        self,
        *,
        state: int,
        stopped: bool,
        set_play: int = 0,
        game_phase: int = 0,
        kicking_team: int | None = None,
        secs_remaining: int | None = None,
        secondary_time: int | None = None,
        team_number: int | None = None,
        player_id: int | None = None,
        role_id: int | None = None,
        my_team_info=None,
        opponent_team_info=None,
        my_penalty: int | None = None,
        secs_till_unpenalised: int | None = None,
        whistle_heard: bool,
        nubots_whistle_heard: bool,
    ) -> None:
        prev = self.game
        self.game = GameModel(
            state=state,
            stopped=stopped,
            set_play=set_play,
            game_phase=game_phase,
            kicking_team=kicking_team,
            secs_remaining=secs_remaining,
            secondary_time=secondary_time,
            team_number=team_number,
            player_id=player_id,
            role_id=role_id,
            my_team_info=my_team_info,
            opponent_team_info=opponent_team_info,
            my_penalty=my_penalty,
            secs_till_unpenalised=secs_till_unpenalised,
            whistle_heard=whistle_heard,
            nubots_whistle_heard=nubots_whistle_heard,
            ball_moved_since_set=prev.ball_moved_since_set,
            ball_xy_at_set=prev.ball_xy_at_set,
            ball_xy_prior_set_tick=prev.ball_xy_prior_set_tick,
        )

    def replace_vision_robots(self, vision_robots: list[RobotObservation], now_sec: float) -> None:
        non_vision_robots = [
            robot for robot in self.robots
            if robot.source != "vision"
        ]
        prev = [
            robot for robot in self.robots
            if robot.source == "vision"
            and robot.last_seen_sec is not None
            and (now_sec - robot.last_seen_sec) <= VISION_ROBOT_MEMORY_SEC
        ]

        matched_prev: set[int] = set()
        out: list[RobotObservation] = []
        merge_r = VISION_ROBOT_MERGE_RADIUS_M

        for new in vision_robots:
            if new.pose is not None and not self.robot_allowed_at(new.pose.x, new.pose.y):
                continue
            if new.pose is None:
                out.append(new)
                continue
            nxy = (new.pose.x, new.pose.y)

            pi = _closest_robot_index(
                nxy, prev, radius=merge_r, skip=matched_prev,
            )
            if pi is not None:
                matched_prev.add(pi)
                out.append(_refresh_vision_robot(prev[pi], new, now_sec))
                continue

            oi = _closest_robot_index(nxy, out, radius=merge_r, skip=set())
            if oi is not None:
                out[oi] = _refresh_vision_robot(out[oi], new, now_sec)
                continue

            out.append(replace(new, vision_miss_ticks=0))

        quad = self.camera_ground_fov
        for i, old in enumerate(prev):
            if i in matched_prev:
                continue
            if _in_camera_ground_quad(old, quad):
                ticks = old.vision_miss_ticks + 1
                if ticks < VISION_QUAD_MISS_TICKS_MAX:
                    out.append(replace(old, vision_miss_ticks=ticks))
            else:
                out.append(old)

        self.robots = non_vision_robots + out

    def upsert_comms_teammate(
        self,
        *,
        player_id: int,
        pose: Pose2 | None,
        confidence: float,
        now_sec: float,
    ) -> None:
        teammate = RobotObservation(
            player_id=player_id,
            role_id=player_id,
            pose=pose,
            team_affinity=1.0,
            confidence=confidence,
            source="comms",
            last_seen_sec=now_sec,
        )

        self.robots = [
            robot for robot in self.robots
            if not (robot.source == "comms" and robot.player_id == player_id)
        ]
        self.robots.append(teammate)

    @property
    def has_pose(self) -> bool:
        return self.self_pose is not None

    @property
    def robot_x(self) -> float:
        return self.self_pose.x if self.self_pose is not None else 0.0

    @property
    def robot_y(self) -> float:
        return self.self_pose.y if self.self_pose is not None else 0.0

    @property
    def robot_yaw(self) -> float:
        return self.self_pose.theta if self.self_pose is not None else 0.0

    @property
    def ball(self) -> BallModel:
        """Deprecated alias for fused_ball (kept for logging and legacy callers)."""
        return self.fused_ball

    @ball.setter
    def ball(self, value: BallModel) -> None:
        self.fused_ball = value

    def has_fresh_vision_ball(
        self,
        now_sec: float,
        timeout_sec: float,
    ) -> bool:
        """Ball was seen in the camera recently (pixel/local may exist without global)."""
        return (
            self.vision_ball.last_seen_sec is not None
            and self.vision_ball.is_fresh(now_sec, timeout_sec)
        )

    def has_fresh_vision_global(
        self,
        now_sec: float,
        timeout_sec: float,
    ) -> bool:
        """Fresh vision with a field-frame position inside allowed bounds."""
        return (
            self.vision_ball.has_global_position()
            and self.vision_ball.is_fresh(now_sec, timeout_sec)
            and self.ball_allowed_by_field_bounds(self.vision_ball)
        )

    def has_vision_memory(
        self,
        now_sec: float,
        max_age_sec: float,
    ) -> bool:
        """Stale but readable vision memory (local or global coords within max_age)."""
        if self.vision_ball.last_seen_sec is None:
            return False
        if self.vision_ball.age_sec(now_sec) > max_age_sec:
            return False
        return (
            self.vision_ball.has_local_position()
            or self.vision_ball.has_global_position()
        )

    def has_fused_ball_position(self) -> bool:
        """Fused team estimate has a field-frame position (snapshot-time validity)."""
        return self.fused_ball.has_global_position()

    def fused_ball_age_sec(self, now_sec: float) -> float:
        return self.fused_ball.age_sec(now_sec)

    def has_fresh_fused_ball(
        self,
        now_sec: float,
        max_age_sec: float,
    ) -> bool:
        """Fused estimate with a position younger than max_age_sec."""
        return (
            self.has_fused_ball_position()
            and self.fused_ball_age_sec(now_sec) <= max_age_sec
        )

    # i am spamming getups if the robot is not upright, this might be a bad idea!
    @property
    def has_fallen(self) -> bool:
        return self.fall_down_state != FallDownState.IS_READY
    
    @property
    def recovery_available(self) -> bool:
        return self.is_recovery_available
    
    @property
    def is_penalised(self) -> bool:
        return self.game.my_penalty is not None and self.game.my_penalty != 0
    
    @property
    def secs_till_unpenalised(self) -> int | None:
        return self.game.secs_till_unpenalised

    def has_global_ball(
        self,
        now_sec: float,
        vision_timeout_sec: float,
    ) -> bool:
        """Trusted in-bounds field-frame ball (fused estimate or fresh vision global)."""
        if self.has_trusted_fused_ball():
            return True
        return self.has_fresh_vision_global(now_sec, vision_timeout_sec)

    def vision_measurement_for_tracker(
        self,
        *,
        now_sec: float,
        vision_timeout_sec: float,
    ) -> BallMeasurement | None:
        """Vision-only measurement for the local ball tracker."""
        if (
            not self.vision_ball.has_global_position()
            or not self.vision_ball.is_fresh(now_sec, vision_timeout_sec)
            or not self.ball_allowed_by_field_bounds(self.vision_ball)
        ):
            return None

        return BallMeasurement(
            ball=self.vision_ball,
            source="vision",
            confidence=self.vision_ball.confidence,
            last_seen_sec=self.vision_ball.last_seen_sec,
        )

    def sync_ball_from_fused(self, fused: BallModel) -> None:
        """Update fused_ball from team fusion output."""
        self.fused_ball = fused

    def build_team_ball_inputs(
        self,
        *,
        now_sec: float,
        my_player_id: int,
        local_tracker: BallTracker,
        peer_timeout_sec: float,
        local_timeout_sec: float,
    ) -> tuple[BallEstimateInput, list[BallEstimateInput]]:
        local_time = (
            local_tracker.last_measurement_sec
            if local_tracker.last_measurement_sec is not None
            else now_sec
        )
        local = BallEstimateInput(
            player_id=my_player_id,
            position=local_tracker.position.copy(),
            velocity=local_tracker.velocity.copy(),
            entry_time_sec=local_time,
            valid=local_tracker.valid,
            pose_quality=DEFAULT_LOCAL_POSE_QUALITY,
        )

        peers: list[BallEstimateInput] = []
        for pid, peer in self.robot_peers_from_comms.items():
            if pid == my_player_id or not peer.ball_valid:
                continue
            ball = peer.ball_global
            if not ball.has_global_position():
                continue
            if (now_sec - peer.last_seen_sec) > peer_timeout_sec:
                continue
            vx = ball.global_vx if ball.global_vx is not None else 0.0
            vy = ball.global_vy if ball.global_vy is not None else 0.0
            peers.append(
                BallEstimateInput(
                    player_id=pid,
                    position=np.array([ball.global_x, ball.global_y], dtype=float),
                    velocity=np.array([vx, vy], dtype=float),
                    entry_time_sec=peer.last_seen_sec,
                    valid=True,
                    pose_quality=DEFAULT_PEER_POSE_QUALITY,
                )
            )
        return local, peers

    def fused_ball_model_from_estimate(
        self,
        estimate: TeamBallEstimate,
        *,
        now_sec: float,
    ) -> BallModel:
        if not estimate.valid:
            return BallModel(source="fused")
        return BallModel(
            global_x=float(estimate.position[0]),
            global_y=float(estimate.position[1]),
            global_vx=float(estimate.velocity[0]),
            global_vy=float(estimate.velocity[1]),
            source="fused",
            confidence=100.0,
            last_seen_sec=estimate.last_seen_sec or now_sec,
        )


    def fused_ball_global_xy(self) -> tuple[float, float]:
        xy = self.fused_ball.global_xy()
        return xy if xy is not None else (0.0, 0.0)

    @property
    def ball_global_x(self) -> float:
        return self.fused_ball_global_xy()[0]

    @property
    def ball_global_y(self) -> float:
        return self.fused_ball_global_xy()[1]

    def reset_ball_movement_since_set(
        self, ball_xy: tuple[float, float] | None,
    ) -> None:
        self.game.ball_moved_since_set = False
        self.game.ball_xy_at_set = ball_xy
        self.game.ball_xy_prior_set_tick = ball_xy

    def tick_ball_movement_since_set(self, _now_sec: float) -> None:
        if self.game.state != STATE_SET:
            return
        if self.game.set_play != SET_PLAY_NONE:
            return
        if self.game.ball_moved_since_set:
            return
        if not self.has_trusted_fused_ball():
            return
        current = self.fused_ball.global_xy()
        if current is None:
            return
        if not self.position_within_circle(current[0], current[1], self._field_buffer_m()):
            return
        if self.game.ball_xy_at_set is None:
            if self.position_within_circle(current[0], current[1], -0.40):
                self.game.ball_xy_at_set = current
                self.game.ball_xy_prior_set_tick = current
            return
        prior = self.game.ball_xy_prior_set_tick
        if prior is None:
            return
        else:
            step = hypot(current[0] - prior[0], current[1] - prior[1])
            if step > SET_BALL_MOTION_MAX_STEP_M:
                return
        
        ref_x, ref_y = self.game.ball_xy_at_set
        if hypot(current[0] - ref_x, current[1] - ref_y) > CENTER_CIRCLE_RADIUS_M:
            self.game.ball_moved_since_set = True
        self.game.ball_xy_prior_set_tick = current

    @property
    def gc_state(self) -> int:
        if self.game.state == STATE_SET:
            if self.game.whistle_heard or self.game.nubots_whistle_heard:
                return STATE_PLAYING
        
        return self.game.state

    @property
    def ball_moved_since_set(self) -> bool:
        return self.game.ball_moved_since_set
    
    @property
    def gc_phase(self) -> int:
        return self.game.game_phase

    @property
    def is_stopped(self) -> bool:
        return self.game.stopped

    @property
    def set_play(self) -> int:
        return self.game.set_play

    @property
    def kicking_team(self) -> int | None:
        return self.game.kicking_team

    @property
    def secs_remaining(self) -> int | None:
        return self.game.secs_remaining

    @property
    def secondary_time(self) -> int | None:
        return self.game.secondary_time

    def role_ball_xy_for_decide(
        self,
        *,
        now_sec: float,
        vision_timeout_sec: float,
        ball_xy: tuple[float, float] | None = None,
    ) -> tuple[float, float] | None:
        """Ball position for role scoring: override, else vision, else fused/ball."""
        if ball_xy is not None:
            return ball_xy
        if self.has_fresh_vision_global(now_sec, vision_timeout_sec):
            return self.vision_ball.global_xy()
        if self.has_trusted_fused_ball():
            return self.fused_ball.global_xy()
        return None

    def decide_role(
        self,
        *,
        my_player_id: int,
        current_role: str,
        margin_m: float,
        now_sec: float,
        peer_timeout_sec: float,
        keep_margin_m: float | None = None,
        w_lane_m_per_rad: float = 0.4,
        w_body_m_per_rad: float = 0.15,
        attack_target: tuple[float, float] | None = None,
        ball_xy: tuple[float, float] | None = None,
        vision_timeout_sec: float = 1.2,
    ) -> str:
        """Elect chase vs assist via attack_score (lower is better).

        attack_score = d_ball + w_lane * lane_err + w_body * body_err

        Ball for scoring: ``ball_xy`` if passed; else fresh in-bounds vision;
        else fused/ball. ``_refresh_role`` passes vision or fused-tracker horizon.

        - lane_err: robot→ball vs ball→attack target (goal-side of ball wins).
        - body_err: |yaw − bearing(robot→ball)|.

        Hysteresis (incumbent chaser only):
        - yield if any peer score < my_score - margin_m.
        - keep if my_score <= best_score + keep_margin_m.

        Tie-break: lower score wins; equal score → higher player_number chases.
        Stale peers (no fresh comms within peer_timeout_sec) are ignored.
        """
        # FIXME: add dynamic goalie role decision as well
        if self.game.player_id == 1:
            return "goalie"
        if self.self_pose is None:
            return current_role

        if self.game.kicking_team is not None and self.game.kicking_team != self.game.team_number:
            # During opponent set plays, don't chase the ball if we're not kicking, to avoid interfering with our defence. Instead, assist by default.
            return "assist"

        resolved = self.role_ball_xy_for_decide(
            now_sec=now_sec,
            vision_timeout_sec=vision_timeout_sec,
            ball_xy=ball_xy,
        )
        if resolved is None:
            return current_role
        bx, by = resolved
        if keep_margin_m is None:
            keep_margin_m = margin_m / 2.0
        tx, ty = attack_target if attack_target is not None else (ATTACK_GOAL_X, ATTACK_GOAL_Y)

        # Penalty is authoritative on the GC packet (my_team_info), not on the
        # comms-peer record. Look it up directly per-pid so we don't have to
        # mirror state onto RobotPeerFromComms.
        my_team_info = self.game.my_team_info
        players = getattr(my_team_info, "players", None) if my_team_info is not None else None

        def _peer_is_penalised(pid: int) -> bool:
            if not players:
                return False
            idx = pid - 1
            if not (0 <= idx < len(players)):
                return False
            pen = getattr(players[idx], "penalty", None)
            return pen is not None and pen != 0

        scores: dict[int, float] = {
            my_player_id: attack_score(
                self.robot_x,
                self.robot_y,
                bx,
                by,
                self.robot_yaw,
                w_lane_m_per_rad=w_lane_m_per_rad,
                w_body_m_per_rad=w_body_m_per_rad,
                tx=tx,
                ty=ty,
            ),
        }

        if current_role == "chase":
            # incumbent chaser gets a small score discount to reduce unnecessary switching
            scores[my_player_id] *= 0.80
            
        for pid, peer in self.robot_peers_from_comms.items():
            if pid == my_player_id or peer.pose is None:
                continue
            if (now_sec - peer.last_seen_sec) > peer_timeout_sec:
                continue
            if _peer_is_penalised(pid):
                continue
            scores[pid] = attack_score(
                peer.pose.x,
                peer.pose.y,
                bx,
                by,
                peer.pose.theta,
                w_lane_m_per_rad=w_lane_m_per_rad,
                w_body_m_per_rad=w_body_m_per_rad,
                tx=tx,
                ty=ty,
            )
            if peer.going_for_ball and pid > my_player_id:
                scores[pid] *= 0.80  # tie-break in favour of higher player_id chasing
                # return "assist"  # if a peer claims chase and has higher player_id, yield to them

        candidates = sorted(scores.items(), key=lambda c: (c[1], -c[0]))
        best_score, best_pid = candidates[0][1], candidates[0][0]
        my_score = scores[my_player_id]

        if best_pid == my_player_id:
            return "chase"

        if current_role == "chase":
            for pid, peer_score in scores.items():
                if pid != my_player_id and peer_score < my_score - margin_m:
                    return "assist"
            if my_score <= best_score + keep_margin_m:
                return "chase"
            return "assist"

        return "assist"


def _pose_to_dict(pose: Pose2 | None) -> dict | None:
    if pose is None:
        return None
    return {"x": pose.x, "y": pose.y, "theta": pose.theta}


def _head_to_dict(head: HeadModel) -> dict:
    return {"pitch": head.pitch, "yaw": head.yaw}


def _camera_ground_fov_to_dict(fov: CameraGroundFovModel) -> dict:
    return {
        "local_corners": [list(corner) for corner in fov.local_corners],
        "global_corners": [list(corner) for corner in fov.global_corners],
        "adjusted_pixels": [list(pixel) for pixel in fov.adjusted_pixels],
        "valid": fov.valid,
        "last_seen_sec": fov.last_seen_sec,
    }


def _ball_to_dict(ball: BallModel) -> dict:
    return {
        "local_x": ball.local_x,
        "local_y": ball.local_y,
        "global_x": ball.global_x,
        "global_y": ball.global_y,
        "global_vx": ball.global_vx,
        "global_vy": ball.global_vy,
        "pixel_x": ball.pixel_x,
        "pixel_y": ball.pixel_y,
        "source": ball.source,
        "confidence": ball.confidence,
        "last_seen_sec": ball.last_seen_sec,
    }


def _game_to_dict(game: GameModel) -> dict:
    return {
        "state": game.state,
        "stopped": game.stopped,
        "set_play": game.set_play,
        "game_phase": game.game_phase,
        "kicking_team": game.kicking_team,
        "secs_remaining": game.secs_remaining,
        "secondary_time": game.secondary_time,
        "team_number": game.team_number,
        "player_id": game.player_id,
        "role_id": game.role_id,
        "gc_listening": game.gc_listening,
        "my_penalty": game.my_penalty,
        "secs_till_unpenalised": game.secs_till_unpenalised,
        "ball_moved_since_set": game.ball_moved_since_set,
    }


def _robot_observation_to_dict(robot: RobotObservation) -> dict:
    return {
        "player_id": robot.player_id,
        "role_id": robot.role_id,
        "pose": _pose_to_dict(robot.pose),
        "team_affinity": robot.team_affinity,
        "confidence": robot.confidence,
        "source": robot.source,
        "last_seen_sec": robot.last_seen_sec,
        "label": robot.label,
        "vision_miss_ticks": robot.vision_miss_ticks,
    }


def _peer_to_dict(peer: RobotPeerFromComms) -> dict:
    return {
        "player_id": peer.player_id,
        "pose": _pose_to_dict(peer.pose),
        "ball_global": _ball_to_dict(peer.ball_global),
        "going_for_ball": peer.going_for_ball,
        "last_seen_sec": peer.last_seen_sec,
    }


def world_model_to_dict(
    wm: WorldModel,
    *,
    now_sec: float | None = None,
    vision_ball_timeout_sec: float = 1.2,
) -> dict:
    """JSON-serializable view of a world model (ROS team blobs omitted)."""
    has_fresh_vision = (
        wm.has_fresh_vision_ball(now_sec, vision_ball_timeout_sec)
        if now_sec is not None
        else None
    )
    return {
        "self_pose": _pose_to_dict(wm.self_pose),
        "head": _head_to_dict(wm.head),
        "ball": _ball_to_dict(wm.fused_ball),
        "fused_ball": _ball_to_dict(wm.fused_ball),
        "vision_ball": _ball_to_dict(wm.vision_ball),
        "camera_ground_fov": _camera_ground_fov_to_dict(wm.camera_ground_fov),
        "game": _game_to_dict(wm.game),
        "robots": [_robot_observation_to_dict(r) for r in wm.robots],
        "robot_peers_from_comms": {
            str(pid): _peer_to_dict(peer)
            for pid, peer in wm.robot_peers_from_comms.items()
        },
        "has_fresh_vision_ball": has_fresh_vision,
        "has_vision_ball": has_fresh_vision,
        "fall_down_state": int(wm.fall_down_state),
        "is_recovery_available": wm.is_recovery_available,
    }


def world_model_to_json(wm: WorldModel) -> str:
    return json.dumps(world_model_to_dict(wm), separators=(",", ":"))


FUTURE_HORIZONS_SEC = (1, 2, 3, 20, 40)


@dataclass
class WorldStateSnapshot:
    """Consistent read-only view for one state-machine tick."""

    wm: WorldModel
    role: str
    vision_ball_timeout_sec: float
    timestamp_sec: float
    ball_tracker: BallTracker = field(default_factory=BallTracker)
    local_ball_tracker: BallTracker = field(default_factory=BallTracker)
    seq: int | None = None

    @property
    def me(self) -> HeadModel:
        return self.wm.head

    def now_sec(self) -> float:
        return self.timestamp_sec

    @property
    def ball_tracker_valid(self) -> bool:
        return self.ball_tracker.valid

    def ball_global_at(self, dt: float = 0.0) -> tuple[float, float]:
        """Filtered global ball position at snapshot time + dt seconds."""
        return self.ball_tracker.position_at(dt)

    def ball_velocity_global(self) -> tuple[float, float]:
        """Filtered global ball velocity (m/s); zero until enough measurements."""
        return self.ball_tracker.velocity_at()

    @property
    def local_ball_tracker_valid(self) -> bool:
        return self.local_ball_tracker.valid

    def local_ball_global_at(self, dt: float = 0.0) -> tuple[float, float]:
        """Local (vision-only) filtered ball position at snapshot time + dt seconds."""
        return self.local_ball_tracker.position_at(dt)

    def local_ball_velocity_global(self) -> tuple[float, float]:
        """Local filtered global ball velocity (m/s)."""
        return self.local_ball_tracker.velocity_at()

    def fused_ball_age_sec(self) -> float:
        if self.ball_tracker.last_measurement_sec is None:
            return float("inf")
        return max(0.0, self.now_sec() - self.ball_tracker.last_measurement_sec)

    def has_fresh_fused_ball(self, max_age_sec: float) -> bool:
        """In-bounds filtered/coasted global estimate younger than max_age_sec."""
        if not self.ball_tracker_valid:
            return False
        if self.fused_ball_age_sec() > max_age_sec:
            return False
        px, py = self.ball_global_at(0.0)
        return self.wm.ball_allowed_at(px, py)

    def has_navigable_ball(self) -> bool:
        """Field-frame ball suitable for walking/kicking (tracker or wm fused/vision)."""
        return self.wm.has_global_ball(
            self.now_sec(),
            self.vision_ball_timeout_sec,
        )

    def to_dict(self) -> dict:
        fused_velocity = self.ball_velocity_global()
        local_velocity = self.local_ball_velocity_global()

        record = {
            "timestamp_sec": self.timestamp_sec,
            "role": self.role,
            "vision_ball_timeout_sec": self.vision_ball_timeout_sec,
            "wm": world_model_to_dict(
                self.wm,
                now_sec=self.timestamp_sec,
                vision_ball_timeout_sec=self.vision_ball_timeout_sec,
            ),
            "fused_ball_valid": self.ball_tracker_valid,
            "fused_ball_position_global": self.ball_global_at(0.0),
            "fused_ball_velocity_global": fused_velocity,
            "local_ball_valid": self.local_ball_tracker_valid,
            "local_ball_position_global": self.local_ball_global_at(0.0),
            "local_ball_velocity_global": local_velocity,
            "ball_velocity_global": fused_velocity,
        }
        for horizon in FUTURE_HORIZONS_SEC:
            fused_future = self.ball_global_at(horizon)
            local_future = self.local_ball_global_at(horizon)
            record[f"fused_future_ball{horizon}"] = fused_future
            record[f"local_future_ball{horizon}"] = local_future
            record[f"future_ball{horizon}"] = fused_future

        if self.seq is not None:
            record["seq"] = self.seq
        return record

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))

    @classmethod
    def from_world_model(
        cls,
        wm: WorldModel,
        *,
        role: str = "unknown",
        vision_ball_timeout_sec: float = 1.2,
        timestamp_sec: float | None = None,
    ) -> "WorldStateSnapshot":
        """Wrap a live world model for visualisation or logging."""
        ts = timestamp_sec if timestamp_sec is not None else (
            wm.ball.last_seen_sec or 0.0
        )
        return cls(
            wm=wm,
            role=role,
            vision_ball_timeout_sec=vision_ball_timeout_sec,
            timestamp_sec=ts,
        )


class WorldStateNode(Node):
    """ROS node that owns perception/game-state subscriptions."""

    def __init__(self, *, team_number: int = 18, player_id: int = 1, gc_listening: bool = True):
        super().__init__("world_state_node")

        self.wm = WorldModel()
        self.wm.game.team_number = team_number
        self.wm.game.player_id = player_id
        self.wm.game.role_id = player_id
        self.wm.gc_listening = gc_listening
        self.me = self.wm.head

        # Shared with ball_chasing: vision fuses here on every /booster_vision/detection
        # (see SimpleAvoidanceFilter docstring — head_yaw + ingest_detections each message).
        self._avoidance_lock = Lock()
        self.avoidance_filter = SimpleAvoidanceFilter(
            PFParams(
                k_rep=1.2, # 0.9
                influence_radius=0.7,
                v_max=1.0,
                deadzone_halfwidth_rad=33.0 * pi / 180.0,
                deadzone_max_range=1.0,
                deadzone_retreat_vx=0.5,
                hard_stop_distance=0.15,
                emergency_distance=0.25,
            ),
            vision_min_confidence=55.0,
            vision_obstacle_labels=("Person", "Opponent"),
            cam_horizontal_fov_deg=105.0,
            max_age_sec=1.5,
            merge_radius_m=0.3,
        )
        self.last_gc_packet_sec: float | None = None
        self.gc_timeout_sec = 5.0

        # Role decision (attack_score + score hysteresis + higher player_number tiebreak).
        self.current_role: str = "chase"
        self.role_margin_m: float = 0.08
        self.role_keep_margin_m: float = 0.04
        self.role_w_lane_m_per_rad: float = 0.4
        self.role_w_body_m_per_rad: float = 0.15
        self.role_ball_horizon_sec: float = 1.0
        self.peer_timeout_sec: float = 2.0

        self.confidence_min = 80
        self.vision_ball_timeout_sec = 1.2
        self.ball_coast_sec = 5.0
        self.set_play_ball_coast_sec = 8.0
        self.ball_tracker = BallTracker(max_coast_sec=self.ball_coast_sec)
        self.local_ball_tracker = BallTracker(max_coast_sec=self.ball_coast_sec)
        self._lock = RLock()
        self._cb_group = ReentrantCallbackGroup()

        self.create_subscription(
            Detections, "/booster_vision/detection",
            self.callback_detections, 1, callback_group=self._cb_group,
        )
        self.create_subscription(
            Pose2D, "/stateestimation/self_2d",
            self.callback_robot_pose, 1, callback_group=self._cb_group,
        )
        # best effort qos
        qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT, history=HistoryPolicy.KEEP_LAST);
        self.create_subscription(
            LowState, "/low_state",
            self.callback_low_state, qos, callback_group=self._cb_group,
        )
        self.create_subscription(
            FallDownState, "/fall_down",
            self.callback_falldown_state, 1, callback_group=self._cb_group,
        )
        self.create_subscription(
            GameState, "/gc/game_state",
            self.callback_game_state, 10, callback_group=self._cb_group,
        )

        self.create_subscription(RobotComms, "robot_comms/peers", self.callback_robot_comms, 1)

        #WhistleDetection
        self.create_subscription(
            WhistleDetection, "/whistle_detection",
            self.callback_whistle_detection, 1, callback_group=self._cb_group,
        )
        self.create_subscription(
            CameraGroundQuad, "/booster_vision/camera_ground_quad",
            self.callback_camera_ground_quad, 1, callback_group=self._cb_group,
        )

        self._camera_ground_fov_markers_pub = self.create_publisher(
            MarkerArray, "/camera_ground_fov/markers", 10,
        )

        self.get_logger().info("WorldStateNode initialized.")

    def now_sec(self) -> float:
        return self.get_clock().now().nanoseconds / 1e9

    def _refresh_role(self, now_sec: float) -> None:
        """Recompute the sticky role from current world model state.

        Caller must hold ``self._lock``. Safe to call when player_id is unset
        (we just keep the existing role).
        """
        my_player_id = self.wm.game.player_id
        if my_player_id is None:
            return
        wm = self.wm
        ball_xy = None
        if wm.has_fresh_vision_global(now_sec, self.vision_ball_timeout_sec):
            ball_xy = wm.vision_ball.global_xy()
        elif self.ball_tracker.valid:
            ball_xy = self.ball_tracker.position_at(self.role_ball_horizon_sec)
        self.current_role = wm.decide_role(
            my_player_id=int(my_player_id),
            current_role=self.current_role,
            margin_m=self.role_margin_m,
            now_sec=now_sec,
            peer_timeout_sec=self.peer_timeout_sec,
            keep_margin_m=self.role_keep_margin_m,
            w_lane_m_per_rad=self.role_w_lane_m_per_rad,
            w_body_m_per_rad=self.role_w_body_m_per_rad,
            ball_xy=ball_xy,
            vision_timeout_sec=self.vision_ball_timeout_sec,
        )

    def get_current_role(self) -> str:
        """Return role after recomputing from the latest world model."""
        with self._lock:
            self._refresh_role(self.now_sec())
            return self.current_role

    @staticmethod
    def _invalidate_ball_tracker_if_off_field(
        wm: WorldModel,
        tracker: BallTracker,
        now_sec: float,
    ) -> None:
        if not tracker.valid:
            return
        px, py = tracker.position_at(0.0)
        if wm.ball_allowed_at(px, py):
            return
        tracker.update(now_sec, None)

    def read_head_pose(self) -> tuple[float, float] | None:
        """Read current head joint angles without building a full snapshot."""
        with self._lock:
            if not self.wm.has_pose:
                return None
            return float(self.wm.head.pitch), float(self.wm.head.yaw)

    def snapshot(self) -> WorldStateSnapshot:
        with self._lock:
            now_sec = self.now_sec()
            wm = deepcopy(self.wm)

            # GC timeout / disabled fallback
            if self.wm.gc_listening:
                if (
                    self.last_gc_packet_sec is None or
                    now_sec - self.last_gc_packet_sec > self.gc_timeout_sec
                ):
                    wm.game.state = STATE_SET
            else:
                wm.game.state = STATE_SET
                wm.game.stopped = False

            coast_sec = (
                self.set_play_ball_coast_sec
                if wm.game.set_play != SET_PLAY_NONE
                else self.ball_coast_sec
            )
            self.local_ball_tracker.max_coast_sec = coast_sec
            self.ball_tracker.max_coast_sec = coast_sec

            vision_meas = wm.vision_measurement_for_tracker(
                now_sec=now_sec,
                vision_timeout_sec=self.vision_ball_timeout_sec,
            )
            self.local_ball_tracker.update(now_sec, vision_meas)

            my_player_id = wm.game.player_id or 0
            local_input, peer_inputs = wm.build_team_ball_inputs(
                now_sec=now_sec,
                my_player_id=int(my_player_id),
                local_tracker=self.local_ball_tracker,
                peer_timeout_sec=self.peer_timeout_sec,
                local_timeout_sec=self.ball_coast_sec,
            )
            team_estimate = fuse_team_ball(
                now_sec=now_sec,
                local=local_input,
                peers=peer_inputs,
                peer_timeout_sec=self.peer_timeout_sec,
                local_timeout_sec=coast_sec,
                inside_field=lambda x, y: wm.ball_allowed_by_field_bounds(
                    BallModel(global_x=x, global_y=y)
                ),
            )
            if not team_estimate.valid and self.local_ball_tracker.valid:
                meas_sec = self.local_ball_tracker.last_measurement_sec
                if meas_sec is not None and (now_sec - meas_sec) <= coast_sec:
                    px, py = self.local_ball_tracker.position_at(0.0)
                    if wm.ball_allowed_by_field_bounds(
                        BallModel(global_x=px, global_y=py)
                    ):
                        vx, vy = self.local_ball_tracker.velocity_at()
                        team_estimate = TeamBallEstimate(
                            valid=True,
                            position=np.array([px, py], dtype=float),
                            velocity=np.array([vx, vy], dtype=float),
                            last_seen_sec=meas_sec,
                            newer_than_local=False,
                        )

            fused_model = wm.fused_ball_model_from_estimate(team_estimate, now_sec=now_sec)
            wm.sync_ball_from_fused(fused_model)
            self.wm.sync_ball_from_fused(fused_model)

            if team_estimate.valid:
                self.ball_tracker.apply_fused_estimate(
                    position=team_estimate.position,
                    velocity=team_estimate.velocity,
                    estimate_time_sec=team_estimate.last_seen_sec or now_sec,
                    now_sec=now_sec,
                    valid=True,
                )
            else:
                self.ball_tracker.update(now_sec, None)

            self._invalidate_ball_tracker_if_off_field(wm, self.local_ball_tracker, now_sec)
            self._invalidate_ball_tracker_if_off_field(wm, self.ball_tracker, now_sec)
            if not self.ball_tracker.valid:
                empty_fused = BallModel(source="fused")
                wm.sync_ball_from_fused(empty_fused)
                self.wm.sync_ball_from_fused(empty_fused)

            self.wm.tick_ball_movement_since_set(now_sec)
            wm.tick_ball_movement_since_set(now_sec)

            self._refresh_role(now_sec)

            snapshot = WorldStateSnapshot(
                wm=wm,
                role=self.current_role,
                vision_ball_timeout_sec=self.vision_ball_timeout_sec,
                timestamp_sec=now_sec,
                ball_tracker=self.ball_tracker,
                local_ball_tracker=self.local_ball_tracker,
            )

            bigbrother.log_world_state(snapshot)

            return snapshot

    # ------------------------------------------------------------------
    #  ROS callbacks
    # ------------------------------------------------------------------

    def callback_low_state(self, msg: LowState):
        with self._lock:
            self.wm.update_head(
                pitch=msg.motor_state_serial[1].q,
                yaw=msg.motor_state_serial[0].q,
            )

    def callback_falldown_state(self, msg: FallDownState):
        with self._lock:
            self.wm.update_falldown_state(
                fall_down_state=msg.fall_down_state,
                is_recovery_available=msg.is_recovery_available,
            )

    def callback_robot_pose(self, msg: Pose2D):
        with self._lock:
            self.wm.update_self_pose(x=msg.x, y=msg.y, theta=msg.theta)

    def callback_game_state(self, msg: GameState):

        if self.wm.gc_listening == False:
            return

        kicking_team = getattr(msg, "kicking_team", None)
        if kicking_team == 255:
            kicking_team = None

        my_team_number = self.wm.game.team_number
        my_player_id = self.wm.game.player_id

        my_team_info = None
        opponent_team_info = None
        my_penalty = self.wm.game.my_penalty
        secs_till_unpenalised = self.wm.game.secs_till_unpenalised

        for team in msg.teams:
            if team.team_number == my_team_number:
                my_team_info = team
            else:
                opponent_team_info = team

        if my_team_info is not None and my_player_id is not None:
            idx = my_player_id - 1
            if 0 <= idx < len(my_team_info.players):
                my_penalty = my_team_info.players[idx].penalty
                secs_till_unpenalised = my_team_info.players[idx].secs_till_unpenalised

        self.last_gc_packet_sec = self.now_sec()

        whistle_heard = self.wm.game.whistle_heard
        nubots_whistle_heard = self.wm.game.nubots_whistle_heard
        entering_set = msg.state == STATE_SET and self.wm.game.state != STATE_SET
        entering_play = msg.state == STATE_PLAYING and self.wm.game.state == STATE_SET
        if entering_set:
            whistle_heard = False
            nubots_whistle_heard = False

        with self._lock:
            if entering_play:
                # if the ball is within center circle, we can set the position
                ball_xy = (
                    self.wm.fused_ball.global_xy()
                    if self.wm.has_trusted_fused_ball() and self.wm.position_within_circle(self.wm.fused_ball.global_x, self.wm.fused_ball.global_y, -0.40)
                    else None
                )
                self.wm.reset_ball_movement_since_set(ball_xy)
            self.wm.update_game(
                state=msg.state,
                stopped=getattr(msg, "stopped", True), # if there's no stopped in the msg we gotta stop playing bro
                set_play=getattr(msg, "set_play", SET_PLAY_NONE),
                game_phase=getattr(msg, "game_phase", GAME_PHASE_NORMAL),
                kicking_team=kicking_team,
                secs_remaining=getattr(msg, "secs_remaining", None),
                secondary_time=getattr(msg, "secondary_time", None),
                team_number=my_team_number,
                player_id=my_player_id,
                role_id=self.wm.game.role_id,
                my_team_info=my_team_info,
                opponent_team_info=opponent_team_info,
                my_penalty=my_penalty,
                secs_till_unpenalised=secs_till_unpenalised,
                whistle_heard=whistle_heard,
                nubots_whistle_heard=nubots_whistle_heard,
            )

    def _publish_camera_ground_fov_markers(
        self,
        global_corners: list[tuple[float, float]],
        stamp,
    ) -> None:
        marker_array = MarkerArray()
        delete_marker = Marker()
        delete_marker.header.frame_id = "world"
        delete_marker.header.stamp = stamp
        delete_marker.action = Marker.DELETEALL
        marker_array.markers.append(delete_marker)

        if len(global_corners) < 4:
            self._camera_ground_fov_markers_pub.publish(marker_array)
            return

        outline = Marker()
        outline.header.frame_id = "world"
        outline.header.stamp = stamp
        outline.ns = "camera_ground_fov"
        outline.id = 0
        outline.type = Marker.LINE_STRIP
        outline.action = Marker.ADD
        outline.pose.orientation.w = 1.0
        outline.scale.x = 0.05
        outline.color.r = 0.2
        outline.color.g = 0.8
        outline.color.b = 1.0
        outline.color.a = 1.0
        for corner in global_corners:
            outline.points.append(Point(x=float(corner[0]), y=float(corner[1]), z=0.0))
        outline.points.append(
            Point(x=float(global_corners[0][0]), y=float(global_corners[0][1]), z=0.0)
        )
        marker_array.markers.append(outline)

        for idx, corner in enumerate(global_corners, start=1):
            sphere = Marker()
            sphere.header.frame_id = "world"
            sphere.header.stamp = stamp
            sphere.ns = "camera_ground_fov"
            sphere.id = idx
            sphere.type = Marker.SPHERE
            sphere.action = Marker.ADD
            sphere.pose.position.x = float(corner[0])
            sphere.pose.position.y = float(corner[1])
            sphere.pose.position.z = 0.0
            sphere.pose.orientation.w = 1.0
            sphere.scale.x = 0.12
            sphere.scale.y = 0.12
            sphere.scale.z = 0.12
            sphere.color.r = 0.2
            sphere.color.g = 0.8
            sphere.color.b = 1.0
            sphere.color.a = 1.0
            marker_array.markers.append(sphere)

        self._camera_ground_fov_markers_pub.publish(marker_array)

    def callback_camera_ground_quad(self, msg: CameraGroundQuad) -> None:
        now_sec = self.now_sec()
        local_corners: list[tuple[float, float]] = []
        adjusted_pixels: list[tuple[float, float]] = []
        global_corners: list[tuple[float, float]] = []

        if len(msg.local_corners) >= 8:
            local_corners = [
                (float(msg.local_corners[i]), float(msg.local_corners[i + 1]))
                for i in range(0, 8, 2)
            ]
        if len(msg.adjusted_pixels) >= 8:
            adjusted_pixels = [
                (float(msg.adjusted_pixels[i]), float(msg.adjusted_pixels[i + 1]))
                for i in range(0, 8, 2)
            ]

        valid = bool(msg.valid) and len(local_corners) == 4
        if valid and self.wm.has_pose:
            global_corners = [
                robot_local_to_global(
                    lx, ly, self.wm.robot_x, self.wm.robot_y, self.wm.robot_yaw,
                )
                for lx, ly in local_corners
            ]
        else:
            valid = False

        with self._lock:
            self.wm.update_camera_ground_fov(
                local_corners=local_corners,
                global_corners=global_corners,
                adjusted_pixels=adjusted_pixels,
                valid=valid,
                now_sec=now_sec,
            )

        bigbrother.log_ground_fov_markers(global_corners if valid else [])

        self._publish_camera_ground_fov_markers(
            global_corners if valid else [],
            msg.header.stamp,
        )

    def callback_detections(self, msg: Detections):
        now_sec = self.get_clock().now().nanoseconds / 1e9
        with self._avoidance_lock:
            self.avoidance_filter.head_yaw = self.wm.head.yaw
            self.avoidance_filter.ingest_detections(msg, now_sec)

            now_sec = self.now_sec()
            vision_robots = []
            ball_updated = False
            
            field_features = []
            for obj in msg.detected_objects:
                if obj.label in ("Robot", "robot", "Person", "Opponent") and len(obj.position_projection) >= 2:
                    rel_x = obj.position_projection[0]
                    rel_y = obj.position_projection[1]
                    global_x = self.wm.robot_x + cos(self.wm.robot_yaw) * rel_x - sin(self.wm.robot_yaw) * rel_y
                    global_y = self.wm.robot_y + sin(self.wm.robot_yaw) * rel_x + cos(self.wm.robot_yaw) * rel_y
                    team_affinity = -0.7 if obj.label == "Opponent" else 0.0
                    vision_robots.append(
                        RobotObservation(
                            pose=Pose2(x=global_x, y=global_y, theta=0.0),
                            team_affinity=_vision_team_affinity(obj.label),
                            confidence=obj.confidence,
                            source="vision",
                            last_seen_sec=now_sec,
                            label=obj.label,
                        )
                    )

                if not ball_updated and obj.label == "Ball" and obj.confidence > self.confidence_min and len(obj.position_projection) >= 2:
                    rel_x = obj.position_projection[0]
                    rel_y = obj.position_projection[1]
                    global_x: float | None = None
                    global_y: float | None = None
                    if self.wm.has_pose:
                        global_x = (
                            self.wm.robot_x
                            + cos(self.wm.robot_yaw) * rel_x
                            - sin(self.wm.robot_yaw) * rel_y
                        )
                        global_y = (
                            self.wm.robot_y
                            + sin(self.wm.robot_yaw) * rel_x
                            + cos(self.wm.robot_yaw) * rel_y
                        )
                    bigbrother.log_ball_vision(global_x=global_x, global_y=global_y, confidence=obj.confidence)

                    self.wm.update_ball_from_vision(
                        local_x=rel_x,
                        local_y=rel_y,
                        global_x=global_x,
                        global_y=global_y,
                        pixel_x=(obj.xmax + obj.xmin) / 2,
                        pixel_y=(obj.ymax + obj.ymin) / 2,
                        confidence=obj.confidence,
                        now_sec=now_sec,
                    )
                    ball_updated = True
                
                if obj.label not in ("Robot", "robot", "Person", "Opponent", "ball", "Ball"):
                    # probably a field feature, log with bigbrother
                    field_features.append((obj.position_projection[0], obj.position_projection[1], obj.label))

        if self.wm.has_pose:
            robot_pose = (self.wm.robot_x, self.wm.robot_y, self.wm.robot_yaw) # as a 3d pose tuple (x, y, theta)
            bigbrother.log_field_features(robot_pose=robot_pose, field_features_relative_to_robot=field_features)
        self.wm.replace_vision_robots(vision_robots, now_sec)
        if ball_updated:
            with self._lock:
                self._refresh_role(now_sec)

    def callback_robot_comms(self, msg: RobotComms):
        with self._lock:
            now_sec = self.now_sec()
            player_id = msg.player_number

            ball_valid = bool(getattr(msg, "ball_valid", False))
            if not ball_valid:
                peer_has_ball = not (
                    abs(msg.global_ball_x) < 1e-6 and
                    abs(msg.global_ball_y) < 1e-6
                )
                ball_valid = peer_has_ball

            if ball_valid:
                peer_ball = BallModel(
                    global_x=msg.global_ball_x,
                    global_y=msg.global_ball_y,
                    global_vx=float(getattr(msg, "global_ball_vx", 0.0)),
                    global_vy=float(getattr(msg, "global_ball_vy", 0.0)),
                    source="comms_peer",
                    confidence=80.0,
                    last_seen_sec=now_sec,
                )
            else:
                peer_ball = BallModel(source="comms_peer")

            self.wm.robot_peers_from_comms[player_id] = RobotPeerFromComms(
                player_id=player_id,
                pose=Pose2(x=msg.pos_x, y=msg.pos_y, theta=msg.heading),
                ball_global=peer_ball,
                going_for_ball=msg.going_for_ball,
                last_seen_sec=now_sec,
                ball_valid=ball_valid,
            )

            if self.wm.game.state == STATE_SET and msg.going_for_ball == True and player_id == 2: # Peter Pham change this if you want different player numbers
                self.wm.game.nubots_whistle_heard = True
    
    def callback_whistle_detection(self, msg: WhistleDetection):
        with self._lock:
            now_sec = self.now_sec()
            #Check the whistle detection type and update the game state accordingly
            #But before that, check if detection's confidence is above 0.9
            if msg.confidence >= 0.9:
                if msg.whistle_type == 1:
                    self.wm.game.whistle_heard = True
                    self.wm.game.whistle_type = 1

                # elif msg.whistle_type == 2:
                #     self.wm.game.whistle_type = 2
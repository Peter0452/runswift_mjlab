#!/usr/bin/env python3
"""
World-model based ball-chasing state machine (tracker-drive entry point).

Dedicated runner using SE2 global planning + PathTracker local control.
For cf-MPC navigation, use ball_chasing_wm_simplified.py --use-cf-mpc.

Keeps the full game state machine and ROS/world-model wiring from the
simplified variant, with navigation always on via path tracker.
"""
from __future__ import annotations

import json
import sys
import threading
import time
from collections import deque
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from math import atan2, cos, pi, sin, sqrt
from typing import Sequence
import argparse
import random
import numpy as np
import pyttsx3
import rclpy
from action.arbiter import ActionArbiter
from action.booster_adapter import BoosterAdapter, create_booster_adapter
from action.config import ALWAYS_SOCCER
from action.head_controller import HeadController
from action.types import ArbiterInput, HeadLimits, MotionCommand, VelocityLimits
from skills.base import Point2, Pose2
from skills.kick import Kick, KickRequest
from skills.obstacle_avoid import avoid_opponents
from skills.walk_to_pose import WalkToPose, WalkToPoseRequest, walk_to_pose_velocity
from std_msgs.msg import Bool, Float32MultiArray, String
from deploy_interface.action import Kick as KickAction
from geometry_msgs.msg import PoseStamped
from rclpy.action import ActionClient
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

import bigbrother

from pathlib import Path

import yaml
from ament_index_python.packages import get_package_share_directory
from communication_interface.msg import RobotComms

from skills.navigate_to_pose import (
    NavigateToPose,
    NavigateToPoseRequest,
    navigation_imports,
)

try:
    navigation_imports()
    _NAV_AVAILABLE = True
except ImportError:
    _NAV_AVAILABLE = False





from blocking import calculate_blocking_pose
from clear_target_provider import (
    ClearTarget,
    ClearTargetInput,
    ClearTargetState,
    calc_best_clear,
    clear_aim_unit,
)
from simple_clear_target import pick_clear_direction

from legacy_world_model import (
    STATE_FINISHED,
    STATE_INITIAL,
    STATE_PLAYING,
    STATE_READY,
    STATE_SET,
    FIELD_LENGTH_M,
    FIELD_WIDTH_M,
    GOAL_WIDTH_M,
    GOAL_LENGTH_M,
    PENALTY_LENGTH_M,
    PENALTY_WIDTH_M,
    FORMATION_FIELD_DIMENSIONS,
    RobotObservation,
    WorldStateNode,
    WorldStateSnapshot,
    GAME_PHASE_NORMAL,
    GAME_PHASE_PENALTY_SHOOT_OUT,
    GAME_PHASE_EXTRA_TIME,
    GAME_PHASE_TIMEOUT,
    SET_PLAY_NONE,
    SET_PLAY_DIRECT_FREE_KICK,
    SET_PLAY_INDIRECT_FREE_KICK,
    SET_PLAY_PENALTY_KICK,
    SET_PLAY_THROW_IN,
    SET_PLAY_GOAL_KICK,
    SET_PLAY_CORNER_KICK,
)

GOAL_X = FIELD_LENGTH_M / 2.0
GOALIE_GOAL_X = -FIELD_LENGTH_M / 2.0
GOAL_Y = 0.0
GOALIE_LINE = GOALIE_GOAL_X + GOAL_LENGTH_M
PENALTY_HALF_WIDTH = PENALTY_WIDTH_M / 2.0
CLEAR_DIST_THRESHOLD = 2.0  # legacy; goalie clear uses goalie_should_clear()
GOALIE_PENALTY_APPROACH_ENTER_M = 1.0  # ball x inside this (beyond box) → track/clear
GOALIE_PENALTY_APPROACH_EXIT_M = 1.2  # hysteresis: leave track when ball is farther out
GOALIE_BALL_TOWARD_GOAL_VX = -0.12  # m/s field-x; ball rolling toward own goal
GOALIE_BLOCKING_DIST_TOL = 0.0
GOALIE_BLOCKING_THETA_TOL = 0.15
# keep the walk engine in gait when blocking: sway laterally at a tiny speed,
# flipping direction once this far off-centre so the oscillation stays centred
# on the target pose
GOALIE_BLOCKING_IDLE_SWAY_SPEED = 0.06
GOALIE_BLOCKING_IDLE_SWAY_AMPLITUDE_M = 0.04
GOALIE_SIDELINE_CLEAR_KICK_POWER = 2.0
SIDELINE_CLEAR_GOAL_OFFSET_M = 3.0  # virtual aim point along touchline for kick msg
SIDELINE_CLEAR_STANDOFF_M = 0.4  # robot standoff behind ball (toward own goal side)
# False: BLOCKING → DRIBBLE_CLEAR (simple_clear_target, direction only).
# True:  BLOCKING → GO (clear_target_provider, landing + kick power).
GOALIE_CLEAR_USE_GO_STATE = False
# TESTING: True -> BLOCKING → KICK directly, spamming the RL kick toward the enemy goal
# (ignores DRIBBLE_CLEAR / GO clear paths).
GOALIE_CLEAR_USE_RL_KICK = False

CAM_PIX_X = 544.0
CAM_PIX_Y = 448.0
CAM_ANGLE_X = 1.211259
CAM_ANGLE_Y = 0.733038
CENTER_PX_TOLERANCE = CAM_PIX_X * 0.14
CENTER_PY_TOLERANCE = CAM_PIX_Y * 0.14
FIELD_MARGIN = 0.5
SEARCH_STALE_BEARING_TOL = 0.08
SEARCH_PRELIM_SCAN_CYCLES = 1
SEARCH_SPIN_VTHETA = 1.2
SEARCH_BOUNDARY_MARGIN_M = 0.5
SEARCH_WING_ANGLE_RAD = 80.0 * pi / 180.0
SEARCH_WING_LOOKAHEAD_M = 2.0
HALF_LENGTH_M = FIELD_LENGTH_M / 2.0
HALF_WIDTH_M = FIELD_WIDTH_M / 2.0
SEARCH_QUADRANT_CENTERS = (
    (HALF_LENGTH_M / 2.0, HALF_WIDTH_M / 2.0),
    (HALF_LENGTH_M / 2.0, -HALF_WIDTH_M / 2.0),
    (-HALF_LENGTH_M / 2.0, -HALF_WIDTH_M / 2.0),
    (-HALF_LENGTH_M / 2.0, HALF_WIDTH_M / 2.0),
)
HEAD_TRACK_SPEED_MIN = 0.45   # rad/s — speed when ball is near centre
HEAD_TRACK_SPEED_MAX = 5.75   # rad/s — speed when ball is at frame edge
HEAD_PITCH_MIN = 0.46
HEAD_PITCH_MAX = 0.74
HEAD_YAW_MIN = -1.02
HEAD_YAW_MAX = 1.02
HEAD_PITCH_NEAR_BALL_M = 1.0
HEAD_PITCH_NEAR = 0.74
HEAD_CONTROL_HZ_DEFAULT = 50.0
HEAD_CONTROL_MAX_DT_SEC = 0.05
GO_HEAD_HOLD_DIST_M = 0.75
BALL_LOST_CONFIRM_TICKS = 5
DEBUG = False
KICK_MODE = "booster_kick"  # "static_kick" or "booster_kick"
VELOCITY_DIAG_FILTER_ALPHA = 0.25
VELOCITY_DIAG_MIN_DT_SEC = 1e-3
VELOCITY_DIAG_MAX_DT_SEC = 0.5
VELOCITY_DIAG_CMD_SIGN_EPS = 0.05

# hardcoded goal mouth area for kick target selection - (should be coupled with vision to increase robustness)
GOAL_WIDTH_M = 1.5 #2.4
GOAL_HALF_WIDTH_M = GOAL_WIDTH_M / 2.0
GOAL_MOUTH_Y_MIN = GOAL_Y - GOAL_HALF_WIDTH_M
GOAL_MOUTH_Y_MAX = GOAL_Y + GOAL_HALF_WIDTH_M
GOAL_MOUTH_SAMPLES = 22

# Opponent-aware kick target (world-frame lateral offset at goal line; dir from target).
KICK_OPPONENT_MAX_AGE_SEC = 1.5
KICK_OPPONENT_FRONT_MIN_X_M = 0.25
KICK_OPPONENT_CORRIDOR_M = 1.0
KICK_OPPONENT_MAX_RANGE_M = 3.5
KICK_OPPONENT_BALL_RADIUS_M = 1.8
# Penalise kick targets that need a large body turn from current heading (faster when |dir| is small).
KICK_EXECUTION_ANGLE_WEIGHT = 5.0
KICK_TARGET_LOCK_SEC = 7.7
KICK_TARGET_SWITCH_MARGIN = 0.9
KICK_TARGET_SAME_POINT_M = 0.10
KICK_TARGET_CHANGE_PENALTY = 0.25
KICK_THREAT_PERSIST_SEC = 0.12
KICK_THREAT_HOLD_SEC = 0.35
KICK_POWER_FAR = 5.5
KICK_POWER_MID = 4.0
KICK_POWER_NEAR = 2.5
GO_KICK_CONFIRM_TICKS = 0
DRIBBLE_KICK_CONFIRM_TICKS = 2
GO_KICK_EXIT_DIST_TOL = 0.55
GO_KICK_EXIT_THETA_TOL = 0.95
DRIBBLE_KICK_ENTER_DIST = 0.50
DRIBBLE_KICK_EXIT_DIST = 0.70



_CONFIG_SHARE = Path(get_package_share_directory("runswift_config"))
_path_yaml = _CONFIG_SHARE / "path.yaml"
if not _path_yaml.is_file():
    raise FileNotFoundError(
        f"runswift_config path.yaml not found at {_path_yaml}. "
        "Rebuild runswift_config and source install/setup.bash."
    )
with _path_yaml.open(encoding="utf-8") as _path_file:
    _path_cfg = yaml.safe_load(_path_file)
_repo_root_raw = _path_cfg.get("path_to_repo_root") if isinstance(_path_cfg, dict) else None
if not _repo_root_raw:
    raise ValueError(
        f"path.yaml at {_path_yaml} must define path_to_repo_root (got {_path_cfg!r})."
    )
REPO_ROOT = Path(_repo_root_raw).resolve()
if not REPO_ROOT.is_dir():
    raise FileNotFoundError(
        f"path_to_repo_root does not exist: {REPO_ROOT} (from {_path_yaml})."
    )

FORMATION_ROOT = REPO_ROOT / "utils" / "formation"
FORMATION_BACKEND_ROOT = FORMATION_ROOT / "backend"

if str(FORMATION_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(FORMATION_BACKEND_ROOT))

UTILS_ROOT = REPO_ROOT / "utils"
if str(UTILS_ROOT) not in sys.path:
    sys.path.insert(0, str(UTILS_ROOT))

try:
    from app.compute import compute_positions, resolve_formation_mode
except Exception:
    compute_positions = None
    resolve_formation_mode = None

FORMATION_JSON_PATH = FORMATION_ROOT / "examples" / "scaling_play_3_players_complete.json"
FORMATION_ACTIVE_PLAYERS = 3

GC_PHASE_TO_FORMATION_STR = {
    GAME_PHASE_NORMAL: "normal",
    GAME_PHASE_PENALTY_SHOOT_OUT: "penalty_shoot_out",
    GAME_PHASE_EXTRA_TIME: "extra_time",
    GAME_PHASE_TIMEOUT: "timeout",
}

GC_STATE_TO_FORMATION_STR = {
    STATE_INITIAL: "initial",
    STATE_READY: "ready",
    STATE_SET: "set",
    STATE_PLAYING: "playing",
    STATE_FINISHED: "finished",
}

GC_SET_PLAY_TO_FORMATION_STR = {
    SET_PLAY_NONE: "none",
    SET_PLAY_DIRECT_FREE_KICK: "direct_free_kick",
    SET_PLAY_INDIRECT_FREE_KICK: "indirect_free_kick",
    SET_PLAY_PENALTY_KICK: "penalty_kick",
    SET_PLAY_THROW_IN: "throw_in",
    SET_PLAY_GOAL_KICK: "goal_kick",
    SET_PLAY_CORNER_KICK: "corner_kick",
}


class StateID(Enum):
    STAND = auto()
    SET = auto()
    MOVE_TO_READY = auto()
    PRE_ENTER_FIELD = auto()
    WALK_TO_POINT = auto()
    LOOK_FOR_BALL = auto()
    ASSIST = auto()
    BLOCKING = auto()
    GO = auto()
    DRIBBLE = auto()
    DRIBBLE_CLEAR = auto()
    KICK = auto()
    WALK_TO_BALL_KICK = auto()

class State(ABC):
    """Base class for every chaser state."""

    id: StateID

    def __init__(self, ctx: "BallChaseStateMachineNode"):
        self.ctx = ctx

    def on_enter(self) -> None:
        self.ctx.get_logger().info(f"State -> {self.id.name}")
        # timer for state enter
        
        print(f"\033[91mEntering {self.id.name} state\033[0m")


    def on_exit(self) -> None:
        self.ctx.get_logger().info(f"{self.id.name} -> exit")

    @abstractmethod
    def execute(self) -> StateID | None:
        """Run one tick and optionally request a transition."""


class StateMachine:
    """Minimal deterministic state machine with enter/exit hooks."""

    def __init__(self, states: dict[StateID, State], initial: StateID):
        self._states = states
        self._current_id = initial
        self._current = states[initial]
        self._current.on_enter()

    @property
    def current_id(self) -> StateID:
        return self._current_id

    def tick(self) -> None:
        next_id = self._current.execute()
        depth = 0
        while next_id is not None and next_id != self._current_id and depth < 3:
            self._transition(next_id)
            next_id = self._current.execute()
            depth += 1

    def force_transition(self, target: StateID) -> None:
        if target != self._current_id:
            self._transition(target)

    def _transition(self, target: StateID) -> None:
        self._current.on_exit()
        self._current_id = target
        self._current = self._states[target]
        self._current.on_enter()

        bigbrother.log_sm_state(str(target))


@dataclass(frozen=True)
class RobotPose:
    player_number: int
    x: float
    y: float
    theta: float


def _search_wrap_angle_pi(angle: float) -> float:
    while angle > pi:
        angle -= 2.0 * pi
    while angle < -pi:
        angle += 2.0 * pi
    return angle


def _search_rotation_dir_shortest_turn(robot_yaw: float, target_yaw: float) -> float:
    err = _search_wrap_angle_pi(target_yaw - robot_yaw)
    if abs(err) < 1e-9:
        return -1.0
    return 1.0 if err > 0.0 else -1.0


def _search_rotation_dir_from_center_line(rx: float, ry: float, robot_yaw: float) -> float:
    if _search_near_field_boundary(rx, ry, SEARCH_BOUNDARY_MARGIN_M):
        qi = _search_quadrant_of(rx, ry)
        if qi in (0, 3):
            arc_lo, arc_hi, arc_mid = -pi, 0.0, -pi / 2.0
        else:
            arc_lo, arc_hi, arc_mid = 0.0, pi, pi / 2.0
        if arc_lo < robot_yaw < arc_hi:
            return _search_rotation_dir_shortest_turn(robot_yaw, arc_mid)
        return 1.0 if robot_yaw <= arc_lo else -1.0
    tcx, tcy = -rx, -ry
    if abs(tcx) < 1e-9 and abs(tcy) < 1e-9:
        return -1.0
    cross = cos(robot_yaw) * tcy - sin(robot_yaw) * tcx
    if abs(cross) < 1e-9:
        return -1.0
    return 1.0 if cross > 0.0 else -1.0


def _search_robot_outside_field(rx: float, ry: float) -> bool:
    return abs(rx) > HALF_LENGTH_M or abs(ry) > HALF_WIDTH_M


def _search_near_field_boundary(rx: float, ry: float, margin_m: float = 0.2) -> bool:
    if _search_robot_outside_field(rx, ry):
        return True
    return min(HALF_LENGTH_M - abs(rx), HALF_WIDTH_M - abs(ry)) <= margin_m


def _search_wing_rays_outside(
    rx: float,
    ry: float,
    robot_yaw: float,
    wing_angle_rad: float = SEARCH_WING_ANGLE_RAD,
    lookahead_m: float = SEARCH_WING_LOOKAHEAD_M,
) -> tuple[bool, bool]:
    left_yaw = robot_yaw + wing_angle_rad
    right_yaw = robot_yaw - wing_angle_rad
    left_out = _search_robot_outside_field(
        rx + cos(left_yaw) * lookahead_m,
        ry + sin(left_yaw) * lookahead_m,
    )
    right_out = _search_robot_outside_field(
        rx + cos(right_yaw) * lookahead_m,
        ry + sin(right_yaw) * lookahead_m,
    )
    return left_out, right_out


def _search_boundary_spin_dir(left_out: bool, right_out: bool) -> float | None:
    if left_out and not right_out:
        return -1.0
    if right_out and not left_out:
        return 1.0
    return None


def _search_yaw_aligned(robot_yaw: float, target_yaw: float, tol_rad: float) -> bool:
    return abs(_search_wrap_angle_pi(target_yaw - robot_yaw)) <= tol_rad


def _search_quadrant_of(x: float, y: float) -> int:
    if x >= 0.0 and y >= 0.0:
        return 0
    if x >= 0.0 and y < 0.0:
        return 1
    if x < 0.0 and y < 0.0:
        return 2
    return 3


def _search_quadrant_center(qi: int) -> tuple[float, float]:
    return SEARCH_QUADRANT_CENTERS[qi]


def _search_dist_xy(ax: float, ay: float, bx: float, by: float) -> float:
    return sqrt((ax - bx) ** 2 + (ay - by) ** 2)


def _search_robots_in_quadrant(poses: Sequence[RobotPose], qi: int) -> list[RobotPose]:
    return [p for p in poses if _search_quadrant_of(p.x, p.y) == qi]


def _search_closest_robot(
    target_xy: tuple[float, float],
    robots: Sequence[RobotPose],
) -> int | None:
    if not robots:
        return None
    tx, ty = target_xy
    best = min(
        robots,
        key=lambda r: (_search_dist_xy(r.x, r.y, tx, ty), -r.player_number),
    )
    return best.player_number


def _search_bearing_to_point(rx: float, ry: float, tx: float, ty: float) -> float:
    return atan2(ty - ry, tx - rx)


class LookForBallState(State):
    id = StateID.LOOK_FOR_BALL

    def on_enter(self) -> None:
        self.ctx.get_logger().info("State -> LOOK_FOR_BALL")
        print("\033[91mEntering LOOK_FOR_BALL state\033[0m")
        self.search_start = self.ctx.get_clock().now()
        self.scan_center_yaw = self.ctx.wm.robot_yaw
        if self.ctx.is_goalie:
            ball = self.ctx.wm.vision_ball
            self.scan_dir = 1.0 if ball.last_seen_sec and ball.local_y > 0.0 else -1.0
            return
        self._init_field_search()

    def on_exit(self) -> None:
        self.ctx.get_logger().info("LOOK_FOR_BALL -> exit")

    def execute(self) -> StateID | None:
        c = self.ctx
        if c.has_global_ball():
            if c.role_decision == "chase":
                return StateID.GO
            if c.is_goalie:
                return StateID.BLOCKING
            return StateID.ASSIST
        if c.is_goalie:
            if not c.robot_in_penalty():
                c.update_head_command(speed_yaw_scale=1.5)
                c.publish_debug_pose(GOALIE_LINE, 0.0, 0.0)
                c.walk_skill.tick(
                    WalkToPoseRequest(
                        robot_pose=c.robot_pose2(),
                        target_pose=Pose2(GOALIE_LINE, 0.0, 0.0),
                        distance_tolerance=GOALIE_BLOCKING_DIST_TOL,
                        theta_tolerance=GOALIE_BLOCKING_THETA_TOL,
                        obstacles=c.avoid_obstacle_points(),
                        apply_avoidance=True,
                    ),
                    c.command,
                )
                return None
            else:
                c.update_head_command(speed_yaw_scale=1.5)
                return self._goalie_fallback_spin()
        self._run_continuous_search()
        return None

    def _init_field_search(self) -> None:
        c = self.ctx
        rx, ry = c.wm.robot_x, c.wm.robot_y
        yaw = c.wm.robot_yaw
        stale = c.stale_ball_xy()
        poses = c.fresh_teammate_poses()
        my_q = _search_quadrant_of(rx, ry)

        self.started_as_stale_actor = False
        self.stale_target_yaw: float | None = None
        self.stale_bearing_reached = False
        self.prelim_scan_cycles = 0
        self.prelim_scan_cycle_start_index = 0
        self.prelim_scan_saw_advance = False

        if stale is not None and self._is_stale_ball_actor(my_q, poses, stale):
            self.started_as_stale_actor = True
            self.stale_target_yaw = _search_bearing_to_point(rx, ry, stale[0], stale[1])
            self.scan_dir = _search_rotation_dir_shortest_turn(yaw, self.stale_target_yaw)
            self.phase = "PRELIM"
            if _search_yaw_aligned(yaw, self.stale_target_yaw, SEARCH_STALE_BEARING_TOL):
                self.stale_bearing_reached = True
                self.prelim_scan_cycle_start_index = c.cmd_index
        else:
            self.scan_dir = _search_rotation_dir_from_center_line(rx, ry, yaw)
            self.phase = "EXPANDED"

        left_out, right_out = _search_wing_rays_outside(rx, ry, yaw)
        override = _search_boundary_spin_dir(left_out, right_out)
        if override is not None:
            self.scan_dir = override
        self.bias_facing_outside = (
            _search_near_field_boundary(rx, ry, SEARCH_BOUNDARY_MARGIN_M)
            and (left_out or right_out)
        )

    def _elapsed_search_sec(self) -> float:
        return (self.ctx.get_clock().now() - self.search_start).nanoseconds / 1e9

    def _is_stale_ball_actor(
        self,
        my_q: int,
        poses: list[RobotPose],
        stale: tuple[float, float],
    ) -> bool:
        ball_q = _search_quadrant_of(stale[0], stale[1])
        if ball_q == my_q:
            return True
        if _search_robots_in_quadrant(poses, ball_q):
            return False
        assignee_id = _search_closest_robot(_search_quadrant_center(ball_q), poses)
        return assignee_id == self.ctx.player_number

    def _maybe_advance_prelim(self) -> None:
        if self.phase != "PRELIM" or self.stale_target_yaw is None:
            return
        c = self.ctx
        yaw = c.wm.robot_yaw
        if not self.stale_bearing_reached:
            if _search_yaw_aligned(yaw, self.stale_target_yaw, SEARCH_STALE_BEARING_TOL):
                self.stale_bearing_reached = True
                self.prelim_scan_cycles = 0
                self.prelim_scan_cycle_start_index = c.cmd_index
                self.prelim_scan_saw_advance = False
            return
        if c.cmd_index != self.prelim_scan_cycle_start_index:
            self.prelim_scan_saw_advance = True
        if (
            self.prelim_scan_saw_advance
            and c.cmd_index == self.prelim_scan_cycle_start_index
        ):
            self.prelim_scan_cycles += 1
            self.prelim_scan_saw_advance = False
            if self.prelim_scan_cycles >= SEARCH_PRELIM_SCAN_CYCLES:
                self.phase = "EXPANDED"

    def _run_continuous_search(self) -> None:
        c = self.ctx
        rx, ry, yaw = c.wm.robot_x, c.wm.robot_y, c.wm.robot_yaw

        c.update_head_command_search()
        self._maybe_advance_prelim()

        left_out, right_out = _search_wing_rays_outside(rx, ry, yaw)
        if self.bias_facing_outside and not (left_out or right_out):
            self.bias_facing_outside = False

        if _search_near_field_boundary(rx, ry, SEARCH_BOUNDARY_MARGIN_M):
            override = _search_boundary_spin_dir(left_out, right_out)
            if override is not None:
                self.scan_dir = override

        cmd_theta = float(np.clip(
            self.scan_dir * SEARCH_SPIN_VTHETA,
            -c.vtheta_limit,
            c.vtheta_limit,
        ))
        c.command.set_body(0.0, 0.0, cmd_theta)

    def _goalie_fallback_spin(self) -> StateID | None:
        c = self.ctx
        elapsed = self._elapsed_search_sec()
        if elapsed > 6.0:
            print("Goalie fallback spin exhausted -> BLOCKING")
            return StateID.BLOCKING
        yaw_scan_max = 0.35
        yaw_gain = 1.6
        yaw_tol = 0.05
        max_scan_vtheta = 1.4
        target_yaw = self.scan_center_yaw + self.scan_dir * yaw_scan_max
        target_yaw = np.clip(target_yaw, -1.0, 1.0) # no turning for more than around 60 degrees in either direction
        y_err = c.to_p_in_pi(target_yaw - c.wm.robot_yaw)
        if abs(y_err) < yaw_tol:
            self.scan_dir = -self.scan_dir
        cmd_theta = np.clip(y_err * yaw_gain, -max_scan_vtheta, max_scan_vtheta)
        c.command.set_body(0.0, 0.0, cmd_theta)
        return None


class AssistState(State):
    id = StateID.ASSIST

    def on_enter(self) -> None:
        self.ctx.get_logger().info("State -> ASSIST")
        print("\033[91mEntering ASSIST state\033[0m")

    def on_exit(self) -> None:
        self.ctx.get_logger().info("ASSIST -> exit")

    def execute(self) -> StateID | None:
        c = self.ctx
        if c.confirmed_ball_lost_in_play():
            return StateID.LOOK_FOR_BALL

        self.ctx.update_head_command()

        # Formation target and test
        formation_target = c.compute_formation_target_for_me()
        if formation_target is not None:
            target_x, target_y = formation_target
            target_theta = 0.0
            c.publish_debug_pose(target_x, target_y, target_theta)
            c.walk_skill.tick(
                WalkToPoseRequest(
                    robot_pose=c.robot_pose2(),
                    target_pose=Pose2(target_x, target_y, target_theta),
                    sprint_distance=4.0,
                    obstacles=c.avoid_obstacle_points(),
                    apply_avoidance=True,
                ),
                c.command,
            )
            return None

         # Otherwise face the ball
        ball_pos = c.ball_global_array()
        robot_pos = c.robot_position_array()
        robot_yaw = c.wm.robot_yaw
        vec_robot_to_ball = ball_pos - robot_pos
        target_theta = atan2(vec_robot_to_ball[1], vec_robot_to_ball[0])
        c.command.set_body(0.0, 0.0, (target_theta - robot_yaw) * 1.6)
        return None

class BlockingState(State):

    id = StateID.BLOCKING
    DIST_TOL = GOALIE_BLOCKING_DIST_TOL
    THETA_TOL = GOALIE_BLOCKING_THETA_TOL

    def on_enter(self) -> None:
        super().on_enter()
        self.ctx.end_goalie_clear()
        self._sway_dir = 1.0

    def execute(self) -> StateID | None:
        c = self.ctx
        if c.set_play == SET_PLAY_GOAL_KICK:
           return StateID.DRIBBLE_CLEAR
        if lost_next := c.goalie_ball_lost_transition():
            return lost_next
        # Don't start a clear (RL kick) while we're inside our own goal; walk back out first.
        if c.goalie_should_clear() and not c.robot_in_own_goal():
            c.begin_goalie_clear()
            if GOALIE_CLEAR_USE_RL_KICK:
                return StateID.KICK
            return StateID.GO if GOALIE_CLEAR_USE_GO_STATE else StateID.DRIBBLE_CLEAR
        c.update_head_command()
        tol = dict(distance_tolerance=self.DIST_TOL, theta_tolerance=self.THETA_TOL)
        if c.has_global_ball():
            block = calculate_blocking_pose(
                "goalie",
                c.goalie_ball_xy(),
                c.ws.ball_velocity_global(),
                c.ws.fused_ball_age_sec(),
                robot_pos=(c.wm.robot_x, c.wm.robot_y),
            )
            target = (block.x, block.y, block.theta)
            scales = dict(
                forward_scale=block.forward_scale,
                strafe_scale=block.strafe_scale,
            )
        else:
            target = (GOALIE_LINE, 0.0, 0.0)
            scales = {}
        c.publish_debug_pose(*target)
        cmd_x, cmd_y, cmd_theta = walk_to_pose_velocity(
            WalkToPoseRequest(
                robot_pose=c.robot_pose2(),
                target_pose=Pose2(target[0], target[1], target[2]),
                **tol,
                **scales,
            ),
        )
        if cmd_x == 0.0 and cmd_y == 0.0 and cmd_theta == 0.0:
            lateral_off = (
                -(c.wm.robot_x - target[0]) * sin(c.wm.robot_yaw)
                + (c.wm.robot_y - target[1]) * cos(c.wm.robot_yaw)
            )
            if lateral_off * self._sway_dir >= GOALIE_BLOCKING_IDLE_SWAY_AMPLITUDE_M:
                self._sway_dir = -self._sway_dir
            cmd_y = GOALIE_BLOCKING_IDLE_SWAY_SPEED * self._sway_dir
        c.command.set_body(cmd_x, cmd_y, cmd_theta)
        return None

class PreEnterFieldState(State):
    id = StateID.PRE_ENTER_FIELD

    def on_enter(self) -> None:
        self.ctx.get_logger().info("State -> PRE_ENTER_FIELD")
        # say "pre enter field"
        print("\033[91mEntering PRE_ENTER_FIELD state\033[0m")
        self._entered_at = self.ctx.get_clock().now()
        self.ctx.set_scan_index = 0

    def on_exit(self) -> None:
        self.ctx.get_logger().info("PRE_ENTER_FIELD -> exit")
        if ALWAYS_SOCCER:
            self.ctx.ensure_soccer_mode()
        else:
            self.ctx.loco_enter_walk()

    def execute(self) -> StateID | None:
        c = self.ctx
        pitch_target, yaw_target = c.cmd_sequence[c.set_scan_index]
        c.command.set_head(
            pitch_target, yaw_target, speed_pitch=0.8, speed_yaw=2.8,
        )
        if (
            abs(c.ws.me.head_pitch - pitch_target) < 0.1
            and abs(c.ws.me.head_yaw - yaw_target) < 0.1
        ):
            c.set_scan_index = (c.set_scan_index + 1) % len(c.cmd_sequence)
            pitch_target, yaw_target = c.cmd_sequence[c.set_scan_index]
            c.command.set_head(
                pitch_target, yaw_target, speed_pitch=0.8, speed_yaw=2.8,
            )
        elapsed = (c.get_clock().now() - self._entered_at).nanoseconds / 1e9
        if elapsed > 5.0:
            c.need_scan_for_localisation = False
        if elapsed > 3.0 and elapsed < 5.0:
            self.ctx.own_half_field_localise_toggle_pub.publish(Bool(data=True))
        return None

class GoState(State):
    """Smooth approach: velocity field to a goal behind the ball with ball keep-out."""

    id = StateID.GO

    BEHIND_DIST = 0.7
    GOALIE_BEHIND_DIST = 0.3
    BALL_KEEP_OUT = 0.45
    ARC_BLEND = 0.65
    GAIN_X = 0.6
    GAIN_Y = 1.0
    MIN_SPEED = 0.30
    BLEND_DIST = 1.4
    DIST_TOLERANCE = 0.8 # 0.38
    THETA_TOLERANCE = 0.8
    GO_APPROACH_EXTRA = 0.1

    def on_enter(self) -> None:
        self.ctx.get_logger().info("State -> GO")
        print("\033[91mEntering GO state\033[0m")


    def on_exit(self) -> None:
        self.ctx.get_logger().info("GO -> exit")

    def execute(self):
        c = self.ctx
        if c.confirmed_ball_lost_in_play():
            return StateID.LOOK_FOR_BALL
        if c.role_decision == "assist":
            return StateID.ASSIST
        if c.is_goalie:
            if lost_next := c.goalie_ball_lost_transition():
                return lost_next
            if not c.goalie_still_clearing():
                return c.goalie_after_clear_transition()

        self.ctx.update_head_command()

        robot_pos = c.robot_position_array()
        robot_yaw = c.wm.robot_yaw
        ball_pos_now = c.ball_global_array(0.0)


        ball_threatened = self.ball_threatened_by_opponent()
        

        # if c.is_goalie and c.goalie_clear_mode:
        #     c.refresh_goalie_clear_target()
        #     aim = c.goalie_clear_aim_unit()
        #     unit_approach = -aim
        #     target_world_now = c.goalie_clear_kick_goal_world(ball_pos_now)
        #     c._last_kick_target_world = target_world_now.copy()
        # else:
        target_world_now = c.current_kick_target_world(ball_pos=ball_pos_now, ball_threatened=ball_threatened)
        vec_goal_to_ball = c.goal_to_ball_vector(0.0, target_world=target_world_now)
        unit_approach = c.unit_or_default(vec_goal_to_ball, np.array([1.0, 0.0]))
        
        # transit walk to ball if threatened and close enough with nonbackwards alignment/goal alignment
        robot_to_ball = ball_pos_now - robot_pos
        dist_to_ball = np.linalg.norm(robot_to_ball)
        own_throw_in_or_corner = (
            c.set_play in (SET_PLAY_CORNER_KICK, SET_PLAY_THROW_IN)
            and c.kicking_team == c.team_number
        )
        if not own_throw_in_or_corner:
            if c.is_goalie and robot_to_ball[0] > 0.0:
                return StateID.WALK_TO_BALL_KICK
            if ball_threatened and dist_to_ball < 1.1:
                if c.in_defend_zone() and robot_to_ball[0] > 0.0:
                    return StateID.WALK_TO_BALL_KICK
                elif not c.in_defend_zone():
                    # NOTE: Ihis makes robot inaccurate in kicking, consider make the threat window smaller or get rid of this when attack
                    robot_to_ball_heading = atan2(robot_to_ball[1], robot_to_ball[0])
                    ball_to_target_heading = atan2(target_world_now[1] - ball_pos_now[1], target_world_now[0] - ball_pos_now[0])
                    heading_error = c.to_p_in_pi(ball_to_target_heading - robot_to_ball_heading)
                    if abs(heading_error) > 0.3:
                        return StateID.WALK_TO_BALL_KICK

        behind_point = ball_pos_now + unit_approach * self.BEHIND_DIST
        target_theta = atan2(-unit_approach[1], -unit_approach[0])

        # Ball-specific route: first reach an approach point on the kick line,
        # then finish along the behind-ball corridor into the stance point.
        #approach_point = (
        #    ball_pos_now
        #    + unit_approach * (self.BEHIND_DIST - self.GO_APPROACH_EXTRA)
        #)
        approach_point = None
        rel_ball_to_robot = robot_pos - ball_pos_now
        behind_progress = float(rel_ball_to_robot @ unit_approach)
        lateral_offset = abs(
            rel_ball_to_robot[0] * unit_approach[1]
            - rel_ball_to_robot[1] * unit_approach[0]
        )
        in_final_corridor = (
            behind_progress >= self.BEHIND_DIST
            and lateral_offset < self.BALL_KEEP_OUT
        )
        c.publish_debug_pose(
            float(behind_point[0]), float(behind_point[1]), target_theta,
        )
        dx = behind_point[0] - robot_pos[0]
        dy = behind_point[1] - robot_pos[1]
        dist = sqrt(dx * dx + dy * dy)
        heading_error = abs(c.to_p_in_pi(robot_yaw - target_theta))
        enter_kick_now = (
            dist * 0.8 < self.DIST_TOLERANCE and heading_error * 0.8 < self.THETA_TOLERANCE
        )
        exit_gate_now = (
            dist > GO_KICK_EXIT_DIST_TOL or heading_error > GO_KICK_EXIT_THETA_TOL
        )

        if c.confirmed_kick_entry("go", enter_kick_now, exit_gate_now):
            if own_throw_in_or_corner:
                return StateID.KICK
            if c.is_goalie:
                return StateID.WALK_TO_BALL_KICK
            # TODO: better cost function to decide which kick to use. Factor in opponents and maybe direction
            if ball_threatened:
                return StateID.WALK_TO_BALL_KICK
            else:
                return StateID.KICK
        if c.is_goalie:
            c.publish_debug_pose(float(behind_point[0]), float(behind_point[1]), target_theta)
            c.walk_skill.tick(
                WalkToPoseRequest(
                    robot_pose=c.robot_pose2(),
                    target_pose=Pose2(float(behind_point[0]), float(behind_point[1]), target_theta),
                    distance_tolerance=self.DIST_TOLERANCE,
                    theta_tolerance=self.THETA_TOLERANCE,
                    obstacles=c.avoid_obstacle_points(),
                    apply_avoidance=True,
                ),
                c.command,
            )
            return None

        obstacles = c.navigation_obstacles(extra=[ball_pos_now])
        keep_out = self.BALL_KEEP_OUT + 0.15
        
        if c.set_play != SET_PLAY_NONE and c.kicking_team == c.team_number:
            safety_margin = 0.8 # extend the margin for kick in
        else:
            safety_margin = 0.35
        
        c.publish_debug_pose(float(behind_point[0]), float(behind_point[1]), target_theta)
        c.navigate_skill.tick(
            NavigateToPoseRequest(
                robot_pose=c.robot_pose2(),
                target_pose=Pose2(float(behind_point[0]), float(behind_point[1]), target_theta),
                plan_obstacles=tuple(
                    (
                        float(np.asarray(item, dtype=float)[0]),
                        float(np.asarray(item, dtype=float)[1]),
                    )
                    for item in obstacles
                ),
                avoid_obstacles=c.avoid_obstacle_points(),
                apply_avoidance=True,
                keep_out=keep_out,
                approach_point=None,
                go_ball_pos=(float(ball_pos_now[0]), float(ball_pos_now[1])),
                safety_margin=safety_margin,
                distance_tolerance=self.DIST_TOLERANCE,
                theta_tolerance=self.THETA_TOLERANCE,
                speed_scale=1.0,
                vx_limit=c.vx_limit,
                vy_limit=c.vy_limit,
                vtheta_limit=c.vtheta_limit,
            ),
            c.command,
        )
        return None

    def ball_threatened_by_opponent(self) -> bool:
        c = self.ctx

        if c.set_play != SET_PLAY_NONE and c.kicking_team == c.team_number:
            return False

        own_goal = np.array([-FIELD_LENGTH_M / 2.0, 0.0])
        our_goal_to_ball = c.ball_global() - own_goal
        
        depth_axis = our_goal_to_ball / np.linalg.norm(our_goal_to_ball)          # unit vector pointing from goal → ball
        perp_axis = np.array([-depth_axis[1], depth_axis[0]])
        half_width = 0.7
        depth = 1.6
        corners = np.array([
            c.ball_global() + perp_axis * half_width,
            c.ball_global() - perp_axis * half_width,
            c.ball_global() - perp_axis * half_width + depth_axis * depth,
            c.ball_global() + perp_axis * half_width + depth_axis * depth,
        ])

        for robot in c.wm.likely_opponents(now_sec=c.ws.now_sec(), max_age_sec=2.0):
            if point_in_polygon(np.array([robot.pose.x, robot.pose.y]), corners):
                bigbrother.log_threatened_polygon(corners, threat=True)
                return True
        bigbrother.log_threatened_polygon(corners, threat=False)
        return False

def point_in_polygon(point: np.ndarray, polygon: np.ndarray) -> bool:
    n = len(polygon)
    for i in range(n):
        edge = polygon[(i + 1) % n] - polygon[i]
        to_point = point - polygon[i]
        if edge[0] * to_point[1] - edge[1] * to_point[0] < 0:
            return False
    return True


class DribbleState(State):
    """Goal-aware dribble with alignment-based speed and heading blend."""

    id = StateID.DRIBBLE

    GAIN_X = 1.0
    GAIN_Y = 1.4
    MIN_DRIBBLE_SPEED = 0.17
    MAX_DRIBBLE_SPEED = 0.5
    HEADING_BLEND_BALL = 0.7
    HEADING_BLEND_GOAL = 0.3
    ABORT_DIST = 1.4
    ABORT_YAW = 1.5

    def on_enter(self) -> None:
        self.ctx.get_logger().info("State -> DRIBBLE")
        print("\033[91mEntering DRIBBLE state\033[0m")

    def on_exit(self) -> None:
        self.ctx.get_logger().info("DRIBBLE -> exit")

    def execute(self) -> StateID | None:
        c = self.ctx

        ball_pos = c.ball_global_array()
        robot_pos = c.robot_position_array()
        robot_yaw = c.wm.robot_yaw
        vec_robot_to_ball = ball_pos - robot_pos
        dist_to_ball = np.linalg.norm(vec_robot_to_ball)
        target_world = c.current_kick_target_world(ball_pos=ball_pos, robot_pos=robot_pos)
        vec_goal_to_ball = c.goal_to_ball_vector(target_world=target_world)
        
        error_yaw = c.goal_alignment_error(vec_robot_to_ball, vec_goal_to_ball)
        if c.confirmed_ball_lost_in_play():
            print("\033[93mBall lost\033[0m")
            return StateID.LOOK_FOR_BALL
        if dist_to_ball > self.ABORT_DIST:
            print("\033[93mFar ball\033[0m")
            return StateID.GO
        if abs(error_yaw) > self.ABORT_YAW and dist_to_ball > 0.25:
            print("\033[93mError heading\033[0m")
            return StateID.GO

        c.update_head_command()

        local_x, local_y = c.world_vector_to_robot(vec_robot_to_ball, robot_yaw)
        alignment = (1.0 + cos(error_yaw)) / 2.0
        speed = self.MIN_DRIBBLE_SPEED + alignment * (
            self.MAX_DRIBBLE_SPEED - self.MIN_DRIBBLE_SPEED
        )
        raw_dist = sqrt(local_x * local_x + local_y * local_y)
        if raw_dist > 1e-3:
            cmd_x = float(np.clip(
                local_x / raw_dist * speed * self.GAIN_X,
                -c.vx_limit,
                c.vx_limit,
            ))
            cmd_y = float(np.clip(
                local_y / raw_dist * speed * self.GAIN_Y,
                -c.vy_limit,
                c.vy_limit,
            ))
        else:
            cmd_x = speed
            cmd_y = 0.0

        angle_to_ball = atan2(local_y, local_x)
        goal_heading = atan2(GOAL_Y - robot_pos[1], GOAL_X - robot_pos[0])
        goal_heading_local = c.to_p_in_pi(goal_heading - robot_yaw)
        cmd_theta = (
            self.HEADING_BLEND_BALL * angle_to_ball +
            self.HEADING_BLEND_GOAL * goal_heading_local
        )
        c.command.set_body(cmd_x, cmd_y, cmd_theta)

        enter_kick_now = (
            dist_to_ball < DRIBBLE_KICK_ENTER_DIST and
            c.ball_global()[0] > FIELD_LENGTH_M / 6.0
        )
        exit_gate_now = dist_to_ball > DRIBBLE_KICK_EXIT_DIST
        if c.confirmed_kick_entry("dribble", enter_kick_now, exit_gate_now):
            return StateID.KICK
        return None


class DribbleClearState(State):
    """Goalie clear: align behind the ball along the clear direction from
    simple_clear_target, then hand off to WALK_TO_BALL_KICK to drive it out."""

    id = StateID.DRIBBLE_CLEAR

    ALIGN_DIST_TOL = 0.1
    ALIGN_THETA_TOL = 0.30
    DIST_TOLERANCE = 0.38
    THETA_TOLERANCE = 0.6

    def on_enter(self) -> None:
        super().on_enter()
        # Lock the clear direction on entry so alignment commits to one axis.
        _, _, _, self._aim = self.ctx.clear_dribble_pose()

    def execute(self) -> StateID | None:
        c = self.ctx
        if c.set_play == SET_PLAY_GOAL_KICK:
            if c.wm.robot_x > GOALIE_LINE:
                c.update_head_command(speed_yaw_scale=1.5)
                c.publish_debug_pose(GOALIE_LINE - 0.2, 0.0, 0.0)
                c.walk_skill.tick(
                    WalkToPoseRequest(
                        robot_pose=c.robot_pose2(),
                        target_pose=Pose2(GOALIE_LINE - 0.2, 0.0, 0.0),
                        distance_tolerance=self.DIST_TOLERANCE,
                        theta_tolerance=self.THETA_TOLERANCE,
                        sprint_distance=1.2,
                        obstacles=c.avoid_obstacle_points(),
                        apply_avoidance=True,
                    ),
                    c.command,
                )
                return None
            else:
                return StateID.KICK

        if lost_next := c.goalie_ball_lost_transition():
            return lost_next
        if not c.goalie_still_clearing():
            return c.goalie_after_clear_transition()

        c.update_head_command()

        # Walk to a standoff pose behind the ball, facing the clear direction.
        target_x, target_y, target_theta, _ = c.clear_dribble_pose(aim=self._aim)
        cmd_x, cmd_y, cmd_theta = walk_to_pose_velocity(
            WalkToPoseRequest(
                robot_pose=c.robot_pose2(),
                target_pose=Pose2(target_x, target_y, target_theta),
                distance_tolerance=self.ALIGN_DIST_TOL,
                theta_tolerance=self.ALIGN_THETA_TOL,
                sprint_distance=1.2,
            ),
        )
        c.publish_debug_pose(target_x, target_y, target_theta)

        # Aligned behind the ball -> let WALK_TO_BALL_KICK drive in and clear it.
        dist = sqrt(
            (c.wm.robot_x - target_x) ** 2 + (c.wm.robot_y - target_y) ** 2
        )
        heading_error = abs(c.to_p_in_pi(target_theta - c.wm.robot_yaw))
        enter_kick_now = (
            dist * 0.8 < self.DIST_TOLERANCE and heading_error * 0.8 < self.THETA_TOLERANCE
        )
        exit_gate_now = (
            dist > GO_KICK_EXIT_DIST_TOL or heading_error > GO_KICK_EXIT_THETA_TOL
        )

        if c.confirmed_kick_entry("go", enter_kick_now, exit_gate_now):
            if (
                c.set_play in (SET_PLAY_CORNER_KICK, SET_PLAY_THROW_IN)
                and c.kicking_team == c.team_number
            ):
                return StateID.KICK
            return StateID.WALK_TO_BALL_KICK
        c.command.set_body(cmd_x, cmd_y, cmd_theta)
        return None


class MoveToReadyPositionState(State):
    id = StateID.MOVE_TO_READY

    def on_enter(self) -> None:
        self.ctx.get_logger().info("State -> MOVE_TO_READY")
        self.ctx.command.set_head(pitch=0.53, yaw=0.0, speed_pitch=0.8, speed_yaw=1.4)
        print("\033[91mEntering MOVE_TO_READY state\033[0m")

    def on_exit(self) -> None:
        self.ctx.get_logger().info("MOVE_TO_READY -> exit")

    def execute(self) -> StateID | None:
        c = self.ctx

        if c.is_goalie:
            c.publish_debug_pose(GOALIE_LINE, 0.0, 0.0)
            c.walk_skill.tick(
                WalkToPoseRequest(
                    robot_pose=c.robot_pose2(),
                    target_pose=Pose2(GOALIE_LINE, 0.0, 0.0),
                    distance_tolerance=0.1,
                    theta_tolerance=0.25,
                    sprint_distance=1.2,
                    obstacles=c.avoid_obstacle_points(),
                    apply_avoidance=True,
                ),
                c.command,
            )
            return None

        formation_target = c.compute_formation_target_for_me()
        if formation_target is not None:
            target_x, target_y = formation_target
            target_theta = 0.0
            c.publish_debug_pose(target_x, target_y, target_theta)
            c.walk_skill.tick(
                WalkToPoseRequest(
                    robot_pose=c.robot_pose2(),
                    target_pose=Pose2(target_x, target_y, target_theta),
                    sprint_distance=1.0,
                    obstacles=c.avoid_obstacle_points(),
                    apply_avoidance=True,
                ),
                c.command,
            )
            return None

        # Safe fallback if formation config/backend cannot be loaded.
        idx = max(0, min(c.player_number - 1, len(c.ready_positions) - 1))
        target_x, target_y, target_theta = c.ready_positions[idx]
        c.publish_debug_pose(target_x, target_y, target_theta)
        c.walk_skill.tick(
            WalkToPoseRequest(
                robot_pose=c.robot_pose2(),
                target_pose=Pose2(target_x, target_y, target_theta),
                sprint_distance=1.0,
                obstacles=c.avoid_obstacle_points(),
                apply_avoidance=True,
            ),
            c.command,
        )
        return None


class WalkToPointState(State):
    """Walk to a fixed world-frame pose; no ball chase or game-controller behaviour."""

    id = StateID.WALK_TO_POINT

    def on_enter(self) -> None:
        self.ctx.get_logger().info("State -> WALK_TO_POINT (awaiting target)")
        print("\033[91mEntering WALK_TO_POINT state (RViz/stdin targets)\033[0m")

    def on_exit(self) -> None:
        self.ctx.get_logger().info("WALK_TO_POINT -> exit")

    def execute(self) -> StateID | None:
        if not self.ctx.has_walk_to_point_target():
            self.ctx.command.stop_body()
            return None
        target_x, target_y, target_theta = self.ctx.get_walk_to_point_target()
        self.ctx.publish_debug_pose(target_x, target_y, target_theta)
        self.ctx.walk_skill.tick(
            WalkToPoseRequest(
                robot_pose=self.ctx.robot_pose2(),
                target_pose=Pose2(target_x, target_y, target_theta),
                sprint_distance=1.0,
                obstacles=self.ctx.avoid_obstacle_points(),
                apply_avoidance=True,
            ),
            self.ctx.command,
        )
        return None


class SetState(State):
    id = StateID.SET

    def on_enter(self) -> None:
        self.ctx.get_logger().info("State -> SET")
        print("\033[91mEntering SET state\033[0m")
        self.ctx.arbiter.request_stop_now()

    def on_exit(self) -> None:
        self.ctx.get_logger().info("SET -> exit")

    def execute(self) -> StateID | None:
        self.ctx.update_head_command()
        return None

class StandState(State):
    id = StateID.STAND

    def on_enter(self) -> None:
        self.ctx.get_logger().info("State -> STAND")
        print("\033[91mEntering STAND state\033[0m")
        self.ctx.command.stop_body()
        self.ctx.arbiter.request_stop_now()

    def on_exit(self) -> None:
        self.ctx.get_logger().info("STAND -> exit")
        if ALWAYS_SOCCER:
            self.ctx.ensure_soccer_mode()
        else:
            self.ctx.loco_enter_walk()

    def execute(self) -> StateID | None:
        self.ctx.command.stop_body()
        return None

class WalkToBallKickState(State):
    id = StateID.WALK_TO_BALL_KICK

    def on_enter(self) -> None:
        self.ctx.get_logger().info("State -> WALK_TO_BALL_KICK")
        self.walk_to_ball_kick_started_at = self.ctx.get_clock().now()
        print("\033[91mEntering WALK_TO_BALL_KICK state\033[0m")
        self.initial_ball_pos = self.ctx.ball_global_array()

    def on_exit(self) -> None:
        self.ctx.get_logger().info("WALK_TO_BALL_KICK -> exit")
        self.walk_to_ball_kick_started_at = None

    def execute(self) -> StateID | None:
        c = self.ctx
        if (
            c.set_play in (SET_PLAY_CORNER_KICK, SET_PLAY_THROW_IN)
            and c.kicking_team == c.team_number
        ):
            return StateID.GO
        elapsed = (c.get_clock().now() - self.walk_to_ball_kick_started_at).nanoseconds / 1e9
        
        c.update_head_command(speed_yaw_scale=2.0)

        ball_pos = c.best_kick_ball_position()
        if ball_pos is None:
            return StateID.LOOK_FOR_BALL

        robot_pos = c.robot_position_array()

        vec_robot_to_ball = ball_pos - robot_pos
        dist_to_ball = np.linalg.norm(vec_robot_to_ball)

        if dist_to_ball < 1e-3:
            c.command.stop_body()
            return None

        theta_correction_robot_frame = c.to_p_in_pi(
            atan2(vec_robot_to_ball[1], vec_robot_to_ball[0]) - c.wm.robot_yaw
        )

        dx_to_ball_robot_frame = dist_to_ball * cos(theta_correction_robot_frame)
        dy_to_ball_robot_frame = dist_to_ball * sin(theta_correction_robot_frame)
        
        if( np.linalg.norm(ball_pos - self.initial_ball_pos) > 2.0):
            return StateID.LOOK_FOR_BALL
        if vec_robot_to_ball[0] < -0.2: # ball is behind in world frame
            print(f"\033[93mWALK_TO_BALL_KICK ball behind {dx_to_ball_robot_frame:.2f}m\033[0m")
            return StateID.GO

        # heading correction, top priority before moving forward
        if dist_to_ball >0.5:
            if abs(theta_correction_robot_frame) > 0.2:
                c.command.set_body(0.0, 0.0, theta_correction_robot_frame * 1.3)
                return None
        else:
            # too close, theta is unreliable, do not us ethat to abort
            if abs(dy_to_ball_robot_frame) > 0.24:
                c.command.set_body(0.0, 0.0, theta_correction_robot_frame * 1.0)
                return None

        cmd_x = float(np.clip(
            dx_to_ball_robot_frame / dist_to_ball * 1.5,
            -c.vx_limit,
            c.vx_limit,
        ))
        cmd_y = float(np.clip(
            dy_to_ball_robot_frame / dist_to_ball * 1.5,
            -c.vy_limit,
            c.vy_limit,
        ))
        
        c.command.set_body(cmd_x, cmd_y, 0.0)
        if c.is_goalie and not c.goalie_still_clearing():
            return StateID.BLOCKING

        if c.fused_ball_age_sec() > 3.0:
            print("\033[93mRL kick lost ball\033[0m")
            return StateID.LOOK_FOR_BALL
        if dist_to_ball > 1.4 and not c.is_goalie:
            print(f"\033[93mWALK_TO_BALL_KICK far ball {dist_to_ball:.2f}m\033[0m")
            return StateID.GO
        if c.ball_global()[0] > FIELD_LENGTH_M / 2.0:
            print(f"\033[93mWALK_TO_BALL_KICK goalled in {c.ball_global()[0]:.2f}m\033[0m")
            return StateID.GO
        if abs(c.ball_global()[1]) > FIELD_WIDTH_M / 2.0 + 0.2:
            print(f"\033[93mWALK_TO_BALL_KICK ball out of field {c.ball_global()[0]:.2f}m\033[0m")
            return StateID.GO
        if elapsed > 1.0:
            return StateID.WALK_TO_BALL_KICK
        return None
    
class KickState(State):
    id = StateID.KICK

    def __init__(self, ctx: "BallChaseStateMachineNode"):
        super().__init__(ctx)
        self._locked_ball_pos: np.ndarray | None = None
        self._locked_target_world: np.ndarray | None = None
        self._locked_power: float = 3.0

    def on_enter(self) -> None:
        c = self.ctx
        c.get_logger().info("State -> KICK")
        c.reset_kick_entry_gate()
        
        self._locked_target_world = None
        self._locked_ball_pos = None
        self._locked_power = 2.4
        use_dynamic_power = True
        
        if c.kicking_off:
            self._locked_target_world = c.default_kick_target_world() #np.array([2.0, 3.0])
        elif c.is_goalie and ((c.goalie_clear_mode and GOALIE_CLEAR_USE_RL_KICK) or c.set_play == SET_PLAY_PENALTY_KICK):
            self._locked_ball_pos = c.ball_global_array()
            self._locked_target_world = c.default_kick_target_world()
            self._locked_power = KICK_POWER_FAR
            use_dynamic_power = False
        elif c.is_goalie and c.goalie_clear_mode:
            self._locked_ball_pos = c.ball_global_array()
            clear_target = c._update_goalie_clear_target()
            if clear_target.valid:
                self._locked_target_world = np.array(clear_target.landing_xy, dtype=float)
                self._locked_power = clear_target.kick_power
            else:
                aim = c.sideline_clear_aim()
                self._locked_target_world = self._locked_ball_pos + aim * SIDELINE_CLEAR_GOAL_OFFSET_M
                self._locked_power = GOALIE_SIDELINE_CLEAR_KICK_POWER
            use_dynamic_power = False
        else:
            # Freeze the target the approach state (GO/DRIBBLE) last used, so the kick
            # direction matches how we lined up. Fall back to a fresh selection, then to
            # the default goal target, only if no approach target is available.
            self._locked_ball_pos = c.ball_global_array()
            target = c._last_kick_target_world
            if target is None:
                target = c.current_kick_target_world(
                    ball_pos=self._locked_ball_pos,
                    robot_pos=c.robot_position_array(),
                )
            self._locked_target_world = (
                target if target is not None else c.default_kick_target_world()
            )
        if use_dynamic_power and self._locked_target_world is not None:
            # Lock dynamic power for this kick; updating it every tick can chatter at band edges.
            self._locked_power = c.dynamic_kick_power(
                self._locked_target_world,
                c.robot_position_array(),
            )
        self.initial_ball_pos = c.ball_global_array()
        c.enable_booster_visual_kick()
        if self._locked_target_world is not None:
            c.kick_skill.on_enter(
                KickRequest(
                    robot_pose=c.robot_pose2(),
                    ball=Point2(
                        float(self._locked_ball_pos[0]) if self._locked_ball_pos is not None else float(self.initial_ball_pos[0]),
                        float(self._locked_ball_pos[1]) if self._locked_ball_pos is not None else float(self.initial_ball_pos[1]),
                    ),
                    target=Point2(float(self._locked_target_world[0]), float(self._locked_target_world[1])),
                    power=float(self._locked_power),
                )
            )
        c.goalie_clear_kick_phase = c.is_goalie and c.goalie_clear_mode
        c.rl_kick_started_at = c.get_clock().now()

        print("\033[91mEntering KICK state\033[0m")

    def on_exit(self) -> None:
        c = self.ctx
        c.get_logger().info("KICK -> exit")
        c.kick_skill.on_exit()
        c.goalie_clear_kick_phase = False
        c.reset_kick_target_lock()
        c.arbiter.request_visual_kick(False)
        if not ALWAYS_SOCCER:
            c.loco_enter_walk()


    def execute(self) -> StateID | None:
        c = self.ctx
        elapsed = (c.get_clock().now() - c.rl_kick_started_at).nanoseconds / 1e9

        # Abort the moment we step inside our own goal, so we don't carry the ball in.
        if c.robot_in_own_goal():
            print("\033[93mRL kick aborted: robot in own goal\033[0m")
            if c.is_goalie:
                c.end_goalie_clear()
                return StateID.BLOCKING
            return StateID.LOOK_FOR_BALL

        if elapsed < 0.5:
            # do not abort for the first 1 seconds of the kick
            try:
                c.update_head_command(speed_yaw_scale=3.0, speed_pitch_scale=0.5)
                c.arbiter.request_stop_now()
            except Exception:
                pass
            return None
        ball_pos = c.best_kick_ball_position()
        if ball_pos is None:
            return StateID.LOOK_FOR_BALL
        
        robot_pos = c.robot_position_array()
        bigbrother.log_robot_to_ball(robot_pos, ball_pos - robot_pos)
        bigbrother.log_kick_target_world(ball_pos, self._locked_target_world, self._locked_power)

        if self._locked_target_world is not None:
            c.kick_skill.tick(
                KickRequest(
                    robot_pose=c.robot_pose2(),
                    ball=Point2(float(ball_pos[0]), float(ball_pos[1])),
                    target=Point2(float(self._locked_target_world[0]), float(self._locked_target_world[1])),
                    power=float(self._locked_power),
                ),
                c.command,
            )
        if ALWAYS_SOCCER:
            c.update_head_command(speed_yaw_scale=3.0, speed_pitch_scale=1.0)
        
        if not c.goalie_should_clear() and c.is_goalie and c.goalie_clear_mode:
            c.end_goalie_clear()
            return StateID.BLOCKING

        dist_to_ball = np.linalg.norm(robot_pos - ball_pos)
        if( np.linalg.norm(ball_pos - self.initial_ball_pos) > 1.5):
            # Ball moved enough, leave kik
            print("\033[93mRL kick ball moved\033[0m")
            return StateID.LOOK_FOR_BALL
        if elapsed < 1.0 or c.set_play == SET_PLAY_GOAL_KICK:
            # do not abort for the first 1 seconds of the kick
            return None
        if elapsed > c.kick_hold_seconds:
            print("\033[93mRL kick timeout\033[0m")
            return StateID.LOOK_FOR_BALL
        if c.fused_ball_age_sec() > 3.0:
            print("\033[93mRL kick lost ball\033[0m")
            return StateID.LOOK_FOR_BALL
        if dist_to_ball > 1.5:
            print(f"\033[93mRL kick far ball {dist_to_ball:.2f}m\033[0m")
            return StateID.GO
        if c.ball_global()[0] > FIELD_LENGTH_M / 2.0: #TODO: make this more robust for corner kicks and goal kicks, check the set play
            print(f"\033[93mRL kick goalled in {c.ball_global()[0]:.2f}m\033[0m")
            return StateID.GO

        c.command.stop_body()
        return None

class StaticKickState(State):
    """Kick by delegating to the `/kick` ROS 2 action server."""

    id = StateID.KICK
    TOP_LEVEL_TIMEOUT_S = 20.0

    def __init__(self, ctx: "BallChaseStateMachineNode"):
        super().__init__(ctx)
        self._goal_future = None
        self._goal_handle = None
        self._result_future = None
        self._done = False
        self._success = False
        self._started_at = None

    def on_enter(self) -> None:
        c = self.ctx
        c.get_logger().info("State -> STATIC_KICK")
        print("\033[91mEntering STATIC_KICK state\033[0m")
        c.command.stop_body()
        c.arbiter.request_stop_now()

        self._goal_future = None
        self._goal_handle = None
        self._result_future = None
        self._done = False
        self._success = False
        self._started_at = c.get_clock().now()

        if not c.kick_action_client.wait_for_server(timeout_sec=0.5):
            c.get_logger().warn("Kick action server not available; skipping kick")
            self._done = True
            self._success = False
            return

        goal = KickAction.Goal()
        goal.timeout_sec = 10.0
        self._goal_future = c.kick_action_client.send_goal_async(goal)
        self._goal_future.add_done_callback(self._on_goal_response)

    def on_exit(self) -> None:
        c = self.ctx
        c.get_logger().info("STATIC_KICK -> exit")
        if self._goal_handle is not None and not self._done:
            try:
                self._goal_handle.cancel_goal_async()
            except Exception as e:
                c.get_logger().warn(f"cancel_goal_async failed: {e}")

    def execute(self) -> StateID | None:
        c = self.ctx
        c.command.stop_body()
        c.command.set_head(0.72 * 0.8 + c.ws.me.head_pitch * 0.2, c.command.head_yaw)

        elapsed = (c.get_clock().now() - self._started_at).nanoseconds / 1e9
        if elapsed > self.TOP_LEVEL_TIMEOUT_S:
            c.get_logger().warn("StaticKick top-level timeout; aborting")
            return StateID.LOOK_FOR_BALL
        if self._done:
            return StateID.LOOK_FOR_BALL
        return None

    def _on_goal_response(self, future) -> None:
        c = self.ctx
        try:
            goal_handle = future.result()
        except Exception as e:
            c.get_logger().warn(f"send_goal failed: {e}")
            self._done = True
            self._success = False
            return
        if not goal_handle.accepted:
            c.get_logger().warn("Kick goal rejected by server")
            self._done = True
            self._success = False
            return
        self._goal_handle = goal_handle
        self._result_future = goal_handle.get_result_async()
        self._result_future.add_done_callback(self._on_result)

    def _on_result(self, future) -> None:
        c = self.ctx
        try:
            result = future.result().result
            self._success = bool(result.success)
            c.get_logger().info(
                f"Kick action done: success={self._success} msg={result.message}"
            )
        except Exception as e:
            c.get_logger().warn(f"get_result failed: {e}")
            self._success = False
        self._done = True


class BallChaseStateMachineNode(Node):
    """Timer node that reads world-model snapshots and executes actions."""

    def __init__(
        self,
        adapter: BoosterAdapter,
        world_state: WorldStateNode,
        *,
        walk_to_point_mode: bool = False,
    ):
        super().__init__("ball_chase_sm_node")
        self.adapter = adapter
        self.ws_node = world_state
        self.ws = world_state.snapshot()
        self.walk_to_point_mode = walk_to_point_mode
        self._walk_to_point_lock = threading.Lock()
        self._walk_to_point_target = (0.0, 0.0, 0.0)
        self._walk_to_point_has_target = False
        self.get_logger().info("Tracker navigation enabled (SE2 planner + path tracker)")
        self.command = MotionCommand()
        self.walk_skill = WalkToPose()
        self.kick_skill = Kick()
        self.navigate_skill = NavigateToPose(
            max_obstacles=10,
            fixed_obstacles=False,
            replan_period_sec=1.0 / 4.0,
            log_warning=lambda msg: self.get_logger().warning(
                msg, throttle_duration_sec=2.0
            ),
        )
        self.speech_engine = pyttsx3.init()
        self.speech_engine.setProperty("rate", 150)

        self.player_number = int(self.ws.wm.game.player_id)
        self.team_number = int(self.ws.wm.game.team_number)

        self.get_logger().info(
            f"Using team_number={self.team_number}, player_number={self.player_number}"
        )

        self.formation = self.load_formation_config()
        self.active_players = FORMATION_ACTIVE_PLAYERS

        self.ready_positions = [
            (GOALIE_LINE, 0.0, 0.0),
            (FIELD_LENGTH_M * -0.17, FIELD_WIDTH_M * -0.12, 0.0),
            (FIELD_LENGTH_M * -0.26, FIELD_WIDTH_M * 0.1, 0.0),
            (FIELD_LENGTH_M * -0.26, FIELD_WIDTH_M * -0.5, 0.0),
            (FIELD_LENGTH_M * -0.35, FIELD_WIDTH_M * 0.5, 0.0),
        ]

        self.vx_limit = 2.2 # 0.75
        self.vy_limit = 1.9 #0.6
        self.frequency = 30
        self.head_frequency = HEAD_CONTROL_HZ_DEFAULT

        self.tick_rate_window: deque[float] = deque(maxlen=self.frequency *2)

        self.vtheta_limit = 1.3
        self.arbiter = ActionArbiter(
            adapter,
            VelocityLimits(vx=self.vx_limit, vy=self.vy_limit, vtheta=self.vtheta_limit),
            on_walk_send=self._on_walk_send,
        )
        self.go_ball_memory_sec = 5.0
        self.head_fused_ball_memory_sec = 5.0
        self.set_play_ball_memory_sec = 8.0
        self.need_scan_for_localisation = False
        self.cmd_sequence = [
            (0.74, -1.01),
            (0.74, 1.01),
            (0.46, 1.01),
            (0.46, -1.01),
        ]
        self.cmd_index = 0
        self.set_scan_index = 0 # TODO: REMOVE THIS AND INTEGRATE WITH SCAN BEHAVIOUR
        self.rl_kick_started_at = self.get_clock().now()
        self.kick_hold_seconds = 10.0
        self.goalie_clear_mode = False
        self.goalie_clear_kick_phase = False
        self._clear_target_state = ClearTargetState()
        self._goalie_clear_target: ClearTarget | None = None
        self._kick_target_lock_world: np.ndarray | None = None
        self._kick_target_locked_at_sec: float = 0.0
        self._kick_target_switches: int = 0
        self._kick_target_last_reason: str = "none"
        # Last target produced by the approach states (GO/DRIBBLE); KICK freezes this.
        self._last_kick_target_world: np.ndarray | None = None
        self._kick_entry_confirm_ticks = {
            "go": 0,
            "dribble": 0,
        }
        self._ball_lost_confirm_ticks = 0
        self._kick_threat_pending_since_sec: float | None = None
        self._kick_threat_active_until_sec: float = 0.0
        self._kick_last_threat_opp_pos: np.ndarray | None = None

        self.own_half_field_localise_toggle_pub = self.create_publisher(Bool, "/own_half_field_localise_toggle", 10)

        self.behaviour_state_pub = self.create_publisher(String, "/behaviour/state", 2)
        self.behaviour_cmd_pub = self.create_publisher(Float32MultiArray, "/behaviour/cmd_vel", 2)
        self.behaviour_ball_pub = self.create_publisher(Float32MultiArray, "/behaviour/ball", 2)
        self.walk_to_pose_pub = self.create_publisher(PoseStamped, "/walk_to_pose_pose", 10)
        self.robot_comms_pub = self.create_publisher(RobotComms, "/robot_comms/to_peers", 1)
        self._last_robot_comms_pub_time = None
        self._action_cb_group = ReentrantCallbackGroup()
        self.rviz_goal_sub = None
        if self.walk_to_point_mode:
            self.rviz_goal_sub = self.create_subscription(
                PoseStamped,
                "/goal_pose",
                self.callback_walk_to_point_goal_pose,
                10,
                callback_group=self._action_cb_group,
            )
        self.kick_action_client = ActionClient(
            self, KickAction, "/kick", callback_group=self._action_cb_group
        )
        self._was_penalised = False

        states = {
            StateID.LOOK_FOR_BALL: LookForBallState(self),
            StateID.ASSIST: AssistState(self),
            StateID.BLOCKING: BlockingState(self),
            StateID.GO: GoState(self),
            StateID.DRIBBLE: DribbleState(self),
            StateID.DRIBBLE_CLEAR: DribbleClearState(self),
            StateID.KICK: (
                KickState(self)
                if KICK_MODE == "booster_kick"
                else StaticKickState(self)
            ),
            StateID.STAND: StandState(self),
            StateID.SET: SetState(self),
            StateID.MOVE_TO_READY: MoveToReadyPositionState(self),
            StateID.PRE_ENTER_FIELD: PreEnterFieldState(self),
            StateID.WALK_TO_POINT: WalkToPointState(self),
            StateID.WALK_TO_BALL_KICK: WalkToBallKickState(self),
        }
        initial_state = (
            StateID.WALK_TO_POINT
            if self.walk_to_point_mode
            else StateID.LOOK_FOR_BALL
        )
        self.sm = StateMachine(states, initial=initial_state)

        self._timer_cb_group = MutuallyExclusiveCallbackGroup()
        self.now = None
        self.timer = self.create_timer(
            1.0 / self.frequency, self.on_timer, callback_group=self._timer_cb_group
        )
        self._head = HeadController(
            self.command,
            rotate_head=self.adapter.rotate_head,
            read_pose=self.ws_node.read_head_pose,
            suppressed=self._head_control_suppressed,
            frequency=self.head_frequency,
            limits=HeadLimits(
                pitch_min=HEAD_PITCH_MIN,
                pitch_max=HEAD_PITCH_MAX,
                yaw_min=HEAD_YAW_MIN,
                yaw_max=HEAD_YAW_MAX,
                max_dt_sec=HEAD_CONTROL_MAX_DT_SEC,
            ),
            log_warning=lambda msg: self.get_logger().warning(
                msg, throttle_duration_sec=5.0
            ),
        )
        self._head.start()
        self.get_logger().info(
            f"Head control thread at {self.head_frequency:.1f} Hz "
            f"(behaviour at {self.frequency} Hz)"
        )
        
        self._snapshot_seq = 0
        self._snapshot_log_path: Path | None = None
        self._snapshot_log_file = None
        self._velocity_diag_log_path: Path | None = None
        self._velocity_diag_log_file = None

        self._velocity_diag_prev_pose: tuple[float, float, float] | None = None
        self._velocity_diag_prev_time_sec: float | None = None
        self._velocity_diag_vx_estimate: float | None = None
        self._velocity_diag_last_cmd_vx: float | None = None
        self._velocity_diag_body_move_sent = False

        if self.walk_to_point_mode:
            self.get_logger().info(
                "Walk-to-point mode enabled; enter 'x y [theta]' on stdin. "
                "Game-controller and ball-chase logic disabled."
            )
        self.get_logger().info("BallChaseStateMachineNode initialized.")

    def loco_enter_walk(self) -> None:
        self.arbiter.enter_walk()

    def has_walk_to_point_target(self) -> bool:
        with self._walk_to_point_lock:
            return self._walk_to_point_has_target

    def get_walk_to_point_target(self) -> tuple[float, float, float]:
        with self._walk_to_point_lock:
            return self._walk_to_point_target

    def update_walk_to_point_target(
        self, x: float, y: float, theta: float
    ) -> None:
        with self._walk_to_point_lock:
            self._walk_to_point_target = (float(x), float(y), float(theta))
            self._walk_to_point_has_target = True
        self.get_logger().info(
            f"Walk-to-point target updated -> ({x:.2f}, {y:.2f}, {theta:.2f})"
        )
        print(
            f"\033[93mWalk-to-point target -> "
            f"({x:.2f}, {y:.2f}, {theta:.2f})\033[0m"
        )

    def callback_walk_to_point_goal_pose(self, msg: PoseStamped) -> None:
        """Accept RViz2 '2D Goal Pose' messages as walk-to-point targets."""
        q = msg.pose.orientation
        theta = atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z),
        )
        frame_id = msg.header.frame_id or "unknown"
        if frame_id not in ("world", "map", ""):
            self.get_logger().warning(
                f"RViz walk-to-point goal is in frame '{frame_id}', using coordinates as world-frame",
                throttle_duration_sec=2.0,
            )
        self.update_walk_to_point_target(
            float(msg.pose.position.x),
            float(msg.pose.position.y),
            theta,
        )

    @property
    def wm(self):
        return self.ws.wm

    @property
    def game_state(self) -> int:
        return self.wm.gc_state
    
    @property
    def game_phase(self) -> int:
        return self.wm.gc_phase
    
    @property
    def set_play(self) -> int:
        return self.wm.set_play

    @property
    def kicking_team(self) -> int | None:
        return self.wm.kicking_team

    @property
    def role_decision(self) -> str:
        return self.ws.role

    @property
    def is_goalie(self) -> bool:
        return self.role_decision == "goalie" or self.player_number == 1

    def load_formation_config(self) -> dict | None:
        if compute_positions is None or resolve_formation_mode is None:
            self.get_logger().warn(
                "Formation backend import failed. Falling back to hardcoded ready positions."
            )
            return None

        try:
            with FORMATION_JSON_PATH.open("r", encoding="utf-8") as file:
                formation = json.load(file)
        except Exception as exc:
            self.get_logger().warn(
                f"Could not load formation file {FORMATION_JSON_PATH}: {exc}. "
                "Falling back to hardcoded ready positions."
            )
            return None

        self.get_logger().info(f"Loaded formation config: {FORMATION_JSON_PATH}")
        return formation

    def advertised_game_controller_state_for_formation(self) -> dict:
        # preventing entering normal play DURING READY when we do not have a kicking team yet
        kicking_team = self.wm.kicking_team
        if kicking_team is None and self.game_state == STATE_READY:
            kicking_team = 0

        return {
            "gamePhase": GC_PHASE_TO_FORMATION_STR.get(self.game_phase, "normal"),
            "state": GC_STATE_TO_FORMATION_STR.get(self.game_state, "initial"),
            "setPlay": GC_SET_PLAY_TO_FORMATION_STR.get(self.set_play, "none"),
            "firstHalf": True,
            "stopped": bool(self.wm.is_stopped),
            "ownTeamNumber": int(self.team_number),
            "kickingTeam": kicking_team,
        }

    def compute_formation_target_for_me(self) -> tuple[float, float] | None:
        if self.formation is None:
            return None
        if compute_positions is None or resolve_formation_mode is None:
            return None

        gc_state = self.advertised_game_controller_state_for_formation()
        advertised_mode, legacy_mode = resolve_formation_mode(gc_state)

        # if there's no available ball or we are moving to ready, use ball pos (0,0) 
        if self.game_state == STATE_READY:
            ball_x = 0.0
            ball_y = 0.0
        else:
            ball_x = self.wm.ball_global_x
            ball_y = self.wm.ball_global_y

        positions, warnings = compute_positions(
            game_controller_state=gc_state,
            advertised_state_mode=advertised_mode,
            legacy_mode=legacy_mode,
            ball={
                "x": ball_x,
                "y": ball_y,
            },
            robot_ids=[int(self.player_number)],
            active_players=int(self.active_players),
            formation=self.formation,
            field_dimensions=FORMATION_FIELD_DIMENSIONS,
        )

        for warning in warnings:
            self.get_logger().warn(warning)

        position = positions.get(str(self.player_number))
        if not position or not position.get("ok"):
            reason = position.get("reason") if position else "missing position"
            self.get_logger().warn(
                f"Formation target unavailable for player {self.player_number}: {reason}"
            )
            return None

        return float(position["x"]), float(position["y"])

    def say(self, message: str) -> None:
        self.speech_engine.say(message)
        self.speech_engine.runAndWait()

    def to_p_in_pi(self, angle: float) -> float:
        while angle > pi:
            angle -= 2 * pi
        while angle < -pi:
            angle += 2 * pi
        return angle

    def has_fresh_vision_ball(self) -> bool:
        return self.wm.has_fresh_vision_ball(
            self.ws.now_sec(),
            self.ws.vision_ball_timeout_sec,
        )

    def has_global_ball(self) -> bool:
        """Trusted field-frame ball for navigation (fused or fresh vision global)."""
        return self.ws.has_navigable_ball()

    def fused_ball_age_sec(self) -> float:
        return self.wm.fused_ball_age_sec(self.ws.now_sec())

    def can_look_at_fused_ball(self) -> bool:
        if self.has_fresh_vision_ball():
            return False
        if not self.has_global_ball() or not self.ws.ball_tracker_valid:
            return False
        return self.ws.fused_ball_age_sec() < self.head_fused_ball_memory_sec
    
    def robot_in_penalty(self) -> bool:
        return self.wm.robot_x > GOALIE_GOAL_X and self.wm.robot_x < GOALIE_GOAL_X + PENALTY_LENGTH_M and abs(self.wm.robot_y) < PENALTY_HALF_WIDTH

    def goalie_ball_xy(self) -> tuple[float, float]:
        vb = self.wm.vision_ball
        if self.has_fresh_vision_ball() and vb.has_global_position():
            return (vb.global_x, vb.global_y)
        return self.ball_global()

    def ball_in_penalty_area(self, willBeIn: float = 0.0) -> bool:
        bx, by = self.ball_global(willBeIn)
        return (
            GOALIE_GOAL_X < bx < GOALIE_GOAL_X + PENALTY_LENGTH_M
            and abs(by) < PENALTY_HALF_WIDTH
        )

    def ball_in_goalie_threat_zone(self, *, entering: bool) -> bool:
        if not self.has_global_ball() or self.ball_in_penalty_area():
            return self.has_global_ball() and self.ball_in_penalty_area()
        bx, _ = self.ball_global()
        approach_x = GOALIE_GOAL_X + PENALTY_LENGTH_M + (
            GOALIE_PENALTY_APPROACH_ENTER_M if entering else GOALIE_PENALTY_APPROACH_EXIT_M
        )
        if bx > approach_x:
            return False
        bvx, _ = self.ws.ball_velocity_global()
        return bvx < GOALIE_BALL_TOWARD_GOAL_VX

    def begin_goalie_clear(self) -> None:
        self.goalie_clear_mode = True
        if GOALIE_CLEAR_USE_GO_STATE:
            self._update_goalie_clear_target()

    def end_goalie_clear(self) -> None:
        self.goalie_clear_mode = False
        self.goalie_clear_kick_phase = False
        self._goalie_clear_target = None

    def goalie_should_clear(self) -> bool:
        if not self.has_global_ball():
            return False
        if self.ball_in_penalty_area() or self.ball_in_goalie_threat_zone(entering=True):
            return True
        return False

    def goalie_still_clearing(self) -> bool:
        """Exit hysteresis: stay clearing until ball is well out of the danger zone."""
        if not self.has_global_ball():
            return False
        if self.ball_in_penalty_area() or self.ball_in_goalie_threat_zone(entering=False):
            return True
        return False

    def _goalie_fully_blind(self) -> bool:
        if self.has_global_ball() or self.has_fresh_vision_ball():
            return False
        return not (
            self.ws.local_ball_tracker_valid
            and self._local_ball_tracker_age_sec() <= self.chase_ball_memory_sec()
        )

    def goalie_ball_lost_transition(self) -> StateID | None:
        if self.has_global_ball():
            self._ball_lost_confirm_ticks = 0
            return None
        if not self.confirmed_ball_lost_in_play():
            return None
        self.end_goalie_clear()
        blockpose = calculate_blocking_pose("goalie", self.ball_global(), self.ws.ball_velocity_global(), self.ws.fused_ball_age_sec())
        if self.robot_near_pose(blockpose[0], blockpose[1], blockpose[2], 0.10, 0.15):
            return StateID.LOOK_FOR_BALL
        return None if self.sm.current_id == StateID.BLOCKING else StateID.BLOCKING

    def goalie_after_clear_transition(self) -> StateID:
        self.end_goalie_clear()
        return StateID.BLOCKING if self._goalie_fully_blind() or self.has_global_ball() else StateID.LOOK_FOR_BALL

    def _goalie_clear_opponents(self) -> list[tuple[float, float]]:
        opponents: list[tuple[float, float]] = []
        now = self.ws.now_sec()
        for opp in self.wm.likely_opponents(now_sec=now, max_age_sec=KICK_OPPONENT_MAX_AGE_SEC):
            if opp.pose is not None:
                opponents.append((opp.pose.x, opp.pose.y))
        return opponents

    def _simple_clear_aim(self) -> np.ndarray:
        bx, by = self.ball_global()
        aim = pick_clear_direction(
            (bx, by),
            self.wm.robot_yaw,
            self._goalie_clear_opponents(),
        )
        return aim if aim is not None else self.sideline_clear_aim(by)

    def _update_goalie_clear_target(self) -> ClearTarget:
        if not self.has_global_ball():
            self._goalie_clear_target = ClearTarget(valid=False)
            return self._goalie_clear_target
        bx, by = self.ball_global()
        teammates: list[tuple[float, float]] = []
        now, timeout = self.ws.now_sec(), self.ws_node.peer_timeout_sec
        for pid, peer in self.wm.robot_peers_from_comms.items():
            if pid == self.player_number or peer.pose is None or (now - peer.last_seen_sec) > timeout:
                continue
            teammates.append((peer.pose.x, peer.pose.y))
        target, _ = calc_best_clear(
            ClearTargetInput(
                ball_xy=(bx, by),
                teammates=teammates,
                opponents=self._goalie_clear_opponents(),
            ),
            self._clear_target_state,
        )
        self._goalie_clear_target = target
        return target

    def refresh_goalie_clear_target(self) -> ClearTarget:
        """Recompute and cache the goalie clear target for the current ball."""
        return self._update_goalie_clear_target()

    def goalie_clear_aim_unit(self) -> np.ndarray:
        """Unit clear direction from the cached target, else the sideline aim."""
        target = self._goalie_clear_target
        if target is not None and target.valid:
            bx, by = self.ball_global()
            aim = np.array(
                [target.landing_xy[0] - bx, target.landing_xy[1] - by],
                dtype=float,
            )
            return self.unit_or_default(aim, self.sideline_clear_aim(by))
        return self.sideline_clear_aim()

    def goalie_clear_kick_goal_world(self, ball_pos: np.ndarray) -> np.ndarray:
        """World-frame aim point for the goalie clear, matching goalie_clear_aim_unit."""
        target = self._goalie_clear_target
        if target is not None and target.valid:
            return np.array(target.landing_xy, dtype=float)
        aim = self.sideline_clear_aim()
        return np.asarray(ball_pos, dtype=float) + aim * SIDELINE_CLEAR_GOAL_OFFSET_M

    def ball_in_own_goal(self) -> bool:
        """True when the ball is detected behind our own goal line, inside the goal mouth."""
        if not (self.has_global_ball() or self.ws.ball_tracker_valid):
            return False
        bx, by = self.ball_global()
        return bx < GOALIE_GOAL_X and abs(by) < GOAL_HALF_WIDTH_M

    def robot_in_own_goal(self) -> bool:
        """True when the robot is behind our own goal line, inside the goal mouth."""
        return self.wm.robot_x < GOALIE_GOAL_X and abs(self.wm.robot_y) < GOAL_HALF_WIDTH_M

    def ball_available_for_go(self) -> bool:
        return not self.ball_lost_in_play()

    def _local_ball_tracker_age_sec(self) -> float:
        tracker = self.ws.local_ball_tracker
        if not self.ws.local_ball_tracker_valid or tracker.last_measurement_sec is None:
            return float("inf")
        return max(0.0, self.ws.now_sec() - tracker.last_measurement_sec)

    def ball_lost_in_play(self) -> bool:
        memory_sec = (
            self.set_play_ball_memory_sec
            if self.set_play != 0
            else self.go_ball_memory_sec
        )
        if self.has_global_ball():
            return False
        if self.ws.has_fresh_fused_ball(memory_sec):
            return False
        if self.ws.local_ball_tracker_valid:
            return self._local_ball_tracker_age_sec() > memory_sec
        return True

    def confirmed_ball_lost_in_play(self) -> bool:
        if not self.ball_lost_in_play():
            self._ball_lost_confirm_ticks = 0
            return False
        self._ball_lost_confirm_ticks += 1
        if self._ball_lost_confirm_ticks >= BALL_LOST_CONFIRM_TICKS:
            self._ball_lost_confirm_ticks = 0
            return True
        return False

    def chase_ball_memory_sec(self) -> float:
        if self.set_play != 0:
            return self.set_play_ball_memory_sec
        return self.go_ball_memory_sec

    def dist_to_ball_global(self) -> float:
        if not (self.has_global_ball() or self.ws.ball_tracker_valid):
            return float("inf")
        ball_pos = self.ball_global_array()
        robot_pos = self.robot_position_array()
        return float(np.linalg.norm(ball_pos - robot_pos))

    def should_hold_head_near_ball(self) -> bool:
        if self.dist_to_ball_global() >= GO_HEAD_HOLD_DIST_M:
            return False
        memory_sec = self.chase_ball_memory_sec()
        return (
            self.has_global_ball() or
            self.ws.has_fresh_fused_ball(memory_sec) or
            self.ws.local_ball_tracker_valid
        )

    def hold_head_toward_last_ball(self) -> None:
        ball_pos = self.ball_global_array()
        vec = ball_pos - self.robot_position_array()
        local_x, local_y = self.world_vector_to_robot(vec, self.wm.robot_yaw)
        pitch_target = HEAD_PITCH_NEAR
        yaw_target = self.to_p_in_pi(atan2(local_y, local_x))
        self.command.set_head(
            pitch_target, yaw_target,
            speed_pitch=0.5, speed_yaw=0.5,
        )

    def fresh_teammate_poses(self) -> list[RobotPose]:
        now = self.ws.now_sec()
        timeout = self.ws_node.peer_timeout_sec
        poses: list[RobotPose] = [
            RobotPose(
                self.player_number,
                self.wm.robot_x,
                self.wm.robot_y,
                self.wm.robot_yaw,
            ),
        ]
        for pid, peer in self.wm.robot_peers_from_comms.items():
            if pid == self.player_number or peer.pose is None:
                continue
            if (now - peer.last_seen_sec) > timeout:
                continue
            poses.append(RobotPose(
                pid,
                peer.pose.x,
                peer.pose.y,
                peer.pose.theta,
            ))
        return poses

    def stale_ball_xy(self) -> tuple[float, float] | None:
        now = self.ws.now_sec()
        vision_xy = self.wm.stale_bounded_vision_ball_xy(now, max_age_sec=10.0)
        if vision_xy is not None:
            return vision_xy
        memory_sec = (
            self.set_play_ball_memory_sec
            if self.set_play != 0
            else self.go_ball_memory_sec
        )
        if self.ws.has_fresh_fused_ball(memory_sec):
            return self.ws.ball_global_at(0.0)
        return None

    def ball_global(self, dt: float = 0.0) -> tuple[float, float]:
        """Filtered/coasted fused global position (use for navigation)."""
        return self.ws.ball_global_at(dt)

    def ball_global_array(self, dt: float = 0.0) -> np.ndarray:
        return np.array(self.ball_global(dt))

    def best_kick_ball_position(self) -> np.ndarray | None:
        """Return the best global ball position for kick execution.

        Prefers live vision when available, otherwise falls back to fused/tracked ball.
        """
        live_ball = self.ws_node.wm.vision_ball
        if live_ball.has_global_position():
            return np.array([live_ball.global_x, live_ball.global_y], dtype=float)

        if self.has_global_ball() or self.ws.ball_tracker_valid:
            return self.ball_global_array()

        return None
    
    def dist_to_ball(self) -> float:
        ball_x, ball_y = self.ball_global()
        return sqrt((self.wm.robot_x - ball_x) ** 2 + (self.wm.robot_y - ball_y) ** 2)

    def robot_position_array(self) -> np.ndarray:
        return np.array([self.wm.robot_x, self.wm.robot_y])

    def goal_to_ball_vector(
        self, dt: float = 0.0, target_world: np.ndarray | None = None
    ) -> np.ndarray:
        ball_x, ball_y = self.ball_global(dt)
        if target_world is None:
            target_world = self.default_kick_target_world()
        return np.array([ball_x - target_world[0], ball_y - target_world[1]])
        

    def current_kick_target_world(
        self,
        *,
        ball_pos: np.ndarray | None = None,
        robot_pos: np.ndarray | None = None,
        ball_threatened: bool = False,
    ) -> np.ndarray:
        """Current dynamic target used by kick-direction selection."""
        if ball_pos is None:
            ball_pos = self.ball_global_array()
        if robot_pos is None:
            robot_pos = self.robot_position_array()

        # Own throw/kick or corner: aim in-field at the near-goal point
        if (
            self.set_play in (SET_PLAY_CORNER_KICK, SET_PLAY_THROW_IN)
            and self.kicking_team == self.team_number
        ):
            target_world = self.default_kick_target_world()
            self._last_kick_target_world = target_world
            return target_world

        if self.in_defend_zone(): # on my own half, if threatened, just go to the ball and move it
            if not ball_threatened:
                # kick forward
                target_world = np.array([GOAL_X, ball_pos[1]])
            else:
                robot_to_ball = ball_pos - robot_pos
                # if it is backwards, remove the x compoennts so it does not trying to kick the ball towards own goal
                if robot_to_ball[0] < 0:
                    robot_to_ball[0] = 0
                target_world = robot_to_ball / np.linalg.norm(robot_to_ball) * 3 + ball_pos
        else:
            opponents = self.wm.likely_opponents(
                now_sec=self.ws.now_sec(),
                max_age_sec=KICK_OPPONENT_MAX_AGE_SEC,
            )
            target_world, _ = self.select_kick_target_world(
                robot_pos,
                ball_pos,
                opponents,
                now_sec=self.ws.now_sec(),
            )
        self._last_kick_target_world = target_world
        return target_world
    

    def in_defend_zone(self) -> bool:
        defend_line_x = FIELD_LENGTH_M/2.0/3
        ball = self.ball_global()
        if ball[0] <= - defend_line_x:
            return True
        # center mid field.
        if abs(ball[1]) < FIELD_WIDTH_M/4.0 and ball[0] < 0 + defend_line_x:
            return True
        return False
    
    def robot_inside_field(self, margin: float) -> bool:
        return (
            abs(self.wm.robot_x) <= FIELD_LENGTH_M / 2.0 + margin and
            abs(self.wm.robot_y) <= FIELD_WIDTH_M / 2.0 + margin
        )
    
    def ensure_soccer_mode(self, timeout_sec: float = 3.0) -> None:
        self.arbiter.ensure_soccer_mode(timeout_sec)

    def enable_booster_visual_kick(self) -> None:
        self.ensure_soccer_mode()
        self.command.set_head_speed(speed_pitch=10)
        self.arbiter.request_visual_kick(True)

    def sideline_clear_aim(self, by: float | None = None) -> np.ndarray:
        """Unit direction toward the nearest touchline (+ small +x escape)."""
        if by is None:
            _, by = self.ball_global()
        if abs(by) < 0.05:
            side = 1.0 if self.wm.robot_y >= 0.0 else -1.0
        else:
            side = 1.0 if by >= 0.0 else -1.0
        return self.unit_or_default(np.array([0.2, side]), np.array([0.0, side]))

    def clear_dribble_pose(
        self,
        aim: np.ndarray | None = None,
    ) -> tuple[float, float, float, np.ndarray]:
        """Return walk-to target: approach behind the ball, then push through along aim."""
        bx, by = self.ball_global()
        if aim is None:
            aim = self._simple_clear_aim()

        ball = np.array([bx, by], dtype=float)
        behind = ball - aim * SIDELINE_CLEAR_STANDOFF_M

        return (
            float(behind[0]),
            float(behind[1]),
            atan2(aim[1], aim[0]),
            aim,
        )

    @staticmethod
    def unit_or_default(vector: np.ndarray, default: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vector)
        return vector / norm if norm > 1e-3 else default

    def world_vector_to_robot(self, vector: np.ndarray, robot_yaw: float) -> tuple[float, float]:
        local_x = vector[0] * cos(robot_yaw) + vector[1] * sin(robot_yaw)
        local_y = -vector[0] * sin(robot_yaw) + vector[1] * cos(robot_yaw)
        return local_x, local_y

    def goal_alignment_error(
        self,
        vec_robot_to_ball: np.ndarray,
        vec_goal_to_ball: np.ndarray,
    ) -> float:
        robot_to_ball_heading = atan2(vec_robot_to_ball[1], vec_robot_to_ball[0])
        ball_to_goal_heading = atan2(-vec_goal_to_ball[1], -vec_goal_to_ball[0])
        return self.to_p_in_pi(ball_to_goal_heading - robot_to_ball_heading)

    def default_kick_target_world(self) -> np.ndarray:
        if (self.set_play in (SET_PLAY_CORNER_KICK, SET_PLAY_THROW_IN) and self.kicking_team == self.team_number):
            # If we are the kicking team in a set play, aim for a point 1m forward of the goal.
            return np.array([GOAL_X - 1, GOAL_Y])
        return np.array([GOAL_X, GOAL_Y])

    @staticmethod
    def dynamic_kick_power(target_world: np.ndarray, robot_pos: np.ndarray) -> float:
        """Choose kick power from three distance bands to the target."""
        distance_to_target = float(np.linalg.norm(target_world - robot_pos))
        one_third = FIELD_LENGTH_M / 3.0
        two_thirds = 2.0 * one_third
        if distance_to_target > two_thirds:
            return KICK_POWER_FAR
        if distance_to_target > one_third:
            return KICK_POWER_MID
        return KICK_POWER_NEAR

    def kick_mouth_samples(self, n: int = GOAL_MOUTH_SAMPLES) -> list[np.ndarray]:
        ys = np.linspace(GOAL_MOUTH_Y_MIN, GOAL_MOUTH_Y_MAX, n)
        return [np.array([GOAL_X, float(y)]) for y in ys]

    @staticmethod
    def _perpendicular_left(unit_xy: np.ndarray) -> np.ndarray:
        return np.array([-unit_xy[1], unit_xy[0]])

    @staticmethod
    def _opponent_position(opponent: RobotObservation) -> np.ndarray | None:
        if opponent.pose is None:
            return None
        return np.array([opponent.pose.x, opponent.pose.y])

    def is_opponent_threatening_kick(
        self,
        robot_pos: np.ndarray,
        robot_yaw: float,
        ball_pos: np.ndarray,
        opp_pos: np.ndarray,
    ) -> bool:
        """Opponent around robot and closing the robot->ball lane."""
        vec_robot_to_opp = opp_pos - robot_pos
        vec_robot_to_ball = ball_pos - robot_pos
        if np.linalg.norm(vec_robot_to_opp) > KICK_OPPONENT_MAX_RANGE_M:
            return False

        opp_local_x, opp_local_y = self.world_vector_to_robot(vec_robot_to_opp, robot_yaw)
        if opp_local_x < KICK_OPPONENT_FRONT_MIN_X_M:
            return False

        robot_to_ball = np.linalg.norm(vec_robot_to_ball)
        if robot_to_ball < 1e-3:
            return True

        ball_line = vec_robot_to_ball / robot_to_ball
        perp = abs(
            vec_robot_to_opp[0] * ball_line[1] - vec_robot_to_opp[1] * ball_line[0]
        )
        if perp > KICK_OPPONENT_CORRIDOR_M:
            return False

        opp_to_ball = np.linalg.norm(opp_pos - ball_pos)
        proj_on_lane = float(np.dot(vec_robot_to_opp, ball_line))
        between_robot_and_ball = 0.0 < proj_on_lane < robot_to_ball
        near_ball = opp_to_ball < KICK_OPPONENT_BALL_RADIUS_M
        return between_robot_and_ball or near_ball

    def kick_dir_robot_rad(
        self,
        target_world: np.ndarray,
        ball_pos: np.ndarray,
        robot_yaw: float,
    ) -> float:
        """Kick impulse direction in robot frame (0 forward, positive left)."""
        vec_ball_to_target = target_world - ball_pos
        # lx, ly = self.world_vector_to_robot(vec_ball_to_target, robot_yaw)
        # return self.to_p_in_pi(atan2(ly, lx))
        return self.to_p_in_pi(atan2(vec_ball_to_target[1], vec_ball_to_target[0])-robot_yaw)

    def kick_target_side_cost(
        self,
        target_world: np.ndarray,
        ball_pos: np.ndarray,
        base_target: np.ndarray,
        opp_pos: np.ndarray | None,
        robot_yaw: float,
        is_threat: bool = False,
    ) -> float:
        """Lower cost = clearer lane, small lateral shift, minimal turn from current pose."""
        kick_vec = target_world - ball_pos
        kick_dist = float(np.linalg.norm(kick_vec))
        if kick_dist < 1e-3:
            return float("inf")

        kick_u = kick_vec / kick_dist
        if is_threat:
            rel = opp_pos - ball_pos
            perp_clearance = abs(rel[0] * kick_u[1] - rel[1] * kick_u[0])
            along = float(np.dot(rel, kick_u))

            block_cost = max(0.0, KICK_OPPONENT_CORRIDOR_M - perp_clearance) * 4.0
            if 0.0 <= along <= 2.5:
                block_cost += (2.5 - along) * 0.8
        goal_cost = float(np.linalg.norm(target_world - base_target)) * 6.0
        # Visual kick is fastest when the robot turns little: prefer small |dir| from current heading.
        execution_cost = (
            abs(self.kick_dir_robot_rad(target_world, ball_pos, robot_yaw))
            * KICK_EXECUTION_ANGLE_WEIGHT
        )

        # Open-field regime (no threat): accuracy is the only priority, so the aim must
        # settle on the best goal point. 1.5 weight for execution cost to ensure the aim is on the goal point.
        if not is_threat:
            block_cost = 0.0
            execution_cost = 1.5

        return block_cost + goal_cost + execution_cost

    def reset_kick_target_lock(self) -> None:
        self._kick_target_lock_world = None
        self._kick_target_locked_at_sec = 0.0
        self._kick_target_last_reason = "reset"

    def reset_kick_entry_gate(self) -> None:
        self._kick_entry_confirm_ticks["go"] = 0
        self._kick_entry_confirm_ticks["dribble"] = 0

    def confirmed_kick_entry(
        self,
        source: str,
        enter_condition: bool,
        exit_condition: bool,
    ) -> bool:
        if source not in self._kick_entry_confirm_ticks:
            self._kick_entry_confirm_ticks[source] = 0

        if exit_condition:
            self._kick_entry_confirm_ticks[source] = 0
            return False

        if not enter_condition:
            self._kick_entry_confirm_ticks[source] = 0
            return False

        self._kick_entry_confirm_ticks[source] += 1
        threshold = (
            GO_KICK_CONFIRM_TICKS
            if source == "go"
            else DRIBBLE_KICK_CONFIRM_TICKS
        )
        if self._kick_entry_confirm_ticks[source] >= threshold:
            if DEBUG:
                print(
                    f"\033[93mKick gate enter: source={source} "
                    f"ticks={self._kick_entry_confirm_ticks[source]}\033[0m"
                )
            self._kick_entry_confirm_ticks[source] = 0
            return True
        return False

    def select_kick_target_world(
        self,
        robot_pos: np.ndarray,
        ball_pos: np.ndarray,
        opponents: list[RobotObservation],
        *,
        now_sec: float,
        max_age_sec: float = KICK_OPPONENT_MAX_AGE_SEC,
    ) -> tuple[np.ndarray, bool]:
        """Pick world-frame kick target; bias to clearer side when blocked in front."""
        base_target = self.default_kick_target_world()
        robot_yaw = self.wm.robot_yaw
        candidates = self.kick_mouth_samples()

        threats: list[tuple[float, np.ndarray]] = []
        for opponent in opponents:
            if not opponent.is_fresh(now_sec, max_age_sec):
                continue
            opp_pos = self._opponent_position(opponent)
            if opp_pos is None:
                continue
            if not self.is_opponent_threatening_kick(robot_pos, robot_yaw, ball_pos, opp_pos):
                continue
            threats.append((float(np.linalg.norm(opp_pos - robot_pos)), opp_pos))

        raw_threat = len(threats) > 0
        if raw_threat:
            if self._kick_threat_pending_since_sec is None:
                self._kick_threat_pending_since_sec = now_sec
            if now_sec - self._kick_threat_pending_since_sec >= KICK_THREAT_PERSIST_SEC:
                self._kick_threat_active_until_sec = now_sec + KICK_THREAT_HOLD_SEC
            _, self._kick_last_threat_opp_pos = min(threats, key=lambda item: item[0])
        else:
            self._kick_threat_pending_since_sec = None

        threat_active = now_sec <= self._kick_threat_active_until_sec
        opp_pos = self._kick_last_threat_opp_pos if threat_active else None

        candidate_target = min(
            candidates,
            key=lambda target: self.kick_target_side_cost(
                target,
                ball_pos,
                base_target,
                opp_pos,
                robot_yaw,
                is_threat=threat_active and opp_pos is not None,
            ),
        )
        candidate_cost = self.kick_target_side_cost(
            candidate_target,
            ball_pos,
            base_target,
            opp_pos,
            robot_yaw,
            is_threat=threat_active and opp_pos is not None,
        )

        lock_expired = (
            self._kick_target_lock_world is None
            or (now_sec - self._kick_target_locked_at_sec) > KICK_TARGET_LOCK_SEC
        )
        if lock_expired:
            self._kick_target_lock_world = candidate_target
            self._kick_target_locked_at_sec = now_sec
            self._kick_target_last_reason = "new_lock"
        else:
            locked_target = self._kick_target_lock_world
            locked_cost = self.kick_target_side_cost(
                locked_target,
                ball_pos,
                base_target,
                opp_pos,
                robot_yaw,
                is_threat=threat_active and opp_pos is not None,
            )
            switched_target = (
                float(np.linalg.norm(candidate_target - locked_target))
                > KICK_TARGET_SAME_POINT_M
            )
            if switched_target:
                effective_candidate_cost = candidate_cost + KICK_TARGET_CHANGE_PENALTY
                if effective_candidate_cost + KICK_TARGET_SWITCH_MARGIN < locked_cost:
                    self._kick_target_lock_world = candidate_target
                    self._kick_target_locked_at_sec = now_sec
                    self._kick_target_switches += 1
                    self._kick_target_last_reason = "better_cost"
                else:
                    self._kick_target_last_reason = "hold_lock"
            else:
                self._kick_target_last_reason = "same_target"

        target_world = self._kick_target_lock_world
        if DEBUG:
            kick_dir = self.kick_dir_robot_rad(target_world, ball_pos, robot_yaw)
            opp_txt = "none"
            if opp_pos is not None:
                opp_txt = f"({opp_pos[0]:.2f},{opp_pos[1]:.2f})"
            print(
                f"\033[93mKick target: lock={self._kick_target_last_reason} "
                f"threat_raw={raw_threat} threat_active={threat_active} "
                f"switches={self._kick_target_switches} dir={kick_dir:.2f} opp={opp_txt}\033[0m"
            )
        return target_world, threat_active
    
    def publish_debug_pose(self, x: float, y: float, theta: float) -> None:
        if not DEBUG:
            return
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "world"
        msg.pose.position.x = float(x)
        msg.pose.position.y = float(y)
        msg.pose.orientation.z = sin(theta / 2.0)
        msg.pose.orientation.w = cos(theta / 2.0)
        self.walk_to_pose_pub.publish(msg)

    def robot_near_pose(
        self,
        x_target: float,
        y_target: float,
        theta_target: float,
        distance_tolerance: float,
        theta_tolerance: float,
    ) -> bool:
        r = sqrt(
            (x_target - self.wm.robot_x) ** 2 + (y_target - self.wm.robot_y) ** 2
        )
        heading_err = abs(self.to_p_in_pi(self.wm.robot_yaw - theta_target))
        return r < distance_tolerance and heading_err < theta_tolerance

    def robot_pose2(self) -> Pose2:
        if self.wm.self_pose is not None:
            return self.wm.self_pose
        return Pose2()

    def avoid_obstacle_points(self) -> tuple[tuple[float, float], ...]:
        now = self.ws.now_sec()
        points: list[tuple[float, float]] = []
        for opp in self.wm.likely_opponents(now_sec=now, max_age_sec=2.0):
            if opp.pose is None:
                continue
            points.append((float(opp.pose.x), float(opp.pose.y)))
        return tuple(points)

    def navigation_obstacles(
        self,
        *,
        extra: list | None = None,
    ) -> list[np.ndarray]:
        """World-frame obstacle centres for navigation (vision humanoids + optional extras)."""
        obs: list[np.ndarray] = []
        for obstacle in self.wm.path_planning_obstacles():
            if obstacle.pose is not None:
                obs.append(np.array([obstacle.pose.x, obstacle.pose.y], dtype=float))
        if extra:
            for item in extra:
                pt = np.asarray(item, dtype=float)
                obs.append(pt[:2].copy())
        return obs

    def refresh_snapshot(self) -> bool:
        self.ws = self.ws_node.snapshot()
        if not self.wm.has_pose:
            self.get_logger().info("Waiting for Pose...", throttle_duration_sec=5.0)
            return False
        return True

    def is_ball_search_head_scanning(self) -> bool:
        if self.sm.current_id != StateID.LOOK_FOR_BALL:
            return False
        if self.is_goalie:
            return False
        return True

    def update_vision_ball_freshness(self) -> None:
        if self.is_ball_search_head_scanning():
            return
        if not self.has_fresh_vision_ball() and self.ball_lost_in_play():
            self.cmd_index = 0

    def update_head_command_search(self) -> None:
        """cmd_sequence left-right sweep only (no vision/fused look-ahead)."""
        pitch_target, yaw_target = self.cmd_sequence[self.cmd_index]
        self.command.set_head(pitch_target, yaw_target, speed_yaw=10.0)
        if (
            abs(self.ws.me.head_pitch - pitch_target) < 0.1 and
            abs(self.ws.me.head_yaw - yaw_target) < 0.1
        ):
            self.cmd_index = (self.cmd_index + 1) % len(self.cmd_sequence)

    def update_head_command(self, speed_yaw_scale: float = 1.0, speed_pitch_scale: float = 1.0) -> bool:
        pixel_xy = self.wm.vision_ball.pixel_xy()
        if self.has_fresh_vision_ball() and pixel_xy is not None:
            delta_x = pixel_xy[0] - CAM_PIX_X / 2
            delta_y = pixel_xy[1] - CAM_PIX_Y / 2
            ball_in_center = (
                abs(delta_x) < CENTER_PX_TOLERANCE and
                abs(delta_y) < CENTER_PY_TOLERANCE
            )
            if not ball_in_center:
                norm_x = abs(delta_x) / (CAM_PIX_X / 2.0)
                speed_range = HEAD_TRACK_SPEED_MAX - HEAD_TRACK_SPEED_MIN
                speed_yaw = float(np.clip(
                    HEAD_TRACK_SPEED_MIN + norm_x * speed_range,
                    HEAD_TRACK_SPEED_MIN,
                    HEAD_TRACK_SPEED_MAX,
                ))
                speed_pitch = 0.7
                yaw_target = self.ws.me.head_yaw - delta_x / CAM_PIX_X * CAM_ANGLE_X
                pitch_target = self.ws.me.head_pitch + delta_y / CAM_PIX_Y * CAM_ANGLE_Y
                self.command.set_head(
                    pitch_target, yaw_target,
                    speed_pitch=speed_pitch * speed_pitch_scale, speed_yaw=speed_yaw * speed_yaw_scale,
                )
            return ball_in_center

        if self.can_look_at_fused_ball():
            print("looking at fused ball")
            ball_pos = self.ball_global_array(0.5)
            vec = ball_pos - self.robot_position_array()
            local_x, local_y = self.world_vector_to_robot(vec, self.wm.robot_yaw)
            dist = sqrt(local_x ** 2 + local_y ** 2)
            pitch_target = (
                HEAD_PITCH_MAX if dist < HEAD_PITCH_NEAR_BALL_M else HEAD_PITCH_MIN
            )
            yaw_target = self.to_p_in_pi(atan2(local_y, local_x))
            yaw_err = abs(self.to_p_in_pi(yaw_target - self.ws.me.head_yaw))
            speed_yaw = float(np.clip(
                HEAD_TRACK_SPEED_MIN + yaw_err * 2.0,
                HEAD_TRACK_SPEED_MIN,
                HEAD_TRACK_SPEED_MAX,
            ))
            self.command.set_head(
                pitch_target, yaw_target,
                speed_pitch=0.7, speed_yaw=speed_yaw,
            )
            return False

        pitch_target, yaw_target = self.cmd_sequence[self.set_scan_index]
        if (
            abs(self.ws.me.head_pitch - pitch_target) < 0.1 and
            abs(self.ws.me.head_yaw - yaw_target) < 0.1
        ):
            self.set_scan_index = (self.set_scan_index + 1) % len(self.cmd_sequence)
            pitch_target, yaw_target = self.cmd_sequence[self.set_scan_index]
        self.command.set_head(pitch_target, yaw_target, speed_yaw = 2.0)
        return False
    
    def apply_game_controller_constraints(self) -> None:
        self.kicking_off = False
        if self.walk_to_point_mode:
            if self.sm.current_id != StateID.WALK_TO_POINT:
                self.sm.force_transition(StateID.WALK_TO_POINT)
            return
        if self.wm.is_penalised or self.game_state == STATE_INITIAL:
            self.need_scan_for_localisation = True
        if self._was_penalised and not self.wm.is_penalised:
            self.need_scan_for_localisation = True
            self.get_logger().info("Returned from penalty -> PRE_ENTER_FIELD re-localise")
        self._was_penalised = self.wm.is_penalised

        if self.game_phase in (GAME_PHASE_NORMAL, GAME_PHASE_EXTRA_TIME):
            if self.game_state in (STATE_INITIAL, STATE_FINISHED) or self.wm.is_stopped or self.wm.is_penalised:
                self.sm.force_transition(StateID.STAND)
            elif self.need_scan_for_localisation:
                self.sm.force_transition(StateID.PRE_ENTER_FIELD)
            elif self.game_state == STATE_READY:
                self.sm.force_transition(StateID.MOVE_TO_READY)
            elif self.game_state == STATE_SET:
                self.sm.force_transition(StateID.SET)
            elif self.game_state == STATE_PLAYING:
                if self.wm.game.kicking_team == None:
                    if self.sm.current_id in (StateID.SET, StateID.STAND, StateID.MOVE_TO_READY, StateID.PRE_ENTER_FIELD) and not self.need_scan_for_localisation:
                        self.sm.force_transition(StateID.LOOK_FOR_BALL)
                else:
                    # there is a kick team, it is a setplay or kickoff
                    if self.set_play == SET_PLAY_NONE: # kickoff
                        if self.wm.game.kicking_team == self.wm.game.team_number:
                            if not self.wm.ball_moved_since_set:
                                print("kicking")
                                self.kicking_off = True
                            if self.sm.current_id in (StateID.SET, StateID.STAND, StateID.MOVE_TO_READY, StateID.PRE_ENTER_FIELD) and not self.need_scan_for_localisation:
                                self.sm.force_transition(StateID.LOOK_FOR_BALL)
                        else:
                            print("opponent kicking")
                            # opponent kick team, we are the set
                            self.sm.force_transition(StateID.SET)
                    else: # setplay
                        if self.wm.game.kicking_team == self.wm.game.team_number:
                            print("kicking in setplay")
                            if self.sm.current_id in (StateID.SET, StateID.STAND, StateID.MOVE_TO_READY):
                                self.sm.force_transition(StateID.LOOK_FOR_BALL)
                        else:
                            print("opponent kicking")
                            if self.is_goalie:
                                self.sm.force_transition(StateID.BLOCKING)
                            else:
                                self.sm.force_transition(StateID.ASSIST)
            else:
                self.sm.force_transition(StateID.STAND)
        elif self.game_phase == GAME_PHASE_PENALTY_SHOOT_OUT:
            # TODO: WE NEED A PENALTY SHOOT OUT BEHAVIOUR STACK
            # THE KICKING HALF IS KNOWN
            # KICKER IS SELECTED
            # KICKER WALKS UP TO BALL
            # KICKS IT IDK
            # GOALIE IS SELECTED
            # IDK
            self.sm.force_transition(StateID.STAND)
        elif self.game_phase == GAME_PHASE_TIMEOUT:
            # just stand still during a timeout
            self.sm.force_transition(StateID.STAND)
        else:
            self.sm.force_transition(StateID.STAND)

    def apply_role_decision(self) -> None:
        """Centralised GO vs ASSIST dispatcher for the active play states.

        States outside (STAND/SET/MOVE_TO_READY/KICK/LOOK_FOR_BALL) own their
        own transitions (game-controller constraints, kick-eligibility, ball
        search) — we only flip GO <-> ASSIST here based on the sticky role
        decided by ``WorldStateNode``.
        """
        if self.walk_to_point_mode:
            return
        if self.is_goalie:
            return
        if self.game_state != STATE_PLAYING:
            return
        if self.sm.current_id not in (StateID.GO, StateID.ASSIST, StateID.DRIBBLE):
            return
        if self.role_decision == "chase" and self.sm.current_id == StateID.ASSIST:
            self.sm.force_transition(StateID.GO)
        elif self.role_decision == "assist" and self.sm.current_id in (StateID.GO, StateID.DRIBBLE):
            self.sm.force_transition(StateID.ASSIST)

    def enter_kick_conditionally(self) -> None:
        if (self.game_state != STATE_PLAYING):
            return
        if self.is_goalie and not self.goalie_clear_mode:
            return
        # TODO: Revisit wheather this may potentially violet rules
        # if I am stand still, probably I am penalised or global stop called
        if self.sm.current_id == StateID.STAND:
            return

        if self.ball_global_array()[0] == 0.0 and self.ball_global_array()[1] == 0.0:
            return
        ball_dist = np.linalg.norm(self.ball_global_array() - self.robot_position_array())
        ball_pos = self.ball_global_array()
        robot_pos = self.robot_position_array()
        target_world = self.current_kick_target_world(ball_pos=ball_pos, robot_pos=robot_pos)
        error_kicking = self.goal_alignment_error(
            ball_pos - robot_pos,
            self.goal_to_ball_vector(target_world=target_world),
        )
        if error_kicking < 1.4 and ball_dist < 0.9 and self.role_decision != "assist": # mabye assisters can also kick the ball idk
            self.sm.force_transition(StateID.KICK)
    
    def send_info_to_peers(self, rate_hz: float = 2.0) -> None:
        if rate_hz <= 0.0:
            return

        now = self.get_clock().now()
        min_period_sec = 1.0 / rate_hz
        if self._last_robot_comms_pub_time is not None:
            elapsed = (now - self._last_robot_comms_pub_time).nanoseconds / 1e9
            if elapsed < min_period_sec:
                return

        local_tracker = self.ws.local_ball_tracker
        px, py = local_tracker.position_at(0.0)
        vx, vy = local_tracker.velocity_at()

        msg = RobotComms()
        msg.team_number = self.wm.game.team_number
        msg.player_number = self.wm.game.player_id
        msg.pos_x = self.wm.robot_x
        msg.pos_y = self.wm.robot_y
        msg.heading = self.wm.robot_yaw

        msg.ball_valid = bool(local_tracker.valid)
        if local_tracker.valid:
            msg.global_ball_x = float(px)
            msg.global_ball_y = float(py)
            msg.global_ball_vx = float(vx)
            msg.global_ball_vy = float(vy)
        else:
            msg.global_ball_x = 0.0
            msg.global_ball_y = 0.0
            msg.global_ball_vx = 0.0
            msg.global_ball_vy = 0.0

        msg.going_for_ball = self.sm.current_id in (StateID.GO, StateID.KICK)

        self.robot_comms_pub.publish(msg)
        self._last_robot_comms_pub_time = now
        
    def on_timer(self) -> None:
        now = time.monotonic()
        if self.now is not None:
            elapsed = now - self.now
            self.tick_rate_window.append(1.0 / elapsed)
            if len(self.tick_rate_window) == self.tick_rate_window.maxlen:
                self.tick_rate_window.popleft()
            self.avg_tick_rate = sum(self.tick_rate_window) / len(self.tick_rate_window)
            bigbrother.log_behaviour_tick_rate(self.avg_tick_rate)
        self.now = now
        self.behaviour_state_pub.publish(String(data=self.sm.current_id.name))

        if not self.refresh_snapshot():
            return

        try:
            ball_x, ball_y = self.ball_global()
            ball_valid = 1.0 if (self.has_global_ball() or self.ws.ball_tracker_valid) else 0.0
            self.behaviour_ball_pub.publish(Float32MultiArray(data=[
                float(ball_x), float(ball_y), ball_valid,
                float(self.fused_ball_age_sec()),
            ]))
        except Exception:
            pass

        self.update_velocity_diagnostic_estimate()
        self.command.reset()
        self._velocity_diag_body_move_sent = False
        self.update_vision_ball_freshness()
        self.send_info_to_peers()

        self.apply_game_controller_constraints()
        self.apply_role_decision()
        #self.enter_kick_conditionally()
        
        self.sm.tick()
        self.execute_commands()
        self.log_velocity_diagnostic()


    def update_velocity_diagnostic_estimate(self) -> None:
        now_sec = float(self.ws.now_sec())
        pose = (
            float(self.wm.robot_x),
            float(self.wm.robot_y),
            float(self.wm.robot_yaw),
        )
        prev_pose = self._velocity_diag_prev_pose
        prev_time_sec = self._velocity_diag_prev_time_sec
        self._velocity_diag_prev_pose = pose
        self._velocity_diag_prev_time_sec = now_sec
        if prev_pose is None or prev_time_sec is None:
            return

        dt = now_sec - prev_time_sec
        if dt < VELOCITY_DIAG_MIN_DT_SEC or dt > VELOCITY_DIAG_MAX_DT_SEC:
            self._velocity_diag_vx_estimate = None
            return

        dx = pose[0] - prev_pose[0]
        dy = pose[1] - prev_pose[1]
        vx_world = dx / dt
        vy_world = dy / dt
        vx_robot = vx_world * cos(pose[2]) + vy_world * sin(pose[2])
        if self._velocity_diag_vx_estimate is None:
            self._velocity_diag_vx_estimate = vx_robot
        else:
            alpha = VELOCITY_DIAG_FILTER_ALPHA
            self._velocity_diag_vx_estimate = (
                alpha * vx_robot + (1.0 - alpha) * self._velocity_diag_vx_estimate
            )

    def log_velocity_diagnostic(self) -> None:
        command_vx = float(self.command.x)
        achieved_vx = self._velocity_diag_vx_estimate
        previous_command_vx = self._velocity_diag_last_cmd_vx
        command_sign_flipped = (
            previous_command_vx is not None
            and abs(previous_command_vx) > VELOCITY_DIAG_CMD_SIGN_EPS
            and abs(command_vx) > VELOCITY_DIAG_CMD_SIGN_EPS
            and previous_command_vx * command_vx < 0.0
        )
        actual_lags_command = (
            achieved_vx is not None
            and abs(command_vx) > VELOCITY_DIAG_CMD_SIGN_EPS
            and (
                command_vx * achieved_vx <= 0.0
                or abs(achieved_vx) < 0.7 * abs(command_vx)
            )
        )
        record = {
            "timestamp_sec": float(self.ws.now_sec()),
            "seq": int(self._snapshot_seq),
            "state": self.sm.current_id.name,
            "body_move_sent": bool(self._velocity_diag_body_move_sent),
            "command_vx_mps": command_vx,
            "achieved_vx_mps": None if achieved_vx is None else float(achieved_vx),
            "vx_lag_mps": None if achieved_vx is None else float(command_vx - achieved_vx),
            "command_sign_flipped": bool(command_sign_flipped),
            "actual_lags_command": bool(actual_lags_command),
        }
        if self._velocity_diag_log_file is not None:
            self._velocity_diag_log_file.write(
                json.dumps(record, separators=(",", ":")) + "\n"
            )

        if achieved_vx is not None and (
            abs(command_vx) > VELOCITY_DIAG_CMD_SIGN_EPS or command_sign_flipped
        ):
            self.get_logger().info(
                "vx_diag "
                f"cmd={command_vx:+.2f}m/s "
                f"ach={achieved_vx:+.2f}m/s "
                f"lag={command_vx - achieved_vx:+.2f}m/s "
                f"flip={int(command_sign_flipped)} "
                f"lagging={int(actual_lags_command)}",
                throttle_duration_sec=0.5,
            )
        self._velocity_diag_last_cmd_vx = command_vx



    def stop_head_control(self) -> None:
        self._head.stop()

    def _head_control_suppressed(self) -> bool:
        if self.wm.has_fallen and self.wm.recovery_available and not self.wm.is_stopped:
            return True
        return self.sm.current_id == StateID.STAND or self.wm.is_penalised

    def obs_avoid(self, cmd_x: float, cmd_y: float, cmd_theta: float) -> tuple[float, float, float]:
        protect_ball = None
        if self.sm.current_id == StateID.WALK_TO_BALL_KICK:
            kick_ball_pos = self.best_kick_ball_position()
            if kick_ball_pos is not None:
                protect_ball = (float(kick_ball_pos[0]), float(kick_ball_pos[1]))
        return avoid_opponents(
            self.robot_pose2(),
            cmd_x,
            cmd_y,
            cmd_theta,
            self.avoid_obstacle_points(),
            protect_ball=protect_ball,
        )

    def _on_walk_send(self, x: float, y: float, theta: float) -> None:
        bigbrother.log_cmd_velocity(
            x,
            y,
            theta,
            robot_x=self.wm.robot_x,
            robot_y=self.wm.robot_y,
            robot_yaw=self.wm.robot_yaw,
        )

    def execute_commands(self) -> None:
        inp = ArbiterInput(
            has_fallen=bool(self.wm.has_fallen),
            recovery_available=bool(self.wm.recovery_available),
            is_stopped=bool(self.wm.is_stopped),
            is_penalised=bool(self.wm.is_penalised),
            force_stop=(
                self.sm.current_id == StateID.STAND or bool(self.wm.is_penalised)
            ),
            skip_body=self.sm.current_id == StateID.SET,
            suppress_body=(
                self.sm.current_id == StateID.KICK or self.goalie_clear_kick_phase
            ),
        )
        recovering = inp.has_fallen and inp.recovery_available and not inp.is_stopped
        if (
            not recovering
            and not inp.force_stop
            and not self.command.avoidance_applied
        ):
            self.command.x, self.command.y, self.command.theta = self.obs_avoid(
                self.command.x, self.command.y, self.command.theta
            )
        result = self.arbiter.execute(self.command, inp)
        self._velocity_diag_body_move_sent = bool(
            result.body_move_sent and result.reason == "walk"
        )
        if result.published_cmd is not None:
            self.behaviour_cmd_pub.publish(
                Float32MultiArray(data=list(result.published_cmd))
            )

def _walk_to_point_stdin_loop(node: BallChaseStateMachineNode) -> None:
    """Read 'x y [theta]' lines from stdin and update the walk-to-point target."""
    print(
        "Walk-to-point: enter 'x y [theta]' per line "
        "(world frame, metres; theta in radians, default 0)."
    )
    while rclpy.ok():
        try:
            line = sys.stdin.readline()
        except Exception:
            break
        if not line:
            break
        parts = line.strip().split()
        if not parts or parts[0].startswith("#"):
            continue
        try:
            x = float(parts[0])
            y = float(parts[1])
            theta = float(parts[2]) if len(parts) > 2 else 0.0
        except (IndexError, ValueError):
            print("Expected: x y [theta]")
            continue
        node.update_walk_to_point_target(x, y, theta)


# might want to use a launch file in the future
def load_robot_config() -> tuple[int, int]:
    config_path = (
        Path(__file__).resolve().parents[2]
        / "communication"
        / "config"
        / "robot.yaml"
    )

    print(config_path)

    with open(config_path, "r") as f:
        data = yaml.safe_load(f)

    params = data["robot_comms"]["ros__parameters"]

    team_number = int(params["team_number"])
    player_number = int(params["player_number"])

    print(f"Loaded robot config: team {team_number}, player {player_number}")

    return team_number, player_number

def main() -> None:
    parser = argparse.ArgumentParser()

    # Defaults to True if user does not specify
    parser.add_argument(
        "--gc_listening",
        type=lambda x: str(x).lower() in ("true", "1", "yes", "y"),
        default=True,
        help="Enable GameController listening (default: True)",
    )

    parser.add_argument(
        "--walk-to-point",
        action="store_true",
        help=(
            "Walk to world-frame poses from RViz2 /goal_pose or stdin. Enter "
            "'x y [theta]' lines on stdin to set or update the target."
        ),
    )
    if not _NAV_AVAILABLE:
        print(
            "Tracker navigation requires skills.navigate_to_pose "
            "(navigation_planner / path_tracker / se2_planner).",
            file=sys.stderr,
        )
        sys.exit(1)

    args = parser.parse_args()

    team_number, player_number = load_robot_config()
    if not rclpy.ok():
        rclpy.init()
    adapter = create_booster_adapter()
    time.sleep(2)

    world_state = WorldStateNode(
        team_number=team_number,
        player_id=player_number,
        gc_listening=args.gc_listening,
    )
    sm_node = BallChaseStateMachineNode(
        adapter,
        world_state,
        walk_to_point_mode=args.walk_to_point,
    )


    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(world_state)
    executor.add_node(sm_node)

    if args.walk_to_point:
        threading.Thread(
            target=_walk_to_point_stdin_loop,
            args=(sm_node,),
            name="walk_to_point_stdin",
            daemon=True,
        ).start()

    spin_thread: threading.Thread | None = None
    try:
        executor.spin()
    except KeyboardInterrupt:
        sm_node.arbiter.shutdown_stop()
        print("\nRobot Stopped Safely.")
    finally:
        sm_node.stop_head_control()
        executor.shutdown()
        if spin_thread is not None:
            spin_thread.join(timeout=2.0)
        sm_node.destroy_node()
        world_state.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

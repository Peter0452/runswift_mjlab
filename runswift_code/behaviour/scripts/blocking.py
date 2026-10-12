from __future__ import annotations

from math import atan2, copysign, hypot, pi, radians, tan
from typing import NamedTuple

from legacy_world_model import FIELD_LENGTH_M, GOAL_WIDTH_M

GOALIE_GOAL_X = -FIELD_LENGTH_M / 2.0
GOALIE_GOAL_Y = 0.0
GOALIE_GOAL_HALF_WIDTH = GOAL_WIDTH_M / 2.0
GOALPOST_LEFT_Y = GOAL_WIDTH_M / 2.0
GOALPOST_RIGHT_Y = -GOAL_WIDTH_M / 2.0
GOAL_AREA_DEPTH = 0.5
OPENING_ANGLE_MIN = radians(2.0)
MIN_OFFSET_FROM_GOAL_LINE = 0.1

# Walk-command shaping while moving to the blocking position on the line: damp forward
# motion and emphasise strafing so the goalie slides along the line to track the ball.
GOALIE_TRACK_FORWARD_SCALE = 0.2
GOALIE_TRACK_STRAFE_SCALE = 4.0
# Beyond this x-distance forward of our own goal line, walk normally (no scaling) so we
# get back to the line quickly rather than crawling forward.
GOALIE_NORMAL_WALK_X_DIST_M = 1.0


class BlockingPose(NamedTuple):
    x: float
    y: float
    theta: float
    forward_scale: float
    strafe_scale: float

# Trajectory-blend tuning
W_SPEED_VMIN = 0.05       # m/s — below this, no trajectory weight
W_SPEED_VMAX = 1.0       # m/s — at/above this, full speed weight
W_AIM_MARGIN = 0.4       # m — crossing may exit the goal mouth by this much before w_aim hits 0
W_CONF_FRESH_SEC = 0.3   # s — ball estimate older than this decays w_conf to 0


def calculate_blocking_pose(role: str, ball_pos: tuple[float, float], velocity: tuple[float, float] | None = None, ball_age_sec: float = 0.0, use_bisector: bool = True, robot_pos: tuple[float, float] | None = None) -> BlockingPose | None:
    if role != "goalie":
        return None
    clamped = _clamp_ball(ball_pos)
    if use_bisector and (aim := _aim_angle_to_post_bisector(clamped)) is not None:
        base_pose = _pose_on_defending_line(clamped, ball_pos, aim, defending_depth(role))
    else:
        base_pose = _pose_on_defending_line(clamped, ball_pos, _aim_angle_to_goal_center(clamped), defending_depth(role))
    x, y, theta = _blend_with_trajectory(role, ball_pos, velocity, ball_age_sec, base_pose)
    forward_scale, strafe_scale = GOALIE_TRACK_FORWARD_SCALE, GOALIE_TRACK_STRAFE_SCALE
    # When we are well forward of our own goal line, walk normally so we can return quickly
    # instead of crawling back with the forward-damped tracking gait.
    if robot_pos is not None and (robot_pos[0] - GOALIE_GOAL_X) > GOALIE_NORMAL_WALK_X_DIST_M:
        forward_scale, strafe_scale = 1.0, 1.0
    return BlockingPose(x, y, theta, forward_scale, strafe_scale)


def defending_depth(role: str) -> float:
    return GOAL_AREA_DEPTH if role == "goalie" else 1.0


def _angle_between_vectors(v1: tuple[float, float], v2: tuple[float, float]) -> float:
    return atan2(v1[1] * v2[0] - v1[0] * v2[1], v1[0] * v2[0] + v1[1] * v2[1])


def to_p_in_pi(angle: float) -> float:
    return (angle + pi) % (2 * pi) - pi


def _subtract(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return (a[0] - b[0], a[1] - b[1])


def _norm(v: tuple[float, float]) -> float:
    return hypot(v[0], v[1])


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _clamp_ball(ball_pos: tuple[float, float]) -> tuple[float, float]:
    bx, by = ball_pos
    return max(bx, GOALIE_GOAL_X + MIN_OFFSET_FROM_GOAL_LINE), by if abs(by) < GOALIE_GOAL_HALF_WIDTH else copysign(GOALIE_GOAL_HALF_WIDTH, by)


def _aim_angle_to_goal_center(clamped_ball: tuple[float, float]) -> float:
    return atan2(GOALIE_GOAL_Y - clamped_ball[1], GOALIE_GOAL_X - clamped_ball[0])


def _aim_angle_to_post_bisector(clamped_ball: tuple[float, float]) -> float | None:
    v_l = _subtract((GOALIE_GOAL_X, GOALPOST_LEFT_Y), clamped_ball)
    v_r = _subtract((GOALIE_GOAL_X, GOALPOST_RIGHT_Y), clamped_ball)
    if _norm(v_l) < 1e-6 or _norm(v_r) < 1e-6:
        return None
    opening = max(abs(_angle_between_vectors(v_l, v_r)), OPENING_ANGLE_MIN)
    return atan2(v_l[1], v_l[0]) + opening / 2.0


def _pose_on_defending_line(clamped_ball: tuple[float, float], ball_pos: tuple[float, float], aim_angle: float, depth: float) -> tuple[float, float, float]:
    bx, by = clamped_ball
    x, y = GOALIE_GOAL_X + depth, by + (GOALIE_GOAL_X + depth - bx) * tan(aim_angle)
    return x, y, to_p_in_pi(atan2(ball_pos[1] - y, ball_pos[0] - x))


def _crossing_y_on_line(ball_pos: tuple[float, float], velocity: tuple[float, float], line_x: float) -> float | None:
    bx, by = ball_pos
    vx, vy = velocity
    if abs(vx) < 1e-6:
        return None
    return by + (vy / vx) * (line_x - bx)


def _w_speed(speed: float) -> float:
    # prefer using bisector/goal_center when the ball is slow, prediction only tends to solve long kicks
    return _clamp((speed - W_SPEED_VMIN) / (W_SPEED_VMAX - W_SPEED_VMIN), 0.0, 1.0)


def _w_aim(crossing_y_goal: float) -> float:
    over = abs(crossing_y_goal) - GOALIE_GOAL_HALF_WIDTH
    if over <= 0.0:
        return 1.0
    return _clamp(1.0 - over / W_AIM_MARGIN, 0.0, 1.0)


# def _w_conf(ball_age_sec: float) -> float:
#     # freshness decay
#     return _clamp(1.0 - ball_age_sec / W_CONF_FRESH_SEC, 0.0, 1.0)


def _blend_with_trajectory(role: str, ball_pos: tuple[float, float], velocity: tuple[float, float] | None, ball_age_sec: float, base_pose: tuple[float, float, float]) -> tuple[float, float, float]:
    # the bisector/goal-center pose as base pose, add in ball trajectory prediction
    x, base_y, _ = base_pose
    if velocity is None:
        return base_pose
    speed = _norm(velocity)
    if speed == 0.0:
        return base_pose

    crossing_y_def = _crossing_y_on_line(ball_pos, velocity, GOALIE_GOAL_X + defending_depth(role))
    crossing_y_goal = _crossing_y_on_line(ball_pos, velocity, GOALIE_GOAL_X)
    if crossing_y_def is None or crossing_y_goal is None:
        return base_pose

    w = _clamp(_w_speed(speed) * _w_aim(crossing_y_goal), 0.0, 1.0)
    if w == 0.0:
        return base_pose

    target_y = (1.0 - w) * base_y + w * _clamp(crossing_y_def, -GOALIE_GOAL_HALF_WIDTH, GOALIE_GOAL_HALF_WIDTH)
    return x, target_y, to_p_in_pi(atan2(ball_pos[1] - target_y, ball_pos[0] - x))

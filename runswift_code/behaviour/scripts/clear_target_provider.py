#!/usr/bin/env python3
"""Clear direction selection for goalkeeper / clear kicks.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import asin, atan2, cos, hypot, pi, sin
from pathlib import Path

import numpy as np
import yaml

try:
    from ament_index_python.packages import get_package_share_directory

    _dimension_yaml = Path(get_package_share_directory("runswift_config")) / "dimension.yaml"
    with _dimension_yaml.open(encoding="utf-8") as _f:
        _dim = yaml.safe_load(_f)
except Exception:
    _dim = {}

FIELD_LENGTH_M = float(_dim.get("length", 9.0))
FIELD_WIDTH_M = float(_dim.get("width", 6.0))
GOALIE_GOAL_X = -FIELD_LENGTH_M / 2.0
HALFWAY_X = 0.0
GOAL_AREA_HALF_WIDTH = float(_dim.get("goalAreaWidth", 2.2)) / 2.0
PENALTY_FRONT_X = GOALIE_GOAL_X + float(_dim.get("penaltyAreaLength", 1.65))

BALL_RADIUS_M = 0.11
GOAL_POST_RADIUS_M = 0.08
BALL_GOAL_POST_TANGENT_OFFSET_M = 0.05
AGENT_RADIUS_M = 0.35
FIELD_BORDER_MARGIN_M = 0.3
GOALIE_BORDER_STRIP_X = GOALIE_GOAL_X + 0.3
PENALTY_HALF_WIDTH = float(_dim.get("penaltyAreaWidth", 4.0)) / 2.0

# Clears must move the ball toward the opponent half, not sideways along the goal line.
CLEAR_MIN_FORWARD_COS = 0.35
CLEAR_MIN_FORWARD_M = 0.25
CLEAR_MIN_LANDING_X = GOALIE_GOAL_X + 0.55

SMALL_SECTOR_STEP_RAD = np.deg2rad(15.0)
HYSTERESIS_SECTOR_RAD = 0.05
HYSTERESIS_KICK_BONUS = 0.1

KICK_POWER_NEAR = 1.5
KICK_POWER_MID = 2.5
KICK_POWER_FAR = 3.5


@dataclass
class ClearKickType:
    name: str
    range_m: float
    power: float


CLEAR_KICK_TYPES: list[ClearKickType] = [
    ClearKickType("near", 1.5, KICK_POWER_NEAR),
    ClearKickType("mid", 2.5, KICK_POWER_MID),
    ClearKickType("long", 3.5, KICK_POWER_FAR),
]


@dataclass
class ClearTargetInput:
    ball_xy: tuple[float, float]
    teammates: list[tuple[float, float]] = field(default_factory=list)
    opponents: list[tuple[float, float]] = field(default_factory=list)
    own_free_kick: bool = False


@dataclass
class ClearTarget:
    valid: bool
    angle_rad: float = 0.0
    kick_range_m: float = 0.0
    kick_power: float = 0.0
    landing_xy: tuple[float, float] = (0.0, 0.0)
    rating: float = -1.0
    kick_name: str = ""
    emergency: bool = False


@dataclass
class ClearTargetState:
    """Hysteresis memory — keep one instance per robot / visualiser session."""

    last_angle_rad: float | None = None
    last_kick_name: str | None = None


@dataclass
class BlockedSector:
    min_angle: float
    max_angle: float
    kind: str  # "teammate" | "opponent"


@dataclass
class ClearTargetDebug:
    """Optional geometry for visualisation."""

    forbidden_left_rad: float = 0.0
    forbidden_right_rad: float = 0.0
    blocked_sectors: list[BlockedSector] = field(default_factory=list)
    candidate_angles: list[float] = field(default_factory=list)
    candidate_ratings: list[float] = field(default_factory=list)


def wrap_angle(angle: float) -> float:
    return atan2(sin(angle), cos(angle))


def unit_from_angle(angle: float) -> np.ndarray:
    return np.array([cos(angle), sin(angle)], dtype=float)


def landing_point(ball: np.ndarray, angle: float, dist: float) -> np.ndarray:
    return ball + dist * unit_from_angle(angle)


def map_to_range(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    if abs(x1 - x0) < 1e-12:
        return y0
    t = float(np.clip((x - x0) / (x1 - x0), 0.0, 1.0))
    return y0 + t * (y1 - y0)


def dist_xy(a: tuple[float, float] | np.ndarray, b: tuple[float, float] | np.ndarray) -> float:
    return float(hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1])))


def own_goal_forbidden_arc(ball_xy: np.ndarray) -> tuple[float, float]:
    """Tangent angles to own posts; arc between them must not be cleared."""
    left_post = np.array([GOALIE_GOAL_X, GOAL_AREA_HALF_WIDTH])
    right_post = np.array([GOALIE_GOAL_X, -GOAL_AREA_HALF_WIDTH])

    v_left = ball_xy - left_post
    v_right = ball_xy - right_post
    d_left = float(np.linalg.norm(v_left))
    d_right = float(np.linalg.norm(v_right))

    min_dist = GOAL_POST_RADIUS_M + BALL_RADIUS_M + BALL_GOAL_POST_TANGENT_OFFSET_M
    off_left = asin(min(1.0, min_dist / max(d_left, 1e-6)))
    off_right = asin(min(1.0, min_dist / max(d_right, 1e-6)))

    left_tan = wrap_angle(atan2(-v_left[1], -v_left[0]) - off_left)
    right_tan = wrap_angle(atan2(-v_right[1], -v_right[0]) + off_right)
    return left_tan, right_tan


def angle_in_arc(angle: float, arc_min: float, arc_max: float) -> bool:
    angle = wrap_angle(angle)
    arc_min = wrap_angle(arc_min)
    arc_max = wrap_angle(arc_max)
    if arc_min <= arc_max:
        return arc_min <= angle <= arc_max
    return angle >= arc_min or angle <= arc_max


def field_factor(ball_x: float, own_free_kick: bool) -> float:
    if own_free_kick:
        return 1.0
    return map_to_range(ball_x, PENALTY_FRONT_X, HALFWAY_X, 1.0, 0.0)


def is_landing_inside_field(landing: np.ndarray, margin: float = FIELD_BORDER_MARGIN_M) -> bool:
    hx = FIELD_LENGTH_M / 2.0 - margin
    hy = FIELD_WIDTH_M / 2.0 - margin
    return (
        -hx < landing[0] < hx
        and -hy < landing[1] < hy
    )


def ball_in_own_penalty_area(ball_xy: np.ndarray) -> bool:
    return (
        GOALIE_GOAL_X < ball_xy[0] < PENALTY_FRONT_X
        and abs(ball_xy[1]) < PENALTY_HALF_WIDTH
    )


def is_safe_clear_landing(
    angle: float,
    ball_xy: np.ndarray,
    kick_range_m: float,
) -> bool:
    """Reject sideways/backward clears that stay on the goal-line x."""
    landing = landing_point(ball_xy, angle, kick_range_m)
    if not is_landing_inside_field(landing):
        return False
    if landing[0] < CLEAR_MIN_LANDING_X:
        return False
    if landing[0] < ball_xy[0] + CLEAR_MIN_FORWARD_M:
        return False
    if ball_in_own_penalty_area(ball_xy) and cos(angle) < CLEAR_MIN_FORWARD_COS:
        return False
    return True


def agent_blocked_sectors(
    ball_xy: np.ndarray,
    agents: list[tuple[float, float]],
    kind: str,
) -> list[BlockedSector]:
    sectors: list[BlockedSector] = []
    for ax, ay in agents:
        obs = np.array([ax, ay], dtype=float)
        if obs[0] < GOALIE_BORDER_STRIP_X:
            continue
        vec = obs - ball_xy
        d = max(float(np.linalg.norm(vec)) - AGENT_RADIUS_M, 1e-3)
        direction = atan2(vec[1], vec[0])
        angular_half = atan2(AGENT_RADIUS_M, d)
        sectors.append(
            BlockedSector(direction - angular_half, direction + angular_half, kind)
        )
    return sectors


def sample_candidate_angles(
    forbidden_left: float,
    forbidden_right: float,
    blocked: list[BlockedSector],
) -> list[float]:
    candidates: list[float] = []
    n = max(1, int(round(2.0 * pi / SMALL_SECTOR_STEP_RAD)))
    for i in range(n):
        angle = wrap_angle(-pi + i * SMALL_SECTOR_STEP_RAD)
        if angle_in_arc(angle, forbidden_left, forbidden_right):
            continue
        if any(angle_in_arc(angle, s.min_angle, s.max_angle) for s in blocked):
            continue
        candidates.append(angle)
    return candidates


def angle_rating(
    angle: float,
    ball_xy: np.ndarray,
    kick_range_m: float,
    opponents: list[tuple[float, float]],
    ff: float,
) -> float:
    if not is_safe_clear_landing(angle, ball_xy, kick_range_m):
        return -1.0
    landing = landing_point(ball_xy, angle, kick_range_m)

    opp_penalty = 0.0
    for opp in opponents:
        opp_penalty += 1.0 / (0.5 + dist_xy(landing, opp))

    forward_bonus = map_to_range(
        float(landing[0]), float(ball_xy[0]), FIELD_LENGTH_M / 2.0, 0.0, 0.3
    )
    openness = 1.0 / (1.0 + opp_penalty)
    return ff * (openness + forward_bonus)


def teammate_preferred_at_landing(
    landing: np.ndarray,
    teammates: list[tuple[float, float]],
    opponents: list[tuple[float, float]],
) -> bool:
    """True when a teammate is closer to the landing than any opponent.

    With no opponents (or no teammates) there is nothing to compare — allow the clear.
    """
    if not opponents or not teammates:
        return True
    tm = min(dist_xy(landing, t) for t in teammates)
    opp = min(dist_xy(landing, o) for o in opponents)
    return tm < opp


def hysteresis_bonus(angle: float, kick_name: str, state: ClearTargetState) -> float:
    bonus = 0.0
    if state.last_angle_rad is not None:
        if abs(wrap_angle(angle - state.last_angle_rad)) < HYSTERESIS_SECTOR_RAD:
            bonus += HYSTERESIS_SECTOR_RAD
    if state.last_kick_name == kick_name:
        bonus += HYSTERESIS_KICK_BONUS
    return bonus


def clear_aim_unit(target: ClearTarget) -> np.ndarray:
    return unit_from_angle(target.angle_rad)


def _select_best_from_angles(
    angles: list[float],
    ball: np.ndarray,
    inp: ClearTargetInput,
    state: ClearTargetState,
    ff: float,
    *,
    require_teammate_gate: bool,
    emergency: bool,
) -> ClearTarget | None:
    best_rating = 0.0
    best: ClearTarget | None = None

    for angle in angles:
        for kick in CLEAR_KICK_TYPES:
            rating = angle_rating(angle, ball, kick.range_m, inp.opponents, ff)
            if rating < 0.0:
                continue
            rating += hysteresis_bonus(angle, kick.name, state)

            landing = landing_point(ball, angle, kick.range_m)
            if require_teammate_gate and not teammate_preferred_at_landing(
                landing, inp.teammates, inp.opponents
            ):
                continue

            if rating > best_rating:
                best_rating = rating
                best = ClearTarget(
                    valid=True,
                    angle_rad=angle,
                    kick_range_m=kick.range_m,
                    kick_power=kick.power,
                    landing_xy=(float(landing[0]), float(landing[1])),
                    rating=rating,
                    kick_name=kick.name,
                    emergency=emergency,
                )
    return best


def calc_emergency_clear(
    inp: ClearTargetInput,
    state: ClearTargetState,
    *,
    left_tan: float,
    right_tan: float,
) -> ClearTarget | None:
    """Goalkeeper must clear: relax teammate gate and teammate obstacle sectors."""
    ball = np.array(inp.ball_xy, dtype=float)
    ff = field_factor(float(ball[0]), inp.own_free_kick)
    blocked = agent_blocked_sectors(ball, inp.opponents, "opponent")
    angles = sample_candidate_angles(left_tan, right_tan, blocked)
    return _select_best_from_angles(
        angles,
        ball,
        inp,
        state,
        ff,
        require_teammate_gate=False,
        emergency=True,
    )


def calc_touchline_escape_clear(inp: ClearTargetInput) -> ClearTarget | None:
    """Last resort near the touchline: kick upfield along the nearest sideline."""
    ball = np.array(inp.ball_xy, dtype=float)
    side = 1.0 if ball[1] >= 0.0 else -1.0
    angle = wrap_angle(atan2(side * 0.75, 0.66))
    kick = CLEAR_KICK_TYPES[0]
    if not is_safe_clear_landing(angle, ball, kick.range_m):
        return None
    landing = landing_point(ball, angle, kick.range_m)
    return ClearTarget(
        valid=True,
        angle_rad=angle,
        kick_range_m=kick.range_m,
        kick_power=kick.power,
        landing_xy=(float(landing[0]), float(landing[1])),
        rating=0.01,
        kick_name="touchline_escape",
        emergency=True,
    )


def calc_best_clear(
    inp: ClearTargetInput,
    state: ClearTargetState | None = None,
    *,
    collect_debug: bool = False,
) -> tuple[ClearTarget, ClearTargetDebug | None]:
    if state is None:
        state = ClearTargetState()

    ball = np.array(inp.ball_xy, dtype=float)
    ff = field_factor(float(ball[0]), inp.own_free_kick)

    left_tan, right_tan = own_goal_forbidden_arc(ball)
    blocked = (
        agent_blocked_sectors(ball, inp.teammates, "teammate")
        + agent_blocked_sectors(ball, inp.opponents, "opponent")
    )
    angles = sample_candidate_angles(left_tan, right_tan, blocked)

    debug = ClearTargetDebug(
        forbidden_left_rad=left_tan,
        forbidden_right_rad=right_tan,
        blocked_sectors=list(blocked),
        candidate_angles=list(angles),
    ) if collect_debug else None

    best_angle_ratings: list[float] = []
    for angle in angles:
        best_angle_rating = -1.0
        for kick in CLEAR_KICK_TYPES:
            rating = angle_rating(angle, ball, kick.range_m, inp.opponents, ff)
            if rating < 0.0:
                continue
            rating += hysteresis_bonus(angle, kick.name, state)
            landing = landing_point(ball, angle, kick.range_m)
            if not teammate_preferred_at_landing(landing, inp.teammates, inp.opponents):
                continue
            best_angle_rating = max(best_angle_rating, rating)
        if collect_debug:
            best_angle_ratings.append(best_angle_rating)

    if collect_debug and debug is not None:
        debug.candidate_ratings = best_angle_ratings

    best = _select_best_from_angles(
        angles,
        ball,
        inp,
        state,
        ff,
        require_teammate_gate=True,
        emergency=False,
    )

    if best is None:
        best = calc_emergency_clear(inp, state, left_tan=left_tan, right_tan=right_tan)
    if best is None:
        best = calc_touchline_escape_clear(inp)

    if best is None:
        return ClearTarget(valid=False), debug

    state.last_angle_rad = best.angle_rad
    state.last_kick_name = best.kick_name
    return best, debug


def calc_best_clear_simple(
    inp: ClearTargetInput,
    state: ClearTargetState | None = None,
) -> ClearTarget:
    """Convenience wrapper returning only the target."""
    target, _ = calc_best_clear(inp, state)
    return target
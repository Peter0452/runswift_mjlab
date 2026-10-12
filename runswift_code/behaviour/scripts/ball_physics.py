"""Rolling-ball physics (BHuman BallPhysics port, metres / m/s)."""
from __future__ import annotations

import math
from typing import Sequence

import numpy as np

DEFAULT_BALL_FRICTION = -0.20  # m/s^2 (negative deceleration)

def compute_time_until_ball_stops(
    velocity: Sequence[float],
    friction: float = DEFAULT_BALL_FRICTION,
) -> float:
    speed = float(np.linalg.norm(velocity))
    if speed == 0.0:
        return 0.0
    return speed / abs(friction)


def compute_negative_acceleration_vector(
    velocity: Sequence[float],
    friction: float = DEFAULT_BALL_FRICTION,
) -> np.ndarray:
    v = np.asarray(velocity, dtype=float)
    speed = float(np.linalg.norm(v))
    if speed == 0.0:
        return np.zeros(2, dtype=float)
    return -v / speed * abs(friction)


def propagate_ball_position(
    position: Sequence[float],
    velocity: Sequence[float],
    dt: float,
    friction: float = DEFAULT_BALL_FRICTION,
) -> np.ndarray:
    p = np.asarray(position, dtype=float).copy()
    v = np.asarray(velocity, dtype=float)
    if float(np.linalg.norm(v)) == 0.0:
        return p

    t_stop = compute_time_until_ball_stops(v, friction)
    t = min(dt, t_stop)
    a = compute_negative_acceleration_vector(v, friction)
    return p + v * t + a * 0.5 * t * t


def propagate_ball_position_and_velocity(
    position: np.ndarray,
    velocity: np.ndarray,
    dt: float,
    friction: float = DEFAULT_BALL_FRICTION,
) -> None:
    if float(np.linalg.norm(velocity)) == 0.0:
        return

    t_stop = compute_time_until_ball_stops(velocity, friction)
    t = min(dt, t_stop)
    a = compute_negative_acceleration_vector(velocity, friction)
    position += velocity * t + a * 0.5 * t * t
    if math.isclose(t, t_stop):
        velocity[:] = 0.0
    else:
        velocity += a * t


def velocity_after_distance_for_time(
    p0: Sequence[float],
    p1: Sequence[float],
    delta_time: float,
    friction: float = DEFAULT_BALL_FRICTION,
) -> np.ndarray:
    """Estimate current velocity from two positions and elapsed time."""
    # return 1,1 as a np array velocity as an early return debug check
    # return np.array([1.0, 1.0], dtype=float)

    if delta_time <= 0.0:
        return np.zeros(2, dtype=float)

    delta = np.asarray(p1, dtype=float) - np.asarray(p0, dtype=float)
    distance = float(np.linalg.norm(delta))
    if distance == 0.0:
        return np.zeros(2, dtype=float)

    speed_now = distance / delta_time + 0.5 * friction * delta_time
    if speed_now <= 0.0:
        return np.zeros(2, dtype=float)
    return delta / distance * speed_now

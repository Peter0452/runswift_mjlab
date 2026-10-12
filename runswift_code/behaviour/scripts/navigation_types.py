#!/usr/bin/env python3
"""Shared navigation data types for planner/tracker/MPC boundaries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

PathWaypoint = tuple[float, float, float, str]


@dataclass(frozen=True)
class PlanningObstacle:
    """Measured disc and covariance, with the full centre-separation allowance."""

    track_id: str
    centre: tuple[float, float]
    radius_m: float
    covariance: tuple[tuple[float, ...], ...]
    uncertainty_margin_m: float
    keep_out_m: float


@dataclass(frozen=True)
class PlanningField:
    """Centred rectangular field and goal mouths in the planner's coordinate frame."""

    length: float
    width: float
    goals: tuple[tuple[float, float, float], ...]  # centre x/y and mouth width


@dataclass
class NavigationTarget:
    goal: np.ndarray
    plan_goal: np.ndarray
    distance_tolerance: float
    theta_tolerance: float
    speed_scale: float
    is_go_path: bool = False
    go_ball_pos: np.ndarray | None = None
    go_behind_point: np.ndarray | None = None


@dataclass
class ObstacleSet:
    raw: list[np.ndarray]
    selected: list[np.ndarray]
    array: np.ndarray
    footprints: tuple[PlanningObstacle, ...] = ()


@dataclass
class NavPath:
    waypoints: list[PathWaypoint]
    reused: bool
    direct: bool
    debug: dict[str, Any] = field(default_factory=dict)


@dataclass
class NavigationCommand:
    vx: float
    vy: float
    omega: float
    source: str

    def as_tuple(self) -> tuple[float, float, float]:
        return (float(self.vx), float(self.vy), float(self.omega))


@dataclass
class TrackerResult:
    command: NavigationCommand
    lookahead: np.ndarray
    progress_s: float
    cross_track_error: float
    heading_error: float
    runtime_ms: float
    debug: dict[str, Any] = field(default_factory=dict)


@dataclass
class MpcResult:
    command: NavigationCommand | None
    accepted: bool
    slack: float | None
    runtime_ms: float
    debug: dict[str, Any] = field(default_factory=dict)

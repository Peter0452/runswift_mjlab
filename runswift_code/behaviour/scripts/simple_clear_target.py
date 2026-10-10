#!/usr/bin/env python3
"""Pick a clear direction for DRIBBLE_CLEAR. Direction only — no power or range."""
from __future__ import annotations

from math import atan2, cos, pi, sin
from pathlib import Path

import numpy as np
import yaml

try:
    from ament_index_python.packages import get_package_share_directory

    _dim_path = Path(get_package_share_directory("runswift_config")) / "dimension.yaml"
    with _dim_path.open(encoding="utf-8") as _f:
        _dim = yaml.safe_load(_f)
except Exception:
    _dim = {}

HALF_LEN = float(_dim.get("length", 9.0)) / 2.0
N_SPOKES = 13  # wheel resolution across the forward arc
OPP_RADIUS_M = 0.35  # opponent footprint -> a near opponent blocks a wider cone than a far one
OPP_MARGIN_RAD = np.deg2rad(8.0)  # extra clearance around each opponent
GAP_WEIGHT = 0.3  # how much to favour open lanes vs. simply going straight forward


def pick_clear_direction(
    ball_xy: tuple[float, float],
    goalie_heading_rad: float,
    opponents: list[tuple[float, float]] | None = None,
) -> np.ndarray | None:
    """Best unit clear direction [dx, dy], chosen from a wheel of spokes over the forward arc.
    - not own goal, attempt to avoid opponents
    """
    ball = np.array(ball_xy, dtype=float)
    own_goal = np.array([-HALF_LEN, 0.0])
    opps = [np.array([ox, oy], dtype=float) for ox, oy in (opponents or [])]
    spokes = [np.array([cos(a), sin(a)]) for a in np.linspace(-pi / 2, pi / 2, N_SPOKES)]
    gap = lambda aim, o: abs((lambda d: atan2(sin(d), cos(d)))(atan2(o[1] - ball[1], o[0] - ball[0]) - atan2(aim[1], aim[0])))
    cone = lambda o: atan2(OPP_RADIUS_M, max(float(np.linalg.norm(o - ball)), 1e-6)) + OPP_MARGIN_RAD
    openness = lambda aim: min((gap(aim, o) for o in opps), default=pi)
    clear = [aim for aim in spokes if all(gap(aim, o) >= cone(o) for o in opps)]
    if clear:
        return max(clear, key=lambda aim: aim[0] + GAP_WEIGHT * openness(aim))
    return max(spokes, key=lambda aim: float(np.linalg.norm((ball + aim) - own_goal)))

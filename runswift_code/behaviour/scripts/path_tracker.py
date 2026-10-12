#!/usr/bin/env python3
from __future__ import annotations

import time
from dataclasses import dataclass
from math import atan2, cos, hypot, pi, sin

import numpy as np
from navigation_types import NavigationCommand, NavPath, TrackerResult


def _wrap(a: float) -> float:
    return (a + pi) % (2.0 * pi) - pi


@dataclass
class PathTrackerConfig:
    cruise_speed: float = 1.85         # nominal along-path speed [m/s]
    max_speed_frac: float = 0.8       # hard cap as a fraction of vx_limit
    heading_lookahead: float = 1.0     # chord distance used for travel heading [m]
    heading_gain: float = 2.0          # omega = gain * heading_error [1/s]
    cross_track_gain: float = 1.2      # lateral restoring gain [1/s]; ~1/(4*tau)
    cross_track_vel_cap: float = 1.8   # cap on lateral correction speed [m/s]
    goal_slowdown_dist: float = 2.2    # start decelerating to stop here [m]
    heading_blend_dist: float = 1.5    # start rotating to the goal heading here [m]
    yaw_couple: float = 1.2            # >0; higher => slow translation more to let yaw finish
    heading_eps: float = 0.05          # heading errors below this don't cap speed [rad]
    align_speed_floor: float = 0.15    # min speed factor when motion would be reverse
    min_speed: float = 0.4            # creep speed once en-route [m/s]
    reverse_limit: float = 1.5         # max backwards vx [m/s]


class _PreparedPath:
    """Pre-computed, cacheable geometry for one NavPath."""

    __slots__ = ("cum", "fingerprint", "pts", "seg_dir", "seglen", "ths", "total")

    def __init__(self, path: NavPath, fingerprint: tuple) -> None:
        self.fingerprint = fingerprint
        pts = np.array([[wp[0], wp[1]] for wp in path.waypoints], dtype=float)
        ths = np.array([wp[2] for wp in path.waypoints], dtype=float)
        self.pts = pts
        self.ths = ths
        if len(pts) < 2:
            self.seg_dir = np.zeros((0, 2), dtype=float)
            self.seglen = np.zeros((0,), dtype=float)
            self.cum = np.zeros((max(len(pts), 1),), dtype=float)
            self.total = 0.0
            return
        seg = np.diff(pts, axis=0)
        seglen = np.hypot(seg[:, 0], seg[:, 1])
        self.seg_dir = seg / np.maximum(seglen, 1e-9)[:, None]
        self.seglen = seglen
        self.cum = np.concatenate([[0.0], np.cumsum(seglen)])
        self.total = float(self.cum[-1])

    @staticmethod
    def fingerprint_of(path: NavPath) -> tuple:
        # Every waypoint and heading affects prepared geometry. Sampling only
        # start/middle/end can reuse an old detour after obstacles change.
        return tuple((float(wp[0]), float(wp[1]), float(wp[2])) for wp in path.waypoints)



class PathTracker:
    """Holonomic path follower with a continuous path-follow -> terminal blend."""

    def __init__(self, config: PathTrackerConfig | None = None):
        self.config = config or PathTrackerConfig()
        self._prepared: _PreparedPath | None = None

    def reset(self) -> None:
        """Discard prepared geometry when navigation ends or its frame changes."""
        self._prepared = None

    def _prepare(self, path: NavPath) -> _PreparedPath:
        fp = _PreparedPath.fingerprint_of(path)
        if self._prepared is None or self._prepared.fingerprint != fp:
            self._prepared = _PreparedPath(path, fp)
        return self._prepared

    @staticmethod
    def _project(pp: _PreparedPath, xy: np.ndarray) -> tuple[float, float, np.ndarray, float]:
        pts = pp.pts
        n = len(pts)
        if n == 0:
            return 0.0, 0.0, xy.copy(), 0.0
        if n == 1:
            return 0.0, float(hypot(*(xy - pts[0]))), pts[0].copy(), 0.0
        a = pts[:-1]
        ap = xy[None, :] - a
        t = np.einsum("ij,ij->i", ap, pp.seg_dir)
        t = np.clip(t, 0.0, pp.seglen)
        proj = a + pp.seg_dir * t[:, None]
        diff = xy[None, :] - proj
        d2 = np.einsum("ij,ij->i", diff, diff)
        i = int(np.argmin(d2))
        proj_i = proj[i]
        tx, ty = float(pp.seg_dir[i, 0]), float(pp.seg_dir[i, 1])
        nx, ny = -ty, tx
        e_ct = (xy[0] - proj_i[0]) * nx + (xy[1] - proj_i[1]) * ny
        s = float(pp.cum[i] + t[i])
        return s, float(e_ct), proj_i, atan2(ty, tx)

    @staticmethod
    def _point_at(pp: _PreparedPath, s: float) -> np.ndarray:
        if len(pp.pts) == 0:
            return np.zeros(2, dtype=float)
        if len(pp.pts) == 1 or pp.total < 1e-9:
            return pp.pts[-1].copy()
        s = float(np.clip(s, 0.0, pp.total))
        idx = int(np.searchsorted(pp.cum, s, side="right") - 1)
        idx = max(0, min(idx, len(pp.pts) - 2))
        return pp.pts[idx] + pp.seg_dir[idx] * (s - pp.cum[idx])

    def _result(self, t0, vx, vy, omega, carrot, desired_heading,
                progress_s, e_ct, heading_error, path_len, debug_extra):
        runtime_ms = (time.perf_counter() - t0) * 1000.0
        debug = {
            "path_len": path_len,
            "vx": round(vx, 3), "vy": round(vy, 3), "omega": round(omega, 3),
            "tracker_ms": round(float(runtime_ms), 3),
        }
        debug.update(debug_extra)
        return TrackerResult(
            command=NavigationCommand(vx=vx, vy=vy, omega=omega, source="path_tracker"),
            lookahead=np.array([carrot[0], carrot[1], desired_heading], dtype=float),
            progress_s=float(progress_s),
            cross_track_error=float(e_ct),
            heading_error=float(heading_error),
            runtime_ms=float(runtime_ms),
            debug=debug,
        )

    def track(
        self,
        *,
        X0: np.ndarray,
        path: NavPath,
        goal: np.ndarray,
        speed_scale: float,
        vx_limit: float,
        vy_limit: float,
        vtheta_limit: float,
        distance_tolerance: float,
        theta_tolerance: float,
    ) -> TrackerResult:
        t0 = time.perf_counter()
        cfg = self.config
        pp = self._prepare(path)
        xy = np.asarray(X0, dtype=float)[:2]
        theta = float(X0[2])
        goal_xy = np.asarray(goal, dtype=float)[:2]
        goal_theta = float(goal[2])

        cruise = min(cfg.cruise_speed * speed_scale, cfg.max_speed_frac * vx_limit)
        to_goal = goal_xy - xy
        gnorm = float(hypot(to_goal[0], to_goal[1]))

        # ---- geometry (path or degenerate go-to-pose) ----
        degenerate = pp.total < 1e-9 or len(pp.pts) < 2
        if degenerate:
            progress_s = 0.0
            e_ct = 0.0
            proj = xy.copy()
            remaining = gnorm
            phi_loc = atan2(to_goal[1], to_goal[0]) if gnorm > 1e-9 else theta
            phi_travel = phi_loc
            carrot = goal_xy
        else:
            progress_s, e_ct, proj, phi_loc = self._project(pp, xy)
            remaining = max(pp.total - progress_s, 0.0)
            head_pt = self._point_at(pp, min(progress_s + cfg.heading_lookahead, pp.total))
            chord = head_pt - proj
            phi_travel = atan2(chord[1], chord[0]) if float(chord @ chord) > 1e-6 else phi_loc
            carrot = head_pt

        # ---- one continuous heading law: travel heading blended to goal ----
        blend = 0.0
        if remaining < cfg.heading_blend_dist:
            span = max(cfg.heading_blend_dist - distance_tolerance, 1e-6)
            blend = float(np.clip((cfg.heading_blend_dist - remaining) / span, 0.0, 1.0))
        desired_heading = _wrap(phi_travel + blend * _wrap(goal_theta - phi_travel))
        heading_error = _wrap(desired_heading - theta)
        he_abs = abs(heading_error)

        # ---- arrival stop (matches planner tolerances) ----
        if gnorm < distance_tolerance and abs(_wrap(goal_theta - theta)) < theta_tolerance:
            return self._result(t0, 0.0, 0.0, 0.0, goal_xy, goal_theta,
                                progress_s, e_ct, _wrap(goal_theta - theta),
                                len(pp.pts), {"mode": "arrived", "alpha": 1.0})

        # ---- speed: full for forward OR lateral, slow only for reverse ----
        def yaw_speed_cap(dist: float) -> float:
            if he_abs <= cfg.heading_eps:
                return float("inf")
            return vtheta_limit * dist / (cfg.yaw_couple * he_abs)

        speed = cruise
        if remaining < cfg.goal_slowdown_dist:
            speed *= max(0.0, remaining / max(cfg.goal_slowdown_dist, 1e-6))
        # heading_error is to the DESIRED facing. cth >= 0: the path velocity is
        # within +/-90deg of facing -> forward or lateral, both fine for a
        # holonomic base -> full speed. cth < 0: it would be reverse -> slow so
        # yaw turns us to the desired heading first.
        cth = cos(heading_error)
        if cth < 0.0:
            speed *= max(cfg.align_speed_floor, 1.0 + cth)
        elif remaining > distance_tolerance:
            speed = max(speed, cfg.min_speed)
        speed = min(speed, yaw_speed_cap(max(remaining, gnorm)))

        # ---- translation: always follow the path; never override it. ----
        # forward vs lateral is just the body-frame decomposition of the same
        # world-frame path velocity, set by whatever heading we command.
        tangent = np.array([cos(phi_travel), sin(phi_travel)])
        normal = np.array([-sin(phi_travel), cos(phi_travel)])
        v_perp = float(np.clip(-cfg.cross_track_gain * e_ct,
                               -cfg.cross_track_vel_cap, cfg.cross_track_vel_cap))
        v_world = speed * tangent + v_perp * normal

        c, s = cos(theta), sin(theta)
        vx = float(np.clip(c * v_world[0] + s * v_world[1], -cfg.reverse_limit, vx_limit))
        vy = float(np.clip(-s * v_world[0] + c * v_world[1], -vy_limit, vy_limit))
        omega = float(np.clip(cfg.heading_gain * heading_error, -vtheta_limit, vtheta_limit))

        if abs(vx) < 1e-3 and abs(vy) < 1e-3:
            mode = "turning"
        elif abs(vy) > abs(vx):
            mode = "lateral"
        else:
            mode = "forward"
        return self._result(t0, vx, vy, omega, carrot, desired_heading,
                            progress_s, e_ct, heading_error, len(pp.pts),
                            {"mode": mode,
                             "remaining_s": round(float(remaining), 3),
                             "cross_track_error": round(float(e_ct), 3),
                             "speed": round(float(speed), 3),
                             "blend": round(float(blend), 3)})

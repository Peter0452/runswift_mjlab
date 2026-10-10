#!/usr/bin/env python3
"""Shared planar collision geometry for global planning and local command checks.

All positions are in one planning frame. Contact is blocked, including numerical
near-contact. Coverage is explicit evidence; missing regions never mean clear.
"""

from dataclasses import dataclass
from itertools import pairwise
from math import cos, hypot, isfinite, sin

import numpy as np
from navigation_types import PlanningField, PlanningObstacle

EPS = 1e-8
Polygon2 = tuple[tuple[float, float], ...]


def segment_distance(a, b, point):
    a, b, point = (np.asarray(p, dtype=float) for p in (a, b, point))
    delta = b - a
    length2 = float(delta @ delta)
    fraction = (
        0.0
        if length2 <= 1e-20
        else float(np.clip((point - a) @ delta / length2, 0.0, 1.0))
    )
    return float(np.linalg.norm(point - (a + fraction * delta)))


def _signed_distances(point, polygon):
    vertices = np.asarray(polygon, dtype=float)
    edges = np.roll(vertices, -1, axis=0) - vertices
    offset = np.asarray(point) - vertices
    return (edges[:, 0] * offset[:, 1] - edges[:, 1] * offset[:, 0]) / np.linalg.norm(
        edges, axis=1
    )


def _contains_capsule(a, b, radius, polygon):
    # Convexity means the whole swept disc fits if both endpoint discs fit.
    return bool(
        np.all(_signed_distances(a, polygon) > radius + EPS)
        and np.all(_signed_distances(b, polygon) > radius + EPS)
    )


def _touches_polygon(a, b, radius, polygon):
    da, db = _signed_distances(a, polygon), _signed_distances(b, polygon)
    # Clip the centre segment against the convex polygon's half planes.
    lo, hi = 0.0, 1.0
    for start, end in zip(da, db):
        change = end - start
        if abs(change) < 1e-15:
            if start < -EPS:
                lo, hi = 1.0, 0.0
                break
        elif change > 0:
            lo = max(lo, (-EPS - start) / change)
        else:
            hi = min(hi, (-EPS - start) / change)
    if lo <= hi:
        return True
    for c, d in zip(polygon, polygon[1:] + polygon[:1]):
        # Non-intersecting segments attain their distance at an endpoint.
        if (
            min(
                segment_distance(a, b, c),
                segment_distance(a, b, d),
                segment_distance(c, d, a),
                segment_distance(c, d, b),
            )
            <= radius + EPS
        ):
            return True
    return False


@dataclass(frozen=True)
class ClearRegion:
    """One usable report in the planning frame, at this tick's reference time."""

    inspected: tuple[Polygon2, ...]
    clear: tuple[Polygon2, ...]
    occluded: tuple[Polygon2, ...]
    boundary_error_m: float


@dataclass(frozen=True)
class CollisionScene:
    """The same inflated footprints and coverage rules for every movement check."""

    obstacles: tuple[PlanningObstacle, ...]
    field: PlanningField
    robot_margin_m: float
    field_margin_m: float
    regions: tuple[ClearRegion, ...] = ()
    unknown_space: str = "require_clear"
    command_horizon_sec: float = 0.5
    heading_margin_rad: float = 0.0
    max_unknown_speed_mps: float = 0.2

    def segment_reason(self, a, b, *, extra_margin=0.0):
        """Check a centre segment swept by the robot and any command deviation."""
        a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
        if not np.isfinite([a, b]).all():
            return "navigation_path_invalid"
        half = np.array([self.field.length, self.field.width]) / 2
        half -= self.field_margin_m + extra_margin
        if np.any(np.abs([a, b]) >= half - EPS):
            return "navigation_field_clearance"
        for item in self.obstacles:
            if (
                segment_distance(a, b, item.centre)
                <= item.keep_out_m + extra_margin + EPS
            ):
                return "navigation_obstacle_clearance"
        # Known occlusions override clear claims, including under allow_unknown.
        for region in self.regions:
            radius = self.robot_margin_m + extra_margin + region.boundary_error_m
            if any(_touches_polygon(a, b, radius, p) for p in region.occluded):
                return "navigation_space_occluded"
        if self.unknown_space == "allow_unknown":
            return None
        for region in self.regions:
            radius = self.robot_margin_m + extra_margin + region.boundary_error_m
            if any(
                _contains_capsule(a, b, radius, p) for p in region.inspected
            ) and any(_contains_capsule(a, b, radius, p) for p in region.clear):
                return None
        return "navigation_space_unobserved"

    def path_reason(self, path, *, start=None):
        """Check the remaining path and the connection from the actual robot pose."""
        if not path:
            return "navigation_path_invalid"
        points = np.asarray([p[:2] for p in path], dtype=float)
        if not np.isfinite(points).all():
            return "navigation_path_invalid"
        if start is not None and len(points) > 1:
            # Match the tracker's nearest-segment projection; travelled portions
            # need not remain clear, but the route back to the path must be clear.
            delta = np.diff(points, axis=0)
            length2 = np.einsum("ij,ij->i", delta, delta)
            t = np.clip(
                np.einsum("ij,ij->i", np.asarray(start) - points[:-1], delta)
                / np.maximum(length2, 1e-20),
                0.0,
                1.0,
            )
            projections = points[:-1] + t[:, None] * delta
            i = int(np.argmin(np.linalg.norm(projections - start, axis=1)))
            points = np.vstack((start, projections[i], points[i + 1 :]))
        elif start is not None:
            points = np.vstack((start, points))
        pairs = pairwise(points) if len(points) > 1 else ((points[0], points[0]),)
        return next(
            (reason for a, b in pairs if (reason := self.segment_reason(a, b))), None
        )

    def limit_command(self, pose, velocity):
        """Slow or stop a body-frame command using the same swept-disc contract.

        The straight reference segment is inflated for initial heading error and
        rotation during the hold horizon. This bounds constant body-velocity arcs
        without relying on sparse samples. The executive must refresh/expire intent
        within that horizon; this is not a braking or dynamic-obstacle controller.
        """
        if not all(isfinite(v) for v in velocity):
            return None, "navigation_command_invalid"
        vx, vy, omega = velocity
        speed = hypot(vx, vy)
        if self.unknown_space == "allow_unknown" and speed > self.max_unknown_speed_mps:
            factor = self.max_unknown_speed_mps / speed
            vx, vy = vx * factor, vy * factor
        start = (pose.x, pose.y)
        c, s = cos(pose.theta), sin(pose.theta)
        horizon = self.command_horizon_sec
        for scale in (1.0, 0.5, 0.25, 0.125, 0.0):
            x, y = vx * scale, vy * scale
            end = (
                pose.x + (c * x - s * y) * horizon,
                pose.y + (s * x + c * y) * horizon,
            )
            deviation = (
                hypot(x, y)
                * horizon
                * min(2.0, self.heading_margin_rad + abs(omega) * horizon)
            )
            reason = self.segment_reason(start, end, extra_margin=deviation)
            if reason is None:
                if scale == 0 and speed > 0 and abs(omega) < 1e-6:
                    break
                return (x, y, omega), "navigation_command_limited" if (
                    x,
                    y,
                ) != velocity[:2] else None
        return None, reason or "navigation_command_blocked"

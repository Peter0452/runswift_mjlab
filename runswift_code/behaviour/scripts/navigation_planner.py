#!/usr/bin/env python3
"""Global path planning wrapper with obstacle selection, threat gating, and profiling."""
from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from math import isfinite
from typing import Any

import numpy as np
from navigation_safety import CollisionScene
from navigation_types import (
    NavPath,
    ObstacleSet,
    PathWaypoint,
    PlanningField,
    PlanningObstacle,
)
from simplier_planner import Obstacles, PlannerParams, plan


def legacy_field() -> PlanningField:
    """Compatibility for legacy callers; context-based navigation supplies geometry."""
    from legacy_world_model import FIELD_LENGTH_M, FIELD_WIDTH_M, GOAL_WIDTH_M

    return PlanningField(FIELD_LENGTH_M, FIELD_WIDTH_M, (
        (-FIELD_LENGTH_M / 2, 0.0, GOAL_WIDTH_M),
        (FIELD_LENGTH_M / 2, 0.0, GOAL_WIDTH_M),
    ))

GOAL_REPLAN_TOLERANCE_M = 0.25
REPLAN_J_HYSTERESIS_M = 0.20
REPLAN_J_GOAL_WEIGHT_M = 0.20
REPLAN_J_AGE_WEIGHT_M = 0.15

# Depth of the goal net behind the goal line. A target point behind the goal
# line and between the posts is inside the physical goal structure.
GOAL_NET_DEPTH_M = 1.0


@dataclass
class GlobalPlannerConfig:
    max_obstacles: int
    fixed_obstacles: bool
    replan_period_sec: float
    tracking_reserve_m: float = 0.0

    def __post_init__(self):
        """Extra waypoint spacing reserves tracking room beyond required clearance."""
        if not isfinite(self.tracking_reserve_m) or self.tracking_reserve_m < 0:
            raise ValueError("tracking_reserve_m must be finite and non-negative")


def obstacle_array(obstacles: list[np.ndarray]) -> np.ndarray:
    if not obstacles:
        return np.zeros((0, 2), dtype=float)
    return np.array([np.asarray(o, dtype=float)[:2] for o in obstacles], dtype=float)


def segment_distance(a: np.ndarray, b: np.ndarray, p: np.ndarray) -> float:
    ab = b - a
    denom = float(ab @ ab)
    if denom < 1e-12:
        return float(np.linalg.norm(p - a))
    t = float(np.clip((p - a) @ ab / denom, 0.0, 1.0))
    closest = a + t * ab
    return float(np.linalg.norm(p - closest))

def pose_in_field(xy: np.ndarray, *, margin: float = 0.0, field: PlanningField | None = None) -> bool:
    field = legacy_field() if field is None else field
    half_length = field.length * 0.5 - margin
    half_width = field.width * 0.5 - margin
    return abs(float(xy[0])) <= half_length and abs(float(xy[1])) <= half_width


def point_in_soccer_goal(xy: np.ndarray, *, field: PlanningField | None = None) -> bool:
    """True when the point lies inside a physical goal (behind either goal line
    and between the posts). Such a target is unreachable/illegal, so the planner
    gives up rather than routing the robot into the net."""
    field = legacy_field() if field is None else field
    for x, y, width in field.goals:
        depth = (float(xy[0]) - x) * (1 if x >= 0 else -1)
        if 0 <= depth <= GOAL_NET_DEPTH_M and abs(float(xy[1]) - y) <= width * 0.5:
            return True
    return False


def direct_waypoints(X0: np.ndarray, plan_goal: np.ndarray) -> list[PathWaypoint]:
    return [
        (float(X0[0]), float(X0[1]), float(X0[2]), "start"),
        (float(plan_goal[0]), float(plan_goal[1]), float(plan_goal[2]), "direct"),
    ]


def build_obstacles(
    obstacle_set: ObstacleSet,
    keep_out: float,
    *,
    safety_margin: float,
    field: PlanningField | None = None,
) -> Obstacles:
    centers = obstacle_set.array
    n = centers.shape[0]
    radii = np.full(n, float(keep_out), dtype=float) if n else np.zeros(0, dtype=float)
    if obstacle_set.footprints:
        radii = np.array([item.keep_out_m for item in obstacle_set.footprints], dtype=float)
    field = legacy_field() if field is None else field
    half_length = field.length * 0.5 - safety_margin
    half_width = field.width * 0.5 - safety_margin
    return Obstacles(
        centers=centers,
        radii=radii,
        field_halfsize=np.array([half_length, half_width], dtype=float),
    )



def waypoints_from_path(path: np.ndarray) -> list[PathWaypoint]:
    return [
        (float(row[0]), float(row[1]), float(row[2]), "planned")
        for row in path
    ]


def path_length(waypoints: list[PathWaypoint]) -> float:
    if len(waypoints) < 2:
        return 0.0
    total = 0.0
    for i in range(len(waypoints) - 1):
        a = np.asarray(waypoints[i][:2], dtype=float)
        b = np.asarray(waypoints[i + 1][:2], dtype=float)
        total += float(np.linalg.norm(b - a))
    return total


def remaining_path_length(waypoints: list[PathWaypoint], xy: np.ndarray) -> float:
    if len(waypoints) < 2:
        return 0.0
    pts = np.array([[wp[0], wp[1]] for wp in waypoints], dtype=float)
    xy = np.asarray(xy, dtype=float)[:2]
    seg = np.diff(pts, axis=0)
    seglen = np.hypot(seg[:, 0], seg[:, 1])
    if float(seglen.sum()) < 1e-9:
        return 0.0
    seg_dir = seg / np.maximum(seglen, 1e-9)[:, None]
    cum = np.concatenate([[0.0], np.cumsum(seglen)])
    a = pts[:-1]
    ap = xy[None, :] - a
    t = np.einsum("ij,ij->i", ap, seg_dir)
    t = np.clip(t, 0.0, seglen)
    proj = a + seg_dir * t[:, None]
    diff = xy[None, :] - proj
    i = int(np.argmin(np.einsum("ij,ij->i", diff, diff)))
    progress_s = float(cum[i] + t[i])
    return max(float(cum[-1]) - progress_s, 0.0)


def path_clear(
    waypoints: list[PathWaypoint],
    obstacles: list[np.ndarray],
    keep_out: float,
) -> bool:
    if len(waypoints) < 2:
        return True
    for i in range(len(waypoints) - 1):
        a = np.asarray(waypoints[i][:2], dtype=float)
        b = np.asarray(waypoints[i + 1][:2], dtype=float)
        for obstacle in obstacles:
            obs_xy = np.asarray(obstacle, dtype=float)[:2]
            if float(np.linalg.norm(obs_xy)) > 900.0:
                continue
            if segment_distance(a, b, obs_xy) < keep_out:
                return False
    return True


def point_threatened(
    xy: np.ndarray,
    obstacles: list[np.ndarray],
    keep_out: float,
) -> bool:
    xy = np.asarray(xy, dtype=float)[:2]
    for obstacle in obstacles:
        obs_xy = np.asarray(obstacle, dtype=float)[:2]
        if float(np.linalg.norm(obs_xy)) > 900.0:
            continue
        if float(np.linalg.norm(obs_xy - xy)) < keep_out:
            return True
    return False


class GlobalPlanner:
    """Threat-gated global planner: straight walk when clear, rate-limited otherwise."""

    def __init__(
        self,
        config: GlobalPlannerConfig,
        *,
        profiler: Callable[[str, dict[str, Any]], None] | None = None,
        path_logger: Callable[[list[PathWaypoint]], None] | None = None,
    ):
        self.config = config
        self.profiler = profiler
        self.path_logger = path_logger
        self._cache: dict[str, Any] | None = None
        self.last_failure: str | None = None

    def reset(self) -> None:
        self._cache = None
        self.last_failure = None

    def _log_path(self, path):
        if self.path_logger is not None:
            self.path_logger(path)

    def prepare_obstacles(
        self,
        obstacles: list[np.ndarray],
        *,
        X0: np.ndarray,
        plan_goal: np.ndarray,
        go_ball_pos: np.ndarray | None,
        footprints: tuple[PlanningObstacle, ...] | None = None,
    ) -> ObstacleSet:
        raw = [np.asarray(o, dtype=float)[:2].copy() for o in obstacles]
        if not raw:
            selected: list[np.ndarray] = []
        else:
            protected_idx = None
            if go_ball_pos is not None:
                ball_xy = np.asarray(go_ball_pos, dtype=float)[:2]
                protected_idx = min(
                    range(len(raw)),
                    key=lambda idx: float(np.linalg.norm(raw[idx] - ball_xy)),
                )
            scored = []
            for idx, pt in enumerate(raw):
                route_dist = segment_distance(X0[:2], plan_goal[:2], pt)
                robot_dist = float(np.linalg.norm(pt - X0[:2]))
                protected_bonus = -1000.0 if idx == protected_idx else 0.0
                scored.append((protected_bonus + route_dist + 0.15 * robot_dist, idx, pt))
            scored.sort(key=lambda item: item[0])
            selected = [pt for _, _, pt in scored[: self.config.max_obstacles]]

        selected_footprints = ()
        if footprints is not None:
            if len(footprints) != len(raw):
                raise ValueError("Each obstacle needs its own footprint")
            selected_footprints = (
                tuple(footprints[idx] for _, idx, _ in scored[: self.config.max_obstacles])
                if raw else ()
            )

        if self.config.fixed_obstacles and footprints is None:
            pad_count = self.config.max_obstacles - len(selected)
            if pad_count > 0:
                far_base = np.array([1000.0, 1000.0], dtype=float)
                selected.extend(far_base + np.array([float(i), 0.0]) for i in range(pad_count))
        return ObstacleSet(
            raw=raw, selected=selected, array=obstacle_array(selected),
            footprints=selected_footprints,
        )

    def direct_path_clear(
        self,
        start_xy: np.ndarray,
        goal_xy: np.ndarray,
        obstacles: list[np.ndarray],
        keep_out: float,
    ) -> bool:
        """True when no obstacle threatens the robot or the straight route to goal."""
        for obstacle in obstacles:
            obs_xy = np.asarray(obstacle, dtype=float)[:2]
            if float(np.linalg.norm(obs_xy - start_xy)) < keep_out:
                return False
            if segment_distance(start_xy, goal_xy, obs_xy) < keep_out:
                return False
        return True

    def _run_plan(
        self,
        *,
        X0: np.ndarray,
        plan_goal: np.ndarray,
        obstacle_set: ObstacleSet,
        keep_out: float,
        safety_margin: float,
        theta_tolerance: float,
        field: PlanningField,
        collision_scene: CollisionScene | None = None,
    ) -> tuple[list[PathWaypoint] | None, dict[str, Any]]:
        obs = build_obstacles(
            obstacle_set, keep_out, safety_margin=safety_margin, field=field
        )
        # Prefer routes with room for tracking error. Covered-start escape
        # candidates from the underlying planner must still pass the original
        # scene's full collision checks below; the reserve relaxes no constraint.
        obs.radii = obs.radii + self.config.tracking_reserve_m
        params = PlannerParams(
            theta_tolerance=theta_tolerance,
            # build_obstacles already shrinks the field. Adding the margin here
            # would undo that shrink and admit boundary collisions.
            field_margin=0.0,
        )
        path_arr, plan_info = plan(X0, plan_goal, obs, params)
        if path_arr is None:
            return None, plan_info
        path = waypoints_from_path(path_arr)
        if collision_scene is not None:
            reason = collision_scene.path_reason(path, start=X0[:2])
            if reason:
                self.last_failure = reason
                return None, {**plan_info, "reason": reason}
        return path, plan_info

    def _store_cache(
        self,
        *,
        now_mono: float,
        path: list[PathWaypoint],
        plan_goal: np.ndarray,
    ) -> None:
        self._cache = {
            "mono_sec": now_mono,
            "path": list(path),
            "plan_goal": np.asarray(plan_goal, dtype=float).copy(),
            "path_length": path_length(path),
        }

    def update(
        self,
        *,
        now_mono: float,
        X0: np.ndarray,
        plan_goal: np.ndarray,
        raw_obstacles: list[np.ndarray],
        keep_out: float,
        go_ball_pos: np.ndarray | None = None,
        obstacle_set: ObstacleSet | None = None,
        safety_margin: float = 0.0,
        theta_tolerance: float = 0.15,
        field: PlanningField | None = None,
        collision_scene: CollisionScene | None = None,
    ) -> tuple[NavPath | None, ObstacleSet]:
        t0 = time.perf_counter()
        self.last_failure = None
        field = legacy_field() if field is None else field
        if point_in_soccer_goal(plan_goal[:2], field=field):
            self.reset()
            self._log_path([])
            empty_set = obstacle_set if obstacle_set is not None else ObstacleSet(
                raw=[], selected=[], array=obstacle_array([])
            )
            return None, empty_set
        if obstacle_set is None:
            obstacle_set = self.prepare_obstacles(
                raw_obstacles,
                X0=X0,
                plan_goal=plan_goal,
                go_ball_pos=go_ball_pos,
                footprints=None if collision_scene is None else collision_scene.obstacles,
            )
        t_obstacles = time.perf_counter()

        plan_info: dict[str, Any] = {}
        t_threat = time.perf_counter()
        no_threat = (
            self.direct_path_clear(X0[:2], plan_goal[:2], obstacle_set.selected, keep_out)
            if collision_scene is None
            else collision_scene.segment_reason(
                X0[:2], plan_goal[:2], extra_margin=self.config.tracking_reserve_m
            ) is None
        )
        on_field = (
            pose_in_field(X0[:2], margin=safety_margin, field=field)
            and pose_in_field(plan_goal[:2], margin=safety_margin, field=field)
        )
        can_direct = no_threat and on_field
        t_threat_done = time.perf_counter()

        cache = self._cache
        goal_shift = (
            float(np.linalg.norm(plan_goal[:2] - cache["plan_goal"][:2]))
            if cache is not None and "plan_goal" in cache
            else float("inf")
        )
        cache_age = (
            float(now_mono - cache["mono_sec"]) if cache is not None else None
        )
        cached_path_clear = None
        j_keep = None
        j_keep_eff = None
        j_new = None

        if can_direct:
            self._cache = None
            path: list[PathWaypoint] | None = direct_waypoints(X0, plan_goal)
            plan_reused = False
            direct_path_used = True
            replan_reason = "direct"
            plan_info = {"reason": "direct"}
            t_plan = t_threat_done
        else:
            cache_age = float(cache_age) if cache_age is not None else float("inf")
            obstacles = obstacle_set.selected
            cached_path = None if cache is None else list(cache["path"])
            if collision_scene is None:
                cached_path_clear = cached_path is not None and path_clear(cached_path, obstacles, keep_out)
                robot_threatened = point_threatened(X0[:2], obstacles, keep_out)
            else:
                cached_path_clear = cached_path is not None and collision_scene.path_reason(cached_path, start=X0[:2]) is None
                robot_threatened = collision_scene.segment_reason(X0[:2], X0[:2]) is not None
            goal_moved = goal_shift > GOAL_REPLAN_TOLERANCE_M

            plan_reused = False
            direct_path_used = False
            t_plan = t_threat_done

            if cache is None:
                path, plan_info = self._run_plan(
                    X0=X0,
                    plan_goal=plan_goal,
                    obstacle_set=obstacle_set,
                    keep_out=keep_out,
                    safety_margin=safety_margin,
                    theta_tolerance=theta_tolerance,
                    field=field,
                    collision_scene=collision_scene,
                )
                t_plan = time.perf_counter()
                replan_reason = "no_cache"
                if path is not None:
                    j_new = path_length(path)
                    self._store_cache(now_mono=now_mono, path=path, plan_goal=plan_goal)
            elif robot_threatened or not cached_path_clear or goal_moved:
                path, plan_info = self._run_plan(
                    X0=X0,
                    plan_goal=plan_goal,
                    obstacle_set=obstacle_set,
                    keep_out=keep_out,
                    safety_margin=safety_margin,
                    theta_tolerance=theta_tolerance,
                    field=field,
                    collision_scene=collision_scene,
                )
                t_plan = time.perf_counter()
                if robot_threatened:
                    replan_reason = "robot_threatened"
                elif not cached_path_clear:
                    replan_reason = "path_blocked"
                else:
                    replan_reason = "goal_moved"
                if path is not None:
                    j_new = path_length(path)
                    self._store_cache(now_mono=now_mono, path=path, plan_goal=plan_goal)
            elif cache_age <= self.config.replan_period_sec:
                path = cached_path
                plan_reused = True
                replan_reason = "cache_hit"
                plan_info = {"reason": "cache_hit"}
                j_keep = remaining_path_length(path, X0[:2])
            else:
                candidate_path, plan_info = self._run_plan(
                    X0=X0,
                    plan_goal=plan_goal,
                    obstacle_set=obstacle_set,
                    keep_out=keep_out,
                    safety_margin=safety_margin,
                    theta_tolerance=theta_tolerance,
                    field=field,
                    collision_scene=collision_scene,
                )
                t_plan = time.perf_counter()
                j_keep = remaining_path_length(cached_path, X0[:2])
                goal_term = REPLAN_J_GOAL_WEIGHT_M * (
                    goal_shift / GOAL_REPLAN_TOLERANCE_M
                )
                age_term = REPLAN_J_AGE_WEIGHT_M * (
                    cache_age / self.config.replan_period_sec
                )
                j_keep_eff = j_keep + goal_term + age_term
                j_new = None if candidate_path is None else path_length(candidate_path)
                if candidate_path is None or j_keep_eff <= j_new + REPLAN_J_HYSTERESIS_M:
                    path = cached_path
                    plan_reused = True
                    replan_reason = "cache_hit_j"
                    plan_info = dict(plan_info)
                    plan_info["reason"] = "cache_hit_j"
                    self._cache["mono_sec"] = now_mono
                else:
                    path = candidate_path
                    replan_reason = "better_j"
                    plan_info = dict(plan_info)
                    plan_info["reason"] = "better_j"
                    self._store_cache(now_mono=now_mono, path=path, plan_goal=plan_goal)

        if path is None:
            self._cache = None
        t_end = time.perf_counter()
        debug = {
            "planner_total_ms": round((t_end - t0) * 1000.0, 2),
            "obstacle_prepare_ms": round((t_obstacles - t0) * 1000.0, 2),
            "threat_check_ms": round((t_threat_done - t_threat) * 1000.0, 2),
            "plan_ms": round((t_plan - t_threat_done) * 1000.0, 2)
            if not can_direct and t_plan > t_threat_done
            else 0.0,
            "path_cache_hit": bool(plan_reused),
            "goal_shift_m": round(goal_shift, 3) if not can_direct and cache is not None else None,
            "cache_age_sec": round(cache_age, 3) if not can_direct and cache is not None else None,
            "cached_path_clear": cached_path_clear,
            "j_keep_m": None if j_keep is None else round(j_keep, 3),
            "j_keep_eff_m": None if j_keep_eff is None else round(j_keep_eff, 3),
            "j_new_m": None if j_new is None else round(j_new, 3),
            "replan_reason": replan_reason,
            "threat": not no_threat,
            "on_field": on_field,
            "keep_out": round(float(keep_out), 3),
            "direct_path": bool(direct_path_used),
            "n_raw_obstacles": len(obstacle_set.raw),
            "n_selected_obstacles": len(obstacle_set.selected),
            "path_len": None if path is None else len(path),
            "plan_info": plan_info,
        }
        if self.profiler is not None:
            self.profiler("global planner timing", debug)

        if path is None:
            self._log_path([])
            return None, obstacle_set

        waypoints = list(path)
        self._log_path(waypoints)

        return NavPath(waypoints=waypoints, reused=plan_reused, direct=direct_path_used, debug=debug), obstacle_set

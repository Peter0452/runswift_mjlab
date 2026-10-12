"""SE(2) global plan + path tracker. WalkToPose is the body/avoid subskill."""
from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from math import hypot
from typing import Any

import numpy as np
from action.types import MotionCommand
from navigation_safety import CollisionScene

from skills.base import Pose2, Skill, SkillProgress, SkillStatus
from skills.walk_to_pose import WalkToPose, WalkToPoseRequest, arrived

DEFAULT_KEEP_OUT_M = 0.6


def _legacy_path_logger(waypoints):
    # The context-based entry point leaves robot telemetry disabled.
    import bigbrother

    bigbrother.log_path_waypoints(waypoints)


def navigation_imports() -> None:
    """Import planner/tracker dependencies. Used as the chase-node availability check."""
    from navigation_planner import GlobalPlanner, GlobalPlannerConfig  # noqa: F401
    from path_tracker import PathTracker, PathTrackerConfig  # noqa: F401


@dataclass(frozen=True)
class NavigateToPoseRequest:
    """Plan and walk to a world-frame target. ``robot_pose`` is the robot this tick."""

    robot_pose: Pose2
    target_pose: Pose2
    plan_obstacles: tuple[tuple[float, float], ...] = ()
    avoid_obstacles: tuple[tuple[float, float], ...] = ()
    apply_avoidance: bool = True
    keep_out: float = DEFAULT_KEEP_OUT_M
    approach_point: tuple[float, float] | None = None
    go_ball_pos: tuple[float, float] | None = None
    safety_margin: float = 0.0
    distance_tolerance: float = 0.3
    theta_tolerance: float = 0.4
    speed_scale: float = 1.0
    vx_limit: float = 2.2
    vy_limit: float = 1.9
    vtheta_limit: float = 1.3


@dataclass
class NavigateDebug:
    active: bool = False
    source: str = "none"
    path: list | None = None
    goal: tuple[float, float, float] | None = None
    obstacles: list | None = None
    keep_out: float | None = None
    tracker_command: tuple[float, float, float] | None = None
    lookahead: np.ndarray | None = None
    tracker_debug: dict[str, Any] | None = None
    collision_scene: CollisionScene | None = None
    planner_debug: dict[str, Any] | None = None
    failure_reason: str | None = None
    command_reason: str | None = None


def _xy_arrays(points: tuple[tuple[float, float], ...]) -> list[np.ndarray]:
    return [np.array([float(x), float(y)], dtype=float) for x, y in points]


def _walk_request(
    request: NavigateToPoseRequest,
    planned_velocity: tuple[float, float, float],
) -> WalkToPoseRequest:
    return WalkToPoseRequest(
        robot_pose=request.robot_pose,
        target_pose=request.target_pose,
        distance_tolerance=request.distance_tolerance,
        theta_tolerance=request.theta_tolerance,
        speed_scale=request.speed_scale,
        obstacles=request.avoid_obstacles,
        apply_avoidance=request.apply_avoidance,
        planned_velocity=planned_velocity,
    )


class NavigateToPose(Skill):
    """Owns the global planner and path tracker. Writes body via WalkToPose."""

    def __init__(
        self,
        *,
        max_obstacles: int = 10,
        fixed_obstacles: bool = False,
        replan_period_sec: float = 0.25,
        log_warning: Callable[[str], None] | None = None,
        planner: Any = None,
        tracker: Any = None,
        log_paths: bool = True,
    ) -> None:
        if planner is None:
            from navigation_planner import GlobalPlanner, GlobalPlannerConfig

            planner = GlobalPlanner(
                GlobalPlannerConfig(
                    max_obstacles=max_obstacles,
                    fixed_obstacles=fixed_obstacles,
                    replan_period_sec=replan_period_sec,
                ),
                path_logger=_legacy_path_logger if log_paths else None,
            )
        if tracker is None:
            from path_tracker import PathTracker, PathTrackerConfig

            tracker = PathTracker(PathTrackerConfig())
        self._planner = planner
        self._tracker = tracker
        self._walk = WalkToPose()
        self._log_warning = log_warning
        self.debug = NavigateDebug()

    def on_exit(self) -> None:
        """Drop all private planning/tracking state; never modify world information."""
        for component in (self._planner, self._tracker, self._walk):
            reset = getattr(component, "reset", None)
            if reset is not None:
                reset()
        self.debug = NavigateDebug()

    def cancel(self, command: MotionCommand) -> None:
        self.on_exit()
        command.reset()

    def tick(
        self,
        request: NavigateToPoseRequest,
        command: MotionCommand,
        *,
        now_mono: float | None = None,
        field=None,
        collision_scene: CollisionScene | None = None,
    ) -> SkillProgress:
        self.debug = NavigateDebug()
        walk_req = _walk_request(request, (0.0, 0.0, 0.0))
        if arrived(walk_req):
            command.stop_body()
            self.debug.source = "stop"
            return SkillProgress(status=SkillStatus.SUCCEEDED, progress=1.0, reason="arrived")

        planned = self._plan_velocity(
            request, now_mono=now_mono, field=field, collision_scene=collision_scene
        )
        if planned is None:
            command.stop_body()
            if self._log_warning is not None:
                self._log_warning("tracker nav: no global path; stopping")
            return SkillProgress(
                status=SkillStatus.FAILED, progress=0.0,
                reason=self.debug.failure_reason or "no_path",
            )

        result = self._walk.tick(_walk_request(request, planned), command)
        if collision_scene is not None:
            # Check the final command after any local adjustment. No point-only
            # avoidance result can bypass the shared footprint/coverage margins.
            if not np.isfinite((command.x, command.y, command.theta)).all():
                command.stop_body()
                return SkillProgress(SkillStatus.FAILED, reason="navigation_command_invalid")
            velocity = tuple(
                float(np.clip(value, -limit * request.speed_scale, limit * request.speed_scale))
                for value, limit in zip(
                    (command.x, command.y, command.theta),
                    (request.vx_limit, request.vy_limit, request.vtheta_limit),
                )
            )
            limited, reason = collision_scene.limit_command(request.robot_pose, velocity)
            self.debug.command_reason = reason
            if limited is None:
                command.stop_body()
                return SkillProgress(SkillStatus.FAILED, reason=reason)
            command.set_body(*limited)
            command.avoidance_applied = True
            if reason:
                result = SkillProgress(SkillStatus.RUNNING, reason=reason)
        return result

    def _plan_velocity(
        self,
        request: NavigateToPoseRequest,
        *,
        now_mono: float | None = None,
        field=None,
        collision_scene: CollisionScene | None = None,
    ) -> tuple[float, float, float] | None:
        obstacles = _xy_arrays(
            request.plan_obstacles if collision_scene is None
            else tuple(item.centre for item in collision_scene.obstacles)
        )
        robot = request.robot_pose
        target = request.target_pose
        X0 = np.array([robot.x, robot.y, robot.theta], dtype=float)
        goal = np.array([target.x, target.y, target.theta], dtype=float)
        r = hypot(target.x - robot.x, target.y - robot.y)
        plan_goal = goal
        approach_point = request.approach_point
        if approach_point is not None and r > request.distance_tolerance:
            plan_goal = np.array(
                [approach_point[0], approach_point[1], target.theta],
                dtype=float,
            )

        go_ball = (
            None
            if request.go_ball_pos is None
            else np.array(request.go_ball_pos, dtype=float)
        )
        keep_out = float(request.keep_out)
        obstacle_set = self._planner.prepare_obstacles(
            obstacles,
            X0=X0,
            plan_goal=plan_goal,
            go_ball_pos=go_ball,
            **({"footprints": collision_scene.obstacles} if collision_scene is not None else {}),
        )
        obstacles = obstacle_set.selected
        nav_path, obstacle_set = self._planner.update(
            now_mono=time.monotonic() if now_mono is None else now_mono,
            X0=X0,
            plan_goal=plan_goal,
            raw_obstacles=obstacles,
            keep_out=keep_out,
            go_ball_pos=go_ball,
            obstacle_set=obstacle_set,
            safety_margin=float(request.safety_margin) if collision_scene is None else collision_scene.field_margin_m,
            theta_tolerance=float(request.theta_tolerance),
            field=field,
            **({"collision_scene": collision_scene} if collision_scene is not None else {}),
        )
        obstacles = obstacle_set.selected
        path = None if nav_path is None else list(nav_path.waypoints)
        if path is None:
            self.debug.source = "stop"
            self.debug.failure_reason = getattr(self._planner, "last_failure", None)
            return None

        if approach_point is not None:
            last_xy = np.array(path[-1][:2], dtype=float)
            target_xy = goal[:2]
            if float(np.linalg.norm(last_xy - target_xy)) > 1e-3:
                path.append((float(goal[0]), float(goal[1]), float(goal[2]), "ball_approach"))

        if collision_scene is not None:
            self.debug.collision_scene = collision_scene
            reason = collision_scene.path_reason(path, start=X0[:2])
            if reason:
                self.debug.failure_reason = reason
                return None

        self.debug.path = path
        self.debug.goal = (float(target.x), float(target.y), float(target.theta))
        self.debug.obstacles = [np.asarray(o, dtype=float).copy() for o in obstacles]
        self.debug.keep_out = keep_out
        self.debug.planner_debug = dict(nav_path.debug)

        from navigation_types import NavPath

        tracker_path = NavPath(
            waypoints=list(path),
            reused=False if nav_path is None else bool(nav_path.reused),
            direct=False if nav_path is None else bool(nav_path.direct),
            debug={} if nav_path is None else dict(nav_path.debug),
        )
        tracker_result = self._tracker.track(
            X0=X0,
            path=tracker_path,
            goal=goal,
            speed_scale=request.speed_scale,
            vx_limit=request.vx_limit,
            vy_limit=request.vy_limit,
            vtheta_limit=request.vtheta_limit,
            distance_tolerance=request.distance_tolerance,
            theta_tolerance=request.theta_tolerance,
        )
        command = tracker_result.command.as_tuple()
        self.debug.tracker_command = command
        self.debug.lookahead = tracker_result.lookahead.copy()
        self.debug.tracker_debug = dict(tracker_result.debug)
        self.debug.active = True
        self.debug.source = "path_tracker"
        return command

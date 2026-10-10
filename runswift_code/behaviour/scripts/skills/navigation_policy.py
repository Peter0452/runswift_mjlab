"""Navigation's configurable clearance and coverage policy over one frozen view."""

from dataclasses import dataclass
from math import isfinite

from navigation_safety import ClearRegion, CollisionScene
from navigation_types import PlanningObstacle

from skills.uncertainty import UnusableEstimate, check_quality, obstacle_spread


@dataclass(frozen=True)
class NavigationPolicy:
    """Robot enclosing radius, clearance and marginal uncertainty bounds in metres.

    require_clear is the default. allow_unknown is a deliberate, speed-limited
    choice; it never changes the world's coverage labels. Profile names describe
    a detector capability agreed with perception, not arbitrary trust levels.
    """

    robot_radius_m: float = 0.28
    clearance_m: float = 0.04
    uncertainty_sigma: float = 3.0
    obstacle_speed_bound_mps: float = 0.5
    command_horizon_sec: float = 0.5
    unknown_space: str = "require_clear"
    coverage_profile: str | None = None
    max_unknown_speed_mps: float = 0.2
    allowed_obstacle_qualities: tuple[str, ...] = ("nominal", "degraded")

    def __post_init__(self):
        positive = {
            "robot_radius_m",
            "uncertainty_sigma",
            "command_horizon_sec",
            "max_unknown_speed_mps",
        }
        for name in (*positive, "clearance_m", "obstacle_speed_bound_mps"):
            value = getattr(self, name)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
                or value < 0
                or (name in positive and value == 0)
            ):
                raise ValueError(f"Invalid navigation option: {name}")
        if self.unknown_space not in {"require_clear", "allow_unknown"}:
            raise ValueError("Choose require_clear or allow_unknown explicitly")
        if self.coverage_profile is not None and (
            not isinstance(self.coverage_profile, str)
            or not self.coverage_profile.strip()
        ):
            raise ValueError("coverage_profile must name an agreed detector capability")
        qualities = tuple(self.allowed_obstacle_qualities)
        if not qualities or any(
            q not in {"nominal", "degraded", "unknown"} for q in qualities
        ):
            raise ValueError("Choose explicit obstacle qualities")
        object.__setattr__(self, "allowed_obstacle_qualities", qualities)

    def scene(self, context, goal, field, obstacles, pose_spread):
        """Keep measured footprints/covariance and derive one conservative scene."""
        robot_margin = (
            self.robot_radius_m
            + self.clearance_m
            + self.uncertainty_sigma * pose_spread.position_std_m
        )
        footprints = []
        for estimate in obstacles.estimates:
            check_quality(estimate, self.allowed_obstacle_qualities, "obstacle")
            spread = obstacle_spread(estimate)
            state = estimate.value
            if (
                state.frame != obstacles.frame
                or not isfinite(state.radius_m)
                or state.radius_m < 0
                or not all(isfinite(v) for v in (state.position.x, state.position.y))
            ):
                raise UnusableEstimate("obstacle_footprint_invalid")
            # Sum marginal deviations: do not assume independent pose/obstacle
            # errors or attempt to reconstruct unpublished cross-covariance.
            uncertainty = self.uncertainty_sigma * (
                spread.position_std_m + pose_spread.position_std_m
            )
            drift = self.obstacle_speed_bound_mps * (
                (context.now.ns - estimate.meta.state_at.ns) / 1e9
                + self.command_horizon_sec
            )
            radius = (
                state.radius_m
                + self.robot_radius_m
                + self.clearance_m
                + uncertainty
                + drift
            )
            footprints.append(
                PlanningObstacle(
                    state.track_id,
                    (state.position.x, state.position.y),
                    state.radius_m,
                    estimate.covariance.matrix,
                    uncertainty,
                    max(goal.keep_out, radius),
                )
            )

        regions = []
        for view in obstacles.coverage_observations:
            report = view.report
            if (
                view.status != "usable"
                or report.profile_id != self.coverage_profile
                or report.frame != obstacles.frame
                or report.reference_at != obstacles.at
                or view.valid_until.clock_epoch != context.now.clock_epoch
                or not report.reference_at.ns <= context.now.ns < view.valid_until.ns
                or report.boundary_error_m is None
            ):
                continue
            # Coverage can have a different source from the newest detector frame.
            if any(
                h.component == view.meta.id.source and h.status != "ready"
                for h in context.world.snapshot.health
            ):
                continue
            polygons = lambda items: tuple(
                tuple((p.x, p.y) for p in item.vertices) for item in items
            )
            regions.append(
                ClearRegion(
                    polygons(report.inspected),
                    polygons(report.clear),
                    polygons(report.occluded),
                    report.boundary_error_m,
                )
            )
        return CollisionScene(
            tuple(footprints),
            field,
            robot_margin,
            robot_margin + goal.safety_margin,
            tuple(regions),
            self.unknown_space,
            self.command_horizon_sec,
            self.uncertainty_sigma * pose_spread.heading_std_rad,
            self.max_unknown_speed_mps,
        )

"""Pure match policy helpers; inputs are frozen views, progress belongs to behaviour."""

from copy import deepcopy
from dataclasses import dataclass
from math import atan2, cos, hypot, isfinite, sin
from typing import Protocol

from navigation_safety import segment_distance
from skills.uncertainty import UnusableEstimate, ball_spread, pose_spread

from world_model import types as wm


def clamp(value, low, high):
    return max(low, min(high, value))


def angle(value):
    return atan2(sin(value), cos(value))


@dataclass(frozen=True)
class TacticsPolicy:
    """Team tactics and release thresholds; these are reviewed policy, not match rules."""

    goalkeeper_number: int = 1
    restart_displacement_m: float = 0.2
    restart_distance_m: float = 2.0
    role_switch_margin_m: float = 0.4
    role_hold_ns: int = 1_000_000_000
    peer_age_ns: int = 500_000_000
    max_peer_std_m: float = 0.25
    role_uncertainty_sigma: float = 2.0
    lane_uncertainty_sigma: float = 3.0
    goalie_depth_m: float = 0.6
    clear_enter_m: float = 1.8
    clear_exit_m: float = 2.4
    clear_range_m: float = 2.5
    support_behind_m: float = 1.5
    support_side_m: float = 1.4
    dribble_distance_m: float = 1.2
    dribble_kick_x_fraction: float = 1 / 6
    search_turn_after_ns: int = 6_000_000_000
    recovery_timeout_ns: int = 12_000_000_000
    head_height_m: float = 0.65
    max_velocity_std_mps: float = 0.25
    interception_horizon_sec: float = 2.0
    trajectory_age_ns: int = 300_000_000

    def __post_init__(self):
        for name, value in vars(self).items():
            if isinstance(value, bool) or not isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be positive and finite")
            if (name.endswith("_ns") or name == "goalkeeper_number") and type(
                value
            ) is not int:
                raise ValueError(f"{name} must be an integer")
        if self.clear_exit_m <= self.clear_enter_m:
            raise ValueError("Clear exit must exceed entry for hysteresis")
        if self.dribble_kick_x_fraction >= 0.5:
            raise ValueError("Dribble kick line must be inside the field")


class RestartTracker:
    """Remember a restart's measured baseline; absence of evidence never releases it."""

    def __init__(self):
        self.key = self.baseline = None
        self.released = False
        self.active = False
        self.timer = 0

    def update(self, context, ball, sigma, policy):
        report = context.world.match.official
        key = (
            report.game_phase,
            report.set_play,
            report.kicking_team,
            report.first_half,
        )
        if report.state not in {"set", "playing"}:
            self.__init__()
            return False
        active = (
            report.state == "set"
            or report.set_play != "none"
            or report.secondary_seconds > 0
        )
        new_restart = active and (
            not self.active or report.secondary_seconds > self.timer
        )
        self.active, self.timer = active, report.secondary_seconds
        if key != self.key or new_restart:
            self.key, self.baseline, self.released = key, None, False
        if ball is not None:
            spread = ball_spread(ball).position_std_m
            if self.baseline is None:
                self.baseline = (ball.value.position, spread, ball.meta.evidence_at)
            elif ball.meta.evidence_at != self.baseline[2]:
                previous, error, _ = self.baseline
                moved = hypot(
                    ball.value.position.x - previous.x,
                    ball.value.position.y - previous.y,
                )
                threshold = policy.restart_displacement_m
                if report.set_play == "none":
                    threshold = max(
                        threshold, context.world.snapshot.field.centre_circle_radius
                    )
                if moved > threshold + sigma * (spread + error):
                    self.released = True
        # SET keeps capturing the actual placement; movement there is not release.
        if report.state == "set":
            self.released = False
            if ball is not None:
                self.baseline = (ball.value.position, spread, ball.meta.evidence_at)
        return self.released


def fresh_peers(context, policy, check):
    """Eligible same-team reports with explicit no-penalty and usable pose evidence."""
    identity = context.world.snapshot.identity
    report = context.world.match.official
    penalties = {
        p.player_number: p.penalty
        for t in report.teams
        if t.team_number == identity.team_number
        for p in t.players
    }
    result = []
    for peer in context.world.peers:
        if (
            peer.identity.team_number != identity.team_number
            or peer.identity == identity
            or peer.connection != "current"
            or penalties.get(peer.identity.player_number) != "none"
            or peer.report.time_quality != "synchronised"
            or peer.report.event_at.clock_epoch != context.now.clock_epoch
            or not 0 <= context.now.ns - peer.report.event_at.ns < policy.peer_age_ns
            or any(
                h.component == peer.report.id.source and h.status != "ready"
                for h in context.world.health
            )
        ):
            continue
        try:
            check(context, peer.pose)
            spread = pose_spread(peer.pose)
            if (
                peer.pose.value.frame != context.world.snapshot.field.frame
                or peer.pose.meta.quality not in {"nominal", "degraded"}
                or spread.position_std_m > policy.max_peer_std_m
            ):
                continue
        except UnusableEstimate:
            continue
        result.append(peer)
    return tuple(result)


class RoleCoordinator:
    """Choose one chaser by distance with uncertainty, deterministic ties and hysteresis."""

    def __init__(self):
        self.chaser = None
        self.since = None

    def choose(self, context, pose, ball, peers, policy):
        identity = context.world.snapshot.identity
        choices = {identity.player_number: pose}
        choices.update(
            {
                p.identity.player_number: p.pose
                for p in peers
                if p.identity.player_number != policy.goalkeeper_number
                and not (
                    p.reported_intention
                    and p.reported_intention.role in {"goalie", "goalkeeper"}
                )
            }
        )
        p = ball.value.position
        scores = {
            number: hypot(item.value.pose.x - p.x, item.value.pose.y - p.y)
            + policy.role_uncertainty_sigma * pose_spread(item).position_std_m
            for number, item in choices.items()
        }
        best = min(scores, key=lambda n: (scores[n], -n))
        if (
            self.chaser not in scores
            or self.since is None
            or (
                context.now.ns - self.since >= policy.role_hold_ns
                and scores[best] + policy.role_switch_margin_m < scores[self.chaser]
            )
        ):
            self.chaser, self.since = best, context.now.ns
        return "striker" if self.chaser == identity.player_number else "assist"


class Formation(Protocol):
    """Return a target intention in the snapshot field; never read a live model."""

    def target(self, context, role, ball, *, ready): ...


class DefaultFormation:
    """Field-scaled READY slots and ball-relative support, separated by player number."""

    def __init__(self, policy):
        self.policy = policy

    def target(self, context, role, ball, *, ready):
        field = context.world.snapshot.field
        number = context.world.snapshot.identity.player_number
        side = -1 if number % 2 == 0 else 1
        if role == "goalkeeper":
            return wm.Pose2(field.own_goal.centre.x + self.policy.goalie_depth_m, 0, 0)
        if ready:
            return wm.Pose2(
                -field.length * (0.17 + 0.04 * ((number - 1) // 2)),
                side * field.width * (0.12 + 0.06 * ((number - 1) // 2)),
                0,
            )
        if ball is None:
            return None
        p = ball.value.position
        x = clamp(
            p.x - self.policy.support_behind_m,
            -field.length / 2 + 1,
            field.length / 2 - 1,
        )
        y = clamp(
            p.y + side * self.policy.support_side_m,
            -field.width / 2 + 1,
            field.width / 2 - 1,
        )
        return wm.Pose2(x, y, atan2(p.y - y, p.x - x))


class RecordedFormation:
    """Adapter for utils/formation's pure compute_player_position function and JSON.

    The application loads the function/configuration once. No ROS import, path
    manipulation, file access or HTTP request takes place during a decision.
    Unsupported/missing entries fall back to the supplied formation policy.
    """

    def __init__(self, configuration, compute_player_position, fallback):
        self.configuration = deepcopy(configuration)
        self.compute, self.fallback = compute_player_position, fallback

    def target(self, context, role, ball, *, ready):
        if role == "goalkeeper" or (not ready and ball is None):
            return self.fallback.target(context, role, ball, ready=ready)
        field, identity = context.world.snapshot.field, context.world.snapshot.identity
        dimensions = {"length": field.length, "width": field.width}
        for name, areas in (
            ("goal", field.goal_areas),
            ("penalty", field.penalty_areas),
        ):
            if areas:
                points = areas[0].vertices
                dimensions[name + "AreaLength"] = max(p.x for p in points) - min(
                    p.x for p in points
                )
                dimensions[name + "AreaWidth"] = max(p.y for p in points) - min(
                    p.y for p in points
                )
        report = context.world.match.official
        xy = self.compute(
            self.configuration,
            identity.player_number,
            report.game_phase,
            report.state,
            report.set_play,
            report.kicking_team,
            identity.team_number,
            report.first_half,
            (0, 0) if ready else (ball.value.position.x, ball.value.position.y),
            field_dimensions=dimensions,
        )
        if xy is None:
            return self.fallback.target(context, role, ball, ready=ready)
        if len(xy) != 2 or not all(isfinite(v) for v in xy):
            raise UnusableEstimate("formation_target_invalid")
        return wm.Pose2(*xy, 0.0)


def blocking_target(context, ball, policy, sigma):
    """Guard the goal mouth; use approaching velocity only with explicit covariance."""
    field = context.world.snapshot.field
    goal = field.own_goal
    x = goal.centre.x + policy.goalie_depth_m
    if ball is None:
        return wm.Pose2(x, goal.centre.y, 0), "blocking_home"
    p = ball.value.position
    # Goal-post angular bisector, intersected with the guarding line.
    vectors = [
        (goal.centre.x - p.x, goal.centre.y + sign * goal.width / 2 - p.y)
        for sign in (-1, 1)
    ]
    direction = tuple(sum(v[i] / max(1e-9, hypot(*v)) for v in vectors) for i in (0, 1))
    y = p.y + (x - p.x) * direction[1] / direction[0] if direction[0] < -1e-6 else p.y
    reason = "blocking_position"
    velocity, covariance = ball.value.velocity, ball.value.velocity_covariance
    if velocity is not None and covariance is not None:
        from skills.uncertainty import _matrix, _position_std

        try:
            # Velocity has its own covariance, independent of position covariance.
            from dataclasses import replace

            matrix = _matrix(
                replace(ball, covariance=covariance),
                components=("vx", "vy"),
                units=("m/s", "m/s"),
                coordinates="cartesian",
                frame=field.frame,
                kind="velocity",
            )
            error = _position_std(matrix)
            if (
                error <= policy.max_velocity_std_mps
                and velocity.x + sigma * error < 0
                and ball.meta.evidence_at is not None
                and 0
                <= context.now.ns - ball.meta.evidence_at.ns
                < policy.trajectory_age_ns
            ):
                position_error = sigma * ball_spread(ball).position_std_m
                velocity_error = sigma * error
                t_min = (p.x - position_error - x) / (-velocity.x + velocity_error)
                t_max = (p.x + position_error - x) / (-velocity.x - velocity_error)
                bounds = [
                    p.y
                    + side * position_error
                    + t * (velocity.y + direction * velocity_error)
                    for side in (-1, 1)
                    for direction in (-1, 1)
                    for t in (t_min, t_max)
                ]
                if (
                    0 < t_min <= t_max <= policy.interception_horizon_sec
                    and min(bounds) > goal.centre.y - goal.width / 2
                    and max(bounds) < goal.centre.y + goal.width / 2
                ):
                    t = (x - p.x) / velocity.x
                    y, reason = p.y + t * velocity.y, "blocking_intercept"
        except UnusableEstimate:
            pass  # No invented zero velocity: guard geometrically instead.
    y = clamp(
        y, goal.centre.y - goal.width / 2 + 0.3, goal.centre.y + goal.width / 2 - 0.3
    )
    return wm.Pose2(x, y, atan2(p.y - y, p.x - x)), reason


def select_target(
    field, ball, scene, policy, *, clearing=False, restart=False, locked=None
):
    """Choose a shot/clearance lane against every known inflated obstacle; no blind fallback."""
    p = ball.value.position
    if clearing:
        candidates = [
            wm.Point2(
                p.x + policy.clear_range_m * cos(a), p.y + policy.clear_range_m * sin(a)
            )
            for a in (0, -0.35, 0.35, -0.7, 0.7, -1.1, 1.1)
        ]
        candidates = [
            q
            for q in candidates
            if abs(q.x) < field.length / 2 - 0.4 and abs(q.y) < field.width / 2 - 0.4
        ]
    elif restart:
        candidates = [wm.Point2(field.opponent_goal.centre.x - 1.0, 0)]
    else:
        centre = field.opponent_goal.centre
        candidates = [
            wm.Point2(centre.x, centre.y + f * field.opponent_goal.width)
            for f in (0, -0.25, 0.25, -0.4, 0.4)
        ]
    if locked is not None:
        candidates.insert(0, locked)
    error = policy.lane_uncertainty_sigma * ball_spread(ball).position_std_m
    for q in candidates:
        if q.x <= p.x:  # Team field always has our goal on negative X.
            continue
        if all(
            segment_distance((p.x, p.y), (q.x, q.y), o.centre) > o.keep_out_m + error
            for o in scene.obstacles
            if o.track_id != "tactical-ball"
        ):
            return q
    raise UnusableEstimate("no_clear_kick_lane")


@dataclass(frozen=True)
class TeamBroadcast:
    """Local observations and our intention, with original evidence times and covariance."""

    at: wm.TimePoint
    snapshot_id: wm.SnapshotId
    report: wm.PeerReport


def team_broadcast(context, role, chasing, pose, ball):
    """Build data only; the application owns encoding, rate limiting and transport."""
    return TeamBroadcast(
        context.now,
        context.world.snapshot.id,
        wm.PeerReport(
            context.world.snapshot.identity,
            None if pose is None else pose.value,
            None
            if ball is None
            else wm.PeerBallReport(
                ball.value, ball.meta.state_at, ball.meta.evidence_at, ball.covariance
            ),
            wm.PeerIntention(role, chasing),
            None if pose is None else pose.meta.evidence_at,
            None if pose is None else pose.covariance,
        ),
    )


@dataclass(frozen=True)
class LocalisationHint:
    """Request a localisation search mode; an application adapter decides how to apply it."""

    at: wm.TimePoint
    snapshot_id: wm.SnapshotId
    mode: str = "own_half"


class TeamReportPort(Protocol):
    """Non-blocking outbound transport; preserve the packet's original evidence times."""

    def send(self, report: TeamBroadcast) -> None: ...


class LocalisationPort(Protocol):
    """Non-blocking application request port; results arrive through normal world inputs."""

    def send(self, hint: LocalisationHint) -> None: ...

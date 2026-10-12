"""Behaviour policies over published covariance; no filtering or frame transforms.

Margins are configurable covariance-based screens, not calibrated probabilities
or guarantees. Unknown/unsupported covariance is rejected, never taken as zero.
"""

from dataclasses import dataclass
from math import hypot, isfinite, sqrt

import numpy as np
from world_model.types import BallState, Estimate, FramedPose2, ObstacleState


class UnusableEstimate(Exception):
    """A skill requirement was not met; the adapter returns a stopped failure."""


def _positive(value, name):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not isfinite(value)
        or value <= 0
    ):
        raise ValueError(f"{name} must be finite and positive")


def _qualities(policy):
    values = tuple(policy.allowed_qualities)
    if not values or any(
        value not in {"nominal", "degraded", "unknown"} for value in values
    ):
        raise ValueError("Choose explicit nominal, degraded or unknown qualities")
    object.__setattr__(policy, "allowed_qualities", values)


@dataclass(frozen=True)
class PosePolicy:
    """Walking/circling precision limits and a margin for arrival/progress checks."""

    max_position_std_m: float = 0.25
    max_heading_std_rad: float = 0.25
    margin_sigma: float = 2.0
    minimum_speed_scale: float = 0.25
    allowed_qualities: tuple[str, ...] = ("nominal", "degraded")

    def __post_init__(self):
        for name in (
            "max_position_std_m",
            "max_heading_std_rad",
            "margin_sigma",
            "minimum_speed_scale",
        ):
            _positive(getattr(self, name), name)
        if self.minimum_speed_scale > 1:
            raise ValueError("minimum_speed_scale must be at most one")
        _qualities(self)

    def assess(self, estimate):
        """Retain the estimate and validate pose precision before issuing movement."""
        check_quality(estimate, self.allowed_qualities, "pose")
        spread = pose_spread(estimate)
        if spread.position_std_m > self.max_position_std_m:
            raise UnusableEstimate("pose_position_uncertain")
        if spread.heading_std_rad > self.max_heading_std_rad:
            raise UnusableEstimate("pose_heading_uncertain")
        return spread

    def speed_scale(self, spread):
        fraction = max(
            spread.position_std_m / self.max_position_std_m,
            spread.heading_std_rad / self.max_heading_std_rad,
        )
        return max(self.minimum_speed_scale, 1.0 - fraction)


@dataclass(frozen=True)
class KickPolicy:
    """Local-ball precision plus a conservative fixed-target angular screen."""

    max_ball_std_m: float = 0.08
    max_heading_std_rad: float = 0.15
    max_aim_margin_rad: float = 0.25
    margin_sigma: float = 2.0
    allowed_qualities: tuple[str, ...] = ("nominal", "degraded")

    def __post_init__(self):
        for name in (
            "max_ball_std_m",
            "max_heading_std_rad",
            "max_aim_margin_rad",
            "margin_sigma",
        ):
            _positive(getattr(self, name), name)
        _qualities(self)

    def assess_ball(self, estimate):
        check_quality(estimate, self.allowed_qualities, "ball")
        spread = ball_spread(estimate)
        if spread.position_std_m > self.max_ball_std_m:
            raise UnusableEstimate("ball_position_uncertain")
        return spread

    def assess_aim(self, pose, ball, target):
        """Screen marginal heading/bearing errors without assuming independence.

        Use the sum of their standard-deviation bounds, not independent variance
        addition. This is a first-order screen for a fixed, exact target; it is
        deliberately conservative when joint correlations are not published.
        """
        check_quality(pose, self.allowed_qualities, "pose")
        check_quality(ball, self.allowed_qualities, "ball")
        pose_error, ball_error = pose_spread(pose), ball_spread(ball)
        if pose_error.heading_std_rad > self.max_heading_std_rad:
            raise UnusableEstimate("pose_heading_uncertain")
        position = ball.value.position
        distance = hypot(target.x - position.x, target.y - position.y)
        if distance <= self.margin_sigma * ball_error.position_std_m:
            raise UnusableEstimate("kick_target_uncertain")
        margin = self.margin_sigma * (
            pose_error.heading_std_rad + ball_error.position_std_m / distance
        )
        if margin > self.max_aim_margin_rad:
            raise UnusableEstimate("kick_direction_uncertain")
        return margin


@dataclass(frozen=True)
class EstimateSpread:
    """A checked estimate and its largest planar positional/heading deviations."""

    estimate: Estimate
    position_std_m: float
    heading_std_rad: float | None = None


def check_quality(estimate, allowed, kind):
    if estimate.meta.quality not in allowed:
        raise UnusableEstimate(f"{kind}_quality_rejected")


def _matrix(estimate, *, components, units, coordinates, frame, kind):
    covariance = estimate.covariance
    if covariance is None:
        raise UnusableEstimate(f"{kind}_uncertainty_unknown")
    if (
        frame is None
        or covariance.frame != frame
        or covariance.components != components
        or covariance.units != units
        or covariance.coordinates != coordinates
    ):
        raise UnusableEstimate(f"{kind}_covariance_convention")
    size = len(components)
    matrix = np.asarray(covariance.matrix, dtype=float)
    if (
        matrix.shape != (size, size)
        or not np.isfinite(matrix).all()
        or not np.allclose(matrix, matrix.T, atol=1e-12, rtol=0)
    ):
        raise UnusableEstimate(f"{kind}_covariance_invalid")
    # Scale by marginal deviations so metres and radians are not compared via
    # one eigenvalue tolerance. Zero variance must have a zero cross-covariance.
    diagonal = matrix.diagonal()
    if np.any(diagonal < 0):
        raise UnusableEstimate(f"{kind}_covariance_invalid")
    scale = np.sqrt(diagonal)
    zero = scale == 0
    if np.any(matrix[zero, :] != 0):
        raise UnusableEstimate(f"{kind}_covariance_invalid")
    indices = np.flatnonzero(~zero)
    if len(indices):
        corr = matrix[np.ix_(indices, indices)] / np.outer(
            scale[indices], scale[indices]
        )
        if np.linalg.eigvalsh(corr).min() < -1e-10:
            raise UnusableEstimate(f"{kind}_covariance_invalid")
    return matrix


def _position_std(matrix):
    # Largest eigenvalue of the planar positional block: rotation invariant and
    # sensitive to off-diagonal correlations, unlike max(diagonal).
    a, b, d = matrix[0, 0], matrix[0, 1], matrix[1, 1]
    return sqrt(max(0.0, (a + d + hypot(a - d, 2 * b)) / 2))


def pose_spread(estimate):
    """Read Cartesian field/odom covariance or the published base right tangent."""
    if not isinstance(estimate.value, FramedPose2):
        raise UnusableEstimate("pose_estimate_type")
    value = estimate.value
    tangent = (
        estimate.covariance is not None
        and estimate.covariance.coordinates == "right_tangent"
    )
    matrix = _matrix(
        estimate,
        components=("forward", "lateral", "turn") if tangent else ("x", "y", "theta"),
        units=("m", "m", "rad"),
        coordinates="right_tangent" if tangent else "cartesian",
        frame=value.child_frame if tangent else value.frame,
        kind="pose",
    )
    if tangent and (value.child_frame.name != "robot_base"):
        raise UnusableEstimate("pose_covariance_convention")
    return EstimateSpread(estimate, _position_std(matrix), sqrt(matrix[2, 2]))


def ball_spread(estimate):
    """Read a planar point covariance in the same frame as the ball value."""
    if not isinstance(estimate.value, BallState):
        raise UnusableEstimate("ball_estimate_type")
    matrix = _matrix(
        estimate,
        components=("x", "y"),
        units=("m", "m"),
        coordinates="cartesian",
        frame=estimate.value.frame,
        kind="ball",
    )
    return EstimateSpread(estimate, _position_std(matrix))


def obstacle_spread(estimate):
    """Validate a footprint's published planar covariance without losing correlation."""
    if not isinstance(estimate.value, ObstacleState):
        raise UnusableEstimate("obstacle_estimate_type")
    matrix = _matrix(
        estimate,
        components=("x", "y"),
        units=("m", "m"),
        coordinates="cartesian",
        frame=estimate.value.frame,
        kind="obstacle",
    )
    return EstimateSpread(estimate, _position_std(matrix))

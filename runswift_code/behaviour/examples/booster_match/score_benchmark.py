"""Fixed benchmark cases and explicit simulator-to-team-field mapping."""

from dataclasses import dataclass, replace
from math import atan2, ceil, cos, hypot, isfinite, pi, sin
from random import Random

from world_match_replay import open_play_report
from world_model_ros.booster import BoosterBatchBuilder

from world_model import types as wm


@dataclass(frozen=True)
class Case:
    """Physical simulator placement, fixed before a trial begins."""

    name: str
    direction: int
    ball: tuple[float, float]
    start: tuple[float, float]
    yaw: float
    power: float = 1.5
    ball_id: str | None = None
    start_id: str | None = None


def cases():
    """Three distinct short-range layouts, rotated 180 degrees for the other goal."""
    layouts = (
        ("centre", (4.0, 0.0), (2.2, -0.5), 0.2),
        ("left", (4.0, 0.6), (2.4, 1.4), -0.3),
        ("right", (3.5, -0.6), (1.9, -1.4), 0.3),
    )
    return tuple(
        Case(
            f"{label}-{side}",
            direction,
            tuple(direction * v for v in ball),
            tuple(direction * v for v in start),
            atan2(
                sin(yaw + (pi if direction < 0 else 0)),
                cos(yaw + (pi if direction < 0 else 0)),
            ),
        )
        for direction, side in ((1, "positive"), (-1, "negative"))
        for label, ball, start, yaw in layouts
    )


GRID_X = (-4.5, 0.0, 4.5)
GRID_Y = (-2.5, 0.0, 2.5)
DEFAULT_SEED = 20261002


def robot_starts(seed=DEFAULT_SEED):
    """Seeded placements within five deliberate approach/heading strata, in metres."""
    rng = Random(seed)
    strata = (
        ("west-away", (-5.8, -5.4), (-0.4, 0.4), pi),
        ("east-away", (5.4, 5.8), (-0.4, 0.4), 0.0),
        ("north-away", (-1.8, -1.2), (3.7, 3.9), pi / 2),
        ("south-away", (1.2, 1.8), (-3.9, -3.7), -pi / 2),
        ("central-oblique", (1.2, 1.6), (0.9, 1.3), -3 * pi / 4),
    )
    return tuple(
        (
            name,
            (round(rng.uniform(*xs), 3), round(rng.uniform(*ys), 3)),
            round(yaw + rng.uniform(-0.15, 0.15), 6),
        )
        for name, xs, ys, yaw in strata
    )


def grid_cases(seed=DEFAULT_SEED):
    """Nine balls × five identical physical starts × two goals; never mirror starts."""
    result = tuple(
        Case(
            f"x{ix}-y{iy}-{name}-{side}",
            direction,
            (x, y),
            start,
            yaw,
            ball_id=f"x{ix}-y{iy}",
            start_id=name,
        )
        for ix, x in enumerate(GRID_X, 1)
        for iy, y in enumerate(GRID_Y, 1)
        for name, start, yaw in robot_starts(seed)
        for direction, side in ((1, "positive"), (-1, "negative"))
    )
    for case in result:
        validate_case(case)
    return result


def validate_case(case):
    """Reject invalid or overlapping initial placements before connecting to motion."""
    if case.direction not in (-1, 1) or not all(
        isfinite(v) for v in (*case.ball, *case.start, case.yaw, case.power)
    ):
        raise ValueError("Case requires finite coordinates and a goal direction")
    if not 1 <= case.power <= 2:
        raise ValueError("Pilot power must be in [1, 2]")
    for position in (case.ball, case.start):
        if abs(position[0]) > 6.4 or abs(position[1]) > 3.9:
            raise ValueError(
                "Placement must retain at least 0.6 m field-edge clearance"
            )
    if hypot(case.ball[0] - case.start[0], case.ball[1] - case.start[1]) < 1.0:
        raise ValueError("Robot must start at least 1 m from the ball")


def suite_cases(suite, seed=DEFAULT_SEED):
    """Select the original smoke run, the full grid, or a six-case grid preflight."""
    if suite == "smoke":
        return cases()
    values = grid_cases(seed)
    if suite == "grid":
        return values
    if suite != "preflight":
        raise ValueError("Unknown benchmark suite")
    chosen = {
        "x2-y2-east-away-positive",  # Between the ball and +X goal, facing away.
        "x2-y2-west-away-negative",  # Same challenge towards -X.
        "x3-y3-north-away-positive",  # Near a touchline, facing out of the field.
        "x1-y1-south-away-negative",  # Opposite touchline and goal direction.
        "x3-y2-west-away-positive",  # Long approach, initially facing away.
        "x1-y2-east-away-negative",
    }
    return tuple(c for c in values if c.name in chosen)


def execution_budget(case):
    """Wall-time budget for travel, circling, turning and one bounded shot/stop."""
    # Travel at the fixture's 0.2 m/s cap, with 50% allowance for slow tracking
    # and 2 m for going around the ball. Another 25 s covers turning/referee/
    # the existing 8 s activation and 2 s stop. This never alters watchdogs.
    distance = hypot(case.ball[0] - case.start[0], case.ball[1] - case.start[1])
    return max(45, ceil((1.5 * distance + 2.0) / 0.2 + 25))


def team_frame(frame, direction):
    """Rotate the whole captured scene, preserving time and body-relative geometry."""
    if direction not in (-1, 1):
        raise ValueError("Direction must be +1 or -1")
    if direction == 1:
        return frame

    def point(p):
        return (-p[0], -p[1], p[2])

    return replace(
        frame,
        ball=None if frame.ball is None else point(frame.ball),
        robots=tuple(
            replace(
                r,
                position=point(r.position),
                yaw=atan2(sin(r.yaw + pi), cos(r.yaw + pi)),
            )
            for r in frame.robots
        ),
    )


class BenchmarkInputs(BoosterBatchBuilder):
    """Ground-truth inputs in team field; raw physical truth stays with the evaluator."""

    def __init__(self, *args, direction, **kwargs):
        super().__init__(*args, **kwargs)
        self.direction, self.state = direction, "initial"

    def build(self, frame):
        batch = super().build(team_frame(frame, self.direction))
        report = wm.WorldEvent(
            wm.InputMeta(
                wm.EventId("scripted-referee", self.epoch, batch.sequence),
                None,
                batch.as_of,
                batch.as_of,
                "synchronised",
                0,
                self.config.configuration_id,
            ),
            open_play_report(state=self.state),
        )
        return replace(batch, events=(*batch.events, report))

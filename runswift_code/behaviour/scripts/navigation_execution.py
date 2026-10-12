"""Behaviour-side navigation lifetime and expiring motion hand-off; no ROS or SDK."""

from dataclasses import dataclass
from time import monotonic_ns

from action.types import MotionCommand
from skills.base import SkillStatus


@dataclass(frozen=True)
class ExecutionResult:
    status: str
    reason: str
    velocity: tuple[float, float, float]


class NavigationExecutive:
    """Own a goal and cancellation, leaving model updates and motion expiry independent."""

    def __init__(
        self, navigation, motion, *, wall_clock=monotonic_ns, observation_ns=350_000_000
    ):
        if type(observation_ns) is not int or not 0 < observation_ns <= 350_000_000:
            raise ValueError("Observation deadline must be at most 350 ms")
        self.navigation, self.motion = navigation, motion
        self._wall, self.observation_ns = wall_clock, observation_ns
        self.command = MotionCommand()
        self.goal = None
        self.result = ExecutionResult("idle", "no_goal", (0.0, 0.0, 0.0))

    def start(self, goal):
        """Explicitly start a new intention after discarding previous navigation state."""
        self.cancel("goal_replaced")
        self.goal = goal
        self.result = ExecutionResult("running", "started", (0.0, 0.0, 0.0))

    def cancel(self, reason="cancelled"):
        """Revoke the motion lease immediately and discard cached paths/progress."""
        self.goal = None
        self.navigation.cancel(self.command)
        self.result = ExecutionResult("stopped", reason, (0.0, 0.0, 0.0))
        self.motion.stop()
        return self.result

    def tick(self, context, received_wall_ns):
        """Use one context, with source receipt time supplied atomically by its owner."""
        if self.goal is None:
            return self.result
        now = self._wall()
        if (
            received_wall_ns is None
            or type(received_wall_ns) is not int
            or not 0 <= now - received_wall_ns < self.observation_ns
        ):
            return self.cancel("observations_expired")
        result = self.navigation.tick(context, self.goal, self.command)
        if result.status == SkillStatus.FAILED:
            return self.cancel(result.reason)
        if result.status == SkillStatus.SUCCEEDED:
            self.cancel(result.reason)
            self.result = ExecutionResult("succeeded", result.reason, (0.0, 0.0, 0.0))
            return self.result
        # Planning time also consumes the observation budget. Never stamp an
        # already stale decision as a fresh command after a slow planner call.
        deadline = received_wall_ns + self.observation_ns
        if self._wall() >= deadline:
            return self.cancel("observations_expired")
        velocity = (self.command.x, self.command.y, self.command.theta)
        try:
            self.motion.send(velocity, deadline)
        except (OSError, RuntimeError, ValueError):
            # Drop the intention/cache before propagating a failed hand-off.
            # The independent relay also expires the previous lease if the
            # transport cannot carry this explicit stop.
            try:
                self.cancel("motion_transport_failed")
            except (OSError, RuntimeError, ValueError):
                pass
            raise
        self.result = ExecutionResult("running", result.reason, velocity)
        return self.result

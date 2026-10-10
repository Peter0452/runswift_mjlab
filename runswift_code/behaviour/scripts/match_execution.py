"""Match lifetime and motion hand-off; world ownership stays with the application."""

from dataclasses import dataclass
from time import monotonic_ns
from uuid import uuid4

from action.match_intent import MatchIntent, MatchMotionPort
from action.types import MotionCommand
from match_runner import MatchGoal, MatchRunner, MotionFeedback
from skills.base import SkillStatus
from world_model.types import SnapshotId

from world_model import TickContext


@dataclass(frozen=True)
class MatchExecutionResult:
    """Explain the decision and identify the frozen snapshot used to make it."""

    status: str
    state: str
    reason: str
    tick_id: int | None = None
    snapshot_id: SnapshotId | None = None
    intent: MatchIntent | None = None


class MatchExecutive:
    """Own start/cancel and deadlines; send no more than one intent per tick."""

    def __init__(
        self,
        runner: MatchRunner,
        motion: MatchMotionPort,
        *,
        wall_clock=monotonic_ns,
        observation_ns=350_000_000,
        command_ns=250_000_000,
        session=None,
        team_port=None,
        localisation_port=None,
        team_period_ns=500_000_000,
    ):
        if type(observation_ns) is not int or not 0 < observation_ns <= 350_000_000:
            raise ValueError("Observation lifetime must be at most 350 ms")
        if type(command_ns) is not int or not 0 < command_ns <= 250_000_000:
            raise ValueError("Command lifetime must be at most 250 ms")
        self.runner, self.motion, self._wall = runner, motion, wall_clock
        self.observation_ns, self.command_ns = observation_ns, command_ns
        self.session, self._sequence = str(uuid4()) if session is None else session, 0
        if not isinstance(self.session, str) or not self.session:
            raise ValueError("A non-empty motion session is required")
        if type(team_period_ns) is not int or team_period_ns <= 0:
            raise ValueError("Team report period must be positive integer nanoseconds")
        self.team_port, self.team_period_ns = team_port, team_period_ns
        self.localisation_port = localisation_port
        self._localisation_requested = False
        self._team_at = None
        self.goal = None
        self.command = MotionCommand()
        self.result = MatchExecutionResult("idle", "stand", "not_started")

    def start(self, goal: MatchGoal):
        """Explicitly arm a tactical intention, discarding previous progress."""
        self.cancel("goal_replaced")
        self.goal = goal
        self._team_at = None
        self._localisation_requested = False

    def cancel(self, reason="cancelled"):
        """Clear all behaviour state and revoke motion, including SDK kick mode."""
        self.goal = None
        self.runner.cancel(self.command)
        self.result = MatchExecutionResult("stopped", "stand", reason)
        self.motion.stop()
        return self.result

    def tick(
        self,
        context: TickContext,
        received_wall_ns: int | None,
        *,
        motion: MotionFeedback | None = None,
    ):
        """Consume an already captured context and its atomic input-receipt time."""
        if self.goal is None:
            return self.result
        now = self._wall()
        if (
            type(received_wall_ns) is not int
            or not 0 <= now - received_wall_ns < self.observation_ns
        ):
            return self.cancel("observations_expired")
        try:
            progress = self.runner.tick(context, self.goal, self.command, motion=motion)
            if progress.status == SkillStatus.FAILED:
                return self.cancel(progress.reason)
            now = self._wall()
            deadline = min(
                received_wall_ns + self.observation_ns, now + self.command_ns
            )
            if now >= deadline:
                return self.cancel("observations_expired")
            command = self.command
            kick = (
                (
                    command.kick_direction,
                    command.kick_power,
                    command.kick_ball_x,
                    command.kick_ball_y,
                )
                if command.kick_active
                else None
            )
            intent = MatchIntent(
                self.session,
                self._sequence,
                now,
                deadline,
                (command.x, command.y, command.theta),
                command.head_targets(),
                kick,
                self.runner.attempt_id if kick is not None else None,
                command.recovery_attempt_id,
            )
            self._sequence += 1
            self.motion.send(intent)
            if self.runner.localisation_hint is None:
                self._localisation_requested = False
            elif (
                self.localisation_port is not None and not self._localisation_requested
            ):
                self.localisation_port.send(self.runner.localisation_hint)
                self._localisation_requested = True
            broadcast = self.runner.broadcast
            if (
                self.team_port is not None
                and broadcast is not None
                and (
                    self._team_at is None
                    or context.now.ns - self._team_at >= self.team_period_ns
                )
            ):
                self.team_port.send(broadcast)
                self._team_at = context.now.ns
        except Exception as error:
            # Unexpected calculation/transport failures also revoke the previous
            # command. The receiver's independent gate bounds a failed stop send.
            try:
                self.cancel("match_execution_failed")
            except Exception as stop_error:  # noqa: BLE001 -- preserve both failures
                error.add_note(f"Motion stop also failed: {stop_error}")
            raise
        self.result = MatchExecutionResult(
            "running",
            self.runner.state,
            progress.reason,
            context.tick_id,
            context.world.snapshot.id,
            intent,
        )
        return self.result

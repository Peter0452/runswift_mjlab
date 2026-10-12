"""Bounded body-velocity leases for an independently scheduled motion watchdog.

Only Python standard-library types cross this boundary. Sender and receiver
must share the same Linux monotonic clock (host and its ordinary container).
"""

from dataclasses import dataclass
from math import hypot, isfinite

ZERO = (0.0, 0.0, 0.0)
SCHEMA = "runswift-sim-motion/1"


@dataclass(frozen=True)
class VelocityLease:
    """A command expires at the earlier of its own and its observation deadline."""

    session: str
    sequence: int
    issued_ns: int
    command_until_ns: int
    observation_until_ns: int
    velocity: tuple[float, float, float]

    def message(self):
        return {
            "schema": SCHEMA,
            "session": self.session,
            "sequence": self.sequence,
            "issued_ns": self.issued_ns,
            "command_until_ns": self.command_until_ns,
            "observation_until_ns": self.observation_until_ns,
            "velocity": list(self.velocity),
        }


class VelocityLeaseGate:
    """Validate leases and latch expiry; a failed gate requires a new session."""

    def __init__(
        self,
        session,
        *,
        max_command_ns=250_000_000,
        max_observation_ns=350_000_000,
        max_speed=0.2,
        max_turn=0.8,
    ):
        if not isinstance(session, str) or not session:
            raise ValueError("A session is required")
        if any(
            type(v) is not int or v <= 0 for v in (max_command_ns, max_observation_ns)
        ):
            raise ValueError("Deadlines must be positive integer nanoseconds")
        if any(not isfinite(v) or v <= 0 for v in (max_speed, max_turn)):
            raise ValueError("Velocity limits must be positive and finite")
        self.session = session
        self.max_command_ns, self.max_observation_ns = (
            max_command_ns,
            max_observation_ns,
        )
        self.max_speed, self.max_turn = max_speed, max_turn
        self.lease = None
        self.sequence = -1
        self.failure = None
        self.expired_at_ns = None
        self.reason = "idle"

    def fail(self, reason):
        self.failure = self.failure or reason
        self.reason = self.failure
        self.lease = None

    def accept(self, message, now_ns):
        """Reject delayed/reordered/oversized commands instead of extending their life."""
        if self.failure:
            return False
        # A newly arriving command cannot hide a missed watchdog deadline.
        self.velocity(now_ns)
        if self.failure:
            return False
        try:
            fields = {
                "schema",
                "session",
                "sequence",
                "issued_ns",
                "command_until_ns",
                "observation_until_ns",
                "velocity",
            }
            if not isinstance(message, dict) or set(message) != fields:
                raise ValueError("invalid_motion_fields")
            if message["schema"] != SCHEMA or message["session"] != self.session:
                raise ValueError("motion_session_mismatch")
            seq, issued, command, observation = (
                message[k]
                for k in (
                    "sequence",
                    "issued_ns",
                    "command_until_ns",
                    "observation_until_ns",
                )
            )
            if any(
                type(v) is not int or v < 0 for v in (seq, issued, command, observation)
            ):
                raise ValueError("invalid_motion_time")
            if seq <= self.sequence:
                raise ValueError("motion_reordered")
            if not 0 <= now_ns - issued <= self.max_command_ns:
                raise ValueError("motion_clock_or_delivery_error")
            velocity = message["velocity"]
            if not isinstance(velocity, (tuple, list)) or len(velocity) != 3:
                raise ValueError("invalid_velocity")
            if any(type(v) not in (int, float) or not isfinite(v) for v in velocity):
                raise ValueError("invalid_velocity")
            velocity = tuple(float(v) for v in velocity)
            if (
                hypot(*velocity[:2]) > self.max_speed + 1e-9
                or abs(velocity[2]) > self.max_turn
            ):
                raise ValueError("velocity_exceeds_limit")
            # Zero commands revoke the lease immediately, including cancellation.
            if velocity == ZERO:
                self.sequence, self.lease, self.reason = seq, None, "stopped"
                return True
            if not now_ns < command <= issued + self.max_command_ns:
                raise ValueError("command_expired_or_unbounded")
            if not now_ns < observation <= issued + self.max_observation_ns:
                raise ValueError("observation_expired_or_unbounded")
            self.lease = VelocityLease(
                self.session, seq, issued, command, observation, velocity
            )
            self.sequence, self.reason = seq, "moving"
            return True
        except (ValueError, TypeError, OverflowError) as exc:
            self.fail(str(exc))
            return False

    def velocity(self, now_ns):
        """Call independently of command receipt, including when input is silent."""
        if self.lease is not None and now_ns >= min(
            self.lease.command_until_ns, self.lease.observation_until_ns
        ):
            self.expired_at_ns = min(
                self.lease.command_until_ns, self.lease.observation_until_ns
            )
            reason = (
                "observation_expired"
                if self.lease.observation_until_ns <= self.lease.command_until_ns
                else "command_expired"
            )
            self.fail(reason)
        return ZERO if self.lease is None else self.lease.velocity

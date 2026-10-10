"""Immutable, expiring match intents at the behaviour/motion boundary (no SDK)."""

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Protocol


@dataclass(frozen=True)
class MatchIntent:
    """One atomic body/head/kick command; all fields share one absolute deadline.

    A receiver must disable its previous kick when kick is None, on stop, or on
    expiry. Retaining an SDK kick mode after the lease expires is not permitted.
    """

    session: str
    sequence: int
    issued_ns: int
    valid_until_ns: int
    velocity: tuple[float, float, float]
    head: tuple[float, float, float, float]
    kick: tuple[float, float, float, float] | None
    kick_attempt_id: str | None
    recovery_attempt_id: str | None = None

    def __post_init__(self):
        if (
            not isinstance(self.session, str)
            or not self.session
            or type(self.sequence) is not int
            or self.sequence < 0
        ):
            raise ValueError("A session and non-negative sequence are required")
        if any(
            type(v) is not int or v < 0 for v in (self.issued_ns, self.valid_until_ns)
        ):
            raise ValueError("Deadlines must be non-negative integer nanoseconds")
        if not 0 < self.valid_until_ns - self.issued_ns <= 250_000_000:
            raise ValueError("Intent lifetime must be at most 250 ms")
        fields = ((self.velocity, 3), (self.head, 4))
        if self.kick is not None:
            fields += ((self.kick, 4),)
        for values, size in fields:
            if (
                not isinstance(values, tuple)
                or len(values) != size
                or any(type(v) not in (int, float) or not isfinite(v) for v in values)
            ):
                raise ValueError("Intent values must be finite immutable tuples")
        if self.kick is not None and (
            not isinstance(self.kick_attempt_id, str)
            or not self.kick_attempt_id
            or any(self.velocity)
        ):
            raise ValueError("Kick requires an attempt ID and exclusive body control")
        if self.recovery_attempt_id is not None and (
            not isinstance(self.recovery_attempt_id, str)
            or not self.recovery_attempt_id
            or self.kick is not None
            or any(self.velocity)
        ):
            raise ValueError("Recovery requires an ID and exclusive body control")
        if self.kick is None and self.kick_attempt_id is not None:
            raise ValueError("An attempt ID requires a kick")

    def message(self):
        """Encode the complete intent without replacing its absolute timestamps."""
        values = asdict(self)
        if self.recovery_attempt_id is None:
            values.pop("recovery_attempt_id")
            return {"schema": "runswift-match/1", **values}
        return {"schema": "runswift-match/2", **values}

    @classmethod
    def parse(cls, message):
        """Validate the IPC schema before admitting a command to the actuator."""
        fields = {
            "schema",
            "session",
            "sequence",
            "issued_ns",
            "valid_until_ns",
            "velocity",
            "head",
            "kick",
            "kick_attempt_id",
        }
        if isinstance(message, dict) and message.get("schema") == "runswift-match/2":
            fields.add("recovery_attempt_id")
        if (
            not isinstance(message, dict)
            or set(message) != fields
            or message["schema"] not in {"runswift-match/1", "runswift-match/2"}
        ):
            raise ValueError("Invalid match intent schema")
        args = {k: v for k, v in message.items() if k != "schema"}
        for name in ("velocity", "head", "kick"):
            if name == "kick" and args[name] is None:
                continue
            if not isinstance(args[name], (list, tuple)):
                raise TypeError("Invalid intent vector")
            args[name] = tuple(args[name])
        return cls(**args)


class MatchMotionPort(Protocol):
    """Non-blocking transport to an independently scheduled, expiring actuator."""

    def send(self, intent: MatchIntent) -> None:
        """Admit the intent without restamping or extending its deadline."""
        ...

    def stop(self) -> None:
        """Revoke body/head/kick and fence all previously sent, possibly queued intents."""
        ...


class MatchIntentGate:
    """Receiver-side expiry and ordering; faults latch until a new session.

    The actuator calls current() independently of the behaviour loop and applies
    a stop (including kick disable) when it returns None. This is a gate, not an
    SDK driver or a watchdog thread. Sender and receiver share a monotonic clock.
    """

    def __init__(self, session):
        if not isinstance(session, str) or not session:
            raise ValueError("A session is required")
        self.session = session
        self.sequence = -1
        self.intent = None
        self.failure = None
        self.expired_at_ns = None

    def fail(self, reason):
        self.failure = self.failure or reason
        self.stop()

    def stop(self, *, through_sequence=None):
        """Revoke the lease; transports supply their last sent sequence to fence queues."""
        if through_sequence is not None:
            if type(through_sequence) is not int or through_sequence < self.sequence:
                raise ValueError("Stop fence must cover all admitted intents")
            self.sequence = through_sequence
        self.intent = None

    def current(self, now_ns):
        if self.intent is not None and now_ns >= self.intent.valid_until_ns:
            self.expired_at_ns = self.intent.valid_until_ns
            self.fail("match_intent_expired")
        return self.intent

    def accept(self, intent, now_ns):
        self.current(now_ns)
        if self.failure:
            return False
        if (
            not isinstance(intent, MatchIntent)
            or intent.session != self.session
            or intent.sequence <= self.sequence
            or not intent.issued_ns <= now_ns < intent.valid_until_ns
        ):
            self.failure = "invalid_or_delayed_match_intent"
            self.stop()
            return False
        self.sequence, self.intent = intent.sequence, intent
        return True

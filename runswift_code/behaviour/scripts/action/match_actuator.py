"""Independently scheduled match actuator; SDK and world-model independent, Python 3.10+."""

from dataclasses import asdict, dataclass
from math import hypot, isfinite

from action.match_intent import MatchIntentGate


@dataclass(frozen=True)
class MotionSample:
    """SDK feedback with original monotonic receipt times; reads never renew it."""

    observed_ns: int
    upright: bool
    ready: bool
    kick_active: bool
    head: tuple[float, float]
    phase: int
    phase_ns: int
    mode: int
    body_control: int
    status_ns: int
    recovery_available: bool = False
    recovery_attempt_id: str | None = None
    recovery_status: str = "idle"


class MatchActuator:
    """Apply leased intents, interpolate the head and revoke kick mode on every stop.

    A caller schedules step() independently of behaviour. The driver must bound
    every operation; this loop must not wait for a world-model update or SDK mode
    transition. Start-up prepares the mode before this actuator is armed.
    """

    def __init__(
        self,
        driver,
        session,
        *,
        clock,
        feedback_ns=150_000_000,
        status_ns=1_200_000_000,
        max_speed=0.2,
        max_turn=0.8,
    ):
        if type(feedback_ns) is not int or not 0 < feedback_ns <= 150_000_000:
            raise ValueError("SDK feedback lifetime must be at most 150 ms")
        if any(not isfinite(v) or v <= 0 for v in (max_speed, max_turn)):
            raise ValueError("Motion limits must be positive and finite")
        if type(status_ns) is not int or not 0 < status_ns <= 1_200_000_000:
            raise ValueError("Slow SDK status lifetime must be at most 1.2 s")
        self.driver, self.clock = driver, clock
        self.gate = MatchIntentGate(session)
        self.feedback_ns, self.max_speed, self.max_turn = (
            feedback_ns,
            max_speed,
            max_turn,
        )
        self.status_ns = status_ns
        self.attempt_id = None
        self.kick_status = "idle"
        self._recovery = None
        self._recovery_done = set()
        self._enabled = False
        self._started = None
        self._kick_stopping_at = None
        self._kick_done = set()
        self._enabled_at = None
        self._last_step = clock()
        self._head_at = None
        self._head_held = False
        self._last_head = (0.45, 0.0)
        self.reason = "idle"
        self.stop_errors = []

    def accept(self, intent):
        """Reject unsupported limits rather than silently clipping a planned command."""
        if (
            hypot(*intent.velocity[:2]) > self.max_speed + 1e-8
            or abs(intent.velocity[2]) > self.max_turn
            or not -0.3 <= intent.head[0] <= 0.7
            or abs(intent.head[1]) > 0.8
            or not all(0 < v <= 1.2 for v in intent.head[2:])
            or (intent.kick is not None and not 1 <= intent.kick[1] <= 2)
        ):
            self.gate.fail("actuator_limits_exceeded")
            return False
        return self.gate.accept(intent, self.clock())

    def stop(self, through_sequence):
        self.gate.stop(through_sequence=through_sequence)
        self.reason = "stopped"

    def _require_lease(self):
        if self.gate.current(self.clock()) is None:
            raise RuntimeError("match_intent_expired")

    def _revoke(self, sample):
        # Each operation is attempted even if another failed. Keep trying on the
        # independently scheduled next step; a failed disable is never success.
        self.stop_errors = []
        if self._recovery is not None:
            self._recovery_done.add(self._recovery)
        recovery = () if self._recovery is None else (self.driver.cancel_recovery,)
        stop_body = getattr(self.driver, "stop_body", None)
        for operation in recovery + (
            self.driver.disable_kick,
            lambda: self._hold_head(sample),
            stop_body
            if callable(stop_body)
            else lambda: self.driver.move((0.0, 0.0, 0.0)),
        ):
            try:
                operation()
            except (RuntimeError, OSError, ValueError) as error:
                self.stop_errors.append(str(error))
        if not self.stop_errors:
            self._enabled = False
            self._recovery = None

    def _hold_head(self, sample):
        # Hold once before leaving Soccer. Reissuing RotateHead while the SDK
        # changes mode is rejected; the acknowledged target already holds it.
        # A failed hold remains pending and is retried on the next watchdog tick.
        if not self._head_held:
            head = (
                sample.head
                if sample and all(isfinite(q) for q in sample.head)
                else self._last_head
            )
            self.driver.head(head)
            self._head_held = True

    def step(self):
        """One watchdog cycle; expiry, stale SDK feedback and faults all revoke motion."""
        now = self.clock()
        dt = min(0.05, max(0.0, (now - self._last_step) / 1e9))
        self._last_step = now
        sample = self.driver.sample()
        intent = self.gate.current(now)
        usable = (
            sample is not None
            and 0 <= now - sample.observed_ns <= self.feedback_ns
            and 0 <= now - sample.status_ns <= self.status_ns
            and all(isfinite(q) for q in sample.head)
        )
        stopping = (
            intent is not None
            and intent.kick is None
            and not any(intent.velocity)
            and (self._enabled or self._kick_stopping_at is not None)
        )
        if intent is not None and (
            not usable
            or (
                intent.recovery_attempt_id is None
                and (not sample.upright or (not sample.ready and not stopping))
            )
            or (
                intent.recovery_attempt_id is not None and not sample.recovery_available
            )
        ):
            self.gate.fail(
                "sdk_feedback_stale" if not usable else "sdk_not_ready_or_fallen"
            )
            intent = None
        if intent is None:
            self._kick_stopping_at = None
            if self.attempt_id and self.kick_status not in {"completed", "stopped"}:
                self.kick_status = "failed"
                self._kick_done.add(self.attempt_id)
            self._revoke(sample)
            self.reason = self.gate.failure or self.reason
        else:
            try:
                if intent.recovery_attempt_id is not None:
                    if not all(
                        callable(getattr(self.driver, name, None))
                        for name in ("recover", "cancel_recovery")
                    ):
                        raise RuntimeError("recovery_unsupported")
                    attempt = intent.recovery_attempt_id
                    if (
                        sample.recovery_attempt_id == attempt
                        and sample.recovery_status in {"completed", "failed"}
                    ):
                        self._recovery_done.add(attempt)
                    if attempt in self._recovery_done:
                        self._revoke(sample)
                        self.reason = "recovery_finished"
                    elif self._recovery != attempt:
                        if self._recovery is not None:
                            raise RuntimeError("recovery_replaced_without_stop")
                        self._revoke(sample)
                        if self.stop_errors:
                            raise RuntimeError("; ".join(self.stop_errors))
                        self._require_lease()
                        self._recovery = attempt
                        self._head_held = False
                        self.driver.recover(attempt)
                        self.reason = "recovering"
                    else:
                        self.reason = "recovering"
                elif self._recovery is not None:
                    self._recovery_done.add(self._recovery)
                    self._revoke(sample)
                    self.reason = "stopping_recovery"
                elif intent.kick is None:
                    if (
                        self._enabled or sample.kick_active
                    ) and self._kick_stopping_at is None:
                        self._kick_stopping_at = now
                        self._kick_done.add(self.attempt_id)
                        self.kick_status = "stopping"
                    if self._kick_stopping_at is not None:
                        self._revoke(sample)
                        if self.stop_errors:
                            raise RuntimeError("; ".join(self.stop_errors))
                        self.reason = "stopping_kick"
                        # A disable acknowledgement is not controller exit. Both
                        # status streams must have progressed beyond the stop.
                        if (
                            not sample.kick_active
                            and sample.ready
                            and sample.observed_ns > self._kick_stopping_at
                            and sample.status_ns > self._kick_stopping_at
                            and sample.phase_ns > self._kick_stopping_at
                            and 0 <= now - sample.phase_ns <= self.status_ns
                            and self.driver.ensure_mode(False)
                        ):
                            self.kick_status = "stopped"
                            self._kick_stopping_at = None
                            self.reason = "kick_stopped"
                    elif self.driver.ensure_mode(False):
                        self._require_lease()
                        self.driver.move(intent.velocity)
                        self.reason = "walking" if any(intent.velocity) else "standing"
                    else:
                        self.reason = "preparing_walk"
                else:
                    if self.attempt_id != intent.kick_attempt_id:
                        if (
                            self._enabled
                            or sample.kick_active
                            or self._kick_stopping_at is not None
                        ):
                            raise RuntimeError("kick_attempt_replaced_without_stop")
                        self.attempt_id = intent.kick_attempt_id
                        self._started = now
                        self._enabled_at = None
                        self.kick_status = (
                            "failed" if self.attempt_id in self._kick_done else "idle"
                        )
                    # Native phases describe a continuous controller, not a
                    # single strike. Completion belongs to the behaviour's
                    # departure + confirmed-stop lifecycle, never a phase edge.
                    if self.attempt_id in self._kick_done:
                        self._revoke(sample)
                        self.reason = "kick_" + self.kick_status
                    elif self.driver.ensure_mode(True):
                        self._require_lease()
                        self.driver.reference(intent.kick)
                        if not self._enabled:
                            self._require_lease()
                            self._enabled_at = self.clock()
                            self._head_held = False
                            self.driver.enable_kick()
                            self._enabled = True
                        if sample.kick_active and sample.observed_ns >= self._started:
                            self.kick_status = "running"
                        elif now - self._enabled_at > 1_500_000_000:
                            raise RuntimeError("kick_enable_not_confirmed")
                        self.reason = (
                            "kicking"
                            if self.kick_status == "running"
                            else "enabling_kick"
                        )
                    else:
                        self.reason = "preparing_kick"
                if self.stop_errors:
                    raise RuntimeError("; ".join(self.stop_errors))
                if self.gate.current(self.clock()) is None:
                    if self.attempt_id and self.kick_status not in {
                        "completed",
                        "stopped",
                    }:
                        self.kick_status = "failed"
                        self._kick_done.add(self.attempt_id)
                    self._revoke(sample)
                    self.reason = self.gate.failure
                elif self.reason in {"walking", "standing", "enabling_kick", "kicking"}:
                    # The K1 service can refuse rapid RotateHead requests.
                    # Schedule interpolation at 10 Hz; the lease watchdog keeps
                    # running at 50 Hz and a stop still holds the head immediately.
                    if self._head_at is None or now - self._head_at >= 100_000_000:
                        head_dt = (
                            dt
                            if self._head_at is None
                            else min(0.15, (now - self._head_at) / 1e9)
                        )
                        target = intent.head[:2]
                        self._last_head = tuple(
                            q + max(-rate * head_dt, min(rate * head_dt, t - q))
                            for q, t, rate in zip(sample.head, target, intent.head[2:])
                        )
                        self._head_held = False
                        self.driver.head(self._last_head)
                        self._head_at = now
                # RPCs consume the existing budget; no SDK operation renews it.
                if self.gate.current(self.clock()) is None:
                    if self.attempt_id and self.kick_status not in {
                        "completed",
                        "stopped",
                    }:
                        self.kick_status = "failed"
                        self._kick_done.add(self.attempt_id)
                    self._revoke(sample)
                    self.reason = self.gate.failure
            except (RuntimeError, OSError, ValueError) as error:
                self.gate.fail("sdk_error:" + str(error))
                self.kick_status = "failed" if self.attempt_id else "idle"
                self._revoke(sample)
                self.reason = self.gate.failure
        return {
            "kind": "feedback",
            "now_ns": self.clock(),
            "session": self.gate.session,
            "sequence": self.gate.sequence,
            "reason": self.reason,
            "failure": self.gate.failure,
            "expired_at_ns": self.gate.expired_at_ns,
            "sample": asdict(sample) if sample else None,
            "kick_requested": self._enabled,
            "kick_attempt_id": self.attempt_id,
            "kick_status": self.kick_status,
            "stop_errors": tuple(self.stop_errors),
        }

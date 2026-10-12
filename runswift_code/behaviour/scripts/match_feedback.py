"""Convert receipt-timed SDK feedback to the match runner's decision-time input."""

from match_runner import MotionFeedback


class SdkFeedback:
    """Check wall age and stamp each new SDK sample once in the decision clock.

    Native SDK state topics have no capture timestamp. This is a receipt-time
    association, not synchronised sensing. Re-reading old data never renews it,
    and the independent actuator also enforces the original wall-clock age.
    """

    def __init__(self, *, wall_clock, max_age_ns=150_000_000):
        if type(max_age_ns) is not int or not 0 < max_age_ns <= 150_000_000:
            raise ValueError("SDK feedback lifetime must be at most 150 ms")
        self.clock, self.max_age_ns = wall_clock, max_age_ns
        self._source = self._at = None

    def read(self, receipt, at):
        if receipt is None or receipt.get("sample") is None:
            return None
        sample = receipt["sample"]
        source = sample["observed_ns"]
        if (
            not 0 <= self.clock() - source <= self.max_age_ns
            or not 0 <= self.clock() - sample["status_ns"] <= 1_200_000_000
        ):
            return None
        if self._at is not None and (
            at.clock_epoch != self._at.clock_epoch or at.ns < self._at.ns
        ):
            raise ValueError("SDK feedback requires a new mapping after a clock reset")
        if self._source is not None and source < self._source:
            raise ValueError("SDK sample receipt time moved backwards")
        if source != self._source:
            self._source, self._at = source, at
        return MotionFeedback(
            self._at,
            sample["upright"],
            sample["ready"],
            sample["ready"],
            receipt["kick_attempt_id"],
            receipt["kick_status"],
            sample.get("recovery_available", False),
            sample.get("recovery_attempt_id"),
            sample.get("recovery_status", "idle"),
        )

"""One bounded kick attempt and separate ball-travel measurements, without ROS."""

from itertools import pairwise
from math import hypot, isfinite
from time import monotonic_ns

from action.match_intent import MatchIntent
from action.types import MotionCommand
from match_feedback import SdkFeedback
from skills.base import SkillStatus
from skills.single_shot import SingleShot, SingleShotGoal
from skills.world import Kick, KickGoal


class KickPilot:
    """Bound one controller activation, with range and completion probe modes.

    This experimental fixture deliberately omits the match runner's post-strike
    distance window. It still requires fresh, usable ball/aim estimates on every
    tick, and never holds a stale ball reference through a missing observation.
    Range mode disarms after departure. Completion mode may expose repeated
    strikes by the vendor controller; its displacement is not single-shot range.
    """

    def __init__(
        self, port, target, *, power, mode="range", timeout=12.0, clock=monotonic_ns
    ):
        if not isfinite(power) or not 1 <= power <= 2:
            raise ValueError("Use the existing SDK power limits [1, 2]")
        if not isfinite(timeout) or not 0 < timeout <= 20:
            raise ValueError("Pilot kick timeout must be in (0, 20] seconds")
        if mode not in {"range", "completion"}:
            raise ValueError("Choose a range or completion pilot")
        self.port, self.clock = port, clock
        self.mode = mode
        self.timeout_ns = round(timeout * 1e9)
        self.attempt = port.session + ":pilot"
        self.feedback = SdkFeedback(wall_clock=clock)
        self.command = MotionCommand()
        self.skill = SingleShot() if mode == "range" else Kick()
        self.goal = (
            SingleShotGoal(
                power, target=target, duration_sec=timeout, attempt_id=self.attempt
            )
            if mode == "range"
            else KickGoal(power, target=target, duration_sec=timeout)
        )
        self.started = None
        self.sequence = 0
        self.reason = None

    def stop(self, reason):
        """Latch the first outcome and fence old commands; never start a second kick."""
        self.reason = self.reason or reason
        self.skill.cancel(self.command)
        self.port.stop()

    def tick(self, context, received_wall_ns, receipt):
        """Use one immutable view and its original receipt for the entire command."""
        if self.reason is not None:
            return None
        now = self.clock()
        if received_wall_ns is None or not 0 <= now - received_wall_ns < 350_000_000:
            self.stop("observations_expired")
            return None
        if receipt is None or not 0 <= now - receipt["now_ns"] <= 150_000_000:
            self.stop("actuator_feedback_expired")
            return None
        if receipt["failure"]:
            self.stop("actuator_fault:" + receipt["failure"])
            return None
        if receipt["kick_attempt_id"] == self.attempt and receipt["kick_status"] in {
            "completed",
            "failed",
        }:
            self.stop("sdk_" + receipt["kick_status"])
            return None
        if self.started is not None and now - self.started >= self.timeout_ns + (
            2_000_000_000 if self.mode == "range" else 0
        ):
            self.stop("kick_timeout")
            return None
        try:
            options = (
                {"motion": self.feedback.read(receipt, context.now)}
                if self.mode == "range"
                else {}
            )
            progress = self.skill.tick(context, self.goal, self.command, **options)
            if self.mode == "range" and progress.status == SkillStatus.SUCCEEDED:
                self.stop(progress.reason)
                return None
            if progress.status != SkillStatus.RUNNING:
                # A held intent reaching its duration is not SDK completion.
                self.stop("world_or_skill:" + progress.reason)
                return None
            command = self.command
            if self.started is None and not (
                0 < command.kick_ball_x < 0.85
                and abs(command.kick_ball_y) < 0.2
                and abs(command.kick_direction) < 0.35
            ):
                self.stop("initial_alignment_rejected")
                return None
            now = self.clock()
            deadline = min(now + 250_000_000, received_wall_ns + 350_000_000)
            if deadline <= now:
                self.stop("observations_expired")
                return None
            intent = MatchIntent(
                self.port.session,
                self.sequence,
                now,
                deadline,
                (0.0, 0.0, 0.0),
                command.head_targets(),
                (
                    command.kick_direction,
                    command.kick_power,
                    command.kick_ball_x,
                    command.kick_ball_y,
                )
                if command.kick_active
                else None,
                self.attempt if command.kick_active else None,
            )
            self.port.send(intent)
            self.started = now if self.started is None else self.started
            self.sequence += 1
            return intent
        except Exception:
            self.stop("pilot_error")
            raise


def measure(rows, origin, *, stop_reason):
    """Measure sampled ground truth; SDK completion never implies contact or a goal."""
    samples = []
    for row in rows:
        if row["ball"] is not None and (
            not samples or row["sim_ns"] > samples[-1]["sim_ns"]
        ):
            samples.append(row)
    if not samples:
        return {"stop_reason": stop_reason, "ball_samples": 0, "range_settled": False}
    moved = [
        r
        for r in samples
        if hypot(r["ball"][0] - origin[0], r["ball"][1] - origin[1]) > 0.1
    ]
    end = samples[-1]
    tail = [r for r in samples if end["sim_ns"] - r["sim_ns"] <= 2_000_000_000]
    speeds = [
        hypot(b["ball"][0] - a["ball"][0], b["ball"][1] - a["ball"][1])
        / ((b["sim_ns"] - a["sim_ns"]) / 1e9)
        for a, b in pairwise(tail)
    ]
    settled = bool(
        moved
        and speeds
        and end["sim_ns"] - tail[0]["sim_ns"] >= 1_800_000_000
        and max(speeds) < 0.05
        and max(b["sim_ns"] - a["sim_ns"] for a, b in pairwise(tail)) <= 250_000_000
        and rows[-1]["wall_ns"] - end["wall_ns"] <= 250_000_000
    )
    sent = next((r for r in rows if r.get("intent")), None)
    stopped = next(
        (r for r in rows if r.get("intent") and r["intent"]["kick"] is None), None
    )
    stopped = stopped or next((r for r in rows if r.get("stop_reason")), None)
    phases = []
    for row in rows:
        receipt = row.get("motion")
        sample = receipt and receipt.get("sample")
        if sample and (not phases or sample["phase"] != phases[-1]["phase"]):
            phases.append({"phase": sample["phase"], "receipt_ns": sample["phase_ns"]})
    # Field/goal contacts can truncate travel. This is an observed displacement,
    # never a calibrated maximum shot range or a goal adjudication.
    return {
        "stop_reason": stop_reason,
        "ball_samples": len(samples),
        "ball_moved": bool(moved),
        "first_motion_wall_ns": moved[0]["wall_ns"] if moved else None,
        "first_motion_after_request_s": (moved[0]["wall_ns"] - sent["wall_ns"]) / 1e9
        if moved and sent
        else None,
        "stop_requested_wall_ns": stopped["wall_ns"] if stopped else None,
        "max_displacement_m": max(
            hypot(r["ball"][0] - origin[0], r["ball"][1] - origin[1]) for r in samples
        ),
        "max_forward_m": max(r["ball"][0] - origin[0] for r in samples),
        "max_lateral_m": max(abs(r["ball"][1] - origin[1]) for r in samples),
        "max_ball_height_m": max(r["ball"][2] for r in samples),
        "final_ball": end["ball"],
        "range_settled": settled,
        "field_boundary_reached": any(
            abs(r["ball"][0]) >= 7 or abs(r["ball"][1]) >= 4.5 for r in samples
        ),
        "sdk_completed": stop_reason == "sdk_completed",
        "single_shot_finished": stop_reason == "shot_departed_and_stopped",
        "phase_transitions": phases,
        "contact_confirmed": False,
    }

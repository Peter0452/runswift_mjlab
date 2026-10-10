"""Frozen calibration cases and independent measurements; standard library only."""

import hashlib
import json
import math
import statistics
from dataclasses import asdict, dataclass
from itertools import pairwise
from pathlib import Path


@dataclass(frozen=True)
class CalibrationCase:
    name: str
    kind: str
    velocity: tuple = (0.0, 0.0, 0.0)
    duration_s: float = 5.0
    power: float = 1.5
    angle_rad: float = 0.0
    yaw_rad: float = 0.0
    target_distance_m: float = 3.0
    timeout_s: float = 35.0
    changes: tuple = ()

    @property
    def ball(self):
        return (4.0 if self.yaw_rad else -4.0, 0.0)

    @property
    def start(self):
        if self.kind == "walk":
            return (0.0, 0.0)
        separation = 1.3 if self.kind == "transition" else 0.65
        return (
            self.ball[0] - separation * math.cos(self.yaw_rad),
            self.ball[1] - separation * math.sin(self.yaw_rad),
        )

    @property
    def target(self):
        angle = self.yaw_rad + self.angle_rad
        return (
            self.ball[0] + self.target_distance_m * math.cos(angle),
            self.ball[1] + self.target_distance_m * math.sin(angle),
        )


def calibration_cases(suite="quick"):
    walks = [
        CalibrationCase(name, "walk", velocity=velocity)
        for name, velocity in (
            ("forward-stop-slow", (0.1, 0.0, 0.0)),
            ("forward-stop-fast", (0.2, 0.0, 0.0)),
            ("forward-stop-creep", (0.05, 0.0, 0.0)),
            ("backward-slow", (-0.1, 0.0, 0.0)),
            ("backward-fast", (-0.2, 0.0, 0.0)),
            ("left", (0.0, 0.1, 0.0)),
            ("right", (0.0, -0.1, 0.0)),
            ("turn-left", (0.0, 0.0, 0.4)),
            ("turn-right", (0.0, 0.0, -0.4)),
        )
    ]
    kicks = [
        CalibrationCase("kick-power-" + str(power), "kick", power=power)
        for power in (1.0, 1.5, 2.0)
    ] + [
        CalibrationCase("kick-left", "kick", angle_rad=0.25),
        CalibrationCase("kick-right", "kick", angle_rad=-0.25),
        CalibrationCase("kick-reversed", "kick", yaw_rad=math.pi),
    ]
    transitions = [
        CalibrationCase("walk-kick-walk", "transition"),
        CalibrationCase("walk-kick-walk-reversed", "transition", yaw_rad=math.pi),
    ]
    changes = [
        CalibrationCase(
            "forward-stop-resume",
            "walk",
            velocity=(0.2, 0, 0),
            duration_s=8,
            changes=((3, (0, 0, 0)), (5, (0.1, 0, 0))),
        ),
        CalibrationCase(
            "forward-sideways",
            "walk",
            velocity=(0.1, 0, 0),
            duration_s=8,
            changes=((4, (0, 0.1, 0)),),
        ),
        CalibrationCase(
            "turn-reverse",
            "walk",
            velocity=(0, 0, 0.4),
            duration_s=8,
            changes=((4, (0, 0, -0.4)),),
        ),
    ]
    cases = walks + changes + kicks + transitions
    if suite == "smoke":
        return [cases[0], kicks[1], transitions[0]]
    if suite != "quick":
        raise ValueError("Choose smoke or quick")
    return cases


def write_json(path, value):
    """Atomically checkpoint a report without allowing non-finite JSON numbers."""
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def read_rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def wrap(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


def _truth(rows, start_ns, end_ns):
    samples, issues = [], []
    for row in rows:
        if not start_ns <= row["wall_ns"] <= end_ns:
            continue
        raw = row["data"]
        at, world = raw["time"], raw["world"]
        own = next((r for r in world["robots"] if r["name"] == "robot1"), None)
        if own is None:
            issues.append("robot_truth_missing")
            continue
        numbers = [at, *own["position"], own["yaw"], *world["ballPosition"]]
        if not all(type(n) in (int, float) and math.isfinite(n) for n in numbers):
            raise ValueError("Non-finite truth sample")
        if samples and (
            at <= samples[-1]["time"] or row["wall_ns"] <= samples[-1]["wall_ns"]
        ):
            if raw == samples[-1]["raw"]:
                continue
            issues.append("truth_time_not_increasing")
            continue
        samples.append(
            {
                "time": at,
                "wall_ns": row["wall_ns"],
                "pose": (*own["position"][:2], own["yaw"]),
                "ball": world["ballPosition"],
                "contacts": world.get("ballContacts"),
                "up_dot": own["upDot"],
                "raw": raw,
            }
        )
    if len(samples) < 2:
        issues.append("insufficient_truth")
    else:
        if (
            samples[0]["wall_ns"] - start_ns > 200_000_000
            or end_ns - samples[-1]["wall_ns"] > 200_000_000
        ):
            issues.append("incomplete_truth_interval")
        if any(
            b["time"] - a["time"] > 0.1 or b["wall_ns"] - a["wall_ns"] > 200_000_000
            for a, b in pairwise(samples)
        ):
            issues.append("truth_gap")
    return samples, sorted(set(issues))


def _velocities(samples):
    values = []
    for a, b in pairwise(samples):
        dt = b["time"] - a["time"]
        dx, dy = b["pose"][0] - a["pose"][0], b["pose"][1] - a["pose"][1]
        yaw = a["pose"][2] + wrap(b["pose"][2] - a["pose"][2]) / 2
        values.append(
            {
                "wall_ns": b["wall_ns"],
                "time": b["time"],
                "dt": dt,
                "velocity": (
                    (math.cos(yaw) * dx + math.sin(yaw) * dy) / dt,
                    (-math.sin(yaw) * dx + math.cos(yaw) * dy) / dt,
                    wrap(b["pose"][2] - a["pose"][2]) / dt,
                ),
            }
        )
    return values


def _persistent_motion(velocities, requested_ns, stop_ns, command=None):
    """Require 150 ms of measured movement; gait sway alone is not a transition."""
    began = None
    for row in velocities:
        if not requested_ns <= row["wall_ns"] < stop_ns:
            continue
        vx, vy, turn = row["velocity"]
        if command is not None and math.hypot(*command[:2]):
            moving = (vx * command[0] + vy * command[1]) / math.hypot(
                *command[:2]
            ) > 0.04
        elif command is not None and command[2]:
            moving = abs(turn) > 0.15 and turn * command[2] > 0
        else:
            moving = math.hypot(vx, vy) > 0.04 or abs(turn) > 0.15
        if moving:
            began = row if began is None else began
            if row["time"] - began["time"] >= 0.15:
                return began["wall_ns"]
        else:
            began = None
    return None


def _settled(samples, stopped_ns, *, ball=False, return_start=False):
    """Find a continuous stable interval in progressing truth, after a stop."""
    began = None
    required = 1.8 if ball else 0.8
    for a, b in pairwise(samples):
        if a["wall_ns"] < stopped_ns:
            continue
        dt = b["time"] - a["time"]
        key = "ball" if ball else "pose"
        speed = math.dist(a[key][:2], b[key][:2]) / dt
        turning = 0 if ball else abs(wrap(b["pose"][2] - a["pose"][2])) / dt
        if dt <= 0.1 and speed < (0.05 if ball else 0.03) and turning < 0.08:
            began = a if began is None else began
            if b["time"] - began["time"] >= required:
                return began["wall_ns"] if return_start else b["wall_ns"]
        else:
            began = None
    return None


def _delay(end_ns, start_ns):
    return (
        (end_ns - start_ns) / 1e9
        if end_ns is not None and start_ns is not None and end_ns >= start_ns
        else None
    )


def measure_case(case, truth_rows, controls, *, start_ns, end_ns):
    """Evaluate raw truth separately from policy inputs and declared outcomes."""
    samples, issues = _truth(truth_rows, start_ns, end_ns)
    result = {
        "valid": not issues,
        "issues": issues,
        "walk": [],
        "kick": None,
        "transitions_s": {},
    }
    if len(samples) < 2:
        return result
    velocities = _velocities(samples)
    sent = [r for r in controls if r.get("intent")]
    segments = []
    for row in sent:
        intent = row["intent"]
        moving = any(intent["velocity"])
        changed = bool(
            moving
            and segments
            and segments[-1].get("stop_ns") is None
            and case.kind == "walk"
            and tuple(intent["velocity"]) != tuple(segments[-1]["command"])
        )
        if changed:
            segments[-1]["stop_ns"] = intent["issued_ns"]
            segments[-1]["end_kind"] = "direction_change"
        if moving and (not segments or segments[-1].get("stop_ns") is not None):
            segments.append(
                {
                    "start_ns": intent["issued_ns"],
                    "command": intent["velocity"],
                    "stage": row["stage"],
                }
            )
        elif not moving and segments and segments[-1].get("stop_ns") is None:
            segments[-1]["stop_ns"] = intent["issued_ns"]
    for index, segment in enumerate(segments):
        stop = segment.get("stop_ns", end_ns)
        began = segment["start_ns"]
        observed = [r for r in velocities if began <= r["wall_ns"] <= stop]
        steady = [r for r in observed if r["wall_ns"] >= began + 1_000_000_000]
        duration = sum(r["dt"] for r in steady)
        mean = (
            [
                sum(r["velocity"][i] * r["dt"] for r in steady) / duration
                for i in range(3)
            ]
            if duration >= 1
            else None
        )
        first = _persistent_motion(
            velocities, began, stop, segment["command"] if case.kind == "walk" else None
        )
        next_start = (
            segments[index + 1]["start_ns"] if index + 1 < len(segments) else end_ns
        )
        stopped_samples = [s for s in samples if s["wall_ns"] <= next_start]
        settled = (
            _settled(stopped_samples, stop)
            if segment.get("end_kind") != "direction_change"
            else None
        )
        points = [s for s in samples if began <= s["wall_ns"] <= stop]
        expected = [0.0, 0.0, 0.0]
        for a, b in pairwise(points):
            # Integrate the actual sent commands, including changing navigation outputs.
            command = next(
                (
                    r["intent"]["velocity"]
                    for r in reversed(sent)
                    if r["intent"]["issued_ns"] <= a["wall_ns"]
                ),
                (0, 0, 0),
            )
            dt = b["time"] - a["time"]
            angle = expected[2] + command[2] * dt / 2
            expected[0] += (
                command[0] * math.cos(angle) - command[1] * math.sin(angle)
            ) * dt
            expected[1] += (
                command[0] * math.sin(angle) + command[1] * math.cos(angle)
            ) * dt
            expected[2] += command[2] * dt
        displacement = None
        if len(points) > 1:
            dx, dy = (
                points[-1]["pose"][0] - points[0]["pose"][0],
                points[-1]["pose"][1] - points[0]["pose"][1],
            )
            yaw = points[0]["pose"][2]
            displacement = [
                dx * math.cos(yaw) + dy * math.sin(yaw),
                -dx * math.sin(yaw) + dy * math.cos(yaw),
                sum(wrap(b["pose"][2] - a["pose"][2]) for a, b in pairwise(points)),
            ]
        after = [
            s
            for s in stopped_samples
            if stop <= s["wall_ns"] and (settled is None or s["wall_ns"] <= settled)
        ]
        result["walk"].append(
            {
                **segment,
                "stop_ns": stop,
                "steady_duration_s": duration,
                "measured_velocity": mean,
                "gain": (
                    [
                        (
                            mean[i] / segment["command"][i]
                            if mean is not None and segment["command"][i]
                            else None
                        )
                        for i in range(3)
                    ]
                    if case.kind == "walk"
                    else None
                ),
                "velocity_error": (
                    [mean[i] - segment["command"][i] for i in range(3)]
                    if mean is not None and case.kind == "walk"
                    else None
                ),
                "displacement_local": displacement,
                "expected_displacement_local": expected,
                "position_error_m": (
                    math.dist(displacement[:2], expected[:2]) if displacement else None
                ),
                "heading_error_rad": (
                    wrap(displacement[2] - expected[2]) if displacement else None
                ),
                "start_latency_s": _delay(first, began),
                "stop_to_settled_s": _delay(settled, stop),
                "stop_to_quiet_s": (
                    _delay(_settled(stopped_samples, stop, return_start=True), stop)
                    if segment.get("end_kind") != "direction_change"
                    else None
                ),
                "stop_drift_m": max(
                    (math.dist(s["pose"][:2], after[0]["pose"][:2]) for s in after),
                    default=None,
                ),
            }
        )
    result["direction_changes"] = []
    result["stop_restarts"] = []
    for previous, segment in pairwise(segments):
        if previous.get("end_kind") != "direction_change":
            restart = _persistent_motion(
                velocities,
                segment["start_ns"],
                segment.get("stop_ns", end_ns),
                segment["command"],
            )
            result["stop_restarts"].append(
                {
                    "stop_requested_ns": previous.get("stop_ns"),
                    "restart_requested_ns": segment["start_ns"],
                    "restart_latency_s": _delay(restart, segment["start_ns"]),
                }
            )
            continue
        requested, command = segment["start_ns"], segment["command"]
        response = matched = None
        window = []
        for v in velocities:
            if not requested <= v["wall_ns"] <= segment.get("stop_ns", end_ns):
                continue
            window.append(v)
            window = [r for r in window if v["time"] - r["time"] <= 0.25]
            duration = sum(r["dt"] for r in window)
            if duration < 0.2:
                continue
            average = [
                sum(r["velocity"][i] * r["dt"] for r in window) / duration
                for i in range(3)
            ]
            speed, desired_speed = math.hypot(*average[:2]), math.hypot(*command[:2])
            aligned = (
                (
                    speed > 0.04
                    and (average[0] * command[0] + average[1] * command[1])
                    / (speed * desired_speed)
                    >= math.cos(math.pi / 6)
                )
                if desired_speed
                else abs(average[2]) > 0.15 and average[2] * command[2] > 0
            )
            if aligned and response is None:
                response = v["wall_ns"]
            if (
                all(
                    abs(average[i] - command[i])
                    <= max((0.04, 0.04, 0.1)[i], abs(command[i]) * 0.25)
                    for i in range(3)
                )
                and matched is None
            ):
                matched = v["wall_ns"]
        points = [
            s
            for s in samples
            if requested <= s["wall_ns"] <= (response or segment.get("stop_ns", end_ns))
        ]
        old = previous["command"]
        old_speed = math.hypot(*old[:2])
        overshoot = None
        turn_overshoot = None
        if points:
            origin = points[0]["pose"]
            if old_speed:
                direction = origin[2] + math.atan2(old[1], old[0])
                overshoot = max(
                    0,
                    max(
                        (s["pose"][0] - origin[0]) * math.cos(direction)
                        + (s["pose"][1] - origin[1]) * math.sin(direction)
                        for s in points
                    ),
                )
            if old[2]:
                turn_overshoot = max(
                    0,
                    max(
                        wrap(s["pose"][2] - origin[2]) * math.copysign(1, old[2])
                        for s in points
                    ),
                )
        result["direction_changes"].append(
            {
                "requested_ns": requested,
                "from_velocity": old,
                "to_velocity": command,
                "direction_response_s": _delay(response, requested),
                "velocity_match_s": _delay(matched, requested),
                "old_direction_overshoot_m": overshoot,
                "old_turn_overshoot_rad": turn_overshoot,
            }
        )
    kick = next((r for r in sent if r["intent"]["kick"] is not None), None)
    if kick:
        request = kick["intent"]["issued_ns"]
        stop = next(
            (
                r["intent"]["issued_ns"]
                for r in sent
                if r["intent"]["issued_ns"] > request and r["intent"]["kick"] is None
            ),
            None,
        )
        if stop is None:
            stop = next(
                (
                    r["wall_ns"]
                    for r in controls
                    if r["wall_ns"] > request and r.get("stop_reason")
                ),
                None,
            )
        active = inactive = ready = None
        for row in controls:
            motion = row.get("motion")
            sample = motion and motion.get("sample")
            if (
                sample is None
                or not 0 <= row["wall_ns"] - sample["observed_ns"] <= 150_000_000
                or not 0 <= row["wall_ns"] - sample["status_ns"] <= 1_200_000_000
            ):
                continue
            if (
                active is None
                and sample["kick_active"]
                and sample["phase_ns"] >= request
            ):
                active = sample["phase_ns"]
            if stop and not sample["kick_active"] and sample["phase_ns"] > stop:
                inactive = inactive or sample["phase_ns"]
                if (
                    sample["ready"]
                    and sample["status_ns"] > stop
                    and sample["observed_ns"] > stop
                    and motion["kick_status"] == "stopped"
                ):
                    ready = ready or max(
                        sample["observed_ns"], sample["status_ns"], sample["phase_ns"]
                    )
        ball_samples = [s for s in samples if s["wall_ns"] >= request]
        if not ball_samples:
            result["valid"] = False
            result["issues"].append("kick_truth_missing")
            return result
        origin = ball_samples[0]["ball"]
        angle = case.yaw_rad + case.angle_rad
        projections = []
        contact = None
        for s in ball_samples:
            dx, dy = s["ball"][0] - origin[0], s["ball"][1] - origin[1]
            forward, lateral = dx * math.cos(angle) + dy * math.sin(
                angle
            ), -dx * math.sin(angle) + dy * math.cos(angle)
            projections.append((s, forward, lateral))
            if (
                contact is None
                and s["contacts"] is not None
                and any(c["name"] == "robot1" for c in s["contacts"])
            ):
                contact = s["wall_ns"]
        crossing = None
        for (a, fa, la), (b, fb, lb) in pairwise(projections):
            if fa < case.target_distance_m <= fb:
                alpha = (case.target_distance_m - fa) / (fb - fa)
                crossing = la + alpha * (lb - la)
                break
        settled = _settled(ball_samples, stop or request, ball=True)
        boundary = any(
            abs(s["ball"][0]) >= 7 or abs(s["ball"][1]) >= 4.5 for s in ball_samples
        )
        final_forward, final_lateral = projections[-1][1:]
        result["kick"] = {
            "requested_ns": request,
            "stop_ns": stop,
            "contact_confirmed": contact is not None,
            "contact_evidence_available": all(
                s["contacts"] is not None for s in ball_samples
            ),
            "controller_activations": sum(
                r["intent"]["kick"] is not None
                and (i == 0 or sent[i - 1]["intent"]["kick"] is None)
                for i, r in enumerate(sent)
            ),
            "strike_count": None,
            "power": case.power,
            "aim_rad": angle,
            "request_to_active_s": _delay(active, request),
            "request_to_contact_s": _delay(contact, request),
            "stop_to_inactive_s": _delay(inactive, stop),
            "stop_to_walking_ready_s": _delay(ready, stop),
            "ball_settled": settled is not None,
            "boundary_censored": boundary,
            "final_forward_m": final_forward,
            "final_lateral_m": final_lateral,
            "final_range_m": math.hypot(final_forward, final_lateral),
            "direction_error_rad": (
                math.atan2(final_lateral, final_forward)
                if math.hypot(final_forward, final_lateral) > 0.1
                else None
            ),
            "target_plane_lateral_error_m": crossing,
            "target_plane_reached": crossing is not None,
            "target_endpoint_error_m": math.hypot(
                final_forward - case.target_distance_m, final_lateral
            ),
        }
        result["transitions_s"].update(
            {
                key: result["kick"][key]
                for key in (
                    "request_to_active_s",
                    "request_to_contact_s",
                    "stop_to_inactive_s",
                    "stop_to_walking_ready_s",
                )
            }
        )
        approach = next((s for s in segments if s["stage"] == "approach"), None)
        recovery = next((s for s in segments if s["stage"] == "recovery"), None)
        if approach:
            result["transitions_s"]["walk_stop_to_kick_active_s"] = _delay(
                active, approach.get("stop_ns")
            )
        if recovery:
            first = _persistent_motion(
                velocities, recovery["start_ns"], recovery.get("stop_ns", end_ns)
            )
            result["transitions_s"]["kick_stop_to_resumed_motion_s"] = _delay(
                first, stop
            )
    result["fallen"] = any(s["up_dot"] < 0.7 for s in samples)
    return result


def _distribution(values):
    values = sorted(v for v in values if v is not None)
    return {
        "n": len(values),
        "mean": statistics.mean(values) if values else None,
        "stddev": statistics.stdev(values) if len(values) > 1 else None,
        "min": min(values) if values else None,
        "max": max(values) if values else None,
    }


def calibration_report(results):
    """Only usable trials contribute to calibration; every attempt stays in totals."""
    usable = [r for r in results if r.get("usable")]
    walks, kicks, transitions, changes, restarts = {}, {}, {}, {}, {}
    for row in usable:
        case, measurement = row["case"], row["measurement"]
        if case["kind"] == "walk":
            for index, leg in enumerate(measurement["walk"]):
                key = case["name"] + (
                    "/leg-%d" % (index + 1) if case.get("changes") else ""
                )
                walks.setdefault(key, []).append(leg)
            changes.setdefault(case["name"], []).extend(
                measurement["direction_changes"]
            )
            restarts.setdefault(case["name"], []).extend(measurement["stop_restarts"])
        elif measurement["kick"]:
            # Transition trials have a different start; retain their own strata.
            key = (
                case["name"]
                if case["kind"] == "transition"
                else "power=%s,angle=%s,yaw=%s"
                % (case["power"], case["angle_rad"], case["yaw_rad"])
            )
            kicks.setdefault(key, []).append(measurement["kick"])
        for key, value in measurement["transitions_s"].items():
            transitions.setdefault(case["name"], {}).setdefault(key, []).append(value)
    return {
        "planned": len(results),
        "attempts": sum(r.get("reason") != "not_started" for r in results),
        "usable": len(usable),
        "excluded": len(results) - len(usable),
        "walk": {
            key: {
                "measured_velocity": [
                    _distribution(
                        [
                            r["measured_velocity"][i]
                            for r in values
                            if r["measured_velocity"]
                        ]
                    )
                    for i in range(3)
                ],
                "gain": [
                    _distribution([r["gain"][i] for r in values if r["gain"]])
                    for i in range(3)
                ],
                "start_latency_s": _distribution(
                    [r["start_latency_s"] for r in values]
                ),
                "stop_to_settled_s": _distribution(
                    [r["stop_to_settled_s"] for r in values]
                ),
                "stop_to_quiet_s": _distribution(
                    [r["stop_to_quiet_s"] for r in values]
                ),
                "position_error_m": _distribution(
                    [r["position_error_m"] for r in values]
                ),
                "heading_error_rad": _distribution(
                    [r["heading_error_rad"] for r in values]
                ),
                "stop_drift_m": _distribution([r["stop_drift_m"] for r in values]),
            }
            for key, values in walks.items()
        },
        "kick": {
            key: {
                metric: _distribution([r[metric] for r in values])
                for metric in (
                    "final_range_m",
                    "final_forward_m",
                    "final_lateral_m",
                    "direction_error_rad",
                    "target_plane_lateral_error_m",
                    "target_endpoint_error_m",
                )
            }
            for key, values in kicks.items()
        },
        "transitions_s": {
            case: {key: _distribution(values) for key, values in metrics.items()}
            for case, metrics in transitions.items()
        },
        "direction_changes": {
            key: {
                metric: _distribution([r[metric] for r in values])
                for metric in (
                    "direction_response_s",
                    "velocity_match_s",
                    "old_direction_overshoot_m",
                    "old_turn_overshoot_rad",
                )
            }
            for key, values in changes.items()
            if values
        },
        "stop_restarts": {
            key: _distribution([r["restart_latency_s"] for r in values])
            for key, values in restarts.items()
            if values
        },
        "interpretation": "Empirical K1 simulator lookup tables within tested commands/powers; one sample is not repeatability evidence. No extrapolation or automatic deployment. Contact windows do not count strikes.",
    }


def evaluate_directory(directory):
    """Recompute saved measurements, verifying original evidence file hashes."""
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    results = []
    for planned in manifest["trials"]:
        trial = directory / planned["id"]
        if not (trial / "summary.json").exists():
            results.append(
                {
                    "id": planned["id"],
                    "case": planned["case"],
                    "usable": False,
                    "reason": "interrupted" if trial.exists() else "not_started",
                }
            )
            continue
        summary = json.loads((trial / "summary.json").read_text())
        summary["id"] = planned["id"]
        if summary["case"] != planned["case"]:
            raise ValueError("Case differs from frozen plan: " + str(trial))
        for name, digest in summary["files_sha256"].items():
            if sha256(trial / name) != digest:
                raise ValueError("Changed evidence: " + str(trial / name))
        if (
            summary["start_ns"] is not None
            and summary["end_ns"] is not None
            and (trial / "truth.jsonl").exists()
        ):
            summary["measurement"] = measure_case(
                CalibrationCase(**planned["case"]),
                read_rows(trial / "truth.jsonl"),
                read_rows(trial / "controller.jsonl"),
                start_ns=summary["start_ns"],
                end_ns=summary["end_ns"],
            )
            summary["usable"] = trial_usable(summary)
        results.append(summary)
    return {
        "schema": "runswift-skill-calibration-results/1",
        "evaluator_sha256": sha256(__file__),
        "policy": manifest["policy"],
        "actuator": manifest.get("actuator", {"factory": "transport:MatchRelay"}),
        "results": results,
        "calibration": calibration_report(results),
    }


def trial_usable(summary):
    measured = summary.get("measurement", {})
    if (
        summary.get("error")
        or summary.get("reason") != "completed"
        or not measured.get("valid")
        or measured.get("fallen")
    ):
        return False
    if summary["case"]["kind"] == "walk":
        return bool(
            measured["walk"]
            and all(s["measured_velocity"] is not None for s in measured["walk"])
            and measured["walk"][-1]["stop_to_settled_s"] is not None
        )
    kick = measured.get("kick")
    return bool(
        kick
        and kick["contact_confirmed"]
        and kick["controller_activations"] == 1
        and kick["ball_settled"]
        and not kick["boundary_censored"]
        and kick["stop_to_walking_ready_s"] is not None
    )

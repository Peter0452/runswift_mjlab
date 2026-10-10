"""Offline scoring from raw simulator truth; no behaviour, SDK or world-model imports."""

from dataclasses import dataclass
from itertools import pairwise
from math import hypot, isfinite


@dataclass(frozen=True)
class GoalSpec:
    """Pinned K1 scene geometry: whole ball past the line, inside posts and crossbar."""

    line_x: float = 7.0
    half_width: float = 1.25  # Post centres +/-1.3 m, cylinder radius 0.05 m.
    height: float = 1.75  # Crossbar centre 1.8 m, cylinder radius 0.05 m.
    ball_radius: float = 0.11
    field_half_width: float = 4.5
    max_gap_s: float = 0.1

    def __post_init__(self):
        if any(not isfinite(v) or v <= 0 for v in vars(self).values()):
            raise ValueError("Geometry and sampling limits must be positive and finite")
        if self.ball_radius >= min(self.half_width, self.height):
            raise ValueError("Ball must fit inside the goal")


def _point(value):
    if not isinstance(value, (tuple, list)) or len(value) != 3:
        raise ValueError("Expected a three-dimensional ball position")
    if any(type(v) not in (int, float) or not isfinite(v) for v in value):
        raise ValueError("Non-finite ball position")
    return tuple(value)


def evaluate(rows, *, direction, start_wall_ns, end_wall_ns, geometry=None):
    """Evaluate original truth packets; gaps cannot become proof of a goal or miss.

    Contacts identify a robot over a publication window, not a foot or a strike.
    A separated run of contact-bearing windows is only an observed contact episode.
    """
    if direction not in (-1, 1) or start_wall_ns >= end_wall_ns:
        raise ValueError("Choose a goal direction and a positive recording interval")
    g = geometry or GoalSpec()
    samples, issues = [], []
    for row in rows:
        if not start_wall_ns <= row["wall_ns"] <= end_wall_ns:
            continue
        raw = row["data"]
        at = raw["time"]
        if type(at) not in (int, float) or not isfinite(at) or at < 0:
            raise ValueError("Invalid truth capture time")
        world = raw["world"]
        ball = _point(world["ballPosition"])
        contacts = world.get("ballContacts")
        if contacts is not None and not isinstance(contacts, list):
            raise ValueError("Invalid contact evidence")
        touch = (
            None if contacts is None else any(c["name"] == "robot1" for c in contacts)
        )
        if samples and at <= samples[-1]["time"]:
            if at == samples[-1]["time"] and raw == samples[-1]["raw"]:
                continue
            issues.append("truth_time_not_increasing")
            continue
        samples.append(
            {
                "time": at,
                "ball": ball,
                "touch": touch,
                "raw": raw,
                "wall_ns": row["wall_ns"],
            }
        )
    if len(samples) < 2:
        return {
            "valid": False,
            "issues": ["insufficient_truth"],
            "goal": None,
            "outcome": "unknown",
            "contact_confirmed": None,
        }
    if (
        samples[0]["wall_ns"] - start_wall_ns > 200_000_000
        or end_wall_ns - samples[-1]["wall_ns"] > 200_000_000
    ):
        issues.append("incomplete_recording_interval")
    if (
        abs(samples[0]["ball"][0]) >= g.line_x
        or abs(samples[0]["ball"][1]) >= g.field_half_width
    ):
        issues.append("ball_started_outside_field")
    crossings = []
    contact_windows = sum(s["touch"] is True for s in samples)
    contact_episodes = sum(
        s["touch"] is True and (i == 0 or samples[i - 1]["touch"] is not True)
        for i, s in enumerate(samples)
    )
    gaps = []
    for a, b in pairwise(samples):
        dt = b["time"] - a["time"]
        gaps.append(dt)
        if dt > g.max_gap_s + 1e-9:
            issues.append("truth_gap")
            continue
        for side in (-1, 1):
            ax, bx = side * a["ball"][0], side * b["ball"][0]
            plane = g.line_x + g.ball_radius
            if ax < plane <= bx:
                f = (plane - ax) / (bx - ax)
                y = a["ball"][1] + f * (b["ball"][1] - a["ball"][1])
                z = a["ball"][2] + f * (b["ball"][2] - a["ball"][2])
                inside = (
                    abs(y) < g.half_width - g.ball_radius
                    and 0 <= z < g.height - g.ball_radius
                )
                crossings.append(
                    {
                        "time": a["time"] + f * dt,
                        "side": side,
                        "y": y,
                        "z": z,
                        "inside_goal": inside,
                        "kind": "goal_line",
                        "interpolated": True,
                    }
                )
            ay, by = side * a["ball"][1], side * b["ball"][1]
            plane = g.field_half_width + g.ball_radius
            if ay < plane <= by:
                f = (plane - ay) / (by - ay)
                crossings.append(
                    {
                        "time": a["time"] + f * dt,
                        "side": side,
                        "kind": "touchline",
                        "inside_goal": False,
                        "interpolated": True,
                    }
                )
    crossings.sort(key=lambda c: c["time"])
    first = crossings[0] if crossings else None
    end = samples[-1]
    tail = [s for s in samples if end["time"] - s["time"] <= 2.0]
    settled = bool(
        len(tail) > 1
        and end["time"] - tail[0]["time"] >= 1.8
        and all(
            0 < b["time"] - a["time"] <= g.max_gap_s + 1e-9
            and hypot(b["ball"][0] - a["ball"][0], b["ball"][1] - a["ball"][1])
            / (b["time"] - a["time"])
            < 0.05
            for a, b in pairwise(tail)
        )
    )
    if first:
        goal = (
            first["kind"] == "goal_line"
            and first["inside_goal"]
            and first["side"] == direction
        )
        outcome = "scored" if goal else "own_goal" if first["inside_goal"] else "out"
    elif settled:
        goal, outcome = False, "short_or_wide"
    else:
        goal, outcome = None, "unresolved"
    if issues:
        goal, outcome = None, "unknown"
    origin = samples[0]["ball"]
    first_contact = next((s for s in samples if s["touch"]), None)
    return {
        "valid": not issues,
        "issues": sorted(set(issues)),
        "goal": goal,
        "outcome": outcome,
        "first_boundary_crossing": first,
        "crossings": crossings,
        "settled": settled,
        "samples": len(samples),
        "max_gap_s": max(gaps, default=None),
        "first_capture_s": samples[0]["time"],
        "last_capture_s": end["time"],
        "final_ball": end["ball"],
        "max_displacement_m": max(
            hypot(s["ball"][0] - origin[0], s["ball"][1] - origin[1]) for s in samples
        ),
        "contact_confirmed": True
        if contact_windows
        else None
        if any(s["touch"] is None for s in samples)
        else False,
        "contact_windows": contact_windows,
        "first_contact_window_end_s": None
        if first_contact is None
        else first_contact["time"],
        "time_to_contact_window_s": None
        if first_contact is None
        else first_contact["time"] - samples[0]["time"],
        "time_to_boundary_s": None
        if first is None
        else first["time"] - samples[0]["time"],
        "observed_contact_episodes": contact_episodes,
        "foot_contact_count": None,
        "strike_count": None,
        "contact_evidence": "Accumulated robot1-ball contact per published physics window; body part and strike count unavailable.",
    }


def case_summary(directory, case):
    """Keep unstarted/interrupted cases in reports; never infer an outcome from silence."""
    import json

    folder = directory / case["name"]
    path = folder / "summary.json"
    if path.exists():
        return json.loads(path.read_text())
    status = "interrupted" if folder.exists() else "not_started"
    return {
        "case": case,
        "start_wall_ns": None,
        "end_wall_ns": None,
        "execution_reason": status,
        "error": None,
        "valid_trial": False,
        "benchmark_success": False,
        "controller_stopped": None,
        "controller_activations": None,
        "files_sha256": {},
        "evaluation": {
            "valid": False,
            "goal": None,
            "outcome": "unknown",
            "issues": [status],
            "contact_confirmed": None,
        },
    }


def stage_results(summary, controls):
    """Separate reaching the kick stage, lifecycle completion and independently scored truth."""
    sent = [r for r in controls if r["result"]["intent"] is not None]
    kicks = [r for r in sent if r["result"]["intent"]["kick"] is not None]
    evaluation = summary["evaluation"]
    return {
        # A kick request is evidence of the behaviour reaching its kick window,
        # not an independent ground-truth judgement of the robot's alignment.
        "approach": "kick_requested"
        if kicks
        else "no_kick_request"
        if summary["start_wall_ns"] is not None
        else "unknown",
        "shot_completed": summary["execution_reason"] == "shot_departed_and_stopped",
        "controller_stopped": summary.get("controller_stopped"),
        "contact_confirmed": evaluation.get("contact_confirmed"),
        "goal": evaluation.get("goal"),
        "goal_line_offset_m": (evaluation.get("first_boundary_crossing") or {}).get(
            "y"
        ),
        "ball_displacement_m": evaluation.get("max_displacement_m"),
    }


def aggregate_results(results):
    """Use all planned cases as the denominator, including failures and missing recordings."""
    return {
        "planned": len(results),
        "not_started": sum(r["execution_reason"] == "not_started" for r in results),
        "interrupted": sum(r["execution_reason"] == "interrupted" for r in results),
        "kick_requested": sum(
            r.get("stages", {}).get("approach") == "kick_requested" for r in results
        ),
        "shot_completed": sum(
            r["execution_reason"] == "shot_departed_and_stopped" for r in results
        ),
        "contact_confirmed": sum(
            r["evaluation"].get("contact_confirmed") is True for r in results
        ),
        "goals_observed": sum(r["evaluation"]["goal"] is True for r in results),
        "valid_trials": sum(bool(r["valid_trial"]) for r in results),
        "benchmark_successes": sum(bool(r.get("benchmark_success")) for r in results),
        "unknown_or_unresolved": sum(r["evaluation"]["goal"] is None for r in results),
    }


def analyse_run(directory):
    """Re-evaluate saved truth without running behaviours or changing original results."""
    import bisect
    import hashlib
    import json
    from math import atan2, cos, sin

    manifest = json.loads((directory / "manifest.json").read_text())
    g = GoalSpec(**manifest["geometry"])
    results = []
    for case in manifest["cases"]:
        folder = directory / case["name"]
        summary = case_summary(directory, case)
        for name in ("truth.jsonl", "controller.jsonl"):
            if name in summary["files_sha256"]:
                actual = hashlib.sha256((folder / name).read_bytes()).hexdigest()
                if actual != summary["files_sha256"][name]:
                    raise ValueError(
                        "Recorded file hash changed: " + str(folder / name)
                    )
        if summary["start_wall_ns"] is None:
            results.append(
                {
                    "case": case["name"],
                    "valid_trial": False,
                    "benchmark_success": False,
                    "execution_reason": summary["execution_reason"],
                    "evaluation": summary["evaluation"],
                    "stages": stage_results(summary, []),
                }
            )
            continue
        truth = [
            json.loads(line)
            for line in (folder / "truth.jsonl").read_text().splitlines()
        ]
        controls = [
            json.loads(line)
            for line in (folder / "controller.jsonl").read_text().splitlines()
        ]
        evaluation = evaluate(
            truth,
            direction=case["direction"],
            start_wall_ns=summary["start_wall_ns"],
            end_wall_ns=summary["end_wall_ns"],
            geometry=g,
        )
        sent = [r for r in controls if r["result"]["intent"] is not None]
        kicks = [r for r in sent if r["result"]["intent"]["kick"] is not None]
        finished = next((r for r in controls if r["stop_reason"] is not None), None)
        times = [r["wall_ns"] for r in truth]
        heading_error = None
        if kicks:
            at = max(0, bisect.bisect_right(times, kicks[0]["wall_ns"]) - 1)
            world = truth[at]["data"]["world"]
            robot = next(r for r in world["robots"] if r["name"] == "robot1")
            ball = world["ballPosition"]
            heading = atan2(-ball[1], case["direction"] * g.line_x - ball[0])
            heading_error = atan2(
                sin(heading - robot["yaw"]), cos(heading - robot["yaw"])
            )
        valid = (
            summary["valid_trial"]
            and evaluation["valid"]
            and evaluation["goal"] is not None
            and not any(
                r.get("motion")
                and (r["motion"]["failure"] or r["motion"]["stop_errors"])
                for r in controls
            )
        )
        results.append(
            {
                "case": case["name"],
                "valid_trial": valid,
                "benchmark_success": valid
                and evaluation["goal"] is True
                and evaluation["contact_confirmed"] is True,
                "execution_reason": summary["execution_reason"],
                "evaluation": evaluation,
                "stages": stage_results(
                    {**summary, "evaluation": evaluation}, controls
                ),
                "first_kick_request_wall_s": None
                if not kicks
                else (kicks[0]["wall_ns"] - summary["start_wall_ns"]) / 1e9,
                "execution_wall_s": None
                if finished is None
                else (finished["wall_ns"] - summary["start_wall_ns"]) / 1e9,
                "body_heading_error_at_first_kick_rad": heading_error,
                "max_snapshot_age_ms": max(
                    ((r["sim_ns"] - r["snapshot_ns"]) / 1e6 for r in sent), default=None
                ),
                "max_intent_gap_ms": max(
                    (
                        (
                            b["result"]["intent"]["issued_ns"]
                            - a["result"]["intent"]["issued_ns"]
                        )
                        / 1e6
                        for a, b in pairwise(sent)
                    ),
                    default=None,
                ),
            }
        )
    return {
        "schema": "runswift-score-evaluation/1",
        "geometry": vars(g),
        "results": results,
        "totals": aggregate_results(results),
        "note": "Independent raw-truth scoring. Heading sampled at last received truth before the first kick command; body-part and exact strike counts unknown.",
    }


def main():
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyse_run(args.run)
    with args.output.open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "trials": len(result["results"]),
                "valid": sum(r["valid_trial"] for r in result["results"]),
                "scored": sum(
                    r.get("benchmark_success", False) for r in result["results"]
                ),
            }
        )
    )


if __name__ == "__main__":
    main()

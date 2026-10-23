"""Verify complete case coverage, trace hashes and recorded kick measurements."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from metrics import StrikeMeasurement


def audit(root):
    plan = json.loads((root / "plan.json").read_text())
    expected = {
        (c["name"], r) for c in plan["cases"] for r in range(1, plan["repeats"] + 1)
    }
    checked = 0
    max_error = 0.0
    peak_time_ties = 0
    for policy in plan["policies"]:
        for profile in plan["selected_ball_profiles"]:
            directory = root / policy / profile
            rows = json.loads((directory / "results.json").read_text())["trials"]
            assert len(rows) == len(expected)
            assert {(r["case"]["name"], r["repeat"]) for r in rows} == expected
            for row in rows:
                assert row["execution_error"] is None, row
                path = directory / Path(row["trace"]).name
                assert (
                    hashlib.sha256(path.read_bytes()).hexdigest() == row["trace_sha256"]
                )
                trace = np.load(path)
                assert np.isfinite(trace["qpos"]).all()
                assert np.isfinite(trace["qvel"]).all()
                measurement = StrikeMeasurement(
                    math.radians(row["case"]["heading_deg"])
                )
                for t, q, v, flags in zip(
                    trace["time_s"],
                    trace["qpos"],
                    trace["qvel"],
                    trace["contact_flags"],
                    strict=True,
                ):
                    measurement.update(float(t), q[29:31], v[28:30], *flags)
                replay = measurement.result(row["survived"])
                for key, value in replay.items():
                    recorded = row[key]
                    if value is None or isinstance(value, (bool, int)):
                        assert value == recorded, (path, key, value, recorded)
                    else:
                        error = abs(value - recorded)
                        if key == "strongest_foot_linked_time_s" and error > 1e-9:
                            # Float32 can tie two almost identical peak speeds.
                            index = int(np.argmin(abs(trace["time_s"] - recorded)))
                            recorded_speed = float(
                                np.linalg.norm(trace["qvel"][index, 28:30])
                            )
                            assert (
                                abs(recorded_speed - measurement.strongest_speed) < 1e-5
                            )
                            peak_time_ties += 1
                            continue
                        max_error = max(max_error, error)
                        assert error < 0.001, (path, key, value, recorded)
                checked += 1
    result = {
        "passed": True,
        "traces_verified": checked,
        "maximum_replay_numeric_difference": max_error,
        "numeric_tolerance": 0.001,
        "float32_peak_timestamp_ties": peak_time_ties,
        "note": "Physics traces store positions and velocities as float32; measurements were originally computed in float64.",
    }
    (root / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    audit(parser.parse_args().results.resolve())

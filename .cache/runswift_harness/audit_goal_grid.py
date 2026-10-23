"""Check every goal-grid trace and reproduce the original independent scorer."""

import argparse
import json
from pathlib import Path

import numpy as np
from compare import digest, write
from goal_grid import EVALUATOR, evaluator, score_trace


def audit(root, evaluator_path):
    plan = json.loads((root / "plan.json").read_text())
    assert digest(evaluator_path) == plan["evaluator_sha256"]
    scorer = evaluator(evaluator_path)
    expected = {c["name"] for c in plan["cases"]}
    checked = 0
    for policy in plan["policies"]:
        for profile in plan["ball_profiles"]:
            directory = root / policy / profile
            rows = json.loads((directory / "results.json").read_text())["trials"]
            assert len(rows) == len(expected)
            assert {r["case"]["name"] for r in rows} == expected
            for row in rows:
                assert row["execution_error"] is None, row
                path = directory / Path(row["trace"]).name
                assert digest(path) == row["trace_sha256"], path
                with np.load(path) as saved:
                    trace = {
                        k: saved[k] for k in ("time_s", "qpos", "qvel", "contact_flags")
                    }
                assert np.isfinite(trace["qpos"]).all()
                assert np.isfinite(trace["qvel"]).all()
                replay = score_trace(
                    trace,
                    row["case"]["direction"],
                    plan["balls"][profile]["radius_m"],
                    scorer,
                )
                assert json.loads(json.dumps(replay)) == row["evaluation"], path
                assert replay["valid"], (path, replay)
                checked += 1
    result = {
        "passed": True,
        "traces_verified": checked,
        "paired_case_coverage": True,
        "all_independent_evaluations_valid": True,
        "all_replayed_evaluations_match": True,
        "evaluator_sha256": plan["evaluator_sha256"],
    }
    write(root / "audit.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--evaluator-file", type=Path, default=EVALUATOR)
    args = parser.parse_args()
    audit(args.results.resolve(), args.evaluator_file.resolve())

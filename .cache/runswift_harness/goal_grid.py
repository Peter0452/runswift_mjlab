"""Run the existing 90 scoring placements with Peter or B-Human motion policies."""

import argparse
import importlib.util
import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import mujoco
import numpy as np
from compare import contacts, digest, physics_step, upstream, write
from contracts import BALLS, DEFAULT_ASSETS, MODELS, REPOSITORIES
from goal_controller import WALK_PATH, WALK_SHA, GoalController, boundary_crossing

REPO = Path(__file__).resolve().parents[2]
GRID = REPO / "benchmarks/results/2026-10-02/k1-score-grid/manifest.json"
EVALUATOR = REPO / "src/behaviour/examples/booster_match/score_evaluator.py"
PREFLIGHT = (
    "x2-y2-east-away-positive",
    "x2-y2-west-away-negative",
    "x3-y3-north-away-positive",
    "x1-y1-south-away-negative",
    "x3-y2-west-away-positive",
    "x1-y2-east-away-negative",
)


def evaluator(path):
    spec = importlib.util.spec_from_file_location("score_evaluator", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def budget(case):
    distance = np.linalg.norm(np.asarray(case["ball"]) - case["start"])
    return max(45, math.ceil((1.5 * distance + 2) / 0.2 + 25))


def score_trace(trace, direction, radius, scorer):
    rows = []
    for index in range(0, len(trace["time_s"]), 10):
        rows.append(
            {
                "wall_ns": round(float(trace["time_s"][index]) * 1e9),
                "data": {
                    "time": float(trace["time_s"][index]),
                    "world": {
                        "ballPosition": trace["qpos"][index, 29:32]
                        .astype(float)
                        .tolist(),
                        "ballContacts": [{"name": "robot1"}]
                        if trace["contact_flags"][index, 0]
                        else [],
                    },
                },
            }
        )
    # Include the last state, preserving partial final control cycles.
    if rows[-1]["wall_ns"] != round(float(trace["time_s"][-1]) * 1e9):
        rows.append(
            {
                "wall_ns": round(float(trace["time_s"][-1]) * 1e9),
                "data": {
                    "time": float(trace["time_s"][-1]),
                    "world": {
                        "ballPosition": trace["qpos"][-1, 29:32].astype(float).tolist(),
                        "ballContacts": [{"name": "robot1"}]
                        if trace["contact_flags"][-1, 0]
                        else [],
                    },
                },
            }
        )
    return scorer.evaluate(
        rows,
        direction=direction,
        start_wall_ns=rows[0]["wall_ns"],
        end_wall_ns=rows[-1]["wall_ns"],
        geometry=scorer.GoalSpec(ball_radius=radius),
    )


def trial(controller, bridge, case, profile, output, scorer, timeout, viewer):
    radius = BALLS[profile]["radius_m"]
    yaw = case["yaw"]
    bridge.reset(
        init_pos=(*case["start"], controller.height),
        init_quat_wxyz=(math.cos(yaw / 2), 0, 0, math.sin(yaw / 2)),
    )
    bridge.data.qpos[7:29] = controller.default_q
    bridge._kp[:], bridge._kd[:] = controller.kp, controller.kd
    mujoco.mj_forward(bridge.model, bridge.data)
    for _ in range(200):
        physics_step(bridge, controller.effort)
    bridge.data.qpos[29:36] = [*case["ball"], radius, 1, 0, 0, 0]
    bridge.data.qvel[28:34] = 0
    mujoco.mj_forward(bridge.model, bridge.data)
    controller.reset_goal(np.array([7 * case["direction"], 0]), bridge)
    start = float(bridge.data.time)
    initial = bridge.data.qpos.copy().tolist()
    ball_geom = bridge.model.geom("ball").id
    feet = {bridge.model.body(n).id for n in ("left_foot_link", "right_foot_link")}
    trunk = bridge.model.body("Trunk").id
    times, qpos, qvel, flags, observations, obs_lengths, actions, targets, modes = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    first_contact = first_foot = first_kick_mode = fall_s = None
    previous_ball = bridge.ball_world().copy()
    limit = timeout or budget(case)
    terminal = None
    active_end = limit
    for _ in range(math.ceil((limit + 8) / 0.02)):
        wall = time.monotonic()
        elapsed = float(bridge.data.time) - start
        if terminal is None and elapsed >= limit:
            terminal, active_end = "timeout", elapsed
        if terminal is None:
            action, obs, raw = controller.action(bridge)
            bridge.publish_action(action)
            mode = controller.mode
            if mode in ("kick", "kick_loop") and first_kick_mode is None:
                first_kick_mode = elapsed
            padded = np.zeros(344, dtype=np.float32)
            padded[: len(obs)] = obs
            observations.append(padded)
            obs_lengths.append(len(obs))
            actions.append(np.r_[raw, np.zeros(22 - len(raw))])
            targets.append(bridge.q_target.astype(np.float32).copy())
            modes.append({"walk": 1, "kick": 2, "kick_loop": 3}[mode])
        for _ in range(10):
            physics_step(bridge, controller.effort)
            elapsed = float(bridge.data.time) - start
            if not np.isfinite(bridge.data.qpos).all():
                raise ValueError("Non-finite simulation state")
            contact, foot = contacts(bridge, ball_geom, feet)
            if contact and first_contact is None:
                first_contact = elapsed
            if foot and first_foot is None:
                first_foot = elapsed
            ball = bridge.ball_world().copy()
            if terminal is None:
                event = boundary_crossing(previous_ball, ball, radius)
                if event:
                    terminal = "boundary"
                    active_end = elapsed
            previous_ball = ball
            if fall_s is None and (
                bridge.data.qpos[2] < 0.25
                or bridge.data.xmat[trunk].reshape(3, 3)[2, 2] < 0.5
            ):
                fall_s = elapsed
                if terminal is None:
                    terminal, active_end = "fall", elapsed
            times.append(elapsed)
            qpos.append(bridge.data.qpos.astype(np.float32).copy())
            qvel.append(bridge.data.qvel.astype(np.float32).copy())
            flags.append((contact, foot))
        if viewer:
            if not viewer.is_running():
                terminal, active_end = "viewer_closed", elapsed
                break
            viewer.sync()
            time.sleep(max(0, 0.02 - (time.monotonic() - wall)))
        if terminal is not None and elapsed >= active_end + 8:
            break
    trace = {
        "time_s": np.asarray(times),
        "qpos": np.asarray(qpos),
        "qvel": np.asarray(qvel),
        "contact_flags": np.asarray(flags),
        "observation": np.asarray(observations),
        "observation_length": np.asarray(obs_lengths),
        "action": np.asarray(actions),
        "joint_target": np.asarray(targets),
        "controller_mode": np.asarray(modes),
    }
    path = output / f"{case['name']}.npz"
    np.savez_compressed(path, **trace)
    evaluation = score_trace(trace, case["direction"], radius, scorer)
    crossing = evaluation["first_boundary_crossing"]
    score_before_fall = bool(
        evaluation["goal"] is True and (fall_s is None or crossing["time"] < fall_s)
    )
    return {
        "case": case,
        "execution_error": None,
        "budget_s": limit,
        "elapsed_sim_s": elapsed,
        "active_end_s": active_end,
        "terminal": terminal,
        "fall_s": fall_s,
        "fell_during_attempt": bool(fall_s is not None and fall_s <= active_end),
        "fell_during_passive_tail": bool(fall_s is not None and fall_s > active_end),
        "upright_through_recording": fall_s is None,
        "scored_before_fall": score_before_fall,
        "first_robot_contact_s": first_contact,
        "first_foot_contact_s": first_foot,
        "first_kick_mode_s": first_kick_mode,
        "initial_qpos": initial,
        "trace": str(path),
        "trace_sha256": digest(path),
        "evaluation": evaluation,
    }


def worker(name, profile, root, output, cases, scorer_path, timeout, visible):
    root, output = Path(root), Path(output) / name / profile
    output.mkdir(parents=True)
    controller = GoalController(name, root)
    module = upstream(root)[0]
    module.BALL_RADIUS = BALLS[profile]["radius_m"]
    module.BALL_MASS = BALLS[profile]["mass_kg"]
    bridge = module.MujocoBridge(
        mjcf_path=str(root / "peter-runner/assets/k1_22dof_scene.xml"),
        default_q=controller.default_q,
        init_pos=(0, 0, controller.height),
        ball_xy=(0, 0),
        control_dt=0.02,
        physics_dt=0.002,
    )
    scorer = evaluator(scorer_path)
    view = None
    if visible:
        import mujoco.viewer

        view = mujoco.viewer.launch_passive(bridge.model, bridge.data)
    write(
        output / "controller.json",
        {
            "home_q": controller.default_q.tolist(),
            "kp": controller.kp.tolist(),
            "kd": controller.kd.tolist(),
            "torque_limit": controller.effort.tolist(),
            "initial_height_m": controller.height,
            "ball": BALLS[profile],
            "speed_limits": [0.5, 0.3, 0.6],
        },
    )
    rows = []
    try:
        for index, case in enumerate(cases):
            try:
                row = trial(
                    controller, bridge, case, profile, output, scorer, timeout, view
                )
            except Exception as error:  # noqa: BLE001 -- keep every attempted case
                row = {
                    "case": case,
                    "execution_error": f"{type(error).__name__}: {error}",
                    "terminal": "execution_error",
                }
            rows.append(row)
            write(output / "results.json", {"planned": len(cases), "trials": rows})
            print(
                f"{name}/{profile}: {index + 1}/{len(cases)} {case['name']} {row.get('evaluation', {}).get('outcome', 'error')}",
                flush=True,
            )
    finally:
        if view:
            view.close()
    valid = [r for r in rows if r.get("evaluation", {}).get("valid")]
    summary = {
        "policy": name,
        "ball_profile": profile,
        "planned": len(cases),
        "execution_errors": sum(r["execution_error"] is not None for r in rows),
        "valid_evaluations": len(valid),
        "goals": sum(r["evaluation"]["goal"] is True for r in valid),
        "goals_before_fall": sum(r.get("scored_before_fall", False) for r in rows),
        "falls_during_attempt": sum(r.get("fell_during_attempt", False) for r in rows),
        "falls_during_passive_tail": sum(
            r.get("fell_during_passive_tail", False) for r in rows
        ),
        "robot_contact": sum(r.get("first_robot_contact_s") is not None for r in rows),
        "foot_contact": sum(r.get("first_foot_contact_s") is not None for r in rows),
        "outcomes": {
            outcome: sum(r["evaluation"]["outcome"] == outcome for r in valid)
            for outcome in ("scored", "own_goal", "out", "short_or_wide", "unresolved")
        },
    }
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", choices=("peter", "bhuman", "both"), default="both")
    parser.add_argument(
        "--suite", choices=("single", "preflight", "grid"), default="single"
    )
    parser.add_argument("--case")
    parser.add_argument("--assets", type=Path, default=DEFAULT_ASSETS)
    parser.add_argument("--grid-file", type=Path, default=GRID)
    parser.add_argument("--evaluator-file", type=Path, default=EVALUATOR)
    parser.add_argument(
        "--ball-profile", choices=(*BALLS, "both"), default="light-small"
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=float)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--viewer", action="store_true")
    args = parser.parse_args()
    grid = json.loads(args.grid_file.read_text())
    cases = grid["cases"]
    if args.case:
        cases = [c for c in cases if c["name"] == args.case]
    elif args.suite == "preflight":
        cases = [c for c in cases if c["name"] in PREFLIGHT]
    elif args.suite == "single":
        cases = [c for c in cases if c["name"] == PREFLIGHT[0]]
    if (
        not cases
        or args.workers < 1
        or (args.timeout is not None and not 0 < args.timeout <= 180)
    ):
        parser.error(
            "Choose a valid case, positive worker count and timeout up to 180 s"
        )
    names = ("peter", "bhuman") if args.policy == "both" else (args.policy,)
    profiles = tuple(BALLS) if args.ball_profile == "both" else (args.ball_profile,)
    if args.viewer and (len(names) * len(profiles) * len(cases) != 1):
        parser.error("Viewer requires one policy, one ball profile and one case")
    output = (
        args.output
        or Path("benchmarks/results")
        / datetime.now(ZoneInfo("Australia/Sydney")).strftime(
            "%Y-%m-%d/k1-goal-policy-comparison/runs/%H%M%S-%f"
        )
    ).resolve()
    output.mkdir(parents=True, exist_ok=False)
    root = args.assets.expanduser().resolve()
    plan = {
        "schema": "runswift-goal-policy-comparison/1",
        "suite": args.suite,
        "cases": cases,
        "policies": names,
        "ball_profiles": profiles,
        "balls": BALLS,
        "timeout_override_s": args.timeout,
        "budgets_s": {c["name"]: args.timeout or budget(c) for c in cases},
        "passive_tail_s": 8,
        "grid_sha256": digest(args.grid_file),
        "evaluator_sha256": digest(args.evaluator_file),
        "repositories": REPOSITORIES,
        "models": {**MODELS, "bhuman-walk": (WALK_PATH, WALK_SHA)},
        "source_hashes": {
            p.name: digest(p) for p in Path(__file__).parent.glob("*.py")
        },
        "runtime": {
            "python": sys.version,
            "mujoco": mujoco.__version__,
            "numpy": np.__version__,
        },
        "upstream_source_hashes": {
            str(p.relative_to(root)): digest(p)
            for p in (root / "peter-runner/python-implementation/policy_runner").rglob(
                "*.py"
            )
        },
        "scene_asset_hashes": {
            str(p.relative_to(root)): digest(p)
            for p in (root / "peter-runner/assets").rglob("*")
            if p.is_file()
        },
        "inputs": "ideal truth; no camera; native homes and joint gains",
        "scope": "Existing grid placements and evaluator in shared flat-floor K1 MuJoCo scene; B-Human competition-motion port with benchmark waypoint requests, not full C++ framework; Peter published kick loop; virtual goal boundaries, no physical posts or other robots.",
    }
    write(output / "plan.json", plan)
    jobs = [
        (
            n,
            p,
            str(root),
            str(output),
            cases,
            str(args.evaluator_file.resolve()),
            args.timeout,
            args.viewer,
        )
        for n in names
        for p in profiles
    ]
    if len(jobs) == 1:
        rows = [worker(*jobs[0])]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            rows = [f.result() for f in [pool.submit(worker, *job) for job in jobs]]
    write(output / "summary.json", {"complete": True, "rows": rows})
    print(json.dumps(rows, indent=2), flush=True)
    return int(any(r["execution_errors"] for r in rows))


if __name__ == "__main__":
    raise SystemExit(main())

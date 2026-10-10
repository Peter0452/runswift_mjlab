"""Run fixed approach/kick/score trials; raw truth evaluates outcomes independently."""

import argparse
import hashlib
import json
import math
import time
import uuid
from contextlib import ExitStack, contextmanager
from dataclasses import asdict
from itertools import pairwise
from pathlib import Path
from threading import Thread

from score_benchmark import (
    DEFAULT_SEED,
    BenchmarkInputs,
    execution_budget,
    suite_cases,
)
from score_evaluator import (
    GoalSpec,
    aggregate_results,
    case_summary,
    evaluate,
    stage_results,
)
from world_model.adapters.booster import K1_MODEL_PATH, K1_MODEL_REVISION


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def wait_for_server(url):
    """Allow bounded, read-only startup before any trial or actuator is created."""
    from run import Scene
    from websockets.exceptions import InvalidMessage

    deadline = time.monotonic() + 30
    while True:
        try:
            scene = Scene(
                url, model_path=K1_MODEL_PATH, model_revision=K1_MODEL_REVISION
            )
            try:
                scene.until(lambda scene=scene: scene.frame.ns > 0, timeout=5)
            finally:
                scene.close()
            return
        except (OSError, InvalidMessage, TimeoutError):
            if time.monotonic() >= deadline:
                raise
            time.sleep(0.25)


def make_runner():
    """Use the production match runner and reviewed K1 fixture motion settings."""
    from match_runner import MatchPolicy, MatchRunner
    from navigation_planner import GlobalPlanner, GlobalPlannerConfig
    from path_tracker import PathTracker, PathTrackerConfig
    from skills.world import NavigateToPose, NavigationPolicy

    return MatchRunner(
        policy=MatchPolicy(kick_heading_rad=0.6, kick_bearing_rad=0.6),
        navigation=NavigateToPose(
            navigation_policy=NavigationPolicy(unknown_space="allow_unknown"),
            planner=GlobalPlanner(
                GlobalPlannerConfig(10, False, 0.25, tracking_reserve_m=0.2)
            ),
            tracker=PathTracker(
                PathTrackerConfig(
                    cruise_speed=0.2,
                    min_speed=0.05,
                    heading_lookahead=0.3,
                    heading_blend_dist=0.5,
                    goal_slowdown_dist=0.6,
                    cross_track_vel_cap=0.2,
                )
            ),
        ),
    )


def trial(case, directory, *, url, timeout):
    """Reset only before release, run one attempt, then observe eight passive seconds."""
    from benchmark_capture import Recorder
    from match_execution import MatchExecutive
    from match_feedback import SdkFeedback
    from match_runner import MatchGoal
    from rclpy.executors import SingleThreadedExecutor
    from run import Scene
    from transport import MatchRelay
    from world_model.adapters.booster import K1_MODEL, make_config
    from world_model_ros.booster_bridge import BoosterBridge
    from world_model_ros.node import WorldModelNode

    directory.mkdir(parents=True, exist_ok=False)
    (directory / "case.json").write_text(json.dumps(asdict(case), indent=2) + "\n")
    rows, errors = [], []
    reason, failure, start_ns, end_ns = None, None, None, None
    relay = executive = recorder = None
    stopped_at = None
    try:
        with (
            ExitStack() as cleanup,
            (directory / "controller.jsonl").open("x") as stream,
        ):
            scene = Scene(
                url,
                model_path=K1_MODEL_PATH,
                model_revision=K1_MODEL_REVISION,
                robot_height=0.55,
                robot2_body=24,
            )
            cleanup.callback(scene.close)
            scene.prepare(start=case.start, obstacle=(-6, 6))
            scene.command(
                "set_body_rotation",
                body_id=1,
                quat=[math.cos(case.yaw / 2), 0, 0, math.sin(case.yaw / 2)],
            )
            scene.command("reset_ball")
            scene.command("set_body_position", body_id=95, position=[*case.ball, 0.11])
            scene.command("set_body_position", body_id=95, is_dragging=False)
            scene.until(
                lambda: (
                    scene.frame.ball is not None
                    and math.dist(scene.frame.ball[:2], case.ball) < 0.02
                    and any(
                        r.name == "robot1"
                        and abs(
                            math.atan2(
                                math.sin(r.yaw - case.yaw), math.cos(r.yaw - case.yaw)
                            )
                        )
                        < 0.02
                        for r in scene.frame.robots
                    )
                )
            )
            scene.finish_setup()
            epoch = str(uuid.uuid4())
            node = WorldModelNode(
                make_config(epoch, model=K1_MODEL), epoch, period_sec=0.02
            )
            cleanup.callback(node.destroy_node)
            bridge = BoosterBridge(
                epoch,
                url=url,
                robot="robot1",
                radii={"robot2": 0.45},
                model=K1_MODEL,
                period_sec=0.05,
            )
            cleanup.callback(bridge.destroy_node)
            inputs = BenchmarkInputs(
                epoch,
                direction=case.direction,
                robot="robot1",
                radii={"robot2": 0.45},
                model=K1_MODEL,
            )
            bridge.builder = inputs
            executor = SingleThreadedExecutor()
            executor.add_node(node)
            executor.add_node(bridge)

            def spin():
                try:
                    executor.spin()
                except Exception as exc:  # noqa: BLE001 -- propagate executor faults
                    errors.append(repr(exc))

            worker = Thread(target=spin, daemon=True)
            worker.start()
            cleanup.callback(worker.join, timeout=2)
            cleanup.callback(executor.shutdown, timeout_sec=2)
            deadline = time.monotonic() + 10
            while node.session.context().world.self.field_pose.summary.value is None:
                if (
                    time.monotonic() > deadline
                    or errors
                    or bridge.error
                    or node.session.fault
                ):
                    raise RuntimeError(
                        ("World not ready", errors, bridge.error, node.session.fault)
                    )
                time.sleep(0.02)
            relay = MatchRelay()
            cleanup.callback(relay.close)
            recorder = Recorder(url, directory)
            cleanup.callback(recorder.close)
            runner = make_runner()
            feedback = SdkFeedback(wall_clock=time.monotonic_ns)
            executive = MatchExecutive(runner, relay, session=relay.session)
            cleanup.callback(executive.cancel, "cleanup")
            scene.release()
            start_ns = time.monotonic_ns()
            executive.start(
                MatchGoal(play_style="kick", kick_power=case.power, kick_duration_sec=8)
            )
            armed_attempt = None
            while True:
                cycle = time.monotonic()
                elapsed = (time.monotonic_ns() - start_ns) / 1e9
                inputs.state = "playing" if elapsed >= 1 else "initial"
                context, received = node.session.context_with_receipt(len(rows))
                receipt = relay.latest()
                if reason is None:
                    if errors or bridge.error or node.session.fault or recorder.error:
                        reason = "input_or_recording_fault"
                    elif receipt and receipt["failure"]:
                        reason = "actuator_fault:" + receipt["failure"]
                    elif elapsed >= timeout:
                        reason = "trial_timeout"
                    else:
                        result = executive.tick(
                            context,
                            received,
                            motion=feedback.read(receipt, context.now),
                        )
                        if (
                            result.status == "stopped"
                            or result.reason == "shot_departed_and_stopped"
                        ):
                            reason = result.reason
                        elif armed_attempt is not None and runner.state != "kick":
                            reason = "attempt_ended:" + result.reason
                        if result.intent and result.intent.kick is not None:
                            if armed_attempt not in (
                                None,
                                result.intent.kick_attempt_id,
                            ):
                                raise RuntimeError("Benchmark attempted a second shot")
                            armed_attempt = result.intent.kick_attempt_id
                result = executive.result
                aim = runner._locked_target  # Diagnostic only; never feeds decisions.
                row = {
                    "wall_ns": time.monotonic_ns(),
                    "sim_ns": context.now.ns,
                    "snapshot_ns": context.world.snapshot.as_of.ns,
                    "input_received_wall_ns": received,
                    "result": asdict(result),
                    "motion": receipt,
                    "aim_team_field": None if aim is None else [aim.x, aim.y],
                    "stop_reason": reason,
                    "input_fault": node.session.fault,
                    "bridge_fault": bridge.error,
                }
                rows.append(row)
                stream.write(json.dumps(row, allow_nan=False) + "\n")
                stream.flush()
                if reason is not None and stopped_at is None:
                    executive.cancel(reason)
                    stopped_at = time.monotonic()
                if stopped_at is not None and cycle - stopped_at >= 8:
                    break
                time.sleep(max(0, 0.05 - (time.monotonic() - cycle)))
            end_ns = time.monotonic_ns()
    except Exception as exc:  # noqa: BLE001 -- every failed trial is retained
        failure = repr(exc)
        reason = reason or "execution_error"
        end_ns = time.monotonic_ns()
    evaluation = {
        "valid": False,
        "goal": None,
        "outcome": "unknown",
        "issues": ["setup_failed"],
    }
    if start_ns is not None and (directory / "truth.jsonl").exists():
        try:
            evaluation = evaluate(
                read_rows(directory / "truth.jsonl"),
                direction=case.direction,
                start_wall_ns=start_ns,
                end_wall_ns=end_ns,
            )
        except (ValueError, KeyError, TypeError) as exc:
            evaluation = {
                "valid": False,
                "goal": None,
                "outcome": "unknown",
                "issues": [repr(exc)],
            }
    active = [bool(r["motion"] and r["motion"]["kick_requested"]) for r in rows]
    activations = sum(a and not (i and active[i - 1]) for i, a in enumerate(active))
    final = rows[-1]["motion"] if rows else None
    stopped = bool(
        final
        and final["sample"]
        and not final["kick_requested"]
        and not final["sample"]["kick_active"]
        and final["sample"]["ready"]
        and final["sample"]["mode"] == 2
        and not final["stop_errors"]
        and 0 <= rows[-1]["wall_ns"] - final["now_ns"] <= 150_000_000
        and 0 <= final["now_ns"] - final["sample"]["observed_ns"] <= 150_000_000
        and 0 <= final["now_ns"] - final["sample"]["status_ns"] <= 1_200_000_000
    )
    valid = bool(
        failure is None
        and not errors
        and not (recorder and recorder.error)
        and stopped
        and reason == "shot_departed_and_stopped"
        and activations == 1
        and evaluation["valid"]
        and evaluation["goal"] is not None
        and not any(
            r["motion"] and (r["motion"]["failure"] or r["motion"]["stop_errors"])
            for r in rows
        )
    )
    sent = [r for r in rows if r["result"]["intent"] is not None]
    kicks = [r for r in sent if r["result"]["intent"]["kick"] is not None]
    finished = next((r for r in rows if r["stop_reason"] is not None), None)
    metrics = {
        "first_kick_request_wall_s": (kicks[0]["wall_ns"] - start_ns) / 1e9
        if kicks
        else None,
        "execution_wall_s": (finished["wall_ns"] - start_ns) / 1e9
        if finished
        else None,
        "max_command_snapshot_age_ms": max(
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
    summary = {
        "case": asdict(case),
        "start_wall_ns": start_ns,
        "end_wall_ns": end_ns,
        "execution_reason": reason,
        "error": failure,
        "executor_errors": errors,
        "recording_error": recorder.error if recorder else None,
        "controller_stopped": stopped,
        "controller_activations": activations,
        "valid_trial": valid,
        "benchmark_success": valid
        and evaluation["goal"] is True
        and evaluation.get("contact_confirmed") is True,
        "evaluation": evaluation,
        "metrics": metrics,
        "states": sorted({r["result"]["state"] for r in rows}),
        "files_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.iterdir()
            if p.is_file()
        },
    }
    summary["stages"] = stage_results(summary, rows)
    write_json(directory / "summary.json", summary)
    return summary


def write_json(path, value):
    """Publish a complete checkpoint atomically; interrupted writes cannot truncate it."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


@contextmanager
def run_lock(directory, *, resume=False):
    """Allow one writer per run directory, with automatic lock release on process exit."""
    import fcntl

    directory.mkdir(parents=True, exist_ok=resume)
    with (directory / "run.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(
                "This run directory already has an active writer"
            ) from exc
        yield


def prepare_run(
    directory, *, resume=False, suite=None, seed=None, names=None, timeout=None
):
    """Freeze cases/settings before execution; resume must match the original manifest."""
    path = directory / "manifest.json"
    original = json.loads(path.read_text()) if resume else None
    if original is not None and original.get("schema") != "runswift-score-benchmark/2":
        raise ValueError(
            "Only version 2 manifests support resume; keep older runs intact"
        )
    suite = suite or (original["suite"] if original else "grid")
    seed = seed if seed is not None else original["seed"] if original else DEFAULT_SEED
    if timeout is None and original:
        timeout = original["timeout_override_s"]
    if timeout is not None and (not math.isfinite(timeout) or not 10 <= timeout <= 180):
        raise ValueError("Timeout override must be 10–180 seconds")
    if names is None and original:
        names = [c["name"] for c in original["cases"]]
    available = suite_cases(suite, seed)
    if names is not None and (not names or set(names) - {c.name for c in available}):
        raise ValueError("Requested case is not in the selected suite")
    selected = [c for c in available if names is None or c.name in names]
    manifest = {
        "schema": "runswift-score-benchmark/2",
        "suite": suite,
        "seed": seed,
        "scene": K1_MODEL_PATH,
        "revision": K1_MODEL_REVISION,
        "inputs": "ground truth; scripted referee; no camera perception",
        "team_field": "Rotate physical XY and yaw by pi for negative-goal inputs; physical placements stay fixed in the grid.",
        "geometry": asdict(GoalSpec()),
        "cases": [asdict(c) for c in selected],
        "timeout_override_s": timeout,
        "execution_timeouts_s": {
            c.name: timeout
            if timeout is not None
            else 45
            if suite == "smoke"
            else execution_budget(c)
            for c in selected
        },
        "budget_policy": "ceil((1.5 * start-to-ball distance + 2 m) / 0.2 m/s + 25 s), minimum 45 s; smoke uses 45 s",
        "passive_observation_s": 8,
        "input_hz": 20,
        "control_hz": 20,
        "unknown_space": "explicit allow_unknown, capped at 0.2 m/s; no invented clear space",
        "power_policy": "Fixed 1.5 for the baseline; distant shots may fall short. No retries or carrying into range.",
        "video": "Offline full-field MuJoCo replay of recorded physics; normal simulation time.",
        "source_sha256": {
            name: hashlib.sha256(
                Path(__file__).with_name(name).read_bytes()
            ).hexdigest()
            for name in (
                "score_benchmark.py",
                "run_score_benchmark.py",
                "score_evaluator.py",
            )
        },
    }
    # Normalise tuples to JSON arrays before comparing a loaded manifest.
    manifest = json.loads(json.dumps(manifest))
    if original is not None:
        if original != manifest:
            raise ValueError(
                "Resume settings or fixture source differ from the frozen manifest"
            )
    else:
        if path.exists():
            raise FileExistsError(path)
        write_json(path, manifest)
    return manifest, selected


def pending_cases(directory, manifest, selected):
    """Only untouched case directories may run; never retry failed or interrupted attempts."""
    pending = []
    for case, saved in zip(selected, manifest["cases"], strict=True):
        folder = directory / case.name
        if folder.exists():
            case_file = folder / "case.json"
            if case_file.exists() and json.loads(case_file.read_text()) != saved:
                raise ValueError("Saved placement differs from manifest: " + case.name)
        else:
            pending.append(case)
    return pending


def checkpoint(directory, manifest):
    """Report every planned case, even when execution stopped before reaching it."""
    results = [case_summary(directory, c) for c in manifest["cases"]]
    write_json(directory / "summary.json", results)
    write_json(directory / "totals.json", aggregate_results(results))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--suite", choices=("grid", "preflight", "smoke"))
    parser.add_argument("--seed", type=int)
    parser.add_argument("--case", action="append")
    parser.add_argument(
        "--timeout", type=float, help="Override distance-based wall-time budgets"
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Freeze the manifest without ROS or simulator access",
    )
    parser.add_argument("--url", default="ws://127.0.0.1:18788")
    args = parser.parse_args()
    with run_lock(args.output, resume=args.resume):
        manifest, selected = prepare_run(
            args.output,
            resume=args.resume,
            suite=args.suite,
            seed=args.seed,
            names=args.case,
            timeout=args.timeout,
        )
        pending = pending_cases(args.output, manifest, selected)
        results = checkpoint(args.output, manifest)
        if args.plan_only:
            print(
                json.dumps(
                    {
                        "cases": len(selected),
                        "pending": len(pending),
                        "manifest": str(args.output / "manifest.json"),
                    }
                )
            )
            return
        if pending:
            # Planning, checkpoint inspection and tests do not require ROS installed.
            import rclpy

            wait_for_server(args.url)
            rclpy.init()
            try:
                for case in pending:
                    result = trial(
                        case,
                        args.output / case.name,
                        url=args.url,
                        timeout=manifest["execution_timeouts_s"][case.name],
                    )
                    checkpoint(args.output, manifest)
                    print(
                        json.dumps(
                            {
                                "case": case.name,
                                "valid": result["valid_trial"],
                                "success": result["benchmark_success"],
                                "reason": result["execution_reason"],
                                "evaluation": result["evaluation"]["outcome"],
                                "error": result["error"],
                            }
                        ),
                        flush=True,
                    )
                    if not rclpy.ok():
                        break
            finally:
                if rclpy.ok():
                    rclpy.shutdown()
                checkpoint(args.output, manifest)
        results = checkpoint(args.output, manifest)
        if not all(r["valid_trial"] for r in results):
            raise SystemExit(
                "Benchmark includes failed, interrupted or incomplete trials; all traces retained."
            )


if __name__ == "__main__":
    main()

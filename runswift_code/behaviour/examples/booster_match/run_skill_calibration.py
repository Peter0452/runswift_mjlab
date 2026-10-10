"""Short, reusable K1 walk/kick calibration with independent recorded truth."""

import argparse
import fcntl
import importlib
import importlib.util
import importlib.metadata
import json
import math
import os
import platform
import subprocess
import sys
import tempfile
import time
import uuid
from contextlib import ExitStack, contextmanager
from dataclasses import asdict
from pathlib import Path
from threading import Thread

from calibration_policy import PolicyStep
from skill_calibration import (
    CalibrationCase,
    calibration_cases,
    evaluate_directory,
    measure_case,
    read_rows,
    sha256,
    trial_usable,
    write_json,
)


def prepare_run(
    directory,
    *,
    suite="quick",
    repeats=1,
    policy="calibration_policy:make_k1_policy",
    actuator="transport:MatchRelay",
    config=None,
    actuator_config=None,
    assets=(),
    names=None,
    resume=False,
    candidate_revision=None,
):
    if not 1 <= repeats <= 10:
        raise ValueError("Repeats must be between 1 and 10")
    module, separator, factory = policy.partition(":")
    if not separator or not factory:
        raise ValueError("Policy must be module:factory")
    spec = importlib.util.find_spec(module)
    if spec is None or not spec.origin:
        raise ValueError("Policy module not found: " + module)
    actuator_module, separator, actuator_factory = actuator.partition(":")
    if not separator or not actuator_factory:
        raise ValueError("Actuator must be module:factory")
    actuator_spec = importlib.util.find_spec(actuator_module)
    if actuator_spec is None or not actuator_spec.origin:
        raise ValueError("Actuator module not found: " + actuator_module)
    cases = calibration_cases(suite)
    if names:
        if set(names) - {c.name for c in cases}:
            raise ValueError("Unknown case in selected suite")
        cases = [c for c in cases if c.name in names]
    behaviour = Path(__file__).resolve().parents[2]
    sources = [
        Path(__file__).resolve().with_name(n)
        for n in (
            "run_skill_calibration.py",
            "skill_calibration.py",
            "calibration_policy.py",
            "benchmark_capture.py",
            "transport.py",
            "relay.py",
            "run.py",
            "run_score_benchmark.py",
        )
    ]
    sources.append(behaviour / "examples/booster_closed_loop/scene.py")
    sources.extend((behaviour / "scripts").rglob("*.py"))
    for folder in ("world_model", "world_model_ros"):
        sources.extend((behaviour.parent / "world_model" / folder).rglob("*.py"))
    try:
        commit = subprocess.check_output(
            ["git", "-C", str(behaviour), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        commit = None
    manifest = {
        "schema": "runswift-skill-calibration/1",
        "suite": suite,
        "repeats": repeats,
        "policy": {
            "factory": policy,
            "config": config or {},
            "entry_sha256": sha256(spec.origin),
            "assets_sha256": {str(Path(p).resolve()): sha256(p) for p in assets},
            "git_commit": candidate_revision or commit,
        },
        "actuator": {
            "factory": actuator,
            "config": actuator_config or {},
            "entry_sha256": sha256(actuator_spec.origin),
        },
        "inputs": "K1 simulator ground truth; no camera perception; scripted referee",
        "source_sha256": {
            str(p.relative_to(behaviour.parent)): sha256(p)
            for p in sorted(set(sources))
        },
        "control_hz": 20,
        "world_update_hz": 50,
        "settle_before_s": 1,
        "observe_after_s": 8,
        "limits": {
            "body_command_limit": 0.2,
            "turn_command_limit": 0.8,
            "kick_power": [1, 2],
            "intent_ms": 250,
            "observation_ms": 350,
        },
        "trials": [
            {"id": "%s-r%02d" % (c.name, repeat), "case": asdict(c)}
            for repeat in range(1, repeats + 1)
            for c in cases
        ],
    }
    manifest = json.loads(json.dumps(manifest))
    path = directory / "manifest.json"
    if resume:
        if json.loads(path.read_text()) != manifest:
            raise ValueError(
                "Resume policy, settings or source differ from frozen plan"
            )
    else:
        if path.exists() or any(directory.iterdir()):
            raise ValueError("Use a new output directory or --resume")
        write_json(path, manifest)
    return manifest


@contextmanager
def motion_lock():
    """Prevent concurrent calibration runners on the shared simulator host."""
    with (
        Path(tempfile.gettempdir())
        / ("runswift-skill-calibration-%s.lock" % os.getuid())
    ).open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def validate_step(step):
    if not isinstance(step, PolicyStep) or step.status not in {
        "running",
        "completed",
        "failed",
    }:
        raise ValueError("Policy must return a PolicyStep with a valid status")
    if math.hypot(*step.velocity[:2]) > 0.2 + 1e-8 or abs(step.velocity[2]) > 0.8:
        raise ValueError("Policy exceeds the calibrated fixture's motion limits")
    if step.status != "running" and (any(step.velocity) or step.kick is not None):
        raise ValueError("Terminal policy steps must stop motion")


def trial(
    case,
    directory,
    *,
    policy_factory,
    config,
    url,
    actuator_factory=None,
    actuator_config=None,
):
    # Keep ROS, numerical libraries and motion dependencies out of offline tooling.
    from action.match_intent import MatchIntent
    from benchmark_capture import Recorder
    from match_feedback import SdkFeedback
    from rclpy.executors import SingleThreadedExecutor
    from run import Scene, ScriptedRefereeInputs
    from transport import MatchRelay
    from world_model.adapters.booster import (
        K1_MODEL,
        K1_MODEL_PATH,
        K1_MODEL_REVISION,
        make_config,
    )
    from world_model_ros.booster_bridge import BoosterBridge
    from world_model_ros.node import WorldModelNode

    directory.mkdir(exist_ok=False)
    write_json(directory / "case.json", asdict(case))
    rows, errors = [], []
    reason = error = start_ns = end_ns = None
    policy = relay = recorder = None
    try:
        with ExitStack() as cleanup, (directory / "controller.jsonl").open(
            "x"
        ) as stream:
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
                quat=[math.cos(case.yaw_rad / 2), 0, 0, math.sin(case.yaw_rad / 2)],
            )
            ball = case.ball if case.kind != "walk" else (-4, 3)
            scene.command("reset_ball")
            scene.command("set_body_position", body_id=95, position=[*ball, 0.11])
            scene.command("set_body_position", body_id=95, is_dragging=False)
            scene.until(
                lambda: scene.frame.ball is not None
                and math.dist(scene.frame.ball[:2], ball) < 0.02
                and any(
                    r.name == "robot1"
                    and abs(
                        math.atan2(
                            math.sin(r.yaw - case.yaw_rad),
                            math.cos(r.yaw - case.yaw_rad),
                        )
                    )
                    < 0.02
                    for r in scene.frame.robots
                )
            )
            scene.finish_setup()
            epoch = str(uuid.uuid4())
            world_config = make_config(epoch, model=K1_MODEL)
            node = WorldModelNode(world_config, epoch, period_sec=0.02)
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
            inputs = ScriptedRefereeInputs(
                epoch, robot="robot1", radii={"robot2": 0.45}, model=K1_MODEL
            )
            inputs.state = "playing"
            bridge.builder = inputs
            executor = SingleThreadedExecutor()
            executor.add_node(node)
            executor.add_node(bridge)

            def spin():
                try:
                    executor.spin()
                except Exception as exc:
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
            relay = (actuator_factory or MatchRelay)(**(actuator_config or {}))
            cleanup.callback(relay.close)
            recorder = Recorder(url, directory)
            cleanup.callback(recorder.close)
            feedback = SdkFeedback(wall_clock=time.monotonic_ns)
            policy = policy_factory(case, world_config.field.frame, config)
            cleanup.callback(policy.cancel)
            write_json(
                directory / "environment.json",
                {
                    "python": sys.version,
                    "host": platform.node(),
                    "platform": platform.platform(),
                    "packages": {
                        name: importlib.metadata.version(name)
                        for name in (
                            "blackwell",
                            "jax",
                            "jaxlib",
                            "msgpack",
                            "websockets",
                        )
                    },
                    "simulator_image": subprocess.check_output(
                        [
                            "docker",
                            "inspect",
                            "--format",
                            "{{.Image}}",
                            "runswift-world-model-sim",
                        ],
                        text=True,
                    ).strip(),
                    "scene": K1_MODEL_PATH,
                    "revision": K1_MODEL_REVISION,
                    "relay_session": relay.session,
                },
            )
            scene.release()
            start_ns = time.monotonic_ns()
            stopped_at = None
            sequence = 0
            while True:
                cycle = time.monotonic()
                now = time.monotonic_ns()
                elapsed = (now - start_ns) / 1e9
                context, received = node.session.context_with_receipt(len(rows))
                receipt = relay.latest()
                intent, step = None, PolicyStep("settling")
                if reason is None:
                    if errors or bridge.error or node.session.fault or recorder.error:
                        reason = "input_or_recording_fault"
                    elif received is None or not 0 <= now - received <= 350_000_000:
                        reason = "observations_expired"
                    elif (
                        not 0
                        <= context.now.ns - context.world.snapshot.as_of.ns
                        <= 150_000_000
                    ):
                        reason = "snapshot_expired"
                    elif (
                        receipt is None
                        or not 0 <= now - receipt["now_ns"] <= 150_000_000
                    ):
                        reason = "actuator_feedback_expired"
                    elif receipt["failure"]:
                        reason = "actuator_fault:" + receipt["failure"]
                    elif elapsed > case.timeout_s:
                        reason = "trial_timeout"
                    else:
                        motion = feedback.read(receipt, context.now)
                        if motion is None or not motion.upright:
                            reason = "motion_feedback_unavailable_or_fallen"
                        else:
                            step = (
                                policy.tick(context, motion, max(0, elapsed - 1))
                                if elapsed >= 1
                                else PolicyStep("settling")
                            )
                            validate_step(step)
                            issued = time.monotonic_ns()
                            deadline_ns = min(
                                issued + 250_000_000, received + 350_000_000
                            )
                            intent = MatchIntent(
                                relay.session,
                                sequence,
                                issued,
                                deadline_ns,
                                step.velocity,
                                step.head,
                                step.kick,
                                "calibration-shot" if step.kick is not None else None,
                            )
                            relay.send(intent)
                            sequence += 1
                            if step.status != "running":
                                reason = (
                                    "completed"
                                    if step.status == "completed"
                                    else "policy_failed:" + step.reason
                                )
                row = {
                    "wall_ns": time.monotonic_ns(),
                    "snapshot_ns": context.world.snapshot.as_of.ns,
                    "input_received_wall_ns": received,
                    "stage": step.stage,
                    "policy_status": step.status,
                    "policy_reason": step.reason,
                    "intent": asdict(intent) if intent else None,
                    "motion": receipt,
                    "stop_reason": reason,
                }
                rows.append(row)
                stream.write(json.dumps(row, allow_nan=False) + "\n")
                stream.flush()
                if reason is not None and stopped_at is None:
                    relay.stop()
                    policy.cancel()
                    stopped_at = time.monotonic()
                if stopped_at is not None:
                    post_stop_faults = [
                        *errors,
                        bridge.error,
                        node.session.fault,
                        recorder.error,
                        receipt["failure"] if receipt else "feedback_missing",
                    ]
                    if any(post_stop_faults):
                        error = error or repr([f for f in post_stop_faults if f])
                if stopped_at is not None and cycle - stopped_at >= 8:
                    end_ns = row["wall_ns"]
                    break
                time.sleep(max(0, 0.05 - (time.monotonic() - cycle)))
    except Exception as exc:
        reason = reason or ("execution_error" if start_ns else "setup_failed")
        error = repr(exc)
        end_ns = rows[-1]["wall_ns"] if rows else None
    summary = {
        "id": directory.name,
        "case": asdict(case),
        "reason": reason,
        "error": error,
        "executor_errors": errors,
        "start_ns": start_ns,
        "end_ns": end_ns,
        "measurement": None,
        "usable": False,
        "relay_logs": list(relay.logs) if relay else [],
        "files_sha256": {p.name: sha256(p) for p in directory.iterdir() if p.is_file()},
    }
    if (
        start_ns is not None
        and end_ns is not None
        and (directory / "truth.jsonl").exists()
    ):
        summary["measurement"] = measure_case(
            case,
            read_rows(directory / "truth.jsonl"),
            rows,
            start_ns=start_ns,
            end_ns=end_ns,
        )
        summary["usable"] = trial_usable(summary)
    write_json(directory / "summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--suite", choices=("smoke", "quick"), default="quick")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--case", action="append")
    parser.add_argument("--policy", default="calibration_policy:make_k1_policy")
    parser.add_argument("--actuator", default="transport:MatchRelay")
    parser.add_argument("--policy-config", type=Path)
    parser.add_argument("--actuator-config", type=Path)
    parser.add_argument("--asset", type=Path, action="append", default=[])
    parser.add_argument(
        "--candidate-revision", help="Git revision when running a synced source tree"
    )
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--evaluate-only", action="store_true")
    parser.add_argument("--url", default="ws://127.0.0.1:18788")
    args = parser.parse_args()
    if args.evaluate_only:
        report = evaluate_directory(args.output)
        write_json(args.output / "results.json", report)
        print(json.dumps(report["calibration"], indent=2))
        return
    args.output.mkdir(parents=True, exist_ok=True)
    config = json.loads(args.policy_config.read_text()) if args.policy_config else {}
    if not isinstance(config, dict):
        parser.error("Policy configuration must be a JSON object")
    actuator_config = (
        json.loads(args.actuator_config.read_text()) if args.actuator_config else {}
    )
    if not isinstance(actuator_config, dict):
        parser.error("Actuator configuration must be a JSON object")
    with motion_lock():
        manifest = prepare_run(
            args.output,
            suite=args.suite,
            repeats=args.repeats,
            policy=args.policy,
            actuator=args.actuator,
            config=config,
            actuator_config=actuator_config,
            assets=args.asset,
            names=args.case,
            resume=args.resume,
            candidate_revision=args.candidate_revision,
        )
        report = evaluate_directory(args.output)
        write_json(args.output / "results.json", report)
        if args.plan_only:
            print(
                json.dumps(
                    {
                        "planned": len(manifest["trials"]),
                        "manifest": str(args.output / "manifest.json"),
                    }
                )
            )
            return
        import rclpy
        from run_score_benchmark import wait_for_server

        module, factory = args.policy.split(":")
        policy_factory = getattr(importlib.import_module(module), factory)
        actuator_module, actuator_name = args.actuator.split(":")
        actuator_factory = getattr(
            importlib.import_module(actuator_module), actuator_name
        )
        rclpy.init()
        try:
            wait_for_server(args.url)
            for planned in manifest["trials"]:
                directory = args.output / planned["id"]
                if directory.exists():
                    continue  # Preserve failed/interrupted trials; never retry silently.
                summary = trial(
                    CalibrationCase(**planned["case"]),
                    directory,
                    policy_factory=policy_factory,
                    config=config,
                    url=args.url,
                    actuator_factory=actuator_factory,
                    actuator_config=actuator_config,
                )
                print(
                    json.dumps(
                        {
                            "id": planned["id"],
                            "reason": summary["reason"],
                            "usable": summary["usable"],
                        }
                    ),
                    flush=True,
                )
                report = evaluate_directory(args.output)
                write_json(args.output / "results.json", report)
        finally:
            rclpy.shutdown()
    print(json.dumps(report["calibration"], indent=2))
    if report["calibration"]["excluded"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

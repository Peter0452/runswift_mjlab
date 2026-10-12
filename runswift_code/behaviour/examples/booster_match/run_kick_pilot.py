"""Small K1 ground-truth kick pilot; run on the isolated Linux simulator host."""

import argparse
import json
import time
import uuid
from contextlib import ExitStack
from dataclasses import asdict
from pathlib import Path
from threading import Thread

import rclpy
from kick_pilot import KickPilot, measure
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

from world_model import types as wm


def trial(output, *, power, url, kick_timeout, mode, input_hz):
    """Reset before arming, then let native motion and physics determine the result."""
    origin = (-4.0, 0.0)
    rows, errors = [], []
    pilot = relay = bridge = node = None
    stopped_at = None
    failure = None
    with ExitStack() as cleanup, output.open("x", encoding="utf-8") as stream:
        try:
            scene = Scene(
                url,
                model_path=K1_MODEL_PATH,
                model_revision=K1_MODEL_REVISION,
                robot_height=0.55,
                robot2_body=24,
            )
            cleanup.callback(scene.close)
            # A parked helper enables named SDK channels; it is held out of play.
            scene.prepare(start=(origin[0] - 0.65, 0.0), obstacle=(-6.0, 6.0))
            scene.command("reset_ball")
            scene.command("set_body_position", body_id=95, position=[*origin, 0.11])
            scene.command("set_body_position", body_id=95, is_dragging=False)
            scene.until(
                lambda: (
                    scene.frame.ball is not None
                    and abs(scene.frame.ball[0] - origin[0]) < 0.02
                    and abs(scene.frame.ball[1]) < 0.02
                )
            )
            scene.finish_setup()
            epoch = str(uuid.uuid4())
            config = make_config(epoch, model=K1_MODEL)
            node = WorldModelNode(config, epoch, period_sec=0.02)
            cleanup.callback(node.destroy_node)
            bridge = BoosterBridge(
                epoch,
                url=url,
                robot="robot1",
                radii={"robot2": 0.45},
                model=K1_MODEL,
                period_sec=1.0 / input_hz,
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
                except Exception as exc:  # noqa: BLE001 -- preserve thread failure
                    errors.append(repr(exc))

            worker = Thread(target=spin, daemon=True)
            worker.start()
            cleanup.callback(worker.join, timeout=2)
            cleanup.callback(executor.shutdown, timeout_sec=2)
            deadline = time.monotonic() + 10
            while node.session.context().world.self.field_pose.summary.value is None:
                if (
                    time.monotonic() >= deadline
                    or errors
                    or bridge.error
                    or node.session.fault
                ):
                    raise RuntimeError(
                        (
                            "World input not ready",
                            errors,
                            bridge.error,
                            node.session.fault,
                        )
                    )
                time.sleep(0.02)
            relay = MatchRelay()
            cleanup.callback(relay.close)
            target = wm.FramedPoint2(config.field.frame, wm.Point2(7.0, 0.0))
            pilot = KickPilot(
                relay, target, power=power, timeout=kick_timeout, mode=mode
            )
            cleanup.callback(pilot.stop, "cleanup")
            scene.release()
            scene.close()
            began = time.monotonic()
            while time.monotonic() - began < kick_timeout + 12:
                cycle = time.monotonic()
                context, received = node.session.context_with_receipt(len(rows))
                receipt = relay.latest()
                intent = None
                if pilot.reason is None and cycle - began >= 1.0:
                    if errors or bridge.error or node.session.fault:
                        pilot.stop("input_fault")
                    else:
                        intent = pilot.tick(context, received, receipt)
                if pilot.reason is not None:
                    stopped_at = stopped_at or time.monotonic()
                raw = bridge._latest
                own = (
                    next((r for r in raw.robots if r.name == "robot1"), None)
                    if raw
                    else None
                )
                row = {
                    "wall_ns": time.monotonic_ns(),
                    "sim_ns": raw.ns if raw else None,
                    "decision_ns": context.now.ns,
                    "snapshot_ns": context.world.snapshot.as_of.ns,
                    "input_received_wall_ns": received,
                    "ball": raw.ball if raw else None,
                    "truth": asdict(own) if own else None,
                    "motion": receipt,
                    "intent": asdict(intent) if intent else None,
                    "stop_reason": pilot.reason,
                    "shot_phase": getattr(pilot.skill, "phase", None),
                    "input_fault": node.session.fault,
                    "bridge_fault": bridge.error,
                }
                rows.append(row)
                stream.write(json.dumps(row, allow_nan=False) + "\n")
                stream.flush()
                # Observe passive ball travel after disarming; never command a retry.
                if stopped_at is not None and cycle - stopped_at >= 8.0:
                    break
                time.sleep(max(0.0, 0.05 - (time.monotonic() - cycle)))
            else:
                pilot.stop("trial_timeout")
        except Exception as exc:  # noqa: BLE001 -- retain every failed trial
            failure = repr(exc)
        finally:
            if pilot is not None:
                pilot.stop("trial_finished")
    reason = pilot.reason if pilot else "setup_failed"
    summary = measure(rows, origin, stop_reason=reason)
    summary.update(
        power=power,
        profile=K1_MODEL,
        inputs="ground_truth",
        origin=origin,
        target=(7.0, 0.0),
        error=failure,
        executor_errors=errors,
        mode=mode,
        input_hz=input_hz,
    )
    if rows:
        last = rows[-1]["motion"]
        summary["controller_stopped"] = bool(
            last
            and last["sample"]
            and not last["sample"]["kick_active"]
            and not last["kick_requested"]
            and not last["stop_errors"]
            and 0 <= rows[-1]["wall_ns"] - last["now_ns"] <= 150_000_000
            and 0 <= last["now_ns"] - last["sample"]["status_ns"] <= 1_200_000_000
        )
    summary["range_usable"] = bool(
        mode == "range"
        and reason == "shot_departed_and_stopped"
        and summary.get("controller_stopped")
        and summary.get("range_settled")
        and not summary.get("field_boundary_reached")
        and failure is None
    )
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--powers", type=float, nargs="+", default=[1.0, 1.5, 2.0])
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--kick-timeout", type=float, default=12.0)
    parser.add_argument("--mode", choices=("range", "completion"), default="range")
    parser.add_argument("--input-hz", type=float, default=20.0)
    parser.add_argument("--url", default="ws://127.0.0.1:18788")
    args = parser.parse_args()
    if not 1 <= args.repeats <= 3 or not all(1 <= p <= 2 for p in args.powers):
        parser.error("Use 1–3 repeats and powers in [1, 2]")
    if len(set(args.powers)) != len(args.powers) or not 0 < args.kick_timeout <= 20:
        parser.error("Use distinct powers and a timeout in (0, 20] seconds")
    if not 5 <= args.input_hz <= 20:
        parser.error("Input rate must be between 5 and 20 Hz")
    args.output.mkdir(parents=True, exist_ok=False)
    results = []
    rclpy.init()
    try:
        for repeat in range(args.repeats):
            for power in args.powers:
                name = f"power-{power:g}-repeat-{repeat + 1}"
                try:
                    result = trial(
                        args.output / (name + ".jsonl"),
                        power=power,
                        url=args.url,
                        kick_timeout=args.kick_timeout,
                        mode=args.mode,
                        input_hz=args.input_hz,
                    )
                except Exception as exc:  # noqa: BLE001 -- preserve cleanup failures too
                    result = {"power": power, "mode": args.mode, "error": repr(exc)}
                result["trial"] = name
                results.append(result)
                (args.output / "summary.json").write_text(
                    json.dumps(results, indent=2) + "\n"
                )
                print(json.dumps(result), flush=True)
                if not rclpy.ok():
                    raise SystemExit(
                        "Pilot interrupted; retained completed traces and outcomes"
                    )
        if not all(
            (r.get("range_usable") if args.mode == "range" else r.get("sdk_completed"))
            and r.get("controller_stopped")
            and not r["error"]
            for r in results
        ):
            raise SystemExit(
                "Pilot includes incomplete or failed attempts; see retained traces"
            )
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()

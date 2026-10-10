"""Validate live K1 match decisions through ROS 2 inputs and the native SDK.

Ground-truth sensing and synthetic referee reports are explicitly labelled.
Run on the Linux Docker host; the motion deadline clock is shared with Docker.
"""

import argparse
import json
import sys
import time
import uuid
from contextlib import ExitStack
from dataclasses import asdict, replace
from math import hypot
from pathlib import Path
from threading import Thread

import rclpy
from match_execution import MatchExecutive
from match_feedback import SdkFeedback
from match_runner import MatchGoal, MatchPolicy, MatchRunner
from navigation_planner import GlobalPlanner, GlobalPlannerConfig
from path_tracker import PathTracker, PathTrackerConfig
from rclpy.executors import SingleThreadedExecutor
from skills.world import NavigateToPose, NavigationPolicy
from transport import MatchRelay
from world_match_replay import open_play_report
from world_model.adapters.booster import (
    K1_MODEL,
    K1_MODEL_PATH,
    K1_MODEL_REVISION,
    make_config,
)
from world_model_ros.booster import BoosterBatchBuilder
from world_model_ros.booster_bridge import BoosterBridge
from world_model_ros.node import WorldModelNode

from world_model import types as wm

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "booster_closed_loop"))
from scene import Scene

SCENARIOS = (
    "sequence",
    "cancel_kick",
    "command_expiry",
    "observation_expiry",
    "referee_stop",
)


class ScriptedRefereeInputs(BoosterBatchBuilder):
    """Simulator test fixture: scripted permissions, optionally withheld ball input."""

    state = "initial"
    hide_ball = False

    def build(self, frame):
        batch = super().build(replace(frame, ball=None) if self.hide_ball else frame)
        report = wm.WorldEvent(
            wm.InputMeta(
                wm.EventId("scripted-referee", self.epoch, batch.sequence),
                None,
                batch.as_of,
                batch.as_of,
                "synchronised",
                0,
                self.config.configuration_id,
            ),
            open_play_report(state=self.state),
        )
        return replace(batch, events=(*batch.events, report))


def run_scenario(name, output, *, url, timeout):
    scene = relay = executor = worker = node = bridge = executive = None
    errors, rows = [], []
    summary = None
    start = (-1.3, 0.0) if name == "sequence" else (-0.65, 0.0)
    injected = None
    stop_started = stop_confirmed = None
    kick_started = False
    try:
        scene = Scene(
            url,
            model_path=K1_MODEL_PATH,
            model_revision=K1_MODEL_REVISION,
            robot_height=0.55,
            robot2_body=24,
        )
        scene.prepare(start=start, obstacle=(0.0, 3.0))
        scene.command("set_body_position", body_id=95, position=[0.0, 0.0, 0.11])
        scene.command("set_body_position", body_id=95, is_dragging=False)
        scene.until(
            lambda: scene.frame.ball is not None and hypot(*scene.frame.ball[:2]) < 0.02
        )
        scene.finish_setup()
        epoch = str(uuid.uuid4())
        config = make_config(epoch, model=K1_MODEL)
        node = WorldModelNode(config, epoch, period_sec=0.02)
        bridge = BoosterBridge(
            epoch,
            url=url,
            robot="robot1",
            radii={"robot2": 0.45},
            model=K1_MODEL,
            period_sec=0.05,
        )
        inputs = ScriptedRefereeInputs(
            epoch, robot="robot1", radii={"robot2": 0.45}, model=K1_MODEL
        )
        inputs.hide_ball = name == "sequence"
        bridge.builder = inputs
        executor = SingleThreadedExecutor()
        executor.add_node(node)
        executor.add_node(bridge)

        def spin():
            try:
                executor.spin()
            except Exception as exc:  # noqa: BLE001 -- propagate executor failure
                errors.append(repr(exc))

        worker = Thread(target=spin, daemon=True)
        worker.start()
        deadline = time.monotonic() + 10
        while node.session.context().world.self.field_pose.summary.value is None:
            if (
                time.monotonic() > deadline
                or errors
                or bridge.error
                or node.session.fault
            ):
                raise RuntimeError(
                    ("World input not ready", errors, bridge.error, node.session.fault)
                )
            time.sleep(0.02)
        relay = MatchRelay()
        feedback = SdkFeedback(wall_clock=time.monotonic_ns)
        runner = MatchRunner(
            # K1's visual-kick controller turns while positioning its feet.
            # Keep checking ball/aim uncertainty and the entire clear corridor.
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
        executive = MatchExecutive(
            runner,
            relay,
            session=relay.session,
            command_ns=250_000_000,
        )
        # Preparation holds the trunk; release it before any tactical command.
        scene.release()
        scene.close()
        scene = None
        began = time.monotonic()
        executive.start(MatchGoal(kick_duration_sec=8.0))
        with output.open("x", encoding="utf-8") as stream:
            while time.monotonic() - began < timeout:
                cycle = time.monotonic()
                elapsed = cycle - began
                inputs.state = "initial" if elapsed < 1 else "playing"
                if name == "sequence" and elapsed > 4:
                    inputs.hide_ball = False
                context, received = node.session.context_with_receipt(len(rows))
                receipt = relay.latest()
                active = bool(
                    receipt and receipt["sample"] and receipt["sample"]["kick_active"]
                )
                if active:
                    kick_started = True
                if injected is None and active and name != "sequence":
                    injected = time.monotonic_ns()
                    if name == "cancel_kick":
                        executive.cancel()
                        stop_started = injected
                    elif name == "observation_expiry":
                        bridge._timer.cancel()  # Physics and evaluation stream continue.
                    elif name == "referee_stop":
                        inputs.state = "set"
                if injected is not None and name == "referee_stop":
                    inputs.state = "set"
                if receipt and receipt["failure"]:
                    if (
                        name not in {"command_expiry", "observation_expiry"}
                        or receipt["failure"] != "match_intent_expired"
                    ):
                        raise AssertionError("Actuator fault: " + str(receipt))
                    if executive.goal is not None:
                        executive.cancel(receipt["failure"])
                    stop_started = receipt["expired_at_ns"]
                if not (injected is not None and name == "command_expiry"):
                    executive.tick(
                        context, received, motion=feedback.read(receipt, context.now)
                    )
                result = executive.result
                raw = bridge._latest
                truth = (
                    next((r for r in raw.robots if r.name == "robot1"), None)
                    if raw
                    else None
                )
                row = {
                    "wall_ns": time.monotonic_ns(),
                    "decision_ns": context.now.ns,
                    "snapshot_ns": context.world.snapshot.as_of.ns,
                    "sim_ns": raw.ns if raw else None,
                    "referee": "scripted:" + inputs.state,
                    "ball_withheld": inputs.hide_ball,
                    "truth": asdict(truth) if truth else None,
                    "ball": raw.ball if raw else None,
                    "result": asdict(result),
                    "motion": receipt,
                    "input_fault": node.session.fault,
                }
                rows.append(row)
                stream.write(json.dumps(row, allow_nan=False) + "\n")
                stream.flush()
                if name == "sequence" and result.reason == "shot_stopping":
                    # Measure from the first stop intention, not from the later
                    # SingleShot success that already confirms controller exit.
                    stop_started = stop_started or row["wall_ns"]
                if (
                    name == "sequence"
                    and kick_started
                    and runner.state == "stand"
                    and injected is None
                ):
                    if result.reason != "shot_departed_and_stopped":
                        raise AssertionError(
                            "Unexpected post-kick hold: " + result.reason
                        )
                    if injected is None:
                        injected = time.monotonic_ns()
                        executive.cancel("sequence_finished")
                        stop_started = stop_started or injected
                if name == "observation_expiry" and injected is not None:
                    stop_started = received + executive.observation_ns
                if name == "referee_stop" and result.reason == "match_set":
                    stop_started = stop_started or time.monotonic_ns()
                stopping = stop_started is not None and receipt is not None
                stopped = (
                    stopping
                    and not active
                    and not receipt["kick_requested"]
                    and not receipt["stop_errors"]
                    and receipt["reason"] not in {"walking", "kicking", "enabling_kick"}
                )
                if stopped:
                    stop_confirmed = stop_confirmed or time.monotonic_ns()
                    if (
                        injected is not None
                        and time.monotonic_ns() - stop_confirmed >= 2_000_000_000
                    ):
                        break
                if (
                    errors
                    or bridge.error
                    or (node.session.fault and name != "observation_expiry")
                ):
                    raise AssertionError((errors, bridge.error, node.session.fault))
                if result.status == "stopped" and injected is None:
                    raise AssertionError("Match stopped: " + result.reason)
                time.sleep(max(0.0, 0.05 - (time.monotonic() - cycle)))
            else:
                raise TimeoutError(f"{name} did not complete in {timeout}s")
        assert kick_started, "SDK must report actual visual-kick entry"
        assert stop_confirmed is not None
        measured = [r for r in rows if r["truth"] is not None]
        travel = max(
            hypot(
                r["truth"]["position"][0] - start[0],
                r["truth"]["position"][1] - start[1],
            )
            for r in measured
        )
        ball_moved = max(
            hypot(*r["ball"][:2]) for r in measured if r["ball"] is not None
        )
        head_yaws = [
            r["motion"]["sample"]["head"][1]
            for r in rows
            if r["motion"] and r["motion"]["sample"]
        ]
        settling = [r for r in measured if r["wall_ns"] >= stop_confirmed]
        drift = max(
            hypot(
                r["truth"]["position"][0] - settling[0]["truth"]["position"][0],
                r["truth"]["position"][1] - settling[0]["truth"]["position"][1],
            )
            for r in settling
        )
        assert drift < 0.15, ("settling drift", drift)
        stop_ms = (stop_confirmed - stop_started) / 1e6
        assert stop_ms < 1500, ("SDK controller exit delay", stop_ms)
        if name == "sequence":
            assert {"stand", "search", "approach", "kick"} <= {
                r["result"]["state"] for r in rows
            }
            assert travel > 0.25 and max(head_yaws) - min(head_yaws) > 0.2
        summary = {
            "scenario": name,
            "profile": K1_MODEL,
            "referee": "scripted",
            "inputs": "ground_truth",
            "travel_m": travel,
            "head_yaw_range_rad": max(head_yaws) - min(head_yaws),
            "ball_displacement_m": ball_moved,
            "sdk_kick_entered": kick_started,
            "sdk_controller_exit_ms": stop_ms,
            "settling_drift_m": drift,
            "outcomes": sorted(
                {r["motion"]["kick_status"] for r in rows if r["motion"]}
            ),
            "passed": True,
        }
        return summary
    finally:
        # Every cleanup runs even if a failed transport also rejects cancel.
        with ExitStack() as cleanup:
            if scene is not None:
                cleanup.callback(scene.close)
            if node is not None:
                cleanup.callback(node.destroy_node)
            if bridge is not None:
                cleanup.callback(bridge.destroy_node)
            if worker is not None:
                cleanup.callback(worker.join, timeout=2)
            if executor is not None:
                cleanup.callback(executor.shutdown, timeout_sec=2)
            if relay is not None:
                cleanup.callback(relay.close)
            if executive is not None:
                cleanup.callback(executive.cancel, "test_finished")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=(*SCENARIOS, "all"), default="all")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--url", default="ws://127.0.0.1:18788")
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    rclpy.init()
    try:
        summaries = []
        for name in SCENARIOS if args.scenario == "all" else (args.scenario,):
            try:
                summary = run_scenario(
                    name,
                    args.output / (name + ".jsonl"),
                    url=args.url,
                    timeout=args.timeout,
                )
            except Exception as exc:  # noqa: BLE001 -- retain failed scenarios as evidence
                summary = {"scenario": name, "passed": False, "error": str(exc)}
            summaries.append(summary)
            print(json.dumps(summary), flush=True)
            (args.output / "summary.json").write_text(
                json.dumps(summaries, indent=2) + "\n"
            )
        if not all(s["passed"] for s in summaries):
            raise SystemExit(
                "One or more live scenarios failed; see summary.json and traces"
            )
    finally:
        rclpy.shutdown()


if __name__ == "__main__":
    main()

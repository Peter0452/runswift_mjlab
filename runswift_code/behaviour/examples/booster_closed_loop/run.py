"""Closed-loop navigation through the real Booster simulator motion controller.

Run on the Docker host with ROS Jazzy and Python >=3.11. The numerical world
runs on the host; the independent Python 3.10 motion relay runs inside the
isolated Humble simulator container. Camera perception is not used.
"""

import argparse
import json
import time
import uuid
from dataclasses import asdict
from math import atan2, cos, hypot, sin
from pathlib import Path
from threading import Thread

import rclpy
from navigation_execution import NavigationExecutive
from navigation_planner import GlobalPlanner, GlobalPlannerConfig
from path_tracker import PathTracker, PathTrackerConfig
from rclpy.executors import SingleThreadedExecutor
from scene import Scene
from skills.world import NavigateToPose, NavigateToPoseGoal, NavigationPolicy
from transport import MotionRelay
from world_model.adapters.booster import make_config
from world_model_ros.booster_bridge import BoosterBridge
from world_model_ros.node import WorldModelNode

from world_model import types as wm

SCENARIOS = ("goal", "obstacle", "cancel", "command_expiry", "observation_expiry")


def run_scenario(name, output, *, url="ws://127.0.0.1:18788", timeout=90):
    if name not in SCENARIOS:
        raise ValueError("Unknown scenario")
    scene = relay = executor = worker = node = bridge = None
    log = output.open("x", encoding="utf-8")
    start = (-2.0, 0.0)
    obstacle = (0.0, 0.0) if name == "obstacle" else (0.0, 2.5)
    target = (2.0, 0.0, 0.0) if name == "obstacle" else (-0.5, 0.0, 0.0)
    samples = []
    freeze_after = None
    injected_at = None
    active = False
    nav = None
    background_errors = []
    stop_delay_ms = None
    expected_stop_ns = None
    try:
        scene = Scene(url)
        scene.prepare(start=start, obstacle=obstacle)
        scene.finish_setup()
        epoch = str(uuid.uuid4())
        config = make_config(epoch)
        # Construction warms Blackwell before subscriptions or motion deadlines.
        node = WorldModelNode(config, epoch)
        bridge = BoosterBridge(epoch, url=url, robot="robot1", radii={"robot2": 0.45})
        executor = SingleThreadedExecutor()
        executor.add_node(node)
        executor.add_node(bridge)

        def spin():
            try:
                executor.spin()
            except Exception as exc:  # noqa: BLE001 -- surface background failures to the runner
                background_errors.append(repr(exc))

        worker = Thread(target=spin, daemon=True)
        worker.start()
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            context = node.session.context()
            if context.world.self.field_pose.summary.value is not None:
                break
            if node.session.fault or bridge.error or background_errors:
                raise RuntimeError(
                    (node.session.fault, bridge.error, background_errors)
                )
            time.sleep(0.02)
        else:
            raise TimeoutError("No usable simulator input")
        # Make command loss expire first in that test. In all other cases the
        # shorter remaining observation budget may legitimately win instead.
        relay = MotionRelay(
            command_ns=150_000_000 if name == "command_expiry" else 250_000_000
        )
        skill = NavigateToPose(
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
        )
        nav = NavigationExecutive(skill, relay)
        goal = NavigateToPoseGoal(
            wm.FramedPose2(config.field.frame, wm.Pose2(*target)),
            distance_tolerance=0.25,
            theta_tolerance=0.25,
            max_vx=0.2,
            max_vy=0.2,
            max_vtheta=0.8,
        )
        scene.release()
        scene.close()
        nav.start(goal)
        began = time.monotonic()
        stop_at = None
        while time.monotonic() - began < timeout:
            tick_start = time.monotonic()
            context, received = node.session.context_with_receipt(len(samples))
            now_ns = time.monotonic_ns()
            pose = context.world.self.field_pose.summary.value
            if pose is not None:
                measured = pose.pose
                distance_moved = hypot(measured.x - start[0], measured.y - start[1])
            else:
                measured, distance_moved = None, 0.0
            # Injection occurs only after observed movement, never just after a send.
            if injected_at is None and distance_moved >= 0.25 and name in SCENARIOS[2:]:
                injected_at = now_ns
                if name == "cancel":
                    expected_stop_ns = now_ns
                    nav.cancel()
                elif name == "command_expiry":
                    freeze_after = True  # World updates continue; no command refresh.
                else:
                    expected_stop_ns = received + nav.observation_ns
                    bridge._timer.cancel()  # No observations or /clock; physics continues.
            receipt = relay.latest()
            failed_motion = receipt is not None and receipt["reason"] not in {
                "moving",
                "idle",
                "stopped",
            }
            expected_fault = {
                "command_expiry": "command_expired",
                "observation_expiry": "observation_expired",
            }.get(name)
            if failed_motion and receipt["reason"] != expected_fault:
                raise AssertionError(f"Unexpected motion watchdog: {receipt}")
            if failed_motion and name == "command_expiry" and nav.goal is not None:
                nav.cancel("command_expired")
            if not freeze_after:
                nav.tick(context, received)
            if (
                name == "observation_expiry"
                and injected_at is not None
                and received is not None
            ):
                # A batch already in DDS at injection can still be applied.
                expected_stop_ns = received + nav.observation_ns
            receipt = relay.latest()
            result = nav.result
            if any(abs(v) > 1e-6 for v in result.velocity):
                active = True
            raw = bridge._latest  # Evaluation only; never fed directly to navigation.
            truth = (
                next((r for r in raw.robots if r.name == "robot1"), None)
                if raw
                else None
            )
            sample = {
                "wall_ns": now_ns,
                "sim_ns": raw.ns if raw else None,
                "snapshot_ns": context.world.snapshot.as_of.ns,
                "pose": asdict(measured) if measured else None,
                "truth": asdict(truth) if truth else None,
                "result": asdict(result),
                "motion": receipt,
                "input_fault": node.session.fault,
            }
            samples.append(sample)
            log.write(json.dumps(sample, allow_nan=False) + "\n")
            if name in ("goal", "obstacle"):
                stopped = result.status == "succeeded"
                if result.status == "stopped":
                    raise AssertionError(
                        f"Navigation stopped before arrival: {result.reason}"
                    )
            elif name == "cancel":
                stopped = injected_at is not None and result.reason == "cancelled"
            elif name == "command_expiry":
                stopped = receipt is not None and receipt["reason"] == "command_expired"
            else:
                stopped = result.reason == "observations_expired"
            if stopped and receipt and receipt["velocity"] == [0.0, 0.0, 0.0]:
                if stop_delay_ms is None and injected_at is not None:
                    expected_stop_ns = receipt.get("expired_at_ns") or expected_stop_ns
                    stop_delay_ms = (receipt["now_ns"] - expected_stop_ns) / 1e6
                    assert stop_delay_ms <= 100.0, stop_delay_ms
                stop_at = tick_start if stop_at is None else stop_at
                if tick_start - stop_at >= 2.0:
                    break
            if node.session.fault and name != "observation_expiry":
                raise AssertionError("World input fault: " + node.session.fault)
            if bridge.error or background_errors:
                raise AssertionError((bridge.error, background_errors))
            time.sleep(max(0.0, 0.05 - (time.monotonic() - tick_start)))
        else:
            raise TimeoutError(f"{name} did not finish in {timeout}s")
        assert active, "The scenario must actually command and observe movement"
        truth = [s["truth"] for s in samples if s["truth"] is not None]
        travelled = max(
            hypot(s["position"][0] - start[0], s["position"][1] - start[1])
            for s in truth
        )
        assert travelled > 0.25, travelled
        minimum_clearance = min(
            hypot(s["position"][0] - obstacle[0], s["position"][1] - obstacle[1])
            - (0.45 + 0.28)
            for s in truth
        )
        assert minimum_clearance > 0.04, minimum_clearance
        assert skill.debug.path is None, "Stop must clear navigation cache"
        final = truth[-1]
        distance = hypot(
            final["position"][0] - target[0], final["position"][1] - target[1]
        )
        if name in ("goal", "obstacle"):
            assert distance < 0.35, (
                distance
            )  # Includes settling after measured arrival.
            assert (
                abs(atan2(sin(final["yaw"] - target[2]), cos(final["yaw"] - target[2])))
                < 0.35
            )
        stopped_samples = [
            s for s in samples if s["wall_ns"] >= int(stop_at * 1e9) and s["truth"]
        ]
        origin = stopped_samples[0]["truth"]["position"]
        stop_drift = max(
            hypot(
                s["truth"]["position"][0] - origin[0],
                s["truth"]["position"][1] - origin[1],
            )
            for s in stopped_samples
        )
        assert stop_drift < 0.15, stop_drift
        if name in ("command_expiry", "observation_expiry"):
            after = [s for s in samples if s["wall_ns"] >= injected_at]
            assert after[-1]["sim_ns"] > after[0]["sim_ns"] + 1_000_000_000
            if name == "command_expiry":
                assert (
                    after[-1]["snapshot_ns"] > after[0]["snapshot_ns"] + 1_000_000_000
                )
            else:
                assert len({s["snapshot_ns"] for s in after[-10:]}) == 1
        if name == "obstacle":
            assert max(abs(s["position"][1]) for s in truth) > 0.8, (
                "Expected an actual detour"
            )
        result = {
            "scenario": name,
            "passed": True,
            "samples": len(samples),
            "goal_distance_m": distance,
            "travelled_m": travelled,
            "minimum_footprint_clearance_m": minimum_clearance,
            "stop_drift_m": stop_drift,
            "stop_delay_ms": stop_delay_ms,
            "motion_reason": relay.latest()["reason"],
        }
        print(json.dumps(result), flush=True)
        return result
    finally:
        # An SDK/pipe error must not skip the remaining shutdown operations.
        cleanups = [
            lambda: nav.cancel("shutdown") if nav else None,
            lambda: relay.close() if relay else None,
            lambda: executor.shutdown(timeout_sec=3) if executor else None,
            lambda: worker.join(timeout=3) if worker else None,
            lambda: bridge.destroy_node() if bridge else None,
            lambda: node.destroy_node() if node else None,
            lambda: scene.close() if scene else None,
            log.close,
        ]
        for cleanup in cleanups:
            try:
                cleanup()
            except Exception as exc:  # noqa: BLE001 -- attempt every remaining shutdown operation
                print(f"Shutdown error: {exc}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=(*SCENARIOS, "all"), default="all")
    parser.add_argument(
        "--output", type=Path, required=True, help="New directory for JSONL traces"
    )
    parser.add_argument("--url", default="ws://127.0.0.1:18788")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    rclpy.init()
    try:
        results = [
            run_scenario(name, args.output / (name + ".jsonl"), url=args.url)
            for name in (SCENARIOS if args.scenario == "all" else (args.scenario,))
        ]
        (args.output / "summary.json").write_text(json.dumps(results, indent=2) + "\n")
    finally:
        rclpy.shutdown()


if __name__ == "__main__":
    main()

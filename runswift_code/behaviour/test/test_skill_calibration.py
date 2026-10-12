"""Calibration measurement and reproducibility contracts without ROS or the SDK."""

import json
import math
import sys
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parents[1] / "examples/booster_match"
sys.path.insert(0, str(EXAMPLES))

from calibration_policy import PolicyStep
from run_skill_calibration import motion_lock, prepare_run, validate_step
from skill_calibration import (
    CalibrationCase,
    calibration_cases,
    calibration_report,
    evaluate_directory,
    measure_case,
    trial_usable,
)


def truth(
    times,
    *,
    robot=lambda t: (0, 0, 0),
    ball=lambda t: (-4, 0, 0.11),
    contact=lambda t: False,
):
    return [
        {
            "wall_ns": round((1 + t) * 1e9),
            "data": {
                "time": 10 + t,
                "world": {
                    "robots": [
                        {
                            "name": "robot1",
                            "position": [*robot(t)[:2], 0.55],
                            "yaw": robot(t)[2],
                            "upDot": 1,
                        }
                    ],
                    "ballPosition": list(ball(t)),
                    "ballContacts": [{"name": "robot1"}] if contact(t) else [],
                },
            },
        }
        for t in times
    ]


def command(t, velocity=(0, 0, 0), *, kick=None, stage="walk"):
    return {
        "wall_ns": round((1 + t) * 1e9),
        "stage": stage,
        "intent": {
            "issued_ns": round((1 + t) * 1e9),
            "velocity": velocity,
            "kick": kick,
        },
        "motion": None,
    }


def measure(case, values, controls):
    return measure_case(
        case,
        values,
        controls,
        start_ns=values[0]["wall_ns"],
        end_ns=values[-1]["wall_ns"],
    )


class MeasurementTest(unittest.TestCase):
    def test_a_stationary_walk_response_is_measured_without_claiming_motion(self):
        case = CalibrationCase("backward", "walk", velocity=(-0.1, 0, 0))
        values = truth([i * 0.05 for i in range(161)])
        result = measure(case, values, [command(0.5, case.velocity), command(5.5)])
        self.assertEqual(result["walk"][0]["measured_velocity"], [0, 0, 0])
        self.assertIsNone(result["walk"][0]["start_latency_s"])
        self.assertTrue(
            trial_usable(
                {
                    "case": asdict(case),
                    "measurement": result,
                    "reason": "completed",
                    "error": None,
                }
            )
        )

    def test_stop_and_restart_measure_braking_before_the_next_walk(self):
        case = CalibrationCase(
            "stop-resume",
            "walk",
            velocity=(0.2, 0, 0),
            duration_s=8,
            changes=((3, (0, 0, 0)), (5, (0.1, 0, 0))),
        )

        def pose(t):
            if t <= 3.2:
                return (0.2 * t, 0, 0)
            return (0.64 + 0.1 * max(0, min(t - 5.2, 2.8)), 0, 0)

        values = truth([i * 0.05 for i in range(221)], robot=pose)
        result = measure(
            case,
            values,
            [command(0, (0.2, 0, 0)), command(3), command(5, (0.1, 0, 0)), command(8)],
        )
        self.assertEqual(len(result["walk"]), 2)
        self.assertEqual(len(result["stop_restarts"]), 1)
        self.assertAlmostEqual(result["walk"][0]["stop_drift_m"], 0.04)
        self.assertLess(result["walk"][0]["stop_to_settled_s"], 1.1)
        self.assertAlmostEqual(result["stop_restarts"][0]["restart_latency_s"], 0.25)
        row = {"case": asdict(case), "measurement": result, "usable": True}
        report = calibration_report([row])
        self.assertEqual(
            set(report["walk"]), {"stop-resume/leg-1", "stop-resume/leg-2"}
        )

    def test_reversal_measures_delay_and_old_direction_overshoot(self):
        case = CalibrationCase(
            "reverse",
            "walk",
            velocity=(0.2, 0, 0),
            duration_s=8,
            changes=((4, (-0.2, 0, 0)),),
        )

        def pose(t):
            if t <= 4.3:
                return (0.2 * t, 0, 0)
            return (0.86 - 0.2 * min(t - 4.3, 3.7), 0, 0)

        values = truth([i * 0.05 for i in range(221)], robot=pose)
        result = measure(
            case,
            values,
            [command(0, (0.2, 0, 0)), command(4, (-0.2, 0, 0)), command(8)],
        )
        change = result["direction_changes"][0]
        self.assertGreaterEqual(change["direction_response_s"], 0.3)
        self.assertLess(change["direction_response_s"], 0.7)
        self.assertAlmostEqual(change["old_direction_overshoot_m"], 0.06)
        self.assertEqual(len(result["walk"]), 2)
        self.assertIsNone(result["walk"][0]["stop_to_settled_s"])
        self.assertIsNotNone(result["walk"][-1]["stop_to_settled_s"])

    def test_walk_gain_error_and_measured_transition_delays(self):
        case = CalibrationCase("forward", "walk", velocity=(0.2, 0, 0))
        values = truth(
            [i * 0.05 for i in range(161)],
            robot=lambda t: (0.16 * max(0, min(t - 0.7, 4.8)), 0, 0),
        )
        controls = [command(0.5, case.velocity), command(5.5)]
        result = measure(case, values, controls)
        self.assertTrue(result["valid"])
        walk = result["walk"][0]
        self.assertAlmostEqual(walk["gain"][0], 0.8)
        self.assertAlmostEqual(walk["velocity_error"][0], -0.04)
        self.assertAlmostEqual(walk["start_latency_s"], 0.25)
        self.assertGreater(walk["position_error_m"], 0.2)
        self.assertIsNotNone(walk["stop_to_settled_s"])

    def test_yaw_wrap_does_not_invent_a_full_turn(self):
        case = CalibrationCase("turn", "walk", velocity=(0, 0, 0.4))
        values = truth(
            [i * 0.05 for i in range(121)],
            robot=lambda t: (
                0,
                0,
                math.atan2(
                    math.sin(3 + 0.4 * min(t, 4)), math.cos(3 + 0.4 * min(t, 4))
                ),
            ),
        )
        result = measure(case, values, [command(0, case.velocity), command(4)])
        self.assertAlmostEqual(result["walk"][0]["measured_velocity"][2], 0.4)
        self.assertAlmostEqual(result["walk"][0]["displacement_local"][2], 1.6)

    def test_command_response_is_measured_in_the_robot_frame(self):
        case = CalibrationCase("left", "walk", velocity=(0, 0.1, 0))
        values = truth(
            [i * 0.05 for i in range(121)],
            robot=lambda t: (-0.1 * min(t, 4), 0, math.pi / 2),
        )
        result = measure(case, values, [command(0, case.velocity), command(4)])
        self.assertAlmostEqual(result["walk"][0]["gain"][1], 1)
        self.assertAlmostEqual(result["walk"][0]["measured_velocity"][0], 0)

    def test_changing_navigation_commands_are_integrated(self):
        case = CalibrationCase("transition", "transition")
        values = truth(
            [i * 0.05 for i in range(121)],
            robot=lambda t: (0.1 * min(t, 2) + 0.2 * max(0, min(t - 2, 2)), 0, 0),
        )
        controls = [
            command(0, (0.1, 0, 0), stage="approach"),
            command(2, (0.2, 0, 0), stage="approach"),
            command(4),
        ]
        result = measure(case, values, controls)
        self.assertAlmostEqual(result["walk"][0]["expected_displacement_local"][0], 0.6)
        self.assertIsNone(result["walk"][0]["gain"])

    def kick_trace(self, *, angle=0, yaw=0):
        case = CalibrationCase("kick", "kick", angle_rad=angle, yaw_rad=yaw)
        direction = angle + yaw
        values = truth(
            [i * 0.05 for i in range(161)],
            ball=lambda t: (
                case.ball[0]
                + 3.5 * min(max((t - 1) / 2, 0), 1) * math.cos(direction)
                - 0.2 * min(max((t - 1) / 2, 0), 1) * math.sin(direction),
                case.ball[1]
                + 3.5 * min(max((t - 1) / 2, 0), 1) * math.sin(direction)
                + 0.2 * min(max((t - 1) / 2, 0), 1) * math.cos(direction),
                0.11,
            ),
            contact=lambda t: 1 <= t < 1.1,
        )
        controls = [
            command(0.5, kick=(0, 1.5, 0.65, 0), stage="kick"),
            command(1.5, stage="kick"),
        ]
        for t, active, ready in (
            (0.8, True, False),
            (1.7, False, False),
            (1.9, False, True),
        ):
            at = round((1 + t) * 1e9)
            controls.append(
                {
                    "wall_ns": at,
                    "motion": {
                        "kick_status": "stopped" if ready else "running",
                        "sample": {
                            "observed_ns": at,
                            "status_ns": at,
                            "phase_ns": at,
                            "kick_active": active,
                            "ready": ready,
                        },
                    },
                }
            )
        controls.sort(key=lambda r: r["wall_ns"])
        return case, values, controls

    def test_range_and_accuracy_follow_requested_aim_in_both_directions(self):
        for angle, yaw in ((0, 0), (0.25, 0), (-0.25, math.pi)):
            case, values, controls = self.kick_trace(angle=angle, yaw=yaw)
            kick = measure(case, values, controls)["kick"]
            self.assertAlmostEqual(kick["final_forward_m"], 3.5)
            self.assertAlmostEqual(kick["final_lateral_m"], 0.2)
            self.assertAlmostEqual(kick["target_plane_lateral_error_m"], 0.2 * 3 / 3.5)
            self.assertAlmostEqual(kick["request_to_contact_s"], 0.5)
            self.assertAlmostEqual(kick["request_to_active_s"], 0.3)
            self.assertAlmostEqual(kick["stop_to_inactive_s"], 0.2)
            self.assertAlmostEqual(kick["stop_to_walking_ready_s"], 0.4)
            self.assertIsNone(kick["strike_count"])

    def test_preexisting_ready_status_cannot_prove_return_to_walking(self):
        case, values, controls = self.kick_trace()
        controls[-1]["motion"]["sample"]["status_ns"] = 2_000_000_000
        self.assertIsNone(
            measure(case, values, controls)["kick"]["stop_to_walking_ready_s"]
        )

    def test_short_shot_has_range_without_inventing_target_crossing(self):
        case, values, controls = self.kick_trace()
        for row in values:
            row["data"]["world"]["ballPosition"][0] = (
                -4 + (row["data"]["world"]["ballPosition"][0] + 4) / 4
            )
        kick = measure(case, values, controls)["kick"]
        self.assertFalse(kick["target_plane_reached"])
        self.assertIsNone(kick["target_plane_lateral_error_m"])
        self.assertTrue(kick["ball_settled"])

    def test_gaps_clock_resets_and_frozen_truth_are_excluded(self):
        case, values, controls = self.kick_trace()
        for invalid in (
            values[:20] + values[30:],
            [*values[:20], values[0], *values[20:]],
            [values[0]] * 20,
        ):
            self.assertFalse(measure(case, invalid, controls)["valid"])

    def test_no_contact_unsettled_and_boundary_travel_cannot_calibrate_range(self):
        case, values, controls = self.kick_trace()
        measured = measure(case, values, controls)
        summary = {
            "case": asdict(case),
            "reason": "completed",
            "error": None,
            "measurement": measured,
        }
        self.assertTrue(trial_usable(summary))
        for key, value in (
            ("contact_confirmed", False),
            ("ball_settled", False),
            ("boundary_censored", True),
            ("controller_activations", 2),
        ):
            measured["kick"][key] = value
            self.assertFalse(trial_usable(summary))
            measured["kick"][key] = {
                "contact_confirmed": True,
                "ball_settled": True,
                "boundary_censored": False,
                "controller_activations": 1,
            }[key]

    def test_failed_trials_stay_in_denominator_and_do_not_influence_calibration(self):
        case, values, controls = self.kick_trace()
        row = {
            "case": asdict(case),
            "measurement": measure(case, values, controls),
            "usable": True,
        }
        report = calibration_report([row, {"case": asdict(case), "usable": False}])
        self.assertEqual(
            (report["attempts"], report["usable"], report["excluded"]), (2, 1, 1)
        )
        result = next(iter(report["kick"].values()))["final_range_m"]
        self.assertEqual(result["n"], 1)
        self.assertIsNone(result["stddev"])


class PlanTest(unittest.TestCase):
    def test_motion_lock_excludes_a_second_runner_and_releases(self):
        with motion_lock():
            with self.assertRaises(BlockingIOError):
                with motion_lock():
                    pass
        with motion_lock():
            pass

    def test_actuator_candidate_is_frozen_with_the_policy(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            plan = prepare_run(directory, candidate_revision="baseline-revision")
            self.assertEqual(plan["actuator"]["factory"], "transport:MatchRelay")
            self.assertEqual(plan["policy"]["git_commit"], "baseline-revision")
            with self.assertRaises(ValueError):
                prepare_run(
                    directory,
                    actuator_config={"robot": "robot2"},
                    candidate_revision="baseline-revision",
                    resume=True,
                )

    def test_short_suite_has_walking_kicking_and_transitions(self):
        self.assertEqual(len(calibration_cases("quick")), 20)
        self.assertEqual(
            {c.kind for c in calibration_cases("smoke")}, {"walk", "kick", "transition"}
        )

    def test_plan_does_not_need_ros_and_resume_freezes_candidate_and_settings(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            original = prepare_run(directory, suite="smoke", repeats=2)
            self.assertEqual(len(original["trials"]), 6)
            self.assertEqual(
                prepare_run(directory, suite="smoke", repeats=2, resume=True), original
            )
            with self.assertRaises(ValueError):
                prepare_run(directory, suite="quick", repeats=2, resume=True)
            report = evaluate_directory(directory)
            self.assertEqual(report["calibration"]["excluded"], 6)

    def test_policy_configuration_and_asset_hashes_are_recorded(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            asset = directory / "weights.bin"
            asset.write_bytes(b"model-v1")
            output = directory / "run"
            output.mkdir()
            plan = prepare_run(output, config={"gain": 0.8}, assets=[asset])
            self.assertEqual(plan["policy"]["config"], {"gain": 0.8})
            asset.write_bytes(b"model-v2")
            with self.assertRaises(ValueError):
                prepare_run(output, config={"gain": 0.8}, assets=[asset], resume=True)

    def test_terminal_steps_cannot_leave_motion_active(self):
        with self.assertRaises(ValueError):
            validate_step(PolicyStep("done", velocity=(0.1, 0, 0), status="completed"))
        with self.assertRaises(ValueError):
            validate_step(PolicyStep("walk", velocity=(0.3, 0, 0)))


if __name__ == "__main__":
    unittest.main()

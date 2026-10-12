"""Pilot lifecycle and measurement contracts without ROS, Docker or the SDK."""

import sys
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "behaviour/scripts"))
sys.path.insert(0, str(ROOT / "behaviour/examples/booster_match"))

from kick_pilot import KickPilot, measure
from world_model.adapters.booster import (
    K1_MODEL,
    Frame,
    GroundTruthInputs,
    Robot,
    make_config,
)

from world_model import capture_tick, create_world_model
from world_model import types as wm


class PilotTest(unittest.TestCase):
    def setUp(self):
        self.wall = 1_000_000_000
        self.at = wm.TimePoint("pilot-test", 0)
        self.clock = SimpleNamespace(now=lambda: self.at)
        self.config = make_config("pilot-test", model=K1_MODEL)
        self.model = create_world_model(config=self.config, clock=self.clock)
        self.inputs = GroundTruthInputs(
            self.model.input, self.config, "pilot-test", robot="robot1", radii={}
        )
        self.port = Mock(session="pilot-session")
        target = wm.FramedPoint2(self.config.field.frame, wm.Point2(7, 0))
        self.pilot = KickPilot(
            self.port, target, power=1, mode="completion", clock=lambda: self.wall
        )
        self.receipt = {
            "now_ns": self.wall,
            "failure": None,
            "kick_attempt_id": None,
            "kick_status": "idle",
            "sample": {
                "observed_ns": self.wall,
                "status_ns": self.wall,
                "upright": True,
                "ready": True,
            },
        }
        self.sequence = 0

    def context(self, *, ball=(0, 0, 0.11), localised=True):
        frame = Frame(
            self.at.ns, self.sequence, (Robot("robot1", (-0.65, 0, 0.55), 0, 1),), ball
        )
        self.sequence += 1
        self.inputs.submit(frame, self.at, localised=localised)
        self.model.owner.advance(self.at)
        return capture_tick(self.model.reader, self.clock, self.sequence)

    def advance(self, ns=50_000_000):
        self.wall += ns
        self.at = replace(self.at, ns=self.at.ns + ns)
        self.receipt["now_ns"] = self.wall
        self.receipt["sample"].update(observed_ns=self.wall, status_ns=self.wall)

    def range_mode(self):
        self.pilot = KickPilot(
            self.port, self.pilot.goal.target, power=1, clock=lambda: self.wall
        )
        self.receipt.update(kick_attempt_id=self.pilot.attempt, kick_status="running")

    def tick(self, **kwargs):
        return self.pilot.tick(self.context(**kwargs), self.wall, self.receipt)

    def test_ball_departure_is_not_completion_and_uses_fresh_reference(self):
        self.assertIsNotNone(self.tick())
        self.advance()
        intent = self.tick(ball=(1, 0, 0.11))
        self.assertIsNone(self.pilot.reason)
        self.assertAlmostEqual(intent.kick[2], 1.65)
        self.assertEqual(intent.kick_attempt_id, self.pilot.attempt)

    def test_completed_attempt_stops_and_cannot_restart(self):
        self.tick()
        self.advance()
        self.receipt.update(kick_attempt_id=self.pilot.attempt, kick_status="completed")
        self.assertIsNone(self.tick())
        self.assertEqual(self.pilot.reason, "sdk_completed")
        self.advance()
        self.tick()
        self.port.send.assert_called_once()
        self.port.stop.assert_called_once()

    def test_another_attempts_completion_does_not_complete_this_one(self):
        self.receipt.update(kick_attempt_id="older", kick_status="completed")
        self.assertIsNotNone(self.tick())
        self.assertIsNone(self.pilot.reason)

    def test_missing_localisation_stops_fixed_goal_aim(self):
        self.assertIsNone(self.tick(localised=False))
        self.assertTrue(self.pilot.reason.startswith("world_or_skill:"))
        self.port.send.assert_not_called()

    def test_expired_observations_stop_even_with_frozen_world_clock(self):
        context = self.context()
        self.pilot.tick(context, self.wall, self.receipt)
        received = self.wall
        self.wall += 350_000_000
        self.receipt["now_ns"] = self.wall
        self.pilot.tick(context, received, self.receipt)
        self.assertEqual(self.pilot.reason, "observations_expired")

    def test_original_receipt_limits_command_deadline(self):
        intent = self.pilot.tick(self.context(), self.wall - 200_000_000, self.receipt)
        self.assertEqual(intent.valid_until_ns, self.wall + 150_000_000)

    def test_wall_timeout_does_not_claim_success_when_sim_time_stalls(self):
        self.tick()
        self.wall += 12_000_000_000
        self.receipt["now_ns"] = self.wall
        self.at = replace(self.at, ns=50_000_000)
        self.tick()
        self.assertEqual(self.pilot.reason, "kick_timeout")

    def test_stale_completion_feedback_cannot_complete(self):
        self.receipt.update(
            now_ns=self.wall - 151_000_000,
            kick_attempt_id=self.pilot.attempt,
            kick_status="completed",
        )
        self.tick()
        self.assertEqual(self.pilot.reason, "actuator_feedback_expired")

    def test_initial_ball_out_of_reach_is_rejected(self):
        self.tick(ball=(1, 0, 0.11))
        self.assertEqual(self.pilot.reason, "initial_alignment_rejected")
        self.port.send.assert_not_called()

    def test_range_mode_stops_after_departure_without_claiming_completion(self):
        self.range_mode()
        self.tick()
        self.advance()
        self.assertIsNotNone(self.tick(ball=(1, 0, 0.11)))
        self.advance(350_000_000)
        self.assertIsNone(self.tick(ball=(1.5, 0, 0.11)).kick)
        self.port.stop.assert_not_called()
        self.advance()
        self.receipt["kick_status"] = "stopped"
        self.assertIsNone(self.tick(ball=(1.6, 0, 0.11)))
        self.assertEqual(self.pilot.reason, "shot_departed_and_stopped")
        self.port.stop.assert_called_once()

    def test_stale_world_still_aborts_post_departure_interval(self):
        self.range_mode()
        self.tick()
        self.advance()
        context = self.context(ball=(1, 0, 0.11))
        self.pilot.tick(context, self.wall, self.receipt)
        self.advance(200_000_000)
        self.pilot.tick(replace(context, now=self.at), self.wall, self.receipt)
        self.assertEqual(self.pilot.reason, "world_or_skill:stale_snapshot")


class MeasurementTest(unittest.TestCase):
    def rows(self, positions):
        return [
            {
                "wall_ns": i * 100_000_000,
                "sim_ns": i * 100_000_000,
                "ball": (x, 0, 0.11),
                "motion": None,
            }
            for i, x in enumerate(positions)
        ]

    def test_range_is_displacement_not_distance_to_origin_or_path_length(self):
        result = measure(
            self.rows([-4, -3, -2, -3] + [-3] * 21),
            (-4, 0),
            stop_reason="sdk_completed",
        )
        self.assertEqual(result["max_displacement_m"], 2)
        self.assertEqual(result["final_ball"][0], -3)
        self.assertTrue(result["range_settled"])
        self.assertTrue(result["sdk_completed"])
        self.assertFalse(result["contact_confirmed"])

    def test_frozen_samples_do_not_prove_ball_settled(self):
        rows = self.rows([-4, -3])
        rows += [rows[-1]] * 30
        result = measure(rows, (-4, 0), stop_reason="kick_timeout")
        self.assertFalse(result["range_settled"])
        self.assertFalse(result["sdk_completed"])
        self.assertEqual(result["ball_samples"], 2)

    def test_completion_without_motion_does_not_prove_contact(self):
        result = measure(self.rows([-4] * 30), (-4, 0), stop_reason="sdk_completed")
        self.assertTrue(result["sdk_completed"])
        self.assertFalse(result["ball_moved"])
        self.assertFalse(result["contact_confirmed"])
        self.assertFalse(result["range_settled"])

    def test_previously_settled_ball_with_stalled_stream_is_not_fresh_evidence(self):
        rows = self.rows([-4, -3] + [-3] * 25)
        rows.append({**rows[-1], "wall_ns": rows[-1]["wall_ns"] + 1_000_000_000})
        self.assertFalse(
            measure(rows, (-4, 0), stop_reason="ball_departed")["range_settled"]
        )

    def test_large_sample_gap_cannot_prove_continuous_settling(self):
        rows = self.rows([-4, -3, -3])
        rows[-1]["sim_ns"] = rows[-1]["wall_ns"] = 2_000_000_000
        self.assertFalse(
            measure(rows, (-4, 0), stop_reason="ball_departed")["range_settled"]
        )


if __name__ == "__main__":
    unittest.main()

"""Actuator contracts exercised without ROS, vendor SDK or robot access."""

import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from threading import Lock
from types import SimpleNamespace
from unittest.mock import Mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS.parent / "examples/booster_match"))

from action.booster_match_sdk import BoosterMatchDriver
from action.match_actuator import MatchActuator, MotionSample
from action.match_intent import MatchIntent
from match_feedback import SdkFeedback
from relay import admit
from world_model.types import TimePoint

MS = 1_000_000


class Driver:
    def __init__(self, clock):
        self.clock = clock
        self.value = MotionSample(
            clock(), True, True, False, (0.0, 0.0), 0, clock(), 4, 10, clock()
        )
        self.calls = []
        self.errors = set()
        self.delay = None

    def sample(self):
        return self.value

    def ensure_mode(self, kick):
        return True

    def refresh(self, **kwargs):
        self.value = replace(
            self.value, observed_ns=self.clock(), status_ns=self.clock(), **kwargs
        )

    def call(self, name, value=None):
        self.calls.append((name, value))
        if self.delay:
            self.delay(name)
        if name in self.errors:
            raise RuntimeError(name + " failed")

    def move(self, value):
        self.call("move", value)

    def head(self, value):
        self.call("head", value)

    def reference(self, value):
        self.call("reference", value)

    def enable_kick(self):
        self.call("enable")

    def disable_kick(self):
        self.call("disable")


class ActuatorTest(unittest.TestCase):
    def setUp(self):
        self.ns = 1_000_000_000
        self.driver = Driver(lambda: self.ns)
        self.actuator = MatchActuator(self.driver, "test", clock=lambda: self.ns)
        self.sequence = -1

    def intent(self, *, kick=False, attempt="a", **kwargs):
        self.sequence += 1
        return MatchIntent(
            "test",
            self.sequence,
            self.ns,
            self.ns + 250 * MS,
            kwargs.get("velocity", (0.0, 0.0, 0.0) if kick else (0.1, 0.0, 0.0)),
            kwargs.get("head", (0.45, 0.8, 0.5, 0.5)),
            (0.0, 1.0, 0.6, 0.0) if kick else None,
            attempt if kick else None,
        )

    def send(self, **kwargs):
        self.driver.refresh()
        self.assertTrue(self.actuator.accept(self.intent(**kwargs)))
        return self.actuator.step()

    def test_expiry_revokes_kick_without_sender_or_simulation_progress(self):
        self.send(kick=True)
        self.ns += 250 * MS
        self.driver.refresh(kick_active=True)
        result = self.actuator.step()
        self.assertEqual(result["failure"], "match_intent_expired")
        self.assertEqual(result["expired_at_ns"], self.ns)
        self.assertEqual(
            self.driver.calls[-3:],
            [("disable", None), ("head", (0.0, 0.0)), ("move", (0.0, 0.0, 0.0))],
        )
        self.assertFalse(self.actuator.accept(self.intent()))

    def test_wire_round_trip_and_malformed_input(self):
        intent = self.intent(kick=True)
        self.assertEqual(
            MatchIntent.parse(json.loads(json.dumps(intent.message()))), intent
        )
        for update in (
            {"schema": "other"},
            {"extra": 1},
            {"session": 1},
            {"kick_attempt_id": 3},
            {"head": [float("nan")] * 4},
        ):
            with self.subTest(update=update), self.assertRaises(ValueError):
                MatchIntent.parse(intent.message() | update)

    def test_stop_envelope_fences_queued_commands(self):
        self.send(kick=True)
        admit(
            self.actuator,
            {
                "schema": "runswift-match/1",
                "stop": True,
                "session": "test",
                "through_sequence": 10,
            },
        )
        self.actuator.step()
        self.assertFalse(self.actuator.accept(self.intent()))
        self.assertEqual(self.driver.calls[-3][0], "disable")

    def test_wrong_session_cannot_cancel_valid_command(self):
        self.send()
        with self.assertRaises(ValueError):
            admit(
                self.actuator,
                {
                    "schema": "runswift-match/1",
                    "stop": True,
                    "session": "other",
                    "through_sequence": 10,
                },
            )

    def test_stale_fast_or_slow_feedback_and_fall_stop(self):
        for fields in (
            {"observed_ns": self.ns - 151 * MS},
            {"status_ns": self.ns - 1201 * MS},
            {"upright": False},
            {"ready": False},
            {"head": (float("nan"), 0.0)},
        ):
            with self.subTest(fields=fields):
                self.actuator = MatchActuator(
                    self.driver, "test", clock=lambda: self.ns
                )
                self.driver.refresh()
                self.driver.value = replace(self.driver.value, **fields)
                self.actuator.accept(self.intent())
                result = self.actuator.step()
                self.assertIsNotNone(result["failure"])
                self.assertIn(("move", (0.0, 0.0, 0.0)), self.driver.calls[-3:])

    def test_kick_ack_is_not_completion_and_references_refresh(self):
        result = self.send(kick=True)
        self.assertEqual(result["kick_status"], "idle")
        self.ns += 50 * MS
        self.driver.refresh(kick_active=True)
        result = self.send(kick=True)
        self.assertEqual(result["kick_status"], "running")
        self.assertEqual([c[0] for c in self.driver.calls].count("enable"), 1)
        self.assertEqual([c[0] for c in self.driver.calls].count("reference"), 2)

    def test_native_phase_transition_never_claims_single_shot_completion(self):
        self.driver.refresh(phase=1, phase_ns=self.ns - MS)
        self.send(kick=True)
        self.ns += 50 * MS
        self.driver.refresh(kick_active=True, phase=0, phase_ns=self.ns)
        self.assertEqual(self.send(kick=True)["kick_status"], "running")
        self.ns += 50 * MS
        self.driver.refresh(phase=1, phase_ns=self.ns)
        self.send(kick=True)
        self.ns += 50 * MS
        self.driver.refresh(phase=0, phase_ns=self.ns)
        self.assertEqual(self.send(kick=True)["kick_status"], "running")
        self.ns += 50 * MS
        self.driver.refresh(kick_active=False)
        self.assertNotEqual(self.send(kick=True)["kick_status"], "completed")
        self.assertEqual([c[0] for c in self.driver.calls].count("enable"), 1)

    def test_stop_during_transition_holds_body_until_sdk_leaves_kick(self):
        self.send(kick=True)
        self.driver.refresh(kick_active=True)
        result = self.send()
        self.assertEqual(result["reason"], "stopping_kick")
        self.assertEqual(
            self.driver.calls[-3:],
            [("disable", None), ("head", (0.0, 0.0)), ("move", (0.0, 0.0, 0.0))],
        )
        self.ns += 50 * MS
        self.driver.refresh(kick_active=False, phase_ns=self.ns)
        self.assertEqual(self.send()["reason"], "kick_stopped")
        self.assertEqual(self.send()["reason"], "walking")

    def test_stop_requires_new_feedback_and_cannot_rearm_a_finished_attempt(self):
        self.send(kick=True)
        self.driver.refresh(kick_active=True, phase=1, phase_ns=self.ns)
        self.ns += 50 * MS
        self.driver.refresh()
        self.assertEqual(self.send()["kick_status"], "stopping")
        self.ns += 50 * MS
        self.driver.refresh(kick_active=False)  # Old phase cannot confirm exit.
        self.assertEqual(self.send()["kick_status"], "stopping")
        self.ns += 50 * MS
        self.driver.refresh(phase=0, phase_ns=self.ns)
        self.assertEqual(self.send()["kick_status"], "stopped")
        self.assertEqual(self.send(kick=True)["kick_status"], "stopped")
        self.assertEqual([c[0] for c in self.driver.calls].count("enable"), 1)
        self.send(kick=True, attempt="b")
        self.ns += 50 * MS
        self.driver.refresh(kick_active=True)
        self.send()
        self.ns += 50 * MS
        self.driver.refresh(kick_active=False, phase=0, phase_ns=self.ns)
        self.send()
        self.assertEqual(self.send(kick=True, attempt="a")["kick_status"], "failed")
        self.assertEqual([c[0] for c in self.driver.calls].count("enable"), 2)

    def test_expiry_while_stopping_is_a_failure_not_completion(self):
        self.send(kick=True)
        self.driver.refresh(kick_active=True)
        self.send()
        self.ns += 251 * MS
        self.driver.refresh(kick_active=False, phase_ns=self.ns)
        result = self.actuator.step()
        self.assertEqual(result["kick_status"], "failed")
        self.assertEqual(result["failure"], "match_intent_expired")

    def test_zero_stop_waits_through_mode_transition_for_walking_readiness(self):
        self.send(kick=True)
        self.driver.ensure_mode = Mock(return_value=False)
        self.driver.refresh(kick_active=True)
        self.assertEqual(self.send(velocity=(0, 0, 0))["kick_status"], "stopping")
        self.ns += 50 * MS
        self.driver.refresh(kick_active=False, ready=False, phase_ns=self.ns)
        result = self.send(velocity=(0, 0, 0))
        self.assertIsNone(result["failure"])
        self.assertEqual(result["kick_status"], "stopping")
        self.driver.refresh(ready=True)
        self.assertEqual(self.send(velocity=(0, 0, 0))["kick_status"], "stopping")
        self.driver.ensure_mode.return_value = True
        self.assertEqual(self.send(velocity=(0, 0, 0))["kick_status"], "stopped")

    def test_stopping_does_not_allow_stale_feedback_or_nonzero_motion(self):
        for fields, velocity in (
            ({"ready": False}, (0.1, 0, 0)),
            ({"ready": False, "upright": False}, (0, 0, 0)),
            ({"ready": False, "observed_ns": self.ns - 151 * MS}, (0, 0, 0)),
        ):
            with self.subTest(fields=fields):
                self.setUp()
                self.send(kick=True)
                self.driver.value = replace(self.driver.value, **fields)
                self.actuator.accept(self.intent(velocity=velocity))
                self.assertIsNotNone(self.actuator.step()["failure"])

    def test_head_hold_precedes_mode_change_and_is_not_reissued_during_transition(self):
        self.send(kick=True)
        self.driver.stop_body = lambda: self.driver.call("stop_body")
        self.actuator.stop(self.sequence)
        self.actuator.step()
        self.assertEqual(
            [name for name, _ in self.driver.calls[-3:]],
            ["disable", "head", "stop_body"],
        )
        self.driver.calls.clear()
        self.driver.errors.add("head")  # SDK refuses this during a mode change.
        self.assertFalse(self.actuator.step()["stop_errors"])
        self.assertNotIn("head", [name for name, _ in self.driver.calls])
        self.driver.errors.clear()
        self.ns += 100 * MS
        self.send()  # A new head intention invalidates the old hold.
        self.actuator.stop(self.sequence)
        self.actuator.step()
        self.assertEqual([name for name, _ in self.driver.calls].count("head"), 2)

    def test_failed_head_hold_is_retried_without_skipping_body_stop(self):
        self.send(kick=True)
        self.driver.errors.add("head")
        self.actuator.stop(self.sequence)
        self.assertTrue(self.actuator.step()["stop_errors"])
        self.assertEqual(self.driver.calls[-1], ("move", (0, 0, 0)))
        self.driver.errors.clear()
        self.assertFalse(self.actuator.step()["stop_errors"])
        self.assertEqual(self.driver.calls[-2], ("head", (0, 0)))

    def test_failure_to_disable_does_not_skip_zero_or_head_hold_and_retries(self):
        self.send(kick=True)
        self.driver.errors.add("disable")
        self.actuator.stop(self.sequence)
        result = self.actuator.step()
        self.assertTrue(result["stop_errors"])
        self.assertTrue(result["kick_requested"])
        self.assertEqual(
            self.driver.calls[-2:], [("head", (0.0, 0.0)), ("move", (0.0, 0.0, 0.0))]
        )
        self.driver.errors.clear()
        self.assertFalse(self.actuator.step()["kick_requested"])

    def test_native_stop_failure_still_holds_head_and_is_retried(self):
        self.send(kick=True)
        self.driver.stop_body = Mock(
            side_effect=RuntimeError("mode transition rejected")
        )
        self.actuator.stop(self.sequence)
        result = self.actuator.step()
        self.assertIn("mode transition rejected", result["stop_errors"])
        self.assertEqual(self.driver.calls[-1][0], "head")
        self.driver.stop_body.side_effect = None
        self.assertFalse(self.actuator.step()["stop_errors"])
        self.assertEqual(self.driver.stop_body.call_count, 2)

    def test_delayed_enable_needs_feedback_and_replaced_attempt_requires_stop(self):
        self.send(kick=True)
        for _ in range(8):
            self.ns += 200 * MS
            result = self.send(kick=True)
        self.assertIn("kick_enable_not_confirmed", result["failure"])
        self.setUp()
        self.send(kick=True)
        self.assertIn("without_stop", self.send(kick=True, attempt="b")["failure"])

    def test_rpc_time_consumes_lease_and_head_is_rate_limited(self):
        self.ns += 20 * MS
        self.send()
        self.assertEqual(self.driver.calls[-1], ("head", (0.01, 0.01)))

        def delay(name):
            if name == "head":
                self.ns += 260 * MS

        self.driver.delay = delay
        self.ns += 100 * MS
        result = self.send()
        self.assertEqual(result["failure"], "match_intent_expired")
        self.assertEqual(self.driver.calls[-1], ("move", (0.0, 0.0, 0.0)))

    def test_limits_reject_instead_of_modifying_collision_checked_command(self):
        for kwargs in ({"velocity": (0.2, 0.2, 0.0)}, {"head": (0.45, 1.0, 0.5, 0.5)}):
            self.actuator = MatchActuator(self.driver, "test", clock=lambda: self.ns)
            self.assertFalse(self.actuator.accept(self.intent(**kwargs)))
            self.assertEqual(self.actuator.gate.failure, "actuator_limits_exceeded")

    def test_slow_reference_publication_cannot_enable_a_now_expired_kick(self):
        def delay(name):
            if name == "reference":
                self.ns += 260 * MS

        self.driver.delay = delay
        result = self.send(kick=True)
        self.assertEqual(result["failure"], "match_intent_expired")
        self.assertNotIn("enable", [c[0] for c in self.driver.calls])
        self.assertEqual(result["kick_status"], "failed")

    def test_sdk_exception_revokes_every_channel(self):
        self.driver.errors.add("reference")
        self.assertIn("reference failed", self.send(kick=True)["failure"])
        self.assertEqual(self.driver.calls[-3][0], "disable")

    def test_feedback_mapping_never_renews_a_cached_sample(self):
        mapper = SdkFeedback(wall_clock=lambda: self.ns)
        receipt = self.send()
        first = mapper.read(receipt, TimePoint("sim", 100 * MS))
        self.ns += 50 * MS
        again = mapper.read(receipt, TimePoint("sim", 200 * MS))
        self.assertEqual(first.at, again.at)
        self.ns += 101 * MS
        self.assertIsNone(mapper.read(receipt, TimePoint("sim", 200 * MS)))

    def test_feedback_mapping_rejects_clock_reset(self):
        mapper = SdkFeedback(wall_clock=lambda: self.ns)
        receipt = self.send()
        mapper.read(receipt, TimePoint("sim", 100 * MS))
        with self.assertRaises(ValueError):
            mapper.read(receipt, TimePoint("reset", 100 * MS))

    def test_mode_transition_never_blocks_expiry_or_enables_a_cancelled_kick(self):
        self.driver.ensure_mode = Mock(return_value=False)
        result = self.send(kick=True)
        self.assertEqual(result["reason"], "preparing_kick")
        self.assertNotIn("enable", [c[0] for c in self.driver.calls])
        self.ns += 250 * MS
        self.driver.refresh()
        self.driver.ensure_mode.return_value = True
        result = self.actuator.step()
        self.assertEqual(result["failure"], "match_intent_expired")
        self.assertEqual(result["kick_status"], "failed")
        self.assertNotIn("enable", [c[0] for c in self.driver.calls])

    def test_ordinary_cancellation_allows_a_new_sequence_but_does_not_rearm_old_kick(
        self,
    ):
        self.send(kick=True)
        self.actuator.stop(self.sequence)
        self.assertEqual(self.actuator.step()["kick_status"], "failed")
        self.assertEqual(self.send(kick=True)["kick_status"], "failed")
        self.assertEqual([c[0] for c in self.driver.calls].count("enable"), 1)
        self.send(kick=True, attempt="new")
        self.assertEqual([c[0] for c in self.driver.calls].count("enable"), 2)


class DriverMappingTest(unittest.TestCase):
    def test_native_stop_leaves_soccer_but_never_changes_mode_on_stale_or_fallen_data(
        self,
    ):
        driver = BoosterMatchDriver.__new__(BoosterMatchDriver)
        driver.clock = lambda: 2000 * MS
        driver.move, driver.ensure_mode = Mock(), Mock()
        driver.sample = Mock(
            return_value=SimpleNamespace(
                upright=True, observed_ns=2000 * MS, status_ns=1900 * MS
            )
        )
        driver.stop_body()
        driver.move.assert_called_with((0, 0, 0))
        driver.ensure_mode.assert_called_once_with(False)
        for changes in (
            {"upright": False},
            {"observed_ns": 1000 * MS},
            {"status_ns": 0},
        ):
            driver.ensure_mode.reset_mock()
            driver.sample.return_value = SimpleNamespace(
                **(
                    {"upright": True, "observed_ns": 2000 * MS, "status_ns": 1900 * MS}
                    | changes
                )
            )
            driver.stop_body()
            driver.ensure_mode.assert_not_called()

    def test_mode_ack_is_not_readiness_and_requests_have_a_timeout(self):
        driver = BoosterMatchDriver.__new__(BoosterMatchDriver)
        driver._mode_request = None
        driver.clock = Mock(return_value=MS)
        driver.sample = Mock(return_value=SimpleNamespace(mode=2))
        driver.move = Mock()
        driver._rpc = Mock()
        driver.sdk = SimpleNamespace(
            RobotMode=SimpleNamespace(kSoccer=4, kWalking=2),
            ChangeModeParameter=lambda x: x,
        )
        self.assertFalse(driver.ensure_mode(True))
        self.assertFalse(driver.ensure_mode(True))
        driver._rpc.assert_called_once_with("kChangeMode", 4)
        driver.clock.return_value = 4000 * MS
        with self.assertRaises(RuntimeError):
            driver.ensure_mode(True)
        driver.sample.return_value.mode = 4
        self.assertTrue(driver.ensure_mode(True))

    def test_rpc_uses_bounded_timeout_and_propagates_rejection(self):
        driver = BoosterMatchDriver.__new__(BoosterMatchDriver)
        driver.sdk = SimpleNamespace(LocoApiId=SimpleNamespace(kMove=9))
        driver.client = Mock()
        driver.client.SendApiRequest.return_value = 0
        parameter = Mock()
        parameter.to_json_str.return_value = "{}"
        driver._rpc("kMove", parameter)
        driver.client.SendApiRequest.assert_called_once_with(9, "{}", 20)
        driver.client.SendApiRequest.return_value = 501
        with self.assertRaises(RuntimeError):
            driver._rpc("kMove", parameter)

    def test_measured_k1_readiness_keeps_slow_status_age_and_checks_fast_tilt(self):
        driver = BoosterMatchDriver.__new__(BoosterMatchDriver)
        driver._lock = Lock()
        driver.clock = lambda: 1000 * MS
        driver._fall, driver._state, driver._phase = (
            (100 * MS, True),
            (900 * MS, 2, 12),
            (0, 800 * MS),
        )
        message = SimpleNamespace(
            motor_state_serial=[SimpleNamespace(q=0.1), SimpleNamespace(q=0.4)],
            imu_state=SimpleNamespace(rpy=[0.0, 0.0, 0.5]),
        )
        driver._on_low(message)
        sample = driver.sample()
        self.assertEqual((sample.observed_ns, sample.status_ns), (1000 * MS, 100 * MS))
        self.assertTrue(sample.ready and sample.upright)
        self.assertEqual(sample.head, (0.4, 0.1))
        message.imu_state.rpy[0] = 0.9
        driver._on_low(message)
        self.assertFalse(driver.sample().upright)
        driver._state = (900 * MS, 4, 5)  # T1 enum values are not a K1 profile.
        self.assertFalse(driver.sample().ready)

    def test_body_ball_and_aim_do_not_read_a_second_pose(self):
        driver = BoosterMatchDriver.__new__(BoosterMatchDriver)
        driver.sdk = SimpleNamespace(
            Kick=SimpleNamespace, Header=SimpleNamespace, Time=SimpleNamespace
        )
        driver.publisher = Mock()
        driver.publisher.Write.return_value = True
        driver.reference((0.0, 2.0, 0.7, -0.1))
        value = driver.publisher.Write.call_args.args[0]
        self.assertEqual(
            (value.x, value.y, value.goal_x, value.goal_y), (0.7, -0.1, 8.7, -0.1)
        )
        self.assertEqual(
            (value.power, value.dir, value.robot_theta_to_field), (2.0, 0.0, 0.0)
        )
        driver.publisher.Write.return_value = False
        with self.assertRaises(RuntimeError):
            driver.reference((0.0, 1.0, 0.6, 0.0))

    def test_timeout_keeps_disable_required_and_uses_k1_v2(self):
        driver = BoosterMatchDriver.__new__(BoosterMatchDriver)
        driver.sdk = SimpleNamespace(
            VisualKickVersion=SimpleNamespace(kV2="v2"),
            VisualKickParameter=lambda *args: args,
        )
        driver._armed = False
        driver._rpc = Mock(side_effect=RuntimeError("timeout"))
        driver.sample = lambda: None
        with self.assertRaises(RuntimeError):
            driver.enable_kick()
        self.assertTrue(driver._armed)
        driver._rpc.side_effect = None
        driver.disable_kick()
        driver._rpc.assert_called_with("kVisualKick", (False, "v2"))
        self.assertFalse(driver._armed)


class RecoveryActuatorTest(unittest.TestCase):
    def setUp(self):
        self.ns = 1_000_000_000
        self.driver = Driver(lambda: self.ns)
        self.driver.recover = lambda attempt: self.driver.call("recover", attempt)
        self.driver.cancel_recovery = lambda: self.driver.call("cancel_recovery")
        self.driver.refresh(upright=False, ready=False, recovery_available=True)
        self.actuator = MatchActuator(self.driver, "recovery", clock=lambda: self.ns)
        self.intent = MatchIntent(
            "recovery",
            0,
            self.ns,
            self.ns + 250 * MS,
            (0, 0, 0),
            (0.45, 0, 1.2, 1.2),
            None,
            None,
            "get-up-1",
        )

    def test_recovery_schema_round_trip_and_exclusive_control(self):
        self.assertEqual(self.intent.message()["schema"], "runswift-match/2")
        self.assertEqual(MatchIntent.parse(self.intent.message()), self.intent)
        for changes in (
            {"velocity": (0.1, 0, 0)},
            {"kick": (0, 1, 0.5, 0), "kick_attempt_id": "kick"},
        ):
            with self.assertRaises(ValueError):
                replace(self.intent, **changes)

    def test_one_recovery_request_is_held_and_expiry_revokes_it(self):
        self.assertTrue(self.actuator.accept(self.intent))
        self.assertEqual(self.actuator.step()["reason"], "recovering")
        self.ns += 50 * MS
        self.driver.refresh()
        self.actuator.step()
        self.assertEqual(
            [call for call in self.driver.calls if call[0] == "recover"],
            [("recover", "get-up-1")],
        )
        self.ns += 201 * MS
        self.driver.refresh()
        result = self.actuator.step()
        self.assertEqual(result["failure"], "match_intent_expired")
        self.assertIn(("cancel_recovery", None), self.driver.calls)
        self.assertIn(("move", (0, 0, 0)), self.driver.calls)

    def test_cancel_fences_recovery_and_a_completion_does_not_restart_it(self):
        self.actuator.accept(self.intent)
        self.actuator.step()
        self.driver.refresh(recovery_attempt_id="get-up-1", recovery_status="completed")
        self.assertEqual(self.actuator.step()["reason"], "recovery_finished")
        self.driver.refresh(recovery_status="idle")
        self.actuator.step()
        self.assertEqual(sum(name == "recover" for name, _ in self.driver.calls), 1)
        self.actuator.stop(0)
        self.actuator.step()
        self.assertIsNone(self.actuator.gate.intent)

    def test_unadvertised_capability_and_stale_motion_feedback_never_recover(self):
        self.driver.refresh(recovery_available=False)
        self.actuator.accept(self.intent)
        result = self.actuator.step()
        self.assertIsNotNone(result["failure"])
        self.assertFalse(any(name == "recover" for name, _ in self.driver.calls))

    def test_failed_cancel_attempts_other_stop_operations_and_retries(self):
        self.actuator.accept(self.intent)
        self.actuator.step()
        self.driver.errors.add("cancel_recovery")
        self.actuator.stop(0)
        self.actuator.step()
        self.assertTrue(self.actuator.stop_errors)
        self.assertIn(("move", (0, 0, 0)), self.driver.calls)
        self.driver.errors.clear()
        self.actuator.step()
        self.assertEqual(self.actuator.stop_errors, [])

    def test_slow_start_cannot_outlive_lease_and_sdk_mapping_preserves_attempt(self):
        self.driver.delay = lambda name: (
            setattr(self, "ns", self.ns + 300 * MS) if name == "recover" else None
        )
        self.actuator.accept(self.intent)
        result = self.actuator.step()
        self.assertEqual(result["failure"], "match_intent_expired")
        self.assertIn(("cancel_recovery", None), self.driver.calls)
        self.driver.refresh(recovery_attempt_id="get-up-1", recovery_status="running")
        result = self.actuator.step()
        mapping = SdkFeedback(wall_clock=lambda: self.ns)
        feedback = mapping.read(result, TimePoint("decision", 0))
        self.assertTrue(feedback.recovery_available)
        self.assertEqual(feedback.recovery_attempt_id, "get-up-1")


if __name__ == "__main__":
    unittest.main()

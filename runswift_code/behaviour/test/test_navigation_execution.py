"""Navigation lifetime and motion deadlines, using the real model and skill."""

import sys
import unittest
from dataclasses import replace
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from action.velocity_lease import ZERO, VelocityLease, VelocityLeaseGate
from navigation_execution import NavigationExecutive
from skills.world import NavigateToPose, NavigateToPoseGoal, NavigationPolicy
from world_model.adapters.booster import Frame, Robot, make_config
from world_model_ros import RosSession
from world_model_ros.booster import BoosterBatchBuilder

from world_model import types as wm

MS = 1_000_000


class LeaseTest(unittest.TestCase):
    def lease(
        self,
        sequence=0,
        issued=0,
        command=250 * MS,
        observation=350 * MS,
        velocity=(0.1, 0.0, 0.0),
    ):
        return VelocityLease(
            "test", sequence, issued, command, observation, velocity
        ).message()

    def test_sender_silence_expires_without_another_message_and_cannot_auto_resume(
        self,
    ):
        gate = VelocityLeaseGate("test")
        self.assertTrue(gate.accept(self.lease(), 0))
        self.assertEqual(gate.velocity(249 * MS), (0.1, 0.0, 0.0))
        self.assertEqual(gate.velocity(250 * MS), ZERO)
        self.assertEqual(gate.reason, "command_expired")
        self.assertFalse(
            gate.accept(self.lease(1, 250 * MS, 500 * MS, 600 * MS), 250 * MS)
        )
        self.assertEqual(gate.velocity(251 * MS), ZERO)

    def test_fresh_commands_cannot_extend_old_observations(self):
        gate = VelocityLeaseGate("test")
        gate.accept(self.lease(), 0)
        gate.accept(self.lease(1, 200 * MS, 450 * MS, 350 * MS), 200 * MS)
        self.assertEqual(gate.velocity(350 * MS), ZERO)
        self.assertEqual(gate.reason, "observation_expired")

    def test_new_arrival_cannot_hide_a_missed_deadline(self):
        gate = VelocityLeaseGate("test")
        gate.accept(self.lease(), 0)
        self.assertFalse(
            gate.accept(self.lease(1, 300 * MS, 550 * MS, 650 * MS), 300 * MS)
        )
        self.assertEqual(gate.reason, "command_expired")

    def test_cancellation_revokes_immediately_and_allows_explicit_new_goal(self):
        gate = VelocityLeaseGate("test")
        gate.accept(self.lease(), 0)
        self.assertTrue(
            gate.accept(self.lease(1, 100 * MS, 100 * MS, 0, ZERO), 100 * MS)
        )
        self.assertEqual(gate.velocity(400 * MS), ZERO)
        self.assertIsNone(gate.failure)
        self.assertTrue(
            gate.accept(self.lease(2, 400 * MS, 650 * MS, 750 * MS), 400 * MS)
        )

    def test_invalid_commands_stop_instead_of_clipping_or_restamping(self):
        cases = [
            {"velocity": (0.2, 0.2, 0)},
            {"velocity": (float("nan"), 0, 0)},
            {"velocity": (0, 0, 0.81)},
            {"velocity": (True, 0, 0)},
            {"issued": 1},
            {"command": 251 * MS},
            {"observation": 351 * MS},
        ]
        for changes in cases:
            with self.subTest(changes=changes):
                gate = VelocityLeaseGate("test")
                self.assertFalse(gate.accept(self.lease(**changes), 0))
                self.assertEqual(gate.velocity(0), ZERO)
        for key, value in (
            ("sequence", -1),
            ("session", "other"),
            ("schema", "future"),
        ):
            gate = VelocityLeaseGate("test")
            message = self.lease()
            message[key] = value
            self.assertFalse(gate.accept(message, 0))

    def test_buffered_and_reordered_commands_do_not_renew_motion(self):
        gate = VelocityLeaseGate("test")
        self.assertFalse(gate.accept(self.lease(), 251 * MS))
        gate = VelocityLeaseGate("test")
        gate.accept(self.lease(), 0)
        self.assertFalse(gate.accept(self.lease(), MS))
        self.assertEqual(gate.velocity(MS), ZERO)


class GateMotion:
    """Test transport: preserves exactly the same absolute lease deadlines."""

    def __init__(self, wall):
        self.wall = wall
        self.gate = VelocityLeaseGate("test")
        self.sequence = -1

    def send(self, velocity, observation_until_ns):
        self.sequence += 1
        now = self.wall()
        message = VelocityLease(
            "test", self.sequence, now, now + 250 * MS, observation_until_ns, velocity
        ).message()
        if not self.gate.accept(message, now):
            raise RuntimeError(self.gate.reason)

    def stop(self):
        # A terminally expired relay is already stopped and rejects renewal.
        if not self.gate.failure:
            self.send(ZERO, self.wall())


class ExecutiveTest(unittest.TestCase):
    def setUp(self):
        self.wall = 0
        self.config = make_config("execution-test")
        self.session = RosSession(
            self.config, "execution-test", wall_clock=lambda: self.wall
        )
        self.builder = BoosterBatchBuilder(
            "execution-test", robot="robot1", radii={"robot2": 0.45}
        )
        self.skill = NavigateToPose(
            navigation_policy=NavigationPolicy(unknown_space="allow_unknown")
        )
        self.motion = GateMotion(lambda: self.wall)
        self.executive = NavigationExecutive(
            self.skill, self.motion, wall_clock=lambda: self.wall
        )
        self.goal = NavigateToPoseGoal(
            wm.FramedPose2(self.config.field.frame, wm.Pose2(-0.5, 0, 0))
        )
        self.executive.start(self.goal)
        self.sequence = -1

    def publish(self, x=-2.0):
        self.sequence += 1
        frame = Frame(
            self.wall + MS,
            self.sequence,
            (
                Robot("robot1", (x, 0.0, 0.7), 0.0, 1.0),
                Robot("robot2", (0.0, 2.5, 0.7), 0.0, 1.0),
            ),
            (0.0, 0.0, 0.11),
        )
        self.session.observe_clock(frame.ns)
        self.assertTrue(self.session.enqueue(self.builder.build(frame)))
        self.session.update()
        return self.session.context_with_receipt(self.sequence)

    def test_measured_movement_reaches_goal_then_stops_and_discards_path(self):
        x = -2.0
        # A simple plant closes the Python loop; live SDK/physics scenarios are
        # separately exercised by the Booster runner, not claimed by this test.
        for _ in range(120):
            result = self.executive.tick(*self.publish(x))
            if result.status == "succeeded":
                break
            self.assertEqual(result.status, "running", result.reason)
            vx, vy, turn = self.motion.gate.velocity(self.wall)
            self.assertAlmostEqual(vy, 0.0)
            self.assertAlmostEqual(turn, 0.0)
            x += vx * 0.1
            self.wall += 100 * MS
        self.assertEqual(result.status, "succeeded")
        self.assertLess(abs(x - self.goal.target.pose.x), 0.3)
        self.assertEqual(self.motion.gate.velocity(self.wall), ZERO)
        self.assertIsNone(self.skill.debug.path)

    def test_cancel_and_goal_replacement_discard_state_and_stop_without_a_tick(self):
        context = self.publish()
        self.executive.tick(*context)
        self.assertIsNotNone(self.skill.debug.path)
        self.executive.cancel()
        self.assertIsNone(self.skill.debug.path)
        self.assertEqual(self.motion.gate.velocity(self.wall), ZERO)
        self.assertEqual(self.executive.tick(*context).reason, "cancelled")
        self.executive.start(replace(self.goal, distance_tolerance=0.4))
        self.assertEqual(self.motion.gate.velocity(self.wall), ZERO)
        self.assertIsNone(self.skill.debug.path)
        self.assertEqual(self.executive.tick(*context).status, "running")

    def test_frozen_simulation_and_repeated_reads_do_not_renew_observations(self):
        context = self.publish()
        self.executive.tick(*context)
        self.wall = 200 * MS
        self.executive.tick(*self.session.context_with_receipt())
        self.wall = 350 * MS
        self.assertEqual(self.motion.gate.velocity(self.wall), ZERO)
        result = self.executive.tick(*self.session.context_with_receipt())
        self.assertEqual(result.reason, "observations_expired")
        self.assertIsNone(self.skill.debug.path)

    def test_executor_stall_stops_while_observations_continue(self):
        self.executive.tick(*self.publish())
        self.wall = 250 * MS
        self.publish(-1.98)  # Owner still runs independently of navigation.
        self.assertEqual(self.motion.gate.velocity(self.wall), ZERO)
        self.assertEqual(self.motion.gate.reason, "command_expired")

    def test_slow_planning_cannot_stamp_an_old_decision_as_fresh(self):
        tick = self.skill.tick

        def slow(*args):
            result = tick(*args)
            self.wall += 350 * MS
            return result

        self.skill.tick = slow
        result = self.executive.tick(*self.publish())
        self.assertEqual(result.reason, "observations_expired")
        self.assertEqual(self.motion.gate.velocity(self.wall), ZERO)
        self.assertIsNone(self.skill.debug.path)

    def test_unavailable_inputs_stop_with_reason(self):
        result = self.executive.tick(*self.session.context_with_receipt())
        self.assertEqual(result.reason, "observations_expired")
        self.assertEqual(self.motion.gate.velocity(self.wall), ZERO)

    def test_broken_motion_transport_discards_goal_and_cache(self):
        context = self.publish()
        self.executive.tick(*context)

        def broken(*_):
            raise BrokenPipeError("closed")

        self.motion.send = broken
        with self.assertRaises(BrokenPipeError):
            self.executive.tick(*context)
        self.assertIsNone(self.executive.goal)
        self.assertIsNone(self.skill.debug.path)
        self.assertEqual(self.executive.result.reason, "motion_transport_failed")
        self.wall = 250 * MS
        self.assertEqual(self.motion.gate.velocity(self.wall), ZERO)

    def test_resuming_after_a_missed_command_deadline_requires_a_new_session(self):
        self.executive.tick(*self.publish())
        self.wall = 250 * MS
        self.assertEqual(self.motion.gate.velocity(self.wall), ZERO)
        with self.assertRaisesRegex(RuntimeError, "command_expired"):
            self.executive.tick(*self.publish(-1.98))
        self.assertIsNone(self.executive.goal)
        self.assertIsNone(self.skill.debug.path)
        self.assertEqual(self.executive.result.reason, "motion_transport_failed")


if __name__ == "__main__":
    unittest.main()

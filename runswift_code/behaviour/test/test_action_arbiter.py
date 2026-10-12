#!/usr/bin/env python3
from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from action.arbiter import ActionArbiter  # noqa: E402
from action.head_controller import HeadController  # noqa: E402
from action.types import ArbiterInput, HeadLimits, MotionCommand, VelocityLimits  # noqa: E402
from skills.base import Point2, Pose2  # noqa: E402
from skills.visual_kick import VisualKickRequest, visual_kick_reference  # noqa: E402
from skills.walk_in_circle import WalkInCircleRequest, walk_in_circle_velocity  # noqa: E402

LIMITS = VelocityLimits(vx=2.2, vy=1.9, vtheta=1.3)
HEAD_LIMITS = HeadLimits(pitch_min=0.46, pitch_max=0.74, yaw_min=-1.02, yaw_max=1.02)


class FakeAdapter:
    def __init__(self) -> None:
        self.calls: list[tuple] = []
        self.move_error: Exception | None = None

    def move(self, x: float, y: float, theta: float) -> None:
        if self.move_error is not None:
            raise self.move_error
        self.calls.append(("move", x, y, theta))

    def get_up(self) -> None:
        self.calls.append(("get_up",))

    def rotate_head(self, pitch: float, yaw: float) -> None:
        self.calls.append(("rotate_head", pitch, yaw))

    def visual_kick(self, enable: bool = True) -> None:
        self.calls.append(("visual_kick", enable))

    def update_kick_command(self, direction: float, power: float) -> None:
        self.calls.append(("update_kick_command", direction, power))

    def update_kick_ball(self, x: float, y: float) -> None:
        self.calls.append(("update_kick_ball", x, y))

    def enter_walk(self) -> None:
        self.calls.append(("enter_walk",))

    def ensure_soccer_mode(self, timeout_sec: float = 3.0) -> None:
        self.calls.append(("ensure_soccer_mode", timeout_sec))

    def reset_odom(self) -> None:
        self.calls.append(("reset_odom",))

    def play_action(self, action_id: str | None) -> None:
        self.calls.append(("play_action", action_id))

    def action_running(self) -> bool:
        return False


def _arbiter(adapter: FakeAdapter | None = None) -> tuple[ActionArbiter, FakeAdapter]:
    adapter = adapter or FakeAdapter()
    return ActionArbiter(adapter, LIMITS), adapter


class RecoverBeatsWalkTest(unittest.TestCase):
    def test_fallen_recovery_sends_get_up_not_walk(self) -> None:
        arbiter, adapter = _arbiter()
        command = MotionCommand()
        command.set_body(1.0, 0.2, 0.1)
        result = arbiter.execute(
            command,
            ArbiterInput(
                has_fallen=True,
                recovery_available=True,
                is_stopped=False,
            ),
        )
        self.assertEqual(adapter.calls, [("get_up",)])
        self.assertTrue(result.recovered)
        self.assertEqual(result.reason, "recover")
        self.assertFalse(result.body_move_sent)
        self.assertIsNone(result.published_cmd)
        self.assertEqual((command.x, command.y, command.theta), (1.0, 0.2, 0.1))

    def test_fallen_while_stopped_does_not_recover(self) -> None:
        arbiter, adapter = _arbiter()
        command = MotionCommand()
        command.set_body(0.5, 0.0, 0.0)
        result = arbiter.execute(
            command,
            ArbiterInput(
                has_fallen=True,
                recovery_available=True,
                is_stopped=True,
            ),
        )
        self.assertEqual(adapter.calls, [("move", 0.5, 0.0, 0.0)])
        self.assertEqual(result.reason, "walk")
        self.assertFalse(result.recovered)


class StopOverridesWalkTest(unittest.TestCase):
    def test_force_stop_sends_zero_and_skips_clip_walk(self) -> None:
        arbiter, adapter = _arbiter()
        command = MotionCommand()
        command.set_body(1.5, 0.4, 0.2)
        result = arbiter.execute(command, ArbiterInput(force_stop=True))
        self.assertEqual(adapter.calls, [("move", 0.0, 0.0, 0.0)])
        self.assertEqual(result.reason, "stop")
        self.assertEqual(result.published_cmd, (0.0, 0.0, 0.0))

    def test_penalised_sends_stop(self) -> None:
        arbiter, adapter = _arbiter()
        command = MotionCommand()
        command.set_body(1.0, 0.0, 0.0)
        result = arbiter.execute(command, ArbiterInput(is_penalised=True))
        self.assertEqual(adapter.calls, [("move", 0.0, 0.0, 0.0)])
        self.assertEqual(result.reason, "stop")


class KickSuppressTest(unittest.TestCase):
    def test_suppress_body_does_not_send_walk(self) -> None:
        arbiter, adapter = _arbiter()
        command = MotionCommand()
        command.set_body(0.8, 0.1, 0.0)
        result = arbiter.execute(command, ArbiterInput(suppress_body=True))
        self.assertEqual(adapter.calls, [])
        self.assertEqual(result.reason, "suppress")
        self.assertFalse(result.body_move_sent)
        self.assertEqual(result.published_cmd, (0.0, 0.0, 0.0))
        self.assertLessEqual(abs(command.x), LIMITS.vx)

    def test_kick_fields_update_adapter_during_suppress(self) -> None:
        arbiter, adapter = _arbiter()
        command = MotionCommand()
        command.set_kick(0.2, 2.5, 0.4, -0.1)
        result = arbiter.execute(command, ArbiterInput(suppress_body=True))
        self.assertEqual(result.reason, "suppress")
        self.assertFalse(result.body_move_sent)
        self.assertEqual(
            adapter.calls,
            [
                ("update_kick_command", 0.2, 2.5),
                ("update_kick_ball", 0.4, -0.1),
            ],
        )

    def test_request_stop_now_still_sends_during_kick_hold(self) -> None:
        arbiter, adapter = _arbiter()
        arbiter.request_stop_now()
        command = MotionCommand()
        command.set_body(0.8, 0.0, 0.0)
        result = arbiter.execute(command, ArbiterInput(suppress_body=True))
        self.assertEqual(adapter.calls, [("move", 0.0, 0.0, 0.0)])
        self.assertEqual(result.reason, "suppress")


class SetSkipBodyTest(unittest.TestCase):
    def test_set_clips_but_does_not_send(self) -> None:
        arbiter, adapter = _arbiter()
        command = MotionCommand()
        command.set_body(3.0, 0.0, 0.0)
        result = arbiter.execute(command, ArbiterInput(skip_body=True))
        self.assertEqual(adapter.calls, [])
        self.assertEqual(result.reason, "skip")
        self.assertIsNone(result.published_cmd)
        self.assertAlmostEqual(command.x, LIMITS.vx)


class VelocityClipTest(unittest.TestCase):
    def test_forward_speed_saturates_and_scales_strafe(self) -> None:
        arbiter, adapter = _arbiter()
        command = MotionCommand()
        command.set_body(3.0, 1.2, 2.0)
        result = arbiter.execute(command, ArbiterInput())
        self.assertEqual(result.reason, "walk")
        self.assertTrue(result.body_move_sent)
        sent = adapter.calls[-1]
        self.assertEqual(sent[0], "move")
        self.assertAlmostEqual(sent[1], LIMITS.vx)
        self.assertAlmostEqual(sent[2], 1.2 * (LIMITS.vx / 3.0))
        self.assertAlmostEqual(sent[3], LIMITS.vtheta)
        self.assertEqual(result.published_cmd, (sent[1], sent[2], sent[3]))

    def test_zero_x_still_clips_y(self) -> None:
        arbiter, adapter = _arbiter()
        command = MotionCommand()
        command.set_body(0.0, 5.0, 0.0)
        arbiter.execute(command, ArbiterInput())
        self.assertEqual(adapter.calls[-1], ("move", 0.0, LIMITS.vy, 0.0))

    def test_walk_move_failure_does_not_claim_sent(self) -> None:
        adapter = FakeAdapter()
        adapter.move_error = RuntimeError("sdk down")
        arbiter, _ = _arbiter(adapter)
        command = MotionCommand()
        command.set_body(0.4, 0.0, 0.0)
        result = arbiter.execute(command, ArbiterInput())
        self.assertFalse(result.body_move_sent)
        self.assertEqual(result.reason, "walk")
        self.assertEqual(result.published_cmd, (0.4, 0.0, 0.0))


class ImmediateRequestTest(unittest.TestCase):
    def test_visual_kick_goes_to_adapter(self) -> None:
        arbiter, adapter = _arbiter()
        arbiter.request_visual_kick(True)
        self.assertEqual(adapter.calls, [("visual_kick", True)])

    def test_kick_updates_go_to_adapter(self) -> None:
        arbiter, adapter = _arbiter()
        arbiter.update_kick_command(0.2, 2.5)
        arbiter.update_kick_ball(0.4, -0.1)
        self.assertEqual(
            adapter.calls,
            [("update_kick_command", 0.2, 2.5), ("update_kick_ball", 0.4, -0.1)],
        )

    def test_reset_odom_goes_to_adapter(self) -> None:
        arbiter, adapter = _arbiter()
        arbiter.reset_odom()
        self.assertEqual(adapter.calls, [("reset_odom",)])

    def test_play_action_goes_to_adapter(self) -> None:
        arbiter, adapter = _arbiter()
        arbiter.request_action("hand_wave")
        arbiter.request_action("cheer")
        arbiter.request_action(None)
        self.assertEqual(
            adapter.calls,
            [
                ("play_action", "hand_wave"),
                ("play_action", "cheer"),
                ("play_action", None),
            ],
        )


class WalkInCircleTest(unittest.TestCase):
    def test_on_circle_facing_tangent_walks_forward(self) -> None:
        request = WalkInCircleRequest(
            robot_pose=Pose2(0.0, 0.0, -1.5708),
            centre=Point2(1.0, 0.0),
            radius=1.0,
            speed=0.30,
            kp_yaw=0.0,
        )
        vx, vy, vtheta = walk_in_circle_velocity(request)
        self.assertGreater(vx, 0.2)
        self.assertAlmostEqual(vy, 0.0, places=2)
        self.assertGreater(vtheta, 0.0)


class VisualKickTest(unittest.TestCase):
    def test_origin_kick_is_forward_with_ball_ahead(self) -> None:
        request = VisualKickRequest(
            robot_pose=Pose2(0.0, 0.0, 0.0),
            ball=Point2(1.0, 0.0),
            target=Point2(5.0, 0.0),
            power=2.5,
        )
        ref = visual_kick_reference(request)
        self.assertAlmostEqual(ref.direction, 0.0, places=3)
        self.assertAlmostEqual(ref.ball_x, 1.0, places=3)
        self.assertAlmostEqual(ref.ball_y, 0.0, places=3)
        self.assertEqual(ref.power, 2.5)


class HeadControllerTest(unittest.TestCase):
    def test_suppressed_does_not_rotate(self) -> None:
        command = MotionCommand()
        command.set_head(0.7, 0.5)
        rotated: list[tuple[float, float]] = []
        head = HeadController(
            command,
            rotate_head=lambda p, y: rotated.append((p, y)),
            read_pose=lambda: (0.5, 0.0),
            suppressed=lambda: True,
            frequency=50.0,
            limits=HEAD_LIMITS,
        )
        head.step(0.02)
        self.assertEqual(rotated, [])

    def test_steps_toward_target_within_limits(self) -> None:
        command = MotionCommand()
        command.set_head(0.74, 0.4, speed_pitch=1.0, speed_yaw=1.0)
        rotated: list[tuple[float, float]] = []
        head = HeadController(
            command,
            rotate_head=lambda p, y: rotated.append((p, y)),
            read_pose=lambda: (0.50, 0.0),
            suppressed=lambda: False,
            frequency=50.0,
            limits=HEAD_LIMITS,
        )
        head.step(0.02)
        self.assertEqual(len(rotated), 1)
        pitch, yaw = rotated[0]
        self.assertGreater(pitch, 0.50)
        self.assertLessEqual(pitch, HEAD_LIMITS.pitch_max)
        self.assertGreater(yaw, 0.0)
        self.assertLessEqual(yaw, HEAD_LIMITS.yaw_max)


class IsolationTest(unittest.TestCase):
    def test_chase_script_does_not_call_vendor_client(self) -> None:
        source = (SCRIPTS / "ball_chasing_wm_simplified.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        banned_names = {
            "B1LocoClient",
            "ChannelFactory",
            "RobotMode",
            "VisualKickVersion",
            "GaitType",
            "GetModeResponse",
            "BodyControl",
            "SoccerKickManager",
            "BoosterRobot",
        }
        hits: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in banned_names:
                hits.append(f"{node.id}:{node.lineno}")
            if isinstance(node, ast.Attribute) and node.attr == "client":
                hits.append(f".client:{node.lineno}")
        self.assertEqual(hits, [])

    def test_arbiter_does_not_import_sdk(self) -> None:
        source = (SCRIPTS / "action" / "arbiter.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertFalse(alias.name.startswith("booster_robotics_sdk"))
                    self.assertFalse(alias.name.startswith("boosteros"))
            if isinstance(node, ast.ImportFrom) and node.module:
                self.assertFalse(node.module.startswith("booster_robotics_sdk"))
                self.assertFalse(node.module.startswith("boosteros"))

    def test_vendor_client_lives_only_in_adapter(self) -> None:
        action_dir = SCRIPTS / "action"
        offenders: list[str] = []
        for path in action_dir.glob("*.py"):
            if path.name in ("booster_adapter.py", "booster_adapter_old_sdk.py"):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id == "B1LocoClient":
                    offenders.append(f"{path.name}:{node.lineno}")
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()

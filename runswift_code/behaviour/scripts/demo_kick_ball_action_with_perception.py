#!/usr/bin/env python3
"""Demo: visual kick using /booster_vision/detection, no world-model chase.

Sequence: reset odom, look down, wait for a ball, kick toward (5, 0) in odom.
Enter repeats the sequence. k / lost ball / ball too far / hold timer stop it.

  ros2 run behaviour demo_kick_ball_action_with_perception.py
"""
from __future__ import annotations

import select
import sys
import termios
import threading
import time
import tty
from math import atan2, cos, hypot, sin

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, String
from vision_interface.msg import Detections

from action.arbiter import ActionArbiter
from action.booster_adapter import create_booster_adapter
from action.config import ALWAYS_SOCCER
from action.types import ArbiterInput, MotionCommand, VelocityLimits
from skills.base import Point2, Pose2, SkillStatus
from skills.visual_kick import VisualKick, VisualKickRequest

ODOM_TOPIC = "/odom"
DETECTION_TOPIC = "/booster_vision/detection"
FREQUENCY_HZ = 30.0
ODOM_RESET_READY_M = 0.35
TARGET_ODOM = Pose2(5.0, 0.0, 0.0)
KICK_POWER = 1.5
KICK_HOLD_SEC = 3.0
HEAD_PITCH = 0.74
HEAD_YAW = 0.0
BALL_LABELS = ("Ball", "ball")
BALL_LOST_SEC = 0.4
BALL_FAR_M = 2.0
MIN_CONFIDENCE = 0.0


def yaw_from_quaternion(x: float, y: float, z: float, w: float) -> float:
    return atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


def _rel_to_odom(pose: Pose2, rel_x: float, rel_y: float) -> Pose2:
    return Pose2(
        x=pose.x + rel_x * cos(pose.theta) - rel_y * sin(pose.theta),
        y=pose.y + rel_x * sin(pose.theta) + rel_y * cos(pose.theta),
        theta=0.0,
    )


class PerceptionKickDemo(Node):
    """Reset, look down, wait for a vision ball, then VisualKick toward odom (5, 0)."""

    def __init__(self, arbiter: ActionArbiter) -> None:
        super().__init__("demo_kick_ball_action_with_perception")
        self.arbiter = arbiter
        self.command = MotionCommand()
        self.kick_skill = VisualKick()
        self._kick_request: VisualKickRequest | None = None
        self._phase = "wait_odom"
        self._pose: Pose2 | None = None
        self._kick_lock = threading.Lock()
        self._kick_requested = False
        self._stop_requested = False
        self._run_after_reset = True
        self._ball_lock = threading.Lock()
        self._ball_rel: tuple[float, float] | None = None
        self._ball_seen_at: float | None = None

        self._state_pub = self.create_publisher(String, "/behaviour/state", 2)
        self._cmd_pub = self.create_publisher(Float32MultiArray, "/behaviour/cmd_vel", 2)
        self.create_subscription(Odometry, ODOM_TOPIC, self._on_odom, 10)
        self.create_subscription(Detections, DETECTION_TOPIC, self._on_detections, 10)
        self.create_timer(1.0 / FREQUENCY_HZ, self._on_timer)
        self.get_logger().info(
            f"Perception kick demo: target=({TARGET_ODOM.x:.1f}, {TARGET_ODOM.y:.1f}) "
            f"power={KICK_POWER} hold={KICK_HOLD_SEC:.1f}s far={BALL_FAR_M:.1f}m "
            f"detections={DETECTION_TOPIC}"
        )
        print(
            "Enter = reset odom, look down, wait for ball, kick. "
            "k = stop. Ctrl-C = quit.",
            flush=True,
        )

    def request_kick(self) -> None:
        with self._kick_lock:
            self._kick_requested = True

    def request_stop(self) -> None:
        with self._kick_lock:
            self._stop_requested = True

    def _consume_kick_request(self) -> bool:
        with self._kick_lock:
            requested = self._kick_requested
            self._kick_requested = False
            return requested

    def _consume_stop_request(self) -> bool:
        with self._kick_lock:
            requested = self._stop_requested
            self._stop_requested = False
            return requested

    def _on_odom(self, msg: Odometry) -> None:
        pose = msg.pose.pose
        yaw = yaw_from_quaternion(
            pose.orientation.x,
            pose.orientation.y,
            pose.orientation.z,
            pose.orientation.w,
        )
        self._pose = Pose2(float(pose.position.x), float(pose.position.y), yaw)

    def _on_detections(self, msg: Detections) -> None:
        best: tuple[float, float, float] | None = None
        for obj in msg.detected_objects:
            if obj.label not in BALL_LABELS:
                continue
            if obj.confidence < MIN_CONFIDENCE or len(obj.position_projection) < 2:
                continue
            if best is None or obj.confidence > best[2]:
                best = (
                    float(obj.position_projection[0]),
                    float(obj.position_projection[1]),
                    float(obj.confidence),
                )
        with self._ball_lock:
            if best is None:
                return
            self._ball_rel = (best[0], best[1])
            self._ball_seen_at = time.monotonic()

    def _ball_rel_fresh(self) -> tuple[float, float] | None:
        with self._ball_lock:
            if self._ball_rel is None or self._ball_seen_at is None:
                return None
            if time.monotonic() - self._ball_seen_at > BALL_LOST_SEC:
                return None
            return self._ball_rel

    def _look_down(self) -> None:
        self.command.set_head(HEAD_PITCH, HEAD_YAW)
        self.arbiter.request_look(HEAD_PITCH, HEAD_YAW)

    def _arm_sequence(self) -> None:
        if self._phase == "kick":
            self._stop_kick("redo")
        self.arbiter.reset_odom()
        self._pose = None
        self._run_after_reset = True
        self._phase = "wait_odom"
        self.get_logger().info("Odom reset; look down, then wait for ball")

    def _start_kick(self, ball_odom: Pose2) -> None:
        pose = self._pose
        self._kick_request = VisualKickRequest(
            robot_pose=Pose2(0.0, 0.0, 0.0) if pose is None else pose,
            ball=Point2(ball_odom.x, ball_odom.y),
            target=Point2(TARGET_ODOM.x, TARGET_ODOM.y),
            power=KICK_POWER,
            duration_sec=KICK_HOLD_SEC,
        )
        self.kick_skill.on_enter(self._kick_request)
        self.arbiter.request_stop_now()
        self.arbiter.request_visual_kick(True)
        self._phase = "kick"
        self.get_logger().info(
            f"Skill -> VisualKick ball_odom=({ball_odom.x:.2f}, {ball_odom.y:.2f})"
        )

    def _stop_kick(self, reason: str) -> None:
        self.kick_skill.on_exit()
        self._kick_request = None
        self.arbiter.request_visual_kick(False)
        self.arbiter.request_stop_now()
        self._phase = "idle"
        self.get_logger().info(f"Kick stopped ({reason}); Enter to redo")

    def _send_kick_reference(self) -> None:
        ref = self.kick_skill.reference
        if ref is None:
            return
        self.arbiter.update_kick_command(ref.direction, ref.power)
        self.arbiter.update_kick_ball(ref.ball_x, ref.ball_y)

    def _on_timer(self) -> None:
        self.command.reset()
        self._look_down()
        pose = self._pose
        if self._consume_stop_request():
            self._run_after_reset = False
            if self._phase in ("kick", "wait_odom", "wait_ball"):
                self._stop_kick("key")
        elif self._consume_kick_request():
            self._arm_sequence()
            pose = self._pose

        if pose is None or self._phase == "wait_odom":
            if pose is not None and hypot(pose.x, pose.y) <= ODOM_RESET_READY_M:
                if self._run_after_reset:
                    self._phase = "wait_ball"
                    self.get_logger().info("Looking down; waiting for a ball")
                else:
                    self._phase = "idle"
            if self._phase == "wait_odom":
                self._hold("WAIT_ODOM")
                return

        ball_rel = self._ball_rel_fresh()
        ball_odom = None
        if pose is not None and ball_rel is not None:
            ball_odom = _rel_to_odom(pose, ball_rel[0], ball_rel[1])

        if self._phase == "wait_ball":
            if ball_rel is None:
                self._hold("WAIT_BALL")
                return
            if hypot(ball_rel[0], ball_rel[1]) > BALL_FAR_M:
                self._hold("WAIT_BALL_FAR")
                return
            assert ball_odom is not None
            self._start_kick(ball_odom)

        if self._phase == "kick":
            if ball_rel is None:
                self._stop_kick("ball_lost")
            elif hypot(ball_rel[0], ball_rel[1]) > BALL_FAR_M:
                self._stop_kick("ball_far")
            elif self._kick_request is not None:
                assert ball_odom is not None
                self._kick_request = VisualKickRequest(
                    robot_pose=pose,
                    ball=Point2(ball_odom.x, ball_odom.y),
                    target=Point2(TARGET_ODOM.x, TARGET_ODOM.y),
                    power=KICK_POWER,
                    duration_sec=self._kick_request.duration_sec,
                )
                progress = self.kick_skill.tick(self._kick_request, self.command)
                self._send_kick_reference()
                if progress.status == SkillStatus.SUCCEEDED:
                    self._stop_kick("timer")
        else:
            self.command.stop_body()

        result = self.arbiter.execute(
            self.command,
            ArbiterInput(force_stop=True, suppress_body=self._phase == "kick"),
        )
        self._state_pub.publish(String(data=self._phase))
        if result.published_cmd is not None:
            self._cmd_pub.publish(Float32MultiArray(data=list(result.published_cmd)))

    def _hold(self, state: str) -> None:
        self.command.stop_body()
        result = self.arbiter.execute(self.command, ArbiterInput(force_stop=True))
        self._state_pub.publish(String(data=state))
        if result.published_cmd is not None:
            self._cmd_pub.publish(Float32MultiArray(data=list(result.published_cmd)))


def _handle_key(node: PerceptionKickDemo, key: str) -> None:
    if key in ("\n", "\r"):
        node.request_kick()
    elif key in ("k", "K"):
        node.request_stop()


def _stdin_loop(node: PerceptionKickDemo) -> None:
    if not sys.stdin.isatty():
        while rclpy.ok():
            try:
                line = sys.stdin.readline()
            except Exception:
                return
            if line == "":
                return
            _handle_key(node, line.strip()[:1] or "\n")
        return

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while rclpy.ok():
            ready, _, _ = select.select([sys.stdin], [], [], 0.2)
            if not ready:
                continue
            key = sys.stdin.read(1)
            if key == "":
                return
            _handle_key(node, key)
    except Exception:
        return
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def main() -> None:
    if not rclpy.ok():
        rclpy.init()
    adapter = create_booster_adapter()
    time.sleep(2)
    arbiter = ActionArbiter(adapter, VelocityLimits(vx=0.8, vy=0.6, vtheta=1.2))
    if ALWAYS_SOCCER:
        arbiter.ensure_soccer_mode()
    else:
        arbiter.enter_walk()
    arbiter.reset_odom()
    time.sleep(0.5)

    node = PerceptionKickDemo(arbiter)
    threading.Thread(target=_stdin_loop, args=(node,), name="kick_stdin", daemon=True).start()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        arbiter.request_visual_kick(False)
        arbiter.shutdown_stop()
        print("\nRobot Stopped Safely.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

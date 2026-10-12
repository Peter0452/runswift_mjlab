#!/usr/bin/env python3
"""Demo: one visual kick per keypress, no perception.

Ball and goal are fixed in the odom frame. Enter resets odom and starts a kick;
press k to stop. The hold timer is only a backup.

  ros2 run behaviour demo_kick_ball_action_no_perception.py
"""
from __future__ import annotations

import select
import sys
import termios
import threading
import time
import tty
from math import atan2, hypot

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, String

from action.arbiter import ActionArbiter
from action.booster_adapter import create_booster_adapter
from action.config import ALWAYS_SOCCER
from action.types import ArbiterInput, MotionCommand, VelocityLimits
from skills.base import Point2, Pose2, SkillStatus, request_with_robot
from skills.visual_kick import VisualKick, VisualKickRequest

ODOM_TOPIC = "/odom"
FREQUENCY_HZ = 30.0
ODOM_RESET_READY_M = 0.35
BALL_ODOM = Pose2(0.5, 0.0, 0.0)
TARGET_ODOM = Pose2(5.0, 0.0, 0.0)
KICK_POWER = 1.5
KICK_HOLD_SEC = 3.0


def yaw_from_quaternion(x: float, y: float, z: float, w: float) -> float:
    return atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


class KickBallDemo(Node):
    """Idle until Enter; then run VisualKick with a fake odom ball."""

    def __init__(self, arbiter: ActionArbiter) -> None:
        super().__init__("demo_kick_ball_action_no_perception")
        self.arbiter = arbiter
        self.command = MotionCommand()
        self.kick_skill = VisualKick()
        self._kick_request = VisualKickRequest(
            robot_pose=Pose2(0.0, 0.0, 0.0),
            ball=Point2(BALL_ODOM.x, BALL_ODOM.y),
            target=Point2(TARGET_ODOM.x, TARGET_ODOM.y),
            power=KICK_POWER,
            duration_sec=KICK_HOLD_SEC,
        )
        self._phase = "wait_odom"
        self._pose: Pose2 | None = None
        self._kick_lock = threading.Lock()
        self._kick_requested = False
        self._stop_requested = False
        self._kick_after_reset = False

        self._state_pub = self.create_publisher(String, "/behaviour/state", 2)
        self._cmd_pub = self.create_publisher(Float32MultiArray, "/behaviour/cmd_vel", 2)
        self.create_subscription(Odometry, ODOM_TOPIC, self._on_odom, 10)
        self.create_timer(1.0 / FREQUENCY_HZ, self._on_timer)
        self.get_logger().info(
            f"Kick demo: ball=({BALL_ODOM.x:.1f}, {BALL_ODOM.y:.1f}) "
            f"target=({TARGET_ODOM.x:.1f}, {TARGET_ODOM.y:.1f}) "
            f"power={KICK_POWER} hold={KICK_HOLD_SEC:.1f}s odom={ODOM_TOPIC}"
        )
        print("Enter = kick. k = stop. Ctrl-C = quit.", flush=True)

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

    def _arm_kick(self) -> None:
        if self._phase == "kick":
            self._stop_kick()
        self.arbiter.reset_odom()
        self._pose = None
        self._kick_after_reset = True
        self._phase = "wait_odom"
        self.get_logger().info("Odom reset; waiting then kicking")

    def _start_kick(self) -> None:
        self.kick_skill.on_enter(self._kick_request)
        self.arbiter.request_stop_now()
        self.arbiter.request_visual_kick(True)
        self._phase = "kick"
        self.get_logger().info("Skill -> VisualKick")

    def _stop_kick(self) -> None:
        self.kick_skill.on_exit()
        self.arbiter.request_visual_kick(False)
        self.arbiter.request_stop_now()
        self._phase = "idle"
        self.get_logger().info("Kick stopped; Enter to kick, k to stop")

    def _send_kick_reference(self) -> None:
        ref = self.kick_skill.reference
        if ref is None:
            return
        self.arbiter.update_kick_command(ref.direction, ref.power)
        self.arbiter.update_kick_ball(ref.ball_x, ref.ball_y)

    def _on_timer(self) -> None:
        self.command.reset()
        pose = self._pose
        if self._consume_stop_request():
            self._kick_after_reset = False
            if self._phase in ("kick", "wait_odom"):
                self._stop_kick()
        elif self._consume_kick_request():
            self._arm_kick()
            pose = self._pose

        if pose is None or self._phase == "wait_odom":
            if pose is not None and hypot(pose.x, pose.y) <= ODOM_RESET_READY_M:
                if self._kick_after_reset:
                    self._kick_after_reset = False
                    self._start_kick()
                else:
                    self._phase = "idle"
                    self.get_logger().info("Odom reset ready; press Enter to kick")
            if self._phase == "wait_odom":
                self.command.stop_body()
                result = self.arbiter.execute(self.command, ArbiterInput(force_stop=True))
                self._state_pub.publish(String(data="WAIT_ODOM"))
                if result.published_cmd is not None:
                    self._cmd_pub.publish(Float32MultiArray(data=list(result.published_cmd)))
                return

        if self._phase == "kick":
            progress = self.kick_skill.tick(
                request_with_robot(self._kick_request, pose),
                self.command,
            )
            self._send_kick_reference()
            if progress.status == SkillStatus.SUCCEEDED:
                self._stop_kick()
        else:
            self.command.stop_body()

        result = self.arbiter.execute(
            self.command,
            ArbiterInput(force_stop=True, suppress_body=self._phase == "kick"),
        )
        self._state_pub.publish(String(data=self._phase))
        if result.published_cmd is not None:
            self._cmd_pub.publish(Float32MultiArray(data=list(result.published_cmd)))


def _handle_key(node: KickBallDemo, key: str) -> None:
    if key in ("\n", "\r"):
        node.request_kick()
    elif key in ("k", "K"):
        node.request_stop()


def _stdin_loop(node: KickBallDemo) -> None:
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

    node = KickBallDemo(arbiter)
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

#!/usr/bin/env python3
"""Open-day / filming demo: square walk+pose, then circle patrol.

Uses /odom. Resets odom once at process start so waypoints are in that frame.
Does not load the chase/gameplay node. Edit the constants below, then:

  ros2 run behaviour open_day_demo.py
"""
from __future__ import annotations

import math
import random
import time
from math import atan2, hypot

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, String

from action.arbiter import ActionArbiter
from action.booster_adapter import create_booster_adapter
from action.config import ALWAYS_SOCCER
from action.types import ArbiterInput, MotionCommand, VelocityLimits
from skills.base import Point2, Pose2, Skill, SkillStatus, request_with_robot
from skills.stand import Stand, StandRequest
from skills.walk_in_circle import WalkInCircle, WalkInCircleRequest
from skills.walk_to_pose import WalkToPose, WalkToPoseRequest

ODOM_TOPIC = "/odom"
FREQUENCY_HZ = 30.0
STOP_SEC = 8.0
# Extra wait after STOP_SEC: stay still until the vendor action reports done.
ACTION_FINISH_TIMEOUT_SEC = 8.0
# SDK action ids, or None for a still pose.
STAND_ACTIONS = ("hand_wave", "gesture_dabing", "bow", None)
LOOP = True
DISTANCE_TOLERANCE = 0.2
THETA_TOLERANCE = 0.4
# After reset_odom, treat poses this close to the origin as "ready".
ODOM_RESET_READY_M = 0.1

SQUARE_SIDE = 1.5
half_pi = math.pi / 2.0
SQUARE_WAYPOINTS = (
    Pose2(SQUARE_SIDE, 0.0, 0.0),
    Pose2(SQUARE_SIDE, SQUARE_SIDE, half_pi),
    Pose2(0.0, SQUARE_SIDE, math.pi),
    Pose2(0.0, 0.0, -half_pi),
)

# Centre (R, 0), radius R: start pose (0, 0) is already on the circle.
CIRCLE_RADIUS = 0.8
CIRCLE_CENTRE = Pose2(CIRCLE_RADIUS, 0.0, 0.0)
CIRCLE_REVOLUTIONS = 1.0
CIRCLE_SPEED = 0.30
CIRCLE_DIRECTION = 1.0  # +1 CCW, -1 CW

# Acts in order. "square" = WalkToPose + Stand at each corner.
SEQUENCE = ("square", "circle")


def yaw_from_quaternion(x: float, y: float, z: float, w: float) -> float:
    return atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


class OpenDayDemo(Node):
    """Sequence WalkToPose, Stand, and WalkInCircle on reset odom."""

    def __init__(self, arbiter: ActionArbiter) -> None:
        super().__init__("open_day_demo")
        self.arbiter = arbiter
        self.command = MotionCommand()
        self.walk_skill = WalkToPose()
        self.stand_skill = Stand()
        self.circle_skill = WalkInCircle()
        self._skill: Skill | None = None
        self._request = None
        self._phase = "wait_odom"
        self._pose: Pose2 | None = None
        self._steps: list[tuple[str, object]] = _build_steps()
        self._step_index = 0
        self._last_wait_log_at = 0.0
        self._action_wait_started = 0.0

        self._state_pub = self.create_publisher(String, "/behaviour/state", 2)
        self._cmd_pub = self.create_publisher(Float32MultiArray, "/behaviour/cmd_vel", 2)
        self.create_subscription(Odometry, ODOM_TOPIC, self._on_odom, 10)
        self.create_timer(1.0 / FREQUENCY_HZ, self._on_timer)
        self.get_logger().info(
            f"Open-day demo: sequence={SEQUENCE} loop={LOOP} "
            f"square={SQUARE_SIDE:.2f}m circle_r={CIRCLE_RADIUS:.2f}m "
            f"odom={ODOM_TOPIC}"
        )

    def _on_odom(self, msg: Odometry) -> None:
        pose = msg.pose.pose
        yaw = yaw_from_quaternion(
            pose.orientation.x,
            pose.orientation.y,
            pose.orientation.z,
            pose.orientation.w,
        )
        self._pose = Pose2(float(pose.position.x), float(pose.position.y), yaw)

    def _activate(self, skill: Skill, request) -> None:
        if self._skill is not None:
            self._skill.on_exit()
        self.arbiter.request_action(None)
        self._skill = skill
        self._request = request
        self._skill.on_enter(request)
        if isinstance(skill, Stand):
            self.arbiter.request_stop_now()
            action_id = random.choice(STAND_ACTIONS)
            if action_id:
                self.arbiter.request_action(action_id)
            self.get_logger().info(f"Skill -> Stand action={action_id!r} {request}")
            return
        self.get_logger().info(f"Skill -> {type(skill).__name__} {request}")

    def _start_step(self, index: int) -> None:
        kind, payload = self._steps[index]
        self._step_index = index
        if kind == "walk":
            target = payload
            assert isinstance(target, Pose2)
            self._activate(
                self.walk_skill,
                WalkToPoseRequest(
                    robot_pose=Pose2(0.0, 0.0, 0.0),
                    target_pose=target,
                    distance_tolerance=DISTANCE_TOLERANCE,
                    theta_tolerance=THETA_TOLERANCE,
                ),
            )
            self._phase = "walk"
        elif kind == "circle":
            self._activate(
                self.circle_skill,
                WalkInCircleRequest(
                    robot_pose=Pose2(0.0, 0.0, 0.0),
                    centre=Point2(CIRCLE_CENTRE.x, CIRCLE_CENTRE.y),
                    radius=CIRCLE_RADIUS,
                    speed=CIRCLE_SPEED,
                    direction=CIRCLE_DIRECTION,
                    revolutions=CIRCLE_REVOLUTIONS,
                ),
            )
            self._phase = "circle"
        else:
            self._activate(self.stand_skill, StandRequest(duration_sec=STOP_SEC))
            self._phase = "stand"

    def _advance(self) -> None:
        nxt = self._step_index + 1
        if nxt >= len(self._steps):
            if LOOP and self._steps:
                self.get_logger().info("Sequence complete; looping")
                self._start_step(0)
            else:
                self.get_logger().info("Sequence complete; standing")
                self._activate(self.stand_skill, StandRequest(duration_sec=STOP_SEC))
                self._phase = "done"
            return
        self._start_step(nxt)

    def _on_timer(self) -> None:
        self.command.reset()
        pose = self._pose
        if pose is None:
            self._state_pub.publish(String(data="WAIT_ODOM"))
            self.command.stop_body()
            result = self.arbiter.execute(self.command, ArbiterInput(force_stop=True))
            if result.published_cmd is not None:
                self._cmd_pub.publish(Float32MultiArray(data=list(result.published_cmd)))
            return

        if self._phase == "wait_odom":
            if hypot(pose.x, pose.y) > ODOM_RESET_READY_M:
                now = time.monotonic()
                if now - self._last_wait_log_at >= 1.0:
                    self.get_logger().info(
                        f"Waiting for odom near origin after reset "
                        f"({pose.x:.2f}, {pose.y:.2f})"
                    )
                    self._last_wait_log_at = now
                self.command.stop_body()
                result = self.arbiter.execute(self.command, ArbiterInput(force_stop=True))
                if result.published_cmd is not None:
                    self._cmd_pub.publish(Float32MultiArray(data=list(result.published_cmd)))
                return
            self._start_step(0)

        if self._phase == "wait_action":
            self.command.stop_body()
            timed_out = (
                time.monotonic() - self._action_wait_started >= ACTION_FINISH_TIMEOUT_SEC
            )
            if self.arbiter.action_running() and not timed_out:
                result = self.arbiter.execute(self.command, ArbiterInput(force_stop=True))
                skill_name = (
                    type(self._skill).__name__ if self._skill is not None else "none"
                )
                self._state_pub.publish(String(data=f"{self._phase}:{skill_name}"))
                if result.published_cmd is not None:
                    self._cmd_pub.publish(Float32MultiArray(data=list(result.published_cmd)))
                return
            if timed_out:
                self.get_logger().warn("Gesture still running; continuing anyway")
            self._advance()

        assert self._skill is not None and self._request is not None
        progress = self._skill.tick(
            request_with_robot(self._request, pose),
            self.command,
        )
        if progress.status == SkillStatus.SUCCEEDED:
            if self._phase == "done":
                self.command.stop_body()
            elif self._phase == "stand":
                self.arbiter.request_action(None)
                if self.arbiter.action_running():
                    self._phase = "wait_action"
                    self._action_wait_started = time.monotonic()
                    self.command.stop_body()
                else:
                    self._advance()
                    if self._skill is not None and self._request is not None:
                        self._skill.tick(
                            request_with_robot(self._request, pose),
                            self.command,
                        )
            else:
                self._advance()
                if self._skill is not None and self._request is not None:
                    self._skill.tick(
                        request_with_robot(self._request, pose),
                        self.command,
                    )

        force_stop = isinstance(self._skill, Stand)
        result = self.arbiter.execute(
            self.command,
            ArbiterInput(force_stop=force_stop),
        )
        skill_name = type(self._skill).__name__ if self._skill is not None else "none"
        self._state_pub.publish(String(data=f"{self._phase}:{skill_name}"))
        if result.published_cmd is not None:
            self._cmd_pub.publish(Float32MultiArray(data=list(result.published_cmd)))


def _build_steps() -> list[tuple[str, object]]:
    steps: list[tuple[str, object]] = []
    for act in SEQUENCE:
        if act == "square":
            for waypoint in SQUARE_WAYPOINTS:
                steps.append(("walk", waypoint))
                steps.append(("stand", STOP_SEC))
        elif act == "circle":
            steps.append(("circle", None))
            steps.append(("stand", STOP_SEC))
        else:
            raise ValueError(f"Unknown SEQUENCE act: {act}")
    return steps


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

    node = OpenDayDemo(arbiter)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        arbiter.shutdown_stop()
        print("\nRobot Stopped Safely.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

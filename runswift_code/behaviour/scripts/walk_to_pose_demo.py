#!/usr/bin/env python3
"""Demo: WalkToPose + Stand through the action arbiter, driven by /odom.

Does not load the chase/gameplay node. Edit the constants below, then:

  ros2 run behaviour walk_to_pose_demo.py
"""
from __future__ import annotations

import math
import time
from math import atan2, cos, sin

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, String

from action.arbiter import ActionArbiter
from action.booster_adapter import create_booster_adapter
from action.config import ALWAYS_SOCCER
from action.types import ArbiterInput, MotionCommand, VelocityLimits
from skills.base import Pose2, Skill, SkillStatus, request_with_robot
from skills.stand import Stand, StandRequest
from skills.walk_to_pose import WalkToPose, WalkToPoseRequest, wrap_pi

ODOM_TOPIC = "/odom"
FREQUENCY_HZ = 30.0
STOP_SEC = 2.0
RELATIVE_TO_START = True
DISTANCE_TOLERANCE = 0.3
THETA_TOLERANCE = 0.4
# Local (x, y, theta) if RELATIVE_TO_START, else odom-frame poses.
half_pi = math.pi / 2.0
WAYPOINTS = (
    Pose2(1.8, 0.0, 0),
    Pose2(1.8, 1.8, half_pi),
    Pose2(0.0, 1.8, half_pi*2),
    Pose2(0.0, 0.0, half_pi*3),
)


def yaw_from_quaternion(x: float, y: float, z: float, w: float) -> float:
    return atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


def compose_pose(base: Pose2, relative: Pose2) -> Pose2:
    """Apply ``relative`` in ``base``'s frame (odom start ⊕ local waypoint)."""
    return Pose2(
        x=base.x + relative.x * cos(base.theta) - relative.y * sin(base.theta),
        y=base.y + relative.x * sin(base.theta) + relative.y * cos(base.theta),
        theta=wrap_pi(base.theta + relative.theta),
    )


class WalkToPoseDemo(Node):
    """Sequence WalkToPose and Stand using /odom as the current pose."""

    def __init__(self, arbiter: ActionArbiter) -> None:
        super().__init__("walk_to_pose_demo")
        self.arbiter = arbiter
        self.command = MotionCommand()
        self.walk_skill = WalkToPose()
        self.stand_skill = Stand()
        self._skill: Skill | None = None
        self._request = None
        self._phase = "wait_odom"
        self._waypoint_index = 0
        self._resolved: list[Pose2] = []
        self._origin: Pose2 | None = None
        self._pose: Pose2 | None = None

        self._state_pub = self.create_publisher(String, "/behaviour/state", 2)
        self._cmd_pub = self.create_publisher(Float32MultiArray, "/behaviour/cmd_vel", 2)
        self.create_subscription(Odometry, ODOM_TOPIC, self._on_odom, 10)
        self.create_timer(1.0 / FREQUENCY_HZ, self._on_timer)
        self.get_logger().info(
            f"WalkToPose demo: {len(WAYPOINTS)} waypoints, "
            f"relative={RELATIVE_TO_START}, stop={STOP_SEC:.1f}s, odom={ODOM_TOPIC}"
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
        if self._origin is None:
            self._origin = self._pose
            if RELATIVE_TO_START:
                self._resolved = [compose_pose(self._origin, wp) for wp in WAYPOINTS]
            else:
                self._resolved = list(WAYPOINTS)
            for i, wp in enumerate(self._resolved):
                self.get_logger().info(
                    f"waypoint[{i}] odom=({wp.x:.2f}, {wp.y:.2f}, {wp.theta:.2f})"
                )

    def _activate(self, skill: Skill, request) -> None:
        if self._skill is not None:
            self._skill.on_exit()
        self._skill = skill
        self._request = request
        self._skill.on_enter(request)
        if isinstance(skill, Stand):
            self.arbiter.request_stop_now()
        self.get_logger().info(f"Skill -> {type(skill).__name__} {request}")

    def _start_walk(self, index: int) -> None:
        target = self._resolved[index]
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
        self._waypoint_index = index

    def _start_stand(self, next_index: int | None) -> None:
        self._activate(self.stand_skill, StandRequest(duration_sec=STOP_SEC))
        self._phase = "stand_done" if next_index is None else "stand"
        self._waypoint_index = 0 if next_index is None else next_index

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
            self._start_walk(0)

        assert self._skill is not None and self._request is not None
        progress = self._skill.tick(
            request_with_robot(self._request, pose),
            self.command,
        )

        if progress.status == SkillStatus.SUCCEEDED:
            if self._phase == "walk":
                nxt = self._waypoint_index + 1
                if nxt >= len(self._resolved):
                    self.get_logger().info("Last waypoint reached; standing")
                    self._start_stand(None)
                else:
                    self.get_logger().info(
                        f"Arrived waypoint {self._waypoint_index}; standing then {nxt}"
                    )
                    self._start_stand(nxt)
            elif self._phase == "stand":
                self._start_walk(self._waypoint_index)
            elif self._phase == "stand_done":
                self.command.stop_body()

        force_stop = isinstance(self._skill, Stand)
        result = self.arbiter.execute(
            self.command,
            ArbiterInput(force_stop=force_stop),
        )
        self._state_pub.publish(String(data=f"{self._phase}:{type(self._skill).__name__}"))
        if result.published_cmd is not None:
            self._cmd_pub.publish(Float32MultiArray(data=list(result.published_cmd)))


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

    node = WalkToPoseDemo(arbiter)
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

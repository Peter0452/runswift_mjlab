"""Walk around an odom-frame centre. Demo-only; not used in match play."""
from __future__ import annotations

from dataclasses import dataclass
from math import atan2, hypot, pi

from action.types import MotionCommand
from skills.base import Point2, Pose2, Skill, SkillProgress, SkillStatus
from skills.walk_to_pose import wrap_pi


def _clip(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


@dataclass(frozen=True)
class WalkInCircleRequest:
    """Circle in the same world/odom frame as ``robot_pose``."""

    robot_pose: Pose2
    centre: Point2
    radius: float
    speed: float = 0.35
    direction: float = 1.0  # +1 CCW, -1 CW
    revolutions: float = 1.0
    max_vx: float = 0.8
    max_vy: float = 0.6
    max_vtheta: float = 1.2
    kp_radius: float = 1.2
    kp_yaw: float = 1.8


def circle_angle(request: WalkInCircleRequest) -> float:
    robot = request.robot_pose
    centre = request.centre
    return atan2(robot.y - centre.y, robot.x - centre.x)


def walk_in_circle_velocity(request: WalkInCircleRequest) -> tuple[float, float, float]:
    """Forward along the tangent, strafe to hold radius, yaw to face tangent."""
    direction = 1.0 if request.direction >= 0.0 else -1.0
    robot = request.robot_pose
    centre = request.centre
    dx = robot.x - centre.x
    dy = robot.y - centre.y
    radius_now = hypot(dx, dy)
    angle = circle_angle(request) if radius_now > 1e-4 else robot.theta
    desired_heading = wrap_pi(angle + direction * (pi / 2.0))
    heading_err = wrap_pi(desired_heading - robot.theta)

    speed = abs(request.speed)
    omega = 0.0
    if request.radius > 1e-3:
        omega = direction * speed / request.radius

    radial_err = radius_now - request.radius
    cmd_x = speed
    cmd_y = direction * request.kp_radius * radial_err
    cmd_theta = request.kp_yaw * heading_err + omega

    max_vx = abs(request.max_vx)
    max_vy = abs(request.max_vy)
    max_vtheta = abs(request.max_vtheta)
    cmd_x = _clip(cmd_x, -max_vx, max_vx)
    cmd_y = _clip(cmd_y, -max_vy, max_vy)
    cmd_theta = _clip(cmd_theta, -max_vtheta, max_vtheta)
    if abs(cmd_x) < 0.05:
        cmd_x = 0.0
    if abs(cmd_y) < 0.05:
        cmd_y = 0.0
    if abs(cmd_theta) < 0.05:
        cmd_theta = 0.0
    return cmd_x, cmd_y, cmd_theta


class WalkInCircle(Skill):
    def __init__(self) -> None:
        self._prev_angle: float | None = None
        self._travelled: float = 0.0

    def on_enter(self, request: WalkInCircleRequest) -> None:
        self._prev_angle = None
        self._travelled = 0.0

    def on_exit(self) -> None:
        self._prev_angle = None
        self._travelled = 0.0

    def tick(
        self,
        request: WalkInCircleRequest,
        command: MotionCommand,
    ) -> SkillProgress:
        angle = circle_angle(request)
        if self._prev_angle is None:
            self._prev_angle = angle
        else:
            self._travelled += wrap_pi(angle - self._prev_angle)
            self._prev_angle = angle

        target = abs(request.revolutions) * 2.0 * pi
        if target > 1e-6 and abs(self._travelled) >= target:
            command.stop_body()
            return SkillProgress(status=SkillStatus.SUCCEEDED, progress=1.0, reason="revolutions")

        vx, vy, vtheta = walk_in_circle_velocity(request)
        command.set_body(vx, vy, vtheta)
        progress = 0.0 if target <= 1e-6 else min(1.0, abs(self._travelled) / target)
        return SkillProgress(status=SkillStatus.RUNNING, progress=progress, reason="circling")

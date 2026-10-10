"""Walk to a world/odom-frame pose. Extracted from ``walk_to_pose_command``."""
from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, hypot, pi, sin

from action.types import MotionCommand
from skills.base import Pose2, Skill, SkillProgress, SkillStatus
from skills.obstacle_avoid import avoid_opponents


def wrap_pi(angle: float) -> float:
    while angle > pi:
        angle -= 2 * pi
    while angle < -pi:
        angle += 2 * pi
    return angle


def _clip(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


@dataclass(frozen=True)
class WalkToPoseRequest:
    """Walk toward a world-frame target. Robot pose is this tick's facts.

    ``robot_pose`` is the robot now (field in match play, odom in the demo).
    ``target_pose`` is the goal in that same frame.
    ``obstacles`` / ``protect_ball`` are world-frame ``(x, y)`` points.
    ``planned_velocity`` is robot-frame ``(vx, vy, vtheta)`` if a parent
    skill already planned the walk.
    """

    robot_pose: Pose2
    target_pose: Pose2
    distance_tolerance: float = 0.3
    theta_tolerance: float = 0.4
    speed_scale: float = 1.0
    max_vx: float = 0.8
    max_vy: float = 0.6
    max_vtheta: float = 1.2
    sprint_distance: float = 10.0
    forward_scale: float = 1.0
    strafe_scale: float = 1.0
    turn_threshold: float = 0.4
    obstacles: tuple[tuple[float, float], ...] = ()
    protect_ball: tuple[float, float] | None = None
    apply_avoidance: bool = False
    planned_velocity: tuple[float, float, float] | None = None


def pose_error(request: WalkToPoseRequest) -> tuple[float, float]:
    """World-frame distance (m) and absolute heading error (rad) to the target."""
    robot = request.robot_pose
    target = request.target_pose
    distance = hypot(target.x - robot.x, target.y - robot.y)
    heading = abs(wrap_pi(robot.theta - target.theta))
    return distance, heading


def arrived(request: WalkToPoseRequest) -> bool:
    distance, heading = pose_error(request)
    return distance < request.distance_tolerance and heading < request.theta_tolerance


def walk_to_pose_velocity(request: WalkToPoseRequest) -> tuple[float, float, float]:
    """Robot-frame body velocity toward ``request.target_pose``."""
    if arrived(request):
        return 0.0, 0.0, 0.0

    robot = request.robot_pose
    target = request.target_pose
    r = hypot(target.x - robot.x, target.y - robot.y)
    max_vx_eff = request.max_vx * request.speed_scale
    max_vy_eff = request.max_vy * request.speed_scale
    max_vtheta_eff = request.max_vtheta * request.speed_scale
    forward_speed = min(max_vx_eff, max_vx_eff * r)

    target_dir = atan2(target.y - robot.y, target.x - robot.x)
    target_dir_robot = wrap_pi(target_dir - robot.theta)
    heading_err = wrap_pi(target.theta - robot.theta)

    if r > request.sprint_distance:
        if abs(target_dir_robot) > request.turn_threshold:
            cmd_x, cmd_y = 0.0, 0.0
            cmd_theta = _clip(target_dir_robot, -max_vtheta_eff, max_vtheta_eff)
        else:
            cmd_x = forward_speed
            cmd_y = 0.0
            cmd_theta = _clip(target_dir_robot, -max_vtheta_eff, max_vtheta_eff)
    else:
        cmd_x = forward_speed * cos(target_dir_robot)
        cmd_y = forward_speed * sin(target_dir_robot)
        if max_vx_eff > 1e-6:
            cmd_y = _clip(cmd_y, -max_vy_eff, max_vy_eff)
        cmd_theta = _clip(heading_err, -max_vtheta_eff, max_vtheta_eff)

    cmd_x = _clip(cmd_x * request.forward_scale, -max_vx_eff, max_vx_eff)
    cmd_y = _clip(cmd_y * request.strafe_scale, -max_vy_eff, max_vy_eff)

    if abs(cmd_x) < 0.05:
        cmd_x = 0.0
    if abs(cmd_y) < 0.05:
        cmd_y = 0.0
    if abs(cmd_theta) < 0.05:
        cmd_theta = 0.0
    return cmd_x, cmd_y, cmd_theta


class WalkToPose(Skill):
    def tick(
        self,
        request: WalkToPoseRequest,
        command: MotionCommand,
    ) -> SkillProgress:
        """Write a robot-frame walk command toward ``request.target_pose``."""
        if request.planned_velocity is None and arrived(request):
            command.stop_body()
            return SkillProgress(status=SkillStatus.SUCCEEDED, progress=1.0, reason="arrived")

        if request.planned_velocity is not None:
            vx, vy, vtheta = request.planned_velocity
        else:
            vx, vy, vtheta = walk_to_pose_velocity(request)

        if request.apply_avoidance:
            vx, vy, vtheta = avoid_opponents(
                request.robot_pose,
                vx,
                vy,
                vtheta,
                request.obstacles,
                protect_ball=request.protect_ball,
            )
            command.set_body(vx, vy, vtheta)
            command.avoidance_applied = True
        else:
            command.set_body(vx, vy, vtheta)

        if arrived(request) and vx == 0.0 and vy == 0.0 and vtheta == 0.0:
            return SkillProgress(status=SkillStatus.SUCCEEDED, progress=1.0, reason="arrived")

        distance, _ = pose_error(request)
        span = max(distance, request.distance_tolerance)
        progress = max(0.0, min(1.0, 1.0 - distance / max(span, 1e-3)))
        return SkillProgress(status=SkillStatus.RUNNING, progress=progress, reason="walking")

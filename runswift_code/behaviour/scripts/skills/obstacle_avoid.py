"""Local opponent avoidance. Soccer geometry; not platform safety."""
from __future__ import annotations

from collections.abc import Sequence
from math import cos, hypot, sin

from skills.base import Pose2

ROBOT_RADIUS_M = 0.28
OPPONENT_RADIUS_M = 0.28
SAFE_RADIUS_M = ROBOT_RADIUS_M + OPPONENT_RADIUS_M
INFLUENCE_RADIUS_M = SAFE_RADIUS_M + 1.5
PROTECT_BALL_LATERAL_M = 0.2
NUDGE_TANGENT_X = 1.2
NUDGE_TANGENT_Y = 1.8


def avoid_opponents(
    pose: Pose2,
    cmd_x: float,
    cmd_y: float,
    cmd_theta: float,
    obstacles: Sequence[tuple[float, float]],
    *,
    protect_ball: tuple[float, float] | None = None,
) -> tuple[float, float, float]:
    """Scale a robot-frame walk command away from world-frame obstacle centres.

    If ``protect_ball`` is set and no obstacle sits between the robot and that
    point, the original command is returned (WALK_TO_BALL_KICK behaviour).
    """
    if cmd_x == 0.0 and cmd_y == 0.0 and cmd_theta == 0.0:
        return cmd_x, cmd_y, cmd_theta

    cos_yaw = cos(pose.theta)
    sin_yaw = sin(pose.theta)
    out_x = cmd_x
    out_y = cmd_y
    ball_robot: tuple[float, float] | None = None
    if protect_ball is not None:
        ball_x = protect_ball[0] - pose.x
        ball_y = protect_ball[1] - pose.y
        ball_robot = (
            ball_x * cos_yaw + ball_y * sin_yaw,
            -ball_x * sin_yaw + ball_y * cos_yaw,
        )
    opponent_between = False

    for obs_x, obs_y in obstacles:
        dx_field = obs_x - pose.x
        dy_field = obs_y - pose.y
        obs_local_x = dx_field * cos_yaw + dy_field * sin_yaw
        obs_local_y = -dx_field * sin_yaw + dy_field * cos_yaw
        dist = hypot(obs_local_x, obs_local_y)
        if dist < 1e-6 or dist >= INFLUENCE_RADIUS_M:
            continue
        if ball_robot is not None:
            if (
                obs_local_x > 0.0
                and obs_local_x < ball_robot[0]
                and abs(obs_local_y - ball_robot[1]) < PROTECT_BALL_LATERAL_M
            ):
                opponent_between = True

        toward_x = obs_local_x / dist
        toward_y = obs_local_y / dist
        away_x = -toward_x
        away_y = -toward_y

        dot_toward = out_x * toward_x + out_y * toward_y
        if dot_toward > 0.0:
            if dist <= SAFE_RADIUS_M:
                removal = 1.0
            else:
                removal = 1.0 - (dist - SAFE_RADIUS_M) / (
                    INFLUENCE_RADIUS_M - SAFE_RADIUS_M
                )
            out_x -= removal * dot_toward * toward_x
            out_y -= removal * dot_toward * toward_y

        nudge_strength = max(0.0, 1.0 - dist / SAFE_RADIUS_M)
        if nudge_strength > 0.0:
            tangent_x = -away_y
            tangent_y = away_x
            out_x += tangent_x * nudge_strength * NUDGE_TANGENT_X
            out_y += tangent_y * nudge_strength * NUDGE_TANGENT_Y

    if ball_robot is not None and not opponent_between:
        return cmd_x, cmd_y, cmd_theta
    return out_x, out_y, cmd_theta

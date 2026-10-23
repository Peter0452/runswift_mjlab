"""MuJoCo port of B-Human's published walk/kick motion contracts.

The outer goal/waypoint request is supplied by this benchmark. This is not
an executable of B-Human's full framework or its soccer behaviour stack.
Apache-2.0 source and modification notices are in this directory's README.
"""

import math
from collections import deque

import numpy as np
from compare import Controller, body_xy, digest, session, yaw_of
from contracts import LEG_DEFAULT, Case, bhuman_observation

WALK_PATH = "bhuman/IsaacGymRL/pre-trained/WalkAndKick/K1_walk.onnx"
WALK_SHA = "9d1ec18504cb9d05ec708b9430783a2331cabf5415fc0db81c6318472e948e8f"


def wrap(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


def walk_observation(history, command, phase, dq, frequency):
    result = np.concatenate(
        [
            *history,
            command,
            [math.cos(2 * math.pi * phase), math.sin(2 * math.pi * phase)],
            np.asarray(dq) * 0.1,
            [frequency],
            np.zeros(6),
        ]
    ).astype(np.float32)
    if result.shape != (344,) or not np.isfinite(result).all():
        raise ValueError("Invalid B-Human walking observation")
    return result


def boundary_crossing(a, b, radius):
    """First whole-ball crossing, matching score_evaluator's virtual boundaries."""
    events = []
    for side in (-1, 1):
        for axis, plane, kind in (
            (0, 7 + radius, "goal_line"),
            (1, 4.5 + radius, "touchline"),
        ):
            if side * a[axis] < plane <= side * b[axis]:
                fraction = (plane - side * a[axis]) / (side * (b[axis] - a[axis]))
                point = a + fraction * (b - a)
                events.append(
                    (
                        fraction,
                        {
                            "side": side,
                            "kind": kind,
                            "inside_goal": bool(
                                kind == "goal_line"
                                and abs(point[1]) < 1.25 - radius
                                and 0 <= point[2] < 1.75 - radius
                            ),
                        },
                    )
                )
    return min(events, key=lambda item: item[0])[1] if events else None


class GoalController(Controller):
    def __init__(self, name, root):
        super().__init__(name, root)
        if name == "bhuman":
            path = root / WALK_PATH
            if digest(path) != WALK_SHA:
                raise ValueError("Pinned B-Human walking model differs")
            self.walker = session(path)
        self.history = deque(maxlen=10)

    def reset_goal(self, goal, bridge):
        ball = bridge.ball_world()[:2]
        heading = math.atan2(goal[1] - ball[1], goal[0] - ball[0])
        super().reset(
            Case(
                "goal", *ball, math.degrees(heading), float(np.linalg.norm(goal - ball))
            ),
            yaw_of(bridge.data),
        )
        self.goal = np.asarray(goal)
        self.history.clear()
        self.mode = "kick_loop" if self.name == "peter" else "walk"
        self.last_ball_net_distance = float("inf")
        self.was_kicking = False
        self.delay_start = None
        self.last_target = self.default_q.copy()
        self.side_sign = 1.0
        self.first_action_time = bridge.data.time

    def action(self, bridge):
        ball_world = bridge.ball_world()[:2]
        delta = self.goal - ball_world
        heading = math.atan2(delta[1], delta[0])
        distance_to_goal = float(np.linalg.norm(delta))
        yaw = yaw_of(bridge.data)
        self.case = Case("goal", *ball_world, math.degrees(heading), distance_to_goal)
        if self.name == "peter":
            # Published runner tracks headings relative to its enable yaw.
            self.actor._kick_heading = wrap(
                heading - (self.actor._yaw0 if self.actor._yaw0 is not None else yaw)
            )
            self.actor._range_one_hot = np.eye(3)[
                0 if distance_to_goal < 4 else 1 if distance_to_goal < 8 else 2
            ]
            return super().action(bridge)
        state = bridge.latest_state()
        q = np.clip(np.asarray(state.q), self.limits[:, 0], self.limits[:, 1])
        frame = np.r_[
            state.projected_gravity,
            state.imu.gyro,
            q[10:] - LEG_DEFAULT,
            self.last_target[10:] - LEG_DEFAULT,
            0,
            0,
        ]
        if not self.history:
            initial = frame.copy()
            initial[3:6] = 0
            self.history.extend(initial.copy() for _ in range(9))
        self.history.append(frame)
        soles = []
        for name in ("left_foot_link", "right_foot_link"):
            body = bridge.model.body(name).id
            soles.append(
                bridge.data.xpos[body]
                + bridge.data.xmat[body].reshape(3, 3) @ np.array([0, 0, -0.038])
            )
        midpoint = np.mean(soles, axis=0)
        ball = body_xy(bridge.ball_world(), midpoint, yaw)
        ball_distance = float(np.linalg.norm(ball))
        direction = wrap(heading - yaw)
        goal_axis = delta / max(distance_to_goal, 1e-8)
        side = np.array([-goal_axis[1], goal_axis[0]])
        robot_from_ball = bridge.data.qpos[:2] - ball_world
        lateral = float(robot_from_ball @ side)
        # Outer request: route around a ball lying between robot and behind-ball target.
        avoiding = float(robot_from_ball @ goal_axis) > -0.2 and abs(lateral) < 0.65
        if avoiding:
            if abs(lateral) > 0.1:
                self.side_sign = float(np.sign(lateral))
            waypoint = ball_world - 0.65 * goal_axis + self.side_sign * 0.85 * side
        else:
            waypoint = ball_world - 0.65 * goal_axis
        threshold = 1.1 + (0.2 if self.last_ball_net_distance < 1.1 else -0.2)
        nearby = ball_distance <= threshold and not avoiding
        t = float(bridge.data.time)
        if not nearby:
            self.delay_start = None
        elif self.delay_start is None:
            self.delay_start = t
        ball_in_kick = body_xy(ball, (0, 0), direction)
        height_diff = float(soles[0][2] - soles[1][2])
        phase_ready = (
            ball_in_kick[1] > 0 and 0 < self.phase < 0.25 and height_diff > 0.005
        ) or (ball_in_kick[1] < 0 and 0.5 < self.phase < 0.75 and height_diff < -0.005)
        kick = nearby and (self.was_kicking or phase_ready or t - self.delay_start >= 1)
        self.mode = "kick" if kick else "walk"
        self.last_ball_net_distance = ball_distance + (-0.2 if kick else 0.2)
        self.was_kicking = kick
        if kick:
            shifted = ball.copy()
            # Published K1 ball shift: 0..50 mm relative to the left sole.
            rotated = body_xy(shifted, (0, 0), direction)
            left = body_xy(soles[0], midpoint, yaw + direction)
            interpolation = float(
                np.clip((math.radians(100) - abs(direction)) / math.radians(20), 0, 1)
            )
            rotated[1] += (
                interpolation
                * float(np.clip((rotated[1] - left[1] - 0.04) / 0.09, 0, 1))
                * 0.05
            )
            shifted = body_xy(rotated, (0, 0), -direction)
            if ball_distance > 2:
                shifted *= 2 / max(float(np.linalg.norm(shifted)), 1e-8)
            if (
                self.previous_ball is None
                or np.linalg.norm(shifted - self.previous_ball) > 0.2
            ):
                self.previous_ball = shifted.copy()
            observation = bhuman_observation(
                state.projected_gravity,
                state.imu.gyro,
                shifted,
                body_xy(bridge.data.qvel[28:30], (0, 0), yaw),
                direction,
                self.phase,
                q[10:],
                state.dq[10:],
                self.previous,
                self.previous_ball,
                distance_to_goal,
            )
            raw = self.actor.run(
                None, {self.actor.get_inputs()[0].name: observation[None]}
            )[0].reshape(-1)
            self.previous_ball = shifted.copy()
        else:
            error = body_xy(waypoint, bridge.data.qpos[:2], yaw)
            bearing = math.atan2(error[1], error[0])
            desired_heading = (
                heading
                if np.linalg.norm(error) < 0.5
                else math.atan2(
                    waypoint[1] - bridge.data.qpos[1], waypoint[0] - bridge.data.qpos[0]
                )
            )
            command = np.r_[
                np.clip(1.2 * error, [-0.5, -0.3], [0.5, 0.3]),
                np.clip(1.5 * wrap(desired_heading - yaw), -0.6, 0.6),
            ]
            command[0] *= max(0.0, math.cos(bearing))
            if nearby:
                command[:] = 0  # Competition phase-gated kick delay.
            observation = walk_observation(
                self.history, command, self.phase, state.dq[10:], self.previous[12]
            )
            raw = self.walker.run(
                None, {self.walker.get_inputs()[0].name: observation[None]}
            )[0].reshape(-1)
        if raw.shape != (13,) or not np.isfinite(raw).all():
            raise ValueError("Invalid B-Human goal-controller output")
        target = self.default_q.copy()
        target[10:] = np.clip(
            LEG_DEFAULT + np.clip(raw[:12], -2, 2),
            self.limits[10:, 0],
            self.limits[10:, 1],
        )
        # Competition arm motion from sole X and tibia lateral displacement.
        for index, sole, shank, sign in (
            (2, soles[0], "Left_Shank", -1),
            (6, soles[1], "Right_Shank", 1),
        ):
            sole_relative = body_xy(sole, bridge.data.qpos[:3], yaw)
            tibia = body_xy(
                bridge.data.xpos[bridge.model.body(shank).id], bridge.data.qpos[:3], yaw
            )
            target[index] = 1.5 * sole_relative[0]
            offset = (
                max(0, tibia[1] - 0.096) if sign == -1 else min(0, tibia[1] + 0.096)
            )
            target[index + 1] = sign * math.radians(78) + 2.5 * offset
            target[index + 2] = 0
            target[index + 3] = sign * (math.radians(30) - 1.95 * sole_relative[0])
        blend = min(1.0, (t - self.first_action_time) / 1.0)
        target[2:10] = (1 - blend) * self.default_q[2:10] + blend * target[2:10]
        from policy_runner.policy.kick_loop_policy import head_track_angles

        self.head += np.clip(
            0.3
            * (
                head_track_angles(
                    [*body_xy(bridge.ball_world(), bridge.data.qpos[:3], yaw), 0]
                )
                - self.head
            ),
            -0.06,
            0.06,
        )
        target[:2] = self.head
        target = np.clip(target, self.limits[:, 0], self.limits[:, 1])
        self.previous = np.r_[target[10:] - LEG_DEFAULT, np.clip(raw[12], -0.5, 0.5)]
        self.phase = (self.phase + 0.02 * (1.5 + self.previous[12])) % 1
        self.last_target = target.copy()
        action = self.Action(
            joint_cmds=[
                self.JointCommand(
                    index=i,
                    q=float(target[i]),
                    kp=float(self.kp[i]),
                    kd=float(self.kd[i]),
                )
                for i in range(22)
            ]
        )
        return action, observation, raw

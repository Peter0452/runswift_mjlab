from dataclasses import dataclass
from math import cos, sin
from pathlib import Path
from threading import Thread
import time
import requests
import yaml

import rerun as rr

import numpy as np
BIGBROTHER_ADDR = "http://127.0.0.1:6767"
BEHAVIOUR_HANDLE = "behaviour"
DIMENSION_YAML = Path("/home/booster/Workspace/runswift/runswift_configs/dimension.yaml")
CONNECT_TIMEOUT_SEC = 0.5
CONNECT_RETRY_INTERVAL_SEC = 1.0
CONNECT_RETRY_DEADLINE_SEC = 30.0
# Keep BigBrother harmless during local runs where the robot config path is missing.
# These defaults match the small-field dimensions used in this repo.
DEFAULT_DIMS = {
    "length": 9.0,
    "width": 6.0,
    "goalAreaLength": 1.0,
    "goalAreaWidth": 3.0,
    "penaltyAreaLength": 2.0,
    "penaltyAreaWidth": 4.0,
    "centreCircleDiameter": 1.51,
}


@dataclass
class LastPublished:
    # previous state
    game_phase: int = -1
    gc_state: int = -1
    gc_phase: int = -1
    set_play: int = -1

    # monotonic timestamp of when field was last published
    field_timestamp: float = -1


last_published = LastPublished()


# Field dimensions may live in the robot workspace or the local checkout.
# Try both, then fall back so a missing YAML file does not break behaviour startup.
def _load_dimensions():
    repo_dimension_yaml = Path(__file__).resolve().parents[3] / "runswift_configs" / "dimension.yaml"
    for path in (DIMENSION_YAML, repo_dimension_yaml):
        try:
            with path.open("r") as f:
                loaded = yaml.safe_load(f)
            if loaded:
                return loaded
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"warning: failed to read field dimensions from {path}: {e}")
    print("warning: falling back to built-in BigBrother field dimensions")
    return DEFAULT_DIMS.copy()


# Rerun has appeared as both a flag and a function across SDK versions.
# This wrapper keeps logging checks consistent and quiet when Rerun is unavailable.
def _rerun_enabled() -> bool:
    enabled = getattr(rr, "is_enabled", None)
    if enabled is None:
        return True
    if callable(enabled):
        try:
            return bool(enabled())
        except Exception:
            return False
    return bool(enabled)


# A coordinate of 0.0 is a real field position, not "missing".
# Only treat ball coordinates as absent when they are explicitly None.
def _has_xy(obj) -> bool:
    return obj is not None and obj.global_x is not None and obj.global_y is not None



# Behaviour can start before the BigBrother daemon is ready.
# Keep trying briefly so launch ordering does not decide whether logging works.
def connect():
    deadline = time.monotonic() + CONNECT_RETRY_DEADLINE_SEC
    last_error = None
    while True:
        try:
            resp = requests.get(BIGBROTHER_ADDR + "/", timeout=CONNECT_TIMEOUT_SEC)
            if resp.ok:
                manifest = resp.json()

                # TODO: maybe application_id = robot_id and the recording id is gotten from the manifest
                robot_id = manifest.get("robot_id", "robot")
                rr.init(application_id=robot_id, recording_id=robot_id)
                rr.connect_grpc()
                return
            last_error = f"HTTP {resp.status_code}"
        except Exception as e:
            last_error = e

        if time.monotonic() >= deadline:
            print(f"warning: failed to connect to BigBrother at {BIGBROTHER_ADDR}: {last_error}")
            return
        time.sleep(CONNECT_RETRY_INTERVAL_SEC)


# Connect to BigBrother in the background so behaviour startup is not blocked.
connector_thread = Thread(target=connect, daemon=True)
connector_thread.start()

dims = _load_dimensions()


def log_world_state(s):
    if not _rerun_enabled():
        return

    if s.wm.self_pose:
        rr.log(
            "/behaviour/wm.self_pose",
            rr.Arrows3D(
                origins=[(s.wm.self_pose.x, s.wm.self_pose.y, 0.0)],
                vectors=[
                    (
                        cos(s.wm.self_pose.theta) * 0.4,
                        sin(s.wm.self_pose.theta) * 0.4,
                        0.0,
                    )
                ]
            ),
        )

        # Self pose is exactly one capsule.
        # Do not size these arrays from whatever robot detections happen to exist.
        rr.log(
            "/behaviour/wm.self_pose.capsule",
            rr.Capsules3D(
                translations=[(s.wm.self_pose.x, s.wm.self_pose.y, 0.25)],
                lengths=[1.0],
                radii=[0.25],
                colors=[(64, 128, 255)],
                labels=["self"],
                show_labels=True,
            ),
        )

    # Ball positions on the centre lines include zeroes, so rely on explicit None checks.
    if _has_xy(s.wm.ball):
        rr.log(
            "/behaviour/wm.ball.global_pos",
            rr.Capsules3D(
                translations=[
                    # 0.1 cause approximate size of ball
                    (s.wm.ball.global_x, s.wm.ball.global_y, 0.1)
                ],
                radii=[0.2],
                lengths=[0.0],
                colors=[(255, 128, 255)],
            ),
        )

        if s.wm.ball.global_vx is not None and s.wm.ball.global_vy is not None:
            rr.log(
                "/behaviour/wm.ball.global_vel",
                rr.Arrows3D(
                    origins=[(s.wm.ball.global_x, s.wm.ball.global_y, 0.1)],
                    vectors=[(s.wm.ball.global_vx, s.wm.ball.global_vy, 0.0)],
                    radii=[0.025],
                ),
            )

    rr.log(
        "/behaviour/wm.robots",
        rr.Capsules3D(
            translations=[
                (robot.pose.x, robot.pose.y, 0.25)
                for robot in s.wm.robots
                if robot.pose
            ],
            radii=[0.25 for robot in s.wm.robots if robot.pose],
            lengths=[1.0 for robot in s.wm.robots if robot.pose],
            rotation_axis_angles=[
                rr.RotationAxisAngle(axis=[0.0, 0.0, 1.0], angle=robot.pose.theta)
                for robot in s.wm.robots
                if robot.pose
            ],
            colors=[(255, 128, 64) for robot in s.wm.robots if robot.pose],
            labels=[robot.label for robot in s.wm.robots if robot.pose],
            show_labels=True,
        ),
    )

    if last_published.gc_state != s.wm.gc_state:
        last_published.gc_state = s.wm.gc_state
        rr.log(
            "/behaviour/wm.gc_state",
            rr.StateChange(
                state={
                    0: "INITIAL",
                    1: "READY",
                    2: "SET",
                    3: "PLAYING",
                    4: "FINISHED",
                }.get(s.wm.gc_state, f"UNKNOWN_{s.wm.gc_state}")
            ),
        )

    if last_published.gc_phase != s.wm.gc_phase:
        last_published.gc_phase = s.wm.gc_phase
        rr.log(
            "/behaviour/wm.gc_phase",
            rr.StateChange(
                state={
                    0: "NORMAL",
                    1: "PENALTY_SHOOT_OUT",
                    2: "EXTRA_TIME",
                    3: "TIMEOUT",
                }.get(s.wm.set_play, f"UNKNOWN_{s.wm.set_play}")
            ),
        )

    if last_published.set_play != s.wm.set_play:
        last_published.set_play = s.wm.set_play
        rr.log(
            "/behaviour/wm.set_play",
            rr.StateChange(
                state={
                    0: "NONE",
                    1: "DIRECT_FREE_KICK",
                    2: "INDIRECT_FREE_KICK",
                    3: "PENALTY_KICK",
                    4: "THROW_IN",
                    5: "GOAL_KICK",
                    6: "CORNER_KICK",
                }.get(s.wm.set_play, f"UNKNOWN_{s.wm.set_play}")
            ),
        )

    now = time.monotonic()

    if (now - last_published.field_timestamp) > 1.0:
        last_published.field_timestamp = now

        field_length = float(dims["length"])
        field_width = float(dims["width"])
        goal_area_length = float(dims["goalAreaLength"])
        goal_area_width = float(dims["goalAreaWidth"])
        penalty_area_length = float(dims["penaltyAreaLength"])
        penalty_area_width = float(dims["penaltyAreaWidth"])
        center_circle_radius = float(dims["centreCircleDiameter"]) / 2.0

        # Rerun expects per-box arrays to match the number of boxes.
        # Keep colours and radii aligned with the seven field/goal boxes below.
        rr.log(
            "/field/boxes",
            rr.Boxes3D(
                half_sizes=[
                    # field
                    (field_length * 0.5, field_width * 0.5, 0.0001),
                    # left_goal_area
                    (goal_area_length * 0.5, goal_area_width * 0.5, 0.0001),
                    # right_goal_area
                    (goal_area_length * 0.5, goal_area_width * 0.5, 0.0001),
                    # left_penalty_area
                    (penalty_area_length * 0.5, penalty_area_width * 0.5, 0.0001),
                    # right_penalty_area
                    (penalty_area_length * 0.5, penalty_area_width * 0.5, 0.0001),
                    # left_goal
                    (goal_area_length * 0.5, goal_area_width * 0.5, 0.5),
                    # right_goal
                    (goal_area_length * 0.5, goal_area_width * 0.5, 0.5),
                ],
                centers=[
                    # field (Base level)
                    (0.0, 0.0, 0.0),
                    # left_goal_area (Slightly raised to prevent Z-fighting)
                    (-field_length * 0.5 + goal_area_length * 0.5, 0.0, 0.0002),
                    # right_goal_area
                    (field_length * 0.5 - goal_area_length * 0.5, 0.0, 0.0002),
                    # left_penalty_area
                    (-field_length * 0.5 + penalty_area_length * 0.5, 0.0, 0.0002),
                    # right_penalty_area
                    (field_length * 0.5 - penalty_area_length * 0.5, 0.0, 0.0002),
                    # left_goal
                    (-field_length * 0.5 - goal_area_length * 0.5, 0.0, 0.5),
                    # right_goal
                    (field_length * 0.5 + goal_area_length * 0.5, 0.0, 0.5),
                ],
                colors=[
                    (255, 255, 255),
                    (255, 255, 255),
                    (255, 255, 255),
                    (255, 255, 255),
                    (255, 255, 255),
                    # left goal
                    (255, 221, 153),
                    # right goal
                    (153, 221, 255),
                ],
                fill_mode="MajorWireframe",
                radii=[0.01] * 7,
                labels=[
                    "field",
                    "left_goal_area",
                    "right_goal_area",
                    "left_penalty_area",
                    "right_penalty_area",
                    "left_goal",
                    "right_goal",
                ],
                show_labels=False,
            ),
        )

        # Center line cutting the field in half vertically
        rr.log(
            "/field/center_line",
            rr.LineStrips3D(
                [[[0.0, -field_width * 0.5, 0.0003], [0.0, field_width * 0.5, 0.0003]]],
                colors=[(255, 255, 255)],
                radii=[0.01],
            ),
        )

        # Center circle
        rr.log(
            "/field/center_circle",
            rr.Cylinders3D(
                fill_mode="MajorWireframe",
                centers=[(0.0, 0.0, 0.0003)],
                radii=[center_circle_radius],
                lengths=[0.0001],  # Thin length to act as a flat circle marker
                line_radii=[0.01],
                colors=[(255, 255, 255)],
                labels=["center_circle"],
                show_labels=False,
            ),
        )



def log_cmd_velocity_as_line(
    vx: float,
    vy: float,
    theta: float,
    *,
    robot_x: float,
    robot_y: float,
    robot_yaw: float,
) -> None:
    # this one log future prediction of where the robot will be as line strips
    if not _rerun_enabled():
        return
    _CMD_VEL_STEP_SEC = 0.05
    _CMD_VEL_HORIZON_SEC = 1.0

    yaw = robot_yaw
    my_points = [(robot_x, robot_y)]
    for _ in range(int(_CMD_VEL_HORIZON_SEC / _CMD_VEL_STEP_SEC)):
        vx_world = cos(yaw) * vx - sin(yaw) * vy
        vy_world = sin(yaw) * vx + cos(yaw) * vy
        last_x, last_y = my_points[-1]
        my_points.append(
            (
                last_x + vx_world * _CMD_VEL_STEP_SEC,
                last_y + vy_world * _CMD_VEL_STEP_SEC,
            )
        )
        yaw += theta * _CMD_VEL_STEP_SEC

    rr.log(
        "/behaviour/cmd_velocity_prediction",
        rr.LineStrips3D(
            strips=[[(pt[0], pt[1], 0.0) for pt in my_points]],
            colors=[(64, 255, 160)],
        ),
    )


def log_cmd_velocity(
    vx: float,
    vy: float,
    theta: float,
    *,
    robot_x: float,
    robot_y: float,
    robot_yaw: float,
) -> None:
    """Predict robot path from current cmd velocity as a single line strip."""
    if not _rerun_enabled():
        return

    log_cmd_velocity_as_line(vx, vy, theta, robot_x=robot_x, robot_y=robot_y, robot_yaw=robot_yaw)

    vx_world= cos(robot_yaw) * vx - sin(robot_yaw) * vy
    vy_world= sin(robot_yaw) * vx + cos(robot_yaw) * vy
    new_x = robot_x + vx_world
    new_y = robot_y + vy_world
    new_theta = robot_yaw + theta
    rr.log(
        "/behaviour/cmd_velocity",
        rr.Arrows3D(
            origins=[(robot_x, robot_y, 0.0), (new_x, new_y, 0.0)],
            vectors=[(vx_world, vy_world, 0.0), (cos(new_theta) * 0.4, sin(new_theta) * 0.4, 0.0)],
            colors=[(64, 255, 160)],
            labels=[f"vx: {vx:.2f} vy: {vy:.2f} vtheta: {theta:.2f}"],
        )
    )


def log_path_waypoints(wps):
    if not _rerun_enabled():
        return

    rr.log(
        "/behaviour/sm.pathplan",
        rr.LineStrips3D(
            strips=[[(pt[0], pt[1], 0.0) for pt in wps]], colors=[(255, 0, 0)]
        ),
    )


def log_sm_state(state):
    if not _rerun_enabled():
        return

    rr.log(
        "/behaviour/sm.state",
        rr.StateChange(state=str(state).replace("StateID.", "", 1)),
    )


def log_robot_to_ball(origin, vector):
    if not _rerun_enabled():
        return

    rr.log(
        "/behaviour/sm.kick.robot_to_ball",
        rr.Arrows3D(
            origins=[(*origin, 0.0)],
            vectors=[(*vector, 0.0)],
            radii=[0.025],
            colors=[(0, 128, 255)],
        ),
    )


def log_kick_target_world(ball, target, power):
    if not _rerun_enabled():
        return

    vector = [
        target[0] - ball[0],
        target[1] - ball[1],
        0.0
    ]

    rr.log(
        "/behaviour/sm.kick.locked_target_world",
        rr.Arrows3D(
            origins=[[*ball, 0.0]],
            vectors=[vector],
            colors=[(0, 0, 255)],
            labels=["Kick Power: " + str(round(power, 3))],
            show_labels=True,
        ),
    )

def log_field_features(robot_pose, field_features_relative_to_robot):
    if not _rerun_enabled():
        return
    robot_x, robot_y, robot_yaw = robot_pose
    points3d = []
    labels = []
    for feature in field_features_relative_to_robot:
        feature_x, feature_y, feature_label = feature
        feature_x_global = robot_x + cos(robot_yaw) * feature_x - sin(robot_yaw) * feature_y
        feature_y_global = robot_y + sin(robot_yaw) * feature_x + cos(robot_yaw) * feature_y
        points3d.append((feature_x_global, feature_y_global, 0.0))
        labels.append(feature_label)
    # Rerun expects colour entries to match point entries for this archetype.
    # An empty list is fine; mismatched lengths are the intermittent failure.
    rr.log(
        "/field/features",
        rr.Points3D(positions=points3d, colors=[(255, 0, 0)] * len(points3d), labels=labels),
    )

def log_ball_vision(global_x, global_y, confidence):
    # Vision can report a ball before localisation has a field pose.
    # Skip those partial points instead of sending None coordinates to Rerun.
    if not _rerun_enabled() or global_x is None or global_y is None:
        return
    rr.log(
        "/behaviour/wm.ball.vision",
        rr.Points3D(positions=[(global_x, global_y, 0.01)], colors=[(0, 0, 0)], radii=[0.10], labels=[f"conf{confidence:.2f}"]),
    )

def log_behaviour_tick_rate(tick_rate):
    if not _rerun_enabled():
        return
    rr.log(
        "/behaviour/tick_rate",
        rr.Scalars([tick_rate])
    )
def log_ground_fov_markers(global_corners):
    if not _rerun_enabled():
        return

    half_l = float(dims["length"]) / 2.0
    half_w = float(dims["width"]) / 2.0
    margin = 1.0

    # clamps the quad so it is not humungous ඞ on the vis
    trapezoid = []
    for x, y in global_corners:
        x = max(-half_l - margin, min(half_l + margin, x))
        y = max(-half_w - margin, min(half_w + margin, y))
        trapezoid.append((x, y, 0.0))

    # not a perfect quad clip, but good enough for what i am doing with opponent tracking
    if not trapezoid:
        return

    trapezoid.append(trapezoid[0])

    rr.log(
        "/behaviour/wm.ground_fov",
        rr.LineStrips3D(strips=[trapezoid], colors=[(255, 255, 0)]),
    )

def log_imu_data(r: float, p: float, y: float):
    if not _rerun_enabled():
        return
    
    rr.log("/imu/metrics/roll", rr.Scalars([r]))
    rr.log("/imu/metrics/pitch", rr.Scalars([p]))
    rr.log("/imu/metrics/yaw", rr.Scalars([y]))


def log_battery_voltage(voltage, current):
    if not _rerun_enabled():
        return
    rr.log(
        "/batteryinfo",
        rr.Scalars([voltage, current])
    )

def log_booster_joint_states(motors):
    if not _rerun_enabled():
        return
    temperatures = [m.temperature for m in motors]
    losts = [m.lost for m in motors]
    
    rr.log(
        "/low_state/joint_temp",
        rr.Scalars(temperatures),
    )
    rr.log(
        "/low_state/joint_lost",
        rr.Scalars(losts),
    )

def log_threatened_polygon(corners: np.array, threat: bool):
    if not _rerun_enabled() or len(corners) == 0:
        return
    color = (255, 0, 0) if threat else (0, 255, 0)
    rr.log(
        "/behaviour/threatened_polygon",
        rr.LineStrips3D(strips=[[(pt[0], pt[1], 0.0) for pt in corners]+[(corners[0][0], corners[0][1], 0.0)]], colors=[color]),
    )

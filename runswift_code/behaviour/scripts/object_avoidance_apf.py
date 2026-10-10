#!/usr/bin/env python3
"""
Simplified vision-based obstacle avoidance for B1 legged robot.

Core features only:
- Multiple obstacle tracking from vision
- Head-to-body frame transform
- Potential field with angular deadzone
- Simple three-zone behavior (clear, slow, retreat)

:class:`SimpleAvoidanceFilter` is the embeddable API (velocity in → velocity out). The ROS node
:class:`SimpleObstacleAvoidance` is a thin wrapper around it for standalone testing.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from math import atan2, cos, hypot, pi, sin
from typing import Iterable, List, Optional, Sequence, Tuple

import rclpy
from rclpy.node import Node
from rclpy.publisher import Publisher
from geometry_msgs.msg import Point, Pose, TransformStamped
from tf2_ros import StaticTransformBroadcaster
from vision_interface.msg import Detections
from visualization_msgs.msg import Marker, MarkerArray

from booster_robotics_sdk_python import B1LocoClient, ChannelFactory, RobotMode

@dataclass
class Obstacle:
    """Single obstacle in body frame (stamp_sec = last fusion update, wall clock)."""
    x: float
    y: float
    confidence: float
    stamp_sec: float


def wrap_angle_pi(angle: float) -> float:
    while angle > pi:
        angle -= 2.0 * pi
    while angle < -pi:
        angle += 2.0 * pi
    return angle


@dataclass
class BodyObstacle:
    """Obstacle pose in base (body) frame, horizontal plane."""

    x: float
    y: float
    confidence: float
    stamp_sec: float


def bearing_body_rad(x: float, y: float) -> float:
    return atan2(y, x)


def in_camera_horizontal_wedge(
    bearing_body_rad: float,
    head_yaw_rad: float,
    half_fov_rad: float,
) -> bool:
    """True if obstacle bearing in body frame lies inside camera horizontal wedge."""
    delta = wrap_angle_pi(bearing_body_rad - head_yaw_rad)
    return abs(delta) <= half_fov_rad


def fuse_body_obstacles(
    prev: Sequence[BodyObstacle],
    new_detections: Sequence[BodyObstacle],
    head_yaw_rad: float,
    now_sec: float,
    *,
    half_fov_rad: float,
    max_age_sec: float,
    merge_radius_m: float,
) -> List[BodyObstacle]:
    """Merge previous body-frame obstacles with new vision in same frame."""
    out: List[BodyObstacle] = [
        BodyObstacle(n.x, n.y, n.confidence, now_sec) for n in new_detections
    ]

    def matched_new(ox: float, oy: float) -> bool:
        return any(hypot(ox - n.x, oy - n.y) < merge_radius_m for n in new_detections)

    def matched_out(ox: float, oy: float) -> bool:
        return any(hypot(ox - o.x, oy - o.y) < merge_radius_m for o in out)

    for old in prev:
        if now_sec - old.stamp_sec > max_age_sec:
            continue
        d0 = hypot(old.x, old.y)
        if d0 < 1e-6:
            continue
        brg = bearing_body_rad(old.x, old.y)
        in_fov = in_camera_horizontal_wedge(brg, head_yaw_rad, half_fov_rad)

        if in_fov:
            # Vision is responsible for this sector this frame.
            if not matched_new(old.x, old.y):
                continue
            continue

        if matched_new(old.x, old.y):
            continue
        if matched_out(old.x, old.y):
            continue
        out.append(old)

    return out

# Added from local map (no longer exists)


@dataclass
class PFParams:
    """Potential field parameters."""
    # Repulsion
    k_rep: float = 0.9
    influence_radius: float = 1.
    min_distance: float = 0.2
    v_max: float = 0.55
    
    # Angular deadzone (frontal cone)
    deadzone_enabled: bool = True
    deadzone_halfwidth_rad: float = 0.6  # ±33°
    deadzone_max_range: float = 1.0
    deadzone_retreat_vx: float = 0.5
    deadzone_zero_lateral: bool = True
    
    # Three-tier zones
    hard_stop_distance: float = 0.2    # Freeze
    emergency_distance: float = 0.35    # Active retreat
    # influence_radius = soft steering


def head_yaw_from_pose(msg: Pose) -> float:
    """Extract head yaw about vertical axis from geometry_msgs/Pose orientation."""
    siny_cosp = 2.0 * (msg.orientation.w * msg.orientation.z + msg.orientation.x * msg.orientation.y)
    cosy_cosp = 1.0 - 2.0 * (msg.orientation.y ** 2 + msg.orientation.z ** 2)
    return atan2(siny_cosp, cosy_cosp)


def transform_head_to_body(x_head: float, y_head: float, head_yaw: float) -> Tuple[float, float]:
    c = cos(-head_yaw)
    s = sin(-head_yaw)
    return c * x_head - s * y_head, s * x_head + c * y_head


def potential_field(
    desired_vx: float,
    desired_vy: float,
    obstacles: Sequence[Obstacle],
    params: PFParams,
 #   ball_distance: float,
 #    goal_distance: float,
) -> Tuple[float, float, str]:
    """
    Planar velocity from desired + repulsion (body frame).

    Returns:
        (vx, vy, state) where state is CLEAR, SLOWING, EMERGENCY, or STOP.
    """
    if not obstacles:
        return desired_vx, desired_vy, "CLEAR"

    nearest_dist = min(hypot(o.x, o.y) for o in obstacles)

    if nearest_dist < params.hard_stop_distance:
        return 0.0, 0.0, "STOP"

    if nearest_dist < params.emergency_distance:

        #if ball_distance < 0.5:
        #    retreat_scale = 0.4  # Gentle retreat, not full
        #else:
        #    retreat_scale = 1.0
        retreat_scale = 1.0

        nearest_obs = min(obstacles, key=lambda o: hypot(o.x, o.y))
        nx = nearest_obs.x / max(nearest_dist, 0.01)
        ny = nearest_obs.y / max(nearest_dist, 0.01)
        return -nx * params.deadzone_retreat_vx * retreat_scale, -ny * params.deadzone_retreat_vx * retreat_scale, "EMERGENCY"

    # FIX 3: Compute desired direction for directional weighting
    # = atan2(desired_vy, desired_vx) if hypot(desired_vx, desired_vy) > 0.01 else 0.0
    # Compute desired direction unit vector
    desired_speed = hypot(desired_vx, desired_vy)
    if desired_speed > 0.01:
        desired_unit_x = desired_vx / desired_speed
        desired_unit_y = desired_vy / desired_speed
        desired_dir = atan2(desired_vy, desired_vx)
    else:
        desired_unit_x = 1.0
        desired_unit_y = 0.0
        desired_dir = 0.0

    fx = desired_vx
    fy = desired_vy

    for obs in obstacles:
        dist = hypot(obs.x, obs.y)
        if dist >= params.influence_radius or dist <= 1e-9:
            continue
        
        # FIX 3: Directional weighting - reduce repulsion for obstacles toward goal
        obs_bearing = atan2(obs.y, obs.x)
        angle_to_goal = abs(((obs_bearing - desired_dir + pi) % (2 * pi)) - pi)
        
        
        d_eff = max(dist, params.min_distance)
        inv_d = 1.0 / d_eff
        inv_r = 1.0 / params.influence_radius
        mag = params.k_rep * ((inv_d - inv_r) ** 2) 
        ux = -obs.x / d_eff
        uy = -obs.y / d_eff

        if angle_to_goal < 0.5:  # Within ~30° of desired direction
            # TANGENTIAL STEERING for frontal obstacles
            
            # Decompose repulsion into forward and lateral components
            forward_component = ux * desired_unit_x + uy * desired_unit_y
            lateral_x = ux - forward_component * desired_unit_x
            lateral_y = uy - forward_component * desired_unit_y
            
            lat_mag = hypot(lateral_x, lateral_y)
            
            if lat_mag < 0.01:
                # Obstacle is dead-center: force perpendicular direction
                # (rightward relative to desired direction)
                lateral_x = desired_unit_y
                lateral_y = -desired_unit_x
            else:
                # Normalize lateral vector for consistent scaling
                lateral_x /= lat_mag
                lateral_y /= lat_mag

            # Scale components differently:
            # - Reduce backward force (keep moving forward)
            # - Amplify lateral force (steer around)
            forward_scale = 0.3
            lateral_scale = 1.5
            
            fx += mag * (forward_component * forward_scale * desired_unit_x + lateral_x * lateral_scale)
            fy += mag * (forward_component * forward_scale * desired_unit_y + lateral_y * lateral_scale)
        else:
            # Standard repulsion for side/behind obstacles
            fx += mag * ux
            fy += mag * uy

    speed = hypot(fx, fy)
    if speed > params.v_max and speed > 1e-9:
        scale = params.v_max / speed
        fx *= scale
        fy *= scale

    deadzone_triggered = False
    deadzone_obs_side = 0.0
    
    if params.deadzone_enabled:
        for obs in obstacles:
            if obs.x <= 1e-6:
                continue
            bearing = abs(atan2(obs.y, obs.x))
            dist = hypot(obs.x, obs.y)
            if bearing < params.deadzone_halfwidth_rad and dist <= params.deadzone_max_range:
                deadzone_triggered = True
                deadzone_obs_side = 1.0 if obs.y > 0 else -1.0  # Left (+) or right (-)
                break

    if deadzone_triggered:
        # NEW: Instead of always backing straight up, try lateral first
        lateral_clearance = 0.4  # How far to side to check
        
        # Check if moving sideways would clear the deadzone
        can_dodge_left = all(
            not (obs.x > 0 and abs(atan2(obs.y - lateral_clearance, obs.x)) < params.deadzone_halfwidth_rad)
            for obs in obstacles if hypot(obs.x, obs.y) < params.deadzone_max_range
        )
        can_dodge_right = all(
            not (obs.x > 0 and abs(atan2(obs.y + lateral_clearance, obs.x)) < params.deadzone_halfwidth_rad)
            for obs in obstacles if hypot(obs.x, obs.y) < params.deadzone_max_range
        )

        if can_dodge_left or can_dodge_right:
            # Lateral escape: move sideways opposite to obstacle
            fx = max(fx, 0.0)  # Keep some forward momentum
            fy = -deadzone_obs_side * 0.4  # Dodge sideways
        else:
            # Fallback: back up straight
            fx = min(fx, -params.deadzone_retreat_vx)
            if params.deadzone_zero_lateral:
                fy = 0.0


    speed = hypot(fx, fy)
    if speed > params.v_max and speed > 1e-9:
        scale = params.v_max / speed
        fx *= scale
        fy *= scale

    state = "SLOWING" if nearest_dist < params.influence_radius else "CLEAR"
    return fx, fy, state


class SimpleAvoidanceFilter:
    """
    Reusable obstacle fusion + PF filter: desired body velocity in, safe velocity out.

    Use from ``ball_chasing_state_machine`` (or any controller) each control tick::

        filt.head_yaw = ...  # from /head_pose (rad, body-relative head yaw)
        filt.ingest_detections(msg, now_sec)
        vx, vy, vtheta, state = filt.filter_velocity(cmd_x, cmd_y, cmd_theta)

    Pass ``match_demo_vtheta=True`` only for the standalone demo behaviour (yaw from planar cmd).
    """

    def __init__(
        self,
        pf_params: PFParams,
        *,
        vision_min_confidence: float = 30.0,
        vision_obstacle_labels: Optional[Iterable[str]] = None,
        cam_horizontal_fov_deg: float = 69.4,
        max_age_sec: float = 1.0,
        merge_radius_m: float = 0.3,
    ) -> None:
        self.pf_params = pf_params
        self.vision_min_confidence = vision_min_confidence
        labels = {"person", "opponent"} if vision_obstacle_labels is None else {x.lower() for x in vision_obstacle_labels}
        self.vision_obstacle_labels = labels
        self.cam_horizontal_fov_deg = cam_horizontal_fov_deg
        self.max_age_sec = max_age_sec
        self.merge_radius_m = merge_radius_m
        self.head_yaw = 0.0
        self.obstacles: List[Obstacle] = []
        self.viz_new_body: List[Tuple[float, float]] = []

    def ingest_detections(self, msg: Detections, now_sec: float) -> None:
        """Fuse vision into ``self.obstacles`` (body frame); updates ``viz_new_body`` for RViz."""
        min_conf = self.vision_min_confidence
        valid_labels = self.vision_obstacle_labels
        new_obstacles: List[Obstacle] = []

        for obj in msg.detected_objects:
            if float(obj.confidence) < min_conf:
                continue
            if len(obj.position_projection) < 2:
                continue
            if obj.label.lower() not in valid_labels:
                continue
            xh = float(obj.position_projection[0])
            yh = float(obj.position_projection[1])
            x_body, y_body = transform_head_to_body(xh, yh, self.head_yaw)
            new_obstacles.append(
                Obstacle(x=x_body, y=y_body, confidence=float(obj.confidence), stamp_sec=now_sec)
            )

        self.viz_new_body = [(o.x, o.y) for o in new_obstacles]
        half_fov_rad = 0.5 * self.cam_horizontal_fov_deg * pi / 180.0
        prev = [BodyObstacle(o.x, o.y, o.confidence, o.stamp_sec) for o in self.obstacles]
        neu = [BodyObstacle(o.x, o.y, o.confidence, o.stamp_sec) for o in new_obstacles]
        fused = fuse_body_obstacles(
            prev,
            neu,
            self.head_yaw,
            now_sec,
            half_fov_rad=half_fov_rad,
            max_age_sec=self.max_age_sec,
            merge_radius_m=self.merge_radius_m,
        )
        self.obstacles = [Obstacle(x=m.x, y=m.y, confidence=m.confidence, stamp_sec=m.stamp_sec) for m in fused]

    def filter_velocity(
        self,
        desired_vx: float,
        desired_vy: float,
        desired_vtheta: float,
    #    ball_distance: float,
        *,
        match_demo_vtheta: bool = False, #False
        vtheta_motion_gain: float = 0.15,
        vtheta_motion_speed_threshold: float = 0.3,
    ) -> Tuple[float, float, float, str]:
        """
        Apply potential field to ``(desired_vx, desired_vy)``; set yaw rate from caller or demo rule.

        When ``match_demo_vtheta`` is False (default for skills like ball chase), ``desired_vtheta``
        is passed through except in STOP (all zeros).
        """
        vx, vy, state = potential_field(desired_vx, desired_vy, self.obstacles, self.pf_params)
        if state == "STOP":
            return 0.0, 0.0, 0.0, state
        if match_demo_vtheta:
            if hypot(vx, vy) > vtheta_motion_speed_threshold:
                vtheta = atan2(vy, vx) * vtheta_motion_gain
            else:
                vtheta = 0.0
        else:
            vtheta = float(desired_vtheta) 
        return float(vx), float(vy), vtheta, state


class SimpleObstacleAvoidance(Node):
    def __init__(self) -> None:
        super().__init__("simple_obstacle_avoidance")
        
        # Parameters
        self.declare_parameter("cruise_vx", 0.5)
        self.declare_parameter("cruise_vy", 0.0)
        
        # PF parameters
        self.declare_parameter("pf.k_rep", 0.9)
        self.declare_parameter("pf.influence_radius", 1.)
        self.declare_parameter("pf.v_max", 0.55)
        self.declare_parameter("pf.deadzone_halfwidth_deg", 33.0)
        self.declare_parameter("pf.deadzone_max_range", 1.0)
        self.declare_parameter("pf.deadzone_retreat_vx", 0.5)
        
        # Zone distances
        self.declare_parameter("zone.hard_stop", 0.35)
        self.declare_parameter("zone.emergency", 0.45)
        
        # Vision filtering
        self.declare_parameter("vision.min_confidence", 30.0)
        self.declare_parameter("vision.obstacle_labels", ["Person", "Opponent"])
        self.declare_parameter("vision.max_age_sec", 1.0)
        self.declare_parameter("vision.cam_horizontal_fov_deg", 69.4)
        self.declare_parameter("vision.merge_radius_m", 0.3)
        
        # RViz2: red = current detections, orange = fused memory, wedge = camera FOV in body frame.
        # Markers use viz.frame_id (not base_link). Identity static TF parent->child attaches that
        # frame to your TF tree; set viz.static_tf_parent to a frame coincident with robot body.
        self.declare_parameter("viz.enabled", False) #True
        self.declare_parameter("viz.markers_topic", "/simple_obstacle_avoidance/viz")
        self.declare_parameter("viz.frame_id", "simple_obstacle_avoidance")
        self.declare_parameter("viz.static_tf_parent", "odom")
        self.declare_parameter("viz.publish_static_tf", True)
        self.declare_parameter("viz.wedge_range_m", 3.0)
        self.declare_parameter("viz.wedge_arc_segments", 36)
        self.declare_parameter("viz.marker_radius", 0.12)
        self.declare_parameter("viz.marker_height", 0.22)
        self.declare_parameter("viz.fov_line_width", 0.04)
        
        # Head tracking
        self.declare_parameter("head.track_motion", True)
        self.declare_parameter("head.pitch_default", 0.36)
        
        self._filter = SimpleAvoidanceFilter(
            PFParams(
                k_rep=float(self.get_parameter("pf.k_rep").value),
                influence_radius=float(self.get_parameter("pf.influence_radius").value),
                v_max=float(self.get_parameter("pf.v_max").value),
                deadzone_halfwidth_rad=float(self.get_parameter("pf.deadzone_halfwidth_deg").value) * pi / 180.0,
                deadzone_max_range=float(self.get_parameter("pf.deadzone_max_range").value),
                deadzone_retreat_vx=float(self.get_parameter("pf.deadzone_retreat_vx").value),
                hard_stop_distance=float(self.get_parameter("zone.hard_stop").value),
                emergency_distance=float(self.get_parameter("zone.emergency").value),
            ),
            vision_min_confidence=float(self.get_parameter("vision.min_confidence").value),
            vision_obstacle_labels=self.get_parameter("vision.obstacle_labels").value,
            cam_horizontal_fov_deg=float(self.get_parameter("vision.cam_horizontal_fov_deg").value),
            max_age_sec=float(self.get_parameter("vision.max_age_sec").value),
            merge_radius_m=float(self.get_parameter("vision.merge_radius_m").value),
        )
        
        # SDK client
        self.client = B1LocoClient()
        self.client.Init()
        time.sleep(1)
        self._ensure_walking()
        
        # Subscriptions
        self.create_subscription(
            Detections,
            "/booster_vision/detection",
            self._on_detections,
            10
        )
        self.create_subscription(
            Pose,
            "/head_pose",
            self._on_head_pose,
            10
        )
        
        self._pub_viz: Optional[Publisher] = None
        self._static_tf_broadcaster: Optional[StaticTransformBroadcaster] = None
        if bool(self.get_parameter("viz.enabled").value):
            self._pub_viz = self.create_publisher(
                MarkerArray,
                str(self.get_parameter("viz.markers_topic").value),
                10,
            )
            if bool(self.get_parameter("viz.publish_static_tf").value):
                self._static_tf_broadcaster = StaticTransformBroadcaster(self)
                self._send_viz_static_tf()
        
        # Control timer
        self.create_timer(0.05, self._control_loop)
        
        self.get_logger().info("Simple obstacle avoidance started")
    
    def _send_viz_static_tf(self) -> None:
        """Publish identity TF so RViz can show markers without base_link in the tree."""
        if self._static_tf_broadcaster is None:
            return
        parent = str(self.get_parameter("viz.static_tf_parent").value)
        child = str(self.get_parameter("viz.frame_id").value)
        tf = TransformStamped()
        tf.header.stamp = self.get_clock().now().to_msg()
        tf.header.frame_id = parent
        tf.child_frame_id = child
        tf.transform.rotation.w = 1.0
        self._static_tf_broadcaster.sendTransform(tf)
        self.get_logger().info(
            f"Viz TF (identity): '{parent}' -> '{child}'. "
            "Parent should match the body frame used by vision projections."
        )
    
    def _ensure_walking(self) -> None:
        """Get robot into walking mode."""
        try:
            self.client.GetUp()
            time.sleep(5)
            self.client.ChangeMode(RobotMode.kWalking)
            time.sleep(1)
            self.get_logger().info("Robot in walking mode")
        except Exception as e:
            self.get_logger().warning(f"Mode setup failed: {e}")
    
    def _sync_filter_vision_params(self) -> None:
        f = self._filter
        f.vision_min_confidence = float(self.get_parameter("vision.min_confidence").value)
        f.vision_obstacle_labels = {str(x).lower() for x in self.get_parameter("vision.obstacle_labels").value}
        f.cam_horizontal_fov_deg = float(self.get_parameter("vision.cam_horizontal_fov_deg").value)
        f.max_age_sec = float(self.get_parameter("vision.max_age_sec").value)
        f.merge_radius_m = float(self.get_parameter("vision.merge_radius_m").value)

    def _on_head_pose(self, msg: Pose) -> None:
        """Track head yaw for coordinate transforms."""
        self._filter.head_yaw = head_yaw_from_pose(msg)
    
    def _on_detections(self, msg: Detections) -> None:
        """Update obstacle list from vision."""
        self._sync_filter_vision_params()
        self._filter.ingest_detections(msg, self.now_sec())

    def _publish_avoidance_viz(self) -> None:
        """RViz2: red = this frame's detections, orange = memory tracks, line = horizontal FOV wedge."""
        if self._pub_viz is None:
            return
        stamp = self.get_clock().now().to_msg()
        frame_id = str(self.get_parameter("viz.frame_id").value)
        R = float(self.get_parameter("viz.wedge_range_m").value)
        fov_deg = float(self.get_parameter("vision.cam_horizontal_fov_deg").value)
        half_fov = 0.5 * fov_deg * pi / 180.0
        n_arc = max(4, int(self.get_parameter("viz.wedge_arc_segments").value))
        merge_r = float(self.get_parameter("vision.merge_radius_m").value)
        mr = float(self.get_parameter("viz.marker_radius").value)
        mh = float(self.get_parameter("viz.marker_height").value)
        lw = float(self.get_parameter("viz.fov_line_width").value)
        hy = self._filter.head_yaw

        arr = MarkerArray()
        clear = Marker()
        clear.header.frame_id = frame_id
        clear.header.stamp = stamp
        clear.ns = "simple_obstacle_avoidance"
        clear.id = 0
        clear.action = Marker.DELETEALL
        arr.markers.append(clear)

        def _pt(x: float, y: float, z: float = 0.05) -> Point:
            p = Point()
            p.x, p.y, p.z = float(x), float(y), float(z)
            return p

        # FOV boundary in body frame: boresight = hy (matches local_map wedge)
        fov_strip = Marker()
        fov_strip.header.frame_id = frame_id
        fov_strip.header.stamp = stamp
        fov_strip.ns = "simple_obstacle_avoidance"
        fov_strip.id = 1
        fov_strip.type = Marker.LINE_STRIP
        fov_strip.action = Marker.ADD
        fov_strip.scale.x = lw
        fov_strip.pose.orientation.w = 1.0
        fov_strip.color.r = 0.2
        fov_strip.color.g = 0.85
        fov_strip.color.b = 1.0
        fov_strip.color.a = 0.95
        th0 = hy - half_fov
        th1 = hy + half_fov
        fov_strip.points.append(_pt(0.0, 0.0, 0.02))
        fov_strip.points.append(_pt(R * cos(th0), R * sin(th0), 0.02))
        for i in range(1, n_arc):
            t = th0 + (th1 - th0) * (i / n_arc)
            fov_strip.points.append(_pt(R * cos(t), R * sin(t), 0.02))
        fov_strip.points.append(_pt(R * cos(th1), R * sin(th1), 0.02))
        fov_strip.points.append(_pt(0.0, 0.0, 0.02))
        arr.markers.append(fov_strip)

        # Red: raw body-frame detections from last vision message
        for i, (nx, ny) in enumerate(self._filter.viz_new_body):
            m = Marker()
            m.header.frame_id = frame_id
            m.header.stamp = stamp
            m.ns = "simple_obstacle_avoidance"
            m.id = 10 + i
            m.type = Marker.CYLINDER
            m.action = Marker.ADD
            m.pose.position.x = float(nx)
            m.pose.position.y = float(ny)
            m.pose.position.z = float(mh) * 0.5 + 0.05
            m.pose.orientation.w = 1.0
            m.scale.x = m.scale.y = float(max(mr * 2.0, 0.05))
            m.scale.z = float(max(mh, 0.05))
            m.color.r = 1.0
            m.color.g = 0.05
            m.color.b = 0.05
            m.color.a = 0.9
            arr.markers.append(m)

        # Orange: fused obstacles not matched to current detections (memory)
        mid = 0
        for o in self._filter.obstacles:
            matched = any(hypot(o.x - nx, o.y - ny) < merge_r for nx, ny in self._filter.viz_new_body)
            if matched:
                continue
            m = Marker()
            m.header.frame_id = frame_id
            m.header.stamp = stamp
            m.ns = "simple_obstacle_avoidance"
            m.id = 200 + mid
            mid += 1
            m.type = Marker.CYLINDER
            m.action = Marker.ADD
            m.pose.position.x = float(o.x)
            m.pose.position.y = float(o.y)
            m.pose.position.z = float(mh) * 0.5 + 0.05
            m.pose.orientation.w = 1.0
            m.scale.x = m.scale.y = float(max(mr * 2.0, 0.05))
            m.scale.z = float(max(mh, 0.05))
            m.color.r = 1.0
            m.color.g = 0.55
            m.color.b = 0.05
            m.color.a = 0.85
            arr.markers.append(m)

        self._pub_viz.publish(arr)
    
    def _get_pf_params(self) -> PFParams:
        """Build PF params from ROS parameters."""
        return PFParams(
            k_rep=float(self.get_parameter("pf.k_rep").value),
            influence_radius=float(self.get_parameter("pf.influence_radius").value),
            v_max=float(self.get_parameter("pf.v_max").value),
            deadzone_halfwidth_rad=float(self.get_parameter("pf.deadzone_halfwidth_deg").value) * 3.14159 / 180.0,
            deadzone_max_range=float(self.get_parameter("pf.deadzone_max_range").value),
            deadzone_retreat_vx=float(self.get_parameter("pf.deadzone_retreat_vx").value),
            hard_stop_distance=float(self.get_parameter("zone.hard_stop").value),
            emergency_distance=float(self.get_parameter("zone.emergency").value),
        )
    
    def _control_loop(self) -> None:
        """Main control loop: compute velocity and command robot."""
        self._filter.pf_params = self._get_pf_params()
        self._sync_filter_vision_params()
        desired_vx = float(self.get_parameter("cruise_vx").value)
        desired_vy = float(self.get_parameter("cruise_vy").value)
        vx, vy, vtheta, state = self._filter.filter_velocity(
            desired_vx, desired_vy, 0.0, match_demo_vtheta=True
        )

        print(f"vx: {vx}, vy: {vy}")
        
        # Command robot
        try:
            self.client.Move(float(vx), float(vy), float(vtheta))
        except Exception as e:
            self.get_logger().error(f"Move failed: {e}", throttle_duration_sec=5.0)
            return
        
        # Head tracking: point head in motion direction
        if self.get_parameter("head.track_motion").value and hypot(vx, vy) > 0.05:
            head_pitch = float(self.get_parameter("head.pitch_default").value)
            # Head yaw relative to body (body already rotating via vtheta)
            head_yaw_target = 0.0  # Keep head aligned with body
            
            # Smooth step toward target
            head_yaw_error = head_yaw_target - self._filter.head_yaw
            head_yaw_cmd = self._filter.head_yaw + head_yaw_error * 0.3
            
            try:
                self.client.RotateHead(head_pitch, head_yaw_cmd)
            except Exception:
                pass
        
        self._publish_avoidance_viz()

        # Logging
        now = self.now_sec()
        obs = self._filter.obstacles
        nearest = min((hypot(o.x, o.y) for o in obs), default=999.0)
        mem_age = max((now - o.stamp_sec for o in obs), default=0.0)
        hy = self._filter.head_yaw
        self.get_logger().info(
            f"{state}: obstacles={len(obs)} nearest={nearest:.2f}m "
            f"cmd=({vx:+.2f},{vy:+.2f},{vtheta:+.2f}) "
            f"head_yaw={hy*180/3.14:.1f}° mem_age≤{mem_age:.2f}s",
            throttle_duration_sec=0.5
        )
    
    def now_sec(self) -> float:
        """Current time in seconds."""
        return float(self.get_clock().now().nanoseconds) * 1e-9


def main() -> None:
    ChannelFactory.Instance().Init(0)
    rclpy.init()
    
    node = SimpleObstacleAvoidance()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.client.Move(0.0, 0.0, 0.0)
        except Exception:
            pass
        
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()

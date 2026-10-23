"""First-strike metrics, retaining misses and stopping before a second contact."""

import math

import numpy as np


class StrikeMeasurement:
    def __init__(self, heading):
        self.heading = heading
        self.direction = np.array([math.cos(heading), math.sin(heading)])
        self.side = np.array([-math.sin(heading), math.cos(heading)])
        self.last_contact = self.last_foot = -float("inf")
        self.contact_bouts = 0
        self.launch = self.origin = self.launch_velocity = None
        self.foot_launch = False
        self.peak_speed = 0.0
        self.peak_velocity = None
        self.max_forward = self.max_planar = 0.0
        self.crossing_error = None
        self.window_end = None
        self.previous_point = None
        self.previous_velocity = np.zeros(2)
        self.initial_velocity = None
        self.first_contact = None
        self.strongest_speed = 0.0
        self.strongest_velocity = None
        self.strongest_time = None
        self.first_fast_foot_launch = None

    def update(self, t, ball, velocity, contact, foot_contact):
        ball = np.asarray(ball)[:2]
        velocity = np.asarray(velocity)[:2]
        if self.initial_velocity is None:
            self.initial_velocity = velocity.copy()
        new_contact = contact and t - self.last_contact > 0.2
        if new_contact:
            self.contact_bouts += 1
            if self.first_contact is None:
                self.first_contact = t
            if self.launch is not None and self.window_end is None:
                self.window_end = t
        if contact:
            self.last_contact = t
        if foot_contact:
            self.last_foot = t
        speed = float(np.linalg.norm(velocity))
        if (
            t - self.last_foot <= 0.15
            and speed >= 0.5
            and np.linalg.norm(velocity - self.initial_velocity) >= 0.3
        ):
            if speed > self.strongest_speed:
                self.strongest_speed = speed
                self.strongest_velocity, self.strongest_time = velocity.copy(), t
            if speed >= 2 and self.first_fast_foot_launch is None:
                self.first_fast_foot_launch = t
        if (
            self.launch is None
            and t - self.last_contact <= 0.15
            and speed >= 0.5
            and np.linalg.norm(velocity - self.initial_velocity) >= 0.3
        ):
            self.launch, self.origin = t, ball.copy()
            self.launch_velocity = velocity.copy()
            self.foot_launch = t - self.last_foot <= 0.15
        if self.launch is not None and self.window_end is None:
            if t <= self.launch + 0.2 and speed > self.peak_speed:
                self.peak_speed, self.peak_velocity = speed, velocity.copy()
            point = ball - self.origin
            forward = float(point @ self.direction)
            lateral = float(point @ self.side)
            self.max_forward = max(self.max_forward, forward)
            self.max_planar = max(self.max_planar, float(np.linalg.norm(point)))
            if self.crossing_error is None and self.previous_point is not None:
                f0, l0 = self.previous_point
                if f0 < 3 <= forward:
                    ratio = (3 - f0) / (forward - f0)
                    self.crossing_error = l0 + ratio * (lateral - l0)
            self.previous_point = (forward, lateral)
        self.previous_velocity = velocity.copy()

    def result(self, survived):
        error = None
        if self.peak_velocity is not None:
            angle = (
                math.atan2(self.peak_velocity[1], self.peak_velocity[0]) - self.heading
            )
            error = math.degrees(math.atan2(math.sin(angle), math.cos(angle)))
        aimed = bool(self.foot_launch and error is not None and abs(error) <= 15)
        strongest_error = None
        if self.strongest_velocity is not None:
            angle = (
                math.atan2(self.strongest_velocity[1], self.strongest_velocity[0])
                - self.heading
            )
            strongest_error = math.degrees(math.atan2(math.sin(angle), math.cos(angle)))
        return {
            "first_contact_s": self.first_contact,
            "launch_s": self.launch,
            "foot_launch": self.foot_launch,
            "peak_launch_speed_m_s": self.peak_speed,
            "launch_heading_error_deg": error,
            "on_direction_launch": aimed,
            "first_strike_forward_m": self.max_forward,
            "first_strike_planar_m": self.max_planar,
            "target_plane_lateral_error_m": self.crossing_error,
            "target_plane_hit": bool(
                self.foot_launch
                and self.crossing_error is not None
                and abs(self.crossing_error) <= 0.5
            ),
            "successful_trial": bool(aimed and survived),
            "contact_bouts": self.contact_bouts,
            "first_strike_ended_by_recontact_s": self.window_end,
            "travel_censored_by_fall": bool(
                not survived and self.launch is not None and self.window_end is None
            ),
            "strongest_foot_linked_speed_m_s": self.strongest_speed,
            "strongest_foot_linked_heading_error_deg": strongest_error,
            "strongest_foot_linked_time_s": self.strongest_time,
            "first_2mps_foot_launch_s": self.first_fast_foot_launch,
        }

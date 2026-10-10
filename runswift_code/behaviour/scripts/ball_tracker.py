"""Filtered global ball state from BallMeasurement stream."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ball_physics import (
    DEFAULT_BALL_FRICTION,
    propagate_ball_position,
    propagate_ball_position_and_velocity,
    velocity_after_distance_for_time,
)

from runswift_types import BallMeasurement

MIN_SPEED_MPS = 0.08
MIN_MEASUREMENTS_FOR_VELOCITY = 4
MIN_MEASUREMENTS_BEFORE_INFERRED_V = 3
MIN_MEAS_DT_SEC = 0.2
MAX_MEAS_DT_SEC = 2.0
DEFAULT_MAX_COAST_SEC = 3.0
MAX_INFERRED_SPEED_MPS = 6.5
STATIONARY_DISPLACEMENT_SPEED_MPS = 0.15

VISION_MEASUREMENT_STD_M = 0.15
COMMS_MEASUREMENT_STD_M = 0.35
PROCESS_NOISE_POS = 0.02
PROCESS_NOISE_VEL = 0.05


@dataclass
class BallTracker:
    """Global rolling-ball Kalman-style tracker fed by BallMeasurement."""

    friction: float = DEFAULT_BALL_FRICTION
    max_coast_sec: float = DEFAULT_MAX_COAST_SEC
    min_speed_mps: float = MIN_SPEED_MPS

    position: np.ndarray = field(default_factory=lambda: np.zeros(2))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(2))
    covariance: np.ndarray = field(default_factory=lambda: np.eye(4))
    last_update_sec: float = 0.0
    last_measurement_sec: float | None = None
    last_measurement_position: np.ndarray | None = None
    num_measurements: int = 0
    valid: bool = False

    _last_source_key: str | None = None

    def source_key(self, candidate: BallMeasurement) -> str:
        if candidate.source == "comms_peer" and candidate.player_id is not None:
            return f"comms_peer:{candidate.player_id}"
        return candidate.source

    def measurement_std(self, source: str) -> float:
        return COMMS_MEASUREMENT_STD_M if source == "comms_peer" else VISION_MEASUREMENT_STD_M

    def _reset_at(
        self,
        position: np.ndarray,
        measurement_sec: float,
    ) -> None:
        self.position = np.asarray(position, dtype=float).copy()
        self.velocity = np.zeros(2, dtype=float)
        self.covariance = np.diag([0.1, 0.1, 1.0, 1.0])
        self.last_update_sec = measurement_sec
        self.last_measurement_sec = measurement_sec
        self.last_measurement_position = self.position.copy()
        self.num_measurements = 1
        self.valid = True

    def _predict_to(self, target_sec: float) -> None:
        if not self.valid:
            return
        dt = target_sec - self.last_update_sec
        if dt <= 0.0:
            return
        propagate_ball_position_and_velocity(
            self.position,
            self.velocity,
            dt,
            self.friction,
        )
        self._add_process_noise(dt)
        self.last_update_sec = target_sec
        if float(np.linalg.norm(self.velocity)) < self.min_speed_mps:
            self.velocity[:] = 0.0

    def _add_process_noise(self, dt: float) -> None:
        q_pos = PROCESS_NOISE_POS * dt
        q_vel = PROCESS_NOISE_VEL * dt
        self.covariance[0, 0] += q_pos
        self.covariance[1, 1] += q_pos
        self.covariance[2, 2] += q_vel
        self.covariance[3, 3] += q_vel

    def _kf_position_update(
        self,
        measurement: np.ndarray,
        measurement_std: float,
    ) -> None:
        z = np.asarray(measurement, dtype=float)
        r_var = measurement_std * measurement_std
        p_pos = self.covariance[:2, :2]
        s = p_pos + np.eye(2) * r_var
        k = self.covariance[:, :2] @ np.linalg.inv(s)
        innovation = z - self.position
        state = np.concatenate([self.position, self.velocity])
        state += k @ innovation
        self.position = state[:2]
        self.velocity = state[2:]
        self.covariance -= k @ self.covariance[:2, :]

    def _apply_inferred_velocity(self, inferred_v: np.ndarray) -> None:
        speed = float(np.linalg.norm(inferred_v))
        if speed < self.min_speed_mps:
            return
        if self.num_measurements < MIN_MEASUREMENTS_BEFORE_INFERRED_V:
            return
        if speed > MAX_INFERRED_SPEED_MPS:
            inferred_v = inferred_v * (MAX_INFERRED_SPEED_MPS / speed)
        self.velocity = inferred_v

    def _zero_velocity_if_stationary(
        self,
        meas: np.ndarray,
        dt_meas: float,
    ) -> None:
        if (
            self.last_measurement_position is None
            or dt_meas < MIN_MEAS_DT_SEC
            or dt_meas > MAX_MEAS_DT_SEC
        ):
            return

        displacement_speed = float(
            np.linalg.norm(meas - self.last_measurement_position) / dt_meas
        )
        if displacement_speed >= STATIONARY_DISPLACEMENT_SPEED_MPS:
            return

        if float(np.linalg.norm(self.velocity)) < self.min_speed_mps:
            return

        self.velocity[:] = 0.0

    def _fuse_measurement(
        self,
        measurement: np.ndarray,
        measurement_sec: float,
        measurement_std: float,
        now_sec: float,
    ) -> None:
        meas = np.asarray(measurement, dtype=float)
        dt_meas = 0.0

        if (
            self.last_measurement_position is not None
            and self.last_measurement_sec is not None
        ):
            dt_meas = measurement_sec - self.last_measurement_sec
            if dt_meas < 0.0:
                return
            if dt_meas <= MAX_MEAS_DT_SEC:
                inferred_v = velocity_after_distance_for_time(
                    self.last_measurement_position,
                    meas,
                    dt_meas,
                    self.friction,
                )
                self._apply_inferred_velocity(inferred_v)

        self._kf_position_update(meas, measurement_std)
        self._zero_velocity_if_stationary(meas, dt_meas)

        if float(np.linalg.norm(self.velocity)) < self.min_speed_mps:
            self.velocity[:] = 0.0

        self.last_measurement_sec = measurement_sec
        self.last_measurement_position = meas.copy()
        self.num_measurements += 1

    def update(
        self,
        now_sec: float,
        candidate: BallMeasurement | None,
    ) -> None:
        if candidate is not None and candidate.ball.has_global_position():
            ball = candidate.ball
            meas = np.array([ball.global_x, ball.global_y], dtype=float)
            meas_sec = (
                candidate.last_seen_sec
                if candidate.last_seen_sec is not None
                else now_sec
            )
            source_key = self.source_key(candidate)
            meas_std = self.measurement_std(candidate.source)

            if not self.valid or source_key != self._last_source_key:
                self._reset_at(meas, meas_sec)
                self._last_source_key = source_key
            else:
                if (
                    self.last_measurement_sec is not None
                    and meas_sec >= self.last_measurement_sec
                ):
                    dt_meas = meas_sec - self.last_measurement_sec
                    if dt_meas < MIN_MEAS_DT_SEC:
                        if self.last_update_sec < now_sec:
                            self._predict_to(now_sec)
                        return
                if meas_sec > self.last_update_sec + 1e-6:
                    self._predict_to(meas_sec)
                elif meas_sec + 1e-6 < self.last_measurement_sec:
                    if self.last_update_sec < now_sec:
                        self._predict_to(now_sec)
                    return
                self._fuse_measurement(meas, meas_sec, meas_std, now_sec)

            if self.last_update_sec < now_sec:
                self._predict_to(now_sec)
            return

        if not self.valid:
            return

        if self.last_update_sec < now_sec:
            self._predict_to(now_sec)

        if self.last_measurement_sec is None:
            self.valid = False
            return

        age = now_sec - self.last_measurement_sec
        if age > self.max_coast_sec:
            self.valid = False

    def effective_velocity(self) -> np.ndarray:
        if self.num_measurements < MIN_MEASUREMENTS_FOR_VELOCITY:
            return np.zeros(2, dtype=float)
        return self.velocity.copy()

    def position_at(self, dt: float) -> tuple[float, float]:
        if not self.valid:
            return (0.0, 0.0)
        p = self.position.copy()
        v = self.effective_velocity()
        if dt > 0.0:
            p = propagate_ball_position(p, v, dt, self.friction)
        return float(p[0]), float(p[1])

    def velocity_at(self) -> tuple[float, float]:
        if not self.valid:
            return (0.0, 0.0)
        v = self.effective_velocity()
        return float(v[0]), float(v[1])

    def apply_fused_estimate(
        self,
        *,
        position: np.ndarray,
        velocity: np.ndarray,
        estimate_time_sec: float,
        now_sec: float,
        valid: bool,
    ) -> None:
        """Set state from team fusion output and propagate to now_sec."""
        if not valid:
            self.valid = False
            return

        self.position = np.asarray(position, dtype=float).copy()
        self.velocity = np.asarray(velocity, dtype=float).copy()
        self.covariance = np.diag([0.1, 0.1, 1.0, 1.0])
        self.last_measurement_sec = estimate_time_sec
        self.last_measurement_position = self.position.copy()
        self.last_update_sec = estimate_time_sec
        self.num_measurements = max(self.num_measurements, MIN_MEASUREMENTS_FOR_VELOCITY)
        self.valid = True
        self._last_source_key = "fused"

        if now_sec > self.last_update_sec + 1e-6:
            self._predict_to(now_sec)

        if float(np.linalg.norm(self.velocity)) < self.min_speed_mps:
            self.velocity[:] = 0.0

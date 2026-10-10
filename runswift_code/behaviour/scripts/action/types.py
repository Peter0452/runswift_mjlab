"""Typed intent records for the action arbiter.

Skills write a ``MotionCommand`` each tick. The arbiter turns that plus an
``ArbiterInput`` into one vendor-facing body send (or a safety override).
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field


@dataclass
class MotionCommand:
    """Per-tick body velocity and head target selected by behaviour."""

    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0
    head_pitch: float = 0.45
    head_yaw: float = 0.0
    head_pitch_speed: float = 1.2
    head_yaw_speed: float = 1.2
    avoidance_applied: bool = False
    recovery_attempt_id: str | None = None
    kick_active: bool = False
    kick_direction: float = 0.0
    kick_power: float = 0.0
    kick_ball_x: float = 0.0
    kick_ball_y: float = 0.0
    _head_lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def reset(self) -> None:
        """Reset body, kick, and avoid flags; head targets persist for the head timer."""
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.avoidance_applied = False
        self.clear_kick()
        self.recovery_attempt_id = None

    def stop_body(self) -> None:
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

    def set_body(self, x: float, y: float, theta: float) -> None:
        self.x = x
        self.y = y
        self.theta = theta
        self.avoidance_applied = False

    def set_kick(
        self,
        direction: float,
        power: float,
        ball_x: float,
        ball_y: float,
    ) -> None:
        self.kick_active = True
        self.kick_direction = float(direction)
        self.kick_power = float(power)
        self.kick_ball_x = float(ball_x)
        self.kick_ball_y = float(ball_y)

    def clear_kick(self) -> None:
        self.kick_active = False
        self.kick_direction = 0.0
        self.kick_power = 0.0
        self.kick_ball_x = 0.0
        self.kick_ball_y = 0.0

    def set_head(
        self,
        pitch: float,
        yaw: float,
        speed_pitch: float = 1.2,
        speed_yaw: float = 1.2,
    ) -> None:
        with self._head_lock:
            self.head_pitch = pitch
            self.head_yaw = yaw
            self.head_pitch_speed = speed_pitch
            self.head_yaw_speed = speed_yaw

    def set_head_speed(
        self,
        speed_pitch: float | None = None,
        speed_yaw: float | None = None,
    ) -> None:
        with self._head_lock:
            if speed_pitch is not None:
                self.head_pitch_speed = speed_pitch
            if speed_yaw is not None:
                self.head_yaw_speed = speed_yaw

    def head_targets(self) -> tuple[float, float, float, float]:
        with self._head_lock:
            return (
                self.head_pitch,
                self.head_yaw,
                self.head_pitch_speed,
                self.head_yaw_speed,
            )


@dataclass(frozen=True)
class VelocityLimits:
    vx: float
    vy: float
    vtheta: float


@dataclass(frozen=True)
class HeadLimits:
    pitch_min: float
    pitch_max: float
    yaw_min: float
    yaw_max: float
    max_dt_sec: float = 0.05


@dataclass(frozen=True)
class ArbiterInput:
    """Per-tick safety and policy flags. No vendor types."""

    has_fallen: bool = False
    recovery_available: bool = False
    is_stopped: bool = False
    is_penalised: bool = False
    force_stop: bool = False
    skip_body: bool = False
    suppress_body: bool = False


@dataclass(frozen=True)
class ArbiterResult:
    """What the arbiter did this tick, for diagnostics and ROS publish."""

    body_move_sent: bool
    published_cmd: tuple[float, float, float] | None
    reason: str
    recovered: bool = False

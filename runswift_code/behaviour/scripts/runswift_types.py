"""Shared behaviour types. Not ROS messages.

Skills use ``Point2`` / ``Pose2``. The world model uses the estimate records.
Skill requests stay next to each skill; they compose these types, they do not
replace them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import inf

# ---------------------------------------------------------------------------
# Game controller state codes (SPL)
# ---------------------------------------------------------------------------

GAME_PHASE_NORMAL = 0
GAME_PHASE_PENALTY_SHOOT_OUT = 1
GAME_PHASE_EXTRA_TIME = 2
GAME_PHASE_TIMEOUT = 3

STATE_INITIAL = 0
STATE_READY = 1
STATE_SET = 2
STATE_PLAYING = 3
STATE_FINISHED = 4

SET_PLAY_NONE = 0
SET_PLAY_DIRECT_FREE_KICK = 1
SET_PLAY_INDIRECT_FREE_KICK = 2
SET_PLAY_PENALTY_KICK = 3
SET_PLAY_THROW_IN = 4
SET_PLAY_GOAL_KICK = 5
SET_PLAY_CORNER_KICK = 6


def age_sec(last_seen_sec: float | None, now_sec: float) -> float:
    if last_seen_sec is None:
        return inf
    return max(0.0, now_sec - last_seen_sec)


def clamp_team_affinity(value: float) -> float:
    return max(-1.0, min(1.0, value))


@dataclass(frozen=True)
class Point2:
    """World-frame point in metres. No heading."""

    x: float = 0.0
    y: float = 0.0


@dataclass(frozen=True)
class Pose2:
    """World-frame pose (field or odom). ``x``, ``y`` metres; ``theta`` radians."""

    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0


@dataclass
class HeadModel:
    """Head joint angles in radians."""

    pitch: float = 0.0
    yaw: float = 0.0

    @property
    def head_pitch(self) -> float:
        return self.pitch

    @head_pitch.setter
    def head_pitch(self, value: float) -> None:
        self.pitch = value

    @property
    def head_yaw(self) -> float:
        return self.yaw

    @head_yaw.setter
    def head_yaw(self, value: float) -> None:
        self.yaw = value


@dataclass
class BallModel:
    """Ball observation in robot-local and field-global coordinates."""

    local_x: float | None = None
    local_y: float | None = None
    global_x: float | None = None
    global_y: float | None = None
    pixel_x: float | None = None
    pixel_y: float | None = None
    source: str = "unknown"
    confidence: float = 0.0
    last_seen_sec: float | None = None
    global_vx: float | None = None
    global_vy: float | None = None

    def age_sec(self, now_sec: float) -> float:
        return age_sec(self.last_seen_sec, now_sec)

    def is_fresh(self, now_sec: float, timeout_sec: float) -> bool:
        return self.age_sec(now_sec) <= timeout_sec

    def has_local_position(self) -> bool:
        return self.local_x is not None and self.local_y is not None

    def has_global_position(self) -> bool:
        return self.global_x is not None and self.global_y is not None

    def has_pixel_position(self) -> bool:
        return self.pixel_x is not None and self.pixel_y is not None

    def local_xy(self) -> tuple[float, float] | None:
        if not self.has_local_position():
            return None
        return (self.local_x, self.local_y)

    def global_xy(self) -> tuple[float, float] | None:
        if not self.has_global_position():
            return None
        return (self.global_x, self.global_y)

    def pixel_xy(self) -> tuple[float, float] | None:
        if not self.has_pixel_position():
            return None
        return (self.pixel_x, self.pixel_y)

    def global_velocity_xy(self) -> tuple[float, float]:
        vx = self.global_vx if self.global_vx is not None else 0.0
        vy = self.global_vy if self.global_vy is not None else 0.0
        return (vx, vy)


@dataclass
class CameraGroundFovModel:
    """Camera image footprint projected onto the ground plane."""

    local_corners: list[tuple[float, float]] = field(default_factory=list)
    global_corners: list[tuple[float, float]] = field(default_factory=list)
    adjusted_pixels: list[tuple[float, float]] = field(default_factory=list)
    valid: bool = False
    last_seen_sec: float = 0.0

    def age_sec(self, now_sec: float) -> float:
        return age_sec(self.last_seen_sec, now_sec)


@dataclass
class GameModel:
    state: int = STATE_INITIAL  # GC packets overwrite this when they arrive
    stopped: bool = True
    set_play: int = SET_PLAY_NONE
    game_phase: int = GAME_PHASE_NORMAL
    kicking_team: int | None = None
    secs_remaining: int | None = None
    secondary_time: int | None = None
    team_number: int | None = None
    player_id: int | None = None
    role_id: int | None = None
    gc_listening: bool = True

    my_team_info: object | None = None
    opponent_team_info: object | None = None
    my_penalty: int | None = None
    secs_till_unpenalised: int | None = None

    whistle_heard: bool = False
    nubots_whistle_heard: bool = False
    whistle_type: int | None = None
    ball_moved_since_set: bool = False
    ball_xy_at_set: tuple[float, float] | None = None
    ball_xy_prior_set_tick: tuple[float, float] | None = None


@dataclass
class RobotPeerFromComms:
    player_id: int
    pose: Pose2
    ball_global: BallModel
    going_for_ball: bool = False
    last_seen_sec: float = 0.0
    ball_valid: bool = False


@dataclass
class BallMeasurement:
    ball: BallModel
    source: str
    player_id: int | None = None
    purpose: str | None = None
    confidence: float = 0.0
    last_seen_sec: float | None = None


@dataclass
class RobotObservation:
    """Non-self robot observation."""

    player_id: int | None = None
    role_id: int | None = None
    pose: Pose2 | None = None
    team_affinity: float = 0.0
    confidence: float = 0.0
    source: str = "unknown"
    last_seen_sec: float | None = None
    label: str | None = None
    vision_miss_ticks: int = 0

    def __post_init__(self) -> None:
        self.team_affinity = clamp_team_affinity(self.team_affinity)

    def age_sec(self, now_sec: float) -> float:
        return age_sec(self.last_seen_sec, now_sec)

    def is_fresh(self, now_sec: float, timeout_sec: float) -> bool:
        return self.age_sec(now_sec) <= timeout_sec

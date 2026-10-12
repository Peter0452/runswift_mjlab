"""50 Hz head-target interpolator. Reads ``MotionCommand`` head fields."""
from __future__ import annotations

import threading
import time
from collections.abc import Callable

from action.types import HeadLimits, MotionCommand


class HeadController:
    """Interpolate head pitch/yaw toward the latest command on a daemon thread."""

    def __init__(
        self,
        command: MotionCommand,
        rotate_head: Callable[[float, float], None],
        read_pose: Callable[[], tuple[float, float] | None],
        suppressed: Callable[[], bool],
        *,
        frequency: float,
        limits: HeadLimits,
        log_warning: Callable[[str], None] | None = None,
    ) -> None:
        self._command = command
        self._rotate_head = rotate_head
        self._read_pose = read_pose
        self._suppressed = suppressed
        self._frequency = frequency
        self._limits = limits
        self._log_warning = log_warning
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is not None:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._loop,
            name="head_control",
            daemon=True,
        )
        self._thread.start()

    def stop(self, timeout: float = 1.0) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout)
            self._thread = None

    def _loop(self) -> None:
        period = 1.0 / self._frequency
        next_tick = time.perf_counter()
        last_mono = next_tick
        while not self._stop_event.is_set():
            now = time.perf_counter()
            sleep_for = next_tick - now
            if sleep_for > 0.0:
                if self._stop_event.wait(timeout=sleep_for):
                    break
                now = time.perf_counter()
            dt = now - last_mono
            last_mono = now
            next_tick += period
            if next_tick < now - period:
                next_tick = now
            dt = min(max(dt, 1e-4), self._limits.max_dt_sec)
            try:
                self.step(dt)
            except Exception as exc:
                if self._log_warning is not None:
                    self._log_warning(f"head control loop: {exc}")

    def step(self, dt: float) -> None:
        if self._suppressed():
            return

        head_pose = self._read_pose()
        if head_pose is None:
            return
        head_pitch, head_yaw = head_pose
        target_pitch, target_yaw, speed_pitch, speed_yaw = self._command.head_targets()

        yaw_arrived = abs(target_yaw - head_yaw) < 0.05
        pitch_arrived = abs(target_pitch - head_pitch) < 0.05
        if yaw_arrived and pitch_arrived:
            return

        speed_yaw_in_rad = speed_yaw * dt if not yaw_arrived else 0.0
        speed_pitch_in_rad = speed_pitch * dt if not pitch_arrived else 0.0
        direction_pitch = 1 if target_pitch > head_pitch else -1
        direction_yaw = 1 if target_yaw > head_yaw else -1

        pitch_cmd = direction_pitch * speed_pitch_in_rad + head_pitch
        yaw_cmd = direction_yaw * speed_yaw_in_rad + head_yaw

        p_min = min(target_pitch, head_pitch)
        p_max = max(target_pitch, head_pitch)
        y_min = min(target_yaw, head_yaw)
        y_max = max(target_yaw, head_yaw)
        pitch_cmd = min(max(pitch_cmd, p_min), p_max)
        yaw_cmd = min(max(yaw_cmd, y_min), y_max)

        pitch_cmd = min(max(pitch_cmd, self._limits.pitch_min), self._limits.pitch_max)
        yaw_cmd = min(max(yaw_cmd, self._limits.yaw_min), self._limits.yaw_max)
        self._rotate_head(float(pitch_cmd), float(yaw_cmd))

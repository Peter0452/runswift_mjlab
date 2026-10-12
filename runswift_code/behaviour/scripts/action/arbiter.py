"""Deterministic body-command arbiter in front of the locomotion adapter.

Precedence matches the previous ``execute_commands()`` path:

1. Fallen + recovery available + not stopped → get-up, no walk.
2. Stand / penalised → stop.
3. Clip walk velocity.
4. SET → skip body send this tick.
5. Kick / clear-kick hold → suppress walk (states may still call ``request_stop_now``).
6. Otherwise send clipped walk velocity.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from action.types import ArbiterInput, ArbiterResult, MotionCommand, VelocityLimits


class MotionAdapter(Protocol):
    def move(self, x: float, y: float, theta: float) -> None: ...
    def get_up(self) -> None: ...
    def rotate_head(self, pitch: float, yaw: float) -> None: ...
    def visual_kick(self, enable: bool = True) -> None: ...
    def update_kick_command(self, direction: float, power: float) -> None: ...
    def update_kick_ball(self, x: float, y: float) -> None: ...
    def enter_walk(self) -> None: ...
    def ensure_soccer_mode(self, timeout_sec: float = 3.0) -> None: ...
    def reset_odom(self) -> None: ...
    def play_action(self, action_id: str | None) -> None: ...
    def action_running(self) -> bool: ...


class ActionArbiter:
    """Owns body/head SDK effects. Skills must not call the vendor client."""

    def __init__(
        self,
        adapter: MotionAdapter,
        limits: VelocityLimits,
        *,
        on_walk_send: Callable[[float, float, float], None] | None = None,
    ) -> None:
        self.adapter = adapter
        self.limits = limits
        self._on_walk_send = on_walk_send

    def request_stop_now(self) -> None:
        """Immediate ``Move(0,0,0)``. Used by SET/STAND enter and kick hold-off."""
        try:
            self.adapter.move(0.0, 0.0, 0.0)
        except Exception:
            pass

    def request_visual_kick(self, enable: bool = True) -> None:
        self.adapter.visual_kick(enable)

    def update_kick_command(self, direction: float, power: float) -> None:
        self.adapter.update_kick_command(direction, power)

    def update_kick_ball(self, x: float, y: float) -> None:
        self.adapter.update_kick_ball(x, y)

    def enter_walk(self) -> None:
        self.adapter.enter_walk()

    def ensure_soccer_mode(self, timeout_sec: float = 3.0) -> None:
        self.adapter.ensure_soccer_mode(timeout_sec)

    def reset_odom(self) -> None:
        try:
            self.adapter.reset_odom()
        except Exception as e:
            print(f"reset odom exception: {e}")

    def request_action(self, action_id: str | None) -> None:
        self.adapter.play_action(action_id)

    def request_look(self, pitch: float, yaw: float) -> None:
        self.adapter.rotate_head(pitch, yaw)

    def action_running(self) -> bool:
        return self.adapter.action_running()

    def shutdown_stop(self) -> None:
        try:
            self.adapter.play_action(None)
        except Exception:
            pass
        try:
            self.adapter.visual_kick(False)
        except Exception:
            pass
        try:
            self.adapter.move(0.0, 0.0, 0.0)
        except Exception:
            pass
        self.adapter.rotate_head(0.36, 0.0)

    def execute(self, command: MotionCommand, inp: ArbiterInput) -> ArbiterResult:
        if inp.has_fallen and inp.recovery_available and not inp.is_stopped:
            self.adapter.get_up()
            return ArbiterResult(
                body_move_sent=False,
                published_cmd=None,
                reason="recover",
                recovered=True,
            )

        self._apply_kick(command)

        if inp.force_stop or inp.is_penalised:
            try:
                self.adapter.move(0.0, 0.0, 0.0)
            except Exception as e:
                print(f"move failed: {e}")
            return ArbiterResult(
                body_move_sent=True,
                published_cmd=(0.0, 0.0, 0.0),
                reason="stop",
            )

        self._clip_body(command)

        if inp.skip_body:
            return ArbiterResult(
                body_move_sent=False,
                published_cmd=None,
                reason="skip",
            )

        if inp.suppress_body:
            return ArbiterResult(
                body_move_sent=False,
                published_cmd=(0.0, 0.0, 0.0),
                reason="suppress",
            )

        vx, vy, vth = float(command.x), float(command.y), float(command.theta)
        try:
            if self._on_walk_send is not None:
                self._on_walk_send(vx, vy, vth)
            self.adapter.move(vx, vy, vth)
            return ArbiterResult(
                body_move_sent=True,
                published_cmd=(vx, vy, vth),
                reason="walk",
            )
        except Exception as e:
            print(f"move exception: {e}")
            return ArbiterResult(
                body_move_sent=False,
                published_cmd=(vx, vy, vth),
                reason="walk",
            )

    def _apply_kick(self, command: MotionCommand) -> None:
        if not command.kick_active:
            return
        self.adapter.update_kick_command(command.kick_direction, command.kick_power)
        self.adapter.update_kick_ball(command.kick_ball_x, command.kick_ball_y)

    def _clip_body(self, command: MotionCommand) -> None:
        vx_limit = self.limits.vx
        vy_limit = self.limits.vy
        vth_limit = self.limits.vtheta
        cmd_x_clipped = _clip(command.x, -vx_limit, vx_limit)
        if command.x != 0:
            command.y *= abs(cmd_x_clipped / command.x)
        command.y = _clip(command.y, -vy_limit, vy_limit)
        command.x = cmd_x_clipped
        command.theta = _clip(command.theta, -vth_limit, vth_limit)


def _clip(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))

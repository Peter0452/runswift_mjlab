"""Vendor-facing Booster locomotion adapter.

This is the only module that should import ``boosteros`` or call SDK methods.
The previous ``B1LocoClient`` wrapper is kept as ``booster_adapter_old_sdk.py``.
"""
from __future__ import annotations

from typing import Any

from boosteros.robots.booster import BoosterRobot, SoccerKickManager

from action.config import ROBOT_INIT_TIMEOUT_SEC, VIRTUAL_ROBOT_NAME


class BoosterAdapter:
    """Thin wrapper around ``BoosterRobot`` with the previous retry/print policy."""

    def __init__(self, robot: BoosterRobot) -> None:
        self._robot = robot
        self._soccer_kick = SoccerKickManager(robot)
        self._action_handle: Any = None
    
    def reset_odom(self) -> None:
        try:
            self._robot.reset_odom()
        except Exception as e:
            print(f"reset odom exception: {e}")

    def play_action(self, action_id: str | None) -> None:
        try:
            if action_id:
                if self.action_running():
                    self._cancel_action()
                    print("play action: previous action still running; not starting", action_id)
                    return
                self._action_handle = self._robot.do_action(action_id)
                return
            self._cancel_action()
        except Exception as e:
            print(f"play action exception: {e}")

    def action_running(self) -> bool:
        handle = self._action_handle
        if handle is None:
            return False
        if handle.done():
            self._action_handle = None
            return False
        return True

    def _cancel_action(self) -> None:
        handle = self._action_handle
        if handle is None:
            return
        if handle.done():
            self._action_handle = None
            return
        handle.cancel()

    def move(self, x: float, y: float, theta: float) -> None:
        self._robot.set_velocity(x, y, theta)

    def rotate_head(self, pitch: float, yaw: float) -> None:
        try:
            self._robot.set_head_angle(pitch, yaw)
        except Exception as e:
            print(f"rotate head exception: {e}")

    def get_up(self) -> None:
        try:
            self._robot.get_up()
        except Exception as e:
            print(f"getup failed: {e}")

    def visual_kick(self, enable: bool = True) -> None:
        try:
            if enable:
                self._soccer_kick.start()
            else:
                self._soccer_kick.stop()
        except Exception as e:
            print(f"visual kick exception: {e}")

    def update_kick_command(self, direction: float, power: float) -> None:
        try:
            self._soccer_kick.update_command(direction, power)
        except Exception as e:
            print(f"update kick command exception: {e}")

    def update_kick_ball(self, x: float, y: float) -> None:
        try:
            self._soccer_kick.update_ball(x, y)
        except Exception as e:
            print(f"update kick ball exception: {e}")

    def enter_walk(self) -> None:
        try:
            self._soccer_kick.stop()
        except Exception as e:
            print(f"disable visual kick exception: {e}")
        try:
            self._robot.set_gait("default")
            self._robot.set_mode("walk")
        except Exception as e:
            print(f"change mode exception: {e}")

    def ensure_soccer_mode(self, timeout_sec: float = 3.0) -> None:
        # Public mode is still "walk"; gait "soccer" maps to raw kSoccer.
        # timeout_sec is kept for the MotionAdapter signature; BoosterRobot
        # waits up to 5s internally on set_mode / set_gait.
        del timeout_sec
        try:
            self._robot.set_gait("soccer")
            self._robot.set_mode("walk")
        except Exception as e:
            print(f"change mode exception: {e}")
            print("ensure_soccer_mode timeout")


def create_booster_adapter() -> BoosterAdapter:
    robot = BoosterRobot(
        virtual_robot_name=VIRTUAL_ROBOT_NAME,
        timeout=ROBOT_INIT_TIMEOUT_SEC,
    )
    return BoosterAdapter(robot)

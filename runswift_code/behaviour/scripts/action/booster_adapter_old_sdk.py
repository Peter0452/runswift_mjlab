"""Backup of the ``B1LocoClient`` locomotion adapter (pre-boosteros).

Kept for comparison / rollback. The live adapter is ``booster_adapter.py``.
"""
from __future__ import annotations

import time
from typing import Any

from booster_robotics_sdk_python import (
    B1LocoClient,
    BodyControl,
    ChannelFactory,
    GaitType,
    RobotMode,
    VisualKickVersion,
)

GAIT_TYPE = GaitType.kHalfBodyHumanlikeGait
KICK_TYPE = VisualKickVersion.kV2


class BoosterAdapter:
    """Thin wrapper around ``B1LocoClient`` with the current retry/print policy."""

    def __init__(
        self,
        client: Any,
        *,
        gait_type: Any = GAIT_TYPE,
        kick_type: Any = KICK_TYPE,
    ) -> None:
        self._client = client
        self.gait_type = gait_type
        self.kick_type = kick_type

    def reset_odom(self) -> None:
        try:
            self._client.ResetOdometry()
        except Exception as e:
            print(f"reset odom exception: {e}")

    def move(self, x: float, y: float, theta: float) -> None:
        self._client.Move(x, y, theta)

    def rotate_head(self, pitch: float, yaw: float) -> None:
        try:
            self._client.RotateHead(pitch, yaw)
        except Exception as e:
            print(f"rotate head exception: {e}")

    def get_up(self) -> None:
        try:
            self._client.GetUpWithMode(RobotMode.kSoccer)
        except Exception as e:
            print(f"getup failed: {e}")

    def visual_kick(self, enable: bool = True) -> None:
        try:
            self._client.VisualKick(enable, self.kick_type)
        except Exception as e:
            print(f"visual kick exception: {e}")

    def update_kick_command(self, direction: float, power: float) -> None:
        del direction, power

    def update_kick_ball(self, x: float, y: float) -> None:
        del x, y

    def play_action(self, action_id: str | None) -> None:
        del action_id

    def action_running(self) -> bool:
        return False

    def enter_walk(self) -> None:
        if self._client.GetMode().mode == RobotMode.kSoccer:
            try:
                self._client.VisualKick(False, self.kick_type)
            except Exception as e:
                print(f"disable visual kick exception: {e}")
            time.sleep(0.02)

        while self._client.GetMode().mode != RobotMode.kWalking:
            time.sleep(0.02)
            try:
                self._client.ChangeMode(RobotMode.kWalking)
                break
            except Exception as e:
                print(f"change mode exception: {e}")
                time.sleep(0.02)

        states_mapping = {
            GaitType.kHalfBodyHumanlikeGait: BodyControl.kUnknown,
            GaitType.kHalfBodyHumanlikeGaitV2: BodyControl.kHumanlikeGait,
            GaitType.kWholeBodyHumanlikeGait: BodyControl.kWBCGait,
        }
        target_body_control = states_mapping[self.gait_type]
        current_body_control = self._client.GetStatus().current_body_control
        print(
            f"current body control: {current_body_control}, "
            f"target body control: {target_body_control}"
        )
        print(f"body control mapping: {states_mapping}")
        if current_body_control == target_body_control:
            print("body control already matched, no need to switch")
            return
        start_time = time.time()
        while time.time() - start_time < 0.5:
            try:
                self._client.SwitchGait(self.gait_type)
                print("switch gait success")
                break
            except Exception as e:
                print(f"switch gait exception: {e}")

    def ensure_soccer_mode(self, timeout_sec: float = 3.0) -> None:
        start_time = time.time()
        if self._client.GetMode().mode == RobotMode.kSoccer:
            return
        while time.time() - start_time < timeout_sec:
            try:
                self._client.ChangeMode(RobotMode.kSoccer)
            except Exception as e:
                print(f"change mode exception: {e}")
            if self._client.GetMode().mode == RobotMode.kSoccer:
                return
            time.sleep(0.02)
        print("ensure_soccer_mode timeout")


def create_booster_adapter() -> BoosterAdapter:
    ChannelFactory.Instance().Init(0)
    client = B1LocoClient()
    client.Init()
    return BoosterAdapter(client)

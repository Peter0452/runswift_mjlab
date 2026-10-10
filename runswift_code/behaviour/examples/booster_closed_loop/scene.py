"""Explicit setup/measurement of the dedicated test scene; no teleporting during runs."""

import json
import struct
import time

import msgpack
from websockets.sync.client import connect
from world_model.adapters.booster import MODEL_PATH, MODEL_REVISION, Frame


class Scene:
    def __init__(
        self,
        url="ws://127.0.0.1:18788",
        *,
        model_path=MODEL_PATH,
        model_revision=MODEL_REVISION,
        robot_height=0.7,
        robot2_body=25,
    ):
        self.model_path, self.model_revision = model_path, model_revision
        self.robot_height, self.robot2_body = robot_height, robot2_body
        self.ws = connect(url, max_size=4 * 1024 * 1024)
        self.ws.send("subscribe:simulation_state")
        self.ws.send("subscribe:game_control_world")
        self.metadata = None
        self.frame = None

    def close(self):
        self.ws.close()

    def command(self, command, **params):
        self.ws.send(
            json.dumps({"type": "command", "command": command, "params": params})
        )

    def read(self, timeout=2):
        packet = self.ws.recv(timeout=timeout)
        kind, length = struct.unpack("!II", packet[:8])
        if length != len(packet) - 8:
            raise ValueError("Invalid simulator message")
        payload = msgpack.unpackb(packet[8:], raw=False)
        if kind == 6:
            if (payload["model_path"], payload["model_revision"]) != (
                self.model_path,
                self.model_revision,
            ):
                raise ValueError("Unexpected simulator scene")
            self.metadata = payload
        elif kind == 13:
            self.frame = Frame.parse(payload)
        return self.frame

    def until(self, predicate, timeout=20):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.read()
            if self.metadata is not None and self.frame is not None and predicate():
                return self.frame
        raise TimeoutError("Simulator did not establish the requested scene")

    def prepare(self, *, start=(-2.0, 0.0), obstacle=(0.0, 0.0)):
        """Position robots only before arming navigation; robot2 remains a fixed obstacle."""
        self.until(lambda: self.frame.ns > 0)
        if not self.metadata["robot_statuses"].get("robot2"):
            self.command("spawn_robot", robot_name="robot2", robot_mode="multi")
        self.until(
            lambda: (
                self.metadata["is_multi_robot"]
                and all(
                    self.metadata["robot_statuses"].get(name)
                    for name in ("robot1", "robot2")
                )
            )
        )
        # Reset joints and controller state as well as the free body. Moving a
        # fallen trunk alone leaves the gait in damping with folded joints.
        self.command("reset_robot", robot_name="robot1")
        self.until(lambda: not self.metadata["robot_statuses"].get("robot1"))
        self.until(lambda: self.metadata["robot_statuses"].get("robot1"))
        self.command("pause")
        for body, xy in ((1, start), (self.robot2_body, obstacle)):
            self.command(
                "set_body_position", body_id=body, position=[*xy, self.robot_height]
            )
            self.command("set_body_rotation", body_id=body, quat=[1.0, 0.0, 0.0, 0.0])
        self.command("resume")
        return self.until(
            lambda: all(
                any(
                    r.name == name
                    and abs(r.position[0] - xy[0]) < 0.02
                    and abs(r.position[1] - xy[1]) < 0.02
                    and r.up_dot > 0.99
                    for r in self.frame.robots
                )
                for name, xy in (("robot1", start), ("robot2", obstacle))
            )
        )

    def release(self):
        """Let the selected robot move under its actual motion controller and physics."""
        self.command("set_body_position", body_id=1, is_dragging=False)

    def finish_setup(self):
        """Stop setup subscriptions before the separate input bridge takes over."""
        self.ws.send("unsubscribe:simulation_state")
        self.ws.send("unsubscribe:game_control_world")
        while True:
            try:
                self.read(timeout=0.1)
            except TimeoutError:
                return

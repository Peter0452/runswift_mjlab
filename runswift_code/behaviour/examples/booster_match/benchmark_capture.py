"""Read-only truth/physics recorder, independent of the world-model input bridge."""

import json
import struct
import time
from threading import Event, Thread

import msgpack
from websockets.sync.client import connect
from world_model.adapters.booster import K1_MODEL_PATH, K1_MODEL_REVISION


class Recorder:
    """Retain contacts at source rate and coherent render states at at most 25 Hz."""

    def __init__(self, url, directory):
        self.directory = directory
        self.error = None
        self._stop, self._ready = Event(), Event()
        self.ws = connect(url, max_size=8 * 1024 * 1024)
        for topic in ("simulation_state", "physics_state", "game_control_world"):
            self.ws.send("subscribe:" + topic)
        self._worker = Thread(target=self._run, daemon=True)
        self._worker.start()
        if not self._ready.wait(5) or self.error:
            self.close()
            raise RuntimeError("Recorder not ready: " + str(self.error))

    def _run(self):
        checked, seen, last_render = False, set(), -1.0
        try:
            with (
                (self.directory / "truth.jsonl").open("x") as truth,
                (self.directory / "physics.jsonl").open("x") as physics,
            ):
                while not self._stop.is_set():
                    packet = self.ws.recv(timeout=1)
                    wall = time.monotonic_ns()
                    kind, length = struct.unpack("!II", packet[:8])
                    if length != len(packet) - 8:
                        raise ValueError("Invalid simulator packet length")
                    value = msgpack.unpackb(packet[8:], raw=False)
                    if kind == 6:
                        if (value["model_path"], value["model_revision"]) != (
                            K1_MODEL_PATH,
                            K1_MODEL_REVISION,
                        ):
                            raise ValueError("Unexpected recorder scene")
                        if not checked:
                            (self.directory / "scene.json").write_text(
                                json.dumps(value, indent=2) + "\n"
                            )
                        checked = True
                    elif checked and kind in (1, 13):
                        seen.add(kind)
                        if kind == 13 or value["time"] - last_render >= 0.04 - 1e-9:
                            stream = truth if kind == 13 else physics
                            stream.write(
                                json.dumps(
                                    {"wall_ns": wall, "data": value}, allow_nan=False
                                )
                                + "\n"
                            )
                            if kind == 1:
                                last_render = value["time"]
                        if seen == {1, 13}:
                            self._ready.set()
        except Exception as exc:  # noqa: BLE001 -- retain asynchronous recording faults
            if not self._stop.is_set():
                self.error = repr(exc)
                self._ready.set()

    def close(self):
        self._stop.set()
        self.ws.close()
        self._worker.join(timeout=3)
        if self._worker.is_alive():
            raise RuntimeError("Recorder did not close")

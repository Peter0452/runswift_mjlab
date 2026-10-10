"""Private host/container IPC for complete match intents and measured SDK feedback."""

import json
import os
import subprocess
import time
import uuid
from collections import deque
from pathlib import Path
from threading import Event, Lock, Thread

CONTAINER = "runswift-world-model-sim"
REMOTE = "/tmp/runswift-match"
PYTHON = "/usr/local/booster_robot/booster_robocup_sim/.venv/bin/python"
PREFIX = "RUNSWIFT_MATCH "


class MatchRelay:
    """Non-blocking motion port; the receiver retains absolute sender deadlines."""

    def __init__(self, *, robot="robot1"):
        if robot not in {"robot1", "robot2", "robot3", "robot4"}:
            raise ValueError("Choose a named simulated K1")
        info = json.loads(subprocess.check_output(["docker", "inspect", CONTAINER]))[0]
        if not info["State"]["Running"] or info["HostConfig"]["NetworkMode"] == "host":
            raise ValueError(
                "The dedicated simulator must run in an isolated Docker network"
            )
        root = Path(__file__).resolve().parents[2]
        subprocess.run(["docker", "exec", CONTAINER, "mkdir", "-p", REMOTE], check=True)
        for source in (root / "scripts/action", Path(__file__).with_name("relay.py")):
            subprocess.run(
                ["docker", "cp", str(source), CONTAINER + ":" + REMOTE + "/"],
                check=True,
            )
        self.session, self.sequence = str(uuid.uuid4()), -1
        self.receipts, self.logs = deque(maxlen=4096), deque(maxlen=30)
        self._lock, self._ready = Lock(), Event()
        self._closed = False
        self.process = subprocess.Popen(
            [
                "docker",
                "exec",
                "-i",
                "-e",
                "ROS_DOMAIN_ID=0",
                "-e",
                "PYTHONPATH=" + REMOTE,
                CONTAINER,
                "bash",
                "-c",
                'source /opt/ros/humble/setup.bash; exec "$@"',
                "match-relay",
                PYTHON,
                REMOTE + "/relay.py",
                "--robot",
                robot,
                "--session",
                self.session,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        os.set_blocking(self.process.stdin.fileno(), False)
        self._reader = Thread(target=self._read, daemon=True)
        self._reader.start()
        if not self._ready.wait(12):
            self.close()
            raise RuntimeError("Match relay not ready: " + "\n".join(self.logs))
        with self._lock:
            ready = next(row for row in self.receipts if row["kind"] == "ready")
        if not 0 <= time.monotonic_ns() - ready["now_ns"] <= 250_000_000:
            self.close()
            raise RuntimeError("Host/container monotonic clocks are not aligned")

    def _read(self):
        for line in self.process.stdout:
            text = line.decode("utf-8", errors="replace").strip()
            if text.startswith(PREFIX):
                try:
                    row = json.loads(text[len(PREFIX) :])
                except ValueError:
                    self.logs.append("Malformed relay feedback: " + text)
                    continue
                with self._lock:
                    self.receipts.append(row)
                if row["kind"] == "ready":
                    self._ready.set()
            else:
                self.logs.append(text)

    def latest(self):
        with self._lock:
            return next(
                (
                    dict(row)
                    for row in reversed(self.receipts)
                    if row["kind"] == "feedback"
                ),
                None,
            )

    def _write(self, message):
        if self._closed or self.process.poll() is not None:
            raise RuntimeError("Match relay is closed: " + "\n".join(self.logs))
        data = (json.dumps(message, allow_nan=False) + "\n").encode()
        if len(data) > 4096 or os.write(self.process.stdin.fileno(), data) != len(data):
            raise RuntimeError("Incomplete match command write")

    def send(self, intent):
        if intent.session != self.session or intent.sequence <= self.sequence:
            raise ValueError("Wrong match session or command sequence")
        receipt = self.latest()
        if (
            receipt is None
            or not 0 <= time.monotonic_ns() - receipt["now_ns"] <= 150_000_000
        ):
            raise RuntimeError("Actuator feedback unavailable or stale")
        if receipt["failure"]:
            raise RuntimeError("Actuator requires a new session: " + receipt["failure"])
        self.sequence = intent.sequence
        self._write(intent.message())

    def stop(self):
        self._write(
            {
                "schema": "runswift-match/1",
                "stop": True,
                "session": self.session,
                "through_sequence": self.sequence,
            }
        )

    def close(self):
        if self._closed:
            return
        try:
            if self.process.poll() is None:
                self.stop()
        finally:
            self._closed = True
            self.process.stdin.close()
            try:
                self.process.wait(timeout=4)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                self.process.wait(timeout=4)
            self._reader.join(timeout=1)

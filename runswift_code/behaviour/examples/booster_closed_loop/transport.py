"""Host-side connection to the independent motion relay in the dedicated simulator."""

import json
import os
import subprocess
import time
import uuid
from collections import deque
from pathlib import Path
from threading import Event, Lock, Thread

from action.velocity_lease import VelocityLease

CONTAINER = "runswift-world-model-sim"
REMOTE = "/tmp/runswift-navigation"
PYTHON = "/usr/local/booster_robot/booster_robocup_sim/.venv/bin/python"


class MotionRelay:
    """Send expiring commands through Docker stdin and retain applied-command receipts."""

    def __init__(self, *, robot="robot1", command_ns=250_000_000):
        if robot not in {"robot1", "robot2", "robot3", "robot4"}:
            raise ValueError("Choose a named simulated robot")
        if type(command_ns) is not int or not 0 < command_ns <= 250_000_000:
            raise ValueError("Command lifetime must be at most 250 ms")
        inspect = json.loads(subprocess.check_output(["docker", "inspect", CONTAINER]))[
            0
        ]
        if (
            not inspect["State"]["Running"]
            or inspect["HostConfig"]["NetworkMode"] == "host"
        ):
            raise ValueError(
                "The dedicated simulator must run in its isolated Docker network"
            )
        root = Path(__file__).resolve().parents[2]
        subprocess.run(["docker", "exec", CONTAINER, "mkdir", "-p", REMOTE], check=True)
        subprocess.run(
            ["docker", "cp", str(root / "scripts/action"), CONTAINER + ":" + REMOTE],
            check=True,
        )
        subprocess.run(
            [
                "docker",
                "cp",
                str(Path(__file__).with_name("motion_relay.py")),
                CONTAINER + ":" + REMOTE + "/motion_relay.py",
            ],
            check=True,
        )
        self.session = str(uuid.uuid4())
        self.command_ns = command_ns
        self.sequence = -1
        self.receipts = deque(maxlen=4096)
        self.logs = deque(maxlen=30)
        self._lock = Lock()
        self._ready = Event()
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
                "motion-relay",
                PYTHON,
                REMOTE + "/motion_relay.py",
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
        if not self._ready.wait(10):
            self.close()
            raise RuntimeError("Motion relay not ready: " + "\n".join(self.logs))
        ready = next(item for item in self.receipts if item["kind"] == "ready")
        if not 0 <= time.monotonic_ns() - ready["now_ns"] <= 250_000_000:
            self.close()
            raise RuntimeError("Host/container monotonic clocks are not aligned")

    def _read(self):
        for line in self.process.stdout:
            text = line.decode("utf-8", errors="replace").strip()
            if text.startswith("RUNSWIFT_MOTION "):
                item = json.loads(text[len("RUNSWIFT_MOTION ") :])
                with self._lock:
                    self.receipts.append(item)
                if item["kind"] == "ready":
                    self._ready.set()
            else:
                self.logs.append(text)

    def latest(self):
        with self._lock:
            return next(
                (
                    dict(item)
                    for item in reversed(self.receipts)
                    if item["kind"] == "applied"
                ),
                None,
            )

    def send(self, velocity, observation_until_ns):
        """Bound command age before writing; never queue behind a blocked relay."""
        if self._closed or self.process.poll() is not None:
            raise RuntimeError("Motion relay is closed: " + "\n".join(self.logs))
        receipt = self.latest()
        if (
            tuple(velocity) != (0.0, 0.0, 0.0)
            and receipt is not None
            and receipt["reason"] not in {"moving", "idle", "stopped"}
        ):
            raise RuntimeError(
                "Motion relay requires a new session: " + receipt["reason"]
            )
        now = time.monotonic_ns()
        self.sequence += 1
        lease = VelocityLease(
            self.session,
            self.sequence,
            now,
            now + self.command_ns,
            observation_until_ns,
            tuple(velocity),
        )
        data = (json.dumps(lease.message(), allow_nan=False) + "\n").encode()
        if os.write(self.process.stdin.fileno(), data) != len(data):
            raise RuntimeError("Incomplete motion command write")
        return lease

    def stop(self):
        return self.send((0.0, 0.0, 0.0), time.monotonic_ns())

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
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                self.process.wait(timeout=3)
            self._reader.join(timeout=1)

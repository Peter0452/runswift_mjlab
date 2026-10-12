"""Simulator-only SDK relay with a wall-clock watchdog; Python 3.10 compatible.

Launched through docker exec stdin, never exposed on a network socket. The
host passes bounded absolute monotonic deadlines; buffering cannot renew them.
"""

import argparse
import json
import os
import selectors
import signal
import sys
import time

from action.velocity_lease import ZERO, VelocityLeaseGate

PREFIX = "RUNSWIFT_MOTION "


def emit(**value):
    print(PREFIX + json.dumps(value, allow_nan=False), flush=True)


def run(robot, session):
    if not os.path.exists("/.dockerenv") or robot not in {
        "robot1",
        "robot2",
        "robot3",
        "robot4",
    }:
        raise ValueError("This relay requires a named virtual robot inside Docker")
    import booster_robotics_sdk_python as b1

    # Container network is isolated; never fall back to the physical/unnamed robot.
    b1.ChannelFactory.Instance().Init(0)
    client = b1.B1LocoClient()
    client.InitWithName(robot)
    gate = VelocityLeaseGate(session)
    stopping = False

    def stop_signal(*_):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, stop_signal)
    signal.signal(signal.SIGINT, stop_signal)
    selector = selectors.DefaultSelector()
    selector.register(sys.stdin, selectors.EVENT_READ)
    buffer = b""
    last_status = None
    try:
        if not client.WaitForService(5000):
            raise RuntimeError("Named simulator motion service did not become ready")
        if client.GetMode().mode != b1.RobotMode.kWalking:
            client.ChangeMode(b1.RobotMode.kPrepare)
            # The test fixture holds the trunk while the joints reach standing
            # posture. No motion lease exists during this startup transition.
            time.sleep(2)
        result = client.ChangeMode(b1.RobotMode.kWalking)
        if result not in (None, 0):
            raise RuntimeError(f"Walking mode rejected: {result}")
        # ChangeMode acknowledges the request before the gait transition has
        # completed. Only arm after walking mode accepts a zero command.
        ready_by = time.monotonic() + 5
        while True:
            try:
                if client.GetMode().mode == b1.RobotMode.kWalking:
                    client.Move(*ZERO)
                    break
            except RuntimeError:
                pass  # No non-zero command has been accepted during startup.
            if stopping or time.monotonic() >= ready_by:
                raise RuntimeError("Walking mode did not become ready")
            time.sleep(0.05)
        emit(kind="ready", session=session, robot=robot, now_ns=time.monotonic_ns())
        while not stopping:
            for _, _ in selector.select(timeout=0.02):
                data = os.read(sys.stdin.fileno(), 4096)
                if not data:
                    gate.fail("command_channel_closed")
                    stopping = True
                    break
                buffer += data
                if len(buffer) > 16384:
                    gate.fail("command_buffer_overflow")
                    stopping = True
                    break
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    try:
                        gate.accept(json.loads(line), time.monotonic_ns())
                    except (ValueError, TypeError):
                        gate.fail("malformed_motion_message")
            velocity = gate.velocity(time.monotonic_ns())
            client.Move(*velocity)
            status = (gate.sequence, gate.reason, velocity)
            if status != last_status:
                emit(
                    kind="applied",
                    sequence=gate.sequence,
                    reason=gate.reason,
                    velocity=velocity,
                    now_ns=time.monotonic_ns(),
                    expired_at_ns=gate.expired_at_ns,
                )
                last_status = status
    finally:
        selector.close()
        # Stop remains explicit on EOF, malformed input, cancellation and shutdown.
        for _ in range(3):
            try:
                client.Move(*ZERO)
            except RuntimeError as exc:
                emit(kind="stop_failed", error=str(exc), now_ns=time.monotonic_ns())
            time.sleep(0.02)
        emit(kind="closed", now_ns=time.monotonic_ns())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--robot", required=True)
    parser.add_argument("--session", required=True)
    args = parser.parse_args()
    run(args.robot, args.session)


if __name__ == "__main__":
    main()

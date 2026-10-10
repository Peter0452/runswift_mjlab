"""K1 simulator actuator process; never connect to an unnamed physical robot."""

import argparse
import json
import os
import selectors
import signal
import sys
import time

from action.booster_match_sdk import BoosterMatchDriver
from action.match_actuator import MatchActuator
from action.match_intent import MatchIntent

PREFIX = "RUNSWIFT_MATCH "


def emit(value):
    # A stalled log consumer must not stall the motion watchdog. Each status is
    # smaller than PIPE_BUF; dropping a receipt cannot renew a command lease.
    data = (PREFIX + json.dumps(value, allow_nan=False) + "\n").encode()
    if len(data) > 4096:
        raise ValueError("Oversized actuator feedback")
    try:
        os.write(sys.stdout.fileno(), data)
    except (BlockingIOError, BrokenPipeError):
        pass


def admit(actuator, message):
    """Validate both command and cancellation envelopes before changing the gate."""
    if isinstance(message, dict) and message.get("stop") is True:
        if (
            set(message) != {"schema", "stop", "session", "through_sequence"}
            or message["schema"] != "runswift-match/1"
            or message["session"] != actuator.gate.session
        ):
            raise ValueError("Invalid stop envelope")
        actuator.stop(message["through_sequence"])
    else:
        actuator.accept(MatchIntent.parse(message))


def run(robot, session):
    if not os.path.exists("/.dockerenv"):
        raise ValueError("The K1 simulator relay must run inside isolated Docker")
    os.set_blocking(sys.stdout.fileno(), False)
    driver = BoosterMatchDriver(robot)
    actuator = MatchActuator(driver, session, clock=time.monotonic_ns)
    stopping = False

    def stop_signal(*_):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, stop_signal)
    signal.signal(signal.SIGINT, stop_signal)
    selector = selectors.DefaultSelector()
    selector.register(sys.stdin, selectors.EVENT_READ)
    buffer = b""
    try:
        driver.prepare()  # Held fixture, no lease; mode transitions happen here.
        emit(actuator.step())
        emit(
            {
                "kind": "ready",
                "session": session,
                "robot": robot,
                "profile": "K1-V2",
                "now_ns": time.monotonic_ns(),
            }
        )
        while not stopping:
            for _, _ in selector.select(timeout=0.02):
                data = os.read(sys.stdin.fileno(), 4096)
                if not data:
                    actuator.gate.fail("command_channel_closed")
                    stopping = True
                    break
                buffer += data
                if len(buffer) > 16384:
                    actuator.gate.fail("command_buffer_overflow")
                    stopping = True
                    break
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    try:
                        admit(actuator, json.loads(line))
                    except (ValueError, TypeError, KeyError, OverflowError):
                        actuator.gate.fail("malformed_match_message")
            emit(actuator.step())
    finally:
        selector.close()
        actuator.gate.fail("command_channel_closed")
        # An acknowledged disable can precede the actual controller transition.
        # Continue stopping while observing it; report an unconfirmed shutdown.
        deadline = time.monotonic() + 2
        confirmed = False
        try:
            while time.monotonic() < deadline:
                result = actuator.step()
                emit(result)
                sample = result["sample"]
                if (
                    sample
                    and not sample["kick_active"]
                    and not result["stop_errors"]
                    and 0 <= time.monotonic_ns() - sample["observed_ns"] < 150_000_000
                    and 0 <= time.monotonic_ns() - sample["status_ns"] < 1_200_000_000
                ):
                    confirmed = True
                    break
                time.sleep(0.02)
        finally:
            # Even malformed SDK feedback or failed status encoding must not
            # prevent the final independent disable/zero attempts.
            try:
                driver.close()
            finally:
                emit(
                    {
                        "kind": "closed",
                        "stop_confirmed": confirmed,
                        "now_ns": time.monotonic_ns(),
                    }
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--robot", required=True)
    parser.add_argument("--session", required=True)
    args = parser.parse_args()
    run(args.robot, args.session)

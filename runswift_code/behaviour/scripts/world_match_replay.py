#!/usr/bin/env python3
"""Replay the new match runner with Booster ground truth; print intents, never actuate."""

import argparse
import json
from dataclasses import asdict, replace

from action.match_intent import MatchIntentGate
from match_execution import MatchExecutive
from match_runner import MatchGoal, MatchRunner, MotionFeedback
from skills.world import NavigateToPose, NavigationPolicy
from world_model.adapters.booster import (
    MODEL_PATH,
    MODEL_REVISION,
    Frame,
    GroundTruthInputs,
    Robot,
    make_config,
)

from world_model import capture_tick, create_world_model
from world_model import types as wm


class ReplayClock:
    def __init__(self, epoch):
        self.epoch, self.ns = epoch, 0

    def now(self):
        return wm.TimePoint(self.epoch, self.ns)


def open_play_report(*, state="playing", penalty="none"):
    """Explicit synthetic referee evidence; the simulator has no official referee feed."""
    return wm.OfficialMatchReport(
        state,
        "normal",
        False,
        "none",
        True,
        1,
        600,
        0,
        (
            wm.TeamReport(1, 0, (wm.PlayerReport(1, penalty, 0),)),
            wm.TeamReport(2, 0, ()),
        ),
    )


class MatchReplayWorld:
    """Application-owned input/update loop, independent of whether a runner ticks."""

    def __init__(self, epoch, *, robot="robot1", radii=None, identity=None):
        self.clock = ReplayClock(epoch)
        self.config = make_config(epoch)
        if identity is not None:
            self.config = replace(self.config, identity=identity)
        self.model = create_world_model(config=self.config, clock=self.clock)
        self.inputs = GroundTruthInputs(
            self.model.input,
            self.config,
            epoch,
            robot=robot,
            radii={} if radii is None else radii,
        )
        self.sequence = 0

    def publish(self, frame, *, report=None, localised=True):
        """Admit capture-time facts and optional scripted referee evidence, then publish."""
        if frame.ns < self.clock.ns:
            raise ValueError("Replay time cannot go backwards")
        self.clock.ns = frame.ns
        self.inputs.submit(frame, self.clock.now(), localised=localised)
        if report is not None:
            event = wm.WorldEvent(
                wm.InputMeta(
                    wm.EventId("scripted-referee", self.clock.epoch, self.sequence),
                    None,
                    self.clock.now(),
                    self.clock.now(),
                    "synchronised",
                    0,
                    self.config.configuration_id,
                ),
                report,
            )
            self.sequence += 1
            admission = self.model.input.submit(event)
            if admission.status != "queued":
                raise ValueError(admission.reason)
        self.model.owner.advance(self.clock.now())
        return capture_tick(self.model.reader, self.clock, frame.sequence)


class ReplayMotion:
    """Exercise the receiver's gate and retain intents; no hardware or SDK access."""

    def __init__(self, clock):
        self.clock, self.gate = clock, None

    def send(self, intent):
        if self.gate is None:
            self.gate = MatchIntentGate(intent.session)
        if not self.gate.accept(intent, self.clock()):
            raise RuntimeError(self.gate.failure)

    def stop(self):
        if self.gate is not None:
            self.gate.stop()


def scripted_frames():
    """Controlled simulator-shaped inputs, not a recording or physics validation."""
    for sequence, (robot_x, ball, state) in enumerate(
        (
            (-2, None, "initial"),
            (-2, None, "playing"),
            (-2, (0.0, 0.0, 0.11), "playing"),
            (-0.7, (0.0, 0.0, 0.11), "playing"),
            (-0.7, (0.0, 0.0, 0.11), "set"),
        )
    ):
        yield (
            Frame(
                sequence * 100_000_000,
                sequence,
                (Robot("robot1", (robot_x, 0.0, 0.7), 0.0, 1.0),),
                ball,
            ),
            open_play_report(state=state),
        )


def recording_frames(path, epoch):
    """Validate the known scene mapping before yielding recorded ground-truth frames."""
    with open(path, encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row["schema"] != "booster-ground-truth-v1" or row["model"] != {
                "path": MODEL_PATH,
                "revision": MODEL_REVISION,
            }:
                raise ValueError(
                    "Recording requires the reviewed Booster scene mapping"
                )
            if row["epoch"] != epoch:
                raise ValueError("Start a new replay for a new recording epoch")
            yield Frame.parse(row["payload"]), None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "recording", nargs="?", help="Omit for the five-step scripted sequence"
    )
    parser.add_argument("--radius", action="append", default=[], metavar="ROBOT=METRES")
    parser.add_argument(
        "--allow-unknown",
        action="store_true",
        help="Explicit speed-limited uninspected-space policy",
    )
    parser.add_argument(
        "--script-open-play",
        action="store_true",
        help="Add synthetic open-play and motion-ready evidence to a recording",
    )
    args = parser.parse_args(argv)
    epoch = "scripted-match"
    if args.recording:
        with open(args.recording, encoding="utf-8") as stream:
            epoch = json.loads(next(stream))["epoch"]
    radii = {
        name: float(value)
        for name, value in (item.split("=", 1) for item in args.radius)
    }
    world = MatchReplayWorld(epoch, radii=radii)
    port = ReplayMotion(lambda: world.clock.ns)
    runner = MatchRunner(
        navigation=NavigateToPose(
            navigation_policy=NavigationPolicy(
                unknown_space="allow_unknown" if args.allow_unknown else "require_clear"
            )
        )
    )
    executive = MatchExecutive(runner, port, wall_clock=lambda: world.clock.ns)
    executive.start(MatchGoal())
    rows = (
        recording_frames(args.recording, epoch) if args.recording else scripted_frames()
    )
    count = 0
    for frame, report in rows:
        if args.script_open_play:
            report = open_play_report()
        context = world.publish(frame, report=report)
        # Mode readiness is explicitly scripted, never inferred from pose alone.
        feedback = (
            MotionFeedback(context.now, True, True, True)
            if report is not None
            else None
        )
        result = executive.tick(context, world.clock.ns, motion=feedback)
        print(
            json.dumps(
                {
                    "input": "recorded" if args.recording else "scripted",
                    "referee_and_readiness": "scripted"
                    if report is not None
                    else "unavailable",
                    **asdict(result),
                },
                allow_nan=False,
            )
        )
        count += 1
    executive.cancel("replay_finished")
    if not count:
        raise ValueError("Empty recording")


if __name__ == "__main__":
    main()

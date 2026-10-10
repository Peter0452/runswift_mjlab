# Live K1 match integration

For short walking/kicking measurements and replaceable policy comparisons, start
with [How to run the benchmark](../../../../benchmarks/README.md), or use the
[detailed calibration guide](skill-calibration.md). It measures command response,
stopping, direction changes, aim/range accuracy and walk–kick–walk transition times.

This example connects the new match runner to the **simulated K1's native
motion controller**. Navigation sends body velocities, search moves the head,
and a kick intent supplies the SDK with a current body-relative ball and aim.
The resulting movement returns through the world model. No robot positions are
written after scene setup.

The world model and behaviours remain independent of ROS and the SDK. This
application uses the optional ROS 2 input adapter; a separate Python 3.10 process
inside the simulator owns the SDK. The application and numerical world model
run on Python 3.11 or later on the Linux Docker host.

This is an integration and validation fixture. It is not the deployed robot
match launch command. Referee reports are explicitly **scripted**, positions
come from simulator **ground truth**, and the sequence test deliberately
withholds ball observations initially to exercise search. Camera perception is
not connected to this live match loop.

## Run on marvin

Use the prepared workspace described in the
[simulator guide](../../../world_model/docs/human/booster-simulator.md). Sync
`src/behaviour/` to `behaviour/` and `src/world_model/` to `world_model/` there.
The host needs the world-model package, ROS Jazzy, `msgpack==1.1.2`,
`websockets==15.0.1`, and Docker access. The existing `ros-venv` contains these.
Do not run another motion client or input publisher at the same time.

```sh
cd /home/oliver/runswift-simulation/booster-1.10.5
# Stop the previous dedicated test scene before selecting K1.
docker stop runswift-world-model-sim
bash behaviour/examples/booster_match/start-simulator.sh
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=87
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export JAX_PLATFORMS=cpu
export PYTHONPATH="$PWD/world_model:$PWD/behaviour/scripts${PYTHONPATH:+:$PYTHONPATH}"
ros-venv/bin/python behaviour/examples/booster_match/run.py \
  --scenario all --output match-k1-results
docker stop runswift-world-model-sim
```

Use a new output directory. Each scenario creates a fresh world and motion
session, resets robot1 and places robot2 at (0, 3) with a conservative 0.45 m
footprint. Robot1 is held only during initial mode preparation. The K1 scene,
body IDs and revision are checked before any actuation. The older T1 navigation
fixture and its defaults remain available separately.

The explicit `world_model` source root avoids the outer package directory
shadowing an editable installation when launching from this workspace.

The command channel is a private `docker exec` pipe into the dedicated isolated
container. It explicitly selects `robot1`; unnamed physical-robot channels and
host-network containers are refused. Host and container must share Linux
monotonic time. This cannot run across a Mac-to-Linux clock boundary by merely
tunnelling the WebSocket port.

## How motion is connected

1. `BoosterBridge` publishes coherent K1 observation batches at 20 Hz.
   `WorldModelNode` updates on a separate 50 Hz steady timer. Its executor runs
   independently of behaviour, including during cancellation and injected stalls.
2. `MatchExecutive` captures no inputs itself. The application gives it one
   context and that view's original input receipt time, plus separate SDK feedback.
   It produces one atomic `MatchIntent` containing body, head and kick commands.
3. `MatchRelay` sends that intent without replacing its timestamps. `relay.py`
   runs `MatchActuator` on its own schedule, checking leases at approximately
   50 Hz even when behaviour or simulation time stops.
4. `BoosterMatchDriver` prepares Walking mode before arming. K1 navigation uses
   Walking; a kick first requests Soccer and waits for measured mode feedback.
   Those transitions are polled rather than slept through in the watchdog loop.
   They time out after three seconds and require fresh intents throughout.
5. Head interpolation runs at 10 Hz with the intent's rate limits. The driver
   sends native `RotateHead` requests. A stop disables visual kicking, holds the
   measured head angles, sends zero body velocity and requests Walking mode.
   The acknowledged head hold is retained during the transition: K1 rejects
   new head requests while changing modes. Failed stop operations remain visible
   and are retried. Stale or fallen SDK feedback prevents a mode-change request.

The reviewed simulator uses Studio 1.10.5, SDK 1.5.6 and **VisualKick V2**.
Its raw K1 body-controller values differ from some Python enum names. Walking
is mode 2/controller 12; Soccer uses mode 4/controllers 10 and 14. Shooting or
passing phase feedback also counts as active kicking. These are pinned simulator
semantics, not a promise about other firmware or physical K1 units.

Kick coordinates come entirely from the behaviour intent. The driver does not
fetch another pose or legacy world view. It publishes the body-relative ball,
an 8 m virtual goal along the supplied aim, and the robot yaw relative to that
virtual goal direction. The unused SDK `dir` stays zero, following the installed
Booster soccer-kick mapping. The SDK header is command publication time;
observation freshness is governed by the unchanged intent deadline.

## Feedback and stopping

Native SDK state messages lack capture timestamps. Joint/IMU and mode/fall
callbacks retain their original monotonic **receipt** times. Fast joint/IMU
feedback expires after 150 ms. The slower mode/fall stream expires after 1.2 s
(the installed fall stream publishes at about 1 Hz). Fast IMU tilt and the
reported fall state must both permit upright operation. No feedback read renews
these times.

`SdkFeedback` associates each new fast sample once with the decision clock and
checks its original wall age on every read. This is an explicit receipt-time
association, not a claim of synchronised sensor capture. Motion facts stay out
of the world model.

A kick acknowledgement means only that the request was accepted. The actuator
reports `running` from observed kick activity. Native phases are diagnostic;
they do not report single-shot completion. The shared `SingleShot` skill observes
ball departure, permits a bounded follow-through, then sends stopped body/kick
intents while awaiting `stopped` feedback for that attempt. The actuator reports
`stopping` until new SDK samples confirm exit and Walking readiness. Only then
does the skill return
`shot_departed_and_stopped`. This does not prove foot contact, accuracy or a goal.
Expiry, cancellation and faults remain failures. A stopped or failed attempt
cannot enable kicking again, even after a different attempt has run.

Commands last at most 250 ms and observations at most 350 ms of wall time.
The earlier absolute deadline wins, including time spent planning and making
SDK calls. Stop messages fence all previously sent sequence numbers. Malformed,
reordered or expired commands latch a fault requiring a new motion session.
EOF, normal process shutdown, stale feedback and SDK rejection also revoke
motion. Each stop operation is attempted even when another fails; failures
remain visible and are retried by the watchdog.

RPC requests have a 20 ms response timeout. This is not a hard real-time or
firmware safety guarantee: SDK/DDS publication, OS scheduling, process crashes
and the physical controller still need platform-level protection. A successful
disable response can precede controller exit. The validation records measured
exit and settling, rather than treating that response as an instantaneous stop.

## Validation scenarios

| Scenario | Evidence required |
| --- | --- |
| `sequence` | Stand, measured head search, approach with measured travel, native kick activity, then a stopped controller and settled robot. Ball movement is measured separately. |
| `cancel_kick` | Cancel only after the SDK reports kick activity; confirm that visual kicking exits and the robot settles. |
| `command_expiry` | Stop sending intentions while the world keeps updating; the independent actuator must expire the last lease. |
| `observation_expiry` | Stop observations and `/clock` while physics continues; movement must stop at the observation deadline. |
| `referee_stop` | Inject a scripted SET report during kicking; the runner must hold and disable kicking. |

JSONL traces include capture/decision/snapshot times, ground truth, intents,
SDK samples, attempt outcomes, errors and stop reasons. `summary.json` retains
failed scenarios as well as successful ones; any failure makes the command exit
unsuccessfully. Shared-host delays and SDK rejections must remain visible.

The fixture explicitly chooses `allow_unknown` for simulator oracle inputs,
which do not report free space. It does not reinterpret empty memory as clear.
The K1 fixture permits 0.6 rad ball-bearing/heading offsets because the native
controller turns while positioning its feet; the default match policy is
unchanged. Footprint, uncertainty, age and kick-corridor checks remain enabled.
The SDK's internal kick trajectory and speed are not controlled by the navigation
planner. This fixture does not validate kicking near obstacles, a complete match,
a camera-driven match or operation on a physical robot.

## Recorded validation, 2 October 2026

All five scenarios passed together on marvin. The
[saved results](validation-2026-10-02.json) include the image/scene identifiers,
trace directory and trace hashes. The full sequence measured 1.54 m of robot
travel, 0.81 rad of head-yaw range and 1.70 m of ball displacement.

Reported controller exit took 0.13–0.54 s after cancellation or expiry, including
the delay of the asynchronous SDK status stream. After reported exit, two-second
settling drift was 0.008–0.126 m. These are measured test results, not guaranteed
braking distances or real-time bounds.

That initial sequence stopped when the ball left the allowed kick window. It
therefore
reported a cancelled/failed attempt despite moving the ball; it did not claim
an SDK-completed kick. The subsequent [kick pilot](kick-pilot.md) found that the
native controller
can stay in SHOOTING while chasing and striking again: this phase is not a
single-shot completion contract. The current driver therefore no longer derives
completion from that phase transition; see the pilot's lifecycle follow-up.

Earlier trials exposed stale snapshots, a short command deadline and head RPC
refusals. They stopped as designed. The final run used 20 Hz input, 50 Hz model
updates, a 250 ms command budget and 10 Hz head requests. It demonstrates the
connected path, not repeated-run reliability under all simulator workloads.
Raw trials are retained beside the final trace directory on marvin.

The [single-shot follow-up](validation-kick-lifecycle-2026-10-02.json) validates
the current lifecycle and timing changes. All six pilot shots passed at 20 Hz,
each with one activation and confirmed departure/stop. All five match scenarios
passed; the sequence was rerun after correcting its exit timer to start at the
first stop intention. Reported kick exit took 0.19–0.50 s across these scenarios,
with 0.04–0.11 m of settling drift. Full fresh Walking-readiness confirmation
takes longer than the first inactive VisualKick report; the pilot records both
stages separately. Failed intermediate trials remain in the evidence record.
The dedicated container was stopped after validation. See the
[pilot guide](kick-pilot.md) for ranges, uncertainty and remaining benchmark work.

The [approach, kick and score benchmark](score-benchmark.md) adds six fixed cases
towards both goals, an independent raw-truth evaluator and videos rendered from
recorded physics. All six cases scored in the first complete series. Contact,
goal crossing and execution completion are separate outcomes, with retained
timestamps, hashes and the limits of this small sample.

The same fixture now has an executed **90-case grid**: nine ball positions in a
3 × 3 grid, five seeded robot starts including wrong-side and facing-away
approaches, and both goals. Use `--suite preflight` for six harder approach
cases, `--suite grid` for the full baseline (the new default), or `--suite smoke`
to repeat the original six. `--plan-only` freezes a manifest without simulator
access; `--resume` runs only cases that have never started. The preflight completed
all six sequences with four goals. The full grid completed 86 shot sequences:
30 goals and 56 non-scoring shots at fixed power 1.5. Four failures remain in the
baseline: one approach timeout, one SDK motion failure and two SDK setup failures.
The 49-minute-45-second video includes all cases and has 90 chapters. See the
[recorded results](score-benchmark.md#full-grid-results-2-october-2026) and
[validation](validation-score-grid-2026-10-02.json) for evidence and remaining work.

The core, transport and selected behaviour suites passed **415 tests each** on
Python 3.11 and 3.14, including 23 new actuator/feedback tests. The live relay ran
with the simulator's Python 3.10 and SDK 1.5.6. The dedicated container was stopped
after validation.

Run the deterministic contracts without ROS or the SDK:

```sh
python -m unittest discover -s src/behaviour/test -p 'test_match*.py' -q
```

For the small power/range and completion experiment, see the
[kick pilot guide](kick-pilot.md). It keeps the match runner's policy unchanged
and records SDK status separately from ball movement and deliberate stopping.

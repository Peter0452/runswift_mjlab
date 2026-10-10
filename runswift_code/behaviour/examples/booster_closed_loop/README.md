# Closed-loop Booster navigation

This runner sends checked navigation commands to the simulated T1's **real
vendor motion controller**. MuJoCo moves the robot; the ground-truth bridge
reports that movement to the world model. Navigation reads one immutable view
per tick. It never moves the robot by writing its position.

The runner is deliberately limited to the dedicated `runswift-world-model-sim`
Docker container and the pinned Booster Studio 1.10.5 four-T1 scene. It resets
robot1 before each scenario and places robot2 as a fixed obstacle. Do not run
another motion client or world-model input publisher alongside it.

## Run on marvin

Use the prepared workspace and Jazzy virtualenv from the
[simulator guide](../../../world_model/docs/human/booster-simulator.md). Sync the
current `src/behaviour/` to `behaviour/` and `src/world_model/` to `world_model/`
in that workspace first; those directories are copies, not another Git checkout.
The host needs Python 3.11+, the world model, `msgpack==1.1.2`,
`websockets==15.0.1`, ROS Jazzy and Docker access. The existing virtualenv uses
Python 3.12 with ROS system packages. The container retains its vendor SDK 1.5.6
and Python 3.10; the world model is not installed there.

```sh
cd /home/oliver/runswift-simulation/booster-1.10.5
./start-headless.sh
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=87
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export JAX_PLATFORMS=cpu
export PYTHONPATH="$PWD/behaviour/scripts:$PYTHONPATH"
ros-venv/bin/python behaviour/examples/booster_closed_loop/run.py \
  --scenario all --output closed-loop-results
```

Use a new output directory. The runner creates a fresh world/frame epoch and
motion session for every scenario. `--scenario` also accepts `goal`, `obstacle`,
`cancel`, `command_expiry` or `observation_expiry`. Run on the Docker host: the
command deadlines require the host and container to share Linux monotonic time;
a WebSocket SSH tunnel alone is insufficient for this motion connection.

When running from a repository checkout on an equivalently prepared host,
use `PYTHONPATH="$PWD/src/behaviour/scripts:$PYTHONPATH"` and run
`python src/behaviour/examples/booster_closed_loop/run.py` with the same options.

Afterwards, stop the dedicated simulator:

```sh
docker stop runswift-world-model-sim
```

## What runs independently

- `BoosterBridge` reads ground truth and publishes coherent input batches at
  10 Hz. `WorldModelNode` updates on a steady 20 Hz timer in its own executor
  thread. This continues while navigation is cancelled or command production
  is deliberately stopped.
- `NavigationExecutive` owns the goal, calls `NavigateToPose.tick` with one
  context, and passes the checked body velocity to `MotionRelay`. It stops and
  clears paths on arrival, cancellation, unusable observations or transport
  failure. No legacy second avoidance or clipping pass alters the checked
  command.
- `motion_relay.py` runs as a separate process **inside the simulator container**.
  It explicitly selects `robot1` via `B1LocoClient.InitWithName`; it never selects
  the unnamed physical robot. The container must use an isolated Docker network.
  Its private stdin pipe carries bounded JSON velocity leases.
- The relay checks deadlines every 20 ms, even if navigation or model updates
  stop. A command lasts at most 250 ms; its source observation lasts at most
  350 ms of wall time. The earlier deadline wins. Both are shorter than this
  navigation policy's 500 ms checked command horizon. Sender timestamps are
  preserved, so buffering cannot renew an old command.

`RosSession.context_with_receipt()` returns the tick context and the arrival time
of its last applied input batch together. Reading a view or receiving an exact
duplicate does not refresh that time. The executive checks it before and after
planning. This wall-clock check still works when simulation `/clock` freezes.

Expiry, invalid commands, wrong sessions and reordered commands latch a stop in
the relay. They require a new relay/session to resume. Ordinary cancellation
sends zero immediately and permits a subsequent explicit goal in a healthy
session. EOF and normal shutdown also send zero. The gate rejects excessive or
non-finite velocities rather than silently changing a collision-checked path.

## What each scenario proves

| Scenario | Physical check |
| --- | --- |
| Goal | Walk from (-2, 0) towards (-0.5, 0), reach the configured position/heading tolerance, send zero and settle. |
| Obstacle | Reach (2, 0) by detouring around robot2 at (0, 0); check the measured trajectory against both enclosing footprints. |
| Cancellation | Cancel only after measured travel exceeds 0.25 m; verify an applied zero command and discarded path. |
| Command expiry | Stop calling navigation while world updates continue; verify the independent relay expires the last command. |
| Observation expiry | Stop publishing input and `/clock` while physics and raw evaluation frames continue; verify stale evidence stops motion. |

The JSONL traces contain measured pose, raw ground truth, simulation/wall times,
executive decisions and SDK-applied command receipts. Raw truth is used directly
only for evaluation; navigation gets it through the world model. Checks require
actual movement, obstacle clearance, goal arrival where applicable, zero output,
cleared planning state and less than 0.15 m settling drift over two seconds.
Injected stops must be acknowledged within 100 ms of cancellation or the relevant
expiry deadline. That is a test tolerance, not a hard real-time guarantee.
`summary.json` is written only when all requested scenarios pass.

## Recorded validation

All five scenarios passed together on marvin on 1 October 2026, using Studio
1.10.5, the isolated `virtual-robot:0.6.5-beta` container, vendor SDK 1.5.6 and
the host's ROS Jazzy/Python 3.12 environment. The
[saved summary](validation-2026-10-01.json) records the numeric results. Full
traces remain in
`/home/oliver/runswift-simulation/booster-1.10.5/closed-loop-final-20261001/`.

| Check | Measured result |
| --- | --- |
| Goal / obstacle goal, after settling | 0.227 m / 0.229 m from target |
| Smallest sampled obstacle footprint clearance | 0.486 m |
| Cancellation to applied zero | 2.44 ms |
| Command deadline to applied zero | 16.07 ms |
| Observation deadline to applied zero | 13.63 ms |
| Largest settling displacement across the five scenarios | 0.077 m |

The command-loss scenario uses a 150 ms lease to ensure that its command deadline
expires before its supporting observation deadline. Other scenarios use 250 ms.
These measurements describe this run and profile; they are not controller timing
guarantees. The simulator was stopped after validation.

The automated `test_navigation_execution.py` suite runs without ROS or the SDK.
It checks the real world-model/navigation loop with a simple kinematic plant,
goal/cancellation lifetime, slow planning, broken transport, frozen time and
lease validation/expiry. The live runner supplies the separate vendor-controller
and MuJoCo evidence. Both are needed; a kinematic plant alone does not validate
the real walking controller.

## Limits

The ground-truth stream provides no observed-clear-space evidence. These test
scenarios explicitly choose `allow_unknown`, capped at 0.2 m/s, while preserving
obstacle and field checks. The default navigation policy still requires clear
coverage. The test footprint radii are 0.28 m for robot1 and 0.45 m for robot2;
these are enclosing-disc test settings, not validated bounds for every posture.

The simulator profile adds a 0.20 m planning reserve
(`GlobalPlannerConfig.tracking_reserve_m`) and configures the tracker for low-speed walking. The reserve
also applies when selecting direct shortcuts: a wide detour must not immediately
be replaced by a path grazing the required clearance. It changes route preference,
not measured footprints or the mandatory collision margins. Any escape from the
preferred reserve still has to pass the original collision checks. Existing
callers retain the default zero reserve.

The relay bounds command lifetime, not physical braking distance. SDK calls and
operating-system scheduling are not hard real-time. A wedged vendor controller
or killed relay needs a controller/hardware-level watchdog; Python cannot
promise delivery of a stop to an unresponsive SDK. Camera perception, moving
obstacle prediction, full match behaviour and real-robot trials remain separate
work. No camera input is used by these tests.

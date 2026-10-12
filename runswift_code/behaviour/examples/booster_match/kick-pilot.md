# Small K1 kick pilot

This experiment checks how far the ball travels and what the native controller
reports when we ask it to kick. It uses simulator ground truth, the new world
model and the existing independent SDK actuator. It does not implement the
planned 90-trial approach-and-score benchmark.

## Fixed setup

- Pinned K1 scene and VisualKick V2, as in the [live fixture](README.md).
- Ball centre starts at **(-4, 0, 0.11) m**. Robot starts at **(-4.65, 0) m**,
  facing the positive-X goal at **(7, 0) m**. Its trunk is held at 0.55 m only
  during initial SDK preparation, then released before any kick command.
- Robot2 is held outside the pitch at **(-6, 6) m**, solely to enable the
  simulator's named SDK channels. Only robot1 participates.
- Power values **1.0, 1.5, 2.0** stay within the existing actuator limits.
  These are controller parameters, not calibrated metres or force units.
- Each trial resets the robot, ball and motion/world sessions. There are no
  teleports after release. Inputs and referee permissions are labelled as
  ground truth and scripted respectively.

The application owns independent world updates. Each pilot tick uses one frozen
view for its local ball, pose and fixed goal. It requires the normal kick
uncertainty checks, 150 ms snapshot/state ages and the original input receipt.
Commands last at most 250 ms, bounded also by the 350 ms observation deadline.
The receiver's independent watchdog, feedback expiry and fault latch stay active.

## Two questions, two modes

**Range mode** is the default. It first checks that the ball is within the
initial kick window and the aim is aligned. It uses the same `SingleShot` skill
as the match runner. With measured kick activity, it recognises field-frame ball
movement greater than 0.25 m plus the uncertainty margin from both observations.
It allows 0.35 seconds of follow-through, then sends zero body velocity and no
kick while awaiting fresh feedback confirming controller exit and Walking
readiness for that attempt. Only then is the result `shot_departed_and_stopped`.
The skill never turns an SDK phase edge into `sdk_completed`.

Stale inputs, unavailable estimates and faults stop it earlier. Activation is
limited to 12 seconds in this pilot, with a further two seconds allowed to
confirm stopping. A stopped or failed attempt cannot rearm the actuator. This
fixture never commands another attempt. The match runner uses an eight-second
activation limit by default and the same lifecycle.

**Completion mode** omits this departure stop to inspect the controller's
lifecycle, still with the same bounded timeout and freshness checks. Live traces
show that the controller can chase the moving ball and strike it again while
remaining in phase 1 (SHOOTING). Its total displacement must therefore not be
reported as single-shot range. A return to phase 0 after we disable kicking is
evidence of controller exit, not natural kick completion.

After a stop, the fixture observes passive ball travel for eight seconds.
`range_settled` requires at least 1.8 seconds of progressing, closely spaced
simulation samples with horizontal speed below 0.05 m/s. A frozen stream cannot
prove settling. Maximum displacement, forward travel, lateral error and ball
height are reported separately. Field-boundary contact flags a potentially
truncated range. We do not adjudicate goals here.

Ball movement is only indirect evidence of contact. The current trace has no
foot/ball contact impulses, so `contact_confirmed` stays false. Even a successful
range trial is an approximate shot measurement, not proof of exactly one contact.

## Reproduce

Use the prepared marvin environment and start the dedicated K1 scene as described
in the [live guide](README.md). Sync the current `behaviour/` and `world_model/`
directories first. From `/home/oliver/runswift-simulation/booster-1.10.5`:

```sh
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=87
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export JAX_PLATFORMS=cpu
export PYTHONPATH="$PWD/behaviour/scripts:$PYTHONPATH"
ros-venv/bin/python behaviour/examples/booster_match/run_kick_pilot.py \
  --mode range --input-hz 20 --powers 1 1.5 2 --repeats 2 \
  --output kick-pilot-results
docker stop runswift-world-model-sim
```

Use a new output directory. `--mode completion --powers 1.5 --repeats 1` runs
the separate bounded completion probe; it may produce several contacts.
The pilot permits 1–3 repeats and a maximum 20-second kick timeout. Default
timeout is 12 seconds. World updates run at 50 Hz and the pilot targets 20 Hz.
Input rate is configurable from 5–20 Hz; the tested rate belongs in every result.

JSONL files retain raw truth, original times, world snapshot times, sent intents,
SDK samples and stop reasons. The summary retains unsuccessful attempts. A
non-zero exit means at least one trial did not reach its mode's expected stop
with a confirmed inactive controller (and settled, uncensored travel for range
mode); it does not erase the remaining trials.

Run the deterministic pilot checks without ROS or the SDK:

```sh
python -m unittest discover -s src/behaviour/test -p 'test_kick_pilot.py' -q
```

## Initial results before the lifecycle and timing fixes, 2 October 2026

The six-trial series at 10 Hz produced **four usable range measurements**.
Two attempts stopped on stale snapshots. All six ultimately reported an
inactive controller. The [saved evidence](validation-kick-pilot-2026-10-02.json)
includes every outcome, earlier probes, remote trace paths, hashes and settings.

| Power | Repeat | Observed travel | Forward travel | Largest lateral offset | Outcome |
| --- | --- | --- | --- | --- | --- |
| 1.0 | 1 | 1.17 m | 1.17 m | 0.04 m | Departure stop; ball settled |
| 1.0 | 2 | 1.48 m | 1.43 m | 0.38 m | Departure stop; ball settled |
| 1.5 | 1 | 4.67 m | 4.50 m | 1.26 m | Departure stop; ball settled |
| 1.5 | 2 | — | — | — | Stale snapshot before ball movement |
| 2.0 | 1 | 6.30 m | 5.82 m | 2.43 m | Departure stop; ball settled |
| 2.0 | 2 | 2.80 m* | 2.12 m* | 1.82 m* | Stale snapshot; excluded from usable ranges |

The starred values preserve an interrupted trial's measured movement; it did
not complete the intended departure policy. None of the usable trials reached
the field boundary. The ball remained close to the ground. First movement was
observed 3.14–4.38 seconds after the initial request, including the transition
from Walking to Soccer and foot positioning. Reported controller exit followed
the explicit stop by 0.17–0.31 seconds in those four trials. That timing includes
asynchronous feedback delay and is not a guaranteed physical stopping time.

**No natural SDK completion was observed.** In the clearest completion probe at
power 1.5, the ball travelled about 4.6 m, came almost to rest, and was then
accelerated again after the robot caught up. Phase 1 persisted throughout.
Total displacement reached 9.03 m; that is excluded as a single-shot range.
Phase 0 arrived only after the stale-input stop disabled kicking.

At 20 Hz, an earlier six-trial range series yielded one usable result; four
attempts stopped on stale snapshots and one on command expiry. Reducing input
rate improved this small run without relaxing any deadlines, but it did not
eliminate timing failures. Do not treat these samples as a reliability estimate
or a power-to-distance calibration. The stronger shots' sideways travel also
prevents treating their displacement as accurate goal-scoring range.

The dedicated simulator container was stopped after the pilot. Sixteen new
deterministic pilot checks pass on Python 3.11 and 3.14; the existing 91 match
checks also pass on Python 3.11.

## After the fixes, 2 October 2026

The repeated six-shot series now completes **six out of six** at 20 Hz input.
Every trial has one measured controller activation, observed ball departure,
confirmed controller exit and a settled ball. There are no stale snapshots,
command expiries or SDK faults in this series. The
[lifecycle validation record](validation-kick-lifecycle-2026-10-02.json) retains
these results, trace hashes and the intermediate failures that led to the fixes.

| Power | Travel, repeat 1 | Travel, repeat 2 | Largest lateral offset |
| --- | --- | --- | --- |
| 1.0 | 1.47 m | 1.61 m | 0.59 m |
| 1.5 | 4.66 m | 4.60 m | 1.03 m |
| 2.0 | 7.42 m | 7.47 m | 1.80 m |

These are ground-truth displacements after a bounded activation, not a power
calibration or proof of one foot contact. Stronger shots still show appreciable
lateral error. No field boundary was reached in these trials.

Maximum snapshot age while sending commands was 64 ms, and the largest gap
between commands was 53.3 ms. The same 150 ms snapshot, 250 ms command and 350 ms
observation limits were retained. The warmed synthetic update benchmark on
marvin improved from a 60.1 ms median to 9.1 ms (maximum 63.5 ms to 13.0 ms),
using Blackwell for the same transforms and uncertainty propagation. Whole
geometry operations are compiled together; behaviour reads use a short lock
around the published view and its original receipt instead of waiting for an
update to finish.

Stopping now holds the measured head target before requesting zero-velocity
Walking mode. It retains that acknowledged hold during the transition, because
K1 rejects new head commands then. SDK exit is still measured from feedback;
requests alone are insufficient. The skill's full stop confirmation, including
fresh Walking readiness and all required status receipts, took 1.25–1.76 seconds
in these six shots, within its two-second limit. This is longer than merely
observing VisualKick become inactive.

The initial safety regression exposed 18 cm of drift after reported kick exit
while remaining in Soccer mode. Returning to Walking fixed that case. An
intermediate implementation sent head commands after requesting the mode change
and failed all six trials with SDK error 400; those traces are retained too.
The final safety checks cover the full match sequence, cancellation, command
expiry, observation expiry and referee stop, with the existing stopping limits.

All 491 automated checks pass on Python 3.11 and 3.14, covering the core, transport,
skills, navigation, tactics, actuator and pilot. The standalone distribution
check also passes. This is a small simulator validation, not a reliability claim
for all workloads or a physical robot test.

## Consequences for the larger benchmark

The match runner and pilot now share the explicit activation, departure,
follow-through and confirmed-stop lifecycle. A native one-shot API or reliable
strike event would still be preferable to inferring contact from movement.
Acknowledgement, elapsed duration and controller exit are different from a
scored goal.

Before scaling up, add reliable contact/strike evidence and aiming checks. The
planned grid includes shots of roughly 12 m; this pilot does not establish that
the K1 can score directly from those places. The timing fixes remove the observed
steady update bottleneck but do not establish reliability under every workload.

The world model already supplies the stationary-ball/pose inputs for this pilot.
It should not receive invented SDK completion facts. Reliable departure detection
for camera inputs will need fresh motion estimates and uncertainty checks; a
ground-truth contact/goal evaluator should remain separate from behaviour inputs.
The full grid, both goal directions, camera pipeline and video recorder remain
separate work.

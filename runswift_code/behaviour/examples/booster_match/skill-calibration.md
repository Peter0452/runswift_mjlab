# K1 walking and kicking calibration

Start with [How to run the benchmark](../../../../benchmarks/README.md) for the
short run instructions. Reports and profiles are collected in
[Benchmark results](../../../../benchmarks/results/README.md).

This short fixture measures the existing simulated K1 native walk controller,
the existing `SingleShot` kick skill, and walk–kick–walk transitions. A candidate
receives the normal world-model context and SDK feedback. A separate read-only
recorder supplies the robot pose, ball travel and contact evidence for evaluation.
This measures simulator ground truth; camera perception and physical robots are
separate validation stages.

The default **quick suite has 20 cases**. Use one repeat for development, two or
three for an initial calibration, and more when estimating repeatability.
The **smoke suite has three cases**: forward-to-stop, a power-1.5 kick, and a
walk–kick–walk sequence. Actual run duration is recorded in the validation file;
setup, native mode transitions and passive settling also take time.

## Cases and measurements

| Cases | Purpose |
| --- | --- |
| Forward-to-stop at 0.05, 0.1 and 0.2 | Low-command response, braking time and drift |
| Backward at −0.1 and −0.2 | Direction-specific response and stopping |
| Sideways at ±0.1 | Lateral response, unintended forward movement and yaw |
| Turns at ±0.4 | Turn response, translation drift and stopping |
| Forward–stop–forward | Braking before a two-second hold, then restart latency |
| Forward-to-sideways | Direction-change latency and old-direction overshoot |
| Left turn to right turn | Turn reversal latency and angular overshoot |
| Straight kicks at powers 1.0, 1.5 and 2.0 | Empirical power-to-range lookup |
| Aims at ±0.25 rad, power 1.5 | Aiming bias, scatter and target-plane error |
| Reversed straight kick, power 1.5 | Same measurement towards physical −X |
| Walk–kick–walk towards both directions | Approach, kick activation, exit and resumed walking |

Walk cases hold the command for five seconds. Direction-change cases last eight
seconds; each leg is measured separately. Commands are **native controller
parameters**. The existing application treats them as nominal body velocities,
but this test measures their physical response rather than assuming the numeric
value equals metres/second or radians/second. The enclosing fixture retains the
existing numeric translation limit 0.2, turn limit 0.8 and kick-power limits [1, 2].

Walking results include mean measured body velocity after the first second,
gain per command axis, unintended motion on other axes, nominal velocity error,
position/heading error against integrated commands, motion onset, stopping time
and braking drift. Physical speed uses simulator time; transition latency uses
the host monotonic clock. They are different measurements and remain labelled.

Motion onset requires 150 ms of progressing measured movement above 0.04 m/s
or 0.15 rad/s. Direction response uses a 200–250 ms body-velocity window and a
30-degree heading allowance. Velocity matching requires errors within 25% of
the requested value, with absolute floors 0.04 m/s and 0.1 rad/s. A null matching
time means that condition was never observed; it is not an instantaneous change.
These timing definitions include their evidence windows.

Physical stopping requires 0.8 seconds of progressing samples below 0.03 m/s
and 0.08 rad/s. The reported time ends when that interval has been demonstrated;
it includes the confirmation window. `stop_to_quiet_s` also reports the start of
that subsequently confirmed interval, separating braking from confirmation.
Braking drift is maximum planar displacement
from the first post-stop sample until confirmation. A stop–restart case measures
the first stop only before the next walking request.

Kicks report forward travel, lateral offset, final range, direction error,
endpoint distance error, and lateral error where the ball first passes the
**3 m target plane**. Short shots retain their measured range and have no target
crossing. Contact, ball departure, controller exit and accuracy are separate
facts. Contact windows identify robot–ball contact; they cannot count strikes or
identify a foot. One activation is not proof of exactly one strike.

Transition measurements keep these events separate:

- First walking command to independently measured movement.
- First kick request to observed SDK kick activity and first recorded contact.
- First kick-stop command to inactive kick feedback.
- Kick-stop command to fresh SDK Walking readiness, including mode/status/phase
  samples newer than the stop.
- Approach stopping to kick activity, and kick stopping to resumed movement.

SDK topics have receipt timestamps, not synchronised capture timestamps. Contact
timing is a recorder publication-window estimate. The fixture starts with Walking
already prepared, so initial Stand-to-Walking SDK mode preparation is excluded
from walking-onset time. Native Soccer-to-Walking transitions are measured.
The transition fixture uses the existing navigation planner/tracker and an
explicit 0.15 m / 0.2 rad approach tolerance, followed by the existing kick skill.

## Prepare and run

Planning, measurement tests and offline evaluation need only Python 3.11+ and
the standard library. From the repository root:

```sh
python3 src/behaviour/examples/booster_match/run_skill_calibration.py \
  --suite quick --plan-only \
  --output benchmarks/results/$(date +%F)/k1-native-calibration/runs/plan-$(date +%H%M%S)
python3 -m unittest discover -s src/behaviour/test -p 'test_skill_calibration.py' -q
```

For motion, use the dedicated marvin simulator from the [live guide](README.md).
Sync the current `src/behaviour/` and `src/world_model/` first. Only one motion
fixture may use this scene at a time. The calibration runner uses a shared lock
against other calibration runners; the other fixtures must be stopped explicitly.

```sh
cd /home/oliver/runswift-simulation/booster-1.10.5
bash behaviour/examples/booster_match/start-simulator.sh
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=87 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST JAX_PLATFORMS=cpu
export PYTHONPATH="$PWD/world_model:$PWD/behaviour/scripts${PYTHONPATH:+:$PYTHONPATH}"
ros-venv/bin/python behaviour/examples/booster_match/run_skill_calibration.py \
  --suite smoke \
  --output benchmarks/results/$(date +%F)/k1-native-calibration/runs/smoke-$(date +%H%M%S)
ros-venv/bin/python behaviour/examples/booster_match/run_skill_calibration.py \
  --suite quick --repeats 3 \
  --output benchmarks/results/$(date +%F)/k1-native-calibration/runs/quick-$(date +%H%M%S)
docker stop runswift-world-model-sim
```

Select individual cases with repeated `--case NAME`. Resume an unchanged frozen
plan with `--resume` and the same suite, repeats, selection, policy and configuration.
Existing trial directories are never retried or overwritten, including failures
and interruptions. A deliberate repeat uses a new run directory.

Each trial retains case/environment metadata, controller intentions and SDK
receipts, raw truth and recorded physics. Results retain every planned trial.
Setup failures, SDK failures, falls, missing evidence, non-progressing time and
truth gaps remain visible. A usable kick range additionally requires contact,
one activation, completed execution, fresh return to Walking, settled ball travel
and no field-boundary truncation. Failed trials do not enter calibration tables.
Recorded source, candidate configuration and optional model assets are hashed.
Use `--candidate-revision REVISION` to label a synced tree that has no `.git`
directory. Source hashes also record modifications beyond that revision.

Recompute measurements without ROS, the SDK or MuJoCo:

```sh
python3 src/behaviour/examples/booster_match/run_skill_calibration.py \
  --evaluate-only \
  --output benchmarks/results/2026-10-03/k1-native-calibration/recordings/baseline
```

`results.json` contains individual results and calibration distributions with
sample count, mean, standard deviation and range. Source recordings are verified
against their original hashes before re-evaluation. Keep large traces outside Git.

## Reuse with another policy

Pass `--policy my_policy:make_policy`, optionally `--policy-config config.json`
and `--asset weights.onnx` (repeatable). The factory is called afresh for each trial:

```python
def make_policy(case, field_frame, config):
    return MyPolicy(case, field_frame, config)
```

Its object implements `tick(context, motion, elapsed_s)` and `cancel()`. It returns
the shared `calibration_policy.PolicyStep` with a stage, body velocity, head targets,
optional `(direction, power, ball_x, ball_y)` kick, and status `running`, `completed`
or `failed`. Terminal steps must request stopped motion. Stages `walk`, `approach`,
`kick` and `recovery` allow comparable transition reporting. The fixture supplies
fresh inputs, leases and independent measurements. Policies never receive evaluator
contact or accuracy results. Each trial has a fresh actuator session; the fixture
uses attempt ID `calibration-shot` for the single permitted activation.

For a policy with its own gait/kick execution, select `--actuator module:factory`
and optionally `--actuator-config actuator.json`. The default is the existing
`transport:MatchRelay`, which executes the K1 native controller. An alternative
adapter implements the same motion port (`session`, `send`, `latest`, `stop`,
`close`) and normalises measured feedback to the existing `MotionSample` and
attempt lifecycle. Its factory/configuration/source are recorded alongside the
policy. The candidate remains a K1 in the same recorded simulator scene.

Use the same frozen cases, repeats and environment when comparing candidates.
Calibrate command response and aiming bias within the tested points, then validate
any proposed compensation in a new labelled run. Do not extrapolate a global gain
from one speed or direction. Calibration tables are saved evidence; this fixture
does not automatically change deployed controller settings.

## Initial K1 calibration, 3 October 2026

The [saved calibration profile](../../../../benchmarks/results/2026-10-03/k1-native-calibration/profile.json) contains
44 usable trials: two passes of the original 19 cases, then two repeats of the
added low-command case and both transition cases. Every final-suite trial was
usable. The [validation record](../../../../benchmarks/results/2026-10-03/k1-native-calibration/validation.json)
retains the source/recording hashes, initial failed preflight and environment
paths. The dedicated simulator was stopped after the runs.

One 19-case pass took **373.5 seconds (6.2 minutes)** from the first robot release
to the last observation, including setup between cases. Initial startup/setup
is additional. The default now adds the five-second low-command case and its
setup/observation interval.

These are means from two repeats per walking case:

| Forward command | Measured forward speed | Stop to quiet motion | Braking drift |
| --- | ---: | ---: | ---: |
| 0.05 | approximately 0 m/s | No sustained forward movement | 0.0003 m |
| 0.10 | 0.446 m/s | 0.839 s | 0.163 m |
| 0.20 | 0.571 m/s | 1.058 s | 0.220 m |

The low command did not produce measured forward onset. Backward commands −0.1
and −0.2 produced only −0.004 and −0.006 m/s mean longitudinal motion. Sideways
commands +0.1 and −0.1 produced +0.086 and −0.145 m/s. These responses need
direction-specific calibration; one constant gain would not describe them.
Forward-to-sideways took 0.579 s to demonstrate the new direction, with 0.134 m
continued travel in the old direction. Turn reversal took 0.584 s, with 0.154 rad
angular overshoot. These direction times include the velocity evidence window.

Straight kicks towards +X, with two repeats at each power:

| Power | Mean final ball range | Mean lateral error at the 3 m target plane |
| --- | ---: | ---: |
| 1.0 | 1.489 m | Target plane not reached |
| 1.5 | 4.464 m | +0.448 m |
| 2.0 | 7.184 m | +0.440 m |

The sign is relative to the requested aim. Final lateral offset and direction
error are also retained in the profile, including off-axis and reversed shots.
The native kick has a measurable aiming bias in this setup; two repeats provide
an initial lookup, not a complete repeatability estimate.

Across four +X walk–kick–walk sequences, mean times were 1.978 s from kick request
to observed activity, 4.271 s to contact, 0.144 s from stopping to inactive kick
feedback, 1.671 s to fresh Walking readiness and 1.847 s to resumed physical motion.
The reversed cases have their own distributions. The distinction between inactive
kicking and ready walking is substantial here.

All 19 calibration contract tests passed locally and on marvin. The existing
kick-pilot, single-shot and scoring regressions also passed: **69 distinct tests**
in total. Raw recordings and exact source archives are kept outside Git at the
paths in the validation record. The profile is saved for policy tuning; deployed
walking and kicking settings were not changed by this experiment.

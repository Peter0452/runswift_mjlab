# Lessons: sim-to-real and deployment

Robot data so far: K1 #291 (other robots may differ; treat hardware findings
as #291-specific until another robot shows them). Sources:
`docs/K1_KICK_LESSONS.md` (§4, §9), `docs/K1_REAL2SIM_2026-10-09.md`,
`docs/K1_KICK_TRACKING_NOTES.md`, `docs/evolution/monitor.md`, session memory
(k1-real2sim-findings, k1-dribble-speed, kick-dr-from-amp-walk,
contact-uan-for-k1).

## Parity: make training, benchmark and runner identical

**S1. Benchmark and train the deployed action path.** The runner clipped every
joint target to the joint ranges; training never did. x4 pushed hip roll
0.38 rad past its stop on ~0.6 % of steps; clipped, its kicks went 20–40° off
(runswift first strikes ≤ 15°: 19 % → 86 % with the clip removed). Any runner
transform (clip, filter, limit) must be in training and in the benchmark.

**S2. Train and test delay ranges that include zero.** sty_power/17149 dropped
from 82 % to 47 % accurate without delay; a policy that only works inside its
training delay range is brittle.

**S3. Match the observation frame exactly.** runswift vision reports the ball
in a level, yaw-only frame on the ground; training used the trunk frame until
v49, so a 5–10° lean moved the ball reading 4–9 cm. Mixing trunk-frame episodes
back in (ft_h022) made the policy far worse. The ball origin is between the
feet.

**S4. Check every input slot on the robot before blaming the policy.** "Walks
to the ball but never kicks" was four joint inputs reading 0: `/joint_states`
lacks the head joints. Use `--joints-from-low-state` and check slots at
start-up (`sensor_check.py`).

**S5. Export scales exactly.** ONNX metadata rounded action scales to 3
decimals (0.2125 → 0.213); now 6. A slot-by-slot parity check
(`parity_check.py`, `onnx_parity.py`, `dribble_parity_check.py`) catches this
class of bug; recent models match to ~3e-6.

**S6. Train only on what the camera can see.** Training only ever reports
camera-visible balls; the runner's FOV gate drops detections at impossible
bearings (|bearing| > head yaw limit 0.85 + half FOV ≈ 66°), which took
goal-attempt falls on the official fixture from 36 to 0.

**S7. No odometry on the robot,** so training uses the same rotation-only ball
memory (`memory_odometry=False`); with odometry the head and approach failed
on the robot.

**S8. Caps outside training cause falls.** The real dynamic fall in run 1122
happened at a turn-rate cap of 2.0, outside the trained 1.5. A runner soft
start (caps ramp from 0.5/0.3/0.6 over 4 s) removed a sprint-on-enable fall.
(Kick-loop training caps are 2.0/2.0/3.0 since 2026-10-23.)

## What the robot shows vs sim (#291)

**S9. Measured gaps** (kick runs 2026-10-09, dribble run 2026-10-19):
- Target → position lag ~80 ms on robot and sim: delay is not the gap.
- Real torques exceed the runner's limits and the 30 Nm B-Human ankle clip
  (knee 64–74, ankle pitch 45–52, hip roll 41 Nm); the MuJoCo runner saturates
  ankles / hip roll at 24/25 Nm constantly, so sim2sim is harsher there.
- Real torque fits the commanded PD poorly (knee slope 0.17–0.38 vs sim 0.6);
  knee tracking error +50 %: the weakest-tracking joint.
- Robot-specific asymmetry: left hip pitch p99 ~30 % above right, right ankle
  roll ~50 % above left.
- Knee excess is only within ±2 steps of footfalls: landing impacts. Median
  footfall softer, worst 10 % harder than anything in sim (why steps are loud).
- Cadence gap is task-dependent (kick real 20 % slower, dribble ~15 % faster),
  so it is not a fixed actuator property.
- Vision ~16 Hz (detection every ~41 ms), ball lost 2–13 %; detection jitter
  ~2 mm (training noise is larger).
- Dribble swaA: 1.9 falls per upright minute on the robot vs 0.13 in sim
  (0.80 in the deploy-matched sim).

**S10. The deploy-match config matters.** Dribble swaA collapsed in the
deploy-matched env (0.5 m/s success 0.84 → 0.19); training in it (v16+) kept
falls low. The deploy conditions together cost ~0.14 m/s of dribble speed.

**S11. Don't change domain randomisation because another config differs.**
The kick DR is inherited from the AMP walk, which transfers well. Use the
measured numbers above before changing DR or the runner, with the user's
go-ahead. Contact-UAN (an actuator residual from robot logs) targets the knee
/ PD / impact gaps but needs the sim effort caps raised first and can't model
L/R asymmetry with shared weights; adopt only through the benchmark gate.

## Runner behaviour

**S12. Runner fixes indicated by real data** (2026-10-09): latch falls (now
`FallLatch`, tilt 50°: stay damped until re-enabled upright), debounce
`enable` flickers (0.3–0.6 s drops reset the policy mid-step), detect lost
motor authority (knee 1.5 rad off target at ~6 Nm — external cause, log the
Booster mode), record every loop iteration and mode decision. Fall latch is
done; the others were not implemented as of the last notes.

**S13. The MuJoCo bridge reported the ball in the tilted trunk frame** while
training and the robot use the feet midpoint on the ground (fix pending in the
dribble notes).

**S14. Motion-tracking deploy sim didn't match training** (tracking kick):
the deploy zeroed the trunk error, held the last clip frame, overwrote head
pitch and used its own torque limits; matching these is listed but not done
(`docs/K1_KICK_TRACKING_NOTES.md`).

## Benchmarks outside our sim

**S15. runswift's fixture disagreed with ours for fixable reasons:** the
runner joint clip (above), foot capsules vs mesh, ball relative to the pelvis
vs between the soles, default caps 0.5/0.3/0.6 while B-Human walks uncapped.
`scripts/tools/rsw_aligned.sh` runs it aligned; official numbers are kept
separately. Ask before changing the official fixture.

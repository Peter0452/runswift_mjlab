# Deployment contract: training ↔ k1_policy_runner

Every policy here is meant to run on the real Booster K1 through
`../k1_policy_runner` (ONNX at 50 Hz). This page is the readable contract
between training and the runner: what each policy sees and outputs, and how the
runner must reproduce it. **If you change anything on this page in training,
the runner must change the same way, and parity must pass before the model
ships.** (The runner repo itself is not edited from this repo's work; record
the needed runner change and its owner.)

Sources: `docs/K1_KICK_LOOP_POLICY_IO.md` (kick loop, detailed),
`../k1_policy_runner/python-implementation/DRIBBLE_POLICY_IO.md` (dribble),
`docs/STRIKER_SELF_PLAY_PLAN.md` §3 (self-play / controller),
`knowledge/lessons/sim2real.md` (why each rule exists).

## 1. Shared by every K1 joint policy

| Item | Value | Notes |
|---|---|---|
| Rate | 50 Hz (training: 200 Hz physics, decimation 4) | |
| Outputs | 22 joint position targets: `target = default + scale × action` | joint order below |
| Default pose | hip pitch −0.4, knee 0.8, ankle pitch −0.4, shoulder roll ∓1.4, elbow yaw ∓0.4, rest 0 | from ONNX metadata |
| Action scale | head 0.375, arms 0.35, hip pitch 0.2125, hip roll 0.2375, hip yaw 0.1197, knee 0.35, ankle 0.1915 | exported with 6 decimals (3 was a bug) |
| PD gains | legs kp 80 / kd 4, ankles 50 / 2, arms 10 / 1, head 4 / 0.25 | from ONNX metadata; randomised ×0.8–1.2 in training |
| Joint-target clip | runner clamps to the joint ranges (`Q_ABS_LIMITS`); training does the same (`_deployment_match`) | a missing clip cost x4 its accuracy (lesson S1) |
| Leg torque | training hard-clips at B-Human's 50 / 50 / 30 / 60 / 30 / 30 Nm (hip pitch, roll, yaw, knee, ankle pitch, roll) | `k1/deploy/contract.py` `LEG_TORQUE_CLIP`; loaded limits unknown, keep one table |
| Motor delay | training 0–40 ms (includes zero), held per episode | the runner adds none; lesson S2 |
| Observation noise | gyro ±0.2, gravity ±0.05, joint pos ±0.01 (+ bias ±0.015), joint vel ±1.5 | training only; the runner adds none |
| Observation history | none | adding history is a runtime change |

Joint order (all 22-joint blocks): 0 head yaw, 1 head pitch, 2–5 left shoulder
pitch / shoulder roll / elbow pitch / elbow yaw, 6–9 right arm (same order),
10–15 left hip pitch / hip roll / hip yaw / knee / ankle pitch / ankle roll,
16–21 right leg (same order). Read joints from `/low_state`
(`--joints-from-low-state`): `/joint_states` was seen without the head joints.

## 2. Ball pipeline (kick loop, dribble, self-play)

| Step | Training | Runner |
|---|---|---|
| Frame | ball on the ground, level yaw-only frame, **origin between the feet** (2 cm jitter) | vision `position_projection` (runswift `base_link`) |
| Seen | ball centre inside the head camera view (±0.606 rad × ±0.367 rad from `Head_2`) | a detection younger than `--ball-hold-s` |
| Detection noise | σ = 0.03 m + 0.05 × distance; dropout 2–5 %; delay 0–4 steps; frame hold 2–4 steps (dribble) | real vision (~16 Hz, 2–13 % lost) |
| Memory | last sighting turned by **IMU yaw only** (no odometry, `memory_odometry=False`) | same rule |
| Lost rule | lost after 0.5 s in view with no detection, or 1.5 s with none; then a **virtual ball** beside the robot on the remembered side (kick: close, dribble: 1.2 m), age 0 | same rule; `lost_rule_parity.py` |
| FOV gate | training only reports camera-visible balls | runner drops detections at impossible bearings (> 66°) |
| Never seen | zeros, age 0 | zeros, age 0 |
| Ball model | `K1_BALL`: ours (0.08 m / 0.1 kg, randomised) by default; `bhuman` (0.095 m / 0.29 kg) opt-in | the real ball |

## 3. Policy families

The slot tables below are also code: `src/k1/deploy/obs_layout.py`, checked
against the golden models by `tests/test_deploy_obs_layout.py`.

### kick_loop_v1: kick loop (83 → 22)
Task `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`; runner
`policy/kick_loop_policy.py`, `start_kick.sh`.

| Slots | Content | Runner source |
|---|---|---|
| 0–5 | gyro, gravity (trunk frame) | IMU |
| 6–71 | joint pos − default, joint vel, previous raw action | low_state, runner |
| 72–74 | ball xy, memory age exp(−t / 2 s) | ball pipeline |
| 75–77 | speed caps \|vx\|, \|vy\|, \|wz\| | `--kick-speed-limits` (soft-start ramp over 4 s) |
| 78–79 | kick direction (cos, sin) from the last-seen ball | `--kick-dir-mode field \| through_ball` |
| 80–82 | range one-hot < 4 / 4–8 / ≥ 8 m | `--kick-range` |

- **Head:** actions 0–1 are overridden by a **scripted ball tracker**, identical in
  training and the runner (`--kick-head track`).
- **Caps:** training caps since 2026-10-23 are the chase caps (vx ≤ 2.0 / 1.75 back,
  vy ≤ 2.0, wz ≤ 3.0). Never run the robot above the trained caps (a wz 2.0 run
  outside the then-trained 1.5 fell).

### dribble_v1: dribble with kick mode (83 → 22)
Task `Mjlab-Velocity-Dribble-Amp-DA-Muon-Booster-K1`; runner
`policy/dribble_policy.py` (subclass of the kick-loop policy), `start_dribble.sh`.
Same 0–73 as the kick loop, but:

| Slots | Content (differs from the kick loop) |
|---|---|
| 74 | memory age exp(−t / **0.6 s**); 0 while lost |
| 75–77 | caps vx 0.3–1.2, vy 0.2–1.0, wz 0.4–1.25 (`--dribble-speed-limits`) |
| 78–79 | commanded ball direction (robot yaw frame); kick direction in kick windows |
| 80 | stop flag; in kick windows the **kicked** flag (0 → 1 once the ball has left) |
| 81 | commanded ball speed 0.2–1.5 m/s |
| 82 | kick flag (v22+ models only) |

- **Head:** the network drives the head itself; the runner passes actions 0–1 through.
- Loading a v20+ checkpoint needs the run's `DRIBBLE_GENES` (discriminator size).
- Run-time modes (kick / stop / dribble via buttons or a topic) exist in the runner
  but are untested on ROS.

### Self-play flat striker (86 → 22)
Kick-loop slots 0–82 + **83–84 opponent xy** (vision robot detection) + **85 opponent
seen**. The runner's kick-loop policy accepts 83 or 86 inputs; with 86 it appends
zeros (opponent unseen) and uses the full head sweep (yaw 0.95). Deployed
`k1_kick_loop_swa_v15v16_9100.onnx`.

### Striker controller (88 + GRU state, 5 Hz)
Inputs: the 86 above + current skill + time since switch. Outputs every 0.2 s:
kick / walk choice, direction, range or walk speed. ONNX `obs [1, 88]` + `h_in
[1, 1, 128]` → `actions` + `h_out`; the runner holds the state and zeroes it at
every striker takeover. Aim directions are held fixed in world between decisions
(IMU yaw). Not yet integrated into the runswift behaviour (plan §7).

### Walk (AMP)
Gold walk `amp_models/model_9950.onnx` (= `wwcmu50_roughft/…stageA/model_9950`),
also the striker's walk skill. Its I/O follows the AMP walk task; document it here
when the walk itself is redeployed.

### B-Human port
59 inputs, 12 leg outputs + gait frequency, its own engine. Runs in our sim
through `play_bhuman_kick.py`; not a deployment target of this repo.

## 4. Before a model ships

1. Golden safety net (`tests/golden/README.md`) passes.
2. Parity, training vs runner: `parity_check.py` (kick loop) or
   `dribble_parity_check.py`, `onnx_parity.py`, `lost_rule_parity.py`. Expected:
   ONNX vs PyTorch ≤ ~4e-6, joint targets identical except the documented cases
   (episode-start ball memory, lost-rule edge cases, runner joint clamp).
3. Runner sim: `sim2real_bench.py`, `gait_bench.py`, `dribble_bench.py`
   (`mujoco_runner_main.py ... --headless`).
4. Model card in `knowledge/models.md`: checkpoint, ONNX, task, contract version,
   bench and parity results.
5. Promotion rule (2026-10-23): robot test may use experimental training-only
   methods if all gates pass; runtime changes need your OK; match deployment uses
   adopted methods only for runtime changes.
6. On the robot: `sensor_check.py` first; record with `--kick-record` /
   `--record-kick-obs`; analyse with `kick_record_analyze.py`, `real_sim_compare.py`;
   add findings to `knowledge/lessons/sim2real.md`.

## 5. Runner items known but not done

From real data (2026-10-09, `docs/K1_REAL2SIM_2026-10-09.md`): debounce `enable`
flickers; detect lost motor authority; log every loop iteration and the Booster
mode. Done: the fall latch (`FallLatch`, 50° tilt). The MuJoCo bridge reports the
ball in the tilted trunk frame (training and the robot use the feet midpoint):
fix pending.

## 6. Changing the contract

A change to any row above is a **runtime change**:
1. Make it in training and in the contract code: `src/k1/deploy/contract.py`
   (rate, joint order, default pose, scales, PD, clips, delay) or
   `src/k1/deploy/obs_layout.py` (actor slots). `tests/test_deploy_contract.py`
   and `tests/test_deploy_obs_layout.py` check training against them.
2. Write down the matching runner change (file, function) and who makes it.
3. Export with the contract in ONNX metadata; run parity until it passes.
4. Mark the run `research` until the runner side exists; only then `deployable`.
5. Update this page and say so in the commit.

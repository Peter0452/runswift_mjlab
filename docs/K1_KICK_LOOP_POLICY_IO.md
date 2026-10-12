# kick_loop_v1 — policy inputs and outputs

Reference for the K1 kick-loop policy (`Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`,
runswift_mjlab) as trained and as run on the robot by `KickLoopPolicy`
(`policy_runner/policy/kick_loop_policy.py`). Values were read from the
training config on 2026-10-03 (stage3 v53 config, robot candidate
`k1_kick_loop_v53_model_10700.onnx`); the ONNX metadata of each exported model
carries the default pose, action scale and PD gains it was trained with.

The policy runs at **50 Hz** (training: 200 Hz physics, decimation 4). Each
step it reads **83 numbers** and writes **22 actions**.

## 1. Observation vector (83)

Order is fixed; slot numbers are what the ONNX model sees. Joint order for all
22-joint blocks is the robot's JointIndex order (section 4).

| Slots | Name | Units / range | Training source | Robot source (runner) |
|---|---|---|---|---|
| 0–2 | Trunk angular velocity (x, y, z) | rad/s | IMU site at the trunk origin (= trunk body frame) | `/imu/data` `angular_velocity`, or `/low_state` `imu_state.gyro` with `--imu-from-low-state` |
| 3–5 | Gravity in the trunk frame | unit vector; upright = (0, 0, −1) | Simulated trunk orientation | `compute_projected_gravity(roll, pitch)` from the IMU |
| 6–27 | Joint positions − default pose | rad | Sim joint positions + per-joint encoder bias | `/joint_states` (by name), or `/low_state` `motor_state_serial` (by index) with `--joints-from-low-state` |
| 28–49 | Joint velocities | rad/s | Sim | Same source as positions |
| 50–71 | Previous action (raw network output) | unitless | Last action | Last action (`_last_action`) |
| 72–73 | Ball x, y in the level ground frame (base_link) | m; x forward, y left | See 1.1 | See 1.1 |
| 74 | Ball memory age | exp(−t_since_seen / 2 s), in (0, 1] | 1 while seen | 1 while seen; 0 before the first sighting |
| 75–77 | Speed limits: max \|vx\|, \|vy\|, \|wz\| | m/s, m/s, rad/s | Random per episode: vx 0.3–2.0 (backward capped at 1.75), vy 0.2–1.5, wz 0.4–1.5 (v34+; v33 and earlier: 0.3–1.2, 0.2–1.0, 0.4–1.25) | Fixed: `--kick-speed-limits vx,vy,wz` (default 0.5,0.3,0.6) |
| 78–79 | Kick direction (cos φ, sin φ) | unit vector in the robot's heading (yaw) frame | Direction from the last-seen ball to the target | See 1.2 |
| 80–82 | Kick range one-hot (short, medium, long) | {0, 1} | Target distance < 4 m / 4–8 m / ≥ 8 m from the last-seen ball | Fixed: `--kick-range short\|medium\|long` |

### 1.1 Ball (slots 72–74)

Training:
- **Frame (v49+)**: the ball relative to the trunk origin projected onto the
  ground, rotated by trunk **yaw only** — the same level, yaw-only frame as
  runswift vision's `base_link`. Models before v49 used the full trunk
  orientation (a 5–10° lean moved the reading 4–9 cm); do not deploy them.
- **Seen**: the ball centre is inside the head camera's view, measured from
  the `Head_2` frame: horizontal half-angle 0.606 rad, vertical half-angle
  0.367 rad (CAM_ANGLE_X/Y = 1.211 × 0.733 rad), camera pitch 0. While seen the
  slot is the true ball xy plus Gaussian noise, σ = 0.03 m + 0.05 × distance
  (per axis, fresh each step).
- **Detection noise (v48+, actor only)**: 2 % of in-view steps drop the
  detection, and the detection is delayed by 0–2 policy steps (0–40 ms, held
  per episode). Rewards use the true visibility.
- **Not seen**: the last sighting in the level frame, turned by the yaw change
  since (no translation: the robot has no odometry), `memory_odometry=False`.
- **Age**: exp(−t / 2 s); 1 while seen.
- At reset the ball spawns 1–4 m away within ±0.4 rad of the heading.

Robot (runner):
- Ball from `/booster_vision/detection` (`vision_interface/Detections`), the
  first object labelled ball: `position_projection` (robot-base frame, metres),
  falling back to `position`. runswift vision computes it by projecting the
  bottom-centre of the bounding box onto the ground using `/head_pose`.
- A detection counts as current for `--ball-hold-s` (default 0.2 s). After
  that, the last detection is turned by the IMU yaw change since it was seen
  (as in training).
- Age from detection arrival times (`time.monotonic()`), not image stamps.
- Optional `--reject-clipped-ball`: a ball box whose short side is < 0.8 × its
  long side (cut by the image edge) is treated as not seen. Off by default.

### 1.2 Kick direction (slots 78–79)

Training: the direction from the last-seen ball to the target, rotated into
the robot's yaw frame. A new target is placed 1–10 m from the ball after each
goal (bins 1–4, 4–8, 8–10 m, equally likely).

Robot, `--kick-dir-mode`:
- `field` (default): `--kick-heading-deg` relative to the robot's heading when
  the policy starts (or is re-enabled), tracked with IMU yaw:
  φ = heading − (yaw − yaw₀). 0 = the start heading, + = left. Depends on IMU
  yaw not drifting.
- `through_ball`: the robot-to-ball direction every step (kick along the
  approach line; no IMU heading).

### 1.3 Observation noise in training (not added by the runner)

| Term | Uniform noise |
|---|---|
| Angular velocity | ±0.2 rad/s |
| Gravity | ±0.05 |
| Joint positions | ±0.01 rad (plus a fixed per-joint encoder bias ±0.015 rad per episode) |
| Joint velocities | ±1.5 rad/s |
| Ball | Gaussian, 0.03 m + 0.05 × distance; 2 % dropout; 0–2 step delay |
| Other slots | none |

No scaling or clipping is applied to any observation term, in training or in
the runner. There is no observation history; the only sensor delay in training
is the 0–2 step ball-detection delay.

## 2. Outputs (22) and joint targets

`target_i = default_i + scale_i × action_i`, sent as a position target with
the trained PD gains. Training does not clip actions or targets; the runner
clamps targets to the joint ranges (`Q_ABS_LIMITS`, same ranges as the MJCF).

| Joint group | Default pose (rad) | Action scale | kp | kd | Effort limit in training (Nm) |
|---|---|---|---|---|---|
| Head yaw, pitch | 0, 0 | 0.375 | 4 | 0.25 | 6 |
| Shoulder pitch L/R | 0, 0 | 0.35 | 10 | 1 | 14 |
| Shoulder roll L/R | −1.4, +1.4 | 0.35 | 10 | 1 | 14 |
| Elbow pitch L/R | 0, 0 | 0.35 | 10 | 1 | 14 |
| Elbow yaw L/R | −0.4, +0.4 | 0.35 | 10 | 1 | 14 |
| Hip pitch | −0.4 | 0.2125 | 80 | 4 | 68 |
| Hip roll | 0 | 0.2375 | 80 | 4 | 76 |
| Hip yaw | 0 | 0.1197 | 80 | 4 | 38.3 |
| Knee pitch | 0.8 | 0.35 | 80 | 4 | 112 |
| Ankle pitch | −0.4 | 0.1915 | 50 | 2 | 38.3 |
| Ankle roll | 0 | 0.1915 | 50 | 2 | 38.3 |

The runner reads default pose, action scale and gains from the ONNX metadata.
Models exported before 2026-10-02 had the scales rounded to 3 decimals
(0.213, 0.237, 0.120, 0.191); re-export to get the exact values.

### 2.1 Head (actions 0–1 are overridden)

The network still outputs head actions, but both training and the runner
replace them with a scripted tracker (same code, checked numerically):

- **Track**: aim at the ball estimate in slots 72–73 from the head pivot
  (0.0056, 0, 0.2149) m in the trunk frame, ball centre 0.47 m below the trunk
  origin; yaw = atan2(dy, dx) clamped to ±0.85; pitch = elevation + 0.18 rad
  (look below the ball) − camera pitch, clamped to [−0.25, 0.82]
  (+ = looking down).
- **Lost close**: ball unseen for 0.2 s and the estimate within 1.5 m → pitch
  0.82 (look down); after 0.5 s also sweep yaw.
- **Lost far**: unseen for 0.5 s → sweep yaw ±0.8 rad (3 s period) and pitch
  0.55 ± 0.2 (1.5 s period). The runner also sweeps before the first sighting.
- **Smoothing**: low-pass 0.3 per step, at most 0.06 rad per step.
- Training only: in 20 % of episodes the head sweeps regardless of the ball,
  so the policy copes with a head it does not control.

Runner `--kick-head`: `track` (default), `fixed` with
`--kick-head-angles yaw,pitch`, or `policy` (network output, for models
before v21). `set_head_target()` switches to fixed angles at run time.

## 3. Training randomization (actor-relevant)

| What | Range |
|---|---|
| Command (policy→motor) delay | 2–8 physics steps (10–40 ms), held per episode |
| PD gains | kp, kd × 0.8–1.2 |
| Encoder bias | ±0.015 rad per joint |
| Foot friction | 0.7–1.4 (v48c+; was 0.75–1.25) |
| Trunk / limb inertia, CoM | ±5 %, CoM ±5 cm (trunk) / ±2.5 cm (limbs) |
| Pushes | every 1.5–4 s: velocity ±0.35 m/s (x, y; v50d+, was ±0.28), ±0.2 m/s (z), ±0.52 rad/s (roll, pitch), ±0.78 rad/s (yaw) |
| Bumps near the ball (v50d+) | within 1 m of the ball, 10 % chance every 0.5–1 s: ±0.25 m/s (x, y), ±0.3 rad/s (roll, pitch) |
| Ball (v34+; config: mass alpha −0.347…0.458, sliding ×0.6–1.4, rolling ×0.5–2.5, solref 0.03–0.08 / 0.08–0.4) | mass ×0.5–2.5 of 0.10 kg (0.05–0.25 kg), sliding friction ×0.6–1.4, rolling resistance ×0.5–2.5, contact softness / bounce (solref timeconst 0.03–0.08, dampratio 0.08–0.4); radius fixed 0.08 m. v33 and earlier: mass ×0.7–1.4, sliding ×0.7–1.3, rolling ×0.6–1.6, no bounce randomization |
| Terrain | v48+: 60 % flat, 40 % gentle bumps (0–2 cm, 5 mm steps, 0.2 m spacing), 16 m patches; play / eval on the flat plane unless stated |

## 4. Joint order (JointIndex, all 22-joint blocks)

0 AAHead_yaw, 1 Head_pitch, 2 Left_Shoulder_Pitch, 3 Left_Shoulder_Roll,
4 Left_Elbow_Pitch, 5 Left_Elbow_Yaw, 6 Right_Shoulder_Pitch,
7 Right_Shoulder_Roll, 8 Right_Elbow_Pitch, 9 Right_Elbow_Yaw,
10 Left_Hip_Pitch, 11 Left_Hip_Roll, 12 Left_Hip_Yaw, 13 Left_Knee_Pitch,
14 Left_Ankle_Pitch, 15 Left_Ankle_Roll, 16 Right_Hip_Pitch, 17 Right_Hip_Roll,
18 Right_Hip_Yaw, 19 Right_Knee_Pitch, 20 Right_Ankle_Pitch,
21 Right_Ankle_Roll.

Training (mjlab) uses the same order. On K1, `/joint_states` reports the
shoulder pitches as `ALeft_Shoulder_Pitch` / `ARight_Shoulder_Pitch` (now
accepted as aliases) and was seen without the head joints; `/low_state`
`motor_state_serial` gives all 22 by index (`--joints-from-low-state`).

## 5. Verification

- `parity_check.py` (runs the training env and the runner side by side): all
  observation slots identical except the ball at episode start when the ball
  spawns out of view (training memory starts at the spawn position, the runner
  has none); ONNX vs training policy ≤ 3e-6; joint targets identical except the
  runner's joint-range clamp (hip roll, ~1.6 % of steps).
- `sensor_check.py` on the robot: prints what the policy will see (gravity,
  gyro, head and shoulder joints, ball position, detection rate and
  camera-to-runner latency). Expected: upright gravity ≈ (0, 0, −1); nose-down
  15° → gravity x ≈ +0.26; right side down 15° → gravity y ≈ −0.26; gyro in
  rad/s.
- `--record-kick-obs PATH` saves every step's 83 inputs, raw actions, sent
  targets, ball-lost time and has-ball flag to `PATH.npz` for replay.

## 6. Typical robot command

```bash
python3 policy_runner_main.py kick_loop_v1 \
  --model-path ../kick_loop_models/k1_kick_loop_v53_model_10700.onnx \
  --kick-head track --kick-dir-mode through_ball \
  --kick-range medium --kick-speed-limits 0.8,0.5,0.9 \
  --imu-from-low-state /low_state --joints-from-low-state \
  --record-kick-obs runs/kick_rec
```

## 7. Model history relevant to deployment

| Model | Notes |
|---|---|
| v31/5450 | old robot candidate; trunk-frame ball (pre-v49) |
| v47/8800 | strongest kick of the trunk-frame models — do not deploy (ball frame) |
| v49/9900 | first level-frame (base_link) model |
| v50d/10200 | + pushes / near-ball bumps; smoothest kick in the runner sim |
| **v53/10700** | **current candidate**: lean at speed +0.7° (was +2.2°), flat 91.5 % within 20° / 1.05 goals, long kicks 5.18 m/s (nominal ball), walking jitter 0.073 (gold walk 0.083) |

Speed limits in training (v34+): vx 0.3–2.0 (backward capped at 1.75), vy 0.2–1.5, wz 0.4–1.5. The runner's `SPEED_LIMIT_RANGES` on branch `kick` still needs this update.

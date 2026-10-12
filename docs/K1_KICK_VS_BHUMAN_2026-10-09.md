# Our K1 kick loop vs B-Human's K1 kick (2026-10-09)

Side by side, from the code: ours is the stage-3 task
`Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1` with the champion
h022_c2_18450's genes; B-Human's is `MachineLearning/IsaacGymRL`
(`envs/K1_Ball.yaml`, `envs/t1_ball.py`). The older
`K1_KICK_BHUMAN_COMPARISON.md` predates most of our current setup.

## 1. Architecture

| | Ours | B-Human |
|---|---|---|
| Policies | **One** policy: search, approach, kick, recover | **Separate** kick policy; a walk policy (or scripted waypoints in the runswift harness) brings the robot to within about 1.1 m |
| Kick episode start | Ball 1–4 m away (20 % far 4–10 m, 30 % any bearing, 15 % unknown position), or mid-kick from recorded clips (25 %) | Ball 0.4–1.5 m in front (far start 0.6–1.5 m); 3 kicks per 30 s episode, ball reset after each |
| What drives the arms / head | Policy outputs all 22 joints; the runner overrides the head (ball tracking) | 13 outputs: 12 leg joints + **gait frequency**; arms are scripted from the sole positions; head scripted |
| Gait timing | Free (no clock); AMP style from walk clips | **Gait clock** (cos / sin of a phase) in the input, frequency chosen by the policy |
| Network | 512-256-128 ELU, actor and critic | 256-256-128 ELU |

## 2. Simulation and robot model

| | Ours | B-Human |
|---|---|---|
| Simulator | MuJoCo (mujoco_warp), dt 5 ms, decimation 4 → 50 Hz | Isaac Gym PhysX TGS, dt 2 ms, decimation 10 → 50 Hz |
| Robot model | Whirlwind K1, foot **mesh** collider | Booster URDF with **box feet**, left / right bias variants |
| PD gains | kp 80 / kd 4 on all leg joints (×0.8–1.2 randomized) | kp 80 hip / knee, 50 ankle pitch, 60 ankle roll; kd 4 / 2 / 2 (±5 %, ankle ±10–20 %) |
| Torque limits | Effort limits 68 / 76 / 38 / 112 / 38 / 38 Nm, **soft** penalty above B-Human's clip | **Hard clip** 50 / 50 / 30 / 60 / 30 / 30 Nm |
| Armature | Per motor type (0.028–0.096) | Same values |
| Actuation delay | 0–40 ms per step (lag 0–8 physics steps, hold prob 0.3) | None modelled |
| Joint friction | none | DR 0–2 |

## 3. Observations

| | Ours (83) | B-Human (59) |
|---|---|---|
| Body | gyro 3, projected gravity 3 | gravity 3, gyro 3 |
| Joints | position 22, velocity 22, last action 22 | position, velocity (scaled 0.1), last action 13 |
| Ball | xy from the soles midpoint (camera model: FOV, memory, lost rule) + memory age | xy (noise grows with distance, odometry noise), **last ball position 2**, **ball velocity 2** (scale noise 0–2×) |
| Task | speed caps 3, kick direction 2, range one-hot 3 | direction angle + sin / cos, **expected launch speed** (continuous range), strong-kick flag, inaccurate flag, allow-deviation flag |
| Gait | none | clock cos / sin |
| Critic extras | true ball, etc. | base mass, linear velocity, height, push forces / torques, kick-pose counters |

## 4. Rewards

**Ours: 54 active terms**, plus the AMP style reward (weight 0.3) and the
far-cap tracking template. Main ones:

- Kick outcome: `long_kick_power` 4000, `kick_goal` 1500, `style_advantage`
  1500, `kick_rest_accuracy` 1000, `kick_direction` 900, `kick_vel` 900,
  `long_kick_speed_linear` 800, `kick_vel_accurate` 300, `kick_lined_up`
  200, `kick_dir_alignment` 50; `long_kick_underpower` −300,
  `kick_double_touch` −200, `kick_fall` −2500.
- Approach / search: `approach_close` 100, `approach_align` 80,
  `search_turn` 10, `walk_speed` 5, `walk_speed_track` 6,
  `walk_speed_limit` −20, `approach_bad_contact` −20, ball avoidance −5.
- Safety / posture: `fall` −1000, `alive` +2, `trunk_tilt` −20,
  `walk_stance_width` −250, `knee_valgus` −200, `foot_flat` −200 (60 ms
  settle), `touchdown_speed` −15, `torque_over_soft_limit` −100,
  `dof_pos_limits` −10, `action_rate` −0.15, plus small terms.
- Aim shape: kick direction σ = 0.35 rad (Gaussian on the angle); long
  kicks σ² = 0.05 rad².
- Speed per range: 3 bins (short < 4 m, medium 4–8, long ≥ 8); rolling
  model `sqrt(2 · 0.95 · d)`; rest-position reward exp(−miss / 2 m).

**B-Human: about 29 terms**, no AMP:

- Kick: `ball_kick_direction` 10 (Gaussian, σ 1 → **0.05** rad² for final
  training, a 3× penalty for wrong directions late, scaled by kick pose and
  sole yaw), `ball_kick_velocity` 4 (Gaussian on expected − actual launch
  speed, σ scale 1 → **0.5**), `ball_kick_velocity_strong` 5 (linear in
  speed × direction), `ball_walk_speed` 2 (walk toward the ball, vision cone,
  rotation logic), `ball_walk_target_overshoot` −100 → 0, `ball_sole_yaw`
  (side-foot target 90°, σ 1 → 0.1).
- Regularisation: terminate −100, base height −40, orientation −5,
  torques −2e-4, **torque tiredness −1e-2, power −2e-3**, lin vel z −2,
  ang vel xy −0.2, dof vel / acc, root acc, **action rate −1**, limits,
  collision −1, feet slip / yaw / roll / distance / pressure / height,
  **feet swing 3** and **gait phase −0.1** (clock-based gait).
- Rolling model `sqrt(2 · 0.3 · d)` (B-Human's ball physics, friction 0.3);
  continuous range 0.5–20 m.

## 5. Terminations and episodes

| | Ours | B-Human |
|---|---|---|
| End | time out (30 s), fell over, illegal contact, NaN | time out (30 s), base height < 0.30 (target height randomised 0.4–0.6) |
| Contacts | illegal contact terminates | penalised on trunk, hips, shanks, ankles |
| Kicks per episode | continuous loop (new target after each kick) | 3 kicks, then reset |

## 6. Randomisation

| | Ours | B-Human |
|---|---|---|
| Terrain | 60 % flat, 40 % 0–2 cm bumps | 60 % plane, 20 % random **7.5 cm**, 20 % discrete 2 cm (trimesh) |
| Ground friction | foot 0.7–1.4 | **0.3–1.5** (ground), terrain friction additive 0.3–1.0 |
| Contact | solref / solimp ranges (stiffness 0.006–0.03) | **compliance 0.5–1.5, restitution 0.1–0.9** |
| Mass / CoM | trunk / limb inertia ±5 %, CoM ±5 / 2.5 cm | base mass **±20 %**, base CoM **±10 cm**, others ±2 % / ±5 mm |
| PD | kp, kd ×0.8–1.2 | ±5 % (ankle ±10–20 %), dof friction 0–2 |
| Encoders | bias ±0.015 rad | offsets pitch 0.02, roll 0.01, other 0.005 |
| Pushes | velocity pushes (±0.35 m/s, rotations); near-ball bumps 10 % | force 0–5 N + torque 0–2 Nm for 2 s every 5 s; velocity kicks 0–0.3 m/s every 3 s |
| Latency | **0–40 ms** | none |
| Ball | radius 0.07–0.13 m, mass 0.05–0.45 kg, friction, bounce | radius 0.095 ± 0.01, mass 0.29 ± 0.01 |
| Initial state | from walk motion clips (moving) | default pose + noise, ball velocity 0–7.5 m/s at init |

## 7. Perception model in training

| | Ours | B-Human |
|---|---|---|
| Camera | FOV ±35° × vertical limit, head tracking, dropout 2 %, delay 0–2 steps, noise 3–5 cm, memory with lost-ball rule | No FOV; ball always observed with distance-scaled noise (up to 2 m in x at 10 m), odometry noise |
| Ball velocity | not observed | observed (noisy, scaled 0–2×) |
| Kick-moment robustness | — | **ball frozen in the input after the kick** (20 %) |
| Moving ball | off (v51 tried) | random resets, velocity adds, incoming balls up to 7.5 m/s |
| Unknown ball | 15 % unknown starts, unseen relocations | — |

## 8. Training algorithm and schedule

| | Ours | B-Human |
|---|---|---|
| Algorithm | PPO + AMP discriminator (style weight 0.3), Muon optimiser, symmetry augmentation | PPO with a **symmetry loss** (coef 1e-2), adaptive learning rate |
| Learning rate | 1e-3 | adaptive 1e-4–1e-2 (later 1e-5) |
| Entropy | 0.005 | −0.01 with a target entropy range (−11…−10, later −16.5…−16) |
| KL | 0.004 | 0.01 → 0.003 |
| γ / λ | 0.995 / 0.95 | 0.98 / 0.95 |
| Epochs / batches | 5 epochs, 4 mini-batches, 24 steps | 20 mini-epochs, 24 steps |
| Schedule | evolutionary loop (genes, reward templates, contexts), speed-cap ramp, soft-landing curriculum | **manual staging**: reward sigmas wide → tight, penalties and robustness probabilities raised late, entropy and lr lowered |

## 9. Where each is better today (measured)

runswift official goal grid (our FOV gate + soft start, caps 1.5 / 1.5 / 1.0): **h012_x50 170 / 180 goals** vs B-Human 165; the champion h022 141.
Near grid (single kick from standstill, stick-foot fixture): B-Human 215 / 216 on direction vs ours 119–176.
Our v2 (camera noise): every recent checkpoint beats B-Human on accuracy, falls and time to kick; B-Human is better with a perfect ball position on aim (3.7° vs 4.7°+) and long-kick power (5.7 vs ≤ 5.0 m/s).

## 10. What B-Human has that we do not (candidates, cheapest first)

1. **Final-stage tight sigmas** for kick direction (to 0.05 rad²) and launch speed (×0.5). Ours stay at 0.35 rad and a 2 m rest scale. Gene-tunable now (`k.KICK_AIM_SIGMA`, `k.LONG_AIM_SIGMA2`, `k.REST_MISS_SCALE`); one try today (bh_prec2, aimlong) was mixed, so staging matters (anneal, don't jump).
2. **Energy costs** (power, torque tiredness) and a **stronger action-rate penalty** (−1 vs our −0.15): smoother, quieter and cooler motors. `w.joint_power` exists; tiredness needs real torque limits in the model.
3. **Hard torque clip** at B-Human's values instead of a soft penalty: the real 291 knee hit −74 Nm in a fall.
4. **Ground randomisation**: friction down to 0.3, restitution and compliance, rougher terrain (7.5 cm). Relevant to the real slip-and-fall on 291.
5. **Wider mass and CoM randomisation** (±20 % / ±10 cm): matches the real knee-load difference.
6. **Kick-moment robustness**: freeze the ball input after the kick; incoming and moving balls. Without a velocity input the moving ball is limited (v51).
7. **Symmetry loss** in PPO (we augment; they also penalise asymmetric outputs).
8. **Kick-pose and sole-yaw shaping** (side-foot target), if the free style choice keeps missing the side-foot kick.
9. Not adoptable under the 83-input rule: ball velocity input, gait clock and frequency action, continuous range input.

And what we have that they do not: one end-to-end policy (search, approach and
kick), a camera and memory model, actuation latency, ball size and mass
randomisation, AMP style, landing-quality terms, and a benchmark-gated
evolution loop.

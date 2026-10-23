---
name: k1-dribble-speed
description: Dribble task (Mjlab-Velocity-Dribble-Amp-DA-Muon-Booster-K1) speed ceiling ~0.8 m/s in v12/v13; v14 speed-scaled envelope launched 2026-10-19 toward 1.5 m/s
metadata:
  node_type: memory
  type: project
  originSessionId: 18ee3867-4055-4a59-a7b5-2a798a71780f
  modified: 2026-10-18T22:47:56.409Z
---

User goal (2026-10-19): dribble at ~1.5 m/s in all directions with good ball control. Runs live in runswift_mjlab/logs/rsl_rl/k1_dribble_amp (v6–v13 were made outside Claude, likely in Cursor; there are no notes on them).

Eval tool: scripts/tools/dribble_eval.py CKPT (deterministic, max speed caps, fixed commanded speed, fwd/side/back bins, post-touch windows only) → logs/dribble_eval/*.jsonl. Training-curve success is not comparable because it mixes the speed curriculum.

v13/8350 baseline: success 0.86 / 0.56 / 0.21 / 0.05 / 0.005 at 0.5 / 0.8 / 1.0 / 1.2 / 1.5 m/s. At a 1.5 command the ball moves at only ~0.77 m/s, in every direction. Ball distance ~0.4 m, falls 1–3%. v13 is better than v12 at every speed. The curriculum was stuck at speed_hi 1.3.

Diagnosis: the gait short-steps (4 Hz × 0.17 m). The reward pins the ball close (velocity gate flat to 0.6 m, proximity 0.28 m, a tap reward on every stride). The AMP style term is not the brake (~2% of reward). The walk prior can reach 2+ m/s.

v14 (logs/.../2026-10-19_09-47-19_gvhmr75_fast_v14, resumed from v13/8350): above 0.6 m/s the gate widens to 1.1 m and proximity to 0.6 m at 1.5; alternate_leg_dribble fades out over 0.7–1.1 m/s; curriculum runs 1.3 → 1.7. Success criterion unchanged. Evals at 8850/9350/9850 → logs/dribble_eval/v14.jsonl. Next lever if it is still capped: AMP mix weights (GVHMR clips average 0.4–0.5 m/s, 75% of the weight).

Related: [[selfplay-run-authority]], [[kill-pattern-self-match]].

**v14 result:** success at 0.8–1.0 m/s rose 10 points, but the top ball speed stayed ~0.75 m/s. v14 degraded after about iteration 11000: model_11900 scores 0.75/0.18 at 0.5/1.0 m/s with odometry and 0.62/0.14 without. Best checkpoint without odometry: model_10900 (0.77/0.27). Always eval before choosing a warm start.

**Speed diagnosis** (per-term reward vs robot speed at a 1.5 m/s command, scratchpad speed_terms.py): task reward flattens above ~0.9 m/s robot speed. fov_recheck (weight 3, ball fresh within 0.5 m) falls 3.8 → 3.2 with speed, and landing/slip/action-rate penalties grow. The robot spends 41% of the time below 0.4 m/s because random 360° commands every 4 s keep it repositioning. The AMP style score does not fall with speed. Multi-critic advantages are normalised per group and mixed 0.2 style / 0.8 task, so style gets 20% of the gradient (not 2%).

**v15** (2026-10-19 12:37, logs/.../2026-10-19_12-37-34_gvhmr75_fastdrive_imu_v15, resumed from v14/10900). User asked for it plus memory_odometry=False (IMU-only ball memory, now the dribble cfg default). Changes:
- fov_recheck near distance 0.5 → 0.9 m at fast commands;
- new fast_dribble_drive (weight 6): min(ball, robot) speed along the command / s;
- fast commands (≥ 0.9 m/s) get 6–8 s windows, turn at most ±60° after the first touch, and window success pays in proportion to window length.

The eval keeps 4 s windows in any direction; dribble_eval `--odom cfg|on|off`. Watcher: scripts/tools/dribble_watch.sh → logs/dribble_eval/v15.watch every 300 iterations. Intervene if success at 0.5 drops below ~0.70, falls exceed ~5%, or ball distance exceeds ~0.7 m. The user asked me to monitor and intervene.

**v15 → v15b (2026-10-19 14:09).** v15 evals at 0.5 / 1.0 / 1.2 m/s:
- 11200: 0.80 / 0.41 / 0.13
- 11500: 0.83 / 0.46 / 0.16; ball reached 0.83 m/s at the 1.5 command (first time above ~0.77)
- 12100 (best): 0.79 / 0.52 / 0.26
- 12400: 0.69 / 0.24 / 0.10, confirmed on seed 11

Training curves stayed flat across the drop. Cause: Muon at the adaptive LR (~1e-3, KL 0.014) with action std pinned at the 0.6 cap, so the deterministic policy random-walks between checkpoints.

v15b (logs/.../2026-10-19_14-08-55_gvhmr75_fastdrive_imu_v15b_lr1e-4) resumes v15/12100 with schedule "fixed", DRIBBLE_LR 1e-4 and std cap 0.4 (rl_cfg.py). AmpPPO.update now re-applies the configured LR under a non-adaptive schedule, because a resumed optimizer otherwise keeps its saved LR. Under the fixed schedule Loss/kl_divergence logs 0 (it is not computed). Watcher → logs/dribble_eval/v15b.watch.

**v15b → v15c (2026-10-19 15:02).** v15b evals at 0.5 / 1.0 m/s:
- 12400 (best so far): 0.83 / 0.56; ball 0.86 m/s at the 1.5 command; falls ~1%
- 12700: 0.83 / 0.43
- 13000: 0.82 / 0.38

Every commanded speed got slower after the curriculum reached 1.5 at ~12200 (top_band_prob 0.5 meant half the windows were 1.3–1.5). v15c (logs/.../2026-10-19_15-02-38_gvhmr75_fastdrive_imu_v15c_midmix) resumes v15b/12400 with top_band_prob 0.25, speed_hi start = max = 1.5. Watcher → logs/dribble_eval/v15c.watch. If it still slows, the next suspect is the train/eval mismatch: training fast windows last 6–8 s and turn ±60°, while the eval uses 4 s windows in any direction.

**v15c result:** at 1.0 m/s, 12700 scored 0.41 and 13000 0.43. That is stable but below v15b/12400 (0.56). Ruled out as causes of the post-12400 slide: the train/eval window mismatch (12400 also wins with --train-windows) and deterministic vs stochastic (13000 is slower with --stochastic too). Reward diff from 12400 to 13000: fov_recheck +0.07 and approach_view +0.04, speed terms −0.02 each, total flat. So it trades speed for ball-watching.

**v15d** (2026-10-19 15:47, logs/.../2026-10-19_15-47-33_gvhmr75_fastdrive_imu_v15d_viewfade) resumes v15b/12400 (top_band 0.25 kept). approach_view → dribble_view, and fov_recheck is scaled by 1 − 0.6·fast_frac(s) (FAST_VIEW_FADE). Watcher → logs/dribble_eval/v15d.watch. dribble_eval now also has --stochastic and --train-windows. Best checkpoint to deploy so far: v15b/12400.

**Weight averages** (2026-10-19, logs/rsl_rl/k1_dribble_amp/swa_v15/; results in logs/dribble_eval/swa_v15.jsonl). Success at 0.5 / 0.8 / 1.0 / 1.2 m/s and top ball speed:

| Checkpoint | Seed 7 | Seed 11 |
|---|---|---|
| swaA (v15b 12150–12400) | 0.82/0.76/0.58/0.28, 0.86 m/s | 0.86/0.78/0.61/0.27, 0.92 m/s |
| v15b/12400 | 0.83/0.76/0.56/0.26, 0.86 m/s | 0.86/0.79/0.59/0.25, 0.92 m/s |
| swaB (v15b/c/d 12500–13000) | 0.86/0.73/0.46/0.17 | 0.90/0.75/0.48/0.18 |

The 12400 level is real, not a lucky peak. Every continuation from it declines, whatever the reward change (v15c curriculum, v15d view fade), the same "peak just after a fix, then slide" pattern as self-play. Seed 11 falls are ~0 vs ~1% on seed 7.

Best to deploy: swaA_v15b_12150-12400.pt (no-odom, IMU memory). v15d was stopped at ~13000.

Remaining lever for 1.5 m/s: the AMP reference (75% weight on GVHMR clips at 0.4–0.5 m/s, 20% of the gradient). Asked the user before launching.

**Deploy work (2026-10-19, user: "do 1 and 2").**

Step 1, deploy match (env_cfgs `_dribble_deploy_match`, DRIBBLE_DEPLOY_MATCH True; train and play):
- `_deployment_match` (runner joint clip, motor delay 0–40 ms) plus `_clip_leg_torque`;
- vision: vision_hold_steps (2, 4) (new ApproachYawCommandCfg field, a ~16 Hz frame hold), delay (1, 4), dropout 0.05, noise (0.03, 0.05), ball_origin feet with jitter 0.02;
- the stage-3 ball DR (size, mass, friction, bounce); before this the dribble always used one 0.1 kg ball;
- training only: cmd_drift_prob 0.3, max 0.6 rad/s (new DribbleCommandCfg fields).

swaA on the deploy cfg collapses: 0.5 m/s success 0.84 → 0.19, falls ~6%. With --ideal-vision it scores 0.32, so the actuators/ball side and vision each cost a lot.

v16 = logs/.../2026-10-19_17-44-27_dribble_deploymatch_v16, from swaA. A first attempt without ball DR was aborted (..._ABORTED_no_ball_dr). Watcher → v16.watch.

Step 2, runner:
- k1_policy_runner policy_runner/policy/dribble_policy.py (DribblePolicy, a subclass of KickLoopPolicy) and a dribble_v1 mode in policy_runner_main.py and mujoco_runner_main.py;
- joystick = /cmd_vel (LB + left stick = ball velocity in the enable-heading frame), fixed mode via flags;
- doc: DRIBBLE_POLICY_IO.md; parity tool: dribble_parity_check.py (swaA: exact apart from 0.75% lost-rule samples);
- ONNX in k1_policy_runner/dribble_models/. In the MuJoCo sim2sim test swaA did not fall but ran 0.3–0.4 m/s over command.

**Deploy candidate (2026-10-19 ~20:00):** k1_policy_runner/dribble_models/k1_dribble_deploy_swa_v16_13300-13900.onnx (average of v16 13300–13900; source logs/rsl_rl/k1_dribble_amp/swa_v15/swa_v16_13300-13900.pt).

Deploy-cfg eval, 2 seeds, at 0.3 / 0.5 / 0.8 / 1.0 m/s: 0.52 / 0.61 / 0.26 / 0.10; falls 0.2–0.8%. Top ball speed ~0.55 m/s.

Ablations at 13600:
- with --ideal-vision it is still slow (0.34 m/s at a 0.5 command);
- adding --nominal-ball barely changes it;
- so the joint clip, torque limits or delay make it cautious. It is not hardware: the kick walks ~1 m/s under the same limits.

Parity: actions 3e-6, targets 2e-6. Ball-slot mismatches: (a) episode start, where training gives the spawn ball as fresh memory before the first sighting and the runner reports zeros (= trained unknown start); (b) ~1% from the runner's lost rule firing early (level trunk, fixed ball z).

MuJoCo sim2sim, distance in 20 s:

| Command | Distance | Speed |
|---|---|---|
| Stop | ball stays put | 0 |
| 0.3 m/s | 8.9 m | 0.44 m/s |
| 0.5 m/s | 10.9 m | 0.54 m/s |
| 0.8 m/s | 14.5 m | 0.72 m/s |
| 0.5 m/s at 90° | — | 0.55 m/s |
| 0.5 m/s at 180° | — | 0.42 m/s |

No falls; ~12–16° heading drift at slow speed. v16 was left training.

v16 stopped at ~14500 (plateau: 13900/14200/14500 = 0.59/0.30/0.1x). Deploy candidate unchanged.

**First robot run (K1 #291, swaA ONNX = not deploy-matched).** Recording data/recorded_data/dribble_1019_1634.npz/.json; analysis scripts in scratchpad real/a1.py, a2.py, simstats.py.
- ~4 min, 50 Hz loop (0.8% overruns), camera 14.3 Hz new detections.
- Command: 0.5 m/s toward the start heading, 13% stop.
- 5 real falls in ~155 s upright (~1.9/min). Sim, same model: old cfg 0.13/min, deploy cfg 0.80/min. The 163 s "fall" was a powered-off or handled robot (torques ~1 Nm).
- Falls happened while moving, with the ball 0.4–1.1 m away, after yaw rates of 64–118°/s and knee/ankle tracking errors of 0.4–1.1 rad.
- Upright dribbling stats match the deploy-matched sim: pitch −11/18°, roll −6/8°, gyro p95 99°/s, action change 0.121. Ball median 0.53 m (sim 0.41).
- Right leg is loaded more: knee p99 39 vs 26 Nm, ankle pitch 29 vs 20.
- The runner kept the policy running on the ground after falls (tilt 55–70°, under the 70° cutoff), which is the known fall-latch gap. The "ball lost / no turning" stretches were the robot lying down, not a search failure.

**Gap analysis (robot #291 swaA vs sim, 2026-10-20).**

Leg tracking |q_target − q| p95, robot vs swaA in deploy-cfg sim:

| Joint | Robot | Sim |
|---|---|---|
| Hip pitch | 0.79 (L) / 0.55 (R) | 0.40 |
| Knee | 0.66 / 0.63 | 0.50 |
| Ankle roll | 0.22 / 0.25 | 0.12 |
| Hip yaw | 0.23 / 0.20 | 0.14 |

Ankle pitch and hip roll are similar; medians match. The target→position lag is ~80 ms on the robot vs 60–80 ms in sim.

- Camera: in view, a detection every 41 ms (p90 63); trained hold 40–80 ms.
- Detection jitter: 2 mm (trained noise is larger).
- Falls per upright minute: robot 1.9 (swaA); sim swaA 0.13 old cfg, 0.80 deploy cfg; v16 in deploy sim 0.13 (pitch p5/p95 −6/16, gyro p95 86°/s, ball 0.34 m).
- MuJoCo bridge reports the ball in the tilted trunk frame (training/robot: feet midpoint on the ground). Fix pending.

**v17 flat foot (2026-10-20 10:07)** = logs/.../2026-10-20_10-07-53_dribble_flatfoot_v17, from swa_v16, with foot_flat −30 (settle 0.06 s) added in booster_k1_dribble_env_cfg. A −200 launch that started by mistake was stopped (..._ABORTED_w200).

Baselines (runner sim, 0.5 m/s), see [[gait-penalty-weighting]]:

| Policy | Flat stance | First loaded step, p50 / p90 (× body weight) |
|---|---|---|
| v16 | 76% | 1.89 / 3.02 (hard landings) |
| AMP walk | 73% | 0.77 / 0.91 |

Watcher: scripts/tools/dribble_watch_flat.sh → logs/dribble_eval/v17.watch (deploy eval + ONNX export + tiptoe_sim). Toe-tip ball contact: 88–97% of touches in sim; 85% of close approaches on the robot.

**v17 result (2026-10-20).**

| Policy | Flat stance | Landing force, p50 / p90 (× body weight) |
|---|---|---|
| v16 | 76% | 1.89 / 3.02 |
| v17 checkpoints 14200–15400 | 81–85% | 1.6–2.4 / 2.2–3.3 (noisy) |
| swa_v17 | 84% | 1.94 / 2.69 |

- Averaged candidate: k1_policy_runner/dribble_models/k1_dribble_flat_swa_v17_14200-15400.onnx (logs/rsl_rl/k1_dribble_amp/swa_v15/swa_v17_14200-15400.pt).
- Deploy eval at 0.3 / 0.5 / 0.8 / 1.0 m/s, 2 seeds: 0.48 / 0.61 / 0.32 / 0.12; falls 0.2–0.7%. Equal or better than swa_v16 (0.52 / 0.61 / 0.26 / 0.10).
- swa_v17 over 180 s: flat stance 84%, landing 1.94 / 2.69.
- foot_flat −30 fixes the flatness but not landing force. A soft-landing term was proposed; waiting for the user's OK.
v17 stopped at ~15700 (plateau; flat stance drifting above target 87%, landings 2.25/3.10). Candidate = swa_v17_14200-15400.

**Ceiling check (2026-10-20, user asked "1.5–2 m/s or hit the ceiling?").** In every eval bin ball speed = robot speed, so the limit is how fast the robot moves while dribbling, not ball control. The AMP walk in the runner sim (runner torque limits, tighter than training's: ankle pitch 24, hip roll 25 Nm) reaches 0.91/1.42/1.67 m/s (model_9950) and 1.06/1.42/1.72 (model_29999) at 1.0/1.5/2.0 commands, no falls. So ~1.4–1.5 is physically there in sim; 2.0 exceeds anything our K1 policies have done even without a ball. Deploy cfg costs speed: swa_v17 robot 0.62 at a 1.0 command (swaA, old cfg: 0.83). Reward finding: ball_vel_cmd_tracking (w8, σ 0.25) gives ~0 gradient once actual speed is >0.5 m/s under the command; only ball_progress + fast_dribble_drive pull toward speed. Script: scratchpad walkspeed (runner sim + root_pos).

**v18 + v19 (launched 2026-10-20 14:42, parallel, both resume swa_v17_14200-15400.pt, user: "do v18 and 19, use v17 as bench for no-regression gate and sim2real").** Per-run switches via env var DRIBBLE_GENES (JSON, read in dribble_rewards.py and rl_cfg.py; empty = v17 recipe; genes.json saved in each run dir).
- v18 = logs/.../2026-10-20_14-41-48_dribble_sigma_v18, DRIBBLE_GENES {"track_sigma_fast": 0.6}: ball_vel_cmd_tracking σ 0.25 → 0.6 across FAST_SPEED_RANGE.
- v19 = logs/.../2026-10-20_14-42-08_dribble_fastmix_v19, {"amp_mix": "fast"}: data/amp_mix_dribble_stage2/dataset_weights_fast.json (40% GVHMR, 36% runs, 8% walk3_04, 6% CMU sprints, 10% walks; mean clip speed 0.56 → 0.78 m/s).
- ~4.3 s/iteration each while sharing the GPU.

Bench = swa_v17. Tools:
- runswift_mjlab/scripts/tools/dribble_watch_bench.sh: every 300 iterations, deploy-cfg eval (2 seeds, 0.3–1.5) → logs/dribble_eval/bench/NAME_IT.jsonl; ONNX → bench/onnx; parity → bench/NAME_IT.parity; runner bench; gate → logs/dribble_eval/v18.watch, v19.watch.
- runswift_mjlab/scripts/tools/dribble_gate.py: gates vs v17. Deploy success at 0.3/0.5/0.8 ≥ v17 − 0.03; falls; ball distance; runner falls 0; flat stance 70–87%; landing p50/p90 ≤ v17 + 0.15/0.2; torque saturation; per-leg torque, Δq, jitter and angular rate ≤ ×1.15; tilt; stop; 0.5 tracking; parity ≤ 1e-4.
- k1_policy_runner/python-implementation/dribble_bench.py: runner MuJoCo, 6 fixed commands, JSON → k1_policy_runner/runs/dribble_bench.jsonl.

v17 runner baseline:
- ball speed 0.59 / 0.80 / 0.91 at 0.5 / 1.0 / 1.5 m/s; 0.81 at 1.0 m/s, 90°;
- flat stance 84%, landing 2.11 / 2.93, torque saturation 0.3%, tilt p90 9.7°, no falls.
v17 parity: actions 3.1e-6.
- v17 deploy-cfg bench at 0.3/0.5/0.8/1.0/1.2/1.5: success 0.49/0.62/0.31/0.11/0.02/0.00; ball speed plateaus at 0.57 m/s at 1.5 (runner sim: 0.91), so the deploy-match conditions are the main cap.
- GPU contention: two parallel benches slowed both trainings from 4.3 to 11.4 s per iteration. After the 15700 gates the watchers hold bench/gpu.lock and run every 600 iterations. At 15700 both runs ≈ v17.

**v18/v19 verdicts (2026-10-20).**

v19 (fast AMP mix) stopped at 17:11 (last checkpoint 16600).
- Trunk tilt p90 rose 9.7 (v17) → 12.5 → 16.3 → 17.3°; landing p50 2.48. The unconditioned style copies the human run clips' forward lean.
- Speed gain small: deploy ball speed +0.03 at 1.5, 0 at 1.0.
- Lesson: don't speed up the AMP mix unconditionally. If style is revisited, condition it on the command (per-frame commands derived from clip root motion; derivation works with xyzw quaternions).

v18 (σ 0.6) at 16300 PASSES every gate:
- landing 2.11 / 2.72, tilt 8.4°, turn rate −22%, success at 0.3 m/s 0.54;
- no speed gain: deploy 0.51 / 0.57 at 1.0 / 1.5; runner speed swings between checkpoints (16100: 0.87, 16300: 0.78 at 1.0 m/s).
Deploy-cfg ball speed is still stuck at ~0.57; suspects are the deploy-match conditions.

**Where the speed cap is (2026-10-20 18:10, v17, training sim).** dribble_eval now has --no-joint-clip, --no-torque-clip and --no-delay.
- Actuator ablation at 1.5 m/s, all directions: deploy 0.55; any single condition off 0.55–0.60; all three off 0.61.
- Forward bin at 1.5 m/s: deploy 0.70 (both 4 s and --train-windows); everything ideal (vision, ball, actuators) 0.84; runner sim 0.91.
- The 0.57 headline is a mix of directions (back is slow).
- Conclusion: deploy conditions together cost ~0.14 m/s, each a little. The real cap is the policy's learned dribble gait at ~0.85–0.9 m/s even in ideal conditions. Reward σ (v18) didn't unlock it; the fast style mix (v19) added ~0.06–0.08 at the cost of forward lean.
- Next lever (proposed, needs user OK): command-conditioned AMP (fast clips only at fast commands) plus an upright guard.
- v18 stopped 18:35 (last ~17550). Peaked at 16300 (only full PASS; best checkpoint, logs/dribble_eval/bench/onnx/v18_16300.onnx), then slid: 16900 tilt 13.3; 17500 fails 0.8 success, landing 2.54 / 3.30, tilt 12.5. Same peak-then-slide as v15. GPU idle; v20 (conditioned AMP + upright guard) and the v18 SWA candidate await user OK.

**v20 (launched 2026-10-20 20:44; user: "speed too slow, we need 1.5 m/s").** logs/.../2026-10-20_20-44-39_dribble_condamp_v20, warm-started from v18/model_16300 (iterations restart at 0). DRIBBLE_GENES {"track_sigma_fast": 0.6, "amp_cond": true, "tilt_guard": -20}.

Command-conditioned AMP (APEX-style command coupling):
- the env adds an "amp_cond" obs group, mdp.amp_dribble_cond = [s/2, cos, sin of the commanded direction in the yaw frame, 1] once touched and not lost, else zeros;
- MotionLoader labels expert frames with their smoothed (0.5 s) heading-frame travel velocity (COND_* in motion_loader.py), rebalances sampling by speed bin (amp_speed_mass: <.3 0.15 / .7 0.30 / 1.1 0.20 / 1.6 0.20 / + 0.15; >1.1 m/s goes from 7.5 % to 35 %), and gives 25 % of expert samples the zero "free" condition;
- the AMP module appends cond to each history (disc input 300 → 304); amp_ppo._widen_discriminator_state warm-starts the old discriminator with zero weights on the new columns.

tilt_guard = linear hinge on |gravity_xy| beyond sin 10°. Why: the plain fast mix (v19) leaned 16.5° at 0.5 m/s; the soft `upright` kernel still pays 72 % at 15°.

Loading a v20 checkpoint (eval, export, parity) needs the same DRIBBLE_GENES; the watcher is started with them. About 2.1 s per iteration with the GPU to itself.
- v20 stopped 22:36 (last ~1950). Deploy forward ball speed at 1.5: 600 0.73, 1200 0.80 (best), 1800 0.77 vs v17 0.72; success at 0.8/1.0 +0.04. Tilt rose to 12° at 1200, then back to 9.8 at 1800. Landings stayed hard (p90 3.4–3.7) and jitter high.
- Conclusion: conditioned style adds ~+0.05–0.08 m/s; reward/style levers are exhausted near 0.8 m/s.
- Remaining structural lever (proposed, awaiting user): the task definition itself. success_ball_dist 1.0 m, gate/proximity ≤ 1.1/0.6 m and per-stride tap terms force tap-every-stride, which caps speed at cadence × step. Proposal: a push-ahead-and-chase regime at fast commands.

**v21 push-and-chase (launched 2026-10-20 22:41; user: "push the ball 1–2 m ahead, sprint after it, touch it again, and try how fast can we go").** logs/.../2026-10-20_22-41-35_dribble_pushchase_v21, resumes v20/model_1200 (iterations continue from 1200). DRIBBLE_GENES = v20's + "push_chase": true.

Over commanded 0.9 → 1.5 m/s (PUSH_SPEED_RANGE; ≤ 0.8 is unchanged, so the slow gates stay comparable):
- window success distance 1 → 2 m (DribbleCommandCfg.push_dist_extra);
- velocity gate flat distance 1.1 → 2.0 m;
- proximity radius 0.6 → 1.6 m;
- fov freshness near distance 0.9 → 1.5 m;
- lost_ball_dist 3 → 3.5 m.
speed_hi_max 1.5 → 2.0, so the curriculum finds the top speed.

Watcher: SPEEDS adds 1.8 and 2.0; PROBE_SPEEDS 1.5/1.8/2.0 run in the runner sim (dribble_bench --probe-speeds; the probe lifts the runner's MAX_TRAINED_SPEED 1.5 guard in sim only).

Runner probe baselines, ball speed at 1.5 / 1.8 / 2.0 commands:
- v17: 0.91 / 0.97 / 0.90;
- v20_1200: 0.93 / 1.07 / 1.13 (ball 0.6–0.9 m ahead, tilt ~12°).

**v22 skills (launched 2026-10-20 23:08; user, before 7 h of sleep: "approach from up to 8 m, ball can disappear → fast search spin, slot 82 = kick straight at 7 m/s with accuracy (side steps), then stand until the command changes; goal is real deployment; keep monitoring and improving, use resources wisely").**
- Run: logs/.../2026-10-20_23-08-27_dribble_skills_v22, resumes v21/model_1800 (v21 stopped there).
- DRIBBLE_GENES: v21 genes + kick_prob 0.25, vanish_prob 0.1, far_spawn_prob 0.3.

Code:
- DribbleCommandCfg: kick_prob, kick_window_s 6–9, kick_half_angle π/2, respawn_dist 1–8 (new ball after a kick window), vanish_prob / vanish_dist 1.5–5, lost_needs_touch.
- _resample_ball_events, _move_ball, _update_kick (classify_touch, loft_factor from kick_loop).
- Slots: 78–79 kick direction, 80–82 = 0, 0, 1 in kick windows. The style gate is off near the ball before the kick and for 0.6 s after. amp cond is free before the kick, stand after.
- Rewards: kick_power 1500 (speed/7 × aim × loft; aim = mean(exp(−e²/0.5), exp(−e²/0.05)), because the sharp kernel alone paid 0 at the untrained 35°), kick_line_up 4, kick_stand 3, kick_wait_cost −1. approach_progress, ball_proximity and lost_ball_spin are off after the kick; ball_stop_tracking is off in kick windows.

Tools:
- scripts/tools/dribble_skill_eval.py: approach / search / kick tests on the deploy cfg.
- dribble_bench.py --kick-probe: runner kick mode at 0 / ±30°.
- Runner: DribblePolicy command_mode "kick" + set_kick(); CLI --dribble-command kick --dribble-heading-deg H.
- The parity check copies kick_mode.
- Watcher env vars: SPEEDS, PROBE_SPEEDS, SKILL, KICK_PROBE.

Baseline v20_1200 (skill eval):
- approach 4–8 m: 9 % touched within 15 s, 82 % falls (illegal_contact = real falls when sprinting at a far ball);
- search: 11 % found within 12 s;
- kick: 0.06 kicks per window at 1.3 m/s.

**v23 kick teacher (launched 2026-10-21 00:20).** logs/.../2026-10-21_00-19-57_dribble_kickteacher_v23, resumes v22/model_2850 (v22 stopped there; v22's kick stalled: 12 % of kick windows kicked, 1.6 m/s, 50° after ~1000 iterations).
- Genes: v22 + "kick_teacher_coef": 0.5 (decay 5000 updates).
- Teacher: kick-loop h011_c2/model_17750 (long kick 4.4–4.5 m/s), src/mjlab/amp/modules/kick_teacher.py (torch MLP; matches the ONNX to 9e-6).
- Slots 80–82 = (0, 0, 1) is the kick loop's long-kick one-hot, so the teacher kicks long along slots 78–79 on dribble observations.
- amp_support._record_kick_teacher masks kick windows within 1.5 m before the kick and 0.4 s after, legs only.
- Runner cfg kick_teacher_checkpoint.
- Watcher every 750 iterations.

**v23 → v24 (2026-10-21 01:30).**

v23 stopped at ~3650. Its 3600 bench was worse than v22:
- dribble success 0.39 / 0.57 / 0.25 at 0.3 / 0.5 / 0.8;
- jitter 0.102;
- kick unchanged (1.65 m/s, 43°).

Diagnostic: the teacher alone (h011; student head) in dribble kick windows made 1146 kicks vs the student's 139, at 3.08 m/s (p90 5.16), 14.5° (71 % within 15°). So the teacher is good and v23's leg-only imitation within 1.5 m was too narrow.

Obs ambiguity found and fixed: after a kick the ball is far and the obs was identical to "far ball, go kick". Kick windows now set slot 80 = kick_done: (0, 0, 1) = kick, (1, 0, 1) = kicked, stand.
- Runner: DribblePolicy sets _kicked once a ball seen within KICK_NEAR_M 0.6 is seen beyond KICK_GONE_M 1.5.
- The parity check copies kick_done.
- Teacher imitation stops at the kick (the teacher reads slot 80 as short range).

v24 = logs/.../2026-10-21_01-29-44_dribble_kickteacher2_v24, from v22/2850. Genes: v22 + kick_teacher_coef 1.0, decay 8000, kick_teacher_dist 100 (the whole window before the kick, approach included), kick_teacher_arms true. A first attempt without the kicked flag was renamed _ABORTED_no_kicked_flag. Watcher every 600 iterations.

**v24 results; v25 (2026-10-21 03:20).**

v24 kick (skill eval):
| | 3450 | 4050 |
|---|---|---|
| Kicks per window | 0.33 | 0.32 |
| Speed mean / p90 (m/s) | 2.7 / 4.4 | 2.76 / 4.56 |
| Mean error | 19° | 17° |
| Within 15° | 60 % | 67 % |
| ≥ 5 m/s | — | 6.8 % |

Runner probe: kicks at 0 / ±30° at 1.1–2.9 m/s, then stands.

Costs at 4050:
- dribble success 0.37 / 0.55 / 0.28 vs v17 0.49 / 0.62 / 0.31;
- jitter 0.106;
- approach 40 % touched / 9 % falls (v22: 44 % / 21 %).

Blends of v22_2850 with v24_4050 (0.5/0.5 and 0.3/0.7, logs/rsl_rl/k1_dribble_amp/blend_v22v24): the kick is lost (1.7 m/s, 41°) and dribbling is not recovered. Lesson: the kick and dribble skills interfere in the weights; blending gives the worst of both.

Cause of the dribble regression: the imitation loss itself. v22 had the same kick windows at 0.46; v23 at coef 0.5 and v24 at ~0.9 both regressed.

v25 = logs/.../2026-10-21_03-20-16_dribble_lightteacher_v25, from v24/4050: teacher coef 0.3, kick_teacher_dist 2.0 (the approach is the dribble's own), decay 8000. Watcher every 500 iterations. v24/4050 is the kick-best fallback.
- v25_4550 (best all-round skill model so far):
  - approach 54 % touched / 6 % falls; search 31 % found;
  - kick 2.78 m/s (p90 4.58), 15.7°, 68 % within 15°; stands 76 %;
  - landings pass again (2.21 / 2.88);
  - still fails slow-dribble success (0.39 / 0.55 / 0.26) and jitter 0.106.
- Runner-sim leg jitter lineage: v17/v18 0.066–0.070 → v20 (amp_cond) ~0.080 → v22 (sprint / vanish / kick scenarios) 0.095 → v23–v25 0.10–0.106. The scenarios, not the teacher, added most of it.
- Added CAPS genes (caps_temporal_coef, caps_spatial_coef, caps_near_ball_scale) to the dribble runner for a v26 smoothness run.

**v25 5050 / 5550 and v26 (2026-10-21 ~05:30).**

v25 by checkpoint:
| | 5050 | 5550 |
|---|---|---|
| Approach (touched / falls) | 65 % / 6 % | 62 % / 5 % |
| Search found | 42 % | 41 % |
| Kick mean error / within 15° | 14.6° / 72 % | 14.3° / 69 % |
| Kick speed mean / p90 (m/s) | — | 2.84 / 4.77 |

v25_5550 passes all dribble gates (0.46 / 0.62 / 0.30) and parity 3.9e-6. It fails only landing p50 2.30 and jitter 0.088.
- Deploy candidate copied to k1_policy_runner/dribble_models/k1_dribble_skills_v25_5550.onnx.
- Runner kick: 0° → 3.81 m/s, 5°, stands at 0.03 m/s; 60° → 3.07 m/s, 1.6°. ±30° never kicks: it parks 0.47 m from the ball for the whole window.
- Cause: the dense kick_line_up reward pays loitering near the spot.

v26 = logs/.../2026-10-21_05-24-53_dribble_kickfix_v26, from v25/5850. kick_line_up × exp(−kick_wait / 1.5 s) (gene kick_line_up_tau); kick_wait_cost −3 (gene kick_wait_w). Watcher every 400 iterations.
- v26 loitering fix works. v26 6400 runner kicks: 0° 2.6 m/s, 18°; +30° 3.3 m/s, 11°; −30° 3.1 m/s, 12°; 60° 3.7 m/s, 10°; all within 0.8–1.6 s, then stands at ≤ 0.03 m/s.
- v26_6250 bench: approach 66 % / 8 % falls; search 48 %; kick 2.86 m/s, 15.8°, 68 % within 15°; parity 6.1e-6. Fails dribble 0.3 / 0.8 (0.42 / 0.26), landing 2.46 / 3.25, jitter 0.094.
- Both candidates are in k1_policy_runner/dribble_models: k1_dribble_skills_v25_5550.onnx (passes dribble gates, straight kicks only) and k1_dribble_skills_v26_6250.onnx (angled kicks work, slow dribble slightly below gate).
- Open: speed ceiling (~0.6 deploy / ~0.9–1.0 runner), 7 m/s kick (now ~2.9 mean, p90 4.7), jitter 0.09 vs 0.066.
- v26 stopped 07:2x at ~7100: 7050 slid (dribble 0.45/0.58/0.21, tilt 13.4, landings 2.53/3.18); skills plateau (approach 78%, search 51%, kick 2.81 m/s 15.6 deg). GPU idle; candidates unchanged (v25_5550 safe, v26_6250 angled kicks).

**v27 push + side kick + kick critic (launched 2026-10-21 09:09).** User: "push the ball 1–2 m ahead (allowed last night but not done), increase speed, reduce style, kick critic, B-Human-style side kick".

I admitted that v21–v26 only *allowed* the push (widened gates). Nothing paid for it, and the ball lead at fast commands stayed ~0.4 m (v26 probe p50 0.38, p90 0.78).

B-Human side kick (MachineLearning/IsaacGymRL/envs/readme.md; port bhuman_kick/stages.py, mdp.ball_sole_yaw):
- inside-of-foot pose: kicking-foot yaw − kick direction = +90° (left) / −90° (right), exp(−diff² / σ);
- multiplied by the kick-pose counter and gated on a correct kick direction;
- stage 2 σ 1.0, weight 25 → stage 3 σ 0.1, weight 15 → 5 → stage 5 weight 0, so the outcome holds the habit.
- Our kick-loop history: the rising target-angle curriculum taught the inside foot (88 % of short kicks) but cut long power 6.99 → 4.70, and free style choice collapsed onto the most rewarded style.

v27 = logs/.../2026-10-21_09-09-02_dribble_pushside_v27, from v26/6250. Iterations restart at 0 (critic grown; optimizer fresh).

Genes: v26 + teacher 0.15 + push_w 300, ahead_w 4, side_w 300, sole_yaw_sigma 1.0, speed_gate_frac 0.75, top_band_prob 0.4, fast_turn_deg 30, style_w 0.15, critic_alphas [0.1, 0.65, 0.25].

New code:
- dribble rewards push_ahead (per launch, ball speed along the command / 1.3 s), ball_ahead (ramp to 1.5 m lead, flat to 2, down by 3, × the robot chasing at the commanded speed), kick_side (sole-yaw ratio × aim, on the kick).
- KICK_GROUP_TERMS = the kick critic's group (runner cfg extra_reward_group; amp_support._reward_terms_sum).
- amp_ppo._add_critic_heads grows the critic from 2 to 3 heads; the new head copies the task head.
- DribbleCommandCfg: speed_gate_achieved_frac, sole_yaw_sigma, kick_min_angle (viewer only).
- Bug found: the dribble runner hard-set alphas (0.2, 0.8) after the gene code; now skipped when the gene is set.

Watcher every 500 from 0. The v26 viser viewer was left running, slowing training to 5.4 s/it.
Next stage when the side kick appears: sole_yaw_sigma 0.1, side_w down (B-Human stage 3).
- v27 first launch (09:09) trained from RANDOM weights: _add_critic_heads replaced load_cfg None with {"optimizer": False}, and rsl_rl treats a missing key as "don't load" (no actor). Symptom: episode length ~48 flat, illegal_contact huge. Renamed _ABORTED_actor_not_loaded. Fixed: start from the full default dict.
- Lesson: after any loader change, check the first iterations' episode length against the parent run.
- v27 relaunched 09:43 = logs/.../2026-10-21_09-43-51_dribble_pushside_v27 (iterations continue at 6250; episode length 864 at 6312, healthy; 2.4 s/it). Watcher from 6250, step 500. The viser viewer was killed per user request.

**v27 results (stopped 2026-10-21 ~12:00 at ~7900; plateau).** Speed curriculum unstuck: ball_speed_hi 1.5 → 1.9.

Forward ball speed (deploy cfg) at 1.5 / 1.8 / 2.0 m/s, lead in brackets:
- v17: 0.72 at 1.5;
- 6750: 0.80 / 0.86 / 0.83 (0.75–0.88 m);
- 7250: 0.85 / 0.90 / 0.90 (1.0 m);
- 7750: 0.85 / 0.91 / 0.87.
Runner sim: 1.07–1.18 m/s (best ever).

Costs:
- 6750 passes the slow gates (0.49 / 0.61 / 0.35); falls 1.06 %;
- 7250 / 7750: slow dribble 0.42–0.43 / 0.55, falls 1.06–1.42 %;
- approach 53 % → 37 %, search 28 % → 22 %;
- jitter 0.09–0.10; landings 2.4 / 3.4.

Kick held (2.8–3.0 m/s, 15–16°, ~65–70 % within 15°; angled kicks OK). The side-kick reward stayed small (kick_side ~0.04).

Copied to k1_policy_runner/dribble_models: k1_dribble_push_v27_6750.onnx (balanced) and k1_dribble_push_v27_7250.onnx (fastest, 1 m lead, more falls).

**v28 safe-fast (launched 2026-10-21 ~12:20; user: "run v28").** logs/rsl_rl/k1_dribble_amp/2026-10-21_13-14-20_dribble_safefast_v28, resumes v27/6750 (3-head critic loads directly; iterations continue at 6750; episode length 759 at 6808, healthy).
- Genes: v27 + top_band_prob 0.3, sole_yaw_sigma 0.3, caps_temporal_coef 2.0, fast_fall_w −150.
- New term fast_fall: on a fall (illegal_contact | fell_over), the robot's planar speed.
- Side-kick measurement before launch (v27_6750, kick windows): foot yaw vs kick direction p10 15 / p50 51 / p90 73°; 32 % in the inside band (60–120°), 13 % front (< 30°). So σ goes 1.0 → 0.3, not straight to B-Human's 0.1 (which would pay ~0.01 at the current median).
- dribble_skill_eval kick test now reports foot_yaw_p50 and inside_foot_share. Watcher every 500 from 6750.
- v28 stopped at ~7300. Its 7250 bench was worse than parent v27_6750:
  - falls 1.75 % (vs 1.06); approach 14 % touched / 14 % falls (vs 53 %); search 8 % (vs 28 %);
  - slow dribble 0.39 / 0.54; speed 0.76–0.80;
  - landings pass (2.26 / 3.13), jitter 0.086; inside-foot share 35 %, foot yaw p50 53°.
  - Suspect: caps_temporal_coef 2.0 (sluggish recoveries). v28 bundled 4 changes, so not certain.
- v28b = logs/.../2026-10-21_14-09-21_dribble_safefast_v28b, same as v28 minus the CAPS change (top_band 0.3, sole σ 0.3, fast_fall −150), from v27/6750. Episode length 818 at 6806, healthy. Watcher every 500 from 6750.
- v28b 7250 bench: approach 53 % / 8 % falls, search 29 %, kick 3.0 m/s (p90 4.97; 9.5 % ≥ 5 m/s), 16°; inside-foot 24 % (σ 0.3 lost ground vs 32 %).
  - Slow dribble 0.34 / 0.54 (fails); falls 1.04 % (the fast_fall penalty did not lower falls vs v27's 1.06).
  - Left-leg torque p99 25 Nm (at the runner limit); landings 2.48 / 3.63; jitter 0.107. Parity 5.5e-6.
  - Runner: 0.62 / 0.88 / 1.10 / 1.16 m/s at 0.5 / 1.0 / 1.5 / 1.8 commands; kicks 3.5–3.6 m/s, 13–15° at 0 / ±30°; no falls.
- Exported k1_policy_runner/dribble_models/k1_dribble_safefast_v28b_7250.onnx (user wanted to robot-test v28b).
- v28b 7750 plateaued (slow 0.40 / 0.54, speed 0.83–0.89, falls 0.96 %). Stopped ~15:45; GPU idle.
- Also fixed fast_fall for play configs (no illegal_contact termination) via termination_manager.active_terms.
- Robot speed advice given: --dribble-max-speed ≤ 1.5 (runner guard); ladder 0.5 → 0.8 → 1.0 → 1.2 → 1.5; keep --dribble-speed-limits 1.2,1.0,1.25. start_dribble.sh still points at swaA_v15b.
- Runner fall latch (2026-10-21, item 1 of the user's one-at-a-time plan): policy_runner.types.FallLatch with FALL_TILT_DEG 50; policy_runner_main uses it plus --fall-tilt-deg. It stays in damping with no commands until re-enabled (enable off → on) while upright. Replaced is_fallen at 70° every step, which resumed on the ground.
  - Regression checks: test_fall_latch.py passes 4/4; max runner-sim tilt for v28b_7250 / v27_6750 is 20.8° worst (kicks), dribble 10–15°, sprints ≤ 18°, so no false trips. Training ends episodes at 63° tilt or on ground contact.
- dribble_gate.py SLOW_TOL 0.08 for 0.3 / 0.5 m/s (user preference); 0.8 stays −0.03. Re-gated: v27_6750 passes all slow gates; v28b_7250 fails 0.3 (0.34) and 0.5.
- Item 2 (smoothness), one change: v29 = logs/.../2026-10-21_16-26-43_dribble_caps13_v29 = v27_6750 genes + caps_temporal_coef 1.3 only (v28's 2.0 broke recovery). Episode length 864 at 6816, healthy. Watcher every 500 from 6750. Judge vs parent v27_6750: jitter 0.092, landing 2.37 / 3.49, falls 1.06 %, approach 53 %, search 28 %, speed 0.80–0.86 fwd.
- Regression-check method: compare a single-change continuation with the same-length no-change control (v27's own checkpoints from 6750), not only the parent. Continuations drift: approach/search fall at every step (v26_6250 66 / 48 % → v27_6750 53 / 28 → v27_7250 37 / 23).
- v29 (CAPS 1.3) at 7250 vs control v27_7250:
  - smoother (jitter 0.100 → 0.089, landing p90 3.42 → 3.25), falls 1.42 → 1.28 %;
  - but slower (0.85–0.90 → 0.78–0.81), approach 37 → 30 %, search 23 → 16 %; inside-foot 17 %.
  - Not adopted; stopped 17:2x.
- Item next: v30 = logs/.../2026-10-21_17-17-41_dribble_findball_v30 = v27_6750 genes + far_spawn_prob 0.4, vanish_prob 0.2 (more approach / search practice), single change. Healthy start (episode length 826). Judge vs control v27_7250.
- v30 (far 0.4, vanish 0.2) at 7250 vs control v27_7250: ADOPTED.
  - search 23 → 44 %, approach 37 → 46 %, falls 1.42 → 0.94 %;
  - slow 0.42 / 0.60 / 0.34, passes all dribble gates (relaxed);
  - kick 2.81 m/s, 14.7°, 71 % within 15°;
  - speed 0.85–0.90 → 0.82 (small loss); landing 2.54 / 3.62, jitter 0.095.
  - Exported k1_policy_runner/dribble_models/k1_dribble_findball_v30_7250.onnx.
  - v30 continues; next single change after its next bench: speed (item 4).
- v30 7750 slid (search 22 %, falls 1.31 %, 0.8 success 0.28; speed 0.82–0.87). Stopped; v30_7250 is the candidate.
- Speed-cap hypothesis rejected (dribble_eval --cap-vx, v30_7250 forward): cap 1.2 / 1.6 / 2.0 gives the same speed (0.79 / 0.78 / 0.76 at 1.5; 0.81–0.82 at 2.0). Robot speed ≈ ball speed ≈ 0.8 in the deploy cfg; falls at fast commands 1.6–3.6 %.
- v31 = logs/.../2026-10-21_18-57-11_dribble_drive12_v31 = v30_7250 + drive_w 12 (fast_dribble_drive 6 → 12; new gene), single change. Control = v30_7750 (fwd speed 0.82–0.87, falls 1.31 %, search 22 %, approach 47 %). Healthy start (episode length 825).
- v31 (drive_w 12) at 7750 vs control v30_7750:
  - forward speed +0.02–0.05 (0.72 / 0.84 / 0.89 at 1.0 / 1.5 / 2.0);
  - tilt 10.2 → 12.4°, jitter 0.08 → 0.10, landing p90 3.13 → 3.39, falls 1.31 → 1.41 %.
  - Not adopted; stopped ~19:55.
- Speed conclusion: reward levers (σ, style mix, conditioned style, push / ahead, curriculum, drive weight, cap obs) are exhausted near ~0.85–0.9 m/s forward in the deploy cfg (1.1–1.2 runner). Falls rise at fast commands. Bigger levers remain: kick-and-chase with the kick skill, a faster locomotion base, or accept the plateau.

**Night 2 plan (2026-10-21 ~22:20; user: "kill uv play, monitor, debug and improve today's objectives, I go to sleep, be wise with resources").** One change per run, each from the latest adopted checkpoint, judged on kick metrics + dribble gates vs the parent and its same-length control.
1. v32 re-kick (kick_leave_dist 0.5), running = logs/.../2026-10-21_22-04-17_dribble_rekick_v32 from v30_7250. Control: v30_7750 re-evaluated with kick_leave_dist 0.5 → bench/v30_7750_rekick.skill.jsonl.
2. v33 power: kick_air_ok true, kick_cap 2.0, kick_power_w 3000.
3. v34 teacher off: kick_teacher_coef 0.
4. v35 side kick by geometry: side_gate_deg 30.
5. v36 quick kick: kick_wait_free_s 1.0.
Then: outcome-based style; dribble→kick transitions (user's later goal).

New code (all off by default):
- DribbleCommandCfg kick_leave_dist, kick_air_ok; command _kicked_once, prev_window_kick_done, kick_offset;
- dribble_rewards KICK_POWER_CAP (kick_cap), kick_power_w, SIDE_GATE (side_gate_deg), KICK_WAIT_FREE_S (kick_wait_free_s);
- runner KICK_NEAR_M 0.5 / KICK_GONE_M 0.7;
- skill eval reports kick_ground_speed, kick_3d_speed, kick_3d_p90, ball_left_share.
- Bug fixed: the skill-eval list named `left` collided with a local in the step fn (the first control eval crashed silently).
- Control v30_7750 (re-kick eval): kick 2.85 ground / 2.90 3D (p90 4.79), ≥ 5 m/s 8 %, 17.6°, within 15° 64 %, time to kick 2.49 s, ball_left 65 %, inside 14 %; approach 46 %, search 22 %.
- v32_7750 (re-kick) vs that: neutral. Ball_left 65.3 % = control; kick 2.92 / p90 4.85, 16.0°, 69 %; time to kick 2.68 s; slow dribble 0.39 / 0.52 / 0.27 (−0.06); falls 1.54 %. Stopped. Re-kick kept as the user's spec in all later runs; v32_7750 = control.
- v33 power = logs/.../2026-10-21_23-01-21_dribble_power_v33, from v30_7250 + kick_leave_dist 0.5 + kick_air_ok, kick_cap 2.0, kick_power_w 3000. Healthy ramp (880 by +60). Watcher from 7250, step 500.
- v33_7750 vs control v32_7750:
  - kick 3D 3.08 vs 2.97, p90 5.30 vs 4.85, ≥ 5 m/s 12.3 vs 8.1 %, ≥ 7 m/s 2.0 vs 0.7 %; error 15.4°, within 15° 69 %;
  - runner ±30° kicks 2.4 m/s / 8° (vs 1.7 / 15°);
  - search 41 vs 25 %, falls 1.29 vs 1.54 %;
  - slow 0.31 / 0.52 / 0.31 (0.3 worse); leg torque p99 25 Nm (at the runner limit).
  - Promising; continue to 8250.
- v33 8250 plateau / slide: kick 3.10 / p90 5.18, error 17.5°, approach 33 %, search 25 %, tilt fail. Stopped at ~8450.
  - v33_7750 adopted as base; ONNX copied to k1_policy_runner/dribble_models/k1_dribble_power_v33_7750.onnx.
- v34 = logs/.../2026-10-22_00-29-28_dribble_noteacher_v34 = v33_7750 genes with kick_teacher_coef 0 (teacher off; no imitation loss in the log). Healthy ramp. Control = v33_8250.
- v34 (teacher off) at 8250 vs control v33_8250:
  - kick 2.63 vs 3.10, p90 4.20 vs 5.18, ≥ 5 m/s 3.5 vs 11 %, so the teacher anchors power;
  - dribble better (0.43 / 0.54 vs 0.34 / 0.52), approach 53 vs 33 %, search 36 vs 25 %, falls 1.10 %, tilt passes;
  - inside-foot 22 vs 10 %, so the h011 front-foot teacher suppresses the side kick.
  - Not adopted; stopped.
- v35 = logs/.../2026-10-22_01-19-57_dribble_sidegate_v35 = v33_7750 + side_gate_deg 30. Control v33_8250.
- Next prepared: v36 kick_teacher_max_offset_deg 30 (teacher only on straight kicks; runner cfg field + amp_support mask using cmd.kick_offset).
- v35 (side_gate 30) at 8250 vs control v33_8250: ADOPTED.
  - power same (3.04 / p90 5.16); error 17.5 → 14.8°, within 15° 65 → 71 %;
  - search 25 → 35 %, approach 33 → 39 %, falls 1.29 → 1.13 %; slow dribble same;
  - inside-foot only 9.7 → 11.2 %. Exported k1_dribble_sidegate_v35_8250.onnx.
- v36 = logs/.../2026-10-22_02-10-44_dribble_teachstraight_v36 = v33_7750 + side_gate 30 + kick_teacher_max_offset_deg 30 (teacher only on straight kicks). Control v35_8250. Healthy (episode length 863); imitation still active (0.055).
- Queue after v36: kick_wait_free_s 1.0 (quick kick), then outcome-based style, then dribble→kick transitions.
- v36_8250 vs v35_8250: ADOPTED as the kick base.
  - Gains: inside-foot 11.2 → 23.7 %; foot yaw p50 44 → 50°; approach 39 → 45 %.
  - Held: kick power 3.02 vs 3.04 (p90 4.94 vs 5.16); error 15.5 vs 14.8°; slow dribble the same.
  - Losses: search 35 → 31 %; deploy falls 1.13 → 1.27 %; runner landing p50 2.23 → 2.37, dq_target p99 0.196 → 0.218, tau left 24.3 → 24.7 (watch smoothness).
  - Exported k1_dribble_sideteach_v36_8250.onnx; v36 stopped at 8380.
- v37 = 2026-10-22_03-01-37_dribble_quickkick_v37: v36 genes + kick_wait_free_s 1.0, from v36/model_8250. Control v36_8250. Watcher from 8250.
- Watcher launch pitfall (v37, 2026-10-22): dribble_watch_bench.sh must get the run's genes in its env, or the eval/export crash on the AMP discriminator size (300 vs 304 with amp_cond) and the watch shows only "no runner bench row".
  - Required env: DRIBBLE_GENES=<genes without from/resume/change/control> SPEEDS=0.3,0.5,0.8,1.0,1.2,1.5,1.8,2.0 PROBE_SPEEDS=1.5,1.8,2.0 SKILL=1 KICK_PROBE=1.
  - After launch, confirm the first dribble_eval runs longer than a minute.
- v37 (kick_wait_free_s 1.0) REJECTED: at 8750/9250 vs v36_8250, slower and worse kicks.
  - Time to kick 2.83/2.82 vs 2.59 s; inside-foot 18/14 vs 24 %; error 17.3/17.6 vs 15.5°; falls 1.15/1.66 %.
  - But approach rose to 47/56 % (v36 45) and search to 37/47 % (v36 31): a lead worth a retest; it may be drift.
  - A tighter wait cost doesn't shorten time to kick (measured over kicked windows); the bottleneck is line-up/approach, not hesitation.
- v38 = 2026-10-22_04-43-23_dribble_sideoutcome_v38: v36 genes + side_outcome (new gene: kick_side × min(kick_speed/7, 1)), from v36/model_8250. Control v37_8750/9250 (same parent, same length).
- v38 (side_outcome) REJECTED at 8750 vs v37_8750: side kicks collapsed (inside-foot 6.7 vs 18.2 %; v36 23.7 %); power only 3.07 vs 2.92. Side kicks are slow, so scaling their bonus by speed removed it. Keep the geometry gate alone.
- v39 = 2026-10-22_05-34-23_dribble_v36cont_v39: plain v36 continuation from 8250, the drift control for v37/v38 (both had search/approach up and side kick down).
- New test: dribble_skill_eval.py --tests transition. It dribbles at 0.5 / 1.0 / 1.5 m/s and, after 4 s with the ball within 1 m, switches to a kick window (0–90° off the robot-to-ball line). Reports kicked within 4 s (straight and angled), time to kick mean/p90, power, error, falls.
- Transition baseline (dribble then kick mid-dribble; kicked within 4 s / time-to-kick mean / p90 / error / falls):
  - v36_8250: 0.5 m/s 86 % / 1.42 / 2.6 s / 16° / 1.6 %; 1.0 m/s 80 % / 1.75 / 3.06 s / 17°; 1.5 m/s 77 % / 1.92 / 3.22 s / 17°.
  - v37_9250: 84 / 83 / 79 % kicked, 1.42 / 1.62 / 1.73 s, error 18–20°. A little quicker but less accurate.
  - v38_8750: no better than v36.
- New gene kick_quick_tau (planned v40): kick_power × (0.5 + 0.5·exp(−wait/τ)), so a kick pays more the sooner it comes; the aim factor still applies.
- v39_8750 (plain continuation of v36_8250): drift is large.
  - Side kicks fell 23.7 → 8.5 %; error 15.5 → 17.5°.
  - Power was the best yet (3.08, p90 5.32, 12.6 % at 5 m/s or more). Slow dribble passed the v17 gate (0.42 at 0.3 m/s). Approach 51 %, search 40 %.
  - Re-judged against this same-length control: v38 neutral; v37 kept side kicks (18 vs 8.5 %) but had less power and slow dribble.
  - Lesson: judge a resumed run only against a same-length no-change continuation, never against the parent checkpoint.
  - Exported k1_dribble_balanced_v39_8750.onnx.
- v40 = v36 genes + kick_quick_tau 1.5, from v36_8250. Control v39_8750, with the transition test as well.
- Transition test on the control v39_8750: kicked within 4 s 85 / 81 / 77 %; time to kick 1.52 / 1.74 / 1.84 s; errors 16–19°; falls 1.4–2.4 %. v37's 1.62 / 1.73 s at 1.0 / 1.5 m/s is a small real gain over it.
- v40 (kick_quick_tau 1.5) at 8750 vs v39_8750: mixed; stopped, not adopted.
  - Better: inside-foot 21.8 vs 8.5 %, time to kick 2.63 vs 2.82 s, error 16.6 vs 17.5°; transition kicked 82–87 vs 77–85 %, falls 0.2 vs ~2 %.
  - Worse: search 19 vs 40 % (reproduced with seed 11); power p90 4.89 vs 5.32; landing and dq jitter worse.
  - Time pressure is what keeps side kicks (v37 showed the same).
- B-Human probe (2026-10-22; dribble_skill_eval --tests kick --kick-min-deg 30 --bhuman-near 1.2, on v36_8250; angled windows only):
  - B-Human acting within 1.2 m: kick 3.91 m/s (p90 7.24; 27 % at 5 m/s or more, 11 % at 7 or more); error 9.5° (87 % within 15°); inside-foot 94 %; time to kick 2.37 s; falls 7.2 % per window.
  - v36 alone: 2.97 m/s (p90 4.86), 16.3°, inside-foot 30 %, falls 3.4 %.
  - So the adapter works (play_bhuman_kick.BHumanKickPolicy now also accepts DribbleCommand).
- v41 = v36 genes + kick_teacher_bhuman_dist 1.2 (new gene: B-Human teaches the legs in angled kick windows within 1.2 m; the kick-loop teacher keeps straight windows and arms), from v36_8250. Control v39_8750. User approved B-Human as a teacher on 2026-10-22.
- v41 (B-Human imitation on angled windows within 1.2 m) FAILED at 8750 vs v39_8750; stopped.
  - The kick collapsed: 1.96 m/s (p90 2.96); error 36.9°; inside-foot 6.6 %; kicks per window 0.26; foot yaw p50 5.5°. Dribble and search roughly the same.
  - Imitation loss started at 0.58 (the kick-loop teacher's was ~0.05).
  - Likely cause: B-Human acts on its own gait clock, which our policy cannot observe, so copying its leg targets averages into neither kick and swamps the straight kick too. B-Human works when it acts (the probe) but cannot be copied action by action.
  - Don't retry plain action imitation of B-Human; it would need the teacher to act (rollouts / DAgger with teacher execution) or a pose/outcome reward instead.
- v42 (side_w 1000, was 300) at 8750 vs v39_8750: best side kick and aim yet; exported k1_dribble_sidew_v42_8750.onnx and continuing to 9250.
  - Better: inside-foot 39.9 vs 8.5 % (v36 23.7); error 14.6 vs 17.5°, within 15° 72 vs 64 %; time to kick 2.64 vs 2.82 s; slow dribble the same (0.42 at 0.3 m/s).
  - Worse: power 2.95 / p90 4.82 vs 3.08 / 5.32; search 27 vs 40 %; approach 40 vs 51 %; landing p50 2.28 vs 2.14; tau left 25.
- v42_9250: search 37 % (8750: 27), approach 47 % (40), inside-foot 34.7 %, error 14.9° (72 % within 15°), power 2.85 / p90 4.79, slow dribble 0.40 / 0.53.
  - vs v37_9250 (same parent and length): far more side kicks and better aim; weaker kick and search.
  - Transition at 8750 beat v39: kicks 0.1 s sooner, 80–84 % kicked.
  - Exported k1_dribble_sidew_v42_9250.onnx; the side-kick deploy candidate. Kick power is the remaining gap.
- v42_9750: plateau, so v42 was stopped at ~9750 (2026-10-22).
  - Inside-foot 37 %; error 15.9°; power 2.90 / p90 4.77; search 44 %; approach 50 %; slow dribble 0.35 at 0.3 m/s.
  - Exported k1_dribble_sidew_v42_9750.onnx.
  - Open: kick power (~2.9 m/s mean vs B-Human ~3.9–4.3). Waiting on the user's choice: A (B-Human takes control in angled windows, its steps feed imitation only) or B (B-Human pose reward).
- v43 = option A, teacher takeover (user chose it on 2026-10-22). New genes kick_takeover_prob / kick_takeover_decay plus kick_teacher_bhuman_dist.
  - In a share β of the angled windows (drawn per window), B-Human *executes* the legs within 1.2 m before the kick; the student keeps arms and head.
  - Those steps feed only the imitation loss and the critic: AmpPPO.record_takeover zeroes their advantage after compute_returns.
  - β 0.5 decays to 0 over 3000 updates. Metric: Metrics/kick_takeover_frac.
  - Smoke test: imitation loss 0.15–0.24 (v41: 0.58).
  - Run: from v42_9250 with v42 genes; control v42_9750.
- v43 (takeover) FAILED at 9750 vs v42_9750; stopped (2026-10-22).
  - Overall: power 2.79 vs 2.90; inside-foot 22 vs 37 %; search 34 vs 44 %; torque saturation 1.1 %; tilt p90 11.8°.
  - Angled-only: power 2.86 vs 2.93; inside-foot 26 vs 48 %; error 15.4 vs 16.3°; time to kick 2.98 vs 2.83 s.
  - Takeover ran on ~1–1.8 % of steps; imitation loss fell 0.29 → 0.11, yet the student's own kick got worse.
  - Conclusion: neither imitation path transfers B-Human's clocked kick into our clock-free policy. Power needs another lever (reward or obs), not B-Human actions.
- B-Human-style kick shaping (user, 2026-10-22: "do 1,2,3", one per run). New genes in dribble_rewards.kick_power:
  - (1) kick_aim_neg / kick_aim_neg_deg: aim ramps to −neg between 40° and 80° error. v44 = v42 genes + kick_aim_neg 0.5, from v42_9250 (run 2026-10-22_21-18-25); control v42_9750.
  - (2) kick_pose_gate: the paid part × (0.5 + 0.5·ready²), ready = seconds set up (ball 0.05–0.40 m ahead of the feet along the kick direction, within 0.15 m sideways, trunk within 60°) over 0.6 s.
  - (3) kick_aim_curriculum: the wide aim σ² goes 0.5 → 0.15 as the running kick-error mean drops from 20° to 10°. Metrics kick_aim_wide_sigma2 / kick_aim_err_ema_deg.
  - (2) and (3) passed a smoke test; queue them after v44.
- v44_9750 (signed aim) vs v42_9750:
  - Better: power 3.08 / p90 5.05 vs 2.90 / 4.77; kicks at 5 m/s or more 10.9 vs 8.2 %.
  - Worse: error 16.9 vs 15.9°; search 33 vs 44 %; slow dribble 0.30 vs 0.35; falls 1.6 vs 1.3 %.
  - Inside-foot 33 vs 37 %; smoothness the same.
  - Note: search and slow dribble swing ±10 points between checks of one run (v42: 27 / 37 / 44 %), so only large gaps count. Judging at 10250 too.
- v44 NOT adopted at 10250; stopped.
  - Power 3.01 / p90 4.96 (v42 2.85–2.95); error 17.4° (v42 14.9–15.9); search 33 % at both checks; inside-foot 33.5 %.
  - Signed aim gave ~5 % power for ~2° aim and ~10 points of search.
- v45 = v42 genes + kick_pose_gate, from v42_9250; control v42_9750.
- Eval noise (v42_9750, seeds 7 / 11 / 13): search 44 / 41 / 39 %, approach 50 / 48 / 44 %, so ~±3 points. Checkpoint-to-checkpoint noise in one run is larger (v42 search 27 → 37 → 44 %), so judge search on two checkpoints.
  - Search spin_rate is only 0.74–0.80 rad/s and tilt p90 ~9° (lost_ball_spin saturates at 1.5 rad/s, weight 1). New gene lost_spin_w.
- v45_9750 (pose gate) vs v42_9750:
  - Better: error 14.7 vs 15.9°; landing p90 2.89 vs 3.19 (pass); tau left 23.8 vs 25 (pass).
  - Same: power 2.93 / 4.87.
  - Worse: search 26 %, approach 39 %, slow dribble 0.28; transition error 17–21°.
- Skill eval now runs approach,search,kick,transition by default; search reports spin_rate / tilt_p90.
- v45 (pose gate) NOT adopted; stopped at ~10400.
  - 10250: error 14.2° (75 % within 15°), search 41 %, approach 55 %, power 2.84 / 4.6, inside-foot 25.5 %, slow dribble 0.27, transition at 1.5 m/s 1.96 s / 74 %.
  - Over two checkpoints: ~1° better aim, but fewer side kicks, slow dribble 0.27–0.28 vs 0.35–0.40, slower transition at speed.
- v46 = v42 genes + kick_aim_curriculum, from v42_9250; control v42_9750.
- Launch helper: scratchpad launch_run.sh NAME TAG GENES BASE_RUN IT CHANGE CONTROL (sets the watcher env correctly).
- Replicate noise (v46_9750 = a no-change v42 continuation, because the curriculum never activated; training error EMA ~20.5° > 20° threshold), vs v42_9750:
  - Kick measures reproduce: power 2.92 vs 2.90, p90 4.77 both, error 15.9 both, inside-foot 35 vs 37 %.
  - Noisy: slow dribble 0.29 / 0.47 vs 0.35 / 0.53 (±0.06); search 39 vs 41 ± 3; approach 44 vs 47.
  - So trust kick deltas over ~0.1 m/s / 0.7°; slow dribble and search need over ~0.08 / 8 points.
  - Re-read: v45's aim gain is real (14.2–14.7°) and its slow-dribble loss is mostly noise; v44's power gain (+4–6 %) and aim loss are real.
- v46b = v42 genes + kick_aim_curriculum with kick_aim_curr_deg [14, 24], from v42_9250.
- v46b_9750 (aim curriculum 14–24°; wide σ² was 0.35 at 9800) vs the no-change replicates:
  - Better: power 3.01 / p90 5.04 vs 2.91 / 4.77; error 14.7 vs 15.9°; transition error 15 / 16 / 18 vs 17.8 / 17.9 / 19.2°.
  - Worse: inside-foot 30.5 vs 35–37 %; time to kick 2.83 vs 2.61 s.
  - Search, approach and slow dribble within noise (37 %, 49 %, 0.39).
  - First change to raise power and aim together. Continuing to 10250.
- v46b_10250: power 2.91 / 4.89, error 16.7° (back to the replicates), search 30 %, tilt p90 12.4 (fail).
  - The adaptive curriculum oscillates: training error rose to 23°, so σ² loosened back to 0.47.
  - Stopped. The v46b_9750 checkpoint is the best all-round model: power 3.01 / p90 5.04, error 14.7°, slow dribble 0.39, approach 49 %, transition error 15–18°. Exported k1_dribble_aimcurr_v46b_9750.onnx.
  - Idea: a fixed wide σ² ≈ 0.35 instead of the adaptive one.
- Parity "ball slot mismatches" (21–267 / 4000) appear in every model; joint targets match 100 %. Not a regression.
- v47 = v42 genes + kick_quick_tau 1.5, from v42_9250 (time-to-kick retest).
- Runner run-time modes (2026-10-23, Level 1; opt-in, default behaviour unchanged).
  - DribblePolicy.handle_mode_request("kick[:deg]" / "stop" / "dribble" / "dribble:<deg>:<speed>") plus set_joystick().
  - RobotBridge mode_buttons / mode_topic (std_msgs/String) → take_mode_request().
  - policy_runner_main flags --dribble-mode-buttons "0=kick,1=stop,3=dribble" and --dribble-mode-topic.
  - Docs: DRIBBLE_POLICY_IO.md §5. Tests: test_dribble_modes.py (run with runswift .venv python; system python has no numpy).
  - Not yet run on ROS: the bridge was only statically checked.
- v47 (kick_quick_tau 1.5 on v42) REJECTED at 9750.
  - Time to kick 2.68 s (no gain); transition 1.45 / 1.70 / 1.85 s (no gain); power 2.95 / 4.95; error 16.1°; inside-foot 40 %.
  - Search 23 %, the second time quick-pay cut search (v40: 19 %), so the effect is real; slow dribble 0.23.
  - Don't use kick_quick_tau.
- v48 = v42 genes + lost_spin_w 3, from v42_9250 (search spin).
- Transition time split (v46b_9750; straight / angled): 0.5 m/s 1.30 / 1.70 s, 1.0 m/s 1.52 / 1.89 s, 1.5 m/s 1.80 / 1.99 s.
  - Straight kicks are slow too; kick_line_up (weight 4 per step, ~0.1 per wait) vs kick_power (~15 per kick) is not the cause.
  - Time to kick looks like a gait/motor floor (~3 steps). Reward levers (v37 wait cost, v40/v47 quick pay) failed.
- New gene kick_aim_wide (fixed wide σ², default 0.5); planned v49 = 0.35 (v46b peaked there with power and aim up).
- v48 (lost_spin_w 3) REJECTED at 9750.
  - Spin 1.16 vs 0.74 rad/s, tilt 9.0 (stable), but time to see is still 4.5 s.
  - Search 28.5 %, approach 33 %, slow dribble 0.24, search falls 4.6 %.
  - Spin speed isn't the search bottleneck (probably the 1.5 s lost-delay or spin direction).
- v49 = v42 genes + kick_aim_wide 0.35 (fixed), from v42_9250.
- Search bottleneck found (2026-10-23).
  - While the ball is lost, head pitch is ~40–44° down (v42 40.4°, v48 43.6°); the camera's vertical half-FOV is 21° (K1_CAMERA_HALF_FOV[1]) with camera_pitch 0.
  - So the view ends ~2–3 m out: the ball is re-seen at 2.6–2.9 m, and balls 3–4 m away stay unseen however fast the robot spins (v48).
  - FOV_VIS_RANGE 3.0 is debug drawing only.
  - New gene lost_head_w (and lost_head_pitch_deg, default 15): rewards the head near 15° down while lost.
  - Search test now reports head_pitch_deg and seen_dist. Planned v50.
- v49_9750 (kick_aim_wide 0.35 fixed) vs the replicates: the best fixed-gene result tonight; exported k1_dribble_aimwide_v49_9750.onnx and continuing to 10250.
  - Better: power 3.07 / p90 5.10 (11.4 % at 5 m/s or more); error 14.0° (74 % within 15°); landing p50 1.91 / p90 2.94 (pass); transition error 15.1 / 16.8 / 16.1°.
  - Worse: inside-foot 30 %; time to kick 2.79 s.
  - Within noise: search 38 %, approach 43 %, slow dribble 0.37.
  - It reproduces v46b_9750's gain with a fixed setting.
- v49_10250: ADOPTED as the new base and best all-round deploy candidate; exported k1_dribble_aimwide_v49_10250.onnx (parity 0 %).
  - Power back to 2.93 / 4.72 (the 9750 power gain didn't hold, like v46b), but error 14.6° held (−1.3°).
  - Inside-foot 34 %, search 42.5 %, approach 55.7 %, slow dribble 0.45 / 0.55 (passes v17 at 0.3).
  - Transition best yet: kicked 87 / 86 / 81 %, straight-kick time 1.19 / 1.42 / 1.49 s, falls ≤ 1.4 %.
- v50 = v42 genes + lost_head_w 1.0 (head ~15° down while lost), from v42_9250; compare with the 9750 replicates.
- v50_9750 (lost_head_w 1) vs the replicates: big search gain; exported k1_dribble_headup_v50_9750.onnx.
  - Better: search 59.6 vs 39–44 %; time to see 3.85 vs 4.5 s; search falls 1.6 vs 3.0 %; approach 53.5 %; slow dribble 0.42 / 0.57; error 14.7°; power 3.0 / 4.91.
  - Head pitch only 42 → 37°; seen distance 3.0 m.
  - Worse: inside-foot 22 vs 35–37 %; search tilt p90 11.1 vs 9°.
- v51 = v49 genes (kick_aim_wide 0.35) + lost_head_w 1, from v49_10250. Control: v49's own checkpoints (9750 / 10250).
- v51_10750 (v49 + lost_head_w) vs v49 9750 / 10250: best gate result yet (only falls, jitter and tilt fail); exported k1_dribble_aimhead_v51_10750.onnx. Continuing to 11250.
  - Search: 59.1 % (v49 38 / 42.5), time to see 3.89 s.
  - Gates: slow dribble passes v17; landing, torque and dq pass.
  - Transition: straight-kick time 1.00 / 1.41 / 1.49 s (best).
  - Kick: power 2.96 / 4.94; inside-foot 30 %.
  - Lost: error 15.9° (v49's aim gain gone); transition error 19–22°; tilt p90 12.9° (fail), search tilt 11.8°.
- v51_11250: ADOPTED v51 (v49 + lost_head_w) as the base; exported k1_dribble_aimhead_v51_11250.onnx.
  - Better: error 14.7° (recovered); inside-foot 41 % (best); straight-kick time 0.95 / 1.20 / 1.37 s (best); search 52 %, search tilt 9.9°.
  - Same: power 2.98 / 4.90.
  - Gates: 8 fails (landing, tau 25, jitter, tilt 12.1, slow dribble 0.39 / 0.53).
  - Deploy picks: 10750 = cleanest gates (3 fails); 11250 = best kick technique and time.
- v51_11750: power 3.07 / p90 5.10, error 14.6° (72 % within 15°), search 55 %, inside-foot 27 %, slow dribble 0.34 / 0.51; gates fail slow dribble, falls, jitter, tilt (landing and torque pass).
  - Plateau over three checkpoints, so stopped. Exported k1_dribble_aimhead_v51_11750.onnx (most balanced).
- v52 = v51 genes + kick_prob 0.5 (was 0.25), from v51_11750: option B (more kick practice, long run). The user hasn't chosen A or B; B keeps the deploy interface.
- v52_12250 (kick_prob 0.5) vs v51 checkpoints:
  - Worse: power 2.76 / 4.52, error 17.3°, jitter 0.118 (fail), transition slower.
  - Better: search 76.5 %, approach 62 %. Kicked balls respawn 1–8 m away, so more kick windows mostly train approach/search, not kicking.
  - One more checkpoint (12750); stop if kick power isn't above 3.0.
- v52 (kick_prob 0.5) REJECTED at 12750; stopped.
  - Power 2.76 / 4.42, error 17.8°, jitter 0.122, 0.5 m/s tracking error 0.19 (fail), slow dribble 0.27.
  - Search 67 % and approach 64 % (more far-ball practice).
  - More kick windows ≠ more kick power.
- AMP style is already gated OFF in kick windows within 1.2 m and for 0.6 s after the kick (dribble.py amp_style_gate), so it is not the kick-power limiter.
- Kick power has stayed at ~3.0 m/s across every reward lever (v33–v52). Remaining options change deployment (B-Human handover, or observation history / phase input), so they need the user's go-ahead.
- v53 = v51 genes + critic_alphas [0.1, 0.5, 0.4] (kick critic 0.25 → 0.4 of the advantage), from v51_11750. Single change, same interface. Control: v51 checkpoints.
- Next (input path, user allowed "change the input if needed"): actor obs history. mjlab ObservationGroupCfg.history_length and the runner's ObservationHistory ("term" layout) both exist. Warm-start by widening the actor's first layer with zero columns. Separate model version; runner + parity updated.
- 2026-10-23 ~11:40: user said "stop". v53 (critic_alphas [0.1, 0.5, 0.4]) was killed right after launch, with no results; nothing is training.
  - Obs-history work was only investigated (no code changed).
  - Best deploy model: k1_dribble_aimhead_v51_11750.onnx.

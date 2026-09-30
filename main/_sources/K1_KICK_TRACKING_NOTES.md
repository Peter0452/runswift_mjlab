# K1 tracking kick: problems and what changed

Last updated: 2026-09-30.

This note is the motion-tracking kick (`Mjlab-Tracking-Flat-Booster-K1-Kick-Stage2` and `Mjlab-Tracking-Flat-Booster-K1-Kick-Box`). It is not the walk-AMP kick in `src/mjlab/tasks/kick/` (`Mjlab-Kick-Near-Booster-K1` and the notes in `docs/K1_KICK_TRAINING_NOTES.md`).

The goal is a Booster K1 DeepMimic / BeyondMimic prior that kicks a ball, then stands, and later deploys through `k1_policy_runner`. Stage 2 is the RoboNaldo task-2a analogue: ten clips (five right-foot clips plus their mirrors), a physical mid goal, and the ball on the recorded strike. The box task is the wider-ball fine-tune on top of that.

## What stayed fixed

- Physics 200 Hz (`dt` 0.005), policy 50 Hz (decimation 4), episode 10 s, 4096 envs. Anchor body is `Trunk`. Network `[512, 256, 128]`, ELU, empirical normalization on. Kick launches are capped at 30,000 added iterations. Checkpoints save every 500.
- Actor 431, critic 554. Style `z` is a 3-D one-hot (planted / running / moving). The policy does not choose the foot. Ball and clip stay paired. Motion adaptation and jump stay off. Continuous `z` was not restored. Observation size was not changed, so a stage-2 checkpoint still loads.
- Left-foot mix on training prefix sampling is 60% left / 40% right (`left_clip_prob = 0.6`). Play ignores that mix.
- Goal is straight ahead, uniform 4–8 m. Ball-to-target reward uses Gaussian std 1.0.
- `10_04` is a straight walk and is excluded. Recorded strikes in the motion frame, where the foot crosses ball height: `10_01` (0.458, ±0.520), `10_02` (0.488, ±0.581), `10_03` (1.189, ±0.650), `11_01` (1.219, ±0.635), `10_05` (1.277, ±0.681). Planted is `10_01` / `10_02`, running is `10_03`, moving is `10_05` / `11_01`.
- Motion file: `/home/peter/Desktop/Project/RL/data/retargeted/k1/kick/tracking.npz`.

## Stand after the kick

**Problem.** After the clip the reference freezes on the last kick pose. The robot has no signal to recover into a stand once the ball is gone.

**What we did.** On the box task only, after the clip has ended and the ball’s planar distance from the trunk is greater than 1.0 m, the command latches the robot’s xy and a yaw-only upright quaternion. Joint targets become the AMP walk home keyframe (`z = 0.5125`, arms out, hips −0.4, knees 0.8, ankles −0.4, velocities 0). While the clip is done but the ball is still close, the last joint pose is held and reference joint and body velocities are zero. The robot is not teleported. Relative body poses are copied from the robot while standing, so body rewards do not fight the stand. `stand_joint_pose` (exp of summed squared joint error, std 0.5, weight 1.0) is zero until that latch. Anchor position termination on this task is z-only, threshold 0.5 m.

## Ball placement

**Problem.** One recorded strike per clip cannot cover a wider ball area, and different styles strike in different places. Planted strikes sit near x ≈ 0.46 m. Running and moving strikes sit near x ≈ 1.2 m.

**What we tried, then removed.** A single box, then two style reaches: planted x 0.16–0.79 m with |y| 0.22–0.88 m, and a shared reach box for running and moving at x 0.70–1.30 m with |y| 0.34–0.98 m. Those regions are no longer used by the box config. The sampling code is still in `commands.py`.

**What is in the box task now.** The clip is chosen first, with the stage-2 prefix and the 60/40 left mix. The ball center is that clip’s estimated strike. x and y are then uniform in ±0.5 m (`strike_pos_noise = (0.5, 0.5)`). Ball velocity noise is 0. Stage 2 stays at ±0.1 m. Play of the box task also uses ±0.5 m. A planted strike minus 0.5 m can put the ball slightly behind the robot (about −0.04 m).

## Rewards

**Problem.** The first box fine-tune lowered limb tracking so the foot could leave the clip for an off-strike ball, while keeping the safety terms.

**What we changed, then reversed.** `motion_body_pos`, `motion_body_ori`, `motion_body_lin_vel`, and `motion_body_ang_vel` were set to 0.2. Stage 2 uses 1.0. That cut is undone. The box task again uses the stage-2 weights.

**What stayed.** `stand_joint_pose` at weight 1.0. Trunk position 1.0, trunk orientation 0.5, base height −20, end-effector fall −100, action rate −0.1, action smoothness −0.0015, joint limit −10, feet slip, no-fly, self-collision. Goal terms are unchanged: ball-to-target 8.0 (std 1.0), contact orientation 1.7, feet / com / torso distance 0.8 (std 0.5), contact and contact count 0.8, ball velocity 0.45 (std 1.0), ball over the line 0.4, weak-foot contact −0.4, self-contact of the feet −0.16. Terminations stay: anchor z 0.5 m, anchor orientation 0.8, end-effector z 0.35 m.

## Why the first box fine-tune failed

Run: `logs/rsl_rl/k1_kick_tracking/2026-09-30_00-55-14/`. It resumed `model_99000.pt` from `2026-09-29_08-23-57` for 30,000 iterations (99000 → 128999). That run used the old wide ball regions, limb weights 0.2, and the stand reward. It finished.

Leaving the clip to reach a ball off the strike tips the trunk. The anchor-orientation termination ends the episode before ball-to-target or the stand is paid. The stand reward’s maximum over the whole run was 0.0015, so the stand never trained. Actions are unclipped (`clip_actions` null). Adaptive learning rate swung from 1e-5 to about 8.6e-4. The first action-rate blow-up was at iteration 99383. About 2702 of 30000 iterations had a negative mean reward, and 1626 had an action-rate magnitude above 10. Value loss exploded. Recoveries hug the clip and miss the ball.

`model_99500.pt` in that folder is still essentially the stage-2 kicker (median reward about 20.2, episode length about 424, ball-to-target about 1.22). `model_111500.pt` was the best later stretch that stayed clean (reward about 16.0, ball-to-target about 0.82). `model_128999.pt` is worse (reward about 9.7, ball-to-target about 0.48, more orientation failures). Do not resume from 128999.

TensorBoard means were useless because of spikes (action rate near −1e9, value loss near 1e16). Medians were used instead.

A curriculum was discussed and not coded: grow the ring around each strike in steps (5 cm, then 10, 15, 30), keep limb tracking high until a wider ring is kicked without extra falls, clip actions, use a fixed low learning rate, and pay the stand only after the ball has actually left. The current box task jumped straight to ±0.5 m.

## How RoboNaldo generalizes

This was a comparison, not a port.

- Task 1: ball ±0.1 m around a fixed init `(0.25, 1.0, 0.12)`, motion adaptation off.
- Task 2: ±0.5 m, adaptation still off. Body tracking stays at scale 1.0. Anchor position and orientation task scale drops to 0.1 (the tracking stage uses 0.5).
- Task 3: ±1.0 m plus ball velocity, adaptation on. The anchor shifts halfway toward the ball (lambda 0.5) and yaw faces the ball. A jump flag snaps the clock when the ball enters 0.25 m within 0.4 s, then latches a stand about 1 s after the kick frame. The policy keeps imitating an edited command.

Our failed run left the clip command fixed and cut limb reward in the same step. Adaptation, the jump flag, and RoboNaldo stages 2b and 3 were not implemented.

## Domain randomization matched to AMP walk

**Problem.** The kick tracker’s randomization did not match the AMP walk, and the first comparison left out delay, observation noise, and reset randomization. Those are part of the randomization.

**What we did.** `_match_amp_walk_dr` in `src/mjlab/tasks/tracking/config/k1/env_cfgs.py` applies the walk’s randomization to stage 1, stage 2, and the box task. This is a different distribution from `model_99000.pt`.

Matched:

- Foot friction, absolute, shared draw, (0.75, 1.25). Kick foot geoms: `r"^(left|right)_foot[0-5]_collision$"`.
- Encoder bias ±0.015 (was ±0.01).
- Command delay 2–8 physics steps (10–40 ms), hold probability 0.3. The kick used 2–16 steps and hold 0.9. The override copies the kick robot’s actuators only. `k1_constants.py` is unchanged, so getup and other K1 tasks keep 2–16 / 0.9. A stale comment in that file still says 0–3 steps.
- PD `kp` and `kd` scaled 0.8–1.2. Effort is not scaled by that event.
- `base_com` removed. Trunk pseudo-inertia alpha ±0.05, t ±0.05. Limb inertia alpha ±0.05, t ±0.025 on every body except `Trunk`.
- Terrain contact `solref` and `solimp` matched, shared, on entity `terrain`. The ground stays a plane.
- Push interval (1.5, 4.0) s. Velocity x/y ±0.28, z ±0.2, roll/pitch ±0.52, yaw ±0.78. The kick push was 1–3 s and xy ±0.5.
- Reset velocity matched to the walk: x/y ±1.0, z (0.01, 0.3), roll/pitch ±0.1, yaw ±0.5. Reset pose stays the tracking clip jitter (xy ±5 cm, z ±1 cm, roll/pitch ±0.1, yaw ±0.2).
- Joint velocity reset ±0.1 on `MotionCommandCfg`. Play zeros it. Joint position reset stays ±0.1.
- Actor joint-velocity observation noise ±1.5 (was ±0.5). Critic joint velocity stays un-noised. Gyro ±0.2 and joint position ±0.01 are unchanged.

Not copied, on purpose: the walk’s spawn pose (xy ±0.5 m, yaw ±π), because that leaves the clip; rough terrain geometry; projected-gravity observation noise, because that would change the observation size. Anchor, ball, and target observation noise stay, because the walk has no such observations.

AMP walk has no ankle-only randomization. Ankles share the PD scale, encoder bias, delay, reset, and limb inertia. Foot friction is one shared draw on the foot collision geoms.

## Torque limits

**Problem.** Torque limit is part of the randomization picture, and the kick clip did not match the walk motors.

The kick had been using a flat Isaac Gym clip: head 7, arm 10, hip pitch 30, hip roll 20, hip yaw 20, knee 40, ankle pitch 20, ankle roll 15. The AMP walk uses motor peaks from the Booster actuator specs, available in full only below a knee-point velocity, then derated. The MJCF has no effort range. The ankle peak is one E4310 value (38.3), not doubled. The actuator file notes that the parallel linkage still needs another look.

**What we did.** The kick tracker (not the shared `k1_constants`, not getup) now flat-clips at the AMP peaks: head 6, arm 14, hip pitch 68, hip roll 76, hip yaw 38.3, knee 112, ankle pitch 38.3, ankle roll 38.3. The clip is still flat at the peak at any speed. The walk’s speed derating was not ported. Deploy `EFFORT_LIMIT` (hips 60, ankle pitch 24, ankle roll 15) was not updated.

## Deploy sim does not match training

Default deploy ONNX is `k1_policy_runner/kick_tracking_models/model_85500.onnx`, trained with the old delay (2–16 steps, hold 0.9), not the new AMP delay. Deploy npz is the five right-foot clips only. `HEAD_PITCH_LOOK_DOWN` 0.85 overwrites the network. `last_action` stores the raw output. The MuJoCo runner holds the last frame unless `--walk-model` blends for 0.4 s. Control is 50 Hz and physics is 5 ms, which already match training. The XML has no actuators; the runner applies PD through `qfrc_applied`.

Training trunk error is the clip trunk relative to the robot trunk. Deploy `project_clip_to_live_pelvis` discards the clip trunk and returns the live pose, so anchor error is identically zero every tick, including orientation. Putting the training formula back only delayed the post-clip fall by about 0.5 s. The fall itself is the frozen last frame.

**Ankle shake.** The policy target is a 50 Hz staircase. In a recorded deploy, ankle-pitch steps were on the order of 25 times the reference step size. Training applies a delayed copy of that staircase (a shift register, not a low-pass), so the joint does not chase each new jump on the next 5 ms step. The same delay in deploy only shifts the jumps. It does not smooth them. The joint is not shaking the same way inside training. The policy target is stepwise in training too.

What would make the deploy sim closer, none of it coded:

1. Use the training trunk error in the shared MuJoCo world. Do not zero it.
2. Delay matching the checkpoint being deployed. For `model_85500` that is lag 2–16 and hold 0.9, as a shift register.
3. Use the training torque clip. That clip is now the AMP peaks in the trainer. The deploy sim still has its own `EFFORT_LIMIT`.
4. Do not overwrite head pitch.
5. Stop at the end of the clip, or resample. Do not hold the last frame.

A ball on the strike and a 7 m straight goal are already inside the stage-2 distribution.

## Checkpoints

| Run | Checkpoint | Role |
|---|---|---|
| `logs/rsl_rl/k1_kick_tracking/2026-09-29_08-23-57/` | `model_99000.pt` | Stage-2 kicker. Start new box runs from here. |
| `logs/rsl_rl/k1_kick_tracking/2026-09-30_00-55-14/` | `model_99500.pt` | Best save of the failed box run. Still the stage-2 kicker. |
| same | `model_128999.pt` | End of the failed box run. Do not resume. |
| `k1_policy_runner` | `model_85500.onnx` | Frozen deploy model. Old delay. Do not replace unless asked. |
| walk handoff | `model_80000.pt` of the 2026-09-29 kick log | Frozen kick for that handoff. Do not change unless asked. |

Resuming `model_99000.pt` into the current box task is another distribution shift: AMP-matched randomization, AMP peak torques, ball ±0.5 m around each strike, stage-2 rewards, plus the stand.

```bash
cd /home/peter/Desktop/Project/RL/runswift_mjlab
uv run train Mjlab-Tracking-Flat-Booster-K1-Kick-Box \
  --agent.resume True \
  --agent.load-run 2026-09-29_08-23-57 \
  --agent.load-checkpoint model_99000.pt \
  --env.scene.num-envs 4096
```

A later launch wrote `logs/rsl_rl/k1_kick_tracking/2026-09-30_10-04-25/`. `model_99500.pt` there is the loaded stage-2 weights after the new config’s first saves, not a finished fine-tune.

## Viewing one agent

`play` with `--checkpoint_file` does not pick up the motion path already set in the task config. Pass the npz, and `--num-envs 1` for a single robot.

```bash
cd /home/peter/Desktop/Project/RL/runswift_mjlab
MUJOCO_GL=egl uv run play Mjlab-Tracking-Flat-Booster-K1-Kick-Box \
  --checkpoint_file logs/rsl_rl/k1_kick_tracking/2026-09-30_10-04-25/model_99500.pt \
  --motion-file /home/peter/Desktop/Project/RL/data/retargeted/k1/kick/tracking.npz \
  --num-envs 1 \
  --viewer viser
```

## Not done

Deploy trunk error, a matching command delay in the deploy sim, deploy torque limits, removing the head-pitch overwrite, stopping at clip end, action clipping, a fixed learning rate, the 5 cm curriculum, speed-derated motor curves, rough terrain, projected-gravity observations, motion adaptation, and the jump flag.

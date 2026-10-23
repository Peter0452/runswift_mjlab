# K1 kick — stage 2 (approach) notes

Task: `Mjlab-Velocity-Kick-Approach-Amp-DA-Muon-Booster-K1`
Logs: `logs/rsl_rl/k1_kick_approach_amp/`
Code: `src/mjlab/tasks/velocity/mdp/approach.py`,
`src/mjlab/tasks/velocity/config/k1_amp/env_cfgs.py`
(`booster_k1_kick_approach_env_cfg`)

The kick is trained in three stages that share one 83-dim actor layout:

1. **Stage 1** (`Mjlab-Velocity-Kick-Stage1-Amp-DA-Muon-Booster-K1`): walk.
   Slots 75–82 are `constant_zeros` placeholders.
2. **Stage 2** (this note): walk to the ball and line up behind it on the
   ball→target line. No kick.
3. **Stage 3**: kick. Uses `kick_range`.

## Stage 2 spec

The robot spawns facing the ball (ball 1–4 m away, within ±0.4 rad of the
trunk heading). The target is 4–8 m from the ball in any direction, so the
robot may have to walk around the ball. Success means standing within 0.5 m,
inside the ±45° wedge behind the ball, with heading within 0.4 rad of the kick
line, keeping the ball in the head camera the whole way, and touching the ball
only when lined up.

The actor gets only what the real robot can know:

| Slots | Content |
|---|---|
| 72–73 | Ball xy in the trunk frame. Zero when the head camera cannot see it. |
| 74 | Unused, always 0. |
| 75–77 | This episode's limits on \|vx\| ∈ [0.3, 1.2], \|vy\| ∈ [0.2, 1.0], \|wz\| ∈ [0.4, 1.25]. |
| 78–79 | Kick direction (cos, sin) in the yaw frame, computed from the **last seen** ball. |
| 80–82 | Kick-range one-hot of the target distance. Nothing rewards it in stage 2; stage 3 inherits it unchanged. |

The critic reads the true, unmasked ball in 72–73.

Rewards: `approach_align` (80), `approach_close` (100), `approach_stand` (2),
`approach_view` (0.5), `approach_heading` (50, see the body-heading change
below), `approach_bad_contact` (−20), `approach_speed_limit` (−10, summed
excess over the limits). Linear and angular velocity tracking are
off (weight 0). The gait terms still read a hidden walk/stand flag in
`vel_command_b`, which drops to zero once the robot is lined up.

Camera: `ApproachYawCommandCfg` holds `fov_half_angle` (0.69 rad horizontal),
`fov_vertical_half_angle` (**None = no vertical check**, the current default)
and `camera_pitch`. When the real camera is measured, set the vertical value
and **err small**: a cone larger than the real camera trains the policy on
views it will not get.

## Issue 1 — resuming stage 2 straight from stage 1 collapses the policy

**Run:** `2026-10-01_03-09-29_approach` (resumed from stage 1 `model_9000.pt`
through a symlink into the approach folder).

**Symptoms:** at the first update, KL = 22 and value loss = 18. After that,
episodes lasted about 12 steps, nearly all ending in `illegal_contact`, ball
distance never moved, and action std rose from 0.45 to 0.75. It never
recovered (iterations 9000 → 13400).

**Root cause:** stage 1 fed zeros into slots 75–82, so:

- the obs normalizer's std for those slots was 0. rsl_rl divides by
  `std + 0.01`, so stage 2's real values were scaled by about 100
  (`see_ball = 1` reached the network as 100);
- the first-layer weights for those slots never received a gradient and were
  still random.

Random weights × inputs around ±100 saturate the first layer. Mean |action|
jumped from 0.64 to 3.30 on the same inputs, so the robot fell immediately.

**Fix:** prepare the warm start with `scripts/prepare_warmstart.py`. For the
slots whose meaning changes, it zeroes their first-layer weight columns (actor
and critic) and resets their normalizer stats, so the stage 2 policy starts out
**exactly** equal to the stage 1 walker (verified: max action difference 0.0).

```bash
uv run python scripts/prepare_warmstart.py \
  --input logs/rsl_rl/k1_kick_stage1_amp/2026-09-30_22-03-48/model_9000.pt \
  --output logs/rsl_rl/k1_kick_approach_amp/2026-10-01_stage1-9000_warmstart_v2/model_0.pt \
  --reset-obs-dims 74:83 --normalizer-count 10000000
```

Then train with `--agent.resume True --agent.warm-start True` pointing at that
folder. Do not symlink a stage 1 run into the approach folder.

**Lesson for stage 3:** any slot a stage holds constant gets the same zero-std
trap at the next handoff. Reset those slots, or better, feed realistic dummy
values during the earlier stage. `kick_range` is already real in stage 2, so
stage 3 needs no reset for it.

## Issue 2 — the first stage 2 code did not match the plan

The first version of `approach.py` differed from the spec above:

- Slot 74 held a scripted yaw rate toward the kick line, and
  `track_angular_velocity` (weight 2) rewarded copying it. When the ball was
  out of view, that yaw rate came from the **true** ball direction, which
  leaks information the real robot does not have.
- `speed_limit` held `[see_ball, 0, 0]`, with no actual speed limit.
- `kick_direction` used the true ball even when unseen.
- The ball spawned at a random bearing, not in front of the robot.
- The symmetry flip negated slot 77 (the old critic ball y). Slot 77 is now a
  speed limit, which is a magnitude and must not flip.

All of these are fixed. Removing the yaw teacher makes the task honest but
slower to learn: after 60 iterations, time in the kick position was 0.21
versus 0.69 with the teacher.

## Issue 3 — one diverged simulation destroyed a healthy run

**Run:** `2026-10-01_14-41-20_approach_v2`.

**Before the collapse:** it was learning well. At about iteration 5100:
episode length about 900, time in the kick position 0.53, ball visible 0.96.

**Event:** at iteration 5121 one of the 4096 simulations diverged. Before its
state turned NaN, it reached huge but finite velocities. The penalties
computed from that state were enormous (`upper_body_posture` −26,590 and
`action_rate_l2` −480 for the episode; the step's mean reward was −1.17
million). The old NaN guard only zeroed NaN/Inf values, so these went straight
into PPO: value loss 10¹², KL 5.79, symmetry loss 1.8·10⁴. The critic was
wrecked, and the policy degraded to about 11-step episodes over the next ~800
iterations. It never recovered, and 9 more blow-ups followed.

KL was normal on the iterations right before (about 0.015), and no
curriculum changed at that point. Look for this signature: a value-loss spike
at the same iteration as `Episode_Termination/nan_state` > 0.

**Fix (protects all k1_amp tasks):**

- New termination `physics_blowup` (`src/mjlab/envs/mdp/terminations.py`):
  NaN/Inf **or** any |qvel| > 200. Healthy rollouts peak at |qvel| = 70
  (1.5M env-steps measured with `model_5100.pt`).
- New `TerminationTermCfg.invalid_state` flag. Envs flagged by such a term get
  **zero reward for every term** that step (`RewardManager.compute(...,
  invalid=...)`).
- The k1_amp base config keeps the `nan_state` log key but uses
  `physics_blowup` with `invalid_state=True`.

**Recovery:** resume from `model_5100.pt`, the last checkpoint before the
blow-up. Checkpoints after about 5150 come from the collapsed policy.

```bash
MUJOCO_GL=egl uv run train Mjlab-Velocity-Kick-Approach-Amp-DA-Muon-Booster-K1 \
  --env.scene.num-envs 4096 --agent.resume True \
  --agent.load-run 2026-10-01_14-41-20_approach_v2 \
  --agent.load-checkpoint model_5100.pt \
  --agent.run-name approach_v2_resume
```

## Change — line up the body on the way in, not at the ball

**Problem:** only the final stand zone rewarded body (pelvis) heading.
`approach_view` rewards the head camera only. Measured on `model_5100.pt`
(1024 envs × 900 steps):

| Phase | Body yaw error to kick line, median / 90th pct | Body within 0.4 rad | Head vs body yaw, median |
|---|---|---|---|
| Stand zone (≤ 0.5 m, in wedge) | 0.03 / 1.90 rad | 75% | 0.13 rad |
| Near (≤ 1.5 m, not lined up) | 1.65 / 2.63 rad | 20% | 0.56 rad |
| Far (> 1.5 m) | 1.97 / 2.86 rad | 8% | 0.21 rad |

The robot walked in facing the ball, turned in place within 0.5 m of it (the
worst place to turn before a kick), and used the head to keep the ball in view.
A quarter of stand-zone time was badly misaligned: the stand reward's yaw
Gaussian (σ = 0.25 rad) is ≈ 0 at large errors (e⁻⁵⁸ at 1.9 rad), so a robot
parked sideways got no signal to turn.

**Changes:**

- New reward `approach_heading` (weight 50): the per-step signed reduction in
  body |yaw error|, active from the previous step inside the wedge and within
  `HEADING_SHAPING_DISTANCE` = 1.5 m. Same form as `approach_align`, so
  turning away costs what turning back pays. A full 1.6 rad turn is worth
  about 1.6 episode-reward, comparable to `approach_align`'s ~3.
- `approach_stand` yaw score is now `stand_yaw_quality`: 0.5 × the old
  Gaussian + 0.5 × a linear ramp `1 − |err|/π`. The peak on the line is
  unchanged; far from the line the score still rises when turning toward it.
- New metrics: `Metrics/approach_body_yaw_err_near` (mean body |yaw error|
  inside the heading gate) and `Metrics/approach_head_offset` (mean |head yaw
  − body yaw|).

The head is left free; looking toward the ball while turning is fine.

**Run:** `2026-10-01_20-32-20_approach_v3_heading` (iterations 5100–5150), a
full resume from `approach_v2/model_5100.pt` with the blow-up guard and these
reward changes. It continues in `2026-10-01_20-35-05_approach_v3_heading` from
`model_5150.pt`.
Watch `approach_body_yaw_err_near` ↓, `approach_in_stand` back to ≥ 0.5, and
the stand-zone alignment improving without a drop in `approach_see_ball`.

## Open issues

- **Why the sim diverges** is unknown. The guard contains the damage but does
  not remove the cause. `NanGuardCfg` can dump the state when it happens.
- **The speed-limit penalty may be too strong.** In the 60-iteration smoke
  test it was −0.53 per episode, versus +0.44 for all approach rewards
  combined, while the real overspeed averaged only 0.05 m/s. It probably
  penalizes normal gait sway. Options: penalize a ~0.5 s average velocity, add
  a tolerance band, or lower the weight to about −3.
- **No memory:** the policy is an MLP. Once the ball leaves the view, it only
  sees zeros for the ball and the kick direction. Spawning facing the ball and
  `approach_view` keep the ball in sight; stacking past observations is the
  fallback.
- **Vertical FOV** is off until the K1 camera is measured.

## Viewing in play

`play` draws debug visuals for this task (`debug_vis` is on only in the play
config):

- **Yellow post and sphere:** the kick target.
- **Thin yellow line on the ground:** ball → target, i.e. the kick line.
- **Lines from the head:** camera FOV edges, 3 m long. **Green** while the
  ball is visible, **red** when it is lost. With a vertical FOV set, four
  corner rays are drawn instead of two.

```bash
uv run play Mjlab-Velocity-Kick-Approach-Amp-DA-Muon-Booster-K1 \
  --checkpoint-file logs/rsl_rl/k1_kick_approach_amp/<run>/model_XXXX.pt \
  --num-envs 1 --viewer viser
```

## Metrics to watch

| Metric | Healthy direction |
|---|---|
| `Metrics/approach_in_stand` | ↑ (about 0.5 by iteration 5000 in `approach_v2`) |
| `Metrics/approach_abs_alpha` | ↓ |
| `Metrics/approach_see_ball` | stays high (> 0.9) |
| `Metrics/approach_speed_excess` | ↓ toward 0 |
| `Loss/value`, `Loss/kl_divergence` | no spikes; a spike together with `nan_state` > 0 means a sim blow-up |
| `Train/mean_episode_length` | about 900 (episodes are 1000 steps) |

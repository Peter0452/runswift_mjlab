# Walk

## Current best

- **Gold walk:** `logs/rsl_rl/k1_velocity_amp_symmetric_muon_wwcmu50_roughft/2026-09-21_20-34-24_stageA/model_9950.pt`
  (ONNX next to it, and `k1_policy_runner/amp_models/model_9950.onnx`).
  The user's reference for smoothness and stability on the robot. 73 % flat
  stance, first loaded step 0.77 × body weight (p90 0.91). In the runner sim
  it reaches 0.91 / 1.42 / 1.67 m/s at 1.0 / 1.5 / 2.0 m/s commands, no falls.
- `k1_velocity_amp_symmetric_muon_wwcmu30/2026-09-20_21-17-22/model_29999.pt`
  (`amp_models/model_29999.onnx`): 1.06 / 1.42 / 1.72 m/s at the same
  commands.
- It is the frozen walk skill in the two-level striker and the base of every
  kick and dribble task.

## Tasks

| Task | Use |
|---|---|
| `Mjlab-Velocity-{Flat,Rough}-Amp-DA-Muon-Booster-K1` | AMP walk with left/right mirroring and Muon; the prior for kick and dribble |
| `Mjlab-Velocity-Rough-Amp-DA-Muon-Booster-K1-KickHandoff` | walk that resets some envs from the end state of a frozen kick tracker, so it learns to take over after a kick |
| `Mjlab-Velocity-{Flat,Rough}-Booster-K1` | plain K1 velocity task, base config |
| `Mjlab-Velocity-{Flat,Rough}-Booster-K1-BaseWalk` | HTWK-gym Base_Walk rewards (47-D obs, 12 leg actions); produced the old curated walk checkpoints (on the archive branch) |
| `Mjlab-Velocity-HTWK*-Booster-K1-Nubots` (4) | HTWK/NUbots-compatible walk; `deploy.py` runs this family's ONNX on the robot |

## How the AMP walk is set up

- AMP-PPO: PPO plus a discriminator on motion clips (WW + CMU mix; dribble
  uses GVHMR clips too). Two critic heads (style, task); advantages are
  normalised per group and mixed 0.2 style / 0.8 task (`multi_critic_alphas`).
  Style weight 0.2: at 98 % discriminator accuracy the style advantage is
  saturated noise, and 0.5 of it washed out velocity tracking
  (`k1_amp/__init__.py`).
- DecAP ("walk spring"): a fading prior that pulls joint targets toward the
  reference clip, β = 0.99^(step/100) (`mdp/decap.py`, from APEX).
- Muon for weight matrices, Adam for the rest, sharing one learning rate via
  `match_rms_adamw` (`rl/muon.py`).

## Lessons specific to walking

From `docs/K1_WALK_TRAINING_NOTES.md` (plain PPO walk, 2026-08-14):

- High tracking reward does not mean walking: the policy matched filtered
  velocity by lurching without alternating swings. Require
  `feet_swing_mean ≳ 0.2` before calling a policy a walker.
- Removing the penalty-scale and clearance curricula (a `cfg.curriculum = {}`
  bug) made early training fall constantly.
- A grid command curriculum is needed; full-range commands from iteration 0
  made tracking peak then collapse.
- The HOME pose without foot-offset rewards splayed the hips; knees-bent pose
  plus `hip_roll_l2` fixed it.
- Pretrain on flat, then fine-tune on rough.
- Oscillating plots came from a too-high LR for scratch training and
  curriculum thresholds the episode length hovered around.

For dribble and kick, speed is limited by the learned gait (cadence × step),
not by the walk prior: the walk alone reaches ~1.4–1.5 m/s in the runner sim.

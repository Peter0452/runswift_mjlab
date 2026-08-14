# K1 Booster-Style Walk Training — Session Notes (2026-08-14)

Notes from debugging `Mjlab-Velocity-*-Booster-K1-FastSAC` training: reward
hacking, hip stretch-out, non-walking policies, and oscillating TensorBoard plots.

Task IDs still use the `FastSAC` suffix but the runner is **PPO**
(`booster_k1_ppo_runner_cfg`). Logs live under `logs/rsl_rl/k1_velocity/`.

---

## 1. Reference configs

| Source | Pose (legs) | Key anti-hack / gait mechanisms |
|--------|-------------|----------------------------------|
| **Booster T1** (`booster_gym/envs/T1.yaml`) | Hip −0.2, knee 0.4, ankle −0.25 | `feet_distance`, `feet_swing` 3.0, `tracking_sigma` 0.25, EMA filter 0.1 |
| **ParameterWalk** (`runswift-gym/.../ParameterWalk.yaml`) | Same HOME defaults | **`feet_offset_x/y` −12**, orientation −20 with pitch/roll cmds, plane terrain |
| **Successful K1 mjlab run** (Aug 7 `track_stance`, ~44k iters) | **KNEES_BENT** (knee **0.7**, hip −0.35) | Grid cmd curriculum, **`penalty_scale`** + **`clearance_terminate`** curriculums, **`hip_roll_l2` −1.0**, `standing_pose_l2`, fine-tuned from ~35k ckpt |

**Takeaway:** ParameterWalk HOME joints only work with ParameterWalk’s foot-offset
rewards. For Booster-style reward stacks on K1 rough terrain, the recipe that
actually worked was **deep crouch + hip roll penalty + soft-start curriculums**,
not HOME pose alone.

---

## 2. Tracking reward — formula is correct

All three codebases use the same Gaussian tracking shape on **body-frame,
EMA-filtered** velocity:

```text
r = exp(-(v_cmd - v_filtered)² / σ)     σ = 0.25, filter_weight = 0.1
```

mjlab implementation: `track_lin_vel_axis`, `track_ang_vel_z` in
`mdp/rewards.py`. Weights in FastSAC config have varied (2/2/0.25 vs Booster
1/1/0.5 vs Params 1/1/1.5); the **mechanism** matches Booster/Params.

---

## 3. Why the robot did not “walk” (despite rising tracking reward)

### 3.1 Reward hacking — high tracking, no gait

Observed on run `2026-08-14_16-13-38` (HOME pose + grid curriculum) @ ~1200 iters:

| Metric | Hacked run | Good run @ 44k |
|--------|------------|----------------|
| `Episode_Reward/tracking_lin_vel_x` | **0.66** | 0.57 |
| `Metrics/feet_swing_mean` | **0.09** | 0.24 |

The policy matched **filtered** velocity via whole-body lurch / hip stretch /
shuffle **without alternating foot swings**. `feet_swing` (weight 3.0) rewards
airborne feet in phase windows but does **not** require COM translation;
`tracking_*` is harder and can be partially satisfied without a true gait.

**Do not trust `tracking_lin_vel_x` alone.** Require `feet_swing_mean ≳ 0.2`
before calling a policy a walker.

### 3.2 Missing curriculums (bug)

`_apply_fast_sac_walk_rewards()` had been doing `cfg.curriculum = {}`, which
**removed** the Aug 7 **`penalty_scale`** and **`clearance_terminate`**
curriculums. Without them:

- Full penalty stack from iter 0 → frequent falls, no time to learn stepping.
- Fixed `root_height` kill at 0.35 → harsh early termination on rough terrain.

**Fix (committed):** `_apply_fast_sac_curriculum()` restores both; clearance
starts at **0.30** and ramps to **0.35**.

### 3.3 Grid command curriculum required

Disabling grid curriculum and sampling full ±1.5 m/s from iter 0 caused tracking
to **peak then collapse** (e.g. 0.38 @ 1.6k → 0.06 @ 2.3k). Aug 7 and stable
training both use **`grid_curriculum.enabled = true`**.

### 3.4 HOME pose → hip stretch-out

With HOME (knee 0.4, spawn z 0.58) and no `feet_offset` rewards, the policy
**splayed hips** to farm `feet_swing` in place. Reverting to **KNEES_BENT** and
adding **`hip_roll_l2` −1.0** (always on) + **`standing_pose_l2`** (still only)
fixed stretch-out visually.

### 3.5 Too few iterations / wrong checkpoint for play

- Aug 7 useful walk: **~44k** iters (and resumed from prior ckpt).
- Early ckpts (1–2k) are not walkers even if tracking looks “okay”.
- **Play:** enable viser joystick, set vx ≈ 0.3–0.5; default cmd is 0.
- **Train/deploy parity:** checkpoint pose must match `KNEES_BENT` /
  `walk_policy_v4.py` `DEFAULT_JOINT_POS` (knee 0.70, hip −0.35).

### 3.6 Rough-before-gait

Rough terrain + push/kick DR while gait is immature → short episodes and
`root_height` / `fell_over` kills. **Flat pretrain first**, then rough FT, is
the safer path (`Mjlab-Velocity-Flat-Booster-K1-FastSAC`).

---

## 4. Oscillating TensorBoard plots

Compared run `2026-08-14_17-02-47` (~1.4k, rough) vs stable Aug 7 @ 44k:

| Metric | Rough 17-02-47 std | Aug 7 std |
|--------|-------------------|-----------|
| `Train/mean_reward` | **9.9** | 2.1 |
| `Episode_Reward/tracking_lin_vel_x` | **0.22** | 0.05 |

**Causes:**

1. **LR too high for scratch:** `1e-5` vs Aug 7 **`5e-6`** (Aug 7 also **FT
   from 35k**, not scratch — inherently smoother curves).
2. **Curriculum ping-pong:** penalty/clearance thresholds **80 / 200** steps —
   when mean episode length hovered ~150–300, penalties flipped every few iters
   → sine-wave plots.
3. **Policy collapse/recover cycles** on rough without soft-start penalties.
4. **Grid `update_rate=0.1`** — command difficulty jumps.

**Stabilization (committed):**

- `learning_rate = 5e-6`
- Curriculum thresholds **150 / 450**, slower `degree`, EMA window **2000** iters
- Grid `update_rate = 0.05`
- Use TensorBoard smoothing **50–100** for raw per-iter lines early on

---

## 5. Current FastSAC K1 config summary (post-fix)

**Pose:** `KNEES_BENT_KEYFRAME` — spawn z 0.53, height target **0.50**.

**Rewards (Booster-base + K1 tweaks):** survival 0.25; tracking lin x/y **2.0**,
ang **1.0**; `feet_swing` **3.0**; `hip_roll_l2` **−1.0**; `standing_pose_l2`
**−1.0** (still); `only_positive_rewards` true; `tracking_sigma=0.25`.

**Curriculums:**

- Grid command (enabled, `update_rate=0.05`)
- `penalty_scale` 0.5 → 1.0
- `clearance_terminate` 0.30 → 0.35

**Commands:** resample 8–12 s; gait freq in twist dim 4; `rel_standing_envs=0.25`;
grid on → `rel_forward_envs` ignored.

**RL:** PPO, `num_steps_per_env=24`, `lr=5e-6`, adaptive KL, init std ≈ 0.135.

**Deploy (`walk_policy_v4.py`):** knees-bent `DEFAULT_JOINT_POS`; ParameterWalk
PD Hip/Knee **100**, Ankle **50**, damping 2/2/1.

---

## 6. Runs log (2026-08-14)

| Run | Config highlights | Outcome @ ~1.3–1.5k |
|-----|-------------------|---------------------|
| `14-52-38` / `16-13-38` | HOME pose, no penalty curriculum early | Tracking rose then collapsed; hip stretch |
| `16-13-38` + grid | HOME @ 1200 | track_x **0.66**, swing **0.09** — hack, not walk |
| `17-02-47` | KNEES_BENT + hip_roll, no penalty curriculum | High plot variance, weak gait |
| `18-00-08` | Flat + penalty/clearance curriculum | Short run, aborted for LR/curriculum tune |
| **`18-01-41`** | Flat + full fix (LR 5e-6, wide curriculum band) | @ ~1460: track_x **0.76**, swing **0.22** — better, still early |

**Recommended training command (flat pretrain):**

```bash
MUJOCO_GL=egl uv run train Mjlab-Velocity-Flat-Booster-K1-FastSAC \
  --env.scene.num-envs 4096 --gpu-ids "[0]"
```

**Play (after ≥10k iters, matching ckpt):**

```bash
uv run play Mjlab-Velocity-Flat-Booster-K1-FastSAC \
  --checkpoint-file logs/rsl_rl/k1_velocity/<run>/model_XXXX.pt \
  --num-envs 1 --viewer viser
```

Enable joystick → set vx > 0.

**Rough FT:** resume from flat ckpt on
`Mjlab-Velocity-Rough-Booster-K1-FastSAC` once `feet_swing_mean ≳ 0.2`.

---

## 7. Metrics checklist

| Metric | Healthy direction | Red flag |
|--------|-------------------|----------|
| `Metrics/feet_swing_mean` | → **0.2–0.3+** | < 0.15 with high tracking |
| `Episode_Reward/tracking_lin_vel_x` | → 0.4–0.6+ (steady) | Spikes then crashes |
| `Train/mean_episode_length` | → 600+ / 1500 | Stuck < 200 on flat |
| `Metrics/twist/error_vel_xy` | ↓ | Flat high while tracking “good” |
| `Curriculum/penalty_scale/scale` | Slow → 1.0 | Fast oscillation 0.5↔1.0 |
| `Episode_Termination/root_height` | ↓ over time | Dominates batch kills |

---

## 8. Key files touched

- `src/mjlab/tasks/velocity/config/k1/env_cfgs.py` — rewards, curriculums, grid
- `src/mjlab/tasks/velocity/config/k1/rl_cfg.py` — PPO LR
- `src/mjlab/asset_zoo/robots/booster_k1/k1_constants.py` — `KNEES_BENT` init
- `src/mjlab/tasks/velocity/mdp/rewards.py` — Booster tracking / feet_swing
- `k1_policy_runner/.../walk_policy_v4.py` — deploy pose + PD

---

*Last updated: 2026-08-14 — flat pretrain run `2026-08-14_18-01-41` in progress.*

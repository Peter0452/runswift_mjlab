# Kick ↔ Walk — living problem context

> **Purpose:** Keep the *problem* stable across prompts. Every change, reward tweak,
> and train run must be judged against this file — not against the latest chat ask alone.
>
> **Update rule:** When the goal, stage, north stars, or “what failed” changes, edit
> this file in the same turn. Do not invent a new objective in chat without updating
> here first.

---

## 1. Problem we are solving

Train a **Near kick** policy for Booster K1 that can eventually hand off to a
**frozen Walk** policy (2 deploy models: Walk + Kick).

**Success (product):**
- Robot approaches / starts near ball, plants, **strikes** the ball toward goal with
  useful power, then **settles upright** in a pose Walk can take over from.
- Deploy is a high-level FSM (Walk ↔ Kick), not a blended policy — but training must
  make the handoff *learnable* (overlapping state, stand settle).

**Explicitly out of scope until Stage 0 is green:**
- Walk↔Kick residual / transition network
- Deploy FSM polish / α-blend at runtime
- Approach-as-third-ONNX
- “Make mean reward go up”

---

## 2. Stages (do not skip)

| Stage | Goal | Exit criteria |
|-------|------|----------------|
| **0 — Reliable kick** | Strike + settle | North stars (§3) hold for a sustained run; no soft-kick / loiter collapse |
| **1 — Transition (frozen skills)** | Glue Walk→Kick→Walk | Smooth handoff with Walk + Kick frozen |
| **2 — Polish Kick + transition** | Kick adapts to handoff states | Walk stays frozen |
| **3 — Optional joint FT** | Only if 2 plateaus | Still preserve strike power |

**Current stage: 1 (Recipe C)** — frozen Walk `9950` enter+exit around Kick PPO
(`--frozen-walk-handoff`). Recipe 1 synthetic mix remains available without the flag.

---

## 3. North-star metrics (not mean reward)

Primary (must move / hold):

| Metric | Intent | Healthy signal (rough) |
|--------|--------|-------------------------|
| `Metrics/kick_ball_speed` | Ball actually launched | Rising toward band; not stuck ~0.02 |
| `Metrics/strong_kick_detected` | Real power (≥ ~5 m/s) | > 0 and not collapsing to 0 |
| `Metrics/ball_vel_toward_goal_raw` | Directional power | Tracks with kick speed |
| Post-kick upright / stance (gated) | Settle for Walk | High **after** real kicks, not instead of them |
| `Metrics/walk_exit_ok` / `walk_exit_fall` | Kick→Walk hold (Recipe C) | `ok` rising; `fall` not dominant |

Secondary (context only — can rise while kick dies):

- `Train/mean_reward`, episode length
- AMP style active, plant latch, contact bridge, waypoint terms

**Abort rule:** If primary metrics are flat/dead for a long stretch while reward↑,
stop the run. Do not “let reward climb.”

---

## 4. Operating principles (anti-greedy)

1. **Problem-first** — Interpret every prompt inside §1–§2. If a request conflicts,
   push back and update this file; don’t silently retarget.
2. **One intentional change per run** — Prefer one reward/termination/spawn knob.
   Multi-edit patches are how we lost the kick basin.
3. **Preserve a kicking checkpoint** — Warm-start from a known-good *kicking* ckpt
   when changing rewards. Never “fix power” starting from a soft/loiter policy
   unless the change is explicitly about recovery discovery.
4. **Gates > deletions** — Prefer scaling/gating farm terms over removing the only
   dense cues that create contact.
5. **Log failures here** — Every failed hypothesis goes in §6 so we don’t repeat it.

---

## 5. Known-good / reference checkpoints

| Run | Ckpt | Notes |
|-----|------|-------|
| `2026-09-23_10-08-54_near_amp_v1` | `model_600`–`model_800` | Peak kick (`kick_ball_speed` ~1.5, `strong_kick` ~0.4) — **best Stage-0 resume** |
| `2026-09-23_10-08-54_near_amp_v1` | `model_1800` | Robust stand, weak kick (`v` ~0.55, strong=0) — good settle, **bad power base** |
| `2026-09-23_12-39-57_near_amp_band_exp_v1` | `model_10700` | Loiter / no launch — **do not** use as kick resume |

Update this table when a new peak appears.

---

## 6. Hypothesis log (iterative)

Newest first. Keep entries short: change → result → lesson.

### 2026-09-23 — H1.1 post_kick_stance weight (in code)
- **Tried:** One knob on H1: `post_kick_stance` 1.5→**2.5** (keep upright gate 4.0 / w=5).
  Also `ball_velocity_toward_goal` 4→**5**. Resume from H1 best when training.
- **Result:** _pending_
- **Lesson:** _pending_

### 2026-09-23 — H1 upright gate
- **Tried:** Restore model_1800 reward stack; only change `post_kick_upright`
  `min_kick_speed` 1.2→4.0 and weight 12→5. Resume `model_600`.
- **Result:** Power held (~1.6 m/s, strong~0.6–0.7); upright farm fixed; plant foot
  after kick looked dragged/tilted vs model_1800 (settle under-weighted).
- **Lesson:** Gate upright for power; boost stance/flat separately for handoff pose.

### 2026-09-23 — Band + farm cuts from soft policy
- **Tried:** Hard then exp speed band [4–10] / [0.5–10]; cut bridge + latch bonus;
  strike↑; `near_ball_no_kick` 5s→1.5s; resume from soft / band ckpts.
- **Result:** Reward/length↑ or capped; `kick_ball_speed` ~0.02; strong=0; AMP always on.
- **Lesson:** Power terms that only pay *after* launch cannot create launch. Cutting
  dense swing cues + starting from non-kicking weights = loiter basin. Timeout
  stops farm but does not teach strike.

### 2026-09-23 — Soft-kick / upright farm on `near_amp_v1`
- **Tried:** Post-kick upright heavy with low speed gate (~1.2 m/s).
- **Result:** Peak kick ~600 iters, then collapse; upright reward stayed high.
- **Lesson:** Settle must be gated/scaled by real kick strength or it becomes the task.

---

## 7. Current config snapshot (facts, not goals)

Update when Near defaults change.

- Task: `Mjlab-Kick-Near-Amp-Booster-K1`
- Spawn: radius `(0.35, 0.55)` m, approach wedge `120°`
- **H1 + H1.1 in code:** `model_1800` landscape; upright gate 4.0 / w=5; `post_kick_stance` **w=2.5**
- **Plant box (relaxed):** support foot **0.20 m** behind + **0.20 m** beside (±0.14 tol); was 0.14/0.175±0.10
- `ball_velocity_toward_goal`: linear `max_reward=6`, weight **5** (was 4)
- `post_kick_upright`: weight **5** (was 12), `min_kick_speed` **4.0** (was 1.2), window 1.5s
- `post_kick_stance`: weight **2.5** (was 1.5)
- `kicking_foot_strike`: weight **5**
- `kick_contact_bridge`: weight **3** (restored)
- `plant_latch_bonus`: weight **20** (restored)
- `near_ball_no_kick`: `max_near_time_s=5.0` (restored)
- AMP: style on until `kick_detected`, then off

---

## 8. Suggestions from post-1800 experiments (ranked)

What failed after `model_1800`: band-only / exp-band, resume from soft weights,
cutting bridge+latch, 1.5s no-kick timeout. None recovered `kick_ball_speed`.

### Do / don’t

| | |
|--|--|
| **Do** | Resume from a **kicking** ckpt (`near_amp_v1` **model_600–800**), not 1800/band/10700 |
| **Do** | Keep a **dense pre-launch** path (strike and/or bridge) |
| **Do** | Fix upright so it cannot outpay strike |
| **Do** | One knob per run; abort on flat `kick_ball_speed` |
| **Don’t** | Band/exp as the *only* ball-speed signal from a soft policy |
| **Don’t** | Cut bridge + latch + tighten timeout in one go |
| **Don’t** | Judge success by mean reward / ep length |

### Hypotheses

**H1 — DONE** — power held; settle feet weaker than 1800.  
**H1.1 — IN CODE** — `post_kick_stance` 1.5→2.5. Resume H1 `model_1500`/`2600`.

**A — DONE (weak alone)** — `swing_plant_lateral_gap` w=−2.0, `gap_max=0.24`.
Penalty ≈0 in train: plant lateral 0.20 already under leash; stretch was
mostly sagittal reach across a wide plant.

**B — DONE (weak alone)** — Plant lateral target 0.20→0.13. Soft latch +
`lateral_tol=0.14` swallowed it; measured gap_lat/Hip_Yaw unchanged, power −0.65.

**B2 — DONE (too tight)** — Hard plant latch + `lateral_tol=0.06`: power
collapsed (ball-vel ~2 vs ~4.7).

**S0/S1 — ABORTED** — CoM latch + 47-term stack: ball-vel ~1.5, latch starved.

**LEAN — DONE** — 17 terms; CoM lure; plant latch tol 0.08; power recovering (~3.3).

**S2 — DONE** — Compact strike gate on `kicking_foot_strike` +
`ball_velocity_toward_goal`: payday only if `gap_lat ≤ 0.22` ∧ `|Hip_Yaw| ≤ 25°`.

**S4 — IN CODE (active)** — Stronger post-kick recovery on `post_kick_stance`:
swing beside plant (lateral ≈0.19 ∧ sagittal retract) × CoM over feet midpoint
(BoS) × flat soles. Lean weight **2→4**. Does not touch pre-strike payday.

**H2** — Linear discovery + light band bonus (only if H1 holds power).  
**H3** — Fine-tune from 1800 settle (only after H1 power OK).  
**H4** — AMP near-ball mask (later).

Later if S4 holds: ankle (S3). If power dies → drop stance weight to 3 or widen
`sagittal_sigma` / `bos_sigma` to 0.12.

### Active run

- **Change:** Stage 4 post-kick BoS (shape + w=4)
- **Resume:** `2026-09-26_12-13-43_near_amp_lean_compact_v1` / `model_400`
- **Keep:** lean 17 terms; Stage 2 compact gate; `--frozen-walk-handoff True`
- **Watch:** `Metrics/post_kick_feet_sagittal`, `post_kick_bos_dist`, ball-vel /
  `strong_kick` (must not collapse)
- **Abort:** ball-vel ≲ 1.5 while stance↑ → loosen sigmas or drop weight to 3

```bash
MUJOCO_GL=egl uv run train Mjlab-Kick-Near-Amp-Booster-K1 \
  --env.scene.num-envs 4096 \
  --frozen-walk-handoff True \
  --agent.experiment-name k1_kick_approach \
  --agent.run-name near_amp_lean_postkick_bos_v1 \
  --agent.resume True --agent.warm-start True \
  --agent.load-run 2026-09-26_12-13-43_near_amp_lean_compact_v1 \
  --agent.load-checkpoint model_400.pt
```

---

## 9. Related docs

- [`REWARDS_model_1800.md`](REWARDS_model_1800.md) — full math + explanation for every reward term in `near_amp_v1` / `model_1800` (saved `env.yaml`).

---

## 10. Stage-1 play — Setup B (Walk→Kick→Walk FSM)

Hard switches in the **Kick Near-Amp env**:

```text
APPROACH (Walk @ ~1.5 m)
  → hard stop d≤0.40 m + face + upright + slow + stand hold 0.3 s
  → KICK → settle 1 s → EXIT (Walk)
```

**Option A enter gate (defaults):**
- hard stop / band: `d_ball ≤ 0.40` m
- `|bearing| ≤ 0.40` rad (~23°)
- trunk tilt ≤ 0.35 rad (~20°): `g_z ≤ -cos(tilt)`
- horizontal speed ≤ 0.55 m/s
- gates held while standing **≥ 0.30 s**

```bash
uv run --no-sync python -m mjlab.scripts.play_kick_to_walk --viewer viser
```

North stars: enter→exit completion rate (was ~21% distance-only); Kick power still fires.

---

## 10b. Stage 1 — Recipe 1 (handoff spawn mix)

Train Kick only (Walk `9950` frozen). Resume kicking Near-Amp ckpt. **Keep H1/H1.1 rewards.**

| Fraction | Init |
|---------:|------|
| 50% | Near spawn as today `(0.35, 0.55)` m |
| 50% | **Handoff init** (Walk enter-like) |

**Handoff init** (`reset_robot_around_ball_facing` + twist teacher):
- `d ∈ [0.30, 0.55]` m (approach side)
- `|bearing| ≤ 0.40` rad, tilt ≤ ~0.35 rad, `‖v_xy‖ ≤ 0.55`
- Twist stand `(0,0,0)` for first 0.3–0.5 s, then Near teacher
- Pose: Near/default joints (v1)
- Play / Setup B: `handoff_fraction=0` (no mix)

**Wired in:** `make_near_kick_env_cfg` sets `handoff_fraction=0.5`; metric
`Metrics/twist_handoff_stand`.

**Eval:** play FSM Option A — enter→exit rate + `kick_ball_speed` / `strong_kick` vs resume baseline.

## 10c. Stage 1 — Recipe C (frozen Walk enter + exit)

Train Kick with Walk `9950` frozen in the loop (`--frozen-walk-handoff True`).

```text
APPROACH (Walk @ ~1.5 m, Option A gates)
  → KICK (student PPO; teacher on)
  → EXIT when settle ∧ ball≥0.5 m
      Walk hold T∈[0.5,1] s → +2 if upright / −5 if fall → done
```

- Spawn `(1.4, 1.6)` m, `handoff_fraction=0`
- Walk-phase rewards zeroed (Kick buffer still gets student actions; advantage≈0)
- Code: `mjlab/tasks/kick/rl/frozen_walk_handoff.py`, helpers in `mdp/walk_handoff.py`

```bash
MUJOCO_GL=egl uv run train Mjlab-Kick-Near-Amp-Booster-K1 \
  --env.scene.num-envs 4096 \
  --frozen-walk-handoff True \
  --agent.experiment-name k1_kick_approach \
  --agent.run-name near_amp_recipeC_frozen_walk_v1 \
  --agent.resume True --agent.warm-start True \
  --agent.load-run 2026-09-24_22-20-55_near_amp_recipe1_handoff_v1 \
  --agent.load-checkpoint model_500.pt
```

**Abort:** power collapse while farming exit bonus / soft-kick to avoid handoff.

## 11. Changelog (this document)

| Date | Edit |
|------|------|
| 2026-09-23 | Initial problem context from Near-Amp / band / loiter postmortem |
| 2026-09-23 | Link reward breakdown for model_1800 |
| 2026-09-23 | §8 suggestions from post-1800 experiments (H1–H4) |
| 2026-09-23 | H1 implemented: restore 1800 rewards + upright gate 4.0 / w=5 |
| 2026-09-23 | H1.1: `post_kick_stance` 1.5→2.5 |
| 2026-09-23 | Setup B play FSM (`play-kick-to-walk`) |
| 2026-09-24 | Setup B: Walk→Kick→Walk from ~1.5 m spawn |
| 2026-09-24 | Option A enter gate (face/upright/speed + 0.3s stand) |
| 2026-09-24 | Recipe 1 handoff spawn `d ∈ [0.30, 0.55]` |
| 2026-09-24 | Recipe 1 wired into Near train cfg (50/50 mix) |
| 2026-09-24 | Recipe C: frozen Walk enter+exit train wrapper |
| 2026-09-24 | Soft-brake approach below 1 m (~50% cruise by 0.45 m) |
| 2026-09-24 | Relax Near plant box 0.14/0.175→0.20/0.20 (±0.14) |
| 2026-09-25 | Recipe A: `swing_plant_lateral_gap` (latch, pre-kick; w=−2.0, gap_max=0.24) |
| 2026-09-25 | Recipe B: plant lateral_target 0.20→0.13 (keep A; sagittal 0.20) |
| 2026-09-25 | Option 2: `require_support_plant_for_latch=True`, lateral_tol 0.14→0.06 |
| 2026-09-26 | Stage 0+1: phase_audit; com_over_plant + CoM latch; lateral_tol 0.08 |
| 2026-09-26 | Lean Near: 47→17 principle terms; CoM lure only (no CoM latch) |
| 2026-09-26 | Stage 2: compact gate on strike+ball_vel (gap≤0.22, |Hip_Yaw|≤25°) |
| 2026-09-26 | Stage 4: post_kick_stance sag retract + BoS; lean w 2→4 |




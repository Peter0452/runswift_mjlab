# K1 kick — stage 3 (kick loop) notes

Task: `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`
Logs: `logs/rsl_rl/k1_kick_stage3_amp/`
Code: `src/mjlab/tasks/velocity/mdp/kick_loop.py`,
`booster_k1_kick_stage3_env_cfg` in
`src/mjlab/tasks/velocity/config/k1_amp/env_cfgs.py`
Eval: `scripts/tools/eval_kick_loop.py`
Monitoring: `scripts/tools/reward_budget.py` (reward budget and failure flags),
`scripts/tools/watch_run.py` (exits when a run reaches an iteration or breaks)

Stage 2 (approach) is described in `K1_KICK_APPROACH_NOTES.md`.

## Status (overnight 2026-10-02)

**Recommended checkpoint:**
`logs/rsl_rl/k1_kick_stage3_amp/2026-10-02_08-25-15_stage3_v17/model_1800.pt`.
It does a real kick (planted support, fast leg swing) with an upright trunk.
1024 episodes × 30 s each, ball randomization, vision noise and random pushes
on, two seeds:

| | Kicks / ep | Within 20° | Goals / ep | Ball speed | Kick quality | Body speed at kick | Trunk tilt mean / p90 | Fell after first 2 s | Fell ≤ 2 s after a kick |
|---|---|---|---|---|---|---|---|---|---|
| **v17 `model_1800`** | 3.6 | **93–94%** | 2.09 | 3.4 m/s | **0.76–0.77** | 0.16 m/s | 5.1–5.2° / 8.5° | **0.1–0.2%** | **0.1%** |
| v17 `model_1500` | 4.0 | 91% | 2.21 | 3.35 m/s | 0.73 | 0.17 m/s | 4.3° / 8.6° | 0.4% | 0.2% |
| **v17 `model_900`** | 3.3 | **89%** | **1.85–1.88** | **3.6 m/s** | **0.78** | **0.15 m/s** | **4.2° / 8.4°** | **0.1–0.2%** | **0.0–0.1%** |
| v17 `model_500` | 3.5 | 78% | 1.67 | 3.45 m/s | 0.67–0.68 | 0.18 m/s | 4.1° / 9.2° | 0.0% | 0.0% |
| v16 `model_1700` (superseded) | 7.5 | 71% | 2.55 | 2.4 m/s | 0.01 | 0.92 m/s | 14.0° / 21.3° | 1.6–1.8% | 1.3–1.4% |

v13/v16 aim and stay up, but they run into the ball while leaning (see
"v13/v16 do not kick"). v17 kicks less often but every kick is a deliberate
planted strike.

```bash
uv run play Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1 \
  --checkpoint-file logs/rsl_rl/k1_kick_stage3_amp/2026-10-02_08-25-15_stage3_v17/model_1800.pt \
  --num-envs 1 --viewer viser
uv run python scripts/tools/eval_kick_loop.py --checkpoint <ckpt>
uv run python scripts/tools/reward_budget.py logs/rsl_rl/k1_kick_stage3_amp/<run>
```

How we got here (details in the run log below): v1 hovered near the ball, v2
fell on purpose, v3 sprayed kicks; v4 was the first stable kicker; v5 added
ball memory and a sharper aim reward; v6 capped action noise; v7 trained with
ball randomization and vision noise; v8 recovers before chasing; v9–v12b
found that every continuation drifts toward riskier kicks; v13 lengthened the
discount horizon (γ 0.995), which gave the best early checkpoints; v14
showed the AMP discriminator only notices the drift; v15 made the aim reward
sharp (accuracy held) and v16 raised the joint-limit penalty (joint use
contained).

**Key finding:** with these rewards, continued training trades a little
safety for productivity (more kicks and goals, more falls), whatever the step
size, style weight or fall penalty; pushes explain only a small part.
Checkpoint selection by evaluation (`eval_kick_loop.py`) is what works: the
good window is roughly 50–150 iterations after a change.

Still open: matching the ball model to the real ball (size, mass, bounce,
rolling); controlled kick speed for the range bins; falls from reset poses in
the first 2 s (a training-setup artifact).

## Goal

One policy that approaches the ball, lines up, kicks it toward a target,
stays stable, finds the ball again, and repeats. A demonstrable, reliable
kick comes first; exact ball speed comes later.

## Episode

```
spawn (ball in view, 1–4 m) → approach → line up → kick → recover
      ↑                                                   ↓
      └──── find the ball, re-approach ←── ball rolls toward the target
kicked ball passes the target → goal, new target 1–10 m from the ball
```

- 30 s episodes on a **flat plane**. Stage 2's rough and wave tiles made the
  ball roll unpredictably.
- Targets sit 1–10 m from the ball in three bins, short **1–4 m**, medium
  **4–8 m** and long **8–10 m**. A bin is picked uniformly, then a distance
  inside it. The `kick_range` one-hot (slots 80–82) uses the same edges and is
  computed from the **last seen** ball, so it follows a ball that has moved.
- A goal is a kicked ball passing within 25% of the target distance (0.5–1.5
  m) of the target. The next target then goes in a random direction, so every
  kick starts from a fresh approach. A kicked ball that comes to rest more than
  10 m from the target also gets a new target, with no bonus.
- The observation layout is unchanged from stage 2. The warm start from stage
  2 (`approach_v3_heading/model_8550.pt`) needs no `--reset-obs-dims`; only the
  optimizer is fresh.

## Events

Detected at the end of a step and paid by the next step's rewards, so each
pays once (`classify_touch`):

- **Kick:** foot–ball contact (this or the previous step) that launches the
  ball to ≥ 1.0 m/s with a jump of ≥ 0.8 m/s, and is not within 0.5 s of the
  previous kick.
- **Double touch:** a new foot contact within 0.5 s after a kick (a carry).
- **Push:** foot contact that does not launch the ball. This is dribbling.

## Rewards

Event rewards are scaled by dt like every term, so weight 300 means 6 per
perfect kick.

| Suggested reward | Term | Weight | What it pays |
|---|---|---|---|
| Ball Vision | `ball_vision` (`approach_view`) | 1.0 | ball inside the head-camera cone |
| Kick Direction Alignment | `kick_dir_alignment` | 50 | step change of −w(d)·\|body yaw error\|, w ramping 0 → 1 from 2.0 m to 0.5 m |
| Walk Speed | `walk_speed` | 2.0 | signed speed toward the ball over the vx limit, outside 1.5 m, off for 2 s after a kick (v8) |
| Walk Speed Limit | `walk_speed_limit` | −10 | excess of ~0.3 s smoothed \|vx\|, \|vy\|, \|wz\| over the limits; off for 0.5 s after a kick (1 s before v8) |
| Kick Direction | `kick_direction` | 300 | per kick: cosine of ball velocity vs target direction, floored at 0 |
| Kick Vel | `kick_vel` | 300 | per kick: min(speed / 3 m/s, 1) |
| Kick Vel Accurate | `kick_vel_accurate` | 100 | per kick: Gaussian match (σ = 25%) to the speed that rolls the ball to the target |
| Ball Avoidance | `ball_avoidance` | −5 | per step of non-foot body contact with the ball, or a foot push |
| Single Feet Avoidance | `single_feet_avoidance` | −5 | seconds beyond 0.8 s that one foot stays up while the other is down |

Also:

| Term | Weight | Why |
|---|---|---|
| `kick_goal` | 500 | per goal |
| `kick_lined_up` | 100 | once per approach, first step lined up; no stop needed |
| `kick_near_ball_time` | −1.5 | each step within 1.5 m with a kick pending, so it kicks quickly |
| `kick_double_touch` | −200 | per double touch |
| `post_kick_stability` | 4.0 (2.0 before v8) | upright and calm trunk for 2 s after each kick |
| `approach_align`, `approach_close`, `approach_bad_contact` | 80, 100, −20 | unchanged from stage 2 |

Switched off from stage 2: `approach_stand` (paying to stand still at the
ball is the opposite of kicking), the gated `approach_heading` (it paid more
for entering misaligned; see the stage 2 notes), and the instantaneous
`approach_speed_limit`. The hidden gait flag stays in "walking", so the gait
terms do not treat a kick as a bad standing pose.

**AMP style:** a walk-only discriminator cannot judge a kick. The command sets
`env.amp_style_gate`, and the AMP runner (`amp_support.py`) uses it instead of
the old proximity gate. Style is **off** within 1.5 m with a kick pending and
for 1 s after each kick, and **on** everywhere else.

## Ball physics

Approach ball: 0.1 kg, radius 0.08 m. On the plane it rolls
d ≈ v² / (2 · 0.95 m/s²): 2.2 m at 2 m/s, 8.4 m at 4 m/s, 18.9 m at 6 m/s.
Rolling a ball d metres needs v ≈ 1.38·√d (1.4 m/s for 1 m, 4.4 m/s for
10 m). `KickLoopCommandCfg.ball_roll_decel` holds 0.95. **Match it and the ball
model to the real ball before tuning kick speed.**

## First results

100-iteration smoke run (`2026-10-01_23-51-59_smoke_stage3/model_99.pt`), 512
episodes × 30 s, measured with `eval_kick_loop.py`:

| Metric | Value |
|---|---|
| Kicks per episode | 5.7 (92% of episodes kick at least once) |
| Kicks within 20° of the target | 33% |
| Mean kick ball speed | 2.45 m/s |
| Time within 1.5 m before kicking | 1.6 s |
| First kick | median 4.0 s |
| Goals per episode | 1.1 |
| Fell during the episode | 9% (2% within 2 s of a kick) |
| Ball in view 1–3 s after kicks | 98% |

Full run: `2026-10-01_23-57-30_stage3_v1`, warm start from stage 2
`model_8550.pt`, learning rate 1e-4.

## Issue — stage3_v1 learned not to kick

**Run:** `2026-10-01_23-57-30_stage3_v1`. It kicked about 2.2 times per
episode around iterations 60–120, dropped to zero by about iteration 400, and
stayed there. Falls dropped at the same time (`illegal_contact` 1.3 → 0.2).
By iteration 1000 the policy circled to the correct side of the ball
(position error 0.18 rad), then **hovered about 1.7 m away, just outside the
1.5 m near zone**.

**Causes:**

1. `kick_near_ball_time` cost 1.5/s only within 1.5 m, so it fenced the zone:
   waiting at 1.7 m was free.
2. The AMP style gate also switched style off within 1.5 m, so stepping in
   lost about 1/s of style reward: a second fence.
3. `walk_speed` paid for speed toward the ball but was clamped at 0 for
   moving away, so shuffling back and forth outside 1.5 m farmed it (it rose
   from 0.29 to 0.65 while kicks went to zero).
4. Early kicks were clumsy and often ended in falls. A fall forfeits about
   2.5/s of per-step rewards (upright, ball vision, style) for the rest of the
   episode, while a kick paid about 14 once. Not kicking was the safer bet.

**Fixes:**

- `walk_speed` is signed (−1 to 1), so stepping back costs what stepping in
  paid.
- `kick_near_ball_time` is removed. `kick_time_cost` (−1.0) applies
  everywhere except the second after a kick: urgency without a fence. It stays
  below the per-step "alive" rewards, so ending the episode never pays.
- When the task owns the style gate, gated-off envs get the **mean style
  reward** of the others instead of none (`amp_support.py`). The gate keeps the
  walk discriminator from judging the kick without creating a reward drop.
- Kick rewards are tripled: `kick_direction` and `kick_vel` 900 (18 each per
  perfect kick), `kick_vel_accurate` 300, `kick_goal` 1500, `kick_lined_up`
  200.
- New explicit `fall` penalty (`is_terminated`, −500 → −10), so the cost of a
  fall is set directly rather than only through the rewards it forfeits.
  Sim blow-ups are not counted, because the blow-up guard zeroes that step.

## Issue — stage3_v2 learned to fall at once

**Run:** `2026-10-02_00-23-06_stage3_v2` (v1's fixes, warm start from
`stage3_v1/model_100.pt`). It kicked about 3 times per episode for the first
100 iterations. Then episodes shrank to about 13 steps (`illegal_contact`
about 300 per log) and action std grew from 1.0 to 1.7. KL stayed normal and
there were no sim blow-ups.

**Cause:** the per-step reward of staying up was net negative: −3.4/s
(iterations 20–100), −7.5/s (100–200), −9.7/s (150–250). With a 30 s episode,
staying up cost far more than the −10 fall penalty, so falling immediately
was the best policy. The drivers were:

- `action_rate_l2`, about −76 to −117 per episode. It scales with action
  noise squared, and the v1 checkpoint's std (0.66, rising to 1.0) was well
  above stage 2's 0.43.
- The new global `kick_time_cost` (−1/s).

v1 failed because staying up was worth too much next to kicking. v2
over-corrected until staying up cost reward.

**Rule:** keep the per-step reward of staying up small but **positive**
(about +1/s), make a kick worth clearly more than a fall costs, and check the
budget from `Episode_Reward/*` × 30 ÷ episode length before a long run.

**Fixes (v3):** `kick_time_cost` removed; `action_rate_l2` −0.1 → −0.03 in
stage 3; warm start from stage 2 `model_8550.pt` (std 0.43) again; v2's other
fixes kept. Rough budget: about +1.3/s while up, a kick about +40, and a
30%-risk kick still nets about +31.

## Issue — stage3_v3 sprayed kicks in any direction

**Run:** `2026-10-02_01-04-31_stage3_v3` (v2's lesson applied, warm start
from stage 2). It kicked about 4.7 times per episode, but the per-second
reward of staying up slid from +2.2 to −2.0/s within 200 iterations. Action
std rose from 0.48 to 1.47, and kick direction error grew from 0.33 to 1.17
rad.

**Cause:** `kick_vel` paid ball speed in **any** direction, so wild, noisy
kicks paid. Its share went from +14 to +64 per episode, while the growing
noise fed `action_rate_l2` (−11 → −60) and `walk_speed_limit` (−2 → −28).
Stopped at iteration 214, before it could collapse like v2.

**Fixes (v4):** `kick_vel` and `kick_vel_accurate` are multiplied by the aim,
cos⁺² (a 67° miss keeps 15%). Stage 3 `entropy_coef` 0.01 → 0.005.

## stage3_v4 — first stable kicker

**Run:** `2026-10-02_01-10-45_stage3_v4`, warm start from stage 2. By
iterations 360–435: 5.7 kicks and 1.0 goal per episode, falls about 0.3,
ball in view 0.83, episodes 28 of 30 s. The ball-in-view rate dipped to 0.2
around iterations 150–250 (the ball was kicked out of sight and lost), then
recovered.

Open problems that v5 addresses:

- **Aim stalled at about 0.85 rad (~49°).** The plain cosine paid 64% for a
  50° miss.
- **No ball memory.** A ball kicked out of view became zeros.
- Action std still crept up (0.47 → 0.81), much more slowly than in v3.

## stage3_v5 — ball memory and sharp aim

- **Ball memory** (`KickLoopCommandCfg.ball_memory = True`): out of view, the
  actor's ball slots 72–73 give the last-seen ball in the current trunk frame
  (on hardware: the ball model carried by odometry) instead of zeros. Slot 74
  carries its age, exp(−t / 2 s): 1 while seen. In env checks the memory was
  never zero when unseen; median error 0.07 m, 90th percentile 1.9 m (ball
  rolled after leaving view). The approach stage is unchanged (memory off).
- **Mirror:** slot 74 is no longer a yaw rate, so the stage 3 runner uses
  `augment_symmetries_kick_loop`, which keeps slot 74 instead of negating it.
- **Aim:** `kick_direction` = 0.5·cos⁺ + 0.5·exp(−(angle / 0.35)²). A 50°
  miss now earns about 0.32 instead of 0.64; a 10° kick earns about 0.94.
- **Warm start:** `v4/model_400.pt` with `--reset-obs-dims 74:75
  --normalizer-count 10000000` (slot 74's meaning changed).

Run: `2026-10-02_01-19-39_stage3_v5`.

## stage3_v6 — action noise capped

Action std grew in every kick run regardless of the reward fixes (v3 0.48 →
1.47, v4 0.47 → 0.83, v5 0.82 → 1.40). Noise inflates `action_rate_l2`
(−10 → −71 per episode in v5) and falls. The stage 3 runner now caps the
Gaussian std with `std_range = (0.05, 0.6)` (`KICK_MAX_ACTION_STD`); the
repo's NaN-guard patch also clamps the stored parameter. v6 resumes
`v5/model_300.pt` with the optimizer state.

## stage3_v7 — a different ball every episode, noisy vision

- **Ball randomization**, re-sampled every episode: mass ±30% via
  `dr.pseudo_inertia` (alpha −0.18 to 0.17, inertia scaled with it, 70–140 g
  observed), sliding friction ×0.7–1.3 and rolling resistance ×0.6–1.6 on
  the `ball_collision` geom.
- **Vision noise:** while the ball is seen, the actor's ball position gets
  Gaussian noise with σ = 3 cm + 5% of distance per axis
  (`KickLoopCommandCfg.ball_obs_noise = (0.03, 0.05)`). Measured median error:
  0.10 m within 1.5 m, 0.23 m beyond 2.5 m. The memory keeps the true
  last-seen position.
- `kick_vel_accurate` still uses the nominal roll deceleration (0.95 m/s²),
  so with rolling resistance randomized it is only approximate; it has a low
  weight.

v7 resumes `v6/model_650.pt` (layout and rewards unchanged).

## stage3_v9 — stop trading balance for kick speed

v8 regressed after iteration 1550: training falls rose 0.29 → 0.52 while kick
speed crept from 2.3 to 2.6 m/s. `kick_vel` paid for speed up to 3 m/s, and
a fall cost only −10, so harder kicks at some risk of falling paid. Changes:

- `KICK_VEL_REF` 3.0 → 2.5 m/s (full `kick_vel` credit at 2.5 m/s).
- `fall` weight −500 → −1000 (−20 per fall). A perfect kick (`kick_direction`
  + `kick_vel`, 36) still clearly beats a fall.

v9 resumes the best checkpoint, `v8/model_1550.pt`.

**Result:** worse. Falls after the first 2 s went 6.0% (1750) → 10.6% (2000)
and kick speed did not drop, so the speed explanation was wrong. Both changes
were reverted. Learning rate (~1.5e-4), KL (~0.013) and the AMP discriminator
were steady in v6–v9, so this is the policy wandering at the current step
size; v8 1500–1600 is a good plateau (re-evaluated with a second seed and
neighbouring checkpoints).

## stage3_v10 — smaller steps from the good plateau

Resumes `v8/model_1550.pt` with v8's rewards and `desired_kl` 0.004 (was
0.01), so the adaptive learning rate takes smaller steps and the policy
consolidates instead of wandering.

## Issue — the motion drifts when style is off most of the time (v8–v10)

Every continuation from the v8 plateau (v8 after ~1700, v9, v10 with smaller
steps) degraded within 200–400 iterations. Learning rate, KL and the
discriminator were steady. During v10's drift (iterations 1600–1700 →
1860–1960):

- `dof_pos_limits` grew 7× (−0.04 → −0.28)
- AMP style reward fell 3.08 → 1.19; discriminator policy prediction 0.29 →
  0.19
- falls tripled (`illegal_contact` 0.28 → 0.95)

**Cause:** the style gate was off within 1.5 m of the ball whenever a kick
was pending, and for 1 s after kicks. Gated envs get the mean style
(mean-fill), whatever they do. The robot spends much of the episode in that
zone, so style was active only ~35–40% of the time, and the motion there
slowly drifted toward extreme, joint-limit-hitting movements that spread to
balance.

**Fix (v11):** style is off only around the kick itself: within 0.6 m and in
the wedge (`STYLE_OFF_DISTANCE`), and for 0.7 s after a kick
(`STYLE_KICK_WINDOW`). Walking, circling and lining up near the ball are
judged again; style is active ~87% of the time. v11 resumes `v8/model_1600`
with default `desired_kl` (0.01).

**Lesson:** watch `Metrics/amp_style_active`, the style reward and
`dof_pos_limits`; a style gate that is off most of the time removes the
motion prior. `reward_budget.py` now flags both (STYLE, LIMITS).

**v11 result:** style active 73–76% of the time, but falls still rose (2.3%
→ 6.6% after the first 2 s, 1600 → 1850). In every continuation (v8 after
~1700, v9, v10, v11) falls rose as `Discriminator/policy_pred` fell below
~0.2 (0.28 → 0.14 within ~300 iterations); in the stable stretches (v6, v7,
v8 to 1600) it stayed 0.21–0.29. The discriminator wins and the style reward
turns harsh. v12b halves the style weight (`KICK_STYLE_WEIGHT` = 0.15, set
after the AMP wrapper in `config/k1_amp/__init__.py`).

## Issue — continuing from the v8 plateau trades falls for kicks

v8 after ~1700, v9, v10 (smaller steps), v11 (narrow style gate) and v12b
(half style weight) all drifted the same way within 200–400 iterations.
Fall probe, 2048 episodes:

| | v8 `model_1600` | v12b `model_1950` |
|---|---|---|
| episodes with a fall | 5.3% | 13.1% |
| falls within 2 s of a kick | 37% of falls | **66% of falls** |
| falls in the first 2 s (reset) | 42% | 15% |

The extra falls come from the kick: the policy learns riskier kicks. Since
step size and style changes made no difference, the objective itself prefers
them. **Likely cause: the discount horizon.** γ = 0.99 at 50 Hz is a ~2 s
horizon, so a fall costs about 10 (penalty) + ~14 (two seconds of ~7/s
discounted) ≈ 24 in value, against ~36 for a kick. Doubling the fall penalty
alone (v9) did not change that.

**v13:** `gamma` 0.995 (~4 s horizon; set in the stage 3 runner) and fall
penalty −20. A fall then costs ≈ 20 + 28 ≈ 48, more than a kick pays.

## Issue — v13/v16 do not kick, they run into the ball, leaning

Review in `play`: weird posture, tilted trunk, "more far dribble than kick".
Measured (512 episodes, no pushes):

| | stage 2 walker `model_8550` | v13 `model_1650` / v16 `model_1700` |
|---|---|---|
| trunk tilt, mean / p90 / p99 | 3.5° / 6.7° / 10.9° | **14.6° / 22–23° / 30°** |
| body speed at the kick (median) | — | **0.92 m/s** (97% of kicks > 0.5 m/s) |
| kicking foot speed relative to body | — | **1.0 m/s** |
| ball speed | — | 2.4 m/s |

The ball speed came mostly from the robot's own momentum: running into the
ball, not a planted kick with a leg swing. Causes: `kick_vel` paid ball speed
however it was produced; nothing penalized trunk tilt strongly; and the
style weight was halved (0.15) and gated off near the ball, which removed
the walking prior's posture discipline where the kick happens.

**v17 fixes:**

- **Kick quality** (`kick_quality_score`) multiplies `kick_direction`,
  `kick_vel` and `kick_vel_accurate`: exp(−(body speed / 0.4)²) ·
  clamp((foot speed relative to body − 1.0) / 1.5, 0, 1). 1.0 for a planted
  kick with a 2.5 m/s swing, 0.005 for v16's running pushes (measured mean
  0.01). `kick_goal` pays times the quality of the kick that launched the
  ball.
- **`trunk_tilt`** (`flat_orientation_l2`, −20): ~0.07/s at the walker's
  3.5°, ~1.3/s at 15°.
- **Style weight back to 0.3** (`KICK_STYLE_WEIGHT`).
- Warm start from the upright stage 2 walker, not the leaning stage 3
  policies (`2026-10-02_stage2-8550_mem_warmstart`, slot 74 reset).
- `eval_kick_loop.py` now reports kick quality, body speed at the kick and
  trunk tilt.

## Issue — quantity over quality (v13, v14)

v14 (AMP style weight 0) drifted exactly like the AMP runs, so the
discriminator only notices the drift. What continued training buys
(v13 `model_1650` → v14 `model_2000`): kicks 6.6 → 8.3, goals 2.26 → 2.54,
but kicks within 20° 71% → 60% and falls after 2 s 1.8% → 5.7%. Every kick
pays on its own (`kick_direction`'s cosine half paid 0.32 even for a 50°
miss), so more, quicker, sloppier kicks earn more, and a small extra fall
risk per kick barely registers.

**v15:** `kick_direction` uses only the sharp Gaussian
(`KickLoopCommandCfg.aim_broad_share` = 0; a 50° miss earns ≈ 0) and a new
`kick_fall` term charges −50 for a fall within 2 s of a kick, on top of
`fall` (−20). Resumes the best checkpoint, `v13/model_1650.pt`.

## Falls — where they happen (v6 `model_650`, 2048 episodes)

122 falls (6.0%). 28% happen in the first 2 s, mostly from motion-pool
reset poses, so `eval_kick_loop.py` now also reports falls after the first
2 s. About half happen within 2 s of a kick (18% within 1 s, 31% at 1–2 s),
at speed (median smoothed \|vx\| 0.65 m/s, \|wz\| 0.81 rad/s): the robot
rushes after the rolling ball before it has its balance back. Per kick that
is about 0.4% (3.3% of episodes over ~7.7 kicks).

## stage3_v8 — recover first, then chase

- `walk_speed` pays nothing for 2 s after a kick (it used to pay right away).
- The `walk_speed_limit` waiver after a kick is 0.5 s instead of 1 s; the
  0.3 s smoothing already absorbs the swing.
- `post_kick_stability` weight 2 → 4.

v8 resumes `v7/model_1100.pt`.

## Per-episode evaluations

`eval_kick_loop.py`, 1024 episodes × 30 s, deterministic policy:

| Checkpoint | Kicks/ep | ≤ 20° on target | Goals/ep | Kick speed | Near → kick | Fell (≤ 2 s after kick) | Ball in view after kick |
|---|---|---|---|---|---|---|---|
| smoke `model_99` (512 eps) | 5.7 | 33% | 1.1 | 2.45 m/s | 1.6 s | 9% (2%) | 98% |
| v4 `model_400` | 6.2 | 33% | 1.35 | 2.43 m/s | 1.85 s | 6% (1%) | 94% |
| v5 `model_300` | 5.9 | **63%** | **2.27** | 2.73 m/s | 1.66 s | **4%** (1%) | 96% |
| v6 `model_650`, **with** ball DR and vision noise (untrained for them) | 7.7 | 53% | 2.29 | 2.43 m/s | 1.58 s | 6% (3%) | 95% |
| v6 `model_650` (rerun, late falls split out) | 7.7 | 54% | 2.26 | 2.43 m/s | 1.58 s | 6.0%, 4.3% after 2 s (3.3%) | 95% |
| v7 `model_1100` (trained with DR and noise) | 7.5 | 53% | 2.08 | 2.42 m/s | 1.48 s | 7.0%, 4.8% after 2 s (4.1%) | 95% |
| **v8 `model_1550`** | 6.2 | **71%** | 2.19 | 2.60 m/s | 1.73 s | 4.4%, **2.2% after 2 s (1.6%)** | **98%** |
| v8 `model_2300` | 6.2 | 64% | 2.16 | 2.57 m/s | 1.78 s | 6.1%, 4.1% after 2 s (3.0%) | 99% |
| v8 `model_1550`, seed 1 | 6.2 | 71% | 2.14 | — | — | 5.4%, 2.6% after 2 s (1.8%) | — |
| v8 `model_1500` | 6.1 | 69% | 2.18 | — | — | 6.1%, 3.5% after 2 s (2.6%) | — |
| v8 `model_1600` | 6.4 | 69% | 2.22 | — | — | 4.2%, 2.3% after 2 s (1.0%) | — |
| v9 `model_1750` | 6.5 | 54% | 2.10 | 2.68 m/s | — | 8.4%, 6.0% after 2 s (4.4%) | 99% |
| v9 `model_2000` | 6.8 | 59% | 2.16 | 2.59 m/s | — | 13.1%, 10.6% after 2 s (8.9%) | 93% |
| **v13 `model_1650`** | 6.6 | **71%** | 2.26 | 2.54 m/s | 1.74 s | 3.5%, **1.8% after 2 s (0.9%)** | 99% |
| v13 `model_1650`, seed 1 | 6.6 | 71% | 2.27 | — | — | 3.3%, **1.3% after 2 s (0.6%)** | 99% |
| v13 `model_1700` | 7.6 | 64% | 2.38 | 2.45 m/s | 1.64 s | 3.8%, 1.8% after 2 s (1.0%) | 99% |
| v13 `model_1800` | 8.1 | 62% | 2.49 | 2.45 m/s | — | 8.3%, 6.0% after 2 s (3.7%) | 97% |
| v13 `model_1950` | 8.2 | 63% | 2.53 | 2.39 m/s | — | 10.7%, 8.5% after 2 s (5.9%) | 94% |
| v14 `model_1850` (style 0) | 7.6 | 58% | 2.45 | — | — | 9.0%, 6.4% after 2 s (4.2%) | 97% |
| v14 `model_2000` (style 0) | 8.3 | 60% | 2.54 | — | — | 8.3%, 5.7% after 2 s (4.0%) | 95% |
| v15 `model_1850` | 7.2 | 69% | 2.52 | 2.57 m/s | — | 7.9%, 4.9% after 2 s (3.3%) | 95% |
| v15 `model_2000` | 7.5 | 67% | 2.48 | 2.49 m/s | — | 7.0%, 5.2% after 2 s (4.2%) | 95% |
| **v16 `model_1700`** | 7.4 | **71%** | **2.55** | — | — | 3.7%, **1.8% after 2 s (1.4%)** | — |
| v16 `model_1700`, seed 1 | 7.5 | 71% | 2.55 | 2.52 m/s | 1.65 s | 3.1%, **1.6% after 2 s (1.3%)** | 99% |
| v16 `model_1750` | 7.8 | 64% | 2.63 | — | — | 4.4%, 2.8% after 2 s (1.7%) | — |
| v16 `model_1800` | 8.3 | 65% | 2.78 | — | — | 6.4%, 4.3% after 2 s (2.8%) | — |
| v16 `model_1850` | 8.5 | 68% | 2.90 | 2.51 m/s | — | 6.2%, 3.9% after 2 s (2.5%) | 98% |
| v16 `model_2000` | 7.6 | 71% | 2.61 | 2.51 m/s | — | 7.7%, 5.8% after 2 s (3.2%) | 95% |
| v13 `model_1650`, no pushes | 6.7 | 71% | 2.32 | — | — | 3.1%, 1.2% after 2 s (1.0%) | — |
| v16 `model_1850`, no pushes | 8.7 | 68% | 3.01 | — | — | 4.7%, 3.2% after 2 s (2.1%) | — |
| **v17 `model_400`** | 3.7 | **78%** | 1.72 | 3.27 m/s | — | 1.7%, 0.8% after 2 s (0.8%) | 99% |
| **v17 `model_500`** | 3.5 | **78%** | 1.67 | 3.45 m/s | — | 1.4%, **0.0% after 2 s (0.0%)** | 99% |
| v17 `model_500`, seed 1 | 3.5 | 78% | 1.68 | 3.47 m/s | — | 1.4%, 0.0% after 2 s (0.0%) | 99% |
| v17 `model_700` | 3.0 | 85% | 1.68 | 3.69 m/s | — | 1.2%, 0.1% after 2 s (0.1%) | 99% |
| **v17 `model_900`** | 3.3 | **89%** | **1.88** | 3.58 m/s | — | 1.5%, 0.2% after 2 s (0.1%) | 99% |
| v17 `model_900`, seed 1 | 3.3 | 89% | 1.85 | 3.56 m/s | — | 1.9%, 0.1% after 2 s (0.0%) | 99% |
| v17 `model_1200` | 3.6 | 87% | 1.85 | 3.29 m/s | — | 2.0%, 0.3% after 2 s (0.1%) | 98% |
| v17 `model_1500` | 4.0 | 91% | 2.21 | 3.35 m/s | — | 2.5%, 0.4% after 2 s (0.2%) | 99% |
| **v17 `model_1800`** | 3.7 | **93%** | 2.09 | 3.37 m/s | — | 1.2%, **0.1% after 2 s (0.1%)** | 97% |
| v17 `model_1800`, seed 1 | 3.6 | 94% | 2.09 | 3.40 m/s | — | 1.9%, 0.2% after 2 s (0.1%) | 98% |
| v17 `model_2100` | 4.1 | 93% | 2.19 | 3.19 m/s | — | 2.4%, 0.7% after 2 s (0.4%) | 92% |
| v10 `model_1750` | 7.1 | 52% | 2.08 | 2.46 m/s | — | 6.5%, 4.2% after 2 s (2.1%) | 100% |
| v10 `model_1950` | 5.1 | 55% | 1.68 | 2.72 m/s | — | 16.7%, 12.9% after 2 s (6.9%) | 97% |

The v4 row was evaluated with the v5 code (ball memory on), which v4 never
trained with.

## Run log

| Run | Start | Outcome | Lesson |
|---|---|---|---|
| v1 `2026-10-01_23-57-30` | stage 2 `model_8550` | kicked by iteration 100, stopped kicking by 400, hovered at 1.7 m | no zone-tied costs or style drops; no one-sided (farmable) rewards |
| v2 `2026-10-02_00-23-06` | v1 `model_100` | fell at once from iteration 300 | keep staying up net positive; check the per-second budget |
| v3 `2026-10-02_01-04-31` | stage 2 `model_8550` | sprayed kicks, std 1.5, stopped at 214 | speed rewards must be gated by aim |
| v4 `2026-10-02_01-10-45` | stage 2 `model_8550` | stable: 5.7 kicks and 1 goal per episode; aim stalled at 49° | — |
| v5 `2026-10-02_01-19-39` | v4 `model_400` | aim improved (0.85 → 0.51 rad in training); action std 0.82 → 1.40 and falls rising, stopped at 327 | ball memory and sharp aim work; noise needs a hard cap |
| v6 `2026-10-02_01-27-00` | v5 `model_300` (resume) | stable through 687: std 0.60, 6.8 kicks and 2.15 goals per episode, falls 0.22, no flags | the noise cap was the missing piece |
| v7 `2026-10-02_01-35-55` | v6 `model_650` (resume) | stable to 1135, no flags; per-episode eval level with v6 (plateau) | randomization costs nothing; falls after kicks are the main gap |
| v8 `2026-10-02_01-50-20` | v7 `model_1100` (resume) | peaked at 1550 (71% on target, falls after 2 s 2.2%); by 2300 drifted to 64% and 4.1% as kick speed crept up; stopped | delaying the chase after a kick halves post-kick falls; select checkpoints by evaluation, not by the latest |
| v9 `2026-10-02_02-20-04` | v8 `model_1550` (resume) | worse: falls after 2 s 6.0% (1750) → 10.6% (2000); kick speed unchanged; stopped at 2028, changes reverted | the speed explanation was wrong; reward-scale changes on resume can shake the critic |
| v10 `2026-10-02_02-34-06` | v8 `model_1550` (resume, v8 rewards) | also drifted: falls after 2 s 4.2% (1750) → 12.9% (1950); stopped | step size was not the cause; style was off ~60% of the time |
| v11 `2026-10-02_02-47-40` | v8 `model_1600` (resume) | still drifted: falls after 2 s 6.6% at 1850; discriminator policy score 0.28 → 0.14; stopped | narrowing the gate was not enough |
| v12 `2026-10-02_02-56-25` | — | invalid: `--agent.style-reward-weight` is overridden by the AMP wrapper's curriculum (stayed 0.3); stopped after ~1 min | set the style weight on the curriculum term |
| v12b `2026-10-02_02-58-26` | v8 `model_1600` (resume) | drifted the same way: falls after 2 s 6.5% (1800) → 11.4% (1950); stopped | the style weight is not the cause |
| v13 `2026-10-02_03-11-59` | v8 `model_1600` (resume) | **best at 1650** (71%, falls after 2 s 1.3–1.8%); more kicks and goals; still drifted after ~1750 (8.5% at 1950); stopped at 1986 | longer horizon helps; select early checkpoints |
| v14 `2026-10-02_03-26-05` | v13 `model_1650` (resume) | diagnostic, AMP style 0: drifted the same way (falls after 2 s 5.7–6.4%, joint limits ×7); stopped at 2036 | the discriminator only notices the drift; the task reward drives it |
| v15 `2026-10-02_03-37-55` | v13 `model_1650` (resume) | accuracy held (69% at 1850, goals 2.5) but falls still rose (4.9–5.2% after 2 s); joint limits ×6; stopped at 2036 | sharp aim fixes quantity-over-quality; fall penalties do not move falls |
| v16 `2026-10-02_03-49-13` | v13 `model_1650` (resume) | **balanced best at 1700** (71%, 2.55 goals, falls after 2 s 1.6–1.8%); joint limits contained (×2.3 instead of ×6); more productive later (1850: 2.9 goals) but falls rose; stopped at ~2030 | the joint-limit penalty keeps motion in range; select early checkpoints |
| v17 `2026-10-02_08-25-15` | stage 2 `model_8550` (warm start, slot 74 reset) | **best at 1800** (93–94% within 20°, quality 0.76–0.77, 2.1 goals, falls after 2 s 0.1–0.2%); improved 500 → 1800; first drift signs at 2100 (falls 0.7%, view 92%, joint limits ×7); stopped at 2144 | paying only for real kicks plus a tilt penalty fixes both the posture and the running push |
| v18 `2026-10-02_12-08-27` | v17 `model_1800` (resume) | action_rate −0.03 → −0.1: runner-sim jitter still 13× the gold walk; left running by mistake to 3650 | action_rate does not smooth the deterministic action |
| v19 | v18 `model_2150` (resume) | CAPS 1.0 / 0.5: jitter 2.1×, but 81% within 20°, 1.23 goals, falls after 2 s 4.2% | CAPS works but this strength costs the kick |
| v20 `2026-10-02_12-44-00` | v18 `model_2150` (resume) | CAPS 0.3 / 0.1: jitter 4.5× (2350), kicking kept; posture worse in the runner sim (knee gap p10 0.145 m vs 0.174, arm dev 0.42 vs 0.07 rad, head looking up −0.17 rad) | see "Issue — posture and head (v18–v20)" |
| v21 `2026-10-02_13-14-11` | v20 `model_2350` (resume) | scripted head tracker, real camera FOV, knee-gap and arm-pose penalties, CAPS 0.5 / 0.2. **`model_2800`**: 94% within 20°, quality 0.81, 1.34 goals, falls after 2 s 0.4%; runner sim jitter 2.1×, Δq mean 1.9×, knee gap p10 0.190 m, arm dev 0.19 rad, no falls. But it walks on its toes (heel up > 5° in 34% of runner-sim contact samples, gold walk 2.4%; 63% in training sim). 2950 regressed (jitter 4.8×). Stopped at ~2990 | the head tracker and posture terms cost no kick accuracy; check the feet too |
| v22 `2026-10-02_13-38-50` | v21 `model_2800` (resume) | `foot_flat` −30. **`model_3000`**: 95% within 20°, quality 0.85, falls after 2 s 0.2%; heel-up 34% → 15% (runner sim), 63% → 25% (training sim); knee gap p10 0.184 m; jitter back at 4.5× (Δq p99 2.0×). Stopped at ~3010 | the flat-foot term works without hurting the kick; CAPS 0.5 / 0.2 does not hold the smoothness |
| v23 `2026-10-02_13-47-46` | v22 `model_3000` (resume) | CAPS 0.8 / 0.3. `model_3350`: 95% within 20°, quality 0.85, falls after 2 s 0.4%; heel-up stalled at ~22% (training sim) / 27% (runner); jitter 4.2×. `model_3250` looked perfect in the runner bench (jitter 0.7×, heel-up 3%) but it barely moved there (1.4 m walked, 0.9 kicks per 20 s vs 10 m and 2.8 for 3350). Stopped at ~3390 | never judge smoothness or posture without activity: the bench now reports kicks and distance walked per run |
| v24 `2026-10-02_14-02-06` | v23 `model_3350` (resume) | `foot_flat` −60, CAPS 1.0 / 0.4. `model_3550`: runner jitter 1.5×, heel-up 7.6%, 92% within 20°, but it stands in front of balls 3–4 m away (idle 28% of the time a ball rests > 1.5 m away; 0 kicks from a ball 3 m ahead). `model_3450`: jitter 2.8×, heel-up 6.4%, idle 24%. Stopped at ~3600 | smoothness and flat feet can be bought by standing still; watch the idle metric |
| v25 `2026-10-02_14-13-20` | v24 `model_3450` (resume) | walk_speed 2 → 5. **`model_3650`**: 97% within 20°, quality 0.88, 1.49 goals, falls after 2 s 0.2%, idle at a far ball 3% (v24 24–28%); runner sim 4.3 kicks per run, kicks from every start, 11.6 m walked, no falls, jitter 3.6×, heel-up 25% (training sim 20%). 3750/3850: heel-up 21–22% (runner 26–38%), jitter ~3.5×, more late falls at 3750. Stopped at ~3900 | walking pays again; the heel lift is in normal walking (p50 0.7°, p90 8.8°), too small for a −60 squared penalty |
| v26 | v25 `model_3650` (resume) | `foot_flat` −200; stopped after a few iterations for v27 (robot feedback) | — |
| v27 `2026-10-02_14-33-18` | v25 `model_3650` (resume) | robot memory (no odometry), head look-down 0.18 + search, pitch limit 0.82, kick promptness multiplier, `foot_flat` −200. `model_4050`: 87% within 20°, falls after 2 s 0.0%, heel-up 3.3% (runner 2.7%, gold walk 2.4%), idle 1%, 5.25 kicks per runner run, jitter 3.4×; near-ball time to kick 3.3 s; ball seen only 51% at 0.4–0.7 m (misses all below the image). Stopped at ~4190 | flat feet solved; near the ball the head still looks at the stale (farther) memory |
| v28 `2026-10-02_14-55-07` | v27 `model_4050` (resume) | lost close (< 1.5 m, 0.2 s) → head straight down, yaw sweep after 0.5 s. **`model_4250`**: 86% within 20°, falls after 2 s 0.0%, heel-up 4.2% (runner 3.6%), idle 1%, near time 3.25 s, seen at 0.4–0.7 m 57% (51%); runner: no falls, 2.9 kicks / 12.6 m per run, jitter 2.8×, Δq p99 1.5×, knee gap p10 0.176 m. **`model_4400`**: 91% within 20°, quality 0.86, falls after 2 s 0.4%, heel-up 3.6% (runner 3.6%), arm dev 0.12 rad, near time 3.1 s; runner: no falls, 3.75 kicks / 12.6 m per run, jitter 2.9×, Δq p99 1.5×. 4500: 83%; 4650/4750: 86%, jitter 2.7–2.8×, heel-up 0.7–1.8% (runner), fewer runner kicks (2.3–2.8). Plateau; stopped at ~4770 | **robot candidate: `model_4400`** |
| v29 `2026-10-02_16-55-34` | v28 `model_4400` (resume) | walking-pose terms (`walk_base_height` −250 → 0.54 m, `walk_stance_width` −250 → 0.12–0.19 m, `knee_valgus` −200; gated off around kicks), style 0.3 → 0.45. `model_4750`: base 0.474 → 0.508 m, knees 1.28 → 0.95 rad, stance 0.26 → 0.17 m, knock-knee +0.08 → 0.00 m, arms 0.12 → 0.09 rad, heel-up 0.5% (runner), roll sd 1.9 → 1.5°; 89% within 20°, falls after 2 s 0.0%, near time 3.0 s; but quality 0.84 → 0.78, runner kicks per run 3.75 → 2.6, walking jitter +10%; cadence unchanged (6.9 steps/s vs walk 4.6). Stopped at ~4860 | pose terms fix the crouch; the higher style weight costs the kick |
| v30 `2026-10-02_17-11-37` | v29 `model_4750` (resume) | style back to 0.3, pose terms kept. `model_5000`: pose held (base 0.507 m, knees 0.97 rad, stance 0.17 m); two seeds × 1024 vs v28/4400: within 20° 89 vs 90%, quality 0.78 vs 0.85, kicks 1.94 vs 2.07, goals 1.1 vs 1.2, ball speed 3.58 vs 3.72 m/s. Stopped at 5000 | the style weight was not the cause; the pose terms reached too close to the ball |
| v31 `2026-10-02_17-25-32` | v30 `model_5000` (resume) | walking-pose terms only with the ball > 1 m away. Two seeds × 1024 vs v28/4400 (90%, q 0.85, 3.72 m/s, 1.2 goals, near 3.16 s): `model_5150` 91%, q 0.81, 3.47 m/s, 1.27 goals, near 2.94 s; runner best posture (ang. rate 44 vs 63 °/s, base 0.514 m, knees 0.88 rad, stance 0.18 m, 3.9 kicks/run) but walking jitter +10%. `model_5500` 91.5%, q 0.825, 3.59 m/s, 1.23 goals; runner leans forward (pitch +2.9°, sd 4.2°), 3.2 kicks/run, jitter 3.4×. Cadence unchanged (6.9–7.3 steps/s vs 4.6). Stopped at ~5560 | freeing the last metre recovers most of the kick; cadence drives the remaining sway and jitter |
| v32 `2026-10-02_17-48-20` | v31 `model_5500` (resume) | cadence term (−10 × ((0.17 − swing)/0.05)² per touchdown, walking only). Backfired: 8.0–8.5 steps/s (6.9 before), leg jitter 0.19 (0.09), heel-up 10–14%, trunk pitch +4.4–4.9° / sd 3.6–5.0°. Stopped at ~5760, term removed | a touchdown-based swing penalty is gamed by shuffling; cadence needs another handle |

| v33 | v31 `model_5450` (resume) | long range = 8 m and beyond (targets 8–20 m), power kick 7–8 m/s: `kick_vel` reference 7.5 m/s for long kicks, `kick_vel_accurate` = 1 inside 7–8 m/s (σ 1 m/s outside); short / medium unchanged. Sim ball 0.10 kg, r 0.08 m. v31/5450 before: long kicks 3.25 m/s, all kicks p99 6.3, max 7.2 m/s, kicking-foot speed p50 3.1 / max 4.7 m/s. After ~260 iterations (5600/5700): long kicks still 3.3 m/s mean (p90 5.0), all kicks p99 6.1–6.9, ≥ 7 m/s 0–0.8 %; foot speed p50 3.0–3.2; other metrics held (92 % within 20°, falls after 2 s 0 %, pose unchanged). Stopped at ~5720 | a 7–8 m/s target far outside what the policy does gives almost no gradient: the band term is ~0 below 6 m/s and kick_vel adds only ~+10 per kick for doubling the speed |

| v34 `stage3_v34` | v31 `model_5450` (resume) | One fine-tune, four parts. (A) speed caps |vx| ≤ 2.0 (backward ≤ 1.75), |vy| ≤ 1.5, |wz| ≤ 1.5, ramped from v31's 1.2 / 1.0 / 1.25 over 300 iterations (ramp counts the command's own steps: on resume the runner sets `common_step_counter` to the checkpoint's, which skipped the ramp in a smoke test). (B) height 0.52 m ± 1 cm (`walk_base_height` −1 × ((excess)/2 cm)²) and `trunk_pitch_band` −0.5 × ((pitch outside −5…+3°)/2°)², both walking only. (C) `long_kick_power` +900: long kicks paid inside a speed band that starts at 5–6 m/s and rises 0.25 m/s whenever 40 % of recent long kicks land in it, up to 7–8 m/s (σ 1.5 m/s); `kick_vel` / `kick_vel_accurate` long kicks use the same band. (D) ball mass ×0.5–2.5 (0.05–0.25 kg), sliding friction ×0.6–1.4, rolling ×0.5–2.5, new `ball_bounce` (solref timeconst 0.03–0.08, dampratio 0.08–0.4; new `mdp.dr.geom_solref`). Before (v31/5450): pitch +4.0° / height 0.497 m at 1–1.5 m/s, long kicks 3.3 m/s. `model_5750` (ramp done): posture better at speed (pitch 1.0–1.5 m/s +1.6° mean / +4.7° p90; 0.8–1.0 m/s +0.5° / 3.2°; height 0.502–0.513 m), 94 % within 20°, 3.0 kicks / ep, 1.10 goals, falls after 2 s 0.1 %, heel-up 5.7 %. But it walked slower (time above 1 m/s 7 % → 3 %) and kicks did not get harder (foot speed p50 3.05 m/s unchanged; ball 2.6 m/s mean, lower because balls are now up to 0.25 kg); long band stuck at 5–6 m/s (hit rate ~1 %). Stopped at ~5860 | raising the caps lowers walk_speed's pay per m/s (score = speed / cap); an absolute ball-speed band is unreachable for heavy balls — reward the controllable part (foot swing speed) |

| v35 `stage3_v35` | v34 `model_5750` (resume) | Feasibility probe first (scripted right-leg swings at a 0.1 kg ball in the training sim, real motor model, no balance control): ball 7–12 m/s in 19 of 256 variants (ball/foot speed 1.5–2.4× for a good strike vs ~1.1× in the policy's kicks); none stayed upright, so the motors allow 7–8 m/s and balance is what must be learned. Changes: `walk_speed` = speed toward the ball clipped to the cap, over a fixed 1 m/s (2 m/s pays twice 1 m/s); `long_kick_power` +900 on the kicking-foot speed relative to the body, band 3.5–4.5 m/s rising 0.25 m/s at 40 % hits up to 5.5–6.5 m/s (σ 1.5); long `kick_vel` pays ball speed up to 7.5 m/s; long `kick_vel_accurate` = min(1, speed / rolling speed); caps start at 2.0 / 1.5 / 1.5 (no re-ramp). Posture, ball randomization and the rest as v34. `model_5950` (1 seed × 1024) vs v34/5750: time above 1 m/s 3 → 10 % (v31 7 %); pitch at 1.0–1.5 m/s +0.8° mean / +3.6° p90 (v34 +1.6 / 4.7, v31 +4.0 / 7.8); height 0.504–0.515 m; 93 % within 20°, 3.2 kicks, 1.19 goals, near-ball time 2.6 s (3.0), falls after 2 s 0.2 %, quality 0.83. Swing band 3.5 → 3.75 m/s in 200 iterations; foot speed p50 3.12 / p90 3.71 (3.05 / 3.57); long-kick ball speed 2.72 m/s. Watch: heel-up 7.0 % (v34 5.7 %, v31 4.4 %), idle 4 % (2 %), falls per episode in training 0.14 → 0.25 — running | the fixed 1 m/s reference made it use the higher caps and it stayed upright at speed; power is rising slowly |

v35/5950 in the runner sim (caps 1.2 / 0.8 / 1.0; gold walk at 0.8 m/s): far steadier trunk than v31/5450 (pitch −1.4° / sd 2.4° vs +1.2° / 5.2°; angular rate p90 70 vs 81 °/s, gold 31), taller (0.509 vs 0.495 m), less knee bend (0.93 vs 1.11 rad), but rougher actions (walking jitter 0.100 vs 0.079, +27 %; overall 3.2× vs 2.6× the gold walk), wider arms (0.154 vs 0.129 rad) and still 7.5 steps/s (gold 3.5). It walked 0.69 m/s mean there vs v31's 1.1 — the runner's fixed caps and scenarios differ from training's per-episode caps; compare per speed bin, not means. Runner benches now run from a scratch export of the `kick` branch + `stash@{0}` (the runner repo is on `main`).

v35 to 6200: the swing band stalled at 3.75 m/s for ~350 iterations (12–16 % of long kicks in it, 40 % needed); foot speed p50 3.08. Cause: with σ 1.5 m/s the band still paid 0.83 for a 3.1 m/s swing, and the kick-quality swing factor saturates at 2.5 m/s, so nothing pulled the swing above ~3 m/s. 6200 also drifted (idle at a far ball 4 → 9 %, heel-up 7.0 → 7.7 %), so v36 resumes from 5950. Stopped at ~6230.

| v36 `stage3_v36` | v35 `model_5950` (resume) | `long_kick_power` = monotonic ramp: clamp((swing − 2.5) / (target − 2.5), 0, 1) × aim² × quality; target starts 3.75 m/s, +0.25 when 40 % of recent long kicks reach it, up to 6.5 m/s. Everything else as v35. `model_6150`: target 3.75 → 4.0 m/s; kicking-foot speed p50 3.29 / p90 3.95 / max 4.98 m/s (v35/5950 3.12 / 3.71); long-kick ball speed 2.92 m/s (p90 4.88); pitch at 1.0–1.5 m/s +0.6° / 3.4°, 14 % of walking above 1 m/s; 94 % within 20°, 1.19 goals, quality 0.84; but idle at a far ball 13 % (5950: 4 %), falls after 2 s 0.4 %. Idle debug (1024 envs): ball seen 73 % of idle time, 2.5 m away, vx cap median 0.41 m/s — since v35, walk_speed paid speed / 1 m/s, so a 0.4 m/s cap paid at most 0.4 and walking no longer beat posture and fall costs. Stopped at ~6200 | a monotonic ramp moves the swing; reward normalisation must keep low caps worth walking |
| v37 `stage3_v37` | v36 `model_6150` (resume) | `walk_speed` over min(cap, 1 m/s): walking at a cap ≤ 1 m/s pays 1 (as v34), above that 2 m/s pays twice 1 m/s (as v35); swing target restarts at 4.0 m/s. `model_6350`: idle at a far ball back to 5 % (v36 13 %); foot speed p50 3.41 / p90 4.40 / max 5.59 m/s; long-kick ball speed 2.99 m/s (p90 5.14, max 8.65); 19 % of walking above 1 m/s, pitch there +0.7° / 3.5°; 93 % within 20°, 1.23 goals, near-ball time 2.44 s, falls after 2 s 0.0 %, quality 0.85. Heel-up 8.8 % keeps rising with walking speed (4.4 → 8.8 % since v31) — check per speed bin: toe-off at speed is normal (gold walk 19 % at 0.7 m/s in the runner) — running | min(cap, 1 m/s) normalisation keeps both low-cap walking and high-speed pay |

Speed-binned checks on v37/6350 (training sim, walking, ball > 1 m):
- **Heel-up is toe-off at speed**, not tip-toeing: 0.9 % at 0–0.2 m/s, 5.4 % at 0.4–0.6, 14.4 % at 0.6–0.8, 19.1 % at 0.8–1.0, 25.6 % at 1.0–1.5 m/s. The gold walk shows ~19–21 % at 0.7 m/s in the runner, so v37 is at or below it at matched speed; the aggregate rose only because it walks faster. Judge heel-up per speed bin.
- **Smoothness unchanged at matched speed**: leg jitter |Δ²a| v31/5450 vs v37/6350 = 0.135 / 0.132 (0–0.4 m/s), 0.152 / 0.155 (0.4–0.8), 0.169 / 0.168 (0.8–1.2), 0.190 / 0.189 (1.2–2.5). Jitter rises with speed for both. The runner bench's 3.6× vs 2.6× (walking jitter 0.115 vs 0.079) reflects v37 walking faster in those scenarios, not a loss of smoothness — smoothness must be compared per speed bin.
- Arms in the runner: 0.162 vs 0.129 rad (v31) — to check per speed as well.

v37/6600 vs 6350: swing target 4.25 m/s; 3.8 kicks / ep, 1.25 goals, idle 3 %, near time 2.39 s, 23 % of walking above 1 m/s, heel-up per bin lower; but accuracy 89 % (6350: 92–93 %), swing p50 back to 3.26 m/s, arm deviation 0.194 rad. Arm deviation across checkpoints (same eval, seed 1): v31/5450 0.129, v34/5750 0.133, v35/5950 0.152, v37/6350 0.167, v37/6600 0.194. Per joint (walking): a static posture, not swing — shoulder roll +0.28 rad outward (v31 0.19) and elbow yaw ±0.21 (v31 ±0.04), mean ≈ rms; shoulder-pitch swing smaller (rms 0.09 vs 0.12). The 8-joint `arm_pose` (−2) priced it at ~0.7/s. Stopped v37 at ~6620.

| v38 `stage3_v38` | v37 `model_6350` (resume) | `arm_abduction` −0.3: Σ ((|shoulder roll, elbow yaw − default| − 0.1 rad) / 0.1)², off around kicks (style gate); ≈ −1.4/s at v37's arm posture. Swing target starts at 4.25 m/s. Rest as v37. `model_6550`: arm deviation 0.117 rad (lowest so far; shoulder roll 0.28 → 0.07, elbow yaw 0.21 → 0.03; elbow pitch now −0.16, covered by arm_pose); long kicks 3.07 m/s (p90 5.12), swing p50 3.43; falls after 2 s 0.0 %, idle 3 %; dip after the change: 2.9 kicks / 1.13 goals (6350: 3.3 / 1.23), quality 0.81 (0.85), 90 % within 20° (93 %), 11 % of walking above 1 m/s (19 %), pitch at 1.0–1.5 m/s +1.1° / 4.1° (+0.7 / 3.5) — running | a targeted term on the joints that drifted fixed the arms in 200 iterations; watch for the usual post-change dip to recover |

v38/6800 (2 seeds × 1024): 89–91 % within 20°, quality 0.84, 3.2 kicks / 1.22 goals, near-ball time 2.44 s, idle 1–2 %, falls after 2 s 0.1–0.3 %, arm deviation 0.103 rad (best), swing p50 3.52 / p90 4.38 / max 5.78 m/s (target 4.5), pitch at 1.0–1.5 m/s +1.0° / 4.0°, height 0.502–0.509 m — **best all-round sim checkpoint so far**. Runner (caps 0.45 / 0.3 / 0.6): 4.75 kicks per run (v31 2.6), arms 0.097 (0.129), no falls; walking at 0.65 m/s vs v31's 0.50, so its higher jitter (0.103 vs 0.079) is again confounded by speed.

Speed-cap compliance while chasing (ball > 1.5 m, 2 s after kicks; training sim): v38 / v31 vx mean at cap 0.3–0.6: 0.45 / 0.42, over cap by > 0.1 m/s 31 % / 24 %; cap 0.9–1.2: 0.76 / 0.76; cap 1.6–2.0: **0.90 / 0.87 (p90 1.24 / 1.30)**. High caps are not used (the 2 m/s goal is not met: chases are short and posture, fall and smoothness costs outweigh speeding up), and low caps are exceeded (already in v31). Stopped v38 at ~6850.

| v39 `stage3_v39` | v38 `model_6800` (resume) | `walk_speed_track` +3: 1 − \|speed toward ball − vx cap\| / cap (clipped at 0) with the ball > 2.5 m away and after the post-kick window — peaks at the cap, linear both sides, so it pulls up to high caps and down to low ones; `walk_speed_limit` −10 → −20; swing target starts at 4.5 m/s. `model_7050`: low caps respected better (0.3–0.6 m/s caps: over by > 0.1 m/s 17 % of chasing, v38 31 %; 0.6–0.9: 8 %, was 15 %); high caps 0.97 m/s mean (v38 0.90); 92 % within 20°, quality 0.82, 1.18 goals, falls after 2 s 0.0 %, arms 0.094 rad (best), long kicks 3.18 m/s (p90 5.44, best); per-second budget positive (+0.3–0.5/s). Max-speed test (cap 2.0, ball 8 m straight ahead): 1.30 m/s mean, p90 1.63, peak 2.67, pitch +0.6°, height 0.498 m — the policy can go faster than it does in play; balls spawn 1–4 m away, so long chases (and speeds above ~1.3 m/s) are rarely practised — running | a two-sided cap-tracking term fixes both under- and over-speed; high speed needs room to practise |

v39/7300 (2 seeds): low caps respected (0.3–0.6 m/s caps over by > 0.1 m/s 7 %, 0.6–0.9: 4 %), arms 0.088 rad, long kicks 3.21 m/s (p90 5.59), max-speed chase 1.38 m/s mean (p90 1.74); but 2.74 kicks / 1.10 goals (7050: 3.09 / 1.18), near-ball time 2.65 s, idle 4–6 %, 90 % within 20°. Stricter speed limits slowed the approach at low caps; 7050 is the better balance. Stopped at ~7310.

| v40 `stage3_v40` | v39 `model_7050` (resume) | balls spawn 1–8 m away (1–4 m before; new `ball_distance_range` cfg, approach stage unchanged) so long chases at high caps are practised. `model_7300` (2 seeds): high caps unchanged (0.93 m/s mean at 1.6–2.0 m/s caps; 8 m chase 1.29 m/s, p90 1.60); swing p50 3.21 m/s (v39/7050 3.51), long kicks 2.97 m/s (3.18), 1.09 goals (1.18); held 91–92 % within 20°, arms 0.088, idle 1–2 %, low-cap compliance (8 % / 3 % over). Stopped at ~7330 | room to run is not what limits speed: the policy cruises at ~1.3 m/s; at weight 3 the cap-tracking gain from 1.3 to 1.8 m/s (~0.8/s) does not pay for a faster gait |
| v41 `stage3_v41` | v40 `model_7300` (resume) | `walk_speed_track` 3 → 8 (balls still 1–8 m). If posture or kicking breaks, 2 m/s needs a different gait than this walk — running | — |

AMP data speed coverage (amp_mix_ww_cmu, as sampled with its weights; root speed at 30 fps): 0–0.5 m/s 30.6 %, 0.5–1.0 39.5 %, 1.0–1.5 12.4 %, 1.5–2.0 6.2 %, > 2.0 11.3 % (sprint clips; p99 2.45 m/s). The style prior has fast references, so it is not what holds the policy at ~1.3 m/s.

v41/7550: no faster (0.95 m/s mean at 1.6–2.0 m/s caps, 8 m chase 1.34 m/s) but kicking fell (2.10 kicks, 0.89 goals, 88 % within 20°; v40 3.0 / 1.09 / 92 %) and lean returned at speed (+1.5° / 4.4°). Reward size is not what holds speed at ~1.3 m/s. Stopped at ~7590; `walk_speed_track` back to 3, balls back to 1–4 m.

| v42 `stage3_v42` | v39 `model_7050` (resume) | CAPS 1.0 / 0.4 → 0.6 / 0.25: test whether the smoothness loss is what caps both walking speed (~1.3 m/s cruise) and kick swing (target stuck at 4.5 m/s). Judge jitter per speed bin. `model_7300` vs v39/7050: kicking-foot speed p50 3.94 / p90 4.79 / max 6.10 m/s (3.51 / 4.34 / 5.27); long kicks 3.24 m/s (p90 5.38); 92 % within 20°, 1.23 goals (1.18), quality 0.86, falls after 2 s 0.1 %, idle 1 %, arms 0.087; walking speed at 1.6–2.0 m/s caps 1.06 (0.97), 8 m chase 1.27 (unchanged); leg jitter at matched speed +7–9 % (0.151 / 0.174 / 0.193 / 0.215 vs 0.138 / 0.161 / 0.177 / 0.203). Stopped at ~7330 | CAPS was what held the kick swing; it does not hold walking speed |
| v43 `stage3_v43` | v42 `model_7300` (resume) | phase-weighted CAPS (new `caps_near_ball_scale` in AmpPPO): 1.0 / 0.4 while walking, × 0.5 on samples whose actor ball estimate is within 0.8 m — keep the freer swing, restore walking smoothness. `model_7550`: leg jitter at matched speed 0.136 / 0.161 / 0.176 / 0.197 (= v39's 0.138 / 0.161 / 0.177 / 0.203; v42 0.151–0.215); swing p50 3.71 / p90 4.62 / max 6.18 m/s; 3.91 kicks / 1.35 goals per episode (best), near-ball time 2.24 s (best), 91 % within 20°, quality 0.84, falls after 2 s 0.1 %, idle 4 %, arms 0.089; walking at 1.6–2.0 m/s caps 1.04 m/s, low caps over by > 0.1 m/s 7 % / 6 %; long kicks 3.01 m/s (p90 5.11) — running | smoothing walking and kicking differently gets both: the walk keeps v39's smoothness, the kick keeps most of v42's freer swing |

v43/7550 in the runner sim (caps 0.45 / 0.3 / 0.6; gold walk commanded 0.45 m/s): walks at 0.46 m/s (respects the cap; v31 0.50), **walking leg jitter 0.085 = gold walk 0.083 at matched speed** (v31 0.076), kicking jitter 0.136 (v31 0.146), arms 0.048 rad (gold 0.096, v31 0.120), pitch −0.9° / tilt 2.3° (gold −4.2° / 2.2°), height 0.510 m, knees 0.92 rad (gold 0.44), 6.7 steps/s (gold 4.6), 3.1 kicks per run, no falls. Remaining gaps to the gold walk: knee bend (~3 cm lower) and cadence.

v43/7800 (2 seeds): 4.3–4.6 kicks / 1.33 goals per episode, 94 % within 20°, near-ball time 2.2 s, jitter per speed unchanged — but weaker long kicks (2.55 m/s, p90 4.34; swing p50 3.51) and idle 4–6 %: quantity over power again (as v13/v14). **Best balanced: v43/7550.** Stopped at ~7810.

| v44 `stage3_v44` | v43 `model_7550` (resume) | `air_time` weight 0.1 → 1.0, threshold_min 0.05 → 0.15 s: pay only longer swings, to lower the 6.7 steps/s cadence (gold 4.6) and test whether short strides cap speed at ~1.3 m/s. `model_7800`: cadence unchanged (7.04 vs 7.06 steps/s in the runner at caps 1.2 / 0.8 / 1.0; gold 3.5 at 0.73 m/s), 8 m chase 1.25 m/s; 4.3 kicks / 1.38 goals, 90 % within 20°; long kicks 2.90 m/s, swing p50 3.50 (quantity up, power not). Reverted; stopped at ~7840 | air_time does not set cadence; cadence and the ~1.3 m/s cruise remain open (a clock / phase input would be needed for a gait-frequency reward) |

Quantity over power (v43/7800, v44): `kick_direction` (900) paid every kick for aim × quality whatever the ball speed, so several weak taps toward a far target earned as much as one strong kick; the taps also dilute the long-kick swing curriculum's hit rate.

| v45 `stage3_v45` | v43 `model_7550` (resume) | `kick_direction` × clamp(ball speed / (0.7 × rolling speed the target needs), 0, 1): weak taps earn proportionally less aim reward; air_time back to the AMP walk's (0.1, 0.05 s). `model_7800` (2 seeds): 94 % within 20°, quality 0.85, 3.8 kicks / 1.31 goals, falls after 2 s 0.0–0.1 %, arms 0.082, jitter per speed unchanged; power not higher (long kicks 2.87 m/s with randomized balls) | the aim reward tied to power improved accuracy, not power |

**Kick speed must be measured with the nominal 0.1 kg ball** (the user's 7–8 m/s goal; since v34 the randomized ball is 0.05–0.25 kg and hides progress). Nominal ball, long kicks mean / p90, all kicks ≥ 7 m/s: v31/5450 3.18 / 4.86 m/s, 0.1 %; **v43/7550 4.34 / 6.75 m/s, 2.8 % (max 8.9; expected roll 11.8 m)**; v45/7800 4.12 / 6.57, 1.9 %. Swing p50 / p90: 2.98 / 3.64 → 3.63 / 4.60 → 3.49 / 4.56 m/s. Long-kick power is +36 % since v31; the gap to 7–8 m/s is mostly swing speed. Swing curriculum stuck at 4.5 m/s (10–25 % of long kicks reach it, 40 % needed).

| v46 `stage3_v46` | v45 `model_7800` (resume) | `long_kick_power` ramp target fixed at 6.5 m/s (no curriculum; the monotonic ramp gives a gradient up to 6.5). `model_8050`: nominal-ball long kicks 4.26 m/s (p90 6.80), swing p50 3.46 — no gain over v43/7550; 92 % within 20°, quality 0.86, 1.20 goals, falls after 2 s 0.1 %, arms 0.075 (best), idle 2 %. Stopped at ~8080 | a gradient alone does not move the swing: +1 m/s pays ~+4.5 per long kick vs ≥ 50 for a post-kick fall |
| v47 `stage3_v47` | v46 `model_8050` (resume) | `long_kick_power` 900 → 2000 — last push before settling on the fastest reliable kick; watch falls after kicks. `model_8300` (nominal ball): long kicks **5.04 m/s mean, p90 8.33**, 10.4 % of all kicks ≥ 7 m/s (max 11.7), expected roll 16.7 m; swing p50 3.97 / p90 6.21 / max 7.53 m/s; 2 seeds: falls after 2 s 0.0–0.1 %, 89 % within 20° (v46 92 %), quality 0.82–0.83, 1.22 goals, arms 0.085 — running | paying enough for the swing moves it without falls: the cost of a post-kick fall had outweighed a faster swing |

v47/8300 checks: leg jitter per speed bin unchanged (0.140 / 0.158 / 0.173 / 0.193); pitch at 1.0–1.5 m/s +1.0° / 4.1°, height 0.50–0.51 m; caps respected (10 % / 4 % over at low caps); 8 m chase 1.39 m/s. Runner sim vs v43/7550: walking jitter 0.085 (same), kick jitter 0.167 (0.136 — the harder swing), joint speed p99 hip pitch 41 % / knee 54 % of the motor limits, no torque saturation, no falls, 4.25 kicks per run (3.1). v47/8550 (nominal ball): long kicks 4.51 m/s (p90 7.42), 7.8 % ≥ 7 m/s, swing p50 4.09 / p90 5.58; 91–92 % within 20°, falls after 2 s 0.1 % — power vs accuracy varies between checkpoints. 8700: long kicks 5.08 m/s (p90 8.46), 10.1 % ≥ 7 m/s, 92 % within 20°, 1.25 goals, falls after 2 s 0.2 %. 8800: long kicks 5.39 (p90 8.67), 13.0 % ≥ 7 m/s (max 11.0), expected roll 18.8 m, 90 % within 20°, 1.23 goals, falls after 2 s 0.3 %, knee gap p10 0.158 m — watch falls and knee gap. 8950 / 9050 (2 seeds): long kicks 4.73 / 4.80 m/s (p90 8.2 / 8.1), 9–10 % ≥ 7 m/s, 90–92 % within 20°, falls after 2 s 0.0–0.6 % — plateau, slight drift. Stopped at ~9070.

**Candidates after v47** (nominal ball): `v47/model_8700` balanced (long kicks 5.08 m/s, p90 8.46, 92 % within 20°, 1.25 goals, falls after 2 s 0.2 %) and `v47/model_8800` most powerful (5.39 m/s, p90 8.67, 13 % of kicks ≥ 7 m/s, 90 %, 0.3 %). Both: walking jitter = gold walk at matched speed, arms ~0.08 rad, upright at speed (+1° / 4° at 1.0–1.5 m/s), height 0.50–0.51 m. Open: cruise speed ~1.3–1.4 m/s (2 m/s not reached; a steady faster gait likely needs more forward lean than the −5…+3° pitch band allows), cadence ~7 steps/s (gold 4.6).

## Soccer-match robustness plan (user picks: 1, 2, 3, 7; small vision noise)

Policy inputs unchanged (83). Order, one change per run from the previous best: v48 field surface + small vision noise → v49 contacts / bumps → v50 moving ball → v51 side kicks / quick shots. Every run keeps all earlier checks (accuracy, falls, posture per speed, arms / knees / feet, walking jitter per speed, caps, nominal-ball long-kick speed) plus a scenario test for its own feature. (The speed-vs-lean diagnostic was dropped: `TRUNK_PITCH_FAST_UPPER_DEG = None`.)

| v48 `stage3_v48` | v47 `model_8800` (resume) | training terrain: 60 % flat / 40 % gentle bumps (heights 0–2 cm, 5 mm steps, 0.2 m sample spacing; 16 m patches, 6 × 6) — play stays flat; foot friction 0.75–1.25 → 0.5–1.4; actor ball detection: 5 % dropout while in view and a per-episode 0–2 step (0–40 ms) delay (new `vision_dropout`, `vision_delay_steps`; rewards keep true visibility). Smoke test: lags spread evenly, 95 % of visible steps detected; v47/8800 on it fell in 20 of 512 envs in 10 s. **Collapsed at ~8848**: `walk_base_height` used the trunk's world height; on generated terrain some robots stood on raised ground (root z up to 0.87 m), the term spiked from −0.2 to −21.8 per episode at 8846, the adaptive learning rate fell to 1e-5 and episodes collapsed (illegal-contact terminations; NaN terminations only after). Stopped at ~8900 | any absolute-height term breaks on non-flat ground; cap squared penalties |
| v48b `stage3_v48b` | v47 `model_8800` (resume) | as v48, with `walk_base_height` measured above the robot's own lowest foot (+ 0.040 m foot-link height on flat ground, measured) and capped at 25 per step (10 cm outside the band) — running | — |

Baseline v47/8800 on the v48 conditions (bumps + vision noise, 1024 envs): 83 % within 20° (flat 90 %), quality 0.77, 1.18 goals, falls after 2 s 1.9 % (flat 0.3 %); with `--push-test 0.6` (base kicks ±0.6 m/s x, y and ±0.6 rad/s roll, pitch every 2–3 s): 78 %, quality 0.67, falls after 2 s 2.1 %. `eval_kick_loop.py` gained `--flat` (plane, no vision noise), `--no-vision-noise` and `--push-test V`.

v48b/9100 (1024 envs) vs v47/8800 (in brackets): bumps + vision 84 % within 20° (83), falls after 2 s 1.1 % (1.9), 0.96 goals (1.18), idle 8 % (5); push test 0.6: 80 % (78), falls 2.2 % (2.1), 0.89 goals (1.10); flat: 87 % (90), falls 0.1 % (0.3), 1.04 goals (1.23). Bumps without vision noise: 85 % / 1.02 goals (v47: 85 % / 1.24); vision noise costs v47 only 1.24 → 1.18 goals. So balance on bumps improved (illegal-contact terminations 0.34 → 0.27 in training), but every kick reward fell ~20 % — the policy itself became less productive and more hesitant, not the test conditions. Continuing to 9350; if goals do not recover, lower vision dropout (5 → 2 %) or keep only the friction change. v48b/9350: goals did not recover (0.95 on bumps and on flat, 2.8 kicks / ep); falls after 2 s 0.8 % on bumps (v47 1.9 %), 0.4 % flat; 85 % / 89 % within 20°. Not kept; stopped at ~9360.

| v48c `stage3_v48c` | v47 `model_8800` (resume) | as v48b but foot friction 0.7–1.4 (slippery 0.5 feet likely made the planted kick risky → caution) and vision dropout 2 % (delay 0–2 steps kept). `model_9100` (1024 envs): bumps + vision 86 % within 20°, 1.10 goals, falls after 2 s 1.3 %; flat 91 %, 1.11 goals, 0.5 %; push test 0.6: 81 %, 1.05 goals, 2.1 %. Recovers most of the productivity lost in v48b (goals 0.95 → 1.10) with similar balance gains | slippery feet (0.5) made the policy cautious |

**Ball frame mismatch (fixed in v49).** Training gave the ball in the trunk frame (full roll / pitch / yaw, origin ~0.5 m above the ball); runswift vision reports it in `base_link`, a level frame on the ground that turns with yaw only (brain publishes it with z = 0, RPY (0, 0, θ); the sim adapter likewise). A trunk lean of θ moved the training ball by ~h·sin θ (5° ≈ 4 cm, 10° ≈ 9 cm), swinging with every step. Measured on v48c/9100 in play: 3.9 cm mean / 6.5 cm p90 with the ball beyond 1 m, **4.7 cm / 8.7 cm within 0.6 m** — in the last steps before contact. Fix: the ball (actor, memory, critic, rewards using its direction) is now the world vector with z dropped, rotated by trunk yaw only, origin at the trunk's ground projection (to change if base_link sits between the feet). Same input dims; the runner already passes vision's base_link ball, so no runner change.

| v49 `stage3_v49` | v48c `model_9100` (resume) | ball in the level, yaw-only ground frame (matches runswift vision) — fine-tune, all other objectives held. `model_9400` (2 seeds): bumps 84 % within 20°, 0.91 goals, falls after 2 s 0.8 %; flat 89 %, 0.97 goals, 0.2–0.5 %; 2.65 kicks / ep, near-ball time 2.8–3.0 s (v48c/9100: 86 % / 1.10, 91 % / 1.11, 3.2 kicks, 2.6 s) — re-learning close-range positioning after the ~5–9 cm shift in the near-ball reading; training falls 0.34 → 0.42 per episode (watch). `model_9650` (seed 1): bumps 88 % within 20°, 0.96 goals, falls after 2 s 0.8 %; flat 91 %, 0.88 goals, 0.1 %; 2.3–2.5 kicks / ep, near-ball time 2.9–3.0 s. Nominal ball, flat (vs v48c/9100): 1468 kicks counted (2070), long kicks 5.34 m/s mean / p90 8.76 (4.50 / 7.39), medium 3.97 (3.20), 13.6 % of kicks ≥ 7 m/s (4.5 %), swing p50 3.95 / p90 6.27 (3.24 / 5.28) — fewer, much stronger kicks (weak taps gone); slower setup is the cost. `model_9900`: productivity back (3.1 kicks / 1.0 goals, near-ball time 2.6–2.7 s), 87 % (bumps) / 92 % (flat) within 20°, falls after 2 s 0.9 / 0.3 %, arms 0.106 (up from 0.084); but nominal-ball long kicks 3.98 m/s (p90 6.82) — the swing stayed fast (p50 4.05 m/s) while ball / foot speed fell 1.16 → 0.93: off-centre strikes, since long_kick_power paid swing speed whether or not it reached the ball. Stopped at ~9910 | **frame-correct robot candidate: v49/9900** (`k1_kick_loop_v49_model_9900.onnx`); swing reward needs a transfer term |
| v50 `stage3_v50` | v49 `model_9900` (resume) | (1) contacts: general pushes ±0.28 → ±0.5 m/s (x, y; the AMP walk's level), new `push_near_ball` (within 1 m of the ball, 30 % chance every 0.5–1 s, ±0.4 m/s x, y, ±0.3 rad/s roll, pitch); (2) `long_kick_power` × clamp(ball speed / (0.9 × swing speed), 0, 1) — only swings that transfer into the ball pay — running | — |

Process note: v48c was left training in parallel after v49 was launched from its 9100 checkpoint (~2 h), halving the speed of v49 and v50; stopped at v50's start. Results are unaffected (each run's checkpoints are separate), only wall-clock time.

v50/10150 (seed 1) vs v49/9900: push test 0.6 falls after 2 s **1.9 % (5.1 %)**, 79 % within 20° (80 %); nominal-ball long kicks **4.87 m/s, p90 8.04 (3.98 / 6.82)**, 8.7 % of kicks ≥ 7 m/s (3.5 %), swing p50 3.91; but bumps 82 % / 0.88 goals (87 % / 1.01), flat 86 % / 0.82 (92 % / 1.00), near-ball time 2.9–3.1 s (2.6–2.7) — the usual post-change dip; both v50 goals (push recovery, strike transfer) met.

**Robot log `robot_data/walk_no_kick.txt` (2026-10-03, a mid-training v50 ONNX):** walked 5.2 m → 0.30 m to the ball (detected throughout, age ≈ 0.99), then stood still for ~6 s with the ball at (0.30, 0.06) m and never swung. Obs joint slots 0, 1, 2, 6 (head yaw / pitch, shoulder pitches) = 0.000: the runner read `/joint_states` without `--joints-from-low-state` (IMU from `/imu/data`). Reproduced in the runner sim with v50/10400 and the same settings (range long, heading −11°, caps 1.1 / 1.0 / 1.0, 3 trials per start): correct joints → kicks in every trial (first after 0.66 s from 0.30 m; 6 and 9 kicks from 1.5 m and 3.0 m); those four joints zeroed → **0 kicks, standing next to the ball** from every start. Cause: the zero-joint input bug (head pitch reads 0 where training always has it pitched down near the ball). Fix: the runner on branch `kick` + `stash@{0}` with `--joints-from-low-state`; check that `obs joint_pos` slots 0, 1, 2, 6 are non-zero at start-up.

v50/10400 (seed 1): push test 0.6 falls after 2 s **0.7 %** (v49/9900 5.1 %); but flat 86 % within 20° / 0.77 goals (92 % / 1.00), bumps 82 % / 0.83, idle at far balls 11 % on bumps, near-ball time 3.0–3.3 s — robust but cautious; not kept. Stopped at ~10470.

| v50b `stage3_v50b` | v49 `model_9900` (resume) | strike-efficiency term kept; milder contacts: general pushes ±0.4 m/s (v50 ±0.5), `push_near_ball` prob 0.15, ±0.3 m/s (v50 0.3, ±0.4). `model_10200` (seed 1): bumps 81 % / 0.95 goals, flat 85 % / 0.89, push test late falls 3.3 % (v49 5.1, v50 0.7), long kicks 4.77 m/s (p90 7.58). Accuracy dropped on flat without pushes too — like v50 — so the shared strike-efficiency term is a suspect. Stopped at ~10240 | — |
| v50c `stage3_v50c` | v49 `model_9900` (resume) | attribution: strike-efficiency term only, contacts back to the original (pushes ±0.28, no near-ball bumps; `CONTACTS_V50 = False`). `model_10200` (seed 1): flat **91 %** within 20° (v49 92 %), bumps 84 % (87 %), 0.91 goals (1.00), 2.46 kicks, near-ball time 3.1 s (2.7), falls after 2 s 0.1–0.2 %; long kicks 4.83 m/s (p90 8.01). Stopped at ~10250 | the pushes cost most of the accuracy (v50b flat 85 %); the efficiency term buys ~+20 % long-kick power for ~0.4 s slower setup |
| v50d `stage3_v50d` | v49 `model_9900` (resume) | strike efficiency 0.9 → 0.7; contacts back on, milder: pushes ±0.35 m/s, near-ball bumps 10 %, ±0.25 m/s. Pass: accuracy / goals within ~3 % of v49/9900, push-test late falls clearly < 5.1 %, long kicks > 4.3 m/s. `model_10200` (seed 1, vs v49/9900): bumps 86 % within 20° / 0.97 goals (87 % / 1.01), late falls 0.9 %; flat **91 % / 0.98** (92 % / 1.00), late falls 0.0 %; push test 0.6: 81 %, late falls **1.8 %** (5.1 %); 2.9 kicks / ep, near-ball time 2.8 s; nominal ball: long kicks **4.40 m/s, p90 7.48** (3.98 / 6.82), 7.5 % of kicks ≥ 7 m/s, swing p50 4.10. Posture: jitter per speed 0.142 / 0.160 / 0.178 / 0.200 (unchanged); height 0.504–0.514 m; arms 0.102 rad; knee gap p10 0.160 m; **but pitch at 1.0–1.5 m/s +2.2° mean / 5.1° p90 (v47 +1.0 / 4.1) and heel-up 31 % at 1.0–1.5 m/s, 22 % at 0.8–1.0 m/s** (5.6 % overall) — leaning forward and running on the toes at speed. Passed; stopped at ~10215 | **pick 1 (contacts) done: v50d/10200** — robust to pushes at v49's accuracy; lean at speed regressed |
| v51 `stage3_v51` | v50d `model_10200` (resume) | pick 2, moving ball (`MOVING_BALL_V51 = True`): ball spawns rolling at 0–1.5 m/s; `ball_nudge` (every 3–6 s, 50 %, 0.5–1.5 m/s, only to a ball at rest > 2 s after a kick); plus `trunk_pitch_band` −0.5 → −1.0 against v50d's lean at speed. Judge with `--moving-ball` plus all earlier checks. `model_10450` (seed 1; the base cfg now carries the moving ball, so every eval mode had it — compared with v50d/10200 on the same cfg in brackets): bumps 82 % within 20° (82), **0.68 goals (0.93), 2.17 kicks (2.78), idle at far balls 31 % (10)**; flat 89 % (88), 0.73 goals (0.94), idle 22 % (2); push test late falls 2.7 %; nominal-ball long kicks 4.01 m/s (p90 6.67); pitch at 1.0–1.5 m/s +2.4° / 5.4°, heel-up 49 % (the −1.0 pitch weight did not fix the lean). Training: kick_direction per episode 0.33 → 0.24 and walk_speed 0.95 → 0.75 over 400 iterations — a steady drift, not a dip. Stopped at ~10610 | random-direction nudges of any ball (often out of view, and the ball memory has no odometry) taught the policy to stand and wait |
| v51b `stage3_v51b` | v50d `model_10200` (resume) | milder moving ball: rolling spawn 0–0.8 m/s; `ball_nudge` only of a ball in view (`require_in_view`), 30 %, 0.3–1.0 m/s; pitch weight back to −0.5 (one change at a time). Judge against v50d/10200 evaluated on the same cfg. `model_10450` (seed 1, v50d/10200 on the v51b cfg in brackets): bumps 86 % within 20° (84), 0.87 goals (0.95), idle 9 % (8), late falls 0.3 % (0.5); flat 91 % (90), 0.93 goals (0.98), idle 2 % (2); push test 79 %, late falls 1.1 %; nominal-ball long kicks **3.94 m/s, p90 6.73 (v50d 4.40 / 7.48)**, swing p50 3.81 (4.10); pitch at 1.0–1.5 m/s +2.6° / 5.5°, heel-up 37 %. Training kick_direction 0.357 → 0.283 over 300 iterations (slower drift than v51) | waiting habit gone once nudges only hit visible balls; power and goals still below v50d |

v51b/10700 (seed 1; v50d/10200 on the same cfg in brackets): bumps 83 % within 20° (84), 0.82 goals (0.95), 2.30 kicks (2.82), idle 11 % (8); **flat 85 % (90), 0.77 goals (0.98)**; push test 78 %, late falls 1.0 %; moving-ball 82 % / 0.81 goals; nominal-ball long kicks 4.83 m/s, p90 7.61 (recovered); pitch at 1.0–1.5 m/s +2.3° / 5.3°. Failed (accuracy and goals fell further); stopped at ~10720. **Pick 2 closed without a new model:** v50d/10200, never trained on a moving ball, already handles the mild one nearly as well as a static ball (0.95 vs 0.97 goals on bumps, 90 vs 91 % on flat), and training on it cost accuracy. `MOVING_BALL_V51 = False`; `eval_kick_loop.py --moving-ball` now uses the v51b settings (0–0.8 m/s starts, nudges of a ball in view, 0.3–1.0 m/s, 30 %).

**v50d/10200 exported** as `k1_kick_loop_v50d_model_10200.onnx` (config restored to v50d before export). Runner sim (`sim2real_bench.py`, vs v49/9900): trunk tilt mean / p90 2.5° / 4.4° (2.9 / 6.5), trunk angular rate p90 65 °/s (76), walking jitter 0.078 (0.076), kicking jitter 0.136 (0.118), no falls, no torque saturation, joint speeds ≤ 45 % of the limits, heel-up 0.1 % (0.8), arms 0.084 (0.096), 2.9 kicks per run (5.4 — fewer, stronger kicks, as in training). **New robot candidate: v50d/10200** (`--joints-from-low-state`).

| v52 `stage3_v52` | v50d `model_10200` (resume) | pick 7, side kicks / quick shots (`SIDE_KICKS_V52`): new `side_aware_angle` folds alpha and yaw error so standing beside the kick line facing the ball (±90°) counts as lined up, +0.2 rad (wedge, `approach_align`, `approach_close`, heading potential, lined-up bonus, bad contact, style gate all use the folded values); 25 % of episodes are side drills (ball 0.4–1.0 m ahead, target 60–110° to the side). Outcome rewards unchanged. Also: the spawn-time ball memory now uses the yaw-only frame (was full trunk orientation, missed in v49; tiny at reset). Eval: `--side-drill` (every episode a drill). `model_10450` (seed 1, v50d/10200 in brackets): bumps 87 % within 20° / 0.99 goals (86 / 0.97), late falls 0.3 % (0.9); flat 91 % / 0.92 goals (91 / 0.98; 2.14 kicks vs 2.71); push test 80 %, late falls 0.7 % (1.8); moving ball 85 % / 0.96; side drill 83 % / 0.98 goals (82 / 0.97), near-ball time 2.81 s (2.69); nominal-ball long kicks **5.03 m/s, p90 8.05 (4.40 / 7.48), 10.4 % of kicks ≥ 7 m/s (7.5)**; pitch at 1.0–1.5 m/s **+0.9° / 3.8° (+2.2 / 5.1)**, heel-up 32 %, height 0.509–0.519 m (0.504–0.514). **But no side kicks yet** (`side_probe.py`, side drills): ball launched > 45° off the body heading in 3.4 % of kicks (v50d 2.6 %), > 70° 1.2 % (0.4), and those hit within 20° only 6 % of the time (front kicks 77 %) — the policy still turns and kicks forward; relaxing the alignment terms alone does not make it discover a side kick. `model_10700`: bumps 87 % / 0.89 goals, flat 92 % / 0.90, push late falls 1.5 %, side drill 85 % / 0.94; long kicks 4.58 m/s (p90 7.30), pitch at 1.0–1.5 m/s +2.0° / 4.7°; side kicks still 2.5 % of kicks. Stopped at ~10710 | 10450's power and posture gains were partly checkpoint luck; side kicks need a direct incentive |
| v52b `stage3_v52b` | v52 `model_10450` (resume) | new `side_kick_bonus` (400): per short / medium kick, ramp of the ball's launch angle off the body heading (0 at 30°, 1 at 60°) × aim² × kick quality — only aimed, well-struck side kicks pay. Judge with `side_probe.py` (side-kick share and their accuracy) plus all checks. `model_10700` (seed 1; v50d/10200 in brackets): bumps 85 % / 0.95 goals (86 / 0.97), late falls 0.7 % (0.9); flat 89 % / 0.91 (91 / 0.98), late falls 0.0 %; push test 80 %, late falls 1.5 % (1.8); moving ball 86 % / 0.94; side drill 84 % / 0.97, near-ball time 2.83 s; nominal-ball long kicks **5.13 m/s, p90 8.30, 12.7 % of kicks ≥ 7 m/s** (4.40 / 7.48 / 7.5); walking height **0.509–0.525 m** (0.504–0.514), pitch at 1.0–1.5 m/s +1.5° / 4.4° (+2.2 / 5.1), heel-up 33 % (31). Side kicks: 3.5 % of drill kicks > 45° off the heading (v52 2.5–3.4), their accuracy 18 % within 20° (6–11) — learning, slowly; bonus per episode 0.003 → 0.010. `model_11200`: side kicks 3.4 %, their accuracy back to 11 %, bonus falling (0.011 → 0.007); 2.25 kicks / 0.88 goals (bumps), flat 93 % / 0.88, long kicks 5.01 m/s, pitch +2.2° / 5.2°. Stopped at ~11400 | **side kicks are not discovered by reward shaping here** (relaxed alignment + aimed side-kick bonus: ~3 % of kicks, ≤ 18 % accurate); a side-kick motion reference (the user's kick motion data) is the likely route |

Seed 2 (v50d/10200 vs v52b/10700): bumps 86 % / 0.94 vs 86 % / 0.96; flat 88 % / 0.93 vs 88 % / 0.89. Two-seed means: bumps tie (86 / 0.96 both); flat 89.5 % / 0.955 vs 88.5 % / 0.90, near-ball time 2.8 vs 3.0 s. v52b/10700 exported (`k1_kick_loop_v52b_model_10700.onnx`). Runner sim vs v50d/10200: walking jitter **0.088 (0.078; gold walk 0.083)**, trunk tilt p90 **5.9° (4.4)**, arms **0.122 rad (0.084)**, kick jitter 0.135 (0.136), 2.9 kicks / run each, no falls, no saturation, knee speed p99 48 % of limit.

**Standing after picks 1, 2, 3, 7:**
- Robot candidate stays **v50d/10200** — smoothest and most upright in the runner sim, accuracy / goals best.
- **v52b/10700** — strongest kicker (nominal-ball long kicks 5.13 m/s, p90 8.30, 12.7 % ≥ 7 m/s), walking height on target (0.51–0.525 m), but rougher in the runner sim (jitter, tilt, arms) and ~6 % fewer goals on flat.
- Pick 2 (moving ball): v50d already copes; training on it cost accuracy. Pick 7 (side kicks): not learned without a motion prior. Picks 1 (contacts) and 3 (surface + small vision noise): in v50d.
- Open: lean / heel-up at 1.0–1.5 m/s (+1.5–2.2° mean; v47 +1.0°), cruise speed ~1.3–1.4 m/s, long-kick mean ~5 m/s vs 7–8 target, cadence ~7 steps/s.

| v53 `stage3_v53` | v50d `model_10200` (resume) | lean fix: `TRUNK_PITCH_BAND_DEG` upper edge +3° → +1° (weight −0.5 kept). v50d's +2.2° mean at 1.0–1.5 m/s sat inside the old band, so only the tail paid — which is why v51's doubled weight did nothing. Side-kick settings off (`SIDE_KICKS_V52 = False`, bonus weight 0). Pass: pitch at 1.0–1.5 m/s mean ≤ +1°, accuracy / goals within ~3 % of v50d, walking speed and runner-sim smoothness held. `model_10450` (seed 1, v50d/10200 in brackets): **pitch at 1.0–1.5 m/s +0.4° / 2.9° (+2.2 / 5.1)**, 0.8–1.0 m/s −1.0° / 1.4°, heel-up at 1.0–1.5 m/s 31 % (31), height 0.502–0.517 m; flat 90 % / 0.96 goals (91 / 0.98), late falls 0.0 %; bumps 86 % / 0.91 (86 / 0.97), **late falls 1.6 % (0.9)**; push test 80 %, late falls 1.5 % (1.8); 2.9 kicks / ep, near-ball time 2.74 s; nominal-ball long kicks 4.15 m/s, p90 7.13 (4.40 / 7.48) | the band edge, not the weight, sets the lean |

v53/10700 (2 seeds; v50d/10200 two-seed means in brackets): **bumps 87.5 % within 20° / 1.02 goals (86 / 0.96)**, late falls 1.0 % (0.95); **flat 91.5 % / 1.05 (89.5 / 0.96)**, late falls 0.1 %; push test 81 % / 0.95, late falls 2.2 % (1.8, one seed); moving ball 86 % / 0.97; side drill 84 % / 1.03; nominal-ball long kicks **5.18 m/s, p90 8.22, 10.7 % ≥ 7 m/s** (4.40 / 7.48 / 7.5); pitch at 1.0–1.5 m/s **+0.7° / 3.5°** (+2.2 / 5.1), 0.8–1.0 m/s −0.5 / 2.0; height 0.504–0.520 m; heel-up at 1.0–1.5 m/s 31 % (unchanged). Runner sim (`sim2real_bench.py`, now also printing pitch / roll split walking vs near the ball): walking jitter **0.073** (v50d 0.078, gold walk 0.083, v47 0.097), walking pitch mean −1.6° (−0.8), pitch sd 1.11° (1.25), roll sd 1.64° (1.68); near the ball pitch sd 4.8° (3.4), roll sd 3.4° (2.9), tilt p90 7.7° (4.4), angular rate p90 85 °/s (65; v47 82) — the extra tilt is the harder kick swing (as v47), not walking wobble; kick jitter 0.098 (0.136); no falls, 2.9 kicks / run. Exported `k1_kick_loop_v53_model_10450.onnx`, `k1_kick_loop_v53_model_10700.onnx`. **New best / robot candidate: v53/10700.** Watch: push-test late falls slightly up, heel-up at speed unchanged.

v53/11200: past the peak — 2.2–2.3 kicks, 0.83–0.88 goals, flat 93 % within 20°, near-ball time 3.1–3.3 s, long kicks 4.69 m/s (p90 7.50), pitch at 1.0–1.5 m/s 0.0° / 2.9°. Stopped at ~11400. **Pattern across v50d, v51b, v52, v52b, v53:** the best checkpoint comes ~250–500 iterations after a resume; by ~1000 the policy drifts to fewer, slower, slightly more accurate kicks (caution). Evaluate every 250 iterations and keep the peak rather than training long.

Heel-up at 1.0–1.5 m/s (~31 % of contact samples > 5°, every model since v47) is likely early heel lift at toe-off when walking fast; the runner sim (low caps) shows 0.1–0.3 %. Not chased further without robot evidence.

Training reward curves swing ±15 % over a few hundred iterations without meaning much: v50d's `kick_direction` went 0.35 → 0.30 → 0.34 and was the best model; judge by evals, not by a 300-iteration slope. (Stage-3 curricula are only `amp_style_weight`, fixed at 0.3, and a constant soft-landing weight, so the "no curriculum state" warning on resume changes nothing here.)

**Current robot candidate: v31 `model_5450`** (config = v31: pose terms beyond 1 m,
style 0.3). Two seeds × 1024 vs v28/4400: within 20° 90 vs 90%, goals 1.24 vs
1.2, kicks 2.27 vs 2.07, quality 0.815 vs 0.85, ball speed 3.40 vs 3.72 m/s,
falls after 2 s 0.25 vs 0.0%, idle 1 vs 1%. Runner sim vs v28/4400: jitter
2.6× vs 2.9× (walking 0.076, gold walk 0.083), 6.2 vs 6.9 steps/s, roll sd
1.26 vs 1.94°, trunk ang. rate 56 vs 63 °/s, base 0.514 vs 0.481 m, knees
0.88 vs 1.21 rad, stance 0.17 vs 0.25 m, no knock-knee, heel-up 0.1 vs 0.8%,
no falls, kicks every start (2.8 vs 3.75 per run).

## Issue — posture and head (v18–v20)

On the robot v17/v18 shook. Measured in the runner's own MuJoCo with
`k1_policy_runner/python-implementation/sim2real_bench.py` against the gold
walk (`k1_velocity_amp_symmetric_muon_wwcmu50_roughft/2026-09-21_20-34-24_stageA/model_9950`):

| | jitter ×ref | Δq mean ×ref | knee gap mean / p10 | arm dev rms | head pitch |
|---|---|---|---|---|---|
| gold walk | 1.0 | 1.0 | 0.184 / 0.174 m | 0.067 rad | +0.01 |
| v18 | 13.4 | 6.3 | — | — | — |
| v19 `2300` | 2.1 | 2.1 | — | — | — |
| v20 `2350` (policy head) | 5.6 | 4.3 | 0.169 / 0.145 m | 0.42 rad | −0.17 |

(v20 bench with the real camera's vertical FOV; one in three runs fell.)

The head drifted to the upper pitch limit because nothing in the reward
pointed the camera; the user also needs to steer the head on the robot.

**v21 fixes:**
- Scripted head (`HeadTrackedJointPositionAction`): the head looks at the
  actor's ball estimate (slots 72–73, seen or remembered), low-pass 0.3 and at
  most 0.06 rad per step, yaw ±0.85, pitch −0.25…0.75 (+ = down). The policy
  still outputs 22 actions; its head outputs are ignored. In 20 % of training
  episodes the head sweeps instead (±0.8 rad, 4 s), so the policy copes with
  a head it does not control. The runner's `KickLoopPolicy` has the same
  tracker (`--kick-head track|fixed|policy`, `set_head_target()`).
- Real camera: CAM_ANGLE_X/Y = 1.211 × 0.733 rad full FOV → half-angles
  0.606 / 0.367. Camera pitch relative to the head link assumed 0 (to check).
- Posture: `knee_gap` −2 × ((0.16 − gap)/0.02)² below 0.16 m; `arm_pose`
  −2 × Σ(shoulder, elbow deviation)².
- CAPS 0.5 / 0.2.

v21 then walked on its toes (see the run log); v22 adds `foot_flat`
(−30 × sole pitch² while that foot touches the ground). `sim2real_bench.py`
now reports stance sole pitch and the heel-up share, plus jitter split into
walking (ball > 1 m) and kicking.

Acceptance needs all three together: kick eval (`eval_kick_loop.py`, which now
also prints knee gap, arm deviation, head pitch and ball-in-view), posture
within ~10 % of the gold walk, and `sim2real_bench.py` jitter ≤ 2×, Δq mean
≤ 1.5×.

## Issue — on the robot the head looks too high and kicks are late

Robot test of v22/v25 (2026-10-02): the head did not look down enough, the
robot did not kick soon when the ball was near, and it was slow.

Cause: the ball memory. In training the out-of-view ball was carried with
the robot's true motion (privileged odometry); the runner has no odometry and
only turns the last sighting by the IMU yaw change. On the robot the remembered
ball stayed where it was last seen (say 0.8 m) while the robot walked onto it,
so the tracker aimed too far (too high) and never found it again, and the
policy, believing the ball farther, crept instead of kicking. Evaluated with the
robot's memory, v25/3650 saw the ball 47 % of the time (82 % before), hit 48 %
within 20° (97 %) and needed 4.2 s near the ball to kick (2.7 s). Slowness was
also the speed limits suggested for the robot (0.5, 0.3, 0.6: low end of the
trained 0.3–1.2 / 0.2–1.0 / 0.4–1.25).

**v27 fixes** (training and runner identical, checked numerically):
- `memory_odometry=False`: training memory = last sighting turned by the yaw
  change, as the runner does.
- Head aims 0.18 rad below the ball (ball in the upper image, stays in view
  to ~0.3 m); pitch limit 0.75 → 0.82 (joint 0.855).
- Head search: unseen for 0.5 s → yaw sweep ±0.8 rad (3 s) with pitch
  0.55 ± 0.2 (1.5 s) until the ball is seen; also before the first sighting.
- Kick promptness: kick_direction and kick_vel × (0.5 + 0.5·exp(−near time /
  1.5 s)). A multiplier, not a time cost (v1 lesson).
- `foot_flat` −200 (heel lift was in normal walking, p50 0.7°, p90 8.8°).

`eval_kick_loop.py` also reports the idle share at a far ball and heel-up
while walking.

## Issue — the kick policy walks crouched, wide and fast (v28)

`k1_policy_runner/python-implementation/gait_bench.py` compares walking only
(kick models: ball > 1 m, moving) with the gold walk at matched speed. v28/4400
vs the gold walk: base 0.48 vs 0.54 m, knees 1.21 vs 0.41 rad, feet 0.25 vs
0.15 m apart with the knees inside the feet (knock-knee; the knee gap alone
looked normal), 6.9 vs 4.8 steps/s, trunk pitch sd 2.2 vs 0.2°, angular rate
63 vs 36 °/s. Leg action jitter while walking was the same (0.085 vs 0.084):
the "3×" in `sim2real_bench.py` compares the kick against a reference that
includes standing. The stage-2 approach policy still walked like the gold walk,
so stage 3 caused it: no velocity tracking, large kick events, fall penalties
and pushes favour a low, wide, quick-stepping stance; style (0.3) is weak and
gated off near the ball; no term fixed height, width or cadence.

## Watch

- `Metrics/twist/kicks`, `goals`, `kick_dir_err` ↓, `kick_speed`,
  `near_time_to_kick` ↓, `double_touches` ↓, `push_time` ↓.
- `Episode_Termination/illegal_contact`: falls rose from about 0.1 to 1.3 per
  log once kicking started in the smoke run. Post-kick stability is the main
  risk.
- `Episode_Reward/action_rate_l2` is the largest penalty (kicks are abrupt).
  Watch that it does not suppress kicking.

## Side kicks — what a motion reference would need (checked 2026-10-03)

The only kick motion in the workspace is `RoboNaldo/motions/right_kick.npz` (and its source `right_kick_reference.csv`): a **right-foot front push kick for the 29-joint Unitree G1** (RoboNaldo's G1 tracking task; root ~0.77 m), 612 frames at 50 Hz, retargeted from human video with GVHMR + GMR. It is neither a K1 motion (22 joints) nor a side kick. (`robot_data/joint_log_kick1.npz` is a corrupt archive — zlib error on read.)

So a side-kick prior needs a new clip: a human side-kick / inside-foot pass video → GVHMR (human motion) → GMR retarget to the K1 → K1-format clip, then a near-ball style discriminator (or tracking term) for it alongside the walking AMP data, gated like the current near-ball style switch. Reward shaping alone (v52, v52b) gave ~3 % side kicks, ≤ 18 % accurate. The front-kick G1 clip could be retargeted G1 → K1 for a kick-style prior, but our kicks are already accurate and strong, so it would mainly change style, with risk to power.

## Short-kick overshoot and slow setup (user check of v53/11400, 2026-10-03)

`range_hesitation.py` (flat, nominal ball, no pushes / vision noise), per kick range:

| | v50d/10200 | v53/10700 | v53/11400 |
|---|---|---|---|
| short (needs ~2.2 m/s): actual, median × needed, over 2× | 4.22 m/s, 2.0×, 50 % | 3.77, 1.8×, 40 % | 4.01, 1.9×, 47 % |
| medium (needs ~3.3): actual, median ×, under 0.7× | 4.16, 1.3×, 23 % | 3.66, 1.1×, 26 % | 3.78, 1.2×, 27 % |
| long (needs ~5.0): actual, median ×, under 0.7× | 4.73, 0.9×, 35 % | 4.98, 1.1×, 32 % | 4.63, 1.0×, 36 % |
| wait inside 1.5 m before the kick (short / medium / long) | 3.4 / 3.5 / 3.2 s | 3.2 / 3.8 / 3.4 | 3.5 / 3.7 / 3.3 |
| share of near-ball time in waits > 3 s | 44–50 % | 45–47 % | 45–53 % |

v53/10700 rest position: short passes stop a median **5.5 m** (p90 9.7) from the target, 4 % within tolerance; medium 3.0 m (p90 5.9), 16 %.

Cause: the goal (1500) counts a ball **passing** the target, and the ball's mass / rolling resistance are randomized, so a soft kick at the needed speed often stops short (no goal) while a blast always passes; `kick_vel` (900) pays full at ≥ 3 m/s and the speed-match term (300) is too small to matter (≈ 945 vs 900 for 2.2 vs 4 m/s to a 2 m target). The near-ball wait is the same for every range (not a weak-kick issue) and is slow against the quick-kick objective.

| v54 `stage3_v54` | v53 `model_10700` (resume) | (1) `kick_vel` reference for short / medium = min(3 m/s, needed speed) (`KICK_VEL_CAP_AT_NEEDED`); (2) new `kick_rest_accuracy` (600): when a short / medium kick's ball comes to rest (< 0.1 m/s, > 0.5 s after the kick, no touch in between), exp(−(miss / goal tolerance)²) × that kick's quality, measured to the target at the kick. Long kicks unchanged. Pass: short passes stop closer (median miss ≪ 5.5 m, more within tolerance), short speed nearer 1× needed, long-kick power / accuracy / falls / posture held. `model_10950` (seed 1): short kicks 3.90 m/s, 1.82× needed (v53/10700 1.76×), short passes stop a median **6.3 m** from the target (5.5), 3 % within tolerance; medium 3.6 m (3.0); bumps 85 % / 0.94 goals, flat 91 % / 0.94, push test late falls **3.3 %** (2.2), long kicks 4.92 m/s (p90 7.60); speed at 1.6–2.0 m/s caps 0.78 m/s, 8 m chase 1.21 m/s. No change in passes. Stopped at ~11000 | **reward too sharp to learn from**: exp(−(miss / 0.5 m)²) is ~0 at the 5–6 m overshoots, and the speed match (Gaussian, σ = 0.25 × needed) is ~0 at 1.8× — no gradient from current behaviour (the v34 lesson again) |
| v54b `stage3_v54b` | v53 `model_10700` (resume) | dense versions: rest score exp(−miss / 2 m) (6 m → 0.05, 3 m → 0.22, 1 m → 0.61); short / medium speed match in `kick_vel_accurate` linear, 1 − \|speed / needed − 1\| (1.8× → 0.2); `kick_vel` capped at the needed speed kept. Rough per-kick value to a 2.2 m/s target: 1.1× ≈ 1640 vs 1.8× ≈ 980 (before the risk of stopping short with a heavy ball). `model_10950` (seed 1; v53/10700 in brackets): short kicks 3.41 m/s, **1.59× needed (1.76)**, over 2× 30 % (40); short passes stop a median **4.25 m** from the target (5.5), 8 % within tolerance (4); medium 3.1 m (3.0), 15 % (16); bumps 88 % / 0.94 goals, flat 90 % / 0.97, push test late falls 2.6 % (2.2); long kicks **4.66 m/s (5.18)**, p90 7.60, 6.2 % ≥ 7 m/s (10.7); pitch at 1.0–1.5 m/s +1.2° / 4.1° (+0.7 / 3.5), height 0.500–0.512 m; speed at 1.6–2.0 m/s caps 0.75, 8 m chase 1.09 | dense terms move the short passes; long power and height dipped (watch) |

v54b/11200 (seed 1): **flat 94 % within 20° / 1.12 goals, bumps 89 % / 1.08**, 3.3–3.4 kicks / ep, near-ball time **2.5 s** (v53/10700: 91.5 / 1.05, 87.5 / 1.02, 2.8 kicks, 2.8–3.0 s), push test late falls 1.7 %; short passes 1.52× needed, stop median 4.2 m, 9 % within tolerance; medium 1.19×, 3.4 m; **long kicks 3.95–4.10 m/s, median 0.74× needed, 47 % under 0.7× (v53/10700 5.18, 1.08×, 32 %)**, 4.1 % ≥ 7 m/s; pitch at 1.0–1.5 m/s +1.0° / 3.8°, heel-up 28 %; 8 m chase 1.17 m/s. The new terms exclude long kicks (checked: rest score and kick_vel cap gate on the range at the kick), and the training `long_kick_power` reward is level with v53's (~0.25 / episode) — the nominal-ball long-kick drop (4.66 → 4.10 → 3.95 over 10950 → 11200) is not a mis-gated reward; most likely the softer short-pass kick bleeding into long kicks (the range input is a small one-hot), unconfirmed.

v54b ended at ~11425 when the session closed (no 11450 checkpoint; 11400 not evaluated).

| v54c `stage3_v54c` | v54b `model_11200` (resume) | new `long_kick_underpower` (−800): per long kick, (1 − speed / (0.8 × needed)) clamped to 0–1 — a long kick at half the needed speed costs ~300. Everything else as v54b. Pass: long kicks back to ≥ 5 m/s (nominal ball), ≥ 1× needed median, while keeping v54b/11200's accuracy (flat 94 % / 1.12 goals), quick kicks (2.5 s) and short-pass progress. `model_11450` (seed 1; v54b/11200 / v53/10700 in brackets): **long kicks 5.83 m/s mean, p90 9.56, 1.16× needed, 13.1 % of all kicks ≥ 7 m/s** (4.10 / 5.18; 4.1 / 9.3–10.7 %), foot speed p90 6.45 (5.45); short passes 1.64× needed, stop median **3.78 m** from target (4.2 / 5.2), medium 1.06×, 2.47 m (3.4 / 3.0); flat 93 % within 20° but **0.98 goals** (94 / 1.12; 91.5 / 1.05), bumps 87 % / 0.93 (89 / 1.08), near-ball time 2.83 s (2.5) — the quicker kicking of v54b/11200 is gone; late falls bumps 1.6 %, push test 2.0 %; pitch at 1.0–1.5 m/s +0.2° / 3.2°, but height there 0.497 m and heel-up 38 %; caps unused (0.66 m/s at 1.6–2.0 m/s caps). — running | the penalty restored long power (best ever) and passes kept improving; goals and quickness fell back |

v54c/11700: **regressed** — bumps 78 % within 20° / 0.69 goals, flat 85 % / 0.78, push-test late falls 6.4 %, long kicks 4.74 m/s (0.94× needed), long kicks counted 555 → 454, near-ball wait 3.5–4.1 s, pitch at 1.0–1.5 m/s +1.7° / 5.1°, heel-up 44 %. Training: illegal-contact terminations 0.28 → 0.47 per episode around 11600–11700; the underpower penalty stayed ~−0.12 / episode (a quarter of the goal reward). Stopped at ~11890. Reading: a penalty on bad kicks makes *not kicking* the safe option — the policy hesitated and fell more, the same trap as zone-tied time costs in stage3_v1.

| v54d `stage3_v54d` | v54c `model_11450` (resume) | `long_kick_underpower` −800 → −300; everything else as v54c. Keep 11450's long power with less pressure to avoid long kicks. `model_11700`: short passes regressed (1.97× needed, stop 6.1 m off), long 5.04 m/s (1.02×), flat 93 % / 0.94 goals, bumps 89 % / 0.89, height 0.51–0.53 m, pitch at 1.0–1.5 m/s −0.4°. Not better than v53/10700 or v54c/11450; stopped at ~11720 | — |

## Real robot: v53 kicks weaker, more air balls (user report, 2026-10-05)

On the robot v53/10700 kicks more often, but the ball's forward speed is lower and more kicks are air balls. New probe `kick_probes.py CK loft` (flat, nominal ball; ball state 2 steps after the kick, peak height over the next 0.8 s):

| Model | launch angle p50 / p90 | long kicks: peak height p50 / p90 | long > 5 cm | long > 15 cm | short / medium > 5 cm |
|---|---|---|---|---|---|
| v50b/10200 | +3.7° / +10.6° | 3.6 / 16.2 cm | 43 % | 11 % | 21 / 26 % |
| v50d/10200 | +3.4° / +10.1° | 1.5 / 8.7 cm | 19 % | 4 % | 26 / 39 % |
| **v53/10700** | **+5.8° / +15.5°** | **11.6 / 37.8 cm** | **73 %** | **41 %** | 32 / 34 % |
| v54c/11450 | +3.5° / +13.0° | 3.3 / 28.5 cm | 40 % | 21 % | 24 / 25 % |

The sim reproduces the report: v53 lofts its long kicks. Every kick-speed reward and metric used the ball's **horizontal** speed at launch, so lofted kicks scored as fast; in sim a lofted ball lands and rolls on, while on the robot it bounces and its forward speed was lower. Likely tied to v53's lean fix (trunk further back → foot under the ball), not verified.

| v55 `stage3_v55` | v54c `model_11450` (resume) | loft fix: `loft_factor(launch angle)` = 1 at ≤ 5°, 0 at ≥ 20°, linear — multiplies `kick_vel`, the long branch of `kick_vel_accurate` and `long_kick_power` (goal reward unchanged, so lofting is never penalised, only unpaid). Underpower penalty −300 (as v54d). Pass: long air balls (> 5 cm) ≤ v50d's ~20 %, launch angle p90 ≤ ~10°, long-kick ground speed ≥ v53, accuracy / goals held. `model_11700` (seed 1): **air balls gone — launch angle p50 +1.3° / p90 +4.8° (v53 +5.8 / +15.5), long kicks > 5 cm 3 % (73), > 15 cm 0 % (41), short / medium 0 %**; flat 93 % / 0.93 goals, bumps 89 % / 0.93, late falls 0.0–0.5 %, push test 1.5 %; but long kicks 4.16 m/s (p90 6.73), 0.82× needed, 2.6 % of kicks ≥ 7 m/s (v54c/11450 5.83, lofted 40 %); short passes back to 1.74× / 5.7 m off (v54c 1.64× / 3.8 m); pitch at 1.0–1.5 m/s +0.3°, height 0.505–0.519 m — running | the loft factor removes air balls at once; grounded long-kick power must be relearned (earlier speed numbers partly counted lofted balls) |

v55/11950 (seed 1): flat 91 % / **1.06 goals**, bumps 85 % / 1.00, **4.0 kicks / ep, near-ball time 2.4 s** (quickest yet), push-test late falls 0.7 %; short passes 1.51× needed, stop **3.1 m** off (13 % within tolerance), medium 2.5 m; air balls long 5 %, short / medium 0 %; but **long kicks 3.74 m/s, 0.71× needed, 50 % under 0.7×**, 1.3 % of kicks ≥ 7 m/s — quantity over power again; pitch at 1.0–1.5 m/s +0.8°, height 0.506–0.520 m; caps unused (0.72 m/s at 1.6–2.0). Stopped at ~12160.

| v55b `stage3_v55b` | v55 `model_11950` (resume) | `long_kick_power` 2000 → 3000 (the v47 lever), loft factor and everything else kept. Pass: grounded long kicks ≥ 1× needed median (≥ ~5 m/s), air balls stay ≤ ~5 %, keep 11950's goals / quick kicks / short passes, falls and posture held. `model_12200` (seed 1): long kicks 4.07 m/s, 0.80× needed (11950: 3.74, 0.71×), 41 % under 0.7×; flat **95 %** within 20° / 1.01 goals, bumps 90 % / 0.95, 3.5–3.6 kicks, near-ball 2.5 s, push late falls 1.7 %; short passes stop 4.0 m off (3.1), medium **2.0 m** (2.5), 27 % within tolerance; air balls long 8 %; pitch at 1.0–1.5 m/s +1.2° / 4.2°, height 0.503–0.515 m. Long power moving, not there. `model_12450`: **push-test late falls 7.9 %** (2.1 % within 2 s of a kick), bumps late falls 2.1 %, long kicks 4.11 m/s (stalled), short passes 2.7 m off (17 % within tolerance); flat 95 % / 1.02. Stopped at ~12660 | raising long power to 3000 bought +0.4 m/s and then cost push robustness |

v55b/12200, seed 2: bumps 91 % / 1.01 goals, late falls 0.3 %; flat 94 % / 1.09, 0.0 %; push test 85 % / 0.95, late falls 1.0 %. Two-seed means: **flat 94.5 % / 1.05, bumps 90.5 % / 0.98, push late falls 1.35 %**, near-ball 2.5 s. Exported `k1_kick_loop_v55b_model_12200.onnx`. Reference: v50d/10200 long kicks 4.63 m/s (0.92× needed) but 19 % of them lofted above 5 cm. Grounded long kicks appear to top out near ~4–4.5 m/s in this sim with this kick style; the 7–8 m/s goal is not reachable grounded so far. The runner-sim bench was not re-run: its scratch copy (branch `kick` + stash) was lost with the temp dir, and the user's runner checkout is on `main`.

**Robot candidate: v55b/12200** — no air balls (0 % short / medium, 8 % long > 5 cm, none > 15 cm), best accuracy (94.5 % flat), 1.05 goals, quick kicks (2.5 s), medium passes 2.0 m off, push robust. Weaker: long kicks 4.07 m/s grounded (0.80× needed), short passes 4.0 m off, lean +1.2° at 1.0–1.5 m/s, speed caps unused. Not runner-benched.

**Eval tooling moved into the repo (2026-10-05):** the scratch probes were lost when the session's temp dir was cleared. Rebuilt as `scripts/tools/kick_probes.py CK {range,lean,caps,chase,side}` and `scripts/tools/eval_kick_ck.sh RUN ITER [SEED]`. Check on v53/10700: `range` and `lean` reproduce the old numbers (long 5.18 m/s, short 1.78× needed, short passes stop 5.2 m off, pitch +0.7° at 1.0–1.5 m/s); `chase` reads 0.95 m/s vs the old 1.13 (different gating) — compare chase only within the new probe.

## Attack plan (docs/K1_KICK_ATTACK_PLAN.md) — Phase 1, search

Search probe (`kick_probes.py CK search`: every 6 s the ball is moved, unseen and at rest, 1.5–4 m away outside the view): v55b/12200 re-found it within 6 s **25 %** (median 4.0 s); while unseen 56 % walking forward (toward the stale memory), 20 % backward, 37 % turning. v50d/10200: 24 %, 61 / 16 / 32 %.

| v56 `stage3_v56` | v55b `model_12200` (resume) | memory invalidation (`memory_invalidate`): lost if the remembered spot is in the camera view (≤ 3 m) and nothing detected for 0.5 s, or nothing detected for 1.5 s (user: 1–2 s, not 4); while lost the actor gets ball (0, 0), age 0, the head does the far sweep; `search_turn` (+3: \|wz\| / wz cap, full toward the side last remembered, half the other way), `search_backward` (−5 per m/s); walk_speed and walk_speed_track off while lost; `ball_relocate_unseen` event (every 1 s, 10 %: an unseen resting ball is moved 1.5–4 m away, ≥ 1 rad off heading). Smoke (v55b/12200, ball moved behind): lost 78 % at 0.6 s, 100 % at 2.0 s, obs (0, 0, age 0). **Runner must mirror the rule** before deploying. Pass: re-found ≥ 70 % within 6 s, median ≤ 2.5 s, backward ≤ 5 %, turning ≥ 60 %, all else held. `model_12450` (seed 1, v55b/12200 in brackets): flat 90 % / 0.99 goals (94.5 / 1.05), bumps 85 % / 0.91 (90.5 / 0.98), push-test late falls **3.8 %** (1.35), near-ball 2.2 s (2.5), long 4.07 m/s, air balls long 4 %; search: re-found 30 %, backward **3 %**, but turning only 13 % (\|wz\| > half cap), mean \|wz\| 0.20 rad/s vs 0.95 cap — stopped walking back, did not learn to spin; walking speed at 1.6–2.0 m/s caps fell to 0.46. Training: lost ~22 % of the time. Stopped at ~12650 | the turn reward at +3 was too weak |

Search probe caveat: with `memory_invalidate` on in the base cfg, models trained before v56 see (0, 0, age 0) inputs they never trained on (v55b/12200 then walks backward 81 % of unseen time), so compare search results only from v56 on. The probe now reports \|wz\| against the episode's wz cap and the share of unseen time the memory was marked lost (~95 %).

| v56b `stage3_v56b` | v56 `model_12450` (resume) | `search_turn` 3 → 10, all else as v56. `model_12700` (seed 1): flat 94 % / 1.03 goals, bumps 91 % / 0.94, push-test 88 %, late falls **0.6 %**, near-ball 2.2 s, air balls long 9 %, long 3.78 m/s; search: backward 2 %, "turning" 58 %, mean \|wz\| 0.60 rad/s — but re-found still 31 %. Step trace: 3.7 rad of summed turning in 6 s while the ball's bearing stayed ~2.3 rad off the heading — **reward hacking: the policy wiggled its heading back and forth** (\|wz\| paid in both directions). Stopped at ~12920 | pay net rotation, not turning speed |
| v56c `stage3_v56c` | v56b `model_12700` (resume) | `search_turn` signed: clamp(wz × lost side / wz cap, −1, 1) — turning back costs what turning on paid, so wiggling nets zero. Search probe now also reports net heading change per search. `model_12950` (seed 1): wiggling gone, but no spin either — net heading change per search **0.34 rad**, mean \|wz\| 0.21 rad/s, re-found 31 %; flat 93 % / 0.96 goals, bumps 89 % / 0.94, push late falls 1.7 %, air balls long 13 %. Stopped at ~13170 | RL did not discover a steady spin from a turning reward |

Why every model re-finds at ~3.98 s: all envs are relocated at the same step, so their head sweeps are in phase; the only balls found are the ones the head sweep reaches (1.2–1.4 rad off heading), at the same sweep phase. Body turning has found nothing so far.

| v56d `stage3_v56d` | v56b `model_12700` (resume) | **virtual ball while lost** (`lost_virtual_ball`): instead of (0, 0) / age 0, the actor sees a ball 2 m away at 1.6 rad (≈ 92°) on the side last remembered, fixed in the body frame (age keeps decaying) — the existing turn-toward-the-ball skill does the search, and it keeps turning until the real ball is detected. Signed `search_turn` (+10) and `search_backward` (−5) kept. Untrained check (v56b/12700 with the virtual ball): net heading change per search 0.66 rad (0.34 with (0, 0)), turning > half cap 42 %. Runner rule: same virtual ball. `model_12950` (seed 1): **search working — net heading change per search 1.80 rad (v56c 0.34), re-found within 6 s 47 % (31), p90 5.4 s (finds now come from body turning, not only the head sweep)**, backward 8 %; flat **95 % / 1.04 goals**, bumps 90 % / 0.96, push test late falls 1.8 % (v55b 1.35), flat late falls 0.8 % (0.0 — watch), near-ball 2.4 s, air balls long 7 %, long 4.12 m/s, short passes 3.5 m off, medium 2.2 m; pitch at 1.0–1.5 m/s +0.6°. | the virtual ball lets an existing skill do the new job |

v56d/13200 (seed 1): search re-found **55 %**, net turn 1.84 rad; **grounded long kicks 5.46 m/s, 1.14× needed, 11.7 % of kicks ≥ 7 m/s**, air balls long 13 % > 5 cm, 0 % > 15 cm (best grounded power so far); late falls flat 0.1 %, push 1.3 %; but goals fell — flat 91 % / 0.85, bumps 90 % / 0.84, 2.4–2.6 kicks, near-ball 2.7 s, short passes back to 1.79× / 6.0 m off, medium 3.8 m. The power-vs-pass-control seesaw again (v54c/11450, v55/11950).

v56d/13450 (seed 1): balanced again — flat **95 % / 1.03 goals**, bumps 91 % / 0.99, 3.6 kicks, near-ball 2.2 s, late falls flat 0.2 %, push 1.7 %; long kicks 4.49 m/s (0.91×), 4.1 % ≥ 7 m/s, air balls long 11 % (0 % > 15 cm); search 49 %, net turn 1.79 rad, mean \|wz\| 0.36 rad/s (38 % of cap); short passes 4.5 m off, medium 2.45 m; pitch at 1.0–1.5 m/s 0.0°, height 0.510–0.516 m. Checkpoints alternate between "power" (13200) and "goals" (12950, 13450).

Search pass bar re-think: wz caps are random 0.4–1.5 rad/s; a ball behind needs ~π rad, i.e. ~8 s at a 0.4 cap, so "≥ 70 % within 6 s" is unreachable at low caps. Judge search by mean \|wz\| as a share of the cap and net turn per search instead (target: ≥ 60 % of cap).

v56d/13700 (seed 1): flat 90 % / **1.09 goals**, bumps 86 % / 0.95, push late falls 0.9 %, near-ball 2.1 s; long kicks 4.75 m/s (1.00× needed), 4.9 % ≥ 7 m/s, air balls long 14 % (0 % > 15 cm); search 52 %, \|wz\| 0.40 rad/s (43 % of cap); pitch at 1.0–1.5 m/s −0.4°, heel-up 30 %; caps 0.60 m/s at 1.6–2.0. Plateau with checkpoints alternating strengths; stopped at ~13915. Seed 2 on 13450 and 13700 to pick.

Seed 2: v56d/13450 bumps 92 % / 1.01, flat 96 % / 1.07, push 88 %, late falls 1.3 %; v56d/13700 bumps 87 % / 1.02, flat 91 % / 1.03, push 81 %, late falls 1.5 %. **Two-seed v56d/13450: flat 95.5 % / 1.05 goals, bumps 91.5 % / 1.00, push late falls 1.5 %** (v55b/12200: 94.5 / 1.05, 90.5 / 0.98, 1.35) — plus body-turn search (49 %, net 1.8 rad), long kicks 4.49 m/s grounded (4.07), near-ball 2.2 s (2.5), pitch 0.0° at speed (+1.2). Exported `k1_kick_loop_v56d_model_13450.onnx`. **Best in sim: v56d/13450. Not deployable until the runner mirrors the lost-ball rule** (in view 0.5 s / none seen 1.5 s → virtual ball 2 m at ±1.6 rad on the last-remembered side, age keeps decaying, head far sweep); until then the robot candidate stays v55b/12200.

## Goal: outperform B-Human's kick from any start, then choose kick styles by situation (user, 2026-10-05)

Head-to-head scoreboard (`scripts/tools/kick_style_compare.py`, ball 0.4–1.5 m, flat, ball DR off; B-Human gets the true ball position, ours only the camera, so the any-bearing row flatters B-Human):

| | ours v56d/13450 | B-Human |
|---|---|---|
| first kick, ball ahead: p50 / within 10 s | 2.58 s / 93 % | 2.34 s / 99 % |
| first kick, any bearing | 3.57 s / 78 % | 3.04 s / 98 % |
| first kick within 20° (ahead / any) | 84 / 90 % | 92 / 97 % |
| all kicks within 20° | 91–93 % | 96–97 % |
| long kicks 3D p50 / p90 | 5.6 / 7.3 m/s | 8.3 / 9.7 m/s |
| short / medium 3D p50 | 4.3 m/s | 3.1 m/s |
| long-kick knee torque p90 | 78 Nm | 42 Nm |
| kick-foot yaw vs kick direction | 11° (front) | 91° (side-foot) |
| body speed at contact (long) | 0.13 m/s | 0.83 m/s |

Plan: K2 unlock momentum / side-foot mechanics → K3 torque guard (B-Human sim2real clip) → K4 two near-ball style references (B-Human side-foot kicks recorded in our sim + our front kicks), outcomes choose → K5 per-situation selection check → K6 any start (behind, far, moving).

| v57 `stage3_v57` | v56d `model_13450` (resume) | K2 kick mechanics: `MOMENTUM_KICKS` — kick quality counts only body motion not toward the kick direction (sideways, backward, > 1.0 m/s forward), swing = kicking foot's world speed; `KICK_SPEED_3D` — kick speed is the ball's 3D speed; loft factor 5 / 20° → 20 / 35°. Pass: long-kick 3D speed up toward B-Human's 8.3 m/s, body speed at contact > 0.3 m/s on long kicks, accuracy / goals / falls / posture / search held. `model_13700` (seed 1): **long kicks 3D 8.19 m/s p50, 9.75 p90 (B-Human 8.28 / 9.71 — matched)**, ground 6.55 m/s, 15.3 % of all kicks ≥ 7 m/s, body speed at contact 0.31 m/s (0.13), still front kicks (92 %); but **long-kick accuracy 68 % within 20° (B-Human 95, v56d 91)**, knee torque p90 88 Nm (78), late falls flat **1.9 %** (0.2), bumps 2.4 %, push 3.7 % (1.5); bumps 84 % / 0.97 goals, flat 88 % / 0.97; first kick p50 2.38 s (B-Human 2.34), 95 % within 10 s; short passes 3.8 m off; air balls long 22 % (> 15 cm 5 %); search held (51 %), posture held (+0.2° at speed) — running | momentum + 3D speed unlocked B-Human-level long-kick speed; accuracy and falls paid for it |

v57/13950 (seed 1): long kicks 3D 8.03 / 9.53 m/s, **long accuracy 86 %** (13700: 68), body speed at contact 0.47 m/s; late falls flat **0.2 %**, bumps 1.5 %, push 2.3 %; bumps 87 % / 1.01 goals, flat 91 % / 1.02; first kick 2.36 s; search 53 %, pitch −0.2° at speed; but **knee torque p90 107 Nm on long kicks**, short passes 4.8 m off, air balls long 29 % (> 15 cm 7 %). Stopped at ~13960.

| v58 `stage3_v58` | v57 `model_13950` (resume) | K3: `torque_over_soft_limit` (−100; B-Human clip 50 / 50 / 30 / 60 / 30 / 30 Nm, ((|τ| − lim) / lim)² summed) and `LONG_AIM_SHARP` (long-kick power × exp(−err² / 0.05) instead of cos²). Pass: knee / hip p90 near the clip on long kicks, long-kick 3D speed ≥ ~7.5 m/s, long accuracy ≥ 90 %, falls and the rest held. `model_14200` (seed 1): **goals best yet — flat 93 % / 1.18, bumps 88 % / 1.10**, push 82 % / 1.00, late falls flat 0.2 %, bumps 1.5 %, push 1.3 %; **long kicks: knee p90 67 Nm (107), accuracy 92 % (86)**, body speed at contact 0.59 m/s (momentum kicks), but 3D speed 6.32 / 8.07 m/s (8.03 / 9.53), hip pitch p90 still 68 Nm (our cap); still front kicks (95 %); search 56 %, net turn 1.98 rad; pitch 0.0° at speed; short passes 3.5 m off; first kick 2.70 s (B-Human 2.34) — running | the torque guard trades ~1.7 m/s of long-kick speed for real-robot-feasible torque and accuracy |

v58/14450: accuracy fell (bumps 84 %, flat 84 %, 0.95–0.99 goals), long 3D 6.81 m/s, long accuracy 76 %. Stopped at ~14660. **v58/14200 is the K3 pick** (goals 1.10–1.18, long accuracy 92 %, knee p90 67 Nm). Gap to B-Human is technique: same body speed into the kick (0.59 vs 0.58), but front foot and 6.3 vs 8.3 m/s.

K4 setup: `scripts/tools/record_kick_clips.py` records good kicks (≤ 15° off target, ≥ 60 % of the needed 3D speed, long ≥ 5 m/s, no fall in the next 0.5 s) in our sim, 0.8 s before to 0.5 s after contact, as AMP clips (50 Hz, xyzw root, robot joint order). 80 B-Human side-foot kicks + 80 of ours (v58/14200 front kicks) in `data/kick_clips`; `data/amp_mix_ww_cmu_kicks` = walk set (weights × 0.8) + kick clips (10 % each style).

| v59 `stage3_v59` | v58 `model_14200` (resume) | K4: AMP data `amp_mix_ww_cmu_kicks` (`KICK_STYLE_AMP_DATA`), style kept on near the ball (`KICK_STYLE_AMP`; walking pose terms still gated by the old style gate). Both kick styles become "natural"; outcome rewards (aim, speed per range, torque guard, goals) pick. Pass: side-foot kicks appear where they pay (long kicks), long 3D speed up at ≤ clip torque, accuracy / goals / falls / posture / search held. `model_14450` (seed 1): side-foot 2 % (not adopted), long 3D 6.61 m/s, long accuracy 92 %, knee p90 79 Nm; flat 93 % / 1.01 goals, bumps 90 % / 0.95; short passes 1.76× needed. Stopped at ~14700 | style data makes a kick "allowed", but the policy never tries it, so never learns it pays |

Whole-body kick anatomy (`scripts/tools/kick_anatomy.py`, ball 0.4–1.5 m any bearing), v58/14200 vs B-Human: support foot on the ground at contact **72 % vs 98 %** (ours hops into the ball with both feet up in 28 % of kicks); kicking leg on the ball's side **46 % vs 85 %** (B-Human picks the leg by ball side — both legs used); touchdowns in the last 1 s **6 vs 4** (ours stutters); support foot 0.30 m behind / 0.19 m beside the ball vs 0.25 / 0.23; kick foot airborne 0.14 s both; trunk pitch range 6.8 vs 8.0°. B-Human's kick is a two-leg action: pick the ball-side leg, a few long steps, plant the support leg beside the ball, sweep the other with the inside of the foot.

| v60 `stage3_v60` | v58 `model_14200` (resume) | K4b: **reference-state init** — 20 % of episodes start 0.2–0.4 s before contact from recorded kicks (10 % B-Human side-foot, 10 % our front; `data/kick_rsi`, 360 states each, rotated to a random heading at the spawn), ball and target as recorded; **support-plant factor** — kick quality × 0.5 if the support foot is off the ground at contact; AMP style data v2 (120 + 120 clips, 20 %) with style on near the ball. Smoke (v58/14200, all RSI): kicks within 2 s 76 %, p50 0.42 s, no falls. Pass: side-foot use where it pays, planted support ≥ 95 %, long 3D speed up at ≤ clip torque, all else held — running | — |

## Overnight evolutionary search (2026-10-05 night)

**Evaluation fix first:** the K4b mid-kick starts (RSI) were on in the base cfg, so every evaluation tool would also have started 20 % of episodes mid-kick. The tools now set `KICK_EVAL=1` (no RSI); training keeps RSI. The v60/14450 eval and the first baseline benchmark were stopped before finishing and discarded.

**Fixed benchmark** (`scripts/tools/kick_benchmark.py`, results in `docs/benchmarks/*.json`): 9 head-to-head metrics in B-Human's scenario (ball 0.4–1.5 m, any bearing: time to / share of first kicks, first-kick and overall accuracy, long-kick 3D speed and accuracy, knee / hip torque, planted support) + 16 full-loop metrics (accuracy, goals, falls on bumps / flat / push / moving ball, short-pass stop distance, long speed vs needed, air balls, search, lean / height at speed, cap use), each with a direction and tolerance.

**Search** (`scripts/tools/evolve_kick.py`, state `docs/evolution/state.json`, log `docs/evolution/log.md`):
- genes (per-run `KICK_GENES`, no source edits): long_kick_power, torque_over_soft_limit, kick_rest_accuracy, kick_direction, long_kick_underpower, search_turn weights; RSI shares (B-Human side-foot, ours); AMP style weight; SUPPORT_PLANT_FACTOR, MOMENTUM_KICK_MAX_SPEED, LONG_AIM_SIGMA2;
- each child: uniform crossover with an elite (50 %) + Gaussian mutation (30 % of genes, σ = 15 % of range), fine-tuned from the champion for +250 / +500 iterations, both benchmarked;
- fitness: tolerance-normalised improvement over the champion (head-to-head ×2, clipped ±3 per metric);
- promotion only with **no regression** vs the champion (beyond tolerance) and none vs the anchor v56d/13450 (beyond 2× tolerance), and a positive score;
- safety: one training at a time, killed by its own process group; 150 min cap per child; stops after 3 failed children or < 20 GB disk; 11 h budget.
- Generation 1 = the v60 recipe (RSI 10 % / 10 %); start champion v58/14200.

### Night findings (live)

- **Confound fixed:** every child first carried K4 (kick clips in AMP data, style near the ball, support factor) because they were code defaults; now genes (`amp_kick_data`, `k.KICK_STYLE_AMP`, RSI shares, `k.SUPPORT_PLANT_FACTOR` = 1 for off). Champion genes = v58's true recipe.
- **Control** (champion recipe unchanged, evo_g003): −26.2 at +250, −6.6 at +500 — plain continued training moves the benchmark more than any gene. **v58/14200 is stable across eval seeds** (goals 1.14 / 1.09 bumps, 1.14 / 1.22 flat; other metrics within 1–2 points), so it is a real peak of a swinging lineage, not a lucky eval.
- Protocol: screen 9 checkpoints (+100 … +500) per child, full benchmark only on the best; `desired_kl` gene added.
- Children so far: evo_g001 (v60 recipe): planted support 98 % (B-Human 99) but goals −0.2, caps speed −0.24; evo_g002, evo_g004: goals / accuracy regressions; **evo_g005_14600: long kicks 6.98 m/s at knee 59 / hip 56 Nm (champion 6.08 at 66 / 68)** but goals 0.88 and short passes 5.4 m off.
- **Weight-space crossover** (`scripts/tools/blend_checkpoints.py`): SWA of v58/14150–14250 — long 6.45 m/s (1.03× needed), lofts > 15 cm 3 % (8), flat goals 1.18, but close-start first-kick accuracy 83 % (90) and all kicks 89 % (93) → not promotable; SWA of 5 checkpoints: bumps goals and caps speed regress; v58/14200 × v56d/13450 50/50: goals regress. Next: champion × evo_g005_14600 blends (`scripts/tools/blend_search.py`), to combine g005's power-at-low-torque with the champion's goals.

### Approach-from-far check (user: the evolved policy must still approach and kick like before)

`kick_probes.py CK approach` (ball 3–8 m, any bearing, flat, nominal ball): kicked within 15 s / first kick p50 / first kick within 20° / approach vx:
x4_g004_70 67 % / 9.24 s / 93 % / 0.45 m/s; v58/14200 69 % / 8.92 / 92 / 0.48; v56d/13450 62 % / 9.80 / 96 / 0.41; v55b/12200 57 % / 9.50 / 92 / 0.37; v53/10700 64 % / 9.24 / 92 / 0.40 (v55b, v53 predate the lost-ball rule, so pessimistic here). **No regression from the evolution**; far-start approach is slow (~9 s) for every model — a shared gap. "Fell before kicking" reads 13–25 % for all models (vs 0.1–1 % late falls in eval_kick_loop) — to be checked as a probe artifact. The 4 approach metrics are now benchmark gates (29 metrics); values added to the champion / baseline records.

Runner: rebuilt from the latest `kick` (ZijieLi 61ce06b / 7137e1e: joint-name aliases, robot-frame ball, no low_state) in `RL/runner_kick_workspace_v2`; ported the lost-ball rule + `--kick-lost-rule on|off` + trained speed-limit ranges as `runner_kick_workspace_v2/lost_rule.patch` (applies cleanly; not applied to the user's repo). Parity vs training (`scripts/tools/lost_rule_parity.py`): 1500 steps, 903 lost, slots 72–74 |diff| p50 / p99 0.000, 5 steps > 0.05. Flags for the user: `start_kick.sh` uses wz cap 2.0 (> trained 1.5); head tracking now uses the vision ball z (~0, ground frame) with the trunk-frame pivot, so the head pitches less than in training.

### Reward lint (first run, x4_g004_70, `scripts/tools/reward_lint.py`)

Share of mean |weighted reward| over 1 M env-steps (training cfg minus pushes): search_turn 8.6 % (lost state 20 % of steps — the unseen-ball relocation event is in the base cfg, so evals since v56 include it), walk_speed 8.3, kick_goal 7.4, upright 7.2, foot_flat 7.1, ball_vision 6.1, kick_direction 5.1, kick_vel 5.1, kick_lined_up 5.0, approach_close 3.8, walk_speed_limit 3.6 … long_kick_power 3.0. Kicking (direction + vel + vel_accurate + goal + long power + rest) ≈ 26 %, posture / gait ≈ 20 %. Never firing: standing_pose_l1, single_feet_avoidance, self_collisions. Input for the structural (L1 / L2) loop.

## Robot test (user, 2026-10-06)

- **evo_g014/14550** (benchmark-rejected, −16.8): reacts and runs faster, but repeatedly fails to kick / misses the ball.
- **x4_g004_70** (current champion): kicks accurately, but seems a bit slower; still behind B-Human (sim head-to-head: first kick 3.54 vs 2.94 s, long 6.9 vs 8.3 m/s, close-start aim 91 vs 98 %).
- **The sim benchmark ranking held on the robot**: the promoted model works, the rejected one does not. The gates measure real quality.
- Likely miss mechanism for g014: walking into the ball at ~0.5 m/s with real camera latency > the 0–40 ms trained (5 cm per 100 ms), plus the runner's higher head aim (vision ball z with the trunk-frame pivot) dropping the ball out of view earlier near the feet, with yaw-only memory. To verify from a `--record-obs` log.
- Next targets: speed (time to first kick, approach from far) without losing accuracy; a latency-robustness test in the benchmark.
- Latency test (`eval_kick_loop.py --vision-delay 3,6`, detections 60–120 ms late, bumps): x4 89 % → 84 % within 20°, 1.09 → 0.98 goals; g014 90 → 86 %, 0.90 → 0.80. Both degrade alike, so **latency alone does not reproduce g014's real-robot misses** (it still kicks in sim with delay). Remaining suspects: the runner's higher head aim / ball dropping out of view near the feet, the lost-ball patch (applied?), and g014's 20 % no-support kicks and 83 Nm knee torque on real motors. Needs the robot log.

## Fair head-to-head (2026-10-06): same perception for both policies

Until now the head-to-head gave B-Human the **true ball** (position and velocity, always visible) while ours saw only the camera. Now `kick_style_compare.py --perception {camera,true}` applies the same definition to both: camera = head-camera view, noise 0.03 m + 5 %, 2 % dropout, 0–2 step delay (B-Human gets exactly our policy's detection, kept in world coordinates when unseen = odometry); true = exact ball every step (`fov_half_angle = π` now means always visible). Close start, any bearing, x4_g004_70 vs B-Human:

| | camera: ours / B-Human | true: ours / B-Human |
|---|---|---|
| first kick p50 | **3.64** / 4.21 s | 3.04 / 3.06 |
| kicked within 10 s | **79** / 77 % | 97 / 98 |
| first kick within 20° | 84 / 84 % | 81 / **96** |
| all kicks within 20° | **90** / 85 % | 89 / **97** |
| long 3D p50 | 6.85 / 7.08 m/s | 6.63 / **8.39** |
| long ground speed p50 | **5.56** / 4.67 m/s | 5.00 / 5.24 |
| long within 20° | **92** / 84 % | 88 / **97** |
| long knee / hip p90 | 56 / 63 vs **38 / 54** Nm | 52 / 65 vs **42 / 53** |

**Under realistic camera perception ours beats B-Human on first-kick time, kick rate, overall and long accuracy and long ground speed; ties first-kick accuracy; is within 0.25 m/s on long 3D speed; loses on torque.** With perfect perception B-Human's kick technique is clearly better (aim 97 vs 89 %, long 8.4 vs 6.6 m/s at less torque). The old "behind on every head-to-head metric" was mostly B-Human's privileged ball input. Caveat: B-Human was trained with its own vision noise model and a filtered ball model, so our camera model may hit it harder than its real pipeline does. Benchmark now carries both: `h2h_*` (camera, both) and `h2h_true_*` (perfect, both).

# Design: Kick-on-Walk-AMP

> **Status:** Spec locked (2026-09-27) — Appendix B scalars + PPO + spawn +
> physics in. Implementation in progress (`walkamp_kick_env_cfg`).
>
> **Fork:** New kick task on Flat AMP Walk stack. Train **from scratch** (no
> Walk weight reload). Walk 9950 used **only** for arrival-buffer collection
> (§9.2). Rewards = thesis §5 + `ball_velocity_toward_goal` (Strike payday).
>
> **Intended skill chain (authoritative):**
> `Approach & Align → Plant & Wind-up → Strike & Launch → Settle & Hold → Ball Stops in Target`
> See §1.1 for phase↔reward map and current blocker.
>
> **Related:** Living Near problem context remains [`PROBLEM.md`](PROBLEM.md).
> This doc is the product spec for the redesign; do not mix Near reward knobs
> into this stack without updating here first.

---

## 1. Goal

Train a **single full-body Kick policy** that:

1. Approaches the ball from Walk-like states (geometry-driven, no twist cmd).
2. Plants and strikes toward a goal with useful power.
3. Settles in a dual-support pose compatible with Walk handoff.
4. Shares obs/action/PD layout with Walk AMP (future warm-start optional; **v1 trains from scratch**).

**Out of scope for v1:** residual Walk↔Kick network, deploy FSM polish, Rough
terrain FT (Flat first).

### 1.1 Intended pipeline ↔ reward coverage (locked context)

```text
Approach & Align  →  Plant & Wind-up  →  Strike & Launch  →  Settle & Hold  →  Ball in Target
```

| Phase | Intent | Current coverage | Status |
|-------|--------|------------------|--------|
| **Approach & Align** | Walk to ball, face goal axis | `agent_approach_ball` (ungated); spawn ±90° behind ball→target, no face-ball snap | **Partially OK** — approach exists; align-to-goal not rewarded |
| **Plant & Wind-up** | Support plant, load swing foot | *none* | **Missing** |
| **Strike & Launch** | Foot–ball impact, ball velocity toward goal | `ball_velocity_toward_goal` \(\min(6, v_b\cdot\hat{d})\) + cosine `ball_approach_target` | **Payday present** — still needs discovery of contact |
| **Settle & Hold** | Dual-support after impact | `upright` / `base_height` (target 0.52) / survival / fall penalties | **base_height added** — anti-crouch |
| **Ball Stops in Target** | Sparse settle in goal | `target_reached` (w=250, needs \(c_t>50\) + ball still) | **Present but almost never sampled** |

**Holding issue (current):** Plant & Wind-up unrewarded; Strike has velocity payday but no contact shaping.

- `ball_velocity_toward_goal` (extra vs thesis 13): \(r=\min(6,\,v_b\cdot\hat{d})\) with \(\hat{d}=(p_g-p_b)/\|p_g-p_b\|\) — encourages high goal-directed ball speed (cap 6 prevents velocity exploit).
- No dense contact/closing term — policy must stumble into impact for payday to light.
- Simultaneously, **`action_rate_l2`** and **`fell_over_penalty`** still dominate return.
- Success metric: rising `Episode_Reward/ball_velocity_toward_goal` / strong_kick.

---

## 2. Why not Near-Amp

| | Near-Amp (today) | Kick-on-Walk-AMP (this) |
|--|--|--|
| Base env | BaseWalk / HTWK lineage | Flat AMP Walk (`velocity_amp_env_cfg`) |
| Actor / critic | 56 / ~67 | **78 / 95** |
| Actions | 12 legs @ scale **0.8** | **22** full body @ **`K1_ACTION_SCALE`** |
| PD | BaseWalk / ParameterWalk-ish | **Whirlwind Walk AMP** |
| Twist command | Yes (teacher + tracking rewards) | **Dropped** |
| Walk ckpt | Frozen enter/exit only | **Arrival buffer only** — train kick **from scratch** |
| AMP dataset | Kick clips only | Kick AMP data |

Near ckpts are **not** weight-compatible. Obs/PD/AMP come from Walk; rewards
from thesis (§5) only — not the Near reward stack.

---

## 3. Observation space (locked)

### 3.1 Actor — **78-D**

| # | Term | Dim | Notes |
|---|------|----:|-------|
| 0 | `base_ang_vel` | 3 | |
| 1 | `projected_gravity` | 3 | |
| 2 | `ball_rel_pos` | 3 | ball in robot base frame |
| 3 | `target_pos` | 3 | **goal in robot base frame** (see §3.3) |
| 4 | `joint_pos` | 22 | full body, biased / noisy like Walk AMP actor |
| 5 | `joint_vel` | 22 | |
| 6 | `actions` | 22 | previous action |

**Not on actor:** twist command, gait clock, kick_range slot, ball velocity,
foot heights/forces, ball–foot contact.

### 3.2 Critic — **95-D** = actor 78 + privileged 17

Critic sees the same 78 actor features (clean joints; no actor noise on ball),
**plus ground-truth**:

| # | Term | Dim | Notes |
|---|------|----:|-------|
| 7 | `foot_height` | 2 | exact clearance (Walk AMP sensor) |
| 8 | `foot_air_time` | 2 | |
| 9 | `foot_contact` | 2 | ground contact |
| 10 | `foot_contact_forces` | 6 | GRF |
| 11 | `ball_velocity` | 3 | **robot base frame** (for DA) |
| 12 | `ball_foot_contact` | 2 | binary L/R foot↔ball |

**Dropped vs Walk critic:** `base_lin_vel` (3). Replaced by ball channels.

### 3.3 Ambiguity resolutions (locked)

**Target = 3-D position in base frame (not 2-D unit heading).**

- Variable goal range (≈2.5–12 m) needs distance to set swing / ballistic speed.
- Body-frame 3-vector from `quat_apply_inverse(root_quat, goal_w − root_w)`.
- DA: \(\rho_{\mathrm{triv}} \oplus \rho_{\mathrm{sign}} \oplus \rho_{\mathrm{triv}}\)
  (flip lateral \(y\) only), matching Julia de Vries Table 3.4 style.

**Ball–foot contact = binary L/R (dim 2), not forces.**

- Impact force spikes are sub-20 ms and high-variance for the critic.
- Ground forces already covered by `foot_contact_forces` (6).
- DA: swap L↔R (\(\rho_{\mathrm{reg}}\)).

**Twist command = dropped (0 dims).**

- Policy is goal-driven via `ball_rel_pos` + `target_pos`.
- **Must remove** `tracking_lin_vel_x/y` and `tracking_ang_vel` (and twist
  teacher that fed them). Unobserved reference is illegal.
- Replace with geometry approach terms (§5).

### 3.4 Actor noise / corruption (locked = Walk AMP)

Match Flat AMP Walk actor sensing. Critic stays **clean**
(`enable_corruption=False`).

| Actor term | Uniform noise | Other |
|------------|---------------|-------|
| `base_ang_vel` | \(\mathcal{U}(-0.2,\ 0.2)\) | |
| `projected_gravity` | \(\mathcal{U}(-0.05,\ 0.05)\) | |
| `joint_pos` | \(\mathcal{U}(-0.01,\ 0.01)\) | `biased=True` + startup **encoder_bias** \(\pm 0.015\) |
| `joint_vel` | \(\mathcal{U}(-1.5,\ 1.5)\) | |
| `actions` | none | |
| `ball_rel_pos` / `target_pos` | **none** (v1) | kick slots clean |

- Actor group: `enable_corruption=True`
- Critic: no noise; joints without encoder bias
- **Obs-term delay:** Walk AMP does **not** set `delay_min/max_lag` on
  observations (unlike BaseWalk 0–2). Kick-on-Walk-AMP follows Walk AMP:
  **no obs lag**. Actuator command delay stays as §4 (lag 2–8).

### 3.5 Actions — **22-D**

Full-body joint position targets (same order as Walk AMP / whirlwind K1).

---

## 4. PD and action scaling (locked = Walk AMP)

Robot: `k1_whirlwind_constants` articulation.

### 4.1 Nominal PD

| Group | Kp | Kd | Effort |
|-------|---:|---:|-------:|
| Knee | 80 | 4 | 112 |
| Hip yaw | 80 | 4 | 38.3 |
| Hip pitch | 80 | 4 | 68 |
| Hip roll | 80 | 4 | 76 |
| Ankle | 50 | 2 | 38.3 |
| Shoulder / elbow | 10 | 1 | 14 |
| Head | 4 | 0.25 | 6 |

- Startup DR: scale **kp, kd ∈ [0.8, 1.2]**
- Actuator delay: lag **2–8**, `hold_prob=0.3`

### 4.2 Action scale

`K1_ACTION_SCALE = 0.25 × effort / stiffness` per group:

| Joint regex | Scale |
|-------------|------:|
| `.*_Knee_Pitch` | 0.350 |
| `.*_Hip_Pitch` | 0.213 |
| `.*_Hip_Roll` | 0.238 |
| `.*_Hip_Yaw` | 0.120 |
| `.*_Ankle_.*` | 0.192 |
| `.*_Shoulder_.*` / `.*_Elbow_.*` | 0.350 |
| `Head_.*` | 0.375 |

**Do not** use BaseWalk flat `0.8` — breaks 9950 warm-start.

---

## 5. Rewards (locked — thesis only)

**Only** the terms and weights below. Do not add other rewards unless this
section is updated first.

### 5.0 Weight table (authoritative)

| Group | Term | Weight |
|-------|------|-------:|
| Task | Target distance (`target_reached`) | **250** |
| Task | Ball approach target | **0.3** |
| Task | Agent approach ball | **0.1** |
| Task | Ball velocity toward goal (`ball_velocity_toward_goal`) | **1.0** (cap 6) |
| Task | Ball not moving (`ball_stagnant`) | **−0.02** |
| Stability | Survival | **0.01** |
| Stability | Upright | **0.05** |
| Stability | Base height (`base_height`) | **−15** (target 0.52) |
| Stability | Fall over (`fell_over_penalty`) | **−100** |
| Stability | Fall down (`fall_down`) | **−100** |
| Style / reg | Joint position limit (`dof_pos_limits`) | **−1** |
| Style / reg | High-frequency actions (`action_rate_l2`) | **−0.0075** |
| Style / reg | Feet sliding (`foot_slip`) | **−0.01** |
| Style / reg | Arm swing | **−0.05** |
| Style / reg | Arm posture | **0.3** |

Active set = **15 terms** (thesis 13 + ball velocity + base height).

### 5.1 Target–ball distance (sparse) — `target_reached` · w=250

\[
\mathbf{d}^{\mathrm{target,ball}}_t =
\begin{pmatrix} x_{\mathrm{target}} - x_{\mathrm{ball}} \\
y_{\mathrm{target}} - y_{\mathrm{ball}} \end{pmatrix}.
\]

Appendix B: \(\sigma^2 = 0.9\) (\(\sigma \approx 0.9487\,\mathrm{m}\)):

\[
r^{\mathrm{target\text{-}reached}}_t =
\begin{cases}
\exp\!\big(-\|\mathbf{d}^{\mathrm{target,ball}}_t\|^2 / 0.9\big)
  & \text{if } c_t > T_{\mathrm{window}} \wedge \|\mathbf{v}^{\mathrm{ball}}_t\| < \varepsilon \\
0 & \text{otherwise.}
\end{cases}
\]

with \(\varepsilon = 0.5\,\mathrm{m/s}\), \(T_{\mathrm{window}} = 50\) steps (§15).

### 5.2 Ball approach target (dense) — `ball_approach_target` · w=0.3

\[
r^{\mathrm{b\text{-}approach\text{-}t}}_t =
\begin{cases}
\max\!\Big(0,\ 
\dfrac{\mathbf{v}^{\mathrm{ball}}_t \cdot \mathbf{d}^{\mathrm{target,ball}}_t}
{\|\mathbf{v}^{\mathrm{ball}}_t\|\,\|\mathbf{d}^{\mathrm{target,ball}}_t\|}\Big)
  & \text{if }\|\mathbf{v}^{\mathrm{ball}}_t\| > \varepsilon \\
0 & \text{otherwise.}
\end{cases}
\]

### 5.3 Agent approach ball (dense) — `agent_approach_ball` · w=0.1

Thesis cosine approach (**no distance gate**). The term keeps pulling the
robot through the ball until \(v_{\mathrm{ball}}\) rises; an artificial
\(\|d\| > 0.3\) cutoff creates a no-man's-land with no contact gradient.

\[
r^{\mathrm{a\text{-}approach\text{-}b}}_t =
\begin{cases}
\dfrac{\mathrm{CosineSimCLIP}(\mathbf{d}^{\mathrm{agent,ball}}_t, \mathbf{v}^{\mathrm{agent}}_t)}
{1 + \max(0,\ \mathbf{v}^{\mathrm{ball}}_t \cdot \mathbf{d}^{\mathrm{target,ball}}_t)}
  & \text{if }\|\mathbf{v}^{\mathrm{agent}}_t\| > \varepsilon \\
0 & \text{otherwise.}
\end{cases}
\]

``velocity_eps=0.1`` so slow walk-in still counts.
### 5.3b Ball velocity toward goal (dense) — `ball_velocity_toward_goal` · w=1.0

**Extra vs thesis Table 4.1** — encourages imparting high ball speed toward the
opponent goal. With \(\hat{d}=(p_g-p_b)/\|p_g-p_b\|\):

\[
r^{\mathrm{ball\text{-}vel}}_t = \min\!\big(6,\ v_b \cdot \hat{d}\big).
\]

Cap at 6.0 prevents exploiting unbounded ball velocity. Implemented as
`ball_velocity_toward_goal` with `max_reward=6`, `use_decay=False` (no plant
gate). Complements scale-free cosine `ball_approach_target` (w=0.3).

### 5.4 Ball not moving (dense penalty) — `ball_stagnant` · w=−0.02

Thesis (sparse target alone is too hard; dense approach terms then create a
rock-near-ball local optimum):

> While targeting accuracy is the primary objective, relying solely on a sparse
> reward makes it very difficult for the agent to learn the task objective. …
> two dense rewards were introduced: Agent Approach Ball and Ball Approach
> Target. … the agent [got] stuck at a local optimum where the robot would rock
> back and forth near the ball without moving it. To address this problem, a
> low penalty was included to incentivise the agent to move the ball (Ball Not
> Moving Penalty).

Thesis table weight is −0.01 ungated. **Kick-on-Walk-AMP lock:** gate on
arrival \(\|d\| < 0.3\,\mathrm{m}\) (do not tax far approach) and raise weight
to **−0.05** so still-ball in the kick zone is strictly worse than survival
(\(+0.01 - 0.05 = -0.04\)/step). Equal −0.01 left freeze + AMP style as a
stable optimum.

\[
r^{\mathrm{ball\text{-}stagnant}}_t =
\begin{cases}
1 & \text{if }\|\mathbf{v}^{\mathrm{ball}}_t\| < 0.5\,\mathrm{m/s}
  \wedge \|d_{\mathrm{agent,ball}}\| < 0.3 \\
0 & \text{otherwise.}
\end{cases}
\]

### 5.5 Survival (dense) — `survival` · w=0.01

Constant positive reward each step while the episode continues.

### 5.6 Upright (dense) — `upright` · w=0.05

Appendix B: \(\sigma_{\mathrm{upright}}^2 = 0.1\)
(\(\sigma \approx 0.3162\)):

\[
r^{\mathrm{upright}}_t = \exp\!\big(-\theta_t^2 / 0.1\big),
\]

where \(\theta_t = \arccos(\hat{\mathbf{z}}_b \cdot \hat{\mathbf{z}}_w)\).

### 5.6b Base height (dense penalty) — `base_height` · w=−15

Walk-style anti-crouch: \(r = (z_{\mathrm{root}} - 0.52)^2\) (flat; no terrain
scan). Target matches Walk / arc trunk height. At measured crouch \(z\approx0.38\)
the raw cost is \(\sim0.02\)/step → \(\sim-0.3\) with w=−15.

### 5.7 Fall over (penalty) — `fell_over_penalty` · w=−100

\[
r^{\mathrm{fell\text{-}over}}_t =
\begin{cases}
1 & \text{if } \theta_t > \theta_{\mathrm{limit}} = 1.2217\,\mathrm{rad}\ (\approx 70^\circ) \\
0 & \text{otherwise.}
\end{cases}
\]

WalkAmp lock: **−100** (was thesis −50) so dive-kick + ball-vel payday does not dominate.

### 5.8 Fall down (penalty) — `fall_down` · w=−100

\[
r^{\mathrm{fall\text{-}down}}_t =
\begin{cases}
1 & \text{if } z^{\mathrm{trunk}}_t < z_{\mathrm{falldown}} = 0.2\,\mathrm{m} \\
0 & \text{otherwise.}
\end{cases}
\]

WalkAmp lock: **−100** (was thesis −50), matched to fell-over.
### 5.9 Joint position limit (dense penalty) — `dof_pos_limits` · w=−1

\[
r^{\mathrm{joint\text{-}limit}}_t =
\begin{cases}
1 & \text{if any joint limit exceeded} \\
0 & \text{otherwise.}
\end{cases}
\]

### 5.10 Action rate (dense penalty) — `action_rate_l2` · w=−0.0075

WalkAmp lock: midway between half-thesis (−0.005) and thesis Appendix B (−0.01).

\[
r^{\mathrm{action\text{-}rate}}_t = -\|\mathbf{a}_t - \mathbf{a}_{t-1}\|_2^2.
\]

### 5.11 Foot slip (dense penalty) — `foot_slip` · w=−0.01

\[
r^{\mathrm{foot\text{-}slip}}_t
=
-\sum_{\mathrm{foot}\in\{\mathrm{L},\mathrm{R}\}}
\big(\|\mathbf{v}^{\mathrm{foot}}_{t,xy}\|^2 \cdot
\mathrm{contact}^{\mathrm{foot,ground}}_t\big).
\]

### 5.12 Arm swing (dense) — `arm_swing` · w=−0.05

\[
r^{\mathrm{arm\text{-}swing}}_t =
\begin{cases}
\exp\!\big(-1 / (q_{\mathrm{pitch},L} + q_{\mathrm{pitch},R})^2\big)
  & \text{if } (q_{\mathrm{pitch},L}\, q_{\mathrm{pitch},R} > 0)
    \wedge |q_{\mathrm{pitch},L} + q_{\mathrm{pitch},R}| > 2.0 \\
0 & \text{otherwise.}
\end{cases}
\]

### 5.13 Arm posture (dense) — `arm_posture` · w=0.3

Appendix B: \(\sigma_{\mathrm{roll}} = 0.5\,\mathrm{rad}\):

\[
r^{\mathrm{arm\text{-}posture}}_t
=
\exp\!\Big(
-\dfrac{(q_{\mathrm{roll}} - q_{\mathrm{roll,def}})^2}{0.5^2}
\Big) - 1
\in (-1, 0].
\]

With weight \(+0.3\), contribution \(\in [-0.3, 0]\) — **strictly a penalty**,
zero at nominal shoulder roll.

**L+R = mean** (keeps bound \([-0.3, 0]\)):

\[
r^{\mathrm{arm\text{-}posture}}_t
=
\frac{1}{2}\sum_{s\in\{L,R\}}
\Bigg[
\exp\!\Big(
-\dfrac{(q_{\mathrm{roll},s} - q_{\mathrm{roll,def}})^2}{0.5^2}
\Big) - 1
\Bigg].
\]

(Weight \(0.3\) applied by the reward manager → contribution \(\in [-0.3, 0]\).)

---

## 6. AMP

Reuse Walk AMP **structure** (obs 30-D, disc, style weight, DA). Style on until
`kick_detected`, then off so settle is task-only.

| Knob | Choice |
|------|--------|
| AMP obs | Walk: legs pos/vel + `base_lin_vel` + gravity = **30** / frame |
| History | **10** steps → 300-D |
| Style weight | **0.3** (base) |
| Style gate | On until `kick_detected`, then **0** |
| Style proximity | \(w_{\mathrm{AMP}}(t)=0.3\cdot\exp(-\|d_{\mathrm{agent,ball}}\|^2/1.0)\) until kick; far wander → style ≈ 0 |
| Discriminator | `(256, 128)`, BCE; warm-start from Walk 9950 if layout matches |
| Dataset | **Kick AMP data** (`data/retargeted/k1/kick`) — not walk-only (walk-only would punish kick swing). Optional walk mix later for approach only |
| Augmentations | Walk AMP DA: mirror + speed ±10% (±20% if Walk) |
| Seeds | **One seed per DA configuration** |
| Optimizer | **Muon** (actor/critic; disc Adam as Walk DA-Muon) |

### 6.1 Data augmentation / symmetry

Need **78 / 95** path (Walk is 75 / 90):

- Flip `ball_rel_pos`, `target_pos`, `ball_velocity` (base frame): negate lateral
  (\(\rho_{\mathrm{triv}}\oplus\rho_{\mathrm{sign}}\oplus\rho_{\mathrm{triv}}\)).
- Swap `ball_foot_contact` L↔R; same for foot height / air / contact.
- Joint / action mirrors: Walk inverted-index tables (22-D).

**`foot_contact_forces` (6-D) — do not only swap feet:**

\[
[F_{L,x}, F_{L,y}, F_{L,z}, F_{R,x}, F_{R,y}, F_{R,z}]
\]

Under \(S_2\) reflection: swap L↔R **and** negate lateral \(F_y\):

\[
F_{L}^{\mathrm{mir}} = [F_{R,x},\ -F_{R,y},\ F_{R,z}],
\quad
F_{R}^{\mathrm{mir}} = [F_{L,x},\ -F_{L,y},\ F_{L,z}].
\]

In the concatenated 6-D slice, **sign-flip indices 1 and 4** (0-based \(F_{L,y}\), \(F_{R,y}\)) after the L↔R swap (or equivalently: swap 3-vectors then negate \(y\) of each).

---

## 7. Train from scratch (no Walk weight reload)

**Do not** load Walk `model_9950` into actor/critic/disc for Kick-on-Walk-AMP
v1. Train **from scratch** with locked architecture (§8): init_std 1.0, Muon,
entropy 0.01.

Walk 9950 is used **only** to:

1. Collect the **Arrival Pose Buffer** (§9.2.1) offline.
2. Optionally validate deploy handoff later (out of scope for v1 train).

Obs/action/PD layout still **match** Walk so a future warm-start remains
possible; v1 deliberately avoids it.

### 7.1 Warm-start remap reference (unused in v1)

| Walk 75 | Kick-on-Walk 78 |
|---------|-----------------|
| `[0:6]` ang + gravity | `[0:6]` |
| — | `[6:12]` ball + target ← zeros |
| `[6:72]` q / qd / a | `[12:78]` |
| `[72:75]` twist cmd | drop |

Critic: drop `base_lin_vel`; pad ball_vel + ball_foot; copy foot block.

---

## 8. Network / algo (locked — thesis Appendix B.1)

Train from scratch with:

| Parameter | Value |
|-----------|------:|
| Parallel envs | **4096** |
| Steps / env (rollout) | **24** (batch \(4096\times24=98304\)) |
| Mini-batches | **4** (mb size 24576) |
| Learning epochs | **5** |
| Learning rate | **\(10^{-4}\)** adaptive, desired KL **0.01** |
| \(\gamma\) / \(\lambda\) | **0.99** / **0.95** |
| PPO clip | **0.2** |
| Max grad norm | **1.0** |
| Value loss coef | **1.0** |
| Actor / critic MLP | **`[512, 256, 128]`**, activation **ELU** |
| Obs normalization | **True** (actor + critic) |
| Init action std | **1.0** (scalar) \[EXACT Table B.1\] |
| Entropy coefficient | **0.01** (Walk AMP; aids early kick exploration) |
| Optimizer | **Muon** (actor/critic; match DA-Muon Walk stack) |
| Max iterations | **15 000** |
| `only_positive_rewards` | **False** |

---

## 9. Env / spawn / physics

### 9.1 Timing

| | Thesis (Appendix / §3.1) | Walk AMP 9950 (actual) |
|--|--|--|
| Sim dt | **0.002 s** (500 Hz) | 0.005 s |
| Control dt | **0.020 s** (50 Hz) | 0.020 s |
| Decimation | **10** | 4 |

**Lock for Kick-on-Walk-AMP:** control **50 Hz**. Prefer **Walk AMP physics
(0.005 × 4)** when seeding 9950 (same control rate, matching contact solver
regime). Thesis 0.002 × 10 is OK for paper-parity ablations only.

Episode length: \(T_{\max} = 400\) steps = **8.0 s** at 50 Hz.

### 9.2 Robot init — Arrival Pose Buffer (locked)

**Goal:** \(p_{\mathrm{kick\_init}}(s) \equiv p_{\mathrm{walk\_arrival}}(s)\).
Sample states from frozen Walk AMP as it decelerates to stop so kick trains on
real residual momentum / foot loading / torso sway (near-zero walk→kick gap).

**Do not** use generic mid-gait pose-pool alone, and **do not** warp root to
\((0,0)\) after sampling.

#### 9.2.1 Offline collection (frozen Walk AMP)

```text
Sample random walk vel → Walk ~1.5 s (steady gait) → cmd v=(0,0,0)
  → Record window −0.4 s … +0.3 s around cmd=0
```

| Knob | Value |
|------|------:|
| \(v_x\) sample | \([-0.3,\ 1.0]\) m/s |
| \(v_y\) sample | \([-0.8,\ 0.8]\) m/s |
| \(\omega_z\) sample | \([-2.0,\ 2.0]\) rad/s |
| Steady walk before stop | ~**1.5 s** |
| Stop command | Abrupt \((0,0,0)\) **and** smooth **0.3 s** ramp (both) |
| Record window @ 50 Hz | **35 frames**: 20 before cmd=0 (~−0.4 s), 5 around 0, 10 after (~+0.2 s) |
| Buffer size | **10k–50k** states (`.npz` / `.pt`); ~2 min @ 4096 envs |

Per frame save full dynamical state:

- \(q \in \mathbb{R}^{22}\), \(\dot{q} \in \mathbb{R}^{22}\)
- Base lin vel (base frame) \(\mathbf{v}_b \in \mathbb{R}^3\)
- Base ang vel \(\boldsymbol{\omega}_b \in \mathbb{R}^3\)
- Base roll/pitch via projected gravity \(\mathbf{g}_b\)
- Root pose in world (for ball/target \(R_z(\psi)\) spawn)

#### 9.2.2 Kick reset

1. Sample a state from the **arrival buffer**; set robot to that state
   (joints + base vel + orientation — keep world XY/yaw from the sample).
2. Spawn ball/target on a shared approach ray within \(\pm 60^\circ\) of that
   heading, then face the ball (``post_reset``, after goal-command resample).
   (§9.2.3 + §9.3).
#### 9.2.3 Momentum-aware ball \(x\) (locked)

If arrival \(v_x > 0\), do **not** allow ball as close as 0.15 m (trample risk).

\[
x_{\min} = 0.15 + \max(v_x, 0) \cdot 0.3\,\mathrm{s},
\quad
x_b \sim \mathrm{Uniform}(x_{\min},\, 1.0).
\]

(\(r_b\) replaces Cartesian \(x_b,y_b\); approach axis \(\alpha\) shared.)

Target lies on the **same** ray beyond the ball (\(R \ge r_b + 1.5\)).
Arrival yaw is **kept** (`face_ball=False`) — no snap toward the ball.

### 9.3 Ball and target ranges (locked)

| Object | Sampling (robot base @ arrival \(t=0\)) | Range |
|--------|----------------------------------------|-------|
| **Approach axis** \(\alpha\) | Shared robot→ball→target ray | \(\alpha \sim \mathcal{U}(-\pi/2,\ \pi/2)\) (±90°) |
| **Ball** \(r\) | Polar radius with **momentum clamp** | \(r \sim \mathcal{U}(0.15+\max(v_x,0)\cdot 0.3,\ 1.5)\) |
| **Ball** \(z\) | Rest on ground | \(z=0.08\) |
| **Target** \(R\) | Same axis, beyond ball | \(R \sim \mathcal{U}(2.5,\ 8.5)\), then \(R \leftarrow \max(R,\ r+1.5)\) |
| **Robot yaw** | Arrival / standing heading | **no** face-ball rewrite |

World map (after arrival state set):

\[
\mathbf{p}^{\mathrm{ball}}_{\mathrm{world}}
=
\mathbf{p}^{\mathrm{robot}}_{xy}
+
R_z(\psi)
\begin{bmatrix} r\cos\alpha \\ r\sin\alpha \end{bmatrix},
\quad
\mathbf{p}^{\mathrm{target}}_{xy}
=
\mathbf{p}^{\mathrm{robot}}_{xy}
+
R_z(\psi)
\begin{bmatrix} R\cos\alpha \\ R\sin\alpha \end{bmatrix}.
\]

\(\psi\) is the arrival heading (unchanged). Ball/target may sit off the
robot's forward axis within ±90°.
### 9.4 Ball physics (locked — thesis Table 3.1)

| | Value |
|--|------:|
| Mass | **0.1 kg** |
| Radius | **0.08 m** |
| Friction (slide, torsion, roll) | **(1.0, 0.5, 0.015)** |

### 9.5 Domain randomization

| DR | Value | Source |
|----|-------|--------|
| Foot friction | \(\mathcal{U}[0.3,\ 1.2]\) per foot at reset | Thesis §3.1 |
| Action delay | lag **2–8** sim steps, hold_prob **0.3** | Thesis + Walk AMP |
| Push | planar trunk force every **1–3 s**; magnitude **~20–40 N** \[GUESS\] | Thesis; Walk has `push_robot` — retune mag |
| Actor obs noise | **Walk AMP** (§3.4); ball/target clean v1 | Our lock over thesis guess |
| PD scale | kp/kd \(\in [0.8,\ 1.2]\) | Walk AMP |
| Encoder bias | \(\pm 0.015\) | Walk AMP |

---

## 10. Terminal states (locked — Julia Table 3.3)

Each episode starts from a chosen init distribution and ends when any row below
is true at timestep \(t\). Termination is evaluated **after** the step that
satisfies the condition, so the **final-step reward is included** in the return.

Let:

- \(\theta_t\) = tilt of robot base \(z\)-axis from world vertical
- \(z^{\mathrm{trunk}}_t\) = trunk height
- \(\mathbf{d}^{\mathrm{target,ball}}_t\) = planar ball→target vector
- \(\mathbf{v}^{\mathrm{ball}}_t\) = ball linear velocity
- \(c_t\) = **latching contact step counter** — steps since **first** agent–ball
  contact (not raw episode time). See §10.5.
- \(\mathrm{contact}^{\mathrm{agent,ball}}_t\) = feet–ball **or** body–ball
- \(\varepsilon\) = ball-still speed threshold; \(r\) = target radius;
  \(T_{\mathrm{window}}\) = post-contact window; \(T_{\max}\) = episode length

### 10.1 Table (thesis §3.3)

| Termination | Description | Condition |
|-------------|-------------|-----------|
| **Time out** | Episode exceeded length | \(t > T_{\max}\) |
| **Fell over** | Orientation exceeds tilt limit | \(\theta_t > \theta_{\mathrm{limit}}\) |
| **Fell down** | Trunk height below minimum | \(z^{\mathrm{trunk}}_t < z_{\mathrm{falldown}}\) |
| **Target hit** | Ball stopped **inside** target | \(\|\mathbf{d}^{\mathrm{target,ball}}_t\| < r\) \(\wedge\) \(\|\mathbf{v}^{\mathrm{ball}}_t\| < \varepsilon\) |
| **Target missed** | Ball stopped **outside** target after window | \(\|\mathbf{d}^{\mathrm{target,ball}}_t\| > r\) \(\wedge\) \(\|\mathbf{v}^{\mathrm{ball}}_t\| < \varepsilon\) \(\wedge\) \(c_t > T_{\mathrm{window}}\) |
| **Double touch** | Any **body or feet**–ball contact after window | \(c_t > T_{\mathrm{window}}\) \(\wedge\) \((\mathrm{contact}^{\mathrm{feet,ball}}_t \vee \mathrm{contact}^{\mathrm{body,ball}}_t)\) |

### 10.2 Roles

**Early / safety:** time out, fell over, fell down, double touch. Double touch =
**any** feet–ball **or** body–ball contact after \(T_{\mathrm{window}}=50\) steps
(1.0 s) — enforces a single decisive strike (no dribble / shove / rebound).

**Outcome:** target hit / target missed. Missed **requires** \(c_t > T_{\mathrm{window}}\)
so a stationary ball at episode start (agent has not touched it yet) does not
fire miss. Hit does not need that guard — the ball cannot rest inside the
target without having moved.

### 10.3 Scalars (Appendix B Table B.2 — EXACT)

| Symbol | Value | Role |
|--------|------:|------|
| \(T_{\max}\) | **400** steps (**8.0 s** @ 50 Hz) | time out |
| \(T_{\mathrm{window}}\) | **50** steps (**1.0 s**) | miss / double-touch / `target_reached` gate |
| \(\theta_{\mathrm{limit}}\) | **1.2217 rad** (\(\approx 70^\circ\)) | fell over |
| \(z_{\mathrm{falldown}}\) | **0.2 m** | fall down |
| \(r\) | **1.0 m** | target hit radius |
| \(\varepsilon\) | **0.5 m/s** | ball stationary |

Code map: `time_out`, `fell_over`, `root_height`, `target_hit`, `target_missed`,
`double_touch` in `kick/mdp/terminations.py`.

### 10.4 Explicitly omitted

- **`illegal_contact`**: in thesis appendix text but **not** in reward Table 4.1
  nor terminal Table 3.3. Do **not** add as reward or termination; knee/shin
  graze handled via fall thresholds.
- **`near_ball_no_kick`**: Near-only; off for v1.

### 10.5 Contact counter \(c_t\) (locked)

Latching step counter — **must not** tick from \(t=0\), or `target_missed` /
double-touch fire at step 51 before the robot reaches the ball.

```python
# reset
contact_counter[:] = 0
contact_has_occurred[:] = False

# each step
is_touching = feet_ball_contact | body_ball_contact
contact_has_occurred |= is_touching
contact_counter += contact_has_occurred.long()  # 0 until first touch, then +1/step
```

Gates that use \(c_t > T_{\mathrm{window}}\) (\(T_{\mathrm{window}}=50\)):

- `target_reached` reward
- `target_missed` termination
- `double_touch` termination

---

## 11. Proposed task IDs

| ID | Role |
|----|------|
| `Mjlab-Kick-WalkAmp-Booster-K1` | PPO, no AMP (debug) |
| `Mjlab-Kick-WalkAmp-Amp-Booster-K1` | + kick/walk AMP |
| `Mjlab-Kick-WalkAmp-Amp-DA-Muon-Booster-K1` | DA + Muon (preferred seed path) |

Names TBD at registration time; keep “WalkAmp” in the id to avoid confusion
with `Mjlab-Kick-Near-Amp-*`.

---

## 12. Implementation checklist

1. [x] Env: Flat AMP Walk + ball/goal; Walk timing; ball physics; DR.
2. [~] **Arrival buffer** collector script (Walk 9950; §9.2.1) → stub `.pt` writer; full frozen rollout TBD.
3. [x] Kick reset from buffer + momentum-aware ball \(x\) + \(R_z(\psi)\) spawn (fallback standing if no buffer).
4. [x] Obs 78/95; base-frame `ball_velocity`; Walk AMP actor noise.
5. [x] Rewards §5.0; arm_posture = mean L/R.
6. [x] Terminations §10.3; latching \(c_t\) (§10.5); double-touch any body/feet–ball.
7. [x] AMP kick dataset; style gate; 78/95 DA (**force \(F_y\) flip** §6.1); Muon.
8. [x] Train **from scratch** (no Walk reload); PPO §8; `only_positive_rewards=False`.
9. [x] Register + play; train one seed per DA.

---

## 13. North stars

| Metric | Intent |
|--------|--------|
| Target hit / miss | Outcome terminations |
| Ball / agent approach | Thesis dense shaping |
| Upright / fall rates | Stay standing |
| Episode length | Context (≤ 8 s) |

**Abort:** never kick / stand still while mean reward ↑.

---

## 14. Guessed vs exact

| Item | Status |
|------|--------|
| Push force magnitude ~20–40 N | **GUESS** |
| `only_positive_rewards=False` | **Locked** |
| Train from scratch (no Walk weight reload) | **Locked** (§7) |
| Latching \(c_t\); GRF DA \(F_y\) flip | **Locked** (§10.5, §6.1) |
| Walk AMP actor noise magnitudes | **Our lock** (§3.4) |
| Arrival buffer + momentum ball \(x\) | **Our lock** (§9.2) |
| Physics 0.005×4 vs thesis 0.002×10 | **Prefer Walk** (§9.1) |
| All other scalars / formulas / weights above | **EXACT** from thesis |

---

## 15. Changelog

| Date | Note |
|------|------|
| 2026-09-27 | Initial design lock: 78/95/22, Walk AMP PD/scale/DA, seed 9950 |
| 2026-09-27 | Terminals Table 3.3; thesis rewards + weights; spawn; actor noise |
| 2026-09-27 | Appendix B scalars; PPO B.1; ball physics; pose-pool init fork; tensions resolved |
| 2026-09-28 | Add `base_height` w=−15 target 0.52 (anti-crouch) |
| 2026-09-27 | `action_rate_l2` −0.005 → **−0.0075** |
| 2026-09-27 | Fall penalties −50 → **−100** (`fell_over` / `fall_down`) |
| 2026-09-27 | Spawn relax: ±90° cone, `face_ball=False`, `ball_x_max=1.5` |
| 2026-09-27 | `ball_stagnant` −0.05 gated (thesis rock-near-ball fix; beat survival+AMP) |
| 2026-09-27 | Remove `agent_approach_ball` \(d>0.3\) gate — thesis pull-through to contact |
| 2026-09-27 | Replace contact bridge with `ball_velocity_toward_goal` \(\min(6,v\cdot\hat{d})\) |
| 2026-09-27 | §1.1 pipeline context: blocker = Plant/Strike gap under action_rate+fall |
| 2026-09-27 | Spawn via robot-frame \(R_z(\psi)\); kick AMP; base ball_vel; arm mean; Muon; init_std 1.0; any-contact double-touch |
| 2026-09-27 | §9.2 Arrival Pose Buffer (walk decelerate→stop); momentum-aware ball \(x\) |
| 2026-09-27 | only_positive=False; from-scratch train; latching \(c_t\); GRF DA \(F_y\) negate |
| 2026-09-27 | AMP style × ball proximity \(\exp(-d^2/1.0)\); off after `kick_detected` |

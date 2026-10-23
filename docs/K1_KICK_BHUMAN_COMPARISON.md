# B-Human K1 kick vs our kick-loop policy: what to adopt (2026-10-05)

Sources read:
- `MachineLearning/IsaacGymRL`: Booster Gym fork, B-Human's RoboCup 2026 policies.
  - `envs/K1_Ball.yaml`;
  - `envs/t1_ball.py` (observations and ball rewards; the K1 env subclasses
    it);
  - `envs/readme.md` (staged kick training);
  - `pre-trained/WalkAndKick/K1_kick_inner.onnx`.
- `runswift_mjlab/src/mjlab/scripts/play_bhuman_kick.py`: our earlier port of
  their policy into our sim.

Our side: v56d/13450 and the stage-3 config.

## Side by side

| | B-Human K1 kick | Ours (v56d) |
|---|---|---|
| Scope | Separate kick policy, switched in within ~1.1 m of the ball (ball spawned 0.4–1.5 m away); separate walk policy brings the robot there | One policy: walk, search, kick, recover |
| **Ball** | **0.29 kg, radius 0.095 m** (±0.01 kg, ±0.01 m randomized) | **0.10 kg, radius 0.08 m** (mass ×0.65–1.46 → 0.07–0.25 kg) |
| Ball rolling model | `expected_vel = sqrt(2 · 0.3 · range)` (B-Human BallPhysics, friction 0.3) | `sqrt(2 · 0.95 · distance)` |
| Kick speed measured as | **3D** ball speed, peak over the first frames after contact | Horizontal speed at launch; since v55, lofted kicks are unpaid |
| Range command | Continuous range 0.5–20 m (log-uniform) + a "strong kick" flag (always 20 m) | One-hot short / medium / long |
| Speed reward | Gaussian on (expected − actual), σ ≈ 1 m/s, × signed direction reward; strong: linear in speed × direction | Capped speed / needed, linear match, rest-position reward, long-power ramp |
| Ball in observation | Position + **velocity** (scale-noised ×0–2), last position, kick direction angle | Position (vision, level frame), memory age; **no velocity** |
| Gait | Policy outputs a gait-frequency action, observes a gait clock (cos/sin) | No clock (cadence ~7 steps/s could not be tuned, v44) |
| Ball robustness events | Ball frozen in obs at kick (20 %); random ball teleports; random ball velocity adds; incoming ball speed up to 7.5 m/s at reset; rare immovable "heavy ball" | Vision dropout / delay; unseen relocation (v56); mild moving ball (eval only) |
| Ground | 60 % plane, 20 % random heights, 20 % 2 cm steps; friction 0.3–1.5; **contact compliance 0.5–1.5, restitution 0.1–0.9** | 60 % flat, 40 % 0–2 cm bumps; foot friction 0.7–1.4 |
| Torque | **Clipped to 50 / 50 / 30 / 60 / 30 / 30 Nm** (hip pitch / roll / yaw, knee, ankle ×2) "for sim2real" | Effort limits 68 / 76 / 38 / 112 / 38 / 38 Nm |
| Feet | Box collision feet, left / right bias variants | Our MJCF foot geoms |
| Training | Staged: reward sigmas from wide to tight (kick direction σ 1 → 0.05), penalties and robustness probabilities raised late, entropy and learning rate lowered | One fine-tune lineage, one change per run |

## What this explains about the real robot

1. **Weaker real ball speed: the ball.** B-Human trains with a 0.29 kg,
   0.095 m ball, almost 3× our 0.10 kg. If the competition ball is like
   theirs, every kick our policy learned is calibrated to a ball a third of
   the real mass. The same swing launches a heavier ball much slower, and a
   larger radius changes the strike height on the foot (loft). This alone
   could explain "weaker ball velocity in x" on the real robot. **The real
   ball's mass and diameter need confirming.**
2. **Torque headroom.** B-Human clips knee torque at 60 Nm and hip pitch at
   50 Nm. Our sim allows 112 and 68. If our kicks use more torque than the
   real motors sustain, the real swing is slower than in sim. To check:
   measure our kick torques per joint in sim.
3. **"Needed" speed per range.** With B-Human's rolling model (0.3), an 8 m
   ball needs 2.2 m/s. With ours (0.95), it needs 3.9 m/s. The right number
   depends on the real field's grass, and it sets every range's target
   speed. **Measure it** by rolling the ball at a known speed and noting the
   distance; that fixes the deceleration.

### Torque check (measured, v56d/13450, flat, nominal ball)

Peak actuator torque per joint group in the 0.3 s around each kick:

| Joint | B-Human clip | Kick p50 | Kick p99 | Kick max | Kick steps over clip | Walking p99 |
|---|---|---|---|---|---|---|
| Hip pitch | 50 Nm | 11.1 | **63.8** | **68.0** (our limit) | **5.1 %** | 23.4 |
| Knee | 60 Nm | 20.0 | **65.8** | **100.1** | 1.7 % | 35.8 |
| Ankle pitch | 30 Nm | 5.0 | 27.4 | 38.3 | 0.5 % | 19.1 |
| Hip roll / yaw, ankle roll | 50 / 30 / 30 Nm | ≤ 8.8 | ≤ 21.4 | ≤ 38.0 | 0 % | ≤ 22.3 |

- Walking stays well inside B-Human's clip.
- The strike does not: the hip pitch saturates our own 68 Nm limit, and the
  knee peaks at 100 Nm.
- So the fastest part of our swing depends on torques B-Human chose not to
  trust on the real K1. That is a second, independent reason the real kick
  is weaker than in sim.
- Recommendation #4 is therefore backed by measurement.

## How they kick, measured in our sim (`scripts/tools/kick_style_compare.py`)

B-Human's `K1_kick_inner.onnx` run in our stage-3 sim via `play_bhuman_kick.py`'s
wrapper, against v56d/13450.

**Setup:**
- Ball 0.4–1.5 m away, which is B-Human's kick-policy range.
- Flat ground, ball DR off.
- Ball 3D speed measured as the peak over the first 0.1 s after contact.

| | Ours v56d/13450 | B-Human kick |
|---|---|---|
| Kick-foot yaw vs kick direction | 11° (front / instep kick, 96 %) | **91° (side-foot / inside-foot kick, 97 %)** |
| Body speed at contact | 0.12 m/s (planted, standstill) | **0.58 m/s overall, 0.83 m/s on long kicks (kicks while walking into the ball)** |
| Kick-foot speed relative to body | 3.8 m/s p50 | 1.4 m/s p50 (the body's momentum does the work) |
| **Long kicks (≥ 8 m), ball 3D speed** | 5.57 m/s p50, 7.43 p90 | **8.24 m/s p50, 9.76 p90** |
| Long kicks, launch angle | −2° | +10.5° (low lofted drive) |
| Long kicks, peak torque p90 hip / knee | 68 / 79 Nm | **54 / 42 Nm** |
| Short / medium, ball 3D speed | 4.33 m/s p50 (overshoots) | **3.04 m/s p50 (scaled to the range)** |
| Short / medium, torque p90 hip / knee | 58 / 60 Nm | 20 / 22 Nm |
| Kicks within 20° | 91–92 % | 95–96 % |

**Ball mass, re-checked:** with B-Human's 0.29 kg / 0.095 m ball, our kick
did **not** slow down in sim (3D p50 4.63 → 5.13 m/s); nor did theirs much
(3.47 → 3.30). In MuJoCo the PD-driven leg is far heavier than either ball,
so ball mass barely changes launch speed. So **the light sim ball is not
shown to be the cause** of the weak real kicks. The torque gap (ours ≥ 64 Nm
p90 at hip and knee on long kicks, theirs 42–54) is the stronger
explanation. Matching the real ball is still right for calibration, but it is
no longer priority 1.

**The way B-Human kicks is the answer to our long-kick problem:**
- a side-foot strike while still walking forward;
- the body's momentum carries the ball;
- in our own simulator, with our PD gains, it reaches the 7–8 m/s goal
  (8.2 m/s median on long kicks);
- it uses about half our knee torque;
- it scales speed down for short passes;
- it is more accurate.

Our reward design blocks this style. `kick_quality` multiplies every kick
reward by exp(−(body speed / 0.4)²), which is 0.2 at 0.5 m/s and 0.01 at
0.83 m/s. That forbids exactly the momentum kick that works.

## Recommendations, in priority order

Each is one run on top of v56d/13450, judged on all objectives.

| # | Change | Why | Cost / risk |
|---|---|---|---|
| 0a | **Allow momentum kicks**: replace the standstill term in `kick_quality` with one that only penalizes body speed *not* toward the kick direction (and keep the post-kick fall penalties) | B-Human's long kicks reach 8.2 m/s with the body moving 0.83 m/s into the ball; our quality term pays them ~1 % | One reward change; watch falls after kicks |
| 0b | **Reward a side-foot strike**: a kick-foot yaw term toward ±90° to the kick direction at contact (B-Human's `kick_sole_yaw_ratio`, target 1.5705) | Larger, flatter contact surface: more accurate, less torque | Reward term; runner unaffected |
| 0c | **Use B-Human's kick as a teacher**: record its kicks in our sim (it already runs there) and either (i) add them as a near-ball AMP style clip, or (ii) behaviour-clone / DAgger the kick phase into our policy | Strongest route to the style; the data is free and in our exact sim | Medium effort; Apache-2.0 licensed (Booster Gym), check B-Human's terms for the trained weights |
| 0d | **Fastest path on the robot: hybrid**, i.e. our policy for walk, search and approach, switching to B-Human's kick policy within ~1.1 m (as B-Human deploys it) | Proven on the real K1 at RoboCup 2026 | Runner work (their 59 inputs, gait clock, handover); licence check |
| 1 | **Match the real ball** (no longer the main suspect, see above): the measured mass and radius (likely ~0.29 kg / 0.095 m), randomized ±10 %. Re-measure "needed" speeds with it | The likely main cause of weak real kicks; every power number so far is for a 0.1 kg ball | Kick speeds will drop in sim at first; the policy must relearn the swing. Needs the real ball spec |
| 2 | **Pay 3D peak ball speed** (as B-Human); replace the v55 loft factor by a mild cap (e.g. no pay above ~30° launch) | User: air balls are acceptable; this restores the power v55 removed, without "skyed" balls | Small; watch accuracy of lofted long kicks |
| 3 | **Calibrate rolling deceleration** from a field measurement; use it in `required_kick_speed` (and per surface in Phase 3) | Sets the correct speed for each range: "power according to range" | Needs one field measurement |
| 4 | **Clip torques to B-Human's sim2real values** (50 / 50 / 30 / 60 / 30 / 30), or at least check our kick torques against them first | The real swing may be torque-limited; a sim kick that needs 100 Nm at the knee won't transfer | May lower sim kick speed; check first (no training needed) |
| 5 | **Continuous range command in the existing slots**: slot 80 = log(range)/log(20), slot 81 = strong-kick flag, slot 82 = 0. Speed reward = Gaussian on expected − actual (σ ~1 m/s), strong = linear in speed | Fine speed control per distance, not three bins; matches B-Human; fixes short-pass overshoot | Same 83 dims, but the meaning changes: runner and parity check must change too |
| 6 | **Ball robustness events**: freeze the ball observation at kick (20 %); incoming ball speeds at reset (0–3 m/s, log-uniform, growing); rare immovable ball | Real vision loses the ball at the kick; balls arrive moving in a game | Low; one at a time (moving-ball lesson from v51) |
| 7 | **Ground contact softness and restitution** randomized (compliance 0.5–1.5, restitution 0.1–0.9 style) plus friction 0.3–1.5 | Part of Phase 3; matches B-Human's ground model for grass / dirt | Medium; slippery feet made v48b cautious, so keep low friction rare |
| 8 | **Ball velocity input** and **gait clock / frequency** | B-Human's moving-ball handling and cadence control depend on these | **Breaks the 83-input rule**: only if you decide to allow new inputs |

Not recommended to copy:
- **Splitting walk and kick into two policies:** ours handles search,
  approach and kick in one. Their split avoids long-range approach in the
  kick policy, but we've already solved that.
- **Their staged sigma schedule:** our curriculum is already well past those
  stages; the idea (wide → tight) is in our dense-reward lesson.

## Suggested order

1. Confirm the real ball spec and the field rolling distance (no training).
2. Torque check of our kicks against B-Human's clip values (no training).
3. #1 ball match + #2 3D speed, as one run if the ball spec is certain.
4. #3 deceleration, then #5 continuous range (with the runner change).
5. #6 robustness events, then #7 ground (merges with attack-plan Phase 3).

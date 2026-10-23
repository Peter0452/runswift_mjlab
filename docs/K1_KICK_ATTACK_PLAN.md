# K1 kick-loop: attack plan (2026-10-05)

Base: **v55b/12200** (flat 94.5 % of kicks within 20° of target, 1.05 goals,
no air balls, quick kicks, push-robust). Inputs stay at 83. One change per
run; each run is judged on every objective
(`scripts/tools/eval_kick_ck.sh` + the `search` and `loft` probes) and the
peak checkpoint is kept.

## Where we stand on the five asks

| Ask | Measured now | Main gap |
|---|---|---|
| Stronger long kick | Grounded long kicks 4.07 m/s, 0.80× what the target needs; air balls 8 % | Grounded kicks top out ~4–4.5 m/s with the current kick style |
| Varied ground | 60 % flat / 40 % 0–2 cm bumps; foot friction 0.7–1.4; ball rolling resistance ×0.5–2.5 | No slopes, no soft ground, one ball-on-ground model |
| Search by spinning | Ball moved out of view: re-found within 6 s **25 %**, median 4.0 s; while unseen 56 % walking forward (toward the old position), 20 % backward, 37 % turning | Policy trusts the stale memory |
| Moving ball | v51/v51b: training on it cost accuracy | Caused mostly by the search problem: nudged balls became lost balls |
| Ball moved by other robots | Never trained | Same: needs search first |

## Order and reasoning

Search comes first. The moving ball and the ball moved by other robots both
turn into "the ball is not where I last saw it". v51 failed because the
policy had no way to recover from that. Ground variety is independent and
low-risk. The long kick is the hardest; it goes last because its lever
(stepping into the kick) changes balance, and needs the varied ground
already in place.

### Phase 1 (v56): search by spinning, and stop trusting a stale memory

1. **Memory invalidation, same rule in training and runner:**
   - if the remembered ball position is inside the camera's view cone, within
     3 m, and nothing has been detected for 0.5 s, the memory is wrong;
   - set slot 74 (memory age) to 0 and slots 72–73 to 0, meaning "lost,
     search";
   - also invalidate after 4 s without a detection, wherever the memory
     points.

   This uses the existing slots, with no new inputs. **Needs a runner change**
   (`kick_loop_policy.py`): the same rule, mirrored, and checked with
   `parity_check.py`.
2. **Search reward, active only while the ball is lost (invalidated):**
   - pay turning speed, |wz|, up to the wz cap, in the direction the ball was
     last seen;
   - penalise backward walking;
   - give small credit for forward walking only after a full turn without
     finding the ball.
   - **Deliberately not a penalty on being lost**, since lesson 10 says that
     teaches avoiding the situation.
3. **Training scenario:** while the ball is unseen, sometimes move it (10 %
   chance per second), so the memory really goes stale.
4. **Pass bar:**
   - `search` probe: re-found within 6 s ≥ 70 %, median ≤ 2.5 s;
   - backward walking while lost ≤ 5 %, turning ≥ 60 %;
   - every other objective held.

### Phase 2 (v57): moving ball and other robots

Turn the v51b moving ball back on, plus "robot touches": while the robot is
**not** near the ball, a 5 % per-second chance the ball is knocked 0.5–2 m/s
in a random direction (seen or unseen). Search from Phase 1 handles the
unseen cases.

Pass bar:
- `--moving-ball` goals within 3 % of the static-ball goals;
- `search` probe held;
- every other objective held.

### Phase 3 (v58): varied ground

| Surface | How it's modelled | Range |
|---|---|---|
| Artificial grass | foot friction 0.8–1.2, ball rolling resistance ×1–2, slightly soft ground contact | default share |
| Real grass | foot friction 0.6–1.1, ball rolling resistance ×1.5–3, softer ground (contact solref time constant up) | |
| Dirt | foot friction 0.5–0.9, low ball rolling resistance, hard ground | |
| Slopes | `hf_pyramid_slope` with 0–4° slopes, 20 % of patches | |
| Bumps | existing 0–2 cm bumps, kept | |

- One surface is sampled per episode.
- Friction, rolling resistance and ground softness are applied together, so
  the combinations are physical.
- Lesson from v48b: 0.5 foot friction everywhere made the policy cautious.
  Keep the slippery cases a minority (dirt ~15 %) and watch goals.
- The speed the target needs currently assumes one rolling deceleration
  (0.95 m/s²). On real grass it is higher, so long kicks will under-reach
  there. Base the needed speed on the episode's surface (sim-only; it's a
  reward term, not an input).
- **Pass bar:**
  - each surface evaluated separately;
  - goals on flat artificial grass within 3 % of v55b;
  - falls on 4° slopes ≤ 2 %.

### Phase 4 (v59+): stronger grounded long kick

The current kick is from a near standstill (kick quality pays fully only
below ~0.4 m/s body speed), and the foot reaches ~5.4 m/s p90 with joint
speeds at ~45–48 % of the motor limits. Options, in order:

1. **Measure the ceiling first:** rerun the scripted kick probe (best
   possible grounded strike in this sim) with a short step-in. If grounded
   ball speed tops out near 5 m/s, say so and stop chasing 7–8 m/s.
2. **Allow a step-in for long kicks:** for long kicks only, relax the
   standstill requirement in kick quality, up to ~0.8 m/s body speed forward
   toward the target. Body momentum adds to foot speed. Watch falls after
   the kick.
3. **Kick motion reference:** retarget RoboNaldo's `right_kick.npz` (G1 front
   kick, from human video) to the K1 and use it as a near-ball style
   reference for long kicks only. It would also be the template for a later
   side-kick clip.
4. **Pass bar:**
   - grounded long kicks ≥ 1× the needed speed on median (≥ 5 m/s);
   - air balls ≤ 10 %;
   - accuracy, goals, falls and posture held.

## Risks

- **Runner parity:** Phase 1 changes what slots 72–74 mean when the ball is
  lost. Training and runner must use the identical rule, or the robot sees
  inputs it never trained on. Check with `parity_check.py` before deploying.
- **Caution:** every new kind of randomization so far cost 5–20 % goals at
  first (v48b, v50, v51). Keep each mild, one per run, and stop early if
  goals drift.
- **Unknowns about the real field:** grass length and ball rolling distance.
  A simple measurement would anchor Phase 3: roll the ball at a known speed
  and note how far it goes.

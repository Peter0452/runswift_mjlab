# K1 kick-loop policy: lessons learned

What we tried, what worked, what did not, and why. This file is the distilled
version; the full run-by-run record (numbers for every checkpoint) is
[K1_KICK_STAGE3_NOTES.md](K1_KICK_STAGE3_NOTES.md), and the policy's
inputs and outputs are in [K1_KICK_LOOP_POLICY_IO.md](K1_KICK_LOOP_POLICY_IO.md).

Last updated 2026-10-03 (through v54b).

## 1. The task

One policy for the Booster K1 that walks to the ball, kicks it toward a target,
recovers, finds the ball again and repeats. Trained in mjlab (MuJoCo Warp) with
AMP-PPO and the Muon optimizer: AMP style from a walking motion set keeps the
gait natural, and the style is switched off near the ball so the kick is free.
Task `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`; all runs are
fine-tunes in one lineage (v1 → v54b), each resumed from the best checkpoint
of an earlier run.

- **83 inputs:** IMU (gyro, gravity), joint positions and velocities, last
  action, ball x/y in the robot's level ground frame, ball memory age, speed
  limits (vx, vy, wz), kick direction (cos, sin), kick range (short / medium
  / long). **22 outputs:** joint position targets. The head is driven by a
  scripted tracker in both training and the runner.
- **Objectives:**
  - kick quickly, with power matched to the range: short 1–4 m soft, medium
    4–8 m, long ≥ 8 m as hard as possible (7–8 m/s goal);
  - run at the speed limits (up to 2.0 m/s forward);
  - stay upright with no lean at about 0.52 m height, with a gait as smooth
    as the gold AMP walk;
  - be accurate and fall rarely;
  - transfer to the real robot.

## 2. Where we are

| Model | Strength | Weakness |
|---|---|---|
| **v53/10700** (recommended for the robot) | Flat 91.5 % of kicks within 20° of target, 1.05 goals per episode. Long kicks 5.18 m/s (nominal 0.1 kg ball), 10.7 % reach 7 m/s. Lean +0.7° at 1.0–1.5 m/s. Smoothest walking in the runner sim. | Short passes overshoot (stop ~5.5 m past the target). Waits ~3 s at the ball before kicking. Only ~0.75 m/s when the limit is 1.6–2.0 m/s. |
| v54b/11200 (in progress) | Flat 94 % within 20°, 1.12 goals per episode. Kicks sooner (2.5 s). Passes move toward the right speed. | Long kicks dropped to 4.1 m/s. |
| v50d/10200 | Previous robot candidate; robust to pushes. | Leans +2.2° at speed. |
| v47/8800 | Strongest kick ever (5.39 m/s). | **Do not deploy:** it was trained with the wrong ball frame (see 4.1). |

Still open:
- running at the speed limit;
- kicking quickly;
- long kicks averaging 7–8 m/s (the mean is ~5);
- side kicks;
- cadence (~7 steps/s against the gold walk's 4.6).

## 3. Reward design lessons

These cost the most runs to learn.

1. **A reward must give signal at the policy's current behaviour.** A sharp
   band or Gaussian centred far from what the policy does is flat (≈ 0) where
   the policy is, so nothing changes.
   - v54: a stop-position reward exp(−(miss / 0.5 m)²) when passes missed by
     5–6 m → no change at all.
   - v54b: exp(−miss / 2 m) plus a linear speed match → passes improved
     within 250 iterations.
   - The same happened earlier with height and speed bands.
   - Prefer monotonic ramps and linear slopes that reach back to current
     behaviour.
2. **Penalties on a band edge only act outside the band.** v50d leaned +2.2°
   inside a −5…+3° pitch band, so only the tail paid. Doubling the weight
   (v51) did nothing; moving the edge to +1° (v53) fixed the lean. **Move the
   edge, not the weight.**
3. **The goal definition shapes behaviour more than any shaping term.** A goal
   that counts the ball *passing* the target, combined with randomized ball
   mass and rolling resistance, made blasting every kick the safe choice (a
   soft pass sometimes stops short and scores nothing). Short passes were
   kicked at ~1.8× the needed speed.
4. **Tie rewards to outcomes, not motions.**
   - Swing-speed reward alone produced fast swings that missed the ball's
     centre (v49): ball speed fell while the swing stayed fast. Fixed by
     scaling with transfer, i.e. ball speed ÷ foot speed (v50).
   - The aim reward paid weak taps as much as strong kicks, so the policy
     made many weak taps (v43/v44). Fixed by scaling aim by power (v45).
5. **Paying enough is what moves a skill.** Raising the long-kick power weight
   900 → 2000 (v47) moved swing speed where a gradient alone (v46) did not.
   Until then a faster swing paid ~+4.5 per long kick against ≥ 50 for avoiding
   a fall after the kick.
6. **Normalize and two-side speed terms.**
   - Signed walk-speed reward, so shuffling back and forth can't farm it.
   - Normalized by min(cap, 1 m/s).
   - Cap tracking two-sided.
   - Squared penalties capped, so rare states can't dominate.
7. **Gating windows decide what the policy can practise.** Cap tracking only
   beyond 2.5 m from the ball, while balls spawn 1–4 m away, meant the policy
   almost never had room to reach cruise speed (0.75 m/s at 2 m/s caps).
8. **Some skills cannot be discovered by shaping alone.** Side kicks (v52,
   v52b):
   - relaxing the "line up behind the ball" terms changed nothing;
   - a direct, accuracy-gated bonus for side kicks reached only ~3 % of kicks,
     ≤ 18 % accurate.
   The policy has never seen a sideways swing. That needs a motion reference
   (a K1 side-kick clip), not more reward.
10. **Penalising a bad action teaches avoiding the action.** A penalty per
    underpowered long kick (v54c, −800) first restored power (5.83 m/s at
    11450), then the policy learned that not kicking long avoided it: fewer
    long kicks, longer waits, goals 0.98 → 0.69 by 11700. Keep such
    penalties small next to the reward for doing the action, or pay the good
    version instead.
11. **Measure what the real objective is, in all three axes.** Kick speed was
    the ball's horizontal speed at launch, so lofted kicks counted as fast.
    v53 lofted 73 % of long kicks (41 % above 15 cm) and was weaker on the
    real robot. Track launch angle and air time, and pay ground speed only.
12. **Reward the net effect, not a rate that can oscillate.** A search reward
    on turning speed |wz| (v56b) was farmed by wiggling the heading back and
    forth: 3.7 rad of "turning" in 6 s, net rotation ~0, ball still behind.
    Pay signed progress (net rotation in one direction), and check behaviour
    with a step trace, not only the summary metric.
13. **Let an existing skill do a new job by changing what it sees.** A turning
    reward never produced a search spin (v56–v56c: net 0.34 rad per search).
    Showing a virtual ball beside the robot while the real one is lost (v56d)
    reused the turn-toward-the-ball skill: net turn 1.8 rad, balls behind found
    by turning. The same rule must then run in the robot runner.
14. **Learn from the reference, then transcend it, by benchmark only.**
    Adopting B-Human's techniques (momentum, side-foot, planted support,
    mid-kick starts) is a means, not the goal. Every adoption or ours+theirs
    combination is accepted only if the fixed benchmark
    (`scripts/tools/kick_benchmark.py`) shows it beating B-Human on the
    head-to-head metrics with no regression on the rest.
15. **The benchmark predicted the robot.** On 2026-10-06 the benchmark-promoted
    x4_g004_70 kicked accurately on the real K1 and the rejected evo_g014/14550
    kept missing. Trust the gates; deploy promoted models.
16. **A benchmark against a reference must give both sides the same inputs.**
    For weeks B-Human was compared with the true ball while ours had the
    camera. Under equal camera perception ours already won most head-to-head
    metrics; under equal perfect perception B-Human's technique still won.
    Compare both ways before concluding.
9. **Never use absolute height on uneven terrain.** v48's height term used
   world z; robots standing on raised terrain produced −21.8 penalties, the
   adaptive learning rate collapsed and the run died. Measure height relative
   to the robot's own lowest foot.

## 4. Sim-to-real lessons

1. **Match the observation frame exactly.** Vision (runswift `base_link`)
   reports the ball in a level, yaw-only frame on the ground; training used the
   trunk frame. A 5–10° lean moved the training ball reading 4–9 cm, mostly in
   the last steps before contact. Fixed in v49; all earlier models read the
   ball wrong on the robot.
2. **Check every input slot on the robot before blaming the policy.**
   - The "walks to the ball but never kicks" robot log was four joint inputs
     reading exactly 0: the runner used `/joint_states`, which lacks the head
     joints.
   - Reproduced in the runner sim: zeroed joints give 0 kicks, correct joints
     give kicks every time.
   - Fix: `--joints-from-low-state`; at start-up, check that slots 0, 1, 2, 6
     are non-zero.
3. **Exported scales must be exact.** Action scales were written with 3
   decimals in ONNX metadata (0.2125 → 0.213); now 6. A parity check (training
   env vs runner, slot by slot) catches this class of bug.
4. **Don't change domain randomization because another config differs.** The
   kick DR is inherited from the AMP walk, which transfers well. Change DR only
   with robot evidence.
5. **Keep vision noise small and realistic.** 2 % detection dropout and
   0–2 step delay were fine. 5 % dropout plus slippery feet (friction 0.5)
   made the policy cautious, with ~20 % fewer goals (v48b).

## 5. Evaluation lessons

1. **Training reward curves lie.** They swing ±15 % over a few hundred
   iterations: v50d's aim reward went 0.35 → 0.30 → 0.34 and it was the best
   model. Judge only by evaluation.
2. **The best checkpoint comes 250–500 iterations after a resume.** By ~1000
   the policy drifts to fewer, slower, more cautious kicks (v50d, v51b, v52,
   v52b, v53). Evaluate every 250 iterations and keep the peak; don't train
   long.
3. **Use two seeds before calling a winner.** One seed varies by a few
   percent; some checkpoints are lucky (v52/10450 looked better in power and
   posture than it was).
4. **Measure on the right conditions.**
   - Kick speed with the **nominal 0.1 kg ball on flat ground**, because the
     randomized 0.05–0.25 kg ball hides progress.
   - Compare models **on the same config**: after enabling a feature in the
     base config, every eval mode inherits it. v51 was briefly judged against
     a v50d number measured without the moving ball.
5. **Split aggregate metrics before concluding.** v53's runner-sim "tilt p90
   7.7°" looked like wobble. Split into walking and near-ball, walking was the
   steadiest yet and the extra tilt was the harder kick swing.
6. **Measure behaviour per range and per speed bin.** Per-range analysis
   showed the "hesitant weak kick" was really blasting short passes, plus a
   ~3 s wait at the ball that was the same for every range. Per-speed-bin
   analysis showed lean and heel-up only appear above 1 m/s.
7. **Test the scenario a feature targets, and the old checks too.** Every run
   gets:
   - bumps, flat, a push test and a moving ball;
   - side drills and nominal-ball power;
   - lean / height per speed;
   - cap tracking and top speed;
   - per-range pass control;
   - the runner-sim bench.
8. **A "smooth" policy can just be standing still.** Track idle time at a far
   ball alongside jitter.

## 6. Process lessons

1. **One change per run** where possible, so the cause of a gain or loss is
   known. When two changes ship together and results drop, split them (v50 →
   v50b → v50c → v50d found that pushes, not the strike-efficiency term, cost
   accuracy).
2. **Stop broken runs early.** v51 drifted from the start; stopping at ~400
   iterations and redesigning (v51b) saved hours.
3. **Training on a feature can cost more than it buys.** The moving ball (v51,
   v51b) cost accuracy, while the untrained v50d already coped with a mild
   moving ball (0.95 vs 0.97 goals). Check whether the current model already
   handles a scenario before training on it.
4. **Curricula must count their own steps.** On resume the runner sets the
   global step counter to the checkpoint's value, so a step-based ramp jumped
   to its end. The kick command now counts its own steps.
5. **Don't leave stray runs going.** A forgotten run in parallel halved
   training speed for two hours.
6. **Kill processes by PID in a separate command.** `pgrep -f "run-name X"`
   matches its own shell when the same command also launches "X…", killing the
   shell before the launch. This happened three times.
7. **Keep evaluation tools in the repo, not a temp directory.** The scratch
   probes were wiped between sessions and had to be rebuilt
   (`scripts/tools/kick_probes.py`, `scripts/tools/eval_kick_ck.sh`).
8. **Write insights down every run, with numbers.** The notes file is the
   reason these lessons are recoverable.

## 7. Physics and skill limits seen so far

- **Long-kick speed:** the best mean was ~5.2–5.4 m/s, with p90 ~8.3 m/s and
  10–13 % of kicks ≥ 7 m/s. Kicking-foot speed is ~3.9 m/s median, ~7 m/s max;
  a scripted kick probe in the same sim was the reference for what the motors
  allow. The 7–8 m/s mean is not reached; the fastest reliable kick is the
  current answer.
- **Cruise speed:**
  - ~1.1–1.4 m/s on a long chase;
  - upright posture (pitch ≤ +1°) cost some top speed: 1.39 m/s for v47
    against 1.13 for v53;
  - whether a 2 m/s gait is possible upright is still unknown (v55 will test
    it).
- **Cadence** stays ~7 steps/s. Air-time rewards did not change it (v44); a
  gait clock input would be needed, which the fixed 83 inputs don't allow.
- **Heel-up** of ~30 % at 1.0–1.5 m/s in every model since v47. It is likely
  normal toe-off at speed (runner sim at low caps: 0.1–0.3 %). Not chased
  without robot evidence.

## 8. Next steps and how to judge them

1. **v54b:**
   - find why long kicks lost power, and keep the short-pass speed cap off
     long kicks;
   - target v54b's accuracy and quickness with v53's power.
2. **v55, run at the speed limit:** a braking profile, target speed = min(cap,
   1.2 × (distance − 0.6 m)), active from 1 m out. It is coded and switched off
   (`TRACK_BRAKE_PROFILE`). Watch lean and falls.
3. **v56, kick quickly.**
4. **Side kicks:** record a human side-kick video → GVHMR → GMR retarget to the
   K1 → near-ball style reference. RoboNaldo's `right_kick.npz` is a G1 front
   kick, so it is not usable directly.
5. **Robot test of v53/10700** with `--record-kick-obs`. Real data should
   steer the next changes more than any further sim tuning.

## 9. Why runswift's kick benchmark disagreed with ours (2026-10-07)

runswift/benchmarks/kick_policies (2026-10-06) reported x4_g004_70 at 20 % first
strikes within 15° (B-Human 94 %); our benchmark had x4 at 78-85 % within 20°.
Bisected with `scripts/tools/runswift_scenario.py` (their 36-task protocol in our
sim) and a local copy of their fixture with switches:

| x4 on their grid | first strike ≤ 15° |
|---|---|
| their fixture, as published | 7/36 (19 %) |
| + our training torque limits | 7/36 |
| + training foot mesh collision | 6/36 |
| + our exact training MjModel | 7/36 |
| + speed caps 1.2/1.0/1.25 (published 0.5/0.3/0.6) | 13/36 |
| **runner joint-target clip removed** | **31/36 (86 %)** |
| our sim, their protocol | 90/108 (83 %) |
| our sim + the runner's joint-target clip | 31/108 (29 %) |

- **Cause 1 (the big one): `walk_policy_amp_v1._action_to_absolute` clips every
  joint target to `Q_ABS_LIMITS` (the joint ranges). Training never clipped.**
  x4 commands hip roll up to 0.38 rad past the 0.40 rad inward limit on ~0.6 % of
  steps, around kicks; clipped, its kicks go 20-40° off. The robot runs the same
  runner code, so the robot sees this too.
- **Cause 2: actuator delay.** Training delays motor commands 10-40 ms; the
  fixture has none. x4 is insensitive; sty_power/17149 drops from 82 % to 47 % in
  our sim without delay (fixture: 50 %).
- Not causes: torque limits, foot collision shape, body / joint / contact model,
  integrator or timestep (2 ms Euler vs 5 ms implicitfast), observation or action
  mapping (checked field by field), ONNX vs checkpoint (3e-6).
- sty_power/17149 is robust to the clip (84 % → 82 % in our sim).

Lesson 17: **benchmark the deployed action path, not the training one.** Any
transform the runner applies (target clip, filters, limits) must be in training
and in our benchmark, or the policy can learn to depend on what deployment removes.
Lesson 18: **a policy that only works inside the training delay range is
brittle**; test (and train) delay ranges that include zero.

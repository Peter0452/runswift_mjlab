# B-Human kick port

A faithful reproduction of B-Human's K1 kick training (Booster Gym on Isaac
Gym, `MachineLearning/IsaacGymRL`) on our simulator, as a baseline to compare
with and mix into our kick.

Sources: `docs/K1_BHUMAN_KICK_PORT.md` (use, file map, known differences),
`docs/K1_KICK_VS_BHUMAN_2026-10-09.md` (side-by-side with our kick loop),
`docs/K1_KICK_BHUMAN_COMPARISON.md` (older, 2026-10-05), session memory
`bhuman-kick-port`.

## Tasks and tools

- `Mjlab-BHuman-Kick-Booster-K1` (= Stage1) and `-Stage2`, `-Stage3a`,
  `-Stage3b`, `-Stage4`, `-Stage5`, `-Stage6a`, `-Stage6`: cumulative stages
  from B-Human's readme (`src/k1/tasks/bhuman/stages.py`).
- Own runner `BHumanPpoRunner` (loads Booster Gym `.pth` directly via
  `--agent.bhuman-checkpoint`); optional `--agent.decap`, `--agent.amp`.
- Eval `scripts/tools/eval_bhuman_kick.py`; benchmark v2 to B-Human's spec
  `scripts/tools/bench_bhuman_kick_v2.py` → `docs/benchmarks_bhuman_kick/`.
- `src/mjlab/scripts/play_bhuman_kick.py`: runs B-Human's ONNX inside our
  kick-loop and dribble envs (used as a probe and teacher).

## Validation

B-Human's own `K1_kick_inner.pth` in the port (1024 robots × 40 s): aim error
p50 3.0–3.5°, 79–81 % within 10° (89–93 % on a plane without noise), falls
0.2–0.3 per robot-minute; benchmark v2 score 0.925 vs their own 0.927. Re-run
this check after changing the port.

## How it differs from our kick loop (summary)

| | B-Human | Ours |
|---|---|---|
| Scope | separate kick policy, switched in within ~1.1 m | one end-to-end policy |
| Outputs | 12 legs + gait frequency; arms scripted | 22 joints, head scripted |
| Gait | **clock input**, frequency chosen by the policy | free, AMP style |
| Ball input | xy, last xy, **velocity** | xy + memory age, camera model |
| Torque | hard clip 50/50/30/60/30/30 Nm | same clip since 2026-10-07 |
| Latency | none | 0–40 ms |
| Training | manual staging: sigmas wide → tight, penalties up late | evolution loop, fixed sigmas |

Measured (2026-10-09): with camera noise every recent checkpoint of ours beats
B-Human on accuracy, falls and time to kick; with a perfect ball B-Human wins
aim (3.7° vs 4.7°+) and long power (5.7 vs ≤ 5.0 m/s). On the official runswift
goal grid our h012_x50 scored 170/180 vs B-Human 165.

## What B-Human has that we could still adopt

Cheapest first (from the 2026-10-09 comparison): final-stage tight sigmas
(direction 0.05 rad², speed ×0.5), annealed rather than jumped; energy costs
and a stronger action-rate penalty; ground randomisation (friction to 0.3,
restitution, 7.5 cm terrain); wider mass / CoM randomisation; kick-moment
robustness (freeze the ball input after the kick); symmetry loss; sole-yaw
shaping. Not adoptable under the 83-input rule: ball velocity input, gait clock,
continuous range input.

## Lessons

- B-Human's side-kick shaping (sole yaw target 90°, σ 1.0 → 0.1, weight
  staged down) works for them; for us a rising target-angle curriculum taught
  the inside foot, a fixed target did not.
- Its actions can't be imitated by our clock-free policy (dribble v41 / v43):
  see [dribble](dribble.md#what-has-been-learned).
- Don't use the `bhuman_side` clips as a motion prior for the port: they are
  B-Human's own policy rollouts.
- Their `K1_walk_start_for_kick.pth` falls 2–4 times per robot-minute in our
  stage-1 env (unverified against Isaac Gym).

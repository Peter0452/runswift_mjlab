# Kick (kick loop)

One end-to-end policy that searches for the ball, walks to it, kicks it toward
a target, recovers and repeats. The main kick line of the project.

Sources: `docs/K1_KICK_STAGE3_NOTES.md` (run-by-run, 120 KB),
`docs/K1_KICK_LESSONS.md`, `docs/K1_KICK_LOOP_POLICY_IO.md`,
`docs/K1_KICK_BENCHMARK_V2.md`, `docs/evolution/HANDOFF.md`,
`docs/K1_KICK_STYLES.md`, `docs/K1_KICK_VS_BHUMAN_2026-10-09.md`.

## Current best

| Model | Why | Where |
|---|---|---|
| **h022_c2_18450 (champion)** | Promoted by the user 2026-10-09. Quietest landings; camera-perception runswift goal grid 90/90 with 0 falls; long power and landings better than the blends | `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`; `k1_policy_runner/kick_loop_models/k1_kick_loop_h022_c2_18450.onnx`; `start_kick.sh` points at it |
| h012_c1_18000_x50 (blend) | Best on the official runswift goal grid: 170/180 goals with FOV gate + soft start, caps 1.5/1.5/1.0 (B-Human 165) — but −47 on bench v2 (long power, landings) | `logs/rsl_rl/k1_kick_stage3_amp/blends/h012_c1_18000_x50.pt` |
| h011_c2_17750 | Long kick 4.4–4.5 m/s 3D, ~0.8 s faster to kick; regresses action rate and style choice. Used as the dribble's kick teacher | `.../2026-10-08_12-04-08_h011_c2/model_17750.pt` |
| x4_g004_70 (v1 champion) | Kicked accurately on the real robot while the rejected evo_g014 kept missing (2026-10-06) | `.../2026-10-06_08-40-00_blend_x4_g004_70/model_14200.pt` |
| swa_v15v16_9100 (self-play) | Self-play fine-tune; +0.019 goal share over h022 under the same scripted controller (6/6 seeds, p ≈ 0.008); 86 inputs | see [self-play](selfplay_striker.md) |

Full table with every deployed model: [../models.md](../models.md).

## Training pipeline

Three stages share one 83-input actor layout, then optional self-play:

1. **Stage 1** `Mjlab-Velocity-Kick-Stage1-Amp-DA-Muon-Booster-K1`: walk; the
   kick slots are placeholders.
2. **Stage 2** `Mjlab-Velocity-Kick-Approach-Amp-DA-Muon-Booster-K1`: walk to
   the ball and line up on the ball→target line, ball only from the camera.
   Notes: `docs/K1_KICK_APPROACH_NOTES.md`.
3. **Stage 3** `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: the kick
   loop. Code `src/mjlab/tasks/velocity/mdp/kick_loop.py`.
4. Self-play fine-tune (86 inputs): [selfplay_striker.md](selfplay_striker.md).

**Stage handoff (must do):** slots a stage held constant have normaliser
std 0 and untrained weights; a plain resume collapsed stage 2 (KL 22,
12-step episodes). Use

```sh
uv run python scripts/prepare_warmstart.py --input <ckpt> --output <newrun>/model_0.pt \
  --reset-obs-dims 74:83 --normalizer-count 10000000
# then train with --agent.resume True --agent.warm-start True
```

## Inputs and outputs (83 → 22, 50 Hz)

Full table: `docs/K1_KICK_LOOP_POLICY_IO.md`.

| Slots | Content |
|---|---|
| 0–5 | gyro, gravity in trunk frame |
| 6–71 | joint pos (− default), joint vel, previous action (22 each) |
| 72–73 | ball xy in the level ground frame, origin between the feet (runswift `base_link`) |
| 74 | ball memory age exp(−t/2 s) |
| 75–77 | speed caps \|vx\|, \|vy\|, \|wz\| |
| 78–79 | kick direction (cos, sin) from the last-seen ball |
| 80–82 | range one-hot: < 4 / 4–8 / ≥ 8 m |

- Head actions are overridden by a scripted ball tracker (same code in
  training and the runner).
- No odometry: when the ball is unseen, memory is the last sighting turned by
  the IMU yaw change (`memory_odometry=False`). A never-seen ball is zeros
  with age 0. While the ball is lost, a **virtual ball** beside the robot
  reuses the turn-to-ball skill as a search spin (v56d).
- The dribble policy reuses this layout, and slots 80–82 = (0, 0, 1) mean
  "long kick" in both, which is what lets the kick loop teach the dribble.

## Rewards (stage 3, champion recipe)

About 54 active terms plus AMP style (weight 0.3, off near the ball and
around kicks). The ones that matter most:

- Kick outcome: `long_kick_power` 4000, `kick_goal` 1500,
  `style_advantage` 1500, `kick_rest_accuracy` 1000, `kick_direction` 900,
  `kick_vel` 900, `long_kick_speed_linear` 800; `kick_fall` −2500.
- Approach / search: `approach_close` 100, `approach_align` 80, `walk_speed`,
  `walk_speed_track`, `walk_speed_limit` −20, `search_turn`.
- Safety and posture: `fall` −1000, `alive` +2/s, `trunk_tilt`,
  `walk_stance_width`, `knee_valgus`, `foot_flat` (60 ms settle),
  `touchdown_speed` −15, `torque_over_soft_limit`, `dof_pos_limits`.
- Smoothness of the deployed (deterministic) action comes from CAPS
  (`caps_temporal_coef`, `caps_spatial_coef`, `caps_near_ball_scale`), not
  from `action_rate_l2`, which acts on noisy sampled actions.
- Speed caps since 2026-10-23: chase caps (lateral 2 m/s, yaw 3 rad/s), see
  [objectives](../objectives.md).

## Ball

Default: our ball (0.08 m / 0.1 kg nominal, randomised 0.07–0.13 m and
0.05–0.45 kg, shell inertia). `K1_BALL=bhuman` switches the kick, approach
and dribble tasks to B-Human's ball (0.095 m / 0.29 kg, solid), the ball
future training should use. The one run trained on it so far,
`k1_kick_stage3_amp/2026-10-16_01-30-01_h022_from_v54c_b`, needs
`K1_BALL=bhuman` to replay. On B-Human's ball the champion scores clearly
lower (goals 1.1 → 0.9, long kick 4.6 → 3.8 m/s, passes ~2 m long, knee
peak +35 %), so expect a retraining step when switching.

## How it is judged

- **Benchmark v2** (`scripts/tools/kick_bench2.py`, scored by
  `fitness_v2.py`): the policy as the robot runs it — runner joint-target clip,
  B-Human torque clip, lost-ball rule, scripted head; low and high caps;
  camera / world / perfect perception; zero and typical delay; falls counted
  from t = 0; bootstrap CIs, "better" only when CIs separate. Tracks:
  near_grid, close_any, approach (any bearing incl. behind), goal_grid,
  full_loop (+ push, moving ball, late detections, bumps). Results in
  `docs/benchmarks_v2/*.json`.
- **runswift fixture** (`.cache/runswift_harness/`, `scripts/tools/rsw_aligned.sh`,
  `kick_bench2_cpu.py`): proxy soft gate on near grid and goal grid.
- Promotion (`evolve_kick.confirm_and_install`): second-seed v2 bench, then
  the runswift gate, then install + ONNX export.

## Evolution system (2026-10-07 →)

`scripts/tools/evolve_hier.py` on top of `evolve_kick.py`: L0 genes, L1
reward templates (JSON reward grammar, `mdp/reward_grammar.py`), L2
constraints, L3 scenarios, L4 `claude -p` designer, L5 catalogue atoms
(`docs/approach_catalogue.yaml`). A frame trains up to 3 children (≤ 500
iterations each), screens them, benches the best, and tries 70/30, 50/50,
30/70 blends with the champion. Run under `scripts/tools/hier_supervisor.sh`;
stop with `docs/evolution/STOP_AFTER_FRAME`. **Read `docs/evolution/HANDOFF.md`
before touching it**, and log interventions in `docs/evolution/monitor.md`.

Outcome so far (`docs/evolution/hier_report.md`, experience README): 23 hier
frames, promotions only via blends or by the user; single gene changes rarely
survive the no-regression gate. See
[lessons/training_eval.md](../lessons/training_eval.md#blending-and-the-evolution-loop).

## Where it stands (gaps)

- Long-kick power: champion long 3D ~4.2–4.6 m/s (h011 4.4–4.5); B-Human
  ~4.3 with camera, 5.7 with a perfect ball. Reward weights alone (pow_a /
  pow_b, 800 it) did not reach 7–10 m/s, and harder kicks went out more.
  Scripted swings show 7–12 m/s is physically possible, so it is a
  balance/skill problem.
- Running at the high caps (approach cap use ~30 %); low-cap time to kick.
- Heavy-ball long kick; shots just wide on the official goal grid (long shots
  from ~11.5 m need < 6° error).
- Single kicks from standstill off the runswift stick-foot fixture still lose
  to B-Human (near grid).
- Cadence ~7 steps/s vs the gold walk's 4.6; a gait clock input is not
  allowed under the 83-input rule.

## Kick styles

Detected at contact: inside foot (toe-out yaw vs the kick line) and hop (no
foot on the ground). A rising target-angle curriculum (20° → 90°) taught the
inside foot where a fixed 90° reward found 1 %. Free style choice collapses
onto the most rewarded style (hop). Inside-foot training cut long power
(6.99 → 4.70 m/s). Details: `docs/K1_KICK_STYLES.md`.

## Tools

| Tool | Use |
|---|---|
| `scripts/tools/kick_bench2.py run NAME CK --size quick\|full` | benchmark v2 (GPU) |
| `scripts/tools/kick_bench2_report.py`, `fitness_v2.py` | reports, fitness vs champion |
| `scripts/tools/eval_kick_loop.py`, `eval_kick_ck.sh`, `kick_probes.py` | per-checkpoint evals and probes |
| `scripts/tools/kick_anatomy.py`, `kick_style_compare.py`, `kick_style_gallery.py` | kick technique analysis |
| `scripts/tools/blend_checkpoints.py`, `blend_search.py` | weight blends |
| `scripts/tools/reward_lint.py`, `reward_budget.py`, `watch_run.py` | pre-training lint, reward budget, watchdog |
| `scripts/tools/onnx_parity.py`, `lost_rule_parity.py`, `export_onnx.py` | deployment parity and export |
| `k1_policy_runner`: `parity_check.py`, `sim2real_bench.py`, `gait_bench.py`, `--kick-record` | runner-side checks |

## Legacy kick tasks

Kept because they produced checkpoints that are still referenced:

- `Mjlab-Kick-Approach-Booster-K1`, `Mjlab-Kick-Near-Booster-K1`: the
  September walk-to-ball and near-ball kick (`docs/K1_KICK_TRAINING_NOTES.md`);
  produced the curated `plant1_65600` and `stance_81800` (now only on the
  archive branch) and the deployed `k1_v24_*` ONNX.
- `Mjlab-Kick-WalkAmp[-Amp]-DA-Muon-Booster-K1`: kick on the walk-AMP stack
  (`src/mjlab/tasks/kick/DESIGN_kick_on_walk_amp.md`, `PROBLEM.md`).
- `Mjlab-Tracking-Flat-Booster-K1-Kick[-Box,-Stage2]`: motion-tracking kick
  (`docs/K1_KICK_TRACKING_NOTES.md`). Stage-2 kicker
  `logs/rsl_rl/k1_kick_tracking/2026-09-29_08-23-57/model_99000.pt`; the
  KickHandoff walk replays its frozen policy.

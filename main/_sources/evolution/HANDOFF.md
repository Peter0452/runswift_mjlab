# K1 kick evolution: handoff for the next agent

Read this first, then the tail of `monitor.md` (interventions, newest last) and
`log.md` (loop events). Update the "Current state" section whenever you
intervene, and log every intervention in `monitor.md`. Last update: 2026-10-09 05:14 AEDT.

## What the system is

- One end-to-end K1 kick policy (no policy switching), trained with AMP-PPO on
  `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`. Deployed through
  `../k1_policy_runner` (branch `kick`) as ONNX.
- `scripts/tools/evolve_hier.py`: a hierarchical evolution loop (L0 gene
  mutation, L1 reward templates, L2 constraints, L3 scenarios, L4 `claude -p`
  designer, L5 catalogue atoms in `docs/approach_catalogue.yaml`), built on
  `scripts/tools/evolve_kick.py`. It runs under `scripts/tools/hier_supervisor.sh`,
  which restarts it on crashes (at most 6 times) and stops on
  `docs/evolution/STOP_AFTER_FRAME` or its time limit.
- A frame trains up to 3 children from a parent: 2 in parallel, then 1 more;
  each runs up to 500 iterations with a screen every 50–100. The best child
  gets the full benchmark. If it is not promoted, 70/30, 50/50 and 30/70
  blends with the champion are screened, and the best blend gets the full
  benchmark. A frame takes about 2 h.
- The judge is benchmark v2 (`scripts/tools/kick_bench2.py`, GPU, deployed
  action path, fixed low/high speed caps, camera/world/perfect ball, 0–40 ms
  delay). It is scored by `scripts/tools/fitness_v2.py` against the champion:
  primary objectives ×3, safety ×2, the rest ×1. A **regression** is a metric
  worse than its tolerance with separated CIs; any regression blocks
  promotion.
- Promotion (`evolve_kick.confirm_and_install`): a second-seed v2 bench, then
  the runswift proxy soft gate (falls, accuracy, 6/9 m kick speed; tolerances
  in `RSW_TOL`), then it installs a run dir and exports ONNX to
  `../k1_policy_runner/kick_loop_models/k1_kick_loop_<name>.onnx`.
- The experience repository (`docs/experience/`, `scripts/tools/experience.py`)
  records context, action, result, impact and lesson for every frame. It feeds
  L4 and the proposers.

## User objectives and standing decisions (do not change without asking)

- Optimise accuracy, time to kick and power without compromising anything
  else; beat B-Human convincingly, then keep improving. Falls stay low and the
  robot stays upright (~0.52 m); run at the speed caps; light and heavy ball.
- Power by range: 1–4 m and 4–8 m matched to the distance; ≥ 8 m uncapped (at
  least B-Human's power); air balls are fine.
- The policy itself chooses its kick style (front, side foot, hop) per
  situation from speed and accuracy; no style is forced by range.
- Runswift is a proxy soft gate: we may be a little worse on its ideal
  assumptions, but not on falls, accuracy or kick speed. Kick speed is gated
  on the 6/9 m tasks only.
- **Action rate must stay stable and smooth without compromising the rest
  (user 2026-10-08).** It is a safety metric on full_loop, close_any and
  approach (tolerance 0.006).
- **Headline (user 2026-10-08): kick faster, more accurately and more
  powerfully than B-Human for diverse ball sizes**, without losing stability,
  no falls or smooth actions. Quiet steps too (loud on the robot).
- Ball randomisation (user 2026-10-08): radius 0.07–0.13 m, mass 0.05–0.45 kg
  (`mdp.ball_size_mass`, event key `ball_mass`).
- Keep training-domain randomisation, latency (0–40 ms) and limits as
  inherited from the AMP walk; B-Human torque clip; ball origin between the
  feet with 2 cm jitter; a never-seen ball is zeros with age 0 (training and
  runner).
- "If it is not improving, then move on": frames stop early when no child
  beats the parent screen.

## Current state (2026-10-08 20:55)

- **Champion:** `h010_c2_17850_x70_2seed`. Checkpoint:
  `logs/rsl_rl/k1_kick_stage3_amp/2026-10-08_11-08-42_champ_h010_c2_17850_x70/model_17149.pt`.
  ONNX: `../k1_policy_runner/kick_loop_models/k1_kick_loop_h010_c2_17850_x70.onnx`.
  `docs/evolution/state.json` holds the champion and archive.
- **Best candidates, not promoted:**
  - `h011_c2_17750` (ONNX exported): long kick 3D 4.4–4.5 m/s against the
    champion's 3.6 (B-Human 4.3); about 0.8 s faster to kick. It regresses on
    action rate (3 tracks) and style selection at high caps.
  - `h012_c1_18000`
    (`logs/rsl_rl/k1_kick_stage3_amp/2026-10-08_13-36-19_h012_c1/model_18000.pt`):
    +170 under the current fitness, long 4.1–4.2 m/s, goals 83/81 %. It
    regresses on close_any action rate at high caps and the heavy-ball long
    kick at high caps.
- **runswift harness findings (2026-10-09, monitor.md)**: the official fixture
  scores our policy with (1) the runner scene's 1 cm sole-capsule feet (training
  collides with the foot mesh) and (2) the ball relative to the pelvis (training:
  between the soles; B-Human gets the soles there), and (3) the runner's default
  caps 0.5/0.3/0.6 while B-Human walks uncapped. `scripts/tools/rsw_aligned.sh`
  runs it with mesh feet + soles origin (+ caps); results in
  `docs/benchmarks_v2/runswift_aligned/`. Aligned, high caps: h017_c0_18500
  beats B-Human on the near grid (107/107 vs 97/99 on-direction, 3.7/4.8 vs
  4.7/5.4 deg, launch 1.00 vs 1.03 s, strongest 3.2 vs 3.0 m/s) and scores
  twice as fast, but loses the goal grid 63-74 vs 88-89/90: every miss is a
  fall within 0.8 s of a standing start with the ball behind. The official
  numbers are unchanged; ask the user before changing the official fixture or
  the loop's runswift gate.
- **Training changes 2026-10-09**: `stand_start` reset event exists but is
  DISABLED (prob 0, gene ignored): every child with it at 0.35 collapsed
  80-140 iterations in; the same genes without it did not. Reward `alive`
  +2/s (gene w.alive); touchdown_speed -50 -> -15. Screen has
  near_grid/large and approach/behind/world/typical (cold start, ball behind,
  world perception; champion falls 32-40 %), also a fitness safety metric.
- **Camera perception result**: with KC_VISION=1 (deployed path) on the
  aligned fixture our policies score 87-90/90 goals with 0-1 falls in ~20 s
  (B-Human 88-89 with truth inputs, 30.5 s). The truth-input falls come from
  a seen ball far behind, which camera training never produces; world-ball
  training (s.world_ball_prob 0.3-0.5) did not fix them in 300-800 it.
- **Env change 2026-10-08 21:10** (monitor.md): ball size + mass DR, foot_flat
  settle 60 ms, touchdown_speed −50. bench v2 has large/small ball and landing
  tracks; the champion and B-Human were being benched on them at 21:10 — check
  that `h010_c2_17850_x70_2seed.json` has `near_grid/large/...`,
  `full_loop/landing/...` keys before trusting new-track scores.
- **Running:** frame h015 (an L1 template, far_cap_tracking, parent
  h011_c2_17750). After it, `inject.json` opens an L2 context from
  `h012_c1_18000` with CAPS temporal 1.3 and near-ball scale 0.8 (smoothness).
- **Supervisor:** started 16:21 with a 7 h limit, so it stops at about 23:20
  and does not restart itself. `scripts/tools/hier_relaunch.sh 3820386 43200`
  (detached) then relaunches it for 12 h unless STOP_AFTER_FRAME is set.

## Runbook

```sh
cd runswift_mjlab
tail -20 docs/evolution/log.md            # loop events
tail -30 docs/evolution/monitor.md        # interventions
cat docs/evolution/hier_report.md         # frame table
pgrep -af "evolve_hier|hier_supervisor|kick_bench2|bin/train" | grep -v pgrep
# Score a benchmarked candidate against the champion (current fitness):
uv run python -c "import json,sys; sys.path.insert(0,'scripts/tools'); import evolve_kick as ek; \
  ref=json.load(open(ek.BENCH/'h010_c2_17850_x70_2seed.json')); \
  print(ek.score(json.load(open(ek.BENCH/'NAME.json')), ref))"
# Stop cleanly after the current frame:
touch docs/evolution/STOP_AFTER_FRAME
# (Re)start: remove the flag, then
nohup bash scripts/tools/hier_supervisor.sh 28800 >/dev/null 2>&1 &   # seconds
# Steer the next frame: write docs/evolution/inject.json = [ {level, desc,
# genes, best?: {name, ck, score, regressions}} ]. It is consumed at the next
# frame boundary; "best" sets the parent checkpoint for the context.
# Full benchmark by hand (~40 min alone, longer while training runs):
env -u KICK_GENES BENCH2_SEED=1 uv run python scripts/tools/kick_bench2.py run NAME CK --size full
# ONNX export:
uv run python scripts/tools/export_onnx.py --checkpoint CK --output ../k1_policy_runner/kick_loop_models/k1_kick_loop_NAME.onnx
```

## Gotchas (each one has cost time)

- A child whose per-episode task reward goes negative learns to end episodes
  at once (h018, 2026-10-09: episode length 1400 -> 35 in ~25 iterations).
  Watch `Mean episode length` / `Episode_Termination/illegal_contact` after
  any change that adds cost or makes scenarios harder.
- The loop's log.md is not reliably append-only for `tail -F` / line-count
  watchers; diff its tail instead.

- `pgrep -f <pattern>` / `pkill -f` match your own shell when its command line
  contains the pattern; wait on a PID (`kill -0 PID`) or kill by PID in a
  separate call.
- Python changes to `fitness_v2.py` / `evolve_*.py` reach the running loop
  only after a restart. Use STOP_AFTER_FRAME, then relaunch; env/reward and
  rl_cfg changes reach the next child training automatically, because each
  child is a new process.
- Context `best` scores are relative to the champion at the time. After a
  promotion, rescore a carried-over best before injecting it, or set `best`
  explicitly.
- The ball's visual mesh does not follow the randomised collision radius; in
  the viewer every ball looks 0.08 m.
- The `action_rate_l2` reward (and `c.action_rate_l2`) acts on sampled actions
  with a fixed std of 0.6; noise dominates it and it does not smooth the
  deployed policy. Smoothness of the deterministic action comes from CAPS
  (`caps_temporal_coef`, `caps_spatial_coef`, `caps_near_ball_scale` genes;
  defaults 1.0 / 0.4 / 0.5 in `config/k1_amp/rl_cfg.py`).
- Limit training to 2 at a time (3 has run out of GPU memory); hand benchmarks
  alongside training are fine but slower.
- Checkpoints are saved every 50 iterations; a run ending at 17649 has no
  model_17650.
- Background shell waits in the agent harness time out (max 2 h); prefer
  detached `nohup` watchers for long waits.

## Pending, awaiting the user

- `../k1_policy_runner/start_kick.sh` still points at
  `2026-10-03_12-51-41_stage3_v50b.onnx` with `--kick-speed-limits 1.5,1.5,2.0`
  (training wz ≤ 1.5). Switch it to the champion and 1.5,1.5,1.5 once the user
  agrees. `DEFAULT_MODEL_PATH` and `--record-obs` for kick_loop_v1 are also
  open.
- Ideas the user raised and is waiting on: a ball tracker (Kalman +
  odometry), then a learned ball predictor; RMA-style test-time adaptation as
  an L5 atom.
- The user was asked to review two metric changes: the censored time-to-kick
  metric and the near-best 5 % style-selection rule (see monitor.md).
- Main remaining gaps: long-kick power without rougher actions or worse style
  selection, running at the high caps (approach cap use ~30 %), low-cap time
  to kick, heavy-ball long kick.

## Other documents

- `docs/K1_REAL2SIM_2026-10-09.md`: first real-robot kick-loop recordings vs
  sim (why the robot went on and off, cadence / torque / impact / vision gaps,
  runner fixes). Tools in `../k1_policy_runner`: `--kick-record`,
  `kick_record_analyze.py`, `real_sim_compare.py`.

- `docs/K1_KICK_BENCHMARK_V2.md`: benchmark tracks and metrics.
- `docs/K1_KICK_REWARD_EVOLUTION_DESIGN.md`: loop design and build status.
- `docs/K1_KICK_LESSONS.md`, `docs/K1_KICK_STYLES.md`: lessons and kick styles.
- `docs/experience/README.md`: the experience repository and objectives.

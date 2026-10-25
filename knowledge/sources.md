# Sources

Every original note this knowledge base draws on, where it is, what it
covers and whether it is still current. Originals are never edited by the
knowledge build; read them for the full numbers.

Status: **current** (still describes the code), **record** (a dated log or
result; true for its time), **superseded** (replaced; see the pointer),
**proposal** (design, partly or fully built).

## Kick loop

| File | Date | Status | What it is |
|---|---|---|---|
| `docs/K1_KICK_STAGE3_NOTES.md` | 10-01 → 10-06 | record | Run-by-run log of stage 3 v1–v57: issues, fixes, evals, robot reports, attack plan progress, overnight search, fair head-to-head. 120 KB; the source behind most kick lessons |
| `docs/K1_KICK_LESSONS.md` | 10-07 | record | Distilled kick lessons (reward, sim2real, eval, process, physics limits) and why runswift's benchmark disagreed (§9) |
| `docs/K1_KICK_LOOP_POLICY_IO.md` | 10-03 | current (layout), record (model list) | The 83 inputs / 22 outputs as trained and as run by the runner; noise, randomisation, joint order |
| `docs/K1_KICK_BENCHMARK_V2.md` | 10-07 | current | Benchmark v2 tracks, metrics, engines, commands |
| `docs/K1_KICK_STYLES.md` | 10-07 | record | Inside-foot and hop styles in one policy; style-choice options A–E; torque regime change |
| `docs/K1_KICK_ATTACK_PLAN.md` | 10-05 | record | Plan: search, moving ball, varied ground, long kick (from v55b) |
| `docs/K1_KICK_APPROACH_NOTES.md` | 10-01 | record | Stage 2: spec, warm-start collapse, sim blow-up guard, body heading change |
| `docs/K1_KICK_REWARD_EVOLUTION_DESIGN.md` | 10-06 | proposal (built) | Reward grammar and L0–L4 ladder |
| `docs/K1_KICK_APPROACH_LOOP_DESIGN.md` | 10-06 | proposal (built) | L5 approach loop: finding and integrating methods |
| `docs/approach_catalogue.yaml` | 10-07 | superseded by `knowledge/approaches/`, `knowledge/sources/`, `knowledge/uses/` (2026-10-25; every atom has a card) | L5 catalogue atoms |
| `docs/evolution/HANDOFF.md` | 10-09 | record (state), current (runbook, gotchas) | Evolution system, user objectives, champion state, runbook, gotchas, pending items. Read before touching the loop |
| `docs/evolution/monitor.md` | 10-07 → 10-09 | record | Every intervention in the loop, with reasons |
| `docs/evolution/log.md` | 10-07 → 10-09 | record | Loop events (machine-written) |
| `docs/evolution/hier_report.md` | 10-09 | record | Frame table h001–h023 |
| `docs/evolution/l5_requests.md` | 10-07 | record | L5 atoms that still need an adapter |
| `docs/evolution/state.json`, `hier_state.json`, `programs/`, `inject*.json` | 10-09 | current (loop state) | Champion, archive, reward programs, injected contexts |
| `docs/experience/README.md`, `experiences.jsonl` | 10-09 | record | Experience repository: objectives, per-action effect table, lessons, every frame |
| `docs/benchmarks_v2/*.json`, `report_*.md`, `screens/`, `runswift_aligned/` | 10-07 → 10-09 | record | Benchmark v2 results (raw traces deleted 2026-10-23) |
| `docs/kick_style_gallery/` | 10-06 | record | Scripted kick style videos |

## B-Human

| File | Date | Status | What it is |
|---|---|---|---|
| `docs/K1_BHUMAN_KICK_PORT.md` | 10-18 | current | The port: use, file map, validation, known differences |
| `docs/K1_KICK_VS_BHUMAN_2026-10-09.md` | 10-09 | record | Side-by-side of our kick loop and B-Human's, what to adopt |
| `docs/K1_KICK_BHUMAN_COMPARISON.md` | 10-05 | superseded by the 10-09 comparison | Earlier comparison |
| `docs/benchmarks_bhuman_kick/` | 10-18 | record | B-Human-spec kick benchmark v2 results |

## Sim-to-real

| File | Date | Status | What it is |
|---|---|---|---|
| `docs/K1_REAL2SIM_2026-10-09.md` | 10-09 | record | First real kick-loop recordings vs sim: on/off causes, gaps, runner fixes |
| `../k1_policy_runner/python-implementation/DRIBBLE_POLICY_IO.md` | 10-19 → 10-23 | current | Dribble policy I/O on the robot, run-time modes |

## Walk and legacy kick

| File | Date | Status | What it is |
|---|---|---|---|
| `docs/K1_WALK_TRAINING_NOTES.md` | 08-14 | record | Plain PPO K1 walk: reward hacking, curricula, oscillating plots. Its FastSAC tasks were removed 2026-10-23 |
| `docs/K1_KICK_TRAINING_NOTES.md` | 09-19 | record (legacy) | Arc / approach / near-kick tasks (September). Arc kick task removed 2026-10-23 |
| `docs/K1_KICK_TRACKING_NOTES.md` | 09-30 | record (legacy) | Motion-tracking kick: stand after kick, ball box, failed box fine-tune, DR matched to the walk, deploy mismatches |
| `src/k1/tasks/legacy/kick/PROBLEM.md` | 09-27 | record (legacy) | Living problem context for the Near kick ↔ walk handoff |
| `src/k1/tasks/legacy/kick/DESIGN_kick_on_walk_amp.md` | 09-28 | record (legacy) | Kick-on-walk-AMP design spec |

## Self-play

| File | Date | Status | What it is |
|---|---|---|---|
| `docs/STRIKER_SELF_PLAY_PLAN.md` | 10-11 → 10-16 | current (plan) | Game, I/O, algorithms, rewards, phases, behaviour integration, next steps |

## Session notes (memory snapshot)

`knowledge/session_notes/` holds unedited copies of the session memory
(2026-10-23). The only detailed run logs for dribble (v13–v53) and self-play
(v1–v16, controller v2–v7) are there.

| Note | Covers |
|---|---|
| `k1-dribble-speed.md` | dribble runs v13–v53 |
| `k1-striker-selfplay.md` | self-play and controller runs |
| `k1-kick-staged-training.md` | kick stages, handoff, stage-3 lessons v1–v46 |
| `k1-kick-objectives.md`, `dribble-kick-objectives.md`, `benchmark-gated-adoption.md`, `dribble-speed-over-slow.md`, `gait-penalty-weighting.md`, `kick-dr-from-amp-walk.md` | user objectives and decisions |
| `k1-real2sim-findings.md` | robot vs sim measurements |
| `kick-evolution-system.md` | how to resume the evolution loop |
| `bhuman-kick-port.md` | port status |
| `contact-uan-for-k1.md` | assessment of the contact-UAN actuator model |
| `selfplay-run-authority.md`, `kill-pattern-self-match.md` | operating rules |
| `selfplay-code-in-stash.md`, `restructure-preserve-knowledge.md` | 2026-10-23 repo events |

## Knowledge in code

Several files carry measured results in docstrings and comments; keep them
when refactoring (move files, don't rewrite them):

- `src/k1/tasks/velocity/rl/anchor.py`: why self-play needs the KL anchor
  (drift vs goal share numbers).
- `src/k1/tasks/{walk,kick,dribble,selfplay,striker}/tasks.py`: style weight 0.2
  rationale.
- `src/k1/tasks/selfplay/config.py`: self-play
  fine-tune settings and why.
- `src/k1/tasks/kick/mdp/kick_loop.py`, `dribble.py`,
  `dribble_rewards.py`: per-version comments (v24, v32, v50, ...) explaining
  each term.
- `src/mjlab/amp/modules/kick_teacher.py`: why the kick loop can teach the
  dribble.
- `src/k1/tasks/velocity/mdp/decap.py`: the DecAP law.

## Restructure records

`restructure/KEEP_LIST.md` (decisions and incidents), `checkpoints.csv`,
`runs.csv`, `best.csv`, `summary.json`, and the scripts `inventory.py`,
`best_ckpt.py`.

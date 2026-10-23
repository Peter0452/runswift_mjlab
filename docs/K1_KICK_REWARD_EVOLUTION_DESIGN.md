# Reward design search: moving up the abstraction ladder (proposal, 2026-10-06)

## Why

Tonight's search tunes **numbers inside a fixed reward**: weights, a few
constants and on/off switches. That is the lowest rung.

- It found no better training recipe in 9 generations. Fine-tuning swings
  more than any weight changes it.
- Both gains came from **combining behaviours** (weight blends).
- The biggest wins of the whole project were **structural reward changes**,
  never weight changes:
  - dense instead of sharp terms (v54b);
  - band edge instead of weight (v53);
  - signed instead of absolute turning (v56c);
  - a virtual ball, changing what the policy sees (v56d);
  - unpaid lofts instead of penalties (v55);
  - momentum-aware kick quality (v57).

  These are all in `K1_KICK_LESSONS.md`. Each took me a manual
  diagnose-and-redesign cycle.

The proposal: make **reward structure** and **task design** the things that
evolve, and keep the current weight search as the inner loop.

## The ladder

| Level | What changes | Today | Proposed |
|---|---|---|---|
| L0 Parameters | weights, constants, switches | `evolve_kick.py` (15 genes) | kept as the inner loop: a short tune of each new structure |
| L1 Term structure | the shape of each term: signal, transform (ramp / linear / Gaussian / band / potential difference), gate (when it is active), coupling (× aim, × quality, × loft…), event vs per-step | hand-written Python per term | a **reward grammar**: terms are JSON specs built from a library of signals and transforms, compiled to mjlab reward functions |
| L2 Composition | which objectives are rewards, which are constraints, how they combine | one weighted sum, ~45 terms | **constrained RL**: falls, torque, posture and speed caps as constraints with automatically adapted Lagrange multipliers (no weights to tune); a small set of rewarded objectives; optional schedules |
| L3 Task / scenarios | start states, ball dynamics, opponents, ground, curriculum | RSI shares, moving ball, relocation, pushes (hand-set) | **scenario genes and adaptive sampling**: train more on the situations where the benchmark is weakest (B-Human-style closed-loop curriculum) |
| L4 Designer | who proposes changes | me, by hand, from evaluations | an **LLM proposer** (Eureka-style) that reads the benchmark tables, per-term diagnostics and the lessons file, and writes L1–L3 changes in the grammar, with a rationale |

## Components

### 1. Reward grammar (L1)

A reward program is a list of term specs:

```json
{"name": "long_power", "signal": "ball_speed_3d", "event": "kick",
 "transform": {"ramp": [2.5, "needed_speed"]},
 "gate": ["range == long"],
 "couple": ["aim_exp(0.05)", "kick_quality", "loft(20, 35)"],
 "weight": 3000}
```

- **Signal library**, from what we already compute:
  - ball 3D and ground speed, launch angle;
  - needed speed per range, rest distance;
  - foot yaw at contact, support contact, body speed along / across the kick
    direction;
  - torque over the soft limit;
  - time near the ball, heading change while lost, trunk pitch and height,
    foot contact pattern.
- **Transforms:** linear, ramp, Gaussian, band (with explicit edges), exp
  decay, signed difference (potential-based shaping), clip.
- **Gates:** range, distance band, ball lost, kick window, walking.
- **Couplings:** products with other signals.
- **Compiler:** builds `RewardTermCfg`s from the spec. No free code, so every
  program is valid and reviewable.
- **Migration:** the current 45 terms are expressed in the grammar first (a
  regression test checks identical rewards on recorded rollouts), so today's
  reward is generation 0.

### 2. Structural operators (L1, L2)

- add / remove a term;
- swap the transform (e.g. Gaussian → linear: the v54 → v54b fix);
- change a gate or a band edge (v53);
- add or remove a coupling (× loft: v55; × transfer: v50);
- signed ↔ absolute (v56c);
- per-step ↔ event ↔ potential difference;
- **reward ↔ constraint** (move a term into the L2 constraint set);
- term-wise crossover between two programs in the archive.

### 3. Reward lint, before any training (cheap, minutes)

Each lesson becomes an automatic check, run on rollouts of the current
champion:

| Check | Lesson | Test |
|---|---|---|
| Signal at current behaviour | 1 (v54) | each term's value is not ~0 over > 90 % of samples where it is gated on, and changes with the policy's own variation |
| Band edges | 2 (v53) | a band term actually binds on the current distribution |
| Avoidance risk | 10 (v54c) | a per-event penalty is small next to the reward for doing the event |
| Oscillation exploit | 12 (v56b) | rate terms are signed or net-change |
| Unmeasured axes | 11 (v55) | speed terms state 2D or 3D explicitly |
| Scale | 5 (v46 / v47) | each term's typical contribution relative to the total (ignored or dominating) |
| Height on terrain | 9 (v48) | no absolute-height signal |

Programs that fail lint are rejected or auto-fixed before costing GPU time.

### 4. Constrained composition (L2)

- **Rewarded:** goals, aim, speed matched to range, pass rest accuracy,
  search progress, style (AMP).
- **Constraints**, with thresholds taken from the benchmark targets:
  - falls after the first 2 s;
  - torque over the soft limit;
  - trunk pitch band, height band;
  - speed caps;
  - support planted at contact.

  Each constraint has a multiplier that grows while it is violated and decays
  when it is satisfied (PPO-Lagrangian).
- **Effect:** removes most weight tuning (the L0 search space shrinks), and
  makes "don't compromise other objectives" part of training, not only of
  selection.

### 5. Scenario design and adaptive curriculum (L3)

- Scenario genes:
  - start-state mix (normal, RSI from B-Human or ours, ball behind, moving);
  - ground mix (attack plan Phase 3);
  - relocation and robot-touch rates;
  - range mix.
- **Adaptive sampling:** after each benchmark, raise the training share of
  the scenarios where the policy is weakest relative to B-Human or to its
  targets (e.g. any-bearing first kick, long kicks), capped so no scenario
  disappears.
- **Situation benchmark:** results split by approach angle × range × ball
  offset. This is what "the right kick style for the situation" is judged
  on.

### 6. Selection: quality-diversity + Pareto (replaces the single score)

- **Behaviour descriptors:**
  - kick style (foot yaw at contact: front ↔ side);
  - body speed at contact;
  - long-kick speed;
  - steps before the kick.
- **MAP-Elites archive:** the best program and checkpoint per descriptor
  cell, so a side-foot specialist survives even before it beats the front
  kick overall.
- **Objective groups:** power, accuracy, robustness, posture / gait, search,
  pass control.
- **Promotion to champion:** Pareto improvement over the champion on the
  groups, the existing no-regression gates, and two-seed confirmation (as
  tonight).
- **Weight-space crossover** (`blend_checkpoints.py`), automated, between
  elites of one lineage: tonight's working combiner. Specialists can be
  blended into the champion.

### 7. LLM proposer (L4)

- **Input:**
  - the champion's benchmark table versus B-Human and the targets;
  - per-term reward statistics (mean, fraction active, correlation with
    each objective);
  - the anatomy, style and situation breakdowns;
  - `K1_KICK_LESSONS.md`;
  - the archive's history of which changes helped.
- **Output:** 3–5 program edits in the grammar, each with a one-line
  hypothesis ("long kicks lack ground speed because …; change …").
- **Path:** edits go through lint, then a short training with L0 tuning,
  then screen and benchmark. Outcomes are fed back into the next prompt
  (Eureka / reflection loop).
- **Guardrails:** grammar only; no changes to observations (83 inputs),
  domain randomization or the benchmark; a human approves anything that
  touches deployment.

## How a structure is judged fairly

A structure is only as good as its best tuning, and fine-tuning swings. So
each candidate program gets:

1. lint;
2. 2 short trainings (+500 iterations) with L0 weights sampled around its
   defaults;
3. 9-checkpoint screens each;
4. a full benchmark of the best.

Its fitness is that **best-of-K**, compared with the same procedure applied
to the champion's program (a control each round). This separates "the
structure is better" from "this run got lucky".

## Loop and budget

| Loop | Time per item | Night (10 h) |
|---|---|---|
| Lint | minutes, no training | dozens of programs |
| Program evaluation (2 × 500 iterations + screens + 1 benchmark) | ~90 min | ~6 programs |
| Blending between elites | ~30 min, no training | after each new elite |
| LLM proposal round | minutes | after each evaluated program |

## What carries over from today

- `kick_benchmark.py`: the fixed 25-metric benchmark and its tolerances.
  It becomes the Pareto groups and the situation benchmark.
- `evolve_kick.py`: becomes the L0 inner loop. Genes are generated from the
  program's weights instead of a fixed list.
- `blend_checkpoints.py`, `blend_search.py`: the crossover operator.
- RSI (`record_kick_clips.py`, `data/kick_rsi`), relocation, moving ball:
  L3 scenario genes.
- `kick_probes.py`, `kick_anatomy.py`, `kick_style_compare.py`: behaviour
  descriptors and diagnostics.
- `K1_KICK_LESSONS.md`: lint rules and LLM context.
- Two-seed confirmation, control runs, anchor model, one-training-at-a-time
  safety.

## Build order

1. **Grammar + compiler + equivalence test.** Today's reward as a program,
   identical values on recorded rollouts. ~1 day.
2. **Reward lint** from the lessons, run on the champion. Immediately useful
   for manual design too. ~0.5 day.
3. **Situation benchmark** and behaviour descriptors, then the MAP-Elites /
   Pareto archive with automated blending. ~1 day.
4. **Constraints (PPO-Lagrangian)** for falls, torque and posture. Changes
   the algorithm, so compared head to head with the weighted-sum champion.
   ~1–2 days.
5. **LLM proposer loop** on top. ~1 day.
6. **Adaptive scenario curriculum.** ~0.5 day.

Steps 1–3 are low-risk and pay off even without the rest; 4–6 are where the
larger gains should come from.

## Risks

- **Reward hacking at a higher level:** a freer grammar finds more exploits.
  Mitigated by the lint, the fixed benchmark the search cannot change, and
  anatomy / style checks.
- **Compute:** structure evaluation is about 4× a gene child. Lint and
  multi-fidelity screening keep GPU time for plausible programs.
- **Constrained RL** may destabilise AMP training at first; keep the
  weighted-sum fallback.
- **Sim-to-real:** the search optimises in sim. Robot logs
  (`--record-kick-obs`) and the runner bench stay the final gate before
  deployment.

## Build status (2026-10-06)

- **Done:**
  - **Reward grammar:** `src/mjlab/tasks/velocity/mdp/reward_grammar.py`. It
    has 30 named signals and the operators mul / add / neg / abs / div / ramp
    / linear_match / gauss / band / exp_decay / clip / gt / lt.
    `KICK_REWARD_PROGRAM=prog.json` adds, replaces or removes terms
    (expression terms or references to existing functions). Gene weights
    (`w.<name>`) still apply on top, so L0 tunes any program.
  - **Equivalence test:** `long_kick_underpower` re-expressed in the grammar
    gives identical values. A wiring test covers changing a weight, removing a
    term and adding an expression term. 28 tests pass.
  - **Reward lint:** `scripts/tools/reward_lint.py` (active %, share %, event
    spread, NO-SIGNAL / INERT / DOMINANT / PENALTY-ON-ACTION). First run on
    x4_g004_70 is in the stage-3 notes.
  - **Search loop:** automated champion × child blending, two-seed
    confirmation, auto-install and ONNX export.
  - **Benchmark:** approach-from-far gates (29 metrics).
  - **Deployability:** `onnx_parity.py`, `lost_rule_parity.py`.
- **Next:**
  - structural operators, with programs as candidates in `evolve_kick.py`
    (the child's program file passed with its genes);
  - lint gating before training;
  - situation benchmark and QD descriptors;
  - constraints (PPO-Lagrangian);
  - LLM proposer.

## Build status (2026-10-07): hierarchy L0-L5 running

`scripts/tools/evolve_hier.py` (orchestrator) on top of `evolve_kick.py`, judged by
benchmark v2 (`kick_bench2.py`) through one fitness (`fitness_v2.py`).

| Level | Implementation | Trigger |
|---|---|---|
| L5 approach | atoms in `approach_catalogue.yaml` with a `frame:`; atoms without an adapter listed in `docs/evolution/l5_requests.md` | every 6 h |
| L4 designer | `claude -p` with a digest (champion v2 metrics, frame history, genes, grammar); frames validated (known genes, clamped ranges, grammar-checked extra terms) | every 3 h (`--no-l4` to disable) |
| L3 scenarios | genes `s.spawn_any_prob`, `s.far_spawn_prob`, `s.world_ball_prob`, `s.cap_low_prob` (approach.py / kick_loop.py); proposed from the champion's weakest v2 situation | every 3rd frame |
| L2 composition | `c.<term> = r`: penalty -> adaptive constraint holding its cost at r x warm-up level (`mdp/constraints.py`, logged `Metrics/lambda_<term>`) | every 4th frame |
| L1 structure | template on / off; shape genes `ts.<template>` scale a template's constants; `_extra_terms` grammar terms from L4 | otherwise |
| L0 parameters | inner loop of every frame: 3 children (frame as proposed + 2 L0 mutations), 2 in parallel, 500 iterations, v2 screen of 5 checkpoints | always |

Per frame the best child gets the full v2 benchmark; promotion needs two seeds without
regressions and a positive summed score; otherwise a blend with the champion is tried.
State `docs/evolution/hier_state.json`, report `docs/evolution/hier_report.md`.
Starting champion: sty_power_17149 (v2 fitness +48 over x4; weak on long-kick power and
falls with the ball behind).

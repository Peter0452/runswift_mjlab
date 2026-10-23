# Architecture (target, decided 2026-10-23)

The structure the restructure moves toward, and the design of the evolution
loop that follows it. Decisions: package `k1`; per-task folders; methods with
cards; YAML recipes; deploy contract as code; our own evolution loop (no
harbor dependency); hybrid promotion rule. Status: Steps 1–3 done (keep-list, knowledge base, safety net); Step 4 (code
move) done 2026-10-24 except the big-file splits, deferred to Step 5 (see "As built"
below and `restructure/STEP4_LOG.md`); Step 5 started 2026-10-24: methods registry, recipes, `run.json` and `rsw` built
(`restructure/STEP5_LOG.md`); parity gate, verdicts and the loops next.

## Layout

```
RL/                              workspace (CLAUDE.md: mission + map)
├── runswift_mjlab/              training, evaluation, knowledge
├── k1_policy_runner/            robot runtime (not edited from this repo)
├── MachineLearning/             B-Human reference (read-only)
└── data/                        motion clips, robot recordings

runswift_mjlab/
├── src/mjlab/                   FRAMEWORK (upstream-derived; our edits small, listed)
│   envs/ managers/ sim/ entity/ sensor/ actuator/ terrains/ viewer/ utils/
│   tasks/registry.py  rl/ (generic runner, exporter, fast_sac/)  scripts/ (train, play)
│
├── src/k1/                      ALL K1 WORK (registered via mjlab's "mjlab.tasks" entry point)
│   ├── cli.py                   `rsw`: one interface for people, agents, the evolution loop
│   ├── robot/                   K1 model, actuators, sensors · ball + goal props
│   ├── deploy/                  contract.py (source of truth) · obs_layout.py (named slots) ·
│   │                            export.py (contract → ONNX metadata) · parity.py (runner checks)
│   ├── common/                  ball.py (K1_BALL) · vision.py (camera, memory, lost rule, head) ·
│   │                            symmetry.py · terrain.py · physics_guard.py · reward_log.py
│   ├── methods/<name>/          METHOD.md card · config + apply() · smoke test; registry.py
│   ├── tasks/                   __init__.py registers the 34 task IDs
│   │   walk/ kick/ dribble/ selfplay/ striker/ bhuman/ legacy/   (each: config.py + mdp/)
│   ├── eval/                    one judge per task, one result shape
│   └── evolve/                  outer.py · pool.py · inner.py (PBT/PB2) · verdict.py · designers/
│
├── experiments/recipes/<task>/*.yaml   run definitions (in git)
├── experiments/evolution/              loop state, verdicts (gitignored)
├── logs/rsl_rl/<exp>/<run>/            checkpoints (latest + best + referenced), params/, run.json
├── knowledge/                          read first (this directory)
├── docs/                               original notes, benchmark JSON
├── tests/{framework,k1,golden}/        upstream tests · our tests · safety net
├── scripts/                            thin wrappers for old commands; scripts/agent/ (hooks)
└── restructure/                        keep-list and inventory records
```

Guarantees during the move: the 34 task IDs, `uv run train/play`, checkpoint
formats and old module paths (kept as aliases) all keep working; the golden
safety net runs after every step.

## As built (Step 4, 2026-10-24)

Differences from the sketch above, all logged with reasons in
`restructure/STEP4_LOG.md`:

- Families: `k1/tasks/{walk,kick,dribble,selfplay,striker}/` hold `mdp/` and
  `tasks.py` (registration); configs are `env_cfg.py` + `rl_cfg.py` (self-play:
  one `config.py`, which also holds the striker controller's configs). Walk
  baselines (PPO, HTWK) in `walk/baselines/`; `getup/`, `bhuman/`, `legacy/{kick,tracking}/`.
- `k1/tasks/velocity/` stays as the shared layer: generic mdp terms and the one
  `mdp` namespace that re-exports the family modules (its import order is
  load-bearing), base env configs, AMP wrapper, runners (AMP runner, anchor). Its
  pieces move to `common/` and `methods/` in Step 5.
- Old module paths resolve through `k1/compat.py` (an import finder; one line per
  moved package). Re-export shims (`k1_amp/env_cfgs.py`, `rl_cfg.py`) are
  read-only: patch the family module.
- Not split yet: `kick/mdp/kick_loop.py` (its module constants are overridden by
  `KICK_GENES` through `globals()`, and tests patch its helpers, so a split would
  silently disconnect genes), and the other large modules. Splitting follows the
  recipes in Step 5, when genes become explicit parameters.
- `scripts/tools/` not moved (live evolution loop, cross-imports); catalogued in
  `scripts/tools/README.md`. `k1/eval` and `k1/evolve` are built in Step 5.
- Our edits inside the framework that stay in `src/mjlab/`: `amp/`, tracking
  `mdp/{shot,shot_rewards,stand_blend}.py`, scripts (`train.py`, `play.py`, …).

## Contracts

| Contract | Lives in | Enforced by |
|---|---|---|
| Deployment (obs, actions, rate, ball, head, caps, clips, delay) | `k1/deploy/contract.py`; readable copy `knowledge/deployment.md` | ONNX metadata, runner parity gate, deployable label |
| Task set | `k1/tasks/__init__.py` | `tests/test_task_registry.py` |
| Model behaviour | `tests/golden/` | `scripts/tools/golden.py`, `golden_bench.py` (later `rsw check`) |
| Method | `k1/methods/<name>/` | `rsw recipe check`, each method's smoke test |
| Run | `logs/…/run.json` | written by `rsw train`, appended by evals |
| Objectives | `knowledge/objectives.md` | CLAUDE.md, session briefing hook |

## Methods and recipes

A **method** is one technique (AMP, DecAP, Muon, multi-critic, CAPS, KL anchor,
kick teacher, symmetry augmentation, conditioned AMP, SWA/blend, reward
grammar; FastSAC parked; B-Human imitation rejected). Each has a card: what /
source, extension point(s), parameters, conflicts, **deployment impact**
(training-only or runtime), status, evidence, pitfalls.

Extension points: algorithm · optimizer · critic · action prior · smoothness ·
data · observation · reward · scenario/DR · curriculum · post-training ·
evaluation. Two methods on the same exclusive point conflict.

A **recipe** (YAML) defines a run: task, init checkpoint, ball, methods with
parameters, reward overrides, same-length control, `change`, `why`,
`budget_rationale`, `touches` (training-only | runtime). The per-run genes
(`KICK_GENES`, `DRIBBLE_GENES`) become recipe parameters; the old env vars keep
working through a translation layer.

Lifecycle: candidate → experimental → trial → adopted | rejected | parked.
**Promotion rule (hybrid):**

| Tier | Training-only methods | Runtime methods |
|---|---|---|
| Sim / research | any | any |
| Robot test (supervised, recorded) | experimental OK if the model passes all gates | experimental only with the user's OK, after runner change + parity |
| Match | adopted, or experimental already robot-tested | adopted only |

## Evolution loop

**Outer loop** (decides what to try; hours): diagnose the champion's gaps
(benchmark v2 + verdicts + experience) → classify the failure (trainer → inner
loop | reward | task | deployment | infra) → a designer writes a recipe
(bounded change, why, budget, hacking-surface check, distinct from the best and
from everything in flight) → gate plan from `touches` → dispatch to the async
pool → strict judges on the population's best → promote or reject, record the
verdict → after N non-improving verdicts, write a decision packet for the user.

**Inner loop** (tunes a design while it trains; minutes): a PBT / PB2 population
of 4–8 copies of one recipe, pinned seed, quick screen every 50–100 iterations;
weak copies take the weights and numbers of strong ones (exploit) and are
nudged (explore); weight blends as crossover. Only continuous numbers inside the
recipe's ranges change. Its best checkpoint goes back to the outer judges.

**Verdict** (fixed schema): status (smoke_failed / parity_failed / train_failed
/ diverged / scored), per-term returns, behaviour checklist (falls, posture,
technique, reward hacking, deployed path, peak vs final), findings. Ungradable
is never zero.

**Designers** (`k1/evolve/designers/`), all emitting recipes:

| Designer | Proposes | Gate before training |
|---|---|---|
| reward (L1) | reward-grammar programs | lint, budget, hacking-surface check |
| constraint (L2) | penalty → constraint, bounds | budget |
| scenario / DR (L3) | spawns, vanishing, pushes, DR ranges (evidence-based) | read-back smoke; DR needs robot evidence + user OK |
| method (L5) | enable / tune a registered method | `rsw recipe check` |
| task / observation | obs, action, command changes | per-section smokes + runner change + parity |
| trainer | the inner loop's search ranges | the inner loop measures it |
| front-end (L4) | an LLM or a person writing any of the above | the gate of the designer it uses |

Ideas borrowed from harbor's reward-tuning design and implemented natively
here: async refill pool, verdict schema, designer/implementer context split,
pinned seed, failure classification, hacking-surface check, budget-first,
adapt-first precedence (user > proven base > repo idioms > heuristics),
"what it touches → which gates", escalation packet, resume-safe single-writer
state. New-task authoring becomes `rsw task new` (section-by-section with smokes).

## Build order

1. **Step 4: move the code** into `src/k1/`: done 2026-10-24 (big-file splits and
   eval deferred to Step 5).
2. **Evolution loop**: methods + registry, recipes reproducing today's configs
   (verified by golden), `run.json`, `rsw`, deploy parity gate and labels,
   outer + inner loop, designers, verdicts; loop state to `experiments/evolution/`.

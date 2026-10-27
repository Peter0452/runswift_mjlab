# Architecture (target, decided 2026-10-23)

The structure the restructure moves toward, and the design of the evolution
loop that follows it. Decisions: package `k1`; per-task folders; methods with
cards; YAML recipes; deploy contract as code; our own evolution loop (no
harbor dependency); hybrid promotion rule. Status: Steps 1–3 done (keep-list, knowledge base, safety net); Step 4 (code
move) done 2026-10-24 except the big-file splits, deferred to Step 5 (see "As built"
below and `restructure/STEP4_LOG.md`); Step 5 built 2026-10-24: methods registry, recipes, `run.json`, `rsw`, deploy
contract + gate, verdicts and judges, outer loop + inner PBT (`k1/evolve`, not yet
run: needs your budget and designer choices; `restructure/STEP5_LOG.md`). Step 6
built 2026-10-25: task requests and implementations, approaches filed by element
with sources and uses, literature reviews; `k1/methods` → `k1/approaches`,
`k1/evolve` → `k1/engine` (old paths alias; see "Task requests and
implementations" below and `restructure/STEP6_LOG.md`).

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
│   ├── common/                  ball.py (B-Human's) · vision.py (camera, memory, lost rule, head) ·
│   │                            symmetry.py · terrain.py · physics_guard.py · reward_log.py
│   ├── approaches/              registry.py (approaches with code: element, detect, apply) ·
│   │                            knowledge.py (cards, sources, uses; check)   [was methods/]
│   ├── requests.py              task requests: schema, check, freeze, task tree
│   ├── tasks/                   __init__.py registers the 34 task IDs
│   │   walk/ kick/ dribble/ selfplay/ striker/ bhuman/ legacy/   (each: config.py + mdp/)
│   ├── eval/                    one judge per task, one result shape
│   └── engine/                  outer.py · inner.py (PBT/PB2) · state.py · real.py · designers/
│                                [was evolve/]
│
├── tasks/<name>/request.yaml           task requests: the "what" (in git)
├── experiments/recipes/<task>/*.yaml   task implementations: run definitions (in git)
├── experiments/evolution/              loop state, verdicts (gitignored)
├── logs/rsl_rl/<exp>/<run>/            checkpoints (latest + best + referenced), params/, run.json
├── knowledge/                          read first (this directory)
│   approaches/<element>/  sources/  uses/  reviews/   approach knowledge (Step 6)
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
| Deployment (obs, actions, rate, ball, head, caps, clips, delay) | authority: the runner's RL development interface (`k1_policy_runner` dev: `docs/rl-development/`, `docs/policies/`); mirror `k1/deploy/contract.py` + `obs_layout.py`; readable `knowledge/deployment.md` | `tests/test_runner_spec.py`, ONNX metadata (`policy_id`, `spec_version`, `obs_dim`, `obs_layout`), runner intake TAKE + parity in `rsw deploy check`, deployable label |
| Task set | `k1/tasks/__init__.py` | `tests/test_task_registry.py` |
| Model behaviour | `tests/golden/` | `scripts/tools/golden.py`, `golden_bench.py` (later `rsw check`) |
| Task request | `tasks/<name>/request.yaml` | `rsw request check`; frozen hash once agreed |
| Approach | `knowledge/approaches/<element>/<id>.md` + `k1/approaches/registry.py` | `rsw knowledge check`, `rsw recipe check` |
| Run | `logs/…/run.json` | written by `rsw train`, appended by evals |
| Objectives | `knowledge/objectives.md` | CLAUDE.md, session briefing hook |

## Task requests and implementations (Step 6, 2026-10-25)

The repo is a task-fulfilment system for the runswift behaviour module and for
people: a requester sends a **task request** (the what), the engine answers it
with **task implementations** (the how), and a judge joins the two.

```
 requester ── TASK REQUEST (tasks/<name>/request.yaml) ──▶ engine
           ◀── report: verdict per requirement ─────────  │
                                                          ▼
 approaches (knowledge) ──options──▶ TASK IMPLEMENTATIONS (recipes) → train
           ▲                                              │
           └── uses ◀── judge (frozen verification) ◀─────┘ → gates → delivery
```

- **Task request:** goal, context, run-time interface, requirements with
  priorities (0 safety, 1 primary, 2 secondary), verification (judge,
  benchmark, promotion rule), constraints, optional priors (typed: clips,
  teacher, reward hint, constraint, curriculum, scenario, warm start,
  approach), budget, deliverable, implementations.
  - **Lifecycle:** draft → agreed → frozen (hash of interface, requirements
    and verification) → delivered. A change is a new version.
  - The system proposes measurable requirements and relaxations with evidence;
    it never relaxes a requirement itself.
- **Task graph:** a request with level > 0 acts through subtasks (lower-level
  requests or deployed policies). A subtask's interface is the parent's action
  space; decomposition (flat vs hierarchical) is an implementation choice.
- **Task implementation:** a recipe naming its `request` and an optional
  falsifiable `hypothesis`; the engine's designers write them from approaches.
- **Approaches** are filed by the element their mechanism changes. The four RL
  elements are agent, reward, value and model. Two context axes cover the
  rest: environment (what the agent experiences) and optimisation. The full
  taxonomy is in `knowledge/approaches/README.md`. Knowledge is stored as
  source → approach → use:
  - **Sources** (`knowledge/sources/`): papers, repositories and our own work,
    each with its approach written as elements.
  - **Approach cards:** idea, conditions, our status.
  - **Uses** (`knowledge/uses/uses.yaml`): which part we used, in which task,
    with what result, negative results included.
- **Literature reviews** (`knowledge/reviews/`): a trigger, related tasks and
  their approaches, a fit judgement and a shortlist with hypotheses. Literature
  decides what is worth trying; the benchmark decides what stays.

## Approaches (formerly methods) and recipes

An **approach** (called a method before Step 6) is one technique (AMP, DecAP, Muon, multi-critic, CAPS, KL anchor,
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

**Child stages** (built 2026-10-26, `k1/engine/outer.py`; each stage is a
background job, `k1/engine/jobs.py`, so judging never holds up training):
smoke (3 training iterations: starts, no crash, every edited reward term
logged) → train from the champion or a named parent child, with probes at 30 /
55 / 80 % of the budget (rs_kick deployed; two significantly negative probes in
a row stop it, `stopped_early`) → screen (kick scorecard at benchmark v2 `gate`
size + rs_kick deployed, per-term training curves attached) → confirm (full
scorecard) → promote, then reverify (the new champion's own results become the
references; a clip with a motion check is recorded). **Kick scorecard**
(`k1/eval/scorecard.py`): benchmark v2 fitness + 1000 x the mean deployed
rs_kick margin; regressions from both; confirmed when benchmark v2 gains on both
seeds or rs_kick gains significantly on both deployed seeds. Around it: doses
(sibling strengths of one change), forecast calibration (measured / forecast,
`worth.calibration`), credit for fixing a parent's regression, a ceiling
detector (3 failed children on one gap → structural request to the user, gap
closed to training-only proposals), a GPU-hour budget, a heartbeat
(`experiments/evolution/heartbeat.json`), notifications (`notify.log`,
`notify-send`) and `scripts/tools/engine_daemon.sh` (restart after a crash).

**Inner loop** (tunes a design while it trains; minutes): a PBT / PB2 population
of 4–8 copies of one recipe, pinned seed, quick screen every 50–100 iterations;
weak copies take the weights and numbers of strong ones (exploit) and are
nudged (explore); weight blends as crossover. Only continuous numbers inside the
recipe's ranges change. Its best checkpoint goes back to the outer judges.
Not wired: at most 2 trainings at a time leaves no room for a population;
doses + probe-based early stopping do its job (successive halving over
strengths) until more GPUs are available.

**Verdict** (fixed schema): status (smoke_failed / parity_failed / train_failed
/ diverged / stopped_early / scored), per-term returns, behaviour checklist (falls, posture,
technique, reward hacking, deployed path, peak vs final), findings. Ungradable
is never zero.

**Designers** (`k1/engine/designers/`), all emitting recipes with a hypothesis:

| Designer | Proposes | Gate before training |
|---|---|---|
| reward (L1) | reward-grammar programs | lint, budget, hacking-surface check |
| constraint (L2) | penalty → constraint, bounds | budget |
| scenario / DR (L3) | spawns, vanishing, pushes, DR ranges (evidence-based) | read-back smoke; DR needs robot evidence + user OK |
| method (L5) | enable / tune a registered method | `rsw recipe check` |
| **approach** (built, Step 8) | reads the champion's measured gaps (`k1/engine/gaps.py`), matches tags to approach cards, proposes add (`trial`) or tune (`tune`) moves; approved review shortlists first; combination by stacking promoted children (`combine` > 1 bundles, off: one change per run) | `rsw recipe check` |
| task / observation | obs, action, command changes | per-section smokes + runner change + parity |
| trainer | the inner loop's search ranges | the inner loop measures it |
| front-end (L4) | an LLM or a person writing any of the above | the gate of the designer it uses |
| **llm** (built, Step 9) | the LLM agent is the designer: `/design` gives it the context pack (`rsw design context`), the knowledge and the tools; it writes proposals in a fixed schema into the inbox; `rsw design check` validates them; the engine reads the inbox first (`InboxDesigner`), the deterministic designers fill in when it is empty | `rsw design check`, then `rsw recipe check` |

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
3. **Step 6: task requests and approach knowledge** (2026-10-25): `tasks/`,
   `k1/requests.py`, approaches by element with sources, uses and reviews,
   `k1/approaches` and `k1/engine` renames, `rsw request|approaches|knowledge|engine`.
4. **Step 7: runner RL development interface** (2026-10-25): the runner's
   `dev` docs are the authority for what a policy sees and outputs. Mirror +
   conformance test, spec metadata in exports, the runner's intake as a gate
   check, `deliveries/` for handover and tier-2 spec drafts.
5. **Step 8: knowledge-driven designer and reviews** (2026-10-25): measured
   gaps → tags → approach cards (`trial`, `tune`) → add / tune moves;
   `rsw review gaps|new|approve`, `/review` command; the engine runs the
   approach designer plus one-gene steps.
6. **Step 9: the LLM agent as designer** (2026-10-26): context pack, proposal
   schema and checker, inbox read first by the engine, `/design` command; the
   deterministic designers become its baseline and fallback.
7. **Step 10: the engine calls the designer itself** (2026-10-26): headless
   `claude -p /design` when the inbox is empty, worth-a-retrain gate.
8. **Step 11: autonomous loop** (2026-10-26): background stages, kick
   scorecard (benchmark v2 + rs_kick), smoke, probes and early stopping, doses,
   parents, calibration, ceilings, reverify + clip on promotion, budget,
   heartbeat, notifications, daemon.

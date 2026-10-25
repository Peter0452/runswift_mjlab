# Step 6 log: task requests, implementations and approach knowledge

Started 2026-10-25 after the user's "do it" on the structure agreed in
conversation (two big interfaces, task graph, approaches filed by element,
literature reviews, source → approach → use). Same rules as `STEP4_LOG.md`:
each entry lists what was built, how it was checked, and every **best guess**
made without asking. No behaviour change: no task, reward, config or deployment
value changed.

## Built

| What | Checked by |
|---|---|
| `tasks/<name>/request.yaml` for `kick`, `dribble` (level 0) and `striker` (level 1: subtasks `kick` request + deployed gold walk), all **draft**; `tasks/README.md` | `rsw request check`; `tests/test_k1_requests.py` |
| `k1/requests.py`: schema, `check` (fields, priorities, a safety requirement, judges exist, implementations exist and are judged by the request's judge, subtasks are lower-level requests or deployed policies, frozen hash), `freeze` (changes only the `status` / `frozen` lines), `tree` | tests (freeze then change is caught; lower-level rule; wrong judge) |
| Recipes gained `request:` (the request they answer) and optional `hypothesis:`; the five relevant recipes name their request | `tests/test_k1_recipes.py`, `tests/test_k1_approaches.py` |
| `k1/methods` → `k1/approaches` (git mv): `Approach` with `element`; `Method` / `METHODS` kept as aliases; old import path `k1.methods` aliased in `k1/compat.py` | `tests/test_k1_compat.py` (new samples), full approach tests |
| `k1/evolve` → `k1/engine` (git mv), alias `k1.evolve`; designers' `Proposal.hypothesis`, written into child recipes and the engine history | `tests/test_k1_engine.py` (new: children carry a hypothesis) |
| Cards moved to `knowledge/approaches/<element>/<id>.md` (git mv of the 13 METHOD.md cards, content kept, front matter added) + 24 new cards: every L5 catalogue atom and the core approaches already in use (AMP-walk DR, vision model, staged curriculum, self-play, two-level controller, torque clip, actuator net); `model/` is empty (a gap, README says so) | `rsw knowledge check`; `test_knowledge_graph_connects` |
| `knowledge/sources/` (20 records: 8 papers, 10 repositories, 2 ours), `knowledge/uses/uses.yaml` (22 uses seeded from card evidence and the catalogue, negatives included), `knowledge/reviews/` (format + 2026-10-06 kick approach loop + 2026-10-25 ENPIRE/harbor review) | cross-references checked by `k1/approaches/knowledge.py` |
| `rsw request list|check|show|freeze`, `rsw approaches [--element E] [ID]` (shows the card and its uses), `rsw knowledge check`, `rsw engine ...`; old `rsw methods`, `rsw evolve` still work; `rsw check` runs the new tests | used for all of the above |
| Docs: `knowledge/architecture.md` (new section "Task requests and implementations", layout, contracts), `knowledge/INDEX.md`, `CLAUDE.md`, `scripts/tools/README.md`, `knowledge/sources.md` (catalogue superseded, kept) | read through |

## Safety net

- Golden model snapshots: all 6 ok (action diff 0). `rsw recipe check`: all 10
  recipes ok. Tests: 138 passed, 4 skipped, **1 failed**.
- The failure is `test_deploy_parity.py::test_deploy_gate_passes_the_deployed_champion`,
  and it is not caused by this step:
  - `../k1_policy_runner` is now on branch `dev`, where the runner package
    moved from `python-implementation/policy_runner/` to
    `policy_runner/policy_runner/`.
  - So `lost_rule_parity.py` can't import `policy_runner.policy.kick_loop_policy`.
  - The ONNX parity and metadata parts of the gate pass.
  - The fix is to point the lost-rule tool at the runner's new layout (or check
    out the runner's `dribble` branch). That needs your call on which runner
    branch is current; nothing in the runner was edited.
- Champion benchmark (`golden_bench.py`, ~10 min of GPU) not run: no
  behaviour-bearing code changed.

## Best guesses (review these)

1. **Requirement priorities and targets** in the three requests are mine,
   from `knowledge/objectives.md`: safety (falls, deploy gate, torque clip) =
   0; the headline (kick: time, accuracy, power by range; dribble: speed,
   control, kick power, no regression) = 1; the rest = 2. Targets the
   objectives don't give as numbers stay as words or `TBD` (budgets, striker
   goal share, dribble time to kick). All requests are **draft**: nothing is
   frozen until you agree them (`rsw request freeze NAME --agreed`).
2. **`tasks/` at the repo root** holds requests (as proposed), next to
   `src/k1/tasks/` (task code). If the two names confuse, `requests/` is the
   alternative.
3. **The recipe field stays `methods:`** (not `approaches:`), so existing
   recipes and every `run.json` keep working; the docstring says it lists
   approaches with code.
4. **Element mapping** (file by mechanism, goal as a tag): AMP and conditioned
   AMP = reward; DecAP, CAPS, KL anchor, kick teacher, B-Human imitation,
   symmetry augmentation = agent; multi-critic, FastSAC = value; Muon, SWA =
   optimisation; DR, vision model, scenarios, clips, self-play, staged
   curriculum, torque clip, actuator net = environment. Muon and SWA have no
   home among the four RL elements, hence the optimisation axis.
5. **Approach code stays where it is** (`src/mjlab/amp/`, task mdp modules);
   `k1/approaches/` holds the registry and the knowledge loader only, not
   per-element code folders (the proposal sketched those; they would be empty).
6. **Uses were seeded only from evidence already written** in cards, skills
   pages and the catalogue; papers' claims are not recorded yet (sources say
   `extraction: summary` or `extracted`). Citations for papers are from memory
   (AMP, CAPS, Muon, SWA, symmetry, AlphaStar, Bansal) and should be checked
   when a review uses them.
7. **Judge lists:** the striker request names two judges (two-level controller
   and flat self-play), since decomposition is an implementation choice.
8. **`docs/approach_catalogue.yaml` is kept** and marked superseded in
   `knowledge/sources.md`; its `gaps:` table lives on in the 2026-10-06 review.

## Not built yet (next)

- The engine reading a request: designers choosing approaches by symptom and
  tag, and the verdict reported per requirement (today the kick judge still
  reports bench v2 / fitness_v2 terms).
- Appending a use automatically when a verdict comes back on a run that
  changed one approach.
- Re-judging a parent request when a subtask gets a new champion.
- A literature-review runner (search → source records → cards → shortlist);
  reviews are written by hand until then.
- Per-section smoke tests for task implementations (harbor's idea).

# Task requests

The **what**: each folder holds one task request from a requester (the
runswift behaviour module or a person): goal, requirements with priorities,
verification (the benchmark that decides success), constraints, optional
priors, budget and deliverable. The **how** (task implementations) are the
recipes in `experiments/recipes/`, each naming the request it answers
(`request:`), built from the approaches in `knowledge/approaches/`.

```
requester ── request.yaml ──▶ engine: implementations (recipes) → train → judge
          ◀── report ──────── verdict per requirement, deploy gate, robot check
```

| Request | Level | Status | Judge |
|---|---|---|---|
| [kick](kick/request.yaml) | 0 | draft | kick_bench_v2 |
| [dribble](dribble/request.yaml) | 0 | draft | dribble_gate |
| [striker](striker/request.yaml) | 1 (subtasks: kick, walk) | draft | controller_eval, selfplay_eval |

## Lifecycle

`draft` → `agreed` (the requester signed off the requirements and the
verification) → `frozen` (`rsw request freeze NAME`: the interface,
requirements and verification are hashed; nothing in the loop may change them)
→ `delivered` / `retired`. A change after freezing is a new `version`.

The system may propose requirements (making a fuzzy wish measurable) and, when
a request proves infeasible, report the evidence and propose a relaxation; it
never relaxes a requirement itself.

## Levels

Level 0 acts on joints. A request with `level` > 0 acts through `subtasks`:
lower-level requests or deployed policies. A child's run-time `interface` is
its parent's action space; a new child result means the parent is judged
again (not automated yet). Decomposition (flat vs hierarchical) is an
implementation choice, tested like any other.

## Commands

```bash
rsw request list            # every request with its status and check
rsw request check [NAME]    # schema, judges, implementations, subtasks, frozen hash
rsw request show NAME       # the request and its task tree
rsw request freeze NAME --agreed   # only after the requester's sign-off
```

Schema: `src/k1/requests.py`.

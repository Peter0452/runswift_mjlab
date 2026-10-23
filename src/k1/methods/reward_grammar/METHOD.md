# reward_grammar

**What.** Reward programs written as JSON expressions (add, scale or gate terms) and loaded into the stage-3 env.

**Source.** `k1/tasks/velocity/mdp/reward_grammar.py`; L1 of the hierarchical evolution loop (`evolve_hier.py`).

**Where it plugs in.** Env var `KICK_REWARD_PROGRAM=path.json`, read by `kick/env_cfg.py`.

**Deployment impact.** Training-only.

**Status.** experimental: used by the evolution loop's reward level.

**Evidence.** See docs/K1_KICK_REWARD_EVOLUTION_DESIGN.md and the experience records (docs/experience/).

**Pitfalls.** Lint programs (`reward_lint.py`) and check the hacking surface (lessons R13, R23) before training.

Registry entry: `k1/methods/registry.py` (extension points, parameter fields, `detect`).
Promotion rule and statuses: `knowledge/architecture.md`.

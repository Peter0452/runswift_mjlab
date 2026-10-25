---
id: fast_sac
title: FastSAC off-policy training
element: value
also:
- agent
- optimisation
tags:
- sample-efficiency
status: parked
impact: training-only
sources:
- ours
registry: fast_sac
trial: null
tune: null
---

# FastSAC off-policy training

**What.** Off-policy FastSAC training for the velocity tasks.

**Source.** `k1/tasks/velocity/rl/fast_sac_runner.py`, `src/mjlab/rl/fast_sac/`.

**Where it plugs in.** Its own runner; no registered K1 task uses it since 2026-10-23 (FastSAC tasks removed, on the archive branch).

**Deployment impact.** Training-only.

**Status.** parked: kept in code, not pursued.

**Evidence.** No benchmark evidence for K1 skills.

**Pitfalls.** Conflicts with AMP-PPO (different algorithm).

Registry entry: `k1/approaches/registry.py` (extension points, parameter fields, `detect`).
Uses: `knowledge/uses/uses.yaml`. Promotion rule and statuses: `knowledge/architecture.md`.

# fast_sac

**What.** Off-policy FastSAC training for the velocity tasks.

**Source.** `k1/tasks/velocity/rl/fast_sac_runner.py`, `src/mjlab/rl/fast_sac/`.

**Where it plugs in.** Its own runner; no registered K1 task uses it since 2026-10-23 (FastSAC tasks removed, on the archive branch).

**Deployment impact.** Training-only.

**Status.** parked: kept in code, not pursued.

**Evidence.** No benchmark evidence for K1 skills.

**Pitfalls.** Conflicts with AMP-PPO (different algorithm).

Registry entry: `k1/methods/registry.py` (extension points, parameter fields, `detect`).
Promotion rule and statuses: `knowledge/architecture.md`.

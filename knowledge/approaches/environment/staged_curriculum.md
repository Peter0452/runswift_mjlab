---
id: staged_curriculum
title: "Staged curriculum with warm-start handoff (walk \u2192 approach \u2192 kick)"
element: environment
also:
- optimisation
tags:
- exploration
status: adopted
impact: training-only
sources:
- ours
registry: null
trial: null
tune: null
---

# Staged curriculum with warm-start handoff (walk → approach → kick)

**What.** Train in stages that share one actor layout; hand off with
`scripts/prepare_warmstart.py --reset-obs-dims` so slots a stage held constant
are re-initialised.

**Evidence.** A plain resume collapsed stage 2 (KL 22); the warm-start reset
fixed it (ball distance 2.5 → 0.65 m in 60 iterations). The champion h022
came out of this pipeline (`knowledge/skills/kick.md`).

Uses: `knowledge/uses/uses.yaml`.

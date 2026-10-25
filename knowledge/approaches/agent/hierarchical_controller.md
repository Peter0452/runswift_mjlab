---
id: hierarchical_controller
title: Two-level controller over frozen skills
element: agent
also:
- environment
tags:
- multi-skill
status: experimental
impact: training-only
sources:
- ours
registry: null
trial: null
tune: null
---

# Two-level controller over frozen skills

**What.** A GRU controller chooses between frozen kick and walk skills
every 0.2 s (striker).

**Where it plugs in.** `Mjlab-Velocity-Striker-Controller-Booster-K1`
(`k1/tasks/striker/`).

**Evidence.** controller_v2/1750 + h022: 0.441 goal share vs h022 (best
two-level system); v3–v7 did not beat v2; the decision layer adds only
~+0.02–0.04 over a scripted rule (`knowledge/skills/selfplay_striker.md`).

Uses: `knowledge/uses/uses.yaml`.

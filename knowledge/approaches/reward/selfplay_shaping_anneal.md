---
id: selfplay_shaping_anneal
title: Anneal task shaping in self-play (Bansal-style)
element: reward
also:
- environment
tags:
- multi-skill
status: experimental
impact: training-only
sources:
- bansal2018_competition
registry: null
---

# Anneal task shaping in self-play (Bansal-style)

**What.** Dense task shaping that is annealed toward the sparse game
reward as self-play training goes on.

**Where it plugs in.** Self-play reward weights (`k1/tasks/selfplay/`).

**Evidence.** The user asked for annealing to 0.2; freezing α in v13–v16
deviated from that and was reported (`knowledge/objectives.md`).

Uses: `knowledge/uses/uses.yaml`.

---
id: fall_constraint
title: Falls as an adaptive constraint (Lagrangian)
element: reward
also:
- value
tags:
- safety
status: candidate
impact: training-only
sources:
- deployment_scenarios
registry: null
trial: null
tune: null
---

# Falls as an adaptive constraint (Lagrangian)

**What.** Treat falls as a constraint with an adaptive multiplier
(PPO-Lagrangian style) instead of a fixed penalty. From the L5 approach catalogue (`docs/approach_catalogue.yaml`, 2026-10-07).

Uses: `knowledge/uses/uses.yaml`.

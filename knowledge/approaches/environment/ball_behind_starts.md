---
id: ball_behind_starts
title: Ball-behind and far spawns
element: environment
also: []
tags:
- sim2real
- safety
- perception
status: candidate
impact: training-only
sources:
- deployment_scenarios
registry: null
trial:
  genes:
    s.spawn_any_prob: 0.3
    s.far_spawn_prob: 0.3
tune:
  genes.s.spawn_any_prob:
    range:
    - 0.1
    - 0.5
    tags:
    - safety
    - perception
    step: up
  genes.s.far_spawn_prob:
    range:
    - 0.1
    - 0.5
    tags:
    - safety
    - perception
    step: up
---

# Ball-behind and far spawns

**What.** Spawn the ball at any bearing and far away. From the L5 approach catalogue (`docs/approach_catalogue.yaml`, 2026-10-07).

**Why.** Benchmark v2 approach falls with the ball behind were 23–45 %.

Uses: `knowledge/uses/uses.yaml`.

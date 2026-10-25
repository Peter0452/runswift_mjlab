---
id: world_model_ball
title: Fresh ball at any bearing (team ball feed)
element: environment
also: []
tags:
- perception
status: candidate
impact: training-only
sources:
- deployment_scenarios
registry: null
trial:
  genes:
    s.world_ball_prob: 0.2
tune:
  genes.s.world_ball_prob:
    range:
    - 0.05
    - 0.4
    tags:
    - perception
    step: up
---

# Fresh ball at any bearing (team ball feed)

**What.** Episodes where a fresh ball appears at any bearing, as a team
ball or localisation feed would give. From the L5 approach catalogue (`docs/approach_catalogue.yaml`, 2026-10-07).

Uses: `knowledge/uses/uses.yaml`.

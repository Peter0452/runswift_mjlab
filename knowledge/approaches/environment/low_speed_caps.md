---
id: low_speed_caps
title: Episodes at runswift's low speed caps
element: environment
also: []
tags:
- speed
status: candidate
impact: training-only
sources:
- deployment_scenarios
registry: null
trial:
  genes:
    s.cap_low_prob: 0.3
tune:
  genes.s.cap_low_prob:
    range:
    - 0.05
    - 0.4
    tags:
    - speed
    step: up
---

# Episodes at runswift's low speed caps

**What.** Train some episodes at runswift's low caps 0.5 / 0.3 / 0.6. From the L5 approach catalogue (`docs/approach_catalogue.yaml`, 2026-10-07).

Uses: `knowledge/uses/uses.yaml`.

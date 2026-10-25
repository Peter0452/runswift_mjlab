---
id: deployment_scenarios
kind: ours
title: 'Benchmark v2 findings: situations the robot meets that training lacked (2026-10-07)'
path: docs/benchmarks_v2/
task: kick loop
robot: Booster K1
approach:
- element: environment
  what: ball-behind, world-model ball, low-cap scenarios
- element: reward
  what: fall constraint
approaches:
- ball_behind_starts
- world_model_ball
- low_speed_caps
- fall_constraint
extraction: extracted
---

# Benchmark v2 findings: situations the robot meets that training lacked (2026-10-07)

Their approach, as elements:

- **environment**: ball-behind, world-model ball, low-cap scenarios
- **reward**: fall constraint

Our evidence: use records (knowledge/uses/uses.yaml), knowledge/skills, knowledge/lessons.

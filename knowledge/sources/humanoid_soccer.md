---
id: humanoid_soccer
kind: repo
title: Learning Agile Striker Skills for Humanoid Soccer Robots from Noisy Sensory Input
citation: ICRA 2026 (Booster)
url: https://humanoidsoccer.github.io
path: ../humanoid-soccer
task: 'striker: chase, kick, from noisy sensing'
robot: Booster humanoid
approach:
- element: agent
  what: four-stage privileged teacher -> DAgger student
- element: reward
  what: N-P3O constrained refinement
approaches:
- privileged_teacher_dagger
- np3o_constrained
extraction: extracted
---

# Learning Agile Striker Skills for Humanoid Soccer Robots from Noisy Sensory Input

Their approach, as elements:

- **agent**: four-stage privileged teacher -> DAgger student
- **reward**: N-P3O constrained refinement

Claims and setting: approach atoms extracted (docs/approach_catalogue.yaml); claims not yet recorded.

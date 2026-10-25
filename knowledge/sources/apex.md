---
id: apex
kind: repo
title: 'APEX: Action Priors Enable Efficient Exploration for Robust Motion Tracking on Legged
  Robots'
citation: IROS 2026
url: https://marmotlab.github.io/APEX/
path: ../APEX
licence: MIT
task: motion tracking
robot: legged robots
approach:
- element: agent
  what: decaying action prior toward reference motions
- element: value
  what: multi-critic advantage mixing
approaches:
- decap
- multi_critic
extraction: extracted
notes: Brought in by the collaborator's appex commit (2026-10-16).
---

# APEX: Action Priors Enable Efficient Exploration for Robust Motion Tracking on Legged Robots

Their approach, as elements:

- **agent**: decaying action prior toward reference motions
- **value**: multi-critic advantage mixing

Claims and setting: approach atoms extracted (docs/approach_catalogue.yaml); claims not yet recorded.

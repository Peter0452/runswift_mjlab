---
id: gmr
kind: repo
title: 'GMR: General Motion Retargeting'
citation: arXiv 2505.02833, 2510.02252
path: ../GMR
licence: MIT
task: human mocap -> robot motion
robot: many (K1 retargets in data/retargeted/k1)
approach:
- element: environment
  what: retargeted human motion as clips
approaches:
- retarget_human_kicks
- retarget_slow_cadence_walks
extraction: extracted
---

# GMR: General Motion Retargeting

Their approach, as elements:

- **environment**: retargeted human motion as clips

Claims and setting: approach atoms extracted (docs/approach_catalogue.yaml); claims not yet recorded.

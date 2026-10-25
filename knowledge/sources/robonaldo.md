---
id: robonaldo
kind: repo
title: 'RoboNaldo: humanoid soccer shooting via motion-guided curriculum RL'
citation: arXiv 2606.11092
path: ../RoboNaldo
task: free kick / shooting
robot: Unitree G1
approach:
- element: reward
  what: track a reference kick, then relax to task reward
- element: environment
  what: reference kick motion data
approaches:
- motion_guided_curriculum
- g1_kick_reference
extraction: extracted
---

# RoboNaldo: humanoid soccer shooting via motion-guided curriculum RL

Their approach, as elements:

- **reward**: track a reference kick, then relax to task reward
- **environment**: reference kick motion data

Claims and setting: approach atoms extracted (docs/approach_catalogue.yaml); claims not yet recorded.

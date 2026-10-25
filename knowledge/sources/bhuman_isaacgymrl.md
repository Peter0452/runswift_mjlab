---
id: bhuman_isaacgymrl
kind: repo
title: B-Human RoboCup 2026 K1 walk + kick policies (Booster Gym fork)
path: MachineLearning/IsaacGymRL
licence: Apache-2.0 (Booster Gym); check B-Human terms for weights
task: K1 walking and inner-foot kicking
robot: Booster K1
approach:
- element: reward
  what: momentum kick, planted support, side-foot strike, Gaussian speed reward
- element: environment
  what: torque clip, their ball and DR
- element: agent
  what: gait clock input
approaches:
- momentum_kick
- planted_support
- side_foot_kick
- continuous_kick_range
- torque_clip
- gait_clock
- bhuman_action_imitation
extraction: extracted
notes: Atoms from docs/approach_catalogue.yaml; port in knowledge/skills/bhuman_kick.md.
---

# B-Human RoboCup 2026 K1 walk + kick policies (Booster Gym fork)

Their approach, as elements:

- **reward**: momentum kick, planted support, side-foot strike, Gaussian speed reward
- **environment**: torque clip, their ball and DR
- **agent**: gait clock input

Claims and setting: approach atoms extracted (docs/approach_catalogue.yaml); claims not yet recorded.

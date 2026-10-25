---
id: side_foot_kick
title: Side-foot (inside-foot) strike
element: reward
also:
- environment
tags:
- accuracy
- style
status: experimental
impact: training-only
sources:
- bhuman_isaacgymrl
registry: null
trial: null
tune: null
---

# Side-foot (inside-foot) strike

**What.** Strike with the inside of the foot (sole yaw ~90° to the kick
direction), via a reward and/or AMP / RSI clips. From the L5 approach catalogue (`docs/approach_catalogue.yaml`, 2026-10-07).

**Evidence.** AMP clips + RSI alone: 1–2 % side-foot (v59, v60). Explicit
`side_foot_strike` reward: the Gaussian version had no gradient (lint
VANISHING), the ramp version gave 1 % side-foot at +250 (evo_g011): local
shaping does not discover it. A straight-kick-only teacher raised inside-foot
kicks 11 → 24 % in the dribble (v36, see `kick_teacher`).

Uses: `knowledge/uses/uses.yaml`.

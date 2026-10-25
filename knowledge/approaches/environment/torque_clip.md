---
id: torque_clip
title: Leg torque clip at B-Human's kick values
element: environment
also: []
tags:
- sim2real
- safety
status: adopted
impact: runtime
sources:
- bhuman_isaacgymrl
registry: null
trial: null
tune: null
---

# Leg torque clip at B-Human's kick values

**What.** Clip leg torque at 50 / 50 / 30 / 60 / 30 / 30 Nm (hip pitch,
roll, yaw, knee, ankle pitch, roll). From the L5 approach catalogue (`docs/approach_catalogue.yaml`, 2026-10-07).

**Deployment impact.** Part of the deploy contract (runner torque clip).

**Evidence.** Knee p90 107 → 54 Nm. Real robot data shows torques above the
sim caps (`knowledge/lessons/sim2real.md`).

Uses: `knowledge/uses/uses.yaml`.

---
id: amp_walk_dr
title: Domain randomisation, latency and limits inherited from the AMP walk
element: environment
also: []
tags:
- sim2real
status: adopted
impact: training-only
sources:
- ours
registry: null
---

# Domain randomisation, latency and limits inherited from the AMP walk

**What.** DR, latency and joint/torque limits copied from the AMP walk,
because that walk transfers to the robot.

**Deployment impact.** Training-only, but tied to what the robot does: change
only with robot evidence and the user's go-ahead (standing decision 2026-10-02).

**Evidence.** Every deployed model; leg torque hard-clipped at B-Human's kick
clip since 2026-10-07 (see `torque_clip`).

Uses: `knowledge/uses/uses.yaml`.

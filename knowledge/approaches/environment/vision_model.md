---
id: vision_model
title: Camera-view, noise, memory and lost-ball model
element: environment
also: []
tags:
- perception
- sim2real
status: adopted
impact: runtime
sources:
- ours
registry: null
trial: null
tune: null
---

# Camera-view, noise, memory and lost-ball model

**What.** The actor only sees the ball as the robot's vision would:
field-of-view gate, detection noise, dropout, delay, IMU-only memory and the
lost rule with a virtual ball.

**Deployment impact.** Deployment contract (`knowledge/deployment.md`);
checked by `lost_rule_parity.py`.

**Evidence.** Training with odometry-based memory made the head and approach
fail on the robot (no odometry in the runner, 2026-10-02).

Uses: `knowledge/uses/uses.yaml`.

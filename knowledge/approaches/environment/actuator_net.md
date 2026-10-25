---
id: actuator_net
title: Learned residual actuator / contact model from robot logs
element: environment
also: []
tags:
- sim2real
status: candidate
impact: training-only
sources:
- contact_uan
registry: null
trial: null
tune: null
---

# Learned residual actuator / contact model from robot logs

**What.** Train a residual model of the actuators and contacts on real robot
logs and keep it frozen inside the simulator while policies train, so the
simulator matches the robot (Contact-UAN).

**Why it fits.** Real K1 runs showed torques above the sim caps, weak knee
tracking and L/R asymmetry (`knowledge/lessons/sim2real.md`).

**Pitfalls.** The code is hard-coded for the Unitree G1; needs K1 logs (so far
from robot #291 only). Port plan in session memory (contact-uan-for-k1).

Uses: `knowledge/uses/uses.yaml`.

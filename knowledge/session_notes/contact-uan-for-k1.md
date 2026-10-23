---
name: contact-uan-for-k1
description: contact-uan repo (RL/contact-uan) = learned residual actuator model from real logs; G1-hardcoded; assessed 2026-10-23 as a fit for K1 real2sim gaps
metadata:
  node_type: memory
  type: reference
  originSessionId: fa876b9b-a11f-4b6e-a0c0-560ef642c26f
  modified: 2026-10-22T23:25:56.647Z
---

RL/contact-uan is an mjlab fork that trains a UAN: a small per-actuator-family MLP that adds a joint-target residual from 3 frames of (target - q, dq). It is trained with PPO so that 24-step sim rollouts, reset from recorded real states with feet on the ground, match the real next joint positions. Downstream policies train with the frozen UAN in the loop and deploy without it. It also has a torque-speed target clip (`TorqueSpeedClippedJointPositionAction`).

Everything is hardcoded for G1: 29 joints, 5 families, 174-dim obs, 96-dim state. Resets need base velocity, root height and contact, which come from 6 estimators trained in sim.

As of 2026-10-23 our K1 logs (q, dq, tau, q_target, imu at 50 Hz, same rate as UAN) total about 8 min from robot #291. Assessment: it targets [[k1-real2sim-findings]] (knee tracking, torque/PD mismatch, impacts). Shared weights per family can't capture L/R asymmetry. A residual can't exceed the sim effort caps, so those must be raised first. Adopt only through [[benchmark-gated-adoption]].

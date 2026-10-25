---
id: contact_uan
kind: repo
title: 'Contact-UAN: learned residual actuator / contact model from robot data'
path: ../contact-uan
task: sim2real for running, force control, jumping
robot: Unitree G1 (hard-coded)
approach:
- element: environment
  what: residual model trained on robot logs, frozen inside the simulator
approaches:
- actuator_net
extraction: summary
notes: Port plan and caveats for the K1 in session memory (contact-uan-for-k1).
---

# Contact-UAN: learned residual actuator / contact model from robot data

Their approach, as elements:

- **environment**: residual model trained on robot logs, frozen inside the simulator

Claims and setting: summary only; extract claims when a review needs them.

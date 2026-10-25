---
id: enpire2026
kind: paper
title: 'ENPIRE: Agentic Robot Policy Self-Improvement in the Real World'
citation: arXiv 2606.19980 (NVIDIA GEAR et al.), 2026
url: https://arxiv.org/abs/2606.19980
path: ../ENPIRE
licence: Apache-2.0
task: real-world manipulation (Push-T, pin insertion, zip tie)
robot: bimanual arm fleet
approach:
- element: agent
  what: behaviour cloning, contrastive BC, BC regularisation of online RL
- element: value
  what: online / offline SAC (PLD learner)
approaches: []
extraction: summary
notes: Mainly a source for the loop design (reviews/2026-10-25_enpire_harbor_loop.md); BC
  regularisation was their largest single gain.
---

# ENPIRE: Agentic Robot Policy Self-Improvement in the Real World

Their approach, as elements:

- **agent**: behaviour cloning, contrastive BC, BC regularisation of online RL
- **value**: online / offline SAC (PLD learner)

Claims and setting: summary only; extract claims when a review needs them.

---
id: vinyals2019_alphastar
kind: paper
title: Grandmaster level in StarCraft II using multi-agent reinforcement learning (AlphaStar)
citation: Vinyals et al. Nature 2019
task: StarCraft II
robot: none
approach:
- element: agent
  what: KL penalty toward the supervised policy during RL
- element: environment
  what: league self-play
approaches:
- kl_anchor
extraction: summary
notes: Inspiration only (cited in k1/tasks/velocity/rl/anchor.py).
---

# Grandmaster level in StarCraft II using multi-agent reinforcement learning (AlphaStar)

Their approach, as elements:

- **agent**: KL penalty toward the supervised policy during RL
- **environment**: league self-play

Claims and setting: summary only; extract claims when a review needs them.

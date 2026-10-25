---
id: peng2021_amp
kind: paper
title: 'AMP: Adversarial Motion Priors for Stylized Physics-Based Character Control'
citation: Peng, Ma, Abbeel, Levine, Kanazawa. ACM TOG (SIGGRAPH) 2021
task: character locomotion and skills with natural style
robot: simulated characters
approach:
- element: reward
  what: style reward from a discriminator on reference motion clips, mixed with the task reward
approaches:
- amp
- conditioned_amp
extraction: summary
notes: Our AMP-PPO lives in src/mjlab/amp/.
---

# AMP: Adversarial Motion Priors for Stylized Physics-Based Character Control

Their approach, as elements:

- **reward**: style reward from a discriminator on reference motion clips, mixed with the task reward

Claims and setting: summary only; extract claims when a review needs them.

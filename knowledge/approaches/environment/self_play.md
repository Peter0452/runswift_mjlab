---
id: self_play
title: Self-play against frozen copies and an opponent pool
element: environment
also: []
tags:
- multi-skill
status: adopted
impact: training-only
sources:
- bansal2018_competition
- ours
registry: null
---

# Self-play against frozen copies and an opponent pool

**What.** Fine-tune in 1v1 games against frozen mirror copies and a pool
(h022, walk 9950, controller v2, snapshots).

**Evidence.** swa_v15v16_9100 beats h022 under the same scripted controller
(goal share 0.421 vs 0.402, 6/6 seeds) and was deployed (user request).
Fine-tunes drift without the KL anchor (`kl_anchor`).

**Pitfalls.** Judge against fixed opponents, not the moving league. Even the
sides by giving the opponent the learner's DR, never by removing it from the learner.

Uses: `knowledge/uses/uses.yaml`.

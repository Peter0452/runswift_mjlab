---
id: multi_critic
title: Multi-critic advantage mix (APEX)
element: value
also: []
tags:
- multi-objective
status: experimental
impact: training-only
sources:
- apex
registry: multi_critic
trial:
  methods:
    multi_critic:
      alphas:
      - 0.5
      - 0.5
tune: null
---

# Multi-critic advantage mix (APEX)

**What.** Separate critic heads per reward group (style, task, optional extra group); advantages normalised per group and mixed by `alphas`.

**Source.** APEX multi-critic; `src/mjlab/amp/modules/multi_critic.py`. Added with the appex commit (2026-10-16).

**Where it plugs in.** `algorithm.multi_critic_alphas` (style first, then task, then `extra_reward_group`), `extra_reward_group` (env reward terms moved into a third group, e.g. the dribble's kick terms).

**Deployment impact.** Training-only.

**Status.** experimental: walk tasks and stage 1 use (0.2, 0.8), stage 3 (0.5, 0.5); no deployed model trained with it yet.

**Evidence.** Walk: style advantage at 98 % discriminator accuracy is saturated noise, so style gets 0.2 (skills/walk.md). Not yet benchmarked against single-critic on the kick.

**Pitfalls.** Changing the number of groups changes the critic's shape: checkpoints don't load across it without a warm-start.

Registry entry: `k1/approaches/registry.py` (extension points, parameter fields, `detect`).
Uses: `knowledge/uses/uses.yaml`. Promotion rule and statuses: `knowledge/architecture.md`.

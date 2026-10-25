---
id: conditioned_amp
title: Command-conditioned AMP discriminator (amp_cond)
element: reward
also: []
tags:
- imitation
- style
status: experimental
impact: training-only
sources:
- peng2021_amp
- ours
registry: conditioned_amp
trial: null
tune: null
---

# Command-conditioned AMP discriminator (amp_cond)

**What.** The discriminator also sees the command (amp_cond observation group), so style can depend on speed / mode instead of copying one posture.

**Source.** Dribble v20; AMP runner (`amp_cond_free_prob`, `amp_speed_mass`).

**Where it plugs in.** Env observation group `amp_cond`; runner `amp_cond_free_prob`, `amp_speed_mass`.

**Deployment impact.** Training-only (discriminator input).

**Status.** experimental: dribble v20+.

**Evidence.** R25: v20 conditioning helped a little (+0.05–0.08) after the faster mix leaned the dribble 16°; runner leg jitter rose 0.066 → 0.080 (skills/dribble.md).

**Pitfalls.** The discriminator's input size depends on it: evaluation and export need the run's `DRIBBLE_GENES`.

Registry entry: `k1/approaches/registry.py` (extension points, parameter fields, `detect`).
Uses: `knowledge/uses/uses.yaml`. Promotion rule and statuses: `knowledge/architecture.md`.

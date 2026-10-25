---
id: swa_blend
title: Weight averaging and weight-space blends of checkpoints
element: optimisation
also:
- agent
tags:
- stability
status: adopted
impact: training-only
sources:
- izmailov2018_swa
registry: swa_blend
trial: null
tune: null
---

# Weight averaging and weight-space blends of checkpoints

**What.** Averaging nearby checkpoints (SWA) or blending two same-architecture checkpoints in weight space.

**Source.** `scripts/tools/average_checkpoints.py`, `blend_checkpoints.py`, `blend_search.py`; the evolution loop's crossover.

**Where it plugs in.** Post-training on checkpoints; no config field.

**Deployment impact.** Training-only (produces a checkpoint; the deployed graph is unchanged).

**Status.** adopted: deployed dribble swaA_v15b and self-play swa_v15v16 are SWA checkpoints.

**Evidence.** E20: champion blends were the main promotion route in the evolution loops; E21: SWA is a cheap, reliable gain. R27: blending the dribble and kick skills gives the worst of both.

**Pitfalls.** Blends don't fine-tune well afterwards (ft_x50a/b fell from 170 to 80–98 goals). Robot: swaA fell 1.9 times per upright minute (skills/dribble.md): the benchmark gate still applies.

Registry entry: `k1/approaches/registry.py` (extension points, parameter fields, `detect`).
Uses: `knowledge/uses/uses.yaml`. Promotion rule and statuses: `knowledge/architecture.md`.

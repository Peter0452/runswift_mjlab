---
id: task_reward_shaping
title: Shaping weights of the task's own reward terms
element: reward
also: []
tags:
- power
- accuracy
- speed
- smoothness
- safety
status: adopted
impact: training-only
sources:
- ours
registry: null
trial: null
tune:
  genes.w.long_kick_power:
    range:
    - 1000.0
    - 8000.0
    tags:
    - power
    step: up
  genes.w.long_kick_speed_linear:
    range:
    - 300.0
    - 2000.0
    tags:
    - power
    step: up
  genes.w.kick_direction:
    range:
    - 300.0
    - 2000.0
    tags:
    - accuracy
    step: up
  genes.w.kick_rest_accuracy:
    range:
    - 300.0
    - 2000.0
    tags:
    - accuracy
    step: up
  genes.w.walk_speed_track:
    range:
    - 1.0
    - 12.0
    tags:
    - speed
    step: up
  genes.w.action_rate_l2:
    range:
    - -0.4
    - -0.05
    tags:
    - smoothness
    step: up
  genes.w.touchdown_speed:
    range:
    - -80.0
    - -10.0
    tags:
    - smoothness
    step: up
  genes.w.hop_kick_fall:
    range:
    - -3000.0
    - -300.0
    tags:
    - safety
    step: up
---

# Shaping weights of the task's own reward terms

**What.** The weights of the kick loop's reward terms, set per run by
`KICK_GENES` (`w.<term>`). Tuning them is reward shaping inside the existing
reward; new terms or programs are `reward_grammar`.

**Where it plugs in.** Recipe `genes:` (`w.<term>`), read by `kick/env_cfg.py`.

**Deployment impact.** Training-only.

**Evidence.** The hierarchical evolution loop's L0 tuned these genes and
produced the champion h022 (`docs/experience/experiences.jsonl`). Ranges are
the outer loop's defaults (`k1/cli.py` `EVOLVE_GENES`, Step 5) widened to the
champion's values.

**Pitfalls.** Lint the hacking surface (lessons R13, R23); gait penalties stay
light (objectives 2026-10-20).

Uses: `knowledge/uses/uses.yaml`.

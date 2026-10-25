---
id: bhuman_action_imitation
title: Plain action imitation of B-Human's kick policy
element: agent
also: []
tags:
- imitation
status: rejected
impact: training-only
sources:
- bhuman_isaacgymrl
registry: bhuman_action_imitation
trial: null
tune: null
---

# Plain action imitation of B-Human's kick policy

**What.** Imitating B-Human's kick policy actions directly.

**Source.** Dribble v41/v43 experiments (B-Human teacher / takeover).

**Where it plugs in.** `kick_teacher_bhuman_dist`, `kick_takeover_prob` (the teacher method's parameters).

**Deployment impact.** Training-only.

**Status.** rejected.

**Evidence.** v41 collapsed our kick (1.96 m/s, 37°); takeover (v43) also hurt; lesson: don't retry plain action imitation of B-Human (skills/dribble.md).

**Pitfalls.** B-Human as a benchmark reference and as a teacher in a gated form remains allowed (user, 2026-10-22); mix B-Human ideas in only on fixed-benchmark gains.

Registry entry: `k1/approaches/registry.py` (extension points, parameter fields, `detect`).
Uses: `knowledge/uses/uses.yaml`. Promotion rule and statuses: `knowledge/architecture.md`.

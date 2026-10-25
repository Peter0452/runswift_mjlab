---
id: decap
title: Decaying action prior (DecAP, from APEX)
element: agent
also: []
tags:
- exploration
- imitation
status: experimental
impact: training-only
sources:
- apex
registry: decap
trial:
  methods:
    decap:
      source: kick
tune: null
---

# Decaying action prior (DecAP, from APEX)

**What.** Decaying action prior: joint targets are blended toward a reference (AMP clips or retargeted kicks) with weight β = gamma^(step/k), fading to zero.

**Source.** APEX (DecAP); `k1/tasks/velocity/mdp/decap.py`, attached by the AMP runner (`_attach_decap`). Added by the collaborator's appex commit (2026-10-16).

**Where it plugs in.** `decap`, `decap_source` (`loader` = this task's AMP clips, `kick` = retargeted kick clips, which also place the ball), `decap_gamma`, `decap_k`.

**Deployment impact.** Training-only as long as β has decayed to ~0 before export; a policy exported while the prior still acts relies on targets the robot never gets.

**Status.** experimental: on in the AMP walk tasks, stage 1 and stage 3 since 2026-10-16; no deployed model was trained with it yet.

**Evidence.** None on the fixed benchmarks yet. With the kick source the strike is placed at the foot, so stage 3 turns `ball_avoidance` off when it is on (user decision 2026-10-23).

**Pitfalls.** Check β at the checkpoint you export. Resumes recompute β from the iteration (`set_decay_steps`).

Registry entry: `k1/approaches/registry.py` (extension points, parameter fields, `detect`).
Uses: `knowledge/uses/uses.yaml`. Promotion rule and statuses: `knowledge/architecture.md`.

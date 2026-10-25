---
id: kick_teacher
title: Teacher imitation near the ball (kick-loop or B-Human teacher)
element: agent
also:
- environment
tags:
- imitation
- power
status: experimental
impact: training-only
sources:
- ours
registry: kick_teacher
trial: null
tune: null
---

# Teacher imitation near the ball (kick-loop or B-Human teacher)

**What.** MSE imitation of a teacher's actions near the ball (kick-loop checkpoint, or B-Human's kick policy in angled windows), decaying over updates.

**Source.** AMP runner and AMP-PPO (`imitation_coef`); dribble kick mode v23+.

**Where it plugs in.** `algorithm.imitation_coef`, `imitation_decay_updates`; runner `kick_teacher_checkpoint`, `kick_teacher_dist`, `kick_teacher_max_offset_deg`, `kick_teacher_arms`, `kick_teacher_bhuman_dist`, `kick_takeover_prob`.

**Deployment impact.** Training-only.

**Status.** experimental: dribble kick mode (not yet deployed).

**Evidence.** The kick-loop teacher (h011, legs) anchors dribble kick power: teacher off (v34) dropped to 2.63 m/s; straight-kick-only teaching (v36) raised inside-foot kicks 11 → 24 %. B-Human as executor/teacher (v41, v43) collapsed our kick (skills/dribble.md).

**Pitfalls.** Plain action imitation of B-Human is rejected (see `bhuman_action_imitation`); B-Human may still be used as a teacher (user, 2026-10-22).

Registry entry: `k1/approaches/registry.py` (extension points, parameter fields, `detect`).
Uses: `knowledge/uses/uses.yaml`. Promotion rule and statuses: `knowledge/architecture.md`.

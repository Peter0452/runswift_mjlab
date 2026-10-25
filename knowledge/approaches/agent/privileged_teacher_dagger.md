---
id: privileged_teacher_dagger
title: Privileged teacher distilled by DAgger into a noisy-input student
element: agent
also:
- environment
tags:
- perception
- sim2real
- accuracy
status: candidate
impact: training-only
sources:
- humanoid_soccer
registry: null
---

# Privileged teacher distilled by DAgger into a noisy-input student

**What.** Train a teacher with privileged inputs (true ball, no vision
noise), then distil it by DAgger into the deployable student (our 83 inputs). From the L5 approach catalogue (`docs/approach_catalogue.yaml`, 2026-10-07).

**Targets.** Aim, time to first kick, search success.

Uses: `knowledge/uses/uses.yaml`.

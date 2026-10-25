---
id: continuous_kick_range
title: Continuous kick-speed command + strong-kick flag
element: reward
also:
- agent
tags:
- power
- accuracy
status: candidate
impact: runtime
sources:
- bhuman_isaacgymrl
registry: null
trial: null
tune: null
---

# Continuous kick-speed command + strong-kick flag

**What.** Kick speed commanded from a continuous range plus a strong-kick
flag, with a Gaussian speed reward. From the L5 approach catalogue (`docs/approach_catalogue.yaml`, 2026-10-07).

**Deployment impact.** Changes the meaning of observation slots 80–82 (same
dims): a runner change and parity check.

**Targets.** Short-pass stopping distance, long kick speed.

Uses: `knowledge/uses/uses.yaml`.

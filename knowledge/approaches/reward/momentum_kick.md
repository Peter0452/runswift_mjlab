---
id: momentum_kick
title: 'Momentum kick: kick while walking into the ball'
element: reward
also: []
tags:
- power
status: adopted
impact: training-only
sources:
- bhuman_isaacgymrl
registry: null
trial: null
tune: null
---

# Momentum kick: kick while walking into the ball

**What.** Reward kick quality without tying it to a standstill, so the
policy kicks while walking into the ball. From the L5 approach catalogue (`docs/approach_catalogue.yaml`, 2026-10-07).

**Where it plugs in.** Stage-3 kick-loop rewards (`k1/tasks/kick/mdp/kick_loop.py`).

**Evidence.** v57: long 3D kick speed 5.6 → 8.0 m/s; body speed at contact 0.12 → 0.56 m/s.

Uses: `knowledge/uses/uses.yaml`.

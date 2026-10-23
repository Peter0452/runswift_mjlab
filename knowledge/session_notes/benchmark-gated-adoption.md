---
name: benchmark-gated-adoption
description: Adopt/mix B-Human (or any external) techniques with ours only when a fixed objective benchmark shows a gain; aim to transcend both
metadata:
  type: feedback
---
Learning from B-Human's kick is good, but the aim is to transcend it: adopt and mix their techniques with ours, then evolve combinations — and accept any adoption/combination only on strict, objective measurements against a fixed benchmark (ours vs B-Human vs our best), never because it resembles the reference. (User, 2026-10-05.)

2026-10-06: optimise primarily for **accuracy, time to kick and power** without compromising other objectives; B-Human must be beaten *convincingly* (clear margin on the head-to-head metrics, both perception modes), then keep improving. Overnight work = the two evolutionary loops (L1 params/weights, L2+ reward structure) kept aligned on one benchmark fitness, iterating continuously.

**Why:** imitation for its own sake can cost our other objectives; the goal is the best kick system, not a copy.
**How to apply:** run the fixed kick benchmark (scripts/tools/kick_benchmark.py) on every candidate; promote only if it beats the reference on the targeted metrics and passes no-regression gates on all others. Related: [[k1-kick-objectives]]

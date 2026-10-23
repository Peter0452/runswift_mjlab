---
name: dribble-kick-objectives
description: User's objectives for the dribble policy's kick mode (2026-10-21) - power ≥ B-Human, air ok, quick, re-kick until the ball leaves, style by geometry then outcome, keep the dribble, later dribble→kick transitions
metadata:
  type: project
---
User, 2026-10-21, for the dribble policy's kick mode (obs slot 82):
- **Style choice:** geometry gating first (kick direction vs approach line: under ~30° = power kick, over = side-foot kick rewarded), then outcome-based style choice.
- **Power:** current (~2.8 m/s mean, p90 4.6) is too weak. Reach B-Human or more (B-Human long kick ~4.3 m/s 3D in our kick bench). **Air balls are fine** (no loft penalty; count 3D speed).
- **Time to kick:** as short as possible.
- **Re-kick:** if the ball is still within 0.5 m after a kick, keep kicking until it leaves, then stand.
- **Do not compromise the dribble;** improve it if possible (gates: [[dribble-speed-over-slow]]).
- **Later, once these are in place:** train smooth, fast, stable transitions from dribbling into a kick.
- Work one change per run with a regression check against a same-length control.

**Why:** real-match deployment on the K1.
**How to apply:** judge kick runs on 3D speed (mean, p90, ≥ 5 / 7 m/s), time to kick, accuracy, re-kick behaviour, falls, plus the dribble gates.
Related: [[k1-dribble-speed]], [[k1-kick-objectives]], [[benchmark-gated-adoption]].

---
name: dribble-speed-over-slow
description: User accepts some slow-dribble (0.3-0.5 m/s) success loss in exchange for faster dribbling
metadata:
  type: feedback
---
The user (2026-10-21) said: "we can sacrifice slow dribble for fast a bit".

**Why:** match play values speed. Slow-dribble success at 0.3 m/s had fallen 0.49 → 0.34–0.43 as speed rose (v27–v28b), and the strict −0.03 gate was failing otherwise better models.

**How to apply:**
- Relax the slow-dribble success gates (0.3 / 0.5 m/s) in dribble_gate.py to about −0.08 vs v17. Keep 0.8 m/s, falls and posture gates strict.
- "A bit" still means bounded: report the slow numbers and don't let them collapse.
- Also: work one change at a time with a regression check after each (user, same day).

Related: [[k1-dribble-speed]], [[selfplay-run-authority]].

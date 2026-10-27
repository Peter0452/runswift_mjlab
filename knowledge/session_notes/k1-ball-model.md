---
name: k1-ball-model
description: "K1 kick/dribble ball — B-Human's ball is the only ball since 2026-10-28; our old 0.08 m/0.1 kg randomised ball removed"
metadata:
  node_type: memory
  type: project
  originSessionId: a6dd5a47-54bf-4ca8-b1f3-5b4bd2f0370f
  modified: 2026-10-23T08:59:02.481Z
---

**Superseded 2026-10-28:** the user asked to remove our old ball; B-Human's ball is the only ball (`src/k1/common/ball.py`, `knowledge/objectives.md`). The note below is the earlier history.

Decided 2026-10-23. Default ball in runswift_mjlab = ours: 0.08 m / 0.1 kg nominal, randomised radius 0.07–0.13 m and mass 0.05–0.45 kg, shell inertia (every kept model — h022 champion, self-play v1–v16, controller v2, dribble v51 — trained on it). B-Human's ball (0.095 m / 0.29 kg, ±0.01, solid) is opt-in via env var `K1_BALL=bhuman` (read at import in `mdp/approach.py`; used by kick, approach, dribble ball spec and DR).

**User intent:** "in the future we want to use the B-Human ball, not our ball." Plan to retrain lineages on it, then make it the default and re-record `tests/golden/`.

**Why:** the self-play stash merge had silently switched the default to B-Human's ball; the champion dropped (goals 1.19→0.91, long 4.5→3.8 m/s) until restored. The only B-Human-ball run is `k1_kick_stage3_amp/2026-10-16_01-30-01_h022_from_v54c_b`.

**How to apply:** set `K1_BALL=bhuman` for new kick/dribble training aimed at the future ball; keep it unset to reproduce or fine-tune existing models. Related: [[k1-kick-objectives]], [[selfplay-code-in-stash]].

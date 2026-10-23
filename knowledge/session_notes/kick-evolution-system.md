---
name: kick-evolution-system
description: "K1 kick hierarchical evolution (L0-L5), benchmark v2, experience repository; Claude monitors it and logs interventions"
metadata:
  node_type: memory
  type: project
  originSessionId: 03a30a32-4b87-4b76-ade4-979cf900f3dd
  modified: 2026-10-08T09:45:28.012Z
---

Since 2026-10-07 the K1 kick work runs as a system (runswift_mjlab):
- `scripts/tools/evolve_hier.py`: hierarchical loop L0-L5 (contexts + stall-based escalation; L4 = `claude -p` designer, L5 = catalogue atoms with `frame:`), on top of `evolve_kick.py`.
- Judged only by benchmark v2 (`kick_bench2.py`, deployed action path, fixed caps/perception/delay, CIs) through `fitness_v2.py`.
- Experience repository `docs/experience/` (`experience.py`: context, action, result, impact, lesson; objectives section) — every frame recorded; feeds L4 and proposers.
- User asked Claude to **monitor** it, intervene when it regresses the objectives, make changes if needed, and **note every intervention** in `docs/evolution/monitor.md`. Stop cleanly via `docs/evolution/STOP_AFTER_FRAME`.

**Why:** the user wants continuous, objective-aligned improvement with an audit trail.
**How to apply:** on resuming, read `docs/evolution/HANDOFF.md` first (state, runbook, gotchas, pending items; keep its "Current state" updated on every intervention), then monitor.md, hier_report.md and the experience README before acting. Related: [[k1-kick-objectives]], [[benchmark-gated-adoption]].

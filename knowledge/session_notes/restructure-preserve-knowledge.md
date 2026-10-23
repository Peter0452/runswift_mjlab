---
name: restructure-preserve-knowledge
description: "runswift_mjlab restructure (started 2026-10-23) for agent integration — preserve all work and knowledge; archive, never delete"
metadata:
  node_type: memory
  type: project
  originSessionId: a6dd5a47-54bf-4ca8-b1f3-5b4bd2f0370f
  modified: 2026-10-23T05:58:56.598Z
---

User wants runswift_mjlab restructured for better organisation and agentic integration, but must not lose work or earned knowledge.

**Why:** months of K1 kick/dribble/self-play results live in docs, logs, code comments, checkpoints and memory; "unused" tasks can still back curated checkpoints (e.g. BaseWalk, Kick-Approach, Kick-Near back checkpoints/README.md).

**Status 2026-10-23:** Step 1 keep-list at `runswift_mjlab/restructure/KEEP_LIST.md`; data pruned (97 → 26 GB), 74 → 34 K1 tasks on branch `restructure`, snapshot on `archive/pre-restructure-2026-10-23`. User deletes some things themselves (deleted `checkpoints/`, `nubots_models/`, `kick_transition_probe.py`, `artifacts/`); don't restore user deletions. **Step 2 done 2026-10-23:** `runswift_mjlab/knowledge/` (INDEX, objectives, skills/, lessons/, models, sources, session_notes snapshot of this memory); CLAUDE.md points to it. Keep it updated when lessons or best models change; refresh session_notes when memory logs grow. Logs contain symlinked run dirs (aliases across experiments): any tool walking logs/ must skip them. **Pending:** trim the dribble runs (logs since 2026-10-20, kept whole while active) once the user says dribble work is finished: re-run `restructure/best_ckpt.py` then `restructure/inventory.py`, keep latest + best + referenced.

**How to apply:** inventory and approve a keep-list before removing anything; archive (git tag + archive dir) instead of deleting; distil knowledge with links back to raw notes; keep tasks that produced kept checkpoints replayable; add golden tests (checkpoint action snapshots, champion bench) before moving code. Related: [[kick-evolution-system]], [[benchmark-gated-adoption]].

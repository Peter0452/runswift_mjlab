---
name: selfplay-code-in-stash
description: "Oct 12–16 self-play/striker code was stranded in a git stash after the 2026-10-16 \"appex\" pull; restored 2026-10-23 on runswift_mjlab branch `restructure` (69560d3)"
metadata:
  node_type: memory
  type: project
  originSessionId: a6dd5a47-54bf-4ca8-b1f3-5b4bd2f0370f
  modified: 2026-10-23T05:58:53.343Z
---

On 2026-10-16 local self-play/striker work was stashed before pulling tmangs' "appex" commit and never re-applied. Found and restored 2026-10-23: commit 69560d3 on branch `restructure`; the original is kept as branch `archive/selfplay-stash-2026-10-16` (older: `archive/selfplay-stash-2026-10-14`, `archive/stash-2026-10-11a/b`, `archive/stash-2026-10-19`).

Restored: KL anchor wiring (self-play v10–v16), walk_engage / possession_change / territory_progress / ball_race rewards, annealing, opponent DR, striker MemoryResetPPO / memory / switch cost, stage-3 goal_mouth.

**Decided 2026-10-23:** chase caps (lateral 2 m/s, yaw 3 rad/s) everywhere, stage 3 included; test updated.

**Why:** self-play/striker runs can only be reproduced with this code. **How to apply:** if self-play tests fail, check the merge first. Related: [[k1-striker-selfplay]], [[restructure-preserve-knowledge]].

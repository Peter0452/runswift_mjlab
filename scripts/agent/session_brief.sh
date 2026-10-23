#!/usr/bin/env bash
# SessionStart hook: a short live briefing for agents working on the K1 project.
# Prints Claude Code hook JSON whose additionalContext is injected at session start.
# Read-only: it never changes either repository.
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNNER="$(dirname "$REPO")/k1_policy_runner"

line() { printf '%s\n' "$*"; }
git_state() {  # <dir>: branch and number of uncommitted paths
  git -C "$1" rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "not a git repo"; return; }
  echo "branch $(git -C "$1" branch --show-current 2>/dev/null), $(git -C "$1" status --porcelain 2>/dev/null | wc -l) uncommitted"
}
deployed() {  # <start script>: the ONNX it launches
  [ -f "$1" ] && grep -oE '[A-Za-z0-9_./-]+\.onnx' "$1" | head -1 || echo "?"
}

brief="$(
  line "K1 ROBOT SOCCER — every change is aimed at the real robot (Booster K1 via k1_policy_runner)."
  line "Read first: knowledge/INDEX.md · objectives + standing decisions: knowledge/objectives.md (ask before changing them)."
  line "Deploy-first: anything the policy sees or does (obs slots, actions/scales/PD, ball, camera/vision, head tracker,"
  line "  caps, joint/torque clip, delay) must match k1_policy_runner; see knowledge/deployment.md. State it in the commit."
  line "Safety net before and after code changes: tests/golden/README.md (task set, model snapshots, champion bench)."
  line "runswift_mjlab: $(git_state "$REPO")"
  line "k1_policy_runner: $(git_state "$RUNNER") (do not edit it from this repo's work)"
  line "Deployed: kick $(deployed "$RUNNER/start_kick.sh") · dribble $(deployed "$RUNNER/start_dribble.sh")"
  line "Ball default: ${K1_BALL:-ours} (K1_BALL=bhuman opts in to B-Human's ball, the future target)."
)"

jq -n --arg ctx "$brief" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $ctx}}'

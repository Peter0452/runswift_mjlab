#!/usr/bin/env bash
# PostToolUse hook (Write|Edit): when a deployment-critical file is edited, remind
# the agent to keep training and k1_policy_runner consistent. Never blocks.
set -u
f="$(jq -r '.tool_input.file_path // .tool_response.filePath // empty' 2>/dev/null)"
[ -n "$f" ] || exit 0

# What the policy sees or does on the robot. Current layout and the planned k1/ package.
pattern='(tasks/velocity/mdp/(approach|kick_loop|dribble|observations|self_play|striker_skills|decap)\.py'
pattern+='|tasks/velocity/config/k1_amp/env_cfgs\.py|asset_zoo/robots/booster_k1/|envs/mdp/actions/'
pattern+='|export_onnx\.py|/k1/(deploy|robot)/|/k1/common/(vision|ball)\.py|k1_policy_runner/)'
echo "$f" | grep -qE "$pattern" || exit 0

msg="Deployment-critical file edited: $f. If this changes what the policy observes or how actions"
msg+=" become joint targets (slots, scales, PD, ball frame, lost rule, head tracker, caps, clips, delay),"
msg+=" the k1_policy_runner counterpart must match: note it, run the parity check, and say so in the"
msg+=" commit (knowledge/deployment.md). Training-only changes (rewards, DR inside approved ranges) are fine."
jq -n --arg ctx "$msg" '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $ctx}}'

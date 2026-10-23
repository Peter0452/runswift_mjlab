#!/usr/bin/env bash
# Stop a self-play training run and resume a new one from a checkpoint.
# Usage: relaunch_selfplay.sh OLD_PID RUN_NAME LOAD_RUN LOAD_CHECKPOINT
set -e
cd "$(dirname "$0")/../.."
old=$1 name=$2 load_run=$3 ckpt=$4
kill "$old" 2>/dev/null || true
while ps -p "$old" >/dev/null; do sleep 2; done
sleep 5
setsid nohup uv run train Mjlab-Velocity-Kick-SelfPlay-Amp-DA-Muon-Booster-K1 \
  --env.scene.num-envs 4096 --agent.run-name "$name" \
  --agent.resume True --agent.load-run "$load_run" \
  --agent.load-checkpoint "$ckpt" \
  --env.actions.opponent.controller-checkpoint logs/rsl_rl/k1_striker_controller/2026-10-11_19-43-56_controller_v2/model_1750.pt \
  > "logs/launch/$name.log" 2>&1 &
echo "$name launched; log: logs/launch/$name.log"

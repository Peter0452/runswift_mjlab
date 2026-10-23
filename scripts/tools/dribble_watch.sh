#!/usr/bin/env bash
# Evaluate a dribble run's checkpoints every STEP iterations while it trains.
# Usage: dribble_watch.sh RUN_DIR START STEP NAME TRAIN_LOG
# Appends JSON lines to logs/dribble_eval/NAME.jsonl and one summary line per
# checkpoint (plus DEAD / TRACEBACK alerts) to logs/dribble_eval/NAME.watch.
set -u
cd "$(dirname "$0")/../.."
run=$1 it=$2 step=$3 name=$4 tlog=$5
summ=/tmp/claude-1000/-home-peter-Desktop-Project-RL/18ee3867-4055-4a59-a7b5-2a798a71780f/scratchpad/summ.py
out=logs/dribble_eval/$name.watch
while true; do
  it=$((it + step))
  while [ ! -f "$run/model_$it.pt" ]; do
    if grep -q Traceback "$tlog"; then echo "TRACEBACK in $tlog" >> "$out"; exit 1; fi
    if ! pgrep -f "train Mjlab-Velocity-Dribble" > /dev/null; then
      echo "DEAD: training process gone before model_$it" >> "$out"; exit 1
    fi
    sleep 30
  done
  sleep 20
  timeout -k 30 1500 .venv/bin/python scripts/tools/dribble_eval.py "$run/model_$it.pt" \
    --num-envs 1024 --windows 5 --speeds 0.5,0.8,1.0,1.2,1.5 2>/dev/null \
    | grep '^{' | tee -a "logs/dribble_eval/$name.jsonl" \
    | python3 "$summ" "$name/$it" >> "$out"
done

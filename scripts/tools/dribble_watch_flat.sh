#!/usr/bin/env bash
# dribble_watch.sh plus a flat-foot check: every STEP iterations, export the
# checkpoint to ONNX and measure stance and landings in the runner sim.
# Usage: dribble_watch_flat.sh RUN_DIR START STEP NAME TRAIN_LOG TIPTOE_SCRIPT
set -u
cd "$(dirname "$0")/../.."
run=$1 it=$2 step=$3 name=$4 tlog=$5 tiptoe=$6
summ=/tmp/claude-1000/-home-peter-Desktop-Project-RL/18ee3867-4055-4a59-a7b5-2a798a71780f/scratchpad/summ.py
out=logs/dribble_eval/$name.watch
runner=../k1_policy_runner/python-implementation
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
    --num-envs 1024 --windows 5 --speeds 0.3,0.5,0.8,1.0 2>/dev/null \
    | grep '^{' | tee -a "logs/dribble_eval/$name.jsonl" \
    | python3 "$summ" "$name/$it" >> "$out"
  onnx=/tmp/claude-1000/-home-peter-Desktop-Project-RL/18ee3867-4055-4a59-a7b5-2a798a71780f/scratchpad/${name}_$it.onnx
  timeout -k 30 600 .venv/bin/python scripts/tools/export_onnx.py \
    --task Mjlab-Velocity-Dribble-Amp-DA-Muon-Booster-K1 \
    --checkpoint "$run/model_$it.pt" --output "$onnx" > /dev/null 2>&1
  (cd "$runner" && timeout -k 30 600 ../../runswift_mjlab/.venv/bin/python "$tiptoe" \
    "$onnx" 0.5 0 60 2>/dev/null | grep -E "flat stance|centre of pressure" \
    | sed "s|^|$name/$it flat: |") >> "$out"
done

#!/usr/bin/env bash
# Dribble bench watcher (v18+): every STEP iterations run the full bench on the
# new checkpoint and gate it against swa_v17 (dribble_gate.py):
#   deploy-cfg eval, 2 seeds x 0.3-1.5 m/s -> logs/dribble_eval/bench/NAME_IT.jsonl
#   ONNX export -> logs/dribble_eval/bench/onnx/NAME_IT.onnx
#   training <-> runner parity, runner-sim bench (dribble_bench.py)
# Verdicts go to logs/dribble_eval/NAME.watch.
# GPU steps (eval, export, parity) hold logs/dribble_eval/bench/gpu.lock, so two
# watchers never run their benches at once: in parallel they slowed both training
# runs from 4.3 to 11.4 s per iteration.
# Env: SPEEDS (eval speeds, default 0.3-1.5), PROBE_SPEEDS (extra forward runner
# commands for the top-speed probe, not gated), SKILL (non-empty: also run
# dribble_skill_eval.py: approach, search, kick), KICK_PROBE (non-empty: runner-sim
# kick-mode probe).
# Usage: dribble_watch_bench.sh RUN_DIR START STEP NAME TRAIN_LOG
set -u
cd "$(dirname "$0")/../.."
run=$1 it=$2 step=$3 name=$4 tlog=$5
bench=logs/dribble_eval/bench
out=logs/dribble_eval/$name.watch
runner=../k1_policy_runner/python-implementation
py=$PWD/.venv/bin/python
speeds=${SPEEDS:-0.3,0.5,0.8,1.0,1.2,1.5}
probe=${PROBE_SPEEDS:+--probe-speeds $PROBE_SPEEDS}${KICK_PROBE:+ --kick-probe}
run_name=${run##*_dribble_}
mkdir -p "$bench/onnx"
while true; do
  it=$((it + step))
  while [ ! -f "$run/model_$it.pt" ]; do
    if grep -q Traceback "$tlog"; then echo "TRACEBACK in $tlog" >> "$out"; exit 1; fi
    if ! pgrep -f "run-name dribble_$run_name" > /dev/null; then
      echo "DEAD: training process gone before model_$it" >> "$out"; exit 1
    fi
    sleep 30
  done
  sleep 20
  tag=${name}_$it
  exec 9> "$bench/gpu.lock"
  flock 9
  rm -f "$bench/$tag.jsonl"
  for seed in 7 11; do
    timeout -k 30 2400 "$py" scripts/tools/dribble_eval.py "$run/model_$it.pt" \
      --num-envs 1024 --windows 5 --speeds "$speeds" --seed $seed \
      2>/dev/null | grep '^{' | sed "s/^{/{\"seed\": $seed, /" >> "$bench/$tag.jsonl"
  done
  onnx=$PWD/$bench/onnx/$tag.onnx
  timeout -k 30 600 "$py" scripts/tools/export_onnx.py \
    --task Mjlab-Velocity-Dribble-Amp-DA-Muon-Booster-K1 \
    --checkpoint "$run/model_$it.pt" --output "$onnx" > /dev/null 2>&1
  (cd "$runner" && timeout -k 30 900 "$py" dribble_parity_check.py \
    --checkpoint "$OLDPWD/$run/model_$it.pt" --onnx "$onnx" \
    > "$OLDPWD/$bench/$tag.parity" 2>&1)
  if [ -n "${SKILL:-}" ]; then
    timeout -k 30 1800 "$py" scripts/tools/dribble_skill_eval.py "$run/model_$it.pt" \
      --num-envs 512 2>/dev/null | grep '^{' > "$bench/$tag.skill.jsonl"
  fi
  flock -u 9
  (cd "$runner" && timeout -k 30 900 "$py" dribble_bench.py "$onnx" \
    --out ../runs/dribble_bench.jsonl $probe > /dev/null 2>&1)
  { echo "=== $tag $(date +%H:%M)"
    "$py" scripts/tools/dribble_gate.py "$tag" --parity "$bench/$tag.parity"
    [ -s "$bench/$tag.skill.jsonl" ] && sed 's/^/skill: /' "$bench/$tag.skill.jsonl"
  } >> "$out" 2>&1
done

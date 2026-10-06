#!/bin/bash
# Full K1 kick-loop checkpoint eval. usage: scripts/tools/eval_kick_ck.sh RUN_SUFFIX ITER [SEED]
# Waits for the checkpoint, then runs eval_kick_loop.py modes and kick_probes.py.
cd "$(dirname "$0")/../.."
D=$(ls -d logs/rsl_rl/k1_kick_stage3_amp/*_$1); CK=$D/model_$2.pt; SEED=${3:-1}
until [ -f "$CK" ]; do sleep 20; done; sleep 10
F='kicks per episode|on target|time near ball|goals per|fell during'
for mode in "--no-push" "--flat --no-push" "--push-test 0.6" "--moving-ball --no-push"; do
  echo "== $1/$2 seed $SEED $mode"
  uv run python scripts/tools/eval_kick_loop.py --checkpoint "$CK" --num-envs 1024 --seed "$SEED" $mode 2>&1 \
    | grep -E "$F" | sed 's/  */ /g' | tr '\n' '|'; echo
done
for p in range loft search lean caps chase; do
  uv run python scripts/tools/kick_probes.py "$CK" $p 2>&1 | grep -E "^(RANGE|REST|NOMINAL|LOFT|SEARCH|LEAN|CAPS|CHASE|SIDE)|Traceback|Error"
done

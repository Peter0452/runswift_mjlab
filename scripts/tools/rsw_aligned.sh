#!/usr/bin/env bash
# runswift harness on an "aligned" fixture (2026-10-09): the runner scene with
# the training foot mesh as the foot collider (instead of five 1 cm sole
# capsules) and our ball observation from the point between the soles
# (KC_BALL_FEET=1, like training and like B-Human's input), optionally at
# given speed caps. See docs/evolution/monitor.md 2026-10-09.
#
#   rsw_aligned.sh NAME CHECKPOINT|ONNX [CAPS]   e.g. CAPS=2.0,1.5,1.5
#   rsw_aligned.sh bhuman                        (B-Human on the same fixture)
# Results: docs/benchmarks_v2/runswift_aligned/<NAME>_{near,goal}/summary.json
set -e
cd "$(dirname "$0")/../.."
R=$PWD
RL=$(dirname "$R")
A=$R/.cache/rsw_meshfoot
OUT=$R/docs/benchmarks_v2/runswift_aligned
mkdir -p "$OUT"

if [ ! -f "$A/peter-runner/assets/k1_22dof_scene.xml" ]; then
  mkdir -p "$A/peter-runner/assets"
  ln -sfn "$RL/MachineLearning" "$A/bhuman"
  ln -sfn "$R" "$A/peter-training"
  for f in "$RL"/k1_policy_runner/* "$RL"/k1_policy_runner/.[!.]*; do
    b=$(basename "$f"); [ "$b" = assets ] && continue
    ln -sfn "$f" "$A/peter-runner/$b"
  done
  ln -sfn "$RL/k1_policy_runner/assets/meshes" "$A/peter-runner/assets/meshes"
  python3 - "$RL/k1_policy_runner/assets/k1_22dof_scene.xml" "$A/peter-runner/assets/k1_22dof_scene.xml" <<'PY'
import re, sys
s = open(sys.argv[1]).read()
for side, mesh in (("left", "Left_Foot"), ("right", "Right_Foot")):
  pat = re.compile(
    r'(\s*<geom name="%s_foot1_collision".*?\n)(\s*<geom name="%s_foot[2-5]_collision"[^\n]*\n){4}'
    % (side, side)
  )
  m = pat.search(s)
  assert m, side
  s = s[: m.start()] + (
    '\n                  <geom name="%s_foot_collision" class="collision" type="mesh"'
    ' mesh="%s" friction="0.6" condim="3" priority="1"/>\n' % (side, mesh)
  ) + s[m.end():]
open(sys.argv[2], "w").write(s)
PY
fi

NAME=$1
GRID="--grid-file $RL/runswift/benchmarks/results/2026-10-02/k1-score-grid/manifest.json"
EVAL="--evaluator-file $RL/runswift/src/behaviour/examples/booster_match/score_evaluator.py"
cd "$R/.cache/runswift_harness"
if [ "$NAME" = bhuman ]; then
  E="env -u KICK_GENES PYTHONPATH=$PWD"
  POL=bhuman
else
  SRC=$2
  O=$OUT/$NAME.onnx
  case "$SRC" in
    *.onnx) cp "$SRC" "$O" ;;
    *) [ -f "$O" ] || (cd "$R" && uv run python scripts/tools/export_onnx.py --checkpoint "$SRC" --output "$O" >/dev/null) ;;
  esac
  E="env -u KICK_GENES KC_BALL_FEET=1 KC_ONNX=$O PYTHONPATH=$PWD"
  [ -n "$3" ] && E="$E KC_CAPS=$3"
  POL=peter
fi
[ -f "$OUT/${NAME}_near/summary.json" ] || $E "$R/.venv/bin/python" compare.py --policy $POL \
  --suite full --repeats 3 --assets "$A" --ball-profile both --workers 12 --output "$OUT/${NAME}_near" >/dev/null
[ -f "$OUT/${NAME}_goal/summary.json" ] || $E "$R/.venv/bin/python" goal_grid.py --policy $POL \
  --suite grid $GRID $EVAL --assets "$A" --ball-profile both --workers 12 --output "$OUT/${NAME}_goal" >/dev/null
echo "done $NAME -> $OUT"

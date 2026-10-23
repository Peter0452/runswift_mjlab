#!/usr/bin/env bash
# Viewer for a v22+ dribble checkpoint with one behaviour in every window.
# Usage: scripts/tools/play_dribble.sh stop|dribble|kick|mix [CHECKPOINT] [SPEED]
#   stop    stop the ball and stay beside it
#   dribble move the ball at SPEED m/s (default 0.5) in random directions
#   kick    one straight kick within DRIBBLE_PLAY_KICK_DEG (default 30) of the
#           robot-to-ball line, then stand; a new ball appears 1-8 m away
#   mix     the training mix (dribble, stop, kick windows, far and vanishing balls)
# CHECKPOINT defaults to v25 model_5550 (the robot candidate). Its genes are
# read from the run folder's genes.json (the discriminator size depends on them).
set -eu
cd "$(dirname "$0")/../.."
mode=${1:?usage: play_dribble.sh stop|dribble|kick|mix [CHECKPOINT] [SPEED]}
ckpt=${2:-logs/rsl_rl/k1_dribble_amp/2026-10-21_03-20-16_dribble_lightteacher_v25/model_5550.pt}
speed=${3:-0.5}
genes=$(python3 -c "
import json, sys
g = json.load(open(sys.argv[1]))
print(json.dumps({k: v for k, v in g.items() if not k.startswith('kick_teacher') and k not in ('from', 'resume', 'teacher', 'obs')}))
" "$(dirname "$ckpt")/genes.json")
[ "$mode" = mix ] && mode=""
DRIBBLE_GENES="$genes" DRIBBLE_PLAY="$mode" DRIBBLE_PLAY_SPEED="$speed" \
  uv run play Mjlab-Velocity-Dribble-Amp-DA-Muon-Booster-K1 \
  --checkpoint-file "$ckpt" --num-envs 4 --viewer native

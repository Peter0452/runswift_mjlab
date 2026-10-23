#!/usr/bin/env bash
# Stop the plateaued v14 run and launch v15 (action std cap 0.4) from v14/5100.
set -e
cd "$(dirname "$0")/../.."
kill 2845754 2845741 2>/dev/null || true
while ps -p 2845754 >/dev/null; do sleep 2; done
sleep 5
setsid nohup uv run train Mjlab-Velocity-Kick-SelfPlay-Amp-DA-Muon-Booster-K1 \
  --env.scene.num-envs 4096 --agent.run-name p2_kick_v15_std04 \
  --agent.resume True --agent.load-run 2026-10-13_19-43-23_p2_kick_v14_possession \
  --agent.load-checkpoint model_5100.pt \
  --env.actions.opponent.controller-checkpoint logs/rsl_rl/k1_striker_controller/2026-10-11_19-43-56_controller_v2/model_1750.pt \
  > logs/launch/p2_kick_v15_std04.log 2>&1 &
echo "v15 launched; log: logs/launch/p2_kick_v15_std04.log"

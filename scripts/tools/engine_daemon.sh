#!/usr/bin/env bash
# Run the evolution engine unattended: `rsw engine run` for HOURS, restarted
# after a crash (up to MAX_RESTARTS, 5 min apart). It stops for good when the
# engine exits cleanly (deadline, decision packet, budget). Progress:
# experiments/evolution/heartbeat.json; events: experiments/evolution/notify.log.
#
#   scripts/tools/engine_daemon.sh HOURS [engine run flags, e.g. --gpu-hours 20]
#   nohup scripts/tools/engine_daemon.sh 10 --gpu-hours 20 > engine_daemon.log 2>&1 &
set -u
cd "$(dirname "$0")/../.."
hours=${1:?usage: engine_daemon.sh HOURS [flags]}
shift
max_restarts=${MAX_RESTARTS:-3}
end=$(( $(date +%s) + ${hours%.*} * 3600 ))
restarts=0
while :; do
  left=$(( (end - $(date +%s)) / 60 ))
  [ "$left" -le 5 ] && { echo "deadline reached"; exit 0; }
  echo "$(date '+%F %T') engine run for ${left} min"
  .venv/bin/python -m k1.cli engine run --hours "$(echo "scale=2; $left/60" | bc)" --go "$@"
  code=$?
  [ "$code" -eq 0 ] && { echo "engine finished cleanly"; exit 0; }
  restarts=$((restarts + 1))
  echo "$(date '+%F %T') crash: engine exited $code (restart $restarts of $max_restarts)" \
    | tee -a experiments/evolution/notify.log
  [ "$restarts" -gt "$max_restarts" ] && { echo "too many crashes; stopping"; exit 1; }
  sleep 300
done

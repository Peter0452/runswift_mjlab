#!/usr/bin/env bash
# Keeps the hierarchical evolution loop running overnight (2026-10-07).
# Restarts evolve_hier.py if it exits without STOP_AFTER_FRAME / time-out,
# at most 6 times; logs every restart to docs/evolution/monitor.md.
cd "$(dirname "$0")/../.."
END=$(( $(date +%s) + ${1:-36000} ))
n=0
while [ "$(date +%s)" -lt "$END" ] && [ $n -lt 6 ]; do
  left=$(( (END - $(date +%s)) / 3600 ))
  [ "$left" -lt 1 ] && left=1
  .venv/bin/python scripts/tools/evolve_hier.py --hours "$left" >> docs/evolution/hier_console.log 2>&1
  code=$?
  if [ -f docs/evolution/STOP_AFTER_FRAME ] || [ "$(date +%s)" -ge "$END" ]; then
    echo "- $(date '+%Y-%m-%d %H:%M') supervisor: loop stopped (flag or time), not restarting" >> docs/evolution/monitor.md
    break
  fi
  free=$(df --output=avail -BG . | tail -1 | tr -dc 0-9)
  if [ "${free:-0}" -lt 20 ]; then
    echo "- $(date '+%Y-%m-%d %H:%M') supervisor: < 20 GB free disk, not restarting" >> docs/evolution/monitor.md
    break
  fi
  n=$((n + 1))
  echo "- $(date '+%Y-%m-%d %H:%M') supervisor: loop exited (code $code), restart $n/6" >> docs/evolution/monitor.md
  sleep 60
done

#!/usr/bin/env bash
# Relaunches the supervisor for another $2 seconds after supervisor PID $1
# exits, unless docs/evolution/STOP_AFTER_FRAME exists (2026-10-08).
cd "$(dirname "$0")/../.."
while kill -0 "$1" 2>/dev/null; do sleep 60; done
if [ -f docs/evolution/STOP_AFTER_FRAME ]; then
  echo "- $(date '+%Y-%m-%d %H:%M') relaunch watcher: STOP_AFTER_FRAME set, not relaunching" >> docs/evolution/monitor.md
  exit 0
fi
echo "- $(date '+%Y-%m-%d %H:%M') relaunch watcher: supervisor $1 ended, relaunching for ${2}s" >> docs/evolution/monitor.md
nohup bash scripts/tools/hier_supervisor.sh "$2" >/dev/null 2>&1 &

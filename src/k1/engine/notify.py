"""Unattended running: a heartbeat file and notifications.

- ``heartbeat``: ``experiments/evolution/heartbeat.json`` after every engine
  step (time, champion, in flight with stages, GPU hours, last log lines), so a
  watcher (``scripts/tools/engine_daemon.sh``, or a person) sees the loop is alive.
- ``notify``: events worth a person's attention (a new champion, a decision
  packet, a ceiling, the budget, a crash) go to ``notify.log`` and, when a
  desktop session is there, to ``notify-send``. Nothing leaves the machine.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from typing import Any

from k1.engine.state import DIR, State

HEARTBEAT = DIR / "heartbeat.json"
NOTIFY_LOG = DIR / "notify.log"
EVENTS = ("NEW CHAMPION", "escalated:", "ceiling:", "budget:", "reverif", "crash")


def heartbeat(st: State, log: list[str]) -> None:
  HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
  data: dict[str, Any] = {
    "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "pid": os.getpid(),
    "champion": st.champion["recipe"].get("name"),
    "champion_checkpoint": st.champion.get("checkpoint"),
    "in_flight": [f"{c['id']} {c.get('stage')} {c['change']}" for c in st.in_flight],
    "queue": len(st.queue),
    "side_jobs": [f"{j['kind']} {j['for']}" for j in st.side_jobs],
    "gpu_hours": round(st.gpu_hours, 2),
    "non_improving": st.non_improving,
    "ceilings": st.ceilings,
    "last_log": log[-10:],
  }
  tmp = HEARTBEAT.with_suffix(".tmp")
  tmp.write_text(json.dumps(data, indent=1))
  os.replace(tmp, HEARTBEAT)


def notify(lines: list[str]) -> list[str]:
  """Send the event lines; returns the ones sent."""
  events = [m for m in lines if any(e in m for e in EVENTS)]
  if not events:
    return []
  NOTIFY_LOG.parent.mkdir(parents=True, exist_ok=True)
  with open(NOTIFY_LOG, "a") as f:
    for m in events:
      f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {m}\n")
  if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
    exe = shutil.which("notify-send")
    if exe:
      for m in events:
        subprocess.run([exe, "K1 engine", m[:300]], check=False, timeout=10)
  return events

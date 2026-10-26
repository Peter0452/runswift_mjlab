"""The real trainer and judge for the outer loop (``rsw engine``).

The trainer launches ``rsw train RECIPE --go`` as a detached process and keeps
only its pid and log path in the state, so a resumed loop can still poll
children started before a crash. The judge runs each stage (``jobs.py``) as a
detached process too, so judging never holds up training.
"""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from k1.engine.state import DIR


class RsTrainer:
  def __init__(self, log_dir: Path = DIR / "logs", extra: tuple[str, ...] = ()) -> None:
    self.log_dir, self.extra = log_dir, extra

  def start(self, recipe_path: Path, run_id: str, iterations: int) -> dict[str, Any]:
    self.log_dir.mkdir(parents=True, exist_ok=True)
    log = self.log_dir / f"{run_id}.log"
    cmd = [sys.executable, "-m", "k1.cli", "train", str(recipe_path), "--go", "--",
           "--agent.max-iterations", str(iterations), "--agent.run-name", run_id,
           "--agent.logger", "tensorboard", "--agent.upload-model", "False", *self.extra]  # fmt: skip
    with open(log, "w") as f:
      proc = subprocess.Popen(
        cmd, stdout=f, stderr=subprocess.STDOUT, start_new_session=True
      )
    return {"pid": proc.pid, "log": str(log), "iterations": iterations,
            "started": time.time()}  # fmt: skip

  def poll(self, handle: dict[str, Any]) -> tuple[str, str] | None:
    try:
      os.kill(handle["pid"], 0)
      return None  # still running
    except ProcessLookupError:
      pass
    except PermissionError:
      return None
    text = Path(handle["log"]).read_text(errors="replace")
    m = re.search(r"\[k1\] run.json -> (\S+)", text)
    if m is None:
      return ("failed", "no run started: " + " | ".join(text.strip().splitlines()[-3:]))
    run_dir = Path(m[1]).parent
    ckpts = sorted(run_dir.glob("model_*.pt"), key=lambda p: int(p.stem.split("_")[1]))
    if "Traceback" in text or not ckpts:
      return (
        "failed",
        "training crashed: " + " | ".join(text.strip().splitlines()[-3:]),
      )
    return ("done", str(ckpts[-1]))

  def _run_dir(self, handle: dict[str, Any]) -> Path | None:
    try:
      text = Path(handle["log"]).read_text(errors="replace")
    except FileNotFoundError:
      return None
    m = re.search(r"\[k1\] run.json -> (\S+)", text)
    return Path(m[1]).parent if m else None

  def progress(self, handle: dict[str, Any]) -> tuple[float, str] | None:
    """(fraction of the budget done, newest checkpoint) while training."""
    run_dir = self._run_dir(handle)
    if run_dir is None:
      return None
    ckpts = sorted(run_dir.glob("model_*.pt"), key=lambda p: int(p.stem.split("_")[1]))
    if len(ckpts) < 2:
      return None
    first, last = (int(c.stem.split("_")[1]) for c in (ckpts[0], ckpts[-1]))
    return (last - first) / max(1, handle.get("iterations", 1)), str(ckpts[-1])

  def kill(self, handle: dict[str, Any]) -> None:
    """Stop the training's whole process group (started in its own session)."""
    try:
      os.killpg(handle["pid"], signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
      pass


def _alive(pid: int) -> bool:
  try:
    os.kill(pid, 0)
  except ProcessLookupError:
    return False
  except PermissionError:
    return True
  return True


class BackgroundJudge:
  """Runs engine jobs (``python -m k1.engine.jobs``) as detached processes."""

  def __init__(self, job_dir: Path = DIR / "jobs") -> None:
    self.job_dir = job_dir

  def start(self, stage: str, spec: dict[str, Any]) -> dict[str, Any]:
    self.job_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{spec['name']}_{stage}_{int(time.time())}"
    spec_path = self.job_dir / f"{tag}.spec.json"
    out = self.job_dir / f"{tag}.out.json"
    log = self.job_dir / f"{tag}.log"
    spec_path.write_text(json.dumps({**spec, "stage": stage}, indent=1, default=str))
    with open(log, "w") as f:
      proc = subprocess.Popen(
        [sys.executable, "-m", "k1.engine.jobs", str(spec_path), str(out)],
        stdout=f, stderr=subprocess.STDOUT, start_new_session=True,
      )  # fmt: skip
    return {"pid": proc.pid, "out": str(out), "log": str(log), "stage": stage}

  def poll(self, handle: dict[str, Any]) -> dict[str, Any] | None:
    out = Path(handle["out"])
    if out.is_file():
      return json.loads(out.read_text())
    if _alive(handle["pid"]):
      return None
    tail = Path(handle["log"]).read_text(errors="replace").strip().splitlines()[-4:]
    return {"stage": handle["stage"], "ok": False, "hours": 0.0,
            "error": "job died without a result: " + " | ".join(tail)}  # fmt: skip

  def kill(self, handle: dict[str, Any]) -> None:
    try:
      os.killpg(handle["pid"], signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
      pass

"""The real trainer and judge for the outer loop (``rsw evolve``).

The trainer launches ``rsw train RECIPE --go`` as a detached process and keeps
only its pid and log path in the state, so a resumed loop can still poll
children started before a crash.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from k1.eval import judges
from k1.eval.verdict import Verdict
from k1.evolve.state import DIR


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
    return {"pid": proc.pid, "log": str(log)}

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


class BenchJudge:
  def screen(self, task: str, checkpoint: str, name: str) -> Verdict:
    return judges.run(task, checkpoint, name, "quick")

  def confirm(self, task: str, checkpoint: str, name: str) -> Verdict:
    return judges.run(task, checkpoint, name, "full", confirm=True)

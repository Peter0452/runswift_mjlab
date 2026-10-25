"""``run.json``: what a training run is, written into its log directory.

``rsw train`` writes it before training starts; evaluations append their
verdicts later (Step 5). Its ``label`` starts as ``research``; a model becomes
``deployable`` only after the runner parity checks pass (knowledge/deployment.md).
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

from k1.recipes import ROOT, Recipe

LABELS = ("research", "deployable", "deployed")


def _git(*args: str) -> str:
  try:
    return subprocess.run(
      ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
  except (OSError, subprocess.CalledProcessError):
    return ""


def describe(recipe: Recipe, env_cfg: Any, rl_cfg: Any, extra_args: list[str]) -> dict:
  from k1.approaches import detect_all

  return {
    "schema": 1,
    "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "recipe": {
      "name": recipe.name,
      "path": str(recipe.path.relative_to(ROOT)) if recipe.path else None,
      "text": recipe.path.read_text() if recipe.path else None,
    },
    "task": recipe.task,
    "change": recipe.change,
    "why": recipe.why,
    "touches": recipe.touches,
    "control": recipe.control,
    "init": recipe.init,
    "env_vars": recipe.env_vars(),
    "extra_args": extra_args,
    "methods": detect_all(env_cfg, rl_cfg),
    "git": {
      "commit": _git("rev-parse", "HEAD"),
      "dirty": bool(_git("status", "--porcelain")),
    },
    "label": "research",
    "verdicts": [],
  }


def write(log_dir: Path, info: dict) -> Path:
  log_dir.mkdir(parents=True, exist_ok=True)
  path = log_dir / "run.json"
  path.write_text(json.dumps(info, indent=2, sort_keys=False, default=str))
  return path


def read(log_dir: str | Path) -> dict:
  return json.loads((Path(log_dir) / "run.json").read_text())

"""Key models still load and act exactly as recorded (scripts/tools/golden.py)."""

import subprocess
import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "tools"))
import golden  # noqa: E402


@pytest.mark.slow
@pytest.mark.skipif(
  not torch.cuda.is_available(), reason="golden snapshots run on CUDA"
)
@pytest.mark.parametrize("name", [m.name for m in golden.MODELS])
def test_golden_policy(name: str) -> None:
  model = golden.BY_NAME[name]
  if not (ROOT / model.checkpoint).exists():
    pytest.skip(f"checkpoint not on this machine: {model.checkpoint}")
  proc = subprocess.run(
    [sys.executable, str(ROOT / "scripts/tools/golden.py"), "check", name],
    cwd=ROOT,
    capture_output=True,
    text=True,
    timeout=900,
  )
  report = "\n".join(
    line for line in proc.stdout.splitlines() if line.startswith(("GOLDEN", "  "))
  )
  assert proc.returncode == 0, report

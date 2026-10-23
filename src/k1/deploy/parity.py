"""Deploy gate: is an exported model the policy we trained, under the runner contract?

Three checks, all required before a run's label becomes ``deployable``:

1. ONNX metadata vs the contract (``contract.py``, ``obs_layout.py``): joint
   order, PD gains, default pose, action scales (6 decimals), actor inputs, no
   observation history.
2. ONNX vs the trained actor on real observations from the task's env, batch 1
   as on the robot (expected ~4e-6; fails above ``ONNX_TOLERANCE``).
3. Kick family: the lost-ball rule, training env vs the runner's
   ``KickLoopPolicy`` (``scripts/tools/lost_rule_parity.py``; reads
   ``../k1_policy_runner``, never writes it).

``rsw deploy check`` runs them; the result goes into the run's ``run.json``.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from k1.deploy import contract
from k1.deploy.obs_layout import LAYOUTS, Layout

ROOT = Path(__file__).resolve().parents[3]
RUNNER_PY = ROOT.parent / "k1_policy_runner" / "python-implementation"
ONNX_TOLERANCE = 1e-4
KICK_FAMILY = ("kick_loop_v1", "dribble_v1", "selfplay_v1")


def layout_for_task(task: str) -> Layout | None:
  return next((lay for lay in LAYOUTS.values() if lay.task == task), None)


def _floats(text: str) -> list[float]:
  return [float(x) for x in text.split(",")]


def _for_joint(table: dict, joint: str) -> Any:
  return next(v for pattern, v in table.items() if re.fullmatch(pattern, joint))


def check_onnx_metadata(onnx_path: str | Path, layout: Layout | None) -> list[str]:
  """Contract problems in an exported model's metadata (empty when it matches)."""
  import onnx

  model = onnx.load(str(onnx_path))
  meta = {p.key: p.value for p in model.metadata_props}
  problems = []
  joints = tuple(meta.get("joint_names", "").split(","))
  if joints != contract.JOINT_ORDER:
    return [f"joint order {joints} differs from the contract"]
  kp, kd = _floats(meta["joint_stiffness"]), _floats(meta["joint_damping"])
  scale, default = _floats(meta["action_scale"]), _floats(meta["default_joint_pos"])
  for i, j in enumerate(joints):
    want_kp, want_kd = _for_joint(contract.PD_GAINS, j)
    if abs(kp[i] - want_kp) > 1e-6 or abs(kd[i] - want_kd) > 1e-6:
      problems.append(f"PD of {j}: ({kp[i]}, {kd[i]}), contract ({want_kp}, {want_kd})")
    if abs(scale[i] - _for_joint(contract.ACTION_SCALE, j)) > 1e-6:
      problems.append(f"action scale of {j}: {scale[i]}")
    if abs(default[i] - contract.DEFAULT_POSE.get(j, 0.0)) > 1e-6:
      problems.append(f"default pose of {j}: {default[i]}")
  history = _floats(meta.get("observation_terms_history_length", "0"))
  if any(h != 0 for h in history):
    problems.append("observation history in the actor (the runner keeps none)")
  if layout is not None:
    names = meta.get("observation_names", "").split(",")
    if names != [b.term for b in layout.blocks]:
      problems.append(f"actor inputs {names} differ from layout {layout.name}")
    dims = [d.dim_value for d in model.graph.input[0].type.tensor_type.shape.dim]
    if dims != [1, layout.size]:
      problems.append(
        f"input shape {dims}, layout {layout.name} needs [1, {layout.size}]"
      )
  return problems


def onnx_vs_actor(
  task: str, checkpoint: str, onnx_path: str, steps: int = 300
) -> float:
  """Largest |action difference| between the ONNX model and the trained actor
  over ``steps`` env steps of 16 envs (run under the run's env vars)."""
  from dataclasses import asdict

  import numpy as np
  import onnxruntime as ort
  import torch

  import mjlab.tasks  # noqa: F401
  from mjlab.envs import ManagerBasedRlEnv
  from mjlab.rl import RslRlVecEnvWrapper
  from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls

  cfg = load_env_cfg(task)
  cfg.scene.num_envs = 16
  agent = load_rl_cfg(task)
  env = RslRlVecEnvWrapper(
    ManagerBasedRlEnv(cfg=cfg, device="cuda:0"), clip_actions=agent.clip_actions
  )
  runner_cls = load_runner_cls(task)
  assert runner_cls is not None
  runner = runner_cls(env, asdict(agent), device="cuda:0")
  runner.load(checkpoint, load_cfg={"actor": True}, strict=True, map_location="cuda:0")
  policy = runner.get_inference_policy(device="cuda:0")
  sess = ort.InferenceSession(str(onnx_path))
  name = sess.get_inputs()[0].name
  obs, _ = env.reset()
  worst = 0.0
  with torch.inference_mode():
    for _ in range(steps):
      actions = policy(obs)
      a, x = actions.cpu().numpy(), obs["actor"].cpu().numpy().astype(np.float32)
      for i in range(x.shape[0]):
        y = sess.run(None, {name: x[i : i + 1]})[0][0]  # ty: ignore[not-subscriptable]
        worst = max(worst, float(np.abs(y - a[i]).max()))
      obs, *_ = env.step(actions)
  env.close()
  return worst


def export(task: str, checkpoint: str, out: Path) -> None:
  subprocess.run(
    [sys.executable, str(ROOT / "scripts/tools/export_onnx.py"), "--checkpoint",
     checkpoint, "--output", str(out), "--task", task],
    cwd=ROOT, check=True, capture_output=True, text=True,
  )  # fmt: skip


# The lost-rule tool prints statistics and always exits 0; pass when the slots
# agree at the 99th percentile and only the documented edge cases (episode-start
# memory, lost-rule boundaries) differ: the champion h022 has 6 of 1500 steps.
LOST_RULE_P99 = 0.01
LOST_RULE_MISMATCH_SHARE = 0.01


def lost_rule(checkpoint: str, onnx_path: Path) -> tuple[bool, str]:
  if not RUNNER_PY.is_dir():
    return False, f"runner not found at {RUNNER_PY}"
  proc = subprocess.run(
    [sys.executable, str(ROOT / "scripts/tools/lost_rule_parity.py"), checkpoint,
     str(RUNNER_PY), str(onnx_path)],
    cwd=ROOT, capture_output=True, text=True,
  )  # fmt: skip
  line = next((ln for ln in proc.stdout.splitlines() if ln.startswith("PARITY")), "")
  m = re.search(r"steps (\d+),.*p99 ([\d.]+), steps with diff > 0.05: (\d+)", line)
  if proc.returncode != 0 or m is None:
    tail = (proc.stderr or proc.stdout).strip().splitlines()[-3:]
    return False, "lost-rule parity did not run: " + " | ".join(tail)
  steps, p99, mismatched = int(m[1]), float(m[2]), int(m[3])
  ok = p99 <= LOST_RULE_P99 and mismatched <= LOST_RULE_MISMATCH_SHARE * steps
  return ok, line


def gate(task: str, checkpoint: str, out_dir: Path) -> dict:
  """Run every check; ``passed`` is True only when all applicable checks pass."""
  out_dir.mkdir(parents=True, exist_ok=True)
  onnx_path = out_dir / (Path(checkpoint).stem + ".onnx")
  layout = layout_for_task(task)
  result: dict[str, Any] = {
    "task": task,
    "checkpoint": checkpoint,
    "onnx": str(onnx_path),
  }
  export(task, checkpoint, onnx_path)
  result["metadata_problems"] = check_onnx_metadata(onnx_path, layout)
  result["onnx_max_diff"] = onnx_vs_actor(task, checkpoint, str(onnx_path))
  checks = [not result["metadata_problems"], result["onnx_max_diff"] <= ONNX_TOLERANCE]
  if layout is not None and layout.name in KICK_FAMILY[:1]:
    ok, detail = lost_rule(checkpoint, onnx_path)
    result["lost_rule"] = {"passed": ok, "detail": detail}
    checks.append(ok)
  result["layout"] = layout.name if layout else None
  result["passed"] = all(checks) and layout is not None
  return result


def _main(argv: list[str]) -> int:
  import json

  task, checkpoint, out_dir = argv
  print("GATE " + json.dumps(gate(task, checkpoint, Path(out_dir))))
  return 0


if __name__ == "__main__":
  sys.exit(_main(sys.argv[1:]))

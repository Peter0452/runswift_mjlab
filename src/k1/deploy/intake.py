"""The runner's model intake, as code (``k1_policy_runner/docs/rl-development/
model-intake.md``): would the runner team take this ONNX, and what would it take?

It runs the runner's own ``tools/onnx_dump.py`` (read-only) and follows the
numbered steps: identify the policy, shape, metadata completeness, values vs
the joint table, ``obs_layout`` vs the spec, then classifies every difference
and writes the report in the runner's template. Verdicts: ``TAKE``, ``TAKE AS
LEGACY``, ``DO NOT TAKE``. Our deploy gate requires ``TAKE``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from k1.deploy import runner_spec

WIDTH_TO_POLICY = {75: "walk_amp_v1", 83: "kick_loop_v1"}  # model-intake.md step 2
LEGACY_OK = ("policy_id", "spec_version", "obs_dim", "obs_layout")
VALUE_KEYS = {
  "default_joint_pos": "default",
  "action_scale": "action_scale",
  "joint_stiffness": "kp",
  "joint_damping": "kd",
}


def dump(onnx_path: str | Path) -> dict[str, Any]:
  """Parse ``tools/onnx_dump.py`` output: input/output shapes and metadata."""
  tool = runner_spec.RUNNER / "tools" / "onnx_dump.py"
  proc = subprocess.run(
    [sys.executable, str(tool), str(onnx_path)], capture_output=True, text=True
  )
  if proc.returncode != 0:
    raise RuntimeError(f"onnx_dump failed: {proc.stderr.strip()[-300:]}")
  out: dict[str, Any] = {"inputs": [], "outputs": [], "metadata": {}}
  section = None
  for line in proc.stdout.splitlines():
    if line.startswith(("inputs:", "outputs:", "metadata:")):
      section = line.split(":")[0]
      continue
    body = line.strip()
    if section in ("inputs", "outputs") and body:
      name, shape = body.split(" [", 1)
      dims = [int(d) if d.isdigit() else d for d in shape.strip("[]").split(", ")]
      out[section].append((name, dims))
    elif section == "metadata" and ": " in body:
      key, value = body.split(": ", 1)
      if value != "MISSING":
        out["metadata"][key] = value
  return out


def intake(onnx_path: str | Path) -> dict[str, Any]:
  """Classify an ONNX model against the runner's specs; returns verdict,
  policy, differences ``[(item, spec, model, class)]`` and the report text."""
  d = dump(onnx_path)
  meta, diffs = d["metadata"], []

  def diff(item: str, spec: Any, model: Any, cls: str) -> None:
    diffs.append((item, str(spec), str(model), cls))

  width = d["inputs"][0][1][-1] if d["inputs"] else None
  legacy = "policy_id" not in meta
  policy = meta.get("policy_id") or WIDTH_TO_POLICY.get(width)
  spec = runner_spec.policy_spec(policy) if policy else None
  if spec is None:
    diff("policy", "a runner policy spec", policy or f"width {width}", "unacceptable")
  table = runner_spec.joint_table()
  want_width = None
  if spec and spec["obs_layout"]:
    from k1.deploy.obs_layout import parse_spec_layout

    want_width = sum(n for _, n in parse_spec_layout(spec["obs_layout"]))
  if d["inputs"][0][1] != [1, want_width]:
    diff("input shape", [1, want_width], d["inputs"][0][1], "needs retrain")
  if d["outputs"][0][1] != [1, 22]:
    diff("output shape", [1, 22], d["outputs"][0][1], "needs retrain")
  shape_ok = not diffs  # step 4: legacy only when policy and shape match
  for key in runner_spec.required_metadata():
    if key in meta:
      continue
    cls = "legacy" if key in LEGACY_OK and shape_ok else "unacceptable"
    diff(f"metadata {key}", "present", "MISSING", cls)
  names = meta.get("joint_names", "").split(",")
  if names and names != [r["joint"] for r in table]:
    diff("joint_names", "joint table order", names, "unacceptable")
  for key, col in VALUE_KEYS.items():
    if key not in meta:
      continue
    got = [float(x) for x in meta[key].split(",")]
    if len(got) != len(table):
      diff(key, f"{len(table)} values", f"{len(got)} values", "unacceptable")
      continue
    for row, value in zip(table, got, strict=True):
      if abs(value - row[col]) > 1e-6:
        diff(f"{key} {row['joint']}", row[col], value, "needs runner change")
  if spec and "policy_id" in meta:
    if meta.get("spec_version") != str(spec["spec_version"]):
      diff(
        "spec_version", spec["spec_version"], meta.get("spec_version"), "needs retrain"
      )
    if meta.get("obs_layout") != spec["obs_layout"]:
      diff("obs_layout", spec["obs_layout"], meta.get("obs_layout"), "needs retrain")
    if meta.get("obs_dim") != str(width):
      diff("obs_dim", width, meta.get("obs_dim"), "needs retrain")
  classes = {c for *_, c in diffs}
  if classes - {"legacy"}:
    verdict = "DO NOT TAKE"
  elif classes:
    verdict = "TAKE AS LEGACY"
  else:
    verdict = "TAKE"
  claimed = policy if not legacy else f"legacy, inferred {policy} from width {width}"
  lines = [
    f"Model: {onnx_path}",
    f"Claimed policy: {claimed}   Verdict: {verdict}",
    "Differences:",
    "  | item | spec | model | class |",
  ] + [f"  | {i} | {s} | {m} | {c} |" for i, s, m, c in diffs]
  if not diffs:
    lines.append("  (none)")
  return {
    "verdict": verdict,
    "policy": policy,
    "differences": diffs,
    "report": "\n".join(lines),
  }

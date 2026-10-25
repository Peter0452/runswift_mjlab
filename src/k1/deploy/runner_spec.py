"""Read the runner's side of the RL development interface (never write it).

``k1_policy_runner`` (branch ``dev``) owns what a model must look like to run:
``docs/rl-development/interface.md`` (three tiers, required ONNX metadata),
``docs/policies/joint_table.md`` (joint order, default pose, action scale, PD,
limits) and one spec per policy (``docs/policies/<policy_id>.md``: the
``obs_layout`` string and the version history). Our mirror is
``k1/deploy/contract.py`` and ``k1/deploy/obs_layout.py``;
``tests/test_runner_spec.py`` compares the two and fails on any drift.

Run-time constants that give the inputs their meaning (lost-ball rule, ball
memory, head tracker, trained speed ranges) are read from the runner's code
with ``ast``, without importing it.
"""

from __future__ import annotations

import ast
import operator
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
RUNNER = ROOT.parent / "k1_policy_runner"
DOCS = RUNNER / "docs"
KICK_POLICY_PY = "policy_runner/policy_runner/policy/kick_loop_policy.py"


def present() -> bool:
  return (DOCS / "rl-development" / "interface.md").is_file()


def package_dir() -> Path | None:
  """Directory to put on ``sys.path`` so ``import policy_runner`` works:
  ``policy_runner/`` on dev, ``python-implementation/`` on older branches."""
  for d in (RUNNER / "policy_runner", RUNNER / "python-implementation"):
    if (d / "policy_runner" / "__init__.py").is_file():
      return d
  return None


def _num(text: str) -> float:
  return float(text.strip())


def joint_table() -> list[dict[str, Any]]:
  """Rows of ``docs/policies/joint_table.md`` in joint order."""
  rows = []
  for line in (DOCS / "policies" / "joint_table.md").read_text().splitlines():
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) != 8 or not cells[0].isdigit():
      continue
    i, name, default, scale, kp, kd, qmin, qmax = cells
    rows.append(
      {
        "index": int(i),
        "joint": name,
        "default": _num(default),
        "action_scale": _num(scale),
        "kp": _num(kp),
        "kd": _num(kd),
        "q_limits": (_num(qmin), _num(qmax)),
      }
    )
  return rows


def policy_spec(policy_id: str) -> dict[str, Any] | None:
  """``obs_layout`` and the current ``spec_version`` from a policy spec."""
  path = DOCS / "policies" / f"{policy_id}.md"
  if not path.is_file():
    return None
  text = path.read_text()
  m = re.search(r"`obs_layout` metadata for this version:\s*\n`([^`]+)`", text)
  versions = re.findall(rf"`{re.escape(policy_id)}` \(spec_version (\d+)\)", text)
  return {
    "path": str(path),
    "obs_layout": m[1] if m else None,
    "spec_version": max(int(v) for v in versions) if versions else None,
  }


def required_metadata() -> list[str]:
  """Keys of the "Required ONNX metadata" table in the RL development interface."""
  text = (DOCS / "rl-development" / "interface.md").read_text()
  section = text.split("## Required ONNX metadata", 1)[1].split("\n## ", 1)[0]
  return re.findall(r"^\| `([a-z_]+)` \|", section, flags=re.M)


_OPS = {
  ast.Add: operator.add,
  ast.Sub: operator.sub,
  ast.Mult: operator.mul,
  ast.Div: operator.truediv,
}


def _value(node: ast.AST) -> Any:
  if isinstance(node, ast.Constant):
    return node.value
  if isinstance(node, ast.Tuple | ast.List):
    return tuple(_value(e) for e in node.elts)
  if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
    return -_value(node.operand)
  if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
    return _OPS[type(node.op)](_value(node.left), _value(node.right))
  if isinstance(node, ast.Dict):
    return {
      _value(k): _value(v) for k, v in zip(node.keys, node.values, strict=True) if k
    }
  raise ValueError("not a literal")


def constants(rel: str = KICK_POLICY_PY) -> dict[str, Any]:
  """Module-level UPPER_CASE literal constants of a runner source file."""
  tree = ast.parse((RUNNER / rel).read_text())
  out = {}
  for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
      target = node.targets[0]
      if isinstance(target, ast.Name) and target.id.isupper():
        try:
          out[target.id] = _value(node.value)
        except ValueError:
          pass
  return out

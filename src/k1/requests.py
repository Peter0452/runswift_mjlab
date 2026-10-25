"""Task requests: the "what" a requester (the runswift behaviour module or a
person) asks of this repo, and how success is proven.

A request lives in ``tasks/<name>/request.yaml``. The system answers it with
task implementations (recipes in experiments/recipes) and judges them against
the request's requirements with its verification. Once agreed, a request is
frozen: ``frozen`` holds the hash of its interface, requirements and
verification, and nothing in the loop may change them; a change is a new
version. A composite request (``level`` > 0) acts through subtasks: other
requests (``request: NAME``, each a lower level) or deployed policies
(``deployed: PATH``).

    name, version, status, level, requested_by, goal, context
    interface      run-time contract with the behaviour module and the runner
    requirements   [{id, metric, target, priority, source}]; priority 0 = hard
                   safety, 1 = primary, 2 = secondary
    verification   {judge (k1.eval.judges; a list when implementations
                   differ in task), benchmark, promotion, secondary}
    constraints    what the implementation must stay inside (deploy contract...)
    subtasks       {name: {request: NAME} | {deployed: PATH}}
    priors         [{type, ref, note}]: optional inductive bias, tested not trusted
    budget, deliverable, implementations (recipe paths), frozen
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from k1.recipes import RECIPES, ROOT

TASKS = ROOT / "tasks"
STATUSES = ("draft", "agreed", "frozen", "delivered", "retired")
FIELDS = (
  "name", "version", "status", "level", "requested_by", "goal", "context",
  "interface", "requirements", "verification", "constraints", "subtasks",
  "priors", "budget", "deliverable", "implementations", "frozen",
)  # fmt: skip
PRIORITIES = (0, 1, 2)
PRIOR_TYPES = (
  "motion_clips", "teacher", "reward_hint", "constraint", "curriculum",
  "scenario", "warm_start", "approach",
)  # fmt: skip
FROZEN_PARTS = ("interface", "requirements", "verification")


def path_of(name: str) -> Path:
  return TASKS / name / "request.yaml"


def names() -> list[str]:
  return sorted(p.parent.name for p in TASKS.glob("*/request.yaml"))


def load(name: str) -> dict[str, Any]:
  return yaml.safe_load(path_of(name).read_text())


def digest(req: dict[str, Any]) -> str:
  """Hash of the parts a frozen request may not change."""
  part = {k: req[k] for k in FROZEN_PARTS}
  return hashlib.sha256(json.dumps(part, sort_keys=True).encode()).hexdigest()[:16]


def check(name: str) -> list[str]:
  from k1.eval.judges import JUDGES

  try:
    req = load(name)
  except (OSError, yaml.YAMLError) as e:
    return [f"cannot read: {e}"]
  if list(req) != list(FIELDS):
    missing = [f for f in FIELDS if f not in req]
    extra = [f for f in req if f not in FIELDS]
    return [f"fields must be {FIELDS} (missing {missing}, unknown {extra})"]
  problems = []
  if req["name"] != name:
    problems.append(f"name {req['name']!r} differs from the folder")
  if req["status"] not in STATUSES:
    problems.append(f"status must be one of {STATUSES}")
  ids = [r.get("id") for r in req["requirements"]]
  if len(ids) != len(set(ids)):
    problems.append("requirement ids repeat")
  for r in req["requirements"]:
    if set(r) != {"id", "metric", "target", "priority", "source"}:
      problems.append(f"{r.get('id')}: needs id, metric, target, priority, source")
    elif r["priority"] not in PRIORITIES:
      problems.append(f"{r['id']}: priority must be 0, 1 or 2")
  if not any(r.get("priority") == 0 for r in req["requirements"]):
    problems.append("no priority-0 (safety) requirement")
  judge = req["verification"].get("judge")
  wanted = judge if isinstance(judge, list) else [judge]
  judges = {j.name: j for j in JUDGES}
  problems += [f"unknown judge {j!r}" for j in wanted if j not in judges]
  judged = {t for j in wanted if j in judges for t in judges[j].tasks}
  for rel in req["implementations"]:
    recipe = RECIPES / rel
    if not recipe.is_file():
      problems.append(f"implementation {rel} not found")
      continue
    data = yaml.safe_load(recipe.read_text())
    if data["task"] not in judged:
      problems.append(
        f"implementation {rel}: task {data['task']} not judged by {judge}"
      )
    if data.get("request") not in (None, name):
      problems.append(f"implementation {rel} answers request {data['request']!r}")
  for sub, ref in req["subtasks"].items():
    if set(ref) == {"request"}:
      if ref["request"] not in names():
        problems.append(f"subtask {sub}: no request {ref['request']!r}")
      elif load(ref["request"])["level"] >= req["level"]:
        problems.append(f"subtask {sub}: must be a lower level")
    elif set(ref) != {"deployed"}:
      problems.append(f"subtask {sub}: give request: NAME or deployed: PATH")
  if req["level"] > 0 and not req["subtasks"]:
    problems.append("a composite request (level > 0) needs subtasks")
  for p in req["priors"]:
    if p.get("type") not in PRIOR_TYPES:
      problems.append(f"prior {p}: type must be one of {PRIOR_TYPES}")
  if req["status"] in ("frozen", "delivered"):
    if req["frozen"] != digest(req):
      problems.append("frozen parts changed since freezing: make a new version")
    if any(str(r.get("target")).startswith("TBD") for r in req["requirements"]):
      problems.append("a frozen request can't have TBD targets")
  return problems


def freeze(name: str) -> str:
  """Mark an agreed request frozen (the requester's sign-off is the caller's job).
  Only the ``status`` and ``frozen`` lines change, so comments stay."""
  path = path_of(name)
  req = load(name)
  h = digest(req)
  lines = path.read_text().splitlines()
  for i, line in enumerate(lines):
    if line.startswith("status:"):
      lines[i] = "status: frozen"
    elif line.startswith("frozen:"):
      lines[i] = f"frozen: {h}"
  path.write_text("\n".join(lines) + "\n")
  return h


def tree(name: str, indent: str = "") -> list[str]:
  req = load(name)
  lines = [f"{indent}{name} (level {req['level']}, {req['status']})"]
  for sub, ref in req["subtasks"].items():
    if "request" in ref:
      lines += tree(ref["request"], indent + "  ")
    else:
      lines.append(f"{indent}  {sub}: deployed {ref['deployed']}")
  return lines

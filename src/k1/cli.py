"""``rsw``: one interface to the K1 work for people, agents and the evolution loop.

rsw tasks                      registered tasks and the methods each has on
rsw methods [NAME]             method registry, or one method's card
rsw recipe check [PATH ...]    build and verify recipes (default: all)
rsw recipe diff PATH RUN_DIR   compare a recipe with a past run's params
rsw train PATH [--go] [-- ARGS]  train a recipe (dry run without --go); ARGS go
                               to the trainer, e.g. --agent.max-iterations 100
rsw run show RUN_DIR           a run's run.json
rsw check [--bench]            the safety net (tests/golden/README.md)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from k1 import recipes

ROOT = recipes.ROOT


def _tasks(_: argparse.Namespace) -> int:
  import mjlab.tasks  # noqa: F401
  from k1.methods import detect_all
  from mjlab.tasks.registry import list_tasks, load_env_cfg, load_rl_cfg

  for task in list_tasks():
    found = detect_all(load_env_cfg(task), load_rl_cfg(task))
    print(f"{task:62s} {', '.join(found) or '-'}")
  return 0


def _methods(args: argparse.Namespace) -> int:
  from k1.methods import METHODS

  if args.name:
    print(METHODS[args.name].card.read_text())
    return 0
  print(f"{'method':24s} {'status':13s} {'impact':14s} points")
  for m in METHODS.values():
    print(f"{m.name:24s} {m.status:13s} {m.impact:14s} {', '.join(m.points)}")
  return 0


def _recipe_check(args: argparse.Namespace) -> int:
  paths = args.paths or recipes.all_recipes()
  bad = 0
  for path in paths:
    problems = recipes.check(path)
    print(f"{'ok  ' if not problems else 'FAIL'} {path}")
    for p in problems:
      print(f"     {p}")
    bad += bool(problems)
  return 1 if bad else 0


def _recipe_diff(args: argparse.Namespace) -> int:
  out = recipes.diff(args.path, args.run_dir)
  for line in out:
    print(line)
  print("identical" if not out else f"{len(out)} differences")
  return 1 if out else 0


def _train(args: argparse.Namespace) -> int:
  return recipes.train(args.path, args.trainer_args, args.go)


def _run_show(args: argparse.Namespace) -> int:
  print(json.dumps(json.loads((Path(args.run_dir) / "run.json").read_text()), indent=2))
  return 0


def _deploy_check(args: argparse.Namespace) -> int:
  import os
  import tempfile

  from k1 import runs

  env = dict(os.environ)
  task = args.task
  info = None
  if args.run:
    info = runs.read(args.run)
    task = task or info["task"]
    env.update(info.get("env_vars", {}))
  if not task:
    print("give --run RUN_DIR (with run.json) or --task TASK")
    return 2
  out = Path(args.out or tempfile.mkdtemp(prefix="deploy_gate_"))
  proc = subprocess.run(
    [sys.executable, "-m", "k1.deploy.parity", task, str(Path(args.checkpoint).resolve()),
     str(out)],
    cwd=ROOT, env=env, capture_output=True, text=True,
  )  # fmt: skip
  lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("GATE ")]
  if proc.returncode != 0 or not lines:
    print(
      "deploy gate crashed:\n"
      + "\n".join((proc.stderr or proc.stdout).splitlines()[-8:])
    )
    return 1
  result = json.loads(lines[-1][len("GATE ") :])
  print(json.dumps(result, indent=2))
  if info is not None:
    info.setdefault("verdicts", []).append({"kind": "deploy_gate", **result})
    if result["passed"] and info.get("label") == "research":
      info["label"] = "deployable"
    runs.write(Path(args.run), info)
    print(f"run.json updated: label {info['label']}")
  print("deploy gate " + ("PASSED" if result["passed"] else "FAILED"))
  return 0 if result["passed"] else 1


def _judge(args: argparse.Namespace) -> int:
  from k1 import runs
  from k1.eval import judges

  env: dict[str, str] = {}
  task, info = args.task, None
  if args.run:
    info = runs.read(args.run)
    task = task or info["task"]
    env = info.get("env_vars", {})
  if not task:
    print("give --run RUN_DIR (with run.json) or --task TASK")
    return 2
  ckpt = str(Path(args.checkpoint).resolve())
  name = args.name or f"judge_{Path(ckpt).parent.name}_{Path(ckpt).stem}"
  verdict = judges.run(task, ckpt, name, args.size, env)
  print(json.dumps(verdict.to_dict(), indent=2))
  if info is not None:
    info.setdefault("verdicts", []).append(verdict.to_dict())
    runs.write(Path(args.run), info)
    print("verdict appended to run.json")
  return 0 if verdict.status == "scored" else 1


def _check(args: argparse.Namespace) -> int:
  py = sys.executable
  steps = [
    [py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_task_registry.py",
     "tests/test_deploy_obs_layout.py", "tests/test_k1_compat.py",
     "tests/test_k1_methods.py", "-m", "not slow"],
    [py, "scripts/tools/golden.py", "check"],
  ]  # fmt: skip
  if args.bench:
    steps.append([py, "scripts/tools/golden_bench.py", "check"])
  for cmd in steps:
    print("$ " + " ".join(cmd[1:]), flush=True)
    if subprocess.run(cmd, cwd=ROOT).returncode != 0:
      print("safety net FAILED")
      return 1
  print("safety net ok")
  return 0


def main(argv: list[str] | None = None) -> int:
  argv = sys.argv[1:] if argv is None else argv
  trainer_args: list[str] = []
  if "--" in argv:
    i = argv.index("--")
    argv, trainer_args = argv[:i], argv[i + 1 :]
  parser = argparse.ArgumentParser(
    prog="rsw",
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
  )
  sub = parser.add_subparsers(dest="cmd", required=True)
  sub.add_parser("tasks").set_defaults(func=_tasks)
  p = sub.add_parser("methods")
  p.add_argument("name", nargs="?")
  p.set_defaults(func=_methods)
  rec = sub.add_parser("recipe").add_subparsers(dest="recipe_cmd", required=True)
  p = rec.add_parser("check")
  p.add_argument("paths", nargs="*")
  p.set_defaults(func=_recipe_check)
  p = rec.add_parser("diff")
  p.add_argument("path")
  p.add_argument("run_dir")
  p.set_defaults(func=_recipe_diff)
  p = sub.add_parser("train")
  p.add_argument("path")
  p.add_argument("--go", action="store_true", help="actually train (default: dry run)")
  p.set_defaults(func=_train)
  run = sub.add_parser("run").add_subparsers(dest="run_cmd", required=True)
  p = run.add_parser("show")
  p.add_argument("run_dir")
  p.set_defaults(func=_run_show)
  dep = sub.add_parser("deploy").add_subparsers(dest="deploy_cmd", required=True)
  p = dep.add_parser("check")
  p.add_argument("checkpoint")
  p.add_argument("--run", help="run directory with run.json (task and env vars)")
  p.add_argument("--task", help="task id when there is no run.json")
  p.add_argument("--out", help="where to write the ONNX (default: a temp dir)")
  p.set_defaults(func=_deploy_check)
  p = sub.add_parser("judge")
  p.add_argument("checkpoint")
  p.add_argument("--run", help="run directory with run.json (task and env vars)")
  p.add_argument("--task", help="task id when there is no run.json")
  p.add_argument("--size", default="quick", choices=("quick", "full"))
  p.add_argument("--name", help="benchmark result name (docs/benchmarks_v2/NAME.json)")
  p.set_defaults(func=_judge)
  p = sub.add_parser("check")
  p.add_argument("--bench", action="store_true", help="also the champion benchmark")
  p.set_defaults(func=_check)
  args = parser.parse_args(argv)
  args.trainer_args = trainer_args
  return args.func(args)


if __name__ == "__main__":
  sys.exit(main())

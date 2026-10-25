"""``rsw``: one interface to the K1 work for people, agents and the engine.

rsw request list               task requests (tasks/<name>/request.yaml), checked
rsw request check [NAME ...]   schema, judges, implementations, subtasks, frozen hash
rsw request show NAME          a request and its task tree
rsw request freeze NAME --agreed   freeze after the requester's sign-off
rsw approaches [--element E] [ID]  approaches by element (cards, registry, uses),
                               or one approach's card and its uses
rsw knowledge check            approach cards, sources, uses and requests connect
rsw tasks                      registered tasks and the approaches each has on
rsw recipe check [PATH ...]    build and verify recipes (default: all)
rsw recipe diff PATH RUN_DIR   compare a recipe with a past run's params
rsw train PATH [--go] [-- ARGS]  train a recipe (dry run without --go); ARGS go
                               to the trainer, e.g. --agent.max-iterations 100
rsw run show RUN_DIR           a run's run.json
rsw judge CKPT [--run RUN_DIR | --task TASK] [--size quick|full] [--confirm]
                               score a checkpoint on its task's fixed benchmark
                               (default env; --confirm: full, seeds 1 and 2);
                               appends the verdict to run.json
rsw deploy check CKPT [--run RUN_DIR | --task TASK]
                               deploy gate: export, ONNX parity, contract
                               metadata, lost-ball rule; records the result in
                               run.json and labels the run deployable
rsw deploy intake ONNX         the runner's model intake (TAKE / TAKE AS LEGACY /
                               DO NOT TAKE) against its specs on branch dev
rsw engine init RECIPE CKPT    set the outer loop's champion
rsw engine status              champion, children in flight, recent verdicts
rsw engine step [--go]         one outer-loop step (collect, escalate, refill)
rsw engine run --hours H [--go]  repeat steps; trains only with --go
rsw check [--bench]            the safety net (tests/golden/README.md)

Old names still work: ``rsw methods`` = ``rsw approaches``, ``rsw evolve`` =
``rsw engine``.
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
  from k1.approaches import detect_all
  from mjlab.tasks.registry import list_tasks, load_env_cfg, load_rl_cfg

  for task in list_tasks():
    found = detect_all(load_env_cfg(task), load_rl_cfg(task))
    print(f"{task:62s} {', '.join(found) or '-'}")
  return 0


def _approaches(args: argparse.Namespace) -> int:
  from k1.approaches import APPROACHES, ELEMENTS
  from k1.approaches import knowledge as kn

  cards = kn.cards()
  if args.name:
    card = cards.get(args.name)
    if card is None and args.name in APPROACHES:  # a registry name
      card = next(c for c in cards.values() if c.meta["registry"] == args.name)
    if card is None:
      print(f"no approach {args.name!r}")
      return 2
    print(card.path.read_text())
    for u in kn.uses_of(card.id):
      print(f"- {u['id']} [{u['result']}] {u['task']}: {u['finding']}")
    return 0
  n_uses: dict[str, int] = {}
  for u in kn.uses():
    n_uses[u["approach"]] = n_uses.get(u["approach"], 0) + 1
  for element in ELEMENTS:
    if args.element and element != args.element:
      continue
    group = [c for c in cards.values() if c.meta["element"] == element]
    print(f"{element} ({len(group)})")
    for c in group:
      m = c.meta
      code = "code" if m["registry"] else "card"
      print(
        f"  {c.id:28s} {m['status']:13s} {m['impact']:14s} {code}  "
        f"uses {n_uses.get(c.id, 0):2d}  {', '.join(m['tags'])}"
      )
  return 0


def _knowledge_check(_: argparse.Namespace) -> int:
  from k1 import requests
  from k1.approaches import knowledge as kn

  problems = kn.check()
  for name in requests.names():
    problems += [f"tasks/{name}: {p}" for p in requests.check(name)]
  for p in problems:
    print(p)
  print("knowledge ok" if not problems else f"{len(problems)} problems")
  return 1 if problems else 0


def _request(args: argparse.Namespace) -> int:
  from k1 import requests

  if args.request_cmd == "freeze":
    if not args.agreed:
      print("freeze needs --agreed: the requester signed off the requirements")
      return 2
    problems = requests.check(args.name)
    if problems:
      print("\n".join(problems))
      return 1
    print(f"{args.name} frozen at {requests.freeze(args.name)}")
    return 0
  if args.request_cmd == "show":
    print(requests.path_of(args.name).read_text())
    print("\n".join(requests.tree(args.name)))
    return 0
  names = getattr(args, "names", None) or requests.names()
  bad = 0
  for name in names:
    problems = requests.check(name)
    req = requests.load(name) if requests.path_of(name).is_file() else {}
    head = f"{name:12s} level {req.get('level', '?')}  {req.get('status', '?'):9s}"
    print(f"{'ok  ' if not problems else 'FAIL'} {head}")
    for p in problems:
      print(f"     {p}")
    bad += bool(problems)
  return 1 if bad else 0


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


def _deploy_intake(args: argparse.Namespace) -> int:
  from k1.deploy import intake, runner_spec

  if not runner_spec.present():
    print(f"runner docs not found under {runner_spec.RUNNER}")
    return 2
  report = intake.intake(args.onnx)
  print(report["report"])
  return 0 if report["verdict"] == "TAKE" else 1


def _judge(args: argparse.Namespace) -> int:
  from k1 import runs
  from k1.eval import judges

  task, info = args.task, None
  if args.run:
    info = runs.read(args.run)
    task = task or info["task"]
  if not task:
    print("give --run RUN_DIR (with run.json) or --task TASK")
    return 2
  ckpt = str(Path(args.checkpoint).resolve())
  name = args.name or f"judge_{Path(ckpt).parent.name}_{Path(ckpt).stem}"
  verdict = judges.run(task, ckpt, name, args.size, confirm=args.confirm)
  print(json.dumps(verdict.to_dict(), indent=2))
  if info is not None:
    info.setdefault("verdicts", []).append(verdict.to_dict())
    runs.write(Path(args.run), info)
    print("verdict appended to run.json")
  return 0 if verdict.status == "scored" else 1


# Outer-loop defaults (best guesses, restructure/STEP5_LOG.md): two deterministic
# designers on the kick champion's recipe; no LLM front-end.
EVOLVE_GENES = {
  "w.kick_direction": (300.0, 2000.0),
  "w.kick_vel": (300.0, 2000.0),
  "w.long_kick_power": (1000.0, 8000.0),
  "w.walk_speed_track": (1.0, 12.0),
  "w.action_rate_l2": (-0.4, -0.05),
}
EVOLVE_METHODS = {"caps": {"temporal": 1.5}, "decap": {"source": "kick"}}


def _engine(args: argparse.Namespace) -> int:
  import random
  import time

  import yaml

  from k1.engine import outer, state
  from k1.engine.designers import GeneDesigner, MethodDesigner

  path = state.DIR / "state.json"
  if args.engine_cmd == "init":
    recipe = yaml.safe_load(Path(args.recipe).read_text())
    ckpt = str(Path(args.checkpoint).resolve())
    champ = {"recipe": recipe, "checkpoint": ckpt, "verdict": None}
    state.save(state.State(champion=champ), path)
    print(f"champion set: {recipe['name']} @ {ckpt}")
    return 0
  if not path.is_file():
    print("no loop state: rsw engine init RECIPE CKPT first")
    return 2
  st = state.load(path)
  if args.engine_cmd == "status":
    print(
      f"champion: {st.champion['recipe'].get('name')} @ {st.champion.get('checkpoint')}"
    )
    print(f"in flight: {[c['id'] + ' ' + c['change'] for c in st.in_flight]}")
    print(f"non-improving in a row: {st.non_improving}")
    for h in st.history[-10:]:
      v = h["verdict"]
      print(
        f"  {h['id']} {h['designer']:7s} {v['status']:13s} {v['score']} {h['change']}"
      )
    return 0
  if not args.go:
    print(
      "dry run: add --go to let the loop train (one or two GPU trainings at a time)"
    )
    return 0
  from k1.engine.real import BenchJudge, RsTrainer

  designers = [GeneDesigner(EVOLVE_GENES), MethodDesigner(EVOLVE_METHODS)]
  cfg = outer.Config()
  rng = random.Random(st.counter)
  deadline = time.time() + 3600 * (args.hours if args.engine_cmd == "run" else 0)
  with state.single_writer(path):
    while True:
      for line in outer.step(
        st, cfg, designers, RsTrainer(), BenchJudge(), rng, state.DIR
      ):
        print(line, flush=True)
      state.save(st, path)
      if args.engine_cmd == "step" or time.time() > deadline:
        return 0
      if st.non_improving >= cfg.escalate_after and not st.in_flight:
        return 0
      time.sleep(60)


def _check(args: argparse.Namespace) -> int:
  py = sys.executable
  steps = [
    [py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_task_registry.py",
     "tests/test_deploy_obs_layout.py", "tests/test_k1_compat.py",
     "tests/test_k1_approaches.py", "tests/test_k1_requests.py",
     "tests/test_runner_spec.py", "tests/test_deploy_contract.py", "-m", "not slow"],
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
  for name in ("approaches", "methods"):
    p = sub.add_parser(name)
    p.add_argument("name", nargs="?")
    p.add_argument("--element", help="only this element")
    p.set_defaults(func=_approaches)
  kn = sub.add_parser("knowledge").add_subparsers(dest="knowledge_cmd", required=True)
  kn.add_parser("check").set_defaults(func=_knowledge_check)
  req = sub.add_parser("request").add_subparsers(dest="request_cmd", required=True)
  req.add_parser("list").set_defaults(func=_request)
  p = req.add_parser("check")
  p.add_argument("names", nargs="*")
  p.set_defaults(func=_request)
  p = req.add_parser("show")
  p.add_argument("name")
  p.set_defaults(func=_request)
  p = req.add_parser("freeze")
  p.add_argument("name")
  p.add_argument("--agreed", action="store_true", help="the requester signed off")
  p.set_defaults(func=_request)
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
  p = dep.add_parser("intake")
  p.add_argument("onnx")
  p.set_defaults(func=_deploy_intake)
  p = sub.add_parser("judge")
  p.add_argument("checkpoint")
  p.add_argument("--run", help="run directory with run.json (task and env vars)")
  p.add_argument("--task", help="task id when there is no run.json")
  p.add_argument("--size", default="quick", choices=("quick", "full"))
  p.add_argument("--name", help="benchmark result name (docs/benchmarks_v2/NAME.json)")
  p.add_argument(
    "--confirm", action="store_true", help="full benchmark, seeds 1 and 2 (promotion)"
  )
  p.set_defaults(func=_judge)
  for cmd in ("engine", "evolve"):
    eng = sub.add_parser(cmd).add_subparsers(dest="engine_cmd", required=True)
    p = eng.add_parser("init")
    p.add_argument("recipe")
    p.add_argument("checkpoint")
    p.set_defaults(func=_engine)
    eng.add_parser("status").set_defaults(func=_engine)
    for name in ("step", "run"):
      p = eng.add_parser(name)
      p.add_argument(
        "--go", action="store_true", help="actually train (default: dry run)"
      )
      if name == "run":
        p.add_argument("--hours", type=float, required=True)
      p.set_defaults(func=_engine)
  p = sub.add_parser("check")
  p.add_argument("--bench", action="store_true", help="also the champion benchmark")
  p.set_defaults(func=_check)
  args = parser.parse_args(argv)
  args.trainer_args = trainer_args
  return args.func(args)


if __name__ == "__main__":
  sys.exit(main())

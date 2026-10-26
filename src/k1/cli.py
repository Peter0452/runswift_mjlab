"""``rsw``: one interface to the K1 work for people, agents and the engine.

rsw design context [--task kick]   the LLM designer's context: request, champion,
                               gaps, history, approaches, rules, proposal schema
rsw design check [FILE ...]    validate candidate proposals (default: the inbox)
rsw design inbox               proposals waiting, used, rejected, to build
rsw request list               task requests (tasks/<name>/request.yaml), checked
rsw request check [NAME ...]   schema, judges, implementations, subtasks, frozen hash
rsw request show NAME          a request and its task tree
rsw request freeze NAME --agreed   freeze after the requester's sign-off
rsw approaches [--element E] [ID]  approaches by element (cards, registry, uses),
                               or one approach's card and its uses
rsw knowledge check            approach cards, sources, uses and requests connect
rsw review gaps [--task kick]  the champion's measured gaps, what the engine would
                               try for them, and what it can't apply
rsw review new TOPIC [--task kick] [--trigger TEXT]
                               start a literature review from the gaps
rsw review approve NAME --agreed   let the engine use a review's shortlist
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
rsw engine step [--go]         one outer-loop step (collect, escalate, refill);
                               trains only inbox proposals worth a run, asking
                               the LLM designer (claude -p /design) when empty
rsw engine run --hours H [--go]  repeat steps; trains only with --go
                               (--min-gain G, --no-llm, --fallback)
rsw design context|check|inbox the LLM designer's context, proposal check
                               (with expected gain), inbox state
rsw design ask [--n N]         run /design headless now (writes proposals only)
rsw rsjudge CKPT --name N      runswift-spec kick benchmark, lab + deployed,
                               paired vs B-Human and the champion (95 % CI)
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


def _engine_champion() -> tuple[dict, list]:
  import yaml

  from k1.engine import state

  if (state.DIR / "state.json").is_file():
    st = state.load(state.DIR / "state.json")
    return st.champion, st.history + [{"change": c["change"]} for c in st.in_flight]
  recipe = yaml.safe_load(
    (recipes.RECIPES / "kick" / "kick_stage3_h022.yaml").read_text()
  )
  return {"recipe": recipe, "checkpoint": None}, []


def _design(args: argparse.Namespace) -> int:
  import yaml

  from k1.engine import design, worth

  champion, history = _engine_champion()
  ceilings = design._ceilings()
  factor = worth.calibration([h for h in history if "verdict" in h])
  if args.design_cmd == "context":
    text = design.context(champion, history, args.task)
    out = design.PROPOSALS / "context.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(text)
    print(f"(saved to {out.relative_to(ROOT)})")
    return 0
  if args.design_cmd == "inbox":
    for d in (design.INBOX, design.USED, design.REJECTED, design.BUILD):
      files = sorted(d.glob("*.yaml")) if d.is_dir() else []
      print(f"{d.name:9s} {len(files):3d}  {' '.join(f.name for f in files[-8:])}")
    return 0
  if args.design_cmd == "ask":
    print(design.ask_llm(args.n, args.task))
    return 0
  paths = [Path(p) for p in args.files] or design.inbox()
  bad = 0
  for path in paths:
    try:
      p = yaml.safe_load(path.read_text()) or {}
      problems = design.check(p, champion, history, ceilings=ceilings, factor=factor)
    except (OSError, yaml.YAMLError) as e:
      problems = [str(e)]
    print(f"{'ok  ' if not problems else 'FAIL'} {path}")
    for msg in problems:
      print(f"     {msg}")
    if not problems and p.get("kind") != "new":
      print(f"     change: {design.change_text(p, champion['recipe'])}")
    if p.get("kind") != "new" and isinstance(p.get("expect"), dict | list):
      est = design.estimate(p)
      for line in [f"expected gain {est.gain:+.1f}", *est.effects]:
        print(f"     {line}")
    bad += bool(problems)
  return 1 if bad else 0


def _review(args: argparse.Namespace) -> int:
  import random

  from k1.approaches import review

  if args.review_cmd == "approve":
    if not args.agreed:
      print("approve needs --agreed: the requester signed off the shortlist")
      return 2
    print(f"approved: {review.approve(args.name)}")
    return 0
  if args.review_cmd == "new":
    path = review.new(args.topic, args.task, args.trigger)
    print(f"review started: {path}")
    print("next: research it (.claude/commands/review.md), fill the shortlist, then")
    print(f"      rsw knowledge check; rsw review approve {path.stem} --agreed")
    return 0
  import yaml

  from k1.engine.designers.approach import ApproachDesigner

  gaps = review.gaps_for(args.task, args.top)
  print(f"{args.task} champion gaps (benchmark v2 full, seed 1):")
  for g in gaps:
    print(f"  {g.weight:5.1f}  {g.describe()}  [{', '.join(g.tags)}]")
  from k1.engine import state

  if (state.DIR / "state.json").is_file():  # the engine's champion
    champ = state.load(state.DIR / "state.json").champion
  else:
    recipe_path = recipes.RECIPES / "kick" / "kick_stage3_h022.yaml"
    champ = {"recipe": yaml.safe_load(recipe_path.read_text())}
  designer = ApproachDesigner(args.task, lambda c: gaps)
  print("\nthe approach designer would try, in order:")
  history: list[dict] = []
  for _ in range(args.top):
    props = designer.propose(champ, history, random.Random(0))
    if not props:
      break
    print(f"  {props[0].change}\n      hypothesis: {props[0].hypothesis}")
    history.append({"change": props[0].change})
  print(f"\nmatching but not applicable by the engine: {', '.join(designer.blocked)}")
  return 0


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


def _rsjudge(args: argparse.Namespace) -> int:
  from k1.eval import rs_judge

  v = rs_judge.run(str(Path(args.checkpoint).resolve()), args.name, tuple(args.seeds))
  print(json.dumps(v.to_dict(), indent=2))
  return 0


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


# Outer-loop defaults (best guesses, restructure/STEP5_LOG.md, STEP8_LOG.md):
# the approach designer (gaps -> approaches from knowledge/) and one-gene steps
# on the kick champion's recipe; no LLM front-end.
EVOLVE_GENES = {
  "w.kick_direction": (300.0, 2000.0),
  "w.kick_vel": (300.0, 2000.0),
  "w.long_kick_power": (1000.0, 8000.0),
  "w.walk_speed_track": (1.0, 12.0),
  "w.action_rate_l2": (-0.4, -0.05),
}


def _champion_gaps(champion: dict):
  """Gaps of the engine's champion: its own confirmed benchmark when it has
  one, else the task's reference benchmark."""
  from k1.engine.gaps import champion_gaps

  bench = ((champion.get("verdict") or {}).get("metrics") or {}).get("bench")
  if isinstance(bench, list):
    bench = bench[0]
  return champion_gaps(champion["recipe"]["task"], bench)


def _engine(args: argparse.Namespace) -> int:
  import random
  import time

  import yaml

  from k1.engine import outer, state
  from k1.engine.designers import GeneDesigner
  from k1.engine.designers.approach import ApproachDesigner
  from k1.engine.designers.llm import InboxDesigner

  path = state.DIR / "state.json"
  if args.engine_cmd == "init":
    recipe = yaml.safe_load(Path(args.recipe).read_text())
    from k1.eval import scorecard

    ckpt = str(Path(args.checkpoint).resolve())
    champ = {"recipe": recipe, "checkpoint": ckpt, "verdict": None,
             "refs": scorecard.default_refs()}  # fmt: skip
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
    print("in flight: " + str([f"{c['id']} {c.get('stage')} {c['change']}"
                               for c in st.in_flight]))  # fmt: skip
    print(f"queued doses: {len(st.queue)}; side jobs: "
          f"{[j['kind'] + ' ' + j['for'] for j in st.side_jobs]}")  # fmt: skip
    print(f"GPU hours spent: {st.gpu_hours:.1f}; ceilings: {st.ceilings or 'none'}")
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
  from k1.engine import design, notify
  from k1.engine.real import BackgroundJudge, RsTrainer
  from k1.eval import scorecard

  if not st.champion.get("refs"):
    st.champion["refs"] = scorecard.default_refs()

  # The LLM designer: proposals in the inbox (written by /design, or by the
  # engine calling it headless when the inbox is empty), the one with the
  # highest expected gain first; nothing trains unless it is worth a run. The
  # deterministic designers (no forecast, no worth gate) only with --fallback.
  designers: list = [
    InboxDesigner(
      gaps=_champion_gaps,
      min_gain=args.min_gain,
      ask=None if args.no_llm else design.ask_llm,
    )
  ]
  if args.fallback:
    designers += [ApproachDesigner("kick", _champion_gaps), GeneDesigner(EVOLVE_GENES)]
  cfg = outer.Config(
    budget_iterations=args.iterations,
    smoke=not args.no_smoke,
    gpu_hours=args.gpu_hours,
  )
  rng = random.Random(st.counter)
  deadline = time.time() + 3600 * (args.hours if args.engine_cmd == "run" else 0)
  with state.single_writer(path):
    while True:
      try:
        log = outer.step(st, cfg, designers, RsTrainer(), BackgroundJudge(), rng,
                         state.DIR)  # fmt: skip
      except Exception as e:
        state.save(st, path)
        notify.notify([f"crash: engine step raised {e!r}"])
        raise
      for line in log:
        print(line, flush=True)
      state.save(st, path)
      notify.heartbeat(st, log)
      notify.notify(log)
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
  des = sub.add_parser("design").add_subparsers(dest="design_cmd", required=True)
  p = des.add_parser("context")
  p.add_argument("--task", default="kick")
  p.set_defaults(func=_design)
  p = des.add_parser("check")
  p.add_argument("files", nargs="*")
  p.set_defaults(func=_design)
  des.add_parser("inbox").set_defaults(func=_design)
  p = des.add_parser("ask")
  p.add_argument("--n", type=int, default=3)
  p.add_argument("--task", default="kick")
  p.set_defaults(func=_design)
  rev = sub.add_parser("review").add_subparsers(dest="review_cmd", required=True)
  p = rev.add_parser("gaps")
  p.add_argument("--task", default="kick")
  p.add_argument("--top", type=int, default=8)
  p.set_defaults(func=_review)
  p = rev.add_parser("new")
  p.add_argument("topic")
  p.add_argument("--task", default="kick")
  p.add_argument("--trigger", default="requested by a person")
  p.set_defaults(func=_review)
  p = rev.add_parser("approve")
  p.add_argument("name")
  p.add_argument("--agreed", action="store_true", help="the requester signed off")
  p.set_defaults(func=_review)
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
      p.add_argument(
        "--min-gain",
        type=float,
        default=4.0,
        help="expected benchmark gain a proposal needs to train",
      )
      p.add_argument(
        "--no-llm",
        action="store_true",
        help="don't call the LLM designer headless (inbox only)",
      )
      p.add_argument(
        "--fallback",
        action="store_true",
        help="also the deterministic designers (no worth gate)",
      )
      p.add_argument("--iterations", type=int, default=500,
                     help="training iterations per child")  # fmt: skip
      p.add_argument("--gpu-hours", type=float, default=None,
                     help="stop starting children beyond this spend")  # fmt: skip
      p.add_argument("--no-smoke", action="store_true",
                     help="skip the few-iteration smoke training before each child")  # fmt: skip
      p.set_defaults(func=_engine)  # fmt: skip
  p = sub.add_parser("rsjudge")
  p.add_argument("checkpoint")
  p.add_argument("--name", required=True)
  p.add_argument("--seeds", type=int, nargs="+", default=[0, 1])
  p.set_defaults(func=_rsjudge)
  p = sub.add_parser("check")
  p.add_argument("--bench", action="store_true", help="also the champion benchmark")
  p.set_defaults(func=_check)
  args = parser.parse_args(argv)
  args.trainer_args = trainer_args
  return args.func(args)


if __name__ == "__main__":
  sys.exit(main())

"""The LLM designer's interface: context in, checked candidate proposals out.

The designer is an LLM agent (Claude Code, ``/design``) with tools and skills:
``rsw review gaps``, ``rsw approaches``, ``/review``, the knowledge files and
``rsw design check``. This module gives it

1. **context** (``rsw design context``): one document with everything a
   proposal must respect:
   - the task request
   - the champion's recipe and measured gaps
   - the engine history (what was tried, verdicts, hypotheses)
   - the approach knowledge (runnable, tunable, blocked, rejected)
   - approved shortlists
   - the deterministic designer's ranked moves (as suggestions)
   - the rules and the proposal schema
2. **the proposal schema** and **check** (``rsw design check``): a candidate
   is valid only if every edit is on the recipe surface (a registered
   approach's parameters, genes, reward weights), names known approaches, stays
   inside the knowledge's tune ranges (or says why not), keeps one change per
   run, isn't a repeat, is training-only, and is worth a kick retrain: its
   forecast (``expect``) must be detectable and reach the minimum expected
   benchmark gain (``k1/engine/worth.py``);
3. **the inbox** (``experiments/evolution/proposals/inbox/*.yaml``): valid
   proposals wait there; the engine's ``InboxDesigner`` turns them into
   children, and later layers implement them (recipe check → train → judge).
   ``kind: new`` proposals (an approach that needs building) are never
   trained; they wait in ``proposals/build/`` for a person.
"""

from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import yaml

from k1 import recipes
from k1.approaches import APPROACHES, knowledge
from k1.engine import worth
from k1.engine.designers import Proposal
from k1.engine.designers.approach import ApproachDesigner, _get
from k1.engine.gaps import Gap, champion_gaps
from k1.engine.state import DIR

PROPOSALS = DIR / "proposals"
INBOX, USED, REJECTED, BUILD = (
  PROPOSALS / d for d in ("inbox", "used", "rejected", "build")
)
KINDS = ("add", "tune", "combine", "new")
REQUIRED = ("designer", "task", "kind", "approaches", "edits", "gap", "hypothesis",
            "expect", "why")  # fmt: skip
OPTIONAL = ("evidence", "touches", "out_of_range_reason", "retry_reason", "name",
            "parent", "doses")  # fmt: skip
FAMILY_TASK = {"kick": "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"}

SCHEMA = """\
designer: claude               # who wrote it
task: kick                     # task request (tasks/<task>/request.yaml)
kind: add                      # add | tune | combine | new (new = needs building, never trained)
approaches: [ball_behind_starts]   # card ids in knowledge/approaches/
edits:                         # recipe paths -> values (empty for kind new)
  genes.s.far_spawn_prob: 0.3            # genes.<gene>
  # methods.caps: {temporal: 1.2}        # methods.<registry name>: {params} (turn on/merge)
  # methods.caps.temporal: 1.2           # methods.<registry name>.<param>
  # methods.decap: false                 # turn off
  # rewards.ball_avoidance: -3.0         # rewards.<term>: weight
gap: "fall_pct in approach/behind/world/typical"   # the measured gap it targets
hypothesis: "more ball-behind spawns cut behind falls below 15 % with no regression"
expect:                        # forecast, judged before anything trains (worth a run?)
  - {metric: fall_pct, situation: approach/behind/world/typical, direction: lower,
     by: 8.0, p: 0.5}            # main effect: metric units; p = chance it happens
  - {metric: fall_pct_behind, situation: approach/camera/typical, direction: lower,
     by: 3.0, p: 0.4, caps: [high]}   # side effects count too; caps default: where the gap is
  # rs_kick metrics too: situation rs_kick/deployed | rs_kick/lab, metric score |
  # power_small | power_medium | power_strong (power by kick class, 0-1)
why: "reasoning, with the evidence it rests on"
evidence: [u017, humanoid_soccer]  # use ids, source ids, review names (optional)
# parent: e0007        # continue from that engine child (its checkpoint and recipe)
#                      # instead of the champion, e.g. to fix the regression that
#                      # blocked it; fixing a parent's regression earns its gain
# doses: {genes.s.far_spawn_prob: [0.2, 0.4]}   # other strengths of the one edit,
#                      # trained as siblings (the edit's value is the first dose)
# out_of_range_reason: "..."       # needed when a value leaves a card's tune range
# retry_reason: "..."              # needed to retry a rejected approach
"""

RULES = """\
- One change per run (standing decision 2026-10-21): one approach per proposal
  (`kind: combine` only when the engine allows bundles; it doesn't by default).
- Training-only: no observation, action, PD, caps or clip changes (deploy
  contract; those need a new runner policy version and the user's OK).
- Stay inside a card's `tune` range unless `out_of_range_reason` explains why.
- Rejected approaches need `retry_reason`; parked ones are off limits.
- Never repeat a change in the history; prefer approaches not tried yet.
- Every proposal names the gap it targets and a falsifiable hypothesis with the
  metric, situation and direction; judge by the benchmark, not the reward.
- Worth a run: a child costs ~2.7 GPU-hours; the benchmark sees a metric move
  only beyond its tolerance (seed noise). `expect` lists the forecast effects (metric,
  situation, by in metric units, p); the main (first) effect must move its
  metric by >= 1 fitness tolerance, and the expected gain
  (sum of p x min(by/tol, 3) x weight x caps) must reach the engine's minimum
  (default 4). Be honest with p: forecasts are compared with verdicts later.
  Trivial nudges (a 25 % weight step on a small gap) usually don't qualify;
  aim for changes with a mechanism that can move a big gap.
- Objectives and standing decisions: knowledge/objectives.md (ask before
  changing any); DR, latency and limits stay as inherited from the AMP walk.
- Learn from the verdicts: read each recent child's scorecard parts, probes and
  training curves below before proposing. A gap at a ceiling is closed to
  training-only proposals (only `kind: new` or a person can address it).
- Forecasts are calibrated: the engine multiplies expected gains by measured /
  forecast so far (shown below), so honest p and by values pay off.
"""


def apply_edits(recipe: dict[str, Any], edits: dict[str, Any]) -> dict[str, Any]:
  out = json.loads(json.dumps(recipe))
  for path, value in edits.items():
    kind, rest = path.split(".", 1)
    if kind == "genes":
      out.setdefault("genes", {})[rest] = value
    elif kind == "rewards":
      out.setdefault("rewards", {})[rest] = value
    else:
      name, _, param = rest.partition(".")
      methods = out.setdefault("methods", {})
      entry = methods.get(name)
      base = entry if isinstance(entry, dict) else {}
      if param:
        methods[name] = {**base, param: value}
      elif value is False:
        methods[name] = False
      else:
        methods[name] = {**base, **value}
  return out


def change_text(p: dict[str, Any], recipe: dict[str, Any]) -> str:
  parts = [f"{k}: {_value(recipe, k)!r} -> {v!r}" for k, v in p["edits"].items()]
  return f"{p['kind']} {'+'.join(p['approaches'])}: " + "; ".join(parts)


def _value(recipe: dict[str, Any], path: str) -> Any:
  if path.startswith("rewards."):
    return (recipe.get("rewards") or {}).get(path.split(".", 1)[1])
  return _get(recipe, path)


def _parent_entry(p: dict[str, Any], history: list[dict[str, Any]]) -> dict | None:
  if p.get("parent") is None:
    return None
  return next((h for h in history if h.get("id") == p["parent"]), None)


def base_recipe(
  p: dict[str, Any], champion: dict[str, Any], history: list[dict[str, Any]]
) -> tuple[dict[str, Any], str | None]:
  """The recipe a proposal edits and the checkpoint it starts from: the
  champion's, or its parent child's."""
  h = _parent_entry(p, history)
  if h is None:
    return champion["recipe"], champion.get("checkpoint")
  recipe = yaml.safe_load(Path(h["recipe"]).read_text())
  for k in ("name", "change", "why", "hypothesis", "control", "init"):
    recipe.pop(k, None)
  return recipe, h["verdict"].get("checkpoint")


def _tune_range(path: str) -> tuple[float, float] | None:
  for card in knowledge.cards().values():
    spec = (card.meta["tune"] or {}).get(path)
    if spec:
      return tuple(spec["range"])
  return None


def check(
  p: dict[str, Any],
  champion: dict[str, Any],
  history: list[dict[str, Any]],
  allow_combine: bool = False,
  gaps: list[Gap] | None = None,
  min_gain: float = worth.MIN_GAIN,
  ceilings: list[str] | tuple[str, ...] = (),
  factor: float = 1.0,
) -> list[str]:
  """Problems with a candidate proposal (empty = valid for the engine)."""
  missing = [f for f in REQUIRED if f not in p]
  unknown = [f for f in p if f not in REQUIRED + OPTIONAL]
  if missing or unknown:
    return [f"fields: missing {missing}, unknown {unknown}"]
  problems = []
  if p["kind"] not in KINDS:
    problems.append(f"kind must be one of {KINDS}")
  if p["task"] not in FAMILY_TASK:
    problems.append(
      f"task {p['task']!r}: proposals are judged only for {sorted(FAMILY_TASK)}"
    )
  if p.get("touches", "training-only") != "training-only":
    problems.append(
      "runtime changes are not proposed to the engine (new policy version)"
    )
  cards = knowledge.cards()
  for a in p["approaches"]:
    card = cards.get(a)
    if card is None:
      problems.append(f"unknown approach {a!r} (add a card first, or kind: new)")
      continue
    status = card.meta["status"]
    if status == "parked" or (status == "rejected" and not p.get("retry_reason")):
      problems.append(
        f"{a} is {status}" + ("" if status == "parked" else ": give retry_reason")
      )
    if card.meta["impact"] == "runtime" and p["kind"] != "new":
      problems.append(f"{a} changes the runtime: not an engine proposal")
  if len(p["approaches"]) > 1 and not allow_combine:
    problems.append("one change per run: one approach per proposal (bundles are off)")
  if p["kind"] == "new":
    return problems  # needs building: no edits to check
  if p["gap"] in ceilings:
    problems.append(f"gap {p['gap']!r} is at a ceiling: training-only children "
                    "failed it; it waits for the user (kind: new or a structural change)")  # fmt: skip
  if p.get("parent") is not None:
    h = _parent_entry(p, history)
    if (
      h is None or not h["verdict"].get("checkpoint") or not Path(h["recipe"]).is_file()
    ):
      problems.append(f"parent {p['parent']!r}: not a judged child with a checkpoint")
      return problems
  doses = p.get("doses") or {}
  if doses:
    if (
      not isinstance(doses, dict)
      or list(doses) != list(p["edits"])[:1]
      or len(p["edits"]) != 1
    ):
      problems.append("doses: other values for the proposal's one edit "
                      "({path: [values]}, same path as its single edit)")  # fmt: skip
    else:
      path, values = next(iter(doses.items()))
      rng = _tune_range(path)
      for v in values:
        if not isinstance(v, int | float):
          problems.append(f"doses: {v!r} is not a number")
        elif rng and not rng[0] <= v <= rng[1] and not p.get("out_of_range_reason"):
          problems.append(f"doses: {v} outside the tune range {list(rng)}")
  if not p["edits"]:
    problems.append("no edits")
  for path, value in p["edits"].items():
    kind, _, rest = path.partition(".")
    if kind == "methods":
      name, _, param = rest.partition(".")
      if name not in APPROACHES:
        problems.append(f"{path}: {name} is not a registered approach")
      elif param and param not in APPROACHES[name].params:
        problems.append(f"{path}: {name} has no parameter {param}")
    elif kind not in ("genes", "rewards") or not rest:
      problems.append(f"{path}: edits must be methods.*, genes.* or rewards.*")
      continue
    rng = _tune_range(path)
    if rng and isinstance(value, int | float) and not rng[0] <= value <= rng[1]:
      if not p.get("out_of_range_reason"):
        problems.append(f"{path}: {value} outside the tune range {list(rng)} "
                        "(give out_of_range_reason)")  # fmt: skip
  if any(" must be methods." in x or "not a registered" in x or "no parameter" in x
         for x in problems):  # fmt: skip
    return problems  # can't apply edits off the recipe surface
  recipe, _ = base_recipe(p, champion, history)
  if apply_edits(recipe, p["edits"]) == recipe:
    problems.append("the edits don't change the base recipe")
  if change_text(p, recipe) in {h.get("change") for h in history}:
    problems.append("already tried (same change in the engine history)")
  problems += estimate(p, gaps, min_gain, factor, _parent_entry(p, history)).problems
  return problems


def estimate(
  p: dict[str, Any],
  gaps: list[Gap] | None = None,
  min_gain: float = worth.MIN_GAIN,
  factor: float = 1.0,
  parent: dict[str, Any] | None = None,
) -> worth.Worth:
  """Expected benchmark gain of a proposal and whether it is worth a run."""
  if gaps is None:
    gaps = champion_gaps(FAMILY_TASK.get(p.get("task"), ""))
  return worth.estimate(p.get("expect"), gaps, min_gain=min_gain, factor=factor,
                        parent=parent)  # fmt: skip


def to_proposal(
  p: dict[str, Any],
  champion: dict[str, Any],
  gain: float | None = None,
  history: list[dict[str, Any]] | None = None,
) -> Proposal:
  history = history or []
  recipe, init = base_recipe(p, champion, history)
  doses = []
  for path, values in (p.get("doses") or {}).items():
    for v in values:
      q = {**p, "edits": {path: v}}
      doses.append((change_text(q, recipe), apply_edits(recipe, q["edits"])))
  return Proposal(
    recipe=apply_edits(recipe, p["edits"]),
    change=change_text(p, recipe),
    why=f"gap {p['gap']}: {p['why']} (evidence: {', '.join(p.get('evidence') or [])})",
    designer=f"llm:{p['designer']}",
    hypothesis=p["hypothesis"],
    expected_gain=gain,
    gap=p["gap"],
    parent=p.get("parent"),
    init=init if p.get("parent") else None,
    doses=doses,
  )


def context(
  champion: dict[str, Any], history: list[dict[str, Any]], family: str
) -> str:
  """Everything the LLM designer needs, as one Markdown document."""
  from k1 import requests
  from k1.approaches.review import gaps_for

  gaps = gaps_for(family, top=10)
  baseline = ApproachDesigner(family, lambda c: gaps)
  moves = baseline.moves(champion, __import__("random").Random(0), history)[:10]
  cards = knowledge.cards()
  shortlist = knowledge.approved_shortlist(family)

  def card_row(c) -> str:
    m = c.meta
    can = "add" if m["trial"] else ""
    can += (" tune:" + ",".join(m["tune"])) if m["tune"] else ""
    uses = ", ".join(
      f"{u['id']}:{u['task']}:{u['result']}" for u in knowledge.uses_of(c.id)
    )
    return (f"| {c.id} | {m['element']} | {m['status']} | {', '.join(m['tags'])} | "
            f"{can.strip() or 'blocked'} | {uses or '-'} |")  # fmt: skip

  recent = history[-15:]
  out = [
    f"# Design context: {family} ({time_now()})",
    "",
    "You are the designer. Propose candidate changes to the champion's recipe that",
    "close its measured gaps. Write each candidate as a YAML file in",
    f"`{INBOX.relative_to(recipes.ROOT)}/` and validate with `rsw design check`.",
    "",
    "## Task request",
    "",
    "```yaml",
    requests.path_of(family).read_text().strip(),
    "```",
    "",
    "## Champion",
    "",
    f"checkpoint: `{champion.get('checkpoint')}`",
    "",
    "```yaml",
    yaml.safe_dump(champion["recipe"], sort_keys=False, width=88).strip(),
    "```",
    "",
    "## Measured gaps (benchmark v2 full, seed 1; vs B-Human or the 0-falls target)",
    "",
    *[
      f"{i + 1}. [{g.weight:.1f}] {g.describe()} — tags {', '.join(g.tags)}"
      for i, g in enumerate(gaps)
    ],  # fmt: skip
    "",
    "## Engine history (most recent last)",
    "",
    *(
      [
        f"- {h['id']} [{h['designer']}] {h['change']} -> {h['verdict']['status']} "
        f"score {h['verdict']['score']}, regressions {len(h['verdict']['regressions'])}"
        f"{' PROMOTED' if h.get('promoted') else ''}; hypothesis: {h.get('hypothesis', '')}"
        for h in recent
      ]
      or ["(nothing tried yet)"]
    ),  # fmt: skip
    "",
    "## What the last children taught (read before proposing)",
    "",
    *reflection(history),
    "",
    f"Forecast calibration: x{worth.calibration(history):.2f} (measured / forecast). "
    f"Gaps at a ceiling (closed to training-only proposals): "
    f"{', '.join(_ceilings()) or 'none'}.",
    "",
    "## rs_kick (runswift-spec kick test, power by kick class)",
    "",
    *rs_gaps(champion),
    "",
    "## Approaches (knowledge/approaches; cards have the details)",
    "",
    "| id | element | status | tags | engine can | uses |",
    "|---|---|---|---|---|---|",
    *[card_row(c) for c in cards.values()],
    "",
    "Tune ranges and steps are in each card's front matter (`tune`).",
    "",
    "## Approved review shortlists",
    "",
    *(
      [
        f"- {e['approach']}: {e.get('hypothesis', '')} ({e['review']})"
        for e in shortlist
      ]
      or ["(none; start one with /review)"]
    ),  # fmt: skip
    "",
    "## Baseline suggestions (deterministic designer, tag matching)",
    "",
    *[
      f"- {mv.change(champion['recipe'])} (score {mv.score:.1f}, gap {mv.gap.metric} "
      f"in {mv.gap.key})"
      for mv in moves
    ],  # fmt: skip
    "",
    "## Rules",
    "",
    RULES,
    "## Proposal schema (one YAML file per candidate)",
    "",
    "```yaml",
    SCHEMA,
    "```",
  ]
  return "\n".join(out) + "\n"


def _ceilings() -> list[str]:
  from k1.engine import state

  path = state.DIR / "state.json"
  return state.load(path).ceilings if path.is_file() else []


def reflection(history: list[dict[str, Any]], n: int = 8) -> list[str]:
  """Per recent judged child: scorecard parts, rs_kick power by class, the
  regressions, probes and the edited terms' training curves."""
  out = []
  for h in [h for h in history if "verdict" in h][-n:]:
    v = h["verdict"]
    m = v.get("metrics") or {}
    rs = m.get("rs") or {}
    parts = [f"- **{h['id']}** {h['change']} -> {v['status']} {v.get('score')}"
             f"{' PROMOTED' if h.get('promoted') else ''}"]  # fmt: skip
    if "bench_score" in m:
      parts.append(
        f"  benchmark v2 {m['bench_score']}, rs_kick points {m.get('rs_points')}"
      )
    if rs.get("margins"):
      parts.append(f"  rs_kick margins vs champion: {rs['margins']}")
    if rs.get("power"):
      parts.append(f"  rs_kick power by class: {rs['power']}")
    if v.get("regressions"):
      parts.append(f"  regressions: {', '.join(v['regressions'][:6])}")
    if h.get("probes"):
      parts.append(
        f"  probes (frac, margin): {[(p['frac'], p['margin']) for p in h['probes']]}"
      )
    cur = m.get("curves") or {}
    if cur.get("focus"):
      parts.append(f"  edited terms' curves (first -> last): {cur['focus']}")
    if cur.get("missing_terms"):
      parts.append(f"  edited terms never logged: {cur['missing_terms']}")
    if h.get("hypothesis"):
      parts.append(f"  hypothesis was: {h['hypothesis']}")
    out += parts
  return out or ["(nothing judged yet)"]


def rs_gaps(champion: dict[str, Any]) -> list[str]:
  """Champion vs B-Human on rs_kick in lab mode: score and power by class."""
  from k1.eval import rs_judge, scorecard

  refs = (champion.get("refs") or scorecard.default_refs())["rs"]
  out = []
  for seed in (0, 1):
    ours_p = refs.get(f"lab_s{seed}")
    bh_p = rs_judge.BHUMAN.get(seed)
    if not ours_p or not bh_p or not Path(ours_p).is_file() or not bh_p.is_file():
      continue
    ours, bh = rs_judge.class_power(Path(ours_p)), rs_judge.class_power(bh_p)
    so = sum(rs_judge.scores_of(Path(ours_p))) / 200
    sb = sum(rs_judge.scores_of(bh_p)) / 200
    out.append(f"- lab s{seed}: score ours {so:.3f} vs B-Human {sb:.3f}; power "
               + ", ".join(f"{c} {ours[c]:.2f} vs {bh[c]:.2f}" for c in ours))  # fmt: skip
  return out or ["(no rs_kick reference results)"]


def time_now() -> str:
  import time

  return time.strftime("%Y-%m-%d %H:%M")


def inbox() -> list[Path]:
  return sorted(INBOX.glob("*.yaml"))


def file_away(path: Path, where: Path, note: str | None = None) -> Path:
  where.mkdir(parents=True, exist_ok=True)
  dest = where / path.name
  shutil.move(str(path), dest)
  if note:
    dest.with_suffix(".why.txt").write_text(note + "\n")
  return dest


# The LLM designer, called by the engine itself when the inbox runs dry
# (user 2026-10-26: "May the engine call the LLM by itself: yes").
ALLOWED_TOOLS = [
  "Read", "Grep", "Glob",
  "Bash(.venv/bin/python -m k1.cli design *)",
  "Bash(.venv/bin/python -m k1.cli review gaps*)",
  "Bash(.venv/bin/python -m k1.cli approaches*)",
  "Edit(experiments/evolution/proposals/inbox/**)",  # covers Write too
]  # fmt: skip
LOGS = PROPOSALS / "llm_logs"


def claude_binary() -> str | None:
  """``$K1_CLAUDE``, ``claude`` on PATH, or the newest editor-extension build."""
  if os.environ.get("K1_CLAUDE"):
    return os.environ["K1_CLAUDE"]
  found = shutil.which("claude")
  if found:
    return found
  home = os.path.expanduser("~")
  builds = sorted(
    glob.glob(f"{home}/.cursor/extensions/anthropic.claude-code-*/resources/native-binary/claude")
    + glob.glob(f"{home}/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude"),
    key=os.path.getmtime,
  )  # fmt: skip
  return str(builds[-1]) if builds else None


def ask_llm(n: int = 3, family: str = "kick", timeout: int = 1800) -> str:
  """Run ``/design`` headless (``claude -p``): it may only read, run the design
  and review commands, and write into the inbox. Returns a one-line outcome;
  the transcript goes to ``proposals/llm_logs/``."""
  exe = claude_binary()
  if exe is None:
    return "no claude binary (set K1_CLAUDE)"
  LOGS.mkdir(parents=True, exist_ok=True)
  log = LOGS / f"{time.strftime('%Y%m%d_%H%M%S')}.log"
  cmd = [exe, "-p", f"/design {n} --task {family}", "--permission-mode", "dontAsk",
         "--allowedTools", *ALLOWED_TOOLS]  # fmt: skip
  if os.environ.get("K1_DESIGN_BUDGET_USD"):
    cmd += ["--max-budget-usd", os.environ["K1_DESIGN_BUDGET_USD"]]
  try:
    out = subprocess.run(
      cmd, cwd=recipes.ROOT, capture_output=True, text=True, timeout=timeout
    )
  except subprocess.TimeoutExpired:
    return f"timed out after {timeout} s"
  log.write_text(f"$ {' '.join(cmd)}\n\n{out.stdout}\n{out.stderr}")
  return f"exit {out.returncode}, {len(inbox())} in the inbox (log {log.name})"

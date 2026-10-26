"""Outer loop: decides what to try, one bounded change at a time.

Every child moves through stages, each a background process the loop polls,
so training never waits on judging:

  smoke -> train (+ probes) -> screen -> confirm -> promoted or recorded

1. **smoke**: a few training iterations of the recipe: it starts, doesn't crash,
   and every reward term it edits is logged; otherwise it never trains;
2. **train** from the champion's (or a named parent child's) checkpoint for
   ``budget_iterations``; at ``probe_fracs`` of the budget the newest checkpoint
   gets a cheap probe (rs_kick deployed); ``kill_after`` significantly negative
   probes in a row stop it early (``stopped_early``);
3. **screen**: the kick scorecard at gate size, with the child's per-term
   training curves attached; a gain without regressions goes on to
4. **confirm** (full scorecard); a confirmed gain is promoted, the champion's
   references are re-made from its own results (``reverify``) and a clip is
   recorded. New screens wait until the references are ready.

Around that: every verdict lands in the history; a gap that ``ceiling_after``
children failed to close goes to the user as a structural request and is not
proposed again; after ``escalate_after`` non-improving verdicts in a row the
loop writes a decision packet and stops proposing; ``gpu_hours`` caps the
loop's spending. Refill: queued doses first, then the designers (LLM inbox
first). The trainer and judge are passed in, so the logic is tested without a
GPU (``tests/test_k1_engine.py``) and ``rsw engine`` plugs in the real ones.
"""

from __future__ import annotations

import random
import time
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

import yaml

from k1 import recipes
from k1.engine import worth
from k1.engine.designers import Designer, Proposal
from k1.engine.state import State
from k1.eval.verdict import Verdict


@dataclass
class Config:
  max_in_flight: int = 2  # at most 2 trainings at a time (lesson O3)
  budget_iterations: int = 500
  escalate_after: int = 6
  smoke: bool = True
  probe_fracs: tuple[float, ...] = (0.3, 0.55, 0.8)
  kill_after: int = 2  # significantly negative probes in a row
  ceiling_after: int = 3  # failed children on one gap before asking the user
  gpu_hours: float | None = None  # stop proposing beyond this spend
  clip: bool = True  # record a clip of every new champion
  # A screen goes on to the confirmation only above this score: an identical
  # re-run of h022 screened +7.0 (benchmark v2 gate 0.0, rs_kick deployed
  # +0.007 = +7 points of seed noise), 2026-10-26.
  screen_min: float = 10.0


class Trainer(Protocol):
  def start(
    self, recipe_path: Path, run_id: str, iterations: int
  ) -> dict[str, Any]: ...

  def poll(self, handle: dict[str, Any]) -> tuple[str, str] | None:
    """None while running; ("done", checkpoint) or ("failed", reason)."""
    ...

  def progress(self, handle: dict[str, Any]) -> tuple[float, str] | None:
    """(fraction of the budget done, newest checkpoint) while training."""
    ...

  def kill(self, handle: dict[str, Any]) -> None: ...


class Judge(Protocol):
  """Runs a stage (``jobs.py``: smoke, probe, screen, confirm, reverify, clip)
  in the background; ``poll`` returns the job's output dict when done."""

  def start(self, stage: str, spec: dict[str, Any]) -> dict[str, Any]: ...

  def poll(self, handle: dict[str, Any]) -> dict[str, Any] | None: ...


def write_recipe(
  proposal: Proposal, champion: dict, run_id: str, out_dir: Path
) -> Path:
  recipe = dict(proposal.recipe)
  recipe["name"] = run_id
  recipe["change"] = proposal.change
  recipe["why"] = f"[{proposal.designer}] {proposal.why}"
  if proposal.hypothesis:
    recipe["hypothesis"] = proposal.hypothesis
  recipe["control"] = proposal.parent or champion["recipe"].get("name")
  recipe["init"] = proposal.init or champion.get("checkpoint")
  out_dir.mkdir(parents=True, exist_ok=True)
  path = out_dir / f"{run_id}.yaml"
  path.write_text(yaml.safe_dump(recipe, sort_keys=False, width=88))
  return path


def _record(state: State, child: dict, verdict: Verdict, promoted: bool) -> None:
  state.history.append(
    {
      "id": child["id"],
      "change": child["change"],
      "designer": child["designer"],
      "hypothesis": child.get("hypothesis", ""),
      "expected_gain": child.get("expected_gain"),
      "gap": child.get("gap", ""),
      "parent": child.get("parent"),
      "family": child.get("family"),
      "recipe": child["recipe_path"],
      "probes": child.get("probes", []),
      "verdict": verdict.to_dict(),
      "promoted": promoted,
      "finished": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
  )


def _verdict(d: dict[str, Any]) -> Verdict:
  return Verdict(**{k: d[k] for k in Verdict.__dataclass_fields__ if k in d})


def _failed(child: dict, what: str, detail: str) -> Verdict:
  status = "smoke_failed" if what != "train" else "train_failed"
  return Verdict("loop", status, child.get("checkpoint", ""), findings=[detail])


def _spec(state: State, child: dict, checkpoint: str = "") -> dict[str, Any]:
  return {
    "name": child["id"],
    "checkpoint": checkpoint,
    "refs": state.champion.get("refs") or {},
    "recipe_path": child["recipe_path"],
    "recipe": yaml.safe_load(Path(child["recipe_path"]).read_text())
    if Path(child["recipe_path"]).is_file()
    else {},
    "champion_recipe": state.champion["recipe"],
    "targets": child.get("targets", []),
  }


def _finish(state: State, cfg: Config, child: dict, v: Verdict, log: list[str]) -> None:
  promoted = v.promotable
  _record(state, child, v, promoted)
  if promoted:
    state.champion = {
      "recipe": yaml.safe_load(Path(child["recipe_path"]).read_text()),
      "checkpoint": v.checkpoint,
      "verdict": v.to_dict(),
      "refs": state.champion.get("refs"),
      "refs_pending": True,
      "id": child["id"],
    }
    state.non_improving = 0
    log.append(f"{child['id']}: NEW CHAMPION ({child['change']}, {v.score:+.1f})")
    return
  state.non_improving += 1
  gap = child.get("gap")
  if gap:
    state.gap_failures[gap] = state.gap_failures.get(gap, 0) + 1
  log.append(f"{child['id']}: {v.status} {v.score} ({child['change']})")


def _side_jobs(state: State, cfg: Config, judge: Judge, log: list[str]) -> None:
  """Reverify (new champion's references) and clips."""
  if state.champion.get("refs_pending") and not any(
    j["kind"] == "reverify" for j in state.side_jobs
  ):
    spec = {"name": state.champion.get("id", "champion"),
            "checkpoint": state.champion["checkpoint"],
            "refs": state.champion.get("refs") or {},
            "verdict": state.champion["verdict"]}  # fmt: skip
    state.side_jobs.append({"kind": "reverify", "for": spec["name"],
                            "handle": judge.start("reverify", spec)})  # fmt: skip
    if cfg.clip:
      state.side_jobs.append({"kind": "clip", "for": spec["name"],
                              "handle": judge.start("clip", spec)})  # fmt: skip
  still = []
  for job in state.side_jobs:
    out = judge.poll(job["handle"])
    if out is None:
      still.append(job)
      continue
    state.gpu_hours += out.get("hours", 0.0)
    if job["kind"] == "reverify":
      refs = out.get("refs") if out.get("ok") else None
      if refs:
        state.champion["refs"] = refs
        v = out["verdict"]
        note = (
          f"; vs previous champion {v.get('score')}, regressions {v.get('regressions')}"
        )
        log.append(f"reverified {job['for']}: references updated{note}")
      else:
        log.append(f"reverify {job['for']} failed: keeping the old references "
                   f"({out.get('error') or out.get('verdict', {}).get('findings')})")  # fmt: skip
      state.champion["refs_pending"] = False
    else:
      for h in state.history:
        if h["id"] == job["for"]:
          h["clip"] = {k: out.get(k) for k in ("file", "checks", "error")}
      log.append(f"clip {job['for']}: {out.get('file')} {out.get('checks')}")
  state.side_jobs = still


def _probe_says_stop(probes: list[dict[str, Any]], kill_after: int) -> bool:
  recent = probes[-kill_after:]
  return len(recent) == kill_after and all(
    p.get("margin") and p["margin"][2] < 0 for p in recent
  )


def collect(state: State, cfg: Config, trainer: Trainer, judge: Judge) -> list[str]:
  log: list[str] = []
  _side_jobs(state, cfg, judge, log)
  still = []
  for child in state.in_flight:
    stage = child["stage"]
    if stage == "smoke":
      out = judge.poll(child["job"])
      if out is None:
        still.append(child)
        continue
      state.gpu_hours += out.get("hours", 0.0)
      problems = out.get("problems", []) if out.get("ok") else [out.get("error", "?")]
      if problems:
        _finish(state, cfg, child, _failed(child, "smoke", "; ".join(problems)), log)
        continue
      child.update(stage="train", job=None, started=time.time(),
                   handle=trainer.start(Path(child["recipe_path"]), child["id"],
                                        cfg.budget_iterations))  # fmt: skip
      log.append(f"{child['id']}: smoke ok, training")
      still.append(child)
    elif stage == "train":
      if child.get("job"):
        out = judge.poll(child["job"])
        if out is not None:
          state.gpu_hours += out.get("hours", 0.0)
          child["probes"].append({"frac": child["job"]["frac"],
                                  "margin": out.get("margin") if out.get("ok") else None})  # fmt: skip
          child["job"] = None
          if _probe_says_stop(child["probes"], cfg.kill_after):
            trainer.kill(child["handle"])
            state.gpu_hours += (time.time() - child["started"]) / 3600
            v = Verdict("loop", "stopped_early", "",
                        findings=[f"probes behind the champion: {child['probes']}"])  # fmt: skip
            _finish(state, cfg, child, v, log)
            continue
      status = trainer.poll(child["handle"])
      if status is None:
        done = {p["frac"] for p in child["probes"]}
        due = [f for f in cfg.probe_fracs if f not in done]
        prog = (
          trainer.progress(child["handle"]) if due and not child.get("job") else None
        )
        if prog and prog[0] >= due[0]:
          child["job"] = {**judge.start("probe", _spec(state, child, prog[1])),
                          "frac": due[0]}  # fmt: skip
        still.append(child)
        continue
      last_probe: dict[str, Any] | None = child.get("job")
      if last_probe is not None and judge.poll(last_probe) is None:
        still.append(child)  # let the last probe land first
        continue
      state.gpu_hours += (time.time() - child["started"]) / 3600
      kind, detail = status
      if kind == "failed":
        _finish(state, cfg, child, _failed(child, "train", detail), log)
        continue
      child.update(stage="await_screen", checkpoint=detail, job=None)
      still.append(child)
    elif stage == "await_screen":
      if not state.champion.get("refs_pending"):
        child.update(stage="screen",
                     job=judge.start("screen", _spec(state, child, child["checkpoint"])))  # fmt: skip
      still.append(child)
    elif stage in ("screen", "confirm"):
      out = judge.poll(child["job"])
      if out is None:
        still.append(child)
        continue
      state.gpu_hours += out.get("hours", 0.0)
      if not out.get("ok"):
        _finish(state, cfg, child, _failed(child, stage, out.get("error", "?")), log)
        continue
      v = _verdict(out["verdict"])
      if out.get("curves"):
        child["curves"] = out["curves"]
        v.metrics["curves"] = out["curves"]
      if (
        stage == "screen"
        and v.status == "scored"
        and (v.score or 0) > cfg.screen_min
        and not v.regressions
      ):
        child.update(stage="confirm", screen=v.to_dict(),
                     job=judge.start("confirm", _spec(state, child, child["checkpoint"])))  # fmt: skip
        log.append(f"{child['id']}: screen {v.score:+.1f}, confirming")
        still.append(child)
        continue
      if stage == "confirm":
        v.metrics["screen"] = child.get("screen")
        v.metrics["curves"] = child.get("curves")
      _finish(state, cfg, child, v, log)
  state.in_flight = still
  return log


def escalation_packet(
  state: State, out_dir: Path, designers: Sequence[Designer] = ()
) -> Path:
  """Decision packet for the user: what was tried, what each verdict said, and
  the matching approaches the engine could not apply (designers' ``blocked``)."""
  out_dir.mkdir(parents=True, exist_ok=True)
  path = out_dir / f"packet_{time.strftime('%Y%m%d_%H%M%S')}.md"
  rows = [
    f"| {h['id']} | {h['designer']} | {h['change']} | {h['verdict']['status']} | "
    f"{h['verdict']['score']} | {len(h['verdict']['regressions'])} |"
    for h in state.history[-state.non_improving :]
  ]
  path.write_text(
    "# Evolution loop: decision needed\n\n"
    f"{state.non_improving} verdicts in a row did not improve on the champion "
    f"({state.champion['recipe'].get('name')}). The loop has stopped proposing.\n\n"
    "| id | designer | change | status | score | regressions |\n|---|---|---|---|---|---|\n"
    + "\n".join(rows)
    + "\n\nOptions: widen a designer's ranges, enable another designer, change the "
    "objective weights, or accept the champion and stop.\n"
    + _blocked_section(designers)
  )
  return path


def ceiling_packet(state: State, gap: str, out_dir: Path) -> Path:
  """Structural request: a gap that training-only changes have failed to close."""
  out_dir.mkdir(parents=True, exist_ok=True)
  path = out_dir / f"ceiling_{time.strftime('%Y%m%d_%H%M%S')}.md"
  tried = [h for h in state.history if h.get("gap") == gap]
  rows = [
    f"| {h['id']} | {h['change']} | {h['verdict']['status']} | {h['verdict']['score']} "
    f"| {', '.join(h['verdict']['regressions'][:3])} |"
    for h in tried
  ]
  path.write_text(
    "# Evolution loop: structural request\n\n"
    f"Gap `{gap}`: {len(tried)} training-only children failed to close it, so the "
    "engine stops proposing for it. Closing it likely needs a change the engine "
    "may not make: an observation or action change (deploy contract + runner + "
    "parity check), a new approach to build (`kind: new`), or a different "
    "objective. Each needs the user.\n\n"
    "| id | change | status | score | regressions |\n|---|---|---|---|---|\n"
    + "\n".join(rows)
    + "\n"
  )
  return path


def _blocked_section(designers: Sequence[Designer]) -> str:
  blocked = sorted({b for d in designers for b in getattr(d, "blocked", [])})
  if not blocked:
    return ""
  return (
    "\nApproaches that match the gaps but need building, a runtime change or a "
    "person (no engine trial): " + ", ".join(blocked) + ". Review them with "
    "`rsw review new TOPIC --task FAMILY`, or give a card a `trial`.\n"
  )


def _launch(
  state: State, cfg: Config, judge: Judge, trainer: Trainer, child: dict, log: list[str]
) -> None:
  if cfg.smoke:
    child.update(stage="smoke", job=judge.start("smoke", _spec(state, child)))
    log.append(f"{child['id']}: smoke test [{child['designer']}] {child['change']}")
  else:
    child.update(stage="train", job=None, started=time.time(),
                 handle=trainer.start(Path(child["recipe_path"]), child["id"],
                                      cfg.budget_iterations))  # fmt: skip
    log.append(f"{child['id']}: started [{child['designer']}] {child['change']}")
  state.in_flight.append(child)


def step(
  state: State,
  cfg: Config,
  designers: list[Designer],
  trainer: Trainer,
  judge: Judge,
  rng: random.Random,
  out_dir: Path,
  check=recipes.check,
) -> list[str]:
  log = collect(state, cfg, trainer, judge)
  for gap, n in state.gap_failures.items():
    if n >= cfg.ceiling_after and gap not in state.ceilings:
      state.ceilings.append(gap)
      log.append(f"ceiling: {ceiling_packet(state, gap, out_dir / 'packets')}")
  if state.non_improving >= cfg.escalate_after:
    packet = escalation_packet(state, out_dir / "packets", designers)
    log.append(f"escalated: {packet}")
    return log
  if cfg.gpu_hours is not None and state.gpu_hours >= cfg.gpu_hours:
    log.append(f"budget: {state.gpu_hours:.1f} of {cfg.gpu_hours:g} GPU-h spent; "
               "not starting more children")  # fmt: skip
    return log
  tried = state.history + [{"change": c["change"]} for c in state.in_flight]
  tried += [{"change": q["change"]} for q in state.queue]
  factor = worth.calibration(state.history)
  for d in designers:  # what the designers must respect this step
    for attr, value in (("ceilings", list(state.ceilings)), ("calibration", factor),
                        ("history", state.history)):  # fmt: skip
      if hasattr(d, attr):
        setattr(d, attr, value)
  attempts = 0
  # Queued doses first; then priority designers (the LLM designer's inbox); the
  # others take turns.
  first = [d for d in designers if getattr(d, "priority", False)]
  for d in first:
    setattr(d, "empty", False)  # noqa: B010  (ask it again this step)
  rest = [d for d in designers if not getattr(d, "priority", False)] or first
  while len(state.in_flight) < cfg.max_in_flight and state.queue:
    child = state.queue.pop(0)
    child["id"] = state.next_id()
    recipe = dict(child.pop("recipe"))
    path = write_recipe(Proposal(recipe, child["change"], child["why"], child["designer"],
                                 child.get("hypothesis", ""), parent=child.get("parent"),
                                 init=child.get("init")),
                        state.champion, child["id"], out_dir / "recipes")  # fmt: skip
    child["recipe_path"] = str(path)
    problems = check(path)
    if problems:
      _record(
        state, child, Verdict("loop", "smoke_failed", "", findings=problems), False
      )
      continue
    _launch(state, cfg, judge, trainer, child, log)
  while len(state.in_flight) < cfg.max_in_flight and attempts < 2 * len(designers):
    pending = [d for d in first if not getattr(d, "empty", False)]
    if pending:
      designer = pending[0]
    else:
      designer = rest[(state.counter + attempts) % len(rest)]
    attempts += 1
    proposals = designer.propose(state.champion, tried, rng)
    if not proposals:
      continue
    proposal = proposals[0]
    if proposal.gap and proposal.gap in state.ceilings:
      log.append(f"[{designer.name}] skipped: gap {proposal.gap} is at a ceiling")
      continue
    run_id = state.next_id()
    path = write_recipe(proposal, state.champion, run_id, out_dir / "recipes")
    family = run_id if proposal.doses else None
    child = {"id": run_id, "change": proposal.change, "designer": designer.name,
             "hypothesis": proposal.hypothesis, "recipe_path": str(path),
             "task": proposal.recipe["task"], "gap": proposal.gap,
             "parent": proposal.parent, "family": family, "probes": [],
             "expected_gain": proposal.expected_gain,
             "targets": proposal.targets}  # fmt: skip
    problems = check(path)
    tried.append({"change": proposal.change})
    if problems:
      _record(
        state, child, Verdict("loop", "smoke_failed", "", findings=problems), False
      )
      log.append(f"{run_id}: recipe check failed ({proposal.change})")
      continue
    for change, recipe in proposal.doses:
      state.queue.append({"change": change, "recipe": recipe, "why": proposal.why,
                          "designer": designer.name, "hypothesis": proposal.hypothesis,
                          "task": proposal.recipe["task"], "gap": proposal.gap,
                          "parent": proposal.parent, "init": proposal.init,
                          "family": family, "probes": [],
                          "expected_gain": proposal.expected_gain,
                          "targets": proposal.targets})  # fmt: skip
      tried.append({"change": change})
    _launch(state, cfg, judge, trainer, child, log)
  log += [m for d in designers for m in _drain(d)]
  return log


def _drain(designer: Designer) -> list[str]:
  msgs = getattr(designer, "log", [])
  out = [f"[{designer.name}] {m}" for m in msgs]
  msgs.clear()
  return out


def config_dict(cfg: Config) -> dict[str, Any]:
  return asdict(cfg)

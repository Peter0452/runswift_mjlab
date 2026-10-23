"""Outer loop: decides what to try, one bounded change at a time.

Each ``step``:
  1. collects finished children: judge (quick screen) -> if it gains without
     regressions, confirm (full benchmark, seeds 1 and 2) -> promote when the
     confirmed verdict is promotable; record every verdict in the history;
  2. escalates: after ``escalate_after`` non-improving verdicts in a row it
     writes a decision packet for the user and stops proposing;
  3. refills the pool up to ``max_in_flight``: a designer proposes a recipe
     (distinct from history), ``rsw recipe check`` gates it, the trainer starts
     it from the champion's checkpoint for ``budget_iterations``.

The trainer and judge are passed in, so the logic is tested without a GPU
(``tests/test_k1_evolve.py``) and ``rsw evolve`` plugs in the real ones.
"""

from __future__ import annotations

import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

import yaml

from k1 import recipes
from k1.eval.verdict import Verdict
from k1.evolve.designers import Designer, Proposal
from k1.evolve.state import State


@dataclass
class Config:
  max_in_flight: int = 2  # at most 2 trainings at a time (lesson O3)
  budget_iterations: int = 500
  escalate_after: int = 6
  screen_size: str = "quick"


class Trainer(Protocol):
  def start(
    self, recipe_path: Path, run_id: str, iterations: int
  ) -> dict[str, Any]: ...

  def poll(self, handle: dict[str, Any]) -> tuple[str, str] | None:
    """None while running; ("done", checkpoint) or ("failed", reason)."""
    ...


class Judge(Protocol):
  def screen(self, task: str, checkpoint: str, name: str) -> Verdict: ...

  def confirm(self, task: str, checkpoint: str, name: str) -> Verdict: ...


def write_recipe(
  proposal: Proposal, champion: dict, run_id: str, out_dir: Path
) -> Path:
  recipe = dict(proposal.recipe)
  recipe["name"] = run_id
  recipe["change"] = proposal.change
  recipe["why"] = f"[{proposal.designer}] {proposal.why}"
  recipe["control"] = champion["recipe"].get("name")
  recipe["init"] = champion.get("checkpoint")
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
      "recipe": child["recipe_path"],
      "verdict": verdict.to_dict(),
      "promoted": promoted,
      "finished": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
  )


def collect(state: State, trainer: Trainer, judge: Judge) -> list[str]:
  log = []
  still = []
  for child in state.in_flight:
    status = trainer.poll(child["handle"])
    if status is None:
      still.append(child)
      continue
    kind, detail = status
    task = child["task"]
    if kind == "failed":
      verdict = Verdict("loop", "train_failed", "", findings=[detail])
    else:
      verdict = judge.screen(task, detail, f"{child['id']}_screen")
      if (
        verdict.status == "scored"
        and (verdict.score or 0) > 0
        and not verdict.regressions
      ):
        verdict = judge.confirm(task, detail, child["id"])
    promoted = verdict.promotable
    _record(state, child, verdict, promoted)
    if promoted:
      state.champion = {
        "recipe": yaml.safe_load(Path(child["recipe_path"]).read_text()),
        "checkpoint": verdict.checkpoint,
        "verdict": verdict.to_dict(),
      }
      state.non_improving = 0
      log.append(
        f"{child['id']}: NEW CHAMPION ({child['change']}, {verdict.score:+.1f})"
      )
    else:
      state.non_improving += 1
      log.append(f"{child['id']}: {verdict.status} {verdict.score} ({child['change']})")
  state.in_flight = still
  return log


def escalation_packet(state: State, out_dir: Path) -> Path:
  """Decision packet for the user: what was tried, what each verdict said."""
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
  )
  return path


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
  log = collect(state, trainer, judge)
  if state.non_improving >= cfg.escalate_after:
    log.append(f"escalated: {escalation_packet(state, out_dir / 'packets')}")
    return log
  tried = state.history + [
    {"change": c["change"]} for c in state.in_flight
  ]  # distinct from everything in flight too
  attempts = 0
  while len(state.in_flight) < cfg.max_in_flight and attempts < 2 * len(designers):
    designer = designers[(state.counter + attempts) % len(designers)]
    attempts += 1
    proposals = designer.propose(state.champion, tried, rng)
    if not proposals:
      continue
    proposal = proposals[0]
    run_id = state.next_id()
    path = write_recipe(proposal, state.champion, run_id, out_dir / "recipes")
    child = {"id": run_id, "change": proposal.change, "designer": designer.name,
             "recipe_path": str(path), "task": proposal.recipe["task"]}  # fmt: skip
    problems = check(path)
    tried.append({"change": proposal.change})
    if problems:
      _record(
        state, child, Verdict("loop", "smoke_failed", "", findings=problems), False
      )
      log.append(f"{run_id}: recipe check failed ({proposal.change})")
      continue
    child["handle"] = trainer.start(path, run_id, cfg.budget_iterations)
    state.in_flight.append(child)
    log.append(f"{run_id}: started [{designer.name}] {proposal.change}")
  return log


def config_dict(cfg: Config) -> dict[str, Any]:
  return asdict(cfg)

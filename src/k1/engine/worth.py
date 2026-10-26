"""Is a candidate worth a kick retrain?

Every engine child costs a fine-tune from the champion plus a quick screen and
a two-seed full confirmation (``RUN_HOURS``, about 2.7 GPU-hours at two
trainings at a time), and the verdict can only see gains above the
benchmark's noise. So before anything trains, the candidate's own forecast
(``expect`` in the proposal) is turned into the score the benchmark would give
it, with the fitness formula (``scripts/tools/fitness_v2.py``):

    gain = sum over expected effects of  p x min(|by| / tol, 3) x weight x caps

- ``by``: expected change of the metric, in its own units; ``tol``: the
  metric's fitness tolerance (widened to seed noise on 2026-10-05); ``weight``:
  primary 3, safety 2, rest 1; ``caps``: the speed caps it shows up at
  (default: where the gap is, else both);
- ``p``: the designer's probability that the effect happens.

Two gates (``Config.min_z``, ``Config.min_gain``):

1. **detectable**: the main effect moves its metric by at least one tolerance;
   smaller moves are inside one metric's seed noise;
2. **worth a run**: the expected gain reaches ``min_gain`` (default 4: one
   safety metric better by one tolerance at both speed caps, for sure; fully
   closing one safety gap at one cap is worth at most 3 x 2 = 6). Detection is
   per metric (tolerances are seed noise; regressions need separated CIs), not
   by the aggregate score, whose one-seed noise reaches about +30 because it
   sums ~80 metric-caps. 4 is a starting value; calibrate it from forecasts
   vs verdicts once the engine has some history.

The expected gain is stored with the child, so verdicts can calibrate the
designer's forecasts later (expected vs measured).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from k1.engine.gaps import Gap

SEC_PER_IT = 7.7  # child fine-tune beside another run (log 2026-10-05)
BENCH_HOURS = 0.3 + 2 * 0.7  # quick screen + full benchmark on seeds 1 and 2
MIN_Z = 1.0
MIN_GAIN = 4.0


def run_hours(iterations: int) -> float:
  return iterations * SEC_PER_IT / 3600 + BENCH_HOURS


@dataclass
class Worth:
  gain: float
  effects: list[str] = field(default_factory=list)
  problems: list[str] = field(default_factory=list)

  @property
  def ok(self) -> bool:
    return not self.problems


def _fitness_rows() -> dict[tuple[str, str], tuple[float, float]]:
  from k1.eval import judges

  return {(k, m): (t, w) for k, m, _, t, w in judges._fitness().METRICS}


def effects_of(expect: Any) -> list[dict[str, Any]]:
  return expect if isinstance(expect, list) else [expect]


# rs_kick metrics a forecast may name (situation "rs_kick/<mode>"): score and
# power by kick class (``rs_judge``); tolerance = about one seed's noise,
# weight as the scorecard counts them (deployed score is the one in the score).
RS_ROWS: dict[tuple[str, str], tuple[float, float]] = {
  ("rs_kick/deployed", "score"): (0.015, 3.0),
  ("rs_kick/lab", "score"): (0.01, 1.0),
  **{(f"rs_kick/{m}", f"power_{c}"): (0.05, 1.0)
     for m in ("deployed", "lab") for c in ("small", "medium", "strong")},
}  # fmt: skip
CALIBRATION_MIN = 3  # verdicts with a forecast before calibration applies
CALIBRATION_RANGE = (0.25, 1.5)


def calibration(history: list[dict[str, Any]]) -> float:
  """Measured over forecast gain across judged children (losses count as 0):
  the factor the next forecasts are multiplied by. 1 until enough history."""
  pairs = [
    (h["expected_gain"], max(0.0, h["verdict"].get("score") or 0.0))
    for h in history
    if (h.get("expected_gain") or 0) > 0
    and h["verdict"]["status"] in ("scored", "stopped_early")
  ]
  if len(pairs) < CALIBRATION_MIN:
    return 1.0
  ratio = sum(m for _, m in pairs) / sum(e for e, _ in pairs)
  return min(CALIBRATION_RANGE[1], max(CALIBRATION_RANGE[0], ratio))


def unblock_credit(effect: dict[str, Any], parent: dict[str, Any] | None) -> float:
  """A forecast effect that fixes one of the parent child's regressions earns
  its share of the parent's gain: that regression is what blocked promoting it."""
  if not parent:
    return 0.0
  regress = parent["verdict"].get("regressions") or []
  gain = max(0.0, parent["verdict"].get("score") or 0.0)
  hits = [r for r in regress
          if r.split(":")[0] == effect["situation"] and r.split(":")[1] == effect["metric"]]  # fmt: skip
  return gain * len(hits) / len(regress) if hits else 0.0


def estimate(
  expect: Any,
  gaps: list[Gap],
  min_z: float = MIN_Z,
  min_gain: float = MIN_GAIN,
  rows: dict[tuple[str, str], tuple[float, float]] | None = None,
  factor: float = 1.0,
  parent: dict[str, Any] | None = None,
) -> Worth:
  """Expected benchmark score of a proposal's ``expect`` and the gate result.
  ``factor``: calibration from past forecasts; ``parent``: the history entry a
  child continues from (fixing its regressions earns credit)."""
  rows = {**(rows if rows is not None else _fitness_rows()), **RS_ROWS}
  w = Worth(0.0)
  for i, e in enumerate(effects_of(expect)):
    if not isinstance(e, dict):
      w.problems.append("expect: each effect is a mapping")
      continue
    missing = [k for k in ("metric", "situation", "by", "p") if k not in e]
    if missing:
      w.problems.append(f"expect: effect {i + 1} needs {missing} (by in metric "
                        "units, p = probability it happens)")  # fmt: skip
      continue
    key, metric = e["situation"], e["metric"]
    if (key, metric) not in rows:
      w.problems.append(f"expect: {metric} in {key} is not a benchmark metric "
                        "(fitness_v2.METRICS)")  # fmt: skip
      continue
    try:
      by, p = abs(float(e["by"])), float(e["p"])
    except (TypeError, ValueError):
      w.problems.append(f"expect: effect {i + 1}: by and p must be numbers")
      continue
    if not 0.0 < p <= 1.0:
      w.problems.append(f"expect: effect {i + 1}: p must be in (0, 1]")
      continue
    tol, weight = rows[(key, metric)]
    z = by / tol
    if key.startswith("rs_kick/"):
      caps = ["-"]  # rs_kick runs at its own caps
    else:
      caps = e.get("caps") or sorted(
        {g.cap for g in gaps if g.key == key and g.metric == metric}
      ) or ["low", "high"]  # fmt: skip
    gain = (
      p * min(z, 3.0) * weight * len(caps) + p * unblock_credit(e, parent)
    ) * factor
    w.gain += gain
    w.effects.append(f"{metric} in {key} by {by:g} ({z:.1f} tol) at {'+'.join(caps)} "
                     f"caps, p {p:g} -> {gain:+.1f}")  # fmt: skip
    if i == 0 and z < min_z:
      w.problems.append(
        f"not detectable: the main effect moves {metric} by {by:g}, below "
        f"{min_z:g} tolerance ({tol:g}); the benchmark can't tell it from noise"
      )
  if factor != 1.0:
    w.effects.append(f"calibration x{factor:.2f} (measured / forecast so far)")
  if not w.problems and w.gain < min_gain:
    w.problems.append(
      f"not worth a run: expected gain {w.gain:+.1f} < {min_gain:g} "
      f"(~{run_hours(500):.1f} GPU-h per child)"
    )
  return w

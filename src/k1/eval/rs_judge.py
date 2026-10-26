"""Judge against B-Human on the runswift-spec kick benchmark (``rs_kick.py``).

Every policy sees the same trials for a given seed, so comparisons are paired
per trial: the margin is the mean score difference over the 200 trials and its
95 % CI. Two modes:

- **lab**: perfect perception, zero delay, as B-Human's kick is run
  (``bench_bhuman_kick_v2.py``, noise off). The head-to-head with B-Human.
- **deployed**: camera ball model and 10-40 ms delay, as on the robot. Compared
  with the champion; B-Human has no deployed-path run (no perception front end
  for its policy), so its lab score is the target there too.

Results land in ``docs/benchmarks_rs_kick/<name>_<mode>_s<seed>/``. The
B-Human and champion trial files are the references below.
"""

from __future__ import annotations

import csv
import math
import statistics
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from k1.eval import rs_kick

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs" / "benchmarks_rs_kick"
MODES = {
  "deployed": [],
  "lab": ["--perception", "perfect", "--delay", "zero"],
}
# B-Human pretrained (K1_kick_inner.pth) per seed, noise off.
BHUMAN = {
  0: ROOT / "docs/benchmarks_bhuman_kick/kick_v2_seed0/trials_pretrained.csv",
  1: ROOT / "docs/benchmarks_bhuman_kick/night_bh_s1/trials_pretrained.csv",
}
# The kick champion (h022_c2_18450) per (mode, seed).
CHAMPION = {
  (mode, seed): OUT / f"night_h022_{tag}_s{seed}" / "trials_h022.csv"
  for mode, tag in (("deployed", "dep"), ("lab", "lab"))
  for seed in (0, 1)
}
SUBSTANTIAL = 0.05  # paired margin over B-Human that counts as substantial


@dataclass
class Paired:
  mean: float
  lo: float
  hi: float

  def __str__(self) -> str:
    return f"{self.mean:+.3f} [{self.lo:+.3f}, {self.hi:+.3f}]"


@dataclass
class RsVerdict:
  checkpoint: str
  scores: dict[str, float] = field(default_factory=dict)  # "<mode>_s<seed>"
  vs_bhuman: dict[str, str] = field(default_factory=dict)
  vs_champion: dict[str, str] = field(default_factory=dict)
  falls: int = 0
  # (mean, lo, hi) of the paired margin over the champion, per "<mode>_s<seed>".
  margins: dict[str, list[float]] = field(default_factory=dict)
  trials: dict[str, str] = field(default_factory=dict)  # per-trial CSV per key
  # Power score by kick class (rs_kick.KICK_CLASSES), per key.
  power: dict[str, dict[str, float]] = field(default_factory=dict)

  def to_dict(self) -> dict[str, Any]:
    return asdict(self)


def scores_of(path: Path) -> list[float]:
  """Trial scores under the current formula (reference files predate changes)."""
  with open(path) as f:
    return [rs_kick.rescore(r) for r in csv.DictReader(f)]


def paired(a: list[float], b: list[float]) -> Paired:
  if len(a) != len(b):
    raise ValueError("paired comparison needs the same trials")
  d = [x - y for x, y in zip(a, b, strict=True)]
  half = 1.96 * statistics.stdev(d) / math.sqrt(len(d))
  m = statistics.fmean(d)
  return Paired(m, m - half, m + half)


def class_power(path: Path) -> dict[str, float]:
  """Mean power score per kick class over the kicked, standing trials."""
  with open(path) as f:
    ok = [
      r for r in csv.DictReader(f) if r["kicked"] == "True" and r["fell"] == "False"
    ]
  out = {}
  for c in rs_kick.KICK_CLASSES:
    vals = [rs_kick.power_score(float(r["peak_speed"]), float(r["range"]))
            for r in ok if rs_kick.kick_class(float(r["range"])) == c]  # fmt: skip
    out[c] = round(statistics.fmean(vals), 4) if vals else float("nan")
  return out


def run(
  checkpoint: str,
  name: str,
  seeds: tuple[int, ...] = (0, 1),
  modes: tuple[str, ...] = tuple(MODES),
  champion: dict[str, str] | None = None,
) -> RsVerdict:
  """``champion``: the champion's per-trial CSV per "<mode>_s<seed>" (default
  h022's)."""
  v = RsVerdict(checkpoint)
  for mode in modes:
    flags = MODES[mode]
    for seed in seeds:
      tag = f"{name}_{mode}_s{seed}"
      subprocess.run(
        [sys.executable, "scripts/tools/rs_kick_bench.py", "--name", tag,
         "--seed", str(seed), *flags, "--policy", f"p={checkpoint}"],
        cwd=ROOT, capture_output=True, text=True, check=True,
      )  # fmt: skip
      trials = OUT / tag / "trials_p.csv"
      ours = scores_of(trials)
      key = f"{mode}_s{seed}"
      v.scores[key] = round(statistics.fmean(ours), 4)
      v.trials[key] = str(trials)
      v.power[key] = class_power(trials)
      with open(trials) as f:
        v.falls += sum(r["fell"] == "True" for r in csv.DictReader(f))
      if seed in BHUMAN and BHUMAN[seed].is_file():
        v.vs_bhuman[key] = str(paired(ours, scores_of(BHUMAN[seed])))
      ref = Path(champion[key]) if champion and key in champion else None
      ref = ref or CHAMPION.get((mode, seed))
      if ref and ref.is_file():
        m = paired(ours, scores_of(ref))
        v.vs_champion[key] = str(m)
        v.margins[key] = [round(m.mean, 4), round(m.lo, 4), round(m.hi, 4)]
  return v

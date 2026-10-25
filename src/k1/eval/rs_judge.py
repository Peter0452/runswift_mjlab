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

  def to_dict(self) -> dict[str, Any]:
    return asdict(self)


def scores_of(path: Path) -> list[float]:
  with open(path) as f:
    return [float(r["score"]) for r in csv.DictReader(f)]


def paired(a: list[float], b: list[float]) -> Paired:
  if len(a) != len(b):
    raise ValueError("paired comparison needs the same trials")
  d = [x - y for x, y in zip(a, b, strict=True)]
  half = 1.96 * statistics.stdev(d) / math.sqrt(len(d))
  m = statistics.fmean(d)
  return Paired(m, m - half, m + half)


def run(checkpoint: str, name: str, seeds: tuple[int, ...] = (0, 1)) -> RsVerdict:
  v = RsVerdict(checkpoint)
  for mode, flags in MODES.items():
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
      with open(trials) as f:
        v.falls += sum(r["fell"] == "True" for r in csv.DictReader(f))
      if seed in BHUMAN and BHUMAN[seed].is_file():
        v.vs_bhuman[key] = str(paired(ours, scores_of(BHUMAN[seed])))
      ref = CHAMPION.get((mode, seed))
      if ref and ref.is_file():
        v.vs_champion[key] = str(paired(ours, scores_of(ref)))
  return v

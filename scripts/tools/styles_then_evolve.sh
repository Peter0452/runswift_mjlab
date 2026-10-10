#!/usr/bin/env bash
# After the kick-style runs finish: style baselines for the champion and
# B-Human, queue the style runs as evolution candidates, start evolution.
set -u
cd "$(dirname "$0")/../.."
L=logs/rsl_rl/k1_kick_stage3_amp
while pgrep -f "[r]un-name sty_" >/dev/null; do sleep 60; done
CK=$(python3 -c "import json;print(json.load(open('docs/evolution/state.json'))['champion']['ck'])")
uv run python scripts/tools/kick_anatomy.py ours "$CK" > docs/benchmarks/anat_champion.txt 2>&1
uv run python scripts/tools/kick_anatomy.py bhuman > docs/benchmarks/anat_bhuman.txt 2>&1
uv run python - <<'PY'
import json, sys
sys.path.insert(0, "scripts/tools")
from kick_benchmark import _anat_styles
from pathlib import Path
B = Path("docs/benchmarks")
champ = json.load(open("docs/evolution/state.json"))["champion"]["name"]
for name, txt in ((champ, "anat_champion.txt"), ("bhuman", "anat_bhuman.txt")):
  m = json.loads((B / f"{name}.json").read_text())
  _anat_styles(m, (B / txt).read_text())
  (B / f"{name}.json").write_text(json.dumps(m, indent=2))
  print(name, {k: m.get(k) for k in ("h2h_support_planted_short_pct", "style_inside_short_pct", "style_hop_long_pct", "hop_fall_pct")})
seeds = []
S = "/tmp/claude-1000/-home-peter-Desktop-Project-RL/03a30a32-4b87-4b76-ade4-979cf900f3dd/scratchpad"
for n in ("sty_range", "sty_free", "sty_range_strong"):
  d = sorted(Path("logs/rsl_rl/k1_kick_stage3_amp").glob(f"*_{n}"))
  if not d:
    continue
  cks = [str(d[-1] / f"model_{i}.pt") for i in range(14450, 16201, 250) if (d[-1] / f"model_{i}.pt").exists()]
  seeds.append({"name": n, "genes": json.load(open(f"{S}/genes_{n}.json")), "cks": cks})
Path("docs/evolution/seed_runs.json").write_text(json.dumps(seeds, indent=2))
print("seeded", [(s["name"], len(s["cks"])) for s in seeds])
PY
exec uv run python scripts/tools/evolve_kick.py --hours 14

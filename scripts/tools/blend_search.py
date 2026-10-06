"""Screen weight-space blends of two checkpoints at several ratios, then
benchmark the best one. usage: blend_search.py NAME CK_A CK_B [ratios...]
(ratio = weight of CK_A)."""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from evolve_kick import BENCH, EVO, ROOT, log, screen, screen_score  # noqa: E402

name, a, b = sys.argv[1:4]
ratios = [float(r) for r in sys.argv[4:]] or [0.8, 0.65, 0.5]
out_dir = ROOT / "logs" / "rsl_rl" / "k1_kick_stage3_amp" / "blends"
st = json.loads((EVO / "state.json").read_text())
ref = st.get("screen") if st.get("screen_of") == st["champion"]["name"] else None
if ref is None:
  ref = screen(Path(st["champion"]["ck"]))
  log(f"blend_search: screened champion {st['champion']['name']}: {ref}")
res = []
for r in ratios:
  ck = out_dir / f"{name}_{int(r * 100)}.pt"
  subprocess.run(
    ["uv", "run", "python", "scripts/tools/blend_checkpoints.py", str(ck), f"{a}:{r}", f"{b}:{1 - r}"],
    cwd=ROOT, capture_output=True,
  )  # fmt: skip
  s = screen(ck)
  if s is None:
    continue
  res.append((screen_score(s, ref), r, ck, s))
  log(f"blend {name} {r:.2f}/{1 - r:.2f}: screen {screen_score(s, ref):+.1f} {s}")
res.sort(key=lambda x: -x[0])
if res:
  _, r, ck, _ = res[0]
  bname = f"{name}_{int(r * 100)}"
  subprocess.run(
    ["uv", "run", "python", "scripts/tools/kick_benchmark.py", "run", bname, str(ck)],
    cwd=ROOT, capture_output=True,
  )  # fmt: skip
  print(subprocess.run(
    ["uv", "run", "python", "scripts/tools/kick_benchmark.py", "compare", bname, "--best", st["champion"]["name"]],
    cwd=ROOT, capture_output=True, text=True,
  ).stdout)  # fmt: skip
  print(f"BEST BLEND {bname} -> {BENCH / (bname + '.json')}")

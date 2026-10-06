"""Overnight evolutionary search over kick training "genes" (K1 stage 3).

Loop (one training at a time):
  1. pick a parent from the elite archive (champion most often), make a child by
     uniform crossover with another elite and Gaussian mutation of the genes;
  2. fine-tune the child from the parent checkpoint with KICK_GENES set, for
     +250 and +500 iterations (one run), then stop it;
  3. benchmark both checkpoints (scripts/tools/kick_benchmark.py) and score them
     against the champion and the anchor (v56d/13450);
  4. a checkpoint replaces the champion only if it has no regression vs the
     champion (benchmark tolerances) or the anchor (2x tolerance) and a
     positive score; every evaluated child enters the archive.

State: docs/evolution/state.json; log: docs/evolution/log.md.
usage: python scripts/tools/evolve_kick.py [--hours H]
"""

from __future__ import annotations

import json
import os
import random
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "tools"))
from kick_benchmark import METRICS  # noqa: E402

EVO = ROOT / "docs" / "evolution"
BENCH = ROOT / "docs" / "benchmarks"
LOGS = ROOT / "logs" / "rsl_rl" / "k1_kick_stage3_amp"
TASK = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"
ANCHOR = "v56d_13450"

# gene: (low, high, default)
GENES: dict[str, tuple[float, float, float]] = {
  "w.long_kick_power": (2000.0, 4500.0, 3000.0),
  "w.torque_over_soft_limit": (-250.0, -40.0, -100.0),
  "w.kick_rest_accuracy": (300.0, 1000.0, 600.0),
  "w.kick_direction": (600.0, 1300.0, 900.0),
  "w.long_kick_underpower": (-600.0, -100.0, -300.0),
  "w.search_turn": (5.0, 15.0, 10.0),
  "rsi_bhuman": (0.0, 0.3, 0.1),
  "rsi_ours": (0.0, 0.3, 0.1),
  "style_w": (0.2, 0.4, 0.3),
  "k.SUPPORT_PLANT_FACTOR": (0.3, 1.0, 0.5),
  "k.MOMENTUM_KICK_MAX_SPEED": (0.6, 1.3, 1.0),
  "k.LONG_AIM_SIGMA2": (0.03, 0.12, 0.05),
  # On/off switches (K4 / K4b): kick clips in the AMP data, style on near the
  # ball. Without them every child carried K4, which v59 showed costs goals.
  "desired_kl": (0.003, 0.012, 0.01),
  "w.side_foot_strike": (0.0, 600.0, 0.0),
  # structural: template term weights (0 = term absent)
  "t.far_cap_tracking": (0.0, 12.0, 0.0),
  "t.long_power_ramp": (0.0, 3000.0, 0.0),
  "t.aim_tight": (0.0, 1200.0, 0.0),
  "t.upright_fast": (-3.0, 0.0, 0.0),
  "amp_kick_data": (0.0, 1.0, 1.0),
  "k.KICK_STYLE_AMP": (0.0, 1.0, 1.0),
}
# Structural genes (L1): expression terms from the reward grammar, weight 0 = off.
TEMPLATES: dict[str, tuple[dict, float]] = {
  # far approach: match the vx cap while the ball is > 3 m away (gap: ~0.45 m/s)
  "far_cap_tracking": (
    {
      "mul": [
        {"gt": [{"sig": "ball_dist"}, 3.0]},
        {"linear_match": [{"sig": "vx"}, {"sig": "vx_cap"}]},
      ]
    },
    6.0,
  ),
  # long kicks: ramp of 3D speed 4 -> 9 m/s, aimed, loft-limited
  "long_power_ramp": (
    {
      "mul": [
        {"sig": "kick_event"},
        {"sig": "kick_long"},
        {"ramp": [{"sig": "kick_speed"}, 4.0, 9.0]},
        {"gauss": [{"sig": "kick_aim_err"}, 0.0, 0.25]},
        {"sig": "kick_loft"},
      ]
    },
    1500.0,
  ),
  # accuracy: every kick, Gaussian on aim error (sigma 0.15 rad ~ 9 deg)
  "aim_tight": (
    {"mul": [{"sig": "kick_event"}, {"gauss": [{"sig": "kick_aim_err"}, 0.0, 0.15]}]},
    600.0,
  ),
  # posture at speed: pitch band only when walking faster than 1 m/s
  "upright_fast": (
    {
      "mul": [
        {"gt": [{"sig": "vx"}, 1.0]},
        {"band": [{"sig": "trunk_pitch_deg"}, -5.0, 1.0, 2.0]},
      ]
    },
    -1.0,
  ),
}
PROGRAMS = EVO / "programs"


def write_program(name: str, genes: dict) -> str | None:
  terms = []
  for t, (expr, _) in TEMPLATES.items():
    w = float(genes.get(f"t.{t}", 0.0))
    if w != 0.0:
      terms.append({"name": f"tpl_{t}", "expr": expr, "weight": w})
  if not terms:
    return None
  PROGRAMS.mkdir(parents=True, exist_ok=True)
  path = PROGRAMS / f"{name}.json"
  path.write_text(json.dumps(terms, indent=2))
  return str(path)


BINARY = {"amp_kick_data", "k.KICK_STYLE_AMP"}
# v58/14200's actual recipe (no K4 / K4b).
V58_GENES_OFF = {
  "rsi_bhuman": 0.0,
  "rsi_ours": 0.0,
  "amp_kick_data": 0.0,
  "k.KICK_STYLE_AMP": 0.0,
  "k.SUPPORT_PLANT_FACTOR": 1.0,
}
STEPS = (
  100,
  150,
  200,
  250,
  300,
  350,
  400,
  450,
  500,
)  # screened; best gets the full benchmark


def log(msg: str) -> None:
  EVO.mkdir(parents=True, exist_ok=True)
  line = f"- {time.strftime('%Y-%m-%d %H:%M')} {msg}\n"
  with open(EVO / "log.md", "a") as f:
    f.write(line)
  print(line, end="", flush=True)


def load_state() -> dict:
  p = EVO / "state.json"
  if p.exists():
    return json.loads(p.read_text())
  return {"gen": 0, "champion": None, "archive": []}


def save_state(st: dict) -> None:
  (EVO / "state.json").write_text(json.dumps(st, indent=2))


def bench(name: str, ck: str | None, seed: int = 1) -> dict | None:
  out = BENCH / f"{name}.json"
  if not out.exists():
    args = ["uv", "run", "python", "scripts/tools/kick_benchmark.py", "run", name]
    if ck:
      args.append(ck)
    env = {k: v for k, v in os.environ.items() if k != "KICK_GENES"}
    env["KICK_BENCH_SEED"] = str(seed)
    subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True)
  if not out.exists():
    return None
  m = json.loads(out.read_text())
  return m if sum(v is not None for v in m.values()) >= 20 else None


def score(m: dict, ref: dict, anchor: dict) -> tuple[float, list[str]]:
  """Sum of tolerance-normalised improvements over the champion (head-to-head
  metrics x2), and the list of regressions (vs champion, or 2x vs anchor)."""
  total, regress = 0.0, []
  for key, (hib, tol, h2h, _) in METRICS.items():
    v, r, a = m.get(key), ref.get(key), anchor.get(key)
    if v is None:
      regress.append(f"{key}:missing")
      continue
    sgn = 1.0 if hib else -1.0
    if r is not None:
      z = max(-3.0, min(3.0, sgn * (v - r) / tol))
      total += (2.0 if h2h else 1.0) * z
      if z < -1.0:
        regress.append(key)
    # Anchor: only flag a metric that is clearly below v56d AND got worse than
    # the champion (values inherited from the champion are not regressions).
    worse_than_champ = r is not None and sgn * (v - r) < 0
    if a is not None and sgn * (v - a) / tol < -2.0 and worse_than_champ:
      if key not in regress:
        regress.append(f"{key}(anchor)")
  return total, regress


def screen(ck: Path) -> dict | None:
  """Fast screen (~3 min): bumps eval (goals, aim, late falls, 512 envs) and the
  close-start style probe (long-kick 3D speed, aim)."""
  env = {k: v for k, v in os.environ.items() if k != "KICK_GENES"}
  ev = subprocess.run(
    ["uv", "run", "python", "scripts/tools/eval_kick_loop.py", "--checkpoint", str(ck),
     "--num-envs", "512", "--seed", "1", "--no-push"],
    cwd=ROOT, env=env, capture_output=True, text=True,
  ).stdout  # fmt: skip
  st = subprocess.run(
    ["uv", "run", "python", "scripts/tools/kick_style_compare.py", "ours", str(ck), "--any-bearing"],
    cwd=ROOT, env=env, capture_output=True, text=True,
  ).stdout  # fmt: skip
  import re

  def f(p, t):
    m = re.search(p, t)
    return float(m.group(1)) if m else None

  out = {
    "goals": f(r"goals per episode\s+mean ([\d.]+)", ev),
    "aim": f(r"kicks on target \(≤20°\)\s+(\d+)%", ev),
    "falls": f(r"after the first 2 s ([\d.]+)%", ev),
    "long3d": f(r"STYLE long .*?ball 3D p50 ([\d.]+)", st),
    "h2h_aim": f(r"aim err <= 20 deg ([\d.]+) %", st),
  }
  return out if all(v is not None for v in out.values()) else None


def screen_score(s: dict, ref: dict) -> float:
  return (
    (s["goals"] - ref["goals"]) / 0.07
    + (s["aim"] - ref["aim"]) / 3.0
    - (s["falls"] - ref["falls"]) / 0.5
    + 2.0 * (s["long3d"] - ref["long3d"]) / 0.3
    + 2.0 * (s["h2h_aim"] - ref["h2h_aim"]) / 2.0
  )


def child_genes(st: dict) -> dict:
  elites = sorted(st["archive"], key=lambda e: -e["score"])[:4]
  parent = st["champion"]
  genes = dict(parent["genes"])
  if elites and random.random() < 0.5:
    other = random.choice(elites)["genes"]
    for g in GENES:
      if random.random() < 0.5 and g in other:
        genes[g] = other[g]
  n_mut = 0
  for g, (lo, hi, _) in GENES.items():
    if g in BINARY:
      if random.random() < 0.15:
        genes[g] = 1.0 - float(genes.get(g, GENES[g][2]))
        n_mut += 1
      continue
    if random.random() < 0.3:
      genes[g] = min(
        hi, max(lo, genes.get(g, GENES[g][2]) + random.gauss(0, 0.15 * (hi - lo)))
      )
      n_mut += 1
  if random.random() < 0.3:
    off = [t for t in TEMPLATES if float(genes.get(f"t.{t}", 0.0)) == 0.0]
    if off:
      t = random.choice(off)
      genes[f"t.{t}"] = TEMPLATES[t][1]
      n_mut += 1
  if n_mut == 0:
    g = random.choice([x for x in GENES if x not in BINARY])
    lo, hi, _ = GENES[g]
    genes[g] = min(
      hi, max(lo, genes.get(g, GENES[g][2]) + random.gauss(0, 0.15 * (hi - lo)))
    )
  return {k: round(v, 4) for k, v in genes.items()}


def train_child(name: str, parent_ck: Path, genes: dict) -> list[Path]:
  """Fine-tune from parent_ck; return checkpoints at +STEPS (as they exist)."""
  run_dir_glob = f"*_{name}"
  it0 = int(parent_ck.stem.split("_")[1])
  logf = open(LOGS / f"{name}_console.log", "w")
  env = dict(os.environ, KICK_GENES=json.dumps(genes))
  prog = write_program(name, genes)
  if prog:
    env["KICK_REWARD_PROGRAM"] = prog
    log(f"{name}: reward program {Path(prog).name}")
  proc = subprocess.Popen(
    [
      "uv", "run", "train", TASK, "--env.scene.num-envs", "4096",
      "--agent.resume", "True", "--agent.load-run", parent_ck.parent.name,
      "--agent.load-checkpoint", parent_ck.name, "--agent.run-name", name,
    ],
    cwd=ROOT, env=env, stdout=logf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
    start_new_session=True,
  )  # fmt: skip
  got: list[Path] = []
  deadline = (
    time.time() + 150 * 60
  )  # 500 iterations: ~25 min alone, ~65 min beside a benchmark
  try:
    while time.time() < deadline:
      time.sleep(30)
      dirs = sorted(LOGS.glob(run_dir_glob))
      if dirs:
        got = [dirs[-1] / f"model_{it0 + s}.pt" for s in STEPS]
        if got[-1].exists():
          time.sleep(15)  # let the file finish writing
          break
      if proc.poll() is not None:
        log(f"{name}: training exited early (code {proc.returncode})")
        break
  finally:
    if proc.poll() is None:
      os.killpg(proc.pid, signal.SIGTERM)
      try:
        proc.wait(timeout=60)
      except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
    logf.close()
  return [p for p in got if p.exists()]


BLENDS = LOGS / "blends"


def try_blends(
  name: str, champ: dict, child_ck: Path, ref: dict, anchor: dict, ref_s: dict
) -> dict | None:
  """Weight-space crossover of the champion with a child's best checkpoint
  (70/30 and 50/50); the best screened blend gets the full benchmark."""
  cands = []
  for r in (0.7, 0.5):
    out = BLENDS / f"{name}_x{int(r * 100)}.pt"
    subprocess.run(
      ["uv", "run", "python", "scripts/tools/blend_checkpoints.py", str(out),
       f"{champ['ck']}:{r}", f"{child_ck}:{1 - r}"],
      cwd=ROOT, capture_output=True,
    )  # fmt: skip
    s_ = screen(out) if out.exists() else None
    if s_ is not None:
      cands.append((screen_score(s_, ref_s), r, out))
      log(
        f"{name}: blend {r:.1f}/{1 - r:.1f} with champion, screen {screen_score(s_, ref_s):+.1f}"
      )
  cands.sort(key=lambda x: -x[0])
  if not cands or cands[0][0] <= -2.0:
    return None
  _, r, out = cands[0]
  bname = f"{name}_x{int(r * 100)}"
  m = bench(bname, str(out))
  if m is None:
    return None
  sc, reg = score(m, ref, anchor)
  log(f"{bname}: score {sc:+.2f} vs {champ['name']}, regressions {reg or 'none'}")
  entry = {
    "name": bname,
    "ck": str(out),
    "genes": champ["genes"],
    "score": round(sc, 2),
    "regressions": reg,
  }
  return entry


def confirm_and_install(entry: dict, champ: dict, anchor: dict) -> dict | None:
  """Second seed, two-seed mean vs the champion; on success install the
  checkpoint as a run directory (resumable) and export ONNX."""
  import torch

  m2 = bench(f"{entry['name']}_s2", entry["ck"], seed=2)
  m1 = json.loads((BENCH / f"{entry['name']}.json").read_text())
  if m2 is None:
    log(f"{entry['name']}: seed-2 benchmark failed")
    return None
  avg = {
    k: (m1[k] + m2[k]) / 2
    if m1.get(k) is not None and m2.get(k) is not None
    else m1.get(k)
    for k in m1
  }
  name2 = f"{entry['name']}_2seed"
  (BENCH / f"{name2}.json").write_text(json.dumps(avg, indent=2))
  ref = json.loads((BENCH / f"{champ['name']}.json").read_text())
  sc, reg = score(avg, ref, anchor)
  log(
    f"{name2}: two-seed score {sc:+.2f} vs {champ['name']}, regressions {reg or 'none'}"
  )
  if reg or sc <= 0:
    return None
  it = int(
    torch.load(entry["ck"], map_location="cpu", weights_only=False).get("iter", 0)
  )
  run_dir = LOGS / f"{time.strftime('%Y-%m-%d_%H-%M-%S')}_champ_{entry['name']}"
  run_dir.mkdir(parents=True, exist_ok=True)
  dst = run_dir / f"model_{it}.pt"
  shutil.copyfile(entry["ck"], dst)
  params = Path(champ["ck"]).parent / "params"
  if params.is_dir() and not (run_dir / "params").exists():
    shutil.copytree(params, run_dir / "params")
  onnx = (
    ROOT.parent
    / "k1_policy_runner"
    / "kick_loop_models"
    / f"k1_kick_loop_{entry['name']}.onnx"
  )
  subprocess.run(
    ["uv", "run", "python", "scripts/tools/export_onnx.py", "--checkpoint", str(dst), "--output", str(onnx)],
    cwd=ROOT, capture_output=True,
  )  # fmt: skip
  log(f"NEW CHAMPION {name2}: installed {dst.relative_to(ROOT)}, ONNX {onnx.name}")
  return {"name": name2, "ck": str(dst), "genes": entry["genes"], "score": round(sc, 2)}


def disk_ok() -> bool:
  st = os.statvfs(ROOT)
  return st.f_bavail * st.f_frsize > 20e9


def main() -> None:
  hours = (
    float(sys.argv[sys.argv.index("--hours") + 1]) if "--hours" in sys.argv else 10.0
  )
  stop_at = time.time() + hours * 3600
  random.seed()
  st = load_state()
  v56d = next(LOGS.glob("*_stage3_v56d")) / "model_13450.pt"
  v58 = next(LOGS.glob("*_stage3_v58")) / "model_14200.pt"
  # Baselines run in the background while the first child trains.
  base_jobs = []
  for bname, bck in ((ANCHOR, v56d), ("bhuman", None), ("v58_14200", v58)):
    if not (BENCH / f"{bname}.json").exists():
      base_jobs.append((bname, str(bck) if bck else None))
  chain = " && ".join(
    "uv run python scripts/tools/kick_benchmark.py run "
    + n
    + (" " + c if c else "")
    + " >/dev/null 2>&1"
    for n, c in base_jobs
  )
  env0 = {k: v for k, v in os.environ.items() if k != "KICK_GENES"}
  base_proc = subprocess.Popen(["bash", "-c", chain or "true"], cwd=ROOT, env=env0)
  if st["champion"] is None:
    defaults = {g: d for g, (_, _, d) in GENES.items()}
    v58_genes = dict(defaults, **V58_GENES_OFF)  # v58 had no K4 / K4b
    st["champion"] = {
      "name": "v58_14200",
      "ck": str(v58),
      "genes": v58_genes,
      "score": 0.0,
    }
    save_state(st)
    log(
      f"start: champion v58_14200, anchor {ANCHOR}; baselines benchmarking in background"
    )
  anchor: dict | None = None
  # Re-score the archive with the current metric rules (tolerances may change).
  if (BENCH / f"{ANCHOR}.json").exists():
    anc = json.loads((BENCH / f"{ANCHOR}.json").read_text())
    ref0 = json.loads((BENCH / f"{st['champion']['name']}.json").read_text())
    for e in st["archive"]:
      f = BENCH / f"{e['name']}.json"
      if f.exists():
        sc, reg = score(json.loads(f.read_text()), ref0, anc)
        e["score"], e["regressions"] = round(sc, 2), reg
        log(f"re-scored {e['name']}: {sc:+.2f}, regressions {reg or 'none'}")
    save_state(st)
  failures = 0
  while time.time() < stop_at and failures < 3:
    if not disk_ok():
      log("less than 20 GB free disk; stopping")
      break
    st["gen"] += 1
    name = f"evo_g{st['gen']:03d}"
    champ = st["champion"]
    # Generation 1 = the v60 recipe (RSI 10 % / 10 %, defaults elsewhere).
    if st["gen"] == 1:
      genes = {g: d for g, (_, _, d) in GENES.items()}
    elif (EVO / "next_genes.json").exists():
      # A queued experiment: exact genes from a file (consumed once).
      genes = dict(champ["genes"], **json.loads((EVO / "next_genes.json").read_text()))
      (EVO / "next_genes.json").rename(EVO / f"used_genes_{st['gen']:03d}.json")
      log(f"{name}: queued experiment genes")
    elif not st.get("control_done"):
      # Control: the champion's exact recipe, to measure how much plain
      # continued training moves the benchmark (noise / drift floor).
      genes = dict(champ["genes"])
      st["control_done"] = True
    else:
      genes = child_genes(st)
    diff = {k: v for k, v in genes.items() if champ["genes"].get(k) != v}
    log(f"{name}: parent {champ['name']}, changed genes {diff}")
    cks = train_child(name, Path(champ["ck"]), genes)
    if not cks:
      failures += 1
      log(f"{name}: no checkpoints (failure {failures}/3)")
      save_state(st)
      continue
    failures = 0
    if base_proc.poll() is None:
      log("waiting for baseline benchmarks")
      base_proc.wait()
    if anchor is None:
      anchor = bench(ANCHOR, str(v56d))
      if anchor is None or bench("v58_14200", str(v58)) is None:
        log("baseline benchmark failed; stopping")
        break
    ref = json.loads((BENCH / f"{champ['name']}.json").read_text())
    if "screen" not in st:
      log("screening the champion")
      st["screen"] = screen(Path(champ["ck"]))
      save_state(st)
    ref_s = (
      st["screen"]
      if st.get("screen_of") in (None, champ["name"])
      else screen(Path(champ["ck"]))
    )
    st["screen_of"] = champ["name"]
    st["screen"] = ref_s
    scored = []
    for ck in cks:
      sc_ = screen(ck)
      if sc_ is None or ref_s is None:
        continue
      scored.append((screen_score(sc_, ref_s), ck, sc_))
    scored.sort(key=lambda x: -x[0])
    summary = ", ".join(f"{c.stem.split('_')[1]}:{v:+.1f}" for v, c, _ in scored)
    log(f"{name}: screen vs champion {summary or 'none'}")
    cks = [c for v, c, _ in scored[:1] if v > -2.0]
    best_entry = None
    for ck in cks:
      cname = f"{name}_{ck.stem.split('_')[1]}"
      m = bench(cname, str(ck))
      if m is None:
        log(f"{cname}: benchmark failed")
        continue
      sc, reg = score(m, ref, anchor)
      entry = {
        "name": cname,
        "ck": str(ck),
        "genes": genes,
        "score": round(sc, 2),
        "regressions": reg,
      }
      st["archive"].append(entry)
      log(f"{cname}: score {sc:+.2f} vs {champ['name']}, regressions {reg or 'none'}")
      if not reg and sc > 0 and (best_entry is None or sc > best_entry["score"]):
        best_entry = entry
    if best_entry is None and scored:
      # The child alone did not win: try crossing it with the champion.
      best_entry = try_blends(name, champ, scored[0][1], ref, anchor, ref_s)
      if best_entry is not None:
        st["archive"].append(best_entry)
        if best_entry["regressions"] or best_entry["score"] <= 0:
          best_entry = None
    if best_entry is not None:
      new = confirm_and_install(best_entry, champ, anchor)
      if new is not None:
        st["champion"] = new
        st.pop("screen", None)
        st.pop("screen_of", None)
    save_state(st)
  log(
    f"stopped after generation {st['gen']} (time or failures); champion {st['champion']['name']}"
  )


if __name__ == "__main__":
  main()

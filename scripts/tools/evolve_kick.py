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
import fitness_v2  # noqa: E402

EVO = ROOT / "docs" / "evolution"
# Benchmark v2 (2026-10-07): deployed action path, fixed caps / perception /
# delay, every fall counted, CIs (scripts/tools/kick_bench2.py).
BENCH = ROOT / "docs" / "benchmarks_v2"
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
  "caps_temporal_coef": (0.8, 2.0, 1.0),
  "caps_near_ball_scale": (0.4, 1.0, 0.5),
  # Quiet steps (2026-10-08): flat-foot settle window and touchdown speed.
  "foot_flat_settle_s": (0.04, 0.12, 0.06),
  "w.touchdown_speed": (-40.0, -5.0, -15.0),
  # Cold starts (2026-10-09): share of resets standing still.
  "stand_start_prob": (0.1, 0.5, 0.25),
  # B-Human power cost (2026-10-09 review).
  "w.joint_power": (-0.005, 0.0, 0.0),
  "w.side_foot_strike": (0.0, 600.0, 0.0),
  # structural: template term weights (0 = term absent)
  "t.far_cap_tracking": (0.0, 12.0, 0.0),
  "t.long_power_ramp": (0.0, 3000.0, 0.0),
  "t.aim_tight": (0.0, 1200.0, 0.0),
  "t.upright_fast": (-3.0, 0.0, 0.0),
  "amp_kick_data": (0.0, 1.0, 1.0),
  "k.KICK_STYLE_AMP": (0.0, 1.0, 1.0),
  # Kick styles (2026-10-06): inside foot (B-Human) + hop; "when" = k.STYLE_MAP.
  "w.inside_foot_style": (0.0, 900.0, 0.0),
  "w.hop_kick_style": (0.0, 900.0, 0.0),
  "w.hop_kick_fall": (-2500.0, 0.0, 0.0),
  "k.STYLE_SHARE_INSIDE": (0.0, 0.8, 0.5),
  "k.STYLE_SHARE_HOP": (0.0, 0.5, 0.0),
  "k.INSIDE_YAW_STEP": (0.05, 0.3, 0.15),
  "k.SHORT_PLANT_FACTOR": (0.2, 1.0, 1.0),
  "t.quick_kick": (0.0, 900.0, 0.0),
  # time to kick (2026-10-07)
  "w.kick_time_cost": (-15.0, 0.0, 0.0),
  "k.PROMPT_KICK_TAU": (0.5, 2.0, 1.5),
  "k.PROMPT_FLOOR": (0.0, 0.5, 0.5),
  "w.turn_rate_track": (0.0, 20.0, 0.0),
  "w.long_kick_speed_linear": (0.0, 2000.0, 0.0),
  "w.style_advantage": (0.0, 1500.0, 0.0),
  "ball_mass_alpha_max": (0.458, 0.6, 0.458),
  "t.hop_power_long": (0.0, 1500.0, 0.0),
  "t.inside_accurate_short": (0.0, 900.0, 0.0),
}
# Categorical genes: (choices, default).
CATEGORICAL: dict[str, tuple[tuple[str, ...], str]] = {
  "k.STYLE_MAP": (("off", "range", "free"), "off"),
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
  # time to kick: an aimed kick soon after reaching the ball (near time < 1 s)
  "quick_kick": (
    {
      "mul": [
        {"sig": "kick_event"},
        {"exp_decay": [{"sig": "kick_near_time"}, 1.0]},
        {"gauss": [{"sig": "kick_aim_err"}, 0.0, 0.3]},
        {"sig": "kick_quality"},
      ]
    },
    400.0,
  ),
  # power: long hop kicks, 3D speed ramp 5 -> 9 m/s, aimed
  "hop_power_long": (
    {
      "mul": [
        {"sig": "kick_event"},
        {"sig": "kick_long"},
        {"sig": "kick_hop"},
        {"ramp": [{"sig": "kick_speed"}, 5.0, 9.0]},
        {"gauss": [{"sig": "kick_aim_err"}, 0.0, 0.25]},
      ]
    },
    800.0,
  ),
  # accuracy: short / medium inside-foot kicks, tight aim (sigma ~9 deg)
  "inside_accurate_short": (
    {
      "mul": [
        {"sig": "kick_event"},
        {"sig": "kick_short_medium"},
        {"sig": "kick_inside"},
        {"gauss": [{"sig": "kick_aim_err"}, 0.0, 0.15]},
      ]
    },
    400.0,
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


def literals(expr) -> int:
  """Number of numeric constants in a grammar expression (L1 shape genes)."""
  if isinstance(expr, (int, float)):
    return 1
  if isinstance(expr, dict):
    ((op, arg),) = expr.items()
    if op == "sig":
      return 0
    return sum(literals(a) for a in (arg if isinstance(arg, list) else [arg]))
  return 0


def shaped(expr, factors: list[float], i: list[int] | None = None):
  """Copy of expr with its numeric constants scaled by factors (in order)."""
  i = [0] if i is None else i
  if isinstance(expr, (int, float)):
    f = factors[i[0]] if i[0] < len(factors) else 1.0
    i[0] += 1
    return float(expr) * float(f)
  ((op, arg),) = expr.items()
  if op == "sig":
    return expr
  if isinstance(arg, list):
    return {op: [shaped(a, factors, i) for a in arg]}
  return {op: shaped(arg, factors, i)}


def write_program(name: str, genes: dict) -> str | None:
  terms = []
  for t, (expr, _) in TEMPLATES.items():
    w = float(genes.get(f"t.{t}", 0.0))
    if w != 0.0:
      # L1 shape genes "ts.<template>": factors on the template's constants.
      f = genes.get(f"ts.{t}")
      terms.append({"name": f"tpl_{t}", "expr": shaped(expr, f) if f else expr, "weight": w})
  # Free-form grammar terms proposed by L4 / L5 (validated by the proposer).
  terms += list(genes.get("_extra_terms", []))
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
STEPS = (150, 250, 350, 450, 500)  # screened (v2 screen ~2 min each); best gets the full benchmark


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
  """Full v2 benchmark (cached as BENCH/name.json, resumable)."""
  out = BENCH / f"{name}.json"
  args = ["uv", "run", "python", "scripts/tools/kick_bench2.py", "run", name,
          ck or "bhuman", "--size", "full"]  # fmt: skip
  env = {k: v for k, v in os.environ.items() if k != "KICK_GENES"}
  env["BENCH2_SEED"] = str(seed)
  subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True)
  if not out.exists():
    return None
  m = json.loads(out.read_text())
  return m if len([k for k in m if not k.startswith("_")]) >= 6 else None


def score(m: dict, ref: dict, anchor: dict | None = None) -> tuple[float, list[str]]:
  """v2 fitness (fitness_v2.score): primary objectives x3, safety x2, rest x1,
  +2 per kick-league metric newly beating B-Human with separated CIs; and the
  regressions (worse by more than the tolerance with separated CIs). The
  anchor argument is unused in v2."""
  bh_p = BENCH / "bhuman.json"
  bh = json.loads(bh_p.read_text()) if bh_p.exists() else None
  return fitness_v2.score(m, ref, bh)


def screen(ck: Path) -> dict | None:
  """v2 screen (~2 min): near-ball grid (camera), approach (camera), loop."""
  name = f"screen_{ck.parent.name}_{ck.stem}"
  out = BENCH / "screens" / f"{name}.json"
  # Re-run when the screen gained tracks (run_all only adds missing ones).
  have = set(json.loads(out.read_text())) if out.exists() else set()
  if not out.exists() or not SCREEN_KEYS <= have:
    env = {k: v for k, v in os.environ.items() if k != "KICK_GENES"}
    subprocess.run(
      ["uv", "run", "python", "scripts/tools/kick_bench2.py", "run", f"screens/{name}",
       str(ck), "--size", "screen"],
      cwd=ROOT, env=env, capture_output=True, text=True,
    )  # fmt: skip
  if not out.exists():
    return None
  m = json.loads(out.read_text())
  return m if len([k for k in m if not k.startswith("_")]) >= 3 else None


# Track keys of kick_bench2.plan("screen"); keep in sync.
SCREEN_KEYS = {
  "near_grid/camera/typical",
  "near_grid/large/camera/typical",
  "approach/camera/typical",
  "approach/behind/world/typical",
  "full_loop/camera/typical",
}


def screen_score(s: dict, ref: dict) -> float:
  return fitness_v2.score(s, ref)[0]


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
  for g, (choices, dflt) in CATEGORICAL.items():
    if elites and random.random() < 0.25:
      genes[g] = random.choice(elites)["genes"].get(g, genes.get(g, dflt))
    if random.random() < 0.15:
      genes[g] = random.choice([c for c in choices if c != genes.get(g, dflt)])
      n_mut += 1
  if genes.get("k.STYLE_MAP", "off") != "off":
    # A styled child needs its style terms live.
    for w, v in (("w.inside_foot_style", 300.0), ("w.hop_kick_style", 300.0), ("w.hop_kick_fall", -1000.0)):
      if float(genes.get(w, 0.0)) == 0.0:
        genes[w] = v
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
  return {k: (round(v, 4) if isinstance(v, (int, float)) else v) for k, v in genes.items()}


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
        # Checkpoints are saved at multiples of the save interval (50), not
        # at parent + step (parent 17149 -> 17150, 17200, ...; 2026-10-07 fix).
        got = [dirs[-1] / f"model_{-(-(it0 + s) // 50) * 50}.pt" for s in STEPS]
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
  for r in (0.7, 0.5, 0.3):
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


RSW = BENCH / "runswift"
HARNESS = ROOT / ".cache" / "runswift_harness"
RSW_ASSETS = ROOT / ".cache" / "bench2_assets"
# runswift soft gate (user 2026-10-07): a proxy reference, not the main fitness.
# A candidate may be a little worse where the fixture's ideal assumptions
# matter, but not on the critical features: falls, accuracy, kick speed.
RSW_TOL = {"goal_falls": 4, "near_ok": 6, "long_speed": 0.15}


def _rsw_long_speed(name: str) -> float | None:
  """Median strongest foot-linked kick speed on runswift's 6 / 9 m tasks only
  (user 2026-10-08: kick speed is judged where power matters; the 3 m passes
  should be soft and are judged by accuracy)."""
  import statistics

  vals = []
  for f in (RSW / f"{name}_near" / "peter").glob("*/results.json"):
    for t in json.loads(f.read_text())["trials"]:
      v = t.get("strongest_foot_linked_speed_m_s")
      if t["case"]["name"].startswith("range") and v is not None:
        vals.append(v)
  return statistics.median(vals) if vals else None


def runswift_proxy(name: str, ck: str) -> dict | None:
  """runswift's harness (near-ball grid + goal grid, light and heavy ball) on
  the candidate's ONNX through k1_policy_runner; summary cached in RSW/."""
  out = RSW / f"{name}.json"
  if out.exists():
    return json.loads(out.read_text())
  RSW.mkdir(parents=True, exist_ok=True)
  onnx = RSW / f"{name}.onnx"
  subprocess.run(
    ["uv", "run", "python", "scripts/tools/export_onnx.py", "--checkpoint", str(ck), "--output", str(onnx)],
    cwd=ROOT, capture_output=True,
  )  # fmt: skip
  if not onnx.exists():
    return None
  rl = ROOT.parent
  env = dict(os.environ, KC_ONNX=str(onnx), PYTHONPATH=str(HARNESS))
  env.pop("KICK_GENES", None)
  py = str(ROOT / ".venv" / "bin" / "python")
  res = {}
  for track, args in (
    ("near", ["compare.py", "--policy", "peter", "--suite", "full", "--repeats", "3"]),
    ("goal", ["goal_grid.py", "--policy", "peter", "--suite", "grid",
              "--grid-file", str(rl / "runswift/benchmarks/results/2026-10-02/k1-score-grid/manifest.json"),
              "--evaluator-file", str(rl / "runswift/src/behaviour/examples/booster_match/score_evaluator.py")]),
  ):  # fmt: skip
    o = RSW / f"{name}_{track}"
    if not (o / "summary.json").exists():
      shutil.rmtree(o, ignore_errors=True)
      subprocess.run(
        [py, *args, "--assets", str(RSW_ASSETS), "--ball-profile", "both", "--workers", "16", "--output", str(o)],
        cwd=HARNESS, env=env, capture_output=True,
      )  # fmt: skip
    if not (o / "summary.json").exists():
      return None
    res[track] = json.loads((o / "summary.json").read_text())["rows"]
  n, g = res["near"], res["goal"]
  d = {
    "near_ok": sum(r["on_direction_launch"] for r in n),
    "near_planned": sum(r["planned"] for r in n),
    "first_strike_speed": sum(r["median_launch_speed_m_s"] for r in n) / len(n),
    "strongest_speed": sum(r["median_strongest_foot_linked_speed_m_s"] for r in n) / len(n),
    "goal_falls": sum(r["falls_during_attempt"] for r in g),
    "goals": sum(r["goals"] for r in g),
    "goal_planned": sum(r["planned"] for r in g),
    "long_speed": _rsw_long_speed(name),
  }
  out.write_text(json.dumps(d, indent=1))
  return d


def runswift_gate(name: str, ck: str, champ: dict) -> tuple[bool, str]:
  cand = runswift_proxy(name, ck)
  ref_p = RSW / f"{champ['name']}.json"
  ref = json.loads(ref_p.read_text()) if ref_p.exists() else runswift_proxy(champ["name"], champ["ck"])
  if cand is None or ref is None:
    return True, "runswift proxy unavailable (not gating)"
  bad = []
  if cand["goal_falls"] > ref["goal_falls"] + RSW_TOL["goal_falls"]:
    bad.append(f"falls {ref['goal_falls']} -> {cand['goal_falls']}")
  if cand["near_ok"] < ref["near_ok"] - RSW_TOL["near_ok"]:
    bad.append(f"first strike <= 15 deg {ref['near_ok']} -> {cand['near_ok']}")
  for d_, n_ in ((cand, name), (ref, champ["name"])):
    if d_.get("long_speed") is None:
      d_["long_speed"] = _rsw_long_speed(n_) or _rsw_long_speed(n_.replace("_2seed", ""))
  if None not in (cand.get("long_speed"), ref.get("long_speed")) and (
    cand["long_speed"] < ref["long_speed"] - RSW_TOL["long_speed"]
  ):
    bad.append(f"6/9 m kick speed {ref['long_speed']:.2f} -> {cand['long_speed']:.2f}")
  msg = (f"runswift: falls {cand['goal_falls']}/{cand['goal_planned']} (champ {ref['goal_falls']}),"
         f" first strike {cand['near_ok']}/{cand['near_planned']} (champ {ref['near_ok']}),"
         f" 6/9 m kick speed {cand.get('long_speed') or float('nan'):.2f} (champ {ref.get('long_speed') or float('nan'):.2f}),"
         f" goals {cand['goals']} (champ {ref['goals']})")  # fmt: skip
  return (not bad), msg + (f"; BLOCKED: {bad}" if bad else "")


def confirm_and_install(entry: dict, champ: dict, anchor: dict | None = None) -> dict | None:
  """v2: second-seed full benchmark; both seeds must be free of regressions
  and their summed score positive. Then install as a resumable run directory
  and export ONNX."""
  import torch

  m2 = bench(f"{entry['name']}_s2", entry["ck"], seed=2)
  m1 = json.loads((BENCH / f"{entry['name']}.json").read_text())
  if m2 is None:
    log(f"{entry['name']}: seed-2 benchmark failed")
    return None
  ref = json.loads((BENCH / f"{champ['name']}.json").read_text())
  ref2_p = BENCH / f"{champ['name']}_s2.json"
  ref2 = json.loads(ref2_p.read_text()) if ref2_p.exists() else ref
  sc1, reg1 = score(m1, ref)
  sc2, reg2 = score(m2, ref2)
  reg = sorted(set(reg1) | set(reg2))
  sc = sc1 + sc2
  name2 = f"{entry['name']}_2seed"
  log(f"{name2}: seed scores {sc1:+.2f} / {sc2:+.2f} vs {champ['name']}, regressions {reg or 'none'}")
  if reg or sc <= 0:
    return None
  ok, msg = runswift_gate(entry["name"], entry["ck"], champ)
  log(f"{entry['name']}: {msg}")
  if not ok:
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
  for src, dst_name in ((f"{entry['name']}.json", f"{name2}.json"), (f"{entry['name']}_s2.json", f"{name2}_s2.json")):
    if (BENCH / src).exists():
      shutil.copyfile(BENCH / src, BENCH / dst_name)
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
  st.pop("screen", None)  # re-screen the champion with the current screen fields
  if st["champion"] is None or not (BENCH / f"{st['champion']['name']}.json").exists():
    log("v2: champion has no v2 benchmark; set state.json champion first")
    return
  bh_job = None
  if not (BENCH / "bhuman.json").exists():
    bh_job = subprocess.Popen(
      ["uv", "run", "python", "scripts/tools/kick_bench2.py", "run", "bhuman", "bhuman", "--size", "full"],
      cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )  # fmt: skip
  anchor: dict = {}
  failures = 0
  while time.time() < stop_at and failures < 3:
    if not disk_ok():
      log("less than 20 GB free disk; stopping")
      break
    st["gen"] += 1
    name = f"evo_g{st['gen']:03d}"
    champ = st["champion"]
    seed = None
    seeds_p = EVO / "seed_runs.json"
    if seeds_p.exists():
      # Externally trained candidates (e.g. the kick-style runs): screened and
      # benchmarked like a child, no training.
      seeds = json.loads(seeds_p.read_text())
      seed = seeds.pop(0) if seeds else None
      if seeds:
        seeds_p.write_text(json.dumps(seeds, indent=2))
      else:
        seeds_p.rename(EVO / f"used_seed_runs_{st['gen']:03d}.json")
    if seed is not None:
      name = seed["name"]
      genes = dict(champ["genes"], **seed["genes"])
      log(f"{name}: external candidate, {len(seed['cks'])} checkpoints")
    # Generation 1 = the v60 recipe (RSI 10 % / 10 %, defaults elsewhere).
    if seed is not None:
      pass
    elif st["gen"] == 1:
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
    cks = (
      [Path(c) for c in seed["cks"] if Path(c).exists()]
      if seed is not None
      else train_child(name, Path(champ["ck"]), genes)
    )
    if not cks:
      failures += 1
      log(f"{name}: no checkpoints (failure {failures}/3)")
      save_state(st)
      continue
    failures = 0
    if bh_job is not None and bh_job.poll() is None:
      log("waiting for the B-Human v2 benchmark")
      bh_job.wait()
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

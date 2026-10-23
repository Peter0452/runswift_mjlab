"""Read-only checkpoint/run inventory for the runswift_mjlab keep-list."""

import csv, json, os, re, sys, time
from collections import defaultdict
from pathlib import Path

REPO = Path("/home/peter/Desktop/Project/RL/runswift_mjlab")
RUNNER = Path("/home/peter/Desktop/Project/RL/k1_policy_runner")
MEM = Path("/home/peter/.claude/projects/-home-peter-Desktop-Project-RL/memory")
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "restructure"
ACTIVE_SINCE = time.mktime((2026, 10, 20, 0, 0, 0, 0, 0, -1))
TS = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_")
STEP = re.compile(r"model_(\d+)\.pt$")

# ---------- inventory of checkpoints ----------
LOGS = REPO / "logs/rsl_rl"
ckpts = {}  # rel path -> dict
runs = {}   # run rel (exp/run) -> dict
for exp in sorted(LOGS.iterdir()):
  if not exp.is_dir():
    continue
  for p in sorted(exp.iterdir()):
    if p.is_file() and p.suffix == ".pt":  # standalone .pt at exp level
      key = f"{exp.name}/_loose"
      runs.setdefault(key, {"exp": exp.name, "run": "_loose", "dir": exp, "ckpts": []})
      runs[key]["ckpts"].append(p)
    elif p.is_dir():
      key = f"{exp.name}/{p.name}"
      pts = [q for q in p.rglob("*.pt") if q.is_file() and not q.is_symlink()]
      runs[key] = {"exp": exp.name, "run": p.name, "dir": p, "ckpts": pts}
for key, r in runs.items():
  r["short"] = TS.sub("", r["run"])
  r["mtime"] = max([os.path.getmtime(q) for q in r["ckpts"]] + [os.path.getmtime(r["dir"])])
  r["active"] = r["mtime"] >= ACTIVE_SINCE
  def order(q):
    m = STEP.search(q.name)
    return (1, int(m.group(1))) if m else (0, os.path.getmtime(q))
  r["ckpts"].sort(key=order)
  for q in r["ckpts"]:
    m = STEP.search(q.name)
    ckpts[str(q.relative_to(REPO))] = {
      "run": key, "file": q.name, "step": int(m.group(1)) if m else None,
      "size": q.stat().st_size, "reasons": set(),
    }
  if r["ckpts"] and r["run"] not in ("_loose", "blends"):
    ckpts[str(r["ckpts"][-1].relative_to(REPO))]["reasons"].add("latest of run")

by_dirname = defaultdict(list)
for key, r in runs.items():
  by_dirname[r["run"]].append(key)
by_short = defaultdict(list)
for key, r in runs.items():
  by_short[r["short"]].append(key)

def ck_in(run_key, step=None, fname=None):
  r = runs[run_key]
  for q in r["ckpts"]:
    if fname and q.name == fname:
      return str(q.relative_to(REPO))
    if step is not None and q.name == f"model_{step}.pt":
      return str(q.relative_to(REPO))
  return None

# ---------- reference corpus ----------
def texts():
  pats = [
    (REPO / "docs", ("*.md", "*.json", "*.yaml", "*.log", "*.txt")),
    (REPO / "checkpoints", ("*.md",)),
    (REPO / "scripts", ("*.py", "*.sh", "*.md", "*.yaml")),
    (REPO / "src", ("*.py",)),
    (REPO / "tests", ("*.py",)),
    (MEM, ("*.md",)),
  ]
  for root, globs in pats:
    for g in globs:
      for f in root.rglob(g):
        if "__pycache__" in f.parts or f.stat().st_size > 5_000_000:
          continue
        yield f, label(f)
  for f in LOGS.glob("*/*/params/*.yaml"):
    yield f, "parent of " + "/".join(f.parts[-4:-2])
  for f in LOGS.glob("*/*/*.json"):
    yield f, "run metadata"
  for f in LOGS.glob("*/*.json"):
    yield f, "exp metadata"
  for d in ("dribble_eval", "controller_eval", "selfplay_eval", "kick_kinematics"):
    for f in (REPO / "logs" / d).rglob("*"):
      if f.is_file() and f.suffix in (".json", ".md", ".txt", ".csv", ".log") and f.stat().st_size < 5_000_000:
        yield f, f"eval output ({d})"
  for f in RUNNER.rglob("*"):
    if "build" in f.parts or ".git" in f.parts or not f.is_file():
      continue
    if f.suffix in (".py", ".yaml", ".yml", ".json", ".md", ".sh", ".txt") and f.stat().st_size < 2_000_000:
      yield f, "k1_policy_runner config/code"

def label(f):
  s = str(f)
  if s.startswith(str(MEM)): return "memory note"
  if "checkpoints/README" in s: return "curated checkpoints/README"
  if "docs/evolution/state.json" in s: return "evolution state (champion/archive)"
  if "docs/evolution" in s: return "evolution records"
  if "docs/experience" in s: return "experience repo"
  if "docs/benchmarks" in s: return "benchmark result"
  if "/docs/" in s: return "K1 notes/docs"
  if "/scripts/" in s: return "script"
  if "/src/" in s: return "code default"
  if "/tests/" in s: return "test"
  return "other"

PT_PATH = re.compile(r"[\w./+=-]+\.pt\b")
mentions = defaultdict(set)  # run_key -> reasons (name mentioned without step)
for f, lab in texts():
  try:
    t = f.read_text(errors="ignore")
  except Exception:
    continue
  # 1. explicit checkpoint paths
  for m in PT_PATH.findall(t):
    parts = m.split("/")
    fname = parts[-1]
    cands = []
    if len(parts) >= 2 and parts[-2] in by_dirname:
      cands = by_dirname[parts[-2]]
    elif len(parts) >= 2 and parts[-2] in runs and False:
      pass
    for rk in cands:
      c = ck_in(rk, fname=fname)
      if c:
        ckpts[c]["reasons"].add(lab)
  # 2. run name mentions (+ step)
  for short, rks in by_short.items():
    if len(short) < 6 or not re.search(r"\d|_", short) or short in ("blends", "_loose"):
      continue
    if short not in t:
      continue
    for mm in re.finditer(r"(?<![\w])" + re.escape(short) + r"(?:[ _/@:-]*(?:model_|iter |it )?(\d{3,6}))?(?![\w])", t):
      step = mm.group(1)
      for rk in rks:
        if step and (c := ck_in(rk, step=int(step))):
          ckpts[c]["reasons"].add(lab)
        else:
          mentions[rk].add(lab)

# ---------- deployed ONNX in k1_policy_runner ----------
deployed, unmatched = [], []
for f in sorted(RUNNER.rglob("*.onnx")):
  if "build" in f.parts:
    continue
  stem = f.stem
  sub = f.parent.name
  exps = {
    "kick_loop_models": ["k1_kick_stage3_amp", "k1_kick_selfplay_amp", "blends"],
    "dribble_models": ["k1_dribble_amp"],
    "amp_models": [e for e in {r["exp"] for r in runs.values()} if e.startswith("k1_velocity_amp")],
  }.get(sub)
  allowed = [rk for rk, r in runs.items() if exps is None or r["exp"] in exps]
  live = [rk for rk in allowed if "ABORTED" not in runs[rk]["run"]] or allowed
  name = re.sub(r"^k1_(kick_loop_|dribble_)?", "", stem)
  hit, how = None, "deployed ONNX (k1_policy_runner)"
  if name in by_dirname or name in by_short:  # exported under its run name
    rk = (by_dirname.get(name) or by_short[name])[0]
    hit = str(runs[rk]["ckpts"][-1].relative_to(REPO)) if runs[rk]["ckpts"] else None
  m = re.match(r"^(.*?)_?(?:model_)?(\d{3,6})(?:-(\d+))?$", name)
  if not hit and m:
    base, step = m.group(1), int(m.group(3) or m.group(2))
    cands = [rk for rk in live if base and (runs[rk]["short"] == base or runs[rk]["short"].endswith(base))]
    for rk in sorted(cands, key=lambda k: runs[k]["short"] != base):
      if (c := ck_in(rk, step=step)):
        hit = c
        break
    if not hit:  # same version token + step (ONNX renamed on export)
      tok = re.findall(r"v\d+[a-z]?", base)
      if tok:
        for rk in live:
          if runs[rk]["short"].endswith(tok[-1]) and (c := ck_in(rk, step=step)):
            hit, how = c, "deployed ONNX (match by version+step)"
            break
  generic = {"deploy", "flat", "k1", "model", "blend"}
  want = set(re.split(r"[_\- ]", name)) - generic - {""}
  weak = all(w.isdigit() for w in want) and exps is None
  if (not hit or "swa" in want) and not weak:  # SWA / blend files: name tokens within run+file tokens
    best = None
    for rk in live:
      rt = set(re.split(r"[_\-]", runs[rk]["short"]))
      for q in runs[rk]["ckpts"]:
        ft = set(re.split(r"[_\-]", q.stem))
        if want and want <= (rt | ft):
          score = len(want & ft)
          if best is None or score > best[0]:
            best = (score, str(q.relative_to(REPO)))
    if best and hit and best[1] != hit:  # SWA output as well as its source run
      ckpts[best[1]]["reasons"].add("deployed ONNX (match by name tokens)")
      deployed.append((str(f.relative_to(RUNNER)), best[1], "deployed ONNX (match by name tokens)"))
    elif best and not hit:
      hit, how = best[1], "deployed ONNX (match by name tokens)"
  if not hit and m and not weak:  # unique step within the allowed experiments
    step = int(m.group(3) or m.group(2))
    any_c = [c for rk in live if (c := ck_in(rk, step=step))]
    if len(any_c) == 1:
      hit, how = any_c[0], "deployed ONNX (probable: unique step)"
  rel = str(f.relative_to(RUNNER))
  if hit:
    ckpts[hit]["reasons"].add(how)
    deployed.append((rel, hit, how))
  else:
    unmatched.append(rel)

# ---------- best by training reward (restructure/best_ckpt.py) ----------
best_csv = REPO / "restructure/best.csv"
if best_csv.exists():
  for row in csv.DictReader(open(best_csv)):
    if row["best_ckpt"] in ckpts:
      ckpts[row["best_ckpt"]]["reasons"].add("best (peak training reward)")

# ---------- decisions ----------
for c, d in ckpts.items():
  r = runs[d["run"]]
  if r["active"]:
    d["decision"] = "KEEP (active run)"
  elif d["reasons"]:
    d["decision"] = "KEEP"
  elif r["run"] in ("blends", "_loose") or r["short"].startswith(("swa_", "blend", "warmstart")):
    d["decision"] = "ASK (unreferenced blend/SWA)"
  else:
    d["decision"] = "PRUNE (intermediate, unreferenced)"

OUT.mkdir(parents=True, exist_ok=True)
with open(OUT / "checkpoints.csv", "w", newline="") as fh:
  w = csv.writer(fh)
  w.writerow(["path", "size_mb", "decision", "reasons"])
  for c, d in sorted(ckpts.items()):
    w.writerow([c, f"{d['size']/1e6:.1f}", d["decision"], "; ".join(sorted(d["reasons"]))])

notable_labels = {"evolution state (champion/archive)", "curated checkpoints/README", "memory note",
                  "deployed ONNX (k1_policy_runner)", "deployed ONNX (match by version+step)", "deployed ONNX (match by name tokens)", "deployed ONNX (probable: unique step)", "K1 notes/docs", "evolution records", "experience repo"}
rows = []
for rk, r in sorted(runs.items()):
  cs = [ckpts[str(q.relative_to(REPO))] for q in r["ckpts"]]
  keep = [c for c in cs if not c["decision"].startswith("PRUNE")]
  reasons = set().union(*[c["reasons"] for c in cs]) | mentions[rk]
  reasons.discard("latest of run")
  notable = sorted(reasons & notable_labels)
  rows.append({
    "exp": r["exp"], "run": r["run"], "date": time.strftime("%m-%d", time.localtime(r["mtime"])),
    "n_ckpt": len(cs), "n_keep": len(keep),
    "size_gb": sum(c["size"] for c in cs) / 1e9, "keep_gb": sum(c["size"] for c in keep) / 1e9,
    "status": "ACTIVE" if r["active"] else ("NOTABLE" if notable else ("REFERENCED" if reasons else "PLAIN")),
    "why": "; ".join(sorted(reasons))[:300],
  })
with open(OUT / "runs.csv", "w", newline="") as fh:
  w = csv.DictWriter(fh, fieldnames=list(rows[0]))
  w.writeheader()
  for row in rows:
    w.writerow({k: (f"{v:.3f}" if isinstance(v, float) else v) for k, v in row.items()})

summary = {
  "n_runs": len(runs), "n_ckpts": len(ckpts),
  "total_gb": sum(d["size"] for d in ckpts.values()) / 1e9,
  "by_decision": {},
  "by_status": {},
  "deployed_matched": len(deployed), "deployed_unmatched": unmatched, "deployed": deployed,
  "by_exp": {},
}
for d in ckpts.values():
  b = summary["by_decision"].setdefault(d["decision"], [0, 0.0])
  b[0] += 1; b[1] += d["size"] / 1e9
for row in rows:
  summary["by_status"][row["status"]] = summary["by_status"].get(row["status"], 0) + 1
  e = summary["by_exp"].setdefault(row["exp"], {"runs": 0, "ckpts": 0, "gb": 0.0, "keep": 0, "keep_gb": 0.0, "active": 0, "notable": 0})
  e["runs"] += 1; e["ckpts"] += row["n_ckpt"]; e["gb"] += row["size_gb"]
  e["keep"] += row["n_keep"]; e["keep_gb"] += row["keep_gb"]
  e["active"] += row["status"] == "ACTIVE"; e["notable"] += row["status"] == "NOTABLE"
(OUT / "summary.json").write_text(json.dumps(summary, indent=1))
print(json.dumps({k: v for k, v in summary.items() if k not in ("by_exp", "deployed")}, indent=1))
for e, v in sorted(summary["by_exp"].items(), key=lambda kv: -kv[1]["gb"]):
  print(f"{e:50s} runs={v['runs']:3d} act={v['active']:2d} notable={v['notable']:3d} ckpts={v['ckpts']:5d} {v['gb']:5.1f}GB -> keep {v['keep']:4d} {v['keep_gb']:5.2f}GB")

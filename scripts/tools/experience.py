"""Experience repository for the K1 kick work (2026-10-07).

Every experiment - an evolution child or frame, a manual run, a benchmark
finding, a robot test - is one record in docs/experience/experiences.jsonl
(append-only, one JSON object per line):

  id, time, source (hier | evolve | manual | robot | bench), level (L0-L5 or -)
  context  what was true before: parent policy and checkpoint, champion,
           benchmark version, deployment settings, scenario, genes in force
  action   what was changed: description, gene / program diff, code change,
           hypothesis (why it should help)
  result   what came out: checkpoints, screen / benchmark names, fitness score,
           regressions, promoted or not, raw notes
  impact   what it did to the objectives: per-metric deltas vs the parent with
           a verdict (better / worse / tie by 95 % CIs), tags
  lesson   optional text: what to keep in mind next time

Tools (also used by the evolution loops):
  python scripts/tools/experience.py sync          # import loop history not yet recorded
  python scripts/tools/experience.py add FILE.json # add records written by hand
  python scripts/tools/experience.py query [--gene G] [--level L] [--tag T] [--text S]
  python scripts/tools/experience.py stats         # what each kind of action did
  python scripts/tools/experience.py report        # docs/experience/README.md
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "tools"))
import fitness_v2  # noqa: E402

REPO = ROOT / "docs" / "experience"
DB = REPO / "experiences.jsonl"
EVO = ROOT / "docs" / "evolution"
BENCH2 = ROOT / "docs" / "benchmarks_v2"


# The user's objectives (memory: k1-kick-objectives, benchmark-gated-adoption).
# Every experience's impact is read against these; metric -> objective below.
OBJECTIVES = {
  "accuracy": "kicks on target (first touch within 15 deg, kicks within 20 deg, goals)",
  "time_to_kick": "kick quickly once at the ball (first kick time / share)",
  "power_by_range": "short passes stop near the target, long kicks as hard as possible",
  "speed_caps": "run at the speed caps (cap use, approach speed)",
  "posture": "upright ~0.52 m, no lean, smooth (height, pitch, action rate)",
  "safety": "few falls in every situation, torque within limits",
  "style_selection": "keep every kick style (front, inside, hop, ...) and use the best one for each situation",
  "beat_bhuman": "beat B-Human convincingly on the kick league, then keep improving",
  "no_regression": "never trade away an objective already built up",
  "deployable": "one end-to-end policy, deployed path (runner clip, lost rule), 83 inputs",
}
METRIC_OBJECTIVE = {
  "first_touch_15_pct": "accuracy", "kicks_20_pct": "accuracy", "goal_pct": "accuracy",
  "first_kick_20_pct": "accuracy", "goals_per_ep": "accuracy",
  "first_kick_s": "time_to_kick", "first_kick_pct": "time_to_kick",
  "long_3d": "power_by_range", "long_x_needed": "power_by_range",
  "short_stop_m": "power_by_range", "first_touch_speed": "power_by_range",
  "cap_use": "speed_caps", "approach_vx": "speed_caps",
  "fast_height_m": "posture", "fast_pitch_deg": "posture", "action_rate": "posture",
  "fall_pct": "safety", "fall_pct_behind": "safety", "torque_sat_pct": "safety",
  "knee_peak_at_kick": "safety",
  "style_selection_pct": "style_selection", "style_repertoire": "style_selection",
}  # fmt: skip


def objective_view(rec: dict) -> dict:
  """Objective -> 'better' / 'worse' / 'mixed' / 'tie' from an impact."""
  per: dict = {}
  for k, v in rec.get("impact", {}).get("metrics", {}).items():
    obj = METRIC_OBJECTIVE.get(k.split(":")[1])
    if obj:
      per.setdefault(obj, set()).add(v["verdict"])
  for t in rec.get("impact", {}).get("tags", []):
    m = t.split(":")[0]
    obj = METRIC_OBJECTIVE.get(m)
    if obj is None:
      for key, o in METRIC_OBJECTIVE.items():
        if key in m:
          obj = o
    if obj is None:  # benchmark v1 names
      for frag, o in (("goals", "accuracy"), ("aim", "accuracy"), ("on_target", "accuracy"),
                      ("first_kick", "time_to_kick"), ("kick_pct", "time_to_kick"),
                      ("3d", "power_by_range"), ("needed", "power_by_range"),
                      ("stop", "power_by_range"), ("air15", "power_by_range"),
                      ("caps", "speed_caps"), ("vx", "speed_caps"),
                      ("height", "posture"), ("lean", "posture"),
                      ("fall", "safety"), ("knee", "safety"), ("hip", "safety"),
                      ("planted", "safety"), ("search", "accuracy")):  # fmt: skip
        if frag in m:
          obj = o
          break
    if obj and ":" in t:
      per.setdefault(obj, set()).add("better" if "better" in t else "worse" if "worse" in t else "tie")
  out = {}
  for obj, vs in per.items():
    vs = vs - {"tie"}
    out[obj] = "mixed" if len(vs) > 1 else (vs.pop() if vs else "tie")
  return out


def load() -> list[dict]:
  if not DB.exists():
    return []
  return [json.loads(line) for line in DB.read_text().splitlines() if line.strip()]


def append(rec: dict) -> dict:
  REPO.mkdir(parents=True, exist_ok=True)
  known = {r["id"] for r in load()}
  if rec["id"] in known:
    return rec
  rec.setdefault("time", time.strftime("%Y-%m-%d %H:%M"))
  for k in ("context", "action", "result", "impact"):
    rec.setdefault(k, {})
  with DB.open("a") as f:
    f.write(json.dumps(rec) + "\n")
  return rec


def git_rev() -> str:
  try:
    return subprocess.run(
      ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
  except Exception:  # noqa: BLE001
    return ""


def deployment_context() -> dict:
  """Deployment-relevant training defaults in force (stage-3 env)."""
  return {
    "torque_clip": "B-Human 50/50/30/60/30/30",
    "deploy_target_clip": True,
    "motor_delay": "0-40 ms",
    "ball_origin": "feet, 2 cm jitter",
    "runner_lost_rule": True,
    "bench": "v2",
  }


def impact(child: dict, parent: dict) -> dict:
  """Per-metric deltas of two v2 results (fitness_v2 metric list)."""
  out, tags = {}, set()
  for key, metric, hib, _tol, _w in fitness_v2.METRICS:
    for cap in ("low", "high"):
      a = child.get(key, {}).get(metric, {}).get(cap)
      b = parent.get(key, {}).get(metric, {}).get(cap)
      if not a or not b or not a[3] or not b[3]:
        continue
      d = a[0] - b[0]
      better = (a[1] > b[2]) if hib else (a[2] < b[1])
      worse = (a[2] < b[1]) if hib else (a[1] > b[2])
      v = "better" if better else "worse" if worse else "tie"
      out[f"{key}:{metric}:{cap}"] = {"delta": round(d, 4), "verdict": v}
      if v != "tie":
        tags.add(f"{metric}:{v}")
  return {"metrics": out, "tags": sorted(tags),
          "n_better": sum(v["verdict"] == "better" for v in out.values()),
          "n_worse": sum(v["verdict"] == "worse" for v in out.values())}  # fmt: skip


def bench2(name: str) -> dict | None:
  p = BENCH2 / f"{name}.json"
  return json.loads(p.read_text()) if p.exists() else None


# ---------------------------------------------------------------------------
# Importers


def record_frame(rec: dict, champ: dict, child_name: str | None, child_genes: dict) -> dict:
  """Called by evolve_hier after each frame (also used by sync)."""
  parent_m = bench2(champ["name"])
  child_m = bench2(child_name) if child_name else None
  return append({
    "id": f"hier/{rec['id']}",
    "source": "hier",
    "level": rec["level"],
    "context": {"parent": champ["name"], "parent_ck": champ.get("ck"),
                "parent_genes": champ.get("genes"), "git": git_rev(),
                "deployment": deployment_context()},
    "action": {"desc": rec["desc"], "genes": rec.get("genes"), "atom": rec.get("atom"),
               "child_genes": child_genes},
    "result": {k: rec.get(k) for k in ("screen", "score", "regressions", "promoted", "blend", "result")}
              | {"bench": child_name},
    "impact": impact(child_m, parent_m) if child_m and parent_m else {},
  })  # fmt: skip


def sync() -> int:
  n0 = len(load())
  # Hierarchical loop frames.
  hp = EVO / "hier_state.json"
  if hp.exists():
    h = json.loads(hp.read_text())
    st = json.loads((EVO / "state.json").read_text())
    for rec in h.get("history", []):
      bench = None
      for f in sorted(BENCH2.glob(f"{rec['id']}_c*.json")):
        if not f.stem.endswith(("_s2", "_2seed")):
          bench = f.stem
      record_frame(rec, st.get("champion", {}), bench, {})
  # Flat evolution loop (benchmark v1): archive entries with log context.
  sp = EVO / "state.json"
  if sp.exists():
    st = json.loads(sp.read_text())
    logtxt = (EVO / "log.md").read_text() if (EVO / "log.md").exists() else ""
    for e in st.get("archive", []):
      gen = re.match(r"(evo_g\d+)", e["name"])
      parent = None
      if gen:
        m = re.search(rf"{gen.group(1)}: parent (\S+), changed genes (\{{.*\}})", logtxt)
        parent = m.group(1).rstrip(",") if m else None
        changed = m.group(2) if m else ""
      else:
        changed = ""
      append({
        "id": f"evolve/{e['name']}",
        "source": "evolve",
        "level": "L0/L1",
        "context": {"parent": parent, "bench": "v1", "deployment": "pre-2026-10-07 (no target clip, trunk ball origin)"},
        "action": {"desc": f"gene child {e['name']}", "genes_changed": changed},
        "context_genes": e.get("genes"),
        "result": {"ck": e.get("ck"), "score": e.get("score"),
                   "regressions": [r for r in (e.get("regressions") or []) if "missing" not in r]},
        "impact": {"tags": sorted({f"{r.split('(')[0].split(':')[0]}:worse"
                                   for r in (e.get("regressions") or []) if "missing" not in r})},
      })  # fmt: skip
  return len(load()) - n0


# ---------------------------------------------------------------------------
# Queries and statistics


def features(r: dict) -> list[str]:
  """Action features: level, genes touched (prefix-grouped), atom."""
  a = r.get("action", {})
  out = [f"level:{r.get('level')}"]
  g = a.get("genes") or {}
  if isinstance(g, dict):
    out += [f"gene:{k}" for k in g]
  ch = a.get("genes_changed")
  if isinstance(ch, str):
    out += [f"gene:{k}" for k in re.findall(r"'([a-zA-Z_.0-9]+)':", ch)]
  if a.get("atom"):
    out.append(f"atom:{a['atom']}")
  return out


def stats(recs: list[dict]) -> dict:
  agg: dict = defaultdict(lambda: {"n": 0, "promoted": 0, "scores": [], "tags": defaultdict(int)})
  for r in recs:
    res = r.get("result", {})
    for f in features(r):
      s = agg[f]
      s["n"] += 1
      s["promoted"] += bool(res.get("promoted"))
      if isinstance(res.get("score"), (int, float)):
        s["scores"].append(res["score"])
      for t in r.get("impact", {}).get("tags", []):
        s["tags"][t] += 1
  out = {}
  for f, s in agg.items():
    sc = s["scores"]
    out[f] = {
      "n": s["n"], "promoted": s["promoted"],
      "mean_score": round(sum(sc) / len(sc), 2) if sc else None,
      "best_score": round(max(sc), 2) if sc else None,
      "top_effects": sorted(s["tags"].items(), key=lambda x: -x[1])[:6],
    }  # fmt: skip
  return out


def query(recs: list[dict], args: list[str]) -> list[dict]:
  def opt(flag):
    return args[args.index(flag) + 1] if flag in args else None

  gene, level, tag, text = opt("--gene"), opt("--level"), opt("--tag"), opt("--text")
  out = []
  for r in recs:
    if gene and not any(f == f"gene:{gene}" or f.startswith(f"gene:{gene}") for f in features(r)):
      continue
    if level and str(r.get("level")) != level:
      continue
    if tag and tag not in r.get("impact", {}).get("tags", []):
      continue
    if text and text.lower() not in json.dumps(r).lower():
      continue
    out.append(r)
  return out


def digest(n: int = 12) -> dict:
  """Compact view for proposers (L4): action statistics and recent lessons."""
  recs = load()
  st = stats(recs)
  top = sorted(st.items(), key=lambda x: -(x[1]["mean_score"] or -99))
  lessons = [{"id": r["id"], "lesson": r["lesson"]} for r in recs if r.get("lesson")][-n:]
  return {"n_experiences": len(recs), "objectives": OBJECTIVES,
          "action_stats": dict(top[:30]), "lessons": lessons,
          "recent": [{"id": r["id"], "level": r.get("level"),
                      "action": r.get("action", {}).get("desc"),
                      "score": r.get("result", {}).get("score"),
                      "objectives": objective_view(r)} for r in recs[-10:]]}  # fmt: skip


def feature_weight(feature: str, prior: float = 1.0) -> float:
  """Sampling weight for an action feature from past results (proposers):
  exp(mean score / 10), clipped to [0.3, 3]; unseen features keep the prior."""
  import math

  s = stats(load()).get(feature)
  if not s or s["mean_score"] is None:
    return prior
  return max(0.3, min(3.0, math.exp(s["mean_score"] / 10.0)))


def report() -> None:
  recs = load()
  st = stats(recs)
  lines = [
    "# Experience repository",
    "",
    f"{len(recs)} experiences in `experiences.jsonl` (context, action, result, impact, lesson).",
    "Updated by `scripts/tools/experience.py` (sync from the evolution loops; manual records via `add`).",
    "",
    "## Objectives (every experience is read against these)",
    "",
    *[f"- **{k}**: {v}" for k, v in OBJECTIVES.items()],
    "",
    "## Objective balance over all experiences",
    "",
    "| objective | improved | worsened | mixed |",
    "|---|---|---|---|",
    *[
      f"| {o} | {sum(objective_view(r).get(o) == 'better' for r in recs)} |"
      f" {sum(objective_view(r).get(o) == 'worse' for r in recs)} |"
      f" {sum(objective_view(r).get(o) == 'mixed' for r in recs)} |"
      for o in OBJECTIVES
    ],
    "",
    "## What each kind of action did",
    "",
    "| action feature | n | promoted | mean score | best | most frequent effects |",
    "|---|---|---|---|---|---|",
  ]
  for f, s in sorted(st.items(), key=lambda x: (-x[1]["n"], x[0])):
    eff = ", ".join(f"{t} ×{c}" for t, c in s["top_effects"])
    lines.append(f"| {f} | {s['n']} | {s['promoted']} | {s['mean_score']} | {s['best_score']} | {eff} |")
  lines += ["", "## Lessons (latest first)", ""]
  for r in reversed([r for r in recs if r.get("lesson")]):
    lines.append(f"- **{r['id']}** ({r.get('time')}): {r['lesson']}")
  lines += ["", "## All experiences (latest first)", "", "| id | level | action | score | promoted | impact | objectives |", "|---|---|---|---|---|---|---|"]
  for r in reversed(recs):
    res, imp = r.get("result", {}), r.get("impact", {})
    nb, nw = imp.get("n_better"), imp.get("n_worse")
    imp_s = f"+{nb} / -{nw}" if nb is not None else ", ".join(imp.get("tags", [])[:4])
    lines.append(
      f"| {r['id']} | {r.get('level')} | {str(r.get('action', {}).get('desc', ''))[:90]} |"
      f" {res.get('score', '')} | {'yes' if res.get('promoted') else ''} | {imp_s} |"
      f" {', '.join(f'{o} {v}' for o, v in objective_view(r).items() if v != 'tie')} |"
    )
  (REPO / "README.md").write_text("\n".join(lines) + "\n")


def main() -> None:
  cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
  if cmd == "sync":
    print(f"added {sync()} experiences")
    report()
  elif cmd == "add":
    data = json.loads(Path(sys.argv[2]).read_text())
    for r in data if isinstance(data, list) else [data]:
      append(r)
    report()
    print(f"{len(load())} experiences")
  elif cmd == "query":
    for r in query(load(), sys.argv[2:]):
      print(json.dumps(r)[:600])
  elif cmd == "stats":
    print(json.dumps(stats(load()), indent=1))
  else:
    report()


if __name__ == "__main__":
  main()

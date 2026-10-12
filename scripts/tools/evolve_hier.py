"""Hierarchical evolution of the K1 kick policy, L0-L5 (2026-10-07).

Every outer level proposes a FRAME (a fixed change of structure, composition,
scenarios or method); inside the frame an inner L0 search tunes weights and
constants (a few children) so a structure is judged by its best tuning, not
by one untuned try. All levels share one fitness and its gates
(fitness_v2 on benchmark v2) and one champion (docs/evolution/state.json).

  L5 approach   method atoms from docs/approach_catalogue.yaml that have a
                `frame:` (an existing adapter); atoms without one are listed
                in docs/evolution/l5_requests.md for a human / L4.   every 6 h
  L4 proposer   `claude -p` reads a digest (champion v2 metrics, frame history,
                genes, grammar) and returns frames as JSON (validated).  every 3 h
  L3 scenarios  from the champion's weakest v2 situation (rules below).  every 3rd frame
  L2 composition  a penalty becomes an adaptive constraint (c.<term>).  every 4th frame
  L1 structure  template on / off or shape mutation (ts.<template>).    otherwise
  L0 parameters the inner loop inside every frame (evolve_kick mutation).

Per frame: INNER_K children (child 0 = the frame as proposed, others with L0
mutations), PARALLEL at a time, each 500 iterations from the champion; v2
screen of 5 checkpoints each; best child -> full v2 benchmark -> promotion
(two seeds) or a blend with the champion. Results: docs/evolution/hier_state.json,
log.md, hier_report.md.

usage: python scripts/tools/evolve_hier.py [--hours H] [--no-l4]
"""

from __future__ import annotations

import json
import math
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "tools"))
import evolve_kick as ek  # noqa: E402
import experience as xp  # noqa: E402
import fitness_v2  # noqa: E402

HSTATE = ek.EVO / "hier_state.json"
CATALOGUE = ROOT / "docs" / "approach_catalogue.yaml"
INNER_K = 3
PARALLEL = 2
L4_EVERY_H, L5_EVERY_H = 3.0, 6.0
# Escalation (true hierarchy, 2026-10-07): a level moves only when the level
# below has stalled. L1 frames run at the base until STALL["L1"] frames in a
# row fail to promote; then an L2 context is opened; L2 contexts that fail
# STALL["L2"] times open an L3 context; L3 failing STALL["L3"] times goes to
# L5 (catalogue) / L4 (designer). A context fixes its genes and runs BUDGET
# inner frames: the context alone, then L1 changes inside it (each with its
# own L0 children). A promotion absorbs the context into the champion and
# resets all stall counters.
STALL = {"L1": 3, "L2": 2, "L3": 2}
BUDGET = {"L2": 2, "L3": 3, "L4": 2, "L5": 3}
CONSTRAINABLE = (
  "fall", "kick_fall", "torque_over_soft_limit", "trunk_pitch_band",
  "hop_kick_fall", "knee_gap",
)  # fmt: skip
SCENARIO_GENES = {
  "s.spawn_any_prob": (0.0, 0.6),
  "s.far_spawn_prob": (0.0, 0.5),
  "s.world_ball_prob": (0.0, 0.4),
  "s.cap_low_prob": (0.0, 0.5),
}
FRAME_PREFIXES = ("w.", "k.", "t.", "ts.", "s.", "c.")


def log(msg: str) -> None:
  ek.log(f"[hier] {msg}")


def load() -> dict:
  if HSTATE.exists():
    return json.loads(HSTATE.read_text())
  return {"frames": 0, "queue": [], "history": [], "last_l4": 0.0, "last_l5": 0.0,
          "stack": [], "stall": {"L1": 0, "L2": 0, "L3": 0}}


def save(h: dict) -> None:
  HSTATE.write_text(json.dumps(h, indent=1))


# ---------------------------------------------------------------------------
# Proposers


def propose_l1(champ: dict) -> dict:
  g = champ["genes"]
  on = [t for t in ek.TEMPLATES if float(g.get(f"t.{t}", 0.0)) != 0.0]
  off = [t for t in ek.TEMPLATES if t not in on]
  r = random.random()
  if on and r < 0.4:
    t = random.choice(on)
    n = ek.literals(ek.TEMPLATES[t][0])
    f = [round(math.exp(random.gauss(0.0, 0.25)), 3) for _ in range(n)]
    return {"level": "L1", "desc": f"reshape template {t}", "genes": {f"ts.{t}": f}}
  if off and (r < 0.85 or not on):
    w = [xp.feature_weight(f"gene:t.{t}") for t in off]
    t = random.choices(off, weights=w)[0]
    return {"level": "L1", "desc": f"add template {t}", "genes": {f"t.{t}": ek.TEMPLATES[t][1]}}
  t = random.choice(on)
  return {"level": "L1", "desc": f"remove template {t}", "genes": {f"t.{t}": 0.0}}


def propose_l2(champ: dict) -> dict:
  g = champ["genes"]
  free = [t for t in CONSTRAINABLE if f"c.{t}" not in g]
  have = [t for t in CONSTRAINABLE if f"c.{t}" in g]
  if free and (random.random() < 0.7 or not have):
    t = random.choice(free)
    return {"level": "L2", "desc": f"constraint on {t} (0.7x)", "genes": {f"c.{t}": 0.7}}
  have = [t for t in CONSTRAINABLE if f"c.{t}" in g]
  if have:
    t = random.choice(have)
    r = round(min(1.0, max(0.3, float(g[f"c.{t}"]) * random.choice((0.8, 1.25)))), 2)
    return {"level": "L2", "desc": f"constraint {t} ratio {r}", "genes": {f"c.{t}": r}}
  return propose_l1(champ)


def _v(m: dict, key: str, metric: str, cap: str) -> float | None:
  v = m.get(key, {}).get(metric, {}).get(cap)
  return v[0] if v and v[3] else None


def propose_l3(champ: dict) -> dict:
  """Scenario mix from the champion's weakest v2 situation."""
  p = ek.BENCH / f"{champ['name']}.json"
  m = json.loads(p.read_text()) if p.exists() else {}
  g = champ["genes"]
  need = []
  behind = _v(m, "approach/camera/typical", "fall_pct_behind", "high") or 0.0
  world = _v(m, "approach/world/typical", "fall_pct", "high") or 0.0
  goal = _v(m, "goal_grid/camera/typical", "goal_pct", "high") or 100.0
  lo = _v(m, "full_loop/camera/typical", "goals_per_ep", "low") or 0.0
  hi = _v(m, "full_loop/camera/typical", "goals_per_ep", "high") or 0.0
  if behind > 10:
    need.append(("s.spawn_any_prob", behind, "falls with the ball behind"))
  if world > 8:
    need.append(("s.world_ball_prob", world, "falls with a world-model ball"))
  if goal < 70:
    need.append(("s.far_spawn_prob", 100 - goal, "goal grid (long approaches)"))
  if hi > 0 and lo < 0.8 * hi:
    need.append(("s.cap_low_prob", 100 * (1 - lo / hi), "low caps loop goals"))
  if not need:
    gene = random.choice(list(SCENARIO_GENES))
    need = [(gene, 0.0, "exploration")]
  need.sort(key=lambda x: -x[1])
  gene, _, why = need[0]
  lo_b, hi_b = SCENARIO_GENES[gene]
  cur = float(g.get(gene, 0.0))
  new = round(min(hi_b, max(lo_b, cur + random.uniform(0.1, 0.25))), 2)
  return {"level": "L3", "desc": f"{gene} {cur} -> {new} ({why})", "genes": {gene: new}}


def propose_l5(h: dict) -> list[dict]:
  import yaml

  cat = yaml.safe_load(CATALOGUE.read_text())
  tried = {f.get("atom") for f in h["history"]} | {f.get("atom") for f in h["queue"]}
  frames, requests = [], []
  for src in cat.get("sources", []):
    for a in src.get("atoms", []) or []:
      if a.get("status") not in ("candidate", "testing"):
        continue
      if a.get("frame") and a["id"] not in tried:
        frames.append(
          {"level": "L5", "desc": f"atom {a['id']}: {a.get('idea', '')}"[:120],
           "genes": dict(a["frame"]), "atom": a["id"]}
        )  # fmt: skip
      elif not a.get("frame"):
        requests.append(f"- {src['id']}/{a['id']} ({a.get('level')}): {a.get('idea')}")
  (ek.EVO / "l5_requests.md").write_text(
    "# L5 atoms without an adapter (need code before the loop can test them)\n\n"
    + "\n".join(requests)
    + "\n"
  )
  return frames[:2]


def _valid_expr(e) -> bool:
  from mjlab.tasks.velocity.mdp import reward_grammar as rg  # noqa: PLC0415

  ops = {"sig", "const", "mul", "add", "neg", "abs", "div", "ramp", "linear_match",
         "gauss", "band", "exp_decay", "clip", "gt", "lt"}  # fmt: skip
  if isinstance(e, (int, float)):
    return True
  if not isinstance(e, dict) or len(e) != 1:
    return False
  ((op, arg),) = e.items()
  if op not in ops:
    return False
  if op == "sig":
    return arg in rg.SIGNALS
  if op == "const":
    return isinstance(arg, (int, float))
  args = arg if isinstance(arg, list) else [arg]
  return all(_valid_expr(a) for a in args)


def validate(frame: dict) -> dict | None:
  g = frame.get("genes", {})
  if not isinstance(g, dict):
    return None
  out = {}
  for k, v in g.items():
    if k == "_extra_terms":
      terms = [
        t for t in v
        if isinstance(t, dict) and isinstance(t.get("name"), str)
        and isinstance(t.get("weight"), (int, float)) and _valid_expr(t.get("expr"))
      ]  # fmt: skip
      if terms:
        out[k] = [{"name": f"l4_{t['name']}", "expr": t["expr"], "weight": float(t["weight"])} for t in terms[:2]]
      continue
    if not k.startswith(FRAME_PREFIXES) and k not in ek.GENES:
      continue
    if k in ek.GENES and isinstance(v, (int, float)):
      lo, hi, _ = ek.GENES[k]
      v = min(hi, max(lo, float(v)))
    if k in SCENARIO_GENES:
      lo, hi = SCENARIO_GENES[k]
      v = min(hi, max(lo, float(v)))
    out[k] = v
  if not out:
    return None
  return {"level": frame.get("level", "L4"), "desc": str(frame.get("desc", ""))[:160], "genes": out}


def propose_l4(h: dict, champ: dict) -> list[dict]:
  """claude -p as the designer: digest in, frames (JSON) out."""
  from mjlab.tasks.velocity.mdp import reward_grammar as rg  # noqa: PLC0415

  p = ek.BENCH / f"{champ['name']}.json"
  m = json.loads(p.read_text()) if p.exists() else {}
  metrics = {
    f"{k}:{met}:{cap}": _v(m, k, met, cap)
    for k, met, *_ in fitness_v2.METRICS
    for cap in ("low", "high")
  }
  digest = {
    "objectives": "K1 end-to-end kick policy: accuracy, time to kick, power by range "
    "(short 1-4 m and medium 4-8 m distance-matched; long >= 8 m without a cap, as "
    "strong as or stronger than B-Human, air balls fine), run at the speed caps, upright "
    "0.52 m, few falls, deployable on the real robot; use the best kick style (front / "
    "side foot / hop) for each situation; light and heavy ball; beat B-Human "
    "convincingly; never trade away built-up objectives. CURRENT PRIORITY (user, "
    "2026-10-07): bring down the time to kick (esp. at low caps 0.5/0.3/0.6) and long-kick "
    "power, without losing the accuracy / safety gains. runswift's fixture is a proxy "
    "(soft gate on falls, accuracy, kick speed).",
    "champion": champ["name"],
    "champion_genes": champ["genes"],
    "champion_v2_metrics": metrics,
    "recent_frames": h["history"][-15:],
    "genes": {k: v for k, v in ek.GENES.items()},
    "scenario_genes": SCENARIO_GENES,
    "constrainable_terms": CONSTRAINABLE,
    "templates": {k: v[0] for k, v in ek.TEMPLATES.items()},
    "grammar_signals": sorted(rg.SIGNALS),
    "grammar_ops": "sig const mul add neg abs div ramp linear_match gauss band exp_decay clip gt lt",
    "hierarchy": {"stack": h.get("stack"), "stall": h.get("stall")},
    "experience": xp.digest(),
  }
  prompt = (
    "You are the L4 designer of a hierarchical evolution loop for a robot kick "
    "policy. Propose up to 3 FRAMES (changes to try next) that target the "
    "weakest metrics without hurting the others. Each frame: "
    '{"desc": str, "genes": {gene: value}} where gene names use the prefixes '
    "w. (reward weight), k. (kick_loop constant), t. (template weight), ts. "
    "(list of factors on a template's constants), s. (scenario share), c. "
    "(constraint ratio 0.3-1.0 on a constrainable term), or keys of `genes`; "
    'optionally "_extra_terms": [{"name": str, "expr": grammar expression, '
    '"weight": float}] using only the listed signals and ops. Reply with ONLY '
    "a JSON list.\n\nDIGEST:\n" + json.dumps(digest)
  )
  try:
    out = subprocess.run(
      ["claude", "-p", prompt, "--output-format", "text"],
      capture_output=True, text=True, timeout=900,
    ).stdout  # fmt: skip
    i, j = out.find("["), out.rfind("]")
    raw = json.loads(out[i : j + 1]) if i >= 0 and j > i else []
  except Exception as e:  # noqa: BLE001
    log(f"L4 proposer failed: {e}")
    return []
  frames = []
  for f in raw if isinstance(raw, list) else []:
    v = validate(dict(f, level="L4"))
    if v:
      frames.append(v)
  log(f"L4 proposed {len(frames)} frames: {[f['desc'] for f in frames]}")
  return frames[:3]


def level_of(genes: dict) -> str:
  if any(k.startswith("s.") for k in genes):
    return "L3"
  if any(k.startswith("c.") for k in genes):
    return "L2"
  if any(k.startswith(("t.", "ts.", "_extra")) for k in genes):
    return "L1"
  return "L0"


def push(h: dict, ctx: dict, origin: str) -> None:
  lv = ctx["level"] if ctx["level"] in BUDGET else level_of(ctx["genes"])
  ctx = dict(ctx, origin=origin, left=BUDGET.get(origin, BUDGET.get(lv, 2)), first=True)
  h["stack"].append(ctx)
  log(f"context opened ({origin}): {ctx['desc']} {ctx['genes']}, budget {ctx['left']}")


def escalate(h: dict, champ: dict, use_l4: bool) -> None:
  """Open a context at the lowest level that has not stalled."""
  st = h["stall"]
  if st["L2"] < STALL["L2"]:
    push(h, propose_l2(champ), "L2")
    st["L1"] = 0
    return
  if st["L3"] < STALL["L3"]:
    push(h, propose_l3(champ), "L3")
    st["L1"] = st["L2"] = 0
    return
  st["L1"] = st["L2"] = st["L3"] = 0
  fr = propose_l5(h)
  if not fr and use_l4:
    h["last_l4"] = time.time()
    fr = propose_l4(h, champ)
  if fr:
    h["queue"] += fr[1:]
    push(h, fr[0], fr[0]["level"])
  else:
    push(h, propose_l3(champ), "L3")


def next_frame(h: dict, champ: dict, use_l4: bool) -> dict:
  now = time.time()
  # Supervisor injection (docs/evolution/inject.json, list of contexts): pushed
  # on top of the stack at the next frame boundary, then the file is consumed.
  inj = ek.EVO / "inject.json"
  if inj.exists():
    try:
      for f in json.loads(inj.read_text()):
        best = f.pop("best", None)
        push(h, f, f.get("level", "L5"))
        if best:
          h["stack"][-1]["best"] = best
      inj.rename(ek.EVO / f"inject_used_{int(now)}.json")
    except Exception as e:  # noqa: BLE001
      log(f"inject.json unreadable: {e}")
  # Timed top-level proposals open a context when nothing is open.
  if not h["stack"]:
    if h["queue"]:
      f = h["queue"].pop(0)
      push(h, f, f["level"])
    elif now - h["last_l5"] > L5_EVERY_H * 3600:
      h["last_l5"] = now
      fr = propose_l5(h)
      if fr:
        h["queue"] += fr[1:]
        push(h, fr[0], "L5")
    elif use_l4 and now - h["last_l4"] > L4_EVERY_H * 3600:
      h["last_l4"] = now
      fr = propose_l4(h, champ)
      if fr:
        h["queue"] += fr[1:]
        push(h, fr[0], "L4")
  while h["stack"]:
    ctx = h["stack"][-1]
    if ctx["left"] <= 0:
      h["stack"].pop()
      if ctx["origin"] in h["stall"]:
        h["stall"][ctx["origin"]] += 1
      log(f"context closed without promotion: {ctx['desc']}; stall {h['stall']}")
      xp.append({"id": f"hier/ctx/{h['frames']:03d}_{ctx['origin']}", "source": "hier",
                 "level": ctx["origin"], "action": {"desc": f"context: {ctx['desc']}", "genes": ctx["genes"]},
                 "result": {"promoted": False, "frames": BUDGET.get(ctx["origin"], 2)}})  # fmt: skip
      continue
    ctx["left"] -= 1
    genes: dict = {}
    for c in h["stack"]:
      genes.update(c["genes"])
    if ctx["first"]:
      ctx["first"] = False
      return {"level": ctx["origin"], "desc": ctx["desc"], "genes": genes,
              "atom": ctx.get("atom"), "in_context": True}  # fmt: skip
    l1 = propose_l1(dict(champ, genes=dict(champ["genes"], **genes)))
    return {"level": f"L1@{ctx['origin']}", "desc": f"{l1['desc']} | in {ctx['desc']}",
            "genes": dict(genes, **l1["genes"]), "in_context": True}  # fmt: skip
  if h["stall"]["L1"] < STALL["L1"]:
    return propose_l1(champ)
  escalate(h, champ, use_l4)
  return next_frame(h, champ, use_l4)


def l0_mutate(genes: dict, fixed: set[str]) -> dict:
  g = dict(genes)
  for k, (lo, hi, d) in ek.GENES.items():
    if k in fixed or k in ek.BINARY or not k.startswith(("w.", "k.")):
      continue
    if random.random() < 0.3:
      g[k] = round(min(hi, max(lo, float(g.get(k, d)) + random.gauss(0, 0.12 * (hi - lo)))), 4)
  return g


def child(name: str, champ: dict, genes: dict, ref_s: dict) -> tuple[float, Path | None]:
  cks = ek.train_child(name, Path(champ["ck"]), genes)
  best = (-1e9, None)
  for ck in cks:
    s = ek.screen(ck)
    if s is None:
      continue
    sc = ek.screen_score(s, ref_s)
    log(f"{name} {ck.stem}: screen {sc:+.1f}")
    if sc > best[0]:
      best = (sc, ck)
  return best


def install_parent(name: str, ck: str) -> str:
  """A checkpoint (e.g. a blend) as a resumable run directory model_<iter>.pt."""
  import shutil

  import torch

  src = Path(ck)
  if src.parent.name != "blends" and src.stem.startswith("model_"):
    return ck
  it = int(torch.load(src, map_location="cpu", weights_only=False).get("iter", 0))
  run_dir = ek.LOGS / f"{time.strftime('%Y-%m-%d_%H-%M-%S')}_ctx_{name}"
  run_dir.mkdir(parents=True, exist_ok=True)
  dst = run_dir / f"model_{it}.pt"
  shutil.copyfile(src, dst)
  params = Path(ek.load_state()["champion"]["ck"]).parent / "params"
  if params.is_dir():
    shutil.copytree(params, run_dir / "params", dirs_exist_ok=True)
  return str(dst)


def context_parent(h: dict, champ: dict) -> dict:
  """Inheritance: inside a context, children start from the best candidate
  found in the context so far (never worse than the champion's v2 score)."""
  for ctx in reversed(h["stack"]):
    b = ctx.get("best")
    if b:
      return {"name": b["name"], "ck": b["ck"], "genes": champ["genes"]}
  return champ


def run_frame(h: dict, frame: dict) -> dict:
  st = ek.load_state()
  champ = st["champion"]
  parent = context_parent(h, champ) if frame.get("in_context") else champ
  h["frames"] += 1
  fid = f"h{h['frames']:03d}"
  log(f"{fid} {frame['level']}: {frame['desc']} genes {frame['genes']} (parent {parent['name']})")
  base = dict(champ["genes"], **frame["genes"])
  kids = [base] + [l0_mutate(base, set(frame["genes"])) for _ in range(INNER_K - 1)]
  ref_s = ek.screen(Path(champ["ck"]))
  with ThreadPoolExecutor(max_workers=PARALLEL) as pool:
    res = list(pool.map(
      lambda i: child(f"{fid}_c{i}", parent, kids[i], ref_s), range(len(kids))
    ))  # fmt: skip
  order = sorted(range(len(kids)), key=lambda i: -res[i][0])
  bi = order[0]
  bsc, bck = res[bi]
  # Early stop (user 2026-10-07: "if it is not improving, then move on"): the
  # best child must beat its parent's screen, else no full benchmark / blends.
  parent_sc = 0.0
  if parent["name"] != champ["name"]:
    ps = ek.screen(Path(parent["ck"]))
    parent_sc = ek.screen_score(ps, ref_s) if ps is not None else 0.0
  rec = {"id": fid, "level": frame["level"], "desc": frame["desc"], "genes": frame["genes"],
         "atom": frame.get("atom"), "screen": round(bsc, 2), "promoted": False}  # fmt: skip
  if bck is None:
    rec["result"] = "no checkpoints"
    return rec
  ref = json.loads((ek.BENCH / f"{champ['name']}.json").read_text())
  cname = f"{fid}_c{bi}_{bck.stem.split('_')[1]}" if bck.stem.startswith("model_") else bck.stem
  entry = None
  if bsc <= parent_sc + 2.0:
    # Blending with the champion cancelled most fine-tune drift in h001
    # (9 low-cap regressions -> 1): screen 70/30 and 50/50 blends first.
    best_bl = None
    for r_ in (0.7, 0.5, 0.3):
      out = ek.BLENDS / f"{fid}_c{bi}_x{int(r_ * 100)}.pt"
      subprocess.run(
        ["uv", "run", "python", "scripts/tools/blend_checkpoints.py", str(out),
         f"{champ['ck']}:{r_}", f"{bck}:{1 - r_}"],
        cwd=ek.ROOT, capture_output=True,
      )  # fmt: skip
      sb = ek.screen(out) if out.exists() else None
      if sb is not None:
        ssc = ek.screen_score(sb, ref_s)
        log(f"{fid}: blend {r_:.1f}/{1 - r_:.1f} with champion, screen {ssc:+.1f}")
        if best_bl is None or ssc > best_bl[0]:
          best_bl = (ssc, out)
    if best_bl is None or best_bl[0] <= parent_sc + 2.0:
      rec["result"] = f"not improving: best screen {bsc:+.1f} (blend {best_bl[0] if best_bl else float('nan'):+.1f}) vs parent {parent_sc:+.1f}"
      log(f"{fid}: {rec['result']} - moving on")
      rec["_bench"], rec["_child_genes"] = None, kids[bi]
      return rec
    bsc, bck = best_bl
    log(f"{fid}: blend beats the parent on the screen; full benchmark for {bck.stem}")
  if bsc > -2.0:
    m = ek.bench(cname, str(bck))
    if m is not None:
      sc, reg = ek.score(m, ref)
      rec.update(score=round(sc, 2), regressions=reg)
      log(f"{cname}: v2 score {sc:+.2f}, regressions {reg or 'none'}")
      entry = {"name": cname, "ck": str(bck), "genes": kids[bi], "score": round(sc, 2), "regressions": reg}
  if entry is None or entry["regressions"] or entry["score"] <= 0:
    blend = ek.try_blends(cname, champ, bck, ref, {}, ref_s)
    if blend is not None:
      rec["blend"] = {"name": blend["name"], "score": blend["score"], "regressions": blend["regressions"]}
      entry = blend if (not blend["regressions"] and blend["score"] > 0) else None
    else:
      entry = None
  # Keep the context's best candidate (child or blend) as the parent of the
  # context's next frames, if it beats the current context best.
  cand = None
  if "score" in rec:
    cand = {"name": cname, "ck": str(bck), "score": rec["score"], "regressions": rec.get("regressions", [])}
  if rec.get("blend") and (cand is None or rec["blend"]["score"] > cand["score"]):
    bl = rec["blend"]
    cand = {"name": bl["name"], "ck": str(ek.BLENDS / f"{bl['name']}.pt"), "score": bl["score"],
            "regressions": bl.get("regressions", [])}  # fmt: skip
  if frame.get("in_context") and h["stack"] and cand and cand["score"] > 0:
    top = h["stack"][-1]
    if not top.get("best") or cand["score"] > top["best"]["score"]:
      cand["ck"] = install_parent(cand["name"], cand["ck"])
      top["best"] = cand
      log(f"{fid}: context best now {cand['name']} ({cand['score']:+.1f}, {len(cand['regressions'])} regressions)")
  rec["_bench"] = cname if "score" in rec else None
  rec["_child_genes"] = kids[bi]
  if entry is not None:
    new = ek.confirm_and_install(entry, champ)
    if new is not None:
      st = ek.load_state()
      st["champion"] = new
      ek.save_state(st)
      rec["promoted"] = True
      log(f"{fid}: NEW CHAMPION {new['name']} ({frame['level']}: {frame['desc']})")
  return rec


def report(h: dict) -> None:
  rows = ["# Hierarchical evolution report\n", "| level | frames | promoted | best screen |", "|---|---|---|---|"]
  for lv in ("L1", "L2", "L3", "L4", "L5"):
    fr = [f for f in h["history"] if f["level"] == lv]
    if fr:
      rows.append(f"| {lv} | {len(fr)} | {sum(f['promoted'] for f in fr)} | {max(f['screen'] for f in fr):+.1f} |")
  rows += ["", "| id | level | change | screen | v2 score | regressions | promoted |", "|---|---|---|---|---|---|---|"]
  for f in h["history"][-40:]:
    rows.append(
      f"| {f['id']} | {f['level']} | {f['desc']} | {f['screen']:+.1f} | {f.get('score', '—')} |"
      f" {len(f.get('regressions', []))} | {'yes' if f['promoted'] else ''} |"
    )
  (ek.EVO / "hier_report.md").write_text("\n".join(rows) + "\n")


def main() -> None:
  hours = float(sys.argv[sys.argv.index("--hours") + 1]) if "--hours" in sys.argv else 12.0
  use_l4 = "--no-l4" not in sys.argv
  stop = time.time() + hours * 3600
  random.seed()
  h = load()
  h.setdefault("stack", [])
  h.setdefault("stall", {"L1": 0, "L2": 0, "L3": 0})
  xp.sync()
  st = ek.load_state()
  if not (ek.BENCH / f"{st['champion']['name']}.json").exists():
    log("champion has no v2 benchmark; set docs/evolution/state.json champion first")
    return
  while time.time() < stop and ek.disk_ok():
    if (ek.EVO / "STOP_AFTER_FRAME").exists():
      log("STOP_AFTER_FRAME found; stopping")
      break
    champ = st["champion"]
    frame = next_frame(h, champ, use_l4)
    save(h)
    rec = run_frame(h, frame)
    bench, kid = rec.pop("_bench", None), rec.pop("_child_genes", {})
    h["history"].append(rec)
    if rec["promoted"]:
      h["stack"] = []
      h["stall"] = {"L1": 0, "L2": 0, "L3": 0}
    elif not frame.get("in_context"):
      h["stall"]["L1"] += 1
    save(h)
    xp.record_frame(rec, champ, bench, kid)
    xp.report()
    report(h)
    st = ek.load_state()
  log(f"stopped after {h['frames']} frames; champion {ek.load_state()['champion']['name']}")


if __name__ == "__main__":
  main()

"""Engine jobs that run in the background (one process each), so the engine
keeps training while a child is judged (``real.BackgroundJudge``).

  python -m k1.engine.jobs SPEC.json OUT.json

SPEC: {"stage": probe | screen | confirm | reverify | smoke | clip,
       "name", "checkpoint", "refs", "recipe", "champion_recipe", "verdict"}.
OUT: {"stage", "ok", "hours", ...stage results} or {"ok": false, "error"}.

- probe: rs_kick deployed s0 margin over the champion (early stopping);
- screen / confirm: the kick scorecard (``k1.eval.scorecard``); screen also
  attaches the child's per-term training curves;
- reverify: after a promotion, the new champion's gate-size benchmark run (its
  screen reference) and its check against the previous champion's;
- smoke: a 3-iteration training of the recipe before the real one: it starts,
  doesn't crash, and every reward term it edits is logged;
- clip: a headless MP4 of the policy with a motion check (robot up, ball moved).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any

import yaml

from k1.engine import curves
from k1.eval import judges, scorecard
from k1.eval.verdict import Verdict

ROOT = judges.ROOT
TASK = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"
SMOKE_ITERATIONS = 3


def probe(spec: dict[str, Any]) -> dict[str, Any]:
  rs = scorecard.probe(spec["checkpoint"], spec["name"], spec["refs"])
  return {"rs": rs.to_dict(), "margin": rs.margins.get("deployed_s0")}


def screen(spec: dict[str, Any]) -> dict[str, Any]:
  v = scorecard.screen(spec["checkpoint"], spec["name"], spec["refs"])
  out: dict[str, Any] = {"verdict": v.to_dict()}
  run_dir = Path(spec["checkpoint"]).parent
  try:
    focus = curves.edited_terms(
      spec.get("recipe") or {}, spec.get("champion_recipe") or {}
    )
    out["curves"] = curves.write(run_dir, focus)
  except Exception as e:  # curves are context, never a reason to fail the screen
    out["curves"] = {"error": repr(e)}
  return out


def confirm(spec: dict[str, Any]) -> dict[str, Any]:
  return {
    "verdict": scorecard.confirm(
      spec["checkpoint"], spec["name"], spec["refs"]
    ).to_dict()
  }


def reverify(spec: dict[str, Any]) -> dict[str, Any]:
  """Gate-size run of the new champion: becomes its screen reference; scored
  against the previous champion's gate run as a re-check of the promotion."""
  old = spec["refs"]
  name = f"{spec['name']}_champion_gate_s1"
  v = judges.run_kick(spec["checkpoint"], name, "gate", 1, Path(old["bench"]["gate_1"]))
  if v.status != "scored":
    return {"verdict": v.to_dict(), "refs": None}
  verdict = Verdict(**{k: spec["verdict"][k] for k in Verdict.__dataclass_fields__})
  refs = scorecard.refs_after_promotion(verdict, f"docs/benchmarks_v2/{name}.json")
  return {"verdict": v.to_dict(), "refs": refs}


def smoke(spec: dict[str, Any]) -> dict[str, Any]:
  """Train the recipe for a few iterations; problems are reasons not to train."""
  run_name = f"smoke_{spec['name']}"
  cmd = [sys.executable, "-m", "k1.cli", "train", spec["recipe_path"], "--go", "--",
         "--agent.max-iterations", str(SMOKE_ITERATIONS), "--agent.run-name", run_name,
         "--agent.logger", "tensorboard", "--agent.upload-model", "False"]  # fmt: skip
  proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=1800)
  text = proc.stdout + proc.stderr
  problems = []
  m = re.search(r"\[k1\] run.json -> (\S+)", text)
  if proc.returncode != 0 or "Traceback" in text or m is None:
    tail = " | ".join(text.strip().splitlines()[-4:])
    return {"problems": [f"smoke training failed: {tail}"]}
  run_dir = Path(m[1]).parent
  (run_dir / "smoke_train.log").write_text(text)
  bad = [ln.strip() for ln in text.splitlines()
         if re.search(r"(loss|reward|episode_)", ln, re.I)
         and re.search(r"[:=\s](-?nan|-?inf)\b", ln, re.I)]  # fmt: skip
  if bad:
    problems.append(f"NaN / inf in the smoke training: {bad[:3]}")
  recipe = yaml.safe_load(Path(spec["recipe_path"]).read_text())
  focus = curves.edited_terms(recipe, spec.get("champion_recipe") or {})
  series = curves.scalars(run_dir)
  missing = [t for t in focus if f"Episode_Reward/{t}" not in series]
  if missing:
    problems.append(f"edited reward terms not logged (not registered?): {missing}")
  return {"problems": problems, "run_dir": str(run_dir), "terms": focus}


def clip(spec: dict[str, Any]) -> dict[str, Any]:
  """Headless MP4 (8 s, one robot) + motion check, in the run directory."""
  from dataclasses import asdict

  import imageio
  import numpy as np
  import torch

  import mjlab.tasks  # noqa: F401
  from mjlab.envs import ManagerBasedRlEnv
  from mjlab.rl import RslRlVecEnvWrapper
  from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls

  dev = "cuda:0"
  cfg = load_env_cfg(TASK, play=True)
  cfg.scene.num_envs = 1
  agent = load_rl_cfg(TASK)
  u = ManagerBasedRlEnv(cfg=cfg, device=dev, render_mode="rgb_array")
  env = RslRlVecEnvWrapper(u, clip_actions=agent.clip_actions)
  runner_cls = load_runner_cls(TASK)
  assert runner_cls is not None
  runner = runner_cls(env, asdict(agent), device=dev)
  runner.load(
    spec["checkpoint"], load_cfg={"actor": True}, strict=True, map_location=dev
  )
  pol = runner.get_inference_policy(device=dev)
  obs, _ = env.reset()
  rob, ball = u.scene["robot"], u.scene["ball"]
  frames, heights, balls = [], [], []
  with torch.inference_mode():
    for i in range(400):
      obs, *_ = env.step(pol(obs))
      heights.append(float(rob.data.root_link_pos_w[0, 2]))
      balls.append(ball.data.root_link_pos_w[0, :2].cpu().numpy())
      if i % 2 == 0:
        frame = u.render()
        if frame is not None:
          frames.append(frame)
  path = Path(spec["checkpoint"]).parent / f"clip_{spec['name']}.mp4"
  if frames:
    imageio.mimsave(path, frames, fps=25, macro_block_size=1)
  motion = (
    float(
      np.mean(
        [
          np.abs(a.astype(float) - b).mean()
          for a, b in zip(frames, frames[1:], strict=False)
        ]
      )
    )
    if len(frames) > 1
    else 0.0
  )
  ball_path = float(np.linalg.norm(np.diff(np.array(balls), axis=0), axis=-1).sum())
  checks = {"frames_move": motion > 0.5, "stays_up": min(heights) > 0.3,
            "ball_moved": ball_path > 0.3}  # fmt: skip
  u.close()
  return {"file": str(path), "motion": round(motion, 3), "min_height": round(min(heights), 3),
          "ball_path_m": round(ball_path, 2), "checks": checks}  # fmt: skip


STAGES = {"probe": probe, "screen": screen, "confirm": confirm, "reverify": reverify,
          "smoke": smoke, "clip": clip}  # fmt: skip


def main(spec_path: str, out_path: str) -> int:
  spec = json.loads(Path(spec_path).read_text())
  t0 = time.time()
  try:
    out = {"stage": spec["stage"], "ok": True, **STAGES[spec["stage"]](spec)}
  except Exception:
    out = {"stage": spec["stage"], "ok": False, "error": traceback.format_exc()[-2000:]}
  out["hours"] = round((time.time() - t0) / 3600, 3)
  tmp = Path(out_path).with_suffix(".tmp")
  tmp.write_text(json.dumps(out, indent=1, default=str))
  os.replace(tmp, out_path)
  return 0


if __name__ == "__main__":
  raise SystemExit(main(*sys.argv[1:3]))

"""Kick benchmark v2, CPU engine: the robot's own runner code (k1_policy_runner
KickLoopPolicy + ONNX, joint-target clip, lost-ball rule, head tracker) in the
runner's MuJoCo bridge, driven by runswift's benchmark harness
(runswift/benchmarks/kick_policies: compare.py near-ball grid, goal_grid.py
goal-scoring grid) with our conditions patched in:

  - our ONNX instead of the pinned one (hash recorded);
  - speed caps low (0.5 / 0.3 / 0.6, runswift's) or high (2.0 / 1.5 / 1.5);
  - ball input like runswift vision's base_link: between the feet, ground
    level, yaw-only frame; perception camera (bridge's camera view, noise
    0.03 + 0.05 * d m, 2 % dropout) / world (fresh at any bearing, noise) /
    perfect (runswift's original, but between the feet).

B-Human keeps runswift's adapter unchanged (perfect ball + velocity; its
goal-grid navigator has runswift's caps hard-coded, so low caps only).
No motor delay in this engine (the GPU engine covers delay).

usage: python scripts/tools/kick_bench2_cpu.py NAME (ONNX | bhuman)
         [--track near|goal|both] [--caps low|high] [--perception camera|world|perfect]
         [--workers 22]
Results: docs/benchmarks_v2/cpu/NAME/<track>-<caps>-<perception>/summary.json
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RL = ROOT.parent
HARNESS = RL / "runswift/benchmarks/kick_policies"
ASSETS = ROOT / ".cache" / "bench2_assets"
OUT = ROOT / "docs" / "benchmarks_v2" / "cpu"
CAPS = {"low": [0.5, 0.3, 0.6], "high": [2.0, 1.5, 1.5]}


def arg(flag: str, default: str) -> str:
  return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def assets() -> Path:
  ASSETS.mkdir(parents=True, exist_ok=True)
  for name, target in (
    ("peter-runner", RL / "k1_policy_runner"),
    ("bhuman", RL / "MachineLearning"),
    ("peter-training", ROOT),
  ):
    link = ASSETS / name
    if not link.exists():
      link.symlink_to(target)
  return ASSETS


def patch(onnx: str | None, caps: list[float], perception: str) -> None:
  sys.path.insert(0, str(HARNESS))
  import compare  # noqa: PLC0415

  if onnx:
    p = Path(onnx).resolve()
    compare.MODELS["peter"] = (str(p), hashlib.sha256(p.read_bytes()).hexdigest())
  up = compare.upstream

  def upstream(root):
    bridge, kick, limits, action_t, cmd_t = up(root)

    class Kick(kick):
      def __init__(self, *a, **kw):
        kw.setdefault("speed_limits", caps)
        super().__init__(*a, **kw)

    return bridge, Kick, limits, action_t, cmd_t

  compare.upstream = upstream
  orig_action = compare.Controller.action
  rng = np.random.default_rng(20261007)

  def action(self, bridge):
    if self.name != "peter":
      return orig_action(self, bridge)
    state = bridge.latest_state()  # bridge camera: seen time if in view
    yaw = compare.yaw_of(bridge.data)
    feet = [
      bridge.data.xpos[bridge.model.body(n).id] for n in ("left_foot_link", "right_foot_link")
    ]
    origin = np.mean(feet, axis=0)
    ball = compare.body_xy(bridge.ball_world(), origin, yaw)
    d = float(np.linalg.norm(ball))
    fresh = perception in ("perfect", "world") or (
      bridge.ball_visible() and rng.random() >= 0.02
    )
    if perception != "perfect":
      ball = ball + rng.normal(0.0, 0.03 + 0.05 * d, 2)
    if fresh:
      state.has_ball, state.ball_seen_time = True, state.time_s
      state.ball_rel_pos = [*ball, 0.0]
    observation = self.actor.build_observation(state, (0, 0, 0))
    act = self.actor.infer(observation)
    return act, np.array(observation.data), np.array(self.actor._last_action)

  compare.Controller.action = action


def main() -> None:
  name, policy = sys.argv[1], sys.argv[2]
  track = arg("--track", "both")
  caps = arg("--caps", "low")
  perception = arg("--perception", "camera")
  workers = arg("--workers", "22")
  who = "bhuman" if policy == "bhuman" else "peter"
  patch(None if who == "bhuman" else policy, CAPS[caps], perception)
  root = assets()
  grid = RL / "runswift/benchmarks/results/2026-10-02/k1-score-grid/manifest.json"
  evaluator = RL / "runswift/src/behaviour/examples/booster_match/score_evaluator.py"
  base = OUT / name
  base.mkdir(parents=True, exist_ok=True)
  meta = {"policy": policy, "caps": CAPS[caps], "perception": perception}
  (base / "meta.json").write_text(json.dumps(meta, indent=1))
  tag = f"{caps}-{perception if who == 'peter' else 'perfect'}"
  if track in ("near", "both"):
    import compare  # noqa: PLC0415

    sys.argv = [
      "compare.py", "--assets", str(root), "--policy", who, "--suite", "full",
      "--ball-profile", "both", "--repeats", "3", "--workers", workers,
      "--output", str(base / f"near-{tag}"),
    ]  # fmt: skip
    compare.main()
  if track in ("goal", "both"):
    import goal_grid  # noqa: PLC0415

    sys.argv = [
      "goal_grid.py", "--assets", str(root), "--policy", who, "--suite", "grid",
      "--ball-profile", "both", "--workers", workers, "--grid-file", str(grid),
      "--evaluator-file", str(evaluator), "--output", str(base / f"goal-{tag}"),
    ]  # fmt: skip
    goal_grid.main()


if __name__ == "__main__":
  os.chdir(ROOT)
  main()

"""B-Human K1_Ball kick benchmark v2 on the ported env (Mjlab-BHuman-Kick-*).

200 trials per policy (default): 4 kick-direction sectors (forward +-45 deg,
left 45-135, back 135-225 = go around the ball, right -135..-45) x 2 ball
sides x 25, Latin-hypercube sampled per cell; half strong (20 m) and half
normal kicks (range log-uniform 0.5-20 m). Identical trials for every policy.

Ball 0.35-1.0 m ahead at 0-30 deg left or right of the heading, still;
standing start; 12 s to kick; deterministic policy. Benchmark ball: radius
0.1 +- 0.02 m, mass 0.3 +- 0.02 kg, friction 1.0, rolling 0.1, torsion 0.1,
damping 0.75 / 0.5, no bounce. Pushes, ball resets and ball velocity events
off; by default also no robot randomization and no observation noise.

Per trial: fell (within the 12 s), kicked (Booster Gym's kick detection), time
to kick, direction error (x-y angle between the commanded direction and the
ball's direction at 50 % and 90 % of its final distance, averaged), average /
peak ball speed and distance / path length from the kick until the ball stops
(max 6 s). Score: 0 if fell or no kick, else 0.5 s_time + 0.3 s_acc +
0.2 s_power with s_time = min(1, 2.3 s / time), s_acc = clip(1 - err / 30 deg),
s_power = clip(peak / sqrt(2 * 0.3 * range)).

Example:
  uv run python scripts/tools/bench_bhuman_kick_v2.py --name seed0 \
    --policy pretrained=../MachineLearning/IsaacGymRL/pre-trained/WalkAndKick/K1_kick_inner.pth \
    --policy mine=logs/rsl_rl/k1_bhuman_kick/<run>/model_400.pt
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch

import mjlab.tasks  # noqa: F401
from k1.tasks.bhuman.kick_command import BHumanKickCommand, BHumanKickCommandCfg
from k1.tasks.bhuman.mdp import set_ball_size_mass
from k1.tasks.bhuman.robot import get_bhuman_ball_cfg
from k1.tasks.bhuman.runner import BHumanPpoRunner, BHumanPpoRunnerCfg
from mjlab.envs import ManagerBasedRlEnv
from mjlab.managers.event_manager import RecomputeLevel
from mjlab.scripts.play_bhuman_kick import _load_mlp
from mjlab.tasks.registry import load_env_cfg

SECTORS = {
  "forward": (-45.0, 45.0),
  "left": (45.0, 135.0),
  "back": (135.0, 225.0),
  "right": (-135.0, -45.0),
}
SIDES = {"left": (0.0, 30.0), "right": (-30.0, 0.0)}
TRIAL_S = 12.0
TRACK_S = 6.0
STOP_SPEED = 0.05
TIME_REF = 2.3
ACC_REF = 30.0


def make_trials(per_cell: int, seed: int) -> list[dict]:
  rng = np.random.default_rng(seed)
  trials = []
  for c, ((sector, (d0, d1)), (side, (b0, b1))) in enumerate(
    (s, b) for s in SECTORS.items() for b in SIDES.items()
  ):
    # Latin hypercube: one stratum per trial in every dimension.
    u = (
      np.stack([rng.permutation(per_cell) for _ in range(5)], 1)
      + rng.random((per_cell, 5))
    ) / per_cell
    for i in range(per_cell):
      strong = (i + c) % 2 == 0
      rng_m = math.exp(math.log(0.5) + u[i, 3] * (math.log(20.0) - math.log(0.5)))
      trials.append(
        {
          "sector": sector,
          "side": side,
          "dist": 0.35 + 0.65 * u[i, 0],
          "bearing_deg": b0 + (b1 - b0) * u[i, 1],
          "direction_deg": d0 + (d1 - d0) * u[i, 2],
          "strong": strong,
          "range": 20.0 if strong else rng_m,
          "radius": 0.08 + 0.04 * u[i, 4],
          "mass": 0.28 + 0.04 * rng.random(),
        }
      )
  return trials


def build_env(task: str, n: int, obs_noise: bool, training_dr: bool, rolling: float):
  cfg = load_env_cfg(task)
  cfg.scene.num_envs = n
  assert cfg.scene.terrain is not None
  cfg.scene.terrain.terrain_type = "plane"
  cfg.scene.terrain.terrain_generator = None
  cfg.scene.entities["ball"] = get_bhuman_ball_cfg(
    friction=(1.0, 0.1, rolling), condim=6, solref=(0.02, 1.0)
  )
  k = cfg.commands["kick"]
  assert isinstance(k, BHumanKickCommandCfg)
  k.time_after_kick = 10**6
  k.random_ball_reset = (0.0, 0.0, 0.0)
  k.random_ball_distance_reset = 0.0
  k.reset_ball_request = 0.0
  k.add_ball_vel = 0.0
  k.add_ball_vel_in_direction = 0.0
  k.heavy_ball = 0.0
  k.push_force = k.push_torque = 0.0
  k.kick_lin_vel = k.kick_lin_vel_z = k.kick_ang_vel = 0.0
  k.observation_noise = obs_noise
  if not obs_noise:
    k.ball_freeze_at_kick = 0.0
  if not training_dr:
    for name in (
      "dof_stiffness",
      "dof_ankle_stiffness",
      "dof_hiproll_stiffness",
      "dof_damping",
      "dof_ankle_damping",
      "dof_hiproll_damping",
    ):
      setattr(k, name, (1.0, 1.0))
    k.dof_pos_offset_pitch = k.dof_pos_offset_roll = k.dof_pos_offset_other = 0.0
    k.init_dof_pos = 0.0
    k.init_base_lin_vel_xy = k.init_base_lin_vel_z = k.init_base_ang_vel_xyz = 0.0
    ev = cfg.events
    ev["body"].params = {
      "base_com": 0.0,
      "base_mass": (1.0, 1.0),
      "other_com": 0.0,
      "other_mass": (1.0, 1.0),
    }
    ev["feet"].params = {"friction": (0.65, 0.65)}
    ev["joint_friction"].params = {"friction": (0.0, 0.0)}
  return ManagerBasedRlEnv(cfg=cfg, device="cuda:0")


def load_actor(path: str, vec, device: str) -> torch.nn.Module:
  if path.endswith(".onnx"):
    return _load_mlp(Path(path), device)
  runner = BHumanPpoRunner(vec, asdict(BHumanPpoRunnerCfg()), None, device)
  runner.load(path)
  return runner.model.actor.eval()


def run_policy(env, vec, actor, trials: list[dict], seed: int) -> list[dict]:
  dev = env.device
  n = len(trials)
  cmd = env.command_manager.get_term("kick")
  assert isinstance(cmd, BHumanKickCommand)
  torch.manual_seed(seed)
  vec.reset()
  ids = torch.arange(n, device=dev)
  t = {
    k: torch.tensor([tr[k] for tr in trials], device=dev, dtype=torch.float)
    for k in ("dist", "bearing_deg", "direction_deg", "range", "radius", "mass")
  }
  set_ball_size_mass(env, ids, t["radius"], t["mass"])
  env.sim.recompute_constants(RecomputeLevel.set_const)
  bearing = torch.deg2rad(t["bearing_deg"])
  ball_b = torch.stack(
    (t["dist"] * torch.cos(bearing), t["dist"] * torch.sin(bearing)), -1
  )
  strong = torch.tensor([tr["strong"] for tr in trials], device=dev)
  cmd.place_task(
    ids, ball_b, torch.deg2rad(t["direction_deg"]), t["range"], strong, t["radius"]
  )
  # Booster Gym keeps action buffers across resets; start every policy clean.
  act_term = cmd.action_term
  act_term.actions.zero_()
  act_term.last_actions.zero_()
  act_term.actions_gait.zero_()
  cmd.gait_process.zero_()
  cmd.compute(0.0)
  ball0 = cmd.ball_state[:, :2].clone()
  to_target = cmd.ball_end_target - ball0
  cmd_dir = torch.atan2(to_target[:, 1], to_target[:, 0])
  obs = env.observation_manager.compute()["actor"]

  dt = env.step_dt
  trial_steps = int(TRIAL_S / dt)
  total = trial_steps + int(TRACK_S / dt)
  kick_step = torch.full((n,), -1, dtype=torch.long, device=dev)
  fell = torch.zeros(n, dtype=torch.bool, device=dev)
  broken = torch.full((n,), total, dtype=torch.long, device=dev)
  pos = torch.zeros(total, n, 2, device=dev)
  speed = torch.zeros(total, n, device=dev)
  p_kick = torch.zeros(n, 2, device=dev)
  for s in range(total):
    with torch.no_grad():
      obs, _, _, done, _, _ = vec.step(actor(obs))
    pos[s] = cmd.ball_state[:, :2]
    speed[s] = cmd.ball_state[:, 7:10].norm(dim=-1)
    new_kick = (
      (kick_step < 0) & (cmd.ball_kicked_counter >= 1) & ~fell & (s < trial_steps)
    )
    p_kick[new_kick] = cmd.ball_pos_at_kick[new_kick, :2]
    kick_step[new_kick] = s
    fall = cmd.terminated.clone()
    fell |= fall & (s < trial_steps)
    # A reset (fall / time-out) moves the ball: tracking ends there.
    broken = torch.where(done & (broken == total), s, broken)
    if s >= trial_steps and bool(((kick_step < 0) | fell | (broken < total)).all()):
      break

  pos_c, speed_c = pos.cpu().numpy(), speed.cpu().numpy()
  ks, br = kick_step.cpu().numpy(), broken.cpu().numpy()
  fl, pk = fell.cpu().numpy(), p_kick.cpu().numpy()
  cd = cmd_dir.cpu().numpy()
  rows = []
  for i, tr in enumerate(trials):
    row = dict(tr)
    kicked = ks[i] >= 0
    row.update(fell=bool(fl[i]), kicked=bool(kicked))
    if not kicked or fl[i]:
      row.update(
        time=float("nan"),
        dir_err=float("nan"),
        avg_speed=float("nan"),
        peak_speed=float("nan"),
        distance=float("nan"),
        path_length=float("nan"),
        score=0.0,
      )
      rows.append(row)
      continue
    s0 = int(ks[i])
    s1 = min(s0 + int(TRACK_S / dt), int(br[i]), total)
    sp = speed_c[s0:s1, i]
    moving = np.nonzero(sp[3:] < STOP_SPEED)[0]
    if len(moving) > 0:
      s1 = s0 + 3 + int(moving[0]) + 1
      sp = speed_c[s0:s1, i]
    path = np.concatenate([pk[i][None], pos_c[s0:s1, i]], 0)
    rel = path - pk[i]
    dist = np.linalg.norm(rel, axis=-1)
    final = float(dist[-1])
    errs = []
    for frac in (0.5, 0.9):
      j = int(np.argmax(dist >= frac * final)) if final > 1e-6 else len(dist) - 1
      ang = math.atan2(rel[j, 1], rel[j, 0])
      errs.append(abs((ang - cd[i] + math.pi) % (2 * math.pi) - math.pi))
    dir_err = math.degrees(sum(errs) / 2)
    time_s = (s0 + 1) * dt
    peak = float(sp.max())
    needed = math.sqrt(2 * 0.3 * tr["range"])
    score = (
      0.5 * min(1.0, TIME_REF / time_s)
      + 0.3 * float(np.clip(1 - dir_err / ACC_REF, 0, 1))
      + 0.2 * float(np.clip(peak / needed, 0, 1))
    )
    row.update(
      time=time_s,
      dir_err=dir_err,
      avg_speed=float(sp.mean()),
      peak_speed=peak,
      distance=final,
      path_length=float(np.linalg.norm(np.diff(path, axis=0), axis=-1).sum()),
      score=score,
    )
    rows.append(row)
  return rows


def _ms(x: list[float]) -> str:
  a = np.array([v for v in x if not math.isnan(v)])
  if len(a) == 0:
    return "-"
  return f"{a.mean():.2f} ± {a.std():.2f} ({np.median(a):.2f})"


def summarize(rows: list[dict]) -> dict:
  def col(k: str) -> list[float]:
    return [r[k] for r in rows]

  ok = [r for r in rows if r["kicked"] and not r["fell"]]
  return {
    "n": len(rows),
    "score": float(np.mean(col("score"))),
    "kicked": sum(r["kicked"] for r in rows),
    "fell": sum(r["fell"] for r in rows),
    "within15": sum(r["dir_err"] <= 15 for r in ok),
    "time": _ms(col("time")),
    "dir_err": _ms(col("dir_err")),
    "avg_speed": _ms(col("avg_speed")),
    "peak_speed": _ms(col("peak_speed")),
    "distance": _ms(col("distance")),
    "path_length": _ms(col("path_length")),
    "time_mean": float(np.nanmean(col("time"))) if ok else float("nan"),
    "dir_err_mean": float(np.nanmean(col("dir_err"))) if ok else float("nan"),
  }


def report(results: dict, args) -> str:
  names = list(results)
  head = "| Metric | " + " | ".join(names) + " |\n|---|" + "---|" * len(names) + "\n"

  def table(get, metrics: list[tuple[str, str]]) -> str:
    out = head
    for label, key in metrics:
      out += f"| {label} | " + " | ".join(str(get(nm)[key]) for nm in names) + " |\n"
    return out

  def fmt(s: dict) -> dict:
    return s | {"score": f"{s['score']:.3f}", "kf": f"{s['kicked']} / {s['fell']}"}

  lines = [
    "# B-Human K1_Ball kick benchmark v2: results\n",
    f"Port env `{args.task}`, plane, seed {args.seed}, {args.trials_per_cell} trials "
    f"per cell, observation noise {'on' if args.obs_noise else 'off'}, robot "
    f"randomization {'on' if args.training_dr else 'off'}, ball rolling friction "
    f"{args.rolling}. Cells: mean ± std (median).\n",
    "## Overall\n",
  ]
  overall = {nm: fmt(results[nm]["overall"]) for nm in names}
  worst = {
    nm: min(results[nm]["sectors"].items(), key=lambda kv: kv[1]["score"])
    for nm in names
  }
  rows = [
    ("**Priority score**", "score"),
    ("Kicked / fell", "kf"),
    ("Kicks within 15° of command", "within15"),
    ("Time to kick [s]", "time"),
    ("Direction error [deg]", "dir_err"),
    ("Avg ball speed [m/s]", "avg_speed"),
    ("Peak ball speed [m/s]", "peak_speed"),
    ("Ball distance [m]", "distance"),
    ("Ball path length [m]", "path_length"),
  ]
  for nm in names:
    overall[nm]["worst"] = f"{worst[nm][0]} {worst[nm][1]['score']:.3f}"
  lines.append(
    table(lambda nm: overall[nm], rows[:1] + [("Worst sector", "worst")] + rows[1:])
  )
  lines.append("## Per kick-direction sector\n")
  for sec in SECTORS:
    lines.append(f"### {sec.capitalize()}\n")
    lines.append(
      table(
        lambda nm, sec=sec: fmt(results[nm]["sectors"][sec]),
        [("Score", "score"), ("Kicked / fell", "kf"), ("Within 15°", "within15")]
        + rows[3:8],
      )
    )
  lines.append("## Per ball side\n")
  side_rows = {
    nm: {f"{sd}_score": f"{results[nm]['sides'][sd]['score']:.3f}" for sd in SIDES}
    | {
      f"{sd}_td": f"{results[nm]['sides'][sd]['time_mean']:.2f} / "
      f"{results[nm]['sides'][sd]['dir_err_mean']:.1f}"
      for sd in SIDES
    }
    for nm in names
  }
  lines.append(
    table(
      lambda nm: side_rows[nm],
      [
        ("ball-left score", "left_score"),
        ("ball-left time [s] / dir. error [deg]", "left_td"),
        ("ball-right score", "right_score"),
        ("ball-right time [s] / dir. error [deg]", "right_td"),
      ],
    )
  )
  lines.append("## Per cell: score / time [s] / direction error [deg] / within 15°\n")
  out = (
    "| Sector / ball side | " + " | ".join(names) + " |\n|---|" + "---|" * len(names)
  )
  out += "\n"
  for sec in SECTORS:
    for sd in SIDES:
      cells = []
      for nm in names:
        c = results[nm]["cells"][f"{sec}/{sd}"]
        cells.append(
          f"{c['score']:.3f} / {c['time_mean']:.2f} / "
          f"{c['dir_err_mean']:.1f} / {c['within15']}"
        )
      out += f"| {sec} / {sd} | " + " | ".join(cells) + " |\n"
  lines.append(out)
  return "\n".join(lines)


def main() -> None:
  p = argparse.ArgumentParser()
  p.add_argument("--policy", action="append", required=True, help="NAME=PATH")
  p.add_argument("--name", default="kick_v2_seed0")
  p.add_argument("--task", default="Mjlab-BHuman-Kick-Booster-K1")
  p.add_argument("--seed", type=int, default=0)
  p.add_argument("--trials-per-cell", type=int, default=25)
  p.add_argument("--obs-noise", action="store_true")
  p.add_argument("--training-dr", action="store_true")
  p.add_argument("--rolling", type=float, default=0.1)
  p.add_argument("--out", default="docs/benchmarks_bhuman_kick")
  args = p.parse_args()

  trials = make_trials(args.trials_per_cell, args.seed)
  env = build_env(
    args.task, len(trials), args.obs_noise, args.training_dr, args.rolling
  )
  vec = BHumanPpoRunner.make_vecenv(env, None)
  out = Path(args.out) / args.name
  out.mkdir(parents=True, exist_ok=True)
  results: dict = {}
  for spec in args.policy:
    name, path = spec.split("=", 1)
    actor = load_actor(path, vec, env.device)
    rows = run_policy(env, vec, actor, trials, args.seed)
    with open(out / f"trials_{name}.csv", "w", newline="") as f:
      w = csv.DictWriter(f, fieldnames=list(rows[0]))
      w.writeheader()
      w.writerows(rows)
    results[name] = {
      "checkpoint": path,
      "overall": summarize(rows),
      "sectors": {s: summarize([r for r in rows if r["sector"] == s]) for s in SECTORS},
      "sides": {s: summarize([r for r in rows if r["side"] == s]) for s in SIDES},
      "cells": {
        f"{s}/{sd}": summarize(
          [r for r in rows if r["sector"] == s and r["side"] == sd]
        )
        for s in SECTORS
        for sd in SIDES
      },
    }
    o = results[name]["overall"]
    print(
      f"{name}: score {o['score']:.3f} kicked {o['kicked']} fell {o['fell']} "
      f"time {o['time']} dir {o['dir_err']} peak {o['peak_speed']}",
      flush=True,
    )
  (out / "results.json").write_text(json.dumps(results, indent=2))
  (out / "report.md").write_text(report(results, args))
  print(f"Wrote {out}/report.md")
  env.close()


if __name__ == "__main__":
  main()

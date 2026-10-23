"""Kick benchmark (runswift spec v2): trials, kick rule, metrics, score, report.

The same benchmark for every kick policy, so results compare across policies
and engines: ``scripts/tools/rs_kick_bench.py`` runs our kick loop (stage-3
env), ``scripts/tools/bench_bhuman_kick_v2.py`` B-Human's kick (its port).

200 trials (default): 4 kick-direction sectors (forward +-45 deg, left 45-135,
back 135-225 = go around the ball, right -135..-45) x 2 ball sides x 25,
Latin-hypercube sampled per cell; half strong (20 m) and half normal kicks
(range log-uniform 0.5-20 m). Ball 0.35-1.0 m ahead at 0-30 deg left or right
of the heading, still; standing start; 12 s to kick. Benchmark ball: radius
0.1 +- 0.02 m, mass 0.3 +- 0.02 kg, friction 1.0, rolling 0.1, torsion 0.1,
damping 0.75 / 0.5 (Isaac Gym's per-step damping), no bounce.

Per trial: fell (within 12 s), kicked (Booster Gym's kick rule, ``KickRule``),
time to kick, direction error (angle between the commanded direction and the
ball's direction at 50 % and 90 % of its final distance, averaged), average /
peak ball speed and distance / path length from the kick until the ball stops
(max 6 s). Score: 0 if fell or no kick, else 0.5 s_time + 0.3 s_acc +
0.2 s_power with s_time = min(1, 2.3 s / time), s_acc = clip(1 - err / 30 deg),
s_power = clip(peak / sqrt(2 * 0.3 * range)).
"""

from __future__ import annotations

import math

import numpy as np
import torch

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
DECEL = 0.3  # ball deceleration assumed for the power reference (m/s^2)
WEAK_M = 0.3  # a kick that moves the ball less than this is weak
# Benchmark ball contact (slide, torsion, rolling friction) and Isaac Gym's
# per-actor damping, as in the B-Human port (BHumanKickCommandCfg).
BALL_FRICTION = (1.0, 0.1, 0.1)
BALL_SOLREF = (0.02, 1.0)
BALL_LINEAR_DAMPING = 0.75
BALL_ANGULAR_DAMPING = 0.5
BALL_MAX_SPEED = 20.0
# Sole corners in the foot link frame (B-Human's K1 feet).
FEET = ("left_foot_link", "right_foot_link")
FEET_EDGE_POS = (
  (0.1185, 0.035, -0.038),
  (0.1185, -0.035, -0.038),
  (-0.0665, 0.035, -0.038),
  (-0.0665, -0.035, -0.038),
)


def make_trials(per_cell: int, seed: int) -> list[dict]:
  """The trial list; identical for every policy and engine given the seed."""
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


def damp_ball(lin: torch.Tensor, ang: torch.Tensor, physics_dt: float, substeps: int):
  """Isaac Gym's per-substep damping applied once per policy step, then the
  speed cap (BHumanKickCommand step 9.3)."""
  lin = lin * (1.0 / (1.0 + physics_dt * BALL_LINEAR_DAMPING)) ** substeps
  ang = ang * (1.0 / (1.0 + physics_dt * BALL_ANGULAR_DAMPING)) ** substeps
  speed = lin.norm(dim=-1, keepdim=True)
  return lin * (BALL_MAX_SPEED / speed.clamp(min=1e-6)).clip(max=1.0), ang


def _wrap(x: torch.Tensor) -> torch.Tensor:
  return torch.remainder(x + math.pi, 2 * math.pi) - math.pi


class KickRule:
  """Booster Gym's kick detection (BHumanKickCommand._update_kick_tensors),
  computed from the robot's feet and the ball so it is the same for any policy.
  Call ``update`` once per policy step after physics; ``kicked`` latches."""

  def __init__(self, n: int, device: str) -> None:
    self.edges = torch.tensor(FEET_EDGE_POS, device=device)
    self.last_feet: torch.Tensor | None = None
    self.last_ball_vel = torch.zeros(n, 3, device=device)
    self.still = torch.zeros(n, device=device)
    self.steps = 0

  def corners(self, feet_pos: torch.Tensor, feet_quat: torch.Tensor) -> torch.Tensor:
    from mjlab.utils.lab_api.math import quat_apply

    n = feet_pos.shape[0]
    q = feet_quat.unsqueeze(2).expand(n, 2, 4, 4).reshape(-1, 4)
    e = self.edges.expand(n, 2, 4, 3).reshape(-1, 3)
    return feet_pos.unsqueeze(2) + quat_apply(q, e).reshape(n, 2, 4, 3)

  def update(
    self,
    feet_pos: torch.Tensor,  # (n, 2, 3) foot link positions
    feet_quat: torch.Tensor,  # (n, 2, 4)
    ball_pos: torch.Tensor,  # (n, 3)
    ball_vel: torch.Tensor,  # (n, 3), after physics, before damping
    radius: torch.Tensor,  # (n,)
    dt: float,
  ) -> torch.Tensor:
    self.steps += 1
    edges = self.corners(feet_pos, feet_quat)
    d = (edges[..., :2] - ball_pos[:, None, None, :2]).norm(dim=-1)
    l_dis, r_dis = d[:, 0].min(dim=-1).values, d[:, 1].min(dim=-1).values
    min_dist = torch.minimum(l_dis, r_dis)
    acc = (ball_vel[:, :2] - self.last_ball_vel[:, :2]).norm(dim=-1)
    right = l_dis >= r_dis
    if self.last_feet is None:
      self.last_feet = feet_pos.clone()
    sel = (~right).unsqueeze(-1)
    move = torch.where(
      sel, feet_pos[:, 0, :2] - self.last_feet[:, 0, :2],
      feet_pos[:, 1, :2] - self.last_feet[:, 1, :2],
    )  # fmt: skip
    to_ball = torch.where(
      sel, ball_pos[:, :2] - feet_pos[:, 0, :2], ball_pos[:, :2] - feet_pos[:, 1, :2]
    )
    height = edges[..., 2].min(dim=-1).values  # flat ground at z = 0
    kick_h = height.gather(1, right.long().unsqueeze(1)).squeeze(1)
    allow = (
      (_wrap(torch.atan2(move[:, 1], move[:, 0]) - torch.atan2(to_ball[:, 1], to_ball[:, 0])).abs() < math.pi / 2)
      & (self.steps > 5)
      & (move.norm(dim=-1) / dt > 0.1)
      & (kick_h > 0.003)
    ) | (self.steps > 50)  # fmt: skip
    still_kick = (self.still > 10) & (acc > 0.01)
    moved_kick = (acc > 0.1) & allow
    kicked = (still_kick | moved_kick) & (min_dist < radius + 0.04)
    self.still = torch.where(ball_vel.norm(dim=-1) < 1e-4, self.still + 1, 0.0)
    self.last_feet = feet_pos.clone()
    return kicked

  def remember_ball_velocity(self, ball_vel: torch.Tensor) -> None:
    """The velocity the next step's acceleration is measured from (damped)."""
    self.last_ball_vel = ball_vel.clone()


def trial_row(
  trial: dict,
  kick_step: int,
  fell: bool,
  broken: int,
  pos: np.ndarray,  # (steps, 2) ball xy per step
  speed: np.ndarray,  # (steps,) ball speed per step
  p_kick: np.ndarray,  # (2,) ball xy at the kick
  cmd_dir: float,  # commanded direction (world, rad)
  dt: float,
) -> dict:
  """Metrics and score of one trial (bench_bhuman_kick_v2's definitions)."""
  row = dict(trial)
  kicked = kick_step >= 0
  row.update(fell=bool(fell), kicked=bool(kicked))
  if not kicked or fell:
    nan = float("nan")
    row.update(time=nan, dir_err=nan, avg_speed=nan, peak_speed=nan, distance=nan,
               path_length=nan, score=0.0)  # fmt: skip
    return row
  total = len(speed)
  s0 = kick_step
  s1 = min(s0 + int(TRACK_S / dt), broken, total)
  sp = speed[s0:s1]
  moving = np.nonzero(sp[3:] < STOP_SPEED)[0]
  if len(moving) > 0:
    s1 = s0 + 3 + int(moving[0]) + 1
    sp = speed[s0:s1]
  path = np.concatenate([p_kick[None], pos[s0:s1]], 0)
  rel = path - p_kick
  dist = np.linalg.norm(rel, axis=-1)
  final = float(dist[-1])
  errs = []
  for frac in (0.5, 0.9):
    j = int(np.argmax(dist >= frac * final)) if final > 1e-6 else len(dist) - 1
    ang = math.atan2(rel[j, 1], rel[j, 0])
    errs.append(abs((ang - cmd_dir + math.pi) % (2 * math.pi) - math.pi))
  dir_err = math.degrees(sum(errs) / 2)
  time_s = (s0 + 1) * dt
  peak = float(sp.max())
  row.update(
    time=time_s,
    dir_err=dir_err,
    avg_speed=float(sp.mean()),
    peak_speed=peak,
    distance=final,
    path_length=float(np.linalg.norm(np.diff(path, axis=0), axis=-1).sum()),
    score=score(time_s, dir_err, peak, trial["range"]),
  )
  return row


def score(time_s: float, dir_err: float, peak: float, range_m: float) -> float:
  needed = math.sqrt(2 * DECEL * range_m)
  return (
    0.5 * min(1.0, TIME_REF / time_s)
    + 0.3 * float(np.clip(1 - dir_err / ACC_REF, 0, 1))
    + 0.2 * float(np.clip(peak / needed, 0, 1))
  )


def _ms(x: list[float]) -> str:
  a = np.array([v for v in x if not math.isnan(v)])
  if len(a) == 0:
    return "-"
  return f"{a.mean():.2f} ± {a.std():.2f} ({np.median(a):.2f})"


def summarize(rows: list[dict]) -> dict:
  ok = [r for r in rows if r["kicked"] and not r["fell"]]

  def col(k: str) -> list[float]:
    return [r[k] for r in rows]

  return {
    "n": len(rows),
    "score": float(np.mean(col("score"))) if rows else float("nan"),
    "kicked": sum(r["kicked"] for r in rows),
    "fell": sum(r["fell"] for r in rows),
    "within15": sum(r["dir_err"] <= 15 for r in ok),
    "weak": sum(r["distance"] < WEAK_M for r in ok),
    "time": _ms(col("time")),
    "dir_err": _ms(col("dir_err")),
    "avg_speed": _ms(col("avg_speed")),
    "peak_speed": _ms(col("peak_speed")),
    "distance": _ms(col("distance")),
    "path_length": _ms(col("path_length")),
    "peak_mean": float(np.nanmean(col("peak_speed"))) if ok else float("nan"),
    "dist_mean": float(np.nanmean(col("distance"))) if ok else float("nan"),
    "dir_err_mean": float(np.nanmean(col("dir_err"))) if ok else float("nan"),
  }


def group(rows: list[dict]) -> dict:
  """Overall, per sector, per ball side, per cell and per kick type."""
  return {
    "overall": summarize(rows),
    "sectors": {s: summarize([r for r in rows if r["sector"] == s]) for s in SECTORS},
    "sides": {b: summarize([r for r in rows if r["side"] == b]) for b in SIDES},
    "cells": {
      f"{s}/{b}": summarize([r for r in rows if r["sector"] == s and r["side"] == b])
      for s in SECTORS
      for b in SIDES
    },
    "kinds": {
      "strong": summarize([r for r in rows if r["strong"]]),
      "normal": summarize([r for r in rows if not r["strong"]]),
    },
  }


def report(results: dict[str, dict], header: str) -> str:
  """Markdown report: overall, per sector, per side, per cell, strong vs normal."""
  names = list(results)
  out = [header, "## Overall\n"]
  out.append("| Metric | " + " | ".join(names) + " |\n|---|" + "---|" * len(names))
  rows = [
    ("**Score**", lambda s: f"**{s['score']:.3f}**"),
    ("Kicked / fell", lambda s: f"{s['kicked']} / {s['fell']}"),
    ("Kicks within 15°", lambda s: str(s["within15"])),
    (f"Weak kicks (< {WEAK_M} m)", lambda s: str(s["weak"])),
    ("Time to kick [s]", lambda s: s["time"]),
    ("Direction error [°]", lambda s: s["dir_err"]),
    ("Avg ball speed [m/s]", lambda s: s["avg_speed"]),
    ("Peak ball speed [m/s]", lambda s: s["peak_speed"]),
    ("Distance [m]", lambda s: s["distance"]),
    ("Path length [m]", lambda s: s["path_length"]),
  ]
  for label, f in rows:
    out.append(
      f"| {label} | " + " | ".join(f(results[n]["overall"]) for n in names) + " |"
    )

  def block(title: str, key: str, keys: list[str], label: str) -> None:
    out.append(f"\n## {title}\n")
    out.append(
      f"| {label} | Policy | Score | Kicked | Fell | Within 15° | Time [s] | "
      "Dir err [°] | Avg speed | Peak speed | Distance [m] |"
    )
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for k in keys:
      for n in names:
        s = results[n][key][k]
        out.append(
          f"| {k} | {n} | {s['score']:.3f} | {s['kicked']}/{s['n']} | {s['fell']} | "
          f"{s['within15']} | {s['time']} | {s['dir_err']} | {s['avg_speed']} | "
          f"{s['peak_speed']} | {s['distance']} |"
        )

  block("Per kick-direction sector", "sectors", list(SECTORS), "Sector")
  block("Per ball side", "sides", list(SIDES), "Ball side")
  block(
    "Per cell (sector / ball side)",
    "cells",
    [f"{s}/{b}" for s in SECTORS for b in SIDES],
    "Cell",
  )
  out.append("\n## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks\n")
  out.append(
    "| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |"
  )
  out.append("|---|---|---|---|---|---|")
  for n in names:
    for kind in ("strong", "normal"):
      s = results[n]["kinds"][kind]
      out.append(
        f"| {n} | {kind} | {s['score']:.3f} | {s['dir_err_mean']:.1f} | "
        f"{s['peak_mean']:.2f} | {s['dist_mean']:.2f} |"
      )
  out.append("\n## Notes\n")
  for n in names:
    sec = results[n]["sectors"]
    worst = min(sec, key=lambda k: sec[k]["score"])
    o = results[n]["overall"]
    out.append(
      f"- {n}: score {o['score']:.3f}, {o['kicked']}/{o['n']} kicked, {o['fell']} fell; "
      f"worst sector {worst} ({sec[worst]['score']:.3f})."
    )
  return "\n".join(out) + "\n"

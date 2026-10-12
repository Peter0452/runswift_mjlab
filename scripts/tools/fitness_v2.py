"""Fitness and promotion gates on kick benchmark v2 results (kick_bench2.py).

One fitness for every loop level (user, 2026-10-06/07): the primary objectives
(accuracy, time to kick, power) weigh 3, safety 2, the rest 1; every listed
metric is also a no-regression gate. A metric regresses only if it is worse
than the reference by more than its tolerance AND the 95 % CIs do not overlap.
B-Human: +2 per kick-league metric newly beaten with separated CIs (-2 lost).
"""

from __future__ import annotations

# (situation key, metric, higher is better, tolerance, weight)
P, S, R = 3.0, 2.0, 1.0  # primary, safety, rest
METRICS: list[tuple[str, str, bool, float, float]] = [
  # accuracy
  ("near_grid/camera/typical", "first_touch_15_pct", True, 6.0, P),
  ("near_grid/perfect/typical", "first_touch_15_pct", True, 6.0, P),
  ("close_any/camera/typical", "kicks_20_pct", True, 4.0, P),
  ("full_loop/camera/typical", "kicks_20_pct", True, 3.0, P),
  ("goal_grid/camera/typical", "goal_pct", True, 6.0, P),
  # time to kick
  ("close_any/camera/typical", "first_kick_cens", False, 0.4, P),
  ("approach/camera/typical", "first_kick_pct", True, 4.0, P),
  ("approach/camera/typical", "first_kick_cens", False, 0.6, P),
  ("full_loop/camera/typical", "first_kick_cens", False, 0.4, P),
  # power by range
  ("full_loop/camera/typical", "long_3d", True, 0.25, P),
  ("full_loop/camera/typical", "long_x_needed", True, 0.05, P),
  ("full_loop/camera/typical", "short_stop_m", False, 0.4, R),
  ("full_loop/camera/typical", "goals_per_ep", True, 0.06, P),
  # safety
  ("near_grid/camera/typical", "fall_pct", False, 2.0, S),
  ("close_any/camera/typical", "fall_pct", False, 1.5, S),
  ("approach/camera/typical", "fall_pct", False, 2.0, S),
  ("approach/camera/typical", "fall_pct_behind", False, 5.0, S),
  ("approach/camera/zero", "fall_pct", False, 3.0, S),
  ("approach/world/typical", "fall_pct", False, 3.0, S),
  ("full_loop/camera/typical", "fall_pct", False, 1.5, S),
  ("full_loop/push/camera/typical", "fall_pct", False, 2.0, S),
  ("goal_grid/camera/typical", "fall_pct", False, 5.0, S),
  ("goal_grid/world/zero", "fall_pct", False, 5.0, S),
  ("goal_grid/world/zero", "goal_pct", True, 6.0, P),
  ("goal_grid/unknown/camera/typical", "goal_pct", True, 6.0, P),
  ("approach/unknown/camera/typical", "first_kick_pct", True, 4.0, P),
  ("approach/unknown/camera/typical", "first_kick_cens", False, 0.6, P),
  ("approach/unknown/camera/typical", "fall_pct", False, 2.0, S),
  ("full_loop/camera/typical", "torque_sat_pct", False, 0.5, R),
  # robustness / style of play
  ("full_loop/moving/camera/typical", "goals_per_ep", True, 0.07, R),
  ("full_loop/late_detect/camera/typical", "goals_per_ep", True, 0.07, R),
  ("full_loop/bumps/camera/typical", "goals_per_ep", True, 0.07, R),
  ("full_loop/robust/camera/typical", "goals_per_ep", True, 0.07, R),
  ("approach/camera/typical", "cap_use", True, 0.05, R),
  ("full_loop/camera/typical", "fast_height_m", True, 0.006, R),
  # Smoothness as safety (user 2026-10-08: "keep action rate stable and
  # smooth while not compromising"): the loop, the kick and the approach.
  ("full_loop/camera/typical", "action_rate", False, 0.006, S),
  ("close_any/camera/typical", "action_rate", False, 0.006, S),
  ("approach/camera/typical", "action_rate", False, 0.006, S),
  # heavy ball (2026-10-07)
  ("near_grid/heavy/camera/typical", "first_touch_15_pct", True, 6.0, P),
  ("close_any/heavy/camera/typical", "kicks_20_pct", True, 4.0, P),
  ("close_any/heavy/camera/typical", "long_3d", True, 0.25, P),
  ("close_any/heavy/camera/typical", "fall_pct", False, 2.0, S),
  # long kicks without a cap: 3D speed in the loop and the close start
  ("close_any/camera/typical", "long_3d", True, 0.25, P),
  # style choice (2026-10-07, user: know when each kick style is best)
  ("full_loop/camera/typical", "style_selection_pct", True, 10.0, R),
  # Ball sizes (user 2026-10-08: faster, more accurate, more powerful than
  # B-Human for any ball): the corners of the 0.07-0.13 m training range.
  ("near_grid/large/camera/typical", "first_touch_15_pct", True, 6.0, P),
  ("close_any/large/camera/typical", "kicks_20_pct", True, 4.0, P),
  ("close_any/large/camera/typical", "long_3d", True, 0.25, P),
  ("close_any/large/camera/typical", "first_kick_cens", False, 0.4, P),
  ("close_any/large/camera/typical", "fall_pct", False, 2.0, S),
  ("near_grid/small/camera/typical", "first_touch_15_pct", True, 6.0, P),
  # Cold start with the ball behind (2026-10-09; runswift goal-grid misses).
  ("approach/behind/world/typical", "fall_pct", False, 3.0, S),
  # Quiet steps (user 2026-10-08, loud on the robot): downward foot speed just
  # before touchdown is safety; the impact force is reported alongside.
  ("full_loop/landing/camera/typical", "touchdown_speed", False, 0.02, S),
  ("full_loop/landing/camera/typical", "landing_force", False, 15.0, R),
]
# Kick league vs B-Human (both kick policies, same near-ball situations).
BHUMAN: list[tuple[str, str, bool]] = [
  ("near_grid/camera/typical", "first_touch_15_pct", True),
  ("near_grid/perfect/typical", "first_touch_15_pct", True),
  ("near_grid/camera/typical", "first_touch_speed", True),
  ("near_grid/camera/typical", "first_kick_cens", False),
  ("close_any/camera/typical", "kicks_20_pct", True),
  ("close_any/camera/typical", "first_kick_cens", False),
  ("close_any/camera/typical", "long_3d", True),
  ("close_any/camera/typical", "fall_pct", False),
]
CAPS = ("low", "high")


# Episode length per track: robots that never kick count as taking the whole
# episode ("censored" time to kick, 2026-10-08). first_kick_s alone averages
# only robots that kicked, so kicking more often (harder cases) looked slower.
TRACK_SECONDS = {"near_grid": 12.0, "close_any": 12.0, "approach": 20.0,
                 "full_loop": 30.0, "goal_grid": 115.0}  # fmt: skip


def _cens(d: dict, key: str, cap: str):
  t = d.get(key, {}).get("first_kick_s", {}).get(cap)
  p = d.get(key, {}).get("first_kick_pct", {}).get(cap)
  if not t or not p or not t[3] or not p[3] or t[0] != t[0]:
    return None
  T = TRACK_SECONDS.get(key.split("/")[0], 30.0)
  f = lambda pp, tt: pp / 100 * tt + (1 - pp / 100) * T  # noqa: E731
  return [f(p[0], t[0]), f(p[2], t[1]), f(p[1], t[2]), p[3]]


def _style_sel(d: dict, key: str, cap: str):
  """style_selection_pct recomputed from the stored style x situation table:
  share of kicks (in cells with >= 2 styles of >= 10 kicks) whose style scores
  within 5 % of the best style there (score = aim x min(1, speed / needed))."""
  tab = d.get(key, {}).get("_styles", {}).get(cap)
  if not tab:
    return None
  tot = good = 0.0
  for cell in tab.values():
    ok = {k: v for k, v in cell.items() if v[0] >= 10}
    if len(ok) < 2:
      continue
    sc = {k: v[1] * min(1.0, v[2]) for k, v in ok.items()}
    top = max(sc.values())
    tot += sum(v[0] for v in cell.values())
    good += sum(cell[k][0] for k in ok if sc[k] >= 0.95 * top)
  if tot == 0:
    return None
  p = 100.0 * good / tot
  return [p, p, p, int(tot)]


def _get(d: dict, key: str, metric: str, cap: str):
  if metric == "first_kick_cens":
    return _cens(d, key, cap)
  if metric == "style_selection_pct":
    return _style_sel(d, key, cap)
  v = d.get(key, {}).get(metric, {}).get(cap)
  return v if v and v[3] > 0 and v[0] == v[0] else None


def beats(a, b, hib: bool) -> bool:
  """a better than b with separated 95 % CIs."""
  return (a[1] > b[2]) if hib else (a[2] < b[1])


def convincing(m: dict, bh: dict) -> list[str]:
  out = []
  for key, metric, hib in BHUMAN:
    for cap in CAPS:
      a, b = _get(m, key, metric, cap), _get(bh, key, metric, cap)
      if a and b and beats(a, b, hib):
        out.append(f"{key}:{metric}:{cap}")
  return out


def score(m: dict, ref: dict, bh: dict | None = None) -> tuple[float, list[str]]:
  """Fitness of m relative to ref and its regressions (metrics present in both)."""
  total, regress = 0.0, []
  for key, metric, hib, tol, w in METRICS:
    for cap in CAPS:
      a, r = _get(m, key, metric, cap), _get(ref, key, metric, cap)
      if not a or not r:
        continue
      sgn = 1.0 if hib else -1.0
      z = max(-3.0, min(3.0, sgn * (a[0] - r[0]) / tol))
      total += w * z
      separated = (a[2] < r[1]) if hib else (a[1] > r[2])
      if z < -1.0 and separated:
        regress.append(f"{key}:{metric}:{cap}")
  if bh:
    total += 2.0 * (len(convincing(m, bh)) - len(convincing(ref, bh)))
  return total, regress

"""L2 of the reward-evolution ladder (2026-10-07): a penalty term turned into a
constraint with an adaptive Lagrange multiplier (dual ascent).

``c.<term> = r`` in KICK_GENES: after a warm-up the term's mean cost is held
at r x its warm-up level. The multiplier starts at the term's weight, rises
while the cost is above target and falls (to 0) below it, capped at 10x.
Logged as Metrics/lambda_<term>.
"""

from __future__ import annotations

from typing import Any, Callable

WARMUP_CALLS = 2000  # env steps (~80 PPO iterations at 24 steps)
EMA = 0.995


def constraint_term(func: Callable[..., Any], name: str, ratio: float, lr: float, lam0: float):
  st: dict[str, float | None] = {"lam": lam0, "ema": None, "base": None, "n": 0}

  def term(env, **params):
    c = func(env, **params)
    m = float(c.float().mean())
    st["n"] = int(st["n"] or 0) + 1
    st["ema"] = m if st["ema"] is None else EMA * float(st["ema"]) + (1 - EMA) * m
    if st["n"] == WARMUP_CALLS:
      st["base"] = st["ema"]
    if st["base"] is not None:
      target = max(ratio * float(st["base"]), 1.0e-8)
      lam = float(st["lam"]) + lr * lam0 * (float(st["ema"]) - target) / target
      st["lam"] = min(10.0 * lam0, max(0.0, lam))
    log = env.extras.setdefault("log", {})
    log[f"Metrics/lambda_{name}"] = float(st["lam"])
    return float(st["lam"]) * c

  term.__name__ = f"constraint_{name}"
  return term

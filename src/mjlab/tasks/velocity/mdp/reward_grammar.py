"""Reward grammar (L1 of docs/K1_KICK_REWARD_EVOLUTION_DESIGN.md).

A reward program is JSON: a list of terms, each either a reference to an
existing reward function (``{"name": ..., "term": "<mdp function>", "weight": w}``)
or an expression over named signals (``{"name": ..., "expr": <expr>, "weight": w}``).

Expressions (JSON trees):
  {"sig": NAME}                       a signal from SIGNALS (tensor [num_envs])
  {"const": x}
  {"mul": [e1, e2, ...]}  {"add": [...]}  {"neg": e}  {"abs": e}
  {"div": [a, b]}                      a / max(b, 1e-6)
  {"ramp": [e, lo, hi]}                clamp((e - lo) / (hi - lo), 0, 1)
  {"linear_match": [e, ref]}           1 - |e / ref - 1|, clipped at 0
  {"gauss": [e, center, sigma]}        exp(-((e - center) / sigma)^2)
  {"band": [e, lo, hi, scale]}         ((excess outside [lo, hi]) / scale)^2
  {"exp_decay": [e, scale]}            exp(-e / scale)
  {"clip": [e, lo, hi]}
  {"gt": [e, x]} {"lt": [e, x]}        1.0 / 0.0 gates
lo / hi / center / sigma / ref may themselves be expressions.

Only signals and operators listed here exist, so every program is valid and
reviewable; the search can change structure (operators, gates, couplings)
without writing free code.
"""

from __future__ import annotations

import json
import math
from typing import TYPE_CHECKING, Any, Callable

import torch

from mjlab.entity import Entity

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv


def _cmd(env):
  from mjlab.tasks.velocity.mdp.kick_loop import _kick_command

  return _kick_command(env)


def _robot(env) -> Entity:
  return env.scene["robot"]


# Signals: name -> f(env) -> [num_envs] float tensor.
SIGNALS: dict[str, Callable[[Any], torch.Tensor]] = {
  # kick events and outcomes (values held from the last kick)
  "kick_event": lambda e: _cmd(e).kick_event.float(),
  "kick_long": lambda e: _cmd(e).kick_long.float(),
  "kick_short_medium": lambda e: (~_cmd(e).kick_long).float(),
  "kick_speed": lambda e: _cmd(e).kick_speed,
  "kick_speed_needed": lambda e: _cmd(e).kick_speed_req.clamp(min=0.5),
  "kick_cos": lambda e: _cmd(e).kick_cos,
  "kick_aim_err": lambda e: torch.acos(_cmd(e).kick_cos.clamp(-1.0, 1.0)),
  "kick_quality": lambda e: _cmd(e).kick_quality,
  "kick_quality_last": lambda e: _cmd(e).last_kick_quality,
  "kick_loft": lambda e: _cmd(e).kick_loft,
  "kick_launch_angle": lambda e: _cmd(e).kick_launch_angle,
  "kick_foot_rel": lambda e: _cmd(e).kick_foot_rel,
  "kick_foot_yaw": lambda e: _cmd(e).kick_foot_yaw,
  "kick_body_speed": lambda e: _cmd(e).kick_body_speed,
  "goal_event": lambda e: _cmd(e).goal_event.float(),
  "rest_event": lambda e: _cmd(e).rest_event.float(),
  "rest_score": lambda e: _cmd(e).rest_score,
  # state
  "ball_dist": lambda e: _cmd(e).dist,
  "ball_lost": lambda e: _cmd(e).ball_lost.float(),
  "ball_seen": lambda e: _cmd(e).see_ball,
  "time_since_kick": lambda e: _cmd(e).time_since_kick,
  "walking": lambda e: _cmd(e).style_gate,
  "wz": lambda e: _robot(e).data.root_link_ang_vel_b[:, 2],
  "vx": lambda e: _robot(e).data.root_link_lin_vel_b[:, 0],
  "wz_cap": lambda e: _cmd(e).speed_limit[:, 2],
  "vx_cap": lambda e: _cmd(e).speed_limit[:, 0],
  "lost_dir": lambda e: _cmd(e).lost_dir,
  "trunk_pitch_deg": lambda e: torch.rad2deg(
    torch.atan2(
      _robot(e).data.projected_gravity_b[:, 0],
      -_robot(e).data.projected_gravity_b[:, 2],
    )
  ),
}


def _eval(expr: Any, env) -> torch.Tensor | float:
  if isinstance(expr, (int, float)):
    return float(expr)
  if not isinstance(expr, dict) or len(expr) != 1:
    raise ValueError(f"reward grammar: bad expression {expr!r}")
  ((op, arg),) = expr.items()
  if op == "sig":
    if arg not in SIGNALS:
      raise KeyError(f"reward grammar: unknown signal {arg}")
    return SIGNALS[arg](env).float()
  if op == "const":
    return float(arg)
  if op in ("mul", "add"):
    vals = [_eval(a, env) for a in arg]
    out = vals[0]
    for v in vals[1:]:
      out = out * v if op == "mul" else out + v
    return out
  if op == "neg":
    return -_eval(arg, env)
  if op == "abs":
    v = _eval(arg, env)
    return v.abs() if torch.is_tensor(v) else abs(v)
  if op == "div":
    a, b = (_eval(x, env) for x in arg)
    b = b.clamp(min=1e-6) if torch.is_tensor(b) else max(b, 1e-6)
    return a / b
  if op == "ramp":
    v, lo, hi = (_eval(x, env) for x in arg)
    return torch.clamp((v - lo) / (hi - lo), 0.0, 1.0)
  if op == "linear_match":
    v, ref = (_eval(x, env) for x in arg)
    return torch.clamp(1.0 - (v / ref - 1.0).abs(), min=0.0)
  if op == "gauss":
    v, c, s = (_eval(x, env) for x in arg)
    return torch.exp(-torch.square((v - c) / s))
  if op == "band":
    v, lo, hi, sc = (_eval(x, env) for x in arg)
    out = torch.clamp(lo - v, min=0.0) + torch.clamp(v - hi, min=0.0)
    return torch.square(out / sc)
  if op == "exp_decay":
    v, sc = (_eval(x, env) for x in arg)
    return torch.exp(-v / sc)
  if op == "clip":
    v, lo, hi = (_eval(x, env) for x in arg)
    return torch.clamp(v, lo, hi)
  if op in ("gt", "lt"):
    v, x = (_eval(a, env) for a in arg)
    return ((v > x) if op == "gt" else (v < x)).float()
  raise KeyError(f"reward grammar: unknown operator {op}")


def make_expr_term(expr: Any) -> Callable[["ManagerBasedRlEnv"], torch.Tensor]:
  """A reward function from an expression (validated at build time)."""

  def term(env: "ManagerBasedRlEnv") -> torch.Tensor:
    v = _eval(expr, env)
    if not torch.is_tensor(v):
      v = torch.full((env.num_envs,), float(v), device=env.device)
    return v

  term.__name__ = "grammar_expr"
  return term


def load_program(path: str) -> list[dict]:
  with open(path) as f:
    prog = json.load(f)
  if not isinstance(prog, list):
    raise ValueError("reward program must be a JSON list of terms")
  return prog


__all__ = ["SIGNALS", "load_program", "make_expr_term", "math"]

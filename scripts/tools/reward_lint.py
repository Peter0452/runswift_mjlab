"""Reward lint (L1 of docs/K1_KICK_REWARD_EVOLUTION_DESIGN.md): per-term reward
statistics on a checkpoint's own behaviour, with checks from K1_KICK_LESSONS.md.

usage: python scripts/tools/reward_lint.py CHECKPOINT [--steps N]

For every reward term (weight != 0), on the training config (bumps, noise,
no pushes) with the deterministic policy:
  * active %: share of env-steps where the term is non-zero;
  * share %: mean |weighted value| / mean total |weighted| over all terms;
  * per-event terms: value spread among active samples (no spread = no signal).
Flags:
  NO-SIGNAL   active but (nearly) constant where active (lesson 1)
  INERT       weight set but active < 0.1 % of steps
  DOMINANT    share > 40 % (one term drives everything)
  VANISHING   per-event term whose raw value is < 0.01 for 90 % of events
              (lesson 1: a reward far from the current behaviour has no gradient)
  PENALTY-ON-ACTION  negative per-event term larger than the positive reward
              of the same event (lesson 10: teaches avoiding the action)
"""

import os
import sys
from dataclasses import asdict

os.environ["KICK_EVAL"] = "1"

import torch  # noqa: E402

import mjlab.tasks  # noqa: E402, F401
from mjlab.envs import ManagerBasedRlEnv  # noqa: E402
from mjlab.rl import RslRlVecEnvWrapper  # noqa: E402
from mjlab.tasks.registry import (  # noqa: E402
  load_env_cfg,
  load_rl_cfg,
  load_runner_cls,
)

T = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"
EVENT_TERMS = {
  "kick_direction", "kick_vel", "kick_vel_accurate", "kick_goal", "kick_lined_up",
  "kick_double_touch", "long_kick_power", "long_kick_underpower", "kick_rest_accuracy",
  "side_foot_strike", "side_kick_bonus",
}  # fmt: skip
# Events that are binary by design (a constant value when active is intended).
BINARY_EVENTS = {"kick_lined_up", "kick_double_touch"}
KICK_REWARDS = {
  "kick_direction",
  "kick_vel",
  "kick_vel_accurate",
  "long_kick_power",
  "kick_goal",
}


def main() -> None:
  ck = sys.argv[1]
  steps = (
    int(sys.argv[sys.argv.index("--steps") + 1]) if "--steps" in sys.argv else 1500
  )
  cfg = load_env_cfg(T)
  cfg.scene.num_envs = 1024
  for k in ("push_robot", "push_near_ball"):
    cfg.events.pop(k, None)
  agent = load_rl_cfg(T)
  env = RslRlVecEnvWrapper(
    ManagerBasedRlEnv(cfg=cfg, device="cuda:0"), clip_actions=agent.clip_actions
  )
  r = load_runner_cls(T)(env, asdict(agent), device="cuda:0")
  r.load(ck, load_cfg={"actor": True}, strict=True, map_location="cuda:0")
  pol = r.get_inference_policy(device="cuda:0")
  u = env.unwrapped
  rm = u.reward_manager
  names = list(rm._term_names)
  weights = torch.tensor([float(c.weight) for c in rm._term_cfgs], device="cuda:0")
  n_t = len(names)
  active = torch.zeros(n_t, device="cuda:0")
  abs_sum = torch.zeros(n_t, device="cuda:0")
  vals: list[list[torch.Tensor]] = [[] for _ in range(n_t)]
  total = 0
  obs, _ = env.reset()
  with torch.inference_mode():
    for _ in range(steps):
      obs, _, _, _ = env.step(pol(obs))
      sr = rm._step_reward  # [envs, terms], raw * weight (rate)
      nz = sr != 0
      active += nz.float().sum(0)
      abs_sum += sr.abs().sum(0)
      total += sr.shape[0]
      for i in range(n_t):
        if names[i] in EVENT_TERMS and nz[:, i].any():
          vals[i].append(sr[nz[:, i], i])
  share = abs_sum / abs_sum.sum().clamp(min=1e-9)
  ev_reward = sum(
    float(abs_sum[names.index(k)])
    for k in KICK_REWARDS
    if k in names and weights[names.index(k)] > 0
  )
  print(f"LINT {ck}: {total} env-steps, {n_t} terms")
  print(
    "LINT term                       weight   active%   share%   event spread (p10..p90 of active)   flags"
  )
  for i in sorted(range(n_t), key=lambda i: -float(share[i])):
    if float(weights[i]) == 0.0:
      continue
    a = 100 * float(active[i]) / total
    flags = []
    spread = ""
    if vals[i]:
      v = torch.cat(vals[i])
      lo, hi = float(v.quantile(0.1)), float(v.quantile(0.9))
      spread = f"{lo:+.3g}..{hi:+.3g}"
      if (
        abs(hi - lo) < 1e-3 * max(abs(hi), abs(lo), 1e-9)
        and names[i] not in BINARY_EVENTS
      ):
        flags.append("NO-SIGNAL")
      raw90 = float((v / float(weights[i])).abs().quantile(0.9))
      if raw90 < 0.01:
        flags.append("VANISHING")  # lesson 1: ~0 at the current behaviour, no gradient
      if float(weights[i]) < 0 and float(abs_sum[i]) > 0.5 * ev_reward:
        flags.append("PENALTY-ON-ACTION")
    if (
      a < 0.1 and names[i] not in EVENT_TERMS and names[i] not in ("fall", "kick_fall")
    ):
      flags.append("INERT")  # per-step term that almost never fires
    if float(share[i]) > 0.4:
      flags.append("DOMINANT")
    print(
      f"LINT {names[i]:28s} {float(weights[i]):8.3g} {a:8.2f} {100 * float(share[i]):8.2f}"
      f"   {spread:34s} {' '.join(flags)}"
    )


if __name__ == "__main__":
  main()

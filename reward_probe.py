"""Dump the per-term reward budget of a policy at a pinned command.

Answers "what is this weight actually competing against?" — a penalty only
changes behaviour if its share of the objective is large enough to outbid the
tracking terms, and only if the behaviour it asks for is reachable at all.

  uv run python reward_probe.py --checkpoint <ckpt> --vx 1.5
"""

from __future__ import annotations

import argparse
from dataclasses import asdict

import torch

from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import MjlabOnPolicyRunner, RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.utils.torch import configure_torch_backends


def main() -> None:
  p = argparse.ArgumentParser(description=__doc__)
  p.add_argument("--task", default="Mjlab-Velocity-Quality-Booster-K1-Nubots")
  p.add_argument("--checkpoint", required=True)
  p.add_argument("--vx", type=float, default=1.5)
  p.add_argument("--wz", type=float, default=0.0)
  p.add_argument("--gait-freq", type=float, default=2.2)
  p.add_argument("--num-envs", type=int, default=256)
  p.add_argument("--steps", type=int, default=300)
  p.add_argument("--warmup", type=int, default=100)
  p.add_argument("--device", default="cuda:0")
  p.add_argument(
    "--set",
    action="append",
    default=[],
    metavar="TERM=WEIGHT",
    help="override a reward weight, e.g. --set orientation=-8",
  )
  p.add_argument(
    "--speed-ref",
    type=float,
    default=None,
    help="override speed_ref on every term that has one",
  )
  p.add_argument(
    "--track-speed-ref",
    type=float,
    default=None,
    help="inject speed_ref into the tracking terms so the positive budget grows "
    "with commanded speed",
  )
  p.add_argument(
    "--penalty-scale",
    type=float,
    default=None,
    help="pin the penalty_scale curriculum (it starts at 0.5, converges to 1.0)",
  )
  args = p.parse_args()

  configure_torch_backends()
  device = args.device

  env_cfg = load_env_cfg(args.task, play=False)
  agent_cfg = load_rl_cfg(args.task)
  env_cfg.scene.num_envs = args.num_envs

  twist = env_cfg.commands["twist"]
  twist.resampling_time_range = (1.0e9, 1.0e9)
  twist.rel_standing_envs = 0.0
  twist.rel_heading_envs = 0.0
  twist.rel_world_envs = 0.0
  twist.rel_forward_envs = 0.0
  twist.init_velocity_prob = 0.0
  twist.ranges.lin_vel_x = (args.vx, args.vx)
  twist.ranges.lin_vel_y = (0.0, 0.0)
  twist.ranges.ang_vel_z = (args.wz, args.wz)
  if twist.ranges.gait_frequency is not None:
    twist.ranges.gait_frequency = (args.gait_freq, args.gait_freq)
  if getattr(twist, "grid_curriculum", None) is not None:
    twist.grid_curriculum.enabled = False

  if args.track_speed_ref is not None:
    for name in ("tracking_lin_vel_x", "tracking_lin_vel_y", "tracking_ang_vel"):
      if name in env_cfg.rewards:
        env_cfg.rewards[name].params["speed_ref"] = args.track_speed_ref

  if args.penalty_scale is not None:
    term = env_cfg.curriculum.get("penalty_scale")
    if term is None:
      raise SystemExit("task has no penalty_scale curriculum")
    term.params["initial_scale"] = args.penalty_scale
    term.params["min_scale"] = args.penalty_scale
    term.params["max_scale"] = args.penalty_scale

  for spec in args.set:
    name, _, value = spec.partition("=")
    if name not in env_cfg.rewards:
      raise SystemExit(f"no such reward term: {name}")
    env_cfg.rewards[name].weight = float(value)
  if args.speed_ref is not None:
    for term in env_cfg.rewards.values():
      if "speed_ref" in term.params:
        term.params["speed_ref"] = args.speed_ref

  env = ManagerBasedRlEnv(cfg=env_cfg, device=device)
  env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
  unwrapped = env.unwrapped

  runner_cls = load_runner_cls(args.task) or MjlabOnPolicyRunner
  runner = runner_cls(env, asdict(agent_cfg), device=device)
  runner.load(
    args.checkpoint, load_cfg={"actor": True}, strict=True, map_location=device
  )
  policy = runner.get_inference_policy(device=device)

  rm = unwrapped.reward_manager
  terms = list(rm.active_terms)
  obs, _ = env.reset()
  obs = obs.to(device)

  totals = torch.zeros(len(terms), device=device)
  counts = 0
  clipped_steps = 0
  sampled_steps = 0
  alive = torch.ones(env.num_envs, dtype=torch.bool, device=device)
  for step in range(args.steps):
    with torch.inference_mode():
      actions = policy(obs)
    obs, _, dones, _ = env.step(actions.to(unwrapped.device))
    obs = obs.to(device)
    alive = alive & ~(dones.to(device).view(-1) > 0)
    if step < args.warmup or not alive.any():
      continue
    # _step_reward is the weighted contribution per second, per env.
    live = rm._step_reward[alive]
    totals += live.mean(dim=0)
    counts += 1
    # only_positive_rewards clamps the *total* at zero, so any step whose raw sum
    # is negative delivers exactly 0 and carries no gradient at all.
    raw_sum = live.sum(dim=1)
    clipped_steps += int((raw_sum <= 0.0).sum().item())
    sampled_steps += int(raw_sum.numel())

  mean = (totals / max(1, counts)).cpu()
  order = mean.abs().argsort(descending=True)
  pos = float(mean[mean > 0].sum())
  neg = float(mean[mean < 0].sum())

  print(f"\n=== reward budget at vx={args.vx} ({int(alive.sum())} envs alive)")
  print(f"{'term':<28s} {'weight':>8s} {'reward/s':>10s} {'share':>7s}")
  for i in order.tolist():
    w = rm.get_term_cfg(terms[i]).weight
    ref = pos if mean[i] > 0 else neg
    share = 100.0 * float(mean[i]) / ref if ref else 0.0
    print(f"{terms[i]:<28s} {w:>8.3f} {float(mean[i]):>+10.3f} {share:>6.1f}%")
  print(f"\n  positive total {pos:+.3f}/s   penalty total {neg:+.3f}/s"
        f"   net {pos + neg:+.3f}/s")
  if getattr(rm, "_only_positive_rewards", False):
    frac = 100.0 * clipped_steps / max(1, sampled_steps)
    print(f"  only_positive_rewards is ON: {frac:.1f}% of live steps have a "
          f"negative raw sum and are clamped to exactly 0 (no gradient)")

  ori = "orientation"
  if ori in terms:
    idx = terms.index(ori)
    w = rm.get_term_cfg(ori).weight
    unit = float(mean[idx]) / w  # raw cost per second, weight-independent
    print(f"\n  raw {ori} cost {unit:.4f}/s. Rescaling that weight:")
    for cand in (-2.0, -4.0, -8.0, -10.0, -12.0, -20.0):
      c = unit * cand
      print(f"    weight {cand:>6.1f} -> {c:+.3f}/s "
            f"({100.0 * abs(c) / pos:5.1f}% of the positive budget)")

  env.close()


if __name__ == "__main__":
  main()

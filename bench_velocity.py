"""Head-to-head velocity benchmark for K1 checkpoints on pinned commands.

The training-time ``Eval/score`` is ``0.6*len + 0.3*rew - 2.0*rh_rate*len``.
With ``len`` around 650 the last term moves the score by ~1300 points per unit
of ``rh_rate`` -- a ratio of termination causes -- so score differences of 60+
points are produced by ordinary run-to-run noise in that ratio rather than by
policy quality. This script instead pins the twist command to a fixed probe and
measures what we actually care about: does the robot survive, and does its
time-averaged body velocity match the command.
"""

from __future__ import annotations

import argparse
import statistics
from dataclasses import asdict
from pathlib import Path

import torch

from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import MjlabOnPolicyRunner, RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.utils.torch import configure_torch_backends

Probe = tuple[float, float, float]

DEFAULT_PROBES: tuple[Probe, ...] = (
  (0.0, 0.0, 0.0),
  (1.0, 0.0, 0.0),
  (1.5, 0.0, 0.0),
  (1.7, 0.0, 0.0),
  (2.0, 0.0, 0.0),
  (1.5, 0.0, 1.0),
  (0.0, 0.0, 1.5),
  (1.5, 0.0, 1.5),
)


def _apply_tight_arms(env_cfg) -> None:
  """Restore deploy-lineage shoulder authority (pre arm-swing unlock).

  A policy is only meaningful under the action scale it was trained with, so
  checkpoints from before the unlock must be benchmarked with the tight bands
  rather than having their shoulder outputs amplified 2.5x.
  """
  from mjlab.tasks.velocity.config.k1 import env_cfgs as e

  action = env_cfg.actions["joint_pos"]
  action.scale = dict(action.scale)
  action.clip = dict(action.clip or {})
  for name in e._NUBOTS_SHOULDER_PITCH_JOINTS:
    action.scale[name] = e._NUBOTS_SHOULDER_PITCH_SCALE
    action.clip[name] = (
      -e._NUBOTS_SHOULDER_PITCH_BAND,
      e._NUBOTS_SHOULDER_PITCH_BAND,
    )
  for name in e._NUBOTS_SHOULDER_ROLL_JOINTS:
    center = -1.3 if name.startswith("Left") else 1.3
    action.scale[name] = e._NUBOTS_SHOULDER_ROLL_SCALE
    action.clip[name] = (
      center - e._NUBOTS_SHOULDER_ROLL_BAND,
      center + e._NUBOTS_SHOULDER_ROLL_BAND,
    )


def _pin_command(env: ManagerBasedRlEnv, probe: Probe, gait_freq: float) -> None:
  term = env.command_manager.get_term("twist")
  ranges = term.cfg.ranges
  vx, vy, wz = probe
  ranges.lin_vel_x = (vx, vx)
  ranges.lin_vel_y = (vy, vy)
  ranges.ang_vel_z = (wz, wz)
  if ranges.gait_frequency is not None:
    ranges.gait_frequency = (gait_freq, gait_freq)


def _run_probe(
  env: RslRlVecEnvWrapper,
  policy,
  probe: Probe,
  steps: int,
  warmup: int,
  gait_freq: float,
  device: str,
) -> dict[str, float]:
  unwrapped = env.unwrapped
  _pin_command(unwrapped, probe, gait_freq)

  obs, _ = env.reset()
  obs = obs.to(device)

  robot = unwrapped.scene["robot"]
  num_envs = env.num_envs
  vx_cmd, vy_cmd, wz_cmd = probe

  alive = torch.ones(num_envs, dtype=torch.bool, device=device)
  vx_sum = torch.zeros(num_envs, device=device)
  wz_sum = torch.zeros(num_envs, device=device)
  vx_sq = torch.zeros(num_envs, device=device)
  n_acc = torch.zeros(num_envs, device=device)
  first_death_step = torch.full((num_envs,), float(steps), device=device)

  term_names = list(unwrapped.termination_manager.active_terms)
  term_counts = {name: 0 for name in term_names}

  for step in range(steps):
    with torch.inference_mode():
      actions = policy(obs)
    obs, _, dones, _ = env.step(actions.to(unwrapped.device))
    obs = obs.to(device)
    dones = dones.to(device).view(-1) > 0

    newly_dead = dones & alive
    if newly_dead.any():
      first_death_step[newly_dead] = float(step)
      for name in term_names:
        flags = unwrapped.termination_manager.get_term(name).to(device).view(-1)
        term_counts[name] += int((flags & newly_dead).sum().item())
      alive = alive & ~dones

    if step >= warmup:
      vx = robot.data.root_link_lin_vel_b[:, 0].to(device)
      wz = robot.data.root_link_ang_vel_b[:, 2].to(device)
      m = alive.float()
      vx_sum += vx * m
      wz_sum += wz * m
      vx_sq += vx * vx * m
      n_acc += m

  valid = n_acc > 10
  measured = float(valid.float().mean().item())
  if valid.any():
    vx_mean = vx_sum[valid] / n_acc[valid]
    wz_mean = wz_sum[valid] / n_acc[valid]
    vx_var = (vx_sq[valid] / n_acc[valid] - vx_mean**2).clamp(min=0)
  else:
    # Every env died before the warmup ended: velocity stats are undefined and
    # must not be reported as "achieved 0 m/s".
    nan = torch.full((1,), float("nan"), device=device)
    vx_mean = wz_mean = vx_var = nan

  survival = float(alive.float().mean().item())
  out = {
    "survival": survival,
    "measured": measured,
    "vx_cmd": vx_cmd,
    "vx_mean": float(vx_mean.mean().item()),
    "vx_err": float((vx_mean - vx_cmd).abs().mean().item()),
    "vx_jitter": float(vx_var.sqrt().mean().item()),
    "wz_cmd": wz_cmd,
    "wz_mean": float(wz_mean.mean().item()),
    "wz_err": float((wz_mean - wz_cmd).abs().mean().item()),
    "mean_life": float(first_death_step.mean().item()),
  }
  for name, count in term_counts.items():
    if count:
      out[f"term_{name}"] = count / num_envs
  return out


def benchmark(
  task: str,
  checkpoint: Path,
  probes: tuple[Probe, ...],
  num_envs: int,
  steps: int,
  warmup: int,
  gait_freq: float,
  device: str,
  tight_arms: bool = False,
) -> dict[Probe, dict[str, float]]:
  env_cfg = load_env_cfg(task, play=False)
  agent_cfg = load_rl_cfg(task)
  env_cfg.scene.num_envs = num_envs
  if tight_arms:
    _apply_tight_arms(env_cfg)

  twist = env_cfg.commands["twist"]
  twist.resampling_time_range = (1.0e9, 1.0e9)
  twist.rel_standing_envs = 0.0
  twist.rel_heading_envs = 0.0
  twist.rel_world_envs = 0.0
  twist.rel_forward_envs = 0.0
  twist.init_velocity_prob = 0.0
  if getattr(twist, "grid_curriculum", None) is not None:
    twist.grid_curriculum.enabled = False

  env = ManagerBasedRlEnv(cfg=env_cfg, device=device)
  env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)

  runner_cls = load_runner_cls(task) or MjlabOnPolicyRunner
  runner = runner_cls(env, asdict(agent_cfg), device=device)
  runner.load(str(checkpoint), load_cfg={"actor": True}, strict=True, map_location=device)
  policy = runner.get_inference_policy(device=device)

  results: dict[Probe, dict[str, float]] = {}
  for probe in probes:
    results[probe] = _run_probe(
      env, policy, probe, steps, warmup, gait_freq, device
    )
    r = results[probe]
    vel = (
      "vel n/a (all envs died before warmup)"
      if r["measured"] == 0.0
      else (
        f"vx={r['vx_mean']:5.2f} (err {r['vx_err']:.3f}, jit {r['vx_jitter']:.2f}) | "
        f"wz={r['wz_mean']:5.2f} (err {r['wz_err']:.3f}) | "
        f"measured={r['measured'] * 100:.0f}%"
      )
    )
    print(
      f"  probe vx={probe[0]:.2f} vy={probe[1]:.2f} wz={probe[2]:.2f} | "
      f"survive={r['survival'] * 100:5.1f}% life={r['mean_life']:6.1f} | {vel}",
      flush=True,
    )
  env.close()
  return results


def main() -> None:
  p = argparse.ArgumentParser(description=__doc__)
  p.add_argument("--task", default="Mjlab-Velocity-Quality-Booster-K1-Nubots")
  p.add_argument("--checkpoint", action="append", required=True)
  p.add_argument("--label", action="append", default=None)
  p.add_argument(
    "--arms",
    action="append",
    default=None,
    choices=["unlocked", "tight"],
    help="Shoulder authority per checkpoint, in the same order as --checkpoint.",
  )
  p.add_argument("--num-envs", type=int, default=512)
  p.add_argument("--steps", type=int, default=500)
  p.add_argument("--warmup", type=int, default=75)
  p.add_argument("--gait-freq", type=float, default=2.0)
  p.add_argument("--device", default="cuda:0")
  args = p.parse_args()

  configure_torch_backends()
  labels = args.label or [Path(c).parent.name[:28] for c in args.checkpoint]
  arms = args.arms or ["unlocked"] * len(args.checkpoint)

  all_results: dict[str, dict[Probe, dict[str, float]]] = {}
  for label, ckpt, arm in zip(labels, args.checkpoint, arms, strict=False):
    print(f"\n=== {label}  [arms={arm}]\n    {ckpt}", flush=True)
    all_results[label] = benchmark(
      args.task,
      Path(ckpt),
      DEFAULT_PROBES,
      args.num_envs,
      args.steps,
      args.warmup,
      args.gait_freq,
      args.device,
      tight_arms=(arm == "tight"),
    )

  print("\n\n================ SUMMARY ================")
  header = f"{'probe':>18s}"
  for label in all_results:
    header += f" | {label[:22]:>22s}"
  print(header)
  for probe in DEFAULT_PROBES:
    row = f"vx{probe[0]:.1f} vy{probe[1]:.1f} wz{probe[2]:.1f}".rjust(18)
    for label in all_results:
      r = all_results[label][probe]
      row += f" | surv{r['survival'] * 100:5.1f}% e{r['vx_err']:.2f}/{r['wz_err']:.2f}"
    print(row)

  print("\nAggregate (mean over probes):")
  for label, res in all_results.items():
    surv = statistics.mean(r["survival"] for r in res.values())
    vxe = statistics.mean(r["vx_err"] for r in res.values())
    wze = statistics.mean(r["wz_err"] for r in res.values())
    print(
      f"  {label[:32]:32s} survival={surv * 100:5.1f}%  "
      f"vx_err={vxe:.3f}  wz_err={wze:.3f}"
    )


if __name__ == "__main__":
  main()

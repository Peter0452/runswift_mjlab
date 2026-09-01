"""Measure the actual gait at a pinned speed to find what caps top speed.

The policy saturates around 1.6-1.8 m/s regardless of command. Three candidate
mechanisms produce that plateau, and they are distinguishable by measurement:

* geometry      -- hip excursion is already at its kinematic limit
* gait clock    -- duty factor is pinned near 0.8 with no flight phase, so the
                   stride cannot lengthen no matter what the legs could do
* actuator      -- hip/knee torque saturates during swing

This records contacts, joint angles and actuator forces over a window in which
the robot stays upright, and reports the gait decomposition ``v = L_step * rate``
alongside torque saturation, so the binding constraint can be read off directly.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

import torch

from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import MjlabOnPolicyRunner, RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.utils.torch import configure_torch_backends

TRACKED_JOINTS = (
  "Left_Hip_Pitch",
  "Right_Hip_Pitch",
  "Left_Knee_Pitch",
  "Right_Knee_Pitch",
  "Left_Ankle_Pitch",
  "Right_Ankle_Pitch",
)
EFFORT_LIMITS = {"Hip_Pitch": 30.0, "Knee_Pitch": 40.0, "Ankle_Pitch": 20.0}
SATURATION_FRACTION = 0.9
PREFALL_STEPS = 60
"""Steps of history to average before each termination (1.2 s at 50 Hz)."""


def _resolve(names: tuple[str, ...], wanted: str) -> int | None:
  if wanted in names:
    return names.index(wanted)
  for i, name in enumerate(names):
    if name.lower() == wanted.lower():
      return i
  return None


def main() -> None:
  p = argparse.ArgumentParser(description=__doc__)
  p.add_argument("--task", default="Mjlab-Velocity-Quality-Booster-K1-Nubots")
  p.add_argument("--checkpoint", required=True)
  p.add_argument("--vx", type=float, default=1.5)
  p.add_argument("--wz", type=float, default=0.0)
  p.add_argument("--gait-freq", type=float, default=2.2)
  p.add_argument("--num-envs", type=int, default=256)
  p.add_argument("--steps", type=int, default=400)
  p.add_argument("--warmup", type=int, default=100)
  p.add_argument("--device", default="cuda:0")
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

  env = ManagerBasedRlEnv(cfg=env_cfg, device=device)
  env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
  unwrapped = env.unwrapped

  runner_cls = load_runner_cls(args.task) or MjlabOnPolicyRunner
  runner = runner_cls(env, asdict(agent_cfg), device=device)
  runner.load(
    args.checkpoint, load_cfg={"actor": True}, strict=True, map_location=device
  )
  policy = runner.get_inference_policy(device=device)

  robot = unwrapped.scene["robot"]
  sensor = unwrapped.scene["feet_ground_contact"]
  primaries = list(sensor.primary_names)
  left_c, right_c = primaries.index("left_foot_link"), primaries.index(
    "right_foot_link"
  )

  joint_ids = {j: _resolve(robot.joint_names, j) for j in TRACKED_JOINTS}
  act_ids = {j: _resolve(robot.actuator_names, j) for j in TRACKED_JOINTS}
  missing = [j for j, i in joint_ids.items() if i is None]
  if missing:
    print(f"[WARN] joints not found, angles skipped: {missing}")

  dt = float(unwrapped.step_dt)
  obs, _ = env.reset()
  obs = obs.to(device)

  contacts, angles, torques = [], [], []
  vxs, heights, alives, pitches = [], [], [], []
  alive = torch.ones(env.num_envs, dtype=torch.bool, device=device)
  death_step = torch.full((env.num_envs,), -1, dtype=torch.long, device=device)
  fell_over_flag = torch.zeros(env.num_envs, dtype=torch.bool, device=device)
  term_names = list(unwrapped.termination_manager.active_terms)
  term_counts = {name: 0 for name in term_names}
  tracked = [j for j in TRACKED_JOINTS if joint_ids[j] is not None]
  tracked_act = [j for j in TRACKED_JOINTS if act_ids[j] is not None]

  for step in range(args.steps):
    with torch.inference_mode():
      actions = policy(obs)
    obs, _, dones, _ = env.step(actions.to(unwrapped.device))
    obs = obs.to(device)
    done = dones.to(device).view(-1) > 0
    newly_dead = done & alive
    if newly_dead.any():
      death_step[newly_dead] = step
      for name in term_names:
        flags = unwrapped.termination_manager.get_term(name).to(device).view(-1)
        term_counts[name] += int((flags & newly_dead).sum().item())
        if name == "fell_over":
          fell_over_flag |= flags & newly_dead
    alive = alive & ~done

    assert sensor.data.found is not None
    found = sensor.data.found
    contacts.append(
      torch.stack([found[:, left_c] > 0, found[:, right_c] > 0], dim=-1).to(device)
    )
    jp = robot.data.joint_pos
    af = robot.data.actuator_force
    angles.append(
      torch.stack([jp[:, joint_ids[j]] for j in tracked], dim=-1).to(device)
    )
    torques.append(
      torch.stack([af[:, act_ids[j]] for j in tracked_act], dim=-1).to(device)
    )
    # projected gravity x is sin(pitch): positive = nose-down / forward tilt.
    pitches.append(robot.data.projected_gravity_b[:, 0].to(device))
    vxs.append(robot.data.root_link_lin_vel_b[:, 0].to(device))
    heights.append(robot.data.root_link_pos_w[:, 2].to(device))
    alives.append(alive.clone())

  contact_all = torch.stack(contacts)
  angle_all = torch.stack(angles)
  torque_all = torch.stack(torques)
  pitch_all = torch.stack(pitches)

  contact = contact_all[args.warmup :]
  angle = angle_all[args.warmup :]
  torque = torque_all[args.warmup :]
  vx = torch.stack(vxs)[args.warmup :]
  height = torch.stack(heights)[args.warmup :]
  hip = angle[..., [tracked.index(j) for j in tracked if "Hip" in j]]
  knee = angle[..., [tracked.index(j) for j in tracked if "Knee" in j]]

  keep = alive
  n_keep = int(keep.sum().item())
  window = contact.shape[0]
  print(f"\n=== gait at vx={args.vx} wz={args.wz} gait_freq={args.gait_freq}")
  print(f"checkpoint : {Path(args.checkpoint).name}")
  print(
    f"envs upright for the whole {window * dt:.1f}s window: "
    f"{n_keep}/{env.num_envs} ({100.0 * n_keep / env.num_envs:.0f}%)"
  )
  fallen = env.num_envs - n_keep
  if fallen:
    causes = ", ".join(
      f"{name}={100.0 * count / fallen:.0f}%"
      for name, count in sorted(term_counts.items(), key=lambda kv: -kv[1])
      if count
    )
    print(f"failure causes (share of the {fallen} that ended): {causes}")

  if n_keep < 8:
    print("[WARN] too few survivors for reliable gait stats; lower --vx or --steps")
    if n_keep == 0:
      env.close()
      return

  c = contact[:, keep]  # [T, K, 2]
  left, right = c[..., 0], c[..., 1]
  duty_l = left.float().mean().item()
  duty_r = right.float().mean().item()
  double = (left & right).float().mean().item()
  flight = (~left & ~right).float().mean().item()

  touchdown = (c[1:] & ~c[:-1]).float().sum(dim=0)  # [K, 2]
  steps_per_s = touchdown.sum(dim=-1) / (window * dt)
  mean_vx = vx[:, keep].mean().item()
  rate = steps_per_s.mean().item()
  step_len = mean_vx / rate if rate > 1e-6 else float("nan")

  hip_pp = (hip[:, keep].amax(dim=0) - hip[:, keep].amin(dim=0)).mean().item()
  knee_max = knee[:, keep].abs().amax(dim=0).mean().item()
  knee_min = knee[:, keep].abs().amin(dim=0).mean().item()

  print(f"\n  mean forward speed      : {mean_vx:.2f} m/s (cmd {args.vx:.2f})")
  print(f"  mean root height        : {height[:, keep].mean().item():.3f} m")
  print(f"  step rate               : {rate:.2f} steps/s  "
        f"(= {rate / 2.0:.2f} Hz cycle, cmd {args.gait_freq:.2f} Hz)")
  print(f"  implied step length     : {step_len:.3f} m")
  print(f"\n  duty factor L / R       : {duty_l:.3f} / {duty_r:.3f}  "
        f"(gait clock implies {1.0 - 0.2:.2f})")
  print(f"  double support fraction : {double:.3f}")
  print(f"  flight fraction         : {flight:.3f}")
  print(f"\n  hip pitch peak-to-peak  : {hip_pp:.3f} rad "
        f"({hip_pp * 57.2958:.1f} deg)")
  print(f"  knee flexion range      : {knee_min:.3f} -> {knee_max:.3f} rad "
        f"({knee_min * 57.2958:.0f} -> {knee_max * 57.2958:.0f} deg)")

  steady_pitch = pitch_all[args.warmup :][:, keep]
  print(
    f"\n  forward tilt while stable: sin(pitch)={steady_pitch.mean().item():+.3f} "
    f"({torch.asin(steady_pitch.clamp(-1, 1)).mean().item() * 57.2958:+.1f} deg), "
    f"max={torch.asin(steady_pitch.clamp(-1, 1)).amax().item() * 57.2958:+.1f} deg"
  )

  tipped = fell_over_flag & (death_step >= PREFALL_STEPS)
  n_tipped = int(tipped.sum().item())
  if n_tipped >= 8:
    idx = tipped.nonzero(as_tuple=False).view(-1)
    offsets = torch.arange(-PREFALL_STEPS, 0, device=device)
    rows = death_step[idx].view(-1, 1) + offsets.view(1, -1)  # [K, P]
    traj = pitch_all[rows, idx.view(-1, 1)]  # [K, P]
    traj = torch.asin(traj.clamp(-1, 1)) * 57.2958
    print(f"\n  pitch run-up for the {n_tipped} envs that tipped over "
          f"(deg before the fall):")
    marks = [60, 50, 40, 30, 20, 15, 10, 5, 2, 1]
    cells = " ".join(f"t-{m:<2d}:{traj[:, -m].mean().item():+6.1f}" for m in marks)
    print(f"    {cells}")

  print("\n  torque saturation (|tau| >= "
        f"{SATURATION_FRACTION:.0%} of limit):")
  tq = torque[:, keep]
  for i, name in enumerate(tracked_act):
    limit = next(v for k, v in EFFORT_LIMITS.items() if k in name)
    lo, hi = tq[..., i].amin().item(), tq[..., i].amax().item()
    at_lo = float((tq[..., i] <= -SATURATION_FRACTION * limit).float().mean()) * 100
    at_hi = float((tq[..., i] >= SATURATION_FRACTION * limit).float().mean()) * 100
    mag = tq[..., i].abs()
    print(
      f"    {name:<18s} mean={mag.mean().item():5.1f} of {limit:3.0f} Nm  "
      f"range=[{lo:+6.1f},{hi:+6.1f}]  "
      f"pinned neg {at_lo:5.1f}% / pos {at_hi:5.1f}%"
    )

  env.close()


if __name__ == "__main__":
  main()

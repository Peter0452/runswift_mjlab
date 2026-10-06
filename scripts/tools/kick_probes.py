"""K1 kick-loop probes beyond eval_kick_loop.py (stage-3 task).

usage: python scripts/tools/kick_probes.py CHECKPOINT MODE
  range  flat, nominal 0.1 kg ball, no pushes / vision noise: per kick range,
         ball speed vs the speed the target needs, near-ball wait, where short /
         medium passes stop, all-kick speed distribution, kicking-foot speed
  lean   trunk pitch, height, knee, heel-up per forward-speed bin while walking
  caps   forward speed vs the vx cap while chasing (ball > 1.5 m, no recent kick)
  chase  cap 2.0 m/s, ball 8 m straight ahead: forward speed on the way
  side   side drills: ball launch angle off the body heading, side-kick accuracy

Rebuilt 2026-10-05 from the scratch probes used up to v54b; the caps / chase
gates may differ slightly from those, so compare checkpoints within one version.
"""

import math
import os
import sys
from dataclasses import asdict

import torch

os.environ["KICK_EVAL"] = "1"  # no mid-kick starts in evaluation

import mjlab.tasks  # noqa: F401  # isort: skip
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.tasks.velocity.mdp.kick_loop import required_kick_speed
from mjlab.utils.lab_api.math import euler_xyz_from_quat, wrap_to_pi

TASK = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"
DEV = "cuda:0"


def make(ck, edit, n=1024):
  cfg = load_env_cfg(TASK)
  cfg.scene.num_envs = n
  for k in ("push_robot", "push_near_ball"):
    cfg.events.pop(k, None)
  edit(cfg)
  agent = load_rl_cfg(TASK)
  env = RslRlVecEnvWrapper(
    ManagerBasedRlEnv(cfg=cfg, device=DEV), clip_actions=agent.clip_actions
  )
  r = load_runner_cls(TASK)(env, asdict(agent), device=DEV)
  r.load(ck, load_cfg={"actor": True}, strict=True, map_location=DEV)
  pol = r.get_inference_policy(device=DEV)
  obs, _ = env.reset()
  u = env.unwrapped
  return env, pol, obs, u, u.command_manager.get_term("twist")


def flat_nominal(cfg):
  for k in ("ball_mass", "ball_friction", "ball_bounce"):
    cfg.events.pop(k, None)
  cfg.scene.terrain.terrain_type = "plane"
  cfg.scene.terrain.terrain_generator = None
  cfg.commands["twist"].vision_dropout = 0.0
  cfg.commands["twist"].vision_delay_steps = (0, 0)


def q(x, p):
  return float(x.quantile(p)) if len(x) else float("nan")


def probe_range(ck):
  env, pol, obs, u, cmd = make(ck, flat_nominal)
  ball = u.scene["ball"]
  n = u.num_envs
  sp, req, wait = ([[] for _ in range(3)] for _ in range(3))
  miss, tol = [[], []], [[], []]
  foot = []
  stall = torch.zeros(3, device=DEV)
  near = torch.zeros(3, device=DEV)
  kr = torch.zeros(n, dtype=torch.long, device=DEV)
  with torch.inference_mode():
    for _ in range(1500):
      rng = cmd.kick_range.argmax(-1).clone()
      td = cmd.target_dist.clone()
      obs, _, _, _ = env.step(pol(obs))
      k = cmd.kick_event
      kr = torch.where(k, rng, kr)
      foot.append(cmd.kick_foot_rel[k])
      for i in range(3):
        m = k & (rng == i)
        sp[i].append(cmd.kick_speed[m])
        req[i].append(required_kick_speed(td[m]))
        wait[i].append(cmd.kick_near_time[m])
        nb = cmd.near_pending & (rng == i)
        near[i] += nb.sum()
        stall[i] += (nb & (cmd.near_time > 3.0)).sum()
      ev = cmd.rest_event
      if ev.any():
        d = (ball.data.root_link_pos_w[:, :2] - cmd.rest_target_w).norm(dim=-1)
        for i in range(2):
          mm = ev & (kr == i)
          miss[i].append(d[mm])
          tol[i].append(cmd.rest_tol[mm])
  for i, name in enumerate(("short ", "medium", "long  ")):
    s, rq, w = torch.cat(sp[i]), torch.cat(req[i]), torch.cat(wait[i])
    ratio = s / rq.clamp(min=0.1)
    print(
      f"RANGE {name} kicks {len(s):4d} | speed {s.mean():.2f} m/s (p90 {q(s, 0.9):.2f})"
      f" vs needed {rq.mean():.2f} | x needed p50 {q(ratio, 0.5):.2f}, <0.7x"
      f" {100 * (ratio < 0.7).float().mean():.0f} %, >2x {100 * (ratio > 2).float().mean():.0f} %"
      f" | wait near ball {w.mean():.2f} s, waits >3 s"
      f" {100 * stall[i] / near[i].clamp(min=1):.0f} % of near time"
    )
  for i, name in enumerate(("short ", "medium")):
    m, t = torch.cat(miss[i]), torch.cat(tol[i])
    if len(m):
      print(
        f"REST {name} rested {len(m)} | stop from target p50 {q(m, 0.5):.2f} m"
        f" p90 {q(m, 0.9):.2f} | within tolerance {100 * (m <= t).float().mean():.0f} %"
      )
  s = torch.cat([torch.cat(x) for x in sp])
  f = torch.cat(foot)
  print(
    f"NOMINAL all kicks {len(s)}: p50 {q(s, 0.5):.2f} p90 {q(s, 0.9):.2f} max"
    f" {s.max():.2f} m/s, >= 7 m/s {100 * (s >= 7).float().mean():.1f} % | foot rel"
    f" p50 {q(f, 0.5):.2f} p90 {q(f, 0.9):.2f} max {f.max():.2f} m/s"
  )


def probe_lean(ck):
  env, pol, obs, u, cmd = make(ck, lambda c: None)
  rob = u.scene["robot"]
  feet, _ = rob.find_bodies(("left_foot_link", "right_foot_link"), preserve_order=True)
  knees, _ = rob.find_joints((r".*_Knee_Pitch",))
  bins = torch.tensor([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5], device=DEV)
  P, H, K, U = ([[] for _ in range(6)] for _ in range(4))
  with torch.inference_mode():
    for t in range(1200):
      obs, _, _, _ = env.step(pol(obs))
      if t < 50:
        continue
      vx = rob.data.root_link_lin_vel_b[:, 0]
      g = rob.data.projected_gravity_b
      pitch = torch.rad2deg(torch.atan2(g[:, 0], -g[:, 2]))
      walking = (cmd.dist > 1.0) & (cmd.time_since_kick > 2.0)
      b = torch.bucketize(vx, bins) - 1
      con = u.scene["feet_ground_contact"].data.found.reshape(u.num_envs, -1)[:, :2] > 0
      _, fp, _ = euler_xyz_from_quat(rob.data.body_link_quat_w[:, feet].reshape(-1, 4))
      up = (wrap_to_pi(fp).reshape(-1, 2) > math.radians(5.0)) & con
      for i in range(6):
        m = walking & (b == i)
        P[i].append(pitch[m])
        H[i].append(rob.data.root_link_pos_w[m, 2])
        K[i].append(rob.data.joint_pos[m][:, knees].mean(-1))
        U[i].append(up[m][con[m]])
  print("LEAN speed     share  pitch mean / p90 (deg, + fwd)  height  knee  heel-up")
  tot = sum(len(torch.cat(P[i])) for i in range(6))
  for i in range(6):
    p, h, k, hu = (torch.cat(x[i]) for x in (P, H, K, U))
    if not len(p):
      continue
    print(
      f"LEAN {bins[i]:.1f}-{bins[i + 1]:.1f} m/s {100 * len(p) / tot:4.0f}%"
      f"   {p.mean():+5.1f} / {q(p, 0.9):+5.1f}   {h.mean():.3f}  {k.mean():.2f}"
      f"  {100 * hu.float().mean():4.1f}%"
    )


def probe_caps(ck):
  env, pol, obs, u, cmd = make(ck, lambda c: None)
  rob = u.scene["robot"]
  bins = torch.tensor([0.3, 0.6, 0.9, 1.2, 1.6, 2.01], device=DEV)
  V, C = [[] for _ in range(5)], [[] for _ in range(5)]
  with torch.inference_mode():
    for t in range(1200):
      obs, _, _, _ = env.step(pol(obs))
      if t < 50:
        continue
      cap = cmd.speed_limit[:, 0]
      vx = rob.data.root_link_lin_vel_b[:, 0]
      chase = (cmd.dist > 1.5) & (cmd.time_since_kick > 2.0)
      b = torch.bucketize(cap, bins) - 1
      for i in range(5):
        m = chase & (b == i)
        V[i].append(vx[m])
        C[i].append(cap[m])
  for i in range(5):
    v, c = torch.cat(V[i]), torch.cat(C[i])
    print(
      f"CAPS cap {bins[i]:.1f}-{bins[i + 1]:.1f}: vx mean {v.mean():.2f} p90"
      f" {q(v, 0.9):.2f} (cap mean {c.mean():.2f}), over cap by >0.1"
      f" {100 * ((v - c) > 0.1).float().mean():.0f} %"
    )


def probe_chase(ck):
  def edit(cfg):
    flat_nominal(cfg)
    t = cfg.commands["twist"]
    t.ball_distance_range = (8.0, 8.0)
    t.spawn_view_half_angle = 0.0
    if getattr(t, "speed_cap_final", None) is not None:
      t.speed_cap_final = ((2.0, 2.0), (1.5, 1.5), (1.5, 1.5))
      t.speed_cap_start_max = (2.0, 1.5, 1.5)
    t.speed_limit_vx = (2.0, 2.0)

  env, pol, obs, u, cmd = make(ck, edit, n=512)
  rob = u.scene["robot"]
  V, P, H = [], [], []
  with torch.inference_mode():
    for t in range(300):
      obs, _, _, _ = env.step(pol(obs))
      if t < 25:
        continue
      m = (cmd.dist > 2.0) & (cmd.time_since_kick > 2.0)
      g = rob.data.projected_gravity_b
      V.append(rob.data.root_link_lin_vel_b[m, 0])
      P.append(torch.rad2deg(torch.atan2(g[m, 0], -g[m, 2])))
      H.append(rob.data.root_link_pos_w[m, 2])
  v, p, h = torch.cat(V), torch.cat(P), torch.cat(H)
  print(
    f"CHASE cap {cmd.speed_limit[:, 0].mean():.2f}, ball 8 m ahead: vx mean {v.mean():.2f}"
    f" p50 {q(v, 0.5):.2f} p90 {q(v, 0.9):.2f} max {v.max():.2f} m/s | pitch"
    f" {p.mean():+.1f} deg | height {h.mean():.3f} m"
  )


def probe_side(ck):
  def edit(cfg):
    cfg.commands["twist"].side_drill_prob = 1.0

  env, pol, obs, u, cmd = make(ck, edit)
  rob, ball = u.scene["robot"], u.scene["ball"]
  n = u.num_envs
  pending = torch.zeros(n, dtype=torch.bool, device=DEV)
  age = torch.zeros(n, device=DEV)
  rel, aim = [], []

  def yaw(qt):
    return torch.atan2(
      2 * (qt[:, 0] * qt[:, 3] + qt[:, 1] * qt[:, 2]),
      1 - 2 * (qt[:, 2] ** 2 + qt[:, 3] ** 2),
    )

  with torch.inference_mode():
    for _ in range(1500):
      obs, _, _, _ = env.step(pol(obs))
      k = cmd.kick_event.clone()
      pending |= k
      age = torch.where(k, torch.zeros_like(age), age + 1)
      ready = pending & (age == 3)
      if ready.any():
        v = ball.data.root_link_vel_w[ready, :2]
        bd = torch.atan2(v[:, 1], v[:, 0])
        rel.append(wrap_to_pi(bd - yaw(rob.data.root_link_quat_w[ready])).abs())
        to = cmd.target_w[ready] - ball.data.root_link_pos_w[ready, :2]
        aim.append(wrap_to_pi(bd - torch.atan2(to[:, 1], to[:, 0])).abs())
        pending &= ~ready
  rel, aim = torch.rad2deg(torch.cat(rel)), torch.rad2deg(torch.cat(aim))
  side = rel > 45
  print(
    f"SIDE kicks {len(rel)}: > 45 deg off heading {100 * side.float().mean():.1f} %,"
    f" > 70 deg {100 * (rel > 70).float().mean():.1f} % | within 20 deg: front"
    f" {100 * (aim[~side] <= 20).float().mean():.0f} %, side"
    f" {100 * (aim[side] <= 20).float().mean():.0f} % (n={int(side.sum())})"
  )


def probe_loft(ck):
  """Launch angle, vertical speed and peak height of the ball after each kick
  (flat, nominal ball): how many kicks are air balls."""
  env, pol, obs, u, cmd = make(ck, flat_nominal)
  ball = u.scene["ball"]
  n = u.num_envs
  age = torch.full((n,), 99, device=DEV)
  peak = torch.zeros(n, device=DEV)
  z0 = torch.zeros(n, device=DEV)
  rng_k = torch.zeros(n, dtype=torch.long, device=DEV)
  ang, vzs, vxy, peaks, rngs = [], [], [], [], []
  with torch.inference_mode():
    for _ in range(1500):
      rng = cmd.kick_range.argmax(-1).clone()
      obs, _, _, _ = env.step(pol(obs))
      k = cmd.kick_event
      z = ball.data.root_link_pos_w[:, 2]
      z0 = torch.where(k, z, z0)
      rng_k = torch.where(k, rng, rng_k)
      age = torch.where(k, torch.zeros_like(age), age + 1)
      peak = torch.where(k, torch.zeros_like(peak), torch.maximum(peak, z - z0))
      at3 = age == 2
      if at3.any():
        v = ball.data.root_link_lin_vel_w[at3]
        h = v[:, :2].norm(dim=-1)
        vxy.append(h)
        vzs.append(v[:, 2])
        ang.append(torch.rad2deg(torch.atan2(v[:, 2], h.clamp(min=1e-3))))
      done = age == 40
      if done.any():
        peaks.append(peak[done])
        rngs.append(rng_k[done])
  a, vz, h = torch.cat(ang), torch.cat(vzs), torch.cat(vxy)
  pk, rk = torch.cat(peaks), torch.cat(rngs)
  print(
    f"LOFT kicks {len(a)}: launch angle p50 {q(a, 0.5):+.1f} p90 {q(a, 0.9):+.1f} deg,"
    f" vz p50 {q(vz, 0.5):+.2f} p90 {q(vz, 0.9):+.2f} m/s, ground speed p50 {q(h, 0.5):.2f}"
  )
  for i, name in enumerate(("short ", "medium", "long  ")):
    m = pk[rk == i]
    if len(m):
      print(
        f"LOFT {name} peak height p50 {100 * q(m, 0.5):.1f} cm p90 {100 * q(m, 0.9):.1f} cm,"
        f" air balls (> 5 cm) {100 * (m > 0.05).float().mean():.0f} %,"
        f" (> 15 cm) {100 * (m > 0.15).float().mean():.0f} %"
      )


def probe_search(ck):
  """Every 6 s, move the ball (unseen) to a random spot 1.5-4 m away outside the
  camera view, stopped. Measure time to see it again and how the robot moves
  while it is unseen: backward walking vs turning on the spot."""

  def edit(cfg):
    flat_nominal(cfg)
    cfg.commands["twist"].vision_dropout = 0.0

  env, pol, obs, u, cmd = make(ck, edit)
  rob, ball = u.scene["robot"], u.scene["ball"]
  n = u.num_envs
  ids = torch.arange(n, device=DEV)
  lost_t = torch.full((n,), -1.0, device=DEV)
  found, back, turn, fwd, steps = [], 0, 0, 0, 0
  wz_sum, wz_cap_sum, lost_sum = 0.0, 0.0, 0
  net = torch.zeros(n, device=DEV)
  nets = []
  found_n = torch.zeros((), device=DEV)
  tried = 0
  dt = u.step_dt
  with torch.inference_mode():
    for t in range(1800):
      if t % 300 == 100:
        # stale the robot's belief: put the ball out of view, at rest
        yaw = torch.atan2(
          2 * (rob.data.root_link_quat_w[:, 0] * rob.data.root_link_quat_w[:, 3]),
          1 - 2 * rob.data.root_link_quat_w[:, 3] ** 2,
        )
        ang = yaw + torch.empty(n, device=DEV).uniform_(1.2, 2 * math.pi - 1.2)
        r = torch.empty(n, device=DEV).uniform_(1.5, 4.0)
        st = ball.data.default_root_state.clone()
        st[:, :2] = rob.data.root_link_pos_w[:, :2] + r[:, None] * torch.stack(
          (ang.cos(), ang.sin()), -1
        )
        st[:, 2] = ball.data.root_link_pos_w[:, 2]
        st[:, 7:] = 0.0
        ball.write_root_state_to_sim(st, ids)
        lost_t[:] = 0.0
        tried += n
      obs, _, _, _ = env.step(pol(obs))
      active = lost_t >= 0
      seen = cmd.see_ball > 0.5
      hit = active & seen & (lost_t > 0.1)
      found.append(lost_t[hit])
      found_n += hit.sum()
      lost_t = torch.where(hit, torch.full_like(lost_t, -1.0), lost_t)
      searching = active & ~seen
      vx = rob.data.root_link_lin_vel_b[:, 0]
      wz = rob.data.root_link_ang_vel_b[:, 2]
      steps += int(searching.sum())
      back += int((searching & (vx < -0.1)).sum())
      fwd += int((searching & (vx > 0.1)).sum())
      turn += int((searching & (wz.abs() > 0.5 * cmd.speed_limit[:, 2])).sum())
      wz_sum += float((wz.abs() * searching).sum())
      wz_cap_sum += float((cmd.speed_limit[:, 2] * searching).sum())
      lost_sum += int((searching & cmd.ball_lost).sum()) if hasattr(cmd, "ball_lost") else 0
      net = torch.where(searching, net + wz * dt, net)
      ended = (hit | (lost_t > 6.0 - dt)) & active
      nets.append(net[ended].abs())
      net = torch.where(ended, torch.zeros_like(net), net)
      lost_t = torch.where(active & ~hit, lost_t + dt, lost_t)
      lost_t = torch.where(lost_t > 6.0, torch.full_like(lost_t, -1.0), lost_t)
  f = torch.cat(found)
  print(
    f"SEARCH relocations {tried}: re-found within 6 s {100 * found_n / tried:.0f} %,"
    f" time to re-find p50 {q(f, 0.5):.2f} s p90 {q(f, 0.9):.2f} s | while unseen:"
    f" walking backward {100 * back / max(steps, 1):.0f} %, forward"
    f" {100 * fwd / max(steps, 1):.0f} %, turning (|wz| > half cap)"
    f" {100 * turn / max(steps, 1):.0f} %, |wz| mean {wz_sum / max(steps, 1):.2f} rad/s"
    f" (cap mean {wz_cap_sum / max(steps, 1):.2f}), memory marked lost"
    f" {100 * lost_sum / max(steps, 1):.0f} % of unseen time, net heading change"
    f" per search p50 {q(torch.cat(nets), .5):.2f} rad"
  )


def probe_approach(ck):
  """Approach from far: ball 3-8 m away at any bearing (caps as sampled).
  Time to the first kick, share kicking within 15 s, first kick on target,
  and the mean forward speed while the ball is > 2 m away."""

  def edit(cfg):
    flat_nominal(cfg)
    t = cfg.commands["twist"]
    t.ball_distance_range = (3.0, 8.0)
    t.spawn_view_half_angle = math.pi

  env, pol, obs, u, cmd = make(ck, edit)
  rob = u.scene["robot"]
  n = u.num_envs
  first = torch.full((n,), float("nan"), device=DEV)
  on_t = torch.zeros(n, dtype=torch.bool, device=DEV)
  fell = torch.zeros(n, dtype=torch.bool, device=DEV)
  V = []
  with torch.inference_mode():
    for t in range(750):
      obs, _, _, _ = env.step(pol(obs))
      k = cmd.kick_event & torch.isnan(first)
      first = torch.where(k, torch.full_like(first, t * u.step_dt), first)
      on_t = torch.where(k, cmd.kick_cos > math.cos(math.radians(20)), on_t)
      fell |= torch.isnan(first) & (rob.data.root_link_pos_w[:, 2] < 0.35)
      far = torch.isnan(first) & (cmd.dist > 2.0)
      V.append(rob.data.root_link_lin_vel_b[far, 0])
  ok = ~torch.isnan(first)
  v = torch.cat(V)
  print(
    f"APPROACH far start (3-8 m, any bearing): kicked within 15 s {100 * ok.float().mean():.0f} %,"
    f" first kick p50 {q(first[ok], .5):.2f} s p90 {q(first[ok], .9):.2f} s, on target"
    f" {100 * on_t[ok].float().mean():.0f} %, fell before kicking {100 * fell.float().mean():.1f} %,"
    f" approach vx mean {v.mean():.2f} m/s"
  )


if __name__ == "__main__":
  {
    "range": probe_range,
    "lean": probe_lean,
    "caps": probe_caps,
    "chase": probe_chase,
    "side": probe_side,
    "loft": probe_loft,
    "search": probe_search,
    "approach": probe_approach,
  }[sys.argv[2]](sys.argv[1])

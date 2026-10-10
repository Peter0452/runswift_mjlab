"""Our policy on runswift's kick-comparison grid, inside our training sim.

runswift/benchmarks/kick_policies (2026-10-06) runs 36 tasks from a standing
start: ball 0.40 / 0.75 / 1.10 m ahead at -0.12 / 0 / +0.12 m lateral, aim
-15 / 0 / +15 deg, range 3 m; range 6 / 9 m at 0.75 m; and an incoming ball.
Speed caps 0.5 / 0.3 / 0.6, perfect ball. First strike = first ball launch
(>= 0.5 m/s, change >= 0.3 m/s) with foot contact in the last 0.15 s; its
direction = peak planar ball velocity in the next 0.2 s. Success = within 15 deg.
This replays that protocol here to separate scenario / scoring effects from
simulator differences.

usage: python scripts/tools/runswift_scenario.py CK [--caps vx,vy,wz] [--repeats N]
"""

import math
import os
import sys
from dataclasses import asdict

import torch

os.environ["KICK_EVAL"] = "1"

import mjlab.tasks  # noqa: F401  # isort: skip
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.utils.lab_api.math import quat_apply_inverse, yaw_quat

TASK = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"
DEPLOY_Q_LIMITS = {
  "Head_Yaw": (-1.0, 1.0),
  "Head_Pitch": (-0.349, 0.855),
  "Left_Shoulder_Pitch": (-3.316, 1.22),
  "Left_Shoulder_Roll": (-1.74, 1.57),
  "Left_Elbow_Pitch": (-2.27, 2.27),
  "Left_Elbow_Yaw": (-2.44, 0.0),
  "Right_Shoulder_Pitch": (-3.316, 1.22),
  "Right_Shoulder_Roll": (-1.57, 1.74),
  "Right_Elbow_Pitch": (-2.27, 2.27),
  "Right_Elbow_Yaw": (0.0, 2.44),
  ".*_Hip_Pitch": (-3.0, 2.21),
  "Left_Hip_Roll": (-0.4, 1.57),
  "Right_Hip_Roll": (-1.57, 0.4),
  ".*_Hip_Yaw": (-1.0, 1.0),
  ".*_Knee_Pitch": (0.0, 2.23),
  ".*_Ankle_Pitch": (-0.87, 0.345),
  ".*_Ankle_Roll": (-0.345, 0.345),
}
DEV = "cuda:0"


def cases() -> list[tuple[str, float, float, float, float, float]]:
  out = []
  for x in (0.40, 0.75, 1.10):
    for y in (-0.12, 0.0, 0.12):
      for h in (-15.0, 0.0, 15.0):
        out.append((f"near-x{x:.2f}-y{y:+.2f}-aim{h:+.0f}", x, y, h, 3.0, 0.0))
  for r in (6.0, 9.0):
    for y in (-0.12, 0.0, 0.12):
      out.append((f"range-{r:.0f}-y{y:+.2f}", 0.75, y, 0.0, r, 0.0))
  for y in (-0.12, 0.0, 0.12):
    out.append((f"incoming-y{y:+.2f}", 0.90, y, 0.0, 3.0, -0.2))
  return out


def main() -> None:
  ck = sys.argv[1]
  caps = (
    [float(v) for v in sys.argv[sys.argv.index("--caps") + 1].split(",")]
    if "--caps" in sys.argv
    else [0.5, 0.3, 0.6]
  )
  reps = int(sys.argv[sys.argv.index("--repeats") + 1]) if "--repeats" in sys.argv else 3
  cs = cases()
  n = len(cs) * reps
  cfg = load_env_cfg(TASK, play=True)
  cfg.scene.num_envs = n
  for k in list(cfg.events):
    if k.startswith("push") or k.startswith("ball_") or k == "ball_relocate_unseen":
      cfg.events.pop(k, None)
  tw = cfg.commands["twist"]
  tw.fov_half_angle = math.pi
  tw.fov_vertical_half_angle = None
  tw.ball_obs_noise = (0.0, 0.0)
  tw.vision_dropout = 0.0
  tw.vision_delay_steps = (0, 0)
  tw.resampling_time_range = (1.0e6, 1.0e6)
  cfg.episode_length_s = 100.0
  if "--deploy-clip" in sys.argv:
    # k1_policy_runner walk_policy_amp_v1.Q_ABS_LIMITS: the runner (robot and
    # runswift fixture) clips every joint target to these before sending.
    cfg.actions["joint_pos"].clip = DEPLOY_Q_LIMITS
  if "--dt2" in sys.argv:
    cfg.sim.mujoco.timestep = 0.002
    cfg.decimation = 10
  if "--euler" in sys.argv:
    cfg.sim.mujoco.integrator = "euler"
  if "--no-delay" in sys.argv:
    import dataclasses

    robot = cfg.scene.entities["robot"]
    robot.articulation = dataclasses.replace(
      robot.articulation,
      actuators=tuple(
        dataclasses.replace(a, delay_min_lag=0, delay_max_lag=0)
        for a in robot.articulation.actuators
      ),
    )
  agent = load_rl_cfg(TASK)
  env = RslRlVecEnvWrapper(
    ManagerBasedRlEnv(cfg=cfg, device=DEV), clip_actions=agent.clip_actions
  )
  r = load_runner_cls(TASK)(env, asdict(agent), device=DEV)
  r.load(ck, load_cfg={"actor": True}, strict=True, map_location=DEV)
  pol = r.get_inference_policy(device=DEV)
  u = env.unwrapped
  env.reset()
  cmd = u.command_manager.get_term("twist")
  rob, ball = u.scene["robot"], u.scene["ball"]
  ids = torch.arange(n, device=DEV)
  origin = u.scene.env_origins[:, :2]
  # Matched perturbations like runswift: yaw 0 / +2 / -2 deg per repeat.
  rep = ids // len(cs)
  case = ids % len(cs)
  yaw0 = torch.tensor([0.0, 2.0, -2.0] * ((reps + 2) // 3), device=DEV)[rep] * math.pi / 180
  bx = torch.tensor([c[1] for c in cs], device=DEV)[case]
  by = torch.tensor([c[2] for c in cs], device=DEV)[case]
  head = torch.tensor([c[3] for c in cs], device=DEV)[case] * math.pi / 180
  rng = torch.tensor([c[4] for c in cs], device=DEV)[case]
  bvx = torch.tensor([c[5] for c in cs], device=DEV)[case]
  # Robot: default standing state, yaw perturbed, at the env origin.
  rs = rob.data.default_root_state.clone()
  rs[:, :2] = origin
  rs[:, 3:7] = torch.stack(
    (torch.cos(yaw0 / 2), torch.zeros_like(yaw0), torch.zeros_like(yaw0), torch.sin(yaw0 / 2)),
    dim=-1,
  )
  rs[:, 7:] = 0.0
  rob.write_root_state_to_sim(rs)
  rob.write_joint_state_to_sim(rob.data.default_joint_pos.clone(), torch.zeros_like(rob.data.default_joint_vel))
  # Ball in the runswift robot frame (x ahead of the robot at yaw 0, as runswift
  # places it in the world while the robot is yawed by the perturbation).
  bs = ball.data.default_root_state.clone()
  bs[:, 0] = origin[:, 0] + bx
  bs[:, 1] = origin[:, 1] + by
  bs[:, 2] = 0.08  # ball radius (the default root height is the unscaled ball's)
  bs[:, 3:7] = torch.tensor([1.0, 0.0, 0.0, 0.0], device=DEV)
  bs[:, 7:] = 0.0
  bs[:, 7] = bvx
  ball.write_root_state_to_sim(bs)
  ball_xy = bs[:, :2]
  cmd.target_w[:] = ball_xy + rng.unsqueeze(-1) * torch.stack((torch.cos(head), torch.sin(head)), -1)
  cmd.last_seen_ball_w[:] = ball_xy
  cmd.time_since_seen[:] = 0.0
  cmd.ball_lost[:] = False
  rel = torch.zeros(n, 3, device=DEV)
  rel[:, :2] = ball_xy - origin
  cmd.last_seen_ball_b[:] = quat_apply_inverse(yaw_quat(rs[:, 3:7]), rel)[:, :2]
  cmd.kicked_since_target[:] = False
  for i, v in enumerate(caps):
    cmd.speed_limit[:, i] = v
  u.sim.forward()
  u.command_manager.compute(dt=0.0)
  obs = env.get_observations()
  if "--debug" in sys.argv:
    o = obs["actor"] if not torch.is_tensor(obs) else obs
    print("DBG obs tail", o[:3, -12:].cpu().numpy().round(2))
    print("DBG root", rob.data.root_link_pos_w[:3].cpu().numpy().round(3), "ball", ball.data.root_link_pos_w[:3].cpu().numpy().round(3))
    print("DBG origin", origin[:3].cpu().numpy())

  dt = u.step_dt
  t = 0.0
  init_v = ball.data.root_link_lin_vel_w[:, :2].clone()
  last_contact = torch.full((n,), -1e9, device=DEV)
  last_foot = torch.full((n,), -1e9, device=DEV)
  launch_t = torch.full((n,), float("nan"), device=DEV)
  peak = torch.zeros(n, device=DEV)
  peak_v = torch.zeros(n, 2, device=DEV)
  foot_launch = torch.zeros(n, dtype=torch.bool, device=DEV)
  fell = torch.zeros(n, dtype=torch.bool, device=DEV)
  with torch.inference_mode():
    for _ in range(int(12.0 / dt)):
      for i, v in enumerate(caps):
        cmd.speed_limit[:, i] = v
      obs, _, dones, _ = env.step(pol(obs))
      t += dt
      fell |= dones.bool()
      if "--debug" in sys.argv and int(t / dt) in (1, 10, 50, 100):
        o = obs["actor"] if not torch.is_tensor(obs) else obs
        print("DBG t", round(t, 2), "root", rob.data.root_link_pos_w[0].cpu().numpy().round(2), "ball", ball.data.root_link_pos_w[0].cpu().numpy().round(2), "target", cmd.target_w[0].cpu().numpy().round(2), "obs", o[0, -11:].cpu().numpy().round(2))
      v = ball.data.root_link_lin_vel_w[:, :2]
      sp = v.norm(dim=-1)
      foot = cmd.prev_touch.clone()
      body = cmd.body_touch.clone()
      last_foot = torch.where(foot, t, last_foot)
      last_contact = torch.where(foot | body, t, last_contact)
      new = (
        launch_t.isnan()
        & ~fell
        & (sp >= 0.5)
        & ((v - init_v).norm(dim=-1) >= 0.3)
        & (t - last_contact <= 0.15)
      )
      launch_t = torch.where(new, t, launch_t)
      foot_launch |= new & (t - last_foot <= 0.15)
      win = ~launch_t.isnan() & (t - launch_t <= 0.2)
      better = win & (sp > peak)
      peak = torch.where(better, sp, peak)
      peak_v = torch.where(better.unsqueeze(-1), v, peak_v)
  err = torch.rad2deg(
    torch.atan2(peak_v[:, 1], peak_v[:, 0]) - head
  )
  err = (err + 180) % 360 - 180
  ok = foot_launch & (err.abs() <= 15) & ~fell
  print(f"RSW caps {caps} trials {n}")
  print(
    f"RSW first strike within 15 deg and upright {int(ok.sum())}/{n} ({100 * ok.float().mean():.1f} %),"
    f" launch speed p50 {peak[foot_launch].median():.2f} m/s, |err| p50 {err[foot_launch].abs().median():.1f} deg,"
    f" time p50 {launch_t[foot_launch].median():.2f} s, falls {int(fell.sum())}"
  )
  for g in ("near-x0.40", "near-x0.75", "near-x1.10", "range", "incoming"):
    m = torch.tensor([cs[int(c)][0].startswith(g) for c in case], device=DEV)
    print(
      f"RSW {g:11s} ok {int((ok & m).sum())}/{int(m.sum())} |err| p50"
      f" {err[m & foot_launch].abs().median():.1f} speed p50 {peak[m & foot_launch].median():.2f}"
    )


if __name__ == "__main__":
  main()

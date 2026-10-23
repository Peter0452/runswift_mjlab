"""Fixed-command evaluation of a dribble checkpoint.

Deterministic policy, speed curriculum off, every moving window (4 s) at one
commanded ball speed. Per speed and per direction bin (command vs robot
heading at window start: fwd < 45°, side 45–135°, back > 135°) it prints one
JSON line: window success (the training criterion: mean ball velocity over the
last 2 s within min(0.25, 0.5 s) m/s of the command, ball within 1 m), mean
ball speed along the command, its vector error, final ball distance and falls.
Only windows that start after the episode's first foot-ball touch count, so
spawn approaches are excluded.

  .venv/bin/python scripts/tools/dribble_eval.py CKPT [--speeds 0.5,1.0,1.5]
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import math
from dataclasses import asdict

import torch

import mjlab.tasks  # noqa: F401
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.tasks.velocity.config.k1_amp import env_cfgs as k1_env_cfgs

TASK = "Mjlab-Velocity-Dribble-Amp-DA-Muon-Booster-K1"
BINS = ("fwd", "side", "back")


def main() -> None:
  ap = argparse.ArgumentParser()
  ap.add_argument("checkpoint")
  ap.add_argument("--num-envs", type=int, default=1024)
  ap.add_argument("--windows", type=int, default=6, help="windows per env per speed")
  ap.add_argument("--speeds", default="0.5,0.8,1.0,1.2,1.5")
  ap.add_argument("--seed", type=int, default=7)
  ap.add_argument("--random-caps", action="store_true", help="keep sampled speed caps")
  ap.add_argument(
    "--cap-vx",
    type=float,
    default=None,
    help="observed forward speed cap (slot 75, m/s); default the trained max 1.2",
  )
  ap.add_argument(
    "--nominal-ball",
    action="store_true",
    help="no ball size / mass / friction / bounce randomization",
  )
  ap.add_argument(
    "--ideal-vision",
    action="store_true",
    help="camera without frame hold, delay, dropout, noise or origin jitter",
  )
  ap.add_argument(
    "--stochastic", action="store_true", help="sample actions (training noise)"
  )
  ap.add_argument(
    "--train-windows",
    action="store_true",
    help="keep the training cfg's fast-command windows (length, turn limit)",
  )
  ap.add_argument(
    "--odom",
    choices=("cfg", "on", "off"),
    default="cfg",
    help="unseen-ball memory with odometry (on) or IMU yaw only (off, the robot)",
  )
  ap.add_argument(
    "--no-joint-clip", action="store_true", help="no runner joint-target clip"
  )
  ap.add_argument(
    "--no-torque-clip",
    action="store_true",
    help="motor-rated leg torques instead of the kick's leg torque clip",
  )
  ap.add_argument("--no-delay", action="store_true", help="no motor command delay")
  args = ap.parse_args()
  dev = "cuda:0" if torch.cuda.is_available() else "cpu"

  ec = load_env_cfg(TASK)
  if args.no_joint_clip:
    ec.actions["joint_pos"].clip = None  # ty: ignore[unresolved-attribute]
  robot = ec.scene.entities["robot"]
  acts = robot.articulation.actuators
  if args.no_torque_clip:
    # The registry cfg is built at import, so restore the motor ratings from a
    # cfg without the leg torque clip.
    rated = {
      a.target_names_expr[0]: a.effort_limit
      for a in k1_env_cfgs.booster_k1_kick_approach_env_cfg(play=True)
      .scene.entities["robot"]
      .articulation.actuators
    }
    acts = tuple(
      dataclasses.replace(a, effort_limit=rated[a.target_names_expr[0]]) for a in acts
    )
  if args.no_delay:
    acts = tuple(dataclasses.replace(a, delay_min_lag=0, delay_max_lag=0) for a in acts)
  robot.articulation = dataclasses.replace(robot.articulation, actuators=acts)
  ec.scene.num_envs = args.num_envs
  ec.seed = args.seed
  tw = ec.commands["twist"]
  tw.speed_curriculum = False
  tw.stop_prob = 0.0
  tw.top_band_prob = 0.0
  tw.spawn_any_prob = 0.0
  tw.unknown_start_prob = 0.0
  # v22 scenarios (kick windows, vanishing ball, far spawns) are judged by
  # dribble_skill_eval.py; this eval stays the dribble bench.
  tw.kick_prob = 0.0
  tw.vanish_prob = 0.0
  tw.far_spawn_prob = 0.0
  if args.nominal_ball:
    for name in ("ball_mass", "ball_friction", "ball_bounce"):
      ec.events.pop(name, None)
  if args.ideal_vision:
    tw.vision_hold_steps = (1, 1)
    tw.vision_delay_steps = (0, 0)
    tw.vision_dropout = 0.0
    tw.ball_obs_noise = (0.0, 0.0)
    tw.ball_origin_jitter = 0.0
  if args.odom != "cfg":
    tw.memory_odometry = args.odom == "on"
  if not args.train_windows:
    # Every direction and the standard 4 s window, comparable across runs.
    tw.fast_window_s = None
    tw.fast_turn_half_angle = math.pi
  if not args.random_caps:
    vx = args.cap_vx if args.cap_vx is not None else tw.speed_limit_vx[1]
    tw.speed_limit_vx = (vx, vx)
    tw.speed_limit_vy = (tw.speed_limit_vy[1],) * 2
    tw.speed_limit_wz = (tw.speed_limit_wz[1],) * 2
  ac = load_rl_cfg(TASK)
  rc = load_runner_cls(TASK)
  base = ManagerBasedRlEnv(cfg=ec, device=dev)
  env = RslRlVecEnvWrapper(base, clip_actions=ac.clip_actions)
  runner = rc(env, asdict(ac), device=dev)
  runner.load(args.checkpoint, load_cfg={"actor": True}, strict=True, map_location=dev)
  policy = runner.get_inference_policy(device=dev)
  if args.stochastic:
    actor = runner.alg.actor

    def policy(obs):
      return actor(obs, stochastic_output=True)

  cmd = base.command_manager.get_term("twist")
  robot, ball = base.scene["robot"], base.scene["ball"]
  n, dt = args.num_envs, base.step_dt
  win_s = cmd.cfg.resampling_time_range[0]
  steps = int(round(args.windows * win_s / dt))

  def yaw() -> torch.Tensor:
    q = robot.data.root_link_quat_w
    return torch.atan2(
      2 * (q[:, 0] * q[:, 3] + q[:, 1] * q[:, 2]), 1 - 2 * (q[:, 2] ** 2 + q[:, 3] ** 2)
    )

  tag = "/".join(args.checkpoint.split("/")[-2:])
  start_bin = torch.zeros(n, dtype=torch.long, device=dev)
  valid = torch.zeros(n, dtype=torch.bool, device=dev)
  along_sum = torch.zeros(n, device=dev)
  robot_along = torch.zeros(n, device=dev)
  k_steps = torch.zeros(n, device=dev)

  def start(mask: torch.Tensor) -> None:
    c = cmd.ball_cmd_dir_w
    rel = torch.atan2(c[:, 1], c[:, 0]) - yaw()
    ang = torch.atan2(torch.sin(rel), torch.cos(rel)).abs()
    b = (ang > math.pi / 4).long() + (ang > 3 * math.pi / 4).long()
    start_bin[mask] = b[mask]
    valid[mask] = cmd.has_touched[mask] & (cmd.ball_cmd_speed[mask] > 0)
    along_sum[mask] = 0.0
    robot_along[mask] = 0.0
    k_steps[mask] = 0.0

  for s in [float(x) for x in args.speeds.split(",")]:
    tw.ball_speed_range = (s, s)
    cmd.speed_hi = s
    torch.manual_seed(args.seed)
    st = {
      b: dict(w=0, ok=0, along=0.0, err=0.0, dist=0.0, rv=0.0, fell=0) for b in BINS
    }
    with torch.inference_mode():
      obs, _ = env.reset()
      start(torch.ones(n, dtype=torch.bool, device=dev))
      for _ in range(steps):
        ending = cmd.time_left - dt <= 0.0
        in_tail = cmd.time_left <= cmd.cfg.success_tail_s
        c = cmd.ball_cmd_dir_w.clone()
        bv = ball.data.root_link_lin_vel_w[:, :2]
        rv = robot.data.root_link_lin_vel_w[:, :2]
        along_sum += torch.sum(bv * c, -1) * in_tail
        robot_along += torch.sum(rv * c, -1) * in_tail
        k_steps += in_tail.float()
        tail_v = cmd._tail_vel_sum / cmd._tail_steps.clamp(min=1).unsqueeze(-1)
        err = torch.linalg.norm(tail_v - c * cmd.ball_cmd_speed.unsqueeze(-1), dim=-1)
        dist = cmd.ball_trunk_dist.clone()
        obs, _, dones, extras = env.step(policy(obs))
        done = dones.bool()
        fell = done & ~extras.get("time_outs", torch.zeros_like(done)).bool()
        fin = (ending | fell) & valid
        for i, b in enumerate(BINS):
          m = fin & (start_bin == i)
          if not m.any():
            continue
          d = st[b]
          d["w"] += int(m.sum())
          d["ok"] += int((m & ending & cmd.window_success).sum())
          kk = k_steps[m].clamp(min=1)
          d["along"] += float((along_sum[m] / kk).sum())
          d["rv"] += float((robot_along[m] / kk).sum())
          d["err"] += float(err[m].sum())
          d["dist"] += float(dist[m].sum())
          d["fell"] += int((m & fell).sum())
        start(ending | done)
    for b in BINS:
      d = st[b]
      w = max(d["w"], 1)
      print(
        json.dumps(
          {
            "ckpt": tag,
            "speed": s,
            "dir": b,
            "windows": d["w"],
            "success": round(d["ok"] / w, 3),
            "ball_along": round(d["along"] / w, 3),
            "robot_along": round(d["rv"] / w, 3),
            "vel_err": round(d["err"] / w, 3),
            "ball_dist": round(d["dist"] / w, 3),
            "fall": round(d["fell"] / w, 3),
          }
        ),
        flush=True,
      )


if __name__ == "__main__":
  main()

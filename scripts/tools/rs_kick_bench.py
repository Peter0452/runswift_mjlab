"""Kick benchmark (runswift spec v2) for our kick loop on the stage-3 env.

The trials, kick rule, metrics and score are k1.eval.rs_kick's, shared with
bench_bhuman_kick_v2.py (B-Human's kick on its port), so the results compare.
The kick loop runs as on the robot: runner joint-target clip, B-Human torque
clip, scripted head tracker, camera ball model and 10-40 ms motor delay
(``--perception perfect`` and ``--delay zero`` for diagnostics), nominal robot
(no randomisation), flat ground. A trial's commanded direction and range become
the kick-loop target: ball + range * (cos, sin)(direction).

usage:
  .venv/bin/python scripts/tools/rs_kick_bench.py --name seed0 \
    --policy h022=logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt
Results: docs/benchmarks_rs_kick/NAME/{report.md, results.json, trials_POLICY.csv}
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import math
import os
import time
from dataclasses import asdict
from pathlib import Path

os.environ["KICK_EVAL"] = "1"  # no mid-kick starts in evaluation

import torch  # noqa: E402

import mjlab.tasks  # noqa: E402, F401
from k1.eval import rs_kick  # noqa: E402
from k1.tasks.bhuman.mdp import set_ball_size_mass  # noqa: E402
from k1.tasks.bhuman.robot import get_bhuman_ball_cfg  # noqa: E402
from k1.tasks.kick.mdp.kick_loop import KickLoopCommandCfg  # noqa: E402
from mjlab.envs import ManagerBasedRlEnv  # noqa: E402
from mjlab.managers.event_manager import RecomputeLevel  # noqa: E402
from mjlab.rl import RslRlVecEnvWrapper  # noqa: E402
from mjlab.tasks.registry import (  # noqa: E402
  load_env_cfg,
  load_rl_cfg,
  load_runner_cls,
)
from mjlab.utils.lab_api.math import quat_apply_inverse, yaw_quat  # noqa: E402

TASK = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"
DEV = "cuda:0"
ROOT = Path(__file__).resolve().parents[2]
DELAYS = {"zero": (0, 0), "typical": (2, 8)}  # physics steps (5 ms)
# Training events that move the robot or the ball, or randomise the robot.
DROP_EVENTS = (
  "push_near_ball", "ball_relocate_unseen", "ball_mass", "ball_friction", "ball_bounce",
  "stand_start", "push_robot", "ball_nudge", "reset_robot_from_motion", "pd_gains",
  "encoder_bias", "trunk_inertia", "limb_inertia", "foot_friction", "terrain_contact",
)  # fmt: skip


def build(n: int, perception: str, delay: str, seed: int, ball: str):
  cfg = load_env_cfg(TASK)
  cfg.scene.num_envs = n
  cfg.seed = seed
  cfg.episode_length_s = rs_kick.TRIAL_S + rs_kick.TRACK_S + 5.0
  for k in DROP_EVENTS:
    cfg.events.pop(k, None)
  cfg.actions["joint_pos"].scan_share = 0.0  # ty: ignore[unresolved-attribute]
  assert cfg.scene.terrain is not None
  cfg.scene.terrain.terrain_type = "plane"
  cfg.scene.terrain.terrain_generator = None
  if ball == "bhuman":
    cfg.scene.entities["ball"] = get_bhuman_ball_cfg(
      friction=rs_kick.BALL_FRICTION, condim=6, solref=rs_kick.BALL_SOLREF
    )
  robot = cfg.scene.entities["robot"]
  assert robot.articulation is not None
  lo, hi = DELAYS[delay]
  robot.articulation = dataclasses.replace(
    robot.articulation,
    actuators=tuple(
      dataclasses.replace(a, delay_min_lag=lo, delay_max_lag=hi)
      for a in robot.articulation.actuators
    ),
  )
  tw = cfg.commands["twist"]
  assert isinstance(tw, KickLoopCommandCfg)
  tw.resampling_time_range = (1.0e6, 1.0e6)
  tw.side_drill_prob = 0.0
  tw.unknown_start_prob = 0.0
  if perception == "perfect":
    tw.fov_half_angle = math.pi
    tw.fov_vertical_half_angle = None
    tw.ball_obs_noise = (0.0, 0.0)
    tw.vision_dropout = 0.0
    tw.vision_delay_steps = (0, 0)
    tw.ball_origin_jitter = 0.0
  return ManagerBasedRlEnv(cfg=cfg, device=DEV)


def place(u, trials: list[dict], radius: torch.Tensor) -> torch.Tensor:
  """Robot standing at the origin facing +x; ball and kick target per trial.
  Returns the commanded direction (world, rad)."""
  rob, ball = u.scene["robot"], u.scene["ball"]
  cmd = u.command_manager.get_term("twist")
  n = u.num_envs
  t = {k: torch.tensor([tr[k] for tr in trials], device=DEV, dtype=torch.float)
       for k in ("dist", "bearing_deg", "direction_deg", "range")}  # fmt: skip
  origin = u.scene.env_origins[:, :2]
  rs = rob.data.default_root_state.clone()
  rs[:, :2] = origin
  rs[:, 3:7] = torch.tensor([1.0, 0.0, 0.0, 0.0], device=DEV)
  rs[:, 7:] = 0.0
  rob.write_root_state_to_sim(rs)
  rob.write_joint_state_to_sim(
    rob.data.default_joint_pos.clone(), torch.zeros_like(rob.data.default_joint_vel)
  )
  b = torch.deg2rad(t["bearing_deg"])
  ball_xy = origin + t["dist"][:, None] * torch.stack((b.cos(), b.sin()), -1)
  bs = ball.data.default_root_state.clone()
  bs[:, :2] = ball_xy
  bs[:, 2] = radius
  bs[:, 3:7] = torch.tensor([1.0, 0.0, 0.0, 0.0], device=DEV)
  bs[:, 7:] = 0.0
  ball.write_root_state_to_sim(bs)
  d = torch.deg2rad(t["direction_deg"])
  cmd.target_w[:] = ball_xy + t["range"][:, None] * torch.stack((d.cos(), d.sin()), -1)
  cmd.last_seen_ball_w[:] = ball_xy
  cmd.time_since_seen[:] = 0.0
  cmd.ball_lost[:] = False
  rel = torch.zeros(n, 3, device=DEV)
  rel[:, :2] = ball_xy - rs[:, :2]
  cmd.last_seen_ball_b[:] = quat_apply_inverse(yaw_quat(rs[:, 3:7]), rel)[:, :2]
  cmd.last_seen_yaw[:] = 0.0
  cmd.kicked_since_target[:] = False
  cmd.never_seen[:] = False
  # 2026-10-28: clear the actor's detection-delay history (and camera hold).
  # env.reset() already pushed a detection of the pre-placement ball into it, so
  # with a detection lag >= 1 the policy's first sightings were of a ball metres
  # away: memory jumped there, the head tracker followed, the real ball was
  # never seen, the lost rule fired (S8 deployed s0: 22 / 62 close-ball "kicks"
  # were bumps at 3.2 m perceived error; score 0.793 -> 0.849 with this fix).
  cmd._det_hist_vis[:] = False
  cmd._det_hist_b[:] = 0.0
  if hasattr(cmd, "_held_vis"):
    cmd._held_vis[:] = False
  return d


def run_policy(ckpt: str, trials: list[dict], args) -> list[dict]:
  u = build(len(trials), args.perception, args.delay, args.seed, args.ball)
  agent = load_rl_cfg(TASK)
  env = RslRlVecEnvWrapper(u, clip_actions=agent.clip_actions)
  runner_cls = load_runner_cls(TASK)
  assert runner_cls is not None
  runner = runner_cls(env, asdict(agent), device=DEV)
  runner.load(ckpt, load_cfg={"actor": True}, strict=True, map_location=DEV)
  policy = runner.get_inference_policy(device=DEV)
  torch.manual_seed(args.seed)
  env.reset()
  n = len(trials)
  ids = torch.arange(n, device=DEV)
  radius = torch.tensor([tr["radius"] for tr in trials], device=DEV, dtype=torch.float)
  mass = torch.tensor([tr["mass"] for tr in trials], device=DEV, dtype=torch.float)
  set_ball_size_mass(u, ids, radius, mass)
  u.sim.recompute_constants(RecomputeLevel.set_const)
  cmd_dir = place(u, trials, radius)
  u.sim.forward()
  u.command_manager.compute(dt=0.0)
  obs = env.get_observations()

  rob, ball = u.scene["robot"], u.scene["ball"]
  cmd = u.command_manager.get_term("twist")
  feet = [rob.body_names.index(f) for f in rs_kick.FEET]
  caps = torch.tensor(args.caps, device=DEV).expand(n, 3).clone()
  dt = u.step_dt
  trial_steps = int(rs_kick.TRIAL_S / dt)
  total = trial_steps + int(rs_kick.TRACK_S / dt)
  rule = rs_kick.KickRule(n, DEV)
  kick_step = torch.full((n,), -1, dtype=torch.long, device=DEV)
  fell = torch.zeros(n, dtype=torch.bool, device=DEV)
  broken = torch.full((n,), total, dtype=torch.long, device=DEV)
  pos = torch.zeros(total, n, 2, device=DEV)
  speed = torch.zeros(total, n, device=DEV)
  p_kick = torch.zeros(n, 2, device=DEV)
  origin = u.scene.env_origins[:, :2]
  with torch.inference_mode():
    for s in range(total):
      cmd.speed_limit[:] = caps
      obs, _, dones, extras = env.step(policy(obs))
      bp = ball.data.root_link_pos_w
      lin, ang = ball.data.root_link_lin_vel_w, ball.data.root_link_ang_vel_w
      kicked = rule.update(
        rob.data.body_link_pos_w[:, feet], rob.data.body_link_quat_w[:, feet],
        bp, lin, radius, dt,
      )  # fmt: skip
      pos[s] = bp[:, :2] - origin
      speed[s] = lin.norm(dim=-1)
      # runswift's fall test (tilt > 60 deg or root below 0.25 m) and any
      # termination that is not a time-out.
      to = extras.get("time_outs")
      done = dones.bool()
      fall = done & ~(to.bool() if to is not None else torch.zeros_like(done))
      fall |= -rob.data.projected_gravity_b[:, 2] < 0.5
      fall |= rob.data.root_link_pos_w[:, 2] < 0.25
      fell |= fall & (s < trial_steps)
      if args.kick_rule == "ours":
        kicked = cmd.kick_event.clone()
      new = (kick_step < 0) & kicked & ~fell & (s < trial_steps)
      p_kick[new] = bp[new, :2] - origin[new]
      kick_step[new] = s
      broken = torch.where(done & (broken == total), s, broken)
      if args.damping:
        lin, ang = rs_kick.damp_ball(lin, ang, u.physics_dt, u.cfg.decimation)
        ball.write_root_link_velocity_to_sim(torch.cat((lin, ang), -1))
      rule.remember_ball_velocity(lin)
      if s >= trial_steps and bool(((kick_step < 0) | fell | (broken < total)).all()):
        break
  ks, br, fl = kick_step.cpu().numpy(), broken.cpu().numpy(), fell.cpu().numpy()
  pc, sc, pk = pos.cpu().numpy(), speed.cpu().numpy(), p_kick.cpu().numpy()
  cd = cmd_dir.cpu().numpy()
  rows = [
    rs_kick.trial_row(
      tr,
      int(ks[i]),
      bool(fl[i]),
      int(br[i]),
      pc[:, i],
      sc[:, i],
      pk[i],
      float(cd[i]),
      dt,
    )  # fmt: skip
    for i, tr in enumerate(trials)
  ]
  env.close()
  return rows


def main() -> None:
  p = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
  )
  p.add_argument("--policy", action="append", required=True, help="NAME=CHECKPOINT")
  p.add_argument("--name", default="seed0")
  p.add_argument("--seed", type=int, default=0)
  p.add_argument("--trials-per-cell", type=int, default=25)
  p.add_argument("--perception", choices=("camera", "perfect"), default="camera")
  p.add_argument("--delay", choices=tuple(DELAYS), default="typical")
  p.add_argument(
    "--caps", type=float, nargs=3, default=(2.0, 1.5, 1.5),
    help="speed caps |vx| |vy| |wz| (default: the caps the champion trained with)",
  )  # fmt: skip
  p.add_argument(
    "--ball", choices=("bhuman", "ours"), default="bhuman",
    help="bhuman: B-Human's ball contact (friction 1.0 / 0.1 / 0.1, solref 0.02, 1.0); "
    "ours: the training ball's contact. Size and mass are the trial's either way.",
  )  # fmt: skip
  p.add_argument(
    "--kick-rule", choices=("booster", "ours"), default="booster",
    help="booster: Booster Gym's touch rule (same as the B-Human benchmark); "
    "ours: the kick loop's kick event (ball leaves at >= 1 m/s after a jump)",
  )  # fmt: skip
  p.add_argument(
    "--no-damping",
    dest="damping",
    action="store_false",
    help="skip Isaac Gym's ball damping (0.75 / 0.5)",
  )
  p.add_argument("--out", default="docs/benchmarks_rs_kick")
  args = p.parse_args()

  trials = rs_kick.make_trials(args.trials_per_cell, args.seed)
  out = ROOT / args.out / args.name
  out.mkdir(parents=True, exist_ok=True)
  results, meta = {}, {}
  for spec in args.policy:
    name, ckpt = spec.split("=", 1)
    t0 = time.time()
    rows = run_policy(ckpt, trials, args)
    with open(out / f"trials_{name}.csv", "w", newline="") as f:
      w = csv.DictWriter(f, fieldnames=list(rows[0]))
      w.writeheader()
      w.writerows(rows)
    results[name] = rs_kick.group(rows)
    meta[name] = {"checkpoint": ckpt, "seconds": round(time.time() - t0, 1)}
    print(f"{name}: score {results[name]['overall']['score']:.3f}", flush=True)
  header = (
    "# Kick benchmark (runswift spec v2): results\n\n"
    f"Our kick loop on `{TASK}`: {len(trials)} trials, seed {args.seed} (4 kick-direction "
    f"sectors x 2 ball sides x {args.trials_per_cell}), ball in front (+-30°, 0.35-1.0 m), "
    "standing start, benchmark ball, flat ground, nominal robot. Deployed action path "
    f"(joint-target and torque clip, scripted head), perception {args.perception}, delay "
    f"{args.delay}, caps {tuple(args.caps)}, ball {args.ball}, kick rule {args.kick_rule}, "
    f"ball damping {'on' if args.damping else 'off'}. Trials and score as "
    "`bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).\n\n"
    "Policies: "
    + "; ".join(f"**{n}** = `{m['checkpoint']}`" for n, m in meta.items())
    + ".\n"
  )
  (out / "report.md").write_text(rs_kick.report(results, header))
  (out / "results.json").write_text(
    json.dumps(
      {"meta": meta, "args": vars(args), "results": results}, indent=1, default=str
    )
  )
  print(f"report: {out / 'report.md'}")


if __name__ == "__main__":
  main()

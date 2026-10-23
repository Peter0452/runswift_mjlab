"""Evaluate a policy in the ported B-Human kick env (Mjlab-BHuman-Kick-*).

Kicks are scored like Booster Gym's ``_add_kick_info``: when a kick's frame
counter reaches 3, record the peak 3D ball speed since contact and the angle
between the ball's direction and the commanded kick direction. Strong kicks
(range 20 m) and range-scaled kicks are reported separately; scaled kicks
also report the speed error against B-Human's expected launch speed
sqrt(2 * 0.3 * range).

Example:
  uv run python scripts/tools/eval_bhuman_kick.py \
    --checkpoint ../MachineLearning/IsaacGymRL/pre-trained/WalkAndKick/K1_kick_inner.pth
"""

from __future__ import annotations

import argparse
import math
from dataclasses import asdict

import torch

import mjlab.tasks  # noqa: F401
from mjlab.envs import ManagerBasedRlEnv
from mjlab.tasks.bhuman_kick.kick_command import BHumanKickCommand
from mjlab.tasks.bhuman_kick.runner import BHumanPpoRunner, BHumanPpoRunnerCfg
from mjlab.tasks.registry import load_env_cfg


def main() -> None:
  p = argparse.ArgumentParser()
  p.add_argument("--checkpoint", required=True)
  p.add_argument("--task", default="Mjlab-BHuman-Kick-Stage6-Booster-K1")
  p.add_argument("--num-envs", type=int, default=1024)
  p.add_argument("--seconds", type=float, default=60.0)
  p.add_argument("--flat", action="store_true", help="Plane instead of the field.")
  p.add_argument("--no-noise", action="store_true")
  p.add_argument("--seed", type=int, default=0)
  args = p.parse_args()

  torch.manual_seed(args.seed)
  cfg = load_env_cfg(args.task)
  cfg.scene.num_envs = args.num_envs
  if args.flat:
    assert cfg.scene.terrain is not None
    cfg.scene.terrain.terrain_type = "plane"
    cfg.scene.terrain.terrain_generator = None
  kick = cfg.commands["kick"]
  if args.no_noise:
    kick.observation_noise = False  # type: ignore[attr-defined]
  env = ManagerBasedRlEnv(cfg=cfg, device="cuda:0")
  vec = BHumanPpoRunner.make_vecenv(env, None)
  runner = BHumanPpoRunner(vec, asdict(BHumanPpoRunnerCfg()), None, "cuda:0")
  runner.load(args.checkpoint)
  actor = runner.model.actor.eval()
  cmd = env.command_manager.get_term("kick")
  assert isinstance(cmd, BHumanKickCommand)

  obs, _ = vec.reset()
  steps = int(args.seconds / env.step_dt)
  strong_v, strong_a, norm_v, norm_a, norm_err = [], [], [], [], []
  falls = 0
  episodes = 0
  approach_steps: list[float] = []
  since_reset = torch.zeros(args.num_envs, device="cuda:0")
  for _ in range(steps):
    with torch.no_grad():
      act = actor(obs)
    obs, _, _, done, _, _ = vec.step(act)
    since_reset += 1
    k3 = cmd.ball_kicked_counter == 3
    if bool(k3.any()):
      ang = torch.atan2(cmd.ball_vel[:, 1], cmd.ball_vel[:, 0])
      err = (ang - cmd.direction_angle_current + math.pi) % (2 * math.pi) - math.pi
      v = cmd.ball_velocity_norm_at_kick
      s = k3 & cmd.flag_is_strong_kick
      nm = k3 & ~cmd.flag_is_strong_kick
      strong_v += v[s].tolist()
      strong_a += err[s].abs().rad2deg().tolist()
      norm_v += v[nm].tolist()
      norm_a += err[nm].abs().rad2deg().tolist()
      expected = torch.sqrt(2 * cmd.cfg.ball_friction * cmd.range)
      norm_err += (v - expected)[nm].tolist()
      approach_steps += (cmd.episode_length_buf[k3].float() * env.step_dt).tolist()
    falls += int(cmd.terminated.sum())
    episodes += int(done.sum())

  def stat(x: list[float]) -> str:
    if not x:
      return "n=0"
    t = torch.tensor(x)
    return (
      f"n={len(x)} mean={t.mean():.2f} p50={t.median():.2f} p90={t.quantile(0.9):.2f}"
    )

  def within(x: list[float], deg: float) -> str:
    if not x:
      return "-"
    return f"{100 * sum(a <= deg for a in x) / len(x):.0f}%"

  sim_s = args.num_envs * args.seconds
  print(f"task {args.task}  envs {args.num_envs} x {args.seconds:.0f} s")
  print(f"falls {falls} ({falls / sim_s * 60:.2f} / robot-min), episodes {episodes}")
  print(f"kicks {(len(strong_v) + len(norm_v)) / sim_s * 60:.2f} / robot-min")
  print(f"time to kick (s since ball placed): {stat(approach_steps)}")
  print(f"strong speed (m/s): {stat(strong_v)}")
  print(
    f"strong aim error (deg): {stat(strong_a)}  "
    f"<=10: {within(strong_a, 10)} <=20: {within(strong_a, 20)}"
  )
  print(f"scaled speed (m/s): {stat(norm_v)}")
  print(f"scaled speed - expected (m/s): {stat(norm_err)}")
  print(
    f"scaled aim error (deg): {stat(norm_a)}  "
    f"<=10: {within(norm_a, 10)} <=20: {within(norm_a, 20)}"
  )
  env.close()


if __name__ == "__main__":
  main()

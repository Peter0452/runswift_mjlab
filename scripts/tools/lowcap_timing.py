"""Where does the time to the first kick go at low caps (0.5 / 0.3 / 0.6)?

Per robot until its first kick: time to come within 1.0 m of the ball, time
from there to the kick, mean |yaw error to the kick line|, |wz| and vx while
within 1 m, touches before the kick, aim at the kick.

usage: python scripts/tools/lowcap_timing.py CK [CK ...]
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

TASK = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"
DEV = "cuda:0"


def run(ck: str, n: int = 512) -> None:
  cfg = load_env_cfg(TASK, play=False)
  cfg.scene.num_envs = n
  for k in ("push_robot", "push_near_ball", "ball_relocate_unseen", "ball_mass", "ball_friction",
            "ball_bounce", "pd_gains", "encoder_bias", "trunk_inertia", "limb_inertia",
            "foot_friction", "terrain_contact"):  # fmt: skip
    cfg.events.pop(k, None)
  cfg.scene.terrain.terrain_type = "plane"
  cfg.scene.terrain.terrain_generator = None
  cfg.actions["joint_pos"].scan_share = 0.0
  tw = cfg.commands["twist"]
  tw.resampling_time_range = (1.0e6, 1.0e6)
  cfg.episode_length_s = 40.0
  agent = load_rl_cfg(TASK)
  env = RslRlVecEnvWrapper(ManagerBasedRlEnv(cfg=cfg, device=DEV), clip_actions=agent.clip_actions)
  r = load_runner_cls(TASK)(env, asdict(agent), device=DEV)
  r.load(ck, load_cfg={"actor": True}, strict=True, map_location=DEV)
  pol = r.get_inference_policy(device=DEV)
  obs, _ = env.reset()
  u = env.unwrapped
  cmd = u.command_manager.get_term("twist")
  rob = u.scene["robot"]
  caps = torch.tensor([0.5, 0.3, 0.6], device=DEV)
  dt = u.step_dt
  t = 0.0
  nan = lambda: torch.full((n,), float("nan"), device=DEV)  # noqa: E731
  t_near, t_kick = nan(), nan()
  yaw_s, wz_s, vx_s, near_n, touches = (torch.zeros(n, device=DEV) for _ in range(5))
  aim = nan()
  done = torch.zeros(n, dtype=torch.bool, device=DEV)
  with torch.inference_mode():
    for _ in range(int(30.0 / dt)):
      cmd.speed_limit[:] = caps
      obs, _, d, _ = env.step(pol(obs))
      t += dt
      done |= d.bool()
      pending = t_kick.isnan() & ~done
      near = pending & (cmd.dist < 1.0)
      t_near = torch.where(near & t_near.isnan(), t, t_near)
      yaw_s += torch.where(near, cmd.yaw_error.abs(), 0.0)
      wz_s += torch.where(near, rob.data.root_link_ang_vel_b[:, 2].abs(), 0.0)
      vx_s += torch.where(near, rob.data.root_link_lin_vel_b[:, 0], 0.0)
      near_n += near.float()
      touches += (pending & cmd.push).float()
      k = pending & cmd.kick_event
      t_kick = torch.where(k, t, t_kick)
      aim = torch.where(k, torch.rad2deg(torch.acos(cmd.kick_cos.clamp(-1, 1))), aim)
  ok = ~t_kick.isnan()
  nn = near_n.clamp(min=1)

  def q(x):
    x = x[ok & ~x.isnan()]
    return f"{float(x.median()):.2f}" if len(x) else "nan"

  print(
    f"LOWCAP {os.path.basename(os.path.dirname(ck))}/{os.path.basename(ck)}: kicked {100 * ok.float().mean():.0f} %,"
    f" first kick p50 {q(t_kick)} s = to 1 m {q(t_near)} s + near {q(t_kick - t_near)} s;"
    f" near the ball: |yaw err| {math.degrees(float((yaw_s / nn)[ok].median())):.0f} deg,"
    f" |wz| {float((wz_s / nn)[ok].median()):.2f} rad/s, vx {float((vx_s / nn)[ok].median()):.2f} m/s,"
    f" pushes {float(touches[ok].mean()) * dt:.2f} s; aim at kick p50 {q(aim)} deg",
    flush=True,
  )
  env.close()


if __name__ == "__main__":
  for ck in sys.argv[1:]:
    run(ck)

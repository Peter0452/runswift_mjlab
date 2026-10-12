"""Whole-body anatomy of each kick: which leg, support-foot placement, steps into
the kick, swing time, flight, trunk motion. Same setup as kick_style_compare.py.

usage: python scripts/tools/kick_anatomy.py {ours CK | bhuman}
"""

import math
import sys
from dataclasses import asdict

import torch

import os

os.environ["KICK_EVAL"] = "1"  # no mid-kick starts in evaluation

import mjlab.tasks  # noqa: F401  # isort: skip
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.utils.lab_api.math import quat_apply_inverse, yaw_quat

TASK = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"
DEV = "cuda:0"
H = 50  # history frames (1 s)


def main() -> None:
  who = sys.argv[1]
  cfg = load_env_cfg(TASK, play=True)
  cfg.scene.num_envs = 512
  for k in (
    "push_robot",
    "push_near_ball",
    "ball_mass",
    "ball_friction",
    "ball_bounce",
  ):
    cfg.events.pop(k, None)
  t = cfg.commands["twist"]
  t.ball_distance_range = (0.4, 1.5)
  t.spawn_view_half_angle = math.pi
  t.vision_dropout = 0.0
  t.vision_delay_steps = (0, 0)
  if who == "ours":
    agent = load_rl_cfg(TASK)
    env = RslRlVecEnvWrapper(
      ManagerBasedRlEnv(cfg=cfg, device=DEV), clip_actions=agent.clip_actions
    )
    r = load_runner_cls(TASK)(env, asdict(agent), device=DEV)
    r.load(sys.argv[2], load_cfg={"actor": True}, strict=True, map_location=DEV)
    pol = r.get_inference_policy(device=DEV)
    u = env.unwrapped

    def act(o):
      return pol(o)
  else:
    from mjlab.scripts.play_bhuman_kick import BHumanKickPlayConfig, BHumanKickPolicy

    u = ManagerBasedRlEnv(cfg=cfg, device=DEV)
    env = RslRlVecEnvWrapper(u)
    bh = BHumanKickPolicy(u, BHumanKickPlayConfig(num_envs=512, print_kicks=False))

    def act(o):
      return bh(o)

  obs, _ = env.reset()
  cmd = u.command_manager.get_term("twist")
  rob, ball = u.scene["robot"], u.scene["ball"]
  feet, _ = rob.find_bodies(("left_foot_link", "right_foot_link"), preserve_order=True)
  feet_t = torch.tensor(feet, device=DEV)
  n = u.num_envs
  rows = torch.arange(n, device=DEV)
  con_hist = torch.zeros(H, n, 2, dtype=torch.bool, device=DEV)
  pitch_hist = torch.zeros(H, n, device=DEV)
  R = {k: [] for k in (
    "left", "same_side", "sup_behind", "sup_lat", "steps", "swing_t", "flight",
    "sup_contact", "pitch_range", "kick_lat", "long", "speed", "aim", "foot_yaw",
  )}  # fmt: skip
  # Falls within 2 s of a kick, by technique (hop / planted).
  since = torch.full((n,), 10_000, device=DEV)
  was_hop = torch.zeros(n, dtype=torch.bool, device=DEV)
  falls = {"hop": 0, "planted": 0}
  with torch.inference_mode():
    for _ in range(1500):
      obs, _, dones, extras = env.step(act(obs))
      tout = extras.get("time_outs")
      fell = dones.bool() & (~tout.bool() if tout is not None else True)
      recent = fell & (since * u.step_dt < 2.0)
      falls["hop"] += int((recent & was_hop).sum())
      falls["planted"] += int((recent & ~was_hop).sum())
      since += 1
      since[dones.bool()] = 10_000
      con = u.scene["feet_ground_contact"].data.found.reshape(n, -1)[:, :2] > 0
      g = rob.data.projected_gravity_b
      con_hist = torch.roll(con_hist, -1, 0)
      pitch_hist = torch.roll(pitch_hist, -1, 0)
      con_hist[-1] = con
      pitch_hist[-1] = torch.rad2deg(torch.atan2(g[:, 0], -g[:, 2]))
      k = cmd.kick_event & (u.episode_length_buf > H)
      if not k.any():
        continue
      ids = k.nonzero(as_tuple=False).flatten()
      bp = ball.data.root_link_pos_w[ids]
      fp = rob.data.body_link_pos_w[ids][:, feet_t]
      which = (fp[:, :, :2] - bp[:, None, :2]).norm(dim=-1).argmin(-1)
      other = 1 - which
      r_ = torch.arange(len(ids), device=DEV)
      # Kick-direction frame at the ball: x toward target, y left.
      to = cmd.target_w[ids] - bp[:, :2]
      ang = torch.atan2(to[:, 1], to[:, 0])
      c, s = ang.cos(), ang.sin()
      sup = fp[r_, other, :2] - bp[:, :2]
      kf = fp[r_, which, :2] - bp[:, :2]
      sup_x = c * sup[:, 0] + s * sup[:, 1]
      sup_y = -s * sup[:, 0] + c * sup[:, 1]
      kick_y = -s * kf[:, 0] + c * kf[:, 1]
      # Ball side relative to the robot heading.
      yq = yaw_quat(rob.data.root_link_quat_w[ids])
      rel = torch.zeros(len(ids), 3, device=DEV)
      rel[:, :2] = bp[:, :2] - rob.data.root_link_pos_w[ids, :2]
      ball_y = quat_apply_inverse(yq, rel)[:, 1]
      ch = con_hist[:, ids]  # H, m, 2
      touchdowns = (ch[1:] & ~ch[:-1]).sum(dim=(0, 2))
      kc = ch[:, r_, which]  # H, m
      off = (~kc).flip(0).cumprod(0).sum(0)  # frames the kick foot has been airborne
      R["left"].append((which == 0).float())
      R["same_side"].append(((which == 0) == (ball_y > 0)).float())
      R["sup_behind"].append(sup_x)
      R["sup_lat"].append(sup_y.abs())
      R["kick_lat"].append(kick_y.abs())
      R["steps"].append(touchdowns.float())
      R["swing_t"].append(off.float() * u.step_dt)
      R["flight"].append((~ch[-1].any(-1)).float())
      R["sup_contact"].append(ch[-1, r_, other].float())
      R["pitch_range"].append(
        pitch_hist[-15:, ids].amax(0) - pitch_hist[-15:, ids].amin(0)
      )
      R["long"].append(cmd.kick_long[ids].float())
      R["speed"].append(cmd.kick_speed[ids])
      R["aim"].append(torch.rad2deg(torch.acos(cmd.kick_cos[ids].clamp(-1.0, 1.0))))
      R["foot_yaw"].append(torch.rad2deg(cmd.kick_foot_yaw[ids]))
      since[ids] = 0
      was_hop[ids] = ~ch[-1].any(-1)
  X = {k: torch.cat(v) for k, v in R.items()}

  def q(x, p):
    return float(x.quantile(p)) if len(x) else float("nan")

  print(f"ANAT {who} kicks {len(X['left'])}")
  print(
    f"ANAT kicking leg: left {100 * X['left'].mean():.0f} %, right"
    f" {100 * (1 - X['left'].mean()):.0f} % | leg on the ball's side"
    f" {100 * X['same_side'].mean():.0f} %"
  )
  print(
    f"ANAT support foot vs ball (kick frame): behind p50 {q(-X['sup_behind'], 0.5):+.2f} m,"
    f" lateral p50 {q(X['sup_lat'], 0.5):.2f} m | kicking foot lateral offset p50"
    f" {q(X['kick_lat'], 0.5):.2f} m | support foot on ground at contact"
    f" {100 * X['sup_contact'].mean():.0f} %, flight (both feet up) {100 * X['flight'].mean():.0f} %"
  )
  print(
    f"ANAT steps (touchdowns) in the last 1 s p50 {q(X['steps'], 0.5):.0f}, p90"
    f" {q(X['steps'], 0.9):.0f} | kick-foot airborne before contact p50"
    f" {q(X['swing_t'], 0.5):.2f} s | trunk pitch range in the last 0.3 s p50"
    f" {q(X['pitch_range'], 0.5):.1f} deg"
  )

  sm = X["long"] < 0.5
  lg = X["long"] > 0.5
  print(
    f"ANAT styles: short/medium support planted {100 * X['sup_contact'][sm].mean():.0f} %,"
    f" short/medium inside-foot (60-120 deg) {100 * ((X['foot_yaw'][sm] > 60) & (X['foot_yaw'][sm] < 120)).float().mean():.0f} %,"
    f" long hop {100 * X['flight'][lg].mean():.0f} %"
  )
  nh = max(1, int(X["flight"].sum()))
  npl = max(1, int((X["flight"] < 0.5).sum()))
  print(
    f"ANAT falls within 2 s of a kick: after hop {100 * falls['hop'] / nh:.1f} %"
    f" ({falls['hop']}/{nh}), after planted {100 * falls['planted'] / npl:.1f} %"
  )
  # Kick outcome by technique: hop (both feet up) vs planted, inside foot vs front.
  side = (X["foot_yaw"] > 60) & (X["foot_yaw"] < 120)
  groups = {
    "hop": X["flight"] > 0.5,
    "planted": X["sup_contact"] > 0.5,
    "inside-foot": side,
    "front": X["foot_yaw"] < 30,
  }
  for rng, m0 in (("long", X["long"] > 0.5), ("short/medium", X["long"] < 0.5)):
    for g, m in groups.items():
      mm = m & m0
      if mm.sum() < 5:
        print(f"ANAT {rng:12s} {g:11s} n {int(mm.sum())}")
        continue
      print(
        f"ANAT {rng:12s} {g:11s} n {int(mm.sum()):4d} ({100 * mm.sum() / m0.sum():.0f} %)"
        f" | ball 3D p50 {q(X['speed'][mm], 0.5):.2f} p90 {q(X['speed'][mm], 0.9):.2f} m/s"
        f" | aim <= 20 deg {100 * (X['aim'][mm] <= 20).float().mean():.0f} %"
      )


if __name__ == "__main__":
  main()

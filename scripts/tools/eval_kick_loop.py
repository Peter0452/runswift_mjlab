"""Per-episode evaluation of the stage-3 kick loop.

Runs one full episode per env and reports what "demonstrable and reliable"
means for the kick: kicks per episode, kicks on target, falls (and falls
within 2 s of a kick), goals, time from getting near the ball to the kick, and
whether the ball is back in view after kicks.

  uv run python scripts/tools/eval_kick_loop.py --checkpoint <ckpt>
"""

from __future__ import annotations

import argparse
import math
import os
from dataclasses import asdict

import torch

os.environ["KICK_EVAL"] = "1"  # no mid-kick starts in evaluation

import mjlab.tasks  # noqa: F401  # isort: skip
from mjlab.envs import ManagerBasedRlEnv
from mjlab.managers.event_manager import EventTermCfg
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.tasks.velocity import mdp as vmdp
from mjlab.tasks.velocity.mdp.kick_loop import (
  KickLoopCommand,
  _lateral_gaps,
  arm_pose_deviation,
  knee_gap,
)
from mjlab.utils.lab_api.math import euler_xyz_from_quat, wrap_to_pi

TASK = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"


def main() -> None:
  p = argparse.ArgumentParser(description=__doc__)
  p.add_argument("--checkpoint", required=True)
  p.add_argument(
    "--vision-delay",
    default="",
    help="ball detection delay range in policy steps, e.g. 3,6 (60-120 ms; trained 0,2)",
  )
  p.add_argument("--task", default=TASK)
  p.add_argument("--num-envs", type=int, default=1024)
  p.add_argument("--seed", type=int, default=0)
  p.add_argument("--on-target-deg", type=float, default=20.0)
  p.add_argument("--device", default="cuda:0")
  p.add_argument(
    "--no-push",
    action="store_true",
    help="disable the random push event (falls without external pushes)",
  )
  p.add_argument(
    "--flat",
    action="store_true",
    help="flat plane and no vision dropout / delay (compare with pre-v48 runs)",
  )
  p.add_argument(
    "--moving-ball",
    action="store_true",
    help="rolling ball starts (0-0.8 m/s) and nudges of a resting ball in view (v51b)",
  )
  p.add_argument(
    "--side-drill",
    action="store_true",
    help="every episode starts with the ball 0.4-1.0 m ahead and the target 60-110 deg to the side",
  )
  p.add_argument(
    "--no-vision-noise",
    action="store_true",
    help="keep the terrain but turn off vision dropout / delay",
  )
  p.add_argument(
    "--push-test",
    type=float,
    default=0.0,
    metavar="V",
    help="fixed pushes every 2-3 s with base velocity kicks up to V m/s "
    "(x, y) and 0.6 rad/s (roll, pitch): push-recovery test",
  )
  args = p.parse_args()
  torch.manual_seed(args.seed)

  cfg = load_env_cfg(args.task, play=False)
  cfg.scene.num_envs = args.num_envs
  cfg.seed = args.seed
  if args.flat:
    assert cfg.scene.terrain is not None
    cfg.scene.terrain.terrain_type = "plane"
    cfg.scene.terrain.terrain_generator = None
    twist = cfg.commands["twist"]
    if hasattr(twist, "vision_dropout"):
      twist.vision_dropout = 0.0
      twist.vision_delay_steps = (0, 0)
  if args.moving_ball:
    cfg.commands["twist"].ball_spawn_speed = (0.0, 0.8)
    cfg.events["ball_nudge"] = EventTermCfg(
      mode="interval",
      interval_range_s=(3.0, 6.0),
      func=vmdp.ball_nudge,
      params={"speed_range": (0.3, 1.0), "prob": 0.3, "require_in_view": True},
    )
  if args.side_drill:
    cfg.commands["twist"].side_drill_prob = 1.0
  if args.vision_delay:
    lo, hi = (int(v) for v in args.vision_delay.split(","))
    cfg.commands["twist"].vision_delay_steps = (lo, hi)
  if args.no_vision_noise:
    twist = cfg.commands["twist"]
    if hasattr(twist, "vision_dropout"):
      twist.vision_dropout = 0.0
      twist.vision_delay_steps = (0, 0)
  if args.push_test > 0.0 and "push_robot" in cfg.events:
    push = cfg.events["push_robot"]
    v = args.push_test
    push.params["velocity_range"] = {
      "x": (-v, v),
      "y": (-v, v),
      "roll": (-0.6, 0.6),
      "pitch": (-0.6, 0.6),
    }
    push.interval_range_s = (2.0, 3.0)
  if args.no_push:
    cfg.events.pop("push_robot", None)
  agent = load_rl_cfg(args.task)
  env = RslRlVecEnvWrapper(
    ManagerBasedRlEnv(cfg=cfg, device=args.device), clip_actions=agent.clip_actions
  )
  runner = load_runner_cls(args.task)(env, asdict(agent), device=args.device)
  runner.load(
    args.checkpoint, load_cfg={"actor": True}, strict=True, map_location=args.device
  )
  policy = runner.get_inference_policy(device=args.device)
  obs, _ = env.reset()
  u = env.unwrapped
  cmd = u.command_manager.get_term("twist")
  assert isinstance(cmd, KickLoopCommand)

  n, dev, dt = args.num_envs, args.device, u.step_dt
  active = torch.ones(n, dtype=torch.bool, device=dev)
  fell = torch.zeros_like(active)
  fell_after_kick = torch.zeros_like(active)
  # Falls in the first 2 s mostly come from the motion-pool reset pose.
  fell_late = torch.zeros_like(active)
  kicks = torch.zeros(n, device=dev)
  on_target = torch.zeros(n, device=dev)
  goals = torch.zeros(n, device=dev)
  speed_sum = torch.zeros(n, device=dev)
  quality_sum = torch.zeros(n, device=dev)
  body_at_kick = []
  tilt = []
  gaps, arms, head_pitch, seen, heel_up = [], [], [], [], []
  heel_far, heel_pitch = [], []
  w_height, w_stance, w_valgus, w_knee = [], [], [], []
  idle = torch.zeros(n, device=dev)
  far_rest = torch.zeros(n, device=dev)
  robot = u.scene["robot"]
  feet_ids, _ = robot.find_bodies(
    ("left_foot_link", "right_foot_link"), preserve_order=True
  )
  knee_ids, _ = robot.find_joints((r".*_Knee_Pitch",))
  near_sum = torch.zeros(n, device=dev)
  seen_after = torch.zeros(n, device=dev)
  seen_after_steps = torch.zeros(n, device=dev)
  first_kick_t = torch.full((n,), float("nan"), device=dev)
  cos_min = math.cos(math.radians(args.on_target_deg))

  with torch.inference_mode():
    for t in range(u.max_episode_length + 5):
      # A fallen env is reset inside step(), so keep its time since the kick.
      prev_since_kick = cmd.time_since_kick.clone()
      obs, _, dones, extras = env.step(policy(obs))
      # Events below were set by this step's command update (pre-reset envs
      # that just finished are excluded through ``active``).
      done = dones.bool()
      timeout = extras.get("time_outs", torch.zeros_like(done)).bool()
      live = active & ~done
      k = live & cmd.kick_event
      kicks += k.float()
      on_target += (k & (cmd.kick_cos >= cos_min)).float()
      speed_sum += torch.where(k, cmd.kick_speed, 0.0)
      if hasattr(cmd, "kick_quality"):
        quality_sum += torch.where(k, cmd.kick_quality, 0.0)
        body_at_kick.append(cmd.kick_body_speed[k])
      g = u.scene["robot"].data.projected_gravity_b
      tilt.append(torch.rad2deg(torch.acos((-g[live, 2]).clamp(-1.0, 1.0))))
      gaps.append(knee_gap(u)[live])
      arms.append(arm_pose_deviation(u)[live])
      head_pitch.append(u.scene["robot"].data.joint_pos[live, 1])
      seen.append(cmd.see_ball[live])
      # Ball resting > 1.5 m away, not just kicked: is the robot going to it?
      ball_v = cmd.ball.data.root_link_lin_vel_w[:, :2].norm(dim=-1)
      waiting = live & (cmd.dist > 1.5) & (ball_v < 0.1) & (cmd.time_since_kick > 2.0)
      slow = robot.data.root_link_lin_vel_b[:, :2].norm(dim=-1) < 0.1
      far_rest += waiting.float()
      speed = robot.data.root_link_lin_vel_b[:, :2].norm(dim=-1)
      walking = live & (cmd.dist > 1.0) & (speed > 0.15)
      kg, fg = _lateral_gaps(u)
      w_height.append(robot.data.root_link_pos_w[walking, 2])
      w_stance.append(fg[walking])
      w_valgus.append((fg - kg)[walking])
      w_knee.append(robot.data.joint_pos[walking][:, knee_ids].mean(dim=-1))
      idle += (waiting & slow).float()
      contact = u.scene["feet_ground_contact"].data.found.reshape(n, -1)[:, :2] > 0
      fq = robot.data.body_link_quat_w[:, feet_ids]
      _, pitch, _ = euler_xyz_from_quat(fq.reshape(-1, 4))
      pitch = wrap_to_pi(pitch).reshape(n, 2)
      # Toe-down pitch in this frame is positive (heel up).
      up = pitch > math.radians(5.0)
      heel_up.append(up[contact & live.unsqueeze(-1)])
      far_c = contact & (live & (cmd.dist > 1.5)).unsqueeze(-1)
      heel_far.append(up[far_c])
      heel_pitch.append(pitch[contact & live.unsqueeze(-1)])
      near_sum += torch.where(k, cmd.kick_near_time, 0.0)
      first_kick_t = torch.where(
        k & first_kick_t.isnan(), torch.full_like(first_kick_t, t * dt), first_kick_t
      )
      goals += (live & cmd.goal_event).float()
      window = live & (cmd.time_since_kick > 1.0) & (cmd.time_since_kick < 3.0)
      seen_after += (window & (cmd.see_ball > 0.5)).float()
      seen_after_steps += window.float()
      ended_fall = active & done & ~timeout
      fell |= ended_fall
      fell_late |= ended_fall & (t * dt >= 2.0)
      fell_after_kick |= ended_fall & (prev_since_kick + dt < 2.0)
      active &= ~done
      if not active.any():
        break

  ep_s = u.max_episode_length * dt
  total = kicks.sum().clamp(min=1)
  print(f"== {args.checkpoint}")
  print(f"episodes {n} x {ep_s:.0f} s")
  print(
    f"kicks per episode      mean {kicks.mean():.2f}  (≥1 kick: {(kicks > 0).float().mean():.0%})"
  )
  print(f"kicks on target (≤{args.on_target_deg:.0f}°)  {on_target.sum() / total:.0%}")
  print(f"mean kick ball speed   {speed_sum.sum() / total:.2f} m/s")
  if body_at_kick:
    bodies = torch.cat(body_at_kick)
    print(
      f"kick quality           mean {quality_sum.sum() / total:.2f}   body speed at kick "
      f"median {bodies.median():.2f} m/s"
    )
  tilts = torch.cat(tilt)
  print(
    f"trunk tilt             mean {tilts.mean():.1f}°  p90 "
    f"{torch.quantile(tilts[torch.randperm(len(tilts))[:500000]], 0.9):.1f}°"
  )
  gap = torch.cat(gaps)
  sub = torch.randperm(len(gap), device=gap.device)[:500000]
  print(
    f"knee gap               mean {gap.mean():.3f} m  p10 "
    f"{torch.quantile(gap[sub], 0.1):.3f} m   arm dev rms "
    f"{(torch.cat(arms).mean() / 8).sqrt():.3f} rad"
  )
  print(
    f"head pitch             mean {torch.cat(head_pitch).mean():+.2f} rad   "
    f"ball in view {torch.cat(seen).mean():.0%}"
  )
  hu = torch.cat(heel_up).float()
  print(
    f"walking pose           base {torch.cat(w_height).mean():.3f} m  knee flex "
    f"{torch.cat(w_knee).mean():.2f} rad  stance {torch.cat(w_stance).mean():.3f} m  "
    f"feet−knees {torch.cat(w_valgus).mean():+.3f} m (gold: 0.544, 0.41, 0.151, −0.037)"
  )
  print(
    f"idle at a far ball     {idle.sum() / far_rest.sum().clamp(min=1):.0%} of time "
    "the ball rests > 1.5 m away (robot < 0.1 m/s)"
  )
  hp = torch.rad2deg(torch.cat(heel_pitch))
  print(
    f"stance heel-up > 5°    {hu.mean():.1%} of contact samples "
    f"(walking, ball > 1.5 m: {torch.cat(heel_far).float().mean():.1%}); "
    f"sole pitch p50/p90 {hp.median():.1f}/{torch.quantile(hp[:500000], 0.9):.1f}°"
  )
  print(f"time near ball → kick  mean {near_sum.sum() / total:.2f} s")
  print(f"first kick at          median {first_kick_t.nanmedian():.1f} s")
  print(f"goals per episode      mean {goals.mean():.2f}")
  print(
    f"fell during episode    {fell.float().mean():.1%}   after the first 2 s "
    f"{fell_late.float().mean():.1%}   within 2 s of a kick "
    f"{fell_after_kick.float().mean():.1%}"
  )
  print(
    f"ball in view 1–3 s after kicks  {seen_after.sum() / seen_after_steps.sum().clamp(min=1):.0%}"
  )


if __name__ == "__main__":
  main()

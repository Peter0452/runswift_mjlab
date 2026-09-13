"""Record near-kick pose / joints around the first strong-ish kick events.

Usage:
  MUJOCO_GL=egl uv run python scripts/record_kick_kinematics.py \
    --checkpoint logs/rsl_rl/k1_arc_kick/<run>/model_XXXX.pt
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch

from mjlab.rl import RslRlVecEnvWrapper
from mjlab.rl.runner import MjlabOnPolicyRunner
from mjlab.tasks.kick.mdp.ball_phase import ensure_ball_phase_updated
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.utils.torch import configure_torch_backends
from mjlab.utils.os import get_wandb_checkpoint_path  # noqa: F401 — unused keep import light


def _parse_args() -> argparse.Namespace:
  p = argparse.ArgumentParser()
  p.add_argument("--task", default="Mjlab-Kick-Near-Booster-K1")
  p.add_argument("--checkpoint", required=True)
  p.add_argument("--num-envs", type=int, default=256)
  p.add_argument("--max-steps", type=int, default=400)
  p.add_argument("--pre-steps", type=int, default=20)
  p.add_argument("--post-steps", type=int, default=30)
  p.add_argument("--min-kick-speed", type=float, default=1.2)
  p.add_argument("--max-events", type=int, default=5)
  p.add_argument(
    "--out-dir",
    default="logs/kick_kinematics",
  )
  return p.parse_args()


def main() -> None:
  args = _parse_args()
  configure_torch_backends()
  device = "cuda:0" if torch.cuda.is_available() else "cpu"
  ckpt = Path(args.checkpoint).resolve()
  if not ckpt.exists():
    raise FileNotFoundError(ckpt)

  env_cfg = load_env_cfg(args.task, play=True)
  env_cfg.scene.num_envs = int(args.num_envs)
  # Keep terminations so episodes reset; we only care about kick windows.
  agent_cfg = load_rl_cfg(args.task)

  from mjlab.envs import ManagerBasedRlEnv

  raw_env = ManagerBasedRlEnv(cfg=env_cfg, device=device)
  env = RslRlVecEnvWrapper(raw_env, clip_actions=agent_cfg.clip_actions)
  runner_cls = load_runner_cls(args.task) or MjlabOnPolicyRunner
  runner = runner_cls(env, asdict(agent_cfg), device=device)
  runner.load(str(ckpt), load_cfg={"actor": True}, strict=True, map_location=device)
  policy = runner.get_inference_policy(device=device)

  robot = raw_env.scene["robot"]
  ball = raw_env.scene["ball"]
  joint_names = list(robot.joint_names)
  left_ids, _ = robot.find_bodies("left_foot_link")
  right_ids, _ = robot.find_bodies("right_foot_link")
  foot_ids = [left_ids[0], right_ids[0]]

  n = raw_env.num_envs
  pre, post = int(args.pre_steps), int(args.post_steps)
  buf_len = pre + post + 1
  # Ring buffer per-env of recent frames.
  ring_q = torch.zeros(buf_len, n, len(joint_names), device=device)
  ring_qd = torch.zeros_like(ring_q)
  ring_root = torch.zeros(buf_len, n, 7, device=device)  # pos3 + quat4
  ring_root_v = torch.zeros(buf_len, n, 6, device=device)
  ring_feet = torch.zeros(buf_len, n, 2, 3, device=device)
  ring_ball = torch.zeros(buf_len, n, 3, device=device)
  ring_ball_v = torch.zeros(buf_len, n, 3, device=device)
  ring_t = torch.zeros(buf_len, n, device=device)
  ring_i = 0
  filled = 0

  prev_kick = torch.zeros(n, dtype=torch.bool, device=device)
  events: list[dict] = []
  captured_envs: set[int] = set()

  obs, _ = env.reset()
  for step in range(int(args.max_steps)):
    with torch.inference_mode():
      actions = policy(obs)
    obs, _, dones, extras = env.step(actions)

    state = ensure_ball_phase_updated(
      raw_env,
      ball_cfg_name="ball",
      goal_command_name="goal",
      robot_cfg_name="robot",
    )
    # Write ring
    idx = ring_i % buf_len
    ring_q[idx] = robot.data.joint_pos
    ring_qd[idx] = robot.data.joint_vel
    ring_root[idx, :, :3] = robot.data.root_link_pos_w
    ring_root[idx, :, 3:] = robot.data.root_link_quat_w
    ring_root_v[idx] = robot.data.root_link_vel_w
    ring_feet[idx] = robot.data.body_link_pos_w[:, foot_ids, :]
    ring_ball[idx] = ball.data.root_link_pos_w
    ring_ball_v[idx] = ball.data.root_link_lin_vel_w
    ring_t[idx] = float(step) * raw_env.step_dt
    ring_i += 1
    filled = min(filled + 1, buf_len)

    kick_now = state.kick_detected
    new_kick = kick_now & ~prev_kick
    vel_ok = state.max_vel_toward_goal >= float(args.min_kick_speed)
    candidates = torch.where(new_kick & vel_ok)[0].tolist()
    prev_kick = kick_now.clone()
    # After reset, clear prev latch for done envs.
    if dones is not None:
      done_ids = torch.where(dones.view(-1).bool())[0]
      prev_kick[done_ids] = False

    for eid in candidates:
      if eid in captured_envs:
        continue
      if filled < pre + 1:
        continue
      # Freeze a snapshot after waiting post steps — schedule by storing pending.
      captured_envs.add(int(eid))
      events.append(
        {
          "env_id": int(eid),
          "trigger_step": int(step),
          "max_vel_toward_goal": float(state.max_vel_toward_goal[eid].item()),
          "pending_post": post,
        }
      )
      if len(events) >= int(args.max_events):
        break

    # Decrement pending and dump when post window elapsed.
    finished = []
    for ev in events:
      if "frames" in ev:
        continue
      if ev["pending_post"] > 0:
        ev["pending_post"] -= 1
        continue
      eid = ev["env_id"]
      # Reconstruct chronological window ending at current ring head.
      order = [(ring_i - 1 - k) % buf_len for k in range(buf_len)][::-1]
      # Keep last pre+1+post frames relative to trigger: trigger was `post` steps ago.
      # Current idx is latest; trigger frame is `post` steps back.
      trig_offset = post
      start = trig_offset + pre
      # order[-1] = now, order[-1-trig_offset] = trigger
      sel = order[-(start + 1) :]
      if len(sel) < pre + post + 1:
        continue
      sel = sel[-(pre + post + 1) :]
      q = ring_q[sel, eid].detach().cpu().numpy()
      qd = ring_qd[sel, eid].detach().cpu().numpy()
      root = ring_root[sel, eid].detach().cpu().numpy()
      root_v = ring_root_v[sel, eid].detach().cpu().numpy()
      feet = ring_feet[sel, eid].detach().cpu().numpy()
      ball_p = ring_ball[sel, eid].detach().cpu().numpy()
      ball_v = ring_ball_v[sel, eid].detach().cpu().numpy()
      t = ring_t[sel, eid].detach().cpu().numpy()
      contact_i = pre
      # Prefer frame of peak |ball speed| in window as "impact" refine.
      speeds = np.linalg.norm(ball_v, axis=-1)
      impact_i = int(np.argmax(speeds))
      ev.update(
        {
          "times_s": t.tolist(),
          "joint_names": joint_names,
          "joint_pos": q,
          "joint_vel": qd,
          "root_pose": root,
          "root_vel": root_v,
          "feet_pos": feet,
          "ball_pos": ball_p,
          "ball_vel": ball_v,
          "contact_index": contact_i,
          "impact_index": impact_i,
          "frames": True,
        }
      )
      finished.append(ev)

    if len(events) >= int(args.max_events) and all("frames" in e for e in events):
      break

  out_dir = Path(args.out_dir)
  out_dir.mkdir(parents=True, exist_ok=True)
  complete = [e for e in events if "frames" in e]
  if not complete:
    summary = {
      "checkpoint": str(ckpt),
      "events": 0,
      "note": "No kick events with min_kick_speed reached in budget.",
      "steps_run": int(step) + 1 if "step" in dir() else 0,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    env.close()
    return

  # Rank by max ball speed in window.
  def peak_speed(ev: dict) -> float:
    return float(np.max(np.linalg.norm(np.asarray(ev["ball_vel"]), axis=-1)))

  complete.sort(key=peak_speed, reverse=True)
  best = complete[0]
  impact = int(best["impact_index"])
  q_imp = np.asarray(best["joint_pos"])[impact]
  default_q = robot.data.default_joint_pos[0].detach().cpu().numpy()
  delta = q_imp - default_q

  # Save npz for best + all
  np.savez_compressed(
    out_dir / "best_kick.npz",
    times_s=np.asarray(best["times_s"]),
    joint_names=np.asarray(best["joint_names"]),
    joint_pos=np.asarray(best["joint_pos"]),
    joint_vel=np.asarray(best["joint_vel"]),
    root_pose=np.asarray(best["root_pose"]),
    root_vel=np.asarray(best["root_vel"]),
    feet_pos=np.asarray(best["feet_pos"]),
    ball_pos=np.asarray(best["ball_pos"]),
    ball_vel=np.asarray(best["ball_vel"]),
    default_joint_pos=default_q,
    impact_index=impact,
    contact_index=best["contact_index"],
  )

  # Human report
  order = np.argsort(-np.abs(delta))
  top = []
  for j in order[:12]:
    top.append(
      {
        "joint": joint_names[j],
        "q_rad": float(q_imp[j]),
        "q_deg": float(np.degrees(q_imp[j])),
        "delta_from_default_deg": float(np.degrees(delta[j])),
      }
    )

  root = np.asarray(best["root_pose"])[impact]
  feet = np.asarray(best["feet_pos"])[impact]
  ball_p = np.asarray(best["ball_pos"])[impact]
  ball_v = np.asarray(best["ball_vel"])[impact]
  # Post-impact standing frame
  post_i = min(len(best["joint_pos"]) - 1, impact + 15)
  feet_post = np.asarray(best["feet_pos"])[post_i]
  lat_post = float(np.linalg.norm(feet_post[0, :2] - feet_post[1, :2]))

  report = {
    "checkpoint": str(ckpt),
    "num_events": len(complete),
    "best_env_id": best["env_id"],
    "best_peak_ball_speed": peak_speed(best),
    "best_max_vel_toward_goal_at_latch": best["max_vel_toward_goal"],
    "dt": float(raw_env.step_dt),
    "window": {"pre": pre, "post": post, "impact_index": impact},
    "at_impact": {
      "root_pos_w": root[:3].tolist(),
      "root_quat_wxyz": root[3:].tolist(),
      "left_foot_pos_w": feet[0].tolist(),
      "right_foot_pos_w": feet[1].tolist(),
      "feet_xy_separation": float(np.linalg.norm(feet[0, :2] - feet[1, :2])),
      "ball_pos_w": ball_p.tolist(),
      "ball_vel_w": ball_v.tolist(),
      "ball_speed": float(np.linalg.norm(ball_v)),
      "robot_to_ball_xy": float(np.linalg.norm(root[:2] - ball_p[:2])),
      "top_joint_deltas_vs_default": top,
      "all_joints_deg": {
        joint_names[i]: float(np.degrees(q_imp[i])) for i in range(len(joint_names))
      },
    },
    "post_impact_standing_proxy": {
      "steps_after_impact": int(post_i - impact),
      "feet_xy_separation": lat_post,
      "root_height": float(np.asarray(best["root_pose"])[post_i, 2]),
    },
    "npz_path": str(out_dir / "best_kick.npz"),
  }
  (out_dir / "report.json").write_text(json.dumps(report, indent=2))
  print(json.dumps(report, indent=2))
  env.close()


if __name__ == "__main__":
  main()

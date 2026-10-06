"""Quantify swing-leg stretch at kick for one or more Near-Amp checkpoints.

Reports hip/knee extrema and swing−plant foot geometry over many kick events.
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
from mjlab.tasks.kick.mdp.geometry import get_approach_waypoint_latch
from mjlab.tasks.kick.mdp.rewards import ball_to_goal_direction_xy
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.utils.lab_api.math import quat_apply_inverse
from mjlab.utils.torch import configure_torch_backends

SWING_JOINTS = (
  "Hip_Pitch",
  "Hip_Roll",
  "Hip_Yaw",
  "Knee_Pitch",
  "Ankle_Pitch",
  "Ankle_Roll",
)


def _parse() -> argparse.Namespace:
  p = argparse.ArgumentParser()
  p.add_argument("--task", default="Mjlab-Kick-Near-Amp-Booster-K1")
  p.add_argument("--checkpoint", action="append", required=True)
  p.add_argument("--label", action="append", default=None)
  p.add_argument("--num-envs", type=int, default=512)
  p.add_argument("--max-steps", type=int, default=500)
  p.add_argument("--min-kick-speed", type=float, default=1.0)
  p.add_argument("--max-events", type=int, default=80)
  return p.parse_args()


def _side_prefix(kicking_is_right: bool) -> str:
  return "Right_" if kicking_is_right else "Left_"


@torch.no_grad()
def measure_one(ckpt: Path, task: str, num_envs: int, max_steps: int,
                min_kick_speed: float, max_events: int, device: str) -> dict:
  env_cfg = load_env_cfg(task, play=True)
  env_cfg.scene.num_envs = int(num_envs)
  agent_cfg = load_rl_cfg(task)

  from mjlab.envs import ManagerBasedRlEnv

  raw_env = ManagerBasedRlEnv(cfg=env_cfg, device=device)
  env = RslRlVecEnvWrapper(raw_env, clip_actions=agent_cfg.clip_actions)
  runner_cls = load_runner_cls(task) or MjlabOnPolicyRunner
  runner = runner_cls(env, asdict(agent_cfg), device=device)
  runner.load(str(ckpt), load_cfg={"actor": True}, strict=True, map_location=device)
  policy = runner.get_inference_policy(device=device)

  robot = raw_env.scene["robot"]
  ball = raw_env.scene["ball"]
  joint_names = list(robot.joint_names)
  name_to_i = {n: i for i, n in enumerate(joint_names)}
  left_ids, _ = robot.find_bodies("left_foot_link")
  right_ids, _ = robot.find_bodies("right_foot_link")
  foot_ids = [left_ids[0], right_ids[0]]

  obs, _ = env.reset()
  # Per-env accumulators for the current latch→kick window.
  n = raw_env.num_envs
  tracking = torch.zeros(n, dtype=torch.bool, device=device)
  peak_ball = torch.zeros(n, device=device)
  max_gap_lat = torch.zeros(n, device=device)
  max_gap_plan = torch.zeros(n, device=device)
  max_gap_sag = torch.zeros(n, device=device)
  max_reach = torch.zeros(n, device=device)  # swing foot → ball xy
  joint_max = {j: torch.full((n,), -1e9, device=device) for j in SWING_JOINTS}
  joint_min = {j: torch.full((n,), 1e9, device=device) for j in SWING_JOINTS}
  kick_side = torch.zeros(n, dtype=torch.long, device=device)  # 1=right

  events: list[dict] = []

  def flush(env_ids: torch.Tensor) -> None:
    nonlocal events
    for e in env_ids.tolist():
      if float(peak_ball[e]) < min_kick_speed:
        continue
      side = "Right" if int(kick_side[e]) == 1 else "Left"
      ev = {
        "peak_ball_speed": float(peak_ball[e]),
        "kick_side": side,
        "max_gap_lat_m": float(max_gap_lat[e]),
        "max_gap_sag_m": float(max_gap_sag[e]),
        "max_gap_planar_m": float(max_gap_plan[e]),
        "max_swing_ball_xy_m": float(max_reach[e]),
        "joints_deg": {},
      }
      for j in SWING_JOINTS:
        ev["joints_deg"][j] = {
          "max": float(np.degrees(joint_max[j][e].item())),
          "min": float(np.degrees(joint_min[j][e].item())),
          "abs_max": float(
            np.degrees(max(abs(joint_max[j][e].item()), abs(joint_min[j][e].item())))
          ),
        }
      events.append(ev)
      if len(events) >= max_events:
        return

  for step in range(max_steps):
    with torch.inference_mode():
      actions = policy(obs)
    obs, _, dones, _ = env.step(actions)
    state = ensure_ball_phase_updated(
      raw_env,
      ball_cfg_name="ball",
      goal_command_name="goal",
      robot_cfg_name="robot",
    )
    q = robot.data.joint_pos
    feet_xy = robot.data.body_link_pos_w[:, foot_ids, :2]
    ball_xy = ball.data.root_link_pos_w[:, :2]
    ball_v = ball.data.root_link_lin_vel_w
    ball_speed = torch.linalg.norm(ball_v[:, :2], dim=-1)

    rel_b = quat_apply_inverse(
      robot.data.root_link_quat_w, ball.data.root_link_pos_w - robot.data.root_link_pos_w
    )
    # rewards: ball_on_left → right foot kicks.
    kicking_right = rel_b[:, 1] > 0.0

    try:
      goal_dir = ball_to_goal_direction_xy(raw_env, ball_xy, "goal")
    except Exception:
      qw = robot.data.root_link_quat_w
      goal_dir = torch.stack(
        [
          1 - 2 * (qw[:, 2] ** 2 + qw[:, 3] ** 2),
          2 * (qw[:, 1] * qw[:, 2] + qw[:, 0] * qw[:, 3]),
        ],
        dim=-1,
      )
      goal_dir = goal_dir / torch.clamp(
        torch.linalg.norm(goal_dir, dim=-1, keepdim=True), min=1e-6
      )
    left_dir = torch.stack((-goal_dir[:, 1], goal_dir[:, 0]), dim=-1)

    swing_idx = kicking_right.long()  # 1=right foot body index
    plant_idx = 1 - swing_idx
    batch = torch.arange(n, device=device)
    swing_xy = feet_xy[batch, swing_idx]
    plant_xy = feet_xy[batch, plant_idx]
    d = swing_xy - plant_xy
    gap_lat = torch.abs(torch.sum(d * left_dir, dim=-1))
    gap_sag = torch.abs(torch.sum(d * goal_dir, dim=-1))
    gap_plan = torch.linalg.norm(d, dim=-1)
    reach = torch.linalg.norm(swing_xy - ball_xy, dim=-1)

    latch = get_approach_waypoint_latch(raw_env)
    at_plant = torch.zeros(n, dtype=torch.bool, device=device)
    if latch is not None:
      at_plant = latch.at_plant.bool()
      # Latch side: +1 = left of axis → right foot kicks (matches rewards).
      if bool((latch.side.abs() > 0.5).any()):
        kicking_right = latch.side > 0.0
        swing_idx = kicking_right.long()
        plant_idx = 1 - swing_idx
        swing_xy = feet_xy[batch, swing_idx]
        plant_xy = feet_xy[batch, plant_idx]
        d = swing_xy - plant_xy
        gap_lat = torch.abs(torch.sum(d * left_dir, dim=-1))
        gap_sag = torch.abs(torch.sum(d * goal_dir, dim=-1))
        gap_plan = torch.linalg.norm(d, dim=-1)
        reach = torch.linalg.norm(swing_xy - ball_xy, dim=-1)
    near = (
      torch.linalg.norm(robot.data.root_link_pos_w[:, :2] - ball_xy, dim=-1) < 0.85
    )
    in_window = (at_plant | near) & (~state.kick_detected)

    # Start tracking when window opens.
    start = in_window & ~tracking
    if start.any():
      ids = start.nonzero(as_tuple=False).view(-1)
      tracking[ids] = True
      peak_ball[ids] = 0
      max_gap_lat[ids] = 0
      max_gap_plan[ids] = 0
      max_gap_sag[ids] = 0
      max_reach[ids] = 0
      kick_side[ids] = kicking_right[ids].long()
      for j in SWING_JOINTS:
        joint_max[j][ids] = -1e9
        joint_min[j][ids] = 1e9

    if tracking.any():
      ids = tracking.nonzero(as_tuple=False).view(-1)
      peak_ball[ids] = torch.maximum(peak_ball[ids], ball_speed[ids])
      max_gap_lat[ids] = torch.maximum(max_gap_lat[ids], gap_lat[ids])
      max_gap_sag[ids] = torch.maximum(max_gap_sag[ids], gap_sag[ids])
      max_gap_plan[ids] = torch.maximum(max_gap_plan[ids], gap_plan[ids])
      max_reach[ids] = torch.maximum(max_reach[ids], reach[ids])
      for e in ids.tolist():
        pref = _side_prefix(bool(kick_side[e].item()))
        for j in SWING_JOINTS:
          ji = name_to_i[pref + j]
          v = q[e, ji]
          joint_max[j][e] = torch.maximum(joint_max[j][e], v)
          joint_min[j][e] = torch.minimum(joint_min[j][e], v)

    # Finalize on kick_detected or episode done while tracking.
    dones_b = dones.view(-1).bool()
    kicked = tracking & state.kick_detected
    done_track = tracking & dones_b
    finish = kicked | done_track
    if finish.any():
      flush(finish.nonzero(as_tuple=False).view(-1))
      tracking[finish] = False
      if len(events) >= max_events:
        break

  env.close()

  def agg(vals: list[float]) -> dict:
    a = np.asarray(vals, dtype=np.float64)
    if a.size == 0:
      return {"n": 0}
    return {
      "n": int(a.size),
      "mean": float(a.mean()),
      "p50": float(np.percentile(a, 50)),
      "p90": float(np.percentile(a, 90)),
      "max": float(a.max()),
    }

  summary = {
    "checkpoint": str(ckpt),
    "num_events": len(events),
    "peak_ball_speed": agg([e["peak_ball_speed"] for e in events]),
    "max_gap_lat_m": agg([e["max_gap_lat_m"] for e in events]),
    "max_gap_sag_m": agg([e["max_gap_sag_m"] for e in events]),
    "max_gap_planar_m": agg([e["max_gap_planar_m"] for e in events]),
    "max_swing_ball_xy_m": agg([e["max_swing_ball_xy_m"] for e in events]),
    "joints_abs_max_deg": {},
    "joints_max_deg": {},
    "joints_min_deg": {},
  }
  for j in SWING_JOINTS:
    summary["joints_abs_max_deg"][j] = agg(
      [e["joints_deg"][j]["abs_max"] for e in events]
    )
    summary["joints_max_deg"][j] = agg([e["joints_deg"][j]["max"] for e in events])
    summary["joints_min_deg"][j] = agg([e["joints_deg"][j]["min"] for e in events])
  return summary


def main() -> None:
  args = _parse()
  configure_torch_backends()
  device = "cuda:0" if torch.cuda.is_available() else "cpu"
  labels = args.label or [None] * len(args.checkpoint)
  while len(labels) < len(args.checkpoint):
    labels.append(None)

  reports = []
  for ckpt_s, label in zip(args.checkpoint, labels, strict=False):
    ckpt = Path(ckpt_s).resolve()
    print(f"Measuring {label or ckpt} …", flush=True)
    rep = measure_one(
      ckpt,
      args.task,
      args.num_envs,
      args.max_steps,
      args.min_kick_speed,
      args.max_events,
      device,
    )
    rep["label"] = label or ckpt.name
    reports.append(rep)
    print(json.dumps(rep, indent=2), flush=True)

  out = Path("logs/kick_kinematics/swing_stretch_compare.json")
  out.parent.mkdir(parents=True, exist_ok=True)
  out.write_text(json.dumps(reports, indent=2))
  print(f"Wrote {out}", flush=True)


if __name__ == "__main__":
  main()

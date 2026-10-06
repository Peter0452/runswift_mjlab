"""Record good kicks in the stage-3 sim as AMP motion clips (K4).

usage: python scripts/tools/record_kick_clips.py {bhuman | ours CK} OUT_DIR PREFIX [N]

Runs the policy with the ball 0.4-1.5 m away at any bearing (flat, ball DR off)
and saves up to N kicks (default 80) as .pkl clips in the AMP dataset format
(fps, root_pos, root_rot xyzw, dof_pos in robot joint order, joint_names,
local_body_pos, link_body_list), 0.8 s before to 0.5 s after contact.
A kick is kept if it is within 15 deg of the target, at least 60 % of the speed
its range needs (3D, long kicks at least 5 m/s), and the robot stays up through
the clip (0.5 s after contact).
"""

import math
import pickle
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch

import mjlab.tasks  # noqa: F401
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.tasks.velocity.mdp.kick_loop import required_kick_speed
from mjlab.utils.lab_api.math import quat_apply_inverse

TASK = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"
DEV = "cuda:0"
PRE, POST = 40, 25  # frames at 50 Hz
JOINT_NAMES = [
  "Head_Yaw", "Head_Pitch", "Left_Shoulder_Pitch", "Left_Shoulder_Roll",
  "Left_Elbow_Pitch", "Left_Elbow_Yaw", "Right_Shoulder_Pitch", "Right_Shoulder_Roll",
  "Right_Elbow_Pitch", "Right_Elbow_Yaw", "Left_Hip_Pitch", "Left_Hip_Roll",
  "Left_Hip_Yaw", "Left_Knee_Pitch", "Left_Ankle_Pitch", "Left_Ankle_Roll",
  "Right_Hip_Pitch", "Right_Hip_Roll", "Right_Hip_Yaw", "Right_Knee_Pitch",
  "Right_Ankle_Pitch", "Right_Ankle_Roll",
]  # fmt: skip
BODIES = [
  "Trunk", "Head_1", "Head_2", "Left_Arm_1", "Left_Arm_2", "Left_Arm_3",
  "left_hand_link", "Right_Arm_1", "Right_Arm_2", "Right_Arm_3", "right_hand_link",
  "Left_Hip_Pitch", "Left_Hip_Roll", "Left_Hip_Yaw", "Left_Shank",
  "Left_Ankle_Cross", "left_foot_link", "Right_Hip_Pitch", "Right_Hip_Roll",
  "Right_Hip_Yaw", "Right_Shank", "Right_Ankle_Cross", "right_foot_link",
]  # fmt: skip


def main() -> None:
  who = sys.argv[1]
  args = sys.argv[2:] if who == "bhuman" else sys.argv[3:]
  out_dir, prefix = Path(args[0]), args[1]
  n_max = int(args[2]) if len(args) > 2 else 80
  out_dir.mkdir(parents=True, exist_ok=True)

  cfg = load_env_cfg(TASK, play=True)
  cfg.scene.num_envs = 256
  for k in (
    "push_robot",
    "push_near_ball",
    "ball_mass",
    "ball_friction",
    "ball_bounce",
  ):
    cfg.events.pop(k, None)
  twist = cfg.commands["twist"]
  twist.ball_distance_range = (0.4, 1.5)
  twist.spawn_view_half_angle = math.pi
  twist.vision_dropout = 0.0
  twist.vision_delay_steps = (0, 0)

  if who == "ours":
    agent = load_rl_cfg(TASK)
    env = RslRlVecEnvWrapper(
      ManagerBasedRlEnv(cfg=cfg, device=DEV), clip_actions=agent.clip_actions
    )
    runner = load_runner_cls(TASK)(env, asdict(agent), device=DEV)
    runner.load(sys.argv[2], load_cfg={"actor": True}, strict=True, map_location=DEV)
    pol = runner.get_inference_policy(device=DEV)
    u = env.unwrapped

    def act(o):
      return pol(o)
  else:
    from mjlab.scripts.play_bhuman_kick import BHumanKickPlayConfig, BHumanKickPolicy

    u = ManagerBasedRlEnv(cfg=cfg, device=DEV)
    env = RslRlVecEnvWrapper(u)
    bh = BHumanKickPolicy(u, BHumanKickPlayConfig(num_envs=256, print_kicks=False))

    def act(o):
      return bh(o)

  obs, _ = env.reset()
  cmd = u.command_manager.get_term("twist")
  rob, ball = u.scene["robot"], u.scene["ball"]
  body_ids = [list(rob.body_names).index(b) for b in BODIES]
  n = u.num_envs
  hist = PRE + POST + 1
  buf_pos = torch.zeros(hist, n, 3, device=DEV)
  buf_rot = torch.zeros(hist, n, 4, device=DEV)
  buf_q = torch.zeros(hist, n, 22, device=DEV)
  buf_body = torch.zeros(hist, n, len(BODIES), 3, device=DEV)
  # Reference-state-init (RSI) data: full robot / ball / target state.
  buf_qd = torch.zeros(hist, n, 22, device=DEV)
  buf_lv = torch.zeros(hist, n, 3, device=DEV)
  buf_av = torch.zeros(hist, n, 3, device=DEV)
  buf_ball = torch.zeros(hist, n, 3, device=DEV)
  buf_bvel = torch.zeros(hist, n, 3, device=DEV)
  buf_tgt = torch.zeros(hist, n, 2, device=DEV)
  rsi_keys = ("root_pos", "root_quat", "lin_vel", "ang_vel", "joint_pos", "joint_vel")
  rsi_keys += ("ball_pos", "ball_vel", "target")
  rsi = {k: [] for k in rsi_keys}
  pending = torch.full((n,), -1, dtype=torch.long, device=DEV)  # frames since kick
  good = torch.zeros(n, dtype=torch.bool, device=DEV)
  fell = torch.zeros(n, dtype=torch.bool, device=DEV)
  saved = 0
  with torch.inference_mode():
    for t in range(20000):
      rng = cmd.kick_range.argmax(-1).clone()
      td = cmd.target_dist.clone()
      obs, _, dones, _ = env.step(act(obs))
      d = rob.data
      for b in (buf_qd, buf_lv, buf_av, buf_ball, buf_bvel, buf_tgt):
        b[:] = torch.roll(b, -1, 0)
      buf_qd[-1] = d.joint_vel
      buf_lv[-1] = d.root_link_lin_vel_w
      buf_av[-1] = d.root_link_ang_vel_w
      buf_ball[-1] = ball.data.root_link_pos_w
      buf_bvel[-1] = ball.data.root_link_lin_vel_w
      buf_tgt[-1] = cmd.target_w
      buf_pos = torch.roll(buf_pos, -1, 0)
      buf_rot = torch.roll(buf_rot, -1, 0)
      buf_q = torch.roll(buf_q, -1, 0)
      buf_body = torch.roll(buf_body, -1, 0)
      buf_pos[-1] = d.root_link_pos_w
      buf_rot[-1] = d.root_link_quat_w
      buf_q[-1] = d.joint_pos
      rel = d.body_link_pos_w[:, body_ids] - d.root_link_pos_w[:, None]
      q = d.root_link_quat_w[:, None].expand(-1, len(BODIES), -1)
      buf_body[-1] = quat_apply_inverse(q.reshape(-1, 4), rel.reshape(-1, 3)).reshape(
        n, len(BODIES), 3
      )
      k = cmd.kick_event & (pending < 0) & (u.episode_length_buf > PRE)
      if k.any():
        need = required_kick_speed(td).clamp(min=0.5)
        long = rng == 2
        fast = (cmd.kick_speed >= 0.6 * need) & (~long | (cmd.kick_speed >= 5.0))
        aimed = cmd.kick_cos >= math.cos(math.radians(15.0))
        good = torch.where(k, fast & aimed, good)
        fell = torch.where(k, torch.zeros_like(fell), fell)
        pending = torch.where(k, torch.zeros_like(pending), pending)
      active = pending >= 0
      fell |= active & ((d.root_link_pos_w[:, 2] < 0.35) | dones.bool())
      pending = torch.where(active, pending + 1, pending)
      ready = pending == POST
      for i in ready.nonzero(as_tuple=False).flatten().tolist():
        if good[i] and not fell[i] and saved < n_max:
          sl = slice(hist - (PRE + POST + 1), hist)
          rot_wxyz = buf_rot[sl, i].cpu().numpy()
          clip = {
            "fps": 50.0,
            "root_pos": buf_pos[sl, i].cpu().numpy(),
            "root_rot": rot_wxyz[:, [1, 2, 3, 0]],
            "dof_pos": buf_q[sl, i].cpu().numpy(),
            "local_body_pos": buf_body[sl, i].cpu().numpy(),
            "link_body_list": BODIES,
            "joint_names": JOINT_NAMES,
            "source_clip": f"{prefix} kick env {i} step {t}",
          }
          with open(out_dir / f"{prefix}_{saved:03d}.pkl", "wb") as f:
            pickle.dump(clip, f)
          # RSI starts at 0.4, 0.3 and 0.2 s before contact.
          for back in (20, 15, 10):
            j = hist - 1 - POST - back
            for key, b in (
              ("root_pos", buf_pos), ("root_quat", buf_rot), ("lin_vel", buf_lv),
              ("ang_vel", buf_av), ("joint_pos", buf_q), ("joint_vel", buf_qd),
              ("ball_pos", buf_ball), ("ball_vel", buf_bvel), ("target", buf_tgt),
            ):  # fmt: skip
              rsi[key].append(b[j, i].cpu().numpy())
          saved += 1
      # Wait for the robot to stay up a full second before the next kick.
      pending = torch.where(pending >= 50, torch.full_like(pending, -1), pending)
      if saved >= n_max:
        break
  rsi_dir = out_dir.parent / "kick_rsi"
  rsi_dir.mkdir(parents=True, exist_ok=True)
  np.savez(rsi_dir / f"{prefix}.npz", **{k: np.stack(v) for k, v in rsi.items()})
  print(
    f"RECORD {who}: saved {saved} kick clips to {out_dir} and"
    f" {len(rsi['root_pos'])} RSI states after {t + 1} steps"
  )


if __name__ == "__main__":
  main()

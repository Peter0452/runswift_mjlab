"""Parity of the lost-ball rule: training env vs the runner's KickLoopPolicy.

Runs the training env (flat, no vision noise / dropout / delay) with a policy,
moves the ball out of view a few times, and feeds the runner's observation
builder the same detections, IMU yaw and head joints each step. Compares the
ball slots (72-73) and age (74).

usage: python scripts/tools/lost_rule_parity.py CHECKPOINT RUNNER_PY_DIR ONNX
"""

import math
import os
import sys
from dataclasses import asdict

os.environ["KICK_EVAL"] = "1"

import numpy as np  # noqa: E402
import torch  # noqa: E402

import mjlab.tasks  # noqa: E402, F401
from mjlab.envs import ManagerBasedRlEnv  # noqa: E402
from mjlab.rl import RslRlVecEnvWrapper  # noqa: E402
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls  # noqa: E402

T = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"
ck, runner_dir, onnx = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, runner_dir)
from policy_runner.policy.kick_loop_policy import KickLoopPolicy  # noqa: E402
from policy_runner.types import ImuState, RobotState  # noqa: E402

cfg = load_env_cfg(T)
cfg.scene.num_envs = 1
for k in ("push_robot", "push_near_ball", "ball_relocate_unseen"):
  cfg.events.pop(k, None)
cfg.scene.terrain.terrain_type = "plane"
cfg.scene.terrain.terrain_generator = None
tw = cfg.commands["twist"]
tw.vision_dropout = 0.0
tw.vision_delay_steps = (0, 0)
tw.ball_obs_noise = (0.0, 0.0)
agent = load_rl_cfg(T)
env = RslRlVecEnvWrapper(ManagerBasedRlEnv(cfg=cfg, device="cuda:0"), clip_actions=agent.clip_actions)
r = load_runner_cls(T)(env, asdict(agent), device="cuda:0")
r.load(ck, load_cfg={"actor": True}, strict=True, map_location="cuda:0")
pol = r.get_inference_policy(device="cuda:0")
u = env.unwrapped
cmd = u.command_manager.get_term("twist")
rob, ball = u.scene["robot"], u.scene["ball"]
kp = KickLoopPolicy(model_path=onnx, ball_hold_s=0.0, lost_rule=True)
obs, _ = env.reset()
dt = u.step_dt
errs, lost_steps, mism = [], 0, 0
with torch.inference_mode():
  for t in range(1500):
    if t % 300 == 150:  # move the ball behind the robot, out of view
      q = rob.data.root_link_quat_w[0]
      yaw = math.atan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] ** 2 + q[3] ** 2))
      ang = yaw + math.pi + np.random.uniform(-0.8, 0.8)
      pose = ball.data.root_link_pose_w.clone()
      pose[0, 0] = rob.data.root_link_pos_w[0, 0] + 2.5 * math.cos(ang)
      pose[0, 1] = rob.data.root_link_pos_w[0, 1] + 2.5 * math.sin(ang)
      ball.write_root_state_to_sim(torch.cat((pose, torch.zeros(1, 6, device="cuda:0")), -1), torch.tensor([0], device="cuda:0"))
    # Training obs this step (after the command update of the previous step).
    train = obs["actor"][0, 72:75].cpu().numpy()
    q = rob.data.root_link_quat_w[0].cpu().numpy()
    yaw = math.atan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] ** 2 + q[3] ** 2))
    seen = bool(cmd.see_ball[0] > 0.5)
    st = RobotState(
      q=rob.data.joint_pos[0].cpu().tolist(),
      dq=rob.data.joint_vel[0].cpu().tolist(),
      imu=ImuState(rpy=[0.0, 0.0, yaw], gyro=[0.0, 0.0, 0.0]),
      ball_rel_pos=[float(cmd.true_ball_b[0, 0]), float(cmd.true_ball_b[0, 1]), 0.0],
      has_ball=seen,
      time_s=t * dt,
    )
    if seen:
      kp._seen_counter = getattr(kp, "_seen_counter", 0) + 1
      st.ball_seen_time = t * dt
    else:
      st.ball_seen_time = kp._mem_seen_time if kp._mem_seen_time is not None else -1.0
    run = kp._kick_slots(st)[:3]
    if bool(cmd.ball_lost[0]):
      lost_steps += 1
    e = float(np.abs(run - train).max())
    errs.append(e)
    if e > 0.05:
      mism += 1
    obs, _, _, _ = env.step(pol(obs))
errs = np.array(errs)
print(
  f"PARITY lost-rule: steps {len(errs)}, training-lost steps {lost_steps}, slot 72-74"
  f" |diff| p50 {np.median(errs):.3f} p99 {np.quantile(errs, 0.99):.3f}, steps with diff > 0.05: {mism}"
)

"""How a policy kicks: ball 3D / ground speed, launch angle, body speed, kick-foot
yaw vs the kick direction, foot speed and peak torques at each kick.

usage: python scripts/tools/kick_style_compare.py {ours CK | bhuman} [--heavy]
  --heavy  B-Human's ball (0.29 kg, r 0.095 m) instead of ours (0.10 kg, r 0.08 m)
Ball spawned 0.4-1.5 m away (B-Human's kick-policy range), flat, nominal ball DR off.
"""

import math
import os
import sys
from dataclasses import asdict

import torch

os.environ["KICK_EVAL"] = "1"  # no mid-kick starts in evaluation

import mjlab.tasks  # noqa: F401  # isort: skip
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.tasks.velocity.config.k1_amp import env_cfgs as ec
from mjlab.utils.lab_api.math import wrap_to_pi

TASK = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"
DEV = "cuda:0"
who = sys.argv[1]
heavy = "--heavy" in sys.argv
# --any-bearing: ball anywhere around the robot (not just in view ahead)
any_bearing = "--any-bearing" in sys.argv
# --perception true|camera (default camera for ours, true for B-Human, as before)
perception = (
  sys.argv[sys.argv.index("--perception") + 1] if "--perception" in sys.argv else None
)
if heavy:
  ec._APPROACH_BALL_MASS = 0.29
  ec._APPROACH_BALL_RADIUS = 0.095

cfg = load_env_cfg(TASK, play=True)
cfg.scene.num_envs = 512
for k in ("push_robot", "push_near_ball", "ball_mass", "ball_friction", "ball_bounce"):
  cfg.events.pop(k, None)
cfg.commands["twist"].ball_distance_range = (0.4, 1.5)
cfg.commands["twist"].vision_dropout = 0.0
cfg.commands["twist"].vision_delay_steps = (0, 0)
if any_bearing:
  cfg.commands["twist"].spawn_view_half_angle = math.pi
# Perception, the same definition for both policies (fair head-to-head):
#   camera: head-camera view, Gaussian noise, 2 % dropout, 0-2 step delay;
#           B-Human gets that detection (with odometry when unseen).
#   true:   exact ball every step (always visible, no noise / dropout / delay).
# Without --perception: ours = camera without dropout / delay, B-Human = true
# (the original, unfair setting).
tw = cfg.commands["twist"]
if perception == "camera":
  tw.vision_dropout = 0.02
  tw.vision_delay_steps = (0, 2)
elif perception == "true":
  tw.fov_half_angle = math.pi
  tw.fov_vertical_half_angle = None
  tw.ball_obs_noise = (0.0, 0.0)

if who == "ours":
  agent = load_rl_cfg(TASK)
  env = RslRlVecEnvWrapper(
    ManagerBasedRlEnv(cfg=cfg, device=DEV), clip_actions=agent.clip_actions
  )
  r = load_runner_cls(TASK)(env, asdict(agent), device=DEV)
  r.load(sys.argv[2], load_cfg={"actor": True}, strict=True, map_location=DEV)
  pol = r.get_inference_policy(device=DEV)
  u = env.unwrapped
  obs, _ = env.reset()

  def step(o):
    return env.step(pol(o))[0]
else:
  from mjlab.scripts.play_bhuman_kick import BHumanKickPlayConfig, BHumanKickPolicy

  u = ManagerBasedRlEnv(cfg=cfg, device=DEV)
  env = RslRlVecEnvWrapper(u)
  obs, _ = env.reset()
  bh = BHumanKickPolicy(
    u,
    BHumanKickPlayConfig(
      num_envs=512, print_kicks=False, perception=perception or "true"
    ),
  )

  def step(o):
    return env.step(bh(o))[0]


cmd = u.command_manager.get_term("twist")
rob, ball = u.scene["robot"], u.scene["ball"]
feet, _ = rob.find_bodies(("left_foot_link", "right_foot_link"), preserve_order=True)
acts = [u.sim.mj_model.actuator(i).name for i in range(u.sim.mj_model.nu)]
hip = [i for i, a in enumerate(acts) if "Hip_Pitch" in a]
knee = [i for i, a in enumerate(acts) if "Knee_Pitch" in a]
n = u.num_envs
age = torch.full((n,), 99, device=DEV)
peak3 = torch.zeros(n, device=DEV)
rec = {
  k: []
  for k in ("v3", "vg", "ang", "body", "yaw", "foot", "hip", "knee", "aim", "long")
}
tq_hip = torch.zeros(n, device=DEV)
tq_knee = torch.zeros(n, device=DEV)
snap = {}
first_kick_t = torch.full((n,), float("nan"), device=DEV)
first_target = torch.zeros(n, dtype=torch.bool, device=DEV)


def yaw_of(q):
  return torch.atan2(
    2 * (q[..., 0] * q[..., 3] + q[..., 1] * q[..., 2]),
    1 - 2 * (q[..., 2] ** 2 + q[..., 3] ** 2),
  )


with torch.inference_mode():
  for t in range(1500):
    obs = step(obs)
    k = cmd.kick_event.clone()
    if t < 500:
      new = k & torch.isnan(first_kick_t)
      first_kick_t = torch.where(
        new, torch.full_like(first_kick_t, t * u.step_dt), first_kick_t
      )
      first_target = torch.where(
        new, cmd.kick_cos > math.cos(math.radians(20)), first_target
      )
    f = u.sim.data.actuator_force
    th = f[:, hip].abs().max(-1).values
    tk = f[:, knee].abs().max(-1).values
    tq_hip = torch.where(age < 8, torch.maximum(tq_hip, th), tq_hip)
    tq_knee = torch.where(age < 8, torch.maximum(tq_knee, tk), tq_knee)
    if k.any():
      bp = ball.data.root_link_pos_w[:, :2]
      fp = rob.data.body_link_pos_w[:, feet, :2]
      which = (fp - bp[:, None]).norm(dim=-1).argmin(-1)
      rows = torch.arange(n, device=DEV)
      fyaw = yaw_of(
        rob.data.body_link_quat_w[
          rows, feet[0] if False else torch.tensor(feet, device=DEV)[which]
        ]
      )
      to = cmd.target_w - bp
      kdir = torch.atan2(to[:, 1], to[:, 0])
      fv = rob.data.body_link_lin_vel_w[rows, torch.tensor(feet, device=DEV)[which], :2]
      bv = rob.data.root_link_lin_vel_w[:, :2]
      snap_new = {
        "body": bv.norm(dim=-1),
        "yaw": wrap_to_pi(fyaw - kdir).abs(),
        "foot": (fv - bv).norm(dim=-1),
      }
      for key, val in snap_new.items():
        snap[key] = torch.where(k, val, snap.get(key, torch.zeros_like(val)))
      tq_hip = torch.where(k, th, tq_hip)
      tq_knee = torch.where(k, tk, tq_knee)
      peak3 = torch.where(k, torch.zeros_like(peak3), peak3)
    age = torch.where(k, torch.zeros_like(age), age + 1)
    v = ball.data.root_link_lin_vel_w
    peak3 = torch.where(age <= 5, torch.maximum(peak3, v.norm(dim=-1)), peak3)
    done = age == 6
    if done.any():
      vg = v[:, :2].norm(dim=-1)
      rec["v3"].append(peak3[done])
      rec["vg"].append(cmd.kick_speed[done])
      rec["ang"].append(torch.rad2deg(cmd.kick_launch_angle[done]))
      rec["aim"].append(torch.rad2deg(torch.acos(cmd.kick_cos[done].clamp(-1, 1))))
      for key in ("body", "yaw", "foot"):
        rec[key].append(snap[key][done])
      rec["long"].append(cmd.kick_long[done])
      rec["hip"].append(tq_hip[done])
      rec["knee"].append(tq_knee[done])

R = {k: torch.cat(v) for k, v in rec.items()}


def q(x, p):
  return float(x.quantile(p)) if len(x) else float("nan")


yaw = torch.rad2deg(R["yaw"])
print(
  f"STYLE {who} {'heavy 0.29 kg' if heavy else 'light 0.10 kg'} ball, kicks {len(R['v3'])}"
)
print(
  f"STYLE ball 3D peak p50 {q(R['v3'], 0.5):.2f} p90 {q(R['v3'], 0.9):.2f} | ground at launch p50 {q(R['vg'], 0.5):.2f} p90 {q(R['vg'], 0.9):.2f} m/s | launch angle p50 {q(R['ang'], 0.5):+.1f} deg | aim err <= 20 deg {100 * (R['aim'] <= 20).float().mean():.0f} %"
)
print(
  f"STYLE body speed at contact p50 {q(R['body'], 0.5):.2f} m/s | kick-foot speed rel. body p50 {q(R['foot'], 0.5):.2f} p90 {q(R['foot'], 0.9):.2f} m/s"
)
print(
  f"STYLE kick-foot yaw vs kick direction p50 {q(yaw, 0.5):.0f} deg; front (< 30) {100 * (yaw < 30).float().mean():.0f} %, side-foot (60-120) {100 * ((yaw > 60) & (yaw < 120)).float().mean():.0f} %"
)
print(
  f"STYLE peak torque around kick: hip pitch p50 {q(R['hip'], 0.5):.0f} p90 {q(R['hip'], 0.9):.0f} Nm, knee p50 {q(R['knee'], 0.5):.0f} p90 {q(R['knee'], 0.9):.0f} Nm"
)
L = R["long"]
for name, m in (("long (>= 8 m)", L), ("short / medium", ~L)):
  print(
    f"STYLE {name}: ball 3D p50 {q(R['v3'][m], 0.5):.2f} p90 {q(R['v3'][m], 0.9):.2f} m/s,"
    f" ground p50 {q(R['vg'][m], 0.5):.2f}, launch p50 {q(R['ang'][m], 0.5):+.1f} deg,"
    f" body {q(R['body'][m], 0.5):.2f} m/s, hip p90 {q(R['hip'][m], 0.9):.0f} Nm, knee p90"
    f" {q(R['knee'][m], 0.9):.0f} Nm, aim <= 20 deg {100 * (R['aim'][m] <= 20).float().mean():.0f} %"
  )
ok = ~torch.isnan(first_kick_t)
print(
  f"STYLE first kick within 10 s: {100 * ok.float().mean():.0f} % of robots, time p50"
  f" {q(first_kick_t[ok], 0.5):.2f} s p90 {q(first_kick_t[ok], 0.9):.2f} s, first kick within 20 deg"
  f" {100 * first_target[ok].float().mean():.0f} %"
)

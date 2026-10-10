"""Scripted K1 kick-style gallery: one MP4 per kick style (illustration, not a policy).

The K1 MJCF (xml_whirlwind) gets position servos with the real effort limits
(hip pitch 68, hip roll 76, hip yaw 38, knee 112, ankles 38 Nm), so a motion is
only as fast as the motors allow. The trunk is welded to a scripted mocap anchor
(held, stepped forward, turned or lifted per style) so one-legged poses do not
topple; the legs follow keyframes. A 0.10 kg, r 0.08 m ball is placed in front
of the striking surface at the style's contact pose. Ball speed and direction
after the kick are printed and drawn on the video.

usage: MUJOCO_GL=glfw python scripts/tools/kick_style_gallery.py [OUT_DIR] [style ...]
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import imageio
import mujoco
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
XML = ROOT / "src/mjlab/asset_zoo/robots/booster_k1/xml_whirlwind/k1.xml"
FPS = 50
DT = 0.002
BALL_R, BALL_M = 0.08, 0.10

DEFAULT = {
  "Hip_Pitch": -0.4, "Hip_Roll": 0.0, "Hip_Yaw": 0.0,
  "Knee_Pitch": 0.8, "Ankle_Pitch": -0.4, "Ankle_Roll": 0.0,
}  # fmt: skip
EFFORT = {
  "Hip_Pitch": 68.0, "Hip_Roll": 76.0, "Hip_Yaw": 38.3,
  "Knee_Pitch": 112.0, "Ankle_Pitch": 38.3, "Ankle_Roll": 38.3,
}  # fmt: skip
ARMS = {"Left_Shoulder_Roll": -1.4, "Right_Shoulder_Roll": 1.4, "Left_Elbow_Yaw": -0.4, "Right_Elbow_Yaw": 0.4}


def leg(**d):
  """Right (kicking) leg targets as offsets from the default pose."""
  out = dict(DEFAULT)
  for k, v in d.items():
    out[k] = DEFAULT[k] + v
  return out


# Each style: keyframes [(t, right_leg, left_leg_offsets, anchor (dx, dy, dz, yaw))],
# contact keyframe index, kick direction (world xy), striking face offset (m)
# from the foot sole site along the kick direction, and a one-line note.
# Signs (K1 right leg): hip pitch - = forward, knee + = bend, ankle pitch + =
# toes down, hip roll + = inward (adduct), hip yaw + = toes in.
STYLES: dict[str, dict] = {
  "1_front_kick": dict(
    note="hip pitch + knee snap, toe/front of foot, straight ahead (ours)",
    keys=[
      (0.0, leg(), {}, (0, 0, 0, 0)),
      (0.35, leg(Hip_Pitch=0.7, Knee_Pitch=0.8, Ankle_Pitch=0.2), {}, (0, 0, 0, 0)),
      (0.52, leg(Hip_Pitch=-0.45, Knee_Pitch=-0.65, Ankle_Pitch=0.25), {}, (0, 0, 0, 0)),
      (0.75, leg(Hip_Pitch=-0.75, Knee_Pitch=-0.5), {}, (0, 0, 0, 0)),
      (1.3, leg(), {}, (0, 0, 0, 0)),
    ],
    contact=2, dir=(1.0, 0.0), face=0.075,
  ),
  "2_inside_sweep": dict(
    note="body angled + hip yaw toe-out, inside of foot sweeps across (B-Human)",
    keys=[
      (0.0, leg(), {}, (0, 0, 0, 0)),
      (0.35, leg(Hip_Pitch=0.45, Knee_Pitch=0.6, Hip_Yaw=-1.0, Hip_Roll=-0.25), {}, (0.0, 0, 0, -0.55)),
      (0.56, leg(Hip_Pitch=-0.75, Knee_Pitch=-0.55, Hip_Yaw=-1.0, Hip_Roll=0.12), {}, (0.05, 0, 0, -0.55)),
      (0.8, leg(Hip_Pitch=-0.9, Knee_Pitch=-0.4, Hip_Yaw=-0.8, Hip_Roll=0.2), {}, (0.07, 0, 0, -0.55)),
      (1.3, leg(), {}, (0.07, 0, 0, -0.55)),
    ],
    contact=2, dir=(1.0, 0.0), face=0.04,
  ),
  "3_outside_flick": dict(
    note="hip yaw toe-in + hip roll outward, outer edge, to the kicking-leg side",
    keys=[
      (0.0, leg(), {}, (0, 0, 0, 0)),
      (0.3, leg(Hip_Pitch=0.2, Knee_Pitch=0.5, Hip_Yaw=0.6, Hip_Roll=0.3), {}, (0, 0, 0, 0)),
      (0.48, leg(Hip_Pitch=-0.3, Knee_Pitch=-0.2, Hip_Yaw=0.6, Hip_Roll=-0.6), {}, (0, 0, 0, 0)),
      (0.7, leg(Hip_Pitch=-0.3, Knee_Pitch=-0.1, Hip_Yaw=0.4, Hip_Roll=-0.75), {}, (0, 0, 0, 0)),
      (1.2, leg(), {}, (0, 0, 0, 0)),
    ],
    contact=2, dir=(0.5, -0.866), face=0.04,
  ),
  "4_side_kick": dict(
    note="hip roll swings the leg sideways (90 deg range, 76 Nm), ball to the side",
    keys=[
      (0.0, leg(), {}, (0, 0, 0, 0)),
      (0.3, leg(Knee_Pitch=0.3, Hip_Roll=0.35, Hip_Pitch=-0.05), {}, (0, 0, 0, 0)),
      (0.48, leg(Knee_Pitch=-0.2, Hip_Roll=-0.85, Hip_Pitch=-0.05), {}, (0, 0, 0, 0)),
      (0.7, leg(Knee_Pitch=-0.2, Hip_Roll=-1.0), {}, (0, 0, 0, 0)),
      (1.2, leg(), {}, (0, 0, 0, 0)),
    ],
    contact=2, dir=(0.0, -1.0), face=0.04,
  ),
  "5_instep_drive": dict(
    note="toes pointed down (ankle +0.35 max = only 20 deg), top of foot, power",
    keys=[
      (0.0, leg(), {}, (0, 0, 0, 0)),
      (0.38, leg(Hip_Pitch=0.8, Knee_Pitch=1.0, Ankle_Pitch=0.74), {}, (0, 0, 0, 0)),
      (0.56, leg(Hip_Pitch=-0.5, Knee_Pitch=-0.6, Ankle_Pitch=0.74), {}, (0.03, 0, 0, 0)),
      (0.8, leg(Hip_Pitch=-0.9, Knee_Pitch=-0.5, Ankle_Pitch=0.5), {}, (0.05, 0, 0, 0)),
      (1.3, leg(), {}, (0.05, 0, 0, 0)),
    ],
    contact=2, dir=(1.0, 0.0), face=0.06,
  ),
  "6_toe_poke": dict(
    note="minimal backswing, quick knee extension, toe tip: fastest, least power",
    keys=[
      (0.0, leg(), {}, (0, 0, 0, 0)),
      (0.15, leg(Hip_Pitch=0.05, Knee_Pitch=0.7, Ankle_Pitch=0.1), {}, (0, 0, 0, 0)),
      (0.28, leg(Hip_Pitch=-0.6, Knee_Pitch=-0.7, Ankle_Pitch=0.2), {}, (0.03, 0, 0, 0)),
      (0.5, leg(Hip_Pitch=-0.5, Knee_Pitch=-0.5), {}, (0.03, 0, 0, 0)),
      (0.9, leg(), {}, (0.03, 0, 0, 0)),
    ],
    contact=2, dir=(1.0, 0.0), face=0.075,
  ),
  "7_chip": dict(
    note="toes up (ankle -0.6), body lowered, foot scoops under the ball: lofted",
    keys=[
      (0.0, leg(), {}, (0, 0, 0, 0)),
      (0.35, leg(Hip_Pitch=0.6, Knee_Pitch=1.0, Ankle_Pitch=-0.45), {"Knee_Pitch": 0.25, "Hip_Pitch": -0.12}, (0, 0, -0.04, 0)),
      (0.53, leg(Hip_Pitch=-0.55, Knee_Pitch=-0.2, Ankle_Pitch=-0.45), {"Knee_Pitch": 0.25, "Hip_Pitch": -0.12}, (0.02, 0, -0.04, 0)),
      (0.78, leg(Hip_Pitch=-1.0, Knee_Pitch=-0.4, Ankle_Pitch=-0.3), {}, (0.02, 0, 0, 0)),
      (1.3, leg(), {}, (0.02, 0, 0, 0)),
    ],
    contact=2, dir=(1.0, 0.0), face=0.07,
  ),
  "8_back_heel": dict(
    note="hip extension + knee bend, heel strikes the ball behind the robot",
    keys=[
      (0.0, leg(), {}, (0, 0, 0, 0)),
      (0.3, leg(Hip_Pitch=-0.3, Knee_Pitch=0.2), {}, (0, 0, 0, 0)),
      (0.48, leg(Hip_Pitch=0.75, Knee_Pitch=0.35), {}, (0, 0, 0, 0)),
      (0.7, leg(Hip_Pitch=0.85, Knee_Pitch=0.6), {}, (0, 0, 0, 0)),
      (1.2, leg(), {}, (0, 0, 0, 0)),
    ],
    contact=2, dir=(-1.0, 0.0), face=0.075,
  ),
  "9_walking_push": dict(
    note="no separate swing: the stride pushes the ball (dribble / short pass)",
    keys=[
      (0.0, leg(), {}, (0, 0, 0, 0)),
      (0.25, leg(Hip_Pitch=-0.15, Knee_Pitch=0.4), {"Hip_Pitch": 0.15}, (0.05, 0, 0, 0)),
      (0.45, leg(Hip_Pitch=-0.4, Knee_Pitch=0.0), {"Hip_Pitch": 0.25}, (0.12, 0, 0, 0)),
      (0.7, leg(Hip_Pitch=-0.2), {"Hip_Pitch": 0.1}, (0.2, 0, 0, 0)),
      (1.1, leg(), {}, (0.24, 0, 0, 0)),
    ],
    contact=2, dir=(1.0, 0.0), face=0.075,
  ),
  "10_pivot_kick": dict(
    note="support leg pivots the body (yaw) while the leg swings across",
    keys=[
      (0.0, leg(), {}, (0, 0, 0, 0)),
      (0.35, leg(Hip_Pitch=0.5, Knee_Pitch=0.6, Hip_Roll=-0.2), {}, (0, 0, 0, -0.45)),
      (0.55, leg(Hip_Pitch=-0.4, Knee_Pitch=-0.4, Hip_Roll=0.35, Hip_Yaw=-0.5), {}, (0, 0, 0, 0.25)),
      (0.8, leg(Hip_Pitch=-0.5, Knee_Pitch=-0.3, Hip_Roll=0.38), {}, (0, 0, 0, 0.45)),
      (1.3, leg(), {}, (0, 0, 0, 0.45)),
    ],
    contact=2, dir=(0.707, 0.707), face=0.05,
  ),
  "11_hop_kick": dict(
    note="both feet leave the ground at contact (risky; v58 did this 28 % of kicks)",
    keys=[
      (0.0, leg(), {}, (0, 0, 0, 0)),
      (0.3, leg(Hip_Pitch=0.6, Knee_Pitch=0.8), {"Knee_Pitch": -0.2}, (0, 0, -0.03, 0)),
      (0.48, leg(Hip_Pitch=-0.5, Knee_Pitch=-0.6), {"Knee_Pitch": 0.5, "Hip_Pitch": -0.2}, (0.06, 0, 0.05, 0)),
      (0.7, leg(Hip_Pitch=-0.7, Knee_Pitch=-0.4), {}, (0.1, 0, 0.0, 0)),
      (1.2, leg(), {}, (0.1, 0, 0, 0)),
    ],
    contact=2, dir=(1.0, 0.0), face=0.075,
  ),
}


def build_model() -> tuple[mujoco.MjModel, dict]:
  spec = mujoco.MjSpec.from_file(str(XML))
  wb = spec.worldbody
  wb.add_light(pos=[0, 0, 3], dir=[0, 0, -1], diffuse=[0.8, 0.8, 0.8])
  wb.add_geom(type=mujoco.mjtGeom.mjGEOM_PLANE, size=[6, 6, 0.1], rgba=[0.35, 0.55, 0.35, 1], friction=[1.0, 0.005, 0.0001])
  anchor = wb.add_body(name="anchor", mocap=True, pos=[0, 0, 1.0])
  anchor.add_geom(type=mujoco.mjtGeom.mjGEOM_SPHERE, size=[0.005], contype=0, conaffinity=0, rgba=[0, 0, 0, 0])
  ball = wb.add_body(name="ball", pos=[1.0, 0, BALL_R])
  ball.add_freejoint(name="ball_free")
  ball.add_geom(
    type=mujoco.mjtGeom.mjGEOM_SPHERE, size=[BALL_R], mass=BALL_M, rgba=[0.95, 0.95, 0.95, 1],
    friction=[0.5, 0.005, 0.0001], solref=[0.05, 0.15],
  )  # fmt: skip
  eq = spec.add_equality(type=mujoco.mjtEq.mjEQ_WELD, name1="Trunk", name2="anchor", objtype=mujoco.mjtObj.mjOBJ_BODY)
  eq.solref = [0.005, 1.0]
  joints = {}
  for side in ("Left", "Right"):
    for j, eff in EFFORT.items():
      name = f"{side}_{j}"
      a = spec.add_actuator(name=f"act_{name}", target=name, trntype=mujoco.mjtTrn.mjTRN_JOINT)
      a.set_to_position(kp=250.0, kv=6.0)
      a.forcerange = [-eff, eff]
      a.forcelimited = True
  for name, val in ARMS.items():
    a = spec.add_actuator(name=f"act_{name}", target=name, trntype=mujoco.mjtTrn.mjTRN_JOINT)
    a.set_to_position(kp=40.0, kv=2.0)
  m = spec.compile()
  m.opt.timestep = DT
  for i in range(m.nu):
    joints[m.actuator(i).name[4:]] = i
  return m, joints


def lerp_keys(keys, t):
  for (t0, r0, l0, a0), (t1, r1, l1, a1) in zip(keys[:-1], keys[1:]):
    if t <= t1:
      s = (t - t0) / max(t1 - t0, 1e-6)
      s = s * s * (3 - 2 * s)  # smoothstep
      r = {k: r0[k] + s * (r1[k] - r0[k]) for k in r0}
      lk = set(l0) | set(l1)
      lft = {k: l0.get(k, 0.0) + s * (l1.get(k, 0.0) - l0.get(k, 0.0)) for k in lk}
      a = tuple(a0[i] + s * (a1[i] - a0[i]) for i in range(4))
      return r, lft, a
  _, r, lft, a = keys[-1]
  return r, lft, a


def set_ctrl(m, d, joints, r, lft):
  for j in EFFORT:
    d.ctrl[joints[f"Right_{j}"]] = r[j]
    d.ctrl[joints[f"Left_{j}"]] = DEFAULT[j] + lft.get(j, 0.0)
  for name, val in ARMS.items():
    d.ctrl[joints[name]] = val


def anchor_pose(base_z, a):
  dx, dy, dz, yaw = a
  quat = [math.cos(yaw / 2), 0, 0, math.sin(yaw / 2)]
  return np.array([dx, dy, base_z + dz]), np.array(quat)


def qpos_for_pose(m, r, lft, z, a):
  """Kinematic qpos for a pose (for placing the ball at the contact pose)."""
  d = mujoco.MjData(m)
  pos, quat = anchor_pose(z, a)
  jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "floating_base_joint")
  adr = m.jnt_qposadr[jid]
  d.qpos[adr : adr + 3] = pos
  d.qpos[adr + 3 : adr + 7] = quat
  for side, vals in (("Right", r), ("Left", {k: DEFAULT[k] + lft.get(k, 0.0) for k in DEFAULT})):
    for j in EFFORT:
      jj = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, f"{side}_{j}")
      d.qpos[m.jnt_qposadr[jj]] = vals[j]
  mujoco.mj_kinematics(m, d)
  return d


def standing_z(m) -> float:
  d = qpos_for_pose(m, leg(), {}, 1.0, (0, 0, 0, 0))
  sid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "left_foot_sole")
  return 1.0 - (d.site_xpos[sid][2] - 0.03)  # sole site sits 3 cm above the sole


def dry_run(m, joints, keys, z0, sid):
  """Run the motion with the ball out of the way; foot sole-site path."""
  d = mujoco.MjData(m)
  r0, l0, a0 = lerp_keys(keys, 0.0)
  d.qpos[:] = qpos_for_pose(m, r0, l0, z0, a0).qpos
  bj = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "ball_free")
  badr = m.jnt_qposadr[bj]
  d.qpos[badr : badr + 3] = [5.0, 5.0, BALL_R]
  d.qpos[badr + 3 : badr + 7] = [1, 0, 0, 0]
  mid = m.body("anchor").mocapid[0]
  lsid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "left_foot_sole")
  out = []
  prev = None
  T = keys[-1][0]
  for _ in range(150):
    set_ctrl(m, d, joints, r0, l0)
    d.mocap_pos[mid], d.mocap_quat[mid] = anchor_pose(z0, a0)
    mujoco.mj_step(m, d)
  for k in range(int(T / DT)):
    t = k * DT
    r, lft, a = lerp_keys(keys, t)
    set_ctrl(m, d, joints, r, lft)
    d.mocap_pos[mid], d.mocap_quat[mid] = anchor_pose(z0, a)
    mujoco.mj_step(m, d)
    pos = d.site_xpos[sid].copy()
    if prev is not None and k % 5 == 0:
      out.append((t, pos, (pos - prev) / DT, d.site_xpos[lsid].copy()))
    prev = pos
  return out


def run_style(name: str, cfg: dict, m, joints, out: Path) -> str:
  d = mujoco.MjData(m)
  z0 = standing_z(m) + 0.003
  keys = cfg["keys"]
  sid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "right_foot_sole")
  dvec = np.array([*cfg["dir"], 0.0])
  dvec /= np.linalg.norm(dvec)
  # Pass 1 (no ball in reach): where does the foot actually go? Pick the step
  # where the sole site moves fastest along the kick direction while low
  # enough to meet a ball (site below 0.16 m); place the ball just ahead of it.
  path = dry_run(m, joints, keys, z0, sid)
  cands = []
  for idx, (t, pos, vel, _) in enumerate(path):
    along = float(vel @ dvec)
    # sole at ball height (site 3 cm above the sole) and moving mostly along
    # the kick direction, not down onto the ball
    low = 0.02 <= pos[2] <= 0.11
    flat = abs(vel[2]) < 0.6 * max(along, 1e-6)
    if low and flat and along > 0.3:
      cands.append((along, idx, pos[:2] + dvec[:2] * (BALL_R + 0.6 * cfg["face"])))
  cands.sort(key=lambda c: -c[0])
  ball_xy = None
  for along, idx, xy in cands:
    # the foot must not touch the ball before the strike (backswing, turning)
    early = [p for (t, p, v, _) in path[: max(0, idx - 4)]]
    clear = all(np.linalg.norm(p[:2] - xy) > BALL_R + 0.09 or p[2] > 0.22 for p in early)
    # and clear of the support (left) foot over the whole motion
    clear = clear and all(np.linalg.norm(lp[:2] - xy) > BALL_R + 0.13 for (t, p, v, lp) in path)
    if clear:
      ball_xy = xy
      break
  if ball_xy is None:
    print(f"  ({name}: no clear contact point; using the fastest low point)")
    ball_xy = cands[0][2] if cands else path[len(path) // 2][1][:2] + dvec[:2] * (BALL_R + cfg["face"])
  # initial state
  r0, l0, a0 = lerp_keys(keys, 0.0)
  init = qpos_for_pose(m, r0, l0, z0, a0)
  d.qpos[:] = init.qpos
  bj = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "ball_free")
  badr = m.jnt_qposadr[bj]
  d.qpos[badr : badr + 3] = [ball_xy[0], ball_xy[1], BALL_R]
  d.qpos[badr + 3 : badr + 7] = [1, 0, 0, 0]
  mid = m.body("anchor").mocapid[0]
  pos, quat = anchor_pose(z0, a0)
  d.mocap_pos[mid], d.mocap_quat[mid] = pos, quat
  set_ctrl(m, d, joints, r0, l0)
  mujoco.mj_forward(m, d)
  # settle 0.3 s
  for _ in range(150):
    mujoco.mj_step(m, d)
  renderer = mujoco.Renderer(m, 360, 480)
  cam = mujoco.MjvCamera()
  cam.lookat[:] = [0.25, -0.05, 0.25]
  cam.distance, cam.azimuth, cam.elevation = 2.0, 145.0, -22.0
  opt = mujoco.MjvOption()
  frames, peak, vdir, t_hit = [], 0.0, None, None
  T = keys[-1][0] + 1.2
  steps_per_frame = int(1 / (FPS * DT))
  for k in range(int(T * FPS)):
    t = k / FPS
    for _ in range(steps_per_frame):
      r, lft, a = lerp_keys(keys, t)
      set_ctrl(m, d, joints, r, lft)
      pos, quat = anchor_pose(z0, a)
      d.mocap_pos[mid], d.mocap_quat[mid] = pos, quat
      mujoco.mj_step(m, d)
    bv = d.qvel[m.jnt_dofadr[bj] : m.jnt_dofadr[bj] + 3]
    sp = float(np.linalg.norm(bv))
    # measure only the first strike: 0.15 s after the ball first moves
    if t_hit is None and sp > 1.0:
      t_hit = t
    if t_hit is not None and t - t_hit <= 0.15 and sp > peak:
      peak, vdir = sp, bv.copy()
    renderer.update_scene(d, cam, opt)
    img = Image.fromarray(renderer.render())
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 480, 44], fill=(0, 0, 0))
    draw.text((6, 4), name.replace("_", " "), fill=(255, 255, 0))
    draw.text((6, 22), cfg["note"][:78], fill=(255, 255, 255))
    if peak > 0.3 and vdir is not None:
      ang = math.degrees(math.atan2(vdir[1], vdir[0]))
      elev = math.degrees(math.atan2(vdir[2], math.hypot(vdir[0], vdir[1])))
      draw.text((6, 340), f"ball peak {peak:.2f} m/s, heading {ang:+.0f} deg, launch {elev:+.0f} deg", fill=(255, 255, 255))
    frames.append(np.asarray(img))
  renderer.close()
  path = out / f"{name}.mp4"
  imageio.mimsave(path, frames, fps=FPS, macro_block_size=1)
  ang = math.degrees(math.atan2(vdir[1], vdir[0])) if vdir is not None else float("nan")
  elev = math.degrees(math.atan2(vdir[2], math.hypot(vdir[0], vdir[1]))) if vdir is not None else float("nan")
  return f"GALLERY {name:16s} ball peak {peak:5.2f} m/s, heading {ang:+5.0f} deg (target {math.degrees(math.atan2(cfg['dir'][1], cfg['dir'][0])):+4.0f}), launch {elev:+4.0f} deg -> {path.name}"


def main() -> None:
  out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "kick_style_gallery"
  out.mkdir(parents=True, exist_ok=True)
  names = sys.argv[2:] or list(STYLES)
  m, joints = build_model()
  for n in names:
    print(run_style(n, STYLES[n], m, joints, out), flush=True)


if __name__ == "__main__":
  main()

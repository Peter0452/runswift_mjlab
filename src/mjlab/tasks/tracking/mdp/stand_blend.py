"""Blend the last kick frame into the AMP stand, and check that path.

Joint angles are mixed with a smoothstep. Forward kinematics of those angles
supplies the body positions, so the joint command and the body command are the
same pose. The blend is kept only when the feet stay supported, the mass stays
between the feet, joint speed stays inside the motors, and a PD replay of the
same targets does not fall.
"""

from __future__ import annotations

from dataclasses import dataclass

import mujoco
import numpy as np
import torch

from mjlab.asset_zoo.robots.booster_k1.k1_constants import (
  ARMATURE_ANKLE,
  ARMATURE_ARM,
  ARMATURE_HEAD,
  ARMATURE_HIP_PITCH,
  ARMATURE_HIP_ROLL,
  ARMATURE_HIP_YAW,
  ARMATURE_KNEE,
  DAMPING_ANKLE,
  DAMPING_ARM,
  DAMPING_HEAD,
  DAMPING_HIP,
  DAMPING_KNEE,
  STIFFNESS_ANKLE,
  STIFFNESS_ARM,
  STIFFNESS_HEAD,
  STIFFNESS_HIP,
  STIFFNESS_KNEE,
  get_spec,
)
from mjlab.asset_zoo.robots.booster_k1.k1_whirlwind_constants import (
  ACTUATOR_E4310,
  ACTUATOR_E4315,
  ACTUATOR_E6408,
  ACTUATOR_E6416,
  ACTUATOR_HT4438,
  ACTUATOR_R14,
  HOME_KEYFRAME,
)
from mjlab.utils.lab_api.math import axis_angle_from_quat, quat_inv, quat_mul, yaw_quat

# Policy rate. One second of blend is 50 steps.
CONTROL_DT = 0.02
PHYSICS_DT = 0.005
# Shortest blend to try, then slower ones if a clip is not supported.
BLEND_STEP_CHOICES = (50, 75, 100)
SOLE_CLEARANCE = 0.01
# Foot-link origin sits about this far above the sole when the foot is flat.
SOLE_OFFSET = 0.038


@dataclass
class StandBlendCache:
  """Baked blend in the motion frame. ``steps`` is the last sample index."""

  steps: int
  joint_pos: torch.Tensor
  joint_vel: torch.Tensor
  body_pos: torch.Tensor
  body_quat: torch.Tensor
  body_lin_vel: torch.Tensor
  body_ang_vel: torch.Tensor
  report: StandBlendReport


@dataclass
class StandBlendReport:
  ok: bool
  steps: int
  min_sole_z: float
  max_stance_rise: float
  max_com_offset: float
  max_speed_ratio: float
  max_self_contacts: int
  pd_min_trunk_z: float
  pd_max_tilt: float
  messages: list[str]


def smoothstep(s: torch.Tensor | float) -> torch.Tensor | float:
  """Zero slope at 0 and at 1."""
  return s * s * (3.0 - 2.0 * s)


def quat_slerp_batch(
  q1: torch.Tensor, q2: torch.Tensor, tau: torch.Tensor
) -> torch.Tensor:
  """Slerp quaternions. ``tau`` has shape ``q1.shape[:-1]``."""
  tau_b = tau.unsqueeze(-1)
  dot = (q1 * q2).sum(dim=-1, keepdim=True)
  q2 = torch.where(dot < 0.0, -q2, q2)
  dot = dot.abs().clamp(max=1.0)
  angle = torch.acos(dot)
  sin_angle = torch.sin(angle).clamp_min(1.0e-6)
  mixed = (
    torch.sin((1.0 - tau_b) * angle) * q1 + torch.sin(tau_b * angle) * q2
  ) / sin_angle
  mixed = torch.where(angle < 1.0e-4, q1, mixed)
  return mixed / mixed.norm(dim=-1, keepdim=True).clamp_min(1.0e-8)


def motor_limits(name: str) -> tuple[float, float, float, float]:
  """Stiffness, damping, peak torque, and peak speed for one joint."""
  if name.endswith("Hip_Pitch"):
    motor = ACTUATOR_E6408
    return STIFFNESS_HIP, DAMPING_HIP, motor.effort_limit, motor.velocity_limit
  if name.endswith("Hip_Roll"):
    motor = ACTUATOR_E4315
    return STIFFNESS_HIP, DAMPING_HIP, motor.effort_limit, motor.velocity_limit
  if name.endswith("Hip_Yaw"):
    motor = ACTUATOR_E4310
    return STIFFNESS_HIP, DAMPING_HIP, motor.effort_limit, motor.velocity_limit
  if name.endswith("Knee_Pitch"):
    motor = ACTUATOR_E6416
    return STIFFNESS_KNEE, DAMPING_KNEE, motor.effort_limit, motor.velocity_limit
  if name.endswith("Ankle_Pitch") or name.endswith("Ankle_Roll"):
    return (
      STIFFNESS_ANKLE,
      DAMPING_ANKLE,
      ACTUATOR_E4310.effort_limit,
      ACTUATOR_E4310.velocity_limit,
    )
  if "Shoulder" in name or "Elbow" in name:
    return (
      STIFFNESS_ARM,
      DAMPING_ARM,
      ACTUATOR_R14.effort_limit,
      ACTUATOR_R14.velocity_limit,
    )
  if name.startswith("Head"):
    return (
      STIFFNESS_HEAD,
      DAMPING_HEAD,
      ACTUATOR_HT4438.effort_limit,
      ACTUATOR_HT4438.velocity_limit,
    )
  raise KeyError(f"No motor limits for joint {name}")


def build_stand_blend(
  motion_file: str,
  body_names: tuple[str, ...],
  *,
  stand_height: float = 0.5125,
  device: str = "cpu",
) -> StandBlendCache:
  """Build the longest-needed blend that passes the support and PD checks."""
  data = np.load(motion_file, allow_pickle=True)
  joint_names = [str(name) for name in data["joint_names"]]
  file_bodies = [str(name) for name in data["body_names"]]
  missing = [name for name in body_names if name not in file_bodies]
  if missing:
    raise RuntimeError(f"Kick motion is missing bodies: {missing}")
  home = np.array(
    [HOME_KEYFRAME.joint_pos.get(name, 0.0) for name in joint_names],
    dtype=np.float64,
  )
  spec = get_spec()
  model = spec.compile()
  mj_data = mujoco.MjData(model)
  messages: list[str] = []
  chosen: StandBlendCache | None = None
  for steps in BLEND_STEP_CHOICES:
    cache, report = _build_one(
      data,
      model,
      mj_data,
      joint_names,
      file_bodies,
      body_names,
      home,
      steps,
      stand_height,
    )
    messages.extend(report.messages)
    if report.ok:
      chosen = cache
      break
  if chosen is None:
    detail = "\n".join(messages)
    raise RuntimeError(f"Stand blend failed the support checks.\n{detail}")
  for line in chosen.report.messages:
    print(line)
  return _cache_to_device(chosen, device)


def _cache_to_device(cache: StandBlendCache, device: str) -> StandBlendCache:
  def move(value: torch.Tensor) -> torch.Tensor:
    return value.to(device=device)

  return StandBlendCache(
    steps=cache.steps,
    joint_pos=move(cache.joint_pos),
    joint_vel=move(cache.joint_vel),
    body_pos=move(cache.body_pos),
    body_quat=move(cache.body_quat),
    body_lin_vel=move(cache.body_lin_vel),
    body_ang_vel=move(cache.body_ang_vel),
    report=cache.report,
  )


def _build_one(
  data: np.lib.npyio.NpzFile,
  model: mujoco.MjModel,
  mj_data: mujoco.MjData,
  joint_names: list[str],
  file_bodies: list[str],
  body_names: tuple[str, ...],
  home: np.ndarray,
  steps: int,
  stand_height: float,
) -> tuple[StandBlendCache, StandBlendReport]:
  joint_pos = np.asarray(data["joint_pos"], dtype=np.float64)
  body_pos = np.asarray(data["body_pos_w"], dtype=np.float64)
  body_quat = np.asarray(data["body_quat_w"], dtype=np.float64)
  ends = np.asarray(data["clip_ends"], dtype=np.int64)
  names = [str(name) for name in data["clip_names"]]
  trunk_col = file_bodies.index("Trunk")
  qadr = np.array(
    [model.joint(name).qposadr[0] for name in joint_names], dtype=np.int32
  )
  n_clips = len(ends)
  n_samples = steps + 1
  n_bodies = len(body_names)
  body_ids = np.array([model.body(name).id for name in body_names], dtype=np.int32)
  joints = np.zeros((n_clips, n_samples, len(joint_names)), dtype=np.float32)
  world_pos = np.zeros((n_clips, n_samples, n_bodies, 3), dtype=np.float32)
  world_quat = np.zeros((n_clips, n_samples, n_bodies, 4), dtype=np.float32)
  solved_pos = np.zeros((n_clips, n_samples, 3), dtype=np.float64)
  solved_quat = np.zeros((n_clips, n_samples, 4), dtype=np.float64)
  min_sole = np.inf
  max_rise = 0.0
  max_com = 0.0
  max_ratio = 0.0
  max_self = 0
  speed_limits = np.array(
    [motor_limits(name)[3] for name in joint_names], dtype=np.float64
  )
  messages = [f"[INFO] Stand blend {steps} steps ({steps * CONTROL_DT:.2f} s)"]
  ok = True
  for clip, end in enumerate(ends):
    frame = int(end) - 1
    q0 = joint_pos[frame]
    root = body_pos[frame, trunk_col].copy()
    root_quat = body_quat[frame, trunk_col].copy()
    upright = yaw_quat(torch.tensor(root_quat, dtype=torch.float32).unsqueeze(0))
    upright_np = upright[0].numpy()
    sole_start: float | None = None
    clip_self_base = 0
    for sample in range(n_samples):
      alpha = float(smoothstep(sample / steps))
      q = (1.0 - alpha) * q0 + alpha * home
      joints[clip, sample] = q
      placed = (1.0 - alpha) * root + alpha * np.array(
        [root[0], root[1], stand_height]
      )
      placed_quat = _slerp_np(root_quat, upright_np, alpha)
      _set_pose(mj_data, model, qadr, placed, placed_quat, q)
      mujoco.mj_fwdPosition(model, mj_data)
      # The mixed trunk height can push a sole through the floor. Shift the
      # whole pose so the lower sole sits on the ground.
      placed = placed.copy()
      placed[2] -= min(_sole_z(model, mj_data))
      _set_pose(mj_data, model, qadr, placed, placed_quat, q)
      mujoco.mj_fwdPosition(model, mj_data)
      world_pos[clip, sample] = mj_data.xpos[body_ids]
      world_quat[clip, sample] = mj_data.xquat[body_ids]
      solved_pos[clip, sample] = mj_data.xpos[model.body(name="Trunk").id]
      solved_quat[clip, sample] = mj_data.xquat[model.body(name="Trunk").id]
      left_z, right_z = _sole_z(model, mj_data)
      sole = min(left_z, right_z)
      min_sole = min(min_sole, sole)
      if sample == 0:
        sole_start = sole
        planted_is_left = left_z <= right_z
        clip_self_base = _self_contacts(mj_data, model)
      assert sole_start is not None
      # The foot that starts lower is the planted one. It has to stay down.
      planted = left_z if planted_is_left else right_z
      rise = planted - sole_start
      max_rise = max(max_rise, rise)
      com = _com_offset(model, mj_data)
      max_com = max(max_com, com)
      self_hits = _self_contacts(mj_data, model)
      max_self = max(max_self, self_hits)
      if sole < -0.005 or rise > 0.03 or com > 0.12 or self_hits > clip_self_base:
        ok = False
    speed = np.max(np.abs(np.diff(joints[clip], axis=0)) / CONTROL_DT, axis=0)
    ratio = float(np.max(speed / speed_limits))
    max_ratio = max(max_ratio, ratio)
    if ratio > 1.0:
      ok = False
      messages.append(f"  {names[clip]}: joint speed {ratio:.2f} of the motor limit")
    limits = _joint_ranges(model, joint_names)
    if np.any(joints[clip] < limits[:, 0] - 1.0e-4) or np.any(
      joints[clip] > limits[:, 1] + 1.0e-4
    ):
      ok = False
      messages.append(f"  {names[clip]}: joint outside its range")
  joint_vel = np.gradient(joints, CONTROL_DT, axis=1).astype(np.float32)
  joint_vel[:, 0] = 0.0
  joint_vel[:, -1] = 0.0
  lin_vel = np.gradient(world_pos, CONTROL_DT, axis=1).astype(np.float32)
  lin_vel[:, 0] = 0.0
  lin_vel[:, -1] = 0.0
  ang_vel = _angular_velocity(world_quat, CONTROL_DT)
  pd_min, pd_tilt, pd_messages = _pd_replay(
    joint_names, joints, solved_pos, solved_quat, names
  )
  messages.extend(pd_messages)
  if pd_min < 0.45 or pd_tilt > 0.8:
    ok = False
  report = StandBlendReport(
    ok=ok,
    steps=steps,
    min_sole_z=float(min_sole),
    max_stance_rise=float(max_rise),
    max_com_offset=float(max_com),
    max_speed_ratio=float(max_ratio),
    max_self_contacts=int(max_self),
    pd_min_trunk_z=pd_min,
    pd_max_tilt=pd_tilt,
    messages=messages,
  )
  if ok:
    report.messages.append(
      "  "
      f"sole {report.min_sole_z:.3f} m, foot rise {report.max_stance_rise:.3f} m, "
      f"com {report.max_com_offset:.3f} m, speed {report.max_speed_ratio:.2f}, "
      f"pd trunk {report.pd_min_trunk_z:.3f} m, tilt {report.pd_max_tilt:.2f} rad"
    )
  cache = StandBlendCache(
    steps=steps,
    joint_pos=torch.tensor(joints),
    joint_vel=torch.tensor(joint_vel),
    body_pos=torch.tensor(world_pos),
    body_quat=torch.tensor(world_quat),
    body_lin_vel=torch.tensor(lin_vel),
    body_ang_vel=ang_vel,
    report=report,
  )
  return cache, report


def _slerp_np(q1: np.ndarray, q2: np.ndarray, tau: float) -> np.ndarray:
  mixed = quat_slerp_batch(
    torch.tensor(q1, dtype=torch.float32),
    torch.tensor(q2, dtype=torch.float32),
    torch.tensor(tau, dtype=torch.float32),
  )
  return mixed.numpy().astype(np.float64)


def _set_pose(
  data: mujoco.MjData,
  model: mujoco.MjModel,
  qadr: np.ndarray,
  root_pos: np.ndarray,
  root_quat: np.ndarray,
  joints: np.ndarray,
) -> None:
  data.qpos[:] = 0.0
  data.qvel[:] = 0.0
  free = int(np.where(model.jnt_type == mujoco.mjtJoint.mjJNT_FREE)[0][0])
  adr = int(model.jnt_qposadr[free])
  data.qpos[adr : adr + 3] = root_pos
  data.qpos[adr + 3 : adr + 7] = root_quat
  data.qpos[qadr] = joints


def _sole_z(model: mujoco.MjModel, data: mujoco.MjData) -> tuple[float, float]:
  return _foot_sole(model, data, "left_foot"), _foot_sole(model, data, "right_foot")


def _foot_sole(model: mujoco.MjModel, data: mujoco.MjData, prefix: str) -> float:
  """Lowest sole capsule. The foot box is a volume stand-in and is ignored."""
  lowest = np.inf
  for geom_id in range(model.ngeom):
    name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, geom_id) or ""
    if not name.startswith(prefix):
      continue
    if model.geom_type[geom_id] != mujoco.mjtGeom.mjGEOM_CAPSULE:
      continue
    center = data.geom_xpos[geom_id]
    rotation = data.geom_xmat[geom_id].reshape(3, 3)
    size = model.geom_size[geom_id]
    half = size[1] * abs(rotation[2, 2])
    lowest = min(lowest, center[2] - size[0] - half)
  if not np.isfinite(lowest):
    raise RuntimeError(f"No foot geoms named {prefix}*")
  return float(lowest)


def _com_offset(model: mujoco.MjModel, data: mujoco.MjData) -> float:
  trunk = model.body(name="Trunk").id
  left = data.xpos[model.body(name="left_foot_link").id, :2]
  right = data.xpos[model.body(name="right_foot_link").id, :2]
  com = data.subtree_com[trunk, :2]
  segment = right - left
  length = float(np.dot(segment, segment))
  if length < 1.0e-8:
    return float(np.linalg.norm(com - left))
  scale = float(np.clip(np.dot(com - left, segment) / length, 0.0, 1.0))
  closest = left + scale * segment
  return float(np.linalg.norm(com - closest))


def _self_contacts(data: mujoco.MjData, model: mujoco.MjModel) -> int:
  count = 0
  for index in range(data.ncon):
    contact = data.contact[index]
    first = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, int(contact.geom1)) or ""
    second = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, int(contact.geom2)) or ""
    if first == "floor" or second == "floor":
      continue
    count += 1
  return count


def _joint_ranges(model: mujoco.MjModel, joint_names: list[str]) -> np.ndarray:
  ranges = np.zeros((len(joint_names), 2), dtype=np.float64)
  for index, name in enumerate(joint_names):
    joint_id = model.joint(name).id
    if model.jnt_limited[joint_id]:
      ranges[index] = model.jnt_range[joint_id]
    else:
      ranges[index] = (-np.inf, np.inf)
  return ranges


def _pd_replay(
  joint_names: list[str],
  joints: np.ndarray,
  trunk_pos: np.ndarray,
  trunk_quat: np.ndarray,
  names: list[str],
) -> tuple[float, float, list[str]]:
  """Track the blend with the training PD gains. The root is free."""
  spec = get_spec()
  floor = spec.worldbody.add_geom()
  floor.name = "floor"
  floor.type = mujoco.mjtGeom.mjGEOM_PLANE
  floor.size[:] = [0.0, 0.0, 0.05]
  floor.friction[:] = [1.0, 0.005, 0.0001]
  model = spec.compile()
  model.opt.timestep = PHYSICS_DT
  data = mujoco.MjData(model)
  qadr = np.array(
    [model.joint(name).qposadr[0] for name in joint_names], dtype=np.int32
  )
  dofadr = np.array(
    [model.joint(name).dofadr[0] for name in joint_names], dtype=np.int32
  )
  gains = np.array([motor_limits(name)[:3] for name in joint_names], dtype=np.float64)
  kp, kd, effort = gains[:, 0], gains[:, 1], gains[:, 2]
  for index, name in enumerate(joint_names):
    model.dof_armature[dofadr[index]] = _armature(name)
  substeps = int(round(CONTROL_DT / PHYSICS_DT))
  worst_trunk = np.inf
  worst_tilt = 0.0
  messages: list[str] = []
  trunk_id = model.body(name="Trunk").id
  # Score the blend itself. Open-loop PD is not a balance controller, so a
  # later drift of the finished pose is left to the policy.
  n_control = joints.shape[1]
  for clip in range(joints.shape[0]):
    root = trunk_pos[clip, 0].astype(np.float64)
    root_quat = trunk_quat[clip, 0].astype(np.float64)
    _set_pose(data, model, qadr, root, root_quat, joints[clip, 0])
    data.qvel[:] = 0.0
    mujoco.mj_forward(model, data)
    clip_trunk = np.inf
    clip_tilt = 0.0
    for sample in range(n_control):
      target_index = min(sample, joints.shape[1] - 1)
      target = joints[clip, target_index]
      for _ in range(substeps):
        q = data.qpos[qadr]
        qd = data.qvel[dofadr]
        torque = np.clip(kp * (target - q) - kd * qd, -effort, effort)
        data.qfrc_applied[:] = 0.0
        data.qfrc_applied[dofadr] = torque
        mujoco.mj_step(model, data)
      height = float(data.xpos[trunk_id, 2])
      tilt = _trunk_tilt(data.xmat[trunk_id])
      clip_trunk = min(clip_trunk, height)
      clip_tilt = max(clip_tilt, tilt)
    worst_trunk = min(worst_trunk, clip_trunk)
    worst_tilt = max(worst_tilt, clip_tilt)
    if clip_trunk < 0.45 or clip_tilt > 0.8:
      messages.append(
        f"  {names[clip]} pd: trunk {clip_trunk:.3f} m, tilt {clip_tilt:.2f} rad"
      )
  return float(worst_trunk), float(worst_tilt), messages


def _armature(name: str) -> float:
  if name.endswith("Hip_Pitch"):
    return ARMATURE_HIP_PITCH
  if name.endswith("Hip_Roll"):
    return ARMATURE_HIP_ROLL
  if name.endswith("Hip_Yaw"):
    return ARMATURE_HIP_YAW
  if name.endswith("Knee_Pitch"):
    return ARMATURE_KNEE
  if name.endswith("Ankle_Pitch") or name.endswith("Ankle_Roll"):
    return ARMATURE_ANKLE
  if "Shoulder" in name or "Elbow" in name:
    return ARMATURE_ARM
  if name.startswith("Head"):
    return ARMATURE_HEAD
  raise KeyError(name)


def _angular_velocity(quat: np.ndarray, dt: float) -> torch.Tensor:
  """Body angular velocity from wxyz quaternions. Shape ``(clip, time, body, 3)``."""
  q = torch.tensor(quat, dtype=torch.float32)
  relative = quat_mul(q[:, 1:], quat_inv(q[:, :-1]))
  omega = axis_angle_from_quat(relative.reshape(-1, 4)).reshape(
    relative.shape[0], relative.shape[1], relative.shape[2], 3
  )
  out = torch.zeros(q.shape[0], q.shape[1], q.shape[2], 3)
  out[:, 1:] = omega / dt
  return out


def _trunk_tilt(xmat: np.ndarray) -> float:
  """Angle between the trunk up-axis and the world up-axis."""
  up = xmat.reshape(3, 3)[:, 2]
  return float(np.arccos(np.clip(up[2], -1.0, 1.0)))

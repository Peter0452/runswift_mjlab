"""Build a BeyondMimic NPZ from the retargeted Booster K1 kick clips.

The tracker plays one frame per policy step. Clips are resampled from 30 Hz to
the tracking control rate (50 Hz) and stored in one file. ``clip_ends`` marks
where each kick stops so training samples a trajectory, then a frame inside it,
instead of walking from the end of one kick into the start of the next.

``10_04`` is a straight walk and is left out. Each right-foot clip is mirrored
across the sagittal plane and stored again, so training draws a left-foot and a
right-foot kick equally often. ``clip_z`` is a 3-way one-hot style for the kick
being tracked, and it is the same for a clip and its mirror:

- planted: ``10_01``, ``10_02``
- running: ``10_03``
- moving: ``10_05``, ``11_01``
"""

from __future__ import annotations

import pickle
from pathlib import Path

import mujoco
import numpy as np
import torch

from mjlab.asset_zoo.robots.booster_k1.k1_constants import get_k1_robot_cfg
from mjlab.entity import Entity
from mjlab.motion.motion_data import MotionFile
from mjlab.utils.lab_api.math import (
  axis_angle_from_quat,
  quat_conjugate,
  quat_mul,
)

TRACKING_FPS = 50.0
KICK_MOTION_DIR = (
  Path(__file__).resolve().parents[7] / "data" / "retargeted" / "k1" / "kick"
)
KICK_TRACKING_NPZ = KICK_MOTION_DIR / "tracking.npz"
# CMU 10_04 retargets to a straight walk, not a kick.
EXCLUDED_KICK_STEMS = frozenset({"10_04_stageii"})
# One-hot order. Planted kicks stay nearly in place, the running kick
# approaches fast and swings early, and the moving pair travels into the kick.
KICK_STYLES = ("planted", "running", "moving")
KICK_STYLE_BY_STEM = {
  "10_01_stageii": 0,
  "10_02_stageii": 0,
  "10_03_stageii": 1,
  "10_05_stageii": 2,
  "11_01_stageii": 2,
}


def _body_angular_velocity(quat_wxyz: torch.Tensor, dt: float) -> torch.Tensor:
  """World angular velocity (T, B, 3) from wxyz quaternions."""
  q_rel = quat_mul(quat_wxyz[2:], quat_conjugate(quat_wxyz[:-2]))
  omega = axis_angle_from_quat(q_rel.reshape(-1, 4)).reshape(
    q_rel.shape[0], q_rel.shape[1], 3
  )
  omega = omega / (2.0 * dt)
  return torch.cat([omega[:1], omega, omega[-1:]], dim=0)


def _clip_kinematics(
  model: mujoco.MjModel,
  data: mujoco.MjData,
  *,
  body_ids: np.ndarray,
  joint_qadr: np.ndarray,
  joint_pos: np.ndarray,
  joint_vel: np.ndarray,
  root_pos: np.ndarray,
  root_quat_wxyz: np.ndarray,
  dt: float,
) -> dict[str, np.ndarray]:
  num_frames = joint_pos.shape[0]
  num_bodies = len(body_ids)
  body_pos = np.zeros((num_frames, num_bodies, 3), dtype=np.float32)
  body_quat = np.zeros((num_frames, num_bodies, 4), dtype=np.float32)
  for frame in range(num_frames):
    data.qpos[:] = 0.0
    data.qpos[0:3] = root_pos[frame]
    data.qpos[3:7] = root_quat_wxyz[frame]
    data.qpos[joint_qadr] = joint_pos[frame]
    mujoco.mj_kinematics(model, data)
    body_pos[frame] = data.xpos[body_ids]
    body_quat[frame] = data.xquat[body_ids]

  pos_t = torch.from_numpy(body_pos)
  quat_t = torch.from_numpy(body_quat)
  body_lin_vel = torch.gradient(pos_t, spacing=dt, dim=0)[0]
  body_ang_vel = _body_angular_velocity(quat_t, dt)
  return {
    "joint_pos": joint_pos.astype(np.float32),
    "joint_vel": joint_vel.astype(np.float32),
    "body_pos_w": body_pos,
    "body_quat_w": body_quat,
    "body_lin_vel_w": body_lin_vel.numpy().astype(np.float32),
    "body_ang_vel_w": body_ang_vel.numpy().astype(np.float32),
  }


def _mirrored_name(name: str) -> str:
  """Swap a left/right body or joint name. Unpaired names stay put."""
  if name.startswith("Left"):
    return "Right" + name[4:]
  if name.startswith("left"):
    return "right" + name[4:]
  if name.startswith("Right"):
    return "Left" + name[5:]
  if name.startswith("right"):
    return "left" + name[5:]
  return name


def _mirror_joint_sign(name: str) -> float:
  """Roll and yaw flip under a left-right reflection. Pitch does not."""
  if name.endswith("_Roll") or name.endswith("_Yaw"):
    return -1.0
  return 1.0


def mirror_kick_state(
  joint_names: tuple[str, ...] | list[str],
  joint_pos: np.ndarray,
  joint_vel: np.ndarray,
  root_pos: np.ndarray,
  root_quat_wxyz: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
  """Reflect a kick through the sagittal plane.

  Verified against forward kinematics: roll and yaw joint angles flip sign,
  root y flips, and the root quaternion becomes ``(w, -x, y, -z)``.
  """
  names = list(joint_names)
  pair = [_mirrored_name(name) for name in names]
  index = [names.index(name) for name in pair]
  sign = np.array([_mirror_joint_sign(name) for name in names], dtype=np.float32)
  joint_pos_m = joint_pos[:, index] * sign
  joint_vel_m = joint_vel[:, index] * sign
  root_pos_m = root_pos.copy()
  root_pos_m[:, 1] *= -1.0
  root_quat_m = root_quat_wxyz.copy()
  root_quat_m[:, 1] *= -1.0
  root_quat_m[:, 3] *= -1.0
  return joint_pos_m, joint_vel_m, root_pos_m, root_quat_m


def style_one_hot(stem: str) -> np.ndarray:
  """Return the 3-D one-hot style for a kick clip stem."""
  try:
    index = KICK_STYLE_BY_STEM[stem]
  except KeyError as exc:
    raise KeyError(f"No kick style for clip {stem}") from exc
  style = np.zeros(len(KICK_STYLES), dtype=np.float32)
  style[index] = 1.0
  return style


def convert_kick_clips(
  src_dir: Path = KICK_MOTION_DIR,
  dst: Path = KICK_TRACKING_NPZ,
  fps: float = TRACKING_FPS,
) -> Path:
  """Resample every ``*.pkl`` in ``src_dir`` and write one tracking NPZ."""
  robot = Entity(get_k1_robot_cfg())
  model = robot.spec.compile()
  data = mujoco.MjData(model)
  body_ids = np.array(
    [
      mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, name)
      for name in robot.body_names
    ],
    dtype=np.int32,
  )
  if np.any(body_ids < 0):
    missing = [
      name
      for name, body_id in zip(robot.body_names, body_ids, strict=True)
      if body_id < 0
    ]
    raise RuntimeError(f"K1 model is missing bodies: {missing}")
  joint_qadr = np.array(
    [model.joint(name).qposadr[0] for name in robot.joint_names],
    dtype=np.int32,
  )

  clips = [
    path
    for path in sorted(src_dir.glob("*.pkl"))
    if path.stem not in EXCLUDED_KICK_STEMS
  ]
  if not clips:
    raise FileNotFoundError(f"No K1 kick pkls in {src_dir}")

  parts: list[dict[str, np.ndarray]] = []
  clip_ends: list[int] = []
  names: list[str] = []
  styles: list[np.ndarray] = []
  kick_foot: list[int] = []
  cursor = 0
  dt = 1.0 / fps
  for path in clips:
    with path.open("rb") as f:
      raw = pickle.load(f)
    source_names = [str(name) for name in raw["joint_names"]]
    prepared = MotionFile.load(path).prepare(simulation_dt=dt)
    src_index = {name: i for i, name in enumerate(source_names)}
    try:
      perm = [src_index[name] for name in robot.joint_names]
    except KeyError as exc:
      raise KeyError(
        f"{path.name} joint names {source_names} do not cover {robot.joint_names}"
      ) from exc
    perm_t = torch.tensor(perm, dtype=torch.long)
    joint_pos = prepared.joint_positions[:, perm_t].cpu().numpy()
    joint_vel = prepared.joint_velocities[:, perm_t].cpu().numpy()
    root_pos = prepared.root_pos.cpu().numpy()
    root_quat_xyzw = prepared.base_quat.cpu().numpy()
    root_quat_wxyz = root_quat_xyzw[:, [3, 0, 1, 2]]
    style = style_one_hot(path.stem)
    for foot, pos, vel, root, quat, name in (
      (0, joint_pos, joint_vel, root_pos, root_quat_wxyz, path.stem),
      (
        1,
        *mirror_kick_state(
          robot.joint_names, joint_pos, joint_vel, root_pos, root_quat_wxyz
        ),
        f"{path.stem}_left",
      ),
    ):
      parts.append(
        _clip_kinematics(
          model,
          data,
          body_ids=body_ids,
          joint_qadr=joint_qadr,
          joint_pos=pos,
          joint_vel=vel,
          root_pos=root,
          root_quat_wxyz=quat,
          dt=dt,
        )
      )
      cursor += parts[-1]["joint_pos"].shape[0]
      clip_ends.append(cursor)
      names.append(name)
      styles.append(style)
      kick_foot.append(foot)

  clip_z = np.stack(styles)
  stacked = {
    key: np.concatenate([part[key] for part in parts], axis=0) for key in parts[0]
  }
  dst.parent.mkdir(parents=True, exist_ok=True)
  np.savez(
    dst,
    fps=np.array([fps], dtype=np.float32),
    clip_ends=np.array(clip_ends, dtype=np.int64),
    clip_names=np.array(names),
    clip_z=clip_z,
    clip_z_names=np.array(KICK_STYLES),
    clip_kick_foot=np.array(kick_foot, dtype=np.int64),
    body_names=np.array(robot.body_names),
    joint_names=np.array(robot.joint_names),
    **stacked,
  )
  for name, style in zip(names, clip_z, strict=True):
    label = KICK_STYLES[int(np.argmax(style))]
    print(f"  {name}: {label} {style.astype(int).tolist()}")
  print(
    f"Wrote {stacked['joint_pos'].shape[0]} frames @ {fps:.0f} Hz "
    f"({len(names)} clips, {stacked['joint_pos'].shape[1]} DoF, "
    f"{stacked['body_pos_w'].shape[1]} bodies) to {dst}"
  )
  return dst


if __name__ == "__main__":
  convert_kick_clips()

"""Decaying action prior (DecAP) for position-controlled robots.

APEX's ``apex_position`` law adds a fading spring toward a reference pose.
K1's implicit position actuators take that spring as a position target:

    q_target = q_policy + β (q_imit - q)

β = gamma ** (step / k), with gamma = 0.99 and k = 100. β = 0 leaves the
policy target unchanged. Head joints stay on the scripted tracker.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import torch

from mjlab.asset_zoo.robots.booster_k1.k1_whirlwind_constants import K1_JOINT_ORDER
from mjlab.utils.lab_api.math import quat_mul

if TYPE_CHECKING:
  from mjlab.motion.motion_loader import MotionLoader


def _yaw_angle(quat: torch.Tensor) -> torch.Tensor:
  qw, qx, qy, qz = quat[:, 0], quat[:, 1], quat[:, 2], quat[:, 3]
  return torch.atan2(2.0 * (qw * qz + qx * qy), 1.0 - 2.0 * (qy * qy + qz * qz))


def _rotate_yaw(v: torch.Tensor, c: torch.Tensor, s_: torch.Tensor) -> torch.Tensor:
  out = v.clone()
  out[:, 0] = c * v[:, 0] - s_ * v[:, 1]
  out[:, 1] = s_ * v[:, 0] + c * v[:, 1]
  return out


def decap_factor(step: int, gamma: float = 0.99, k: float = 100.0) -> float:
  """Exponential DecAP scale in ``(0, 1]``."""
  if k <= 0.0:
    raise ValueError(f"decap k must be positive, got {k}")
  return float(math.pow(gamma, step / k))


_STAND_DEFAULTS = {
  "Left_Hip_Pitch": -0.2,
  "Left_Knee_Pitch": 0.4,
  "Left_Ankle_Pitch": -0.2,
  "Right_Hip_Pitch": -0.2,
  "Right_Knee_Pitch": 0.4,
  "Right_Ankle_Pitch": -0.2,
}


def _stance_frame(
  q_clip: torch.Tensor, lin_vel_b: torch.Tensor, action_names: list[str]
) -> int:
  """Pick the frame in the first 3/4 of a clip closest to a quiet standing pose."""
  horizon = max(1, (3 * int(q_clip.shape[0])) // 4)
  stand = torch.tensor(
    [_STAND_DEFAULTS.get(n, 0.0) for n in action_names],
    dtype=q_clip.dtype,
    device=q_clip.device,
  )
  leg_mask = torch.tensor(
    [
      any(k in n for k in ("Hip", "Knee", "Ankle"))
      for n in action_names
    ],
    dtype=torch.bool,
    device=q_clip.device,
  )
  if bool(leg_mask.any()):
    pose_err = (q_clip[:horizon, leg_mask] - stand[leg_mask]).norm(dim=-1)
  else:
    pose_err = (q_clip[:horizon] - stand).norm(dim=-1)
  speed = lin_vel_b[:horizon, :2].norm(dim=-1)
  return int((pose_err + 0.5 * speed).argmin().item())
# stay on the sampled command; mixed takes change direction, so the command
# has to follow the frame.
_MIXED_SPEED = 0.15
_MIXED_FWD = math.radians(45.0)
_MIXED_BACK = math.radians(135.0)


def clip_is_mixed(lin_vel_b: torch.Tensor) -> bool:
  """True when a clip walks forward, backward, and sideways, not one way."""
  vx = lin_vel_b[:, 0]
  vy = lin_vel_b[:, 1]
  moving = torch.hypot(vx, vy) > _MIXED_SPEED
  if int(moving.sum()) < 5:
    return True
  ang = torch.atan2(vy[moving], vx[moving]).abs()
  fwd = float((ang < _MIXED_FWD).float().mean())
  back = float((ang > _MIXED_BACK).float().mean())
  side = 1.0 - fwd - back
  return fwd < 0.7 or back > 0.25 or side > 0.25


def apply_clip_velocity_command(
  vel_command_b: torch.Tensor,
  reference: DecapReference,
  follow: torch.Tensor,
) -> None:
  """Write the playing frame's body velocity onto environments that follow it.

  ``follow`` is chosen when the command is sampled, with probability equal to
  the spring scale. Early on that is nearly every environment. As the scale
  falls, resamples land on the task's random command instead. Kick references
  have no body velocity, so this leaves them alone.
  """
  if reference.factor <= 0.0 or reference.body_vel is None:
    return
  tracked = reference.reference_command()
  if tracked is None:
    return
  vel, active = tracked
  use = follow & active
  if not bool(use.any()):
    return
  vel_command_b[use, :3] = vel[use]


def blend_position_target(
  policy_target: torch.Tensor,
  reference: torch.Tensor,
  joint_pos: torch.Tensor,
  factor: float,
  head_cols: torch.Tensor | None = None,
) -> torch.Tensor:
  """APEX ``apex_position`` blend. Head columns keep ``policy_target``."""
  if factor <= 0.0:
    return policy_target
  blended = policy_target + factor * (reference - joint_pos)
  if head_cols is not None and head_cols.numel() > 0:
    blended[:, head_cols] = policy_target[:, head_cols]
  return blended


class DecapReference:
  """Per-env playback of AMP clip joint positions, plus the decay scale."""

  def __init__(
    self,
    joint_pos: torch.Tensor,
    clip_starts: torch.Tensor,
    clip_lengths: torch.Tensor,
    weights: torch.Tensor,
    head_cols: torch.Tensor,
    num_envs: int,
    gamma: float = 0.99,
    k: float = 100.0,
    stop_at_end: bool = False,
    lead_lo: torch.Tensor | None = None,
    lead_hi: torch.Tensor | None = None,
    root_pos: torch.Tensor | None = None,
    root_quat: torch.Tensor | None = None,
    root_lin_vel: torch.Tensor | None = None,
    root_ang_vel: torch.Tensor | None = None,
    spawn_joint_pos: torch.Tensor | None = None,
    spawn_joint_vel: torch.Tensor | None = None,
    ball_pos: torch.Tensor | None = None,
    target_xy: torch.Tensor | None = None,
    body_vel: torch.Tensor | None = None,
    clip_mixed: torch.Tensor | None = None,
    stance_frame: torch.Tensor | None = None,
  ) -> None:
    if joint_pos.ndim != 2 or clip_starts.shape != clip_lengths.shape:
      raise ValueError("DecAP clip storage has an unexpected shape")
    if int(clip_lengths.min()) < 1:
      raise ValueError("DecAP clips must contain at least one frame")
    self.joint_pos = joint_pos
    self.clip_starts = clip_starts.long()
    self.clip_lengths = clip_lengths.long()
    self.weights = weights / weights.sum()
    self.head_cols = head_cols.long()
    self.gamma = float(gamma)
    self.k = float(k)
    self.device = joint_pos.device
    self.decay_steps = 0
    self.factor = decap_factor(0, self.gamma, self.k)
    self.stop_at_end = bool(stop_at_end)
    self.lead_lo = lead_lo
    self.lead_hi = lead_hi
    self.root_pos = root_pos
    self.root_quat = root_quat
    self.root_lin_vel = root_lin_vel
    self.root_ang_vel = root_ang_vel
    self.spawn_joint_pos = spawn_joint_pos
    self.spawn_joint_vel = spawn_joint_vel
    self.ball_pos = ball_pos
    self.target_xy = target_xy
    # Body-frame (vx, vy, wz) of every frame, and which clips change direction.
    self.body_vel = body_vel
    self.clip_mixed = clip_mixed
    self.stance_frame = stance_frame.long() if stance_frame is not None else None
    n = int(num_envs)
    self.clip_id = torch.zeros(n, dtype=torch.long, device=self.device)
    self.frame = torch.zeros(n, dtype=torch.long, device=self.device)
    self.targets = torch.zeros(n, joint_pos.shape[1], device=self.device)
    self.active = torch.ones(n, dtype=torch.bool, device=self.device)
    self.pending = torch.zeros(n, dtype=torch.bool, device=self.device)
    self.synced = torch.zeros(n, dtype=torch.bool, device=self.device)
    self.play_index = torch.zeros(n, dtype=torch.long, device=self.device)
    # World anchor captured when a take is armed, and the clip root there.
    self.anchor_xy = torch.zeros(n, 2, device=self.device)
    self.anchor_z = torch.zeros(n, device=self.device)
    self.anchor_yaw = torch.zeros(n, device=self.device)
    self.anchor_clip_xy = torch.zeros(n, 2, device=self.device)
    self.anchor_clip_z = torch.zeros(n, device=self.device)
    self.anchor_clip_yaw = torch.zeros(n, device=self.device)
    self.reset(slice(None))

  @classmethod
  def from_loader(
    cls,
    loader: MotionLoader,
    action_names: list[str],
    num_envs: int,
    gamma: float = 0.99,
    k: float = 100.0,
  ) -> DecapReference:
    """Stack the loader's clips in action-joint order."""
    if not loader.motion_data:
      raise ValueError("DecAP requires at least one AMP motion clip")
    missing = [name for name in action_names if name not in K1_JOINT_ORDER]
    if missing:
      raise ValueError(f"DecAP has no clip column for joints {missing}")
    cols = [K1_JOINT_ORDER.index(name) for name in action_names]
    width = loader.motion_data[0].joint_positions.shape[1]
    if width <= max(cols):
      raise ValueError(
        f"AMP clips have {width} joints, but the action layout needs column {max(cols)}"
      )

    pieces: list[torch.Tensor] = []
    vels: list[torch.Tensor] = []
    mixed: list[bool] = []
    stance: list[int] = []
    starts: list[int] = []
    lengths: list[int] = []
    cursor = 0
    for motion in loader.motion_data:
      q = motion.joint_positions
      if q.shape[1] != width:
        raise ValueError(
          f"DecAP clips disagree on joint count ({q.shape[1]} vs {width})"
        )
      q_act = q[:, cols]
      pieces.append(q_act)
      lin = motion.base_lin_velocities_local
      wz = motion.base_ang_velocities_local[:, 2:3]
      vels.append(torch.cat((lin[:, :2], wz), dim=-1))
      mixed.append(clip_is_mixed(lin))
      stance.append(_stance_frame(q_act, lin, action_names))
      starts.append(cursor)
      lengths.append(int(q.shape[0]))
      cursor += int(q.shape[0])

    device = pieces[0].device
    head_cols = torch.tensor(
      [i for i, name in enumerate(action_names) if name.startswith("Head_")],
      dtype=torch.long,
      device=device,
    )
    weights = torch.tensor(loader.motion_weights, dtype=torch.float32, device=device)
    if weights.shape[0] != len(pieces):
      raise ValueError(
        f"DecAP has {len(pieces)} clips but {weights.shape[0]} sampling weights"
      )
    return cls(
      joint_pos=torch.cat(pieces, dim=0),
      clip_starts=torch.tensor(starts, dtype=torch.long, device=device),
      clip_lengths=torch.tensor(lengths, dtype=torch.long, device=device),
      weights=weights,
      head_cols=head_cols,
      num_envs=num_envs,
      gamma=gamma,
      k=k,
      body_vel=torch.cat(vels, dim=0),
      clip_mixed=torch.tensor(mixed, dtype=torch.bool, device=device),
      stance_frame=torch.tensor(stance, dtype=torch.long, device=device),
    )

  def reference_command(self) -> tuple[torch.Tensor, torch.Tensor] | None:
    """Body-frame ``(vx, vy, wz)`` of the frame about to be played, and which
    envs are still inside a clip. ``None`` when this reference has no velocities.
    """
    if self.body_vel is None:
      return None
    idx = self.clip_starts[self.clip_id] + self.frame
    vel = self.body_vel[idx]
    return vel, self.active

  def set_decay_steps(self, steps: int) -> None:
    """Restore the schedule when resuming a run."""
    self.decay_steps = max(0, int(steps))
    self.factor = decap_factor(self.decay_steps, self.gamma, self.k)

  def reset(self, env_ids: torch.Tensor | slice | None) -> None:
    """Sample a new clip and phase for the given environments."""
    if isinstance(env_ids, torch.Tensor):
      ids = env_ids.to(device=self.device, dtype=torch.long)
      if ids.numel() == 0:
        return
      if bool(self.synced[ids].any()):
        keep = self.synced[ids]
        self.synced[ids] = False
        ids = ids[~keep]
        if ids.numel() == 0:
          return
      n = int(ids.numel())
      index: torch.Tensor | slice = ids
    else:
      if bool(self.synced.any()):
        keep = self.synced.clone()
        self.synced.zero_()
        ids = (~keep).nonzero(as_tuple=False).flatten()
        if ids.numel() == 0:
          return
        n = int(ids.numel())
        index = ids
      else:
        n = int(self.clip_id.shape[0])
        index = slice(None)
    if self.stop_at_end:
      self.arm(index if isinstance(index, torch.Tensor) else env_ids)
      return
    clip = torch.multinomial(self.weights, n, replacement=True)
    length = self.clip_lengths[clip]
    frame = (torch.rand(n, device=self.device) * length).long()
    self.clip_id[index] = clip
    self.frame[index] = frame
    self.active[index] = True
    self.pending[index] = False

  def sync_to_flat_index(
    self, env_ids: torch.Tensor, flat_idx: torch.Tensor
  ) -> None:
    """Align playback with a flat frame index into ``joint_pos``."""
    ids = env_ids.to(device=self.device, dtype=torch.long)
    if ids.numel() == 0:
      return
    flat = flat_idx.to(device=self.device, dtype=torch.long).clamp(
      0, int(self.joint_pos.shape[0]) - 1
    )
    if self.clip_starts.numel() > 1:
      clip = torch.searchsorted(self.clip_starts[1:].contiguous(), flat, right=True)
    else:
      clip = torch.zeros_like(flat)
    frame = (flat - self.clip_starts[clip]).clamp(min=0)
    frame = torch.minimum(frame, self.clip_lengths[clip] - 1)
    self.clip_id[ids] = clip
    self.frame[ids] = frame
    self.active[ids] = True
    self.pending[ids] = False
    self.synced[ids] = True
    self.refresh(ids)

  def sync_to_stance(self, env_ids: torch.Tensor) -> None:
    """Start playback at a quiet stance frame of a sampled clip."""
    ids = env_ids.to(device=self.device, dtype=torch.long)
    n = int(ids.numel())
    if n == 0:
      return
    clip = torch.multinomial(self.weights, n, replacement=True)
    if self.stance_frame is not None:
      frame = self.stance_frame[clip]
    else:
      frame = torch.zeros_like(clip)
    self.clip_id[ids] = clip
    self.frame[ids] = frame
    self.active[ids] = True
    self.pending[ids] = False
    self.synced[ids] = True
    self.refresh(ids)

  def refresh(self, env_ids: torch.Tensor | slice | None = None) -> None:
    """Load joint targets for the current frame of each environment."""
    if env_ids is None:
      self.play_index = self.clip_starts[self.clip_id] + self.frame
      self.targets = self.joint_pos[self.play_index]
      return
    ids = env_ids.to(device=self.device, dtype=torch.long)
    self.play_index[ids] = self.clip_starts[self.clip_id[ids]] + self.frame[ids]
    self.targets[ids] = self.joint_pos[self.play_index[ids]]

  def capture_anchor(
    self,
    env_ids: torch.Tensor,
    xy: torch.Tensor,
    z: torch.Tensor,
    yaw: torch.Tensor,
  ) -> None:
    """Remember where this take was placed, so later frames share that spot."""
    if self.root_pos is None or self.root_quat is None:
      return
    ids = env_ids.to(device=self.device, dtype=torch.long)
    frame = self.clip_starts[self.clip_id[ids]] + self.frame[ids]
    self.anchor_xy[ids] = xy
    self.anchor_z[ids] = z
    self.anchor_yaw[ids] = yaw
    self.anchor_clip_xy[ids] = self.root_pos[frame, :2]
    self.anchor_clip_z[ids] = self.root_pos[frame, 2]
    self.anchor_clip_yaw[ids] = _yaw_angle(self.root_quat[frame])

  def write_root(self, robot, env_ids: torch.Tensor | None = None) -> None:
    """Put the base on this frame of the retarget. The spring is joint-space,
    and the kick is not balanced with the base left behind."""
    if (
      self.factor <= 0.0
      or self.root_pos is None
      or self.root_quat is None
      or self.root_lin_vel is None
      or self.root_ang_vel is None
      or not bool(self.active.any())
    ):
      return
    if env_ids is None:
      ids = self.active.nonzero(as_tuple=False).flatten()
    else:
      ids = env_ids.to(device=self.device, dtype=torch.long)
      ids = ids[self.active[ids]]
    if len(ids) == 0:
      return
    idx = self.play_index[ids]
    dyaw = self.anchor_yaw[ids] - self.anchor_clip_yaw[ids]
    c, s_ = dyaw.cos(), dyaw.sin()
    delta = self.root_pos[idx, :2] - self.anchor_clip_xy[ids]
    pos = torch.empty(len(ids), 3, device=self.device)
    pos[:, 0] = self.anchor_xy[ids, 0] + c * delta[:, 0] - s_ * delta[:, 1]
    pos[:, 1] = self.anchor_xy[ids, 1] + s_ * delta[:, 0] + c * delta[:, 1]
    pos[:, 2] = self.anchor_z[ids] + (self.root_pos[idx, 2] - self.anchor_clip_z[ids])
    half = 0.5 * dyaw
    qz = torch.stack(
      (half.cos(), torch.zeros_like(half), torch.zeros_like(half), half.sin()), -1
    )
    quat = quat_mul(qz, self.root_quat[idx])
    lin = _rotate_yaw(self.root_lin_vel[idx], c, s_)
    ang = _rotate_yaw(self.root_ang_vel[idx], c, s_)
    # Fade the base puppet with β. At 1 the retarget carries the body through
    # the kick. At 0 the base is the policy's to keep upright.
    if self.factor < 1.0:
      adr = robot.data.indexing.free_joint_q_adr
      cur = robot.data.data.qpos[ids][:, adr]
      f = self.factor
      pos = (1.0 - f) * cur[:, 0:3] + f * pos
      mixed = (1.0 - f) * cur[:, 3:7] + f * quat
      mixed = mixed / mixed.norm(dim=-1, keepdim=True).clamp(min=1.0e-8)
      quat = mixed
      lin = f * lin
      ang = f * ang
    robot.write_root_state_to_sim(torch.cat((pos, quat, lin, ang), -1), env_ids=ids)

  def arm(self, env_ids: torch.Tensor | slice | None) -> None:
    """Start a kick take in its pre-strike window. The clip then plays to the end."""
    if self.lead_lo is None or self.lead_hi is None:
      raise RuntimeError("DecAP arm() requires a kick-clip lead window")
    if isinstance(env_ids, torch.Tensor):
      n = int(env_ids.numel())
      if n == 0:
        return
      index = env_ids.to(device=self.device, dtype=torch.long)
    else:
      n = int(self.clip_id.shape[0])
      index = slice(None)
    clip = torch.multinomial(self.weights, n, replacement=True)
    lo = self.lead_lo[clip]
    hi = self.lead_hi[clip]
    frame = lo + (torch.rand(n, device=self.device) * (hi - lo + 1).float()).long()
    frame = torch.minimum(frame, hi)
    self.clip_id[index] = clip
    self.frame[index] = frame
    self.active[index] = True
    self.pending[index] = False

  def advance(self) -> None:
    """Move one policy step along the clip and the exponential schedule."""
    self.decay_steps += 1
    self.factor = decap_factor(self.decay_steps, self.gamma, self.k)
    if self.stop_at_end:
      moving = self.active
      self.frame[moving] += 1
      done = moving & (self.frame >= self.clip_lengths[self.clip_id])
      if bool(done.any()):
        done_ids = done.nonzero(as_tuple=False).flatten()
        self.frame[done_ids] = self.clip_lengths[self.clip_id[done_ids]] - 1
        self.active[done_ids] = False
        self.pending[done_ids] = True
      return
    self.frame += 1
    done = self.frame >= self.clip_lengths[self.clip_id]
    if bool(done.any()):
      done_ids = done.nonzero(as_tuple=False).flatten()
      self.synced[done_ids] = False
      self.reset(done_ids)

  def blend(self, policy_target: torch.Tensor, joint_pos: torch.Tensor) -> torch.Tensor:
    if self.stop_at_end:
      # Grow law. The additive spring settles halfway between the policy and
      # the clip, and these kicks sit several action-scales from the default
      # pose, so a fresh policy never actually plays them. β = 1 holds the clip.
      blended = (1.0 - self.factor) * policy_target + self.factor * self.targets
      if self.head_cols.numel() > 0:
        blended[:, self.head_cols] = policy_target[:, self.head_cols]
      if not bool(self.active.all()):
        blended = torch.where(self.active.unsqueeze(-1), blended, policy_target)
      return blended
    return blend_position_target(
      policy_target, self.targets, joint_pos, self.factor, self.head_cols
    )


_LEAD_S = (0.15, 0.35)
_BALL_RADIUS = 0.08
_TARGET_DISTANCE = 5.0
_POLICY_DT = 0.02


def _kick_motion_dir():
  from pathlib import Path

  return Path(__file__).resolve().parents[6] / "data" / "retargeted" / "k1" / "kick"


def _strike_ball(
  body_pos: "torch.Tensor",
  body_vel: "torch.Tensor",
  foot: int,
) -> tuple[int, "torch.Tensor", "torch.Tensor"]:
  """Strike frame, ball xyz and target xy for one kicking foot."""
  speed = torch.linalg.norm(body_vel[:, foot, :2], dim=-1)
  strike = int(speed.argmax())
  vel = body_vel[strike, foot, :2]
  direction = vel / torch.linalg.norm(vel).clamp(min=1.0e-6)
  ball = torch.zeros(3)
  ball[:2] = body_pos[strike, foot, :2] + direction * _BALL_RADIUS
  ball[2] = _BALL_RADIUS
  target = ball[:2] + direction * _TARGET_DISTANCE
  return strike, ball, target


def _load_kick_clip(path, robot_names: list[str], dt: float):
  """Resample one CSV to the policy rate in ``robot_names`` order."""
  from mjlab.motion.motion_data import MotionFile
  from mjlab.tasks.tracking.config.k1.kick_motion import mirror_kick_state

  prepared = MotionFile.load(path).prepare(simulation_dt=dt)
  names = list(K1_JOINT_ORDER)
  src = {name: i for i, name in enumerate(names)}
  perm = [src[name] for name in robot_names]
  joint_pos = prepared.joint_positions[:, perm].cpu()
  joint_vel = prepared.joint_velocities[:, perm].cpu()
  root_pos = prepared.root_pos.cpu()
  xyzw = prepared.base_quat.cpu()
  root_quat = xyzw[:, [3, 0, 1, 2]]
  lin = prepared.base_lin_velocities_mixed.cpu()
  ang = prepared.base_ang_velocities_mixed.cpu()
  mirrored = mirror_kick_state(
    robot_names,
    joint_pos.numpy(),
    joint_vel.numpy(),
    root_pos.numpy(),
    root_quat.numpy(),
  )
  joint_pos_m, joint_vel_m, root_pos_m, root_quat_m = (
    torch.from_numpy(part) for part in mirrored
  )
  lin_m = lin.clone()
  lin_m[:, 1] *= -1.0
  ang_m = ang.clone()
  ang_m[:, 0] *= -1.0
  ang_m[:, 2] *= -1.0
  return (
    (joint_pos, joint_vel, root_pos, root_quat, lin, ang),
    (joint_pos_m, joint_vel_m, root_pos_m, root_quat_m, lin_m, ang_m),
  )


def from_kick_clips(
  action_names: list[str],
  num_envs: int,
  gamma: float = 0.99,
  k: float = 100.0,
  device: str | torch.device = "cpu",
) -> DecapReference:
  """Kick retargets, both feet, started 0.15–0.35 s before the strike.

  ``10_04`` is a walk and is left out. Each right-foot CSV is mirrored.
  The spring plays from the pre-strike frame through the end of the take,
  then turns off. ``spawn_joint_pos`` follows the robot joint order.
  """
  import mujoco

  from mjlab.asset_zoo.robots.booster_k1.k1_whirlwind_constants import (
    get_k1_whirlwind_robot_cfg,
  )
  from mjlab.entity import Entity
  from mjlab.tasks.tracking.config.k1.kick_motion import EXCLUDED_KICK_STEMS

  robot = Entity(get_k1_whirlwind_robot_cfg())
  model = robot.spec.compile()
  data = mujoco.MjData(model)
  robot_names = list(robot.joint_names)
  missing = [name for name in action_names if name not in robot_names]
  if missing:
    raise ValueError(f"Kick clips have no column for joints {missing}")
  action_index = [robot_names.index(name) for name in action_names]
  joint_qadr = [int(model.joint(name).qposadr[0]) for name in robot_names]
  feet = (
    mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "right_foot_link"),
    mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "left_foot_link"),
  )
  if min(feet) < 0:
    raise RuntimeError("K1 model is missing a foot body")

  src = _kick_motion_dir()
  paths = [
    path
    for path in sorted(src.glob("*_stageii.csv"))
    if path.stem not in EXCLUDED_KICK_STEMS
  ]
  if not paths:
    raise FileNotFoundError(f"No kick retarget CSVs in {src}")

  pieces_q: list[torch.Tensor] = []
  pieces_spawn: list[torch.Tensor] = []
  pieces_spawn_vel: list[torch.Tensor] = []
  pieces_root: list[torch.Tensor] = []
  pieces_quat: list[torch.Tensor] = []
  pieces_lin: list[torch.Tensor] = []
  pieces_ang: list[torch.Tensor] = []
  starts: list[int] = []
  lengths: list[int] = []
  lead_lo: list[int] = []
  lead_hi: list[int] = []
  balls: list[torch.Tensor] = []
  targets: list[torch.Tensor] = []
  cursor = 0
  for path in paths:
    sides = _load_kick_clip(path, robot_names, _POLICY_DT)
    for foot, side in enumerate(sides):
      joint_pos, joint_vel, root_pos, root_quat, lin, ang = side
      frames = int(joint_pos.shape[0])
      body_pos = torch.zeros(frames, 2, 3)
      for frame in range(frames):
        data.qpos[:] = 0.0
        data.qpos[0:3] = root_pos[frame].numpy()
        data.qpos[3:7] = root_quat[frame].numpy()
        for adr, value in zip(joint_qadr, joint_pos[frame].tolist(), strict=True):
          data.qpos[adr] = value
        mujoco.mj_kinematics(model, data)
        for slot, body in enumerate(feet):
          body_pos[frame, slot] = torch.from_numpy(data.xpos[body].copy())
      body_vel = torch.gradient(body_pos, spacing=_POLICY_DT, dim=0)[0]
      strike, ball, target = _strike_ball(body_pos, body_vel, foot)
      lead_frames = (
        int(round(_LEAD_S[1] * (1.0 / _POLICY_DT))),
        int(round(_LEAD_S[0] * (1.0 / _POLICY_DT))),
      )
      lo = max(0, strike - lead_frames[0])
      hi = max(lo, min(frames - 1, strike - lead_frames[1]))
      pieces_q.append(joint_pos[:, action_index])
      pieces_spawn.append(joint_pos)
      pieces_spawn_vel.append(joint_vel)
      pieces_root.append(root_pos)
      pieces_quat.append(root_quat)
      pieces_lin.append(lin)
      pieces_ang.append(ang)
      starts.append(cursor)
      lengths.append(frames)
      lead_lo.append(lo)
      lead_hi.append(hi)
      balls.append(ball)
      targets.append(target)
      cursor += frames

  dev = torch.device(device)
  head_cols = torch.tensor(
    [i for i, name in enumerate(action_names) if name.startswith("Head_")],
    dtype=torch.long,
    device=dev,
  )
  n_clips = len(starts)
  reference = DecapReference(
    joint_pos=torch.cat(pieces_q, dim=0).to(dev),
    clip_starts=torch.tensor(starts, dtype=torch.long, device=dev),
    clip_lengths=torch.tensor(lengths, dtype=torch.long, device=dev),
    weights=torch.ones(n_clips, device=dev),
    head_cols=head_cols,
    num_envs=num_envs,
    gamma=gamma,
    k=k,
    stop_at_end=True,
    lead_lo=torch.tensor(lead_lo, dtype=torch.long, device=dev),
    lead_hi=torch.tensor(lead_hi, dtype=torch.long, device=dev),
    root_pos=torch.cat(pieces_root, dim=0).to(dev),
    root_quat=torch.cat(pieces_quat, dim=0).to(dev),
    root_lin_vel=torch.cat(pieces_lin, dim=0).to(dev),
    root_ang_vel=torch.cat(pieces_ang, dim=0).to(dev),
    spawn_joint_pos=torch.cat(pieces_spawn, dim=0).to(dev),
    spawn_joint_vel=torch.cat(pieces_spawn_vel, dim=0).to(dev),
    ball_pos=torch.stack(balls).to(dev),
    target_xy=torch.stack(targets).to(dev),
  )
  return reference

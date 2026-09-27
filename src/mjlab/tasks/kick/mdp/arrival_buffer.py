"""Arrival Pose Buffer for Kick-on-Walk-AMP reset (§9.2)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import torch

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

# Keys stored per frame (DESIGN §9.2.1).
ARRIVAL_KEYS = (
  "joint_pos",  # [N, 22]
  "joint_vel",  # [N, 22]
  "base_lin_vel_b",  # [N, 3]
  "base_ang_vel_b",  # [N, 3]
  "projected_gravity_b",  # [N, 3]
  "root_pos_w",  # [N, 3]
  "root_quat_w",  # [N, 4]
)

_DEFAULT_BUFFER_PATH = (
  Path(__file__).resolve().parents[6].parent
  / "data"
  / "kick"
  / "arrival_pose_buffer.pt"
)


def default_arrival_buffer_path() -> Path:
  return _DEFAULT_BUFFER_PATH


def load_arrival_buffer(
  path: str | Path | None = None,
  *,
  device: torch.device | str = "cpu",
) -> dict[str, torch.Tensor] | None:
  """Load ``.pt`` buffer; return ``None`` if missing."""
  buf_path = Path(path) if path is not None else default_arrival_buffer_path()
  if not buf_path.is_file():
    return None
  data = torch.load(buf_path, map_location=device, weights_only=True)
  if not isinstance(data, dict):
    raise TypeError(f"Arrival buffer must be a dict, got {type(data)}")
  for key in ARRIVAL_KEYS:
    if key not in data:
      raise KeyError(f"Arrival buffer missing key '{key}' in {buf_path}")
  return {k: data[k].to(device) for k in ARRIVAL_KEYS}


def sample_arrival_indices(
  buffer: dict[str, torch.Tensor],
  n: int,
  device: torch.device | str,
) -> torch.Tensor:
  """Uniform sample of ``n`` frame indices from the buffer."""
  num = int(buffer["joint_pos"].shape[0])
  return torch.randint(0, num, (n,), device=device)


def apply_arrival_state(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor,
  buffer: dict[str, torch.Tensor],
  indices: torch.Tensor,
  *,
  robot_name: str = "robot",
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
  """Write sampled arrival state onto robot.

  Returns:
    ``(v_x_b, root_pos_w, root_quat_w, lin_vel_w, ang_vel_w)`` — the values
    actually written. Callers must use these (not ``robot.data.*``) for any
    follow-up spawn math: ``write_*_to_sim`` does not refresh data tensors
    until the next kinematics flush.
  """
  from mjlab.entity import Entity
  from mjlab.utils.lab_api.math import quat_apply

  robot: Entity = env.scene[robot_name]
  idx = indices.long().cpu()

  joint_pos = buffer["joint_pos"][idx].to(env.device)
  joint_vel = buffer["joint_vel"][idx].to(env.device)
  root_quat = buffer["root_quat_w"][idx].to(env.device)
  lin_vel_b = buffer["base_lin_vel_b"][idx].to(env.device)
  ang_vel_b = buffer["base_ang_vel_b"][idx].to(env.device)
  sample_z = buffer["root_pos_w"][idx, 2].to(env.device)

  origins = env.scene.env_origins[env_ids]
  root_pos = torch.zeros(len(env_ids), 3, device=env.device)
  root_pos[:, 0] = origins[:, 0]
  root_pos[:, 1] = origins[:, 1]
  root_pos[:, 2] = origins[:, 2] + sample_z

  lin_vel_w = quat_apply(root_quat, lin_vel_b)
  ang_vel_w = quat_apply(root_quat, ang_vel_b)

  root_state = robot.data.default_root_state[env_ids].clone()
  root_state[:, 0:3] = root_pos
  root_state[:, 3:7] = root_quat
  root_state[:, 7:10] = lin_vel_w
  root_state[:, 10:13] = ang_vel_w
  robot.write_root_state_to_sim(root_state, env_ids=env_ids)
  robot.write_joint_state_to_sim(joint_pos, joint_vel, env_ids=env_ids)
  return lin_vel_b[:, 0], root_pos, root_quat, lin_vel_w, ang_vel_w


def apply_fallback_standing(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor,
  *,
  robot_name: str = "robot",
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
  """Default standing reset when arrival buffer is absent; ``v_x = 0``.

  Returns the same tuple as ``apply_arrival_state`` (written pose/vel).
  """
  from mjlab.entity import Entity
  from mjlab.utils.lab_api.math import sample_uniform

  robot: Entity = env.scene[robot_name]
  n = len(env_ids)
  device = env.device
  origins = env.scene.env_origins[env_ids]

  root_state = robot.data.default_root_state[env_ids].clone()
  root_state[:, 0:2] = origins[:, :2]
  # Keep default standing height (do not hardcode); XY from env origin.
  root_state[:, 2] = origins[:, 2] + root_state[:, 2]
  # Random yaw so ball/target R_z(ψ) varies.
  yaw = sample_uniform(
    torch.full((n,), -3.14, device=device),
    torch.full((n,), 3.14, device=device),
    (n,),
    device,
  )
  half = 0.5 * yaw
  root_state[:, 3] = torch.cos(half)  # w
  root_state[:, 4] = 0.0
  root_state[:, 5] = 0.0
  root_state[:, 6] = torch.sin(half)  # z
  root_state[:, 7:] = 0.0
  robot.write_root_state_to_sim(root_state, env_ids=env_ids)

  default_pos = robot.data.default_joint_pos[env_ids]
  default_vel = torch.zeros_like(default_pos)
  robot.write_joint_state_to_sim(default_pos, default_vel, env_ids=env_ids)

  root_pos = root_state[:, 0:3].clone()
  root_quat = root_state[:, 3:7].clone()
  lin_vel_w = root_state[:, 7:10].clone()
  ang_vel_w = root_state[:, 10:13].clone()
  return torch.zeros(n, device=device), root_pos, root_quat, lin_vel_w, ang_vel_w

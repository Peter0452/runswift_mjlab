from __future__ import annotations

from functools import partial

import torch
from rsl_rl.env import VecEnv
from tensordict import TensorDict

K1_JOINT_DIM = 22
K1_ACTION_DIM = 22

# Joint slots whose axes change sign under a left/right mirror.
K1_INVERTED_JOINT_INDICES: tuple[int, ...] = (
  0,
  3,
  5,
  7,
  9,
  11,
  12,
  15,
  17,
  18,
  21,
)

# The parallel ankle's A/B crank axes both point along +y. Unlike serial ankle
# roll, neither crank changes sign under a left/right mirror.
K1_PARALLEL_INVERTED_JOINT_INDICES: tuple[int, ...] = tuple(
  index for index in K1_INVERTED_JOINT_INDICES if index not in (15, 21)
)
POLICY_DIM_NO_BASE_LIN_VEL = 75
POLICY_DIM_KICK_STAGE1 = 83
# Kick loop: the stage-1 yaw-command slot carries the ball-memory age.
KICK_LOOP_AGE_SLOT = 74
POLICY_DIM_KICK_WALKAMP = 78
CRITIC_EXTRA_DIM_WALK = 15
CRITIC_EXTRA_DIM_KICK = 17
# Backward-compatible alias (Walk AMP).
CRITIC_EXTRA_DIM = CRITIC_EXTRA_DIM_WALK


def _critic_extra_dim(policy_dim: int) -> int:
  if policy_dim == POLICY_DIM_KICK_WALKAMP:
    return CRITIC_EXTRA_DIM_KICK
  if policy_dim in (POLICY_DIM_NO_BASE_LIN_VEL, POLICY_DIM_KICK_STAGE1):
    return CRITIC_EXTRA_DIM_WALK
  raise ValueError(f"Unknown policy dim {policy_dim}")


def _augment_symmetries(
  obs: TensorDict | None,
  actions: torch.Tensor | None,
  inverted_indices: tuple[int, ...],
) -> tuple[TensorDict | None, torch.Tensor | None]:
  """Apply symmetry augmentations to observations and actions."""

  if obs is not None:
    actor_obs = obs["actor"]
    critic_obs = obs["critic"]
    actor_dim = actor_obs.shape[1]
    critic_dim = critic_obs.shape[1]
    if not _is_supported_policy_dim(actor_dim):
      raise ValueError(
        f"Unsupported actor observation dim: {actor_dim}. "
        f"Expected one of {SUPPORTED_POLICY_DIMS}."
      )
    expected_critic_dim = actor_dim + _critic_extra_dim(actor_dim)
    if critic_dim != expected_critic_dim:
      raise ValueError(
        f"Critic observation dim mismatch: got {critic_dim}, "
        f"expected {expected_critic_dim}."
      )

    n_envs = actor_obs.shape[0]

    # augment the batch size to 2 different symmetries
    actor_aug = torch.zeros(n_envs * 2, actor_obs.shape[1], device=actor_obs.device)
    actor_aug[:n_envs] = actor_obs
    actor_aug[n_envs : 2 * n_envs] = flip_k1_policy_obs_left_right(
      actor_obs, inverted_indices
    )

    critic_aug = torch.zeros(n_envs * 2, critic_obs.shape[1], device=critic_obs.device)
    critic_aug[:n_envs] = critic_obs
    critic_aug[n_envs : 2 * n_envs] = flip_k1_critic_obs_left_right(
      critic_obs, inverted_indices
    )

    obs = TensorDict(
      {"actor": actor_aug, "critic": critic_aug}, batch_size=(n_envs * 2,)
    )

  if actions is not None:
    if actions.shape[1] != K1_ACTION_DIM:
      raise ValueError(
        f"Unsupported action dim: {actions.shape[1]}. Expected {K1_ACTION_DIM}."
      )

    n_envs = actions.shape[0]

    # augment the batch size to 2 different symmetries
    actions_aug = torch.zeros(n_envs * 2, actions.shape[1], device=actions.device)
    actions_aug[:n_envs] = actions[:]
    actions_aug[n_envs : 2 * n_envs] = flip_k1_action_left_right(
      actions, inverted_indices
    )

    actions = actions_aug

  return obs, actions


def augment_symmetries(
  env: VecEnv, obs: TensorDict | None, actions: torch.Tensor | None
) -> tuple[TensorDict | None, torch.Tensor | None]:
  """Apply left/right symmetry for the serial-ankle K1."""
  del env
  return _augment_symmetries(obs, actions, K1_INVERTED_JOINT_INDICES)


def augment_symmetries_kick_loop(
  env: VecEnv, obs: TensorDict | None, actions: torch.Tensor | None
) -> tuple[TensorDict | None, torch.Tensor | None]:
  """``augment_symmetries`` for the kick loop: slot 74 holds the ball-memory
  age, not a yaw rate, so the mirror keeps it instead of negating it."""
  del env
  kept = None
  if obs is not None:
    kept = (
      obs["actor"][:, KICK_LOOP_AGE_SLOT].clone(),
      obs["critic"][:, KICK_LOOP_AGE_SLOT].clone(),
    )
  obs, actions = _augment_symmetries(obs, actions, K1_INVERTED_JOINT_INDICES)
  if obs is not None and kept is not None:
    n = kept[0].shape[0]
    obs["actor"][n:, KICK_LOOP_AGE_SLOT] = kept[0]
    obs["critic"][n:, KICK_LOOP_AGE_SLOT] = kept[1]
  return obs, actions


def augment_symmetries_parallel(
  env: VecEnv, obs: TensorDict | None, actions: torch.Tensor | None
) -> tuple[TensorDict | None, torch.Tensor | None]:
  """Apply left/right symmetry for the parallel-ankle K1."""
  del env
  return _augment_symmetries(obs, actions, K1_PARALLEL_INVERTED_JOINT_INDICES)


def flip_k1_action_left_right(
  action: torch.Tensor,
  inverted_indices: tuple[int, ...] = K1_INVERTED_JOINT_INDICES,
) -> torch.Tensor:
  action = action.clone()
  # switch left and right joints
  action = _switch_k1_joints_left_right(action, inverted_indices)
  return action


def flip_k1_policy_obs_left_right(
  obs: torch.Tensor,
  inverted_indices: tuple[int, ...] = K1_INVERTED_JOINT_INDICES,
) -> torch.Tensor:
  obs = obs.clone()
  policy_dim = obs.shape[1]
  layout = _get_policy_layout(policy_dim)
  if layout is None:
    raise ValueError(
      f"Unsupported policy observation dim: {policy_dim}. "
      f"Expected one of {SUPPORTED_POLICY_DIMS}."
    )

  # Base ang vel + projected gravity (always first 6).
  obs[:, 0:3] = obs[:, 0:3] * obs.new_tensor([-1.0, 1.0, -1.0])
  obs[:, 3:6] = obs[:, 3:6] * obs.new_tensor([1.0, -1.0, 1.0])

  # Optional kick slots: ball_rel_pos + target_pos (base-frame 3-vectors).
  kick_start = 6
  for i in range(layout["kick_vec_blocks"]):
    s = kick_start + i * 3
    obs[:, s : s + 3] = obs[:, s : s + 3] * obs.new_tensor([1.0, -1.0, 1.0])

  joint_pos_start = kick_start + layout["kick_vec_blocks"] * 3
  joint_vel_start = joint_pos_start + K1_JOINT_DIM
  last_actions_start = joint_vel_start + K1_JOINT_DIM
  command_start = last_actions_start + K1_ACTION_DIM

  obs[:, joint_pos_start:joint_vel_start] = _switch_k1_joints_left_right(
    obs[:, joint_pos_start:joint_vel_start], inverted_indices
  )
  obs[:, joint_vel_start:last_actions_start] = _switch_k1_joints_left_right(
    obs[:, joint_vel_start:last_actions_start], inverted_indices
  )
  obs[:, last_actions_start:command_start] = _switch_k1_joints_left_right(
    obs[:, last_actions_start:command_start], inverted_indices
  )
  if layout["has_command"]:
    obs[:, command_start : command_start + 3] = obs[
      :, command_start : command_start + 3
    ] * obs.new_tensor([1.0, -1.0, -1.0])
  if obs.shape[1] == POLICY_DIM_KICK_STAGE1:
    # Speed limits (magnitudes) and the range one-hot stay put; the
    # kick-direction sine flips. Stage 1 stores zeros in these slots, so this
    # is an identity for that task.
    obs[:, command_start + 7] = -obs[:, command_start + 7]

  return obs


def flip_k1_critic_obs_left_right(
  obs: torch.Tensor,
  inverted_indices: tuple[int, ...] = K1_INVERTED_JOINT_INDICES,
) -> torch.Tensor:
  obs = obs.clone()
  # Infer policy dim from known extras.
  if obs.shape[1] == POLICY_DIM_KICK_WALKAMP + CRITIC_EXTRA_DIM_KICK:
    policy_dim = POLICY_DIM_KICK_WALKAMP
  elif obs.shape[1] == POLICY_DIM_NO_BASE_LIN_VEL + CRITIC_EXTRA_DIM_WALK:
    policy_dim = POLICY_DIM_NO_BASE_LIN_VEL
  elif obs.shape[1] == POLICY_DIM_KICK_STAGE1 + CRITIC_EXTRA_DIM_WALK:
    policy_dim = POLICY_DIM_KICK_STAGE1
  else:
    raise ValueError(
      f"Unsupported critic observation dim: {obs.shape[1]}. "
      f"Expected {POLICY_DIM_NO_BASE_LIN_VEL}+{CRITIC_EXTRA_DIM_WALK}, "
      f"{POLICY_DIM_KICK_STAGE1}+{CRITIC_EXTRA_DIM_WALK}, or "
      f"{POLICY_DIM_KICK_WALKAMP}+{CRITIC_EXTRA_DIM_KICK}."
    )

  obs[:, :policy_dim] = flip_k1_policy_obs_left_right(
    obs[:, :policy_dim], inverted_indices
  )

  if policy_dim in (POLICY_DIM_NO_BASE_LIN_VEL, POLICY_DIM_KICK_STAGE1):
    # Walk: base_lin_vel + foot block. Stage 1 uses the same tail.
    base_lin_vel_start = policy_dim
    obs[:, base_lin_vel_start : base_lin_vel_start + 3] = obs[
      :, base_lin_vel_start : base_lin_vel_start + 3
    ] * obs.new_tensor([1.0, -1.0, 1.0])
    foot_height_start = policy_dim + 3
  else:
    # Kick-on-Walk: foot block then ball_velocity + ball_foot_contact.
    foot_height_start = policy_dim

  foot_air_time_start = foot_height_start + 2
  foot_contact_start = foot_air_time_start + 2
  foot_contact_forces_start = foot_contact_start + 2

  obs[:, [foot_height_start, foot_height_start + 1]] = obs[
    :, [foot_height_start + 1, foot_height_start]
  ]
  obs[:, [foot_air_time_start, foot_air_time_start + 1]] = obs[
    :, [foot_air_time_start + 1, foot_air_time_start]
  ]
  obs[:, [foot_contact_start, foot_contact_start + 1]] = obs[
    :, [foot_contact_start + 1, foot_contact_start]
  ]
  # Swap L↔R force triples and negate F_y (DESIGN §6.1).
  obs[
    :,
    [
      foot_contact_forces_start,
      foot_contact_forces_start + 1,
      foot_contact_forces_start + 2,
      foot_contact_forces_start + 3,
      foot_contact_forces_start + 4,
      foot_contact_forces_start + 5,
    ],
  ] = obs[
    :,
    [
      foot_contact_forces_start + 3,
      foot_contact_forces_start + 4,
      foot_contact_forces_start + 5,
      foot_contact_forces_start,
      foot_contact_forces_start + 1,
      foot_contact_forces_start + 2,
    ],
  ] * obs.new_tensor([1.0, -1.0, 1.0, 1.0, -1.0, 1.0])

  if policy_dim == POLICY_DIM_KICK_WALKAMP:
    ball_vel_start = foot_contact_forces_start + 6
    ball_foot_start = ball_vel_start + 3
    obs[:, ball_vel_start : ball_vel_start + 3] = obs[
      :, ball_vel_start : ball_vel_start + 3
    ] * obs.new_tensor([1.0, -1.0, 1.0])
    obs[:, [ball_foot_start, ball_foot_start + 1]] = obs[
      :, [ball_foot_start + 1, ball_foot_start]
    ]

  return obs


SUPPORTED_POLICY_DIMS = (
  POLICY_DIM_NO_BASE_LIN_VEL,
  POLICY_DIM_KICK_STAGE1,
  POLICY_DIM_KICK_WALKAMP,
)


def _is_supported_policy_dim(policy_dim: int) -> bool:
  return policy_dim in SUPPORTED_POLICY_DIMS


def _get_policy_layout(policy_dim: int) -> dict[str, int | bool] | None:
  """Return layout metadata for Walk (75) or Kick-on-Walk-AMP (78)."""
  if policy_dim in (POLICY_DIM_NO_BASE_LIN_VEL, POLICY_DIM_KICK_STAGE1):
    # Walk: [ang(3), grav(3), q(22), qd(22), a(22), cmd(3)].
    # The 8-slot tail keeps the speed limits and the range one-hot, and
    # flips the kick-direction sine.
    return {"kick_vec_blocks": 0, "has_command": True}
  if policy_dim == POLICY_DIM_KICK_WALKAMP:
    # [ang(3), grav(3), ball(3), target(3), q(22), qd(22), a(22)]
    return {"kick_vec_blocks": 2, "has_command": False}
  return None


def _get_num_linear_obs_blocks(policy_dim: int) -> int | None:
  """Legacy helper — kick vectors are handled in ``_get_policy_layout``."""
  layout = _get_policy_layout(policy_dim)
  if layout is None:
    return None
  return int(layout["kick_vec_blocks"])


def _switch_k1_joints_left_right(
  joints: torch.Tensor,
  inverted_indices: tuple[int, ...] = K1_INVERTED_JOINT_INDICES,
) -> torch.Tensor:
  """Switch left and right joints in the K1 joint tensor.

  Joint order:

  'Head_Yaw' (Inverted), 'Head_Pitch',
  'Left_Shoulder_Pitch', 'Left_Shoulder_Roll' (Inverted), 'Left_Elbow_Pitch', 'Left_Elbow_Yaw' (Inverted),
  'Right_Shoulder_Pitch', 'Right_Shoulder_Roll' (Inverted), 'Right_Elbow_Pitch', 'Right_Elbow_Yaw' (Inverted),
  'Left_Hip_Pitch', 'Left_Hip_Roll' (Inverted), 'Left_Hip_Yaw' (Inverted), 'Left_Knee_Pitch', 'Left_Ankle_Pitch', 'Left_Ankle_Roll' (Inverted),
  'Right_Hip_Pitch', 'Right_Hip_Roll' (Inverted), 'Right_Hip_Yaw' (Inverted), 'Right_Knee_Pitch', 'Right_Ankle_Pitch', 'Right_Ankle_Roll' (Inverted)

  Joints marked as "Inverted" need to have their sign flipped when calculating the left-right symmetry.

  Args:
      joint_tensor (torch.Tensor): The joint tensor of shape (..., 22).
  """
  if joints.shape[1] != K1_JOINT_DIM:
    raise ValueError(
      f"Unsupported joint tensor dim: {joints.shape[1]}. Expected {K1_JOINT_DIM}."
    )
  joints_flipped = torch.zeros_like(joints)

  # Head joints
  joints_flipped[:, :2] = joints[:, :2]
  # Shoulders and Elbows
  joints_flipped[:, 2:6] = joints[:, 6:10]
  joints_flipped[:, 6:10] = joints[:, 2:6]
  # Hips, Knees, Ankles
  joints_flipped[:, 10:16] = joints[:, 16:22]
  joints_flipped[:, 16:22] = joints[:, 10:16]

  joints_flipped[:, list(inverted_indices)] = -joints_flipped[:, list(inverted_indices)]

  return joints_flipped


flip_k1_parallel_action_left_right = partial(
  flip_k1_action_left_right,
  inverted_indices=K1_PARALLEL_INVERTED_JOINT_INDICES,
)
flip_k1_parallel_policy_obs_left_right = partial(
  flip_k1_policy_obs_left_right,
  inverted_indices=K1_PARALLEL_INVERTED_JOINT_INDICES,
)
flip_k1_parallel_critic_obs_left_right = partial(
  flip_k1_critic_obs_left_right,
  inverted_indices=K1_PARALLEL_INVERTED_JOINT_INDICES,
)

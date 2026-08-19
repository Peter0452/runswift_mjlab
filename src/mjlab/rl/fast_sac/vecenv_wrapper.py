"""VecEnv wrapper for FastSAC with correct terminal / truncation handling."""

from __future__ import annotations

import torch
from tensordict import TensorDict

from mjlab.envs import ManagerBasedRlEnv, ManagerBasedRlEnvCfg
from mjlab.utils.spaces import Space


class FastSacVecEnvWrapper:
  """Adapt ``ManagerBasedRlEnv`` for FastSAC.

  Forces ``auto_reset=False`` so terminal observations are returned, then resets
  done envs without double-pushing observation history for continuing envs.
  Pre-reset obs are exposed under ``extras["observations"]["final"]`` for timeout
  bootstrapping.
  """

  def __init__(
    self,
    env: ManagerBasedRlEnv,
    clip_actions: float | None = None,
    actor_obs_key: str = "actor",
    critic_obs_key: str = "critic",
  ):
    self.env = env
    self.clip_actions = clip_actions
    self.actor_obs_key = actor_obs_key
    self.critic_obs_key = critic_obs_key

    # Need true terminal observations for truncated bootstrap.
    self.unwrapped.cfg.auto_reset = False

    self.num_envs = self.unwrapped.num_envs
    self.device = torch.device(self.unwrapped.device)
    self.max_episode_length = self.unwrapped.max_episode_length
    self.num_actions = self.unwrapped.action_manager.total_action_dim

    # Seed buffer so callers can randomize episode lengths like OnPolicyRunner.
    self.env.reset()

  @property
  def cfg(self) -> ManagerBasedRlEnvCfg:
    return self.unwrapped.cfg

  @property
  def unwrapped(self) -> ManagerBasedRlEnv:
    return self.env.unwrapped

  @property
  def observation_space(self) -> Space:
    return self.env.observation_space

  @property
  def action_space(self) -> Space:
    return self.env.action_space

  @property
  def episode_length_buf(self) -> torch.Tensor:
    return self.unwrapped.episode_length_buf

  @episode_length_buf.setter
  def episode_length_buf(self, value: torch.Tensor) -> None:
    self.unwrapped.episode_length_buf = value

  def _extract_group(self, obs_dict, key: str) -> torch.Tensor:
    obs = obs_dict[key]
    if isinstance(obs, dict):
      return torch.cat(list(obs.values()), dim=-1)
    return obs

  def get_observations(self) -> TensorDict:
    obs_dict = self.unwrapped.observation_manager.compute()
    return TensorDict(obs_dict, batch_size=[self.num_envs])

  def reset_with_obs(self) -> tuple[torch.Tensor, torch.Tensor]:
    obs_dict, _ = self.env.reset()
    actor_obs = self._extract_group(obs_dict, self.actor_obs_key)
    critic_obs = self._extract_group(obs_dict, self.critic_obs_key)
    return actor_obs, critic_obs

  def reset(self) -> tuple[TensorDict, dict]:
    obs_dict, extras = self.env.reset()
    return TensorDict(obs_dict, batch_size=[self.num_envs]), extras

  @staticmethod
  def _circular_write_env_ids(
    circular, env_ids: torch.Tensor, data: torch.Tensor
  ) -> None:
    """Write ``data[env_ids]`` at the current pointer without advancing it."""
    if circular._buffer is None:
      circular._pointer = 0
      circular._buffer = torch.empty(
        (circular._max_len, *data.shape), dtype=data.dtype, device=circular._device
      )
      circular._buffer[:] = 0.0

    ptr = max(circular._pointer, 0)
    circular._pointer = ptr
    ids = env_ids.long()
    circular._buffer[ptr, ids] = data[ids]

    is_first = circular._num_pushes[ids] == 0
    if torch.any(is_first):
      first_ids = ids[is_first]
      circular._buffer[:, first_ids] = data[first_ids].unsqueeze(0)

    circular._num_pushes[ids] = torch.maximum(
      circular._num_pushes[ids], torch.ones_like(circular._num_pushes[ids])
    )

  def _recompute_obs_for_reset_envs(self, env_ids: torch.Tensor) -> dict:
    """Build post-reset observations, updating buffers only for ``env_ids``."""
    env = self.unwrapped
    obs_manager = env.observation_manager
    obs_buffer: dict = {}
    ids = env_ids.long()

    for group_name in obs_manager.cfg.keys():
      group_term_names = obs_manager._group_obs_term_names[group_name]
      group_term_cfgs = obs_manager._group_obs_term_cfgs[group_name]
      group_obs: dict[str, torch.Tensor] = {}

      for term_name, term_cfg in zip(group_term_names, group_term_cfgs, strict=False):
        obs: torch.Tensor = term_cfg.func(env, **term_cfg.params).clone()
        if term_cfg.clip:
          obs = obs.clip_(min=term_cfg.clip[0], max=term_cfg.clip[1])
        if term_cfg.scale is not None:
          assert isinstance(term_cfg.scale, torch.Tensor)
          obs = obs.mul_(term_cfg.scale)

        # Fresh episode: no observation delay on the first post-reset frame.
        if term_cfg.delay_max_lag > 0:
          delay_buffer = obs_manager._group_obs_term_delay_buffer[group_name][term_name]
          self._circular_write_env_ids(delay_buffer._buffer, ids, obs)
          delay_buffer._current_lags[ids] = 0
          delay_buffer._step_count[ids] = 1

        if term_cfg.history_length > 0:
          circular = obs_manager._group_obs_term_history_buffer[group_name][term_name]
          self._circular_write_env_ids(circular, ids, obs)
          if term_cfg.flatten_history_dim:
            term_obs = circular.buffer.reshape(env.num_envs, -1)
          else:
            term_obs = circular.buffer
        else:
          term_obs = obs

        group_obs[term_name] = term_obs

      if obs_manager._group_obs_concatenate[group_name]:
        obs_buffer[group_name] = torch.cat(
          list(group_obs.values()),
          dim=obs_manager._group_obs_concatenate_dim[group_name],
        )
      else:
        obs_buffer[group_name] = group_obs

    return obs_buffer

  def step(
    self, actions: torch.Tensor
  ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, dict]:
    """Step and return flat actor/critic obs with final-obs extras.

    Returns:
      actor_obs, rewards, dones, truncations, extras
    """
    if self.clip_actions is not None:
      actions = torch.clamp(actions, -self.clip_actions, self.clip_actions)

    obs_dict, rew, terminated, truncated, extras = self.env.step(actions)
    assert isinstance(rew, torch.Tensor)
    assert isinstance(terminated, torch.Tensor)
    assert isinstance(truncated, torch.Tensor)

    dones = (terminated | truncated).to(dtype=torch.long)
    truncations = truncated.to(dtype=torch.long)

    actor_obs = self._extract_group(obs_dict, self.actor_obs_key)
    critic_obs = self._extract_group(obs_dict, self.critic_obs_key)

    # Terminal obs before reset (needed for timeout bootstrap).
    final_actor = actor_obs.clone()
    final_critic = critic_obs.clone()

    reset_ids = dones.nonzero(as_tuple=False).squeeze(-1)
    if reset_ids.numel() > 0:
      if reset_ids.ndim == 0:
        reset_ids = reset_ids.unsqueeze(0)
      env = self.unwrapped
      env.recorder_manager.record_pre_reset(reset_ids)
      env._reset_idx(reset_ids)
      env.scene.write_data_to_sim()
      env.sim.forward()
      env.command_manager.compute(dt=0.0)
      env.sim.sense()
      reset_obs = self._recompute_obs_for_reset_envs(reset_ids)
      env.obs_buf = {
        key: (
          value.clone()
          if torch.is_tensor(value)
          else {k: v.clone() for k, v in value.items()}
        )
        for key, value in obs_dict.items()
      }
      # Overlay post-reset obs for done envs only.
      for key, value in reset_obs.items():
        if torch.is_tensor(value):
          env.obs_buf[key] = env.obs_buf[key].clone()
          env.obs_buf[key][reset_ids] = value[reset_ids]
        else:
          for term_name, term_val in value.items():
            env.obs_buf[key][term_name] = env.obs_buf[key][term_name].clone()
            env.obs_buf[key][term_name][reset_ids] = term_val[reset_ids]
      env.recorder_manager.record_post_reset(reset_ids)

      actor_obs = actor_obs.clone()
      critic_obs = critic_obs.clone()
      actor_obs[reset_ids] = self._extract_group(reset_obs, self.actor_obs_key)[
        reset_ids
      ]
      critic_obs[reset_ids] = self._extract_group(reset_obs, self.critic_obs_key)[
        reset_ids
      ]

    if not self.cfg.is_finite_horizon:
      extras["time_outs"] = truncated
    else:
      extras["time_outs"] = truncations.bool()

    extras["observations"] = {
      "critic": critic_obs,
      "final": {
        "actor_obs": final_actor,
        "critic_obs": final_critic,
      },
    }
    return actor_obs, rew, dones, truncations, extras

  def close(self) -> None:
    return self.env.close()

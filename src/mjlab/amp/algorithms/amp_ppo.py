from __future__ import annotations

from itertools import chain
from typing import Union

import torch
import torch.nn as nn
from rsl_rl.algorithms.ppo import PPO
from rsl_rl.env import VecEnv
from rsl_rl.extensions import resolve_rnd_config, resolve_symmetry_config
from rsl_rl.models import MLPModel
from rsl_rl.storage import RolloutStorage
from rsl_rl.utils import resolve_callable, resolve_obs_groups
from tensordict import TensorDict

from mjlab.amp.modules.amp import (
  AMP,
  construct_amp,
)
from mjlab.amp.modules.multi_critic import MultiCritic, mix_group_advantages
from mjlab.rl.muon import HybridMuonOptimizer


def _add_critic_heads(loaded: dict, current: dict) -> dict | None:
  """Grow a MultiCritic state with k heads to the current model's n > k heads
  (v27: a kick head next to style and task). Heads 0..k-1 load as saved; each
  extra head copies head k-1, whose return contains the new group's reward.
  None when the layouts differ in any other way."""

  def heads(sd: dict) -> int:
    idx = {int(k.split(".")[1]) for k in sd if k.startswith("critics.")}
    return max(idx) + 1 if idx else 0

  k, n = heads(loaded), heads(current)
  if k == 0 or n <= k:
    return None
  out = {}
  for key, value in current.items():
    i = int(key.split(".")[1])
    src = key if i < k else key.replace(f"critics.{i}.", f"critics.{k - 1}.", 1)
    if src not in loaded or loaded[src].shape != value.shape:
      return None
    out[key] = loaded[src].clone()
  return out


def _widen_discriminator_state(loaded: dict, current: dict) -> dict:
  """Fit a checkpoint discriminator to one with extra trailing inputs (an AMP
  condition appended to the history). The old inputs keep their weights and
  normalizer stats; the new input columns start at zero weight, so the warm
  discriminator judges as before until it learns to use the condition. Any
  other mismatch is left for load_state_dict to report."""
  out = dict(loaded)
  for key, value in loaded.items():
    target = current.get(key)
    if target is None or target.shape == value.shape or value.ndim != 2:
      continue
    if target.shape[0] != value.shape[0] or target.shape[1] <= value.shape[1]:
      continue
    widened = target.detach().clone()
    n = value.shape[1]
    widened[:, :n] = value
    if not key.startswith("amp_normalizer."):
      widened[:, n:] = 0.0
    out[key] = widened
  return out


class AmpPPO(PPO):
  """Proximal Policy Optimization algorithm with AMP support.

  Based on "AMP: Adverserial Motion Priors for Stylized Physics-Based Character Control" (https://arxiv.org/abs/2104.02180).
  """

  def __init__(
    self,
    actor: MLPModel,
    critic: MLPModel,
    storage: RolloutStorage,
    amp: AMP,
    use_smooth_ratio_clipping: bool = False,
    use_muon: bool = False,
    muon_weight_decay: float = 0.0,
    muon_momentum: float = 0.95,
    muon_ns_steps: int = 5,
    caps_temporal_coef: float = 0.0,
    caps_spatial_coef: float = 0.0,
    caps_spatial_sigma: float = 0.05,
    caps_near_ball_scale: float = 1.0,
    caps_near_ball_dist: float = 0.8,
    caps_ball_slot: int = 72,
    imitation_coef: float = 0.0,
    imitation_decay_updates: int = 1000,
    multi_critic_alphas: tuple[float, ...] | None = None,
    device: Union[str, torch.device] = "cpu",
    **kwargs,
  ):
    super().__init__(
      actor=actor, critic=critic, storage=storage, device=device, **kwargs
    )
    self.amp = amp
    self.use_smooth_ratio_clipping = use_smooth_ratio_clipping
    # CAPS smoothness of the deterministic action (Mysore et al., 2021).
    self.caps_temporal_coef = caps_temporal_coef
    self.caps_spatial_coef = caps_spatial_coef
    self.caps_spatial_sigma = caps_spatial_sigma
    # Kick tasks: scale CAPS on samples whose actor ball estimate (slots
    # caps_ball_slot, +1) is within caps_near_ball_dist, so the kick swing is
    # less smoothed than walking. 1.0 = uniform CAPS.
    self.caps_near_ball_scale = caps_near_ball_scale
    self.caps_near_ball_dist = caps_near_ball_dist
    self.caps_ball_slot = caps_ball_slot
    # Teacher imitation (L5, e.g. B-Human's kick near the ball): the runner
    # stores teacher actions + a mask per rollout step (record_teacher); the
    # update adds coef_eff * MSE(actor mean, teacher) on masked samples and
    # the given action columns. coef_eff decays linearly to 0.
    self.imitation_coef = imitation_coef
    self.imitation_decay_updates = max(1, int(imitation_decay_updates))
    self._imit_updates = 0
    self._teacher_actions: torch.Tensor | None = None
    self._teacher_mask: torch.Tensor | None = None
    self.imitation_cols: list[int] | None = None
    # v43 teacher takeover: steps the teacher executed (not sampled by the
    # actor) get zero advantage, so they only feed imitation and the critic.
    self._takeover_mask: torch.Tensor | None = None
    # APEX multi-critic: one advantage weight per reward group. None keeps the
    # single critic. Order matches the groups stacked in the AMP runner
    # (motion style, then task).
    self.multi_critic_alphas = (
      None
      if not multi_critic_alphas
      else tuple(float(alpha) for alpha in multi_critic_alphas)
    )
    self._reward_groups: torch.Tensor | None = None
    self.loaded_matching_critic = False
    if self.multi_critic_alphas is not None:
      groups = len(self.multi_critic_alphas)
      steps, envs = storage.num_transitions_per_env, storage.num_envs
      storage.rewards = torch.zeros(steps, envs, groups, device=self.device)
      storage.values = torch.zeros(steps, envs, groups, device=self.device)
      storage.returns = torch.zeros(steps, envs, groups, device=self.device)

    # Rebuild optimizer to include discriminator parameters alongside actor+critic
    params = [
      {
        "params": chain(self.actor.parameters(), self.critic.parameters()),
        "name": "actor_critic",
        "lr_scale": 1.0,
      },
      {
        "params": self.amp.discriminator.trunk.parameters(),
        "weight_decay": 1.0e-3,
        "name": "amp_trunk",
        "lr_scale": 1.0,
      },
      {
        "params": self.amp.discriminator.linear.parameters(),
        "weight_decay": 1.0e-1,
        "name": "amp_head",
        "lr_scale": 1.0,
      },
    ]
    self.optimizer = torch.optim.Adam(params, lr=self.learning_rate)

    if use_muon:
      matrix_params: list[nn.Parameter] = []
      actor_critic_other_params: list[nn.Parameter] = []
      for module in (self.actor, self.critic):
        for parameter in module.parameters():
          if parameter.ndim == 2:
            matrix_params.append(parameter)
          else:
            actor_critic_other_params.append(parameter)

      self.optimizer = HybridMuonOptimizer(
        matrix_params,
        [
          {
            "params": actor_critic_other_params,
            "name": "actor_critic_adam",
            "lr_scale": 1.0,
            "weight_decay": 0.0,
          },
          {
            "params": self.amp.discriminator.trunk.parameters(),
            "name": "amp_trunk",
            "lr_scale": 1.0,
            "weight_decay": 1.0e-3,
          },
          {
            "params": self.amp.discriminator.linear.parameters(),
            "name": "amp_head",
            "lr_scale": 1.0,
            "weight_decay": 1.0e-1,
          },
        ],
        lr=self.learning_rate,
        muon_weight_decay=muon_weight_decay,
        muon_momentum=muon_momentum,
        muon_ns_steps=muon_ns_steps,
      )

  def set_reward_groups(self, groups: torch.Tensor) -> None:
    """Store per-group rewards for the transition about to be recorded."""
    self._reward_groups = groups

  def process_env_step(
    self,
    obs: TensorDict,
    rewards: torch.Tensor,
    dones: torch.Tensor,
    extras: dict[str, torch.Tensor],
  ) -> None:
    """Record one step. Grouped rewards replace the scalar when multi-critic is on."""
    if self.multi_critic_alphas is None:
      return super().process_env_step(obs, rewards, dones, extras)
    if self._reward_groups is None:
      raise RuntimeError(
        "Multi-critic is enabled but this step did not record reward groups."
      )

    groups = self._reward_groups.to(self.device).clone()
    self._reward_groups = None
    self.actor.update_normalization(obs)
    self.critic.update_normalization(obs)
    if self.rnd:
      self.intrinsic_rewards = self.rnd.get_intrinsic_reward(obs)
      self.rnd.update_normalization(obs)
      groups[:, -1] = groups[:, -1] + self.intrinsic_rewards.view(-1)
    if "time_outs" in extras:
      timeouts = extras["time_outs"].to(self.device).view(-1, 1)
      groups = groups + self.gamma * self.transition.values * timeouts
    self.transition.rewards = groups
    self.transition.dones = dones
    self._add_grouped_transition()
    self.transition.clear()
    self.actor.reset(dones)
    self.critic.reset(dones)

  def _add_grouped_transition(self) -> None:
    """``RolloutStorage.add_transition`` with rewards shaped ``(N, G)``."""
    storage = self.storage
    assert storage is not None
    transition = self.transition
    if storage.step >= storage.num_transitions_per_env:
      raise OverflowError(
        "Rollout buffer overflow! You should call clear() before adding new transitions."
      )
    storage.observations[storage.step].copy_(transition.observations)
    storage.actions[storage.step].copy_(transition.actions)
    storage.rewards[storage.step].copy_(transition.rewards)
    storage.dones[storage.step].copy_(transition.dones.view(-1, 1))
    storage.values[storage.step].copy_(transition.values)
    storage.actions_log_prob[storage.step].copy_(
      transition.actions_log_prob.view(-1, 1)
    )
    if storage.distribution_params is None:
      storage.distribution_params = tuple(
        torch.zeros(
          storage.num_transitions_per_env, *param.shape, device=storage.device
        )
        for param in transition.distribution_params
      )
    for index, param in enumerate(transition.distribution_params):
      storage.distribution_params[index][storage.step].copy_(param)
    storage._save_hidden_states(transition.hidden_states)
    storage.step += 1

  def compute_returns(self, obs: TensorDict) -> None:
    """Per-group GAE, then APEX's normalized weighted advantage."""
    if self.multi_critic_alphas is None:
      super().compute_returns(obs)
      self._zero_takeover_advantages()
      return
    storage = self.storage
    assert storage is not None
    critic_hidden_state = self.critic.get_hidden_state()
    last_values = self.critic(obs).detach()
    self.critic.reset(hidden_state=critic_hidden_state)
    advantage = torch.zeros_like(last_values)
    for step in reversed(range(storage.num_transitions_per_env)):
      next_values = (
        last_values
        if step == storage.num_transitions_per_env - 1
        else storage.values[step + 1]
      )
      next_is_not_terminal = (1.0 - storage.dones[step].float()).expand_as(next_values)
      delta = (
        storage.rewards[step]
        + next_is_not_terminal * self.gamma * next_values
        - storage.values[step]
      )
      advantage = delta + next_is_not_terminal * self.gamma * self.lam * advantage
      storage.returns[step] = advantage + storage.values[step]
    storage.advantages = mix_group_advantages(
      storage.returns, storage.values, self.multi_critic_alphas
    )
    self._zero_takeover_advantages()

  def act_amp(self, amp_obs: torch.Tensor) -> None:
    """Initialize AMP history if collection has not started yet."""
    self.amp.act(amp_obs)

  def reset_amp_history(self, amp_obs: torch.Tensor) -> None:
    """Backfill the policy AMP history from the current observation."""
    self.amp.reset_history(amp_obs)

  def process_amp_step(
    self,
    next_amp_obs: torch.Tensor,
    dones: torch.Tensor,
    cond: torch.Tensor | None = None,
  ) -> torch.Tensor:
    """Append an AMP frame and insert its history into the replay buffer."""
    return self.amp.process_step(next_amp_obs, dones, cond)

  def predict_style_reward(self, amp_history: torch.Tensor) -> torch.Tensor:
    """Predict style reward for a flattened AMP history."""
    return self.amp.predict_style_reward(amp_history)

  def _actor_mean(self, obs, latent_noise: float = 0.0) -> torch.Tensor:
    """Deterministic action; optional Gaussian noise on the normalized input."""
    assert self.actor.distribution is not None
    latent = self.actor.get_latent(obs)
    if latent_noise > 0.0:
      latent = latent + latent_noise * torch.randn_like(latent)
    return self.actor.distribution.deterministic_output(self.actor.mlp(latent))

  def _caps_losses(self, batch, n: int) -> tuple[torch.Tensor, torch.Tensor]:
    """CAPS terms on the deterministic action, which is what runs on hardware.

    Reward penalties on the sampled action are dominated by exploration noise,
    which the policy cannot change; these see the mean directly.
    Temporal: change between consecutive steps of the same episode, from the
    rollout. Spatial: change under small noise on the normalized input. With
    caps_near_ball_scale != 1, samples near the ball are weighted by it.
    """
    storage = self.storage
    assert storage is not None
    steps, envs = storage.num_transitions_per_env, storage.num_envs
    t = torch.randint(0, steps - 1, (n,), device=self.device)
    e = torch.randint(0, envs, (n,), device=self.device)
    same_episode = (storage.dones[t, e, 0] == 0).float()
    obs_t = storage.observations[t, e]
    mu_t = self._actor_mean(obs_t)
    mu_next = self._actor_mean(storage.observations[t + 1, e])
    w_t = same_episode * self._caps_weight(obs_t)
    temporal = ((mu_next - mu_t).pow(2).mean(-1) * w_t).sum() / (
      same_episode.sum().clamp(min=1.0)
    )
    obs = batch.observations[:n]
    w_s = self._caps_weight(obs)
    spatial = (
      (self._actor_mean(obs, self.caps_spatial_sigma) - self._actor_mean(obs))
      .pow(2)
      .mean(-1)
      * w_s
    ).mean()
    return temporal, spatial

  def imitation_coef_eff(self) -> float:
    frac = 1.0 - self._imit_updates / self.imitation_decay_updates
    return self.imitation_coef * max(0.0, frac)

  def record_teacher(self, actions: torch.Tensor, mask: torch.Tensor) -> None:
    """Store the teacher action / mask for the transition being collected."""
    storage = self.storage
    assert storage is not None
    if self._teacher_actions is None:
      steps, envs = storage.num_transitions_per_env, storage.num_envs
      # Allocated outside inference mode so the update can reset / read them.
      with torch.inference_mode(False):
        self._teacher_actions = torch.zeros(
          steps, envs, actions.shape[-1], device=self.device
        )
        self._teacher_mask = torch.zeros(
          steps, envs, dtype=torch.bool, device=self.device
        )
    assert self._teacher_mask is not None
    i = storage.step
    self._teacher_actions[i] = actions.to(self.device)
    self._teacher_mask[i] = mask.to(self.device)

  def record_takeover(self, mask: torch.Tensor) -> None:
    """Mark this rollout step's envs whose executed action was the teacher's."""
    storage = self.storage
    assert storage is not None
    if self._takeover_mask is None:
      with torch.inference_mode(False):
        self._takeover_mask = torch.zeros(
          storage.num_transitions_per_env,
          storage.num_envs,
          dtype=torch.bool,
          device=self.device,
        )
    self._takeover_mask[storage.step] = mask.to(self.device)

  def _zero_takeover_advantages(self) -> None:
    if self._takeover_mask is None or self.storage is None:
      return
    adv = self.storage.advantages
    self.storage.advantages = torch.where(
      self._takeover_mask.view(*self._takeover_mask.shape, 1), 0.0, adv
    )
    self._takeover_mask.zero_()

  def _imitation_loss(self, n: int) -> torch.Tensor | None:
    if self._teacher_actions is None or self._teacher_mask is None:
      return None
    idx = self._teacher_mask.nonzero(as_tuple=False)
    if len(idx) == 0:
      return None
    pick = idx[torch.randint(0, len(idx), (min(n, len(idx)),), device=self.device)]
    # Rollout buffers were filled in inference mode: copy them into normal
    # tensors before they enter the autograd graph.
    pick = pick.clone()
    obs = self.storage.observations[pick[:, 0], pick[:, 1]]
    mu = self._actor_mean(obs)
    target = self._teacher_actions[pick[:, 0], pick[:, 1]].clone()
    if self.imitation_cols is not None:
      cols = torch.tensor([int(c) for c in self.imitation_cols], device=self.device)
      mu, target = mu.index_select(1, cols), target.index_select(1, cols)
    return (mu - target).pow(2).mean()

  def _caps_weight(self, obs) -> torch.Tensor:
    """Per-sample CAPS weight: caps_near_ball_scale near the ball, else 1."""
    actor = obs["actor"] if "actor" in obs.keys() else None
    if self.caps_near_ball_scale == 1.0 or actor is None:
      return torch.ones(obs.batch_size[0], device=self.device)
    k = self.caps_ball_slot
    near = actor[..., k : k + 2].norm(dim=-1) < self.caps_near_ball_dist
    return torch.where(near, self.caps_near_ball_scale, 1.0)

  def update(self) -> dict[str, dict[str, float]]:  # noqa: C901
    """Perform the AMP/PPO update step.

    Most of this implementatation is a direct copy from PPO.update.
    This merely introduces the AMP update described in Algorithm 1.


    Raises:
        RuntimeError: raised when the transition storage isn't initialized

    Returns:
        dict[str, float]: A dictionary containing metrics data
    """
    if self.storage is None:
      raise RuntimeError("Storage is not initialized. Call init_storage first.")
    if self.schedule != "adaptive":
      # A resumed optimizer state carries the learning rate it was saved with;
      # a fixed schedule means the configured one.
      for param_group in self.optimizer.param_groups:
        lr_scale = float(param_group.get("lr_scale", 1.0))
        param_group["lr"] = self.learning_rate * lr_scale

    # Accumulate on GPU to avoid synchronization
    mean_value_loss = torch.zeros(1, device=self.device)
    mean_surrogate_loss = torch.zeros(1, device=self.device)
    mean_entropy = torch.zeros(1, device=self.device)
    mean_amp_loss = torch.zeros(1, device=self.device)
    mean_grad_pen_loss = torch.zeros(1, device=self.device)
    mean_policy_pred = torch.zeros(1, device=self.device)
    mean_expert_pred = torch.zeros(1, device=self.device)
    mean_accuracy_policy = torch.zeros(1, device=self.device)
    mean_accuracy_expert = torch.zeros(1, device=self.device)
    mean_accuracy_policy_elem = 0.0
    mean_accuracy_expert_elem = 0.0
    mean_kl_divergence = torch.zeros(1, device=self.device)
    mean_rnd_loss = torch.zeros(1, device=self.device) if self.rnd else None
    mean_symmetry_loss = torch.zeros(1, device=self.device) if self.symmetry else None
    use_caps = self.caps_temporal_coef > 0.0 or self.caps_spatial_coef > 0.0
    mean_caps_temporal = torch.zeros(1, device=self.device)
    mean_imitation = torch.zeros(1, device=self.device)
    mean_caps_spatial = torch.zeros(1, device=self.device)

    if self.actor.is_recurrent or self.critic.is_recurrent:
      generator = self.storage.recurrent_mini_batch_generator(
        self.num_mini_batches, self.num_learning_epochs
      )
    else:
      generator = self.storage.mini_batch_generator(
        self.num_mini_batches, self.num_learning_epochs
      )

    batch_size = self.storage.num_envs * self.storage.num_transitions_per_env
    mini_batch_size = batch_size // self.num_mini_batches
    num_updates = self.num_learning_epochs * self.num_mini_batches

    amp_policy_generator, amp_expert_generator = self.amp.generators(
      num_mini_batch=num_updates,
      mini_batch_size=mini_batch_size,
      allow_policy_replacement=True,
    )

    # line 18: sample batch of transitions from motion data
    # line 19: sample batch of transitions from policy replay buffer
    for batch, sample_amp_policy, sample_amp_expert in zip(
      generator, amp_policy_generator, amp_expert_generator, strict=False
    ):
      original_batch_size = batch.observations.batch_size[0]

      # normalize advantages, from original PPO impl
      if self.normalize_advantage_per_mini_batch:
        with torch.no_grad():
          batch.advantages = (batch.advantages - batch.advantages.mean()) / (
            batch.advantages.std() + 1.0e-8
          )

      if self.symmetry:
        self.symmetry.augment_batch(batch, original_batch_size)

      self.actor(
        batch.observations,
        masks=batch.masks,
        hidden_state=batch.hidden_states[0],
        stochastic_output=True,
      )
      actions_log_prob_batch = self.actor.get_output_log_prob(batch.actions)
      value_batch = self.critic(
        batch.observations,
        masks=batch.masks,
        hidden_state=batch.hidden_states[1],
      )
      distribution_params = tuple(
        p[:original_batch_size] for p in self.actor.output_distribution_params
      )
      entropy_batch = self.actor.output_entropy[:original_batch_size]

      if self.desired_kl is not None and self.schedule == "adaptive":
        with torch.inference_mode():
          kl = self.actor.get_kl_divergence(
            batch.old_distribution_params, distribution_params
          )
          kl_mean = torch.mean(kl)
          if self.is_multi_gpu:
            torch.distributed.all_reduce(kl_mean, op=torch.distributed.ReduceOp.SUM)
            kl_mean /= self.gpu_world_size
          if self.gpu_global_rank == 0:
            if kl_mean > self.desired_kl * 2.0:
              self.learning_rate = max(1e-5, self.learning_rate / 1.5)
            elif kl_mean < self.desired_kl / 2.0 and kl_mean > 0.0:
              self.learning_rate = min(1e-2, self.learning_rate * 1.5)
          if self.is_multi_gpu:
            lr_tensor = torch.tensor(self.learning_rate, device=self.device)
            torch.distributed.broadcast(lr_tensor, src=0)
            self.learning_rate = lr_tensor.item()
          for param_group in self.optimizer.param_groups:
            # Preserve per-group learning rate ratios (e.g., AMP head/trunk).
            lr_scale = float(param_group.get("lr_scale", 1.0))
            param_group["lr"] = self.learning_rate * lr_scale
          mean_kl_divergence += kl_mean

      ratio = torch.exp(
        actions_log_prob_batch - torch.squeeze(batch.old_actions_log_prob)
      )
      min_ratio = 1.0 - self.clip_param
      max_ratio = 1.0 + self.clip_param
      if self.use_smooth_ratio_clipping:
        clipped_ratio = (
          1
          / (1 + torch.exp((-(ratio - min_ratio) / (max_ratio - min_ratio) + 0.5) * 4))
          * (max_ratio - min_ratio)
          + min_ratio
        )
      else:
        clipped_ratio = torch.clamp(ratio, min_ratio, max_ratio)
      surrogate = -torch.squeeze(batch.advantages) * ratio
      surrogate_clipped = -torch.squeeze(batch.advantages) * clipped_ratio
      surrogate_loss = torch.max(surrogate, surrogate_clipped).mean()

      if self.use_clipped_value_loss:
        value_clipped = batch.values + (value_batch - batch.values).clamp(
          -self.clip_param, self.clip_param
        )
        value_losses = (value_batch - batch.returns).pow(2)
        value_losses_clipped = (value_clipped - batch.returns).pow(2)
        value_loss = torch.max(value_losses, value_losses_clipped).mean()
      else:
        value_loss = (batch.returns - value_batch).pow(2).mean()

      loss = (
        surrogate_loss
        + self.value_loss_coef * value_loss
        - self.entropy_coef * entropy_batch.mean()
      )
      imit_coef = self.imitation_coef_eff()
      if imit_coef > 0.0:
        imit = self._imitation_loss(original_batch_size)
        if imit is not None:
          loss = loss + imit_coef * imit
          mean_imitation += imit.detach()
      if use_caps:
        caps_t, caps_s = self._caps_losses(batch, original_batch_size)
        loss = loss + self.caps_temporal_coef * caps_t + self.caps_spatial_coef * caps_s
        mean_caps_temporal += caps_t.detach()
        mean_caps_spatial += caps_s.detach()
      rnd_loss = (
        self.rnd.compute_loss(batch.observations[:original_batch_size])
        if self.rnd
        else None
      )
      symmetry_loss = None
      if self.symmetry:
        symmetry_loss = self.symmetry.compute_loss(
          self.actor, batch, original_batch_size
        )
        if self.symmetry.use_mirror_loss:
          loss = loss + self.symmetry.mirror_loss_coeff * symmetry_loss

      amp_loss, grad_pen_loss, amp_metrics = self.amp.compute_discriminator_batch(
        sample_amp_policy,
        sample_amp_expert,
        grad_penalty_lambda=10.0,
      )

      total_loss = loss + amp_loss + grad_pen_loss

      self.optimizer.zero_grad()
      total_loss.backward()
      if self.rnd:
        self.rnd.optimizer.zero_grad()
        rnd_loss.backward()
      if self.is_multi_gpu:
        self.reduce_parameters()
      nn.utils.clip_grad_norm_(self.actor.parameters(), self.max_grad_norm)
      nn.utils.clip_grad_norm_(self.critic.parameters(), self.max_grad_norm)
      self.optimizer.step()
      if self.rnd:
        self.rnd.optimizer.step()

      # Detach metrics so we don't hold onto autograd graphs.
      entropy_mean = entropy_batch.mean().detach()
      value_loss_det = value_loss.detach()
      surrogate_loss_det = surrogate_loss.detach()
      amp_loss_det = amp_loss.detach()
      grad_pen_loss_det = grad_pen_loss.detach()

      # Update metrics (accumulate on GPU, no synchronization)
      mean_value_loss += value_loss_det
      mean_surrogate_loss += surrogate_loss_det
      mean_entropy += entropy_mean
      if mean_rnd_loss is not None:
        mean_rnd_loss += rnd_loss.detach()
      if mean_symmetry_loss is not None:
        mean_symmetry_loss += symmetry_loss.detach()
      mean_amp_loss += amp_loss_det
      mean_grad_pen_loss += grad_pen_loss_det
      mean_policy_pred += amp_metrics["policy_pred"]
      mean_expert_pred += amp_metrics["expert_pred"]
      mean_accuracy_policy += amp_metrics["accuracy_policy_num"]
      mean_accuracy_expert += amp_metrics["accuracy_expert_num"]
      mean_accuracy_policy_elem += float(amp_metrics["accuracy_policy_den"].item())
      mean_accuracy_expert_elem += float(amp_metrics["accuracy_expert_den"].item())

    # Finalize metrics (single GPU sync point)
    mean_value_loss = (mean_value_loss / num_updates).item()
    mean_surrogate_loss = (mean_surrogate_loss / num_updates).item()
    mean_entropy = (mean_entropy / num_updates).item()
    mean_amp_loss = (mean_amp_loss / num_updates).item()
    mean_grad_pen_loss = (mean_grad_pen_loss / num_updates).item()
    mean_policy_pred = (mean_policy_pred / num_updates).item()
    mean_expert_pred = (mean_expert_pred / num_updates).item()
    mean_accuracy_policy = (
      mean_accuracy_policy / max(1.0, mean_accuracy_policy_elem)
    ).item()
    mean_accuracy_expert = (
      mean_accuracy_expert / max(1.0, mean_accuracy_expert_elem)
    ).item()
    mean_kl_divergence = (mean_kl_divergence / num_updates).item()
    if mean_rnd_loss is not None:
      mean_rnd_loss = (mean_rnd_loss / num_updates).item()
    if mean_symmetry_loss is not None:
      mean_symmetry_loss = (mean_symmetry_loss / num_updates).item()

    # Update the observation normalizers from the rollout, as PPO.update does.
    obs = self.storage.observations.flatten(0, 1)
    self.actor.update_normalization(obs)
    self.critic.update_normalization(obs)
    if self.rnd:
      self.rnd.update_normalization(obs)

    self.storage.clear()
    if self.imitation_coef > 0.0:
      self._imit_updates += 1
      if self._teacher_mask is not None:
        self._teacher_mask.zero_()

    loss_dict = {
      **(
        {
          "caps_temporal": (mean_caps_temporal / num_updates).item(),
          "caps_spatial": (mean_caps_spatial / num_updates).item(),
        }
        if use_caps
        else {}
      ),
      **(
        {
          "imitation": (mean_imitation / num_updates).item(),
          "imitation_coef": self.imitation_coef_eff(),
        }
        if self.imitation_coef > 0.0
        else {}
      ),
      "value": mean_value_loss,
      "surrogate": mean_surrogate_loss,
      "entropy": mean_entropy,
      "Discriminator/loss": mean_amp_loss,
      "Discriminator/grad_penalty": mean_grad_pen_loss,
      "kl_divergence": mean_kl_divergence,
    }
    if self.rnd:
      loss_dict["rnd"] = mean_rnd_loss
    if self.symmetry:
      loss_dict["symmetry"] = mean_symmetry_loss

    return {
      "loss": loss_dict,
      "extra": {
        "policy_pred": mean_policy_pred,
        "expert_pred": mean_expert_pred,
        "accuracy_policy": mean_accuracy_policy,
        "accuracy_expert": mean_accuracy_expert,
      },
    }

  def save(self) -> dict:
    """Return a dict of all models for saving."""
    saved_dict = {
      "actor_state_dict": self.actor.state_dict(),
      "critic_state_dict": self.critic.state_dict(),
      "optimizer_state_dict": self.optimizer.state_dict(),
      "discriminator_state_dict": self.amp.discriminator.state_dict(),
    }
    if self.rnd:
      saved_dict["rnd_state_dict"] = self.rnd.state_dict()
      saved_dict["rnd_optimizer_state_dict"] = self.rnd.optimizer.state_dict()
    return saved_dict

  def _critic_state_matches(self, loaded_critic: dict) -> bool:
    current = self._raw_critic.state_dict()
    if set(current) != set(loaded_critic):
      return False
    return all(current[key].shape == loaded_critic[key].shape for key in current)

  def load(self, loaded_dict: dict, load_cfg: dict | None, strict: bool) -> bool:
    """Load specified models from a saved dict."""
    if "discriminator_state_dict" in loaded_dict:
      self.amp.discriminator.load_state_dict(
        _widen_discriminator_state(
          loaded_dict["discriminator_state_dict"],
          self.amp.discriminator.state_dict(),
        ),
        strict=strict,
      )

    loaded_critic = loaded_dict.get("critic_state_dict")
    if loaded_critic is not None:
      grown = _add_critic_heads(loaded_critic, self._raw_critic.state_dict())
      if grown is not None:
        print(
          "[INFO] Checkpoint critic has fewer heads: extra heads start as copies "
          "of its last head; the optimizer starts fresh."
        )
        loaded_dict = dict(loaded_dict, critic_state_dict=grown)
        loaded_critic = grown
        # rsl_rl treats a missing key as "do not load": start from its full
        # default (None = everything), not an empty dict (v27's first launch
        # loaded no actor and trained from random weights).
        load_cfg = dict(
          load_cfg or {"actor": True, "critic": True, "iteration": True, "rnd": True}
        )
        load_cfg["optimizer"] = False
    self.loaded_matching_critic = (
      loaded_critic is not None and self._critic_state_matches(loaded_critic)
    )
    if loaded_critic is not None and not self.loaded_matching_critic:
      print(
        "[INFO] Checkpoint critic does not match this model "
        "(multi-critic layout or tensor shapes). "
        "Loading the actor and discriminator only; critic, optimizer, and "
        "iteration counter start fresh."
      )
      load_cfg = dict(load_cfg or {})
      load_cfg["critic"] = False
      load_cfg["optimizer"] = False
      load_cfg["iteration"] = False
      if "actor" not in load_cfg:
        load_cfg["actor"] = True

    return super().load(loaded_dict, load_cfg, strict)

  @staticmethod
  def construct_algorithm(
    obs: TensorDict, env: VecEnv, cfg: dict, device: str
  ) -> AmpPPO:
    """Construct the AmpPPO algorithm.

    Uses the base PPO.construct_algorithm to create actor, critic, and storage,
    then wraps them in AmpPPO with the discriminator and motion loader.
    """
    # Resolve class callables for actor/critic
    actor_class: type[MLPModel] = resolve_callable(cfg["actor"].pop("class_name"))
    critic_class: type[MLPModel] = resolve_callable(cfg["critic"].pop("class_name"))

    # Resolve observation groups
    default_sets = ["actor", "critic"]
    if "rnd_cfg" in cfg["algorithm"] and cfg["algorithm"]["rnd_cfg"] is not None:
      default_sets.append("rnd_state")
    cfg["obs_groups"] = resolve_obs_groups(obs, cfg["obs_groups"], default_sets)

    # Resolve RND and symmetry configs
    cfg["algorithm"] = resolve_rnd_config(cfg["algorithm"], obs, cfg["obs_groups"], env)
    cfg["algorithm"] = resolve_symmetry_config(cfg["algorithm"], env)

    # Remove class_name from algorithm config (we're constructing AmpPPO, not the resolved class)
    cfg["algorithm"].pop("class_name", None)

    # Create actor and critic
    actor: MLPModel = actor_class(
      obs, cfg["obs_groups"], "actor", env.num_actions, **cfg["actor"]
    ).to(device)
    print(f"Actor Model: {actor}")
    if cfg["algorithm"].pop("share_cnn_encoders", None):
      cfg["critic"]["cnns"] = actor.cnns  # type: ignore[attr-defined]
    alphas = cfg["algorithm"].get("multi_critic_alphas")
    n_critics = len(alphas) if alphas else 1
    if n_critics == 1:
      critic: MLPModel | MultiCritic = critic_class(
        obs, cfg["obs_groups"], "critic", 1, **cfg["critic"]
      ).to(device)
    else:
      # A fresh critic config per head: constructing a head can pop keys.
      critic = MultiCritic(
        [
          critic_class(obs, cfg["obs_groups"], "critic", 1, **dict(cfg["critic"])).to(
            device
          )
          for _ in range(n_critics)
        ]
      ).to(device)
    print(f"Critic Model: {critic}")

    # Create storage
    storage = RolloutStorage(
      "rl", env.num_envs, cfg["num_steps_per_env"], obs, [env.num_actions], device
    )

    amp, _ = construct_amp(obs, env, cfg, device)

    # Create AmpPPO
    alg = AmpPPO(
      actor=actor,
      critic=critic,
      storage=storage,
      amp=amp,
      device=device,
      **cfg["algorithm"],
      multi_gpu_cfg=cfg["multi_gpu"],
    )
    alg.compile(cfg.get("torch_compile_mode"))
    return alg

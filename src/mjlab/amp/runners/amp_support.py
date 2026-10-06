from __future__ import annotations

import torch
from tensordict import TensorDict

from mjlab.amp.curriculums import AMP_STYLE_WEIGHT_ATTR

AMP_STYLE_REWARD_KEY = "Episode_Metrics/Amp/style_reward"
AMP_TASK_REWARD_KEY = "Episode_Metrics/Amp/task_reward"
AMP_STYLE_TASK_RATIO_KEY = "Episode_Metrics/Amp/style_task_ratio"


class AmpRunner:
  """Shared AMP reward/metrics utilities for runners."""

  _amp_enabled: bool = False

  def _setup_amp_support(self, train_cfg: dict, *, require_amp_group: bool) -> bool:
    amp_groups = train_cfg["obs_groups"].get("amp")
    if not amp_groups:
      if require_amp_group:
        raise ValueError("AMP runner requires an 'amp' observation group.")
      self._amp_enabled = False
      return False

    self.style_reward_weight = train_cfg["style_reward_weight"]
    self.amp_group_names = list(amp_groups)

    # Per-environment episode sums for cumulative reward tracking.
    self._amp_style_reward_sum = torch.zeros(
      self.env.num_envs, dtype=torch.float32, device=self.device
    )
    self._amp_task_reward_sum = torch.zeros(
      self.env.num_envs, dtype=torch.float32, device=self.device
    )
    self._amp_metric_log_keys = (
      AMP_STYLE_REWARD_KEY,
      AMP_TASK_REWARD_KEY,
      AMP_STYLE_TASK_RATIO_KEY,
    )
    self._amp_enabled = True
    return True

  def _compute_style_weight(self) -> float:
    env = self.env.unwrapped
    return getattr(env, AMP_STYLE_WEIGHT_ATTR, self.style_reward_weight)

  def _compute_style_reward_scale(self) -> float:
    """Match the environment's reward-rate scaling convention."""
    env = self.env.unwrapped
    return env.step_dt if env.cfg.scale_rewards_by_dt else 1.0

  def _get_amp_style_mask(self) -> torch.Tensor:
    """Per-env AMP style scale in ``[0, 1]`` (multiplies base style weight).

    * Non-kick AMP (no ball): always 1.
    * Kick AMP: ``(~kick_detected) * exp(-‖d_agent,ball‖² / σ²)`` with
      ``σ² = 1.0`` by default — style fades when wandering far from the ball
      so walking-style farming requires closing in. After ``kick_detected``,
      scale is 0 so settle is task-only.
    * A task that sets ``env.amp_style_gate`` ([N] in ``[0, 1]``) owns the
      gate outright (e.g. style off only around each kick of a multi-kick
      episode); the latch and proximity gate are skipped.
    """
    env = self.env.unwrapped
    gate = getattr(env, "amp_style_gate", None)
    if gate is not None:
      return gate.to(dtype=torch.float32, device=self.device)
    mask = torch.ones(env.num_envs, device=self.device, dtype=torch.float32)

    phase = getattr(env, "_kick_ball_phase", None)
    if phase is not None and phase.kick_detected is not None:
      mask = (~phase.kick_detected).to(dtype=torch.float32, device=self.device)

    # Ball proximity gate (Kick-on-Walk-AMP / Near-Amp when ball is present).
    entities = getattr(env.scene, "entities", None)
    if entities is not None and "ball" in entities and "robot" in entities:
      robot = env.scene["robot"]
      ball = env.scene["ball"]
      delta_xy = ball.data.root_link_pos_w[:, :2] - robot.data.root_link_pos_w[:, :2]
      dist_sq = torch.sum(torch.square(delta_xy), dim=-1)
      sigma_sq = float(getattr(env, "amp_style_proximity_sigma_sq", 1.0))
      proximity = torch.exp(-dist_sq / max(sigma_sq, 1.0e-6))
      mask = mask * proximity
      self._amp_last_proximity = proximity

    return mask

  def _get_amp_obs(self, obs: TensorDict) -> torch.Tensor:
    return torch.cat([obs[group] for group in self.amp_group_names], dim=-1)

  def _reset_amp_metrics(self) -> None:
    if not self._amp_enabled or self.logger.log_dir is None:
      return
    self._amp_style_reward_sum.zero_()
    self._amp_task_reward_sum.zero_()

  def _record_teacher(self, obs) -> None:
    """B-Human's kick policy as the teacher within IMITATION_DIST of a visible
    ball (kick tasks); its leg actions are imitated (see AmpPPO)."""
    env = self.env.unwrapped
    if not hasattr(self, "_teacher"):
      from mjlab.scripts.play_bhuman_kick import BHumanKickPlayConfig, BHumanKickPolicy

      self._teacher = BHumanKickPolicy(
        env, BHumanKickPlayConfig(num_envs=env.num_envs, print_kicks=False)
      )
      self.alg.imitation_cols = [int(c) for c in self._teacher.leg_cols.tolist()]
    cmd = env.command_manager.get_term("twist")
    teacher_actions = self._teacher(obs)
    mask = (cmd.dist <= 1.1) & ~cmd.ball_lost
    self.alg.record_teacher(teacher_actions, mask)

  def _amp_collect_step(
    self,
    obs: TensorDict,
    amp_obs: torch.Tensor | None,
  ) -> tuple[TensorDict, torch.Tensor | None, torch.Tensor, torch.Tensor, dict]:
    """One env step with optional AMP reward shaping.

    Returns (obs, amp_obs, rewards, dones, extras) where rewards are
    the final (potentially AMP-combined) rewards.
    """
    actions = self.alg.act(obs)
    if getattr(self.alg, "imitation_coef", 0.0) > 0.0:
      self._record_teacher(obs)
    if self._amp_enabled:
      self.alg.act_amp(amp_obs)

    obs, rewards, dones, extras = self.env.step(actions.to(self.env.device))
    obs = obs.to(self.device)
    rewards = rewards.to(self.device)
    dones = dones.to(self.device)

    if self._amp_enabled:
      next_amp_obs = self._get_amp_obs(obs)
      next_amp_history = self.alg.process_amp_step(next_amp_obs, dones)
      style_weight = self._compute_style_weight()
      style_mask = self._get_amp_style_mask().view_as(rewards)
      style_pred = self.alg.predict_style_reward(next_amp_history).view_as(rewards)
      logged_mask = style_mask
      if getattr(self.env.unwrapped, "amp_style_gate", None) is not None:
        # Task-owned gate: gated-off envs get the mean style of the others
        # instead of none, so stepping into the gate is not a reward drop the
        # policy learns to avoid.
        on = style_mask > 0.5
        fill = style_pred[on].mean() if on.any() else style_pred.mean()
        style_pred = torch.where(on, style_pred, fill)
        style_mask = torch.ones_like(style_mask)
      # After kick: full task reward, zero style (stabilisation without AMP).
      active_w = style_weight * style_mask
      task_rewards = (1.0 - active_w) * rewards
      style_rewards = active_w * self._compute_style_reward_scale() * style_pred
      rewards = task_rewards + style_rewards
      log = extras.setdefault("log", {})
      if isinstance(log, dict):
        # Mean effective style scale (kick gate × proximity); ∈ [0, 1].
        log["Metrics/amp_style_active"] = logged_mask.mean()
        log["Metrics/amp_style_weight_effective"] = (
          float(style_weight) * style_mask.mean()
        )
        proximity = getattr(self, "_amp_last_proximity", None)
        if proximity is not None:
          log["Metrics/amp_style_proximity"] = proximity.mean()
      self._update_amp_metrics_log(
        extras=extras,
        dones=dones,
        task_rewards=task_rewards,
        style_rewards=style_rewards,
      )
      amp_obs = next_amp_obs

    self.alg.process_env_step(obs, rewards, dones, extras)
    return obs, amp_obs, rewards, dones, extras

  def _update_amp_metrics_log(
    self,
    extras: dict,
    dones: torch.Tensor,
    task_rewards: torch.Tensor,
    style_rewards: torch.Tensor,
  ) -> None:
    if not self._amp_enabled or self.logger.log_dir is None:
      return

    # Accumulate per-environment episode sums.
    self._amp_task_reward_sum.add_(task_rewards.view(-1))
    self._amp_style_reward_sum.add_(style_rewards.view(-1))

    log_data = extras.get("log")
    if isinstance(log_data, dict):
      log_data = dict(log_data)
    else:
      log_data = {}

    # Keep AMP metrics write-once per reset event.
    for key in self._amp_metric_log_keys:
      log_data.pop(key, None)

    done_env_ids = (dones > 0).nonzero(as_tuple=False).flatten()
    if done_env_ids.numel() == 0:
      return

    style_sums = self._amp_style_reward_sum[done_env_ids]
    task_sums = self._amp_task_reward_sum[done_env_ids]
    mean_style = style_sums.mean()
    mean_task = task_sums.mean()

    log_data[AMP_STYLE_REWARD_KEY] = mean_style
    log_data[AMP_TASK_REWARD_KEY] = mean_task
    log_data[AMP_STYLE_TASK_RATIO_KEY] = mean_style.item() / (
      abs(mean_task.item()) + 1.0e-8
    )

    # Reset accumulators for done environments.
    self._amp_style_reward_sum[done_env_ids] = 0.0
    self._amp_task_reward_sum[done_env_ids] = 0.0

    extras["log"] = log_data

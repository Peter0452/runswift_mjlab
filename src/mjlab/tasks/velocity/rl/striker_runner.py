"""Two-level striker training (phase 1): PPO on the controller, frozen skills.

``StrikerControllerVecEnv`` turns ``decision_steps`` env steps into one
controller step: it decodes the controller's action into a skill decision,
runs the frozen kick / walk skills for the learner at every env step, and sums
the env reward. ``StrikerControllerRunner`` keeps the opponent's controller
mirror and pool in step with the learner, as the flat self-play runner does.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

import torch
from tensordict import TensorDict

from mjlab.rl import MjlabOnPolicyRunner, RslRlOnPolicyRunnerCfg, RslRlVecEnvWrapper
from mjlab.tasks.velocity.mdp import striker_skills as skills
from mjlab.tasks.velocity.mdp.self_play import OpponentPolicyAction
from mjlab.tasks.velocity.rl.selfplay_runner import sync_opponent


class StrikerControllerVecEnv(RslRlVecEnvWrapper):
  """The learner as a two-level striker; the policy is its controller."""

  def __init__(
    self,
    env,
    *,
    clip_actions: float | None = None,
    switch_cost: float = 0.05,
    opponent_action_name: str = "opponent",
  ) -> None:
    super().__init__(env, clip_actions=clip_actions)
    opponent = self.unwrapped.action_manager.get_term(opponent_action_name)
    assert isinstance(opponent, OpponentPolicyAction)
    self.kick_skill, self.walk_skill = opponent.skills()
    self.decision_steps = int(opponent.cfg.decision_steps)
    self.switch_cost = float(switch_cost)
    self.num_actions = skills.CONTROLLER_ACTION_DIM
    n, dev = self.num_envs, self.device
    self.kick = torch.zeros(n, dtype=torch.bool, device=dev)
    self.since = torch.zeros(n, dtype=torch.long, device=dev)
    self._obs = self.unwrapped.observation_manager.compute()

  def _wrap(self, obs: dict) -> TensorDict:
    state = skills.skill_state(self.kick, self.since)
    return TensorDict(
      {
        "actor": torch.cat((obs["actor"], state), dim=-1),
        "critic": torch.cat((obs["critic"], state), dim=-1),
      },
      batch_size=[self.num_envs],
    )

  def get_observations(self) -> TensorDict:
    self._obs = self.unwrapped.observation_manager.compute()
    return self._wrap(self._obs)

  def reset(self) -> tuple[TensorDict, dict]:
    obs, extras = self.env.reset()
    self._obs = obs
    self.kick[:] = False
    self.since[:] = 0
    return self._wrap(obs), extras

  def step(
    self, actions: torch.Tensor
  ) -> tuple[TensorDict, torch.Tensor, torch.Tensor, dict]:
    kick, theta, level = skills.decode(actions.to(self.device))
    switched = kick != self.kick
    self.since = torch.where(switched, 0, self.since)
    self.kick = kick
    n, dev = self.num_envs, self.device
    total = -self.switch_cost * switched.float()
    done = torch.zeros(n, dtype=torch.bool, device=dev)
    time_out = torch.zeros(n, dtype=torch.bool, device=dev)
    stand_kick, stand_theta, stand_level = skills.stand_action(n, dev)
    log: dict = {}
    extras: dict = {}
    obs = self._obs
    for _ in range(self.decision_steps):
      # After an env ends inside the chunk its new episode stands until the
      # next decision; those steps are not this transition's.
      k = torch.where(done, stand_kick, kick)
      th = torch.where(done, stand_theta, theta)
      lv = torch.where(done, stand_level, level)
      actor = cast(torch.Tensor, obs["actor"])
      joint = skills.run_skills(actor, k, th, lv, self.kick_skill, self.walk_skill)
      obs, rew, terminated, truncated, extras = self.env.step(joint)
      assert isinstance(rew, torch.Tensor)
      total = total + torch.where(done, 0.0, rew)
      ended = (terminated | truncated) & ~done
      time_out |= truncated & ended
      done |= ended
      log.update(extras.get("log", {}))
      self.since += 1
    self._obs = obs
    self.kick = self.kick & ~done
    self.since = torch.where(done, 0, self.since)
    extras = dict(extras)
    extras["log"] = log
    if not self.cfg.is_finite_horizon:
      extras["time_outs"] = time_out
    return self._wrap(obs), total, done.to(dtype=torch.long), extras


@dataclass
class StrikerControllerRunnerCfg(RslRlOnPolicyRunnerCfg):
  """PPO on the two-level striker's controller."""

  class_name: str = "StrikerControllerRunner"
  snapshot_interval: int = 200
  """Iterations between opponent pool snapshots of the controller."""
  switch_cost: float = 0.05
  """Reward cost per kick / walk switch (discourages dithering)."""
  opponent_action_name: str = "opponent"


class StrikerControllerRunner(MjlabOnPolicyRunner):
  """PPO on the controller; the opponent's mirror follows it."""

  @staticmethod
  def make_vecenv(env, agent_cfg) -> StrikerControllerVecEnv:
    return StrikerControllerVecEnv(
      env,
      clip_actions=agent_cfg.clip_actions,
      switch_cost=agent_cfg.switch_cost,
      opponent_action_name=agent_cfg.opponent_action_name,
    )

  def __init__(self, env, train_cfg: dict, log_dir=None, device: str = "cpu"):
    super().__init__(env, train_cfg, log_dir, device)
    self._it = 0
    update = self.alg.update
    runner = self

    def update_and_sync(*args, **kwargs):
      result = update(*args, **kwargs)
      runner._sync(runner._it)
      runner._it += 1
      return result

    self.alg.update = update_and_sync  # ty: ignore[invalid-assignment]

  def _sync(self, it: int, *, snapshot: bool = True) -> None:
    name = self.cfg.get("opponent_action_name", "opponent")
    term = self.env.unwrapped.action_manager.get_term(name)
    assert isinstance(term, OpponentPolicyAction)
    sync_opponent(
      term,
      self.alg.get_policy().state_dict(),
      it,
      int(self.cfg.get("snapshot_interval", 0)) if snapshot else 0,
      self.logger.log_dir if self.logger.writer is not None else None,
    )

  def learn(self, num_learning_iterations: int, init_at_random_ep_len: bool = False):
    self._it = self.current_learning_iteration
    self._sync(self._it, snapshot=False)
    return super().learn(num_learning_iterations, init_at_random_ep_len)


class StrikerControllerPlayEnv:
  """Play-only view of ``StrikerControllerVecEnv``: one env step per ``step``.

  Viewers pace ``step()`` at the env's ``step_dt``; the training wrapper runs a
  whole decision chunk per call, so play advanced 0.2 s of sim per frame and
  looked choppy. This runs the same chunk one env step at a time and asks the
  controller (wrapped by :meth:`hold`) for a decision only at chunk starts, so
  the controller and its GRU see exactly what they see in training.
  """

  def __init__(self, inner: StrikerControllerVecEnv) -> None:
    self.inner = inner
    self.num_envs = inner.num_envs
    self.unwrapped = inner.unwrapped
    self.t = 0
    self._done = torch.zeros(inner.num_envs, dtype=torch.bool, device=inner.device)
    self._decision: tuple[torch.Tensor, torch.Tensor, torch.Tensor] | None = None
    self._wrapped = inner._wrap(inner._obs)

  def __getattr__(self, name):
    return getattr(self.inner, name)

  def hold(self, policy):
    """Query ``policy`` at chunk starts only; repeat its action in between."""
    env = self

    class _Held:
      def __init__(self) -> None:
        self.action: torch.Tensor | None = None

      def __call__(self, obs):
        if env.t == 0 or self.action is None:
          self.action = policy(obs)
        return self.action

      def reset(self, *args, **kwargs):
        self.action = None
        fn = getattr(policy, "reset", None)
        if fn is not None:
          fn(*args, **kwargs)

    return _Held()

  def get_observations(self) -> TensorDict:
    return self._wrapped

  def reset(self) -> tuple[TensorDict, dict]:
    obs, extras = self.inner.reset()
    self.t = 0
    self._done[:] = False
    self._decision = None
    self._wrapped = obs
    return obs, extras

  def step(self, actions: torch.Tensor):
    inner = self.inner
    if self.t == 0 or self._decision is None:
      kick, theta, level = skills.decode(actions.to(inner.device))
      switched = kick != inner.kick
      inner.since = torch.where(switched, 0, inner.since)
      inner.kick = kick
      self._decision = (kick, theta, level)
      self._done[:] = False
      self.t = 0
    kick, theta, level = self._decision
    done = self._done
    sk, st, sl = skills.stand_action(inner.num_envs, inner.device)
    k = torch.where(done, sk, kick)
    th = torch.where(done, st, theta)
    lv = torch.where(done, sl, level)
    actor = cast(torch.Tensor, inner._obs["actor"])
    joint = skills.run_skills(actor, k, th, lv, inner.kick_skill, inner.walk_skill)
    obs, rew, terminated, truncated, extras = inner.env.step(joint)
    done |= (terminated | truncated) & ~done
    inner.since += 1
    inner._obs = obs
    self.t += 1
    if self.t >= inner.decision_steps:
      inner.kick = inner.kick & ~done
      inner.since = torch.where(done, 0, inner.since)
      self.t = 0
    self._wrapped = inner._wrap(obs)
    return self._wrapped, rew, (terminated | truncated).long(), extras

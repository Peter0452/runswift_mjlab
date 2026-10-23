"""Two-level striker training (phase 1): PPO on the controller, frozen skills.

``StrikerControllerVecEnv`` turns ``decision_steps`` env steps into one
controller step: it decodes the controller's action into a skill decision,
runs the frozen kick / walk skills for the learner at every env step, and sums
the env reward. ``StrikerControllerRunner`` keeps the opponent's controller
mirror and pool in step with the learner, as the flat self-play runner does.

GRU memory: on the robot the runner zeroes the controller's state whenever
the striker takes over (kickoffs, restarts, get-ups, role changes, expired
intents), so in training it is zeroed at every kickoff / restart and at random
(``memory_reset_mean_s``), not only at episode ends. ``MemoryResetPPO`` replays
the GRU through the same resets in its update.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

import torch
from rsl_rl.algorithms import PPO
from tensordict import TensorDict

from k1.tasks.selfplay.mdp.self_play import (
  CONTROLLER_VIS_LEGEND,
  OpponentPolicyAction,
  SelfPlayKickCommand,
)
from k1.tasks.selfplay.runner import actor_std_range, sync_opponent
from k1.tasks.striker.mdp import striker_skills as skills
from mjlab.rl import MjlabOnPolicyRunner, RslRlOnPolicyRunnerCfg, RslRlVecEnvWrapper


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
    command = self.unwrapped.command_manager.get_term(opponent.cfg.command_name)
    assert isinstance(command, SelfPlayKickCommand)
    self.command = command
    self.memory_reset_prob = memory_reset_prob(opponent.cfg, self.unwrapped.step_dt)
    self.controller_ball_memory = bool(opponent.cfg.controller_ball_memory)
    self.walk_velocity = bool(opponent.cfg.controller_walk_velocity)
    self.aim_world = bool(opponent.cfg.aim_world)
    self.robot = self.unwrapped.scene["robot"]
    self.switch_cost = float(switch_cost)
    self.num_actions = skills.CONTROLLER_ACTION_DIM
    n, dev = self.num_envs, self.device
    self.kick = torch.zeros(n, dtype=torch.bool, device=dev)
    self.since = torch.zeros(n, dtype=torch.long, device=dev)
    self._obs = self.unwrapped.observation_manager.compute()

  def yaw(self) -> torch.Tensor:
    return skills.yaw_of(self.robot.data.root_link_quat_w)

  def held(self, theta: torch.Tensor, yaw0: torch.Tensor) -> torch.Tensor:
    """The decision's direction now (``aim_world``), else as decided."""
    if not self.aim_world:
      return theta
    return skills.held_direction(theta, yaw0, self.yaw())

  def walk_cmd(self, actions: torch.Tensor) -> torch.Tensor | None:
    """Direct walk commands (``controller_walk_velocity``), else None."""
    if not self.walk_velocity:
      return None
    return skills.walk_velocity_command(actions, self.command.speed_limit)

  def _controller_actor(self, actor: torch.Tensor) -> torch.Tensor:
    """The skills' actor inputs with the controller's view of a lost ball."""
    if not self.controller_ball_memory:
      return actor
    cmd = self.command
    age = torch.exp(-cmd.time_since_seen / cmd.cfg.ball_memory_tau)
    return skills.controller_ball_obs(
      actor,
      cmd.ball_lost | cmd.never_seen,
      cmd.memory_disproved | cmd.never_seen,
      cmd.memory_ball_b,
      age,
    )

  def _wrap(self, obs: dict) -> TensorDict:
    state = skills.skill_state(self.kick, self.since)
    actor = self._controller_actor(obs["actor"])
    return TensorDict(
      {
        "actor": torch.cat((actor, state), dim=-1),
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
    actions = actions.to(self.device)
    kick, theta, level = skills.decode(actions)
    walk_cmd = self.walk_cmd(actions)
    yaw0 = self.yaw()
    self.command.controller_decision = (kick, theta, level, walk_cmd)
    switched = kick != self.kick
    self.since = torch.where(switched, 0, self.since)
    self.kick = kick
    n, dev = self.num_envs, self.device
    total = -self.switch_cost * switched.float()
    done = torch.zeros(n, dtype=torch.bool, device=dev)
    time_out = torch.zeros(n, dtype=torch.bool, device=dev)
    kickoff = torch.zeros(n, dtype=torch.bool, device=dev)
    stand_kick, stand_theta, stand_level = skills.stand_action(n, dev)
    log: dict = {}
    extras: dict = {}
    obs = self._obs
    for _ in range(self.decision_steps):
      # After an env ends inside the chunk its new episode stands until the
      # next decision; those steps are not this transition's.
      k = torch.where(done, stand_kick, kick)
      th = torch.where(done, stand_theta, self.held(theta, yaw0))
      lv = torch.where(done, stand_level, level)
      wc = None if walk_cmd is None else torch.where(done.unsqueeze(-1), 0.0, walk_cmd)
      actor = cast(torch.Tensor, obs["actor"])
      joint = skills.run_skills(actor, k, th, lv, self.kick_skill, self.walk_skill, wc)
      obs, rew, terminated, truncated, extras = self.env.step(joint)
      assert isinstance(rew, torch.Tensor)
      total = total + torch.where(done, 0.0, rew)
      ended = (terminated | truncated) & ~done
      time_out |= truncated & ended
      done |= ended
      kickoff |= self.command.kickoff_pending & ~done
      log.update(extras.get("log", {}))
      self.since += 1
    self._obs = obs
    self.kick = self.kick & ~done
    self.since = torch.where(done, 0, self.since)
    extras = dict(extras)
    extras["log"] = log
    if self.memory_reset_prob is not None:
      drop = torch.rand(n, device=dev) < self.memory_reset_prob
      extras["memory_reset"] = (kickoff | drop) & ~done
    if not self.cfg.is_finite_horizon:
      extras["time_outs"] = time_out
    return self._wrap(obs), total, done.to(dtype=torch.long), extras


def memory_reset_prob(opponent_cfg, step_dt: float) -> float | None:
  """Per-decision chance of a random GRU reset (None: episode ends only)."""
  mean_s = opponent_cfg.memory_reset_mean_s
  if mean_s is None:
    return None
  return opponent_cfg.decision_steps * step_dt / mean_s


class MemoryResetPPO(PPO):
  """PPO whose recurrent actor also forgets at ``extras["memory_reset"]``.

  The rollout zeroes the actor's state there; the update splits the replayed
  trajectories at the same steps, so it recomputes exactly the rollout's
  actions. Returns still run across the reset (the game goes on).
  """

  _memory_splits: torch.Tensor | None = None

  def process_env_step(self, obs, rewards, dones, extras) -> None:
    reset = extras.get("memory_reset")
    super().process_env_step(obs, rewards, dones, extras)
    if reset is None:
      return
    st = self.storage
    if self._memory_splits is None:
      self._memory_splits = torch.zeros_like(st.dones)
    self._memory_splits[st.step - 1].copy_(reset.view(-1, 1))
    self.actor.reset(reset.to(self.device).long())

  def update(self) -> dict:
    splits = self._memory_splits
    if splits is None:
      return super().update()
    st = self.storage
    dones = st.dones
    st.dones = dones | splits
    try:
      return super().update()
    finally:
      # Made in the rollout's inference mode: replaced, not zeroed in place.
      st.dones = dones
      self._memory_splits = None


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
      actor_std_range(self.cfg),
    )

  def load(
    self,
    path: str,
    load_cfg: dict | None = None,
    strict: bool = True,
    map_location: str | None = None,
  ) -> dict:
    """Load, then mirror the loaded controller into the opponent. Play never
    calls ``learn``, so without this its opponent stays the zero placeholder
    (walk straight ahead at 0.6 m/s, ignoring the ball)."""
    infos = super().load(path, load_cfg, strict, map_location)
    self._sync(self.current_learning_iteration, snapshot=False)
    return infos

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
    print(f"[INFO] Two-level striker overlay: {CONTROLLER_VIS_LEGEND}")
    self.inner = inner
    self.num_envs = inner.num_envs
    self.unwrapped = inner.unwrapped
    self.t = 0
    self._done = torch.zeros(inner.num_envs, dtype=torch.bool, device=inner.device)
    self._yaw0 = torch.zeros(inner.num_envs, device=inner.device)
    self._decision: (
      tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor | None] | None
    ) = None
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
      actions = actions.to(inner.device)
      kick, theta, level = skills.decode(actions)
      switched = kick != inner.kick
      inner.since = torch.where(switched, 0, inner.since)
      inner.kick = kick
      self._decision = (kick, theta, level, inner.walk_cmd(actions))
      self._yaw0 = inner.yaw()
      inner.command.controller_decision = self._decision
      self._done[:] = False
      self.t = 0
    kick, theta, level, walk_cmd = self._decision
    done = self._done
    sk, st, sl = skills.stand_action(inner.num_envs, inner.device)
    k = torch.where(done, sk, kick)
    th = torch.where(done, st, inner.held(theta, self._yaw0))
    lv = torch.where(done, sl, level)
    wc = None if walk_cmd is None else torch.where(done.unsqueeze(-1), 0.0, walk_cmd)
    actor = cast(torch.Tensor, inner._obs["actor"])
    joint = skills.run_skills(actor, k, th, lv, inner.kick_skill, inner.walk_skill, wc)
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

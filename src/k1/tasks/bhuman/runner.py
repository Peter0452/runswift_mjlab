"""B-Human's PPO (Booster Gym ``utils/runner.py`` + ``utils/model.py``).

- Actor 59 -> 256 -> 128 -> 128 -> 13 (ELU), critic (59 + 16) -> 256 -> 256
  -> 128 -> 1, state-independent log-std (init -2). No observation
  normalization.
- Each iteration: ``horizon_length`` steps from all envs, then
  ``mini_epochs`` full-batch updates. GAE is recomputed with the current
  critic every epoch; time-outs bootstrap by replacing the reward with the
  value.
- Loss = value MSE + clipped surrogate + bound loss (means beyond
  +-clip_actions) + entropy_coef * entropy + 0.01 * (entropy outside
  ``entropy_range``)^2; grad-norm clip 1; the learning rate adapts to the KL
  after every epoch within ``learning_rate_range``.

Checkpoints from Booster Gym (``{"model": ..., "optimizer": ...}``, e.g.
``pre-trained/WalkAndKick/K1_kick_inner.pth``) load directly.
"""

from __future__ import annotations

import os
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import torch
import torch.nn.functional as F
from torch.utils.tensorboard import SummaryWriter

from k1.tasks.bhuman.amp_style import AmpStyle
from k1.tasks.bhuman.kick_command import BHumanKickCommand
from k1.tasks.bhuman.robot import LEG_JOINTS
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import RslRlBaseRunnerCfg
from mjlab.tasks.velocity.mdp.decap import from_kick_clips


@dataclass
class BHumanPpoAlgorithmCfg:
  e_clip: float = 0.2
  learning_rate: float = 1.0e-8
  gamma: float = 0.98
  lam: float = 0.95
  bound_coef: float = 1.0
  entropy_coef: float = -0.01
  desired_kl: float = 0.01
  entropy_range: tuple[float, float] = (-11.0, -10.0)
  learning_rate_range: tuple[float, float] = (1.0e-4, 1.0e-2)
  clip_actions: float = 2.0
  init_logstd: float = -2.0


@dataclass
class BHumanPpoRunnerCfg(RslRlBaseRunnerCfg):
  class_name: str = "BHumanPpoRunner"
  num_steps_per_env: int = 24
  mini_epochs: int = 20
  save_interval: int = 100
  max_iterations: int = 200000
  experiment_name: str = "k1_bhuman_kick"
  logger: Literal["wandb", "tensorboard"] = "tensorboard"
  wandb_project: str = "mjlab"
  algorithm: BHumanPpoAlgorithmCfg = field(default_factory=BHumanPpoAlgorithmCfg)
  bhuman_checkpoint: str = ""
  """Booster Gym .pth to start from (model weights; optimizer if present)."""
  decap: bool = False
  """APEX DecAP: a fading action prior from the mocap kick retargets (training
  only; play never attaches it)."""
  decap_gamma: float = 0.99
  decap_k: float = 100.0
  amp: bool = False
  """AMP walking style from the gold walk's motion mix, on while walking to
  the ball (training only)."""
  amp_style_weight: float = 2.0
  """Style reward weight (x dt, like the task terms)."""


class ActorCritic(torch.nn.Module):
  """``utils/model.py``; parameter names match Booster Gym checkpoints."""

  def __init__(self, num_act: int, num_obs: int, num_priv: int, init_logstd: float):
    super().__init__()
    elu = torch.nn.ELU
    self.critic = torch.nn.Sequential(
      torch.nn.Linear(num_obs + num_priv, 256),
      elu(),
      torch.nn.Linear(256, 256),
      elu(),
      torch.nn.Linear(256, 128),
      elu(),
      torch.nn.Linear(128, 1),
    )
    self.actor = torch.nn.Sequential(
      torch.nn.Linear(num_obs, 256),
      elu(),
      torch.nn.Linear(256, 128),
      elu(),
      torch.nn.Linear(128, 128),
      elu(),
      torch.nn.Linear(128, num_act),
    )
    self.logstd = torch.nn.Parameter(torch.full((1, num_act), init_logstd))

  def act(self, obs: torch.Tensor) -> torch.distributions.Normal:
    mean = self.actor(obs)
    return torch.distributions.Normal(mean, torch.exp(self.logstd).expand_as(mean))

  def est_value(self, obs: torch.Tensor, priv: torch.Tensor) -> torch.Tensor:
    return self.critic(torch.cat((obs, priv), dim=-1)).squeeze(-1)


def discount_values(
  rewards: torch.Tensor,
  dones: torch.Tensor,
  values: torch.Tensor,
  last_values: torch.Tensor,
  gamma: float,
  lam: float,
) -> torch.Tensor:
  advantages = torch.zeros_like(rewards)
  last = torch.zeros_like(advantages[-1])
  for t in reversed(range(rewards.shape[0])):
    nonterminal = 1.0 - dones[t].float()
    next_values = last_values if t == rewards.shape[0] - 1 else values[t + 1]
    delta = rewards[t] + gamma * nonterminal * next_values - values[t]
    advantages[t] = last = delta + gamma * lam * nonterminal * last
  return advantages


def surrogate_loss(
  old_log_prob: torch.Tensor,
  log_prob: torch.Tensor,
  advantages: torch.Tensor,
  e_clip: float,
) -> torch.Tensor:
  ratio = torch.exp(log_prob - old_log_prob)
  surrogate = -advantages * ratio
  clipped = -advantages * torch.clamp(ratio, 1.0 - e_clip, 1.0 + e_clip)
  return torch.max(surrogate, clipped).mean()


def _groups(obs: Any) -> tuple[torch.Tensor, torch.Tensor]:
  actor, critic = obs["actor"], obs["critic"]
  assert isinstance(actor, torch.Tensor) and isinstance(critic, torch.Tensor)
  return actor, critic


class _Env:
  """Thin step interface over the mjlab env (no clipping, no wrappers)."""

  def __init__(self, env: ManagerBasedRlEnv):
    self.env = env
    self.num_envs = env.num_envs
    self.num_actions = env.action_manager.total_action_dim
    self.device = env.device

  @property
  def unwrapped(self) -> ManagerBasedRlEnv:
    return self.env

  @property
  def cfg(self):
    return self.env.cfg

  @property
  def kick(self) -> BHumanKickCommand:
    term = self.env.command_manager.get_term("kick")
    assert isinstance(term, BHumanKickCommand)
    return term

  def get_observations(self) -> dict:
    """Observation groups (play viewers)."""
    return dict(self.env.observation_manager.compute())

  def reset(self) -> tuple[torch.Tensor, torch.Tensor]:
    obs, _ = self.env.reset()
    return _groups(obs)

  def step(self, actions: torch.Tensor):
    obs, rew, terminated, truncated, extras = self.env.step(actions)
    dones = terminated | truncated
    time_outs = self.kick.bootstrap_buf.clone()
    return *_groups(obs), rew, dones, time_outs, extras

  def close(self) -> None:
    self.env.close()


class _InferencePolicy(torch.nn.Module):
  def __init__(self, actor: torch.nn.Module):
    super().__init__()
    self.actor = actor

  @torch.no_grad()
  def forward(self, obs) -> torch.Tensor:
    if not isinstance(obs, torch.Tensor):
      obs = obs["actor"]
    return self.actor(obs)


class BHumanPpoRunner:
  @staticmethod
  def make_vecenv(env: ManagerBasedRlEnv, agent_cfg: Any) -> _Env:
    del agent_cfg
    return _Env(env)

  def __init__(
    self,
    env: _Env,
    train_cfg: dict,
    log_dir: str | None = None,
    device: str = "cpu",
  ):
    self.env = env
    self.cfg = train_cfg
    self.alg = train_cfg["algorithm"]
    self.device = device
    self.log_dir = log_dir
    self.current_learning_iteration = 0
    self.learning_rate = float(self.alg["learning_rate"])
    gm = env.unwrapped.observation_manager.group_obs_dim
    num_obs = int(gm["actor"][0])  # type: ignore[index]
    num_priv = int(gm["critic"][0])  # type: ignore[index]
    self.model = ActorCritic(
      env.num_actions, num_obs, num_priv, float(self.alg["init_logstd"])
    ).to(device)
    self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
    self.writer: SummaryWriter | None = None
    self.amp: AmpStyle | None = None
    if train_cfg.get("amp", False):
      self.amp = AmpStyle(
        env.kick, style_weight=float(train_cfg["amp_style_weight"]), device=device
      )
    if train_cfg.get("bhuman_checkpoint"):
      self.load(train_cfg["bhuman_checkpoint"])

  def add_git_repo_to_log(self, _file: str) -> None:
    pass

  def _attach_decap(self) -> None:
    if not self.cfg.get("decap", False):
      return
    horizon = int(self.cfg["num_steps_per_env"])
    reference = from_kick_clips(
      list(LEG_JOINTS),
      self.env.num_envs,
      gamma=float(self.cfg["decap_gamma"]),
      k=float(self.cfg["decap_k"]),
      device=self.device,
    )
    reference.set_decay_steps(self.current_learning_iteration * horizon)
    reference.active[:] = False
    self.env.unwrapped.decap = reference  # type: ignore[attr-defined]
    print(
      f"[BHumanPPO] DecAP: {int(reference.clip_lengths.shape[0])} kick takes, "
      f"factor {reference.factor:.3f}"
    )

  def _init_logging(self) -> None:
    if self.log_dir is None or self.writer is not None:
      return
    if self.cfg.get("logger") == "wandb":
      import wandb

      wandb.init(
        project=self.cfg.get("wandb_project", "mjlab"),
        name=Path(self.log_dir).name,
        dir=self.log_dir,
        config=self.cfg,
        sync_tensorboard=True,
      )
    self.writer = SummaryWriter(log_dir=self.log_dir, flush_secs=10)

  def learn(self, num_learning_iterations: int, init_at_random_ep_len: bool = False):
    del init_at_random_ep_len  # Booster Gym starts all episodes at 0.
    self._init_logging()
    self._attach_decap()
    alg = self.alg
    env = self.env
    n, horizon = env.num_envs, int(self.cfg["num_steps_per_env"])
    dev = self.device
    obs, priv = env.reset()
    if self.amp is not None:
      self.amp.start()
    num_obs, num_priv = obs.shape[-1], priv.shape[-1]
    buf_obs = torch.zeros(horizon, n, num_obs, device=dev)
    buf_priv = torch.zeros(horizon, n, num_priv, device=dev)
    buf_act = torch.zeros(horizon, n, env.num_actions, device=dev)
    buf_rew = torch.zeros(horizon, n, device=dev)
    buf_done = torch.zeros(horizon, n, dtype=torch.bool, device=dev)
    buf_tout = torch.zeros(horizon, n, dtype=torch.bool, device=dev)
    ep_rew = torch.zeros(n, device=dev)
    ep_len = torch.zeros(n, device=dev)
    done_rews: list[float] = []
    done_lens: list[float] = []
    clip = float(alg["clip_actions"])
    lr_lo, lr_hi = alg["learning_rate_range"]
    ent_lo, ent_hi = alg["entropy_range"]
    start = self.current_learning_iteration
    for it in range(start, start + num_learning_iterations):
      t0 = time.time()
      logs: dict[str, list[float]] = defaultdict(list)
      for k in range(horizon):
        buf_obs[k] = obs
        buf_priv[k] = priv
        with torch.no_grad():
          act = self.model.act(obs).sample()
        obs, priv, rew, done, tout, extras = env.step(act)
        if self.amp is not None:
          style = self.amp.reward(done)
          logs["Train/style_reward"].append(float(style.mean()))
          rew = rew + style
        buf_act[k] = act
        buf_rew[k] = rew
        buf_done[k] = done
        buf_tout[k] = tout
        ep_rew += rew
        ep_len += 1
        ids = done.nonzero().flatten()
        if len(ids) > 0:
          done_rews.extend(ep_rew[ids].tolist())
          done_lens.extend(ep_len[ids].tolist())
          ep_rew[ids] = 0
          ep_len[ids] = 0
        for key, v in extras.get("log", {}).items():
          logs[key].append(float(v))
      collect_time = time.time() - t0

      t1 = time.time()
      with torch.no_grad():
        old_dist = self.model.act(buf_obs)
        old_log_prob = old_dist.log_prob(buf_act).sum(dim=-1)
      stats: dict[str, float] = defaultdict(float)
      kl_mean = torch.tensor(0.0)
      epochs = int(self.cfg["mini_epochs"])
      for _ in range(epochs):
        values = self.model.est_value(buf_obs, buf_priv)
        last_values = self.model.est_value(obs, priv)
        with torch.no_grad():
          buf_rew[buf_tout] = values[buf_tout]
          adv = discount_values(
            buf_rew,
            buf_done | buf_tout,
            values,
            last_values,
            float(alg["gamma"]),
            float(alg["lam"]),
          )
          returns = values + adv
          adv = (adv - adv.mean()) / (adv.std() + 1e-8)
        value_loss = F.mse_loss(values, returns)
        dist = self.model.act(buf_obs)
        log_prob = dist.log_prob(buf_act).sum(dim=-1)
        actor_loss = surrogate_loss(old_log_prob, log_prob, adv, float(alg["e_clip"]))
        bound_loss = (dist.loc - clip).clip(min=0.0).square().mean() + (
          dist.loc + clip
        ).clip(max=0.0).square().mean()
        entropy = dist.entropy().sum(dim=-1).mean()
        entropy_loss = (entropy.clamp(ent_lo, ent_hi) - entropy).square()
        loss = (
          value_loss
          + actor_loss
          + float(alg["bound_coef"]) * bound_loss
          + float(alg["entropy_coef"]) * entropy
          + 0.01 * entropy_loss
        )
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
        self.optimizer.step()
        with torch.no_grad():
          kl = torch.sum(
            torch.log(dist.scale / old_dist.scale)
            + 0.5
            * (old_dist.scale.square() + (dist.loc - old_dist.loc).square())
            / dist.scale.square()
            - 0.5,
            dim=-1,
          )
          kl_mean = kl.mean()
          if kl_mean > float(alg["desired_kl"]) * 2:
            self.learning_rate = max(float(lr_lo), self.learning_rate / 1.5)
          elif kl_mean < float(alg["desired_kl"]) / 2:
            self.learning_rate = min(float(lr_hi), self.learning_rate * 1.5)
          for group in self.optimizer.param_groups:
            group["lr"] = self.learning_rate
        stats["value_loss"] += value_loss.item() / epochs
        stats["actor_loss"] += actor_loss.item() / epochs
        stats["bound_loss"] += bound_loss.item() / epochs
        stats["entropy"] += entropy.item() / epochs
      stats["kl_mean"] = float(kl_mean)
      if self.amp is not None:
        stats.update(self.amp.update())
      decap = getattr(self.env.unwrapped, "decap", None)
      if decap is not None:
        stats["decap_factor"] = decap.factor
      stats["lr"] = self.learning_rate
      learn_time = time.time() - t1
      self.current_learning_iteration = it + 1

      self._log(it, stats, logs, done_rews, done_lens, collect_time, learn_time)
      done_rews.clear()
      done_lens.clear()
      if self.log_dir is not None and (it + 1) % int(self.cfg["save_interval"]) == 0:
        self.save(os.path.join(self.log_dir, f"model_{it + 1}.pt"))
    last = self.current_learning_iteration
    if self.log_dir is not None and last % int(self.cfg["save_interval"]) != 0:
      self.save(os.path.join(self.log_dir, f"model_{last}.pt"))

  def _log(
    self,
    it: int,
    stats: dict[str, float],
    logs: dict[str, list[float]],
    rews: list[float],
    lens: list[float],
    collect_time: float,
    learn_time: float,
  ) -> None:
    n = self.env.num_envs * int(self.cfg["num_steps_per_env"])
    fps = n / max(collect_time + learn_time, 1e-6)
    line = f"[{it + 1}] fps {fps:.0f}"
    if rews:
      line += (
        f" | ep reward {sum(rews) / len(rews):.2f} len {sum(lens) / len(lens):.0f}"
      )
    line += f" | value {stats['value_loss']:.4f} kl {stats['kl_mean']:.4f}"
    line += f" lr {stats['lr']:.1e} entropy {stats['entropy']:.2f}"
    print(line, flush=True)
    if self.writer is None:
      return
    for k, v in stats.items():
      self.writer.add_scalar(f"Loss/{k}", v, it)
    self.writer.add_scalar("Perf/fps", fps, it)
    if rews:
      self.writer.add_scalar("Train/mean_reward", sum(rews) / len(rews), it)
      self.writer.add_scalar("Train/mean_episode_length", sum(lens) / len(lens), it)
    for k, v in logs.items():
      self.writer.add_scalar(k, sum(v) / len(v), it)

  def save(self, path: str, infos: dict | None = None) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    torch.save(
      {
        "model": self.model.state_dict(),
        "optimizer": self.optimizer.state_dict(),
        "iter": self.current_learning_iteration,
        "learning_rate": self.learning_rate,
        "amp": self.amp.state_dict() if self.amp is not None else None,
        "infos": infos,
      },
      path,
    )
    print(f"[BHumanPPO] Saved {path}")

  def load(
    self,
    path: str,
    load_cfg: dict | None = None,
    strict: bool = False,
    map_location: str | None = None,
  ) -> dict:
    del load_cfg
    ckpt = torch.load(path, map_location=map_location or self.device, weights_only=True)
    self.model.load_state_dict(ckpt["model"], strict=strict)
    try:
      self.optimizer.load_state_dict(ckpt["optimizer"])
    except (KeyError, ValueError) as e:
      print(f"[BHumanPPO] Optimizer state not loaded: {e}")
    self.current_learning_iteration = int(ckpt.get("iter", 0))
    if self.amp is not None and ckpt.get("amp"):
      self.amp.load_state_dict(ckpt["amp"])
    if "learning_rate" in ckpt:
      self.learning_rate = float(ckpt["learning_rate"])
    print(f"[BHumanPPO] Loaded {path}")
    return ckpt.get("infos") or {}

  def get_inference_policy(self, device: str | None = None) -> _InferencePolicy:
    if device is not None:
      self.model.to(device)
    self.model.eval()
    return _InferencePolicy(self.model.actor)

  def export_policy_to_onnx(
    self, path: str, filename: str = "policy.onnx", verbose: bool = False
  ) -> None:
    import copy

    os.makedirs(path, exist_ok=True)
    actor = copy.deepcopy(self.model.actor).to("cpu").eval()
    first = actor[0]
    assert isinstance(first, torch.nn.Linear)
    num_obs = first.in_features
    torch.onnx.export(
      actor,
      (torch.zeros(1, num_obs),),
      os.path.join(path, filename),
      input_names=["obs"],
      output_names=["actions"],
      verbose=verbose,
      dynamo=False,
    )

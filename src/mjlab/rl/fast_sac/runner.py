"""FastSAC training runner for mjlab."""

from __future__ import annotations

import math
import os
import time
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F
from tensordict import TensorDict
from torch.amp import GradScaler, autocast
from torch.utils.tensorboard import SummaryWriter

from mjlab.rl.fast_sac.buffer import EmpiricalNormalization, SimpleReplayBuffer
from mjlab.rl.fast_sac.networks import Actor, Critic
from mjlab.rl.fast_sac.vecenv_wrapper import FastSacVecEnvWrapper


def _cpu_state(sd: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
  return {k: v.detach().to("cpu", non_blocking=True) for k, v in sd.items()}


class _InferencePolicy(torch.nn.Module):
  """Callable policy for play viewers: accepts TensorDict or tensor."""

  def __init__(
    self,
    actor: Actor,
    obs_normalizer: torch.nn.Module,
    actor_obs_key: str,
    obs_groups: dict[str, tuple[str, ...]],
  ):
    super().__init__()
    self.actor = actor
    self.obs_normalizer = obs_normalizer
    self.actor_obs_key = actor_obs_key
    self.obs_groups = obs_groups

  def _extract_actor_obs(self, obs) -> torch.Tensor:
    if isinstance(obs, torch.Tensor):
      return obs
    keys = self.obs_groups.get("actor", (self.actor_obs_key,))
    parts = []
    for key in keys:
      val = obs[key]
      if isinstance(val, dict):
        parts.extend(val.values())
      else:
        parts.append(val)
    return torch.cat(parts, dim=-1) if len(parts) > 1 else parts[0]

  @torch.no_grad()
  def forward(self, obs) -> torch.Tensor:
    actor_obs = self._extract_actor_obs(obs)
    norm_obs = self.obs_normalizer(actor_obs, update=False)
    return self.actor.explore(norm_obs, deterministic=True)

  def __call__(self, obs) -> torch.Tensor:
    return self.forward(obs)


class FastSacRunner:
  """Off-policy FastSAC runner compatible with mjlab ``train.py`` / ``play.py``."""

  def __init__(
    self,
    env: FastSacVecEnvWrapper,
    train_cfg: dict,
    log_dir: str | None = None,
    device: str = "cpu",
  ):
    if not isinstance(env, FastSacVecEnvWrapper):
      raise TypeError(
        "FastSacRunner requires FastSacVecEnvWrapper. "
        "train.py / play.py should wrap the env accordingly."
      )

    self.cfg = train_cfg
    self.alg_cfg = train_cfg["algorithm"]
    self.env = env
    self.device = device
    self.log_dir = log_dir
    self.gpu_world_size = int(os.environ.get("WORLD_SIZE", "1"))
    self.is_main_process = int(os.environ.get("RANK", "0")) == 0

    self.obs_groups: dict[str, tuple[str, ...]] = train_cfg.get(
      "obs_groups", {"actor": ("actor",), "critic": ("critic",)}
    )
    actor_keys = self.obs_groups.get("actor", ("actor",))
    critic_keys = self.obs_groups.get("critic", ("critic",))
    self.actor_obs_key = actor_keys[0]
    self.critic_obs_key = critic_keys[0]
    # Keep wrapper keys in sync.
    self.env.actor_obs_key = self.actor_obs_key
    self.env.critic_obs_key = self.critic_obs_key

    self.current_learning_iteration = 0
    self.global_step = 0
    self.writer: SummaryWriter | None = None
    if log_dir is not None and self.is_main_process:
      self.writer = SummaryWriter(log_dir=log_dir, flush_secs=10)

    self._setup()

  def _obs_dim(self, key: str) -> int:
    dim = self.env.unwrapped.observation_manager.group_obs_dim[key]
    if isinstance(dim, list):
      return int(sum(math.prod(d) for d in dim))
    return int(math.prod(dim))

  def _setup(self) -> None:
    args = self.alg_cfg
    device = self.device
    n_act = self.env.num_actions
    actor_obs_dim = self._obs_dim(self.actor_obs_key)
    critic_obs_dim = self._obs_dim(self.critic_obs_key)

    self.scaler = GradScaler(enabled=bool(args.get("amp", True)))

    if args.get("obs_normalization", True):
      self.obs_normalizer: torch.nn.Module = EmpiricalNormalization(
        shape=actor_obs_dim, device=device
      )
      self.critic_obs_normalizer: torch.nn.Module = EmpiricalNormalization(
        shape=critic_obs_dim, device=device
      )
    else:
      self.obs_normalizer = EmpiricalNormalization(
        shape=actor_obs_dim, device=device, until=0
      )
      self.critic_obs_normalizer = EmpiricalNormalization(
        shape=critic_obs_dim, device=device, until=0
      )
      # until=0 freezes stats at identity-ish init (mean0/std1).

    # Env action manager already applies scale/offset; keep actor in [-1, 1].
    action_scale = torch.ones(n_act, device=device)
    action_bias = torch.zeros(n_act, device=device)

    self.actor = Actor(
      n_obs=actor_obs_dim,
      n_act=n_act,
      hidden_dim=args.get("actor_hidden_dim", 512),
      log_std_max=args.get("log_std_max", 0.0),
      log_std_min=args.get("log_std_min", -5.0),
      use_tanh=args.get("use_tanh", True),
      use_layer_norm=args.get("use_layer_norm", True),
      device=device,
      action_scale=action_scale,
      action_bias=action_bias,
    )
    critic_kwargs = dict(
      n_obs=critic_obs_dim,
      n_act=n_act,
      num_atoms=args.get("num_atoms", 101),
      v_min=args.get("v_min", -20.0),
      v_max=args.get("v_max", 20.0),
      hidden_dim=args.get("critic_hidden_dim", 768),
      use_layer_norm=args.get("use_layer_norm", True),
      num_q_networks=args.get("num_q_networks", 2),
      device=device,
    )
    self.qnet = Critic(**critic_kwargs)
    self.qnet_target = Critic(**critic_kwargs)
    self.qnet_target.load_state_dict(self.qnet.state_dict())

    wd = args.get("weight_decay", 0.001)
    betas = (0.9, 0.95)
    fused = device.startswith("cuda")
    self.q_optimizer = torch.optim.AdamW(
      self.qnet.parameters(),
      lr=args.get("critic_learning_rate", 3e-4),
      weight_decay=wd,
      fused=fused,
      betas=betas,
    )
    self.actor_optimizer = torch.optim.AdamW(
      self.actor.parameters(),
      lr=args.get("actor_learning_rate", 3e-4),
      weight_decay=wd,
      fused=fused,
      betas=betas,
    )
    self.log_alpha = torch.tensor(
      [math.log(args.get("alpha_init", 0.001))],
      requires_grad=True,
      device=device,
    )
    self.target_entropy = -n_act * args.get("target_entropy_ratio", 0.0)
    self.alpha_optimizer = torch.optim.AdamW(
      [self.log_alpha],
      lr=args.get("alpha_learning_rate", 3e-4),
      fused=fused,
      betas=betas,
    )

    self.rb = SimpleReplayBuffer(
      n_env=self.env.num_envs,
      buffer_size=args.get("buffer_size", 1024),
      n_obs=actor_obs_dim,
      n_act=n_act,
      n_critic_obs=critic_obs_dim,
      n_steps=args.get("num_steps", 1),
      gamma=args.get("gamma", 0.97),
      device=device,
    )

    self.policy = self.actor.explore
    print(f"[FastSAC] actor_obs_dim={actor_obs_dim}, critic_obs_dim={critic_obs_dim}, n_act={n_act}")
    print(self.actor)
    print(self.qnet)

  @contextmanager
  def _maybe_amp(self):
    amp_dtype = (
      torch.bfloat16
      if self.alg_cfg.get("amp_dtype", "bf16") == "bf16"
      else torch.float16
    )
    with autocast(
      device_type="cuda" if str(self.device).startswith("cuda") else "cpu",
      dtype=amp_dtype,
      enabled=bool(self.alg_cfg.get("amp", True)) and str(self.device).startswith("cuda"),
    ):
      yield

  def add_git_repo_to_log(self, _file: str) -> None:
    """No-op for API compatibility with OnPolicyRunner."""

  def _update_main(self, data: TensorDict):
    args = self.alg_cfg
    with self._maybe_amp():
      next_observations = data["next"]["observations"]
      critic_observations = data["critic_observations"]
      next_critic_observations = data["next"]["critic_observations"]
      actions = data["actions"]
      rewards = data["next"]["rewards"]
      dones = data["next"]["dones"].bool()
      truncations = data["next"]["truncations"].bool()
      bootstrap = (truncations | ~dones).float()

      with torch.no_grad():
        next_state_actions, next_state_log_probs = self.actor.get_actions_and_log_probs(
          next_observations
        )
        discount = args["gamma"] ** data["next"]["effective_n_steps"]
        target_distributions = self.qnet_target.projection(
          next_critic_observations,
          next_state_actions,
          rewards - discount * bootstrap * self.log_alpha.exp() * next_state_log_probs,
          bootstrap,
          discount,
        )
        target_values = self.qnet_target.get_value(target_distributions)
        target_value_max = target_values.max()
        target_value_min = target_values.min()

      q_outputs = self.qnet(critic_observations, actions)
      critic_log_probs = F.log_softmax(q_outputs, dim=-1)
      critic_losses = -torch.sum(target_distributions * critic_log_probs, dim=-1)
      qf_loss = critic_losses.mean(dim=1).sum(dim=0)

    self.q_optimizer.zero_grad(set_to_none=True)
    self.scaler.scale(qf_loss).backward()
    self.scaler.unscale_(self.q_optimizer)
    max_grad = args.get("max_grad_norm", 0.0)
    if max_grad > 0:
      critic_grad_norm = torch.nn.utils.clip_grad_norm_(
        self.qnet.parameters(), max_norm=max_grad
      )
    else:
      critic_grad_norm = torch.tensor(0.0, device=self.device)
    self.scaler.step(self.q_optimizer)
    self.scaler.update()

    alpha_loss = torch.tensor(0.0, device=self.device)
    if args.get("use_autotune", True):
      self.alpha_optimizer.zero_grad(set_to_none=True)
      with self._maybe_amp():
        alpha_loss = (
          -self.log_alpha.exp() * (next_state_log_probs.detach() + self.target_entropy)
        ).mean()
      self.scaler.scale(alpha_loss).backward()
      self.scaler.unscale_(self.alpha_optimizer)
      self.scaler.step(self.alpha_optimizer)
      self.scaler.update()

    return (
      rewards.mean(),
      critic_grad_norm.detach(),
      qf_loss.detach(),
      target_value_max.detach(),
      target_value_min.detach(),
      alpha_loss.detach(),
    )

  def _update_pol(self, data: TensorDict):
    args = self.alg_cfg
    with self._maybe_amp():
      critic_observations = data["critic_observations"]
      actions, log_probs = self.actor.get_actions_and_log_probs(data["observations"])
      with torch.no_grad():
        _, _, log_std = self.actor(data["observations"])
        action_std = log_std.exp().mean()
        policy_entropy = -log_probs.mean()

      q_outputs = self.qnet(critic_observations, actions)
      q_probs = F.softmax(q_outputs, dim=-1)
      q_values = self.qnet.get_value(q_probs)
      qf_value = q_values.mean(dim=0)
      actor_loss = (self.log_alpha.exp().detach() * log_probs - qf_value).mean()

    self.actor_optimizer.zero_grad(set_to_none=True)
    self.scaler.scale(actor_loss).backward()
    self.scaler.unscale_(self.actor_optimizer)
    max_grad = args.get("max_grad_norm", 0.0)
    if max_grad > 0:
      actor_grad_norm = torch.nn.utils.clip_grad_norm_(
        self.actor.parameters(), max_norm=max_grad
      )
    else:
      actor_grad_norm = torch.tensor(0.0, device=self.device)
    self.scaler.step(self.actor_optimizer)
    self.scaler.update()
    return (
      actor_grad_norm.detach(),
      actor_loss.detach(),
      policy_entropy.detach(),
      action_std.detach(),
    )

  def _sample_and_prepare_batches(
    self, batch_size: int, num_updates: int, normalize_obs, normalize_critic_obs
  ) -> list[TensorDict]:
    large_data = self.rb.sample(batch_size * num_updates)
    samples_per_update = batch_size * self.env.num_envs

    large_data["observations"] = normalize_obs(large_data["observations"])
    large_data["next"]["observations"] = normalize_obs(
      large_data["next"]["observations"]
    )
    large_data["critic_observations"] = normalize_critic_obs(
      large_data["critic_observations"]
    )
    large_data["next"]["critic_observations"] = normalize_critic_obs(
      large_data["next"]["critic_observations"]
    )

    prepared = []
    for i in range(num_updates):
      start = i * samples_per_update
      end = (i + 1) * samples_per_update
      batch = TensorDict(
        {
          "observations": large_data["observations"][start:end],
          "actions": large_data["actions"][start:end],
          "next": {
            "rewards": large_data["next"]["rewards"][start:end],
            "dones": large_data["next"]["dones"][start:end],
            "truncations": large_data["next"]["truncations"][start:end],
            "observations": large_data["next"]["observations"][start:end],
            "effective_n_steps": large_data["next"]["effective_n_steps"][start:end],
          },
          "critic_observations": large_data["critic_observations"][start:end],
        },
        batch_size=samples_per_update,
      )
      batch["next"]["critic_observations"] = large_data["next"]["critic_observations"][
        start:end
      ]
      prepared.append(batch)
    return prepared

  def learn(
    self,
    num_learning_iterations: int,
    init_at_random_ep_len: bool = False,
  ) -> None:
    args = self.alg_cfg
    if init_at_random_ep_len:
      self.env.episode_length_buf = torch.randint_like(
        self.env.episode_length_buf, high=int(self.env.max_episode_length)
      )

    if args.get("compile", False):
      update_main = torch.compile(self._update_main)
      update_pol = torch.compile(self._update_pol)
      policy = torch.compile(self.policy)
      normalize_obs = torch.compile(self.obs_normalizer.forward)
      normalize_critic_obs = torch.compile(self.critic_obs_normalizer.forward)
    else:
      update_main = self._update_main
      update_pol = self._update_pol
      policy = self.policy
      normalize_obs = self.obs_normalizer.forward
      normalize_critic_obs = self.critic_obs_normalizer.forward

    obs, critic_obs = self.env.reset_with_obs()
    dones = None
    policy_entropy = torch.tensor(0.0, device=self.device)
    action_std = torch.tensor(0.0, device=self.device)
    actor_loss = torch.tensor(0.0, device=self.device)
    actor_grad_norm = torch.tensor(0.0, device=self.device)

    metric_sums: dict[str, float] = defaultdict(float)
    metric_counts: dict[str, int] = defaultdict(int)
    ep_rew_sum = torch.zeros(self.env.num_envs, device=self.device)
    ep_len_sum = torch.zeros(self.env.num_envs, device=self.device)
    completed_ep_rews: list[float] = []
    completed_ep_lens: list[float] = []

    start_step = self.global_step
    total_steps = start_step + num_learning_iterations
    t0 = time.time()
    collection_time = 0.0
    learn_time = 0.0

    while self.global_step <= total_steps:
      t_collect = time.time()
      with torch.no_grad(), self._maybe_amp():
        norm_obs = normalize_obs(obs, update=False)
        actions = policy(obs=norm_obs, dones=dones)

      next_obs, rewards, dones, truncations, infos = self.env.step(actions.float())
      next_critic_obs = infos["observations"]["critic"]

      ep_rew_sum += rewards
      ep_len_sum += 1
      done_mask = dones.bool()
      if done_mask.any():
        completed_ep_rews.extend(ep_rew_sum[done_mask].detach().cpu().tolist())
        completed_ep_lens.extend(ep_len_sum[done_mask].detach().cpu().tolist())
        ep_rew_sum[done_mask] = 0.0
        ep_len_sum[done_mask] = 0.0

      true_next_obs = torch.where(
        truncations[:, None] > 0,
        infos["observations"]["final"]["actor_obs"],
        next_obs,
      )
      true_next_critic_obs = torch.where(
        truncations[:, None] > 0,
        infos["observations"]["final"]["critic_obs"],
        next_critic_obs,
      )

      transition = TensorDict(
        {
          "observations": obs,
          "actions": actions.float(),
          "next": {
            "observations": true_next_obs,
            "rewards": rewards.float(),
            "truncations": truncations.long(),
            "dones": dones.long(),
          },
        },
        batch_size=(self.env.num_envs,),
        device=self.device,
      )
      transition["critic_observations"] = critic_obs
      transition["next"]["critic_observations"] = true_next_critic_obs
      self.rb.extend(transition)

      obs = next_obs
      critic_obs = next_critic_obs
      collection_time += time.time() - t_collect

      batch_size = max(
        args.get("batch_size", 8192) // self.env.num_envs // self.gpu_world_size, 1
      )
      if self.global_step > args.get("learning_starts", 10):
        t_learn = time.time()
        prepared = self._sample_and_prepare_batches(
          batch_size,
          args.get("num_updates", 8),
          normalize_obs,
          normalize_critic_obs,
        )
        num_updates = args.get("num_updates", 8)
        policy_frequency = args.get("policy_frequency", 4)
        for i, data in enumerate(prepared):
          (
            buffer_rewards,
            critic_grad_norm,
            qf_loss,
            qf_max,
            qf_min,
            alpha_loss,
          ) = update_main(data)
          if num_updates > 1:
            if i % policy_frequency == 1:
              actor_grad_norm, actor_loss, policy_entropy, action_std = update_pol(data)
          elif self.global_step % policy_frequency == 0:
            actor_grad_norm, actor_loss, policy_entropy, action_std = update_pol(data)

          for key, value in {
            "actor_loss": actor_loss,
            "qf_loss": qf_loss,
            "qf_max": qf_max,
            "qf_min": qf_min,
            "actor_grad_norm": actor_grad_norm,
            "critic_grad_norm": critic_grad_norm,
            "buffer_rewards": buffer_rewards,
            "alpha_loss": alpha_loss,
            "alpha_value": self.log_alpha.exp().detach().mean(),
            "policy_entropy": policy_entropy,
            "action_std": action_std,
          }.items():
            metric_sums[key] += float(value.detach().item())
            metric_counts[key] += 1

          with torch.no_grad():
            src_ps = [p.data for p in self.qnet.parameters()]
            tgt_ps = [p.data for p in self.qnet_target.parameters()]
            torch._foreach_mul_(tgt_ps, 1.0 - args.get("tau", 0.125))
            torch._foreach_add_(tgt_ps, src_ps, alpha=args.get("tau", 0.125))
        learn_time += time.time() - t_learn

        log_interval = args.get("logging_interval", 100)
        if self.global_step % log_interval == 0 and self.is_main_process:
          loss_dict = {
            k: metric_sums[k] / max(metric_counts[k], 1) for k in metric_sums
          }
          metric_sums.clear()
          metric_counts.clear()
          loss_dict["env_rewards"] = float(rewards.mean().item())
          if completed_ep_rews:
            loss_dict["episode_reward"] = sum(completed_ep_rews) / len(completed_ep_rews)
            loss_dict["episode_length"] = sum(completed_ep_lens) / len(completed_ep_lens)
            completed_ep_rews.clear()
            completed_ep_lens.clear()

          elapsed = max(time.time() - t0, 1e-6)
          fps = (self.global_step - start_step + 1) * self.env.num_envs / elapsed
          print(
            f"[FastSAC] step={self.global_step} "
            f"rew={loss_dict.get('episode_reward', loss_dict['env_rewards']):.3f} "
            f"qf={loss_dict.get('qf_loss', 0):.4f} "
            f"actor={loss_dict.get('actor_loss', 0):.4f} "
            f"alpha={loss_dict.get('alpha_value', 0):.4f} "
            f"fps={fps:.0f}",
            flush=True,
          )
          if self.writer is not None:
            for k, v in loss_dict.items():
              self.writer.add_scalar(f"Train/{k}", v, self.global_step)
            self.writer.add_scalar("Train/fps", fps, self.global_step)
            self.writer.add_scalar(
              "Train/collection_time", collection_time, self.global_step
            )
            self.writer.add_scalar("Train/learn_time", learn_time, self.global_step)
            # Also log episode extras if present.
            if "log" in infos:
              for k, v in infos["log"].items():
                if isinstance(v, torch.Tensor):
                  self.writer.add_scalar(f"Episode/{k}", v.item(), self.global_step)

        save_interval = self.cfg.get("save_interval", 1000)
        if (
          save_interval > 0
          and self.global_step > 0
          and self.global_step % save_interval == 0
          and self.is_main_process
          and self.log_dir is not None
        ):
          path = os.path.join(self.log_dir, f"model_{self.global_step}.pt")
          self.save(path)

      if self.global_step >= total_steps:
        break
      self.global_step += 1
      self.current_learning_iteration = self.global_step

    if self.is_main_process and self.log_dir is not None:
      self.save(os.path.join(self.log_dir, f"model_{self.global_step}.pt"))

  def save(self, path: str, infos: dict | None = None) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    env_state = {"common_step_counter": self.env.unwrapped.common_step_counter}
    save_dict: dict[str, Any] = {
      "actor_state_dict": _cpu_state(self.actor.state_dict()),
      "qnet_state_dict": _cpu_state(self.qnet.state_dict()),
      "qnet_target_state_dict": _cpu_state(self.qnet_target.state_dict()),
      "log_alpha": self.log_alpha.detach().cpu(),
      "obs_normalizer_state": _cpu_state(self.obs_normalizer.state_dict())
      if hasattr(self.obs_normalizer, "state_dict")
      else None,
      "critic_obs_normalizer_state": _cpu_state(self.critic_obs_normalizer.state_dict())
      if hasattr(self.critic_obs_normalizer, "state_dict")
      else None,
      "actor_optimizer_state_dict": self.actor_optimizer.state_dict(),
      "q_optimizer_state_dict": self.q_optimizer.state_dict(),
      "alpha_optimizer_state_dict": self.alpha_optimizer.state_dict(),
      "grad_scaler_state_dict": self.scaler.state_dict(),
      "args": self.alg_cfg,
      "global_step": self.global_step,
      "iter": self.global_step,
      "infos": {**(infos or {}), "env_state": env_state},
    }
    torch.save(save_dict, path)
    print(f"[FastSAC] Saved checkpoint to {path}")

    if self.cfg.get("upload_model", True):
      try:
        import wandb

        if wandb.run is not None:
          wandb.save(path, base_path=str(Path(path).parent))
      except Exception:
        pass

  def load(
    self,
    path: str,
    load_cfg: dict | None = None,
    strict: bool = True,
    map_location: str | None = None,
  ) -> dict:
    del load_cfg
    loaded = torch.load(
      path, map_location=map_location or self.device, weights_only=False
    )
    self.actor.load_state_dict(loaded["actor_state_dict"], strict=strict)
    if "qnet_state_dict" in loaded:
      self.qnet.load_state_dict(loaded["qnet_state_dict"], strict=strict)
      self.qnet_target.load_state_dict(
        loaded["qnet_target_state_dict"], strict=strict
      )
    if loaded.get("obs_normalizer_state") is not None and hasattr(
      self.obs_normalizer, "load_state_dict"
    ):
      self.obs_normalizer.load_state_dict(loaded["obs_normalizer_state"])
    if loaded.get("critic_obs_normalizer_state") is not None and hasattr(
      self.critic_obs_normalizer, "load_state_dict"
    ):
      self.critic_obs_normalizer.load_state_dict(
        loaded["critic_obs_normalizer_state"]
      )
    if "log_alpha" in loaded:
      self.log_alpha.data.copy_(loaded["log_alpha"].to(self.device))
    if "actor_optimizer_state_dict" in loaded:
      self.actor_optimizer.load_state_dict(loaded["actor_optimizer_state_dict"])
    if "q_optimizer_state_dict" in loaded:
      self.q_optimizer.load_state_dict(loaded["q_optimizer_state_dict"])
    if "alpha_optimizer_state_dict" in loaded:
      self.alpha_optimizer.load_state_dict(loaded["alpha_optimizer_state_dict"])
    if loaded.get("grad_scaler_state_dict") is not None:
      self.scaler.load_state_dict(loaded["grad_scaler_state_dict"])
    self.global_step = int(loaded.get("global_step", loaded.get("iter", 0)))
    self.current_learning_iteration = self.global_step

    infos = loaded.get("infos") or {}
    if "env_state" in infos:
      self.env.unwrapped.common_step_counter = infos["env_state"]["common_step_counter"]
    return infos

  def get_inference_policy(self, device: str | None = None) -> _InferencePolicy:
    if device is not None:
      self.actor.to(device)
      if hasattr(self.obs_normalizer, "to"):
        self.obs_normalizer.to(device)
    self.actor.eval()
    return _InferencePolicy(
      self.actor,
      self.obs_normalizer,
      self.actor_obs_key,
      self.obs_groups,
    )

  def export_policy_to_onnx(
    self, path: str, filename: str = "policy.onnx", verbose: bool = False
  ) -> None:
    """Export deterministic tanh-mean actor (with obs normalizer) to ONNX.

    Uses deep copies so ``.to("cpu")`` does not move the live training modules.
    """
    import copy

    os.makedirs(path, exist_ok=True)
    actor_obs_dim = self.actor.n_obs

    class _OnnxActor(torch.nn.Module):
      def __init__(self, obs_normalizer: torch.nn.Module, actor: Actor):
        super().__init__()
        self.obs_normalizer = obs_normalizer
        self.actor = actor

      def forward(self, obs: torch.Tensor) -> torch.Tensor:
        if hasattr(self.obs_normalizer, "forward"):
          try:
            obs = self.obs_normalizer(obs, update=False)
          except TypeError:
            obs = self.obs_normalizer(obs)
        action, _, _ = self.actor(obs)
        return action

    model = _OnnxActor(
      copy.deepcopy(self.obs_normalizer),
      copy.deepcopy(self.actor),
    ).to("cpu").eval()
    dummy = torch.zeros(1, actor_obs_dim)
    torch.onnx.export(
      model,
      dummy,
      os.path.join(path, filename),
      export_params=True,
      opset_version=18,
      verbose=verbose,
      input_names=["obs"],
      output_names=["actions"],
      dynamic_axes={},
      dynamo=False,
    )

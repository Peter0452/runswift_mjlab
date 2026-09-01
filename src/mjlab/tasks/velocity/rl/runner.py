from __future__ import annotations

import os
import statistics
import time

import torch
import wandb
from rsl_rl.utils import check_nan

from mjlab.rl import RslRlVecEnvWrapper
from mjlab.rl.exporter_utils import (
  attach_metadata_to_onnx,
  get_base_metadata,
)
from mjlab.rl.runner import MjlabOnPolicyRunner


def _patch_gaussian_std_nan_guard() -> None:
  """Keep Gaussian std finite/non-negative so PPO sampling cannot crash.

  Adaptive LR and long FT can push scalar ``std_param`` to NaN; ``clamp`` does
  not repair NaN, and ``torch.normal`` then raises. Idempotent.
  """
  from rsl_rl.modules.distribution import GaussianDistribution
  from torch.distributions import Normal

  if getattr(GaussianDistribution.update, "_mjlab_nan_guard", False):
    return

  _orig_update = GaussianDistribution.update

  def _safe_update(self, mlp_output: torch.Tensor) -> None:
    if self.std_type == "scalar" and hasattr(self, "std_param"):
      with torch.no_grad():
        self.std_param.data.nan_to_num_(nan=0.5, posinf=1.0, neginf=1e-3)
        lo, hi = float(self.std_range[0]), float(self.std_range[1])
        self.std_param.data.clamp_(lo, hi)
    _orig_update(self, mlp_output)
    # Belt-and-suspenders: rebuild Normal if scale still non-finite.
    dist = self._distribution
    if dist is not None and not torch.isfinite(dist.scale).all():
      scale = torch.nan_to_num(dist.scale, nan=0.5, posinf=1.0, neginf=1e-3)
      scale = scale.clamp(min=1e-6)
      self._distribution = Normal(dist.loc, scale)

  _safe_update._mjlab_nan_guard = True  # type: ignore[attr-defined]
  GaussianDistribution.update = _safe_update  # type: ignore[method-assign]


_RH_PENALTY_PER_1K = 100.0
"""Score cost per root-height termination per 1000 env steps.

Calibrated so a typical sink rate (~0.3 per 1000 steps) costs ~30 points against
a ~390 point episode-length term, i.e. it discriminates without dominating.
"""


class VelocityOnPolicyRunner(MjlabOnPolicyRunner):
  env: RslRlVecEnvWrapper

  def __init__(self, *args, **kwargs):
    _patch_gaussian_std_nan_guard()
    super().__init__(*args, **kwargs)
    self._best_eval_score = float("-inf")
    self._best_eval_iter = -1
    self._best_roll_ep_len = 0.0
    self._early_stop_counter = 0

  def save(self, path: str, infos=None):
    super().save(path, infos)
    policy_dir, filename, onnx_path = self._get_export_paths(path)
    try:
      self.export_policy_to_onnx(str(policy_dir), filename)
      run_name: str = (
        wandb.run.name
        if self.logger.logger_type in ("wandb", "WandbLogWriter") and wandb.run
        else "local"
      )  # type: ignore[assignment]
      metadata = get_base_metadata(self.env.unwrapped, run_name)
      attach_metadata_to_onnx(str(onnx_path), metadata)
      if (
        self.logger.logger_type in ("wandb", "WandbLogWriter")
        and self.cfg["upload_model"]
      ):
        wandb.save(str(onnx_path), base_path=str(policy_dir))
    except Exception as e:
      print(f"[WARN] ONNX export failed (training continues): {e}")

  @torch.inference_mode()
  def _eval_policy_score(self) -> tuple[float, float, float, float]:
    """Deterministic eval rollout; returns (score, mean_len, mean_rew, rh_per_1k).

    The root-height cost is a *rate* (kills per 1000 env steps), not a fraction
    of terminations. The old ``rh_rate`` form had two defects: it moved whenever
    any other termination cause changed, and since ``rh_rate ~= rh_per_step *
    mean_len`` the penalty scaled with ``mean_len**2``, punishing longer-surviving
    policies for an unchanged sink rate. Together those made run-to-run noise in
    the ratio worth more score than real policy differences. Scores are therefore
    not comparable with runs logged before this change.
    """
    policy = self.alg.get_policy()
    policy.eval()
    unwrapped = self.env.unwrapped

    obs = self.env.get_observations().to(self.device)
    num_steps = int(self.cfg.get("eval_steps", 240))
    cur_rew = torch.zeros(self.env.num_envs, dtype=torch.float, device=self.device)
    cur_len = torch.zeros(self.env.num_envs, dtype=torch.float, device=self.device)
    completed_rewards: list[float] = []
    completed_lengths: list[float] = []
    root_height_kills = 0
    total_completions = 0

    has_rh_term = "root_height" in unwrapped.termination_manager.active_terms

    for _ in range(num_steps):
      actions = policy(obs)
      obs, rewards, dones, extras = self.env.step(actions.to(self.env.device))
      if self.cfg.get("check_for_nan", True):
        check_nan(obs, rewards, dones)
      obs = obs.to(self.device)
      rewards = rewards.to(self.device)
      dones = dones.to(self.device)

      cur_rew += rewards.view(-1)
      cur_len += 1.0
      done_ids = (dones > 0).nonzero(as_tuple=False).view(-1)
      if done_ids.numel() > 0:
        if has_rh_term:
          rh = unwrapped.termination_manager.get_term("root_height")
          root_height_kills += int(rh[done_ids].sum().item())
        total_completions += int(done_ids.numel())
        completed_rewards.extend(cur_rew[done_ids].cpu().tolist())
        completed_lengths.extend(cur_len[done_ids].cpu().tolist())
        cur_rew[done_ids] = 0.0
        cur_len[done_ids] = 0.0

    if completed_lengths:
      mean_len = float(statistics.mean(completed_lengths))
      mean_rew = float(statistics.mean(completed_rewards))
    elif len(self.logger.lenbuffer) > 0:
      mean_len = float(statistics.mean(self.logger.lenbuffer))
      mean_rew = float(statistics.mean(self.logger.rewbuffer))
    else:
      mean_len = 0.0
      mean_rew = 0.0

    total_env_steps = max(1, num_steps * self.env.num_envs)
    rh_per_1k = 1000.0 * float(root_height_kills) / float(total_env_steps)
    score = 0.6 * mean_len + 0.3 * mean_rew - _RH_PENALTY_PER_1K * rh_per_1k
    return score, mean_len, mean_rew, rh_per_1k

  def _maybe_eval_and_save_best(self, it: int) -> None:
    eval_interval = int(self.cfg.get("eval_interval", 0))
    if eval_interval <= 0 or it <= 0 or it % eval_interval != 0:
      return
    if self.logger.writer is None:
      return

    score, mean_len, mean_rew, rh_per_1k = self._eval_policy_score()
    self.logger.writer.add_scalar("Eval/score", score, it)
    self.logger.writer.add_scalar("Eval/mean_episode_length", mean_len, it)
    self.logger.writer.add_scalar("Eval/mean_reward", mean_rew, it)
    self.logger.writer.add_scalar("Eval/root_height_per_1k", rh_per_1k, it)

    if score > self._best_eval_score:
      self._best_eval_score = score
      self._best_eval_iter = it
      best_path = os.path.join(self.logger.log_dir, "model_best.pt")
      self.save(best_path)
      print(
        f"[INFO] New best eval score {score:.2f} at iter {it} "
        f"(len={mean_len:.1f}, rew={mean_rew:.2f}, rh/1k={rh_per_1k:.3f})"
        f" -> {best_path}"
      )
      self.logger.writer.add_scalar("Eval/best_score", score, it)

    self.alg.train_mode()

  def _maybe_early_stop(self, it: int, start_it: int) -> bool:
    if not self.cfg.get("early_stop_enabled", False):
      return False
    if len(self.logger.lenbuffer) < 10:
      return False
    if it < start_it + int(self.cfg.get("early_stop_min_iters", 200)):
      return False
    # Wait until at least one eval *after* resume so model_best can move.
    eval_interval = int(self.cfg.get("eval_interval", 0))
    if eval_interval > 0 and it < start_it + eval_interval:
      return False

    cur_len = float(statistics.mean(self.logger.lenbuffer))
    if cur_len > self._best_roll_ep_len:
      self._best_roll_ep_len = cur_len
      self._early_stop_counter = 0
      return False

    drop = float(self.cfg.get("early_stop_drop_fraction", 0.15))
    threshold = self._best_roll_ep_len * (1.0 - drop)
    if cur_len < threshold:
      self._early_stop_counter += 1
    else:
      self._early_stop_counter = 0

    patience = int(self.cfg.get("early_stop_patience", 50))
    if self._early_stop_counter >= patience:
      print(
        f"[INFO] Early stop at iter {it}: rolling ep length {cur_len:.1f} "
        f"< {threshold:.1f} ({drop:.0%} below best {self._best_roll_ep_len:.1f})"
      )
      return True
    return False

  def learn(
    self, num_learning_iterations: int, init_at_random_ep_len: bool = False
  ) -> None:
    """On-policy learning with eval-based best checkpoint and optional early stop."""
    if init_at_random_ep_len:
      self.env.episode_length_buf = torch.randint_like(
        self.env.episode_length_buf, high=int(self.env.max_episode_length)
      )

    obs = self.env.get_observations().to(self.device)
    self.alg.train_mode()

    if self.is_distributed:
      print(f"Synchronizing parameters for rank {self.gpu_global_rank}...")
      self.alg.broadcast_parameters()

    self.logger.init_logging_writer()

    start_it = self.current_learning_iteration
    total_it = start_it + num_learning_iterations
    for it in range(start_it, total_it):
      start = time.time()
      with torch.inference_mode():
        for _ in range(self.cfg["num_steps_per_env"]):
          actions = self.alg.act(obs)
          obs, rewards, dones, extras = self.env.step(actions.to(self.env.device))
          if self.cfg.get("check_for_nan", True):
            check_nan(obs, rewards, dones)
          obs, rewards, dones = (
            obs.to(self.device),
            rewards.to(self.device),
            dones.to(self.device),
          )
          self.alg.process_env_step(obs, rewards, dones, extras)
          intrinsic_rewards = (
            self.alg.intrinsic_rewards if self.cfg["algorithm"]["rnd_cfg"] else None
          )
          self.logger.process_env_step(rewards, dones, extras, intrinsic_rewards)

        stop = time.time()
        collect_time = stop - start
        start = stop
        self.alg.compute_returns(obs)

      loss_dict = self.alg.update()

      stop = time.time()
      learn_time = stop - start
      self.current_learning_iteration = it

      self.logger.log(
        it=it,
        start_it=start_it,
        total_it=total_it,
        collect_time=collect_time,
        learn_time=learn_time,
        loss_dict=loss_dict,
        learning_rate=self.alg.learning_rate,
        action_std=self.alg.get_policy().output_std,
        rnd_weight=self.alg.rnd.weight if self.cfg["algorithm"]["rnd_cfg"] else None,
      )

      if self.logger.writer is not None and it % self.cfg["save_interval"] == 0:
        self.save(os.path.join(self.logger.log_dir, f"model_{it}.pt"))

      self._maybe_eval_and_save_best(it)

      if self._maybe_early_stop(it, start_it):
        break

    if self.logger.writer is not None:
      self.save(
        os.path.join(self.logger.log_dir, f"model_{self.current_learning_iteration}.pt")
      )
      self.logger.stop_logging_writer()

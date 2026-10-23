"""Anchor a self-play policy to its warm start: β·KL(π_θ ‖ π_ref).

Self-play fine-tuning of the stage-3 kick (h022) drifted away from it and
played worse against it in fixed matches the further it drifted (actor weight
change 22 % / 27 % / 36 % at v6/350, v6/600, v5/1100; goal share vs h022
0.39 → 0.26 → 0.17). The self-play signal is too weak to steer full-size
updates, so they partly random-walk. The anchor adds the analytic KL to a
frozen copy of the warm start on rollout observations: updates that pay
outweigh it, while undirected drift is pulled back (cf. AlphaStar's KL to its
supervised policy).

``AnchoredAmpPPO`` reuses ``AmpPPO``'s imitation hook (an extra loss term on
rollout observations with its own coefficient); teacher recording stays off
because ``imitation_coef`` stays 0. It logs ``Loss/anchor`` (the KL, nats per
sample summed over action dims) and ``Loss/anchor_coef`` (β).

Wiring (runner cfg ``cfg``, e.g. in ``booster_k1_kick_selfplay_runner_cfg``)::

  from mjlab.tasks.velocity.rl.anchor import with_anchor
  cfg.algorithm = with_anchor(
    cfg.algorithm, SELFPLAY_KICK_CKPT, coef=0.5, coef_final=0.1,
    decay_updates=5000,
  )

β falls linearly from ``coef`` to ``coef_final`` over ``decay_updates``
updates (one per iteration). The update count is not checkpointed: a resume
restarts the schedule.
"""

from __future__ import annotations

import copy
import dataclasses
from typing import Any, cast

import torch
from tensordict import TensorDict

from mjlab.amp.algorithms.amp_ppo import AmpPPO
from mjlab.amp.runners.amp_on_policy_runner import AmpRslRlMuonPpoAlgorithmCfg
from mjlab.tasks.velocity.mdp.self_play import pad_input_columns, resolve_checkpoint

ANCHOR_KEYS = (
  "anchor_checkpoint",
  "anchor_coef",
  "anchor_coef_final",
  "anchor_decay_updates",
  "anchor_loss",
)


def gaussian_std(model: Any) -> torch.Tensor:
  """State-independent std of an rsl-rl ``GaussianDistribution`` (clamped)."""
  dist: Any = model.distribution
  lo, hi = dist.std_range
  if getattr(dist, "std_type", "scalar") == "log":
    return torch.exp(dist.log_std_param.clamp(*dist.log_std_range))
  return dist.std_param.clamp(lo, hi)


def model_mean(model: Any, obs: TensorDict) -> torch.Tensor:
  """Deterministic action (the Gaussian mean) without touching the model's
  stored distribution, which the PPO update still reads."""
  latent = model.get_latent(obs)
  return model.distribution.deterministic_output(model.mlp(latent))


def diag_gaussian_kl(
  mu_p: torch.Tensor, std_p: torch.Tensor, mu_q: torch.Tensor, std_q: torch.Tensor
) -> torch.Tensor:
  """KL(p ‖ q) for diagonal Gaussians, summed over the last dim."""
  var_p, var_q = std_p.square(), std_q.square()
  kl = (std_q / std_p).log() + (var_p + (mu_p - mu_q).square()) / (2.0 * var_q) - 0.5
  return kl.sum(dim=-1)


def load_reference(actor: Any, checkpoint: str, device: str) -> Any:
  """Frozen copy of ``actor`` holding ``checkpoint``'s actor, widened to the
  actor's inputs as the self-play warm start widens it."""
  loaded = torch.load(
    str(resolve_checkpoint(checkpoint)), map_location=device, weights_only=False
  )
  sd = loaded["actor_state_dict"]
  if "std" in sd:
    sd["distribution.std_param"] = sd.pop("std")
  if "log_std" in sd:
    sd["distribution.log_std_param"] = sd.pop("log_std")
  in_dim = actor.state_dict()["mlp.0.weight"].shape[1]
  sd = pad_input_columns(sd, in_dim)
  ref = copy.deepcopy(actor)
  ref.load_state_dict(sd, strict=True)
  ref.eval()
  for p in ref.parameters():
    p.requires_grad_(False)
  return ref


class AnchoredAmpPPO(AmpPPO):
  """``AmpPPO`` plus β·KL(π_θ ‖ π_ref) to a frozen reference actor."""

  anchor_ref: Any = None

  @staticmethod
  def construct_algorithm(
    obs: TensorDict, env: Any, cfg: dict, device: str
  ) -> AnchoredAmpPPO:
    anchor = {k: cfg["algorithm"].pop(k) for k in ANCHOR_KEYS if k in cfg["algorithm"]}
    alg = AmpPPO.construct_algorithm(obs, env, cfg, device)
    alg.__class__ = AnchoredAmpPPO
    assert isinstance(alg, AnchoredAmpPPO)
    alg.init_anchor(**anchor)
    return alg

  def init_anchor(
    self,
    anchor_checkpoint: str | None = None,
    anchor_coef: float = 0.0,
    anchor_coef_final: float | None = None,
    anchor_decay_updates: int = 0,
    anchor_loss: str = "kl",
  ) -> None:
    assert anchor_loss in ("kl", "mse"), anchor_loss
    assert self.imitation_coef == 0.0, "anchor reuses the imitation hook"
    self.anchor_coef = float(anchor_coef)
    self.anchor_coef_final = (
      self.anchor_coef if anchor_coef_final is None else float(anchor_coef_final)
    )
    self.anchor_decay_updates = int(anchor_decay_updates)
    self.anchor_loss_kind = anchor_loss
    self.anchor_updates = 0
    self._anchor_sum = torch.zeros(1, device=self.device)
    self._anchor_n = 0
    self.anchor_ref = (
      load_reference(self.actor, anchor_checkpoint, self.device)
      if anchor_checkpoint and self.anchor_coef > 0.0
      else None
    )

  def anchor_coef_eff(self) -> float:
    if self.anchor_ref is None:
      return 0.0
    if self.anchor_decay_updates <= 0:
      return self.anchor_coef
    frac = min(self.anchor_updates / self.anchor_decay_updates, 1.0)
    return self.anchor_coef + frac * (self.anchor_coef_final - self.anchor_coef)

  def anchor_loss(self, obs: TensorDict) -> torch.Tensor:
    """Mean over samples of KL(π_θ ‖ π_ref), or the mean squared mean gap."""
    assert self.anchor_ref is not None
    mu = model_mean(self.actor, obs)
    with torch.no_grad():
      mu_ref = model_mean(self.anchor_ref, obs)
    if self.anchor_loss_kind == "mse":
      return (mu - mu_ref).square().mean()
    std = gaussian_std(self.actor).expand_as(mu)
    std_ref = gaussian_std(self.anchor_ref).expand_as(mu_ref)
    return diag_gaussian_kl(mu, std, mu_ref, std_ref).mean()

  # AmpPPO's imitation hook: called once per mini-batch inside update().

  def imitation_coef_eff(self) -> float:
    return self.anchor_coef_eff()

  def _imitation_loss(self, n: int) -> torch.Tensor | None:
    if self.anchor_ref is None:
      return None
    storage = self.storage
    steps, envs = storage.num_transitions_per_env, storage.num_envs
    i = torch.randint(0, steps, (n,), device=self.device)
    j = torch.randint(0, envs, (n,), device=self.device)
    # Rollout buffers were filled in inference mode: index into new tensors.
    obs = cast(TensorDict, storage.observations[i, j]).clone()
    loss = self.anchor_loss(obs)
    self._anchor_sum += loss.detach()
    self._anchor_n += 1
    return loss

  def update(self) -> dict[str, Any]:
    self._anchor_sum.zero_()
    self._anchor_n = 0
    coef = self.anchor_coef_eff()
    out = super().update()
    if self.anchor_ref is not None:
      # The runner logs out["loss"][k] as Loss/k.
      out["loss"]["anchor"] = (self._anchor_sum / max(self._anchor_n, 1)).item()
      out["loss"]["anchor_coef"] = coef
      self.anchor_updates += 1
    return out


@dataclasses.dataclass
class AnchoredAmpMuonPpoAlgorithmCfg(AmpRslRlMuonPpoAlgorithmCfg):
  """``AmpRslRlMuonPpoAlgorithmCfg`` with the anchor's settings."""

  class_name: str = "mjlab.tasks.velocity.rl.anchor:AnchoredAmpPPO"
  anchor_checkpoint: str | None = None
  anchor_coef: float = 0.0
  anchor_coef_final: float | None = None
  anchor_decay_updates: int = 0
  anchor_loss: str = "kl"


def with_anchor(
  algorithm: AmpRslRlMuonPpoAlgorithmCfg,
  checkpoint: str,
  coef: float,
  coef_final: float | None = None,
  decay_updates: int = 0,
  loss: str = "kl",
) -> AnchoredAmpMuonPpoAlgorithmCfg:
  """The same algorithm settings plus an anchor to ``checkpoint``."""
  fields = {
    f.name: getattr(algorithm, f.name)
    for f in dataclasses.fields(algorithm)
    if f.init and f.name != "class_name"
  }
  return AnchoredAmpMuonPpoAlgorithmCfg(
    **fields,
    anchor_checkpoint=checkpoint,
    anchor_coef=coef,
    anchor_coef_final=coef_final,
    anchor_decay_updates=decay_updates,
    anchor_loss=loss,
  )

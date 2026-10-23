"""AMP runner for 1v1 self-play (``mdp.self_play``).

After every update the opponent's mirror slot gets the learner's actor
weights; every ``snapshot_interval`` iterations a copy joins the opponent pool
and is saved under ``<log_dir>/opponents``.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass

import torch

from k1.tasks.selfplay.mdp.self_play import (
  OpponentPolicyAction,
  pad_input_columns,
  resolve_checkpoint,
)
from k1.tasks.velocity.rl.amp_runner import VelocityAmpOnPolicyRunner
from mjlab.amp.runners import AmpOnPolicyRunnerCfg


@dataclass
class SelfPlayAmpRunnerCfg(AmpOnPolicyRunnerCfg):
  """AMP runner configuration with self-play opponent syncing."""

  class_name: str = "SelfPlayAmpOnPolicyRunner"
  init_checkpoint: str | None = None
  """Warm start (actor, critic, discriminator) when nothing else was loaded,
  e.g. a stage-3 blend outside this experiment's log directory."""
  snapshot_interval: int = 200
  """Iterations between opponent pool snapshots of the learner."""
  opponent_action_name: str = "opponent"


class SelfPlayAmpOnPolicyRunner(VelocityAmpOnPolicyRunner):
  """Keeps the env's frozen opponent in step with the learner."""

  _checkpoint_loaded = False

  def load(
    self,
    path: str,
    load_cfg: dict | None = None,
    strict: bool = True,
    map_location: str | None = None,
  ) -> dict:
    self._checkpoint_loaded = True
    loaded = torch.load(path, map_location=map_location, weights_only=False)
    widened = False
    for key, model in (
      ("actor_state_dict", self.alg.actor),
      ("critic_state_dict", self.alg.critic),
    ):
      weights = model.state_dict()
      if "mlp.0.weight" not in weights:
        continue
      in_dim = weights["mlp.0.weight"].shape[1]
      sd = loaded.get(key)
      if sd is not None and sd["mlp.0.weight"].shape[1] < in_dim:
        loaded[key] = pad_input_columns(sd, in_dim)
        widened = True
    if not widened:
      return super().load(
        path, load_cfg=load_cfg, strict=strict, map_location=map_location
      )
    # A stage-3 checkpoint: the detection inputs start with zero weights.
    print(f"[INFO] Widened {path} to this task's inputs (zero new weights).")
    with tempfile.TemporaryDirectory() as tmp:
      out = os.path.join(tmp, "widened.pt")
      torch.save(loaded, out)
      return super().load(
        out, load_cfg=load_cfg, strict=strict, map_location=map_location
      )

  def _opponent(self) -> OpponentPolicyAction:
    name = self.cfg.get("opponent_action_name", "opponent")
    term = self.env.unwrapped.action_manager.get_term(name)
    assert isinstance(term, OpponentPolicyAction)
    return term

  def _actor_state(self) -> dict[str, torch.Tensor]:
    return self.alg.get_policy().state_dict()

  def _on_learn_start(self) -> None:
    init = self.cfg.get("init_checkpoint")
    if init and not self._checkpoint_loaded:
      path = resolve_checkpoint(init)
      print(f"[INFO] Self-play warm start from {path}")
      self.load(str(path), load_cfg={"actor": True, "critic": True})
    self._opponent().set_latest(
      clamp_action_std(self._actor_state(), actor_std_range(self.cfg))
    )

  def _on_policy_update(self, it: int) -> None:
    sync_opponent(
      self._opponent(),
      self._actor_state(),
      it,
      int(self.cfg.get("snapshot_interval", 0)),
      self.logger.log_dir if self.logger.writer is not None else None,
      actor_std_range(self.cfg),
    )


def actor_std_range(cfg: dict) -> tuple[float, float] | None:
  """The actor distribution's ``std_range`` in a runner cfg dict, if any."""
  dist = (cfg.get("actor") or {}).get("distribution_cfg") or {}
  rng = dist.get("std_range")
  return (float(rng[0]), float(rng[1])) if rng is not None else None


def clamp_action_std(
  state: dict[str, torch.Tensor], std_range: tuple[float, float] | None
) -> dict[str, torch.Tensor]:
  """The actor state with its action std clamped as the learner's
  distribution clamps it, so sampled copies explore as the learner does."""
  if std_range is None or "distribution.std_param" not in state:
    return state
  out = dict(state)
  out["distribution.std_param"] = state["distribution.std_param"].clamp(*std_range)
  return out


def sync_opponent(
  opponent: OpponentPolicyAction,
  state: dict[str, torch.Tensor],
  it: int,
  interval: int,
  log_dir: str | None,
  std_range: tuple[float, float] | None = None,
) -> None:
  """Mirror the learner into the opponent after update ``it``; every
  ``interval`` iterations add a snapshot to the pool (and save it)."""
  state = clamp_action_std(state, std_range)
  opponent.set_latest(state)
  if interval <= 0 or (it + 1) % interval != 0:
    return
  name = f"iter_{it + 1}"
  opponent.add_snapshot(state, name)
  if log_dir is not None:
    out = os.path.join(log_dir, "opponents")
    os.makedirs(out, exist_ok=True)
    torch.save(
      {"actor_state_dict": {k: v.cpu() for k, v in state.items()}},
      os.path.join(out, f"{name}.pt"),
    )

"""AMP runner for 1v1 self-play (``mdp.self_play``).

After every update the opponent's mirror slot gets the learner's actor
weights; every ``snapshot_interval`` iterations a copy joins the opponent pool
and is saved under ``<log_dir>/opponents``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import torch

from mjlab.amp.runners import AmpOnPolicyRunnerCfg
from mjlab.tasks.velocity.mdp.self_play import OpponentPolicyAction, resolve_checkpoint
from mjlab.tasks.velocity.rl.amp_runner import VelocityAmpOnPolicyRunner


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
    return super().load(
      path, load_cfg=load_cfg, strict=strict, map_location=map_location
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
    self._opponent().set_latest(self._actor_state())

  def _on_policy_update(self, it: int) -> None:
    opponent = self._opponent()
    state = self._actor_state()
    opponent.set_latest(state)
    interval = int(self.cfg.get("snapshot_interval", 0))
    if interval <= 0 or (it + 1) % interval != 0:
      return
    name = f"iter_{it + 1}"
    opponent.add_snapshot(state, name)
    if self.logger.writer is not None and self.logger.log_dir is not None:
      out = os.path.join(self.logger.log_dir, "opponents")
      os.makedirs(out, exist_ok=True)
      torch.save(
        {"actor_state_dict": {k: v.cpu() for k, v in state.items()}},
        os.path.join(out, f"{name}.pt"),
      )

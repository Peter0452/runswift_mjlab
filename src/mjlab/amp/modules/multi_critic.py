"""One actor, several critic heads, as in APEX.

Each head learns the value of one reward group. Advantages are normalized
per group, then mixed with fixed weights. The actor sees only that mix.
"""

from __future__ import annotations

import torch
import torch.nn as nn
from rsl_rl.models import MLPModel
from rsl_rl.modules import HiddenState
from tensordict import TensorDict


class MultiCritic(nn.Module):
  """Independent critic MLPs that share nothing but the observation."""

  is_recurrent: bool = False

  def __init__(self, critics: list[MLPModel]) -> None:
    super().__init__()
    if len(critics) < 2:
      raise ValueError(f"MultiCritic needs at least 2 heads, got {len(critics)}")
    self.critics = nn.ModuleList(critics)

  def forward(
    self,
    obs: TensorDict,
    masks: torch.Tensor | None = None,
    hidden_state: HiddenState = None,
    stochastic_output: bool = False,
  ) -> torch.Tensor:
    del stochastic_output
    values = [
      critic(obs, masks=masks, hidden_state=hidden_state) for critic in self.critics
    ]
    return torch.cat(values, dim=-1)

  def update_normalization(self, obs: TensorDict) -> None:
    for critic in self.critics:
      critic.update_normalization(obs)

  def reset(
    self, dones: torch.Tensor | None = None, hidden_state: HiddenState = None
  ) -> None:
    for critic in self.critics:
      critic.reset(dones=dones, hidden_state=hidden_state)

  def get_hidden_state(self) -> HiddenState:
    return None

  def detach_hidden_state(self, dones: torch.Tensor | None = None) -> None:
    del dones


def mix_group_advantages(
  returns: torch.Tensor,
  values: torch.Tensor,
  alphas: tuple[float, ...],
) -> torch.Tensor:
  """Normalize each group's advantage, then sum with ``alphas``.

  ``returns`` and ``values`` have shape ``(T, N, G)``. The result has shape
  ``(T, N, 1)`` and is what the PPO surrogate consumes.
  """
  if returns.shape != values.shape:
    raise ValueError(
      f"returns shape {tuple(returns.shape)} != values shape {tuple(values.shape)}"
    )
  if returns.shape[-1] != len(alphas):
    raise ValueError(
      f"expected {len(alphas)} reward groups, got {returns.shape[-1]}"
    )
  mixed = torch.zeros(
    returns.shape[0], returns.shape[1], 1, device=returns.device, dtype=returns.dtype
  )
  for group, alpha in enumerate(alphas):
    advantage = returns[:, :, group] - values[:, :, group]
    advantage = (advantage - advantage.mean()) / (advantage.std() + 1.0e-8)
    mixed[:, :, 0] = mixed[:, :, 0] + float(alpha) * advantage
  return mixed

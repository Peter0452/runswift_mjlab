"""A kick-loop actor as a frozen teacher for the dribble's kick mode (v23).

Kick-loop (stage 3) and dribble policies share the 83 inputs and 22 actions,
and a dribble kick window shows slots 80-82 = (0, 0, 1), the kick loop's "long
kick" one-hot, with the kick direction in slots 78-79 as the kick loop has it.
So the kick-loop actor, given the dribble's kick-window observations, does a
long kick along the commanded direction; AmpPPO imitates its leg actions there
(``record_teacher`` / ``imitation_coef``).
"""

from __future__ import annotations

import torch
from torch import nn


class KickLoopTeacher(nn.Module):
  """Deterministic mean action of a saved kick-loop actor (obs normalizer and
  ELU MLP), evaluated on the GPU for all envs at once."""

  def __init__(self, checkpoint: str, device: torch.device | str) -> None:
    super().__init__()
    sd = torch.load(checkpoint, map_location="cpu", weights_only=False)[
      "actor_state_dict"
    ]
    self.register_buffer("mean", sd["obs_normalizer._mean"].float())
    self.register_buffer("std", sd["obs_normalizer._std"].float())
    linears = sorted(
      int(k.split(".")[1]) for k in sd if k.startswith("mlp.") and k.endswith(".weight")
    )
    layers: list[nn.Module] = []
    for i, idx in enumerate(linears):
      w = sd[f"mlp.{idx}.weight"]
      lin = nn.Linear(w.shape[1], w.shape[0])
      lin.weight.data.copy_(w)
      lin.bias.data.copy_(sd[f"mlp.{idx}.bias"])
      layers.append(lin)
      if i < len(linears) - 1:
        layers.append(nn.ELU())
    self.mlp = nn.Sequential(*layers)
    self.to(device)
    self.eval()

  @torch.no_grad()
  def forward(self, obs: torch.Tensor) -> torch.Tensor:
    return self.mlp((obs - self.mean) / (self.std + NORMALIZER_EPS))


NORMALIZER_EPS = 1.0e-2
"""rsl_rl EmpiricalNormalization: (x - mean) / (std + eps), eps 1e-2."""

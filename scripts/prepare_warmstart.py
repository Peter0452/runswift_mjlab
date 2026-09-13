#!/usr/bin/env python3
"""Create a fresh-optimizer warm-start checkpoint from an rsl_rl checkpoint."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch


def _first_linear_weight_key(state_dict: dict[str, torch.Tensor]) -> str:
  if "mlp.0.weight" in state_dict:
    return "mlp.0.weight"
  for key in sorted(state_dict):
    if key.endswith(".weight"):
      return key
  raise KeyError("No linear weight found in state dict")


def _pad_obs_vector(
  tensor: torch.Tensor,
  target_obs_dim: int,
  *,
  fill: float,
) -> torch.Tensor:
  if tensor.ndim != 2 or tensor.shape[0] != 1:
    raise ValueError(
      f"Expected obs normalizer tensor [1, obs], got {tuple(tensor.shape)}"
    )
  current_obs_dim = tensor.shape[1]
  if current_obs_dim == target_obs_dim:
    return tensor.clone()
  if current_obs_dim > target_obs_dim:
    raise ValueError(
      f"Cannot pad obs vector: current dim {current_obs_dim} > target {target_obs_dim}"
    )
  padded = torch.full(
    (1, target_obs_dim),
    fill,
    dtype=tensor.dtype,
    device=tensor.device,
  )
  padded[:, :current_obs_dim] = tensor
  return padded


def pad_state_dict_obs_dim(
  state_dict: dict[str, torch.Tensor],
  target_obs_dim: int,
) -> dict[str, torch.Tensor]:
  """Pad first MLP input and obs normalizer stats to ``target_obs_dim``."""
  out = {k: v.clone() if torch.is_tensor(v) else v for k, v in state_dict.items()}
  key = _first_linear_weight_key(out)
  weight = out[key]
  if weight.ndim != 2:
    raise ValueError(f"Expected 2-D weight at {key}, got shape {tuple(weight.shape)}")
  current_obs_dim = weight.shape[1]
  if current_obs_dim > target_obs_dim:
    raise ValueError(
      f"Cannot pad {key}: current obs dim {current_obs_dim} > target {target_obs_dim}"
    )
  if current_obs_dim != target_obs_dim:
    padded = torch.zeros(weight.shape[0], target_obs_dim, dtype=weight.dtype)
    padded[:, :current_obs_dim] = weight
    out[key] = padded

  normalizer_defaults = {
    "obs_normalizer._mean": 0.0,
    "obs_normalizer._var": 1.0,
    "obs_normalizer._std": 1.0,
  }
  for norm_key, fill in normalizer_defaults.items():
    if norm_key not in out:
      continue
    out[norm_key] = _pad_obs_vector(out[norm_key], target_obs_dim, fill=fill)
  return out


def pad_input_layer(
  state_dict: dict[str, torch.Tensor],
  target_obs_dim: int,
) -> dict[str, torch.Tensor]:
  """Zero-pad the first MLP input layer from ``[H, obs]`` to ``[H, target_obs_dim]``."""
  return pad_state_dict_obs_dim(state_dict, target_obs_dim)


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument("--input", type=Path, required=True)
  parser.add_argument("--output", type=Path, required=True)
  parser.add_argument(
    "--pad-obs-dim",
    type=int,
    default=None,
    help="Zero-pad actor/critic first-layer input to this width (e.g. 75).",
  )
  parser.add_argument(
    "--pad-actor-obs-dim",
    type=int,
    default=None,
    help="Override actor input width when padding (defaults to --pad-obs-dim).",
  )
  parser.add_argument(
    "--pad-critic-obs-dim",
    type=int,
    default=None,
    help="Override critic input width when padding (defaults to --pad-obs-dim).",
  )
  args = parser.parse_args()

  checkpoint = torch.load(args.input, map_location="cpu", weights_only=False)
  actor_sd = dict(checkpoint["actor_state_dict"])
  critic_sd = dict(checkpoint.get("critic_state_dict", {}))

  pad_actor = args.pad_actor_obs_dim or args.pad_obs_dim
  pad_critic = args.pad_critic_obs_dim or args.pad_obs_dim
  if pad_actor is not None:
    actor_sd = pad_state_dict_obs_dim(actor_sd, pad_actor)
  if pad_critic is not None and critic_sd:
    critic_sd = pad_state_dict_obs_dim(critic_sd, pad_critic)

  args.output.parent.mkdir(parents=True, exist_ok=True)
  payload = {
    "actor_state_dict": actor_sd,
    "critic_state_dict": critic_sd,
    "infos": {
      "source": str(args.input),
      "env_state": {"common_step_counter": 0},
      "padded_actor_obs_dim": pad_actor,
      "padded_critic_obs_dim": pad_critic,
    },
  }
  torch.save(payload, args.output)
  if pad_actor is not None:
    key = _first_linear_weight_key(actor_sd)
    print(
      f"Padded actor {key} to obs dim {actor_sd[key].shape[1]} "
      f"(target {pad_actor})"
    )
  if pad_critic is not None and critic_sd:
    key = _first_linear_weight_key(critic_sd)
    print(
      f"Padded critic {key} to obs dim {critic_sd[key].shape[1]} "
      f"(target {pad_critic})"
    )
  print(f"Wrote fresh-optimizer warm start: {args.output}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

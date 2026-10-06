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


def parse_obs_dims(spec: str) -> list[int]:
  """Parse ``"75:83,90"`` into ``[75, ..., 82, 90]`` (end-exclusive slices)."""
  dims: list[int] = []
  for part in spec.split(","):
    part = part.strip()
    if not part:
      continue
    if ":" in part:
      start, end = (int(x) for x in part.split(":"))
      dims.extend(range(start, end))
    else:
      dims.append(int(part))
  return sorted(set(dims))


def reset_state_dict_obs_dims(
  state_dict: dict[str, torch.Tensor],
  dims: list[int],
  normalizer_count: int | None = None,
) -> dict[str, torch.Tensor]:
  """Make ``dims`` start as no-ops: zero their first-layer columns, reset their stats.

  Use for inputs the source run only ever saw as constants (e.g. zero
  placeholders). Their normalizer std is ~0, so new non-zero values would be
  scaled by ~1/eps, and their weights never got a gradient. With the columns
  zeroed the warm-started policy matches the source policy at step 0, and PPO
  grows the weights from there.
  """
  out = {k: v.clone() if torch.is_tensor(v) else v for k, v in state_dict.items()}
  key = _first_linear_weight_key(out)
  obs_dim = out[key].shape[1]
  if dims and max(dims) >= obs_dim:
    raise ValueError(f"Reset dim {max(dims)} out of range for {key} obs dim {obs_dim}")
  out[key][:, dims] = 0.0

  normalizer_defaults = {
    "obs_normalizer._mean": 0.0,
    "obs_normalizer._var": 1.0,
    "obs_normalizer._std": 1.0,
  }
  for norm_key, fill in normalizer_defaults.items():
    if norm_key in out:
      out[norm_key][:, dims] = fill
  if normalizer_count is not None and "obs_normalizer.count" in out:
    # The running stats share one count, so a smaller count lets every dim
    # re-estimate quickly on the new task's data.
    out["obs_normalizer.count"] = torch.tensor(normalizer_count, dtype=torch.long)
  return out


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
  parser.add_argument(
    "--reset-obs-dims",
    type=str,
    default=None,
    help="Obs dims (e.g. '75:83') to zero in actor/critic first layer and reset "
    "in the obs normalizer, for inputs the source run never varied.",
  )
  parser.add_argument(
    "--normalizer-count",
    type=int,
    default=None,
    help="Override obs normalizer sample count (with --reset-obs-dims) so stats "
    "adapt quickly, e.g. 10000000.",
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

  reset_dims = parse_obs_dims(args.reset_obs_dims) if args.reset_obs_dims else []
  if reset_dims:
    actor_sd = reset_state_dict_obs_dims(actor_sd, reset_dims, args.normalizer_count)
    if critic_sd:
      critic_sd = reset_state_dict_obs_dims(
        critic_sd, reset_dims, args.normalizer_count
      )

  args.output.parent.mkdir(parents=True, exist_ok=True)
  payload = {
    "actor_state_dict": actor_sd,
    "critic_state_dict": critic_sd,
    "infos": {
      "source": str(args.input),
      "env_state": {"common_step_counter": 0},
      "padded_actor_obs_dim": pad_actor,
      "padded_critic_obs_dim": pad_critic,
      "reset_obs_dims": reset_dims,
    },
  }
  torch.save(payload, args.output)
  if pad_actor is not None:
    key = _first_linear_weight_key(actor_sd)
    print(
      f"Padded actor {key} to obs dim {actor_sd[key].shape[1]} (target {pad_actor})"
    )
  if pad_critic is not None and critic_sd:
    key = _first_linear_weight_key(critic_sd)
    print(
      f"Padded critic {key} to obs dim {critic_sd[key].shape[1]} (target {pad_critic})"
    )
  if reset_dims:
    print(f"Reset obs dims {reset_dims[0]}..{reset_dims[-1]} ({len(reset_dims)} dims)")
  print(f"Wrote fresh-optimizer warm start: {args.output}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

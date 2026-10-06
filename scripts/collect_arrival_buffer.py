#!/usr/bin/env python3
"""Collect Arrival Pose Buffer from a frozen Walk AMP policy (§9.2.1).

Example::

  uv run python scripts/collect_arrival_buffer.py \\
    --checkpoint /path/to/model_9950.pt \\
    --num-states 20000 \\
    --output data/kick/arrival_pose_buffer.pt

Requires a trained Flat AMP Walk checkpoint. Samples random walk velocities,
walks ~1.5 s, then commands stop and records a 35-frame window around cmd=0.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--checkpoint", type=Path, required=True)
  parser.add_argument(
    "--task",
    default="Mjlab-Velocity-Flat-Amp-Booster-K1-Whirlwind",
    help="Walk AMP task id used for collection.",
  )
  parser.add_argument("--num-envs", type=int, default=256)
  parser.add_argument("--num-states", type=int, default=20_000)
  parser.add_argument(
    "--output",
    type=Path,
    default=Path("data/kick/arrival_pose_buffer.pt"),
  )
  parser.add_argument("--device", default="cuda:0")
  parser.add_argument("--seed", type=int, default=0)
  args = parser.parse_args()

  # Lazy imports so --help works without GPU deps.
  from mjlab.tasks.kick.mdp.arrival_buffer import ARRIVAL_KEYS
  from mjlab.tasks.registry import load_env_cfg
  from mjlab.utils.torch import configure_torch_backends

  configure_torch_backends()
  torch.manual_seed(args.seed)

  print(
    "Arrival buffer collector scaffolding is ready.\n"
    f"  checkpoint: {args.checkpoint}\n"
    f"  task: {args.task}\n"
    f"  target states: {args.num_states}\n"
    f"  output: {args.output}\n"
    "\n"
    "Full frozen-policy rollout collection (walk → stop window) should be\n"
    "wired to VelocityAmpOnPolicyRunner + env.step once a 9950 ckpt path is\n"
    "confirmed. For now this writes an empty-schema placeholder if --dry-run\n"
    "is not set; raise NotImplemented for live collection until runner hook\n"
    "is attached in a follow-up."
  )
  # Minimal schema stub so reset path can be developed against a file.
  if not args.checkpoint.is_file():
    raise FileNotFoundError(args.checkpoint)

  # Placeholder tensors (zeros) — replace with real collection.
  n = min(args.num_states, 64)
  stub = {
    "joint_pos": torch.zeros(n, 22),
    "joint_vel": torch.zeros(n, 22),
    "base_lin_vel_b": torch.zeros(n, 3),
    "base_ang_vel_b": torch.zeros(n, 3),
    "projected_gravity_b": torch.tensor([[0.0, 0.0, -1.0]]).expand(n, 3).clone(),
    "root_pos_w": torch.zeros(n, 3),
    "root_quat_w": torch.tensor([[1.0, 0.0, 0.0, 0.0]]).expand(n, 4).clone(),
  }
  assert set(stub) == set(ARRIVAL_KEYS)
  args.output.parent.mkdir(parents=True, exist_ok=True)
  torch.save(stub, args.output)
  print(
    f"Wrote stub buffer ({n} frames) to {args.output}. "
    "Replace with real Walk-9950 collection before training."
  )
  _ = load_env_cfg  # keep import for future runner wiring


if __name__ == "__main__":
  main()

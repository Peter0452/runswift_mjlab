#!/usr/bin/env python3
"""Create a fresh-optimizer warm-start checkpoint from an rsl_rl checkpoint."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument("--input", type=Path, required=True)
  parser.add_argument("--output", type=Path, required=True)
  args = parser.parse_args()

  checkpoint = torch.load(args.input, map_location="cpu", weights_only=False)
  args.output.parent.mkdir(parents=True, exist_ok=True)
  torch.save(
    {
      "actor_state_dict": checkpoint["actor_state_dict"],
      "critic_state_dict": checkpoint["critic_state_dict"],
      "infos": {
        "source": str(args.input),
        "env_state": {"common_step_counter": 0},
      },
    },
    args.output,
  )
  print(f"Wrote fresh-optimizer warm start: {args.output}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

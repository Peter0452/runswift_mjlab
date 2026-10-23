"""Average the actor weights of several checkpoints (stochastic weight averaging).

Self-play checkpoints of one run sit a few thousandths of a nat apart and their
fixed-opponent goal share swings by about ±0.02 between them; the mean of their
weights played better than any one of them (v15/v16: 0.425 / 0.461 vs h022 /
controller, against 0.42 / 0.435 for the single checkpoints).

  python scripts/tools/average_checkpoints.py OUT.pt CKPT [CKPT ...]

Everything but the actor (critic, optimizer, AMP) is copied from the last
checkpoint, so OUT.pt also loads for evaluation and play.
"""

import argparse

import torch


def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument("out")
  parser.add_argument("checkpoints", nargs="+")
  args = parser.parse_args()
  loaded = [
    torch.load(c, map_location="cpu", weights_only=False) for c in args.checkpoints
  ]
  out = loaded[-1]
  out["actor_state_dict"] = {
    k: (
      sum(d["actor_state_dict"][k] for d in loaded) / len(loaded)
      if torch.is_floating_point(v)
      else v
    )
    for k, v in out["actor_state_dict"].items()
  }
  torch.save(out, args.out)
  print(f"averaged {len(loaded)} checkpoints -> {args.out}")


if __name__ == "__main__":
  main()

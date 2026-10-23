"""Relative actor weight change of checkpoints against a reference.

.venv/bin/python scripts/tools/weight_drift.py REF CKPT [CKPT ...]
"""

import sys

import torch


def load(path):
  return torch.load(path, map_location="cpu", weights_only=False)["actor_state_dict"]


def main() -> None:
  ref = load(sys.argv[1])
  for path in sys.argv[2:]:
    sd = load(path)
    num = den = 0.0
    for k, w in ref.items():
      if not k.startswith("mlp.") or not k.endswith("weight"):
        continue
      v = sd[k]
      if v.shape != w.shape:  # padded first layer: compare the shared columns
        v = v[:, : w.shape[1]]
      num += float((v - w).square().sum())
      den += float(w.square().sum())
    print(
      f"{path.split('/')[-2][-18:]}/{path.split('/')[-1]}: "
      f"weight change {100 * (num / den) ** 0.5:.1f}%"
    )


if __name__ == "__main__":
  main()

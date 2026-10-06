"""Weight-space crossover: blend checkpoints of the same architecture.

usage: python scripts/tools/blend_checkpoints.py OUT.pt CK1:W1 CK2:W2 [...]

Floating-point tensors in the actor, critic and discriminator state dicts are
averaged with the given weights (normalised to sum 1); everything else
(optimizer, counters, iteration) comes from the first checkpoint. Running-mean
normaliser statistics are averaged too. Intended for checkpoints of one
fine-tune lineage (e.g. neighbouring iterations, or two runs from a shared
ancestor), where linear interpolation stays in a good region.
"""

import sys
from pathlib import Path

import torch


def main() -> None:
  out = Path(sys.argv[1])
  parts = [a.rsplit(":", 1) for a in sys.argv[2:]]
  cks = [torch.load(p, map_location="cpu", weights_only=False) for p, _ in parts]
  w = torch.tensor([float(x) for _, x in parts])
  w = w / w.sum()
  blended = dict(cks[0])
  for key in ("actor_state_dict", "critic_state_dict", "discriminator_state_dict"):
    sd = {}
    for name, t0 in cks[0][key].items():
      if torch.is_tensor(t0) and t0.is_floating_point():
        sd[name] = sum(wi * c[key][name].float() for wi, c in zip(w, cks)).to(t0.dtype)
      else:
        sd[name] = t0
    blended[key] = sd
  out.parent.mkdir(parents=True, exist_ok=True)
  torch.save(blended, out)
  print(f"BLEND {out}: " + ", ".join(f"{p} x{wi:.2f}" for (p, _), wi in zip(parts, w.tolist())))


if __name__ == "__main__":
  main()

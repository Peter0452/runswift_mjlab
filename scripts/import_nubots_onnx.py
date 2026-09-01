#!/usr/bin/env python3
"""Import NuBots ONNX actor weights into an mjlab / rsl_rl checkpoint.

The NuBots ``k1_walk_htwk`` ONNX is a plain MLP::

    66 → 512 → 256 → 128 → 16   (ELU between layers)

which matches ``Mjlab-Velocity-*-Booster-K1-Nubots`` (student = teacher).

Example::

  uv run python scripts/import_nubots_onnx.py \\
    --onnx ../k1_policy_runner/nubots_models/k1_walk_htwk_k1_walk_htwk.onnx \\
    --out logs/rsl_rl/k1_nubots/nubots_teacher/model_0.pt

  uv run train Mjlab-Velocity-Flat-Booster-K1-Nubots \\
    --agent.resume True \\
    --agent.load_run nubots_teacher \\
    --env.scene.num-envs 1024
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import onnx
import torch
from onnx import numpy_helper

# Isaac ActorCritic Linear indices → rsl_rl MLP Sequential indices.
_ONNX_TO_MLP = (
  ("actor.0", "mlp.0"),
  ("actor.2", "mlp.2"),
  ("actor.4", "mlp.4"),
  ("actor.6", "mlp.6"),
)


def load_onnx_actor_weights(onnx_path: Path) -> dict[str, torch.Tensor]:
  model = onnx.load(str(onnx_path))
  inits = {i.name: numpy_helper.to_array(i) for i in model.graph.initializer}
  actor_sd: dict[str, torch.Tensor] = {}
  for onnx_prefix, mlp_prefix in _ONNX_TO_MLP:
    w = inits.get(f"{onnx_prefix}.weight")
    b = inits.get(f"{onnx_prefix}.bias")
    if w is None or b is None:
      raise KeyError(f"Missing {onnx_prefix}.weight/bias in {onnx_path}")
    actor_sd[f"{mlp_prefix}.weight"] = torch.from_numpy(np.array(w, copy=True))
    actor_sd[f"{mlp_prefix}.bias"] = torch.from_numpy(np.array(b, copy=True))

  # Scalar action std (agent.yaml init_noise_std=0.5).
  actor_sd["distribution.std_param"] = torch.full((16,), 0.5)
  return actor_sd


def random_critic_weights(
  obs_dim: int = 70, hidden: tuple[int, ...] = (512, 256, 128)
) -> dict[str, torch.Tensor]:
  """Untrained critic with NuBots dims (actor 66 + lin_vel 3 + height 1)."""
  dims = (obs_dim, *hidden, 1)
  sd: dict[str, torch.Tensor] = {}
  # MLP layout: Linear, ELU, Linear, ELU, ... → even indices are Linear.
  layer_idx = 0
  for i in range(len(dims) - 1):
    w = torch.empty(dims[i + 1], dims[i])
    torch.nn.init.orthogonal_(w, gain=np.sqrt(2))
    b = torch.zeros(dims[i + 1])
    sd[f"mlp.{layer_idx}.weight"] = w
    sd[f"mlp.{layer_idx}.bias"] = b
    layer_idx += 2
  return sd


def build_checkpoint(
  actor_sd: dict[str, torch.Tensor],
  critic_sd: dict[str, torch.Tensor],
) -> dict:
  return {
    "actor_state_dict": actor_sd,
    "critic_state_dict": critic_sd,
    "iter": 0,
    "infos": {"source": "nubots_onnx", "env_state": {"common_step_counter": 0}},
  }


def verify_against_onnx(
  onnx_path: Path, actor_sd: dict[str, torch.Tensor], n: int = 8
) -> float:
  """Max abs error: ONNX vs reconstructed MLP on random obs."""
  import onnxruntime as ort
  from rsl_rl.modules import MLP

  mlp = MLP(66, 16, [512, 256, 128], "elu")
  mlp.load_state_dict(
    {k.replace("mlp.", ""): v for k, v in actor_sd.items() if k.startswith("mlp.")}
  )
  mlp.eval()

  sess = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
  inp = sess.get_inputs()[0].name
  out = sess.get_outputs()[0].name
  errs: list[float] = []
  for _ in range(n):
    x = np.random.randn(1, 66).astype(np.float32)
    onnx_y = sess.run([out], {inp: x})[0]
    with torch.no_grad():
      pt_y = mlp(torch.from_numpy(x)).numpy()
    errs.append(float(np.max(np.abs(onnx_y - pt_y))))
  return max(errs)


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
    "--onnx",
    type=Path,
    default=Path(__file__).resolve().parents[2]
    / "k1_policy_runner"
    / "nubots_models"
    / "k1_walk_htwk_k1_walk_htwk.onnx",
    help="Path to NuBots ONNX policy",
  )
  parser.add_argument(
    "--out",
    type=Path,
    default=Path("logs/rsl_rl/k1_nubots/nubots_teacher/model_0.pt"),
    help="Output checkpoint path",
  )
  parser.add_argument(
    "--skip-verify",
    action="store_true",
    help="Skip ONNX↔MLP numerical check",
  )
  args = parser.parse_args()

  if not args.onnx.is_file():
    # Fallback: sibling checkout under /workspace
    alt = Path(
      "/workspace/k1_policy_runner/nubots_models/k1_walk_htwk_k1_walk_htwk.onnx"
    )
    if alt.is_file():
      args.onnx = alt
    else:
      raise SystemExit(f"ONNX not found: {args.onnx}")

  actor_sd = load_onnx_actor_weights(args.onnx)
  critic_sd = random_critic_weights()
  ckpt = build_checkpoint(actor_sd, critic_sd)

  if not args.skip_verify:
    err = verify_against_onnx(args.onnx, actor_sd)
    print(f"ONNX↔MLP max abs error: {err:.3e}")
    if err > 1e-4:
      raise SystemExit(f"Weight import mismatch (err={err})")

  args.out.parent.mkdir(parents=True, exist_ok=True)
  torch.save(ckpt, args.out)
  print(f"Wrote teacher checkpoint → {args.out.resolve()}")
  print("Fine-tune with:")
  print(
    "  uv run train Mjlab-Velocity-Flat-Booster-K1-Nubots "
    "--agent.resume True "
    f"--agent.load_run {args.out.parent.name} "
    "--agent.load_checkpoint model_0.pt "
    "--env.scene.num-envs 1024"
  )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

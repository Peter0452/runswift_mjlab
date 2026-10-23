"""Verify Peter's supplied checkpoint against the deployment ONNX export."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from compare import session
from contracts import DEFAULT_ASSETS, MODELS


def audit(root):
    paths = {key: root / MODELS[key][0] for key in ("peter", "peter-checkpoint")}
    for key, path in paths.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != MODELS[key][1]:
            raise ValueError(f"Checkpoint hash differs: {key}")
    torch.set_num_threads(1)
    actor = torch.load(
        paths["peter-checkpoint"], map_location="cpu", weights_only=True
    )["actor_state_dict"]
    exported = session(paths["peter"])
    inputs = torch.from_numpy(
        np.random.default_rng(20261006).normal(0, 0.4, (128, 83)).astype(np.float32)
    )
    expected = (inputs - actor["obs_normalizer._mean"]) / (
        actor["obs_normalizer._std"] + 0.01
    )
    for layer in (0, 2, 4, 6):
        expected = torch.nn.functional.linear(
            expected, actor[f"mlp.{layer}.weight"], actor[f"mlp.{layer}.bias"]
        )
        if layer != 6:
            expected = torch.nn.functional.elu(expected)
    actual = np.concatenate(
        [
            exported.run(None, {exported.get_inputs()[0].name: row.numpy()[None]})[0]
            for row in inputs
        ]
    )
    error = float(np.max(np.abs(actual - expected.numpy())))
    report = {
        "samples": 128,
        "seed": 20261006,
        "normalizer_epsilon": 0.01,
        "activation": "ELU",
        "actor_widths": [83, 512, 256, 128, 22],
        "max_absolute_output_error": error,
        "tolerance": 1e-5,
        "passed": error < 1e-5,
        "models": {
            key: {"path": MODELS[key][0], "sha256": MODELS[key][1]} for key in paths
        },
    }
    if not report["passed"]:
        raise ValueError(
            f"ONNX export does not reproduce the supplied checkpoint: {error}"
        )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=DEFAULT_ASSETS)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.assets.expanduser().resolve())
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

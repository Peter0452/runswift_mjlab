"""Export one training checkpoint to ONNX with deploy metadata.

The run directory's ``.onnx`` is overwritten at every save, so it is always
the latest checkpoint. This exports a chosen one, with the same metadata
(default_joint_pos, action_scale, PD gains, joint and observation names) that
``k1_policy_runner`` reads.

  uv run python scripts/tools/export_onnx.py --checkpoint <ckpt> --output <file.onnx>
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

import mjlab.tasks  # noqa: F401
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.rl.exporter_utils import attach_metadata_to_onnx, get_base_metadata
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls

TASK = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"


def main() -> None:
  p = argparse.ArgumentParser(description=__doc__)
  p.add_argument("--checkpoint", required=True)
  p.add_argument("--output", required=True)
  p.add_argument("--task", default=TASK)
  p.add_argument("--device", default="cuda:0")
  args = p.parse_args()

  cfg = load_env_cfg(args.task, play=True)
  cfg.scene.num_envs = 1
  agent = load_rl_cfg(args.task)
  env = RslRlVecEnvWrapper(
    ManagerBasedRlEnv(cfg=cfg, device=args.device), clip_actions=agent.clip_actions
  )
  runner = load_runner_cls(args.task)(env, asdict(agent), device=args.device)
  runner.load(
    args.checkpoint, load_cfg={"actor": True}, strict=True, map_location=args.device
  )

  out = Path(args.output).resolve()
  out.parent.mkdir(parents=True, exist_ok=True)
  runner.export_policy_to_onnx(str(out.parent), out.name)
  attach_metadata_to_onnx(
    str(out), get_base_metadata(env.unwrapped, Path(args.checkpoint).stem)
  )
  print(f"exported {args.checkpoint} -> {out}")


if __name__ == "__main__":
  main()

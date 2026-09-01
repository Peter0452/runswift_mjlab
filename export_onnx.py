"""Export a training checkpoint to ONNX with deploy metadata attached.

Training only exports ONNX for checkpoints it happens to save, so promoting an
arbitrary checkpoint to a deployable artifact needs this.

  uv run python export_onnx.py --checkpoint <ckpt.pt> --out nubots_models/foo.onnx
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import MjlabOnPolicyRunner, RslRlVecEnvWrapper
from mjlab.rl.exporter_utils import attach_metadata_to_onnx, get_base_metadata
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.utils.torch import configure_torch_backends


def main() -> None:
  p = argparse.ArgumentParser(description=__doc__)
  p.add_argument("--task", default="Mjlab-Velocity-Quality-Booster-K1-Nubots")
  p.add_argument("--checkpoint", required=True)
  p.add_argument("--out", required=True, help="destination .onnx path")
  p.add_argument("--device", default="cuda:0")
  p.add_argument(
    "--tight-arms",
    action="store_true",
    help="restore pre-unlock shoulder scales (0.12 pitch / 0.05 roll). Required "
    "for checkpoints trained before the arm-swing unlock: the exported scales "
    "are applied to the network output at deploy time, so a mismatch silently "
    "amplifies shoulder commands 2.5x.",
  )
  p.add_argument(
    "--expect-scales-like",
    metavar="ONNX",
    help="fail unless the exported action_scale matches this reference model",
  )
  args = p.parse_args()

  configure_torch_backends()
  out = Path(args.out).resolve()
  out.parent.mkdir(parents=True, exist_ok=True)

  env_cfg = load_env_cfg(args.task, play=False)
  agent_cfg = load_rl_cfg(args.task)
  env_cfg.scene.num_envs = 1

  if args.tight_arms:
    from mjlab.tasks.velocity.config.k1 import env_cfgs as e

    action = env_cfg.actions["joint_pos"]
    action.scale = dict(action.scale)
    action.clip = dict(action.clip or {})
    for name in e._NUBOTS_SHOULDER_PITCH_JOINTS:
      action.scale[name] = e._NUBOTS_SHOULDER_PITCH_SCALE
      action.clip[name] = (
        -e._NUBOTS_SHOULDER_PITCH_BAND,
        e._NUBOTS_SHOULDER_PITCH_BAND,
      )
    for name in e._NUBOTS_SHOULDER_ROLL_JOINTS:
      center = -1.3 if name.startswith("Left") else 1.3
      action.scale[name] = e._NUBOTS_SHOULDER_ROLL_SCALE
      action.clip[name] = (
        center - e._NUBOTS_SHOULDER_ROLL_BAND,
        center + e._NUBOTS_SHOULDER_ROLL_BAND,
      )

  env = ManagerBasedRlEnv(cfg=env_cfg, device=args.device)
  env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)

  runner_cls = load_runner_cls(args.task) or MjlabOnPolicyRunner
  runner = runner_cls(env, asdict(agent_cfg), device=args.device)
  runner.load(
    args.checkpoint, load_cfg={"actor": True}, strict=True, map_location=args.device
  )

  runner.export_policy_to_onnx(str(out.parent), out.name)
  attach_metadata_to_onnx(str(out), get_base_metadata(env.unwrapped, "local"))

  if args.expect_scales_like:
    import onnx

    def scales(path: str) -> str:
      props = {p.key: p.value for p in onnx.load(path).metadata_props}
      return props["action_scale"]

    got, want = scales(str(out)), scales(args.expect_scales_like)
    if got != want:
      out.unlink(missing_ok=True)
      raise SystemExit(
        f"action_scale mismatch vs {args.expect_scales_like}\n"
        f"  exported: {got}\n  expected: {want}\n"
        "Export deleted. Check --tight-arms and that --task matches training."
      )
    print(f"[OK] action_scale matches {args.expect_scales_like}")

  print(f"[OK] {args.checkpoint}\n  -> {out} ({out.stat().st_size / 1e6:.2f} MB)")
  env.close()


if __name__ == "__main__":
  main()

"""FastSAC velocity runner with ONNX export metadata."""

from __future__ import annotations

from pathlib import Path

import wandb

from mjlab.rl.exporter_utils import attach_metadata_to_onnx, get_base_metadata
from mjlab.rl.fast_sac.runner import FastSacRunner
from mjlab.rl.fast_sac.vecenv_wrapper import FastSacVecEnvWrapper


class VelocityFastSacRunner(FastSacRunner):
  env: FastSacVecEnvWrapper

  def save(self, path: str, infos=None) -> None:
    super().save(path, infos)
    if self.log_dir is None:
      return
    policy_dir = Path(path).parent
    filename = f"{policy_dir.name}.onnx"
    onnx_path = policy_dir / filename
    try:
      self.export_policy_to_onnx(str(policy_dir), filename)
      run_name: str = wandb.run.name if wandb.run is not None else "local"
      metadata = get_base_metadata(self.env.unwrapped, run_name)
      attach_metadata_to_onnx(str(onnx_path), metadata)
      if wandb.run is not None and self.cfg.get("upload_model", True):
        wandb.save(str(onnx_path), base_path=str(policy_dir))
    except Exception as e:
      print(f"[WARN] FastSAC ONNX export failed (training continues): {e}")

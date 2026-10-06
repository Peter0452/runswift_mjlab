"""Deployability check: the exported ONNX gives the same actions as the trained
actor on real observations from the stage-3 env (batch 1, as on the robot).

usage: python scripts/tools/onnx_parity.py CHECKPOINT ONNX
"""

import os
import sys
from dataclasses import asdict

os.environ["KICK_EVAL"] = "1"

import numpy as np  # noqa: E402
import onnxruntime as ort  # noqa: E402
import torch  # noqa: E402

import mjlab.tasks  # noqa: E402, F401
from mjlab.envs import ManagerBasedRlEnv  # noqa: E402
from mjlab.rl import RslRlVecEnvWrapper  # noqa: E402
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls  # noqa: E402

T = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"
ck, onnx_path = sys.argv[1], sys.argv[2]
cfg = load_env_cfg(T)
cfg.scene.num_envs = 16
agent = load_rl_cfg(T)
env = RslRlVecEnvWrapper(ManagerBasedRlEnv(cfg=cfg, device="cuda:0"), clip_actions=agent.clip_actions)
r = load_runner_cls(T)(env, asdict(agent), device="cuda:0")
r.load(ck, load_cfg={"actor": True}, strict=True, map_location="cuda:0")
pol = r.get_inference_policy(device="cuda:0")
sess = ort.InferenceSession(onnx_path)
name = sess.get_inputs()[0].name
obs, _ = env.reset()
worst = 0.0
with torch.inference_mode():
  for _ in range(300):
    a = pol(obs).cpu().numpy()
    x = obs["actor"].cpu().numpy().astype(np.float32)
    for i in range(x.shape[0]):
      y = sess.run(None, {name: x[i : i + 1]})[0][0]
      worst = max(worst, float(np.abs(y - a[i]).max()))
    obs, _, _, _ = env.step(torch.as_tensor(a, device="cuda:0"))
print(f"PARITY ONNX vs actor: max |Δaction| over 300 steps x 16 envs = {worst:.2e}"
      f" -> {'OK' if worst < 1e-3 else 'MISMATCH'}")

"""Golden action snapshots for the models we must not break.

For each model in MODELS: build the task's play env (fixed seed), load the
checkpoint the way `play` does, and record the observation layout, one batch
of reset observations and the policy's actions on them. `check` reloads the
model and requires the same layout, the same actions on the stored
observations, and the same actor observations after a fresh seeded reset
(critic-only inputs carry float noise and are reported, not checked).

  .venv/bin/python scripts/tools/golden.py record [NAME ...]
  .venv/bin/python scripts/tools/golden.py check [NAME ...]   # exit 1 on failure

Each model runs in its own process (per-run genes are read at import time).
Snapshots live in tests/golden/policies/<name>.pt; tests/test_golden_policies.py
runs `check` (slow, needs CUDA and the checkpoints under logs/).
"""

from __future__ import annotations

import dataclasses
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "tests" / "golden" / "policies"
NUM_ENVS = 16
SEED = 7
ACTION_ATOL = 1e-5
ACTOR_OBS_ATOL = 1e-4
GENE_META = {"from", "resume", "change", "control"}


@dataclasses.dataclass(frozen=True)
class Model:
  name: str
  task: str
  checkpoint: str
  genes_env: str | None = None  # env var fed from the run dir's genes.json
  note: str = ""


MODELS = [
  Model(
    "gold_walk",
    "Mjlab-Velocity-Rough-Amp-DA-Muon-Booster-K1",
    "logs/rsl_rl/k1_velocity_amp_symmetric_muon_wwcmu50_roughft/"
    "2026-09-21_20-34-24_stageA/model_9950.pt",
    note="AMP walk, deployed as amp_models/model_9950.onnx; striker walk skill",
  ),
  Model(
    "kick_champion_h022",
    "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1",
    "logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/"
    "model_18450.pt",
    note="kick-loop champion",
  ),
  Model(
    "kick_h011_teacher",
    "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1",
    "logs/rsl_rl/k1_kick_stage3_amp/2026-10-08_12-04-08_h011_c2/model_17750.pt",
    note="long-power kick; the dribble's kick teacher",
  ),
  Model(
    "selfplay_swa_v15v16",
    "Mjlab-Velocity-Kick-SelfPlay-Amp-DA-Muon-Booster-K1",
    "logs/rsl_rl/k1_kick_selfplay_amp/swa_v15v16/model_9100.pt",
    note="best flat self-play striker (86 inputs)",
  ),
  Model(
    "striker_controller_v2",
    "Mjlab-Velocity-Striker-Controller-Booster-K1",
    "logs/rsl_rl/k1_striker_controller/2026-10-11_19-43-56_controller_v2/model_1750.pt",
    note="best two-level controller (GRU)",
  ),
  Model(
    "dribble_v51_11750",
    "Mjlab-Velocity-Dribble-Amp-DA-Muon-Booster-K1",
    "logs/rsl_rl/k1_dribble_amp/2026-10-23_08-22-20_dribble_aimhead_v51/model_11750.pt",
    genes_env="DRIBBLE_GENES",
    note="best balanced dribble with kick mode",
  ),
]
BY_NAME = {m.name: m for m in MODELS}


def _genes(model: Model) -> dict[str, str]:
  if model.genes_env is None:
    return {}
  path = ROOT / Path(model.checkpoint).parent / "genes.json"
  genes = {k: v for k, v in json.loads(path.read_text()).items() if k not in GENE_META}
  return {model.genes_env: json.dumps(genes)}


def _one(name: str, mode: str) -> int:
  """Record or check one model in this process."""
  import torch

  import mjlab.tasks  # noqa: F401  (registers tasks)
  from mjlab.envs import ManagerBasedRlEnv
  from mjlab.rl import RslRlVecEnvWrapper
  from mjlab.rl.runner import MjlabOnPolicyRunner
  from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls

  model = BY_NAME[name]
  device = "cuda:0"
  torch.manual_seed(SEED)
  env_cfg = load_env_cfg(model.task, play=True)
  agent_cfg = load_rl_cfg(model.task)
  env_cfg.scene.num_envs = NUM_ENVS
  env_cfg.seed = SEED
  env = ManagerBasedRlEnv(cfg=env_cfg, device=device)
  runner_cls = load_runner_cls(model.task)
  make_vecenv = getattr(runner_cls, "make_vecenv", None)
  venv = (
    make_vecenv(env, agent_cfg)
    if make_vecenv is not None
    else RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
  )
  runner = (runner_cls or MjlabOnPolicyRunner)(
    venv, dataclasses.asdict(agent_cfg), device=device
  )
  runner.load(
    str(ROOT / model.checkpoint),
    load_cfg={"actor": True, "iteration": True},
    strict=True,
    map_location=device,
  )
  policy = runner.get_inference_policy(device=device)

  om = env.observation_manager
  layout = {
    group: [
      (term, list(dim))
      for term, dim in zip(terms, om.group_obs_term_dim[group], strict=True)
    ]
    for group, terms in om.active_terms.items()
  }
  fresh_obs = venv.get_observations()
  path = GOLDEN / f"{name}.pt"

  def act(obs):
    if hasattr(policy, "reset"):
      policy.reset()  # recurrent policies start from a zero state
    with torch.inference_mode():
      return policy(obs.to(device)).detach().cpu()

  if mode == "record":
    obs_cpu = fresh_obs.cpu()
    torch.save(
      {
        "model": dataclasses.asdict(model),
        "layout": layout,
        "obs": obs_cpu,
        "actions": act(obs_cpu),
      },
      path,
    )
    print(f"GOLDEN {name}: recorded {path.relative_to(ROOT)}", flush=True)
    return 0

  ref = torch.load(path, weights_only=False)
  ok = True
  if layout != ref["layout"]:
    ok = False
    print(f"GOLDEN {name}: FAIL observation layout changed", flush=True)
    for group in sorted(set(layout) | set(ref["layout"])):
      if layout.get(group) != ref["layout"].get(group):
        print(
          f"  {group}: was {ref['layout'].get(group)}\n  {group}: now {layout.get(group)}"
        )
  actions = act(ref["obs"])
  diff = float((actions - ref["actions"]).abs().max())
  if diff > ACTION_ATOL:
    ok = False
    print(
      f"GOLDEN {name}: FAIL actions differ by {diff:.3g} (> {ACTION_ATOL})", flush=True
    )
  drift = {
    k: float((fresh_obs[k].cpu() - ref["obs"][k]).abs().max())
    for k in ref["obs"].keys()
    if k in fresh_obs.keys() and fresh_obs[k].shape == ref["obs"][k].shape
  }
  # Seeded resets reproduce the actor's inputs exactly (critic inputs carry
  # float noise), so a drift here means observation or reset code changed.
  if drift.get("actor", float("inf")) > ACTOR_OBS_ATOL:
    ok = False
    print(
      f"GOLDEN {name}: FAIL fresh actor observations differ by "
      f"{drift.get('actor', float('nan')):.3g} (> {ACTOR_OBS_ATOL})",
      flush=True,
    )
    if "actor" in fresh_obs.keys() and "actor" in ref["obs"].keys():
      # Where (env, slot): the drift is intermittent (2026-10-27/28, ~1 run in
      # 4, always 1.67 on kick_champion_h022), so name it when it happens.
      d = (fresh_obs["actor"].cpu() - ref["obs"]["actor"]).abs()
      for flat in d.flatten().topk(min(5, d.numel())).indices.tolist():
        e, s = divmod(flat, d.shape[-1])
        print(
          f"  env {e} slot {s}: ref {float(ref['obs']['actor'][e, s]):.4g} "
          f"now {float(fresh_obs['actor'][e, s]):.4g}",
          flush=True,
        )
  verdict = "ok" if ok else "FAIL"
  print(
    f"GOLDEN {name}: {verdict} (action diff {diff:.2g}; fresh reset obs drift "
    + ", ".join(f"{k} {v:.2g}" for k, v in drift.items())
    + ")",
    flush=True,
  )
  return 0 if ok else 1


def run(mode: str, names: list[str]) -> int:
  GOLDEN.mkdir(parents=True, exist_ok=True)
  failed = []
  for name in names or [m.name for m in MODELS]:
    model = BY_NAME[name]
    if not (ROOT / model.checkpoint).exists():
      print(f"GOLDEN {name}: SKIP checkpoint missing ({model.checkpoint})", flush=True)
      continue
    # Default ball (K1_BALL unset = B-Human's); the snapshots were recorded with it.
    env = {k: v for k, v in os.environ.items() if k != "K1_BALL"}
    env.update(_genes(model))
    proc = subprocess.run(
      [sys.executable, __file__, "_one", name, mode], cwd=ROOT, env=env
    )
    if proc.returncode != 0:
      failed.append(name)
  if failed:
    print(f"GOLDEN {mode}: failed {failed}", flush=True)
  return 1 if failed else 0


if __name__ == "__main__":
  cmd = sys.argv[1]
  if cmd == "_one":
    sys.exit(_one(sys.argv[2], sys.argv[3]))
  sys.exit(run(cmd, sys.argv[2:]))

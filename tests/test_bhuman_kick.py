"""B-Human kick port: field heights, randomization helper, stages, env shape."""

from __future__ import annotations

import mujoco
import numpy as np
import pytest
import torch
from conftest import get_test_device

import mjlab.tasks  # noqa: F401
from mjlab.envs import ManagerBasedRlEnv
from mjlab.tasks.bhuman_kick.kick_command import (
  BHumanKickCommand,
  BHumanKickCommandCfg,
  Rand,
  apply_rand,
)
from mjlab.tasks.bhuman_kick.robot import LEG_JOINTS, get_bhuman_k1_spec
from mjlab.tasks.bhuman_kick.terrain import FieldHeights, bhuman_field_generator_cfg
from mjlab.tasks.registry import list_tasks, load_env_cfg, load_rl_cfg
from mjlab.terrains.terrain_generator import TerrainGenerator


def test_field_heights_match_ray_casts() -> None:
  cfg = bhuman_field_generator_cfg()
  cfg.seed = 3
  spec = mujoco.MjSpec()
  TerrainGenerator(cfg).compile(spec)
  model = spec.compile()
  data = mujoco.MjData(model)
  mujoco.mj_forward(model, data)
  heights = FieldHeights(model, 15.0, "cpu")
  lo, hi = heights.inner_lo.numpy(), heights.inner_hi.numpy()
  assert np.allclose(hi - lo, (80.0, 20.0), atol=0.11)
  rng = np.random.default_rng(0)
  geom = np.zeros(1, np.int32)
  errors = []
  for _ in range(300):
    x, y = rng.uniform(lo, hi)
    d = mujoco.mj_ray(
      model, data, np.array([x, y, 1.0]), np.array([0, 0, -1.0]), None, 1, -1, geom
    )
    z = heights(torch.tensor([[x, y]], dtype=torch.float)).item()
    errors.append(abs(1.0 - d - z))
  # Bilinear lookup vs. MuJoCo's triangulated surface: equal up to step edges.
  assert np.median(errors) < 1e-3 and max(errors) < 0.01


def test_robot_has_bhuman_legs_only() -> None:
  model = get_bhuman_k1_spec().compile()
  names = [
    mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(1, model.njnt)
  ]
  assert tuple(names) == LEG_JOINTS


def test_apply_rand_matches_booster_gym() -> None:
  x = torch.zeros(100_000)
  u = apply_rand(x, Rand("uniform", "additive", 0.5, 1.5))
  assert 0.5 <= u.min() and u.max() <= 1.5
  g = apply_rand(x, Rand("gaussian", "additive", 0.0, 2.0))
  assert abs(g.std().item() - 2.0) < 0.05
  # uniform_log: lo + (hi - lo) U / -log(clamp(U', 0.0067, 0.37)).
  ul = apply_rand(x, Rand("uniform_log", "additive", 0.5, 20.0))
  rng = np.random.default_rng(0)
  ref = 0.5 + 19.5 * rng.random(100_000) / -np.log(
    np.clip(rng.random(100_000), 0.0067, 0.37)
  )
  assert ul.min() >= 0.5 and ul.max() <= 0.5 + 19.5 / 0.99
  assert abs(ul.mean().item() - ref.mean()) < 0.1
  assert abs(ul.median().item() - np.median(ref)) < 0.15


def test_stages_are_cumulative() -> None:
  tasks = list_tasks()
  for stage in ("Stage1", "Stage3b", "Stage5", "Stage6"):
    assert f"Mjlab-BHuman-Kick-{stage}-Booster-K1" in tasks
  s5 = load_env_cfg("Mjlab-BHuman-Kick-Stage5-Booster-K1")
  kick = s5.commands["kick"]
  assert isinstance(kick, BHumanKickCommandCfg)
  assert kick.target_sole_yaw_angle == pytest.approx(1.5705)  # stage 2
  assert kick.kick_direction_negative_factor == 3.0  # stage 3b
  assert kick.kick_direction_sigma_range == 0.25  # stage 5
  assert s5.rewards["ball_sole_yaw"].weight == 0.0  # 25 -> 15 -> 5 -> 0
  assert load_rl_cfg("Mjlab-BHuman-Kick-Stage5-Booster-K1").algorithm.desired_kl == (  # type: ignore[attr-defined]
    0.003
  )
  base = load_env_cfg("Mjlab-BHuman-Kick-Booster-K1").commands["kick"]
  assert isinstance(base, BHumanKickCommandCfg)
  assert base.kick_direction_sigma_range == 1.0 and base.heavy_ball == 0.0


@pytest.mark.slow
def test_env_dims_and_steps() -> None:
  cfg = load_env_cfg("Mjlab-BHuman-Kick-Booster-K1")
  cfg.scene.num_envs = 4
  env = ManagerBasedRlEnv(cfg=cfg, device=get_test_device())
  obs, _ = env.reset()
  assert obs["actor"].shape == (4, 59)
  assert obs["critic"].shape == (4, 16)
  assert env.action_manager.total_action_dim == 13
  for _ in range(5):
    obs, *_ = env.step(torch.zeros(4, 13, device=env.device))
  assert torch.isfinite(obs["actor"]).all()
  cmd = env.command_manager.get_term("kick")
  assert isinstance(cmd, BHumanKickCommand)
  # Ball starts 0.4-1.5 m from the robot (uniform_log, 1.5 can be exceeded
  # slightly) and the robot stands at roughly its spawn height.
  dist = (cmd.ball_state[:, :2] - cmd.base_pos[:, :2]).norm(dim=-1)
  assert (dist > 0.3).all() and (dist < 2.0).all()
  env.close()

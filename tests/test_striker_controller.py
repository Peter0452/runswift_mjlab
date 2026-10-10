"""Tests for the two-level striker (controller over frozen walk / kick)."""

from types import SimpleNamespace

import pytest
import torch
from conftest import get_test_device

from mjlab.envs import ManagerBasedRlEnv
from mjlab.tasks.registry import load_env_cfg
from mjlab.tasks.velocity.mdp import striker_skills as skills
from mjlab.tasks.velocity.mdp.self_play import (
  OpponentPolicyAction,
  OpponentPolicyActionCfg,
  OpponentSeedCfg,
)
from mjlab.tasks.velocity.rl.striker_runner import (
  StrikerControllerRunner,
  StrikerControllerVecEnv,
)

TASK = "Mjlab-Velocity-Striker-Controller-Booster-K1"
KICK_CKPT = "logs/rsl_rl/k1_kick_stage3_amp/blends/x4_g004_70.pt"
WALK_CKPT = (
  "logs/rsl_rl/k1_velocity_amp_symmetric_muon_wwcmu45_roughft/"
  "2026-09-21_09-46-12_trk275/model_9950.pt"
)


def test_decode_and_skill_inputs():
  a = torch.tensor([[0.5, 0.0, 1.0, 0.9], [-0.5, 1.0, 0.0, -1.0]])
  kick, theta, level = skills.decode(a)
  assert kick.tolist() == [True, False]
  torch.testing.assert_close(theta, torch.tensor([torch.pi / 2, 0.0]))
  assert skills.range_from_level(level).tolist() == [[0, 0, 1], [1, 0, 0]]
  obs = torch.zeros(2, 86)
  k = skills.kick_inputs(obs, theta, level)
  torch.testing.assert_close(k[0, 78:80], torch.tensor([0.0, 1.0]), atol=1e-6, rtol=0)
  w = skills.walk_inputs(obs, theta, level)
  assert w.shape == (2, 75)
  # Level -1 walks at zero speed.
  torch.testing.assert_close(w[1, 72:74], torch.zeros(2))


@pytest.fixture(scope="module")
def venv():
  cfg = load_env_cfg(TASK)
  cfg.scene.num_envs = 2
  cfg.events.pop("reset_robot_from_motion")
  opp = cfg.actions["opponent"]
  assert isinstance(opp, OpponentPolicyActionCfg)
  opp.kick_skill_checkpoint = KICK_CKPT
  opp.walk_skill_checkpoint = WALK_CKPT
  opp.seeds = (OpponentSeedCfg(KICK_CKPT, "kick"),)
  env = ManagerBasedRlEnv(cfg=cfg, device=get_test_device())
  venv = StrikerControllerVecEnv(env)
  yield venv
  env.close()


@pytest.mark.slow
def test_controller_step_runs_ten_env_steps(venv):
  obs = venv.get_observations()
  assert obs["actor"].shape == (2, 86 + skills.SKILL_STATE_DIM)
  assert obs["critic"].shape == (2, 101 + skills.SKILL_STATE_DIM)
  assert venv.num_actions == skills.CONTROLLER_ACTION_DIM
  before = venv.unwrapped.episode_length_buf.clone()
  action = torch.tensor([[1.0, 1.0, 0.0, 0.0], [-1.0, 1.0, 0.0, 0.0]])
  obs, rew, dones, extras = venv.step(action.to(venv.device))
  steps = venv.unwrapped.episode_length_buf - before
  alive = dones == 0
  assert bool((steps[alive] == venv.decision_steps).all())
  assert rew.shape == (2,) and "time_outs" in extras
  # The skill state the controller sees: env 0 kicks, env 1 walks.
  expect = torch.tensor([1.0, 0.0], device=venv.device)
  torch.testing.assert_close(obs["actor"][alive, -2], expect[alive])
  assert venv.kick[alive].tolist() == expect[alive].bool().tolist()


@pytest.mark.slow
def test_skills_drive_the_learner(venv):
  obs = venv.unwrapped.observation_manager.compute()["actor"]
  kick, theta, level = skills.decode(
    torch.tensor([[1.0, 1.0, 0.0, 0.0], [-1.0, 1.0, 0.0, 0.5]], device=venv.device)
  )
  joint = skills.run_skills(obs, kick, theta, level, venv.kick_skill, venv.walk_skill)
  kick_only = venv.kick_skill(skills.kick_inputs(obs, theta, level))
  walk_only = venv.walk_skill(skills.walk_inputs(obs, theta, level))
  torch.testing.assert_close(joint[0], kick_only[0])
  torch.testing.assert_close(joint[1], walk_only[1])


@pytest.mark.slow
def test_opponent_runs_a_controller(venv):
  opp = venv.unwrapped.action_manager.get_term("opponent")
  assert isinstance(opp, OpponentPolicyAction)
  assert opp.slots[0].kind == "controller"
  # A controller that always kicks straight ahead.
  state = {
    "mlp.0.weight": torch.zeros(4, 88),
    "mlp.0.bias": torch.tensor([1.0, 1.0, 0.0, 0.0]),
  }
  opp.set_latest(state)
  opp.slot[:] = 0
  opp.ctrl_wait[:] = 0
  zero = torch.zeros(2, 4, device=venv.device)
  venv.step(zero)
  assert bool(opp.ctrl_kick.all())
  assert int(opp.ctrl_wait.max()) < opp.cfg.decision_steps


@pytest.mark.slow
def test_runner_mirrors_the_controller(venv, tmp_path):
  opp = venv.unwrapped.action_manager.get_term("opponent")
  assert isinstance(opp, OpponentPolicyAction)
  state = {
    "mlp.0.weight": torch.randn(4, 88),
    "mlp.0.bias": torch.zeros(4),
  }
  runner = StrikerControllerRunner.__new__(StrikerControllerRunner)
  runner.__dict__.update(
    cfg={"snapshot_interval": 1, "opponent_action_name": "opponent"},
    env=venv,
    alg=SimpleNamespace(get_policy=lambda: SimpleNamespace(state_dict=lambda: state)),
    logger=SimpleNamespace(writer=object(), log_dir=str(tmp_path)),
  )
  runner._sync(0)
  assert opp.slots[-1].name == "iter_1" and opp.slots[-1].kind == "controller"
  x = torch.randn(3, 88, device=venv.device)
  torch.testing.assert_close(
    opp.slots[0](x), x @ state["mlp.0.weight"].T.to(venv.device), rtol=1e-4, atol=1e-4
  )

"""Tests for the two-level striker (controller over frozen walk / kick)."""

from types import SimpleNamespace

import pytest
import torch
from conftest import get_test_device
from rsl_rl.models import RNNModel
from tensordict import TensorDict

from mjlab.envs import ManagerBasedRlEnv
from mjlab.tasks.registry import load_env_cfg
from mjlab.tasks.velocity.mdp import striker_skills as skills
from mjlab.tasks.velocity.mdp.self_play import (
  OpponentPolicyAction,
  OpponentPolicyActionCfg,
  OpponentSeedCfg,
  SelfPlayKickCommand,
  frozen_policy_from_state_dict,
)
from mjlab.tasks.velocity.rl.striker_runner import (
  StrikerControllerPlayEnv,
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


def test_frozen_gru_matches_rsl_rl_rnn_model():
  """The opponent's GRU controller steps like rsl_rl's ``RNNModel`` actor."""
  torch.manual_seed(0)
  obs = TensorDict({"actor": torch.zeros(3, 88)}, batch_size=[3])
  actor = RNNModel(
    obs,
    {"actor": ["actor"]},
    "actor",
    skills.CONTROLLER_ACTION_DIM,
    hidden_dims=(128,),
    obs_normalization=True,
    rnn_type="gru",
    rnn_hidden_dim=32,
    distribution_cfg={
      "class_name": "rsl_rl.modules.distribution:GaussianDistribution",
      "init_std": 0.5,
    },
  )
  # Non-trivial normalizer statistics.
  actor.obs_normalizer.train()
  actor.obs_normalizer(torch.randn(64, 88) * 3.0 + 1.0)
  actor.eval()
  frozen = frozen_policy_from_state_dict(actor.state_dict(), "controller", "t", "cpu")
  assert frozen.hidden_dim == 32
  h = None
  for _ in range(4):
    x = torch.randn(3, 88)
    expect = actor(TensorDict({"actor": x}, batch_size=[3]))
    got, h = frozen.step(x, h)
    torch.testing.assert_close(got, expect, rtol=1e-4, atol=1e-5)


@pytest.mark.slow
def test_learner_out_restarts_with_the_opponent(venv):
  cmd = venv.unwrapped.command_manager.get_term("twist")
  assert isinstance(cmd, SelfPlayKickCommand)
  hw = 0.5 * float(cmd.field_width[0])
  before = int(cmd._opponent_restarts[0])
  cmd.last_touch[0] = 1  # The learner touched it last.
  ball = venv.unwrapped.scene["ball"]
  ids = torch.tensor([0], device=venv.device)
  state = ball.data.default_root_state[ids].clone()
  state[:, :2] = cmd._to_world(
    torch.zeros(1, device=venv.device),
    torch.full((1,), hw + 0.3, device=venv.device),
    ids,
  )
  state[:, 2] = ball.data.root_link_pos_w[ids, 2]
  state[:, 3:] = 0.0
  state[:, 3] = 1.0
  ball.write_root_state_to_sim(state, env_ids=ids)
  venv.unwrapped.step(torch.zeros(2, 22, device=venv.device))
  assert bool(cmd.ball_out[0])
  assert int(cmd._opponent_restarts[0]) == before + 1
  # Ball back in, clear of the learner (the restart wrote it after the
  # step's forward pass).
  venv.unwrapped.sim.forward()
  xy = ball.data.root_link_pos_w[0, :2]
  learner = venv.unwrapped.scene["robot"].data.root_link_pos_w[0, :2]
  _, across = cmd.field_coords(xy.unsqueeze(0), ids)
  assert float(across.abs()) < hw
  assert float((xy - learner).norm()) >= cmd.cfg.restart_learner_distance - 0.05


@pytest.mark.slow
def test_play_env_decides_per_chunk_and_resets_memory(venv):
  calls, resets = [], []

  class Recurrent:
    def __call__(self, obs):
      calls.append(1)
      return torch.zeros(obs["actor"].shape[0], 4, device=venv.device)

    def reset(self, dones=None):
      resets.append(None if dones is None else dones.clone())

  play = StrikerControllerPlayEnv(venv)
  policy = play.hold(Recurrent())
  play.reset()
  for _ in range(2 * venv.decision_steps):
    play.step(policy(play.get_observations()))
  # One decision per chunk; the full reset cleared every env's memory.
  assert len(calls) == 2
  assert len(resets) == 1 and bool(resets[0].all())
  # An episode ending inside a chunk clears that env before the next decision.
  play._ended[0] = True
  play.t = 0
  policy(play.get_observations())
  assert resets[-1].tolist() == [True, False]

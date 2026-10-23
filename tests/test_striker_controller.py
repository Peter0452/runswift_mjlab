"""Tests for the two-level striker (controller over frozen walk / kick)."""

import math
from types import SimpleNamespace

import pytest
import torch
from conftest import get_test_device
from rsl_rl.models import MLPModel, RNNModel
from rsl_rl.storage import RolloutStorage
from tensordict import TensorDict

from mjlab.envs import ManagerBasedRlEnv
from mjlab.tasks.registry import load_env_cfg
from mjlab.tasks.velocity.mdp import striker_skills as skills
from mjlab.tasks.velocity.mdp.self_play import (
  OpponentPolicyAction,
  OpponentPolicyActionCfg,
  OpponentSeedCfg,
  frozen_policy_from_state_dict,
  race_time,
)
from mjlab.tasks.velocity.rl.selfplay_runner import clamp_action_std
from mjlab.tasks.velocity.rl.striker_runner import (
  MemoryResetPPO,
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


def test_walk_arcs_toward_a_direction_behind():
  # Behind: forward at a third of the speed while turning, not backing up.
  cmd = skills.walk_command(torch.tensor([3.0, 0.0]), torch.tensor([1.0, 1.0]))
  vmax = skills.WALK_SPEED_MAX
  assert abs(float(cmd[0, 0]) - skills.WALK_TURN_SPEED_SHARE * vmax) < 1e-6
  assert abs(float(cmd[0, 2]) - skills.WALK_TURN_MAX) < 1e-6
  torch.testing.assert_close(cmd[1], torch.tensor([vmax, 0.0, 0.0]))


def test_walk_velocity_command_is_direct_and_capped():
  a = torch.tensor([[0.0, 1.0, -0.5, 1.0], [0.0, -1.0, 1.0, -0.2]])
  cmd = skills.walk_velocity_command(a)
  want = torch.tensor(
    [
      [skills.WALK_VEL_FORWARD, -0.5 * skills.WALK_VEL_LATERAL, skills.WALK_VEL_TURN],
      [-skills.WALK_VEL_BACKWARD, skills.WALK_VEL_LATERAL, -0.2 * skills.WALK_VEL_TURN],
    ]
  )
  torch.testing.assert_close(cmd, want)
  caps = torch.tensor([[0.5, 0.3, 0.4]] * 2)
  capped = skills.walk_velocity_command(a, caps)
  torch.testing.assert_close(capped[0], torch.tensor([0.5, -0.3, 0.4]))
  torch.testing.assert_close(capped[1], torch.tensor([-0.5, 0.3, -0.3]))


def test_race_time_counts_distance_and_turn():
  def robot(x, yaw):
    q = [math.cos(yaw / 2), 0.0, 0.0, math.sin(yaw / 2)]
    return SimpleNamespace(
      data=SimpleNamespace(
        root_link_pos_w=torch.tensor([[x, 0.0, 0.5]]),
        root_link_quat_w=torch.tensor([q]),
      )
    )

  ball = torch.tensor([[2.0, 0.0]])
  caps = torch.tensor([[1.0, 0.5, 1.0]])
  facing = race_time(robot(0.0, 0.0), ball, caps)  # type: ignore[arg-type]
  away = race_time(robot(0.0, math.pi), ball, caps)  # type: ignore[arg-type]
  torch.testing.assert_close(facing, torch.tensor([2.0]))
  torch.testing.assert_close(away, torch.tensor([2.0 + math.pi]))


def test_held_direction_stays_fixed_in_the_world():
  # Decided 0.5 rad left at heading 0; after the robot turns 0.3 rad left the
  # same world direction is 0.2 rad left of it, and wraps past pi.
  theta = torch.tensor([0.5, 3.0])
  yaw0 = torch.tensor([0.0, 0.0])
  yaw = torch.tensor([0.3, -0.5])
  got = skills.held_direction(theta, yaw0, yaw)
  torch.testing.assert_close(got, torch.tensor([0.2, 3.5 - 2 * math.pi]))


def test_controller_sees_memory_until_disproved():
  obs = torch.zeros(3, 86)
  obs[:, 72:75] = torch.tensor([1.0, 2.0, 0.3])  # the skills' (virtual) ball
  lost = torch.tensor([False, True, True])
  disproved = torch.tensor([False, False, True])
  memory = torch.tensor([[-2.0, 0.5]] * 3)
  age = torch.full((3,), 0.4)
  out = skills.controller_ball_obs(obs, lost, disproved, memory, age)
  torch.testing.assert_close(out[0, 72:75], torch.tensor([1.0, 2.0, 0.3]))
  torch.testing.assert_close(out[1, 72:75], torch.tensor([-2.0, 0.5, 0.4]))
  torch.testing.assert_close(out[2, 72:75], torch.zeros(3))
  assert float(obs[1, 72]) == 1.0  # the skills' inputs are untouched


def _gru_actor() -> RNNModel:
  obs = TensorDict({"actor": torch.zeros(3, 88)}, batch_size=[3])
  model = RNNModel(
    obs,
    {"actor": ["actor"]},
    "actor",
    skills.CONTROLLER_ACTION_DIM,
    hidden_dims=(128,),
    obs_normalization=True,
    distribution_cfg={
      "class_name": "rsl_rl.modules.distribution:GaussianDistribution",
      "init_std": 0.5,
    },
    rnn_type="gru",
    rnn_hidden_dim=32,
  )
  # A non-identity normalizer, as a trained controller has.
  model.update_normalization(
    TensorDict({"actor": torch.randn(64, 88) * 2.0 + 1.0}, batch_size=[64])
  )
  return model.eval()


def test_frozen_gru_matches_rsl_rl():
  model = _gru_actor()
  frozen = frozen_policy_from_state_dict(model.state_dict(), "controller", "gru", "cpu")
  assert frozen.in_dim == 88 and frozen.hidden_dim == 32
  h = None
  with torch.no_grad():
    for _ in range(4):
      x = torch.randn(3, 88)
      want = model(TensorDict({"actor": x}, batch_size=[3]))
      got, h = frozen.step(x, h)
      torch.testing.assert_close(got, want, rtol=1e-4, atol=1e-5)


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
  # Episode-end resets only, so memory tests are deterministic.
  opp.memory_reset_mean_s = None
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


@pytest.mark.slow
def test_opponent_gru_memory_lasts_an_episode(venv):
  opp = venv.unwrapped.action_manager.get_term("opponent")
  assert isinstance(opp, OpponentPolicyAction)
  opp.set_latest(_gru_actor().state_dict())
  opp.slot[:] = 0
  opp.ctrl_wait[:] = 0
  zero = torch.zeros(2, 4, device=venv.device)
  venv.step(zero)
  assert opp.ctrl_h.shape == (2, 32) and bool(opp.ctrl_h.abs().sum(-1).gt(0).all())
  opp.reset(torch.tensor([1], device=venv.device))
  assert float(opp.ctrl_h[1].abs().sum()) == 0.0
  assert float(opp.ctrl_h[0].abs().sum()) > 0.0


@pytest.mark.slow
def test_kickoff_zeroes_opponent_gru_memory(venv):
  opp = venv.unwrapped.action_manager.get_term("opponent")
  assert isinstance(opp, OpponentPolicyAction)
  opp.set_latest(_gru_actor().state_dict())
  opp.slot[:] = 0
  opp.ctrl_wait[:] = 0
  venv.step(torch.zeros(2, 4, device=venv.device))
  assert bool(opp.ctrl_h.abs().sum(-1).gt(0).all())
  opp.cfg.memory_reset_mean_s = 5.0
  try:
    opp._restart(torch.tensor([0], device=venv.device))
  finally:
    opp.cfg.memory_reset_mean_s = None
  assert float(opp.ctrl_h[0].abs().sum()) == 0.0
  assert float(opp.ctrl_h[1].abs().sum()) > 0.0


@pytest.mark.slow
def test_wrapper_reports_memory_resets(venv):
  venv.memory_reset_prob = 1.0
  try:
    _, _, dones, extras = venv.step(torch.zeros(2, 4, device=venv.device))
  finally:
    venv.memory_reset_prob = None
  assert extras["memory_reset"].tolist() == (dones == 0).tolist()


@pytest.mark.slow
def test_wrapper_gives_the_controller_its_ball_view(venv):
  cmd = venv.command
  venv.controller_ball_memory = True
  cmd.ball_lost[:] = True
  cmd.never_seen[:] = False
  cmd.memory_disproved[:] = torch.tensor([False, True], device=venv.device)
  cmd.memory_ball_b[:] = torch.tensor([-2.0, 0.5], device=venv.device)
  cmd.time_since_seen[:] = 2.0
  skills_obs = venv.unwrapped.observation_manager.compute()["actor"]
  obs = venv.get_observations()["actor"]
  age = float(torch.exp(torch.tensor(-2.0 / cmd.cfg.ball_memory_tau)))
  want = torch.tensor([[-2.0, 0.5, age], [0.0, 0.0, 0.0]], device=venv.device)
  torch.testing.assert_close(obs[:, 72:75], want)
  torch.testing.assert_close(obs[:, :72], skills_obs[:, :72])


@pytest.mark.slow
def test_overlay_draws_the_controller_decisions(venv):
  calls: list[tuple[str, str | None]] = []

  class _Vis:
    env_idx, show_all_envs = 0, True

    def get_env_indices(self, n):
      return range(n)

    def __getattr__(self, name):
      return lambda *a, label=None, **k: calls.append((name, label))

  venv.step(torch.tensor([[1.0, 1.0, 0.0, 0.0], [-1.0, 0.0, 1.0, 0.0]]).to(venv.device))
  venv.command._draw_controllers(_Vis(), [0, 1])
  labels = [label for _, label in calls]
  assert labels.count("skill") >= 2 and labels.count("command") >= 2


def test_memory_reset_ppo_replays_the_rollout():
  """The update recomputes the rollout's actions through mid-episode resets
  (and would not without splitting there)."""
  torch.manual_seed(0)
  n, steps = 4, 6
  obs = TensorDict(
    {"actor": torch.randn(n, 88), "critic": torch.randn(n, 90)}, batch_size=[n]
  )
  groups = {"actor": ["actor"], "critic": ["critic"]}
  actor = RNNModel(
    obs,
    groups,
    "actor",
    4,
    hidden_dims=(16,),
    distribution_cfg={
      "class_name": "rsl_rl.modules.distribution:GaussianDistribution",
      "init_std": 0.5,
    },
    rnn_type="gru",
    rnn_hidden_dim=8,
  )
  critic = MLPModel(obs, groups, "critic", 1, hidden_dims=(16,))
  storage = RolloutStorage("rl", n, steps, obs, [4], "cpu")
  alg = MemoryResetPPO(actor, critic, storage, num_mini_batches=1)
  reset_at = {1: [0, 2], 3: [1]}
  with torch.inference_mode():
    for t in range(steps):
      obs = TensorDict(
        {"actor": torch.randn(n, 88), "critic": torch.randn(n, 90)}, batch_size=[n]
      )
      alg.act(obs)
      reset = torch.zeros(n, dtype=torch.bool)
      reset[reset_at.get(t, [])] = True
      dones = torch.zeros(n, dtype=torch.long)
      dones[3] = int(t == 2)
      alg.process_env_step(obs, torch.zeros(n), dones, {"memory_reset": reset})
  splits = alg._memory_splits
  assert splits is not None and int(splits.sum()) == 3

  def replay_error(split: bool) -> float:
    dones = storage.dones
    storage.dones = dones | splits if split else dones
    try:
      batch = next(storage.recurrent_mini_batch_generator(1, 1))
    finally:
      storage.dones = dones
    with torch.no_grad():
      actor(
        batch.observations,
        masks=batch.masks,
        hidden_state=batch.hidden_states[0],
        stochastic_output=True,
      )
      mean = actor.output_distribution_params[0]
    return float((mean - batch.old_distribution_params[0]).abs().max())

  assert replay_error(split=True) < 1e-5
  assert replay_error(split=False) > 1e-3


def test_copies_sample_with_the_clamped_learner_std():
  state = _gru_actor().state_dict()
  state["distribution.std_param"] = torch.tensor([0.4, 0.3, 0.002, 0.5])
  clamped = clamp_action_std(state, (0.15, 1.0))
  frozen = frozen_policy_from_state_dict(clamped, "controller", "copy", "cpu")
  assert frozen.action_std is not None
  torch.testing.assert_close(frozen.action_std, torch.tensor([[0.4, 0.3, 0.15, 0.5]]))
  assert clamp_action_std(state, None) is state


@pytest.mark.slow
def test_mirror_samples_and_seeds_do_not(venv):
  opp = venv.unwrapped.action_manager.get_term("opponent")
  assert isinstance(opp, OpponentPolicyAction)
  opp.set_latest(clamp_action_std(_gru_actor().state_dict(), (0.15, 1.0)))
  out = torch.zeros(4096, 4, device=venv.device)
  noisy = opp._sample(0, out)
  assert 0.4 < float(noisy.std()) < 0.6  # init_std 0.5 per output
  seed = opp._num_fixed - 1
  torch.testing.assert_close(opp._sample(seed, out), out)
  opp.cfg.sample_copies = False
  torch.testing.assert_close(opp._sample(0, out), out)
  opp.cfg.sample_copies = True


@pytest.mark.slow
def test_opponent_ball_detection_is_delayed_as_the_learners(venv):
  opp = venv.unwrapped.action_manager.get_term("opponent")
  cmd = venv.unwrapped.command_manager.get_term("twist")
  assert isinstance(opp, OpponentPolicyAction)
  assert opp._det_hist_b.shape[1] == cmd.cfg.vision_delay_steps[1] + 1
  opp.reset(torch.arange(venv.num_envs, device=venv.device))
  lo, hi = cmd.cfg.vision_delay_steps
  assert bool(((opp._det_lag >= lo) & (opp._det_lag <= hi)).all())

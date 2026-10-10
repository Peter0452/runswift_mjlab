"""Tests for 1v1 self-play on the stage-3 kick loop."""

from types import SimpleNamespace

import pytest
import torch
from conftest import get_test_device
from rsl_rl.models import MLPModel
from tensordict import TensorDict

from mjlab.envs import ManagerBasedRlEnv
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg
from mjlab.tasks.velocity.mdp.self_play import (
  OpponentPolicyAction,
  OpponentPolicyActionCfg,
  OpponentSeedCfg,
  SelfPlayKickCommand,
  load_frozen_policy,
  resolve_checkpoint,
)
from mjlab.tasks.velocity.rl.selfplay_runner import (
  SelfPlayAmpOnPolicyRunner,
  SelfPlayAmpRunnerCfg,
)

TASK = "Mjlab-Velocity-Kick-SelfPlay-Amp-DA-Muon-Booster-K1"
# Tracked checkpoints with the same layouts as the defaults.
KICK_CKPT = "logs/rsl_rl/k1_kick_stage3_amp/blends/x4_g004_70.pt"
WALK_CKPT = (
  "logs/rsl_rl/k1_velocity_amp_symmetric_muon_wwcmu45_roughft/"
  "2026-09-21_09-46-12_trk275/model_9950.pt"
)


def test_frozen_policy_matches_rsl_rl_actor():
  ckpt = torch.load(resolve_checkpoint(KICK_CKPT), weights_only=False)
  obs = TensorDict({"actor": torch.zeros(1, 83)}, batch_size=[1])
  actor = MLPModel(
    obs,
    {"actor": ["actor"]},
    "actor",
    22,
    hidden_dims=(512, 256, 128),
    obs_normalization=True,
    distribution_cfg={
      "class_name": "rsl_rl.modules.distribution:GaussianDistribution",
      "init_std": 1.0,
    },
  )
  actor.load_state_dict(ckpt["actor_state_dict"])
  frozen = load_frozen_policy(KICK_CKPT, "kick", "cpu")
  x = torch.randn(16, 83)
  batch = TensorDict({"actor": x}, batch_size=[16])
  torch.testing.assert_close(frozen(x), actor(batch), rtol=1e-5, atol=1e-5)


def test_selfplay_config():
  cfg = load_env_cfg(TASK)
  assert "opponent" in cfg.scene.entities
  assert "push_near_ball" not in cfg.events
  assert "ball_relocate_unseen" not in cfg.events
  assert cfg.rewards["contest_score"].weight > 0
  assert cfg.rewards["contest_concede"].weight < 0
  rl = load_rl_cfg(TASK)
  assert isinstance(rl, SelfPlayAmpRunnerCfg)
  assert rl.experiment_name == "k1_kick_selfplay_amp"
  assert rl.init_checkpoint is not None


@pytest.fixture(scope="module")
def env():
  cfg = load_env_cfg(TASK)
  cfg.scene.num_envs = 2
  # The AMP motion reset needs the motion dataset; a default-pose reset is
  # enough here.
  cfg.events.pop("reset_robot_from_motion")
  opp = cfg.actions["opponent"]
  assert isinstance(opp, OpponentPolicyActionCfg)
  opp.latest_init_checkpoint = KICK_CKPT
  opp.seeds = (OpponentSeedCfg(KICK_CKPT, "kick"), OpponentSeedCfg(WALK_CKPT, "walk"))
  opp.max_snapshots = 2
  env = ManagerBasedRlEnv(cfg=cfg, device=get_test_device())
  env.reset()
  yield env
  env.close()


def _parts(env):
  cmd = env.command_manager.get_term("twist")
  opp = env.action_manager.get_term("opponent")
  assert isinstance(cmd, SelfPlayKickCommand)
  assert isinstance(opp, OpponentPolicyAction)
  return cmd, opp


def _put_ball(env, env_id: int, xy: torch.Tensor) -> None:
  ball = env.scene["ball"]
  ids = torch.tensor([env_id], device=env.device)
  state = ball.data.default_root_state[ids].clone()
  state[:, :2] = xy
  state[:, 2] = ball.data.root_link_pos_w[ids, 2]
  state[:, 3:] = 0.0
  state[:, 3] = 1.0
  ball.write_root_state_to_sim(state, env_ids=ids)


def _zero_action(env):
  return torch.zeros(
    env.num_envs, env.action_manager.total_action_dim, device=env.device
  )


@pytest.mark.slow
def test_learner_layout_unchanged(env):
  assert env.action_manager.total_action_dim == 22
  obs = env.observation_manager.compute()
  assert obs["actor"].shape[-1] == 83


@pytest.mark.slow
@pytest.mark.parametrize("goal", ["target", "own"])
def test_point_outcome_pays_and_restarts(env, goal):
  cmd, opp = _parts(env)
  goal_w = cmd.target_w if goal == "target" else cmd.own_goal_w
  old_goal = goal_w[0].clone()
  _put_ball(env, 0, old_goal)
  env.step(_zero_action(env))
  won = cmd.contest_scored[0] if goal == "target" else cmd.contest_conceded[0]
  assert bool(won)
  # The kickoff moved the ball off the goal and flagged the opponent.
  assert bool(cmd.kickoff_pending[0])
  _, reward, *_ = env.step(_zero_action(env))
  term = "contest_score" if goal == "target" else "contest_concede"
  paid = env.reward_manager._step_reward[0, env.reward_manager.active_terms.index(term)]
  assert paid != 0.0
  assert not bool(cmd.kickoff_pending[0])
  ball_xy = env.scene["ball"].data.root_link_pos_w[0, :2]
  assert (ball_xy - old_goal).norm() > 0.5


@pytest.mark.slow
def test_snapshot_pool_and_runner_sync(env, tmp_path):
  _, opp = _parts(env)
  fixed = opp._num_fixed
  policy = load_frozen_policy(KICK_CKPT, "kick", env.device)
  state = torch.load(resolve_checkpoint(KICK_CKPT), weights_only=False)[
    "actor_state_dict"
  ]
  runner = SelfPlayAmpOnPolicyRunner.__new__(SelfPlayAmpOnPolicyRunner)
  runner.__dict__.update(
    cfg={"snapshot_interval": 2, "opponent_action_name": "opponent"},
    env=SimpleNamespace(unwrapped=env),
    alg=SimpleNamespace(get_policy=lambda: SimpleNamespace(state_dict=lambda: state)),
    logger=SimpleNamespace(writer=object(), log_dir=str(tmp_path)),
  )
  for it in range(6):
    runner._on_policy_update(it)
  # Snapshots at iterations 2, 4 and 6; the pool keeps the newest two.
  assert [p.name for p in opp.slots[fixed:]] == ["iter_4", "iter_6"]
  assert sorted(p.name for p in (tmp_path / "opponents").iterdir()) == [
    "iter_2.pt",
    "iter_4.pt",
    "iter_6.pt",
  ]
  x = torch.randn(4, 83, device=env.device)
  torch.testing.assert_close(opp.slots[0](x), policy(x))
  assert int(opp.slot.max()) < len(opp.slots)
  env.step(_zero_action(env))


@pytest.mark.slow
def test_referee_stands_up_fallen_opponent(env):
  _, opp = _parts(env)
  entity = env.scene["opponent"]
  ids = torch.tensor([1], device=env.device)
  state = entity.data.default_root_state[ids].clone()
  state[:, :2] = entity.data.root_link_pos_w[ids, :2]
  state[:, 2] = 0.15
  # Lying on its back: pitched 90 degrees.
  state[:, 3:7] = torch.tensor([[0.7071, 0.0, 0.7071, 0.0]], device=env.device)
  state[:, 7:] = 0.0
  entity.write_root_state_to_sim(state, env_ids=ids)
  steps = int(opp.cfg.getup_after_s / env.step_dt) + 2
  for _ in range(steps):
    env.step(_zero_action(env))
  assert float(entity.data.projected_gravity_b[1, 2]) < -0.9

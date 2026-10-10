"""Tests for 1v1 self-play on the stage-3 kick loop."""

from types import SimpleNamespace
from typing import Any, cast

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
  augment_symmetries_selfplay,
  frozen_policy_from_state_dict,
  load_frozen_policy,
  pad_input_columns,
  place_upright,
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
def test_learner_layout(env):
  """Stage 3's 83 / 98 inputs, then the opponent detection; 22 actions."""
  assert env.action_manager.total_action_dim == 22
  obs = env.observation_manager.compute()
  assert obs["actor"].shape[-1] == 86
  assert obs["critic"].shape[-1] == 101


def test_padded_stage3_checkpoint_keeps_its_output():
  frozen = load_frozen_policy(KICK_CKPT, "kick", "cpu")
  state = torch.load(resolve_checkpoint(KICK_CKPT), weights_only=False)
  wide = pad_input_columns(state["actor_state_dict"], 86)
  assert wide["mlp.0.weight"].shape[1] == 86
  x = torch.randn(8, 86)
  padded = frozen_policy_from_state_dict(wide, "kick", "wide", "cpu")
  torch.testing.assert_close(padded(x), frozen(x[:, :83]))
  # Changing only the detection inputs changes nothing yet.
  y = x.clone()
  y[:, 83:] = torch.randn(8, 3) * 5
  torch.testing.assert_close(padded(y), padded(x))


def test_symmetry_mirrors_detection():
  actor = torch.randn(4, 86)
  critic = torch.randn(4, 101)
  obs = TensorDict({"actor": actor, "critic": critic}, batch_size=[4])
  out, _ = augment_symmetries_selfplay(cast(Any, None), obs, None)
  assert out is not None
  assert out["actor"].shape == (8, 86)
  torch.testing.assert_close(out["actor"][:4], actor)
  torch.testing.assert_close(out["actor"][4:, 83], actor[:, 83])
  torch.testing.assert_close(out["actor"][4:, 84], -actor[:, 84])
  torch.testing.assert_close(out["critic"][4:, 99], -critic[:, 99])


@pytest.mark.slow
def test_opponent_detected_in_view_only(env):
  cmd, _ = _parts(env)
  robot, opp = env.scene["robot"], env.scene["opponent"]
  ids = torch.arange(env.num_envs, device=env.device)
  pose = robot.data.root_link_pos_w[:, :2]
  q = robot.data.root_link_quat_w
  yaw = torch.atan2(
    2 * (q[:, 0] * q[:, 3] + q[:, 1] * q[:, 2]), 1 - 2 * (q[:, 2] ** 2 + q[:, 3] ** 2)
  )
  heading = torch.stack((yaw.cos(), yaw.sin()), -1)
  for sign, seen in ((1.0, True), (-1.0, False)):
    place_upright(opp, ids, pose + sign * 2.5 * heading, yaw, env.scene.env_origins)
    env.sim.forward()
    cmd.cfg.opponent_dropout = 0.0
    cmd._update_command()
    det = cmd.opponent_detection
    assert bool((det[:, 2] > 0.5).all()) is seen
    if seen:
      # About 2.5 m ahead in the robot frame.
      assert bool(((det[:, 0] - 2.5).abs() < 0.6).all())
      assert bool((det[:, 1].abs() < 0.6).all())
    else:
      assert bool((det == 0.0).all())


@pytest.mark.slow
@pytest.mark.parametrize("goal", ["target", "own"])
def test_point_outcome_pays_and_restarts(env, goal):
  cmd, opp = _parts(env)
  goal_w = cmd.target_w if goal == "target" else cmd.own_goal_w
  old_goal = goal_w[0].clone()
  old_own = cmd.own_goal_w[0].clone()
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
  # A new point: new goals, and the ball in neither.
  assert (cmd.own_goal_w[0] - old_own).norm() > 1e-3
  ball_xy = env.scene["ball"].data.root_link_pos_w[0, :2]
  assert (ball_xy - cmd.target_w[0]).norm() > cmd.goal_tol[0]
  assert (ball_xy - cmd.own_goal_w[0]).norm() > cmd.own_goal_tol[0]


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

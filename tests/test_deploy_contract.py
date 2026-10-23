"""The deployed tasks' training configs match the runner contract
(k1/deploy/contract.py, knowledge/deployment.md)."""

import re

import pytest

import mjlab.tasks  # noqa: F401
from k1.deploy import contract
from k1.robot.k1_whirlwind_constants import HOME_KEYFRAME, K1_ACTION_SCALE
from mjlab.tasks.registry import load_env_cfg

WALK = "Mjlab-Velocity-Rough-Amp-DA-Muon-Booster-K1"
# The kick-loop family trains with the runner's deployment match.
KICK_FAMILY = (
  "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1",
  "Mjlab-Velocity-Dribble-Amp-DA-Muon-Booster-K1",
  "Mjlab-Velocity-Kick-SelfPlay-Amp-DA-Muon-Booster-K1",
)


def _value_for(table: dict, joint: str):
  hits = [v for pattern, v in table.items() if re.fullmatch(pattern, joint)]
  assert len(hits) == 1, (joint, hits)
  return hits[0]


def test_robot_constants_match_the_contract() -> None:
  for joint in contract.JOINT_ORDER:
    assert _value_for(K1_ACTION_SCALE, joint) == pytest.approx(
      _value_for(contract.ACTION_SCALE, joint), abs=1e-6
    )
  assert HOME_KEYFRAME.joint_pos == contract.DEFAULT_POSE


@pytest.mark.parametrize("task", (WALK, *KICK_FAMILY))
def test_rate_pd_and_joint_order(task: str) -> None:
  cfg = load_env_cfg(task)
  assert cfg.decimation == contract.DECIMATION
  assert cfg.sim.mujoco.timestep == contract.PHYSICS_DT
  assert round(1.0 / (cfg.decimation * cfg.sim.mujoco.timestep)) == contract.RATE_HZ
  spec = cfg.scene.entities["robot"].spec_fn()
  model = spec.compile()
  joints = tuple(
    model.joint(i).name for i in range(model.njnt) if model.jnt_type[i] != 0
  )
  assert joints == contract.JOINT_ORDER
  for act in cfg.scene.entities["robot"].articulation.actuators:
    for pattern in act.target_names_expr:
      joint = next(j for j in contract.JOINT_ORDER if re.fullmatch(pattern, j))
      assert (act.stiffness, act.damping) == _value_for(contract.PD_GAINS, joint)


@pytest.mark.parametrize("task", KICK_FAMILY)
def test_kick_family_deployment_match(task: str) -> None:
  cfg = load_env_cfg(task)
  assert cfg.actions["joint_pos"].clip == contract.DEPLOY_Q_LIMITS
  for act in cfg.scene.entities["robot"].articulation.actuators:
    lag = (act.delay_min_lag, act.delay_max_lag)
    assert lag == contract.MOTOR_DELAY_STEPS, act.target_names_expr
    clip = contract.LEG_TORQUE_CLIP.get(act.target_names_expr[0])
    if clip is not None:
      assert act.effort_limit <= clip

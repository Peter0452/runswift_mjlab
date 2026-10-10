"""1v1 self-play on the stage-3 kick loop (``mdp.self_play``)."""

from __future__ import annotations

import dataclasses

from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.envs.mdp.actions import JointPositionActionCfg
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.tasks.velocity import mdp
from mjlab.tasks.velocity.mdp.self_play import (
  SELFPLAY_KICK_CKPT,
  OpponentPolicyActionCfg,
  SelfPlayKickCommandCfg,
)
from mjlab.tasks.velocity.rl.selfplay_runner import SelfPlayAmpRunnerCfg

from .env_cfgs import booster_k1_kick_stage3_env_cfg
from .rl_cfg import booster_k1_kick_stage3_runner_cfg

# Per point, paid once (value × weight × dt): ±20, the size of a fall.
CONTEST_SCORE_WEIGHT = 1000.0
CONTEST_CONCEDE_WEIGHT = -1000.0


def booster_k1_kick_selfplay_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Stage 3 with a second K1 that attacks the learner's goal.

  The learner's observations, actions and rewards are those of stage 3, plus
  a reward per point won or lost. The opponent replaces the scripted contact
  events (pushes near the ball, an unseen ball moved away).
  """
  cfg = booster_k1_kick_stage3_env_cfg(play=play)

  # Same robot as the learner after every stage-3 change (torque clip, delays,
  # feet). The initial pose is overwritten at each kickoff; the offset only
  # keeps the two apart when the scene is built.
  robot = cfg.scene.entities["robot"]
  x, y, z = robot.init_state.pos
  cfg.scene.entities["opponent"] = dataclasses.replace(
    robot, init_state=dataclasses.replace(robot.init_state, pos=(x + 3.0, y, z))
  )
  cfg.sim.nconmax = 2 * (cfg.sim.nconmax or 80)
  cfg.sim.njmax = 2 * (cfg.sim.njmax or 1500)

  assert cfg.commands is not None
  old = cfg.commands["twist"]
  cfg.commands["twist"] = SelfPlayKickCommandCfg(
    **{f.name: getattr(old, f.name) for f in dataclasses.fields(old) if f.init}
  )

  joint = cfg.actions["joint_pos"]
  assert isinstance(joint, JointPositionActionCfg)
  cfg.actions["opponent"] = OpponentPolicyActionCfg(
    joint_action=JointPositionActionCfg(
      entity_name="opponent",
      actuator_names=joint.actuator_names,
      scale=joint.scale,
      offset=joint.offset,
      clip=joint.clip,
      preserve_order=joint.preserve_order,
      use_default_offset=joint.use_default_offset,
    ),
    obs_noise=not play,
  )
  if play:
    # Play needs one checkpoint: the learner meets the frozen warm start.
    opponent = cfg.actions["opponent"]
    assert isinstance(opponent, OpponentPolicyActionCfg)
    opponent.seeds = ()
    opponent.latest_prob = 1.0
    cfg.events.pop("push_robot", None)

  for name in ("push_near_ball", "ball_relocate_unseen"):
    cfg.events.pop(name, None)

  cfg.rewards["contest_score"] = RewardTermCfg(
    func=mdp.contest_score, weight=CONTEST_SCORE_WEIGHT
  )
  cfg.rewards["contest_concede"] = RewardTermCfg(
    func=mdp.contest_concede, weight=CONTEST_CONCEDE_WEIGHT
  )
  return cfg


def booster_k1_kick_selfplay_runner_cfg() -> SelfPlayAmpRunnerCfg:
  """Stage-3 runner, warm-started from the stage-3 blend."""
  base = booster_k1_kick_stage3_runner_cfg()
  cfg = SelfPlayAmpRunnerCfg(
    **{
      f.name: getattr(base, f.name)
      for f in dataclasses.fields(base)
      if f.init and f.name != "class_name"
    }
  )
  cfg.experiment_name = "k1_kick_selfplay_amp"
  cfg.run_name = "selfplay"
  cfg.init_checkpoint = SELFPLAY_KICK_CKPT
  return cfg

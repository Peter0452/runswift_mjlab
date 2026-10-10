"""1v1 self-play on the stage-3 kick loop (``mdp.self_play``)."""

from __future__ import annotations

import dataclasses

from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.envs.mdp.actions import JointPositionActionCfg
from mjlab.managers.observation_manager import ObservationTermCfg
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.rl import RslRlModelCfg, RslRlPpoAlgorithmCfg
from mjlab.tasks.velocity import mdp
from mjlab.tasks.velocity.mdp.self_play import (
  SELFPLAY_KICK_CKPT,
  OpponentPolicyActionCfg,
  SelfPlayKickCommandCfg,
)
from mjlab.tasks.velocity.rl.selfplay_runner import SelfPlayAmpRunnerCfg
from mjlab.tasks.velocity.rl.striker_runner import StrikerControllerRunnerCfg

from .env_cfgs import booster_k1_kick_stage3_env_cfg
from .rl_cfg import booster_k1_kick_stage3_runner_cfg

# Per goal, paid once (value × weight × dt): ±30, the stage-3 goal payoff
# (kick_goal, off here: it paid a ball passing near a point target).
CONTEST_SCORE_WEIGHT = 1500.0
CONTEST_CONCEDE_WEIGHT = -1500.0
# Ball carried towards goal in possession: 1 m/s pays 4/s, near walk_speed.
DRIBBLE_WEIGHT = 4.0


def booster_k1_kick_selfplay_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Stage 3 as striker against striker on a real field.

  The learner's actions are those of stage 3. Rewards add goals scored and
  conceded and ball carried towards goal in possession, and drop the stage-3
  second-touch penalty and point-target goal. Actor and critic append the opponent as the robot's
  vision reports it (x, y, seen; the critic gets the truth). The opponent
  replaces the scripted contact events (pushes near the ball, an unseen ball
  moved away).
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
    **{f.name: getattr(old, f.name) for f in dataclasses.fields(old) if f.init},
    # Aim lanes across the mouth, as select_target hands them: the striker
    # (and, as a skill, a controller) can then aim anywhere.
    aim_offset=0.4,
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

  # Last in both groups, so the stage-3 slots keep their indices.
  cfg.observations["actor"].terms["opponent"] = ObservationTermCfg(
    func=mdp.opponent_detection
  )
  cfg.observations["critic"].terms["opponent"] = ObservationTermCfg(
    func=mdp.opponent_detection, params={"privileged": True}
  )

  for name in ("push_near_ball", "ball_relocate_unseen"):
    cfg.events.pop(name, None)

  # Outmanoeuvring needs repeated touches: stage 3 charged each second touch
  # (-200) and paid only kicks.
  cfg.rewards["kick_double_touch"].weight = 0.0
  cfg.rewards["kick_goal"].weight = 0.0
  cfg.rewards["dribble_progress"] = RewardTermCfg(
    func=mdp.dribble_progress, weight=DRIBBLE_WEIGHT
  )
  cfg.rewards["contest_score"] = RewardTermCfg(
    func=mdp.contest_score, weight=CONTEST_SCORE_WEIGHT
  )
  cfg.rewards["contest_concede"] = RewardTermCfg(
    func=mdp.contest_concede, weight=CONTEST_CONCEDE_WEIGHT
  )
  return cfg


def booster_k1_kick_selfplay_runner_cfg() -> SelfPlayAmpRunnerCfg:
  """Stage-3 runner, warm-started from the stage-3 blend (the runner pads its
  first layers for the detection inputs)."""
  base = booster_k1_kick_stage3_runner_cfg()
  cfg = SelfPlayAmpRunnerCfg(
    **{
      f.name: getattr(base, f.name)
      for f in dataclasses.fields(base)
      if f.init and f.name != "class_name"
    }
  )
  assert cfg.algorithm.symmetry_cfg is not None
  cfg.algorithm.symmetry_cfg = dict(
    cfg.algorithm.symmetry_cfg,
    data_augmentation_func=(
      "mjlab.tasks.velocity.mdp.self_play:augment_symmetries_selfplay"
    ),
  )
  cfg.experiment_name = "k1_kick_selfplay_amp"
  cfg.run_name = "selfplay"
  cfg.init_checkpoint = SELFPLAY_KICK_CKPT
  return cfg


# Two-level striker (phase 1 of the alternating recipe): only outcome and
# ball terms reach the controller; the skills own posture and smoothness.
CONTROLLER_REWARDS = (
  "contest_score",
  "contest_concede",
  "dribble_progress",
  "kick_vel",
  "kick_direction",
  "kick_vel_accurate",
  "fall",
  "kick_fall",
  "alive",
)


def booster_k1_striker_controller_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """The self-play field with a two-level learner (see ``striker_skills``).

  The policy is the controller; the frozen kick / walk skills are the
  opponent action's ``kick_skill_checkpoint`` / ``walk_skill_checkpoint``,
  shared by both strikers. The opponent's mirror is a controller too.
  """
  cfg = booster_k1_kick_selfplay_env_cfg(play=play)
  twist = cfg.commands["twist"]
  assert isinstance(twist, SelfPlayKickCommandCfg)
  # The controller chooses its own aim; it is told where the goal centre is.
  twist.aim_offset = 0.0
  opponent = cfg.actions["opponent"]
  assert isinstance(opponent, OpponentPolicyActionCfg)
  opponent.latest_kind = "controller"
  opponent.latest_init_checkpoint = None
  for name, term in cfg.rewards.items():
    if name not in CONTROLLER_REWARDS and term is not None:
      term.weight = 0.0
  return cfg


def booster_k1_striker_controller_runner_cfg() -> StrikerControllerRunnerCfg:
  """PPO on the controller at 5 Hz (gamma 0.99 is a ~20 s horizon)."""
  return StrikerControllerRunnerCfg(
    actor=RslRlModelCfg(
      hidden_dims=(256, 128),
      activation="elu",
      obs_normalization=True,
      distribution_cfg={
        "class_name": "rsl_rl.modules.distribution:GaussianDistribution",
        "init_std": 0.5,
      },
    ),
    critic=RslRlModelCfg(
      hidden_dims=(256, 128), activation="elu", obs_normalization=True
    ),
    algorithm=RslRlPpoAlgorithmCfg(
      learning_rate=3.0e-4,
      gamma=0.99,
      lam=0.95,
      entropy_coef=0.005,
      num_learning_epochs=5,
      num_mini_batches=4,
    ),
    num_steps_per_env=24,
    max_iterations=5000,
    save_interval=50,
    experiment_name="k1_striker_controller",
    run_name="controller",
  )

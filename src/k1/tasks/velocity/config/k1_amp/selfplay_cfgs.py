"""1v1 self-play on the stage-3 kick loop (``mdp.self_play``)."""

from __future__ import annotations

import dataclasses

from k1.tasks.velocity import mdp
from k1.tasks.velocity.mdp.kick_loop import (
  HEAD_FULL_SEARCH_PITCH,
  HEAD_FULL_SEARCH_YAW,
)
from k1.tasks.velocity.mdp.self_play import (
  SELFPLAY_KICK_CKPT,
  OpponentPolicyActionCfg,
  SelfPlayKickCommandCfg,
)
from k1.tasks.velocity.rl.anchor import with_anchor
from k1.tasks.velocity.rl.selfplay_runner import SelfPlayAmpRunnerCfg
from k1.tasks.velocity.rl.striker_runner import StrikerControllerRunnerCfg
from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.envs.mdp.actions import JointPositionActionCfg
from mjlab.managers.curriculum_manager import CurriculumTermCfg
from mjlab.managers.observation_manager import ObservationTermCfg
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.rl import RslRlModelCfg, RslRlPpoAlgorithmCfg
from mjlab.sensor import ContactMatch, ContactSensorCfg

from .env_cfgs import booster_k1_kick_stage3_env_cfg
from .rl_cfg import booster_k1_kick_stage3_runner_cfg

# Learner events the opponent gets a copy of (pushes and startup DR).
OPPONENT_DR_EVENTS = (
  "push_robot",
  "foot_friction",
  "encoder_bias",
  "pd_gains",
  "trunk_inertia",
  "limb_inertia",
)
# Per goal, paid once (value × weight × dt): ±30, the stage-3 goal payoff
# (kick_goal, off here: it paid a ball passing near a point target).
# v11: ×3 (±90 per goal). Through v10 the game paid ~+0.4/s scored and
# -0.85/s conceded against several /s of stage-3 shaping, and every run ended
# below h022 in fixed matches (best 0.345 vs 0.386) against every opponent:
# the policy kept optimising the stage-3 objective h022 was already tuned for.
CONTEST_SCORE_WEIGHT = 4500.0
CONTEST_CONCEDE_WEIGHT = -4500.0
# Ball carried towards goal in possession: 1 m/s pays 4/s, near walk_speed.
DRIBBLE_WEIGHT = 4.0
# Ball lost (replaces search_turn): 2/s cancels alive, searching the wrong way
# or not at all costs up to 6/s.
BALL_LOST_WEIGHT = -2.0
# Opponent sampling (p2_kick_v2 settled into slow, passive play against its
# own copies and met the fast h022 in ~4.5 % of games): in the pool h022
# weighs as all 8 snapshots together, the controller half that. Mirror 10 %
# (v4: 20 %, and it overfit to its copy from ~1050: copy win rate 0.54, pool
# 0.40 -> 0.31).
# v12: every run peaked a few hundred iterations after a change, then slid vs
# h022 while beating its own pool (v11: 0.365 -> 0.352 -> 0.336 at
# 2300/2600/3000). Fewer games against itself, more against fixed strong
# opponents: mirror 5 %, snapshots half weight; h022 ~45 %, controller ~23 %.
LATEST_PROB = 0.05
SEED_WEIGHTS = {"kick": 12.0, "walk": 1.0}
CONTROLLER_WEIGHT = 6.0
SNAPSHOT_WEIGHT = 0.5
# Task shaping annealed linearly to zero in favour of the competition reward
# (goals scored / conceded), as in Bansal et al. 2018: the policy trains most
# of the run on the sparse game outcome and handles the ball as the game
# needs, not as the stage-3 drill paid. Deploy-safety, survival, gait, speed
# caps and the ball-lost search stay at full weight. v4 annealed to 0 and its
# attack collapsed as alpha fell (goals 0.22 -> 0.12 by alpha 0.75): the floor
# keeps 20 % of the shaping, as the plan's OpenAI note suggests. v5 (floor
# 0.2) still turned down at alpha ~0.8 (iteration ~1200), with kick quality
# falling from the start (0.29 -> 0.19): goals and territory pay where the
# ball goes, not how well it is struck. Kick technique (kick_direction,
# kick_vel, kick_vel_accurate, kick_rest_accuracy, long_kick_power,
# long_kick_underpower) therefore stays at full weight, held to the kick
# objectives; only where to go and when to play anneals.
ANNEALED_TASK_REWARDS = (
  "kick_lined_up",
  "kick_dir_alignment",
  "approach_align",
  "approach_close",
  "approach_bad_contact",
  "walk_engage",
  "ball_vision",
  "ball_avoidance",
  "dribble_progress",
)
# Iterations (24 env steps each) over which alpha falls from 1 to the floor.
# v13: frozen at alpha 0.57 (its value at v12/2600). Every run peaked a few
# hundred iterations after a fix and then slid vs h022 AND the controller as
# alpha kept falling (v12: 0.36/0.42 at 2600 -> 0.35/0.37 at 2900, alpha
# 0.57 -> 0.53), whatever the opponent mix. Test: does holding alpha stop it?
ANNEAL_ITERATIONS = (0, 2600)
ANNEAL_FLOOR = 0.57
# Ball progress up the field (zero-sum, not annealed): 1 m of net progress
# pays 1.5, so carrying it the length of a 10 m field is half a goal.
TERRITORY_WEIGHT = 3.0  # v11: ×2 with the goals
# Approach pay (replaces stage 3's walk_speed / walk_speed_track, which paid
# following a ball carried away and nothing inside 1.5 m): same scale as
# walk_speed (1 m/s of closing pays 5/s).
WALK_ENGAGE_WEIGHT = 5.0
# v14: taking the ball +6, the opponent taking it -6 (zero-sum, not annealed).
# v13 plateaued below h022 (0.37-0.38 vs 0.40) with goals x3: goals reach the
# decision to commit to a ball too faintly; winning the ball is quick and
# frequent. With gamma 0.998 (~10 s horizon) so race -> kick -> goal counts.
POSSESSION_WEIGHT = 300.0
SELFPLAY_GAMMA = 0.998
# PPO step size for the warm-started self-play kick: a fixed LR. Stage 3's
# adaptive schedule (desired_kl 0.01) drove Muon to ~1.1e-3; a 0.002 target
# (v7) pinned it at the 1e-5 floor, as KL has a ~0.003 floor independent of
# the LR, and learning stalled.
SELFPLAY_LR = 1.0e-4
# Anchor to the warm start (rl.anchor): v9 (walk_engage) peaked vs h022 at
# iteration ~600 (goal share 0.33, 2 seeds) and fell to 0.29 by 1000 while its
# self-play curves still rose: it specialised against its training pool. β
# falls 0.5 -> 0.1 over 5000 iterations; Loss/anchor is the KL in nats (v6/350
# had drifted to 1.25, v5/1100 to 2.14).
ANCHOR_COEF = (0.5, 0.1)
# Reference: v9's best checkpoint vs h022, not h022 itself. Anchored to h022,
# v9/600 started 2.4 nats away (walk_engage changed its approach on purpose)
# and was pulled back toward h022's passive approach (1.6 nats after 3
# iterations).
ANCHOR_CKPT = (
  "logs/rsl_rl/k1_kick_selfplay_amp/2026-10-13_23-24-12_p2_kick_v15_std04/model_7600.pt"
)
ANCHOR_DECAY_ITERATIONS = 5000
# v15: action noise cap 0.6 -> 0.4. Every joint of v14 sat at stage 3's 0.6 cap
# (the entropy bonus holds it there) and v14 plateaued at h022's level from
# ~4500 (training curves flat, evals 0.39-0.42): rollouts that noisy hide the
# small differences between deterministic plays that the sparse game pays.
# v15 (0.4) from v14/5100: vs h022/controller 0.42/0.435 over 6600-8100
# (v14 0.40/0.42) and goals for vs h022 rose past h022's own (0.55 vs 0.525).
# v16: 0.25, from v15/7600.
SELFPLAY_MAX_ACTION_STD = 0.25


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
  # Who touched the ball last decides restarts.
  cfg.scene.sensors = tuple(cfg.scene.sensors) + (
    ContactSensorCfg(
      name="opponent_ball_contact",
      primary=ContactMatch(mode="body", entity="opponent", pattern=r".*"),
      secondary=ContactMatch(mode="body", pattern="ball", entity="ball"),
      fields=("found",),
      reduce="none",
      num_slots=1,
    ),
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
    # The learner's head sweeps instead of tracking in this share of episodes.
    scan_share=float(getattr(joint, "scan_share", 0.0)),
  )
  opponent = cfg.actions["opponent"]
  assert isinstance(opponent, OpponentPolicyActionCfg)
  opponent.latest_prob = LATEST_PROB
  opponent.seeds = tuple(
    dataclasses.replace(seed, weight=SEED_WEIGHTS.get(seed.kind, seed.weight))
    for seed in opponent.seeds
  )
  opponent.controller_weight = CONTROLLER_WEIGHT
  opponent.snapshot_weight = SNAPSHOT_WEIGHT
  # Both heads search the whole head range for a lost ball (the opponent reads
  # the learner's range).
  assert isinstance(joint, mdp.HeadTrackedJointPositionActionCfg)
  joint.search_yaw = HEAD_FULL_SEARCH_YAW
  joint.search_pitch = HEAD_FULL_SEARCH_PITCH

  if play:
    # Play needs one checkpoint: the learner meets the frozen warm start.
    opponent = cfg.actions["opponent"]
    assert isinstance(opponent, OpponentPolicyActionCfg)
    opponent.seeds = ()
    opponent.latest_prob = 1.0
    opponent.sample_copies = False
    cfg.events.pop("push_robot", None)
    cfg.events.pop("push_opponent", None)

  # Last in both groups, so the stage-3 slots keep their indices.
  cfg.observations["actor"].terms["opponent"] = ObservationTermCfg(
    func=mdp.opponent_detection
  )
  cfg.observations["critic"].terms["opponent"] = ObservationTermCfg(
    func=mdp.opponent_detection, params={"privileged": True}
  )

  # The opponent gets the learner's pushes and startup DR (the learner's own
  # DR is never weakened to even the sides).
  for name in OPPONENT_DR_EVENTS:
    term = cfg.events.get(name)
    if term is None:
      continue
    params = dict(term.params or {})
    asset = params.get("asset_cfg", SceneEntityCfg("robot"))
    assert isinstance(asset, SceneEntityCfg) and asset.name == "robot", name
    params["asset_cfg"] = dataclasses.replace(asset, name="opponent")
    target = "push_opponent" if name == "push_robot" else f"{name}_opponent"
    cfg.events[target] = dataclasses.replace(term, params=params)

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
  # p2_kick_v1 farmed search_turn (+10/s while lost): the opponent loses the
  # ball for it far more often than stage 3 did. Losing the ball now costs.
  cfg.rewards["search_turn"].weight = 0.0
  cfg.rewards["ball_lost"] = RewardTermCfg(
    func=mdp.ball_lost_penalty, weight=BALL_LOST_WEIGHT
  )
  assert cfg.curriculum is not None
  start, end = ANNEAL_ITERATIONS
  steps = 24  # env steps per iteration (stage-3 runner num_steps_per_env)
  cfg.curriculum["task_reward_anneal"] = CurriculumTermCfg(
    func=mdp.anneal_rewards,
    params={
      "reward_names": ANNEALED_TASK_REWARDS,
      "start_step": start * steps,
      "end_step": end * steps,
      "final_scale": ANNEAL_FLOOR,
    },
  )
  cfg.rewards["walk_speed"].weight = 0.0
  cfg.rewards["walk_speed_track"].weight = 0.0
  cfg.rewards["possession"] = RewardTermCfg(
    func=mdp.possession_change, weight=POSSESSION_WEIGHT
  )
  cfg.rewards["walk_engage"] = RewardTermCfg(
    func=mdp.walk_engage, weight=WALK_ENGAGE_WEIGHT
  )
  cfg.rewards["territory"] = RewardTermCfg(
    func=mdp.territory_progress, weight=TERRITORY_WEIGHT
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
      "k1.tasks.velocity.mdp.self_play:augment_symmetries_selfplay"
    ),
  )
  cfg.experiment_name = "k1_kick_selfplay_amp"
  cfg.run_name = "selfplay"
  cfg.init_checkpoint = SELFPLAY_KICK_CKPT
  # Stage 3 turns these on. Self-play warm-starts a single-critic checkpoint.
  cfg.decap = False
  cfg.algorithm.multi_critic_alphas = None
  # Fine-tune, not retrain: Muon takes full-size steps whatever the gradient's
  # strength, and at stage 3's desired_kl 0.01 the weak, noisy self-play
  # signal random-walked the policy away from h022 (first layer 26 % changed
  # by iteration 350; fixed-opponent share vs h022 0.39 -> 0.26, v5 at 1100:
  # 0.17).
  cfg.algorithm.schedule = "fixed"
  cfg.algorithm.learning_rate = SELFPLAY_LR
  cfg.algorithm.gamma = SELFPLAY_GAMMA
  assert cfg.actor.distribution_cfg is not None
  cfg.actor.distribution_cfg = dict(
    cfg.actor.distribution_cfg, std_range=(0.05, SELFPLAY_MAX_ACTION_STD)
  )
  cfg.algorithm = with_anchor(
    cfg.algorithm,
    ANCHOR_CKPT,
    coef=ANCHOR_COEF[0],
    coef_final=ANCHOR_COEF[1],
    decay_updates=ANCHOR_DECAY_ITERATIONS,
  )
  return cfg


# Two-level striker: the controller decides when, where and with which skill,
# so only game terms reach it (goals, possession, field position, keeping the
# ball in view) plus safety; the skills own posture and smoothness. Kick
# technique (kick_vel, kick_direction, kick_vel_accurate) is the kick skill's
# job: the controller is paid to score, not to shoot. None of these anneal.
CONTROLLER_REWARDS = (
  "contest_score",
  "contest_concede",
  "possession",
  "territory",
  "dribble_progress",
  "ball_lost",
  "ball_race",
  "fall",
  "kick_fall",
  "alive",
)
# controller_v2 left 93 % of its walk -> kick switches before any kick (about
# 6 per game at -0.05 each). v3/v4 at 1.0 (1/6 of a possession change) all
# but stopped walking (3 %, from 41 %); v5/v6 at 0.25 lost it too (v6 from
# controller_v2: 22 % -> 6 % in 300 iterations). v6b: back to v2's 0.05.
CONTROLLER_SWITCH_COST = 0.05
# v5: +2 per second of ball-race advantage gained (``mdp.ball_race``; a third
# of a possession change). Being first to the ball, which neither possession
# (paid at the touch) nor territory (paid as the ball moves) says until late:
# defence by position, kicking into space, not standing while the opponent
# closes (the stall with the ball beside / behind in v4).
BALL_RACE_WEIGHT = 2.0
# The kick skill both strikers run: the fine-tuned self-play kick (weight mean
# of v15/7600 and v16/8100-9100; flat goal share 0.425 / 0.461 vs h022 /
# controller against h022's 0.399 / 0.455).
CONTROLLER_KICK_SKILL = "logs/rsl_rl/k1_kick_selfplay_amp/swa_v15v16/model_9100.pt"


# The robot's runner zeroes the controller's GRU on every striker takeover, so
# memory never spans a point: zeroed at kickoffs / restarts and at random
# every 5 s on average (BPTT reaches 4.8 s, so it cannot use more anyway).
CONTROLLER_MEMORY_S = 5.0


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
  opponent.memory_reset_mean_s = CONTROLLER_MEMORY_S
  opponent.controller_ball_memory = True
  opponent.controller_walk_velocity = True
  cfg.rewards["ball_race"] = RewardTermCfg(func=mdp.ball_race, weight=BALL_RACE_WEIGHT)
  opponent.kick_skill_checkpoint = CONTROLLER_KICK_SKILL
  for name, term in cfg.rewards.items():
    if name not in CONTROLLER_REWARDS and term is not None:
      term.weight = 0.0
  # Reward curricula would set zeroed terms back (soft_landing came back at
  # -0.005 in controller_v2).
  assert cfg.curriculum is not None
  for name, term in list(cfg.curriculum.items()):
    reward = (term.params or {}).get("reward_name") if term is not None else None
    if reward is not None and reward not in CONTROLLER_REWARDS:
      cfg.curriculum.pop(name)
  cfg.curriculum.pop("task_reward_anneal")
  return cfg


def booster_k1_striker_controller_runner_cfg() -> StrikerControllerRunnerCfg:
  """PPO on the controller at 5 Hz (gamma 0.99 is a ~20 s horizon).

  The actor is a GRU: single-frame detections and a ball memory leave the
  opponent's motion and the play's history to be remembered. Its state is
  zeroed at episode ends, kickoffs and at random (``CONTROLLER_MEMORY_S``);
  backprop is truncated at a rollout (24 decisions, 4.8 s). The critic stays
  feed-forward on the true state.
  """
  return StrikerControllerRunnerCfg(
    actor=RslRlModelCfg(
      class_name="RNNModel",
      rnn_type="gru",
      rnn_hidden_dim=128,
      rnn_num_layers=1,
      hidden_dims=(128,),
      activation="elu",
      obs_normalization=True,
      distribution_cfg={
        "class_name": "rsl_rl.modules.distribution:GaussianDistribution",
        "init_std": 0.5,
        # The direction's sin output collapsed to std 0.002 (run
        # 2026-10-11_11-21-21); KL ~ dmu^2 / std^2 then exploded and the
        # adaptive schedule pinned the learning rate at 1e-5. 0.15 is ~8 deg
        # of steering noise; 0.05 still drove KL past the target. The cap was
        # 1.0 until v5, whose a[3] (kick range) sat at it: as the walk skill's
        # turn rate that is +-1.5 rad/s of noise on every walk, which the
        # controller learned to avoid (walk 3 % of the time). 0.5: +-0.75.
        "std_range": (0.15, 0.5),
      },
    ),
    critic=RslRlModelCfg(
      hidden_dims=(256, 128), activation="elu", obs_normalization=True
    ),
    algorithm=RslRlPpoAlgorithmCfg(
      class_name="k1.tasks.velocity.rl.striker_runner:MemoryResetPPO",
      learning_rate=3.0e-4,
      gamma=0.99,
      lam=0.95,
      # controller_v3 (0.005): the action std rose 0.40 -> 0.48 in 400
      # iterations while goal share was flat; the bonus outweighed the signal.
      entropy_coef=0.001,
      num_learning_epochs=5,
      num_mini_batches=4,
    ),
    num_steps_per_env=24,
    max_iterations=5000,
    save_interval=50,
    switch_cost=CONTROLLER_SWITCH_COST,
    experiment_name="k1_striker_controller",
    run_name="controller",
  )

"""Score task: kick the ball toward a goal target.

Stage 2 of the two-stage soccer pipeline.  Extends the approach env by:
  - Placing the robot already near the ball at reset (no approach needed)
  - Adding a goal position command
  - Adding kick-prior tracking reward (fades out during training)
  - Adding ball-velocity-toward-goal and ball-goal-proximity rewards

Load an approach-task checkpoint to warm-start; or a flat-velocity checkpoint
to skip approach pretraining (convergence will be slower).
"""

from mjlab.entity import EntityCfg
from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.managers.event_manager import EventTermCfg
from mjlab.managers.observation_manager import ObservationTermCfg
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.tasks.kick import mdp as kick_mdp
from mjlab.tasks.kick.mdp.commands import UniformGoalPositionCommandCfg
from mjlab.tasks.kick.mdp.events import reset_ball_relative_to_robot
from mjlab.tasks.velocity.mdp.kick_prior import kick_prior_target, kick_prior_tracking


def make_score_env_cfg(
  base_cfg: ManagerBasedRlEnvCfg,
  kick_style: str = "snap",
) -> ManagerBasedRlEnvCfg:
  """Add ball, goal command, and kick rewards to a flat K1 velocity cfg.

  Args:
    base_cfg: A fully-constructed flat K1 velocity env config.
    kick_style: Which Bézier prior to use (``"snap"``, ``"high"``,
      ``"side"``, ``"back"``, ``"chip"``).

  Returns:
    The modified score-task config.
  """
  from mjlab.asset_zoo.props import get_ball_spec

  # ── Scene: add the ball ──────────────────────────────────────────────────
  base_cfg.scene.entities["ball"] = EntityCfg(spec_fn=get_ball_spec)

  # ── Commands: goal position ──────────────────────────────────────────────
  if base_cfg.commands is None:
    base_cfg.commands = {}
  base_cfg.commands["goal"] = UniformGoalPositionCommandCfg(
    distance_range=(4.0, 8.0),
    resampling_time_range=(10.0, 15.0),
    debug_vis=True,
  )

  # ── Observations ─────────────────────────────────────────────────────────
  ball_obs = ObservationTermCfg(
    func=kick_mdp.ball_relative_position,
    params={
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
      "clip_distance": 5.0,
    },
  )
  goal_dir_obs = ObservationTermCfg(
    func=kick_mdp.goal_direction,
    params={
      "command_name": "goal",
      "robot_cfg": SceneEntityCfg("robot"),
    },
  )
  kick_prior_obs = ObservationTermCfg(
    func=kick_prior_target,
    params={
      "kick": kick_style,
      "period": 1.5,
      "command_name": "twist",
      "command_threshold": 0.05,
      "drop_step": 5_000 * 24,
      "fade_steps": 3_000 * 24,
    },
  )
  for group in ("actor", "critic"):
    base_cfg.observations[group].terms["ball_rel_pos"] = ball_obs
    base_cfg.observations[group].terms["goal_direction"] = goal_dir_obs
    base_cfg.observations[group].terms["kick_prior"] = kick_prior_obs

  # ── Events: robot near ball at episode start ─────────────────────────────
  # Narrow robot-reset range so it always starts near the ball.
  base_cfg.events["reset_base"].params["pose_range"] = {
    "x": (-0.1, 0.1),
    "y": (-0.1, 0.1),
    "z": (0.01, 0.05),
    "yaw": (-0.3, 0.3),  # mostly facing forward
  }

  base_cfg.events["reset_ball"] = EventTermCfg(
    func=reset_ball_relative_to_robot,
    mode="reset",
    params={
      "forward_range": (0.25, 0.45),
      "lateral_range": (-0.08, 0.08),
      "height": 0.11,
      "ball_cfg": SceneEntityCfg("ball"),
      "robot_cfg": SceneEntityCfg("robot"),
    },
  )

  # ── Rewards ──────────────────────────────────────────────────────────────

  # Down-weight generic locomotion; the task reward is ball-toward-goal.
  base_cfg.rewards["track_linear_velocity"].weight = 0.3
  base_cfg.rewards["track_angular_velocity"].weight = 0.3

  # Kick-prior imitation: fades from weight 3 → 0 over the first ~5k iters.
  base_cfg.rewards["kick_prior_tracking"] = RewardTermCfg(
    func=kick_prior_tracking,
    weight=3.0,
    params={
      "kick": kick_style,
      "std": 0.25,
      "period": 1.5,
      "command_name": "twist",
      "command_threshold": 0.05,
      "asset_cfg": SceneEntityCfg("robot"),
      "drop_step": 5_000 * 24,
      "fade_steps": 3_000 * 24,
    },
  )

  # Ball speed in goal direction — the primary task signal.
  base_cfg.rewards["ball_velocity_toward_goal"] = RewardTermCfg(
    func=kick_mdp.ball_velocity_toward_goal,
    weight=4.0,
    params={
      "command_name": "goal",
      "ball_cfg": SceneEntityCfg("ball"),
      "min_speed": 0.3,
    },
  )

  # Dense ball-goal proximity shaping (std = 2 m, broad).
  base_cfg.rewards["ball_goal_proximity"] = RewardTermCfg(
    func=kick_mdp.ball_goal_proximity,
    weight=1.0,
    params={
      "std": 2.0,
      "command_name": "goal",
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )

  # Stay near ball before kicking (don't run away).
  base_cfg.rewards["ball_approach"] = RewardTermCfg(
    func=kick_mdp.ball_approach_reward,
    weight=1.0,
    params={
      "std": 0.8,
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )

  base_cfg.episode_length_s = 10.0  # short episodes: kick happens fast

  if base_cfg.sim.nconmax is not None:
    base_cfg.sim.nconmax = max(base_cfg.sim.nconmax, base_cfg.sim.nconmax + 20)

  return base_cfg

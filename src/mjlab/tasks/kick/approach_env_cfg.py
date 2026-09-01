"""Target-conditioned approach task for the K1 kick pipeline.

The ball is fixed near the centre of each environment.  The robot is reset at
an arbitrary radius around it, initially facing the ball.  A target is sampled
in any direction, and the policy must move to the point behind the ball on the
ball-to-target line while keeping the ball in front of its body.
"""

import math

from mjlab.entity import EntityCfg
from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.envs.mdp.actions.actions import JointPositionActionCfg
from mjlab.managers.curriculum_manager import CurriculumTermCfg
from mjlab.managers.event_manager import EventTermCfg
from mjlab.managers.observation_manager import ObservationTermCfg
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.tasks.kick import mdp as kick_mdp
from mjlab.tasks.kick.mdp.commands import UniformGoalPositionCommandCfg
from mjlab.tasks.kick.mdp.events import (
  reset_ball_uniform,
  reset_robot_around_ball_facing,
  update_approach_twist_command,
)
from mjlab.tasks.velocity import mdp as velocity_mdp
from mjlab.tasks.velocity.config.k1.env_cfgs import (
  _HTWK_EXACT_SHOULDER_ROLL_BAND,
  _NUBOTS_ACTION_SCALE,
  _NUBOTS_SHOULDER_PITCH_BAND,
)

# Deploy-tight shoulder bands: small pitch, arms-down roll (±7.5°).
_APPROACH_SHOULDER_CLIP: dict[str, tuple[float, float]] = {
  "Left_Shoulder_Pitch": (
    -_NUBOTS_SHOULDER_PITCH_BAND,
    _NUBOTS_SHOULDER_PITCH_BAND,
  ),
  "Right_Shoulder_Pitch": (
    -_NUBOTS_SHOULDER_PITCH_BAND,
    _NUBOTS_SHOULDER_PITCH_BAND,
  ),
  "Left_Shoulder_Roll": (
    -1.3 - _HTWK_EXACT_SHOULDER_ROLL_BAND,
    -1.3 + _HTWK_EXACT_SHOULDER_ROLL_BAND,
  ),
  "Right_Shoulder_Roll": (
    1.3 - _HTWK_EXACT_SHOULDER_ROLL_BAND,
    1.3 + _HTWK_EXACT_SHOULDER_ROLL_BAND,
  ),
}


def make_approach_env_cfg(base_cfg: ManagerBasedRlEnvCfg) -> ManagerBasedRlEnvCfg:
  """Add target-conditioned ball approach to a flat K1 velocity cfg.

  Args:
    base_cfg: A fully-constructed flat K1 velocity env config (call
      ``booster_k1_flat_env_cfg()`` then pass the result here).

  Returns:
    The modified config.  The caller should use this as the registered env cfg.
  """
  from mjlab.asset_zoo.props import get_ball_spec

  # ── Scene: add the ball ──────────────────────────────────────────────────
  base_cfg.scene.entities["ball"] = EntityCfg(spec_fn=get_ball_spec)
  # Keep independent 4 m approach circles from visually/physically overlapping.
  base_cfg.scene.env_spacing = max(base_cfg.scene.env_spacing, 10.0)

  # ── Commands: target relative to the ball at the env centre ─────────────
  base_cfg.commands["goal"] = UniformGoalPositionCommandCfg(
    distance_range=(4.0, 8.0),
    angle_range=(-math.pi, math.pi),
    resampling_time_range=(30.0, 30.0),
    debug_vis=True,
  )

  # ── Observations: ball and ball-to-target geometry ──────────────────────
  ball_obs = ObservationTermCfg(
    func=kick_mdp.ball_relative_position,
    params={
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
      "clip_distance": 6.0,
    },
  )
  target_obs = ObservationTermCfg(
    func=kick_mdp.ball_to_goal_direction,
    params={
      "command_name": "goal",
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )
  base_cfg.observations["actor"].terms["ball_rel_pos"] = ball_obs
  base_cfg.observations["critic"].terms["ball_rel_pos"] = ball_obs
  base_cfg.observations["actor"].terms["ball_goal_direction"] = target_obs
  base_cfg.observations["critic"].terms["ball_goal_direction"] = target_obs

  # ── Events: centre the ball, then place robot after goal is sampled ─────
  base_cfg.events["reset_ball"] = EventTermCfg(
    func=reset_ball_uniform,
    mode="reset",
    params={
      "pose_range": {
        "x": (0.0, 0.0),
        "y": (0.0, 0.0),
        "z": (0.11, 0.11),  # ball resting on flat terrain
      },
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )
  base_cfg.events["reset_base"] = EventTermCfg(
    func=reset_robot_around_ball_facing,
    mode="post_reset",
    params={
      # Training starts short; ``spawn_radius`` curriculum expands to 4 m.
      "radius_range": (0.5, 1.0),
      "spawn_on_approach_side": True,
      "goal_command_name": "goal",
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )
  base_cfg.events["approach_twist"] = EventTermCfg(
    func=update_approach_twist_command,
    mode="step",
    params={
      "command_name": "twist",
      "goal_command_name": "goal",
      "target_distance": 0.35,
      "cruise_speed": 1.0,
      "min_speed": 0.35,
      "slow_distance": 0.8,
      "gait_frequency": 2.5,
      "max_ang_vel": 1.4,
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )

  # Velocity kicks are too disruptive while learning approach; trunk pushes
  # every 3–4 s build robustness without knocking the robot off its feet.
  base_cfg.events.pop("kick_robot", None)
  base_cfg.events["push_robot"] = EventTermCfg(
    func=velocity_mdp.booster_push_robots,
    mode="step",
    params={
      "push_interval_range_s": (3.0, 4.0),
      "push_duration_s": 1.0,
      "push_force_std": 8.0,
      "push_torque_std": 1.5,
      "asset_cfg": SceneEntityCfg("robot", body_names=("Trunk",)),
    },
  )

  # Random HTWK twist samples fight the approach objective.  A per-step event
  # overwrites twist with a waypoint-directed command; keep gait frequency on.
  twist = base_cfg.commands["twist"]
  twist.still_proportion = 0.0
  twist.rel_standing_envs = 0.0
  twist.resampling_time_range = (45.0, 45.0)

  # Keep arms in a deploy-safe envelope while learning robust walk + approach.
  # The HTWK base gives shoulders the same 0.8 scale as legs; tighten both
  # the action authority and the deviation penalty so the policy cannot fling
  # arms up/out while closing on the ball.
  action = base_cfg.actions["joint_pos"]
  assert isinstance(action, JointPositionActionCfg)
  action.scale = dict(_NUBOTS_ACTION_SCALE)
  action.clip = dict(_APPROACH_SHOULDER_CLIP)
  base_cfg.rewards["shoulder_deviation"].weight = -4.0
  base_cfg.curriculum.pop("shoulder_release", None)

  # ── Rewards ──────────────────────────────────────────────────────────────

  # The base config is the faithful HTWK/NuBots walking task.  Keep its
  # ParameterWalk command, phase clock, foot orientation/yaw/offset terms,
  # swing reward, and torso stabilization intact; kick shaping is layered on
  # top of that walking objective below.

  # Stay in the kick-distance band: reward 0.35-0.45 m, penalise outside it.
  base_cfg.rewards.pop("ball_approach", None)
  base_cfg.rewards["ball_distance_band"] = RewardTermCfg(
    func=kick_mdp.ball_distance_band,
    weight=3.0,
    params={
      "min_distance": 0.35,
      "max_distance": 0.45,
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )
  base_cfg.rewards["ball_approach_far"] = RewardTermCfg(
    func=kick_mdp.ball_approach_far,
    weight=2.0,
    params={
      "activate_distance": 0.6,
      "std": 2.5,
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )
  base_cfg.rewards["waypoint_approach_velocity"] = RewardTermCfg(
    func=kick_mdp.waypoint_approach_velocity,
    weight=2.5,
    params={
      "target_distance": 0.35,
      "command_name": "goal",
      "activate_ball_distance": 0.55,
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )
  base_cfg.rewards["waypoint_retreat_penalty"] = RewardTermCfg(
    func=kick_mdp.waypoint_retreat_penalty,
    weight=-2.0,
    params={
      "target_distance": 0.35,
      "command_name": "goal",
      "activate_ball_distance": 0.55,
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )

  # The main objective is the target-dependent point behind the ball.
  base_cfg.rewards["behind_ball_waypoint"] = RewardTermCfg(
    func=kick_mdp.behind_ball_waypoint,
    weight=6.0,
    params={
      "target_distance": 0.35,
      "std": 0.50,
      "command_name": "goal",
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )
  base_cfg.rewards["body_face_ball"] = RewardTermCfg(
    func=kick_mdp.body_face_ball,
    weight=1.5,
    params={
      "sigma": 0.60,
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )
  base_cfg.rewards["ball_camera_cone"] = RewardTermCfg(
    func=kick_mdp.ball_camera_cone,
    weight=1.0,
    params={
      "soft_limit": math.radians(45.0),
      "sigma": 0.35,
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )
  base_cfg.rewards["kick_ready"] = RewardTermCfg(
    func=kick_mdp.kick_ready,
    weight=4.0,
    params={
      "target_distance": 0.35,
      "waypoint_std": 0.20,
      "distance_std": 0.08,
      "lateral_half_width": 0.12,
      "bearing_std": 0.35,
      "target_alignment_std": 0.20,
      "camera_soft_limit": math.radians(45.0),
      "camera_sigma": 0.35,
      "command_name": "goal",
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )

  # Low weight until the kick stage; approach geometry dominates for now.
  base_cfg.rewards["kick_zone"] = RewardTermCfg(
    func=kick_mdp.ball_in_kick_zone,
    weight=0.25,
    params={
      "kick_distance": 0.35,
      "lateral_half_width": 0.12,
      "distance_std": 0.08,
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )

  base_cfg.episode_length_s = 45.0

  base_cfg.curriculum["spawn_radius"] = CurriculumTermCfg(
    func=kick_mdp.approach_spawn_radius_curriculum,
    params={
      "event_name": "reset_base",
      "start_radius": (0.5, 1.0),
      "end_radius": (4.0, 4.0),
      "start_step": 0,
      "end_step": 400_000,
    },
  )

  # nconmax must account for ball contacts.
  if base_cfg.sim.nconmax is not None:
    base_cfg.sim.nconmax = max(base_cfg.sim.nconmax, base_cfg.sim.nconmax + 20)

  return base_cfg

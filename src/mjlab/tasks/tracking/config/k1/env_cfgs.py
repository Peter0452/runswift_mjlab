"""Booster K1 flat kick-tracking configuration.

Same prior as the G1 tracker: one reference clock, failure-biased
reference-state initialization, trunk-relative body rewards, and no ball
reward. The actor is body-frame and does not see base linear velocity.
Ball and target positions are in the observation so a later shooting stage
can resume the same input.
"""

from dataclasses import replace

from mjlab.asset_zoo.props.ball import get_ball_radius, get_ball_spec
from mjlab.asset_zoo.props.goal import get_goal_spec
from mjlab.asset_zoo.robots.booster_k1.k1_constants import (
  K1_ACTION_SCALE,
  get_k1_robot_cfg,
)
from mjlab.asset_zoo.robots.booster_k1.k1_whirlwind_constants import (
  ACTUATOR_E4310,
  ACTUATOR_E4315,
  ACTUATOR_E6408,
  ACTUATOR_E6416,
  ACTUATOR_HT4438,
  ACTUATOR_K1_ANKLE,
  ACTUATOR_R14,
)
from mjlab.entity import EntityArticulationInfoCfg, EntityCfg
from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.envs.mdp import dr
from mjlab.envs.mdp.actions import JointPositionActionCfg
from mjlab.envs.mdp.events import reset_root_state_uniform
from mjlab.managers.event_manager import EventTermCfg
from mjlab.managers.observation_manager import ObservationGroupCfg, ObservationTermCfg
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.sensor import ContactMatch, ContactSensorCfg
from mjlab.tasks.kick.mdp.commands import UniformGoalPositionCommandCfg
from mjlab.tasks.tracking.config.k1.kick_motion import KICK_TRACKING_NPZ
from mjlab.tasks.tracking.mdp import MotionCommandCfg
from mjlab.tasks.tracking.mdp.events import place_goal_at_command
from mjlab.tasks.tracking.mdp.observations import (
  ball_pos_b,
  motion_style_z,
  target_pos_b,
)
from mjlab.tasks.tracking.mdp.rewards import (
  action_smoothness,
  base_height_too_low,
  ee_body_pos_fall_penalty,
  feet_slip,
  no_fly,
  stand_joint_pose,
)
from mjlab.tasks.tracking.mdp.shot_rewards import (
  ball_contact_orientation,
  ball_over_line,
  ball_velocity,
  error_ball_to_target,
  penalize_self_contact_feet,
  penalize_weak_foot_contact,
  robot_ball_contact,
  robot_ball_contact_count,
  robot_com_ball_distance,
  robot_feet_ball_distance,
  robot_torso_ball_distance,
)
from mjlab.tasks.tracking.tracking_env_cfg import make_tracking_env_cfg
from mjlab.tasks.velocity.mdp.amp_terrain_dr import randomize_terrain_contact
from mjlab.utils.noise import UniformNoiseCfg as Unoise

K1_TRACKED_BODY_NAMES = (
  "Trunk",
  "Head_2",
  "Left_Hip_Roll",
  "Left_Shank",
  "left_foot_link",
  "Right_Hip_Roll",
  "Right_Shank",
  "right_foot_link",
  "Left_Arm_2",
  "left_hand_link",
  "Right_Arm_2",
  "right_hand_link",
)

_PROPRIO_HISTORY = 5
_EE_BODIES = (
  "left_foot_link",
  "right_foot_link",
  "left_hand_link",
  "right_hand_link",
)
_FEET = ("left_foot_link", "right_foot_link")
_BALL_POS_HISTORY = 5
# Static tracking-stage ball, in front of the env origin. Reward stays motion-only.
_BALL_POS = (0.35, -0.15, get_ball_radius())
# Target point is straight ahead. Stage 2 scores the ball with a Gaussian of this width.
_GOAL_DISTANCE = (4.0, 8.0)
_GOAL_REWARD_STD = 1.0


def _ball_foot_sensor(name: str, foot: str) -> ContactSensorCfg:
  return ContactSensorCfg(
    name=name,
    primary=ContactMatch(mode="subtree", pattern=foot, entity="robot"),
    secondary=ContactMatch(mode="body", pattern="ball", entity="ball"),
    fields=("found", "force"),
    reduce="netforce",
    num_slots=1,
  )


def _with_history(terms: dict[str, ObservationTermCfg], names: tuple[str, ...]) -> None:
  for name in names:
    terms[name].history_length = _PROPRIO_HISTORY


# AMP walk startup and push ranges. The kick keeps its clip-aligned spawn pose.
_AMP_PUSH_RANGE = {
  "x": (-0.28, 0.28),
  "y": (-0.28, 0.28),
  "z": (-0.2, 0.2),
  "roll": (-0.52, 0.52),
  "pitch": (-0.52, 0.52),
  "yaw": (-0.78, 0.78),
}
# Peak torque from the AMP walk motors. The kick clip stays flat at that peak.
_AMP_EFFORT_BY_EXPR = {
  ".*_Hip_Pitch": ACTUATOR_E6408.effort_limit,
  ".*_Hip_Roll": ACTUATOR_E4315.effort_limit,
  ".*_Hip_Yaw": ACTUATOR_E4310.effort_limit,
  ".*_Knee_Pitch": ACTUATOR_E6416.effort_limit,
  ".*_Ankle_Pitch": ACTUATOR_K1_ANKLE.effort_limit,
  ".*_Ankle_Roll": ACTUATOR_K1_ANKLE.effort_limit,
  ".*_Shoulder_Pitch": ACTUATOR_R14.effort_limit,
  "Head_Yaw": ACTUATOR_HT4438.effort_limit,
}


_AMP_RESET_VELOCITY = {
  "x": (-1.0, 1.0),
  "y": (-1.0, 1.0),
  "z": (0.01, 0.3),
  "roll": (-0.1, 0.1),
  "pitch": (-0.1, 0.1),
  "yaw": (-0.5, 0.5),
}


def _match_amp_walk_dr(cfg: ManagerBasedRlEnvCfg) -> None:
  """Use the AMP walk's robot randomization on the kick tracker.

  Friction, encoder bias, PD gains, trunk and limb inertia, ground contact,
  command delay, push, reset velocity, joint-velocity reset, joint-velocity
  observation noise, and peak torque match the walk. The torque clip stays
  flat at that peak. The clip pose offset stays, and the ground stays a plane.
  """
  robot = cfg.scene.entities["robot"]
  articulation = robot.articulation
  assert articulation is not None
  robot.articulation = EntityArticulationInfoCfg(
    actuators=tuple(
      replace(
        actuator,
        delay_min_lag=2,
        delay_max_lag=8,
        delay_hold_prob=0.3,
        effort_limit=_AMP_EFFORT_BY_EXPR[actuator.target_names_expr[0]],
      )
      for actuator in articulation.actuators
    ),
    soft_joint_pos_limit_factor=articulation.soft_joint_pos_limit_factor,
  )

  cfg.events.pop("base_com", None)
  cfg.events["push_robot"].interval_range_s = (1.5, 4.0)
  cfg.events["push_robot"].params["velocity_range"] = _AMP_PUSH_RANGE
  cfg.events["encoder_bias"].params["bias_range"] = (-0.015, 0.015)
  cfg.events["foot_friction"].params["ranges"] = (0.75, 1.25)
  cfg.events["pd_gains"] = EventTermCfg(
    mode="startup",
    func=dr.pd_gains,
    params={
      "asset_cfg": SceneEntityCfg("robot", actuator_names=".*"),
      "operation": "scale",
      "kp_range": (0.8, 1.2),
      "kd_range": (0.8, 1.2),
    },
  )
  cfg.events["trunk_inertia"] = EventTermCfg(
    mode="startup",
    func=dr.pseudo_inertia,
    params={
      "asset_cfg": SceneEntityCfg("robot", body_names=("Trunk",)),
      "alpha_range": (-0.05, 0.05),
      "t_range": (-0.05, 0.05),
    },
  )
  cfg.events["limb_inertia"] = EventTermCfg(
    mode="startup",
    func=dr.pseudo_inertia,
    params={
      "asset_cfg": SceneEntityCfg("robot", body_names=(r"(?!Trunk$).*",)),
      "alpha_range": (-0.05, 0.05),
      "t_range": (-0.025, 0.025),
    },
  )
  cfg.events["terrain_contact"] = EventTermCfg(
    func=randomize_terrain_contact,
    mode="startup",
    params={
      "asset_cfg": SceneEntityCfg("terrain"),
      "solref_ranges": {0: (0.006, 0.03), 1: (0.95, 1.05)},
      "solimp_ranges": {0: (0.88, 0.92), 1: (0.94, 0.99), 2: (0.003, 0.01)},
      "shared_random": True,
    },
  )

  motion_cmd = cfg.commands["motion"]
  assert isinstance(motion_cmd, MotionCommandCfg)
  motion_cmd.velocity_range = _AMP_RESET_VELOCITY
  motion_cmd.joint_velocity_range = (-0.1, 0.1)
  cfg.observations["actor"].terms["joint_vel"].noise = Unoise(n_min=-1.5, n_max=1.5)


def booster_k1_kick_tracking_env_cfg(
  play: bool = False, stage: int = 1
) -> ManagerBasedRlEnvCfg:
  """Create the flat-plane K1 kick tracking configuration."""
  cfg = make_tracking_env_cfg()
  cfg.scene.entities = {
    "robot": get_k1_robot_cfg(),
    "ball": EntityCfg(
      spec_fn=get_ball_spec,
      init_state=EntityCfg.InitialStateCfg(pos=_BALL_POS),
    ),
    # Mid frame, 2.40 m × 1.60 m. The mouth is moved onto the goal command
    # after each reset; this pose is only the pre-reset default.
    "goal": EntityCfg(
      spec_fn=get_goal_spec,
      init_state=EntityCfg.InitialStateCfg(
        pos=(5.5, 0.0, 0.0),
        rot=(0.70710678118, 0.0, 0.0, 0.70710678118),
      ),
    ),
  }
  cfg.scene.num_envs = 4096
  # Farther than the 8 m goal so one env's frame does not reach the next.
  cfg.scene.env_spacing = 20.0
  cfg.sim.nconmax = 128
  cfg.sim.njmax = 300

  cfg.scene.sensors = (
    ContactSensorCfg(
      name="self_collision",
      primary=ContactMatch(mode="subtree", pattern="Trunk", entity="robot"),
      secondary=ContactMatch(mode="subtree", pattern="Trunk", entity="robot"),
      fields=("found", "force"),
      reduce="none",
      num_slots=1,
      history_length=4,
    ),
    ContactSensorCfg(
      name="feet_ground_contact",
      primary=ContactMatch(
        mode="subtree",
        pattern=r"^(left_foot_link|right_foot_link)$",
        entity="robot",
      ),
      secondary=ContactMatch(mode="body", pattern="terrain"),
      fields=("found", "force"),
      reduce="netforce",
      num_slots=1,
    ),
  )

  joint_pos_action = cfg.actions["joint_pos"]
  assert isinstance(joint_pos_action, JointPositionActionCfg)
  joint_pos_action.scale = K1_ACTION_SCALE

  motion_cmd = cfg.commands["motion"]
  assert isinstance(motion_cmd, MotionCommandCfg)
  motion_cmd.motion_file = str(KICK_TRACKING_NPZ)
  motion_cmd.anchor_body_name = "Trunk"
  motion_cmd.body_names = K1_TRACKED_BODY_NAMES
  motion_cmd.adaptive_kernel_size = 3
  cfg.commands["goal"] = UniformGoalPositionCommandCfg(
    distance_range=_GOAL_DISTANCE,
    angle_range=(0.0, 0.0),
    resampling_time_range=(1.0e9, 1.0e9),
    debug_vis=False,
  )
  cfg.events["place_goal"] = EventTermCfg(
    func=place_goal_at_command,
    mode="post_reset",
    params={"command_name": "goal", "asset_cfg": SceneEntityCfg("goal")},
  )
  cfg.events["reset_ball"] = EventTermCfg(
    func=reset_root_state_uniform,
    mode="reset",
    params={
      "asset_cfg": SceneEntityCfg("ball"),
      "pose_range": {"x": (-0.05, 0.05), "y": (-0.05, 0.05)},
      "velocity_range": {},
    },
  )

  actor_terms = cfg.observations["actor"].terms
  actor_terms.pop("base_lin_vel", None)
  _with_history(actor_terms, ("base_ang_vel", "joint_pos", "joint_vel", "actions"))
  style_term = ObservationTermCfg(
    func=motion_style_z, params={"command_name": "motion"}
  )
  actor_terms["motion_style_z"] = style_term
  actor_terms["ball_pos_b"] = ObservationTermCfg(
    func=ball_pos_b,
    params={"command_name": "motion"},
    noise=Unoise(n_min=-0.05, n_max=0.05),
    history_length=_BALL_POS_HISTORY,
  )
  actor_terms["target_pos_b"] = ObservationTermCfg(
    func=target_pos_b,
    params={"command_name": "goal"},
    noise=Unoise(n_min=-0.1, n_max=0.1),
    history_length=_BALL_POS_HISTORY,
  )
  cfg.observations["actor"] = ObservationGroupCfg(
    terms=actor_terms,
    concatenate_terms=True,
    enable_corruption=True,
  )
  critic_terms = cfg.observations["critic"].terms
  _with_history(
    critic_terms,
    ("base_lin_vel", "base_ang_vel", "joint_pos", "joint_vel", "actions"),
  )
  critic_terms["motion_style_z"] = ObservationTermCfg(
    func=motion_style_z, params={"command_name": "motion"}
  )
  critic_terms["ball_pos_b"] = ObservationTermCfg(
    func=ball_pos_b,
    params={"command_name": "motion"},
    history_length=_BALL_POS_HISTORY,
  )
  critic_terms["target_pos_b"] = ObservationTermCfg(
    func=target_pos_b,
    params={"command_name": "goal"},
    history_length=_BALL_POS_HISTORY,
  )

  cfg.events["foot_friction"].params[
    "asset_cfg"
  ].geom_names = r"^(left|right)_foot[0-5]_collision$"
  _match_amp_walk_dr(cfg)
  cfg.terminations["ee_body_pos"].params["body_names"] = _EE_BODIES
  cfg.rewards["feet_slip"] = RewardTermCfg(
    func=feet_slip,
    weight=-0.025,
    params={
      "command_name": "motion",
      "sensor_name": "feet_ground_contact",
      "body_names": _FEET,
      "threshold": 1.0,
    },
  )
  cfg.rewards["no_fly"] = RewardTermCfg(
    func=no_fly,
    weight=-0.05,
    params={"command_name": "motion", "body_names": _FEET, "height": 0.05},
  )
  cfg.rewards["base_height"] = RewardTermCfg(
    func=base_height_too_low,
    weight=-20.0,
    params={"command_name": "motion", "threshold": 0.48},
  )
  cfg.rewards["action_smoothness"] = RewardTermCfg(
    func=action_smoothness, weight=-0.0015
  )
  cfg.rewards["ee_body_pos_fall"] = RewardTermCfg(
    func=ee_body_pos_fall_penalty,
    weight=-100.0,
    params={
      "command_name": "motion",
      "threshold": 0.25,
      "body_names": _EE_BODIES,
    },
  )
  cfg.viewer.body_name = "Trunk"

  if stage == 2:
    _apply_kick_stage2(cfg, motion_cmd)
  elif stage != 1:
    raise ValueError(f"K1 kick stage must be 1 or 2, got {stage}")

  if play:
    cfg.episode_length_s = int(1e9)
    cfg.observations["actor"].enable_corruption = False
    cfg.events.pop("push_robot", None)
    motion_cmd.pose_range = {}
    motion_cmd.velocity_range = {}
    motion_cmd.joint_velocity_range = (0.0, 0.0)
    motion_cmd.sampling_mode = "start"
    motion_cmd.place_ball_at_strike = True
    motion_cmd.strike_body_name = "right_foot_link"
    motion_cmd.strike_height = get_ball_radius()
    motion_cmd.strike_pos_noise = (0.0, 0.0)
    motion_cmd.strike_vel_noise = (0.0, 0.0)
    cfg.events["reset_ball"].params["pose_range"] = {}

  return cfg


def _apply_kick_stage2(cfg: ManagerBasedRlEnvCfg, motion_cmd: MotionCommandCfg) -> None:
  """Static ball on the clip strike, kick rewards, looser failure limits."""
  motion_cmd.sampling_mode = "prefix"
  motion_cmd.start_fraction = 0.05
  motion_cmd.left_clip_prob = 0.6
  motion_cmd.place_ball_at_strike = True
  motion_cmd.strike_body_name = "right_foot_link"
  motion_cmd.strike_height = get_ball_radius()
  motion_cmd.strike_pos_noise = (0.1, 0.1)
  motion_cmd.strike_vel_noise = (0.05, 0.05)
  cfg.events["reset_ball"].params["pose_range"] = {}
  cfg.rewards["motion_global_root_pos"].weight = 1.0
  cfg.terminations["anchor_pos"].params["threshold"] = 0.5
  cfg.terminations["ee_body_pos"].params["threshold"] = 0.35
  cfg.scene.sensors = (
    *cfg.scene.sensors,
    _ball_foot_sensor("ball_foot_contact", "right_foot_link"),
    _ball_foot_sensor("ball_left_foot_contact", "left_foot_link"),
  )
  cfg.rewards["error_ball_to_target"] = RewardTermCfg(
    func=error_ball_to_target, weight=8.0, params={"std": _GOAL_REWARD_STD}
  )
  cfg.rewards["ball_contact_orientation"] = RewardTermCfg(
    func=ball_contact_orientation, weight=1.7
  )
  cfg.rewards["robot_feet_ball_distance"] = RewardTermCfg(
    func=robot_feet_ball_distance, weight=0.8, params={"std": 0.5}
  )
  cfg.rewards["robot_com_ball_distance"] = RewardTermCfg(
    func=robot_com_ball_distance, weight=0.8, params={"std": 0.5}
  )
  cfg.rewards["robot_torso_ball_distance"] = RewardTermCfg(
    func=robot_torso_ball_distance, weight=0.8, params={"std": 0.5}
  )
  cfg.rewards["robot_ball_contact"] = RewardTermCfg(
    func=robot_ball_contact, weight=0.8
  )
  cfg.rewards["robot_ball_contact_count"] = RewardTermCfg(
    func=robot_ball_contact_count, weight=0.8
  )
  cfg.rewards["ball_velocity"] = RewardTermCfg(
    func=ball_velocity, weight=0.45, params={"std": 1.0}
  )
  cfg.rewards["ball_over_line"] = RewardTermCfg(func=ball_over_line, weight=0.4)
  cfg.rewards["penalize_weak_foot_contact"] = RewardTermCfg(
    func=penalize_weak_foot_contact, weight=-0.4
  )
  cfg.rewards["penalize_self_contact_feet"] = RewardTermCfg(
    func=penalize_self_contact_feet, weight=-0.16
  )


def booster_k1_kick_box_env_cfg(*, play: bool = False) -> ManagerBasedRlEnvCfg:
  """Stage 2 kick, with the ball within 0.5 m of that clip's strike.

  The clip is chosen first. Its estimated strike is the ball center, and x
  and y are then uniform in ±0.5 m. Rewards match stage 2, plus the stand
  pose after the ball has gone. Observation size matches stage 2, so a
  stage-2 checkpoint still loads.
  """
  cfg = booster_k1_kick_tracking_env_cfg(play=play, stage=2)
  motion_cmd = cfg.commands["motion"]
  assert isinstance(motion_cmd, MotionCommandCfg)
  motion_cmd.ball_spawn_regions = None
  motion_cmd.ball_spawn_range = None
  motion_cmd.strike_pos_noise = (0.5, 0.5)
  motion_cmd.strike_vel_noise = (0.0, 0.0)
  motion_cmd.stand_after_kick = True
  motion_cmd.ball_gone_distance = 1.0
  motion_cmd.stand_height = 0.5125
  cfg.rewards["stand_joint_pose"] = RewardTermCfg(
    func=stand_joint_pose,
    weight=1.0,
    params={"command_name": "motion", "std": 0.5},
  )
  return cfg

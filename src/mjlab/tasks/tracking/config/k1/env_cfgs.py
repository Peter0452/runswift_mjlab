"""Booster K1 flat kick-tracking configuration.

Same prior as the G1 tracker: one reference clock, failure-biased
reference-state initialization, trunk-relative body rewards, and no ball
reward. The actor is body-frame and does not see base linear velocity.
Ball and target positions are in the observation so a later shooting stage
can resume the same input.
"""

from mjlab.asset_zoo.props.ball import get_ball_radius, get_ball_spec
from mjlab.asset_zoo.robots.booster_k1.k1_constants import (
  K1_ACTION_SCALE,
  get_k1_robot_cfg,
)
from mjlab.entity import EntityCfg
from mjlab.envs import ManagerBasedRlEnvCfg
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
from mjlab.tasks.tracking.mdp.observations import (
  ball_pos_b,
  motion_style_z,
  target_pos_b,
)
from mjlab.tasks.tracking.mdp.rewards import (
  action_smoothness,
  ee_body_pos_fall_penalty,
  feet_slip,
  no_fly,
)
from mjlab.tasks.tracking.tracking_env_cfg import make_tracking_env_cfg
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


def _with_history(terms: dict[str, ObservationTermCfg], names: tuple[str, ...]) -> None:
  for name in names:
    terms[name].history_length = _PROPRIO_HISTORY


def booster_k1_kick_tracking_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Create the flat-plane K1 kick tracking configuration."""
  cfg = make_tracking_env_cfg()
  cfg.scene.entities = {
    "robot": get_k1_robot_cfg(),
    "ball": EntityCfg(
      spec_fn=get_ball_spec,
      init_state=EntityCfg.InitialStateCfg(pos=_BALL_POS),
    ),
  }
  cfg.scene.num_envs = 4096
  cfg.scene.env_spacing = 8.0
  cfg.sim.nconmax = 64
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
    distance_range=(2.5, 8.5),
    angle_range=(-1.5708, 1.5708),
    resampling_time_range=(1.0e9, 1.0e9),
    debug_vis=False,
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
  cfg.events["base_com"].params["asset_cfg"].body_names = ("Trunk",)
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

  if play:
    cfg.episode_length_s = int(1e9)
    cfg.observations["actor"].enable_corruption = False
    cfg.events.pop("push_robot", None)
    motion_cmd.pose_range = {}
    motion_cmd.velocity_range = {}
    motion_cmd.sampling_mode = "start"

  return cfg

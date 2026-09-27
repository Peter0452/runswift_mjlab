"""Booster K1 flat kick-tracking configuration.

Same prior as the G1 tracker: one reference clock, failure-biased
reference-state initialization, trunk-relative body rewards, and no ball
reward. The actor is body-frame and does not see base linear velocity.
"""

from mjlab.asset_zoo.robots.booster_k1.k1_constants import (
  K1_ACTION_SCALE,
  get_k1_robot_cfg,
)
from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.envs.mdp.actions import JointPositionActionCfg
from mjlab.managers.observation_manager import ObservationGroupCfg, ObservationTermCfg
from mjlab.sensor import ContactMatch, ContactSensorCfg
from mjlab.tasks.tracking.config.k1.kick_motion import KICK_TRACKING_NPZ
from mjlab.tasks.tracking.mdp import MotionCommandCfg
from mjlab.tasks.tracking.mdp.observations import motion_style_z
from mjlab.tasks.tracking.tracking_env_cfg import make_tracking_env_cfg

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


def _with_history(terms: dict[str, ObservationTermCfg], names: tuple[str, ...]) -> None:
  for name in names:
    terms[name].history_length = _PROPRIO_HISTORY


def booster_k1_kick_tracking_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Create the flat-plane K1 kick tracking configuration."""
  cfg = make_tracking_env_cfg()
  cfg.scene.entities = {"robot": get_k1_robot_cfg()}
  cfg.scene.num_envs = 4096
  cfg.scene.env_spacing = 8.0

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

  actor_terms = cfg.observations["actor"].terms
  actor_terms.pop("base_lin_vel", None)
  _with_history(actor_terms, ("base_ang_vel", "joint_pos", "joint_vel", "actions"))
  style_term = ObservationTermCfg(
    func=motion_style_z, params={"command_name": "motion"}
  )
  actor_terms["motion_style_z"] = style_term
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

  cfg.events["foot_friction"].params[
    "asset_cfg"
  ].geom_names = r"^(left|right)_foot[0-5]_collision$"
  cfg.events["base_com"].params["asset_cfg"].body_names = ("Trunk",)
  cfg.terminations["ee_body_pos"].params["body_names"] = (
    "left_foot_link",
    "right_foot_link",
    "left_hand_link",
    "right_hand_link",
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

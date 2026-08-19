"""Booster K1 velocity environment configurations."""

import math

from mjlab.asset_zoo.robots import (
  K1_ACTION_SCALE,
  get_k1_robot_cfg,
)
from mjlab.asset_zoo.robots.booster_k1.k1_constants import (
  HOME_KEYFRAME,
  KNEES_BENT_KEYFRAME,
)
from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.envs import mdp as envs_mdp
from mjlab.envs.mdp import dr
from mjlab.envs.mdp.actions import JointPositionActionCfg
from mjlab.managers.curriculum_manager import CurriculumTermCfg
from mjlab.managers.event_manager import EventTermCfg
from mjlab.managers.observation_manager import ObservationTermCfg
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.managers.termination_manager import TerminationTermCfg
from mjlab.sensor import (
  ContactMatch,
  ContactSensorCfg,
  ObjRef,
  RayCastSensorCfg,
  RingPatternCfg,
  TerrainHeightSensorCfg,
)
from mjlab.tasks.velocity import mdp
from mjlab.tasks.velocity.mdp import UniformVelocityCommandCfg, walk_params
from mjlab.tasks.velocity.velocity_env_cfg import make_velocity_env_cfg
from mjlab.terrains.config import flat, random_rough, wave_terrain

# Legs + arms: head stays at default via PD. Arms get a small action scale
# (±0.15 rad) so the policy can balance with them without swinging into
# obstacles.
_K1_POLICY_ACTUATORS = (
  ".*_Hip_Pitch",
  ".*_Hip_Roll",
  ".*_Hip_Yaw",
  ".*_Knee_Pitch",
  ".*_Ankle_Pitch",
  ".*_Ankle_Roll",
  ".*_Shoulder_Pitch",
  ".*_Shoulder_Roll",
  ".*_Elbow_Pitch",
  ".*_Elbow_Yaw",
)

# Head only: not policy-controlled; held at default keyframe.
_K1_PASSIVE_JOINTS = ("Head_.*",)

# Leg-only patterns (rewards that should ignore arms).
_K1_LEG_ACTUATORS = (
  ".*_Hip_Pitch",
  ".*_Hip_Roll",
  ".*_Hip_Yaw",
  ".*_Knee_Pitch",
  ".*_Ankle_Pitch",
  ".*_Ankle_Roll",
)

# Absolute q_target clip on processed actions (after scale + default offset).
# Parity with k1_policy_runner walk_policy_v4 deploy limits.
_K1_ARM_BAND = math.radians(15.0)
_K1_ARM_CLIP: dict[str, tuple[float, float]] = {
  "Left_Shoulder_Pitch": (0.0 - _K1_ARM_BAND, 0.0 + _K1_ARM_BAND),
  "Right_Shoulder_Pitch": (0.0 - _K1_ARM_BAND, 0.0 + _K1_ARM_BAND),
  "Left_Shoulder_Roll": (-1.45 - _K1_ARM_BAND, -1.45 + _K1_ARM_BAND),
  "Right_Shoulder_Roll": (1.45 - _K1_ARM_BAND, 1.45 + _K1_ARM_BAND),
  "Left_Elbow_Pitch": (0.0 - _K1_ARM_BAND, 0.0 + _K1_ARM_BAND),
  "Right_Elbow_Pitch": (0.0 - _K1_ARM_BAND, 0.0 + _K1_ARM_BAND),
  "Left_Elbow_Yaw": (0.0 - _K1_ARM_BAND, 0.0 + _K1_ARM_BAND),
  "Right_Elbow_Yaw": (0.0 - _K1_ARM_BAND, 0.0 + _K1_ARM_BAND),
}
_K1_LEG_CLIP: dict[str, tuple[float, float]] = {
  "Left_Hip_Pitch": (-2.740, 1.950),
  "Right_Hip_Pitch": (-2.740, 1.950),
  "Left_Hip_Roll": (-0.302, 1.472),
  "Right_Hip_Roll": (-1.472, 0.302),
  "Left_Hip_Yaw": (-0.900, 0.900),
  "Right_Hip_Yaw": (-0.900, 0.900),
  "Left_Knee_Pitch": (0.111, 2.119),
  "Right_Knee_Pitch": (0.111, 2.119),
  "Left_Ankle_Pitch": (-0.809, 0.284),
  "Right_Ankle_Pitch": (-0.809, 0.284),
  "Left_Ankle_Roll": (-0.310, 0.310),
  "Right_Ankle_Roll": (-0.310, 0.310),
}
_K1_JOINT_POS_CLIP = {**_K1_ARM_CLIP, **_K1_LEG_CLIP}

# Actor sensor terms to delay (not command / last_action).
_K1_SENSOR_OBS = (
  "base_ang_vel",
  "projected_gravity",
  "joint_pos",
  "joint_vel",
)


def booster_k1_rough_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Create Booster K1 rough terrain velocity configuration."""
  cfg = make_velocity_env_cfg()

  cfg.sim.mujoco.ccd_iterations = 500
  cfg.sim.contact_sensor_maxmatch = 500
  cfg.sim.nconmax = 70

  cfg.scene.entities = {"robot": get_k1_robot_cfg()}

  # Set raycast sensor frame to K1 trunk.
  for sensor in cfg.scene.sensors or ():
    if sensor.name == "terrain_scan":
      assert isinstance(sensor, RayCastSensorCfg)
      assert isinstance(sensor.frame, ObjRef)
      sensor.frame.name = "Trunk"

  site_names = ("left_foot", "right_foot")
  geom_names = tuple(
    f"{side}_foot{i}_collision" for side in ("left", "right") for i in range(1, 6)
  )

  # Wire foot height scan to per-foot sites.
  for sensor in cfg.scene.sensors or ():
    if sensor.name == "foot_height_scan":
      assert isinstance(sensor, TerrainHeightSensorCfg)
      sensor.frame = tuple(
        ObjRef(type="site", name=s, entity="robot") for s in site_names
      )
      sensor.pattern = RingPatternCfg.single_ring(radius=0.03, num_samples=6)

  feet_ground_cfg = ContactSensorCfg(
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
    track_air_time=True,
  )
  self_collision_cfg = ContactSensorCfg(
    name="self_collision",
    primary=ContactMatch(mode="subtree", pattern="Trunk", entity="robot"),
    secondary=ContactMatch(mode="subtree", pattern="Trunk", entity="robot"),
    fields=("found", "force"),
    reduce="none",
    num_slots=1,
    history_length=4,
  )
  cfg.scene.sensors = (cfg.scene.sensors or ()) + (
    feet_ground_cfg,
    self_collision_cfg,
  )

  if cfg.scene.terrain is not None and cfg.scene.terrain.terrain_generator is not None:
    # Mixed terrains, no level curriculum (fixed proportions each reset).
    cfg.scene.terrain.terrain_generator.curriculum = False
    cfg.scene.terrain.terrain_generator.sub_terrains = {
      "flat": flat(proportion=0.6),
      "wave_terrain": wave_terrain(proportion=0.2),
      "random_rough": random_rough(proportion=0.2),
    }
  cfg.curriculum.pop("terrain_levels", None)

  joint_pos_action = cfg.actions["joint_pos"]
  assert isinstance(joint_pos_action, JointPositionActionCfg)
  joint_pos_action.actuator_names = _K1_POLICY_ACTUATORS
  # Legs: ±1.0 rad; arms: ±0.15 rad (see K1_ACTION_SCALE).
  joint_pos_action.scale = {
    name: K1_ACTION_SCALE[name] for name in _K1_POLICY_ACTUATORS
  }
  # Absolute target clip (post scale+offset); deploy parity with walk_policy_v4.
  joint_pos_action.clip = _K1_JOINT_POS_CLIP

  cfg.viewer.body_name = "Trunk"

  twist_cmd = cfg.commands["twist"]
  assert isinstance(twist_cmd, UniformVelocityCommandCfg)
  twist_cmd.viz.z_offset = 0.7
  twist_cmd.ranges.lin_vel_x = (-1.5, 2.0)
  twist_cmd.ranges.lin_vel_y = (-1.5, 2.0)
  twist_cmd.ranges.ang_vel_z = (-0.5, 0.5)
  # ParameterWalk gait frequency command → 4-D twist [vx, vy, wz, freq].
  twist_cmd.ranges.gait_frequency = walk_params.GAIT_FREQUENCY_RANGE
  # More standing (T1-like) so the policy learns to hold still as well as walk.
  twist_cmd.rel_standing_envs = 0.25
  twist_cmd.rel_forward_envs = 0.4
  twist_cmd.rel_heading_envs = 0.2

  # Keep curriculum stage 0 in sync with the wider base ranges.
  cfg.curriculum["command_vel"].params["velocity_stages"][0] = {
    "step": 0,
    "lin_vel_x": (-1.5, 2.0),
    "lin_vel_y": (-1.5, 2.0),
    "ang_vel_z": (-0.5, 0.5),
  }

  cfg.events["foot_friction"].params["asset_cfg"].geom_names = geom_names
  cfg.events["base_com"].params["asset_cfg"].body_names = ("Trunk",)

  # Always reset to knees-bent crouch (robot default / ParameterWalk-like squat).
  cfg.events["reset_robot_joints"] = EventTermCfg(
    func=mdp.reset_joints_from_pose_catalog,
    mode="reset",
    params={
      "poses": [KNEES_BENT_KEYFRAME.joint_pos],
      "base_heights": [KNEES_BENT_KEYFRAME.pos[2]],
      "position_range": (-0.1, 0.1),
      "velocity_range": (0.0, 0.0),
      "asset_cfg": SceneEntityCfg("robot", joint_names=(".*",)),
    },
  )

  # clear_state zeros all PD targets; keep head at default keyframe.
  cfg.events["hold_head"] = EventTermCfg(
    func=mdp.set_joint_position_targets_to_default,
    mode="reset",
    params={
      "asset_cfg": SceneEntityCfg("robot", joint_names=_K1_PASSIVE_JOINTS),
    },
  )

  # Mass/inertia (±~20% via alpha), PD gains, and armature for sim-to-real.
  cfg.events["robot_inertia"] = EventTermCfg(
    mode="startup",
    func=dr.pseudo_inertia,
    params={
      "asset_cfg": SceneEntityCfg("robot", body_names=(".*",)),
      "alpha_range": (-0.1, 0.1),
    },
  )
  cfg.events["pd_gains"] = EventTermCfg(
    mode="startup",
    func=dr.pd_gains,
    params={
      # Do not pass actuator_names: SceneEntityCfg resolves those to MuJoCo
      # ctrl indices, but dr.pd_gains indexes entity actuator groups.
      "asset_cfg": SceneEntityCfg("robot"),
      "kp_range": (0.8, 1.2),
      "kd_range": (0.8, 1.2),
      "operation": "scale",
    },
  )
  cfg.events["joint_armature"] = EventTermCfg(
    mode="startup",
    func=dr.joint_armature,
    params={
      "asset_cfg": SceneEntityCfg("robot", joint_names=_K1_LEG_ACTUATORS),
      "operation": "scale",
      "ranges": (0.5, 1.5),
    },
  )

  # Sensor pipeline latency: 0-2 control steps (0-40 ms at 50 Hz).
  for obs_name in _K1_SENSOR_OBS:
    term = cfg.observations["actor"].terms[obs_name]
    term.delay_min_lag = 0
    term.delay_max_lag = 2
    term.delay_hold_prob = 0.9

  # Open-loop gait clock; cadence from commanded gait_frequency (walk_params).
  # Sin/cos fades after ~8k iters; frequency command stays in twist forever.
  gait_cycle_cfg = ObservationTermCfg(
    func=mdp.gait_cycle,
    params={
      # Fallback only if command lacks freq dim (K1 always has it).
      "period": 1.0 / walk_params.GAIT_FREQUENCY_DEFAULT,
      "command_name": "twist",
      "command_threshold": 0.05,
      "drop_step": 8_000 * 24,
      "fade_steps": 2_000 * 24,
    },
  )
  cfg.observations["actor"].terms["gait_cycle"] = gait_cycle_cfg
  cfg.observations["critic"].terms["gait_cycle"] = gait_cycle_cfg

  # Pose reward: use running tolerances at all speeds (allow large leg motion).
  # Default pose reference is knees-bent (robot init_state / action offset).
  _POSE_STD_RUNNING = {
    r".*_Hip_Pitch": 0.5,
    r".*_Hip_Roll": 0.15,
    r".*_Hip_Yaw": 0.15,
    r".*_Knee_Pitch": 0.6,
    r".*_Ankle_Pitch": 0.35,
    r".*_Ankle_Roll": 0.15,
    r".*_Shoulder_Pitch": 0.05,
    r".*_Shoulder_Roll": 0.05,
    r".*_Elbow_Pitch": 0.05,
    r".*_Elbow_Yaw": 0.05,
    r"Head_.*": 0.05,
  }
  cfg.rewards["pose"].params["std_standing"] = _POSE_STD_RUNNING
  cfg.rewards["pose"].params["std_walking"] = _POSE_STD_RUNNING
  cfg.rewards["pose"].params["std_running"] = _POSE_STD_RUNNING

  cfg.rewards["upright"].params["asset_cfg"].body_names = ("Trunk",)
  cfg.rewards["body_ang_vel"].params["asset_cfg"].body_names = ("Trunk",)

  for reward_name in ["foot_clearance", "foot_slip"]:
    cfg.rewards[reward_name].params["asset_cfg"].site_names = site_names

  cfg.rewards["body_ang_vel"].weight = -0.05
  cfg.rewards["angular_momentum"].weight = -0.02
  # Tracking must dominate — prior runs farmed upright/gait without moving.
  cfg.rewards["track_linear_velocity"].weight = 5.0
  cfg.rewards["track_angular_velocity"].weight = 4.0
  cfg.rewards["track_linear_velocity"].params["std"] = math.sqrt(0.15)
  cfg.rewards["track_angular_velocity"].params["std"] = math.sqrt(0.3)
  cfg.rewards["upright"].weight = 0.5
  cfg.rewards["pose"].weight = 0.5
  cfg.rewards["air_time"].weight = 0.25
  cfg.rewards["foot_swing_height"].weight = -0.5

  # Phase-synced stepping vs the shared gait clock (fades with the obs).
  cfg.rewards["gait"] = RewardTermCfg(
    func=mdp.feet_gait,
    weight=0.25,
    params={
      "sensor_name": "feet_ground_contact",
      "period": 1.0 / walk_params.GAIT_FREQUENCY_DEFAULT,
      "command_name": "twist",
      "command_threshold": 0.05,
      "left_foot_name": "left_foot_link",
      "right_foot_name": "right_foot_link",
      "drop_step": 8_000 * 24,
      "fade_steps": 2_000 * 24,
    },
  )

  # ParameterWalk feet_swing: bonus for airborne foot in phase windows
  # around 0.25 (L) / 0.75 (R). Keep below track so it cannot replace walking.
  cfg.rewards["feet_swing"] = RewardTermCfg(
    func=mdp.feet_swing,
    weight=1.0,
    params={
      "sensor_name": "feet_ground_contact",
      "period": 1.0 / walk_params.GAIT_FREQUENCY_DEFAULT,
      "swing_period": walk_params.SWING_PERIOD,
      "command_name": "twist",
      "command_threshold": 0.05,
      "left_foot_name": "left_foot_link",
      "right_foot_name": "right_foot_link",
    },
  )

  # Non-saturating penalty on hip abduction/adduction (wide stance).
  cfg.rewards["hip_roll_l2"] = RewardTermCfg(
    func=mdp.joint_deviation_l2,
    weight=-1.0,
    params={
      "asset_cfg": SceneEntityCfg("robot", joint_names=(".*_Hip_Roll",)),
    },
  )

  # Keep ankles near default roll (avoids rolling onto edges).
  cfg.rewards["ankle_roll_l2"] = RewardTermCfg(
    func=mdp.joint_deviation_l2,
    weight=-1.0,
    params={
      "asset_cfg": SceneEntityCfg("robot", joint_names=(".*_Ankle_Roll",)),
    },
  )

  # Disabled: L2 on pitch joints fights stride while learning to walk.
  cfg.rewards["crouch_l2"] = RewardTermCfg(
    func=mdp.joint_deviation_l2,
    weight=0.0,
    params={
      "asset_cfg": SceneEntityCfg(
        "robot",
        joint_names=(".*_Hip_Pitch", ".*_Knee_Pitch", ".*_Ankle_Pitch"),
      ),
    },
  )

  cfg.rewards["self_collisions"] = RewardTermCfg(
    func=mdp.self_collision_cost,
    weight=-1.0,
    params={"sensor_name": self_collision_cfg.name, "force_threshold": 10.0},
  )

  # Kill splits postures that stay upright past fell_over.
  # Nominal foot spacing is ~0.19 m; 0.38 m is roughly 2x.
  cfg.terminations["feet_too_far"] = TerminationTermCfg(
    func=mdp.feet_too_far_apart,
    params={
      "max_separation": 0.38,
      "asset_cfg": SceneEntityCfg("robot", site_names=site_names),
    },
  )

  # Real K1 has no reliable base lin-vel or height scan; train the actor
  # without them. Critic keeps privileged copies where available.
  del cfg.observations["actor"].terms["base_lin_vel"]
  del cfg.observations["actor"].terms["height_scan"]

  # Apply play mode overrides.
  if play:
    # Effectively infinite episode length.
    cfg.episode_length_s = int(1e9)

    cfg.observations["actor"].enable_corruption = False
    # Keep open-loop gait clock fully on during play. Zeroing it (old
    # final-policy mode) breaks mid-train checkpoints that still rely on
    # sin/cos; play's step counter also resets, so training drop_step would
    # not match a late checkpoint's faded state either. Always-on clock is
    # correct for early/mid eval; late policies largely ignore these dims.
    for group in ("actor", "critic"):
      gait_term = cfg.observations[group].terms.get("gait_cycle")
      if gait_term is not None:
        gait_term.params["drop_step"] = 10**18
        gait_term.params["fade_steps"] = 0
    gait_reward = cfg.rewards.get("gait")
    if gait_reward is not None:
      gait_reward.params["drop_step"] = 10**18
      gait_reward.params["fade_steps"] = 0
    cfg.events.pop("push_robot", None)
    cfg.terminations.pop("out_of_terrain_bounds", None)
    cfg.curriculum = {}
    cfg.events["randomize_terrain"] = EventTermCfg(
      func=envs_mdp.randomize_terrain,
      mode="reset",
      params={},
    )

    if cfg.scene.terrain is not None:
      if cfg.scene.terrain.terrain_generator is not None:
        cfg.scene.terrain.terrain_generator.curriculum = False
        cfg.scene.terrain.terrain_generator.num_cols = 5
        cfg.scene.terrain.terrain_generator.num_rows = 5
        cfg.scene.terrain.terrain_generator.border_width = 10.0

  return cfg


def booster_k1_flat_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Create Booster K1 flat terrain velocity configuration."""
  cfg = booster_k1_rough_env_cfg(play=play)

  # Do not lower njmax: K1 uses full-body collision; a fallen robot can need
  # ~750 constraint rows (nefc overflow at njmax=300 → sim NaNs → policy NaNs).
  # Inherit njmax=1500 from make_velocity_env_cfg().
  cfg.sim.mujoco.ccd_iterations = 50
  cfg.sim.contact_sensor_maxmatch = 500
  cfg.sim.nconmax = None

  # Switch to flat terrain.
  assert cfg.scene.terrain is not None
  cfg.scene.terrain.terrain_type = "plane"
  cfg.scene.terrain.terrain_generator = None

  # Remove raycast sensor and critic height scan (no terrain to scan; actor
  # already drops height_scan above).
  cfg.scene.sensors = tuple(
    s for s in (cfg.scene.sensors or ()) if s.name != "terrain_scan"
  )
  del cfg.observations["critic"].terms["height_scan"]

  cfg.terminations.pop("out_of_terrain_bounds", None)

  # Disable terrain curriculum (not present in play mode since rough clears all).
  cfg.curriculum.pop("terrain_levels", None)

  if play:
    twist_cmd = cfg.commands["twist"]
    assert isinstance(twist_cmd, UniformVelocityCommandCfg)
    twist_cmd.ranges.lin_vel_x = (-1.5, 2.0)
    twist_cmd.ranges.ang_vel_z = (-0.7, 0.7)

  return cfg


# G1 pose std mapped onto K1 joint names. K1 has no waist/wrists; Head_* stays
# tight like G1 waist, Elbow_Yaw like G1 shoulder_yaw.
_K1_G1_POSE_STD_STANDING = {".*": 0.05}
_K1_G1_POSE_STD_WALKING = {
  r".*_Hip_Pitch": 0.3,
  r".*_Hip_Roll": 0.15,
  r".*_Hip_Yaw": 0.15,
  r".*_Knee_Pitch": 0.35,
  r".*_Ankle_Pitch": 0.25,
  r".*_Ankle_Roll": 0.1,
  r".*_Shoulder_Pitch": 0.15,
  r".*_Shoulder_Roll": 0.15,
  r".*_Elbow_Pitch": 0.15,
  r".*_Elbow_Yaw": 0.1,
  r"Head_.*": 0.05,
}
_K1_G1_POSE_STD_RUNNING = {
  r".*_Hip_Pitch": 0.5,
  r".*_Hip_Roll": 0.2,
  r".*_Hip_Yaw": 0.2,
  r".*_Knee_Pitch": 0.6,
  r".*_Ankle_Pitch": 0.35,
  r".*_Ankle_Roll": 0.15,
  r".*_Shoulder_Pitch": 0.5,
  r".*_Shoulder_Roll": 0.2,
  r".*_Elbow_Pitch": 0.35,
  r".*_Elbow_Yaw": 0.15,
  r"Head_.*": 0.08,
}
_K1_G1_EXTRA_REWARDS = (
  "gait",
  "feet_swing",
  "hip_roll_l2",
  "ankle_roll_l2",
  "crouch_l2",
)


def _apply_g1_style_rewards(cfg: ManagerBasedRlEnvCfg) -> ManagerBasedRlEnvCfg:
  """Replace ParameterWalk extras with G1-like mjlab velocity rewards.

  Restores default tracking / pose / air-time weights from ``make_velocity_env_cfg``
  plus G1's speed-dependent pose std and ``self_collisions``. Drops gait-clock
  rewards and the K1 hip/ankle L2 terms. Robot, sensors, and commands stay K1.

  Unlike G1, neither actor nor critic observes ``base_lin_vel`` — the real K1
  has no reliable base linear-velocity estimate.
  """
  cfg.rewards["track_linear_velocity"].weight = 2.0
  cfg.rewards["track_angular_velocity"].weight = 2.0
  cfg.rewards["track_linear_velocity"].params["std"] = math.sqrt(0.25)
  cfg.rewards["track_angular_velocity"].params["std"] = math.sqrt(0.5)
  cfg.rewards["upright"].weight = 1.0
  cfg.rewards["pose"].weight = 1.0
  cfg.rewards["pose"].params["std_standing"] = _K1_G1_POSE_STD_STANDING
  cfg.rewards["pose"].params["std_walking"] = _K1_G1_POSE_STD_WALKING
  cfg.rewards["pose"].params["std_running"] = _K1_G1_POSE_STD_RUNNING
  cfg.rewards["body_ang_vel"].weight = -0.05
  cfg.rewards["angular_momentum"].weight = -0.02
  cfg.rewards["air_time"].weight = 0.0
  cfg.rewards["foot_swing_height"].weight = -0.25

  for name in _K1_G1_EXTRA_REWARDS:
    cfg.rewards.pop(name, None)

  # Gait clock obs only exists to support the dropped gait / feet_swing terms.
  # Real K1 has no base lin-vel; drop it from critic too (actor already omits it).
  for group in ("actor", "critic"):
    cfg.observations[group].terms.pop("gait_cycle", None)
    cfg.observations[group].terms.pop("base_lin_vel", None)

  return cfg


def booster_k1_rough_g1_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Rough-terrain K1 velocity env with G1-like mjlab rewards."""
  return _apply_g1_style_rewards(booster_k1_rough_env_cfg(play=play))


def booster_k1_flat_g1_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Flat-terrain K1 velocity env with G1-like mjlab rewards."""
  return _apply_g1_style_rewards(booster_k1_flat_env_cfg(play=play))


# Non-trunk bodies for small COM jitter (T1 ``other_com``).
_K1_OTHER_COM_BODIES = (
  "Head_.*",
  ".*_Arm_.*",
  ".*_hand_link",
  ".*_Hip_.*",
  ".*_Shank",
  ".*_Ankle_.*",
  ".*_foot_link",
)

# K1 geometry (vs T1 booster_gym 0.68 / 0.45 / 0.20 / 0.72).
# Successful K1 rough FT (Aug 2026): knees-bent crouch, not ParameterWalk HOME.
# HOME (-0.2/0.4) needs ParameterWalk feet_offset (-12) to stop hip stretch-out.
_K1_FAST_SAC_SPAWN_HEIGHT = KNEES_BENT_KEYFRAME.pos[2]
_K1_FAST_SAC_HEIGHT_TARGET = 0.50
_K1_FAST_SAC_TERMINATE_HEIGHT = 0.35  # clearance curriculum target (max)
_K1_FAST_SAC_TERMINATE_INITIAL = 0.30  # soft-start kill height
_K1_FAST_SAC_TERMINATE_HEIGHT_SOFT = 0.30  # Soft-start while standing learns.
# Hip pitch frames at y=±0.096 in k1.xml → natural foot spacing ≈ 0.192 m
# (straight-leg sites); default crouch with ±0.04 hip roll ≈ 0.16 m.
_K1_FAST_SAC_FEET_DISTANCE_REF = 0.19
# Base wide band [0.19, 0.28]; |vy|>0.1 → margin×3 → [0.19, 0.46].
_K1_FAST_SAC_FEET_DISTANCE_WIDE_MARGIN = 0.09
# Booster T1 filter for EMA velocity tracking rewards.
_K1_FAST_SAC_TRACK_FILTER_WEIGHT = 0.1  # Booster normalization.filter_weight
# Still-only: curb V / stretch-out when standing; silent while walking.
_K1_FAST_SAC_STANDING_HIP_ROLL_WEIGHT = -1.0

# Aug 7 track_stance: penalty scale soft-start + clearance kill curriculum.
_FAST_SAC_PENALTY_REWARD_NAMES = (
  "base_height",
  "orientation",
  "torques",
  "torque_tiredness",
  "power",
  "lin_vel_z",
  "ang_vel_xy",
  "dof_vel",
  "dof_acc",
  "root_acc",
  "action_rate",
  "dof_pos_limits",
  "collision",
  "feet_slip",
  "feet_yaw_diff",
  "feet_yaw_mean",
  "feet_roll",
  "feet_distance",
  "hip_roll_l2",
  "standing_hip_roll_l2",
  "standing_pose_l2",
)


def _apply_fast_sac_curriculum(cfg: ManagerBasedRlEnvCfg) -> None:
  """Aug 7 K1 rough FT curriculums (grid cmd set separately)."""
  cfg.curriculum.pop("command_vel", None)
  cfg.curriculum.pop("terrain_levels", None)
  cfg.curriculum["penalty_scale"] = CurriculumTermCfg(
    func=mdp.penalty_scale_curriculum,
    params={
      "reward_names": list(_FAST_SAC_PENALTY_REWARD_NAMES),
      "initial_scale": 0.5,
      "min_scale": 0.5,
      "max_scale": 1.0,
      # Wider band than 80/200 — narrow thresholds caused penalty ping-pong when
      # mean episode length hovered ~150–300 (plot looked like a sine wave).
      "level_down_threshold": 150.0,
      "level_up_threshold": 450.0,
      "degree": 0.0005,
      "num_compute_average_epl": 2000,
    },
  )
  cfg.curriculum["clearance_terminate"] = CurriculumTermCfg(
    func=mdp.clearance_terminate_curriculum,
    params={
      "term_name": "root_height",
      "initial_height": _K1_FAST_SAC_TERMINATE_INITIAL,
      "target_height": _K1_FAST_SAC_TERMINATE_HEIGHT,
      "min_height": _K1_FAST_SAC_TERMINATE_INITIAL,
      "max_height": _K1_FAST_SAC_TERMINATE_HEIGHT,
      "level_down_threshold": 150.0,
      "level_up_threshold": 450.0,
      "degree": 0.001,
      "num_compute_average_epl": 2000,
    },
  )


def _apply_fast_sac_commands(cfg: ManagerBasedRlEnvCfg) -> None:
  """Command setup aligned with the successful K1 rough FT run (Aug 2026).

  Grid curriculum ramps command difficulty from near-zero; without it, full-range
  ±1.5 m/s from iter 0 prevents gait formation (tracking peaks then collapses).
  ``rel_forward_envs`` is ignored while grid curriculum is enabled.
  """
  twist_cmd = cfg.commands["twist"]
  assert isinstance(twist_cmd, UniformVelocityCommandCfg)

  twist_cmd.heading_command = False
  twist_cmd.ranges.heading = None
  twist_cmd.resampling_time_range = (8.0, 12.0)
  twist_cmd.ranges.lin_vel_x = (-1.5, 1.5)
  twist_cmd.ranges.lin_vel_y = (-1.5, 1.5)
  twist_cmd.ranges.ang_vel_z = (-1.0, 1.0)
  twist_cmd.rel_standing_envs = 0.25
  twist_cmd.rel_forward_envs = 0.4
  twist_cmd.rel_heading_envs = 0.0
  twist_cmd.ranges.gait_frequency = (1.3, 2.6)
  twist_cmd.grid_curriculum = UniformVelocityCommandCfg.GridCurriculumCfg(
    enabled=True,
    update_rate=0.05,
    lin_vel_levels=10,
    ang_vel_levels=10,
    lin_vel_x_resolution=0.15,
    lin_vel_y_resolution=0.15,
    ang_vel_resolution=0.1,
    episode_length_toler=0.1,
    lin_vel_x_toler=0.4,
    lin_vel_y_toler=0.2,
    ang_vel_yaw_toler=0.2,
    filter_weight=0.1,
  )

  cfg.curriculum.pop("command_vel", None)


def _apply_booster_critic_obs(cfg: ManagerBasedRlEnvCfg) -> None:
  """Match Booster / ParameterWalk critic privileged obs (14-D).

  Critic = actor-like terms + ``base_mass_scaled(4) + base_lin_vel(3) +
  base_clearance(1) + push_force(3) + push_torque(3)``. Drops foot-centric
  privileged terms (height / contact / forces).
  """
  trunk_cfg = SceneEntityCfg("robot", body_names=("Trunk",))
  critic = cfg.observations["critic"].terms
  for key in (
    "foot_height",
    "foot_air_time",
    "foot_contact",
    "foot_contact_forces",
  ):
    critic.pop(key, None)
  critic["base_mass_scaled"] = ObservationTermCfg(
    func=mdp.base_mass_scaled,
    params={"asset_cfg": trunk_cfg},
  )
  critic["base_clearance"] = ObservationTermCfg(
    func=mdp.base_clearance,
    params={
      "sensor_name": "terrain_scan",
      "asset_cfg": SceneEntityCfg("robot"),
    },
  )
  critic["push_force"] = ObservationTermCfg(
    func=mdp.trunk_external_force,
    params={"asset_cfg": trunk_cfg, "scale": 0.1},
  )
  critic["push_torque"] = ObservationTermCfg(
    func=mdp.trunk_external_torque,
    params={"asset_cfg": trunk_cfg, "scale": 0.5},
  )


def _apply_fast_sac_domain_rand(cfg: ManagerBasedRlEnvCfg) -> None:
  """Booster T1-style mass/COM, friction, PD, kicks, and force/torque pushes."""
  # Mass/inertia (~±20% via alpha; T1 base_mass scale 0.8–1.2).
  cfg.events["robot_inertia"] = EventTermCfg(
    mode="startup",
    func=dr.pseudo_inertia,
    params={
      "asset_cfg": SceneEntityCfg("robot", body_names=(".*",)),
      "alpha_range": (-0.2, 0.2),
    },
  )
  # Trunk COM (T1 base_com ±0.1 m).
  cfg.events["base_com"] = EventTermCfg(
    mode="startup",
    func=dr.body_com_offset,
    params={
      "asset_cfg": SceneEntityCfg("robot", body_names=("Trunk",)),
      "operation": "add",
      "ranges": {
        0: (-0.1, 0.1),
        1: (-0.1, 0.1),
        2: (-0.1, 0.1),
      },
    },
  )
  # Other-body COM jitter (T1 other_com ±0.005 m).
  cfg.events["other_com"] = EventTermCfg(
    mode="startup",
    func=dr.body_com_offset,
    params={
      "asset_cfg": SceneEntityCfg("robot", body_names=_K1_OTHER_COM_BODIES),
      "operation": "add",
      "ranges": {
        0: (-0.005, 0.005),
        1: (-0.005, 0.005),
        2: (-0.005, 0.005),
      },
    },
  )
  # Foot friction (T1 friction 0.1–2.0).
  if "foot_friction" in cfg.events:
    cfg.events["foot_friction"].params["ranges"] = (0.1, 2.0)
  # PD gains (T1 dof_stiffness/damping scale 0.95–1.05).
  cfg.events["pd_gains"] = EventTermCfg(
    mode="startup",
    func=dr.pd_gains,
    params={
      "asset_cfg": SceneEntityCfg("robot"),
      "kp_range": (0.95, 1.05),
      "kd_range": (0.95, 1.05),
      "operation": "scale",
    },
  )
  # Booster T1 kick: additive Gaussian vel noise every 2 s.
  cfg.events.pop("push_robot", None)
  cfg.events["kick_robot"] = EventTermCfg(
    func=mdp.booster_kick_robots,
    mode="step",
    params={
      "kick_interval_s": 2.0,
      "kick_lin_vel_std": 0.1,
      "kick_ang_vel_std": 0.02,
      "asset_cfg": SceneEntityCfg("robot"),
    },
  )
  # Booster T1 push: trunk wrench N(0,10)/N(0,2) for 1 s every 5 s.
  cfg.events["push_robot"] = EventTermCfg(
    func=mdp.booster_push_robots,
    mode="step",
    params={
      "push_interval_s": 5.0,
      "push_duration_s": 1.0,
      "push_force_std": 10.0,
      "push_torque_std": 2.0,
      "asset_cfg": SceneEntityCfg("robot", body_names=("Trunk",)),
    },
  )


def _apply_fast_sac_walk_rewards(cfg: ManagerBasedRlEnvCfg) -> ManagerBasedRlEnvCfg:
  """Replace K1 PPO rewards with Booster Gym T1 reward set (K1 geometry).

  Weights match ``booster_gym/envs/T1.yaml`` (zero-weight terms omitted). K1-only
  numbers: height target 0.51, terminate clearance 0.35, stance ref 0.19.
  Enables ``only_positive_rewards``. Booster-style gait clock always on (no Holosoma
  fade); ``feet_swing`` only (no phase-sync ``gait`` reward). No curriculum.
  No ``feet_too_far``.
  """
  site_names = ("left_foot", "right_foot")
  foot_body_names = ("left_foot_link", "right_foot_link")

  # Kill NaN envs instead of crashing the whole batch in bf16 Normal().
  cfg.terminations["nan_state"] = TerminationTermCfg(func=mdp.nan_detection)

  def _policy_joints() -> SceneEntityCfg:
    # Policy joints (legs + arms); matches Booster "all controlled DOFs".
    return SceneEntityCfg(
      "robot",
      joint_names=_K1_POLICY_ACTUATORS,
      actuator_names=list(_K1_POLICY_ACTUATORS),
    )

  for key in list(cfg.curriculum.keys()):
    if key.startswith("penalty_") or key == "clearance_terminate":
      del cfg.curriculum[key]
  cfg.curriculum.pop("terrain_levels", None)

  cfg.episode_length_s = 30.0

  reset_joints = cfg.events.get("reset_robot_joints")
  if reset_joints is not None:
    reset_joints.params["poses"] = [KNEES_BENT_KEYFRAME.joint_pos]
    reset_joints.params["base_heights"] = [_K1_FAST_SAC_SPAWN_HEIGHT]

  # Start lenient; ``clearance_terminate`` curriculum tightens toward target.
  cfg.terminations["root_height"] = TerminationTermCfg(
    func=mdp.root_clearance_below_minimum,
    params={
      "minimum_height": _K1_FAST_SAC_TERMINATE_INITIAL,
      "sensor_name": "terrain_scan",
    },
  )
  # Not in booster_gym; drop K1 PPO split-kill.
  cfg.terminations.pop("feet_too_far", None)

  tracking_sigma = 0.25  # Booster: exp(-err² / sigma)
  track_filter = _K1_FAST_SAC_TRACK_FILTER_WEIGHT
  foot_pose_cfg = SceneEntityCfg("robot", body_names=foot_body_names)

  # Exact T1.yaml scales (non-zero only). Clip total reward ≥ 0 like Booster.
  cfg.only_positive_rewards = True

  cfg.rewards = {
    "survival": RewardTermCfg(func=mdp.is_alive, weight=0.25),
    "tracking_lin_vel_x": RewardTermCfg(
      func=mdp.track_lin_vel_axis,
      weight=2.0,
      params={
        "axis": 0,
        "command_name": "twist",
        "tracking_sigma": tracking_sigma,
        "filter_weight": track_filter,
      },
    ),
    "tracking_lin_vel_y": RewardTermCfg(
      func=mdp.track_lin_vel_axis,
      weight=2.0,
      params={
        "axis": 1,
        "command_name": "twist",
        "tracking_sigma": tracking_sigma,
        "filter_weight": track_filter,
      },
    ),
    "tracking_ang_vel": RewardTermCfg(
      func=mdp.track_ang_vel_z,
      weight=1.0,
      params={
        "command_name": "twist",
        "tracking_sigma": tracking_sigma,
        "filter_weight": track_filter,
      },
    ),
    "base_height": RewardTermCfg(
      func=mdp.base_height_target_l2,
      weight=-20.0,
      params={
        "target_height": _K1_FAST_SAC_HEIGHT_TARGET,
        "sensor_name": "terrain_scan",
      },
    ),
    "orientation": RewardTermCfg(
      func=mdp.flat_orientation_l2,
      weight=-5.0,
      params={"asset_cfg": SceneEntityCfg("robot")},
    ),
    "torques": RewardTermCfg(
      func=mdp.joint_torques_l2,
      weight=-3.0e-4,
      params={"asset_cfg": _policy_joints()},
    ),
    "torque_tiredness": RewardTermCfg(
      func=mdp.torque_tiredness,
      weight=-1.0e-2,
      params={"asset_cfg": _policy_joints()},
    ),
    "power": RewardTermCfg(
      func=mdp.joint_power_penalty,
      weight=-3.0e-3,
      params={"asset_cfg": _policy_joints()},
    ),
    "lin_vel_z": RewardTermCfg(
      func=mdp.root_lin_vel_z_l2,
      weight=-2.0,
      params={"filter_weight": track_filter},
    ),
    "ang_vel_xy": RewardTermCfg(
      func=mdp.body_angular_velocity_penalty,
      weight=-0.2,
      params={"asset_cfg": SceneEntityCfg("robot", body_names=("Trunk",))},
    ),
    "dof_vel": RewardTermCfg(
      func=mdp.joint_vel_l2,
      weight=-2.0e-4,
      params={"asset_cfg": _policy_joints()},
    ),
    "dof_acc": RewardTermCfg(
      func=mdp.joint_acc_l2,
      weight=-2.0e-7,
      params={"asset_cfg": _policy_joints()},
    ),
    "root_acc": RewardTermCfg(
      func=mdp.root_acc_l2,
      weight=-1.0e-4,
      params={"asset_cfg": SceneEntityCfg("robot")},
    ),
    "action_rate": RewardTermCfg(func=mdp.action_rate_l2, weight=-1.0),
    "dof_pos_limits": RewardTermCfg(func=mdp.joint_pos_limits, weight=-1.0),
    "collision": RewardTermCfg(
      func=mdp.self_collision_cost,
      weight=-1.0,
      params={"sensor_name": "self_collision", "force_threshold": 10.0},
    ),
    "feet_slip": RewardTermCfg(
      func=mdp.feet_slip,
      weight=-0.1,
      params={
        "sensor_name": "feet_ground_contact",
        "command_name": "twist",
        "command_threshold": 0.05,
        "asset_cfg": SceneEntityCfg("robot", site_names=site_names),
      },
    ),
    "feet_yaw_diff": RewardTermCfg(
      func=mdp.feet_yaw_diff_l2,
      weight=-0.5,
      params={"asset_cfg": foot_pose_cfg},
    ),
    "feet_yaw_mean": RewardTermCfg(
      func=mdp.feet_yaw_mean_l2,
      weight=-1.0,
      params={"asset_cfg": foot_pose_cfg},
    ),
    # Flat sole vs world horizontal (gravity). Allows hip roll if ankle cancels
    # it so the foot still lands flat.
    "feet_roll": RewardTermCfg(
      func=mdp.feet_roll_l2,
      weight=-0.35,
      params={"asset_cfg": foot_pose_cfg},
    ),
    "feet_distance": RewardTermCfg(
      func=mdp.feet_distance_lateral,
      weight=-1.0,
      params={
        "feet_distance_ref": 0.18,
        "wide_margin": _K1_FAST_SAC_FEET_DISTANCE_WIDE_MARGIN,
        "command_name": "twist",
        "side_walk_threshold": 0.1,
        "side_walk_margin_scale": 3.0,
        "asset_cfg": SceneEntityCfg("robot", site_names=site_names),
      },
    ),
    # Always-on (Aug 7 track_stance): stops hip ab/adduction stretch-out while walking.
    "hip_roll_l2": RewardTermCfg(
      func=mdp.joint_deviation_l2,
      weight=-1.0,
      params={
        "asset_cfg": SceneEntityCfg("robot", joint_names=(".*_Hip_Roll",)),
      },
    ),
    # Stand only: hip roll toward default ±0.04 (no stretch-out). Off while walking
    # so side-step / ankle-cancel flat contact are free.
    "standing_hip_roll_l2": RewardTermCfg(
      func=mdp.joint_deviation_l2_when_still,
      weight=_K1_FAST_SAC_STANDING_HIP_ROLL_WEIGHT,
      params={
        "command_name": "twist",
        "command_threshold": 0.05,
        "asset_cfg": SceneEntityCfg("robot", joint_names=(".*_Hip_Roll",)),
      },
    ),
    "standing_pose_l2": RewardTermCfg(
      func=mdp.joint_deviation_l2_when_still,
      weight=-1.0,
      params={
        "command_name": "twist",
        "command_threshold": 0.05,
        "asset_cfg": SceneEntityCfg(
          "robot", joint_names=(".*_Hip_Roll", ".*_Ankle_Roll")
        ),
      },
    ),
    "feet_swing": RewardTermCfg(
      func=mdp.feet_swing,
      weight=3.0,
      params={
        "sensor_name": "feet_ground_contact",
        "period": 1.0 / walk_params.GAIT_FREQUENCY_DEFAULT,
        "swing_period": walk_params.SWING_PERIOD,
        "command_name": "twist",
        "command_threshold": 0.05,
        "left_foot_name": "left_foot_link",
        "right_foot_name": "right_foot_link",
      },
    ),
  }

  _apply_fast_sac_domain_rand(cfg)

  _apply_booster_critic_obs(cfg)

  # Booster / ParameterWalk: sin/cos gait clock always on (zero when standing).
  for group in ("actor", "critic"):
    gait_term = cfg.observations[group].terms.get("gait_cycle")
    if gait_term is not None:
      gait_term.params["drop_step"] = int(1e12)
      gait_term.params["fade_steps"] = 0
    cmd_term = cfg.observations[group].terms.get("command")
    if cmd_term is not None:
      cmd_term.func = mdp.twist_velocity_commands
      cmd_term.params["command_name"] = "twist"

  _apply_fast_sac_curriculum(cfg)
  _apply_fast_sac_commands(cfg)
  return cfg


def booster_k1_rough_fast_sac_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Rough-terrain K1 velocity env with Booster T1-aligned rewards (PPO)."""
  cfg = booster_k1_rough_env_cfg(play=play)
  cfg = _apply_fast_sac_walk_rewards(cfg)
  # Match flat Booster actor/critic dims so flat PPO checkpoints can FT here.
  # Keep ``terrain_scan`` for clearance / base_height; drop privileged height obs.
  if "height_scan" in cfg.observations["critic"].terms:
    del cfg.observations["critic"].terms["height_scan"]
  if play:
    # Keep Booster rewards / commands / arm actions; drop train disturbances.
    cfg.episode_length_s = int(1e9)
    cfg.events.pop("kick_robot", None)
    cfg.events.pop("push_robot", None)
    cfg.curriculum = {}
    if "root_height" in cfg.terminations:
      cfg.terminations["root_height"].params["minimum_height"] = (
        _K1_FAST_SAC_TERMINATE_HEIGHT
      )
    twist = cfg.commands["twist"]
    assert isinstance(twist, UniformVelocityCommandCfg)
    if twist.grid_curriculum is not None:
      twist.grid_curriculum.enabled = False
    twist.ranges.lin_vel_x = (-1.5, 1.5)
    twist.ranges.lin_vel_y = (-1.5, 1.5)
    twist.ranges.ang_vel_z = (-1.0, 1.0)
  return cfg


def booster_k1_flat_fast_sac_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Flat-terrain K1 velocity env with Booster T1-aligned rewards (PPO/FastSAC)."""
  cfg = booster_k1_flat_env_cfg(play=play)
  cfg = _apply_fast_sac_walk_rewards(cfg)
  if play:
    cfg.episode_length_s = int(1e9)
    cfg.events.pop("kick_robot", None)
    cfg.events.pop("push_robot", None)
    cfg.curriculum = {}
    if "root_height" in cfg.terminations:
      cfg.terminations["root_height"].params["minimum_height"] = (
        _K1_FAST_SAC_TERMINATE_HEIGHT
      )
    twist = cfg.commands["twist"]
    assert isinstance(twist, UniformVelocityCommandCfg)
    if twist.grid_curriculum is not None:
      twist.grid_curriculum.enabled = False
    twist.ranges.lin_vel_x = (-1.5, 1.5)
    twist.ranges.lin_vel_y = (-1.5, 1.5)
    twist.ranges.ang_vel_z = (-1.0, 1.0)
  return cfg

"""Booster K1 velocity environment configurations."""

import math

from mjlab.asset_zoo.robots import (
  K1_ACTION_SCALE,
  get_k1_robot_cfg,
)
from mjlab.asset_zoo.robots.booster_k1.k1_constants import (
  KNEES_BENT_KEYFRAME,
  NUBOTS_KEYFRAME,
  get_k1_nubots_robot_cfg,
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
from mjlab.tasks.velocity.mdp import (
  ParameterWalkCommandCfg,
  UniformVelocityCommandCfg,
  walk_params,
)
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


# NuBots / Isaac Lab k1_walk_htwk: 16 policy joints, type-major L/R order.
_NUBOTS_ACTION_JOINTS = (
  "Left_Shoulder_Pitch",
  "Right_Shoulder_Pitch",
  "Left_Hip_Pitch",
  "Right_Hip_Pitch",
  "Left_Shoulder_Roll",
  "Right_Shoulder_Roll",
  "Left_Hip_Roll",
  "Right_Hip_Roll",
  "Left_Hip_Yaw",
  "Right_Hip_Yaw",
  "Left_Knee_Pitch",
  "Right_Knee_Pitch",
  "Left_Ankle_Pitch",
  "Right_Ankle_Pitch",
  "Left_Ankle_Roll",
  "Right_Ankle_Roll",
)

_NUBOTS_PASSIVE_JOINTS = (
  "Head_.*",
  ".*_Elbow_Pitch",
  ".*_Elbow_Yaw",
)

# Back to torso_swing_vx15 deploy lineage (tight shoulders).
# Keep torso rewards at orientation −8 / L −0.2 / ang_vel_xy −0.6.
_NUBOTS_LEG_ACTION_SCALE = 0.8
_NUBOTS_SHOULDER_ROLL_SCALE = 0.05
_NUBOTS_SHOULDER_PITCH_SCALE = 0.12
_NUBOTS_SHOULDER_PITCH_JOINTS = ("Left_Shoulder_Pitch", "Right_Shoulder_Pitch")
_NUBOTS_SHOULDER_ROLL_JOINTS = ("Left_Shoulder_Roll", "Right_Shoulder_Roll")
_NUBOTS_SHOULDER_JOINTS = _NUBOTS_SHOULDER_PITCH_JOINTS + _NUBOTS_SHOULDER_ROLL_JOINTS
_NUBOTS_ACTION_SCALE: dict[str, float] = {
  name: (
    _NUBOTS_SHOULDER_PITCH_SCALE
    if name in _NUBOTS_SHOULDER_PITCH_JOINTS
    else _NUBOTS_SHOULDER_ROLL_SCALE
    if name in _NUBOTS_SHOULDER_ROLL_JOINTS
    else _NUBOTS_LEG_ACTION_SCALE
  )
  for name in _NUBOTS_ACTION_JOINTS
}
# Pitch ±12° around 0; roll ±7.5° around arms-down (±1.3).
_NUBOTS_SHOULDER_PITCH_BAND = math.radians(12.0)
_NUBOTS_SHOULDER_ROLL_BAND = math.radians(30.5)
# Exact HTWK deployment guard: keep the arms-down shoulder-roll pose tight.
_HTWK_EXACT_SHOULDER_ROLL_BAND = math.radians(7.5)
# Pseudo-inertia alpha ranges corresponding to the desired mass-scale ranges.
_HTWK_EXACT_TRUNK_ALPHA_RANGE = (0.5 * math.log(0.8), 0.5 * math.log(1.2))
_HTWK_EXACT_OTHER_LINK_ALPHA_RANGE = (0.5 * math.log(0.9), 0.5 * math.log(1.1))
# Robust FT passive elbow fold range: 34–46 degrees.
_NUBOTS_ELBOW_FOLD_RANGE = (math.radians(34.0), math.radians(46.0))
_NUBOTS_ROBUST_FT_TRUNK_WRENCH_INTERVAL_S = 4.0
# Robust FT: allow counter-swing without the teacher's full shoulder lock.
_NUBOTS_ROBUST_FT_SHOULDER_DEV_START = -0.5
_NUBOTS_ROBUST_FT_SHOULDER_DEV_END = -0.05
# Leg-spacing FT: keep foot/knee clearance active at run speed and on hardware.
_NUBOTS_ROBUST_FT_FOOT_OFFSET_MIN_VEL_SCALE = 0.35
_NUBOTS_ROBUST_FT_MIN_FEET_SEPARATION = 0.14
_NUBOTS_ROBUST_FT_MIN_FEET_SITE_XY = 0.14
_NUBOTS_ROBUST_FT_FEET_MIN_SEP_WEIGHT = -3.0
_NUBOTS_ROBUST_FT_FEET_SITE_XY_WEIGHT = -2.0
_NUBOTS_ROBUST_FT_KNEE_SAFE_DISTANCE = 0.18
_NUBOTS_ROBUST_FT_KNEE_SEPARATION_WEIGHT = -3.0
_NUBOTS_ROBUST_FT_HIP_ROLL_MAX_DEVIATION = 0.18
_NUBOTS_ROBUST_FT_FOOT_FOOT_COLLISION_WEIGHT = -3.0
# Sole must clear the ground during swing (not heel-up / toe-drag).
_NUBOTS_ROBUST_FT_SWING_MIN_CLEARANCE = 0.04
_NUBOTS_ROBUST_FT_SWING_TARGET_CLEARANCE = 0.06
_NUBOTS_ROBUST_FT_SWING_SOLE_CLEARANCE_WEIGHT = 2.0
# Wider shoulder authority used by the high-speed FT (see arm-swing unlock).
_NUBOTS_ARM_SWING_PITCH_SCALE = 0.30
_NUBOTS_ARM_SWING_ROLL_SCALE = 0.12
_NUBOTS_ARM_SWING_PITCH_BAND = math.radians(25.0)
_NUBOTS_ARM_SWING_ROLL_BAND = math.radians(15.0)
_NUBOTS_HEIGHT_TARGET = 0.575
_NUBOTS_ACTION_RATE_WEIGHT = -0.5
_NUBOTS_TERRAIN_MIX_INITIAL = (0.80, 0.10, 0.10)  # flat / rough / wave
_NUBOTS_TERRAIN_MIX_TARGET = (0.80, 0.10, 0.10)
_NUBOTS_PHASE1_TERRAIN = (0.95, 0.05)  # flat / rough only
_NUBOTS_PHASE2_TERRAIN_INITIAL = (0.90, 0.05, 0.05)  # flat / rough / wave
_NUBOTS_PHASE2_TERRAIN_TARGET = (0.70, 0.15, 0.15)
# Raise with taller keyframe so clearance reward does not pull back into squat.
_NUBOTS_CLEARANCE_BAND = (0.54, 0.60)
_NUBOTS_DEPLOY_PW_RANGES: dict[str, tuple[float, float]] = {
  "foot_yaw_l_range": (-0.15, 0.15),
  "foot_yaw_r_range": (-0.15, 0.15),
  "feet_offset_x_range": (-0.03, 0.03),
  "feet_offset_y_range": (-0.03, 0.03),
  # Mild forward pitch only — deep crouch + 0.1 pitch fought upright FT.
  "body_pitch_range": (0.0, 0.06),
  "body_roll_range": (-0.05, 0.05),
}
_NUBOTS_SHOULDER_CLIP: dict[str, tuple[float, float]] = {
  "Left_Shoulder_Pitch": (
    -_NUBOTS_SHOULDER_PITCH_BAND,
    _NUBOTS_SHOULDER_PITCH_BAND,
  ),
  "Right_Shoulder_Pitch": (
    -_NUBOTS_SHOULDER_PITCH_BAND,
    _NUBOTS_SHOULDER_PITCH_BAND,
  ),
  "Left_Shoulder_Roll": (
    -1.3 - _NUBOTS_SHOULDER_ROLL_BAND,
    -1.3 + _NUBOTS_SHOULDER_ROLL_BAND,
  ),
  "Right_Shoulder_Roll": (
    1.3 - _NUBOTS_SHOULDER_ROLL_BAND,
    1.3 + _NUBOTS_SHOULDER_ROLL_BAND,
  ),
}


def _nubots_policy_joint_cfg() -> SceneEntityCfg:
  return SceneEntityCfg(
    "robot",
    joint_names=_NUBOTS_ACTION_JOINTS,
    preserve_order=True,
  )


def _apply_nubots_deploy_pw_ranges(cfg: ManagerBasedRlEnvCfg, play: bool) -> None:
  """Narrow ParameterWalk command randomization toward deploy defaults."""
  if play:
    return
  for group in ("actor", "critic"):
    terms = cfg.observations[group].terms
    pw = terms.get("velocity_commands")
    if pw is not None:
      pw.params.update(_NUBOTS_DEPLOY_PW_RANGES)


def booster_k1_nubots_flat_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Flat K1 env matching NuBots teacher: 66-D actor obs, 16-D actions.

  Obs order (Isaac ``k1_walk_htwk`` / ``walk_policy_nubots_v1``)::

    projected_gravity(3), base_ang_vel(3), parameter_walk_cmd(12),
    joint_pos(16), joint_vel(16)×0.1, last_action(16)

  Student MLP matches the teacher so ONNX weights load 1:1.
  """
  from mjlab.managers.observation_manager import ObservationGroupCfg
  from mjlab.utils.noise import UniformNoiseCfg as Unoise

  cfg = booster_k1_flat_fast_sac_env_cfg(play=play)
  cfg.scene.entities = {"robot": get_k1_nubots_robot_cfg()}

  cfg.events["reset_robot_joints"] = EventTermCfg(
    func=mdp.reset_joints_from_pose_catalog,
    mode="reset",
    params={
      "poses": [NUBOTS_KEYFRAME.joint_pos],
      "base_heights": [NUBOTS_KEYFRAME.pos[2]],
      "position_range": (0.0, 0.0) if play else (-0.1, 0.1),
      "velocity_range": (0.0, 0.0),
      "asset_cfg": SceneEntityCfg("robot", joint_names=(".*",)),
    },
  )
  cfg.events["hold_passive"] = EventTermCfg(
    func=mdp.set_joint_position_targets_to_default,
    mode="reset",
    params={
      "asset_cfg": SceneEntityCfg("robot", joint_names=_NUBOTS_PASSIVE_JOINTS),
    },
  )

  joint_pos_action = cfg.actions["joint_pos"]
  assert isinstance(joint_pos_action, JointPositionActionCfg)
  joint_pos_action.actuator_names = _NUBOTS_ACTION_JOINTS
  # Legs ±0.8; shoulder roll ±0.05 / ±7.5°; pitch ±0.12 / ±12°.
  joint_pos_action.scale = dict(_NUBOTS_ACTION_SCALE)
  joint_pos_action.preserve_order = True
  joint_pos_action.clip = dict(_NUBOTS_SHOULDER_CLIP)
  joint_pos_action.use_default_offset = True

  policy_joints = _nubots_policy_joint_cfg()
  pw_params: dict = {
    "command_name": "twist",
    "command_threshold": 0.05,
    "period": 1.0 / walk_params.GAIT_FREQUENCY_DEFAULT,
    # Play: small forward pitch only (was 0.1). Train: allow mild pitch.
    "body_pitch_range": (0.05, 0.05) if play else (-0.05, 0.15),
    "body_roll_range": (0.0, 0.0) if play else (-0.1, 0.1),
  }
  if not play:
    pw_params.update(
      {
        "foot_yaw_l_range": (-0.7, 0.7),
        "foot_yaw_r_range": (-0.7, 0.7),
        "feet_offset_x_range": (-0.15, 0.15),
        "feet_offset_y_range": (-0.08, 0.15),
      }
    )

  actor_terms = {
    "projected_gravity": ObservationTermCfg(
      func=mdp.projected_gravity,
      noise=None if play else Unoise(n_min=-0.05, n_max=0.05),
    ),
    "base_ang_vel": ObservationTermCfg(
      func=mdp.base_ang_vel,
      noise=None if play else Unoise(n_min=-0.2, n_max=0.2),
    ),
    "velocity_commands": ObservationTermCfg(
      func=mdp.nubots_parameter_walk_commands,
      params=pw_params,
    ),
    "joint_pos": ObservationTermCfg(
      func=mdp.joint_pos_rel,
      params={"asset_cfg": policy_joints},
      noise=None if play else Unoise(n_min=-0.01, n_max=0.01),
    ),
    "joint_vel": ObservationTermCfg(
      func=mdp.joint_vel_rel,
      params={"asset_cfg": policy_joints},
      scale=0.1,
      noise=None if play else Unoise(n_min=-0.15, n_max=0.15),
    ),
    "actions": ObservationTermCfg(func=mdp.last_action),
  }
  critic_terms = {
    **actor_terms,
    "base_lin_vel": ObservationTermCfg(func=mdp.base_lin_vel),
    "base_height": ObservationTermCfg(
      func=mdp.base_clearance,
      params={
        "sensor_name": None,
        "asset_cfg": SceneEntityCfg("robot"),
      },
    ),
  }
  cfg.observations["actor"] = ObservationGroupCfg(
    terms=actor_terms,
    concatenate_terms=True,
    enable_corruption=not play,
  )
  cfg.observations["critic"] = ObservationGroupCfg(
    terms=critic_terms,
    concatenate_terms=True,
    enable_corruption=False,
  )

  # Sensor latency 0–2 steps (0–40 ms @ 50 Hz); matches base K1 rough. Skip
  # commands / last_action so the MDP timing of those stays clean.
  if not play:
    for obs_name in (
      "projected_gravity",
      "base_ang_vel",
      "joint_pos",
      "joint_vel",
    ):
      term = cfg.observations["actor"].terms[obs_name]
      term.delay_min_lag = 0
      term.delay_max_lag = 2
      term.delay_hold_prob = 0.9

  twist = cfg.commands["twist"]
  assert isinstance(twist, UniformVelocityCommandCfg)
  twist.ranges.lin_vel_x = (-1.0, 2.0)
  twist.ranges.lin_vel_y = (-1.0, 1.0)
  twist.ranges.ang_vel_z = (-1.6, 1.6)
  twist.ranges.gait_frequency = (1.5, 3.0)
  twist.rel_standing_envs = 0.1
  _apply_nubots_trunk_com_bias(cfg)
  return cfg


def _apply_nubots_trunk_com_bias(cfg: ManagerBasedRlEnvCfg) -> None:
  """Bias Trunk COM slightly forward so a heavy upper body need not lean back."""
  if "base_com" not in cfg.events:
    return
  cfg.events["base_com"].params["ranges"] = {
    0: (-0.02, 0.08),  # X: prefer forward
    1: (-0.05, 0.05),
    2: (-0.04, 0.04),
  }


def _apply_nubots_torso_swing_penalties(cfg: ManagerBasedRlEnvCfg) -> None:
  """Dampen trunk swing at speed without overconstraining fast turns.

  Sway is suppressed by the rate terms (``ang_vel_xy``, ``angular_momentum``);
  ``orientation`` stays at the proven −8 because it penalizes absolute tilt and
  cannot tell a steady accelerating lean from oscillation. Both speed-scaled
  terms reference 2 m/s so they do not triple at the target speed.
  """
  cfg.rewards["ang_vel_xy"].weight = -0.6
  cfg.rewards["ang_vel_xy"].params["command_name"] = "twist"
  cfg.rewards["ang_vel_xy"].params["speed_ref"] = 2.0
  cfg.rewards["orientation"].weight = -8.0
  cfg.rewards["orientation"].params["command_name"] = "twist"
  cfg.rewards["orientation"].params["speed_ref"] = 2.0
  cfg.rewards["angular_momentum"] = RewardTermCfg(
    func=mdp.angular_momentum_penalty,
    weight=-0.2,
    params={"sensor_name": "robot/root_angmom"},
  )
  if "collision" in cfg.rewards:
    cfg.rewards["collision"].weight = -1.75


def _apply_nubots_arm_swing_unlock(cfg: ManagerBasedRlEnvCfg) -> None:
  """Widen shoulder authority so the momentum penalty has an actuator.

  At deploy-tight shoulder scales the only way to shed trunk angular momentum
  is a shorter stride, so ``angular_momentum`` acts as a speed cap instead of a
  sway damper. Deploy configs keep the tight bands; only the high-speed FT
  unlocks them.
  """
  action = cfg.actions["joint_pos"]
  assert isinstance(action, JointPositionActionCfg)
  action.scale = dict(action.scale)
  action.clip = dict(action.clip or {})
  for name in _NUBOTS_SHOULDER_PITCH_JOINTS:
    action.scale[name] = _NUBOTS_ARM_SWING_PITCH_SCALE
    action.clip[name] = (
      -_NUBOTS_ARM_SWING_PITCH_BAND,
      _NUBOTS_ARM_SWING_PITCH_BAND,
    )
  for name in _NUBOTS_SHOULDER_ROLL_JOINTS:
    center = -1.3 if name.startswith("Left") else 1.3
    action.scale[name] = _NUBOTS_ARM_SWING_ROLL_SCALE
    action.clip[name] = (
      center - _NUBOTS_ARM_SWING_ROLL_BAND,
      center + _NUBOTS_ARM_SWING_ROLL_BAND,
    )


def booster_k1_nubots_rough_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Rough-terrain NuBots-parity env (same 66→16 interface as flat).

  Terrain mix (train): starts flat 90% / rough 5% / wave 5%, ramps to 80/10/10
  when avg episode length > 600 and root_height kills < 2%.
  Tracking weights raised vs flat FastSAC base; velocity grid update slowed
  so command difficulty does not outrun rough adaptation.
  """
  cfg = booster_k1_rough_fast_sac_env_cfg(play=play)
  flat_cfg = booster_k1_nubots_flat_env_cfg(play=play)
  cfg.scene.entities = flat_cfg.scene.entities
  cfg.actions = flat_cfg.actions
  cfg.observations = flat_cfg.observations
  cfg.events["reset_robot_joints"] = flat_cfg.events["reset_robot_joints"]
  cfg.events["hold_passive"] = flat_cfg.events["hold_passive"]

  cfg.rewards["base_height"].params["target_height"] = _NUBOTS_HEIGHT_TARGET
  cfg.rewards["action_rate"].weight = _NUBOTS_ACTION_RATE_WEIGHT
  _apply_nubots_trunk_com_bias(cfg)
  _apply_nubots_torso_swing_penalties(cfg)

  if (
    not play
    and cfg.scene.terrain is not None
    and cfg.scene.terrain.terrain_generator is not None
  ):
    flat_p, rough_p, wave_p = _NUBOTS_TERRAIN_MIX_INITIAL
    cfg.scene.terrain.terrain_generator.curriculum = False
    cfg.scene.terrain.terrain_generator.sub_terrains = {
      "flat": flat(proportion=flat_p),
      "random_rough": random_rough(proportion=rough_p),
      "wave_terrain": wave_terrain(proportion=wave_p),
    }
    cfg.curriculum["nubots_terrain_mix"] = CurriculumTermCfg(
      func=mdp.nubots_terrain_mix_curriculum,
      params={
        "initial_proportions": list(_NUBOTS_TERRAIN_MIX_INITIAL),
        "target_proportions": list(_NUBOTS_TERRAIN_MIX_TARGET),
        "ep_length_threshold": 600.0,
        "root_height_rate_threshold": 0.02,
        "num_compute_average_epl": 2000,
      },
    )
  # Emphasize velocity tracking on rough (was 2.0 / 2.0 / 1.0).
  cfg.rewards["tracking_lin_vel_x"].weight = 2.5
  cfg.rewards["tracking_lin_vel_y"].weight = 2.5
  cfg.rewards["tracking_ang_vel"].weight = 1.25

  # Slightly wider actuator mismatch + stronger disturbances for rough FT.
  if not play:
    if "pd_gains" in cfg.events:
      cfg.events["pd_gains"].params["kp_range"] = (0.9, 1.1)
      cfg.events["pd_gains"].params["kd_range"] = (0.9, 1.1)
    if "kick_robot" in cfg.events:
      cfg.events["kick_robot"].params["kick_lin_vel_std"] = 0.15
      cfg.events["kick_robot"].params["kick_ang_vel_std"] = 0.03
    if "push_robot" in cfg.events:
      cfg.events["push_robot"].params["push_force_std"] = 12.0
      cfg.events["push_robot"].params["push_torque_std"] = 2.5
    # Small pitch/roll at reset (yaw already full-range).
    pose = cfg.events["reset_base"].params.setdefault("pose_range", {})
    pose.setdefault("roll", (-0.1, 0.1))
    pose.setdefault("pitch", (-0.1, 0.1))

  twist = cfg.commands["twist"]
  assert isinstance(twist, UniformVelocityCommandCfg)
  flat_twist = flat_cfg.commands["twist"]
  assert isinstance(flat_twist, UniformVelocityCommandCfg)
  twist.ranges = flat_twist.ranges
  twist.rel_standing_envs = flat_twist.rel_standing_envs
  # Slow velocity-grid expansion (default update_rate=0.05 was too aggressive).
  if twist.grid_curriculum is not None and twist.grid_curriculum.enabled:
    twist.grid_curriculum.update_rate = 0.01
    twist.grid_curriculum.lin_vel_x_toler = 0.25
    twist.grid_curriculum.lin_vel_y_toler = 0.15
    twist.grid_curriculum.ang_vel_yaw_toler = 0.15
  return cfg


def booster_k1_nubots_phase1_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Phase-1 posture lock FT: calm terrain, clearance band, deploy-narrow PW.

  Train mix: flat 95% / rough 5% (no wave, no terrain ramp).
  Reduced kick/push, ang velocity grid capped at level 6, gait 1.6–2.2 Hz.
  """
  cfg = booster_k1_nubots_rough_env_cfg(play=play)
  cfg.curriculum.pop("nubots_terrain_mix", None)

  min_clear, max_clear = _NUBOTS_CLEARANCE_BAND
  cfg.rewards["base_height"] = RewardTermCfg(
    func=mdp.base_clearance_range_l2,
    weight=-20.0,
    params={
      "minimum_height": min_clear,
      "maximum_height": max_clear,
      "sensor_name": "terrain_scan",
    },
  )
  cfg.rewards["action_rate"].weight = _NUBOTS_ACTION_RATE_WEIGHT
  _apply_nubots_deploy_pw_ranges(cfg, play)

  if (
    not play
    and cfg.scene.terrain is not None
    and cfg.scene.terrain.terrain_generator is not None
  ):
    flat_p, rough_p = _NUBOTS_PHASE1_TERRAIN
    cfg.scene.terrain.terrain_generator.curriculum = False
    cfg.scene.terrain.terrain_generator.sub_terrains = {
      "flat": flat(proportion=flat_p),
      "random_rough": random_rough(proportion=rough_p),
    }

  if not play:
    if "kick_robot" in cfg.events:
      cfg.events["kick_robot"].params["kick_lin_vel_std"] = 0.08
      cfg.events["kick_robot"].params["kick_ang_vel_std"] = 0.015
    if "push_robot" in cfg.events:
      cfg.events["push_robot"].params["push_force_std"] = 8.0
      cfg.events["push_robot"].params["push_torque_std"] = 1.5

  twist = cfg.commands["twist"]
  assert isinstance(twist, UniformVelocityCommandCfg)
  twist.ranges.gait_frequency = (1.6, 2.2)
  if twist.grid_curriculum is not None and twist.grid_curriculum.enabled:
    twist.grid_curriculum.update_rate = 0.005
    twist.grid_curriculum.lin_vel_levels = 8
    twist.grid_curriculum.ang_vel_levels = 6
    twist.grid_curriculum.lin_vel_x_toler = 0.30
    twist.grid_curriculum.lin_vel_y_toler = 0.20
    twist.grid_curriculum.ang_vel_yaw_toler = 0.20
  return cfg


def booster_k1_nubots_phase2_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Phase-2 rough ramp FT from Phase-1 posture lock.

  Starts flat 90% / rough 5% / wave 5%; ramps to 70/15/15 when avg ep length
  > 700 and fell_over rate < 5%. Soft kick/push until ramp, then restored.
  Keeps clearance band, deploy-narrow PW, ang grid capped at 6.
  """
  cfg = booster_k1_nubots_phase1_env_cfg(play=play)

  if (
    not play
    and cfg.scene.terrain is not None
    and cfg.scene.terrain.terrain_generator is not None
  ):
    flat_p, rough_p, wave_p = _NUBOTS_PHASE2_TERRAIN_INITIAL
    cfg.scene.terrain.terrain_generator.curriculum = False
    cfg.scene.terrain.terrain_generator.sub_terrains = {
      "flat": flat(proportion=flat_p),
      "random_rough": random_rough(proportion=rough_p),
      "wave_terrain": wave_terrain(proportion=wave_p),
    }
    cfg.curriculum["nubots_terrain_mix"] = CurriculumTermCfg(
      func=mdp.nubots_terrain_mix_curriculum,
      params={
        "initial_proportions": list(_NUBOTS_PHASE2_TERRAIN_INITIAL),
        "target_proportions": list(_NUBOTS_PHASE2_TERRAIN_TARGET),
        "ep_length_threshold": 700.0,
        "fell_over_rate_threshold": 0.05,
        "num_compute_average_epl": 2000,
        "restore_disturbances": {
          "kick_lin_vel_std": 0.12,
          "kick_ang_vel_std": 0.025,
          "push_force_std": 10.0,
          "push_torque_std": 2.0,
        },
      },
    )

  # Soft disturbances until terrain ramp fires.
  if not play:
    if "kick_robot" in cfg.events:
      cfg.events["kick_robot"].params["kick_lin_vel_std"] = 0.08
      cfg.events["kick_robot"].params["kick_ang_vel_std"] = 0.015
    if "push_robot" in cfg.events:
      cfg.events["push_robot"].params["push_force_std"] = 8.0
      cfg.events["push_robot"].params["push_torque_std"] = 1.5

  # Keep ang grid capped; slightly slower lin unlock than Phase 1.
  twist = cfg.commands["twist"]
  assert isinstance(twist, UniformVelocityCommandCfg)
  twist.ranges.gait_frequency = (1.6, 2.2)
  if twist.grid_curriculum is not None and twist.grid_curriculum.enabled:
    twist.grid_curriculum.update_rate = 0.005
    twist.grid_curriculum.lin_vel_levels = 7
    twist.grid_curriculum.ang_vel_levels = 6
    twist.grid_curriculum.lin_vel_x_toler = 0.30
    twist.grid_curriculum.lin_vel_y_toler = 0.20
    twist.grid_curriculum.ang_vel_yaw_toler = 0.20
  return cfg


def booster_k1_nubots_phase2_stabilize_env_cfg(
  play: bool = False,
) -> ManagerBasedRlEnvCfg:
  """Phase-2 finish: stabilize on fixed 70/15/15 before speed unlock.

  No terrain ramp. Soft disturbances. Velocity grid disabled with moderate
  fixed command ranges (~1 m/s forward focus). Clearance band + deploy PW kept.
  """
  cfg = booster_k1_nubots_phase1_env_cfg(play=play)
  cfg.curriculum.pop("nubots_terrain_mix", None)

  if (
    not play
    and cfg.scene.terrain is not None
    and cfg.scene.terrain.terrain_generator is not None
  ):
    flat_p, rough_p, wave_p = _NUBOTS_PHASE2_TERRAIN_TARGET
    cfg.scene.terrain.terrain_generator.curriculum = False
    cfg.scene.terrain.terrain_generator.sub_terrains = {
      "flat": flat(proportion=flat_p),
      "random_rough": random_rough(proportion=rough_p),
      "wave_terrain": wave_terrain(proportion=wave_p),
    }

  if not play:
    if "kick_robot" in cfg.events:
      cfg.events["kick_robot"].params["kick_lin_vel_std"] = 0.08
      cfg.events["kick_robot"].params["kick_ang_vel_std"] = 0.015
    if "push_robot" in cfg.events:
      cfg.events["push_robot"].params["push_force_std"] = 8.0
      cfg.events["push_robot"].params["push_torque_std"] = 1.5

  twist = cfg.commands["twist"]
  assert isinstance(twist, UniformVelocityCommandCfg)
  if twist.grid_curriculum is not None:
    twist.grid_curriculum.enabled = False
  twist.ranges.lin_vel_x = (-0.5, 1.0)
  twist.ranges.lin_vel_y = (-0.5, 0.5)
  twist.ranges.ang_vel_z = (-0.8, 0.8)
  twist.ranges.gait_frequency = (1.6, 2.2)
  twist.rel_standing_envs = 0.15
  return cfg


def booster_k1_nubots_phase3_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Phase-3 speed unlock on fixed Phase-2 terrain (70/15/15).

  Re-enables velocity grid toward full NuBots ranges (vx up to 2.0 m/s).
  Stronger lin tracking; ang grid still capped below max; soft disturbances.
  Keeps clearance band + deploy-narrow ParameterWalk.
  """
  cfg = booster_k1_nubots_phase2_stabilize_env_cfg(play=play)

  # Emphasize forward speed tracking.
  cfg.rewards["tracking_lin_vel_x"].weight = 3.0
  cfg.rewards["tracking_lin_vel_y"].weight = 2.5
  cfg.rewards["tracking_ang_vel"].weight = 1.5
  for name in ("tracking_lin_vel_x", "tracking_lin_vel_y", "tracking_ang_vel"):
    if "tracking_sigma" in cfg.rewards[name].params:
      cfg.rewards[name].params["tracking_sigma"] = 0.20

  if not play:
    if "kick_robot" in cfg.events:
      cfg.events["kick_robot"].params["kick_lin_vel_std"] = 0.10
      cfg.events["kick_robot"].params["kick_ang_vel_std"] = 0.02
    if "push_robot" in cfg.events:
      cfg.events["push_robot"].params["push_force_std"] = 9.0
      cfg.events["push_robot"].params["push_torque_std"] = 1.8

  twist = cfg.commands["twist"]
  assert isinstance(twist, UniformVelocityCommandCfg)
  # Full NuBots command envelope; unlock via grid (not all at once).
  twist.ranges.lin_vel_x = (-1.0, 2.0)
  twist.ranges.lin_vel_y = (-1.0, 1.0)
  twist.ranges.ang_vel_z = (-1.6, 1.6)
  twist.ranges.gait_frequency = (1.5, 2.6)
  twist.rel_standing_envs = 0.1
  if twist.grid_curriculum is None:
    from mjlab.tasks.velocity.mdp.velocity_command import (
      UniformVelocityCommandCfg as _U,
    )

    twist.grid_curriculum = _U.GridCurriculumCfg(enabled=True)
  twist.grid_curriculum.enabled = True
  # Slower unlock than first phase3_speed_arms5 (ang max hit 8 by ~+450 iters
  # while ep length fell 1100→560 and model_best never moved — phase2_sym mode).
  twist.grid_curriculum.update_rate = 0.004
  twist.grid_curriculum.lin_vel_levels = 10
  twist.grid_curriculum.ang_vel_levels = 6
  twist.grid_curriculum.lin_vel_x_resolution = 0.15
  twist.grid_curriculum.lin_vel_y_resolution = 0.15
  twist.grid_curriculum.ang_vel_resolution = 0.1
  twist.grid_curriculum.lin_vel_x_toler = 0.30
  twist.grid_curriculum.lin_vel_y_toler = 0.20
  twist.grid_curriculum.ang_vel_yaw_toler = 0.25
  return cfg


def booster_k1_nubots_quality_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Quality FT: cut fall rate on mixed rough before another speed unlock.

  Fixed terrain 80/10/10 (flat / rough / wave). Velocity grid off.
  Moderate command ranges (vx up to 1.0). Soft disturbances. Survival boosted
  vs tracking so upright episodes win over chasing speed into falls.
  """
  cfg = booster_k1_nubots_phase1_env_cfg(play=play)
  cfg.curriculum.pop("nubots_terrain_mix", None)

  if (
    not play
    and cfg.scene.terrain is not None
    and cfg.scene.terrain.terrain_generator is not None
  ):
    cfg.scene.terrain.terrain_generator.curriculum = False
    cfg.scene.terrain.terrain_generator.sub_terrains = {
      "flat": flat(proportion=0.80),
      "random_rough": random_rough(proportion=0.10),
      "wave_terrain": wave_terrain(proportion=0.10),
    }

  # Prefer staying up / upright over chasing Phase-3 speed tracking.
  cfg.rewards["survival"].weight = 0.40
  cfg.rewards["tracking_lin_vel_x"].weight = 2.5
  cfg.rewards["tracking_lin_vel_y"].weight = 2.25
  cfg.rewards["tracking_ang_vel"].weight = 1.25
  # orientation weight set in _apply_nubots_torso_swing_penalties (−8).
  cfg.rewards["standing_pose_l2"].weight = -1.5  # pull legs toward taller keyframe
  _apply_nubots_arm_swing_unlock(cfg)

  if not play:
    if "kick_robot" in cfg.events:
      cfg.events["kick_robot"].params["kick_lin_vel_std"] = 0.06
      cfg.events["kick_robot"].params["kick_ang_vel_std"] = 0.012
    if "push_robot" in cfg.events:
      cfg.events["push_robot"].params["push_force_std"] = 6.0
      cfg.events["push_robot"].params["push_torque_std"] = 1.2

  twist = cfg.commands["twist"]
  assert isinstance(twist, UniformVelocityCommandCfg)
  if twist.grid_curriculum is not None:
    twist.grid_curriculum.enabled = False
  twist.ranges.lin_vel_x = (-0.5, 1.0)
  twist.ranges.lin_vel_y = (-0.5, 0.5)
  twist.ranges.ang_vel_z = (-0.8, 0.8)
  twist.ranges.gait_frequency = (1.6, 2.2)
  twist.rel_standing_envs = 0.20
  return cfg


# Speed-lineage constants. Measured on the Quality lineage's best checkpoint
# (model_63200) with reward_probe.py / gait_probe.py; see the docstring of
# ``booster_k1_nubots_speed_env_cfg`` for what each number is answering.
_NUBOTS_SPEED_TILT_SPEED_REF = 4.0
_NUBOTS_SPEED_TRACK_SPEED_REF = 1.5
_NUBOTS_SPEED_ANG_VEL_XY_WEIGHT = -0.15
_NUBOTS_SPEED_ORIENTATION_WEIGHT = -4.0
_NUBOTS_SPEED_GAIT_WEIGHT = 2.0
# Duty factor for the reference gait schedule. The Quality lineage runs at 0.49
# with 6% double support -- effectively a run. 0.60 restores ~20% double support.
_NUBOTS_SPEED_STANCE_FRACTION = 0.60
# Cadence must be able to buy the speed that trunk lean currently buys: 2.0 m/s
# needs ~0.31 m of stride at 3.2 Hz, versus 0.247 m at 2.73 Hz today.
_NUBOTS_SPEED_GAIT_FREQUENCY_RANGE = (1.6, 3.4)


def _apply_nubots_speed_budget(cfg: ManagerBasedRlEnvCfg) -> None:
  """Keep the reward sum positive at target speed.

  ``only_positive_rewards`` clamps the *total* step reward at zero, so any step
  whose raw sum is negative delivers exactly 0 and carries no gradient. Measured
  on the Quality lineage at full penalty scale, the raw sum crosses zero between
  1.3 and 1.5 m/s and 48% of steps at 1.5 m/s (80% at 1.8) are clamped flat --
  which is why pushing the tilt penalties harder did nothing: the extra weight
  lands on steps that are already at the clamp floor and is discarded.

  Two structural causes, both addressed here:

  1. The tracking rewards are bounded exponentials capped at 1, so the positive
     budget is flat in commanded speed while the penalties grow with the
     violence of the motion. ``speed_ref`` on the tracking terms makes the
     income scale with the command, mirroring the penalties.
  2. ``ang_vel_xy`` and ``orientation`` are multiplied by ``1 + speed/speed_ref``
     with ``speed_ref = 1``, i.e. 2.5x at 1.5 m/s. Raising the reference and
     cutting ``ang_vel_xy`` (the single largest penalty in the objective, at
     -4.38/s) stops the trunk terms outspending the entire positive budget.

  Net at 1.5 m/s moves from -4.18/s to +3.36/s, and the share of clamped steps
  from 48% to 11%.
  """
  for name in ("tracking_lin_vel_x", "tracking_lin_vel_y", "tracking_ang_vel"):
    cfg.rewards[name].params["speed_ref"] = _NUBOTS_SPEED_TRACK_SPEED_REF
  cfg.rewards["ang_vel_xy"].weight = _NUBOTS_SPEED_ANG_VEL_XY_WEIGHT
  cfg.rewards["ang_vel_xy"].params["speed_ref"] = _NUBOTS_SPEED_TILT_SPEED_REF
  cfg.rewards["orientation"].weight = _NUBOTS_SPEED_ORIENTATION_WEIGHT
  cfg.rewards["orientation"].params["speed_ref"] = _NUBOTS_SPEED_TILT_SPEED_REF


def _apply_nubots_cadence_tracking(cfg: ManagerBasedRlEnvCfg) -> None:
  """Close the cadence loop by scoring contact state against the gait clock.

  The clock itself already runs at the commanded frequency
  (``phase += dt * gait_frequency``), but nothing holds the feet to it. The
  lineage keeps only ``feet_swing``, which pays a one-sided bonus for being
  airborne inside a narrow window and never penalises stepping off-schedule, so
  the robot free-runs: at a commanded 2.2 Hz (4.4 steps/s) it actually takes
  5.45 steps/s and simply forgoes most of the swing reward, collecting 1.15/s of
  an available 6.0/s.

  ``feet_gait`` scores both directions -- planted during swing and airborne
  during stance are equally wrong -- which pins step timing to the command and
  makes cadence a usable control input. That matters because cadence is the only
  way to buy speed that does not go through trunk lean, and lean is hard-capped
  at 11.3 deg by the 20 Nm ankle.

  ``drop_step`` must stay effectively infinite: the term shares the gait clock's
  drop/fade curriculum, so leaving the default would fade cadence enforcement
  out after 8000*24 steps and silently restore the free-running gait.
  """
  cfg.rewards["gait"] = RewardTermCfg(
    func=mdp.feet_gait,
    weight=_NUBOTS_SPEED_GAIT_WEIGHT,
    params={
      "sensor_name": "feet_ground_contact",
      "period": 1.0 / walk_params.GAIT_FREQUENCY_DEFAULT,
      "command_name": "twist",
      "command_threshold": 0.05,
      "left_foot_name": "left_foot_link",
      "right_foot_name": "right_foot_link",
      "stance_fraction": _NUBOTS_SPEED_STANCE_FRACTION,
      "drop_step": int(1e12),
      "fade_steps": 0,
    },
  )


def booster_k1_nubots_speed_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Speed lineage: reach 2.0 m/s via cadence instead of trunk lean.

  Train from scratch, not by resuming Quality -- the objective differs too much
  for a warm start to be meaningful.

  The Quality lineage plateaus near 1.6 m/s for two reasons that reinforce each
  other. Physically it has one gear: cadence is stuck near 2.73 Hz regardless of
  the commanded frequency, so speed comes from longer strides and a forward lean
  that inclines the ground reaction force. That lean reaches 13.9 deg at
  1.34 m/s, past the 11.3 deg the 20 Nm ankle can hold against a 19.7 kg body
  with its centre of mass 0.53 m up, so the ankle saturates ~20% of the time and
  the trunk pitches forward monotonically into a fall. In reward terms the same
  speed range is where the objective goes net-negative and gets clamped flat, so
  there is no gradient with which to learn anything better.

  Hence the two changes: :func:`_apply_nubots_speed_budget` restores a gradient
  at speed, and :func:`_apply_nubots_cadence_tracking` makes cadence the lever
  for going faster. Commands open up to 2.0 m/s and 1.5 rad/s to match.
  """
  cfg = booster_k1_nubots_quality_env_cfg(play=play)

  _apply_nubots_speed_budget(cfg)
  _apply_nubots_cadence_tracking(cfg)

  twist = cfg.commands["twist"]
  assert isinstance(twist, UniformVelocityCommandCfg)
  twist.ranges.lin_vel_x = (-0.6, 2.0)
  twist.ranges.lin_vel_y = (-0.5, 0.5)
  twist.ranges.ang_vel_z = (-1.5, 1.5)
  twist.ranges.gait_frequency = _NUBOTS_SPEED_GAIT_FREQUENCY_RANGE
  return cfg


_HTWK_PARAMETER_WALK_RANGES = {
  "foot_yaw_l": (-0.7, 0.7),
  "foot_yaw_r": (-0.7, 0.7),
  "body_pitch": (-0.1, 0.3),
  "body_roll": (-0.1, 0.1),
  "feet_offset_x": (-0.15, 0.15),
  "feet_offset_y": (-0.08, 0.15),
}


def booster_k1_nubots_htwk_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Faithful HTWK/NuBots ParameterWalk reward setup.

  This is intentionally separate from the experimental Speed task. It keeps the
  NuBots 66-D observation / 16-D action interface while restoring the teacher's
  command-conditioned posture, foot-yaw, foot-offset, swing, shoulder, and
  curriculum terms. The target fields live in the command manager's 10-D
  command, so rewards and observations consume the same sampled values.
  """
  cfg = booster_k1_nubots_flat_env_cfg(play=play)

  action = cfg.actions["joint_pos"]
  assert isinstance(action, JointPositionActionCfg)
  action.scale = {name: _NUBOTS_LEG_ACTION_SCALE for name in _NUBOTS_ACTION_JOINTS}
  action.clip = None

  # The HTWK contact helper uses force history, matching the teacher's
  # max-over-history threshold instead of a single instantaneous contact bit.
  for sensor in cfg.scene.sensors or ():
    if sensor.name == "feet_ground_contact":
      assert isinstance(sensor, ContactSensorCfg)
      sensor.history_length = 4

  htwk_collision = ContactSensorCfg(
    name="htwk_collision",
    primary=ContactMatch(
      mode="body",
      pattern=r"^(Trunk|.*_Shank|.*_Arm_.*|Head_.*)$",
      entity="robot",
    ),
    secondary=ContactMatch(mode="body", pattern="terrain"),
    fields=("force",),
    reduce="netforce",
    num_slots=1,
    history_length=4,
  )
  foot_foot_collision = ContactSensorCfg(
    name="foot_foot_collision",
    primary=ContactMatch(
      mode="body",
      pattern=r"^left_foot_link$",
      entity="robot",
    ),
    secondary=ContactMatch(
      mode="body",
      pattern=r"^right_foot_link$",
      entity="robot",
    ),
    fields=("force",),
    reduce="netforce",
    num_slots=1,
    history_length=4,
  )
  cfg.scene.sensors = (cfg.scene.sensors or ()) + (
    htwk_collision,
    foot_foot_collision,
  )

  feet = SceneEntityCfg(
    "robot", body_names=("left_foot_link", "right_foot_link")
  )
  actuated = SceneEntityCfg(
    "robot",
    joint_names=_NUBOTS_ACTION_JOINTS,
    actuator_names=_NUBOTS_ACTION_JOINTS,
  )
  shoulders = SceneEntityCfg("robot", joint_names=_NUBOTS_SHOULDER_JOINTS)
  trunk = SceneEntityCfg("robot", body_names=("Trunk",))

  cfg.rewards = {
    "survival": RewardTermCfg(func=mdp.htwk_survival, weight=0.25),
    "tracking_lin_vel_x": RewardTermCfg(
      func=mdp.htwk_track_lin_vel_axis,
      weight=2.0,
      params={"axis": 0, "command_name": "twist", "sigma": 0.25},
    ),
    "tracking_lin_vel_y": RewardTermCfg(
      func=mdp.htwk_track_lin_vel_axis,
      weight=2.0,
      params={"axis": 1, "command_name": "twist", "sigma": 0.25},
    ),
    "tracking_ang_vel": RewardTermCfg(
      func=mdp.htwk_track_ang_vel_z,
      weight=1.5,
      params={"command_name": "twist", "sigma": 0.25},
    ),
    "base_height": RewardTermCfg(
      func=mdp.htwk_base_height,
      weight=-8.0,
      params={"target_height": 0.52, "asset_cfg": trunk},
    ),
    "orientation": RewardTermCfg(
      func=mdp.htwk_orientation_target,
      weight=-8.0,
      params={"command_name": "twist", "asset_cfg": trunk},
    ),
    "lin_vel_z": RewardTermCfg(
      func=mdp.htwk_lin_vel_z,
      weight=-2.0,
      params={"asset_cfg": trunk},
    ),
    "ang_vel_xy": RewardTermCfg(
      func=mdp.htwk_ang_vel_xy,
      weight=-0.2,
      params={"asset_cfg": trunk},
    ),
    "torques": RewardTermCfg(
      func=mdp.joint_torques_l2, weight=-3.0e-5, params={"asset_cfg": actuated}
    ),
    "torque_tiredness": RewardTermCfg(
      func=mdp.torque_tiredness,
      weight=-1.0e-3,
      params={"asset_cfg": actuated},
    ),
    "power": RewardTermCfg(
      func=mdp.joint_power_penalty,
      weight=-3.0e-4,
      params={"asset_cfg": actuated},
    ),
    "dof_vel": RewardTermCfg(
      func=mdp.joint_vel_l2, weight=-2.0e-5, params={"asset_cfg": actuated}
    ),
    "dof_acc": RewardTermCfg(
      func=mdp.joint_acc_l2, weight=-1.0e-7, params={"asset_cfg": actuated}
    ),
    "root_acc": RewardTermCfg(
      func=mdp.root_acc_l2, weight=-1.0e-5, params={"asset_cfg": trunk}
    ),
    "action_rate": RewardTermCfg(func=mdp.action_rate_l2, weight=-0.1),
    "dof_pos_limits": RewardTermCfg(
      func=mdp.htwk_joint_pos_limits, weight=-1.0, params={"asset_cfg": actuated}
    ),
    "collision": RewardTermCfg(
      func=mdp.htwk_collision,
      weight=-1.0,
      params={"sensor_name": "htwk_collision", "threshold": 1.0},
    ),
    "foot_foot_collision": RewardTermCfg(
      func=mdp.htwk_foot_foot_collision,
      weight=-2.0,
      params={"sensor_name": "foot_foot_collision", "threshold": 1.0},
    ),
    "feet_slip": RewardTermCfg(
      func=mdp.htwk_feet_slip,
      weight=-0.1,
      params={"sensor_name": "feet_ground_contact", "asset_cfg": feet},
    ),
    "feet_roll": RewardTermCfg(
      func=mdp.htwk_feet_orientation,
      weight=-0.2,
      params={"axis": 0, "asset_cfg": feet},
    ),
    "feet_pitch": RewardTermCfg(
      func=mdp.htwk_feet_orientation,
      weight=-0.1,
      params={"axis": 1, "asset_cfg": feet},
    ),
    "foot_yaw_l": RewardTermCfg(
      func=mdp.htwk_foot_yaw_l,
      weight=-1.0,
      params={"command_name": "twist", "asset_cfg": feet},
    ),
    "foot_yaw_r": RewardTermCfg(
      func=mdp.htwk_foot_yaw_r,
      weight=-1.0,
      params={"command_name": "twist", "asset_cfg": feet},
    ),
    "feet_yaw_diff": RewardTermCfg(
      func=mdp.htwk_feet_yaw_diff,
      weight=-0.5,
      params={"command_name": "twist", "asset_cfg": feet},
    ),
    "feet_yaw_mean": RewardTermCfg(
      func=mdp.htwk_feet_yaw_mean,
      weight=-0.5,
      params={"command_name": "twist", "asset_cfg": feet},
    ),
    "feet_offset_x": RewardTermCfg(
      func=mdp.htwk_feet_offset_x,
      weight=-12.0,
      params={"command_name": "twist", "max_vel": 1.0, "asset_cfg": feet},
    ),
    "feet_offset_y": RewardTermCfg(
      func=mdp.htwk_feet_offset_y,
      weight=-12.0,
      params={
        "command_name": "twist",
        "max_vel": 1.0,
        "feet_distance_ref": 0.18,
        "asset_cfg": feet,
      },
    ),
    "feet_minimum_separation": RewardTermCfg(
      func=mdp.htwk_feet_minimum_separation,
      weight=-2.0,
      params={
        "min_separation": 0.10,
        "asset_cfg": feet,
      },
    ),
    "feet_swing": RewardTermCfg(
      func=mdp.htwk_feet_swing,
      weight=3.0,
      params={
        "sensor_name": "feet_ground_contact",
        "period": 1.0 / walk_params.GAIT_FREQUENCY_DEFAULT,
        "swing_period": walk_params.SWING_PERIOD,
        "command_name": "twist",
        "threshold": 1.0,
      },
    ),
    "shoulder_deviation": RewardTermCfg(
      func=mdp.htwk_shoulder_deviation_l1,
      weight=-3.0,
      params={"asset_cfg": shoulders},
    ),
  }
  cfg.only_positive_rewards = True

  twist = cfg.commands["twist"]
  assert isinstance(twist, UniformVelocityCommandCfg)
  twist.ranges.lin_vel_x = (-1.0, 2.0)
  twist.ranges.lin_vel_y = (-1.0, 1.0)
  twist.ranges.ang_vel_z = (-1.6, 1.6)
  twist.ranges.gait_frequency = (1.5, 3.0)
  twist.parameter_walk_ranges = dict(_HTWK_PARAMETER_WALK_RANGES)
  twist.still_proportion = 0.1
  twist.rel_standing_envs = 0.0
  # HTWK samples uniform ranges; do not inherit the experimental Booster grid.
  if twist.grid_curriculum is not None:
    twist.grid_curriculum.enabled = False
  twist.vel_curriculum = True
  twist.init_vel_scale = 0.5
  twist.vel_scale_step = 2.0e-4
  twist.vel_scale_error_thresh = 0.4

  # The observation term consumes the 10-D command fields. Keep its fallback
  # ranges too, so it remains self-contained for legacy command restores.
  for group in ("actor", "critic"):
    pw = cfg.observations[group].terms["velocity_commands"]
    pw.params.update(
      {
        "period": 1.0 / walk_params.GAIT_FREQUENCY_DEFAULT,
        "foot_yaw_l_range": _HTWK_PARAMETER_WALK_RANGES["foot_yaw_l"],
        "foot_yaw_r_range": _HTWK_PARAMETER_WALK_RANGES["foot_yaw_r"],
        "body_pitch_range": _HTWK_PARAMETER_WALK_RANGES["body_pitch"],
        "body_roll_range": _HTWK_PARAMETER_WALK_RANGES["body_roll"],
        "feet_offset_x_range": _HTWK_PARAMETER_WALK_RANGES["feet_offset_x"],
        "feet_offset_y_range": _HTWK_PARAMETER_WALK_RANGES["feet_offset_y"],
      }
    )

  cfg.curriculum = {
    "velocity": CurriculumTermCfg(
      func=mdp.htwk_velocity_levels,
      params={"command_name": "twist"},
    ),
    "action_rate": CurriculumTermCfg(
      func=mdp.htwk_action_rate_curriculum,
      params={
        "command_name": "twist",
        "term_name": "action_rate",
        "start_weight": -0.1,
        "end_weight": -1.0,
        "error_thresh": 0.45,
        "step": 3.0e-4,
      },
    ),
    "shoulder_release": CurriculumTermCfg(
      func=mdp.htwk_shoulder_release,
      params={
        "term_name": "shoulder_deviation",
        "start_weight": -3.0,
        "end_weight": -0.1,
        "start_step": 60_000,
        "end_step": 200_000,
      },
    ),
  }
  return cfg


def booster_k1_nubots_htwk_unclipped_env_cfg(
  play: bool = False,
) -> ManagerBasedRlEnvCfg:
  """HTWK task variant that preserves signed rewards for fine-tuning."""
  cfg = booster_k1_nubots_htwk_env_cfg(play=play)
  cfg.only_positive_rewards = False
  return cfg


def booster_k1_nubots_htwk_exact_env_cfg(
  play: bool = False,
) -> ManagerBasedRlEnvCfg:
  """Reference HTWK task with the dedicated ParameterWalk command."""
  cfg = booster_k1_nubots_htwk_env_cfg(play=play)
  cfg.episode_length_s = int(1e9) if play else 30.0

  # HTWK startup domain randomization. MuJoCo exposes one tangential Coulomb
  # coefficient rather than separate static/dynamic coefficients, so the
  # reference static-friction range is used for the supported field.
  cfg.events["foot_friction"].params["ranges"] = (0.1, 2.0)

  # Use physically consistent mass/inertia variation for deployment realism.
  # The Trunk gets 0.8–1.2× mass; other links get a narrower 0.9–1.1× range,
  # replacing the inherited all-body 0.67–1.49× variation.
  cfg.events.pop("robot_inertia", None)
  cfg.events["trunk_inertia"] = EventTermCfg(
    mode="startup",
    func=dr.pseudo_inertia,
    params={
      "asset_cfg": SceneEntityCfg("robot", body_names=("Trunk",)),
      "alpha_range": _HTWK_EXACT_TRUNK_ALPHA_RANGE,
    },
  )
  cfg.events["other_link_inertia"] = EventTermCfg(
    mode="startup",
    func=dr.pseudo_inertia,
    params={
      "asset_cfg": SceneEntityCfg(
        "robot", body_names=("^(?!Trunk$).*",)
      ),
      "alpha_range": _HTWK_EXACT_OTHER_LINK_ALPHA_RANGE,
    },
  )

  # Match HTWK reset placement and its small initial forward/lateral velocity.
  cfg.events["reset_base"].params = {
    "pose_range": {
      "x": (-1.0, 1.0),
      "y": (-1.0, 1.0),
      "yaw": (-math.pi, math.pi),
    },
    "velocity_range": {
      "x": (0.0, 0.1),
      "y": (0.0, 0.1),
      "z": (0.0, 0.0),
      "roll": (0.0, 0.0),
      "pitch": (0.0, 0.0),
      "yaw": (0.0, 0.0),
    },
  }

  action = cfg.actions["joint_pos"]
  assert isinstance(action, JointPositionActionCfg)
  action.clip = {
    "Left_Shoulder_Roll": (
      -1.3 - _HTWK_EXACT_SHOULDER_ROLL_BAND,
      -1.3 + _HTWK_EXACT_SHOULDER_ROLL_BAND,
    ),
    "Right_Shoulder_Roll": (
      1.3 - _HTWK_EXACT_SHOULDER_ROLL_BAND,
      1.3 + _HTWK_EXACT_SHOULDER_ROLL_BAND,
    ),
  }
  cfg.commands["twist"] = ParameterWalkCommandCfg(
    entity_name="robot",
    resampling_time_range=(3.0, 8.0),
    still_proportion=0.1,
    debug_vis=False,
  )
  # Reference HTWK terminates only on timeout or low base height.
  cfg.terminations.pop("fell_over", None)
  cfg.terminations.pop("nan_state", None)
  root_height = cfg.terminations.pop("root_height", None)
  if root_height is not None:
    root_height.params["minimum_height"] = 0.35
    cfg.terminations["base_height"] = root_height

  if not play:
    # Reference HTWK uses a velocity push every five seconds.
    cfg.events.pop("kick_robot", None)
    cfg.events["push_robot"] = EventTermCfg(
      func=envs_mdp.push_by_setting_velocity,
      mode="interval",
      interval_range_s=(5.0, 5.0),
      params={
        "velocity_range": {
          "x": (-0.3, 0.3),
          "y": (-0.3, 0.3),
        },
      },
    )
    # Randomized episode-level external Trunk force/torque. The ranges mirror
    # the existing Booster disturbance magnitudes while targeting only Trunk.
    cfg.events["trunk_external_wrench"] = EventTermCfg(
      func=envs_mdp.apply_external_force_torque,
      mode="reset",
      params={
        "force_range": (-10.0, 10.0),
        "torque_range": (-2.0, 2.0),
        "asset_cfg": SceneEntityCfg("robot", body_names=("Trunk",)),
      },
    )

  # The reference has no observation latency; the compatible task retains
  # latency for the NuBots deployment lineage.
  for name in ("projected_gravity", "base_ang_vel", "joint_pos", "joint_vel"):
    term = cfg.observations["actor"].terms[name]
    term.delay_min_lag = 0
    term.delay_max_lag = 0
    term.delay_hold_prob = 0.0

  # The reference collision reward counts the current contact sample.
  for sensor in cfg.scene.sensors or ():
    if sensor.name == "htwk_collision":
      assert isinstance(sensor, ContactSensorCfg)
      sensor.history_length = 0
  cfg.rewards["collision"].func = mdp.htwk_collision_instant
  cfg.rewards["collision"].params = {
    "sensor_name": "htwk_collision",
    "threshold": 1.0,
  }
  cfg.rewards["root_acc"].func = mdp.htwk_root_acc
  cfg.rewards["torque_tiredness"].func = mdp.htwk_torque_tiredness
  cfg.only_positive_rewards = True
  return cfg


def booster_k1_nubots_htwk_robust_ft_env_cfg(
  play: bool = False,
) -> ManagerBasedRlEnvCfg:
  """Deployment-focused HTWK fine-tune with cadence, yaw, and terrain curricula."""
  cfg = booster_k1_nubots_htwk_exact_env_cfg(play=play)
  if not play:
    # Resample trunk force/torque every 4 s (exact HTWK holds one wrench/episode).
    cfg.events["trunk_external_wrench"] = EventTermCfg(
      func=envs_mdp.apply_external_force_torque,
      mode="interval",
      interval_range_s=(
        _NUBOTS_ROBUST_FT_TRUNK_WRENCH_INTERVAL_S,
        _NUBOTS_ROBUST_FT_TRUNK_WRENCH_INTERVAL_S,
      ),
      params={
        "force_range": (-10.0, 10.0),
        "torque_range": (-2.0, 2.0),
        "asset_cfg": SceneEntityCfg("robot", body_names=("Trunk",)),
      },
    )

  # Elbows are passive in the 16-D policy. Reset them near the center of the
  # requested 34–46° fold range, then randomize their held PD targets within
  # that range on each reset.
  elbow_fold_mid = sum(_NUBOTS_ELBOW_FOLD_RANGE) / 2.0
  folded_pose = dict(cfg.events["reset_robot_joints"].params["poses"][0])
  folded_pose.update(
    {
      "Left_Elbow_Pitch": elbow_fold_mid,
      "Right_Elbow_Pitch": elbow_fold_mid,
    }
  )
  cfg.events["reset_robot_joints"].params["poses"] = [folded_pose]
  cfg.events["fold_elbows"] = EventTermCfg(
    func=mdp.set_joint_position_targets_random,
    mode="reset",
    params={
      "position_range": _NUBOTS_ELBOW_FOLD_RANGE,
      "asset_cfg": SceneEntityCfg(
        "robot",
        joint_names=("Left_Elbow_Pitch", "Right_Elbow_Pitch"),
      ),
    },
  )

  knees = SceneEntityCfg(
    "robot", body_names=("Left_Shank", "Right_Shank")
  )
  feet = SceneEntityCfg("robot", body_names=("left_foot_link", "right_foot_link"))
  hip_roll = SceneEntityCfg("robot", joint_names=(".*_Hip_Roll",))
  foot_sites = SceneEntityCfg("robot", site_names=("left_foot", "right_foot"))
  # These barriers are intentionally only in the robust fine-tune variant.
  # The exact HTWK task remains unchanged for teacher compatibility.
  cfg.rewards["feet_offset_x"].params["min_velocity_scale"] = (
    _NUBOTS_ROBUST_FT_FOOT_OFFSET_MIN_VEL_SCALE
  )
  cfg.rewards["feet_offset_y"].params["min_velocity_scale"] = (
    _NUBOTS_ROBUST_FT_FOOT_OFFSET_MIN_VEL_SCALE
  )
  cfg.rewards["feet_minimum_separation"].weight = (
    _NUBOTS_ROBUST_FT_FEET_MIN_SEP_WEIGHT
  )
  cfg.rewards["feet_minimum_separation"].params["min_separation"] = (
    _NUBOTS_ROBUST_FT_MIN_FEET_SEPARATION
  )
  cfg.rewards["foot_foot_collision"].weight = (
    _NUBOTS_ROBUST_FT_FOOT_FOOT_COLLISION_WEIGHT
  )
  cfg.rewards["feet_site_xy_separation"] = RewardTermCfg(
    func=mdp.htwk_feet_site_xy_separation,
    weight=_NUBOTS_ROBUST_FT_FEET_SITE_XY_WEIGHT,
    params={
      "min_separation": _NUBOTS_ROBUST_FT_MIN_FEET_SITE_XY,
      "asset_cfg": foot_sites,
    },
  )
  cfg.rewards["knee_separation"] = RewardTermCfg(
    func=mdp.htwk_knee_separation,
    weight=_NUBOTS_ROBUST_FT_KNEE_SEPARATION_WEIGHT,
    params={
      "safe_distance": _NUBOTS_ROBUST_FT_KNEE_SAFE_DISTANCE,
      "softness": 0.01,
      "asset_cfg": knees,
    },
  )
  cfg.rewards["hip_roll_barrier"] = RewardTermCfg(
    func=mdp.htwk_hip_roll_barrier,
    weight=-4.0,
    params={
      "max_deviation": _NUBOTS_ROBUST_FT_HIP_ROLL_MAX_DEVIATION,
      "softness": 0.02,
      "asset_cfg": hip_roll,
    },
  )
  # Allow ankle dorsiflex during swing; flat-foot penalty only when planted.
  for orient_name, axis in (("feet_roll", 0), ("feet_pitch", 1)):
    term = cfg.rewards[orient_name]
    term.func = mdp.htwk_feet_orientation_contact_gated
    term.params = {
      "axis": axis,
      "sensor_name": "feet_ground_contact",
      "threshold": 1.0,
      "asset_cfg": feet,
    }
  cfg.rewards["swing_sole_clearance"] = RewardTermCfg(
    func=mdp.htwk_swing_sole_clearance,
    weight=_NUBOTS_ROBUST_FT_SWING_SOLE_CLEARANCE_WEIGHT,
    params={
      "height_sensor_name": "foot_height_scan",
      "sensor_name": "feet_ground_contact",
      "period": 1.0 / walk_params.GAIT_FREQUENCY_DEFAULT,
      "swing_period": walk_params.SWING_PERIOD,
      "command_name": "twist",
      "min_clearance": _NUBOTS_ROBUST_FT_SWING_MIN_CLEARANCE,
      "target_clearance": _NUBOTS_ROBUST_FT_SWING_TARGET_CLEARANCE,
      "threshold": 1.0,
    },
  )

  _apply_nubots_arm_swing_unlock(cfg)
  cfg.rewards["shoulder_deviation"].weight = _NUBOTS_ROBUST_FT_SHOULDER_DEV_START
  shoulder_release = cfg.curriculum.get("shoulder_release")
  if shoulder_release is not None:
    shoulder_release.params["start_weight"] = _NUBOTS_ROBUST_FT_SHOULDER_DEV_START
    shoulder_release.params["end_weight"] = _NUBOTS_ROBUST_FT_SHOULDER_DEV_END

  # Keep the 66-D actor unchanged: terrain is privileged critic information.
  rough_cfg = booster_k1_rough_env_cfg(play=play)
  assert cfg.scene.terrain is not None
  assert rough_cfg.scene.terrain is not None
  assert rough_cfg.scene.terrain.terrain_generator is not None
  cfg.scene.terrain.terrain_type = "generator"
  cfg.scene.terrain.terrain_generator = rough_cfg.scene.terrain.terrain_generator
  terrain_generator = cfg.scene.terrain.terrain_generator
  terrain_generator.curriculum = False
  terrain_generator.sub_terrains = {
    "flat": flat(proportion=0.80),
    "random_rough": random_rough(proportion=0.10),
    "wave_terrain": wave_terrain(proportion=0.10),
  }

  terrain_scan = next(
    sensor for sensor in (rough_cfg.scene.sensors or ())
    if sensor.name == "terrain_scan"
  )
  cfg.scene.sensors = (cfg.scene.sensors or ()) + (terrain_scan,)
  cfg.observations["critic"].terms["base_height"].params["sensor_name"] = (
    "terrain_scan"
  )
  cfg.rewards["base_height"] = RewardTermCfg(
    func=mdp.base_height_target_l2,
    weight=-8.0,
    params={
      "target_height": 0.52,
      "sensor_name": "terrain_scan",
      "asset_cfg": SceneEntityCfg("robot", body_names=("Trunk",)),
    },
  )
  cfg.terminations["base_height"].params["sensor_name"] = "terrain_scan"

  command = cfg.commands["twist"]
  assert isinstance(command, ParameterWalkCommandCfg)
  command.ranges.lin_vel_x = (-1.5, 2.0)
  command.ranges.lin_vel_y = (-1.3, 1.3)
  command.ranges.ang_vel_yaw = (-1.5, 1.5)
  command.ranges.gait_frequency = (1.5, 3.0)
  # The forward-speed oversampler must operate on physical commands, not the
  # exact task's startup velocity scale.
  command.vel_curriculum = False
  command.init_vel_scale = 1.0
  command.yaw_curriculum = True
  command.init_yaw_scale = 0.4 / 1.5
  command.yaw_scale_step = 1.0e-4
  command.yaw_scale_error_thresh = 0.3
  command.high_speed_oversample = True
  command.high_speed_sampling_probability = 0.5
  command.high_speed_gait_bias = True
  command.high_speed_gait_probability = 0.7
  command.high_speed_gait_frequency_range = (2.5, 3.0)

  if play:
    # Keep the feet visibly separated during interactive playback while
    # staying within the range seen during training.
    command.ranges.feet_offset_y_target = (0.05, 0.05)
    cfg.curriculum = {}
  else:
    cfg.curriculum["yaw"] = CurriculumTermCfg(
      func=mdp.htwk_yaw_levels,
      params={"command_name": "twist"},
    )
    cfg.curriculum["terrain_mix"] = CurriculumTermCfg(
      func=mdp.scheduled_terrain_mix_curriculum,
      params={
        "steps_per_iteration": 24,
        "stages": [
          # Start the robust fine-tune with the requested terrain mix.
          {"iteration": 0, "proportions": [0.8, 0.1, 0.1]},
          {"iteration": 20_000, "proportions": [0.8, 0.1, 0.1]},
          {"iteration": 40_000, "proportions": [0.7, 0.15, 0.15]},
        ],
      },
    )
  return cfg

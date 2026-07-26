"""Booster K1 velocity environment configurations."""

from mjlab.asset_zoo.robots import (
  K1_ACTION_SCALE,
  get_k1_robot_cfg,
)
from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.envs import mdp as envs_mdp
from mjlab.envs.mdp import dr
from mjlab.envs.mdp.actions import JointPositionActionCfg
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
from mjlab.tasks.velocity.mdp import UniformVelocityCommandCfg
from mjlab.tasks.velocity.velocity_env_cfg import make_velocity_env_cfg

# Legs only: head/arms stay at the tucked keyframe via PD (see k1_constants).
_K1_LEG_ACTUATORS = (
  ".*_Hip_Pitch",
  ".*_Hip_Roll",
  ".*_Hip_Yaw",
  ".*_Knee_Pitch",
  ".*_Ankle_Pitch",
  ".*_Ankle_Roll",
)

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
    cfg.scene.terrain.terrain_generator.curriculum = True

  joint_pos_action = cfg.actions["joint_pos"]
  assert isinstance(joint_pos_action, JointPositionActionCfg)
  joint_pos_action.actuator_names = _K1_LEG_ACTUATORS
  # Scale dict must only include keys that match the restricted action joints.
  joint_pos_action.scale = {name: K1_ACTION_SCALE[name] for name in _K1_LEG_ACTUATORS}

  cfg.viewer.body_name = "Trunk"

  twist_cmd = cfg.commands["twist"]
  assert isinstance(twist_cmd, UniformVelocityCommandCfg)
  twist_cmd.viz.z_offset = 0.7

  cfg.events["foot_friction"].params["asset_cfg"].geom_names = geom_names
  cfg.events["base_com"].params["asset_cfg"].body_names = ("Trunk",)

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

  # Open-loop gait clock for early training; fades to zeros after ~8k iters
  # (keep dim fixed so the network can run without the clock later).
  gait_cycle_cfg = ObservationTermCfg(
    func=mdp.gait_cycle,
    params={
      "period": 0.6,
      "command_name": "twist",
      "command_threshold": 0.05,
      "drop_step": 8_000 * 24,
      "fade_steps": 2_000 * 24,
    },
  )
  cfg.observations["actor"].terms["gait_cycle"] = gait_cycle_cfg
  cfg.observations["critic"].terms["gait_cycle"] = gait_cycle_cfg

  # Pose stds: keep hip roll/yaw tight so the policy cannot sit in a wide
  # stance (exp pose saturates once spread, so tightness matters early).
  cfg.rewards["pose"].params["std_standing"] = {".*": 0.05}
  cfg.rewards["pose"].params["std_walking"] = {
    r".*_Hip_Pitch": 0.3,
    r".*_Hip_Roll": 0.1,
    r".*_Hip_Yaw": 0.1,
    r".*_Knee_Pitch": 0.35,
    r".*_Ankle_Pitch": 0.25,
    r".*_Ankle_Roll": 0.1,
    r".*_Shoulder_Pitch": 0.05,
    r".*_Shoulder_Roll": 0.05,
    r".*_Elbow_Pitch": 0.05,
    r".*_Elbow_Yaw": 0.05,
    r"Head_.*": 0.05,
  }
  cfg.rewards["pose"].params["std_running"] = {
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

  cfg.rewards["upright"].params["asset_cfg"].body_names = ("Trunk",)
  cfg.rewards["body_ang_vel"].params["asset_cfg"].body_names = ("Trunk",)

  for reward_name in ["foot_clearance", "foot_slip"]:
    cfg.rewards[reward_name].params["asset_cfg"].site_names = site_names

  cfg.rewards["body_ang_vel"].weight = -0.05
  cfg.rewards["angular_momentum"].weight = -0.02
  cfg.rewards["air_time"].weight = 0.0

  # Non-saturating penalty on hip abduction/adduction (wide stance).
  cfg.rewards["hip_roll_l2"] = RewardTermCfg(
    func=mdp.joint_deviation_l2,
    weight=-1.0,
    params={
      "asset_cfg": SceneEntityCfg("robot", joint_names=(".*_Hip_Roll",)),
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
    # Play/deploy: keep the 2-D slot but always emit zeros (final-policy mode).
    for group in ("actor", "critic"):
      gait_term = cfg.observations[group].terms.get("gait_cycle")
      if gait_term is not None:
        gait_term.params["drop_step"] = 0
        gait_term.params["fade_steps"] = 0
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

  cfg.sim.njmax = 300
  cfg.sim.mujoco.ccd_iterations = 50
  cfg.sim.contact_sensor_maxmatch = 64
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

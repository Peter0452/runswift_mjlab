"""Booster K1 AMP velocity tracking environment configurations."""

import mujoco

from mjlab.asset_zoo.props.ball import BALL_XML, get_ball_radius
from mjlab.asset_zoo.robots.booster_k1.k1_whirlwind_constants import (
  K1_ACTION_SCALE,
  get_k1_whirlwind_robot_cfg,
)
from mjlab.asset_zoo.robots.booster_k1.whirlwind_sensors import (
  FootClearanceSensorCfg,
  FootSoleGridPatternCfg,
)
from mjlab.entity import EntityCfg
from mjlab.envs import ManagerBasedRlEnvCfg
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
)
from mjlab.tasks.velocity import mdp
from mjlab.tasks.velocity.velocity_amp_env_cfg import make_velocity_env_cfg
from mjlab.terrains.config import flat, random_rough, wave_terrain

# Rough FT terrain mix (flat / random_rough / wave).
_AMP_ROUGH_FT_MIX = (0.80, 0.10, 0.10)
# Early FT: hold mid speeds until tracking recovers (~4k iters @ 24 steps/iter).
_AMP_EARLY_VEL = {
  "lin_vel_x": (-1.25, 1.5),
  "lin_vel_y": (-1.5, 1.5),
  "ang_vel_z": (-1.25, 1.25),
}
# After widen (matches prior max FT ranges).
_AMP_MAX_VEL = {
  "lin_vel_x": (-1.75, 2.0),
  "lin_vel_y": (-1.8, 1.8),
  "ang_vel_z": (-1.6, 1.6),
}
# PPO iters → env steps (num_steps_per_env=24).
_AMP_VEL_WIDEN_STEP = 4000 * 24
# Kick-handoff FT only: one more widen after the rough-walk ranges.
_HANDOFF_VEL_WIDEN_STEP = 8000 * 24
_HANDOFF_LATE_VEL = {
  "lin_vel_x": (-2.0, 2.5),
  "lin_vel_y": (-2.0, 2.0),
  "ang_vel_z": (-1.8, 1.8),
}


def _apply_amp_rough_ft_terrain(cfg: ManagerBasedRlEnvCfg) -> None:
  """Fixed 80/10/10 flat/rough/wave; no terrain-level curriculum."""
  assert cfg.scene.terrain is not None
  assert cfg.scene.terrain.terrain_generator is not None
  terrain_generator = cfg.scene.terrain.terrain_generator
  terrain_generator.curriculum = False
  flat_p, rough_p, wave_p = _AMP_ROUGH_FT_MIX
  terrain_generator.sub_terrains = {
    "flat": flat(proportion=flat_p),
    "random_rough": random_rough(proportion=rough_p),
    "wave_terrain": wave_terrain(proportion=wave_p),
  }
  if cfg.curriculum is not None:
    cfg.curriculum.pop("terrain_levels", None)


def _apply_amp_max_vel_curriculum(cfg: ManagerBasedRlEnvCfg) -> None:
  """Start at vx≤1.5, widen to full FT ranges after ``_AMP_VEL_WIDEN_STEP``."""
  assert cfg.commands is not None
  twist_cmd = cfg.commands["twist"]
  assert isinstance(twist_cmd, mdp.UniformVelocityCommandCfg)
  twist_cmd.ranges.lin_vel_x = _AMP_EARLY_VEL["lin_vel_x"]
  twist_cmd.ranges.lin_vel_y = _AMP_EARLY_VEL["lin_vel_y"]
  twist_cmd.ranges.ang_vel_z = _AMP_EARLY_VEL["ang_vel_z"]

  assert cfg.curriculum is not None
  cfg.curriculum["command_vel"] = CurriculumTermCfg(
    func=mdp.commands_vel,
    params={
      "command_name": "twist",
      "velocity_stages": [
        {"step": 0, **_AMP_EARLY_VEL},
        {"step": _AMP_VEL_WIDEN_STEP, **_AMP_MAX_VEL},
      ],
    },
  )


def booster_k1_amp_rough_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Create Booster K1 rough-terrain AMP velocity tracking configuration."""
  cfg = make_velocity_env_cfg()

  cfg.scene.entities = {"robot": get_k1_whirlwind_robot_cfg()}

  site_names = ("left_foot", "right_foot")
  sole_site_names = ("left_foot_sole", "right_foot_sole")
  geom_names = ("left_foot_collision", "right_foot_collision")
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
  nonfoot_ground_cfg = ContactSensorCfg(
    name="non_foot_ground_contact",
    primary=ContactMatch(
      mode="body",
      entity="robot",
      pattern=r".*",
      exclude=("left_foot_link", "right_foot_link"),
    ),
    secondary=ContactMatch(mode="body", pattern="terrain"),
    fields=("found", "force"),
    reduce="netforce",
    num_slots=1,
  )
  self_collision_cfg = ContactSensorCfg(
    name="self_collision",
    primary=ContactMatch(mode="subtree", pattern="Trunk", entity="robot"),
    secondary=ContactMatch(mode="subtree", pattern="Trunk", entity="robot"),
    fields=("found",),
    reduce="none",
    num_slots=1,
  )

  foot_height_scan = FootClearanceSensorCfg(
    name="foot_height_scan",
    frame=tuple(ObjRef(type="site", name=s, entity="robot") for s in sole_site_names),
    pattern=FootSoleGridPatternCfg(),
    ray_alignment="yaw",
    max_distance=1.0,
    exclude_parent_body=True,
    include_geom_groups=(0,),
    debug_vis=True,
    viz=FootClearanceSensorCfg.VizCfg(
      show_rays=True,
      hit_color=(1.0, 0.0, 1.0, 0.8),
      hit_sphere_color=(1.0, 0.0, 1.0, 1.0),
    ),
  )
  cfg.scene.sensors = (
    feet_ground_cfg,
    nonfoot_ground_cfg,
    self_collision_cfg,
    foot_height_scan,
  )

  if cfg.scene.terrain is not None and cfg.scene.terrain.terrain_generator is not None:
    cfg.scene.terrain.terrain_generator.curriculum = True

  joint_pos_action = cfg.actions["joint_pos"]
  assert isinstance(joint_pos_action, JointPositionActionCfg)
  joint_pos_action.scale = K1_ACTION_SCALE

  cfg.viewer.body_name = "Trunk"

  assert cfg.commands is not None
  twist_cmd = cfg.commands["twist"]
  assert isinstance(twist_cmd, mdp.UniformVelocityCommandCfg)
  twist_cmd.rel_standing_envs = 0.2
  twist_cmd.viz.z_offset = 1.15

  cfg.events["foot_friction"].params["asset_cfg"].geom_names = geom_names
  cfg.events["trunk_inertia"].params["asset_cfg"].body_names = ("Trunk",)
  cfg.events["limb_inertia"].params["asset_cfg"].body_names = (r"(?!Trunk$).*",)

  cfg.rewards["upright"].params["asset_cfg"].body_names = ("Trunk",)
  cfg.rewards["body_ang_vel"].params["asset_cfg"].body_names = ("Trunk",)

  for reward_name in ["foot_clearance", "foot_slip"]:
    cfg.rewards[reward_name].params["asset_cfg"].site_names = site_names

  for metric_cfg in cfg.metrics.values():
    if "asset_cfg" in metric_cfg.params:
      metric_cfg.params["asset_cfg"].site_names = site_names

  assert cfg.curriculum is not None
  assert "command_vel" in cfg.curriculum

  # Reset NaN/Inf physics envs instead of letting check_nan kill the whole run.
  cfg.terminations["nan_state"] = TerminationTermCfg(func=mdp.nan_detection)

  if play:
    cfg.episode_length_s = int(1e9)
    cfg.observations["actor"].enable_corruption = False
    cfg.terminations.pop("illegal_contact", None)

    if cfg.scene.terrain is not None:
      if cfg.scene.terrain.terrain_generator is not None:
        cfg.scene.terrain.terrain_generator.num_cols = 5
        cfg.scene.terrain.terrain_generator.num_rows = 5
        cfg.scene.terrain.terrain_generator.border_width = 10.0
        _apply_amp_rough_ft_terrain(cfg)

  return cfg


def booster_k1_amp_rough_ft_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """AMP rough fine-tune: 80/10/10 flat/rough/wave, velocity curriculum at max."""
  cfg = booster_k1_amp_rough_env_cfg(play=play)
  _apply_amp_rough_ft_terrain(cfg)
  _apply_amp_max_vel_curriculum(cfg)
  # Stronger tracking for rough FT (base AMP is 2.25 / 2.0).
  cfg.rewards["track_linear_velocity"].weight = 3.0
  cfg.rewards["track_angular_velocity"].weight = 2.5
  return cfg


def booster_k1_amp_kick_handoff_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Rough-walk fine-tune. 35% of resets are a live kick, then a small command.

  The other resets stay on the AMP motion pool, so the gait keeps training.
  After a kick the command is a stand or a twist inside ±0.5, until the
  normal resampler replaces it.
  """
  cfg = booster_k1_amp_rough_ft_env_cfg(play=play)
  assert cfg.curriculum is not None
  stages = cfg.curriculum["command_vel"].params["velocity_stages"]
  stages.append({"step": _HANDOFF_VEL_WIDEN_STEP, **_HANDOFF_LATE_VEL})
  cfg.events["kick_handoff"] = EventTermCfg(
    func=mdp.kick_handoff_reset,
    mode="post_reset",
    params={
      "fraction": 0.0 if play else 0.35,
      "stand_prob": 0.5,
      "cmd_limit": 0.5,
      "batch_size": 32,
      "kick_checkpoints": tuple(str(path) for path in mdp.DEFAULT_KICK_CKPTS),
    },
  )
  return cfg


# Flat walk command curriculum, with the final forward cap raised to 2.0.
_KICK_STAGE1_VEL_STAGES = (
  {
    "step": 0,
    "lin_vel_x": (-1.0, 1.2),
    "lin_vel_y": (-1.0, 1.0),
    "ang_vel_z": (-1.0, 1.0),
  },
  {
    "step": 5000 * 24,
    "lin_vel_x": (-1.0, 1.5),
    "lin_vel_y": (-1.25, 1.25),
    "ang_vel_z": (-1.25, 1.25),
  },
  {
    "step": 10000 * 24,
    "lin_vel_x": (-1.25, 1.5),
    "lin_vel_y": (-1.5, 1.5),
    "ang_vel_z": (-1.5, 1.5),
  },
  {
    "step": 15000 * 24,
    "lin_vel_x": (-1.5, 2.0),
    "lin_vel_y": (-1.75, 1.75),
    "ang_vel_z": (-1.5, 1.5),
  },
)
_KICK_STAGE1_CRITIC_TAIL = (
  "base_lin_vel",
  "foot_height",
  "foot_air_time",
  "foot_contact",
  "foot_contact_forces",
)


def _append_kick_stage1_command_slots(cfg: ManagerBasedRlEnvCfg) -> None:
  """Append speed limit, kick direction, and kick range. All zeros in stage 1."""
  for group in ("actor", "critic"):
    terms = cfg.observations[group].terms
    terms["speed_limit"] = ObservationTermCfg(
      func=mdp.constant_zeros, params={"dim": 3}
    )
    terms["kick_direction"] = ObservationTermCfg(
      func=mdp.constant_zeros, params={"dim": 2}
    )
    terms["kick_range"] = ObservationTermCfg(
      func=mdp.constant_zeros, params={"dim": 3}
    )
    if group == "critic":
      for key in _KICK_STAGE1_CRITIC_TAIL:
        terms[key] = terms.pop(key)


def booster_k1_kick_stage1_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Flat DA-Muon walk with the rough fine-tune ground and zero kick slots.

  Command curriculum matches the flat walk except the last forward cap is 2.0.
  """
  cfg = booster_k1_amp_rough_env_cfg(play=play)
  _apply_amp_rough_ft_terrain(cfg)
  assert cfg.curriculum is not None
  cfg.curriculum["command_vel"].params["velocity_stages"] = [
    dict(stage) for stage in _KICK_STAGE1_VEL_STAGES
  ]
  _append_kick_stage1_command_slots(cfg)
  if play:
    commands = cfg.commands
    assert commands is not None
    twist_cmd = commands["twist"]
    assert isinstance(twist_cmd, mdp.UniformVelocityCommandCfg)
    twist_cmd.ranges.lin_vel_x = (-2.5, 2.5)
    twist_cmd.ranges.lin_vel_y = (-2.0, 2.0)
    twist_cmd.ranges.ang_vel_z = (-3.7, 3.7)
  return cfg


_APPROACH_BALL_RADIUS = 0.08
_APPROACH_BALL_MASS = 0.1
_APPROACH_BALL_FRICTION = (1.0, 0.5, 0.015)


def _get_approach_ball_spec() -> mujoco.MjSpec:
  """Size-5 mesh scaled to the 0.08 m kick ball."""
  spec = mujoco.MjSpec.from_file(str(BALL_XML))
  scale = _APPROACH_BALL_RADIUS / get_ball_radius(5)
  for mesh in spec.meshes:
    mesh.scale = (scale, scale, scale)
  ball_body = spec.worldbody.bodies[0]
  for geom in ball_body.geoms:
    if geom.name.startswith("ball_visual"):
      geom.mass = 0.0
      geom.density = 0.0
      geom.friction = _APPROACH_BALL_FRICTION
    elif geom.name == "ball_collision":
      geom.group = 3
      geom.size = (_APPROACH_BALL_RADIUS, 0, 0)
      geom.typeinertia = mujoco.mjtGeomInertia.mjINERTIA_SHELL
      geom.priority = 1
      geom.condim = 6
      geom.mass = _APPROACH_BALL_MASS
      geom.solref = (0.05, 0.15)
      geom.friction = _APPROACH_BALL_FRICTION
  return spec


def _configure_approach_observations(cfg: ManagerBasedRlEnvCfg) -> None:
  """Replace the zero kick slots. Critic speed-limit carries the true ball."""
  for group, privileged in (("actor", False), ("critic", True)):
    terms = cfg.observations[group].terms
    terms["command"] = ObservationTermCfg(func=mdp.approach_command_obs)
    terms["speed_limit"] = ObservationTermCfg(
      func=mdp.approach_speed_limit_obs,
      params={"privileged": privileged},
    )
    terms["kick_direction"] = ObservationTermCfg(func=mdp.approach_kick_direction_obs)
    terms["kick_range"] = ObservationTermCfg(func=mdp.approach_kick_range_obs)


def _free_head_posture(cfg: ManagerBasedRlEnvCfg) -> None:
  """Drop the head from the upper-body pose penalty so it can hold the ball in view."""
  posture = cfg.rewards["upper_body_posture"]
  posture.params["asset_cfg"] = SceneEntityCfg(
    "robot",
    joint_names=(r".*_Shoulder_.*", r".*_Elbow_.*"),
  )
  for regime in ("std_standing", "std_walking", "std_running"):
    posture.params[regime] = {
      pattern: value
      for pattern, value in posture.params[regime].items()
      if "Head" not in pattern
    }


def booster_k1_kick_approach_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Stage-1 walk resumed into the approach task.

  Linear velocity tracking is off. The yaw channel is still tracked. A hidden
  walk-speed flag keeps the gait terms active until the robot is standing in
  the wedge.
  """
  cfg = booster_k1_kick_stage1_env_cfg(play=play)
  assert cfg.commands is not None
  assert cfg.curriculum is not None
  cfg.curriculum.pop("command_vel", None)
  cfg.commands["twist"] = mdp.ApproachYawCommandCfg()
  cfg.scene.entities["ball"] = EntityCfg(spec_fn=_get_approach_ball_spec)
  cfg.scene.sensors = tuple(cfg.scene.sensors) + (
    ContactSensorCfg(
      name="feet_ball_contact",
      primary=ContactMatch(
        mode="body",
        pattern=("left_foot_link", "right_foot_link"),
        entity="robot",
      ),
      secondary=ContactMatch(mode="body", pattern="ball", entity="ball"),
      fields=("found",),
      reduce="none",
      num_slots=1,
    ),
  )
  _configure_approach_observations(cfg)
  _free_head_posture(cfg)

  cfg.rewards["track_linear_velocity"].weight = 0.0
  cfg.rewards["approach_align"] = RewardTermCfg(func=mdp.approach_align, weight=80.0)
  cfg.rewards["approach_close"] = RewardTermCfg(func=mdp.approach_close, weight=100.0)
  cfg.rewards["approach_stand"] = RewardTermCfg(func=mdp.approach_stand, weight=2.0)
  cfg.rewards["approach_bad_contact"] = RewardTermCfg(
    func=mdp.approach_bad_contact, weight=-20.0
  )
  cfg.rewards["approach_view"] = RewardTermCfg(func=mdp.approach_view, weight=0.5)
  return cfg


def booster_k1_amp_flat_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Create Booster K1 flat-terrain AMP velocity tracking configuration."""
  cfg = booster_k1_amp_rough_env_cfg(play=play)

  cfg.sim.njmax = 300
  cfg.sim.mujoco.ccd_iterations = 60
  cfg.sim.contact_sensor_maxmatch = 64
  cfg.sim.nconmax = 50

  assert cfg.scene.terrain is not None
  cfg.scene.terrain.terrain_type = "plane"
  cfg.scene.terrain.terrain_generator = None

  assert cfg.curriculum is not None
  cfg.curriculum.pop("terrain_levels", None)

  if play:
    commands = cfg.commands
    assert commands is not None
    twist_cmd = commands["twist"]
    assert isinstance(twist_cmd, mdp.UniformVelocityCommandCfg)
    twist_cmd.ranges.lin_vel_x = (-2.5, 2.5)
    twist_cmd.ranges.lin_vel_y = (-2.0, 2.0)
    twist_cmd.ranges.ang_vel_z = (-3.7, 3.7)

  return cfg

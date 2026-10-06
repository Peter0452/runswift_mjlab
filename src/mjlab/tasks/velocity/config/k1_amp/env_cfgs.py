"""Booster K1 AMP velocity tracking environment configurations."""

import json
import os
from pathlib import Path

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
from mjlab.terrains.terrain_generator import TerrainGeneratorCfg

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

  # Reset NaN/Inf or blown-up envs instead of letting check_nan kill the run,
  # and zero their step reward so one diverged sim cannot wreck the critic.
  cfg.terminations["nan_state"] = TerminationTermCfg(
    func=mdp.physics_blowup, params={"max_qvel": 200.0}, invalid_state=True
  )

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
    terms["kick_range"] = ObservationTermCfg(func=mdp.constant_zeros, params={"dim": 3})
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
  """Replace the zero kick slots. The critic's command carries the true ball."""
  for group, privileged in (("actor", False), ("critic", True)):
    terms = cfg.observations[group].terms
    terms["command"] = ObservationTermCfg(
      func=mdp.approach_command_obs,
      params={"privileged": privileged},
    )
    terms["speed_limit"] = ObservationTermCfg(func=mdp.approach_speed_limit_obs)
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

  Velocity tracking is off; the policy picks its own path under per-episode
  speed limits. A hidden walk-speed flag keeps the gait terms active until the
  robot is lined up in the wedge.
  """
  cfg = booster_k1_kick_stage1_env_cfg(play=play)
  assert cfg.commands is not None
  assert cfg.curriculum is not None
  cfg.curriculum.pop("command_vel", None)
  # Play draws the target, kick line and camera FOV.
  cfg.commands["twist"] = mdp.ApproachYawCommandCfg(debug_vis=play)
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
  cfg.rewards["track_angular_velocity"].weight = 0.0
  cfg.rewards["approach_align"] = RewardTermCfg(func=mdp.approach_align, weight=80.0)
  cfg.rewards["approach_close"] = RewardTermCfg(func=mdp.approach_close, weight=100.0)
  cfg.rewards["approach_stand"] = RewardTermCfg(func=mdp.approach_stand, weight=2.0)
  cfg.rewards["approach_bad_contact"] = RewardTermCfg(
    func=mdp.approach_bad_contact, weight=-20.0
  )
  cfg.rewards["approach_view"] = RewardTermCfg(func=mdp.approach_view, weight=0.5)
  # Line the body up on the way in (≤1.5 m, in the wedge), not at the ball.
  cfg.rewards["approach_heading"] = RewardTermCfg(
    func=mdp.approach_heading, weight=50.0
  )
  # Extra speed earns at most ~2 (close) to ~3 (align near the ball) per m/s.
  cfg.rewards["approach_speed_limit"] = RewardTermCfg(
    func=mdp.approach_speed_limit, weight=-10.0
  )
  return cfg


# AMP style weight for the kick stage, applied at registration after the AMP
# wrapper. 0.15 in v12b–v16; v14 (style 0) showed the drift is not caused by
# the discriminator, while less style let the posture degrade (trunk tilt
# ~15° vs 3.5° for the walker), so v17 is back at the walk's 0.3.
# Evolutionary search (scripts/tools/evolve_kick.py): per-run "genes" as JSON
# in KICK_GENES — reward weights ("w.<term>"), RSI shares ("rsi_bhuman",
# "rsi_ours"), the AMP style weight ("style_w") and kick_loop constants
# ("k.<NAME>", applied in mdp/kick_loop.py). Empty outside the search.
KICK_GENES: dict = json.loads(os.environ.get("KICK_GENES", "{}") or "{}")
KICK_STYLE_WEIGHT = float(KICK_GENES.get("style_w", 0.3))
# v29 tried 0.45 with the walking-pose terms (the AMP mix is (1 − w)·task +
# w·style, so it also cut the kick rewards by 21 %): the gait improved but kick
# quality fell 0.84 → 0.78. From v30 the pose terms hold the gait at 0.3.


K1_CAMERA_HALF_FOV = (1.211259 / 2.0, 0.733038 / 2.0)


def booster_k1_kick_stage3_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Stage 3: approach, kick, recover and repeat, warm-started from stage 2.

  Same actor layout as the approach stage. A flat plane keeps ball physics
  predictable. Targets are 1–10 m away in short/medium/long bins; reaching
  one places the next. Rewards follow the kick reward list: ball vision, kick
  direction alignment, walk speed and its limit, kick direction, kick
  velocity and its accuracy, ball avoidance and single-foot avoidance.
  """
  cfg = booster_k1_kick_approach_env_cfg(play=play)
  if not play:
    cfg.episode_length_s = 30.0
  assert cfg.scene.terrain is not None
  # v48: field-like surface instead of a perfect plane: 60 % flat, 40 % gentle
  # bumps (heights 0–2 cm, 5 mm steps, 0.2 m between samples) on large patches
  # so 8–20 m kicks stay on the field. Play keeps the flat plane.
  if play:
    cfg.scene.terrain.terrain_type = "plane"
    cfg.scene.terrain.terrain_generator = None
  else:
    cfg.scene.terrain.terrain_type = "generator"
    cfg.scene.terrain.terrain_generator = TerrainGeneratorCfg(
      size=(16.0, 16.0),
      num_rows=6,
      num_cols=6,
      border_width=10.0,
      curriculum=False,
      sub_terrains={
        "flat": flat(proportion=0.6),
        "bumpy": random_rough(
          proportion=0.4,
          noise_range=(0.0, 0.02),
          noise_step=0.005,
          downsampled_scale=0.2,
          border_width=0.25,
        ),
      },
    )
  # v48c: foot friction 0.75–1.25 → 0.7–1.4. v48/v48b used 0.5–1.4 and the
  # policy became cautious (goals 1.2 → 0.95 per episode, on flat too).
  cfg.events["foot_friction"].params["ranges"] = (0.7, 1.4)
  assert cfg.curriculum is not None
  cfg.curriculum.pop("terrain_levels", None)

  assert cfg.commands is not None
  # The real head camera: 1.211 x 0.733 rad full FOV (CAM_ANGLE_X/Y).
  cfg.commands["twist"] = mdp.KickLoopCommandCfg(
    debug_vis=play,
    fov_half_angle=K1_CAMERA_HALF_FOV[0],
    fov_vertical_half_angle=K1_CAMERA_HALF_FOV[1],
  )
  # Scripted head: it looks at the ball estimate (see kick_loop.py).
  old = cfg.actions["joint_pos"]
  assert isinstance(old, JointPositionActionCfg)
  cfg.actions["joint_pos"] = mdp.HeadTrackedJointPositionActionCfg(
    entity_name=old.entity_name,
    actuator_names=old.actuator_names,
    scale=old.scale,
    offset=old.offset,
    clip=old.clip,
    preserve_order=old.preserve_order,
    use_default_offset=old.use_default_offset,
    scan_share=0.0 if play else mdp.HEAD_SCAN_SHARE,
  )
  cfg.scene.sensors = tuple(cfg.scene.sensors) + (
    ContactSensorCfg(
      name="body_ball_contact",
      primary=ContactMatch(
        mode="body",
        entity="robot",
        pattern=r".*",
        exclude=("left_foot_link", "right_foot_link"),
      ),
      secondary=ContactMatch(mode="body", pattern="ball", entity="ball"),
      fields=("found",),
      reduce="none",
      num_slots=1,
    ),
  )

  # A different ball every episode, so the kick does not depend on one ball:
  # mass ±30 % (inertia scaled with it), sliding friction ±30 %, rolling
  # resistance 0.6–1.6×.
  cfg.events["ball_mass"] = EventTermCfg(
    mode="reset",
    func=mdp.dr.pseudo_inertia,
    params={
      "asset_cfg": SceneEntityCfg("ball", body_names=(".*",)),
      # v34: mass ×0.5–2.5 (0.05–0.25 kg) for harder, more varied kicks
      # (×0.7–1.4 before). e^{2α} scales mass and inertia.
      "alpha_range": (-0.347, 0.458),
    },
  )
  cfg.events["ball_friction"] = EventTermCfg(
    mode="reset",
    func=mdp.dr.geom_friction,
    params={
      "asset_cfg": SceneEntityCfg("ball", geom_names=("ball_collision",)),
      "operation": "scale",
      # v34: sliding ×0.6–1.4, rolling resistance ×0.5–2.5 (slower surfaces).
      "ranges": {0: (0.6, 1.4), 2: (0.5, 2.5)},
      "axes": [0, 2],
    },
  )

  # v50 / v50b contacts disabled for v50c (attribution: strike efficiency
  # only). v50: pushes ±0.5 + near-ball bumps 30 % ±0.4; v50b: ±0.4 + 15 % ±0.3.
  # v50d: contacts back on, milder than v50b (v50c showed the pushes, not the
  # strike-efficiency term, cost most of the accuracy).
  CONTACTS_V50 = True
  if CONTACTS_V50:
    # ±0.28, and contested-ball bumps near the ball (30 % chance every 0.5–1 s
    # within 1 m, ±0.4 m/s).
    push = cfg.events["push_robot"]
    # v50b: ±0.4 (v50's ±0.5 made the policy cautious: idle at far balls 11 %,
    # 0.77 goals on flat vs 1.00, though push-test late falls 5.1 → 0.7 %).
    push.params["velocity_range"] = dict(
      push.params["velocity_range"], x=(-0.35, 0.35), y=(-0.35, 0.35)
    )
    cfg.events["push_near_ball"] = EventTermCfg(
      mode="interval",
      interval_range_s=(0.5, 1.0),
      func=mdp.push_near_ball,
      params={
        "velocity_range": {
          "x": (-0.25, 0.25),
          "y": (-0.25, 0.25),
          "roll": (-0.3, 0.3),
          "pitch": (-0.3, 0.3),
        },
        "max_dist": 1.0,
        "prob": 0.1,
      },
    )

  # v52: side kicks / quick shots. Standing beside the kick line facing the
  # ball counts as lined up (heading, wedge, lined-up bonus, bad contact; +0.2
  # rad so kicks from behind stay slightly preferred), and 25 % of episodes
  # start with the ball 0.4–1.0 m ahead and the target 60–110° to the side,
  # where circling the ball wastes time. Outcome rewards are unchanged, so a
  # side kick only pays if the ball goes to the target.
  # Off from v53: side kicks were not learned this way (v52, v52b).
  SIDE_KICKS_V52 = False
  if SIDE_KICKS_V52:
    cfg.commands["twist"].side_kicks = True
    cfg.commands["twist"].side_drill_prob = 0.25

  # v56: search. A remembered ball that should be in view but is not (0.5 s),
  # or none seen for 1.5 s, is "lost": the actor gets ball (0, 0) and age 0,
  # the head sweeps, turning toward where it was is paid and backward walking
  # costs. 10 % per second an unseen resting ball is moved elsewhere (another
  # robot), so the memory really goes stale. v55b/12200 re-found a moved ball
  # within 6 s only 25 % of the time, walking toward the old spot.
  SEARCH_V56 = True
  if SEARCH_V56:
    twist = cfg.commands["twist"]
    twist.memory_invalidate = True
    twist.memory_lost_in_view_s = 0.5
    twist.memory_lost_timeout_s = 1.5
    # v56d: virtual ball beside the robot while lost (v56–v56c: (0, 0) and
    # age 0 — the policy never found a steady spin, net 0.34 rad per search).
    twist.lost_virtual_ball = True
    cfg.events["ball_relocate_unseen"] = EventTermCfg(
      mode="interval",
      interval_range_s=(1.0, 1.0),
      func=mdp.ball_relocate_unseen,
      params={"prob": 0.1},
    )

  # K4b (v60): 20 % of episodes start mid-kick (0.2–0.4 s before contact)
  # from recorded kicks in our sim: 10 % B-Human side-foot, 10 % our front
  # kicks (data/kick_rsi). The policy experiences both styles; outcomes pick.
  KICK_RSI_V60 = True
  # Training only: evaluation must start every episode normally
  # (KICK_EVAL=1 is set by the eval / benchmark tools).
  if KICK_RSI_V60 and os.environ.get("KICK_EVAL") != "1":
    _rsi = Path(__file__).resolve().parents[6].parent / "data" / "kick_rsi"
    if (_rsi / "bhuman_side.npz").is_file():
      cfg.commands["twist"].rsi_files = (
        (str(_rsi / "bhuman_side.npz"), float(KICK_GENES.get("rsi_bhuman", 0.1))),
        (str(_rsi / "ours_front.npz"), float(KICK_GENES.get("rsi_ours", 0.1))),
      )

  # v51: moving ball. Rolling starts (0–1.5 m/s, random direction) and nudges
  # of a resting ball (50 % chance every 3–6 s, 0.5–1.5 m/s), like
  # deflections or an opponent's touch. The policy has no ball-velocity input,
  # so it learns to re-target and kick a slowly rolling ball.
  MOVING_BALL_V51 = False
  if MOVING_BALL_V51:
    # v51b: milder than v51 (0–1.5 m/s spawn, 0.5–1.5 m/s nudges of any
    # ball), which taught the policy to wait for the ball.
    cfg.commands["twist"].ball_spawn_speed = (0.0, 0.8)
    cfg.events["ball_nudge"] = EventTermCfg(
      mode="interval",
      interval_range_s=(3.0, 6.0),
      func=mdp.ball_nudge,
      params={"speed_range": (0.3, 1.0), "prob": 0.3, "require_in_view": True},
    )

  # v34: ball bounce. Nominal solref (0.05, 0.15); dampratio 0.08–0.4 spans
  # bouncier to deader balls, timeconst 0.03–0.08 harder to softer contact.
  cfg.events["ball_bounce"] = EventTermCfg(
    mode="reset",
    func=mdp.dr.geom_solref,
    params={
      "asset_cfg": SceneEntityCfg("ball", geom_names=("ball_collision",)),
      "operation": "abs",
      "ranges": {0: (0.03, 0.08), 1: (0.08, 0.4)},
      "axes": [0, 1],
    },
  )

  # Replaced: standing still at the ball, the gated heading term and the
  # instantaneous speed limit.
  for name in ("approach_stand", "approach_heading", "approach_speed_limit"):
    cfg.rewards[name].weight = 0.0

  # Event rewards pay once (value × weight × dt): 900 → 18 per perfect kick.
  # Kicks must clearly outweigh the risk of a fall (−10 plus the per-step
  # rewards it forfeits), or the policy learns not to kick (stage3_v1).
  terms = {
    "ball_vision": (mdp.approach_view, 1.0),
    "kick_dir_alignment": (mdp.kick_dir_alignment, 50.0),
    # 2 → 5 in v25: with CAPS 1.0 and foot_flat −60, v24 stood still in
    # front of balls 3–4 m away (standing is smooth and costs nothing).
    "walk_speed": (mdp.walk_speed, 5.0),
    # v39: −10 → −20; low caps were exceeded 24–31 % of chasing time.
    "walk_speed_limit": (mdp.walk_speed_limit, -20.0),
    # v39: move at the cap when the ball is far (> 2.5 m).
    # v41 tried 8: no faster (0.95 m/s at 2 m/s caps) and kicking fell
    # (2.1 kicks, 0.89 goals, 88 % within 20°); back to 3.
    "walk_speed_track": (mdp.walk_speed_track, 3.0),
    "kick_direction": (mdp.kick_direction, 900.0),
    "kick_vel": (mdp.kick_vel, 900.0),
    "kick_vel_accurate": (mdp.kick_vel_accurate, 300.0),
    "ball_avoidance": (mdp.ball_avoidance, -5.0),
    "single_feet_avoidance": (mdp.single_feet_avoidance, -5.0),
    "kick_goal": (mdp.kick_goal, 1500.0),
    "kick_lined_up": (mdp.kick_lined_up, 200.0),
    "kick_double_touch": (mdp.kick_double_touch, -200.0),
    "post_kick_stability": (mdp.post_kick_stability, 4.0),
    "fall": (mdp.is_terminated, -1000.0),
    # Lean costs: ~0.07/s at the walker's 3.5°, ~1.3/s at 15° (v13/v16 mean).
    "trunk_tilt": (mdp.flat_orientation_l2, -20.0),
    "kick_fall": (mdp.kick_fall, -2500.0),
    # Posture (v21): knees closed to 0.09–0.12 m and arms spread in kicks.
    # 0.12 m costs 8/s, 0.10 m 18/s; the default pose costs nothing.
    "knee_gap": (mdp.knee_gap_violation, -2.0),
    "arm_pose": (mdp.arm_pose_deviation, -2.0),
    # Walking pose (v29), gated off around kicks: at v28's pose each costs
    # ~0.7–1.0/s (height 6 cm low, feet 6 cm too wide, knees 7 cm inside).
    # v34: 0.52 m ± 1 cm free band, ((excess) / 2 cm)²: 2 cm over the band
    # costs 1/s, 4 cm 4/s (was −250 × err² around 0.54 m).
    "walk_base_height": (mdp.walk_base_height, -1.0),
    # v34: trunk pitch kept in −5°…+3° while walking: 2° outside costs 0.5/s.
    # v51 tried −1.0 (with the moving ball); reverted for v51b to change one
    # thing at a time.
    "trunk_pitch_band": (mdp.trunk_pitch_band, -0.5),
    # v34: long kicks paid for landing in the (rising) speed band.
    # v47: 900 → 2000. At 900, +1 m/s of swing paid ~+4.5 per long kick
    # against ≥ 50 for one post-kick fall, and the swing stayed at p50 ~3.5.
    # v55b: 2000 → 3000. With lofted kicks unpaid (v55) grounded long kicks
    # fell to 0.71× the needed speed while short / medium kicks multiplied.
    "long_kick_power": (mdp.long_kick_power, 3000.0),
    # v56: search while the ball is lost (memory judged stale).
    # v56b: 3 → 10. At 3, v56 stopped walking back but barely turned (0.20
    # rad/s mean vs 0.95 cap while searching).
    "search_turn": (mdp.search_turn, 10.0),
    # K3 (v58): soft torque limit at B-Human's sim2real clip. Walking stays
    # inside it (p99 ≤ 36 Nm); v57/13950's long kicks reach knee p90 107 Nm.
    # A 0.6 overshoot for ~5 strike steps costs ~6 vs ~30 for a long kick.
    "torque_over_soft_limit": (mdp.torque_over_soft_limit, -100.0),
    # Side-foot strike (B-Human style): off; an experiment / gene only.
    "side_foot_strike": (mdp.side_foot_strike, 0.0),
    "search_backward": (mdp.search_backward, -5.0),
    # v54: short / medium passes paid for stopping near the target (v53 kicked
    # short targets at 1.8× the needed speed; the goal counts a ball passing
    # the target, so overshooting cost nothing).
    "kick_rest_accuracy": (mdp.kick_rest_accuracy, 600.0),
    # v54c: a long kick at half the needed speed costs ~300 (≈ a fifth of a
    # goal), so the soft short-pass motion stops leaking into long kicks.
    # v54d: −800 → −300. At −800 (v54c) not kicking long became the safe
    # choice: long kicks 555 → 454, near-ball wait up, goals 0.98 → 0.69.
    "long_kick_underpower": (mdp.long_kick_underpower, -300.0),
    # v52b: per aimed, well-struck short / medium kick launched 30–60°+ off
    # the body heading (v52's relaxed alignment alone left side kicks at ~3 %).
    "side_kick_bonus": (mdp.side_kick_bonus, 400.0 if SIDE_KICKS_V52 else 0.0),
    # v38: arms out sideways (shoulder roll +0.28, elbow yaw ±0.21 rad at
    # v37/6600); 0.1 rad free, ((excess)/0.1)² per joint, off around kicks.
    "arm_abduction": (mdp.arm_abduction, -0.3),
    "walk_stance_width": (mdp.walk_stance_width, -250.0),
    "knee_valgus": (mdp.knee_valgus, -200.0),
  }
  # Flat stance foot (v22): v21 walked on its toes, heel up > 5° in 34 % of
  # contact samples in the runner sim (gold walk 2.4 %). Pitch² while the foot
  # is on the ground; the swing (kicking) foot is free. At −30 (v22/v23)
  # heel-up stalled near 22 % of contact samples; at −60 (v24/v25) it stayed
  # ~20 %, mostly an early heel lift while walking (p50 0.7°, p90 8.8°).
  # −200 from v26 (8° ≈ 3.9/s per foot while it lasts).
  cfg.rewards["foot_flat"] = RewardTermCfg(
    func=mdp.htwk_feet_orientation_contact_gated,
    weight=-200.0,
    params={
      "axis": 1,
      "sensor_name": "feet_ground_contact",
      "asset_cfg": SceneEntityCfg(
        "robot", body_names=("left_foot_link", "right_foot_link")
      ),
    },
  )
  # Keep the per-step reward of staying up positive (~+1/s): in stage3_v2 a
  # global time cost plus action_rate on noisy kicking actions made it −3 to
  # −10/s, and the policy learned to fall at once. Kicks are abrupt, so
  # action_rate is lighter here than in the walk.
  # Back to the walk's −0.1 (−0.03 in v3–v17): at −0.03 the leg targets jumped
  # 0.13 rad per step on average (0.9 rad p99), 5–8× the AMP walker, and the
  # real robot shook. The per-second budget at −0.1 stays positive (~+2.6/s).
  cfg.rewards["action_rate_l2"].weight = -0.1
  # v44 tried air_time weight 1.0 with threshold_min 0.15 s: cadence unchanged
  # (7.04 vs 7.06 steps/s), speed unchanged; reverted to the AMP walk's.
  # Joint-limit use grew 5–7× in every long kick run (v8–v15) as falls rose;
  # at −1 the term was ~0.1 per episode against ~230 of kick rewards.
  cfg.rewards["dof_pos_limits"].weight = -10.0
  cfg.rewards.pop("approach_view")
  # Reward program (L1 reward grammar, KICK_REWARD_PROGRAM=path.json): add,
  # replace or remove terms; expression terms are built from the grammar.
  prog_path = os.environ.get("KICK_REWARD_PROGRAM")
  if prog_path:
    from mjlab.tasks.velocity.mdp import reward_grammar as rg

    for entry in rg.load_program(prog_path):
      name = entry["name"]
      if entry.get("remove"):
        terms.pop(name, None)
        cfg.rewards.pop(name, None)
      elif "expr" in entry:
        terms[name] = (rg.make_expr_term(entry["expr"]), float(entry["weight"]))
      else:
        func = getattr(mdp, entry.get("term", name))
        terms[name] = (func, float(entry.get("weight", terms.get(name, (None, 0.0))[1])))
  for name, (func, weight) in terms.items():
    weight = float(KICK_GENES.get(f"w.{name}", weight))
    cfg.rewards[name] = RewardTermCfg(func=func, weight=weight)
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

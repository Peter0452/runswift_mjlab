"""Kick-on-Walk-AMP environment: Flat AMP Walk + thesis kick (78/95 obs)."""

from __future__ import annotations

import math

import mujoco

from mjlab.asset_zoo.props.ball import BALL_XML, get_ball_radius
from mjlab.entity import EntityCfg
from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.envs.mdp import rewards as env_rewards
from mjlab.envs.mdp.terminations import bad_orientation, root_height_below_minimum
from mjlab.managers.event_manager import EventTermCfg
from mjlab.managers.observation_manager import ObservationGroupCfg, ObservationTermCfg
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.managers.termination_manager import TerminationTermCfg
from mjlab.sensor import ContactMatch, ContactSensorCfg
from mjlab.tasks.kick import mdp as kick_mdp
from mjlab.tasks.kick.mdp.ball_phase import reset_ball_phase_state
from mjlab.tasks.kick.mdp.commands import UniformGoalPositionCommandCfg
from mjlab.tasks.kick.mdp.events import (
  reset_walkamp_kick_episode,
  update_ball_phase_buffers,
)
from mjlab.tasks.velocity import mdp as velocity_mdp
from mjlab.tasks.velocity.config.k1_amp.env_cfgs import booster_k1_amp_flat_env_cfg
from mjlab.utils.noise import UniformNoiseCfg as Unoise
from mjlab.utils.spec_config import CollisionCfg

_BALL_RADIUS = 0.08
_BALL_MASS = 0.1
_BALL_FRICTION = (1.0, 0.5, 0.015)
_PLANE_SOLREF = (0.02, 1.0)
_PLANE_SOLIMP = (0.99, 0.99, 0.01)
_PLANE_FRICTION = (1.0, 0.005, 0.0001)
_CONTACT_WINDOW_STEPS = 50
_TARGET_RADIUS = 1.0
_BALL_STILL_EPS = 0.5
_THETA_LIMIT = 1.2217
_FALL_HEIGHT = 0.2
_BASE_HEIGHT_TARGET = 0.5  # Walk / arc standing trunk target
_EPISODE_S = 8.0  # 400 steps @ 50 Hz


def _get_walkamp_ball_spec() -> mujoco.MjSpec:
  """Thesis Table 3.1 ball: 0.08 m, 0.1 kg, friction (1, 0.5, 0.015)."""
  spec = mujoco.MjSpec.from_file(str(BALL_XML))
  # Scale meshes from size-5 (0.11 m) to 0.08 m.
  scale = _BALL_RADIUS / get_ball_radius(5)
  for mesh in spec.meshes:
    mesh.scale = (scale, scale, scale)
  ball_body = spec.worldbody.bodies[0]
  for geom in ball_body.geoms:
    if geom.name.startswith("ball_visual"):
      geom.mass = 0.0
      geom.density = 0.0
      geom.friction = _BALL_FRICTION
    elif geom.name == "ball_collision":
      geom.group = 3
      geom.size = (_BALL_RADIUS, 0, 0)
      geom.typeinertia = mujoco.mjtGeomInertia.mjINERTIA_SHELL
      geom.priority = 1
      geom.condim = 6
      geom.mass = _BALL_MASS
      geom.solref = (0.05, 0.15)
      geom.friction = _BALL_FRICTION
  return spec


def make_walkamp_kick_env_cfg(
  play: bool = False,
  *,
  arrival_buffer_path: str | None = None,
) -> ManagerBasedRlEnvCfg:
  """Flat AMP Walk base + ball/goal + thesis 13 rewards + Table 3.3 terms."""
  cfg = booster_k1_amp_flat_env_cfg(play=False)
  robot = SceneEntityCfg("robot")
  ball = SceneEntityCfg("ball")
  trunk = SceneEntityCfg("robot", body_names=("Trunk",))
  feet_sites = SceneEntityCfg("robot", site_names=("left_foot", "right_foot"))

  cfg.only_positive_rewards = False
  cfg.episode_length_s = _EPISODE_S
  cfg.scene.env_spacing = max(cfg.scene.env_spacing, 12.0)
  cfg.sim.mujoco.impratio = 10.0
  cfg.sim.mujoco.cone = "elliptic"
  cfg.sim.njmax = max(cfg.sim.njmax, 300)

  # Ball entity + thesis physics.
  cfg.scene.entities["ball"] = EntityCfg(spec_fn=_get_walkamp_ball_spec)
  if cfg.scene.terrain is not None:
    cfg.scene.terrain.collisions = (
      CollisionCfg(
        geom_names_expr=(r"^terrain$",),
        solref=_PLANE_SOLREF,
        solimp=_PLANE_SOLIMP,
        friction=_PLANE_FRICTION,
        disable_other_geoms=False,
      ),
    )

  feet_ball_contact = ContactSensorCfg(
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
  )
  body_ball_contact = ContactSensorCfg(
    name="body_ball_contact",
    primary=ContactMatch(
      mode="subtree",
      pattern="Trunk",
      entity="robot",
      exclude=("left_foot_link", "right_foot_link"),
    ),
    secondary=ContactMatch(mode="body", pattern="ball", entity="ball"),
    fields=("found",),
    reduce="netforce",
    num_slots=1,
  )
  cfg.scene.sensors = (cfg.scene.sensors or ()) + (
    feet_ball_contact,
    body_ball_contact,
  )

  # Goal command (no twist for policy — drop tracking rewards).
  # Reset overwrites pose; angle_range documents the ±90° approach cone.
  cfg.commands["goal"] = UniformGoalPositionCommandCfg(
    distance_range=(2.5, 8.5),
    angle_range=(-math.pi / 2.0, math.pi / 2.0),
    resampling_time_range=(1e9, 1e9),
    debug_vis=True,
  )
  # Keep twist for AMP walk legacy sensors if any, but disable sampling impact.
  if "twist" in cfg.commands:
    cfg.commands["twist"].debug_vis = False
    cfg.commands["twist"].resampling_time_range = (1e9, 1e9)
    cfg.commands["twist"].rel_standing_envs = 1.0

  # ---- Observations: actor 78 / critic 95 ----
  actor_terms = {
    "base_ang_vel": ObservationTermCfg(
      func=velocity_mdp.builtin_sensor,
      params={"sensor_name": "robot/imu_ang_vel"},
      noise=Unoise(n_min=-0.2, n_max=0.2),
    ),
    "projected_gravity": ObservationTermCfg(
      func=velocity_mdp.projected_gravity,
      noise=Unoise(n_min=-0.05, n_max=0.05),
    ),
    "ball_rel_pos": ObservationTermCfg(
      func=kick_mdp.ball_relative_position,
      params={"robot_cfg": robot, "ball_cfg": ball},
    ),
    "target_pos": ObservationTermCfg(
      func=kick_mdp.target_position,
      params={"command_name": "goal", "robot_cfg": robot},
    ),
    "joint_pos": ObservationTermCfg(
      func=velocity_mdp.joint_pos_rel,
      params={"biased": True},
      noise=Unoise(n_min=-0.01, n_max=0.01),
    ),
    "joint_vel": ObservationTermCfg(
      func=velocity_mdp.joint_vel_rel,
      noise=Unoise(n_min=-1.5, n_max=1.5),
    ),
    "actions": ObservationTermCfg(func=velocity_mdp.last_action),
  }
  critic_terms = {
    **actor_terms,
    "joint_pos": ObservationTermCfg(func=velocity_mdp.joint_pos_rel),
    "joint_vel": ObservationTermCfg(func=velocity_mdp.joint_vel_rel),
    "foot_height": ObservationTermCfg(
      func=velocity_mdp.foot_height,
      params={"sensor_name": "foot_height_scan"},
    ),
    "foot_air_time": ObservationTermCfg(
      func=velocity_mdp.foot_air_time,
      params={"sensor_name": "feet_ground_contact"},
    ),
    "foot_contact": ObservationTermCfg(
      func=velocity_mdp.foot_contact,
      params={"sensor_name": "feet_ground_contact"},
    ),
    "foot_contact_forces": ObservationTermCfg(
      func=velocity_mdp.foot_contact_forces,
      params={"sensor_name": "feet_ground_contact"},
    ),
    "ball_velocity": ObservationTermCfg(
      func=kick_mdp.ball_velocity_base,
      params={"robot_cfg": robot, "ball_cfg": ball},
    ),
    "ball_foot_contact": ObservationTermCfg(
      func=kick_mdp.ball_foot_contact,
      params={"sensor_name": "feet_ball_contact"},
    ),
  }
  cfg.observations = {
    "actor": ObservationGroupCfg(
      terms=actor_terms,
      concatenate_terms=True,
      enable_corruption=True,
    ),
    "critic": ObservationGroupCfg(
      terms=critic_terms,
      concatenate_terms=True,
      enable_corruption=False,
    ),
  }

  # ---- Rewards: thesis 13 + ball_vel + base_height ----
  cfg.rewards = {
    "target_reached": RewardTermCfg(
      func=kick_mdp.target_reached_walkamp,
      weight=250.0,
      params={
        "command_name": "goal",
        "contact_window_steps": _CONTACT_WINDOW_STEPS,
        "velocity_eps": _BALL_STILL_EPS,
        "sigma_sq": 0.9,
        "ball_cfg": ball,
      },
    ),
    "ball_approach_target": RewardTermCfg(
      func=kick_mdp.ball_approach_target,
      weight=0.3,
      params={
        "command_name": "goal",
        "velocity_eps": _BALL_STILL_EPS,
        "ball_cfg": ball,
      },
    ),
    "agent_approach_ball": RewardTermCfg(
      func=kick_mdp.agent_approach_ball,
      weight=0.1,
      params={
        "command_name": "goal",
        # Thesis: no distance gate — pull through until the ball moves.
        "velocity_eps": 0.1,
        "robot_cfg": robot,
        "ball_cfg": ball,
      },
    ),
    # Paper: r = min(6, v_b · d̂_goal) — high ball speed toward opponent goal.
    "ball_velocity_toward_goal": RewardTermCfg(
      func=kick_mdp.ball_velocity_toward_goal,
      weight=1.0,
      params={
        "command_name": "goal",
        "max_reward": 6.0,
        "use_decay": False,
        "ball_cfg": ball,
        "robot_cfg": robot,
      },
    ),
    "ball_stagnant": RewardTermCfg(
      func=kick_mdp.ball_stagnant,
      # Thesis −0.01 cancelled survival → freeze local optimum under AMP.
      # −0.05 keeps arrival-gated tax and makes still-ball strictly negative.
      weight=-0.02,
      params={
        "velocity_eps": _BALL_STILL_EPS,
        "max_ball_distance": 0.3,
        "ball_cfg": ball,
        "robot_cfg": robot,
      },
    ),
    "survival": RewardTermCfg(func=env_rewards.is_alive, weight=0.01),
    "upright": RewardTermCfg(
      func=kick_mdp.upright_tilt,
      weight=0.05,
      params={"sigma_sq": 0.1, "asset_cfg": trunk},
    ),
    # Anti-crouch: (z − 0.52)² — Walk BaseWalk target; flat uses root z.
    "base_height": RewardTermCfg(
      func=velocity_mdp.base_height_target_l2,
      weight=-15.0,
      params={
        "target_height": _BASE_HEIGHT_TARGET,
        "sensor_name": None,
        "asset_cfg": robot,
      },
    ),
    "fell_over_penalty": RewardTermCfg(
      func=kick_mdp.fell_over_penalty,
      weight=-100.0,
      params={"limit_angle": _THETA_LIMIT, "asset_cfg": trunk},
    ),
    "fall_down": RewardTermCfg(
      func=kick_mdp.fall_down,
      weight=-100.0,
      params={"minimum_height": _FALL_HEIGHT, "asset_cfg": trunk},
    ),
    "dof_pos_limits": RewardTermCfg(
      func=kick_mdp.dof_pos_limits_binary,
      weight=-1.0,
      params={"asset_cfg": robot},
    ),
    "action_rate_l2": RewardTermCfg(func=env_rewards.action_rate_l2, weight=-0.0075),
    "foot_slip": RewardTermCfg(
      func=kick_mdp.foot_slip_ungated,
      weight=-0.01,
      params={
        "sensor_name": "feet_ground_contact",
        "asset_cfg": feet_sites,
      },
    ),
    "arm_swing": RewardTermCfg(
      func=kick_mdp.arm_swing,
      weight=-0.05,
      params={"asset_cfg": robot},
    ),
    "arm_posture": RewardTermCfg(
      func=kick_mdp.arm_posture,
      weight=0.3,
      params={"sigma": 0.5, "asset_cfg": robot},
    ),
  }

  # ---- Terminations: Table 3.3 ----
  cfg.terminations = {
    "time_out": TerminationTermCfg(
      func=velocity_mdp.time_out, time_out=True
    ),
    "fell_over": TerminationTermCfg(
      func=bad_orientation,
      params={"limit_angle": _THETA_LIMIT, "asset_cfg": trunk},
    ),
    "root_height": TerminationTermCfg(
      func=root_height_below_minimum,
      params={"minimum_height": _FALL_HEIGHT, "asset_cfg": trunk},
    ),
    "target_hit": TerminationTermCfg(
      func=kick_mdp.target_hit_walkamp,
      params={
        "target_radius": _TARGET_RADIUS,
        "ball_stationary_speed_threshold": _BALL_STILL_EPS,
        "command_name": "goal",
        "ball_cfg": ball,
        "robot_cfg": robot,
      },
    ),
    "target_missed": TerminationTermCfg(
      func=kick_mdp.target_missed_walkamp,
      params={
        "target_radius": _TARGET_RADIUS,
        "contact_window_steps": _CONTACT_WINDOW_STEPS,
        "ball_stationary_speed_threshold": _BALL_STILL_EPS,
        "command_name": "goal",
        "ball_cfg": ball,
        "robot_cfg": robot,
      },
    ),
    "double_touch": TerminationTermCfg(
      func=kick_mdp.double_touch_walkamp,
      params={
        "contact_window_steps": _CONTACT_WINDOW_STEPS,
        "command_name": "goal",
        "ball_cfg": ball,
        "robot_cfg": robot,
      },
    ),
    "nan_state": TerminationTermCfg(func=velocity_mdp.nan_detection),
  }

  # ---- Events: arrival reset + ball phase; retune foot friction / push ----
  cfg.events.pop("reset_base", None)
  cfg.events.pop("reset_robot_joints", None)
  cfg.events.pop("terrain_contact", None)
  # Drop walk-only curriculum that references twist tracking.
  if cfg.curriculum is not None:
    cfg.curriculum.pop("terrain_levels", None)
    cfg.curriculum.pop("command_vel", None)
    cfg.curriculum.pop("soft_landing_weight", None)

  buf_path = arrival_buffer_path
  cfg.events["reset_walkamp"] = EventTermCfg(
    func=reset_walkamp_kick_episode,
    # After command_manager.reset so our ball/target/goal write is not overwritten.
    mode="post_reset",
    params={
      "buffer_path": buf_path,
      "ball_height": _BALL_RADIUS,
      # Relaxed vs ±60° + face_ball: wider cone, keep arrival heading.
      "spawn_half_angle": math.pi / 2.0,
      "face_ball": False,
      "ball_x_max": 1.5,
      "ball_cfg": ball,
      "robot_cfg": robot,
    },
  )
  cfg.events["reset_ball_phase"] = EventTermCfg(
    func=reset_ball_phase_state,
    mode="reset",
  )
  cfg.events["update_ball_phase"] = EventTermCfg(
    func=update_ball_phase_buffers,
    mode="step",
    params={
      "ball_stationary_speed_threshold": _BALL_STILL_EPS,
      "kick_detection_speed_increase_threshold": 0.5,
      "ball_cfg": ball,
      "robot_cfg": robot,
    },
  )
  # Foot friction thesis U[0.3, 1.2]
  if "foot_friction" in cfg.events:
    cfg.events["foot_friction"].params["ranges"] = (0.3, 1.2)
    cfg.events["foot_friction"].params["shared_random"] = False
  # Push: planar-ish, every 1–3 s (magnitude via velocity impulse; Walk-style).
  if "push_robot" in cfg.events:
    cfg.events["push_robot"].interval_range_s = (1.0, 3.0)
    cfg.events["push_robot"].params["velocity_range"] = {
      "x": (-0.5, 0.5),
      "y": (-0.5, 0.5),
      "z": (0.0, 0.0),
      "roll": (0.0, 0.0),
      "pitch": (0.0, 0.0),
      "yaw": (-0.3, 0.3),
    }

  # Drop walk metrics that need twist tracking.
  cfg.metrics = {}

  if play:
    cfg.episode_length_s = int(1e9)
    cfg.observations["actor"].enable_corruption = False
    cfg.events.pop("push_robot", None)
    cfg.commands["goal"].debug_vis = True
    # Fixed standoff: robot 0.6 m behind ball on the approach axis.
    cfg.events["reset_walkamp"].params.update(
      {
        "ball_x_min_base": 0.3,
        "ball_x_max": 0.3,
        "momentum_time_s": 0.0,
        "spawn_half_angle": 0.0,
        "face_ball": True,
      }
    )
    # Keep double_touch so play matches train (single-strike rule).
    # Hit/miss still popped so infinite play is not cut by outcome terms.
    cfg.terminations.pop("target_hit", None)
    cfg.terminations.pop("target_missed", None)

  return cfg


def make_walkamp_kick_amp_env_cfg(
  play: bool = False,
  *,
  arrival_buffer_path: str | None = None,
  style_weight: float = 0.3,
) -> ManagerBasedRlEnvCfg:
  """WalkAmp kick + AMP obs group (style gated on ``kick_detected``)."""
  from mjlab.tasks.kick.config.k1.amp_wrapper import with_kick_amp_obs_group

  return with_kick_amp_obs_group(
    make_walkamp_kick_env_cfg(
      play=play, arrival_buffer_path=arrival_buffer_path
    ),
    style_weight=style_weight,
  )

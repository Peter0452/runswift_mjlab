"""Unified Arc→Setup→Strike kick task on BaseWalk (replaces chase/approach/strike/score)."""

from __future__ import annotations

import math

from mjlab.entity import EntityCfg
from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.managers.curriculum_manager import CurriculumTermCfg
from mjlab.managers.event_manager import EventTermCfg
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.managers.termination_manager import TerminationTermCfg
from mjlab.tasks.kick import mdp as kick_mdp
from mjlab.tasks.kick.kick_obs import add_unified_kick_observations
from mjlab.tasks.kick.mdp.ball_phase import reset_ball_phase_state
from mjlab.tasks.kick.mdp.commands import UniformGoalPositionCommandCfg
from mjlab.tasks.kick.mdp.events import (
  reset_ball_uniform,
  reset_robot_around_ball_facing,
  update_ball_phase_buffers,
  update_pref_pose_twist_command,
)
from mjlab.tasks.kick.mdp.pref_pose import reset_pref_pose_state
from mjlab.tasks.kick.mdp.terminations import (
  double_touch,
  target_hit,
  target_missed,
)
from mjlab.tasks.velocity import mdp as velocity_mdp
from mjlab.utils.spec_config import CollisionCfg

# Shared 3-phase geometry knobs (reward params).
# enter < exit required for Arc↔Setup hysteresis (else phases chatter).
_PREF = {
  # Legacy / debug only — P_ref is always setup_xy (no side-arc magnet).
  "arc_radius": 0.4,
  "setup_enter_dist": 0.45,
  "setup_exit_dist": 0.5,
  "setup_behind": 0.35,
  "setup_lateral": 0.12,
  "prefer_right_foot": True,
  "bearing_thresh": 0.2,
  "lateral_thresh": 0.05,
  # P_ref = setup_xy in Arc/Setup/Strike (never arc ring, never onto ball).
  # setup_blend_end / strike_blend_thresh only drive Setup→Strike hysteresis.
  "setup_blend_end": 0.20,
  "strike_blend_thresh": 0.75,
  "setup_pos_thresh": 0.28,
  # Nearest-foot during Arc; latch on Setup (prefer_right_foot = reset default only).
  "dynamic_kick_foot": True,
}

_TRUNK_HEIGHT_TARGET = 0.52
_TRUNK_HEIGHT_MIN = 0.46
_MIN_KICK_SPEED = 5.0  # "strong kick" threshold (post_kick_upright bonus)
# Dribble band: ball speed >= dribble_speed but projected speed toward goal
# below this is treated as a slow nudge, not a real kick. Kept in sync with
# ``ensure_ball_phase_updated``'s default ``min_kick_speed`` (first caller wins).
_KICK_REWARD_GATE_SPEED = 1.2
_BALL_RADIUS = 0.11  # FIFA size-5; spawn z = radius so the ball rests on the plane
# Critically damped contacts (solref = timeconst, dampratio — not COR).
_BALL_SOLREF = (0.02, 1.0)
_BALL_JOINT_DAMPING = 0.05
_PLANE_SOLREF = (0.02, 1.0)
_PLANE_SOLIMP = (0.99, 0.99, 0.01)
_PLANE_FRICTION = (1.0, 0.005, 0.0001)
_AIR_DENSITY = 1.2
_AIR_VISCOSITY = 0.000018
_POST_KICK_STABILITY_S = 1.0
_TARGET_RADIUS = 1.0  # metres — ball stopped inside this of goal = hit
_POST_KICK_WINDOW_S = 2.0  # T_window for target miss / settle
_DOUBLE_TOUCH_WINDOW_S = 0.10  # debounce before a second contact edge is illegal
_BALL_SPAWN_XY_NOISE = 0.05  # ±m jitter on ball reset XY
_BALL_OBS_NOISE = (-0.05, 0.05)  # actor ball_rel_pos uniform noise (m)


def make_arc_kick_env_cfg(base_cfg: ManagerBasedRlEnvCfg) -> ManagerBasedRlEnvCfg:
  """BaseWalk + ball/goal + 3-phase ``P_ref`` rewards (policy-owned twist)."""
  from mjlab.asset_zoo.props import get_ball_spec

  robot = SceneEntityCfg("robot")
  ball = SceneEntityCfg("ball")
  trunk = SceneEntityCfg("robot", body_names=("Trunk",))
  robot_ball = {"robot_cfg": robot, "ball_cfg": ball}
  goal_params = {**robot_ball, "command_name": "goal", **_PREF}

  base_cfg.only_positive_rewards = False
  base_cfg.scene.entities["ball"] = EntityCfg(
    spec_fn=lambda: get_ball_spec(
      radius=_BALL_RADIUS,
      solref=_BALL_SOLREF,
      joint_damping=_BALL_JOINT_DAMPING,
      friction=(1.0, 0.5, 0.015),
    )
  )
  if base_cfg.scene.terrain is not None:
    # Keep the infinite plane; only retune contact (do not change walk terrains).
    base_cfg.scene.terrain.collisions = (
      CollisionCfg(
        geom_names_expr=(r"^terrain$",),
        solref=_PLANE_SOLREF,
        solimp=_PLANE_SOLIMP,
        friction=_PLANE_FRICTION,
        disable_other_geoms=False,
      ),
    )
  base_cfg.sim.mujoco.density = _AIR_DENSITY
  base_cfg.sim.mujoco.viscosity = _AIR_VISCOSITY
  base_cfg.scene.env_spacing = max(base_cfg.scene.env_spacing, 10.0)

  # Real robot↔ball contacts for kick latch / double_touch (not distance proxies).
  from mjlab.sensor.contact_sensor import ContactMatch, ContactSensorCfg

  feet_ball_contact = ContactSensorCfg(
    name="feet_ball_contact",
    primary=ContactMatch(
      mode="subtree",
      pattern=r"^(left_foot_link|right_foot_link)$",
      entity="robot",
    ),
    secondary=ContactMatch(mode="body", pattern="ball", entity="ball"),
    fields=("found",),
    reduce="netforce",
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
  base_cfg.scene.sensors = (base_cfg.scene.sensors or ()) + (
    feet_ball_contact,
    body_ball_contact,
  )

  base_cfg.commands["goal"] = UniformGoalPositionCommandCfg(
    distance_range=(4.0, 8.0),
    angle_range=(-math.pi, math.pi),
    resampling_time_range=(30.0, 30.0),
    debug_vis=True,
    **_PREF,
  )

  add_unified_kick_observations(
    base_cfg,
    robot_cfg=robot,
    ball_cfg=ball,
    ball_pos_noise=_BALL_OBS_NOISE,
  )

  # Twist teacher: overwrite random walk cmd toward P_ref each step so
  # tracking_* rewards reinforce approach instead of fighting kick geometry.
  for name in ("approach_twist", "kick_twist", "reset_strike", "kick_robot"):
    base_cfg.events.pop(name, None)

  base_cfg.events["reset_ball"] = EventTermCfg(
    func=reset_ball_uniform,
    mode="reset",
    params={
      "pose_range": {
        "x": (-_BALL_SPAWN_XY_NOISE, _BALL_SPAWN_XY_NOISE),
        "y": (-_BALL_SPAWN_XY_NOISE, _BALL_SPAWN_XY_NOISE),
        "z": (_BALL_RADIUS, _BALL_RADIUS),
      },
      "ball_cfg": ball,
    },
  )
  base_cfg.events["reset_base"] = EventTermCfg(
    func=reset_robot_around_ball_facing,
    mode="post_reset",
    params={
      "radius_range": (0.8, 1.5),
      "spawn_on_approach_side": True,
      "goal_command_name": "goal",
      "robot_cfg": robot,
      "ball_cfg": ball,
    },
  )
  base_cfg.events["reset_ball_phase"] = EventTermCfg(
    func=reset_ball_phase_state,
    mode="reset",
  )
  base_cfg.events["reset_pref_pose"] = EventTermCfg(
    func=reset_pref_pose_state,
    mode="reset",
  )
  base_cfg.events["ball_phase"] = EventTermCfg(
    func=update_ball_phase_buffers,
    mode="step",
    params={
      "ball_stationary_speed_threshold": 0.1,
      "kick_detection_speed_increase_threshold": 0.5,
      # Dribble / slow-ball gate (not the strong-kick upright threshold).
      "min_kick_speed": _KICK_REWARD_GATE_SPEED,
      "strong_kick_speed": _MIN_KICK_SPEED,
      "kick_phase_robot_ball_distance": _PREF["setup_exit_dist"],
      "ball_cfg": ball,
      "robot_cfg": robot,
      "goal_command_name": "goal",
    },
  )
  # Twist teacher: paper-style robot→ball aligned tracking targets
  # (v = v_x·r̂_rb, ω = ω_z·sign(θ)); overwrites random walk resample.
  base_cfg.events["pref_pose_twist"] = EventTermCfg(
    func=update_pref_pose_twist_command,
    mode="step",
    params={
      "command_name": "twist",
      "goal_command_name": "goal",
      "cruise_speed": 0.7,
      "min_speed": 0.25,
      "slow_distance": 1.0,
      "plant_distance": 0.20,
      "turn_speed": 1.0,
      "heading_deadzone": 0.05,
      "use_sampled_magnitudes": True,
      "robot_cfg": robot,
      "ball_cfg": ball,
    },
  )
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

  twist = base_cfg.commands["twist"]
  twist.still_proportion = 0.1
  twist.rel_standing_envs = 0.0
  twist.resampling_time_range = (8.0, 12.0)

  # Drop legacy waypoint / approach / strike-only reward names.
  for name in (
    "behind_ball_waypoint",
    "waypoint_approach_velocity",
    "waypoint_retreat_penalty",
    "ball_approach_far",
    "ball_distance_band",
    "ball_camera_cone",
    "kick_ready",
    "kick_zone",
    "kicking_foot_approach",
    "kicking_foot_strike",
    "kicking_foot_swing",
    "kick_pre_urgency",
    "premature_kick_lunge",
    "support_foot_clear",
    "support_foot_planted",
  ):
    base_cfg.rewards.pop(name, None)

  if "base_height" in base_cfg.rewards:
    base_cfg.rewards["base_height"].weight = -12.0
    base_cfg.rewards["base_height"].params["target_height"] = _TRUNK_HEIGHT_TARGET
  if "orientation" in base_cfg.rewards:
    base_cfg.rewards["orientation"].weight = -10.0

  base_cfg.rewards["trunk_height_floor"] = RewardTermCfg(
    func=kick_mdp.trunk_height_floor,
    weight=-8.0,
    params={"minimum_height": _TRUNK_HEIGHT_MIN, "asset_cfg": trunk},
  )

  # --- Paper kick recipe: approach / align / kick cosine / settle ---
  # Tracking / feet_swing: invert farm — full near plant, weak far (no keep-out band).

  _plant_walk = {
    "plant_full_dist": 0.6,
    "plant_far_dist": 2.0,
    "plant_far_scale": 0.15,
    "restore_tracking_after_kick": True,
    "goal_command_name": "goal",
    # Student tracking uses the same robot→ball twist as the teacher.
    "align_robot_ball": True,
    "cruise_speed": 0.7,
    "min_speed": 0.25,
    "slow_distance": 1.0,
    "plant_distance": 0.20,
    "turn_speed": 1.0,
    "heading_deadzone": 0.05,
    "use_sampled_magnitudes": True,
    **{k: v for k, v in goal_params.items() if k != "command_name"},
  }

  # Replace BaseWalk tracking with plant-proximity-scaled versions.
  _tracking_replacements = {
    "tracking_lin_vel_x": (kick_mdp.track_lin_vel_axis_for_kick, {"axis": 0}),
    "tracking_lin_vel_y": (kick_mdp.track_lin_vel_axis_for_kick, {"axis": 1}),
    "tracking_ang_vel": (kick_mdp.track_ang_vel_z_for_kick, {}),
  }
  for name, (func, extra) in _tracking_replacements.items():
    if name not in base_cfg.rewards:
      continue
    term = base_cfg.rewards[name]
    weight = {
      "tracking_lin_vel_x": 1.5,
      "tracking_lin_vel_y": 1.5,
      "tracking_ang_vel": 1.0,
    }[name]
    base_cfg.rewards[name] = RewardTermCfg(
      func=func,
      weight=weight,
      params={**term.params, "ball_cfg": ball, **_plant_walk, **extra},
    )

  # Soften foot/knee regularizers only in Setup/Strike so a kick swing is allowed.
  # Plant invert only on feet_swing (positive farm); placement penalties stay un-inverted
  # so far-away gait isn't under-regularized.
  _walk_pref = {
    **{k: v for k, v in goal_params.items() if k != "command_name"},
    "goal_command_name": "goal",
  }
  _placement_scales = {
    "arc_scale": 1.0,
    "setup_scale": 0.25,
    "strike_scale": 0.0,
    "plant_full_dist": None,
  }
  _swing_scales = {
    "arc_scale": 1.0,
    "setup_scale": 0.15,
    "strike_scale": 0.0,
    "near_ball_dist": None,
    "near_ball_scale": 1.0,
    **{
      k: _plant_walk[k]
      for k in (
        "plant_full_dist",
        "plant_far_dist",
        "plant_far_scale",
        "restore_tracking_after_kick",
      )
    },
  }

  _knee_scales = {
    "arc_scale": 1.0,
    "setup_scale": 0.25,
    "strike_scale": 0.0,
    "plant_full_dist": None,
  }
  _phase_walk_replacements = {
    "feet_swing": (kick_mdp.feet_swing_for_kick, _swing_scales),
    "feet_offset_x": (kick_mdp.feet_offset_x_for_kick, _placement_scales),
    "feet_offset_y": (kick_mdp.feet_offset_y_for_kick, _placement_scales),
    "feet_distance": (kick_mdp.feet_distance_for_kick, _placement_scales),
    "feet_yaw_diff": (kick_mdp.feet_yaw_diff_for_kick, _placement_scales),
    "feet_yaw_mean": (kick_mdp.feet_yaw_mean_for_kick, _placement_scales),
    "knee_flex_cmd_excess": (kick_mdp.knee_flex_cmd_excess_for_kick, _knee_scales),
  }
  for name, (func, scales) in _phase_walk_replacements.items():
    if name not in base_cfg.rewards:
      continue
    term = base_cfg.rewards[name]
    base_cfg.rewards[name] = RewardTermCfg(
      func=func,
      weight=term.weight,
      params={**term.params, **_walk_pref, **scales},
    )

  # Drop complex anti-farm / magnet terms if present from older recipes.
  # Also drop terms that conflict with the paper approach/kick/settle trio.
  for name in (
    "pref_pose",
    "pref_pose_velocity",
    "swing_foot_proximity",
    "swing_foot_velocity",
    "loiter_stage",
    "premature_ball_contact",
    "ball_not_moving",
    "ball_avoidance",
    "both_feet_near_ball",
    "stance_foot_clear",
    "kick_heading",
    "post_kick_chase",
    # Conflicts with paper trio:
    "approach_ball",  # stand-still Gaussian vs agent_approach_ball
    "approach_plant_vel",  # plant offset vs agent→ball direction
    "ball_velocity_toward_goal",  # projected speed vs ball_approach_target cosine
  ):
    base_cfg.rewards.pop(name, None)

  # Paper trio: approach → kick align → settle near target.
  # Twist teacher still steers tracking_* toward plant (no separate plant-vel reward).
  base_cfg.rewards["agent_approach_ball"] = RewardTermCfg(
    func=kick_mdp.agent_approach_ball,
    weight=2.0,
    params={"velocity_eps": 0.1, "command_name": "goal", **robot_ball},
  )

  # Align: face-ball disabled (was farmable from outside the plant).
  base_cfg.rewards.pop("body_face_ball", None)

  # Kick: cosine ball vel ↔ goal (main payday; [0,1] so weight carries scale).
  base_cfg.rewards["ball_approach_target"] = RewardTermCfg(
    func=kick_mdp.ball_approach_target,
    weight=8.0,
    params={"velocity_eps": 0.1, "command_name": "goal", "ball_cfg": ball},
  )
  base_cfg.rewards["ball_acceleration_toward_goal"] = RewardTermCfg(
    func=kick_mdp.ball_acceleration_toward_goal,
    weight=2.0,
    params={"command_name": "goal", "ball_cfg": ball},
  )
  # Sparse settle after kick window + stagnant ball.
  base_cfg.rewards["target_reached"] = RewardTermCfg(
    func=kick_mdp.target_reached,
    weight=5.0,
    params={
      "contact_window_s": _POST_KICK_WINDOW_S,
      "velocity_eps": 0.1,
      "std": 1.0,
      "command_name": "goal",
      "ball_cfg": ball,
    },
  )

  # 4) Balance after a hard kick: upright × walk height.
  base_cfg.rewards["post_kick_upright"] = RewardTermCfg(
    func=kick_mdp.post_kick_upright,
    weight=2.0,
    params={
      "asset_cfg": trunk,
      "ball_cfg": ball,
      "contact_window_s": _POST_KICK_STABILITY_S,
      "min_kick_speed": _MIN_KICK_SPEED,
      "target_height": _TRUNK_HEIGHT_TARGET,
      "height_sigma": 0.08,
      "sigma": 0.20,
    },
  )

  # 5) No dribble / weak nudge (near ball, moving but not toward goal).
  _NEAR_BALL = _PREF["setup_exit_dist"]
  base_cfg.rewards["ball_dribble_penalty"] = RewardTermCfg(
    func=kick_mdp.ball_dribble_penalty,
    weight=-8.0,
    params={
      "min_kick_speed": _KICK_REWARD_GATE_SPEED,
      "dribble_speed": 0.15,
      "kick_phase_robot_ball_distance": _NEAR_BALL,
      **robot_ball,
    },
  )

  # Waiting near the ball without kicking (still stands pay more).
  base_cfg.rewards["near_ball_wait"] = RewardTermCfg(
    func=kick_mdp.near_ball_wait_penalty,
    weight=-4.0,
    params={
      "near_ball_distance": 1.0,
      "ramp_tau_s": 1.0,
      "max_scale": 3.0,
      "robot_still_speed": 0.25,
      **robot_ball,
    },
  )

  if "collision" in base_cfg.rewards:
    base_cfg.rewards["collision"].weight = -1.0

  # Terminations: time_out / fell_over / root_height come from BaseWalk.
  # Target hit/missed + double touch follow the kick episode logic.
  base_cfg.terminations.pop("kick_success", None)
  base_cfg.terminations["target_hit"] = TerminationTermCfg(
    func=target_hit,
    time_out=True,
    params={
      "target_radius": _TARGET_RADIUS,
      "command_name": "goal",
      "ball_cfg": ball,
      "robot_cfg": robot,
    },
  )
  base_cfg.terminations["target_missed"] = TerminationTermCfg(
    func=target_missed,
    time_out=False,
    params={
      "target_radius": _TARGET_RADIUS,
      "post_kick_window_s": _POST_KICK_WINDOW_S,
      "command_name": "goal",
      "ball_cfg": ball,
      "robot_cfg": robot,
    },
  )
  base_cfg.terminations["double_touch"] = TerminationTermCfg(
    func=double_touch,
    time_out=False,
    params={
      "post_kick_window_s": _DOUBLE_TOUCH_WINDOW_S,
      "command_name": "goal",
      "ball_cfg": ball,
      "robot_cfg": robot,
    },
  )
  # Near-ball pressure: loiter <1 m without kick → episode ends (anti length-farm).
  base_cfg.terminations["near_ball_no_kick"] = TerminationTermCfg(
    func=kick_mdp.near_ball_no_kick_timeout,
    time_out=False,
    params={
      "max_near_time_s": 2.5,
      "near_ball_distance": 1.0,
      "command_name": "goal",
      "ball_cfg": ball,
      "robot_cfg": robot,
    },
  )

  base_cfg.curriculum["spawn_radius"] = CurriculumTermCfg(
    func=kick_mdp.approach_spawn_radius_curriculum,
    params={
      "event_name": "reset_base",
      # Start nearer (kick discoverability), expand to full approach range.
      "start_radius": (0.8, 1.5),
      "end_radius": (2.0, 3.0),
      "start_step": 0,
      "end_step": 20_000,
    },
  )

  base_cfg.episode_length_s = 25.0
  if base_cfg.sim.nconmax is not None:
    base_cfg.sim.nconmax = max(base_cfg.sim.nconmax, base_cfg.sim.nconmax + 20)

  return base_cfg


def make_approach_only_env_cfg(base_cfg: ManagerBasedRlEnvCfg) -> ManagerBasedRlEnvCfg:
  """Stage-1 curriculum: approach / orbit the ball only (no kick payday).

  Twist + rewards target the behind-ball waypoint (orbit when wrong-side).
  Keep-out stops ball touch; success is holding near the ball outside keep-out.
  Full-annulus spawn so wrong-side starts must circle.
  """
  from mjlab.managers.reward_manager import RewardTermCfg
  from mjlab.managers.scene_entity_config import SceneEntityCfg
  from mjlab.managers.termination_manager import TerminationTermCfg
  from mjlab.tasks.kick import mdp as kick_mdp
  from mjlab.tasks.kick.mdp.terminations import near_ball_reached

  cfg = make_arc_kick_env_cfg(base_cfg)
  robot = SceneEntityCfg("robot")
  ball = SceneEntityCfg("ball")
  # Plant: pelvis 0.15 m behind, 0.08–0.12 m off-axis. Keep-out 9 cm
  # (0.09; 0.9 m would sit in front of the plant). After latch, yellow
  # collapses onto the ball (lateral stays) and keep-out releases.
  keepout_m = 0.09
  standoff_m = 0.15
  ready_wp_m = 0.15
  finish_band_m = 0.25

  # No kick / settle / anti-loiter-without-kick pressure.
  for name in (
    "ball_approach_target",
    "ball_acceleration_toward_goal",
    "target_reached",
    "post_kick_upright",
    "ball_dribble_penalty",
    "near_ball_wait",
  ):
    cfg.rewards.pop(name, None)

  for name in (
    "target_hit",
    "target_missed",
    "double_touch",
    "near_ball_no_kick",
  ):
    cfg.terminations.pop(name, None)

  # Align with orbit teacher (not radial agent→ball — that fights circling).
  cfg.rewards.pop("agent_approach_ball", None)
  cfg.rewards["waypoint_approach"] = RewardTermCfg(
    func=kick_mdp.waypoint_approach_velocity,
    weight=5.0,
    params={
      "target_distance": standoff_m,
      "command_name": "goal",
      "activate_ball_distance": None,
      "activate_waypoint_distance": ready_wp_m,
      "velocity_eps": 0.1,
      "use_cosine": True,
      "robot_cfg": robot,
      "ball_cfg": ball,
    },
  )
  # Position × facing: on the waypoint and lined up with ball→goal.
  cfg.rewards["waypoint_proximity"] = RewardTermCfg(
    func=kick_mdp.behind_ball_waypoint,
    weight=5.0,
    params={
      "target_distance": standoff_m,
      "std": 0.22,
      "facing_std": 0.40,
      "command_name": "goal",
      "robot_cfg": robot,
      "ball_cfg": ball,
    },
  )
  # Long-range finish pressure: 1/(1+d) still differs 1.2 m vs 0.32 m.
  cfg.rewards["waypoint_inv_distance"] = RewardTermCfg(
    func=kick_mdp.behind_ball_inv_distance,
    weight=3.0,
    params={
      "target_distance": standoff_m,
      "command_name": "goal",
      "robot_cfg": robot,
      "ball_cfg": ball,
    },
  )
  # Finish band around the ball (outside touch keep-out).
  cfg.rewards["ball_proximity"] = RewardTermCfg(
    func=kick_mdp.ball_distance_band,
    weight=2.0,
    params={
      "min_distance": keepout_m,
      "max_distance": finish_band_m,
      "robot_cfg": robot,
      "ball_cfg": ball,
    },
  )
  cfg.rewards["ball_touch_keepout"] = RewardTermCfg(
    func=kick_mdp.ball_touch_keepout_penalty,
    weight=-8.0,
    params={
      "keepout_distance": keepout_m,
      "contact_cost": 1.0,
      "release_when_planted": True,
      "robot_cfg": robot,
      "ball_cfg": ball,
    },
  )
  cfg.rewards["ball_velocity_toward_goal"] = RewardTermCfg(
    func=kick_mdp.ball_velocity_toward_goal,
    weight=4.0,
    params={
      "command_name": "goal",
      "ball_cfg": ball,
      "max_reward": 6.0,
      "use_decay": False,
      "require_plant_latch": True,
    },
  )
  cfg.rewards["kicking_foot_strike"] = RewardTermCfg(
    func=kick_mdp.kicking_foot_strike_ball,
    weight=2.0,
    params={
      "command_name": "goal",
      "target_distance": standoff_m,
      "activate_inside_ball_distance": 1.0,
      "require_kick_ready": False,
      "require_plant_latch": True,
      "robot_cfg": robot,
      "ball_cfg": ball,
    },
  )
  # Light FOV insurance (75% of 105° HFOV ≈ ±0.69 rad).
  cfg.rewards["ball_camera_cone"] = RewardTermCfg(
    func=kick_mdp.ball_camera_cone,
    weight=0.5,
    params={
      "soft_limit": 0.69,
      "sigma": 0.25,
      "robot_cfg": robot,
      "ball_cfg": ball,
    },
  )

  # Stronger fall / tip penalties (higher speed orbit).
  if "orientation" in cfg.rewards:
    cfg.rewards["orientation"].weight = -20.0
  if "base_height" in cfg.rewards:
    cfg.rewards["base_height"].weight = -18.0
  if "trunk_height_floor" in cfg.rewards:
    cfg.rewards["trunk_height_floor"].weight = -14.0
  if "ang_vel_xy" in cfg.rewards:
    cfg.rewards["ang_vel_xy"].weight = -0.6
  if "survival" in cfg.rewards:
    cfg.rewards["survival"].weight = 0.15

  # Success: ball [keepout, 0.50] OR within 0.12 m of the close waypoint.
  cfg.terminations["near_ball_reached"] = TerminationTermCfg(
    func=near_ball_reached,
    time_out=True,
    params={
      "near_ball_distance": finish_band_m,
      "min_keepout_distance": keepout_m,
      "max_waypoint_distance": 0.12,
      "approach_standoff": standoff_m,
      "command_name": "goal",
      "min_time_s": 0.5,
      "robot_cfg": robot,
      "ball_cfg": ball,
    },
  )

  # Paper annulus + full 360° (learn to orbit when spawned on the goal side).
  cfg.events["reset_base"].params["radius_range"] = (0.4, 4.0)
  cfg.events["reset_base"].params["spawn_on_approach_side"] = False
  # Spawn-side plant: yellow marker 0.08–0.12 m off-axis (hip half-width ~0.095).
  cfg.events["reset_base"].params["waypoint_lateral_range"] = (0.08, 0.12)

  # Orbit teacher: path-facing + FOV clamp; creep through plant (no freeze).
  _orbit = {
    "orbit_to_approach": True,
    "goal_command_name": "goal",
    "approach_standoff": standoff_m,
    "ready_waypoint_distance": ready_wp_m,
    "plant_distance": keepout_m,
    "plant_full_dist": 0.6,
    "plant_far_dist": 1.5,
    # Full tracking/gait credit at range — 0.5 was soft-pedaling the teacher at ~1.5 m.
    "plant_far_scale": 1.0,
    "cruise_speed": 1.35,
    "min_speed": 0.55,
    "slow_distance": 0.45,
    "turn_speed": 1.2,
    "face_path_fov_clip": True,
    "fov_half_angle": 0.69,
    "yaw_gain": 2.0,
    "heading_deadzone": 0.05,
    "creep_through_plant": True,
    "creep_speed": 0.25,
  }
  if "pref_pose_twist" in cfg.events:
    cfg.events["pref_pose_twist"].params.update(
      {
        k: _orbit[k]
        for k in (
          "orbit_to_approach",
          "goal_command_name",
          "approach_standoff",
          "ready_waypoint_distance",
          "plant_distance",
          "cruise_speed",
          "min_speed",
          "slow_distance",
          "turn_speed",
          "face_path_fov_clip",
          "fov_half_angle",
          "yaw_gain",
          "heading_deadzone",
          "creep_through_plant",
          "creep_speed",
        )
      }
    )
  for name in ("tracking_lin_vel_x", "tracking_lin_vel_y", "tracking_ang_vel"):
    if name in cfg.rewards:
      cfg.rewards[name].params.update(_orbit)
  # Same plant invert on feet_swing so far gait isn't still soft-pedaled at 0.15.
  if "feet_swing" in cfg.rewards:
    cfg.rewards["feet_swing"].params.update(
      {
        "plant_full_dist": _orbit["plant_full_dist"],
        "plant_far_dist": _orbit["plant_far_dist"],
        "plant_far_scale": _orbit["plant_far_scale"],
      }
    )

  if "spawn_radius" in cfg.curriculum:
    cfg.curriculum["spawn_radius"].params.update(
      {
        "start_radius": (0.4, 4.0),
        "end_radius": (0.4, 4.0),
        "start_step": 0,
        "end_step": 1,
      }
    )

  cfg.commands["goal"].approach_standoff = standoff_m
  cfg.episode_length_s = 15.0
  return cfg


def make_near_kick_env_cfg(base_cfg: ManagerBasedRlEnvCfg) -> ManagerBasedRlEnvCfg:
  """Stage-2: near-ball kick discovery (plant → strike → recover).

  Spawn one step outside the plant box. Reward support-foot plant
  (beside/behind ball), gate contact bridge on plant score, shape instep
  ankle at contact, then post-kick upright + standing feet.
  """
  from mjlab.managers.reward_manager import RewardTermCfg
  from mjlab.managers.scene_entity_config import SceneEntityCfg
  from mjlab.managers.termination_manager import TerminationTermCfg
  from mjlab.tasks.kick import mdp as kick_mdp
  from mjlab.tasks.kick.mdp.terminations import (
    double_touch,
    target_hit,
    target_missed,
  )

  cfg = make_approach_only_env_cfg(base_cfg)
  robot = SceneEntityCfg("robot")
  ball = SceneEntityCfg("ball")
  trunk = SceneEntityCfg("robot", body_names=("Trunk",))
  robot_ball = {"robot_cfg": robot, "ball_cfg": ball}

  # Preserve the finished approach policy's complete reward landscape.
  # Alignment latch enables kick outcome; keep-out is removed so it cannot
  # shove the robot back before plant.
  cfg.terminations.pop("near_ball_reached", None)

  # No explicit planting stage: alignment unlocks a straight-through strike.
  cfg.rewards.pop("support_plant_score", None)
  cfg.rewards["kicking_foot_strike"] = RewardTermCfg(
    func=kick_mdp.kicking_foot_strike_ball,
    weight=2.0,
    params={
      "activate_inside_ball_distance": 0.85,
      "target_distance": 0.35,
      "command_name": "goal",
      "require_kick_ready": False,
      "require_plant_latch": True,
      "proximity_sigma": 0.30,
      "proximity_gated_speed": True,
      **robot_ball,
    },
  )
  for name in (
    "feet_swing",
    "knee_flex_cmd_excess",
    "feet_offset_x",
    "feet_offset_y",
  ):
    cfg.rewards[name].params["disable_when_planted"] = True
  # Ball-attached target (standoff 0, no lateral). Pay closing
  # speed, not a static stand-off magnet.
  cfg.rewards["waypoint_approach"].params.update(
    {
      "target_distance": 0.0,
      "use_cosine": False,
      "activate_waypoint_distance": None,
      "activate_ball_distance": None,
      "facing_std": 0.40,
      "stop_after_plant_latch": True,
    }
  )
  cfg.rewards["waypoint_proximity"].params.update(
    {
      "target_distance": 0.0,
      "progress": True,
      "facing_std": 0.40,
      "stop_after_plant_latch": True,
    }
  )
  cfg.rewards["waypoint_inv_distance"].params.update(
    {
      "target_distance": 0.0,
      "progress": True,
      "stop_after_plant_latch": True,
    }
  )
  # One-shot lure onto the latch; waypoint terms stay off afterward.
  cfg.rewards["plant_latch_bonus"] = RewardTermCfg(
    func=kick_mdp.plant_latch_arrival_bonus,
    weight=3.0,
  )
  cfg.rewards["orientation"].weight = -18.0
  cfg.rewards["base_height"].weight = -14.0
  cfg.rewards["wrong_ball_contact"] = RewardTermCfg(
    func=kick_mdp.wrong_ball_contact_penalty,
    weight=-4.0,
    params=robot_ball,
  )

  # Yellow sits on the ball (no standoff, no lateral). Face kick-axis in
  # the close zone; do not recycle last vx.
  _plant_twist = {
    "orbit_to_plant_box": False,
    "orbit_to_approach": True,
    "creep_through_plant": True,
    "creep_speed": 0.25,
    "plant_root_behind": 0.10,
    "plant_root_lateral": 0.0,
    "plant_feet_offset_x": -0.02,
    "plant_feet_offset_y": 0.12,
    "ready_waypoint_distance": 0.22,
    "slow_distance": 0.80,
    "cruise_speed": 0.9,
    "min_speed": 0.30,
    "face_path_fov_clip": True,
    "use_sampled_magnitudes": False,
    "approach_standoff": 0.0,
    "plant_distance": 0.22,
  }
  for name in ("tracking_lin_vel_x", "tracking_lin_vel_y", "tracking_ang_vel"):
    if name in cfg.rewards:
      cfg.rewards[name].params.update(_plant_twist)
  if "pref_pose_twist" in cfg.events:
    cfg.events["pref_pose_twist"].params.update(
      {
        **_plant_twist,
        "ready_facing_angle": math.radians(20.0),
        "ready_hold_time_s": 0.05,
      }
    )

  # Main payday dominates shaping: a visually plausible swing without ball
  # speed is not a successful kick.
  for name in (
    "kick_contact_bridge",
    "strike_ankle_pitch",
    "premature_kick_lunge",
    "ball_approach_target",
    "ball_acceleration_toward_goal",
    "target_reached",
    "post_kick_stance",
    "near_ball_wait",
    "ball_touch_keepout",
    "ball_proximity",
  ):
    cfg.rewards.pop(name, None)
  cfg.rewards["ball_velocity_toward_goal"] = RewardTermCfg(
    func=kick_mdp.ball_velocity_toward_goal,
    weight=4.0,
    params={
      "command_name": "goal",
      "ball_cfg": ball,
      "max_reward": 6.0,
      "use_decay": False,
      "require_plant_latch": True,
    },
  )
  cfg.rewards["kick_direction_accuracy"] = RewardTermCfg(
    func=kick_mdp.kick_direction_accuracy_window,
    weight=2.0,
    params={
      "command_name": "goal",
      "ball_cfg": ball,
      "robot_cfg": robot,
      "window_s": 0.30,
      "angle_sigma": 0.25,
    },
  )
  cfg.rewards["kick_speed_loose"] = RewardTermCfg(
    func=kick_mdp.kick_speed_match_window,
    weight=2.0,
    params={
      "command_name": "goal",
      "ball_cfg": ball,
      "robot_cfg": robot,
      "window_s": 0.30,
      "relative_sigma": 0.35,
    },
  )
  cfg.rewards["kick_speed_tight"] = RewardTermCfg(
    func=kick_mdp.kick_speed_match_window,
    weight=2.0,
    params={
      "command_name": "goal",
      "ball_cfg": ball,
      "robot_cfg": robot,
      "window_s": 0.30,
      "relative_sigma": 0.12,
    },
  )
  # Balance after a real kick (≥1.2 m/s toward goal).
  cfg.rewards["post_kick_upright"] = RewardTermCfg(
    func=kick_mdp.post_kick_upright,
    weight=2.0,
    params={
      "asset_cfg": trunk,
      "ball_cfg": ball,
      "contact_window_s": 1.5,
      "min_kick_speed": _KICK_REWARD_GATE_SPEED,
      "target_height": _TRUNK_HEIGHT_TARGET,
      "height_sigma": 0.08,
      "sigma": 0.20,
    },
  )
  cfg.rewards["ball_dribble_penalty"] = RewardTermCfg(
    func=kick_mdp.ball_dribble_penalty,
    weight=-2.0,
    params={
      "min_kick_speed": _KICK_REWARD_GATE_SPEED,
      "dribble_speed": 0.15,
      "kick_phase_robot_ball_distance": _PREF["setup_exit_dist"],
      **robot_ball,
    },
  )
  cfg.terminations["target_hit"] = TerminationTermCfg(
    func=target_hit,
    time_out=True,
    params={
      "target_radius": _TARGET_RADIUS,
      "command_name": "goal",
      "ball_cfg": ball,
      "robot_cfg": robot,
    },
  )
  cfg.terminations["target_missed"] = TerminationTermCfg(
    func=target_missed,
    time_out=False,
    params={
      "target_radius": _TARGET_RADIUS,
      "post_kick_window_s": _POST_KICK_WINDOW_S,
      "command_name": "goal",
      "ball_cfg": ball,
      "robot_cfg": robot,
    },
  )
  cfg.terminations["double_touch"] = TerminationTermCfg(
    func=double_touch,
    time_out=False,
    params={
      "post_kick_window_s": _DOUBLE_TOUCH_WINDOW_S,
      "command_name": "goal",
      "ball_cfg": ball,
      "robot_cfg": robot,
    },
  )
  cfg.terminations["near_ball_no_kick"] = TerminationTermCfg(
    func=kick_mdp.near_ball_no_kick_timeout,
    time_out=False,
    params={
      "max_near_time_s": 5.0,
      "near_ball_distance": 1.0,
      "command_name": "goal",
      "ball_cfg": ball,
      "robot_cfg": robot,
    },
  )

  # Slightly outside plant box — one step into plant, then strike.
  cfg.events["reset_base"].params["radius_range"] = (0.50, 0.70)
  cfg.events["reset_base"].params["spawn_on_approach_side"] = True
  cfg.events["reset_base"].params["approach_spread"] = math.pi / 4.0
  # Yellow on the ball; kick with the spawn-closer foot.
  cfg.events["reset_base"].params["waypoint_lateral_range"] = (0.0, 0.0)
  cfg.events["reset_base"].params["fixed_kick_side"] = None
  goal = cfg.commands["goal"]
  assert isinstance(goal, UniformGoalPositionCommandCfg)
  goal.distance_range = (8.0, 12.0)
  goal.approach_standoff = 0.0
  goal.collapse_waypoint_when_planted = True
  if "spawn_radius" in cfg.curriculum:
    cfg.curriculum["spawn_radius"].params.update(
      {
        "start_radius": (0.50, 0.70),
        "end_radius": (0.50, 0.70),
        "start_step": 0,
        "end_step": 1,
      }
    )

  # Short horizon: plant + strike quickly; loitering is costly (wait penalty).
  cfg.episode_length_s = 7.0
  return cfg

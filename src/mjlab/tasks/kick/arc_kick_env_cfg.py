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
_POST_KICK_STABILITY_S = 1.0
_TARGET_RADIUS = 1.0  # metres — ball stopped inside this of goal = hit
_POST_KICK_WINDOW_S = 2.0  # T_window for target miss / settle
_DOUBLE_TOUCH_WINDOW_S = 1.0  # T_window for illegal re-contact
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
      restitution=0.0,
      friction=(1.0, 0.5, 0.015),
    )
  )
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
    weight = {"tracking_lin_vel_x": 1.5, "tracking_lin_vel_y": 1.5, "tracking_ang_vel": 1.0}[
      name
    ]
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
    **{k: _plant_walk[k] for k in (
      "plant_full_dist",
      "plant_far_dist",
      "plant_far_scale",
      "restore_tracking_after_kick",
    )},
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
  keepout_m = 0.3
  standoff_m = 0.40

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
    weight=4.0,
    params={
      "target_distance": standoff_m,
      "command_name": "goal",
      "activate_ball_distance": None,
      "activate_waypoint_distance": 0.20,
      "velocity_eps": 0.1,
      "use_cosine": True,
      "robot_cfg": robot,
      "ball_cfg": ball,
    },
  )
  # Sharp Gaussian — at 1.2 m this is ~e^{-11} with std=0.8, now bites.
  cfg.rewards["waypoint_proximity"] = RewardTermCfg(
    func=kick_mdp.behind_ball_waypoint,
    weight=4.0,
    params={
      "target_distance": standoff_m,
      "std": 0.35,
      "command_name": "goal",
      "robot_cfg": robot,
      "ball_cfg": ball,
    },
  )
  # Long-range finish pressure: 1/(1+d) still differs 1.2 m vs 0.4 m.
  cfg.rewards["waypoint_inv_distance"] = RewardTermCfg(
    func=kick_mdp.behind_ball_inv_distance,
    weight=2.0,
    params={
      "target_distance": standoff_m,
      "command_name": "goal",
      "robot_cfg": robot,
      "ball_cfg": ball,
    },
  )
  # Soft finish band around the ball (outside touch keep-out).
  cfg.rewards["ball_proximity"] = RewardTermCfg(
    func=kick_mdp.ball_distance_band,
    weight=2.0,
    params={
      "min_distance": keepout_m,
      "max_distance": 0.80,
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

  # Soft success: ball [0.3, 0.8] OR within 0.35 m of approach waypoint.
  cfg.terminations["near_ball_reached"] = TerminationTermCfg(
    func=near_ball_reached,
    time_out=True,
    params={
      "near_ball_distance": 0.80,
      "min_keepout_distance": keepout_m,
      "max_waypoint_distance": 0.35,
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

  # Orbit teacher: path-facing + FOV clamp; faster cruise for bigger steps.
  _orbit = {
    "orbit_to_approach": True,
    "goal_command_name": "goal",
    "approach_standoff": standoff_m,
    "ready_waypoint_distance": 0.20,
    "plant_distance": keepout_m,
    "plant_full_dist": 0.6,
    "plant_far_dist": 1.5,
    # Full tracking/gait credit at range — 0.5 was soft-pedaling the teacher at ~1.5 m.
    "plant_far_scale": 1.0,
    "cruise_speed": 1.1,
    "min_speed": 0.40,
    "slow_distance": 0.8,
    "turn_speed": 1.2,
    "face_path_fov_clip": True,
    "fov_half_angle": 0.69,
    "yaw_gain": 2.0,
    "heading_deadzone": 0.05,
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

  # Unlock touch / hover-band (approach keep-out fights kicking).
  cfg.rewards.pop("ball_touch_keepout", None)
  cfg.rewards.pop("ball_proximity", None)
  cfg.rewards.pop("agent_approach_ball", None)
  cfg.terminations.pop("near_ball_reached", None)

  # Soften approach shaping; keep it until near the plant box (~0.4 m).
  _kick_zone_m = 0.40
  if "waypoint_approach" in cfg.rewards:
    cfg.rewards["waypoint_approach"].weight = 0.5
    cfg.rewards["waypoint_approach"].params["inactive_inside_ball_distance"] = (
      _kick_zone_m
    )
  if "waypoint_proximity" in cfg.rewards:
    cfg.rewards["waypoint_proximity"].weight = 0.75
    cfg.rewards["waypoint_proximity"].params["inactive_inside_ball_distance"] = (
      _kick_zone_m
    )
  if "waypoint_inv_distance" in cfg.rewards:
    cfg.rewards["waypoint_inv_distance"].weight = 0.75
    cfg.rewards["waypoint_inv_distance"].params["inactive_inside_ball_distance"] = (
      _kick_zone_m
    )
  for name in ("tracking_lin_vel_x", "tracking_lin_vel_y", "tracking_ang_vel"):
    if name in cfg.rewards:
      cfg.rewards[name].weight = 0.5
      cfg.rewards[name].params["inactive_inside_ball_distance"] = _kick_zone_m

  # Plant → strike: steep sagittal-closing plant (product funnel), soft bridge.
  _plant = {
    "sagittal_target": 0.14,
    "sagittal_sigma": 0.12,
    "lateral_target": 0.175,
    "lateral_sigma": 0.08,
    "sagittal_funnel": 0.12,
    "lateral_funnel": 0.10,
    "funnel_weight": 0.55,
    "command_name": "goal",
  }
  cfg.rewards["support_plant_score"] = RewardTermCfg(
    func=kick_mdp.support_plant_score,
    weight=8.0,
    params={
      "activate_inside_ball_distance": 1.2,
      **_plant,
      **robot_ball,
    },
  )
  cfg.rewards["kick_contact_bridge"] = RewardTermCfg(
    func=kick_mdp.kick_contact_bridge,
    weight=5.0,
    params={
      "activate_inside_ball_distance": 0.85,
      "closing_scale": 0.15,
      "contact_bonus": 3.0,
      "impulse_scale": 4.0,
      "max_impulse": 3.0,
      "impulse_contact_eps": 0.05,
      "min_plant_score": 0.15,
      "plant_gate_power": 1.0,
      "max_closing_speed": 2.0,
      **_plant,
      **robot_ball,
    },
  )
  cfg.rewards["strike_ankle_pitch"] = RewardTermCfg(
    func=kick_mdp.strike_ankle_pitch,
    weight=2.0,
    params={
      "target_pitch": -0.50,
      "pitch_sigma": 0.15,
      "command_name": "goal",
      **robot_ball,
    },
  )

  # Soften anti-lunge so closing into the plant box is not over-punished.
  cfg.rewards["premature_kick_lunge"] = RewardTermCfg(
    func=kick_mdp.premature_kick_lunge_penalty,
    weight=-1.5,
    params={
      "target_distance": 0.35,
      "command_name": "goal",
      "kick_ready_threshold": 0.40,
      **robot_ball,
    },
  )
  # Planted support foot while near the ball (still / on ground).
  cfg.rewards["support_foot_planted"] = RewardTermCfg(
    func=kick_mdp.support_foot_planted,
    weight=2.0,
    params={
      "activate_inside_ball_distance": 0.85,
      "target_distance": 0.35,
      "command_name": "goal",
      "require_kick_ready": False,
      "kick_ready_threshold": 0.40,
      **robot_ball,
    },
  )

  # Gait placement off during strike; keep light crouch-runaway tax.
  for name in (
    "feet_swing",
    "feet_offset_x",
    "feet_offset_y",
    "feet_distance",
  ):
    if name in cfg.rewards:
      cfg.rewards[name].weight = 0.0
  if "knee_flex_cmd_excess" in cfg.rewards:
    cfg.rewards["knee_flex_cmd_excess"].weight = -1.0

  if "action_rate" in cfg.rewards:
    cfg.rewards["action_rate"].weight = -1.0

  # Walk-height posture: crouch / collapse is expensive; mid-strike lean is softer.
  if "orientation" in cfg.rewards:
    cfg.rewards["orientation"].weight = -6.0
  if "base_height" in cfg.rewards:
    cfg.rewards["base_height"].weight = -10.0
    cfg.rewards["base_height"].params["target_height"] = _TRUNK_HEIGHT_TARGET
  if "trunk_height_floor" in cfg.rewards:
    cfg.rewards["trunk_height_floor"].weight = -8.0
    cfg.rewards["trunk_height_floor"].params["minimum_height"] = _TRUNK_HEIGHT_MIN
  # Dive kills were ending eps in ~0.25 s before any kick — rely on fell_over only.
  cfg.terminations.pop("root_height", None)
  if "fell_over" in cfg.terminations:
    cfg.terminations["fell_over"].params["limit_angle"] = math.radians(85.0)

  # Approach-side drive to plant, then creep toward ball (no standstill catch).
  _plant_twist = {
    "orbit_to_plant_box": True,
    "orbit_to_approach": False,
    "creep_through_plant": True,
    "creep_speed": 0.25,
    "plant_root_behind": 0.22,
    "plant_root_lateral": 0.10,
    "plant_feet_offset_x": -0.02,
    "plant_feet_offset_y": 0.12,
    "ready_waypoint_distance": 0.15,
    "slow_distance": 0.45,
    "cruise_speed": 0.9,
    "min_speed": 0.30,
    "face_path_fov_clip": True,
    "approach_standoff": 0.22,
    "plant_distance": 0.22,
  }
  for name in ("tracking_lin_vel_x", "tracking_lin_vel_y", "tracking_ang_vel"):
    if name in cfg.rewards:
      cfg.rewards[name].params.update(_plant_twist)
  if "pref_pose_twist" in cfg.events:
    cfg.events["pref_pose_twist"].params.update(_plant_twist)

  # Main payday: clip(v·d̂, 0, 6); aux direction gated at 0.25 m/s.
  cfg.rewards["ball_velocity_toward_goal"] = RewardTermCfg(
    func=kick_mdp.ball_velocity_toward_goal,
    weight=4.0,
    params={
      "command_name": "goal",
      "ball_cfg": ball,
      "max_reward": 6.0,
      "use_decay": False,
    },
  )
  cfg.rewards["ball_approach_target"] = RewardTermCfg(
    func=kick_mdp.ball_approach_target,
    weight=1.5,
    params={
      "velocity_eps": 0.25,
      "command_name": "goal",
      "ball_cfg": ball,
    },
  )
  cfg.rewards["ball_acceleration_toward_goal"] = RewardTermCfg(
    func=kick_mdp.ball_acceleration_toward_goal,
    weight=4.0,
    params={"command_name": "goal", "ball_cfg": ball},
  )
  cfg.rewards["target_reached"] = RewardTermCfg(
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
  # Balance after any real kick (≥1.2 m/s toward goal): upright × walk height.
  cfg.rewards["post_kick_upright"] = RewardTermCfg(
    func=kick_mdp.post_kick_upright,
    weight=5.0,
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
  # Standing recovery: feet close (~0.19 m) + soles flat (roll/pitch ~0).
  feet = SceneEntityCfg("robot", body_names=("left_foot_link", "right_foot_link"))
  cfg.rewards["post_kick_stance"] = RewardTermCfg(
    func=kick_mdp.post_kick_stance,
    weight=4.0,
    params={
      "contact_window_s": 1.5,
      "min_kick_speed": _KICK_REWARD_GATE_SPEED,
      "feet_distance_ref": 0.19,
      "distance_sigma": 0.06,
      "flat_sigma": 0.25,
      "feet_cfg": feet,
      **robot_ball,
    },
  )
  # Stronger always-on flat-foot tax so tipped soles are costly even mid-episode.
  if "feet_roll" in cfg.rewards:
    cfg.rewards["feet_roll"].weight = -1.5
  cfg.rewards["ball_dribble_penalty"] = RewardTermCfg(
    func=kick_mdp.ball_dribble_penalty,
    weight=-8.0,
    params={
      "min_kick_speed": _KICK_REWARD_GATE_SPEED,
      "dribble_speed": 0.15,
      "kick_phase_robot_ball_distance": _PREF["setup_exit_dist"],
      **robot_ball,
    },
  )
  cfg.rewards["near_ball_wait"] = RewardTermCfg(
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
  # Keep FOV insurance from approach.
  assert "ball_camera_cone" in cfg.rewards

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

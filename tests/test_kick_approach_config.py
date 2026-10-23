"""Regression tests for approach-only stage-1 kick curriculum."""

from mjlab.tasks.registry import load_env_cfg, load_rl_cfg

TASK = "Mjlab-Kick-Approach-Booster-K1"


def test_approach_only_wiring():
  cfg = load_env_cfg(TASK)

  assert "agent_approach_ball" not in cfg.rewards
  assert cfg.rewards["waypoint_approach"].weight == 5.0
  assert cfg.rewards["waypoint_approach"].params["target_distance"] == 0.15
  assert cfg.rewards["waypoint_approach"].params["activate_waypoint_distance"] == 0.15
  assert cfg.rewards["waypoint_proximity"].params["std"] == 0.22
  assert cfg.rewards["waypoint_proximity"].params["facing_std"] == 0.40
  assert cfg.rewards["waypoint_inv_distance"].weight == 3.0
  assert cfg.rewards["ball_proximity"].params["min_distance"] == 0.09
  assert cfg.rewards["ball_proximity"].params["max_distance"] == 0.25
  assert cfg.rewards["ball_touch_keepout"].params["keepout_distance"] == 0.09
  assert cfg.rewards["ball_touch_keepout"].params["release_when_planted"] is True
  assert cfg.rewards["ball_velocity_toward_goal"].weight == 4.0
  assert cfg.rewards["ball_velocity_toward_goal"].params["require_plant_latch"] is True
  assert cfg.rewards["kicking_foot_strike"].params["require_plant_latch"] is True
  assert cfg.rewards["ball_camera_cone"].weight == 0.5
  assert cfg.rewards["ball_camera_cone"].params["soft_limit"] == 0.69
  assert cfg.rewards["orientation"].weight == -20.0
  assert cfg.rewards["base_height"].weight == -18.0
  assert cfg.rewards["tracking_lin_vel_x"].params["face_path_fov_clip"] is True
  assert cfg.rewards["tracking_lin_vel_x"].params["cruise_speed"] == 1.35
  assert cfg.rewards["tracking_lin_vel_x"].params["min_speed"] == 0.55
  assert cfg.rewards["tracking_lin_vel_x"].params["slow_distance"] == 0.45
  assert cfg.rewards["tracking_lin_vel_x"].params["fov_half_angle"] == 0.69
  assert cfg.rewards["tracking_lin_vel_x"].params["plant_far_scale"] == 1.0
  assert cfg.rewards["feet_swing"].params["plant_far_scale"] == 1.0
  twist = cfg.events["pref_pose_twist"].params
  assert twist["face_path_fov_clip"] is True
  assert twist["cruise_speed"] == 1.35
  assert twist["approach_standoff"] == 0.15
  assert twist["ready_waypoint_distance"] == 0.15
  assert twist["creep_through_plant"] is True
  assert cfg.commands["goal"].approach_standoff == 0.15

  term = cfg.terminations["near_ball_reached"]
  assert term.params["near_ball_distance"] == 0.25
  assert term.params["min_keepout_distance"] == 0.09
  assert term.params["max_waypoint_distance"] == 0.12
  assert cfg.events["reset_base"].params["spawn_on_approach_side"] is False
  assert cfg.events["reset_base"].params["waypoint_lateral_range"] == (0.08, 0.12)


def test_approach_rl_experiment_name():
  rl = load_rl_cfg(TASK)
  assert rl.experiment_name == "k1_kick_approach"
  assert rl.actor.hidden_dims == (256, 128, 128)

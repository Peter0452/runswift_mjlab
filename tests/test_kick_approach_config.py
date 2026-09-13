"""Regression tests for approach-only stage-1 kick curriculum."""

from mjlab.tasks.registry import load_env_cfg, load_rl_cfg

TASK = "Mjlab-Kick-Approach-Booster-K1"


def test_approach_only_wiring():
  cfg = load_env_cfg(TASK)

  assert "agent_approach_ball" not in cfg.rewards
  assert cfg.rewards["waypoint_approach"].weight == 4.0
  assert cfg.rewards["waypoint_proximity"].params["std"] == 0.35
  assert cfg.rewards["waypoint_inv_distance"].weight == 2.0
  assert cfg.rewards["ball_camera_cone"].weight == 0.5
  assert cfg.rewards["ball_camera_cone"].params["soft_limit"] == 0.69
  assert cfg.rewards["orientation"].weight == -20.0
  assert cfg.rewards["base_height"].weight == -18.0
  assert cfg.rewards["tracking_lin_vel_x"].params["face_path_fov_clip"] is True
  assert cfg.rewards["tracking_lin_vel_x"].params["cruise_speed"] == 1.1
  assert cfg.rewards["tracking_lin_vel_x"].params["fov_half_angle"] == 0.69
  assert cfg.rewards["tracking_lin_vel_x"].params["plant_far_scale"] == 1.0
  assert cfg.rewards["feet_swing"].params["plant_far_scale"] == 1.0
  assert cfg.events["pref_pose_twist"].params["face_path_fov_clip"] is True
  assert cfg.events["pref_pose_twist"].params["cruise_speed"] == 1.1

  term = cfg.terminations["near_ball_reached"]
  assert term.params["near_ball_distance"] == 0.80
  assert term.params["max_waypoint_distance"] == 0.35
  assert cfg.events["reset_base"].params["spawn_on_approach_side"] is False


def test_approach_rl_experiment_name():
  rl = load_rl_cfg(TASK)
  assert rl.experiment_name == "k1_kick_approach"
  assert rl.actor.hidden_dims == (256, 128, 128)

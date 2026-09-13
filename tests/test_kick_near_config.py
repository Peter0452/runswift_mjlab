"""Regression tests for near-ball kick stage-2 curriculum."""

import math

from mjlab.tasks.registry import load_env_cfg, load_rl_cfg

TASK = "Mjlab-Kick-Near-Booster-K1"


def test_near_kick_payday_and_weights():
  cfg = load_env_cfg(TASK)

  assert "ball_touch_keepout" not in cfg.rewards
  assert "ball_proximity" not in cfg.rewards
  assert "agent_approach_ball" not in cfg.rewards
  assert "near_ball_reached" not in cfg.terminations

  vel = cfg.rewards["ball_velocity_toward_goal"]
  assert vel.weight == 4.0
  assert vel.params["max_reward"] == 6.0
  assert vel.params["use_decay"] is False

  direction = cfg.rewards["ball_approach_target"]
  assert direction.weight == 1.5
  assert direction.params["velocity_eps"] == 0.25

  assert cfg.rewards["ball_acceleration_toward_goal"].weight == 4.0
  assert cfg.rewards["ball_dribble_penalty"].weight == -8.0
  assert cfg.rewards["near_ball_wait"].weight == -4.0
  assert cfg.rewards["near_ball_wait"].params["ramp_tau_s"] == 1.0
  assert cfg.rewards["ball_camera_cone"].weight == 0.5
  assert cfg.rewards["action_rate"].weight == -1.0

  assert cfg.rewards["waypoint_approach"].params["inactive_inside_ball_distance"] == 0.4

  plant = cfg.rewards["support_plant_score"]
  assert plant.weight == 8.0
  assert plant.params["sagittal_target"] == 0.14
  assert plant.params["lateral_target"] == 0.175
  assert plant.params["sagittal_sigma"] == 0.12
  assert plant.params["funnel_weight"] == 0.55

  bridge = cfg.rewards["kick_contact_bridge"]
  assert bridge.weight == 5.0
  assert bridge.params["activate_inside_ball_distance"] == 0.85
  assert bridge.params["min_plant_score"] == 0.15
  assert bridge.params["plant_gate_power"] == 1.0
  assert bridge.params["impulse_scale"] == 4.0

  ankle = cfg.rewards["strike_ankle_pitch"]
  assert ankle.weight == 2.0
  assert ankle.params["target_pitch"] == -0.50

  assert cfg.rewards["premature_kick_lunge"].weight == -1.5
  assert cfg.rewards["support_foot_planted"].weight == 2.0
  assert cfg.rewards["knee_flex_cmd_excess"].weight == -1.0

  twist = cfg.events["pref_pose_twist"].params
  assert twist["orbit_to_plant_box"] is True
  assert twist["creep_through_plant"] is True
  assert twist["plant_root_behind"] == 0.22
  assert twist["plant_feet_offset_y"] == 0.12
  assert twist["creep_speed"] == 0.25

  post = cfg.rewards["post_kick_upright"]
  assert post.weight == 5.0
  assert post.params["min_kick_speed"] == 1.2
  assert post.params["target_height"] == 0.52

  stance = cfg.rewards["post_kick_stance"]
  assert stance.weight == 4.0
  assert stance.params["feet_distance_ref"] == 0.19
  assert cfg.rewards["feet_roll"].weight == -1.5

  assert cfg.events["reset_base"].params["radius_range"] == (0.50, 0.70)
  assert cfg.events["reset_base"].params["spawn_on_approach_side"] is True
  assert math.isclose(
    cfg.events["reset_base"].params["approach_spread"], math.pi / 4.0
  )
  assert "root_height" not in cfg.terminations
  assert cfg.terminations["near_ball_no_kick"].params["max_near_time_s"] == 5.0
  assert cfg.episode_length_s == 7.0


def test_near_kick_rl_experiment_name():
  rl = load_rl_cfg(TASK)
  assert rl.experiment_name == "k1_kick_near"

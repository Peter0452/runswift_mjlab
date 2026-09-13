"""Regression tests for the simple approach→align→kick K1 task."""

import math

from mjlab.tasks.registry import load_env_cfg, load_rl_cfg

TASK = "Mjlab-Kick-Booster-K1"


def test_arc_kick_task_wiring():
  cfg = load_env_cfg(TASK)

  goal = cfg.commands["goal"]
  assert goal.distance_range == (4.0, 8.0)
  assert goal.angle_range == (-math.pi, math.pi)

  assert "ball" in cfg.scene.entities
  assert "ball_rel_pos" in cfg.observations["actor"].terms
  assert "ball_goal_direction" in cfg.observations["actor"].terms
  sensor_names = {s.name for s in (cfg.scene.sensors or ())}
  assert "feet_ball_contact" in sensor_names
  assert "body_ball_contact" in sensor_names

  assert "pref_pose_twist" in cfg.events
  assert cfg.events["pref_pose_twist"].func.__name__ == "update_pref_pose_twist_command"
  assert cfg.events["pref_pose_twist"].params.get("use_sampled_magnitudes") is True
  assert cfg.events["pref_pose_twist"].params.get("turn_speed") == 1.0
  assert cfg.events["pref_pose_twist"].params.get("plant_distance") == 0.20
  assert cfg.events["reset_base"].params["spawn_on_approach_side"] is True
  assert cfg.events["reset_base"].params["radius_range"] == (0.8, 1.5)

  # Paper trio + support terms.
  assert cfg.rewards["agent_approach_ball"].weight == 2.0
  assert cfg.rewards["agent_approach_ball"].params["velocity_eps"] == 0.1
  assert "body_face_ball" not in cfg.rewards
  assert cfg.rewards["ball_approach_target"].weight == 8.0
  assert cfg.rewards["ball_approach_target"].params["velocity_eps"] == 0.1
  assert cfg.rewards["ball_acceleration_toward_goal"].weight == 2.0
  assert cfg.rewards["target_reached"].weight == 5.0
  assert cfg.rewards["target_reached"].params["contact_window_s"] == 2.0
  assert cfg.rewards["target_reached"].params["std"] == 1.0
  assert cfg.rewards["post_kick_upright"].weight == 2.0
  assert cfg.rewards["post_kick_upright"].params["min_kick_speed"] == 5.0
  assert cfg.rewards["ball_dribble_penalty"].weight == -8.0
  assert cfg.rewards["near_ball_wait"].weight == -4.0
  assert cfg.rewards["near_ball_wait"].params["near_ball_distance"] == 1.0
  assert cfg.terminations["near_ball_no_kick"].params["max_near_time_s"] == 2.5
  assert cfg.terminations["near_ball_no_kick"].params["near_ball_distance"] == 1.0
  assert cfg.rewards["tracking_lin_vel_x"].weight == 1.5
  assert cfg.rewards["tracking_lin_vel_y"].weight == 1.5
  assert cfg.rewards["tracking_lin_vel_x"].func.__name__ == "track_lin_vel_axis_for_kick"
  assert cfg.rewards["tracking_ang_vel"].func.__name__ == "track_ang_vel_z_for_kick"
  assert cfg.rewards["tracking_lin_vel_x"].params["plant_full_dist"] == 0.6
  assert cfg.rewards["tracking_lin_vel_x"].params["plant_far_scale"] == 0.15
  assert cfg.rewards["feet_swing"].params["plant_full_dist"] == 0.6
  assert cfg.rewards["feet_offset_x"].params.get("plant_full_dist") is None

  # Conflicting / complex stack removed.
  for name in (
    "approach_ball",
    "approach_plant_vel",
    "ball_velocity_toward_goal",
    "pref_pose",
    "loiter_stage",
    "premature_ball_contact",
    "ball_not_moving",
    "ball_avoidance",
    "swing_foot_proximity",
    "kick_heading",
  ):
    assert name not in cfg.rewards

  assert cfg.rewards["feet_swing"].func.__name__ == "feet_swing_for_kick"
  assert cfg.rewards["feet_swing"].params.get("near_ball_dist") is None
  assert cfg.rewards["feet_swing"].params["setup_scale"] == 0.15
  assert cfg.events["ball_phase"].params["strong_kick_speed"] == 5.0
  assert cfg.events["ball_phase"].params["min_kick_speed"] == 1.2

  assert cfg.terminations["target_hit"].params["target_radius"] == 1.0
  assert cfg.only_positive_rewards is False
  assert cfg.episode_length_s == 25.0
  assert cfg.curriculum["spawn_radius"].params["start_radius"] == (0.8, 1.5)
  assert cfg.curriculum["spawn_radius"].params["end_radius"] == (2.0, 3.0)

  assert len(cfg.actions["joint_pos"].actuator_names) == 12


def test_arc_kick_rl_matches_basewalk_mlp():
  rl = load_rl_cfg(TASK)
  assert rl.actor.hidden_dims == (256, 128, 128)
  assert rl.critic.hidden_dims == (256, 256, 128)
  assert rl.experiment_name == "k1_arc_kick"

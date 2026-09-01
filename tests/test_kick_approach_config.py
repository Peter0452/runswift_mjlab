"""Regression tests for the target-conditioned K1 approach task."""

import math

from mjlab.tasks.registry import load_env_cfg

TASK = "Mjlab-Kick-Approach-Booster-K1"


def test_approach_task_uses_target_relative_setup():
  cfg = load_env_cfg(TASK)

  goal = cfg.commands["goal"]
  assert goal.distance_range == (4.0, 8.0)
  assert goal.angle_range == (-math.pi, math.pi)
  assert goal.resampling_time_range == (30.0, 30.0)
  assert goal.debug_vis is True

  reset_base = cfg.events["reset_base"]
  assert reset_base.func.__name__ == "reset_robot_around_ball_facing"
  assert reset_base.mode == "post_reset"
  assert reset_base.params["radius_range"] == (0.5, 1.0)
  assert reset_base.params["spawn_on_approach_side"] is True
  assert cfg.events["approach_twist"].func.__name__ == "update_approach_twist_command"
  assert cfg.events["approach_twist"].params["cruise_speed"] == 1.0
  assert cfg.events["approach_twist"].params["gait_frequency"] == 2.5
  assert cfg.events["push_robot"].func.__name__ == "booster_push_robots"
  assert cfg.events["push_robot"].params["push_interval_range_s"] == (3.0, 4.0)
  assert cfg.events["push_robot"].params["push_duration_s"] == 1.0
  assert "kick_robot" not in cfg.events

  reset_ball = cfg.events["reset_ball"]
  assert reset_ball.func.__name__ == "reset_ball_uniform"
  assert reset_ball.params["pose_range"] == {
    "x": (0.0, 0.0),
    "y": (0.0, 0.0),
    "z": (0.11, 0.11),
  }

  assert "ball_rel_pos" in cfg.observations["actor"].terms
  assert "ball_goal_direction" in cfg.observations["actor"].terms
  assert cfg.rewards["ball_distance_band"].weight == 3.0
  assert cfg.rewards["ball_distance_band"].params["min_distance"] == 0.35
  assert cfg.rewards["ball_distance_band"].params["max_distance"] == 0.45
  assert cfg.rewards["ball_approach_far"].weight == 2.0
  assert cfg.rewards["waypoint_approach_velocity"].weight == 2.5
  assert cfg.rewards["waypoint_retreat_penalty"].weight == -2.0
  assert "ball_approach" not in cfg.rewards
  assert cfg.curriculum["spawn_radius"].params["end_radius"] == (4.0, 4.0)
  assert cfg.episode_length_s == 45.0
  assert cfg.rewards["behind_ball_waypoint"].weight == 6.0
  assert cfg.rewards["body_face_ball"].weight == 1.5
  assert cfg.rewards["ball_camera_cone"].weight == 1.0
  assert cfg.rewards["kick_ready"].func.__name__ == "kick_ready"
  assert cfg.rewards["kick_ready"].weight == 4.0
  assert cfg.rewards["kick_ready"].params["target_distance"] == 0.35
  assert cfg.rewards["kick_ready"].params["camera_soft_limit"] == math.radians(45.0)
  assert cfg.actions["joint_pos"].scale is not None
  assert len(cfg.actions["joint_pos"].scale) == 16
  assert cfg.actions["joint_pos"].scale["Left_Shoulder_Pitch"] == 0.12
  assert cfg.actions["joint_pos"].scale["Left_Shoulder_Roll"] == 0.05
  assert cfg.actions["joint_pos"].scale["Left_Hip_Pitch"] == 0.8
  assert cfg.actions["joint_pos"].clip is not None
  assert "Left_Shoulder_Roll" in cfg.actions["joint_pos"].clip
  assert cfg.rewards["shoulder_deviation"].weight == -4.0
  assert cfg.rewards["base_height"].weight == -8.0
  assert cfg.rewards["orientation"].weight == -8.0
  assert cfg.rewards["feet_roll"].weight == -0.2
  assert cfg.rewards["feet_pitch"].weight == -0.1
  assert cfg.rewards["foot_yaw_l"].weight == -1.0
  assert cfg.rewards["foot_yaw_r"].weight == -1.0
  assert cfg.rewards["feet_offset_x"].weight == -12.0
  assert cfg.rewards["feet_offset_y"].weight == -12.0
  assert cfg.rewards["feet_minimum_separation"].weight == -2.0


def test_approach_task_preserves_htwk_walking_objective():
  cfg = load_env_cfg(TASK)
  twist = cfg.commands["twist"]

  assert twist.ranges.lin_vel_x == (-1.0, 2.0)
  assert twist.ranges.lin_vel_y == (-1.0, 1.0)
  assert twist.ranges.ang_vel_z == (-1.6, 1.6)
  assert twist.ranges.gait_frequency == (1.5, 3.0)
  assert twist.still_proportion == 0.0
  assert twist.rel_standing_envs == 0.0
  assert twist.resampling_time_range == (45.0, 45.0)
  assert cfg.rewards["tracking_lin_vel_x"].weight == 2.0
  assert cfg.rewards["tracking_lin_vel_y"].weight == 2.0
  assert cfg.rewards["tracking_ang_vel"].weight == 1.5
  assert set(cfg.curriculum) == {
    "velocity",
    "action_rate",
    "spawn_radius",
  }

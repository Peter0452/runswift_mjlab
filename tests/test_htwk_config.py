"""Configuration regression tests for the HTWK/NuBots compatibility task."""

from __future__ import annotations

import math

import pytest

from mjlab.tasks.registry import load_env_cfg, load_rl_cfg
from mjlab.tasks.velocity.config.k1 import env_cfgs as k1_env_cfgs


TASK = "Mjlab-Velocity-HTWK-Booster-K1-Nubots"
UNCLIPPED_TASK = "Mjlab-Velocity-HTWK-Unclipped-Booster-K1-Nubots"


def test_htwk_task_preserves_nubots_interfaces_and_teacher_ranges():
  cfg = load_env_cfg(TASK)
  runner = load_rl_cfg(TASK)
  twist = cfg.commands["twist"]

  assert cfg.observations["actor"].terms["velocity_commands"].func.__name__ == (
    "nubots_parameter_walk_commands"
  )
  assert cfg.observations["actor"].terms["velocity_commands"].params["command_name"] == (
    "twist"
  )
  assert twist.ranges.lin_vel_x == (-1.0, 2.0)
  assert twist.ranges.lin_vel_y == (-1.0, 1.0)
  assert twist.ranges.ang_vel_z == (-1.6, 1.6)
  assert twist.ranges.gait_frequency == (1.5, 3.0)
  assert twist.still_proportion == pytest.approx(0.1)
  assert twist.parameter_walk_ranges == {
    "foot_yaw_l": (-0.7, 0.7),
    "foot_yaw_r": (-0.7, 0.7),
    "body_pitch": (-0.1, 0.3),
    "body_roll": (-0.1, 0.1),
    "feet_offset_x": (-0.15, 0.15),
    "feet_offset_y": (-0.08, 0.15),
  }
  assert cfg.actions["joint_pos"].scale == {
    name: 0.8 for name in cfg.actions["joint_pos"].actuator_names
  }
  assert runner.max_iterations == 20_000


def test_htwk_task_has_no_experimental_speed_terms():
  cfg = load_env_cfg(TASK)

  assert "gait" not in cfg.rewards
  assert "angular_momentum" not in cfg.rewards
  assert all(
    "speed_ref" not in term.params for term in cfg.rewards.values()
  )
  assert cfg.rewards["tracking_lin_vel_x"].weight == 2.0
  assert cfg.rewards["tracking_lin_vel_y"].weight == 2.0
  assert cfg.rewards["tracking_ang_vel"].weight == 1.5
  assert cfg.rewards["base_height"].params["target_height"] == 0.52
  assert cfg.rewards["orientation"].weight == -8.0
  assert cfg.rewards["ang_vel_xy"].weight == -0.2
  assert cfg.rewards["feet_offset_x"].weight == -12.0
  assert cfg.rewards["feet_offset_y"].weight == -12.0
  assert cfg.rewards["feet_swing"].weight == 3.0
  assert cfg.rewards["shoulder_deviation"].weight == -3.0


def test_htwk_unclipped_variant_only_changes_reward_clamp_and_horizon():
  cfg = load_env_cfg(UNCLIPPED_TASK)
  runner = load_rl_cfg(UNCLIPPED_TASK)

  assert cfg.only_positive_rewards is False
  assert runner.max_iterations == 40_000
  assert cfg.rewards["tracking_lin_vel_x"].weight == 2.0
  assert cfg.rewards["orientation"].weight == -8.0
  assert cfg.commands["twist"].ranges.gait_frequency == (1.5, 3.0)


def test_htwk_exact_task_matches_reference_command_and_runner():
  cfg = load_env_cfg("Mjlab-Velocity-HTWK-Exact-Booster-K1-Nubots")
  runner = load_rl_cfg("Mjlab-Velocity-HTWK-Exact-Booster-K1-Nubots")
  command = cfg.commands["twist"]

  assert type(command).__name__ == "ParameterWalkCommandCfg"
  assert command.resampling_time_range == (3.0, 8.0)
  assert command.still_proportion == pytest.approx(0.1)
  assert command.ranges.body_pitch_target == (-0.1, 0.3)
  assert command.ranges.feet_offset_y_target == (-0.08, 0.15)
  assert cfg.observations["actor"].terms["velocity_commands"].params["command_name"] == (
    "twist"
  )
  assert cfg.only_positive_rewards is True
  assert set(cfg.terminations) == {"time_out", "base_height"}
  assert cfg.terminations["base_height"].params["minimum_height"] == pytest.approx(0.35)
  assert cfg.actions["joint_pos"].clip == {
    "Left_Shoulder_Roll": pytest.approx((-1.3 - 0.1308996939, -1.3 + 0.1308996939)),
    "Right_Shoulder_Roll": pytest.approx((1.3 - 0.1308996939, 1.3 + 0.1308996939)),
  }
  assert cfg.scene.terrain is not None
  assert cfg.scene.terrain.terrain_type == "plane"
  assert cfg.scene.terrain.terrain_generator is None
  assert cfg.events["foot_friction"].params["ranges"] == (0.1, 2.0)
  assert "robot_inertia" not in cfg.events
  assert cfg.events["trunk_inertia"].func.__name__ == "pseudo_inertia"
  assert cfg.events["trunk_inertia"].params["alpha_range"] == pytest.approx(
    (0.5 * math.log(0.8), 0.5 * math.log(1.2))
  )
  assert cfg.events["trunk_inertia"].params["asset_cfg"].body_names == ("Trunk",)
  assert cfg.events["other_link_inertia"].func.__name__ == "pseudo_inertia"
  assert cfg.events["other_link_inertia"].params["asset_cfg"].body_names == (
    "^(?!Trunk$).*",
  )
  assert cfg.events["other_link_inertia"].params["alpha_range"] == pytest.approx(
    (0.5 * math.log(0.9), 0.5 * math.log(1.1))
  )
  reset_base = cfg.events["reset_base"].params
  assert reset_base["pose_range"]["x"] == (-1.0, 1.0)
  assert reset_base["pose_range"]["y"] == (-1.0, 1.0)
  assert reset_base["velocity_range"]["x"] == (0.0, 0.1)
  assert reset_base["velocity_range"]["y"] == (0.0, 0.1)
  assert cfg.events["trunk_external_wrench"].func.__name__ == (
    "apply_external_force_torque"
  )
  assert cfg.events["trunk_external_wrench"].params["force_range"] == (-10.0, 10.0)
  assert cfg.events["trunk_external_wrench"].params["torque_range"] == (-2.0, 2.0)
  assert cfg.events["trunk_external_wrench"].params["asset_cfg"].body_names == (
    "Trunk",
  )
  sensor_names = {sensor.name for sensor in (cfg.scene.sensors or ())}
  assert "foot_foot_collision" in sensor_names
  assert cfg.rewards["feet_offset_y"].params["feet_distance_ref"] == pytest.approx(
    0.18
  )
  assert cfg.rewards["feet_minimum_separation"].func.__name__ == (
    "htwk_feet_minimum_separation"
  )
  assert cfg.rewards["feet_minimum_separation"].params["min_separation"] == pytest.approx(
    0.10
  )
  assert cfg.rewards["foot_foot_collision"].func.__name__ == (
    "htwk_foot_foot_collision"
  )
  assert runner.experiment_name == "k1_walk_htwk"
  assert runner.max_iterations == 20_000
  assert runner.algorithm.learning_rate == pytest.approx(1.0e-3)
  assert runner.algorithm.schedule == "adaptive"
  assert runner.clip_actions is None
  assert cfg.rewards["torque_tiredness"].func.__name__ == "htwk_torque_tiredness"


def test_htwk_robust_ft_task_has_staged_yaw_and_terrain_setup():
  task = "Mjlab-Velocity-HTWK-Robust-FT-Booster-K1-Nubots"
  cfg = load_env_cfg(task)
  runner = load_rl_cfg(task)
  command = cfg.commands["twist"]

  assert command.ranges.lin_vel_x == (-1.5, 2.0)
  assert command.ranges.ang_vel_yaw == (-1.5, 1.5)
  assert command.vel_curriculum is False
  assert command.yaw_curriculum is True
  assert command.init_yaw_scale == pytest.approx(0.4 / 1.5)
  assert command.high_speed_oversample is True
  assert command.high_speed_sampling_probability == pytest.approx(0.5)
  assert command.high_speed_gait_bias is True
  assert command.high_speed_gait_frequency_range == (2.5, 3.0)
  assert cfg.scene.terrain is not None
  assert cfg.scene.terrain.terrain_type == "generator"
  assert cfg.scene.terrain.terrain_generator is not None
  assert set(cfg.scene.terrain.terrain_generator.sub_terrains) == {
    "flat",
    "random_rough",
    "wave_terrain",
  }
  assert [
    cfg.scene.terrain.terrain_generator.sub_terrains[name].proportion
    for name in ("flat", "random_rough", "wave_terrain")
  ] == pytest.approx([0.8, 0.1, 0.1])
  assert cfg.observations["critic"].terms["base_height"].params["sensor_name"] == (
    "terrain_scan"
  )
  assert cfg.observations["actor"].terms["velocity_commands"].func.__name__ == (
    "nubots_parameter_walk_commands"
  )
  assert cfg.curriculum["yaw"].func.__name__ == "htwk_yaw_levels"
  assert cfg.curriculum["terrain_mix"].func.__name__ == (
    "scheduled_terrain_mix_curriculum"
  )
  assert cfg.curriculum["terrain_mix"].params["steps_per_iteration"] == 24
  assert cfg.curriculum["terrain_mix"].params["stages"] == [
    {"iteration": 0, "proportions": [0.8, 0.1, 0.1]},
    {"iteration": 20_000, "proportions": [0.8, 0.1, 0.1]},
    {"iteration": 40_000, "proportions": [0.7, 0.15, 0.15]},
  ]
  assert runner.experiment_name == "k1_walk_htwk_robust_ft"
  assert cfg.events["foot_friction"].params["ranges"] == pytest.approx(
    (0.1, 2.0)
  )
  assert cfg.events["trunk_external_wrench"].mode == "interval"
  assert cfg.events["trunk_external_wrench"].interval_range_s == pytest.approx(
    (4.0, 4.0)
  )
  assert runner.max_iterations == 50_000
  assert runner.algorithm.learning_rate == pytest.approx(5.0e-6)
  assert runner.algorithm.schedule == "fixed"
  assert runner.clip_actions == pytest.approx(1.0)
  assert cfg.rewards["knee_separation"].func.__name__ == "htwk_knee_separation"
  assert cfg.rewards["knee_separation"].weight == pytest.approx(-3.0)
  assert cfg.rewards["knee_separation"].params["safe_distance"] == pytest.approx(
    0.18
  )
  assert cfg.rewards["knee_separation"].params["softness"] == pytest.approx(0.01)
  assert cfg.rewards["knee_separation"].params["asset_cfg"].body_names == (
    "Left_Shank",
    "Right_Shank",
  )
  assert cfg.rewards["hip_roll_barrier"].func.__name__ == "htwk_hip_roll_barrier"
  assert cfg.rewards["hip_roll_barrier"].weight == pytest.approx(-4.0)
  assert cfg.rewards["hip_roll_barrier"].params["max_deviation"] == pytest.approx(
    0.18
  )
  assert cfg.rewards["hip_roll_barrier"].params["softness"] == pytest.approx(0.02)
  assert cfg.rewards["hip_roll_barrier"].params["asset_cfg"].joint_names == (
    ".*_Hip_Roll",
  )
  action = cfg.actions["joint_pos"]
  assert action.scale["Left_Shoulder_Pitch"] == pytest.approx(
    k1_env_cfgs._NUBOTS_ARM_SWING_PITCH_SCALE
  )
  assert action.scale["Left_Shoulder_Roll"] == pytest.approx(
    k1_env_cfgs._NUBOTS_ARM_SWING_ROLL_SCALE
  )
  assert action.clip["Left_Shoulder_Pitch"] == pytest.approx(
    (
      -k1_env_cfgs._NUBOTS_ARM_SWING_PITCH_BAND,
      k1_env_cfgs._NUBOTS_ARM_SWING_PITCH_BAND,
    )
  )
  assert cfg.rewards["shoulder_deviation"].weight == pytest.approx(-0.5)
  assert cfg.curriculum["shoulder_release"].params["start_weight"] == pytest.approx(
    -0.5
  )
  assert cfg.curriculum["shoulder_release"].params["end_weight"] == pytest.approx(
    -0.05
  )
  assert cfg.rewards["feet_offset_x"].params["min_velocity_scale"] == pytest.approx(
    0.35
  )
  assert cfg.rewards["feet_minimum_separation"].params["min_separation"] == (
    pytest.approx(0.14)
  )
  assert cfg.rewards["feet_minimum_separation"].weight == pytest.approx(-3.0)
  assert cfg.rewards["feet_site_xy_separation"].func.__name__ == (
    "htwk_feet_site_xy_separation"
  )
  assert cfg.rewards["feet_site_xy_separation"].weight == pytest.approx(-2.0)
  assert cfg.rewards["foot_foot_collision"].weight == pytest.approx(-3.0)
  assert cfg.events["fold_elbows"].func.__name__ == (
    "set_joint_position_targets_random"
  )
  assert cfg.events["fold_elbows"].params["position_range"] == pytest.approx(
    (math.radians(34.0), math.radians(46.0))
  )
  assert cfg.events["reset_robot_joints"].params["poses"][0][
    "Left_Elbow_Pitch"
  ] == pytest.approx(math.radians(40.0))
  assert cfg.events["reset_robot_joints"].params["poses"][0][
    "Right_Elbow_Pitch"
  ] == pytest.approx(math.radians(40.0))
  assert cfg.rewards["feet_roll"].func.__name__ == (
    "htwk_feet_orientation_contact_gated"
  )
  assert cfg.rewards["feet_pitch"].func.__name__ == (
    "htwk_feet_orientation_contact_gated"
  )
  assert cfg.rewards["swing_sole_clearance"].func.__name__ == (
    "htwk_swing_sole_clearance"
  )
  assert cfg.rewards["swing_sole_clearance"].weight == pytest.approx(2.0)
  assert cfg.rewards["swing_sole_clearance"].params["min_clearance"] == (
    pytest.approx(0.04)
  )
  assert cfg.rewards["swing_sole_clearance"].params["target_clearance"] == (
    pytest.approx(0.06)
  )

"""Regression tests for lean Near-kick (principle-aligned) curriculum."""

import math

from mjlab.tasks.registry import load_env_cfg

TASK = "Mjlab-Kick-Near-Booster-K1"

_LEAN = {
  "tracking_lin_vel_x",
  "tracking_lin_vel_y",
  "tracking_ang_vel",
  "waypoint_approach",
  "support_plant_score",
  "com_over_plant",
  "kicking_foot_strike",
  "ball_velocity_toward_goal",
  "orientation",
  "base_height",
  "feet_yaw_diff",
  "feet_yaw_mean",
  "post_kick_stance",
  "action_rate",
  "wrong_ball_contact",
  "survival",
  "phase_audit",
}


def test_near_kick_lean_principle_rewards():
  cfg = load_env_cfg(TASK)

  assert set(cfg.rewards.keys()) == _LEAN
  assert len(cfg.rewards) == 17

  assert cfg.rewards["waypoint_approach"].weight == 1.5
  assert cfg.rewards["support_plant_score"].weight == 2.0
  assert cfg.rewards["support_plant_score"].params["lateral_target"] == 0.13
  assert cfg.rewards["com_over_plant"].weight == 1.5
  assert cfg.rewards["kicking_foot_strike"].weight == 3.0
  assert cfg.rewards["kicking_foot_strike"].params["require_plant_latch"] is True
  assert cfg.rewards["kicking_foot_strike"].params["require_compact"] is True
  assert cfg.rewards["kicking_foot_strike"].params["compact_gap_max"] == 0.22
  assert math.isclose(
    cfg.rewards["kicking_foot_strike"].params["compact_max_yaw_rad"],
    math.radians(25.0),
  )
  assert cfg.rewards["ball_velocity_toward_goal"].weight == 5.0
  assert cfg.rewards["ball_velocity_toward_goal"].params["require_compact"] is True
  assert cfg.rewards["orientation"].weight == -15.0
  assert cfg.rewards["base_height"].weight == -12.0
  assert cfg.rewards["feet_yaw_diff"].weight == -2.0
  assert cfg.rewards["feet_yaw_mean"].weight == -2.0
  assert cfg.rewards["post_kick_stance"].weight == 4.0
  assert cfg.rewards["post_kick_stance"].params["sagittal_sigma"] == 0.10
  assert cfg.rewards["post_kick_stance"].params["bos_sigma"] == 0.10
  assert cfg.rewards["post_kick_stance"].params["command_name"] == "goal"
  assert cfg.rewards["action_rate"].weight == -1.0
  assert cfg.rewards["wrong_ball_contact"].weight == -3.0
  assert cfg.rewards["survival"].weight == 0.15
  assert cfg.rewards["phase_audit"].weight == 1.0e-6

  # Bloat removed
  for name in (
    "plant_latch_bonus",
    "kick_contact_bridge",
    "kick_direction_accuracy",
    "kick_speed_loose",
    "kick_speed_tight",
    "feet_offset_x",
    "feet_offset_y",
    "feet_swing",
    "swing_plant_lateral_gap",
    "post_kick_upright",
    "trunk_height_floor",
    "waypoint_proximity",
    "waypoint_inv_distance",
  ):
    assert name not in cfg.rewards

  twist = cfg.events["pref_pose_twist"].params
  assert twist["require_support_plant_for_latch"] is True
  assert twist["support_plant_lateral_target"] == 0.13
  assert twist["support_plant_lateral_tol"] == 0.08
  assert twist["require_com_over_plant_for_latch"] is False
  assert twist["creep_through_plant"] is True

  tracking = cfg.rewards["tracking_lin_vel_x"].params
  assert tracking["require_support_plant_for_latch"] is True
  assert tracking["require_com_over_plant_for_latch"] is False
  assert tracking["support_plant_lateral_tol"] == 0.08

  assert cfg.events["reset_base"].params["radius_range"] == (0.35, 0.55)
  assert cfg.events["reset_base"].params["handoff_fraction"] == 0.5
  assert cfg.commands["goal"].approach_standoff == 0.0
  assert cfg.episode_length_s == 7.0
  assert "near_ball_reached" not in cfg.terminations


def test_near_kick_play_disables_handoff_mix():
  cfg = load_env_cfg(TASK, play=True)
  assert cfg.events["reset_base"].params["handoff_fraction"] == 0.0



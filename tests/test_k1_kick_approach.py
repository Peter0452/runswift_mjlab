"""Approach stage: ball channels, speed limits, wedge rewards, head-camera mask."""

from __future__ import annotations

import math

import torch

import mjlab.tasks  # noqa: F401
from k1.tasks.kick.mdp.approach import (
  FOV_HALF_ANGLE,
  STAND_DISTANCE,
  WEDGE_HALF_ANGLE,
  approach_alpha,
  camera_angles,
  fov_edge_rays,
  in_camera_view,
  kick_direction_b,
  range_one_hot,
  speed_limit_excess,
  stand_yaw_quality,
)
from k1.tasks.velocity.mdp.amp_symmetry import (
  POLICY_DIM_KICK_STAGE1,
  flip_k1_policy_obs_left_right,
)
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg

TASK = "Mjlab-Velocity-Kick-Approach-Amp-DA-Muon-Booster-K1"


def test_alpha_is_zero_on_the_approach_side() -> None:
  ball = torch.tensor([[2.0, 3.0]])
  target = ball + torch.tensor([[4.0, 0.0]])
  behind = ball + torch.tensor([[-1.5, 0.0]])
  side = ball + torch.tensor([[0.0, 1.5]])
  assert approach_alpha(behind, ball, target).abs().item() < 1e-5
  assert math.isclose(
    abs(approach_alpha(side, ball, target).item()), math.pi / 2, abs_tol=1e-5
  )
  assert WEDGE_HALF_ANGLE == math.pi / 4


def test_range_one_hot_splits_four_to_eight() -> None:
  distance = torch.tensor([4.0, 6.0, 8.0])
  one_hot = range_one_hot(distance)
  assert torch.equal(one_hot[0], torch.tensor([1.0, 0.0, 0.0]))
  assert torch.equal(one_hot[1], torch.tensor([0.0, 1.0, 0.0]))
  assert torch.equal(one_hot[2], torch.tensor([0.0, 0.0, 1.0]))


def test_vertical_fov_is_optional_and_follows_camera_pitch() -> None:
  # Ball on the ground 0.5 m ahead, 0.45 m below the head.
  ball = torch.tensor([[0.5, 0.0, -0.45]])
  depth, az, el = camera_angles(ball)
  assert in_camera_view(depth, az, el, FOV_HALF_ANGLE, None).item()
  assert not in_camera_view(depth, az, el, FOV_HALF_ANGLE, 0.5).item()
  depth, az, el = camera_angles(ball, camera_pitch=0.5)
  assert in_camera_view(depth, az, el, FOV_HALF_ANGLE, 0.5).item()
  behind = torch.tensor([[-1.0, 0.0, 0.0]])
  assert not in_camera_view(*camera_angles(behind), FOV_HALF_ANGLE, None).item()


def test_fov_edge_rays_sit_on_the_visibility_cone() -> None:
  for half_v, pitch in ((None, 0.0), (0.45, 0.3)):
    rays = fov_edge_rays(FOV_HALF_ANGLE, half_v, pitch)
    depth, az, el = camera_angles(rays, camera_pitch=pitch)
    assert (depth > 0).all()
    assert torch.allclose(az.abs(), torch.full_like(az, FOV_HALF_ANGLE), atol=1e-5)
    expected_el = 0.0 if half_v is None else half_v
    assert torch.allclose(el.abs(), torch.full_like(el, expected_el), atol=1e-5)


def test_stand_yaw_quality_peaks_on_the_line_and_never_goes_flat() -> None:
  err = torch.tensor([0.0, 0.5, 1.9, math.pi])
  q = stand_yaw_quality(err)
  assert math.isclose(q[0].item(), 1.0, abs_tol=1e-6)
  assert math.isclose(q[3].item(), 0.0, abs_tol=1e-6)
  assert (q[:-1] > q[1:]).all()
  # Far from the line the score still rises when turning toward it.
  assert stand_yaw_quality(torch.tensor([1.8])) > stand_yaw_quality(torch.tensor([1.9]))


def test_speed_limit_excess_sums_each_axis() -> None:
  lin_vel = torch.tensor([[1.0, -0.5, 0.0]])
  yaw_rate = torch.tensor([-1.0])
  limits = torch.tensor([[0.8, 0.6, 0.5]])
  assert math.isclose(
    speed_limit_excess(lin_vel, yaw_rate, limits).item(), 0.7, abs_tol=1e-6
  )


def test_kick_direction_is_in_the_yaw_frame() -> None:
  half = math.sqrt(0.5)
  facing_y = torch.tensor([[half, 0.0, 0.0, half]])
  direction = kick_direction_b(
    torch.tensor([[5.0, 0.0]]), torch.tensor([[1.0, 0.0]]), facing_y
  )
  assert torch.allclose(direction, torch.tensor([[0.0, -1.0]]), atol=1e-6)


def test_approach_cfg_matches_the_stage1_width() -> None:
  cfg = load_env_cfg(TASK)
  assert cfg.episode_length_s == 20.0
  assert cfg.commands is not None
  assert cfg.commands["twist"].__class__.__name__ == "ApproachYawCommandCfg"
  assert cfg.curriculum is not None
  assert "command_vel" not in cfg.curriculum
  assert "ball" in cfg.scene.entities
  assert any(sensor.name == "feet_ball_contact" for sensor in cfg.scene.sensors)

  actor = cfg.observations["actor"].terms
  critic = cfg.observations["critic"].terms
  assert list(actor)[5:9] == ["command", "speed_limit", "kick_direction", "kick_range"]
  assert critic["command"].params["privileged"] is True
  assert actor["command"].params["privileged"] is False
  assert cfg.commands["twist"].fov_vertical_half_angle is None
  assert "Head" not in str(
    cfg.rewards["upper_body_posture"].params["asset_cfg"].joint_names
  )

  assert cfg.rewards["track_linear_velocity"].weight == 0.0
  assert cfg.rewards["track_angular_velocity"].weight == 0.0
  assert cfg.rewards["approach_align"].weight == 80.0
  assert cfg.rewards["approach_close"].weight == 100.0
  assert cfg.rewards["approach_stand"].weight == 2.0
  assert cfg.rewards["approach_bad_contact"].weight == -20.0
  assert cfg.rewards["approach_view"].weight == 0.5
  assert cfg.rewards["approach_speed_limit"].weight == -10.0
  assert cfg.rewards["approach_heading"].weight == 50.0
  assert STAND_DISTANCE == 0.5

  rl = load_rl_cfg(TASK)
  assert rl.experiment_name == "k1_kick_approach_amp"
  assert rl.style_reward_weight == 0.3
  assert rl.algorithm.use_muon is True
  assert rl.algorithm.symmetry_cfg is not None


def test_symmetry_flips_ball_y_and_kick_sine_but_not_limits() -> None:
  actor = torch.randn(2, POLICY_DIM_KICK_STAGE1)
  flipped = flip_k1_policy_obs_left_right(actor)
  assert torch.equal(flipped[:, 72], actor[:, 72])
  assert torch.equal(flipped[:, 73], -actor[:, 73])
  assert torch.equal(flipped[:, 74], -actor[:, 74])
  assert torch.equal(flipped[:, 75:78], actor[:, 75:78])
  assert torch.equal(flipped[:, 79], -actor[:, 79])
  assert torch.equal(flip_k1_policy_obs_left_right(flipped), actor)

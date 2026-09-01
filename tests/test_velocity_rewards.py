"""Tests for velocity task reward functions."""

from __future__ import annotations

import math
from unittest.mock import MagicMock, PropertyMock

import pytest

import torch

from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.sensor import RayCastData, RayCastSensor
from mjlab.tasks.velocity.mdp.rewards import upright
from mjlab.utils.lab_api.math import quat_from_euler_xyz


def _identity_quat(B: int) -> torch.Tensor:
  """(w, x, y, z) = (1, 0, 0, 0)."""
  q = torch.zeros(B, 4)
  q[:, 0] = 1.0
  return q


def _quat_from_roll(roll_rad: float, B: int = 1) -> torch.Tensor:
  roll = torch.full((B,), roll_rad)
  zero = torch.zeros(B)
  return quat_from_euler_xyz(roll, zero, zero)


def _quat_from_pitch(pitch_rad: float, B: int = 1) -> torch.Tensor:
  pitch = torch.full((B,), pitch_rad)
  zero = torch.zeros(B)
  return quat_from_euler_xyz(zero, pitch, zero)


def _make_env_and_reward(
  terrain_sensor_names: tuple[str, ...] | None = None,
  body_quat_w: torch.Tensor | None = None,
  terrain_hit_z: float = 0.0,
  terrain_slope_x: float = 0.0,
):
  """Build mocked env + upright reward instance.

  Args:
    terrain_sensor_names: If set, enables terrain-aware mode.
    body_quat_w: [B, 4] root orientation. Defaults to identity.
    terrain_hit_z: Z value for flat terrain hits.
    terrain_slope_x: Slope in X (z = terrain_slope_x * x).
  """
  B = 1 if body_quat_w is None else body_quat_w.shape[0]
  if body_quat_w is None:
    body_quat_w = _identity_quat(B)

  # Mock asset data. Use explicit asset_cfg with no body_names so
  # body_ids stays None and the reward uses root_link_quat_w.
  asset = MagicMock()
  asset.data.root_link_quat_w = body_quat_w
  asset.data.root_link_pos_w = torch.zeros(B, 3)
  asset.data.gravity_vec_w = torch.tensor([0.0, 0.0, -1.0]).expand(B, 3)
  asset_cfg = SceneEntityCfg("robot", body_names=None, body_ids=[])

  # Mock terrain sensor if needed.
  sensors: dict = {"robot": asset}
  if terrain_sensor_names is not None:
    N = 100
    torch.manual_seed(0)
    hit_pos = torch.zeros(B, N, 3)
    hit_pos[:, :, 0] = torch.randn(B, N)
    hit_pos[:, :, 1] = torch.randn(B, N)
    hit_pos[:, :, 2] = terrain_hit_z + terrain_slope_x * hit_pos[:, :, 0]

    raycast_sensor = MagicMock(spec=RayCastSensor)
    raycast_data = RayCastData(
      distances=torch.ones(B, N),
      normals_w=torch.zeros(B, N, 3),
      hit_pos_w=hit_pos,
      pos_w=torch.zeros(B, 3),
      quat_w=torch.zeros(B, 4),
      frame_pos_w=torch.zeros(B, 1, 3),
      frame_quat_w=torch.zeros(B, 1, 4),
    )
    type(raycast_sensor).data = PropertyMock(return_value=raycast_data)
    for name in terrain_sensor_names:
      sensors[name] = raycast_sensor

  env = MagicMock()
  env.scene.__getitem__ = MagicMock(side_effect=lambda n: sensors[n])

  params: dict = {"std": 1.0, "asset_cfg": asset_cfg}
  if terrain_sensor_names is not None:
    params["terrain_sensor_names"] = terrain_sensor_names
  cfg = MagicMock(spec=RewardTermCfg)
  cfg.params = params

  reward_fn = upright(cfg, env)
  return env, reward_fn, params


def test_world_up_identity_gives_max_reward():
  """Perfectly upright robot on flat ground → reward ≈ 1."""
  env, reward, params = _make_env_and_reward()
  r = reward(env, std=params["std"], asset_cfg=params["asset_cfg"])
  assert r.shape == (1,)
  assert r.item() > 0.99


def test_world_up_tilted_gives_lower_reward():
  """30° roll → reward significantly below 1."""
  quat = _quat_from_roll(math.radians(30))
  env, reward, params = _make_env_and_reward(body_quat_w=quat)
  r = reward(env, std=params["std"], asset_cfg=params["asset_cfg"])
  assert r.item() < 0.8


def test_terrain_aware_aligned_with_slope():
  """Robot pitched to match a slope → terrain-aware reward ≈ 1."""
  slope = 0.5  # z = 0.5 * x
  tilt = math.atan(slope)  # Pitch to match slope in XZ plane.
  quat = _quat_from_pitch(-tilt)
  env, reward, params = _make_env_and_reward(
    terrain_sensor_names=("terrain_scan",),
    body_quat_w=quat,
    terrain_slope_x=slope,
  )
  r = reward(
    env,
    std=params["std"],
    asset_cfg=params["asset_cfg"],
    terrain_sensor_names=params["terrain_sensor_names"],
  )
  # Should be close to 1 since robot matches terrain.
  assert r.item() > 0.9


def test_terrain_aware_upright_on_slope_penalized():
  """Robot staying vertical on a slope → terrain-aware reward < 1."""
  slope = 0.5
  quat = _identity_quat(1)  # Robot is world-vertical, not matching slope.
  env, reward, params = _make_env_and_reward(
    terrain_sensor_names=("terrain_scan",),
    body_quat_w=quat,
    terrain_slope_x=slope,
  )
  r = reward(
    env,
    std=params["std"],
    asset_cfg=params["asset_cfg"],
    terrain_sensor_names=params["terrain_sensor_names"],
  )
  # Should be penalized since robot doesn't match terrain.
  assert r.item() < 0.95


def test_terrain_aware_flat_ground_matches_world_up():
  """On flat terrain, terrain-aware and world-up should give same reward."""
  quat = _quat_from_roll(math.radians(15))
  env_t, reward_t, params_t = _make_env_and_reward(
    terrain_sensor_names=("terrain_scan",),
    body_quat_w=quat,
  )
  env_w, reward_w, params_w = _make_env_and_reward(body_quat_w=quat)

  r_terrain = reward_t(
    env_t,
    std=params_t["std"],
    asset_cfg=params_t["asset_cfg"],
    terrain_sensor_names=params_t["terrain_sensor_names"],
  )
  r_world = reward_w(env_w, std=params_w["std"], asset_cfg=params_w["asset_cfg"])

  torch.testing.assert_close(r_terrain, r_world, atol=0.02, rtol=0.02)


def test_batch_consistency():
  """Multiple envs with different orientations get independent rewards."""
  B = 4
  quats = torch.zeros(B, 4)
  quats[:, 0] = 1.0  # All identity.
  # Tilt env 2 by 45°.
  quats[2] = _quat_from_roll(math.radians(45))[0]

  env, reward, params = _make_env_and_reward(body_quat_w=quats)
  r = reward(env, std=params["std"], asset_cfg=params["asset_cfg"])

  assert r.shape == (B,)
  # Env 0, 1, 3 should be ~1, env 2 should be lower.
  assert r[0].item() > 0.99
  assert r[1].item() > 0.99
  assert r[2].item() < 0.7
  assert r[3].item() > 0.99


def _make_feet_swing(phase: torch.Tensor, in_air: torch.Tensor, moving: torch.Tensor):
  """Mock env + feet_swing for ParameterWalk-style window tests.

  Args:
    phase: [B] gait phase in [0, 1).
    in_air: [B, 2] bool/float — column 0 left, 1 right (found==0).
    moving: [B] bool command gate.
  """
  from unittest.mock import patch

  from mjlab.sensor import ContactSensor
  from mjlab.tasks.velocity.mdp.rewards import feet_swing

  B = phase.shape[0]
  contact = MagicMock(spec=ContactSensor)
  contact.primary_names = ("left_foot_link", "right_foot_link")
  found = (~in_air.bool()).float()  # found > 0 when not in air
  contact_data = MagicMock()
  contact_data.found = found
  type(contact).data = PropertyMock(return_value=contact_data)

  env = MagicMock()
  env.num_envs = B
  env.device = phase.device
  env.extras = {"log": {}}
  env.scene.__getitem__ = MagicMock(return_value=contact)

  cfg = MagicMock(spec=RewardTermCfg)
  cfg.params = {
    "sensor_name": "feet_ground_contact",
    "left_foot_name": "left_foot_link",
    "right_foot_name": "right_foot_link",
  }
  reward_fn = feet_swing(cfg, env)

  def _call():
    with patch(
      "mjlab.tasks.velocity.mdp.rewards.advance_gait_phase",
      return_value=(phase, moving),
    ):
      return reward_fn(
        env,
        sensor_name="feet_ground_contact",
        period=0.6,
        swing_period=0.2,
        command_name="twist",
        command_threshold=0.05,
      )

  return _call


def test_feet_swing_rewards_airborne_in_window():
  """Left air at φ=0.25 and right air at φ=0.75 each score +1."""
  phase = torch.tensor([0.25, 0.75, 0.0])
  in_air = torch.tensor(
    [
      [True, False],  # left swing window, left air → 1
      [False, True],  # right swing window, right air → 1
      [True, True],  # outside windows → 0
    ]
  )
  moving = torch.tensor([True, True, True])
  r = _make_feet_swing(phase, in_air, moving)()
  assert r.shape == (3,)
  torch.testing.assert_close(r, torch.tensor([1.0, 1.0, 0.0]))


def test_feet_swing_zero_when_standing_or_planted():
  """Standing (not moving) or planted feet in window → 0."""
  phase = torch.tensor([0.25, 0.25])
  in_air = torch.tensor([[True, False], [False, False]])
  moving = torch.tensor([False, True])  # env0 standing; env1 planted
  r = _make_feet_swing(phase, in_air, moving)()
  torch.testing.assert_close(r, torch.tensor([0.0, 0.0]))


def test_body_ang_vel_penalty_scales_with_command_speed():
  from mjlab.tasks.velocity.mdp.rewards import body_angular_velocity_penalty

  env = MagicMock()
  asset = MagicMock()
  ang = torch.zeros(2, 1, 3)
  ang[:, 0, 0] = 1.0  # roll rate → cost 1.0 before speed scale
  asset.data.body_link_ang_vel_w = ang
  env.scene = {"robot": asset}
  env.command_manager.get_command.return_value = torch.tensor(
    [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]
  )
  cfg = SceneEntityCfg("robot", body_ids=[0])
  cost = body_angular_velocity_penalty(
    env, asset_cfg=cfg, command_name="twist", speed_ref=1.0
  )
  torch.testing.assert_close(cost, torch.tensor([1.0, 2.0]))


def test_nubots_quality_torso_swing_penalties():
  from mjlab.tasks.velocity.config.k1.env_cfgs import (
    booster_k1_nubots_quality_env_cfg,
  )
  from mjlab.tasks.velocity.mdp.rewards import angular_momentum_penalty

  cfg = booster_k1_nubots_quality_env_cfg(play=False)
  assert cfg.rewards["ang_vel_xy"].weight == -0.6
  assert cfg.rewards["ang_vel_xy"].params["command_name"] == "twist"
  assert cfg.rewards["ang_vel_xy"].params["speed_ref"] == 2.0
  assert cfg.rewards["orientation"].weight == -8.0
  assert cfg.rewards["orientation"].params["speed_ref"] == 2.0
  assert cfg.rewards["angular_momentum"].func is angular_momentum_penalty
  assert cfg.rewards["angular_momentum"].weight == -0.2
  assert cfg.rewards["collision"].weight == -1.75


def test_nubots_quality_unlocks_arm_swing():
  """The momentum penalty needs shoulder authority to act through."""
  from mjlab.tasks.velocity.config.k1.env_cfgs import (
    booster_k1_nubots_quality_env_cfg,
    booster_k1_nubots_rough_env_cfg,
  )

  cfg = booster_k1_nubots_quality_env_cfg(play=False)
  action = cfg.actions["joint_pos"]
  assert action.scale["Left_Shoulder_Pitch"] == pytest.approx(0.30)
  assert action.scale["Right_Shoulder_Pitch"] == pytest.approx(0.30)
  assert action.scale["Left_Shoulder_Roll"] == pytest.approx(0.12)
  assert action.clip["Left_Shoulder_Pitch"] == pytest.approx(
    (-math.radians(25.0), math.radians(25.0))
  )
  assert action.clip["Right_Shoulder_Roll"] == pytest.approx(
    (1.3 - math.radians(15.0), 1.3 + math.radians(15.0))
  )

  # Deploy lineage keeps the tight shoulder bands.
  rough = booster_k1_nubots_rough_env_cfg(play=False)
  assert rough.actions["joint_pos"].scale["Left_Shoulder_Pitch"] == pytest.approx(0.12)
  assert rough.actions["joint_pos"].clip["Left_Shoulder_Pitch"][1] == pytest.approx(
    math.radians(12.0)
  )


def _make_feet_gait(
  phase: torch.Tensor,
  contact: torch.Tensor,
  moving: torch.Tensor,
  stance_fraction: float,
):
  """Mock env + feet_gait for schedule-matching tests.

  Args:
    phase: [B] gait phase in [0, 1).
    contact: [B, 2] bool — column 0 left, 1 right (True = foot planted).
    moving: [B] bool command gate.
    stance_fraction: duty factor of the reference schedule.
  """
  from unittest.mock import patch

  from mjlab.sensor import ContactSensor
  from mjlab.tasks.velocity.mdp.rewards import feet_gait

  sensor = MagicMock(spec=ContactSensor)
  sensor.primary_names = ("left_foot_link", "right_foot_link")
  sensor_data = MagicMock()
  sensor_data.found = contact.float()
  type(sensor).data = PropertyMock(return_value=sensor_data)

  env = MagicMock()
  env.num_envs = phase.shape[0]
  env.device = phase.device
  env.common_step_counter = 0
  env.extras = {"log": {}}
  env.scene.__getitem__ = MagicMock(return_value=sensor)

  cfg = MagicMock(spec=RewardTermCfg)
  cfg.params = {
    "sensor_name": "feet_ground_contact",
    "left_foot_name": "left_foot_link",
    "right_foot_name": "right_foot_link",
  }
  reward_fn = feet_gait(cfg, env)

  def _call():
    with patch(
      "mjlab.tasks.velocity.mdp.rewards.advance_gait_phase",
      return_value=(phase, moving),
    ):
      return reward_fn(
        env,
        sensor_name="feet_ground_contact",
        period=0.6,
        command_name="twist",
        stance_fraction=stance_fraction,
        drop_step=int(1e12),
        fade_steps=0,
      )

  return _call


def test_feet_gait_default_stance_fraction_matches_legacy_schedule():
  """At duty 0.5 the windows meet: phi<0.5 is left swing / right stance.

  The boundary phases 0.0 and 0.5 are included deliberately -- the windows are
  half-open, so the default must reproduce the legacy ``phase >= 0.5``
  schedule there and not merely in the window interiors.
  """
  phase = torch.tensor([0.25, 0.25, 0.75, 0.75, 0.0, 0.5])
  contact = torch.tensor(
    [
      [False, True],  # left swinging, right planted -> both correct
      [True, False],  # exactly inverted -> both wrong
      [True, False],  # left planted, right swinging -> both correct
      [False, True],  # inverted -> both wrong
      [False, True],  # phi=0.0 starts left swing -> both correct
      [True, False],  # phi=0.5 starts right swing -> both correct
    ]
  )
  moving = torch.ones(6, dtype=torch.bool)
  r = _make_feet_gait(phase, contact, moving, stance_fraction=0.5)()
  torch.testing.assert_close(r, torch.tensor([1.0, 0.0, 1.0, 0.0, 1.0, 1.0]))


def test_feet_gait_stance_fraction_creates_double_support():
  """Above duty 0.5 the swing windows shrink and leave double support gaps."""
  # duty 0.6 -> swing half-width 0.2, so left swings on (0.05, 0.45) and the
  # exchange phases 0.5 / 1.0 expect BOTH feet planted.
  phase = torch.tensor([0.5, 0.5, 0.25])
  contact = torch.tensor(
    [
      [True, True],  # double support at the exchange -> correct
      [False, True],  # left airborne during double support -> half wrong
      [False, True],  # mid left-swing -> correct
    ]
  )
  moving = torch.tensor([True, True, True])
  r = _make_feet_gait(phase, contact, moving, stance_fraction=0.6)()
  torch.testing.assert_close(r, torch.tensor([1.0, 0.5, 1.0]))

  # At duty 0.5 that same exchange phase permits no double support, so the
  # fully-planted case is now half wrong. This is what the new parameter buys.
  legacy = _make_feet_gait(
    phase[:1], contact[:1], moving[:1], stance_fraction=0.5
  )()
  torch.testing.assert_close(legacy, torch.tensor([0.5]))


def test_feet_gait_zero_when_standing():
  phase = torch.tensor([0.25])
  contact = torch.tensor([[False, True]])  # would otherwise score 1.0
  r = _make_feet_gait(phase, contact, torch.tensor([False]), stance_fraction=0.5)()
  torch.testing.assert_close(r, torch.tensor([0.0]))


def test_tracking_reward_scales_with_commanded_speed():
  """speed_ref makes the positive budget grow with the command.

  Without it the tracking terms are bounded exponentials capped at 1, so income
  is flat in speed while penalties grow -- the sum goes negative and
  only_positive_rewards clamps away the gradient.
  """
  from unittest.mock import patch

  from mjlab.tasks.velocity.mdp.rewards import track_lin_vel_axis

  env = MagicMock()
  asset = MagicMock()
  env.scene = {"robot": asset}
  # Perfect tracking at 0 and at 1.5 m/s.
  command = torch.tensor([[0.0, 0.0, 0.0], [1.5, 0.0, 0.0]])
  env.command_manager.get_command.return_value = command
  measured = command[:, :3].clone()

  def _call(speed_ref: float):
    with patch(
      "mjlab.tasks.velocity.mdp.rewards._ema_filtered_base_vel",
      return_value=(measured, torch.zeros_like(measured)),
    ):
      return track_lin_vel_axis(
        env, axis=0, command_name="twist", speed_ref=speed_ref
      )

  # speed_ref=0 disables scaling: both cap at 1.0 regardless of command.
  torch.testing.assert_close(_call(0.0), torch.tensor([1.0, 1.0]))
  # speed_ref=1.5 pays 1 + 1.5/1.5 = 2x for the same tracking quality at speed.
  torch.testing.assert_close(_call(1.5), torch.tensor([1.0, 2.0]))


def test_nubots_speed_cfg_restores_gradient_and_cadence():
  from mjlab.tasks.velocity.config.k1.env_cfgs import (
    booster_k1_nubots_speed_env_cfg,
  )
  from mjlab.tasks.velocity.mdp.rewards import feet_gait

  cfg = booster_k1_nubots_speed_env_cfg(play=False)

  # Budget: tilt penalties cut and de-scaled, tracking income scaled with speed.
  assert cfg.rewards["ang_vel_xy"].weight == -0.15
  assert cfg.rewards["ang_vel_xy"].params["speed_ref"] == 4.0
  assert cfg.rewards["orientation"].weight == -4.0
  assert cfg.rewards["orientation"].params["speed_ref"] == 4.0
  for name in ("tracking_lin_vel_x", "tracking_lin_vel_y", "tracking_ang_vel"):
    assert cfg.rewards[name].params["speed_ref"] == 1.5

  # Cadence: two-sided schedule term present, with double support...
  gait = cfg.rewards["gait"]
  assert gait.func is feet_gait
  assert gait.params["stance_fraction"] == 0.60
  # ...and never faded out, or cadence enforcement silently disappears.
  assert gait.params["drop_step"] >= int(1e12)
  assert gait.params["fade_steps"] == 0

  # The penalty_scale curriculum must not scale a positive shaping term.
  assert "gait" not in cfg.curriculum["penalty_scale"].params["reward_names"]

  # Commands opened up to the target envelope, with cadence headroom past the
  # 2.73 Hz the old lineage free-ran at.
  twist = cfg.commands["twist"]
  assert twist.ranges.lin_vel_x == (-0.6, 2.0)
  assert twist.ranges.ang_vel_z == (-1.5, 1.5)
  assert twist.ranges.gait_frequency == (1.6, 3.4)


def test_nubots_speed_runner_is_configured_for_scratch():
  from mjlab.tasks.velocity.config.k1.rl_cfg import (
    booster_k1_nubots_speed_ppo_runner_cfg,
  )

  cfg = booster_k1_nubots_speed_ppo_runner_cfg()
  # Early stop on an episode-length drop would fire on normal early thrash.
  assert cfg.early_stop_enabled is False
  assert cfg.max_iterations == 60_000
  assert cfg.algorithm.learning_rate == 1.0e-4
  # Adaptive clamps to a 1e-5 floor and chases KL, overriding the request.
  assert cfg.algorithm.schedule == "fixed"


def test_k1_env_cfg_includes_feet_swing():
  from mjlab.tasks.velocity.config.k1.env_cfgs import booster_k1_flat_env_cfg
  from mjlab.tasks.velocity.mdp import walk_params
  from mjlab.tasks.velocity.mdp.rewards import feet_swing

  cfg = booster_k1_flat_env_cfg(play=False)
  term = cfg.rewards["feet_swing"]
  assert term.func is feet_swing
  assert term.weight == 1.0
  assert term.params["swing_period"] == walk_params.SWING_PERIOD
  twist = cfg.commands["twist"]
  assert twist.ranges.gait_frequency == walk_params.GAIT_FREQUENCY_RANGE


def test_htwk_nubots_reward_setup_matches_teacher():
  from mjlab.tasks.velocity.config.k1.env_cfgs import (
    booster_k1_nubots_htwk_env_cfg,
  )
  from mjlab.tasks.velocity.mdp import rewards

  cfg = booster_k1_nubots_htwk_env_cfg(play=False)
  expected = {
    "survival": 0.25,
    "tracking_lin_vel_x": 2.0,
    "tracking_lin_vel_y": 2.0,
    "tracking_ang_vel": 1.5,
    "base_height": -8.0,
    "orientation": -8.0,
    "lin_vel_z": -2.0,
    "ang_vel_xy": -0.2,
    "torques": -3.0e-5,
    "torque_tiredness": -1.0e-3,
    "power": -3.0e-4,
    "dof_vel": -2.0e-5,
    "dof_acc": -1.0e-7,
    "root_acc": -1.0e-5,
    "action_rate": -0.1,
    "dof_pos_limits": -1.0,
    "collision": -1.0,
    "foot_foot_collision": -2.0,
    "feet_slip": -0.1,
    "feet_roll": -0.2,
    "feet_pitch": -0.1,
    "foot_yaw_l": -1.0,
    "foot_yaw_r": -1.0,
    "feet_yaw_diff": -0.5,
    "feet_yaw_mean": -0.5,
    "feet_offset_x": -12.0,
    "feet_offset_y": -12.0,
    "feet_minimum_separation": -2.0,
    "feet_swing": 3.0,
    "shoulder_deviation": -3.0,
  }
  assert set(cfg.rewards) == set(expected)
  for name, weight in expected.items():
    assert cfg.rewards[name].weight == pytest.approx(weight)

  assert cfg.rewards["orientation"].func is rewards.htwk_orientation_target
  assert cfg.rewards["feet_offset_x"].func is rewards.htwk_feet_offset_x
  assert cfg.rewards["feet_offset_y"].params["feet_distance_ref"] == pytest.approx(0.18)
  assert cfg.rewards["feet_minimum_separation"].func is (
    rewards.htwk_feet_minimum_separation
  )
  assert cfg.rewards["foot_foot_collision"].func is rewards.htwk_foot_foot_collision
  assert cfg.rewards["feet_swing"].func is rewards.htwk_feet_swing
  assert cfg.rewards["shoulder_deviation"].func is rewards.htwk_shoulder_deviation_l1
  assert "gait" not in cfg.rewards
  assert "feet_distance" not in cfg.rewards

  twist = cfg.commands["twist"]
  assert twist.ranges.lin_vel_x == (-1.0, 2.0)
  assert twist.ranges.lin_vel_y == (-1.0, 1.0)
  assert twist.ranges.ang_vel_z == (-1.6, 1.6)
  assert twist.ranges.gait_frequency == (1.5, 3.0)
  assert twist.parameter_walk_ranges == {
    "foot_yaw_l": (-0.7, 0.7),
    "foot_yaw_r": (-0.7, 0.7),
    "body_pitch": (-0.1, 0.3),
    "body_roll": (-0.1, 0.1),
    "feet_offset_x": (-0.15, 0.15),
    "feet_offset_y": (-0.08, 0.15),
  }
  assert twist.vel_curriculum is True
  assert cfg.curriculum["shoulder_release"].params["start_step"] == 60_000


def test_htwk_orientation_uses_commanded_pitch_and_roll():
  from mjlab.tasks.velocity.mdp.rewards import htwk_orientation_target

  env = MagicMock()
  asset = MagicMock()
  env.scene = {"robot": asset}
  asset.data.root_link_quat_w = quat_from_euler_xyz(
    torch.tensor([0.10]), torch.tensor([0.20]), torch.tensor([0.0])
  )
  command = torch.zeros(1, 10)
  command[0, 6] = 0.05  # body pitch target
  command[0, 7] = -0.03  # body roll target
  env.command_manager.get_command.return_value = command

  cost = htwk_orientation_target(env, command_name="twist")
  torch.testing.assert_close(cost, torch.tensor([0.13**2 + 0.15**2]))


def test_htwk_parameter_walk_rewards_reject_legacy_command():
  from mjlab.tasks.velocity.mdp.rewards import htwk_orientation_target

  env = MagicMock()
  env.command_manager.get_command.return_value = torch.zeros(1, 4)
  with pytest.raises(ValueError, match="10-D"):
    htwk_orientation_target(env, command_name="twist")


def test_htwk_foot_offset_uses_command_target_and_velocity_gate():
  from mjlab.tasks.velocity.mdp.rewards import htwk_feet_offset_x

  env = MagicMock()
  asset = MagicMock()
  env.scene = {"robot": asset}
  asset.data.body_link_pos_w = torch.tensor(
    [[[0.10, 0.08, 0.0], [-0.10, -0.08, 0.0]]]
  )
  asset.data.root_link_quat_w = _identity_quat(1)
  env.command_manager.get_command.return_value = torch.tensor(
    [[0.5, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.0]]
  )
  feet = SceneEntityCfg("robot", body_ids=slice(0, 2))

  cost = htwk_feet_offset_x(
    env, command_name="twist", max_vel=1.0, asset_cfg=feet
  )
  # |0.2 - 0.1| clipped at 0.1, then (1 - 0.5)^2 velocity gate.
  torch.testing.assert_close(cost, torch.tensor([0.025]))


def test_htwk_y_offset_is_relative_to_nominal_foot_distance():
  from mjlab.tasks.velocity.mdp.rewards import htwk_feet_offset_y

  env = MagicMock()
  asset = MagicMock()
  env.scene = {"robot": asset}
  asset.data.body_link_pos_w = torch.tensor(
    [[[0.0, 0.19, 0.0], [0.0, 0.0, 0.0]]]
  )
  asset.data.root_link_quat_w = _identity_quat(1)
  env.command_manager.get_command.return_value = torch.tensor(
    [[0.5, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01]]
  )
  feet = SceneEntityCfg("robot", body_ids=slice(0, 2))

  cost = htwk_feet_offset_y(
    env,
    command_name="twist",
    max_vel=1.0,
    feet_distance_ref=0.18,
    asset_cfg=feet,
  )
  torch.testing.assert_close(cost, torch.zeros(1))


def test_htwk_feet_offset_x_keeps_min_velocity_scale_at_high_speed():
  from mjlab.tasks.velocity.mdp.rewards import htwk_feet_offset_x

  env = MagicMock()
  asset = MagicMock()
  env.scene = {"robot": asset}
  asset.data.body_link_pos_w = torch.tensor(
    [[[0.10, 0.08, 0.0], [-0.10, -0.08, 0.0]]]
  )
  asset.data.root_link_quat_w = _identity_quat(1)
  env.command_manager.get_command.return_value = torch.tensor(
    [[1.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.0]]
  )
  feet = SceneEntityCfg("robot", body_ids=slice(0, 2))

  cost_without_floor = htwk_feet_offset_x(
    env, command_name="twist", max_vel=1.0, asset_cfg=feet
  )
  cost_with_floor = htwk_feet_offset_x(
    env,
    command_name="twist",
    max_vel=1.0,
    min_velocity_scale=0.35,
    asset_cfg=feet,
  )
  torch.testing.assert_close(cost_without_floor, torch.zeros(1))
  torch.testing.assert_close(cost_with_floor, torch.tensor([0.035]))


def test_htwk_feet_site_xy_separation_penalizes_close_sites():
  from mjlab.tasks.velocity.mdp.rewards import htwk_feet_site_xy_separation

  env = MagicMock()
  asset = MagicMock()
  env.scene = {"robot": asset}
  asset.data.site_pos_w = torch.tensor(
    [[[0.0, 0.06, 0.0], [0.0, -0.05, 0.0]]]
  )
  asset.data.root_link_quat_w = _identity_quat(1)
  sites = SceneEntityCfg("robot", site_ids=slice(0, 2))

  cost = htwk_feet_site_xy_separation(
    env, min_separation=0.14, asset_cfg=sites
  )
  # Lateral separation is 0.11 m: ((0.14 - 0.11) / 0.14)^2.
  torch.testing.assert_close(cost, torch.tensor([0.045918367]))


def test_htwk_minimum_feet_separation_is_a_smooth_squared_hinge():
  from mjlab.tasks.velocity.mdp.rewards import htwk_feet_minimum_separation

  env = MagicMock()
  asset = MagicMock()
  env.scene = {"robot": asset}
  asset.data.body_link_pos_w = torch.tensor(
    [[[0.0, 0.05, 0.0], [0.0, -0.04, 0.0]]]
  )
  asset.data.root_link_quat_w = _identity_quat(1)
  feet = SceneEntityCfg("robot", body_ids=slice(0, 2))

  cost = htwk_feet_minimum_separation(
    env, min_separation=0.10, asset_cfg=feet
  )
  # Separation is 0.09 m: ((0.10 - 0.09) / 0.10)^2 = 0.01.
  torch.testing.assert_close(cost, torch.tensor([0.01]))


def test_htwk_knee_separation_increases_below_safe_distance():
  from mjlab.tasks.velocity.mdp.rewards import htwk_knee_separation

  env = MagicMock()
  asset = MagicMock()
  env.scene = {"robot": asset}
  asset.data.body_link_pos_w = torch.tensor(
    [
      [[0.0, 0.18, 0.0], [0.0, 0.0, 0.0]],
      [[0.0, 0.129, 0.0], [0.0, 0.0, 0.0]],
      [[0.0, 0.09, 0.0], [0.0, 0.0, 0.0]],
    ]
  )
  knees = SceneEntityCfg("robot", body_ids=slice(0, 2))

  cost = htwk_knee_separation(
    env, safe_distance=0.15, softness=0.01, asset_cfg=knees
  )
  assert cost.shape == (3,)
  assert cost[0] < cost[1] < cost[2]


def test_htwk_hip_roll_barrier_has_deadband():
  from mjlab.tasks.velocity.mdp.rewards import htwk_hip_roll_barrier

  env = MagicMock()
  asset = MagicMock()
  env.scene = {"robot": asset}
  asset.data.default_joint_pos = torch.tensor([[0.04, -0.04]]).expand(3, -1)
  asset.data.joint_pos = torch.tensor(
    [
      [0.04 + 0.05, -0.04 - 0.05],
      [0.04 + 0.12, -0.04 - 0.12],
      [0.04 + 0.25, -0.04 - 0.25],
    ]
  )
  hips = SceneEntityCfg("robot", joint_ids=slice(0, 2))

  cost = htwk_hip_roll_barrier(
    env, max_deviation=0.12, softness=0.02, asset_cfg=hips
  )
  assert cost.shape == (3,)
  assert cost[0] < cost[1] < cost[2]


def test_htwk_feet_orientation_contact_gated_zeros_in_swing():
  from mjlab.tasks.velocity.mdp.rewards import htwk_feet_orientation_contact_gated

  env = MagicMock()
  asset = MagicMock()
  sensor = MagicMock()
  env.scene = {"robot": asset, "feet_ground_contact": sensor}
  sensor.data.force_history = None
  sensor.data.force = torch.tensor([[[0.0, 5.0]]])  # right foot only
  asset.data.body_link_quat_w = torch.tensor(
    [[[1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]]]
  )
  feet = SceneEntityCfg("robot", body_ids=slice(0, 2))

  cost = htwk_feet_orientation_contact_gated(
    env, axis=1, sensor_name="feet_ground_contact", asset_cfg=feet
  )
  torch.testing.assert_close(cost, torch.zeros(1))


def test_htwk_swing_sole_clearance_penalizes_toe_drag():
  from mjlab.tasks.velocity.mdp.rewards import htwk_swing_sole_clearance

  env = MagicMock()
  env.num_envs = 1
  env.extras = {"log": {}}
  height_sensor = MagicMock()
  height_sensor.data.heights = torch.tensor([[0.01, 0.07]])
  env.scene = {"foot_height_scan": height_sensor}
  term = MagicMock()
  term.gait_process = torch.tensor([0.25])
  term.gait_frequency = torch.tensor([2.0])
  env.command_manager.get_term.return_value = term
  env.command_manager.get_command.return_value = torch.zeros(1, 12)

  signal = htwk_swing_sole_clearance(
    env,
    height_sensor_name="foot_height_scan",
    min_clearance=0.04,
    target_clearance=0.06,
  )
  # Left foot drags (0.01 < 0.04) during left swing; right foot lifts.
  assert signal.item() < 1.0
  assert signal.item() > 0.0


def test_htwk_swing_sole_clearance_rewards_full_lift():
  from mjlab.tasks.velocity.mdp.rewards import htwk_swing_sole_clearance

  env = MagicMock()
  env.num_envs = 1
  env.extras = {"log": {}}
  height_sensor = MagicMock()
  height_sensor.data.heights = torch.tensor([[0.02, 0.08]])
  env.scene = {"foot_height_scan": height_sensor}
  term = MagicMock()
  term.gait_process = torch.tensor([0.75])
  term.gait_frequency = torch.tensor([2.0])
  env.command_manager.get_term.return_value = term
  env.command_manager.get_command.return_value = torch.zeros(1, 12)

  signal = htwk_swing_sole_clearance(
    env,
    height_sensor_name="foot_height_scan",
    min_clearance=0.04,
    target_clearance=0.06,
  )
  # Right swing with high clearance should dominate over left (not swinging).
  torch.testing.assert_close(signal, torch.tensor([1.0]))

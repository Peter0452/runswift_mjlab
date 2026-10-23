"""K1 kick tracking task configuration."""

from pathlib import Path

import mujoco
import numpy as np
import pytest
import torch

from k1.robot.k1_constants import K1_ACTION_SCALE
from mjlab.asset_zoo.props.ball import get_ball_radius
from mjlab.asset_zoo.props.goal import (
  GOAL_DIVISION_SCALE,
  MID_GOAL_HEIGHT,
  MID_GOAL_WIDTH,
  get_goal_spec,
)
from mjlab.envs.mdp.actions import JointPositionActionCfg
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg
from mjlab.tasks.tracking.config.k1.env_cfgs import (
  _GOAL_REWARD_STD,
  K1_TRACKED_BODY_NAMES,
)
from mjlab.tasks.tracking.config.k1.kick_motion import KICK_TRACKING_NPZ
from mjlab.tasks.tracking.mdp import MotionCommandCfg
from mjlab.tasks.tracking.mdp.commands import (
  MotionCommand,
  estimate_clip_strike_positions,
)
from mjlab.tasks.tracking.mdp.events import goal_yaw_facing_origin
from mjlab.tasks.tracking.mdp.stand_blend import build_stand_blend

TASK = "Mjlab-Tracking-Flat-Booster-K1-Kick"
STAGE2 = "Mjlab-Tracking-Flat-Booster-K1-Kick-Stage2"
BOX = "Mjlab-Tracking-Flat-Booster-K1-Kick-Box"


def test_k1_kick_tracking_matches_prior_setup() -> None:
  cfg = load_env_cfg(TASK)
  motion = cfg.commands["motion"]
  assert isinstance(motion, MotionCommandCfg)
  assert motion.anchor_body_name == "Trunk"
  assert motion.body_names[0] == "Trunk"
  assert motion.body_names == K1_TRACKED_BODY_NAMES
  assert motion.sampling_mode == "adaptive"
  assert motion.adaptive_kernel_size == 3
  assert Path(motion.motion_file).is_file()

  actor_terms = cfg.observations["actor"].terms
  assert "base_lin_vel" not in actor_terms
  assert "motion_anchor_pos_b" in actor_terms
  assert "motion_style_z" in actor_terms
  assert actor_terms["motion_style_z"].history_length == 0
  assert actor_terms["joint_pos"].history_length == 5
  assert "base_lin_vel" in cfg.observations["critic"].terms
  assert "motion_style_z" in cfg.observations["critic"].terms
  assert "ball" in cfg.scene.entities
  assert "goal" in cfg.scene.entities
  assert cfg.scene.entities["goal"].spec_fn is get_goal_spec
  assert cfg.events["place_goal"].mode == "post_reset"
  assert cfg.scene.env_spacing == 20.0
  assert cfg.sim.nconmax == 128
  assert "goal" in cfg.commands
  goal = cfg.commands["goal"]
  assert goal.distance_range == (4.0, 8.0)
  assert goal.angle_range == (0.0, 0.0)
  assert _GOAL_REWARD_STD == 1.0
  for group in ("actor", "critic"):
    terms = cfg.observations[group].terms
    assert terms["ball_pos_b"].history_length == 5
    assert terms["target_pos_b"].history_length == 5

  action = cfg.actions["joint_pos"]
  assert isinstance(action, JointPositionActionCfg)
  assert action.scale == K1_ACTION_SCALE
  assert cfg.scene.num_envs == 4096
  assert "error_ball_to_target" not in cfg.rewards
  assert cfg.rewards["joint_limit"].weight == -10.0
  assert cfg.rewards["feet_slip"].weight == -0.025
  assert cfg.rewards["no_fly"].weight == -0.05
  base_height = cfg.rewards["base_height"]
  assert base_height.weight == -20.0
  assert base_height.params["threshold"] == 0.48
  assert cfg.rewards["action_smoothness"].weight == -0.0015
  assert any(sensor.name == "feet_ground_contact" for sensor in cfg.scene.sensors)
  fall = cfg.rewards["ee_body_pos_fall"]
  assert fall.weight == -100.0
  assert fall.params["threshold"] == 0.25
  assert (
    fall.params["body_names"] == cfg.terminations["ee_body_pos"].params["body_names"]
  )


def test_kick_dr_matches_amp_walk() -> None:
  cfg = load_env_cfg(STAGE2)
  motion = cfg.commands["motion"]
  assert isinstance(motion, MotionCommandCfg)
  assert cfg.events["foot_friction"].params["ranges"] == (0.75, 1.25)
  assert cfg.events["encoder_bias"].params["bias_range"] == (-0.015, 0.015)
  assert "base_com" not in cfg.events
  assert cfg.events["pd_gains"].params["kp_range"] == (0.8, 1.2)
  assert cfg.events["pd_gains"].params["kd_range"] == (0.8, 1.2)
  assert cfg.events["trunk_inertia"].params["alpha_range"] == (-0.05, 0.05)
  assert cfg.events["trunk_inertia"].params["t_range"] == (-0.05, 0.05)
  assert cfg.events["limb_inertia"].params["t_range"] == (-0.025, 0.025)
  assert cfg.events["push_robot"].interval_range_s == (1.5, 4.0)
  assert cfg.events["push_robot"].params["velocity_range"]["x"] == (-0.28, 0.28)
  assert "terrain_contact" in cfg.events
  assert motion.velocity_range["x"] == (-1.0, 1.0)
  assert motion.velocity_range["yaw"] == (-0.5, 0.5)
  assert motion.joint_velocity_range == (-0.1, 0.1)
  noise = cfg.observations["actor"].terms["joint_vel"].noise
  assert noise is not None
  assert noise.n_min == -1.5
  assert noise.n_max == 1.5
  robot = cfg.scene.entities["robot"]
  assert robot.articulation is not None
  effort_by_expr = {
    ".*_Hip_Pitch": 68.0,
    ".*_Hip_Roll": 76.0,
    ".*_Hip_Yaw": 38.3,
    ".*_Knee_Pitch": 112.0,
    ".*_Ankle_Pitch": 38.3,
    ".*_Ankle_Roll": 38.3,
    ".*_Shoulder_Pitch": 14.0,
    "Head_Yaw": 6.0,
  }
  for actuator in robot.articulation.actuators:
    assert actuator.delay_min_lag == 2
    assert actuator.delay_max_lag == 8
    assert actuator.delay_hold_prob == 0.3
    assert actuator.effort_limit == pytest.approx(
      effort_by_expr[actuator.target_names_expr[0]]
    )
  play = load_env_cfg(STAGE2, play=True)
  play_motion = play.commands["motion"]
  assert isinstance(play_motion, MotionCommandCfg)
  assert play_motion.joint_velocity_range == (0.0, 0.0)
  assert "push_robot" not in play.events


def test_k1_kick_tracking_network() -> None:
  agent = load_rl_cfg(TASK)
  assert agent.actor.hidden_dims == (512, 256, 128)
  assert agent.critic.hidden_dims == (512, 256, 128)
  assert agent.actor.distribution_cfg["init_std"] == 1.0
  assert agent.algorithm.learning_rate == 5.0e-5


def test_k1_kick_motion_is_multi_clip() -> None:
  cfg = load_env_cfg(TASK)
  motion = cfg.commands["motion"]
  assert isinstance(motion, MotionCommandCfg)
  with np.load(motion.motion_file) as data:
    assert data["joint_pos"].shape[1] == 22
    assert data["joint_pos"].shape[0] == data["joint_vel"].shape[0]
    assert data["body_pos_w"].shape[0] == data["joint_pos"].shape[0]
    assert data["body_quat_w"].shape[-1] == 4
    assert float(data["fps"][0]) == 50.0
    ends = data["clip_ends"]
    names = [str(name) for name in data["clip_names"]]
    right = [
      "10_01_stageii",
      "10_02_stageii",
      "10_03_stageii",
      "10_05_stageii",
      "11_01_stageii",
    ]
    assert names == [name for stem in right for name in (stem, f"{stem}_left")]
    assert "10_04_stageii" not in names
    assert len(ends) == 10
    assert int(ends[-1]) == data["joint_pos"].shape[0]
    assert list(data["body_names"])[0] == "Trunk"
    style = data["clip_z"]
    right_style = np.array(
      [
        [1, 0, 0],
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [0, 0, 1],
      ],
      dtype=np.float32,
    )
    assert style.shape == (10, 3)
    assert list(data["clip_z_names"]) == ["planted", "running", "moving"]
    assert np.array_equal(style[0::2], right_style)
    assert np.array_equal(style[1::2], right_style)
    assert np.array_equal(data["clip_kick_foot"], np.array([0, 1] * 5))


def test_multi_clip_clock_stops_at_each_clip() -> None:
  command = MotionCommand.__new__(MotionCommand)

  class _Motion:
    time_step_total = 10
    clip_ends = torch.tensor([4, 10])

  class _Cfg:
    sampling_mode = "adaptive"

  command.motion = _Motion()
  command.cfg = _Cfg()
  command.time_steps = torch.tensor([3, 4, 9, 10])
  leaving = command._envs_leaving_motion()
  assert leaving.tolist() == [1, 3]

  command.cfg.sampling_mode = "start"
  leaving = command._envs_leaving_motion()
  assert leaving.tolist() == [1, 3]

  class _Styled:
    time_step_total = 10
    clip_ends = torch.tensor([4, 10])
    clip_starts = torch.tensor([0, 4])
    clip_z = torch.tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])

  command.motion = _Styled()
  command.time_steps = torch.tensor([0, 3, 4, 9])
  assert command._clip_index(command.time_steps).tolist() == [0, 0, 1, 1]
  assert torch.equal(
    command.style_z,
    torch.tensor(
      [
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 1.0, 0.0],
      ]
    ),
  )
  restart = command._start_mode_frames(torch.tensor([0, 1, 2, 3]))
  assert restart.tolist() == [0, 0, 4, 0]


def test_play_places_ball_on_each_clip_strike() -> None:
  play = load_env_cfg(TASK, play=True)
  motion = play.commands["motion"]
  assert isinstance(motion, MotionCommandCfg)
  assert motion.place_ball_at_strike is True
  assert motion.strike_body_name == "right_foot_link"
  assert motion.strike_height == get_ball_radius()
  assert play.events["reset_ball"].params["pose_range"] == {}
  trained = load_env_cfg(TASK)
  trained_motion = trained.commands["motion"]
  assert isinstance(trained_motion, MotionCommandCfg)
  assert trained_motion.place_ball_at_strike is False


def test_clip_strike_is_the_descending_foot() -> None:
  foot = torch.tensor(
    [
      [0.0, 0.0, 0.05],
      [0.1, -0.1, 0.20],
      [0.2, -0.2, 0.40],
      [0.3, -0.3, 0.20],
      [0.4, -0.4, 0.05],
    ]
  )
  strike = estimate_clip_strike_positions(foot, torch.tensor([5]), ball_z=0.11)
  assert torch.allclose(strike, torch.tensor([[0.3, -0.3, 0.11]]))

  cfg = load_env_cfg(TASK)
  motion = cfg.commands["motion"]
  assert isinstance(motion, MotionCommandCfg)
  with np.load(motion.motion_file) as data:
    names = list(data["body_names"])
    right_foot = torch.tensor(data["body_pos_w"][:, names.index("right_foot_link")])
    left_foot = torch.tensor(data["body_pos_w"][:, names.index("left_foot_link")])
    ends = torch.tensor(data["clip_ends"])
  expected_right = torch.tensor(
    [
      [0.46, -0.52, 0.11],
      [0.49, -0.58, 0.11],
      [1.19, -0.65, 0.11],
      [1.28, -0.68, 0.11],
      [1.22, -0.64, 0.11],
    ]
  )
  starts = [0, *ends[:-1].tolist()]
  spans = list(zip(starts, ends.tolist(), strict=True))
  right_strikes = []
  left_strikes = []
  for start, end in spans[0::2]:
    right_strikes.append(
      estimate_clip_strike_positions(
        right_foot[start:end], torch.tensor([end - start]), 0.11
      )[0]
    )
  for start, end in spans[1::2]:
    left_strikes.append(
      estimate_clip_strike_positions(
        left_foot[start:end], torch.tensor([end - start]), 0.11
      )[0]
    )
  right_strikes = torch.stack(right_strikes)
  left_strikes = torch.stack(left_strikes)
  assert torch.allclose(right_strikes, expected_right, atol=0.02)
  mirrored = expected_right.clone()
  mirrored[:, 1] *= -1
  assert torch.allclose(left_strikes, mirrored, atol=0.02)


def test_mid_goal_is_two_point_four_by_one_point_six() -> None:
  assert MID_GOAL_WIDTH == 2.40
  assert MID_GOAL_HEIGHT == 1.60
  spec = get_goal_spec("mid")
  scale = GOAL_DIVISION_SCALE["mid"]
  assert np.allclose(spec.meshes[0].scale, (scale, scale, scale))
  model = spec.compile()
  assert isinstance(model, mujoco.MjModel)


def test_stage2_keeps_the_stage1_observation() -> None:
  stage1 = load_env_cfg(TASK)
  stage2 = load_env_cfg(STAGE2)
  for group in ("actor", "critic"):
    assert list(stage1.observations[group].terms) == list(stage2.observations[group].terms)
    for name, term in stage1.observations[group].terms.items():
      other = stage2.observations[group].terms[name]
      assert term.history_length == other.history_length
  assert "error_ball_to_target" not in stage1.rewards
  assert stage1.commands["motion"].sampling_mode == "adaptive"


def test_stage2_places_the_ball_and_pays_for_the_kick() -> None:
  cfg = load_env_cfg(STAGE2)
  motion = cfg.commands["motion"]
  assert isinstance(motion, MotionCommandCfg)
  assert motion.sampling_mode == "prefix"
  assert motion.start_fraction == 0.05
  assert motion.left_clip_prob == 0.6
  assert motion.place_ball_at_strike is True
  assert motion.strike_pos_noise == (0.1, 0.1)
  assert motion.strike_vel_noise == (0.05, 0.05)
  assert cfg.rewards["motion_global_root_pos"].weight == 1.0
  assert cfg.rewards["motion_global_root_ori"].weight == 0.7
  assert cfg.rewards["error_ball_to_target"].weight == 8.0
  assert cfg.rewards["error_ball_to_target"].params["std"] == 1.0
  assert cfg.rewards["ball_contact_orientation"].weight == 1.7
  assert cfg.rewards["robot_feet_ball_distance"].weight == 0.8
  assert cfg.rewards["robot_com_ball_distance"].weight == 0.8
  assert cfg.rewards["robot_torso_ball_distance"].weight == 0.8
  assert cfg.rewards["robot_ball_contact"].weight == 0.8
  assert cfg.rewards["robot_ball_contact_count"].weight == 0.8
  assert cfg.rewards["ball_velocity"].weight == 0.45
  assert cfg.rewards["ball_over_line"].weight == 0.4
  assert cfg.rewards["penalize_weak_foot_contact"].weight == -0.4
  assert cfg.rewards["penalize_self_contact_feet"].weight == -0.16
  assert cfg.terminations["anchor_pos"].params["threshold"] == 0.5
  assert cfg.terminations["ee_body_pos"].params["threshold"] == 0.35
  sensor_names = {sensor.name for sensor in cfg.scene.sensors}
  assert "ball_foot_contact" in sensor_names
  assert "ball_left_foot_contact" in sensor_names
  assert load_rl_cfg(STAGE2).experiment_name == "k1_kick_tracking"

  play = load_env_cfg(STAGE2, play=True)
  play_motion = play.commands["motion"]
  assert isinstance(play_motion, MotionCommandCfg)
  assert play_motion.sampling_mode == "start"
  assert play_motion.strike_pos_noise == (0.0, 0.0)
  assert play_motion.strike_vel_noise == (0.0, 0.0)
  assert "error_ball_to_target" in play.rewards


def test_left_clip_prob_can_draw_only_left_kicks() -> None:
  command = MotionCommand.__new__(MotionCommand)
  command.motion = type("Motion", (), {})()
  command.motion.clip_ends = torch.tensor([10, 20, 30, 40])
  command.motion.clip_starts = torch.tensor([0, 10, 20, 30])
  command.motion.clip_kick_foot = torch.tensor([0, 1, 0, 1])
  command.cfg = type("Cfg", (), {"start_fraction": 1.0, "left_clip_prob": 1.0})()
  command.time_steps = torch.zeros(64, dtype=torch.long)
  command._prefix_sampling(torch.arange(64))
  clip_ids = torch.bucketize(command.time_steps, command.motion.clip_ends, right=True)
  assert torch.all(command.motion.clip_kick_foot[clip_ids] == 1)


def test_prefix_sampling_stays_in_the_opening_of_one_clip() -> None:
  command = MotionCommand.__new__(MotionCommand)
  command.motion = type("Motion", (), {})()
  command.motion.clip_ends = torch.tensor([100, 300])
  command.motion.clip_starts = torch.tensor([0, 100])
  command.cfg = type("Cfg", (), {"start_fraction": 0.05})()
  command.time_steps = torch.zeros(32, dtype=torch.long)
  torch.manual_seed(0)
  command._prefix_sampling(torch.arange(32))
  clip_ids = torch.bucketize(
    command.time_steps, command.motion.clip_ends, right=True
  )
  starts = command.motion.clip_starts[clip_ids]
  spans = command.motion.clip_ends[clip_ids] - starts
  windows = (spans.float() * 0.05).long().clamp(min=1)
  assert torch.all(command.time_steps >= starts)
  assert torch.all(command.time_steps < starts + windows)


def test_box_ball_is_around_each_clip_strike() -> None:
  cfg = load_env_cfg(BOX)
  motion = cfg.commands["motion"]
  assert isinstance(motion, MotionCommandCfg)
  assert motion.ball_spawn_regions is None
  assert motion.ball_spawn_range is None
  assert motion.strike_pos_noise == (0.5, 0.5)
  assert motion.place_ball_at_strike is True
  assert motion.strike_vel_noise == (0.0, 0.0)
  assert motion.stand_after_kick is True
  assert motion.ball_gone_distance == 1.0
  assert motion.stand_height == 0.5125
  assert cfg.rewards["stand_joint_pose"].weight == 1.0
  assert cfg.rewards["foot_sole_penetration"].weight == -50.0
  assert cfg.rewards["joint_velocity_over_motor"].weight == -0.1
  assert load_env_cfg(STAGE2).commands["motion"].stand_after_kick is False
  stage2 = load_env_cfg(STAGE2)
  assert "foot_sole_penetration" not in stage2.rewards
  assert "joint_velocity_over_motor" not in stage2.rewards
  for group in ("actor", "critic"):
    assert list(cfg.observations[group].terms) == list(stage2.observations[group].terms)
  assert cfg.rewards["error_ball_to_target"].weight == 8.0
  for name in (
    "motion_body_pos",
    "motion_body_ori",
    "motion_body_lin_vel",
    "motion_body_ang_vel",
    "motion_global_root_pos",
  ):
    assert cfg.rewards[name].weight == stage2.rewards[name].weight
  assert "stand_joint_pose" not in stage2.rewards
  assert cfg.rewards["motion_global_root_ori"].weight == stage2.rewards[
    "motion_global_root_ori"
  ].weight
  for name in (
    "base_height",
    "ee_body_pos_fall",
    "action_smoothness",
    "action_rate_l2",
    "joint_limit",
  ):
    assert cfg.rewards[name].weight == stage2.rewards[name].weight
  assert cfg.terminations["anchor_pos"].params["threshold"] == 0.5
  assert cfg.terminations["anchor_ori"].params["threshold"] == stage2.terminations[
    "anchor_ori"
  ].params["threshold"]
  assert load_rl_cfg(BOX).experiment_name == "k1_kick_tracking"
  assert stage2.commands["motion"].strike_pos_noise == (0.1, 0.1)

  play = load_env_cfg(BOX, play=True)
  play_motion = play.commands["motion"]
  assert isinstance(play_motion, MotionCommandCfg)
  assert play_motion.sampling_mode == "start"
  assert play_motion.strike_pos_noise == (0.5, 0.5)


def test_stand_blend_stays_supported() -> None:
  cache = build_stand_blend(str(KICK_TRACKING_NPZ), K1_TRACKED_BODY_NAMES)
  report = cache.report
  assert report.ok
  assert report.min_sole_z >= -0.005
  assert report.max_stance_rise <= 0.03
  assert report.max_com_offset <= 0.12
  assert report.max_speed_ratio <= 1.0
  assert report.pd_min_trunk_z >= 0.45
  assert report.pd_max_tilt <= 0.8
  assert cache.joint_pos.shape[1] == cache.steps + 1
  home = cache.joint_pos[:, -1]
  assert torch.allclose(home, home[:1].expand_as(home), atol=1.0e-5)


def test_goal_mouth_faces_the_env_origin() -> None:
  yaw = goal_yaw_facing_origin(torch.tensor([[5.0, 0.0], [0.0, 5.0], [0.0, -5.0]]))
  assert torch.allclose(
    yaw, torch.tensor([torch.pi / 2, torch.pi, 0.0]), atol=1.0e-5
  )

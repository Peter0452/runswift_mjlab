"""Kick stage: touch classification, heading potential, kick speed, wiring."""

from __future__ import annotations

import math

import torch

import mjlab.tasks  # noqa: F401
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg
from mjlab.tasks.velocity.mdp.amp_symmetry import (
  KICK_LOOP_AGE_SLOT,
  augment_symmetries,
  augment_symmetries_kick_loop,
)
from mjlab.tasks.velocity.mdp.approach import (
  SIDE_KICK_COST,
  range_one_hot,
  sample_binned,
  side_aware_angle,
)
from mjlab.tasks.velocity.mdp.kick_loop import (
  RANGE_EDGES,
  TARGET_BINS,
  classify_touch,
  goal_tolerance,
  heading_potential,
  kick_quality_score,
  required_kick_speed,
)

TASK = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"


def test_touch_is_kick_double_touch_or_push() -> None:
  far = torch.tensor([1.0e3])
  t, f = torch.tensor([True]), torch.tensor([False])
  # Launch on contact: kick, not push.
  kick, double, push = classify_touch(
    t, f, torch.tensor([2.0]), torch.tensor([0.0]), far
  )
  assert kick.item() and not double.item() and not push.item()
  # Launch seen the step after the contact ended still counts.
  kick, _, _ = classify_touch(f, t, torch.tensor([2.0]), torch.tensor([0.1]), far)
  assert kick.item()
  # Slow contact: push.
  kick, _, push = classify_touch(t, f, torch.tensor([0.3]), torch.tensor([0.0]), far)
  assert not kick.item() and push.item()
  # New contact 0.2 s after a kick: double touch, never a second kick.
  recent = torch.tensor([0.2])
  kick, double, push = classify_touch(
    t, f, torch.tensor([3.0]), torch.tensor([0.5]), recent
  )
  assert double.item() and not kick.item() and not push.item()
  # Follow-through contact right after the kick is neither.
  _, double, push = classify_touch(
    t, t, torch.tensor([3.0]), torch.tensor([3.0]), recent
  )
  assert not double.item() and not push.item()


def test_heading_potential_ramps_in_and_telescopes() -> None:
  yaw = torch.tensor([1.0])
  assert heading_potential(torch.tensor([2.5]), yaw).item() == 0.0
  assert math.isclose(heading_potential(torch.tensor([0.4]), yaw).item(), -1.0)
  # Same start and end, two paths: the summed differences agree.
  path_a = [(2.5, 1.5), (1.0, 1.5), (0.5, 0.0)]
  path_b = [(2.5, 1.5), (2.2, 0.0), (0.5, 0.0)]

  def total(path: list[tuple[float, float]]) -> float:
    phis = [
      heading_potential(torch.tensor([d]), torch.tensor([y])).item() for d, y in path
    ]
    return sum(b - a for a, b in zip(phis[:-1], phis[1:], strict=True))

  assert math.isclose(total(path_a), total(path_b), abs_tol=1e-6)
  # Turning before the ramp avoids the cost of closing in misaligned.
  closing_misaligned = heading_potential(
    torch.tensor([1.0]), torch.tensor([1.5])
  ) - heading_potential(torch.tensor([2.5]), torch.tensor([1.5]))
  assert closing_misaligned.item() < 0.0


def test_required_kick_speed_matches_measured_roll() -> None:
  # Measured on a plane: 4 m/s rolls about 8.4 m.
  assert abs(required_kick_speed(torch.tensor([8.44])).item() - 4.0) < 0.05
  tol = goal_tolerance(torch.tensor([1.0, 4.0, 10.0]))
  assert torch.allclose(tol, torch.tensor([0.5, 1.0, 1.5]))


def test_target_bins_and_range_one_hot_agree() -> None:
  dist = sample_binned(30_000, TARGET_BINS, "cpu")
  assert dist.min() >= 1.0 and dist.max() <= 20.0
  one_hot = range_one_hot(dist, *RANGE_EDGES)
  share = one_hot.mean(dim=0)
  assert torch.allclose(share, torch.full((3,), 1.0 / 3.0), atol=0.02)
  assert torch.equal(
    range_one_hot(torch.tensor([3.9, 4.0, 8.0]), *RANGE_EDGES),
    torch.eye(3),
  )


def test_stage3_cfg_wiring() -> None:
  cfg = load_env_cfg(TASK)
  assert cfg.episode_length_s == 30.0
  assert cfg.scene.terrain is not None
  # v48: gentle field-like terrain in training (play stays flat).
  assert cfg.scene.terrain.terrain_type == "generator"
  assert load_env_cfg(TASK, play=True).scene.terrain.terrain_type == "plane"
  assert cfg.events["foot_friction"].params["ranges"] == (0.7, 1.4)
  assert cfg.commands["twist"].vision_dropout == 0.02
  assert cfg.commands["twist"].vision_delay_steps == (0, 2)
  assert cfg.commands is not None
  assert cfg.commands["twist"].__class__.__name__ == "KickLoopCommandCfg"
  assert any(s.name == "body_ball_contact" for s in cfg.scene.sensors)
  for name in (
    "ball_vision",
    "kick_dir_alignment",
    "walk_speed",
    "walk_speed_limit",
    "kick_direction",
    "kick_vel",
    "kick_vel_accurate",
    "ball_avoidance",
    "single_feet_avoidance",
  ):
    assert cfg.rewards[name].weight != 0.0, name
  for name in ("approach_stand", "approach_heading", "approach_speed_limit"):
    assert cfg.rewards[name].weight == 0.0
  # Zone-tied time cost fenced the ball off in stage3_v1; a global one replaces it.
  assert "kick_near_ball_time" not in cfg.rewards
  # A global time cost drove the per-step reward negative in stage3_v2.
  assert "kick_time_cost" not in cfg.rewards
  assert cfg.rewards["action_rate_l2"].weight == -0.1
  assert cfg.rewards["dof_pos_limits"].weight == -10.0
  assert cfg.rewards["fall"].weight < 0.0
  # A good kick still outweighs the fall penalty alone; with gamma 0.995 the
  # lost future makes a fall cost more than a kick pays.
  kick = cfg.rewards["kick_direction"].weight + cfg.rewards["kick_vel"].weight
  assert kick > 1.5 * abs(cfg.rewards["fall"].weight)
  assert cfg.commands["twist"].ball_memory is True
  assert cfg.commands["twist"].aim_broad_share == 0.0
  assert cfg.rewards["kick_fall"].weight < cfg.rewards["fall"].weight
  assert cfg.curriculum is not None
  style = cfg.curriculum["amp_style_weight"].params
  assert style["start_weight"] == style["end_weight"] == 0.3
  assert cfg.rewards["trunk_tilt"].weight < 0.0
  rl = load_rl_cfg(TASK)
  assert rl.experiment_name == "k1_kick_stage3_amp"
  assert rl.algorithm.symmetry_cfg is not None
  assert rl.algorithm.symmetry_cfg["data_augmentation_func"].endswith(
    "augment_symmetries_kick_loop"
  )
  assert rl.algorithm.entropy_coef == 0.005
  assert rl.algorithm.gamma == 0.995
  assert rl.actor.distribution_cfg is not None
  assert rl.actor.distribution_cfg["std_range"] == (0.05, 0.6)


def test_kick_loop_mirror_keeps_the_memory_age() -> None:
  from tensordict import TensorDict

  actor = torch.randn(3, 83)
  critic = torch.randn(3, 98)
  actor[:, KICK_LOOP_AGE_SLOT] = torch.tensor([1.0, 0.5, 0.1])
  critic[:, KICK_LOOP_AGE_SLOT] = torch.tensor([1.0, 0.5, 0.1])

  def batch() -> TensorDict:
    return TensorDict(
      {"actor": actor.clone(), "critic": critic.clone()}, batch_size=(3,)
    )

  plain, _ = augment_symmetries(None, batch(), None)
  loop, _ = augment_symmetries_kick_loop(None, batch(), None)
  assert plain is not None and loop is not None
  # The walk mirror negates slot 74 (a yaw rate there); the kick loop keeps it.
  assert torch.equal(plain["actor"][3:, 74], -actor[:, 74])
  assert torch.equal(loop["actor"][3:, 74], actor[:, 74])
  assert torch.equal(loop["critic"][3:, 74], critic[:, 74])
  # Everything else matches the walk mirror.
  others = [i for i in range(83) if i != 74]
  assert torch.equal(loop["actor"][:, others], plain["actor"][:, others])


def test_kick_quality_pays_planted_swings_not_running_pushes() -> None:
  # (body speed, foot speed relative to body) -> quality
  planted_swing = kick_quality_score(torch.tensor([0.05]), torch.tensor([2.6]))
  running_push = kick_quality_score(torch.tensor([0.92]), torch.tensor([1.0]))
  slow_tap = kick_quality_score(torch.tensor([0.05]), torch.tensor([1.0]))
  assert planted_swing.item() > 0.95
  assert running_push.item() < 0.01
  assert slow_tap.item() == 0.0


def test_head_tracker_points_at_the_ball_and_is_rate_limited() -> None:
  from mjlab.tasks.velocity.mdp.kick_loop import (
    HEAD_MAX_STEP,
    HEAD_PITCH_LIMITS,
    head_step,
    head_track_angles,
  )

  ang = head_track_angles(torch.tensor([[2.0, 0.0], [1.0, 1.0], [0.3, 0.0]]))
  assert abs(ang[0, 0].item()) < 1e-6
  # 2 m ahead: ~0.33 rad to the ball, aimed 0.18 below it.
  assert 0.45 < ang[0, 1].item() < 0.58
  assert math.isclose(ang[1, 0].item(), math.atan2(1.0, 1.0 - 0.0056), rel_tol=1e-4)
  assert math.isclose(ang[2, 1].item(), HEAD_PITCH_LIMITS[1], rel_tol=1e-6)
  step = head_step(torch.zeros(1, 2), torch.tensor([[1.0, -1.0]]))
  assert torch.allclose(step, torch.tensor([[HEAD_MAX_STEP, -HEAD_MAX_STEP]]))


def test_stage3_v21_head_fov_and_posture_wiring() -> None:
  cfg = load_env_cfg(TASK)
  assert cfg.commands is not None
  twist = cfg.commands["twist"]
  assert math.isclose(twist.fov_half_angle, 0.6056, abs_tol=1e-3)
  assert math.isclose(twist.fov_vertical_half_angle, 0.3665, abs_tol=1e-3)
  assert type(cfg.actions["joint_pos"]).__name__ == "HeadTrackedJointPositionActionCfg"
  assert cfg.rewards["knee_gap"].weight < 0.0
  assert cfg.rewards["arm_pose"].weight < 0.0
  assert cfg.rewards["foot_flat"].weight < 0.0
  assert cfg.rewards["foot_flat"].params["axis"] == 1
  for name in ("walk_base_height", "walk_stance_width", "knee_valgus"):
    assert cfg.rewards[name].weight < 0.0, name
  # Ball memory as on the robot: no odometry.
  assert twist.memory_odometry is False


def test_head_looks_down_when_a_near_ball_is_lost() -> None:
  from mjlab.tasks.velocity.mdp.kick_loop import HEAD_PITCH_LIMITS, head_goal

  ball = torch.tensor([[1.3, 0.1], [1.3, 0.1], [3.0, 0.0], [3.0, 0.0]])
  lost = torch.tensor([0.0, 0.3, 0.3, 1.0])
  g = head_goal(ball, lost)
  assert g[0, 1] < HEAD_PITCH_LIMITS[1]  # seen: track
  assert math.isclose(g[1, 1].item(), HEAD_PITCH_LIMITS[1], rel_tol=1e-6)
  assert g[2, 1] < 0.6  # far, briefly lost: keep tracking the estimate
  assert g[3, 1] < HEAD_PITCH_LIMITS[1]  # far, lost long: full sweep


def test_long_kicks_reward_speed_and_swing() -> None:
  from types import SimpleNamespace

  from mjlab.tasks.velocity.mdp import kick_loop as kl

  speeds = torch.tensor([3.3, 7.5, 9.5, 3.3])
  long = torch.tensor([True, True, True, False])
  cmd = SimpleNamespace(
    kick_event=torch.ones(4, dtype=torch.bool),
    kick_loft=1.0,
    kick_speed=speeds,
    kick_long=long,
    kick_speed_req=torch.full((4,), 3.4),
    kick_cos=torch.ones(4),
    kick_quality=torch.ones(4),
    kick_near_time=torch.zeros(4),
    kick_foot_rel=torch.tensor([3.0, 4.0, 6.0, 4.0]),
    long_band_lo=3.5,
    long_band_width=1.0,
  )
  orig = kl._kick_command
  kl._kick_command = lambda env: cmd
  try:
    vel = kl.kick_vel(None)
    acc = kl.kick_vel_accurate(None)
    power = kl.long_kick_power(None)
  finally:
    kl._kick_command = orig
  # Long kicks: kick_vel pays ball speed up to 7.5 m/s.
  assert math.isclose(vel[0].item(), 3.3 / 7.5, rel_tol=1e-5)
  assert vel[1] == 1.0 and vel[2] == 1.0
  assert vel[3] == 1.0  # short / medium keep the 3 m/s reference
  # Long: at least the rolling speed pays fully, faster is never penalised.
  assert math.isclose(acc[0].item(), 3.3 / 3.4, rel_tol=1e-5)
  assert acc[1] == 1.0 and acc[2] == 1.0
  assert acc[3] > 0.9  # medium: matches the rolling speed
  # Swing ramp 2.5 → target 3.5 m/s, 1 above; medium kicks get no power reward.
  assert math.isclose(power[0].item(), 0.5, rel_tol=1e-5)  # 3.0 m/s
  assert power[1] == 1.0 and power[2] == 1.0  # 4.0, 6.0 m/s
  assert power[3] == 0.0


def test_v34_posture_bands_and_speed_caps() -> None:
  from types import SimpleNamespace

  from mjlab.tasks.velocity.mdp import kick_loop as kl

  walking = torch.ones(3)
  robot = SimpleNamespace(
    find_bodies=lambda names, preserve_order=True: ([0, 1], list(names)),
    data=SimpleNamespace(
      # Third robot stands 0.3 m higher (raised ground): only its pose matters.
      body_link_pos_w=torch.tensor(
        [
          [[0, 0, 0.04], [0, 0, 0.06]],
          [[0, 0, 0.04], [0, 0, 0.1]],
          [[0, 0, 0.34], [0, 0, 0.36]],
        ]
      ),
      root_link_pos_w=torch.tensor([[0, 0, 0.52], [0, 0, 0.535], [0, 0, 0.78]]),
      # gravity in the trunk frame: upright, 10° nose down, 6° nose up
      projected_gravity_b=torch.tensor(
        [
          [0.0, 0.0, -1.0],
          [math.sin(math.radians(10)), 0.0, -math.cos(math.radians(10))],
          [-math.sin(math.radians(6)), 0.0, -math.cos(math.radians(6))],
        ]
      ),
    ),
  )
  env = SimpleNamespace(scene={"robot": robot})
  orig = kl._walking
  kl._walking = lambda e: walking
  try:
    h = kl.walk_base_height(env)
    p = kl.trunk_pitch_band(env)
  finally:
    kl._walking = orig
  assert h[0] == 0.0  # on target
  assert math.isclose(h[1].item(), 0.0625, abs_tol=1e-4)  # 0.5 cm over the band
  assert math.isclose(h[2].item(), 2.25, abs_tol=1e-3)  # 3 cm over the band
  assert p[0] == 0.0
  assert math.isclose(p[1].item(), 20.25, rel_tol=1e-3)  # 9° beyond +1° (v53)
  assert math.isclose(p[2].item(), 0.25, rel_tol=1e-2)  # 1° beyond −5°

  cfg = load_env_cfg(TASK)
  assert cfg.commands is not None
  twist = cfg.commands["twist"]
  assert twist.speed_cap_final == ((0.3, 2.0), (0.2, 1.5), (0.4, 1.5))
  assert kl.BACKWARD_SPEED_MAX == 1.75
  assert twist.ball_distance_range == (1.0, 4.0)
  for name in (
    "trunk_pitch_band",
    "long_kick_power",
    "walk_base_height",
    "arm_abduction",
  ):
    assert name in cfg.rewards
  assert "ball_bounce" in cfg.events


def test_walk_speed_pays_low_caps_fully_and_high_caps_more() -> None:
  from types import SimpleNamespace

  from mjlab.tasks.velocity.mdp import kick_loop as kl

  caps = torch.tensor([0.4, 0.4, 2.0, 2.0])
  toward = torch.tensor([0.4, 0.2, 1.0, 2.0])
  cmd = SimpleNamespace(
    speed_limit=torch.stack((caps, caps, caps), dim=-1),
    ball_lost=torch.zeros(len(caps), dtype=torch.bool),
    cfg=SimpleNamespace(near_distance=1.5),
    time_since_kick=torch.full((4,), 10.0),
  )
  ball_b = torch.tensor([[3.0, 0.0]] * 4)
  robot = SimpleNamespace(
    data=SimpleNamespace(
      root_link_lin_vel_b=torch.stack((toward, torch.zeros(4), torch.zeros(4)), -1)
    )
  )
  env = SimpleNamespace(scene={"robot": robot})
  o1, o2 = kl._kick_command, kl._current
  kl._kick_command = lambda e: cmd
  kl._current = lambda e: (
    None,
    torch.full((4,), 3.0),
    None,
    None,
    None,
    None,
    None,
    ball_b,
  )
  try:
    w = kl.walk_speed(env)
  finally:
    kl._kick_command, kl._current = o1, o2
  assert torch.allclose(w, torch.tensor([1.0, 0.5, 1.0, 2.0]))


def test_walk_speed_track_peaks_at_the_cap() -> None:
  from types import SimpleNamespace

  from mjlab.tasks.velocity.mdp import kick_loop as kl

  caps = torch.tensor([2.0, 2.0, 0.45, 0.45, 2.0])
  toward = torch.tensor([2.0, 1.0, 0.45, 0.65, 2.0])
  dist = torch.tensor([4.0, 4.0, 4.0, 4.0, 1.0])
  cmd = SimpleNamespace(
    speed_limit=torch.stack((caps, caps, caps), dim=-1),
    ball_lost=torch.zeros(len(caps), dtype=torch.bool),
    time_since_kick=torch.full((5,), 10.0),
  )
  ball_b = torch.tensor([[3.0, 0.0]] * 5)
  robot = SimpleNamespace(
    data=SimpleNamespace(
      root_link_lin_vel_b=torch.stack((toward, torch.zeros(5), torch.zeros(5)), -1)
    )
  )
  env = SimpleNamespace(scene={"robot": robot})
  o1, o2 = kl._kick_command, kl._current
  kl._kick_command = lambda e: cmd
  kl._current = lambda e: (None, dist, None, None, None, None, None, ball_b)
  try:
    w = kl.walk_speed_track(env)
  finally:
    kl._kick_command, kl._current = o1, o2
  assert w[0] == 1.0 and w[2] == 1.0  # at the cap
  assert math.isclose(w[1].item(), 0.5, rel_tol=1e-5)  # half the cap
  assert math.isclose(w[3].item(), 1.0 - 0.2 / 0.45, rel_tol=1e-4)  # over the cap
  assert w[4] == 0.0  # ball close: off


def test_kick_direction_needs_power() -> None:
  from types import SimpleNamespace

  from mjlab.tasks.velocity.mdp import kick_loop as kl

  # Target needs 4.0 m/s: a 1.4 m/s tap earns half the aim reward of a kick at
  # 2.8 m/s (= 0.7 x 4.0) or faster.
  speeds = torch.tensor([1.4, 2.8, 6.0])
  cmd = SimpleNamespace(
    kick_event=torch.ones(3, dtype=torch.bool),
    kick_loft=1.0,
    kick_cos=torch.ones(3),
    kick_quality=torch.ones(3),
    kick_near_time=torch.zeros(3),
    kick_speed=speeds,
    kick_speed_req=torch.full((3,), 4.0),
    cfg=SimpleNamespace(aim_broad_share=0.0),
  )
  orig = kl._kick_command
  kl._kick_command = lambda e: cmd
  try:
    d = kl.kick_direction(None)
  finally:
    kl._kick_command = orig
  assert math.isclose(d[0].item(), 0.5, rel_tol=1e-5)
  assert d[1] == 1.0 and d[2] == 1.0


def test_long_kick_power_needs_transfer() -> None:
  from types import SimpleNamespace

  from mjlab.tasks.velocity.mdp import kick_loop as kl

  # Same 5 m/s swing: a clean strike (ball 6 m/s) pays in full, a glancing one
  # (ball 1.75 m/s = half of 0.7 x 5) half.
  cmd = SimpleNamespace(
    kick_event=torch.ones(2, dtype=torch.bool),
    kick_loft=1.0,
    kick_long=torch.ones(2, dtype=torch.bool),
    kick_speed=torch.tensor([6.0, 1.75]),
    kick_foot_rel=torch.tensor([5.0, 5.0]),
    kick_cos=torch.ones(2),
    kick_quality=torch.ones(2),
    long_band_lo=4.5,
  )
  orig = kl._kick_command
  kl._kick_command = lambda e: cmd
  try:
    p = kl.long_kick_power(None)
  finally:
    kl._kick_command = orig
  assert p[0] == 1.0
  assert math.isclose(p[1].item(), 0.5, rel_tol=1e-5)


def test_side_aware_angle_folds_90_degrees() -> None:
  a = torch.tensor([0.0, 0.3, -0.3, math.pi / 2, -math.pi / 2, math.pi / 4, math.pi])
  got = side_aware_angle(a)
  want = torch.tensor(
    [
      0.0,
      0.3,
      0.3,
      SIDE_KICK_COST,
      SIDE_KICK_COST,
      math.pi / 4,
      math.pi / 2 + SIDE_KICK_COST,
    ]
  )
  assert torch.allclose(got, want, atol=1e-6)
  # Behind the ball always at least as good as side-on.
  assert float(side_aware_angle(torch.tensor([0.0]))) < float(
    side_aware_angle(torch.tensor([math.pi / 2]))
  )


def test_stage3_side_kicks_wired() -> None:
  cfg = load_env_cfg("Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1")
  twist = cfg.commands["twist"]
  # Off from v53 (side kicks not learned by shaping); the fields stay wired.
  assert twist.side_drill_prob <= 0.3
  assert cfg.rewards["side_kick_bonus"].weight == (400.0 if twist.side_kicks else 0.0)
  lo, hi = twist.side_drill_angle
  assert math.radians(50) < lo < hi < math.radians(120)


def test_short_kick_vel_full_at_needed_speed() -> None:
  from types import SimpleNamespace

  from mjlab.tasks.velocity.mdp import kick_loop as kl

  # Short target needing 2.2 m/s: 2.2 and 4.4 m/s both pay 1 (no extra for a
  # blast); a long kick still pays speed / 7.5.
  cmd = SimpleNamespace(
    kick_event=torch.ones(3, dtype=torch.bool),
    kick_loft=1.0,
    kick_cos=torch.ones(3),
    kick_quality=torch.ones(3),
    kick_near_time=torch.zeros(3),
    kick_speed=torch.tensor([2.2, 4.4, 3.75]),
    kick_speed_req=torch.tensor([2.2, 2.2, 5.0]),
    kick_long=torch.tensor([False, False, True]),
    cfg=SimpleNamespace(aim_broad_share=0.0),
  )
  orig = kl._kick_command
  kl._kick_command = lambda e: cmd
  try:
    v = kl.kick_vel(None)
  finally:
    kl._kick_command = orig
  assert math.isclose(v[0].item(), 1.0, rel_tol=1e-5)
  assert math.isclose(v[1].item(), 1.0, rel_tol=1e-5)
  assert math.isclose(v[2].item(), 0.5, rel_tol=1e-5)


def test_kick_rest_accuracy_wired() -> None:
  from types import SimpleNamespace

  from mjlab.tasks.velocity.mdp import kick_loop as kl

  cmd = SimpleNamespace(
    rest_event=torch.tensor([True, True, False]),
    rest_score=torch.tensor([1.0, 0.2, 1.0]),
    last_kick_quality=torch.tensor([0.5, 1.0, 1.0]),
  )
  orig = kl._kick_command
  kl._kick_command = lambda e: cmd
  try:
    r = kl.kick_rest_accuracy(None)
  finally:
    kl._kick_command = orig
  assert torch.allclose(r, torch.tensor([0.5, 0.2, 0.0]))
  cfg = load_env_cfg("Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1")
  assert cfg.rewards["kick_rest_accuracy"].weight > 0.0


def test_short_speed_match_is_linear() -> None:
  from types import SimpleNamespace

  from mjlab.tasks.velocity.mdp import kick_loop as kl

  cmd = SimpleNamespace(
    kick_event=torch.ones(3, dtype=torch.bool),
    kick_loft=1.0,
    kick_cos=torch.ones(3),
    kick_quality=torch.ones(3),
    kick_speed=torch.tensor([2.0, 3.6, 1.0]),
    kick_speed_req=torch.tensor([2.0, 2.0, 2.0]),
    kick_long=torch.zeros(3, dtype=torch.bool),
    cfg=SimpleNamespace(aim_broad_share=0.0),
  )
  orig = kl._kick_command
  kl._kick_command = lambda e: cmd
  try:
    m = kl.kick_vel_accurate(None)
  finally:
    kl._kick_command = orig
  assert torch.allclose(m, torch.tensor([1.0, 0.2, 0.5]), atol=1e-5)


def test_long_kick_underpower() -> None:
  from types import SimpleNamespace

  from mjlab.tasks.velocity.mdp import kick_loop as kl

  cmd = SimpleNamespace(
    kick_event=torch.ones(4, dtype=torch.bool),
    kick_loft=1.0,
    kick_long=torch.tensor([True, True, True, False]),
    kick_speed=torch.tensor([5.0, 4.0, 2.0, 0.5]),
    kick_speed_req=torch.full((4,), 5.0),
  )
  orig = kl._kick_command
  kl._kick_command = lambda e: cmd
  try:
    u = kl.long_kick_underpower(None)
  finally:
    kl._kick_command = orig
  assert torch.allclose(u, torch.tensor([0.0, 0.0, 0.5, 0.0]), atol=1e-5)


def test_loft_factor() -> None:
  from mjlab.tasks.velocity.mdp import kick_loop as kl

  lo, hi = kl.LOFT_FREE_DEG, kl.LOFT_ZERO_DEG
  a = torch.deg2rad(torch.tensor([0.0, lo, (lo + hi) / 2, hi, hi + 20.0, -10.0]))
  f = kl.loft_factor(a)
  assert torch.allclose(f, torch.tensor([1.0, 1.0, 0.5, 0.0, 0.0, 1.0]), atol=1e-5)


def test_stage3_search_wired() -> None:
  cfg = load_env_cfg("Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1")
  twist = cfg.commands["twist"]
  assert twist.memory_invalidate
  assert twist.memory_lost_in_view_s <= 1.0
  assert 1.0 <= twist.memory_lost_timeout_s <= 2.0
  assert "ball_relocate_unseen" in cfg.events
  assert cfg.rewards["search_turn"].weight > 0.0
  assert cfg.rewards["search_backward"].weight < 0.0


def test_search_turn_is_signed() -> None:
  from types import SimpleNamespace

  from mjlab.tasks.velocity.mdp import kick_loop as kl

  wz = torch.tensor([1.0, -1.0, 0.5, 2.0])
  robot = SimpleNamespace(
    data=SimpleNamespace(root_link_ang_vel_b=torch.stack((0 * wz, 0 * wz, wz), -1))
  )
  cmd = SimpleNamespace(
    ball_lost=torch.tensor([True, True, True, False]),
    lost_dir=torch.ones(4),
    speed_limit=torch.ones(4, 3),
  )
  env = SimpleNamespace(scene={"robot": robot}, extras={"log": {}})
  orig = kl._kick_command
  kl._kick_command = lambda e: cmd
  try:
    r = kl.search_turn(env)
  finally:
    kl._kick_command = orig
  assert torch.allclose(r, torch.tensor([1.0, -1.0, 0.5, 0.0]))


def test_momentum_kick_constants() -> None:
  from mjlab.tasks.velocity.mdp import kick_loop as kl

  # K2: walking into the ball at B-Human's ~0.8 m/s must not be "off-axis".
  assert kl.MOMENTUM_KICKS and kl.MOMENTUM_KICK_MAX_SPEED >= 0.8
  q = kl.kick_quality_score(torch.tensor([0.0, 0.4]), torch.tensor([2.5, 2.5]))
  assert q[0] > 0.99 and q[1] < 0.5


def test_reward_grammar_matches_hand_written_terms() -> None:
  """Grammar re-expressions of existing terms give identical values."""
  from types import SimpleNamespace

  from mjlab.tasks.velocity.mdp import kick_loop as kl
  from mjlab.tasks.velocity.mdp import reward_grammar as rg

  n = 6
  g = torch.Generator().manual_seed(0)
  cmd = SimpleNamespace(
    kick_event=torch.tensor([1, 1, 1, 0, 1, 1], dtype=torch.bool),
    kick_long=torch.tensor([1, 1, 0, 1, 1, 0], dtype=torch.bool),
    kick_speed=torch.rand(n, generator=g) * 8.0,
    kick_speed_req=torch.rand(n, generator=g) * 6.0,
    rest_event=torch.tensor([1, 0, 1, 1, 0, 1], dtype=torch.bool),
    rest_score=torch.rand(n, generator=g),
    last_kick_quality=torch.rand(n, generator=g),
  )
  orig = kl._kick_command
  kl._kick_command = lambda e: cmd
  try:
    under = rg.make_expr_term(
      {
        "mul": [
          {"sig": "kick_event"},
          {"sig": "kick_long"},
          {
            "clip": [
              {
                "add": [
                  1.0,
                  {
                    "neg": {
                      "div": [
                        {"sig": "kick_speed"},
                        {"mul": [0.8, {"sig": "kick_speed_needed"}]},
                      ]
                    }
                  },
                ]
              },
              0.0,
              1.0,
            ]
          },
        ]
      }  # fmt: skip
    )
    env = SimpleNamespace(num_envs=n, device="cpu")
    assert torch.allclose(under(env), kl.long_kick_underpower(env), atol=1e-6)
    rest = (
      rg.make_expr_term(
        {
          "mul": [
            {"sig": "rest_event"},
            {"sig": "rest_score"},
            {"sig": "kick_quality_last"},
          ]
        }
      )
      if "kick_quality_last" in rg.SIGNALS
      else None
    )
    assert rest is None or torch.allclose(
      rest(env), kl.kick_rest_accuracy(env), atol=1e-6
    )
  finally:
    kl._kick_command = orig


def test_reward_program_wiring(tmp_path) -> None:
  import json
  import os

  prog = [
    {"name": "long_kick_power", "weight": 2500.0},
    {"name": "standing_pose_l1", "remove": True},
    {
      "name": "lost_spin",
      "expr": {"mul": [{"sig": "ball_lost"}, {"sig": "wz"}]},
      "weight": 2.0,
    },
  ]
  p = tmp_path / "prog.json"
  p.write_text(json.dumps(prog))
  from mjlab.tasks.velocity.config.k1_amp.env_cfgs import booster_k1_kick_stage3_env_cfg

  # Registered cfgs are built at import; training processes get the variable
  # before import, so build directly here.
  os.environ["KICK_REWARD_PROGRAM"] = str(p)
  try:
    cfg = booster_k1_kick_stage3_env_cfg()
  finally:
    del os.environ["KICK_REWARD_PROGRAM"]
  assert cfg.rewards["long_kick_power"].weight == 2500.0
  assert "standing_pose_l1" not in cfg.rewards
  assert cfg.rewards["lost_spin"].weight == 2.0


def test_goal_mouth_pays_inside_the_posts_and_ramps_outside() -> None:
  from types import SimpleNamespace

  from mjlab.tasks.velocity.mdp import kick_loop as kl

  # Ball at the origin, target 8 m ahead. A centred shot is a goal; 2 m of
  # lateral miss is past the post and part-way down the ramp; heading away pays 0.
  def cmd(vel):
    ball = SimpleNamespace(
      data=SimpleNamespace(
        root_link_pos_w=torch.zeros(1, 3),
        root_link_lin_vel_w=torch.tensor([vel]),
      )
    )
    return SimpleNamespace(
      ball=ball,
      target_w=torch.tensor([[8.0, 0.0]]),
      kick_event=torch.ones(1, dtype=torch.bool),
      kick_long=torch.ones(1, dtype=torch.bool),
      kick_quality=torch.ones(1),
      kick_speed=torch.tensor([8.0]),
      kick_near_time=torch.zeros(1),
    )

  orig = kl._kick_command
  try:
    kl._kick_command = lambda e: cmd([2.0, 0.0, 0.0])
    on_goal = kl.goal_mouth(None)
    powered = kl.long_kick_speed_in_mouth(None)
    # Velocity (2, 0.5): |v x d| / |v| = |2*0 - 0.5*8| / sqrt(4.25) = 1.940 m.
    kl._kick_command = lambda e: cmd([2.0, 0.5, 0.0])
    wide = kl.goal_mouth(None)
    kl._kick_command = lambda e: cmd([-1.0, 0.0, 0.0])
    away = kl.goal_mouth(None)
  finally:
    kl._kick_command = orig
  assert math.isclose(on_goal.item(), 1.0, rel_tol=1e-5)
  assert math.isclose(powered.item(), 1.0, rel_tol=1e-5)
  lateral = 4.0 / math.sqrt(4.25)
  expected = 1.0 - (lateral - 1.25) / 1.5
  assert math.isclose(wide.item(), expected, rel_tol=1e-4)
  assert away.item() == 0.0

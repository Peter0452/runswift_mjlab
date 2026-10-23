"""Unit tests for spawn-side behind-ball waypoint offset."""

from types import SimpleNamespace

import torch

from mjlab.tasks.kick.mdp.geometry import (
  ensure_approach_waypoint_latch,
  expected_ballistic_speed,
  nearest_foot_kick_side,
  offset_behind_ball_waypoint_xy,
  update_plant_arrival_latch,
)
from mjlab.tasks.kick.mdp.rewards import plant_latch_arrival_bonus


def test_lateral_offset_puts_swing_foot_on_kick_line():
  ball = torch.tensor([[0.0, 0.0]])
  goal_dir = torch.tensor([[1.0, 0.0]])  # goal at +x
  # Spawn left of axis → side +1 → yellow left (y>0) → right-foot kick.
  left = offset_behind_ball_waypoint_xy(
    ball, goal_dir, 0.30, torch.tensor([1.0]), torch.tensor([0.10])
  )
  assert torch.allclose(left, torch.tensor([[-0.30, 0.10]]), atol=1e-6)
  right = offset_behind_ball_waypoint_xy(
    ball, goal_dir, 0.30, torch.tensor([-1.0]), torch.tensor([0.10])
  )
  assert torch.allclose(right, torch.tensor([[-0.30, -0.10]]), atol=1e-6)


def test_zero_side_stays_on_axis():
  ball = torch.tensor([[1.0, 2.0]])
  goal_dir = torch.tensor([[0.0, 1.0]])
  wp = offset_behind_ball_waypoint_xy(
    ball, goal_dir, 0.30, torch.tensor([0.0]), torch.tensor([0.12])
  )
  assert torch.allclose(wp, torch.tensor([[1.0, 1.70]]), atol=1e-6)


def test_zero_standoff_is_ball_plus_lateral():
  ball = torch.tensor([[0.0, 0.0]])
  goal_dir = torch.tensor([[1.0, 0.0]])
  wp = offset_behind_ball_waypoint_xy(
    ball, goal_dir, 0.0, torch.tensor([1.0]), torch.tensor([0.10])
  )
  assert torch.allclose(wp, torch.tensor([[0.0, 0.10]]), atol=1e-6)


def test_offset_range_keeps_ball_outside_keepout():
  # hypot(0.15, 0.12) > 0.09 keep-out.
  ball = torch.zeros(1, 2)
  goal_dir = torch.tensor([[1.0, 0.0]])
  for lat in (0.08, 0.10, 0.12):
    wp = offset_behind_ball_waypoint_xy(
      ball, goal_dir, 0.15, torch.tensor([1.0]), torch.tensor([lat])
    )
    dist = torch.linalg.norm(wp - ball, dim=-1).item()
    assert dist > 0.09
    assert abs(dist - (0.15**2 + lat**2) ** 0.5) < 1e-6


def test_nearest_foot_kick_side_picks_closer_leg():
  ball = torch.tensor([[0.0, 0.0], [0.0, 0.0]])
  goal_dir = torch.tensor([[1.0, 0.0], [1.0, 0.0]])
  # Facing the ball from behind, left vs right of the kick axis.
  robot = torch.tensor([[-0.60, 0.15], [-0.60, -0.15]])
  side = nearest_foot_kick_side(robot, ball, goal_dir)
  assert torch.equal(side, torch.tensor([1.0, -1.0]))


def test_plant_latch_requires_continuous_ready_hold():
  env = SimpleNamespace(num_envs=1, device="cpu", step_dt=0.025)
  distance = torch.tensor([0.12])
  facing = torch.tensor([1.0])

  for _ in range(3):
    assert not update_plant_arrival_latch(
      env, distance, facing, 0.12, facing_min=0.94, hold_time_s=0.10
    ).item()
  assert update_plant_arrival_latch(
    env, distance, facing, 0.12, facing_min=0.94, hold_time_s=0.10
  ).item()


def test_plant_latch_blocked_without_support_ready():
  env = SimpleNamespace(num_envs=1, device="cpu", step_dt=0.025)
  distance = torch.tensor([0.12])
  facing = torch.tensor([1.0])
  not_ready = torch.tensor([False])
  for _ in range(8):
    assert not update_plant_arrival_latch(
      env,
      distance,
      facing,
      0.12,
      facing_min=0.94,
      hold_time_s=0.10,
      support_ready=not_ready,
    ).item()
  ready = torch.tensor([True])
  for _ in range(3):
    assert not update_plant_arrival_latch(
      env,
      distance,
      facing,
      0.12,
      facing_min=0.94,
      hold_time_s=0.10,
      support_ready=ready,
    ).item()
  assert update_plant_arrival_latch(
    env,
    distance,
    facing,
    0.12,
    facing_min=0.94,
    hold_time_s=0.10,
    support_ready=ready,
  ).item()


def test_plant_latch_blocked_without_swing_ready():
  env = SimpleNamespace(num_envs=1, device="cpu", step_dt=0.025)
  distance = torch.tensor([0.12])
  facing = torch.tensor([1.0])
  support = torch.tensor([True])
  swing_far = torch.tensor([False])
  for _ in range(8):
    assert not update_plant_arrival_latch(
      env,
      distance,
      facing,
      0.12,
      facing_min=0.94,
      hold_time_s=0.10,
      support_ready=support,
      swing_ready=swing_far,
    ).item()


def test_plant_latch_bonus_fires_once_on_rising_edge():
  env = SimpleNamespace(num_envs=2, device="cpu", extras={"log": {}})
  latch = ensure_approach_waypoint_latch(env)
  assert torch.equal(plant_latch_arrival_bonus(env), torch.zeros(2))
  latch.at_plant[:] = torch.tensor([True, False])
  assert torch.equal(plant_latch_arrival_bonus(env), torch.tensor([1.0, 0.0]))
  assert torch.equal(plant_latch_arrival_bonus(env), torch.zeros(2))
  latch.at_plant[1] = True
  assert torch.equal(plant_latch_arrival_bonus(env), torch.tensor([0.0, 1.0]))


def test_expected_ballistic_speed_matches_range_equation():
  speed = expected_ballistic_speed(torch.tensor([10.0]))
  assert torch.allclose(speed, torch.tensor([(9.81 * 10.0) ** 0.5]))

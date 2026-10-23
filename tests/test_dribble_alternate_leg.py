"""Alternating-leg forward dribble: tap classification and reward gating."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import torch

from k1.tasks.dribble.mdp.dribble import classify_alternate_tap
from k1.tasks.dribble.mdp.dribble_rewards import alternate_leg_dribble
from k1.tasks.velocity.config.k1_amp.env_cfgs import booster_k1_dribble_env_cfg
from mjlab.utils.lab_api.math import quat_from_euler_xyz


def _bool2(left: bool, right: bool) -> torch.Tensor:
  return torch.tensor([[left, right]], dtype=torch.bool)


def test_first_tap_is_neither_alt_nor_same() -> None:
  alt, same, side, t = classify_alternate_tap(
    _bool2(True, False),
    _bool2(False, False),
    torch.zeros(1),
    torch.full((1,), 1.0),
    dt=0.02,
  )
  assert not bool(alt.item())
  assert not bool(same.item())
  assert side.item() == 1.0
  assert t.item() == 0.0


def test_left_then_right_is_alternate() -> None:
  alt, same, side, t = classify_alternate_tap(
    _bool2(False, True),
    _bool2(False, False),
    torch.ones(1),
    torch.full((1,), 0.20),
    dt=0.02,
  )
  assert bool(alt.item())
  assert not bool(same.item())
  assert side.item() == -1.0
  assert t.item() == 0.0


def test_left_then_left_is_same_foot() -> None:
  alt, same, side, _ = classify_alternate_tap(
    _bool2(True, False),
    _bool2(False, False),
    torch.ones(1),
    torch.full((1,), 0.20),
    dt=0.02,
  )
  assert not bool(alt.item())
  assert bool(same.item())
  assert side.item() == 1.0


def test_chatter_inside_min_interval_is_ignored() -> None:
  alt, same, side, t = classify_alternate_tap(
    _bool2(False, True),
    _bool2(False, False),
    torch.ones(1),
    torch.full((1,), 0.04),
    dt=0.02,
    min_interval_s=0.12,
  )
  assert not bool(alt.item())
  assert not bool(same.item())
  assert side.item() == 1.0
  assert t.item() == pytest.approx(0.06)


def test_two_foot_trap_is_not_a_tap() -> None:
  alt, same, side, t = classify_alternate_tap(
    _bool2(True, True),
    _bool2(True, False),
    torch.ones(1),
    torch.full((1,), 0.20),
    dt=0.02,
  )
  assert not bool(alt.item())
  assert not bool(same.item())
  assert side.item() == 1.0
  assert t.item() > 0.0


def test_sustained_contact_is_not_a_new_tap() -> None:
  alt, same, side, t = classify_alternate_tap(
    _bool2(True, False),
    _bool2(True, False),
    torch.ones(1),
    torch.zeros(1),
    dt=0.02,
  )
  assert not bool(alt.item())
  assert not bool(same.item())
  assert side.item() == 1.0
  assert t.item() == pytest.approx(0.02)


def _quat_yaw(yaw: float) -> torch.Tensor:
  return quat_from_euler_xyz(torch.zeros(1), torch.zeros(1), torch.tensor([yaw]))


def _forward_env(
  *,
  alt: bool = False,
  tap_side: float = 1.0,
  time_since_tap: float = 0.25,
  cmd_speed: float = 0.6,
  ball_lost: bool = False,
  win_touched: bool = True,
  robot_xy: tuple[float, float] = (0.0, 0.0),
  ball_xy: tuple[float, float] = (0.35, 0.0),
  ball_vel: tuple[float, float] = (0.5, 0.0),
  cmd_dir: tuple[float, float] = (1.0, 0.0),
  yaw: float = 0.0,
  left_ground: bool = True,
  right_ground: bool = False,
  left_foot_vel: tuple[float, float] = (0.0, 0.0),
  right_foot_vel: tuple[float, float] = (0.7, 0.0),
) -> tuple[MagicMock, MagicMock]:
  env = MagicMock()
  env.extras = {"log": {}}
  cmd = MagicMock()
  cmd.ball_cmd_speed = torch.tensor([cmd_speed])
  cmd.ball_cmd_dir_w = torch.tensor([list(cmd_dir)])
  cmd.ball_lost = torch.tensor([ball_lost])
  cmd.win_touched = torch.tensor([win_touched])
  cmd.alt_touch_event = torch.tensor([alt])
  cmd.tap_side = torch.tensor([tap_side])
  cmd.time_since_tap = torch.tensor([time_since_tap])
  cmd.gait_contact_prev = torch.tensor([[left_ground, right_ground]])
  cmd._gait_feet_ids = [0, 1]

  robot = MagicMock()
  robot.data.root_link_pos_w = torch.tensor([[robot_xy[0], robot_xy[1], 0.5]])
  robot.data.root_link_quat_w = _quat_yaw(yaw)
  robot.data.body_link_lin_vel_w = torch.tensor(
    [[
      [left_foot_vel[0], left_foot_vel[1], 0.0],
      [right_foot_vel[0], right_foot_vel[1], 0.0],
    ]]
  )
  ball = MagicMock()
  ball.data.root_link_pos_w = torch.tensor([[ball_xy[0], ball_xy[1], 0.1]])
  ball.data.root_link_lin_vel_w = torch.tensor([[ball_vel[0], ball_vel[1], 0.0]])
  env.scene = {"robot": robot, "ball": ball}
  env.command_manager.get_term.return_value = cmd
  return env, cmd


def _reward(env: MagicMock, cmd: MagicMock) -> torch.Tensor:
  with patch(
    "k1.tasks.dribble.mdp.dribble_rewards._dribble", return_value=cmd
  ):
    return alternate_leg_dribble(env)


def test_alternate_event_pays_when_dribbling_forwards() -> None:
  env, cmd = _forward_env(alt=True, time_since_tap=0.0)
  r = _reward(env, cmd)
  assert r.item() > 0.5


def test_alternate_event_zero_before_first_touch() -> None:
  env, cmd = _forward_env(alt=True, win_touched=False)
  r = _reward(env, cmd)
  assert r.item() == 0.0


def test_alternate_event_zero_when_sideways() -> None:
  env, cmd = _forward_env(
    alt=True,
    robot_xy=(0.35, 0.4),
    ball_xy=(0.35, 0.0),
  )
  r = _reward(env, cmd)
  assert r.item() == 0.0


def test_other_leg_swing_pays_between_taps() -> None:
  env, cmd = _forward_env(alt=False, tap_side=1.0, time_since_tap=0.25)
  r = _reward(env, cmd)
  assert r.item() > 0.1


def test_other_leg_swing_zero_outside_window() -> None:
  env, cmd = _forward_env(alt=False, tap_side=1.0, time_since_tap=0.80)
  r = _reward(env, cmd)
  assert r.item() == 0.0


def test_dribble_env_registers_alternate_leg_term() -> None:
  cfg = booster_k1_dribble_env_cfg()
  term = cfg.rewards["alternate_leg_dribble"]
  assert term.func is alternate_leg_dribble
  assert term.weight == 2.0

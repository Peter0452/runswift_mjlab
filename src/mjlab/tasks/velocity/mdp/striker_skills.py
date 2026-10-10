"""Two-level striker: a controller picks a skill every few steps, frozen skills
turn it into joint targets.

The controller acts every ``DECISION_STEPS`` env steps (5 Hz at 50 Hz) with
four numbers in [-1, 1]:

- ``a[0]``: kick (> 0) or walk.
- ``a[1:3]``: direction (cos, sin), robot frame. The kick skill aims the ball
  along it; the walk skill heads along it.
- ``a[3]``: kick range (short / medium / long in thirds) or walk speed.

Skills are the stage-3 kick loop (83 inputs, or 86 with the opponent
detection) and the AMP walk (75 inputs: the same 72 body inputs and a
velocity command). Both drive the same 22 joints, so switching only changes
which network runs. The controller sees the kick loop's 86 inputs (ball,
target goal direction / range, opponent) and the skill state.
"""

from __future__ import annotations

from collections.abc import Callable

import torch

Policy = Callable[[torch.Tensor], torch.Tensor]

# Actor layout of the kick loop (see docs/K1_KICK_LOOP_POLICY_IO.md).
BODY_DIM = 72
KICK_DIR_SLOTS = slice(78, 80)
KICK_RANGE_SLOTS = slice(80, 83)

CONTROLLER_ACTION_DIM = 4
SKILL_STATE_DIM = 2
DECISION_STEPS = 10
"""Env steps per controller decision (5 Hz at the 50 Hz env step)."""
WALK_SPEED_MAX = 1.2
"""Walk speed at ``a[3] = 1`` (m/s)."""
WALK_LATERAL_SHARE = 0.35
WALK_TURN_GAIN = 2.0
WALK_TURN_MAX = 1.2
SWITCH_HOLD_STEPS = 50
"""Steps since the last switch at which the skill-state input saturates."""


def decode(action: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
  """(kick mask, direction angle in the robot frame, level in [-1, 1])."""
  a = action.clamp(-1.0, 1.0)
  kick = a[:, 0] > 0.0
  theta = torch.atan2(a[:, 2], a[:, 1])
  return kick, theta, a[:, 3]


def range_from_level(level: torch.Tensor) -> torch.Tensor:
  """Kick range one-hot (short, medium, long) from thirds of [-1, 1]."""
  idx = torch.bucketize(level, level.new_tensor([-1.0 / 3.0, 1.0 / 3.0]))
  return torch.nn.functional.one_hot(idx, 3).to(level.dtype)


def walk_command(theta: torch.Tensor, level: torch.Tensor) -> torch.Tensor:
  """Velocity command (vx, vy, wz) that walks along ``theta`` and turns to it."""
  speed = WALK_SPEED_MAX * 0.5 * (level + 1.0)
  facing = (theta.abs() < 0.8).to(theta.dtype)
  speed = speed * (0.35 + 0.65 * facing)
  vx = speed * theta.cos()
  vy = WALK_LATERAL_SHARE * speed * theta.sin()
  wz = (WALK_TURN_GAIN * theta).clamp(-WALK_TURN_MAX, WALK_TURN_MAX)
  return torch.stack((vx, vy, wz), dim=-1)


def kick_inputs(actor_obs: torch.Tensor, theta: torch.Tensor, level: torch.Tensor):
  """The kick loop's inputs with the controller's aim and range."""
  obs = actor_obs.clone()
  obs[:, KICK_DIR_SLOTS] = torch.stack((theta.cos(), theta.sin()), dim=-1)
  obs[:, KICK_RANGE_SLOTS] = range_from_level(level)
  return obs


def walk_inputs(actor_obs: torch.Tensor, theta: torch.Tensor, level: torch.Tensor):
  """The AMP walk's 75 inputs: body state and the controller's command."""
  return torch.cat((actor_obs[:, :BODY_DIM], walk_command(theta, level)), dim=-1)


def skill_state(kick: torch.Tensor, since_switch: torch.Tensor) -> torch.Tensor:
  """Controller input: current skill and how long it has run (saturating)."""
  held = (since_switch.float() / SWITCH_HOLD_STEPS).clamp(max=1.0)
  return torch.stack((kick.float(), held), dim=-1)


def controller_inputs(
  actor_obs: torch.Tensor, kick: torch.Tensor, since_switch: torch.Tensor
) -> torch.Tensor:
  return torch.cat((actor_obs, skill_state(kick, since_switch)), dim=-1)


def run_skills(
  actor_obs: torch.Tensor,
  kick: torch.Tensor,
  theta: torch.Tensor,
  level: torch.Tensor,
  kick_skill: Policy,
  walk_skill: Policy,
) -> torch.Tensor:
  """Joint actions (22) from the chosen skill per env."""
  out = torch.zeros(actor_obs.shape[0], 22, device=actor_obs.device)
  if bool(kick.any()):
    ids = kick.nonzero(as_tuple=False).squeeze(-1)
    out[ids] = kick_skill(kick_inputs(actor_obs[ids], theta[ids], level[ids]))
  walk = ~kick
  if bool(walk.any()):
    ids = walk.nonzero(as_tuple=False).squeeze(-1)
    out[ids] = walk_skill(walk_inputs(actor_obs[ids], theta[ids], level[ids]))
  return out


def stand_action(n: int, device) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
  """A walk decision with zero speed facing forward (after a reset)."""
  kick = torch.zeros(n, dtype=torch.bool, device=device)
  theta = torch.zeros(n, device=device)
  level = torch.full((n,), -1.0, device=device)
  return kick, theta, level

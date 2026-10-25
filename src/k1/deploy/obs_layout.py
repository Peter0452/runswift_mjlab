"""Actor input layouts of the deployed policy families (knowledge/deployment.md §3).

A layout that the runner can run names the runner policy spec it delivers to
(``policy_id``, ``spec_version``: ``k1_policy_runner/docs/policies/<id>.md`` on
the runner's ``dev`` branch) and that spec's ``obs_layout`` string, which the
export writes into the ONNX metadata. ``tests/test_runner_spec.py`` checks
these against the runner's docs; a layout without a spec can't be delivered.

Each layout lists the actor observation terms in order with their sizes, what
they hold and where the runner gets them. ``tests/test_deploy_obs_layout.py``
checks these against the layouts the golden models were recorded with, and
``scripts/tools/golden.py check`` checks those against the live envs, so a
training change that moves a slot fails here before it reaches the robot.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Block:
  term: str  # actor observation term name in the env config
  size: int
  content: str
  runner: str  # where k1_policy_runner gets it


@dataclass(frozen=True)
class Layout:
  name: str
  task: str
  blocks: tuple[Block, ...]
  outputs: int = 22  # joint position targets, deployment.md §1 joint order
  # Runner policy spec this layout delivers to (None: no spec, not deliverable).
  policy_id: str | None = None
  spec_version: int | None = None
  spec_layout: str | None = None  # the spec's obs_layout string, verbatim

  @property
  def size(self) -> int:
    return sum(b.size for b in self.blocks)

  def terms(self) -> list[tuple[str, int]]:
    return [(b.term, b.size) for b in self.blocks]

  def slots(self, term: str) -> range:
    """Input indices of one term, e.g. ``KICK_LOOP_V1.slots("command")``."""
    start = 0
    for b in self.blocks:
      if b.term == term:
        return range(start, start + b.size)
      start += b.size
    raise KeyError(f"{self.name} has no term {term!r}")


_PROPRIO = (
  Block("base_ang_vel", 3, "gyro, trunk frame", "IMU"),
  Block("projected_gravity", 3, "gravity, trunk frame", "IMU"),
  Block("joint_pos", 22, "joint pos - default", "low_state"),
  Block("joint_vel", 22, "joint vel", "low_state"),
  Block("actions", 22, "previous raw action", "runner"),
)

WALK_AMP = Layout(
  name="walk_amp",
  task="Mjlab-Velocity-Rough-Amp-DA-Muon-Booster-K1",
  blocks=_PROPRIO
  + (Block("command", 3, "velocity command vx, vy, wz", "behaviour / joystick"),),
  policy_id="walk_amp_v1",
  spec_version=1,
  spec_layout="base_ang_vel[3],projected_gravity[3],joint_pos[22],joint_vel[22],"
  "actions[22],command[3]",
)

KICK_LOOP_V1 = Layout(
  name="kick_loop_v1",
  task="Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1",
  blocks=_PROPRIO
  + (
    Block(
      "command",
      3,
      "ball xy (feet-midpoint yaw frame), memory age exp(-t / 2 s)",
      "ball pipeline (IMU-yaw memory, lost rule, virtual ball)",
    ),
    Block("speed_limit", 3, "speed caps |vx|, |vy|, |wz|", "--kick-speed-limits"),
    Block("kick_direction", 2, "kick direction cos, sin", "--kick-dir-mode"),
    Block("kick_range", 3, "range one-hot < 4 / 4-8 / >= 8 m", "--kick-range"),
  ),
  policy_id="kick_loop_v1",
  spec_version=1,
  spec_layout="base_ang_vel[3],projected_gravity[3],joint_pos[22],joint_vel[22],"
  "actions[22],ball_xy[2],ball_age[1],speed_limit[3],kick_direction[2],kick_range[3]",
)

DRIBBLE_V1 = Layout(
  name="dribble_v1",
  task="Mjlab-Velocity-Dribble-Amp-DA-Muon-Booster-K1",
  blocks=_PROPRIO
  + (
    Block(
      "command",
      3,
      "ball xy, memory age exp(-t / 0.6 s) (0 while lost)",
      "ball pipeline",
    ),
    Block(
      "speed_limit",
      3,
      "caps vx 0.3-1.2, vy 0.2-1.0, wz 0.4-1.25",
      "--dribble-speed-limits",
    ),
    Block(
      "kick_direction",
      2,
      "commanded ball direction (kick direction in kick windows)",
      "dribble_policy.py",
    ),
    Block(
      "kick_range",
      3,
      "stop / kicked flag, commanded ball speed 0.2-1.5 m/s, kick flag (v22+)",
      "dribble_policy.py",
    ),
  ),
)

SELFPLAY_V1 = Layout(
  name="selfplay_v1",
  task="Mjlab-Velocity-Kick-SelfPlay-Amp-DA-Muon-Booster-K1",
  blocks=KICK_LOOP_V1.blocks
  + (
    Block(
      "opponent",
      3,
      "opponent xy, opponent seen",
      "vision robot detection (zeros when unseen)",
    ),
  ),
)

# The striker controller's env shares the self-play actor inputs; its runner
# adds the current skill and the time since the last switch (88 + GRU state).
STRIKER_CONTROLLER_V2 = Layout(
  name="striker_controller_v2",
  task="Mjlab-Velocity-Striker-Controller-Booster-K1",
  blocks=SELFPLAY_V1.blocks,
)

LAYOUTS = {
  lay.name: lay
  for lay in (WALK_AMP, KICK_LOOP_V1, DRIBBLE_V1, SELFPLAY_V1, STRIKER_CONTROLLER_V2)
}


def layout_for_task(task: str) -> Layout | None:
  return next((lay for lay in LAYOUTS.values() if lay.task == task), None)


def parse_spec_layout(text: str) -> list[tuple[str, int]]:
  """``"a[3],b[2]"`` -> ``[("a", 3), ("b", 2)]``."""
  out = []
  for part in text.split(","):
    name, size = part.strip().rstrip("]").split("[")
    out.append((name, int(size)))
  return out


def spec_metadata(layout: Layout) -> dict[str, str]:
  """The ONNX metadata keys the runner's RL development interface requires on
  top of pose, scales and gains: empty for a layout without a runner spec."""
  if layout.policy_id is None or layout.spec_layout is None:
    return {}
  return {
    "policy_id": layout.policy_id,
    "spec_version": str(layout.spec_version),
    "obs_dim": str(layout.size),
    "obs_layout": layout.spec_layout,
  }

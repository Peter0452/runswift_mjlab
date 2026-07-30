"""Kick trajectory visualiser for the Booster K1.

Usage:
    .venv/bin/mjpython src/mjlab/test.py [--kick NAME] [--cycle SECONDS]

Kick names: snap, high, side, back, chip  (default: snap)
"""

import argparse
import time
from pathlib import Path
from typing import NamedTuple

import mujoco
import mujoco.viewer
import numpy as np

# ---------------------------------------------------------------------------
# Trajectory library
# ---------------------------------------------------------------------------

# Each trajectory is a dict mapping joint name -> (P0, P1, P2, P3) scalars
# in radians.  Joints omitted from a trajectory stay at their resting pose.
#
# Joint limits (rad) for reference:
#   Hip_Pitch  : [-3.0,  2.21]   Hip_Roll : [-0.4, 1.57]
#   Hip_Yaw    : [-1.0,  1.0 ]   Knee_Pitch: [0.0, 2.23]
#   Ankle_Pitch: [-0.87, 0.345]  Ankle_Roll: [-0.345, 0.345]


class Trajectory(NamedTuple):
  joints: dict[str, tuple[float, float, float, float]]
  cycle: float  # seconds


TRAJECTORIES: dict[str, Trajectory] = {
  # ------------------------------------------------------------------
  # Front snap kick — hip cocks to -0.8, drives forward to 1.3 rad;
  # knee snaps to near-straight (0.05) at contact
  # ------------------------------------------------------------------
  "snap": Trajectory(
    cycle=1.5,
    joints={
      "Left_Hip_Pitch": (0.0, -0.8, 1.3, 0.0),
      "Left_Knee_Pitch": (0.0, 1.4, 0.05, 0.0),
      "Left_Ankle_Pitch": (0.0, -0.6, 0.3, 0.0),
    },
  ),
  # ------------------------------------------------------------------
  # High front kick — hip drives to 2.1 rad (near its 2.21 limit)
  # with leg mostly straight at apex, toe-up
  # ------------------------------------------------------------------
  "high": Trajectory(
    cycle=2.2,
    joints={
      "Left_Hip_Pitch": (0.0, -0.4, 2.1, 0.0),
      "Left_Knee_Pitch": (0.0, 1.6, 0.15, 0.0),
      "Left_Ankle_Pitch": (0.0, -0.3, 0.3, 0.0),
    },
  ),
  # ------------------------------------------------------------------
  # Side kick — hip pitch carries leg slightly forward before the
  # abduction arc so the foot clears the stance leg
  # ------------------------------------------------------------------
  "side": Trajectory(
    cycle=2.0,
    joints={
      "Left_Hip_Pitch": (0.0, 0.2, 0.4, 0.0),
      "Left_Hip_Roll": (0.0, 0.5, 1.1, 0.0),
      "Left_Hip_Yaw": (0.0, 0.3, 0.5, 0.0),
      "Left_Knee_Pitch": (0.0, 1.0, 0.15, 0.0),
      "Left_Ankle_Roll": (0.0, 0.1, 0.2, 0.0),
    },
  ),
  # ------------------------------------------------------------------
  # Back kick — hip extends to -2.3 rad (safe within -3.0 limit),
  # knee cocks fully then snaps, heel strike
  # ------------------------------------------------------------------
  "back": Trajectory(
    cycle=2.0,
    joints={
      "Left_Hip_Pitch": (0.0, -0.3, -2.3, 0.0),
      "Left_Knee_Pitch": (0.0, 1.8, 0.2, 0.0),
      "Left_Ankle_Pitch": (0.0, -0.4, -0.75, 0.0),
    },
  ),
  # ------------------------------------------------------------------
  # Chip / push kick — short forward arc (~0.7 rad), fast cycle,
  # ball-tap or close-range pass
  # ------------------------------------------------------------------
  "chip": Trajectory(
    cycle=0.8,
    joints={
      "Left_Hip_Pitch": (0.0, -0.3, 0.7, 0.0),
      "Left_Knee_Pitch": (0.0, 0.6, 0.05, 0.0),
      "Left_Ankle_Pitch": (0.0, -0.3, 0.2, 0.0),
    },
  ),
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def cubic_bezier(s: float, p0: float, p1: float, p2: float, p3: float) -> float:
  s = float(np.clip(s, 0.0, 1.0))
  return (
    (1 - s) ** 3 * p0 + 3 * (1 - s) ** 2 * s * p1 + 3 * (1 - s) * s**2 * p2 + s**3 * p3
  )


def get_qpos_adr(model: mujoco.MjModel, joint_name: str) -> int:
  jid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, joint_name)
  if jid == -1:
    raise ValueError(f"Joint '{joint_name}' not found in model.")
  return int(model.jnt_qposadr[jid])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
  p = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
  )
  p.add_argument(
    "--kick",
    choices=list(TRAJECTORIES),
    default="snap",
    metavar="NAME",
    help=f"Kick style: {', '.join(TRAJECTORIES)} (default: snap)",
  )
  p.add_argument(
    "--cycle",
    type=float,
    default=None,
    metavar="SECONDS",
    help="Override cycle duration in seconds",
  )
  return p.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
  args = parse_args()
  traj = TRAJECTORIES[args.kick]
  cycle_duration = args.cycle if args.cycle is not None else traj.cycle

  xml_path = Path(__file__).resolve().parent / "asset_zoo/robots/booster_k1/xml/k1.xml"
  spec = mujoco.MjSpec.from_file(str(xml_path))
  for joint in list(spec.joints):
    if joint.name == "floating_base_joint":
      spec.delete(joint)
      break
  model = spec.compile()
  data = mujoco.MjData(model)

  # Resolve joint addresses once.
  joint_addrs: dict[str, int] = {}
  for name in traj.joints:
    try:
      joint_addrs[name] = get_qpos_adr(model, name)
    except ValueError as e:
      print(f"Warning: {e}")

  steps_per_cycle = max(1, int(cycle_duration / model.opt.timestep))

  # Natural resting arm pose.
  for name, angle in [
    ("Left_Shoulder_Pitch", -0.2),
    ("Right_Shoulder_Pitch", -0.2),
    ("Left_Elbow_Pitch", 0.5),
    ("Right_Elbow_Pitch", 0.5),
  ]:
    try:
      data.qpos[get_qpos_adr(model, name)] = angle
    except ValueError:
      pass

  print(f"Kick: {args.kick!r}  |  cycle: {cycle_duration:.2f}s  |  Press ESC to exit.")

  with mujoco.viewer.launch_passive(model, data) as viewer:
    step = 0
    while viewer.is_running():
      t0 = time.time()
      s = (step % steps_per_cycle) / steps_per_cycle

      for name, (p0, p1, p2, p3) in traj.joints.items():
        if name in joint_addrs:
          data.qpos[joint_addrs[name]] = cubic_bezier(s, p0, p1, p2, p3)

      mujoco.mj_forward(model, data)
      viewer.sync()
      step += 1

      elapsed = time.time() - t0
      if elapsed < model.opt.timestep:
        time.sleep(model.opt.timestep - elapsed)


if __name__ == "__main__":
  main()

"""Soccer goal prop, ported from booster_mjlab.

The mesh is the small frame (1.80 m × 1.20 m). Mid and large scale it
uniformly. The mouth faces local +y and the net extends toward local −y.

Layout::

  asset_zoo/props/
    goal.py
    xml/goal.xml
    xml/assets/goal_180_120.obj
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Literal

import mujoco

GOAL_XML = Path(__file__).parent / "xml" / "goal.xml"
assert GOAL_XML.exists()

GoalDivision = Literal["small", "mid", "large"]

# Scale relative to the 1.80 m × 1.20 m mesh.
GOAL_DIVISION_SCALE: dict[GoalDivision, float] = {
  "small": 1.0,
  "mid": 240 / 180,
  "large": 300 / 180,
}

SMALL_GOAL_WIDTH = 1.80
SMALL_GOAL_HEIGHT = 1.20
MID_GOAL_WIDTH = 2.40
MID_GOAL_HEIGHT = 1.60
LARGE_GOAL_WIDTH = 3.00
LARGE_GOAL_HEIGHT = 2.00


def get_goal_spec(division: GoalDivision = "mid") -> mujoco.MjSpec:
  """Load the soccer goal. Default is mid: 2.40 m wide and 1.60 m tall."""
  spec = mujoco.MjSpec.from_file(str(GOAL_XML))

  for mesh in spec.meshes:
    mesh.name = f"{mesh.name}_{division}"

  for geom in spec.geoms:
    if geom.meshname:
      geom.meshname = f"{geom.meshname}_{division}"
    if geom.contype != 0 or geom.conaffinity != 0:
      geom.group = 3

  scale = GOAL_DIVISION_SCALE[division]
  if scale != 1.0:
    mesh = spec.meshes[0]
    mesh.scale = (scale, scale, scale)
    for geom in spec.geoms:
      if geom.group != 3:
        continue
      geom.pos = tuple(v * scale for v in geom.pos)
      geom.size = tuple(v * scale for v in geom.size)
      if not math.isnan(geom.fromto[0]):
        geom.fromto = tuple(v * scale for v in geom.fromto)

  return spec

"""Soccer ball prop — FIFA sphere with booster_mjlab visual meshes and rolling model.

Layout::

  asset_zoo/props/
    ball.py
    xml/ball.xml
    xml/assets/ball_size5_*.obj
"""

from pathlib import Path
from typing import Literal

import mujoco

BALL_XML: Path = Path(__file__).parent / "xml" / "ball.xml"
assert BALL_XML.exists()

BALL_SIZE_5_RADIUS = 0.11  # metres
BALL_SIZE_5_MASS = 0.430  # kg
BALL_COLLISION_CONDIM = 6
BALL_COLLISION_SOLREF = (0.05, 0.15)
BALL_SHELL_INERTIA = True
BALL_INERTIA_RATIO = 2 / 3 if BALL_SHELL_INERTIA else 2 / 5
BALL_SLIDING_FRICTION = 0.5
BALL_TORSIONAL_FRICTION = 0.002
BALL_ROLLING_RESISTANCE = 0.060
_ROLLING_FRICTION_SOLVER_GAIN = 1.0

# Scale factors relative to FIFA size 5.
BALL_SIZE_SCALES: dict[int, dict[str, float]] = {
  1: {"size": 0.6304, "weight": 0.4419},
  2: {"size": 0.8188, "weight": 0.6163},
  3: {"size": 0.8551, "weight": 0.7209},
  4: {"size": 0.9384, "weight": 0.8605},
  5: {"size": 1.0, "weight": 1.0},
}

BallSize = Literal[1, 2, 3, 4, 5]


def get_ball_radius(size: BallSize = 5) -> float:
  return BALL_SIZE_5_RADIUS * BALL_SIZE_SCALES[size]["size"]


def get_ball_mass(size: BallSize = 5) -> float:
  return BALL_SIZE_5_MASS * BALL_SIZE_SCALES[size]["weight"]


def get_rolling_friction(
  size: BallSize = 5,
  rolling_resistance: float = BALL_ROLLING_RESISTANCE,
) -> float:
  """MuJoCo rolling-friction length for dimensionless C_r = |a| / g."""
  radius = get_ball_radius(size)
  return (1.0 + BALL_INERTIA_RATIO) * rolling_resistance * radius / _ROLLING_FRICTION_SOLVER_GAIN


def get_ball_friction(
  size: BallSize = 5,
  rolling_resistance: float = BALL_ROLLING_RESISTANCE,
) -> tuple[float, float, float]:
  return (
    BALL_SLIDING_FRICTION,
    BALL_TORSIONAL_FRICTION,
    get_rolling_friction(size, rolling_resistance),
  )


def get_ball_spec(size: BallSize = 5) -> mujoco.MjSpec:
  """Load the textured FIFA ball (shell inertia, elliptic-ready condim=6).

  Default size 5 matches kick spawn / observations (radius 0.11 m).
  """
  spec = mujoco.MjSpec.from_file(str(BALL_XML))
  friction = get_ball_friction(size)
  scale_factor = BALL_SIZE_SCALES[size]["size"]
  mass = get_ball_mass(size)
  radius = get_ball_radius(size)

  if scale_factor != 1.0:
    for mesh in spec.meshes:
      mesh.scale = (scale_factor, scale_factor, scale_factor)

  ball_body = spec.worldbody.bodies[0]
  for geom in ball_body.geoms:
    if geom.name.startswith("ball_visual"):
      geom.mass = 0.0
      geom.density = 0.0
      geom.friction = friction
    elif geom.name == "ball_collision":
      geom.group = 3
      geom.size = (radius, 0, 0)
      if BALL_SHELL_INERTIA:
        geom.typeinertia = mujoco.mjtGeomInertia.mjINERTIA_SHELL
      geom.priority = 1
      geom.condim = BALL_COLLISION_CONDIM
      geom.mass = mass
      geom.solref = BALL_COLLISION_SOLREF
      geom.friction = friction

  return spec

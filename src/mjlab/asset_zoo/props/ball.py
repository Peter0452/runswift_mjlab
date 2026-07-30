"""Soccer ball prop asset."""

import mujoco


def get_ball_spec(
  radius: float = 0.11,
  mass: float = 0.43,
  restitution: float = 0.7,
  friction: tuple[float, float, float] = (0.8, 0.005, 0.0001),
  rgba: tuple[float, float, float, float] = (0.9, 0.5, 0.1, 1.0),
) -> mujoco.MjSpec:
  """Build a soccer-ball MjSpec.

  Args:
    radius: Ball radius in metres (FIFA size-5 ≈ 0.11 m).
    mass: Ball mass in kg (FIFA ≈ 0.43 kg).
    restitution: Coefficient of restitution (elasticity). 1.0 = perfectly
      elastic. 0.7 is a reasonable value for a pumped soccer ball.
    friction: MuJoCo (slide, spin, roll) friction tuple.
    rgba: Colour.

  Returns:
    An ``MjSpec`` with a single free-floating sphere body named ``"ball"``.
  """
  spec = mujoco.MjSpec()

  # Global contact solver tweak: lower solimp/solref for a lively bounce.
  spec.option.timestep = 0.005  # overridden by the sim config at merge time

  body = spec.worldbody.add_body(name="ball")
  body.add_freejoint(name="ball_joint")
  body.add_geom(
    name="ball_geom",
    type=mujoco.mjtGeom.mjGEOM_SPHERE,
    size=(radius, 0.0, 0.0),
    mass=mass,
    rgba=rgba,
    friction=friction,
    # solref: stiffness ratio (negative = timestep-relative), restitution.
    # solimp: penetration limits and contact-force profile.
    solref=(-200.0, restitution),
    solimp=(0.9, 0.99, 0.001, 0.4, 2.0),
  )

  return spec

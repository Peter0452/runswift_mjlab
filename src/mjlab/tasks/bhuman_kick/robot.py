"""B-Human's K1 kick robot and ball (Booster Gym ``K1_Ball.yaml``).

Robot: our ``k1.xml`` (same kinematics, masses and armature as B-Human's
``K1_locomotion*.urdf``) with B-Human's training changes:

- head and arms welded at the URDF's fixed pose (shoulder roll -/+1.35 rad),
  leaving the 12 leg joints in B-Human's DOF order;
- box sole (0.18 x 0.07 x 0.016 m), box shin and a small toe nub. B-Human
  trains three robot variants side by side (mesh feet, nub left, nub right).
  One MuJoCo model serves all worlds here, so the nub's y offset is set per
  env at startup instead (left, right, or tucked inside the sole);
- leg PD from ``control`` (Isaac Gym gains, armature, torque clip).

Ball: radius 0.095 m, 0.29 kg, solid sphere, restitution ~0.1. Isaac Gym's
linear / angular damping (0.75 / 0.5 per second) is applied by the kick
command once per policy step.
"""

from __future__ import annotations

import functools

import mujoco
import numpy as np

from mjlab.asset_zoo.props.ball import BALL_XML, get_ball_radius
from mjlab.asset_zoo.robots.booster_k1.k1_constants import get_spec as get_k1_spec
from mjlab.entity import EntityArticulationInfoCfg, EntityCfg
from mjlab.tasks.bhuman_kick.actuator import BHumanPdActuatorCfg
from mjlab.utils.spec_config import CollisionCfg

##
# Joints (B-Human DOF order) and control constants.
##

LEG_JOINTS: tuple[str, ...] = tuple(
  f"{side}_{j}"
  for side in ("Left", "Right")
  for j in (
    "Hip_Pitch",
    "Hip_Roll",
    "Hip_Yaw",
    "Knee_Pitch",
    "Ankle_Pitch",
    "Ankle_Roll",
  )
)

# init_state.default_joint_angles.
DEFAULT_LEG_POS = (-0.2, 0.0, 0.0, 0.4, -0.25, 0.0) * 2

# URDF <limit effort>, used by the torque_limits / torque_tiredness rewards.
URDF_EFFORT = (30.0, 35.0, 20.0, 40.0, 20.0, 20.0) * 2
# control.torque_clipping: the torque the motors may actually apply.
TORQUE_CLIP = (50.0, 50.0, 30.0, 60.0, 30.0, 30.0) * 2

# Joints fixed in B-Human's URDF, and their angle there.
WELDED_JOINTS: dict[str, float] = {
  "Head_Yaw": 0.0,
  "Head_Pitch": 0.0,
  "Left_Shoulder_Pitch": 0.0,
  "Left_Shoulder_Roll": -1.35,
  "Left_Elbow_Pitch": 0.0,
  "Left_Elbow_Yaw": 0.0,
  "Right_Shoulder_Pitch": 0.0,
  "Right_Shoulder_Roll": 1.35,
  "Right_Elbow_Pitch": 0.0,
  "Right_Elbow_Yaw": 0.0,
}

FEET = ("left_foot_link", "right_foot_link")
# asset.feet_edge_pos / feet_sole_pos (foot body frame).
FEET_EDGE_POS = (
  (0.1185, 0.035, -0.038),
  (0.1185, -0.035, -0.038),
  (-0.0665, 0.035, -0.038),
  (-0.0665, -0.035, -0.038),
)
FEET_SOLE_POS = (0.0, 0.0, -0.038)

# Toe nub y offsets of B-Human's left / right bias URDFs; "none" tucks it
# inside the sole box (the mesh-foot variant has no nub).
TOE_NUB_Y = {"left": 0.015, "right": -0.015}
TOE_NUB_HIDDEN_POS = (0.026, 0.0, -0.030)

BALL_RADIUS = 0.095
BALL_MASS = 0.290


def _weld(spec: mujoco.MjSpec, name: str, angle: float) -> None:
  joint = spec.joint(name)
  body = joint.parent
  q = np.zeros(4)
  mujoco.mju_axisAngle2Quat(q, np.asarray(joint.axis, dtype=float), angle)
  out = np.zeros(4)
  mujoco.mju_mulQuat(out, np.asarray(body.quat, dtype=float), q)
  body.quat = out
  spec.delete(joint)


def _box(body: mujoco.MjsBody, name: str, half, pos) -> None:
  body.add_geom(
    name=name,
    type=mujoco.mjtGeom.mjGEOM_BOX,
    size=half,
    pos=pos,
    group=3,
    rgba=(0.2, 0.6, 0.2, 0.3),
  )


def get_bhuman_k1_spec() -> mujoco.MjSpec:
  spec = get_k1_spec()
  for name, angle in WELDED_JOINTS.items():
    _weld(spec, name, angle)
  for side in ("left", "right"):
    foot = spec.body(f"{side}_foot_link")
    for geom in list(foot.geoms):
      if geom.name.startswith(f"{side}_foot") and geom.name.endswith("_collision"):
        spec.delete(geom)
    _box(foot, f"{side}_sole_collision", (0.09, 0.035, 0.008), (0.026, 0.0, -0.030))
    _box(foot, f"{side}_toe_collision", (0.005, 0.0025, 0.005), (0.11, 0.015, 0.002))
    shank = spec.body(f"{side.capitalize()}_Shank")
    spec.delete(spec.geom(f"{side}_shin_collision"))
    _box(shank, f"{side}_shin_collision", (0.04, 0.035, 0.065), (0.0, 0.0, -0.13))
  return spec


def get_bhuman_ball_spec(
  friction: tuple[float, float, float] = (0.65, 0.005, 0.0001),
  condim: int = 3,
  solref: tuple[float, float] = (0.01, 0.8),
) -> mujoco.MjSpec:
  """Size-5 visual mesh scaled to B-Human's ball; solid-sphere inertia.
  Default contact: stiff, mostly inelastic (PhysX restitution 0.1); torsional
  and rolling friction act only with ``condim`` 6."""
  spec = mujoco.MjSpec.from_file(str(BALL_XML))
  scale = BALL_RADIUS / get_ball_radius(5)
  for mesh in spec.meshes:
    mesh.scale = (scale, scale, scale)
  for geom in spec.worldbody.bodies[0].geoms:
    if geom.name.startswith("ball_visual"):
      geom.mass = 0.0
      geom.density = 0.0
    elif geom.name == "ball_collision":
      geom.size = (BALL_RADIUS, 0, 0)
      geom.mass = BALL_MASS
      geom.condim = condim
      geom.priority = 1
      geom.friction = friction
      geom.solref = solref
  return spec


##
# Leg PD (control.stiffness / damping / armature, Isaac Gym values).
##


def _leg(
  joint: str, kp: float, kd: float, clip: float, armature: float
) -> BHumanPdActuatorCfg:
  return BHumanPdActuatorCfg(
    target_names_expr=(f".*_{joint}",),
    stiffness=kp,
    damping=kd,
    effort_limit=clip,
    torque_clip=clip,
    armature=armature,
  )


BHUMAN_K1_ARTICULATION = EntityArticulationInfoCfg(
  actuators=(
    _leg("Hip_Pitch", 80.0, 4.0, 50.0, 0.0478125),
    _leg("Hip_Roll", 80.0, 4.0, 50.0, 0.0339552),
    _leg("Hip_Yaw", 80.0, 4.0, 30.0, 0.0282528),
    _leg("Knee_Pitch", 80.0, 4.0, 60.0, 0.095625),
    _leg("Ankle_Pitch", 50.0, 2.0, 30.0, 0.0565056),
    _leg("Ankle_Roll", 60.0, 2.0, 30.0, 0.0565056),
  ),
  soft_joint_pos_limit_factor=1.0,
)

_SOLE_REGEX = r"^(left|right)_(sole|toe)_collision$"

BHUMAN_K1_COLLISION = CollisionCfg(
  geom_names_expr=(".*_collision",),
  condim={_SOLE_REGEX: 3, ".*_collision": 1},
  priority={_SOLE_REGEX: 1},
  friction={_SOLE_REGEX: (0.65,)},
)


def get_bhuman_k1_cfg() -> EntityCfg:
  # init_state.pos z 0.60 is Isaac Gym's drop height; here the robot starts
  # with its soles just above the ground (0.542 m at the default pose).
  return EntityCfg(
    init_state=EntityCfg.InitialStateCfg(
      pos=(0.0, 0.0, 0.545),
      joint_pos=dict(zip(LEG_JOINTS, DEFAULT_LEG_POS, strict=True)),
      joint_vel={".*": 0.0},
    ),
    collisions=(BHUMAN_K1_COLLISION,),
    spec_fn=get_bhuman_k1_spec,
    articulation=BHUMAN_K1_ARTICULATION,
  )


def get_bhuman_ball_cfg(**spec_kwargs) -> EntityCfg:
  if not spec_kwargs:
    return EntityCfg(spec_fn=get_bhuman_ball_spec)
  return EntityCfg(spec_fn=functools.partial(get_bhuman_ball_spec, **spec_kwargs))

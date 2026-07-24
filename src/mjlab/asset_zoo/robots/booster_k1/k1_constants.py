"""Booster K1 constants for mjlab.

Layout::

  asset_zoo/robots/booster_k1/
    k1_constants.py
    xml/k1.xml
    xml/assets/*.STL
"""

from pathlib import Path

import mujoco

from mjlab.actuator import BuiltinPositionActuatorCfg
from mjlab.entity import EntityArticulationInfoCfg, EntityCfg
from mjlab.utils.spec_config import CollisionCfg

##
# MJCF and assets.
##

K1_XML: Path = Path(__file__).parent / "xml" / "k1.xml"
assert K1_XML.exists()


def get_spec() -> mujoco.MjSpec:
  return mujoco.MjSpec.from_file(str(K1_XML))


##
# Actuator config.
##
# Armature from Booster MJCF (reflected inertia). PD gains, torque limits,
# default pose, and action scale from the Isaac Gym K1 walk deploy config
# (common.stiffness / damping / torque_limit / default_qpos,
#  policy.control.action_scale = 1.0).
#
# Joint order in that config:
#   Head(2), LeftArm(4), RightArm(4), LeftLeg(6), RightLeg(6)

ARMATURE_KNEE = 0.095625
ARMATURE_HIP_PITCH = 0.0478125
ARMATURE_HIP_ROLL = 0.0339552
ARMATURE_HIP_YAW = 0.0282528
ARMATURE_ANKLE = 0.0565
ARMATURE_ARM = 0.001
ARMATURE_HEAD = 0.002

# Isaac Gym torque_limit (Nm).
EFFORT_HEAD = 7.0
EFFORT_ARM = 10.0
EFFORT_HIP_PITCH = 30.0
EFFORT_HIP_ROLL = 20.0
EFFORT_HIP_YAW = 20.0
EFFORT_KNEE = 40.0
EFFORT_ANKLE_PITCH = 20.0
EFFORT_ANKLE_ROLL = 15.0

# Isaac Gym common.stiffness / common.damping.
STIFFNESS_HEAD = 2.0
DAMPING_HEAD = 0.2
STIFFNESS_ARM = 5.0
DAMPING_ARM = 0.5
STIFFNESS_HIP = 80.0
DAMPING_HIP = 4.0
STIFFNESS_KNEE = 80.0
DAMPING_KNEE = 4.0
STIFFNESS_ANKLE = 25.0
DAMPING_ANKLE = 1.0

# Isaac policy.control.action_scale. Do NOT use mjlab's 0.25*effort/stiffness
# here — with kp=80 that yields ~0.09 rad and blocks gait learning.
ISAAC_ACTION_SCALE = 1.0


# Command (policy -> motor bus) latency. The ideal PD model applies each target
# the same substep the policy issues it; the real K1 has comms/driver lag. Delay
# the command 0-3 physics substeps (0-15 ms at the 5 ms timestep) and mostly hold
# the sampled lag (hold_prob) so each episode sees a steady-but-randomized delay
# with occasional jitter, instead of resampling white noise every substep.
def _k1_actuator(
  target_names_expr: tuple[str, ...],
  *,
  stiffness: float,
  damping: float,
  effort_limit: float,
  armature: float,
) -> BuiltinPositionActuatorCfg:
  return BuiltinPositionActuatorCfg(
    target_names_expr=target_names_expr,
    stiffness=stiffness,
    damping=damping,
    effort_limit=effort_limit,
    armature=armature,
    delay_min_lag=2,
    delay_max_lag=16,
    delay_hold_prob=0.9,
  )


K1_ACTUATOR_HIP_PITCH = _k1_actuator(
  (".*_Hip_Pitch",),
  stiffness=STIFFNESS_HIP,
  damping=DAMPING_HIP,
  effort_limit=EFFORT_HIP_PITCH,
  armature=ARMATURE_HIP_PITCH,
)
K1_ACTUATOR_HIP_ROLL = _k1_actuator(
  (".*_Hip_Roll",),
  stiffness=STIFFNESS_HIP,
  damping=DAMPING_HIP,
  effort_limit=EFFORT_HIP_ROLL,
  armature=ARMATURE_HIP_ROLL,
)
K1_ACTUATOR_HIP_YAW = _k1_actuator(
  (".*_Hip_Yaw",),
  stiffness=STIFFNESS_HIP,
  damping=DAMPING_HIP,
  effort_limit=EFFORT_HIP_YAW,
  armature=ARMATURE_HIP_YAW,
)
K1_ACTUATOR_KNEE = _k1_actuator(
  (".*_Knee_Pitch",),
  stiffness=STIFFNESS_KNEE,
  damping=DAMPING_KNEE,
  effort_limit=EFFORT_KNEE,
  armature=ARMATURE_KNEE,
)
K1_ACTUATOR_ANKLE_PITCH = _k1_actuator(
  (".*_Ankle_Pitch",),
  stiffness=STIFFNESS_ANKLE,
  damping=DAMPING_ANKLE,
  effort_limit=EFFORT_ANKLE_PITCH,
  armature=ARMATURE_ANKLE,
)
K1_ACTUATOR_ANKLE_ROLL = _k1_actuator(
  (".*_Ankle_Roll",),
  stiffness=STIFFNESS_ANKLE,
  damping=DAMPING_ANKLE,
  effort_limit=EFFORT_ANKLE_ROLL,
  armature=ARMATURE_ANKLE,
)
K1_ACTUATOR_ARM = _k1_actuator(
  (
    ".*_Shoulder_Pitch",
    ".*_Shoulder_Roll",
    ".*_Elbow_Pitch",
    ".*_Elbow_Yaw",
  ),
  stiffness=STIFFNESS_ARM,
  damping=DAMPING_ARM,
  effort_limit=EFFORT_ARM,
  armature=ARMATURE_ARM,
)
K1_ACTUATOR_HEAD = _k1_actuator(
  ("Head_Yaw", "Head_Pitch"),
  stiffness=STIFFNESS_HEAD,
  damping=DAMPING_HEAD,
  effort_limit=EFFORT_HEAD,
  armature=ARMATURE_HEAD,
)

##
# Keyframe config (Isaac Gym common.default_qpos).
##

# Arms folded behind the back (elbows bent, forearms swept down/in) to avoid
# entanglement in ball contests. With these angles the hands sit behind the
# trunk near the midline at ~waist height (hand center ~ x=-0.08, y=0.10,
# z=-0.04 in the trunk frame), collision-free. Head/arms are PD-held, not
# policy-controlled.
_TUCKED_ARM_HEAD_POS = {
  "Head_Yaw": 0.0,
  "Head_Pitch": 0.0,
  "Left_Shoulder_Pitch": 0.3,
  "Left_Shoulder_Roll": -1.65,
  "Left_Elbow_Pitch": 2.0,
  "Left_Elbow_Yaw": -0.45,
  "Right_Shoulder_Pitch": 0.3,
  "Right_Shoulder_Roll": 1.65,
  "Right_Elbow_Pitch": 2.0,
  "Right_Elbow_Yaw": 0.45,
}

HOME_KEYFRAME = EntityCfg.InitialStateCfg(
  pos=(0, 0, 0.54),
  joint_pos={
    **_TUCKED_ARM_HEAD_POS,
    ".*_Hip_Pitch": -0.2,
    ".*_Hip_Roll": 0.0,
    ".*_Hip_Yaw": 0.0,
    ".*_Knee_Pitch": 0.4,
    ".*_Ankle_Pitch": -0.25,
    ".*_Ankle_Roll": 0.0,
  },
  joint_vel={".*": 0.0},
)

# Deeper squat for training resets: lower CoM and pre-bent legs so the
# policy is closer to a walk-ready stance (same tucked arm/head pose).
# Base height chosen so foot collision bottoms sit near z=0.
KNEES_BENT_KEYFRAME = EntityCfg.InitialStateCfg(
  pos=(0, 0, 0.525),
  joint_pos={
    **_TUCKED_ARM_HEAD_POS,
    ".*_Hip_Pitch": -0.35,
    ".*_Hip_Roll": 0.0,
    ".*_Hip_Yaw": 0.0,
    ".*_Knee_Pitch": 0.70,
    ".*_Ankle_Pitch": -0.40,
    ".*_Ankle_Roll": 0.0,
  },
  joint_vel={".*": 0.0},
)

##
# Collision config.
##

_FOOT_REGEX = r"^(left|right)_foot[1-5]_collision$"

FULL_COLLISION = CollisionCfg(
  geom_names_expr=(".*_collision",),
  condim={_FOOT_REGEX: 3, ".*_collision": 1},
  priority={_FOOT_REGEX: 1},
  friction={_FOOT_REGEX: (0.6,)},
)

FULL_COLLISION_WITHOUT_SELF = CollisionCfg(
  geom_names_expr=(".*_collision",),
  contype=0,
  conaffinity=1,
  condim={_FOOT_REGEX: 3, ".*_collision": 1},
  priority={_FOOT_REGEX: 1},
  friction={_FOOT_REGEX: (0.6,)},
)

FEET_ONLY_COLLISION = CollisionCfg(
  geom_names_expr=(_FOOT_REGEX,),
  contype=0,
  conaffinity=1,
  condim=3,
  priority=1,
  friction=(0.6,),
)

##
# Final config.
##

K1_ARTICULATION = EntityArticulationInfoCfg(
  actuators=(
    K1_ACTUATOR_HIP_PITCH,
    K1_ACTUATOR_HIP_ROLL,
    K1_ACTUATOR_HIP_YAW,
    K1_ACTUATOR_KNEE,
    K1_ACTUATOR_ANKLE_PITCH,
    K1_ACTUATOR_ANKLE_ROLL,
    K1_ACTUATOR_ARM,
    K1_ACTUATOR_HEAD,
  ),
  soft_joint_pos_limit_factor=0.9,
)


def get_k1_robot_cfg() -> EntityCfg:
  """Get a fresh K1 robot configuration instance."""
  return EntityCfg(
    init_state=KNEES_BENT_KEYFRAME,
    collisions=(FULL_COLLISION,),
    spec_fn=get_spec,
    articulation=K1_ARTICULATION,
  )


# Match Isaac Gym policy.control.action_scale = 1.0 (not 0.25*effort/stiffness).
K1_ACTION_SCALE: dict[str, float] = {}
for a in K1_ARTICULATION.actuators:
  assert isinstance(a, BuiltinPositionActuatorCfg)
  for n in a.target_names_expr:
    K1_ACTION_SCALE[n] = ISAAC_ACTION_SCALE


if __name__ == "__main__":
  import mujoco
  import mujoco.viewer as viewer

  from mjlab.entity.entity import Entity

  robot = Entity(get_k1_robot_cfg())
  model = robot.spec.compile()

  # `viewer.launch(model)` starts at the all-zero default qpos, so the arms/head
  # would appear at 0. Load the "init_state" keyframe (added by Entity from
  # KNEES_BENT_KEYFRAME) so the viewer shows the training crouch.
  data = mujoco.MjData(model)
  mujoco.mj_resetDataKeyframe(model, data, model.key("init_state").id)
  mujoco.mj_forward(model, data)
  viewer.launch(model, data)

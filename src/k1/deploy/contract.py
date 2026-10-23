"""The deployment contract with k1_policy_runner: what the robot runtime assumes.

The single source for the values below; ``knowledge/deployment.md`` is the
readable version. Changing any of them is a runtime change: make the matching
runner change, pass the parity checks, and say so in the commit.
``tests/test_deploy_contract.py`` checks the deployed tasks' configs against it.
"""

# Control loop: the runner steps the policy at 50 Hz; training runs 200 Hz
# physics with 4 physics steps per policy step.
RATE_HZ = 50
PHYSICS_DT = 0.005
DECIMATION = 4

# Order of the 22 joint targets (policy outputs) and of every 22-joint
# observation block.
JOINT_ORDER = (
  "Head_Yaw",
  "Head_Pitch",
  "Left_Shoulder_Pitch",
  "Left_Shoulder_Roll",
  "Left_Elbow_Pitch",
  "Left_Elbow_Yaw",
  "Right_Shoulder_Pitch",
  "Right_Shoulder_Roll",
  "Right_Elbow_Pitch",
  "Right_Elbow_Yaw",
  "Left_Hip_Pitch",
  "Left_Hip_Roll",
  "Left_Hip_Yaw",
  "Left_Knee_Pitch",
  "Left_Ankle_Pitch",
  "Left_Ankle_Roll",
  "Right_Hip_Pitch",
  "Right_Hip_Roll",
  "Right_Hip_Yaw",
  "Right_Knee_Pitch",
  "Right_Ankle_Pitch",
  "Right_Ankle_Roll",
)

# target = default + scale * action. Exported to ONNX metadata with 6 decimals
# (3 was a bug: lesson S5).
DEFAULT_POSE = {
  "Left_Shoulder_Roll": -1.4,
  "Left_Elbow_Yaw": -0.4,
  "Right_Shoulder_Roll": 1.4,
  "Right_Elbow_Yaw": 0.4,
  "Left_Hip_Pitch": -0.4,
  "Left_Knee_Pitch": 0.8,
  "Left_Ankle_Pitch": -0.4,
  "Right_Hip_Pitch": -0.4,
  "Right_Knee_Pitch": 0.8,
  "Right_Ankle_Pitch": -0.4,
}
ACTION_SCALE = {
  "Head_.*": 0.375,
  ".*_Shoulder_.*": 0.35,
  ".*_Elbow_.*": 0.35,
  ".*_Hip_Pitch": 0.2125,
  ".*_Hip_Roll": 0.2375,
  ".*_Hip_Yaw": 0.119687,
  ".*_Knee_Pitch": 0.35,
  ".*_Ankle_.*": 0.1915,
}
# PD gains (kp, kd); training randomises them x0.8-1.2.
PD_GAINS = {
  "Head_.*": (4.0, 0.25),
  ".*_Shoulder_.*": (10.0, 1.0),
  ".*_Elbow_.*": (10.0, 1.0),
  ".*_Hip_Pitch": (80.0, 4.0),
  ".*_Hip_Roll": (80.0, 4.0),
  ".*_Hip_Yaw": (80.0, 4.0),
  ".*_Knee_Pitch": (80.0, 4.0),
  ".*_Ankle_.*": (50.0, 2.0),
}

# Deployment match of the kick-loop family (kick loop, dribble, self-play):
# what the runner does to the policy's targets, reproduced in training.
# Hard leg torque limits (N*m), user 2026-10-07: B-Human's kick clip
# (K1_Ball.yaml torque_clipping). The motor ratings in k1_whirlwind_constants
# (knee 112, hip roll 76, hip pitch 68, hip yaw / ankle 38.3) are believed to
# be no-load numbers; the real loaded limits are not measured yet - replace
# these when they are. B-Human's own note on "real" limits: 80/60/40/70/36/36.
LEG_TORQUE_CLIP = {
  ".*_Hip_Pitch": 50.0,
  ".*_Hip_Roll": 50.0,
  ".*_Hip_Yaw": 30.0,
  ".*_Knee_Pitch": 60.0,
  ".*_Ankle_.*": 30.0,
}


# Joint-target clip of k1_policy_runner (walk_policy_amp_v1.Q_ABS_LIMITS): the
# runner (robot, runswift fixture) clips every target to these. Training did
# not until 2026-10-07; x4_g004_70 pressed hip roll up to 0.38 rad past the
# 0.40 rad stop around kicks and lost its aim under the clip (86 % -> 19 %).
DEPLOY_Q_LIMITS = {
  "Head_Yaw": (-1.0, 1.0),
  "Head_Pitch": (-0.349, 0.855),
  "Left_Shoulder_Pitch": (-3.316, 1.22),
  "Left_Shoulder_Roll": (-1.74, 1.57),
  "Left_Elbow_Pitch": (-2.27, 2.27),
  "Left_Elbow_Yaw": (-2.44, 0.0),
  "Right_Shoulder_Pitch": (-3.316, 1.22),
  "Right_Shoulder_Roll": (-1.57, 1.74),
  "Right_Elbow_Pitch": (-2.27, 2.27),
  "Right_Elbow_Yaw": (0.0, 2.44),
  ".*_Hip_Pitch": (-3.0, 2.21),
  "Left_Hip_Roll": (-0.4, 1.57),
  "Right_Hip_Roll": (-1.57, 0.4),
  ".*_Hip_Yaw": (-1.0, 1.0),
  ".*_Knee_Pitch": (0.0, 2.23),
  ".*_Ankle_Pitch": (-0.87, 0.345),
  ".*_Ankle_Roll": (-0.345, 0.345),
}

# Motor delay the policy must tolerate: 0-40 ms (physics steps of 5 ms),
# including zero (lesson S2). The runner adds none.
MOTOR_DELAY_STEPS = (0, 8)

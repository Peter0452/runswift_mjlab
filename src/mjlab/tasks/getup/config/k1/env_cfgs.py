"""Booster K1 get-up environment configuration.

Discovery-based port of ``booster_train`` ``Booster-K1-Getup-v1``: one policy
rises from any fallen posture (supine / prone / side) with no reference motion.
"""

from __future__ import annotations

import math
from dataclasses import replace

from mjlab.asset_zoo.robots.booster_k1.k1_constants import (
  HOME_KEYFRAME,
  get_k1_robot_cfg,
)
from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.envs.mdp import dr
from mjlab.envs.mdp.actions import JointPositionActionCfg
from mjlab.managers.curriculum_manager import CurriculumTermCfg
from mjlab.managers.event_manager import EventTermCfg
from mjlab.managers.observation_manager import ObservationGroupCfg, ObservationTermCfg
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.managers.termination_manager import TerminationTermCfg
from mjlab.scene import SceneCfg
from mjlab.sim import MujocoCfg, SimulationCfg
from mjlab.tasks.getup import mdp
from mjlab.terrains import TerrainEntityCfg
from mjlab.utils.noise import UniformNoiseCfg as Unoise
from mjlab.viewer import ViewerConfig

# Legs (12) + arms (8); head locked at default (push-off needs arms).
_K1_GETUP_ACTION_JOINTS = (
  ".*_Hip_Pitch",
  ".*_Hip_Roll",
  ".*_Hip_Yaw",
  ".*_Knee_Pitch",
  ".*_Ankle_Pitch",
  ".*_Ankle_Roll",
  ".*_Shoulder_Pitch",
  ".*_Shoulder_Roll",
  ".*_Elbow_Pitch",
  ".*_Elbow_Yaw",
)
_K1_PASSIVE_JOINTS = ("Head_.*",)
_K1_ARM_JOINTS = (
  ".*_Shoulder_Pitch",
  ".*_Shoulder_Roll",
  ".*_Elbow_Pitch",
  ".*_Elbow_Yaw",
)

# Verified K1 standing base height (asset HOME / booster_train STAND_HEIGHT).
_K1_STAND_HEIGHT = 0.57
_K1_GETUP_SPAWN_Z = 0.35
_K1_FOOT_FRICTION_GEOMS = r"^(left|right)_foot[1-5]_collision$"


def _getup_policy_joint_cfg() -> SceneEntityCfg:
  return SceneEntityCfg(
    "robot",
    joint_names=_K1_GETUP_ACTION_JOINTS,
    actuator_names=list(_K1_GETUP_ACTION_JOINTS),
    preserve_order=True,
  )


def _getup_robot_cfg():
  """K1 with low spawn height for fallen resets (orientation randomized later)."""
  robot = get_k1_robot_cfg()
  # Prefer HOME joint defaults (straighter legs) as the standing target for
  # arms_at_side / joint scale reset; spawn z is overridden for fallen starts.
  init = replace(HOME_KEYFRAME, pos=(0.0, 0.0, _K1_GETUP_SPAWN_Z))
  return replace(robot, init_state=init)


def booster_k1_getup_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Flat-plane K1 get-up env (``Mjlab-Getup-Flat-Booster-K1``)."""
  policy_joints = _getup_policy_joint_cfg()
  arm_joints = SceneEntityCfg("robot", joint_names=_K1_ARM_JOINTS)

  actor_terms = {
    "projected_gravity": ObservationTermCfg(
      func=mdp.projected_gravity,
      noise=None if play else Unoise(n_min=-0.05, n_max=0.05),
    ),
    "base_ang_vel": ObservationTermCfg(
      func=mdp.base_ang_vel,
      noise=None if play else Unoise(n_min=-0.2, n_max=0.2),
    ),
    "joint_pos": ObservationTermCfg(
      func=mdp.joint_pos_rel,
      params={"asset_cfg": policy_joints},
      noise=None if play else Unoise(n_min=-0.01, n_max=0.01),
    ),
    "joint_vel": ObservationTermCfg(
      func=mdp.joint_vel_rel,
      params={"asset_cfg": policy_joints},
      scale=0.1,
      noise=None if play else Unoise(n_min=-0.15, n_max=0.15),
    ),
    "actions": ObservationTermCfg(func=mdp.last_action),
  }
  critic_terms = {
    **actor_terms,
    "base_lin_vel": ObservationTermCfg(func=mdp.base_lin_vel),
    "base_height": ObservationTermCfg(func=mdp.base_height),
  }

  observations = {
    "actor": ObservationGroupCfg(
      terms=actor_terms,
      concatenate_terms=True,
      enable_corruption=not play,
    ),
    "critic": ObservationGroupCfg(
      terms=critic_terms,
      concatenate_terms=True,
      enable_corruption=False,
    ),
  }

  actions = {
    "joint_pos": JointPositionActionCfg(
      entity_name="robot",
      actuator_names=_K1_GETUP_ACTION_JOINTS,
      scale=0.8,
      use_default_offset=True,
      preserve_order=True,
    )
  }

  stand_params = {"stand_height": _K1_STAND_HEIGHT}
  rewards = {
    "standing_bonus": RewardTermCfg(
      func=mdp.standing_bonus, weight=10.0, params=dict(stand_params)
    ),
    "upright_climb": RewardTermCfg(
      func=mdp.upright_climb, weight=10.0, params=dict(stand_params)
    ),
    "head_height": RewardTermCfg(
      func=mdp.head_height,
      weight=3.0,
      params={"max_diff": 0.7},
    ),
    "upright": RewardTermCfg(func=mdp.upright, weight=3.0),
    "feet_under_body": RewardTermCfg(func=mdp.feet_under_body, weight=2.0),
    "time_penalty": RewardTermCfg(
      func=mdp.not_standing_time_penalty,
      weight=-0.3,
      params=dict(stand_params),
    ),
    "rising_velocity": RewardTermCfg(
      func=mdp.rising_velocity,
      weight=1.0,
      params={"max_vel": 1.0},
    ),
    "standing_stability": RewardTermCfg(
      func=mdp.standing_stability, weight=2.0, params=dict(stand_params)
    ),
    "arms_at_side": RewardTermCfg(
      func=mdp.arms_at_side,
      weight=1.0,
      params={**stand_params, "asset_cfg": arm_joints},
    ),
    "dof_torques": RewardTermCfg(
      func=mdp.joint_torques_l2,
      weight=-1.0e-4,
      params={"asset_cfg": policy_joints},
    ),
    "dof_vel": RewardTermCfg(
      func=mdp.joint_vel_l2,
      weight=-1.0e-3,
      params={"asset_cfg": policy_joints},
    ),
    "dof_acc": RewardTermCfg(
      func=mdp.joint_acc_l2,
      weight=-1.0e-7,
      params={"asset_cfg": policy_joints},
    ),
    "action_rate": RewardTermCfg(func=mdp.action_rate_l2, weight=-0.01),
    "dof_pos_limits": RewardTermCfg(
      func=mdp.joint_pos_limits,
      weight=-1.0,
      params={"asset_cfg": policy_joints},
    ),
  }

  terminations = {
    "time_out": TerminationTermCfg(func=mdp.time_out, time_out=True),
  }

  events = {
    "reset_base": EventTermCfg(
      func=mdp.reset_root_state_uniform,
      mode="reset",
      params={
        "pose_range": {
          "x": (-0.3, 0.3),
          "y": (-0.3, 0.3),
          "roll": (-math.pi, math.pi),
          "pitch": (-math.pi, math.pi),
          "yaw": (-math.pi, math.pi),
        },
        "velocity_range": {
          "x": (0.0, 0.0),
          "y": (0.0, 0.0),
          "z": (0.0, 0.0),
          "roll": (0.0, 0.0),
          "pitch": (0.0, 0.0),
          "yaw": (0.0, 0.0),
        },
      },
    ),
    "reset_robot_joints": EventTermCfg(
      func=mdp.reset_joints_by_scale,
      mode="reset",
      params={
        "position_range": (1.0, 1.0) if play else (0.8, 1.2),
        "velocity_range": (0.0, 0.0),
        "asset_cfg": SceneEntityCfg("robot", joint_names=(".*",)),
      },
    ),
    "hold_passive": EventTermCfg(
      func=mdp.set_joint_position_targets_to_default,
      mode="reset",
      params={
        "asset_cfg": SceneEntityCfg("robot", joint_names=_K1_PASSIVE_JOINTS),
      },
    ),
    "foot_friction": EventTermCfg(
      mode="startup",
      func=dr.geom_friction,
      params={
        "asset_cfg": SceneEntityCfg("robot", geom_names=_K1_FOOT_FRICTION_GEOMS),
        "operation": "abs",
        # High grip kills the "splits then squeeze" exploit; keep a band for DR.
        "ranges": (0.9, 1.5),
      },
    ),
  }

  curriculum = {
    "speed_pressure": CurriculumTermCfg(
      func=mdp.speed_pressure_curriculum,
      params={
        "term_name": "time_penalty",
        "start_weight": -0.3,
        "end_weight": -5.0,
        "start_step": 8_000,
        "end_step": 50_000,
      },
    ),
  }

  cfg = ManagerBasedRlEnvCfg(
    scene=SceneCfg(
      terrain=TerrainEntityCfg(terrain_type="plane"),
      entities={"robot": _getup_robot_cfg()},
      num_envs=1,
      extent=2.0,
    ),
    observations=observations,
    actions=actions,
    events=events,
    rewards=rewards,
    terminations=terminations,
    curriculum={} if play else curriculum,
    viewer=ViewerConfig(
      origin_type=ViewerConfig.OriginType.ASSET_BODY,
      entity_name="robot",
      body_name="Trunk",
      distance=3.0,
      elevation=-5.0,
      azimuth=90.0,
    ),
    sim=SimulationCfg(
      nconmax=70,
      njmax=1500,
      contact_sensor_maxmatch=500,
      mujoco=MujocoCfg(
        timestep=0.005,
        iterations=10,
        ls_iterations=20,
        ccd_iterations=500,
      ),
    ),
    decimation=4,
    episode_length_s=8.0 if not play else int(1e9),
  )

  if play:
    cfg.observations["actor"].enable_corruption = False

  return cfg

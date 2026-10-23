"""Environment config for B-Human's K1 kick (``K1_Ball.yaml``).

2 ms physics x 10 substeps (50 Hz policy), 59 actor / 16 privileged inputs,
13 actions, reward scales x dt. Values are the YAML's initial-stage ones;
``stages.py`` holds the later stages of B-Human's schedule.
"""

from __future__ import annotations

from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.managers.event_manager import EventTermCfg
from mjlab.managers.observation_manager import ObservationGroupCfg, ObservationTermCfg
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.termination_manager import TerminationTermCfg
from mjlab.scene import SceneCfg
from mjlab.sensor import ContactMatch, ContactSensorCfg
from mjlab.sim import MujocoCfg, SimulationCfg
from mjlab.tasks.bhuman_kick import mdp
from mjlab.tasks.bhuman_kick.kick_command import BHumanKickCommandCfg
from mjlab.tasks.bhuman_kick.robot import FEET, get_bhuman_ball_cfg, get_bhuman_k1_cfg
from mjlab.tasks.bhuman_kick.terrain import bhuman_field_generator_cfg
from mjlab.terrains import TerrainEntityCfg
from mjlab.viewer import ViewerConfig

# rewards.scales of K1_Ball.yaml (initial stage). Zero entries are B-Human
# terms switched on by later stages.
REWARD_SCALES: dict[str, float] = {
  "terminate": -100.0,
  "base_height": -40.0,
  "orientation": -5.0,
  "torques": -2.0e-4,
  "torque_tiredness": -1.0e-2,
  "power": -2.0e-3,
  "lin_vel_z": -2.0,
  "ang_vel_xy": -0.2,
  "dof_vel": -1.0e-4,
  "dof_acc": -1.0e-7,
  "root_acc": -1.0e-4,
  "action_rate": -1.0,
  "dof_pos_limits": -1.0,
  "actions_in_range": -1.0,
  "action_pos_limits": -1.0,
  "torque_limits": -0.01,
  "collision": -1.0,
  "feet_slip": -0.1,
  "feet_yaw_diff": -0.25,
  "feet_yaw_mean": -0.25,
  "feet_roll": -0.1,
  "feet_swing": 3.0,
  "feet_distance": -0.25,
  "ground_pressure": -0.1,
  "gait_phase_factor": -0.1,
  "feet_height": -0.25,
  "ball_kick_velocity": 4.0,
  "ball_kick_velocity_strong": 5.0,
  "ball_kick_direction": 10.0,
  "ball_walk_speed": 2.0,
  "ball_sole_yaw": 0.0,
  "ball_walk_target_overshoot": -100.0,
}


def bhuman_kick_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  command = BHumanKickCommandCfg(debug_vis=play)
  if play:
    terrain = TerrainEntityCfg(terrain_type="plane")
  else:
    terrain = TerrainEntityCfg(
      terrain_type="generator", terrain_generator=bhuman_field_generator_cfg()
    )

  body_contact = ContactSensorCfg(
    name="body_contact",
    primary=ContactMatch(mode="body", pattern=".*", entity="robot", exclude=FEET),
    fields=("force",),
    reduce="netforce",
  )

  return ManagerBasedRlEnvCfg(
    scene=SceneCfg(
      terrain=terrain,
      entities={"robot": get_bhuman_k1_cfg(), "ball": get_bhuman_ball_cfg()},
      sensors=(body_contact,),
      num_envs=1,
      env_spacing=0.0,
    ),
    observations={
      "actor": ObservationGroupCfg({"bhuman": ObservationTermCfg(func=mdp.actor_obs)}),
      "critic": ObservationGroupCfg(
        {"privileged": ObservationTermCfg(func=mdp.critic_obs)}
      ),
    },
    actions={"legs": mdp.BHumanKickActionCfg()},
    commands={"kick": command},
    events={
      "body": EventTermCfg(func=mdp.bhuman_body_dr, mode="startup"),
      "feet": EventTermCfg(func=mdp.bhuman_feet_dr, mode="startup"),
      "ball": EventTermCfg(func=mdp.bhuman_ball_dr, mode="startup"),
      "joint_friction": EventTermCfg(func=mdp.bhuman_joint_friction, mode="startup"),
    },
    rewards={
      name: RewardTermCfg(func=getattr(mdp, name), weight=w)
      for name, w in REWARD_SCALES.items()
    },
    terminations={
      "terminated": TerminationTermCfg(func=mdp.terminated),
      "time_out": TerminationTermCfg(func=mdp.time_out, time_out=True),
    },
    viewer=ViewerConfig(
      origin_type=ViewerConfig.OriginType.ASSET_ROOT,
      entity_name="robot",
      distance=3.0,
      elevation=-20.0,
      azimuth=135.0,
    ),
    sim=SimulationCfg(
      nconmax=64,
      njmax=600,
      mujoco=MujocoCfg(timestep=0.002, iterations=10, ls_iterations=20),
    ),
    decimation=10,
    # Episodes end through the kick command (30 s after the last ball reset,
    # or after episode_number_of_kicks kicks); this is only a backstop.
    episode_length_s=1.0e5,
  )

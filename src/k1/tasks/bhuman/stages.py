"""B-Human's staged kick training (``envs/readme.md``, "Training kick").

Each stage applies its changes on top of all earlier ones. Train a stage,
then start the next from its checkpoint (``--agent.resume`` with the same
experiment, or ``--agent.bhuman-checkpoint <model.pt>``). Their advice: move
on only once strong and scaled kicks are both somewhat accurate; the later
stages mostly polish accuracy.

Steps the readme does gradually (``target_sole_yaw_sigma`` down to 0.1,
``kick_direction_sigma_range`` 0.25 -> 0.05) take the first value here; go
further with CLI overrides, e.g.
``--env.commands.kick.kick-direction-sigma-range 0.1``.
"""

from __future__ import annotations

from collections.abc import Callable

from k1.tasks.bhuman.kick_command import BHumanKickCommandCfg
from k1.tasks.bhuman.runner import BHumanPpoRunnerCfg
from mjlab.envs import ManagerBasedRlEnvCfg

Stage = Callable[[ManagerBasedRlEnvCfg, BHumanPpoRunnerCfg], None]


def _kick(cfg: ManagerBasedRlEnvCfg) -> BHumanKickCommandCfg:
  kick = cfg.commands["kick"]
  assert isinstance(kick, BHumanKickCommandCfg)
  return kick


def _w(cfg: ManagerBasedRlEnvCfg, **weights: float) -> None:
  for name, w in weights.items():
    cfg.rewards[name].weight = w


def stage2(cfg: ManagerBasedRlEnvCfg, rl: BHumanPpoRunnerCfg) -> None:
  k = _kick(cfg)
  k.target_sole_yaw_angle = 1.5705
  k.disable_sole_yaw_direction_penalty = True
  k.disable_deviation_flag = False
  k.ball_pos_noise_x = (0.03, k.ball_pos_noise_x[1])
  k.ball_pos_noise_y = (0.03, k.ball_pos_noise_y[1])
  _w(cfg, ball_sole_yaw=25.0)


def stage3a(cfg: ManagerBasedRlEnvCfg, rl: BHumanPpoRunnerCfg) -> None:
  _kick(cfg).target_sole_yaw_sigma = 0.1
  _w(cfg, ball_walk_speed=1.0, ball_sole_yaw=15.0)
  rl.algorithm.entropy_range = (-15.0, -14.0)
  rl.algorithm.learning_rate_range = (1.0e-5, rl.algorithm.learning_rate_range[1])


def stage3b(cfg: ManagerBasedRlEnvCfg, rl: BHumanPpoRunnerCfg) -> None:
  k = _kick(cfg)
  k.disable_sole_yaw_direction_penalty = False
  k.kick_direction_negative_factor = 3.0
  _w(cfg, ball_sole_yaw=5.0, ball_walk_target_overshoot=-10.0, feet_swing=0.75)


def stage4(cfg: ManagerBasedRlEnvCfg, rl: BHumanPpoRunnerCfg) -> None:
  k = _kick(cfg)
  k.kick_direction_sigma_range = 0.75
  k.kick_direction_sigma_just_hit = 0.5


def stage5(cfg: ManagerBasedRlEnvCfg, rl: BHumanPpoRunnerCfg) -> None:
  k = _kick(cfg)
  k.kick_direction_sigma_range = 0.25
  k.random_ball_distance_reset = 0.0005
  _w(cfg, ball_sole_yaw=0.0, ball_walk_speed=1.0)
  rl.algorithm.desired_kl = 0.003
  rl.algorithm.entropy_range = (-16.6, -16.5)


def _robustness(cfg: ManagerBasedRlEnvCfg, f: float) -> None:
  """Stage 6 event probabilities at fraction ``f`` of their final values."""
  k = _kick(cfg)
  k.random_ball_reset = (0.01 * f, 0.02 * f, 0.02 * f)
  k.reset_ball_request = 0.005 * f
  k.add_ball_vel = 1.0e-4 * f
  k.add_ball_vel_in_direction = 1.0e-4 * f
  k.heavy_ball = 1.0e-5 if f < 1.0 else 1.0e-4


def stage6a(cfg: ManagerBasedRlEnvCfg, rl: BHumanPpoRunnerCfg) -> None:
  _robustness(cfg, 0.1)
  _w(cfg, ball_kick_direction=5.0, ball_walk_speed=0.75)


def stage6(cfg: ManagerBasedRlEnvCfg, rl: BHumanPpoRunnerCfg) -> None:
  """Final values; B-Human runs these for only a few hundred iterations."""
  _robustness(cfg, 1.0)
  k = _kick(cfg)
  k.kick_pose_increase_value = 0.2
  k.ball_distance_offset = 0.7
  k.ball_rotation_offset = 0.2


STAGES: dict[str, list[Stage]] = {
  "Stage1": [],
  "Stage2": [stage2],
  "Stage3a": [stage2, stage3a],
  "Stage3b": [stage2, stage3a, stage3b],
  "Stage4": [stage2, stage3a, stage3b, stage4],
  "Stage5": [stage2, stage3a, stage3b, stage4, stage5],
  "Stage6a": [stage2, stage3a, stage3b, stage4, stage5, stage6a],
  "Stage6": [stage2, stage3a, stage3b, stage4, stage5, stage6a, stage6],
}


def apply_stage(name: str, cfg: ManagerBasedRlEnvCfg, rl: BHumanPpoRunnerCfg) -> None:
  for stage in STAGES[name]:
    stage(cfg, rl)

"""Booster K1 dribble (with kick mode) env config."""

import math
import os

from k1.tasks.kick.env_cfg import (
  _APPROACH_BALL_MASS,
  K1_CAMERA_HALF_FOV,
  _clip_leg_torque,
  _deployment_match,
  booster_k1_kick_approach_env_cfg,
)
from k1.tasks.kick.mdp import approach as approach_mdp
from k1.tasks.velocity import mdp
from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.managers.event_manager import EventTermCfg
from mjlab.managers.observation_manager import ObservationGroupCfg, ObservationTermCfg
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.managers.termination_manager import TerminationTermCfg


def booster_k1_dribble_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Stage-2 closed-loop ball dribbling task built on the approach layout."""
  cfg = booster_k1_kick_approach_env_cfg(play=play)
  assert cfg.commands is not None
  assert cfg.terminations is not None
  cfg.commands["twist"] = mdp.DribbleCommandCfg(
    debug_vis=play,
    fov_half_angle=K1_CAMERA_HALF_FOV[0],
    fov_vertical_half_angle=K1_CAMERA_HALF_FOV[1],
    ball_distance_range=(0.4, 2.0),
    spawn_any_prob=0.20 if not play else 0.0,
    unknown_start_prob=0.15 if not play else 0.0,
    speed_curriculum=not play,
    # v14: resume at v13's 1.3 and run past the 1.5 m/s target, so 1.5 sits
    # inside the oversampled top band [hi - 0.2, hi] at the end.
    speed_hi_start=1.5,
    # v15c: capped at the 1.5 m/s target. v15b reached 1.5 at ~12200 and then
    # slowed at every commanded speed (1.0 m/s success 0.56 -> 0.38 by 13000).
    speed_hi_max=1.5,
    speed_band_success=0.12,
    speed_low_min_success=0.06,
    speed_gate_post_touch=True,
    speed_gate_relative=True,
    speed_low_band=(0.2, 0.4),
    # v15c: 0.5 -> 0.25, so mid speeds keep their share of training.
    top_band_prob=0.25 if not play else 0.0,
    amp_style_weight=0.25,
    # v15 (2026-10-19, user): unseen-ball memory turned by IMU yaw only, as the
    # robot runner does (no odometry). v14 lost 2-5 points of success and
    # doubled falls when evaluated this way untrained.
    memory_odometry=False,
    # v15: fast commands (>= 0.9 m/s) get 6-8 s windows and turn at most 60
    # degrees once the ball is under control, so speed gets practised.
    fast_window_s=None if play else (6.0, 8.0),
    fast_turn_half_angle=math.pi if play else math.pi / 3.0,
  )
  if not play:
    cfg.terminations["ball_lost"] = TerminationTermCfg(
      func=mdp.dribble_ball_lost, params={"grace_s": 2.0}
    )
  mdp.apply_dribble_rewards(cfg)
  # v17 (2026-10-20, user: no tiptoe walking, it loads the ankles): the kick's
  # flat stance-foot term (booster_k1_kick_stage3_env_cfg "foot_flat"). On
  # robot #291 the v15 dribble had the lower foot > 10 deg toe-down 15 % of the
  # time (0-3 % in the runner sim); in sim 24-31 % of loaded steps were on the
  # toe only, the AMP walk 27 %. Light on purpose (user): the target is a flat
  # stance like the AMP walk (70-80 % of loaded steps), not a sole slapped
  # down. The kick used -200; there -30 already cut heel-up from 34 % to ~22 %.
  cfg.rewards["foot_flat"] = RewardTermCfg(
    func=mdp.htwk_feet_orientation_contact_gated,
    weight=-30.0,
    params={
      "axis": 1,
      "sensor_name": "feet_ground_contact",
      "asset_cfg": SceneEntityCfg(
        "robot", body_names=("left_foot_link", "right_foot_link")
      ),
      "settle_s": 0.06,
    },
  )
  if DRIBBLE_DEPLOY_MATCH:
    _dribble_deploy_match(cfg, play)
  if mdp.DRIBBLE_GENES.get("push_chase"):
    # v21 (2026-10-20, user: push the ball 1-2 m ahead, sprint after it, touch
    # it again, and find the top speed). Reward envelopes widen in
    # dribble_rewards; here the window success distance (1 -> 2 m at fast
    # commands), the lost-ball distance and the speed curriculum ceiling.
    twist = cfg.commands["twist"]
    twist.push_dist_extra = 1.0
    twist.lost_ball_dist = 3.5
    twist.speed_hi_max = 2.0
  genes = mdp.DRIBBLE_GENES
  if any(k in genes for k in ("kick_prob", "vanish_prob", "far_spawn_prob")):
    # v22 (2026-10-20, user, for the real robot): approach from up to 8 m, a
    # ball that disappears and must be searched for, and the slot-82 kick
    # mode (one straight kick along slots 78-79, then stand). The ball-lost
    # termination skips far spawns, replaced balls and kick windows.
    twist = cfg.commands["twist"]
    twist.kick_prob = float(genes.get("kick_prob", 0.0))
    twist.vanish_prob = float(genes.get("vanish_prob", 0.0))
    twist.far_spawn_prob = float(genes.get("far_spawn_prob", 0.0))
    twist.far_spawn_range = (2.0, 8.0)
    twist.lost_needs_touch = True
  # v27 (2026-10-21, user: faster push-and-chase, less style, B-Human side kick).
  twist = cfg.commands["twist"]
  if "speed_gate_frac" in genes:
    twist.speed_gate_achieved_frac = float(genes["speed_gate_frac"])
  if "top_band_prob" in genes and not play:
    twist.top_band_prob = float(genes["top_band_prob"])
  if "fast_turn_deg" in genes and not play:
    twist.fast_turn_half_angle = math.radians(float(genes["fast_turn_deg"]))
  if genes.get("kick_air_ok"):
    twist.kick_air_ok = True
  if "kick_leave_dist" in genes:
    twist.kick_leave_dist = float(genes["kick_leave_dist"])
  if "sole_yaw_sigma" in genes:
    twist.sole_yaw_sigma = float(genes["sole_yaw_sigma"])
  if "style_w" in genes:
    twist.amp_style_weight = float(genes["style_w"])
  play_mode = os.environ.get("DRIBBLE_PLAY", "")
  if play and play_mode:
    # Viewer only (2026-10-21, user): every window is one behaviour. stop =
    # stop the ball and stay beside it; dribble = move it at
    # DRIBBLE_PLAY_SPEED (m/s, default 0.5); kick = one straight kick within
    # DRIBBLE_PLAY_KICK_DEG of the robot-to-ball bearing, then stand (v24+).
    assert play_mode in ("stop", "dribble", "kick"), play_mode
    twist = cfg.commands["twist"]
    twist.stop_prob = 1.0 if play_mode == "stop" else 0.0
    twist.kick_prob = 1.0 if play_mode == "kick" else 0.0
    twist.vanish_prob = 0.0
    speed = float(os.environ.get("DRIBBLE_PLAY_SPEED", "0.5"))
    twist.speed_curriculum = False
    twist.ball_speed_range = (speed, speed)
    twist.kick_half_angle = math.radians(
      float(os.environ.get("DRIBBLE_PLAY_KICK_DEG", "30"))
    )
    twist.kick_min_angle = math.radians(
      float(os.environ.get("DRIBBLE_PLAY_KICK_MIN_DEG", "0"))
    )
  if mdp.DRIBBLE_GENES.get("amp_cond"):
    # v20: the discriminator also sees the commanded ball velocity (rl_cfg
    # adds the group to the AMP runner); not part of the actor or critic.
    cfg.observations["amp_cond"] = ObservationGroupCfg(
      terms={"cond": ObservationTermCfg(func=mdp.amp_dribble_cond)},
      concatenate_terms=True,
      enable_corruption=False,
    )
  return cfg


# Deploy match (2026-10-19, user): train the dribble on the robot path. Up to
# swa_v15 it had no joint-target clip, motor-rating torques, a ball seen every
# step with no delay, noise or jitter, and steady commands.
DRIBBLE_DEPLOY_MATCH = True


def _dribble_deploy_match(cfg: ManagerBasedRlEnvCfg, play: bool) -> None:
  """Runner joint clip, motor delay 0-40 ms and the kick's leg torque clip;
  vision as on the robot (~16 Hz frames held, 20-80 ms latency, 5 % missed
  detections, range-scaled noise, ball measured from between the feet with
  2 cm jitter); the kick's ball size / mass / friction / bounce DR; and in
  training, 30 % of commands turning slowly (+-0.6 rad/s) as a joystick would."""
  _deployment_match(cfg)
  _clip_leg_torque(cfg)
  assert cfg.commands is not None
  twist = cfg.commands["twist"]
  twist.vision_hold_steps = (2, 4)
  twist.vision_delay_steps = (1, 4)
  twist.vision_dropout = 0.05
  twist.ball_obs_noise = (0.03, 0.05)
  twist.ball_origin = "feet"
  twist.ball_origin_jitter = 0.02
  if not play:
    twist.cmd_drift_prob = 0.3
    twist.cmd_drift_max = 0.6
  # The stage-3 kick's ball DR (booster_k1_kick_stage3_env_cfg): the dribble
  # had one 0.1 kg ball, real balls are 0.29-0.43 kg. In the MuJoCo runner
  # (0.29 kg ball) swa_v15 dribbled 0.3-0.4 m/s faster than commanded.
  cfg.events["ball_mass"] = EventTermCfg(
    mode="reset",
    func=mdp.ball_size_mass,
    params={
      "radius_range": approach_mdp.BALL_RADIUS_RANGE,
      "alpha_range": approach_mdp.BALL_ALPHA_RANGE,
      "nominal_mass": _APPROACH_BALL_MASS,
      "geom_cfg": SceneEntityCfg("ball", geom_names=("ball_collision",)),
      "body_cfg": SceneEntityCfg("ball", body_names=("ball",)),
    },
  )
  cfg.events["ball_friction"] = EventTermCfg(
    mode="reset",
    func=mdp.dr.geom_friction,
    params={
      "asset_cfg": SceneEntityCfg("ball", geom_names=("ball_collision",)),
      "operation": "scale",
      "ranges": {0: (0.6, 1.4), 2: (0.5, 2.5)},
      "axes": [0, 2],
    },
  )
  cfg.events["ball_bounce"] = EventTermCfg(
    mode="reset",
    func=mdp.dr.geom_solref,
    params={
      "asset_cfg": SceneEntityCfg("ball", geom_names=("ball_collision",)),
      "operation": "abs",
      "ranges": {0: (0.03, 0.08), 1: (0.08, 0.4)},
      "axes": [0, 1],
    },
  )

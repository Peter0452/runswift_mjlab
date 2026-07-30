"""Approach task: walk to the ball and reach the kick zone.

Stage 1 of the two-stage soccer pipeline.  Built on top of the flat velocity
task so the locomotion interface (observations, actions, commands) is
identical — a checkpoint from ``Mjlab-Velocity-Flat-Booster-K1`` can be
loaded directly to warm-start training.

The ball is placed at a random position in the env.  The robot receives:
  - the standard locomotion observations (joint pos/vel, IMU, gait clock, …)
  - ``ball_rel_pos``: ball position in body frame [3]

Rewards:
  - All standard locomotion rewards (upright, pose, action rate, …)
  - ``ball_approach``: Gaussian on robot–ball distance (pulls toward ball)
  - ``kick_zone``: bonus for reaching the kick zone in correct alignment

The velocity command (``twist``) is kept but its weight is reduced; the
approach reward dominates navigation.  On reaching the kick zone the policy
will naturally slow down since the ``ball_in_kick_zone`` reward peaks there.
"""


from mjlab.entity import EntityCfg
from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.managers.event_manager import EventTermCfg
from mjlab.managers.observation_manager import ObservationTermCfg
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.tasks.kick import mdp as kick_mdp
from mjlab.tasks.kick.mdp.events import reset_ball_uniform


def make_approach_env_cfg(base_cfg: ManagerBasedRlEnvCfg) -> ManagerBasedRlEnvCfg:
  """Add the ball entity and approach rewards to a flat-terrain velocity cfg.

  Args:
    base_cfg: A fully-constructed flat K1 velocity env config (call
      ``booster_k1_flat_env_cfg()`` then pass the result here).

  Returns:
    The modified config.  The caller should use this as the registered env cfg.
  """
  from mjlab.asset_zoo.props import get_ball_spec

  # ── Scene: add the ball ──────────────────────────────────────────────────
  base_cfg.scene.entities["ball"] = EntityCfg(spec_fn=get_ball_spec)

  # ── Observations: ball relative position ────────────────────────────────
  ball_obs = ObservationTermCfg(
    func=kick_mdp.ball_relative_position,
    params={
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
      "clip_distance": 5.0,
    },
  )
  base_cfg.observations["actor"].terms["ball_rel_pos"] = ball_obs
  base_cfg.observations["critic"].terms["ball_rel_pos"] = ball_obs

  # ── Events: reset ball to random position each episode ──────────────────
  base_cfg.events["reset_ball"] = EventTermCfg(
    func=reset_ball_uniform,
    mode="reset",
    params={
      "pose_range": {
        "x": (-2.0, 2.0),
        "y": (-2.0, 2.0),
        "z": (0.11, 0.11),  # ball resting on flat terrain
      },
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )

  # ── Rewards ──────────────────────────────────────────────────────────────

  # Reduce velocity-tracking weight: navigation is driven by ball approach.
  base_cfg.rewards["track_linear_velocity"].weight = 0.5
  base_cfg.rewards["track_angular_velocity"].weight = 0.5

  # Pull the robot toward the ball (std = 1.5 m → broad, always active).
  base_cfg.rewards["ball_approach"] = RewardTermCfg(
    func=kick_mdp.ball_approach_reward,
    weight=3.0,
    params={
      "std": 1.5,
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )

  # Bonus for achieving the correct approach pose.
  base_cfg.rewards["kick_zone"] = RewardTermCfg(
    func=kick_mdp.ball_in_kick_zone,
    weight=2.0,
    params={
      "kick_distance": 0.35,
      "lateral_half_width": 0.12,
      "distance_std": 0.08,
      "robot_cfg": SceneEntityCfg("robot"),
      "ball_cfg": SceneEntityCfg("ball"),
    },
  )

  # nconmax must account for ball contacts.
  if base_cfg.sim.nconmax is not None:
    base_cfg.sim.nconmax = max(base_cfg.sim.nconmax, base_cfg.sim.nconmax + 20)

  return base_cfg

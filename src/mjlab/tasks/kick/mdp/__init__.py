from .commands import UniformGoalPositionCommand, UniformGoalPositionCommandCfg
from .curriculums import approach_spawn_radius_curriculum
from .events import (
  reset_ball_relative_to_robot,
  reset_ball_uniform,
  reset_robot_around_ball_facing,
  update_approach_twist_command,
)
from .observations import ball_relative_position, ball_to_goal_direction, goal_direction
from .rewards import (
  ball_approach_far,
  ball_approach_reward,
  ball_camera_cone,
  ball_distance_band,
  ball_goal_proximity,
  ball_in_kick_zone,
  ball_velocity_toward_goal,
  behind_ball_waypoint,
  body_face_ball,
  kick_ready,
  trunk_orientation_l2,
  waypoint_approach_velocity,
  waypoint_retreat_penalty,
)

__all__ = [
  "UniformGoalPositionCommand",
  "UniformGoalPositionCommandCfg",
  "reset_ball_uniform",
  "reset_ball_relative_to_robot",
  "reset_robot_around_ball_facing",
  "update_approach_twist_command",
  "ball_relative_position",
  "goal_direction",
  "ball_to_goal_direction",
  "ball_approach_reward",
  "ball_approach_far",
  "approach_spawn_radius_curriculum",
  "ball_distance_band",
  "behind_ball_waypoint",
  "body_face_ball",
  "ball_camera_cone",
  "kick_ready",
  "trunk_orientation_l2",
  "waypoint_approach_velocity",
  "waypoint_retreat_penalty",
  "ball_in_kick_zone",
  "ball_velocity_toward_goal",
  "ball_goal_proximity",
]

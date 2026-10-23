"""Old home of the K1 AMP env configs, now split by family (walk, kick,
dribble). Re-exports every name so existing imports keep working.
"""

from k1.tasks.dribble.env_cfg import (  # noqa: F401
  DRIBBLE_DEPLOY_MATCH,
  _dribble_deploy_match,
  booster_k1_dribble_env_cfg,
)
from k1.tasks.kick.env_cfg import (  # noqa: F401
  _APPROACH_BALL_FRICTION,
  _APPROACH_BALL_MASS,
  _APPROACH_BALL_RADIUS,
  _FOOT_CAPSULES,
  _HANDOFF_LATE_VEL,
  _HANDOFF_VEL_WIDEN_STEP,
  _KICK_STAGE1_CRITIC_TAIL,
  _KICK_STAGE1_VEL_STAGES,
  DEPLOY_Q_LIMITS,
  K1_CAMERA_HALF_FOV,
  KICK_GENES,
  KICK_STYLE_WEIGHT,
  LEG_TORQUE_CLIP,
  TOUCHDOWN_SPEED_WEIGHT,
  _append_kick_stage1_command_slots,
  _capsule_foot_spec,
  _clip_leg_torque,
  _configure_approach_observations,
  _deployment_match,
  _free_head_posture,
  _get_approach_ball_spec,
  _use_foot_capsules,
  booster_k1_amp_kick_handoff_env_cfg,
  booster_k1_kick_approach_env_cfg,
  booster_k1_kick_stage1_env_cfg,
  booster_k1_kick_stage3_env_cfg,
  with_stand_start,
)
from k1.tasks.walk.env_cfg import (  # noqa: F401
  _AMP_EARLY_VEL,
  _AMP_MAX_VEL,
  _AMP_ROUGH_FT_MIX,
  _AMP_VEL_WIDEN_STEP,
  _apply_amp_max_vel_curriculum,
  _apply_amp_rough_ft_terrain,
  booster_k1_amp_flat_env_cfg,
  booster_k1_amp_rough_env_cfg,
  booster_k1_amp_rough_ft_env_cfg,
)

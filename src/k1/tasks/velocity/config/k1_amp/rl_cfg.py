"""Old home of the K1 AMP runner configs, now split by family (walk, kick,
dribble). Re-exports every name so existing imports keep working.
"""

from k1.tasks.dribble.rl_cfg import (  # noqa: F401
  _AMP_DRIBBLE_FAST_MIX_WEIGHTS,
  _AMP_DRIBBLE_MIX_DIR,
  _AMP_DRIBBLE_MIX_WEIGHTS,
  DRIBBLE_LR,
  DRIBBLE_MAX_ACTION_STD,
  booster_k1_dribble_runner_cfg,
)
from k1.tasks.kick.rl_cfg import (  # noqa: F401
  _AMP_KICK_MIX_DIR,
  _AMP_KICK_MIX_WEIGHTS,
  _KICK_TEACHER_CKPT,
  KICK_MAX_ACTION_STD,
  KICK_STYLE_AMP_DATA,
  booster_k1_amp_kick_handoff_runner_cfg,
  booster_k1_kick_approach_runner_cfg,
  booster_k1_kick_stage1_runner_cfg,
  booster_k1_kick_stage3_runner_cfg,
)
from k1.tasks.walk.rl_cfg import (  # noqa: F401
  _AMP_MIX_DIR,
  _AMP_MIX_WEIGHTS_FILE,
  _AMP_SYMMETRY_CFG,
  _amp_mix_dataset,
  booster_k1_amp_ppo_runner_cfg,
  booster_k1_amp_ppo_symmetric_runner_cfg,
)

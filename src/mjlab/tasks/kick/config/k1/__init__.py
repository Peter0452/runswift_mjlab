from mjlab.rl.runner import MjlabOnPolicyRunner
from mjlab.tasks.registry import register_mjlab_task

from .env_cfgs import k1_approach_env_cfg, k1_score_env_cfg
from .rl_cfg import k1_approach_ppo_runner_cfg, k1_score_ppo_runner_cfg

register_mjlab_task(
  task_id="Mjlab-Kick-Approach-Booster-K1",
  env_cfg=k1_approach_env_cfg(),
  play_env_cfg=k1_approach_env_cfg(play=True),
  rl_cfg=k1_approach_ppo_runner_cfg(),
  runner_cls=MjlabOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Kick-Score-Booster-K1",
  env_cfg=k1_score_env_cfg(),
  play_env_cfg=k1_score_env_cfg(play=True),
  rl_cfg=k1_score_ppo_runner_cfg(),
  runner_cls=MjlabOnPolicyRunner,
)

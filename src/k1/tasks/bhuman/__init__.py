"""B-Human's K1 kick training pipeline (Booster Gym / Isaac Gym), ported.

Tasks ``Mjlab-BHuman-Kick-<Stage>-Booster-K1`` follow B-Human's staged
schedule (``stages.py``); ``Mjlab-BHuman-Kick-Booster-K1`` is stage 1.
"""

from k1.tasks.bhuman.env_cfg import bhuman_kick_env_cfg
from k1.tasks.bhuman.runner import BHumanPpoRunner, BHumanPpoRunnerCfg
from k1.tasks.bhuman.stages import STAGES, apply_stage
from mjlab.tasks.registry import register_mjlab_task


def _register(task_id: str, stage: str) -> None:
  env_cfg = bhuman_kick_env_cfg()
  play_cfg = bhuman_kick_env_cfg(play=True)
  rl_cfg = BHumanPpoRunnerCfg(run_name=stage.lower())
  apply_stage(stage, env_cfg, rl_cfg)
  apply_stage(stage, play_cfg, BHumanPpoRunnerCfg())
  register_mjlab_task(
    task_id=task_id,
    env_cfg=env_cfg,
    play_env_cfg=play_cfg,
    rl_cfg=rl_cfg,
    runner_cls=BHumanPpoRunner,
  )


_register("Mjlab-BHuman-Kick-Booster-K1", "Stage1")
for _stage in STAGES:
  _register(f"Mjlab-BHuman-Kick-{_stage}-Booster-K1", _stage)

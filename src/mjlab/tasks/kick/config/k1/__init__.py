from mjlab.rl.runner import MjlabOnPolicyRunner
from mjlab.tasks.registry import register_mjlab_task
from mjlab.tasks.velocity.rl.amp_runner import VelocityAmpOnPolicyRunner

from .amp_rl_cfg import k1_kick_near_amp_ppo_runner_cfg
from .env_cfgs import (
  k1_arc_kick_env_cfg,
  k1_kick_approach_env_cfg,
  k1_kick_near_amp_env_cfg,
  k1_kick_near_env_cfg,
  k1_kick_walkamp_amp_env_cfg,
  k1_kick_walkamp_env_cfg,
)
from .rl_cfg import (
  k1_arc_kick_ppo_runner_cfg,
  k1_kick_approach_ppo_runner_cfg,
  k1_kick_near_ppo_runner_cfg,
)
from .walkamp_rl_cfg import (
  k1_kick_walkamp_amp_ppo_runner_cfg,
  k1_kick_walkamp_ppo_runner_cfg,
)

# Unified Arc → Setup → Strike kick (replaces Chase / Approach / Strike / Score).
register_mjlab_task(
  task_id="Mjlab-Kick-Booster-K1",
  env_cfg=k1_arc_kick_env_cfg(),
  play_env_cfg=k1_arc_kick_env_cfg(play=True),
  rl_cfg=k1_arc_kick_ppo_runner_cfg(),
  runner_cls=MjlabOnPolicyRunner,
)

# Stage-1: approach / face ball only (warm-start before full kick).
register_mjlab_task(
  task_id="Mjlab-Kick-Approach-Booster-K1",
  env_cfg=k1_kick_approach_env_cfg(),
  play_env_cfg=k1_kick_approach_env_cfg(play=True),
  rl_cfg=k1_kick_approach_ppo_runner_cfg(),
  runner_cls=MjlabOnPolicyRunner,
)

# Stage-2: near-ball kick discovery (kick hard, no dribble).
register_mjlab_task(
  task_id="Mjlab-Kick-Near-Booster-K1",
  env_cfg=k1_kick_near_env_cfg(),
  play_env_cfg=k1_kick_near_env_cfg(play=True),
  rl_cfg=k1_kick_near_ppo_runner_cfg(),
  runner_cls=MjlabOnPolicyRunner,
)

# Stage-2 + kick AMP: style on until kick_detected, then off for settle.
register_mjlab_task(
  task_id="Mjlab-Kick-Near-Amp-Booster-K1",
  env_cfg=k1_kick_near_amp_env_cfg(),
  play_env_cfg=k1_kick_near_amp_env_cfg(play=True),
  rl_cfg=k1_kick_near_amp_ppo_runner_cfg(),
  runner_cls=VelocityAmpOnPolicyRunner,
)

# Kick-on-Walk-AMP (78/95): thesis rewards/terms on Flat AMP Walk.
register_mjlab_task(
  task_id="Mjlab-Kick-WalkAmp-Booster-K1",
  env_cfg=k1_kick_walkamp_env_cfg(),
  play_env_cfg=k1_kick_walkamp_env_cfg(play=True),
  rl_cfg=k1_kick_walkamp_ppo_runner_cfg(),
  runner_cls=MjlabOnPolicyRunner,
)

# Same env, Muon + left/right DA, no AMP style/discriminator.
register_mjlab_task(
  task_id="Mjlab-Kick-WalkAmp-DA-Muon-Booster-K1",
  env_cfg=k1_kick_walkamp_env_cfg(),
  play_env_cfg=k1_kick_walkamp_env_cfg(play=True),
  rl_cfg=k1_kick_walkamp_ppo_runner_cfg(use_muon=True, use_symmetry=True),
  runner_cls=MjlabOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Kick-WalkAmp-Amp-Booster-K1",
  env_cfg=k1_kick_walkamp_amp_env_cfg(),
  play_env_cfg=k1_kick_walkamp_amp_env_cfg(play=True),
  rl_cfg=k1_kick_walkamp_amp_ppo_runner_cfg(),
  runner_cls=VelocityAmpOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Kick-WalkAmp-Amp-DA-Muon-Booster-K1",
  env_cfg=k1_kick_walkamp_amp_env_cfg(),
  play_env_cfg=k1_kick_walkamp_amp_env_cfg(play=True),
  rl_cfg=k1_kick_walkamp_amp_ppo_runner_cfg(use_muon=True, use_symmetry=True),
  runner_cls=VelocityAmpOnPolicyRunner,
)

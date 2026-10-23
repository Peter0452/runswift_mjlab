from k1.tasks.velocity.config.k1_amp.amp_wrapper import with_amp_obs_group
from k1.tasks.velocity.rl.amp_runner import VelocityAmpOnPolicyRunner
from k1.tasks.velocity.rl.selfplay_runner import SelfPlayAmpOnPolicyRunner
from k1.tasks.velocity.rl.striker_runner import StrikerControllerRunner
from mjlab.tasks.registry import register_mjlab_task

from .env_cfgs import (
  KICK_STYLE_WEIGHT,
  booster_k1_amp_flat_env_cfg,
  booster_k1_amp_kick_handoff_env_cfg,
  booster_k1_amp_rough_ft_env_cfg,
  booster_k1_dribble_env_cfg,
  booster_k1_kick_approach_env_cfg,
  booster_k1_kick_stage1_env_cfg,
  booster_k1_kick_stage3_env_cfg,
  with_stand_start,
)
from .rl_cfg import (
  booster_k1_amp_kick_handoff_runner_cfg,
  booster_k1_amp_ppo_symmetric_runner_cfg,
  booster_k1_dribble_runner_cfg,
  booster_k1_kick_approach_runner_cfg,
  booster_k1_kick_stage1_runner_cfg,
  booster_k1_kick_stage3_runner_cfg,
)
from .selfplay_cfgs import (
  booster_k1_kick_selfplay_env_cfg,
  booster_k1_kick_selfplay_runner_cfg,
  booster_k1_striker_controller_env_cfg,
  booster_k1_striker_controller_runner_cfg,
)


def _with_amp_reset_cfg(env_cfg, runner_cfg):
  return with_amp_obs_group(
    env_cfg,
    dataset_root=runner_cfg.dataset_root,
    speed_factor=runner_cfg.speed_factor,
    dataset_weights=runner_cfg.dataset_weights,
    augmentations=runner_cfg.dataset_augmentations,
    include_base_lin_vel=True,
  )


_AMP_TASKS = {
  "Rough-Amp-DA": (
    booster_k1_amp_rough_ft_env_cfg,
    booster_k1_amp_ppo_symmetric_runner_cfg,
  ),
  "Flat-Amp-DA": (
    booster_k1_amp_flat_env_cfg,
    booster_k1_amp_ppo_symmetric_runner_cfg,
  ),
}

for name, (env_cfg_fn, rl_cfg_fn) in _AMP_TASKS.items():
  rl_cfg = rl_cfg_fn(use_muon=True)
  # Walk spring and two critics. Style is 0.2: at a 98% discriminator
  # accuracy the style advantage is saturated noise, and 0.5 of it was
  # washing out the tracking gradient.
  rl_cfg.decap = True
  rl_cfg.decap_source = "loader"
  rl_cfg.algorithm.multi_critic_alphas = (0.2, 0.8)
  register_mjlab_task(
    task_id=f"Mjlab-Velocity-{name}-Muon-Booster-K1",
    env_cfg=_with_amp_reset_cfg(env_cfg_fn(), rl_cfg),
    play_env_cfg=_with_amp_reset_cfg(env_cfg_fn(play=True), rl_cfg),
    rl_cfg=rl_cfg,
    runner_cls=VelocityAmpOnPolicyRunner,
  )

_approach_rl = booster_k1_kick_approach_runner_cfg()
register_mjlab_task(
  task_id="Mjlab-Velocity-Kick-Approach-Amp-DA-Muon-Booster-K1",
  env_cfg=_with_amp_reset_cfg(booster_k1_kick_approach_env_cfg(), _approach_rl),
  play_env_cfg=_with_amp_reset_cfg(
    booster_k1_kick_approach_env_cfg(play=True), _approach_rl
  ),
  rl_cfg=_approach_rl,
  runner_cls=VelocityAmpOnPolicyRunner,
)

_dribble_rl = booster_k1_dribble_runner_cfg()
register_mjlab_task(
  task_id="Mjlab-Velocity-Dribble-Amp-DA-Muon-Booster-K1",
  env_cfg=_with_amp_reset_cfg(booster_k1_dribble_env_cfg(), _dribble_rl),
  play_env_cfg=_with_amp_reset_cfg(booster_k1_dribble_env_cfg(play=True), _dribble_rl),
  rl_cfg=_dribble_rl,
  runner_cls=VelocityAmpOnPolicyRunner,
)


def _with_kick_style(env_cfg):
  """The AMP wrapper sets style weight 0.3; the kick stage sets its own."""
  style = env_cfg.curriculum["amp_style_weight"].params
  style["start_weight"] = style["end_weight"] = KICK_STYLE_WEIGHT
  return env_cfg


def _with_kick_prior_contact(env_cfg, rl_cfg):
  """No ball-touch cost when the kick-retarget prior places the ball."""
  if rl_cfg.decap and rl_cfg.decap_source == "kick":
    env_cfg.rewards["ball_avoidance"].weight = 0.0
  return env_cfg


_stage3_rl = booster_k1_kick_stage3_runner_cfg()
register_mjlab_task(
  task_id="Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1",
  env_cfg=with_stand_start(
    _with_kick_prior_contact(
      _with_kick_style(
        _with_amp_reset_cfg(booster_k1_kick_stage3_env_cfg(), _stage3_rl)
      ),
      _stage3_rl,
    )
  ),
  play_env_cfg=_with_kick_prior_contact(
    _with_kick_style(
      _with_amp_reset_cfg(booster_k1_kick_stage3_env_cfg(play=True), _stage3_rl)
    ),
    _stage3_rl,
  ),
  rl_cfg=_stage3_rl,
  runner_cls=VelocityAmpOnPolicyRunner,
)

# 1v1 self-play: stage 3 against a frozen opponent (mirror + snapshot pool).
_selfplay_rl = booster_k1_kick_selfplay_runner_cfg()
register_mjlab_task(
  task_id="Mjlab-Velocity-Kick-SelfPlay-Amp-DA-Muon-Booster-K1",
  env_cfg=with_stand_start(
    _with_kick_style(
      _with_amp_reset_cfg(booster_k1_kick_selfplay_env_cfg(), _selfplay_rl)
    )
  ),
  play_env_cfg=_with_kick_style(
    _with_amp_reset_cfg(booster_k1_kick_selfplay_env_cfg(play=True), _selfplay_rl)
  ),
  rl_cfg=_selfplay_rl,
  runner_cls=SelfPlayAmpOnPolicyRunner,
)

# Two-level striker: a controller over the frozen walk and kick skills, also
# trained by self-play (phase 1; the flat self-play task is phase 2).
register_mjlab_task(
  task_id="Mjlab-Velocity-Striker-Controller-Booster-K1",
  env_cfg=_with_amp_reset_cfg(booster_k1_striker_controller_env_cfg(), _stage3_rl),
  play_env_cfg=_with_amp_reset_cfg(
    booster_k1_striker_controller_env_cfg(play=True), _stage3_rl
  ),
  rl_cfg=booster_k1_striker_controller_runner_cfg(),
  runner_cls=StrikerControllerRunner,
)

_stage1_rl = booster_k1_kick_stage1_runner_cfg()
_stage1_rl.decap = True
_stage1_rl.decap_source = "loader"
_stage1_rl.algorithm.multi_critic_alphas = (0.2, 0.8)
register_mjlab_task(
  task_id="Mjlab-Velocity-Kick-Stage1-Amp-DA-Muon-Booster-K1",
  env_cfg=_with_amp_reset_cfg(booster_k1_kick_stage1_env_cfg(), _stage1_rl),
  play_env_cfg=_with_amp_reset_cfg(
    booster_k1_kick_stage1_env_cfg(play=True), _stage1_rl
  ),
  rl_cfg=_stage1_rl,
  runner_cls=VelocityAmpOnPolicyRunner,
)

_handoff_rl = booster_k1_amp_kick_handoff_runner_cfg()
register_mjlab_task(
  task_id="Mjlab-Velocity-Rough-Amp-DA-Muon-Booster-K1-KickHandoff",
  env_cfg=_with_amp_reset_cfg(booster_k1_amp_kick_handoff_env_cfg(), _handoff_rl),
  play_env_cfg=_with_amp_reset_cfg(
    booster_k1_amp_kick_handoff_env_cfg(play=True), _handoff_rl
  ),
  rl_cfg=_handoff_rl,
  runner_cls=VelocityAmpOnPolicyRunner,
)

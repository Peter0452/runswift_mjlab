---
id: amp
title: Adversarial motion priors (AMP-PPO)
element: reward
also:
- environment
tags:
- imitation
- style
status: adopted
impact: training-only
sources:
- peng2021_amp
registry: amp
---

# Adversarial motion priors (AMP-PPO)

**What.** PPO plus a motion discriminator on reference clips (WW + CMU walk mix; kick and dribble mixes add their own clips). The style reward is mixed with the task reward; with multi-critic it gets its own critic head.

**Source.** AMP (Peng et al. 2021); `src/mjlab/amp/` (runner, discriminator, AMP-PPO), wrapper `k1/tasks/velocity/config/k1_amp/amp_wrapper.py`.

**Where it plugs in.** Runner config (`AmpOnPolicyRunnerCfg`: `dataset_root`, `dataset_weights`, `style_reward_weight`, `num_amp_obs_steps`); env curriculum `amp_style_weight` (start/end weight; the kick stage sets its own via `with_kick_style`).

**Deployment impact.** Training-only (the discriminator and its observation group never run on the robot).

**Status.** adopted: every deployed model (gold walk, kick champion h022, dribble swaA_v15b, self-play swa_v15v16) was trained with it.

**Evidence.** Walk style weight 0.2 (98 % discriminator accuracy makes 0.5 saturated noise that washed out velocity tracking; skills/walk.md). R25: an unconditioned style prior copies the clips' posture. R26: turn style off near the ball / around the kick.

**Pitfalls.** Raising the style weight cuts task reward ((1−w)·task). A faster clip mix changes posture (dribble v19 leaned 16°). Loading a dribble v20+ checkpoint needs the run's `DRIBBLE_GENES` (discriminator size).

Registry entry: `k1/approaches/registry.py` (extension points, parameter fields, `detect`).
Uses: `knowledge/uses/uses.yaml`. Promotion rule and statuses: `knowledge/architecture.md`.

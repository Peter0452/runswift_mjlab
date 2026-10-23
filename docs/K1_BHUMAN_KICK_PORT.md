# B-Human K1 kick training pipeline in mjlab (2026-10-18)

Port of B-Human's kick training from `MachineLearning/IsaacGymRL` (Booster Gym on
Isaac Gym: `envs/t1_ball.py`, `envs/K1_Ball.yaml`, `utils/runner.py`,
`envs/readme.md`) into `src/mjlab/tasks/bhuman_kick/`. The goal is a faithful
reproduction (same inputs, outputs, rewards, randomization and PPO), so B-Human's
recipe can be trained, compared and mixed with ours on the same simulator.

## Use

```sh
# Stage 1 from B-Human's recommended start (a walk policy in kick-env format):
uv run train Mjlab-BHuman-Kick-Booster-K1 --env.scene.num-envs 4096 \
  --agent.bhuman-checkpoint ../MachineLearning/IsaacGymRL/pre-trained/WalkAndKick/K1_walk_start_for_kick.pth

# Next stage from the previous run's checkpoint:
uv run train Mjlab-BHuman-Kick-Stage2-Booster-K1 --agent.bhuman-checkpoint logs/rsl_rl/k1_bhuman_kick/<run>/model_<it>.pt

# Evaluate (B-Human's kick bookkeeping: launch speed, aim error, falls):
uv run python scripts/tools/eval_bhuman_kick.py --checkpoint <model.pt or .pth> [--task ...] [--flat] [--no-noise]

# Watch (plane, kick line red = strong / yellow = scaled, kick pose blue, walk target green):
uv run play Mjlab-BHuman-Kick-Stage6-Booster-K1 --checkpoint-file <model.pt or .pth>
```

Kick benchmark v2 (B-Human's spec: 200 trials, 4 kick-direction sectors x 2 ball
sides, priority score 0.5 time + 0.3 accuracy + 0.2 power; report, JSON and per-trial
CSVs in `docs/benchmarks_bhuman_kick/<name>/`):

```sh
uv run python scripts/tools/bench_bhuman_kick_v2.py --name <name> \
  --policy pretrained=../MachineLearning/IsaacGymRL/pre-trained/WalkAndKick/K1_kick_inner.pth \
  --policy mine=logs/rsl_rl/k1_bhuman_kick/<run>/model_<it>.pt
```

B-Human's pretrained kick scores 0.925 here (their own run of this spec: 0.927).

Optional training aids (off by default, training only):
`--agent.decap True` (APEX DecAP: spawns on mocap kick takes shortly before the
strike and blends the leg targets toward the clip, both fading as 0.99^(steps/100))
and `--agent.amp True` (AMP walking style from the gold walk's motion mix, legs
only, rewarded while walking to the ball, off within 0.8 m and after a kick).

Stages (`stages.py`, cumulative, from B-Human's readme): `Stage1` (= the plain
task id), `Stage2`, `Stage3a`, `Stage3b`, `Stage4`, `Stage5`, `Stage6a` (robustness
events at 10 %), `Stage6` (final values; a few hundred iterations only). Gradual
steps inside a stage take the first value; continue with CLI overrides such as
`--env.commands.kick.kick-direction-sigma-range 0.1`. B-Human's advice: move on
only once strong and scaled kicks are both somewhat accurate.

## What is where

| Booster Gym | mjlab port |
|---|---|
| `T1_Ball.step` after physics, `_update_kick_tensors`, `_check_termination` | `BHumanKickCommand.post_physics_step` (new opt-in hook, runs before terminations / rewards) |
| `_reset_idx`, `_reset_ball_idx`, `_resample_kick_ball` | `BHumanKickCommand._resample_command` and helpers |
| ball-only resets, `_teleport_robot`, `_resample_commands` | `BHumanKickCommand.compute` (after env resets) |
| `_compute_observations` (59 + 16) | `actor_obs` / `critic_obs`; the critic gets both |
| `_reward_*` (32 terms, scale x dt) | `mdp.py`, same names, weights in `env_cfg.REWARD_SCALES` |
| PD loop (2 ms x 10, filtered FD damping, friction, torque clip, target delay) | `actuator.BHumanPdActuator` |
| URDF (fixed arms / head, box feet, toe nub) | `robot.py` (our `k1.xml`, same masses / kinematics) |
| trimesh field (8 strips: plane / random / discrete) | `terrain.py` (one heightfield, bilinear height lookup) |
| `Runner` + `ActorCritic` | `runner.BHumanPpoRunner` (loads Booster Gym `.pth` directly) |

## Validation: B-Human's own trained policy in the port

`K1_kick_inner.pth`, deterministic, 1024 robots x 40 s (`eval_bhuman_kick.py`):

| Setting | Falls / robot-min | Kicks / robot-min | Aim error p50 | Within 10° | Scaled speed - expected (p50) | Strong speed (mean) |
|---|---|---|---|---|---|---|
| Stage 6 env (field, noise, all events) | 0.32 | 12.1 | 3.0-3.5° | 79-81 % | -0.10 m/s | 4.05 m/s |
| Stage 1 env | 0.29 | 12.6 | 3.2-3.5° | 78-81 % | -0.08 m/s | 4.12 m/s |
| Stage 6, plane, no observation noise | 0.20 | 14.4 | 2.3-2.5° | 89-93 % | -0.07 m/s | 4.49 m/s |

Their policy approaches, aims and scales its kick power as trained, so the
port reproduces their training conditions closely. Training runs at about 65k env
steps/s with 4096 envs on the RTX 5090 (about 1.5 s per iteration).

`K1_walk_start_for_kick.pth` (their suggested stage-1 start) falls 2-4 times per
robot-minute in the stage-1 env and does not aim yet; that is expected of a start
point, but it was not checked against Isaac Gym.

## Known differences from Isaac Gym

- One MuJoCo model for all worlds: B-Human's three robot assets (mesh feet, toe
  nub left / right) become box feet with a per-env toe nub (left / right / tucked
  in, `env_id % 3`).
- Ground friction: Isaac Gym used the terrain patch's friction (0.3-1.0 per 5 m
  patch); here the sole friction is drawn per env from 0.3-1.0. Contact compliance
  and restitution randomization have no direct MuJoCo equivalent and are not ported.
- Ball damping (Isaac Gym actor damping 0.75 / 0.5 per s) is applied once per policy
  step instead of every substep; the ball is a solid sphere with a stiff, mostly
  inelastic contact.
- Robots spawn on a random spot of the field at every reset (B-Human: fixed env
  origin per robot, +-1 m). They start on the ground instead of being dropped from 0.6 m.
- Reset joint noise is drawn per robot (Booster Gym draws one sample per reset batch).
- Feet, ball and robot state after a reset come from the post-reset kinematics
  (Booster Gym reads them one step stale).
- Slope and stairs strips (proportion 0 in the YAML) are not ported.

## Inputs vs. B-Human's deployed engine

The env (and this port) puts the flags as (strong, inaccurate, allow deviation);
the deployed `WalkingEngine.cpp` feeds (strong, steal-kick side, just-hit-the-ball).
For normal kicks the second slot is 0 in both, since training keeps
`disable_extra_deviation_flag` on. The engine also clips the ball velocity input
to 2 m/s, which the training env does not.

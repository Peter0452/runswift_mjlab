# runswift_mjlab knowledge base

Start here. This directory distils what the K1 work has learned so far, for
people and for agents. It does not replace the original notes: every entry
links to the note, run or memory it came from, and the originals stay where
they are (see [sources.md](sources.md)).

Last built: 2026-10-23, from the notes in `docs/`, the evolution and
experience records, in-code design notes and the session memory.

## The project in five lines

- Booster K1 humanoid football skills, trained in mjlab (MuJoCo Warp, Isaac
  Lab-style managers) with PPO, mostly AMP-PPO with the Muon optimizer.
- Deployed through `../k1_policy_runner` as ONNX at 50 Hz (22 joint targets).
- Skills: an AMP walk, one end-to-end kick loop (search, approach, kick,
  recover), a dribble policy with a kick mode, a 1v1 self-play striker, and a
  faithful port of B-Human's kick for comparison.
- Everything is judged on fixed benchmarks, never on training curves.
- Real-robot data so far comes from K1 #291.

## Read in this order

| If you want to | Read |
|---|---|
| Know what "better" means and what must not change | [objectives.md](objectives.md) |
| Keep training and the robot runner consistent | [deployment.md](deployment.md) |
| See the target layout, methods/recipes and the evolution-loop design | [architecture.md](architecture.md) |
| Work on a skill | [skills/](skills/): [walk](skills/walk.md), [kick](skills/kick.md), [dribble](skills/dribble.md), [self-play striker](skills/selfplay_striker.md), [B-Human port](skills/bhuman_kick.md) |
| Find the current best model for something | [models.md](models.md) |
| Design a reward or a run | [lessons/reward_design.md](lessons/reward_design.md) |
| Judge a run or pick a checkpoint | [lessons/training_eval.md](lessons/training_eval.md) |
| Deploy or interpret robot data | [lessons/sim2real.md](lessons/sim2real.md) |
| Run jobs without wasting a night | [lessons/operations.md](lessons/operations.md) |
| Find the original note behind any of this | [sources.md](sources.md) |

## Tasks that exist (34, all K1)

| Group | Task ids | Skill page |
|---|---|---|
| Walk prior | `Mjlab-Velocity-{Flat,Rough}-Amp-DA-Muon-Booster-K1` | [walk](skills/walk.md) |
| Kick pipeline | `Mjlab-Velocity-Kick-{Stage1,Approach,Stage3}-Amp-DA-Muon-Booster-K1`, `Mjlab-Velocity-Rough-Amp-DA-Muon-Booster-K1-KickHandoff` | [kick](skills/kick.md) |
| Dribble | `Mjlab-Velocity-Dribble-Amp-DA-Muon-Booster-K1` | [dribble](skills/dribble.md) |
| Self-play | `Mjlab-Velocity-Kick-SelfPlay-Amp-DA-Muon-Booster-K1`, `Mjlab-Velocity-Striker-Controller-Booster-K1` | [self-play](skills/selfplay_striker.md) |
| B-Human port | `Mjlab-BHuman-Kick[-Stage1..6a]-Booster-K1` (9) | [B-Human](skills/bhuman_kick.md) |
| Walk baselines | `Mjlab-Velocity-{Flat,Rough}-Booster-K1[-BaseWalk]`, `Mjlab-Velocity-HTWK[-Exact,-Unclipped,-Robust-FT]-Booster-K1-Nubots` | [walk](skills/walk.md) |
| Legacy kick | `Mjlab-Kick-{Approach,Near}-Booster-K1`, `Mjlab-Kick-WalkAmp[-Amp]-DA-Muon-Booster-K1`, `Mjlab-Tracking-Flat-Booster-K1-Kick[-Box,-Stage2]` | [kick](skills/kick.md#legacy-kick-tasks) |
| Other | `Mjlab-Getup-Flat-Booster-K1` | — |

Tasks removed on 2026-10-23 (upstream demos, unused variants) are on branch
`archive/pre-restructure-2026-10-23`; see `restructure/KEEP_LIST.md`.

## Where things live

| Thing | Place |
|---|---|
| Task code, per family | `src/k1/tasks/<family>/`: `walk/`, `kick/`, `dribble/`, `selfplay/`, `striker/` (each `env_cfg.py` + `rl_cfg.py` or `config.py`, `mdp/`, `tasks.py` registers), `bhuman/`, `getup/`, `legacy/` (old kick + tracking), `walk/baselines/` (PPO / HTWK walks) |
| Shared task code | `src/k1/tasks/velocity/`: shared mdp terms (`mdp/`, one namespace re-exporting the families), AMP wrapper, runners (`rl/`: AMP runner, anchor), base env configs |
| Robot model, ball, deploy layouts | `src/k1/robot/`, `src/k1/common/ball.py`, `src/k1/deploy/obs_layout.py` |
| Old module paths | `mjlab.tasks.velocity.*`, `mjlab.tasks.kick.*` etc. still import (served by `src/k1/compat.py`); patch family modules, not the re-export shims |
| AMP, multi-critic, kick teacher | `src/mjlab/amp/` |
| Methods, recipes, CLI | `src/k1/methods/` (registry + `METHOD.md` cards), `experiments/recipes/<family>/*.yaml` (run definitions, checked against the code), `rsw` (`rsw --help`; `src/k1/cli.py`) |
| Training runs | `logs/rsl_rl/<experiment>/<run>/` (latest, best and referenced checkpoints kept; configs in `params/`; `run.json` for runs started with `rsw train`) |
| Eval and bench tools | `scripts/tools/` (catalog: `scripts/tools/README.md`) |
| Benchmark results | `docs/benchmarks*/` (JSON) |
| Kick evolution loop state | `docs/evolution/` (`HANDOFF.md` first) |
| Experience records | `docs/experience/` |
| Robot runner, ONNX models, robot recordings | `../k1_policy_runner/` |

## Before and after changing code

Run the safety net in `tests/golden/README.md`: the task-set test, the
env-build test, the model snapshots (`scripts/tools/golden.py check`) and,
for anything that touches the kick loop, the champion benchmark
(`scripts/tools/golden_bench.py check`). A failure means behaviour changed;
either fix the change or, if it was intended, re-record and say why.

## Keeping this up to date

- New finding with evidence → add it to the right `lessons/` file with its
  source; never delete a superseded lesson, mark it `superseded` and say by what.
- New best model → update [models.md](models.md) and the skill page.
- New objective or standing decision from the user → [objectives.md](objectives.md), with the date.
- Long run-by-run logs stay in `docs/` notes; this directory holds the distilled version.

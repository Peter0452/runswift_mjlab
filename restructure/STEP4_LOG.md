# Step 4 log: moving K1 code into `src/k1/`

Running record of the code move (branch `restructure`), written while the user
was away (night of 2026-10-23). Each entry: what moved, the safety-net result,
and every **best guess** made without asking, so it can be reviewed and undone.

Safety net per commit: full `pytest tests/` + `scripts/tools/golden.py check`
(6 models, action diff must be 0); plus `scripts/tools/golden_bench.py check`
when kick-loop code is touched.

## Mechanism

- `k1` is a second top-level package next to `mjlab` (`pyproject.toml`:
  `[tool.uv.build-backend] module-name = ["mjlab", "k1"]`), registered through
  mjlab's own `mjlab.tasks` entry point (`k1 = "k1.tasks"`).
- Old module paths keep working through `k1.compat`: a finder first on
  `sys.meta_path` serves `<old>.<x>` as the module `<new>.<x>` itself (same
  objects, no double registration, real `__spec__` restored). One line per
  moved package in `k1.compat.ALIASES`. Run-log `params/*.yaml` that name old
  paths therefore still resolve.
- Files move with `git mv`; diffs of moved files are import lines only.

## Done

| Commit | What | Safety net |
|---|---|---|
| e25c412 | Stage 3 `ball_avoidance` −5 default, 0 only with the kick-retarget prior (user decision) | 1261 pass, golden ok |
| 609225f | B-Human port → `k1/tasks/bhuman/` | 1261 pass, golden ok |
| 9a8c1d1 | K1 model → `k1/robot/` | 1261 pass, golden ok. **Correction:** its message says "ty clean on k1"; the moved robot code has ~13 pre-existing ty diagnostics (unchanged by the move). Only the B-Human code is ty-clean. |
| 0565b45 | Ball model → `k1/common/ball.py` (re-exported by `approach.py`) | 1261 pass, golden ok, bench ok (2 separated) |
| bd17078 | Fix: gait-clock state on the env, not a dict keyed by `id(env)` (cause of the intermittent env-build test failures) | 1261 pass, golden ok |
| 544fe20 | `k1/deploy/obs_layout.py` + `tests/test_deploy_obs_layout.py` (deployed actor layouts as code, checked against golden) | new tests pass |
| ea8abe5 | `k1.compat` import finder replaces alias folders | 1272 pass, golden ok |
| 311ad64 | Legacy kick (`Mjlab-Kick-*`, arc kick, walk-AMP kick) → `k1/tasks/legacy/kick/`; alias `mjlab.tasks.kick` | 1273 pass, golden ok |
| e9587e3 | K1 tracking kick tasks (`Mjlab-Tracking-Flat-Booster-K1-Kick*`) → `k1/tasks/legacy/tracking/` | 1273 pass, golden ok |
| 3356ca6 | Getup (`Mjlab-Getup-Flat-Booster-K1`) → `k1/tasks/getup/` | 1273 pass, golden ok |
| ab41a60 | Whole `mjlab.tasks.velocity` (walk, kick, dribble, self-play, striker, AMP configs and runners; all K1 now) → `k1/tasks/velocity/` | 1273 pass, golden ok, bench ok (2 separated) |
| 23fe941 | Family mdp modules out of `velocity/mdp`: approach, kick_loop, kick_handoff, kick_prior → `kick/mdp/`; dribble, dribble_rewards → `dribble/mdp/`; self_play → `selfplay/mdp/`; striker_skills → `striker/mdp/`; walk_params → `walk/mdp/`. `velocity.mdp` re-exports them; namespace verified identical (482 names, 0 differences vs the previous commit) | 1273 pass, golden ok (one intermittent fail, see note 7), bench ok (2 separated) |
| ec1f0c7 | Configs split by family: `k1_amp/env_cfgs.py` → `walk/`, `kick/`, `dribble/env_cfg.py`; `k1_amp/rl_cfg.py` → `walk/`, `kick/`, `dribble/rl_cfg.py` (old files are re-export shims); `selfplay_cfgs.py` → `selfplay/config.py`; `selfplay_runner.py` → `selfplay/runner.py`; `striker_runner.py` → `striker/runner.py`. All 34 tasks' train/play/RL configs compared with the previous commit: identical except the `MemoryResetPPO` class_name string, which now names its new module (same class) | 1273 pass, golden ok, bench ok (2 separated) |
| (this) | Tasks register per family (`k1/tasks/{walk,kick,dribble,selfplay,striker}/tasks.py`); `k1_amp/__init__` no longer registers. **Fixes a bug from ec1f0c7:** `kick_bench2.py` (`--heavy` / ball overrides) and `kick_style_compare.py` patched `_APPROACH_BALL_*` on `env_cfgs`, which became a shim, so the patch no longer reached the ball; they now patch `k1.tasks.kick.env_cfg` (verified 0.1→0.29 kg, 0.08→0.095 m), and dribble reads the mass at call time again. Configs identical to before the split | 1273 pass, golden ok, bench ok (2 separated) |

## Best guesses (review these)

1. **Your uncommitted `kick_loop.py` edit** (joins `goal_mouth`'s return onto
   one 99-column line; whitespace only). `kick_loop.py` has to be split, so the
   edit was saved to `restructure/user_uncommitted/kick_loop_goal_mouth.patch`
   and the file reset to the committed version. Re-apply with
   `git apply restructure/user_uncommitted/kick_loop_goal_mouth.patch` before
   the split lands, or from the new location afterwards.
2. `deploy_2.py` deletion (yours) left uncommitted, untouched.
3. **`arrival_buffer.py` default path** resolves to `Desktop/Project/data/kick/` (outside
   `RL/`; `parents[6].parent`, now `parents[7].parent` after the move). Looks like a
   pre-existing bug, but kept identical: the legacy task's behaviour must not change.
4. **Tracking: only the K1 config moved.** `tracking/mdp/shot.py`, `shot_rewards.py`
   and `stand_blend.py` are ours but upstream's `tracking/mdp/commands.py` and
   `rewards.py` were edited to use them, so they stay in the framework for now
   (moving them would make mjlab import k1). Listed in "Our edits inside the
   framework" below.
7. **Intermittent golden failure (not treated as a regression):** after the mdp split one
   full `golden.py check` had `kick_h011_teacher` fresh-reset obs drift 2.5 (actions on
   stored obs: diff 0). It passed alone and in two more full runs, and the `mdp`
   namespace is identical name by name, so the guess is GPU nondeterminism in the reset
   (one sampled value). Seen once in ~12 golden runs tonight. Watch for it; if it recurs,
   pin the reset (deterministic warp, or compare with a tolerance on sampled spawns).
8. **`velocity/mdp/__init__` import order is load-bearing** (star imports, later wins):
   marked `# ruff: noqa: I001`. Family `mdp/__init__` files import the aggregate first so
   direct imports load in the old order. Transitional; goes away when configs import
   family modules directly.
9. **Family config files are `env_cfg.py` + `rl_cfg.py`** (the repo's existing split, as in
   the B-Human port), not one `config.py` as the architecture sketch says. Self-play keeps
   one `config.py` (it was one module) that also holds the striker controller's configs:
   the controller is trained by self-play and its env builds on it.
10. **Deployment-match helpers stay in `kick/env_cfg.py`** (`LEG_TORQUE_CLIP`,
   `DEPLOY_Q_LIMITS`, `_deployment_match`, `_clip_leg_torque`; dribble imports them).
   `_deployment_match` reads `KICK_GENES`, so it is not contract-only yet; the tables move
   to `k1/deploy/contract.py` in Step 5.
11. **Config refactors are checked by dumping every task's configs** (repr, addresses
   stripped, worktree paths normalised) before and after, in addition to golden.
12. **Shims are read-only.** Writing a module attribute on a re-export shim
   (`env_cfgs.X = ...`, `rl_cfg.X = ...`) no longer affects the configs; patch the family
   module (`k1.tasks.kick.env_cfg`) instead. All in-repo writers were found and moved;
   outside scripts that patch the shim would silently do nothing.

## Our edits inside the framework (left in `src/mjlab/`, to list or move later)

- `tasks/tracking/mdp/{shot,shot_rewards,stand_blend}.py` + hooks in `commands.py`, `rewards.py`.
5. **`mjlab.tasks.velocity` moved whole first**, then split by family in later commits
   (keeps each commit checkable). Its generic pieces (upstream-derived rewards,
   observations, terminations, velocity command) came along: no non-K1 velocity task
   remains, so the velocity task is K1 territory.
6. **Never run tools with `--help` to smoke-test them:** `kick_style_gallery.py` ran
   for real and `evolve_hier.py` would have started a 12 h loop (stopped before it
   reached it). Tools are import-checked by executing only their import lines.

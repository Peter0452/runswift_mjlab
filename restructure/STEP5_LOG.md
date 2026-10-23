# Step 5 log: methods, recipes, rsw, the evolution loop

Started 2026-10-24 while the user was away; same rules as `STEP4_LOG.md`:
each entry lists what was built, how it was checked, and every **best guess**
made without asking.

## Built

| Commit | What | Checked by |
|---|---|---|
| 6138b66 | `k1/methods/`: registry (13 methods: extension points, deployment impact, status, parameter fields, `detect`) + one `METHOD.md` card each | `tests/test_k1_methods.py`; detection on all 34 tasks reviewed |
| 6138b66 | `k1/recipes.py` + `experiments/recipes/<family>/*.yaml`: one default recipe per AMP task, and `kick_stage3_h022` (the deployed champion's training) | every recipe checks clean; h022 recipe vs the champion run: identical except the speed caps |
| 6138b66 | `k1/runs.py`: `run.json` in each run directory (recipe, env vars, methods actually on, git, label `research`, verdicts later) | written by a real 2-iteration `rsw train` smoke run (run deleted afterwards) |
| 6138b66 | `rsw` CLI (`k1/cli.py`, `pyproject` script): `tasks`, `methods`, `recipe check|diff`, `train` (dry run unless `--go`), `run show`, `check [--bench]` | used for all of the above |
| 6138b66 | `mjlab/scripts/train.py`: `launch_training(..., log_dir=None)` and `run_log_dir()` so `rsw train` can write `run.json` first (backward compatible) | full test suite |
| c35e46e | `k1/deploy/contract.py` (rate, joint order, default pose, scales, PD, joint-target clip, torque clip, delay) + `tests/test_deploy_contract.py` | configs unchanged; contract test on walk, kick, dribble, self-play |
| 86cb231 | Deploy gate `k1/deploy/parity.py` + `rsw deploy check` (export, ONNX metadata vs contract, ONNX vs actor, lost-ball rule) recording a verdict in `run.json` and labelling the run `deployable` | deployed champion h022 passes (ONNX diff 3.8e-6, lost-rule p99 0); metadata check on the four deployed ONNX files |
| 1ffc692, 7b73768 | `k1/eval`: `Verdict` (fixed shape; only `scored` has a score; `promotable` needs a seed-2 confirmation) and judges per task (kick wrapped: bench v2 + `fitness_v2` vs the champion and B-Human; dribble, self-play, striker, B-Human listed with their current tools); `rsw judge` appends the verdict to `run.json` | `tests/test_k1_eval.py`; `rsw judge` on the champion |
| d471411 | `k1/evolve`: outer loop (collect → screen → confirm → promote / record; escalate with a decision packet; refill the pool from designers through `rsw recipe check`), inner PBT (exploit / explore within ranges), state store, deterministic designers (genes, method), real trainer (`rsw train` detached, pid + log) and judge; `rsw evolve init|status|step|run` (trains only with `--go`). Loop state initialised with the h022 champion | `tests/test_k1_evolve.py` (fake trainer and judge); real designer proposals pass `rsw recipe check`; **not run for real** |

## What the checks found

- **The registered stage-3 task no longer trains the deployed champion.** Since
  2026-10-16 (appex) it adds DecAP from kick clips, multi-critic (0.5, 0.5) and the
  kick motion mix; h022 (2026-10-09) had none of these, used the walk mix,
  `desired_kl` 0.004, its lineage's genes and a reward program. The recipe
  `kick/kick_stage3_h022.yaml` is the champion's setup; to continue the champion
  line, train from it, not from the bare task.
- **The evolution state records the wrong genes for the champion.**
  `docs/evolution/state.json` `champion.genes` are the frame's genes and miss the
  child's L0 mutations (h022_c2 had `w.touchdown_speed` −39.0636,
  `k.MOMENTUM_KICK_MAX_SPEED` 0.9646, `k.PROMPT_KICK_TAU` 1.3626). The exact genes
  are `child_genes` of `hier/h022` in `docs/experience/experiences.jsonl`. The new
  loop records the full recipe per run (`run.json`) so this can't recur.
- The champion run's env, compared field by field after module renames and
  build-time fields: identical except the speed caps (chase caps vy 2.0 / wz 3.0
  since 2026-10-23 vs h022's 1.5 / 1.5). Newer fields are off or at defaults, among
  them the head tracker's search pose (`search_pitch`, `search_yaw`) — a
  deployment-relevant addition after h022.

## Best guesses (review these)

1. **Method statuses** follow the promotion rule's meaning of "adopted" = in a
   deployed model: adopted AMP, Muon, symmetry augmentation, SWA/blends;
   experimental DecAP, multi-critic (both post-date every deployed model), CAPS,
   KL anchor, kick teacher, conditioned AMP, reward grammar; parked FastSAC;
   rejected plain B-Human action imitation. The h022 champion did train with CAPS
   (temporal 1.0, spatial 0.4), so CAPS could be argued adopted; left experimental
   until you say.
2. **Recipes declare every method that is on**, with key parameters only (a
   verifier checks the declared ones). Strict on purpose: a recipe that forgets a
   method fails `rsw recipe check`.
3. **`touches: runtime` is enforced only for actor-input changes** on tasks with a
   deployed layout (`k1/deploy/obs_layout.py`); action scales, PD, caps and clips
   are not yet detected (they move into `k1/deploy/contract.py` with the parity gate).
4. **The h022 recipe keeps today's chase caps** rather than h022's narrower ones:
   the caps are a deployment-contract value you set on 2026-10-23.
5. **PyYAML is used as installed** (an indirect dependency); not added to
   `pyproject.toml` to avoid touching `uv.lock` unattended. Add it when convenient.
6. **`rsw train` resumes from `init`** by setting `resume`, `load_run`,
   `load_checkpoint` (the trainer's own mechanism); `warm_start` stays a recipe
   `rl:` field when wanted.
8. **Lost-rule gate thresholds:** `lost_rule_parity.py` always exits 0, so the gate
   parses its statistics: pass when p99 |diff| <= 0.01 and at most 1 % of steps
   differ by > 0.05 (the champion: 0-6 of 1500, the documented edge cases).
9. **The gold walk's deployed ONNX fails the metadata check:**
   `../k1_policy_runner/amp_models/model_9950.onnx` has 3-decimal action scales
   (0.213 for 0.2125, 0.12 for 0.119687; lesson S5 predates the fix). Marked as a
   strict known failure in `tests/test_deploy_parity.py`. Fix: re-export with
   `scripts/tools/export_onnx.py --task Mjlab-Velocity-Rough-Amp-DA-Muon-Booster-K1`
   and deploy it (a runner-side file swap; not done from this repo). Worth checking
   whether the runner reads the walk's scales from this metadata.
10. **Judge noise and promotion:** the champion judged against its own reference
   scored +10.6 and +29.3 on single quick runs (0 real regressions), so a verdict is
   `promotable` only with `confirmed=True` (second seed vs the reference's second
   seed, as `evolve_kick.confirm_and_install` does). Seed-2 confirmation inside
   `rsw judge` is not built yet.
11. **CI-less style metrics are findings, not regressions** in the kick judge
   (`style_selection_pct`, `style_repertoire`), matching golden_bench's UNGATED set;
   `fitness_v2` itself still counts them (left unchanged: the old loop uses it).
12. **Loop defaults:** at most 2 trainings in flight (lesson O3), 500 iterations per
   child from the champion checkpoint, escalate after 6 non-improving verdicts,
   quick screen then full two-seed confirmation (as the old loop). Designers: one-gene
   steps (x0.8 / x1.25) on `w.kick_direction`, `w.kick_vel`, `w.long_kick_power`,
   `w.walk_speed_track`, `w.action_rate_l2` within ranges in `k1/cli.py`
   (`EVOLVE_GENES`), and switching `caps` (temporal 1.5) or `decap` (kick clips) on
   (`EVOLVE_METHODS`). No LLM designer. All of these are placeholders to review.
13. **`ball_avoidance` rule enforced in recipes:** with DecAP from kick clips on,
   `recipes.build` sets `ball_avoidance` to 0 even over a recipe's override (your
   2026-10-23 rule), so a designer that turns the prior on can't keep -5.
14. **The loop was not started.** Running it spends GPU nights on the choices above;
   start with `rsw evolve step --go` (one step) or `rsw evolve run --hours 8 --go`.
7. The smoke run used `--agent.logger tensorboard --agent.upload-model False`
   so nothing went to wandb.

## Not built yet (next)

- Wrap the dribble / self-play / striker judges; seed-2 confirmation in `rsw judge`;
  behaviour checklist filled automatically (falls, posture, peak vs final).
- Decisions from you before the loop runs: GPU budget per night, designer ranges,
  whether an LLM front-end may write recipes unattended.
- Wire the inner PBT loop into training (needs mid-run checkpoint swaps in the
  runner); PB2 instead of random explore.
- Retire the old loop (`evolve_hier.py`, `docs/evolution/`) once the new one has
  promoted a champion; its records stay as history.

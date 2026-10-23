# Step 5 log: methods, recipes, rsw, the evolution loop

Started 2026-10-24 while the user was away; same rules as `STEP4_LOG.md`:
each entry lists what was built, how it was checked, and every **best guess**
made without asking.

## Built

| Commit | What | Checked by |
|---|---|---|
| (this) | `k1/methods/`: registry (13 methods: extension points, deployment impact, status, parameter fields, `detect`) + one `METHOD.md` card each | `tests/test_k1_methods.py`; detection on all 34 tasks reviewed |
| (this) | `k1/recipes.py` + `experiments/recipes/<family>/*.yaml`: one default recipe per AMP task, and `kick_stage3_h022` (the deployed champion's training) | every recipe checks clean; h022 recipe vs the champion run: identical except the speed caps |
| (this) | `k1/runs.py`: `run.json` in each run directory (recipe, env vars, methods actually on, git, label `research`, verdicts later) | written by a real 2-iteration `rsw train` smoke run (run deleted afterwards) |
| (this) | `rsw` CLI (`k1/cli.py`, `pyproject` script): `tasks`, `methods`, `recipe check|diff`, `train` (dry run unless `--go`), `run show`, `check [--bench]` | used for all of the above |
| (this) | `mjlab/scripts/train.py`: `launch_training(..., log_dir=None)` and `run_log_dir()` so `rsw train` can write `run.json` first (backward compatible) | full test suite |

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
7. The smoke run used `--agent.logger tensorboard --agent.upload-model False`
   so nothing went to wandb.

## Not built yet (next)

- Deploy parity gate and labels (`research` → `deployable`), contract tables into
  `k1/deploy/contract.py`.
- Verdict schema and `k1/eval` judges (one shape per task), appended to `run.json`.
- Outer loop (diagnose → designer → recipe → gates → pool → judge → verdict →
  escalate) and inner PBT/PB2 loop; loop state in `experiments/evolution/`
  (gitignored). These need decisions from you (GPU budget per night, which
  designers to enable first, whether an LLM front-end may write recipes
  unattended), so they wait.

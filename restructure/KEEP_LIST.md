# runswift_mjlab keep-list (Step 1)

Generated 2026-10-23. Read-only inventory: nothing has been moved or deleted.
Approve or edit the decisions below; Step 0 (backup) and Step 4 (restructure)
act only on what is approved here.

Decisions: **KEEP** stays in place · **LEGACY** kept and replayable, not active ·
**ARCHIVE** leaves the active repo but is recoverable (git tag or backup) ·
**MERGE** folded into another file · **PRUNE** large regenerable or
unreferenced data · **DELETE** junk · **ASK** your call.

Files in this folder:

- `checkpoints.csv`: every checkpoint (10,040) with decision and reasons
- `runs.csv`: every run (430) with status, size, keep size and why
- `summary.json`: totals, per-experiment numbers, deployed-model matches
- `inventory.py`: re-run with `python3 restructure/inventory.py`

---

## Approved decisions (2026-10-23)

| # | Decision | Status |
|---|---|---|
| A1 | Keep the latest and best checkpoint per run. "Best" means the peak of smoothed `Train/mean_reward` (`best.csv`, from `best_ckpt.py`) plus checkpoints chosen by evaluation (champions, deployed, parents, benchmarked). Active dribble runs are untouched until they finish; the 18 git-tracked log files are kept. | **Done**: 7,940 checkpoints deleted, 31 GB freed |
| A2 | Keep the JSON benchmark results, discard the traces | **Done**: 4,862 `.npz` deleted, 18.5 GB freed; 837 JSON kept |
| A3 | wandb | open |
| A4 | Keep the 4 HTWK tasks; remove the other 14 `*-Nubots` tasks | **Done** (`restructure` branch) |
| A5 | Remove non-K1 tasks (Cartpole, Yam, G1, Go1) and their G1/Go1-only tooling (`demo`, `csv_to_npz`, nightly benchmarks, cloud configs, Go1 terrain demo) | **Done**; framework tests ported to K1 envs |
| — | Remove `Velocity-Flat/Rough-Booster-K1-FastSAC`, `-K1-G1` | **Done**; 33 orphaned config functions removed |
| — | No ARCHIVE category: AMP walk grid (6), arc kick, Kick-Near-Amp, Kick-WalkAmp, Kick-WalkAmp-Amp, root probes, `launch_v15.sh`, `relaunch_selfplay.sh`, `styles_then_evolve.sh` deleted | **Done**. Kept `dribble_watch*.sh` and `play_dribble.sh` while dribble is active. `kick_transition_probe.py` and `artifacts/` are untracked, so deleting them is permanent: not done yet |
| — | Delete `record_kick_kinematics.py`, `collect_arrival_buffer.py`, `measure_swing_stretch.py`, `import_nubots_onnx.py` | **Done** |
| A9 | No cold backup | approved |
| — | Git: snapshot on `archive/pre-restructure-2026-10-23`; stashes saved as `archive/selfplay-stash-*` and `archive/stash-*`; `git gc` | **Done**: `.git` 17 GB → 148 MB |

### Incident found during Step 2 (2026-10-23)

Three run directories in `logs/rsl_rl` are symlinks to runs in other
experiments (`wwcmu45_roughft/2026-09-20_21-17-22` → wwcmu30,
`wwcmu50_roughft/2026-09-21_09-46-12_trk275` → wwcmu45,
`k1_kick_approach_amp/2026-09-30_22-03-48` → stage 1). The inventory listed
each alias as its own run, so pruning through an alias deleted
`k1_velocity_amp_symmetric_muon_wwcmu30/2026-09-20_21-17-22/model_9950.pt`,
which the real run had marked KEEP. It was kept only because of a wrong
deployed-ONNX match: the deployed `amp_models/model_9950.onnx` is
byte-identical to the gold walk's export
(`wwcmu50_roughft/2026-09-21_20-34-24_stageA/model_9950.onnx`), whose `.pt`
is intact. So the lost file was an ordinary intermediate checkpoint; nothing
referenced is missing (all 2,091 kept rows checked). Fixed in `inventory.py`:
symlinked run dirs are skipped, deployed models are matched by exact ONNX hash
first, and "active" uses checkpoint times only (deleting files had bumped the
directory times). The CSVs here are the corrected run.

## Decisions needed from you

| # | Question | Recommendation |
|---|---|---|
| A1 | Prune 8,209 unreferenced intermediate checkpoints (38.3 GB)? Every run keeps its latest checkpoint, all referenced ones and all metadata. | Yes. Cold backup first only if you want it |
| A2 | Back up the raw benchmark `.npz` dumps (17.4 GB) to cold storage, or delete them? The JSON results stay. | Cold backup, then remove from repo |
| A3 | Delete local `wandb/` (11 GB) after checking every run is on the server? | Yes, after the sync check |
| A4 | NUbots/HTWK walk tasks (18): keep which? | Keep the configs behind `deploy.py`'s torso_swing ONNX and HTWK-Robust-FT; archive the rest |
| A5 | Upstream demo tasks (Cartpole, Yam, G1, Go1): keep? | Depends on whether you still pull from upstream mjlab |
| A6 | `Getup-Flat-Booster-K1`: never trained. Needed later for matches? | Keep as LEGACY |
| A7 | **Self-play / striker code exists only in `stash@{0}`** (Oct 12–16; never re-applied after the Oct 16 pull of `appex`). Includes the anchor wiring used by self-play v10–v16, possession/territory/walk-engage rewards, and striker memory. 5 self-play test files fail now. | Save as a branch now; then restore by merging with `appex` |
| A8 | 32 unreferenced blend/SWA checkpoints (0.15 GB) | Keep; they're cheap |
| A9 | Where should the backup go? | You choose: external drive, another disk, or cloud |

---

## 1. Checkpoints (`logs/rsl_rl`, 49.7 GB, 430 runs)

**Rule:** every run keeps its **latest checkpoint and its full metadata**:
`params/`, `git/` diff, tfevents, `genes.json` and the run's ONNX (5.2 GB in total).
On top of that it keeps every checkpoint that something refers to:

- evolution `state.json` / `hier_state.json` (champion, v1 champion, archive)
- a parent checkpoint named in any run's `params/agent.yaml` (warm start, kick teacher)
- a deployed ONNX in `../k1_policy_runner`
- notes, memory, evolution records, the experience repo, benchmark JSONs or eval outputs
- runs touched since 2026-10-20 (**active**: nothing is pruned there yet)

| Decision | Checkpoints | Size |
|---|---|---|
| KEEP (referenced or latest) | 839 | 3.9 GB |
| KEEP (active runs, dribble v14–v53) | 960 | 7.4 GB |
| ASK → keep (unreferenced blend/SWA) | 32 | 0.15 GB |
| **PRUNE** (intermediate, unreferenced) | 8,209 | **38.3 GB** |

Safety checks, all passed:

- Evolution state: 34 checkpoint references, **0** marked prune
- Parent checkpoints: 43 references, **0** marked prune
- Paths in memory: 3, **0** marked prune. Paths in notes: 10, **0** marked prune.

Run status: 236 **notable** (champion, deployed, or in notes/memory), 133 referenced
elsewhere, 44 active, 17 plain (smoke runs, ABORTED runs, early walk stages; each
still keeps its latest checkpoint).

| Experiment | Runs | Now | After |
|---|---|---|---|
| k1_kick_stage3_amp | 234 | 12.3 GB | 3.2 GB |
| k1_dribble_amp (44 active) | 67 | 10.9 GB | 7.6 GB, then about 0.5 GB once finished |
| k1_velocity_amp_*_wwcmu45_roughft | 5 | 4.1 GB | 0.03 GB |
| k1_kick_tracking | 8 | 3.5 GB | 0.10 GB |
| k1_kick_approach_amp | 11 | 3.4 GB | 0.06 GB |
| k1_velocity_amp_*_wwcmu50_roughft | 6 | 3.0 GB | 0.04 GB |
| k1_velocity_amp_*_wwcmu30 | 1 | 2.8 GB | 0.01 GB |
| k1_kick_approach | 47 | 2.6 GB | 0.13 GB |
| k1_kick_selfplay_amp | 18 | 2.5 GB | 0.12 GB |
| k1_kick_stage1_amp | 2 | 1.5 GB | 0.02 GB |
| others (7 experiments) | 31 | 3.1 GB | 0.2 GB |

**Deployed models** (`../k1_policy_runner`, 138 ONNX):

- 108 matched to a source checkpoint, all kept. Some matches were made by version
  and step, by SWA/blend file name, or (for one file) as a probable match; see
  `summary.json → deployed`.
- 26 date from August (`v2_models`–`v6_models`, `robocup_s2r_*`, `k1_minimal_*`)
  and were trained before this repo existed, so they're out of scope.
- 6 recent ones have no source `.pt` here, so **the ONNX is the only copy**. KEEP,
  and record this on their model cards: `kick_loop_models/stage2_approach_8550`,
  `k1_v24_model_105600`, `k1_v28_model_116000`, `kick_models/model_10600`,
  `nubots_models/2026-08-21_06-32-23`, `nubots_models/k1_walk_htwk_*`.

Other checkpoint stores:

- `checkpoints/` (5 curated files): **KEEP**. These are the only copies; the
  BaseWalk and Kick-Near runs are not in `logs/`.
- `nubots_models/` (17 MB): **KEEP**
- Broken link `logs/rsl_rl/k1_kick_approach/plant1_65600/model_65600.pt` points
  at the old repo path `/home/peter/Desktop/runswift_mjlab/...`. **Fix** it to
  point at `checkpoints/k1_approach_plant1_65600.pt`.

---

## 2. Tasks (74 registered)

| Decision | Tasks | Evidence |
|---|---|---|
| **KEEP (live)** | `Velocity-Kick-Stage1/Approach/Stage3/SelfPlay-Amp-DA-Muon`, `Velocity-Dribble-Amp-DA-Muon`, `Velocity-Striker-Controller`, `Velocity-Rough-Amp-DA-Muon-KickHandoff` | runs Sep 29 – Oct 23, tests, evolution |
| **KEEP (live base)** | `Velocity-Flat/Rough-Amp-DA-Muon-Booster-K1` | AMP walk prior, parent of the kick lineage |
| **KEEP (live)** | `BHuman-Kick-Booster-K1` + Stage1–6a (9, one loop) | runs Oct 18, tests, bench reference |
| **KEEP (dependency)** | `Tracking-Flat-Booster-K1-Kick-Stage2` | `kick_handoff` replays its frozen kick tracker; tested |
| **LEGACY** | `Velocity-Flat/Rough-Booster-K1-BaseWalk` | produced 3 curated checkpoints |
| **LEGACY** | `Kick-Approach-Booster-K1`, `Kick-Near-Booster-K1` | curated `plant1_65600`, `stance_81800`; 47 runs; deployed `k1_v24_*` |
| **LEGACY** | `Kick-WalkAmp-DA-Muon`, `Kick-WalkAmp-Amp-DA-Muon` | 14 runs (Sep 27–28), tested |
| **LEGACY** | `Tracking-Flat-Booster-K1-Kick`, `-Kick-Box` | 8 runs (Sep 30), tested |
| **LEGACY** | `Velocity-Flat/Rough-Booster-K1` | the base K1 velocity config the others build on |
| ASK (A4) | 18 × `*-Booster-K1-Nubots` (Phase1–3, Sym, Stab, Quality, Speed, Symmetry, HTWK ×4, Flat/Rough) | 0 local runs, but `deploy.py` runs their ONNX; 4 HTWK tasks are in tests |
| ASK (A5) | Cartpole ×2, Yam ×4, G1 ×4, Go1 ×2 | upstream; G1/Go1 are in upstream tests |
| ASK (A6) | `Getup-Flat-Booster-K1` | 0 runs |
| **ARCHIVE** | `Velocity-Flat/Rough-Amp`, `-Amp-DA`, `-Amp-Muon` (6 of the 8-task grid) | 0 runs; generated by a loop, so just narrow the loop |
| **ARCHIVE** | `Kick-Booster-K1` (arc), `Kick-Near-Amp`, `Kick-WalkAmp`, `Kick-WalkAmp-Amp` | 0 runs |
| **ARCHIVE** | `Velocity-Flat/Rough-Booster-K1-FastSAC`, `-K1-G1` | one shared run, Jul 24 |

Note: `tasks/kick/` cannot be removed as a package. `train.py`, the
velocity/tracking K1 configs and three scripts import its helpers
(`ball_phase`, `pref_pose`, `terminations`, the AMP wrapper). Those move to a
shared module first.

---

## 3. Code and scripts

| Decision | Item | Reason |
|---|---|---|
| **MOVE** | `src/mjlab/test.py` → `scripts/tools/kick_traj_viewer.py` | standalone kick viewer inside the package |
| **DELETE** | `src/mjlab/amp/utils/normalizer.py` | never imported (stays in git history) |
| **KEEP** | `src/mjlab/tasks/velocity/rl/anchor.py` | used by self-play v10–v16 through the `class_name` string; its wiring is in `stash@{0}` (A7) |
| **MERGE** | `deploy_2.py` → `deploy.py --model` | 16-line diff; robot-side path hard-coded |
| **MERGE** | root `export_onnx.py` ↔ `scripts/tools/export_onnx.py` | 100-line diff; keep one |
| **ARCHIVE** → `scripts/probes/` | `gait_probe.py`, `reward_probe.py`, `bench_velocity.py`, `kick_transition_probe.py` (+ `artifacts/`) | one-off probes at the repo root |
| **ARCHIVE** → `scripts/archive/launch/` | `launch_v15.sh`, `relaunch_selfplay.sh`, `dribble_watch*.sh`, `play_dribble.sh`, `styles_then_evolve.sh` | record how runs were launched |
| **LEGACY** (with old kick) | `record_kick_kinematics.py`, `collect_arrival_buffer.py`, `measure_swing_stretch.py`, `import_nubots_onnx.py` | tools for the legacy tasks |
| **KEEP** | other `scripts/tools/*` (eval, bench, evolve, parity, lint, blend/SWA) | in use or mentioned in notes/memory |
| **KEEP** | `render_terrain_gallery.py`, `terrain_explorer.py` | upstream tools |
| Later (Step 4) | about 220 lines of unreferenced K1 functions (`rewards.py` ×4, `fast_sac_runner_cfg`, `augment_symmetries_parallel`, `_long_band`, …) | remove during the code move |

---

## 4. Data, docs and git

| Decision | Item | Size | Note |
|---|---|---|---|
| **KEEP** | run metadata in `logs/rsl_rl` (params, git diffs, tfevents, genes) | 5.2 GB | the record of everything tried |
| **KEEP**, gzip | `logs/launch/*.log` | 509 MB | about 10× smaller compressed |
| **KEEP** | `logs/{dribble,controller,selfplay}_eval`, `logs/kick_kinematics` | 55 MB | measured results |
| **KEEP** → `results/` in Step 4 | `docs/benchmarks*/**/*.json` (837), reports, `screens/`, 7 bench ONNX | 85 MB | the benchmark record |
| ASK (A2) | `docs/benchmarks_v2/{cpu,runswift}/**/*.npz` (4,862) | 17.4 GB | raw trajectories; JSON summaries already kept |
| **KEEP** | all `docs/*.md`, `docs/evolution/`, `docs/experience/`, `kick_style_gallery/`, `approach_catalogue.yaml` | 3 MB | knowledge; Step 2 indexes it |
| **KEEP** | `harbor/outputs`, `.cache/` | 5 MB | small |
| ASK (A3) | `wandb/` (386 runs) | 11 GB | check sync first |
| **DELETE** (git gc) | 5,377 staged-but-never-committed files in `.git` | 18.1 GB | byte-identical to files on disk (verified by hash) |
| **EXPORT first** | 20 more such files not on disk: 3 overwritten blend checkpoints, 17 older source versions | 15 MB | save to the backup before gc |
| **BRANCH first** | 13 dropped stashes (Oct 10–19) + live `stash@{0}` | tiny | save as `archive/stash-*` branches so gc keeps them. `stash@{0}` and `2b7bc9a` hold unrestored self-play work (A7) |
| **DELETE** | `__pycache__/`, `.ruff_cache/`, `.pytest_cache/`, `MUJOCO_LOG.TXT` | <1 MB | regenerable |

---

## 5. Knowledge to carry forward (input to Step 2)

Nothing here is removed. These are the sources Step 2 indexes into `knowledge/`:

- 18 K1 notes (~460 KB), `docs/evolution/{HANDOFF,log,monitor,hier_report}.md`,
  `docs/experience/experiences.jsonl`, `checkpoints/README.md`, 17 memory files
- Measured results inside code comments and docstrings (e.g. `anchor.py`
  drift numbers, the `k1_amp/__init__.py` style-weight rationale, `v24`/`v32`
  notes in `dribble.py`). Step 4 must move these files, not rewrite them.
- Lineage in each run's `params/agent.yaml` (`load_checkpoint`,
  `kick_teacher_checkpoint`), which can build a full model family tree.

## Expected result once approved

| | Now | After |
|---|---|---|
| Repo on disk | 97 GB | about 15 GB (8 GB of it `.venv`) |
| `logs/` | 45 GB | about 13 GB, falling to about 6 GB once dribble finishes |
| `.git` | 17 GB | about 0.1 GB |
| Work lost | | none: every run keeps its latest checkpoint and metadata, all referenced checkpoints stay, archives stay recoverable |

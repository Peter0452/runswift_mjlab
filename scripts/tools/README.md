# scripts/tools: catalog

Every tool here, grouped by the job it does. Run them as
`.venv/bin/python scripts/tools/<tool>.py ...` (long evals under
`timeout -k 30 N`); each file's docstring has its usage.

**Do not smoke-test a tool with `--help`.** Several tools take their arguments
from `sys.argv` by position and ignore flags they do not know: `--help` has run
`kick_style_gallery.py` for real, and `evolve_hier.py` would start a 12-hour
evolution loop.

These stay where they are during the restructure (old commands keep working);
the evaluation and evolution layer is rebuilt in Step 5 as `k1/eval` (one judge
per task, one verdict shape) and `k1/engine` (was `k1/evolve`; see `knowledge/architecture.md`).

## Safety net (run before and after code changes; `tests/golden/README.md`)

| Tool | What it checks |
|---|---|
| `golden.py` | Golden action snapshots for the six models we must not break |
| `golden_bench.py` | Champion benchmark: the kick champion still scores the same on bench v2 quick |

## Judges: score a checkpoint on a fixed benchmark

| Task | Tool | What it does |
|---|---|---|
| Kick (stage 3) | `kick_bench2.py` | **Benchmark v2**: the policy as the robot runs it, per situation (GPU engine) |
| Kick | `kick_bench2_cpu.py` | Benchmark v2 on the CPU engine: the robot's own runner code in the runner's MuJoCo bridge |
| Kick | `kick_bench2_report.py` | Side-by-side report of benchmark v2 results |
| Kick | `fitness_v2.py` | Fitness and promotion gates on benchmark v2 results |
| Kick | `rs_kick_bench.py` | **runswift kick benchmark v2**: 200 trials (4 direction sectors x 2 ball sides x 25), ball in front, standing start; same trials and score as `bench_bhuman_kick_v2.py` (`k1/eval/rs_kick.py`) |
| Kick | `kick_benchmark.py` | Benchmark v1 (older; scored table vs B-Human and our best) |
| Kick | `eval_kick_loop.py` | Per-episode evaluation of the stage-3 kick loop |
| Kick | `kick_probes.py` | Probes beyond `eval_kick_loop.py` |
| Kick | `eval_kick_ck.sh` | Waits for a checkpoint, then runs `eval_kick_loop.py` modes and `kick_probes.py` |
| Kick | `runswift_scenario.py` | Our policy on runswift's kick-comparison grid, in our sim |
| Kick | `lowcap_timing.py` | Where the time to the first kick goes at low speed caps |
| Dribble | `dribble_eval.py` | Fixed-command evaluation of a dribble checkpoint |
| Dribble | `dribble_skill_eval.py` | Skill evaluation for the v22 scenarios |
| Dribble | `dribble_gate.py` | No-regression gate against the fixed bench model (swa_v17) |
| Dribble | `dribble_watch.sh`, `dribble_watch_bench.sh`, `dribble_watch_flat.sh` | Evaluate (and gate, and flat-foot check) a dribble run's checkpoints while it trains |
| Self-play | `selfplay_eval.py` | Fixed-opponent evaluation of a phase-2 (flat self-play) checkpoint |
| Striker | `controller_eval.py` | Fixed-opponent evaluation of the two-level striker |
| B-Human port | `bench_bhuman_kick_v2.py` | B-Human K1_Ball kick benchmark v2 on the ported env |
| B-Human port | `eval_bhuman_kick.py` | Evaluate a policy in the ported B-Human kick env |

## Deployment: export and parity with k1_policy_runner

| Tool | What it does |
|---|---|
| `export_onnx.py` | Export a checkpoint to ONNX with deploy metadata |
| `onnx_parity.py` | ONNX gives the same actions as the trained actor (batch 1, as on the robot) |
| `lost_rule_parity.py` | Lost-ball rule: training env vs the runner's `KickLoopPolicy` (needs the runner path) |
| `rsw_aligned.sh` | runswift harness on the "aligned" fixture (training foot mesh as collider) |

## How a policy moves (diagnostics)

| Tool | What it does |
|---|---|
| `kick_style_compare.py` | Ball speed, launch angle, body speed, foot yaw, foot speed and torques at each kick |
| `kick_anatomy.py` | Whole-body anatomy of each kick (leg, support foot, steps, swing, flight, trunk) |
| `reward_lint.py` | Per-term reward statistics on a checkpoint's own behaviour, with lesson-based checks |
| `reward_budget.py` | Reward budget report for a training run (TensorBoard) |
| `selfplay_progress.py` | Block-averaged self-play training curves |
| `weight_drift.py` | Relative actor weight change against a reference |
| `watch_run.py` | Watch a run; exit at an iteration or when it breaks |

## Checkpoint operations

| Tool | What it does |
|---|---|
| `average_checkpoints.py` | Average actor weights (SWA) |
| `blend_checkpoints.py` | Weight-space crossover of same-architecture checkpoints |
| `blend_search.py` | Screen blends at several ratios, benchmark the best |

## Evolution loop (old, replaced by `k1/engine`, built in Step 5)

| Tool | What it does |
|---|---|
| `evolve_hier.py` | Hierarchical L0-L5 evolution of the kick policy (state in `docs/evolution/`, start from `HANDOFF.md`) |
| `hier_supervisor.sh`, `hier_relaunch.sh` | Keep `evolve_hier.py` running overnight |
| `evolve_kick.py` | Older overnight gene search (stage 3) |
| `experience.py` | Experience repository (`docs/experience/`) |

## Data, media and visualisation

| Tool | What it does |
|---|---|
| `record_kick_clips.py` | Record good sim kicks as AMP motion clips |
| `kick_style_gallery.py` | Scripted kick-style MP4 gallery (illustration, not a policy) |
| `play_dribble.sh` | Viewer for a v22+ dribble checkpoint, one behaviour per window |
| `render_terrain_gallery.py` | Images of each sub-terrain type |
| `terrain_explorer.py` | Interactive terrain explorer (Viser) |

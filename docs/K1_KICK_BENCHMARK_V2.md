# K1 kick benchmark v2

Built 2026-10-07 after runswift's kick and goal-scoring comparisons disagreed
with our benchmark (see `K1_KICK_LESSONS.md` §9). Purpose: measure the policy
**as the robot runs it**, per situation, fairly to B-Human, with nothing averaged
or excluded away.

## What changed from v1 (`kick_benchmark.py`)

| | v1 | v2 |
|---|---|---|
| Action path | training path (no target clip) | runner path: joint-target clip `Q_ABS_LIMITS`, B-Human torque clip, lost-ball rule, scripted head |
| Ball frame | trunk ground projection | between the feet (runswift vision `base_link`, user 2026-10-07), 2 cm jitter |
| Engines | GPU sim only | GPU sim (many robots) **and** the runner's own code in the runner's CPU MuJoCo bridge via runswift's harness; they must roughly agree |
| Speed caps | random | fixed **low** 0.5 / 0.3 / 0.6 (runswift's) and **high** 2.0 / 1.5 / 1.5 (our limit), reported separately |
| Perception | camera, perfect | **camera** (main), **world** (fresh ball at any bearing, as from team ball / localisation), perfect (diagnostic) |
| Motor delay | trained 10-40 ms only | **zero** and **typical** (10-40 ms) |
| Falls | after the first 2 s only | **every fall from t = 0** (runswift's test: tilt > 60° or root < 0.25 m, every step), split by situation and ball bearing |
| Situations | full loop, close start, probes | near-ball grid (runswift), close any-bearing, approach 2-10 m any bearing incl. behind, goal grid (runswift), full loop + push / bumps / moving / late detections |
| First touch | ignored nudges (< 1 m/s) | runswift's first strike (≥ 0.5 m/s, nudges count) **and** our first kick |
| Statistics | point values, two seeds | mean with bootstrap 95 % CI and n for every metric; "better" only when CIs separate |
| B-Human | one comparison | **kick league** (near-ball tracks, both kick policies with their own deployment contracts) and **system league** (goal grid: ours end-to-end vs B-Human walk + scripted navigator + kick, labelled as such) |

## Tracks (GPU engine, `scripts/tools/kick_bench2.py`)

| Track | Setup | Perception × delay (full) |
|---|---|---|
| near_grid | runswift's 36 near-ball tasks × 3 yaw perturbations, standing start, 12 s | perfect, camera × typical, zero |
| close_any | ball 0.4-1.5 m any bearing, walking start, 12 s | camera, perfect × typical |
| approach | ball 2-10 m any bearing, standing start, 20 s; metrics by bearing (front < 60°, side, behind > 120°) | camera × typical, zero; world × typical |
| goal_grid | runswift's 90 approaches (manifest), budgets 45-115 s, goal line ±1.25 m, touchline 4.5 m | camera, world × typical |
| full_loop | 30 s loop, walking start; variants push 0.6 m/s, moving ball, late detections 60-120 ms, bumps | camera × typical |

Every run: half the robots at low caps, half at high caps. One episode per robot.

Metrics: first touch ≤ 15° (+ error, speed), first kick (share, time, ≤ 20°), all
kicks ≤ 20°, long-kick 3D speed and speed / needed, short / medium stop distance,
goals, falls (any, first 2 s, by bearing, before ball contact), knee torque peak
at kicks, torque saturation share, joint-stop share (targets beyond the joint
range, clipped), approach speed and cap use, height and pitch above 1 m/s,
action rate, double touches.

`quick` (~3 min): near_grid (perfect, camera), close_any, approach, full_loop.
`full` (~20-30 min per policy).

## CPU engine (`scripts/tools/kick_bench2_cpu.py`)

runswift's harness (`runswift/benchmarks/kick_policies`) with our conditions
patched in: our ONNX, caps, between-feet ball with camera / world / perfect
perception; the policy runs through `k1_policy_runner`'s `KickLoopPolicy`
(now with the lost-ball rule). B-Human uses runswift's adapters unchanged (its
goal-grid navigator hard-codes low caps). No motor delay in this engine.

## Commands

```bash
uv run python scripts/tools/kick_bench2.py run NAME CK_OR_bhuman --size quick|full
.venv/bin/python scripts/tools/kick_bench2_cpu.py NAME ONNX_OR_bhuman --track near|goal|both \
  --caps low|high --perception camera|world|perfect
uv run python scripts/tools/kick_bench2.py compare NAME_A NAME_B
uv run python scripts/tools/kick_bench2_report.py NAME [NAME ...] > report.md
```

Results: `docs/benchmarks_v2/NAME.json`, `docs/benchmarks_v2/cpu/NAME/`.

## Not yet in v2

- Real motor delay and loaded torque limits (user: not now); torque limits are
  B-Human's clip in one table (`env_cfgs.LEG_TORQUE_CLIP`).
- Robot-log replay / calibration (§7 of the proposal).
- Promotion gates for the evolution loop (v1 still drives it until v2 baselines
  exist).
- B-Human system league at high caps (navigator caps are hard-coded upstream).

## Engine agreement check (2026-10-07)

x4, near grid, perfect ball, zero delay, light ball: first touch ≤ 15° GPU
10.2 % [4.6, 16] vs CPU 2.8 % (3/108); error p50 24.9° vs 31.9°; speed 2.45 vs
2.62 m/s. Both say the same thing (x4 cannot aim under the deployed path); the
CPU value sits just below the GPU interval.

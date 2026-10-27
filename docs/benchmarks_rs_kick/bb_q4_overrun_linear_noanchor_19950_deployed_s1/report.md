# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_02-42-52_q4_overrun_linear_noanchor/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.855** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.79 ± 0.55 (1.66) |
| Direction error [°] | 5.22 ± 3.34 (4.74) |
| Avg ball speed [m/s] | 2.30 ± 0.36 (2.39) |
| Peak ball speed [m/s] | 5.03 ± 0.99 (5.47) |
| Distance [m] | 2.18 ± 0.66 (2.32) |
| Path length [m] | 2.19 ± 0.66 (2.33) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.875 | 50/50 | 0 | 49 | 1.26 ± 0.26 (1.28) | 4.42 ± 3.46 (3.59) | 2.29 ± 0.36 (2.40) | 5.04 ± 1.00 (5.57) | 2.15 ± 0.62 (2.31) |
| left | p | 0.864 | 50/50 | 0 | 49 | 1.70 ± 0.35 (1.62) | 5.76 ± 3.21 (5.83) | 2.31 ± 0.37 (2.34) | 5.03 ± 1.00 (5.35) | 2.21 ± 0.72 (2.25) |
| back | p | 0.822 | 50/50 | 0 | 50 | 2.51 ± 0.31 (2.49) | 6.00 ± 3.34 (5.35) | 2.36 ± 0.34 (2.43) | 5.18 ± 0.91 (5.60) | 2.29 ± 0.61 (2.46) |
| right | p | 0.859 | 50/50 | 0 | 50 | 1.69 ± 0.34 (1.63) | 4.69 ± 3.05 (4.37) | 2.25 ± 0.37 (2.36) | 4.86 ± 1.03 (5.43) | 2.08 ± 0.68 (2.29) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.852 | 100/100 | 0 | 98 | 1.78 ± 0.55 (1.60) | 5.21 ± 3.39 (4.64) | 2.31 ± 0.36 (2.41) | 5.07 ± 0.97 (5.54) | 2.21 ± 0.66 (2.34) |
| right | p | 0.859 | 100/100 | 0 | 100 | 1.79 ± 0.56 (1.68) | 5.22 ± 3.29 (4.91) | 2.29 ± 0.36 (2.37) | 4.98 ± 1.01 (5.45) | 2.15 ± 0.66 (2.28) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.863 | 25/25 | 0 | 24 | 1.24 ± 0.27 (1.28) | 5.01 ± 3.94 (4.02) | 2.24 ± 0.31 (2.30) | 4.97 ± 0.92 (5.35) | 2.10 ± 0.55 (2.23) |
| forward/right | p | 0.887 | 25/25 | 0 | 25 | 1.28 ± 0.25 (1.30) | 3.82 ± 2.78 (3.12) | 2.34 ± 0.39 (2.46) | 5.10 ± 1.06 (5.65) | 2.21 ± 0.68 (2.37) |
| left/left | p | 0.861 | 25/25 | 0 | 24 | 1.62 ± 0.33 (1.58) | 6.18 ± 3.28 (5.87) | 2.35 ± 0.37 (2.38) | 5.13 ± 1.00 (5.38) | 2.29 ± 0.73 (2.28) |
| left/right | p | 0.867 | 25/25 | 0 | 25 | 1.78 ± 0.35 (1.78) | 5.33 ± 3.08 (5.61) | 2.27 ± 0.37 (2.27) | 4.93 ± 0.99 (5.19) | 2.12 ± 0.70 (2.19) |
| back/left | p | 0.822 | 25/25 | 0 | 25 | 2.51 ± 0.24 (2.54) | 5.93 ± 3.29 (6.36) | 2.40 ± 0.38 (2.43) | 5.26 ± 0.93 (5.63) | 2.35 ± 0.65 (2.46) |
| back/right | p | 0.822 | 25/25 | 0 | 25 | 2.51 ± 0.37 (2.38) | 6.06 ± 3.38 (5.12) | 2.33 ± 0.30 (2.43) | 5.11 ± 0.87 (5.56) | 2.22 ± 0.55 (2.46) |
| right/left | p | 0.861 | 25/25 | 0 | 25 | 1.76 ± 0.34 (1.76) | 3.69 ± 2.25 (3.34) | 2.27 ± 0.35 (2.43) | 4.93 ± 0.98 (5.59) | 2.11 ± 0.66 (2.32) |
| right/right | p | 0.858 | 25/25 | 0 | 25 | 1.61 ± 0.32 (1.58) | 5.68 ± 3.41 (5.38) | 2.23 ± 0.38 (2.33) | 4.79 ± 1.07 (5.30) | 2.06 ± 0.70 (2.25) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.892 | 4.9 | 5.75 | 2.63 |
| p | normal | 0.818 | 5.5 | 4.30 | 1.74 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.760 | 0.13 | 2.44 ± 0.78 (2.29) | 3.78 | 1.39 |
| p | medium | 20 | 0.885 | 0.76 | 1.21 ± 0.17 (1.23) | 3.86 | 1.47 |
| p | strong | 126 | 0.891 | 0.77 | - | 5.75 | 2.64 |

## Notes

- p: score 0.855, 200/200 kicked, 0 fell; worst sector back (0.822).

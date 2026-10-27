# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_02-42-52_q4_overrun_linear_noanchor/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.856** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.81 ± 0.54 (1.72) |
| Direction error [°] | 5.02 ± 3.31 (4.79) |
| Avg ball speed [m/s] | 2.25 ± 0.35 (2.32) |
| Peak ball speed [m/s] | 5.01 ± 1.01 (5.48) |
| Distance [m] | 2.08 ± 0.63 (2.18) |
| Path length [m] | 2.09 ± 0.64 (2.20) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.856 | 50/50 | 0 | 50 | 1.28 ± 0.24 (1.30) | 4.99 ± 2.98 (5.08) | 2.23 ± 0.41 (2.22) | 4.93 ± 1.13 (5.44) | 2.03 ± 0.70 (1.92) |
| left | p | 0.888 | 50/50 | 0 | 49 | 1.74 ± 0.35 (1.74) | 4.44 ± 4.01 (3.59) | 2.32 ± 0.32 (2.39) | 5.20 ± 0.95 (5.49) | 2.20 ± 0.62 (2.27) |
| back | p | 0.821 | 50/50 | 0 | 50 | 2.49 ± 0.34 (2.42) | 6.00 ± 3.03 (5.71) | 2.27 ± 0.30 (2.35) | 5.07 ± 0.93 (5.52) | 2.14 ± 0.59 (2.32) |
| right | p | 0.858 | 50/50 | 0 | 50 | 1.73 ± 0.34 (1.71) | 4.66 ± 2.89 (4.34) | 2.18 ± 0.33 (2.29) | 4.84 ± 0.97 (5.30) | 1.95 ± 0.58 (2.10) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.855 | 100/100 | 0 | 99 | 1.82 ± 0.56 (1.73) | 5.27 ± 3.51 (4.86) | 2.26 ± 0.34 (2.33) | 5.04 ± 1.00 (5.50) | 2.10 ± 0.63 (2.25) |
| right | p | 0.857 | 100/100 | 0 | 100 | 1.80 ± 0.52 (1.72) | 4.77 ± 3.08 (4.71) | 2.24 ± 0.36 (2.30) | 4.98 ± 1.01 (5.45) | 2.06 ± 0.64 (2.08) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.867 | 25/25 | 0 | 25 | 1.28 ± 0.24 (1.30) | 4.62 ± 2.63 (4.62) | 2.24 ± 0.41 (2.33) | 4.97 ± 1.17 (5.53) | 2.06 ± 0.72 (2.16) |
| forward/right | p | 0.844 | 25/25 | 0 | 25 | 1.27 ± 0.24 (1.30) | 5.35 ± 3.24 (5.41) | 2.22 ± 0.42 (2.11) | 4.90 ± 1.08 (5.14) | 2.00 ± 0.68 (1.76) |
| left/left | p | 0.875 | 25/25 | 0 | 24 | 1.65 ± 0.36 (1.70) | 5.51 ± 5.02 (3.74) | 2.30 ± 0.33 (2.34) | 5.13 ± 0.98 (5.48) | 2.18 ± 0.65 (2.20) |
| left/right | p | 0.901 | 25/25 | 0 | 25 | 1.83 ± 0.32 (1.92) | 3.37 ± 2.16 (2.80) | 2.34 ± 0.31 (2.42) | 5.27 ± 0.92 (5.50) | 2.22 ± 0.59 (2.30) |
| back/left | p | 0.814 | 25/25 | 0 | 25 | 2.53 ± 0.36 (2.44) | 6.16 ± 2.64 (5.77) | 2.31 ± 0.25 (2.33) | 5.12 ± 0.81 (5.51) | 2.19 ± 0.53 (2.33) |
| back/right | p | 0.829 | 25/25 | 0 | 25 | 2.46 ± 0.31 (2.38) | 5.84 ± 3.37 (5.53) | 2.23 ± 0.35 (2.39) | 5.01 ± 1.03 (5.53) | 2.09 ± 0.65 (2.26) |
| right/left | p | 0.863 | 25/25 | 0 | 25 | 1.83 ± 0.33 (1.80) | 4.79 ± 2.96 (4.36) | 2.19 ± 0.33 (2.31) | 4.94 ± 1.00 (5.47) | 1.99 ± 0.57 (2.18) |
| right/right | p | 0.854 | 25/25 | 0 | 25 | 1.63 ± 0.31 (1.60) | 4.53 ± 2.80 (3.91) | 2.17 ± 0.32 (2.27) | 4.74 ± 0.94 (4.97) | 1.91 ± 0.59 (1.90) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.895 | 4.8 | 5.75 | 2.51 |
| p | normal | 0.816 | 5.2 | 4.27 | 1.66 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.764 | 0.12 | 2.37 ± 0.75 (2.10) | 3.75 | 1.35 |
| p | medium | 16 | 0.897 | 0.83 | 1.17 ± 0.12 (1.13) | 3.80 | 1.40 |
| p | strong | 126 | 0.893 | 0.77 | - | 5.74 | 2.50 |

## Notes

- p: score 0.856, 200/200 kicked, 0 fell; worst sector back (0.821).

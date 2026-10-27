# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_02-42-52_q4_overrun_linear_noanchor/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.828** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 182 |
| Weak kicks (< 0.3 m) | 4 |
| Time to kick [s] | 1.54 ± 0.52 (1.46) |
| Direction error [°] | 8.11 ± 10.79 (6.59) |
| Avg ball speed [m/s] | 1.66 ± 0.45 (1.65) |
| Peak ball speed [m/s] | 3.49 ± 0.98 (3.49) |
| Distance [m] | 1.22 ± 0.56 (1.12) |
| Path length [m] | 1.23 ± 0.57 (1.13) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.829 | 50/50 | 0 | 48 | 1.02 ± 0.22 (1.05) | 6.55 ± 4.01 (6.13) | 1.42 ± 0.37 (1.36) | 3.02 ± 0.80 (2.88) | 0.90 ± 0.45 (0.75) |
| left | p | 0.834 | 50/50 | 0 | 44 | 1.48 ± 0.36 (1.48) | 8.17 ± 5.20 (7.46) | 1.76 ± 0.38 (1.84) | 3.70 ± 0.82 (3.80) | 1.33 ± 0.49 (1.27) |
| back | p | 0.828 | 50/50 | 0 | 48 | 2.18 ± 0.29 (2.16) | 9.56 ± 19.74 (6.02) | 1.74 ± 0.52 (1.83) | 3.69 ± 1.16 (3.94) | 1.39 ± 0.64 (1.49) |
| right | p | 0.822 | 50/50 | 0 | 42 | 1.46 ± 0.35 (1.44) | 8.18 ± 5.30 (7.98) | 1.71 ± 0.42 (1.70) | 3.58 ± 0.92 (3.57) | 1.27 ± 0.53 (1.29) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.821 | 100/100 | 0 | 90 | 1.54 ± 0.52 (1.46) | 9.28 ± 14.46 (7.05) | 1.68 ± 0.48 (1.74) | 3.54 ± 1.05 (3.65) | 1.26 ± 0.60 (1.21) |
| right | p | 0.836 | 100/100 | 0 | 92 | 1.53 ± 0.52 (1.45) | 6.95 ± 4.56 (6.17) | 1.64 ± 0.41 (1.61) | 3.45 ± 0.89 (3.41) | 1.18 ± 0.53 (1.09) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.818 | 25/25 | 0 | 23 | 1.03 ± 0.23 (1.08) | 7.13 ± 4.14 (6.42) | 1.43 ± 0.29 (1.38) | 3.03 ± 0.64 (2.91) | 0.91 ± 0.38 (0.81) |
| forward/right | p | 0.841 | 25/25 | 0 | 25 | 1.01 ± 0.21 (1.04) | 5.98 ± 3.79 (4.86) | 1.41 ± 0.43 (1.35) | 3.01 ± 0.93 (2.81) | 0.90 ± 0.51 (0.73) |
| left/left | p | 0.817 | 25/25 | 0 | 21 | 1.36 ± 0.36 (1.40) | 9.52 ± 5.09 (9.73) | 1.71 ± 0.40 (1.83) | 3.56 ± 0.84 (3.78) | 1.24 ± 0.48 (1.24) |
| left/right | p | 0.851 | 25/25 | 0 | 23 | 1.60 ± 0.33 (1.52) | 6.81 ± 4.96 (5.91) | 1.81 ± 0.35 (1.84) | 3.84 ± 0.78 (3.93) | 1.41 ± 0.48 (1.49) |
| back/left | p | 0.816 | 25/25 | 0 | 23 | 2.19 ± 0.29 (2.16) | 13.40 ± 27.24 (6.87) | 1.81 ± 0.66 (2.02) | 3.84 ± 1.45 (4.30) | 1.54 ± 0.77 (1.72) |
| back/right | p | 0.841 | 25/25 | 0 | 25 | 2.18 ± 0.28 (2.16) | 5.71 ± 2.74 (5.22) | 1.68 ± 0.31 (1.65) | 3.53 ± 0.72 (3.44) | 1.24 ± 0.43 (1.10) |
| right/left | p | 0.834 | 25/25 | 0 | 23 | 1.57 ± 0.34 (1.54) | 7.08 ± 5.00 (5.62) | 1.78 ± 0.41 (1.83) | 3.73 ± 0.90 (3.90) | 1.35 ± 0.51 (1.46) |
| right/right | p | 0.810 | 25/25 | 0 | 19 | 1.36 ± 0.33 (1.38) | 9.28 ± 5.36 (8.81) | 1.65 ± 0.42 (1.50) | 3.43 ± 0.92 (3.00) | 1.19 ± 0.55 (0.92) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.838 | 6.5 | 4.03 | 1.52 |
| p | normal | 0.819 | 9.7 | 2.96 | 0.93 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.799 | 0.45 | 1.60 ± 0.59 (1.45) | 2.52 | 0.69 |
| p | medium | 16 | 0.859 | 0.82 | 0.83 ± 0.13 (0.83) | 2.70 | 0.76 |
| p | strong | 126 | 0.838 | 0.54 | - | 4.04 | 1.53 |

## Notes

- p: score 0.828, 200/200 kicked, 0 fell; worst sector right (0.822).

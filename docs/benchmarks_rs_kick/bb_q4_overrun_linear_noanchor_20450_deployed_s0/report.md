# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_02-42-52_q4_overrun_linear_noanchor/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.840** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 181 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.81 ± 0.56 (1.72) |
| Direction error [°] | 8.04 ± 10.26 (6.83) |
| Avg ball speed [m/s] | 2.42 ± 0.57 (2.58) |
| Peak ball speed [m/s] | 5.21 ± 1.38 (5.82) |
| Distance [m] | 2.35 ± 0.95 (2.59) |
| Path length [m] | 2.36 ± 0.95 (2.61) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.870 | 50/50 | 0 | 49 | 1.26 ± 0.24 (1.30) | 3.83 ± 3.59 (2.79) | 2.24 ± 0.45 (2.36) | 4.89 ± 1.22 (5.28) | 2.02 ± 0.76 (1.98) |
| left | p | 0.851 | 50/50 | 0 | 42 | 1.74 ± 0.37 (1.72) | 9.11 ± 5.79 (8.88) | 2.52 ± 0.54 (2.65) | 5.43 ± 1.26 (5.98) | 2.50 ± 0.87 (2.77) |
| back | p | 0.796 | 50/50 | 0 | 43 | 2.53 ± 0.33 (2.45) | 11.93 ± 17.76 (10.21) | 2.56 ± 0.67 (2.76) | 5.47 ± 1.56 (6.22) | 2.63 ± 1.11 (3.08) |
| right | p | 0.843 | 50/50 | 0 | 47 | 1.74 ± 0.36 (1.72) | 7.29 ± 4.93 (6.99) | 2.37 ± 0.57 (2.53) | 5.07 ± 1.35 (5.58) | 2.24 ± 0.91 (2.45) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.837 | 100/100 | 0 | 88 | 1.81 ± 0.56 (1.72) | 8.94 ± 13.55 (6.85) | 2.42 ± 0.59 (2.53) | 5.18 ± 1.39 (5.71) | 2.33 ± 0.97 (2.57) |
| right | p | 0.843 | 100/100 | 0 | 93 | 1.82 ± 0.56 (1.73) | 7.14 ± 5.02 (6.80) | 2.43 ± 0.56 (2.61) | 5.25 ± 1.36 (5.97) | 2.36 ± 0.93 (2.65) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.874 | 25/25 | 0 | 24 | 1.26 ± 0.23 (1.30) | 4.09 ± 3.83 (3.18) | 2.21 ± 0.45 (2.36) | 4.81 ± 1.22 (5.38) | 1.96 ± 0.76 (1.96) |
| forward/right | p | 0.867 | 25/25 | 0 | 25 | 1.26 ± 0.24 (1.30) | 3.56 ± 3.32 (2.58) | 2.28 ± 0.45 (2.47) | 4.96 ± 1.22 (5.18) | 2.07 ± 0.75 (2.01) |
| left/left | p | 0.841 | 25/25 | 0 | 19 | 1.61 ± 0.35 (1.64) | 9.65 ± 6.63 (9.20) | 2.49 ± 0.54 (2.60) | 5.30 ± 1.25 (5.90) | 2.45 ± 0.90 (2.70) |
| left/right | p | 0.861 | 25/25 | 0 | 23 | 1.87 ± 0.34 (1.96) | 8.56 ± 4.74 (8.44) | 2.54 ± 0.54 (2.67) | 5.57 ± 1.25 (5.99) | 2.56 ± 0.83 (2.80) |
| back/left | p | 0.783 | 25/25 | 0 | 21 | 2.53 ± 0.32 (2.48) | 14.89 ± 24.39 (11.10) | 2.57 ± 0.70 (2.73) | 5.49 ± 1.62 (6.12) | 2.66 ± 1.15 (3.03) |
| back/right | p | 0.808 | 25/25 | 0 | 22 | 2.52 ± 0.33 (2.42) | 8.97 ± 4.33 (8.36) | 2.54 ± 0.62 (2.79) | 5.44 ± 1.49 (6.24) | 2.59 ± 1.07 (3.13) |
| right/left | p | 0.848 | 25/25 | 0 | 24 | 1.85 ± 0.33 (1.80) | 7.13 ± 4.28 (6.86) | 2.39 ± 0.58 (2.52) | 5.14 ± 1.34 (5.48) | 2.25 ± 0.88 (2.45) |
| right/right | p | 0.837 | 25/25 | 0 | 23 | 1.62 ± 0.35 (1.62) | 7.45 ± 5.49 (7.12) | 2.35 ± 0.55 (2.53) | 5.01 ± 1.37 (5.82) | 2.22 ± 0.94 (2.46) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.869 | 8.4 | 6.22 | 2.98 |
| p | normal | 0.811 | 7.6 | 4.21 | 1.71 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.767 | 0.17 | 2.21 ± 0.73 (2.01) | 3.48 | 1.21 |
| p | medium | 16 | 0.884 | 0.85 | 1.13 ± 0.15 (1.13) | 3.65 | 1.31 |
| p | strong | 126 | 0.868 | 0.83 | - | 6.21 | 3.00 |

## Notes

- p: score 0.840, 200/200 kicked, 0 fell; worst sector back (0.796).

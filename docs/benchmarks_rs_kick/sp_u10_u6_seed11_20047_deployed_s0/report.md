# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_13-42-50_u10_u6_seed11/model_20047.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.784** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 165 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 2.15 ± 1.86 (1.75) |
| Direction error [°] | 20.63 ± 40.93 (5.44) |
| Avg ball speed [m/s] | 2.04 ± 0.67 (2.24) |
| Peak ball speed [m/s] | 4.45 ± 1.58 (4.98) |
| Distance [m] | 1.83 ± 0.85 (1.94) |
| Path length [m] | 1.84 ± 0.86 (1.95) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.793 | 50/50 | 0 | 41 | 1.77 ± 1.81 (1.33) | 10.25 ± 17.34 (4.80) | 1.95 ± 0.71 (2.03) | 4.21 ± 1.67 (4.19) | 1.68 ± 0.89 (1.64) |
| left | p | 0.817 | 50/50 | 0 | 43 | 2.03 ± 1.86 (1.79) | 17.48 ± 33.62 (5.52) | 2.10 ± 0.60 (2.31) | 4.60 ± 1.46 (5.25) | 1.90 ± 0.81 (2.12) |
| back | p | 0.731 | 50/50 | 0 | 39 | 2.73 ± 1.79 (2.53) | 36.23 ± 61.11 (6.31) | 2.06 ± 0.73 (2.31) | 4.48 ± 1.67 (5.00) | 1.89 ± 0.89 (2.00) |
| right | p | 0.795 | 50/50 | 0 | 42 | 2.07 ± 1.82 (1.75) | 18.58 ± 34.20 (5.42) | 2.07 ± 0.63 (2.19) | 4.53 ± 1.48 (5.09) | 1.85 ± 0.81 (1.99) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.807 | 100/100 | 0 | 87 | 1.92 ± 1.32 (1.74) | 18.90 ± 40.04 (5.30) | 2.12 ± 0.63 (2.33) | 4.62 ± 1.48 (5.25) | 1.92 ± 0.82 (2.12) |
| right | p | 0.760 | 100/100 | 0 | 78 | 2.38 ± 2.25 (1.78) | 22.37 ± 41.72 (5.86) | 1.97 ± 0.71 (2.16) | 4.29 ± 1.66 (4.50) | 1.74 ± 0.88 (1.80) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.831 | 25/25 | 0 | 23 | 1.55 ± 1.38 (1.30) | 6.46 ± 10.36 (3.97) | 2.14 ± 0.65 (2.32) | 4.60 ± 1.53 (4.47) | 1.91 ± 0.83 (1.82) |
| forward/right | p | 0.754 | 25/25 | 0 | 18 | 1.99 ± 2.13 (1.36) | 14.03 ± 21.58 (6.01) | 1.75 ± 0.71 (1.97) | 3.81 ± 1.71 (3.99) | 1.44 ± 0.89 (1.55) |
| left/left | p | 0.854 | 25/25 | 0 | 23 | 1.59 ± 0.42 (1.66) | 11.93 ± 22.08 (5.51) | 2.20 ± 0.51 (2.36) | 4.81 ± 1.24 (5.46) | 2.02 ± 0.71 (2.26) |
| left/right | p | 0.781 | 25/25 | 0 | 20 | 2.46 ± 2.52 (1.96) | 23.03 ± 41.37 (6.40) | 2.00 ± 0.67 (2.16) | 4.38 ± 1.61 (5.14) | 1.77 ± 0.89 (1.97) |
| back/left | p | 0.737 | 25/25 | 0 | 20 | 2.72 ± 1.93 (2.52) | 36.66 ± 61.15 (7.61) | 2.10 ± 0.69 (2.34) | 4.58 ± 1.59 (5.16) | 1.93 ± 0.90 (2.02) |
| back/right | p | 0.725 | 25/25 | 0 | 19 | 2.74 ± 1.64 (2.66) | 35.81 ± 61.06 (4.41) | 2.01 ± 0.76 (2.24) | 4.38 ± 1.74 (4.82) | 1.84 ± 0.87 (1.96) |
| right/left | p | 0.809 | 25/25 | 0 | 21 | 1.82 ± 0.50 (1.80) | 20.56 ± 39.47 (4.75) | 2.05 ± 0.63 (2.19) | 4.48 ± 1.52 (5.09) | 1.82 ± 0.82 (2.04) |
| right/right | p | 0.781 | 25/25 | 0 | 21 | 2.33 ± 2.51 (1.74) | 16.59 ± 27.81 (6.00) | 2.09 ± 0.63 (2.15) | 4.59 ± 1.45 (5.09) | 1.88 ± 0.79 (1.83) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.814 | 19.6 | 5.11 | 2.19 |
| p | normal | 0.754 | 21.7 | 3.79 | 1.46 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.711 | 0.17 | 2.19 ± 1.01 (2.06) | 3.44 | 1.28 |
| p | medium | 16 | 0.839 | 0.74 | 1.23 ± 0.21 (1.25) | 3.98 | 1.56 |
| p | strong | 126 | 0.811 | 0.66 | - | 4.98 | 2.12 |

## Notes

- p: score 0.784, 200/200 kicked, 0 fell; worst sector back (0.731).

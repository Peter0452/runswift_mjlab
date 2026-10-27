# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-08-39_u2_aim_sigma02/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.840** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 193 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.53 ± 0.49 (1.46) |
| Direction error [°] | 6.36 ± 10.22 (4.95) |
| Avg ball speed [m/s] | 2.22 ± 0.36 (2.21) |
| Peak ball speed [m/s] | 4.63 ± 0.81 (4.58) |
| Distance [m] | 2.07 ± 0.55 (2.02) |
| Path length [m] | 2.08 ± 0.55 (2.03) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.823 | 50/50 | 0 | 47 | 1.02 ± 0.23 (1.09) | 5.89 ± 4.13 (5.08) | 2.06 ± 0.26 (2.03) | 4.26 ± 0.60 (4.14) | 1.78 ± 0.43 (1.72) |
| left | p | 0.867 | 50/50 | 0 | 50 | 1.48 ± 0.34 (1.48) | 4.98 ± 3.54 (4.42) | 2.27 ± 0.27 (2.29) | 4.78 ± 0.63 (4.86) | 2.16 ± 0.47 (2.19) |
| back | p | 0.834 | 50/50 | 0 | 47 | 2.15 ± 0.23 (2.13) | 8.64 ± 19.06 (5.99) | 2.25 ± 0.51 (2.30) | 4.73 ± 1.10 (4.83) | 2.19 ± 0.66 (2.19) |
| right | p | 0.836 | 50/50 | 0 | 49 | 1.46 ± 0.33 (1.44) | 5.92 ± 4.16 (4.84) | 2.28 ± 0.29 (2.26) | 4.75 ± 0.69 (4.79) | 2.14 ± 0.49 (2.10) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.847 | 100/100 | 0 | 99 | 1.53 ± 0.50 (1.45) | 5.49 ± 3.93 (4.69) | 2.24 ± 0.28 (2.25) | 4.68 ± 0.67 (4.72) | 2.10 ± 0.50 (2.08) |
| right | p | 0.834 | 100/100 | 0 | 94 | 1.52 ± 0.49 (1.46) | 7.23 ± 13.85 (5.48) | 2.20 ± 0.43 (2.16) | 4.57 ± 0.93 (4.43) | 2.04 ± 0.59 (1.96) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.833 | 25/25 | 0 | 24 | 1.03 ± 0.23 (1.08) | 5.64 ± 3.79 (5.08) | 2.14 ± 0.24 (2.10) | 4.42 ± 0.58 (4.32) | 1.89 ± 0.42 (1.81) |
| forward/right | p | 0.813 | 25/25 | 0 | 23 | 1.02 ± 0.24 (1.10) | 6.14 ± 4.42 (5.20) | 1.98 ± 0.27 (1.95) | 4.10 ± 0.59 (3.98) | 1.68 ± 0.42 (1.59) |
| left/left | p | 0.858 | 25/25 | 0 | 25 | 1.38 ± 0.33 (1.44) | 5.51 ± 4.20 (4.59) | 2.17 ± 0.27 (2.17) | 4.58 ± 0.65 (4.70) | 2.02 ± 0.47 (2.05) |
| left/right | p | 0.876 | 25/25 | 0 | 25 | 1.58 ± 0.32 (1.58) | 4.45 ± 2.63 (4.37) | 2.37 ± 0.24 (2.41) | 4.98 ± 0.54 (5.12) | 2.30 ± 0.42 (2.40) |
| back/left | p | 0.848 | 25/25 | 0 | 25 | 2.18 ± 0.24 (2.14) | 5.53 ± 3.66 (5.89) | 2.33 ± 0.27 (2.33) | 4.92 ± 0.63 (4.95) | 2.29 ± 0.52 (2.26) |
| back/right | p | 0.821 | 25/25 | 0 | 22 | 2.13 ± 0.21 (2.10) | 11.76 ± 26.34 (6.32) | 2.17 ± 0.66 (2.24) | 4.54 ± 1.40 (4.79) | 2.09 ± 0.77 (2.05) |
| right/left | p | 0.848 | 25/25 | 0 | 25 | 1.56 ± 0.30 (1.54) | 5.27 ± 4.05 (3.97) | 2.30 ± 0.29 (2.36) | 4.82 ± 0.69 (5.09) | 2.18 ± 0.51 (2.28) |
| right/right | p | 0.824 | 25/25 | 0 | 24 | 1.36 ± 0.32 (1.38) | 6.56 ± 4.16 (6.91) | 2.26 ± 0.30 (2.15) | 4.68 ± 0.68 (4.39) | 2.09 ± 0.48 (2.00) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.875 | 5.5 | 4.99 | 2.31 |
| p | normal | 0.805 | 7.2 | 4.27 | 1.82 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.760 | 0.08 | 2.48 ± 0.82 (2.37) | 3.94 | 1.58 |
| p | medium | 16 | 0.864 | 0.71 | 1.28 ± 0.17 (1.33) | 4.14 | 1.71 |
| p | strong | 126 | 0.874 | 0.67 | - | 5.01 | 2.34 |

## Notes

- p: score 0.840, 200/200 kicked, 0 fell; worst sector forward (0.823).

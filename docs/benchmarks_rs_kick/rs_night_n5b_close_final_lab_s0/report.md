# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_08-51-51_night_n5b_close/model_19849.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.945** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.53 ± 0.49 (1.48) |
| Direction error [°] | 5.94 ± 12.34 (4.74) |
| Avg ball speed [m/s] | 2.05 ± 0.38 (2.15) |
| Peak ball speed [m/s] | 4.43 ± 0.91 (4.69) |
| Distance [m] | 1.77 ± 0.58 (1.84) |
| Path length [m] | 1.78 ± 0.58 (1.86) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.956 | 50/50 | 0 | 50 | 1.03 ± 0.24 (1.06) | 4.41 ± 2.76 (4.12) | 1.81 ± 0.38 (1.72) | 3.86 ± 0.84 (3.66) | 1.39 ± 0.53 (1.25) |
| left | p | 0.940 | 50/50 | 0 | 49 | 1.48 ± 0.32 (1.48) | 6.03 ± 3.21 (5.99) | 2.12 ± 0.28 (2.19) | 4.61 ± 0.74 (4.83) | 1.88 ± 0.49 (1.94) |
| back | p | 0.946 | 50/50 | 0 | 49 | 2.15 ± 0.24 (2.12) | 7.23 ± 23.95 (3.00) | 2.22 ± 0.39 (2.37) | 4.77 ± 0.96 (5.19) | 2.03 ± 0.59 (2.22) |
| right | p | 0.939 | 50/50 | 0 | 50 | 1.47 ± 0.32 (1.46) | 6.10 ± 3.64 (5.41) | 2.06 ± 0.32 (2.15) | 4.46 ± 0.80 (4.79) | 1.77 ± 0.50 (1.78) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.945 | 100/100 | 0 | 100 | 1.54 ± 0.50 (1.48) | 5.18 ± 3.23 (4.84) | 2.07 ± 0.35 (2.13) | 4.46 ± 0.86 (4.64) | 1.79 ± 0.57 (1.84) |
| right | p | 0.945 | 100/100 | 0 | 98 | 1.53 ± 0.48 (1.46) | 6.70 ± 17.11 (4.39) | 2.04 ± 0.40 (2.16) | 4.39 ± 0.95 (4.72) | 1.75 ± 0.59 (1.82) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.951 | 25/25 | 0 | 25 | 1.04 ± 0.24 (1.08) | 4.86 ± 2.52 (5.09) | 1.85 ± 0.34 (1.79) | 3.95 ± 0.73 (3.67) | 1.43 ± 0.46 (1.24) |
| forward/right | p | 0.960 | 25/25 | 0 | 25 | 1.03 ± 0.23 (1.04) | 3.96 ± 2.91 (3.23) | 1.76 ± 0.41 (1.71) | 3.77 ± 0.93 (3.57) | 1.35 ± 0.59 (1.26) |
| left/left | p | 0.941 | 25/25 | 0 | 25 | 1.38 ± 0.32 (1.44) | 5.86 ± 3.09 (6.06) | 2.06 ± 0.29 (2.14) | 4.46 ± 0.78 (4.63) | 1.79 ± 0.50 (1.91) |
| left/right | p | 0.938 | 25/25 | 0 | 24 | 1.59 ± 0.30 (1.56) | 6.19 ± 3.31 (5.92) | 2.19 ± 0.24 (2.23) | 4.76 ± 0.67 (4.99) | 1.98 ± 0.46 (1.97) |
| back/left | p | 0.950 | 25/25 | 0 | 25 | 2.19 ± 0.25 (2.12) | 3.83 ± 2.88 (3.36) | 2.29 ± 0.29 (2.44) | 4.94 ± 0.78 (5.33) | 2.14 ± 0.55 (2.37) |
| back/right | p | 0.942 | 25/25 | 0 | 24 | 2.11 ± 0.23 (2.04) | 10.63 ± 33.40 (2.46) | 2.15 ± 0.46 (2.35) | 4.61 ± 1.08 (5.09) | 1.93 ± 0.60 (2.05) |
| right/left | p | 0.938 | 25/25 | 0 | 25 | 1.56 ± 0.30 (1.56) | 6.17 ± 3.76 (6.09) | 2.07 ± 0.33 (2.12) | 4.50 ± 0.83 (4.81) | 1.80 ± 0.51 (1.77) |
| right/right | p | 0.940 | 25/25 | 0 | 25 | 1.38 ± 0.32 (1.42) | 6.02 ± 3.52 (5.05) | 2.06 ± 0.30 (2.17) | 4.41 ± 0.76 (4.69) | 1.74 ± 0.47 (1.78) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.945 | 5.2 | 4.96 | 2.09 |
| p | normal | 0.945 | 6.7 | 3.89 | 1.45 |

## Notes

- p: score 0.945, 200/200 kicked, 0 fell; worst sector right (0.939).

# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_08-51-51_night_n5b_close/model_19849.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.876** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 172 |
| Weak kicks (< 0.3 m) | 17 |
| Time to kick [s] | 1.98 ± 1.47 (1.70) |
| Direction error [°] | 14.64 ± 29.44 (5.69) |
| Avg ball speed [m/s] | 2.48 ± 0.87 (2.71) |
| Peak ball speed [m/s] | 5.21 ± 1.94 (6.09) |
| Distance [m] | 2.61 ± 1.26 (3.05) |
| Path length [m] | 2.62 ± 1.27 (3.06) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.892 | 50/50 | 0 | 44 | 1.70 ± 1.85 (1.30) | 8.32 ± 11.24 (4.59) | 2.47 ± 0.78 (2.66) | 5.24 ± 1.76 (6.08) | 2.57 ± 1.14 (2.92) |
| left | p | 0.900 | 50/50 | 0 | 44 | 1.72 ± 0.51 (1.65) | 13.28 ± 26.61 (5.69) | 2.44 ± 0.85 (2.70) | 5.10 ± 1.90 (5.98) | 2.51 ± 1.25 (2.99) |
| back | p | 0.803 | 50/50 | 0 | 39 | 2.61 ± 1.51 (2.43) | 27.02 ± 45.72 (9.51) | 2.52 ± 1.08 (2.88) | 5.32 ± 2.35 (6.48) | 2.82 ± 1.50 (3.42) |
| right | p | 0.908 | 50/50 | 0 | 45 | 1.91 ± 1.45 (1.79) | 9.94 ± 18.05 (5.25) | 2.48 ± 0.73 (2.60) | 5.17 ± 1.67 (5.99) | 2.53 ± 1.11 (2.91) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.879 | 100/100 | 0 | 86 | 1.91 ± 1.21 (1.65) | 14.15 ± 27.82 (5.64) | 2.50 ± 0.87 (2.71) | 5.25 ± 1.94 (6.13) | 2.64 ± 1.26 (3.13) |
| right | p | 0.873 | 100/100 | 0 | 86 | 2.06 ± 1.68 (1.76) | 15.13 ± 30.98 (5.69) | 2.46 ± 0.88 (2.71) | 5.16 ± 1.94 (6.06) | 2.58 ± 1.27 (2.97) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.902 | 25/25 | 0 | 22 | 1.40 ± 0.80 (1.30) | 7.84 ± 10.61 (4.38) | 2.42 ± 0.82 (2.65) | 5.12 ± 1.86 (6.04) | 2.51 ± 1.15 (3.04) |
| forward/right | p | 0.883 | 25/25 | 0 | 22 | 1.99 ± 2.46 (1.32) | 8.80 ± 11.81 (4.98) | 2.52 ± 0.74 (2.67) | 5.35 ± 1.65 (6.12) | 2.64 ± 1.14 (2.87) |
| left/left | p | 0.911 | 25/25 | 0 | 23 | 1.72 ± 0.52 (1.62) | 7.61 ± 7.17 (5.50) | 2.56 ± 0.74 (2.88) | 5.43 ± 1.74 (6.17) | 2.73 ± 1.16 (3.14) |
| left/right | p | 0.890 | 25/25 | 0 | 21 | 1.71 ± 0.50 (1.80) | 18.95 ± 36.07 (5.70) | 2.32 ± 0.93 (2.27) | 4.77 ± 1.99 (4.32) | 2.29 ± 1.29 (1.87) |
| back/left | p | 0.816 | 25/25 | 0 | 19 | 2.32 ± 0.69 (2.50) | 28.46 ± 45.45 (8.96) | 2.60 ± 1.02 (2.81) | 5.43 ± 2.19 (6.37) | 2.87 ± 1.47 (3.39) |
| back/right | p | 0.790 | 25/25 | 0 | 20 | 2.90 ± 1.97 (2.40) | 25.58 ± 45.94 (9.90) | 2.44 ± 1.14 (2.94) | 5.20 ± 2.49 (6.59) | 2.76 ± 1.52 (3.46) |
| right/left | p | 0.887 | 25/25 | 0 | 22 | 2.21 ± 1.98 (1.98) | 12.68 ± 23.99 (5.36) | 2.42 ± 0.85 (2.68) | 5.01 ± 1.91 (6.01) | 2.45 ± 1.18 (2.96) |
| right/right | p | 0.928 | 25/25 | 0 | 23 | 1.61 ± 0.35 (1.54) | 7.20 ± 7.84 (5.02) | 2.55 ± 0.57 (2.51) | 5.33 ± 1.38 (5.98) | 2.61 ± 1.03 (2.85) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.866 | 15.6 | 5.89 | 3.14 |
| p | normal | 0.886 | 13.7 | 4.52 | 2.08 |

## Notes

- p: score 0.876, 200/200 kicked, 0 fell; worst sector back (0.803).

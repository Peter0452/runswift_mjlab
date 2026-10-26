# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_11-17-40_ovp_o3/model_19049.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.838** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 155 |
| Weak kicks (< 0.3 m) | 18 |
| Time to kick [s] | 1.86 ± 0.92 (1.76) |
| Direction error [°] | 20.15 ± 36.35 (8.37) |
| Avg ball speed [m/s] | 2.22 ± 0.86 (2.54) |
| Peak ball speed [m/s] | 4.64 ± 1.86 (5.51) |
| Distance [m] | 2.23 ± 1.17 (2.69) |
| Path length [m] | 2.24 ± 1.18 (2.70) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.879 | 49/50 | 0 | 42 | 1.55 ± 1.39 (1.38) | 8.82 ± 10.91 (5.56) | 2.11 ± 0.82 (2.03) | 4.40 ± 1.80 (3.98) | 2.02 ± 1.16 (1.60) |
| left | p | 0.828 | 48/50 | 0 | 38 | 1.70 ± 0.52 (1.76) | 20.91 ± 32.44 (9.54) | 2.29 ± 0.88 (2.65) | 4.77 ± 1.89 (5.82) | 2.32 ± 1.17 (2.82) |
| back | p | 0.770 | 49/50 | 0 | 34 | 2.47 ± 0.67 (2.54) | 33.94 ± 54.10 (10.64) | 2.24 ± 0.96 (2.64) | 4.67 ± 2.06 (5.82) | 2.34 ± 1.28 (3.00) |
| right | p | 0.873 | 49/50 | 0 | 41 | 1.73 ± 0.47 (1.76) | 16.96 ± 29.18 (6.39) | 2.24 ± 0.75 (2.42) | 4.73 ± 1.64 (5.37) | 2.24 ± 1.05 (2.44) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.861 | 99/100 | 0 | 81 | 1.79 ± 0.63 (1.76) | 20.59 ± 38.57 (7.61) | 2.26 ± 0.84 (2.55) | 4.74 ± 1.82 (5.56) | 2.29 ± 1.16 (2.76) |
| right | p | 0.814 | 96/100 | 0 | 74 | 1.94 ± 1.14 (1.79) | 19.70 ± 33.89 (8.79) | 2.18 ± 0.87 (2.34) | 4.55 ± 1.89 (5.20) | 2.17 ± 1.19 (2.36) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.932 | 25/25 | 0 | 23 | 1.34 ± 0.32 (1.34) | 6.61 ± 10.57 (4.06) | 2.19 ± 0.76 (2.12) | 4.62 ± 1.70 (4.30) | 2.13 ± 1.09 (1.77) |
| forward/right | p | 0.826 | 24/25 | 0 | 19 | 1.76 ± 1.94 (1.42) | 11.13 ± 10.78 (7.70) | 2.03 ± 0.86 (1.98) | 4.17 ± 1.86 (3.93) | 1.91 ± 1.21 (1.57) |
| left/left | p | 0.880 | 25/25 | 0 | 20 | 1.64 ± 0.42 (1.72) | 15.05 ± 20.10 (7.61) | 2.34 ± 0.87 (2.68) | 4.86 ± 1.86 (5.91) | 2.40 ± 1.09 (2.86) |
| left/right | p | 0.777 | 23/25 | 0 | 18 | 1.77 ± 0.60 (1.98) | 27.27 ± 40.99 (10.47) | 2.24 ± 0.88 (2.63) | 4.68 ± 1.92 (5.82) | 2.24 ± 1.24 (2.78) |
| back/left | p | 0.753 | 24/25 | 0 | 16 | 2.37 ± 0.73 (2.50) | 41.25 ± 60.25 (12.45) | 2.23 ± 0.92 (2.64) | 4.67 ± 2.00 (5.81) | 2.33 ± 1.31 (2.99) |
| back/right | p | 0.787 | 25/25 | 0 | 18 | 2.56 ± 0.59 (2.66) | 26.93 ± 46.38 (9.27) | 2.25 ± 0.99 (2.72) | 4.66 ± 2.12 (5.82) | 2.36 ± 1.26 (3.00) |
| right/left | p | 0.878 | 25/25 | 0 | 22 | 1.83 ± 0.49 (1.82) | 20.29 ± 35.43 (8.74) | 2.29 ± 0.81 (2.48) | 4.79 ± 1.72 (5.50) | 2.29 ± 1.12 (2.76) |
| right/right | p | 0.867 | 24/25 | 0 | 19 | 1.63 ± 0.44 (1.72) | 13.49 ± 20.17 (6.38) | 2.19 ± 0.69 (2.34) | 4.68 ± 1.56 (5.20) | 2.18 ± 0.97 (2.36) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.839 | 16.2 | 5.56 | 2.87 |
| p | normal | 0.836 | 24.1 | 3.74 | 1.60 |

## Notes

- p: score 0.838, 195/200 kicked, 0 fell; worst sector back (0.770).

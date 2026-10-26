# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_11-17-40_ovp_o3/model_19049.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.871** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 177 |
| Weak kicks (< 0.3 m) | 18 |
| Time to kick [s] | 2.01 ± 1.30 (1.79) |
| Direction error [°] | 15.13 ± 32.55 (6.01) |
| Avg ball speed [m/s] | 2.07 ± 0.67 (2.20) |
| Peak ball speed [m/s] | 4.51 ± 1.56 (5.05) |
| Distance [m] | 1.91 ± 0.87 (2.05) |
| Path length [m] | 1.92 ± 0.87 (2.06) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.903 | 50/50 | 0 | 46 | 1.52 ± 1.37 (1.33) | 8.04 ± 11.58 (4.82) | 1.97 ± 0.73 (2.05) | 4.34 ± 1.69 (4.45) | 1.78 ± 0.91 (1.73) |
| left | p | 0.886 | 49/50 | 0 | 43 | 1.77 ± 0.46 (1.76) | 13.70 ± 26.07 (5.89) | 2.12 ± 0.58 (2.21) | 4.59 ± 1.38 (5.05) | 1.94 ± 0.81 (2.05) |
| back | p | 0.773 | 50/50 | 0 | 40 | 2.94 ± 1.80 (2.62) | 33.02 ± 53.90 (9.17) | 2.06 ± 0.87 (2.43) | 4.48 ± 1.96 (5.50) | 2.00 ± 1.06 (2.35) |
| right | p | 0.921 | 49/50 | 0 | 48 | 1.83 ± 0.39 (1.94) | 5.55 ± 5.28 (4.13) | 2.14 ± 0.37 (2.16) | 4.65 ± 1.00 (4.93) | 1.91 ± 0.61 (1.90) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.878 | 98/100 | 0 | 91 | 1.95 ± 1.07 (1.78) | 11.86 ± 26.53 (5.88) | 2.15 ± 0.62 (2.26) | 4.70 ± 1.44 (5.27) | 2.02 ± 0.84 (2.21) |
| right | p | 0.864 | 100/100 | 0 | 86 | 2.07 ± 1.48 (1.81) | 18.35 ± 37.24 (6.29) | 1.99 ± 0.71 (2.08) | 4.33 ± 1.64 (4.60) | 1.80 ± 0.89 (1.78) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.920 | 25/25 | 0 | 24 | 1.24 ± 0.30 (1.28) | 7.35 ± 8.69 (5.06) | 2.00 ± 0.70 (2.10) | 4.44 ± 1.60 (4.82) | 1.82 ± 0.88 (2.07) |
| forward/right | p | 0.887 | 25/25 | 0 | 22 | 1.79 ± 1.88 (1.50) | 8.73 ± 13.84 (4.71) | 1.94 ± 0.77 (2.01) | 4.23 ± 1.77 (4.08) | 1.73 ± 0.95 (1.58) |
| left/left | p | 0.899 | 24/25 | 0 | 23 | 1.74 ± 0.35 (1.65) | 6.14 ± 3.85 (5.42) | 2.32 ± 0.42 (2.40) | 5.04 ± 1.05 (5.54) | 2.22 ± 0.71 (2.39) |
| left/right | p | 0.873 | 25/25 | 0 | 20 | 1.80 ± 0.54 (1.96) | 20.96 ± 34.79 (7.07) | 1.93 ± 0.65 (2.05) | 4.15 ± 1.52 (3.95) | 1.68 ± 0.81 (1.52) |
| back/left | p | 0.781 | 25/25 | 0 | 20 | 2.85 ± 1.68 (2.74) | 28.91 ± 47.59 (8.61) | 2.12 ± 0.84 (2.46) | 4.56 ± 1.85 (5.50) | 2.05 ± 1.02 (2.50) |
| back/right | p | 0.764 | 25/25 | 0 | 20 | 3.03 ± 1.91 (2.60) | 37.13 ± 59.27 (9.45) | 2.00 ± 0.90 (2.40) | 4.39 ± 2.05 (5.50) | 1.95 ± 1.09 (2.19) |
| right/left | p | 0.911 | 24/25 | 0 | 24 | 1.98 ± 0.34 (2.06) | 4.50 ± 3.26 (3.85) | 2.18 ± 0.35 (2.20) | 4.79 ± 0.94 (5.06) | 1.99 ± 0.61 (2.08) |
| right/right | p | 0.931 | 25/25 | 0 | 24 | 1.68 ± 0.38 (1.68) | 6.56 ± 6.51 (4.87) | 2.10 ± 0.39 (2.09) | 4.52 ± 1.03 (4.81) | 1.84 ± 0.61 (1.87) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.866 | 13.5 | 5.08 | 2.27 |
| p | normal | 0.875 | 16.8 | 3.94 | 1.55 |

## Notes

- p: score 0.871, 198/200 kicked, 0 fell; worst sector back (0.773).

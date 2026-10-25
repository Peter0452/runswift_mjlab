# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-45_night_n1_near025/model_19049.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.948** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.52 ± 0.55 (1.40) |
| Direction error [°] | 4.84 ± 3.49 (4.11) |
| Avg ball speed [m/s] | 2.02 ± 0.28 (2.05) |
| Peak ball speed [m/s] | 4.34 ± 0.69 (4.50) |
| Distance [m] | 1.80 ± 0.46 (1.82) |
| Path length [m] | 1.81 ± 0.46 (1.83) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.946 | 50/50 | 0 | 49 | 0.98 ± 0.26 (1.00) | 5.35 ± 4.13 (4.54) | 1.89 ± 0.31 (1.92) | 4.12 ± 0.74 (4.25) | 1.64 ± 0.48 (1.70) |
| left | p | 0.939 | 50/50 | 0 | 49 | 1.48 ± 0.47 (1.36) | 5.71 ± 3.46 (5.19) | 1.99 ± 0.27 (1.98) | 4.25 ± 0.66 (4.31) | 1.76 ± 0.42 (1.82) |
| back | p | 0.954 | 50/50 | 0 | 50 | 2.18 ± 0.27 (2.17) | 3.47 ± 2.84 (2.29) | 2.16 ± 0.21 (2.14) | 4.63 ± 0.58 (4.75) | 1.99 ± 0.42 (2.01) |
| right | p | 0.952 | 50/50 | 0 | 50 | 1.45 ± 0.34 (1.40) | 4.82 ± 2.94 (4.57) | 2.04 ± 0.26 (2.09) | 4.37 ± 0.68 (4.68) | 1.81 ± 0.46 (1.96) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.945 | 100/100 | 0 | 99 | 1.53 ± 0.57 (1.38) | 5.03 ± 3.59 (4.19) | 2.00 ± 0.30 (2.05) | 4.32 ± 0.71 (4.53) | 1.79 ± 0.47 (1.86) |
| right | p | 0.950 | 100/100 | 0 | 99 | 1.51 ± 0.53 (1.51) | 4.65 ± 3.37 (4.11) | 2.04 ± 0.27 (2.05) | 4.37 ± 0.66 (4.44) | 1.81 ± 0.46 (1.78) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.946 | 25/25 | 0 | 25 | 0.97 ± 0.26 (1.00) | 5.43 ± 4.14 (4.62) | 1.91 ± 0.32 (1.96) | 4.15 ± 0.76 (4.35) | 1.66 ± 0.48 (1.76) |
| forward/right | p | 0.947 | 25/25 | 0 | 24 | 0.98 ± 0.26 (1.00) | 5.27 ± 4.13 (4.49) | 1.88 ± 0.30 (1.87) | 4.08 ± 0.71 (4.16) | 1.61 ± 0.47 (1.69) |
| left/left | p | 0.929 | 25/25 | 0 | 24 | 1.45 ± 0.57 (1.30) | 6.23 ± 3.85 (5.05) | 1.91 ± 0.31 (1.97) | 4.11 ± 0.74 (4.29) | 1.66 ± 0.45 (1.81) |
| left/right | p | 0.948 | 25/25 | 0 | 25 | 1.51 ± 0.34 (1.56) | 5.19 ± 2.92 (5.26) | 2.06 ± 0.20 (2.05) | 4.40 ± 0.52 (4.40) | 1.85 ± 0.37 (1.82) |
| back/left | p | 0.953 | 25/25 | 0 | 25 | 2.17 ± 0.24 (2.16) | 3.75 ± 2.73 (2.64) | 2.14 ± 0.21 (2.15) | 4.59 ± 0.60 (4.78) | 1.96 ± 0.43 (1.99) |
| back/right | p | 0.954 | 25/25 | 0 | 25 | 2.18 ± 0.29 (2.18) | 3.19 ± 2.92 (1.95) | 2.18 ± 0.20 (2.14) | 4.67 ± 0.55 (4.71) | 2.02 ± 0.42 (2.14) |
| right/left | p | 0.953 | 25/25 | 0 | 25 | 1.52 ± 0.34 (1.40) | 4.70 ± 2.96 (4.70) | 2.06 ± 0.25 (2.17) | 4.43 ± 0.63 (4.83) | 1.85 ± 0.44 (2.01) |
| right/right | p | 0.951 | 25/25 | 0 | 25 | 1.38 ± 0.32 (1.38) | 4.94 ± 2.90 (4.44) | 2.03 ± 0.28 (2.06) | 4.31 ± 0.71 (4.52) | 1.77 ± 0.47 (1.83) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.947 | 4.7 | 4.77 | 2.07 |
| p | normal | 0.948 | 5.0 | 3.92 | 1.52 |

## Notes

- p: score 0.948, 200/200 kicked, 0 fell; worst sector left (0.939).

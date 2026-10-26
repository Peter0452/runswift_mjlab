# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_08-51-51_night_n7_rest15/model_19847.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.937** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.61 ± 0.53 (1.54) |
| Direction error [°] | 6.36 ± 12.65 (5.00) |
| Avg ball speed [m/s] | 1.86 ± 0.34 (1.98) |
| Peak ball speed [m/s] | 4.17 ± 0.84 (4.41) |
| Distance [m] | 1.47 ± 0.47 (1.50) |
| Path length [m] | 1.47 ± 0.47 (1.51) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.943 | 50/50 | 0 | 49 | 1.05 ± 0.22 (1.09) | 5.27 ± 3.76 (4.33) | 1.65 ± 0.37 (1.65) | 3.64 ± 0.81 (3.55) | 1.16 ± 0.44 (1.09) |
| left | p | 0.945 | 50/50 | 0 | 50 | 1.54 ± 0.34 (1.54) | 5.46 ± 3.01 (5.12) | 1.90 ± 0.29 (1.99) | 4.30 ± 0.72 (4.58) | 1.52 ± 0.43 (1.52) |
| back | p | 0.916 | 50/50 | 0 | 49 | 2.29 ± 0.26 (2.26) | 9.33 ± 24.38 (5.99) | 1.99 ± 0.34 (2.10) | 4.49 ± 0.86 (4.89) | 1.68 ± 0.46 (1.83) |
| right | p | 0.945 | 50/50 | 0 | 50 | 1.56 ± 0.35 (1.53) | 5.37 ± 3.28 (4.83) | 1.89 ± 0.28 (2.00) | 4.24 ± 0.72 (4.44) | 1.50 ± 0.39 (1.53) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.940 | 100/100 | 0 | 100 | 1.62 ± 0.54 (1.55) | 5.35 ± 3.12 (4.74) | 1.89 ± 0.31 (2.01) | 4.24 ± 0.78 (4.55) | 1.50 ± 0.45 (1.57) |
| right | p | 0.935 | 100/100 | 0 | 98 | 1.60 ± 0.52 (1.52) | 7.37 ± 17.56 (5.24) | 1.83 ± 0.37 (1.94) | 4.09 ± 0.89 (4.10) | 1.43 ± 0.48 (1.47) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.947 | 25/25 | 0 | 25 | 1.06 ± 0.22 (1.10) | 4.95 ± 3.32 (3.57) | 1.74 ± 0.37 (1.78) | 3.81 ± 0.81 (3.63) | 1.26 ± 0.45 (1.16) |
| forward/right | p | 0.939 | 25/25 | 0 | 24 | 1.04 ± 0.22 (1.06) | 5.58 ± 4.13 (4.34) | 1.57 ± 0.34 (1.50) | 3.46 ± 0.77 (3.36) | 1.06 ± 0.40 (1.00) |
| left/left | p | 0.942 | 25/25 | 0 | 25 | 1.43 ± 0.33 (1.48) | 5.81 ± 3.47 (4.72) | 1.86 ± 0.27 (1.96) | 4.17 ± 0.69 (4.51) | 1.45 ± 0.40 (1.47) |
| left/right | p | 0.949 | 25/25 | 0 | 25 | 1.64 ± 0.31 (1.64) | 5.11 ± 2.41 (5.21) | 1.94 ± 0.30 (2.06) | 4.42 ± 0.74 (4.74) | 1.60 ± 0.44 (1.56) |
| back/left | p | 0.921 | 25/25 | 0 | 25 | 2.32 ± 0.28 (2.26) | 5.63 ± 2.75 (4.98) | 2.00 ± 0.28 (2.09) | 4.54 ± 0.73 (4.87) | 1.70 ± 0.46 (1.88) |
| back/right | p | 0.910 | 25/25 | 0 | 24 | 2.27 ± 0.23 (2.20) | 13.03 ± 33.97 (6.12) | 1.98 ± 0.39 (2.12) | 4.43 ± 0.97 (4.92) | 1.66 ± 0.46 (1.77) |
| right/left | p | 0.948 | 25/25 | 0 | 25 | 1.67 ± 0.33 (1.62) | 4.99 ± 2.81 (4.60) | 1.97 ± 0.24 (2.04) | 4.44 ± 0.67 (4.81) | 1.60 ± 0.35 (1.64) |
| right/right | p | 0.942 | 25/25 | 0 | 25 | 1.44 ± 0.34 (1.46) | 5.76 ± 3.65 (5.02) | 1.81 ± 0.29 (1.75) | 4.05 ± 0.71 (4.05) | 1.40 ± 0.40 (1.25) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.937 | 5.4 | 4.60 | 1.69 |
| p | normal | 0.938 | 7.3 | 3.73 | 1.24 |

## Notes

- p: score 0.937, 200/200 kicked, 0 fell; worst sector back (0.916).

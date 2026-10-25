# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **h022** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | h022 |
|---|---|
| **Score** | **0.936** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 4 |
| Time to kick [s] | 1.62 ± 0.55 (1.52) |
| Direction error [°] | 5.49 ± 4.07 (4.92) |
| Avg ball speed [m/s] | 1.95 ± 0.40 (1.97) |
| Peak ball speed [m/s] | 4.14 ± 0.91 (4.23) |
| Distance [m] | 1.71 ± 0.55 (1.72) |
| Path length [m] | 1.72 ± 0.55 (1.73) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | h022 | 0.955 | 50/50 | 0 | 50 | 1.06 ± 0.24 (1.11) | 4.47 ± 3.07 (4.19) | 1.80 ± 0.29 (1.73) | 3.79 ± 0.66 (3.52) | 1.44 ± 0.44 (1.32) |
| left | h022 | 0.939 | 50/50 | 0 | 49 | 1.55 ± 0.35 (1.56) | 6.09 ± 3.80 (5.39) | 2.03 ± 0.25 (2.12) | 4.34 ± 0.66 (4.50) | 1.84 ± 0.45 (1.91) |
| back | h022 | 0.910 | 50/50 | 0 | 48 | 2.32 ± 0.27 (2.29) | 5.51 ± 5.51 (4.78) | 1.98 ± 0.62 (2.18) | 4.20 ± 1.35 (4.64) | 1.81 ± 0.70 (1.99) |
| right | h022 | 0.941 | 50/50 | 0 | 50 | 1.54 ± 0.35 (1.52) | 5.88 ± 3.25 (5.43) | 2.00 ± 0.29 (1.99) | 4.23 ± 0.70 (4.25) | 1.76 ± 0.46 (1.76) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | h022 | 0.932 | 100/100 | 0 | 97 | 1.62 ± 0.55 (1.54) | 5.71 ± 4.71 (4.82) | 1.95 ± 0.44 (2.05) | 4.15 ± 1.01 (4.40) | 1.73 ± 0.58 (1.87) |
| right | h022 | 0.940 | 100/100 | 0 | 100 | 1.62 ± 0.54 (1.52) | 5.27 ± 3.30 (4.96) | 1.96 ± 0.36 (1.91) | 4.13 ± 0.81 (4.05) | 1.70 ± 0.51 (1.62) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | h022 | 0.955 | 25/25 | 0 | 25 | 1.05 ± 0.24 (1.12) | 4.50 ± 3.13 (3.63) | 1.80 ± 0.26 (1.72) | 3.78 ± 0.61 (3.54) | 1.44 ± 0.43 (1.24) |
| forward/right | h022 | 0.954 | 25/25 | 0 | 25 | 1.06 ± 0.24 (1.10) | 4.44 ± 3.01 (4.20) | 1.81 ± 0.31 (1.73) | 3.79 ± 0.69 (3.51) | 1.44 ± 0.44 (1.32) |
| left/left | h022 | 0.937 | 25/25 | 0 | 24 | 1.46 ± 0.36 (1.52) | 6.34 ± 4.06 (5.92) | 2.04 ± 0.27 (2.15) | 4.37 ± 0.72 (4.74) | 1.85 ± 0.49 (1.95) |
| left/right | h022 | 0.941 | 25/25 | 0 | 25 | 1.64 ± 0.33 (1.64) | 5.84 ± 3.51 (5.36) | 2.01 ± 0.23 (2.06) | 4.31 ± 0.58 (4.37) | 1.82 ± 0.40 (1.87) |
| back/left | h022 | 0.890 | 25/25 | 0 | 23 | 2.32 ± 0.29 (2.28) | 6.69 ± 7.17 (4.95) | 1.91 ± 0.71 (2.11) | 4.07 ± 1.56 (4.62) | 1.78 ± 0.78 (1.99) |
| back/right | h022 | 0.929 | 25/25 | 0 | 25 | 2.32 ± 0.25 (2.30) | 4.34 ± 2.56 (4.56) | 2.05 ± 0.50 (2.20) | 4.32 ± 1.09 (4.72) | 1.84 ± 0.60 (1.95) |
| right/left | h022 | 0.946 | 25/25 | 0 | 25 | 1.64 ± 0.33 (1.60) | 5.30 ± 2.83 (5.01) | 2.05 ± 0.28 (2.15) | 4.37 ± 0.70 (4.63) | 1.85 ± 0.46 (1.90) |
| right/right | h022 | 0.935 | 25/25 | 0 | 25 | 1.45 ± 0.34 (1.44) | 6.46 ± 3.53 (6.29) | 1.95 ± 0.29 (1.91) | 4.09 ± 0.67 (4.02) | 1.68 ± 0.45 (1.61) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| h022 | strong | 0.944 | 4.9 | 4.60 | 1.99 |
| h022 | normal | 0.928 | 6.1 | 3.68 | 1.43 |

## Notes

- h022: score 0.936, 200/200 kicked, 0 fell; worst sector back (0.910).

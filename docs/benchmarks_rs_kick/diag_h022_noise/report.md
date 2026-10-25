# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **h022** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | h022 |
|---|---|
| **Score** | **0.939** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.64 ± 0.55 (1.57) |
| Direction error [°] | 5.03 ± 3.25 (4.50) |
| Avg ball speed [m/s] | 1.68 ± 0.30 (1.68) |
| Peak ball speed [m/s] | 3.58 ± 0.69 (3.48) |
| Distance [m] | 1.22 ± 0.40 (1.16) |
| Path length [m] | 1.22 ± 0.40 (1.17) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | h022 | 0.949 | 50/50 | 0 | 49 | 1.08 ± 0.24 (1.12) | 4.07 ± 3.76 (2.85) | 1.45 ± 0.31 (1.43) | 3.10 ± 0.65 (3.00) | 0.93 ± 0.35 (0.94) |
| left | h022 | 0.943 | 50/50 | 0 | 50 | 1.57 ± 0.35 (1.60) | 5.62 ± 3.20 (5.69) | 1.75 ± 0.24 (1.83) | 3.76 ± 0.58 (3.98) | 1.32 ± 0.34 (1.38) |
| back | h022 | 0.923 | 50/50 | 0 | 50 | 2.36 ± 0.28 (2.31) | 4.87 ± 2.58 (4.63) | 1.82 ± 0.28 (1.84) | 3.88 ± 0.67 (3.93) | 1.41 ± 0.40 (1.42) |
| right | h022 | 0.942 | 50/50 | 0 | 50 | 1.57 ± 0.34 (1.56) | 5.57 ± 3.09 (5.47) | 1.69 ± 0.23 (1.66) | 3.58 ± 0.58 (3.42) | 1.22 ± 0.31 (1.16) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | h022 | 0.941 | 100/100 | 0 | 100 | 1.64 ± 0.56 (1.58) | 4.77 ± 2.78 (4.63) | 1.69 ± 0.29 (1.70) | 3.59 ± 0.68 (3.55) | 1.23 ± 0.40 (1.20) |
| right | h022 | 0.937 | 100/100 | 0 | 99 | 1.65 ± 0.55 (1.56) | 5.30 ± 3.63 (4.45) | 1.67 ± 0.31 (1.67) | 3.57 ± 0.69 (3.44) | 1.21 ± 0.39 (1.13) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | h022 | 0.954 | 25/25 | 0 | 25 | 1.06 ± 0.23 (1.12) | 3.62 ± 2.59 (2.42) | 1.45 ± 0.28 (1.42) | 3.08 ± 0.59 (2.93) | 0.93 ± 0.36 (0.83) |
| forward/right | h022 | 0.945 | 25/25 | 0 | 24 | 1.09 ± 0.25 (1.14) | 4.52 ± 4.61 (3.19) | 1.44 ± 0.34 (1.45) | 3.12 ± 0.70 (3.04) | 0.93 ± 0.35 (0.96) |
| left/left | h022 | 0.945 | 25/25 | 0 | 25 | 1.48 ± 0.35 (1.52) | 5.51 ± 3.07 (5.70) | 1.73 ± 0.21 (1.82) | 3.70 ± 0.53 (3.92) | 1.28 ± 0.30 (1.32) |
| left/right | h022 | 0.942 | 25/25 | 0 | 25 | 1.66 ± 0.32 (1.66) | 5.72 ± 3.32 (5.50) | 1.77 ± 0.26 (1.85) | 3.82 ± 0.61 (4.06) | 1.36 ± 0.37 (1.46) |
| back/left | h022 | 0.923 | 25/25 | 0 | 25 | 2.36 ± 0.29 (2.30) | 4.61 ± 2.20 (4.63) | 1.81 ± 0.30 (1.86) | 3.87 ± 0.74 (4.11) | 1.40 ± 0.44 (1.51) |
| back/right | h022 | 0.924 | 25/25 | 0 | 25 | 2.36 ± 0.28 (2.32) | 5.13 ± 2.89 (4.83) | 1.84 ± 0.25 (1.79) | 3.90 ± 0.61 (3.79) | 1.41 ± 0.36 (1.39) |
| right/left | h022 | 0.945 | 25/25 | 0 | 25 | 1.66 ± 0.32 (1.62) | 5.32 ± 2.80 (5.57) | 1.76 ± 0.22 (1.73) | 3.73 ± 0.56 (3.73) | 1.31 ± 0.31 (1.28) |
| right/right | h022 | 0.939 | 25/25 | 0 | 25 | 1.49 ± 0.34 (1.54) | 5.82 ± 3.34 (5.36) | 1.62 ± 0.22 (1.59) | 3.43 ± 0.55 (3.20) | 1.12 ± 0.28 (1.05) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| h022 | strong | 0.934 | 5.1 | 3.87 | 1.37 |
| h022 | normal | 0.945 | 4.9 | 3.29 | 1.07 |

## Notes

- h022: score 0.939, 200/200 kicked, 0 fell; worst sector back (0.923).

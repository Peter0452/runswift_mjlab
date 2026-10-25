# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **h022** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | h022 |
|---|---|
| **Score** | **0.938** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.64 ± 0.55 (1.56) |
| Direction error [°] | 5.86 ± 11.94 (4.63) |
| Avg ball speed [m/s] | 1.53 ± 0.30 (1.54) |
| Peak ball speed [m/s] | 3.69 ± 0.75 (3.63) |
| Distance [m] | 1.20 ± 0.39 (1.16) |
| Path length [m] | 1.20 ± 0.39 (1.16) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | h022 | 0.948 | 50/50 | 0 | 49 | 1.09 ± 0.24 (1.13) | 4.37 ± 3.55 (3.29) | 1.38 ± 0.31 (1.35) | 3.29 ± 0.75 (3.05) | 0.98 ± 0.39 (0.90) |
| left | h022 | 0.940 | 50/50 | 0 | 49 | 1.58 ± 0.36 (1.59) | 5.84 ± 2.99 (5.26) | 1.57 ± 0.26 (1.62) | 3.83 ± 0.64 (3.96) | 1.26 ± 0.35 (1.27) |
| back | h022 | 0.925 | 50/50 | 0 | 49 | 2.34 ± 0.28 (2.30) | 7.50 ± 23.06 (3.46) | 1.65 ± 0.31 (1.66) | 3.97 ± 0.77 (4.14) | 1.36 ± 0.38 (1.42) |
| right | h022 | 0.939 | 50/50 | 0 | 48 | 1.56 ± 0.35 (1.53) | 5.71 ± 3.49 (5.25) | 1.54 ± 0.25 (1.49) | 3.67 ± 0.65 (3.52) | 1.18 ± 0.33 (1.14) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | h022 | 0.937 | 100/100 | 0 | 97 | 1.64 ± 0.55 (1.58) | 6.48 ± 16.50 (4.63) | 1.52 ± 0.33 (1.55) | 3.63 ± 0.80 (3.61) | 1.18 ± 0.41 (1.15) |
| right | h022 | 0.940 | 100/100 | 0 | 98 | 1.65 ± 0.55 (1.54) | 5.23 ± 3.48 (4.74) | 1.55 ± 0.27 (1.53) | 3.75 ± 0.70 (3.65) | 1.22 ± 0.37 (1.17) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | h022 | 0.949 | 25/25 | 0 | 25 | 1.08 ± 0.25 (1.06) | 3.73 ± 2.57 (3.26) | 1.31 ± 0.33 (1.34) | 3.10 ± 0.75 (3.03) | 0.91 ± 0.40 (0.87) |
| forward/right | h022 | 0.947 | 25/25 | 0 | 24 | 1.09 ± 0.24 (1.16) | 5.01 ± 4.21 (3.42) | 1.44 ± 0.29 (1.36) | 3.48 ± 0.71 (3.25) | 1.06 ± 0.35 (0.93) |
| left/left | h022 | 0.939 | 25/25 | 0 | 24 | 1.46 ± 0.35 (1.56) | 5.99 ± 3.12 (5.15) | 1.56 ± 0.26 (1.63) | 3.79 ± 0.62 (3.98) | 1.23 ± 0.32 (1.37) |
| left/right | h022 | 0.942 | 25/25 | 0 | 25 | 1.69 ± 0.33 (1.72) | 5.70 ± 2.84 (5.60) | 1.58 ± 0.25 (1.61) | 3.88 ± 0.66 (3.85) | 1.30 ± 0.37 (1.26) |
| back/left | h022 | 0.916 | 25/25 | 0 | 24 | 2.33 ± 0.29 (2.30) | 10.75 ± 32.17 (3.91) | 1.61 ± 0.37 (1.64) | 3.85 ± 0.91 (3.98) | 1.32 ± 0.43 (1.31) |
| back/right | h022 | 0.934 | 25/25 | 0 | 25 | 2.34 ± 0.27 (2.30) | 4.25 ± 2.76 (3.29) | 1.68 ± 0.24 (1.66) | 4.09 ± 0.59 (4.20) | 1.39 ± 0.32 (1.45) |
| right/left | h022 | 0.942 | 25/25 | 0 | 24 | 1.66 ± 0.31 (1.64) | 5.47 ± 3.31 (5.15) | 1.57 ± 0.25 (1.56) | 3.79 ± 0.64 (3.59) | 1.25 ± 0.34 (1.23) |
| right/right | h022 | 0.936 | 25/25 | 0 | 24 | 1.47 ± 0.36 (1.52) | 5.96 ± 3.63 (5.55) | 1.51 ± 0.25 (1.49) | 3.55 ± 0.64 (3.43) | 1.12 ± 0.31 (1.06) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| h022 | strong | 0.933 | 5.3 | 3.96 | 1.33 |
| h022 | normal | 0.943 | 6.4 | 3.43 | 1.06 |

## Notes

- h022: score 0.938, 200/200 kicked, 0 fell; worst sector back (0.925).

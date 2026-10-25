# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **h022** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | h022 |
|---|---|
| **Score** | **0.942** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.62 ± 0.54 (1.55) |
| Direction error [°] | 5.77 ± 12.41 (4.15) |
| Avg ball speed [m/s] | 1.72 ± 0.31 (1.76) |
| Peak ball speed [m/s] | 3.72 ± 0.73 (3.76) |
| Distance [m] | 1.29 ± 0.42 (1.25) |
| Path length [m] | 1.29 ± 0.42 (1.25) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | h022 | 0.950 | 50/50 | 0 | 50 | 1.07 ± 0.25 (1.11) | 4.35 ± 3.06 (2.92) | 1.48 ± 0.29 (1.48) | 3.20 ± 0.63 (3.10) | 0.98 ± 0.38 (0.94) |
| left | h022 | 0.946 | 50/50 | 0 | 50 | 1.56 ± 0.35 (1.57) | 5.37 ± 3.39 (4.53) | 1.79 ± 0.25 (1.83) | 3.90 ± 0.63 (4.08) | 1.39 ± 0.36 (1.46) |
| back | h022 | 0.925 | 50/50 | 0 | 49 | 2.32 ± 0.25 (2.28) | 8.09 ± 24.05 (4.15) | 1.83 ± 0.34 (1.86) | 3.95 ± 0.80 (4.07) | 1.45 ± 0.43 (1.48) |
| right | h022 | 0.946 | 50/50 | 0 | 50 | 1.55 ± 0.34 (1.53) | 5.27 ± 3.00 (5.04) | 1.77 ± 0.23 (1.82) | 3.83 ± 0.60 (3.93) | 1.34 ± 0.33 (1.33) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | h022 | 0.943 | 100/100 | 0 | 100 | 1.63 ± 0.55 (1.58) | 4.88 ± 3.08 (4.08) | 1.73 ± 0.29 (1.73) | 3.74 ± 0.69 (3.69) | 1.29 ± 0.41 (1.24) |
| right | h022 | 0.941 | 100/100 | 0 | 99 | 1.62 ± 0.53 (1.53) | 6.66 ± 17.24 (4.36) | 1.71 ± 0.34 (1.78) | 3.71 ± 0.77 (3.79) | 1.28 ± 0.43 (1.25) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | h022 | 0.951 | 25/25 | 0 | 25 | 1.06 ± 0.24 (1.12) | 4.18 ± 2.66 (2.73) | 1.47 ± 0.28 (1.48) | 3.16 ± 0.61 (3.09) | 0.96 ± 0.37 (0.95) |
| forward/right | h022 | 0.948 | 25/25 | 0 | 25 | 1.07 ± 0.26 (1.10) | 4.51 ± 3.40 (3.00) | 1.49 ± 0.30 (1.43) | 3.25 ± 0.66 (3.11) | 1.00 ± 0.38 (0.92) |
| left/left | h022 | 0.947 | 25/25 | 0 | 25 | 1.46 ± 0.35 (1.54) | 5.30 ± 3.81 (3.84) | 1.77 ± 0.21 (1.79) | 3.82 ± 0.55 (3.89) | 1.34 ± 0.31 (1.39) |
| left/right | h022 | 0.945 | 25/25 | 0 | 25 | 1.66 ± 0.32 (1.64) | 5.44 ± 2.90 (6.68) | 1.82 ± 0.28 (1.89) | 3.99 ± 0.69 (4.18) | 1.43 ± 0.40 (1.52) |
| back/left | h022 | 0.930 | 25/25 | 0 | 25 | 2.34 ± 0.27 (2.30) | 4.56 ± 2.80 (4.04) | 1.85 ± 0.23 (1.85) | 3.98 ± 0.58 (4.04) | 1.44 ± 0.36 (1.53) |
| back/right | h022 | 0.921 | 25/25 | 0 | 24 | 2.29 ± 0.23 (2.28) | 11.62 ± 33.53 (4.41) | 1.82 ± 0.42 (1.95) | 3.93 ± 0.96 (4.23) | 1.45 ± 0.50 (1.44) |
| right/left | h022 | 0.944 | 25/25 | 0 | 25 | 1.65 ± 0.32 (1.64) | 5.47 ± 2.70 (5.25) | 1.82 ± 0.27 (1.90) | 3.98 ± 0.68 (4.25) | 1.42 ± 0.38 (1.49) |
| right/right | h022 | 0.949 | 25/25 | 0 | 25 | 1.46 ± 0.33 (1.44) | 5.07 ± 3.25 (3.86) | 1.72 ± 0.18 (1.74) | 3.68 ± 0.45 (3.74) | 1.26 ± 0.24 (1.22) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| h022 | strong | 0.943 | 4.7 | 4.08 | 1.46 |
| h022 | normal | 0.941 | 6.8 | 3.37 | 1.11 |

## Notes

- h022: score 0.942, 200/200 kicked, 0 fell; worst sector back (0.925).

# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **night_n2_near04_18600** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-48_night_n2_near04/model_18600.pt`.

## Overall

| Metric | night_n2_near04_18600 |
|---|---|
| **Score** | **0.940** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.61 ± 0.53 (1.54) |
| Direction error [°] | 6.09 ± 12.59 (4.60) |
| Avg ball speed [m/s] | 1.82 ± 0.33 (1.88) |
| Peak ball speed [m/s] | 4.02 ± 0.82 (4.24) |
| Distance [m] | 1.45 ± 0.45 (1.49) |
| Path length [m] | 1.46 ± 0.45 (1.49) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | night_n2_near04_18600 | 0.953 | 50/50 | 0 | 49 | 1.06 ± 0.24 (1.09) | 4.52 ± 3.48 (3.32) | 1.64 ± 0.28 (1.62) | 3.60 ± 0.69 (3.43) | 1.19 ± 0.39 (1.11) |
| left | night_n2_near04_18600 | 0.946 | 50/50 | 0 | 50 | 1.56 ± 0.35 (1.57) | 5.38 ± 3.12 (5.30) | 1.90 ± 0.25 (1.97) | 4.26 ± 0.67 (4.53) | 1.59 ± 0.40 (1.67) |
| back | night_n2_near04_18600 | 0.922 | 50/50 | 0 | 48 | 2.29 ± 0.26 (2.26) | 8.50 ± 24.33 (4.09) | 1.89 ± 0.41 (2.00) | 4.19 ± 1.00 (4.54) | 1.58 ± 0.48 (1.70) |
| right | night_n2_near04_18600 | 0.939 | 50/50 | 0 | 50 | 1.54 ± 0.35 (1.51) | 5.95 ± 3.34 (5.69) | 1.84 ± 0.27 (1.90) | 4.05 ± 0.69 (4.29) | 1.47 ± 0.39 (1.48) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | night_n2_near04_18600 | 0.937 | 100/100 | 0 | 99 | 1.62 ± 0.55 (1.57) | 5.63 ± 4.82 (5.38) | 1.83 ± 0.33 (1.92) | 4.06 ± 0.83 (4.37) | 1.48 ± 0.46 (1.49) |
| right | night_n2_near04_18600 | 0.944 | 100/100 | 0 | 98 | 1.60 ± 0.52 (1.52) | 6.55 ± 17.12 (3.73) | 1.80 ± 0.32 (1.88) | 3.98 ± 0.80 (4.20) | 1.43 ± 0.43 (1.46) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | night_n2_near04_18600 | 0.949 | 25/25 | 0 | 25 | 1.05 ± 0.22 (1.10) | 4.90 ± 3.53 (3.44) | 1.63 ± 0.26 (1.62) | 3.56 ± 0.61 (3.32) | 1.16 ± 0.37 (1.03) |
| forward/right | night_n2_near04_18600 | 0.957 | 25/25 | 0 | 24 | 1.06 ± 0.25 (1.08) | 4.14 ± 3.39 (3.00) | 1.66 ± 0.31 (1.62) | 3.63 ± 0.75 (3.43) | 1.21 ± 0.40 (1.11) |
| left/left | night_n2_near04_18600 | 0.950 | 25/25 | 0 | 25 | 1.47 ± 0.36 (1.50) | 4.99 ± 2.70 (5.11) | 1.89 ± 0.24 (1.98) | 4.22 ± 0.67 (4.51) | 1.55 ± 0.39 (1.59) |
| left/right | night_n2_near04_18600 | 0.942 | 25/25 | 0 | 25 | 1.66 ± 0.32 (1.62) | 5.76 ± 3.45 (5.67) | 1.92 ± 0.27 (1.97) | 4.30 ± 0.67 (4.57) | 1.62 ± 0.41 (1.73) |
| back/left | night_n2_near04_18600 | 0.911 | 25/25 | 0 | 24 | 2.32 ± 0.27 (2.26) | 6.45 ± 7.91 (5.42) | 1.90 ± 0.44 (2.02) | 4.23 ± 1.05 (4.58) | 1.62 ± 0.50 (1.74) |
| back/right | night_n2_near04_18600 | 0.933 | 25/25 | 0 | 24 | 2.25 ± 0.24 (2.22) | 10.56 ± 33.35 (3.32) | 1.88 ± 0.39 (1.98) | 4.14 ± 0.95 (4.53) | 1.54 ± 0.45 (1.64) |
| right/left | night_n2_near04_18600 | 0.936 | 25/25 | 0 | 25 | 1.63 ± 0.33 (1.62) | 6.19 ± 2.98 (5.67) | 1.91 ± 0.28 (1.97) | 4.23 ± 0.71 (4.47) | 1.58 ± 0.42 (1.61) |
| right/right | night_n2_near04_18600 | 0.943 | 25/25 | 0 | 25 | 1.45 ± 0.34 (1.46) | 5.72 ± 3.64 (5.72) | 1.76 ± 0.23 (1.77) | 3.87 ± 0.61 (3.81) | 1.35 ± 0.32 (1.39) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| night_n2_near04_18600 | strong | 0.941 | 5.1 | 4.48 | 1.69 |
| night_n2_near04_18600 | normal | 0.939 | 7.1 | 3.56 | 1.22 |

## Notes

- night_n2_near04_18600: score 0.940, 200/200 kicked, 0 fell; worst sector back (0.922).

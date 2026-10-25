# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **night_n1_near025_18600** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-45_night_n1_near025/model_18600.pt`.

## Overall

| Metric | night_n1_near025_18600 |
|---|---|
| **Score** | **0.944** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.68 ± 0.56 (1.58) |
| Direction error [°] | 6.26 ± 16.53 (3.71) |
| Avg ball speed [m/s] | 1.61 ± 0.29 (1.62) |
| Peak ball speed [m/s] | 4.36 ± 0.76 (4.48) |
| Distance [m] | 1.66 ± 0.45 (1.63) |
| Path length [m] | 1.67 ± 0.45 (1.64) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | night_n1_near025_18600 | 0.954 | 50/50 | 0 | 49 | 1.14 ± 0.33 (1.12) | 4.43 ± 3.35 (3.62) | 1.47 ± 0.30 (1.48) | 4.05 ± 0.75 (4.04) | 1.46 ± 0.43 (1.50) |
| left | night_n1_near025_18600 | 0.949 | 50/50 | 0 | 50 | 1.57 ± 0.34 (1.60) | 5.06 ± 2.80 (4.71) | 1.64 ± 0.25 (1.66) | 4.50 ± 0.67 (4.72) | 1.74 ± 0.43 (1.79) |
| back | night_n1_near025_18600 | 0.932 | 50/50 | 0 | 49 | 2.34 ± 0.27 (2.34) | 6.76 ± 22.31 (2.88) | 1.70 ± 0.31 (1.75) | 4.51 ± 0.85 (4.89) | 1.78 ± 0.48 (1.91) |
| right | night_n1_near025_18600 | 0.942 | 50/50 | 0 | 48 | 1.68 ± 0.47 (1.58) | 8.81 ± 23.76 (3.48) | 1.64 ± 0.25 (1.63) | 4.36 ± 0.66 (4.41) | 1.66 ± 0.39 (1.58) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | night_n1_near025_18600 | 0.949 | 100/100 | 0 | 99 | 1.65 ± 0.54 (1.58) | 5.62 ± 15.92 (3.56) | 1.63 ± 0.32 (1.65) | 4.39 ± 0.84 (4.47) | 1.68 ± 0.51 (1.62) |
| right | night_n1_near025_18600 | 0.939 | 100/100 | 0 | 97 | 1.72 ± 0.58 (1.58) | 6.91 ± 17.09 (4.02) | 1.60 ± 0.25 (1.60) | 4.33 ± 0.66 (4.51) | 1.64 ± 0.38 (1.64) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | night_n1_near025_18600 | 0.960 | 25/25 | 0 | 25 | 1.09 ± 0.22 (1.10) | 4.05 ± 3.01 (3.29) | 1.50 ± 0.32 (1.54) | 4.08 ± 0.78 (4.10) | 1.46 ± 0.46 (1.47) |
| forward/right | night_n1_near025_18600 | 0.948 | 25/25 | 0 | 24 | 1.18 ± 0.41 (1.12) | 4.80 ± 3.63 (3.77) | 1.45 ± 0.28 (1.36) | 4.02 ± 0.72 (3.86) | 1.47 ± 0.39 (1.53) |
| left/left | night_n1_near025_18600 | 0.952 | 25/25 | 0 | 25 | 1.48 ± 0.36 (1.54) | 4.76 ± 2.52 (4.71) | 1.70 ± 0.30 (1.77) | 4.60 ± 0.74 (4.79) | 1.82 ± 0.49 (1.79) |
| left/right | night_n1_near025_18600 | 0.946 | 25/25 | 0 | 25 | 1.66 ± 0.30 (1.68) | 5.36 ± 3.02 (4.73) | 1.58 ± 0.16 (1.58) | 4.39 ± 0.57 (4.61) | 1.66 ± 0.33 (1.78) |
| back/left | night_n1_near025_18600 | 0.924 | 25/25 | 0 | 24 | 2.34 ± 0.26 (2.32) | 9.99 ± 31.10 (2.45) | 1.65 ± 0.36 (1.69) | 4.44 ± 1.04 (4.86) | 1.73 ± 0.57 (1.94) |
| back/right | night_n1_near025_18600 | 0.940 | 25/25 | 0 | 25 | 2.34 ± 0.28 (2.36) | 3.52 ± 2.64 (2.97) | 1.74 ± 0.23 (1.86) | 4.59 ± 0.60 (4.93) | 1.83 ± 0.35 (1.89) |
| right/left | night_n1_near025_18600 | 0.962 | 25/25 | 0 | 25 | 1.67 ± 0.32 (1.62) | 3.69 ± 2.26 (2.87) | 1.67 ± 0.26 (1.65) | 4.43 ± 0.68 (4.44) | 1.71 ± 0.41 (1.63) |
| right/right | night_n1_near025_18600 | 0.923 | 25/25 | 0 | 23 | 1.68 ± 0.58 (1.54) | 13.94 ± 32.73 (3.99) | 1.62 ± 0.23 (1.61) | 4.30 ± 0.63 (4.40) | 1.61 ± 0.36 (1.52) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| night_n1_near025_18600 | strong | 0.945 | 4.6 | 4.80 | 1.89 |
| night_n1_near025_18600 | normal | 0.943 | 7.9 | 3.91 | 1.43 |

## Notes

- night_n1_near025_18600: score 0.944, 200/200 kicked, 0 fell; worst sector back (0.932).

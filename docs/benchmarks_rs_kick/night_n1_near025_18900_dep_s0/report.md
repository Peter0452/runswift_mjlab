# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **night_n1_near025_18900** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-45_night_n1_near025/model_18900.pt`.

## Overall

| Metric | night_n1_near025_18900 |
|---|---|
| **Score** | **0.860** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 166 |
| Weak kicks (< 0.3 m) | 9 |
| Time to kick [s] | 1.93 ± 1.24 (1.76) |
| Direction error [°] | 16.46 ± 33.02 (6.18) |
| Avg ball speed [m/s] | 2.30 ± 0.75 (2.54) |
| Peak ball speed [m/s] | 4.79 ± 1.64 (5.65) |
| Distance [m] | 2.30 ± 1.06 (2.66) |
| Path length [m] | 2.31 ± 1.06 (2.66) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | night_n1_near025_18900 | 0.873 | 49/50 | 0 | 43 | 1.86 ± 2.23 (1.36) | 8.34 ± 10.95 (4.19) | 2.17 ± 0.67 (2.18) | 4.52 ± 1.49 (4.22) | 2.04 ± 0.93 (1.79) |
| left | night_n1_near025_18900 | 0.879 | 49/50 | 0 | 42 | 1.73 ± 0.47 (1.82) | 16.98 ± 32.04 (6.61) | 2.38 ± 0.78 (2.69) | 5.00 ± 1.72 (5.85) | 2.47 ± 1.09 (2.99) |
| back | night_n1_near025_18900 | 0.796 | 48/50 | 0 | 39 | 2.42 ± 0.58 (2.47) | 24.67 ± 45.87 (9.25) | 2.35 ± 0.84 (2.77) | 4.90 ± 1.78 (5.90) | 2.45 ± 1.15 (3.10) |
| right | night_n1_near025_18900 | 0.891 | 49/50 | 0 | 42 | 1.72 ± 0.47 (1.78) | 16.02 ± 31.63 (5.57) | 2.29 ± 0.69 (2.46) | 4.75 ± 1.50 (5.38) | 2.24 ± 0.99 (2.54) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | night_n1_near025_18900 | 0.885 | 100/100 | 0 | 86 | 1.86 ± 0.98 (1.77) | 17.67 ± 36.16 (6.08) | 2.27 ± 0.77 (2.51) | 4.75 ± 1.69 (5.65) | 2.28 ± 1.08 (2.64) |
| right | night_n1_near025_18900 | 0.834 | 95/100 | 0 | 80 | 2.01 ± 1.45 (1.76) | 15.18 ± 29.31 (6.21) | 2.33 ± 0.73 (2.58) | 4.83 ± 1.58 (5.65) | 2.32 ± 1.04 (2.66) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | night_n1_near025_18900 | 0.913 | 25/25 | 0 | 22 | 1.63 ± 1.65 (1.32) | 7.23 ± 11.89 (3.41) | 2.16 ± 0.70 (2.19) | 4.55 ± 1.55 (4.41) | 2.05 ± 0.94 (1.83) |
| forward/right | night_n1_near025_18900 | 0.834 | 24/25 | 0 | 21 | 2.10 ± 2.69 (1.39) | 9.49 ± 9.73 (7.49) | 2.19 ± 0.64 (2.08) | 4.48 ± 1.42 (4.13) | 2.02 ± 0.91 (1.71) |
| left/left | night_n1_near025_18900 | 0.909 | 25/25 | 0 | 22 | 1.66 ± 0.41 (1.72) | 11.21 ± 17.00 (6.80) | 2.43 ± 0.73 (2.68) | 5.05 ± 1.61 (5.91) | 2.52 ± 1.01 (2.99) |
| left/right | night_n1_near025_18900 | 0.849 | 24/25 | 0 | 20 | 1.80 ± 0.52 (1.97) | 22.99 ± 41.52 (6.08) | 2.33 ± 0.83 (2.69) | 4.94 ± 1.82 (5.80) | 2.42 ± 1.16 (2.92) |
| back/left | night_n1_near025_18900 | 0.815 | 25/25 | 0 | 20 | 2.32 ± 0.65 (2.42) | 33.30 ± 54.14 (9.52) | 2.25 ± 0.93 (2.73) | 4.70 ± 1.96 (5.92) | 2.34 ± 1.27 (3.13) |
| back/right | night_n1_near025_18900 | 0.776 | 23/25 | 0 | 19 | 2.53 ± 0.47 (2.54) | 15.29 ± 32.19 (8.84) | 2.46 ± 0.72 (2.80) | 5.11 ± 1.55 (5.84) | 2.57 ± 1.01 (3.07) |
| right/left | night_n1_near025_18900 | 0.905 | 25/25 | 0 | 22 | 1.82 ± 0.47 (1.90) | 18.96 ± 38.37 (5.57) | 2.24 ± 0.70 (2.46) | 4.69 ± 1.54 (5.38) | 2.19 ± 1.00 (2.53) |
| right/right | night_n1_near025_18900 | 0.877 | 24/25 | 0 | 20 | 1.63 ± 0.46 (1.64) | 12.96 ± 22.15 (5.17) | 2.33 ± 0.68 (2.48) | 4.82 ± 1.45 (5.40) | 2.30 ± 0.97 (2.64) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| night_n1_near025_18900 | strong | 0.863 | 13.5 | 5.63 | 2.89 |
| night_n1_near025_18900 | normal | 0.856 | 19.5 | 3.94 | 1.70 |

## Notes

- night_n1_near025_18900: score 0.860, 195/200 kicked, 0 fell; worst sector back (0.796).

# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **night_n1_near025_18600** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-45_night_n1_near025/model_18600.pt`.

## Overall

| Metric | night_n1_near025_18600 |
|---|---|
| **Score** | **0.836** |
| Kicked / fell | 187 / 0 |
| Kicks within 15° | 164 |
| Weak kicks (< 0.3 m) | 6 |
| Time to kick [s] | 1.92 ± 0.86 (1.80) |
| Direction error [°] | 15.06 ± 32.46 (4.69) |
| Avg ball speed [m/s] | 1.87 ± 0.47 (1.94) |
| Peak ball speed [m/s] | 4.36 ± 1.15 (4.58) |
| Distance [m] | 1.68 ± 0.65 (1.69) |
| Path length [m] | 1.69 ± 0.66 (1.70) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | night_n1_near025_18600 | 0.841 | 45/50 | 0 | 41 | 1.36 ± 0.28 (1.36) | 6.73 ± 10.08 (3.05) | 1.83 ± 0.50 (1.86) | 4.28 ± 1.27 (4.05) | 1.66 ± 0.73 (1.50) |
| left | night_n1_near025_18600 | 0.864 | 48/50 | 0 | 40 | 1.73 ± 0.52 (1.82) | 18.97 ± 35.60 (4.76) | 1.89 ± 0.54 (2.00) | 4.41 ± 1.28 (4.81) | 1.72 ± 0.73 (1.91) |
| back | night_n1_near025_18600 | 0.791 | 47/50 | 0 | 42 | 2.61 ± 0.68 (2.74) | 19.68 ± 44.25 (6.62) | 1.94 ± 0.41 (2.01) | 4.51 ± 1.01 (4.60) | 1.77 ± 0.58 (1.78) |
| right | night_n1_near025_18600 | 0.849 | 47/50 | 0 | 41 | 1.94 ± 1.14 (1.80) | 14.43 ± 27.20 (4.69) | 1.82 ± 0.42 (1.89) | 4.24 ± 0.98 (4.52) | 1.57 ± 0.53 (1.65) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | night_n1_near025_18600 | 0.874 | 97/100 | 0 | 87 | 1.98 ± 0.99 (1.84) | 13.39 ± 30.83 (4.81) | 1.92 ± 0.40 (1.99) | 4.47 ± 0.98 (4.60) | 1.75 ± 0.56 (1.77) |
| right | night_n1_near025_18600 | 0.798 | 90/100 | 0 | 77 | 1.85 ± 0.69 (1.76) | 16.86 ± 34.04 (4.61) | 1.82 ± 0.54 (1.89) | 4.24 ± 1.29 (4.51) | 1.61 ± 0.73 (1.62) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | night_n1_near025_18600 | 0.880 | 23/25 | 0 | 22 | 1.39 ± 0.29 (1.34) | 5.35 ± 10.44 (2.07) | 1.98 ± 0.30 (1.94) | 4.59 ± 0.84 (4.29) | 1.80 ± 0.49 (1.64) |
| forward/right | night_n1_near025_18600 | 0.801 | 22/25 | 0 | 19 | 1.33 ± 0.28 (1.36) | 8.16 ± 9.48 (4.28) | 1.68 ± 0.61 (1.62) | 3.97 ± 1.54 (3.59) | 1.50 ± 0.89 (1.31) |
| left/left | night_n1_near025_18600 | 0.926 | 25/25 | 0 | 22 | 1.68 ± 0.46 (1.82) | 11.16 ± 22.07 (4.02) | 1.95 ± 0.47 (2.00) | 4.54 ± 1.12 (4.90) | 1.81 ± 0.64 (1.91) |
| left/right | night_n1_near025_18600 | 0.802 | 23/25 | 0 | 18 | 1.78 ± 0.58 (1.96) | 27.46 ± 44.46 (6.22) | 1.81 ± 0.60 (1.89) | 4.25 ± 1.41 (4.65) | 1.62 ± 0.81 (1.71) |
| back/left | night_n1_near025_18600 | 0.804 | 24/25 | 0 | 21 | 2.64 ± 0.72 (2.75) | 20.62 ± 46.44 (7.43) | 1.94 ± 0.34 (2.00) | 4.57 ± 0.87 (4.60) | 1.81 ± 0.52 (1.85) |
| back/right | night_n1_near025_18600 | 0.778 | 23/25 | 0 | 21 | 2.58 ± 0.63 (2.72) | 18.71 ± 41.83 (5.33) | 1.94 ± 0.47 (2.02) | 4.45 ± 1.14 (4.73) | 1.74 ± 0.63 (1.65) |
| right/left | night_n1_near025_18600 | 0.887 | 25/25 | 0 | 22 | 2.18 ± 1.46 (1.92) | 16.07 ± 30.16 (5.27) | 1.82 ± 0.44 (1.91) | 4.21 ± 1.00 (4.46) | 1.58 ± 0.53 (1.67) |
| right/right | night_n1_near025_18600 | 0.811 | 22/25 | 0 | 19 | 1.66 ± 0.47 (1.72) | 12.56 ± 23.25 (3.49) | 1.82 ± 0.40 (1.87) | 4.28 ± 0.96 (4.59) | 1.57 ± 0.53 (1.63) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| night_n1_near025_18600 | strong | 0.839 | 11.2 | 4.95 | 2.00 |
| night_n1_near025_18600 | normal | 0.834 | 18.9 | 3.78 | 1.36 |

## Notes

- night_n1_near025_18600: score 0.836, 187/200 kicked, 0 fell; worst sector back (0.791).

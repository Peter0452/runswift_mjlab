# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **night_n2_near04_18900** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-48_night_n2_near04/model_18900.pt`.

## Overall

| Metric | night_n2_near04_18900 |
|---|---|
| **Score** | **0.840** |
| Kicked / fell | 190 / 0 |
| Kicks within 15° | 156 |
| Weak kicks (< 0.3 m) | 4 |
| Time to kick [s] | 1.77 ± 0.93 (1.66) |
| Direction error [°] | 19.98 ± 38.69 (6.02) |
| Avg ball speed [m/s] | 1.84 ± 0.51 (1.97) |
| Peak ball speed [m/s] | 4.39 ± 1.26 (4.73) |
| Distance [m] | 1.67 ± 0.67 (1.73) |
| Path length [m] | 1.68 ± 0.67 (1.75) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | night_n2_near04_18900 | 0.850 | 47/50 | 0 | 39 | 1.48 ± 1.46 (1.30) | 11.46 ± 21.51 (4.38) | 1.77 ± 0.52 (1.88) | 4.20 ± 1.34 (4.18) | 1.55 ± 0.70 (1.61) |
| left | night_n2_near04_18900 | 0.848 | 48/50 | 0 | 38 | 1.62 ± 0.50 (1.68) | 22.42 ± 37.30 (6.79) | 1.83 ± 0.54 (2.01) | 4.38 ± 1.28 (4.98) | 1.66 ± 0.67 (1.86) |
| back | night_n2_near04_18900 | 0.798 | 47/50 | 0 | 39 | 2.34 ± 0.60 (2.40) | 28.02 ± 53.76 (8.79) | 1.91 ± 0.50 (2.01) | 4.54 ± 1.24 (4.90) | 1.80 ± 0.65 (1.89) |
| right | night_n2_near04_18900 | 0.864 | 48/50 | 0 | 40 | 1.66 ± 0.56 (1.66) | 18.01 ± 33.26 (5.82) | 1.86 ± 0.45 (1.90) | 4.42 ± 1.13 (4.73) | 1.67 ± 0.63 (1.73) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | night_n2_near04_18900 | 0.876 | 98/100 | 0 | 84 | 1.72 ± 0.64 (1.67) | 18.08 ± 36.82 (5.36) | 1.90 ± 0.48 (2.01) | 4.51 ± 1.19 (4.90) | 1.73 ± 0.64 (1.79) |
| right | night_n2_near04_18900 | 0.804 | 92/100 | 0 | 72 | 1.83 ± 1.17 (1.63) | 22.01 ± 40.49 (6.79) | 1.78 ± 0.53 (1.92) | 4.26 ± 1.31 (4.53) | 1.61 ± 0.69 (1.70) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | night_n2_near04_18900 | 0.907 | 24/25 | 0 | 22 | 1.23 ± 0.27 (1.25) | 6.58 ± 11.47 (3.22) | 1.92 ± 0.34 (2.00) | 4.55 ± 0.90 (4.54) | 1.67 ± 0.54 (1.63) |
| forward/right | night_n2_near04_18900 | 0.793 | 23/25 | 0 | 17 | 1.75 ± 2.04 (1.30) | 16.55 ± 27.53 (6.09) | 1.61 ± 0.62 (1.76) | 3.84 ± 1.60 (3.98) | 1.42 ± 0.81 (1.33) |
| left/left | night_n2_near04_18900 | 0.894 | 25/25 | 0 | 21 | 1.53 ± 0.43 (1.64) | 16.03 ± 25.14 (8.28) | 1.90 ± 0.55 (2.01) | 4.52 ± 1.26 (5.02) | 1.77 ± 0.64 (1.87) |
| left/right | night_n2_near04_18900 | 0.802 | 23/25 | 0 | 17 | 1.71 ± 0.55 (1.90) | 29.36 ± 46.08 (6.37) | 1.76 ± 0.51 (1.99) | 4.22 ± 1.29 (4.94) | 1.54 ± 0.69 (1.77) |
| back/left | night_n2_near04_18900 | 0.804 | 24/25 | 0 | 20 | 2.41 ± 0.62 (2.49) | 28.15 ± 53.23 (9.93) | 1.93 ± 0.49 (2.00) | 4.58 ± 1.24 (4.90) | 1.84 ± 0.67 (1.98) |
| back/right | night_n2_near04_18900 | 0.792 | 23/25 | 0 | 19 | 2.26 ± 0.56 (2.40) | 27.89 ± 54.31 (7.60) | 1.88 ± 0.51 (2.01) | 4.51 ± 1.24 (4.90) | 1.76 ± 0.62 (1.82) |
| right/left | night_n2_near04_18900 | 0.900 | 25/25 | 0 | 21 | 1.70 ± 0.48 (1.72) | 21.50 ± 39.95 (5.40) | 1.83 ± 0.50 (2.06) | 4.39 ± 1.29 (4.88) | 1.65 ± 0.69 (1.75) |
| right/right | night_n2_near04_18900 | 0.828 | 23/25 | 0 | 19 | 1.60 ± 0.62 (1.48) | 14.22 ± 23.38 (7.12) | 1.89 ± 0.39 (1.85) | 4.46 ± 0.94 (4.71) | 1.70 ± 0.56 (1.70) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| night_n2_near04_18900 | strong | 0.835 | 16.5 | 4.96 | 1.95 |
| night_n2_near04_18900 | normal | 0.845 | 23.3 | 3.84 | 1.40 |

## Notes

- night_n2_near04_18900: score 0.840, 190/200 kicked, 0 fell; worst sector back (0.798).

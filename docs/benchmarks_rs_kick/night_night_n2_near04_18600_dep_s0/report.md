# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **night_n2_near04_18600** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-48_night_n2_near04/model_18600.pt`.

## Overall

| Metric | night_n2_near04_18600 |
|---|---|
| **Score** | **0.829** |
| Kicked / fell | 190 / 0 |
| Kicks within 15° | 156 |
| Weak kicks (< 0.3 m) | 17 |
| Time to kick [s] | 1.88 ± 0.87 (1.78) |
| Direction error [°] | 21.06 ± 41.92 (5.83) |
| Avg ball speed [m/s] | 1.91 ± 0.67 (2.11) |
| Peak ball speed [m/s] | 4.19 ± 1.57 (4.88) |
| Distance [m] | 1.64 ± 0.80 (1.71) |
| Path length [m] | 1.65 ± 0.81 (1.72) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | night_n2_near04_18600 | 0.865 | 48/50 | 0 | 41 | 1.57 ± 1.25 (1.38) | 7.58 ± 9.16 (5.50) | 1.88 ± 0.70 (2.00) | 4.04 ± 1.60 (3.92) | 1.56 ± 0.82 (1.51) |
| left | night_n2_near04_18600 | 0.841 | 48/50 | 0 | 38 | 1.70 ± 0.53 (1.81) | 23.15 ± 39.23 (5.75) | 1.86 ± 0.67 (2.06) | 4.18 ± 1.58 (4.92) | 1.61 ± 0.80 (1.77) |
| back | night_n2_near04_18600 | 0.767 | 47/50 | 0 | 38 | 2.51 ± 0.61 (2.68) | 33.24 ± 59.32 (7.74) | 1.97 ± 0.73 (2.16) | 4.29 ± 1.65 (4.99) | 1.77 ± 0.86 (1.99) |
| right | night_n2_near04_18600 | 0.844 | 47/50 | 0 | 39 | 1.75 ± 0.52 (1.78) | 20.52 ± 39.87 (4.27) | 1.94 ± 0.58 (2.12) | 4.26 ± 1.41 (4.90) | 1.63 ± 0.71 (1.83) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | night_n2_near04_18600 | 0.871 | 99/100 | 0 | 83 | 1.90 ± 0.99 (1.78) | 20.45 ± 42.12 (4.66) | 1.95 ± 0.64 (2.13) | 4.25 ± 1.49 (4.92) | 1.66 ± 0.76 (1.83) |
| right | night_n2_near04_18600 | 0.788 | 91/100 | 0 | 73 | 1.86 ± 0.71 (1.78) | 21.73 ± 41.69 (6.46) | 1.88 ± 0.71 (2.03) | 4.13 ± 1.64 (4.62) | 1.62 ± 0.85 (1.65) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | night_n2_near04_18600 | 0.919 | 25/25 | 0 | 23 | 1.66 ± 1.55 (1.30) | 6.52 ± 10.30 (3.40) | 1.99 ± 0.57 (2.13) | 4.30 ± 1.37 (4.24) | 1.67 ± 0.67 (1.60) |
| forward/right | night_n2_near04_18600 | 0.810 | 23/25 | 0 | 18 | 1.47 ± 0.80 (1.40) | 8.73 ± 7.58 (7.00) | 1.76 ± 0.80 (1.79) | 3.75 ± 1.77 (3.70) | 1.44 ± 0.93 (1.40) |
| left/left | night_n2_near04_18600 | 0.888 | 25/25 | 0 | 20 | 1.60 ± 0.45 (1.74) | 17.28 ± 28.65 (6.07) | 1.90 ± 0.66 (2.06) | 4.22 ± 1.55 (4.97) | 1.65 ± 0.76 (1.86) |
| left/right | night_n2_near04_18600 | 0.795 | 23/25 | 0 | 18 | 1.81 ± 0.58 (1.96) | 29.53 ± 47.35 (5.44) | 1.83 ± 0.67 (2.00) | 4.13 ± 1.62 (4.76) | 1.57 ± 0.83 (1.61) |
| back/left | night_n2_near04_18600 | 0.792 | 24/25 | 0 | 20 | 2.51 ± 0.73 (2.69) | 31.29 ± 58.31 (6.62) | 2.03 ± 0.65 (2.18) | 4.40 ± 1.49 (5.00) | 1.81 ± 0.83 (2.09) |
| back/right | night_n2_near04_18600 | 0.742 | 23/25 | 0 | 18 | 2.51 ± 0.46 (2.66) | 35.27 ± 60.29 (8.86) | 1.91 ± 0.79 (2.12) | 4.18 ± 1.80 (4.97) | 1.73 ± 0.89 (1.83) |
| right/left | night_n2_near04_18600 | 0.884 | 25/25 | 0 | 20 | 1.84 ± 0.55 (1.82) | 27.13 ± 49.74 (3.63) | 1.86 ± 0.65 (2.07) | 4.07 ± 1.54 (4.17) | 1.53 ± 0.74 (1.65) |
| right/right | night_n2_near04_18600 | 0.805 | 22/25 | 0 | 19 | 1.65 ± 0.46 (1.75) | 13.00 ± 21.86 (4.95) | 2.03 ± 0.48 (2.20) | 4.46 ± 1.21 (5.08) | 1.74 ± 0.66 (1.87) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| night_n2_near04_18600 | strong | 0.826 | 18.2 | 4.83 | 1.99 |
| night_n2_near04_18600 | normal | 0.832 | 23.9 | 3.57 | 1.30 |

## Notes

- night_n2_near04_18600: score 0.829, 190/200 kicked, 0 fell; worst sector back (0.767).

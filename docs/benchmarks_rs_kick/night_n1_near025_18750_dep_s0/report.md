# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **night_n1_near025_18750** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-45_night_n1_near025/model_18750.pt`.

## Overall

| Metric | night_n1_near025_18750 |
|---|---|
| **Score** | **0.848** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 160 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 2.19 ± 1.92 (1.80) |
| Direction error [°] | 22.45 ± 41.28 (5.86) |
| Avg ball speed [m/s] | 1.73 ± 0.58 (1.89) |
| Peak ball speed [m/s] | 4.36 ± 1.47 (4.71) |
| Distance [m] | 1.81 ± 0.80 (1.94) |
| Path length [m] | 1.82 ± 0.80 (1.95) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | night_n1_near025_18750 | 0.876 | 50/50 | 0 | 41 | 1.73 ± 1.89 (1.35) | 11.67 ± 17.85 (5.10) | 1.65 ± 0.58 (1.85) | 4.13 ± 1.46 (4.51) | 1.66 ± 0.76 (1.87) |
| left | night_n1_near025_18750 | 0.859 | 49/50 | 0 | 40 | 1.90 ± 1.46 (1.86) | 19.84 ± 33.20 (6.19) | 1.76 ± 0.50 (1.92) | 4.50 ± 1.30 (5.06) | 1.85 ± 0.72 (1.95) |
| back | night_n1_near025_18750 | 0.804 | 50/50 | 0 | 40 | 2.79 ± 1.77 (2.68) | 33.12 ± 57.87 (6.51) | 1.79 ± 0.65 (2.02) | 4.49 ± 1.61 (5.24) | 1.94 ± 0.90 (2.23) |
| right | night_n1_near025_18750 | 0.851 | 50/50 | 0 | 39 | 2.34 ± 2.28 (1.80) | 25.11 ± 42.31 (5.90) | 1.73 ± 0.59 (1.84) | 4.33 ± 1.46 (4.60) | 1.81 ± 0.77 (1.89) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | night_n1_near025_18750 | 0.858 | 100/100 | 0 | 80 | 2.03 ± 1.52 (1.80) | 23.74 ± 43.63 (6.09) | 1.76 ± 0.56 (1.91) | 4.39 ± 1.40 (4.66) | 1.82 ± 0.75 (1.93) |
| right | night_n1_near025_18750 | 0.837 | 99/100 | 0 | 80 | 2.36 ± 2.24 (1.78) | 21.14 ± 38.71 (5.55) | 1.71 ± 0.61 (1.88) | 4.34 ± 1.54 (4.75) | 1.81 ± 0.84 (1.95) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | night_n1_near025_18750 | 0.889 | 25/25 | 0 | 21 | 1.51 ± 1.32 (1.30) | 12.51 ± 21.56 (3.35) | 1.71 ± 0.51 (1.89) | 4.23 ± 1.30 (4.52) | 1.69 ± 0.66 (1.86) |
| forward/right | night_n1_near025_18750 | 0.862 | 25/25 | 0 | 20 | 1.95 ± 2.30 (1.36) | 10.83 ± 13.09 (5.41) | 1.58 ± 0.63 (1.78) | 4.03 ± 1.61 (4.51) | 1.63 ± 0.84 (1.88) |
| left/left | night_n1_near025_18750 | 0.890 | 25/25 | 0 | 20 | 1.56 ± 0.48 (1.68) | 17.68 ± 27.32 (6.45) | 1.79 ± 0.53 (1.92) | 4.47 ± 1.33 (5.06) | 1.84 ± 0.72 (2.08) |
| left/right | night_n1_near025_18750 | 0.828 | 24/25 | 0 | 20 | 2.26 ± 1.96 (2.00) | 22.09 ± 38.25 (5.76) | 1.73 ± 0.46 (1.85) | 4.54 ± 1.28 (5.01) | 1.86 ± 0.73 (1.92) |
| back/left | night_n1_near025_18750 | 0.800 | 25/25 | 0 | 20 | 2.79 ± 1.56 (2.66) | 36.58 ± 62.15 (6.53) | 1.81 ± 0.62 (2.02) | 4.56 ± 1.53 (5.22) | 1.98 ± 0.88 (2.26) |
| back/right | night_n1_near025_18750 | 0.809 | 25/25 | 0 | 20 | 2.80 ± 1.95 (2.72) | 29.66 ± 53.02 (5.71) | 1.77 ± 0.68 (2.02) | 4.41 ± 1.68 (5.25) | 1.89 ± 0.91 (2.21) |
| right/left | night_n1_near025_18750 | 0.854 | 25/25 | 0 | 19 | 2.24 ± 1.91 (1.94) | 28.21 ± 46.84 (5.95) | 1.71 ± 0.56 (1.83) | 4.30 ± 1.40 (4.49) | 1.76 ± 0.71 (1.89) |
| right/right | night_n1_near025_18750 | 0.849 | 25/25 | 0 | 20 | 2.44 ± 2.59 (1.72) | 22.02 ± 36.96 (5.86) | 1.75 ± 0.62 (1.86) | 4.37 ± 1.51 (4.75) | 1.86 ± 0.82 (1.98) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| night_n1_near025_18750 | strong | 0.837 | 21.7 | 4.77 | 2.03 |
| night_n1_near025_18750 | normal | 0.858 | 23.2 | 3.96 | 1.60 |

## Notes

- night_n1_near025_18750: score 0.848, 199/200 kicked, 0 fell; worst sector back (0.804).

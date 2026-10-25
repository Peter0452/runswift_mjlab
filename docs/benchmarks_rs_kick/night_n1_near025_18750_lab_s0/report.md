# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **night_n1_near025_18750** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-45_night_n1_near025/model_18750.pt`.

## Overall

| Metric | night_n1_near025_18750 |
|---|---|
| **Score** | **0.937** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.63 ± 0.56 (1.54) |
| Direction error [°] | 5.47 ± 3.39 (4.94) |
| Avg ball speed [m/s] | 1.67 ± 0.25 (1.72) |
| Peak ball speed [m/s] | 3.66 ± 0.61 (3.73) |
| Distance [m] | 1.17 ± 0.32 (1.19) |
| Path length [m] | 1.18 ± 0.32 (1.19) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | night_n1_near025_18750 | 0.953 | 50/50 | 0 | 49 | 1.05 ± 0.23 (1.06) | 4.32 ± 3.04 (4.08) | 1.45 ± 0.29 (1.50) | 3.16 ± 0.63 (3.18) | 0.90 ± 0.31 (0.94) |
| left | night_n1_near025_18750 | 0.947 | 50/50 | 0 | 50 | 1.56 ± 0.35 (1.56) | 5.28 ± 2.95 (4.72) | 1.71 ± 0.21 (1.73) | 3.79 ± 0.56 (3.96) | 1.24 ± 0.30 (1.24) |
| back | night_n1_near025_18750 | 0.907 | 50/50 | 0 | 50 | 2.36 ± 0.28 (2.31) | 6.58 ± 3.38 (7.01) | 1.82 ± 0.14 (1.85) | 3.99 ± 0.39 (4.06) | 1.37 ± 0.20 (1.38) |
| right | night_n1_near025_18750 | 0.942 | 50/50 | 0 | 49 | 1.54 ± 0.35 (1.52) | 5.69 ± 3.73 (4.82) | 1.69 ± 0.19 (1.72) | 3.68 ± 0.50 (3.66) | 1.19 ± 0.24 (1.18) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | night_n1_near025_18750 | 0.937 | 100/100 | 0 | 100 | 1.63 ± 0.56 (1.56) | 5.49 ± 3.19 (4.78) | 1.68 ± 0.23 (1.72) | 3.67 ± 0.57 (3.73) | 1.18 ± 0.30 (1.20) |
| right | night_n1_near025_18750 | 0.938 | 100/100 | 0 | 98 | 1.63 ± 0.56 (1.54) | 5.45 ± 3.58 (5.05) | 1.66 ± 0.28 (1.72) | 3.64 ± 0.65 (3.74) | 1.17 ± 0.33 (1.17) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | night_n1_near025_18750 | 0.952 | 25/25 | 0 | 25 | 1.05 ± 0.22 (1.08) | 4.45 ± 2.80 (4.22) | 1.48 ± 0.21 (1.48) | 3.17 ± 0.45 (3.23) | 0.91 ± 0.26 (0.91) |
| forward/right | night_n1_near025_18750 | 0.954 | 25/25 | 0 | 24 | 1.05 ± 0.23 (1.04) | 4.18 ± 3.25 (2.52) | 1.43 ± 0.36 (1.51) | 3.15 ± 0.77 (3.14) | 0.89 ± 0.35 (0.97) |
| left/left | night_n1_near025_18750 | 0.940 | 25/25 | 0 | 25 | 1.45 ± 0.35 (1.50) | 6.02 ± 3.14 (6.42) | 1.67 ± 0.21 (1.68) | 3.66 ± 0.58 (3.68) | 1.18 ± 0.28 (1.21) |
| left/right | night_n1_near025_18750 | 0.954 | 25/25 | 0 | 25 | 1.67 ± 0.32 (1.68) | 4.54 ± 2.55 (3.51) | 1.76 ± 0.20 (1.77) | 3.93 ± 0.51 (4.03) | 1.30 ± 0.30 (1.26) |
| back/left | night_n1_near025_18750 | 0.907 | 25/25 | 0 | 25 | 2.37 ± 0.28 (2.32) | 6.56 ± 3.62 (7.32) | 1.84 ± 0.11 (1.85) | 4.02 ± 0.34 (4.04) | 1.39 ± 0.20 (1.41) |
| back/right | night_n1_near025_18750 | 0.908 | 25/25 | 0 | 25 | 2.35 ± 0.28 (2.30) | 6.61 ± 3.12 (6.81) | 1.80 ± 0.16 (1.84) | 3.96 ± 0.43 (4.07) | 1.34 ± 0.21 (1.35) |
| right/left | night_n1_near025_18750 | 0.950 | 25/25 | 0 | 25 | 1.65 ± 0.32 (1.64) | 4.93 ± 2.63 (4.24) | 1.75 ± 0.18 (1.76) | 3.84 ± 0.51 (3.87) | 1.25 ± 0.25 (1.24) |
| right/right | night_n1_near025_18750 | 0.935 | 25/25 | 0 | 24 | 1.44 ± 0.35 (1.48) | 6.45 ± 4.45 (6.42) | 1.64 ± 0.18 (1.64) | 3.53 ± 0.44 (3.54) | 1.13 ± 0.22 (1.14) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| night_n1_near025_18750 | strong | 0.936 | 5.4 | 3.94 | 1.29 |
| night_n1_near025_18750 | normal | 0.939 | 5.5 | 3.37 | 1.06 |

## Notes

- night_n1_near025_18750: score 0.937, 200/200 kicked, 0 fell; worst sector back (0.907).

# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **night_n2_near04_18750** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-48_night_n2_near04/model_18750.pt`.

## Overall

| Metric | night_n2_near04_18750 |
|---|---|
| **Score** | **0.944** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.60 ± 0.54 (1.52) |
| Direction error [°] | 4.88 ± 2.91 (4.51) |
| Avg ball speed [m/s] | 1.76 ± 0.32 (1.81) |
| Peak ball speed [m/s] | 3.80 ± 0.75 (3.89) |
| Distance [m] | 1.29 ± 0.41 (1.30) |
| Path length [m] | 1.30 ± 0.41 (1.30) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | night_n2_near04_18750 | 0.946 | 50/50 | 0 | 50 | 1.05 ± 0.23 (1.06) | 4.58 ± 2.82 (3.91) | 1.51 ± 0.35 (1.54) | 3.24 ± 0.77 (3.23) | 0.97 ± 0.37 (0.98) |
| left | night_n2_near04_18750 | 0.952 | 50/50 | 0 | 50 | 1.53 ± 0.35 (1.52) | 4.77 ± 2.92 (4.06) | 1.84 ± 0.27 (1.93) | 4.01 ± 0.68 (4.17) | 1.40 ± 0.38 (1.46) |
| back | night_n2_near04_18750 | 0.932 | 50/50 | 0 | 50 | 2.28 ± 0.28 (2.24) | 4.89 ± 2.55 (4.88) | 1.94 ± 0.20 (1.98) | 4.18 ± 0.56 (4.32) | 1.53 ± 0.33 (1.60) |
| right | night_n2_near04_18750 | 0.946 | 50/50 | 0 | 50 | 1.53 ± 0.34 (1.51) | 5.28 ± 3.27 (5.21) | 1.75 ± 0.25 (1.75) | 3.78 ± 0.62 (3.83) | 1.27 ± 0.34 (1.25) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | night_n2_near04_18750 | 0.945 | 100/100 | 0 | 100 | 1.59 ± 0.54 (1.52) | 4.81 ± 2.93 (4.21) | 1.77 ± 0.30 (1.81) | 3.81 ± 0.71 (3.90) | 1.30 ± 0.40 (1.33) |
| right | night_n2_near04_18750 | 0.943 | 100/100 | 0 | 100 | 1.60 ± 0.53 (1.52) | 4.95 ± 2.89 (4.80) | 1.75 ± 0.34 (1.81) | 3.80 ± 0.79 (3.88) | 1.28 ± 0.42 (1.28) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | night_n2_near04_18750 | 0.949 | 25/25 | 0 | 25 | 1.05 ± 0.23 (1.06) | 4.52 ± 3.06 (3.78) | 1.54 ± 0.29 (1.59) | 3.30 ± 0.60 (3.35) | 0.99 ± 0.32 (1.05) |
| forward/right | night_n2_near04_18750 | 0.943 | 25/25 | 0 | 25 | 1.06 ± 0.24 (1.06) | 4.64 ± 2.55 (5.02) | 1.48 ± 0.40 (1.41) | 3.19 ± 0.91 (3.02) | 0.95 ± 0.40 (0.85) |
| left/left | night_n2_near04_18750 | 0.955 | 25/25 | 0 | 25 | 1.42 ± 0.34 (1.46) | 4.53 ± 3.22 (3.49) | 1.80 ± 0.27 (1.90) | 3.87 ± 0.68 (4.07) | 1.33 ± 0.36 (1.44) |
| left/right | night_n2_near04_18750 | 0.949 | 25/25 | 0 | 25 | 1.64 ± 0.33 (1.62) | 5.01 ± 2.57 (4.52) | 1.89 ± 0.26 (1.97) | 4.14 ± 0.66 (4.32) | 1.47 ± 0.39 (1.49) |
| back/left | night_n2_near04_18750 | 0.924 | 25/25 | 0 | 25 | 2.28 ± 0.27 (2.24) | 5.57 ± 2.24 (5.79) | 1.96 ± 0.19 (1.97) | 4.23 ± 0.54 (4.34) | 1.57 ± 0.33 (1.65) |
| back/right | night_n2_near04_18750 | 0.939 | 25/25 | 0 | 25 | 2.28 ± 0.28 (2.24) | 4.21 ± 2.66 (4.15) | 1.93 ± 0.21 (2.02) | 4.14 ± 0.58 (4.31) | 1.49 ± 0.33 (1.42) |
| right/left | night_n2_near04_18750 | 0.951 | 25/25 | 0 | 25 | 1.62 ± 0.34 (1.60) | 4.62 ± 2.99 (4.83) | 1.78 ± 0.26 (1.80) | 3.84 ± 0.67 (3.88) | 1.32 ± 0.36 (1.35) |
| right/right | night_n2_near04_18750 | 0.940 | 25/25 | 0 | 25 | 1.44 ± 0.33 (1.46) | 5.94 ± 3.40 (6.34) | 1.72 ± 0.23 (1.72) | 3.72 ± 0.55 (3.66) | 1.23 ± 0.32 (1.23) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| night_n2_near04_18750 | strong | 0.939 | 5.2 | 4.16 | 1.47 |
| night_n2_near04_18750 | normal | 0.949 | 4.6 | 3.44 | 1.11 |

## Notes

- night_n2_near04_18750: score 0.944, 200/200 kicked, 0 fell; worst sector back (0.932).

# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **night_n2_near04_18900** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-48_night_n2_near04/model_18900.pt`.

## Overall

| Metric | night_n2_near04_18900 |
|---|---|
| **Score** | **0.938** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.52 ± 0.51 (1.44) |
| Direction error [°] | 5.85 ± 3.53 (5.45) |
| Avg ball speed [m/s] | 1.77 ± 0.30 (1.80) |
| Peak ball speed [m/s] | 3.89 ± 0.74 (3.94) |
| Distance [m] | 1.31 ± 0.41 (1.28) |
| Path length [m] | 1.32 ± 0.41 (1.28) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | night_n2_near04_18900 | 0.938 | 50/50 | 0 | 49 | 1.00 ± 0.22 (1.03) | 5.91 ± 3.75 (5.25) | 1.59 ± 0.32 (1.56) | 3.46 ± 0.66 (3.31) | 1.06 ± 0.38 (1.01) |
| left | night_n2_near04_18900 | 0.945 | 50/50 | 0 | 50 | 1.46 ± 0.33 (1.44) | 5.48 ± 3.60 (4.88) | 1.82 ± 0.26 (1.86) | 4.03 ± 0.64 (4.22) | 1.38 ± 0.34 (1.43) |
| back | night_n2_near04_18900 | 0.933 | 50/50 | 0 | 50 | 2.19 ± 0.26 (2.16) | 5.44 ± 2.89 (5.64) | 1.91 ± 0.26 (2.00) | 4.17 ± 0.70 (4.38) | 1.50 ± 0.41 (1.52) |
| right | night_n2_near04_18900 | 0.934 | 50/50 | 0 | 49 | 1.44 ± 0.31 (1.42) | 6.56 ± 3.71 (6.07) | 1.78 ± 0.29 (1.88) | 3.89 ± 0.74 (4.20) | 1.31 ± 0.37 (1.37) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | night_n2_near04_18900 | 0.934 | 100/100 | 0 | 99 | 1.52 ± 0.51 (1.44) | 6.23 ± 3.55 (5.72) | 1.79 ± 0.28 (1.81) | 3.91 ± 0.71 (3.95) | 1.33 ± 0.41 (1.30) |
| right | night_n2_near04_18900 | 0.942 | 100/100 | 0 | 99 | 1.52 ± 0.51 (1.45) | 5.47 ± 3.48 (4.88) | 1.76 ± 0.32 (1.79) | 3.87 ± 0.77 (3.94) | 1.30 ± 0.41 (1.27) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | night_n2_near04_18900 | 0.929 | 25/25 | 0 | 24 | 1.01 ± 0.21 (1.04) | 6.70 ± 4.13 (5.46) | 1.56 ± 0.25 (1.51) | 3.41 ± 0.53 (3.27) | 1.03 ± 0.34 (0.92) |
| forward/right | night_n2_near04_18900 | 0.947 | 25/25 | 0 | 25 | 1.00 ± 0.23 (1.02) | 5.11 ± 3.15 (4.16) | 1.61 ± 0.37 (1.67) | 3.52 ± 0.76 (3.45) | 1.09 ± 0.41 (1.10) |
| left/left | night_n2_near04_18900 | 0.937 | 25/25 | 0 | 25 | 1.36 ± 0.32 (1.40) | 6.29 ± 4.08 (5.71) | 1.77 ± 0.24 (1.80) | 3.90 ± 0.60 (3.91) | 1.31 ± 0.31 (1.33) |
| left/right | night_n2_near04_18900 | 0.953 | 25/25 | 0 | 25 | 1.56 ± 0.31 (1.56) | 4.67 ± 2.81 (4.11) | 1.87 ± 0.27 (1.98) | 4.17 ± 0.66 (4.54) | 1.45 ± 0.35 (1.51) |
| back/left | night_n2_near04_18900 | 0.932 | 25/25 | 0 | 25 | 2.21 ± 0.25 (2.18) | 5.55 ± 2.84 (5.68) | 1.95 ± 0.25 (2.01) | 4.24 ± 0.71 (4.40) | 1.56 ± 0.43 (1.65) |
| back/right | night_n2_near04_18900 | 0.934 | 25/25 | 0 | 25 | 2.16 ± 0.27 (2.16) | 5.32 ± 2.93 (5.60) | 1.88 ± 0.26 (1.99) | 4.11 ± 0.68 (4.36) | 1.45 ± 0.37 (1.42) |
| right/left | night_n2_near04_18900 | 0.936 | 25/25 | 0 | 25 | 1.52 ± 0.29 (1.52) | 6.36 ± 2.80 (6.37) | 1.86 ± 0.25 (1.92) | 4.11 ± 0.66 (4.46) | 1.42 ± 0.34 (1.42) |
| right/right | night_n2_near04_18900 | 0.932 | 25/25 | 0 | 24 | 1.36 ± 0.31 (1.38) | 6.76 ± 4.44 (5.94) | 1.69 ± 0.30 (1.70) | 3.68 ± 0.75 (3.67) | 1.20 ± 0.37 (1.23) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| night_n2_near04_18900 | strong | 0.940 | 5.5 | 4.29 | 1.51 |
| night_n2_near04_18900 | normal | 0.936 | 6.2 | 3.49 | 1.12 |

## Notes

- night_n2_near04_18900: score 0.938, 200/200 kicked, 0 fell; worst sector back (0.933).

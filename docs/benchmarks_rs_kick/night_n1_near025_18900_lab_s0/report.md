# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **night_n1_near025_18900** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-45_night_n1_near025/model_18900.pt`.

## Overall

| Metric | night_n1_near025_18900 |
|---|---|
| **Score** | **0.936** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.59 ± 0.52 (1.54) |
| Direction error [°] | 5.89 ± 3.76 (5.30) |
| Avg ball speed [m/s] | 1.82 ± 0.26 (1.83) |
| Peak ball speed [m/s] | 3.96 ± 0.64 (3.92) |
| Distance [m] | 1.42 ± 0.38 (1.36) |
| Path length [m] | 1.43 ± 0.38 (1.37) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | night_n1_near025_18900 | 0.938 | 50/50 | 0 | 49 | 1.08 ± 0.25 (1.11) | 5.75 ± 3.84 (5.15) | 1.61 ± 0.25 (1.62) | 3.45 ± 0.55 (3.42) | 1.11 ± 0.32 (1.12) |
| left | night_n1_near025_18900 | 0.940 | 50/50 | 0 | 50 | 1.53 ± 0.34 (1.55) | 5.97 ± 4.02 (4.90) | 1.85 ± 0.20 (1.89) | 4.05 ± 0.52 (4.23) | 1.47 ± 0.30 (1.51) |
| back | night_n1_near025_18900 | 0.932 | 50/50 | 0 | 50 | 2.24 ± 0.27 (2.24) | 5.30 ± 2.46 (5.49) | 1.97 ± 0.21 (1.98) | 4.29 ± 0.59 (4.43) | 1.64 ± 0.36 (1.67) |
| right | night_n1_near025_18900 | 0.934 | 50/50 | 0 | 50 | 1.52 ± 0.35 (1.53) | 6.55 ± 4.34 (6.16) | 1.86 ± 0.23 (1.86) | 4.03 ± 0.59 (4.11) | 1.46 ± 0.33 (1.45) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | night_n1_near025_18900 | 0.935 | 100/100 | 0 | 100 | 1.59 ± 0.52 (1.58) | 5.87 ± 3.45 (5.72) | 1.83 ± 0.27 (1.84) | 3.98 ± 0.68 (3.99) | 1.44 ± 0.40 (1.36) |
| right | night_n1_near025_18900 | 0.937 | 100/100 | 0 | 99 | 1.60 ± 0.51 (1.53) | 5.92 ± 4.05 (4.62) | 1.82 ± 0.24 (1.81) | 3.93 ± 0.60 (3.88) | 1.40 ± 0.36 (1.35) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | night_n1_near025_18900 | 0.942 | 25/25 | 0 | 25 | 1.05 ± 0.24 (1.10) | 5.07 ± 3.25 (4.03) | 1.57 ± 0.26 (1.62) | 3.36 ± 0.56 (3.39) | 1.06 ± 0.33 (1.12) |
| forward/right | night_n1_near025_18900 | 0.934 | 25/25 | 0 | 24 | 1.10 ± 0.27 (1.12) | 6.43 ± 4.24 (5.60) | 1.65 ± 0.24 (1.62) | 3.55 ± 0.51 (3.42) | 1.15 ± 0.30 (1.13) |
| left/left | night_n1_near025_18900 | 0.934 | 25/25 | 0 | 25 | 1.44 ± 0.34 (1.48) | 6.56 ± 4.13 (6.41) | 1.86 ± 0.20 (1.87) | 4.04 ± 0.53 (4.17) | 1.47 ± 0.30 (1.55) |
| left/right | night_n1_near025_18900 | 0.946 | 25/25 | 0 | 25 | 1.63 ± 0.32 (1.60) | 5.39 ± 3.82 (3.53) | 1.85 ± 0.20 (1.91) | 4.06 ± 0.51 (4.29) | 1.47 ± 0.30 (1.51) |
| back/left | night_n1_near025_18900 | 0.922 | 25/25 | 0 | 25 | 2.25 ± 0.26 (2.24) | 6.12 ± 2.22 (6.08) | 1.97 ± 0.19 (1.94) | 4.31 ± 0.56 (4.42) | 1.65 ± 0.37 (1.68) |
| back/right | night_n1_near025_18900 | 0.942 | 25/25 | 0 | 25 | 2.23 ± 0.27 (2.24) | 4.48 ± 2.42 (4.20) | 1.97 ± 0.22 (2.01) | 4.28 ± 0.62 (4.45) | 1.63 ± 0.36 (1.66) |
| right/left | night_n1_near025_18900 | 0.942 | 25/25 | 0 | 25 | 1.62 ± 0.33 (1.60) | 5.73 ± 3.71 (6.02) | 1.93 ± 0.23 (1.95) | 4.23 ± 0.61 (4.44) | 1.57 ± 0.34 (1.56) |
| right/right | night_n1_near025_18900 | 0.925 | 25/25 | 0 | 25 | 1.42 ± 0.34 (1.44) | 7.37 ± 4.75 (6.30) | 1.79 ± 0.20 (1.81) | 3.83 ± 0.49 (3.79) | 1.35 ± 0.28 (1.29) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| night_n1_near025_18900 | strong | 0.937 | 5.6 | 4.26 | 1.57 |
| night_n1_near025_18900 | normal | 0.935 | 6.2 | 3.65 | 1.27 |

## Notes

- night_n1_near025_18900: score 0.936, 200/200 kicked, 0 fell; worst sector back (0.932).

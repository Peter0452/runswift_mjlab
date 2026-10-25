# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-48_night_n2_near04/model_19049.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.934** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 194 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.54 ± 0.51 (1.46) |
| Direction error [°] | 7.37 ± 15.20 (5.32) |
| Avg ball speed [m/s] | 1.82 ± 0.38 (1.92) |
| Peak ball speed [m/s] | 4.01 ± 0.91 (4.24) |
| Distance [m] | 1.46 ± 0.52 (1.50) |
| Path length [m] | 1.47 ± 0.52 (1.51) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.937 | 50/50 | 0 | 49 | 1.03 ± 0.23 (1.06) | 6.12 ± 4.31 (5.08) | 1.64 ± 0.32 (1.56) | 3.55 ± 0.72 (3.27) | 1.16 ± 0.41 (0.99) |
| left | p | 0.940 | 50/50 | 0 | 49 | 1.47 ± 0.33 (1.49) | 5.95 ± 3.87 (5.02) | 1.93 ± 0.32 (2.03) | 4.28 ± 0.77 (4.60) | 1.61 ± 0.46 (1.68) |
| back | p | 0.916 | 50/50 | 0 | 48 | 2.18 ± 0.27 (2.15) | 11.59 ± 29.18 (5.43) | 1.90 ± 0.46 (2.06) | 4.19 ± 1.08 (4.63) | 1.62 ± 0.56 (1.73) |
| right | p | 0.942 | 50/50 | 0 | 48 | 1.47 ± 0.33 (1.44) | 5.82 ± 3.95 (5.50) | 1.82 ± 0.35 (1.87) | 4.00 ± 0.86 (4.03) | 1.46 ± 0.51 (1.44) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.934 | 100/100 | 0 | 96 | 1.54 ± 0.51 (1.46) | 7.40 ± 16.39 (5.16) | 1.83 ± 0.36 (1.88) | 4.02 ± 0.88 (4.13) | 1.47 ± 0.52 (1.43) |
| right | p | 0.933 | 100/100 | 0 | 98 | 1.53 ± 0.50 (1.46) | 7.34 ± 13.91 (5.71) | 1.82 ± 0.40 (1.94) | 3.99 ± 0.94 (4.33) | 1.45 ± 0.53 (1.58) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.933 | 25/25 | 0 | 24 | 1.03 ± 0.22 (1.06) | 6.41 ± 3.98 (5.60) | 1.63 ± 0.26 (1.58) | 3.55 ± 0.60 (3.25) | 1.16 ± 0.36 (1.04) |
| forward/right | p | 0.940 | 25/25 | 0 | 25 | 1.02 ± 0.24 (1.02) | 5.84 ± 4.60 (4.11) | 1.64 ± 0.37 (1.54) | 3.55 ± 0.81 (3.29) | 1.16 ± 0.45 (0.95) |
| left/left | p | 0.938 | 25/25 | 0 | 24 | 1.37 ± 0.33 (1.42) | 6.25 ± 4.56 (4.69) | 1.89 ± 0.31 (2.00) | 4.17 ± 0.76 (4.49) | 1.53 ± 0.44 (1.59) |
| left/right | p | 0.943 | 25/25 | 0 | 25 | 1.57 ± 0.31 (1.58) | 5.66 ± 3.00 (5.27) | 1.98 ± 0.32 (2.09) | 4.39 ± 0.77 (4.63) | 1.68 ± 0.46 (1.71) |
| back/left | p | 0.922 | 25/25 | 0 | 24 | 2.19 ± 0.29 (2.16) | 11.45 ± 31.64 (5.28) | 1.94 ± 0.42 (2.07) | 4.27 ± 1.03 (4.65) | 1.66 ± 0.57 (1.86) |
| back/right | p | 0.910 | 25/25 | 0 | 24 | 2.17 ± 0.25 (2.08) | 11.72 ± 26.48 (6.48) | 1.87 ± 0.49 (2.02) | 4.12 ± 1.12 (4.61) | 1.57 ± 0.56 (1.67) |
| right/left | p | 0.945 | 25/25 | 0 | 24 | 1.58 ± 0.30 (1.56) | 5.50 ± 3.75 (4.62) | 1.87 ± 0.36 (1.98) | 4.11 ± 0.88 (4.45) | 1.52 ± 0.52 (1.66) |
| right/right | p | 0.939 | 25/25 | 0 | 24 | 1.37 ± 0.33 (1.40) | 6.15 ± 4.12 (5.75) | 1.77 ± 0.34 (1.73) | 3.90 ± 0.81 (3.82) | 1.40 ± 0.48 (1.36) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.941 | 5.4 | 4.54 | 1.75 |
| p | normal | 0.927 | 9.3 | 3.47 | 1.18 |

## Notes

- p: score 0.934, 200/200 kicked, 0 fell; worst sector back (0.916).

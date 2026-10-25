# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_07-58-51_night_n3_aim025/model_19448.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.939** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.54 ± 0.53 (1.44) |
| Direction error [°] | 5.54 ± 3.33 (5.13) |
| Avg ball speed [m/s] | 1.91 ± 0.27 (1.92) |
| Peak ball speed [m/s] | 4.08 ± 0.67 (4.07) |
| Distance [m] | 1.52 ± 0.41 (1.48) |
| Path length [m] | 1.52 ± 0.41 (1.49) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.947 | 50/50 | 0 | 50 | 1.02 ± 0.27 (1.04) | 5.04 ± 3.19 (4.10) | 1.74 ± 0.26 (1.76) | 3.73 ± 0.64 (3.64) | 1.27 ± 0.36 (1.19) |
| left | p | 0.941 | 50/50 | 0 | 50 | 1.49 ± 0.35 (1.41) | 5.79 ± 3.25 (5.58) | 1.93 ± 0.26 (1.99) | 4.13 ± 0.65 (4.34) | 1.55 ± 0.38 (1.61) |
| back | p | 0.932 | 50/50 | 0 | 50 | 2.21 ± 0.31 (2.15) | 5.20 ± 2.84 (5.06) | 2.07 ± 0.21 (2.10) | 4.42 ± 0.56 (4.60) | 1.74 ± 0.36 (1.75) |
| right | p | 0.937 | 50/50 | 0 | 50 | 1.45 ± 0.34 (1.43) | 6.12 ± 3.86 (6.68) | 1.91 ± 0.26 (1.89) | 4.05 ± 0.65 (3.83) | 1.51 ± 0.39 (1.39) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.939 | 100/100 | 0 | 100 | 1.54 ± 0.53 (1.42) | 5.63 ± 3.16 (5.55) | 1.92 ± 0.27 (1.94) | 4.10 ± 0.67 (4.16) | 1.53 ± 0.41 (1.53) |
| right | p | 0.940 | 100/100 | 0 | 100 | 1.55 ± 0.54 (1.50) | 5.45 ± 3.49 (4.85) | 1.91 ± 0.27 (1.90) | 4.06 ± 0.67 (3.99) | 1.50 ± 0.41 (1.44) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.943 | 25/25 | 0 | 25 | 1.02 ± 0.28 (1.02) | 5.38 ± 3.03 (5.47) | 1.73 ± 0.25 (1.76) | 3.70 ± 0.60 (3.62) | 1.26 ± 0.34 (1.16) |
| forward/right | p | 0.951 | 25/25 | 0 | 25 | 1.03 ± 0.26 (1.06) | 4.71 ± 3.32 (3.91) | 1.74 ± 0.27 (1.80) | 3.75 ± 0.67 (3.90) | 1.28 ± 0.38 (1.24) |
| left/left | p | 0.937 | 25/25 | 0 | 25 | 1.40 ± 0.34 (1.34) | 6.10 ± 3.32 (5.99) | 1.93 ± 0.25 (1.99) | 4.14 ± 0.64 (4.35) | 1.54 ± 0.36 (1.61) |
| left/right | p | 0.945 | 25/25 | 0 | 25 | 1.58 ± 0.34 (1.58) | 5.48 ± 3.14 (5.00) | 1.93 ± 0.26 (1.96) | 4.12 ± 0.65 (4.32) | 1.56 ± 0.39 (1.54) |
| back/left | p | 0.934 | 25/25 | 0 | 25 | 2.21 ± 0.26 (2.16) | 5.20 ± 2.86 (5.35) | 2.07 ± 0.23 (2.10) | 4.42 ± 0.60 (4.60) | 1.75 ± 0.39 (1.74) |
| back/right | p | 0.930 | 25/25 | 0 | 25 | 2.22 ± 0.35 (2.14) | 5.19 ± 2.82 (4.78) | 2.07 ± 0.19 (2.10) | 4.43 ± 0.52 (4.61) | 1.73 ± 0.33 (1.78) |
| right/left | p | 0.942 | 25/25 | 0 | 25 | 1.54 ± 0.34 (1.50) | 5.82 ± 3.33 (5.62) | 1.94 ± 0.25 (1.88) | 4.14 ± 0.64 (4.06) | 1.57 ± 0.38 (1.53) |
| right/right | p | 0.933 | 25/25 | 0 | 25 | 1.36 ± 0.32 (1.34) | 6.41 ± 4.30 (7.34) | 1.89 ± 0.27 (1.89) | 3.95 ± 0.65 (3.74) | 1.44 ± 0.39 (1.31) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.938 | 5.4 | 4.42 | 1.70 |
| p | normal | 0.941 | 5.7 | 3.74 | 1.34 |

## Notes

- p: score 0.939, 200/200 kicked, 0 fell; worst sector back (0.932).

# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-48_night_n2_near04/model_19049.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.924** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 189 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.53 ± 0.53 (1.39) |
| Direction error [°] | 8.37 ± 16.65 (6.31) |
| Avg ball speed [m/s] | 2.03 ± 0.44 (2.06) |
| Peak ball speed [m/s] | 4.37 ± 1.01 (4.51) |
| Distance [m] | 1.85 ± 0.64 (1.89) |
| Path length [m] | 1.86 ± 0.64 (1.90) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.930 | 50/50 | 0 | 47 | 1.01 ± 0.26 (1.04) | 6.99 ± 4.49 (6.30) | 1.96 ± 0.34 (1.96) | 4.22 ± 0.82 (4.25) | 1.71 ± 0.54 (1.66) |
| left | p | 0.936 | 50/50 | 0 | 46 | 1.45 ± 0.33 (1.38) | 6.45 ± 4.79 (5.25) | 2.05 ± 0.36 (2.12) | 4.40 ± 0.84 (4.63) | 1.86 ± 0.58 (1.99) |
| back | p | 0.903 | 50/50 | 0 | 48 | 2.19 ± 0.35 (2.21) | 13.09 ± 31.92 (6.77) | 2.14 ± 0.53 (2.31) | 4.60 ± 1.19 (5.08) | 2.04 ± 0.70 (2.28) |
| right | p | 0.927 | 50/50 | 0 | 48 | 1.46 ± 0.35 (1.40) | 6.95 ± 4.16 (6.27) | 1.98 ± 0.47 (1.95) | 4.26 ± 1.09 (4.14) | 1.80 ± 0.69 (1.70) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.928 | 100/100 | 0 | 94 | 1.54 ± 0.54 (1.37) | 6.58 ± 4.35 (5.96) | 2.06 ± 0.43 (2.14) | 4.43 ± 0.98 (4.67) | 1.89 ± 0.63 (2.06) |
| right | p | 0.920 | 100/100 | 0 | 95 | 1.52 ± 0.53 (1.45) | 10.15 ± 23.01 (6.92) | 2.01 ± 0.45 (1.99) | 4.31 ± 1.03 (4.31) | 1.82 ± 0.65 (1.80) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.936 | 25/25 | 0 | 24 | 1.01 ± 0.26 (1.00) | 6.44 ± 4.14 (5.86) | 1.94 ± 0.35 (1.83) | 4.15 ± 0.82 (3.88) | 1.67 ± 0.54 (1.45) |
| forward/right | p | 0.925 | 25/25 | 0 | 23 | 1.01 ± 0.25 (1.10) | 7.54 ± 4.74 (7.51) | 1.99 ± 0.33 (1.98) | 4.30 ± 0.81 (4.30) | 1.75 ± 0.54 (1.76) |
| left/left | p | 0.935 | 25/25 | 0 | 21 | 1.38 ± 0.32 (1.34) | 6.55 ± 5.56 (3.85) | 2.08 ± 0.33 (2.19) | 4.47 ± 0.80 (4.88) | 1.90 ± 0.52 (2.12) |
| left/right | p | 0.937 | 25/25 | 0 | 25 | 1.53 ± 0.33 (1.54) | 6.35 ± 3.88 (6.15) | 2.03 ± 0.38 (1.98) | 4.33 ± 0.87 (4.20) | 1.83 ± 0.63 (1.80) |
| back/left | p | 0.923 | 25/25 | 0 | 25 | 2.24 ± 0.27 (2.22) | 6.01 ± 3.53 (5.64) | 2.26 ± 0.36 (2.40) | 4.85 ± 0.86 (5.17) | 2.18 ± 0.59 (2.39) |
| back/right | p | 0.883 | 25/25 | 0 | 23 | 2.14 ± 0.41 (2.14) | 20.17 ± 43.88 (7.99) | 2.02 ± 0.64 (2.28) | 4.34 ± 1.41 (5.08) | 1.91 ± 0.78 (2.26) |
| right/left | p | 0.919 | 25/25 | 0 | 24 | 1.54 ± 0.35 (1.42) | 7.35 ± 3.79 (7.31) | 1.97 ± 0.55 (2.01) | 4.25 ± 1.24 (4.33) | 1.82 ± 0.73 (1.84) |
| right/right | p | 0.935 | 25/25 | 0 | 24 | 1.38 ± 0.32 (1.36) | 6.55 ± 4.47 (4.77) | 1.99 ± 0.37 (1.88) | 4.28 ± 0.91 (3.88) | 1.77 ± 0.63 (1.50) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.922 | 8.4 | 4.88 | 2.20 |
| p | normal | 0.926 | 8.4 | 3.86 | 1.51 |

## Notes

- p: score 0.924, 200/200 kicked, 0 fell; worst sector back (0.903).

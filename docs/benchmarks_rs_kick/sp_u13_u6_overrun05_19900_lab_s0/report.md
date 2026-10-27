# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_15-32-24_u13_u6_overrun05/model_19900.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.856** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.58 ± 0.52 (1.50) |
| Direction error [°] | 5.59 ± 11.33 (4.25) |
| Avg ball speed [m/s] | 1.76 ± 0.38 (1.87) |
| Peak ball speed [m/s] | 3.83 ± 0.91 (4.09) |
| Distance [m] | 1.31 ± 0.49 (1.36) |
| Path length [m] | 1.31 ± 0.49 (1.37) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.859 | 50/50 | 0 | 49 | 1.05 ± 0.23 (1.08) | 3.99 ± 3.50 (2.59) | 1.58 ± 0.41 (1.67) | 3.42 ± 0.90 (3.54) | 1.06 ± 0.46 (1.11) |
| left | p | 0.868 | 50/50 | 0 | 50 | 1.52 ± 0.34 (1.51) | 5.01 ± 3.23 (4.44) | 1.82 ± 0.31 (1.92) | 3.97 ± 0.76 (4.29) | 1.38 ± 0.42 (1.46) |
| back | p | 0.843 | 50/50 | 0 | 49 | 2.24 ± 0.24 (2.19) | 8.38 ± 21.69 (5.17) | 1.89 ± 0.38 (2.05) | 4.13 ± 0.91 (4.50) | 1.50 ± 0.50 (1.67) |
| right | p | 0.853 | 50/50 | 0 | 50 | 1.51 ± 0.35 (1.49) | 4.99 ± 3.00 (4.29) | 1.75 ± 0.35 (1.85) | 3.82 ± 0.89 (4.02) | 1.28 ± 0.45 (1.25) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.855 | 100/100 | 0 | 99 | 1.58 ± 0.53 (1.50) | 4.90 ± 3.28 (4.25) | 1.79 ± 0.35 (1.89) | 3.90 ± 0.85 (4.15) | 1.34 ± 0.47 (1.42) |
| right | p | 0.856 | 100/100 | 0 | 99 | 1.58 ± 0.51 (1.49) | 6.28 ± 15.65 (4.16) | 1.73 ± 0.41 (1.83) | 3.77 ± 0.95 (3.95) | 1.27 ± 0.50 (1.25) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.852 | 25/25 | 0 | 24 | 1.04 ± 0.22 (1.10) | 4.34 ± 3.93 (2.98) | 1.61 ± 0.35 (1.64) | 3.44 ± 0.79 (3.53) | 1.08 ± 0.43 (1.14) |
| forward/right | p | 0.865 | 25/25 | 0 | 25 | 1.06 ± 0.23 (1.06) | 3.63 ± 2.98 (2.44) | 1.56 ± 0.46 (1.72) | 3.39 ± 0.99 (3.54) | 1.04 ± 0.49 (1.08) |
| left/left | p | 0.861 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.46) | 5.43 ± 3.63 (4.45) | 1.77 ± 0.30 (1.89) | 3.86 ± 0.75 (4.23) | 1.32 ± 0.42 (1.42) |
| left/right | p | 0.875 | 25/25 | 0 | 25 | 1.64 ± 0.31 (1.64) | 4.60 ± 2.72 (3.95) | 1.87 ± 0.31 (2.00) | 4.09 ± 0.74 (4.41) | 1.44 ± 0.42 (1.54) |
| back/left | p | 0.842 | 25/25 | 0 | 25 | 2.26 ± 0.26 (2.20) | 5.24 ± 2.78 (4.97) | 1.94 ± 0.26 (2.07) | 4.22 ± 0.71 (4.57) | 1.54 ± 0.43 (1.73) |
| back/right | p | 0.844 | 25/25 | 0 | 24 | 2.21 ± 0.22 (2.18) | 11.51 ± 30.22 (5.55) | 1.84 ± 0.46 (2.03) | 4.03 ± 1.07 (4.47) | 1.46 ± 0.55 (1.64) |
| right/left | p | 0.864 | 25/25 | 0 | 25 | 1.62 ± 0.32 (1.58) | 4.61 ± 2.43 (4.28) | 1.84 ± 0.37 (2.02) | 4.07 ± 0.94 (4.63) | 1.42 ± 0.48 (1.60) |
| right/right | p | 0.842 | 25/25 | 0 | 25 | 1.41 ± 0.35 (1.44) | 5.38 ± 3.44 (5.05) | 1.66 ± 0.31 (1.65) | 3.56 ± 0.74 (3.43) | 1.15 ± 0.37 (1.13) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.864 | 4.8 | 4.35 | 1.56 |
| p | normal | 0.847 | 6.4 | 3.32 | 1.05 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.820 | 0.36 | 1.77 ± 0.60 (1.65) | 2.82 | 0.78 |
| p | medium | 16 | 0.920 | 0.86 | 0.95 ± 0.17 (0.98) | 3.08 | 0.92 |
| p | strong | 126 | 0.864 | 0.59 | - | 4.40 | 1.60 |

## Notes

- p: score 0.856, 200/200 kicked, 0 fell; worst sector back (0.843).

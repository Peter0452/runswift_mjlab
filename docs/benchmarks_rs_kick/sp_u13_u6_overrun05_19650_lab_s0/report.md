# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_15-32-24_u13_u6_overrun05/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.851** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.61 ± 0.54 (1.53) |
| Direction error [°] | 4.75 ± 2.96 (4.29) |
| Avg ball speed [m/s] | 1.91 ± 0.30 (1.97) |
| Peak ball speed [m/s] | 4.20 ± 0.75 (4.43) |
| Distance [m] | 1.56 ± 0.45 (1.63) |
| Path length [m] | 1.57 ± 0.45 (1.64) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.851 | 50/50 | 0 | 50 | 1.05 ± 0.22 (1.08) | 4.39 ± 2.76 (3.56) | 1.73 ± 0.34 (1.83) | 3.78 ± 0.80 (3.85) | 1.29 ± 0.45 (1.32) |
| left | p | 0.862 | 50/50 | 0 | 50 | 1.54 ± 0.34 (1.56) | 5.39 ± 3.29 (5.53) | 1.97 ± 0.25 (2.02) | 4.34 ± 0.66 (4.56) | 1.65 ± 0.39 (1.73) |
| back | p | 0.844 | 50/50 | 0 | 50 | 2.31 ± 0.27 (2.25) | 4.44 ± 2.25 (4.43) | 2.03 ± 0.24 (2.11) | 4.51 ± 0.67 (4.85) | 1.75 ± 0.42 (1.84) |
| right | p | 0.848 | 50/50 | 0 | 50 | 1.55 ± 0.34 (1.50) | 4.78 ± 3.31 (4.13) | 1.91 ± 0.25 (1.99) | 4.19 ± 0.67 (4.55) | 1.56 ± 0.39 (1.60) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.853 | 100/100 | 0 | 100 | 1.62 ± 0.54 (1.54) | 4.56 ± 3.01 (4.03) | 1.91 ± 0.26 (1.95) | 4.21 ± 0.70 (4.37) | 1.57 ± 0.42 (1.62) |
| right | p | 0.850 | 100/100 | 0 | 100 | 1.61 ± 0.54 (1.53) | 4.94 ± 2.90 (4.69) | 1.90 ± 0.33 (1.99) | 4.20 ± 0.80 (4.49) | 1.56 ± 0.47 (1.65) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.853 | 25/25 | 0 | 25 | 1.05 ± 0.21 (1.08) | 4.25 ± 2.87 (3.32) | 1.74 ± 0.26 (1.82) | 3.77 ± 0.64 (3.75) | 1.30 ± 0.38 (1.35) |
| forward/right | p | 0.849 | 25/25 | 0 | 25 | 1.05 ± 0.23 (1.08) | 4.52 ± 2.64 (3.66) | 1.72 ± 0.41 (1.91) | 3.78 ± 0.93 (4.04) | 1.28 ± 0.50 (1.28) |
| left/left | p | 0.849 | 25/25 | 0 | 25 | 1.45 ± 0.35 (1.50) | 6.02 ± 3.67 (6.03) | 1.91 ± 0.21 (1.94) | 4.19 ± 0.58 (4.39) | 1.56 ± 0.34 (1.64) |
| left/right | p | 0.875 | 25/25 | 0 | 25 | 1.63 ± 0.31 (1.60) | 4.76 ± 2.71 (5.03) | 2.02 ± 0.27 (2.14) | 4.49 ± 0.69 (4.79) | 1.75 ± 0.41 (1.82) |
| back/left | p | 0.854 | 25/25 | 0 | 25 | 2.31 ± 0.26 (2.24) | 3.75 ± 1.86 (3.47) | 2.06 ± 0.21 (2.14) | 4.59 ± 0.65 (4.87) | 1.81 ± 0.42 (1.97) |
| back/right | p | 0.834 | 25/25 | 0 | 25 | 2.31 ± 0.28 (2.26) | 5.14 ± 2.38 (5.33) | 2.00 ± 0.26 (2.09) | 4.43 ± 0.69 (4.84) | 1.70 ± 0.41 (1.76) |
| right/left | p | 0.856 | 25/25 | 0 | 25 | 1.65 ± 0.32 (1.58) | 4.21 ± 2.83 (3.99) | 1.95 ± 0.24 (2.04) | 4.28 ± 0.66 (4.58) | 1.61 ± 0.38 (1.67) |
| right/right | p | 0.840 | 25/25 | 0 | 25 | 1.45 ± 0.34 (1.48) | 5.34 ± 3.64 (4.38) | 1.87 ± 0.25 (1.92) | 4.09 ± 0.66 (4.39) | 1.50 ± 0.39 (1.48) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.872 | 4.6 | 4.69 | 1.83 |
| p | normal | 0.830 | 4.9 | 3.72 | 1.30 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.790 | 0.20 | 2.11 ± 0.65 (1.97) | 3.36 | 1.10 |
| p | medium | 16 | 0.905 | 0.85 | 1.05 ± 0.18 (1.04) | 3.42 | 1.15 |
| p | strong | 126 | 0.873 | 0.63 | - | 4.69 | 1.83 |

## Notes

- p: score 0.851, 200/200 kicked, 0 fell; worst sector back (0.844).

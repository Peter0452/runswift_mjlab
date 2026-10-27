# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-27-29_u4_overrun1_linear1600/model_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.856** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.92 ± 0.57 (1.89) |
| Direction error [°] | 5.63 ± 10.49 (4.02) |
| Avg ball speed [m/s] | 2.20 ± 0.47 (2.37) |
| Peak ball speed [m/s] | 4.96 ± 1.27 (5.63) |
| Distance [m] | 2.03 ± 0.76 (2.29) |
| Path length [m] | 2.04 ± 0.76 (2.31) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.869 | 50/50 | 0 | 50 | 1.31 ± 0.26 (1.30) | 4.49 ± 3.17 (3.31) | 2.09 ± 0.53 (2.31) | 4.70 ± 1.38 (5.32) | 1.86 ± 0.81 (2.11) |
| left | p | 0.883 | 50/50 | 0 | 49 | 1.87 ± 0.39 (1.91) | 5.05 ± 3.72 (3.89) | 2.29 ± 0.40 (2.42) | 5.20 ± 1.12 (5.73) | 2.18 ± 0.68 (2.39) |
| back | p | 0.809 | 50/50 | 0 | 49 | 2.62 ± 0.29 (2.62) | 8.48 ± 19.89 (5.69) | 2.23 ± 0.48 (2.44) | 5.03 ± 1.29 (5.67) | 2.11 ± 0.76 (2.41) |
| right | p | 0.864 | 50/50 | 0 | 50 | 1.89 ± 0.37 (1.81) | 4.49 ± 3.12 (3.87) | 2.18 ± 0.44 (2.35) | 4.89 ± 1.23 (5.54) | 1.97 ± 0.73 (2.19) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.854 | 100/100 | 0 | 99 | 1.94 ± 0.59 (1.90) | 5.26 ± 3.66 (4.01) | 2.20 ± 0.45 (2.38) | 4.97 ± 1.24 (5.64) | 2.04 ± 0.75 (2.30) |
| right | p | 0.858 | 100/100 | 0 | 99 | 1.91 ± 0.55 (1.81) | 6.00 ± 14.37 (4.03) | 2.19 ± 0.49 (2.37) | 4.94 ± 1.31 (5.62) | 2.02 ± 0.76 (2.24) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.878 | 25/25 | 0 | 25 | 1.32 ± 0.26 (1.30) | 4.47 ± 3.03 (3.11) | 2.12 ± 0.55 (2.31) | 4.76 ± 1.42 (5.27) | 1.91 ± 0.84 (2.25) |
| forward/right | p | 0.861 | 25/25 | 0 | 25 | 1.30 ± 0.27 (1.30) | 4.52 ± 3.31 (3.48) | 2.06 ± 0.50 (2.31) | 4.64 ± 1.32 (5.36) | 1.82 ± 0.77 (1.99) |
| left/left | p | 0.875 | 25/25 | 0 | 24 | 1.73 ± 0.38 (1.86) | 5.70 ± 4.53 (3.95) | 2.21 ± 0.40 (2.28) | 4.99 ± 1.14 (5.38) | 2.06 ± 0.70 (2.18) |
| left/right | p | 0.891 | 25/25 | 0 | 25 | 2.02 ± 0.34 (2.04) | 4.40 ± 2.51 (3.73) | 2.36 ± 0.39 (2.48) | 5.42 ± 1.06 (5.81) | 2.29 ± 0.63 (2.56) |
| back/left | p | 0.810 | 25/25 | 0 | 25 | 2.67 ± 0.31 (2.64) | 5.30 ± 3.25 (4.56) | 2.27 ± 0.35 (2.40) | 5.10 ± 1.07 (5.65) | 2.13 ± 0.68 (2.40) |
| back/right | p | 0.809 | 25/25 | 0 | 24 | 2.58 ± 0.25 (2.52) | 11.66 ± 27.57 (6.24) | 2.19 ± 0.57 (2.45) | 4.96 ± 1.48 (5.80) | 2.09 ± 0.83 (2.43) |
| right/left | p | 0.855 | 25/25 | 0 | 25 | 2.04 ± 0.33 (1.98) | 5.58 ± 3.51 (4.45) | 2.22 ± 0.45 (2.40) | 5.05 ± 1.26 (5.76) | 2.07 ± 0.75 (2.34) |
| right/right | p | 0.872 | 25/25 | 0 | 25 | 1.74 ± 0.34 (1.76) | 3.41 ± 2.20 (2.74) | 2.13 ± 0.42 (2.26) | 4.74 ± 1.18 (5.38) | 1.88 ± 0.70 (2.06) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.888 | 5.2 | 5.88 | 2.56 |
| p | normal | 0.825 | 6.1 | 4.03 | 1.50 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.776 | 0.20 | 2.09 ± 0.66 (1.99) | 3.31 | 1.08 |
| p | medium | 16 | 0.900 | 0.85 | 1.11 ± 0.16 (1.08) | 3.60 | 1.27 |
| p | strong | 126 | 0.888 | 0.78 | - | 5.89 | 2.57 |

## Notes

- p: score 0.856, 200/200 kicked, 0 fell; worst sector back (0.809).

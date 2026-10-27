# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_15-32-24_u13_u6_overrun05/model_19900.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.778** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 165 |
| Weak kicks (< 0.3 m) | 12 |
| Time to kick [s] | 1.95 ± 1.37 (1.74) |
| Direction error [°] | 19.32 ± 39.24 (5.50) |
| Avg ball speed [m/s] | 2.03 ± 0.64 (2.23) |
| Peak ball speed [m/s] | 4.48 ± 1.52 (5.16) |
| Distance [m] | 1.81 ± 0.80 (1.96) |
| Path length [m] | 1.81 ± 0.80 (1.96) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.781 | 49/50 | 0 | 41 | 1.70 ± 1.95 (1.34) | 8.61 ± 10.70 (5.31) | 1.99 ± 0.58 (2.13) | 4.34 ± 1.38 (4.22) | 1.70 ± 0.76 (1.71) |
| left | p | 0.803 | 48/50 | 0 | 43 | 1.71 ± 0.47 (1.77) | 15.29 ± 30.61 (5.50) | 2.15 ± 0.53 (2.28) | 4.79 ± 1.29 (5.37) | 1.95 ± 0.70 (2.10) |
| back | p | 0.743 | 50/50 | 0 | 41 | 2.57 ± 1.29 (2.50) | 32.67 ± 58.61 (5.87) | 2.01 ± 0.75 (2.27) | 4.42 ± 1.75 (5.28) | 1.84 ± 0.90 (2.12) |
| right | p | 0.785 | 49/50 | 0 | 40 | 1.81 ± 1.12 (1.74) | 20.36 ± 36.16 (5.14) | 1.97 ± 0.65 (2.18) | 4.38 ± 1.56 (5.12) | 1.73 ± 0.80 (1.90) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.810 | 100/100 | 0 | 86 | 1.84 ± 1.05 (1.74) | 17.87 ± 38.43 (4.91) | 2.07 ± 0.60 (2.25) | 4.57 ± 1.46 (5.15) | 1.86 ± 0.79 (1.99) |
| right | p | 0.746 | 96/100 | 0 | 79 | 2.07 ± 1.63 (1.75) | 20.84 ± 40.00 (5.95) | 1.99 ± 0.67 (2.20) | 4.39 ± 1.57 (5.18) | 1.75 ± 0.81 (1.89) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.820 | 25/25 | 0 | 21 | 1.34 ± 0.49 (1.30) | 7.95 ± 11.10 (3.83) | 2.00 ± 0.58 (2.23) | 4.35 ± 1.40 (4.30) | 1.70 ± 0.72 (1.72) |
| forward/right | p | 0.741 | 24/25 | 0 | 20 | 2.07 ± 2.69 (1.35) | 9.30 ± 10.22 (6.61) | 1.99 ± 0.57 (2.03) | 4.33 ± 1.35 (4.20) | 1.69 ± 0.79 (1.64) |
| left/left | p | 0.866 | 25/25 | 0 | 24 | 1.62 ± 0.38 (1.74) | 8.95 ± 16.65 (5.51) | 2.26 ± 0.43 (2.38) | 5.01 ± 1.12 (5.57) | 2.10 ± 0.64 (2.38) |
| left/right | p | 0.741 | 23/25 | 0 | 19 | 1.82 ± 0.53 (1.92) | 22.17 ± 39.54 (5.49) | 2.03 ± 0.60 (2.21) | 4.55 ± 1.42 (5.27) | 1.80 ± 0.73 (2.05) |
| back/left | p | 0.756 | 25/25 | 0 | 21 | 2.68 ± 1.66 (2.44) | 30.50 ± 58.53 (4.71) | 2.13 ± 0.63 (2.36) | 4.68 ± 1.50 (5.37) | 1.96 ± 0.84 (2.16) |
| back/right | p | 0.730 | 25/25 | 0 | 20 | 2.46 ± 0.75 (2.52) | 34.85 ± 58.61 (7.42) | 1.89 ± 0.85 (2.22) | 4.16 ± 1.95 (5.18) | 1.72 ± 0.93 (2.00) |
| right/left | p | 0.798 | 25/25 | 0 | 20 | 1.73 ± 0.48 (1.82) | 24.07 ± 41.31 (5.12) | 1.90 ± 0.68 (2.18) | 4.26 ± 1.67 (4.48) | 1.66 ± 0.83 (1.90) |
| right/right | p | 0.772 | 24/25 | 0 | 20 | 1.89 ± 1.51 (1.70) | 16.50 ± 29.36 (5.39) | 2.04 ± 0.61 (2.22) | 4.51 ± 1.43 (5.23) | 1.81 ± 0.77 (1.97) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.810 | 18.9 | 5.05 | 2.13 |
| p | normal | 0.746 | 19.7 | 3.92 | 1.48 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.707 | 0.17 | 2.22 ± 0.91 (2.14) | 3.52 | 1.25 |
| p | medium | 16 | 0.790 | 0.67 | 1.25 ± 0.28 (1.31) | 4.04 | 1.59 |
| p | strong | 126 | 0.809 | 0.66 | - | 4.98 | 2.09 |

## Notes

- p: score 0.778, 196/200 kicked, 0 fell; worst sector back (0.743).

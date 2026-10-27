# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_15-32-24_u13_u6_overrun05/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.773** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 162 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 2.14 ± 1.84 (1.76) |
| Direction error [°] | 19.85 ± 38.68 (5.50) |
| Avg ball speed [m/s] | 2.06 ± 0.70 (2.26) |
| Peak ball speed [m/s] | 4.51 ± 1.67 (4.95) |
| Distance [m] | 1.81 ± 0.88 (1.86) |
| Path length [m] | 1.82 ± 0.89 (1.87) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.786 | 50/50 | 0 | 42 | 1.89 ± 2.17 (1.35) | 9.31 ± 10.80 (5.85) | 1.96 ± 0.75 (2.08) | 4.24 ± 1.76 (4.22) | 1.66 ± 0.92 (1.61) |
| left | p | 0.802 | 49/50 | 0 | 42 | 1.90 ± 1.52 (1.76) | 19.25 ± 34.73 (6.26) | 2.16 ± 0.62 (2.34) | 4.81 ± 1.56 (5.39) | 1.95 ± 0.87 (2.04) |
| back | p | 0.723 | 48/50 | 0 | 38 | 2.60 ± 1.48 (2.54) | 30.56 ± 56.44 (6.01) | 2.13 ± 0.67 (2.36) | 4.66 ± 1.61 (5.29) | 1.91 ± 0.87 (2.03) |
| right | p | 0.780 | 50/50 | 0 | 40 | 2.17 ± 2.01 (1.77) | 20.67 ± 36.28 (3.68) | 2.00 ± 0.72 (2.21) | 4.35 ± 1.67 (4.44) | 1.71 ± 0.85 (1.81) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.798 | 98/100 | 0 | 87 | 1.84 ± 0.97 (1.72) | 16.66 ± 35.88 (4.96) | 2.15 ± 0.62 (2.31) | 4.70 ± 1.48 (5.11) | 1.90 ± 0.82 (2.01) |
| right | p | 0.747 | 99/100 | 0 | 75 | 2.43 ± 2.38 (1.78) | 22.99 ± 41.02 (6.05) | 1.97 ± 0.76 (2.22) | 4.32 ± 1.81 (4.53) | 1.71 ± 0.93 (1.81) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.819 | 25/25 | 0 | 24 | 1.61 ± 1.53 (1.34) | 7.09 ± 8.37 (5.39) | 2.14 ± 0.68 (2.26) | 4.62 ± 1.57 (4.69) | 1.87 ± 0.87 (1.89) |
| forward/right | p | 0.752 | 25/25 | 0 | 18 | 2.17 ± 2.62 (1.38) | 11.54 ± 12.39 (6.07) | 1.79 ± 0.78 (1.97) | 3.85 ± 1.84 (4.09) | 1.45 ± 0.92 (1.53) |
| left/left | p | 0.851 | 25/25 | 0 | 23 | 1.60 ± 0.42 (1.64) | 11.88 ± 21.64 (6.27) | 2.21 ± 0.53 (2.34) | 4.89 ± 1.31 (5.39) | 1.98 ± 0.74 (2.04) |
| left/right | p | 0.752 | 24/25 | 0 | 19 | 2.21 ± 2.08 (2.00) | 26.93 ± 43.11 (6.22) | 2.12 ± 0.70 (2.34) | 4.71 ± 1.78 (5.44) | 1.92 ± 0.98 (2.06) |
| back/left | p | 0.712 | 23/25 | 0 | 20 | 2.42 ± 0.72 (2.50) | 25.27 ± 52.32 (5.19) | 2.24 ± 0.49 (2.43) | 4.90 ± 1.21 (5.58) | 2.00 ± 0.73 (2.29) |
| back/right | p | 0.734 | 25/25 | 0 | 18 | 2.78 ± 1.91 (2.64) | 35.42 ± 59.58 (6.18) | 2.03 ± 0.79 (2.36) | 4.44 ± 1.88 (5.14) | 1.83 ± 0.97 (1.95) |
| right/left | p | 0.809 | 25/25 | 0 | 20 | 1.79 ± 0.49 (1.82) | 23.11 ± 42.03 (3.36) | 2.03 ± 0.72 (2.23) | 4.40 ± 1.70 (4.46) | 1.76 ± 0.91 (1.87) |
| right/right | p | 0.750 | 25/25 | 0 | 20 | 2.55 ± 2.74 (1.72) | 18.24 ± 29.21 (4.89) | 1.97 ± 0.71 (2.21) | 4.30 ± 1.64 (4.42) | 1.66 ± 0.78 (1.81) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.797 | 19.0 | 5.13 | 2.15 |
| p | normal | 0.748 | 20.7 | 3.91 | 1.47 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.711 | 0.19 | 2.26 ± 1.01 (2.12) | 3.55 | 1.27 |
| p | medium | 16 | 0.831 | 0.69 | 1.28 ± 0.20 (1.28) | 4.15 | 1.64 |
| p | strong | 126 | 0.794 | 0.67 | - | 5.01 | 2.08 |

## Notes

- p: score 0.773, 197/200 kicked, 0 fell; worst sector back (0.723).

# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_21-18-55_q2_speed_to_ball/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.782** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 171 |
| Weak kicks (< 0.3 m) | 9 |
| Time to kick [s] | 2.14 ± 1.92 (1.72) |
| Direction error [°] | 18.71 ± 37.53 (5.87) |
| Avg ball speed [m/s] | 2.09 ± 0.61 (2.24) |
| Peak ball speed [m/s] | 4.58 ± 1.46 (5.02) |
| Distance [m] | 1.81 ± 0.78 (1.93) |
| Path length [m] | 1.82 ± 0.78 (1.94) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.790 | 50/50 | 0 | 44 | 1.82 ± 2.06 (1.32) | 8.79 ± 10.27 (5.34) | 2.05 ± 0.60 (2.21) | 4.48 ± 1.42 (4.42) | 1.73 ± 0.79 (1.74) |
| left | p | 0.813 | 50/50 | 0 | 43 | 2.04 ± 1.99 (1.76) | 18.77 ± 35.25 (5.57) | 2.14 ± 0.56 (2.25) | 4.72 ± 1.38 (5.13) | 1.88 ± 0.77 (1.96) |
| back | p | 0.734 | 49/50 | 0 | 42 | 2.66 ± 1.55 (2.46) | 27.20 ± 51.01 (8.35) | 2.11 ± 0.62 (2.27) | 4.61 ± 1.47 (5.05) | 1.85 ± 0.76 (2.01) |
| right | p | 0.793 | 50/50 | 0 | 42 | 2.04 ± 1.93 (1.72) | 20.24 ± 39.19 (4.74) | 2.06 ± 0.64 (2.21) | 4.53 ± 1.54 (4.99) | 1.78 ± 0.79 (1.82) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.801 | 100/100 | 0 | 87 | 1.88 ± 1.20 (1.70) | 19.58 ± 40.60 (5.60) | 2.11 ± 0.59 (2.25) | 4.63 ± 1.42 (5.01) | 1.83 ± 0.76 (1.93) |
| right | p | 0.763 | 99/100 | 0 | 84 | 2.40 ± 2.42 (1.74) | 17.83 ± 34.11 (6.23) | 2.07 ± 0.62 (2.23) | 4.54 ± 1.49 (5.05) | 1.79 ± 0.79 (1.90) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.822 | 25/25 | 0 | 23 | 1.58 ± 1.62 (1.32) | 7.15 ± 8.77 (4.65) | 2.16 ± 0.46 (2.31) | 4.74 ± 1.17 (4.87) | 1.85 ± 0.65 (1.94) |
| forward/right | p | 0.757 | 25/25 | 0 | 21 | 2.06 ± 2.40 (1.34) | 10.44 ± 11.33 (7.17) | 1.94 ± 0.69 (1.95) | 4.21 ± 1.59 (4.09) | 1.62 ± 0.89 (1.52) |
| left/left | p | 0.846 | 25/25 | 0 | 23 | 1.58 ± 0.40 (1.68) | 12.09 ± 21.82 (6.02) | 2.18 ± 0.50 (2.20) | 4.78 ± 1.20 (5.04) | 1.91 ± 0.68 (1.93) |
| left/right | p | 0.780 | 25/25 | 0 | 20 | 2.51 ± 2.71 (1.92) | 25.45 ± 43.81 (4.36) | 2.09 ± 0.62 (2.29) | 4.65 ± 1.54 (5.20) | 1.84 ± 0.84 (1.96) |
| back/left | p | 0.744 | 25/25 | 0 | 21 | 2.63 ± 1.42 (2.48) | 30.77 ± 55.97 (8.35) | 2.14 ± 0.59 (2.27) | 4.67 ± 1.40 (5.02) | 1.90 ± 0.78 (2.01) |
| back/right | p | 0.725 | 24/25 | 0 | 21 | 2.70 ± 1.69 (2.42) | 23.47 ± 44.97 (8.34) | 2.08 ± 0.66 (2.27) | 4.54 ± 1.53 (5.13) | 1.80 ± 0.75 (1.98) |
| right/left | p | 0.794 | 25/25 | 0 | 20 | 1.73 ± 0.46 (1.82) | 28.29 ± 49.97 (4.04) | 1.96 ± 0.76 (2.24) | 4.31 ± 1.78 (4.64) | 1.67 ± 0.90 (1.71) |
| right/right | p | 0.791 | 25/25 | 0 | 22 | 2.35 ± 2.66 (1.70) | 12.18 ± 21.07 (5.36) | 2.15 ± 0.49 (2.18) | 4.76 ± 1.21 (5.08) | 1.89 ± 0.66 (1.93) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.814 | 17.2 | 5.18 | 2.12 |
| p | normal | 0.750 | 20.2 | 3.99 | 1.50 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.707 | 0.15 | 2.30 ± 0.90 (2.18) | 3.66 | 1.31 |
| p | medium | 16 | 0.828 | 0.68 | 1.28 ± 0.21 (1.28) | 4.17 | 1.66 |
| p | strong | 126 | 0.811 | 0.68 | - | 5.07 | 2.06 |

## Notes

- p: score 0.782, 199/200 kicked, 0 fell; worst sector back (0.734).

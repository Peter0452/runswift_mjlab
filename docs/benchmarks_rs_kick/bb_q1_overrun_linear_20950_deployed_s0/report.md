# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_18-10-03_q1_overrun_linear/model_20950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.784** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 170 |
| Weak kicks (< 0.3 m) | 10 |
| Time to kick [s] | 2.08 ± 1.76 (1.75) |
| Direction error [°] | 16.77 ± 33.21 (6.38) |
| Avg ball speed [m/s] | 1.98 ± 0.59 (2.15) |
| Peak ball speed [m/s] | 4.49 ± 1.46 (5.02) |
| Distance [m] | 1.69 ± 0.75 (1.83) |
| Path length [m] | 1.70 ± 0.75 (1.84) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.793 | 50/50 | 0 | 42 | 1.93 ± 2.44 (1.33) | 8.51 ± 11.42 (4.59) | 1.88 ± 0.65 (1.90) | 4.23 ± 1.60 (3.97) | 1.56 ± 0.84 (1.40) |
| left | p | 0.803 | 50/50 | 0 | 43 | 2.07 ± 1.87 (1.78) | 18.47 ± 32.38 (7.14) | 1.99 ± 0.58 (2.16) | 4.57 ± 1.45 (5.07) | 1.73 ± 0.70 (1.90) |
| back | p | 0.740 | 49/50 | 0 | 43 | 2.64 ± 1.45 (2.54) | 23.14 ± 46.69 (7.78) | 2.09 ± 0.48 (2.21) | 4.72 ± 1.20 (5.20) | 1.83 ± 0.62 (2.01) |
| right | p | 0.799 | 49/50 | 0 | 42 | 1.70 ± 0.47 (1.74) | 17.09 ± 31.00 (5.74) | 1.94 ± 0.61 (2.15) | 4.43 ± 1.52 (5.10) | 1.65 ± 0.78 (1.81) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.810 | 100/100 | 0 | 88 | 1.87 ± 1.17 (1.74) | 16.07 ± 34.27 (5.99) | 2.01 ± 0.56 (2.17) | 4.53 ± 1.39 (5.01) | 1.71 ± 0.73 (1.83) |
| right | p | 0.757 | 98/100 | 0 | 82 | 2.30 ± 2.18 (1.76) | 17.49 ± 32.08 (7.08) | 1.95 ± 0.62 (2.11) | 4.44 ± 1.53 (5.06) | 1.67 ± 0.77 (1.83) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.826 | 25/25 | 0 | 23 | 1.68 ± 2.06 (1.34) | 7.34 ± 12.44 (3.62) | 1.92 ± 0.65 (1.94) | 4.33 ± 1.61 (4.13) | 1.62 ± 0.83 (1.36) |
| forward/right | p | 0.760 | 25/25 | 0 | 19 | 2.17 ± 2.74 (1.32) | 9.68 ± 10.16 (5.44) | 1.85 ± 0.65 (1.82) | 4.13 ± 1.58 (3.93) | 1.51 ± 0.84 (1.43) |
| left/left | p | 0.850 | 25/25 | 0 | 23 | 1.63 ± 0.39 (1.72) | 9.90 ± 16.16 (6.99) | 2.08 ± 0.34 (2.13) | 4.74 ± 0.92 (5.01) | 1.78 ± 0.49 (1.88) |
| left/right | p | 0.757 | 25/25 | 0 | 20 | 2.51 ± 2.54 (1.90) | 27.04 ± 41.09 (8.92) | 1.90 ± 0.74 (2.26) | 4.40 ± 1.82 (5.38) | 1.67 ± 0.86 (2.03) |
| back/left | p | 0.757 | 25/25 | 0 | 21 | 2.38 ± 0.67 (2.44) | 26.73 ± 50.76 (7.87) | 2.13 ± 0.47 (2.28) | 4.74 ± 1.16 (5.26) | 1.87 ± 0.67 (2.05) |
| back/right | p | 0.723 | 24/25 | 0 | 22 | 2.90 ± 1.93 (2.61) | 19.41 ± 41.72 (7.77) | 2.06 ± 0.49 (2.13) | 4.69 ± 1.24 (5.11) | 1.79 ± 0.57 (1.91) |
| right/left | p | 0.809 | 25/25 | 0 | 21 | 1.79 ± 0.50 (1.80) | 20.30 ± 38.21 (5.16) | 1.89 ± 0.67 (2.17) | 4.31 ± 1.66 (5.10) | 1.59 ± 0.83 (1.72) |
| right/right | p | 0.789 | 24/25 | 0 | 21 | 1.59 ± 0.41 (1.67) | 13.74 ± 20.49 (7.29) | 1.99 ± 0.54 (2.15) | 4.55 ± 1.36 (5.19) | 1.70 ± 0.73 (1.91) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.822 | 12.2 | 5.25 | 2.07 |
| p | normal | 0.745 | 21.3 | 3.72 | 1.31 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.706 | 0.20 | 2.13 ± 0.92 (2.00) | 3.35 | 1.10 |
| p | medium | 16 | 0.794 | 0.72 | 1.12 ± 0.33 (1.24) | 3.62 | 1.28 |
| p | strong | 126 | 0.818 | 0.68 | - | 5.11 | 2.01 |

## Notes

- p: score 0.784, 198/200 kicked, 0 fell; worst sector back (0.740).

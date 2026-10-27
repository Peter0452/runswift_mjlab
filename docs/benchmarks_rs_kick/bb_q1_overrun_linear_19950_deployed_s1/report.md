# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_18-10-03_q1_overrun_linear/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.793** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 170 |
| Weak kicks (< 0.3 m) | 21 |
| Time to kick [s] | 1.87 ± 1.28 (1.62) |
| Direction error [°] | 16.21 ± 30.86 (7.28) |
| Avg ball speed [m/s] | 2.29 ± 0.77 (2.46) |
| Peak ball speed [m/s] | 4.86 ± 1.74 (5.62) |
| Distance [m] | 2.30 ± 1.07 (2.60) |
| Path length [m] | 2.31 ± 1.08 (2.62) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.830 | 50/50 | 0 | 44 | 1.41 ± 1.42 (1.26) | 7.86 ± 11.62 (3.36) | 2.22 ± 0.77 (2.40) | 4.78 ± 1.75 (5.46) | 2.21 ± 1.04 (2.31) |
| left | p | 0.807 | 50/50 | 0 | 42 | 1.82 ± 1.24 (1.62) | 14.30 ± 21.59 (7.88) | 2.32 ± 0.74 (2.51) | 4.88 ± 1.68 (5.66) | 2.32 ± 1.09 (2.81) |
| back | p | 0.744 | 50/50 | 0 | 42 | 2.56 ± 1.43 (2.45) | 30.33 ± 50.28 (10.10) | 2.28 ± 0.91 (2.64) | 4.84 ± 1.99 (5.91) | 2.36 ± 1.17 (2.93) |
| right | p | 0.790 | 49/50 | 0 | 42 | 1.68 ± 0.40 (1.72) | 12.26 ± 19.48 (6.64) | 2.33 ± 0.64 (2.43) | 4.94 ± 1.49 (5.47) | 2.31 ± 0.96 (2.42) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.796 | 99/100 | 0 | 87 | 1.81 ± 1.02 (1.56) | 14.74 ± 28.15 (6.07) | 2.29 ± 0.77 (2.50) | 4.89 ± 1.73 (5.66) | 2.32 ± 1.07 (2.72) |
| right | p | 0.789 | 100/100 | 0 | 83 | 1.93 ± 1.48 (1.66) | 17.67 ± 33.25 (8.11) | 2.28 ± 0.77 (2.39) | 4.83 ± 1.74 (5.47) | 2.28 ± 1.08 (2.48) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.845 | 25/25 | 0 | 23 | 1.20 ± 0.27 (1.24) | 6.29 ± 8.87 (3.31) | 2.18 ± 0.79 (2.43) | 4.69 ± 1.77 (5.44) | 2.14 ± 1.01 (2.29) |
| forward/right | p | 0.816 | 25/25 | 0 | 21 | 1.63 ± 1.97 (1.28) | 9.44 ± 13.67 (3.40) | 2.26 ± 0.75 (2.33) | 4.87 ± 1.72 (5.47) | 2.28 ± 1.06 (2.34) |
| left/left | p | 0.832 | 25/25 | 0 | 23 | 1.95 ± 1.67 (1.54) | 8.86 ± 9.62 (5.64) | 2.47 ± 0.66 (2.75) | 5.23 ± 1.53 (6.18) | 2.55 ± 1.02 (3.06) |
| left/right | p | 0.782 | 25/25 | 0 | 19 | 1.69 ± 0.50 (1.74) | 19.74 ± 27.94 (8.65) | 2.16 ± 0.78 (2.22) | 4.52 ± 1.76 (4.24) | 2.08 ± 1.12 (1.71) |
| back/left | p | 0.747 | 25/25 | 0 | 21 | 2.32 ± 0.68 (2.54) | 28.30 ± 44.68 (11.39) | 2.28 ± 0.84 (2.66) | 4.89 ± 1.89 (5.96) | 2.38 ± 1.16 (2.95) |
| back/right | p | 0.741 | 25/25 | 0 | 21 | 2.79 ± 1.87 (2.38) | 32.37 ± 55.25 (9.32) | 2.27 ± 0.96 (2.64) | 4.79 ± 2.08 (5.88) | 2.34 ± 1.18 (2.79) |
| right/left | p | 0.762 | 24/25 | 0 | 20 | 1.76 ± 0.44 (1.87) | 15.54 ± 26.63 (5.11) | 2.23 ± 0.73 (2.37) | 4.74 ± 1.66 (4.97) | 2.18 ± 1.01 (2.20) |
| right/right | p | 0.818 | 25/25 | 0 | 22 | 1.60 ± 0.35 (1.54) | 9.12 ± 6.52 (8.53) | 2.42 ± 0.52 (2.43) | 5.12 ± 1.27 (5.47) | 2.43 ± 0.91 (2.42) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.829 | 15.8 | 5.41 | 2.72 |
| p | normal | 0.757 | 16.6 | 4.30 | 1.87 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.702 | 0.09 | 2.52 ± 1.02 (2.31) | 3.87 | 1.55 |
| p | medium | 20 | 0.856 | 0.69 | 1.24 ± 0.26 (1.27) | 3.98 | 1.63 |
| p | strong | 126 | 0.822 | 0.72 | - | 5.41 | 2.72 |

## Notes

- p: score 0.793, 199/200 kicked, 0 fell; worst sector back (0.744).

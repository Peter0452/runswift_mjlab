# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_23-01-41_q3_speed_fastmix/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.806** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 174 |
| Weak kicks (< 0.3 m) | 22 |
| Time to kick [s] | 1.94 ± 1.38 (1.64) |
| Direction error [°] | 13.23 ± 26.75 (4.99) |
| Avg ball speed [m/s] | 2.39 ± 0.85 (2.56) |
| Peak ball speed [m/s] | 5.01 ± 1.87 (5.73) |
| Distance [m] | 2.46 ± 1.20 (2.79) |
| Path length [m] | 2.47 ± 1.20 (2.81) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.820 | 50/50 | 0 | 43 | 1.60 ± 1.86 (1.29) | 7.90 ± 10.94 (3.77) | 2.27 ± 0.91 (2.42) | 4.79 ± 1.98 (5.11) | 2.29 ± 1.20 (2.38) |
| left | p | 0.844 | 50/50 | 0 | 45 | 1.84 ± 1.15 (1.62) | 10.30 ± 22.15 (4.23) | 2.40 ± 0.71 (2.54) | 5.09 ± 1.65 (5.70) | 2.47 ± 1.10 (2.68) |
| back | p | 0.740 | 49/50 | 0 | 41 | 2.48 ± 1.06 (2.50) | 24.49 ± 42.38 (8.38) | 2.41 ± 1.04 (2.77) | 5.03 ± 2.23 (6.16) | 2.58 ± 1.40 (3.27) |
| right | p | 0.819 | 50/50 | 0 | 45 | 1.86 ± 1.14 (1.75) | 10.44 ± 17.58 (5.20) | 2.47 ± 0.66 (2.54) | 5.14 ± 1.52 (5.78) | 2.50 ± 1.05 (2.80) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.813 | 100/100 | 0 | 87 | 1.98 ± 1.52 (1.62) | 14.42 ± 30.61 (4.38) | 2.42 ± 0.84 (2.73) | 5.09 ± 1.84 (5.98) | 2.51 ± 1.18 (3.00) |
| right | p | 0.799 | 99/100 | 0 | 87 | 1.90 ± 1.23 (1.68) | 12.03 ± 22.12 (5.97) | 2.35 ± 0.85 (2.51) | 4.94 ± 1.89 (5.63) | 2.41 ± 1.21 (2.58) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.838 | 25/25 | 0 | 23 | 1.62 ± 1.94 (1.26) | 6.04 ± 7.37 (3.69) | 2.40 ± 0.84 (2.75) | 5.06 ± 1.80 (6.17) | 2.44 ± 1.14 (3.00) |
| forward/right | p | 0.801 | 25/25 | 0 | 20 | 1.59 ± 1.79 (1.30) | 9.77 ± 13.34 (4.51) | 2.14 ± 0.96 (2.31) | 4.52 ± 2.11 (4.60) | 2.13 ± 1.23 (2.08) |
| left/left | p | 0.857 | 25/25 | 0 | 23 | 1.97 ± 1.54 (1.62) | 5.61 ± 6.99 (3.85) | 2.50 ± 0.71 (2.77) | 5.30 ± 1.64 (6.14) | 2.64 ± 1.05 (3.18) |
| left/right | p | 0.830 | 25/25 | 0 | 22 | 1.72 ± 0.50 (1.76) | 14.99 ± 29.80 (4.99) | 2.31 ± 0.70 (2.36) | 4.88 ± 1.63 (4.56) | 2.30 ± 1.12 (2.03) |
| back/left | p | 0.753 | 25/25 | 0 | 20 | 2.24 ± 0.73 (2.38) | 33.03 ± 50.89 (9.36) | 2.41 ± 1.02 (2.93) | 5.01 ± 2.18 (6.40) | 2.55 ± 1.41 (3.31) |
| back/right | p | 0.728 | 24/25 | 0 | 21 | 2.73 ± 1.28 (2.57) | 15.60 ± 28.53 (7.56) | 2.40 ± 1.05 (2.72) | 5.05 ± 2.28 (6.05) | 2.61 ± 1.38 (3.20) |
| right/left | p | 0.803 | 25/25 | 0 | 21 | 2.11 ± 1.53 (1.90) | 12.99 ± 23.63 (4.03) | 2.37 ± 0.74 (2.49) | 4.98 ± 1.67 (5.73) | 2.39 ± 1.08 (2.72) |
| right/right | p | 0.836 | 25/25 | 0 | 24 | 1.61 ± 0.34 (1.54) | 7.89 ± 6.84 (6.91) | 2.57 ± 0.55 (2.80) | 5.30 ± 1.35 (6.26) | 2.61 ± 1.00 (3.09) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.838 | 13.9 | 5.71 | 2.97 |
| p | normal | 0.773 | 12.6 | 4.32 | 1.95 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.731 | 0.10 | 2.56 ± 1.06 (2.45) | 3.93 | 1.61 |
| p | medium | 20 | 0.845 | 0.57 | 1.15 ± 0.47 (1.29) | 3.69 | 1.53 |
| p | strong | 126 | 0.832 | 0.76 | - | 5.69 | 2.97 |

## Notes

- p: score 0.806, 199/200 kicked, 0 fell; worst sector back (0.740).

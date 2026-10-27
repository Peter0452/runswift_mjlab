# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_15-01-05_u12_u6_seed23/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.778** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 159 |
| Weak kicks (< 0.3 m) | 17 |
| Time to kick [s] | 2.06 ± 1.79 (1.71) |
| Direction error [°] | 20.39 ± 37.15 (6.71) |
| Avg ball speed [m/s] | 2.31 ± 0.88 (2.53) |
| Peak ball speed [m/s] | 4.80 ± 1.89 (5.59) |
| Distance [m] | 2.35 ± 1.21 (2.60) |
| Path length [m] | 2.36 ± 1.22 (2.61) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.779 | 49/50 | 0 | 41 | 1.68 ± 1.97 (1.30) | 10.59 ± 16.26 (5.04) | 2.14 ± 0.81 (2.19) | 4.45 ± 1.75 (4.30) | 2.05 ± 1.09 (1.86) |
| left | p | 0.809 | 50/50 | 0 | 41 | 1.99 ± 1.81 (1.73) | 18.89 ± 32.16 (8.14) | 2.44 ± 0.80 (2.76) | 5.08 ± 1.73 (5.90) | 2.52 ± 1.13 (3.04) |
| back | p | 0.740 | 49/50 | 0 | 37 | 2.47 ± 1.33 (2.44) | 32.26 ± 54.92 (7.66) | 2.36 ± 1.03 (2.87) | 4.86 ± 2.18 (6.13) | 2.49 ± 1.38 (3.31) |
| right | p | 0.784 | 50/50 | 0 | 40 | 2.09 ± 1.87 (1.72) | 19.85 ± 31.34 (7.08) | 2.31 ± 0.84 (2.55) | 4.78 ± 1.80 (5.51) | 2.32 ± 1.16 (2.60) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.798 | 99/100 | 0 | 85 | 1.76 ± 0.78 (1.68) | 18.87 ± 36.06 (7.27) | 2.39 ± 0.81 (2.56) | 4.96 ± 1.76 (5.75) | 2.44 ± 1.16 (2.80) |
| right | p | 0.758 | 99/100 | 0 | 74 | 2.35 ± 2.37 (1.72) | 21.90 ± 38.16 (6.24) | 2.23 ± 0.94 (2.33) | 4.63 ± 1.99 (5.20) | 2.25 ± 1.25 (2.35) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.832 | 25/25 | 0 | 23 | 1.32 ± 0.41 (1.28) | 8.24 ± 13.26 (4.50) | 2.28 ± 0.76 (2.37) | 4.74 ± 1.65 (4.38) | 2.23 ± 1.08 (1.96) |
| forward/right | p | 0.726 | 24/25 | 0 | 18 | 2.04 ± 2.73 (1.30) | 13.03 ± 18.57 (5.51) | 2.00 ± 0.83 (2.12) | 4.16 ± 1.80 (4.20) | 1.87 ± 1.07 (1.80) |
| left/left | p | 0.845 | 25/25 | 0 | 22 | 1.54 ± 0.40 (1.60) | 13.68 ± 22.15 (6.98) | 2.51 ± 0.61 (2.82) | 5.26 ± 1.38 (6.10) | 2.62 ± 0.96 (3.11) |
| left/right | p | 0.773 | 25/25 | 0 | 19 | 2.44 ± 2.45 (1.90) | 24.10 ± 39.04 (8.44) | 2.36 ± 0.95 (2.72) | 4.90 ± 2.00 (5.83) | 2.43 ± 1.27 (3.02) |
| back/left | p | 0.723 | 24/25 | 0 | 19 | 2.30 ± 0.67 (2.45) | 34.41 ± 56.60 (11.64) | 2.41 ± 0.98 (2.94) | 4.97 ± 2.09 (6.22) | 2.55 ± 1.38 (3.39) |
| back/right | p | 0.756 | 25/25 | 0 | 18 | 2.64 ± 1.72 (2.40) | 30.20 ± 53.17 (6.63) | 2.31 ± 1.07 (2.81) | 4.75 ± 2.26 (5.98) | 2.44 ± 1.38 (3.10) |
| right/left | p | 0.790 | 25/25 | 0 | 21 | 1.91 ± 1.06 (1.76) | 19.77 ± 32.17 (8.20) | 2.37 ± 0.85 (2.56) | 4.88 ± 1.81 (5.48) | 2.39 ± 1.15 (2.56) |
| right/right | p | 0.777 | 25/25 | 0 | 19 | 2.28 ± 2.42 (1.64) | 19.92 ± 30.50 (5.56) | 2.25 ± 0.83 (2.53) | 4.68 ± 1.78 (5.54) | 2.24 ± 1.17 (2.63) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.802 | 18.3 | 5.61 | 2.93 |
| p | normal | 0.754 | 22.4 | 3.99 | 1.77 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.718 | 0.18 | 2.23 ± 1.11 (2.31) | 3.47 | 1.39 |
| p | medium | 16 | 0.795 | 0.67 | 1.15 ± 0.37 (1.25) | 3.71 | 1.53 |
| p | strong | 126 | 0.803 | 0.74 | - | 5.55 | 2.90 |

## Notes

- p: score 0.778, 198/200 kicked, 0 fell; worst sector back (0.740).

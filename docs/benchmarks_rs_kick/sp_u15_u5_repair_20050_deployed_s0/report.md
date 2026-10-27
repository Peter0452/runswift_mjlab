# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-26-24_u15_u5_repair/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.783** |
| Kicked / fell | 194 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.84 ± 1.14 (1.72) |
| Direction error [°] | 17.18 ± 35.87 (4.71) |
| Avg ball speed [m/s] | 2.10 ± 0.59 (2.28) |
| Peak ball speed [m/s] | 4.56 ± 1.40 (4.99) |
| Distance [m] | 1.87 ± 0.76 (1.96) |
| Path length [m] | 1.88 ± 0.76 (1.97) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.782 | 48/50 | 0 | 42 | 1.45 ± 1.37 (1.30) | 8.15 ± 11.64 (4.03) | 2.09 ± 0.58 (2.17) | 4.47 ± 1.39 (4.30) | 1.82 ± 0.77 (1.78) |
| left | p | 0.806 | 48/50 | 0 | 43 | 1.68 ± 0.44 (1.78) | 15.12 ± 30.48 (5.26) | 2.16 ± 0.51 (2.29) | 4.79 ± 1.23 (5.17) | 1.97 ± 0.69 (2.09) |
| back | p | 0.751 | 49/50 | 0 | 41 | 2.37 ± 0.73 (2.44) | 27.59 ± 52.00 (5.41) | 2.10 ± 0.69 (2.36) | 4.53 ± 1.56 (4.99) | 1.91 ± 0.82 (2.02) |
| right | p | 0.791 | 49/50 | 0 | 41 | 1.86 ± 1.47 (1.72) | 17.64 ± 33.96 (3.63) | 2.05 ± 0.57 (2.23) | 4.46 ± 1.37 (4.76) | 1.80 ± 0.74 (1.93) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.812 | 99/100 | 0 | 89 | 1.83 ± 1.09 (1.72) | 15.53 ± 35.24 (4.71) | 2.15 ± 0.52 (2.27) | 4.67 ± 1.23 (5.10) | 1.92 ± 0.70 (1.99) |
| right | p | 0.753 | 95/100 | 0 | 78 | 1.85 ± 1.20 (1.72) | 18.90 ± 36.43 (5.14) | 2.05 ± 0.66 (2.28) | 4.44 ± 1.55 (4.76) | 1.82 ± 0.82 (1.96) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.831 | 25/25 | 0 | 24 | 1.65 ± 1.86 (1.30) | 6.55 ± 10.50 (4.14) | 2.21 ± 0.47 (2.25) | 4.75 ± 1.16 (5.14) | 1.97 ± 0.66 (2.00) |
| forward/right | p | 0.733 | 23/25 | 0 | 18 | 1.24 ± 0.26 (1.28) | 9.88 ± 12.54 (3.93) | 1.96 ± 0.65 (2.11) | 4.16 ± 1.54 (4.21) | 1.65 ± 0.84 (1.78) |
| left/left | p | 0.863 | 25/25 | 0 | 24 | 1.62 ± 0.39 (1.72) | 8.48 ± 15.44 (4.71) | 2.19 ± 0.37 (2.28) | 4.86 ± 0.95 (5.16) | 1.99 ± 0.54 (2.13) |
| left/right | p | 0.749 | 23/25 | 0 | 19 | 1.75 ± 0.48 (1.84) | 22.33 ± 39.75 (5.51) | 2.13 ± 0.62 (2.32) | 4.72 ± 1.47 (5.25) | 1.95 ± 0.82 (1.97) |
| back/left | p | 0.756 | 24/25 | 0 | 21 | 2.36 ± 0.69 (2.45) | 23.75 ± 51.64 (4.95) | 2.22 ± 0.49 (2.38) | 4.77 ± 1.13 (4.91) | 2.00 ± 0.71 (1.99) |
| back/right | p | 0.746 | 25/25 | 0 | 20 | 2.37 ± 0.77 (2.42) | 31.28 ± 52.08 (6.77) | 1.99 ± 0.83 (2.34) | 4.29 ± 1.86 (5.14) | 1.82 ± 0.90 (2.05) |
| right/left | p | 0.800 | 25/25 | 0 | 20 | 1.73 ± 0.49 (1.80) | 23.68 ± 41.81 (3.66) | 1.98 ± 0.65 (2.23) | 4.32 ± 1.53 (4.50) | 1.72 ± 0.81 (1.93) |
| right/right | p | 0.783 | 24/25 | 0 | 21 | 1.99 ± 2.03 (1.68) | 11.35 ± 21.36 (3.38) | 2.12 ± 0.47 (2.26) | 4.60 ± 1.17 (4.83) | 1.87 ± 0.66 (1.97) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.804 | 14.4 | 5.12 | 2.16 |
| p | normal | 0.761 | 19.8 | 4.02 | 1.60 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.729 | 0.16 | 2.37 ± 1.05 (2.31) | 3.69 | 1.42 |
| p | medium | 16 | 0.801 | 0.68 | 1.29 ± 0.21 (1.32) | 4.18 | 1.69 |
| p | strong | 126 | 0.805 | 0.67 | - | 5.03 | 2.11 |

## Notes

- p: score 0.783, 194/200 kicked, 0 fell; worst sector back (0.751).

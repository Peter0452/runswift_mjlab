# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_15-01-05_u12_u6_seed23/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.784** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 161 |
| Weak kicks (< 0.3 m) | 10 |
| Time to kick [s] | 1.91 ± 1.45 (1.70) |
| Direction error [°] | 18.74 ± 37.40 (4.95) |
| Avg ball speed [m/s] | 2.12 ± 0.67 (2.29) |
| Peak ball speed [m/s] | 4.58 ± 1.57 (5.19) |
| Distance [m] | 1.92 ± 0.88 (1.96) |
| Path length [m] | 1.93 ± 0.88 (1.98) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.812 | 50/50 | 0 | 42 | 1.66 ± 1.92 (1.32) | 8.19 ± 11.20 (3.96) | 1.99 ± 0.71 (2.19) | 4.28 ± 1.68 (4.26) | 1.72 ± 0.88 (1.75) |
| left | p | 0.783 | 48/50 | 0 | 38 | 1.61 ± 0.48 (1.66) | 20.63 ± 35.19 (5.88) | 2.15 ± 0.66 (2.40) | 4.65 ± 1.56 (5.34) | 1.96 ± 0.86 (2.28) |
| back | p | 0.748 | 49/50 | 0 | 39 | 2.48 ± 1.46 (2.44) | 29.22 ± 53.78 (6.38) | 2.22 ± 0.66 (2.35) | 4.75 ± 1.52 (5.21) | 2.07 ± 0.93 (2.26) |
| right | p | 0.791 | 49/50 | 0 | 42 | 1.90 ± 1.37 (1.76) | 17.20 ± 33.64 (4.71) | 2.14 ± 0.62 (2.27) | 4.63 ± 1.46 (5.16) | 1.93 ± 0.80 (2.02) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.809 | 99/100 | 0 | 85 | 1.74 ± 0.62 (1.68) | 16.71 ± 35.80 (4.27) | 2.18 ± 0.63 (2.33) | 4.70 ± 1.49 (5.21) | 1.98 ± 0.83 (2.06) |
| right | p | 0.759 | 97/100 | 0 | 76 | 2.09 ± 1.95 (1.70) | 20.82 ± 38.85 (5.50) | 2.07 ± 0.71 (2.27) | 4.45 ± 1.63 (4.99) | 1.85 ± 0.92 (1.91) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.839 | 25/25 | 0 | 22 | 1.28 ± 0.30 (1.30) | 7.16 ± 11.35 (2.41) | 2.14 ± 0.63 (2.29) | 4.60 ± 1.53 (4.34) | 1.90 ± 0.80 (1.84) |
| forward/right | p | 0.785 | 25/25 | 0 | 20 | 2.03 ± 2.64 (1.34) | 9.21 ± 10.95 (4.34) | 1.84 ± 0.76 (2.01) | 3.97 ± 1.77 (4.09) | 1.55 ± 0.93 (1.68) |
| left/left | p | 0.836 | 25/25 | 0 | 21 | 1.52 ± 0.40 (1.62) | 13.79 ± 22.92 (5.49) | 2.19 ± 0.64 (2.46) | 4.76 ± 1.52 (5.46) | 2.03 ± 0.82 (2.31) |
| left/right | p | 0.730 | 23/25 | 0 | 17 | 1.71 ± 0.53 (1.84) | 28.06 ± 43.68 (6.33) | 2.11 ± 0.68 (2.30) | 4.54 ± 1.60 (5.25) | 1.89 ± 0.90 (1.97) |
| back/left | p | 0.752 | 24/25 | 0 | 21 | 2.34 ± 0.66 (2.41) | 24.77 ± 50.84 (6.30) | 2.31 ± 0.52 (2.36) | 4.96 ± 1.25 (5.31) | 2.16 ± 0.84 (2.33) |
| back/right | p | 0.744 | 25/25 | 0 | 18 | 2.61 ± 1.93 (2.44) | 33.48 ± 56.12 (6.66) | 2.14 ± 0.77 (2.33) | 4.55 ± 1.72 (4.99) | 1.98 ± 1.01 (1.90) |
| right/left | p | 0.807 | 25/25 | 0 | 21 | 1.85 ± 0.50 (1.84) | 21.43 ± 41.88 (3.75) | 2.08 ± 0.68 (2.24) | 4.50 ± 1.61 (4.94) | 1.86 ± 0.82 (1.98) |
| right/right | p | 0.776 | 24/25 | 0 | 21 | 1.96 ± 1.89 (1.64) | 12.79 ± 21.11 (6.70) | 2.20 ± 0.53 (2.32) | 4.76 ± 1.28 (5.40) | 2.00 ± 0.76 (2.03) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.807 | 17.1 | 5.19 | 2.25 |
| p | normal | 0.760 | 20.3 | 3.97 | 1.60 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.733 | 0.18 | 2.29 ± 1.05 (2.23) | 3.60 | 1.37 |
| p | medium | 16 | 0.801 | 0.68 | 1.27 ± 0.23 (1.29) | 4.09 | 1.66 |
| p | strong | 126 | 0.805 | 0.68 | - | 5.10 | 2.21 |

## Notes

- p: score 0.784, 196/200 kicked, 0 fell; worst sector back (0.748).

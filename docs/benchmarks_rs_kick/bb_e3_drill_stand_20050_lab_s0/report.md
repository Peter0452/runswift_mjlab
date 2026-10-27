# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_01-18-00_e3_drill_stand/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.838** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.57 ± 0.52 (1.50) |
| Direction error [°] | 7.22 ± 11.60 (6.57) |
| Avg ball speed [m/s] | 2.15 ± 0.43 (2.17) |
| Peak ball speed [m/s] | 4.54 ± 0.97 (4.63) |
| Distance [m] | 1.98 ± 0.64 (2.01) |
| Path length [m] | 1.98 ± 0.64 (2.03) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.833 | 50/50 | 0 | 50 | 1.03 ± 0.23 (1.04) | 5.88 ± 3.63 (5.36) | 1.93 ± 0.34 (1.84) | 4.07 ± 0.75 (3.83) | 1.61 ± 0.50 (1.43) |
| left | p | 0.858 | 50/50 | 0 | 50 | 1.52 ± 0.34 (1.51) | 6.37 ± 4.18 (6.28) | 2.22 ± 0.36 (2.31) | 4.71 ± 0.80 (4.95) | 2.08 ± 0.54 (2.25) |
| back | p | 0.833 | 50/50 | 0 | 48 | 2.23 ± 0.25 (2.23) | 9.37 ± 21.87 (6.73) | 2.25 ± 0.53 (2.46) | 4.76 ± 1.19 (5.23) | 2.18 ± 0.72 (2.43) |
| right | p | 0.827 | 50/50 | 0 | 47 | 1.51 ± 0.35 (1.47) | 7.26 ± 4.69 (6.90) | 2.21 ± 0.40 (2.25) | 4.62 ± 0.89 (4.82) | 2.02 ± 0.62 (2.10) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.841 | 100/100 | 0 | 98 | 1.58 ± 0.53 (1.52) | 6.38 ± 4.34 (6.09) | 2.18 ± 0.44 (2.24) | 4.60 ± 0.98 (4.90) | 2.02 ± 0.65 (2.07) |
| right | p | 0.835 | 100/100 | 0 | 97 | 1.56 ± 0.51 (1.49) | 8.07 ± 15.77 (6.89) | 2.13 ± 0.43 (2.16) | 4.47 ± 0.95 (4.57) | 1.93 ± 0.62 (1.95) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.828 | 25/25 | 0 | 25 | 1.03 ± 0.23 (1.04) | 6.51 ± 3.67 (7.42) | 1.95 ± 0.31 (1.85) | 4.11 ± 0.70 (3.99) | 1.64 ± 0.48 (1.50) |
| forward/right | p | 0.838 | 25/25 | 0 | 25 | 1.02 ± 0.23 (1.04) | 5.25 ± 3.49 (5.14) | 1.91 ± 0.37 (1.76) | 4.02 ± 0.80 (3.66) | 1.59 ± 0.52 (1.41) |
| left/left | p | 0.853 | 25/25 | 0 | 25 | 1.42 ± 0.35 (1.48) | 6.52 ± 4.38 (6.69) | 2.18 ± 0.36 (2.29) | 4.63 ± 0.83 (4.89) | 2.02 ± 0.56 (2.23) |
| left/right | p | 0.864 | 25/25 | 0 | 25 | 1.63 ± 0.30 (1.58) | 6.23 ± 3.95 (5.86) | 2.26 ± 0.35 (2.31) | 4.79 ± 0.77 (5.03) | 2.15 ± 0.52 (2.29) |
| back/left | p | 0.835 | 25/25 | 0 | 24 | 2.27 ± 0.25 (2.24) | 6.48 ± 4.64 (6.45) | 2.26 ± 0.53 (2.45) | 4.80 ± 1.21 (5.27) | 2.21 ± 0.74 (2.56) |
| back/right | p | 0.831 | 25/25 | 0 | 24 | 2.20 ± 0.25 (2.18) | 12.26 ± 30.30 (6.97) | 2.23 ± 0.53 (2.46) | 4.72 ± 1.17 (5.16) | 2.15 ± 0.70 (2.26) |
| right/left | p | 0.849 | 25/25 | 0 | 24 | 1.62 ± 0.31 (1.56) | 6.00 ± 4.58 (4.21) | 2.33 ± 0.41 (2.48) | 4.87 ± 0.92 (5.29) | 2.21 ± 0.64 (2.54) |
| right/right | p | 0.805 | 25/25 | 0 | 23 | 1.41 ± 0.35 (1.46) | 8.53 ± 4.44 (7.87) | 2.10 ± 0.36 (2.04) | 4.37 ± 0.79 (3.93) | 1.84 ± 0.54 (1.56) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.872 | 6.0 | 5.10 | 2.34 |
| p | normal | 0.804 | 8.5 | 3.98 | 1.61 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.748 | 0.13 | 2.23 ± 0.76 (2.08) | 3.52 | 1.30 |
| p | medium | 16 | 0.880 | 0.84 | 1.11 ± 0.16 (1.11) | 3.60 | 1.34 |
| p | strong | 126 | 0.874 | 0.68 | - | 5.13 | 2.37 |

## Notes

- p: score 0.838, 200/200 kicked, 0 fell; worst sector right (0.827).

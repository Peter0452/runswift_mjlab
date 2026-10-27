# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_10-50-14_u6_u4_anchor02/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.859** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.57 ± 0.51 (1.50) |
| Direction error [°] | 4.94 ± 2.85 (4.53) |
| Avg ball speed [m/s] | 1.85 ± 0.38 (1.99) |
| Peak ball speed [m/s] | 4.11 ± 0.93 (4.42) |
| Distance [m] | 1.45 ± 0.52 (1.57) |
| Path length [m] | 1.46 ± 0.52 (1.58) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.864 | 50/50 | 0 | 50 | 1.04 ± 0.22 (1.06) | 4.22 ± 2.86 (2.77) | 1.62 ± 0.44 (1.60) | 3.54 ± 0.97 (3.41) | 1.13 ± 0.52 (0.97) |
| left | p | 0.871 | 50/50 | 0 | 50 | 1.51 ± 0.33 (1.54) | 5.02 ± 2.71 (4.64) | 1.95 ± 0.30 (2.03) | 4.36 ± 0.77 (4.62) | 1.59 ± 0.46 (1.62) |
| back | p | 0.853 | 50/50 | 0 | 50 | 2.21 ± 0.25 (2.18) | 4.94 ± 2.24 (4.46) | 2.00 ± 0.28 (2.13) | 4.47 ± 0.78 (4.87) | 1.66 ± 0.46 (1.83) |
| right | p | 0.848 | 50/50 | 0 | 50 | 1.51 ± 0.34 (1.48) | 5.59 ± 3.31 (5.72) | 1.84 ± 0.34 (1.95) | 4.06 ± 0.87 (4.21) | 1.42 ± 0.46 (1.53) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.855 | 100/100 | 0 | 100 | 1.57 ± 0.51 (1.54) | 5.25 ± 2.81 (5.09) | 1.89 ± 0.34 (2.00) | 4.18 ± 0.85 (4.54) | 1.49 ± 0.48 (1.61) |
| right | p | 0.864 | 100/100 | 0 | 100 | 1.56 ± 0.51 (1.48) | 4.63 ± 2.85 (4.17) | 1.82 ± 0.41 (1.94) | 4.04 ± 0.99 (4.34) | 1.41 ± 0.55 (1.51) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.854 | 25/25 | 0 | 25 | 1.05 ± 0.21 (1.08) | 4.93 ± 2.93 (3.71) | 1.73 ± 0.37 (1.84) | 3.75 ± 0.83 (3.77) | 1.24 ± 0.47 (1.41) |
| forward/right | p | 0.875 | 25/25 | 0 | 25 | 1.03 ± 0.23 (1.06) | 3.51 ± 2.60 (2.64) | 1.51 ± 0.48 (1.43) | 3.33 ± 1.05 (2.99) | 1.02 ± 0.55 (0.91) |
| left/left | p | 0.859 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.50) | 5.76 ± 3.17 (5.96) | 1.88 ± 0.28 (2.00) | 4.18 ± 0.73 (4.42) | 1.48 ± 0.42 (1.56) |
| left/right | p | 0.883 | 25/25 | 0 | 25 | 1.60 ± 0.31 (1.60) | 4.29 ± 1.89 (4.16) | 2.02 ± 0.30 (2.09) | 4.54 ± 0.77 (4.80) | 1.70 ± 0.47 (1.71) |
| back/left | p | 0.850 | 25/25 | 0 | 25 | 2.22 ± 0.25 (2.16) | 5.10 ± 2.33 (4.75) | 2.02 ± 0.26 (2.13) | 4.51 ± 0.73 (4.88) | 1.69 ± 0.45 (1.86) |
| back/right | p | 0.857 | 25/25 | 0 | 25 | 2.20 ± 0.25 (2.20) | 4.78 ± 2.14 (4.18) | 1.98 ± 0.31 (2.13) | 4.43 ± 0.82 (4.86) | 1.63 ± 0.47 (1.69) |
| right/left | p | 0.856 | 25/25 | 0 | 25 | 1.60 ± 0.32 (1.58) | 5.22 ± 2.69 (4.71) | 1.92 ± 0.35 (2.04) | 4.28 ± 0.91 (4.77) | 1.54 ± 0.48 (1.70) |
| right/right | p | 0.839 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.42) | 5.96 ± 3.79 (6.07) | 1.75 ± 0.31 (1.77) | 3.85 ± 0.77 (3.76) | 1.30 ± 0.41 (1.24) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.869 | 5.1 | 4.67 | 1.75 |
| p | normal | 0.849 | 4.8 | 3.54 | 1.16 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.815 | 0.32 | 1.91 ± 0.66 (1.74) | 3.05 | 0.89 |
| p | medium | 16 | 0.928 | 0.88 | 1.01 ± 0.16 (1.01) | 3.27 | 1.01 |
| p | strong | 126 | 0.871 | 0.63 | - | 4.70 | 1.76 |

## Notes

- p: score 0.859, 200/200 kicked, 0 fell; worst sector right (0.848).

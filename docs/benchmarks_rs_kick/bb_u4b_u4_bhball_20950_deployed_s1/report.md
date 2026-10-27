# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_04-46-54_u4b_u4_bhball/model_20950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.844** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 192 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.83 ± 0.57 (1.71) |
| Direction error [°] | 6.38 ± 4.03 (5.87) |
| Avg ball speed [m/s] | 2.41 ± 0.43 (2.50) |
| Peak ball speed [m/s] | 5.17 ± 1.09 (5.67) |
| Distance [m] | 2.33 ± 0.78 (2.55) |
| Path length [m] | 2.34 ± 0.79 (2.56) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.875 | 50/50 | 0 | 50 | 1.28 ± 0.25 (1.30) | 4.51 ± 2.68 (4.57) | 2.32 ± 0.42 (2.44) | 5.01 ± 1.08 (5.52) | 2.16 ± 0.73 (2.24) |
| left | p | 0.855 | 50/50 | 0 | 48 | 1.73 ± 0.36 (1.65) | 6.90 ± 3.85 (6.96) | 2.41 ± 0.43 (2.48) | 5.17 ± 1.09 (5.52) | 2.33 ± 0.79 (2.55) |
| back | p | 0.797 | 50/50 | 0 | 45 | 2.56 ± 0.35 (2.49) | 8.65 ± 4.34 (8.16) | 2.58 ± 0.43 (2.69) | 5.48 ± 1.08 (5.99) | 2.60 ± 0.80 (2.94) |
| right | p | 0.850 | 50/50 | 0 | 49 | 1.76 ± 0.37 (1.76) | 5.45 ± 3.78 (4.32) | 2.35 ± 0.41 (2.48) | 5.03 ± 1.05 (5.59) | 2.22 ± 0.74 (2.41) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.846 | 100/100 | 0 | 98 | 1.83 ± 0.56 (1.72) | 6.01 ± 3.85 (5.36) | 2.44 ± 0.43 (2.52) | 5.25 ± 1.07 (5.76) | 2.37 ± 0.77 (2.60) |
| right | p | 0.843 | 100/100 | 0 | 94 | 1.84 ± 0.58 (1.71) | 6.74 ± 4.16 (6.68) | 2.39 ± 0.43 (2.45) | 5.10 ± 1.11 (5.53) | 2.29 ± 0.80 (2.52) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.870 | 25/25 | 0 | 25 | 1.27 ± 0.26 (1.30) | 4.80 ± 2.63 (4.87) | 2.31 ± 0.42 (2.49) | 5.02 ± 1.09 (5.42) | 2.16 ± 0.72 (2.27) |
| forward/right | p | 0.880 | 25/25 | 0 | 25 | 1.29 ± 0.25 (1.30) | 4.22 ± 2.69 (4.31) | 2.33 ± 0.42 (2.40) | 5.01 ± 1.08 (5.63) | 2.16 ± 0.74 (2.22) |
| left/left | p | 0.856 | 25/25 | 0 | 24 | 1.65 ± 0.32 (1.60) | 7.21 ± 4.24 (7.37) | 2.51 ± 0.41 (2.55) | 5.34 ± 1.07 (5.76) | 2.47 ± 0.78 (2.62) |
| left/right | p | 0.854 | 25/25 | 0 | 24 | 1.82 ± 0.37 (1.80) | 6.58 ± 3.38 (6.75) | 2.31 ± 0.41 (2.40) | 4.99 ± 1.09 (5.36) | 2.19 ± 0.77 (2.17) |
| back/left | p | 0.802 | 25/25 | 0 | 24 | 2.55 ± 0.30 (2.48) | 8.05 ± 3.95 (7.37) | 2.61 ± 0.43 (2.66) | 5.56 ± 1.04 (5.91) | 2.66 ± 0.77 (2.80) |
| back/right | p | 0.791 | 25/25 | 0 | 21 | 2.58 ± 0.39 (2.54) | 9.25 ± 4.61 (9.31) | 2.55 ± 0.43 (2.71) | 5.41 ± 1.11 (6.04) | 2.55 ± 0.82 (2.98) |
| right/left | p | 0.854 | 25/25 | 0 | 25 | 1.86 ± 0.37 (1.82) | 3.97 ± 2.73 (2.97) | 2.34 ± 0.38 (2.49) | 5.06 ± 1.00 (5.65) | 2.20 ± 0.68 (2.40) |
| right/right | p | 0.847 | 25/25 | 0 | 24 | 1.67 ± 0.34 (1.64) | 6.93 ± 4.10 (7.36) | 2.36 ± 0.43 (2.47) | 5.01 ± 1.10 (5.57) | 2.25 ± 0.80 (2.49) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.877 | 6.7 | 5.95 | 2.85 |
| p | normal | 0.811 | 6.1 | 4.40 | 1.81 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.751 | 0.12 | 2.46 ± 0.76 (2.32) | 3.82 | 1.41 |
| p | medium | 20 | 0.882 | 0.78 | 1.21 ± 0.14 (1.24) | 3.88 | 1.48 |
| p | strong | 126 | 0.878 | 0.79 | - | 5.96 | 2.86 |

## Notes

- p: score 0.844, 200/200 kicked, 0 fell; worst sector back (0.797).

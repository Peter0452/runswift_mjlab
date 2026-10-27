# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_04-46-54_u4b_u4_bhball/model_20950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.845** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 194 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.85 ± 0.56 (1.75) |
| Direction error [°] | 5.83 ± 4.13 (5.08) |
| Avg ball speed [m/s] | 2.34 ± 0.42 (2.40) |
| Peak ball speed [m/s] | 4.99 ± 1.04 (5.42) |
| Distance [m] | 2.16 ± 0.70 (2.31) |
| Path length [m] | 2.17 ± 0.70 (2.33) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.862 | 50/50 | 0 | 50 | 1.31 ± 0.25 (1.32) | 4.34 ± 3.16 (3.10) | 2.21 ± 0.43 (2.15) | 4.72 ± 1.14 (4.78) | 1.94 ± 0.71 (1.74) |
| left | p | 0.873 | 50/50 | 0 | 49 | 1.76 ± 0.36 (1.75) | 5.71 ± 4.13 (5.39) | 2.40 ± 0.39 (2.50) | 5.15 ± 0.93 (5.59) | 2.25 ± 0.62 (2.39) |
| back | p | 0.789 | 50/50 | 0 | 46 | 2.57 ± 0.35 (2.50) | 8.12 ± 4.37 (7.21) | 2.44 ± 0.38 (2.45) | 5.13 ± 0.96 (5.46) | 2.32 ± 0.70 (2.46) |
| right | p | 0.855 | 50/50 | 0 | 49 | 1.77 ± 0.35 (1.73) | 5.13 ± 3.75 (4.23) | 2.32 ± 0.42 (2.39) | 4.94 ± 1.08 (5.32) | 2.12 ± 0.70 (2.28) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.847 | 100/100 | 0 | 97 | 1.86 ± 0.57 (1.75) | 5.66 ± 3.99 (4.88) | 2.35 ± 0.41 (2.39) | 4.99 ± 1.04 (5.36) | 2.17 ± 0.72 (2.27) |
| right | p | 0.842 | 100/100 | 0 | 97 | 1.84 ± 0.55 (1.75) | 6.00 ± 4.26 (5.33) | 2.34 ± 0.43 (2.42) | 4.98 ± 1.04 (5.50) | 2.14 ± 0.69 (2.34) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.870 | 25/25 | 0 | 25 | 1.32 ± 0.25 (1.32) | 4.07 ± 2.91 (3.03) | 2.27 ± 0.43 (2.26) | 4.81 ± 1.15 (5.02) | 2.03 ± 0.75 (1.99) |
| forward/right | p | 0.854 | 25/25 | 0 | 25 | 1.29 ± 0.26 (1.32) | 4.62 ± 3.37 (3.51) | 2.14 ± 0.43 (1.94) | 4.63 ± 1.11 (4.34) | 1.85 ± 0.66 (1.50) |
| left/left | p | 0.880 | 25/25 | 0 | 24 | 1.64 ± 0.34 (1.72) | 4.85 ± 4.19 (3.83) | 2.35 ± 0.38 (2.33) | 5.03 ± 0.95 (5.47) | 2.19 ± 0.64 (2.27) |
| left/right | p | 0.866 | 25/25 | 0 | 25 | 1.87 ± 0.35 (1.98) | 6.58 ± 3.87 (6.20) | 2.44 ± 0.40 (2.57) | 5.26 ± 0.90 (5.61) | 2.32 ± 0.59 (2.41) |
| back/left | p | 0.793 | 25/25 | 0 | 24 | 2.59 ± 0.37 (2.60) | 7.67 ± 3.83 (6.72) | 2.47 ± 0.40 (2.42) | 5.20 ± 1.01 (5.37) | 2.38 ± 0.76 (2.40) |
| back/right | p | 0.785 | 25/25 | 0 | 22 | 2.54 ± 0.33 (2.50) | 8.58 ± 4.81 (8.00) | 2.41 ± 0.37 (2.53) | 5.06 ± 0.90 (5.48) | 2.26 ± 0.63 (2.50) |
| right/left | p | 0.847 | 25/25 | 0 | 24 | 1.87 ± 0.34 (1.78) | 6.04 ± 3.93 (5.24) | 2.29 ± 0.40 (2.40) | 4.94 ± 1.02 (5.34) | 2.09 ± 0.64 (2.27) |
| right/right | p | 0.863 | 25/25 | 0 | 25 | 1.67 ± 0.32 (1.68) | 4.22 ± 3.32 (3.00) | 2.35 ± 0.44 (2.39) | 4.95 ± 1.14 (5.30) | 2.15 ± 0.76 (2.32) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.881 | 6.1 | 5.73 | 2.62 |
| p | normal | 0.809 | 5.6 | 4.24 | 1.70 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.754 | 0.13 | 2.32 ± 0.66 (2.15) | 3.70 | 1.35 |
| p | medium | 16 | 0.896 | 0.82 | 1.17 ± 0.11 (1.17) | 3.80 | 1.44 |
| p | strong | 126 | 0.880 | 0.76 | - | 5.73 | 2.62 |

## Notes

- p: score 0.845, 200/200 kicked, 0 fell; worst sector back (0.789).

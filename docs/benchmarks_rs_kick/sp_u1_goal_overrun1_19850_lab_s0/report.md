# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_08-10-04_u1_goal_overrun1/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.850** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.64 ± 0.55 (1.57) |
| Direction error [°] | 5.21 ± 3.15 (4.79) |
| Avg ball speed [m/s] | 1.76 ± 0.34 (1.89) |
| Peak ball speed [m/s] | 3.82 ± 0.84 (4.20) |
| Distance [m] | 1.35 ± 0.47 (1.48) |
| Path length [m] | 1.36 ± 0.47 (1.48) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.851 | 50/50 | 0 | 50 | 1.08 ± 0.24 (1.12) | 4.60 ± 3.12 (3.54) | 1.60 ± 0.35 (1.51) | 3.47 ± 0.83 (3.02) | 1.14 ± 0.45 (0.95) |
| left | p | 0.860 | 50/50 | 0 | 50 | 1.57 ± 0.36 (1.57) | 5.68 ± 3.19 (5.22) | 1.77 ± 0.34 (1.89) | 3.89 ± 0.84 (4.25) | 1.39 ± 0.46 (1.50) |
| back | p | 0.836 | 50/50 | 0 | 50 | 2.33 ± 0.27 (2.30) | 5.25 ± 2.43 (5.45) | 1.88 ± 0.28 (2.00) | 4.09 ± 0.74 (4.42) | 1.52 ± 0.43 (1.63) |
| right | p | 0.852 | 50/50 | 0 | 49 | 1.57 ± 0.36 (1.55) | 5.29 ± 3.64 (4.51) | 1.77 ± 0.33 (1.89) | 3.84 ± 0.82 (4.22) | 1.35 ± 0.45 (1.47) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.848 | 100/100 | 0 | 100 | 1.64 ± 0.56 (1.60) | 5.28 ± 2.98 (4.82) | 1.76 ± 0.32 (1.89) | 3.85 ± 0.81 (4.20) | 1.36 ± 0.45 (1.48) |
| right | p | 0.852 | 100/100 | 0 | 99 | 1.64 ± 0.54 (1.54) | 5.13 ± 3.31 (4.76) | 1.75 ± 0.35 (1.88) | 3.80 ± 0.86 (4.19) | 1.34 ± 0.48 (1.41) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.847 | 25/25 | 0 | 25 | 1.07 ± 0.24 (1.12) | 5.32 ± 3.22 (4.35) | 1.64 ± 0.31 (1.72) | 3.53 ± 0.75 (3.55) | 1.18 ± 0.42 (1.19) |
| forward/right | p | 0.855 | 25/25 | 0 | 25 | 1.08 ± 0.25 (1.12) | 3.89 ± 2.83 (2.94) | 1.57 ± 0.37 (1.41) | 3.41 ± 0.89 (2.92) | 1.11 ± 0.47 (0.90) |
| left/left | p | 0.854 | 25/25 | 0 | 25 | 1.46 ± 0.36 (1.52) | 5.71 ± 3.27 (5.19) | 1.72 ± 0.35 (1.89) | 3.79 ± 0.86 (4.21) | 1.33 ± 0.44 (1.50) |
| left/right | p | 0.867 | 25/25 | 0 | 25 | 1.69 ± 0.33 (1.72) | 5.65 ± 3.11 (5.48) | 1.82 ± 0.33 (1.93) | 3.98 ± 0.82 (4.26) | 1.45 ± 0.46 (1.50) |
| back/left | p | 0.831 | 25/25 | 0 | 25 | 2.35 ± 0.28 (2.26) | 5.32 ± 2.47 (5.58) | 1.90 ± 0.24 (1.99) | 4.16 ± 0.69 (4.41) | 1.56 ± 0.41 (1.63) |
| back/right | p | 0.841 | 25/25 | 0 | 25 | 2.31 ± 0.25 (2.32) | 5.19 ± 2.40 (5.32) | 1.85 ± 0.31 (2.01) | 4.03 ± 0.78 (4.42) | 1.48 ± 0.45 (1.58) |
| right/left | p | 0.858 | 25/25 | 0 | 25 | 1.68 ± 0.34 (1.66) | 4.78 ± 2.81 (4.70) | 1.79 ± 0.33 (1.92) | 3.92 ± 0.82 (4.30) | 1.39 ± 0.44 (1.51) |
| right/right | p | 0.845 | 25/25 | 0 | 24 | 1.47 ± 0.35 (1.50) | 5.80 ± 4.24 (4.33) | 1.76 ± 0.33 (1.88) | 3.77 ± 0.81 (4.06) | 1.31 ± 0.45 (1.26) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.859 | 5.0 | 4.37 | 1.64 |
| p | normal | 0.840 | 5.4 | 3.28 | 1.07 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.814 | 0.36 | 1.85 ± 0.62 (1.65) | 2.93 | 0.87 |
| p | medium | 16 | 0.892 | 0.85 | 0.85 ± 0.16 (0.86) | 2.76 | 0.80 |
| p | strong | 126 | 0.861 | 0.58 | - | 4.37 | 1.64 |

## Notes

- p: score 0.850, 200/200 kicked, 0 fell; worst sector back (0.836).

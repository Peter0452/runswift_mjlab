# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_08-10-04_u1_goal_overrun1/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.856** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 10 |
| Time to kick [s] | 1.63 ± 0.54 (1.54) |
| Direction error [°] | 6.01 ± 14.84 (3.93) |
| Avg ball speed [m/s] | 1.45 ± 0.43 (1.48) |
| Peak ball speed [m/s] | 3.52 ± 1.01 (3.61) |
| Distance [m] | 1.12 ± 0.53 (1.10) |
| Path length [m] | 1.12 ± 0.53 (1.10) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.843 | 50/50 | 0 | 47 | 1.11 ± 0.36 (1.12) | 7.66 ± 17.61 (4.24) | 1.19 ± 0.39 (1.13) | 2.91 ± 0.89 (2.74) | 0.80 ± 0.42 (0.69) |
| left | p | 0.873 | 50/50 | 0 | 50 | 1.57 ± 0.35 (1.54) | 4.23 ± 2.71 (3.77) | 1.53 ± 0.43 (1.64) | 3.71 ± 0.93 (3.93) | 1.21 ± 0.51 (1.27) |
| back | p | 0.852 | 50/50 | 0 | 49 | 2.29 ± 0.26 (2.25) | 7.13 ± 23.35 (3.32) | 1.66 ± 0.41 (1.70) | 3.95 ± 1.04 (4.26) | 1.38 ± 0.56 (1.52) |
| right | p | 0.855 | 50/50 | 0 | 50 | 1.57 ± 0.36 (1.54) | 5.02 ± 3.21 (4.49) | 1.44 ± 0.35 (1.45) | 3.50 ± 0.88 (3.49) | 1.09 ± 0.43 (1.04) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.854 | 100/100 | 0 | 97 | 1.64 ± 0.54 (1.57) | 7.28 ± 20.65 (3.67) | 1.46 ± 0.45 (1.52) | 3.53 ± 1.03 (3.78) | 1.13 ± 0.55 (1.12) |
| right | p | 0.858 | 100/100 | 0 | 99 | 1.63 ± 0.54 (1.54) | 4.74 ± 3.32 (4.07) | 1.45 ± 0.41 (1.48) | 3.50 ± 1.00 (3.58) | 1.11 ± 0.50 (1.08) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.840 | 25/25 | 0 | 23 | 1.15 ± 0.45 (1.16) | 9.81 ± 24.38 (4.37) | 1.20 ± 0.36 (1.12) | 2.92 ± 0.81 (2.71) | 0.80 ± 0.40 (0.64) |
| forward/right | p | 0.846 | 25/25 | 0 | 24 | 1.07 ± 0.25 (1.12) | 5.51 ± 4.13 (4.13) | 1.18 ± 0.42 (1.23) | 2.90 ± 0.96 (2.76) | 0.80 ± 0.44 (0.71) |
| left/left | p | 0.869 | 25/25 | 0 | 25 | 1.46 ± 0.34 (1.48) | 3.86 ± 2.68 (2.65) | 1.43 ± 0.46 (1.52) | 3.51 ± 0.93 (3.82) | 1.12 ± 0.54 (1.20) |
| left/right | p | 0.876 | 25/25 | 0 | 25 | 1.68 ± 0.33 (1.70) | 4.60 ± 2.68 (5.23) | 1.62 ± 0.36 (1.73) | 3.91 ± 0.87 (4.23) | 1.29 ± 0.45 (1.40) |
| back/left | p | 0.848 | 25/25 | 0 | 24 | 2.28 ± 0.25 (2.26) | 10.52 ± 32.58 (3.41) | 1.65 ± 0.46 (1.72) | 3.96 ± 1.09 (4.41) | 1.41 ± 0.59 (1.56) |
| back/right | p | 0.857 | 25/25 | 0 | 25 | 2.30 ± 0.26 (2.24) | 3.73 ± 2.39 (3.28) | 1.66 ± 0.36 (1.59) | 3.95 ± 0.99 (3.92) | 1.35 ± 0.51 (1.34) |
| right/left | p | 0.857 | 25/25 | 0 | 25 | 1.68 ± 0.34 (1.62) | 4.92 ± 2.90 (5.70) | 1.54 ± 0.37 (1.69) | 3.76 ± 0.94 (4.15) | 1.19 ± 0.45 (1.34) |
| right/right | p | 0.853 | 25/25 | 0 | 25 | 1.46 ± 0.34 (1.46) | 5.12 ± 3.50 (4.39) | 1.35 ± 0.30 (1.35) | 3.24 ± 0.73 (3.16) | 0.99 ± 0.40 (0.93) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.856 | 4.7 | 4.08 | 1.40 |
| p | normal | 0.856 | 7.3 | 2.95 | 0.83 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.839 | 0.48 | 1.56 ± 0.60 (1.38) | 2.45 | 0.58 |
| p | medium | 16 | 0.895 | 0.77 | 0.79 ± 0.19 (0.86) | 2.55 | 0.64 |
| p | strong | 126 | 0.859 | 0.55 | - | 4.13 | 1.43 |

## Notes

- p: score 0.856, 200/200 kicked, 0 fell; worst sector forward (0.843).

# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_21-18-55_q2_speed_to_ball/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.849** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.57 ± 0.52 (1.50) |
| Direction error [°] | 5.20 ± 3.26 (4.75) |
| Avg ball speed [m/s] | 1.86 ± 0.38 (1.98) |
| Peak ball speed [m/s] | 4.05 ± 0.92 (4.21) |
| Distance [m] | 1.44 ± 0.52 (1.51) |
| Path length [m] | 1.45 ± 0.52 (1.52) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.841 | 50/50 | 0 | 50 | 1.03 ± 0.22 (1.05) | 4.56 ± 2.94 (3.84) | 1.52 ± 0.38 (1.41) | 3.25 ± 0.82 (3.08) | 0.98 ± 0.45 (0.84) |
| left | p | 0.869 | 50/50 | 0 | 49 | 1.50 ± 0.34 (1.52) | 5.04 ± 3.47 (4.44) | 1.98 ± 0.30 (2.07) | 4.34 ± 0.78 (4.70) | 1.60 ± 0.45 (1.69) |
| back | p | 0.841 | 50/50 | 0 | 50 | 2.23 ± 0.26 (2.20) | 5.72 ± 2.72 (6.05) | 2.06 ± 0.25 (2.17) | 4.50 ± 0.69 (4.84) | 1.72 ± 0.42 (1.86) |
| right | p | 0.844 | 50/50 | 0 | 49 | 1.50 ± 0.33 (1.49) | 5.49 ± 3.71 (4.97) | 1.89 ± 0.32 (1.99) | 4.11 ± 0.83 (4.32) | 1.46 ± 0.44 (1.51) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.848 | 100/100 | 0 | 99 | 1.57 ± 0.52 (1.51) | 5.27 ± 3.36 (4.57) | 1.88 ± 0.36 (1.99) | 4.07 ± 0.90 (4.21) | 1.46 ± 0.52 (1.52) |
| right | p | 0.850 | 100/100 | 0 | 99 | 1.56 ± 0.51 (1.49) | 5.13 ± 3.17 (4.79) | 1.85 ± 0.39 (1.96) | 4.03 ± 0.93 (4.26) | 1.42 ± 0.52 (1.51) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.841 | 25/25 | 0 | 25 | 1.03 ± 0.22 (1.06) | 4.57 ± 2.83 (3.26) | 1.54 ± 0.36 (1.40) | 3.26 ± 0.74 (3.09) | 1.00 ± 0.45 (0.84) |
| forward/right | p | 0.841 | 25/25 | 0 | 25 | 1.03 ± 0.23 (1.04) | 4.55 ± 3.05 (4.50) | 1.50 ± 0.41 (1.42) | 3.24 ± 0.89 (3.07) | 0.97 ± 0.45 (0.91) |
| left/left | p | 0.858 | 25/25 | 0 | 24 | 1.40 ± 0.33 (1.46) | 5.71 ± 4.20 (4.37) | 1.93 ± 0.28 (2.03) | 4.19 ± 0.74 (4.51) | 1.52 ± 0.42 (1.61) |
| left/right | p | 0.881 | 25/25 | 0 | 25 | 1.60 ± 0.31 (1.60) | 4.37 ± 2.35 (4.68) | 2.02 ± 0.32 (2.16) | 4.49 ± 0.78 (4.85) | 1.67 ± 0.46 (1.77) |
| back/left | p | 0.838 | 25/25 | 0 | 25 | 2.24 ± 0.25 (2.20) | 5.94 ± 3.07 (6.45) | 2.10 ± 0.23 (2.20) | 4.56 ± 0.69 (4.99) | 1.77 ± 0.44 (1.94) |
| back/right | p | 0.845 | 25/25 | 0 | 25 | 2.21 ± 0.26 (2.20) | 5.49 ± 2.31 (5.44) | 2.03 ± 0.26 (2.17) | 4.44 ± 0.69 (4.81) | 1.67 ± 0.39 (1.79) |
| right/left | p | 0.857 | 25/25 | 0 | 25 | 1.60 ± 0.32 (1.58) | 4.87 ± 2.96 (4.92) | 1.94 ± 0.31 (2.12) | 4.28 ± 0.85 (4.77) | 1.54 ± 0.44 (1.64) |
| right/right | p | 0.832 | 25/25 | 0 | 24 | 1.41 ± 0.32 (1.44) | 6.10 ± 4.24 (5.50) | 1.84 ± 0.33 (1.81) | 3.94 ± 0.77 (3.69) | 1.37 ± 0.41 (1.25) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.859 | 5.6 | 4.45 | 1.64 |
| p | normal | 0.839 | 4.8 | 3.65 | 1.24 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.800 | 0.25 | 2.02 ± 0.63 (1.83) | 3.22 | 1.00 |
| p | medium | 16 | 0.917 | 0.85 | 1.01 ± 0.17 (1.03) | 3.28 | 1.04 |
| p | strong | 126 | 0.863 | 0.60 | - | 4.53 | 1.69 |

## Notes

- p: score 0.849, 200/200 kicked, 0 fell; worst sector forward (0.841).

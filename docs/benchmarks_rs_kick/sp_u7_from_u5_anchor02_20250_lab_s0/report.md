# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_11-31-02_u7_from_u5_anchor02/model_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.856** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.57 ± 0.52 (1.50) |
| Direction error [°] | 4.47 ± 2.89 (3.87) |
| Avg ball speed [m/s] | 1.71 ± 0.34 (1.78) |
| Peak ball speed [m/s] | 3.80 ± 0.82 (3.87) |
| Distance [m] | 1.27 ± 0.44 (1.28) |
| Path length [m] | 1.28 ± 0.45 (1.29) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.864 | 50/50 | 0 | 50 | 1.04 ± 0.23 (1.06) | 3.62 ± 2.67 (2.57) | 1.51 ± 0.38 (1.41) | 3.30 ± 0.85 (3.01) | 1.01 ± 0.43 (0.92) |
| left | p | 0.873 | 50/50 | 0 | 50 | 1.51 ± 0.33 (1.53) | 4.11 ± 2.81 (3.44) | 1.77 ± 0.31 (1.91) | 3.97 ± 0.76 (4.40) | 1.35 ± 0.42 (1.50) |
| back | p | 0.841 | 50/50 | 0 | 50 | 2.22 ± 0.26 (2.17) | 5.19 ± 2.88 (4.84) | 1.89 ± 0.24 (1.96) | 4.21 ± 0.65 (4.42) | 1.51 ± 0.38 (1.62) |
| right | p | 0.845 | 50/50 | 0 | 50 | 1.50 ± 0.33 (1.47) | 4.96 ± 2.89 (5.08) | 1.68 ± 0.31 (1.75) | 3.73 ± 0.75 (3.83) | 1.22 ± 0.39 (1.25) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.853 | 100/100 | 0 | 100 | 1.57 ± 0.52 (1.52) | 4.49 ± 2.80 (3.93) | 1.72 ± 0.30 (1.78) | 3.83 ± 0.75 (3.90) | 1.28 ± 0.42 (1.27) |
| right | p | 0.859 | 100/100 | 0 | 100 | 1.56 ± 0.51 (1.49) | 4.45 ± 2.97 (3.83) | 1.70 ± 0.37 (1.78) | 3.78 ± 0.90 (3.87) | 1.26 ± 0.47 (1.29) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.858 | 25/25 | 0 | 25 | 1.04 ± 0.23 (1.08) | 3.60 ± 2.50 (2.47) | 1.57 ± 0.30 (1.68) | 3.41 ± 0.67 (3.57) | 1.05 ± 0.36 (1.11) |
| forward/right | p | 0.871 | 25/25 | 0 | 25 | 1.03 ± 0.23 (1.04) | 3.64 ± 2.84 (3.30) | 1.46 ± 0.44 (1.39) | 3.20 ± 0.98 (2.93) | 0.96 ± 0.49 (0.90) |
| left/left | p | 0.860 | 25/25 | 0 | 25 | 1.42 ± 0.33 (1.50) | 4.81 ± 2.96 (4.95) | 1.72 ± 0.29 (1.74) | 3.86 ± 0.73 (3.75) | 1.29 ± 0.41 (1.26) |
| left/right | p | 0.886 | 25/25 | 0 | 25 | 1.60 ± 0.31 (1.62) | 3.41 ± 2.46 (2.60) | 1.81 ± 0.32 (1.96) | 4.09 ± 0.77 (4.49) | 1.41 ± 0.42 (1.55) |
| back/left | p | 0.835 | 25/25 | 0 | 25 | 2.24 ± 0.26 (2.18) | 5.52 ± 2.83 (5.00) | 1.88 ± 0.22 (1.94) | 4.19 ± 0.60 (4.39) | 1.50 ± 0.38 (1.66) |
| back/right | p | 0.846 | 25/25 | 0 | 25 | 2.21 ± 0.26 (2.16) | 4.86 ± 2.89 (4.53) | 1.89 ± 0.27 (2.00) | 4.22 ± 0.69 (4.53) | 1.51 ± 0.38 (1.57) |
| right/left | p | 0.857 | 25/25 | 0 | 25 | 1.60 ± 0.32 (1.58) | 4.02 ± 2.50 (3.62) | 1.73 ± 0.31 (1.85) | 3.85 ± 0.76 (4.09) | 1.28 ± 0.40 (1.36) |
| right/right | p | 0.834 | 25/25 | 0 | 25 | 1.41 ± 0.31 (1.42) | 5.91 ± 2.94 (5.75) | 1.63 ± 0.29 (1.66) | 3.61 ± 0.71 (3.65) | 1.16 ± 0.37 (1.19) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.862 | 4.7 | 4.25 | 1.49 |
| p | normal | 0.850 | 4.2 | 3.36 | 1.05 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.820 | 0.32 | 1.89 ± 0.64 (1.74) | 3.01 | 0.87 |
| p | medium | 16 | 0.928 | 0.85 | 0.89 ± 0.15 (0.84) | 2.92 | 0.83 |
| p | strong | 126 | 0.863 | 0.57 | - | 4.28 | 1.51 |

## Notes

- p: score 0.856, 200/200 kicked, 0 fell; worst sector back (0.841).

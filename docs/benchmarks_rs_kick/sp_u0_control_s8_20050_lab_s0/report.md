# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_08-10-04_u0_control_s8/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.848** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.67 ± 0.55 (1.60) |
| Direction error [°] | 5.47 ± 9.55 (3.86) |
| Avg ball speed [m/s] | 1.97 ± 0.37 (1.95) |
| Peak ball speed [m/s] | 4.19 ± 0.85 (4.22) |
| Distance [m] | 1.62 ± 0.53 (1.55) |
| Path length [m] | 1.63 ± 0.53 (1.55) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.851 | 50/50 | 0 | 50 | 1.09 ± 0.24 (1.16) | 4.01 ± 3.13 (2.90) | 1.75 ± 0.32 (1.71) | 3.74 ± 0.73 (3.60) | 1.30 ± 0.44 (1.20) |
| left | p | 0.864 | 50/50 | 0 | 49 | 1.62 ± 0.37 (1.63) | 5.43 ± 3.87 (4.84) | 2.06 ± 0.33 (2.12) | 4.41 ± 0.78 (4.53) | 1.76 ± 0.52 (1.82) |
| back | p | 0.840 | 50/50 | 0 | 49 | 2.36 ± 0.26 (2.31) | 6.71 ± 17.84 (3.20) | 2.08 ± 0.41 (2.17) | 4.44 ± 0.95 (4.76) | 1.80 ± 0.53 (1.98) |
| right | p | 0.836 | 50/50 | 0 | 48 | 1.61 ± 0.37 (1.58) | 5.72 ± 4.30 (3.86) | 1.98 ± 0.31 (1.93) | 4.19 ± 0.73 (4.01) | 1.61 ± 0.46 (1.45) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.845 | 100/100 | 0 | 99 | 1.67 ± 0.57 (1.59) | 5.14 ± 3.74 (4.49) | 1.97 ± 0.32 (1.99) | 4.22 ± 0.78 (4.30) | 1.63 ± 0.51 (1.55) |
| right | p | 0.850 | 100/100 | 0 | 97 | 1.67 ± 0.54 (1.61) | 5.80 ± 12.98 (3.47) | 1.96 ± 0.41 (1.95) | 4.17 ± 0.91 (4.15) | 1.61 ± 0.54 (1.52) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.846 | 25/25 | 0 | 25 | 1.08 ± 0.23 (1.16) | 4.76 ± 3.42 (4.11) | 1.75 ± 0.28 (1.75) | 3.75 ± 0.66 (3.62) | 1.30 ± 0.41 (1.21) |
| forward/right | p | 0.856 | 25/25 | 0 | 25 | 1.10 ± 0.26 (1.16) | 3.25 ± 2.60 (2.60) | 1.74 ± 0.35 (1.71) | 3.73 ± 0.79 (3.44) | 1.30 ± 0.46 (1.19) |
| left/left | p | 0.861 | 25/25 | 0 | 25 | 1.51 ± 0.36 (1.54) | 5.34 ± 3.10 (4.85) | 2.02 ± 0.30 (2.14) | 4.31 ± 0.75 (4.51) | 1.70 ± 0.49 (1.78) |
| left/right | p | 0.867 | 25/25 | 0 | 24 | 1.73 ± 0.35 (1.76) | 5.52 ± 4.50 (4.53) | 2.11 ± 0.35 (2.10) | 4.50 ± 0.81 (4.55) | 1.82 ± 0.54 (1.84) |
| back/left | p | 0.840 | 25/25 | 0 | 25 | 2.40 ± 0.27 (2.32) | 4.46 ± 3.83 (3.14) | 2.13 ± 0.28 (2.19) | 4.55 ± 0.74 (4.85) | 1.85 ± 0.49 (2.03) |
| back/right | p | 0.840 | 25/25 | 0 | 24 | 2.32 ± 0.25 (2.28) | 8.95 ± 24.73 (3.27) | 2.03 ± 0.50 (2.14) | 4.33 ± 1.10 (4.62) | 1.75 ± 0.56 (1.94) |
| right/left | p | 0.835 | 25/25 | 0 | 24 | 1.70 ± 0.35 (1.66) | 5.99 ± 4.32 (5.40) | 2.00 ± 0.31 (1.93) | 4.26 ± 0.74 (4.29) | 1.66 ± 0.46 (1.59) |
| right/right | p | 0.836 | 25/25 | 0 | 24 | 1.52 ± 0.37 (1.52) | 5.46 ± 4.27 (3.68) | 1.96 ± 0.32 (1.88) | 4.12 ± 0.72 (3.86) | 1.57 ± 0.46 (1.41) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.863 | 5.1 | 4.62 | 1.86 |
| p | normal | 0.832 | 5.8 | 3.77 | 1.38 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.784 | 0.20 | 2.13 ± 0.75 (1.98) | 3.37 | 1.14 |
| p | medium | 16 | 0.910 | 0.88 | 1.02 ± 0.14 (1.05) | 3.31 | 1.09 |
| p | strong | 126 | 0.869 | 0.63 | - | 4.69 | 1.91 |

## Notes

- p: score 0.848, 200/200 kicked, 0 fell; worst sector right (0.836).

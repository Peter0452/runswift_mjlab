# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_08-10-04_u0_control_s8/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.845** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.62 ± 0.54 (1.54) |
| Direction error [°] | 5.41 ± 3.75 (4.56) |
| Avg ball speed [m/s] | 2.01 ± 0.38 (2.04) |
| Peak ball speed [m/s] | 4.27 ± 0.89 (4.43) |
| Distance [m] | 1.67 ± 0.56 (1.63) |
| Path length [m] | 1.68 ± 0.57 (1.65) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.843 | 50/50 | 0 | 49 | 1.06 ± 0.24 (1.11) | 4.72 ± 3.81 (3.64) | 1.71 ± 0.36 (1.61) | 3.63 ± 0.83 (3.37) | 1.24 ± 0.50 (1.10) |
| left | p | 0.861 | 50/50 | 0 | 49 | 1.56 ± 0.34 (1.59) | 5.79 ± 3.85 (5.06) | 2.08 ± 0.37 (2.15) | 4.45 ± 0.86 (4.68) | 1.78 ± 0.53 (1.87) |
| back | p | 0.843 | 50/50 | 0 | 50 | 2.32 ± 0.27 (2.31) | 4.88 ± 3.01 (4.56) | 2.19 ± 0.29 (2.30) | 4.68 ± 0.75 (5.14) | 1.94 ± 0.49 (2.14) |
| right | p | 0.835 | 50/50 | 0 | 49 | 1.55 ± 0.34 (1.53) | 6.22 ± 4.03 (5.30) | 2.05 ± 0.31 (2.05) | 4.33 ± 0.77 (4.42) | 1.71 ± 0.48 (1.61) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.841 | 100/100 | 0 | 97 | 1.63 ± 0.55 (1.55) | 5.58 ± 3.76 (4.78) | 1.99 ± 0.38 (2.04) | 4.24 ± 0.91 (4.30) | 1.65 ± 0.58 (1.55) |
| right | p | 0.850 | 100/100 | 0 | 100 | 1.62 ± 0.54 (1.53) | 5.23 ± 3.73 (3.81) | 2.02 ± 0.37 (2.07) | 4.31 ± 0.88 (4.50) | 1.69 ± 0.55 (1.76) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.836 | 25/25 | 0 | 24 | 1.05 ± 0.23 (1.10) | 4.76 ± 3.72 (4.42) | 1.66 ± 0.32 (1.59) | 3.51 ± 0.76 (3.28) | 1.18 ± 0.48 (1.00) |
| forward/right | p | 0.849 | 25/25 | 0 | 25 | 1.06 ± 0.25 (1.12) | 4.68 ± 3.89 (2.52) | 1.75 ± 0.38 (1.63) | 3.75 ± 0.88 (3.44) | 1.31 ± 0.51 (1.16) |
| left/left | p | 0.846 | 25/25 | 0 | 24 | 1.46 ± 0.34 (1.52) | 6.55 ± 4.21 (5.66) | 1.97 ± 0.37 (2.09) | 4.19 ± 0.87 (4.32) | 1.61 ± 0.52 (1.54) |
| left/right | p | 0.875 | 25/25 | 0 | 25 | 1.66 ± 0.30 (1.66) | 5.03 ± 3.28 (3.95) | 2.19 ± 0.33 (2.32) | 4.71 ± 0.76 (5.05) | 1.95 ± 0.49 (2.11) |
| back/left | p | 0.839 | 25/25 | 0 | 25 | 2.34 ± 0.26 (2.32) | 5.03 ± 2.91 (4.86) | 2.21 ± 0.25 (2.26) | 4.72 ± 0.72 (4.92) | 1.98 ± 0.49 (2.15) |
| back/right | p | 0.847 | 25/25 | 0 | 25 | 2.30 ± 0.28 (2.28) | 4.74 ± 3.10 (3.78) | 2.17 ± 0.31 (2.33) | 4.64 ± 0.77 (5.14) | 1.91 ± 0.49 (2.13) |
| right/left | p | 0.844 | 25/25 | 0 | 24 | 1.66 ± 0.31 (1.62) | 5.99 ± 3.80 (5.11) | 2.14 ± 0.31 (2.20) | 4.52 ± 0.78 (4.84) | 1.84 ± 0.49 (1.92) |
| right/right | p | 0.827 | 25/25 | 0 | 25 | 1.45 ± 0.34 (1.50) | 6.46 ± 4.24 (5.49) | 1.97 ± 0.28 (1.91) | 4.14 ± 0.72 (3.87) | 1.58 ± 0.44 (1.46) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.868 | 5.2 | 4.72 | 1.93 |
| p | normal | 0.823 | 5.6 | 3.83 | 1.41 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.779 | 0.20 | 2.14 ± 0.68 (1.98) | 3.40 | 1.15 |
| p | medium | 16 | 0.881 | 0.80 | 1.03 ± 0.23 (1.12) | 3.33 | 1.13 |
| p | strong | 126 | 0.872 | 0.64 | - | 4.80 | 1.98 |

## Notes

- p: score 0.845, 200/200 kicked, 0 fell; worst sector right (0.835).

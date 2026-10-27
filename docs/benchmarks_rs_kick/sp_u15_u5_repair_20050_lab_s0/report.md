# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-26-24_u15_u5_repair/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.845** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.57 ± 0.53 (1.49) |
| Direction error [°] | 5.05 ± 3.16 (4.50) |
| Avg ball speed [m/s] | 1.91 ± 0.30 (1.94) |
| Peak ball speed [m/s] | 4.12 ± 0.72 (4.19) |
| Distance [m] | 1.54 ± 0.44 (1.55) |
| Path length [m] | 1.55 ± 0.44 (1.56) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.844 | 50/50 | 0 | 50 | 1.03 ± 0.23 (1.06) | 4.36 ± 3.08 (2.97) | 1.68 ± 0.36 (1.67) | 3.59 ± 0.79 (3.49) | 1.21 ± 0.47 (1.20) |
| left | p | 0.860 | 50/50 | 0 | 50 | 1.50 ± 0.34 (1.51) | 5.31 ± 3.34 (4.53) | 1.97 ± 0.21 (2.02) | 4.29 ± 0.57 (4.49) | 1.63 ± 0.35 (1.61) |
| back | p | 0.840 | 50/50 | 0 | 50 | 2.24 ± 0.28 (2.19) | 4.90 ± 2.77 (4.21) | 2.09 ± 0.20 (2.14) | 4.49 ± 0.57 (4.77) | 1.79 ± 0.35 (1.87) |
| right | p | 0.837 | 50/50 | 0 | 50 | 1.50 ± 0.34 (1.44) | 5.65 ± 3.25 (5.46) | 1.91 ± 0.24 (1.95) | 4.12 ± 0.60 (4.20) | 1.53 ± 0.34 (1.57) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.843 | 100/100 | 0 | 100 | 1.57 ± 0.53 (1.49) | 5.35 ± 3.07 (4.58) | 1.93 ± 0.27 (1.95) | 4.15 ± 0.67 (4.22) | 1.56 ± 0.41 (1.56) |
| right | p | 0.847 | 100/100 | 0 | 100 | 1.56 ± 0.52 (1.49) | 4.76 ± 3.22 (4.31) | 1.89 ± 0.33 (1.93) | 4.09 ± 0.76 (4.13) | 1.52 ± 0.46 (1.53) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.848 | 25/25 | 0 | 25 | 1.04 ± 0.23 (1.06) | 4.19 ± 2.82 (2.65) | 1.73 ± 0.31 (1.77) | 3.67 ± 0.66 (3.50) | 1.25 ± 0.39 (1.23) |
| forward/right | p | 0.840 | 25/25 | 0 | 25 | 1.02 ± 0.23 (1.02) | 4.52 ± 3.32 (3.19) | 1.62 ± 0.40 (1.63) | 3.50 ± 0.90 (3.49) | 1.17 ± 0.54 (1.20) |
| left/left | p | 0.849 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.48) | 6.18 ± 3.83 (4.36) | 1.93 ± 0.21 (1.93) | 4.17 ± 0.57 (4.20) | 1.57 ± 0.33 (1.63) |
| left/right | p | 0.872 | 25/25 | 0 | 25 | 1.58 ± 0.32 (1.58) | 4.43 ± 2.49 (4.53) | 2.01 ± 0.20 (2.05) | 4.41 ± 0.54 (4.64) | 1.69 ± 0.35 (1.59) |
| back/left | p | 0.833 | 25/25 | 0 | 25 | 2.26 ± 0.27 (2.18) | 5.33 ± 2.37 (4.49) | 2.12 ± 0.16 (2.14) | 4.57 ± 0.47 (4.77) | 1.84 ± 0.31 (1.88) |
| back/right | p | 0.847 | 25/25 | 0 | 25 | 2.22 ± 0.29 (2.20) | 4.47 ± 3.07 (3.99) | 2.06 ± 0.24 (2.13) | 4.41 ± 0.64 (4.74) | 1.74 ± 0.37 (1.86) |
| right/left | p | 0.844 | 25/25 | 0 | 25 | 1.58 ± 0.32 (1.58) | 5.69 ± 2.72 (5.57) | 1.93 ± 0.24 (1.96) | 4.18 ± 0.65 (4.40) | 1.57 ± 0.37 (1.57) |
| right/right | p | 0.830 | 25/25 | 0 | 25 | 1.41 ± 0.34 (1.42) | 5.62 ± 3.71 (5.21) | 1.89 ± 0.23 (1.92) | 4.05 ± 0.53 (4.06) | 1.50 ± 0.30 (1.53) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.864 | 5.1 | 4.49 | 1.74 |
| p | normal | 0.826 | 5.0 | 3.76 | 1.34 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.784 | 0.18 | 2.16 ± 0.68 (2.00) | 3.45 | 1.17 |
| p | medium | 16 | 0.908 | 0.85 | 1.11 ± 0.15 (1.12) | 3.59 | 1.27 |
| p | strong | 126 | 0.865 | 0.60 | - | 4.50 | 1.75 |

## Notes

- p: score 0.845, 200/200 kicked, 0 fell; worst sector right (0.837).

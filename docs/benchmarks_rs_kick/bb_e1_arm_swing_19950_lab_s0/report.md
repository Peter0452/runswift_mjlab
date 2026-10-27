# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_00-03-35_e1_arm_swing/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.828** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 192 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.58 ± 0.52 (1.52) |
| Direction error [°] | 7.76 ± 11.85 (6.15) |
| Avg ball speed [m/s] | 2.02 ± 0.40 (2.02) |
| Peak ball speed [m/s] | 4.27 ± 0.88 (4.23) |
| Distance [m] | 1.67 ± 0.56 (1.56) |
| Path length [m] | 1.68 ± 0.56 (1.57) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.835 | 50/50 | 0 | 50 | 1.03 ± 0.24 (1.05) | 5.45 ± 3.58 (4.47) | 1.71 ± 0.33 (1.77) | 3.64 ± 0.74 (3.56) | 1.23 ± 0.43 (1.25) |
| left | p | 0.838 | 50/50 | 0 | 46 | 1.53 ± 0.35 (1.55) | 7.60 ± 4.68 (7.06) | 2.09 ± 0.31 (2.14) | 4.43 ± 0.70 (4.59) | 1.75 ± 0.46 (1.74) |
| back | p | 0.822 | 50/50 | 0 | 48 | 2.22 ± 0.26 (2.20) | 10.19 ± 22.29 (6.74) | 2.22 ± 0.41 (2.28) | 4.69 ± 0.95 (4.92) | 2.00 ± 0.57 (2.14) |
| right | p | 0.818 | 50/50 | 0 | 48 | 1.52 ± 0.33 (1.50) | 7.80 ± 4.32 (8.64) | 2.06 ± 0.33 (2.03) | 4.33 ± 0.73 (4.29) | 1.70 ± 0.45 (1.60) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.827 | 100/100 | 0 | 96 | 1.57 ± 0.51 (1.54) | 8.39 ± 16.20 (6.15) | 2.00 ± 0.39 (2.02) | 4.24 ± 0.87 (4.24) | 1.65 ± 0.53 (1.56) |
| right | p | 0.829 | 100/100 | 0 | 96 | 1.58 ± 0.53 (1.49) | 7.13 ± 4.19 (6.26) | 2.04 ± 0.40 (2.01) | 4.31 ± 0.89 (4.23) | 1.69 ± 0.58 (1.57) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.827 | 25/25 | 0 | 25 | 1.03 ± 0.23 (1.10) | 5.93 ± 3.35 (5.16) | 1.72 ± 0.27 (1.82) | 3.65 ± 0.61 (3.59) | 1.24 ± 0.38 (1.30) |
| forward/right | p | 0.844 | 25/25 | 0 | 25 | 1.03 ± 0.25 (1.02) | 4.97 ± 3.73 (3.64) | 1.69 ± 0.38 (1.77) | 3.62 ± 0.85 (3.53) | 1.22 ± 0.49 (1.22) |
| left/left | p | 0.826 | 25/25 | 0 | 22 | 1.43 ± 0.34 (1.50) | 8.30 ± 4.81 (9.37) | 1.99 ± 0.31 (2.03) | 4.24 ± 0.70 (4.32) | 1.62 ± 0.44 (1.54) |
| left/right | p | 0.850 | 25/25 | 0 | 24 | 1.63 ± 0.32 (1.62) | 6.89 ± 4.44 (5.55) | 2.18 ± 0.27 (2.19) | 4.62 ± 0.65 (4.64) | 1.89 ± 0.44 (1.91) |
| back/left | p | 0.823 | 25/25 | 0 | 24 | 2.21 ± 0.25 (2.16) | 12.53 ± 31.13 (5.85) | 2.16 ± 0.47 (2.24) | 4.57 ± 1.07 (4.86) | 1.94 ± 0.58 (2.10) |
| back/right | p | 0.820 | 25/25 | 0 | 24 | 2.23 ± 0.27 (2.22) | 7.84 ± 3.66 (6.86) | 2.28 ± 0.34 (2.34) | 4.81 ± 0.80 (5.15) | 2.06 ± 0.55 (2.16) |
| right/left | p | 0.832 | 25/25 | 0 | 25 | 1.62 ± 0.29 (1.58) | 6.78 ± 4.50 (5.70) | 2.13 ± 0.30 (2.12) | 4.49 ± 0.69 (4.61) | 1.80 ± 0.42 (1.85) |
| right/right | p | 0.804 | 25/25 | 0 | 23 | 1.42 ± 0.34 (1.46) | 8.82 ± 3.88 (9.18) | 1.99 ± 0.35 (1.97) | 4.17 ± 0.73 (3.98) | 1.60 ± 0.46 (1.44) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.853 | 6.8 | 4.71 | 1.93 |
| p | normal | 0.803 | 8.7 | 3.83 | 1.41 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.758 | 0.17 | 2.18 ± 0.75 (1.99) | 3.45 | 1.18 |
| p | medium | 16 | 0.863 | 0.82 | 1.06 ± 0.20 (1.10) | 3.45 | 1.19 |
| p | strong | 126 | 0.856 | 0.63 | - | 4.75 | 1.96 |

## Notes

- p: score 0.828, 200/200 kicked, 0 fell; worst sector right (0.818).

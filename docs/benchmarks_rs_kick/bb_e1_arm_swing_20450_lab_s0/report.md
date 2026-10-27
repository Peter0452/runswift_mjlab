# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_00-03-35_e1_arm_swing/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.831** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 193 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.56 ± 0.52 (1.50) |
| Direction error [°] | 6.51 ± 4.05 (5.63) |
| Avg ball speed [m/s] | 1.87 ± 0.34 (1.93) |
| Peak ball speed [m/s] | 4.00 ± 0.79 (4.11) |
| Distance [m] | 1.48 ± 0.48 (1.46) |
| Path length [m] | 1.49 ± 0.48 (1.47) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.823 | 50/50 | 0 | 48 | 1.03 ± 0.21 (1.05) | 6.04 ± 4.33 (4.99) | 1.56 ± 0.36 (1.47) | 3.31 ± 0.76 (3.15) | 1.06 ± 0.44 (0.93) |
| left | p | 0.851 | 50/50 | 0 | 49 | 1.49 ± 0.34 (1.51) | 6.43 ± 4.09 (5.45) | 1.96 ± 0.26 (2.02) | 4.22 ± 0.66 (4.41) | 1.61 ± 0.40 (1.62) |
| back | p | 0.830 | 50/50 | 0 | 50 | 2.22 ± 0.26 (2.17) | 6.46 ± 2.68 (6.40) | 2.04 ± 0.23 (2.06) | 4.38 ± 0.61 (4.61) | 1.73 ± 0.40 (1.77) |
| right | p | 0.820 | 50/50 | 0 | 46 | 1.49 ± 0.34 (1.46) | 7.12 ± 4.73 (6.26) | 1.91 ± 0.27 (1.95) | 4.07 ± 0.64 (4.14) | 1.52 ± 0.37 (1.47) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.832 | 100/100 | 0 | 97 | 1.57 ± 0.52 (1.52) | 6.49 ± 3.85 (5.73) | 1.87 ± 0.34 (1.95) | 4.02 ± 0.78 (4.14) | 1.49 ± 0.48 (1.51) |
| right | p | 0.830 | 100/100 | 0 | 96 | 1.55 ± 0.52 (1.46) | 6.54 ± 4.24 (5.62) | 1.86 ± 0.34 (1.92) | 3.97 ± 0.79 (3.95) | 1.47 ± 0.48 (1.45) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.820 | 25/25 | 0 | 24 | 1.04 ± 0.21 (1.06) | 6.19 ± 4.07 (5.19) | 1.56 ± 0.35 (1.49) | 3.30 ± 0.75 (3.14) | 1.06 ± 0.46 (0.91) |
| forward/right | p | 0.826 | 25/25 | 0 | 24 | 1.02 ± 0.21 (1.02) | 5.89 ± 4.57 (4.96) | 1.56 ± 0.37 (1.45) | 3.32 ± 0.77 (3.19) | 1.07 ± 0.43 (0.93) |
| left/left | p | 0.845 | 25/25 | 0 | 24 | 1.40 ± 0.34 (1.50) | 6.95 ± 4.43 (6.45) | 1.92 ± 0.28 (2.00) | 4.14 ± 0.70 (4.24) | 1.54 ± 0.40 (1.59) |
| left/right | p | 0.857 | 25/25 | 0 | 25 | 1.58 ± 0.32 (1.56) | 5.91 ± 3.64 (5.30) | 2.00 ± 0.24 (2.08) | 4.31 ± 0.61 (4.54) | 1.68 ± 0.39 (1.70) |
| back/left | p | 0.832 | 25/25 | 0 | 25 | 2.23 ± 0.26 (2.16) | 6.24 ± 2.46 (5.82) | 2.04 ± 0.24 (2.06) | 4.39 ± 0.62 (4.60) | 1.74 ± 0.42 (1.71) |
| back/right | p | 0.827 | 25/25 | 0 | 25 | 2.21 ± 0.27 (2.22) | 6.68 ± 2.87 (6.88) | 2.04 ± 0.22 (2.06) | 4.37 ± 0.60 (4.64) | 1.73 ± 0.38 (1.77) |
| right/left | p | 0.830 | 25/25 | 0 | 24 | 1.59 ± 0.32 (1.56) | 6.57 ± 4.09 (5.64) | 1.98 ± 0.22 (1.97) | 4.23 ± 0.55 (4.30) | 1.61 ± 0.32 (1.63) |
| right/right | p | 0.811 | 25/25 | 0 | 22 | 1.40 ± 0.34 (1.44) | 7.66 ± 5.24 (6.80) | 1.84 ± 0.29 (1.76) | 3.91 ± 0.69 (3.68) | 1.42 ± 0.40 (1.31) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.848 | 6.3 | 4.29 | 1.64 |
| p | normal | 0.814 | 6.7 | 3.70 | 1.32 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.773 | 0.22 | 2.12 ± 0.70 (1.92) | 3.36 | 1.12 |
| p | medium | 16 | 0.888 | 0.85 | 1.04 ± 0.17 (1.07) | 3.38 | 1.15 |
| p | strong | 126 | 0.851 | 0.58 | - | 4.36 | 1.69 |

## Notes

- p: score 0.831, 200/200 kicked, 0 fell; worst sector right (0.820).

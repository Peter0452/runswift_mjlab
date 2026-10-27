# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_01-18-00_e3_drill_stand/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.848** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.57 ± 0.53 (1.47) |
| Direction error [°] | 5.08 ± 3.49 (4.37) |
| Avg ball speed [m/s] | 1.81 ± 0.38 (1.89) |
| Peak ball speed [m/s] | 3.92 ± 0.88 (3.97) |
| Distance [m] | 1.37 ± 0.50 (1.37) |
| Path length [m] | 1.37 ± 0.50 (1.37) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.844 | 50/50 | 0 | 50 | 1.04 ± 0.23 (1.06) | 4.63 ± 3.39 (3.32) | 1.50 ± 0.39 (1.48) | 3.20 ± 0.81 (3.10) | 0.96 ± 0.44 (0.98) |
| left | p | 0.862 | 50/50 | 0 | 50 | 1.50 ± 0.34 (1.49) | 5.49 ± 3.75 (4.42) | 1.88 ± 0.33 (1.94) | 4.12 ± 0.81 (4.33) | 1.47 ± 0.47 (1.48) |
| back | p | 0.846 | 50/50 | 0 | 50 | 2.25 ± 0.27 (2.21) | 4.59 ± 2.69 (4.78) | 2.04 ± 0.24 (2.13) | 4.40 ± 0.64 (4.69) | 1.66 ± 0.37 (1.77) |
| right | p | 0.841 | 50/50 | 0 | 50 | 1.49 ± 0.34 (1.44) | 5.60 ± 3.87 (4.72) | 1.83 ± 0.31 (1.90) | 3.95 ± 0.77 (4.02) | 1.38 ± 0.41 (1.37) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.846 | 100/100 | 0 | 100 | 1.58 ± 0.54 (1.47) | 5.03 ± 3.57 (4.29) | 1.81 ± 0.39 (1.93) | 3.92 ± 0.90 (4.06) | 1.37 ± 0.52 (1.39) |
| right | p | 0.851 | 100/100 | 0 | 100 | 1.57 ± 0.52 (1.47) | 5.12 ± 3.40 (4.78) | 1.81 ± 0.36 (1.87) | 3.92 ± 0.85 (3.89) | 1.37 ± 0.48 (1.36) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.840 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.08) | 4.29 ± 3.27 (2.81) | 1.46 ± 0.41 (1.48) | 3.14 ± 0.82 (3.10) | 0.92 ± 0.48 (0.97) |
| forward/right | p | 0.847 | 25/25 | 0 | 25 | 1.04 ± 0.23 (1.06) | 4.97 ± 3.48 (3.54) | 1.54 ± 0.36 (1.48) | 3.27 ± 0.79 (3.11) | 0.99 ± 0.41 (0.99) |
| left/left | p | 0.848 | 25/25 | 0 | 25 | 1.39 ± 0.33 (1.42) | 6.12 ± 4.35 (4.29) | 1.83 ± 0.32 (1.93) | 3.96 ± 0.79 (4.19) | 1.38 ± 0.44 (1.43) |
| left/right | p | 0.876 | 25/25 | 0 | 25 | 1.61 ± 0.31 (1.60) | 4.85 ± 2.89 (5.04) | 1.94 ± 0.33 (1.96) | 4.27 ± 0.79 (4.45) | 1.56 ± 0.48 (1.52) |
| back/left | p | 0.842 | 25/25 | 0 | 25 | 2.29 ± 0.27 (2.22) | 4.45 ± 2.63 (4.46) | 2.07 ± 0.22 (2.15) | 4.47 ± 0.60 (4.80) | 1.69 ± 0.37 (1.84) |
| back/right | p | 0.850 | 25/25 | 0 | 25 | 2.22 ± 0.26 (2.16) | 4.73 ± 2.73 (5.10) | 2.01 ± 0.25 (2.10) | 4.34 ± 0.67 (4.58) | 1.62 ± 0.38 (1.73) |
| right/left | p | 0.852 | 25/25 | 0 | 25 | 1.59 ± 0.31 (1.58) | 5.28 ± 3.51 (4.80) | 1.89 ± 0.33 (2.03) | 4.11 ± 0.82 (4.50) | 1.47 ± 0.44 (1.46) |
| right/right | p | 0.830 | 25/25 | 0 | 25 | 1.39 ± 0.34 (1.42) | 5.91 ± 4.18 (4.14) | 1.78 ± 0.29 (1.78) | 3.80 ± 0.68 (3.76) | 1.30 ± 0.36 (1.25) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.854 | 5.6 | 4.28 | 1.55 |
| p | normal | 0.843 | 4.5 | 3.56 | 1.18 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.809 | 0.28 | 1.98 ± 0.64 (1.81) | 3.16 | 0.97 |
| p | medium | 16 | 0.916 | 0.85 | 1.00 ± 0.20 (1.01) | 3.24 | 1.02 |
| p | strong | 126 | 0.858 | 0.58 | - | 4.35 | 1.59 |

## Notes

- p: score 0.848, 200/200 kicked, 0 fell; worst sector right (0.841).

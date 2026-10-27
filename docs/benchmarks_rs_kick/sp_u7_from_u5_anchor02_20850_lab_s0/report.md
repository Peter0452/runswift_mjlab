# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_11-31-02_u7_from_u5_anchor02/model_20850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.853** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.56 ± 0.50 (1.48) |
| Direction error [°] | 5.47 ± 11.33 (4.31) |
| Avg ball speed [m/s] | 1.93 ± 0.32 (1.97) |
| Peak ball speed [m/s] | 4.21 ± 0.79 (4.30) |
| Distance [m] | 1.59 ± 0.49 (1.59) |
| Path length [m] | 1.60 ± 0.49 (1.60) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.848 | 50/50 | 0 | 50 | 1.04 ± 0.22 (1.06) | 4.17 ± 3.02 (2.89) | 1.71 ± 0.27 (1.67) | 3.71 ± 0.65 (3.50) | 1.27 ± 0.39 (1.19) |
| left | p | 0.869 | 50/50 | 0 | 50 | 1.49 ± 0.33 (1.50) | 4.93 ± 2.79 (4.30) | 2.00 ± 0.27 (2.03) | 4.40 ± 0.69 (4.62) | 1.70 ± 0.45 (1.70) |
| back | p | 0.848 | 50/50 | 0 | 49 | 2.20 ± 0.24 (2.16) | 7.72 ± 21.82 (5.02) | 2.09 ± 0.35 (2.18) | 4.54 ± 0.85 (4.84) | 1.83 ± 0.51 (1.94) |
| right | p | 0.845 | 50/50 | 0 | 50 | 1.50 ± 0.34 (1.47) | 5.06 ± 3.59 (4.19) | 1.92 ± 0.26 (1.96) | 4.19 ± 0.68 (4.33) | 1.57 ± 0.40 (1.55) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.853 | 100/100 | 0 | 100 | 1.57 ± 0.52 (1.51) | 4.75 ± 2.89 (4.50) | 1.95 ± 0.30 (1.98) | 4.23 ± 0.74 (4.30) | 1.61 ± 0.48 (1.59) |
| right | p | 0.852 | 100/100 | 0 | 99 | 1.55 ± 0.49 (1.48) | 6.19 ± 15.72 (4.12) | 1.92 ± 0.34 (1.97) | 4.19 ± 0.83 (4.30) | 1.58 ± 0.49 (1.58) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.852 | 25/25 | 0 | 25 | 1.03 ± 0.22 (1.06) | 3.99 ± 3.07 (2.29) | 1.72 ± 0.27 (1.74) | 3.71 ± 0.64 (3.67) | 1.28 ± 0.42 (1.22) |
| forward/right | p | 0.844 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.06) | 4.34 ± 2.96 (3.30) | 1.71 ± 0.27 (1.65) | 3.71 ± 0.65 (3.50) | 1.26 ± 0.36 (1.17) |
| left/left | p | 0.863 | 25/25 | 0 | 25 | 1.39 ± 0.33 (1.48) | 5.08 ± 2.98 (4.41) | 1.95 ± 0.22 (2.00) | 4.27 ± 0.61 (4.43) | 1.62 ± 0.37 (1.63) |
| left/right | p | 0.876 | 25/25 | 0 | 25 | 1.59 ± 0.31 (1.60) | 4.78 ± 2.58 (4.12) | 2.04 ± 0.31 (2.10) | 4.52 ± 0.74 (4.78) | 1.78 ± 0.50 (1.83) |
| back/left | p | 0.846 | 25/25 | 0 | 25 | 2.24 ± 0.26 (2.16) | 4.98 ± 2.19 (5.30) | 2.17 ± 0.25 (2.19) | 4.68 ± 0.66 (4.84) | 1.93 ± 0.47 (2.02) |
| back/right | p | 0.851 | 25/25 | 0 | 24 | 2.16 ± 0.22 (2.16) | 10.47 ± 30.53 (4.76) | 2.02 ± 0.42 (2.12) | 4.39 ± 0.99 (4.77) | 1.73 ± 0.53 (1.80) |
| right/left | p | 0.852 | 25/25 | 0 | 25 | 1.60 ± 0.32 (1.56) | 4.95 ± 3.11 (4.58) | 1.95 ± 0.27 (2.02) | 4.26 ± 0.70 (4.42) | 1.60 ± 0.41 (1.59) |
| right/right | p | 0.839 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.42) | 5.18 ± 4.02 (3.86) | 1.90 ± 0.25 (1.92) | 4.11 ± 0.64 (4.27) | 1.53 ± 0.38 (1.46) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.872 | 4.9 | 4.66 | 1.84 |
| p | normal | 0.834 | 6.1 | 3.76 | 1.34 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.791 | 0.20 | 2.12 ± 0.71 (1.95) | 3.35 | 1.11 |
| p | medium | 16 | 0.918 | 0.86 | 1.11 ± 0.14 (1.12) | 3.59 | 1.25 |
| p | strong | 126 | 0.873 | 0.62 | - | 4.68 | 1.86 |

## Notes

- p: score 0.853, 200/200 kicked, 0 fell; worst sector right (0.845).

# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_11-31-02_u7_from_u5_anchor02/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.854** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.56 ± 0.53 (1.48) |
| Direction error [°] | 4.54 ± 3.02 (3.96) |
| Avg ball speed [m/s] | 1.94 ± 0.34 (2.00) |
| Peak ball speed [m/s] | 4.23 ± 0.86 (4.24) |
| Distance [m] | 1.61 ± 0.53 (1.59) |
| Path length [m] | 1.61 ± 0.53 (1.60) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.848 | 50/50 | 0 | 50 | 1.02 ± 0.24 (1.05) | 4.04 ± 2.82 (2.80) | 1.63 ± 0.32 (1.56) | 3.52 ± 0.74 (3.43) | 1.17 ± 0.46 (1.08) |
| left | p | 0.865 | 50/50 | 0 | 49 | 1.49 ± 0.33 (1.49) | 5.27 ± 3.19 (4.44) | 2.00 ± 0.33 (2.15) | 4.40 ± 0.85 (4.72) | 1.71 ± 0.52 (1.77) |
| back | p | 0.856 | 50/50 | 0 | 50 | 2.23 ± 0.27 (2.19) | 3.78 ± 2.41 (3.42) | 2.15 ± 0.23 (2.20) | 4.69 ± 0.69 (4.98) | 1.89 ± 0.44 (2.01) |
| right | p | 0.845 | 50/50 | 0 | 50 | 1.49 ± 0.34 (1.46) | 5.05 ± 3.29 (4.65) | 1.98 ± 0.25 (2.03) | 4.32 ± 0.69 (4.48) | 1.65 ± 0.39 (1.60) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.856 | 100/100 | 0 | 100 | 1.56 ± 0.53 (1.47) | 4.35 ± 2.85 (4.04) | 1.95 ± 0.35 (2.02) | 4.26 ± 0.90 (4.46) | 1.63 ± 0.56 (1.58) |
| right | p | 0.851 | 100/100 | 0 | 99 | 1.55 ± 0.52 (1.48) | 4.73 ± 3.16 (3.73) | 1.93 ± 0.33 (1.99) | 4.21 ± 0.83 (4.20) | 1.58 ± 0.49 (1.60) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.845 | 25/25 | 0 | 25 | 1.02 ± 0.25 (1.08) | 4.07 ± 2.48 (3.50) | 1.65 ± 0.33 (1.54) | 3.54 ± 0.76 (3.33) | 1.20 ± 0.50 (1.08) |
| forward/right | p | 0.850 | 25/25 | 0 | 25 | 1.01 ± 0.23 (1.02) | 4.01 ± 3.13 (2.69) | 1.62 ± 0.31 (1.62) | 3.49 ± 0.72 (3.45) | 1.15 ± 0.41 (1.09) |
| left/left | p | 0.861 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.44) | 5.17 ± 3.10 (4.55) | 1.93 ± 0.35 (2.02) | 4.22 ± 0.90 (4.59) | 1.60 ± 0.54 (1.68) |
| left/right | p | 0.869 | 25/25 | 0 | 24 | 1.58 ± 0.30 (1.60) | 5.37 ± 3.27 (4.21) | 2.07 ± 0.29 (2.16) | 4.58 ± 0.75 (4.89) | 1.82 ± 0.48 (1.90) |
| back/left | p | 0.862 | 25/25 | 0 | 25 | 2.25 ± 0.27 (2.18) | 3.35 ± 2.61 (2.93) | 2.21 ± 0.20 (2.23) | 4.84 ± 0.68 (5.12) | 2.00 ± 0.46 (2.12) |
| back/right | p | 0.850 | 25/25 | 0 | 25 | 2.21 ± 0.26 (2.20) | 4.21 ± 2.10 (4.19) | 2.08 ± 0.24 (2.12) | 4.54 ± 0.67 (4.75) | 1.78 ± 0.38 (1.78) |
| right/left | p | 0.854 | 25/25 | 0 | 25 | 1.57 ± 0.33 (1.54) | 4.79 ± 2.82 (4.37) | 2.02 ± 0.26 (2.07) | 4.43 ± 0.71 (4.63) | 1.71 ± 0.42 (1.70) |
| right/right | p | 0.836 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.44) | 5.31 ± 3.68 (5.28) | 1.95 ± 0.24 (1.93) | 4.21 ± 0.65 (4.04) | 1.58 ± 0.36 (1.56) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.874 | 4.5 | 4.63 | 1.82 |
| p | normal | 0.833 | 4.5 | 3.83 | 1.39 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.791 | 0.19 | 2.16 ± 0.69 (1.98) | 3.44 | 1.16 |
| p | medium | 16 | 0.898 | 0.81 | 1.09 ± 0.19 (1.14) | 3.52 | 1.22 |
| p | strong | 126 | 0.877 | 0.62 | - | 4.69 | 1.86 |

## Notes

- p: score 0.854, 200/200 kicked, 0 fell; worst sector right (0.845).

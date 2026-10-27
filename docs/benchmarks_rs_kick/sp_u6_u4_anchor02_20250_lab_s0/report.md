# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_10-50-14_u6_u4_anchor02/model_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.851** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.58 ± 0.52 (1.50) |
| Direction error [°] | 5.49 ± 12.47 (4.01) |
| Avg ball speed [m/s] | 1.69 ± 0.34 (1.75) |
| Peak ball speed [m/s] | 3.99 ± 0.81 (4.14) |
| Distance [m] | 1.41 ± 0.46 (1.41) |
| Path length [m] | 1.42 ± 0.46 (1.42) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.850 | 50/50 | 0 | 50 | 1.05 ± 0.23 (1.06) | 3.99 ± 2.91 (2.67) | 1.48 ± 0.34 (1.40) | 3.46 ± 0.78 (3.29) | 1.09 ± 0.42 (0.96) |
| left | p | 0.867 | 50/50 | 0 | 50 | 1.53 ± 0.34 (1.53) | 4.91 ± 3.19 (4.10) | 1.77 ± 0.31 (1.84) | 4.20 ± 0.72 (4.42) | 1.55 ± 0.45 (1.58) |
| back | p | 0.844 | 50/50 | 0 | 49 | 2.25 ± 0.24 (2.23) | 7.81 ± 24.21 (4.00) | 1.79 ± 0.34 (1.85) | 4.26 ± 0.82 (4.54) | 1.58 ± 0.43 (1.65) |
| right | p | 0.843 | 50/50 | 0 | 50 | 1.51 ± 0.34 (1.48) | 5.23 ± 2.92 (4.88) | 1.73 ± 0.28 (1.73) | 4.05 ± 0.66 (4.20) | 1.43 ± 0.37 (1.37) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.851 | 100/100 | 0 | 100 | 1.59 ± 0.53 (1.53) | 4.57 ± 2.72 (4.14) | 1.70 ± 0.30 (1.73) | 3.98 ± 0.73 (4.13) | 1.41 ± 0.43 (1.41) |
| right | p | 0.851 | 100/100 | 0 | 99 | 1.58 ± 0.51 (1.49) | 6.40 ± 17.37 (3.76) | 1.68 ± 0.37 (1.77) | 4.00 ± 0.88 (4.16) | 1.42 ± 0.49 (1.42) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.847 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.06) | 4.07 ± 2.51 (2.80) | 1.51 ± 0.34 (1.40) | 3.43 ± 0.71 (3.32) | 1.09 ± 0.41 (0.95) |
| forward/right | p | 0.852 | 25/25 | 0 | 25 | 1.05 ± 0.24 (1.04) | 3.91 ± 3.27 (2.66) | 1.44 ± 0.34 (1.39) | 3.49 ± 0.84 (3.26) | 1.09 ± 0.42 (0.96) |
| left/left | p | 0.854 | 25/25 | 0 | 25 | 1.42 ± 0.35 (1.48) | 5.45 ± 2.73 (4.94) | 1.69 ± 0.25 (1.68) | 4.02 ± 0.62 (4.17) | 1.44 ± 0.37 (1.39) |
| left/right | p | 0.881 | 25/25 | 0 | 25 | 1.63 ± 0.30 (1.62) | 4.37 ± 3.51 (3.23) | 1.84 ± 0.33 (2.01) | 4.38 ± 0.77 (4.60) | 1.67 ± 0.50 (1.80) |
| back/left | p | 0.852 | 25/25 | 0 | 25 | 2.28 ± 0.25 (2.26) | 3.82 ± 2.55 (3.46) | 1.86 ± 0.22 (1.88) | 4.36 ± 0.53 (4.58) | 1.63 ± 0.34 (1.70) |
| back/right | p | 0.837 | 25/25 | 0 | 24 | 2.22 ± 0.23 (2.18) | 11.80 ± 33.68 (4.63) | 1.73 ± 0.42 (1.80) | 4.16 ± 1.02 (4.53) | 1.53 ± 0.50 (1.65) |
| right/left | p | 0.850 | 25/25 | 0 | 25 | 1.61 ± 0.31 (1.58) | 4.95 ± 2.75 (4.81) | 1.73 ± 0.29 (1.73) | 4.12 ± 0.72 (4.36) | 1.47 ± 0.40 (1.58) |
| right/right | p | 0.835 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.46) | 5.52 ± 3.05 (4.94) | 1.72 ± 0.27 (1.72) | 3.97 ± 0.60 (4.03) | 1.40 ± 0.34 (1.35) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.862 | 5.1 | 4.40 | 1.64 |
| p | normal | 0.840 | 5.9 | 3.58 | 1.19 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.801 | 0.25 | 2.02 ± 0.71 (1.87) | 3.21 | 0.99 |
| p | medium | 16 | 0.924 | 0.85 | 1.04 ± 0.18 (1.07) | 3.37 | 1.07 |
| p | strong | 126 | 0.865 | 0.59 | - | 4.43 | 1.65 |

## Notes

- p: score 0.851, 200/200 kicked, 0 fell; worst sector right (0.843).

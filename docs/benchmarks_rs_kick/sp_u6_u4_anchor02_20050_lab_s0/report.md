# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_10-50-14_u6_u4_anchor02/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.850** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.58 ± 0.52 (1.48) |
| Direction error [°] | 4.79 ± 2.99 (4.24) |
| Avg ball speed [m/s] | 1.88 ± 0.33 (1.91) |
| Peak ball speed [m/s] | 4.07 ± 0.76 (4.11) |
| Distance [m] | 1.51 ± 0.46 (1.48) |
| Path length [m] | 1.51 ± 0.46 (1.49) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.847 | 50/50 | 0 | 50 | 1.04 ± 0.22 (1.07) | 4.45 ± 3.20 (3.88) | 1.60 ± 0.33 (1.57) | 3.45 ± 0.73 (3.34) | 1.12 ± 0.42 (1.08) |
| left | p | 0.863 | 50/50 | 0 | 50 | 1.52 ± 0.34 (1.54) | 4.83 ± 2.84 (5.05) | 1.96 ± 0.26 (1.92) | 4.26 ± 0.62 (4.31) | 1.62 ± 0.40 (1.54) |
| back | p | 0.850 | 50/50 | 0 | 50 | 2.24 ± 0.25 (2.22) | 4.30 ± 2.43 (4.03) | 2.07 ± 0.20 (2.11) | 4.48 ± 0.59 (4.66) | 1.76 ± 0.35 (1.82) |
| right | p | 0.840 | 50/50 | 0 | 50 | 1.50 ± 0.33 (1.48) | 5.58 ± 3.26 (4.41) | 1.90 ± 0.30 (1.90) | 4.11 ± 0.70 (4.13) | 1.52 ± 0.41 (1.45) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.848 | 100/100 | 0 | 100 | 1.58 ± 0.52 (1.52) | 5.00 ± 3.11 (4.77) | 1.90 ± 0.31 (1.91) | 4.10 ± 0.74 (4.12) | 1.52 ± 0.46 (1.48) |
| right | p | 0.852 | 100/100 | 0 | 100 | 1.57 ± 0.52 (1.48) | 4.58 ± 2.85 (3.82) | 1.87 ± 0.34 (1.91) | 4.05 ± 0.78 (4.09) | 1.49 ± 0.46 (1.48) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.841 | 25/25 | 0 | 25 | 1.05 ± 0.22 (1.06) | 4.75 ± 3.34 (3.71) | 1.63 ± 0.27 (1.58) | 3.50 ± 0.59 (3.36) | 1.15 ± 0.38 (1.09) |
| forward/right | p | 0.853 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.08) | 4.16 ± 3.02 (4.06) | 1.57 ± 0.38 (1.50) | 3.41 ± 0.84 (3.15) | 1.10 ± 0.46 (1.06) |
| left/left | p | 0.851 | 25/25 | 0 | 25 | 1.43 ± 0.34 (1.52) | 5.62 ± 3.12 (5.80) | 1.90 ± 0.22 (1.87) | 4.10 ± 0.56 (4.15) | 1.52 ± 0.35 (1.53) |
| left/right | p | 0.875 | 25/25 | 0 | 25 | 1.62 ± 0.31 (1.60) | 4.03 ± 2.25 (3.54) | 2.03 ± 0.29 (2.11) | 4.42 ± 0.64 (4.70) | 1.72 ± 0.43 (1.76) |
| back/left | p | 0.851 | 25/25 | 0 | 25 | 2.25 ± 0.25 (2.20) | 4.39 ± 2.63 (4.97) | 2.07 ± 0.19 (2.12) | 4.50 ± 0.60 (4.76) | 1.78 ± 0.37 (1.88) |
| back/right | p | 0.849 | 25/25 | 0 | 25 | 2.23 ± 0.25 (2.24) | 4.21 ± 2.21 (3.66) | 2.06 ± 0.21 (2.10) | 4.45 ± 0.57 (4.62) | 1.74 ± 0.32 (1.80) |
| right/left | p | 0.851 | 25/25 | 0 | 25 | 1.59 ± 0.30 (1.58) | 5.24 ± 3.15 (4.25) | 1.99 ± 0.34 (2.04) | 4.29 ± 0.79 (4.59) | 1.64 ± 0.47 (1.72) |
| right/right | p | 0.828 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.44) | 5.92 ± 3.33 (5.90) | 1.82 ± 0.22 (1.85) | 3.93 ± 0.54 (3.91) | 1.41 ± 0.28 (1.36) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.865 | 4.8 | 4.42 | 1.70 |
| p | normal | 0.835 | 4.7 | 3.73 | 1.32 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.793 | 0.22 | 2.11 ± 0.67 (1.98) | 3.37 | 1.12 |
| p | medium | 16 | 0.925 | 0.88 | 1.09 ± 0.13 (1.06) | 3.54 | 1.21 |
| p | strong | 126 | 0.867 | 0.60 | - | 4.47 | 1.73 |

## Notes

- p: score 0.850, 200/200 kicked, 0 fell; worst sector right (0.840).

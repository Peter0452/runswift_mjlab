# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_08-10-04_u1_goal_overrun1/model_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.824** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 182 |
| Weak kicks (< 0.3 m) | 7 |
| Time to kick [s] | 1.63 ± 0.50 (1.60) |
| Direction error [°] | 8.69 ± 12.83 (7.62) |
| Avg ball speed [m/s] | 1.70 ± 0.47 (1.74) |
| Peak ball speed [m/s] | 3.60 ± 1.01 (3.66) |
| Distance [m] | 1.28 ± 0.58 (1.26) |
| Path length [m] | 1.28 ± 0.58 (1.27) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.840 | 50/50 | 0 | 49 | 1.13 ± 0.24 (1.17) | 6.43 ± 5.32 (5.01) | 1.38 ± 0.47 (1.31) | 2.95 ± 0.96 (2.82) | 0.88 ± 0.50 (0.79) |
| left | p | 0.827 | 50/50 | 0 | 45 | 1.58 ± 0.35 (1.62) | 8.87 ± 4.81 (8.92) | 1.86 ± 0.39 (1.89) | 3.92 ± 0.84 (4.00) | 1.46 ± 0.52 (1.45) |
| back | p | 0.809 | 50/50 | 0 | 45 | 2.22 ± 0.28 (2.18) | 11.21 ± 23.72 (8.09) | 1.85 ± 0.46 (1.89) | 3.92 ± 1.03 (4.10) | 1.50 ± 0.54 (1.63) |
| right | p | 0.818 | 50/50 | 0 | 43 | 1.58 ± 0.34 (1.56) | 8.26 ± 5.74 (7.29) | 1.71 ± 0.40 (1.70) | 3.60 ± 0.89 (3.56) | 1.27 ± 0.52 (1.20) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.819 | 100/100 | 0 | 93 | 1.62 ± 0.49 (1.60) | 9.39 ± 17.24 (7.23) | 1.71 ± 0.49 (1.75) | 3.63 ± 1.06 (3.72) | 1.30 ± 0.60 (1.30) |
| right | p | 0.828 | 100/100 | 0 | 89 | 1.63 ± 0.50 (1.56) | 7.99 ± 5.58 (7.62) | 1.69 ± 0.46 (1.73) | 3.56 ± 0.96 (3.64) | 1.25 ± 0.56 (1.23) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.834 | 25/25 | 0 | 25 | 1.12 ± 0.23 (1.18) | 6.33 ± 3.87 (5.05) | 1.35 ± 0.44 (1.34) | 2.92 ± 0.90 (2.92) | 0.85 ± 0.48 (0.83) |
| forward/right | p | 0.846 | 25/25 | 0 | 24 | 1.13 ± 0.26 (1.16) | 6.53 ± 6.45 (4.96) | 1.40 ± 0.50 (1.21) | 2.98 ± 1.03 (2.62) | 0.90 ± 0.52 (0.70) |
| left/left | p | 0.815 | 25/25 | 0 | 23 | 1.48 ± 0.35 (1.54) | 9.53 ± 4.76 (10.97) | 1.83 ± 0.38 (1.94) | 3.84 ± 0.82 (4.02) | 1.40 ± 0.48 (1.43) |
| left/right | p | 0.839 | 25/25 | 0 | 22 | 1.68 ± 0.33 (1.74) | 8.21 ± 4.77 (8.80) | 1.89 ± 0.39 (1.87) | 3.99 ± 0.85 (3.98) | 1.51 ± 0.54 (1.46) |
| back/left | p | 0.800 | 25/25 | 0 | 22 | 2.21 ± 0.28 (2.14) | 14.42 ± 32.93 (7.70) | 1.81 ± 0.57 (1.84) | 3.88 ± 1.25 (4.09) | 1.52 ± 0.64 (1.60) |
| back/right | p | 0.818 | 25/25 | 0 | 23 | 2.23 ± 0.29 (2.26) | 7.99 ± 4.52 (8.13) | 1.89 ± 0.32 (1.91) | 3.96 ± 0.74 (4.10) | 1.49 ± 0.43 (1.66) |
| right/left | p | 0.829 | 25/25 | 0 | 23 | 1.68 ± 0.32 (1.66) | 7.29 ± 5.28 (6.49) | 1.84 ± 0.38 (1.85) | 3.90 ± 0.87 (4.06) | 1.44 ± 0.52 (1.50) |
| right/right | p | 0.807 | 25/25 | 0 | 20 | 1.49 ± 0.34 (1.48) | 9.23 ± 6.02 (7.61) | 1.58 ± 0.39 (1.53) | 3.30 ± 0.80 (3.18) | 1.10 ± 0.47 (1.03) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.823 | 8.1 | 4.08 | 1.54 |
| p | normal | 0.824 | 9.3 | 3.12 | 1.02 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.806 | 0.42 | 1.66 ± 0.72 (1.48) | 2.61 | 0.74 |
| p | medium | 16 | 0.889 | 0.83 | 0.87 ± 0.17 (0.89) | 2.84 | 0.83 |
| p | strong | 126 | 0.823 | 0.55 | - | 4.15 | 1.58 |

## Notes

- p: score 0.824, 200/200 kicked, 0 fell; worst sector back (0.809).

# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_05-06-31_u4c_u4b_lowcap03/model_20950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.852** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.82 ± 0.57 (1.66) |
| Direction error [°] | 6.01 ± 9.98 (5.13) |
| Avg ball speed [m/s] | 2.66 ± 0.48 (2.72) |
| Peak ball speed [m/s] | 5.47 ± 1.10 (5.86) |
| Distance [m] | 2.61 ± 0.80 (2.84) |
| Path length [m] | 2.62 ± 0.80 (2.85) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.875 | 50/50 | 0 | 50 | 1.28 ± 0.25 (1.31) | 4.61 ± 3.52 (3.92) | 2.52 ± 0.45 (2.49) | 5.27 ± 1.07 (5.50) | 2.43 ± 0.75 (2.54) |
| left | p | 0.870 | 50/50 | 0 | 49 | 1.72 ± 0.35 (1.61) | 4.89 ± 3.49 (5.06) | 2.67 ± 0.40 (2.69) | 5.50 ± 0.95 (5.89) | 2.60 ± 0.73 (2.79) |
| back | p | 0.811 | 50/50 | 0 | 47 | 2.54 ± 0.41 (2.47) | 9.02 ± 18.54 (6.56) | 2.79 ± 0.56 (2.91) | 5.67 ± 1.19 (6.24) | 2.82 ± 0.81 (3.22) |
| right | p | 0.854 | 50/50 | 0 | 49 | 1.73 ± 0.35 (1.71) | 5.51 ± 4.24 (5.19) | 2.67 ± 0.47 (2.76) | 5.44 ± 1.13 (5.98) | 2.60 ± 0.85 (2.91) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.853 | 100/100 | 0 | 100 | 1.82 ± 0.57 (1.66) | 5.03 ± 3.49 (5.06) | 2.66 ± 0.45 (2.72) | 5.47 ± 1.00 (5.85) | 2.61 ± 0.75 (2.83) |
| right | p | 0.852 | 100/100 | 0 | 95 | 1.81 ± 0.58 (1.68) | 6.99 ± 13.61 (5.31) | 2.66 ± 0.52 (2.73) | 5.48 ± 1.18 (5.92) | 2.62 ± 0.84 (2.86) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.867 | 25/25 | 0 | 25 | 1.27 ± 0.25 (1.30) | 4.55 ± 3.64 (4.06) | 2.46 ± 0.39 (2.43) | 5.12 ± 0.93 (5.36) | 2.32 ± 0.63 (2.52) |
| forward/right | p | 0.883 | 25/25 | 0 | 25 | 1.29 ± 0.24 (1.34) | 4.68 ± 3.40 (3.57) | 2.58 ± 0.50 (2.69) | 5.43 ± 1.18 (5.84) | 2.54 ± 0.84 (2.76) |
| left/left | p | 0.868 | 25/25 | 0 | 25 | 1.63 ± 0.32 (1.58) | 5.50 ± 3.47 (5.64) | 2.71 ± 0.41 (2.77) | 5.56 ± 0.92 (5.96) | 2.68 ± 0.72 (2.97) |
| left/right | p | 0.872 | 25/25 | 0 | 24 | 1.80 ± 0.35 (1.82) | 4.29 ± 3.40 (4.16) | 2.62 ± 0.38 (2.56) | 5.44 ± 0.97 (5.75) | 2.53 ± 0.73 (2.53) |
| back/left | p | 0.820 | 25/25 | 0 | 25 | 2.55 ± 0.34 (2.46) | 5.76 ± 3.31 (5.47) | 2.85 ± 0.45 (3.01) | 5.76 ± 0.96 (6.25) | 2.86 ± 0.76 (3.24) |
| back/right | p | 0.802 | 25/25 | 0 | 22 | 2.53 ± 0.47 (2.48) | 12.28 ± 25.60 (7.37) | 2.72 ± 0.64 (2.90) | 5.59 ± 1.38 (6.23) | 2.78 ± 0.86 (3.08) |
| right/left | p | 0.857 | 25/25 | 0 | 25 | 1.84 ± 0.36 (1.80) | 4.31 ± 3.32 (2.52) | 2.62 ± 0.44 (2.73) | 5.42 ± 1.09 (5.91) | 2.56 ± 0.80 (2.91) |
| right/right | p | 0.851 | 25/25 | 0 | 24 | 1.63 ± 0.31 (1.58) | 6.72 ± 4.70 (6.22) | 2.71 ± 0.50 (2.79) | 5.45 ± 1.16 (6.06) | 2.64 ± 0.90 (3.04) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.885 | 6.5 | 6.20 | 3.13 |
| p | normal | 0.820 | 5.5 | 4.74 | 2.10 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.762 | 0.07 | 2.64 ± 0.92 (2.49) | 4.09 | 1.62 |
| p | medium | 20 | 0.867 | 0.61 | 1.39 ± 0.18 (1.39) | 4.47 | 1.86 |
| p | strong | 126 | 0.889 | 0.83 | - | 6.22 | 3.16 |

## Notes

- p: score 0.852, 200/200 kicked, 0 fell; worst sector back (0.811).

# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_05-06-31_u4c_u4b_lowcap03/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.851** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.55 ± 0.51 (1.46) |
| Direction error [°] | 6.71 ± 10.89 (5.31) |
| Avg ball speed [m/s] | 1.72 ± 0.48 (1.88) |
| Peak ball speed [m/s] | 3.83 ± 1.12 (4.18) |
| Distance [m] | 1.31 ± 0.61 (1.45) |
| Path length [m] | 1.31 ± 0.61 (1.47) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.852 | 50/50 | 0 | 50 | 1.04 ± 0.22 (1.06) | 5.47 ± 3.78 (4.74) | 1.45 ± 0.51 (1.45) | 3.22 ± 1.06 (3.00) | 0.95 ± 0.58 (0.83) |
| left | p | 0.863 | 50/50 | 0 | 50 | 1.48 ± 0.35 (1.47) | 6.01 ± 3.66 (4.82) | 1.83 ± 0.42 (2.00) | 4.09 ± 0.99 (4.50) | 1.44 ± 0.55 (1.55) |
| back | p | 0.836 | 50/50 | 0 | 49 | 2.20 ± 0.27 (2.17) | 9.42 ± 20.46 (6.37) | 1.89 ± 0.43 (2.08) | 4.20 ± 1.09 (4.71) | 1.55 ± 0.57 (1.78) |
| right | p | 0.854 | 50/50 | 0 | 47 | 1.47 ± 0.33 (1.43) | 5.91 ± 4.30 (5.16) | 1.72 ± 0.45 (1.95) | 3.81 ± 1.08 (4.30) | 1.29 ± 0.57 (1.46) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.848 | 100/100 | 0 | 98 | 1.54 ± 0.51 (1.46) | 7.39 ± 14.95 (5.16) | 1.73 ± 0.49 (1.98) | 3.84 ± 1.12 (4.38) | 1.32 ± 0.61 (1.49) |
| right | p | 0.854 | 100/100 | 0 | 98 | 1.55 ± 0.51 (1.45) | 6.02 ± 3.59 (5.44) | 1.72 ± 0.48 (1.84) | 3.82 ± 1.13 (4.14) | 1.30 ± 0.61 (1.38) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.858 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.08) | 5.38 ± 3.96 (3.49) | 1.51 ± 0.54 (1.52) | 3.36 ± 1.11 (3.22) | 1.04 ± 0.64 (0.91) |
| forward/right | p | 0.845 | 25/25 | 0 | 25 | 1.04 ± 0.23 (1.06) | 5.57 ± 3.59 (5.30) | 1.39 ± 0.46 (1.27) | 3.08 ± 0.99 (2.74) | 0.86 ± 0.50 (0.72) |
| left/left | p | 0.850 | 25/25 | 0 | 25 | 1.37 ± 0.33 (1.42) | 6.59 ± 3.99 (4.86) | 1.71 ± 0.43 (1.86) | 3.81 ± 0.97 (4.22) | 1.28 ± 0.53 (1.47) |
| left/right | p | 0.876 | 25/25 | 0 | 25 | 1.59 ± 0.33 (1.58) | 5.43 ± 3.20 (4.62) | 1.95 ± 0.38 (2.13) | 4.37 ± 0.93 (4.88) | 1.60 ± 0.53 (1.78) |
| back/left | p | 0.827 | 25/25 | 0 | 24 | 2.20 ± 0.28 (2.16) | 12.04 ± 28.57 (6.12) | 1.90 ± 0.46 (2.09) | 4.21 ± 1.16 (4.72) | 1.58 ± 0.58 (1.80) |
| back/right | p | 0.845 | 25/25 | 0 | 25 | 2.21 ± 0.26 (2.18) | 6.81 ± 2.63 (6.48) | 1.89 ± 0.39 (2.07) | 4.18 ± 1.01 (4.58) | 1.52 ± 0.56 (1.68) |
| right/left | p | 0.858 | 25/25 | 0 | 24 | 1.56 ± 0.32 (1.54) | 5.56 ± 4.04 (5.17) | 1.78 ± 0.44 (2.01) | 3.96 ± 1.04 (4.53) | 1.37 ± 0.54 (1.62) |
| right/right | p | 0.849 | 25/25 | 0 | 23 | 1.38 ± 0.33 (1.42) | 6.26 ± 4.51 (4.82) | 1.67 ± 0.46 (1.83) | 3.65 ± 1.10 (4.03) | 1.21 ± 0.58 (1.39) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.858 | 5.9 | 4.54 | 1.68 |
| p | normal | 0.844 | 7.5 | 3.12 | 0.94 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.824 | 0.44 | 1.62 ± 0.61 (1.52) | 2.55 | 0.64 |
| p | medium | 16 | 0.889 | 0.83 | 0.84 ± 0.18 (0.89) | 2.72 | 0.72 |
| p | strong | 126 | 0.859 | 0.61 | - | 4.56 | 1.69 |

## Notes

- p: score 0.851, 200/200 kicked, 0 fell; worst sector back (0.836).

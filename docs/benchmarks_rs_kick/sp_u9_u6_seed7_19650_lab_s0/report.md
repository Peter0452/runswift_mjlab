# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_13-42-50_u9_u6_seed7/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.843** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.56 ± 0.53 (1.51) |
| Direction error [°] | 6.56 ± 12.27 (5.60) |
| Avg ball speed [m/s] | 1.82 ± 0.37 (1.95) |
| Peak ball speed [m/s] | 3.94 ± 0.90 (4.14) |
| Distance [m] | 1.37 ± 0.49 (1.39) |
| Path length [m] | 1.38 ± 0.49 (1.39) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.858 | 50/50 | 0 | 50 | 1.01 ± 0.25 (1.05) | 3.86 ± 2.98 (2.63) | 1.60 ± 0.38 (1.58) | 3.39 ± 0.84 (3.25) | 1.07 ± 0.43 (1.06) |
| left | p | 0.855 | 50/50 | 0 | 49 | 1.50 ± 0.34 (1.51) | 6.19 ± 3.79 (6.29) | 1.87 ± 0.33 (2.01) | 4.11 ± 0.81 (4.44) | 1.45 ± 0.46 (1.58) |
| back | p | 0.817 | 50/50 | 0 | 49 | 2.24 ± 0.27 (2.23) | 10.58 ± 23.33 (7.68) | 1.96 ± 0.36 (2.11) | 4.26 ± 0.88 (4.62) | 1.59 ± 0.48 (1.83) |
| right | p | 0.844 | 50/50 | 0 | 50 | 1.50 ± 0.33 (1.50) | 5.59 ± 3.21 (5.13) | 1.84 ± 0.32 (1.97) | 3.98 ± 0.81 (4.39) | 1.38 ± 0.44 (1.40) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.843 | 100/100 | 0 | 99 | 1.56 ± 0.54 (1.51) | 5.82 ± 3.54 (5.60) | 1.85 ± 0.34 (1.96) | 4.00 ± 0.84 (4.31) | 1.41 ± 0.47 (1.43) |
| right | p | 0.844 | 100/100 | 0 | 99 | 1.57 ± 0.52 (1.51) | 7.29 ± 16.96 (5.54) | 1.78 ± 0.40 (1.91) | 3.87 ± 0.95 (4.06) | 1.34 ± 0.50 (1.34) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.856 | 25/25 | 0 | 25 | 1.02 ± 0.25 (1.08) | 4.13 ± 2.89 (2.96) | 1.65 ± 0.36 (1.64) | 3.50 ± 0.77 (3.27) | 1.13 ± 0.41 (1.11) |
| forward/right | p | 0.860 | 25/25 | 0 | 25 | 1.01 ± 0.24 (1.04) | 3.59 ± 3.04 (2.28) | 1.54 ± 0.40 (1.48) | 3.29 ± 0.89 (3.18) | 1.00 ± 0.44 (0.87) |
| left/left | p | 0.837 | 25/25 | 0 | 24 | 1.39 ± 0.34 (1.42) | 6.99 ± 4.04 (7.47) | 1.80 ± 0.31 (1.89) | 3.89 ± 0.76 (4.01) | 1.34 ± 0.43 (1.27) |
| left/right | p | 0.873 | 25/25 | 0 | 25 | 1.61 ± 0.30 (1.58) | 5.39 ± 3.34 (5.46) | 1.95 ± 0.34 (2.09) | 4.32 ± 0.80 (4.65) | 1.56 ± 0.45 (1.67) |
| back/left | p | 0.817 | 25/25 | 0 | 25 | 2.26 ± 0.28 (2.26) | 7.53 ± 3.42 (8.49) | 2.04 ± 0.22 (2.16) | 4.45 ± 0.65 (4.77) | 1.69 ± 0.40 (1.93) |
| back/right | p | 0.817 | 25/25 | 0 | 24 | 2.22 ± 0.25 (2.16) | 13.63 ± 32.53 (7.52) | 1.88 ± 0.44 (2.06) | 4.07 ± 1.03 (4.52) | 1.49 ± 0.52 (1.72) |
| right/left | p | 0.860 | 25/25 | 0 | 25 | 1.59 ± 0.30 (1.56) | 4.62 ± 2.30 (4.13) | 1.90 ± 0.33 (2.03) | 4.15 ± 0.84 (4.55) | 1.47 ± 0.46 (1.47) |
| right/right | p | 0.827 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.44) | 6.56 ± 3.67 (6.05) | 1.78 ± 0.30 (1.80) | 3.81 ± 0.73 (3.62) | 1.30 ± 0.39 (1.32) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.851 | 6.1 | 4.39 | 1.60 |
| p | normal | 0.836 | 7.1 | 3.48 | 1.14 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.806 | 0.30 | 1.90 ± 0.66 (1.75) | 3.02 | 0.90 |
| p | medium | 16 | 0.903 | 0.84 | 0.97 ± 0.19 (0.99) | 3.14 | 0.97 |
| p | strong | 126 | 0.853 | 0.59 | - | 4.46 | 1.64 |

## Notes

- p: score 0.843, 200/200 kicked, 0 fell; worst sector back (0.817).

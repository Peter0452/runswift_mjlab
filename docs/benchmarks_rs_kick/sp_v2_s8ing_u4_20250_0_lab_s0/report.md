# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/v2_s8ing_u4_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.855** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.58 ± 0.53 (1.50) |
| Direction error [°] | 4.92 ± 3.16 (4.35) |
| Avg ball speed [m/s] | 1.91 ± 0.36 (2.00) |
| Peak ball speed [m/s] | 4.21 ± 0.89 (4.49) |
| Distance [m] | 1.58 ± 0.53 (1.64) |
| Path length [m] | 1.59 ± 0.53 (1.65) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.851 | 50/50 | 0 | 50 | 1.04 ± 0.23 (1.08) | 4.60 ± 3.18 (3.98) | 1.67 ± 0.39 (1.63) | 3.64 ± 0.88 (3.40) | 1.23 ± 0.50 (1.04) |
| left | p | 0.870 | 50/50 | 0 | 50 | 1.51 ± 0.34 (1.50) | 5.14 ± 3.22 (4.55) | 2.00 ± 0.31 (2.09) | 4.43 ± 0.78 (4.75) | 1.72 ± 0.47 (1.82) |
| back | p | 0.850 | 50/50 | 0 | 50 | 2.25 ± 0.27 (2.22) | 4.75 ± 2.46 (4.71) | 2.06 ± 0.27 (2.20) | 4.55 ± 0.76 (4.90) | 1.80 ± 0.47 (1.96) |
| right | p | 0.849 | 50/50 | 0 | 50 | 1.51 ± 0.34 (1.49) | 5.19 ± 3.62 (4.61) | 1.91 ± 0.33 (1.99) | 4.20 ± 0.85 (4.51) | 1.57 ± 0.48 (1.58) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.856 | 100/100 | 0 | 100 | 1.58 ± 0.53 (1.52) | 4.95 ± 3.03 (4.40) | 1.93 ± 0.34 (2.00) | 4.22 ± 0.86 (4.49) | 1.59 ± 0.52 (1.64) |
| right | p | 0.854 | 100/100 | 0 | 100 | 1.58 ± 0.53 (1.48) | 4.89 ± 3.28 (4.29) | 1.90 ± 0.38 (2.01) | 4.19 ± 0.91 (4.49) | 1.57 ± 0.53 (1.64) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.848 | 25/25 | 0 | 25 | 1.04 ± 0.23 (1.08) | 4.79 ± 3.07 (3.87) | 1.68 ± 0.32 (1.73) | 3.64 ± 0.74 (3.46) | 1.23 ± 0.43 (1.04) |
| forward/right | p | 0.854 | 25/25 | 0 | 25 | 1.04 ± 0.24 (1.06) | 4.42 ± 3.27 (4.10) | 1.67 ± 0.46 (1.58) | 3.65 ± 1.01 (3.35) | 1.24 ± 0.56 (1.04) |
| left/left | p | 0.864 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.46) | 5.37 ± 3.46 (5.27) | 1.95 ± 0.32 (2.03) | 4.28 ± 0.79 (4.51) | 1.63 ± 0.47 (1.72) |
| left/right | p | 0.876 | 25/25 | 0 | 25 | 1.62 ± 0.31 (1.62) | 4.91 ± 2.95 (4.26) | 2.06 ± 0.29 (2.18) | 4.57 ± 0.73 (4.87) | 1.81 ± 0.46 (1.91) |
| back/left | p | 0.853 | 25/25 | 0 | 25 | 2.27 ± 0.26 (2.20) | 4.45 ± 2.44 (4.11) | 2.10 ± 0.25 (2.21) | 4.64 ± 0.73 (4.93) | 1.86 ± 0.48 (2.04) |
| back/right | p | 0.846 | 25/25 | 0 | 25 | 2.24 ± 0.28 (2.24) | 5.04 ± 2.44 (5.24) | 2.03 ± 0.29 (2.18) | 4.47 ± 0.77 (4.87) | 1.74 ± 0.46 (1.85) |
| right/left | p | 0.857 | 25/25 | 0 | 25 | 1.61 ± 0.31 (1.58) | 5.18 ± 2.97 (5.22) | 1.97 ± 0.33 (2.04) | 4.35 ± 0.85 (4.64) | 1.66 ± 0.49 (1.83) |
| right/right | p | 0.842 | 25/25 | 0 | 25 | 1.41 ± 0.35 (1.42) | 5.20 ± 4.18 (3.75) | 1.85 ± 0.32 (1.92) | 4.05 ± 0.81 (4.25) | 1.49 ± 0.46 (1.54) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.875 | 4.7 | 4.74 | 1.88 |
| p | normal | 0.836 | 5.1 | 3.67 | 1.28 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.793 | 0.26 | 2.02 ± 0.65 (1.82) | 3.21 | 1.02 |
| p | medium | 16 | 0.913 | 0.85 | 1.03 ± 0.17 (1.06) | 3.35 | 1.10 |
| p | strong | 126 | 0.876 | 0.64 | - | 4.77 | 1.90 |

## Notes

- p: score 0.855, 200/200 kicked, 0 fell; worst sector right (0.849).

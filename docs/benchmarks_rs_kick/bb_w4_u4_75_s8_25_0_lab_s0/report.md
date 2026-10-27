# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w4_u4_75_s8_25.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.864** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 9 |
| Time to kick [s] | 1.61 ± 0.53 (1.53) |
| Direction error [°] | 5.43 ± 3.51 (4.83) |
| Avg ball speed [m/s] | 1.82 ± 0.53 (2.04) |
| Peak ball speed [m/s] | 3.99 ± 1.21 (4.48) |
| Distance [m] | 1.43 ± 0.67 (1.63) |
| Path length [m] | 1.43 ± 0.68 (1.63) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.864 | 50/50 | 0 | 49 | 1.05 ± 0.23 (1.08) | 5.37 ± 3.98 (4.25) | 1.53 ± 0.60 (1.71) | 3.33 ± 1.21 (3.59) | 1.04 ± 0.63 (1.25) |
| left | p | 0.885 | 50/50 | 0 | 50 | 1.56 ± 0.36 (1.58) | 4.66 ± 3.11 (4.10) | 1.96 ± 0.45 (2.17) | 4.32 ± 1.08 (4.83) | 1.60 ± 0.61 (1.81) |
| back | p | 0.846 | 50/50 | 0 | 50 | 2.27 ± 0.25 (2.27) | 6.17 ± 2.78 (6.02) | 2.00 ± 0.43 (2.21) | 4.39 ± 1.07 (4.95) | 1.69 ± 0.64 (2.00) |
| right | p | 0.860 | 50/50 | 0 | 50 | 1.56 ± 0.35 (1.51) | 5.51 ± 3.84 (4.50) | 1.79 ± 0.49 (2.07) | 3.90 ± 1.15 (4.56) | 1.37 ± 0.62 (1.65) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.862 | 100/100 | 0 | 100 | 1.61 ± 0.54 (1.55) | 5.40 ± 3.48 (4.75) | 1.84 ± 0.52 (2.06) | 4.01 ± 1.18 (4.48) | 1.45 ± 0.67 (1.63) |
| right | p | 0.865 | 100/100 | 0 | 99 | 1.61 ± 0.52 (1.53) | 5.46 ± 3.53 (4.91) | 1.80 ± 0.55 (2.01) | 3.96 ± 1.23 (4.49) | 1.41 ± 0.68 (1.54) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.860 | 25/25 | 0 | 25 | 1.05 ± 0.23 (1.08) | 5.83 ± 4.07 (4.94) | 1.58 ± 0.56 (1.92) | 3.40 ± 1.13 (4.09) | 1.09 ± 0.61 (1.37) |
| forward/right | p | 0.867 | 25/25 | 0 | 24 | 1.06 ± 0.24 (1.08) | 4.92 ± 3.84 (4.10) | 1.47 ± 0.62 (1.62) | 3.26 ± 1.29 (3.36) | 0.99 ± 0.66 (0.93) |
| left/left | p | 0.877 | 25/25 | 0 | 25 | 1.45 ± 0.35 (1.52) | 5.19 ± 3.35 (4.72) | 1.88 ± 0.47 (2.14) | 4.12 ± 1.11 (4.72) | 1.49 ± 0.61 (1.67) |
| left/right | p | 0.893 | 25/25 | 0 | 25 | 1.67 ± 0.33 (1.70) | 4.12 ± 2.75 (3.49) | 2.05 ± 0.42 (2.21) | 4.52 ± 1.00 (4.98) | 1.72 ± 0.57 (1.85) |
| back/left | p | 0.845 | 25/25 | 0 | 25 | 2.29 ± 0.26 (2.20) | 5.69 ± 3.03 (5.90) | 2.04 ± 0.40 (2.24) | 4.45 ± 1.01 (5.00) | 1.73 ± 0.63 (2.02) |
| back/right | p | 0.848 | 25/25 | 0 | 25 | 2.25 ± 0.24 (2.28) | 6.65 ± 2.42 (6.60) | 1.97 ± 0.46 (2.18) | 4.33 ± 1.12 (4.92) | 1.64 ± 0.65 (1.86) |
| right/left | p | 0.868 | 25/25 | 0 | 25 | 1.65 ± 0.33 (1.60) | 4.88 ± 3.31 (4.45) | 1.86 ± 0.51 (2.19) | 4.07 ± 1.19 (4.77) | 1.47 ± 0.66 (1.74) |
| right/right | p | 0.853 | 25/25 | 0 | 25 | 1.47 ± 0.34 (1.48) | 6.15 ± 4.22 (4.77) | 1.72 ± 0.46 (1.95) | 3.73 ± 1.08 (4.29) | 1.28 ± 0.57 (1.38) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.868 | 5.6 | 4.81 | 1.87 |
| p | normal | 0.860 | 5.3 | 3.16 | 0.98 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.843 | 0.50 | 1.58 ± 0.61 (1.44) | 2.52 | 0.63 |
| p | medium | 16 | 0.896 | 0.78 | 0.82 ± 0.19 (0.82) | 2.65 | 0.71 |
| p | strong | 126 | 0.869 | 0.64 | - | 4.83 | 1.89 |

## Notes

- p: score 0.864, 200/200 kicked, 0 fell; worst sector back (0.846).

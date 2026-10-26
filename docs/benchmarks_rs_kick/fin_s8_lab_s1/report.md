# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.850** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.56 ± 0.54 (1.47) |
| Direction error [°] | 5.59 ± 3.56 (5.25) |
| Avg ball speed [m/s] | 2.17 ± 0.39 (2.18) |
| Peak ball speed [m/s] | 4.63 ± 0.89 (4.78) |
| Distance [m] | 2.01 ± 0.61 (2.04) |
| Path length [m] | 2.02 ± 0.61 (2.06) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.844 | 50/50 | 0 | 50 | 1.02 ± 0.27 (1.10) | 6.14 ± 3.28 (6.31) | 1.99 ± 0.33 (1.96) | 4.29 ± 0.74 (4.27) | 1.74 ± 0.50 (1.68) |
| left | p | 0.862 | 50/50 | 0 | 49 | 1.49 ± 0.35 (1.41) | 5.39 ± 3.70 (5.04) | 2.18 ± 0.35 (2.19) | 4.63 ± 0.82 (4.76) | 2.01 ± 0.57 (2.05) |
| back | p | 0.851 | 50/50 | 0 | 49 | 2.25 ± 0.27 (2.22) | 5.24 ± 3.46 (4.83) | 2.33 ± 0.43 (2.43) | 4.97 ± 1.00 (5.32) | 2.29 ± 0.64 (2.56) |
| right | p | 0.843 | 50/50 | 0 | 50 | 1.49 ± 0.35 (1.50) | 5.60 ± 3.73 (4.93) | 2.17 ± 0.35 (2.18) | 4.61 ± 0.85 (4.87) | 2.01 ± 0.60 (2.05) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.844 | 100/100 | 0 | 99 | 1.56 ± 0.55 (1.44) | 5.90 ± 3.71 (5.43) | 2.19 ± 0.36 (2.19) | 4.68 ± 0.85 (4.85) | 2.05 ± 0.60 (2.09) |
| right | p | 0.856 | 100/100 | 0 | 99 | 1.56 ± 0.54 (1.51) | 5.29 ± 3.38 (5.11) | 2.15 ± 0.41 (2.15) | 4.57 ± 0.92 (4.75) | 1.98 ± 0.61 (1.97) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.837 | 25/25 | 0 | 25 | 1.00 ± 0.27 (1.00) | 6.49 ± 3.59 (6.71) | 1.94 ± 0.26 (1.93) | 4.19 ± 0.65 (4.09) | 1.68 ± 0.42 (1.67) |
| forward/right | p | 0.851 | 25/25 | 0 | 25 | 1.03 ± 0.26 (1.12) | 5.79 ± 2.91 (5.73) | 2.04 ± 0.38 (2.00) | 4.38 ± 0.82 (4.34) | 1.81 ± 0.56 (1.81) |
| left/left | p | 0.855 | 25/25 | 0 | 24 | 1.40 ± 0.34 (1.36) | 6.24 ± 4.26 (5.49) | 2.19 ± 0.37 (2.29) | 4.68 ± 0.86 (4.99) | 2.05 ± 0.58 (2.09) |
| left/right | p | 0.869 | 25/25 | 0 | 25 | 1.57 ± 0.34 (1.58) | 4.54 ± 2.80 (4.09) | 2.17 ± 0.34 (2.10) | 4.59 ± 0.78 (4.73) | 1.98 ± 0.55 (1.96) |
| back/left | p | 0.847 | 25/25 | 0 | 25 | 2.26 ± 0.25 (2.24) | 5.33 ± 3.16 (5.39) | 2.39 ± 0.30 (2.48) | 5.10 ± 0.75 (5.33) | 2.36 ± 0.55 (2.57) |
| back/right | p | 0.855 | 25/25 | 0 | 24 | 2.25 ± 0.29 (2.20) | 5.15 ± 3.74 (4.65) | 2.27 ± 0.52 (2.39) | 4.83 ± 1.19 (5.29) | 2.22 ± 0.71 (2.54) |
| right/left | p | 0.836 | 25/25 | 0 | 25 | 1.58 ± 0.35 (1.50) | 5.53 ± 3.63 (4.75) | 2.22 ± 0.36 (2.23) | 4.74 ± 0.88 (4.94) | 2.11 ± 0.63 (2.26) |
| right/right | p | 0.850 | 25/25 | 0 | 25 | 1.40 ± 0.32 (1.38) | 5.67 ± 3.81 (5.12) | 2.12 ± 0.33 (2.08) | 4.49 ± 0.79 (4.49) | 1.92 ± 0.55 (1.85) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.878 | 5.3 | 5.15 | 2.36 |
| p | normal | 0.822 | 5.9 | 4.10 | 1.66 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.764 | 0.13 | 2.32 ± 0.78 (2.18) | 3.62 | 1.34 |
| p | medium | 20 | 0.892 | 0.80 | 1.20 ± 0.15 (1.21) | 3.84 | 1.47 |
| p | strong | 126 | 0.880 | 0.69 | - | 5.18 | 2.39 |

## Notes

- p: score 0.850, 200/200 kicked, 0 fell; worst sector right (0.843).

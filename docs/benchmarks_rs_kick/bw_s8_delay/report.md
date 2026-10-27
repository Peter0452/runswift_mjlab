# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.778** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 164 |
| Weak kicks (< 0.3 m) | 28 |
| Time to kick [s] | 2.01 ± 1.85 (1.52) |
| Direction error [°] | 21.32 ± 40.04 (5.73) |
| Avg ball speed [m/s] | 1.66 ± 0.62 (1.88) |
| Peak ball speed [m/s] | 3.61 ± 1.43 (3.90) |
| Distance [m] | 1.26 ± 0.67 (1.34) |
| Path length [m] | 1.27 ± 0.68 (1.34) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.787 | 50/50 | 0 | 41 | 1.60 ± 1.88 (1.14) | 10.23 ± 13.58 (4.91) | 1.50 ± 0.57 (1.52) | 3.19 ± 1.29 (3.19) | 1.01 ± 0.61 (0.95) |
| left | p | 0.782 | 50/50 | 0 | 41 | 1.99 ± 1.91 (1.54) | 21.63 ± 36.43 (6.24) | 1.73 ± 0.58 (1.94) | 3.77 ± 1.35 (4.44) | 1.33 ± 0.65 (1.46) |
| back | p | 0.749 | 50/50 | 0 | 40 | 2.62 ± 1.79 (2.36) | 34.16 ± 58.25 (6.27) | 1.75 ± 0.70 (2.09) | 3.82 ± 1.61 (4.60) | 1.42 ± 0.74 (1.70) |
| right | p | 0.795 | 50/50 | 0 | 42 | 1.83 ± 1.65 (1.49) | 19.28 ± 34.89 (5.33) | 1.68 ± 0.57 (1.80) | 3.67 ± 1.35 (3.76) | 1.27 ± 0.62 (1.33) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.804 | 100/100 | 0 | 86 | 1.71 ± 1.18 (1.49) | 18.50 ± 36.99 (5.68) | 1.71 ± 0.57 (1.92) | 3.72 ± 1.32 (4.01) | 1.30 ± 0.64 (1.37) |
| right | p | 0.752 | 100/100 | 0 | 78 | 2.31 ± 2.29 (1.52) | 24.14 ± 42.70 (6.03) | 1.62 ± 0.66 (1.80) | 3.51 ± 1.52 (3.76) | 1.22 ± 0.70 (1.32) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.819 | 25/25 | 0 | 22 | 1.19 ± 0.44 (1.16) | 7.90 ± 9.40 (4.54) | 1.56 ± 0.57 (1.51) | 3.31 ± 1.26 (3.17) | 1.06 ± 0.61 (0.93) |
| forward/right | p | 0.755 | 25/25 | 0 | 19 | 2.01 ± 2.56 (1.14) | 12.56 ± 16.41 (5.99) | 1.43 ± 0.56 (1.53) | 3.06 ± 1.32 (3.21) | 0.95 ± 0.62 (0.98) |
| left/left | p | 0.832 | 25/25 | 0 | 22 | 1.37 ± 0.40 (1.42) | 15.56 ± 24.61 (7.09) | 1.78 ± 0.49 (1.95) | 3.87 ± 1.13 (4.42) | 1.37 ± 0.59 (1.45) |
| left/right | p | 0.733 | 25/25 | 0 | 19 | 2.62 ± 2.51 (1.66) | 27.69 ± 44.44 (5.56) | 1.69 ± 0.65 (1.94) | 3.68 ± 1.54 (4.46) | 1.30 ± 0.70 (1.47) |
| back/left | p | 0.763 | 25/25 | 0 | 21 | 2.66 ± 1.93 (2.28) | 29.15 ± 54.40 (6.93) | 1.84 ± 0.56 (2.08) | 4.01 ± 1.32 (4.57) | 1.49 ± 0.66 (1.75) |
| back/right | p | 0.734 | 25/25 | 0 | 19 | 2.58 ± 1.64 (2.44) | 39.17 ± 61.46 (5.58) | 1.66 ± 0.81 (2.10) | 3.62 ± 1.82 (4.63) | 1.35 ± 0.80 (1.64) |
| right/left | p | 0.802 | 25/25 | 0 | 21 | 1.63 ± 0.46 (1.64) | 21.39 ± 39.70 (4.89) | 1.67 ± 0.60 (1.80) | 3.68 ± 1.43 (3.77) | 1.27 ± 0.64 (1.32) |
| right/right | p | 0.787 | 25/25 | 0 | 21 | 2.03 ± 2.27 (1.46) | 17.17 ± 29.13 (7.45) | 1.69 ± 0.53 (1.79) | 3.66 ± 1.26 (3.74) | 1.27 ± 0.61 (1.34) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.796 | 17.3 | 4.17 | 1.54 |
| p | normal | 0.761 | 25.4 | 3.06 | 0.98 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.731 | 0.37 | 1.73 ± 0.89 (1.57) | 2.69 | 0.78 |
| p | medium | 16 | 0.846 | 0.80 | 0.94 ± 0.30 (1.06) | 3.05 | 0.96 |
| p | strong | 126 | 0.791 | 0.55 | - | 4.11 | 1.52 |

## Notes

- p: score 0.778, 200/200 kicked, 0 fell; worst sector back (0.749).

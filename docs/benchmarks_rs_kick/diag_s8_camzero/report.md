# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.777** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 164 |
| Weak kicks (< 0.3 m) | 31 |
| Time to kick [s] | 1.92 ± 1.72 (1.51) |
| Direction error [°] | 22.97 ± 42.89 (6.27) |
| Avg ball speed [m/s] | 1.70 ± 0.66 (1.89) |
| Peak ball speed [m/s] | 3.72 ± 1.51 (4.06) |
| Distance [m] | 1.38 ± 0.75 (1.46) |
| Path length [m] | 1.39 ± 0.75 (1.46) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.788 | 50/50 | 0 | 42 | 1.61 ± 1.93 (1.15) | 10.40 ± 14.17 (5.26) | 1.54 ± 0.59 (1.60) | 3.35 ± 1.37 (3.36) | 1.13 ± 0.67 (1.12) |
| left | p | 0.790 | 50/50 | 0 | 41 | 1.85 ± 1.67 (1.54) | 23.43 ± 40.39 (6.92) | 1.77 ± 0.61 (1.95) | 3.88 ± 1.42 (4.33) | 1.45 ± 0.72 (1.53) |
| back | p | 0.743 | 50/50 | 0 | 39 | 2.42 ± 1.45 (2.33) | 39.06 ± 62.96 (7.49) | 1.74 ± 0.79 (2.09) | 3.81 ± 1.78 (4.73) | 1.51 ± 0.85 (1.80) |
| right | p | 0.787 | 50/50 | 0 | 42 | 1.82 ± 1.69 (1.49) | 18.98 ± 33.62 (6.17) | 1.75 ± 0.59 (1.89) | 3.84 ± 1.36 (3.95) | 1.43 ± 0.68 (1.46) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.800 | 100/100 | 0 | 83 | 1.58 ± 0.67 (1.50) | 22.41 ± 42.69 (6.13) | 1.70 ± 0.66 (1.89) | 3.71 ± 1.48 (4.07) | 1.37 ± 0.74 (1.47) |
| right | p | 0.754 | 100/100 | 0 | 81 | 2.27 ± 2.29 (1.53) | 23.52 ± 43.09 (6.82) | 1.71 ± 0.66 (1.94) | 3.73 ± 1.53 (4.06) | 1.39 ± 0.76 (1.46) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.813 | 25/25 | 0 | 22 | 1.17 ± 0.42 (1.14) | 8.64 ± 11.31 (4.97) | 1.56 ± 0.55 (1.57) | 3.40 ± 1.23 (3.32) | 1.14 ± 0.59 (1.02) |
| forward/right | p | 0.762 | 25/25 | 0 | 20 | 2.05 ± 2.62 (1.16) | 12.17 ± 16.36 (5.68) | 1.52 ± 0.63 (1.72) | 3.31 ± 1.49 (3.64) | 1.13 ± 0.73 (1.23) |
| left/left | p | 0.837 | 25/25 | 0 | 22 | 1.38 ± 0.40 (1.50) | 15.15 ± 25.10 (6.89) | 1.79 ± 0.53 (1.89) | 3.91 ± 1.21 (4.08) | 1.43 ± 0.64 (1.48) |
| left/right | p | 0.742 | 25/25 | 0 | 19 | 2.32 ± 2.23 (1.66) | 31.70 ± 49.96 (6.95) | 1.75 ± 0.69 (2.03) | 3.85 ± 1.60 (4.62) | 1.46 ± 0.79 (1.66) |
| back/left | p | 0.753 | 25/25 | 0 | 19 | 2.20 ± 0.82 (2.22) | 41.67 ± 64.45 (6.42) | 1.72 ± 0.79 (2.13) | 3.78 ± 1.78 (4.73) | 1.49 ± 0.85 (1.82) |
| back/right | p | 0.732 | 25/25 | 0 | 20 | 2.64 ± 1.85 (2.38) | 36.46 ± 61.32 (7.69) | 1.76 ± 0.79 (2.09) | 3.83 ± 1.78 (4.73) | 1.53 ± 0.85 (1.79) |
| right/left | p | 0.794 | 25/25 | 0 | 20 | 1.58 ± 0.45 (1.60) | 24.20 ± 41.97 (5.37) | 1.72 ± 0.70 (1.91) | 3.76 ± 1.59 (4.05) | 1.42 ± 0.78 (1.55) |
| right/right | p | 0.780 | 25/25 | 0 | 22 | 2.05 ± 2.33 (1.48) | 13.76 ± 21.07 (6.83) | 1.79 ± 0.45 (1.77) | 3.92 ± 1.07 (3.80) | 1.44 ± 0.57 (1.43) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.799 | 20.2 | 4.25 | 1.66 |
| p | normal | 0.755 | 25.8 | 3.19 | 1.10 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.721 | 0.32 | 1.83 ± 0.93 (1.73) | 2.85 | 0.89 |
| p | medium | 16 | 0.843 | 0.74 | 0.99 ± 0.35 (1.10) | 3.20 | 1.09 |
| p | strong | 126 | 0.794 | 0.56 | - | 4.19 | 1.64 |

## Notes

- p: score 0.777, 200/200 kicked, 0 fell; worst sector back (0.743).

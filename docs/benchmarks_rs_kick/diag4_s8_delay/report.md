# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.777** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 165 |
| Weak kicks (< 0.3 m) | 25 |
| Time to kick [s] | 2.02 ± 1.89 (1.51) |
| Direction error [°] | 20.75 ± 39.17 (5.99) |
| Avg ball speed [m/s] | 1.64 ± 0.58 (1.84) |
| Peak ball speed [m/s] | 3.61 ± 1.36 (3.93) |
| Distance [m] | 1.23 ± 0.64 (1.36) |
| Path length [m] | 1.24 ± 0.64 (1.36) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.787 | 50/50 | 0 | 42 | 1.72 ± 2.17 (1.18) | 10.09 ± 13.96 (4.36) | 1.51 ± 0.58 (1.60) | 3.27 ± 1.30 (3.35) | 1.05 ± 0.59 (1.07) |
| left | p | 0.790 | 50/50 | 0 | 42 | 2.04 ± 2.08 (1.59) | 19.72 ± 36.31 (6.37) | 1.71 ± 0.55 (1.96) | 3.79 ± 1.32 (4.44) | 1.32 ± 0.63 (1.48) |
| back | p | 0.760 | 50/50 | 0 | 40 | 2.43 ± 1.29 (2.28) | 32.73 ± 56.49 (6.01) | 1.72 ± 0.62 (2.04) | 3.78 ± 1.46 (4.55) | 1.35 ± 0.69 (1.60) |
| right | p | 0.771 | 50/50 | 0 | 41 | 1.91 ± 1.82 (1.49) | 20.46 ± 34.25 (6.70) | 1.64 ± 0.56 (1.81) | 3.58 ± 1.29 (3.86) | 1.22 ± 0.59 (1.36) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.805 | 100/100 | 0 | 86 | 1.71 ± 1.16 (1.47) | 19.23 ± 38.00 (5.84) | 1.69 ± 0.56 (1.87) | 3.72 ± 1.31 (4.04) | 1.29 ± 0.63 (1.41) |
| right | p | 0.749 | 100/100 | 0 | 79 | 2.34 ± 2.36 (1.57) | 22.27 ± 40.24 (6.20) | 1.59 ± 0.59 (1.79) | 3.49 ± 1.40 (3.82) | 1.18 ± 0.63 (1.29) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.835 | 25/25 | 0 | 24 | 1.39 ± 1.57 (1.18) | 6.47 ± 10.92 (3.19) | 1.61 ± 0.52 (1.86) | 3.47 ± 1.14 (3.67) | 1.13 ± 0.55 (1.26) |
| forward/right | p | 0.739 | 25/25 | 0 | 18 | 2.04 ± 2.60 (1.22) | 13.71 ± 15.64 (7.14) | 1.41 ± 0.61 (1.58) | 3.07 ± 1.41 (3.30) | 0.97 ± 0.62 (0.99) |
| left/left | p | 0.837 | 25/25 | 0 | 22 | 1.38 ± 0.40 (1.44) | 13.68 ± 23.62 (7.38) | 1.75 ± 0.53 (1.98) | 3.89 ± 1.24 (4.55) | 1.37 ± 0.58 (1.49) |
| left/right | p | 0.743 | 25/25 | 0 | 20 | 2.70 ± 2.76 (1.78) | 25.75 ± 44.78 (5.90) | 1.67 ± 0.56 (1.89) | 3.70 ± 1.39 (4.09) | 1.27 ± 0.66 (1.41) |
| back/left | p | 0.767 | 25/25 | 0 | 20 | 2.47 ± 1.31 (2.26) | 31.82 ± 54.55 (6.36) | 1.77 ± 0.59 (2.05) | 3.91 ± 1.41 (4.66) | 1.41 ± 0.71 (1.71) |
| back/right | p | 0.752 | 25/25 | 0 | 20 | 2.39 ± 1.26 (2.30) | 33.65 ± 58.36 (5.60) | 1.67 ± 0.64 (1.91) | 3.64 ± 1.50 (4.12) | 1.29 ± 0.67 (1.49) |
| right/left | p | 0.782 | 25/25 | 0 | 20 | 1.58 ± 0.46 (1.56) | 24.95 ± 41.68 (6.51) | 1.65 ± 0.60 (1.83) | 3.61 ± 1.36 (3.78) | 1.25 ± 0.64 (1.36) |
| right/right | p | 0.760 | 25/25 | 0 | 21 | 2.24 ± 2.48 (1.42) | 15.98 ± 23.85 (7.04) | 1.63 ± 0.52 (1.80) | 3.55 ± 1.21 (3.96) | 1.18 ± 0.53 (1.36) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.792 | 19.1 | 4.17 | 1.52 |
| p | normal | 0.761 | 22.5 | 3.04 | 0.95 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.733 | 0.36 | 1.72 ± 0.85 (1.62) | 2.70 | 0.78 |
| p | medium | 16 | 0.872 | 0.84 | 1.00 ± 0.22 (1.02) | 3.25 | 1.03 |
| p | strong | 126 | 0.785 | 0.54 | - | 4.07 | 1.47 |

## Notes

- p: score 0.777, 200/200 kicked, 0 fell; worst sector back (0.760).

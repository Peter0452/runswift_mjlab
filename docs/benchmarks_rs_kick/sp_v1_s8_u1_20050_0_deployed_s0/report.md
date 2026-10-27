# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/v1_s8_u1_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.782** |
| Kicked / fell | 194 / 0 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 14 |
| Time to kick [s] | 1.95 ± 1.39 (1.74) |
| Direction error [°] | 19.59 ± 41.18 (4.49) |
| Avg ball speed [m/s] | 1.98 ± 0.66 (2.21) |
| Peak ball speed [m/s] | 4.44 ± 1.63 (5.20) |
| Distance [m] | 1.70 ± 0.85 (1.85) |
| Path length [m] | 1.71 ± 0.85 (1.86) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.787 | 48/50 | 0 | 42 | 1.73 ± 2.12 (1.36) | 8.19 ± 10.38 (5.16) | 1.99 ± 0.63 (1.99) | 4.39 ± 1.57 (3.99) | 1.67 ± 0.88 (1.43) |
| left | p | 0.804 | 48/50 | 0 | 42 | 1.69 ± 0.50 (1.76) | 17.29 ± 33.91 (5.18) | 2.03 ± 0.62 (2.25) | 4.59 ± 1.57 (5.40) | 1.77 ± 0.82 (2.03) |
| back | p | 0.740 | 49/50 | 0 | 40 | 2.46 ± 0.79 (2.54) | 33.07 ± 60.41 (4.66) | 1.98 ± 0.71 (2.22) | 4.42 ± 1.71 (5.26) | 1.71 ± 0.84 (2.07) |
| right | p | 0.796 | 49/50 | 0 | 39 | 1.89 ± 1.41 (1.74) | 19.52 ± 38.98 (3.18) | 1.93 ± 0.67 (1.95) | 4.34 ± 1.64 (4.76) | 1.65 ± 0.85 (1.58) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.813 | 99/100 | 0 | 86 | 1.86 ± 1.19 (1.74) | 18.75 ± 41.53 (4.05) | 2.02 ± 0.62 (2.24) | 4.52 ± 1.52 (5.26) | 1.74 ± 0.81 (2.01) |
| right | p | 0.751 | 95/100 | 0 | 77 | 2.03 ± 1.56 (1.74) | 20.46 ± 40.80 (5.29) | 1.94 ± 0.70 (2.11) | 4.35 ± 1.73 (4.76) | 1.66 ± 0.89 (1.62) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.836 | 25/25 | 0 | 23 | 1.72 ± 2.10 (1.32) | 7.04 ± 10.18 (3.64) | 2.08 ± 0.55 (2.22) | 4.61 ± 1.41 (5.36) | 1.78 ± 0.79 (1.87) |
| forward/right | p | 0.738 | 23/25 | 0 | 19 | 1.74 ± 2.14 (1.36) | 9.44 ± 10.45 (6.91) | 1.88 ± 0.69 (1.74) | 4.15 ± 1.70 (3.62) | 1.55 ± 0.95 (1.25) |
| left/left | p | 0.865 | 25/25 | 0 | 23 | 1.61 ± 0.42 (1.70) | 10.91 ± 22.38 (4.29) | 2.12 ± 0.51 (2.24) | 4.75 ± 1.29 (5.37) | 1.85 ± 0.73 (2.01) |
| left/right | p | 0.744 | 23/25 | 0 | 19 | 1.77 ± 0.55 (1.90) | 24.22 ± 42.00 (6.07) | 1.93 ± 0.71 (2.26) | 4.42 ± 1.81 (5.51) | 1.68 ± 0.90 (2.06) |
| back/left | p | 0.742 | 24/25 | 0 | 20 | 2.36 ± 0.69 (2.54) | 31.08 ± 59.29 (4.63) | 2.05 ± 0.58 (2.30) | 4.61 ± 1.43 (5.25) | 1.78 ± 0.77 (2.09) |
| back/right | p | 0.738 | 25/25 | 0 | 20 | 2.56 ± 0.87 (2.54) | 34.98 ± 61.40 (4.66) | 1.90 ± 0.80 (2.13) | 4.24 ± 1.92 (5.26) | 1.65 ± 0.90 (1.71) |
| right/left | p | 0.809 | 25/25 | 0 | 20 | 1.79 ± 0.51 (1.82) | 26.46 ± 49.46 (2.71) | 1.84 ± 0.76 (1.91) | 4.12 ± 1.82 (3.90) | 1.55 ± 0.90 (1.49) |
| right/right | p | 0.784 | 24/25 | 0 | 19 | 2.00 ± 1.94 (1.71) | 12.28 ± 21.25 (3.35) | 2.03 ± 0.54 (2.12) | 4.58 ± 1.39 (5.06) | 1.76 ± 0.78 (1.76) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.803 | 18.5 | 5.22 | 2.13 |
| p | normal | 0.761 | 20.6 | 3.67 | 1.28 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.722 | 0.23 | 2.06 ± 0.85 (1.94) | 3.24 | 1.04 |
| p | medium | 16 | 0.828 | 0.79 | 1.13 ± 0.21 (1.16) | 3.65 | 1.26 |
| p | strong | 126 | 0.804 | 0.68 | - | 5.09 | 2.06 |

## Notes

- p: score 0.782, 194/200 kicked, 0 fell; worst sector back (0.740).

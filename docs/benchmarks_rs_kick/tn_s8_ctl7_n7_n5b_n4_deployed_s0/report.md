# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.793** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 17 |
| Time to kick [s] | 1.98 ± 1.54 (1.72) |
| Direction error [°] | 20.39 ± 39.40 (5.44) |
| Avg ball speed [m/s] | 2.31 ± 0.90 (2.59) |
| Peak ball speed [m/s] | 4.84 ± 1.93 (5.83) |
| Distance [m] | 2.37 ± 1.22 (2.88) |
| Path length [m] | 2.38 ± 1.22 (2.90) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.802 | 50/50 | 0 | 42 | 1.63 ± 1.82 (1.34) | 9.65 ± 13.51 (4.41) | 2.19 ± 0.83 (2.19) | 4.57 ± 1.79 (4.31) | 2.13 ± 1.11 (1.84) |
| left | p | 0.827 | 49/50 | 0 | 43 | 1.85 ± 1.35 (1.74) | 14.33 ± 29.17 (4.73) | 2.50 ± 0.71 (2.77) | 5.26 ± 1.58 (6.06) | 2.61 ± 1.07 (3.08) |
| back | p | 0.742 | 50/50 | 0 | 37 | 2.38 ± 0.73 (2.43) | 38.23 ± 59.29 (8.64) | 2.25 ± 1.10 (2.80) | 4.74 ± 2.36 (6.25) | 2.43 ± 1.46 (3.36) |
| right | p | 0.800 | 50/50 | 0 | 41 | 2.05 ± 1.89 (1.74) | 19.23 ± 34.29 (4.92) | 2.30 ± 0.87 (2.57) | 4.80 ± 1.84 (5.68) | 2.31 ± 1.13 (2.85) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.815 | 100/100 | 0 | 85 | 1.75 ± 0.62 (1.69) | 19.46 ± 39.58 (5.37) | 2.35 ± 0.85 (2.61) | 4.94 ± 1.86 (5.87) | 2.44 ± 1.19 (2.94) |
| right | p | 0.771 | 99/100 | 0 | 78 | 2.22 ± 2.07 (1.74) | 21.33 ± 39.20 (5.48) | 2.27 ± 0.94 (2.51) | 4.74 ± 2.00 (5.63) | 2.30 ± 1.24 (2.82) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.843 | 25/25 | 0 | 22 | 1.29 ± 0.29 (1.28) | 7.56 ± 12.79 (3.42) | 2.28 ± 0.74 (2.22) | 4.76 ± 1.64 (4.34) | 2.23 ± 1.03 (1.83) |
| forward/right | p | 0.761 | 25/25 | 0 | 20 | 1.98 ± 2.51 (1.36) | 11.74 ± 13.88 (6.37) | 2.11 ± 0.91 (2.15) | 4.39 ± 1.91 (4.28) | 2.03 ± 1.18 (1.86) |
| left/left | p | 0.873 | 25/25 | 0 | 24 | 1.59 ± 0.38 (1.68) | 9.02 ± 14.86 (5.17) | 2.62 ± 0.57 (2.78) | 5.53 ± 1.36 (6.13) | 2.81 ± 0.96 (3.23) |
| left/right | p | 0.782 | 24/25 | 0 | 19 | 2.13 ± 1.85 (1.94) | 19.87 ± 38.04 (3.73) | 2.38 ± 0.81 (2.66) | 4.98 ± 1.73 (5.96) | 2.40 ± 1.14 (3.01) |
| back/left | p | 0.735 | 25/25 | 0 | 18 | 2.34 ± 0.71 (2.44) | 41.26 ± 60.82 (9.90) | 2.20 ± 1.11 (2.68) | 4.68 ± 2.38 (5.92) | 2.40 ± 1.52 (3.25) |
| back/right | p | 0.750 | 25/25 | 0 | 19 | 2.42 ± 0.75 (2.36) | 35.20 ± 57.56 (7.69) | 2.31 ± 1.09 (2.82) | 4.80 ± 2.33 (6.25) | 2.47 ± 1.41 (3.36) |
| right/left | p | 0.811 | 25/25 | 0 | 21 | 1.76 ± 0.48 (1.80) | 20.01 ± 38.15 (4.84) | 2.31 ± 0.83 (2.56) | 4.81 ± 1.78 (5.56) | 2.30 ± 1.09 (2.81) |
| right/right | p | 0.790 | 25/25 | 0 | 20 | 2.34 ± 2.60 (1.72) | 18.45 ± 29.92 (5.01) | 2.28 ± 0.91 (2.67) | 4.80 ± 1.91 (6.00) | 2.32 ± 1.17 (2.92) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.831 | 16.9 | 5.72 | 2.99 |
| p | normal | 0.755 | 23.9 | 3.97 | 1.76 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.714 | 0.16 | 2.20 ± 1.21 (2.13) | 3.39 | 1.35 |
| p | medium | 16 | 0.809 | 0.66 | 1.17 ± 0.37 (1.24) | 3.80 | 1.58 |
| p | strong | 126 | 0.827 | 0.75 | - | 5.65 | 2.94 |

## Notes

- p: score 0.793, 199/200 kicked, 0 fell; worst sector back (0.742).

# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/x1_u6_u10_u9.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.780** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 171 |
| Weak kicks (< 0.3 m) | 13 |
| Time to kick [s] | 2.11 ± 1.80 (1.74) |
| Direction error [°] | 16.71 ± 34.54 (5.75) |
| Avg ball speed [m/s] | 2.06 ± 0.60 (2.20) |
| Peak ball speed [m/s] | 4.53 ± 1.48 (4.92) |
| Distance [m] | 1.77 ± 0.79 (1.84) |
| Path length [m] | 1.78 ± 0.80 (1.85) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.804 | 50/50 | 0 | 45 | 1.90 ± 2.26 (1.36) | 7.84 ± 9.80 (4.54) | 2.03 ± 0.62 (2.07) | 4.43 ± 1.51 (4.18) | 1.71 ± 0.83 (1.66) |
| left | p | 0.808 | 49/50 | 0 | 43 | 1.85 ± 1.41 (1.76) | 17.72 ± 33.68 (5.69) | 2.10 ± 0.65 (2.26) | 4.64 ± 1.59 (5.13) | 1.87 ± 0.86 (2.00) |
| back | p | 0.730 | 48/50 | 0 | 42 | 2.64 ± 1.28 (2.56) | 23.70 ± 48.70 (6.16) | 2.14 ± 0.56 (2.28) | 4.68 ± 1.36 (5.23) | 1.88 ± 0.72 (2.03) |
| right | p | 0.779 | 49/50 | 0 | 41 | 2.07 ± 1.94 (1.70) | 17.89 ± 32.96 (6.49) | 1.97 ± 0.56 (2.14) | 4.37 ± 1.41 (4.70) | 1.63 ± 0.72 (1.69) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.802 | 99/100 | 0 | 88 | 1.94 ± 1.32 (1.70) | 16.74 ± 36.43 (4.64) | 2.11 ± 0.58 (2.24) | 4.65 ± 1.41 (5.07) | 1.84 ± 0.78 (1.92) |
| right | p | 0.758 | 97/100 | 0 | 83 | 2.29 ± 2.17 (1.74) | 16.68 ± 32.50 (6.30) | 2.00 ± 0.62 (2.14) | 4.40 ± 1.54 (4.72) | 1.70 ± 0.80 (1.74) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.836 | 25/25 | 0 | 24 | 1.62 ± 1.63 (1.30) | 6.03 ± 8.96 (4.04) | 2.18 ± 0.50 (2.23) | 4.80 ± 1.22 (5.07) | 1.89 ± 0.71 (1.92) |
| forward/right | p | 0.772 | 25/25 | 0 | 21 | 2.18 ± 2.73 (1.36) | 9.64 ± 10.25 (6.46) | 1.87 ± 0.69 (1.90) | 4.06 ± 1.68 (3.72) | 1.53 ± 0.90 (1.39) |
| left/left | p | 0.858 | 25/25 | 0 | 23 | 1.59 ± 0.40 (1.70) | 11.51 ± 21.87 (4.42) | 2.17 ± 0.55 (2.23) | 4.81 ± 1.35 (5.13) | 1.94 ± 0.77 (2.05) |
| left/right | p | 0.758 | 24/25 | 0 | 20 | 2.12 ± 1.93 (1.94) | 24.20 ± 41.66 (6.64) | 2.02 ± 0.74 (2.32) | 4.46 ± 1.79 (4.95) | 1.79 ± 0.94 (1.95) |
| back/left | p | 0.745 | 25/25 | 0 | 21 | 2.74 ± 1.71 (2.56) | 28.76 ± 54.01 (6.59) | 2.14 ± 0.61 (2.30) | 4.63 ± 1.43 (5.22) | 1.89 ± 0.81 (2.08) |
| back/right | p | 0.715 | 23/25 | 0 | 21 | 2.53 ± 0.48 (2.56) | 18.21 ± 41.48 (5.15) | 2.14 ± 0.50 (2.23) | 4.73 ± 1.26 (5.24) | 1.87 ± 0.62 (1.99) |
| right/left | p | 0.770 | 24/25 | 0 | 20 | 1.79 ± 0.51 (1.74) | 20.82 ± 39.24 (6.61) | 1.96 ± 0.62 (2.15) | 4.35 ± 1.55 (4.70) | 1.64 ± 0.79 (1.82) |
| right/right | p | 0.788 | 25/25 | 0 | 21 | 2.35 ± 2.64 (1.70) | 15.07 ± 25.21 (5.44) | 1.99 ± 0.49 (2.10) | 4.39 ± 1.26 (4.70) | 1.62 ± 0.65 (1.67) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.794 | 14.1 | 5.25 | 2.13 |
| p | normal | 0.766 | 19.2 | 3.84 | 1.42 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.727 | 0.20 | 2.19 ± 0.96 (2.07) | 3.45 | 1.20 |
| p | medium | 16 | 0.836 | 0.72 | 1.23 ± 0.20 (1.28) | 4.01 | 1.53 |
| p | strong | 126 | 0.798 | 0.68 | - | 5.11 | 2.07 |

## Notes

- p: score 0.780, 196/200 kicked, 0 fell; worst sector back (0.730).

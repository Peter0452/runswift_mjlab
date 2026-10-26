# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s3_ctl7_n7.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.780** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 172 |
| Weak kicks (< 0.3 m) | 18 |
| Time to kick [s] | 2.20 ± 1.99 (1.78) |
| Direction error [°] | 15.99 ± 32.19 (5.39) |
| Avg ball speed [m/s] | 2.08 ± 0.65 (2.25) |
| Peak ball speed [m/s] | 4.53 ± 1.51 (5.08) |
| Distance [m] | 1.87 ± 0.81 (1.99) |
| Path length [m] | 1.88 ± 0.81 (2.01) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.822 | 50/50 | 0 | 45 | 1.66 ± 2.03 (1.28) | 8.64 ± 14.67 (4.74) | 2.09 ± 0.64 (2.25) | 4.57 ± 1.50 (4.98) | 1.89 ± 0.83 (1.99) |
| left | p | 0.809 | 50/50 | 0 | 43 | 1.82 ± 1.16 (1.71) | 15.43 ± 29.19 (6.53) | 2.09 ± 0.64 (2.24) | 4.58 ± 1.50 (5.08) | 1.89 ± 0.84 (2.02) |
| back | p | 0.737 | 49/50 | 0 | 43 | 2.69 ± 1.44 (2.54) | 21.64 ± 41.34 (6.76) | 2.14 ± 0.60 (2.30) | 4.62 ± 1.39 (5.12) | 1.93 ± 0.76 (2.07) |
| right | p | 0.753 | 50/50 | 0 | 41 | 2.65 ± 2.71 (1.88) | 18.35 ± 35.91 (4.97) | 1.99 ± 0.68 (2.19) | 4.34 ± 1.62 (4.42) | 1.77 ± 0.79 (1.83) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.805 | 100/100 | 0 | 88 | 1.88 ± 0.97 (1.75) | 14.05 ± 29.52 (5.30) | 2.09 ± 0.63 (2.25) | 4.53 ± 1.49 (5.09) | 1.88 ± 0.79 (2.06) |
| right | p | 0.756 | 99/100 | 0 | 84 | 2.53 ± 2.60 (1.82) | 17.95 ± 34.56 (6.05) | 2.06 ± 0.66 (2.26) | 4.52 ± 1.53 (5.06) | 1.86 ± 0.82 (1.92) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.837 | 25/25 | 0 | 22 | 1.27 ± 0.31 (1.28) | 8.16 ± 14.42 (4.25) | 2.00 ± 0.72 (2.19) | 4.33 ± 1.66 (4.32) | 1.79 ± 0.88 (1.85) |
| forward/right | p | 0.807 | 25/25 | 0 | 23 | 2.05 ± 2.80 (1.28) | 9.13 ± 14.91 (4.86) | 2.17 ± 0.55 (2.27) | 4.82 ± 1.27 (5.33) | 2.00 ± 0.77 (2.17) |
| left/left | p | 0.807 | 25/25 | 0 | 21 | 1.57 ± 0.41 (1.60) | 13.54 ± 21.43 (7.40) | 2.08 ± 0.63 (2.24) | 4.52 ± 1.49 (5.09) | 1.87 ± 0.82 (2.05) |
| left/right | p | 0.812 | 25/25 | 0 | 22 | 2.07 ± 1.55 (1.82) | 17.33 ± 35.17 (5.84) | 2.10 ± 0.64 (2.23) | 4.64 ± 1.50 (5.06) | 1.92 ± 0.85 (1.99) |
| back/left | p | 0.790 | 25/25 | 0 | 23 | 2.52 ± 0.64 (2.54) | 15.54 ± 33.32 (5.53) | 2.21 ± 0.55 (2.33) | 4.78 ± 1.30 (5.32) | 2.01 ± 0.70 (2.20) |
| back/right | p | 0.683 | 24/25 | 0 | 20 | 2.88 ± 1.94 (2.58) | 28.00 ± 47.47 (8.28) | 2.07 ± 0.65 (2.22) | 4.45 ± 1.46 (4.73) | 1.85 ± 0.80 (1.92) |
| right/left | p | 0.785 | 25/25 | 0 | 22 | 2.16 ± 1.47 (1.92) | 18.95 ± 40.60 (3.31) | 2.08 ± 0.58 (2.20) | 4.51 ± 1.44 (4.31) | 1.86 ± 0.74 (1.83) |
| right/right | p | 0.721 | 25/25 | 0 | 19 | 3.13 ± 3.47 (1.86) | 17.75 ± 30.51 (6.38) | 1.90 ± 0.76 (2.17) | 4.16 ± 1.77 (4.50) | 1.68 ± 0.82 (1.82) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.825 | 12.4 | 5.06 | 2.16 |
| p | normal | 0.736 | 19.7 | 3.98 | 1.58 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.699 | 0.12 | 2.36 ± 0.93 (2.33) | 3.78 | 1.46 |
| p | medium | 18 | 0.842 | 0.67 | 1.13 ± 0.37 (1.26) | 3.65 | 1.37 |
| p | strong | 124 | 0.809 | 0.67 | - | 5.00 | 2.13 |

## Notes

- p: score 0.780, 199/200 kicked, 0 fell; worst sector back (0.737).

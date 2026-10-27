# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/r5_u5_u0_u12.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.790** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 172 |
| Weak kicks (< 0.3 m) | 18 |
| Time to kick [s] | 2.19 ± 1.92 (1.80) |
| Direction error [°] | 15.66 ± 33.39 (4.59) |
| Avg ball speed [m/s] | 2.11 ± 0.67 (2.28) |
| Peak ball speed [m/s] | 4.65 ± 1.59 (5.16) |
| Distance [m] | 1.93 ± 0.86 (1.95) |
| Path length [m] | 1.94 ± 0.86 (1.96) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.814 | 49/50 | 0 | 44 | 1.66 ± 1.93 (1.30) | 8.58 ± 15.13 (4.36) | 2.17 ± 0.61 (2.38) | 4.86 ± 1.50 (5.55) | 2.03 ± 0.89 (2.05) |
| left | p | 0.822 | 50/50 | 0 | 42 | 1.78 ± 0.69 (1.76) | 14.47 ± 29.52 (4.30) | 2.09 ± 0.67 (2.26) | 4.63 ± 1.60 (5.20) | 1.92 ± 0.88 (2.00) |
| back | p | 0.750 | 50/50 | 0 | 44 | 2.93 ± 2.06 (2.60) | 20.51 ± 41.35 (5.54) | 2.19 ± 0.67 (2.33) | 4.74 ± 1.55 (4.75) | 2.03 ± 0.85 (1.97) |
| right | p | 0.773 | 50/50 | 0 | 42 | 2.38 ± 2.28 (1.90) | 18.96 ± 39.33 (4.55) | 1.98 ± 0.70 (2.19) | 4.38 ± 1.68 (4.72) | 1.75 ± 0.81 (1.83) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.810 | 99/100 | 0 | 87 | 1.85 ± 0.84 (1.78) | 14.36 ± 32.75 (4.53) | 2.16 ± 0.64 (2.33) | 4.75 ± 1.55 (5.26) | 1.99 ± 0.87 (1.99) |
| right | p | 0.769 | 100/100 | 0 | 85 | 2.53 ± 2.53 (1.85) | 16.96 ± 33.96 (4.90) | 2.06 ± 0.70 (2.25) | 4.56 ± 1.63 (4.94) | 1.87 ± 0.84 (1.93) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.810 | 24/25 | 0 | 21 | 1.28 ± 0.28 (1.30) | 8.47 ± 14.81 (3.69) | 2.15 ± 0.65 (2.27) | 4.75 ± 1.60 (4.92) | 2.00 ± 0.94 (1.90) |
| forward/right | p | 0.818 | 25/25 | 0 | 23 | 2.02 ± 2.64 (1.32) | 8.67 ± 15.43 (4.76) | 2.19 ± 0.57 (2.41) | 4.97 ± 1.39 (5.56) | 2.05 ± 0.83 (2.21) |
| left/left | p | 0.821 | 25/25 | 0 | 21 | 1.60 ± 0.41 (1.62) | 12.12 ± 20.43 (5.86) | 2.08 ± 0.68 (2.25) | 4.60 ± 1.65 (5.16) | 1.90 ± 0.92 (2.02) |
| left/right | p | 0.823 | 25/25 | 0 | 21 | 1.95 ± 0.85 (1.82) | 16.83 ± 36.25 (2.72) | 2.11 ± 0.66 (2.27) | 4.67 ± 1.55 (5.29) | 1.93 ± 0.83 (1.99) |
| back/left | p | 0.803 | 25/25 | 0 | 23 | 2.50 ± 0.47 (2.58) | 15.21 ± 36.12 (4.08) | 2.32 ± 0.60 (2.45) | 5.00 ± 1.44 (5.73) | 2.20 ± 0.82 (2.23) |
| back/right | p | 0.697 | 25/25 | 0 | 21 | 3.37 ± 2.81 (2.62) | 25.81 ± 45.37 (8.48) | 2.07 ± 0.71 (2.23) | 4.47 ± 1.61 (4.52) | 1.86 ± 0.84 (1.88) |
| right/left | p | 0.805 | 25/25 | 0 | 22 | 2.00 ± 1.23 (1.90) | 21.40 ± 47.17 (4.53) | 2.09 ± 0.59 (2.27) | 4.64 ± 1.46 (5.26) | 1.87 ± 0.76 (1.84) |
| right/right | p | 0.741 | 25/25 | 0 | 20 | 2.77 ± 2.93 (1.90) | 16.53 ± 29.27 (4.96) | 1.87 ± 0.78 (2.16) | 4.13 ± 1.84 (4.60) | 1.64 ± 0.83 (1.74) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.830 | 13.4 | 5.17 | 2.22 |
| p | normal | 0.750 | 18.0 | 4.13 | 1.63 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.720 | 0.10 | 2.43 ± 1.03 (2.31) | 3.82 | 1.47 |
| p | medium | 18 | 0.802 | 0.69 | 1.22 ± 0.26 (1.28) | 3.95 | 1.49 |
| p | strong | 124 | 0.821 | 0.69 | - | 5.14 | 2.21 |

## Notes

- p: score 0.790, 199/200 kicked, 0 fell; worst sector back (0.750).

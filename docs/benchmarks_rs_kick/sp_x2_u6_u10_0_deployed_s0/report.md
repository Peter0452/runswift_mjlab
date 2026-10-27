# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/x2_u6_u10.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.782** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 164 |
| Weak kicks (< 0.3 m) | 12 |
| Time to kick [s] | 1.94 ± 1.53 (1.68) |
| Direction error [°] | 19.03 ± 39.61 (4.70) |
| Avg ball speed [m/s] | 2.08 ± 0.63 (2.26) |
| Peak ball speed [m/s] | 4.56 ± 1.51 (5.23) |
| Distance [m] | 1.85 ± 0.82 (1.96) |
| Path length [m] | 1.86 ± 0.83 (1.96) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.795 | 50/50 | 0 | 43 | 1.95 ± 2.46 (1.34) | 8.19 ± 10.75 (4.38) | 2.03 ± 0.60 (2.11) | 4.43 ± 1.45 (4.27) | 1.75 ± 0.78 (1.69) |
| left | p | 0.799 | 48/50 | 0 | 41 | 1.65 ± 0.48 (1.70) | 18.33 ± 35.02 (4.67) | 2.10 ± 0.60 (2.29) | 4.66 ± 1.44 (5.42) | 1.89 ± 0.78 (2.12) |
| back | p | 0.747 | 49/50 | 0 | 40 | 2.47 ± 1.48 (2.44) | 33.22 ± 59.89 (5.00) | 2.08 ± 0.73 (2.35) | 4.55 ± 1.69 (5.40) | 1.90 ± 0.92 (2.11) |
| right | p | 0.787 | 48/50 | 0 | 40 | 1.68 ± 0.47 (1.72) | 16.53 ± 32.10 (4.24) | 2.09 ± 0.59 (2.24) | 4.61 ± 1.43 (5.27) | 1.87 ± 0.79 (2.02) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.813 | 100/100 | 0 | 85 | 1.92 ± 1.46 (1.67) | 19.18 ± 41.56 (4.61) | 2.13 ± 0.60 (2.28) | 4.68 ± 1.43 (5.29) | 1.93 ± 0.81 (2.04) |
| right | p | 0.751 | 95/100 | 0 | 79 | 1.97 ± 1.59 (1.72) | 18.87 ± 37.44 (4.87) | 2.02 ± 0.66 (2.19) | 4.43 ± 1.57 (5.09) | 1.78 ± 0.83 (1.83) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.835 | 25/25 | 0 | 22 | 1.65 ± 1.87 (1.30) | 6.58 ± 10.78 (3.54) | 2.18 ± 0.50 (2.26) | 4.74 ± 1.22 (5.23) | 1.93 ± 0.73 (1.93) |
| forward/right | p | 0.755 | 25/25 | 0 | 21 | 2.25 ± 2.91 (1.36) | 9.80 ± 10.47 (6.77) | 1.88 ± 0.65 (1.98) | 4.12 ± 1.58 (4.17) | 1.58 ± 0.79 (1.66) |
| left/left | p | 0.855 | 25/25 | 0 | 23 | 1.58 ± 0.41 (1.66) | 11.61 ± 22.37 (5.18) | 2.20 ± 0.53 (2.35) | 4.85 ± 1.28 (5.46) | 2.02 ± 0.72 (2.18) |
| left/right | p | 0.743 | 23/25 | 0 | 18 | 1.72 ± 0.53 (1.94) | 25.63 ± 43.74 (3.83) | 2.00 ± 0.65 (2.16) | 4.45 ± 1.56 (5.21) | 1.75 ± 0.83 (2.03) |
| back/left | p | 0.758 | 25/25 | 0 | 20 | 2.68 ± 1.96 (2.44) | 37.27 ± 64.99 (4.85) | 2.10 ± 0.69 (2.31) | 4.60 ± 1.62 (5.40) | 1.91 ± 0.92 (2.19) |
| back/right | p | 0.737 | 24/25 | 0 | 20 | 2.27 ± 0.64 (2.40) | 29.00 ± 53.75 (5.07) | 2.07 ± 0.77 (2.36) | 4.50 ± 1.76 (5.27) | 1.90 ± 0.91 (2.02) |
| right/left | p | 0.804 | 25/25 | 0 | 20 | 1.77 ± 0.50 (1.78) | 21.26 ± 39.02 (5.45) | 2.06 ± 0.65 (2.23) | 4.53 ± 1.55 (5.04) | 1.85 ± 0.85 (1.96) |
| right/right | p | 0.770 | 23/25 | 0 | 20 | 1.59 ± 0.43 (1.66) | 11.38 ± 21.11 (3.43) | 2.12 ± 0.52 (2.27) | 4.69 ± 1.28 (5.38) | 1.90 ± 0.73 (2.08) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.807 | 17.3 | 5.24 | 2.22 |
| p | normal | 0.757 | 20.7 | 3.88 | 1.49 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.722 | 0.16 | 2.23 ± 1.00 (2.22) | 3.51 | 1.28 |
| p | medium | 16 | 0.809 | 0.70 | 1.25 ± 0.23 (1.26) | 4.03 | 1.58 |
| p | strong | 126 | 0.806 | 0.68 | - | 5.11 | 2.15 |

## Notes

- p: score 0.782, 195/200 kicked, 0 fell; worst sector back (0.747).

# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s3_ctl7_n7.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.781** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 170 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 2.22 ± 2.05 (1.82) |
| Direction error [°] | 16.77 ± 33.01 (5.97) |
| Avg ball speed [m/s] | 2.11 ± 0.75 (2.26) |
| Peak ball speed [m/s] | 4.81 ± 1.66 (5.44) |
| Distance [m] | 2.34 ± 1.20 (2.47) |
| Path length [m] | 2.36 ± 1.21 (2.50) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.809 | 50/50 | 0 | 44 | 1.62 ± 2.02 (1.26) | 11.40 ± 21.28 (5.55) | 2.10 ± 0.69 (2.24) | 4.83 ± 1.56 (5.23) | 2.37 ± 1.22 (2.49) |
| left | p | 0.796 | 50/50 | 0 | 43 | 2.42 ± 2.24 (1.86) | 13.54 ± 24.24 (5.41) | 2.02 ± 0.75 (2.15) | 4.78 ± 1.68 (5.35) | 2.45 ± 1.41 (2.31) |
| back | p | 0.730 | 48/50 | 0 | 42 | 2.77 ± 1.82 (2.53) | 20.09 ± 40.00 (7.15) | 2.24 ± 0.74 (2.40) | 5.09 ± 1.52 (5.78) | 2.46 ± 1.07 (2.81) |
| right | p | 0.791 | 50/50 | 0 | 41 | 2.10 ± 1.91 (1.83) | 22.18 ± 40.76 (5.74) | 2.09 ± 0.79 (2.31) | 4.57 ± 1.82 (5.39) | 2.07 ± 1.02 (2.32) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.790 | 99/100 | 0 | 85 | 2.10 ± 1.69 (1.80) | 18.38 ± 36.47 (5.89) | 2.14 ± 0.74 (2.29) | 4.87 ± 1.66 (5.54) | 2.37 ± 1.17 (2.51) |
| right | p | 0.773 | 99/100 | 0 | 85 | 2.35 ± 2.35 (1.84) | 15.16 ± 29.06 (6.00) | 2.08 ± 0.76 (2.17) | 4.75 ± 1.66 (4.77) | 2.30 ± 1.23 (2.21) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.806 | 25/25 | 0 | 22 | 1.23 ± 0.26 (1.32) | 14.77 ± 27.59 (6.60) | 2.08 ± 0.72 (2.26) | 4.65 ± 1.63 (4.62) | 2.17 ± 0.96 (2.32) |
| forward/right | p | 0.811 | 25/25 | 0 | 22 | 2.02 ± 2.79 (1.20) | 8.03 ± 11.02 (5.02) | 2.12 ± 0.66 (2.18) | 5.00 ± 1.47 (5.45) | 2.57 ± 1.42 (2.68) |
| left/left | p | 0.796 | 25/25 | 0 | 22 | 2.65 ± 2.43 (1.88) | 9.92 ± 16.22 (5.45) | 2.09 ± 0.69 (2.19) | 5.01 ± 1.50 (5.71) | 2.64 ± 1.40 (2.46) |
| left/right | p | 0.796 | 25/25 | 0 | 21 | 2.19 ± 2.01 (1.84) | 17.16 ± 29.75 (5.37) | 1.95 ± 0.80 (2.15) | 4.54 ± 1.81 (4.63) | 2.26 ± 1.40 (2.21) |
| back/left | p | 0.760 | 24/25 | 0 | 21 | 2.31 ± 0.59 (2.53) | 19.85 ± 38.12 (6.89) | 2.27 ± 0.70 (2.50) | 5.15 ± 1.52 (5.78) | 2.55 ± 1.12 (2.81) |
| back/right | p | 0.700 | 24/25 | 0 | 21 | 3.24 ± 2.41 (2.52) | 20.33 ± 41.78 (8.46) | 2.21 ± 0.78 (2.28) | 5.03 ± 1.51 (5.33) | 2.37 ± 1.02 (2.47) |
| right/left | p | 0.796 | 25/25 | 0 | 20 | 2.23 ± 1.96 (1.84) | 29.03 ± 51.46 (4.97) | 2.12 ± 0.82 (2.34) | 4.69 ± 1.90 (5.68) | 2.13 ± 1.08 (2.51) |
| right/right | p | 0.785 | 25/25 | 0 | 21 | 1.97 ± 1.85 (1.82) | 15.33 ± 24.10 (6.51) | 2.06 ± 0.77 (2.17) | 4.45 ± 1.73 (4.33) | 2.01 ± 0.96 (1.93) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.813 | 17.3 | 5.37 | 2.68 |
| p | normal | 0.750 | 16.2 | 4.26 | 1.99 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.704 | 0.18 | 2.26 ± 0.98 (2.08) | 3.79 | 1.54 |
| p | medium | 15 | 0.858 | 0.67 | 1.23 ± 0.30 (1.27) | 4.04 | 1.99 |
| p | strong | 125 | 0.809 | 0.72 | - | 5.40 | 2.77 |

## Notes

- p: score 0.781, 198/200 kicked, 0 fell; worst sector back (0.730).

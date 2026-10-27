# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/r6_u5_75_u0_25.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.797** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 174 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 2.01 ± 1.44 (1.70) |
| Direction error [°] | 12.43 ± 25.47 (4.65) |
| Avg ball speed [m/s] | 2.15 ± 0.58 (2.27) |
| Peak ball speed [m/s] | 4.67 ± 1.39 (5.21) |
| Distance [m] | 1.93 ± 0.75 (2.00) |
| Path length [m] | 1.93 ± 0.75 (2.01) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.813 | 50/50 | 0 | 43 | 1.70 ± 1.83 (1.35) | 8.35 ± 10.89 (3.78) | 2.17 ± 0.63 (2.28) | 4.73 ± 1.51 (5.37) | 1.98 ± 0.82 (2.16) |
| left | p | 0.834 | 50/50 | 0 | 45 | 1.91 ± 1.33 (1.66) | 10.72 ± 22.92 (3.97) | 2.16 ± 0.49 (2.27) | 4.71 ± 1.20 (5.14) | 1.92 ± 0.67 (1.95) |
| back | p | 0.733 | 49/50 | 0 | 41 | 2.72 ± 1.52 (2.58) | 21.50 ± 38.84 (6.94) | 2.12 ± 0.69 (2.34) | 4.64 ± 1.59 (5.32) | 1.93 ± 0.82 (2.08) |
| right | p | 0.810 | 49/50 | 0 | 45 | 1.74 ± 0.39 (1.74) | 9.28 ± 18.55 (3.66) | 2.14 ± 0.48 (2.22) | 4.61 ± 1.22 (4.91) | 1.87 ± 0.66 (1.93) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.792 | 99/100 | 0 | 85 | 1.95 ± 1.25 (1.64) | 13.79 ± 27.44 (4.23) | 2.11 ± 0.61 (2.28) | 4.61 ± 1.46 (5.22) | 1.90 ± 0.78 (2.07) |
| right | p | 0.803 | 99/100 | 0 | 89 | 2.08 ± 1.60 (1.78) | 11.08 ± 23.26 (4.76) | 2.18 ± 0.54 (2.26) | 4.73 ± 1.31 (5.07) | 1.95 ± 0.72 (1.98) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.822 | 25/25 | 0 | 21 | 1.37 ± 0.60 (1.34) | 7.73 ± 9.76 (3.68) | 2.11 ± 0.61 (2.28) | 4.60 ± 1.50 (5.28) | 1.89 ± 0.78 (2.19) |
| forward/right | p | 0.804 | 25/25 | 0 | 22 | 2.03 ± 2.47 (1.38) | 8.96 ± 11.88 (4.03) | 2.22 ± 0.65 (2.24) | 4.87 ± 1.51 (5.44) | 2.07 ± 0.85 (2.14) |
| left/left | p | 0.844 | 25/25 | 0 | 23 | 2.04 ± 1.80 (1.62) | 5.86 ± 5.54 (3.90) | 2.27 ± 0.38 (2.32) | 4.99 ± 0.97 (5.26) | 2.09 ± 0.59 (2.12) |
| left/right | p | 0.823 | 25/25 | 0 | 22 | 1.77 ± 0.50 (1.78) | 15.57 ± 31.19 (4.31) | 2.04 ± 0.55 (2.19) | 4.43 ± 1.34 (4.62) | 1.76 ± 0.72 (1.84) |
| back/left | p | 0.731 | 25/25 | 0 | 20 | 2.54 ± 1.33 (2.56) | 27.92 ± 44.11 (8.32) | 2.01 ± 0.80 (2.22) | 4.39 ± 1.79 (5.17) | 1.81 ± 0.93 (2.07) |
| back/right | p | 0.734 | 24/25 | 0 | 21 | 2.91 ± 1.67 (2.58) | 14.81 ± 31.06 (6.13) | 2.24 ± 0.53 (2.36) | 4.89 ± 1.29 (5.52) | 2.04 ± 0.68 (2.24) |
| right/left | p | 0.770 | 24/25 | 0 | 21 | 1.83 ± 0.40 (1.91) | 13.63 ± 25.21 (3.85) | 2.06 ± 0.56 (2.22) | 4.47 ± 1.39 (4.70) | 1.80 ± 0.74 (1.88) |
| right/right | p | 0.850 | 25/25 | 0 | 24 | 1.65 ± 0.35 (1.58) | 5.11 ± 5.37 (3.66) | 2.21 ± 0.37 (2.21) | 4.76 ± 1.00 (5.01) | 1.93 ± 0.56 (1.95) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.828 | 11.7 | 5.17 | 2.18 |
| p | normal | 0.766 | 13.1 | 4.18 | 1.67 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.718 | 0.11 | 2.47 ± 0.99 (2.37) | 3.83 | 1.46 |
| p | medium | 20 | 0.863 | 0.70 | 1.29 ± 0.17 (1.28) | 4.15 | 1.63 |
| p | strong | 126 | 0.821 | 0.68 | - | 5.12 | 2.17 |

## Notes

- p: score 0.797, 198/200 kicked, 0 fell; worst sector back (0.733).

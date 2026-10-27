# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w5_w3_75_s8_25.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.848** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.88 ± 0.57 (1.84) |
| Direction error [°] | 6.00 ± 10.43 (4.73) |
| Avg ball speed [m/s] | 2.28 ± 0.42 (2.39) |
| Peak ball speed [m/s] | 5.00 ± 1.11 (5.55) |
| Distance [m] | 2.13 ± 0.71 (2.29) |
| Path length [m] | 2.14 ± 0.71 (2.31) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.875 | 50/50 | 0 | 48 | 1.29 ± 0.23 (1.30) | 4.64 ± 3.82 (3.18) | 2.17 ± 0.43 (2.37) | 4.83 ± 1.15 (5.49) | 1.97 ± 0.72 (2.20) |
| left | p | 0.869 | 50/50 | 0 | 49 | 1.81 ± 0.30 (1.79) | 5.15 ± 3.81 (4.03) | 2.35 ± 0.38 (2.48) | 5.17 ± 1.03 (5.70) | 2.24 ± 0.68 (2.38) |
| back | p | 0.794 | 50/50 | 0 | 49 | 2.60 ± 0.42 (2.57) | 8.79 ± 19.61 (6.12) | 2.34 ± 0.47 (2.43) | 4.99 ± 1.21 (5.57) | 2.21 ± 0.76 (2.40) |
| right | p | 0.854 | 50/50 | 0 | 50 | 1.80 ± 0.33 (1.88) | 5.42 ± 3.27 (5.06) | 2.27 ± 0.37 (2.38) | 5.01 ± 1.01 (5.53) | 2.12 ± 0.64 (2.33) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.847 | 100/100 | 0 | 96 | 1.86 ± 0.55 (1.82) | 7.04 ± 14.30 (5.04) | 2.28 ± 0.45 (2.40) | 5.00 ± 1.17 (5.60) | 2.14 ± 0.74 (2.36) |
| right | p | 0.848 | 100/100 | 0 | 100 | 1.89 ± 0.59 (1.88) | 4.96 ± 3.30 (4.28) | 2.29 ± 0.39 (2.39) | 5.00 ± 1.05 (5.52) | 2.13 ± 0.68 (2.25) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.874 | 25/25 | 0 | 23 | 1.29 ± 0.25 (1.30) | 4.93 ± 4.22 (3.18) | 2.17 ± 0.39 (2.36) | 4.80 ± 1.07 (5.20) | 1.96 ± 0.68 (1.94) |
| forward/right | p | 0.875 | 25/25 | 0 | 25 | 1.29 ± 0.21 (1.28) | 4.35 ± 3.34 (3.32) | 2.17 ± 0.47 (2.38) | 4.85 ± 1.23 (5.56) | 1.98 ± 0.76 (2.23) |
| left/left | p | 0.869 | 25/25 | 0 | 24 | 1.70 ± 0.27 (1.76) | 5.74 ± 4.41 (4.14) | 2.41 ± 0.37 (2.51) | 5.29 ± 1.03 (5.78) | 2.33 ± 0.69 (2.49) |
| left/right | p | 0.868 | 25/25 | 0 | 25 | 1.92 ± 0.30 (2.00) | 4.55 ± 2.98 (3.31) | 2.30 ± 0.38 (2.42) | 5.05 ± 1.02 (5.63) | 2.14 ± 0.66 (2.25) |
| back/left | p | 0.801 | 25/25 | 0 | 24 | 2.57 ± 0.39 (2.46) | 11.70 ± 27.21 (5.86) | 2.32 ± 0.58 (2.47) | 4.97 ± 1.39 (5.72) | 2.23 ± 0.84 (2.47) |
| back/right | p | 0.787 | 25/25 | 0 | 25 | 2.63 ± 0.44 (2.60) | 5.88 ± 3.40 (6.38) | 2.35 ± 0.34 (2.38) | 5.01 ± 0.99 (5.50) | 2.20 ± 0.66 (2.30) |
| right/left | p | 0.845 | 25/25 | 0 | 25 | 1.90 ± 0.28 (1.98) | 5.80 ± 3.22 (5.46) | 2.20 ± 0.39 (2.35) | 4.95 ± 1.09 (5.55) | 2.04 ± 0.68 (2.13) |
| right/right | p | 0.862 | 25/25 | 0 | 25 | 1.71 ± 0.35 (1.70) | 5.04 ± 3.26 (4.84) | 2.34 ± 0.34 (2.46) | 5.07 ± 0.92 (5.50) | 2.19 ± 0.60 (2.36) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.884 | 7.0 | 5.76 | 2.60 |
| p | normal | 0.812 | 5.0 | 4.24 | 1.67 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.756 | 0.13 | 2.37 ± 0.70 (2.26) | 3.74 | 1.36 |
| p | medium | 18 | 0.889 | 0.78 | 1.17 ± 0.17 (1.21) | 3.75 | 1.36 |
| p | strong | 124 | 0.885 | 0.77 | - | 5.77 | 2.61 |

## Notes

- p: score 0.848, 200/200 kicked, 0 fell; worst sector back (0.794).

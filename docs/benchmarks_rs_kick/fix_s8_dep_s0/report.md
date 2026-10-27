# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.849** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 192 |
| Weak kicks (< 0.3 m) | 5 |
| Time to kick [s] | 1.81 ± 0.54 (1.74) |
| Direction error [°] | 7.36 ± 16.11 (5.14) |
| Avg ball speed [m/s] | 2.60 ± 0.58 (2.77) |
| Peak ball speed [m/s] | 5.43 ± 1.33 (6.03) |
| Distance [m] | 2.74 ± 0.93 (3.10) |
| Path length [m] | 2.75 ± 0.93 (3.12) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.855 | 50/50 | 0 | 49 | 1.26 ± 0.25 (1.29) | 5.21 ± 7.53 (3.96) | 2.46 ± 0.51 (2.49) | 5.16 ± 1.21 (5.44) | 2.48 ± 0.83 (2.47) |
| left | p | 0.875 | 50/50 | 0 | 48 | 1.76 ± 0.36 (1.79) | 5.88 ± 4.14 (4.86) | 2.66 ± 0.54 (2.77) | 5.58 ± 1.19 (6.04) | 2.84 ± 0.84 (3.14) |
| back | p | 0.813 | 50/50 | 0 | 47 | 2.48 ± 0.32 (2.45) | 12.82 ± 30.11 (6.91) | 2.65 ± 0.75 (2.96) | 5.55 ± 1.70 (6.37) | 2.92 ± 1.12 (3.42) |
| right | p | 0.854 | 50/50 | 0 | 48 | 1.75 ± 0.34 (1.72) | 5.51 ± 4.18 (4.89) | 2.62 ± 0.46 (2.79) | 5.43 ± 1.10 (6.09) | 2.70 ± 0.82 (3.10) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.847 | 100/100 | 0 | 94 | 1.82 ± 0.55 (1.76) | 7.97 ± 16.19 (5.29) | 2.62 ± 0.55 (2.78) | 5.47 ± 1.29 (6.14) | 2.77 ± 0.92 (3.21) |
| right | p | 0.852 | 100/100 | 0 | 98 | 1.80 ± 0.52 (1.72) | 6.74 ± 16.01 (4.70) | 2.58 ± 0.61 (2.76) | 5.39 ± 1.37 (5.91) | 2.70 ± 0.93 (2.94) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.863 | 25/25 | 0 | 24 | 1.26 ± 0.24 (1.26) | 5.60 ± 10.29 (3.99) | 2.44 ± 0.61 (2.54) | 5.11 ± 1.41 (5.45) | 2.48 ± 0.92 (2.48) |
| forward/right | p | 0.846 | 25/25 | 0 | 25 | 1.27 ± 0.25 (1.30) | 4.83 ± 2.67 (3.92) | 2.49 ± 0.38 (2.41) | 5.21 ± 0.96 (5.29) | 2.48 ± 0.72 (2.43) |
| left/left | p | 0.863 | 25/25 | 0 | 23 | 1.66 ± 0.36 (1.76) | 7.04 ± 4.43 (6.22) | 2.67 ± 0.44 (2.78) | 5.56 ± 1.01 (6.12) | 2.82 ± 0.81 (3.16) |
| left/right | p | 0.887 | 25/25 | 0 | 25 | 1.85 ± 0.33 (1.92) | 4.72 ± 3.45 (3.95) | 2.66 ± 0.62 (2.77) | 5.60 ± 1.35 (5.98) | 2.85 ± 0.88 (3.09) |
| back/left | p | 0.812 | 25/25 | 0 | 24 | 2.51 ± 0.34 (2.52) | 12.36 ± 29.54 (6.77) | 2.69 ± 0.63 (2.90) | 5.66 ± 1.50 (6.43) | 2.98 ± 1.06 (3.44) |
| back/right | p | 0.815 | 25/25 | 0 | 23 | 2.45 ± 0.29 (2.36) | 13.28 ± 30.67 (6.92) | 2.61 ± 0.86 (2.98) | 5.44 ± 1.87 (6.33) | 2.86 ± 1.17 (3.38) |
| right/left | p | 0.848 | 25/25 | 0 | 23 | 1.85 ± 0.32 (1.76) | 6.88 ± 4.77 (6.44) | 2.68 ± 0.45 (2.85) | 5.57 ± 1.09 (6.16) | 2.79 ± 0.81 (3.28) |
| right/right | p | 0.861 | 25/25 | 0 | 25 | 1.65 ± 0.34 (1.70) | 4.14 ± 2.92 (3.34) | 2.56 ± 0.46 (2.59) | 5.29 ± 1.09 (5.79) | 2.61 ± 0.82 (2.81) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.897 | 5.8 | 6.31 | 3.37 |
| p | normal | 0.802 | 8.9 | 4.55 | 2.10 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.747 | 0.06 | 2.51 ± 1.02 (2.38) | 3.91 | 1.64 |
| p | medium | 16 | 0.862 | 0.65 | 1.24 ± 0.32 (1.29) | 4.01 | 1.72 |
| p | strong | 126 | 0.895 | 0.84 | - | 6.31 | 3.37 |

## Notes

- p: score 0.849, 200/200 kicked, 0 fell; worst sector back (0.813).

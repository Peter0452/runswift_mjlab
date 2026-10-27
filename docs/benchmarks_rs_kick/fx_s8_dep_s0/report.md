# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.853** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.81 ± 0.54 (1.76) |
| Direction error [°] | 6.12 ± 15.74 (4.01) |
| Avg ball speed [m/s] | 2.07 ± 0.35 (2.09) |
| Peak ball speed [m/s] | 5.24 ± 0.94 (5.47) |
| Distance [m] | 2.35 ± 0.60 (2.31) |
| Path length [m] | 2.36 ± 0.60 (2.32) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.846 | 50/50 | 0 | 50 | 1.26 ± 0.24 (1.30) | 5.04 ± 3.38 (4.38) | 2.02 ± 0.32 (2.03) | 5.12 ± 0.85 (5.18) | 2.24 ± 0.57 (2.09) |
| left | p | 0.885 | 50/50 | 0 | 50 | 1.75 ± 0.35 (1.78) | 4.32 ± 3.19 (3.66) | 2.10 ± 0.26 (2.09) | 5.43 ± 0.78 (5.68) | 2.45 ± 0.49 (2.55) |
| back | p | 0.824 | 50/50 | 0 | 48 | 2.48 ± 0.31 (2.42) | 10.51 ± 30.59 (3.45) | 2.10 ± 0.46 (2.17) | 5.25 ± 1.22 (5.57) | 2.41 ± 0.73 (2.41) |
| right | p | 0.854 | 50/50 | 0 | 50 | 1.76 ± 0.34 (1.73) | 4.63 ± 2.83 (4.41) | 2.06 ± 0.31 (2.08) | 5.18 ± 0.83 (5.51) | 2.29 ± 0.54 (2.32) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.852 | 100/100 | 0 | 99 | 1.82 ± 0.55 (1.77) | 6.45 ± 15.97 (4.44) | 2.06 ± 0.38 (2.13) | 5.24 ± 1.00 (5.50) | 2.36 ± 0.64 (2.39) |
| right | p | 0.853 | 100/100 | 0 | 99 | 1.80 ± 0.53 (1.74) | 5.80 ± 15.50 (3.35) | 2.08 ± 0.32 (2.09) | 5.24 ± 0.89 (5.46) | 2.33 ± 0.55 (2.23) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.851 | 25/25 | 0 | 25 | 1.26 ± 0.24 (1.28) | 5.39 ± 3.29 (4.64) | 2.05 ± 0.38 (2.15) | 5.17 ± 0.90 (5.29) | 2.28 ± 0.62 (2.08) |
| forward/right | p | 0.841 | 25/25 | 0 | 25 | 1.26 ± 0.25 (1.30) | 4.69 ± 3.43 (4.01) | 1.98 ± 0.23 (1.99) | 5.07 ± 0.79 (4.92) | 2.19 ± 0.51 (2.09) |
| left/left | p | 0.879 | 25/25 | 0 | 25 | 1.64 ± 0.35 (1.76) | 4.76 ± 3.74 (2.79) | 2.08 ± 0.29 (2.05) | 5.38 ± 0.84 (5.67) | 2.45 ± 0.55 (2.56) |
| left/right | p | 0.891 | 25/25 | 0 | 25 | 1.85 ± 0.32 (1.90) | 3.88 ± 2.45 (3.96) | 2.11 ± 0.23 (2.09) | 5.47 ± 0.70 (5.70) | 2.45 ± 0.42 (2.54) |
| back/left | p | 0.815 | 25/25 | 0 | 24 | 2.52 ± 0.31 (2.46) | 11.13 ± 31.00 (5.07) | 2.08 ± 0.46 (2.18) | 5.22 ± 1.27 (5.45) | 2.42 ± 0.76 (2.44) |
| back/right | p | 0.834 | 25/25 | 0 | 24 | 2.45 ± 0.31 (2.38) | 9.88 ± 30.16 (2.60) | 2.12 ± 0.45 (2.17) | 5.28 ± 1.16 (5.61) | 2.40 ± 0.69 (2.26) |
| right/left | p | 0.863 | 25/25 | 0 | 25 | 1.86 ± 0.30 (1.80) | 4.51 ± 2.27 (4.49) | 2.04 ± 0.34 (2.01) | 5.21 ± 0.89 (5.57) | 2.28 ± 0.58 (2.33) |
| right/right | p | 0.845 | 25/25 | 0 | 25 | 1.65 ± 0.34 (1.70) | 4.75 ± 3.30 (3.83) | 2.09 ± 0.28 (2.11) | 5.14 ± 0.77 (5.43) | 2.29 ± 0.50 (2.22) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.895 | 4.8 | 5.82 | 2.67 |
| p | normal | 0.811 | 7.5 | 4.66 | 2.02 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.757 | 0.06 | 2.66 ± 0.95 (2.43) | 4.17 | 1.73 |
| p | medium | 16 | 0.859 | 0.64 | 1.36 ± 0.17 (1.37) | 4.42 | 1.92 |
| p | strong | 126 | 0.896 | 0.78 | - | 5.84 | 2.69 |

## Notes

- p: score 0.853, 200/200 kicked, 0 fell; worst sector back (0.824).

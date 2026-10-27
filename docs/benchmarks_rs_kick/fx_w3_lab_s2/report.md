# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w3_u4_tail.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.859** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 5 |
| Time to kick [s] | 1.59 ± 0.51 (1.58) |
| Direction error [°] | 8.07 ± 21.67 (5.11) |
| Avg ball speed [m/s] | 2.01 ± 0.56 (2.22) |
| Peak ball speed [m/s] | 4.30 ± 1.27 (4.86) |
| Distance [m] | 1.81 ± 0.77 (2.06) |
| Path length [m] | 1.81 ± 0.78 (2.07) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.872 | 50/50 | 0 | 50 | 1.07 ± 0.25 (1.07) | 4.72 ± 2.83 (4.70) | 1.95 ± 0.50 (2.08) | 4.21 ± 1.15 (4.66) | 1.70 ± 0.73 (1.92) |
| left | p | 0.868 | 50/50 | 0 | 50 | 1.54 ± 0.37 (1.56) | 4.99 ± 3.03 (4.47) | 2.04 ± 0.48 (2.23) | 4.34 ± 1.11 (4.82) | 1.82 ± 0.72 (2.03) |
| back | p | 0.819 | 50/50 | 0 | 46 | 2.20 ± 0.31 (2.21) | 17.65 ± 41.58 (6.02) | 1.99 ± 0.72 (2.34) | 4.24 ± 1.61 (5.12) | 1.85 ± 0.88 (2.25) |
| right | p | 0.876 | 50/50 | 0 | 50 | 1.55 ± 0.33 (1.60) | 4.92 ± 3.29 (4.41) | 2.07 ± 0.50 (2.23) | 4.41 ± 1.14 (4.88) | 1.86 ± 0.74 (2.13) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.866 | 100/100 | 0 | 98 | 1.58 ± 0.50 (1.60) | 8.01 ± 22.45 (5.12) | 2.03 ± 0.58 (2.28) | 4.35 ± 1.31 (4.98) | 1.85 ± 0.79 (2.13) |
| right | p | 0.852 | 100/100 | 0 | 98 | 1.60 ± 0.52 (1.56) | 8.13 ± 20.87 (5.09) | 1.99 ± 0.54 (2.18) | 4.25 ± 1.23 (4.78) | 1.76 ± 0.75 (1.98) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.869 | 25/25 | 0 | 25 | 1.07 ± 0.23 (1.10) | 4.46 ± 2.66 (4.38) | 1.91 ± 0.48 (1.99) | 4.11 ± 1.13 (4.38) | 1.65 ± 0.71 (1.86) |
| forward/right | p | 0.876 | 25/25 | 0 | 25 | 1.08 ± 0.26 (1.00) | 4.99 ± 2.97 (5.20) | 1.99 ± 0.51 (2.15) | 4.31 ± 1.16 (4.80) | 1.75 ± 0.74 (1.97) |
| left/left | p | 0.877 | 25/25 | 0 | 25 | 1.42 ± 0.33 (1.44) | 5.07 ± 3.08 (5.02) | 2.02 ± 0.53 (2.24) | 4.32 ± 1.19 (4.82) | 1.80 ± 0.76 (1.99) |
| left/right | p | 0.860 | 25/25 | 0 | 25 | 1.66 ± 0.36 (1.62) | 4.92 ± 2.97 (3.93) | 2.05 ± 0.43 (2.22) | 4.36 ± 1.03 (4.82) | 1.83 ± 0.68 (2.06) |
| back/left | p | 0.830 | 25/25 | 0 | 23 | 2.18 ± 0.28 (2.22) | 17.97 ± 43.09 (6.00) | 2.03 ± 0.78 (2.36) | 4.37 ± 1.72 (5.15) | 1.95 ± 0.90 (2.28) |
| back/right | p | 0.807 | 25/25 | 0 | 23 | 2.22 ± 0.34 (2.14) | 17.33 ± 40.00 (6.06) | 1.94 ± 0.66 (2.25) | 4.11 ± 1.47 (4.76) | 1.74 ± 0.83 (1.92) |
| right/left | p | 0.887 | 25/25 | 0 | 25 | 1.66 ± 0.31 (1.66) | 4.55 ± 3.14 (3.56) | 2.17 ± 0.45 (2.29) | 4.62 ± 1.05 (5.09) | 2.00 ± 0.71 (2.16) |
| right/right | p | 0.864 | 25/25 | 0 | 25 | 1.44 ± 0.32 (1.52) | 5.28 ± 3.39 (4.81) | 1.98 ± 0.53 (2.07) | 4.20 ± 1.19 (4.60) | 1.72 ± 0.75 (2.02) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.879 | 6.8 | 5.11 | 2.31 |
| p | normal | 0.838 | 9.4 | 3.49 | 1.30 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.807 | 0.34 | 1.80 ± 0.66 (1.67) | 2.95 | 0.95 |
| p | medium | 15 | 0.906 | 0.81 | 0.93 ± 0.28 (0.96) | 3.01 | 0.99 |
| p | strong | 125 | 0.878 | 0.68 | - | 5.10 | 2.32 |

## Notes

- p: score 0.859, 200/200 kicked, 0 fell; worst sector back (0.819).

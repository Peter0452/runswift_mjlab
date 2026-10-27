# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.847** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.57 ± 0.52 (1.51) |
| Direction error [°] | 6.13 ± 11.59 (5.08) |
| Avg ball speed [m/s] | 2.15 ± 0.41 (2.18) |
| Peak ball speed [m/s] | 4.58 ± 0.93 (4.77) |
| Distance [m] | 2.00 ± 0.61 (2.06) |
| Path length [m] | 2.01 ± 0.61 (2.07) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.835 | 50/50 | 0 | 50 | 1.01 ± 0.22 (1.02) | 4.95 ± 3.31 (3.51) | 1.88 ± 0.26 (1.83) | 4.01 ± 0.62 (3.87) | 1.58 ± 0.41 (1.45) |
| left | p | 0.867 | 50/50 | 0 | 49 | 1.52 ± 0.33 (1.54) | 5.76 ± 3.70 (5.35) | 2.29 ± 0.33 (2.38) | 4.88 ± 0.75 (5.16) | 2.20 ± 0.54 (2.29) |
| back | p | 0.846 | 50/50 | 0 | 49 | 2.23 ± 0.27 (2.19) | 7.87 ± 22.24 (4.95) | 2.24 ± 0.52 (2.40) | 4.76 ± 1.17 (5.15) | 2.17 ± 0.69 (2.41) |
| right | p | 0.841 | 50/50 | 0 | 49 | 1.52 ± 0.34 (1.48) | 5.94 ± 3.68 (5.51) | 2.20 ± 0.34 (2.25) | 4.67 ± 0.81 (4.99) | 2.05 ± 0.55 (2.20) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.847 | 100/100 | 0 | 97 | 1.56 ± 0.51 (1.51) | 7.05 ± 16.02 (5.08) | 2.15 ± 0.41 (2.22) | 4.58 ± 0.94 (4.84) | 2.00 ± 0.62 (2.12) |
| right | p | 0.847 | 100/100 | 0 | 100 | 1.58 ± 0.53 (1.50) | 5.22 ± 3.25 (5.10) | 2.15 ± 0.41 (2.16) | 4.57 ± 0.92 (4.69) | 1.99 ± 0.61 (2.00) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.833 | 25/25 | 0 | 25 | 1.02 ± 0.22 (1.02) | 5.62 ± 3.43 (5.37) | 1.89 ± 0.29 (1.87) | 4.03 ± 0.71 (3.88) | 1.61 ± 0.48 (1.54) |
| forward/right | p | 0.837 | 25/25 | 0 | 25 | 1.01 ± 0.22 (1.02) | 4.28 ± 3.04 (3.14) | 1.87 ± 0.23 (1.82) | 3.98 ± 0.53 (3.87) | 1.55 ± 0.33 (1.44) |
| left/left | p | 0.857 | 25/25 | 0 | 24 | 1.43 ± 0.32 (1.52) | 6.40 ± 4.37 (5.57) | 2.24 ± 0.32 (2.30) | 4.76 ± 0.76 (4.97) | 2.12 ± 0.53 (2.25) |
| left/right | p | 0.876 | 25/25 | 0 | 25 | 1.62 ± 0.31 (1.64) | 5.13 ± 2.73 (4.63) | 2.34 ± 0.32 (2.49) | 4.99 ± 0.72 (5.24) | 2.28 ± 0.53 (2.30) |
| back/left | p | 0.851 | 25/25 | 0 | 24 | 2.20 ± 0.28 (2.18) | 10.29 ± 31.08 (4.30) | 2.25 ± 0.51 (2.44) | 4.78 ± 1.17 (5.19) | 2.18 ± 0.70 (2.44) |
| back/right | p | 0.841 | 25/25 | 0 | 25 | 2.26 ± 0.25 (2.20) | 5.44 ± 3.46 (5.39) | 2.24 ± 0.53 (2.36) | 4.73 ± 1.18 (5.15) | 2.15 ± 0.69 (2.37) |
| right/left | p | 0.847 | 25/25 | 0 | 24 | 1.60 ± 0.32 (1.58) | 5.87 ± 3.88 (5.35) | 2.24 ± 0.34 (2.28) | 4.76 ± 0.82 (5.00) | 2.10 ± 0.56 (2.23) |
| right/right | p | 0.835 | 25/25 | 0 | 25 | 1.43 ± 0.33 (1.44) | 6.01 ± 3.47 (6.37) | 2.16 ± 0.33 (2.19) | 4.58 ± 0.80 (4.76) | 1.99 ± 0.54 (2.15) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.885 | 4.7 | 5.10 | 2.34 |
| p | normal | 0.810 | 7.5 | 4.06 | 1.65 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.759 | 0.11 | 2.29 ± 0.79 (2.16) | 3.61 | 1.36 |
| p | medium | 16 | 0.880 | 0.81 | 1.15 ± 0.16 (1.16) | 3.72 | 1.40 |
| p | strong | 126 | 0.884 | 0.68 | - | 5.13 | 2.37 |

## Notes

- p: score 0.847, 200/200 kicked, 0 fell; worst sector forward (0.835).

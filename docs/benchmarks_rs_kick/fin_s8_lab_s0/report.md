# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.847** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.56 ± 0.51 (1.48) |
| Direction error [°] | 6.87 ± 14.05 (5.00) |
| Avg ball speed [m/s] | 2.17 ± 0.41 (2.20) |
| Peak ball speed [m/s] | 4.61 ± 0.94 (4.82) |
| Distance [m] | 2.02 ± 0.64 (2.03) |
| Path length [m] | 2.03 ± 0.64 (2.04) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.829 | 50/50 | 0 | 50 | 1.02 ± 0.22 (1.03) | 6.07 ± 3.45 (6.32) | 1.94 ± 0.29 (1.89) | 4.10 ± 0.70 (3.87) | 1.64 ± 0.48 (1.53) |
| left | p | 0.867 | 50/50 | 0 | 50 | 1.50 ± 0.34 (1.49) | 5.42 ± 3.70 (4.63) | 2.24 ± 0.33 (2.31) | 4.79 ± 0.80 (5.08) | 2.15 ± 0.58 (2.28) |
| back | p | 0.847 | 50/50 | 0 | 48 | 2.20 ± 0.25 (2.18) | 10.26 ± 27.10 (4.66) | 2.28 ± 0.53 (2.44) | 4.84 ± 1.21 (5.31) | 2.23 ± 0.76 (2.49) |
| right | p | 0.844 | 50/50 | 0 | 50 | 1.50 ± 0.34 (1.46) | 5.75 ± 3.77 (4.62) | 2.22 ± 0.34 (2.33) | 4.69 ± 0.79 (5.03) | 2.06 ± 0.55 (2.23) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.849 | 100/100 | 0 | 99 | 1.56 ± 0.51 (1.47) | 6.82 ± 14.57 (4.88) | 2.16 ± 0.39 (2.20) | 4.59 ± 0.92 (4.85) | 2.01 ± 0.63 (2.09) |
| right | p | 0.844 | 100/100 | 0 | 99 | 1.55 ± 0.51 (1.48) | 6.93 ± 13.52 (5.09) | 2.18 ± 0.43 (2.22) | 4.62 ± 0.97 (4.79) | 2.03 ± 0.65 (2.01) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.832 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.06) | 6.21 ± 3.42 (6.38) | 1.95 ± 0.26 (1.92) | 4.15 ± 0.68 (3.96) | 1.67 ± 0.47 (1.55) |
| forward/right | p | 0.826 | 25/25 | 0 | 25 | 1.01 ± 0.22 (1.02) | 5.93 ± 3.49 (5.52) | 1.92 ± 0.32 (1.88) | 4.06 ± 0.71 (3.85) | 1.61 ± 0.49 (1.44) |
| left/left | p | 0.861 | 25/25 | 0 | 25 | 1.39 ± 0.33 (1.46) | 5.40 ± 3.74 (4.53) | 2.15 ± 0.29 (2.17) | 4.59 ± 0.72 (4.82) | 2.00 ± 0.52 (2.10) |
| left/right | p | 0.873 | 25/25 | 0 | 25 | 1.61 ± 0.32 (1.62) | 5.45 ± 3.66 (4.93) | 2.34 ± 0.34 (2.46) | 4.99 ± 0.82 (5.28) | 2.29 ± 0.60 (2.52) |
| back/left | p | 0.847 | 25/25 | 0 | 24 | 2.22 ± 0.26 (2.18) | 10.31 ± 28.14 (4.76) | 2.31 ± 0.51 (2.45) | 4.87 ± 1.18 (5.33) | 2.26 ± 0.75 (2.49) |
| back/right | p | 0.847 | 25/25 | 0 | 24 | 2.18 ± 0.24 (2.18) | 10.20 ± 26.02 (4.55) | 2.26 ± 0.55 (2.42) | 4.81 ± 1.23 (5.28) | 2.21 ± 0.76 (2.40) |
| right/left | p | 0.855 | 25/25 | 0 | 25 | 1.59 ± 0.32 (1.58) | 5.35 ± 3.75 (4.18) | 2.24 ± 0.34 (2.35) | 4.76 ± 0.83 (5.16) | 2.11 ± 0.56 (2.35) |
| right/right | p | 0.833 | 25/25 | 0 | 25 | 1.41 ± 0.34 (1.46) | 6.14 ± 3.74 (5.51) | 2.20 ± 0.33 (2.23) | 4.63 ± 0.75 (4.84) | 2.02 ± 0.52 (2.18) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.882 | 5.1 | 5.15 | 2.38 |
| p | normal | 0.812 | 8.6 | 4.07 | 1.67 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.755 | 0.12 | 2.29 ± 0.82 (2.17) | 3.59 | 1.35 |
| p | medium | 16 | 0.884 | 0.81 | 1.16 ± 0.15 (1.18) | 3.76 | 1.44 |
| p | strong | 126 | 0.884 | 0.69 | - | 5.18 | 2.41 |

## Notes

- p: score 0.847, 200/200 kicked, 0 fell; worst sector forward (0.829).

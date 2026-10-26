# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s7_ctl7_n7_n5b_n1.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.801** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 175 |
| Weak kicks (< 0.3 m) | 13 |
| Time to kick [s] | 1.96 ± 1.39 (1.68) |
| Direction error [°] | 12.72 ± 26.32 (5.20) |
| Avg ball speed [m/s] | 2.24 ± 0.61 (2.36) |
| Peak ball speed [m/s] | 4.79 ± 1.42 (5.36) |
| Distance [m] | 2.10 ± 0.84 (2.22) |
| Path length [m] | 2.11 ± 0.84 (2.23) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.822 | 50/50 | 0 | 43 | 1.58 ± 1.57 (1.31) | 8.35 ± 13.05 (3.43) | 2.14 ± 0.69 (2.29) | 4.65 ± 1.58 (5.08) | 1.99 ± 0.88 (2.07) |
| left | p | 0.825 | 50/50 | 0 | 44 | 1.89 ± 1.49 (1.62) | 12.86 ± 24.98 (5.04) | 2.20 ± 0.59 (2.35) | 4.70 ± 1.39 (5.18) | 2.05 ± 0.82 (2.20) |
| back | p | 0.758 | 49/50 | 0 | 44 | 2.68 ± 1.49 (2.52) | 19.47 ± 40.24 (6.32) | 2.38 ± 0.61 (2.49) | 5.07 ± 1.37 (5.56) | 2.32 ± 0.87 (2.51) |
| right | p | 0.801 | 49/50 | 0 | 44 | 1.71 ± 0.39 (1.74) | 10.28 ± 17.28 (5.60) | 2.23 ± 0.51 (2.34) | 4.73 ± 1.26 (4.72) | 2.04 ± 0.75 (1.93) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.796 | 99/100 | 0 | 87 | 1.89 ± 1.26 (1.60) | 14.71 ± 29.37 (6.22) | 2.21 ± 0.66 (2.37) | 4.74 ± 1.52 (5.36) | 2.08 ± 0.89 (2.20) |
| right | p | 0.806 | 99/100 | 0 | 88 | 2.04 ± 1.52 (1.76) | 10.72 ± 22.69 (4.55) | 2.27 ± 0.55 (2.36) | 4.84 ± 1.30 (5.36) | 2.12 ± 0.79 (2.24) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.839 | 25/25 | 0 | 22 | 1.26 ± 0.31 (1.28) | 7.86 ± 11.88 (4.13) | 2.13 ± 0.71 (2.43) | 4.64 ± 1.61 (5.07) | 2.00 ± 0.89 (2.21) |
| forward/right | p | 0.804 | 25/25 | 0 | 21 | 1.91 ± 2.15 (1.32) | 8.84 ± 14.10 (2.72) | 2.15 ± 0.67 (2.22) | 4.66 ± 1.54 (5.09) | 1.99 ± 0.87 (1.92) |
| left/left | p | 0.826 | 25/25 | 0 | 23 | 2.04 ± 2.03 (1.58) | 9.96 ± 17.16 (6.22) | 2.30 ± 0.57 (2.42) | 4.93 ± 1.35 (5.59) | 2.21 ± 0.79 (2.47) |
| left/right | p | 0.824 | 25/25 | 0 | 21 | 1.74 ± 0.49 (1.82) | 15.76 ± 30.60 (4.55) | 2.10 ± 0.59 (2.29) | 4.48 ± 1.39 (4.40) | 1.90 ± 0.82 (1.80) |
| back/left | p | 0.757 | 25/25 | 0 | 21 | 2.46 ± 1.06 (2.52) | 26.92 ± 47.31 (7.39) | 2.26 ± 0.74 (2.49) | 4.81 ± 1.65 (5.43) | 2.17 ± 1.01 (2.19) |
| back/right | p | 0.759 | 24/25 | 0 | 23 | 2.91 ± 1.80 (2.53) | 11.72 ± 29.28 (5.44) | 2.52 ± 0.38 (2.49) | 5.36 ± 0.92 (5.61) | 2.47 ± 0.67 (2.59) |
| right/left | p | 0.764 | 24/25 | 0 | 21 | 1.81 ± 0.40 (1.93) | 14.07 ± 23.36 (6.52) | 2.15 ± 0.59 (2.31) | 4.58 ± 1.42 (4.63) | 1.94 ± 0.81 (1.92) |
| right/right | p | 0.837 | 25/25 | 0 | 23 | 1.62 ± 0.35 (1.54) | 6.63 ± 5.88 (4.87) | 2.31 ± 0.40 (2.39) | 4.87 ± 1.06 (5.36) | 2.14 ± 0.67 (2.29) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.828 | 12.8 | 5.26 | 2.40 |
| p | normal | 0.775 | 12.7 | 4.31 | 1.80 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.727 | 0.11 | 2.57 ± 0.98 (2.38) | 3.95 | 1.55 |
| p | medium | 20 | 0.875 | 0.71 | 1.29 ± 0.15 (1.29) | 4.14 | 1.67 |
| p | strong | 126 | 0.822 | 0.70 | - | 5.25 | 2.40 |

## Notes

- p: score 0.801, 198/200 kicked, 0 fell; worst sector back (0.758).

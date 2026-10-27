# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.782** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 165 |
| Weak kicks (< 0.3 m) | 14 |
| Time to kick [s] | 2.12 ± 1.86 (1.74) |
| Direction error [°] | 19.67 ± 40.18 (5.29) |
| Avg ball speed [m/s] | 2.10 ± 0.65 (2.29) |
| Peak ball speed [m/s] | 4.52 ± 1.51 (5.06) |
| Distance [m] | 1.88 ± 0.83 (1.99) |
| Path length [m] | 1.89 ± 0.83 (2.01) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.785 | 50/50 | 0 | 41 | 1.92 ± 2.35 (1.36) | 8.82 ± 10.83 (5.35) | 2.08 ± 0.63 (2.16) | 4.47 ± 1.47 (4.35) | 1.83 ± 0.83 (1.79) |
| left | p | 0.806 | 49/50 | 0 | 42 | 1.85 ± 1.48 (1.76) | 18.47 ± 35.25 (5.19) | 2.13 ± 0.60 (2.30) | 4.61 ± 1.41 (5.25) | 1.92 ± 0.79 (2.08) |
| back | p | 0.743 | 50/50 | 0 | 41 | 2.64 ± 1.44 (2.52) | 32.42 ± 58.98 (6.95) | 2.11 ± 0.76 (2.38) | 4.51 ± 1.71 (5.25) | 1.95 ± 0.89 (2.22) |
| right | p | 0.795 | 50/50 | 0 | 41 | 2.05 ± 1.93 (1.74) | 18.94 ± 36.45 (4.79) | 2.07 ± 0.60 (2.23) | 4.47 ± 1.45 (4.98) | 1.82 ± 0.77 (1.94) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.807 | 100/100 | 0 | 85 | 1.88 ± 1.23 (1.69) | 18.81 ± 40.63 (5.36) | 2.16 ± 0.59 (2.32) | 4.62 ± 1.39 (5.19) | 1.94 ± 0.78 (2.05) |
| right | p | 0.757 | 99/100 | 0 | 80 | 2.36 ± 2.31 (1.76) | 20.54 ± 39.69 (5.27) | 2.04 ± 0.70 (2.22) | 4.41 ± 1.63 (4.54) | 1.82 ± 0.87 (1.86) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.822 | 25/25 | 0 | 21 | 1.69 ± 2.10 (1.30) | 7.37 ± 11.32 (2.84) | 2.26 ± 0.47 (2.34) | 4.84 ± 1.14 (5.45) | 2.04 ± 0.73 (2.06) |
| forward/right | p | 0.747 | 25/25 | 0 | 20 | 2.14 ± 2.55 (1.36) | 10.28 ± 10.11 (7.14) | 1.90 ± 0.71 (2.00) | 4.11 ± 1.66 (4.08) | 1.62 ± 0.87 (1.65) |
| left/left | p | 0.859 | 25/25 | 0 | 23 | 1.58 ± 0.41 (1.62) | 11.06 ± 22.72 (5.41) | 2.22 ± 0.52 (2.31) | 4.80 ± 1.22 (5.28) | 2.03 ± 0.70 (2.13) |
| left/right | p | 0.752 | 24/25 | 0 | 19 | 2.12 ± 2.03 (1.93) | 26.19 ± 43.39 (5.16) | 2.03 ± 0.66 (2.27) | 4.43 ± 1.56 (5.04) | 1.80 ± 0.85 (1.97) |
| back/left | p | 0.753 | 25/25 | 0 | 21 | 2.49 ± 0.83 (2.54) | 31.16 ± 58.94 (7.45) | 2.17 ± 0.62 (2.37) | 4.64 ± 1.41 (5.25) | 1.97 ± 0.79 (2.19) |
| back/right | p | 0.734 | 25/25 | 0 | 20 | 2.79 ± 1.85 (2.50) | 33.67 ± 59.00 (6.15) | 2.05 ± 0.88 (2.38) | 4.38 ± 1.95 (5.25) | 1.92 ± 0.99 (2.27) |
| right/left | p | 0.795 | 25/25 | 0 | 20 | 1.74 ± 0.47 (1.74) | 25.66 ± 45.78 (4.91) | 1.97 ± 0.70 (2.23) | 4.21 ± 1.63 (4.73) | 1.69 ± 0.84 (1.94) |
| right/right | p | 0.794 | 25/25 | 0 | 21 | 2.36 ± 2.65 (1.74) | 12.23 ± 21.70 (4.66) | 2.17 ± 0.47 (2.21) | 4.74 ± 1.17 (5.22) | 1.94 ± 0.68 (1.96) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.807 | 20.2 | 5.08 | 2.20 |
| p | normal | 0.758 | 19.2 | 3.96 | 1.56 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.717 | 0.14 | 2.32 ± 0.97 (2.20) | 3.66 | 1.39 |
| p | medium | 16 | 0.833 | 0.68 | 1.27 ± 0.22 (1.29) | 4.15 | 1.68 |
| p | strong | 126 | 0.806 | 0.66 | - | 4.96 | 2.13 |

## Notes

- p: score 0.782, 199/200 kicked, 0 fell; worst sector back (0.743).

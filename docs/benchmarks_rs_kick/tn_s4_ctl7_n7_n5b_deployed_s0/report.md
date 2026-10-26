# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s4_ctl7_n7_n5b.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.784** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 165 |
| Weak kicks (< 0.3 m) | 14 |
| Time to kick [s] | 2.12 ± 1.84 (1.74) |
| Direction error [°] | 18.79 ± 37.35 (4.94) |
| Avg ball speed [m/s] | 2.03 ± 0.64 (2.25) |
| Peak ball speed [m/s] | 4.48 ± 1.55 (4.97) |
| Distance [m] | 1.75 ± 0.79 (1.83) |
| Path length [m] | 1.76 ± 0.79 (1.84) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.797 | 50/50 | 0 | 42 | 1.87 ± 2.24 (1.35) | 7.95 ± 10.08 (4.05) | 1.99 ± 0.67 (2.08) | 4.36 ± 1.63 (4.27) | 1.70 ± 0.87 (1.60) |
| left | p | 0.811 | 50/50 | 0 | 42 | 2.06 ± 2.08 (1.75) | 18.79 ± 34.73 (5.93) | 2.08 ± 0.56 (2.29) | 4.64 ± 1.38 (5.36) | 1.81 ± 0.73 (2.04) |
| back | p | 0.730 | 49/50 | 0 | 40 | 2.49 ± 0.71 (2.56) | 28.28 ± 51.30 (5.75) | 2.05 ± 0.67 (2.31) | 4.50 ± 1.58 (5.20) | 1.78 ± 0.75 (1.95) |
| right | p | 0.797 | 50/50 | 0 | 41 | 2.05 ± 1.85 (1.73) | 20.32 ± 38.20 (3.08) | 2.01 ± 0.65 (2.21) | 4.40 ± 1.57 (4.92) | 1.72 ± 0.79 (1.80) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.806 | 99/100 | 0 | 87 | 1.83 ± 1.01 (1.68) | 16.05 ± 35.03 (5.18) | 2.13 ± 0.53 (2.28) | 4.69 ± 1.31 (5.31) | 1.85 ± 0.70 (1.96) |
| right | p | 0.761 | 100/100 | 0 | 78 | 2.40 ± 2.35 (1.74) | 21.49 ± 39.34 (4.92) | 1.94 ± 0.72 (2.15) | 4.27 ± 1.72 (4.65) | 1.65 ± 0.85 (1.76) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.820 | 25/25 | 0 | 22 | 1.59 ± 1.65 (1.30) | 6.99 ± 10.47 (2.47) | 2.10 ± 0.58 (2.15) | 4.58 ± 1.44 (4.53) | 1.81 ± 0.75 (1.77) |
| forward/right | p | 0.774 | 25/25 | 0 | 20 | 2.15 ± 2.67 (1.36) | 8.92 ± 9.57 (4.74) | 1.89 ± 0.74 (1.98) | 4.14 ± 1.77 (3.95) | 1.59 ± 0.96 (1.43) |
| left/left | p | 0.850 | 25/25 | 0 | 23 | 1.58 ± 0.42 (1.64) | 12.19 ± 22.35 (6.01) | 2.14 ± 0.46 (2.27) | 4.79 ± 1.15 (5.36) | 1.87 ± 0.64 (2.05) |
| left/right | p | 0.771 | 25/25 | 0 | 19 | 2.54 ± 2.83 (1.96) | 25.38 ± 42.72 (5.83) | 2.02 ± 0.64 (2.33) | 4.49 ± 1.57 (5.34) | 1.75 ± 0.81 (2.01) |
| back/left | p | 0.733 | 24/25 | 0 | 21 | 2.40 ± 0.72 (2.49) | 25.38 ± 50.66 (6.08) | 2.19 ± 0.42 (2.29) | 4.79 ± 1.06 (5.26) | 1.89 ± 0.60 (1.92) |
| back/right | p | 0.727 | 25/25 | 0 | 19 | 2.57 ± 0.68 (2.64) | 31.06 ± 51.75 (5.35) | 1.92 ± 0.83 (2.32) | 4.23 ± 1.92 (5.09) | 1.67 ± 0.86 (1.95) |
| right/left | p | 0.820 | 25/25 | 0 | 21 | 1.78 ± 0.50 (1.78) | 20.03 ± 39.86 (2.77) | 2.11 ± 0.62 (2.30) | 4.60 ± 1.51 (5.31) | 1.83 ± 0.80 (1.98) |
| right/right | p | 0.773 | 25/25 | 0 | 20 | 2.32 ± 2.54 (1.72) | 20.61 ± 36.46 (3.86) | 1.91 ± 0.67 (2.14) | 4.21 ± 1.59 (4.90) | 1.61 ± 0.77 (1.68) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.811 | 17.0 | 5.09 | 2.07 |
| p | normal | 0.756 | 20.5 | 3.87 | 1.44 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.715 | 0.18 | 2.23 ± 1.00 (2.03) | 3.52 | 1.26 |
| p | medium | 16 | 0.824 | 0.70 | 1.25 ± 0.22 (1.29) | 4.06 | 1.58 |
| p | strong | 126 | 0.810 | 0.66 | - | 4.98 | 2.00 |

## Notes

- p: score 0.784, 199/200 kicked, 0 fell; worst sector back (0.730).

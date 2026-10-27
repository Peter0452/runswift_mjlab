# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/r1_u5_u0.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.772** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 165 |
| Weak kicks (< 0.3 m) | 21 |
| Time to kick [s] | 2.04 ± 1.50 (1.81) |
| Direction error [°] | 18.17 ± 35.55 (5.62) |
| Avg ball speed [m/s] | 2.16 ± 0.76 (2.34) |
| Peak ball speed [m/s] | 4.63 ± 1.72 (5.21) |
| Distance [m] | 2.04 ± 0.95 (2.23) |
| Path length [m] | 2.05 ± 0.96 (2.24) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.779 | 48/50 | 0 | 42 | 1.29 ± 0.34 (1.27) | 12.68 ± 22.07 (6.05) | 2.15 ± 0.67 (2.26) | 4.66 ± 1.58 (5.02) | 2.01 ± 0.89 (2.10) |
| left | p | 0.771 | 49/50 | 0 | 40 | 2.13 ± 1.50 (1.92) | 14.74 ± 22.96 (7.75) | 2.13 ± 0.84 (2.35) | 4.60 ± 1.85 (5.33) | 2.05 ± 1.03 (2.32) |
| back | p | 0.750 | 50/50 | 0 | 43 | 2.83 ± 1.93 (2.57) | 24.25 ± 48.53 (5.15) | 2.28 ± 0.74 (2.51) | 4.84 ± 1.66 (5.60) | 2.20 ± 0.93 (2.54) |
| right | p | 0.788 | 49/50 | 0 | 40 | 1.86 ± 1.26 (1.82) | 20.79 ± 39.53 (4.72) | 2.05 ± 0.78 (2.31) | 4.41 ± 1.74 (5.06) | 1.90 ± 0.94 (1.91) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.776 | 99/100 | 0 | 82 | 2.04 ± 1.44 (1.82) | 20.43 ± 37.83 (6.07) | 2.14 ± 0.83 (2.42) | 4.63 ± 1.87 (5.42) | 2.08 ± 1.04 (2.36) |
| right | p | 0.768 | 97/100 | 0 | 83 | 2.03 ± 1.56 (1.80) | 15.87 ± 32.92 (5.24) | 2.17 ± 0.69 (2.30) | 4.63 ± 1.55 (4.78) | 2.00 ± 0.86 (1.99) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.801 | 25/25 | 0 | 22 | 1.35 ± 0.40 (1.38) | 15.71 ± 28.78 (5.46) | 2.14 ± 0.75 (2.25) | 4.59 ± 1.73 (4.56) | 2.03 ± 0.96 (1.94) |
| forward/right | p | 0.757 | 23/25 | 0 | 20 | 1.23 ± 0.25 (1.20) | 9.40 ± 9.79 (6.66) | 2.18 ± 0.57 (2.26) | 4.73 ± 1.40 (5.10) | 1.98 ± 0.80 (2.23) |
| left/left | p | 0.763 | 25/25 | 0 | 20 | 2.35 ± 2.03 (1.90) | 13.73 ± 16.20 (9.42) | 2.07 ± 0.93 (2.33) | 4.50 ± 2.07 (5.37) | 2.05 ± 1.14 (2.36) |
| left/right | p | 0.780 | 24/25 | 0 | 20 | 1.90 ± 0.46 (1.94) | 15.79 ± 28.29 (5.53) | 2.20 ± 0.72 (2.35) | 4.70 ± 1.59 (5.06) | 2.06 ± 0.90 (2.23) |
| back/left | p | 0.776 | 25/25 | 0 | 21 | 2.34 ± 0.66 (2.52) | 24.12 ± 44.31 (5.54) | 2.30 ± 0.74 (2.57) | 4.97 ± 1.70 (5.80) | 2.28 ± 0.99 (2.72) |
| back/right | p | 0.724 | 25/25 | 0 | 22 | 3.33 ± 2.56 (2.60) | 24.37 ± 52.41 (4.59) | 2.25 ± 0.73 (2.38) | 4.71 ± 1.62 (4.77) | 2.11 ± 0.87 (2.02) |
| right/left | p | 0.764 | 24/25 | 0 | 19 | 2.12 ± 1.71 (1.85) | 28.47 ± 50.71 (4.39) | 2.06 ± 0.86 (2.44) | 4.44 ± 1.91 (5.53) | 1.94 ± 1.01 (2.36) |
| right/right | p | 0.812 | 25/25 | 0 | 21 | 1.61 ± 0.42 (1.72) | 13.41 ± 21.99 (4.89) | 2.05 ± 0.69 (2.17) | 4.38 ± 1.57 (4.31) | 1.85 ± 0.86 (1.80) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.799 | 19.2 | 5.10 | 2.32 |
| p | normal | 0.745 | 17.2 | 4.16 | 1.76 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.704 | 0.16 | 2.25 ± 1.01 (2.19) | 3.76 | 1.49 |
| p | medium | 15 | 0.782 | 0.62 | 1.22 ± 0.38 (1.31) | 3.95 | 1.58 |
| p | strong | 125 | 0.804 | 0.68 | - | 5.12 | 2.35 |

## Notes

- p: score 0.772, 196/200 kicked, 0 fell; worst sector back (0.750).

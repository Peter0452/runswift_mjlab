# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/r5_u5_u0_u12.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.782** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 166 |
| Weak kicks (< 0.3 m) | 14 |
| Time to kick [s] | 2.00 ± 1.53 (1.74) |
| Direction error [°] | 19.32 ± 39.52 (4.90) |
| Avg ball speed [m/s] | 2.07 ± 0.67 (2.26) |
| Peak ball speed [m/s] | 4.54 ± 1.58 (5.02) |
| Distance [m] | 1.87 ± 0.86 (1.92) |
| Path length [m] | 1.87 ± 0.86 (1.92) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.792 | 50/50 | 0 | 42 | 1.75 ± 1.85 (1.34) | 9.60 ± 13.31 (4.86) | 2.04 ± 0.70 (2.15) | 4.44 ± 1.66 (4.28) | 1.81 ± 0.91 (1.72) |
| left | p | 0.800 | 48/50 | 0 | 42 | 1.65 ± 0.50 (1.74) | 17.93 ± 35.48 (5.01) | 2.08 ± 0.61 (2.23) | 4.62 ± 1.47 (5.13) | 1.87 ± 0.80 (1.92) |
| back | p | 0.738 | 49/50 | 0 | 41 | 2.49 ± 1.14 (2.46) | 31.30 ± 58.38 (6.53) | 2.11 ± 0.70 (2.29) | 4.58 ± 1.57 (5.20) | 1.94 ± 0.85 (1.97) |
| right | p | 0.797 | 50/50 | 0 | 41 | 2.10 ± 1.96 (1.76) | 18.61 ± 34.52 (4.05) | 2.06 ± 0.68 (2.26) | 4.51 ± 1.61 (5.12) | 1.84 ± 0.86 (2.02) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.810 | 100/100 | 0 | 86 | 1.84 ± 0.96 (1.72) | 18.19 ± 38.60 (5.17) | 2.15 ± 0.61 (2.29) | 4.71 ± 1.46 (5.17) | 1.96 ± 0.83 (2.02) |
| right | p | 0.754 | 97/100 | 0 | 80 | 2.16 ± 1.93 (1.74) | 20.47 ± 40.43 (4.80) | 1.99 ± 0.72 (2.19) | 4.36 ± 1.68 (4.71) | 1.77 ± 0.88 (1.86) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.821 | 25/25 | 0 | 21 | 1.35 ± 0.50 (1.30) | 9.61 ± 14.92 (4.42) | 2.14 ± 0.68 (2.37) | 4.68 ± 1.64 (4.51) | 1.97 ± 0.90 (1.87) |
| forward/right | p | 0.763 | 25/25 | 0 | 21 | 2.14 ± 2.51 (1.36) | 9.60 ± 11.48 (5.24) | 1.94 ± 0.70 (2.02) | 4.19 ± 1.64 (4.15) | 1.66 ± 0.90 (1.60) |
| left/left | p | 0.856 | 25/25 | 0 | 23 | 1.58 ± 0.42 (1.66) | 11.59 ± 22.32 (5.29) | 2.17 ± 0.52 (2.28) | 4.80 ± 1.28 (5.14) | 1.98 ± 0.75 (2.11) |
| left/right | p | 0.745 | 23/25 | 0 | 19 | 1.72 ± 0.56 (1.90) | 24.83 ± 44.66 (4.79) | 1.98 ± 0.67 (2.17) | 4.42 ± 1.63 (5.02) | 1.74 ± 0.84 (1.86) |
| back/left | p | 0.745 | 25/25 | 0 | 21 | 2.64 ± 1.44 (2.52) | 31.72 ± 58.13 (7.82) | 2.18 ± 0.61 (2.30) | 4.72 ± 1.39 (5.21) | 2.00 ± 0.84 (2.00) |
| back/right | p | 0.731 | 24/25 | 0 | 20 | 2.34 ± 0.66 (2.42) | 30.86 ± 58.63 (4.87) | 2.04 ± 0.77 (2.28) | 4.42 ± 1.73 (5.08) | 1.88 ± 0.86 (1.97) |
| right/left | p | 0.819 | 25/25 | 0 | 21 | 1.80 ± 0.50 (1.80) | 19.86 ± 39.44 (3.18) | 2.11 ± 0.62 (2.28) | 4.63 ± 1.50 (5.41) | 1.89 ± 0.83 (2.02) |
| right/right | p | 0.776 | 25/25 | 0 | 20 | 2.39 ± 2.70 (1.74) | 17.37 ± 28.72 (4.33) | 2.00 ± 0.73 (2.21) | 4.39 ± 1.71 (4.97) | 1.79 ± 0.88 (2.03) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.808 | 18.5 | 5.17 | 2.22 |
| p | normal | 0.757 | 20.1 | 3.91 | 1.51 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.721 | 0.16 | 2.29 ± 1.04 (2.16) | 3.61 | 1.36 |
| p | medium | 16 | 0.807 | 0.71 | 1.24 ± 0.21 (1.27) | 4.02 | 1.56 |
| p | strong | 126 | 0.807 | 0.67 | - | 5.03 | 2.14 |

## Notes

- p: score 0.782, 197/200 kicked, 0 fell; worst sector back (0.738).

# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s6_ctl7_30_n7_70.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.781** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 173 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 2.12 ± 1.86 (1.72) |
| Direction error [°] | 15.37 ± 31.39 (5.85) |
| Avg ball speed [m/s] | 2.15 ± 0.68 (2.32) |
| Peak ball speed [m/s] | 4.65 ± 1.56 (5.21) |
| Distance [m] | 2.02 ± 0.88 (2.15) |
| Path length [m] | 2.03 ± 0.88 (2.17) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.814 | 49/50 | 0 | 44 | 1.44 ± 1.39 (1.30) | 8.75 ± 14.99 (4.14) | 2.16 ± 0.66 (2.30) | 4.68 ± 1.54 (5.31) | 2.02 ± 0.89 (1.96) |
| left | p | 0.807 | 50/50 | 0 | 43 | 1.72 ± 0.63 (1.70) | 16.89 ± 31.66 (6.38) | 2.13 ± 0.67 (2.34) | 4.64 ± 1.56 (5.28) | 2.00 ± 0.88 (2.20) |
| back | p | 0.744 | 50/50 | 0 | 45 | 2.97 ± 2.11 (2.55) | 18.32 ± 36.51 (7.20) | 2.26 ± 0.59 (2.34) | 4.83 ± 1.38 (5.34) | 2.14 ± 0.80 (2.37) |
| right | p | 0.760 | 49/50 | 0 | 41 | 2.35 ± 2.40 (1.80) | 17.44 ± 36.24 (4.29) | 2.07 ± 0.76 (2.25) | 4.45 ± 1.73 (4.42) | 1.92 ± 0.93 (1.85) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.807 | 100/100 | 0 | 89 | 1.84 ± 0.87 (1.72) | 14.13 ± 29.97 (6.09) | 2.18 ± 0.64 (2.33) | 4.71 ± 1.50 (5.30) | 2.06 ± 0.87 (2.20) |
| right | p | 0.756 | 98/100 | 0 | 84 | 2.41 ± 2.46 (1.74) | 16.64 ± 32.72 (5.50) | 2.13 ± 0.71 (2.31) | 4.58 ± 1.62 (5.19) | 1.98 ± 0.89 (2.11) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.827 | 25/25 | 0 | 22 | 1.26 ± 0.29 (1.30) | 9.41 ± 13.95 (5.81) | 2.09 ± 0.74 (2.19) | 4.50 ± 1.70 (4.34) | 1.95 ± 0.97 (1.79) |
| forward/right | p | 0.801 | 24/25 | 0 | 22 | 1.64 ± 1.94 (1.30) | 8.05 ± 15.97 (3.40) | 2.24 ± 0.57 (2.31) | 4.87 ± 1.34 (5.36) | 2.09 ± 0.79 (2.08) |
| left/left | p | 0.800 | 25/25 | 0 | 21 | 1.57 ± 0.41 (1.62) | 14.41 ± 21.17 (7.31) | 2.09 ± 0.68 (2.22) | 4.56 ± 1.59 (5.19) | 1.97 ± 0.93 (2.13) |
| left/right | p | 0.814 | 25/25 | 0 | 22 | 1.86 ± 0.76 (1.72) | 19.37 ± 39.30 (5.88) | 2.16 ± 0.66 (2.38) | 4.71 ± 1.53 (5.49) | 2.04 ± 0.83 (2.35) |
| back/left | p | 0.792 | 25/25 | 0 | 24 | 2.55 ± 0.61 (2.52) | 12.08 ± 27.75 (6.19) | 2.36 ± 0.40 (2.34) | 5.07 ± 1.03 (5.37) | 2.27 ± 0.64 (2.40) |
| back/right | p | 0.696 | 25/25 | 0 | 21 | 3.38 ± 2.86 (2.60) | 24.55 ± 42.65 (7.66) | 2.16 ± 0.72 (2.26) | 4.58 ± 1.62 (4.76) | 2.01 ± 0.91 (2.09) |
| right/left | p | 0.810 | 25/25 | 0 | 22 | 1.96 ± 1.21 (1.76) | 20.61 ± 45.96 (3.95) | 2.17 ± 0.65 (2.31) | 4.72 ± 1.54 (5.27) | 2.03 ± 0.86 (2.14) |
| right/right | p | 0.711 | 24/25 | 0 | 19 | 2.75 ± 3.15 (1.85) | 14.13 ± 21.44 (5.84) | 1.95 ± 0.84 (2.16) | 4.17 ± 1.87 (4.22) | 1.80 ± 0.99 (1.72) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.831 | 12.1 | 5.17 | 2.34 |
| p | normal | 0.732 | 18.7 | 4.12 | 1.70 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.703 | 0.10 | 2.43 ± 1.03 (2.42) | 3.82 | 1.51 |
| p | medium | 18 | 0.815 | 0.63 | 1.16 ± 0.40 (1.30) | 3.75 | 1.45 |
| p | strong | 124 | 0.813 | 0.69 | - | 5.18 | 2.35 |

## Notes

- p: score 0.781, 198/200 kicked, 0 fell; worst sector back (0.744).

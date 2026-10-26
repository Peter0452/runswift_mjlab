# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s4_ctl7_n7_n5b.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.802** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 176 |
| Weak kicks (< 0.3 m) | 17 |
| Time to kick [s] | 1.96 ± 1.30 (1.69) |
| Direction error [°] | 14.41 ± 29.79 (5.38) |
| Avg ball speed [m/s] | 2.12 ± 0.62 (2.29) |
| Peak ball speed [m/s] | 4.62 ± 1.49 (5.15) |
| Distance [m] | 1.90 ± 0.78 (2.07) |
| Path length [m] | 1.91 ± 0.79 (2.08) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.814 | 50/50 | 0 | 44 | 1.61 ± 1.67 (1.31) | 9.31 ± 14.30 (4.18) | 2.06 ± 0.70 (2.33) | 4.56 ± 1.68 (5.18) | 1.87 ± 0.86 (1.99) |
| left | p | 0.834 | 50/50 | 0 | 45 | 1.73 ± 0.49 (1.67) | 11.13 ± 22.55 (4.46) | 2.12 ± 0.56 (2.26) | 4.61 ± 1.34 (5.11) | 1.90 ± 0.73 (2.05) |
| back | p | 0.754 | 50/50 | 0 | 43 | 2.73 ± 1.63 (2.50) | 24.89 ± 46.65 (7.33) | 2.18 ± 0.65 (2.38) | 4.74 ± 1.51 (5.49) | 1.99 ± 0.80 (2.21) |
| right | p | 0.807 | 50/50 | 0 | 44 | 1.77 ± 0.53 (1.75) | 12.31 ± 22.60 (5.26) | 2.10 ± 0.55 (2.23) | 4.55 ± 1.38 (4.83) | 1.85 ± 0.73 (1.82) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.801 | 100/100 | 0 | 86 | 1.84 ± 0.90 (1.63) | 16.23 ± 31.85 (5.38) | 2.08 ± 0.68 (2.30) | 4.55 ± 1.60 (5.24) | 1.87 ± 0.83 (2.11) |
| right | p | 0.804 | 100/100 | 0 | 90 | 2.07 ± 1.60 (1.77) | 12.59 ± 27.46 (5.40) | 2.15 ± 0.56 (2.29) | 4.69 ± 1.35 (5.02) | 1.94 ± 0.74 (2.01) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.829 | 25/25 | 0 | 22 | 1.26 ± 0.33 (1.26) | 9.47 ± 15.58 (3.61) | 2.05 ± 0.72 (2.36) | 4.52 ± 1.67 (5.24) | 1.86 ± 0.87 (2.18) |
| forward/right | p | 0.799 | 25/25 | 0 | 22 | 1.95 ± 2.29 (1.34) | 9.15 ± 12.89 (4.36) | 2.07 ± 0.69 (2.30) | 4.60 ± 1.69 (5.17) | 1.88 ± 0.85 (1.93) |
| left/left | p | 0.843 | 25/25 | 0 | 23 | 1.71 ± 0.49 (1.62) | 6.74 ± 7.06 (4.44) | 2.20 ± 0.56 (2.29) | 4.80 ± 1.34 (5.24) | 2.02 ± 0.71 (2.16) |
| left/right | p | 0.825 | 25/25 | 0 | 22 | 1.74 ± 0.50 (1.82) | 15.51 ± 30.48 (5.70) | 2.04 ± 0.54 (2.21) | 4.41 ± 1.32 (4.36) | 1.78 ± 0.73 (1.72) |
| back/left | p | 0.752 | 25/25 | 0 | 20 | 2.48 ± 1.32 (2.46) | 30.90 ± 50.04 (8.19) | 2.03 ± 0.72 (2.33) | 4.47 ± 1.70 (5.40) | 1.81 ± 0.86 (2.21) |
| back/right | p | 0.755 | 25/25 | 0 | 23 | 2.98 ± 1.86 (2.56) | 18.88 ± 42.14 (7.12) | 2.33 ± 0.52 (2.42) | 5.01 ± 1.22 (5.55) | 2.17 ± 0.69 (2.21) |
| right/left | p | 0.780 | 25/25 | 0 | 21 | 1.91 ± 0.63 (1.98) | 17.80 ± 30.15 (5.62) | 2.04 ± 0.68 (2.25) | 4.39 ± 1.65 (4.29) | 1.79 ± 0.84 (1.78) |
| right/right | p | 0.835 | 25/25 | 0 | 23 | 1.62 ± 0.35 (1.58) | 6.82 ± 7.25 (4.49) | 2.17 ± 0.39 (2.19) | 4.72 ± 1.03 (4.94) | 1.91 ± 0.60 (1.84) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.827 | 13.9 | 5.05 | 2.14 |
| p | normal | 0.777 | 14.9 | 4.18 | 1.66 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.728 | 0.13 | 2.39 ± 0.97 (2.28) | 3.72 | 1.40 |
| p | medium | 20 | 0.868 | 0.71 | 1.29 ± 0.14 (1.26) | 4.14 | 1.61 |
| p | strong | 126 | 0.824 | 0.68 | - | 5.08 | 2.16 |

## Notes

- p: score 0.802, 200/200 kicked, 0 fell; worst sector back (0.754).

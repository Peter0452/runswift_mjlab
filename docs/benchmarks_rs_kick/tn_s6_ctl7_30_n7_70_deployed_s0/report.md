# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s6_ctl7_30_n7_70.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.784** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 156 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 1.94 ± 1.54 (1.70) |
| Direction error [°] | 20.86 ± 39.86 (6.87) |
| Avg ball speed [m/s] | 2.30 ± 0.86 (2.55) |
| Peak ball speed [m/s] | 4.76 ± 1.85 (5.52) |
| Distance [m] | 2.33 ± 1.18 (2.78) |
| Path length [m] | 2.34 ± 1.18 (2.81) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.793 | 50/50 | 0 | 39 | 1.86 ± 2.30 (1.30) | 9.39 ± 11.92 (5.01) | 2.26 ± 0.81 (2.23) | 4.60 ± 1.70 (4.26) | 2.16 ± 1.08 (1.85) |
| left | p | 0.807 | 49/50 | 0 | 41 | 1.83 ± 1.19 (1.76) | 17.59 ± 32.14 (7.31) | 2.43 ± 0.78 (2.62) | 5.06 ± 1.70 (5.83) | 2.53 ± 1.11 (3.06) |
| back | p | 0.750 | 49/50 | 0 | 38 | 2.26 ± 0.65 (2.42) | 36.56 ± 60.67 (7.39) | 2.22 ± 1.00 (2.72) | 4.65 ± 2.15 (5.88) | 2.33 ± 1.32 (2.99) |
| right | p | 0.785 | 49/50 | 0 | 38 | 1.83 ± 1.46 (1.70) | 20.13 ± 33.72 (7.06) | 2.29 ± 0.82 (2.38) | 4.74 ± 1.75 (5.48) | 2.29 ± 1.16 (2.58) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.808 | 99/100 | 0 | 80 | 1.72 ± 0.61 (1.68) | 18.72 ± 38.17 (5.94) | 2.38 ± 0.76 (2.57) | 4.94 ± 1.65 (5.62) | 2.42 ± 1.08 (2.81) |
| right | p | 0.759 | 98/100 | 0 | 76 | 2.17 ± 2.07 (1.71) | 23.02 ± 41.39 (7.37) | 2.22 ± 0.95 (2.52) | 4.58 ± 2.01 (5.40) | 2.23 ± 1.26 (2.48) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.827 | 25/25 | 0 | 20 | 1.32 ± 0.38 (1.28) | 9.02 ± 13.60 (4.13) | 2.35 ± 0.76 (2.30) | 4.80 ± 1.62 (4.49) | 2.27 ± 1.03 (2.05) |
| forward/right | p | 0.758 | 25/25 | 0 | 19 | 2.39 ± 3.14 (1.32) | 9.76 ± 9.94 (5.66) | 2.18 ± 0.85 (2.19) | 4.40 ± 1.77 (4.23) | 2.04 ± 1.11 (1.80) |
| left/left | p | 0.865 | 25/25 | 0 | 22 | 1.60 ± 0.37 (1.74) | 9.63 ± 15.24 (6.35) | 2.60 ± 0.61 (2.67) | 5.41 ± 1.34 (6.04) | 2.76 ± 0.95 (3.13) |
| left/right | p | 0.750 | 24/25 | 0 | 19 | 2.07 ± 1.62 (1.86) | 25.89 ± 41.62 (9.01) | 2.25 ± 0.90 (2.60) | 4.70 ± 1.94 (5.78) | 2.30 ± 1.21 (2.93) |
| back/left | p | 0.748 | 24/25 | 0 | 20 | 2.29 ± 0.67 (2.46) | 31.99 ± 59.06 (6.07) | 2.35 ± 0.77 (2.69) | 4.94 ± 1.70 (5.87) | 2.43 ± 1.13 (2.96) |
| back/right | p | 0.752 | 25/25 | 0 | 18 | 2.23 ± 0.63 (2.32) | 40.95 ± 61.87 (8.61) | 2.10 ± 1.17 (2.77) | 4.36 ± 2.48 (5.94) | 2.23 ± 1.47 (3.13) |
| right/left | p | 0.792 | 25/25 | 0 | 18 | 1.69 ± 0.49 (1.74) | 24.76 ± 40.27 (7.06) | 2.22 ± 0.84 (2.28) | 4.60 ± 1.80 (4.38) | 2.20 ± 1.14 (2.00) |
| right/right | p | 0.778 | 24/25 | 0 | 20 | 1.98 ± 2.01 (1.66) | 15.31 ± 24.23 (6.05) | 2.36 ± 0.80 (2.63) | 4.87 ± 1.69 (5.75) | 2.38 ± 1.17 (2.82) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.806 | 18.3 | 5.59 | 2.91 |
| p | normal | 0.762 | 23.4 | 3.96 | 1.76 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.725 | 0.19 | 2.25 ± 1.14 (2.22) | 3.44 | 1.38 |
| p | medium | 16 | 0.799 | 0.65 | 1.18 ± 0.36 (1.27) | 3.81 | 1.62 |
| p | strong | 126 | 0.809 | 0.73 | - | 5.51 | 2.86 |

## Notes

- p: score 0.784, 197/200 kicked, 0 fell; worst sector back (0.750).

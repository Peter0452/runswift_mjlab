# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s6_ctl7_30_n7_70.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.800** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 173 |
| Weak kicks (< 0.3 m) | 10 |
| Time to kick [s] | 2.00 ± 1.44 (1.72) |
| Direction error [°] | 13.84 ± 30.13 (4.68) |
| Avg ball speed [m/s] | 1.90 ± 0.56 (2.01) |
| Peak ball speed [m/s] | 4.76 ± 1.43 (5.01) |
| Distance [m] | 2.05 ± 0.80 (2.04) |
| Path length [m] | 2.06 ± 0.80 (2.05) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.812 | 50/50 | 0 | 43 | 1.89 ± 2.25 (1.36) | 9.34 ± 15.54 (4.36) | 1.87 ± 0.59 (2.02) | 4.77 ± 1.56 (5.15) | 2.07 ± 0.84 (2.11) |
| left | p | 0.825 | 50/50 | 0 | 44 | 1.74 ± 0.47 (1.67) | 12.37 ± 24.17 (4.82) | 1.92 ± 0.52 (1.96) | 4.73 ± 1.34 (4.76) | 2.03 ± 0.80 (1.94) |
| back | p | 0.757 | 49/50 | 0 | 42 | 2.65 ± 1.49 (2.52) | 24.10 ± 48.48 (5.31) | 1.92 ± 0.64 (2.05) | 4.82 ± 1.60 (5.43) | 2.10 ± 0.88 (2.19) |
| right | p | 0.808 | 49/50 | 0 | 44 | 1.73 ± 0.38 (1.74) | 9.68 ± 18.19 (4.61) | 1.89 ± 0.47 (1.99) | 4.72 ± 1.19 (4.85) | 2.00 ± 0.65 (2.02) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.802 | 99/100 | 0 | 85 | 1.77 ± 0.62 (1.62) | 16.71 ± 34.50 (5.13) | 1.86 ± 0.59 (2.01) | 4.69 ± 1.52 (5.03) | 2.01 ± 0.83 (2.09) |
| right | p | 0.799 | 99/100 | 0 | 88 | 2.23 ± 1.91 (1.88) | 10.98 ± 24.68 (4.20) | 1.94 ± 0.52 (1.99) | 4.83 ± 1.33 (4.91) | 2.08 ± 0.77 (1.99) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.829 | 25/25 | 0 | 21 | 1.31 ± 0.45 (1.28) | 10.32 ± 17.20 (3.68) | 1.83 ± 0.62 (1.99) | 4.72 ± 1.57 (4.97) | 2.03 ± 0.85 (2.18) |
| forward/right | p | 0.796 | 25/25 | 0 | 22 | 2.47 ± 3.03 (1.42) | 8.37 ± 13.62 (4.69) | 1.90 ± 0.57 (2.02) | 4.81 ± 1.55 (5.34) | 2.10 ± 0.83 (2.08) |
| left/left | p | 0.846 | 25/25 | 0 | 24 | 1.75 ± 0.44 (1.62) | 5.80 ± 3.97 (5.13) | 2.01 ± 0.43 (2.02) | 4.95 ± 1.20 (5.03) | 2.17 ± 0.66 (2.04) |
| left/right | p | 0.804 | 25/25 | 0 | 20 | 1.72 ± 0.51 (1.80) | 18.93 ± 32.66 (4.40) | 1.83 ± 0.58 (1.87) | 4.51 ± 1.44 (4.43) | 1.90 ± 0.90 (1.83) |
| back/left | p | 0.761 | 25/25 | 0 | 19 | 2.19 ± 0.76 (2.46) | 37.20 ± 57.05 (6.03) | 1.78 ± 0.72 (2.01) | 4.52 ± 1.83 (5.43) | 1.92 ± 1.00 (2.17) |
| back/right | p | 0.752 | 24/25 | 0 | 23 | 3.13 ± 1.87 (2.60) | 10.47 ± 32.31 (3.24) | 2.07 ± 0.50 (2.13) | 5.14 ± 1.24 (5.37) | 2.28 ± 0.69 (2.24) |
| right/left | p | 0.773 | 24/25 | 0 | 21 | 1.83 ± 0.39 (2.01) | 13.38 ± 24.11 (4.55) | 1.81 ± 0.54 (2.02) | 4.58 ± 1.39 (4.88) | 1.93 ± 0.72 (2.07) |
| right/right | p | 0.843 | 25/25 | 0 | 23 | 1.63 ± 0.35 (1.66) | 6.13 ± 8.02 (4.97) | 1.96 ± 0.37 (1.95) | 4.85 ± 0.93 (4.85) | 2.06 ± 0.58 (1.90) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.835 | 15.3 | 5.10 | 2.21 |
| p | normal | 0.766 | 12.4 | 4.41 | 1.88 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.720 | 0.10 | 2.56 ± 0.96 (2.32) | 4.01 | 1.62 |
| p | medium | 20 | 0.824 | 0.67 | 1.33 ± 0.15 (1.34) | 4.29 | 1.79 |
| p | strong | 126 | 0.831 | 0.69 | - | 5.15 | 2.27 |

## Notes

- p: score 0.800, 198/200 kicked, 0 fell; worst sector back (0.757).

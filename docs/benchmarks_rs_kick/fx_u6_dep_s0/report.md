# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u6_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.853** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.83 ± 0.54 (1.74) |
| Direction error [°] | 5.54 ± 11.97 (4.24) |
| Avg ball speed [m/s] | 2.29 ± 0.37 (2.33) |
| Peak ball speed [m/s] | 5.11 ± 1.00 (5.42) |
| Distance [m] | 2.07 ± 0.58 (2.13) |
| Path length [m] | 2.08 ± 0.59 (2.14) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.858 | 50/50 | 0 | 50 | 1.28 ± 0.24 (1.30) | 4.78 ± 2.53 (4.74) | 2.25 ± 0.44 (2.30) | 5.06 ± 1.16 (5.40) | 2.03 ± 0.70 (2.13) |
| left | p | 0.883 | 50/50 | 0 | 50 | 1.76 ± 0.36 (1.79) | 4.66 ± 3.21 (3.91) | 2.35 ± 0.32 (2.40) | 5.28 ± 0.89 (5.53) | 2.18 ± 0.55 (2.27) |
| back | p | 0.816 | 50/50 | 0 | 49 | 2.51 ± 0.30 (2.46) | 8.31 ± 23.21 (5.09) | 2.28 ± 0.38 (2.28) | 5.06 ± 1.02 (5.28) | 2.07 ± 0.54 (2.15) |
| right | p | 0.858 | 50/50 | 0 | 50 | 1.77 ± 0.34 (1.74) | 4.40 ± 2.70 (3.95) | 2.26 ± 0.30 (2.29) | 5.03 ± 0.90 (5.38) | 2.00 ± 0.51 (2.07) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.850 | 100/100 | 0 | 99 | 1.83 ± 0.54 (1.76) | 6.72 ± 16.66 (4.60) | 2.28 ± 0.40 (2.32) | 5.08 ± 1.05 (5.38) | 2.07 ± 0.60 (2.15) |
| right | p | 0.857 | 100/100 | 0 | 100 | 1.83 ± 0.54 (1.74) | 4.35 ± 2.51 (4.00) | 2.29 ± 0.33 (2.36) | 5.13 ± 0.95 (5.49) | 2.07 ± 0.56 (2.12) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.862 | 25/25 | 0 | 25 | 1.28 ± 0.25 (1.30) | 4.57 ± 2.49 (4.05) | 2.25 ± 0.42 (2.30) | 5.04 ± 1.10 (5.38) | 2.02 ± 0.66 (2.13) |
| forward/right | p | 0.853 | 25/25 | 0 | 25 | 1.27 ± 0.24 (1.30) | 4.99 ± 2.56 (5.22) | 2.26 ± 0.46 (2.42) | 5.08 ± 1.21 (5.79) | 2.05 ± 0.74 (2.29) |
| left/left | p | 0.873 | 25/25 | 0 | 25 | 1.65 ± 0.35 (1.72) | 5.34 ± 3.59 (5.85) | 2.28 ± 0.33 (2.32) | 5.09 ± 0.92 (5.19) | 2.08 ± 0.58 (2.09) |
| left/right | p | 0.893 | 25/25 | 0 | 25 | 1.88 ± 0.32 (1.96) | 3.97 ± 2.59 (3.78) | 2.42 ± 0.28 (2.49) | 5.47 ± 0.82 (5.70) | 2.27 ± 0.51 (2.34) |
| back/left | p | 0.803 | 25/25 | 0 | 24 | 2.52 ± 0.29 (2.46) | 12.31 ± 32.25 (6.60) | 2.30 ± 0.49 (2.45) | 5.08 ± 1.23 (5.47) | 2.14 ± 0.61 (2.40) |
| back/right | p | 0.828 | 25/25 | 0 | 25 | 2.50 ± 0.30 (2.46) | 4.31 ± 2.40 (3.95) | 2.26 ± 0.23 (2.23) | 5.04 ± 0.74 (5.20) | 2.00 ± 0.43 (1.99) |
| right/left | p | 0.862 | 25/25 | 0 | 25 | 1.88 ± 0.31 (1.78) | 4.66 ± 2.96 (3.95) | 2.29 ± 0.34 (2.31) | 5.12 ± 0.93 (5.47) | 2.05 ± 0.56 (2.08) |
| right/right | p | 0.854 | 25/25 | 0 | 25 | 1.67 ± 0.34 (1.74) | 4.13 ± 2.38 (3.94) | 2.23 ± 0.26 (2.29) | 4.94 ± 0.85 (5.38) | 1.95 ± 0.45 (2.05) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.893 | 5.0 | 5.81 | 2.45 |
| p | normal | 0.814 | 6.1 | 4.41 | 1.69 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.761 | 0.08 | 2.46 ± 0.81 (2.31) | 3.89 | 1.40 |
| p | medium | 16 | 0.883 | 0.72 | 1.27 ± 0.15 (1.27) | 4.14 | 1.57 |
| p | strong | 126 | 0.892 | 0.77 | - | 5.79 | 2.44 |

## Notes

- p: score 0.853, 200/200 kicked, 0 fell; worst sector back (0.816).

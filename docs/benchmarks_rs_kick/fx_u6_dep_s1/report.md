# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u6_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.855** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 4 |
| Time to kick [s] | 1.79 ± 0.54 (1.72) |
| Direction error [°] | 6.15 ± 8.11 (5.52) |
| Avg ball speed [m/s] | 2.61 ± 0.57 (2.67) |
| Peak ball speed [m/s] | 5.49 ± 1.34 (6.03) |
| Distance [m] | 2.74 ± 0.95 (3.03) |
| Path length [m] | 2.75 ± 0.95 (3.04) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.878 | 50/50 | 0 | 50 | 1.25 ± 0.25 (1.25) | 4.73 ± 3.35 (3.79) | 2.58 ± 0.43 (2.65) | 5.50 ± 1.11 (5.95) | 2.67 ± 0.81 (2.94) |
| left | p | 0.864 | 50/50 | 0 | 49 | 1.73 ± 0.34 (1.69) | 5.81 ± 3.83 (5.75) | 2.59 ± 0.55 (2.66) | 5.44 ± 1.33 (5.90) | 2.71 ± 0.95 (3.07) |
| back | p | 0.825 | 50/50 | 0 | 48 | 2.47 ± 0.29 (2.42) | 8.51 ± 14.66 (6.78) | 2.68 ± 0.78 (2.95) | 5.62 ± 1.72 (6.48) | 2.94 ± 1.12 (3.39) |
| right | p | 0.853 | 50/50 | 0 | 50 | 1.72 ± 0.34 (1.67) | 5.54 ± 3.74 (4.93) | 2.58 ± 0.43 (2.61) | 5.40 ± 1.09 (5.84) | 2.64 ± 0.84 (2.87) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.856 | 100/100 | 0 | 98 | 1.79 ± 0.54 (1.67) | 5.47 ± 3.66 (4.87) | 2.64 ± 0.51 (2.78) | 5.56 ± 1.22 (6.07) | 2.78 ± 0.89 (3.10) |
| right | p | 0.855 | 100/100 | 0 | 99 | 1.79 ± 0.53 (1.76) | 6.82 ± 10.82 (6.11) | 2.57 ± 0.62 (2.66) | 5.42 ± 1.45 (5.99) | 2.71 ± 1.00 (3.00) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.879 | 25/25 | 0 | 25 | 1.23 ± 0.26 (1.24) | 4.02 ± 3.11 (3.28) | 2.56 ± 0.42 (2.61) | 5.44 ± 1.07 (5.88) | 2.63 ± 0.78 (2.85) |
| forward/right | p | 0.877 | 25/25 | 0 | 25 | 1.27 ± 0.25 (1.28) | 5.44 ± 3.43 (5.77) | 2.60 ± 0.44 (2.67) | 5.55 ± 1.14 (6.13) | 2.71 ± 0.84 (2.99) |
| left/left | p | 0.862 | 25/25 | 0 | 24 | 1.65 ± 0.34 (1.60) | 6.14 ± 4.46 (5.70) | 2.57 ± 0.64 (2.67) | 5.41 ± 1.49 (6.02) | 2.71 ± 1.00 (3.17) |
| left/right | p | 0.866 | 25/25 | 0 | 25 | 1.80 ± 0.33 (1.84) | 5.48 ± 3.04 (6.14) | 2.61 ± 0.45 (2.54) | 5.47 ± 1.14 (5.76) | 2.71 ± 0.90 (2.75) |
| back/left | p | 0.826 | 25/25 | 0 | 24 | 2.49 ± 0.26 (2.44) | 6.91 ± 3.37 (6.65) | 2.84 ± 0.44 (2.99) | 5.96 ± 1.08 (6.52) | 3.10 ± 0.85 (3.54) |
| back/right | p | 0.825 | 25/25 | 0 | 24 | 2.46 ± 0.32 (2.40) | 10.11 ± 20.33 (6.78) | 2.52 ± 0.98 (2.84) | 5.28 ± 2.13 (6.29) | 2.77 ± 1.32 (3.34) |
| right/left | p | 0.856 | 25/25 | 0 | 25 | 1.80 ± 0.35 (1.74) | 4.80 ± 2.73 (4.21) | 2.59 ± 0.43 (2.62) | 5.43 ± 1.08 (5.87) | 2.66 ± 0.82 (2.93) |
| right/right | p | 0.851 | 25/25 | 0 | 25 | 1.64 ± 0.32 (1.58) | 6.27 ± 4.40 (6.08) | 2.57 ± 0.42 (2.50) | 5.36 ± 1.09 (5.67) | 2.63 ± 0.85 (2.82) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.893 | 7.2 | 6.33 | 3.36 |
| p | normal | 0.817 | 5.1 | 4.64 | 2.12 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.761 | 0.06 | 2.60 ± 0.91 (2.49) | 4.02 | 1.65 |
| p | medium | 20 | 0.882 | 0.67 | 1.33 ± 0.13 (1.33) | 4.26 | 1.79 |
| p | strong | 126 | 0.891 | 0.84 | - | 6.31 | 3.36 |

## Notes

- p: score 0.855, 200/200 kicked, 0 fell; worst sector back (0.825).

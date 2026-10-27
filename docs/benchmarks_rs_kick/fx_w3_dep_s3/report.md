# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w3_u4_tail.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.856** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.90 ± 0.58 (1.88) |
| Direction error [°] | 5.13 ± 3.80 (4.58) |
| Avg ball speed [m/s] | 2.37 ± 0.49 (2.51) |
| Peak ball speed [m/s] | 5.10 ± 1.21 (5.69) |
| Distance [m] | 2.30 ± 0.85 (2.50) |
| Path length [m] | 2.31 ± 0.85 (2.51) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.872 | 50/50 | 0 | 49 | 1.31 ± 0.24 (1.30) | 5.29 ± 3.49 (5.09) | 2.26 ± 0.49 (2.40) | 4.96 ± 1.24 (5.54) | 2.16 ± 0.84 (2.35) |
| left | p | 0.877 | 50/50 | 0 | 48 | 1.83 ± 0.32 (1.87) | 4.66 ± 4.14 (3.41) | 2.41 ± 0.45 (2.56) | 5.20 ± 1.16 (5.85) | 2.36 ± 0.80 (2.59) |
| back | p | 0.804 | 50/50 | 0 | 49 | 2.63 ± 0.41 (2.56) | 6.06 ± 3.53 (5.67) | 2.42 ± 0.47 (2.55) | 5.13 ± 1.21 (5.73) | 2.36 ± 0.87 (2.58) |
| right | p | 0.869 | 50/50 | 0 | 49 | 1.83 ± 0.34 (1.90) | 4.52 ± 3.82 (4.05) | 2.41 ± 0.52 (2.58) | 5.13 ± 1.21 (5.69) | 2.33 ± 0.86 (2.51) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.857 | 100/100 | 0 | 96 | 1.90 ± 0.58 (1.88) | 5.27 ± 3.94 (4.35) | 2.41 ± 0.48 (2.52) | 5.17 ± 1.19 (5.69) | 2.36 ± 0.84 (2.55) |
| right | p | 0.854 | 100/100 | 0 | 99 | 1.90 ± 0.58 (1.87) | 4.99 ± 3.66 (4.61) | 2.34 ± 0.49 (2.51) | 5.04 ± 1.23 (5.69) | 2.25 ± 0.85 (2.44) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.870 | 25/25 | 0 | 24 | 1.31 ± 0.25 (1.30) | 6.01 ± 4.06 (5.20) | 2.28 ± 0.47 (2.45) | 5.00 ± 1.22 (5.45) | 2.22 ± 0.86 (2.29) |
| forward/right | p | 0.875 | 25/25 | 0 | 25 | 1.31 ± 0.24 (1.28) | 4.56 ± 2.63 (4.98) | 2.24 ± 0.50 (2.40) | 4.91 ± 1.26 (5.63) | 2.11 ± 0.82 (2.42) |
| left/left | p | 0.875 | 25/25 | 0 | 23 | 1.71 ± 0.27 (1.78) | 5.18 ± 4.72 (3.65) | 2.48 ± 0.40 (2.61) | 5.34 ± 1.06 (5.87) | 2.47 ± 0.75 (2.64) |
| left/right | p | 0.878 | 25/25 | 0 | 25 | 1.96 ± 0.32 (2.00) | 4.15 ± 3.39 (2.67) | 2.34 ± 0.49 (2.51) | 5.07 ± 1.24 (5.69) | 2.26 ± 0.84 (2.54) |
| back/left | p | 0.815 | 25/25 | 0 | 24 | 2.64 ± 0.42 (2.56) | 5.97 ± 3.74 (5.53) | 2.47 ± 0.49 (2.62) | 5.22 ± 1.24 (5.81) | 2.44 ± 0.89 (2.92) |
| back/right | p | 0.792 | 25/25 | 0 | 25 | 2.61 ± 0.41 (2.56) | 6.15 ± 3.30 (5.80) | 2.36 ± 0.44 (2.51) | 5.04 ± 1.18 (5.71) | 2.27 ± 0.84 (2.31) |
| right/left | p | 0.868 | 25/25 | 0 | 25 | 1.93 ± 0.28 (1.98) | 3.93 ± 2.53 (3.79) | 2.40 ± 0.50 (2.47) | 5.11 ± 1.20 (5.60) | 2.29 ± 0.84 (2.41) |
| right/right | p | 0.871 | 25/25 | 0 | 24 | 1.73 ± 0.36 (1.70) | 5.12 ± 4.70 (4.15) | 2.41 ± 0.53 (2.59) | 5.16 ± 1.23 (5.85) | 2.37 ± 0.87 (2.67) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.892 | 5.4 | 5.99 | 2.89 |
| p | normal | 0.819 | 4.9 | 4.22 | 1.72 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.764 | 0.15 | 2.28 ± 0.70 (2.20) | 3.59 | 1.30 |
| p | medium | 18 | 0.892 | 0.80 | 1.18 ± 0.15 (1.21) | 3.77 | 1.40 |
| p | strong | 124 | 0.893 | 0.80 | - | 6.01 | 2.91 |

## Notes

- p: score 0.856, 200/200 kicked, 0 fell; worst sector back (0.804).
